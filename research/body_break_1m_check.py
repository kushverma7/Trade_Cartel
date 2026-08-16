"""Decisive test: re-resolve the same trades on 1-MINUTE data.
Signals stay on 5m (unchanged). Only the exit path resolution changes."""
import csv, datetime as dt, zoneinfo, math, statistics as st, sys
sys.path.insert(0,'research')
from collections import defaultdict
from body_break_stress import signals, day_bars as bars5, DAYS as DAYS5, ATR

UTC=dt.timezone.utc; MEL=zoneinfo.ZoneInfo("Australia/Melbourne")
M1="/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv"
m1=defaultdict(list)
for r in csv.DictReader(open(M1)):
    t=dt.datetime.strptime(r["timestamp"][:19],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).astimezone(MEL)
    m1[t.date()].append((t,float(r["open"]),float(r["high"]),float(r["low"]),float(r["close"])))
for d in m1: m1[d].sort()
OVERLAP=[d for d in DAYS5 if d in m1 and len(m1[d])>50]
print(f"overlap sessions with 1-minute data: {len(OVERLAP)}  ({OVERLAP[0]} .. {OVERLAP[-1]})")

def bt(res, cost=2.0, entry_after=None, end_hour=16):
    """res='5m' or '1m' — which series resolves the exit path."""
    out=[]
    for day in OVERLAP:
        bs5=bars5[day]; sigs=signals(day,end_hour)
        for n,(s,e,idx,bh,bl,do) in enumerate(sigs):
            body=bh-bl
            tmin=bs5[idx][0].hour*60+bs5[idx][0].minute
            if entry_after is not None and tmin<entry_after: continue
            risk=abs(e-do)
            if risk<=0.5 or risk>80: continue
            trail=body*0.5
            t_entry=bs5[idx][0]+dt.timedelta(minutes=5)
            t_flip=bs5[sigs[n+1][2]][0] if n+1<len(sigs) else None
            path = [b for b in (bs5 if res=='5m' else m1[day]) if b[0]>=t_entry]
            step = 5 if res=='5m' else 1
            pnl=None; peak=e; cur=do
            for (t,o,h,l,c) in path:
                if t_flip is not None and t>=t_flip:
                    pnl=s*(c if res=='1m' else c)-s*e
                    # close at the flip bar's close on the 5m grid
                    pnl=s*(bs5[sigs[n+1][2]][4]-e); break
                adv=l if s>0 else h
                if s*(adv-cur)<=0: pnl=s*(cur-e); break
                ts=peak-s*trail
                if s*(ts-cur)>0: cur=ts
                if s*(c-peak)>0: peak=c
                if t.hour>=end_hour: pnl=s*(c-e); break
            if pnl is None: pnl=s*(path[-1][4]-e) if path else 0.0
            out.append((day,s,pnl-cost,risk))
    return out

def rep(lab,tr):
    p=[x[2] for x in tr]
    if len(p)<10: print(f"  {lab:34s} n={len(p)}"); return
    g=sum(v for v in p if v>0); l=-sum(v for v in p if v<=0)
    eq=pk=dd=0.0
    for v in p: eq+=v; pk=max(pk,eq); dd=max(dd,pk-eq)
    m=sum(p)/len(p); sd=st.pstdev(p) or 1e-9
    print(f"  {lab:34s} n={len(p):4d} PF={g/l if l else 9.99:6.3f} win={100*sum(1 for v in p if v>0)/len(p):5.1f}%"
          f" net={sum(p):+8.1f} avg={m:+6.2f} DD={dd:6.1f} MAR={sum(p)/dd if dd else 0:6.2f} t={m/sd*math.sqrt(len(p)):+5.2f}")

print("\nBASELINE (all entries)")
rep("exits resolved on 5-minute bars", bt('5m'))
rep("exits resolved on 1-MINUTE bars", bt('1m'))
print("\nCHALLENGER (entries after 10:15)")
rep("exits resolved on 5-minute bars", bt('5m',entry_after=615))
rep("exits resolved on 1-MINUTE bars", bt('1m',entry_after=615))
print("\nAT 3-POINT COST")
rep("baseline, 1-minute exits", bt('1m',cost=3.0))
rep("after 10:15, 1-minute exits", bt('1m',cost=3.0,entry_after=615))
