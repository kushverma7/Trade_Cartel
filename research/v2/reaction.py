"""REACTION TO THE LEVEL — Python port of strategies/reaction_to_the_level.pine.

Mirrors the Pine section for section. Runs under the v2 engine's rules.

PORT DELTAS (the Pine's higher-timeframe requests have no exact analogue here):
  D1. `rDO` in Pine is request.security(...,"D",open). This data has no
      unambiguous 24h daily open (see BUG-039), so the CASH SESSION OPEN is
      used and named as such. Stated, not silently substituted.
  D2. PDH/PDL/PDC are the previous CASH session's high/low/close.
  D3. 1H and 15M pivots are built by aggregating the 5m series, and a pivot
      becomes visible only at the close of the bar that confirms it, which is
      the same lag ta.pivothigh(n,n) has.
"""
import sys, math, statistics as st, datetime as dt
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine
from collections import defaultdict

D = engine.Data()
TF = 5


def agg(bars, mult):
    """Aggregate 5m session bars into mult*5-minute bars."""
    out, cur = [], None
    for mn, o, h, l, c, v in bars:
        k = mn // (5 * mult)
        if cur is None or cur[0] != k:
            if cur:
                out.append(cur[1:])
            cur = [k, mn, o, h, l, c]
        else:
            cur[3] = max(cur[3], h)
            cur[4] = min(cur[4], l)
            cur[5] = c
    if cur:
        out.append(cur[1:])
    return out                      # (start_min, o, h, l, c)


def pivots(bars, n):
    """(confirm_minute, price) for each confirmed pivot high / low."""
    ph, pl = [], []
    for i in range(n, len(bars) - n):
        w = bars[i - n:i + n + 1]
        if bars[i][2] == max(b[2] for b in w):
            ph.append((bars[i + n][0], bars[i][2]))
        if bars[i][3] == min(b[3] for b in w):
            pl.append((bars[i + n][0], bars[i][3]))
    return ph, pl


# ---- per-session precomputation --------------------------------------
SESS = {}
prev = None
for d in D.days:
    bs = D.bars[d]
    p1h_h, p1h_l = pivots(agg(bs, 12), 3)      # 60-minute pivots, lookback 3
    p15_h, p15_l = pivots(agg(bs, 3), 4)       # 15-minute pivots, lookback 4
    psw_h, psw_l = pivots([(b[0], b[1], b[2], b[3], b[4]) for b in bs], 10)
    r = D.ref[d]
    SESS[d] = dict(bars=bs, p1hH=p1h_h, p1hL=p1h_l, p15H=p15_h, p15L=p15_l,
                   swH=psw_h, swL=psw_l,
                   do=bs[0][1], pdh=r["prev_high"], pdl=r["prev_low"],
                   pdc=r["prev_close"], adr=r["adr"])

WEIGHT = dict(DO=2.0, PDH=2.0, PDL=2.0, PDC=1.5, DayH=1.5, DayL=1.5,
              SH=1.5, SL=1.5, H1R=2.0, H1S=2.0, M15R=1.0, M15S=1.0)


