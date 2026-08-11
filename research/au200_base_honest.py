import csv, datetime as dt, zoneinfo, statistics as st
from collections import defaultdict
UTC=dt.timezone.utc; MEL=zoneinfo.ZoneInfo("Australia/Sydney"); FIX10=dt.timezone(dt.timedelta(hours=10))
rows=[]
with open("/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv") as f:
    for r in csv.DictReader(f):
        t=dt.datetime.strptime(r['timestamp'][:19],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
        rows.append((t,float(r['open']),float(r['high']),float(r['low']),float(r['close'])))
rows.sort()
MINTICK=0.1

def build(tfmin):
    out=[]; cur=None; key=None
    for t,o,h,l,c in rows:
        k=int(t.timestamp())//(tfmin*60)
        if k!=key:
            if cur: out.append(cur)
            key=k; cur=[t,o,h,l,c]
        else:
            cur[2]=max(cur[2],h); cur[3]=min(cur[3],l); cur[4]=c
    if cur: out.append(cur)
    return out

def rma(vals,n):
    out=[]; a=None
    for i,v in enumerate(vals):
        if i<n-1: out.append(None); continue
        if a is None: a=sum(vals[:n])/n
        else: a=(a*(n-1)+v)/n
        out.append(a)
    return out

def indicators(bars):
    c=[b[4] for b in bars]; h=[b[2] for b in bars]; l=[b[3] for b in bars]
    ema=[None]*len(c); k=2/201
    for i,v in enumerate(c):
        if i==199: ema[i]=sum(c[:200])/200
        elif i>199: ema[i]=v*k+ema[i-1]*(1-k)
    g=[0.0]*len(c); ls=[0.0]*len(c)
    for i in range(1,len(c)):
        d=c[i]-c[i-1]; g[i]=max(d,0); ls[i]=max(-d,0)
    ag=rma(g,14); al=rma(ls,14)
    rsi=[None if ag[i] is None else (100.0 if al[i]==0 else 100-100/(1+ag[i]/al[i])) for i in range(len(c))]
    tr=[h[0]-l[0]]+[max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1])) for i in range(1,len(c))]
    atr=rma(tr,97)
    ub=[None]*len(c); lb=[None]*len(c); dirn=[None]*len(c); stv=[None]*len(c)
    for i in range(len(c)):
        if atr[i] is None: continue
        hl2=(h[i]+l[i])/2; u=hl2+3.1*atr[i]; d_=hl2-3.1*atr[i]
        pu=ub[i-1] if i>0 and ub[i-1] is not None else u
        pl=lb[i-1] if i>0 and lb[i-1] is not None else d_
        lb[i]=d_ if (d_>pl or c[i-1]<pl) else pl
        ub[i]=u  if (u<pu  or c[i-1]>pu) else pu
        if i==0 or atr[i-1] is None: dirn[i]=1
        elif stv[i-1]==pu: dirn[i]=-1 if c[i]>ub[i] else 1
        else: dirn[i]=1 if c[i]<lb[i] else -1
        stv[i]=lb[i] if dirn[i]==-1 else ub[i]
    return ema,rsi,dirn

# minute index for path resolution
mi=defaultdict(list)
for t,o,h,l,c in rows: mi[t.date()].append((t,o,h,l,c))

def simulate(tfmin, sl_pts, trig_pts, trail_pts, tick_units, tzmode, hours):
    bars=build(tfmin); ema,rsi,dirn=indicators(bars)
    scale = 1.0 if tick_units=="points" else MINTICK   # multiplier applied to raw input
    trades=[]
    for i,b in enumerate(bars):
        if ema[i] is None or rsi[i] is None or dirn[i] is None: continue
        t=b[0]; lt = t.astimezone(FIX10) if tzmode=="fixed" else t.astimezone(MEL)
        if (lt.hour,lt.minute) not in hours: continue
        c=b[4]
        bull = c>ema[i] and rsi[i]>50 and dirn[i]<0
        bear = c<ema[i] and rsi[i]<50 and dirn[i]>0
        if not (bull or bear): continue
        s=1 if bull else -1
        entry=c; hard=entry-s*sl_pts
        trig=trig_pts*scale; off=trail_pts*scale
        peak=entry; trailing=False; tstop=None; exitpx=None
        path=[m for m in mi[t.astimezone(UTC).date()] if m[0]>t] + [m for m in mi[(t+dt.timedelta(days=1)).astimezone(UTC).date()] if m[0]>t]
        for (mt,mo,mh,ml,mc) in path[:600]:
            adv = ml if s>0 else mh; fav = mh if s>0 else ml
            if s*(adv-hard)<=0: exitpx=hard; break                       # hard stop first (conservative)
            if trailing and s*(adv-tstop)<=0: exitpx=tstop; break
            if not trailing and s*(fav-entry)>=trig:
                trailing=True; peak=fav; tstop=peak-s*off
                if s*(adv-tstop)<=0 and s*(adv-fav)<0: exitpx=tstop; break
            elif trailing:
                if s*(fav-peak)>0: peak=fav; tstop=peak-s*off
                if s*(adv-tstop)<=0: exitpx=tstop; break
            if (mt.astimezone(MEL).hour,mt.astimezone(MEL).minute)==(15,59): exitpx=mc; break
        if exitpx is None: exitpx=path[min(len(path)-1,599)][4] if path else entry
        trades.append((t, s, s*(exitpx-entry)-2.0))
    return trades

def rep(tr,label):
    if not tr: print(f"{label:52s} no trades"); return
    p=[x[2] for x in tr]; g=sum(v for v in p if v>0); l=-sum(v for v in p if v<=0)
    eq=0;pk=0;dd=0
    for v in p: eq+=v; pk=max(pk,eq); dd=max(dd,pk-eq)
    days=len(set(x[0].astimezone(MEL).date() for x in tr))
    print(f"{label:52s} n={len(p):4d} PF={g/l if l else 9.99:5.3f} win={100*sum(1 for v in p if v>0)/len(p):5.1f}% "
          f"net={sum(p):+8.1f} exp={sum(p)/len(p):+6.2f} maxDD={dd:6.1f} pts/day={sum(p)/days:+6.2f}")

print("AU200-BASE, YOUR EXACT LOGIC, exits resolved on 1-MINUTE path")
print(f"data {rows[0][0].date()} .. {rows[-1][0].date()}   SL=20  (as booked in your trade list)\n")
for tf,hrs,nm in [(60,{(10,0)},"1H"),(15,{(10,0)},"15m"),(5,{(9,50),(9,55),(10,0)},"5m")]:
    print(f"-- {nm} chart --")
    rep(simulate(tf,20,30,5,"ticks","fixed",hrs), f"  AS WRITTEN (trail 0.5pt, trig 3pt, UTC+10 fixed)")
    rep(simulate(tf,20,5,30,"points","fixed",hrs), f"  FIXED units+swap (trig 5pt, trail 30pt)")
    rep(simulate(tf,20,5,30,"points","local",hrs), f"  FIXED + true Melbourne local time")
