"""
LIQUIDITY SWEEP -> MSS -> RETEST : the v2.0 rule set, measured.

Implements trader_playbooks/LIQUIDITY_SWEEP_MASTER_RULESET.md as an
executable state machine and runs it against every instrument this repo
actually has data for.

STATED DEVIATIONS FROM THE SPEC (each one weakens the test; none is hidden)
--------------------------------------------------------------------------
1. TIMEFRAME. The spec's execution timeframe is 5m. The only 5m file in the
   repo is AU200. Gold and US30 are 15m. The 15m runs are therefore a
   TIMEFRAME-SUBSTITUTED test of the logic, not a test of the shipped spec.
2. INSTRUMENTS. There is no NQ data in this container and every market-data
   host is 403 at the egress proxy. US30 15m is used as the nearest
   available equity-index proxy. It is NOT NQ. Gold is XAUUSD spot, used as
   the GC proxy.
3. CORRELATION GATES NOT TESTED. No VIX, Mag7, DXY or Silver series are
   reachable, so spec Steps 5-6 (sections 5.5 / 3.2) are inert here: every
   confirmation multiplier is 1.00. The spec expects these to REMOVE trades,
   so the measured population is a superset of the specified one.
4. Volume on spot gold is broker tick-volume, not exchange volume. The
   spec's volume criterion (5.1.4) is therefore weaker than intended.

EXECUTION DISCIPLINE (the registered bugs this file is written against)
----------------------------------------------------------------------
BUG-035  entry is a RESTING LIMIT priced from bars that had already closed
         when it was placed. Never a fill conditioned on the filling bar's
         own close. Three fill assumptions are reported.
BUG-019  order of operations per bar: (1) resolve the bar against a stop
         that is already one bar stale, (2) THEN update excursion/trail.
BUG-020  the trail does not arm at zero excursion.
BUG-032  a bar that OPENS beyond the stop fills at the open, not the stop.
BUG-029  a bar that could hit both stop and target resolves as the STOP.
BUG-015  every "price was previously beyond X" reference is shifted.
BUG-018  stops do not fill at exactly the stop price; slippage is charged.
BUG-021  costs are in PRICE POINTS here, converted per instrument.
BUG-016  counters increment on FILLS.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict

import numpy as np
import pandas as pd

from backtest.inspect_csv import load
from backtest import levels as LV

# ---------------------------------------------------------------- instruments

@dataclass
class Instrument:
    name: str
    path: str
    kind: str                 # "metal" | "index"
    cost_pts: float           # ONE SIDE, in price points
    round_steps: tuple        # round-number grid for the cluster scan (1.3)
    atr_x_buf: float          # 1.2 buffer, ATR_X multiple
    atr_d_buf: float          # 1.2 buffer, ATR_D multiple
    risk_floor: float         # 1.2 validity gate, ATR_D multiple
    risk_cap: float
    a_windows: tuple          # (start,end) ET, entries allowed
    b_windows: tuple
    flat_at: str              # session-end flat, ET
    speed_bars: int           # 5.3.3 sweep -> MSS
    be_r: float               # 2.4.1


GOLD = Instrument(
    name="XAUUSD (GC proxy)", path="data/xauusd_15m.csv.gz", kind="metal",
    cost_pts=0.27, round_steps=(5.0, 10.0),
    atr_x_buf=0.70, atr_d_buf=0.060, risk_floor=0.10, risk_cap=0.35,
    a_windows=(("03:00", "06:00"), ("08:20", "11:00")), b_windows=(),
    flat_at="13:30", speed_bars=12, be_r=1.3,
)
US30 = Instrument(
    name="US30 (NQ proxy)", path="data/us30_15m_native.csv.gz", kind="index",
    cost_pts=2.0, round_steps=(50.0, 100.0),
    atr_x_buf=0.50, atr_d_buf=0.045, risk_floor=0.08, risk_cap=0.32,
    a_windows=(("09:35", "11:00"),),
    b_windows=(("11:00", "12:00"), ("13:30", "15:00")),
    flat_at="15:45", speed_bars=9, be_r=1.2,
)
AU200 = Instrument(
    name="AU200 5m (5m-TF check)", path="data/au200_5m.csv.gz", kind="index",
    cost_pts=1.0, round_steps=(50.0, 100.0),
    atr_x_buf=0.50, atr_d_buf=0.045, risk_floor=0.08, risk_cap=0.32,
    a_windows=(("09:35", "11:00"),),
    b_windows=(("11:00", "12:00"), ("13:30", "15:00")),
    flat_at="15:45", speed_bars=9, be_r=1.2,
)
INSTRUMENTS = {"gold": GOLD, "us30": US30, "au200": AU200}

# Level ranking, spec 5.7.1 / 5.8. Type R needs rank >= 0.5.
RANK = {"PWH": 1.0, "PWL": 1.0, "PMH": 1.0, "PML": 1.0,
        "PDH": 0.5, "PDL": 0.5, "DO": 0.5,
        "WO": 0.0, "MO": 0.0, "H4O": 0.0, "P4HH": 0.0, "P4HL": 0.0,
        "MONH": 0.0, "MONL": 0.0, "LONH": 0.0, "LONL": 0.0,
        "NYH": 0.0, "NYL": 0.0}
LEVEL_ORDER = list(RANK.keys())


@dataclass
class Cfg:
    """Every spec parameter that the ablation switches."""
    sweep_basis: str = "D"      # "D" = ATR_D (v1.0 reading), "X" = ATR_X
    sweep_min: float = 0.25     # 5.3.1
    sweep_max: float = 0.55
    reject_bars: int = 3        # 5.3.2
    disp_range: float = 1.5     # 5.1.1
    disp_body: float = 0.60     # 5.1.2
    disp_vol: float = 1.4       # 5.1.4
    require_fvg: bool = True    # 5.2
    fvg_min: float = 0.20
    retrace_lo: float = 0.50    # 5.4.1
    retrace_hi: float = 0.79
    invalidate: float = 0.85    # 5.4.2
    retest_bars: int = 15       # 5.4.4
    arm_bars: int = 24
    proximity: float = 0.80     # step 1
    cluster: bool = True        # 1.3
    min_r: float = 2.5          # 2.2
    max_tested: int = 2         # 5.9
    session_gate: bool = True   # 4.2
    time_stop: bool = False     # 2.4.2  HYPOTHESIS, default OFF
    time_stop_bars: int = 12
    use_be: bool = True         # 2.4.1
    trail_r: float = 2.0        # 2.4.3
    trail_atr: float = 4.24     # Type C trail width, ATR_X
    trail_arm: float = 1.0      # BUG-020 guard, ATR_X
    types: str = "RC"           # which populations to trade
    cost_mult: float = 2.0      # repo convention: headline is 2x slippage
    risk_cap: float = None      # override Instrument.risk_cap (ATR_D mult)
    risk_floor: float = None
    speed_mult: float = 1.0     # widen 5.3.3
    require_vol: bool = True    # 5.1.4


# ------------------------------------------------------------------ prepare

def _atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().values


def prepare(inst: Cfg | Instrument, cfg: Cfg):
    df = load(inst.path)[0].sort_index()
    df = df[~df.index.duplicated(keep="first")]
    idx = df.index
    if idx.tz is None:
        idx = idx.tz_localize("UTC")
        df.index = idx
    et = idx.tz_convert("America/New_York")          # BUG-037: real DST

    o, h, l, c = (df[k].values.astype(float) for k in ("open", "high", "low", "close"))
    v = df["volume"].values.astype(float)

    # --- ATR_X on the execution TF, shifted so bar i uses info through i-1
    atr_x = np.roll(_atr(h, l, c), 1); atr_x[0] = np.nan

    # --- daily ATR_D and ADR20 from CLOSED daily bars only
    d = df.resample("1D").agg({"open": "first", "high": "max",
                               "low": "min", "close": "last"}).dropna()
    d_atr = pd.Series(_atr(d["high"].values, d["low"].values,
                           d["close"].values), index=d.index).shift(1)
    d_adr = (d["high"] - d["low"]).rolling(20).mean().shift(1)
    day = idx.normalize().tz_localize(None) if idx.tz else idx.normalize()
    day = pd.DatetimeIndex(idx.tz_convert("UTC").normalize().tz_localize(None))
    d_atr.index = pd.DatetimeIndex(d_atr.index.tz_convert("UTC").tz_localize(None)) \
        if d_atr.index.tz else d_atr.index
    d_adr.index = d_atr.index
    atr_d = d_atr.reindex(day).values
    adr = d_adr.reindex(day).values

    # --- day's range so far (5.6), non-lookahead: through the previous bar
    dser = pd.Series(day)
    hi_sf = pd.Series(h).groupby(dser).cummax().shift(1).values
    lo_sf = pd.Series(l).groupby(dser).cummin().shift(1).values
    rng_state = (hi_sf - lo_sf) / adr

    # --- trend, from CLOSED daily and 4H bars (Type R vs C, spec 5.8)
    dtr = (d["close"] > d["close"].rolling(20).mean()).astype(int) * 2 - 1
    dtr = dtr.shift(1)
    dtr.index = d_atr.index
    d_trend = dtr.reindex(day).values

    f = df.resample("4h").agg({"close": "last"}).dropna()
    ftr = (f["close"] > f["close"].rolling(20).mean()).astype(int) * 2 - 1
    ftr = ftr.shift(1)
    h4 = pd.DatetimeIndex(idx.tz_convert("UTC").floor("4h").tz_localize(None))
    ftr.index = pd.DatetimeIndex(ftr.index.tz_convert("UTC").tz_localize(None)) \
        if ftr.index.tz else ftr.index
    h4_trend = ftr.reindex(h4).values

    # --- levels (non-lookahead by construction) + how many times tested
    lvl = LV.build(df)[LEVEL_ORDER]
    lm = lvl.values.astype(float)
    tested = np.zeros_like(lm)
    for j, nm in enumerate(LEVEL_ORDER):
        s = lvl[nm]
        epoch = (s != s.shift(1)).cumsum()
        touch = ((l <= s.values) & (h >= s.values)).astype(int)
        tested[:, j] = pd.Series(touch).groupby(epoch.values).cumsum().shift(1).values

    # --- volume baseline
    vsma = pd.Series(v).rolling(20).mean().shift(1).values

    # --- session masks
    mins = et.hour * 60 + et.minute

    def mask(wins):
        m = np.zeros(len(idx), bool)
        for a, b in wins:
            ah, am = map(int, a.split(":")); bh, bm = map(int, b.split(":"))
            m |= (mins >= ah * 60 + am) & (mins < bh * 60 + bm)
        return m

    entry_ok = mask(inst.a_windows + inst.b_windows)
    fh, fm = map(int, inst.flat_at.split(":"))
    flat = mins >= fh * 60 + fm
    newday = np.r_[True, day.values[1:] != day.values[:-1]]

    return dict(idx=idx, o=o, h=h, l=l, c=c, v=v, vsma=vsma,
                atr_x=atr_x, atr_d=atr_d, adr=adr, rng_state=rng_state,
                d_trend=d_trend, h4_trend=h4_trend, lm=lm, tested=tested,
                entry_ok=entry_ok, flat=flat, newday=newday, n=len(idx))


# ------------------------------------------------------------------- engine

def _cluster_push(sl, side, price_levels, atr_d, steps, cfg):
    """Spec 1.3 -- never park a stop inside a level cluster."""
    if not cfg.cluster or not np.isfinite(atr_d):
        return sl
    win = 0.06 * atr_d
    lo, hi = (sl - win, sl) if side > 0 else (sl, sl + win)
    hits = [x for x in price_levels if np.isfinite(x) and lo <= x <= hi]
    for st in steps:                                   # round numbers
        k = np.floor(lo / st) * st
        while k <= hi:
            if k >= lo:
                hits.append(k)
            k += st
    if not hits:
        return sl
    return (min(hits) - 0.03 * atr_d) if side > 0 else (max(hits) + 0.03 * atr_d)


def run(A, inst: Instrument, cfg: Cfg, fill_mode="limit", rng=None,
        random_entry=False):
    """The state machine. Returns a list of closed trades."""
    n = A["n"]
    o, h, l, c, v = A["o"], A["h"], A["l"], A["c"], A["v"]
    atr_x, atr_d, lm = A["atr_x"], A["atr_d"], A["lm"]
    cost = inst.cost_pts * cfg.cost_mult
    trades = []

    state = "IDLE"
    st = {}
    pos = None
    day_fills = 0

    for i in range(60, n):
        # ---------------------------------------------------- manage open pos
        if pos is not None:
            # BUG-019: the stop in force was set with data through bar i-1.
            sl, tp, side = pos["sl"], pos["tp"], pos["side"]
            exit_px = None
            reason = None
            gap = (o[i] <= sl) if side > 0 else (o[i] >= sl)
            if gap:                                        # BUG-032
                exit_px, reason = o[i], "gap_stop"
            elif (l[i] <= sl) if side > 0 else (h[i] >= sl):
                exit_px, reason = sl, "stop"               # BUG-029: stop wins
            elif tp is not None and ((h[i] >= tp) if side > 0 else (l[i] <= tp)):
                exit_px, reason = tp, "target"
            elif A["flat"][i] or A["newday"][i]:
                exit_px, reason = c[i], "session_flat"
            elif cfg.time_stop and pos["type"] == "R" and \
                    (i - pos["i"]) >= cfg.time_stop_bars and not pos["swing"]:
                r = ((c[i] - pos["px"]) * side) / pos["risk"]
                if r < 0.5:
                    exit_px, reason = c[i], "time_stop"

            if exit_px is not None:
                pnl = (exit_px - pos["px"]) * side - 2 * cost
                trades.append(dict(i=pos["i"], t=A["idx"][pos["i"]], exit_i=i,
                                   type=pos["type"], side=side, px=pos["px"],
                                   exit=exit_px, risk=pos["risk"],
                                   r=pnl / pos["risk"], pnl=pnl, reason=reason,
                                   rank=pos["rank"], bars=i - pos["i"]))
                pos = None
                state = "IDLE"
            else:
                # --- state update AFTER resolution (BUG-019)
                run_px = h[i] if side > 0 else l[i]
                pos["best"] = max(pos["best"], (run_px - pos["px"]) * side)
                rr = pos["best"] / pos["risk"]
                if pos["type"] == "C":
                    if pos["best"] >= cfg.trail_arm * pos["atr"]:   # BUG-020
                        t = run_px - side * cfg.trail_atr * atr_x[i]
                        pos["sl"] = max(pos["sl"], t) if side > 0 else min(pos["sl"], t)
                else:
                    swing = (l[i] > l[i - 1] and c[i] > c[i - 1]) if side > 0 \
                        else (h[i] < h[i - 1] and c[i] < c[i - 1])
                    if swing:
                        pos["swing"] = True
                    if cfg.use_be and rr >= inst.be_r and pos["swing"]:
                        b = l[i - 1] - inst.atr_x_buf * atr_x[i] if side > 0 \
                            else h[i - 1] + inst.atr_x_buf * atr_x[i]
                        pos["sl"] = max(pos["sl"], b) if side > 0 else min(pos["sl"], b)
                    if rr >= cfg.trail_r:
                        b = l[i - 1] - inst.atr_x_buf * atr_x[i] if side > 0 \
                            else h[i - 1] + inst.atr_x_buf * atr_x[i]
                        pos["sl"] = max(pos["sl"], b) if side > 0 else min(pos["sl"], b)
                continue

        if A["newday"][i]:
            day_fills = 0
        ad, ax = atr_d[i], atr_x[i]
        if not (np.isfinite(ad) and np.isfinite(ax)) or ad <= 0 or ax <= 0:
            continue

        # ------------------------------------------------------- PENDING_ENTRY
        if state == "PENDING_ENTRY":
            side, leg = st["side"], st["leg"]
            if i - st["mss_i"] > cfg.retest_bars:
                state = "IDLE"; continue
            ent = st["entry"]
            hit = (l[i] <= ent) if side > 0 else (h[i] >= ent)
            if hit:
                if fill_mode == "limit":
                    px = ent                       # conservative: no gap benefit
                elif fill_mode == "close":
                    px = c[i]
                else:                              # next open
                    if i + 1 >= n:
                        state = "IDLE"; continue
                    px = o[i + 1]
                risk = abs(px - st["sl"])
                if risk <= 0:
                    state = "IDLE"; continue
                pos = dict(i=i, px=px, sl=st["sl"], tp=st["tp"], side=side,
                           risk=risk, type=st["type"], best=0.0, swing=False,
                           atr=ax, rank=st["rank"])
                day_fills += 1                     # BUG-016: on FILL
                state = "IN_TRADE"
                continue
            inval = st["dhi"] - cfg.invalidate * leg if side > 0 \
                else st["dlo"] + cfg.invalidate * leg
            if (l[i] < inval) if side > 0 else (h[i] > inval):
                state = "IDLE"
            continue

        # -------------------------------------------------------------- SWEPT
        if state == "SWEPT":
            side = st["side"]
            if i - st["sweep_i"] > inst.speed_bars * cfg.speed_mult:
                state = "IDLE"; continue
            if i - st["sweep_i"] <= cfg.reject_bars:
                back = (c[i] > st["level"]) if side > 0 else (c[i] < st["level"])
                st["rejected"] = st.get("rejected", False) or back
            elif not st.get("rejected", False):
                state = "IDLE"; continue
            st["ext"] = min(st["ext"], l[i]) if side > 0 else max(st["ext"], h[i])

            # MSS: close beyond the running extreme since the sweep (BUG-008
            # idiom -- real-time BOS, no pivot lag; BUG-015 -- excludes bar i)
            ref = st["ref"]
            st["ref"] = max(ref, h[i]) if side > 0 else min(ref, l[i])
            if not st.get("rejected", False):
                continue
            brk = (c[i] > ref) if side > 0 else (c[i] < ref)
            if not brk:
                continue

            rng = h[i] - l[i]
            if rng < cfg.disp_range * ax:
                continue
            if abs(c[i] - o[i]) / max(rng, 1e-9) < cfg.disp_body:
                continue
            if cfg.require_vol and np.isfinite(A["vsma"][i]) and \
                    v[i] < cfg.disp_vol * A["vsma"][i]:
                continue

            if cfg.require_fvg:
                fvg = (l[i] - h[i - 2]) if side > 0 else (l[i - 2] - h[i])
                if fvg < cfg.fvg_min * ax:
                    continue
                edge = l[i] if side > 0 else h[i]
            else:
                edge = l[i] if side > 0 else h[i]

            dhi, dlo = h[i], st["ext"] if side > 0 else None
            if side > 0:
                dhi, dlo = h[i], st["ext"]
            else:
                dhi, dlo = st["ext"], l[i]
            leg = dhi - dlo
            if leg <= 0:
                continue

            # spec 5.4.1 retracement band, entry at the FVG proximal edge
            rt = (dhi - edge) / leg if side > 0 else (edge - dlo) / leg
            if rt > cfg.retrace_hi:
                continue
            if rt < cfg.retrace_lo:
                edge = dhi - cfg.retrace_lo * leg if side > 0 \
                    else dlo + cfg.retrace_lo * leg

            # ------------------------------------------------ stop (spec 1.2)
            ob = None
            for k in range(i - 1, max(i - 6, 0), -1):
                if (c[k] < o[k]) if side > 0 else (c[k] > o[k]):
                    ob = l[k] if side > 0 else h[k]
                    break
            anchor = min(st["ext"], ob) if (side > 0 and ob is not None) else \
                (max(st["ext"], ob) if (side < 0 and ob is not None) else st["ext"])
            buf = max(inst.atr_x_buf * ax, inst.atr_d_buf * ad)
            sl = anchor - buf if side > 0 else anchor + buf
            sl = _cluster_push(sl, side, lm[i], ad, inst.round_steps, cfg)

            risk = abs(edge - sl)
            rfl = inst.risk_floor if cfg.risk_floor is None else cfg.risk_floor
            rcp = inst.risk_cap if cfg.risk_cap is None else cfg.risk_cap
            if not (rfl * ad <= risk <= rcp * ad):
                state = "IDLE"; continue

            # ------------------------------------------ type + target (2.2/5.8)
            tt = "C" if (side == A["d_trend"][i] and side == A["h4_trend"][i]) else "R"
            if tt not in cfg.types:
                state = "IDLE"; continue
            if tt == "R" and st["rank"] < 0.5:
                state = "IDLE"; continue
            rs = A["rng_state"][i]
            if np.isfinite(rs):
                if tt == "C" and rs > 1.20:
                    state = "IDLE"; continue
                if tt == "R" and rs > 1.80:
                    state = "IDLE"; continue

            tp = None
            if tt == "R":
                # CORRECTED 2.2: nearest pool that CLEARS the gate, not nearest
                cand = [x for x in lm[i] if np.isfinite(x) and
                        ((x - edge) if side > 0 else (edge - x)) >= cfg.min_r * risk]
                if not cand:
                    state = "IDLE"; continue
                tp = min(cand) if side > 0 else max(cand)

            st.update(entry=edge, sl=sl, tp=tp, type=tt, mss_i=i,
                      leg=leg, dhi=dhi, dlo=dlo)
            state = "PENDING_ENTRY"
            continue

        # -------------------------------------------------------------- ARMED
        if state == "ARMED":
            if i - st["arm_i"] > cfg.arm_bars:
                state = "IDLE"
            else:
                side, lvl = st["side"], st["level"]
                base = ad if cfg.sweep_basis == "D" else ax
                d = (lvl - l[i]) if side > 0 else (h[i] - lvl)
                if d >= cfg.sweep_min * base:
                    if d > cfg.sweep_max * base:
                        state = "IDLE"                     # breakout, not sweep
                    else:
                        st.update(sweep_i=i, ext=(l[i] if side > 0 else h[i]),
                                  ref=(h[i] if side > 0 else l[i]),
                                  rejected=False)
                        state = "SWEPT"
                continue
            # fall through to IDLE re-arm on the same bar

        # --------------------------------------------------------------- IDLE
        if state == "IDLE":
            if day_fills >= 3:                             # spec 3.4
                continue
            if cfg.session_gate and not A["entry_ok"][i]:
                continue
            best = None
            for j, nm in enumerate(LEVEL_ORDER):
                x = lm[i, j]
                if not np.isfinite(x):
                    continue
                if A["tested"][i, j] > cfg.max_tested:
                    continue
                if abs(c[i] - x) > cfg.proximity * ad:
                    continue
                side = 1 if c[i] > x else -1               # sweep DOWN -> long
                r = RANK[nm]
                if best is None or r > best[2]:
                    best = (x, side, r)
            if best is not None:
                st = dict(level=best[0], side=best[1], rank=best[2], arm_i=i)
                state = "ARMED"

    return trades


# -------------------------------------------------------------------- stats

def stats(tr, label=""):
    if not tr:
        return dict(label=label, n=0)
    r = np.array([t["r"] for t in tr])
    p = np.array([t["pnl"] for t in tr])
    w, lo = p[p > 0], p[p <= 0]
    pf = w.sum() / abs(lo.sum()) if len(lo) and lo.sum() != 0 else float("inf")
    eq = np.cumsum(p)
    dd = float(np.max(np.maximum.accumulate(eq) - eq)) if len(eq) else 0.0
    top10 = float(np.sort(p)[-10:].sum()) if len(p) >= 10 else float(p.sum())
    return dict(label=label, n=len(tr), pf=round(float(pf), 3),
                wr=round(100 * len(w) / len(tr), 2),
                exp_r=round(float(r.mean()), 4), net=round(float(p.sum()), 1),
                maxdd=round(dd, 1),
                top10_share=round(100 * top10 / p.sum(), 1) if p.sum() else None,
                avg_bars=round(float(np.mean([t["bars"] for t in tr])), 1))


def split(tr, idx, frac=0.70):
    if not tr:
        return [], []
    cut = idx[int(len(idx) * frac)]
    return [t for t in tr if t["t"] < cut], [t for t in tr if t["t"] >= cut]


def null_control(A, inst, cfg, tr, seed=0):
    """
    CONTROL 1 (spec 7.2). Matched random entry through the IDENTICAL exit
    engine: same trade count, same side mix, same session windows, same
    risk distribution. If the sweep entry cannot beat this, the entry
    contributes nothing.  BUG-023: the null must not skip the filters.
    """
    if not tr:
        return []
    rs = np.random.default_rng(seed)
    n = A["n"]
    ok = np.flatnonzero(A["entry_ok"][60:n - 30] & np.isfinite(A["atr_d"][60:n - 30])) + 60
    if len(ok) == 0:
        return []
    out = []
    for t in tr:
        i = int(rs.choice(ok))
        side = t["side"]
        risk = t["risk"]
        px = A["c"][i]
        sl = px - side * risk
        tp = px + side * risk * cfg.min_r if t["type"] == "R" else None
        pos = dict(i=i, px=px, sl=sl, tp=tp, side=side, risk=risk,
                   type=t["type"], best=0.0, swing=False, atr=A["atr_x"][i],
                   rank=t["rank"])
        cost = inst.cost_pts * cfg.cost_mult
        for k in range(i + 1, min(i + 400, n)):
            sl_, tp_ = pos["sl"], pos["tp"]
            ex = rsn = None
            if (A["o"][k] <= sl_) if side > 0 else (A["o"][k] >= sl_):
                ex, rsn = A["o"][k], "gap_stop"
            elif (A["l"][k] <= sl_) if side > 0 else (A["h"][k] >= sl_):
                ex, rsn = sl_, "stop"
            elif tp_ is not None and ((A["h"][k] >= tp_) if side > 0 else (A["l"][k] <= tp_)):
                ex, rsn = tp_, "target"
            elif A["flat"][k] or A["newday"][k]:
                ex, rsn = A["c"][k], "session_flat"
            if ex is not None:
                pnl = (ex - px) * side - 2 * cost
                out.append(dict(i=i, t=A["idx"][i], exit_i=k, type=t["type"],
                                side=side, px=px, exit=ex, risk=risk,
                                r=pnl / risk, pnl=pnl, reason=rsn,
                                rank=t["rank"], bars=k - i))
                break
            run_px = A["h"][k] if side > 0 else A["l"][k]
            pos["best"] = max(pos["best"], (run_px - px) * side)
            if pos["type"] == "C" and pos["best"] >= cfg.trail_arm * pos["atr"]:
                tl = run_px - side * cfg.trail_atr * A["atr_x"][k]
                pos["sl"] = max(pos["sl"], tl) if side > 0 else min(pos["sl"], tl)
    return out


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inst", default="gold,us30")
    ap.add_argument("--mode", default="base")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    rows = []
    for key in a.inst.split(","):
        inst = INSTRUMENTS[key]
        cfg = Cfg()
        A = prepare(inst, cfg)
        print(f"\n{'='*78}\n{inst.name}   bars={A['n']}   "
              f"{A['idx'][0].date()} -> {A['idx'][-1].date()}\n{'='*78}")

        for basis in ("D", "X"):
            cfg = Cfg(sweep_basis=basis)
            tr = run(A, inst, cfg)
            s = stats(tr, f"{key} sweep_basis={basis}")
            print(f"  sweep basis {basis}: {s}")
            rows.append({**s, "inst": key, "basis": basis, "arm": "base"})
        if a.out:
            json.dump(rows, open(a.out, "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
