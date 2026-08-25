"""Baseline: the supplied Pine's own defaults, executed on real quotes."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "code")
from engine import Ticks, build_days, run, stats

bars = pd.read_parquet("data/bars_5m_melbourne.parquet")
T = Ticks(np.load("data/session_ticks.npy", mmap_mode="r"))
days = build_days(bars)
ok = sum(1 for v in days.values() if v["ok"])
print(f"calendar days in file : {len(days)}")
print(f"constructible days    : {ok}")
print(f"skipped (no 09:50/10:00): {len(days)-ok}\n")

rows = []
for lbl, kw in [
    ("AS SUPPLIED  (A-short + Flip)", dict(use_A=True, a_short_only=True,  use_flip=True)),
    ("Logic A short only",            dict(use_A=True, a_short_only=True,  use_flip=False)),
    ("Logic A both directions",       dict(use_A=True, a_short_only=False, use_flip=False)),
    ("Flip only (both directions)",   dict(use_A=False, a_short_only=True, use_flip=True)),
    ("All three (A both + Flip)",     dict(use_A=True, a_short_only=False, use_flip=True)),
]:
    tr = run(bars, T, sl_pts=18, tp_pts=40, days=days, **kw)
    s = stats(tr, lbl); rows.append(s)
    if lbl.startswith("AS SUPPLIED"):
        tr.to_csv("results/trades_as_supplied.csv", index=False)

R = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(R[["label","n","net","exp","win","pf","max_dd","mar","r2","tstat"]].to_string(
    index=False, float_format=lambda v: f"{v:,.2f}"))
R.to_csv("results/baseline.csv", index=False)

tr = pd.read_csv("results/trades_as_supplied.csv")
if len(tr):
    print("\nAS SUPPLIED — by signal type:")
    for k, g in tr.groupby("kind"):
        s = stats(g, k)
        print(f"  {k:5s} n={s['n']:4d}  exp={s['exp']:+7.3f} pts  win={s['win']:5.1f}%  net={s['net']:+9.1f}")
    print("\n  exit reason:", tr["why"].value_counts().to_dict())
    print(f"  median hold: {tr['hold_min'].median():.0f} min")
