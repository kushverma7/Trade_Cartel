import sys, numpy as np, pandas as pd
sys.path.insert(0,"research"); import mean_reversion_lab as L
from cost_gated_lab import load, rs, D, SLIP

CAND=[("US30","1h",100,2.5,6.0),("AU200","1h",50,2.5,6.0)]
def st(c,zl,ez): return L.state_zrev(c,n=zl,entry=ez)

for name,tf,zl,ez,sa in CAND:
    df=rs(D[name],tf); a=L.atr(df); c=df.close.to_numpy(float); cut=df.index[int(len(df)*0.7)]
    print("="*80)
    print(f"{name} {tf}  z{zl} entry|z|>={ez} exit z=0 stop {sa}xATR   {df.index[0].date()} -> {df.index[-1].date()}")
    for m in (1.0,2.0,3.0,4.0):
        t=L.run(df,st(c,zl,ez),a,SLIP[name]*m,0.0,stop_atr=sa); s=L.stats(t,df,cut)
        print(f"  slip {m}x: n={s['n']:4d} PF={s['pf']:.3f} net={s['net']:8.1f} WR={s['wr']:4.1f} "
              f"DD={s['maxdd']:7.1f} top10={s['top10']:6.1f}% yrs+={s['yrs_pos']}/{s['yrs']} "
              f"IS/OOS={s['is_pf']:.2f}/{s['oos_pf']:.2f} (n {s['is_n']}/{s['oos_n']})")
    t=L.run(df,st(c,zl,ez),a,SLIP[name]*2,0.0,stop_atr=sa); s=L.stats(t,df,cut)
    print(f"  by year: {s['by_year']}")
    print(f"  exits: {t.why.value_counts().to_dict()}  avgwin={t[t.pnl>0].pnl.mean():.1f} avgloss={t[t.pnl<0].pnl.mean():.1f}")
    hold=t.bar.diff().median()
    print(f"  median bars between entries: {hold:.0f}  -> about {len(t)/ (len(df)/ (24 if tf=='1h' else 6) /365*12):.1f} trades/month")
    # synthetic null
    pfs=[]
    for sd in range(30):
        r=np.diff(np.log(c)); r=r-r.mean(); np.random.default_rng(sd).shuffle(r)
        g=c[0]*np.exp(np.r_[0,np.cumsum(r)]); scl=g/c
        gd=pd.DataFrame({"open":df.open.to_numpy()*scl,"high":df.high.to_numpy()*scl,
                         "low":df.low.to_numpy()*scl,"close":g},index=df.index)
        q=L.stats(L.run(gd,st(g,zl,ez),L.atr(gd),SLIP[name]*2,0.0,stop_atr=sa))
        if q.get("n"): pfs.append(q["pf"])
    pfs=np.array(pfs)
    print(f"  NULL (30 seeds): median={np.median(pfs):.3f} p95={np.percentile(pfs,95):.3f} max={pfs.max():.3f}  vs real {s['pf']:.3f}")
    # mirror
    mt=L.run(df,(-st(c,zl,ez)).astype(np.int8),a,SLIP[name]*2,0.0,stop_atr=sa)
    print(f"  MIRROR (fade the fade): PF={L.stats(mt)['pf']:.3f}")
    # neighbourhood
    print("  neighbourhood (slip 2x):", end=" ")
    for zl2 in (50,75,100,150):
        for ez2 in (2.0,2.5,3.0):
            q=L.stats(L.run(df,st(c,zl2,ez2),a,SLIP[name]*2,0.0,stop_atr=sa),df,cut)
            if q.get("n") and q["n"]>=20:
                print(f"{zl2}/{ez2}:{q['pf']:.2f}", end="  ")
    print()
