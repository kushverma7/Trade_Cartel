"""Control for the Q1 -> Q2 expansion claim.

The reported pattern is that the smallest quartile of Q1 ranges is followed by
Q2 expanding to ~1.84x Q1, falling monotonically to ~0.83x for the largest
quartile. Clean and monotonic -- and that is exactly the shape a RATIO produces
with no underlying relationship at all.

If Q1 and Q2 ranges are merely two draws from the same distribution, then
selecting the days where Q1 happened to be small selects days where Q1 was
below ITS OWN mean, and dividing anything by a small number gives a large ratio.
Regression to the mean does the rest. The monotonicity is guaranteed by the
construction, not by the market.

The control: keep every real Q1 and every real Q2, but PAIR THEM AT RANDOM
across different cycles. That destroys any genuine Q1->Q2 link while preserving
both marginal distributions exactly. If the monotonic ladder survives the
shuffle, it was arithmetic. If it collapses, the effect is real.
"""
import sys, datetime as dt, numpy as np, pandas as pd
from zoneinfo import ZoneInfo
MEL, NY = ZoneInfo("Australia/Melbourne"), ZoneInfo("America/New_York")

bars = pd.read_parquet("/home/user/Trade_Cartel/research/gold_10am_flip/data/bars_5m_melbourne.parquet")
naive = pd.to_datetime(bars["ts_mel"])
inst = naive.dt.tz_localize(MEL, ambiguous=True, nonexistent="shift_forward")
ny = inst.dt.tz_convert(NY).dt.tz_localize(None)
bars = bars.assign(ny=ny).dropna(subset=["ny"]).sort_values("ny")

# minutes since 18:00 NY -> 90-minute quarter index within the daily cycle
m = (bars.ny.dt.hour * 60 + bars.ny.dt.minute).to_numpy().astype(float) - 18 * 60
m = np.where(m < 0, m + 1440, m)
cycle_day = (bars.ny + pd.Timedelta(hours=6)).dt.date          # 18:00 NY starts the cycle
q90 = (m // 90).astype(int)                                    # 0..15 across the 24h cycle
bars = bars.assign(cyc=cycle_day, q90=q90)

g = bars.groupby(["cyc", "q90"]).agg(hi=("h", "max"), lo=("l", "min"), nb=("h", "size")).reset_index()
g = g[g.nb >= 15]                                              # near-complete 90-minute quarters only
g["rng"] = g.hi - g.lo
piv = g.pivot(index="cyc", columns="q90", values="rng")

pairs = []
for k in range(0, 16, 4):                                      # Q1 of each 6h block, and its Q2
    if k in piv.columns and (k + 1) in piv.columns:
        sub = piv[[k, k + 1]].dropna()
        pairs.append(pd.DataFrame({"q1": sub[k].to_numpy(), "q2": sub[k + 1].to_numpy()}))
P = pd.concat(pairs, ignore_index=True)
print(f"complete Q1->Q2 pairs: {len(P)}   (their count: 772)")


def ladder(q1, q2, tag):
    qs = pd.qcut(q1, 4, labels=["smallest25", "25-50", "50-75", "largest25"])
    out = []
    for lab in ["smallest25", "25-50", "50-75", "largest25"]:
        s = (qs == lab)
        out.append((lab, np.median(q1[s]), np.median(q2[s]), np.median(q2[s] / q1[s])))
    print(f"\n  {tag}")
    print(f"    {'Q1 size':<12}{'med Q1':>9}{'med Q2':>9}{'med Q2/Q1':>11}")
    for lab, a, b, r in out:
        print(f"    {lab:<12}{a:>9.2f}{b:>9.2f}{r:>11.2f}x")
    return [r for _, _, _, r in out]


real = ladder(P.q1.to_numpy(), P.q2.to_numpy(), "REAL pairing (their finding, reproduced)")
rng = np.random.default_rng(5)
shuf = ladder(P.q1.to_numpy(), rng.permutation(P.q2.to_numpy()),
              "SHUFFLED pairing — Q2 taken from a RANDOM other cycle")

print("\n  If the shuffled ladder is also monotonic and similar in magnitude,")
print("  the pattern is a property of dividing by a small number, not of gold.")
mono = lambda v: all(v[i] > v[i+1] for i in range(3))
print(f"    real ladder monotonic decreasing : {mono(real)}   {[f'{v:.2f}' for v in real]}")
print(f"    shuffled ladder monotonic dec.   : {mono(shuf)}   {[f'{v:.2f}' for v in shuf]}")
