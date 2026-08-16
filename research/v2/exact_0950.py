"""EXACT PORT of "10 AM Body Break [Daily-Open Filtered]" v5, as supplied.

PORT, DON'T REIMPLEMENT. Every line below maps to a line of the indicator.
The one thing the indicator does not specify is the EXIT, because it is an
indicator. Exits are therefore swept, and the signal layer is untouched.

DATA LIMITATION, STATED UP FRONT: dailyOpen is `open` of the 09:50 bar. That bar
is the ASX pre-open auction print. It is present on only a fraction of the
sessions in the exported CSVs, and a session without it can never produce a
signal because `side` stays 0. Every result below is therefore reported against
the count of sessions that actually HAVE the bar, not the count in the file.
"""
import sys, csv, datetime as dt, zoneinfo, math, statistics as st, itertools
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine
from collections import defaultdict

UTC = dt.timezone.utc
MEL = zoneinfo.ZoneInfo("Australia/Melbourne")
U = "/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"


def load_5m(path, agg_from_1m=False):
    by = defaultdict(list)
    if agg_from_1m:
        rows = []
        for r in csv.DictReader(open(path)):
            t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
            rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
        rows.sort()
        cur, key = None, None
        for t, o, h, l, c in rows:
            k = int(t.timestamp()) // 300
            if k != key:
                if cur:
                    lt = cur[0].astimezone(MEL)
                    by[lt.date()].append((lt.hour * 60 + lt.minute, cur[1], cur[2], cur[3], cur[4]))
                key, cur = k, [t, o, h, l, c]
            else:
                cur[2] = max(cur[2], h); cur[3] = min(cur[3], l); cur[4] = c
        if cur:
            lt = cur[0].astimezone(MEL)
            by[lt.date()].append((lt.hour * 60 + lt.minute, cur[1], cur[2], cur[3], cur[4]))
    else:
        for r in csv.DictReader(open(path)):
            t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S")\
                  .replace(tzinfo=UTC).astimezone(MEL)
            by[t.date()].append((t.hour * 60 + t.minute, float(r["open"]), float(r["high"]),
                                 float(r["low"]), float(r["close"])))
    for d in by:
        by[d].sort()
    return by


def signals(bars, use_candle, show_flip, one_shot, end_hour):
    """Line-for-line port. bars = one session, (minute, o, h, l, c), any hours."""
    dailyOpen = bodyHi = bodyLo = None
    side = activeDir = 0
    signaledA = flipped = False
    out = []
    for i, (mn, o, h, l, c) in enumerate(bars):
        hh, mm = divmod(mn, 60)
        if hh == 9 and mm == 50:                      # isLine
            dailyOpen = o
        if hh == 10 and mm == 0 and dailyOpen is not None:   # isBody
            bodyHi = max(o, c); bodyLo = min(o, c)
            side = -1 if bodyHi < dailyOpen else (1 if bodyLo > dailyOpen else 0)
        afterBody = (hh > 10 or (hh == 10 and mm > 0)) and hh < end_hour
        armedA = (not use_candle) and bodyHi is not None and side != 0 \
                 and activeDir == 0 and afterBody and (not signaledA or not one_shot)
        buyA = armedA and side == 1 and c > bodyHi
        sellA = armedA and side == -1 and c < bodyLo
        buyB = use_candle and hh == 10 and mm == 0 and dailyOpen is not None and c > o and c > dailyOpen
        sellB = use_candle and hh == 10 and mm == 0 and dailyOpen is not None and c < o and c < dailyOpen
        buy, sell = buyA or buyB, sellA or sellB
        if buy:
            activeDir = 1; signaledA = True; flipped = False
            out.append((1, i, dailyOpen, bodyHi, bodyLo))
        if sell:
            activeDir = -1; signaledA = True; flipped = False
            out.append((-1, i, dailyOpen, bodyHi, bodyLo))
        flipSell = show_flip and not flipped and activeDir == 1 and afterBody \
                   and bodyLo is not None and c < bodyLo and not buy and not sell
        flipBuy = show_flip and not flipped and activeDir == -1 and afterBody \
                  and bodyHi is not None and c > bodyHi and not buy and not sell
        if flipSell:
            activeDir = -1; flipped = True
            out.append((-1, i, dailyOpen, bodyHi, bodyLo))
        if flipBuy:
            activeDir = 1; flipped = True
            out.append((1, i, dailyOpen, bodyHi, bodyLo))
    return out


def build(path, agg):
    by = load_5m(path, agg)
    days, have0950 = [], []
    for d in sorted(by):
        bs = by[d]
        if not any(b[0] == 600 for b in bs):
            continue
        days.append(d)
        if any(b[0] == 590 for b in bs):
            have0950.append(d)
    return by, days, have0950


def adr_map(by, days):
    out, hist = {}, []
    for d in days:
        cash = [b for b in by[d] if 600 <= b[0] < 960]
        out[d] = st.mean(hist[-14:]) if len(hist) >= 14 else None
        if cash:
            hist.append(max(b[2] for b in cash) - min(b[3] for b in cash))
    return out


