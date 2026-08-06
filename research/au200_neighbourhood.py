import sys, numpy as np, pandas as pd
sys.path.insert(0,"research"); import mean_reversion_lab as L
exec(open("research/verify_three.py").read().split("D={k:load")[0].split("import mean_reversion_lab as L")[1])
D={"AU200":load("data/au200_15m.csv.gz")}
print("AU200 z-rev neighbourhood, slip x2 -- PF (n) [IS/OOS], * = OOS PF<1")
for rule in ["4h","1D"]:
    df=rs(D["AU200"],rule); a=L.atr(df); cut=df.index[int(len(df)*0.7)]
    print(f"-- {rule}  bars={len(df)}")
    for zl in (20,50,100):
        row=[]
        for ez in (2.0,2.5,3.0):
            for sa in (4.0,6.0,8.0):
                st=L.state_zrev(df.close.to_numpy(float),n=zl,entry=ez)
                s=L.stats(L.run(df,st,a,2.0,0.0,stop_atr=sa),df,cut)
                if not s.get("n"): row.append("   --   "); continue
                bad="*" if not (s.get("oos_pf",0)>1) else " "
                row.append(f"z{zl}/{ez}/{sa:.0f}:{s['pf']:.2f}({s['n']}){bad}")
        print("   "+"  ".join(row))
