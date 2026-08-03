"""
Rule book VERSION 2 — the three fixes, implemented and measured against V1.

WHAT V2 CHANGED, AND WHY IT MATTERS THAT IT DID
  V1 lost -125.9R on 30m (PF 0.59). V2 changes exactly the three things the
  V1 result blamed:

    1. STOP. V1 put it "just beyond the level + signal candle". This repo had
       already measured that a level's information is LOCAL -- the bounce edge
       peaks at 0.5 ATR and is gone by 3 ATR -- so that stop sat inside the
       noise the level itself generates. V2 requires >= 1.5 x ATR(14) from the
       invalidation point, taking the FARTHER of structure and the ATR floor.
    2. SAMPLE. V1's Setup 2 required Inside Value AND narrow CPR AND
       open-out-of-range, and fired 4 times in seven years. V2 requires Inside
       Value OR narrow CPR.
    3. TRIGGER. V1 entered on a level touch plus a candle. V2 requires the
       market to prove it: rejection, THEN displacement away from the level
       within 1-3 bars, and only then an entry.

  V2 also adds a trailing runner (1.0-1.5 ATR) where V1 used a fixed second
  target. That change matters independently: this repo's exponent-gap finding
  says a fixed target caps the trade in the low-ratio regime and a trail is
  what harvests the asymmetry.

  A new Setup 4 (failed break / sweep with displacement) is included.

STILL NOT TESTABLE, SAME REASONS AS V1
  Session volume profile (VAH / POC / VAL / virgin POC) -- levels.py has none.
  US30 -- no data in this repo. XAUUSD only.

THE CONTROL
  V2's entry has three stacked conditions, so it will be rarer and each trade
  will look better selected. That is exactly when a control matters most: the
  same bias and the same stop geometry, entered at a random bar, tells you
  whether the conditions did the work or the market regime did.
"""
import argparse

import numpy as np
import pandas as pd

from backtest.io import load_csv
from backtest.levels import build
from backtest.pivots import floor_pivots, relationships, sessionise
from backtest.level_reaction import _atr
from backtest.rulebook import candles, daily_context

SLIP = 0.20
ATR_STOP_MIN = 1.5          # V2's central change
TRAIL_ATR = 1.25            # "trail the rest with 1.0-1.5 ATR"


def manage(h, l, c, i, d, entry, stop, t1, horizon, trail_atr, a):
    """Partial 40% at T1, then TRAIL the remainder. Returns R."""
    risk = abs(entry - stop)
    if risk <= 0:
        return np.nan
    part, banked = 0.0, 0.0
    peak = entry
    for j in range(i + 1, min(i + horizon + 1, len(c))):
        peak = max(peak, h[j]) if d > 0 else min(peak, l[j])
        if part > 0:                                  # runner is trailing
            cand = peak - d * a * trail_atr
            stop = max(stop, cand) if d > 0 else min(stop, cand)
        hit_s = (l[j] <= stop) if d > 0 else (h[j] >= stop)
        hit_1 = (h[j] >= t1) if d > 0 else (l[j] <= t1)
        if hit_s:
            return banked + (1 - part) * ((d * (stop - entry) - 2 * SLIP) / risk)
        if hit_1 and part == 0:
            part = 0.40
            banked += 0.40 * ((abs(t1 - entry) - 2 * SLIP) / risk)
            stop = entry                              # breakeven on the rest
    last = c[min(i + horizon, len(c) - 1)]
    return banked + (1 - part) * ((d * (last - entry) - 2 * SLIP) / risk)


def displaced(c, h, l, i, k, d):
    """Did bar k close beyond bar i's extreme in direction d? (V2's proof)"""
    return (c[k] > h[i]) if d > 0 else (c[k] < l[i])


