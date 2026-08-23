"""WHY IS P(continuation) ABOVE 0.500 AT ALL?

The deviation is not drift and not market structure -- it is the OVERSHOOT of
the crossing tick. Prices move in discrete jumps, so when the tape crosses a
grid line it lands some distance PAST it. That leaves price already nearer the
next line than the previous one, which biases the first-passage race toward
continuation by roughly overshoot/S.

Prediction: the bias should scale as 1/S. Measured below against the observed
excess. If it matches, the deviation is an artefact of the crossing definition
and has nothing to do with round numbers -- which is also why every phase
returns the same number.
"""
import sys, numpy as np
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from grid import Book, DATA
from qt_engine import PTS

OBS = {  # observed excess of P(cont) over 0.500, round grid, from asymmetry.log
 "2025-26": {2.5:.0231, 5:.0123, 10:.0065, 12.5:.0052, 25:.0027, 50:.0016, 100:.0010, 250:.0005},
 "2024-25": {2.5:.0100, 5:.0051, 10:.0026, 12.5:.0021, 25:.0012},
}
for year, d in DATA.items():
    b = Book(d, year)
    print(f"\n{'='*96}\n{year}\n{'='*96}")
    print(f"  {'S':>8}{'mean overshoot $':>18}{'overshoot/2S':>14}{'observed excess':>17}{'ratio':>8}")
    for S, obs in OBS[year].items():
        S_i = int(round(S * PTS))
        cell = np.floor_divide(b.mid, S_i)
        chg = np.flatnonzero(cell[1:] != cell[:-1]) + 1
        up = cell[chg] > cell[chg - 1]
        line = np.where(up, cell[chg], cell[chg] + 1) * S_i
        ov = np.abs(b.mid[chg] - line) / PTS          # how far past the line it landed
        m = float(ov.mean())
        pred = m / (2 * S)                            # first-passage bias from a head start
        print(f"  {S:>8.2f}{m:>18.4f}{pred:>14.4f}{obs:>17.4f}{obs/pred:>8.2f}")
    del b
print("\n  A ratio near 1 means the excess IS the crossing overshoot. The bias falls as")
print("  1/S because the overshoot is a roughly fixed number of dollars set by tick")
print("  size and volatility, while S grows. Nothing about roundness enters.")
