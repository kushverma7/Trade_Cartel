"""Parts 22, 23, 25 — is there ANY conditioning variable with cross-year signal?

Univariate scan first: for every candidate feature, split at its median and at
its quartiles and measure the expectancy difference, SEPARATELY IN EACH YEAR. A
feature only counts if it points the same way in both. Then the honest model
test: train on 2024-25 only, apply once to 2025-26.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
from outcomes import score
pd.set_option("display.width", 250)

F = pd.read_parquet("research/goldmap/results/events_features.parquet")
F["pnl"] = F["pnl_q90"]                       # pure structural exit, no stop/target search
Y1, Y2 = F[F.year == "2024-25"], F[F.year == "2025-26"]
print(f"events {len(F):,}  ({len(Y1):,} + {len(Y2):,});  exit = end of the 90-minute quarter")
print(f"baseline expectancy: year1 {Y1.pnl.mean():+.3f}   year2 {Y2.pnl.mean():+.3f}\n")

FEATS = ["comp_p40", "comp_atr", "act_p40", "spread_p40", "spread_rel", "anchor_eff",
         "body_ratio", "loc_in_anchor", "dist_tdo_atr", "speed", "anchor_ticks",
         "anchor_rng", "q90_idx", "sig_mq"]
BOOL = ["cont", "long", "anchor_up", "with_tdo"]

print("=" * 118)
print("UNIVARIATE SCAN — top-half minus bottom-half expectancy, computed in each year")
print("A feature is only interesting if BOTH years agree in sign. Ranked by the weaker year.")
print("=" * 118)
rows = []
for f in FEATS:
    d = F.dropna(subset=[f])
    if len(d) < 500:
        continue
    for yr in ("2024-25", "2025-26"):
        pass
    res = {}
    for yr in ("2024-25", "2025-26"):
        dy = d[d.year == yr]
        cut = dy[f].median()
        hi, lo = dy[dy[f] > cut].pnl, dy[dy[f] <= cut].pnl
        res[yr] = (hi.mean() - lo.mean(), len(hi), len(lo))
    a, b = res["2024-25"][0], res["2025-26"][0]
    rows.append(dict(feature=f, d24=a, d25=b, agree=(np.sign(a) == np.sign(b)),
                     weaker=min(abs(a), abs(b)) * np.sign(a) if np.sign(a) == np.sign(b) else 0.0))
for f in BOOL:
    d = F.dropna(subset=[f])
    res = {}
    for yr in ("2024-25", "2025-26"):
        dy = d[d.year == yr]
        hi, lo = dy[dy[f].astype(bool)].pnl, dy[~dy[f].astype(bool)].pnl
        res[yr] = hi.mean() - lo.mean()
    a, b = res["2024-25"], res["2025-26"]
    rows.append(dict(feature=f + " (T-F)", d24=a, d25=b, agree=(np.sign(a) == np.sign(b)),
                     weaker=min(abs(a), abs(b)) * np.sign(a) if np.sign(a) == np.sign(b) else 0.0))
S = pd.DataFrame(rows).sort_values("weaker", key=abs, ascending=False)
print(f"  {'feature':<24}{'delta 24-25':>13}{'delta 25-26':>13}{'agree?':>9}{'weaker side':>14}")
for _, r in S.iterrows():
    print(f"  {r.feature:<24}{r.d24:>+13.3f}{r.d25:>+13.3f}{str(r.agree):>9}{r.weaker:>+14.3f}")
S.to_csv("research/goldmap/results/feature_scan.csv", index=False)
n_agree = int(S.agree.sum())
print(f"\n  features agreeing in sign across the two years: {n_agree} of {len(S)}")
print(f"  expected by chance alone if every feature were noise: {len(S)/2:.0f}")
best = S[S.agree].head(3)
print(f"  largest consistent effect: {best.iloc[0].feature} at {best.iloc[0].weaker:+.3f} "
      f"points a trade (baseline loss is {F.pnl.mean():+.3f})")

print("\n" + "=" * 118)
print("PART 23 — HONEST MODEL TEST: fit on 2024-25 ONLY, apply once to 2025-26")
print("=" * 118)
from sklearn.tree import DecisionTreeRegressor, export_text
from sklearn.linear_model import LogisticRegression
use = [f for f in FEATS if f not in ("q90_idx", "sig_mq")] + ["cont", "long"]
tr = Y1.dropna(subset=use).copy(); te = Y2.dropna(subset=use).copy()
Xtr, Xte = tr[use].astype(float).to_numpy(), te[use].astype(float).to_numpy()
print(f"  train {len(tr):,}   test {len(te):,}   features {len(use)}")
for depth in (2, 3):
    m = DecisionTreeRegressor(max_depth=depth, min_samples_leaf=200, random_state=0)
    m.fit(Xtr, tr.pnl)
    for thr in (0.0,):
        ptr, pte = m.predict(Xtr), m.predict(Xte)
        sel_tr, sel_te = tr.pnl[ptr > thr], te.pnl[pte > thr]
        f = lambda p: (f"n={len(p):>5} exp={p.mean():+.3f} PF="
                       f"{(p[p>0].sum()/-p[p<0].sum() if (p<0).any() else np.inf):.3f}")
        print(f"  tree depth {depth}: IN-SAMPLE {f(sel_tr)}   |   OUT-OF-SAMPLE {f(sel_te)}")
m = LogisticRegression(C=0.1, max_iter=2000)
m.fit((Xtr - Xtr.mean(0)) / (Xtr.std(0) + 1e-9), (tr.pnl > 0).astype(int))
sc = m.predict_proba((Xte - Xtr.mean(0)) / (Xtr.std(0) + 1e-9))[:, 1]
for q in (0.5, 0.75, 0.9):
    sel = te.pnl[sc >= np.quantile(sc, q)]
    print(f"  logistic, top {100*(1-q):>2.0f}% of test scores: n={len(sel):>5} "
          f"exp={sel.mean():+.3f} PF={(sel[sel>0].sum()/-sel[sel<0].sum()):.3f}")
