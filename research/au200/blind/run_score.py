import sys, json, math, random, statistics as st
sys.path.insert(0,'research/au200'); sys.path.insert(0,'research/au200/blind')
import score as SC
from collections import Counter, defaultdict

key = SC.load_key()
A = {k: v["answer"] for k, v in json.load(open('research/au200/blind/CLAUDE_ANSWERS.json')).items()}
Apat = {k: v["patterns"] for k, v in json.load(open('research/au200/blind/CLAUDE_ANSWERS.json')).items()}
B = json.load(open('research/au200/blind/CLAUDE_ANSWERS_B.json'))

def wilson(w, n, z=1.96):
    if n == 0: return (float('nan'), float('nan'))
    p = w / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (100*(c-h), 100*(c+h))

def out(rec, d):
    t = rec["touch20"]
    if t in ("NONE","AMB"): return None
    return 1 if ((t=="UP") if d=="L" else (t=="DOWN")) else 0

def logicA_out(rec):
    t = rec["touch20"]
    if t in ("NONE","AMB"): return None
    return 1 if ((t=="UP") if rec["logicA"]=="LONG" else (t=="DOWN")) else 0

def blk(rows, lab, cost=1.0):
    d = [r for r in rows if r[1] is not None]
    if not d:
        print(f"  {lab:34} no resolved trades"); return None
    n = len(d); w = sum(r[1] for r in d)
    lo, hi = wilson(w, n)
    print(f"  {lab:34} n={n:>3}  win {100*w/n:>6.2f}%  CI [{lo:>5.1f},{hi:>5.1f}]  "
          f"gross {((w*20-(n-w)*20)/n):>+7.3f}  net@1pt {((w*(20-cost)-(n-w)*(20+cost))/n):>+7.3f}")
    return dict(n=n, w=w, wr=100*w/n)

print("="*104); print("SET A — STRICT (descriptive only, sample size is the headline)"); print("="*104)
selA = [(i, out(key[i], a[0])) for i, a in A.items() if a[0] in "LS"]
cA = Counter(a[0] for a in A.values())
print(f"  LONG {cA['L']}  SHORT {cA['S']}  NO TRADE {cA['N']}   selected {len(selA)}")
blk(selA, "Set A selected trades")
print("  Individual outcomes:")
for i, a in sorted(A.items()):
    if a[0] in "LS":
        o = out(key[i], a[0])
        print(f"    {i}  {a}  patterns {', '.join(Apat[i]) or '-'}  -> "
              f"{'WIN' if o==1 else ('LOSS' if o==0 else 'unresolved')}")
print("  8 trades gives a 95% interval roughly +-35 points. Nothing is concluded from this.")

print("\n"+"="*104); print("SET B — SCANNED (primary test, 46 selected trades)"); print("="*104)
cB = Counter(v[0] for v in B.values())
selB = [(i, out(key[i], v[0])) for i, v in B.items() if v[0] in "LS"]
print(f"  total charts 120   LONG {cB['L']}  SHORT {cB['S']}  NO TRADE {cB['N']}   selected {len(selB)}")
print("\n  --- OVERALL ---")
allB = blk(selB, "ALL selected")
print("\n  --- BY DIRECTION ---")
blk([(i,o) for i,o in selB if B[i][0]=="L"], "LONG calls")
blk([(i,o) for i,o in selB if B[i][0]=="S"], "SHORT calls")
print("\n  --- BY CONFIDENCE / TIER ---")
for c in "123":
    blk([(i,o) for i,o in selB if B[i][1]==c], f"confidence {c}")
print("\n  --- BY YEAR (years revealed only now) ---")
for y in range(2019, 2027):
    blk([(i,o) for i,o in selB if key[i]['date'][:4]==str(y)], f"{y}")
print("\n  --- DEV vs OOS ---")
blk([(i,o) for i,o in selB if int(key[i]['date'][:4])<=2023], "DEV 2019-2023")
blk([(i,o) for i,o in selB if int(key[i]['date'][:4])>=2024], "OOS 2024-2026")
