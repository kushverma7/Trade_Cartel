import numpy as np, pandas as pd
from research.au200_lab import load, supertrend, adx, sig_gap, sig_base, flip_engine, score
from research.au200_ma import *
d15=load("data/au200_15m.csv.gz"); d5=load("data/au200_5m.csv.gz"); a5=atr(d5,14)
cut=pd.Timestamp("2023-08-01",tz="Australia/Sydney")

BEST={
 "EMA5/20 L +rising":        dict(fast=5,slow=20,ftype="EMA",long_only=True,rising=True),
 "EMA5/20 L +SMA200 +rising":dict(fast=5,slow=20,ftype="EMA",long_only=True,rising=True,trend=("SMA",200)),
 "EMA5/20 L (plain)":        dict(fast=5,slow=20,ftype="EMA",long_only=True),
 "SMA5/20 L +rising":        dict(fast=5,slow=20,ftype="SMA",long_only=True,rising=True),
 "SMA5/20 L +SMA200 +rising":dict(fast=5,slow=20,ftype="SMA",long_only=True,rising=True,trend=("SMA",200)),
}
print("="*120); print("STEP 6 — EXIT VARIANTS on the two leading arms, 1.0 pt/side"); print("="*120)
EX={"A cross only":dict(),
    "B cross or 30pt stop":dict(stop_pts=30.0),
    "B cross or 3xATR stop":dict(stop_atr=3.0),
    "C cross or 20pt trail (arm 10)":dict(trail_pts=20.0,arm_pts=10.0),
    "C cross or 30pt trail (arm 15)":dict(trail_pts=30.0,arm_pts=15.0),
    "D cross + flat 16:00":dict(flat_hour=16)}
for nm in ("EMA5/20 L +rising","EMA5/20 L +SMA200 +rising"):
    st=cross_state(d15,**BEST[nm]); print(f"\n  {nm}")
    for en,kw in EX.items():
        r=stat(run(st,d5,slip=1.0,a5=a5,**kw),"")
        print(f"    {en:<32} n={r['n']:>5} WR={r['wr']:5.1f}% PF={r['pf']:6.3f} "
              f"net={r['net']:>9.1f} maxDD={r['maxdd']:>8.1f} top10={r['top10']:>7.1f}%")

print("\n"+"="*120); print("STEP 2a(bis) — SLIPPAGE on the leading arms, exit A"); print("="*120)
print(f"{'arm':<30}"+"".join(f"{'PF@'+str(s):>9}" for s in SLIPS)+f"{'net@2.0':>10}{'maxDD':>9}")
for nm,kw in BEST.items():
    st=cross_state(d15,**kw); pfs=[];n2=None;md=None
    for sl in SLIPS:
        r=stat(run(st,d5,slip=sl),"")
        pfs.append(r["pf"])
        if sl==2.0: n2,md=r["net"],r["maxdd"]
    print(f"{nm:<30}"+"".join(f"{p:>9.3f}" for p in pfs)+f"{n2:>10.0f}{md:>9.0f}")

print("\n"+"="*120); print("YEAR BY YEAR and OOS, leading arms, 1.0 pt"); print("="*120)
for nm,kw in BEST.items():
    st=cross_state(d15,**kw); t=run(st,d5,slip=1.0); r=stat(t,"")
    t["dt"]=pd.to_datetime(t["day"])
    if t.dt.dt.tz is None: t["dt"]=t.dt.dt.tz_localize("Australia/Sydney")
    A,B=stat(t[t.dt<cut],""),stat(t[t.dt>=cut],"")
    line=f"  {nm:<28}"
    for y in range(2020,2027): line+=f"{y}:{r.get(f'pf{y}',float('nan')):5.2f} "
    print(line+f" | IS {A['pf']:.3f}({A['n']}) OOS {B['pf']:.3f}({B['n']}) top10={r['top10']:.0f}%")

print("\n"+"="*120); print("STEP 5 — SMA REGIME FILTER ON THE NON-MA FAMILIES (5m signals, flip exit, 1.0 pt)"); print("="*120)
c5=d5["close"].to_numpy(float)
st5=supertrend(d5,1.5,10); ad5=adx(d5,14)
s200=pd.Series(c5).rolling(200).mean().to_numpy()
s50=pd.Series(c5).rolling(50).mean().to_numpy()
base=sig_base(d5); gap=sig_gap(d5,1.0,st=st5,use_st=True)
for lbl,sig in (("C AU200-BASE",base),("A gap+ST",gap)):
    for fn,filt in (("no filter",None),("close>SMA200",c5>s200),("close>SMA50",c5>s50)):
        s=sig.copy()
        if filt is not None:
            s=np.where((s>0)&filt,1,np.where((s<0)&~filt,-1,0)).astype(np.int8)
        r=score(flip_engine(d5,s,slip=1.0),d5,"","")
        print(f"  {lbl:<16} {fn:<14} n={r.get('n',0):>5} WR={r.get('wr',0):5.1f}% "
              f"PF={r.get('pf',0):6.3f} net={r.get('net',0):>9.1f} top10={r.get('top10_net',0):>8.1f}%")
