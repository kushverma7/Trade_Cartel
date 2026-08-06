import sys, numpy as np, pandas as pd
sys.path.insert(0,"research")
import mean_reversion_lab as L

FILES={"GOLD":"data/xauusd_15m.csv.gz","US30":"data/us30_15m_native.csv.gz","AU200":"data/au200_15m.csv.gz"}
def load(p):
    df=pd.read_csv(p)
    tc=[c for c in df.columns if c.lower() in ("time","date","datetime","timestamp")][0]
    s=df[tc]
    idx=pd.to_datetime(s,unit="s",utc=True) if pd.api.types.is_numeric_dtype(s) else pd.to_datetime(s,utc=True,format="mixed")
    df.index=pd.DatetimeIndex(idx).tz_convert(None); df.columns=[c.lower() for c in df.columns]
    return df[["open","high","low","close"]].astype(float).sort_index()
def rs(df,r): return df.resample(r).agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()

D={k:load(v) for k,v in FILES.items()}

def report(tag,t,df,cut):
    s=L.stats(t,df,cut)
    if not s.get("n"): print(f"  {tag:34s} no trades"); return s
    stopn=int((t.why=="stop").sum())
    print(f"  {tag:34s} n={s['n']:4d} PF={s['pf']:.3f} net={s['net']:8.1f} WR={s['wr']:4.1f} "
          f"DD={s['maxdd']:7.1f} top10={s['top10']:6.1f}% yrs+={s['yrs_pos']}/{s['yrs']} "
          f"IS/OOS={s['is_pf']:.2f}/{s['oos_pf']:.2f} stops={stopn}")
    return s

print("### AU200 z-reversion 4H  (z=(c-SMA50)/sd50, |z|>=2.5, exit z=0, 6xATR stop)")
df=rs(D["AU200"],"4h"); a=L.atr(df); cut=df.index[int(len(df)*0.7)]
st=L.state_zrev(df.close.to_numpy(float),n=50,entry=2.5)
for m in (1.0,2.0,3.0):
    report(f"slip x{m}", L.run(df,st,a,L.COSTS['AU200']*m,0.0,stop_atr=6.0), df, cut)

print("### US30 RSI(2) daily  (RSI2<10 above SMA200 long / >90 below short, exit RSI50)")
df=rs(D["US30"],"1D"); a=L.atr(df); cut=df.index[int(len(df)*0.7)]
st=L.state_rsi(df.close.to_numpy(float),long_only=False)
for m in (1.0,2.0,3.0):
    report(f"slip x{m}", L.run(df,st,a,L.COSTS['US30']*m,0.0,stop_atr=4.0), df, cut)

print("### SYNTHETIC NULL (demeaned return-shuffle, 20 seeds) -- engine must land at PF~1.0")
def shuffle(df,seed):
    r=np.diff(np.log(df.close.to_numpy(float))); r=r-r.mean()
    rng=np.random.default_rng(seed); rng.shuffle(r)
    c=df.close.iloc[0]*np.exp(np.r_[0,np.cumsum(r)])
    sc=c/df.close.to_numpy(float)
    return pd.DataFrame({"open":df.open.to_numpy()*sc,"high":df.high.to_numpy()*sc,
                         "low":df.low.to_numpy()*sc,"close":c},index=df.index)
for name,rule,mk,sa,cost in [("AU200","4h",lambda c:L.state_zrev(c,n=50,entry=2.5),6.0,1.0),
                             ("US30","1D",lambda c:L.state_rsi(c,long_only=False),4.0,1.0)]:
    base=rs(D[name],rule); pfs=[]
    for sd in range(20):
        g=shuffle(base,sd); a=L.atr(g)
        s=L.stats(L.run(g,mk(g.close.to_numpy(float)),a,cost,0.0,stop_atr=sa))
        if s.get("n"): pfs.append(s["pf"])
    pfs=np.array(pfs)
    print(f"  {name:6s} null PF median={np.median(pfs):.3f} mean={pfs.mean():.3f} "
          f"p95={np.percentile(pfs,95):.3f} n_seeds={len(pfs)}")

print()
print("### CROSS-INSTRUMENT: the SAME RSI(2) daily rule on all three (no re-tuning)")
for name in ["US30","AU200","GOLD"]:
    df=rs(D[name],"1D"); a=L.atr(df); cut=df.index[int(len(df)*0.7)]
    st=L.state_rsi(df.close.to_numpy(float),long_only=False)
    t=L.run(df,st,a,L.COSTS[name]*2.0,L.COMM[name],stop_atr=4.0)
    s=report(f"{name} RSI2 daily slip x2", t, df, cut)
    if s.get("n"):
        print(f"     by year: {s['by_year']}")
        lo=t[t.pnl>0]; print(f"     avg win={lo.pnl.mean():.1f} avg loss={t[t.pnl<0].pnl.mean():.1f}")

print()
print("### US30 RSI(2) LONG-ONLY vs LONG+SHORT (slip x2)")
df=rs(D["US30"],"1D"); a=L.atr(df); cut=df.index[int(len(df)*0.7)]
for lo_ in (True,False):
    st=L.state_rsi(df.close.to_numpy(float),long_only=lo_)
    report(f"long_only={lo_}", L.run(df,st,a,2.0,0.0,stop_atr=4.0), df, cut)

print()
print("### US30 RSI(2) parameter neighbourhood (slip x2) -- is the peak isolated?")
for lo_,hi_ in [(5,95),(10,90),(15,85),(20,80)]:
    for man in (100,200,300):
        st=L.state_rsi(df.close.to_numpy(float),lo=lo_,hi=hi_,ma_n=man,long_only=False)
        s=L.stats(L.run(df,st,a,2.0,0.0,stop_atr=4.0),df,cut)
        if s.get("n"): print(f"  lo/hi={lo_}/{hi_} sma={man:3d}: n={s['n']:3d} PF={s['pf']:.2f} net={s['net']:8.1f} yrs+={s['yrs_pos']}/{s['yrs']}")
