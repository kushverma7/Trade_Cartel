"""
COST-GATED REVERSION.

DIAGNOSIS. Twenty-plus intraday families died the same way: entries were gated
in statistical units (z-score, RSI) which say nothing about whether the expected
move exceeds the spread. On a quiet 15m bar a z of 2.5 might be 3 points; the
round trip costs 2. The edge is real and the cost eats it.

FIX. Gate on POINTS, not sigma. Require the extension that triggers the entry to
be at least K times the round-trip cost. The signal is unchanged; the filter is
purely economic. If the cost-to-risk diagnosis is right this should turn losing
intraday families profitable at the SAME parameters, and the improvement should
grow monotonically with K -- a mechanism, not a fitted cell.
"""
import numpy as np, pandas as pd, sys
sys.path.insert(0,"research"); import mean_reversion_lab as L

FILES={"GOLD":"data/xauusd_15m.csv.gz","US30":"data/us30_15m_native.csv.gz","AU200":"data/au200_15m.csv.gz"}
SLIP={"GOLD":0.20,"US30":1.0,"AU200":1.0}
def load(p):
    df=pd.read_csv(p)
    tc=[c for c in df.columns if c.lower() in ("time","date","datetime","timestamp")][0]
    s=df[tc]
    idx=pd.to_datetime(s,unit="s",utc=True) if pd.api.types.is_numeric_dtype(s) else pd.to_datetime(s,utc=True,format="mixed")
    df.index=pd.DatetimeIndex(idx).tz_convert(None); df.columns=[c.lower() for c in df.columns]
    return df[["open","high","low","close"]].astype(float).sort_index()
def rs(df,r): return df.resample(r).agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()

def state_gated(c, zl, ez, min_pts):
    """Same fade rule, plus: the extension must be >= min_pts in POINTS."""
    s=pd.Series(c); m=s.rolling(zl).mean(); sd=s.rolling(zl).std(ddof=0)
    z=((s-m)/sd).to_numpy(); dist=(s-m).abs().to_numpy()
    d=np.zeros(len(c),np.int8); cur=0
    for i in range(len(c)):
        if not np.isfinite(z[i]): d[i]=0; cur=0; continue
        if cur==0:
            if dist[i] >= min_pts:
                if z[i]<=-ez: cur=1
                elif z[i]>=ez: cur=-1
        elif (cur>0 and z[i]>=0) or (cur<0 and z[i]<=0): cur=0
        d[i]=cur
    return d

D={k:load(v) for k,v in FILES.items()}
print("Cost gate K = required extension in POINTS as a multiple of the ROUND-TRIP cost.")
print("K=0 is the ungated control -- the family as previously tested and rejected.\n")
for name in ["AU200","US30","GOLD"]:
    rt=2*SLIP[name]                      # round-trip cost in points
    for tf in ["1h","4h"]:
        df=rs(D[name],tf); a=L.atr(df); c=df.close.to_numpy(float)
        cut=df.index[int(len(df)*0.7)]
        print(f"-- {name} {tf}  (round-trip cost {rt} pts, {len(df)} bars)")
        for K in (0,2,4,8,16,32):
            row=[]
            for zl,ez in [(50,2.0),(50,2.5),(100,2.0),(100,2.5)]:
                st=state_gated(c,zl,ez,K*rt)
                s=L.stats(L.run(df,st,a,SLIP[name],0.0,stop_atr=6.0),df,cut)
                if not s.get("n") or s["n"]<15: row.append(f"z{zl}/{ez}:  n<15  "); continue
                row.append(f"z{zl}/{ez}:PF{s['pf']:.2f}(n{s['n']},{s['yrs_pos']}/{s['yrs']}y,OOS{s.get('oos_pf',np.nan):.2f})")
            print(f"   K={K:2d} (>={K*rt:5.1f}pt)  " + "  ".join(row))
        print()
