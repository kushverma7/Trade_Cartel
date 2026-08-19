"""Re-render the SAME 120 charts, larger and TradingView-like.

Reads ANSWER_KEY.json for the exact ids/dates/decision points, so nothing is
resampled and the key is untouched. Presentation only.

Two presentation changes:
  1. Much larger canvas, thicker candles, right-hand price axis.
  2. The price axis is expressed in POINTS RELATIVE TO THE 09:50 OPEN. Absolute
     AU200 levels leak the era (about 5,500 in 2020 versus about 9,000 in 2026),
     which would have partly defeated the year blinding.
"""
import sys, os, json, datetime as dt
sys.path.insert(0, "research/au200")
import phase1 as P1
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

CTX_START = 540
BG, GRID, AXC = "#0d1117", "#1b2129", "#8b949e"
UP, DN = "#26a69a", "#ef5350"


def render(D, do, bh, bl, entry_m, out):
    bars = [(m,) + D[m] for m in sorted(D) if CTX_START <= m <= entry_m]
    fig, ax = plt.subplots(figsize=(16, 9), dpi=110)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    for i, (m, o, h, l, c) in enumerate(bars):
        col = UP if c >= o else DN
        ax.plot([i, i], [l - do, h - do], color=col, linewidth=1.6, solid_capstyle="butt", zorder=3)
        ax.add_patch(Rectangle((i - 0.36, min(o, c) - do), 0.72, max(abs(c - o), 1e-9),
                               facecolor=col, edgecolor=col, linewidth=0.8, zorder=4))
    n = len(bars)
    for y, col, lab, lw in ((0.0, "#4b8bff", "09:50 open", 2.0),
                            (bh - do, "#b6c0cc", "10:00 body high", 1.4),
                            (bl - do, "#b6c0cc", "10:00 body low", 1.4)):
        ax.axhline(y, color=col, linewidth=lw, alpha=0.95, zorder=2)
        ax.annotate(f"{lab}  {y:+.1f}", xy=(n - 0.5, y), xytext=(6, 0),
                    textcoords="offset points", va="center", ha="left",
                    color=col, fontsize=11, family="monospace", zorder=6)
    idx = {m: i for i, (m, *_) in enumerate(bars)}
    if 600 in idx:
        ax.axvspan(idx[600] - 0.5, idx[600] + 0.5, color="#ffffff", alpha=0.05, zorder=1)
        ax.annotate("10:00", xy=(idx[600], 1), xycoords=("data", "axes fraction"),
                    xytext=(0, -14), textcoords="offset points", ha="center",
                    color="#c9d1d9", fontsize=11, family="monospace", zorder=6)
    if 590 in idx:
        ax.annotate("09:50", xy=(idx[590], 1), xycoords=("data", "axes fraction"),
                    xytext=(0, -14), textcoords="offset points", ha="center",
                    color="#4b8bff", fontsize=11, family="monospace", zorder=6)
    ticks = [i for i, (m, *_) in enumerate(bars) if m % 15 == 0]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{bars[i][0]//60:02d}:{bars[i][0]%60:02d}" for i in ticks],
                       color=AXC, fontsize=10)
    ax.yaxis.tick_right(); ax.yaxis.set_label_position("right")
    ax.tick_params(axis="y", colors=AXC, labelsize=11)
    ax.set_ylabel("points from the 09:50 open", color=AXC, fontsize=11, labelpad=14)
    for k, sp in ax.spines.items():
        sp.set_color("#30363d")
    ax.grid(color=GRID, linewidth=0.7, zorder=0)
    lo = min(b[3] for b in bars) - do; hi = max(b[2] for b in bars) - do
    pad = max((hi - lo) * 0.10, 1.5)
    ax.set_xlim(-1.5, n + 7); ax.set_ylim(lo - pad, hi + pad)
    fig.tight_layout(pad=0.8)
    fig.savefig(out, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    key = json.load(open("research/au200/blind/ANSWER_KEY.json"))
    days = P1.load()
    os.makedirs("research/au200/blind/charts_v2", exist_ok=True)
    for r in key:
        d = dt.date.fromisoformat(r["date"])
        render(days[d], r["daily_open"], r["body_hi"], r["body_lo"],
               r["entry_m"], f"research/au200/blind/charts_v2/{r['id']}.png")
    print(f"re-rendered {len(key)} charts at 1760x990 into charts_v2/")
