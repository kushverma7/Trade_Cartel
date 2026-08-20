"""Full E_XJO-ASX 1-minute pull, year by year, raw preserved, no interpolation."""
import datetime as dt, os, sys, csv, gzip, time
from zoneinfo import ZoneInfo
import dukascopy_python
from dukascopy_python.instruments import INSTRUMENT_IDX_ASIA_E_XJO_ASX as SYM

UTC = dt.timezone.utc
RAW = "data/raw_dukascopy_au200_1m.csv.gz"
rows = []
seen = set()
dups = 0
start = dt.datetime(2019, 1, 1)
end = dt.datetime(2026, 8, 19)
cur = start
while cur < end:
    nxt = min(cur + dt.timedelta(days=90), end)
    for attempt in range(3):
        try:
            df = dukascopy_python.fetch(SYM, dukascopy_python.INTERVAL_MIN_1,
                                        dukascopy_python.OFFER_SIDE_BID, cur, nxt)
            break
        except Exception as e:
            print(f"  retry {attempt+1} {cur:%Y-%m-%d}: {type(e).__name__}", flush=True)
            time.sleep(3)
    else:
        print(f"  FAILED chunk {cur:%Y-%m-%d}", flush=True); cur = nxt; continue
    n = 0
    if df is not None and len(df):
        for ts, r in df.iterrows():
            t = ts.to_pydatetime()
            t = t.replace(tzinfo=UTC) if t.tzinfo is None else t.astimezone(UTC)
            if t in seen:
                dups += 1; continue
            seen.add(t)
            rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]),
                         float(r["close"]), float(r.get("volume", 0))))
            n += 1
    print(f"{cur:%Y-%m-%d}..{nxt:%Y-%m-%d}  +{n:>6}  total {len(rows):>9,}", flush=True)
    cur = nxt
rows.sort(key=lambda x: x[0])
os.makedirs("data", exist_ok=True)
with gzip.open(RAW, "wt", newline="") as f:
    w = csv.writer(f); w.writerow(["timestamp", "open", "high", "low", "close", "volume"])
    for t, o, h, l, c, v in rows:
        w.writerow([t.isoformat(), o, h, l, c, v])
print(f"\nDONE  {len(rows):,} 1-minute rows, {dups} duplicates dropped -> {RAW}")
