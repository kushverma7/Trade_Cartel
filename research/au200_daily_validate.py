import sys, numpy as np, pandas as pd
sys.path.insert(0,"research"); import mean_reversion_lab as L
exec(open("research/verify_three.py").read().split("D={k:load")[0].split("import mean_reversion_lab as L")[1])
df=rs(load("data/au200_15m.csv.gz"),"1D"); a=L.atr(df); cut=df.index[int(len(df)*0.7)]
c=df.close.to_numpy(float)
print("AU200 DAILY z-rev: z=(c-SMA20)/sd20, |z|>=2.0, exit z=0, 6xATR stop")
print("range",df.index[0].date(),"->",df.index[-1].date(),"bars",len(df),"| IS/OOS cut",cut.date())
for m in (1.0,2.0,3.0,4.0):
    st=L.state_zrev(c,n=20,entry=2.0)
    t=L.run(df,st,a,1.0*m,0.0,stop_atr=6.0); s=L.stats(t,df,cut)
    print(f"  slip x{m}: n={s['n']:3d} PF={s['pf']:.3f} net={s['net']:8.1f} WR={s['wr']:4.1f} "
          f"DD={s['maxdd']:7.1f} top10={s['top10']:5.1f}% yrs+={s['yrs_pos']}/{s['yrs']} "
          f"IS/OOS={s['is_pf']:.2f}/{s['oos_pf']:.2f} (n {s['is_n']}/{s['oos_n']})")
    if m==2.0:
        print(f"    by year: {s['by_year']}")
        print(f"    longs n={int((t.pnl.index.size and (L.run(df,st,a,2.0,0.0,stop_atr=6.0) is not None)) and 0)}", end="")
        print()
st=L.state_zrev(c,n=20,entry=2.0); t=L.run(df,st,a,2.0,0.0,stop_atr=6.0)
print(f"    exits: {t.why.value_counts().to_dict()}  avgwin={t[t.pnl>0].pnl.mean():.1f} avgloss={t[t.pnl<0].pnl.mean():.1f}")

print("  synthetic null (demeaned shuffle, 30 seeds):")
pfs=[]
for sd in range(30):
    r=np.diff(np.log(c)); r=r-r.mean(); np.random.default_rng(sd).shuffle(r)
    g=df.close.iloc[0]*np.exp(np.r_[0,np.cumsum(r)]); scl=g/c
    gd=pd.DataFrame({"open":df.open.to_numpy()*scl,"high":df.high.to_numpy()*scl,
                     "low":df.low.to_numpy()*scl,"close":g},index=df.index)
    s=L.stats(L.run(gd,L.state_zrev(g,n=20,entry=2.0),L.atr(gd),2.0,0.0,stop_atr=6.0))
    if s.get("n"): pfs.append(s["pf"])
pfs=np.array(pfs)
print(f"    null PF median={np.median(pfs):.3f} p95={np.percentile(pfs,95):.3f} max={pfs.max():.3f}  vs real 2.31")
