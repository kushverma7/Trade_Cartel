"""The 10AM A+Flip logics, executed against real quotes.

SIGNALS are a faithful port of the supplied Pine: the 09:50 bar's open is the
daily line, the 10:00 bar's BODY (max/min of open,close) is the box, `side` is
which way that body closed relative to the line, and a close beyond the body AND
beyond the line arms an entry. The per-day aDone/fDone latches, the one-position
rule and the end-of-day flatten are reproduced, including the Pine detail that a
latch is only set when a trade is actually TAKEN, not when a signal merely fires.

EXECUTION is where this departs from the Pine, deliberately and in the honest
direction. The Pine models cost by shrinking the stop and target by half a
"cost" input, which assumes a cost instead of paying one, and it resolves stops
and targets on bar data, which forces a guess about the intrabar path. Here:

  * a long enters at the ASK and exits at the BID; a short does the reverse.
    The round-trip spread is therefore PAID at whatever it actually was at that
    instant, not assumed. No cost input exists, because none is needed.
  * once a position is open, the exit is found by walking real ticks forward in
    arrival order. If both the stop and the target lie inside one bar, the tick
    that arrived first wins. Nothing is assumed about which was touched first.

That second point is the whole reason for using tick data. This repo has seen
five separate "champions" dissolve when their fill assumption was attacked, so
the fill assumption is removed rather than refined.
"""
import numpy as np, pandas as pd

PTS = 1000.0                      # integer points <-> dollars


class Ticks:
    """Session quote stream, integer points, sorted by time."""
    def __init__(self, arr):
        self.t = np.ascontiguousarray(arr[:, 0])
        self.bid = np.ascontiguousarray(arr[:, 1])
        self.ask = np.ascontiguousarray(arr[:, 2])

    def slice_from(self, t0, t1):
        i = np.searchsorted(self.t, t0, side="right")   # strictly after entry
        j = np.searchsorted(self.t, t1, side="right")
        return i, j


def build_days(bars, line_hhmm=950, body_hhmm=1000, end_hr=23):
    """Per-day state: the line, the body box, and the side. Days that cannot be
    constructed (no line bar, or no body bar) are returned with ok=False rather
    than silently dropped, so the count of skipped days stays visible."""
    out = {}
    for d, day in bars.groupby("date", sort=True):
        day = day.sort_values("hhmm")
        ln = day[day.hhmm == line_hhmm]
        bd = day[day.hhmm == body_hhmm]
        if len(ln) == 0 or len(bd) == 0:
            out[d] = dict(ok=False, reason="no line bar" if len(ln) == 0 else "no body bar")
            continue
        dopen = float(ln.iloc[0]["o"])
        bo, bc = float(bd.iloc[0]["o"]), float(bd.iloc[0]["c"])
        out[d] = dict(ok=True, dopen=dopen, bhi=max(bo, bc), blo=min(bo, bc),
                      side=1 if bc > dopen else -1,
                      bars=day[(day.hhmm > body_hhmm) & (day.hhmm < end_hr * 100)])
    return out


