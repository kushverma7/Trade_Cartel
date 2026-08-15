import pickle, math, random, statistics as st, sys
sys.path.insert(0,'research')
from body_break_sweep import DAYS, day_bars, signals, run, metrics, COST
from collections import defaultdict

# 1. why so few trades?
side_counts=defaultdict(int); has_line=0; has_body=0
for d in DAYS:
    bs=day_bars[d]; do=bh=bl=None
    for t,o,h,l,c in bs:
        if t.hour==9 and t.minute==50: do=o
        if t.hour==10 and t.minute==0 and do is not None:
            bh=max(o,c); bl=min(o,c)
    if do is not None: has_line+=1
    if bh is not None:
        has_body+=1
        side = -1 if bh<do else (1 if bl>do else 0)
        side_counts[side]+=1
print("WHY THE TRADE COUNT IS LOW")
print(f"  sessions total                         {len(DAYS)}")
print(f"  sessions with a 09:50 bar (dailyOpen)  {has_line}")
print(f"  sessions with a 10:00 body             {has_body}")
print(f"  of those:  side=+1 (body above open)   {side_counts[1]}  ({100*side_counts[1]/has_body:.1f}%)")
print(f"             side=-1 (body below open)   {side_counts[-1]} ({100*side_counts[-1]/has_body:.1f}%)")
print(f"             side= 0 (STRADDLES open)    {side_counts[0]} ({100*side_counts[0]/has_body:.1f}%)  <- Logic A cannot arm")
print(f"  => Logic A is eligible on {side_counts[1]+side_counts[-1]} of {len(DAYS)} sessions "
      f"({100*(side_counts[1]+side_counts[-1])/len(DAYS):.1f}%)")

# 2. does oneShot do anything?
a=run("A",True,False,14,"daily_open","fixed20"); b=run("A",True,True,14,"daily_open","fixed20")
print(f"\nONESHOT: off n={len(a)} net={sum(x[2] for x in a):+.1f} | on n={len(b)} net={sum(x[2] for x in b):+.1f}"
      f" | identical={a==b}")
print("  activeDir==0 in armedA already enforces one signal per day, so oneShot is a dead input.")

# 3. Logic B on its own
print("\nLOGIC B (10:00 candle itself), best cells:")
res=pickle.load(open("/tmp/claude-0/-home-user-Trade-Cartel/af36979e-ba34-557a-a8b0-0a27e52e3758/scratchpad/bb_res.pkl","rb"))
bs_=[r for r in res if r[0]['logic']=='B']
bs_.sort(key=lambda r:-r[1]['t'])
for c,m in bs_[:5]:
    print(f"  flip={str(c['flip']):5} end={c['endHour']:2} {c['stop']:10} {c['tp']:11} "
          f"n={m['n']:4d} PF={m['pf']:.3f} win={m['win']:.1f}% net={m['net']:+7.1f} t={m['t']:+.2f} yrs+={m['yp']}/{m['ny']}")

# 4. flip on vs off, like for like
print("\nFLIP ON vs OFF (same cell otherwise):")
for eh,sk,tk in [(14,"daily_open","fixed20"),(11,"daily_open","trail_half"),(14,"body_far","2R")]:
    for fl in (False,True):
        m=metrics(run("A",fl,False,eh,sk,tk))
        if m: print(f"  end={eh:2} {sk:10} {tk:11} flip={str(fl):5} n={m['n']:4d} PF={m['pf']:.3f} net={m['net']:+7.1f} t={m['t']:+.2f}")

# 5. Monte Carlo on the leader
print("\nMONTE CARLO — leader: Logic A, flip ON, end 14, stop daily_open, tp fixed20")
tr=run("A",True,False,14,"daily_open","fixed20")
p=[x[2] for x in tr]; rng=random.Random(42)
nets=[];dds=[]
for _ in range(10000):
    s=[p[rng.randrange(len(p))] for _ in range(len(p))]
    eq=pk=dd=0.0
    for v in s:
        eq+=v; pk=max(pk,eq); dd=max(dd,pk-eq)
    nets.append(eq); dds.append(dd)
nets.sort(); dds.sort()
q=lambda a,f:a[int(f*(len(a)-1))]
print(f"  observed net {sum(p):+.1f} pts over n={len(p)}")
print(f"  bootstrap net   p05 {q(nets,.05):+7.1f}   p50 {q(nets,.50):+7.1f}   p95 {q(nets,.95):+7.1f}")
print(f"  bootstrap maxDD p50 {q(dds,.50):7.1f}   p95 {q(dds,.95):7.1f}")
print(f"  P(net > 0) = {100*sum(1 for v in nets if v>0)/len(nets):.1f}%")
# shuffle null: randomise trade DIRECTION, keep the same entries/exits
nulls=[]
for _ in range(2000):
    tot=0.0
    for d,s,pnl,risk in tr:
        tot += (pnl if rng.random()<0.5 else -(pnl+2*COST))
    nulls.append(tot)
nulls.sort()
print(f"  direction-shuffle null: max over 2000 runs = {nulls[-1]:+.1f}, "
      f"95th pct = {q(nulls,.95):+.1f}, observed = {sum(p):+.1f}")
print(f"  observed beats {100*sum(1 for v in nulls if v<sum(p))/len(nulls):.1f}% of shuffled runs")
