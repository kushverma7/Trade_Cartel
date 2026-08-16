"""STEP 4 — out-of-sample confirmation, cost sensitivity, Monte Carlo, plateau check.

Runs ONCE, after sweep.py. Self-contained: reloads the IS results from the
pickle and re-implements the cell runner so that importing this file never
re-runs the sweep.
"""
import sys, math, pickle, random, datetime as dt, statistics as st
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine

D = engine.Data()
SPLIT = dt.date(2025, 1, 1)
IS = [d for d in D.days if d < SPLIT]
OOS = [d for d in D.days if d >= SPLIT]
SIGCFG, RES, BAR = pickle.load(open("/home/user/Trade_Cartel/research/v2/sweep_is.pkl", "rb"))

_cache = {}
def sigs_for(si, d):
    if si not in _cache:
        sc = SIGCFG[si]
        fn = engine.SIGNALS[sc["sig"]]
        _cache[si] = {x: fn(D, x, sc) for x in D.days}
    return _cache[si][d]


def run(si, stop, exit_, be, days, cost=2.0):
    out = []
    for d in days:
        sg = sigs_for(si, d)
        if not sg:
            continue
        bs, adr = D.bars[d], D.ref[d]["adr"]
        for s, i, lv in sg:
            e = bs[i][4]
            if   stop == "ref":     sp = lv["ref"]
            elif stop == "adr0.25": sp = e - s * adr * 0.25
            elif stop == "adr0.5":  sp = e - s * adr * 0.5
            elif stop == "adr0.75": sp = e - s * adr * 0.75
            elif stop == "fixed10": sp = e - s * 10
            elif stop == "fixed20": sp = e - s * 20
            elif stop == "fixed30": sp = e - s * 30
            if s * (e - sp) <= 0:                     # R8: stop must be adverse
                continue
            risk = abs(e - sp)
            if risk < 3.0 or risk > 80.0:
                continue
            tp = trail = None
            if   exit_ == "1R":   tp = e + s * risk
            elif exit_ == "1.5R": tp = e + s * risk * 1.5
            elif exit_ == "2R":   tp = e + s * risk * 2
            elif exit_ == "3R":   tp = e + s * risk * 3
            elif exit_ == "adr0.5": tp = e + s * adr * 0.5
            elif exit_ == "adr1.0": tp = e + s * adr * 1.0
            elif exit_ == "trail_adr0.3": trail = adr * 0.3
            elif exit_ == "trail_adr0.5": trail = adr * 0.5
            pnl, why, held = engine.resolve(bs, i, s, e, sp, tp, trail,
                                            (risk * 0.5 if be == "half" else None),
                                            955, cost)
            out.append(dict(day=d, s=s, pnl=pnl, risk=risk, why=why, held=held))
    return out


def monte(tr, runs=10000, seed=7):
    rng = random.Random(seed)
    p = [t["pnl"] for t in tr]
    nets, dds = [], []
    for _ in range(runs):
        s = [p[rng.randrange(len(p))] for _ in range(len(p))]
        eq = pk = dd = 0.0
        for v in s:
            eq += v; pk = max(pk, eq); dd = max(dd, pk - eq)
        nets.append(eq); dds.append(dd)
    nets.sort(); dds.sort()
    q = lambda a, f: a[int(f * (len(a) - 1))]
    tot = sum(p)
    thr = 0.15 * abs(tot) if tot else 1e9
    return dict(p05=q(nets, .05), p50=q(nets, .50), p95=q(nets, .95),
                dd50=q(dds, .50), dd95=q(dds, .95),
                p_profit=100 * sum(1 for v in nets if v > 0) / runs,
                p_dd15=100 * sum(1 for v in dds if v >= thr) / runs)


def lab(si):
    return " ".join(f"{k}={v}" for k, v in SIGCFG[si].items() if k != "or_floor")


