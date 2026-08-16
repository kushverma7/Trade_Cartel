"""STEP 3 — the sweep. Runs only after selftest.py exits 0.

IS  = 2020-08-25 .. 2024-12-31   (in sample, used for selection)
OOS = 2025-01-01 .. 2026-08-03   (out of sample, LOOKED AT ONCE, at the end)

Selection is made on IS only. The multiple-testing bar is computed from the
number of cells that produced enough trades, and applied to IS t.
"""
import sys, math, itertools, datetime as dt, statistics as st, pickle
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine
from collections import defaultdict

D = engine.Data()
SPLIT = dt.date(2025, 1, 1)
IS = [d for d in D.days if d < SPLIT]
OOS = [d for d in D.days if d >= SPLIT]
print(f"[sweep] IS {len(IS)} sessions ({IS[0]}..{IS[-1]})   "
      f"OOS {len(OOS)} sessions ({OOS[0]}..{OOS[-1]})")

# ---- signal configs -------------------------------------------------------
SIGCFG = []
for mode in ("cont", "fade"):
    for thr, rel in ((0.25, True), (0.5, True), (10.0, False), (20.0, False)):
        for delay in (0, 15, 30):
            SIGCFG.append(dict(sig="gap", mode=mode, gap_thr=thr, gap_rel=rel,
                               delay=delay, cutoff=840))
for mode in ("cont", "fade"):
    for om in (15, 30, 45, 60):
        for cut in (720, 780, 840):
            SIGCFG.append(dict(sig="orb", mode=mode, or_min=om, or_floor=3.0, cutoff=cut))
for cut in (720, 780, 840):
    SIGCFG.append(dict(sig="body", mode="cont", cutoff=cut))
for mode in ("cont", "fade"):
    for cut in (720, 780, 840):
        SIGCFG.append(dict(sig="pdhl", mode=mode, cutoff=cut))
print(f"[sweep] {len(SIGCFG)} signal configurations")

# precompute signals once per config per day
CACHE = {}
for si, sc in enumerate(SIGCFG):
    fn = engine.SIGNALS[sc["sig"]]
    CACHE[si] = {d: fn(D, d, sc) for d in D.days}
print(f"[sweep] signals precomputed")

STOPS = ["ref", "adr0.25", "adr0.5", "adr0.75", "fixed10", "fixed20", "fixed30"]
EXITS = ["1R", "1.5R", "2R", "3R", "adr0.5", "adr1.0", "trail_adr0.3", "trail_adr0.5", "time"]
BES = [None, "half"]
COST = 2.0
print(f"[sweep] grid = {len(SIGCFG)} x {len(STOPS)} x {len(EXITS)} x {len(BES)} = "
      f"{len(SIGCFG)*len(STOPS)*len(EXITS)*len(BES)} cells")


def run(si, stop, exit_, be, days):
    sc = SIGCFG[si]
    out = []
    for d in days:
        sigs = CACHE[si][d]
        if not sigs:
            continue
        bs, r = D.bars[d], D.ref[d]
        adr = r["adr"]
        for s, i, lv in sigs:
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
                                            955, COST)
            out.append(dict(day=d, s=s, pnl=pnl, risk=risk, why=why, held=held))
    return out


res = []
for si in range(len(SIGCFG)):
    for stop in STOPS:
        for exit_ in EXITS:
            for be in BES:
                mis = engine.metrics(run(si, stop, exit_, be, IS), min_n=60)
                if mis:
                    res.append((si, stop, exit_, be, mis))
    if si % 10 == 0:
        print(f"  .. signal config {si+1}/{len(SIGCFG)}  cells kept {len(res)}", flush=True)

K = len(res)
BAR = math.sqrt(2 * math.log(K))
print(f"\n[sweep] {K} cells produced >=60 IS trades.  multiple-testing bar t >= "
      f"sqrt(2 ln {K}) = {BAR:.2f}")
res.sort(key=lambda r: -r[4]["t"])
print(f"[sweep] cells clearing the bar on IS: {sum(1 for r in res if r[4]['t'] >= BAR)}")
print(f"[sweep] cells with IS PF > 1.0: {sum(1 for r in res if r[4]['pf'] > 1.0)} "
      f"({100*sum(1 for r in res if r[4]['pf']>1.0)/K:.1f}%)")

print(f"\nTOP 20 BY IN-SAMPLE t  (OOS column computed but NOT used for ranking)")
print(f"{'#':>3} {'signal':38} {'stop':8} {'exit':13} {'be':5} "
      f"{'n':>5} {'PF':>6} {'win%':>5} {'net':>8} {'t':>6} {'yrs+':>5}")
for i, (si, stop, exit_, be, m) in enumerate(res[:20], 1):
    sc = SIGCFG[si]
    lab = " ".join(f"{k}={v}" for k, v in sc.items() if k not in ("or_floor",))
    print(f"{i:>3} {lab:38.38} {stop:8} {exit_:13} {str(be):5} "
          f"{m['n']:>5} {m['pf']:>6.3f} {m['win']:>5.1f} {m['net']:>8.1f} "
          f"{m['t']:>6.2f} {m['yp']}/{m['ny']}")

pickle.dump((SIGCFG, res, BAR), open("/home/user/Trade_Cartel/research/v2/sweep_is.pkl", "wb"))
print("\n[sweep] IS results saved. OOS not yet examined.")
