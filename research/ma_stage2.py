import numpy as np, pandas as pd, time
from research.au200_lab import load
from research.au200_ma import *
d15=load("data/au200_15m.csv.gz"); d5=load("data/au200_5m.csv.gz"); a5=atr(d5,14)
cut=pd.Timestamp("2023-08-01",tz="Australia/Sydney")

TOP=[("EMA",5,20,True),("EMA",5,20,False),("EMA",8,21,True),("EMA",10,30,True),
     ("SMA",5,20,True),("SMA",8,21,True)]

print("="*118); print("STEP 2a — SLIPPAGE SENSITIVITY, exit = opposite cross only"); print("="*118)
print(f"{'arm':<28}"+"".join(f"{'PF@'+str(s):>9}" for s in SLIPS)+f"{'net@1.5':>10}{'net@2.0':>10}")
keep=[]
for mt,f,s,lo in TOP:
    st=cross_state(d15,f,s,mt,long_only=lo)
    pfs=[];nets={}
    for sl in SLIPS:
        r=stat(run(st,d5,slip=sl),"")
        pfs.append(r["pf"]); nets[sl]=r["net"]
    nm=f"{mt}{f}/{s} {'long' if lo else 'both'}"
    print(f"{nm:<28}"+"".join(f"{p:>9.3f}" for p in pfs)+f"{nets[1.5]:>10.0f}{nets[2.0]:>10.0f}")
    if pfs[3]>1.0: keep.append((mt,f,s,lo))
print(f"\n  arms above PF 1.0 at 2.0 pt/side: {len(keep)}  -> {[f'{a[0]}{a[1]}/{a[2]}' for a in keep]}")

print("\n"+"="*118); print("STEP 2b — YEAR BY YEAR at 1.0 pt/side"); print("="*118)
for mt,f,s,lo in TOP:
    st=cross_state(d15,f,s,mt,long_only=lo)
    r=stat(run(st,d5,slip=1.0),"")
    nm=f"{mt}{f}/{s} {'long' if lo else 'both'}"
    line=f"  {nm:<20}"
    for y in range(2020,2027):
        line+=f"{y}:{r.get(f'pf{y}',float('nan')):5.2f} "
    print(line+f"  top10={r['top10']:.0f}%")

print("\n"+"="*118); print("STEP 2c — TIME-BASED OOS (train to 2023-07, test from 2023-08), 1.0 pt"); print("="*118)
print(f"{'arm':<24}{'IS n':>7}{'IS PF':>8}{'OOS n':>7}{'OOS PF':>8}{'degrade':>9}")
for mt,f,s,lo in TOP:
    st=cross_state(d15,f,s,mt,long_only=lo)
    t=run(st,d5,slip=1.0)
    t["dt"]=pd.to_datetime(t["day"])
    if t.dt.dt.tz is None: t["dt"]=t.dt.dt.tz_localize("Australia/Sydney")
    A,B=stat(t[t.dt<cut],""),stat(t[t.dt>=cut],"")
    nm=f"{mt}{f}/{s} {'long' if lo else 'both'}"
    deg=100*(1-B['pf']/A['pf']) if A['pf']>0 else np.nan
    print(f"{nm:<24}{A['n']:>7}{A['pf']:>8.3f}{B['n']:>7}{B['pf']:>8.3f}{deg:>8.1f}%")

print("\n"+"="*118); print("STEP 3 — MIXED CROSS on the 5/20 and 8/21 pairs, long-only, 1.0 pt"); print("="*118)
for f,s in ((5,20),(8,21)):
    for ft,stp in (("EMA","EMA"),("SMA","SMA"),("SMA","EMA"),("EMA","SMA")):
        st=cross_state(d15,f,s,ft,stp,long_only=True)
        r=stat(run(st,d5,slip=1.0),"")
        print(f"  fast {ft}{f} x slow {stp}{s:<4} n={r['n']:>5} WR={r['wr']:5.1f}% "
              f"PF={r['pf']:6.3f} net={r['net']:>9.1f} top10={r['top10']:>7.1f}%")

print("\n"+"="*118); print("STEP 4 — SESSION FILTER and TREND FILTER on EMA5/20 long, 1.0 pt"); print("="*118)
for nm,kw in (("all-day (baseline)",{}),
              ("entries 09:50-10:30",{"win":(590,630)}),
              ("entries 10:00-12:00",{"win":(600,720)}),
              ("+ close > SMA200",{"trend":("SMA",200)}),
              ("+ close > EMA200",{"trend":("EMA",200)}),
              ("+ slow MA rising",{"rising":True}),
              ("+ SMA200 + rising",{"trend":("SMA",200),"rising":True})):
    st=cross_state(d15,5,20,"EMA",long_only=True,**kw)
    r=stat(run(st,d5,slip=1.0),"")
    print(f"  {nm:<26} n={r['n']:>5} WR={r['wr']:5.1f}% PF={r['pf']:6.3f} "
          f"net={r['net']:>9.1f} maxDD={r['maxdd']:>8.1f} top10={r['top10']:>7.1f}%")
