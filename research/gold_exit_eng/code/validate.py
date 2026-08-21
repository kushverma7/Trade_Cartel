"""Is the winner real, or the best of 1,456 coin flips?

Three tests, in increasing order of how much they hurt.

1. ROBUST SELECTION. Pick the configuration that maximises the WORST train MAR
   among itself and its eight grid neighbours, not the one with the highest peak.
   A cell that is only good because its neighbours are bad is a fitting artefact.
2. DIRECTION-FLIP CONTROL. Invert every signal. If the rules carry directional
   information the inverse must be clearly worse; if the two are mirror images of
   each other the rules are just harvesting drift or volatility.
3. SELECTION-AWARE SIGNIFICANCE. A t of 2.2 is unremarkable when it is the best
   of 1,456 tries. The null here resamples the SAME trade dates with randomised
   directions and re-runs the whole selection, so the comparison is like for
   like: best-of-grid against best-of-grid.
"""
import sys, pickle, itertools, numpy as np, pandas as pd
sys.path.insert(0, "code")
from fastsim import simulate
from engine import stats

SPLIT = "2026-04-30"
R = pd.read_csv("results/sweep.csv")
prep = pickle.load(open("data/prep10.pkl", "rb"))
class TK:
    t = np.load("data/tk_t.npy"); bid = np.load("data/tk_bid.npy"); ask = np.load("data/tk_ask.npy")

# ---------- 1. robust selection, TRAIN ONLY ----------
print("=== 1. ROBUST SELECTION (max of the worst neighbour), train only ===")
best = None
for st in R.set.unique():
    piv = R[R.set == st].pivot(index="sl", columns="tp", values="mar_tr")
    sls, tps = list(piv.index), list(piv.columns)
    for i, sl in enumerate(sls):
        for j, tp in enumerate(tps):
            if tp < 3:
                continue
            nb = piv.iloc[max(0,i-1):i+2, max(0,j-1):j+2].to_numpy()
            nb = nb[~np.isnan(nb)]
            if len(nb) < 6:
                continue
            score = float(nb.min())
            if best is None or score > best[0]:
                best = (score, st, sl, tp, float(piv.iloc[i, j]))
score, SET, SL, TP, peak = best
print(f"  winner: {SET}  SL={SL}  TP={TP}")
print(f"  worst neighbour train MAR = {score:.2f}   (its own = {peak:.2f})")
row = R[(R.set==SET)&(R.sl==SL)&(R.tp==TP)].iloc[0]
print(f"  TRAIN n={row.n_tr:.0f} exp={row.exp_tr:+.2f} pf={row.pf_tr:.2f} dd={row.dd_tr:.0f} r2={row.r2_tr:.2f} t={row.t_tr:.2f}")
print(f"  TEST  n={row.n_te:.0f} exp={row.exp_te:+.2f} pf={row.pf_te:.2f} dd={row.dd_te:.0f} r2={row.r2_te:.2f}")

ALLOW = {"A_both":{"A_L","A_S"}, "All_four":{"A_L","A_S","F_L","F_S"},
         "A_short_only":{"A_S"}, "Flip_both":{"F_L","F_S"}, "Flip_short_only":{"F_S"},
         "Flip_long_only":{"F_L"}, "A_short_plus_Flip":{"A_S","F_L","F_S"},
         "Shorts_only":{"A_S","F_S"}}
# NOTE: the boolean flags apply ON TOP of `allow`. Omitting a_short_only=False
# here silently dropped the A_L leg and produced 101 trades where the sweep had
# 235 -- the train/test counts not summing to the full count is what caught it.
tr = simulate(prep, TK, SL, TP, use_A=True, a_short_only=False, use_flip=True,
              allow=ALLOW[SET])
tr["date"] = pd.to_datetime(tr["date"])
tr.to_csv("results/trades_selected.csv", index=False)
f = stats(tr, "full")
assert f["n"] == int(row.n_tr) + int(row.n_te), (
    f"re-run produced {f['n']} trades but the sweep recorded "
    f"{int(row.n_tr)}+{int(row.n_te)}={int(row.n_tr)+int(row.n_te)} -- flags disagree")
print(f"  FULL  n={f['n']} exp={f['exp']:+.2f} pf={f['pf']:.2f} net={f['net']:+.0f} dd={f['max_dd']:.0f} mar={f['mar']:.2f} t={f['tstat']:.2f}")

# ---------- 2. direction flip ----------
print("\n=== 2. DIRECTION-FLIP CONTROL ===")
p = tr["pnl"].to_numpy(float)
print(f"  as traded : exp {p.mean():+.3f}  pf {p[p>0].sum()/max(-p[p<0].sum(),1e-9):.3f}")
print("  inverted  : not a clean mirror (stop and target swap roles), so this is")
print("              reported as the sign test on per-trade P&L instead:")
print(f"              share of winners {100*(p>0).mean():.1f}%  vs  {100*(p<0).mean():.1f}% losers")

# ---------- 3. selection-aware null ----------
print("\n=== 3. SELECTION-AWARE NULL (best-of-grid vs best-of-grid) ===")
sub = tr[["date","kind","pnl"]].copy()
train_mask = (sub.date <= SPLIT).to_numpy()
rng = np.random.default_rng(20260821)
obs_mar_tr = float(row.mar_tr)
obs_exp_full = float(f["exp"])

# Null A: randomise the SIGN of each trade's outcome, preserving magnitudes and dates.
nulls_exp, nulls_mar = [], []
for _ in range(20000):
    s = rng.choice([-1.0, 1.0], size=len(p))
    q = p * s
    nulls_exp.append(q.mean())
    eq = np.cumsum(q[train_mask])
    if len(eq) == 0: continue
    peak_ = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    mdd = float((peak_-eq).max())
    nulls_mar.append(eq[-1]/mdd if mdd > 0 else np.nan)
nulls_exp = np.array(nulls_exp); nulls_mar = np.array(nulls_mar, dtype=float)
nulls_mar = nulls_mar[~np.isnan(nulls_mar)]
print(f"  observed full expectancy {obs_exp_full:+.3f} pts")
print(f"  null expectancy          mean {nulls_exp.mean():+.3f}  sd {nulls_exp.std():.3f}")
print(f"  one-sided p (sign null)  {(nulls_exp >= obs_exp_full).mean():.4f}")
print(f"  observed TRAIN MAR {obs_mar_tr:.2f}")
print(f"  null TRAIN MAR      p95 {np.percentile(nulls_mar,95):.2f}   p99 {np.percentile(nulls_mar,99):.2f}   max {nulls_mar.max():.2f}")
print(f"  one-sided p (MAR)   {(nulls_mar >= obs_mar_tr).mean():.4f}   <-- SINGLE config, no selection penalty yet")

n_cfg = len(R)
p_single = float((nulls_exp >= obs_exp_full).mean())
print(f"\n  configurations searched : {n_cfg}")
print(f"  Sidak-adjusted p        : {1-(1-p_single)**n_cfg:.4f}")
print(f"  expected best-of-{n_cfg} t under pure noise ~ {np.sqrt(2*np.log(n_cfg)):.2f}; observed full t = {f['tstat']:.2f}")
