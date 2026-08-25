"""Parts 7, 8, 9, 10, 33A — the actual Quarterly Theory claims, on the cycle itself.

The unit here is one 6-hour daily quarter containing four 90-minute quarters
Q1..Q4. This is where the QT claims live:
    Q1 accumulates, Q2 manipulates (sweeps Q1's liquidity), Q3 distributes.

Measured, per cycle:
    Q1 range, its causal percentile, body/range efficiency
    Q2 range / Q1 range, Q3 range / Q1 range
    which Q1 extreme Q2 swept, and whether price closed back inside Q1
    True Daily Open reclaim
    Q3 direction and size

The compression ladder gets the control it needs: re-pairing each real Q1 with a
Q2 from a RANDOM UNRELATED cycle. Ratios of a quantity to a selected-on quantity
always inflate, and the shuffled ladder shows by how much.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
from qt_engine import Book, PTS
pd.set_option("display.width", 250)

rows = []
for dd, yr in (("research/microq3/data_holdout", "2024-25"),
               ("research/microq3/data", "2025-26")):
    b = Book(dd, yr)
    for day in b.days:
        for dq_h, dq in ((18, "Q1"), (0, "Q2"), (6, "Q3"), (12, "Q4")):
            qs = [(dq_h * 3600 + k * 5400) % 86400 for k in range(4)]
            cs = [b.candle(day, s, s + 5400, min_ticks=60) for s in qs]
            if any(c is None for c in cs):
                continue
            q1, q2, q3, q4 = [dict(o=c["o"] / PTS, c=c["c"] / PTS,
                                   h=c["h"] / PTS, l=c["l"] / PTS) for c in cs]
            r1 = q1["h"] - q1["l"]
            if r1 <= 0:
                continue
            sweep_hi = q2["h"] > q1["h"]; sweep_lo = q2["l"] < q1["l"]
            sw = ("both" if sweep_hi and sweep_lo else
                  "high only" if sweep_hi else "low only" if sweep_lo else "none")
            back_inside = (q1["l"] <= q2["c"] <= q1["h"])
            rows.append(dict(
                year=yr, day=day, date=pd.Timestamp(day * 86400000, unit="ms").date(),
                daily_q=dq, dq_open_s=dq_h * 3600,
                q1_rng=r1, q1_body=abs(q1["c"] - q1["o"]), q1_eff=abs(q1["c"] - q1["o"]) / r1,
                q1_up=q1["c"] > q1["o"], q1_hi=q1["h"], q1_lo=q1["l"], q1_mid=(q1["h"] + q1["l"]) / 2,
                q1_open=q1["o"], q1_close=q1["c"],
                q2_rng=q2["h"] - q2["l"], q2_c=q2["c"], q2_o=q2["o"],
                q3_rng=q3["h"] - q3["l"], q3_c=q3["c"], q3_o=q3["o"],
                q3_ret=q3["c"] - q3["o"], q3_up=(q3["c"] > q3["o"]),
                q4_rng=q4["h"] - q4["l"],
                sweep=sw, back_inside=back_inside,
                reclaim_open=(q2["c"] > q1["o"]) if sw == "low only" else
                             ((q2["c"] < q1["o"]) if sw == "high only" else np.nan),
                cross_mid=((q2["c"] - (q1["h"] + q1["l"]) / 2) > 0)))
C = pd.DataFrame(rows)

# causal Q1 compression percentile: prior 40 cycles of the SAME daily quarter
C = C.sort_values(["year", "day", "dq_open_s"]).reset_index(drop=True)
C["q1_pct"] = np.nan
for (yr, dq), idx in C.groupby(["year", "daily_q"]).groups.items():
    idx = np.array(sorted(idx)); v = C.loc[idx, "q1_rng"].to_numpy()
    for i in range(len(v)):
        pr = v[max(0, i - 40):i]
        if len(pr) >= 15:
            C.loc[idx[i], "q1_pct"] = (pr < v[i]).mean()
C["q2_over_q1"] = C.q2_rng / C.q1_rng
C["q3_over_q1"] = C.q3_rng / C.q1_rng
C.to_parquet("research/goldmap/results/quarter_cycles.parquet", index=False)
print(f"complete 6-hour cycles with all four 90-minute quarters: {len(C):,}")
print(C.groupby(['year','daily_q']).size().unstack().to_string(), "\n")

print("=" * 116)
print("PART 8 — DOES A COMPRESSED Q1 PREDICT AN EXPANDED Q2?  (causal percentile bins)")
print("=" * 116)
D = C.dropna(subset=["q1_pct"]).copy()
D["bin"] = pd.cut(D.q1_pct, [0, .2, .4, .6, .8, 1.001],
                  labels=["0-20% (tightest)", "20-40%", "40-60%", "60-80%", "80-100% (widest)"])
print(f"  {'Q1 percentile':<22}" + "".join(f"{h:>13}" for h in
      ("n 24-25", "Q2/Q1", "Q3/Q1", "n 25-26", "Q2/Q1", "Q3/Q1")))
for g, d in D.groupby("bin", observed=True):
    a, b = d[d.year == "2024-25"], d[d.year == "2025-26"]
    print(f"  {str(g):<22}{len(a):>13}{a.q2_over_q1.median():>13.2f}{a.q3_over_q1.median():>13.2f}"
          f"{len(b):>13}{b.q2_over_q1.median():>13.2f}{b.q3_over_q1.median():>13.2f}")

print("\n  SHUFFLED CONTROL — each real Q1 re-paired with a Q2 from a random unrelated cycle")
rng = np.random.default_rng(9)
print(f"  {'Q1 percentile':<22}{'real Q2/Q1':>13}{'shuffled':>13}{'real Q3/Q1':>13}{'shuffled':>13}")
for g, d in D.groupby("bin", observed=True):
    sh2 = np.median(rng.choice(D.q2_rng.to_numpy(), (len(d), 200)) / d.q1_rng.to_numpy()[:, None])
    sh3 = np.median(rng.choice(D.q3_rng.to_numpy(), (len(d), 200)) / d.q1_rng.to_numpy()[:, None])
    print(f"  {str(g):<22}{d.q2_over_q1.median():>13.2f}{sh2:>13.2f}"
          f"{d.q3_over_q1.median():>13.2f}{sh3:>13.2f}")
print("  A ladder that the SHUFFLE reproduces is arithmetic, not prediction: dividing by a")
print("  small selected-on denominator makes any numerator look large.")

print("\n" + "=" * 116)
print("PART 9 — WHICH Q1 EXTREME DID Q2 SWEEP, AND WHAT DID Q3 DO?")
print("=" * 116)
print(f"  {'Q2 sweep':<14}{'n 24-25':>9}{'Q3 up%':>9}{'|Q3 ret|':>10}{'n 25-26':>9}{'Q3 up%':>9}{'|Q3 ret|':>10}")
for sw, d in C.groupby("sweep"):
    a, b = d[d.year == "2024-25"], d[d.year == "2025-26"]
    print(f"  {sw:<14}{len(a):>9}{100*a.q3_up.mean():>8.1f}%{a.q3_ret.abs().median():>10.2f}"
          f"{len(b):>9}{100*b.q3_up.mean():>8.1f}%{b.q3_ret.abs().median():>10.2f}")

print("\n  PART 33A — single-sided sweep: does Q3 go AGAINST the swept side?")
print("  (sweeping the LOW is bearish manipulation, so the hypothesis predicts Q3 UP)")
print(f"  {'condition':<40}{'n 24-25':>9}{'Q3 as predicted':>18}{'n 25-26':>9}{'Q3 as predicted':>18}")
for tag, m in (("low swept -> expect Q3 UP", C.sweep == "low only"),
               ("high swept -> expect Q3 DOWN", C.sweep == "high only")):
    want_up = "low" in tag
    for extra, em in (("", pd.Series(True, index=C.index)),
                      ("  + closed back inside Q1", C.back_inside),
                      ("  + closed back inside + tight Q1", C.back_inside & (C.q1_pct <= 0.4))):
        d = C[m & em]
        a, b = d[d.year == "2024-25"], d[d.year == "2025-26"]
        ok_a = (a.q3_up == want_up).mean() * 100 if len(a) else np.nan
        ok_b = (b.q3_up == want_up).mean() * 100 if len(b) else np.nan
        print(f"  {(tag+extra):<40}{len(a):>9}{ok_a:>17.1f}%{len(b):>9}{ok_b:>17.1f}%")
