"""Architecture B: separate exits per first-break direction, entry untouched."""
import sys, itertools, numpy as np, pandas as pd
sys.path.insert(0,"code")
from entry_universe import build, splits, label
from exits import resolve, stats

SLS=[5,6,8,10,12,13,14,15,16,18,20,22,25,30,35,40]
TPS=[6,8,10,12,15,18,20,22,25,27,30,32,35,40,50,60,75]

def per_kind(trades, kind):
    sub=[t for t in trades if t["kind"]==kind]
    rows=[]
    for sl,tp in itertools.product(SLS,TPS):
        recs=[(t["split"], resolve(t, sl=sl, tp=tp)[0]) for t in sub]
        d={s:[v for sp,v in recs if sp==s] for s in ("DEV","VAL","HOLD")}
        allv=[v for _,v in recs]
        A=stats(allv); S={s:stats(d[s]) for s in d}
        rows.append(dict(kind=kind, sl=sl, tp=tp, n=A["n"], pf=A["pf"], exp=A["exp"], net=A["net"],
                         mdd=A["mdd"], pf_dev=S["DEV"]["pf"], pf_val=S["VAL"]["pf"], pf_hold=S["HOLD"]["pf"],
                         n_dev=S["DEV"]["n"], n_val=S["VAL"]["n"], n_hold=S["HOLD"]["n"],
                         minPF=min(S[s]["pf"] for s in S), minEXP=min(S[s]["exp"] for s in S)))
    return pd.DataFrame(rows)

if __name__=="__main__":
    tr=build(1100,2.0); d1,d2=splits(tr); label(tr,d1,d2)
    out=pd.concat([per_kind(tr,"A_LONG"), per_kind(tr,"FLIP_SHORT")], ignore_index=True)
    out.to_csv("results/grid_split.csv", index=False)
    pd.set_option("display.width",250)
    for k in ("A_LONG","FLIP_SHORT"):
        s=out[out.kind==k]
        r=s.iloc[0]
        print(f"\n=== {k}  (n={int(r.n)}; splits {int(r.n_dev)}/{int(r.n_val)}/{int(r.n_hold)}) — top 10 by minPF ===")
        print(s.nlargest(10,"minPF")[["sl","tp","n","pf","exp","net","mdd","pf_dev","pf_val","pf_hold","minPF"]]
              .to_string(index=False,float_format=lambda v:f"{v:,.2f}"))
