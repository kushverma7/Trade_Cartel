"""
Port of "DE Hybrid: V5 Entry + V6 X Exit [Kush]" (user-supplied indicator).

PORT, DON'T REIMPLEMENT (standing rule). Every rule below is a line-for-line
translation of the supplied Pine, including the state machine. Deviations are
numbered port deltas at the bottom of this docstring.

The point of the port is that the supplied script is an INDICATOR. It draws
BUY/SELL/X labels and colours bars; it has no position size, no stop loss and
no accounting, so it cannot state whether its signals make money. This module
puts those exact signals through the same execution model, costs and sizing as
every other engine in this repo so the answer is measurable.

signals() returns the raw booleans. run() trades them.

PORT DELTAS
  1. ta.supertrend uses hl2 +/- mult*ATR(len) with the standard band-lock
     recursion. Reproduced explicitly.
  2. ta.mfi(hlc3, n) reproduced with the standard positive/negative money-flow
     ratio.
  3. `bss` (cooldown counter) is reset on entry in the Pine by the same
     assignment that sets state; order preserved here.
  4. The Pine has no stop loss. run() adds an optional ATR stop, because a
     backtest without one reports a drawdown that no account could survive.
     stop_atr=0 reproduces the script exactly.
"""
import numpy as np
import pandas as pd


def _rma(x, n):
    return pd.Series(x).ewm(alpha=1.0 / n, adjust=False).mean().to_numpy()


def _true_range(h, l, c):
    pc = np.roll(c, 1); pc[0] = c[0]
    return np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))


def _supertrend(h, l, c, mult, length):
    """ta.supertrend: returns (line, dir) with dir -1 = bullish."""
    atr = _rma(_true_range(h, l, c), length)
    hl2 = (h + l) / 2.0
    up, dn = hl2 - mult * atr, hl2 + mult * atr
    n = len(c)
    lo = np.full(n, np.nan); hi = np.full(n, np.nan)
    d = np.ones(n, dtype=int)
    lo[0], hi[0] = up[0], dn[0]
    for i in range(1, n):
        lo[i] = max(up[i], lo[i - 1]) if c[i - 1] > lo[i - 1] else up[i]
        hi[i] = min(dn[i], hi[i - 1]) if c[i - 1] < hi[i - 1] else dn[i]
        if d[i - 1] == 1 and c[i] > hi[i - 1]:
            d[i] = -1
        elif d[i - 1] == -1 and c[i] < lo[i - 1]:
            d[i] = 1
        else:
            d[i] = d[i - 1]
    return np.where(d == -1, lo, hi), d


def _mfi(h, l, c, v, n):
    tp = (h + l + c) / 3.0
    raw = tp * v
    dtp = np.diff(tp, prepend=tp[0])
    pos = pd.Series(np.where(dtp > 0, raw, 0.0)).rolling(n).sum().to_numpy()
    neg = pd.Series(np.where(dtp < 0, raw, 0.0)).rolling(n).sum().to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100.0 - 100.0 / (1.0 + pos / neg)


