"""Four-trader hybrid v3.0, reconstructed from its Section 5 prose and tested on
AU200 with achievable fills.

Conditions, exactly as the document specifies them:
  1. Session filter   - first two hours of the cash open
  2. Sweep            - wick through a respected level, close back inside (Marco)
  3. Aggression proxy - volume spike + body ratio (the document's own proxy)
  4. CVD proxy        - cumulative signed delta direction
  5. VWAP bias        - close vs session VWAP

Entries fill at the signal bar's CLOSE. Exits resolve on the 1-minute path with the
adverse extreme taken first. Costs included. Also sweeps the REQUIRED CONDITION COUNT
from 1 to 5, which directly tests the document's Absolute Law #2.
"""
import csv, datetime as dt, zoneinfo, math, statistics as st
from collections import defaultdict

UTC = dt.timezone.utc
MEL = zoneinfo.ZoneInfo("Australia/Sydney")
SRC = "/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv"
COST = 2.0

raw = []
with open(SRC) as f:
    for r in csv.DictReader(f):
        t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
        raw.append((t, float(r["open"]), float(r["high"]), float(r["low"]),
                    float(r["close"]), float(r["volume"] or 0)))
raw.sort()
minute = {r[0]: r for r in raw}
byday = defaultdict(list)
for r in raw:
    byday[r[0].astimezone(MEL).date()].append(r)


def build(tf):
    out, cur, key = [], None, None
    for t, o, h, l, c, v in raw:
        k = int(t.timestamp()) // (tf * 60)
        if k != key:
            if cur:
                out.append(tuple(cur))
            key, cur = k, [t, o, h, l, c, v]
        else:
            cur[3] = min(cur[3], l)
            cur[2] = max(cur[2], h)
            cur[4] = c
            cur[5] += v
    if cur:
        out.append(tuple(cur))
    return out


def atr(bars, n=14):
    tr, out, a = [], [], None
    for i, b in enumerate(bars):
        t = b[2] - b[3] if i == 0 else max(b[2] - b[3], abs(b[2] - bars[i-1][4]), abs(b[3] - bars[i-1][4]))
        tr.append(t)
        if i < n - 1:
            out.append(None)
            continue
        a = sum(tr[:n]) / n if a is None else (a * (n - 1) + t) / n
        out.append(a)
    return out


BARS = build(5)
ATR = atr(BARS)

# session VWAP + cumulative delta, both reset at the 10:00 Melbourne open
vwap, cvd = [None] * len(BARS), [None] * len(BARS)
pv = vv = cd = 0.0
curday = None
for i, b in enumerate(BARS):
    lt = b[0].astimezone(MEL)
    d = lt.date()
    if d != curday or (lt.hour, lt.minute) == (10, 0):
        if d != curday:
            curday = d
            pv = vv = cd = 0.0
    tp = (b[2] + b[3] + b[4]) / 3
    pv += tp * b[5]
    vv += b[5]
    rng = b[2] - b[3]
    cd += ((b[4] - b[1]) / rng if rng > 0 else 0.0) * b[5]
    vwap[i] = pv / vv if vv > 0 else None
    cvd[i] = cd

volma = [None] * len(BARS)
for i in range(len(BARS)):
    if i >= 20:
        volma[i] = sum(BARS[j][5] for j in range(i - 20, i)) / 20


def swings(i, look=10):
    lo = min(BARS[j][3] for j in range(max(0, i - look), i)) if i > 0 else None
    hi = max(BARS[j][2] for j in range(max(0, i - look), i)) if i > 0 else None
    return hi, lo


def resolve(entry_t, s, e, stop, tp1, tp2, deadline):
    """1-minute path, adverse extreme first. 50% off at tp1, remainder to tp2/deadline.

    entry_t is the signal bar's START. The bar is not tradeable until it CLOSES,
    so the path begins 5 minutes later. Starting earlier replays the very minutes
    that formed the sweep and stops the trade out inside its own signal bar.
    """
    bar_end = entry_t + dt.timedelta(minutes=5)
    d = bar_end.astimezone(MEL).date()
    path = [m for m in byday[d] if m[0] >= bar_end]
    half = False
    pnl = 0.0
    for (mt, mo, mh, ml, mc, mv) in path:
        adv = ml if s > 0 else mh
        fav = mh if s > 0 else ml
        if s * (adv - stop) <= 0:                      # stop first, always
            return pnl + (1.0 if half else 2.0) * 0.5 * s * (stop - e)
        if not half and s * (fav - tp1) >= 0:
            pnl += 0.5 * s * (tp1 - e)
            half = True
            stop = e                                   # remainder to breakeven
        elif half and s * (fav - tp2) >= 0:
            return pnl + 0.5 * s * (tp2 - e)
        if mt.astimezone(MEL).hour * 60 + mt.astimezone(MEL).minute >= deadline:
            return pnl + (0.5 if half else 1.0) * s * (mc - e)
    if path:
        return pnl + (0.5 if half else 1.0) * s * (path[-1][4] - e)
    return 0.0


