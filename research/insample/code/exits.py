"""ONE-YEAR IN-SAMPLE — exit optimisation, equity curves, monthly tables.

*** EVERY NUMBER PRODUCED BY THIS FILE IS IN-SAMPLE, 2025-08-21 to 2026-08-20. ***
Nothing here is a forecast and nothing here has been tested out of sample.

FILL CONVENTION (identical to resolve.py, applied to every exit family):
  long enters ASK and is marked out on BID; short enters BID, marked out on ASK.
  A TARGET is a resting limit at an exact price: it fills AT the target and
  favourable overshoot is NEVER credited.
  A STOP -- structural, break-even or trailing -- is market-triggered and fills
  at the real next executable quote, including slippage past the level.
  A TIME exit fills at the quote showing when the clock runs out.

All P&L is in R, where 1R = |entry - structural stop| for that cycle.
"""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
from qt_engine import Book, PTS

pd.set_option("display.width", 250)
OUT = "research/insample/results"
C = pd.read_parquet(f"{OUT}/cycles.parquet").reset_index(drop=True)
B = Book("research/microq3/data", "2025-26")

MAXSPAN = 6 * 3600            # widest window any exit family can need
NYSEC = 86400


def paths():
    """One tick walk per cycle, cached. Stores the favourable-excursion series in
    integer points together with its running extremes, so every static exit is a
    searchsorted and every path-dependent exit is one vectorised comparison."""
    cache = f"{OUT}/paths.npz"
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        return list(z["fav"]), list(z["ts"])
    fav_all, ts_all = [], []
    for k0, long_, t0 in zip(C.k0, C.long, C.t_entry):
        k1 = min(int(np.searchsorted(B.ny, t0 + MAXSPAN * 1000, "right")), len(B.ny))
        if k1 - int(k0) < 5:
            fav_all.append(np.zeros(0, np.int64)); ts_all.append(np.zeros(0, np.int64)); continue
        k0 = int(k0)
        e_i = int(B.ask[k0]) if long_ else int(B.bid[k0])
        ex = B.bid[k0:k1] if long_ else B.ask[k0:k1]
        f = (ex.astype(np.int64) - e_i) if long_ else (e_i - ex.astype(np.int64))
        fav_all.append(f); ts_all.append(B.ny[k0:k1].astype(np.int64))
    np.savez(cache, fav=np.array(fav_all, dtype=object), ts=np.array(ts_all, dtype=object))
    return fav_all, ts_all


FAV, TS = paths()
RISK = C.risk.to_numpy(float)
TGT = np.abs(C.target.to_numpy(float) - C.entry.to_numpy(float))
T0 = C.t_entry.to_numpy(np.int64)
COPEN = C.cycle_open_s.to_numpy(np.int64)


def horizon_idx(i, span_s):
    """Index one past the last tick inside span_s seconds of entry."""
    t = TS[i]
    return int(np.searchsorted(t, T0[i] + span_s * 1000, "right"))


