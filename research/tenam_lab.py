import csv, datetime as dt, zoneinfo, math, statistics as st
from collections import defaultdict
UTC=dt.timezone.utc; MEL=zoneinfo.ZoneInfo("Australia/Sydney")
raw=[]
with open("/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv") as f:
    for r in csv.DictReader(f):
        t=dt.datetime.strptime(r['timestamp'][:19],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).astimezone(MEL)
        raw.append((t,float(r['open']),float(r['high']),float(r['low']),float(r['close'])))
raw.sort()
day=defaultdict(dict)
for t,o,h,l,c in raw: day[t.date()][t.hour*60+t.minute]=(o,h,l,c)
days=sorted(d for d in day if sum(1 for m in day[d] if 600<=m<=959)>200)
print(f"sessions with a full 10:00-15:59 cash day: {len(days)}  ({days[0]} .. {days[-1]})")
prevclose={}
for i,d in enumerate(days):
    if i: 
        pm=[m for m in day[days[i-1]] if m<=959]
        if pm: prevclose[d]=day[days[i-1]][max(pm)][3]

def blk(d,a,b):
    ms=[m for m in day[d] if a<=m<b]
    if not ms: return None
    ms.sort(); o=day[d][ms[0]][0]; c=day[d][ms[-1]][3]
    return o,max(day[d][m][1] for m in ms),min(day[d][m][2] for m in ms),c

def path(d,frm,to):
    return [(m,)+day[d][m] for m in sorted(day[d]) if frm<=m<to]

def resolve(d,s,e,frm,to,tp,sl):
    """conservative: adverse extreme first within each minute"""
    for m,o,h,l,c in path(d,frm,to):
        adv=l if s>0 else h; fav=h if s>0 else l
        if sl and s*(adv-e)<=-sl: return -sl
        if tp and s*(fav-e)>=tp: return tp
    p=path(d,frm,to)
    return s*(p[-1][4]-e) if p else 0.0

COST=2.0
results=[]
def record(name,trades):
    p=[x-COST for x in trades]
    if len(p)<60: return
    g=sum(v for v in p if v>0); l=-sum(v for v in p if v<=0)
    pf=g/l if l>0 else 99.0
    m=sum(p)/len(p); sd=st.pstdev(p) or 1e-9
    results.append((name,len(p),pf,100*sum(1 for v in p if v>0)/len(p),sum(p),m,m/sd*math.sqrt(len(p)),sum(p)/len(days)))

# ---------- family A: the 10:00 candle's own body, continue or fade ----------
for clen in (5,15,30,60):
    for hold_to,hl in [(600+clen+60,"+1h"),(600+clen+120,"+2h"),(959,"to close")]:
        for tp,sl in [(None,None),(10,10),(10,20),(10,30),(15,20),(20,20),(20,40)]:
            for sign,slab in [(1,"continue"),(-1,"fade")]:
                tr=[]
                for d in days:
                    b=blk(d,600,600+clen)
                    if not b or b[3]==b[0]: continue
                    s=sign*(1 if b[3]>b[0] else -1); e=b[3]
                    tr.append(resolve(d,s,e,600+clen,hold_to,tp,sl))
                record(f"A {clen:2d}m 10:00 body {slab:8s} hold{hl:9s} tp{tp} sl{sl}",tr)

# ---------- family B: position vs the DAILY OPEN at 10:00+X ----------
for x in (15,30,60):
    for hold_to,hl in [(600+x+60,"+1h"),(959,"to close")]:
        for tp,sl in [(None,None),(10,20),(10,30),(20,30)]:
            for sign,slab in [(1,"with"),(-1,"against")]:
                tr=[]
                for d in days:
                    b=blk(d,600,600+x); dop=blk(d,600,601)
                    if not b or not dop: continue
                    s=sign*(1 if b[3]>dop[0] else -1)
                    tr.append(resolve(d,s,b[3],600+x,hold_to,tp,sl))
                record(f"B daily-open {slab:7s} at 10:{x:02d} hold{hl:9s} tp{tp} sl{sl}",tr)

# ---------- family C: opening-range breakout, RESTING order at a known level ----------
for n in (5,15,30,60):
    for hold_to,hl in [(959,"to close"),(600+n+120,"+2h")]:
        for tp,sl in [(None,None),(10,10),(10,20),(20,20),(20,30)]:
            for sign,slab in [(1,"break"),(-1,"fade")]:
                tr=[]
                for d in days:
                    orr=blk(d,600,600+n)
                    if not orr: continue
                    hi,lo=orr[1],orr[2]
                    if hi<=lo: continue
                    s=0; e=None
                    for m,o,h,l,c in path(d,600+n,hold_to):
                        if h>=hi: s=1; e=max(hi,o); break
                        if l<=lo:  s=-1; e=min(lo,o); break
                    if not s: continue
                    s*=sign
                    tr.append(resolve(d,s,e,m+1,hold_to,tp,sl))
                record(f"C OR{n:2d}m {slab:6s} hold{hl:9s} tp{tp} sl{sl}",tr)

# ---------- family D: overnight gap ----------
for hold_to,hl in [(660,"+1h"),(720,"+2h"),(959,"to close")]:
    for tp,sl in [(None,None),(10,20),(20,30)]:
        for sign,slab in [(1,"with gap"),(-1,"fade gap")]:
            for thr in (0,5,10):
                tr=[]
                for d in days:
                    if d not in prevclose: continue
                    dop=blk(d,600,601)
                    if not dop: continue
                    g=dop[0]-prevclose[d]
                    if abs(g)<thr: continue
                    s=sign*(1 if g>0 else -1)
                    b=blk(d,600,660)
                    if not b: continue
                    tr.append(resolve(d,s,b[3],660,hold_to,tp,sl))
                record(f"D gap {slab:8s} |g|>={thr:2d} hold{hl:9s} tp{tp} sl{sl}",tr)

K=len(results); bar=math.sqrt(2*math.log(K)) if K>1 else 0
print(f"\ncells tested K={K}   multiple-testing bar  t >= sqrt(2 ln K) = {bar:.2f}")
print(f"target for '10 points a day' = +10.0 pts/day\n")
results.sort(key=lambda r:-r[6])
print(f"{'rule':52s} {'n':>4} {'PF':>6} {'win':>6} {'net':>8} {'/trade':>7} {'t':>6} {'pts/day':>8}")
for r in results[:15]:
    flag="  <-- clears bar" if r[6]>=bar else ""
    print(f"{r[0]:52s} {r[1]:4d} {r[2]:6.3f} {r[3]:5.1f}% {r[4]:+8.1f} {r[5]:+7.2f} {r[6]:+6.2f} {r[7]:+8.2f}{flag}")
print(f"\ncells with t >= {bar:.2f}: {sum(1 for r in results if r[6]>=bar)}")
print(f"cells with PF > 1.0      : {sum(1 for r in results if r[2]>1.0)} of {K}")
print(f"cells reaching +10 pts/day: {sum(1 for r in results if r[7]>=10)}")
