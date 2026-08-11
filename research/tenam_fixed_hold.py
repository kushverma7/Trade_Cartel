import csv, datetime as dt, zoneinfo, statistics as st
from collections import defaultdict
UTC=dt.timezone.utc; MEL=zoneinfo.ZoneInfo("Australia/Sydney")
rows=[]
with open("/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv") as f:
    for r in csv.DictReader(f):
        t=dt.datetime.strptime(r['timestamp'][:19],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
        rows.append((t,float(r['open']),float(r['high']),float(r['low']),float(r['close'])))
rows.sort()

def build(tf):
    out=[];cur=None;key=None
    for t,o,h,l,c in rows:
        k=int(t.timestamp())//(tf*60)
        if k!=key:
            if cur:out.append(tuple(cur))
            key=k;cur=[t,o,h,l,c]
        else:
            cur[2]=max(cur[2],h);cur[3]=min(cur[3],l);cur[4]=c
    if cur:out.append(tuple(cur))
    return out
def rma(v,n):
    o=[];a=None
    for i,x in enumerate(v):
        if i<n-1:o.append(None);continue
        a=sum(v[:n])/n if a is None else (a*(n-1)+x)/n
        o.append(a)
    return o
def ind(b):
    c=[x[4] for x in b];h=[x[2] for x in b];l=[x[3] for x in b]
    ema=[None]*len(c);k=2/201
    for i,v in enumerate(c):
        if i==199:ema[i]=sum(c[:200])/200
        elif i>199:ema[i]=v*k+ema[i-1]*(1-k)
    g=[0.0]*len(c);ls=[0.0]*len(c)
    for i in range(1,len(c)):
        d=c[i]-c[i-1];g[i]=max(d,0);ls[i]=max(-d,0)
    ag=rma(g,14);al=rma(ls,14)
    rsi=[None if ag[i] is None else (100.0 if al[i]==0 else 100-100/(1+ag[i]/al[i])) for i in range(len(c))]
    tr=[h[0]-l[0]]+[max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1])) for i in range(1,len(c))]
    atr=rma(tr,97)
    ub=[None]*len(c);lb=[None]*len(c);dn=[None]*len(c);sv=[None]*len(c)
    for i in range(len(c)):
        if atr[i] is None:continue
        m=(h[i]+l[i])/2;u=m+3.1*atr[i];d_=m-3.1*atr[i]
        pu=ub[i-1] if i>0 and ub[i-1] is not None else u
        pl=lb[i-1] if i>0 and lb[i-1] is not None else d_
        lb[i]=d_ if(d_>pl or c[i-1]<pl) else pl
        ub[i]=u  if(u<pu  or c[i-1]>pu) else pu
        if i==0 or atr[i-1] is None:dn[i]=1
        elif sv[i-1]==pu:dn[i]=-1 if c[i]>ub[i] else 1
        else:dn[i]=1 if c[i]<lb[i] else -1
        sv[i]=lb[i] if dn[i]==-1 else ub[i]
    return ema,rsi,dn

def stats(p):
    if not p: return None
    g=sum(v for v in p if v>0);l=-sum(v for v in p if v<=0)
    eq=0;pk=0;dd=0
    for v in p: eq+=v;pk=max(pk,eq);dd=max(dd,pk-eq)
    return len(p),(g/l if l else float('inf')),100*sum(1 for v in p if v>0)/len(p),sum(p),sum(p)/len(p),dd

def line(lab,p,cost):
    s=stats([v-cost for v in p])
    if not s: print(f"  {lab:34s}  no trades");return
    n,pf,w,net,ex,dd=s
    print(f"  {lab:34s} n={n:4d}  PF={pf:6.3f}  win={w:5.1f}%  net={net:+8.1f}  avg={ex:+6.2f}  maxDD={dd:7.1f}")

for tf,nm in [(30,"30-minute"),(45,"45-minute"),(60,"1-hour"),(120,"2-hour")]:
    b=build(tf); ema,rsi,dn=ind(b)
    exact=0; contains=0; res=[]; allday=[]
    for i in range(len(b)-1):
        if ema[i] is None or rsi[i] is None or dn[i] is None: continue
        lt=b[i][0].astimezone(MEL); nt=b[i+1][0].astimezone(MEL)
        # "the 10:00 candle": starts at 10:00, else the bar containing 10:00
        starts = (lt.hour,lt.minute)==(10,0)
        cont   = lt.astimezone(MEL).date()==nt.date() and lt.hour*60+lt.minute<600<nt.hour*60+nt.minute
        if not (starts or cont): continue
        if starts: exact+=1
        else: contains+=1
        c=b[i][4]; nxt=b[i+1][4]
        allday.append((lt.date(), nxt-c))
        if c>ema[i] and rsi[i]>50 and dn[i]<0: res.append((lt.date(),  nxt-c))
        elif c<ema[i] and rsi[i]<50 and dn[i]>0: res.append((lt.date(),-(nxt-c)))
    tag = "bar starts exactly at 10:00" if contains==0 else f"{exact} start at 10:00, {contains} merely contain it"
    print(f"\n=== {nm} chart  ({tag}) ===")
    print(f"  full sample {rows[0][0].astimezone(MEL).date()} .. {rows[-1][0].astimezone(MEL).date()}")
    cut=dt.date(2026,5,11)
    for cost,clab in [(0.0,"gross, no costs"),(2.0,"net of 2 pts cost")]:
        print(f"  -- {clab} --")
        line("FULL SAMPLE",              [x[1] for x in res], cost)
        line("LAST 3 MONTHS",            [x[1] for x in res if x[0]>=cut], cost)
    print("  -- baselines (gross) --")
    line("NULL: every day, always long", [x[1] for x in allday], 0.0)
    line("NULL: signal days, always long",[y for (d,y) in allday if d in {r[0] for r in res}], 0.0)