def run(bars, ticks, sl_pts, tp_pts, use_A=True, a_short_only=True, use_flip=True,
        line_hhmm=950, body_hhmm=1000, end_hr=23, days=None, be_at=None, trail=None):
    """-> DataFrame of trades. sl_pts/tp_pts are pure point distances from the
    actual fill; the spread is paid on top, by construction, not deducted."""
    days = days if days is not None else build_days(bars, line_hhmm, body_hhmm, end_hr)
    sl_i, tp_i = int(round(sl_pts * PTS)), int(round(tp_pts * PTS))
    be_i = int(round(be_at * PTS)) if be_at else None
    tr_i = int(round(trail * PTS)) if trail else None
    trades = []

    for d, st in days.items():
        if not st["ok"]:
            continue
        side, bhi, blo, dopen = st["side"], st["bhi"], st["blo"], st["dopen"]
        a_done = f_done = False
        in_pos = False
        exit_t = -1

        for _, bar in st["bars"].iterrows():
            if in_pos:
                continue
            t_close = int(pd.Timestamp(bar["ts_mel"]).value // 1_000_000) + 5 * 60 * 1000
            if t_close <= exit_t:
                continue                       # still inside the bar we exited on
            c = float(bar["c"])
            buyA  = use_A and not a_short_only and not a_done and side == 1  and c > bhi and c > dopen
            sellA = use_A and not a_done and side == -1 and c < blo and c < dopen
            flipB = use_flip and not f_done and side == -1 and c > bhi and c > dopen
            flipS = use_flip and not f_done and side == 1  and c < blo and c < dopen
            if not (buyA or sellA or flipB or flipS):
                continue

            long_ = buyA or flipB
            kind = "A_L" if buyA else "F_L" if flipB else "A_S" if sellA else "F_S"
            entry = int(round(float(bar["ask_c"] if long_ else bar["bid_c"]) * PTS))
            stop = entry - sl_i if long_ else entry + sl_i
            targ = entry + tp_i if long_ else entry - tp_i

            eod = int(pd.Timestamp(bar["ts_mel"]).normalize().value // 1_000_000) + end_hr * 3600_000
            i, j = ticks.slice_from(t_close, eod)
            px, why, xt = None, "EOD", eod
            if j > i:
                b, a, tt = ticks.bid[i:j], ticks.ask[i:j], ticks.t[i:j]
                if long_:
                    ex = b                      # a long is stopped and taken out on the BID
                    hit_s = ex <= stop
                    hit_t = ex >= targ
                else:
                    ex = a                      # a short on the ASK
                    hit_s = ex >= stop
                    hit_t = ex <= targ
                is_ = int(np.argmax(hit_s)) if hit_s.any() else 10**9
                it_ = int(np.argmax(hit_t)) if hit_t.any() else 10**9
                if min(is_, it_) < 10**9:
                    k = min(is_, it_)
                    px, why, xt = int(ex[k]), ("SL" if is_ <= it_ else "TP"), int(tt[k])
                else:
                    px, xt = int(ex[-1]), int(tt[-1])
            if px is None:
                continue                        # no quotes at all after the signal
            pnl = (px - entry) if long_ else (entry - px)
            trades.append(dict(date=d, kind=kind, side="long" if long_ else "short",
                               t_entry=t_close, t_exit=xt, entry=entry / PTS,
                               exit=px / PTS, pnl=pnl / PTS, why=why,
                               bars_side=side, hold_min=(xt - t_close) / 60000.0))
            in_pos, exit_t = True, xt
            if buyA or sellA:
                a_done = True
            else:
                f_done = True
            in_pos = False                      # one position at a time, but the day continues

    return pd.DataFrame(trades)


def stats(tr, label=""):
    """Equity-curve quality, not just profit. max_dd and the linearity of the
    curve are what "smooth" has to mean if it is to mean anything testable."""
    if tr is None or len(tr) == 0:
        return dict(label=label, n=0, net=0.0, pf=np.nan, win=np.nan, exp=np.nan,
                    max_dd=np.nan, mar=np.nan, r2=np.nan, tstat=np.nan, sharpe=np.nan)
    p = tr["pnl"].to_numpy(float)
    eq = np.cumsum(p)
    peak = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    dd = peak - eq
    mdd = float(dd.max()) if len(dd) else 0.0
    gp, gl = p[p > 0].sum(), -p[p < 0].sum()
    x = np.arange(len(eq), dtype=float)
    r2 = float(np.corrcoef(x, eq)[0, 1] ** 2) if len(eq) > 2 and eq.std() > 0 else np.nan
    sd = p.std(ddof=1) if len(p) > 1 else np.nan
    return dict(label=label, n=int(len(p)), net=float(p.sum()),
                pf=float(gp / gl) if gl > 0 else np.inf,
                win=float((p > 0).mean() * 100), exp=float(p.mean()),
                max_dd=mdd, mar=float(p.sum() / mdd) if mdd > 0 else np.inf,
                r2=r2, tstat=float(p.mean() / sd * np.sqrt(len(p))) if sd and sd > 0 else np.nan,
                sharpe=float(p.mean() / sd) if sd and sd > 0 else np.nan)
