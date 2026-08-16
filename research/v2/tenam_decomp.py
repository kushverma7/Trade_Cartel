"""Is the 10:00 candle a real signal being eaten by costs, or no signal at all?

Run the same trades at zero cost. If gross expectancy is positive and net is
negative, there is a signal and the problem is execution. If gross expectancy is
~0 or negative, there is nothing there and no amount of tuning helps.

Then: a direction-shuffle null tested against the MAXIMUM of the search, not the
mean, so the comparison accounts for the fact that 2,620 cells were searched.
"""
import sys, math, random, statistics as st, datetime as dt
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine, tenam as T
from collections import defaultdict

D, C = T.D, T.C

print("\n" + "=" * 84)
print("A. GROSS vs NET — the 10:00 candle direction, no filter, no stop, all "
      f"{len(D.days)} sessions")
print("=" * 84)
print(f"{'horizon':8} {'mode':5} | {'gross avg':>10} {'gross PF':>9} {'gross t':>8} | "
      f"{'net avg':>8} {'net PF':>7}")
for ex in ("hold1", "hold3", "hold6", "hold12", "eod"):
    for mode in ("cont", "fade"):
        g = engine.metrics(T.run(mode, "none", "fixed30", ex, None, D.days, cost=0.0),
                           min_n=60, strict=False)
        n = engine.metrics(T.run(mode, "none", "fixed30", ex, None, D.days, cost=2.0),
                           min_n=60, strict=False)
        print(f"{ex:8} {mode:5} | {g['avg']:>+10.3f} {g['pf']:>9.3f} {g['t']:>+8.2f} | "
              f"{n['avg']:>+8.2f} {n['pf']:>7.3f}")

print("\n" + "=" * 84)
print("B. DOES THE 10:00 CANDLE PREDICT ANYTHING? Directional accuracy of the")
print("   candle's sign against the next N bars' return, zero cost, no stops.")
print("=" * 84)
for nb in (1, 2, 3, 6, 12, 24, 71):
    hit = tot = 0
    rets = []
    for d in D.days:
        bs, x = D.bars[d], C[d]
        if x["body"] == 0 or len(bs) <= nb:
            continue
        fwd = bs[min(nb, len(bs) - 1)][4] - x["c"]
        s = 1 if x["body"] > 0 else -1
        tot += 1
        hit += 1 if s * fwd > 0 else 0
        rets.append(s * fwd)
    p = hit / tot
    se = math.sqrt(0.25 / tot)
    z = (p - 0.5) / se
    m, sd = st.mean(rets), st.pstdev(rets)
    print(f"  next {nb:2d} bars ({5*nb:3d} min): accuracy {100*p:5.2f}%  z={z:+5.2f}   "
          f"mean signed move {m:+6.3f} pts (t={m/sd*math.sqrt(len(rets)):+5.2f})  n={tot}")

print("\n" + "=" * 84)
print("C. SHUFFLE NULL — is the best of 2,620 cells better than the best of a")
print("   search over randomised directions? Compared against the MAXIMUM.")
print("=" * 84)
import pickle
res, BAR = pickle.load(open("/home/user/Trade_Cartel/research/v2/tenam_is.pkl", "rb"))
real_max = max(m["t"] for _, m in res)
SPLIT = dt.date(2025, 1, 1)
IS = [d for d in D.days if d < SPLIT]
CELLS = [c for c, _ in res[:120]]           # the 120 strongest real cells
maxes = []
for trial in range(12):
    rng = random.Random(1000 + trial)
    flip = {d: (1 if rng.random() < .5 else -1) for d in D.days}
    orig = {}
    for d in D.days:
        orig[d] = C[d]["body"]
        C[d]["body"] = abs(C[d]["body"]) * flip[d]
    best = -9
    for cfg in CELLS:
        m = engine.metrics(T.run(*cfg, IS), min_n=60, strict=False)
        if m:
            best = max(best, m["t"])
    maxes.append(best)
    for d in D.days:
        C[d]["body"] = orig[d]
print(f"  real search maximum IS t         : {real_max:+.2f}")
print(f"  shuffled-direction search maxima : "
      f"{', '.join(f'{v:+.2f}' for v in sorted(maxes))}")
print(f"  mean {st.mean(maxes):+.2f}, max {max(maxes):+.2f}")
beat = sum(1 for v in maxes if v >= real_max)
print(f"  shuffles whose maximum matched or beat the real one: {beat}/{len(maxes)}")
print("\n  A real edge must beat the SHUFFLED MAXIMUM, not the shuffled mean —"
      "\n  otherwise it is only beating a coin that was flipped once.")
