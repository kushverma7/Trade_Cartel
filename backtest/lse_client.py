#!/usr/bin/env python3
"""
London Strategic Edge data client.

CREDENTIAL HANDLING: the key is read from the LSE_API_KEY environment
variable and is never written to disk, never logged, and never echoed. Do
not pass it as a command-line argument -- argv is visible in the process
table and in shell history.

    export LSE_API_KEY='...'
    python3 -m backtest.lse_client --probe
    python3 -m backtest.lse_client --symbol XAUUSD --tf 15m --save data/xau15.csv

CURRENT STATUS: londonstrategicedge.com is NOT reachable from this
container. DNS resolves (Cloudflare), but the policy-enforcing egress proxy
refuses the connection outright -- no response at all, not a 403 from the
site. The key is irrelevant until the domain is added to the environment's
network allowlist; authentication is not the blocker, egress policy is.

Because the API shape is undocumented here, --probe walks a list of
plausible endpoints and reports which respond, rather than assuming one.
"""
import argparse, json, os, sys
import pandas as pd
import requests

HOSTS = ["https://api.londonstrategicedge.com", "https://londonstrategicedge.com",
         "https://data.londonstrategicedge.com"]
PATHS = ["/v1/bars", "/api/v1/bars", "/api/bars", "/data/bars", "/v1/ohlc",
         "/api/ohlc", "/v1/candles", "/api/candles", "/data/export",
         "/v1/instruments", "/api/instruments", "/v1/status", "/api/status"]


def _load_dotenv(path=".env"):
    """Read .env if present. That file is gitignored -- a live credential
    must never enter git history, where it survives forever, is visible to
    every collaborator, and cannot be removed without a history rewrite.
    A private chat does not make a public-by-default repo a safe store.
    For persistence across sessions, set LSE_API_KEY in the environment's
    own variable settings instead; this container is ephemeral."""
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def key():
    _load_dotenv()
    k = os.environ.get("LSE_API_KEY", "").strip()
    if not k:
        sys.exit("LSE_API_KEY is not set. export it first; do not pass it as an argument.")
    return k


def headers(k):
    return {"Authorization": f"Bearer {k}", "X-API-Key": k,
            "Accept": "application/json", "User-Agent": "trade-cartel/1.0"}


def probe(timeout=15):
    k = key(); h = headers(k); hits = []
    for host in HOSTS:
        for path in PATHS:
            url = host + path
            try:
                r = requests.get(url, headers=h, timeout=timeout)
            except Exception as e:
                print(f"  {url:<58} unreachable ({type(e).__name__})")
                continue
            body = (r.text or "")[:120].replace("\n", " ")
            print(f"  {url:<58} {r.status_code}  {body}")
            if r.status_code < 400:
                hits.append(url)
    if not hits:
        print("\nNothing responded. The domain is blocked by the environment's "
              "network policy — this is not an authentication problem.")
    return hits


def fetch(symbol, tf, start=None, end=None, url=None, timeout=60):
    k = key()
    params = {"symbol": symbol, "instrument": symbol, "timeframe": tf,
              "interval": tf, "resolution": tf}
    if start: params["from"] = params["start"] = start
    if end:   params["to"] = params["end"] = end
    targets = [url] if url else [h + p for h in HOSTS for p in PATHS[:8]]
    for u in targets:
        try:
            r = requests.get(u, headers=headers(k), params=params, timeout=timeout)
        except Exception:
            continue
        if r.status_code >= 400:
            continue
        try:
            data = r.json()
        except Exception:
            from io import StringIO
            return pd.read_csv(StringIO(r.text))
        for node in ("bars", "data", "candles", "results", "ohlc"):
            if isinstance(data, dict) and node in data:
                return pd.DataFrame(data[node])
        if isinstance(data, list):
            return pd.DataFrame(data)
        return pd.DataFrame(data)
    sys.exit("no endpoint returned data — run --probe first")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--symbol", default="XAUUSD"); ap.add_argument("--tf", default="15m")
    ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--url"); ap.add_argument("--save")
    a = ap.parse_args()
    if a.probe:
        probe(); return
    df = fetch(a.symbol, a.tf, a.start, a.end, a.url)
    print(df.head().to_string())
    print(f"\nrows: {len(df):,}")
    if a.save:
        os.makedirs(os.path.dirname(a.save) or ".", exist_ok=True)
        df.to_csv(a.save, index=False)
        print(f"saved {a.save}\n\nnext:\n  python3 -m backtest.inspect_csv {a.save}")


if __name__ == "__main__":
    main()
