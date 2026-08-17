"""Fetch NQ / VIX / Mag-7 from London Strategic Edge into the backtest's CSV format.

VERIFIED AGAINST lse-data 0.14.0 SOURCE (not the doc pages, which are blocked
by this container's egress proxy):
  base URL   https://api.londonstrategicedge.com/vault
  auth       HTTP header  x-api-key: <key>        (not Bearer, not a query param)
  endpoint   GET /vault/candles
  params     symbol, timeframe, order, limit, dataset, start, end
  limit      server-side hard cap 5000 rows  (min(int(limit), 5000) in client.py)
  intervals  1s 5s 15s 30s 1m 3m 5m 15m 30m 1h 4h 1d 1w 1mo
  catalog    GET /vault/catalog -> {dataset, symbol, ticks, first_tick, last_tick, years}
  BAR TIME   the vault's `ts` is the bar OPEN, renamed to `timestamp` by the
             client. This matches what the backtest requires — no adjustment.

THE KEY IS NEVER PRINTED, LOGGED OR WRITTEN. It is read from os.environ only.
"""
import os, sys, csv, time, datetime as dt

TFS = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m"}
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "nq")
MAG7 = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA"]


def client():
    if "LSE_API_KEY" not in os.environ or not os.environ["LSE_API_KEY"].strip():
        sys.exit("LSE_API_KEY is not set in this environment. Export it and re-run.\n"
                 "Do NOT pass the key on the command line — it lands in shell history.")
    try:
        from lse import LSE
    except ImportError:
        sys.exit("pip install lse-data")
    return LSE(api_key=os.environ["LSE_API_KEY"], timeout=120)


def find_symbol(c, want=("NQ", "NASDAQ", "NDX", "MNQ")):
    """The exact NQ symbol string is NOT documented anywhere public. Discover it
    from the catalog rather than guessing — a guessed symbol either 404s or,
    worse, silently returns a different instrument."""
    rows = c.datasets()
    fut = [r for r in rows if r.get("dataset") == "futures"]
    print(f"catalog: {len(rows)} instruments, {len(fut)} in the futures dataset")
    hits = [r for r in rows
            if any(w.lower() in str(r.get("symbol", "")).lower() for w in want)]
    for r in sorted(hits, key=lambda x: -(x.get("ticks") or 0))[:25]:
        print(f"  {r.get('dataset'):12} {r.get('symbol'):18} "
              f"ticks={r.get('ticks'):>14,} {r.get('first_tick')} .. {r.get('last_tick')}")
    if not hits:
        print("  no NQ-like symbol found. Print the futures list with:")
        print("    python3 -c \"from lse import LSE; "
              "[print(r) for r in LSE().datasets('futures')]\"")
    return hits


def fetch(c, symbol, timeframe, start, end, dataset=None, cap=5000, pause=0.25):
    """Page forward on `start`. The server caps at 5000 rows per call, so the
    loop advances past the last bar returned until it reaches `end`."""
    rows, cur, seen = [], start, set()
    while True:
        page = c.candles(symbol, timeframe, start=cur, end=end,
                         limit=cap, order="asc", dataset=dataset)
        if not page:
            break
        fresh = [r for r in page if r["timestamp"] not in seen]
        if not fresh:
            break
        for r in fresh:
            seen.add(r["timestamp"])
        rows += fresh
        last = fresh[-1]["timestamp"]
        print(f"  {symbol} {timeframe}: {len(rows):>8,} rows  ->  {last}", flush=True)
        if len(page) < cap:
            break
        cur = last                       # inclusive overlap is removed by `seen`
        time.sleep(pause)
    rows.sort(key=lambda r: r["timestamp"])
    return rows


def write(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        for r in rows:
            w.writerow([r["timestamp"], r["open"], r["high"], r["low"],
                        r["close"], r.get("volume", 0)])
    print(f"  wrote {len(rows):,} rows -> {path}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true",
                    help="list NQ-like symbols from the catalog and exit")
    ap.add_argument("--symbol", help="exact NQ symbol, once discovered")
    ap.add_argument("--dataset", default=None, help="e.g. futures")
    ap.add_argument("--start", default="2019-01-01")
    ap.add_argument("--end", default=dt.date.today().isoformat())
    ap.add_argument("--tfs", default="1m,5m,15m,30m")
    ap.add_argument("--extras", action="store_true", help="also pull VIX and the Mag 7")
    a = ap.parse_args()

    c = client()
    if a.discover or not a.symbol:
        find_symbol(c)
        if not a.symbol:
            sys.exit("\nRe-run with --symbol <exact symbol> once you have confirmed it above.")
    for tf in a.tfs.split(","):
        tf = tf.strip()
        if tf not in TFS:
            print(f"skipping unsupported timeframe {tf!r}"); continue
        write(fetch(c, a.symbol, tf, a.start, a.end, a.dataset),
              os.path.join(OUT, f"nq_{tf}.csv"))
    if a.extras:
        for sym, name in [("VIX", "vix_daily")] + [(s, s.lower()) for s in MAG7]:
            try:
                write(fetch(c, sym, "1d", a.start, a.end), os.path.join(OUT, f"{name}.csv"))
            except Exception as e:
                print(f"  {sym}: {type(e).__name__}: {e}")
