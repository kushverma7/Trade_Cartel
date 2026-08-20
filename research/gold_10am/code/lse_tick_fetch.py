"""Download LONDON STRATEGIC EDGE XAU/USD TICK data for the replication study.

WHAT THIS USES, AND WHY IT IS THE RIGHT DOOR
--------------------------------------------
`lse.vault.history(symbol, timeframe="tick", ...)` is the vault's raw-tape
export: it POSTs /vault/export, polls the job, and downloads a Parquet file
with resume. That is LSE's own bulk mechanism for tick history — not a candle
endpoint, not an aggregation. Verified from lse-data 0.14.0 source, not from
the doc pages.

Deliberately NOT used:
  - /v1/candles on data-api — its own description says it "queries 1-minute
    candles from the database and aggregates", so it can never return ticks.
  - the websocket `stream(start=...)` replay — capped at 24 hours of history.
  - Dukascopy — the whole point of this study is a second, independent feed.

PARTITIONING AND RESUMABILITY
Two years of gold ticks is large, so the pull is partitioned by month, each
month cached as its own Parquet file, and a completed month is never re-fetched.
Interrupt and re-run freely. Nothing is aggregated or resampled here — the raw
tape is preserved exactly as delivered.

THE KEY IS READ FROM os.environ ONLY. Never printed, never logged, never
written to disk, never passed on argv.
"""
import os, sys, time, argparse, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw", "lse_ticks")

START = dt.date(2024, 8, 20)
END = dt.date(2026, 8, 19)
SYMBOL = "XAU/USD"


def months(a, b):
    cur = dt.date(a.year, a.month, 1)
    while cur <= b:
        nxt = dt.date(cur.year + (cur.month == 12), (cur.month % 12) + 1, 1)
        yield max(cur, a), min(nxt - dt.timedelta(days=1), b)
        cur = nxt


def client():
    key = os.environ.get("LSE_API_KEY", "").strip()
    if not key:
        sys.exit(
            "LSE_API_KEY is not set in this environment.\n"
            "Create a free key at https://londonstrategicedge.com/data (sign in -> API keys),\n"
            "then export it into the environment. Do NOT paste it into chat: this repo is public."
        )
    from lse import LSE
    return LSE(api_key=key, timeout=1800)


def preflight(c):
    """Prove, before pulling 24 months, that this key can actually see gold ticks."""
    print("preflight:", flush=True)
    print(f"  tier                : {c.tier}", flush=True)
    rows = [r for r in c.datasets() if r.get("symbol") == SYMBOL]
    if not rows:
        sys.exit(f"  '{SYMBOL}' is NOT in this key's vault catalog.\n"
                 f"  The free 'registered' tier is documented as '8 trial symbols'; if gold is\n"
                 f"  not one of them this key cannot serve this study. Check /databank.")
    for r in rows:
        print(f"  dataset={r.get('dataset')} ticks={r.get('ticks'):,} "
              f"{r.get('first_tick')} .. {r.get('last_tick')}", flush=True)
    meta = c.vault_meta()
    tfs = meta.get("timeframes") or meta.get("candle_timeframes") or []
    print(f"  timeframes offered  : {tfs}", flush=True)
    if tfs and "tick" not in [str(t).lower() for t in tfs]:
        print("  NOTE: 'tick' is not in the advertised timeframe list; history() may still\n"
              "        accept it (the docstring documents it). Continuing.", flush=True)
    return rows[0].get("dataset")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeframe", default="tick")
    ap.add_argument("--dataset", default=None, help="override catalog auto-resolution")
    ap.add_argument("--preflight-only", action="store_true")
    a = ap.parse_args()

    os.makedirs(RAW, exist_ok=True)
    c = client()
    ds = a.dataset or preflight(c)
    if a.preflight_only:
        return

    done, failed = [], []
    for lo, hi in months(START, END):
        tag = f"{lo:%Y-%m}"
        path = os.path.join(RAW, f"xauusd_{a.timeframe}_{tag}.parquet")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"  {tag}  cached ({os.path.getsize(path)/1e6:.1f} MB)", flush=True)
            done.append(path)
            continue
        for attempt in range(4):
            try:
                t0 = time.time()
                out = c.history(SYMBOL, dataset=ds, timeframe=a.timeframe,
                                start=lo.isoformat(), end=hi.isoformat(),
                                dest=path, dataframe=False, timeout=3600)
                sz = os.path.getsize(out) if os.path.exists(out) else 0
                print(f"  {tag}  {sz/1e6:>8.1f} MB in {time.time()-t0:.0f}s", flush=True)
                done.append(out)
                break
            except Exception as e:
                wait = 2 ** attempt
                print(f"  {tag}  attempt {attempt+1} failed: {e} (retry in {wait}s)", flush=True)
                time.sleep(wait)
        else:
            failed.append(tag)

    print(f"\n{len(done)} monthly files in {RAW}")
    if failed:
        print(f"FAILED months (re-run to resume): {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()
