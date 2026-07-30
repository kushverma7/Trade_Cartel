"""Synthetic OHLC generator -- ONLY for proving the pipeline runs.

Results on synthetic data are meaningless as evidence: the series has no
real market structure, so any PF it produces is noise. Its single purpose
is to verify the code path end to end before real bars arrive.
"""
import numpy as np, pandas as pd


def make(bars=20000, tf="15min", start="2025-01-02", seed=7, px0=2600.0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=bars, freq=tf, tz=None)
    idx = idx[(idx.dayofweek < 5)]
    n = len(idx)
    step = rng.standard_normal(n) * 1.6 + np.sin(np.arange(n) / 400) * 0.35
    close = px0 + np.cumsum(step)
    spread = np.abs(rng.standard_normal(n)) * 1.4 + 0.4
    open_ = np.r_[close[0], close[:-1]]
    high = np.maximum(open_, close) + spread
    low = np.minimum(open_, close) - spread
    return pd.DataFrame({"open": open_, "high": high, "low": low,
                         "close": close}, index=idx)
