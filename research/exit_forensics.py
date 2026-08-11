import csv, datetime as dt, zoneinfo, statistics as st
exec(open("research/verify_10am_fills.py").read().split("# --- load trade list")[0])
D="/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"
def load(fn):
    rows=list(csv.DictReader(open(fn,encoding='utf-8-sig'))); tr={}
    for r in rows:
        n=int(r['Trade number']); tr.setdefault(n,{})
        if r['Type'].startswith('Entry'):
            tr[n]['dt']=r['Date and time']; tr[n]['dir']='long' if 'long' in r['Type'] else 'short'; tr[n]['px']=float(r['Price AUD'])
        else: tr[n]['xdt']=r['Date and time']; tr[n]['xpx']=float(r['Price AUD'])
        tr[n]['pnl']=float(r['Net PnL AUD'])
    return [v for v in tr.values() if 'dt' in v and 'xdt' in v]
ts=[t for t in load(D+"6404634b-AU200BASE_OANDA_AU200AUD_20260811_3.csv") if t['dt'][11:16]=='10:00' and t['dt'][:10]>="2025-01-13"]

inrange=0; outside=0; fav=0; tot=0; gap=[]; details=[]
for t in ts:
    day=dt.date.fromisoformat(t['dt'][:10])
    e=agg(day,10,0,60); x=agg(day,11,0,60)
    if not e or not x: continue
    tot+=1; s=1 if t['dir']=='long' else -1
    if x[2]-0.5 <= t['xpx'] <= x[1]+0.5: inrange+=1
    else: outside+=1
    if s*(t['xpx']-t['px'])>0: fav+=1
    gap.append(s*(t['xpx']-x[3]))          # exit vs true 11:00 close, signed by trade dir
    details.append((t['dt'][:10],t['dir'],t['px'],t['xpx'],x[0],x[1],x[2],x[3],t['pnl']))

print(f"n={tot}")
print(f"  exit price inside the 11:00 bar's high/low : {inrange} ({100*inrange/tot:.1f}%)")
print(f"  exit price OUTSIDE that bar entirely       : {outside} ({100*outside/tot:.1f}%)")
print(f"  exits booked in the FAVOURABLE direction   : {fav} ({100*fav/tot:.1f}%)")
print(f"  signed(exit - true 11:00 close): mean {st.mean(gap):+.2f}  median {st.median(gap):+.2f}")
print(f"     -> positive means the booked exit is systematically BETTER than the real price")
print("\nfirst 12 trades  date       dir   entry    EXIT | 11:00 bar O/H/L/C            pnl")
for d in details[:12]:
    print(f"  {d[0]}  {d[1]:5s} {d[2]:8.1f} {d[3]:8.1f} | {d[4]:7.1f} {d[5]:7.1f} {d[6]:7.1f} {d[7]:7.1f}   {d[8]:+7.1f}")

print("\n--- how are WINNERS vs LOSERS booked? ---")
wd=[]; ld=[]
for t in ts:
    day=dt.date.fromisoformat(t['dt'][:10]); x=agg(day,11,0,60)
    if not x: continue
    s=1 if t['dir']=='long' else -1
    best = x[1] if s>0 else x[2]          # the bar's most favourable extreme
    if t['pnl']>0: wd.append(abs(t['xpx']-best))
    else: ld.append(t['pnl'])
print(f"  WINNERS n={len(wd)}: distance from exit fill to the bar's FAVOURABLE EXTREME")
print(f"     median {st.median(wd):.2f} pts | within 1pt of the extreme: {100*sum(1 for v in wd if v<=1)/len(wd):.1f}%")
from collections import Counter
c=Counter(ld)
print(f"  LOSERS  n={len(ld)}: pnl distribution -> {c.most_common(5)}")
print(f"     exactly -22.0 (a fixed 20pt stop + 2 comm): {100*c[-22.0]/len(ld):.1f}%")
