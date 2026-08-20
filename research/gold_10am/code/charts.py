"""Charts for the Gold 10AM report."""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import core, lib, analysis as A

CH = os.path.join(core.HERE, "..", "charts")
COST = 1.26
COL = {"A_SHORT": "#c0392b", "A_LONG": "#27ae60", "FLIP_L": "#2980b9", "FLIP_S": "#8e44ad"}


def main():
    os.makedirs(CH, exist_ok=True)
    tr = lib.load("trades.csv")
    paths, _ = A.load_paths(tr)

    # 1 — equity curves with the OOS boundaries marked
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for lg in core.LOGICS:
        sub = sorted([r for r in tr if r["logic"] == lg], key=lambda r: (r["date"], r["entry_minute"]))
        eq, s = [], 0.0
        for r in sub:
            s += r["base_pnl"] - COST
            eq.append((r["date_d"], s))
        ax.plot([x[0] for x in eq], [x[1] for x in eq], label=A.LABEL[lg], color=COL[lg], lw=1.6)
    for b, nm in ((lib.VAL[0], "VAL"), (lib.HOLD[0], "HOLD")):
        ax.axvline(b, color="#555", ls="--", lw=1)
        ax.text(b, ax.get_ylim()[1] * 0.95, " " + nm, fontsize=9, color="#555")
    ax.axhline(0, color="#999", lw=0.8)
    ax.set_title(f"Gold 10AM — cumulative $/oz per branch, SL $17 / TP $39, ${COST:.2f} round-trip cost")
    ax.set_ylabel("cumulative $ per ounce"); ax.legend(); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(os.path.join(CH, "equity_curves.png"), dpi=130); plt.close(fig)

    # 2 — first passage favourable-first % vs barrier
    fig, ax = plt.subplots(figsize=(10, 5))
    for lg in core.LOGICS:
        sub = [r for r in tr if r["logic"] == lg]
        xs, ys = [], []
        for x in A.FP:
            fav = sum(1 for r in sub if r[f"fp_{x}"] == "fav")
            adv = sum(1 for r in sub if r[f"fp_{x}"] == "adv")
            if fav + adv >= 20:
                xs.append(x); ys.append(100 * fav / (fav + adv))
        ax.plot(xs, ys, "o-", label=A.LABEL[lg], color=COL[lg], lw=1.6, ms=4)
    ax.axhline(50, color="k", ls="--", lw=1.2)
    ax.set_xscale("log"); ax.set_xticks(A.FP); ax.set_xticklabels([f"{x:g}" for x in A.FP])
    ax.set_xlabel("symmetric barrier, $ per ounce"); ax.set_ylabel("favourable touched first, %")
    ax.set_title("First passage: no branch separates from the 50% null at any distance")
    ax.set_ylim(25, 75); ax.legend(); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(os.path.join(CH, "first_passage.png"), dpi=130); plt.close(fig)

    # 3 — winner MAE / loser MFE curves
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for lg in core.LOGICS:
        w = [r["mae"] for r in tr if r["logic"] == lg and r["base_pnl"] > 0]
        l = [r["mfe"] for r in tr if r["logic"] == lg and r["base_pnl"] < 0]
        axes[0].plot(A.DOLLARS, [100 * sum(1 for x in w if x >= d) / len(w) for d in A.DOLLARS],
                     "o-", color=COL[lg], label=A.LABEL[lg], ms=3)
        axes[1].plot(A.DOLLARS, [100 * sum(1 for x in l if x >= d) / len(l) for d in A.DOLLARS],
                     "o-", color=COL[lg], label=A.LABEL[lg], ms=3)
    axes[0].set_title("Winner MAE survival: % of winners that first went this far against")
    axes[1].set_title("Loser MFE: % of losers that first went this far in favour")
    for a in axes:
        a.set_xlabel("$ per ounce"); a.set_ylabel("%"); a.grid(alpha=.25); a.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(CH, "mae_mfe.png"), dpi=130); plt.close(fig)

    # 4 — 09:50 coverage by month
    import csv, datetime as dt
    rows = list(csv.DictReader(open(os.path.join(lib.TAB, "coverage_by_day.csv"))))
    rows = [r for r in rows if dt.date.fromisoformat(r["date"]).weekday() < 5]
    g = collections.OrderedDict()
    for r in rows:
        b = g.setdefault(r["month"], [0, 0])
        b[0] += 1; b[1] += r["ref"] == "True"
    fig, ax = plt.subplots(figsize=(12, 4.2))
    ks = list(g)
    ax.bar(range(len(ks)), [100 * g[k][1] / g[k][0] for k in ks], color="#b8860b")
    ax.set_xticks(range(len(ks))); ax.set_xticklabels(ks, rotation=90, fontsize=7)
    ax.set_ylabel("% of weekdays with a 09:50 candle")
    ax.set_title("The 09:50 Melbourne reference candle does not exist in the southern summer\n"
                 "(gold's daily maintenance break sits at 09:00–10:00 Melbourne while "
                 "Melbourne is AEDT and New York is EST)")
    ax.grid(axis="y", alpha=.25)
    fig.tight_layout(); fig.savefig(os.path.join(CH, "coverage_by_month.png"), dpi=130); plt.close(fig)

    # 5 — clock placebo
    fig, ax = plt.subplots(figsize=(11, 5))
    pairs = ["09:30/09:40", "09:35/09:45", "09:40/09:50", "09:45/09:55",
             "09:50/10:00", "09:55/10:05", "10:00/10:10", "10:05/10:15"]
    data = {"A_SHORT": [-0.04, 1.16, 1.98, 2.35, 0.32, -0.92, -0.81, 2.91],
            "A_LONG": [-0.09, 1.66, 0.31, 2.21, 0.64, 1.67, 3.12, 1.70],
            "FLIP_L": [1.41, 0.37, -0.81, -0.45, 1.75, 0.12, -0.48, 0.58],
            "FLIP_S": [-0.94, -1.06, -1.02, -1.64, 1.17, 1.89, 1.13, -2.64]}
    for lg in core.LOGICS:
        ax.plot(pairs, data[lg], "o-", color=COL[lg], label=A.LABEL[lg], ms=5)
    ax.axhline(0, color="k", lw=1)
    ax.axvline(4, color="#555", ls="--", lw=1.2)
    ax.text(4.05, ax.get_ylim()[1] * 0.9, " the traded pair", fontsize=9, color="#555")
    ax.set_ylabel("expectancy $ per trade (net of cost)")
    ax.set_title("Clock placebo: the 09:50/10:00 pair is not distinguishable from its neighbours")
    ax.legend(); ax.grid(alpha=.25)
    fig.tight_layout(); fig.savefig(os.path.join(CH, "clock_placebo.png"), dpi=130); plt.close(fig)
    print("wrote 5 charts")


if __name__ == "__main__":
    main()
