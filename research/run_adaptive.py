import sys, numpy as np, pandas as pd
sys.path.insert(0, "research")
from adaptive_sim import regime, simulate, stats, TREND, REVERT

FILES = {"GOLD": "data/xauusd_15m.csv.gz", "US30": "data/us30_15m_native.csv.gz",
         "AU200": "data/au200_15m.csv.gz"}
SLIP = {"GOLD": 0.20, "US30": 1.0, "AU200": 1.0}

def load(p):
    df = pd.read_csv(p)
    tc = [c for c in df.columns if c.lower() in ("time","date","datetime","timestamp")][0]
    s = df[tc]
    idx = pd.to_datetime(s, unit="s", utc=True) if pd.api.types.is_numeric_dtype(s) \
          else pd.to_datetime(s, utc=True, format="mixed")
    df.index = pd.DatetimeIndex(idx).tz_convert(None)
    df.columns = [c.lower() for c in df.columns]
    return df[["open","high","low","close"]].astype(float).sort_index()

def rs(df, rule):
    return df.resample(rule).agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()

DATA = {k: load(v) for k, v in FILES.items()}

for tf in ["4h","1D"]:
    print("="*84); print("TIMEFRAME", tf)
    for name in FILES:
        df = rs(DATA[name], tf)
        reg, ac = regime(df.close.to_numpy(float))
        v = pd.Series(reg)[np.isfinite(ac)]
        print(f"  {name:6s} bars={len(df):5d} cov={len(v):5d}  TREND={100*(v==TREND).mean():5.1f}%"
              f"  REVERT={100*(v==REVERT).mean():5.1f}%  FLAT={100*(v==0).mean():5.1f}%"
              f"  meanAC={np.nanmean(ac):+.4f}")
    print("-"*84)
    for name in FILES:
        df = rs(DATA[name], tf)
        reg, ac = regime(df.close.to_numpy(float))
        cut = df.index[int(len(df)*0.7)]
        for mult in (1.0, 2.0):
            t = simulate(df, reg, SLIP[name]*mult)
            s = stats(t, df, cut)
            if s["n"] == 0:
                print(f"  {name:6s} x{mult}: no trades"); continue
            print(f"  {name:6s} x{mult}: n={s['n']:4d} PF={s['pf']:.3f} net={s['net']:9.1f} "
                  f"WR={s['wr']:4.1f} DD={s['maxdd']:8.1f} top10={s['top10']:6.1f}% "
                  f"yrs+={s.get('yrs_pos')}/{s.get('yrs')} IS/OOS={s.get('is_pf',np.nan):.2f}/{s.get('oos_pf',np.nan):.2f}")
            if mult == 1.0:
                bm = t.groupby("mode").pnl.agg(["count","sum"])
                print(f"           by mode: " + "  ".join(
                    f"{'TREND' if k==1 else 'REVERT'}: n={int(r['count'])} net={r['sum']:.1f}"
                    for k, r in bm.iterrows()))
