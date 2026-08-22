"""Fully honest walk-forward: EVERY parameter re-selected from past data only.

The earlier walk-forward re-derived only the anchor and inherited body, quarter,
spread and the exit from the full-sample fit -- which is the very thing under
suspicion. Here the whole parameter vector is chosen inside each training
window and then traded, untouched, on the next block.

Equivalence used for speed: in microq3.signals() the body, quarter and spread
filters all SKIP the day and none of them changes which break is first. So
building once with every filter open and post-filtering the output is identical
to rebuilding, and lets a 10,000-point grid be evaluated per fold.
"""
import sys, numpy as np, pandas as pd, itertools
sys.path.insert(0, "research/microq3/code")
import engine as E
import microq3 as M

ANCHORS = list(range(18 * 60 + 15, 19 * 60 + 45, 5))
BODYMIN = [0.0, 0.5, 1.0, 1.5, 2.0]
BODYMAX = [6.25, 10.0, None]
QD = [5.0, 6.25, 7.5, None]
SPR = [1.25, 1.5, 2.0, None]
SLS = [12.5, 15.5, 20.0]
TPS = [20.0, 25.5, 30.0]

print("building signal sets (all filters open) ...", flush=True)
raw = {}
for a in ANCHORS:
    t = M.signals(anchor_start=a, win_from=a + 15, win_to=a + 45,
                  body_min=0.0, body_max=None, qdist=None, spread_max=None)
    for sl, tp in itertools.product(SLS, TPS):
        raw[(a, sl, tp)] = M.apply(t, sl, tp)
print(f"  {len(raw)} (anchor, SL, TP) tables built")

# verify the post-filter equivalence against a real rebuild
chk = M.apply(M.signals(), 15.5, 25.5)
d = raw[(18 * 60 + 45, 15.5, 25.5)]
d2 = d[(d.anchor_body >= 1.0) & (d.anchor_body <= 6.25) &
       (d.dist25 <= 6.25) & (d.entry_spread <= 1.5)]
assert len(d2) == len(chk) and abs(d2.pnl.sum() - chk.pnl.sum()) < 1e-6, \
    f"post-filter mismatch {len(d2)} vs {len(chk)}"
print(f"  post-filter equivalence verified: {len(d2)} trades, net {d2.pnl.sum():+.1f}\n")

GRID = list(itertools.product(ANCHORS, BODYMIN, BODYMAX, QD, SPR, SLS, TPS))
print(f"parameter grid: {len(GRID):,} points per fold")


def sel(a, bmn, bmx, q, sp, sl, tp, lo=None, hi=None):
    d = raw[(a, sl, tp)]
    m = (d.anchor_body >= bmn)
    if bmx is not None: m &= (d.anchor_body <= bmx)
    if q is not None:   m &= (d.dist25 <= q)
    if sp is not None:  m &= (d.entry_spread <= sp)
    if lo is not None:  m &= (d.date > lo)
    if hi is not None:  m &= (d.date <= hi)
    return d[m]


alld = sorted(set(pd.concat([raw[k] for k in raw]).date))
print(f"candidate dates: {len(alld)}   {alld[0]} .. {alld[-1]}\n")

folds, oos = [], []
n_tr = int(len(alld) * 0.40); step = int(len(alld) * 0.15)
i = n_tr
while i < len(alld):
    tr_end = alld[i - 1]; te_end = alld[min(i + step, len(alld)) - 1]
    best, bscore = None, -1e9
    for g in GRID:
        t = sel(*g, hi=tr_end)
        if len(t) < 10:                       # need a real training sample
            continue
        s = E.stats(t.pnl.tolist())
        if s["exp"] > bscore:
            best, bscore = g, s["exp"]
    if best is None:
        i += step; continue
    te = sel(*best, lo=tr_end, hi=te_end)
    s = E.stats(te.pnl.tolist())
    a = best[0]
    folds.append(dict(train_to=tr_end, test_to=te_end,
                      anchor=f"{a//60:02d}:{a%60:02d}", bmin=best[1], bmax=best[2],
                      qd=best[3], spr=best[4], sl=best[5], tp=best[6],
                      train_exp=bscore, n=s["n"], pf=s["pf"], exp=s["exp"], net=s["net"]))
    oos += te.pnl.tolist()
    i += step
    print(f"  fold to {tr_end}: picked {folds[-1]['anchor']} body>={best[1]} "
          f"max={best[2]} q={best[3]} spr={best[4]} SL{best[5]}/TP{best[6]} "
          f"-> OOS n={s['n']} exp={s['exp']:+.2f}", flush=True)

F = pd.DataFrame(folds)
F.to_csv("research/microq3/results/K_walkforward_full.csv", index=False)
pd.set_option("display.width", 250)
print("\n" + "=" * 110)
print("FULL-PARAMETER WALK-FORWARD — every parameter chosen on past data only")
print("=" * 110)
print(F.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
S = E.stats(oos)
print(f"\nPOOLED OUT-OF-SAMPLE: n={S['n']}  PF={S['pf']:.2f}  exp={S['exp']:+.2f}  "
      f"net={S['net']:+.1f}  maxDD={S['mdd']:.1f}  WR={S['wr']:.0f}%")
print(f"anchor stability: {F.anchor.nunique()} distinct anchors over {len(F)} folds  {F.anchor.tolist()}")
print(f"exit stability:   {F[['sl','tp']].drop_duplicates().shape[0]} distinct (SL,TP) pairs")
