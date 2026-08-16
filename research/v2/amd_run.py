import sys, math, statistics as st, random, itertools
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import amd, engine

bars = amd.load(amd.U + "c1e55d1f-au200_aud_1m_4.csv", True)
full, _ = amd.coverage(bars, "AU200 1m->5m")
ATR = amd.atr_series(bars)
half = len(full) // 2
IS, OOS = full[:half], full[half:]
print(f"\n[amd] testable cycles {len(full)}   IS {len(IS)} ({IS[0]}..{IS[-1]})"
      f"   OOS {len(OOS)} ({OOS[0]}..{OOS[-1]})")

res = []
for rr in (True, False):
    sg_is = amd.signals(bars, IS, rr)
    for sk in amd.STOPS:
        for xk in amd.EXITS:
            for be in (False, True):
                m = engine.metrics(amd.run(bars, sg_is, sk, xk, be, atr=ATR), min_n=30)
                if m:
                    res.append(((rr, sk, xk, be), m))
K = len(res)
BAR = math.sqrt(2 * math.log(K)) if K > 1 else 0
res.sort(key=lambda r: -r[1]["t"])
print(f"[amd] {K} cells with >=30 IS trades.  multiple-testing bar t >= {BAR:.2f}")
print(f"[amd] clearing it: {sum(1 for _, m in res if m['t'] >= BAR)}")
print(f"[amd] PF > 1.0: {sum(1 for _, m in res if m['pf'] > 1.0)} of {K} "
      f"({100*sum(1 for _,m in res if m['pf']>1.0)/max(1,K):.1f}%)")

print(f"\nTOP 12 BY IN-SAMPLE t, with out-of-sample beside it")
print(f"{'reentry':7} {'stop':9} {'exit':13} {'be':5} | {'IS n':>4} {'IS PF':>6} {'IS win':>6} "
      f"{'IS t':>6} | {'OOS n':>5} {'OOS PF':>6} {'OOS t':>6}")
for (rr, sk, xk, be), m in res[:12]:
    sg_o = amd.signals(bars, OOS, rr)
    mo = engine.metrics(amd.run(bars, sg_o, sk, xk, be, atr=ATR), min_n=20)
    print(f"{str(rr):7} {sk:9} {xk:13} {str(be):5} | {m['n']:>4} {m['pf']:>6.3f} "
          f"{m['win']:>5.1f}% {m['t']:>6.2f} | " +
          (f"{mo['n']:>5} {mo['pf']:>6.3f} {mo['t']:>6.2f}" if mo else f"{'--':>5} {'--':>6} {'--':>6}"))

print("\nFULL-SAMPLE BASELINE — no stop tuning, hold the whole distribution window:")
for rr in (True, False):
    sg = amd.signals(bars, full, rr)
    for c in (0.0, 2.0, 3.0):
        m = engine.metrics(amd.run(bars, sg, "fixed30", "session", False, cost=c, atr=ATR),
                           min_n=30, strict=False)
        if m:
            print(f"  reentry={str(rr):5} cost {c:>3.1f}  n={m['n']:4d} PF={m['pf']:6.3f} "
                  f"win={m['win']:5.1f}% net={m['net']:+8.1f} avg={m['avg']:+6.2f} t={m['t']:+5.2f}")

print("\nDOES THE SWEEP DIRECTION PREDICT THE DISTRIBUTION WINDOW? "
      "(zero cost, no stop, hold to window end)")
for rr in (True, False):
    sg = amd.signals(bars, full, rr)
    tr = amd.run(bars, sg, "fixed30", "session", False, cost=0.0, atr=ATR)
    p = [x["pnl"] for x in tr]
    hit = 100 * sum(1 for v in p if v > 0) / len(p)
    z = (hit/100 - 0.5) / math.sqrt(0.25/len(p))
    m, sd = st.mean(p), st.pstdev(p)
    print(f"  reentry={str(rr):5} n={len(p):4d}  accuracy {hit:5.2f}% (z={z:+5.2f})  "
          f"gross mean {m:+6.3f} pts (t={m/sd*math.sqrt(len(p)):+5.2f})")

print("\nSHUFFLE NULL — randomise the signal DIRECTION, compare against the search MAXIMUM")
real = max(m["t"] for _, m in res)
maxes = []
for trial in range(12):
    rng = random.Random(500 + trial)
    best = -9
    for (rr, sk, xk, be), _ in res[:60]:
        sg = [(k, (1 if rng.random() < .5 else -1), i) for k, s, i in amd.signals(bars, IS, rr)]
        m = engine.metrics(amd.run(bars, sg, sk, xk, be, atr=ATR), min_n=30, strict=False)
        if m:
            best = max(best, m["t"])
    maxes.append(best)
print(f"  real search maximum   : {real:+.2f}")
print(f"  shuffled maxima       : {', '.join(f'{v:+.2f}' for v in sorted(maxes))}")
print(f"  mean {st.mean(maxes):+.2f}   beat-or-matched real: "
      f"{sum(1 for v in maxes if v >= real)}/{len(maxes)}")
