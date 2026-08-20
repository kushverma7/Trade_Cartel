"""Fetch Dukascopy AU200 and build exact Melbourne 5-minute candles.

INSTRUMENT (verified from dukascopy-python 4.0.1 instruments.py, line 221):
    INSTRUMENT_IDX_ASIA_E_XJO_ASX = "E_XJO-ASX"
That is Dukascopy's Australia 200 / S&P-ASX 200 index CFD. It is the only
Australia/ASX instrument in the entire Dukascopy instrument list.

SOURCE ENDPOINT: https://freeserv.dukascopy.com/2.0/index.php
CURRENTLY UNREACHABLE from this container — every dukascopy.com host returns a
blocked connection at the egress proxy. Nothing below has been run.

WHY 1-MINUTE, NOT 5-MINUTE, IS REQUESTED:
Dukascopy's own 5-minute bars are aligned to UTC. Melbourne is UTC+10/+11, both
whole hours, so a UTC 5-minute grid and a Melbourne 5-minute grid coincide
exactly — but only if the DST offset is a whole number of hours, which it is
for Australia. Requesting 1-minute data and aggregating locally removes the
assumption entirely and lets us verify alignment rather than trust it.

NO INTERPOLATION. Missing minutes stay missing. A 5-minute bar is emitted only
if at least one 1-minute bar exists inside it, and the bar records how many of
its five constituent minutes were actually present.
"""
import os, sys, csv, gzip, datetime as dt
from zoneinfo import ZoneInfo

MEL = ZoneInfo("Australia/Melbourne")
UTC = dt.timezone.utc
SYMBOL = "E_XJO-ASX"
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "au200_duka_5m.csv.gz")
RAW = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw_dukascopy_au200_1m.csv.gz")


def fetch(start: dt.date, end: dt.date, offer_side="bid"):
    try:
        import dukascopy_python
        from dukascopy_python.instruments import INSTRUMENT_IDX_ASIA_E_XJO_ASX
    except ImportError:
        sys.exit("pip install dukascopy-python")
    print(f"fetching {SYMBOL} 1-minute {start} .. {end} ({offer_side})", flush=True)
    df = dukascopy_python.fetch(
        INSTRUMENT_IDX_ASIA_E_XJO_ASX,
        dukascopy_python.INTERVAL_MIN_1,
        dukascopy_python.OFFER_SIDE_BID if offer_side == "bid" else dukascopy_python.OFFER_SIDE_ASK,
        start, end,
    )
    if df is None or len(df) == 0:
        sys.exit("empty response — check the date range and that the host is reachable")
    return df


def save_raw(df):
    os.makedirs(os.path.dirname(RAW), exist_ok=True)
    with gzip.open(RAW, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        for ts, r in df.iterrows():
            t = ts.to_pydatetime()
            if t.tzinfo is None:
                t = t.replace(tzinfo=UTC)
            w.writerow([t.astimezone(UTC).isoformat(), r["open"], r["high"],
                        r["low"], r["close"], r.get("volume", 0)])
    print(f"raw 1-minute preserved -> {RAW}")


def to_melbourne_5m(rows):
    """rows: (utc_datetime, o,h,l,c,v). Bucket on MELBOURNE local 5-minute
    boundaries, DST-aware, one bar at a time. No fixed offset anywhere."""
    buckets = {}
    for t, o, h, l, c, v in rows:
        lt = t.astimezone(MEL)
        key = (lt.date(), (lt.hour * 60 + lt.minute) // 5 * 5)
        b = buckets.get(key)
        if b is None:
            buckets[key] = [o, h, l, c, v, 1, lt]
        else:
            b[1] = max(b[1], h); b[2] = min(b[2], l); b[3] = c; b[4] += v; b[5] += 1
    out = []
    for (d, m), b in sorted(buckets.items()):
        out.append(dict(date=d, minute=m, open=b[0], high=b[1], low=b[2],
                        close=b[3], volume=b[4], minutes_present=b[5]))
    return out


def coverage(bars):
    from collections import defaultdict
    days = defaultdict(set)
    for b in bars:
        days[b["date"]].add(b["minute"])
    yrs = defaultdict(lambda: [0, 0, 0, 0])
    mons = defaultdict(lambda: [0, 0])
    for d, ms in days.items():
        y = yrs[d.year]; y[0] += 1
        has950 = 590 in ms; has1000 = 600 in ms
        y[1] += has950; y[2] += has1000; y[3] += (has950 and has1000)
        mk = (d.year, d.month); mons[mk][0] += 1; mons[mk][1] += (has950 and has1000)
    print(f"\n{'year':>6} {'dates':>7} {'has 09:50':>10} {'has 10:00':>10} {'BOTH':>7} {'% BOTH':>8}")
    for y in sorted(yrs):
        t, a, b_, c = yrs[y]
        print(f"{y:>6} {t:>7} {a:>10} {b_:>10} {c:>7} {100*c/t:>7.1f}%")
    print(f"\n{'year-month':>12} {'dates':>7} {'BOTH':>7} {'%':>7}")
    for k in sorted(mons):
        t, c = mons[k]
        print(f"{k[0]}-{k[1]:02d}     {t:>7} {c:>7} {100*c/t:>6.1f}%")
    return yrs


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--end", default=dt.date.today().isoformat())
    a = ap.parse_args()
    df = fetch(dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end))
    save_raw(df)
    rows = []
    for ts, r in df.iterrows():
        t = ts.to_pydatetime()
        if t.tzinfo is None:
            t = t.replace(tzinfo=UTC)
        rows.append((t.astimezone(UTC), r["open"], r["high"], r["low"], r["close"], r.get("volume", 0)))
    bars = to_melbourne_5m(rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.open(OUT, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "open", "high", "low", "close", "volume", "minutes_present"])
        for b in bars:
            lt = dt.datetime.combine(b["date"], dt.time(b["minute"] // 60, b["minute"] % 60), tzinfo=MEL)
            w.writerow([lt.astimezone(UTC).isoformat(), b["open"], b["high"], b["low"],
                        b["close"], b["volume"], b["minutes_present"]])
    print(f"wrote {len(bars):,} Melbourne-aligned 5-minute bars -> {OUT}")
    coverage(bars)
