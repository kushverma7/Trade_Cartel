"""Reproduce the UNFILTERED 10AM rule on both years and dump the ledger.

The saved tenam_both_years.csv holds only the quarter-filtered universe, so the
pooled 'strip the $25 filter' claim could not be checked against it. This
re-runs the same engine with qd disabled and writes the trade list out.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
sys.path.insert(0, "research/goldmap")
import importlib.util
spec = importlib.util.spec_from_file_location("th", "research/goldmap/code/tenam_holdout.py")
# tenam_holdout runs at import; instead lift the two functions by exec of its source
src = open("research/goldmap/code/tenam_holdout.py").read()
cut = src.index("\nbooks = {}")
ns = {"__name__": "th"}
exec(compile(src[:cut], "tenam_holdout.py", "exec"), ns)
Book, mel_labels, tenam, stat = ns["Book"], ns["mel_labels"], ns["tenam"], ns["stat"]

from scipy import stats as st
BIG = 1e9
out = []
for dd, yr, cache in (("research/microq3/data_holdout", "2024-25", "research/goldmap/results/mel_y1.npy"),
                      ("research/microq3/data", "2025-26", "research/goldmap/results/mel_y2.npy")):
    b = Book(dd, yr)
    mel = mel_labels(b, cache)
    print(f"{yr}: {len(b.ny):,} ticks", flush=True)
    for tag, kw in (("no quarter filter",  dict(qd=BIG, spr=2.0)),
                    ("no quarter, no spread", dict(qd=BIG, spr=BIG)),
                    ("quarter filter (as researched)", dict(qd=7.5, spr=2.0))):
        d = tenam(b, mel, "researched", **kw)
        out.append(d.assign(year=yr, variant=tag))
    del b, mel

R = pd.concat(out, ignore_index=True)
R.to_csv("research/goldmap/results/tenam_unfiltered_both_years.csv", index=False)

print("\n" + "=" * 104)
print("THE $25 QUARTER FILTER, IN AND OUT, ON BOTH TICK YEARS   [researched rule, SL15/TP25]")
print("=" * 104)
print(f"  {'variant':<32}{'year':<10}{'n':>5}{'WR':>8}{'PF':>8}{'exp':>9}{'net':>9}{'maxDD':>8}{'t':>7}{'p':>8}")
for tag in R.variant.unique():
    for yr in ("2024-25", "2025-26", "POOLED"):
        x = R[R.variant == tag]
        if yr != "POOLED":
            x = x[x.year == yr]
        s = stat(x)
        t = st.ttest_1samp(x.pnl.values, 0)
        lab = tag if yr == "2024-25" else ""
        print(f"  {lab:<32}{yr:<10}{s['n']:>5}{s['wr']:>7.1f}%{s['pf']:>8.3f}"
              f"{s['exp']:>9.2f}{s['net']:>9.1f}{s['mdd']:>8.1f}{t.statistic:>+7.2f}{t.pvalue:>8.4f}")
    print()
