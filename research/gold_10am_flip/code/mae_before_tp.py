"""The stop question, asked in a way that can actually answer it.

The proposal justifies SL 13.5 like this: with SL 13.5 / TP 26 applied, A-Long
winners went on average only 5.96 points against first, and the worst winner
reached about 13. That last figure cannot be evidence. With a 13.5-point stop
in force, any trade that went further than 13.5 against was stopped out and is
not a winner -- so "no winner exceeded ~13" is guaranteed by the stop, whatever
the market did. Conditioning on survival and then measuring survival is circular.

The non-circular version: take every signal that EVER reaches the target with no
stop applied at all, and ask how far it went against BEFORE getting there. That
distribution is a property of the market, not of the chosen stop, and it says
directly what a stop has to tolerate. The gap between the two framings is the
share of genuine winners a stop throws away.
"""
import sys, pickle, numpy as np, pandas as pd
sys.path.insert(0,"code")
PTS=1000.0
rows=pickle.load(open("data/mfe_rows.pkl","rb"))
class TK:
    t=np.load("data/tk_t.npy"); bid=np.load("data/tk_bid.npy"); ask=np.load("data/tk_ask.npy")
paths=[]
for r in rows:
    k0,j0,e,long_=r["_k0"],r["_j0"],r["_e"],r["_long"]
    if k0>=j0: continue
    ex=TK.bid[k0:j0] if long_ else TK.ask[k0:j0]
    fav=(ex.astype(np.int64)-e) if long_ else (e-ex.astype(np.int64))
    paths.append(dict(kind=r["kind"],date=pd.Timestamp(r["date"]),fav=fav,
                      rmax=np.maximum.accumulate(fav),rmin=np.minimum.accumulate(fav)))

def mae_before_tp(ks, tp):
    """For signals that EVER reach tp (no stop), the worst excursion first."""
    tp_i=int(tp*PTS); out=[]
    for p in paths:
        if p["kind"] not in ks: continue
        n=len(p["fav"]); i_t=int(np.searchsorted(p["rmax"],tp_i,side="left"))
        if i_t>=n: continue                      # never reached the target
        out.append(-int(p["rmin"][i_t])/PTS)     # deepest adverse up to that point
    return np.array(out)

for lbl,ks,tp,claimed_sl in [("A_LONG",["A_L"],26,13.5), ("FLIP_LONG",["F_L"],31,5.5),
                             ("A_SHORT",["A_S"],26,13.5), ("FLIP_SHORT",["F_S"],20,7.5)]:
    m=mae_before_tp(ks,tp)
    tot=sum(1 for p in paths if p["kind"] in ks)
    print(f"\n{'='*96}\n{lbl}: signals that EVER reach +{tp} with no stop = {len(m)} of {tot} ({100*len(m)/tot:.0f}%)")
    print(f"  adverse excursion BEFORE getting there (points):")
    print(f"    mean {m.mean():6.2f}  median {np.median(m):6.2f}  p75 {np.percentile(m,75):6.2f}  "
          f"p80 {np.percentile(m,80):6.2f}  p90 {np.percentile(m,90):6.2f}  p95 {np.percentile(m,95):6.2f}  max {m.max():7.2f}")
    for sl in sorted({5.5,6,7.5,8,10,12,13.5,15,18,20,25,30}):
        kept=(m<=sl).mean()
        print(f"    SL {sl:>5g} keeps {100*kept:5.1f}% of eventual winners, discards {100*(1-kept):5.1f}%"
              + ("   <-- proposed" if abs(sl-claimed_sl)<1e-9 else ""))
