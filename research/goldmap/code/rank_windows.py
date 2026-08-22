"""Part 2/17 — rank the day by activity, independently per year, then ask which
windows survive in BOTH. Activity windows are chosen here BEFORE any strategy
performance is looked at."""
import numpy as np, pandas as pd
from scipy import stats
pd.set_option("display.width", 260)
D = pd.read_parquet("research/goldmap/results/activity_5m.parquet")

# gold trades Sunday 18:00 NY -> Friday 17:00 NY. Keep buckets inside that, drop
# the 17:00-18:00 daily settlement stop, which is a hole not a quiet period.
D = D[D.ticks >= 5]
open_mask = ~(((D.dow == 4) & (D.hm >= 17 * 60)) | ((D.dow == 5)) |
              ((D.dow == 6) & (D.hm < 18 * 60)) |
              ((D.hm >= 17 * 60) & (D.hm < 18 * 60)))
D = D[open_mask].copy()
print(f"open 5-minute buckets: {len(D):,}   days per year: "
      f"{D.groupby('year').date.nunique().to_dict()}")

MEAS = dict(ticks="median", tot_vol="median", rng="median", rv="median",
            spread_med="median", mv_per_spread="median", abs_ret="median",
            ge10="mean", ge15="mean", ge20="mean", ge25="mean")


def profile(df, res):
    """Aggregate to a time-of-day grid of `res` minutes, per year."""
    d = df.assign(slot=(df.hm // res) * res)
    g = d.groupby(["year", "slot"]).agg(**{k: (k, v) for k, v in MEAS.items()})
    g["n_obs"] = d.groupby(["year", "slot"]).size()
    return g.reset_index()


def label(m):
    return f"{m//60:02d}:{m%60:02d}"


print("\n" + "=" * 132)
print("HOURLY PROFILE — medians per hour of the New York day, each year independently")
print("=" * 132)
H = profile(D, 60)
piv = H.pivot(index="slot", columns="year")
rows = []
print(f"{'NY hour':<9}" + "".join(f"{c:>22}" for c in ("ticks (med)", "quoted vol (med)",
      "range $ (med)", "spread $ (med)", "move/spread")))
for s in sorted(H.slot.unique()):
    a = H[(H.slot == s) & (H.year == "2024-25")]
    b = H[(H.slot == s) & (H.year == "2025-26")]
    if len(a) == 0 or len(b) == 0:
        continue
    a, b = a.iloc[0], b.iloc[0]
    rows.append(dict(slot=s, t24=a.ticks, t25=b.ticks, v24=a.tot_vol, v25=b.tot_vol,
                     r24=a.rng, r25=b.rng, s24=a.spread_med, s25=b.spread_med,
                     m24=a.mv_per_spread, m25=b.mv_per_spread, rv24=a.rv, rv25=b.rv))
    print(f"{label(s):<9}" + f"{a.ticks:>10.0f}{b.ticks:>12.0f}"
          + f"{a.tot_vol:>11.1f}{b.tot_vol:>11.1f}"
          + f"{a.rng:>11.2f}{b.rng:>11.2f}"
          + f"{a.spread_med:>11.3f}{b.spread_med:>11.3f}"
          + f"{a.mv_per_spread:>11.1f}{b.mv_per_spread:>11.1f}")
R = pd.DataFrame(rows)
R.to_csv("research/goldmap/results/hourly_profile.csv", index=False)

print("\n" + "=" * 132)
print("CROSS-YEAR RANK STABILITY — do the same hours lead in both years?")
print("=" * 132)
for nm, c1, c2 in (("tick count", "t24", "t25"), ("quoted volume", "v24", "v25"),
                   ("5m range", "r24", "r25"), ("realized vol", "rv24", "rv25"),
                   ("median spread", "s24", "s25"), ("move/spread", "m24", "m25")):
    rho = stats.spearmanr(R[c1], R[c2]).statistic
    print(f"  {nm:<18} Spearman rho = {rho:+.3f}")

print("\n" + "=" * 132)
print("PERSISTENT ACTIVE HOURS — top quartile in BOTH years, chosen before any strategy is run")
print("=" * 132)
for nm, c1, c2, hi in (("tick count", "t24", "t25", True), ("range", "r24", "r25", True),
                       ("move/spread", "m24", "m25", True), ("spread (low is good)", "s24", "s25", False)):
    q1 = R[c1].quantile(0.75 if hi else 0.25); q2 = R[c2].quantile(0.75 if hi else 0.25)
    sel = R[(R[c1] >= q1) & (R[c2] >= q2)] if hi else R[(R[c1] <= q1) & (R[c2] <= q2)]
    print(f"  {nm:<22} {', '.join(label(int(s)) for s in sorted(sel.slot))}")

both = R.copy()
for c in ("t24", "t25", "r24", "r25", "m24", "m25", "rv24", "rv25"):
    both[c + "_p"] = both[c].rank(pct=True)
both["s24_p"] = 1 - both.s24.rank(pct=True); both["s25_p"] = 1 - both.s25.rank(pct=True)
both["A24"] = both[["t24_p", "r24_p", "rv24_p", "s24_p"]].mean(axis=1)
both["A25"] = both[["t25_p", "r25_p", "rv25_p", "s25_p"]].mean(axis=1)
both["Amin"] = both[["A24", "A25"]].min(axis=1)
both = both.sort_values("Amin", ascending=False)
print("\n  EQUAL-WEIGHT ACTIVITY SCORE (tick, range, realized vol, inverse spread percentiles)")
print(f"  {'NY hour':<10}{'A 24-25':>10}{'A 25-26':>10}{'min':>8}")
for _, r in both.head(10).iterrows():
    print(f"  {label(int(r.slot)):<10}{r.A24:>10.2f}{r.A25:>10.2f}{r.Amin:>8.2f}")
print("  ...")
for _, r in both.tail(4).iterrows():
    print(f"  {label(int(r.slot)):<10}{r.A24:>10.2f}{r.A25:>10.2f}{r.Amin:>8.2f}")
both.to_csv("research/goldmap/results/hourly_activity_score.csv", index=False)
print(f"\n  Spearman rho between the two years' activity scores: "
      f"{stats.spearmanr(both.A24, both.A25).statistic:+.3f}")
