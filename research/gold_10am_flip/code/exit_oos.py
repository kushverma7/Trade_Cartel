"""Does the chosen (SL, TP) survive a split it did not see?

The grid optimum sits at the TP edge with a 9% target-hit rate, which means the
target is not doing the work -- the end-of-day close is. A recommendation has to
be checked on a holdout, and it has to be checked for whether the TP is actually
earning its place.
"""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,"code")
PTS=1000.0
SPLIT=pd.Timestamp("2026-04-30")
rows=pickle.load(open("data/mfe_rows.pkl","rb"))
class TK:
    t=np.load("data/tk_t.npy"); bid=np.load("data/tk_bid.npy"); ask=np.load("data/tk_ask.npy")
paths=[]
for r in rows:
    k0,j0,e,long_=r["_k0"],r["_j0"],r["_e"],r["_long"]
    ex=TK.bid[k0:j0] if long_ else TK.ask[k0:j0]
    fav=(ex.astype(np.int64)-e) if long_ else (e-ex.astype(np.int64))
    paths.append(dict(kind=r["kind"],date=pd.Timestamp(r["date"]),
                      rmax=np.maximum.accumulate(fav),rmin=np.minimum.accumulate(fav),fav=fav))

def res(p,sl_i,tp_i):
    n=len(p["fav"])
    i_t=int(np.searchsorted(p["rmax"],tp_i,side="left")); i_t=i_t if i_t<n else 10**9
    i_s=int(np.searchsorted(-p["rmin"],sl_i,side="left")); i_s=i_s if i_s<n else 10**9
    if min(i_t,i_s)>=10**9: return int(p["fav"][-1]),"EOD"
    return (int(p["fav"][i_s]),"SL") if i_s<=i_t else (int(p["fav"][i_t]),"TP")

def ev(ks,sl,tp):
    sl_i,tp_i=int(sl*PTS),int(tp*PTS)
    tr,te=[],[]
    for p in paths:
        if p["kind"] not in ks: continue
        v,w=res(p,sl_i,tp_i)
        (tr if p["date"]<=SPLIT else te).append((v/PTS,w))
    def st(a):
        if not a: return dict(n=0,exp=np.nan,ptp=np.nan,pf=np.nan)
        q=np.array([x for x,_ in a]); ws=[w for _,w in a]
        return dict(n=len(q),exp=q.mean(),ptp=100*np.mean([w=="TP" for w in ws]),
                    pf=q[q>0].sum()/max(-q[q<0].sum(),1e-9))
    return st(tr),st(te)

CAND=[("A_both",["A_L","A_S"],[(10,20),(12,22),(12,25),(15,20),(15,25),(15,30),(15,75),(18,25),(40,25),(8,25)]),
      ("A_long",["A_L"],       [(10,20),(12,25),(15,25),(15,30),(18,25),(20,30)]),
      ("Flip_both",["F_L","F_S"],[(6,30),(6,40),(18,40),(20,50),(20,60),(15,30)]),
      ("ALL",["A_L","A_S","F_L","F_S"],[(12,25),(15,25),(15,30),(6,30),(18,40)])]
print(f"{'set':<11}{'SL':>4}{'TP':>4} | {'TRAIN n':>8}{'exp':>8}{'P(TP)':>7}{'PF':>6} | {'TEST n':>7}{'exp':>8}{'P(TP)':>7}{'PF':>6} | verdict")
print("-"*104)
for name,ks,cands in CAND:
    for sl,tp in cands:
        a,b=ev(ks,sl,tp)
        ok = (a["exp"]>0 and b["exp"]>0)
        v = "both halves +" if ok else ("TEST NEGATIVE" if b["exp"]<=0 else "train negative")
        print(f"{name:<11}{sl:>4g}{tp:>4g} | {a['n']:>8}{a['exp']:>8.2f}{a['ptp']:>7.0f}{a['pf']:>6.2f} | "
              f"{b['n']:>7}{b['exp']:>8.2f}{b['ptp']:>7.0f}{b['pf']:>6.2f} | {v}")
