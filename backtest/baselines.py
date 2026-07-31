#!/usr/bin/env python3
"""
Reference points every strategy must beat before it means anything.

No engine in this repo's history was ever compared against either of these,
which is how PF 1.093 came to be called a breakthrough.

1. BUY AND HOLD -- gold rose a long way over this period. A strategy that
   makes money while being flat most of the time has to be judged against
   simply owning the thing.

2. RANDOM ENTRY -- coin-flip direction fired at the same rate as the real
   strategy, run through the IDENTICAL filters, stops, targets, sizing and
   costs. This is the honest null hypothesis. If random entries with our
   exit machinery already produce PF ~1.0, then the exit machinery is doing
   the work and the entry logic is decoration.

  python3 -m backtest.baselines --csv data/xauusd_15m.csv.gz --trials 200
"""
import argparse
import numpy as np
from backtest import engine, levels as L, io as bio
from backtest.optimize import session_mask

LEVELS = ["DO", "PDH", "PDL", "WO", "PWH", "PWL", "MONH", "MONL"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--trials", type=int, default=200)
    ap.add_argument("--split", type=float, default=0.60)
    a = ap.parse_args()

    df = bio.load_csv(a.csv)
    lv = L.build(df)
    sess = session_mask(df.index)
    cut = int(len(df) * a.split)
    te, lvte, ste = df.iloc[cut:], lv.iloc[cut:], sess[cut:]
    print(f"TEST block: {len(te):,} bars  "
          f"{te.index[0]:%Y-%m-%d} -> {te.index[-1]:%Y-%m-%d}\n")

    # ---- 1. buy and hold, on the test block ----
    bh = (te["close"].iloc[-1] / te["close"].iloc[0] - 1) * 100
    yrs = (te.index[-1] - te.index[0]).days / 365.25
    peak = te["close"].cummax()
    bh_dd = ((peak - te["close"]) / peak).max() * 100
    print("BUY AND HOLD")
    print(f"  net {bh:+.2f}% over {yrs:.2f} years  "
          f"({(1 + bh / 100) ** (1 / yrs) * 100 - 100:+.2f}%/yr)   maxDD {bh_dd:.2f}%")

    # ---- 2. random entry through the identical machinery ----
    ref = engine.Config(levels=LEVELS)
    real, _ = engine.run(te, lvte, ref, ste)
    rate = len(real) / max(len(te), 1)
    print(f"\nreal signal rate on TEST: {len(real)} trades "
          f"({rate * 100:.4f}% of bars) — random entries matched to it")

    pfs, nets, ns = [], [], []
    for s in range(a.trials):
        cfg = engine.Config(levels=LEVELS, random_p=rate * 3, random_seed=s)
        tr, st = engine.run(te, lvte, cfg, ste)
        if st["n"] >= 30 and np.isfinite(st["pf"]):
            pfs.append(st["pf"]); nets.append(st["net_pct"]); ns.append(st["n"])
    pfs, nets = np.array(pfs), np.array(nets)
    if len(pfs) == 0:
        print("\nno random trial reached a readable sample"); return

    print(f"\nRANDOM ENTRY  ({len(pfs)} trials, median {int(np.median(ns))} trades each)")
    for q in (5, 25, 50, 75, 95):
        print(f"  {q:>2}th pct   PF {np.percentile(pfs, q):5.3f}   "
              f"net {np.percentile(nets, q):+7.2f}%")
    print(f"  mean       PF {pfs.mean():5.3f}   net {nets.mean():+7.2f}%")

    print("\n" + "=" * 62)
    print("THE BAR A REAL STRATEGY HAS TO CLEAR")
    print("=" * 62)
    p95 = np.percentile(pfs, 95)
    print(f"  Random entries reach PF {np.median(pfs):.3f} at the median and "
          f"{p95:.3f} at the 95th percentile.")
    print(f"  A strategy scoring below {p95:.3f} on a comparable sample has not")
    print("  demonstrated anything a coin flip could not have produced.")
    if np.median(pfs) > 0.95:
        print("\n  NOTE: random entry is already near break-even. That means the")
        print("  exit geometry -- not the entry logic -- is carrying the result.")


if __name__ == "__main__":
    main()
