"""
Do key levels actually DO anything? A first-passage test against a matched
random control.

THE QUESTION
  The SpacemanBTC key-level indicator draws ~36 lines. Traders treat a touch
  as information: price is supposed to react there. That is a testable claim
  and it has never been tested in this repo -- BUG-017 measured that levels
  fail as TARGETS, but that is a different question from whether price
  reacts at them at all.

THE TEST
  For every touch of a level, ask a first-passage question:
      from the touch, does price travel R ATR AWAY from the level (a bounce)
      or R ATR THROUGH it (a break) first?
  A level with no information gives ~50%. A level that genuinely holds gives
  materially more.

THE CONTROL IS THE POINT
  Bounce rate alone proves nothing, because ANY price in a mean-reverting
  series bounces sometimes. So every real level is matched against a FAKE
  level: the same bar, the same direction of approach, but the level shifted
  by a random 2-6 ATR. The fake is touched under identical volatility and
  identical trend conditions. If real levels carry information, they must
  beat their own shadows.

  This is the corrected-null discipline from BUG-023 applied to levels: the
  control differs from the treatment in exactly one respect -- whether the
  price is a real level or an arbitrary one.

WHAT A RESULT MEANS
  real >> control   levels carry information; trading them can make sense
  real ~= control   the indicator is a MAP, not a SIGNAL. It tells you where
                    you are, not what will happen. Still useful for context,
                    stop placement and journalling -- but any edge must come
                    from something else.
"""
import argparse

import numpy as np
import pandas as pd

from backtest.io import load_csv
from backtest.levels import build


def _atr(df, n=14):
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1.0 / n, adjust=False).mean().values


def first_passage(h, l, i, px, up_first, r, horizon):
    """From bar i, does price reach px+r before px-r (or vice versa)?

    Returns 1 for a BOUNCE (moved back the way it came), 0 for a BREAK,
    np.nan if neither happened inside the horizon.
    """
    hi_t, lo_t = px + r, px - r
    for j in range(i + 1, min(i + horizon + 1, len(h))):
        hit_up = h[j] >= hi_t
        hit_dn = l[j] <= lo_t
        if hit_up and hit_dn:
            return np.nan                       # ambiguous bar, discard
        if hit_up:
            return 0 if up_first else 1
        if hit_dn:
            return 1 if up_first else 0
    return np.nan


def run(df, lv, tol_atr=0.15, r_atr=1.0, horizon=48, seed=0, dense=True):
    A = _atr(df)
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    rng = np.random.default_rng(seed)
    cols = [k for k in lv.columns]
    real, ctrl = [], []

    for name in cols:
        v = lv[name].values
        for i in range(50, len(c) - horizon):
            a = A[i]
            px = v[i]
            if not np.isfinite(px) or not np.isfinite(a) or a <= 0:
                continue
            # a TOUCH: this bar reaches the level, the previous bar had not
            if not (l[i] <= px <= h[i]) or (l[i - 1] <= v[i - 1] <= h[i - 1]):
                continue
            up_first = c[i - 1] < px          # approached from below
            r = a * r_atr
            res = first_passage(h, l, i, px, up_first, r, horizon)
            if np.isfinite(res):
                real.append(res)
            # MATCHED CONTROL. It must be touched on the SAME bar with the
            # SAME geometry, or the comparison is meaningless: a price the bar
            # never reaches is resolved by whichever side is nearer, which is
            # not a bounce at all. (First version of this file placed the
            # control 2-6 ATR away and scored a 99.94% "bounce rate" -- an
            # impossible number that gave the bug away.)
            #
            # So: a uniformly random price INSIDE this bar's range. Same bar,
            # same volatility, same trend, genuinely touched. The only thing
            # that differs is whether the price is a real level.
            fpx = rng.uniform(l[i], h[i])
            cres = first_passage(h, l, i, fpx, c[i - 1] < fpx, r, horizon)
            if np.isfinite(cres):
                ctrl.append(cres)
    return np.array(real), np.array(ctrl)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rule", default="30min")
    ap.add_argument("--r-atr", type=float, default=1.0)
    ap.add_argument("--horizon", type=int, default=48)
    a = ap.parse_args()

    df = load_csv("data/xauusd_15m.csv.gz", rule=a.rule)
    lv = build(df, dense=True)
    print(f"{len(df):,} bars on {a.rule}, {lv.shape[1]} level types\n")

    real, ctrl = run(df, lv, r_atr=a.r_atr, horizon=a.horizon)
    from math import sqrt
    pr, pc_ = real.mean(), ctrl.mean()
    se = sqrt(pr * (1 - pr) / len(real) + pc_ * (1 - pc_) / len(ctrl))
    z = (pr - pc_) / se

    print(f"first passage: bounce {a.r_atr} ATR away vs break {a.r_atr} ATR through,"
          f" horizon {a.horizon} bars")
    print(f"  REAL levels      n={len(real):>7,}   bounce rate {pr * 100:6.2f}%")
    print(f"  RANDOM control   n={len(ctrl):>7,}   bounce rate {pc_ * 100:6.2f}%")
    print(f"  difference       {(pr - pc_) * 100:+6.2f} pp   z = {z:+.2f}")
    print(f"\n  VERDICT: {'levels carry information' if z > 3 else 'indistinguishable from an arbitrary price'}")


if __name__ == "__main__":
    main()
