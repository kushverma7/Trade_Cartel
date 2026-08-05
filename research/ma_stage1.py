import numpy as np, pandas as pd, time
from research.au200_lab import load
from research.au200_ma import *

d15=load("data/au200_15m.csv.gz"); d5=load("data/au200_5m.csv.gz")
a5=atr(d5,14)
print("="*112)
print("DATA & COST CONFIRMATION — parity with the AU200-BASE run")
print("="*112)
print(f"  signals   data/au200_15m.csv.gz  {len(d15):,} bars  {d15.index[0]} -> {d15.index[-1]}")
print(f"  exit path data/au200_5m.csv.gz   {len(d5):,} bars   (same span, Australia/Sydney)")
print(f"  commission {COMM} AUD/contract/side | slippage swept {SLIPS} pt/side")
print(f"  path      stops & trails walked on 5m; cross is a 15m close event")
print(f"  mintick   0.1 (native 15m) | no sub-point trails used\n")

t0=time.time(); rows=[]
# ---- 1. dual MA cross, EMA and SMA, both-sides and long-only, exit A (cross only)
for mt in ("SMA","EMA"):
    for f,s in PAIRS:
        for lo in (False,True):
            st=cross_state(d15,f,s,mt,long_only=lo)
            r=stat(run(st,d5,slip=1.0),f"1 {mt}{f}/{s} {'long' if lo else 'both'} | A cross-only")
            r.update(family="dual-cross",matype=mt,fast=f,slow=s,longonly=lo)
            rows.append(r)
t=pd.DataFrame(rows)
pd.set_option("display.width",250)
cols=["arm","n","wr","pf","net","maxdd","top10"]
print("="*112); print("STEP 1 — DUAL MA CROSS, exit = opposite cross only, 1.0 pt/side"); print("="*112)
print(t.sort_values("pf",ascending=False)[cols].to_string(index=False,float_format=lambda v:f"{v:9.3f}"))
t.to_csv("research/au200_ma_step1.csv",index=False)
print(f"\n  SMA mean PF {t[t.matype=='SMA'].pf.mean():.3f} | EMA mean PF {t[t.matype=='EMA'].pf.mean():.3f}")
print(f"  elapsed {time.time()-t0:.0f}s")
