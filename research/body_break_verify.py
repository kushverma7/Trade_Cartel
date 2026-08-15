import sys, math, statistics as st, random
sys.path.insert(0,'research')
import body_break_sweep as S
from collections import defaultdict, Counter
S.DO_MODE="proxy"

CFG=dict(logic="A",flip=True,one_shot=False,end_hour=16,stop="daily_open",tp="trail_half")
tr=S.run("A",True,False,16,"daily_open","trail_half")
print(f"TOP PROXY CELL: {CFG}\n  n={len(tr)}  net={sum(x[2] for x in tr):+.1f}")

# 1. where does dailyOpen actually come from?
first_bar=Counter()
do_dist=[]
for d in S.DAYS:
    bs=S.day_bars[d]
    if not bs: continue
    first_bar[(bs[0][0].hour,bs[0][0].minute)]+=1
print("\n1. SESSION FIRST BAR (this is what proxy uses as dailyOpen):")
for (h,m),c in first_bar.most_common(6):
    print(f"     {h:02d}:{m:02d}  {c:5d} sessions")

# 2. risk distribution — how far is the stop?
risks=[x[3] for x in tr]
risks.sort()
print(f"\n2. STOP DISTANCE (entry -> dailyOpen), points:")
print(f"     min {risks[0]:.1f}  p25 {risks[len(risks)//4]:.1f}  median {risks[len(risks)//2]:.1f}"
      f"  p75 {risks[3*len(risks)//4]:.1f}  max {risks[-1]:.1f}")
print(f"     trades with stop > 40 pts: {sum(1 for r in risks if r>40)} ({100*sum(1 for r in risks if r>40)/len(risks):.0f}%)")

# 3. year by year
yr=defaultdict(list)
for d,s,p,r in tr: yr[d.year].append(p)
print("\n3. YEAR BY YEAR:")
for y in sorted(yr):
    v=yr[y]; g=sum(x for x in v if x>0); l=-sum(x for x in v if x<=0)
    print(f"     {y}  n={len(v):4d}  net={sum(v):+8.1f}  PF={g/l if l else 9.99:5.2f}  win={100*sum(1 for x in v if x>0)/len(v):.1f}%")

# 4. IN-SAMPLE / OUT-OF-SAMPLE split at the midpoint
tr_sorted=sorted(tr,key=lambda x:x[0])
half=len(tr_sorted)//2
for lab,part in (("IS (first half)",tr_sorted[:half]),("OOS (second half)",tr_sorted[half:])):
    p=[x[2] for x in part]; g=sum(v for v in p if v>0); l=-sum(v for v in p if v<=0)
    m=sum(p)/len(p); sd=st.pstdev(p) or 1e-9
    print(f"\n4. {lab}: {part[0][0]} .. {part[-1][0]}  n={len(p)} PF={g/l if l else 9.99:.3f} "
          f"net={sum(p):+.1f} t={m/sd*math.sqrt(len(p)):+.2f}")

# 5. direction-shuffle null vs the MAXIMUM over the whole grid
rng=random.Random(5)
nulls=[]
for _ in range(2000):
    tot=0.0
    for d,s,p,r in tr:
        tot += p if rng.random()<0.5 else -(p+2*S.COST)
    nulls.append(tot)
nulls.sort()
obs=sum(x[2] for x in tr)
print(f"\n5. DIRECTION-SHUFFLE NULL (2000 runs): max {nulls[-1]:+.1f}  p95 {nulls[int(.95*1999)]:+.1f}  observed {obs:+.1f}")
print(f"   observed exceeds the shuffled MAXIMUM: {obs>nulls[-1]}")

# 6. bootstrap
p=[x[2] for x in tr]; nets=[];dds=[]
for _ in range(10000):
    s=[p[rng.randrange(len(p))] for _ in range(len(p))]
    eq=pk=dd=0.0
    for v in s: eq+=v; pk=max(pk,eq); dd=max(dd,pk-eq)
    nets.append(eq); dds.append(dd)
nets.sort(); dds.sort()
q=lambda a,f:a[int(f*(len(a)-1))]
print(f"\n6. MONTE CARLO (10k bootstrap): net p05 {q(nets,.05):+.1f}  p50 {q(nets,.50):+.1f}  p95 {q(nets,.95):+.1f}")
print(f"   maxDD p50 {q(dds,.50):.1f}  p95 {q(dds,.95):.1f}   P(net>0) {100*sum(1 for v in nets if v>0)/len(nets):.1f}%")