def run(by, days, ADR, use_candle, flip, one_shot, end_hour, stop_k, exit_k, cost=2.0):
    tr = []
    for d in days:
        bs = by[d]
        adr = ADR.get(d)
        if adr is None:
            continue
        sg = signals(bs, use_candle, flip, one_shot, end_hour)
        for n, (s, i, do, bh, bl) in enumerate(sg):
            e = bs[i][4]
            body = bh - bl
            if   stop_k == "daily_open": sp = do
            elif stop_k == "body_far":   sp = bl if s > 0 else bh
            elif stop_k == "body_1x":    sp = e - s * max(body, 1.0)
            elif stop_k == "adr0.25":    sp = e - s * adr * 0.25
            elif stop_k == "adr0.5":     sp = e - s * adr * 0.5
            elif stop_k == "fixed10":    sp = e - s * 10
            elif stop_k == "fixed20":    sp = e - s * 20
            elif stop_k == "fixed30":    sp = e - s * 30
            if s * (e - sp) <= 0:                      # R8
                continue
            risk = abs(e - sp)
            if risk < 3.0 or risk > 80.0:              # R5
                continue
            tp = trail = None
            if   exit_k == "1R":   tp = e + s * risk
            elif exit_k == "1.5R": tp = e + s * risk * 1.5
            elif exit_k == "2R":   tp = e + s * risk * 2
            elif exit_k == "3R":   tp = e + s * risk * 3
            elif exit_k == "fixed20": tp = e + s * 20
            elif exit_k == "adr0.5":  tp = e + s * adr * 0.5
            elif exit_k == "trail_body": trail = max(body, 1.0)
            elif exit_k == "trail_adr0.3": trail = adr * 0.3
            elif exit_k == "time": pass
            # a later signal on the same day closes the previous leg at its close
            stop_i = sg[n + 1][1] if n + 1 < len(sg) else None
            cash = bs
            peak, cur, pnl = e, sp, None
            for j in range(i + 1, len(cash)):
                mn, o, h, l, c = cash[j]
                if stop_i is not None and j >= stop_i:
                    pnl = s * (cash[stop_i][4] - e) - cost; break
                adv = l if s > 0 else h
                fav = h if s > 0 else l
                if s * (adv - cur) <= 0:
                    pnl = s * (cur - e) - cost; break
                if tp is not None and s * (fav - tp) >= 0:
                    pnl = s * (tp - e) - cost; break
                if trail is not None:
                    if s * (c - peak) > 0:
                        peak = c
                    t2 = peak - s * trail
                    if s * (t2 - cur) > 0:
                        cur = t2
                if mn >= end_hour * 60 - 5:
                    pnl = s * (c - e) - cost; break
            if pnl is None:
                pnl = s * (cash[-1][4] - e) - cost
            tr.append(dict(day=d, s=s, pnl=pnl, risk=risk))
    return tr


STOPS = ["daily_open", "body_far", "body_1x", "adr0.25", "adr0.5", "fixed10", "fixed20", "fixed30"]
EXITS = ["1R", "1.5R", "2R", "3R", "fixed20", "adr0.5", "trail_body", "trail_adr0.3", "time"]

if __name__ == "__main__":
    for tag, path, agg in (("5m file (2020-2026)", U + "30348eaf-au200_aud_5m.csv", False),
                           ("1m file -> 5m (2025-2026)", U + "c1e55d1f-au200_aud_1m_4.csv", True)):
        by, days, have = build(path, agg)
        ADR = adr_map(by, days)
        print(f"\n{'='*86}\n{tag}")
        print(f"  sessions with a 10:00 bar : {len(days)}")
        print(f"  sessions with a 09:50 bar : {len(have)}   <-- the only ones that can signal")
        if len(have) < 40:
            print("  TOO FEW SESSIONS TO TEST. Not reported.")
            continue
        res = []
        for uc, fl, os_, eh in itertools.product([False, True], [False, True], [False, True], [12, 14, 16]):
            for sk in STOPS:
                for xk in EXITS:
                    m = engine.metrics(run(by, have, ADR, uc, fl, os_, eh, sk, xk), min_n=40)
                    if m:
                        res.append(((uc, fl, os_, eh, sk, xk), m))
        K = len(res)
        if K == 0:
            print("  no cell produced >=40 trades. NOTHING TO REPORT.")
            continue
        bar = math.sqrt(2 * math.log(K))
        res.sort(key=lambda r: -r[1]["t"])
        print(f"  {K} cells with >=40 trades.  multiple-testing bar t >= {bar:.2f}")
        print(f"  cells clearing it: {sum(1 for _, m in res if m['t'] >= bar)}")
        print(f"  cells with PF > 1.0: {sum(1 for _, m in res if m['pf'] > 1.0)} ({100*sum(1 for _,m in res if m['pf']>1.0)/K:.1f}%)")
        print(f"\n  {'logicB':6} {'flip':5} {'1shot':5} {'end':>3} {'stop':11} {'exit':13} "
              f"{'n':>4} {'PF':>6} {'win%':>5} {'net':>8} {'t':>6} {'yrs+':>5}")
        for (uc, fl, os_, eh, sk, xk), m in res[:12]:
            print(f"  {str(uc):6} {str(fl):5} {str(os_):5} {eh:>3} {sk:11} {xk:13} "
                  f"{m['n']:>4} {m['pf']:>6.3f} {m['win']:>5.1f} {m['net']:>8.1f} "
                  f"{m['t']:>6.2f} {m['yp']}/{m['ny']}")