def run(min_conf=3, mode="retest", setup="both", zone=25.0, target="next",
        rr=2.0, confl_d=15.0, vol_mult=1.2, ema_len=20, pad=3.0,
        min_r=3.0, max_r=80.0, min_rr=1.0, wait=12, cost=2.0, days=None,
        flip=False):
    trades = []
    for d in (days if days is not None else D.days):
        S = SESS[d]
        bs = S["bars"]
        if S["pdh"] is None:
            continue
        # rolling level state
        h1r = h1s = m15r = m15s = swh = swl = None
        i1r = i1s = i15r = i15s = isw_h = isw_l = 0
        dayH = dayL = None
        ema = None
        k = 2.0 / (ema_len + 1)
        vols = []
        state, aLvl, aBar, aExt = 0, None, 0, None
        done = False
        for j, (mn, o, h, l, c, v) in enumerate(bs):
            # advance pivot pointers to everything confirmed by this bar
            while i1r < len(S["p1hH"]) and S["p1hH"][i1r][0] <= mn:
                h1r = S["p1hH"][i1r][1]; i1r += 1
            while i1s < len(S["p1hL"]) and S["p1hL"][i1s][0] <= mn:
                h1s = S["p1hL"][i1s][1]; i1s += 1
            while i15r < len(S["p15H"]) and S["p15H"][i15r][0] <= mn:
                m15r = S["p15H"][i15r][1]; i15r += 1
            while i15s < len(S["p15L"]) and S["p15L"][i15s][0] <= mn:
                m15s = S["p15L"][i15s][1]; i15s += 1
            while isw_h < len(S["swH"]) and S["swH"][isw_h][0] <= mn:
                swh = S["swH"][isw_h][1]; isw_h += 1
            while isw_l < len(S["swL"]) and S["swL"][isw_l][0] <= mn:
                swl = S["swL"][isw_l][1]; isw_l += 1
            dayH = h if dayH is None else max(dayH, h)
            dayL = l if dayL is None else min(dayL, l)
            ema = c if ema is None else ema + k * (c - ema)
            vols.append(v)
            vma = st.mean(vols[-20:]) if len(vols) >= 20 else None

            if j == 0 or done:
                prev_c = c
                continue
            pool = [(S["do"], "DO"), (S["pdh"], "PDH"), (S["pdl"], "PDL"),
                    (S["pdc"], "PDC"), (dayH, "DayH"), (dayL, "DayL"),
                    (swh, "SH"), (swl, "SL"), (h1r, "H1R"), (h1s, "H1S"),
                    (m15r, "M15R"), (m15s, "M15S")]
            pool = [(p, n) for p, n in pool if p is not None]
            if not pool:
                prev_c = c
                continue
            lvl = min(pool, key=lambda x: abs(c - x[0]))[0]
            in_band = abs(c - lvl) <= zone or (l <= lvl <= h)

            def confl(px):
                return sum(WEIGHT[n] for p, n in pool if abs(p - px) <= confl_d)

            def conf(dirn, lv, retested):
                n = 0
                n += 1 if (c > lv if dirn > 0 else c < lv) else 0
                n += 1 if (c > ema if dirn > 0 else c < ema) else 0
                n += 1 if (vma is None or vma == 0 or v > vma * vol_mult) else 0
                n += 1 if confl(lv) >= 3.0 else 0
                n += 1 if (c > o if dirn > 0 else c < o) else 0
                n += 1 if retested else 0
                return n

            fire, use_lvl, retested = 0, None, False
            # --- break state machine (sections 5, 6, 17) ---
            if state == 0 and in_band and setup != "rejection":
                if c > lvl >= prev_c:
                    state, aLvl, aBar, aExt = 1, lvl, j, l
                elif c < lvl <= prev_c:
                    state, aLvl, aBar, aExt = -1, lvl, j, h
            elif state == 1:
                aExt = min(aExt, l)
            elif state == -1:
                aExt = max(aExt, h)
            if state != 0:
                hold = c > aLvl if state == 1 else c < aLvl
                back = (l <= aLvl + zone * 0.4) if state == 1 else (h >= aLvl - zone * 0.4)
                if mode == "close":
                    fire, use_lvl, state = state, aLvl, 0
                elif mode == "next":
                    if mn // 60 != bs[aBar][0] // 60 and j > aBar:
                        if hold:
                            fire, use_lvl = state, aLvl
                        state = 0
                else:
                    if back and hold and j > aBar:
                        fire, use_lvl, retested, state = state, aLvl, True, 0
                    elif not hold and j > aBar:
                        state = 0
                    elif j - aBar > wait:
                        state = 0
            # --- rejection / false break (sections 3, 17) ---
            if fire == 0 and in_band and setup != "break":
                if l < lvl and c > lvl and prev_c > lvl:
                    fire, use_lvl = 1, lvl
                elif h > lvl and c < lvl and prev_c < lvl:
                    fire, use_lvl = -1, lvl

            if fire != 0:
                dirn = fire * (-1 if flip else 1)
                if conf(fire, use_lvl, retested) >= min_conf:
                    inval = aExt if retested or mode != "retest" else (l if fire > 0 else h)
                    if inval is None:
                        inval = l if fire > 0 else h
                    stop = (min(inval, use_lvl) - pad) if dirn > 0 else (max(inval, use_lvl) + pad)
                    risk = (c - stop) if dirn > 0 else (stop - c)
                    above = [p for p, _ in pool if p > c]
                    below = [p for p, _ in pool if p < c]
                    nxt = (min(above) if above else None) if dirn > 0 else (max(below) if below else None)
                    if target == "next" and nxt is not None:
                        tgt = nxt
                    else:
                        tgt = c + dirn * risk * rr
                    rew = (tgt - c) if dirn > 0 else (c - tgt)
                    if min_r <= risk <= max_r and rew > 0 and rew / risk >= min_rr:
                        pnl = None
                        for q in range(j + 1, len(bs)):
                            _, _, hh, ll, cc, _ = bs[q]
                            adv = ll if dirn > 0 else hh
                            fav = hh if dirn > 0 else ll
                            if dirn * (adv - stop) <= 0:
                                pnl = dirn * (stop - c) - cost; break
                            if dirn * (fav - tgt) >= 0:
                                pnl = dirn * (tgt - c) - cost; break
                        if pnl is None:
                            pnl = dirn * (bs[-1][4] - c) - cost
                        trades.append(dict(day=d, s=dirn, pnl=pnl, risk=risk))
                        done = True
            prev_c = c
    return trades