def eod_idx(i):
    """Index one past the last tick before 17:00 New York, gold's daily settlement."""
    t = TS[i]
    sod = (T0[i] // 1000) % NYSEC
    to_close = (17 * 3600 - sod) % NYSEC
    if to_close == 0:
        to_close = NYSEC
    return int(np.searchsorted(t, T0[i] + to_close * 1000, "right"))


def walk(i, tp_R=None, tp_pts=None, sl_R=1.0, span_s=10800, eod=False,
         be_at=None, trail_R=None, part_frac=0.0, part_at=None):
    """Resolve one cycle under a named exit family. Returns (pnl_R, why, hold_min).

    tp_R / tp_pts  target as a multiple of R, or as an absolute point distance
                   (the structural target). None means no target.
    sl_R           stop distance as a multiple of R. 1.0 is the structural stop.
    span_s / eod   time bound; eod overrides span_s with 17:00 New York.
    be_at          move the stop to entry once this many R of favourable
                   excursion has printed.
    trail_R        trail the stop this many R behind the running favourable high.
    part_frac      bank this fraction of the position at part_at R and run the
                   remainder under the same management.
    """
    f = FAV[i]
    if len(f) == 0:
        return np.nan, "--", 0.0
    risk = RISK[i]
    r_ticks = risk * PTS
    m = eod_idx(i) if eod else horizon_idx(i, span_s)
    m = min(m, len(f))
    if m < 5:
        return np.nan, "--", 0.0
    f = f[:m]
    rmax = np.maximum.accumulate(f)
    rmin = np.minimum.accumulate(f)

    tp_t = None
    if tp_pts is not None:
        tp_t = int(round(tp_pts * PTS))
    elif tp_R is not None:
        tp_t = int(round(tp_R * r_ticks))
    sl_t = int(round(sl_R * r_ticks))

    def first_static():
        """Index and kind of the first static hit (target limit vs structural stop)."""
        i_tp = int(np.searchsorted(rmax, tp_t, "left")) if tp_t is not None else 10 ** 9
        i_sl = int(np.searchsorted(-rmin, sl_t, "left"))
        if i_tp < m and i_tp <= i_sl:
            return i_tp, "TP", tp_t / PTS / risk
        if i_sl < m:
            return i_sl, "SL", f[i_sl] / PTS / risk
        return m - 1, "TIME", f[-1] / PTS / risk

    # dynamic stop level in ticks, as a function of time
    if trail_R is not None:
        lvl = np.maximum(-sl_t, rmax - int(round(trail_R * r_ticks)))
        # the trail only arms once it would sit above the structural stop
        hit = np.flatnonzero(f <= lvl)
        i_dyn = int(hit[0]) if len(hit) else 10 ** 9
        dyn_kind = "TRAIL"
    elif be_at is not None:
        arm = int(np.searchsorted(rmax, int(round(be_at * r_ticks)), "left"))
        if arm < m:
            seg = np.flatnonzero(f[arm:] <= 0)
            i_dyn = int(seg[0]) + arm if len(seg) else 10 ** 9
        else:
            i_dyn = 10 ** 9
        dyn_kind = "BE"
    else:
        i_dyn = 10 ** 9
        dyn_kind = None

    j, why, pnl = first_static()
    if i_dyn < j:
        j, why, pnl = i_dyn, dyn_kind, f[i_dyn] / PTS / risk

    if part_frac > 0 and part_at is not None:
        i_p = int(np.searchsorted(rmax, int(round(part_at * r_ticks)), "left"))
        if i_p < m and i_p <= j:
            pnl = part_frac * part_at + (1 - part_frac) * pnl
            why = why + "+P"

    hold = (int(TS[i][j]) - int(T0[i])) / 60000.0
    return pnl, why, hold


def run(fam, mask=None, **kw):
    idx = np.arange(len(C)) if mask is None else np.flatnonzero(mask)
    rec = [walk(int(i), **kw) for i in idx]
    d = pd.DataFrame(rec, columns=["pnl_R", "why", "hold_min"], index=idx)
    d["date"] = C.date.to_numpy()[idx]
    d["family"] = fam
    return d.dropna(subset=["pnl_R"])


def stats(d):
    p = d.pnl_R.to_numpy(float)
    if len(p) == 0:
        return None
    gp, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    dd = pk - eq
    b = mx = 0
    for v in p:
        b = b + 1 if v <= 0 else 0; mx = max(mx, b)
    r2 = float(np.corrcoef(np.arange(len(eq)), eq)[0, 1] ** 2) if len(eq) > 2 else np.nan
    mo = d.groupby(pd.to_datetime(d.date).dt.to_period("M")).pnl_R.sum()
    return dict(n=len(p), pf=(gp / gl if gl > 0 else np.inf), exp=p.mean(), net=p.sum(),
                wr=100 * (p > 0).mean(), mdd=float(dd.max()),
                ulcer=float(np.sqrt((dd ** 2).mean())), r2=r2, streak=mx,
                mo_pos=int((mo > 0).sum()), mo=len(mo),
                hold=float(d.hold_min.median()))


HDR = (f"  {'exit family':<34}{'n':>5}{'PF':>8}{'exp R':>8}{'net R':>8}{'WR':>7}"
       f"{'DD':>7}{'Ulcer':>7}{'R2':>7}{'strk':>5}{'mo+':>7}{'hold':>7}")


def line(tag, s):
    if s is None:
        return f"  {tag:<34}{'no trades':>5}"
    pf = "  inf" if np.isinf(s["pf"]) else f"{s['pf']:8.2f}"
    return (f"  {tag:<34}{s['n']:>5}{pf}{s['exp']:>+8.3f}{s['net']:>+8.2f}{s['wr']:>6.1f}%"
            f"{s['mdd']:>7.2f}{s['ulcer']:>7.2f}{s['r2']:>7.3f}{s['streak']:>5}"
            f"{str(s['mo_pos']) + '/' + str(s['mo']):>7}{s['hold']:>7.0f}")


# ----------------------------------------------------------------------------
# universes: the winning models from models.py, rebuilt from their printed rules
# ----------------------------------------------------------------------------
F = {k: np.nan_to_num(C[k].to_numpy(float), nan=(9.9 if k == "q2_eff" else -1.0))
     for k in ("q2_eff", "dfr_over_q1", "q1_eff", "rr", "sweep_depth", "act_pct")}
F["sweep_depth"] = C.sweep_depth.to_numpy(float)
CYC, SWP = C.cycle.to_numpy(), C.sweep.to_numpy()


def mask(cyc="ALL", swp="any", q2e=9.0, dfr=9.0, q1e=0.0, rr=99.0, swd=9.0, act=(0.0, 1.0)):
    m = np.ones(len(C), bool)
    if cyc == "D123": m &= CYC != "D4"
    elif cyc != "ALL": m &= CYC == cyc
    if swp == "single": m &= SWP != "both"
    elif swp == "both": m &= SWP == "both"
    if act != (0.0, 1.0): m &= (F["act_pct"] >= act[0]) & (F["act_pct"] <= act[1])
    return (m & (F["q2_eff"] <= q2e) & (F["dfr_over_q1"] <= dfr) & (F["q1_eff"] >= q1e)
            & (F["rr"] <= rr) & (F["sweep_depth"] <= swd))


UNIV = {
    "BASE (all cycles)":  None,
    "M2  n=20 highest PF": mask("D123", "any", 0.40, 0.85, 0.0, 0.75, 9.0, (0.3, 0.8)),
    "M10 n=25 best all-day": mask("ALL", "any", 0.4375, 0.90, 0.20, 0.75, 9.0, (0.3, 0.8)),
    "M3  n=31 highest PF": mask("ALL", "any", 0.40, 0.75, 0.20, 2.00, 9.0, (0.3, 0.8)),
    "M6  n=22 smoothest": mask("D1", "any", 0.4375, 9.0, 0.0, 1.00, 9.0, (0.2, 0.8)),
    "SWD shallow sweeps only": mask(swd=0.05),
}
STRUCT = dict(tp_pts=None, sl_R=1.0, span_s=10800)


def struct_kw(i_unused=None):
    return STRUCT


def fam_table(name, m, log):
    """Every exit family on one universe. The structural exit is the baseline
    every other row is measured against."""
    tp_struct = TGT
    base = None
    log(f"\n{'=' * 128}\n{name}   [IN-SAMPLE 2025-08-21..2026-08-20]\n{'=' * 128}")
    log(HDR)

    def emit(tag, **kw):
        nonlocal base
        d = run(tag, m, **kw)
        s = stats(d)
        log(line(tag, s))
        return d, s

    # --- A. target family, structural stop, Q3+Q4 window -------------------
    log("  -- targets (structural stop, exit by end of the 6h cycle) " + "-" * 61)
    idx = np.arange(len(C)) if m is None else np.flatnonzero(m)
    rec = [walk(int(i), tp_pts=tp_struct[i], sl_R=1.0, span_s=10800) for i in idx]
    d = pd.DataFrame(rec, columns=["pnl_R", "why", "hold_min"], index=idx)
    d["date"] = C.date.to_numpy()[idx]; d = d.dropna(subset=["pnl_R"])
    base = d; s0 = stats(d)
    log(line("structural target  [BASELINE]", s0))
    for r in (0.5, 1.0, 1.5, 2.0, 3.0):
        emit(f"fixed {r:g}R target", tp_R=r, sl_R=1.0, span_s=10800)
    emit("no target, time only", tp_R=None, sl_R=1.0, span_s=10800)

    # --- B. time bound, structural target and stop -------------------------
    log("  -- time bounds (structural target and stop) " + "-" * 76)
    for tag, kw in (("end of Q3   (+90 min)", dict(span_s=5400)),
                    ("end of cycle (+3h)  [BASELINE]", dict(span_s=10800)),
                    ("+6 hours", dict(span_s=21600)),
                    ("17:00 New York (EOD)", dict(eod=True))):
        rec = [walk(int(i), tp_pts=tp_struct[i], sl_R=1.0, **kw) for i in idx]
        dd = pd.DataFrame(rec, columns=["pnl_R", "why", "hold_min"], index=idx)
        dd["date"] = C.date.to_numpy()[idx]
        log(line(tag, stats(dd.dropna(subset=["pnl_R"]))))

    # --- C. stop distance ---------------------------------------------------
    log("  -- stop distance (structural target, R still = structural risk) " + "-" * 55)
    for sl in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
        rec = [walk(int(i), tp_pts=tp_struct[i], sl_R=sl, span_s=10800) for i in idx]
        dd = pd.DataFrame(rec, columns=["pnl_R", "why", "hold_min"], index=idx)
        dd["date"] = C.date.to_numpy()[idx]
        tag = f"stop {sl:g}R" + ("   [BASELINE]" if sl == 1.0 else "")
        log(line(tag, stats(dd.dropna(subset=["pnl_R"]))))

    # --- D. management overlays --------------------------------------------
    log("  -- break-even, trailing, partials (structural target and stop) " + "-" * 56)
    for be in (0.25, 0.5, 0.75, 1.0):
        rec = [walk(int(i), tp_pts=tp_struct[i], sl_R=1.0, span_s=10800, be_at=be) for i in idx]
        dd = pd.DataFrame(rec, columns=["pnl_R", "why", "hold_min"], index=idx)
        dd["date"] = C.date.to_numpy()[idx]
        log(line(f"break-even at +{be:g}R", stats(dd.dropna(subset=["pnl_R"]))))
    for tr in (0.5, 0.75, 1.0, 1.5):
        rec = [walk(int(i), tp_pts=tp_struct[i], sl_R=1.0, span_s=10800, trail_R=tr) for i in idx]
        dd = pd.DataFrame(rec, columns=["pnl_R", "why", "hold_min"], index=idx)
        dd["date"] = C.date.to_numpy()[idx]
        log(line(f"trail {tr:g}R behind the high", stats(dd.dropna(subset=["pnl_R"]))))
    for fr in (0.33, 0.5, 0.75):
        for pa in (0.5, 1.0):
            rec = [walk(int(i), tp_pts=tp_struct[i], sl_R=1.0, span_s=10800,
                        part_frac=fr, part_at=pa) for i in idx]
            dd = pd.DataFrame(rec, columns=["pnl_R", "why", "hold_min"], index=idx)
            dd["date"] = C.date.to_numpy()[idx]
            log(line(f"bank {fr:.0%} at +{pa:g}R, run the rest",
                     stats(dd.dropna(subset=["pnl_R"]))))
    return base, s0


def surface(name, m, log):
    """The stop x target surface in R. A plateau of adjacent positive cells is
    evidence of structure; a single high cell surrounded by weak ones is not."""
    idx = np.arange(len(C)) if m is None else np.flatnonzero(m)
    SLS = [0.5, 0.75, 1.0, 1.25, 1.5]
    TPS = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    log(f"\n  STOP x TARGET SURFACE (PF, then n) — {name}   [IN-SAMPLE]")
    log("    " + "SL\\TP".ljust(8) + "".join(f"{t:>9g}R" for t in TPS))
    grid = {}
    for sl in SLS:
        cells = []
        for tp in TPS:
            rec = [walk(int(i), tp_R=tp, sl_R=sl, span_s=10800) for i in idx]
            dd = pd.DataFrame(rec, columns=["pnl_R", "why", "hold_min"], index=idx)
            dd["date"] = C.date.to_numpy()[idx]
            s = stats(dd.dropna(subset=["pnl_R"]))
            grid[(sl, tp)] = s
            cells.append("     inf" if s and np.isinf(s["pf"]) else
                         (f"{s['pf']:>9.2f}" if s else "        -"))
        log("    " + f"{sl:g}R".ljust(8) + "".join(cells))
    log("    " + "n".ljust(8) + "".join(f"{grid[(SLS[0], t)]['n']:>10d}" for t in TPS))
    return grid


def curves(name, d, log):
    """Equity and drawdown in R, plus the monthly table. Printed as text so the
    result survives in the log rather than only in a PNG."""
    d = d.sort_values("date")
    p = d.pnl_R.to_numpy(float)
    eq = np.cumsum(p)
    pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    dd = pk - eq
    log(f"\n  EQUITY / DRAWDOWN — {name}   [IN-SAMPLE]")
    w = 74
    lo, hi = min(0.0, eq.min()), max(eq.max(), 0.1)
    for k in range(0, len(eq), max(1, len(eq) // 28)):
        col = int(round((eq[k] - lo) / (hi - lo) * (w - 1)))
        bar = " " * col + "*"
        log(f"    {str(d.date.iloc[k]):<12}{eq[k]:>8.2f}R  dd {dd[k]:>5.2f}R  |{bar}")
    log(f"    {'FINAL':<12}{eq[-1]:>8.2f}R  maxDD {dd.max():.2f}R  "
        f"Ulcer {np.sqrt((dd ** 2).mean()):.2f}R")
    mo = d.groupby(pd.to_datetime(d.date).dt.to_period("M")).pnl_R.agg(["sum", "count"])
    log(f"\n  MONTHLY — {name}   [IN-SAMPLE]")
    log("    " + "".join(f"{str(k):>10}" for k in mo.index))
    log("    " + "".join(f"{v:>+10.2f}" for v in mo["sum"]))
    log("    " + "".join(f"{'n=' + str(int(v)):>10}" for v in mo["count"]))
    log(f"    months positive: {(mo['sum'] > 0).sum()} of {len(mo)}")


def activity_heat(log):
    """Does the activity gate that appears in every winning model do anything?
    Measured on the structural exit across the whole base universe."""
    idx = np.arange(len(C))
    rec = [walk(int(i), tp_pts=TGT[i], sl_R=1.0, span_s=10800) for i in idx]
    d = pd.DataFrame(rec, columns=["pnl_R", "why", "hold_min"], index=idx)
    d["act"] = F["act_pct"]; d["cyc"] = CYC
    d = d.dropna(subset=["pnl_R"])
    d = d[d.act >= 0]
    log(f"\n{'=' * 128}\nACTIVITY x CYCLE HEATMAP — structural exit, base universe   [IN-SAMPLE]\n{'=' * 128}")
    bins = [0, .2, .4, .6, .8, 1.01]
    d["band"] = pd.cut(d.act, bins, right=False,
                       labels=["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"])
    log("  PF by activity band x cycle   (n in brackets)")
    log("    " + "band".ljust(10) + "".join(f"{c:>16}" for c in ("D1", "D2", "D3", "D4", "ALL")))
    for b in d.band.cat.categories:
        row = []
        for c in ("D1", "D2", "D3", "D4", "ALL"):
            x = d[d.band == b] if c == "ALL" else d[(d.band == b) & (d.cyc == c)]
            p = x.pnl_R.to_numpy(float)
            if len(p) < 3:
                row.append(f"{'-':>16}"); continue
            gl = -p[p < 0].sum()
            pf = p[p > 0].sum() / gl if gl > 0 else np.inf
            row.append(f"{('inf' if np.isinf(pf) else f'{pf:.2f}') + f' ({len(p)})':>16}")
        log("    " + str(b).ljust(10) + "".join(row))


if __name__ == "__main__":
    buf = []
    def log(s=""):
        print(s, flush=True); buf.append(s)

    log("*" * 128)
    log("EXIT OPTIMISATION, EQUITY CURVES AND MONTHLY TABLES")
    log("*** EVERY NUMBER BELOW IS IN-SAMPLE: XAUUSD 2025-08-21 to 2026-08-20, one year, no holdout. ***")
    log("*" * 128)
    log(f"universe: {len(C)} QT cycles, tick-exact fills, 1R = |entry - structural stop|")

    keep = {}
    for name, m in UNIV.items():
        d, s = fam_table(name, m, log)
        keep[name] = d
    for name in ("BASE (all cycles)", "M10 n=25 best all-day", "M3  n=31 highest PF"):
        surface(name, UNIV[name], log)
    for name in ("BASE (all cycles)", "M2  n=20 highest PF", "M10 n=25 best all-day",
                 "M3  n=31 highest PF"):
        curves(name, keep[name], log)
    activity_heat(log)

    with open(f"{OUT}/exits.log", "w") as fh:
        fh.write("\n".join(buf) + "\n")
    log(f"\nwritten to {OUT}/exits.log")
