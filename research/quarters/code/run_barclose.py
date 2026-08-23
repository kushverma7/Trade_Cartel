"""THE FAIRER IMPLEMENTATION — trigger on a BAR CLOSE, not a tick touch.

The tick-touch version fires whenever any single print reaches 0.30*S past the
quarter point. Yotov does not trade that way: he reads 60-minute and daily
charts and judges a move "decisive" from where the bar CLOSES. Tick-touch is
the most aggressive possible reading and generates the most trades, so if the
system loses only from overtrading, this variant is where it would show.

Trigger: the first H1 (or D1) close beyond Q +/- 0.30*S, entered at the next
tick. Everything else -- stop at Q, target the next quarter point, 3-day
clock, real bid/ask fills -- is unchanged.
"""
import sys, time, numpy as np, pandas as pd
sys.path.insert(0, "research/quarters/code"); sys.path.insert(0, "research/goldmap/code")
from system import Book, stats, PTS
from grid import DATA

DAY_MS = 86_400_000


def bars(book, ms):
    """Bar close price and the tick index of each close."""
    b = book.ny // ms
    end = np.concatenate([np.flatnonzero(b[1:] != b[:-1]), [len(b) - 1]])
    return book.mid[end], end


def run_bars(book, S, phase_frac, bar_ms, zone=0.30, tgt=1.0, days=3):
    S_i = int(round(S * PTS)); ph = int(round(phase_frac * S_i))
    close, kend = bars(book, bar_ms)
    ny, bid, ask, mid = book.ny, book.bid, book.ask, book.mid
    zi = int(round(zone * S_i)); ti = int(round(tgt * S_i))
    trades, busy = [], -1
    prev_cell = (close[0] - ph) // S_i
    for i in range(1, len(close)):
        k = int(kend[i])
        if k <= busy:
            prev_cell = (close[i] - ph) // S_i
            continue
        c = (close[i] - ph) // S_i
        if c == prev_cell:
            continue
        up = c > prev_cell
        q = (int(prev_cell) + 1 if up else int(prev_cell)) * S_i + ph
        prev_cell = c
        # decisive: the close must be 0.30*S beyond Q, not merely past it
        if up and close[i] < q + zi:
            continue
        if (not up) and close[i] > q - zi:
            continue
        k0 = k + 1
        if k0 >= len(ny):
            break
        e = int(ask[k0]) if up else int(bid[k0])
        stop_px, tgt_px = q, (q + ti if up else q - ti)
        risk = abs(e - stop_px)
        if risk <= 0:
            continue
        t_end = ny[k0] + days * DAY_MS
        j = k0
        lim = int(np.searchsorted(ny, t_end, "right"))
        if up:
            seg = bid[k0:lim]
            hit_t = np.flatnonzero(seg >= tgt_px); hit_s = np.flatnonzero(seg <= stop_px)
        else:
            seg = ask[k0:lim]
            hit_t = np.flatnonzero(seg <= tgt_px); hit_s = np.flatnonzero(seg >= stop_px)
        it = hit_t[0] if len(hit_t) else 1 << 60
        isl = hit_s[0] if len(hit_s) else 1 << 60
        if it < isl:
            pnl, tag, kx = (tgt_px - e) if up else (e - tgt_px), "TP", k0 + it
        elif isl < 1 << 60:
            kx = k0 + isl
            pnl, tag = ((int(bid[kx]) - e) if up else (e - int(ask[kx]))), "SL"
        else:
            kx = min(lim, len(ny)) - 1
            pnl, tag = ((int(bid[kx]) - e) if up else (e - int(ask[kx]))), "TIME"
        trades.append((int(ny[k0]), 1 if up else -1, e / PTS, pnl / PTS,
                       pnl / risk, tag, (int(ny[kx]) - int(ny[k0])) / 60000.0))
        busy = kx
    return trades


rows = []
for year, d in DATA.items():
    b = Book(d, year)
    print(f"\n{'='*104}\n{year}\n{'='*104}", flush=True)
    for bar, bms in (("H1", 3_600_000), ("D1", DAY_MS)):
        print(f"\n  {bar} close trigger")
        print(f"  {'S':>8}{'phase':>7}{'n':>6}{'PF':>8}{'exp R':>9}{'net R':>9}"
              f"{'net $':>10}{'WR':>7}{'TP/SL/T':>13}{'hold':>8}")
        for S in (25.0, 50.0, 100.0, 250.0):
            for k in (0, 3, 6, 9):          # round + three shifted phases
                tr = run_bars(b, S, k / 12, bms)
                s = stats(tr)
                if s is None or s["n"] < 5:
                    continue
                rows.append(dict(year=year, bar=bar, S=S, k=k, round=(k == 0), **s))
                mix = "%d/%d/%d" % (s['tp'], s['sl'], s['time'])
                print(f"  {S:>8.2f}{('ROUND' if k==0 else f'{k}/12'):>7}{s['n']:>6}"
                      f"{s['pf']:>8.3f}{s['exp']:>+9.4f}{s['net_R']:>+9.1f}"
                      f"{s['net_usd']:>+10.0f}{s['wr']:>6.1f}%{mix:>13}{s['hold']:>7.0f}m",
                      flush=True)
    del b
pd.DataFrame(rows).to_csv("research/quarters/results/barclose.csv", index=False)
print("\nwritten -> research/quarters/results/barclose.csv")