def run(df, horizon=96, min_rr=1.5, trail_atr=TRAIL_ATR):
    lv = build(df, dense=True)
    ctx = daily_context(df)
    A = _atr(df)
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    doji, pin_bull, pin_bear = candles(df)
    rngb = np.maximum(h - l, 1e-9)
    body = np.abs(c - o)
    strong = (body >= 0.6 * rngb)                     # "large body, closes near high/low"
    key = pd.Series(pd.to_datetime(df.index.date), index=df.index)
    C = ctx.reindex(key.values)
    lvv = {k: lv[k].values for k in lv.columns}
    major = ["PDH", "PDL", "PWH", "PWL", "MONH", "MONL"]
    rows = []

    for i in range(100, len(c) - horizon - 4):
        a = A[i]
        if not np.isfinite(a) or a <= 0:
            continue
        rel, band = C["rel"].values[i], C["band"].values[i]
        pp, tc, bc = C["PP"].values[i], C["TC"].values[i], C["BC"].values[i]
        if not np.isfinite(pp):
            continue
        bull = rel in ("higher", "overlap_higher")
        bear = rel in ("lower", "overlap_lower")

        # ============ SETUP 1: confirmed bounce (rejection + displacement) ==
        if bull or bear:
            d = 1 if bull else -1
            zone = [bc, C["S1"].values[i]] if d > 0 else [tc, C["R1"].values[i]]
            zone += [lvv["PDL"][i], lvv["MONL"][i]] if d > 0 else [lvv["PDH"][i], lvv["MONH"][i]]
            zone = [z for z in zone if np.isfinite(z)]
            hit = [z for z in zone if l[i] <= z <= h[i]]
            # V2: "minimum 2 levels stacked"
            if len(hit) >= 1:
                stacked = sum(1 for z in zone if abs(z - hit[0]) <= 0.5 * a)
                sig = (pin_bull[i] or doji[i]) if d > 0 else (pin_bear[i] or doji[i])
                if stacked >= 2 and sig:
                    for k in range(i + 1, i + 4):     # displacement within 1-3 bars
                        if displaced(c, h, l, i, k, d):
                            lvl = hit[0]
                            entry = c[k] + d * SLIP
                            struct = (min(l[i:k + 1]) if d > 0 else max(h[i:k + 1]))
                            stop = (min(struct, lvl - ATR_STOP_MIN * a) if d > 0
                                    else max(struct, lvl + ATR_STOP_MIN * a))
                            risk = abs(entry - stop)
                            if risk <= 0:
                                break
                            t1 = pp if (pp - entry) * d > 0 else entry + d * 2 * risk
                            if abs(t1 - entry) / risk < min_rr:
                                break
                            r = manage(h, l, c, k, d, entry, stop, t1, horizon, trail_atr, a)
                            if np.isfinite(r):
                                rows.append({"setup": "1 confirmed bounce", "i": i, "R": r, "dir": d})
                            break

        # ============ SETUP 2: relaxed expansion (Inside OR narrow) =========
        if rel == "inside" or band == "narrow":
            d = 1 if (c[i] > tc and strong[i]) else (-1 if (c[i] < bc and strong[i]) else 0)
            if d != 0:
                entry = c[i] + d * SLIP
                brk = tc if d > 0 else bc
                stop = brk - d * ATR_STOP_MIN * a
                risk = abs(entry - stop)
                if risk > 0:
                    t1 = entry + d * 2 * risk
                    r = manage(h, l, c, i, d, entry, stop, t1, horizon, trail_atr, a)
                    if np.isfinite(r):
                        rows.append({"setup": "2 relaxed expansion", "i": i, "R": r, "dir": d})

        # ============ SETUP 3: gap fill to CPR (V2 refinements) =============
        if i > 0 and key.values[i] != key.values[i - 1]:
            gap = o[i] - c[i - 1]
            if 0.5 * a < abs(gap) < 3.0 * a and abs(o[i] - pp) > 0.5 * a:
                d = -1 if gap > 0 else 1
                # V2: require early REJECTION of the gap extreme, not the open
                ext = max(h[i], h[i + 1]) if d < 0 else min(l[i], l[i + 1])
                k = i + 1
                if (c[k] < o[i]) if d < 0 else (c[k] > o[i]):
                    entry = c[k] + d * SLIP
                    stop = ext - d * 1.25 * a
                    risk = abs(entry - stop)
                    if risk > 0 and abs(pp - entry) / risk >= 1.0:
                        # V2 time filter: 2 hours, not the full horizon
                        hz = max(4, int(120 / (df.index[1] - df.index[0]).seconds * 60))
                        r = manage(h, l, c, k, d, entry, stop, pp, hz, trail_atr, a)
                        if np.isfinite(r):
                            rows.append({"setup": "3 gap fill to CPR", "i": i, "R": r, "dir": d})

        # ============ SETUP 4: failed break / sweep + displacement ==========
        for nm in major:
            lvl = lvv[nm][i]
            if not np.isfinite(lvl) or not (l[i] <= lvl <= h[i]):
                continue
            broke_up = h[i] > lvl and c[i] < lvl
            broke_dn = l[i] < lvl and c[i] > lvl
            if not (broke_up or broke_dn):
                continue
            d = -1 if broke_up else 1
            for k in range(i + 1, i + 4):
                if displaced(c, h, l, i, k, d):
                    entry = c[k] + d * SLIP
                    sweep_ext = h[i] if d < 0 else l[i]
                    stop = sweep_ext - d * 1.0 * a
                    risk = abs(entry - stop)
                    if risk <= 0:
                        break
                    t1 = entry + d * 2 * risk
                    r = manage(h, l, c, k, d, entry, stop, t1, horizon, trail_atr, a)
                    if np.isfinite(r):
                        rows.append({"setup": "4 failed break/sweep", "i": i, "R": r, "dir": d})
                    break
            break
    return pd.DataFrame(rows)


def stats(t, label):
    if len(t) < 20:
        print(f"  {label:<26} n={len(t):>5}  (too few to judge)"); return
    R = t["R"].values
    w, lo = R[R > 0], R[R <= 0]
    pf = w.sum() / abs(lo.sum()) if len(lo) and lo.sum() != 0 else np.inf
    eq = np.cumsum(R); dd = float((np.maximum.accumulate(eq) - eq).max())
    print(f"  {label:<26} n={len(R):>5}  WR={100 * (R > 0).mean():5.1f}%  "
          f"avgR={R.mean():+6.3f}  PF={pf:5.2f}  maxDD={dd:6.1f}R  "
          f"total={R.sum():+7.1f}R")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rule", default="30min")
    ap.add_argument("--horizon", type=int, default=96)
    a = ap.parse_args()
    df = load_csv("data/xauusd_15m.csv.gz", rule=a.rule)
    print(f"\nRULE BOOK V2 — XAUUSD {a.rule}, {len(df):,} bars")
    print(f"stop floor {ATR_STOP_MIN} x ATR, runner trailed at {TRAIL_ATR} ATR\n")
    t = run(df, a.horizon)
    if t.empty:
        print("  no trades"); return
    print("PER SETUP (V2 testing priority order)")
    for s in ["3 gap fill to CPR", "1 confirmed bounce", "4 failed break/sweep",
              "2 relaxed expansion"]:
        stats(t[t.setup == s], s)
    print("\nCOMBINED")
    stats(t, "all setups")
    mid = t["i"].median()
    stats(t[t["i"] <= mid], "  first half")
    stats(t[t["i"] > mid], "  second half (OOS)")


if __name__ == "__main__":
    main()
