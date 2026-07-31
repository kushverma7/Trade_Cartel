"""Single entry point for loading exported bar files.

There used to be a second, weaker parser here. It did not understand
semicolon delimiters, day-first dates, O/H/L/C aliases or unnamed timestamp
columns, and it choked on a file the inspector had just normalised -- two
loaders, two behaviours, one of them wrong. Everything now goes through the
inspector's parser, which has tests behind it.
"""
from backtest.inspect_csv import load as _load, resample


def load_csv(path, rule=None):
    df, _sep, _hdr = _load(path)
    need = ["open", "high", "low", "close"]
    # keep volume when the export has it -- V11 (Valentini volume tsunami)
    # silently compared against a constant when this dropped it
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise SystemExit(f"missing columns {missing}; found {list(df.columns)}")
    if rule:
        df = resample(df, rule)
    keep = need + (["volume"] if "volume" in df.columns else [])
    return df[keep].dropna(subset=need)
