"""Fast, exact simulator over precomputed per-DAY arrays.

A first attempt cached the post-entry tick path per candidate signal. That is
wrong-headed: the break condition stays true on every bar after it first fires,
so a year produces 24,062 candidates even though the per-day latches mean at
most two ever become trades. Caching a path each was 8 GB and got the process
killed.

The fix is to cache per DAY, not per signal. A day's quote stream is shared by
every candidate inside it, so the arrays are built once and each trade just
slices from its own entry index. Signals are evaluated on numpy arrays rather
than DataFrame rows. Nothing here is an approximation -- exits are still found by
walking real ticks in arrival order; this only stops redoing identical work.
"""
import numpy as np, pandas as pd

PTS = 1000.0


def prepare(bars, days, ticks, end_hr=23):
    """One record per constructible day: bar arrays + INDEX RANGE into the global
    quote arrays.

    Storing each day's ticks as its own numpy copy duplicated the entire 52M-tick
    stream and got the process OOM-killed. The days partition the stream, so a
    pair of indices carries the same information at no memory cost."""
    prep = []
    for d, st in days.items():
        if not st["ok"]:
            continue
        b = st["bars"]
        if len(b) == 0:
            continue
        # Parquet returns ts_mel as datetime64[ms], NOT [ns]. Calling .astype("int64")
        # and dividing by 1e6 therefore divided MILLISECONDS by a million, making
        # every timestamp ~1.7e6 instead of ~1.755e12, so every day's tick slice
        # began at index 0 of the year. Convert through an explicit ms dtype.
        t_close = (pd.to_datetime(b["ts_mel"]).to_numpy().astype("datetime64[ms]")
                   .astype("int64")) + 5 * 60 * 1000
        eod = int(pd.Timestamp(d).normalize().value // 1_000_000) + end_hr * 3600_000
        i = int(np.searchsorted(ticks.t, int(t_close[0]) - 1, side="left"))
        j = int(np.searchsorted(ticks.t, eod, side="right"))
        if j <= i:
            continue
        prep.append(dict(
            date=d, side=st["side"], bhi=st["bhi"], blo=st["blo"], dopen=st["dopen"],
            t_close=t_close, c=b["c"].to_numpy(float),
            ask_c=np.rint(b["ask_c"].to_numpy(float) * PTS).astype(np.int64),
            bid_c=np.rint(b["bid_c"].to_numpy(float) * PTS).astype(np.int64),
            i0=i, j0=j, eod=eod))
    return prep


def _exit(day, TK, t_entry, entry_i, long_, sl_i, tp_i):
    i0, j0 = day["i0"], day["j0"]
    k0 = i0 + int(np.searchsorted(TK.t[i0:j0], t_entry, side="right"))
    if k0 >= j0:
        return None
    ex = TK.bid[k0:j0] if long_ else TK.ask[k0:j0]
    if long_:
        hit_s, hit_t = ex <= entry_i - sl_i, ex >= entry_i + tp_i
    else:
        hit_s, hit_t = ex >= entry_i + sl_i, ex <= entry_i - tp_i
    i_s = int(hit_s.argmax()) if hit_s.any() else 10**9
    i_t = int(hit_t.argmax()) if hit_t.any() else 10**9
    if min(i_s, i_t) >= 10**9:
        k, why = len(ex) - 1, "EOD"
    else:
        k = min(i_s, i_t)
        why = "SL" if i_s <= i_t else "TP"        # tie -> stop, the conservative read
    return int(ex[k]), why, int(TK.t[k0 + k])


def simulate(prep, TK, sl_pts, tp_pts, use_A=True, a_short_only=True, use_flip=True,
             allow=None):
    """allow: optional set of signal kinds to permit, e.g. {"F_S"}. Lets a single
    leg be isolated without pretending the boolean flags can express it."""
    sl_i, tp_i = int(round(sl_pts * PTS)), int(round(tp_pts * PTS))
    rows = []
    for day in prep:
        side, bhi, blo, dop = day["side"], day["bhi"], day["blo"], day["dopen"]
        c = day["c"]
        if side == 1:
            armL, armS = (c > bhi) & (c > dop), (c < blo) & (c < dop)   # A_L , F_S
            kL, kS = "A_L", "F_S"
        else:
            armL, armS = (c > bhi) & (c > dop), (c < blo) & (c < dop)   # F_L , A_S
            kL, kS = "F_L", "A_S"
        a_done = f_done = False
        exit_t = -1
        for i in range(len(c)):
            for arm, kind, long_ in ((armL, kL, True), (armS, kS, False)):
                if not arm[i]:
                    continue
                if allow is not None and kind not in allow:
                    continue
                if kind == "A_L" and (not use_A or a_short_only or a_done):
                    continue
                if kind == "A_S" and (not use_A or a_done):
                    continue
                if kind in ("F_L", "F_S") and (not use_flip or f_done):
                    continue
                te = int(day["t_close"][i])
                if te <= exit_t:
                    continue
                e = int(day["ask_c"][i] if long_ else day["bid_c"][i])
                r = _exit(day, TK, te, e, long_, sl_i, tp_i)
                if r is None:
                    continue
                px, why, xt = r
                rows.append(dict(date=day["date"], kind=kind,
                                 side="long" if long_ else "short",
                                 t_entry=te, t_exit=xt, entry=e / PTS, exit=px / PTS,
                                 pnl=((px - e) if long_ else (e - px)) / PTS,
                                 why=why, hold_min=(xt - te) / 60000.0))
                exit_t = xt
                if kind in ("A_L", "A_S"):
                    a_done = True
                else:
                    f_done = True
    return pd.DataFrame(rows)
