"""
Rule book V3 — test the two survivors, in the priority order V3 specifies.

V3 removed what the data killed (pure level-touch entries, Setups 1 and 4 of
V2) and kept what survived (the 1.5 ATR stop floor and the CPR gate). This
module tests exactly its stated priorities:

  1. Setup B, gap fill to CPR, with the CORRECTED rejection window of 3-6
     bars. V2 crippled this by demanding the rejection close on the very next
     bar, which cut the sample from 115 to 19. That was an implementation
     error on my side, not a property of the rule.

  2. Setup A, CPR-gated momentum, stress-tested three ways:
       a. does the gate survive on other timeframes
       b. does restricting to the London/NY overlap improve expectancy
       c. is the "narrow" definition parameter-stable

  3. Setup C is deliberately not run until 1 and 2 are settled.

ON "A SECOND INSTRUMENT"
  V3 asks whether the CPR gate holds on a second instrument. It cannot be
  answered here: `data/` contains XAUUSD only, and there is no US30 series in
  this repo. Timeframe robustness is a real but WEAKER substitute -- the bars
  overlap, so the tests are not independent. Stated rather than skipped.
"""
import argparse

import numpy as np
import pandas as pd

from backtest.io import load_csv
from backtest.rulebook import daily_context
from backtest.level_reaction import _atr
from backtest.rulebook_v2 import manage, stats, SLIP, ATR_STOP_MIN, TRAIL_ATR


def setup_B(df, reject_lo=1, reject_hi=6, horizon=None):
    """Gap fill to CPR. Rejection anywhere in the first `reject_hi` bars."""
    ctx = daily_context(df)
    A = _atr(df)
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    key = pd.Series(pd.to_datetime(df.index.date), index=df.index)
    C = ctx.reindex(key.values)
    step_min = (df.index[1] - df.index[0]).total_seconds() / 60.0
    hz = horizon or max(4, int(120 / step_min))     # V3: 90-120 minute time stop
    rows = []
    for i in range(100, len(c) - 20 - hz):
        if key.values[i] == key.values[i - 1]:
            continue                                 # session open only
        a = A[i]
        pp = C["PP"].values[i]
        if not np.isfinite(a) or a <= 0 or not np.isfinite(pp):
            continue
        gap = o[i] - c[i - 1]
        if not (0.5 * a < abs(gap) < 3.0 * a):
            continue                                 # "moderate" gap
        d = -1 if gap > 0 else 1                     # fade toward the CPR
        if (pp - o[i]) * d <= 0:
            continue                                 # CPR must be the magnet
        # V3: rejection of the gap extreme ANYWHERE in the first 3-6 bars
        ext = o[i]
        for k in range(i + reject_lo, i + reject_hi + 1):
            if k >= len(c):
                break
            ext = max(ext, h[k]) if d < 0 else min(ext, l[k])
            rejected = (c[k] < o[i]) if d < 0 else (c[k] > o[i])
            if not rejected:
                continue
            entry = c[k] + d * SLIP
            stop = ext - d * 1.25 * a
            risk = abs(entry - stop)
            if risk <= 0 or abs(pp - entry) / risk < 1.0:
                break
            r = manage(h, l, c, k, d, entry, stop, pp, hz, TRAIL_ATR, a)
            if np.isfinite(r):
                rows.append({"R": r, "i": i, "dir": d})
            break
    return pd.DataFrame(rows)


def setup_A(df, narrow_q=0.33, session=None, lookback=60):
    """CPR-gated momentum. `session` = (start_hour, end_hour) UTC or None."""
    sess = daily_context(df, lookback=lookback)
    A = _atr(df)
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    rngb = np.maximum(h - l, 1e-9)
    strong = np.abs(c - o) >= 0.6 * rngb
    key = pd.Series(pd.to_datetime(df.index.date), index=df.index)
    C = sess.reindex(key.values)
    # rebuild the narrow band at the requested quantile
    w = sess["pivot_width"]
    thr = w.rolling(lookback).quantile(narrow_q)
    narrow_by_day = (w <= thr)
    NARROW = pd.Series(narrow_by_day.values, index=narrow_by_day.index)
    is_narrow = key.map(NARROW).fillna(False).values
    hh = df.index.hour + df.index.minute / 60.0
    in_sess = np.ones(len(c), bool) if session is None else (
        (hh >= session[0]) & (hh < session[1]))
    rows = []
    for i in range(100, len(c) - 100):
        a = A[i]
        if not np.isfinite(a) or a <= 0 or not strong[i] or not in_sess[i]:
            continue
        rel = C["rel"].values[i]
        tc, bc = C["TC"].values[i], C["BC"].values[i]
        if not np.isfinite(tc):
            continue
        if not (is_narrow[i] or rel == "inside"):
            continue                                  # THE GATE
        d = 1 if c[i] > tc else (-1 if c[i] < bc else 0)
        if d == 0:
            continue
        # V3: direction must align with the two-day bias
        if d > 0 and rel in ("lower", "overlap_lower"):
            continue
        if d < 0 and rel in ("higher", "overlap_higher"):
            continue
        entry = c[i] + d * SLIP
        stop = (tc if d > 0 else bc) - d * ATR_STOP_MIN * a
        risk = abs(entry - stop)
        if risk <= 0:
            continue
        r = manage(h, l, c, i, d, entry, stop, entry + d * 2 * risk, 96, TRAIL_ATR, a)
        if np.isfinite(r):
            rows.append({"R": r, "i": i, "dir": d})
    return pd.DataFrame(rows)


def halves(t, label):
    stats(t, label)
    if len(t) >= 40:
        mid = t["i"].median()
        stats(t[t["i"] <= mid], "    first half")
        stats(t[t["i"] > mid], "    OOS half")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rule", default="30min")
    a = ap.parse_args()
    df = load_csv("data/xauusd_15m.csv.gz", rule=a.rule)
    print(f"\nRULE BOOK V3 — XAUUSD {a.rule}, {len(df):,} bars\n")

    print("PRIORITY 1 — Setup B (gap fill), rejection window restored")
    for hi in (1, 3, 6, 10):
        t = setup_B(df, reject_hi=hi)
        halves(t, f"  reject within {hi} bar(s)") if hi == 6 else stats(t, f"  reject within {hi} bar(s)")

    print("\nPRIORITY 2a — Setup A, does the gate hold across timeframes?")
    for rule in ("15min", "30min", "60min", "240min"):
        d2 = load_csv("data/xauusd_15m.csv.gz", rule=rule)
        stats(setup_A(d2), f"  {rule}")

    print("\nPRIORITY 2b — Setup A, session restriction")
    for nm, s in (("all hours", None), ("LDN/NY overlap 13:30-16:30", (13.5, 16.5)),
                  ("NY first 90m 13:30-15:00", (13.5, 15.0)),
                  ("London 08:00-12:00", (8.0, 12.0))):
        stats(setup_A(df, session=s), f"  {nm}")

    print("\nPRIORITY 2c — Setup A, is 'narrow' parameter-stable?")
    for q in (0.20, 0.25, 0.33, 0.40, 0.50):
        stats(setup_A(df, narrow_q=q), f"  narrow = bottom {int(q * 100)}%")


if __name__ == "__main__":
    main()
