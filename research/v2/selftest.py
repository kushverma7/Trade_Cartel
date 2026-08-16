"""STEP 2 — engine self-test. The sweep does not run until all four pass.

T1  NULL, ZERO COST: randomise the trade direction with costs off. A correct
    execution model has no directional bias, so mean t must be ~0. (Run WITH
    costs this measures cost drag, not the harness — that was the first
    version's error.)
T2  INJECTED EDGE: a deterministic post-10:30 drift must be recovered.
T3  COST MONOTONICITY: net must fall by exactly n*dc.
T4  RANDOM WALK: on a synthetic driftless series with matched volatility, a
    stop/target rule must return PF ~1.0 at zero cost. This is the test that
    catches an execution model which silently favours one side.
"""
import sys, random, math, statistics as st
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine

BASE = dict(sig="orb", mode="cont", or_min=30, or_floor=3.0, cutoff=840,
            stop="adr0.5", exit="2R", min_risk=3.0, max_risk=80.0,
            deadline=955, cost=2.0)

D = engine.Data()
ok = True

# ---------------------------------------------------------------- T1  null, zero cost
tr0 = engine.backtest(D, dict(BASE, cost=0.0))
rng = random.Random(1)
ts = []
for _ in range(300):
    flip = [dict(t, pnl=(t["pnl"] if rng.random() < .5 else -t["pnl"])) for t in tr0]
    ts.append(engine.metrics(flip)["t"])
mu, sd = st.mean(ts), st.pstdev(ts)
p1 = abs(mu) < 0.5
print(f"T1 NULL (cost 0)  direction randomised, 300 draws: mean t = {mu:+.3f} "
      f"(sd {sd:.2f})   {'PASS' if p1 else 'FAIL'}")
ok &= p1

# ---------------------------------------------------------------- T2  injected edge
DRIFT = 0.40
D2 = engine.Data()
for d in D2.days:
    new, add = [], 0.0
    for b in D2.bars[d]:
        if b[0] > 630:
            add += DRIFT
        new.append((b[0], b[1] + add, b[2] + add, b[3] + add, b[4] + add, b[5]))
    D2.bars[d] = new
LONG = dict(BASE, exit="time", stop="fixed30", min_risk=1.0, cost=0.0)
mb = engine.metrics(engine.backtest(D, LONG))
mi = engine.metrics(engine.backtest(D2, LONG))
p2 = mi["t"] > mb["t"] + 5 and mi["net"] > mb["net"]
print(f"T2 INJECTED EDGE  +{DRIFT} pts/bar after 10:30, costs off")
print(f"     clean    n={mb['n']:4d} PF={mb['pf']:5.3f} net={mb['net']:+9.1f} t={mb['t']:+6.2f}")
print(f"     injected n={mi['n']:4d} PF={mi['pf']:5.3f} net={mi['net']:+9.1f} t={mi['t']:+6.2f}"
      f"   {'PASS' if p2 else 'FAIL'}")
ok &= p2

# ---------------------------------------------------------------- T3  cost
a = engine.backtest(D, dict(BASE, cost=0.0))
b = engine.backtest(D, dict(BASE, cost=3.0))
exp = -3.0 * len(a)
got = sum(t["pnl"] for t in b) - sum(t["pnl"] for t in a)
p3 = len(a) == len(b) and abs(got - exp) < 1e-6
print(f"T3 COST           n={len(a)} unchanged, delta = {got:+.1f} (expected {exp:+.1f})"
      f"   {'PASS' if p3 else 'FAIL'}")
ok &= p3

# ---------------------------------------------------------------- T4  random walk
def synth(seed):
    r = random.Random(seed)
    S = engine.Data.__new__(engine.Data)
    S.tf, S.bars, S.ref = 5, {}, {}
    steps = [b[2] - b[3] for d in D.days[:200] for b in D.bars[d]]
    sig = st.mean(steps) / 2
    prev_c = 6000.0
    prev = None
    hist = []
    for d in D.days:
        n = len(D.bars[d])
        bs, px = [], prev_c
        for k in range(n):
            o = px
            moves = [r.gauss(0, sig) for _ in range(4)]
            path = [o]
            for mv in moves:
                path.append(path[-1] + mv)
            bs.append((D.bars[d][k][0], o, max(path), min(path), path[-1], 1.0))
            px = path[-1]
        S.bars[d] = bs
        rf = {"open10": bs[0][1], "adr": st.mean(hist[-14:]) if len(hist) >= 14 else None}
        if prev is not None:
            p = S.bars[prev]
            rf.update(prev_close=p[-1][4], prev_high=max(x[2] for x in p),
                      prev_low=min(x[3] for x in p))
            rf["prev_mid"] = (rf["prev_high"] + rf["prev_low"]) / 2
        S.ref[d] = rf
        hist.append(max(x[2] for x in bs) - min(x[3] for x in bs))
        prev_c = bs[-1][4]
        prev = d
    S.days = [d for d in D.days if "prev_close" in S.ref[d] and S.ref[d]["adr"] is not None]
    return S

pfs = []
for sd_ in range(6):
    m = engine.metrics(engine.backtest(synth(sd_), dict(BASE, cost=0.0)))
    pfs.append(m["pf"])
mpf = st.mean(pfs)
p4 = 0.92 < mpf < 1.08
print(f"T4 RANDOM WALK    6 synthetic driftless series, PF = "
      f"{', '.join(f'{v:.3f}' for v in pfs)}  mean {mpf:.3f}   {'PASS' if p4 else 'FAIL'}")
ok &= p4

print("\nSELF-TEST:", "ALL PASS — sweep may run" if ok else "FAILED — sweep must not run")
sys.exit(0 if ok else 1)
