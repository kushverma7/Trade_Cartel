"""The only null that answers the real question.

A t of 2.21 selected out of 1,456 configurations means nothing on its own, and
the Sidak correction that says p=1.00 is equally useless -- it assumes the 1,456
tests are independent when neighbouring SL/TP cells share most of their trades.

So instead of correcting analytically, the WHOLE PROCEDURE is re-run on data
that cannot contain the effect. For each permutation the 10:00 candle's body
delta (close - open) is transplanted from a randomly chosen OTHER day onto this
day's real 10:00 open. That keeps every nuisance feature intact -- the real price
path, the real open, the real spread, the real body-size distribution, gold's own
autocorrelation and volatility clustering -- and destroys exactly one thing: any
link between THIS day's candle and THIS day's subsequent path.

Then the identical sweep and the identical robust-selection rule are applied, and
the selected configuration's full-period expectancy is recorded. The resulting
distribution is what this search procedure produces from nothing. Correlation
between cells is handled automatically, because the null search faces the same
correlation the real one did.
"""
import sys, pickle, itertools, copy, numpy as np, pandas as pd
sys.path.insert(0, "code")
from fastsim import simulate
from engine import stats
from sweep import SLS, TPS, SETS, SPLIT

N_PERM = 20
prep0 = pickle.load(open("data/prep10.pkl", "rb"))
class TK:
    t = np.load("data/tk_t.npy"); bid = np.load("data/tk_bid.npy"); ask = np.load("data/tk_ask.npy")

# body delta of the 10:00 candle for each day: bullish -> bhi is the close.
deltas = []
for d in prep0:
    delta = (d["bhi"] - d["dopen"]) if d["side"] == 1 else (d["blo"] - d["dopen"])
    deltas.append(delta)
deltas = np.array(deltas, float)
print(f"days={len(prep0)}  body delta: mean {deltas.mean():+.3f}  sd {deltas.std():.3f}")


def permuted(rng):
    idx = rng.permutation(len(prep0))
    out = []
    for k, d in enumerate(prep0):
        e = dict(d)
        dl = deltas[idx[k]]
        O = d["dopen"]
        e["side"] = 1 if dl > 0 else -1
        e["bhi"] = O + max(dl, 0.0)
        e["blo"] = O + min(dl, 0.0)
        out.append(e)
    return out


def sweep_and_select(prep):
    rows = []
    for name, kw in SETS.items():
        for sl, tp in itertools.product(SLS, TPS):
            tr = simulate(prep, TK, sl, tp, use_A=True, a_short_only=False,
                          use_flip=True, allow=kw["allow"])
            if len(tr) == 0:
                continue
            tr["date"] = pd.to_datetime(tr["date"])
            a = stats(tr[tr.date <= SPLIT], "t"); f = stats(tr, "f")
            rows.append(dict(set=name, sl=sl, tp=tp, mar_tr=a["mar"],
                             n_tr=a["n"], n_te=f["n"] - a["n"],
                             exp_f=f["exp"], t_f=f["tstat"], mar_f=f["mar"]))
    R = pd.DataFrame(rows)
    R = R[(R.n_tr >= 25) & (R.n_te >= 10)]
    best = None
    for st in R.set.unique():
        piv = R[R.set == st].pivot(index="sl", columns="tp", values="mar_tr")
        for i in range(len(piv.index)):
            for j in range(len(piv.columns)):
                nb = piv.iloc[max(0,i-1):i+2, max(0,j-1):j+2].to_numpy()
                nb = nb[~np.isnan(nb)]
                if len(nb) < 6:
                    continue
                sc = float(nb.min())
                if best is None or sc > best[0]:
                    best = (sc, st, piv.index[i], piv.columns[j])
    if best is None:
        return None
    _, st, sl, tp = best
    r = R[(R.set==st)&(R.sl==sl)&(R.tp==tp)]
    return None if len(r)==0 else r.iloc[0]


rng = np.random.default_rng(20260821)
recs = []
for k in range(N_PERM):
    r = sweep_and_select(permuted(rng))
    if r is not None:
        recs.append(dict(perm=k, set=r["set"], sl=r.sl, tp=r.tp,
                         exp_f=r.exp_f, t_f=r.t_f, mar_f=r.mar_f))
        print(f"  perm {k+1:2d}/{N_PERM}: {r['set']:<18s} SL={r.sl:<3g} TP={r.tp:<3g} "
              f"exp={r.exp_f:+7.3f} t={r.t_f:+5.2f} mar={r.mar_f:6.2f}", flush=True)
N = pd.DataFrame(recs); N.to_csv("results/null_permutation.csv", index=False)

OBS_EXP, OBS_T = 2.806, 2.21
print(f"\n=== NULL DISTRIBUTION OF THE SELECTION PROCEDURE (n={len(N)}) ===")
print(f"  selected expectancy : mean {N.exp_f.mean():+.3f}  sd {N.exp_f.std():.3f}  max {N.exp_f.max():+.3f}")
print(f"  selected t-stat     : mean {N.t_f.mean():+.3f}  sd {N.t_f.std():.3f}  max {N.t_f.max():+.3f}")
print(f"\n  OBSERVED expectancy {OBS_EXP:+.3f}  ->  p = {(N.exp_f >= OBS_EXP).mean():.3f}")
print(f"  OBSERVED t-stat     {OBS_T:+.3f}  ->  p = {(N.t_f  >= OBS_T ).mean():.3f}")
