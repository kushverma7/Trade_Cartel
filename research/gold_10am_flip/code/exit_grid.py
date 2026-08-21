"""Exact expectancy for every (stop, target) pair, from first passage.

MFE and MAE tell you how far a trade CAN run. They do not tell you what to set,
because they ignore order: a signal whose MFE is +40 and MAE is -20 pays nothing
if the -20 arrived first. This walks each signal's real tick path once, builds
its running extremes, and then resolves every candidate (SL, TP) pair by binary
search on those extremes -- exact, not sampled.

Three numbers come out per pair, and all three are needed:
  P(target first)   how often the trade pays
  expectancy        the only figure that decides anything, spread included
  EOD share         trades that reached neither and were closed at 23:00, whose
                    P&L is whatever the market left them at
"""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0, "code")

PTS = 1000.0
SLS = [3,4,5,6,8,10,12,15,18,20,22,25,30,35,40,50]
TPS = [3,4,5,6,8,10,12,15,18,20,22,25,30,35,40,50,60,75]
rows = pickle.load(open("data/mfe_rows.pkl","rb"))
class TK:
    t=np.load("data/tk_t.npy"); bid=np.load("data/tk_bid.npy"); ask=np.load("data/tk_ask.npy")

paths=[]
for r in rows:
    k0,j0,e,long_ = r["_k0"], r["_j0"], r["_e"], r["_long"]
    ex = TK.bid[k0:j0] if long_ else TK.ask[k0:j0]
    fav = (ex.astype(np.int64) - e) if long_ else (e - ex.astype(np.int64))
    paths.append(dict(kind=r["kind"], date=r["date"],
                      rmax=np.maximum.accumulate(fav), rmin=np.minimum.accumulate(fav),
                      fav=fav))
print(f"paths built: {len(paths)}")

def pnl_for(p, sl_i, tp_i):
    n=len(p["fav"])
    i_t=int(np.searchsorted(p["rmax"], tp_i, side="left"))
    i_s=int(np.searchsorted(-p["rmin"], sl_i, side="left"))
    i_t = i_t if i_t<n else 10**9
    i_s = i_s if i_s<n else 10**9
    if min(i_t,i_s)>=10**9:
        return int(p["fav"][-1]), "EOD"
    if i_s<=i_t:
        return int(p["fav"][i_s]), "SL"
    return int(p["fav"][i_t]), "TP"

out=[]
for sl in SLS:
    for tp in TPS:
        sl_i, tp_i = int(sl*PTS), int(tp*PTS)
        by={}
        for p in paths:
            v,w = pnl_for(p, sl_i, tp_i)
            by.setdefault(p["kind"],[]).append((v/PTS, w, p["date"]))
        for kind,vals in by.items():
            q=np.array([v for v,_,_ in vals]); ws=[w for _,w,_ in vals]
            out.append(dict(kind=kind, sl=sl, tp=tp, n=len(q), exp=q.mean(),
                            net=q.sum(), win=100*(q>0).mean(),
                            p_tp=100*np.mean([w=="TP" for w in ws]),
                            p_sl=100*np.mean([w=="SL" for w in ws]),
                            p_eod=100*np.mean([w=="EOD" for w in ws]),
                            pf=(q[q>0].sum()/max(-q[q<0].sum(),1e-9))))
G=pd.DataFrame(out)
# combined legs
comb=[]
for (sl,tp),g in G.groupby(["sl","tp"]):
    for lbl,ks in [("A_both",["A_L","A_S"]),("Flip_both",["F_L","F_S"]),
                   ("ALL",["A_L","A_S","F_L","F_S"])]:
        h=g[g.kind.isin(ks)]
        if len(h)==0: continue
        n=h.n.sum()
        comb.append(dict(kind=lbl, sl=sl, tp=tp, n=n,
                         exp=(h.exp*h.n).sum()/n, net=h.net.sum(),
                         win=(h.win*h.n).sum()/n, p_tp=(h.p_tp*h.n).sum()/n,
                         p_sl=(h.p_sl*h.n).sum()/n, p_eod=(h.p_eod*h.n).sum()/n, pf=np.nan))
G=pd.concat([G,pd.DataFrame(comb)],ignore_index=True)
G.to_csv("results/exit_grid.csv",index=False)

pd.set_option("display.width",260)
for k in ["A_L","A_S","F_L","F_S","A_both","Flip_both"]:
    g=G[G.kind==k]
    print(f"\n{'='*104}\n{k}  — expectancy in points per trade (rows SL, cols TP)\n{'='*104}")
    print(g.pivot(index="sl",columns="tp",values="exp").round(2).to_string())
    b=g.loc[g.exp.idxmax()]
    print(f"  best: SL={b.sl:g} TP={b.tp:g}  exp={b.exp:+.2f}  P(TP first)={b.p_tp:.0f}%  "
          f"P(SL first)={b.p_sl:.0f}%  P(EOD)={b.p_eod:.0f}%  n={int(b.n)}")
