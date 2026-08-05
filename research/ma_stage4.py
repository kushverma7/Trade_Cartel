import numpy as np, pandas as pd
from research.au200_lab import load
from research.au200_ma import *
d15=load("data/au200_15m.csv.gz"); d5=load("data/au200_5m.csv.gz"); a5=atr(d5,14)
cut=pd.Timestamp("2023-08-01",tz="Australia/Sydney")
CH=dict(fast=5,slow=20,ftype="EMA",long_only=True,rising=True)

print("="*120); print("CHAMPION STRESS — EMA5/20 long + rising slow MA + 3xATR stop"); print("="*120)
st=cross_state(d15,**CH)
print(f"{'slippage/side':>14}{'n':>7}{'WR':>8}{'PF':>8}{'net':>11}{'maxDD':>9}{'top10':>8}")
for sl in (0.0,1.0,1.5,2.0,3.0):
    r=stat(run(st,d5,slip=sl,stop_atr=3.0,a5=a5),"")
    print(f"{sl:>14.1f}{r['n']:>7}{r['wr']:>8.1f}{r['pf']:>8.3f}{r['net']:>11.0f}{r['maxdd']:>9.0f}{r['top10']:>7.1f}%")

t=run(st,d5,slip=1.0,stop_atr=3.0,a5=a5); r=stat(t,"")
t["dt"]=pd.to_datetime(t["day"])
if t.dt.dt.tz is None: t["dt"]=t.dt.dt.tz_localize("Australia/Sydney")
A,B=stat(t[t.dt<cut],""),stat(t[t.dt>=cut],"")
print(f"\n  year by year @1.0pt: "+" ".join(f"{y}:{r.get(f'pf{y}',float('nan')):.2f}" for y in range(2020,2027)))
print(f"  OOS split: IS {A['pf']:.3f} (n={A['n']})  ->  OOS {B['pf']:.3f} (n={B['n']})  "
      f"degradation {100*(1-B['pf']/A['pf']):+.1f}%")
p=np.sort(t.pnl.to_numpy())[::-1]; tot=p.sum()
print(f"  concentration: top5 {100*p[:5].sum()/tot:.1f}%  top10 {100*p[:10].sum()/tot:.1f}%  "
      f"top50 {100*p[:50].sum()/tot:.1f}%  of net")
yr=t.groupby(t.dt.dt.year).pnl.sum()
print(f"  net by year: "+" ".join(f"{y}:{v:+.0f}" for y,v in yr.items()))
print(f"  years positive: {(yr>0).sum()}/{len(yr)}")
mc=[]
for sd in (11,101,2027,55555,987654):
    g=np.random.default_rng(sd)
    for _ in range(2000):
        x=g.permutation(t.pnl.to_numpy()); e=np.cumsum(x)
        mc.append(np.max(np.maximum.accumulate(e)-e))
print(f"  Monte Carlo (5 seeds x 2000): median maxDD {np.median(mc):.0f} pts, "
      f"95th pct {np.percentile(mc,95):.0f} pts  (historical {r['maxdd']:.0f})")

print("\n"+"="*120); print("PLATEAU — neighbouring pairs and stop multiples, 1.0 pt, all with +rising"); print("="*120)
print(f"{'pair':>10}"+"".join(f"{'ATR'+str(m):>10}" for m in (2.0,2.5,3.0,3.5,4.0)))
for f,s in ((4,16),(5,18),(5,20),(5,24),(6,20),(6,24),(8,21),(8,30),(10,30)):
    row=f"{f}/{s:<8}"
    for mlt in (2.0,2.5,3.0,3.5,4.0):
        ss=cross_state(d15,f,s,"EMA",long_only=True,rising=True)
        row+=f"{stat(run(ss,d5,slip=1.0,stop_atr=mlt,a5=a5),'')['pf']:>10.3f}"
    print(f"{row}")

print("\n"+"="*120); print("BOTH-SIDES vs LONG-ONLY, champion config, 1.0 pt"); print("="*120)
for lo in (True,False):
    ss=cross_state(d15,5,20,"EMA",long_only=lo,rising=True)
    r2=stat(run(ss,d5,slip=1.0,stop_atr=3.0,a5=a5),"")
    print(f"  {'long-only' if lo else 'both sides':<12} n={r2['n']:>5} WR={r2['wr']:5.1f}% "
          f"PF={r2['pf']:6.3f} net={r2['net']:>9.0f} maxDD={r2['maxdd']:>7.0f} top10={r2['top10']:>6.1f}%")
print(f"\n  buy & hold same span: {d5['close'].iloc[-1]-d5['close'].iloc[0]:+.0f} pts")
