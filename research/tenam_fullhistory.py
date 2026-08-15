"""Re-run the 10:00 one-bar-hold result on the FULL six-year 5-minute file,
against the 19-month 1-minute file it was originally measured on."""
import csv, datetime as dt, zoneinfo, math, statistics as st
from collections import defaultdict
UTC=dt.timezone.utc; MEL=zoneinfo.ZoneInfo("Australia/Sydney")
U="/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"

def load(path):
    rows=[]
    for r in csv.DictReader(open(path)):
        t=dt.datetime.strptime(r["timestamp"][:19],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
        rows.append((t,float(r["open"]),float(r["high"]),float(r["low"]),float(r["close"]),float(r["volume"] or 0)))
    rows.sort(); return rows

def agg(rows,tf):
    out,cur,key=[],None,None
    for t,o,h,l,c,v in rows:
        k=int(t.timestamp())//(tf*60)
        if k!=key:
            if cur: out.append(tuple(cur))
            key,cur=k,[t,o,h,l,c,v]
        else: cur[3]=min(cur[3],l); cur[2]=max(cur[2],h); cur[4]=c; cur[5]+=v
    if cur: out.append(tuple(cur))
    return out

def ind(B):
    c=[x[4] for x in B]; h=[x[2] for x in B]; l=[x[3] for x in B]
    ema=[None]*len(c); k=2/201
    for i,v in enumerate(c):
        if i==199: ema[i]=sum(c[:200])/200
        elif i>199: ema[i]=v*k+ema[i-1]*(1-k)
    g=[0.0]*len(c); ls=[0.0]*len(c)
    for i in range(1,len(c)):
        d=c[i]-c[i-1]; g[i]=max(d,0); ls[i]=max(-d,0)
    def rma(v,n):
        o=[];a=None
        for i,x in enumerate(v):
            if i<n-1: o.append(None); continue
            a=sum(v[:n])/n if a is None else (a*(n-1)+x)/n
            o.append(a)
        return o
    ag=rma(g,14); al=rma(ls,14)
    rsi=[None if ag[i] is None else (100.0 if al[i]==0 else 100-100/(1+ag[i]/al[i])) for i in range(len(c))]
    tr=[h[0]-l[0]]+[max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1])) for i in range(1,len(c))]
    a=rma(tr,97)
    ub=[None]*len(c); lb=[None]*len(c); dn=[None]*len(c); sv=[None]*len(c)
    for i in range(len(c)):
        if a[i] is None: continue
        m=(h[i]+l[i])/2; u=m+3.1*a[i]; d_=m-3.1*a[i]
        pu=ub[i-1] if i>0 and ub[i-1] is not None else u
        pl=lb[i-1] if i>0 and lb[i-1] is not None else d_
        lb[i]=d_ if(d_>pl or c[i-1]<pl) else pl
        ub[i]=u  if(u<pu  or c[i-1]>pu) else pu
        if i==0 or a[i-1] is None: dn[i]=1
        elif sv[i-1]==pu: dn[i]=-1 if c[i]>ub[i] else 1
        else: dn[i]=1 if c[i]<lb[i] else -1
        sv[i]=lb[i] if dn[i]==-1 else ub[i]
    return ema,rsi,dn

def test(rows,tf,label,cost):
    B=agg(rows,tf); ema,rsi,dn=ind(B)
    res=[]; nul=[]
    for i in range(len(B)-1):
        if ema[i] is None or rsi[i] is None or dn[i] is None: continue
        lt=B[i][0].astimezone(MEL)
        if (lt.hour,lt.minute)!=(10,0): continue
        c=B[i][4]; nxt=B[i+1][4]
        nul.append((lt.date(),nxt-c))
        if c>ema[i] and rsi[i]>50 and dn[i]<0: res.append((lt.date(),nxt-c))
        elif c<ema[i] and rsi[i]<50 and dn[i]>0: res.append((lt.date(),-(nxt-c)))
    def rep(lab,tr,ct):
        if not tr: print(f"    {lab:26s} no trades"); return
        p=[x[1]-ct for x in tr]
        g=sum(v for v in p if v>0); l=-sum(v for v in p if v<=0)
        m=sum(p)/len(p); sd=st.pstdev(p) or 1e-9
        yr=defaultdict(float)
        for d,v in tr: yr[d.year]+=v-ct
        pos=sum(1 for v in yr.values() if v>0)
        print(f"    {lab:26s} n={len(p):5d} PF={g/l if l else 9.99:5.3f} win={100*sum(1 for v in p if v>0)/len(p):5.1f}%"
              f" avg={m:+6.2f} t={m/sd*math.sqrt(len(p)):+6.2f} yrs+={pos}/{len(yr)}")
    print(f"  {label}")
    rep("filtered signal, gross",res,0.0)
    rep("filtered signal, 2pt cost",res,cost)
    rep("NULL always-long, gross",nul,0.0)

rows1=load(U+"c1e55d1f-au200_aud_1m_4.csv")
rows5=load(U+"30348eaf-au200_aud_5m.csv")
d1=sorted({r[0].astimezone(MEL).date() for r in rows1})
d5=sorted({r[0].astimezone(MEL).date() for r in rows5})
print("10:00 CANDLE + ONE-BAR HOLD, 1-HOUR — SAME LOGIC, TWO SAMPLES\n")
print(f"  1m file : {d1[0]} .. {d1[-1]}  {len(d1)} sessions")
print(f"  5m file : {d5[0]} .. {d5[-1]}  {len(d5)} sessions   <- 3.7x more\n")
test(rows1,60,"FROM 1-MINUTE FILE (what I reported earlier)",2.0)
print()
test(rows5,60,"FROM 5-MINUTE FILE (full six years)",2.0)
