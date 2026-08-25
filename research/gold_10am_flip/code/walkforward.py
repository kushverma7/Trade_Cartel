"""Walk-forward: what the equity curve would ACTUALLY have looked like.

A single train/test split reports one draw and lets the chosen split flatter the
result. Walk-forward re-runs the whole selection inside each fold and trades only
the days that follow it, so every trade in the resulting curve was taken with
parameters chosen without seeing it. That curve -- not the in-sample one -- is
the honest answer to "is this dependable and smooth".
"""
import sys, pickle, itertools, numpy as np, pandas as pd
sys.path.insert(0, "code")
from fastsim import simulate
from engine import stats
from sweep import SLS, TPS, SETS

prep = pickle.load(open("data/prep10.pkl", "rb"))
class TK:
    t=np.load("data/tk_t.npy"); bid=np.load("data/tk_bid.npy"); ask=np.load("data/tk_ask.npy")
dates = sorted([d["date"] for d in prep])
TRAIN, TEST = 150, 30


def select(dmin, dmax):
    """Robust selection (max-of-worst-neighbour on MAR) inside a date window."""
    rows = []
    for name, kw in SETS.items():
        for sl, tp in itertools.product(SLS, TPS):
            tr = simulate(prep, TK, sl, tp, use_A=True, a_short_only=False,
                          use_flip=True, allow=kw["allow"])
            if len(tr) == 0: continue
            tr["date"] = pd.to_datetime(tr["date"])
            w = tr[(tr.date >= dmin) & (tr.date <= dmax)]
            if len(w) < 20: continue
            s = stats(w, "w")
            rows.append(dict(set=name, sl=sl, tp=tp, mar=s["mar"], n=s["n"]))
    R = pd.DataFrame(rows)
    if len(R) == 0: return None
    best = None
    for st in R.set.unique():
        piv = R[R.set == st].pivot(index="sl", columns="tp", values="mar")
        for i in range(len(piv.index)):
            for j in range(len(piv.columns)):
                nb = piv.iloc[max(0,i-1):i+2, max(0,j-1):j+2].to_numpy()
                nb = nb[~np.isnan(nb)]
                if len(nb) < 6: continue
                sc = float(nb.min())
                if best is None or sc > best[0]:
                    best = (sc, st, piv.index[i], piv.columns[j])
    return best


ALLOW = {k: v["allow"] for k, v in SETS.items()}
oos = []
folds = []
start = 0
while start + TRAIN + 1 <= len(dates):
    tr0, tr1 = dates[start], dates[start + TRAIN - 1]
    te0 = dates[start + TRAIN]
    te1 = dates[min(start + TRAIN + TEST - 1, len(dates) - 1)]
    b = select(pd.Timestamp(tr0), pd.Timestamp(tr1))
    if b is None:
        start += TEST; continue
    _, st, sl, tp = b
    tr = simulate(prep, TK, sl, tp, use_A=True, a_short_only=False,
                  use_flip=True, allow=ALLOW[st])
    tr["date"] = pd.to_datetime(tr["date"])
    seg = tr[(tr.date >= pd.Timestamp(te0)) & (tr.date <= pd.Timestamp(te1))]
    s = stats(seg, "oos")
    folds.append(dict(train_start=tr0, train_end=tr1, test_start=te0, test_end=te1,
                      chosen=st, sl=sl, tp=tp, n=s["n"], exp=s["exp"], net=s["net"]))
    print(f"  fold {len(folds)}: train {tr0}..{tr1} -> chose {st} SL={sl} TP={tp} | "
          f"OOS n={s['n']} exp={s['exp']:+.2f} net={s['net']:+.1f}", flush=True)
    oos.append(seg)
    start += TEST

F = pd.DataFrame(folds); F.to_csv("results/walkforward_folds.csv", index=False)
if oos:
    O = pd.concat(oos).sort_values("date")
    O.to_csv("results/walkforward_trades.csv", index=False)
    s = stats(O, "WF")
    print(f"\n=== WALK-FORWARD (all out-of-sample) ===")
    print(f"  folds {len(F)}   trades {s['n']}   net {s['net']:+.1f} pts")
    print(f"  expectancy {s['exp']:+.3f}   PF {s['pf']:.3f}   win {s['win']:.1f}%")
    print(f"  maxDD {s['max_dd']:.1f}   MAR {s['mar']:.2f}   R2 {s['r2']:.2f}   t {s['tstat']:.2f}")
    print(f"  parameter choice was stable? {F.groupby(['chosen','sl','tp']).size().to_dict()}")
