"""QUARTERS THEORY ON GOLD — the full Hesitation Zone system, tick-exact.

The system assembled from Yotov's webinars 4 and 5, ported to gold by choosing
the large-quarter size S (every rule is a fraction of S, so it is scale-free):

    trigger    price crosses quarter point Q, then penetrates 0.30*S past it
               (the far edge of the Hesitation Zone). Yotov calls a penetration
               of <=0.10*S "just an overshoot", not decisive.
    abort      if price falls back 0.10*S the wrong side of Q first, no trade
    entry      at the trigger, paying the real spread
    stop       back through Q (the pullback-hold test failing)
    target     the next quarter point, Q +/- S
    time stop  3 days (the Three-Day Rule)

FILL CONVENTION (identical to research/insample/code/resolve.py):
    long enters ASK and is marked out on BID; short enters BID, marked out on
    ASK. The TARGET is a resting limit at the exact price -- it fills AT the
    target, favourable overshoot is NEVER credited. The STOP is market-triggered
    at the real next executable quote, including slippage.

GRID ARITHMETIC. Fine line W sits at price ph + W*f where f = S/SUB. Cell
v = floor((price-ph)/f) spans [ph+v*f, ph+(v+1)*f). So:
    price >= line W   <=>   cell >= W          (exact)
    price <= line W   <=>   cell <= W-1        (strictly below; conservative
                                                by less than f = 0.01*S)
Getting this asymmetry wrong is what an earlier version did: it used cell <= W
for downward tests, firing short triggers 0.05*S early and inflating R.

Trades never overlap: after an exit, no new event is considered until the exit
tick. All P&L is in R, where 1R = the realised entry-to-stop distance.
"""
import sys, numpy as np
sys.path.insert(0, "research/goldmap/code")
from qt_engine import Book, PTS

SUB = 100                     # fine grid = S/100, so discretisation is 1% of S
DAY_MS = 86_400_000


def fine(series, S_i, phase_i):
    """(tick index, cell) at every fine-grid cell change, as int32."""
    f = S_i // SUB
    cell = np.floor_divide(series.astype(np.int64) - phase_i, f)
    chg = np.flatnonzero(cell[1:] != cell[:-1]) + 1
    idx = np.empty(len(chg) + 1, np.int64); idx[0] = 0; idx[1:] = chg
    return idx, cell[idx].astype(np.int32), f


def _race(idx, cells, pos, up_lvl, dn_lvl, want_up, t_end, ny):
    """Scan forward from position `pos`. Returns (tick index, outcome) where
    outcome is 'WIN' if the wanted side is reached first, 'LOSE' if the other
    side is, 'TIME' if neither before t_end.
    up_lvl is a cell threshold tested with >=, dn_lvl with <=."""
    n = len(cells)
    last = pos
    for j in range(pos + 1, n):
        k = idx[j]
        if ny[k] > t_end:
            return idx[last], "TIME"
        v = cells[j]
        if v >= up_lvl:
            return k, "WIN" if want_up else "LOSE"
        if v <= dn_lvl:
            return k, "LOSE" if want_up else "WIN"
        last = j
    return idx[last], "TIME"


def prep(book, S, phase_frac):
    """Build the three fine grids once so every config variant can reuse them.
    Grid construction dominates the runtime, so this is what makes a full
    phase x config sweep affordable."""
    S_i = int(round(S * PTS))
    ph = int(round(phase_frac * S_i))
    return dict(S_i=S_i, ph=ph, f=S_i // SUB,
                m=fine(book.mid, S_i, ph)[:2],
                b=fine(book.bid, S_i, ph)[:2],
                a=fine(book.ask, S_i, ph)[:2])


def run(book, S, phase_frac, zone=0.30, abort=0.10, stop_at=0.0, tgt=1.0,
        days=3, decisive=True, grids=None):
    """One pass of the system over one year. Returns a list of trades:
    (t_entry_ms, direction, entry$, pnl$, pnl_R, exit_tag, hold_minutes)."""
    g = grids if grids is not None else prep(book, S, phase_frac)
    S_i, ph, f = g["S_i"], g["ph"], g["f"]
    z, ab = int(round(zone * SUB)), max(int(round(abort * SUB)), 1)
    st, tg = int(round(stop_at * SUB)), int(round(tgt * SUB))

    (idx_m, cm), (idx_b, cb), (idx_a, ca) = g["m"], g["b"], g["a"]
    ny, bid, ask = book.ny, book.bid, book.ask

    trades, busy = [], -1
    for j in range(1, len(cm)):
        k0 = idx_m[j]
        if k0 <= busy:
            continue
        c, prev = cm[j], cm[j - 1]
        up = c > prev
        # first quarter line crossed in the direction of travel
        if up:
            q = -(-(int(prev) + 1) // SUB) * SUB
            if q > c:
                continue
        else:
            q = (int(prev) // SUB) * SUB
            if q < c + 1:
                continue

        if decisive:
            if up:
                kt, why = _race(idx_m, cm, j, q + z, q - ab - 1, True,
                                ny[k0] + days * DAY_MS, ny)
            else:
                kt, why = _race(idx_m, cm, j, q + ab, q - z - 1, False,
                                ny[k0] + days * DAY_MS, ny)
            if why != "WIN":
                continue
        else:
            kt = k0

        e = int(ask[kt]) if up else int(bid[kt])
        stop_px = ph + (q - st) * f if up else ph + (q + st) * f
        tgt_px = ph + (q + tg) * f if up else ph + (q - tg) * f
        risk = abs(e - stop_px)
        if risk < f:
            continue
        t_end = ny[kt] + days * DAY_MS

        if up:                                    # long: marked out on BID
            p0 = max(int(np.searchsorted(idx_b, kt, "right")) - 1, 0)
            kx, why = _race(idx_b, cb, p0, q + tg, q - st - 1, True, t_end, ny)
            pnl = (tgt_px - e) if why == "WIN" else (int(bid[kx]) - e)
        else:                                     # short: marked out on ASK
            p0 = max(int(np.searchsorted(idx_a, kt, "right")) - 1, 0)
            kx, why = _race(idx_a, ca, p0, q + st, q - tg - 1, False, t_end, ny)
            pnl = (e - tgt_px) if why == "WIN" else (e - int(ask[kx]))

        trades.append((int(ny[kt]), 1 if up else -1, e / PTS, pnl / PTS,
                       pnl / risk, {"WIN": "TP", "LOSE": "SL", "TIME": "TIME"}[why],
                       (int(ny[kx]) - int(ny[kt])) / 60000.0))
        busy = kx
    return trades


def stats(trades):
    if not trades:
        return None
    r = np.array([t[4] for t in trades], float)
    p = np.array([t[3] for t in trades], float)
    gp, gl = r[r > 0].sum(), -r[r < 0].sum()
    eq = np.cumsum(r); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    tags = [t[5] for t in trades]
    return dict(n=len(r), pf=(gp / gl if gl > 0 else np.inf), exp=float(r.mean()),
                net_R=float(r.sum()), net_usd=float(p.sum()),
                wr=100 * float((r > 0).mean()), dd=float((pk - eq).max()),
                tp=tags.count("TP"), sl=tags.count("SL"), time=tags.count("TIME"),
                hold=float(np.median([t[6] for t in trades])))
