"""Load a TradingView chart-data CSV export.

TradingView: right-click chart -> Export chart data -> CSV.
Accepts the usual column spellings and either a unix 'time' or a datetime.
"""
import pandas as pd


def load_csv(path):
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    tcol = next((c for c in ("time", "date", "datetime", "timestamp")
                 if c in df.columns), None)
    if tcol is None:
        raise SystemExit(f"no time column; found {list(df.columns)}")
    s = df[tcol]
    df["dt"] = (pd.to_datetime(s, unit="s")
                if pd.api.types.is_numeric_dtype(s) else pd.to_datetime(s))
    need = ["open", "high", "low", "close"]
    miss = [c for c in need if c not in df.columns]
    if miss:
        raise SystemExit(f"missing columns {miss}; found {list(df.columns)}")
    df = df.set_index("dt").sort_index()
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    return df[need].dropna()
