"""AU200 Dukascopy data validation — the ten items, no backtest."""
import csv, gzip, datetime as dt, random, statistics as st
from zoneinfo import ZoneInfo
from collections import defaultdict, Counter

UTC = dt.timezone.utc
MEL = ZoneInfo("Australia/Melbourne")
RAW = "data/raw_dukascopy_au200_1m.csv.gz"
OUT = "data/au200_duka_5m.csv.gz"

# ---- load raw 1-minute, verify integrity -------------------------------
rows = []
seen = set(); dups = 0
for r in csv.DictReader(gzip.open(RAW, "rt")):
    t = dt.datetime.fromisoformat(r["timestamp"])
    if t in seen:
        dups += 1; continue
    seen.add(t)
    rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]),
                 float(r["close"]), float(r["volume"])))
rows.sort()
print(f"1  DATE RANGE (UTC)        : {rows[0][0]} .. {rows[-1][0]}")
print(f"2  TOTAL 1-MINUTE ROWS     : {len(rows):,}")
print(f"3  DUPLICATE TIMESTAMPS    : {dups} on re-read (21 dropped during download)")

# ---- Melbourne 5-minute construction, DST-aware, per bar ---------------
buck = {}
for t, o, h, l, c, v in rows:
    lt = t.astimezone(MEL)                       # per-bar DST-correct conversion
    key = (lt.date(), (lt.hour * 60 + lt.minute) // 5 * 5)
    b = buck.get(key)
    if b is None:
        buck[key] = [o, h, l, c, v, 1]
    else:
        b[1] = max(b[1], h); b[2] = min(b[2], l); b[3] = c; b[4] += v; b[5] += 1
bars = {k: v for k, v in sorted(buck.items())}
with gzip.open(OUT, "wt", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp", "open", "high", "low", "close", "volume", "minutes_present"])
    for (d, m), b in bars.items():
        lt = dt.datetime.combine(d, dt.time(m // 60, m % 60), tzinfo=MEL)
        w.writerow([lt.astimezone(UTC).isoformat(), b[0], b[1], b[2], b[3], b[4], b[5]])
print(f"   5-MINUTE BARS BUILT     : {len(bars):,}  -> {OUT}")

days = defaultdict(dict)
for (d, m), b in bars.items():
    days[d][m] = b

# a trading session = has any bar inside 10:00-16:00 Melbourne
sess = [d for d in sorted(days) if any(600 <= m < 960 for m in days[d])]
print(f"4  TRADING SESSIONS        : {len(sess)}   {sess[0]} .. {sess[-1]}")

h950 = [d for d in sess if 590 in days[d]]
h1000 = [d for d in sess if 600 in days[d]]
both = [d for d in sess if 590 in days[d] and 600 in days[d]]
print(f"5  EXACT 09:50 CANDLE      : {len(h950):5d} / {len(sess)}  ({100*len(h950)/len(sess):.2f}%)")
print(f"6  EXACT 10:00 CANDLE      : {len(h1000):5d} / {len(sess)}  ({100*len(h1000)/len(sess):.2f}%)")
print(f"7  BOTH                    : {len(both):5d} / {len(sess)}  ({100*len(both)/len(sess):.2f}%)")

print(f"\n8  COVERAGE BY YEAR")
print(f"   {'year':>6} {'sessions':>9} {'09:50':>7} {'10:00':>7} {'BOTH':>7} {'% BOTH':>8} {'partial 09:50':>14}")
yr = defaultdict(lambda: [0, 0, 0, 0, 0])
for d in sess:
    y = yr[d.year]; y[0] += 1
    a = 590 in days[d]; b_ = 600 in days[d]
    y[1] += a; y[2] += b_; y[3] += (a and b_)
    if a and days[d][590][5] < 5:
        y[4] += 1
for y in sorted(yr):
    t, a, b_, c, p = yr[y]
    print(f"   {y:>6} {t:>9} {a:>7} {b_:>7} {c:>7} {100*c/t:>7.2f}% {p:>14}")

print(f"\n9  COVERAGE BY MONTH (% with BOTH)")
mo = defaultdict(lambda: [0, 0])
for d in sess:
    k = (d.year, d.month); mo[k][0] += 1
    mo[k][1] += (590 in days[d] and 600 in days[d])
yrs = sorted({k[0] for k in mo})
print("   " + "month ".rjust(8) + "".join(f"{y:>9}" for y in yrs))
for m in range(1, 13):
    cells = []
    for y in yrs:
        t, c = mo.get((y, m), [0, 0])
        cells.append(f"{100*c/t:>8.1f}%" if t else f"{'-':>9}")
    print(f"   {dt.date(2000,m,1):%b}    " + "".join(cells))

print(f"\n10 TWENTY RANDOM SESSIONS — 09:50 open and full 10:00 OHLC")
random.seed(20260819)
pick = sorted(random.sample(both, 20))
print(f"   {'date':11} {'09:50 O':>9} {'10:00 O':>9} {'10:00 H':>9} {'10:00 L':>9} {'10:00 C':>9} "
      f"{'bodyHi':>9} {'bodyLo':>9} {'SIDE':9} {'A time':>7} {'A dir':>6} {'C2 time':>8} {'C2 px':>9}")
for d in pick:
    D = days[d]
    do = D[590][0]
    o, h, l, c = D[600][0], D[600][1], D[600][2], D[600][3]
    bh, bl = max(o, c), min(o, c)
    side = "ABOVE" if bl > do else ("BELOW" if bh < do else "STRADDLE")
    at, ad, ct, cp, entry, sidev = "-", "-", "-", "-", None, 0
    if side in ("ABOVE", "BELOW"):
        for m in sorted(k for k in D if 600 < k < 960):
            cc = D[m][3]
            if side == "ABOVE" and cc > bh:
                at, ad, entry, sidev = f"{m//60:02d}:{m%60:02d}", "LONG", cc, 1; break
            if side == "BELOW" and cc < bl:
                at, ad, entry, sidev = f"{m//60:02d}:{m%60:02d}", "SHORT", cc, -1; break
        if entry is not None:
            em = int(at[:2]) * 60 + int(at[3:])
            for m in sorted(k for k in D if em < k < 960):
                cc = D[m][3]
                if (sidev > 0 and cc < bl) or (sidev < 0 and cc > bh):
                    ct, cp = f"{m//60:02d}:{m%60:02d}", f"{cc:.1f}"; break
    print(f"   {str(d):11} {do:>9.1f} {o:>9.1f} {h:>9.1f} {l:>9.1f} {c:>9.1f} "
          f"{bh:>9.1f} {bl:>9.1f} {side:9} {at:>7} {ad:>6} {ct:>8} {cp:>9}")

sides = Counter()
for d in both:
    D = days[d]; do = D[590][0]
    o, c = D[600][0], D[600][3]
    bh, bl = max(o, c), min(o, c)
    sides["ABOVE" if bl > do else ("BELOW" if bh < do else "STRADDLE")] += 1
print(f"\n   SIDE distribution over all {len(both)} testable sessions: {dict(sides)}")
print(f"   Logic A eligible (ABOVE+BELOW): {sides['ABOVE']+sides['BELOW']}")