if __name__ == "__main__":
    clears = [r for r in RES if r[4]["t"] >= BAR]
    print(f"IS cells: {len(RES)}   bar t>={BAR:.2f}   clearing: {len(clears)}")
    cands = clears if clears else RES[:10]
    if not clears:
        print("\nNO CELL CLEARS THE IN-SAMPLE BAR. Reporting the top 10 by IS t anyway,\n"
              "explicitly as NOT significant, and testing them out of sample so the\n"
              "record shows what they did rather than leaving it unstated.\n")
    print(f"{'signal':38} {'stop':8} {'exit':13} {'be':5} | "
          f"{'IS n':>5} {'IS PF':>6} {'IS t':>6} | {'OOS n':>5} {'OOS PF':>6} "
          f"{'OOS t':>6} {'OOS net':>8}")
    keep = []
    for si, stop, exit_, be, mis in cands:
        mo = engine.metrics(run(si, stop, exit_, be, OOS), min_n=20)
        print(f"{lab(si):38.38} {stop:8} {exit_:13} {str(be):5} | "
              f"{mis['n']:>5} {mis['pf']:>6.3f} {mis['t']:>6.2f} | " +
              (f"{mo['n']:>5} {mo['pf']:>6.3f} {mo['t']:>6.2f} {mo['net']:>8.1f}"
               if mo else f"{'--':>5} {'--':>6} {'--':>6} {'--':>8}"))
        if mo:
            keep.append((si, stop, exit_, be, mis, mo))

    if not keep:
        print("\nno candidate produced >=20 out-of-sample trades.")
        sys.exit()

    best = max(keep, key=lambda r: r[5]["t"])
    si, stop, exit_, be, mis, mo = best
    print(f"\n{'='*78}\nBEST BY OUT-OF-SAMPLE t: {lab(si)}  stop={stop} exit={exit_} be={be}\n{'='*78}")
    full = run(si, stop, exit_, be, D.days)
    mf = engine.metrics(full)
    print(f"FULL SAMPLE  n={mf['n']}  PF={mf['pf']:.3f}  win={mf['win']:.1f}%  "
          f"net={mf['net']:+.1f} pts  maxDD={mf['dd']:.1f}  t={mf['t']:+.2f}  "
          f"avgR={mf['avgR']:+.3f}  years positive {mf['yp']}/{mf['ny']}")
    print(f"  fill assumption: entry at the signal bar's 5-minute CLOSE, exits "
          f"resolved on 5-minute bars with the adverse extreme taken first, "
          f"2.0 points cost per trade.")

    print("\nCOST SENSITIVITY (full sample)")
    for c in (2.0, 2.5, 3.0, 4.0):
        m = engine.metrics(run(si, stop, exit_, be, D.days, cost=c))
        print(f"  cost {c:>4.1f}  n={m['n']:4d} PF={m['pf']:6.3f} win={m['win']:5.1f}% "
              f"net={m['net']:+9.1f} t={m['t']:+6.2f}")

    print("\nMONTE CARLO — 10,000 bootstrap resamples of the full-sample trade list")
    for c in (2.0, 3.0):
        tr = run(si, stop, exit_, be, D.days, cost=c)
        mc = monte(tr)
        print(f"  cost {c:.1f}: median {mc['p50']:+9.1f}  5th {mc['p05']:+9.1f}  "
              f"95th {mc['p95']:+9.1f}  medianDD {mc['dd50']:7.1f}  95thDD {mc['dd95']:7.1f}")
        print(f"            P(profit) {mc['p_profit']:5.1f}%   "
              f"P(drawdown >= 15% of net) {mc['p_dd15']:5.1f}%")

    print("\nPARAMETER NEIGHBOURHOOD — plateau or spike?")
    for s2 in ["ref", "adr0.25", "adr0.5", "adr0.75", "fixed10", "fixed20", "fixed30"]:
        m = engine.metrics(run(si, s2, exit_, be, D.days))
        mark = " <-- chosen" if s2 == stop else ""
        print(f"  stop={s2:8} " + (f"n={m['n']:4d} PF={m['pf']:6.3f} t={m['t']:+6.2f}"
                                   if m else "insufficient") + mark)
    for e2 in ["1R", "1.5R", "2R", "3R", "adr0.5", "adr1.0", "trail_adr0.3", "trail_adr0.5", "time"]:
        m = engine.metrics(run(si, stop, e2, be, D.days))
        mark = " <-- chosen" if e2 == exit_ else ""
        print(f"  exit={e2:13} " + (f"n={m['n']:4d} PF={m['pf']:6.3f} t={m['t']:+6.2f}"
                                    if m else "insufficient") + mark)
