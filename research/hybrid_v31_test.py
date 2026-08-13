"""Hybrid v3.1 exactly as written, on AU200 5m, plus the two variants that
isolate its remaining defects."""
import csv, datetime as dt, zoneinfo, math, statistics as st
from collections import defaultdict
UTC=dt.timezone.utc; MEL=zoneinfo.ZoneInfo("Australia/Sydney")
SRC="/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv"
COST=2.0
raw=[]
for r in csv.DictReader(open(SRC)):
    t=dt.datetime.strptime(r["timestamp"][:19],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    raw.append((t,float(r["open"]),float(r["high"]),float(r["low"]),float(r["close"]),float(r["volume"] or 0)))
raw.sort()
byday=defaultdict(list)
for r in raw: byday[r[0].astimezone(MEL).date()].append(r)
def build(tf):
    out,cur,key=[],None,None
    for t,o,h,l,c,v in raw:
        k=int(t.timestamp())//(tf*60)
        if k!=key:
            if cur: out.append(tuple(cur))
            key,cur=k,[t,o,h,l,c,v]
        else: cur[3]=min(cur[3],l); cur[2]=max(cur[2],h); cur[4]=c; cur[5]+=v
    if cur: out.append(tuple(cur))
    return out
B=build(5)
tr=[];a=None;ATR=[]
for i,b in enumerate(B):
    t=b[2]-b[3] if i==0 else max(b[2]-b[3],abs(b[2]-B[i-1][4]),abs(b[3]-B[i-1][4]))
    tr.append(t)
    if i<13: ATR.append(None); continue
    a=sum(tr[:14])/14 if a is None else (a*13+t)/14
    ATR.append(a)
vwap=[None]*len(B); cvd=[0.0]*len(B); pv=vv=cd=0.0; cur=None
for i,b in enumerate(B):
    d=b[0].astimezone(MEL).date()
    if d!=cur: cur=d; pv=vv=cd=0.0
    pv+=(b[2]+b[3])/2*b[5]; vv+=b[5]
    rng=b[2]-b[3]
    cd+=b[5]*(2*((b[4]-b[3])/rng if rng>0 else 0.5)-1)
    vwap[i]=pv/vv if vv>0 else None; cvd[i]=cd
volma=[None]*len(B)
for i in range(20,len(B)): volma[i]=sum(B[j][5] for j in range(i-20,i))/20

def sim(stop_mode="as_written", add_tp=False, window=(600,720)):
    out=[]; unresolved=0; widened=0
    for i in range(40,len(B)-1):
        if ATR[i] is None or vwap[i] is None or not volma[i]: continue
        b=B[i]; lt=b[0].astimezone(MEL); mins=lt.hour*60+lt.minute
        if not (window[0]<=mins<window[1]): continue
        rh=max(B[j][2] for j in range(i-30,i)); rl=min(B[j][3] for j in range(i-30,i))
        rng=b[2]-b[3]
        if rng<=0: continue
        body=abs(b[4]-b[1])/rng; vr=b[5]/volma[i]
        rising = i>=8 and cvd[i]>cvd[i-8]
        bull = b[3]<rl and b[4]>rl and vr>=1.8 and body>=0.35 and b[4]>b[1] and rising and b[4]>vwap[i]
        bear = b[2]>rh and b[4]<rh and vr>=1.8 and body>=0.35 and b[4]<b[1] and (not rising) and b[4]<vwap[i]
        if not (bull or bear): continue
        s=1 if bull else -1; e=b[4]; A=ATR[i]
        struct = (rl - A*0.15) if s>0 else (rh + A*0.15)
        atrst  = e - s*A*0.35
        stop = (min(struct,atrst) if s>0 else max(struct,atrst)) if stop_mode=="as_written" \
               else (max(struct,atrst) if s>0 else min(struct,atrst))
        part = e + s*A*1.5
        tp   = e + s*A*3.0
        end=b[0]+dt.timedelta(minutes=5)
        path=[m for m in byday[end.astimezone(MEL).date()] if m[0]>=end]
        half=False; acc=0.0; pnl=None; k=i
        for (mt,mo,mh,ml,mc,mv) in path:
            # v3.1 recomputes the structural stop every bar -> it can widen
            if stop_mode=="as_written" and mt.minute%5==0:
                k=min(k+1,len(B)-1)
                nrl=min(B[j][3] for j in range(max(0,k-30),k)); nrh=max(B[j][2] for j in range(max(0,k-30),k))
                ns=(min(nrl-A*0.15,atrst) if s>0 else max(nrh+A*0.15,atrst))
                if s*(ns-stop)<0: widened+=1
                stop=ns
            adv=ml if s>0 else mh; fav=mh if s>0 else ml
            if s*(adv-stop)<=0: pnl=acc+(0.5 if half else 1.0)*s*(stop-e); break
            if not half and s*(fav-part)>=0: acc+=0.5*s*(part-e); half=True
            elif half and add_tp and s*(fav-tp)>=0: pnl=acc+0.5*s*(tp-e); break
        if pnl is None:
            unresolved+=1
            pnl=acc+(0.5 if half else 1.0)*s*(path[-1][4]-e) if path else 0.0
        out.append(pnl-COST)
    return out,unresolved,widened

def rep(lab,t,u,w):
    if not t: print(f"  {lab:40s} no trades"); return
    g=sum(v for v in t if v>0); l=-sum(v for v in t if v<=0)
    eq=pk=dd=0.0
    for v in t: eq+=v; pk=max(pk,eq); dd=max(dd,pk-eq)
    m=sum(t)/len(t); sd=st.pstdev(t) or 1e-9
    print(f"  {lab:40s} n={len(t):4d} PF={g/l if l else 9.99:5.3f} win={100*sum(1 for v in t if v>0)/len(t):5.1f}%"
          f" net={sum(t):+7.1f} avg={m:+6.2f} t={m/sd*math.sqrt(len(t)):+5.2f} DD={dd:6.1f} unres={u} stopWidened={w}")

print(f"AU200 5m, 444 sessions, {COST:.0f}pt cost, entries at bar close (process_orders_on_close)")
print("v3.1 SPEC: sweep30, vol>=1.8x, body>=0.35, CVD rising(8), VWAP side, 1.5xATR partial\n")
rep("v3.1 as written (min = wider stop)", *sim("as_written"))
rep("stop logic corrected (max = tighter)", *sim("corrected"))
rep("as written + a real take profit (3xATR)", *sim("as_written", add_tp=True))
rep("corrected + take profit", *sim("corrected", add_tp=True))
print()
rep("as written, 10:00-close window", *sim("as_written", window=(600,959)))
