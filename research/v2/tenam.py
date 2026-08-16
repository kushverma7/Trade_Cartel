"""THE 10:00 CANDLE — exhaustive study, AU200 5-minute, full sample.

The signal object is the 10:00-10:05 Melbourne candle and nothing else. This
needs no 09:50 bar, so it runs on every session with a 10:00 open: 1,489
sessions, six years, rather than the 173 that carry a pre-open print.

ONE TRADE PER SESSION. Entry at the 10:00 candle's CLOSE (= the 10:05 bar's
open), which is the first tradeable instant after the candle exists.

All nine engine rules apply. IS/OOS split fixed before ranking.
"""
import sys, math, itertools, datetime as dt, statistics as st, pickle
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine
from collections import defaultdict

D = engine.Data()
SPLIT = dt.date(2025, 1, 1)
IS = [d for d in D.days if d < SPLIT]
OOS = [d for d in D.days if d >= SPLIT]
print(f"[10am] IS {len(IS)} sessions   OOS {len(OOS)} sessions")

# ---- characterise the 10:00 candle on every session -----------------------
C = {}
for d in D.days:
    b = D.bars[d][0]                       # the 10:00 bar
    mn, o, h, l, c, v = b
    assert mn == 600
    rng = h - l
    C[d] = dict(o=o, h=h, l=l, c=c, body=c - o, absbody=abs(c - o), rng=rng,
                ratio=(abs(c - o) / rng if rng > 0 else 0.0),
                gap=o - D.ref[d]["prev_close"], adr=D.ref[d]["adr"])
