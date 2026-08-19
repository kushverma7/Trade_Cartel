"""BLIND MANUAL VALIDATION — build the experiment.

DESIGN, fixed before any chart is drawn:
  * Sample 120 days uniformly at random across 2019-2026 from days that produce
    a Logic A signal. Sampling Logic A days is deliberate: the question is
    whether discretionary selection can separate GOOD Logic A signals from bad
    ones, which is what the screenshots implied.
  * DECISION POINT = the close of the Logic A entry candle. The chart shows
    everything up to and including that candle and nothing after.
  * The chart does NOT mark the signal or its direction. The 09:50 level and
    the 10:00 body are drawn, because those are the levels the trader uses.
  * Blinding: no date, no year, randomised presentation order, anonymous ids.
    Clock times remain because 09:50/10:00 are structural to the strategy.
  * The outcome key is written and committed BEFORE any answers are given.
"""
import sys, os, csv, json, random, datetime as dt, base64, io
sys.path.insert(0, "research/au200")
import phase1 as P1, phase2 as P2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

CTX_START = 540          # 09:00 Melbourne, for pre-09:50 context
N = 120
SEED = 20260819


def render(D, s, entry_m, path):
    do, bh, bl, side = s
    bars = [(m,) + D[m] for m in sorted(D) if CTX_START <= m <= entry_m]
    fig, ax = plt.subplots(figsize=(7.6, 4.4), dpi=100)
    fig.patch.set_facecolor("#0d1117"); ax.set_facecolor("#0d1117")
    for i, (m, o, h, l, c) in enumerate(bars):
        up = c >= o
        col = "#26a69a" if up else "#ef5350"
        ax.plot([i, i], [l, h], color=col, linewidth=0.9, solid_capstyle="butt")
        ax.add_patch(Rectangle((i - 0.32, min(o, c)), 0.64, max(abs(c - o), 1e-9),
                               facecolor=col, edgecolor=col, linewidth=0.5))
    ax.axhline(do, color="#4b8bff", linewidth=1.4, alpha=0.95)
    ax.axhline(bh, color="#9aa4b2", linewidth=1.0, alpha=0.75)
    ax.axhline(bl, color="#9aa4b2", linewidth=1.0, alpha=0.75)
    idx = {m: i for i, (m, *_ ) in enumerate(bars)}
    if 600 in idx:
        ax.axvline(idx[600] - 0.5, color="#5a6472", linewidth=0.8, linestyle=":", alpha=0.8)
    ticks = [i for i, (m, *_ ) in enumerate(bars) if m % 30 == 0]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{bars[i][0]//60:02d}:{bars[i][0]%60:02d}" for i in ticks],
                       color="#8b949e", fontsize=7)
    ax.tick_params(axis="y", colors="#8b949e", labelsize=7)
    for sp in ax.spines.values():
        sp.set_color("#21262d")
    ax.grid(color="#161b22", linewidth=0.6)
    ax.set_xlim(-1, len(bars))
    lo = min(b[3] for b in bars); hi = max(b[2] for b in bars); pad = (hi - lo) * 0.12
    ax.set_ylim(lo - pad, hi + pad)
    ax.margins(0)
    fig.tight_layout(pad=0.4)
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    days = P1.load(); m1 = P2.load_1m()
    cand = []
    for d in sorted(days):
        D = days[d]
        s = P1.setup(D)
        if s is None or P1.SESS_EXIT not in D:
            continue
        a = P1.logic_a(D, s)
        if not a:
            continue
        side, em, entry = a
        if em - CTX_START < 30:          # need some context before the decision
            continue
        cand.append((d, s, side, em, entry))
    print(f"eligible Logic A days: {len(cand)}")
    rng = random.Random(SEED)
    samp = rng.sample(cand, N)
    rng.shuffle(samp)
    os.makedirs("research/au200/blind/charts", exist_ok=True)
    key = []
    for i, (d, s, side, em, entry) in enumerate(samp, 1):
        cid = f"{i:03d}"
        render(days[d], s, em, f"research/au200/blind/charts/{cid}.png")
        path = [b for b in m1.get(d, []) if em + 5 <= b[0] <= P1.SESS_EXIT]
        touch, tm = P2.first_touch(path, entry, 20)
        mfe = mae = 0.0
        for m, o, h, l, c in path:
            mfe = max(mfe, (h - entry) if side > 0 else (entry - l))
            mae = max(mae, (entry - l) if side > 0 else (h - entry))
        key.append(dict(id=cid, date=str(d), logicA=("LONG" if side > 0 else "SHORT"),
                        entry_m=em, entry=entry, touch20=touch,
                        t_first=(tm - em) if tm else None, mfe=round(mfe, 2),
                        mae=round(mae, 2), body_hi=s[1], body_lo=s[2], daily_open=s[0]))
    with open("research/au200/blind/ANSWER_KEY.json", "w") as f:
        json.dump(key, f, indent=1)
    print(f"rendered {len(key)} charts; key written (DO NOT OPEN until answers are locked)")
