import sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "research/microq3/code")
import engine as E, microq3 as M

SL, TP = 15.5, 25.5
BASE = M.signals()
d = M.apply(BASE, SL, TP).sort_values("t_entry").reset_index(drop=True)
p = d.pnl.to_numpy()
eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]; dd = pk - eq
w, l = p[p > 0], p[p < 0]
neg = p[p < 0]


def streak(x):
    b = m = 0
    for v in x:
        b = b + 1 if v <= 0 else 0; m = max(m, b)
    return m


R = dict(trades=len(p), wins=len(w), losses=len(l), win_rate=100 * len(w) / len(p),
         gross_profit=w.sum(), gross_loss=-l.sum(), profit_factor=w.sum() / -l.sum(),
         net=p.sum(), expectancy=p.mean(), median_trade=np.median(p),
         avg_winner=w.mean(), avg_loser=l.mean(), payoff=w.mean() / abs(l.mean()),
         max_dd=dd.max(), avg_dd=dd[dd > 0].mean() if (dd > 0).any() else 0.0,
         ulcer=np.sqrt((dd ** 2).mean()), max_losing_streak=streak(p),
         sharpe_like=p.mean() / p.std(ddof=1),
         sortino_like=p.mean() / neg.std(ddof=1) if len(neg) > 1 else np.nan,
         equity_r2=np.corrcoef(np.arange(len(eq)), eq)[0, 1] ** 2)
S = pd.Series(R)
S.to_csv("research/microq3/results/headline_metrics.csv")
print("HEADLINE METRICS — Micro-Q3 Compression as specified (SL 15.50 / TP 25.50)")
print("=" * 70)
for k, v in R.items():
    print(f"  {k:<22}{v:>14.3f}" if isinstance(v, float) else f"  {k:<22}{v:>14}")

fig, ax = plt.subplots(5, 2, figsize=(15, 21))
ax = ax.ravel()
ax[0].plot(np.concatenate([[0], eq]), lw=2, color="#2b6cb0"); ax[0].set_title("1. Cumulative equity (points)")
ax[0].grid(alpha=.3); ax[0].axhline(0, color="k", lw=.6)
ax[1].fill_between(range(len(dd)), 0, -dd, color="#c53030", alpha=.7); ax[1].set_title("2. Drawdown (points)")
ax[1].grid(alpha=.3)
mth = d.assign(m=pd.to_datetime(d.t_entry).dt.to_period("M").astype(str)).groupby("m").pnl.sum()
ax[2].bar(range(len(mth)), mth.values, color=np.where(mth.values >= 0, "#2f855a", "#c53030"))
ax[2].set_xticks(range(len(mth))); ax[2].set_xticklabels(mth.index, rotation=60, fontsize=7)
ax[2].set_title("3. Monthly P/L"); ax[2].grid(alpha=.3)
k = 10
rp = [w_.sum() / -l_.sum() if (l_ := p[max(0, i - k):i][p[max(0, i - k):i] < 0]).sum() != 0
      else np.nan for i in range(k, len(p) + 1) for w_ in [p[max(0, i - k):i][p[max(0, i - k):i] > 0]]]
ax[3].plot(range(k, len(p) + 1), rp, marker="o", color="#6b46c1"); ax[3].axhline(1, color="k", ls="--", lw=.8)
ax[3].set_title(f"4. Rolling PF ({k}-trade window)"); ax[3].grid(alpha=.3)
re = pd.Series(p).rolling(k).mean()
ax[4].plot(re, marker="o", color="#b7791f"); ax[4].axhline(0, color="k", ls="--", lw=.8)
ax[4].set_title(f"5. Rolling expectancy ({k}-trade)"); ax[4].grid(alpha=.3)
ax[5].hist(p, bins=18, color="#4a5568", edgecolor="white"); ax[5].axvline(0, color="k")
ax[5].set_title("6. Trade outcome distribution"); ax[5].grid(alpha=.3)
raw = M.apply(BASE, 10_000, 10_000)
ax[6].scatter(raw.mae.abs(), raw.mfe, c=np.where(d.pnl > 0, "#2f855a", "#c53030"), s=45)
lim = max(raw.mfe.max(), raw.mae.abs().max())
ax[6].plot([0, lim], [0, lim], "k--", lw=.8); ax[6].axvline(SL, color="#c53030", ls=":", label=f"SL {SL}")
ax[6].axhline(TP, color="#2f855a", ls=":", label=f"TP {TP}")
ax[6].set_xlabel("MAE (unrestricted)"); ax[6].set_ylabel("MFE (unrestricted)")
ax[6].set_title("7. MFE vs MAE"); ax[6].legend(); ax[6].grid(alpha=.3)
ax[7].hist(d.entry_spread, bins=15, color="#2c7a7b", edgecolor="white")
ax[7].axvline(1.5, color="#c53030", ls="--"); ax[7].set_title("8. Entry spread ($)"); ax[7].grid(alpha=.3)
ax[8].hist(d.anchor_body, bins=15, color="#805ad5", edgecolor="white")
ax[8].axvline(1.0, color="#c53030", ls="--"); ax[8].axvline(6.25, color="#c53030", ls="--")
ax[8].set_title("9. Anchor body size ($)"); ax[8].grid(alpha=.3)
ax[9].hist(d.dist25, bins=15, color="#dd6b20", edgecolor="white")
ax[9].axvline(6.25, color="#c53030", ls="--"); ax[9].set_title("10. Distance to nearest $25 ($)")
ax[9].grid(alpha=.3)
plt.tight_layout(); plt.savefig("research/microq3/figs/microq3_panels.png", dpi=110)
print("\nwrote research/microq3/figs/microq3_panels.png")

# equity + drawdown comparison across strategies
lab = pd.read_csv("research/microq3/results/equity_labels.csv", header=None)[0].tolist()
cur = np.load("research/microq3/results/equity_curves.npy")
fig, a2 = plt.subplots(2, 1, figsize=(12, 10))
for nm, c in zip(lab, cur):
    v = c[~np.isnan(c)]
    a2[0].plot(np.arange(len(v)) / max(len(v) - 1, 1), v, lw=2, label=f"{nm} (n={len(v)})")
    pk2 = np.maximum.accumulate(np.concatenate([[0.], v]))[1:]
    a2[1].plot(np.arange(len(v)) / max(len(v) - 1, 1), -(pk2 - v), lw=2, label=nm)
a2[0].set_title("Equity curves, same tick engine, x-axis = fraction of that strategy's trades")
a2[1].set_title("Drawdown curves")
for x in a2: x.grid(alpha=.3); x.legend(fontsize=8); x.axhline(0, color="k", lw=.6)
plt.tight_layout(); plt.savefig("research/microq3/figs/comparison.png", dpi=110)
print("wrote research/microq3/figs/comparison.png")
