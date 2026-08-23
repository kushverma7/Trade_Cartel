"""Step 3 — the Quarter Theory state machine as an event table, tick-exact.

ARCHITECTURE. The coarse $25 grid is used only to FIND attempts, which is cheap.
Everything else is computed on the RAW tick arrays inside each attempt's window:
attempts average ~1,100 ticks, so a full pass costs about one sweep of the tape
and nothing is quantised to a grid. That matters here because the targets under
test go down to $0.50 and a $0.25 grid would blur them.

RUNGS, as dollars from the originating LQP (mirrored for bearish):
    0.00 LQP | 2.50 overshoot | 7.50 HZ | 12.50 half | 20.00 whole
    22.50 completion | 25.00 next LQP

AN ATTEMPT starts when mid crosses an LQP and ends when mid either reaches the
next LQP one quarter away (TARGET) or loses the originating LQP (LOST), or a
3-day clock expires (STALE).

ACCEPTANCE vs TOUCH (the brief's section 8). At each rung six entry definitions
are located, so the same event can be traded six ways on identical ticks:
    TOUCH         first tick at or beyond the rung
    EXC(x)        first tick x dollars beyond it
    DWELL(T)      first tick after T continuous seconds beyond it
    TICKS(n)      first tick after n consecutive ticks beyond it
    RETEST        beyond -> back to within the rung -> beyond again, LQP intact
    CLOSE(m)      first m-minute bar close beyond it
Each yields a different entry price and a different remaining distance to the
next rung, so each has its OWN geometric baseline. They are compared against
that, never against each other's raw win rates.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from system import fine, SUB
from qt_engine import Book, PTS

Q_I = 25_000                       # $25 large quarter, in integer thousandths
RUNGS = [("lqp", 0), ("over", 2_500), ("hz", 7_500), ("half", 12_500),
         ("whole", 20_000), ("comp", 22_500), ("tgt", 25_000)]
RIDX = {n: i for i, (n, _) in enumerate(RUNGS)}
DAY_MS = 86_400_000


def attempts(book, phase_i=0, max_open_ms=3 * DAY_MS):
    """Locate every LQP attempt on the coarse grid. Returns arrays, not a frame:
    (k0, kx, q_i, up, res) with q_i the originating LQP in integer price."""
    idx, cells, f = fine(book.mid, Q_I, phase_i)
    n = len(cells)
    ny = book.ny
    k0s, kxs, qs, ups, res = [], [], [], [], []
    j = 1
    while j < n:
        c, prev = int(cells[j]), int(cells[j - 1])
        up = c > prev
        if up:
            qc = -(-(prev + 1) // SUB) * SUB
            if qc > c:
                j += 1; continue
        else:
            qc = (prev // SUB) * SUB
            if qc < c + 1:
                j += 1; continue
        hi, lo = (qc + SUB, qc - 1) if up else (qc + 1, qc - SUB)
        k, t0, out = int(idx[j]), int(ny[idx[j]]), "STALE"
        for m in range(j, n):
            v = int(cells[m]); k = int(idx[m])
            if (up and v >= hi) or ((not up) and v <= lo):
                out = "TARGET"; break
            if (up and v <= lo) or ((not up) and v >= hi):
                out = "LOST"; break
            if int(ny[k]) - t0 > max_open_ms:
                break
        k0s.append(int(idx[j])); kxs.append(k); qs.append(phase_i + qc * f)
        ups.append(up); res.append(out)
        while j < n and idx[j] <= k:
            j += 1
    del idx, cells
    return (np.array(k0s), np.array(kxs), np.array(qs, np.int64),
            np.array(ups), np.array(res))


def entries_at_rung(prog, ny, r_i, exc_i, dwell_ms, n_ticks):
    """Locate the six acceptance entries for one rung inside one attempt.

    `prog` is signed progress in integer dollars-thousandths from the LQP, so
    the same code serves bullish and bearish attempts. Returns a dict of
    definition -> offset into the attempt window, or -1 when never satisfied.
    """
    out = {k: -1 for k in ("touch", "exc", "dwell", "ticks", "retest")}
    beyond = prog >= r_i
    if not beyond.any():
        return out
    i_touch = int(np.argmax(beyond))
    out["touch"] = i_touch

    far = prog >= r_i + exc_i
    if far.any():
        out["exc"] = int(np.argmax(far))

    # DWELL / TICKS: the first index at which the CURRENT unbroken run of
    # "beyond" has lasted long enough. Runs are found from the boundaries of
    # `beyond`, so a dip back below the rung resets the clock.
    b = beyond.astype(np.int8)
    edges = np.flatnonzero(np.diff(b)) + 1
    starts = np.concatenate(([0], edges))
    ends = np.concatenate((edges, [len(b)]))
    for s, e in zip(starts, ends):
        if not b[s]:
            continue
        if out["dwell"] < 0:
            j = int(np.searchsorted(ny[s:e], ny[s] + dwell_ms, "left"))
            if s + j < e:
                out["dwell"] = s + j
        if out["ticks"] < 0 and e - s >= n_ticks:
            out["ticks"] = s + n_ticks - 1
        if out["dwell"] >= 0 and out["ticks"] >= 0:
            break

    # RETEST: go exc beyond, come back to within the rung (but never lose the
    # LQP -- the attempt would have ended), then exceed the prior high again.
    if out["exc"] >= 0:
        i = out["exc"]
        back = np.flatnonzero(prog[i:] < r_i)
        if len(back):
            j = i + int(back[0])
            peak = int(prog[:j].max())
            again = np.flatnonzero(prog[j:] >= peak)
            if len(again):
                out["retest"] = j + int(again[0])
    return out
