"""
OVERNIGHT (close->open) vs INTRADAY (open->close), measured off real session breaks.

Session boundaries are detected from the data itself: any jump in the timestamp
larger than the modal bar interval is a real market break, not an assumption.
"""
import numpy as np, pandas as pd
FILES={"GOLD":"data/xauusd_15m.csv.gz","US30":"data/us30_15m_native.csv.gz","AU200":"data/au200_15m.csv.gz"}
def load(p):
    df=pd.read_csv(p)
    tc=[c for c in df.columns if c.lower() in ("time","date","datetime","timestamp")][0]
    s=df[tc]
    idx=pd.to_datetime(s,unit="s",utc=True) if pd.api.types.is_numeric_dtype(s) else pd.to_datetime(s,utc=True,format="mixed")
    df.index=pd.DatetimeIndex(idx).tz_convert(None); df.columns=[c.lower() for c in df.columns]
    return df[["open","high","low","close"]].astype(float).sort_index()

for name,p in FILES.items():
    df=load(p); t=df.index
    step=pd.Series(t).diff().mode()[0]
    brk=pd.Series(t).diff() > step          # a real session break
    brk.iloc[0]=True
    sess=brk.cumsum().to_numpy()
    g=df.groupby(sess).agg(o=("open","first"),c=("close","last"),
                           h=("high","max"),l=("low","min"))
    g["t"]=df.groupby(sess).apply(lambda x:x.index[0])
    g=g[g.index.isin(g.index)]
    overnight=(g.o - g.c.shift(1)).dropna()          # close -> next open
    intraday =(g.c - g.o)                            # open -> close
    n=min(len(overnight),len(intraday))
    tot=overnight.sum()+intraday.sum()
    print("="*76)
    print(f"{name}: {len(g)} sessions, modal bar {step}, total drift {tot:,.0f} pts")
    for lbl,v in [("OVERNIGHT close->open",overnight),("INTRADAY  open->close",intraday)]:
        wr=100*(v>0).mean()
        print(f"  {lbl}: sum={v.sum():9,.0f} ({100*v.sum()/tot:6.1f}%)  mean={v.mean():+7.3f}  "
              f"median={v.median():+7.3f}  WR={wr:4.1f}%  sd={v.std():.2f}  n={len(v)}")
    # what a naive always-on overnight book earns per unit of risk
    v=overnight
    print(f"  overnight Sharpe-ish (mean/sd) = {v.mean()/v.std():+.4f}   "
          f"t-stat = {v.mean()/(v.std()/np.sqrt(len(v))):+.2f}")
    v=intraday
    print(f"  intraday  Sharpe-ish (mean/sd) = {v.mean()/v.std():+.4f}   "
          f"t-stat = {v.mean()/(v.std()/np.sqrt(len(v))):+.2f}")
