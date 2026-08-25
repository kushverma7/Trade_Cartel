"""Do daily pivots and prior-day levels produce a reaction a sham level wouldn't?

Same discipline as the grid test. Each day's levels are computed from the PRIOR
day's high, low and close in the usual way. The control keeps every level's
geometry but severs its link to this day: each day is given the levels computed
from a RANDOMLY CHOSEN OTHER day, rescaled to this day's price so the distances
are comparable. That preserves the distribution of "a line somewhere near price"
and removes only the part the theory claims matters -- that the line came from
THIS market's own prior session.

Reaction is measured as: on first touch, does price move AWAY from the level in
the direction it approached from (a rejection) or through it (acceptance), over
the following hour, measured on real bars.
"""
import numpy as np, pandas as pd

b = pd.read_parquet("/home/user/Trade_Cartel/research/gold_10am_flip/data/bars_5m_melbourne.parquet")
b["ts"] = pd.to_datetime(b["ts_mel"]); b = b.sort_values("ts")
b["d"] = b["ts"].dt.date
days = b.groupby("d").agg(o=("o", "first"), h=("h", "max"), l=("l", "min"),
                          c=("c", "last"), n=("c", "size")).reset_index()
days = days[days.n >= 100].reset_index(drop=True)
print(f"complete days: {len(days)}")

HOR = 12          # one hour of 5-minute bars after the touch


def levels_from(prev, ref_open):
    H, L, C = prev.h, prev.l, prev.c
    P = (H + L + C) / 3.0
    return {"PDH": H, "PDL": L, "PDC": C, "PP": P,
            "R1": 2 * P - L, "S1": 2 * P - H,
            "R2": P + (H - L), "S2": P - (H - L)}


def reaction(day_bars, lvl):
    """-> +1 rejection, 0 acceptance, None if never touched."""
    hi = day_bars["h"].to_numpy(); lo = day_bars["l"].to_numpy(); cl = day_bars["c"].to_numpy()
    t = np.flatnonzero((hi >= lvl) & (lo <= lvl))
    if len(t) == 0:
        return None
    k = int(t[0])
    if k == 0:
        return None
    approach_up = cl[k - 1] < lvl              # came from below
    seg = cl[k + 1:k + 1 + HOR]
    if len(seg) < 3:
        return None
    end = seg[-1]
    # rejection = ended back on the side it approached from
    return 1 if ((end < lvl) if approach_up else (end > lvl)) else 0


rng = np.random.default_rng(9)
real = {k: [0, 0] for k in ["PDH", "PDL", "PDC", "PP", "R1", "S1", "R2", "S2"]}
sham = {k: [0, 0] for k in real}
for i in range(1, len(days)):
    d = days.iloc[i]; prev = days.iloc[i - 1]
    db = b[b.d == d.d]
    if len(db) < 50:
        continue
    L_real = levels_from(prev, d.o)
    # sham: a random other day's levels, rescaled so distance-from-open matches
    j = int(rng.integers(1, len(days)))
    pj = days.iloc[j - 1]; dj = days.iloc[j]
    L_sham = {k: d.o + (v - dj.o) for k, v in levels_from(pj, dj.o).items()}
    for k in real:
        for store, lv in ((real, L_real[k]), (sham, L_sham[k])):
            r = reaction(db, lv)
            if r is not None:
                store[k][0] += r; store[k][1] += 1

print(f"\n{'='*84}")
print("REJECTION RATE ON FIRST TOUCH (price ends the next hour back on the approach side)")
print("50% = the level told you nothing. SHAM = the same level type from a random other day.")
print(f"{'='*84}")
print(f"{'level':<6}{'REAL n':>9}{'reject':>9}   {'SHAM n':>9}{'reject':>9}   {'edge':>8}")
for k in ["PDH", "PDL", "PDC", "PP", "R1", "S1", "R2", "S2"]:
    a, na = real[k]; s, ns = sham[k]
    ra, rs = a / max(na, 1), s / max(ns, 1)
    print(f"{k:<6}{na:>9}{100*ra:>8.1f}%   {ns:>9}{100*rs:>8.1f}%   {100*(ra-rs):>+7.1f}pp")
