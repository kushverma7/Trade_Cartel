"""THE FAIRER IMPLEMENTATION — trigger on a BAR CLOSE, not a tick touch.

The tick-touch version fires whenever any single print reaches 0.30*S past the
quarter point. Yotov does not trade that way: he reads 60-minute and daily
charts and judges a move "decisive" from where the bar CLOSES. Tick-touch is
the most aggressive possible reading and generates the most trades, so if the
system loses only from overtrading, this variant is where it would show.

Trigger: the first H1 or D1 close beyond Q +/- 0.30*S, entered at the next tick.
Everything else -- stop at Q, target the next quarter point, 3-day clock, real
bid/ask fills -- is unchanged, and resolution reuses the SAME fine-grid racer
system.py uses. (A first version scanned up to three days of raw ticks per
trade with flatnonzero, which is O(window) per trade and far too slow.)
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from system import Book, stats, prep, _race, SUB, PTS
from grid import DATA

DAY_MS = 86_400_000
SCALES = [25.0, 50.0, 100.0, 250.0]
PHASES = [0, 3, 6, 9]                 # round plus three shifted grids


def bars(book, ms):
    """Close price and closing tick index of every bar."""
    b = book.ny // ms
    end = np.concatenate([np.flatnonzero(b[1:] != b[:-1]), [len(b) - 1]])
    return book.mid[end], end


def run_bars(book, S, bar_ms, grids, zone=0.30, tgt=1.0, days=3):
    S_i, ph, f = grids["S_i"], grids["ph"], grids["f"]
    (idx_b, cb), (idx_a, ca) = grids["b"], grids["a"]
    close, kend = bars(book, bar_ms)
    ny, bid, ask = book.ny, book.bid, book.ask
    tg = int(round(tgt * SUB))
    zi = zone * S_i

    trades, busy = [], -1
    prev = int((close[0] - ph) // S_i)
    for i in range(1, len(close)):
        k = int(kend[i])
        c = int((close[i] - ph) // S_i)
        if k <= busy:
            prev = c
            continue
        if c == prev:
            continue
        up = c > prev
        qc = (prev + 1) if up else prev          # quarter line, in coarse units
        Q = ph + qc * S_i
        prev = c
        # decisive: the CLOSE must sit 0.30*S beyond Q, not merely past it
        if up and close[i] < Q + zi:
            continue
        if (not up) and close[i] > Q - zi:
            continue
        k0 = k + 1
        if k0 >= len(ny):
            break
        e = int(ask[k0]) if up else int(bid[k0])
        qf = qc * SUB                            # the same line in fine units
        tgt_px = Q + tg * f if up else Q - tg * f
        risk = abs(e - Q)
        if risk < f:
            continue
        t_end = ny[k0] + days * DAY_MS
        if up:                                   # long: marked out on BID
            p0 = max(int(np.searchsorted(idx_b, k0, "right")) - 1, 0)
            kx, why = _race(idx_b, cb, p0, qf + tg, qf - 1, True, t_end, ny)
            pnl = (tgt_px - e) if why == "WIN" else (int(bid[kx]) - e)
        else:                                    # short: marked out on ASK
            p0 = max(int(np.searchsorted(idx_a, k0, "right")) - 1, 0)
            kx, why = _race(idx_a, ca, p0, qf, qf - tg - 1, False, t_end, ny)
            pnl = (e - tgt_px) if why == "WIN" else (e - int(ask[kx]))
        trades.append((int(ny[k0]), 1 if up else -1, e / PTS, pnl / PTS,
                       pnl / risk, {"WIN": "TP", "LOSE": "SL", "TIME": "TIME"}[why],
                       (int(ny[kx]) - int(ny[k0])) / 60000.0))
        busy = kx
    return trades


rows = []
for year, d in DATA.items():
    b = Book(d, year)
    print(f"\n{'='*104}\n{year}\n{'='*104}", flush=True)
    for S in SCALES:
        grids = {k: prep(b, S, k / 12) for k in PHASES}
        for bar, bms in (("H1", 3_600_000), ("D1", DAY_MS)):
            print(f"\n  {bar} close trigger, S = ${S:.0f}")
            print(f"  {'phase':>7}{'n':>6}{'PF':>8}{'exp R':>9}{'net R':>9}"
                  f"{'net $':>10}{'WR':>7}{'TP/SL/T':>13}{'hold':>8}")
            for k in PHASES:
                tr = run_bars(b, S, bms, grids[k])
                s = stats(tr)
                if s is None or s["n"] < 5:
                    print(f"  {('ROUND' if k==0 else f'{k}/12'):>7}"
                          f"{(0 if s is None else s['n']):>6}   (too few trades)", flush=True)
                    continue
                rows.append(dict(year=year, bar=bar, S=S, k=k, round=(k == 0), **s))
                mix = "%d/%d/%d" % (s['tp'], s['sl'], s['time'])
                print(f"  {('ROUND' if k==0 else f'{k}/12'):>7}{s['n']:>6}"
                      f"{s['pf']:>8.3f}{s['exp']:>+9.4f}{s['net_R']:>+9.1f}"
                      f"{s['net_usd']:>+10.0f}{s['wr']:>6.1f}%{mix:>13}{s['hold']:>7.0f}m",
                      flush=True)
        del grids
    del b
pd.DataFrame(rows).to_csv("research/quarters/results/barclose.csv", index=False)
print("\nwritten -> research/quarters/results/barclose.csv")
