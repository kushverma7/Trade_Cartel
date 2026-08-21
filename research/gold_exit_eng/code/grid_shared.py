"""Shared SL/TP grid, ranked by the MINIMUM profit factor across DEV/VAL/HOLD.

That ranking is the brief's, and it targets the right thing -- a system that
holds together across time rather than one that made all its money in one
stretch. At this sample size it also has a hazard worth stating: VAL and HOLD
hold 26 trades each, where the bootstrap 95% interval on PF spans roughly 0.7 to
4.5. Taking the MINIMUM of three such numbers over hundreds of candidates is a
minimum-of-noisy-draws, and it will preferentially surface whichever cell got
lucky in the smallest window. The plateau requirement, the tail-removal test and
the walk-forward are what actually discipline that, so they are not optional
extras here; they are the real filter.
"""
import sys, itertools, numpy as np, pandas as pd
sys.path.insert(0, "code")
from entry_universe import build, splits, label
from exits import run, by_split

SLS = [3,4,5,6,7,8,9,10,11,12,13,14,15,16,18,20,22,25,30,35,40]
TPS = [3,4,5,6,7,8,10,12,15,18,20,22,25,27,30,32,35,40,45,50,60,75,100]


def sweep(trades, tag, **fixed):
    rows = []
    for sl, tp in itertools.product(SLS, TPS):
        df = run(trades, sl=sl, tp=tp, **fixed)
        S = by_split(df)
        A = S["ALL"]
        rows.append(dict(tag=tag, sl=sl, tp=tp, n=A["n"], pf=A["pf"], exp=A["exp"],
                         net=A["net"], mdd=A["mdd"], wr=A["wr"],
                         pf_dev=S["DEV"]["pf"], pf_val=S["VAL"]["pf"], pf_hold=S["HOLD"]["pf"],
                         exp_dev=S["DEV"]["exp"], exp_val=S["VAL"]["exp"], exp_hold=S["HOLD"]["exp"],
                         n_dev=S["DEV"]["n"], n_val=S["VAL"]["n"], n_hold=S["HOLD"]["n"],
                         minPF=S["minPF"], minEXP=S["minEXP"]))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = []
    for tag, w, s in [("LOCKED", 1100, 2.0), ("NOFILT", 2400, None),
                      ("W1030", 1030, 2.0), ("W1200", 1200, 2.0), ("W1400", 1400, 2.0)]:
        tr = build(w, s); d1, d2 = splits(tr); label(tr, d1, d2)
        g = sweep(tr, tag)
        out.append(g)
        print(f"  swept {tag}: {len(tr)} trades, {len(g)} cells", flush=True)
    G = pd.concat(out, ignore_index=True)
    G.to_csv("results/grid_shared.csv", index=False)
    print(f"\ntotal cells: {len(G)} -> results/grid_shared.csv")
