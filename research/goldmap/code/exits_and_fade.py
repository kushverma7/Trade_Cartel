"""Part 29 — structural time exits, and the obvious counter-hypothesis.

59% of the baseline's trades reach neither stop nor target inside six hours, so
the horizon is doing a lot of the work. Quarterly Theory offers structural
alternatives; they are compared here against fixed clock horizons, per year.

Then the counter-hypothesis the negative baseline demands: if breaking out of a
compressed quarter loses, does FADING the break win?
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
from outcomes import score, LV
pd.set_option("display.width", 240)
F = pd.read_parquet("research/goldmap/results/events_features.parquet")


def st(p):
    p = p[np.isfinite(p)]
    if len(p) < 20:
        return None
    gp, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    return dict(n=len(p), wr=100 * (p > 0).mean(), pf=(gp / gl if gl else np.inf),
                exp=p.mean(), net=p.sum(), mdd=float((pk - eq).max()),
                t=p.mean() / (p.std(ddof=1) / np.sqrt(len(p))))


def row(tag, a, b, c):
    f = lambda s, k, fm: (fm.format(s[k]) if s else "--")
    print(f"  {tag:<26}{f(a,'n','{:.0f}'):>8}{f(a,'exp','{:+.2f}'):>8}{f(a,'pf','{:.2f}'):>7}"
          f"{f(b,'n','{:.0f}'):>8}{f(b,'exp','{:+.2f}'):>8}{f(b,'pf','{:.2f}'):>7}"
          f"{f(c,'exp','{:+.2f}'):>9}{f(c,'t','{:+.2f}'):>8}")


HDR = (f"  {'':<26}{'n 24-25':>8}{'exp':>8}{'PF':>7}{'n 25-26':>8}{'exp':>8}{'PF':>7}"
       f"{'exp both':>9}{'t':>8}")
m24 = (F.year == "2024-25").to_numpy(); m25 = (F.year == "2025-26").to_numpy()

print("=" * 104)
print("PART 29 — PURE TIME EXITS, no stop and no target at all")
print("=" * 104)
print(HDR)
for k, nm in (("mq", "end of micro quarter"), ("q90", "end of this 90m quarter"),
              ("q90_next", "end of next 90m quarter"), ("dailyq", "end of daily quarter"),
              ("h2", "fixed 2 hours"), ("h4", "fixed 4 hours"), ("h6", "fixed 6 hours")):
    p = F[f"pnl_{k}"].to_numpy()
    row(nm, st(p[m24]), st(p[m25]), st(p))

print("\n" + "=" * 104)
print("STOP AND TARGET, WITH THE UNRESOLVED TRADE CUT AT THE 90-MINUTE QUARTER INSTEAD OF 6h")
print("=" * 104)
print(HDR)
for sl, tp in ((10, 10), (15, 15), (20, 20), (20, 30), (15, 25), (25, 25)):
    i_tp = int(np.where(LV == tp)[0][0]); i_sl = int(np.where(LV == sl)[0][0])
    tu = F[f"t_up_{i_tp}"].to_numpy(); td = F[f"t_dn_{i_sl}"].to_numpy()
    fill = F[f"fill_dn_{i_sl}"].to_numpy(); alt = F["pnl_q90"].to_numpy()
    p = np.where(tu < td, tp, np.where(np.isfinite(td), fill, alt))
    row(f"SL{sl}/TP{tp}, cut at Q90", st(p[m24]), st(p[m25]), st(p))

print("\n" + "=" * 104)
print("THE COUNTER-HYPOTHESIS — fade the break instead of following it")
print("=" * 104)
print("  Inverting a trade is not simply negating its P&L: the fade enters on the other")
print("  side of the book and its stop and target swap roles. The ladder stored for each")
print("  event is one-sided, so the honest proxy available here is the mark-to-market")
print("  series, which IS symmetric up to the spread paid at entry.")
print(HDR)
for k, nm in (("mq", "fade, exit end of micro Q"), ("q90", "fade, exit end of 90m Q"),
              ("h2", "fade, exit after 2 hours"), ("h4", "fade, exit after 4 hours")):
    sprd = F.spread.to_numpy()
    p = -F[f"pnl_{k}"].to_numpy() - 2 * sprd      # pay the spread again on the other side
    row(nm, st(p[m24]), st(p[m25]), st(p))

print("\n" + "=" * 104)
print("WHERE DOES THE MONEY ACTUALLY GO? mark-to-market by horizon, all 7,887 events")
print("=" * 104)
print(f"  {'horizon':<26}{'mean':>9}{'median':>9}{'p25':>9}{'p75':>9}{'share > 0':>11}")
for k, nm in (("mq", "end of micro quarter"), ("q90", "end of this 90m quarter"),
              ("q90_next", "end of next 90m quarter"), ("h2", "2 hours"),
              ("h4", "4 hours"), ("h6", "6 hours")):
    v = F[f"pnl_{k}"].dropna().to_numpy()
    print(f"  {nm:<26}{v.mean():>9.3f}{np.median(v):>9.3f}{np.percentile(v,25):>9.2f}"
          f"{np.percentile(v,75):>9.2f}{100*(v>0).mean():>10.1f}%")
print(f"\n  mean entry spread across all events: ${F.spread.mean():.3f} "
      f"(median ${F.spread.median():.3f})")
