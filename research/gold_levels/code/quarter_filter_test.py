"""Is "entry within 7.5 points of a $25 quarter" a level effect, or a coin flip?

The proposed filter keeps 59 of the locked universe's trades and lifts profit
factor from ~1.6 to ~2.1. Two things could produce that:

  (a) $25 quarters matter, or
  (b) any rule that discards 55% of the trades has a wide distribution of
      possible profit factors, and this one landed high.

There is a control that separates them cleanly and costs nothing. Keep the rule
EXACTLY as written -- same spacing, same 7.5-point tolerance, same everything --
and only move the grid's PHASE: levels at 25k+1, 25k+2, ... 25k+24 instead of
25k. Those grids are not round. If roundness is doing the work, phase 0 must
stand out from the other 24. If phase 0 sits inside that spread, the filter is
selecting a subset, not a level.

The second control is blunter: random subsets of the same size, which says how
much profit factor moves when you drop 55% of 131 trades for no reason at all.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "/home/user/Trade_Cartel/research/gold_exit_eng/code")
from entry_universe import build, splits, label
from exits import resolve, stats

SL, TP = 15.0, 25.0
GRID, TOL = 25.0, 7.5

tr = build(1100, 2.0); d1, d2 = splits(tr); label(tr, d1, d2)
import pickle
prep = pickle.load(open("/home/user/Trade_Cartel/research/gold_10am_flip/data/prep10.pkl", "rb"))
BODY = {pd.Timestamp(d["date"]): (d["bhi"] - d["blo"]) for d in prep}   # bhi/blo are prices, not ticks
for t in tr:
    t["body"] = BODY[t["date"]]

print(f"locked universe                    n={len(tr)}")
tr1 = [t for t in tr if t["body"] >= 1.0]
print(f"+ 10AM body >= 1.0                 n={len(tr1)}")


def dist_to_grid(px, phase):
    r = (px - phase) % GRID
    return min(r, GRID - r)


def score(sub):
    recs = [(t["split"], resolve(t, sl=SL, tp=TP)[0]) for t in sub]
    A = stats([v for _, v in recs])
    S_ = {s: stats([v for sp, v in recs if sp == s]) for s in ("DEV", "VAL", "HOLD")}
    return dict(n=A["n"], pf=A["pf"], exp=A["exp"], net=A["net"], wr=A["wr"], mdd=A["mdd"],
                pf_dev=S_["DEV"]["pf"], pf_val=S_["VAL"]["pf"], pf_hold=S_["HOLD"]["pf"],
                n_dev=S_["DEV"]["n"], n_val=S_["VAL"]["n"], n_hold=S_["HOLD"]["n"],
                minPF=min(S_[s]["pf"] for s in S_))


base = score(tr1)
sel0 = [t for t in tr1 if dist_to_grid(t["entry"], 0.0) <= TOL]
r0 = score(sel0)
print(f"+ within {TOL:g} of a $25 quarter    n={r0['n']}\n")
print(f"{'='*100}")
print("REPRODUCTION of the proposed setup (SL 15 / TP 25, tick-exact bid/ask first passage)")
print(f"{'='*100}")
for nm, r in (("no quarter filter", base), ("PROPOSED (round $25 grid)", r0)):
    print(f"{nm:<28} n={r['n']:>4}  PF={r['pf']:.3f}  exp={r['exp']:+.2f}  net={r['net']:+.1f}  "
          f"WR={r['wr']:.1f}%  DD={r['mdd']:.1f}  splits {r['pf_dev']:.2f}/{r['pf_val']:.2f}/{r['pf_hold']:.2f}"
          f"  ({r['n_dev']}/{r['n_val']}/{r['n_hold']})  minPF={r['minPF']:.2f}")

print(f"\n{'='*100}")
print("CONTROL 1 — THE SAME FILTER ON A GRID THAT IS NOT ROUND (phase shifted, spacing unchanged)")
print(f"{'='*100}")
rows = []
for ph in range(25):
    sub = [t for t in tr1 if dist_to_grid(t["entry"], float(ph)) <= TOL]
    if len(sub) < 20:
        continue
    r = score(sub); r["phase"] = ph; rows.append(r)
P = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(P[["phase", "n", "pf", "exp", "net", "wr", "mdd", "pf_dev", "pf_val", "pf_hold", "minPF"]]
      .to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
oth = P[P.phase != 0]
print(f"\nround grid (phase 0):      PF {r0['pf']:.3f}   minPF {r0['minPF']:.2f}")
print(f"the 24 non-round grids:    PF {oth.pf.mean():.3f} +- {oth.pf.std():.3f}   "
      f"range {oth.pf.min():.2f}..{oth.pf.max():.2f}")
print(f"                           minPF {oth.minPF.mean():.2f} +- {oth.minPF.std():.2f}   "
      f"range {oth.minPF.min():.2f}..{oth.minPF.max():.2f}")
print(f"non-round grids beating the round one on PF:    {int((oth.pf    >= r0['pf']).sum())} of {len(oth)}")
print(f"non-round grids beating the round one on minPF: {int((oth.minPF >= r0['minPF']).sum())} of {len(oth)}")

print(f"\n{'='*100}")
print(f"CONTROL 2 — RANDOM SUBSETS of {r0['n']} of the {len(tr1)} trades (2000 draws, no rule at all)")
print(f"{'='*100}")
rng = np.random.default_rng(5)
pf_n, mp_n = [], []
for _ in range(2000):
    sub = [tr1[i] for i in rng.choice(len(tr1), r0["n"], replace=False)]
    s = score(sub)
    if np.isfinite(s["pf"]): pf_n.append(s["pf"])
    if np.isfinite(s["minPF"]): mp_n.append(s["minPF"])
pf_n, mp_n = np.array(pf_n), np.array(mp_n)
print(f"random-subset PF:    mean {pf_n.mean():.2f}  sd {pf_n.std():.2f}  "
      f"5-95% {np.percentile(pf_n,5):.2f}..{np.percentile(pf_n,95):.2f}   "
      f"P(>= {r0['pf']:.2f}) = {(pf_n>=r0['pf']).mean():.3f}")
print(f"random-subset minPF: mean {mp_n.mean():.2f}  sd {mp_n.std():.2f}  "
      f"5-95% {np.percentile(mp_n,5):.2f}..{np.percentile(mp_n,95):.2f}   "
      f"P(>= {r0['minPF']:.2f}) = {(mp_n>=r0['minPF']).mean():.3f}")
P.to_csv("/home/user/Trade_Cartel/research/gold_levels/results/quarter_filter_phase.csv", index=False)
