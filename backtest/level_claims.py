"""
Test the four specific, falsifiable claims that key-level methodology makes.

The methodology write-up (pivots + price action + level-to-level + ICT/SMC) is
accurate as history and taxonomy. It is also full of claims stated as settled
fact that have never been measured on this desk's own instrument. Four of them
are precise enough to test:

  C1  "High-probability when the level is UNTESTED."
      -> first touch should beat later touches.

  C2  "Liquidity sweep beyond PDH/PDL, then close back inside -> reversal."
      -> the ICT core. A sweep-and-reclaim should beat a plain touch.

  C3  "Session + key level CONFLUENCE ... strong resistance."
      -> touches where several levels stack should beat isolated ones.

  C4  "Target at least 1:2 or the next clear level."
      -> an asymmetric payoff should fix what a symmetric one could not.
      backtest/level_reaction.py only tested R-for-R, so this claim was NOT
      addressed there. It is addressed here.

Everything is measured against the same cost the rest of this repo uses
($0.54 round turn) and reported as clears / does not clear, because a
statistically real effect that does not pay the spread is not a strategy.
"""
import argparse
from math import sqrt

import numpy as np
import pandas as pd

from backtest.io import load_csv
from backtest.levels import build
from backtest.level_reaction import _atr

COST_USD = 0.54


def touches(df, lv, horizon=48):
    """Every level touch, tagged with the facts the claims turn on."""
    A = _atr(df)
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    o = df["open"].values
    n = len(c)
    allv = {k: lv[k].values for k in lv.columns}
    rows = []
    seen = {k: {} for k in lv.columns}     # level value -> times touched

    for name, v in allv.items():
        for i in range(50, n - horizon):
            a, px = A[i], v[i]
            if not np.isfinite(px) or not np.isfinite(a) or a <= 0:
                continue
            if not (l[i] <= px <= h[i]) or (l[i - 1] <= v[i - 1] <= h[i - 1]):
                continue
            key = round(px, 3)
            cnt = seen[name].get(key, 0)
            seen[name][key] = cnt + 1

            up = c[i - 1] < px                      # approached from below
            # C2: did this bar SWEEP the level and close back on the origin side?
            swept = (h[i] > px and c[i] < px) if up else (l[i] < px and c[i] > px)
            # C3: how many OTHER level types sit within 0.25 ATR of this one?
            conf = sum(1 for k2, v2 in allv.items()
                       if k2 != name and np.isfinite(v2[i])
                       and abs(v2[i] - px) <= 0.25 * a)
            rows.append({"i": i, "px": px, "atr": a, "up": up,
                         "first": cnt == 0, "swept": swept, "conf": conf})
    return pd.DataFrame(rows)


def outcome(df, t, stop_atr, rr, horizon=48):
    """Fade the level, priced from the ACTUAL ENTRY.

    CORRECTION 2026-08-02. The first version measured target and stop as
    distances from the LEVEL. That is not the trade. You enter at the close of
    the touch bar, which on a sweep-and-reclaim sits well away from the level
    -- so measuring from the level understated the risk and overstated the
    reward, and it inflated the sweep result specifically, because sweep bars
    close furthest from the level.

    The real trade, and the one the methodology actually describes:
        entry  = close of the touch bar
        stop   = stop_atr ATR BEYOND the level  ("stops beyond the key level")
        risk   = |entry - stop|                  (measured from the entry)
        target = rr x risk from the entry
    """
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    out = np.full(len(t), np.nan)
    rrisk = np.full(len(t), np.nan)
    for k, r in enumerate(t.itertuples()):
        i, px, a, up = r.i, r.px, r.atr, r.up
        entry = c[i]
        # approached from below -> fade SHORT: stop above the level
        stp = px + a * stop_atr if up else px - a * stop_atr
        risk = abs(entry - stp)
        if risk <= 0:
            continue
        rrisk[k] = risk / a
        tgt = entry - risk * rr if up else entry + risk * rr
        for j in range(i + 1, min(i + horizon + 1, len(h))):
            hit_t = (l[j] <= tgt) if up else (h[j] >= tgt)
            hit_s = (h[j] >= stp) if up else (l[j] <= stp)
            if hit_t and hit_s:
                break                                # ambiguous bar
            if hit_t:
                out[k] = 1.0; break
            if hit_s:
                out[k] = 0.0; break
    return out, rrisk


def verdict(name, res, risk, rr, c_atr):
    m = np.isfinite(res) & np.isfinite(risk)
    r, rk = res[m], risk[m]
    if len(r) < 200:
        print(f"  {name:<34} n={len(r):>6}  (too few)"); return
    p = r.mean(); mr = rk.mean()          # mean risk in ATR, from the entry
    be = (mr + c_atr) / (mr * (1 + rr))
    edge = p * (mr * rr - c_atr) - (1 - p) * (mr + c_atr)
    print(f"  {name:<34} n={len(r):>6}  hit={p * 100:6.2f}%  "
          f"risk={mr:4.2f}ATR  breakeven={be * 100:6.2f}%  "
          f"edge={edge:+6.3f} ATR  {'CLEARS' if edge > 0 else 'no'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rule", default="30min")
    ap.add_argument("--horizon", type=int, default=48)
    a = ap.parse_args()

    df = load_csv("data/xauusd_15m.csv.gz", rule=a.rule)
    lv = build(df, dense=True)
    A = _atr(df)
    c_atr = COST_USD / float(np.nanmedian(A))
    print(f"{len(df):,} bars, {lv.shape[1]} level types, "
          f"cost {c_atr:.3f} ATR\n")

    t = touches(df, lv, a.horizon)
    print(f"{len(t):,} level touches\n")

    for stop_atr, rr in ((0.5, 2.0), (1.0, 2.0), (1.0, 3.0)):
        print(f"--- fade: stop {stop_atr} ATR beyond the level, target {rr:.0f}R "
              f"from ENTRY (claim C4) ---")
        res, risk = outcome(df, t, stop_atr, rr, a.horizon)
        for nm, mask in (("ALL touches", np.ones(len(t), bool)),
                         ("C1 first touch (untested)", t["first"].values),
                         ("C1 retest (2nd+)", ~t["first"].values),
                         ("C2 swept + reclaimed", t["swept"].values),
                         ("C2 plain touch", ~t["swept"].values),
                         ("C3 confluence >=2 others", (t["conf"] >= 2).values),
                         ("C3 isolated (0 others)", (t["conf"] == 0).values)):
            verdict(nm, res[mask], risk[mask], rr, c_atr)
        print()


if __name__ == "__main__":
    main()
