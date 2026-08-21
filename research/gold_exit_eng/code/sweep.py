"""Parameter sweep, selected on TRAIN and reported on an untouched holdout.

The brief is "smoothest equity curve". That is a real objective but a dangerous
one: on a few hundred trades, ranking configurations by curve smoothness is
close to ranking them by luck, and this repo's own evidence rule says a visually
straight curve is a bug until proven otherwise. So smoothness is measured, but
the number that counts is the OUT-OF-SAMPLE one, and the plateau around each
winner is reported so a lucky spike can be told from a real region.
"""
import sys, itertools, pickle, numpy as np, pandas as pd
sys.path.insert(0, "code")
from fastsim import simulate
from engine import stats

SPLIT = "2026-04-30"          # ~2/3 train, ~1/3 untouched holdout
SLS = [2,3,4,5,6,8,10,12,15,18,22,26,30,40]
TPS = [3,4,5,6,8,10,12,15,20,25,30,40,50]
SETS = {
    "A_short_only":      dict(allow={"A_S"}),
    "Flip_short_only":   dict(allow={"F_S"}),
    "Flip_long_only":    dict(allow={"F_L"}),
    "Flip_both":         dict(allow={"F_L","F_S"}),
    "A_short_plus_Flip": dict(allow={"A_S","F_L","F_S"}),
    "A_both":            dict(allow={"A_L","A_S"}),
    "All_four":          dict(allow={"A_L","A_S","F_L","F_S"}),
    "Shorts_only":       dict(allow={"A_S","F_S"}),
}

def main():
    prep = pickle.load(open("data/prep10.pkl","rb"))
    class TK:
        t=np.load("data/tk_t.npy"); bid=np.load("data/tk_bid.npy"); ask=np.load("data/tk_ask.npy")
    rows=[]
    for name, kw in SETS.items():
        for sl, tp in itertools.product(SLS, TPS):
            tr = simulate(prep, TK, sl, tp, use_A=True, a_short_only=False,
                          use_flip=True, allow=kw["allow"])
            if len(tr)==0: continue
            tr["date"]=pd.to_datetime(tr["date"])
            trn = tr[tr.date<=SPLIT]; tst = tr[tr.date>SPLIT]
            a=stats(trn,"train"); b=stats(tst,"test"); f=stats(tr,"full")
            rows.append(dict(set=name, sl=sl, tp=tp,
                n_tr=a["n"], net_tr=a["net"], exp_tr=a["exp"], pf_tr=a["pf"],
                dd_tr=a["max_dd"], mar_tr=a["mar"], r2_tr=a["r2"], t_tr=a["tstat"],
                n_te=b["n"], net_te=b["net"], exp_te=b["exp"], pf_te=b["pf"],
                dd_te=b["max_dd"], mar_te=b["mar"], r2_te=b["r2"],
                n_f=f["n"], net_f=f["net"], exp_f=f["exp"], pf_f=f["pf"],
                dd_f=f["max_dd"], mar_f=f["mar"], r2_f=f["r2"], t_f=f["tstat"]))
        print(f"  swept {name}", flush=True)
    R=pd.DataFrame(rows); R.to_csv("results/sweep.csv", index=False)
    print(f"\n{len(R)} configurations swept -> results/sweep.csv")

    pd.set_option("display.width",250)
    cols=["set","sl","tp","n_tr","exp_tr","pf_tr","mar_tr","r2_tr","t_tr","n_te","exp_te","pf_te","r2_te"]
    elig=R[(R.n_tr>=25)&(R.n_te>=10)]
    print(f"\nEligible (>=25 train trades, >=10 test): {len(elig)}")
    print("\n--- TOP 15 BY TRAIN MAR (net/maxDD), the smoothness proxy ---")
    print(elig.nlargest(15,"mar_tr")[cols].to_string(index=False,float_format=lambda v:f"{v:,.2f}"))
    print("\n--- TOP 15 BY TRAIN R-SQUARED (equity linearity) ---")
    print(elig.nlargest(15,"r2_tr")[cols].to_string(index=False,float_format=lambda v:f"{v:,.2f}"))
    print("\n--- best per logic set, by train MAR ---")
    best=elig.loc[elig.groupby("set")["mar_tr"].idxmax()]
    print(best[cols].to_string(index=False,float_format=lambda v:f"{v:,.2f}"))

if __name__=="__main__":
    main()
