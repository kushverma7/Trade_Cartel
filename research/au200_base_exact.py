import numpy as np, pandas as pd
from research.au200_lab import load

d15 = load("data/au200_15m.csv.gz")        # NATIVE 15m, mintick 0.1
d5  = load("data/au200_5m.csv.gz")         # 5m, for intrabar path resolution
print(f"native 15m: {len(d15):,} bars   5m: {len(d5):,} bars   "
      f"{d15.index[0]} -> {d15.index[-1]}")

def ema(s,n): return pd.Series(s).ewm(span=n,adjust=False).mean().to_numpy()
def rsi(c,n=14):
    d=pd.Series(c).diff(); u=d.clip(lower=0).ewm(alpha=1/n,adjust=False).mean()
    v=(-d.clip(upper=0)).ewm(alpha=1/n,adjust=False).mean()
    return (100-100/(1+u/v.replace(0,np.nan))).to_numpy()
def supertrend(df,f,n):
    h,l,c=(df[k].to_numpy(float) for k in ("high","low","close"))
    pc=np.r_[c[0],c[:-1]]
    tr=np.maximum(h-l,np.maximum(abs(h-pc),abs(l-pc)))
    a=pd.Series(tr).ewm(alpha=1/n,adjust=False).mean().to_numpy()
    hl2=(h+l)/2; up,dn=hl2-f*a,hl2+f*a
    fu,fd=np.copy(up),np.copy(dn); dd=np.ones(len(c))
    for i in range(1,len(c)):
        fu[i]=max(up[i],fu[i-1]) if c[i-1]>fu[i-1] else up[i]
        fd[i]=min(dn[i],fd[i-1]) if c[i-1]<fd[i-1] else dn[i]
        dd[i]=-1 if c[i]>fd[i-1] else (1 if c[i]<fu[i-1] else dd[i-1])
    return dd

c=d15["close"].to_numpy(float)
bull=(c>ema(c,200))&(rsi(c)>50)&(supertrend(d15,3.1,97)<0)
bear=(c<ema(c,200))&(rsi(c)<50)&(supertrend(d15,3.1,97)>0)
m=d15.index.minute.to_numpy()
win=((d15.index.hour==9)&(m==50))|((d15.index.hour==9)&(m==55))|((d15.index.hour==10)&(m==0))
print(f"entry-window bars on native 15m: {win.sum():,}  "
      f"(9:50 and 9:55 can never fire on 15m bars -- only 10:00 does)")
ent={t:(1 if bull[i] else -1) for i,t in enumerate(d15.index)
     if win[i] and (bull[i] or bear[i])}
print(f"signals: {len(ent):,}\n")

def run(path, slip, sl=15.0, arm=3.0, off=0.5, longonly=False):
    o,h,l,cc=(path[k].to_numpy(float) for k in ("open","high","low","close"))
    idx=path.index; day=idx.normalize().to_numpy()
    tr=[]; pos=None
    for i in range(1,len(cc)):
        if pos is not None:
            dd,e=pos["d"],pos["e"]
            pos["pk"]=max(pos["pk"],h[i]) if dd>0 else min(pos["pk"],l[i])
            if not pos["armed"] and (pos["pk"]-e)*dd>=arm: pos["armed"]=True
            st=(e-dd*sl) if not pos["armed"] else pos["pk"]-dd*off
            if (l[i]<=st) if dd>0 else (h[i]>=st):
                px=st-dd*slip
                tr.append(dict(pnl=dd*(px-e)-2.0,day=pos["day"])); pos=None; continue
        if pos is None and idx[i] in ent:
            dd=ent[idx[i]]
            if longonly and dd<0: continue
            pos=dict(d=dd,e=cc[i]+dd*slip,pk=cc[i],armed=False,day=day[i])
    return pd.DataFrame(tr)

def st(t,lbl):
    if len(t)==0: return print(f"  {lbl:<38} no trades")
    p=t.pnl.to_numpy(); gw,gl=p[p>0].sum(),-p[p<0].sum()
    eq=np.cumsum(p); dd=float(np.max(np.maximum.accumulate(eq)-eq))
    print(f"  {lbl:<38} n={len(p):>4} WR={100*(p>0).mean():5.1f}% "
          f"PF={(gw/gl if gl>0 else 9.99):6.3f} net={p.sum():>9.1f} maxDD={dd:>7.1f}")
    return t

print("="*104)
print("EXIT PATH RESOLUTION — identical signals, path walked at 15m vs 5m")
print("  TV models the 15m path. The trail sits 0.5 pt behind the peak, which is")
print("  far smaller than a 15m bar's range, so bar-order assumptions decide most trades.")
print("="*104)
print("\n15-MINUTE path (reproduces TradingView; TV reported n=937 WR 83.0% PF 2.014):")
for s in (0.0,0.5,1.0,1.5,2.0): st(run(d15,s),f"slip {s} pt/side")
print("\n5-MINUTE path (same trades, 3x finer event ordering):")
best=None
for s in (0.0,0.5,1.0,1.5,2.0):
    t=st(run(d5,s),f"slip {s} pt/side")
    if s==1.0: best=t
print("\n5-MINUTE path, LONG ONLY:")
for s in (0.0,1.0): st(run(d5,s,longonly=True),f"long-only slip {s}")

print("\n"+"="*104); print("ATTRIBUTION — 5m path, 1.0 pt/side"); print("="*104)
best["yr"]=pd.to_datetime(best["day"]).dt.year; tot=best.pnl.sum()
print(f"{'year':>6}{'n':>6}{'PF':>8}{'net':>10}{'% of total':>12}")
for y,g in best.groupby("yr"):
    p=g.pnl.to_numpy(); w,l=p[p>0].sum(),-p[p<0].sum()
    print(f"{y:>6}{len(g):>6}{(w/l if l>0 else 9.99):>8.2f}{p.sum():>10.1f}{100*p.sum()/tot:>11.1f}%")
ex=best[best.yr!=2026]; p=ex.pnl.to_numpy(); w,l=p[p>0].sum(),-p[p<0].sum()
print(f"\n  EXCLUDING 2026: n={len(ex)} PF={w/l:.3f} net={p.sum():+.1f}")
ps=np.sort(best.pnl.to_numpy())[::-1]
print(f"  top 5 = {100*ps[:5].sum()/tot:.1f}% of net | top 10 = {100*ps[:10].sum()/tot:.1f}%")
print(f"  buy & hold same span: {c[-1]-c[0]:+.1f} pts")
