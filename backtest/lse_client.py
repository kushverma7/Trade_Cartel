#!/usr/bin/env python3
"""
London Strategic Edge data puller, built on their official `lse-data` client.

    pip install lse-data                    # already installed
    python3 -m backtest.lse_client --check
    python3 -m backtest.lse_client --symbol XAU/USD --tf 15m --start 2021-01-01 \
        --save data/xau_15m.csv.gz

WHY THIS SOLVES THE FILE-SIZE PROBLEM
Nothing has to travel through chat. The data lands directly in the container
from the API, so years of bars are a non-issue -- the export size limit only
ever existed because the file had to be carried by hand.

  candles()  paged OHLCV, capped per call by the plan's row limit
  history()  server-side bulk job: builds the file, polls, downloads with
             resume. This is the route for very long ranges or tick data.

CURRENT BLOCKER — not authentication
    LSEError [0] request failed before an HTTP response:
    Tunnel connection failed: 403 Forbidden

The session's egress proxy refuses the CONNECT tunnel to
api.londonstrategicedge.com, so the request never leaves the container and
the key never reaches their server. `authenticated` reads False for the same
reason. Fix by adding londonstrategicedge.com (and api.*) to the
environment's network allowlist:
https://code.claude.com/docs/en/claude-code-on-the-web

CREDENTIAL: read from LSE_API_KEY, falling back to a gitignored .env.
Never passed on argv, never logged, never committed.
"""
import argparse, os, sys
import pandas as pd


def _key(required=True):
    if not os.environ.get("LSE_API_KEY") and os.path.exists(".env"):
        for line in open(".env"):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    k = os.environ.get("LSE_API_KEY", "").strip()
    if not k and required:
        sys.exit("LSE_API_KEY not set (env or .env)")
    return k


def client():
    import lse
    return lse.LSE(api_key=_key())


def egress_ok(host="api.londonstrategicedge.com", timeout=15):
    """Can we open a tunnel to the API host at all? Independent of any key."""
    import socket, urllib.request, urllib.error
    try:
        urllib.request.urlopen(f"https://{host}/", timeout=timeout)
        return True, "reachable"
    except urllib.error.HTTPError as e:
        return True, f"reachable (HTTP {e.code} at /, which is normal)"
    except Exception as e:
        msg = str(e)
        if "tunnel" in msg.lower() or "403" in msg or "CONNECT" in msg:
            return False, "blocked by the environment's egress proxy (CONNECT refused)"
        return False, f"unreachable — {type(e).__name__}: {msg[:90]}"


def check():
    """Report EVERY gate in one run.

    An earlier version exited at the missing-credential check, which hid the
    network failure behind it and made it look like setting the key would be
    enough. Both gates are independent and both must be reported, or the user
    fixes one, re-runs, and discovers the second only then.
    """
    print("GATE 1 — credential")
    k = _key(required=False)
    src = ("environment variable" if os.environ.get("LSE_API_KEY") and
           not os.path.exists(".env") else ".env or environment")
    if k:
        print(f"  PASS  key present ({len(k)} chars, from {src})")
    else:
        print("  FAIL  LSE_API_KEY not set in the environment and no .env file.")
        print("        Set it in the environment's variable settings — .env does")
        print("        not survive a new container.")

    print("\nGATE 2 — network egress (independent of the key)")
    ok, detail = egress_ok()
    print(f"  {'PASS' if ok else 'FAIL'}  api.londonstrategicedge.com: {detail}")
    if not ok:
        print("        Allowlist londonstrategicedge.com and")
        print("        api.londonstrategicedge.com in the environment's network")
        print("        settings. No credential can bypass this.")

    if not (k and ok):
        print("\nBoth gates must pass before any data can be pulled.")
        print("Neither one alone is sufficient. Route around both by exporting")
        print("bars from the LSE builder and running:")
        print("  python3 -m backtest.inspect_csv <file.csv.gz>")
        return

    print("\nGATE 3 — authenticated call")
    c = client()
    print(f"  authenticated : {c.authenticated}")
    print(f"  tier          : {c.tier or '(none)'}")
    try:
        cat = c.catalog("commodities")
        print(f"  catalog       : {len(cat)} commodity symbols")
        for row in cat[:12]:
            print("     ", row)
    except Exception as e:
        print(f"  catalog       : FAILED — {type(e).__name__}: {str(e)[:160]}")


def pull(symbol, tf, start, end, save, bulk=False):
    c = client()
    if bulk:
        df = c.history(symbol, timeframe=tf, start=start, end=end, dataframe=True)
    else:
        rows, cursor = [], start
        while True:
            batch = c.candles(symbol, tf, start=cursor, end=end, limit=5000, order="asc")
            if not batch:
                break
            rows.extend(batch)
            last = batch[-1]
            nxt = last.get("time") or last.get("timestamp") or last.get("t")
            print(f"  {len(rows):>8,} bars ... through {nxt}")
            if len(batch) < 5000 or nxt == cursor:
                break
            cursor = nxt
        df = pd.DataFrame(rows)
    print(f"\nrows: {len(df):,}")
    if save:
        os.makedirs(os.path.dirname(save) or ".", exist_ok=True)
        df.to_csv(save, index=False,
                  compression="gzip" if save.endswith(".gz") else None)
        print(f"saved {save}\n\nnext:\n  python3 -m backtest.inspect_csv {save}"
              f"\n  python3 -m backtest.optimize   --csv {save}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--symbol", default="XAU/USD")
    ap.add_argument("--tf", default="15m")
    ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--bulk", action="store_true", help="server-side export job")
    ap.add_argument("--save")
    a = ap.parse_args()
    if a.check:
        check(); return
    pull(a.symbol, a.tf, a.start, a.end, a.save, a.bulk)


if __name__ == "__main__":
    main()
