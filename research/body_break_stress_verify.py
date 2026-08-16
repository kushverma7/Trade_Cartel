import sys, math, statistics as st; sys.path.insert(0,'research')
from body_break_stress import *

BASE=dict(cost=2.0,end_hour=16,stop="daily_open",exit_="trail_half")
cands={
 "BASELINE":                 dict(BASE),
 "after 10:15":              {**BASE,"entry_after":615},
 "after 10:30":              {**BASE,"entry_after":630},
 "partial 1R + trail_half":  {**BASE,"partial":True},
}

print("A. WHERE DOES THE STOP ACTUALLY SIT? (baseline)")
tr=backtest(**BASE)
losses=sorted(x[2] for x in tr if x[2]<0)
wins=sorted((x[2] for x in tr if x[2]>0),reverse=True)
print(f"   worst 8 losses: {[round(v,1) for v in losses[:8]]}")
print(f"   best  8 wins  : {[round(v,1) for v in wins[:8]]}")
print(f"   mean loss {st.mean(losses):+.2f}   mean win {st.mean(wins):+.2f}   "
      f"median |loss| {abs(st.median(losses)):.2f}")
print(f"   nominal stop distance (entry->daily_open): median {st.median([x[3] for x in tr]):.1f} pts")
print("   -> the trailing stop tightens on the first bar, so the daily-open stop is")
print("      almost never the binding exit. Losses are capped near half the body.")

print("\nB. IN-SAMPLE / OUT-OF-SAMPLE (split at the midpoint of each series)")
for name,cfg in cands.items():
    tr=sorted(backtest(**cfg),key=lambda x:x[0]); h=len(tr)//2
    a,b=metrics(tr[:h]),metrics(tr[h:])
    if a and b:
        print(f"   {name:26s} IS PF={a['pf']:6.3f} t={a['t']:+5.2f} | OOS PF={b['pf']:6.3f} t={b['t']:+5.2f}"
              f" | decay {100*(1-b['pf']/a['pf']):+5.1f}%")

print("\nC. MONTE CARLO, 10,000 sequences, at 2.0 and 3.0 pt cost")
print(f"   {'config':26s} {'cost':>4} {'p05':>9} {'p50':>9} {'p95':>9} {'DD50':>7} {'DD95':>7} {'P(profit)':>10} {'P(DD>=15%)':>11}")
for name,cfg in cands.items():
    for c in (2.0,3.0):
        tr=backtest(**{**cfg,"cost":c})
        if len(tr)<30: continue
        mc=monte(tr,runs=10000)
        print(f"   {name:26s} {c:>4.1f} {mc['p05']:>9.1f} {mc['p50']:>9.1f} {mc['p95']:>9.1f} "
              f"{mc['dd50']:>7.1f} {mc['dd95']:>7.1f} {mc['p_profit']:>9.1f}% {mc['p_dd15']:>10.1f}%")

print("\nD. COST SENSITIVITY OF THE TWO TIME-FILTERED VERSIONS")
for name,cfg in [("after 10:15",cands["after 10:15"]),("after 10:30",cands["after 10:30"])]:
    for c in (2.0,3.0,4.0):
        m=metrics(backtest(**{**cfg,"cost":c}))
        if m: print(f"   {name:14s} cost {c:.1f}  n={m['n']:4d} PF={m['pf']:6.3f} net={m['net']:+8.1f} "
                    f"DD={m['dd']:6.1f} t={m['t']:+5.2f} yrs+={m['yp']}/{m['ny']}")

print("\nE. YEAR BY YEAR — after 10:15")
tr=backtest(**cands["after 10:15"])
yr=defaultdict(list)
for d,s,p,r in tr: yr[d.year].append(p)
for y in sorted(yr):
    v=yr[y]; g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0)
    print(f"   {y}  n={len(v):4d} net={sum(v):+8.1f} PF={g/l if l else 9.99:5.2f} win={100*sum(1 for x in v if x>0)/len(v):.1f}%")
