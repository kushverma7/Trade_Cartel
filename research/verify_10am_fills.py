import csv, datetime as dt, zoneinfo, collections, statistics
MEL=zoneinfo.ZoneInfo("Australia/Sydney"); UTC=dt.timezone.utc
# --- load 1m ---
bars={}
with open("/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv") as f:
    for r in csv.DictReader(f):
        t=dt.datetime.strptime(r['timestamp'][:19],"%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC).astimezone(MEL)
        bars[t]=(float(r['open']),float(r['high']),float(r['low']),float(r['close']))
print("1m bars:",len(bars),"range",min(bars).date(),"..",max(bars).date())

def agg(day,h0,m0,mins):
    """aggregate `mins` 1-min bars from local time h0:m0 on `day`"""
    o=h=l=c=None
    for k in range(mins):
        t=dt.datetime.combine(day,dt.time(h0,m0),tzinfo=MEL)+dt.timedelta(minutes=k)
        b=bars.get(t)
        if b is None: continue
        if o is None: o=b[0]; h=b[1]; l=b[2]
        h=max(h,b[1]); l=min(l,b[2]); c=b[3]
    return (o,h,l,c) if o is not None else None

# --- load trade list (1H OANDA file) ---
def load(fn):
    rows=list(csv.DictReader(open(fn,encoding='utf-8-sig'))); tr={}
    for r in rows:
        n=int(r['Trade number']); tr.setdefault(n,{})
        if r['Type'].startswith('Entry'):
            tr[n]['dt']=r['Date and time']; tr[n]['dir']='long' if 'long' in r['Type'] else 'short'
            tr[n]['px']=float(r['Price AUD'])
        else: tr[n]['xdt']=r['Date and time']; tr[n]['xpx']=float(r['Price AUD'])
        tr[n]['pnl']=float(r['Net PnL AUD'])
    return [v for v in tr.values() if 'dt' in v and 'xdt' in v]

D="/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"
ts=[t for t in load(D+"6404634b-AU200BASE_OANDA_AU200AUD_20260811_3.csv") if t['dt'][11:16]=='10:00']
ov=[t for t in ts if t['dt'][:10]>="2025-01-13"]
print(f"\n1H file: {len(ts)} 10:00 trades, {len(ov)} overlap my 1m data")

dopen=[]; dclose=[]; dxopen=[]
for t in ov:
    day=dt.date.fromisoformat(t['dt'][:10])
    bar=agg(day,10,0,60)
    if not bar: continue
    dopen.append(t['px']-bar[0]); dclose.append(t['px']-bar[3])
    xbar=agg(day,11,0,60)
    if xbar: dxopen.append(t['xpx']-xbar[0])

def m(v,lab):
    if not v: print(f"  {lab}: none"); return
    a=[abs(x) for x in v]
    print(f"  {lab}: n={len(v)} med|d|={statistics.median(a):6.2f}  mean|d|={sum(a)/len(a):6.2f}  within1pt={100*sum(1 for x in a if x<=1.0)/len(a):5.1f}%")
print("\nENTRY price vs my 1-min feed:")
m(dopen ,"entry vs 10:00 hourly OPEN ")
m(dclose,"entry vs 10:00 hourly CLOSE")
print("EXIT price vs my 1-min feed:")
m(dxopen,"exit  vs 11:00 hourly OPEN ")

print("\n--- exit vs 11:00 hourly CLOSE, and P&L identity ---")
dxc=[]; pnl_err=[]; recon=[]
for t in ov:
    day=dt.date.fromisoformat(t['dt'][:10])
    e=agg(day,10,0,60); x=agg(day,11,0,60)
    if not e or not x: continue
    dxc.append(t['xpx']-x[3])
    s=1 if t['dir']=='long' else -1
    pnl_err.append(t['pnl'] - (s*(t['xpx']-t['px'])-2))
    recon.append((s, x[3]-e[3], t['pnl']))
m(dxc,"exit vs 11:00 hourly CLOSE ")
m(pnl_err,"pnl - [dir*(xpx-px)-2]     ")

# NULL: always-long / always-short over the SAME hour, my feed
mv=[]
days=sorted(set(dt.date.fromisoformat(t['dt'][:10]) for t in ov))
for day in days:
    e=agg(day,10,0,60); x=agg(day,11,0,60)
    if e and x: mv.append(x[3]-e[3])
import statistics as st
print(f"\nNULL on the same {len(mv)} sessions, 10:00close -> 11:00close move:")
print(f"  always LONG : mean {st.mean(mv):+6.3f}  win {100*sum(1 for v in mv if v>0)/len(mv):5.1f}%  sd {st.pstdev(mv):.2f}")
print(f"  always SHORT: mean {-st.mean(mv):+6.3f}  win {100*sum(1 for v in mv if v<0)/len(mv):5.1f}%")
print(f"  |move| median {st.median([abs(v) for v in mv]):.2f}   >=10pts: {100*sum(1 for v in mv if abs(v)>=10)/len(mv):.1f}%")

hit=sum(1 for s,mvv,p in recon if s*mvv>0)
print(f"\nSTRATEGY directional hit rate on my feed: {100*hit/len(recon):.1f}%  (n={len(recon)})")
print(f"  strategy mean signed move (my feed): {st.mean([s*mvv for s,mvv,p in recon]):+.3f}")
print(f"  strategy mean reported net pnl     : {st.mean([p for _,_,p in recon]):+.3f}")
