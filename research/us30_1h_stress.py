import sys, numpy as np, pandas as pd
sys.path.insert(0,"research"); import mean_reversion_lab as L
from cost_gated_lab import load, rs, D, SLIP
df=rs(D["US30"],"1h"); a=L.atr(df); c=df.close.to_numpy(float)
t=L.run(df,L.state_zrev(c,n=100,entry=2.5),a,2.0,0.0,stop_atr=6.0)
dt=df.index[t.bar.values]
hold=[]
print("US30 1h z100/2.5 -- STRESS")
# holding period
o=df.index
for i,r in t.iterrows(): pass
print(f"  n={len(t)}  span {dt.min().date()} -> {dt.max().date()}")
# drop the best year, drop 2026, walk-forward by year
for drop in [None,2026,2021,2025]:
    m=(dt.year!=drop) if drop else np.ones(len(t),bool)
    s=L.stats(t[m]); print(f"  excluding {str(drop):5s}: n={s['n']:4d} PF={s['pf']:.3f} net={s['net']:8.1f}")
# anchored walk-forward: train nothing (params fixed), just report each year forward
print("  anchored yearly:")
for y in sorted(set(dt.year)):
    s=L.stats(t[dt.year==y]); print(f"    {y}: n={s['n']:3d} PF={s['pf']:.2f} net={s['net']:8.1f} WR={s['wr']:.0f}%")
# equity-curve monotonicity: rolling 30-trade PF
p=t.pnl.to_numpy(); w=30
rp=[np.sum(p[i:i+w][p[i:i+w]>0])/max(1e-9,-np.sum(p[i:i+w][p[i:i+w]<0])) for i in range(0,len(p)-w)]
rp=np.array(rp)
print(f"  rolling 30-trade PF: min={rp.min():.2f} median={np.median(rp):.2f} max={rp.max():.2f} "
      f"share<1.0={100*(rp<1).mean():.0f}%")
# how much of net is the single best trade
ps=np.sort(p)[::-1]
print(f"  best trade = {100*ps[0]/p.sum():.1f}% of net | top5 = {100*ps[:5].sum()/p.sum():.1f}% | "
      f"median trade = {np.median(p):+.1f}")
# per-side
for d,lbl in [(1,"LONG"),(-1,"SHORT")]:
    pass
print("  long/short split needs dir column -- recomputing:")
st=L.state_zrev(c,n=100,entry=2.5)
