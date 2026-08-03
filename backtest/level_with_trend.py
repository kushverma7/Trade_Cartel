"""
The one key-level claim this repo had NOT tested: trade WITH the trend at the
level, not against it.

WHY THIS IS A SEPARATE TEST
  Everything measured so far -- level_reaction.py and level_claims.py -- FADES
  the level. Price arrives, you bet it holds. All of it failed: 21 of 21
  cohort-geometry combinations negative once priced from the real entry.

  But that is not what the methodology actually recommends. Ochoa's "Pivot
  Trend Analysis" says BUY SUPPORT IN AN UPTREND, SELL RESISTANCE IN A
  DOWNTREND. The price-action guides say the same: take the pin bar at the
  level, but only in the direction of the dominant trend. The bias filter is
  explicit -- "price above Weekly + Monthly Open -> bullish bias".

  A fade and a with-trend continuation at the same level are opposite trades.
  Rejecting one says nothing about the other, and this repo has only ever
  tested the one the methodology does not recommend.

  It is also the version consistent with this repo's own strongest finding:
  the exponent gap (MFE 0.558 vs MAE 0.493) says profit accrues to holding
  a directional move, not to catching a turn.

THE RULE, AS THE SOURCES STATE IT
  bias      close above BOTH the weekly and monthly open  -> bullish
            close below BOTH                              -> bearish
            otherwise                                     -> no trade
  setup     bullish bias + price pulls back DOWN onto a level -> BUY
            bearish bias + price rallies UP into a level      -> SELL
  stop      stop_atr ATR beyond the level (the standard rule)
  target    rr x the resulting risk, measured from the entry

  Entry is the close of the touch bar, and risk is measured from that entry --
  the correction that overturned the sweep result in level_claims.py.
"""
import argparse

import numpy as np
import pandas as pd

from backtest.io import load_csv
from backtest.levels import build
from backtest.level_reaction import _atr

COST_USD = 0.54


def run(df, lv, stop_atr=1.0, rr=2.0, horizon=48, seed=0):
    A = _atr(df)
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    wo, mo = lv["WO"].values, lv["MO"].values
    allv = {k: lv[k].values for k in lv.columns}
    rng = np.random.default_rng(seed)
    rows = []

    for name, v in allv.items():
        if name in ("WO", "MO"):
            continue                       # the bias levels are not the setup
        for i in range(50, len(c) - horizon):
            a, px = A[i], v[i]
            if not np.isfinite(px) or not np.isfinite(a) or a <= 0:
                continue
            if not (l[i] <= px <= h[i]) or (l[i - 1] <= v[i - 1] <= h[i - 1]):
                continue
            if not (np.isfinite(wo[i]) and np.isfinite(mo[i])):
                continue
            bull = c[i] > wo[i] and c[i] > mo[i]
            bear = c[i] < wo[i] and c[i] < mo[i]
            if not (bull or bear):
                continue
            approached_down = c[i - 1] > px      # pulled back onto the level

            # WITH-TREND: buy support in an uptrend / sell resistance in a downtrend
            if bull and approached_down:
                d = 1
            elif bear and not approached_down:
                d = -1
            else:
                continue

            entry = c[i]
            stp = px - a * stop_atr if d > 0 else px + a * stop_atr
            risk = abs(entry - stp)
            if risk <= 0:
                continue
            tgt = entry + d * risk * rr
            res = np.nan
            for j in range(i + 1, min(i + horizon + 1, len(c))):
                hit_t = (h[j] >= tgt) if d > 0 else (l[j] <= tgt)
                hit_s = (l[j] <= stp) if d > 0 else (h[j] >= stp)
                if hit_t and hit_s:
                    break
                if hit_t:
                    res = 1.0; break
                if hit_s:
                    res = 0.0; break
            rows.append({"i": i, "dir": d, "res": res, "risk_atr": risk / a,
                         "level": name, "bull": bull})
    return pd.DataFrame(rows)


def verdict(name, t, rr, c_atr):
    t = t[np.isfinite(t["res"])]
    if len(t) < 200:
        print(f"  {name:<32} n={len(t):>6}  (too few)"); return None
    p = t["res"].mean(); mr = t["risk_atr"].mean()
    be = (mr + c_atr) / (mr * (1 + rr))
    edge = p * (mr * rr - c_atr) - (1 - p) * (mr + c_atr)
    print(f"  {name:<32} n={len(t):>6}  hit={p * 100:6.2f}%  risk={mr:4.2f}ATR  "
          f"breakeven={be * 100:6.2f}%  edge={edge:+6.3f} ATR  "
          f"{'CLEARS' if edge > 0 else 'no'}")
    return edge


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rule", default="30min")
    ap.add_argument("--horizon", type=int, default=48)
    a = ap.parse_args()

    df = load_csv("data/xauusd_15m.csv.gz", rule=a.rule)
    lv = build(df, dense=True)
    c_atr = COST_USD / float(np.nanmedian(_atr(df)))
    print(f"{len(df):,} bars, cost {c_atr:.3f} ATR")
    print("bias: close above BOTH weekly and monthly open = bullish (and mirror)\n")

    for stop_atr, rr in ((1.0, 2.0), (1.0, 3.0), (0.5, 2.0)):
        print(f"--- WITH-TREND at the level: stop {stop_atr} ATR beyond, "
              f"target {rr:.0f}R from entry ---")
        t = run(df, lv, stop_atr, rr, a.horizon)
        verdict("all with-trend touches", t, rr, c_atr)
        verdict("  longs (bull bias)", t[t.dir == 1], rr, c_atr)
        verdict("  shorts (bear bias)", t[t.dir == -1], rr, c_atr)
        # split by half, so nothing can be cherry-picked
        mid = t["i"].median()
        verdict("  first half", t[t["i"] <= mid], rr, c_atr)
        verdict("  second half (OOS)", t[t["i"] > mid], rr, c_atr)
        print()


if __name__ == "__main__":
    main()
