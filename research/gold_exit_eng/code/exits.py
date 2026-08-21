"""Exit resolution on real quotes. First passage, exact, no bar-path guessing.

Every exit style below is resolved against the same cached tick path, so the
only thing that ever changes between experiments is the exit rule -- the entry
universe and the fills are byte-identical throughout.

Convention, fixed: a long enters at the ASK and is marked out on the BID; a
short enters at the BID and is marked out on the ASK. The round-trip spread is
therefore paid at whatever it actually was, never assumed.
"""
import numpy as np, pandas as pd
PTS = 1000.0


def resolve(tr, sl, tp, time_stop_min=None, be_at=None, be_offset=0.0,
            partial_at=None, partial_frac=0.5, partial_tp=None,
            trail_after=None, trail_dist=None):
    """-> (pnl_points, exit_reason). All levels in gold points."""
    fav, rmax, rmin, tms = tr["fav"], tr["rmax"], tr["rmin"], tr["tms"]
    n = len(fav)
    sl_i, tp_i = int(round(sl * PTS)), int(round(tp * PTS))
    horizon = n
    if time_stop_min:
        lim = tms[0] + int(time_stop_min * 60_000)
        horizon = int(np.searchsorted(tms, lim, side="right"))
        if horizon <= 0:
            return 0.0, "TIME0"
    fv, rx, rn = fav[:horizon], rmax[:horizon], rmin[:horizon]
    m = len(fv)

    def first_ge(arr, v):                       # arr non-decreasing
        k = int(np.searchsorted(arr, v, side="left")); return k if k < m else 10**9

    def first_le(arr, v):                       # arr non-increasing
        k = int(np.searchsorted(-arr, -v, side="left")); return k if k < m else 10**9

    i_tp = first_ge(rx, tp_i)
    i_sl = first_le(rn, -sl_i)

    # break-even: once +be_at is reached the stop moves to entry+be_offset
    i_be = 10**9
    if be_at is not None:
        i_arm = first_ge(rx, int(round(be_at * PTS)))
        if i_arm < m:
            lvl = int(round(be_offset * PTS))
            after = fv[i_arm:]
            hit = after <= lvl
            if hit.any():
                i_be = i_arm + int(hit.argmax())

    # trailing: arms at +trail_after, then exits on a give-back of trail_dist
    i_tr = 10**9
    if trail_after is not None and trail_dist is not None:
        i_arm = first_ge(rx, int(round(trail_after * PTS)))
        if i_arm < m:
            seg = fv[i_arm:]
            peak = np.maximum.accumulate(seg)
            hit = (peak - seg) >= int(round(trail_dist * PTS))
            if hit.any():
                i_tr = i_arm + int(hit.argmax())

    # partial: bank partial_frac at +partial_at, remainder runs to partial_tp
    if partial_at is not None:
        i_p = first_ge(rx, int(round(partial_at * PTS)))
        if i_p < min(i_sl, 10**9) and i_p < m:
            banked = partial_frac * partial_at
            rest_tp = int(round((partial_tp if partial_tp else tp) * PTS))
            seg_rx = np.maximum.accumulate(fv[i_p:])
            seg_rn = np.minimum.accumulate(fv[i_p:])
            mm = len(seg_rx)
            j_tp = int(np.searchsorted(seg_rx, rest_tp, side="left")); j_tp = j_tp if j_tp < mm else 10**9
            j_sl = int(np.searchsorted(-seg_rn, sl_i, side="left")); j_sl = j_sl if j_sl < mm else 10**9
            j_be = 10**9
            if be_at is not None:
                lvl = int(round(be_offset * PTS)); hb = fv[i_p:] <= lvl
                if hb.any(): j_be = int(hb.argmax())
            j = min(j_tp, j_sl, j_be)
            if j >= 10**9:
                run = int(fv[-1]); why = "PART+EOD"
            else:
                run = int(fv[i_p + j]); why = "PART+" + ("TP" if j == j_tp else ("SL" if j == j_sl else "BE"))
            return (banked + (1 - partial_frac) * run / PTS), why

    k = min(i_tp, i_sl, i_be, i_tr)
    if k >= 10**9:
        return (int(fv[-1]) / PTS, "TIME" if time_stop_min and horizon < n else "EOD")
    why = "SL" if k == i_sl else ("TP" if k == i_tp else ("BE" if k == i_be else "TRAIL"))
    return int(fv[k]) / PTS, why


def stats(pnls):
    p = np.asarray(pnls, float)
    if len(p) == 0:
        return dict(n=0, pf=np.nan, exp=np.nan, net=0.0, mdd=np.nan, wr=np.nan)
    gp, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    return dict(n=len(p), pf=(gp / gl if gl > 0 else np.inf), exp=p.mean(), net=p.sum(),
                mdd=float((pk - eq).max()), wr=100 * (p > 0).mean())


def run(trades, **kw):
    rows = []
    for t in trades:
        v, why = resolve(t, **kw)
        rows.append(dict(date=t["date"], kind=t["kind"], split=t.get("split"),
                         hhmm=t["hhmm"], entry=t["entry"], spread=t["spread"],
                         pnl=v, why=why))
    return pd.DataFrame(rows)


def by_split(df):
    o = {}
    for s in ("DEV", "VAL", "HOLD"):
        o[s] = stats(df[df.split == s]["pnl"].tolist())
    o["ALL"] = stats(df["pnl"].tolist())
    o["minPF"] = min(o[s]["pf"] for s in ("DEV", "VAL", "HOLD"))
    o["minEXP"] = min(o[s]["exp"] for s in ("DEV", "VAL", "HOLD"))
    return o
