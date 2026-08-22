"""Battery part 3: N Monte Carlo, O random-entry placebo, plus the day-selection
control that the grid placebo really needs."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E
import microq3 as M
from engine import PTS

SL, TP = 15.5, 25.5
BASE = M.signals()
BD = M.apply(BASE, SL, TP).sort_values("t_entry").reset_index(drop=True)
p = BD.pnl.to_numpy()
S = E.stats(p.tolist())
print(f"base: n={S['n']} PF={S['pf']:.3f} net={S['net']:+.1f} exp={S['exp']:+.2f} maxDD={S['mdd']:.1f}\n")


def maxdd(x):
    eq = np.cumsum(x); pk = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    return float((pk - eq).max())


def streak(x):
    b = m = 0
    for v in x:
        b = b + 1 if v <= 0 else 0
        m = max(m, b)
    return m


print("=" * 96)
print("N. MONTE CARLO — 50,000 resamples of the realised trade P&L")
print("=" * 96)
rng = np.random.default_rng(7)
NS = 50_000
n = len(p)
# (a) iid bootstrap with replacement
idx = rng.integers(0, n, size=(NS, n))
boot = p[idx]
net_b = boot.sum(1)
gp = np.where(boot > 0, boot, 0).sum(1); gl = -np.where(boot < 0, boot, 0).sum(1)
pf_b = np.where(gl > 0, gp / np.maximum(gl, 1e-9), np.inf)
dd_b = np.array([maxdd(r) for r in boot[:5000]])       # dd is loopy; 5k is plenty
st_b = np.array([streak(r) for r in boot[:5000]])
# (b) order-only shuffle (same trades, different sequence) -> DD / streak distribution
perm = np.argsort(rng.random((5000, n)), axis=1)
sh = p[perm]
dd_s = np.array([maxdd(r) for r in sh]); st_s = np.array([streak(r) for r in sh])


def q(a, name, fmt="{:.2f}"):
    v = [np.percentile(a, x) for x in (1, 5, 10, 50, 90, 95, 99)]
    print(f"  {name:<26}" + "".join(fmt.format(x).rjust(11) for x in v))


print(f"  {'':<26}" + "".join(s.rjust(11) for s in ("p1", "p5", "p10", "median", "p90", "p95", "p99")))
q(net_b, "net (bootstrap)", "{:+.1f}")
q(pf_b[np.isfinite(pf_b)], "PF (bootstrap)")
q(dd_b, "maxDD (bootstrap)", "{:.1f}")
q(st_b, "losing streak (boot)", "{:.0f}")
q(dd_s, "maxDD (order shuffle)", "{:.1f}")
q(st_s, "losing streak (shuffle)", "{:.0f}")
print(f"\n  P(net <= 0) = {(net_b <= 0).mean():.4f}     P(PF < 1) = {(pf_b < 1).mean():.4f}")
print(f"  realised maxDD {S['mdd']:.1f} sits at the {100*(dd_s < S['mdd']).mean():.0f}th percentile "
      f"of order-shuffled draws — the realised sequence was FAVOURABLE" if (dd_s < S['mdd']).mean() < .5
      else f"  realised maxDD {S['mdd']:.1f} is at the {100*(dd_s < S['mdd']).mean():.0f}th percentile of shuffles")
pd.DataFrame(dict(net=net_b[:5000], pf=pf_b[:5000], dd=dd_b, streak=st_b)).to_csv(
    "research/microq3/results/N_montecarlo.csv", index=False)

print("\n" + "=" * 96)
print("O. RANDOM-ENTRY PLACEBO — same days, same direction mix, random entry minute")
print("=" * 96)
# eligible days = the 25 real trade days; random entry uniform in 19:00-19:30 NY,
# same direction as the real trade, same SL/TP, same session end, real bid/ask.
real_days = [(t["day"], t["long"]) for t in BASE]
NR = 4000
exps, pfs = [], []
for it in range(NR):
    pl = []
    for day, long_ in real_days:
        hm = 19 * 60 + int(rng.integers(0, 30))
        k = E.window(day, hm, hm + 1)
        if k is None:
            continue
        k0 = int(E.I0[k[0]])
        kend = E.session_end_index(day, 17 * 60)
        if kend is None or k0 >= kend:
            continue
        r = E.resolve(k0, kend, long_, SL, TP)
        if r:
            pl.append(r["pnl"])
    if len(pl) >= 15:
        st = E.stats(pl)
        exps.append(st["exp"]); pfs.append(st["pf"])
exps = np.array(exps); pfs = np.array(pfs)
print(f"  {NR} simulations, {len(exps)} usable")
print(f"  random-entry expectancy: mean {exps.mean():+.2f}  sd {exps.std():.2f}  "
      f"p95 {np.percentile(exps,95):+.2f}  max {exps.max():+.2f}")
print(f"  random-entry PF:         mean {np.nanmean(pfs):.2f}   p95 {np.nanpercentile(pfs,95):.2f}")
z = (S["exp"] - exps.mean()) / exps.std()
print(f"  REAL expectancy {S['exp']:+.2f}   z = {z:+.2f}   "
      f"empirical p = {((exps >= S['exp']).sum()+1)/(len(exps)+1):.4f}")

print("\n" + "=" * 96)
print("D-bis. GRID PLACEBO, done properly: is the 25/22 split better than a random split?")
print("=" * 96)
# the quarter filter partitions the 47 unfiltered candidates into 25 kept / 22 dropped
allc = M.signals(qdist=None)
AD = M.apply(allc, SL, TP)
keep = AD.dist25 <= 6.25
print(f"  unfiltered candidates: {len(AD)}   kept by the $25 filter: {int(keep.sum())}   "
      f"dropped: {int((~keep).sum())}")
print(f"  kept   net {AD[keep].pnl.sum():+.1f}  PF {E.stats(AD[keep].pnl.tolist())['pf']:.2f}")
print(f"  dropped net {AD[~keep].pnl.sum():+.1f}  PF {E.stats(AD[~keep].pnl.tolist())['pf']:.2f}")
k = int(keep.sum()); tot = len(AD)
draws = np.array([E.stats(AD.pnl.to_numpy()[rng.choice(tot, k, replace=False)].tolist())["pf"]
                  for _ in range(20000)])
real_pf = E.stats(AD[keep].pnl.tolist())["pf"]
print(f"\n  random {k}-of-{tot} subsets: PF median {np.nanmedian(draws):.2f}  "
      f"p95 {np.nanpercentile(draws,95):.2f}  p99 {np.nanpercentile(draws,99):.2f}")
print(f"  the $25 filter's PF {real_pf:.2f} -> empirical p = "
      f"{((draws >= real_pf).sum()+1)/(len(draws)+1):.4f}")
print("  (this asks whether ROUNDNESS picked the good days, or whether any 25-of-47 split")
print("   would land here as often. It is the honest version of the shifted-grid test.)")