def _rsi(c, n):
    d = np.diff(c, prepend=c[0])
    up, dn = _rma(np.maximum(d, 0), n), _rma(np.maximum(-d, 0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 100.0 - 100.0 / (1.0 + up / dn)


def _ema(c, n):
    return pd.Series(c).ewm(span=n, adjust=False).mean().to_numpy()


def signals(df, st_len=97, st_mult=4.0, at_period=14, at_coeff=1.0,
            no_vol_at=False, ema_bbsr=200, ema_fast=9, ema_mid=21,
            ema_slow=50, rsi_len=14, rsi_ob=60, rsi_os=40,
            macd_f=8, macd_s=17, macd_sig=9, ag_len=14, ag_mult=1.0,
            bb_len=20, bb_mult=2.0, use_vg=True, liq_lb=20, sw_age=5,
            vol_len=20, vol_thr=1.1, use_vol=False, min_conf=3,
            use_trend=True, use_rev=True, cooldown=5):
    o = df["open"].to_numpy(float); h = df["high"].to_numpy(float)
    l = df["low"].to_numpy(float);  c = df["close"].to_numpy(float)
    v = df["volume"].to_numpy(float) if "volume" in df else np.ones(len(c))
    n = len(c)

    _, st_dir = _supertrend(h, l, c, st_mult, st_len)
    st_bull, st_bear = st_dir == -1, st_dir == 1

    at_atr = pd.Series(_true_range(h, l, c)).rolling(at_period).mean().to_numpy()
    upT, downT = l - at_atr * at_coeff, h + at_atr * at_coeff
    mom = (_rsi(c, at_period) if no_vol_at else _mfi(h, l, c, v, at_period)) >= 50
    AT = np.full(n, np.nan)
    prev = 0.0
    for i in range(n):
        if np.isnan(upT[i]):
            AT[i] = prev; continue
        AT[i] = (max(prev, upT[i]) if mom[i] else min(prev, downT[i]))
        prev = AT[i]

    def sh(a, k):
        out = np.full(n, np.nan); out[k:] = a[:-k]; return out
    AT1, AT2, AT3, AT4 = sh(AT, 1), sh(AT, 2), sh(AT, 3), sh(AT, 4)
    at_flip_bull = (AT > AT2) & (AT1 <= AT3)
    at_flip_bear = (AT < AT2) & (AT1 >= AT3)
    at_cont_bull = (AT > AT2) & (AT2 > AT4)
    at_cont_bear = (AT < AT2) & (AT2 < AT4)

    bbsr = _ema(c, ema_bbsr)
    above, below = c > bbsr, c < bbsr

    ef, em, es = _ema(c, ema_fast), _ema(c, ema_mid), _ema(c, ema_slow)
    ema50_rise, ema50_fall = es > sh(es, 3), es < sh(es, 3)
    ema9_up = (ef > sh(ef, 1)) & (sh(ef, 1) > sh(ef, 2))
    ema9_dn = (ef < sh(ef, 1)) & (sh(ef, 1) < sh(ef, 2))

    rsi = _rsi(c, rsi_len)
    rsi_bull_z = (rsi > 45) & (rsi < 70)
    rsi_bear_z = (rsi < 55) & (rsi > 30)
    rsi_rev_bull = (rsi < rsi_os) & (rsi > sh(rsi, 1))
    rsi_rev_bear = (rsi > rsi_ob) & (rsi < sh(rsi, 1))

    ml = _ema(c, macd_f) - _ema(c, macd_s)
    sl2 = _ema(ml, macd_sig)
    mh = ml - sl2
    macd_bull, macd_bear = ml > sl2, ml < sl2

    agv = _rma(_true_range(h, l, c), ag_len)
    axp = agv > pd.Series(agv).rolling(50).mean().to_numpy() * ag_mult
    bbs = pd.Series(c).rolling(bb_len).mean().to_numpy()
    vgb = np.ones(n, bool) if not use_vg else (axp & (c > bbs))
    vgs = np.ones(n, bool) if not use_vg else (axp & (c < bbs))

    rph = pd.Series(sh(h, 1)).rolling(liq_lb).max().to_numpy()
    rpl = pd.Series(sh(l, 1)).rolling(liq_lb).min().to_numpy()
    swb = (l < rpl) & (c > rpl)
    sws = (h > rph) & (c < rph)
    sba = np.full(n, 9999); ssa = np.full(n, 9999)
    a = b = 9999
    for i in range(n):
        a = 0 if swb[i] else a + 1
        b = 0 if sws[i] else b + 1
        sba[i], ssa[i] = a, b
    rsb, rss = sba <= sw_age, ssa <= sw_age

    vma = pd.Series(v).rolling(vol_len).mean().to_numpy()
    vok = np.ones(n, bool) if not use_vol else (v > vma * vol_thr)

    tgb = st_bull & above & ema50_rise
    tgs = st_bear & below & ema50_fall
    tbs = (st_bull.astype(int) + np.nan_to_num(at_cont_bull).astype(int)
           + above.astype(int) + np.nan_to_num(rsi_bull_z).astype(int)
           + macd_bull.astype(int))
    tss = (st_bear.astype(int) + np.nan_to_num(at_cont_bear).astype(int)
           + below.astype(int) + np.nan_to_num(rsi_bear_z).astype(int)
           + macd_bear.astype(int))

    return dict(
        tgb=tgb, tgs=tgs, tbs=tbs, tss=tss, vgb=vgb, vgs=vgs, vok=vok,
        rsb=rsb, rss=rss, swb=swb, sws=sws,
        at_flip_bull=np.nan_to_num(at_flip_bull).astype(bool),
        at_flip_bear=np.nan_to_num(at_flip_bear).astype(bool),
        rsi_rev_bull=np.nan_to_num(rsi_rev_bull).astype(bool),
        rsi_rev_bear=np.nan_to_num(rsi_rev_bear).astype(bool),
        ema9_up=np.nan_to_num(ema9_up).astype(bool),
        ema9_dn=np.nan_to_num(ema9_dn).astype(bool),
        rsi=rsi, mh=mh, em=em, min_conf=min_conf, cooldown=cooldown,
        use_trend=use_trend, use_rev=use_rev)


def run(df, sig=None, stop_atr=0.0, exit_atr_len=14, giveback_atr=0.8,
        use_giveback=True, use_ema21=True, use_mom=True, use_at=True,
        use_sweep=True, min_bars_exit=1, alternate=True, trail_exit=0.0,
        risk_pct=1.0, equity0=10000.0, commission=0.07, slippage=0.05,
        max_lev=20, gap_fill=True, **kw):
    """Trade the ported signals.

    alternate=True reproduces the Pine state machine, where states 2/-2 mean
    "just exited a long, may ONLY take a short next". trail_exit>0 replaces
    the five V6 X exits with this repo's ATR trailing stop, which is the
    comparison that matters.
    """
    S = sig if sig is not None else signals(df, **kw)
    h = df["high"].to_numpy(float); l = df["low"].to_numpy(float)
    c = df["close"].to_numpy(float); o = df["open"].to_numpy(float)
    n = len(c)
    atr = _rma(_true_range(h, l, c), exit_atr_len)
    rsi, mh, em = S["rsi"], S["mh"], S["em"]

    def sh(a, k):
        out = np.full(n, np.nan); out[k:] = a[:-k]; return out
    mh1, mh2, rsi1 = sh(mh, 1), sh(mh, 2), sh(rsi, 1)
    em1 = sh(em, 1); c1 = sh(c, 1)

    tbr = (S["use_trend"] & S["tgb"] & (S["tbs"] >= S["min_conf"])
           & S["vgb"] & S["vok"])
    tsr = (S["use_trend"] & S["tgs"] & (S["tss"] >= S["min_conf"])
           & S["vgs"] & S["vok"])
    rbr = (S["use_rev"] & S["rsb"] & S["at_flip_bull"] & S["rsi_rev_bull"]
           & S["ema9_up"] & S["vgb"])
    rsr = (S["use_rev"] & S["rss"] & S["at_flip_bear"] & S["rsi_rev_bear"]
           & S["ema9_dn"] & S["vgs"])
    buy_raw, sell_raw = tbr | rbr, tsr | rsr

    eq = equity0
    trades = []
    state = 0; pos = None; bss = S["cooldown"] + 1
    for i in range(210, n):
        bss += 1
        cd = bss > S["cooldown"]

        if pos is not None:
            d = pos["dir"]
            pos["best"] = (max(pos["best"], h[i]) if d > 0
                           else min(pos["best"], l[i]))
            stopped = False
            if trail_exit > 0:
                cand = (h[i - 1] - atr[i] * trail_exit if d > 0
                        else l[i - 1] + atr[i] * trail_exit)
                pos["stop"] = (max(pos["stop"], cand) if d > 0
                               else min(pos["stop"], cand))
            if pos["stop"] is not None and not np.isnan(pos["stop"]):
                stopped = l[i] <= pos["stop"] if d > 0 else h[i] >= pos["stop"]
            hit = False
            if stopped:
                px = pos["stop"]
                if gap_fill:
                    px = min(px, o[i]) if d > 0 else max(px, o[i])
                px -= d * slippage
                hit = True
            elif trail_exit == 0 and i - pos["bar"] >= min_bars_exit:
                prof = (c[i] > pos["entry"]) if d > 0 else (c[i] < pos["entry"])
                gb = (use_giveback and prof and
                      ((c[i] < pos["best"] - atr[i] * giveback_atr) if d > 0
                       else (c[i] > pos["best"] + atr[i] * giveback_atr)))
                eb = (use_ema21 and ((c[i] < em[i] and c1[i] < em1[i]) if d > 0
                                     else (c[i] > em[i] and c1[i] > em1[i])))
                mo = (use_mom and ((mh[i] < mh1[i] and mh1[i] < mh2[i] and rsi[i] < rsi1[i]) if d > 0
                                   else (mh[i] > mh1[i] and mh1[i] > mh2[i] and rsi[i] > rsi1[i])))
                af = (use_at and (S["at_flip_bear"][i] if d > 0 else S["at_flip_bull"][i]))
                ow = (use_sweep and ((S["sws"][i] and rsi[i] > 55 and rsi[i] < rsi1[i]) if d > 0
                                     else (S["swb"][i] and rsi[i] < 45 and rsi[i] > rsi1[i])))
                if gb or eb or mo or af or ow:
                    px = c[i] - d * slippage
                    hit = True
                    pos["why"] = ("giveback" if gb else "ema21" if eb else
                                  "momentum" if mo else "at_flip" if af else "sweep")
            if hit:
                pnl = d * (px - pos["entry"]) * pos["qty"] - 2 * commission * pos["qty"]
                eq += pnl
                trades.append({"pnl": pnl, "dir": d, "bar": pos["bar"],
                               "bars_held": i - pos["bar"],
                               "why": pos.get("why", "stop")})
                state = (2 if d > 0 else -2) if alternate else 0
                pos = None

        if pos is not None or np.isnan(atr[i]) or atr[i] <= 0 or not cd:
            continue
        allow_b = (state in (0, -2)) if alternate else True
        allow_s = (state in (0, 2)) if alternate else True
        d = 1 if (buy_raw[i] and allow_b) else (-1 if (sell_raw[i] and allow_s) else 0)
        if d == 0:
            continue
        sdist = atr[i] * (trail_exit if trail_exit > 0 else stop_atr)
        entry = c[i] + d * slippage
        qty = (min(eq * risk_pct / 100.0 / sdist, eq * max_lev / c[i])
               if sdist > 0 else eq * max_lev / c[i])
        qty = float(np.floor(max(qty, 0)))
        if qty < 1:
            continue
        pos = {"dir": d, "entry": entry, "qty": qty, "bar": i,
               "best": h[i] if d > 0 else l[i],
               "stop": (entry - d * sdist) if sdist > 0 else np.nan}
        state = d
        bss = 0
    return trades