def run(need, vol_mult=1.3, body_min=0.5, window=(600, 720), stop_pad=1.0):
    trades = []
    for i in range(30, len(BARS) - 1):
        if ATR[i] is None or vwap[i] is None or volma[i] is None or volma[i] == 0:
            continue
        b = BARS[i]
        lt = b[0].astimezone(MEL)
        mins = lt.hour * 60 + lt.minute
        if not (window[0] <= mins < window[1]):
            continue
        hi, lo = swings(i)
        if hi is None or lo is None:
            continue
        rng = b[2] - b[3]
        if rng <= 0:
            continue
        body = abs(b[4] - b[1]) / rng

        for s, sweep, vw_ok, cvd_ok in (
            (+1, b[3] < lo and b[4] > lo, b[4] > vwap[i], cvd[i] > cvd[i-1]),
            (-1, b[2] > hi and b[4] < hi, b[4] < vwap[i], cvd[i] < cvd[i-1]),
        ):
            aggr = b[5] > volma[i] * vol_mult and body >= body_min
            score = sum([bool(sweep), bool(aggr), bool(cvd_ok), bool(vw_ok), True])
            if score < need or not sweep:      # sweep is Marco's iron rule, always required
                continue
            e = b[4]
            level = lo if s > 0 else hi
            stop = level - s * stop_pad
            risk = abs(e - stop)
            if risk < 1.0 or risk > 40:
                continue
            tp1 = e + s * risk
            tp2 = e + s * risk * 3
            pnl = resolve(b[0], s, e, stop, tp1, tp2, 959)
            trades.append((lt.date(), s, pnl - COST, risk))
            break
    return trades


def rep(label, tr):
    if not tr:
        print(f"  {label:34s}  no trades")
        return
    p = [x[2] for x in tr]
    g = sum(v for v in p if v > 0)
    l = -sum(v for v in p if v <= 0)
    eq = pk = dd = 0.0
    for v in p:
        eq += v
        pk = max(pk, eq)
        dd = max(dd, pk - eq)
    days = len(set(x[0] for x in tr))
    m = sum(p) / len(p)
    sd = st.pstdev(p) or 1e-9
    print(f"  {label:34s} n={len(p):4d}  PF={g/l if l else 9.99:5.3f}  win={100*sum(1 for v in p if v>0)/len(p):5.1f}%"
          f"  net={sum(p):+8.1f}  avg={m:+6.2f}  t={m/sd*math.sqrt(len(p)):+5.2f}  maxDD={dd:6.1f}  {len(p)/days:.2f}/day")


sessions = len({r[0].astimezone(MEL).date() for r in raw})
print(f"AU200 5-minute, {BARS[0][0].astimezone(MEL).date()} .. {BARS[-1][0].astimezone(MEL).date()}, "
      f"{sessions} sessions, {COST:.0f}pt cost, entries at bar close, exits on 1m path\n")

print("ABSOLUTE LAW #2 UNDER TEST -- does requiring more conditions improve results?")
print("  (sweep is always required; the count is how many of the 5 must align)")
for need in (1, 2, 3, 4, 5):
    rep(f"require {need} of 5 conditions", run(need))

print("\nSENSITIVITY on the aggression proxy (require 4):")
for vm, bm in ((1.1, 0.4), (1.3, 0.5), (1.5, 0.6), (2.0, 0.6)):
    rep(f"vol>{vm}x MA, body>={bm}", run(4, vol_mult=vm, body_min=bm))

print("\nSESSION WINDOW (require 3, the count their own docs say is the max workable):")
for w, nm in (((600, 720), "10:00-12:00 open"), ((600, 780), "10:00-13:00"), ((600, 959), "10:00-close")):
    rep(nm, run(3, window=w))

print("\nBASELINE -- sweep alone, no other condition, same fills and costs:")
rep("sweep only", run(1))
