"""Independently reproduce the proposed per-leg settings.

Two things are being checked. First, whether the headline numbers reproduce on
this dataset at all. Second, and more importantly, whether the evidence offered
FOR the stop distance actually supports it.

Entry convention is tested both ways, because the proposal enters on the first
executable tick AFTER the signal candle closes while the original Pine (with
process_orders_on_close=true) fills at the closing quote of the signal candle
itself. Those are one tick apart and should differ only slightly -- if they
differ a lot, that is itself the finding.
"""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "code")
PTS = 1000.0
rows = pickle.load(open("data/mfe_rows.pkl", "rb"))
class TK:
    t=np.load("data/tk_t.npy"); bid=np.load("data/tk_bid.npy"); ask=np.load("data/tk_ask.npy")

def build(entry_mode):
    out=[]
    for r in rows:
        k0,j0,long_ = r["_k0"], r["_j0"], r["_long"]
        if k0>=j0: continue
        if entry_mode=="bar_close_quote":
            e = r["_e"]                      # last quote inside the signal bar
            s = k0
        else:                                # first executable tick AFTER the bar
            e = int(TK.ask[k0] if long_ else TK.bid[k0])
            s = k0+1
            if s>=j0: continue
        ex = TK.bid[s:j0] if long_ else TK.ask[s:j0]
        fav = (ex.astype(np.int64)-e) if long_ else (e-ex.astype(np.int64))
        out.append(dict(kind=r["kind"], date=pd.Timestamp(r["date"]), fav=fav,
                        rmax=np.maximum.accumulate(fav), rmin=np.minimum.accumulate(fav)))
    return out

def res(p, sl_i, tp_i):
    n=len(p["fav"])
    i_t=int(np.searchsorted(p["rmax"],tp_i,side="left")); i_t=i_t if i_t<n else 10**9
    i_s=int(np.searchsorted(-p["rmin"],sl_i,side="left")); i_s=i_s if i_s<n else 10**9
    if min(i_t,i_s)>=10**9: return int(p["fav"][-1]),"EOD"
    return (int(p["fav"][i_s]),"SL") if i_s<=i_t else (int(p["fav"][i_t]),"TP")

def evaluate(paths, ks, sl, tp):
    sl_i,tp_i=int(sl*PTS),int(tp*PTS)
    d=[(p["date"],)+res(p,sl_i,tp_i) for p in paths if p["kind"] in ks]
    d.sort(key=lambda x:x[0])
    q=np.array([x[1]/PTS for x in d]); why=[x[2] for x in d]
    dates=[x[0] for x in d]
    eq=np.cumsum(q); pk=np.maximum.accumulate(np.concatenate([[0.0],eq]))[1:]
    mdd=float((pk-eq).max()) if len(q) else 0.0
    gp,gl=q[q>0].sum(), -q[q<0].sum()
    # chronological thirds
    n=len(q); a,b=n//3, 2*n//3
    seg=[q[:a].mean() if a else np.nan, q[a:b].mean() if b>a else np.nan, q[b:].mean() if n>b else np.nan]
    mon=pd.Series(q, index=pd.to_datetime(dates)).groupby(pd.to_datetime(dates).to_period("M")).sum()
    return dict(n=n, net=q.sum(), exp=q.mean(), pf=gp/max(gl,1e-9), mdd=mdd,
                green=f"{int((mon>0).sum())}/{len(mon)}", seg=seg,
                ptp=100*np.mean([w=="TP" for w in why]))

CLAIMS=[("A Long",["A_L"],13.5,26),("A Long",["A_L"],14,26),
        ("A Short",["A_S"],13.5,26),
        ("Flip Long",["F_L"],5.5,31),("Flip Long",["F_L"],6,30),
        ("Flip Short",["F_S"],7.5,20),
        ("Flip both",["F_L","F_S"],6,29.5),
        ("ALL four",["A_L","A_S","F_L","F_S"],13.5,29.5)]
for mode in ["next_tick","bar_close_quote"]:
    paths=build(mode)
    print(f"\n{'='*112}\nENTRY = {mode}   ({len(paths)} signals)\n{'='*112}")
    print(f"{'leg':<11}{'SL':>6}{'TP':>5}{'n':>5}{'net':>9}{'exp':>8}{'PF':>6}{'maxDD':>8}{'green':>7}{'P(TP)':>7}   dev/val/holdout")
    for name,ks,sl,tp in CLAIMS:
        r=evaluate(paths,ks,sl,tp)
        s=r["seg"]
        print(f"{name:<11}{sl:>6g}{tp:>5g}{r['n']:>5}{r['net']:>9.1f}{r['exp']:>8.2f}{r['pf']:>6.2f}"
              f"{r['mdd']:>8.1f}{r['green']:>7}{r['ptp']:>7.0f}   {s[0]:+.2f} / {s[1]:+.2f} / {s[2]:+.2f}")
