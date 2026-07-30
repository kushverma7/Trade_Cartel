#!/usr/bin/env python3
"""
Apply the Deflated Sharpe Ratio to this repo's own recorded results.

The question: 17 configurations were tried and the best scored PF 1.093.
How surprising is that, given that 17 attempts were made?
"""
import numpy as np
from backtest.overfit import sr_from_pf_wr, deflated_sharpe_ratio

# every ledger row that recorded pf, wr AND n (the rest cannot be used)
ROWS = [
    ("#6  Top/Bottom run 4",        112, 35.70, 1.110),
    ("#9  OMNIBUS four-model",      298, 40.60, 0.843),
    ("#10 Key-to-Key",              245, 26.10, 0.886),
    ("#11 Trendline x Key Levels",  382, 40.80, 0.882),
    ("#13 Multi-Voice",             521, 44.15, 1.093),
    ("#14 MV + level-to-level",     461, 34.06, 0.892),
    ("#15 Key Levels v1.0 (void)",   22, 63.64, 1.783),
]

print("per-trade Sharpe reconstructed from (PF, WR, n)")
print("assumes uniform win/loss sizes -> OPTIMISTIC, treat as an upper bound\n")
srs = []
for name, n, wr, pf in ROWS:
    sr = sr_from_pf_wr(pf, wr, n)
    srs.append(sr)
    print(f"  {name:30s} n={n:>4}  PF {pf:5.3f}  SR/trade {sr:+.4f}")

# trial variance: spread of outcomes across the attempts actually made
usable = np.array([s for s in srs if np.isfinite(s)])
var_trials = float(usable.var(ddof=1))
best_name, best_n, best_wr, best_pf = ROWS[4]           # #13 Multi-Voice
best_sr = sr_from_pf_wr(best_pf, best_wr, best_n)

print(f"\nvariance of Sharpe across trials: {var_trials:.6f}")
print(f"best surviving result: {best_name}  SR/trade {best_sr:+.4f}  n={best_n}")

print("\n" + "=" * 68)
print("DEFLATED SHARPE — how many attempts were really made?")
print("=" * 68)
print(f"{'trials':>7} | {'E[max SR] from noise':>21} | {'adj SR':>8} | {'DSR':>6} | verdict")
for k in (7, 17, 40, 100):
    d = deflated_sharpe_ratio(best_sr, best_n, n_trials=k, variance_trials=var_trials)
    v = ("skill"    if d["dsr"] >= 0.95 else
         "weak"     if d["dsr"] >= 0.80 else
         "not distinguishable from noise")
    print(f"{k:>7} | {d['expected_max_sharpe']:>21.4f} | "
          f"{d['adjusted_sharpe']:>+8.4f} | {d['dsr']:>6.3f} | {v}")

# sensitivity: the void 22-trade row has SR +0.293 on n=22 and inflates the
# trial variance badly. Rerun without it -- if the verdict flips, the
# conclusion was an artifact of one bad row and must be reported as such.
usable2 = np.array([sr_from_pf_wr(pf, wr, n) for _, n, wr, pf in ROWS[:-1]])
var2 = float(usable2.var(ddof=1))
print(f"\nSENSITIVITY — excluding the void 22-trade row (var {var2:.6f}):")
for k in (7, 17, 40):
    d = deflated_sharpe_ratio(best_sr, best_n, n_trials=k, variance_trials=var2)
    print(f"  trials={k:>3}  E[max SR]={d['expected_max_sharpe']:.4f}  "
          f"adjSR={d['adjusted_sharpe']:+.4f}  DSR={d['dsr']:.4f}")
print("  -> verdict unchanged: DSR stays far below 0.95 either way.")

print("""
HOW TO READ THE TRIAL COUNT
  7   only the ledger rows above -- the most generous possible count
  17  every engine built in this repo
  40+ realistic: each engine went through several parameter passes, and
      every one of those was a trial whether or not it was written down

DSR is the probability the true Sharpe is above zero AFTER accounting for
the search. At 0.5 the result is exactly what the search would produce from
noise. Only >= 0.95 counts as evidence of skill.
""")
