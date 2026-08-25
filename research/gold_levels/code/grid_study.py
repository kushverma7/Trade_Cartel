"""Do ROUND price levels do anything a shifted grid of the same spacing wouldn't?

The repo already knows scale matters (H76: Yotov's 250-point quarters never bind
on 15m gold; H77: a 2.50 grid works as a counter-trend target). What neither
tested is whether ROUNDNESS itself carries information, as opposed to simply
"take profit every N points".

The control is a PHASE SHIFT. For every grid spacing S, the same analysis is run
on levels at k*S (round: 3300, 3325, 3350 ...) and on levels at k*S + S/2 and
k*S + S/3 -- identical spacing, identical count, identical everything except
that the numbers are not round. If gold respects round numbers, the round phase
must beat the shifted ones. If all phases behave alike, the grid is a ruler, not
a magnet, and any apparent level effect is really an effect of spacing.

Two measurements:
  TRAVERSE   having crossed a level going up, does price reach the NEXT level up
             before falling back to the one below? A level structure that means
             anything should make that asymmetric.
  MAGNETISM  where does price actually sit, relative to the grid? Excess time
             near k*S would be attraction; excess time at the midpoint repulsion.
"""
import sys, numpy as np, pandas as pd

BARS = "/home/user/Trade_Cartel/research/gold_10am_flip/data/bars_5m_melbourne.parquet"
b = pd.read_parquet(BARS).sort_values("ts_mel")
hi = b["h"].to_numpy(float); lo = b["l"].to_numpy(float); cl = b["c"].to_numpy(float)
print(f"5-minute bars: {len(cl):,}   price range {cl.min():.1f} .. {cl.max():.1f}")


def traverse(S, phase):
    """-> (n_events, P(continue)). One event per grid-cell change."""
    idx = np.floor((cl - phase) / S).astype(np.int64)
    ch = np.flatnonzero(np.diff(idx) != 0) + 1
    cont = tot = 0
    for k in ch:
        start = idx[k]
        up = idx[k] > idx[k - 1]
        # walk forward until price leaves this cell; did it exit the same way in?
        j = k + 1
        while j < len(idx) and idx[j] == start:
            j += 1
        if j >= len(idx):
            break
        tot += 1
        if (idx[j] > start) == up:
            cont += 1
    return tot, cont / tot if tot else np.nan


def magnet(S, sample):
    """Fraction of observations in the middle third of each cell vs the outer
    thirds touching the levels. 1/3 means no preference."""
    r = np.mod(sample, S) / S
    near = ((r < 1/6) | (r > 5/6)).mean()      # within 1/6 of a level
    mid = ((r > 1/3) & (r < 2/3)).mean()        # middle third, away from levels
    return near, mid


print(f"\n{'='*104}")
print("TRAVERSE: crossed a level going one way -- does price continue to the next level, or turn back?")
print("P(continue) = 0.50 means the grid says nothing. ROUND is phase 0; the others are the SAME grid, shifted.")
print(f"{'='*104}")
print(f"{'spacing':>9} | {'ROUND':>16} | {'shift S/2':>16} | {'shift S/3':>16} | round advantage")
for S in [1, 2.5, 5, 10, 12.5, 25, 50, 100]:
    out = []
    for ph in [0.0, S/2, S/3]:
        n, p = traverse(S, ph)
        out.append((n, p))
    adv = out[0][1] - np.mean([out[1][1], out[2][1]])
    print(f"{S:>9.1f} | {out[0][0]:>7,} {out[0][1]:>7.4f} | {out[1][0]:>7,} {out[1][1]:>7.4f} | "
          f"{out[2][0]:>7,} {out[2][1]:>7.4f} | {adv:+.4f}")

print(f"\n{'='*104}")
print("MAGNETISM: share of 5-minute closes sitting within 1/6 of a grid level vs in the middle third.")
print("No preference = 33.3% near / 33.3% middle.")
print(f"{'='*104}")
print(f"{'spacing':>9} | {'ROUND near':>11}{'mid':>9} | {'shift S/2 near':>15}{'mid':>9} | {'shift S/3 near':>15}{'mid':>9}")
for S in [1, 2.5, 5, 10, 12.5, 25, 50, 100]:
    cells = []
    for ph in [0.0, S/2, S/3]:
        nr, md = magnet(S, cl - ph)
        cells.append((nr, md))
    print(f"{S:>9.1f} | {100*cells[0][0]:>10.2f}%{100*cells[0][1]:>8.2f}% | "
          f"{100*cells[1][0]:>14.2f}%{100*cells[1][1]:>8.2f}% | {100*cells[2][0]:>14.2f}%{100*cells[2][1]:>8.2f}%")
