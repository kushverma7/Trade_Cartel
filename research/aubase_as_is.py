import csv, glob, os, datetime as dt
from collections import defaultdict
D="/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"
NAMES={"262bdc4a":"30-minute","c1518c59":"45-minute","6404634b":"1-hour","9057561c":"2-hour",
       "b558cb8b":"15-min (Capital.com)"}
def load(fn):
    tr={}
    for r in csv.DictReader(open(fn,encoding='utf-8-sig')):
        n=int(r['Trade number']); tr.setdefault(n,{})
        if r['Type'].startswith('Entry'): tr[n]['dt']=r['Date and time']
        tr[n]['pnl']=float(r['Net PnL AUD'])
    return [v for v in tr.values() if 'dt' in v]
def bdays(a,b):
    n=0; d=a
    while d<=b:
        if d.weekday()<5: n+=1
        d+=dt.timedelta(days=1)
    return int(n*0.96)   # ~4% public holidays
print("AU200-BASE exactly as it stands -- YOUR exported trades, TradingView's own P&L")
print("points per day = net points / every trading day in the range (not just days it traded)\n")
print(f"{'timeframe':22s} {'window':12s} {'n':>5} {'net pts':>9} {'/trade':>7} {'days':>6} {'PTS/DAY':>8}")
print("-"*76)
for fn in sorted(glob.glob(D+"*AU200BASE*.csv")):
    key=os.path.basename(fn)[:8]; nm=NAMES.get(key,key)
    T=load(fn)
    if not T: continue
    a=dt.date.fromisoformat(min(t['dt'] for t in T)[:10])
    b=dt.date.fromisoformat(max(t['dt'] for t in T)[:10])
    nd=bdays(a,b)
    for lab,sel in [("all trades",T),("10:00 only",[t for t in T if t['dt'][11:16]=='10:00'])]:
        if not sel: continue
        net=sum(t['pnl'] for t in sel)
        print(f"{nm:22s} {lab:12s} {len(sel):5d} {net:+9.1f} {net/len(sel):+7.2f} {nd:6d} {net/nd:+8.2f}")
    print(f"{'':22s} range {a} .. {b}")
print("\ntarget = +10.00 pts/day")
