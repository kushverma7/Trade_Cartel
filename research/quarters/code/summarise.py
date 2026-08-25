"""Aggregate the three tests into the answer."""
import numpy as np, pandas as pd
from scipy import stats as st
R = "research/quarters/results"

print("="*104)
print("TEST 1  P(continuation) from a quarter-point crossing.  H99 predicts 0.500")
print("="*104)
a = pd.read_csv(f"{R}/asymmetry.csv")
for year in a.year.unique():
    print(f"\n  {year}")
    print(f"  {'S':>8}{'n (round)':>12}{'ROUND':>9}{'shifted mean':>14}{'shifted sd':>12}"
          f"{'z vs shifted':>14}{'rank':>8}")
    for S in sorted(a.S.unique()):
        g = a[(a.year == year) & (a.S == S)]
        if g.empty: continue
        rnd = g[g["round"]].p.iloc[0]; sh = g[~g["round"]].p.values
        z = (rnd - sh.mean()) / sh.std(ddof=1) if sh.std(ddof=1) > 0 else np.nan
        rank = int((np.sort(np.append(sh, rnd))[::-1] == rnd).argmax()) + 1
        print(f"  {S:8.2f}{g[g['round']].n.iloc[0]:>12,}{rnd:>9.4f}{sh.mean():>14.4f}"
              f"{sh.std(ddof=1):>12.5f}{z:>+14.2f}{rank:>5}/12")

print("\n" + "="*104)
print("TEST 2  Swing extremes within 0.10*S of a quarter point.  Base rate 20%")
print("="*104)
e = pd.read_csv(f"{R}/extremes.csv")
pool = (e.assign(k_hits=e.hit * e.n).groupby(["kind", "S", "k", "round"])
          .agg(hits=("k_hits", "sum"), n=("n", "sum")).reset_index())
pool["rate"] = pool.hits / pool.n
print("\n  BOTH YEARS POOLED")
print(f"  {'kind':<8}{'S':>8}{'n':>7}{'ROUND':>9}{'shifted mean':>14}{'rank':>8}{'binom p vs 20%':>16}")
for kind in ("daily", "weekly"):
    for S in sorted(pool.S.unique()):
        g = pool[(pool.kind == kind) & (pool.S == S)]
        if g.empty: continue
        rnd = g[g["round"]].rate.iloc[0]; sh = g[~g["round"]].rate.values
        n = int(g[g["round"]].n.iloc[0]); h = int(round(rnd * n))
        rank = int((np.sort(np.append(sh, rnd))[::-1] == rnd).argmax()) + 1
        p = st.binomtest(h, n, 0.20, alternative="greater").pvalue
        print(f"  {kind:<8}{S:>8.2f}{n:>7}{rnd:>9.3f}{sh.mean():>14.3f}{rank:>5}/12{p:>16.3f}")
print("\n  PER YEAR -- does the round grid's rank hold up out of sample?")
print(f"  {'kind':<8}{'S':>8}{'2025-26 rank':>15}{'2024-25 rank':>15}")
for kind in ("daily", "weekly"):
    for S in sorted(e.S.unique()):
        rr = []
        for year in ("2025-26", "2024-25"):
            g = e[(e.year == year) & (e.kind == kind) & (e.S == S)]
            if g.empty: rr.append(None); continue
            rnd = g[g["round"]].hit.iloc[0]; sh = g[~g["round"]].hit.values
            rr.append(int((np.sort(np.append(sh, rnd))[::-1] == rnd).argmax()) + 1)
        print(f"  {kind:<8}{S:>8.2f}{str(rr[0])+'/12':>15}{str(rr[1])+'/12':>15}")

print("\n" + "="*104)
print("TEST 3  The Hesitation Zone system, tick-exact with real bid/ask fills")
print("="*104)
s = pd.read_csv(f"{R}/system.csv")
y = s[s.config == "yotov"]
for year in y.year.unique():
    print(f"\n  {year}   [baseline: zone 0.30S, stop at Q, target next quarter point, 3-day clock]")
    print(f"  {'S':>8}{'n':>7}{'ROUND PF':>10}{'shifted PF mean':>17}{'range':>16}"
          f"{'rank':>8}{'ROUND net $':>13}")
    for S in sorted(y.S.unique()):
        g = y[(y.year == year) & (y.S == S)]
        if g.empty or not g["round"].any(): continue
        rnd = g[g["round"]].pf.iloc[0]; sh = g[~g["round"]].pf.values
        if len(sh) == 0: continue
        rank = int((np.sort(np.append(sh, rnd))[::-1] == rnd).argmax()) + 1
        print(f"  {S:8.2f}{g[g['round']].n.iloc[0]:>7}{rnd:>10.3f}{sh.mean():>17.3f}"
              f"{f'{sh.min():.3f}-{sh.max():.3f}':>16}{rank:>5}/12"
              f"{g[g['round']].net_usd.iloc[0]:>+13.0f}")
print("\n  CONFIG VARIANTS (round grid only)")
print(f"  {'year':<9}{'S':>8}{'config':<14}{'n':>7}{'PF':>8}{'exp R':>9}{'net $':>11}")
for _, r in s[s.config != "yotov"].sort_values(["year", "S", "config"]).iterrows():
    print(f"  {r.year:<9}{r.S:>8.2f}{r.config:<14}{int(r.n):>7}{r.pf:>8.3f}"
          f"{r.exp:>+9.4f}{r.net_usd:>+11.0f}")
