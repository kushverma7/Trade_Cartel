"""Equity curve of the pasted Pine ("Micro-Q3 Smoother") on one year of ticks.

Runs the script AS WRITTEN -- selection rule included, so the BUG-047 trades are
in -- over the research year it restricts itself to, and resolves every trade on
the real bid/ask tape with the script's own SL 15.50 / TP 25.50 / 12h stop.

The researched rule is overlaid for reference, in both its forms: with the
$1.50 spread filter (the header's 25 trades, not reproducible in Pine) and
without it (34 trades, which IS what Pine can express).
"""
import sys, numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["axes.formatter.use_mathtext"] = False
matplotlib.rcParams["text.usetex"] = False
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.path.insert(0, "research/microq3/code")
import engine as E, microq3 as M
from pine_smoother_audit import signals_pine, SL, TP, HOLD

OUT = "research/microq3/results"
ARMS = [
    ("PINE as written (BUG-047)", signals_pine(),                "#c1121f", 2.4),
    ("researched, no spread filter", M.signals(spread_max=None), "#1d3557", 1.8),
    ("researched, spread <= 1.50",   M.signals(),                "#2a9d8f", 1.8),
]

curves = {}
for name, sig, col, lw in ARMS:
    d = M.apply(sig, SL, TP, time_stop_min=HOLD).sort_values("t_entry")
    d = d.reset_index(drop=True)
    d["equity"] = d.pnl.cumsum()
    d["peak"] = d.equity.cummax().clip(lower=0)
    d["dd"] = d.peak - d.equity
    curves[name] = (d, col, lw)
    d.to_csv(f"{OUT}/equity_{'pine' if 'PINE' in name else ('ref_nospread' if 'no spread' in name else 'ref')}.csv",
             index=False)

fig, ax = plt.subplots(3, 1, figsize=(13, 11), height_ratios=[3, 1.3, 1.6],
                       sharex=True)
fig.suptitle("Micro-Q3 Smoother — equity on XAUUSD Dukascopy ticks, "
             "2025-08-20 to 2026-08-20\n"
             "SL $15.50 / TP 25.50 / 12h stop, real bid-ask fills, 1 oz",
             fontsize=13, fontweight="bold", y=0.975)

for name, (d, col, lw) in curves.items():
    t = pd.to_datetime(d.t_entry)
    s = E.stats(d.pnl.values)
    lab = (f"{name}   n={s['n']}  PF={s['pf']:.2f}  "
           f"net={s['net']:+.0f}  maxDD {s['mdd']:.0f}")
    ax[0].step(t, d.equity, where="post", color=col, lw=lw, label=lab)
    ax[0].scatter(t, d.equity, s=14, color=col, zorder=3)
    if "PINE" in name:
        ex = ~d.date.isin(set(M.apply(M.signals(spread_max=None), SL, TP,
                                      time_stop_min=HOLD).date))
        ax[0].scatter(t[ex], d.equity[ex], s=70, facecolors="none",
                      edgecolors="#e07a5f", lw=1.8, zorder=4,
                      label="  \u2514 trade the BUG-047 search added")
    ax[1].fill_between(t, 0, -d.dd, step="post", color=col, alpha=0.25)
    ax[1].step(t, -d.dd, where="post", color=col, lw=1.2)

ax[0].axhline(0, color="#666", lw=0.8)
ax[0].set_ylabel("cumulative $ per ounce")
ax[0].legend(loc="upper left", fontsize=9, framealpha=0.95)
ax[0].grid(alpha=0.25)
ax[1].set_ylabel("drawdown $")
ax[1].grid(alpha=0.25)

# bottom panel: the Pine's individual trades, coloured by whether the
# researched rule would have taken that day at all
d, _, _ = curves["PINE as written (BUG-047)"]
ref_days = set(curves["researched, no spread filter"][0].date)
extra = ~d.date.isin(ref_days)
t = pd.to_datetime(d.t_entry)
ax[2].bar(t[~extra], d.pnl[~extra], width=4, color="#1d3557",
          label=f"break the researched rule also takes  ({(~extra).sum()})")
ax[2].bar(t[extra], d.pnl[extra], width=4, color="#e07a5f",
          label=f"added by BUG-047  ({extra.sum()}, net {d.pnl[extra].sum():+.1f})")
ax[2].axhline(0, color="#666", lw=0.8)
ax[2].set_ylabel("per-trade $")
ax[2].legend(loc="lower left", fontsize=9)
ax[2].grid(alpha=0.25)
ax[2].xaxis.set_major_locator(mdates.MonthLocator())
ax[2].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.setp(ax[2].get_xticklabels(), rotation=45, ha="right")
fig.tight_layout(rect=[0, 0, 1, 0.955])
fig.savefig(f"{OUT}/pine_equity_curve.png", dpi=150)
print(f"written -> {OUT}/pine_equity_curve.png")

print("\n" + "=" * 96)
print("PINE AS WRITTEN — trade-by-trade equity, 2025-08-20 .. 2026-08-20")
print("=" * 96)
d, _, _ = curves["PINE as written (BUG-047)"]
print(f"  {'#':>3} {'date':>12}{'sig':>7}{'kind':>11}{'entry':>10}"
      f"{'why':>6}{'pnl':>9}{'equity':>10}{'dd':>8}  src")
for i, r in d.iterrows():
    print(f"  {i+1:>3} {str(r.date):>12}"
          f"{int(r.sig_hm)//60:>4}:{int(r.sig_hm)%60:02d}{r.kind:>11}"
          f"{r.entry:>10.2f}{r.exit_reason:>6}{r.pnl:>+9.2f}"
          f"{r.equity:>+10.1f}{-r.dd:>8.1f}"
          f"   {'BUG-047' if r.date not in ref_days else ''}")

print("\n" + "=" * 96)
print("MONTHLY")
print("=" * 96)
d["month"] = pd.to_datetime(d.t_entry).dt.to_period("M")
mo = d.groupby("month").agg(n=("pnl", "size"), net=("pnl", "sum"),
                            wins=("pnl", lambda x: (x > 0).sum()))
mo["cum"] = mo.net.cumsum()
print(f"  {'month':>9}{'n':>5}{'wins':>6}{'net $':>10}{'cum $':>10}")
for m, r in mo.iterrows():
    print(f"  {str(m):>9}{r.n:>5}{r.wins:>6}{r.net:>+10.1f}{r.cum:>+10.1f}")

print("\n" + "=" * 96)
print("SUMMARY")
print("=" * 96)
for name, (dd_, _, _) in curves.items():
    s = E.stats(dd_.pnl.values)
    eq = dd_.equity.values
    print(f"  {name:<32} n={s['n']:>3}  PF={s['pf']:>5.2f}  WR={s['wr']:>5.1f}%"
          f"  net=${s['net']:>+7.1f}  maxDD=${s['mdd']:>5.1f}"
          f"  final/DD={s['net']/s['mdd']:>5.2f}")
