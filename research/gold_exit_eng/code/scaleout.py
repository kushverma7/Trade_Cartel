"""TP1 partial exit, then trail the runner to TP2. Simulated on real ticks.

Mechanics, per trade (P&L quoted per 1 unit of the FULL original position):

  phase 1  from entry, whichever comes first on the tick stream:
             fav <= -SL      -> full stop, P&L = -SL
             fav >= TP1      -> bank `frac` of the position at TP1, go to phase 2
             neither         -> flat at the close
  phase 2  the runner, from the tick TP1 was hit:
             stop becomes max(be_floor, peak - trail), where peak is the running
             maximum since entry, so it ratchets up and never falls back
             exits on that stop, on TP2, or at the close

Everything is resolved on actual quotes in arrival order -- the trail ratchet is
path-dependent and cannot be shortcut, but the exit test is still vectorised:
the trailing stop is breached exactly when the drawdown from the running peak
first reaches `trail`.

The grid deliberately holds SL and TP1 FIXED at the values already chosen. Only
frac, trail and TP2 are searched. Adding a scale-out adds three more free
parameters to a strategy whose entry already fails its permutation null, so the
search is kept as narrow as the question allows.
"""
import sys, pickle, itertools, numpy as np, pandas as pd
sys.path.insert(0, "code")
PTS = 1000.0
rows = pickle.load(open("data/mfe_rows.pkl", "rb"))
class TK:
    t=np.load("data/tk_t.npy"); bid=np.load("data/tk_bid.npy"); ask=np.load("data/tk_ask.npy")
P=[]
for r in rows:
    k0,j0,e,long_=r["_k0"],r["_j0"],r["_e"],r["_long"]
    if k0>=j0: continue
    ex=TK.bid[k0:j0] if long_ else TK.ask[k0:j0]
    fav=(ex.astype(np.int64)-e) if long_ else (e-ex.astype(np.int64))
    P.append(dict(kind=r["kind"],date=pd.Timestamp(r["date"]),fav=fav,
                  rmax=np.maximum.accumulate(fav),rmin=np.minimum.accumulate(fav)))

def trade(p, sl_i, tp1_i, frac, trail_i, tp2_i, be_i):
    fav=p["fav"]; n=len(fav)
    i_s=int(np.searchsorted(-p["rmin"], sl_i, side="left")); i_s=i_s if i_s<n else 10**9
    i_1=int(np.searchsorted(p["rmax"], tp1_i, side="left")); i_1=i_1 if i_1<n else 10**9
    if min(i_s,i_1)>=10**9:
        return int(fav[-1]), "EOD_flat"
    if i_s <= i_1:
        return -sl_i, "SL"
    g = fav[i_1:]
    if len(g)<=1:
        return int(frac*tp1_i + (1-frac)*g[-1]), "TP1_close"
    rg = np.maximum.accumulate(g)
    hit_tp2  = rg >= tp2_i
    hit_trail= (rg - g) >= trail_i
    hit_be   = g <= be_i
    cond = hit_tp2 | hit_trail | hit_be
    if cond.any():
        k=int(cond.argmax())
        run = tp2_i if (hit_tp2[k] and not (hit_trail[k] or hit_be[k])) else int(g[k])
        why = "TP2" if hit_tp2[k] else ("BE" if hit_be[k] else "TRAIL")
    else:
        run, why = int(g[-1]), "EOD_run"
    return int(frac*tp1_i + (1-frac)*run), why

def evaluate(ks, sl, tp1, frac, trail, tp2, be, split):
    a=[int(sl*PTS),int(tp1*PTS),int(trail*PTS),int(tp2*PTS),int(be*PTS)]
    d=[]
    for p in P:
        if p["kind"] not in ks: continue
        v,w=trade(p,a[0],a[1],frac,a[2],a[3],a[4])
        d.append((p["date"], v/PTS, w))
    d.sort(key=lambda x:x[0])
    q=np.array([x[1] for x in d]); dt=[x[0] for x in d]
    tr=np.array([x[1] for x in d if x[0]<=split]); te=np.array([x[1] for x in d if x[0]>split])
    eq=np.cumsum(q); pk=np.maximum.accumulate(np.concatenate([[0.0],eq]))[1:]
    mdd=float((pk-eq).max()) if len(q) else 0.0
    gp,gl=q[q>0].sum(), -q[q<0].sum()
    mon=pd.Series(q,index=pd.to_datetime(dt)).groupby(pd.to_datetime(dt).to_period("M")).sum()
    return dict(n=len(q), net=q.sum(), exp=q.mean(), pf=gp/max(gl,1e-9), mdd=mdd,
                mar=q.sum()/mdd if mdd>0 else np.inf, green=int((mon>0).sum()), months=len(mon),
                tr=tr.mean() if len(tr) else np.nan, te=te.mean() if len(te) else np.nan,
                whys=pd.Series([x[2] for x in d]).value_counts().to_dict())

SPLIT=pd.Timestamp("2026-04-30")
for name, ks, SL, TP1 in [("A_LONG",["A_L"],14,26), ("FLIP_LONG",["F_L"],6,30)]:
    base=evaluate(ks,SL,TP1,1.0,10**6,10**6,-10**6,SPLIT)   # frac=1 -> plain TP1, no runner
    print(f"\n{'='*118}\n{name}   SL {SL} / TP1 {TP1}   BASELINE (flat take-profit, no scale-out)")
    print(f"  n={base['n']}  net {base['net']:+.1f}  exp {base['exp']:+.2f}  PF {base['pf']:.2f}  "
          f"maxDD {base['mdd']:.1f}  MAR {base['mar']:.2f}  green {base['green']}/{base['months']}  "
          f"train {base['tr']:+.2f} / holdout {base['te']:+.2f}")
    print(f"{'='*118}")
    print(f"{'frac':>5}{'trail':>7}{'TP2':>6} | {'n':>4}{'net':>9}{'exp':>8}{'PF':>6}{'maxDD':>8}{'MAR':>7}{'green':>7} | {'train':>7}{'hold':>7} | exits")
    out=[]
    for frac,trail,tp2 in itertools.product([0.25,0.5,0.75],[5,8,10,15,20],[50,60,75,100]):
        r=evaluate(ks,SL,TP1,frac,trail,tp2,0.0,SPLIT)
        out.append((frac,trail,tp2,r))
    out.sort(key=lambda x:-x[3]["mar"])
    for frac,trail,tp2,r in out[:10]:
        w=r["whys"]; ws=" ".join(f"{k}:{v}" for k,v in sorted(w.items(), key=lambda x:-x[1])[:4])
        print(f"{frac:>5.2f}{trail:>7g}{tp2:>6g} | {r['n']:>4}{r['net']:>9.1f}{r['exp']:>8.2f}{r['pf']:>6.2f}"
              f"{r['mdd']:>8.1f}{r['mar']:>7.2f}{r['green']:>4}/{r['months']:<2} | {r['tr']:>+7.2f}{r['te']:>+7.2f} | {ws}")
