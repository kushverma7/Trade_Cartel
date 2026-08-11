import csv, datetime as dt, zoneinfo, statistics as st
UTC=dt.timezone.utc; MEL=zoneinfo.ZoneInfo("Australia/Sydney")
rows=[]
with open("/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv") as f:
    for r in csv.DictReader(f):
        t=dt.datetime.strptime(r['timestamp'][:19],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
        rows.append((t,float(r['open']),float(r['high']),float(r['low']),float(r['close'])))
rows.sort()
from collections import defaultdict
by=defaultdict(list)
for r in rows: by[r[0].astimezone(MEL).date()].append(r)

D="/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"
tr={}
for r in csv.DictReader(open(D+"6404634b-AU200BASE_OANDA_AU200AUD_20260811_3.csv",encoding='utf-8-sig')):
    n=int(r['Trade number']); tr.setdefault(n,{})
    if r['Type'].startswith('Entry'):
        tr[n]['dt']=r['Date and time']; tr[n]['dir']=1 if 'long' in r['Type'] else -1
        tr[n]['px']=float(r['Price AUD'])
    else: tr[n]['booked']=float(r['Net PnL AUD'])
T=[v for v in tr.values() if 'dt' in v and v['dt'][:10]>="2025-01-14"]
print(f"YOUR entries, unchanged: n={len(T)}   ({T[0]['dt'][:10]} .. {T[-1]['dt'][:10]})\n")

def run(mode,tp=None,sl=None,trail=None,trig=None,cost=2.0):
    out=[]
    for t in T:
        d=dt.date.fromisoformat(t['dt'][:10]); s=t['dir']; e=t['px']
        # start the minute AFTER the signal bar closes
        start=dt.datetime.strptime(t['dt'],"%Y-%m-%d %H:%M").replace(tzinfo=MEL)+dt.timedelta(hours=1)
        path=[m for m in by[d] if m[0]>=start.astimezone(UTC)]
        if not path: continue
        px=None; peak=e; on=False; tstop=None
        for (mt,mo,mh,ml,mc) in path:
            adv = ml if s>0 else mh; fav = mh if s>0 else ml
            if sl is not None and s*(adv-e)<=-sl: px=e-s*sl; break      # adverse first (conservative)
            if mode=='tp' and s*(fav-e)>=tp: px=e+s*tp; break
            if mode=='trail':
                if not on and s*(fav-e)>=trig: on=True; peak=fav; tstop=peak-s*trail
                elif on:
                    if s*(fav-peak)>0: peak=fav; tstop=peak-s*trail
                if on and s*(adv-tstop)<=0: px=tstop; break
            if mt.astimezone(MEL).hour==15 and mt.astimezone(MEL).minute==59: px=mc; break
        if px is None: px=path[-1][4]
        out.append(s*(px-e)-cost)
    g=sum(v for v in out if v>0); l=-sum(v for v in out if v<=0)
    eq=0;pk=0;dd=0
    for v in out: eq+=v; pk=max(pk,eq); dd=max(dd,pk-eq)
    return out,(g/l if l else 9.99),100*sum(1 for v in out if v>0)/len(out),sum(out),dd

print(f"{'exit rule':38s} {'n':>4} {'PF':>6} {'win':>6} {'net':>9} {'/trade':>7} {'maxDD':>7}")
booked=[t['booked'] for t in T]
gb=sum(v for v in booked if v>0); lb=-sum(v for v in booked if v<=0)
print(f"{'TradingView BOOKED (for reference)':38s} {len(booked):4d} {gb/lb:6.3f} {100*sum(1 for v in booked if v>0)/len(booked):5.1f}% {sum(booked):+9.1f} {sum(booked)/len(booked):+7.2f} {'--':>7}")
print("-"*80)
for lab,kw in [
    ("their trail, resolved on 1m",      dict(mode='trail',trail=0.5,trig=3.0,sl=20)),
    ("trail 30pt, arm at 5pt, SL20",     dict(mode='trail',trail=30,trig=5,sl=20)),
    ("TP 10 / SL 10",                    dict(mode='tp',tp=10,sl=10)),
    ("TP 10 / SL 15",                    dict(mode='tp',tp=10,sl=15)),
    ("TP 10 / SL 20",                    dict(mode='tp',tp=10,sl=20)),
    ("TP 10 / SL 30",                    dict(mode='tp',tp=10,sl=30)),
    ("TP 15 / SL 20",                    dict(mode='tp',tp=15,sl=20)),
    ("TP 20 / SL 20",                    dict(mode='tp',tp=20,sl=20)),
    ("hold to 15:59, SL 20",             dict(mode='none',sl=20)),
]:
    o,pf,w,net,dd=run(**kw)
    print(f"{lab:38s} {len(o):4d} {pf:6.3f} {w:5.1f}% {net:+9.1f} {net/len(o):+7.2f} {dd:7.1f}")
