import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); matplotlib.rcParams["axes.formatter.use_mathtext"] = False
import matplotlib.pyplot as plt, matplotlib.dates as mdates
E = pd.read_parquet("research/qt2/results/events.parquet")
S = pd.read_parquet("research/qt2/results/sweep.parquet")
D = S.merge(E[["eid","year","book","adef","t"]], on="eid")
D["ts"] = pd.to_datetime(D.t, unit="ms")
D["split"] = np.where(D.ts < "2025-08-20", "TRAIN",
             np.where(D.ts < "2026-02-20", "VALIDATION", "HOLDOUT"))
CAND = [("B_comp","dwell",5.0,20.0,"#c1121f"), ("B_comp","dwell",5.0,10.0,"#e07a5f"),
        ("B_comp","dwell",4.0,20.0,"#f2a65a"), ("B_comp","dwell",4.0,3.0,"#8ab17d")]
fig, ax = plt.subplots(2, 1, figsize=(13, 9), height_ratios=[3, 1.6])
fig.suptitle("Quarter Theory late-state books — the 8 cells that were positive on TRAIN\n"
             "1,000 (book x acceptance x target x stop) cells searched; "
             "0 survived either unseen split",
             fontsize=13, fontweight="bold", y=0.97)
for b, a, tp, sl, col in CAND:
    q = D[(D.book==b)&(D.adef==a)&(D.tp==tp)&(D.sl==sl)].sort_values("ts")
    ax[0].step(q.ts, q.pnl.cumsum(), where="post", color=col, lw=1.9,
               label=f"{b} {a}  target {tp:.0f} / stop {sl:.0f}   "
                     f"net {q.pnl.sum():+.0f}")
for x, lab in (("2025-08-20","TRAIN | VALIDATION"), ("2026-02-20","VALIDATION | HOLDOUT")):
    ax[0].axvline(pd.Timestamp(x), color="#333", ls="--", lw=1.2)
    ax[0].text(pd.Timestamp(x), ax[0].get_ylim()[1], "  " + lab, fontsize=9,
               va="top", color="#333")
ax[0].axhline(0, color="#666", lw=0.8)
ax[0].set_ylabel("cumulative $ per ounce"); ax[0].grid(alpha=0.25)
ax[0].legend(loc="lower left", fontsize=9)
# how many cells are positive, by split
g = D.groupby(["split","book","adef","tp","sl"]).pnl.mean().reset_index()
order = ["TRAIN","VALIDATION","HOLDOUT"]
vals = [100*(g[g.split==s].pnl>0).mean() for s in order]
ax[1].bar(order, vals, color=["#2a9d8f","#c1121f","#c1121f"], width=0.5)
for i, v in enumerate(vals):
    ax[1].text(i, v + 0.03, f"{v:.1f}%  ({int(v*10)} of 1000)", ha="center", fontsize=10)
ax[1].set_ylabel("% of the 1,000 cells\nwith positive expectancy")
ax[1].set_ylim(0, 1.2); ax[1].grid(alpha=0.25, axis="y")
ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.setp(ax[0].get_xticklabels(), rotation=45, ha="right")
fig.tight_layout(rect=[0,0,1,0.94])
fig.savefig("research/qt2/results/train_val_holdout.png", dpi=150)
print("written -> research/qt2/results/train_val_holdout.png")
