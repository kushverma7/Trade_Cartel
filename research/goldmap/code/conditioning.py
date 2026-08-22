"""Parts 4, 14, 12, 15 — does ANY condition rescue the negative all-day baseline?

Every table below is reported PER YEAR. A condition is only interesting if it
points the same way in both. Exits are held at the unoptimised SL 20 / TP 30
throughout so that nothing here is an exit result in disguise.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
from outcomes import score, LV
pd.set_option("display.width", 250)

F = pd.read_parquet("research/goldmap/results/events_features.parquet")
SL, TP = 20, 30
p, w = score(F, SL, TP)
F["pnl"] = p
print(f"all-day baseline, SL{SL}/TP{TP}: n={len(F):,}  exp={F.pnl.mean():+.3f}  "
      f"PF={F.pnl[F.pnl>0].sum()/-F.pnl[F.pnl<0].sum():.3f}\n")


def stat(d):
    p = d.pnl.to_numpy()
    if len(p) < 20:
        return None
    gp, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    return dict(n=len(p), wr=100 * (p > 0).mean(), pf=(gp / gl if gl else np.inf),
                exp=p.mean(), net=p.sum(), mdd=float((pk - eq).max()),
                t=p.mean() / (p.std(ddof=1) / np.sqrt(len(p))))


def by(col, bins=None, labels=None, title="", qcut=False):
    print("=" * 118); print(title); print("=" * 118)
    d = F.dropna(subset=[col]).copy()
    if qcut:
        d["g"] = pd.qcut(d[col], bins, labels=labels, duplicates="drop")
    elif bins is not None:
        d["g"] = pd.cut(d[col], bins, labels=labels)
    else:
        d["g"] = d[col]
    print(f"  {'group':<22}" + "".join(f"{h:>9}" for h in
          ("n 24-25", "exp", "PF", "n 25-26", "exp", "PF", "t both")))
    for g, dd in d.groupby("g", observed=True):
        a = stat(dd[dd.year == "2024-25"]); b = stat(dd[dd.year == "2025-26"])
        c = stat(dd)
        if c is None:
            continue
        f = lambda s, k, fmt: (fmt.format(s[k]) if s else "--")
        print(f"  {str(g):<22}{f(a,'n','{:.0f}'):>9}{f(a,'exp','{:+.2f}'):>9}{f(a,'pf','{:.2f}'):>9}"
              f"{f(b,'n','{:.0f}'):>9}{f(b,'exp','{:+.2f}'):>9}{f(b,'pf','{:.2f}'):>9}"
              f"{c['t']:>9.2f}")
    print()


by("act_p40", [0, .25, .5, .75, 1.001], ["bottom 25%", "25-50%", "50-75%", "top 25%"],
   "PART 4 — ACTIVITY QUARTILE (trailing 40 same-slot observations, past-only)")
by("comp_p40", [0, .25, .5, .75, 1.001], ["most compressed", "25-50%", "50-75%", "widest"],
   "PART 8 — ANCHOR COMPRESSION QUARTILE (trailing percentile of the same slot)")
by("spread_p40", [0, .25, .5, .75, 1.001], ["tightest 25%", "25-50%", "50-75%", "widest 25%"],
   "PART 11/19 — ENTRY SPREAD QUARTILE, relative to the same slot's recent history")
by("cont", None, None, "PART 14 — CONTINUATION vs FLIP")
by("daily_q", None, None, "PART 12 — DAILY 6-HOUR QUARTER")
by("q90_idx", None, None, "PART 12 — WHICH 90-MINUTE QUARTER INSIDE THE DAILY QUARTER")
by("sig_mq", None, None, "PART 12 — MICRO QUARTER THE BREAK LANDS IN")
by("speed", [0, 25, 35, 45, 70], ["<25 min", "25-35", "35-45", "45+"],
   "PART 13 — HOW FAST THE BREAK CAME (minutes into the 90-minute quarter)")
