import csv, datetime as dt, zoneinfo
from collections import Counter, defaultdict
D="/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"
MEL=zoneinfo.ZoneInfo("Australia/Sydney")
def load(fn):
    tr={}
    for r in csv.DictReader(open(fn,encoding='utf-8-sig')):
        n=int(r['Trade number']); tr.setdefault(n,{})
        if r['Type'].startswith('Entry'):
            tr[n]['dt']=r['Date and time']; tr[n]['dir']='long' if 'long' in r['Type'] else 'short'
    return [v for v in tr.values() if 'dt' in v]
ts=load(D+"6404634b-AU200BASE_OANDA_AU200AUD_20260811_3.csv")

# (a) Is the 10:00 / 11:00 split daylight saving?
mon=defaultdict(Counter)
for t in ts:
    m=int(t['dt'][5:7]); mon[t['dt'][11:16]][m]+=1
print("Entries by month  (1=Jan ... 12=Dec)")
for clock in sorted(mon):
    print(f"  {clock}: " + " ".join(f"{m}:{mon[clock][m]:3d}" for m in range(1,13)))
same=Counter(t['dt'][:10] for t in ts)
print(f"\n  days with BOTH a 10:00 and an 11:00 entry: {sum(1 for d,c in same.items() if c>1)}")
print(f"  total distinct days: {len(same)}   total trades: {len(ts)}")

# (b) do MY reconstructed signals match THEIR trade list?
import importlib.util
src=open("research/au200_base_honest.py").read().split("# minute index")[0]
g={}; exec(src,g)
bars=g['build'](60); ema,rsi,dirn=g['indicators'](bars)
FIX10=dt.timezone(dt.timedelta(hours=10))
mine={}
for i,b in enumerate(bars):
    if ema[i] is None or rsi[i] is None or dirn[i] is None: continue
    lt=b[0].astimezone(FIX10)
    if (lt.hour,lt.minute)!=(10,0): continue
    c=b[4]
    if c>ema[i] and rsi[i]>50 and dirn[i]<0: mine[b[0].astimezone(MEL).date()]='long'
    elif c<ema[i] and rsi[i]<50 and dirn[i]>0: mine[b[0].astimezone(MEL).date()]='short'
theirs={dt.date.fromisoformat(t['dt'][:10]):t['dir'] for t in ts
        if t['dt'][:10]>="2025-01-14"}
allbars={b[0].astimezone(MEL).date() for b in bars if ema[bars.index(b)] is not None} if False else None
days=sorted(set(theirs)|set(mine))
both=[d for d in days if d in theirs and d in mine]
agree=[d for d in both if theirs[d]==mine[d]]
print(f"\nENTRY RECONSTRUCTION vs their trade list, {days[0]} .. {days[-1]}")
print(f"  days they traded : {len(theirs)}")
print(f"  days I traded    : {len(mine)}")
print(f"  both traded      : {len(both)}   direction agrees: {len(agree)} ({100*len(agree)/max(1,len(both)):.1f}%)")
print(f"  they traded, I did not: {len([d for d in theirs if d not in mine])}")
print(f"  I traded, they did not: {len([d for d in mine if d not in theirs])}")
