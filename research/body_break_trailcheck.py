import sys, math, statistics as st
sys.path.insert(0,'research')
import body_break_sweep as S
from collections import Counter
S.DO_MODE="proxy"

# A. which sessions can Logic A even arm on, in proxy mode?
print("A. WHY ONLY 2023+ : proxy dailyOpen comes from the session's FIRST bar.")
print("   If that first bar IS the 10:00 bar, then dailyOpen == its open, and")
print("     side=+1 needs min(o,c) > o  -> impossible")
print("     side=-1 needs max(o,c) < o  -> impossible")
print("   so side=0 and Logic A can NEVER arm on those sessions.")
elig=0; byyear=Counter()
for d in S.DAYS:
    bs=S.day_bars[d]
    if bs and (bs[0][0].hour,bs[0][0].minute)!=(10,0):
        elig+=1; byyear[d.year]+=1
print(f"   sessions with genuine pre-10:00 data: {elig} of {len(S.DAYS)}")
print(f"   by year: {dict(sorted(byyear.items()))}")

# B. the trailing exit: favourable-first vs conservative
def run_trail(conservative):
    out=[]
    for day in S.DAYS:
        bs=S.day_bars[day]
        sigs=S.signals(day,"A",True,False,16)
        for n,(s,e,idx,bh,bl,do) in enumerate(sigs):
            body=bh-bl; stop=do; risk=abs(e-stop)
            if risk<=0.5 or risk>80: continue
            trail=body*0.5
            stop_idx=sigs[n+1][2] if n+1<len(sigs) else None
            pnl=None; peak=e
            for j in range(idx+1,len(bs)):
                t,o,h,l,c=bs[j]
                if stop_idx is not None and j>=stop_idx:
                    pnl=s*(bs[stop_idx][4]-e); break
                adv=l if s>0 else h; fav=h if s>0 else l
                if s*(adv-stop)<=0: pnl=s*(stop-e); break
                ts=peak-s*trail
                if s*(adv-ts)<=0 and s*(ts-stop)>0:
                    pnl=s*(ts-e); break
                # update the peak AFTER testing the stop
                nf = c if conservative else fav     # conservative: peak can only move on a CLOSE
                if s*(nf-peak)>0: peak=nf
                if t.hour>=16: pnl=s*(c-e); break
            if pnl is None: pnl=s*(bs[-1][4]-e)
            out.append((day,s,pnl-S.COST,risk))
    return out

for lab,cons in (("favourable-first (as swept)",False),("conservative: peak moves only on CLOSE",True)):
    tr=run_trail(cons)
    p=[x[2] for x in tr]; g=sum(v for v in p if v>0); l=-sum(v for v in p if v<=0)
    eq=pk=dd=0.0
    for v in p: eq+=v; pk=max(pk,eq); dd=max(dd,pk-eq)
    m=sum(p)/len(p); sd=st.pstdev(p) or 1e-9
    print(f"\nB. {lab}")
    print(f"     n={len(p)} PF={g/l if l else 9.99:.3f} win={100*sum(1 for v in p if v>0)/len(p):.1f}% "
          f"net={sum(p):+.1f} avg={m:+.2f} maxDD={dd:.1f} MAR={sum(p)/dd if dd else 0:.2f} t={m/sd*math.sqrt(len(p)):+.2f}")
