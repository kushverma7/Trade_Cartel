"""
WHERE DOES THE RETURN ACTUALLY LIVE?

Pure measurement, no trading rules. Every failed family this session paid ~1pt
of cost to capture a ~1pt intraday move. Rather than hunt for a better intraday
signal, ask a prior question: across the clock, WHICH hours carry the drift?

If a large share of total return accrues in a window you can enter and exit ONCE,
the cost-to-risk ratio collapses -- the same 1pt spread now sits against a much
larger move. That is a structural fix, not a better signal.
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
    df=load(p)
    r=df.close.diff()                      # POINTS, the unit costs are paid in
    g=r.groupby(df.index.hour).agg(["sum","mean","count"])
    tot=r.sum()
    print("="*72)
    print(f"{name}  {df.index[0].date()} -> {df.index[-1].date()}  total drift {tot:,.0f} pts (UTC hours)")
    print("  hr    sum_pts   share%   mean_pts/bar    n")
    for h,row in g.iterrows():
        sh=100*row["sum"]/tot if tot else np.nan
        bar="#"*int(abs(sh)/3) if np.isfinite(sh) else ""
        print(f"  {h:02d}  {row['sum']:9.0f}  {sh:7.1f}  {row['mean']:+10.4f}  {int(row['count']):5d}  {bar}")
