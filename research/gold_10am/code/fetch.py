"""Download authentic XAU/USD 1-minute OHLCV for the Gold 10AM study.

SOURCE DECISION (documented, not silent — see report section 2)
--------------------------------------------------------------
The brief names London Strategic Edge. LSE is reachable from this container
now (api.londonstrategicedge.com answers 401, not the 403 tunnel refusal
recorded on 2026-08-17), but LSE_API_KEY is ABSENT from this container's
environment — the container that held it was recycled, and the key pasted on
2026-08-17 was a live credential in a public repo that the user was told to
rotate. Without a key the vault cannot be read.

So the primary feed here is Dukascopy XAU/USD, the same provider whose
E_XJO-ASX feed was validated for the AU200 study (10-item audit, 98.91%
09:50 coverage). Dukascopy publishes BID and ASK separately, which lets the
cost model in Phase 27 use a MEASURED historical spread rather than an
assumed one — something LSE mid candles could not have given.

`--source lse` runs the identical pipeline against the LSE vault the moment a
key is exported, so the study can be re-run and compared without edits.

NO INTERPOLATION anywhere. Missing minutes stay missing and are reported.
The key is read from os.environ only; never printed, logged or written.
"""
import os, sys, csv, gzip, argparse, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")

START = dt.date(2024, 8, 20)
END = dt.date(2026, 8, 19)          # inclusive; 2026-08-20 deliberately excluded
UTC = dt.timezone.utc


def month_edges(start, end):
    cur = start
    while cur <= end:
        if cur.month == 12:
            nxt = dt.date(cur.year + 1, 1, 1)
        else:
            nxt = dt.date(cur.year, cur.month + 1, 1)
        yield cur, min(nxt - dt.timedelta(days=1), end)
        cur = nxt


def fetch_duka(side, start, end):
    import dukascopy_python as d
    from dukascopy_python.instruments import INSTRUMENT_FX_METALS_XAU_USD as XAU
    offer = d.OFFER_SIDE_BID if side == "bid" else d.OFFER_SIDE_ASK
    frames = []
    for a, b in month_edges(start, end):
        for attempt in range(4):
            try:
                df = d.fetch(XAU, d.INTERVAL_MIN_1, offer,
                             dt.datetime(a.year, a.month, a.day),
                             dt.datetime(b.year, b.month, b.day, 23, 59))
                n = 0 if df is None else len(df)
                print(f"  {side} {a}..{b}  {n:>7,} rows", flush=True)
                if n:
                    frames.append(df)
                break
            except Exception as e:                      # transient host errors
                print(f"  {side} {a}..{b}  retry {attempt+1}: {e}", flush=True)
                import time; time.sleep(2 ** attempt)
        else:
            sys.exit(f"FAILED permanently on {a}..{b} — do not proceed with a hole")
    import pandas as pd
    return pd.concat(frames).sort_index()


def fetch_lse(side, start, end):
    if not os.environ.get("LSE_API_KEY", "").strip():
        sys.exit("LSE_API_KEY is not set in this environment.")
    from lse import LSE
    c = LSE(api_key=os.environ["LSE_API_KEY"], timeout=120)
    import pandas as pd
    rows, cur = [], dt.datetime(start.year, start.month, start.day, tzinfo=UTC)
    stop = dt.datetime(end.year, end.month, end.day, 23, 59, tzinfo=UTC)
    while cur < stop:
        page = c.candles("XAU/USD", "1m", start=cur.isoformat(), end=stop.isoformat(),
                         limit=5000, order="asc")
        if not page:
            break
        rows.extend(page)
        last = pd.to_datetime(page[-1]["timestamp"], utc=True).to_pydatetime()
        if last <= cur:
            break
        cur = last + dt.timedelta(minutes=1)
        print(f"  lse {len(rows):>9,} rows -> {last}", flush=True)
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.set_index("timestamp").sort_index()


def save(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        for ts, r in df.iterrows():
            t = ts.to_pydatetime()
            if t.tzinfo is None:
                t = t.replace(tzinfo=UTC)
            w.writerow([t.astimezone(UTC).isoformat(),
                        r["open"], r["high"], r["low"], r["close"], r.get("volume", 0)])
    print(f"saved {len(df):,} rows -> {path}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="dukascopy", choices=["dukascopy", "lse"])
    ap.add_argument("--side", default="both", choices=["bid", "ask", "both"])
    a = ap.parse_args()
    fn = fetch_duka if a.source == "dukascopy" else fetch_lse
    sides = ["bid", "ask"] if a.side == "both" else [a.side]
    for s in sides:
        print(f"=== {a.source} XAU/USD 1m {s} {START} .. {END} ===", flush=True)
        df = fn(s, START, END)
        save(df, os.path.join(RAW, f"xauusd_1m_{s}_{a.source}.csv.gz"))
