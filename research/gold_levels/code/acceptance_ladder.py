"""The acceptance ladder, against the number a coin flip already predicts.

The reported result is that once gold has "accepted" x dollars beyond a $25
quarter without recrossing it, the chance of completing the move to the next
quarter climbs 8.6% -> 50.5% -> 76% as x goes 0.25 -> 12.5 -> 20, and that the
50% crossover lands at the halfway mark on EVERY grid size tested.

There is a closed form for that. For a driftless walk starting x above the lower
boundary of an interval of width S, the probability of touching the upper
boundary before the lower one is exactly x/S. So x/S = 0.5 at x = S/2 -- for
every S, at every scale, in any market, and in simulated noise. The "fractal
price-quarter behaviour" is the arithmetic of a fair game, not a property of
gold.

This script measures the ladder tick-exactly and prints x/S beside it, then
repeats the whole thing on phase-shifted grids. If the ladder is structural,
the shifted grids produce the same ladder.

Method: label every tick by which grid cell it sits in. A crossing is a change
of cell. Within one uninterrupted run inside a cell, price by definition has not
touched either boundary, so the run's maximum IS the acceptance reached, and the
side it exits on IS the first passage. No path is assumed anywhere.
"""
import numpy as np

BASE = "/home/user/Trade_Cartel/research/gold_10am_flip/data"
bid = np.load(f"{BASE}/tk_bid.npy", mmap_mode="r")
ask = np.load(f"{BASE}/tk_ask.npy", mmap_mode="r")
N = len(bid)
mid = np.empty(N, np.float64)
CH = 4_000_000
for i in range(0, N, CH):
    mid[i:i + CH] = (bid[i:i + CH].astype(np.float64) + ask[i:i + CH].astype(np.float64)) / 2000.0
print(f"ticks: {N:,}   mid {mid.min():.2f} .. {mid.max():.2f}")

THRESH = [0.25, 1, 2, 5, 7.5, 10, 12.5, 15, 20]


def ladder(S, phase):
    """-> (n_events, dict x0 -> P(complete next level | accepted x0), overall P)."""
    cell = np.floor((mid - phase) / S).astype(np.int32)
    ch = np.flatnonzero(np.diff(cell)) + 1          # first tick of each new run
    starts = np.concatenate([[0], ch])
    ends = np.concatenate([ch, [N]])                # run i is mid[starts[i]:ends[i]]
    k = cell[starts]
    # entered from below (k rose) and left upward / downward
    entered_up = np.concatenate([[False], np.diff(k) > 0])
    left_up = np.concatenate([np.diff(k) > 0, [False]])
    left_dn = np.concatenate([np.diff(k) < 0, [False]])
    # a clean event: entered from below, and left to an ADJACENT cell
    ok = entered_up & (left_up | left_dn) & (np.abs(np.concatenate([np.diff(k), [0]])) == 1)
    idx = np.flatnonzero(ok)
    lower = k[idx] * S + phase
    acc = np.array([mid[starts[i]:ends[i]].max() for i in idx]) - lower
    cont = left_up[idx]
    out = {}
    for x in THRESH:
        m = acc >= x
        out[x] = (cont[m].mean() if m.sum() else np.nan, int(m.sum()))
    return len(idx), out, cont.mean()


print(f"\n{'='*104}")
print("P(reach the NEXT level before falling back through the one just crossed), given acceptance x")
print("x/S is the fair-coin value: the probability for a driftless walk, with no level effect at all.")
print(f"{'='*104}")
for S in (6.25, 12.5, 25.0, 50.0, 100.0):
    n, tab, base = ladder(S, 0.0)
    print(f"\n$ {S:<6g} grid   {n:,} crossing events   immediate continuation {100*base:.2f}%")
    print(f"   {'acceptance x':<14}{'observed':>10}{'x/S (coin)':>12}{'diff':>8}{'n':>10}")
    for x in THRESH:
        if x >= S: continue
        p, m = tab[x]
        print(f"   ${x:<13g}{100*p:>9.1f}%{100*x/S:>11.1f}%{100*(p-x/S):>+7.1f}{m:>10,}")

print(f"\n{'='*104}")
print("SAME LADDER ON GRIDS THAT ARE NOT ROUND ($25 spacing, phase shifted)")
print(f"{'='*104}")
print(f"{'phase':<10}{'events':>10}{'immediate':>11}" + "".join(f"{'x='+str(x):>9}" for x in [5, 10, 12.5, 15, 20]))
for ph in (0.0, 3.0, 6.25, 8.0, 12.5, 17.0, 21.0):
    n, tab, base = ladder(25.0, ph)
    row = f"{ph:<10g}{n:>10,}{100*base:>10.2f}%"
    for x in [5, 10, 12.5, 15, 20]:
        row += f"{100*tab[x][0]:>8.1f}%"
    print(row + ("   <- round" if ph == 0 else ""))

print(f"\n{'='*104}")
print("DOES THE LAST DIGIT MATTER?  immediate continuation by which quarter was crossed ($25 grid)")
print(f"{'='*104}")
S = 25.0
cell = np.floor(mid / S).astype(np.int32)
ch = np.flatnonzero(np.diff(cell)) + 1
starts = np.concatenate([[0], ch]); k = cell[starts]
entered_up = np.concatenate([[False], np.diff(k) > 0])
left_up = np.concatenate([np.diff(k) > 0, [False]])
left_dn = np.concatenate([np.diff(k) < 0, [False]])
ok = entered_up & (left_up | left_dn) & (np.abs(np.concatenate([np.diff(k), [0]])) == 1)
idx = np.flatnonzero(ok)
lower = k[idx] * S
ending = np.round(lower % 100).astype(int)
cont = left_up[idx]
print(f"{'level ends':<12}{'events':>10}{'immediate continuation':>26}")
for e in (0, 25, 50, 75):
    m = ending == e
    print(f"{'x'+f'{e:02d}':<12}{int(m.sum()):>10,}{100*cont[m].mean():>25.2f}%")
sd = np.sqrt(cont.mean() * (1 - cont.mean()) / min([(ending == e).sum() for e in (0, 25, 50, 75)]))
print(f"\nbinomial sd on the smallest bucket: {100*sd:.2f}pp  "
      f"-- spread across the four buckets: {100*(max(cont[ending==e].mean() for e in (0,25,50,75)) - min(cont[ending==e].mean() for e in (0,25,50,75))):.2f}pp")