bodies = sorted(x["absbody"] for x in C.values())
BMED = bodies[len(bodies) // 2]
ratios = sorted(x["ratio"] for x in C.values())
RMED = ratios[len(ratios) // 2]
print(f"[10am] 10:00 candle: median |body| {BMED:.2f} pts, median body/range "
      f"{RMED:.2f}, median range {st.median([x['rng'] for x in C.values()]):.2f} pts")

FILTERS = {
    "none":        lambda x: True,
    "body>med":    lambda x: x["absbody"] > BMED,
    "body<med":    lambda x: x["absbody"] <= BMED,
    "ratio>med":   lambda x: x["ratio"] > RMED,
    "gap_aligned": lambda x: x["gap"] * x["body"] > 0,
    "gap_opposed": lambda x: x["gap"] * x["body"] < 0,
}
STOPS = ["candle_far", "candle_far2", "body_1x", "adr0.25", "adr0.5",
         "fixed10", "fixed20", "fixed30"]
EXITS = ["1R", "1.5R", "2R", "3R", "fixed10", "fixed20", "adr0.5",
         "trail_adr0.3", "trail_body", "hold1", "hold3", "hold6", "hold12", "eod"]
BES = [None, "half"]


def run(mode, filt, stop, exit_, be, days, cost=2.0):
    f = FILTERS[filt]
    tr = []
    for d in days:
        x = C[d]
        if x["body"] == 0 or not f(x):
            continue
        bs = D.bars[d]
        if len(bs) < 3:
            continue
        s = (1 if x["body"] > 0 else -1) * (1 if mode == "cont" else -1)
        e = x["c"]
        adr = x["adr"]
        if   stop == "candle_far":  sp = x["l"] if s > 0 else x["h"]
        elif stop == "candle_far2": sp = (x["l"] - 2) if s > 0 else (x["h"] + 2)
        elif stop == "body_1x":     sp = e - s * max(x["absbody"], 1.0)
        elif stop == "adr0.25":     sp = e - s * adr * 0.25
        elif stop == "adr0.5":      sp = e - s * adr * 0.5
        elif stop == "fixed10":     sp = e - s * 10
        elif stop == "fixed20":     sp = e - s * 20
        elif stop == "fixed30":     sp = e - s * 30
        if s * (e - sp) <= 0:                                  # R8
            continue
        risk = abs(e - sp)
        if risk < 3.0 or risk > 80.0:                          # R5
            continue
        tp = trail = None
        deadline = 955
        if   exit_ == "1R":   tp = e + s * risk
        elif exit_ == "1.5R": tp = e + s * risk * 1.5
        elif exit_ == "2R":   tp = e + s * risk * 2
        elif exit_ == "3R":   tp = e + s * risk * 3
        elif exit_ == "fixed10": tp = e + s * 10
        elif exit_ == "fixed20": tp = e + s * 20
        elif exit_ == "adr0.5":  tp = e + s * adr * 0.5
        elif exit_ == "trail_adr0.3": trail = adr * 0.3
        elif exit_ == "trail_body":   trail = max(x["absbody"], 1.0)
        elif exit_.startswith("hold"): deadline = 600 + 5 * int(exit_[4:])
        pnl, why, held = engine.resolve(bs, 0, s, e, sp, tp, trail,
                                        (risk * 0.5 if be == "half" else None),
                                        deadline, cost)
        tr.append(dict(day=d, s=s, pnl=pnl, risk=risk, why=why, held=held))
    return tr


res = []
for mode in ("cont", "fade"):
    for filt in FILTERS:
        for stop in STOPS:
            for exit_ in EXITS:
                for be in BES:
                    m = engine.metrics(run(mode, filt, stop, exit_, be, IS), min_n=60)
                    if m:
                        res.append(((mode, filt, stop, exit_, be), m))
K = len(res)
BAR = math.sqrt(2 * math.log(K))
res.sort(key=lambda r: -r[1]["t"])
print(f"\n[10am] {K} cells with >=60 IS trades.  multiple-testing bar t >= {BAR:.2f}")
print(f"[10am] clearing the bar: {sum(1 for _, m in res if m['t'] >= BAR)}")
print(f"[10am] PF > 1.0: {sum(1 for _, m in res if m['pf'] > 1.0)} of {K} "
      f"({100*sum(1 for _, m in res if m['pf'] > 1.0)/K:.1f}%)")

print(f"\nTOP 15 BY IN-SAMPLE t, with the out-of-sample result beside it")
print(f"{'mode':5} {'filter':12} {'stop':12} {'exit':13} {'be':5} | "
      f"{'IS n':>5} {'IS PF':>6} {'IS win':>6} {'IS t':>6} | "
      f"{'OOS n':>5} {'OOS PF':>6} {'OOS t':>6}")
for cfg, m in res[:15]:
    mo = engine.metrics(run(*cfg, OOS), min_n=20)
    print(f"{cfg[0]:5} {cfg[1]:12} {cfg[2]:12} {cfg[3]:13} {str(cfg[4]):5} | "
          f"{m['n']:>5} {m['pf']:>6.3f} {m['win']:>5.1f}% {m['t']:>6.2f} | " +
          (f"{mo['n']:>5} {mo['pf']:>6.3f} {mo['t']:>6.2f}" if mo
           else f"{'--':>5} {'--':>6} {'--':>6}"))

print("\nDIRECTIONAL BASELINE — the 10:00 candle with no filter, no stop, "
      "held to a fixed horizon, costs on:")
for exit_ in ("hold1", "hold3", "hold6", "hold12", "eod"):
    for mode in ("cont", "fade"):
        m = engine.metrics(run(mode, "none", "fixed30", exit_, None, D.days), min_n=60)
        if m:
            print(f"  {mode:5} {exit_:6} n={m['n']:4d} PF={m['pf']:6.3f} "
                  f"win={m['win']:5.1f}% net={m['net']:+8.1f} avg={m['avg']:+5.2f} "
                  f"t={m['t']:+5.2f} yrs+={m['yp']}/{m['ny']}")

pickle.dump((res, BAR), open("/home/user/Trade_Cartel/research/v2/tenam_is.pkl", "wb"))
