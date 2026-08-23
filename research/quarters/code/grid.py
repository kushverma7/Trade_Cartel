"""QUARTERS THEORY ON GOLD — grid geometry and the first-passage asymmetry.

Yotov's rules are all FRACTIONS of the large quarter S, so the system is
scale-free and ports to gold by choosing S:

    completion tolerance   0.10 S   (25 of 250 pips)
    overshoot / not decisive 0.10 S
    hesitation zone        0.30 S   (75 of 250 pips)
    half point             0.50 S
    target                 1.00 S   (the next large quarter point)
    reversal target        1.00 S   back to the preceding quarter point

Gold has no pip convention, so S is a RESEARCHER DEGREE OF FREEDOM. Every scale
is therefore tested, and every scale is tested against PHASE-SHIFTED grids of
identical spacing. A grid at phase p has lines at p + j*S. The round grid is
p = 0. If the round grid does not beat the shifted distribution, roundness
carries no information and only the spacing matters.

THE DECISIVE MEASUREMENT. From a crossing of quarter point Q, does price reach
Q+S before Q-S (continuation) or Q-S before Q+S (reversal)? For a driftless
walk starting at a boundary this is 0.50 by gambler's ruin (H99), on any grid,
in any market. Yotov's premise requires continuation to beat 0.50 on the ROUND
grid specifically.
"""
import os, sys, numpy as np

sys.path.insert(0, "research/goldmap/code")
from qt_engine import Book, PTS

DATA = {"2025-26": "research/microq3/data", "2024-25": "research/microq3/data_holdout"}


def cell_sequence(mid, S_i, phase_i):
    """Compressed sequence of grid-cell indices.

    cell c spans [phase + c*S, phase + (c+1)*S). Returns the tick index and the
    cell index at every point the cell changes, plus the cell at tick 0.
    Working on the compressed sequence rather than the raw ticks is what makes
    the first-passage scan affordable: gold spends long stretches inside one
    cell and the sequence is 2-3 orders of magnitude shorter than the tape.
    """
    cell = np.floor_divide(mid - phase_i, S_i).astype(np.int64)
    chg = np.flatnonzero(cell[1:] != cell[:-1]) + 1
    idx = np.concatenate([[0], chg])
    return idx, cell[idx]


def first_passage(cells, cap=200_000):
    """For every cell change, does the sequence reach one cell further in the
    direction of travel before one cell back past the origin?

    Crossing UP into cell c means price crossed line c (= Q). Q+S is line c+1,
    reached by entering cell c+1. Q-S is line c-1, reached by entering cell c-2.
    So: continuation iff the sequence hits >= c+1 before <= c-2.
    Crossing DOWN into cell c means price crossed line c+1 (= Q). Q-S is line c,
    reached by entering cell c-1. Q+S is line c+2, reached by entering c+2.
    So: continuation iff the sequence hits <= c-1 before >= c+2.

    Returns (event_positions, direction, outcome) where outcome is
    +1 continuation, -1 reversal, 0 unresolved by the end of the data.
    """
    n = len(cells)
    pos, dirn, out = [], [], []
    for k in range(1, n):
        c, prev = cells[k], cells[k - 1]
        if c == prev:
            continue
        up = c > prev
        if up:
            hi, lo = c + 1, c - 2          # continuation up / reversal down
        else:
            hi, lo = c + 2, c - 1          # reversal up / continuation down
        res = 0
        end = min(n, k + cap)
        for j in range(k + 1, end):
            v = cells[j]
            if v >= hi:
                res = +1 if up else -1
                break
            if v <= lo:
                res = -1 if up else +1
                break
        pos.append(k); dirn.append(1 if up else -1); out.append(res)
    return np.array(pos), np.array(dirn), np.array(out, np.int8)


def _fp_fast(cells, cap=200_000):
    """Vectorised-ish first passage. Same contract as first_passage but avoids
    the inner Python loop for the common case by scanning with numpy over a
    bounded window."""
    n = len(cells)
    chg = np.flatnonzero(cells[1:] != cells[:-1]) + 1
    out = np.zeros(len(chg), np.int8)
    dirn = np.where(cells[chg] > cells[chg - 1], 1, -1).astype(np.int8)
    for m, k in enumerate(chg):
        c = cells[k]
        up = dirn[m] == 1
        hi, lo = (c + 1, c - 2) if up else (c + 2, c - 1)
        end = min(n, k + cap)
        seg = cells[k + 1:end]
        if len(seg) == 0:
            continue
        a = np.flatnonzero(seg >= hi)
        b = np.flatnonzero(seg <= lo)
        ia = a[0] if len(a) else 1 << 60
        ib = b[0] if len(b) else 1 << 60
        if ia == ib:
            continue
        if ia < ib:
            out[m] = +1 if up else -1
        else:
            out[m] = -1 if up else +1
    return chg, dirn, out


def asymmetry(book, S, phase_frac, cap=200_000):
    """P(continuation) from a quarter-point crossing, on the grid of spacing S
    offset by phase_frac * S. H99 predicts 0.50 for a driftless walk."""
    S_i = int(round(S * PTS))
    phase_i = int(round(phase_frac * S_i))
    idx, cells = cell_sequence(book.mid, S_i, phase_i)
    chg, dirn, out = _fp_fast(cells, cap)
    res = out[out != 0]
    if len(res) == 0:
        return None
    up = dirn[out != 0] == 1
    cont = res == +1
    return dict(
        n=len(res),
        p_cont=float(cont.mean()),
        n_up=int(up.sum()),
        p_cont_up=float(cont[up].mean()) if up.any() else np.nan,
        p_cont_dn=float(cont[~up].mean()) if (~up).any() else np.nan,
        unresolved=int((out == 0).sum()),
        crossings=len(chg),
    )
