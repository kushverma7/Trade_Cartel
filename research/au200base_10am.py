import csv, glob, os, collections, math
D="/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"
FILES=sorted(glob.glob(D+"*AU200BASE*.csv"))

def load(fn):
    rows=list(csv.DictReader(open(fn,encoding='utf-8-sig')))
    trades={}
    for r in rows:
        n=int(r['Trade number']); t=r['Type']
        trades.setdefault(n,{})
        if t.startswith('Entry'):
            trades[n]['entry_dt']=r['Date and time']; trades[n]['dir']='long' if 'long' in t else 'short'
            trades[n]['entry_px']=float(r['Price AUD'])
        else:
            trades[n]['exit_dt']=r['Date and time']; trades[n]['exit_px']=float(r['Price AUD'])
        trades[n]['pnl']=float(r['Net PnL AUD']); trades[n]['comm']=float(r['Commission AUD'] or 0)
        trades[n]['mfe']=float(r['Favorable excursion AUD'] or 0)
        trades[n]['mae']=float(r['Adverse excursion AUD'] or 0)
        trades[n]['bars']=r['Duration (bars)']
    return [v for v in trades.values() if 'entry_dt' in v and 'exit_dt' in v]

def stats(ts,label):
    if not ts: print(f"  {label}: no trades"); return
    g=sum(t['pnl'] for t in ts if t['pnl']>0); l=-sum(t['pnl'] for t in ts if t['pnl']<=0)
    net=sum(t['pnl'] for t in ts); w=sum(1 for t in ts if t['pnl']>0)
    pf=g/l if l>0 else float('inf')
    days=len(set(t['entry_dt'][:10] for t in ts))
    # equity curve DD
    eq=0.0; peak=0.0; dd=0.0
    for t in sorted(ts,key=lambda x:x['entry_dt']):
        eq+=t['pnl']; peak=max(peak,eq); dd=max(dd,peak-eq)
    print(f"  {label}: n={len(ts):5d}  net={net:+9.1f}  PF={pf:5.3f}  win={100*w/len(ts):5.1f}%  "
          f"exp={net/len(ts):+6.2f}  maxDD={dd:7.1f}  days={days}  pts/day={net/days:+6.2f}")

for fn in FILES:
    base=os.path.basename(fn)
    ts=load(fn)
    if not ts: continue
    hh=collections.Counter(t['entry_dt'][11:16] for t in ts)
    print(f"\n=== {base}")
    print(f"  range {min(t['entry_dt'] for t in ts)[:10]} .. {max(t['entry_dt'] for t in ts)[:10]}")
    print(f"  entry-time distribution (top 8): {hh.most_common(8)}")
    stats(ts,"ALL          ")
    ten=[t for t in ts if t['entry_dt'][11:16]=='10:00']
    stats(ten,"10:00 ONLY   ")
    stats([t for t in ten if t['dir']=='long'],"  10:00 long ")
    stats([t for t in ten if t['dir']=='short'],"  10:00 short")
    if ten:
        yr=collections.defaultdict(list)
        for t in ten: yr[t['entry_dt'][:4]].append(t)
        print("  10:00 by year:")
        for y in sorted(yr):
            stats(yr[y],f"    {y}      ")
