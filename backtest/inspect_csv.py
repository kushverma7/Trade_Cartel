#!/usr/bin/env python3
"""
Inspect and normalise any exported bar file, then say whether it is usable.

Point this at whatever the London Strategic Edge builder (or TradingView, or
anything else) produces. It figures out the delimiter, the timestamp format,
the column naming, decimal separators and tick-vs-bar data, then reports what
it found and whether there is enough of it to run a train/test split.

  python3 -m backtest.inspect_csv myfile.csv
  python3 -m backtest.inspect_csv myfile.csv --resample 15min --save bars.csv
"""
import argparse, sys
import numpy as np, pandas as pd

TIME_KEYS = ("time", "date", "datetime", "timestamp", "dt",
             "local time", "gmt time", "open time", "bar")
ALIASES = {
    "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume",
    "bid": "close", "last": "close", "price": "close", "vol": "volume",
    "adj close": "close",
}


def sniff(path):
    with open(path, "r", errors="replace") as fh:
        head = [fh.readline() for _ in range(5)]
    text = "".join(head)
    sep = max([",", ";", "\t", "|"], key=text.count)
    return sep, head[0].strip()


def load(path):
    sep, header = sniff(path)
    df = pd.read_csv(path, sep=sep, engine="python")
    df.columns = [str(c).strip().lower().lstrip("﻿") for c in df.columns]
    df = df.rename(columns={c: ALIASES.get(c, c) for c in df.columns})

    tcol = next((c for c in df.columns if any(k == c or k in c for k in TIME_KEYS)), None)
    if tcol is None:
        # exporters (and pandas' own to_csv) frequently write the timestamp as
        # an UNNAMED first column. Try any non-price column that actually
        # parses as dates before giving up.
        for c in df.columns:
            if c in ("open", "high", "low", "close", "volume"):
                continue
            try:
                probe = pd.to_datetime(df[c], errors="coerce")
            except Exception:
                continue
            if probe.notna().mean() > 0.9:
                tcol = c
                print(f"  note: using unnamed/undeclared column {c!r} as the timestamp")
                break
    if tcol is None:
        raise SystemExit(f"no timestamp column found in {list(df.columns)}")

    s = df[tcol]
    if pd.api.types.is_numeric_dtype(s):
        unit = "s" if s.max() < 1e11 else "ms"
        dt = pd.to_datetime(s, unit=unit)
    else:
        # DO NOT use format="mixed" here. It infers a format PER ELEMENT, so
        # a day-first file parses "02/01/2025" as 2 Jan and "13/01/2025" as
        # 13 Jan -- no error, no NaT, and the series is silently scrambled
        # across months. Caught on a test file that read as Jan->Oct when it
        # was Jan->Feb. One consistent format, verified by monotonicity.
        cands = []
        for dayfirst in (False, True):
            try:
                p_ = pd.to_datetime(s, errors="coerce", dayfirst=dayfirst)
            except Exception:
                continue
            nat = float(p_.isna().mean())
            mono = bool(p_.dropna().is_monotonic_increasing)
            cands.append((nat, not mono, dayfirst, p_))
        if not cands:
            raise SystemExit("could not parse the timestamp column")
        # prefer: fewest unparseable, then strictly increasing
        cands.sort(key=lambda t: (t[0], t[1]))
        nat, notmono, dayfirst, dt = cands[0]
        if notmono:
            print("  WARNING: timestamps are not monotonically increasing after "
                  "parsing. Check the date format and column order before "
                  "trusting any result from this file.")
        if dayfirst:
            print("  note: parsed as DAY-first (dd/mm/yyyy)")
    df["dt"] = dt
    df = df.dropna(subset=["dt"]).set_index("dt").sort_index()
    if getattr(df.index, "tz", None) is not None:
        df.index = df.index.tz_convert(None)

    for c in ("open", "high", "low", "close", "volume"):
        if c in df.columns and df[c].dtype == object:
            df[c] = pd.to_numeric(
                df[c].astype(str).str.replace(" ", "").str.replace(",", "."),
                errors="coerce")
    return df, sep, header


def resample(df, rule):
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    if "volume" in df.columns:
        agg["volume"] = "sum"
    return df.resample(rule).agg(agg).dropna(subset=["open", "high", "low", "close"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path"); ap.add_argument("--resample"); ap.add_argument("--save")
    a = ap.parse_args()

    df, sep, header = load(a.path)
    print(f"delimiter : {sep!r}")
    print(f"header    : {header[:110]}")
    print(f"columns   : {list(df.columns)}")

    have = [c for c in ("open", "high", "low", "close") if c in df.columns]
    if have != ["open", "high", "low", "close"]:
        if "close" in df.columns:
            print("\nOnly a price column found — this looks like TICK or "
                  "close-only data. Re-run with --resample 15min to build bars.")
        else:
            raise SystemExit(f"need open/high/low/close; found {list(df.columns)}")

    if a.resample:
        df = resample(df, a.resample)
        print(f"resampled : {a.resample}")

    n = len(df)
    span = df.index[-1] - df.index[0]
    gaps = df.index.to_series().diff().dropna()
    step = gaps.median()
    print(f"\nbars      : {n:,}")
    print(f"range     : {df.index[0]:%Y-%m-%d %H:%M}  ->  {df.index[-1]:%Y-%m-%d %H:%M}"
          f"   ({span.days} days)")
    print(f"bar size  : {step}   (median gap)")
    bad = int((df.high < df.low).sum() + (df.high < df.open).sum()
              + (df.high < df.close).sum() + (df.low > df.open).sum()
              + (df.low > df.close).sum())
    print(f"OHLC sane : {'yes' if bad == 0 else f'NO — {bad} impossible bars'}")
    print(f"duplicates: {int(df.index.duplicated().sum())}")
    print(f"NaNs      : {int(df[have].isna().sum().sum())}")

    print("\nVERDICT")
    ok = True
    if n < 5000:
        print(f"  {n:,} bars is thin. The split halves it, and a test block "
              "under ~30 trades concludes nothing. Export more history if you can.")
        ok = n >= 2000
    else:
        print(f"  {n:,} bars is enough to split 60/40 and still test properly.")
    if bad:
        print("  Impossible OHLC bars present — fix or drop these first."); ok = False
    if ok:
        print("\n  USABLE. Run:")
        tgt = a.save or a.path
        print(f"    python3 -m backtest.optimize --csv {tgt}")

    if a.save:
        df.to_csv(a.save)
        print(f"\nnormalised file written to {a.save}")


if __name__ == "__main__":
    main()
