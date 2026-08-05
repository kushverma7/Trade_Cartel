"""
Exit laboratory: TP1 / TP2 / runner, and six trailing algorithms.

User brief 2026-07-31: "find even better profit taking and trailing logic
and also you can make tp1 and tp2. also do not miss the found best results
already in our session."

Everything this project has learned says the EXIT is where the money is, so
this module makes the whole exit space searchable in one engine instead of
one knob at a time. It supersedes take_profit.py (single target) and the
exit half of trend.py, and it reproduces both as special cases so the
existing ledger rows stay comparable:

    trail_mode="chandelier", trail_atr=4.24, no TPs   -> trend.py's exit
    trail_mode="none", tp1 at 4% taking 100%          -> take_profit.py's

TRAILING MODES
    trail_atr_series  OPTIONAL per-bar override of trail_atr (a numpy array the
                  length of df). Added 2026-08-02 to test whether a REGIME
                  signal should widen or tighten the leash, rather than
                  changing the entry. The exponent-gap finding says the edge
                  accrues to hold time, so anything that legitimately extends a
                  hold should be applied HERE, not at the entry.

    "none"        static stop only
    "chandelier"  highest-high-since-entry minus N x ATR (the current build)
    "donchian"    lowest low of the last N bars (price structure, not ATR)
    "ema"         an EMA of close, trailing behind price
    "step"        chandelier whose multiple TIGHTENS as profit grows, so the
                  trade is given room early and protected late
    "giveback"    give back a fixed FRACTION of the best excursion, which
                  scales the leash to how far the trade has already run
    "structure"   Dave's 21-EMA confirmed structure trail (voice #7,
                  dave_market_structure.md:107-111, source transcript
                  raw_transcripts/line1200). Verbatim rule: "Trail stop ONLY
                  to lows that closed below the 21 EMA and were then
                  reclaimed. BE when the high that made your low is taken.
                  After swing 3-4 of the run, switch to aggressive candle-low
                  trailing."

                  This was the highest-value UNBUILT exit in the archive --
                  extracted correctly into a playbook in July and implemented
                  in zero engines until now (BELIEF_REGISTER: "the knowledge
                  layer's EXIT rules have never been tested, only its
                  entries", 8 mechanics, 8 unbuilt).

                  It is structurally unlike the other five: it tightens on
                  SWING COUNT, where "step" tightens on ATR progress and
                  "giveback" on a fraction of excursion. Ordinary noise lows
                  never move the stop -- only lows that closed through the EMA
                  and were then reclaimed by a higher high qualify.

PROFIT TAKING
    tp1/tp2 each have a mode ("atr", "pct", "points", "rr") and a fraction of
    the ORIGINAL position to close. Whatever is left runs on the trail.
    tp_be moves the stop to breakeven once TP1 fills, which is the cheapest
    risk reduction available and is measured separately here.

EXECUTION MODEL (unchanged from every other engine here so results compare)
  - entry at the signal bar's close, from the NEXT bar exits are live
  - a bar touching both a stop and a target is assumed to hit the STOP first
  - stop fills are gap-aware (BUG-018); target fills are at the target price
  - costs per contract per side, notional capped at equity * max_lev
"""
import numpy as np

LEVCAP=[0]; LEVTRY=[0]; LASTLOSS=[False]; STREAK=[0]
import pandas as pd

FIELDS = ("open", "high", "low", "close")


def _atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1.0 / n, adjust=False).mean().to_numpy()


def _target(entry, d, a, mode, val, stop_dist):
    if mode is None or val <= 0:
        return np.nan
    if mode == "atr":
        return entry + d * a * val
    if mode == "pct":
        return entry * (1.0 + d * val / 100.0)
    if mode == "points":
        return entry + d * val
    if mode == "rr":
        return entry + d * stop_dist * val
    raise ValueError(mode)


def _grid_target(grid, i, entry, d, rank):
    """The `rank`-th level in `grid[i]` strictly beyond `entry` in direction d.

    This is what "take profits at each pivot point level" means mechanically:
    the targets are not a multiple of anything, they are wherever the levels
    happen to sit relative to the fill. A trade entered right underneath R1
    gets a tiny first target; one entered just above S1 gets a large one. That
    variability is the rule, not a flaw in it.
    """
    row = grid[i]
    row = row[np.isfinite(row)]
    beyond = np.sort(row[row > entry]) if d > 0 else np.sort(row[row < entry])[::-1]
    return float(beyond[rank]) if len(beyond) > rank else np.nan


def run(df, sigL, sigS,
        stop_atr=4.0,
        trail_mode="chandelier", trail_atr=4.24, trail_n=20, trail_ema=0,
        trail_atr_series=None,
        step_from=3.0, step_to=1.5, step_span=10.0, giveback_frac=0.35,
        giveback_arm=2.0,
        struct_ema=21, struct_swings=3, struct_aggr=True,
        trail_only_after_tp1=False,
        tp1_mode=None, tp1_val=0.0, tp1_pct=0.5,
        tp2_mode=None, tp2_val=0.0, tp2_pct=0.3,
        tp_be=False, be_atr=0.0, tp_shorts_only=False, tp_grid=None,
        pyr_atr=0.0, pyr_max=0, pyr_risk=1.0,
        pyr_mode="current", pyr_budget=1.0, pyr_gate=None, pyr_decay=1.0,
        long_only=False, short_risk=1.0, cooldown=0, cooldown_loss=0,
        cooldown_win=0, risk_series=None, tighten_after=0.0, tighten_to=0.0,
        dd_trigger=0.0, dd_scale=1.0, dd_recover=0.0,
        trail_after_add=0.0, trail_short=0.0, trail_time_bars=0, trail_time_to=0.0,
        pyr_pause_lo=0.0, pyr_pause_hi=0.0, vol_rank=None,
        tighten_sched=None, streak_step=0.0, streak_cap=1.0, reentry=False,
        pyr_trail_gate=0.0, atr_n=14,
        risk_pct=1.0, equity0=10000.0, commission=0.07, slippage=0.05,
        max_lev=20, frac_qty=False):
    # PYRAMIDING MODES (pyr_mode). All default to "current" so every result
    # already in the ledger reproduces unchanged.
    #   current    each add risks another `risk_pct * pyr_risk` of equity,
    #              sized on the CURRENT ATR. Total NOMINAL risk grows linearly
    #              with the number of adds; realised open risk depends on where
    #              the ratcheting stop has got to, which is why it is measured
    #              rather than assumed.
    #   bounded    Turtle-style. Size the add so TOTAL open risk across the
    #              whole stack -- qty_total * |blended entry - current stop| --
    #              equals `pyr_budget` x the initial risk budget. pyr_budget=1
    #              holds open risk constant; 1.5 lets it grow modestly.
    #   fixed_frac each add is `pyr_risk` x the ORIGINAL position size (q0),
    #              independent of ATR and of the stop.
    #   vol_entry  like current, but sized on the ATR AT ENTRY rather than the
    #              current ATR -- isolates whether re-reading volatility at
    #              each add helps or hurts.
    #   decay      like current, but each successive add is scaled by
    #              pyr_decay ** add_index (0.5 = halve each time).
    # pyr_gate="breakeven" additionally requires the trailing stop to have
    # ratcheted past the blended entry before any add is allowed.
    # frac_qty: size in FRACTIONAL units instead of whole contracts.
    # Whole-contract sizing is a units artifact, not a strategy property: at
    # $10k equity and 1% risk, one gold contract near $2,000 is affordable but
    # one US30 contract near $35,000 is not, so np.floor() silently rejected
    # 788 of 789 US30 entries and reported "n=1" rather than an error. That is
    # the BUG-012 family. Defaults to False so every result already in the
    # ledger reproduces byte-for-byte; the cross-instrument tests pass True on
    # BOTH instruments so the comparison stays like-for-like.
    o, h, l, c = (df[k].to_numpy(float) for k in FIELDS)
    n = len(c)
    A = _atr(h, l, c, atr_n)
    lowN = pd.Series(l).rolling(trail_n).min().shift(1).to_numpy()
    highN = pd.Series(h).rolling(trail_n).max().shift(1).to_numpy()
    ema = (pd.Series(c).ewm(span=trail_ema, adjust=False).mean().to_numpy()
           if trail_ema else None)
    ema_s = pd.Series(c).ewm(span=struct_ema, adjust=False).mean().to_numpy()

    eq = equity0
    peak_eq = equity0
    derisked = [False]
    trades = []
    pos = None
    last_exit = -10 ** 9
    LASTLOSS[0] = False
    STREAK[0] = 0

    def close_part(pos, i, px, qout, why):
        nonlocal eq, peak_eq
        d = pos["dir"]
        pnl = d * (px - pos["entry"]) * qout - 2 * commission * qout
        eq += pnl
        peak_eq = max(peak_eq, eq)
        pos["banked"] += pnl
        pos["qty"] -= qout
        if pos["qty"] < (1e-8 if frac_qty else 1):
            trades.append({"pnl": pos["banked"], "dir": d, "bar": pos["bar"],
                           "bars_held": i - pos["bar"], "why": why,
                           "adds": pos["adds"], "orisk": pos["orisk"],
                           # PRICE-SPACE record, for reporting in POINTS rather
                           # than dollars: blended entry, final exit, the signed
                           # move in points, and the size that carried it.
                           "entry_px": pos["entry"], "exit_px": px,
                           "points": d * (px - pos["entry"]),
                           "qty": pos["q0"], "atr0": pos["a0"],
                           "exit_bar": i})
            LASTLOSS[0] = pos["banked"] < 0
            STREAK[0] = 0 if pos["banked"] < 0 else STREAK[0] + 1
            return True
        return False

    for i in range(max(atr_n, trail_n, 210) + 1, n):
        a = A[i]
        if pos is not None:
            d = pos["dir"]
            # NOTE: pos["best"] holds the best excursion through bar i-1. It is
            # updated at the END of this block, AFTER the stop and targets are
            # resolved. Updating it first would let bar i's own high push the
            # stop up and then trigger it on the same bar -- intrabar
            # lookahead, and it silently doubled drawdown when this engine was
            # first written.

            # ---------- add to a winner -------------------------------
            if pyr_atr > 0 and pos["adds"] < pyr_max:
                nxt = pos["last_add"] + d * a * pyr_atr
                gate_ok = True
                if vol_rank is not None and (pyr_pause_lo > 0 or pyr_pause_hi > 0):
                    # allow adds only while volatility sits inside the band
                    vr = vol_rank[i]
                    if np.isfinite(vr):
                        if pyr_pause_lo > 0 and vr < pyr_pause_lo:
                            gate_ok = False
                        if pyr_pause_hi > 0 and vr > pyr_pause_hi:
                            gate_ok = False
                if pyr_gate == "breakeven":
                    gate_ok = (pos["stop"] - pos["entry"]) * d > 0
                if pyr_trail_gate > 0:
                    # require the STOP itself to have ratcheted this many ATR
                    # from where it started before any add is allowed
                    moved = d * (pos["stop"] - pos["stop0"]) / max(pos["a0"], 1e-9)
                    gate_ok = gate_ok and moved >= pyr_trail_gate
                if gate_ok and ((h[i] >= nxt) if d > 0 else (l[i] <= nxt)):
                    ar = (risk_pct if d > 0 else risk_pct * short_risk) * pyr_risk
                    # GAP-AWARE ADD FILL (BUG-030). Filling at `nxt` assumes the
                    # add level is crossed DURING this bar. If the bar already
                    # opened beyond it -- which happens on a gap, and happens
                    # systematically whenever a gate has suppressed earlier adds
                    # and left `last_add` stranded behind the market -- then the
                    # level is stale and filling there buys at a price that was
                    # never available. Fill at the open in that case.
                    px = (max(nxt, o[i]) if d > 0 else min(nxt, o[i])) + d * slippage
                    if pyr_mode == "bounded":
                        # total open risk of the WHOLE stack, not the new unit
                        # A ratcheted stop can sit arbitrarily close to the add
                        # price, so budget/risk_per diverges. Floor the
                        # denominator at a quarter of the initial stop distance:
                        # below that the "risk" is an artifact of the stop
                        # having caught up, not room the trade actually has.
                        risk_per = max(abs(px - pos["stop"]), 0.25 * pos["a0"] * stop_atr)
                        budget = eq * (risk_pct if d > 0 else
                                       risk_pct * short_risk) / 100.0 * pyr_budget
                        aq = budget / risk_per - pos["qty"]
                    elif pyr_mode == "fixed_frac":
                        aq = pos["q0"] * pyr_risk
                    elif pyr_mode == "vol_entry":
                        aq = eq * ar / 100.0 / (pos["a0"] * stop_atr)
                    elif pyr_mode == "decay":
                        aq = (eq * ar / 100.0 / (a * stop_atr)) * (pyr_decay ** pos["adds"])
                    else:
                        aq = eq * ar / 100.0 / (a * stop_atr)
                    want = aq
                    aq = max(min(aq, eq * max_lev / c[i] - pos["qty"]), 0)
                    if want > aq + 1e-9:
                        LEVCAP[0] += 1
                    LEVTRY[0] += 1
                    aq = aq if frac_qty else np.floor(aq)
                    if aq >= (1e-8 if frac_qty else 1):
                        tot = pos["qty"] + aq
                        pos["entry"] = (pos["entry"] * pos["qty"] + px * aq) / tot
                        pos["qty"] = tot
                        pos["banked"] -= commission * aq
                        pos["adds"] += 1
                        pos["last_add"] = nxt
                        # instrumentation: open risk of the stack right after
                        # the add, as a multiple of the initial risk budget
                        orisk = tot * abs(pos["entry"] - pos["stop"])
                        pos["orisk"] = max(pos["orisk"], orisk / pos["r0"]
                                           if pos["r0"] > 0 else 0.0)

            # ---------- move the stop ---------------------------------
            active = (not trail_only_after_tp1) or pos["tp1_done"]
            if active and trail_mode != "none":
                cand = np.nan
                if trail_mode == "chandelier":
                    # anchored to the PREVIOUS bar's extreme, exactly as
                    # trend.py does, so the two engines agree
                    ta_ = (trail_atr if trail_atr_series is None
                           else float(trail_atr_series[i]))
                    # PATH-DEPENDENT TRAIL. Applied before the excursion-based
                    # tightening so an explicit tighten can still override.
                    #   trail_after_add : a different (usually wider) leash once
                    #                     the position has been added to at least
                    #                     once -- the stack is bigger, so the same
                    #                     ATR distance is a larger dollar risk.
                    #   trail_short     : separate width for shorts.
                    #   trail_time_*    : tighten purely on time in trade.
                    if trail_after_add > 0 and pos["adds"] >= 1:
                        ta_ = trail_after_add
                    if trail_short > 0 and d < 0:
                        ta_ = trail_short
                    if trail_time_bars > 0 and (i - pos["bar"]) >= trail_time_bars:
                        ta_ = min(ta_, trail_time_to) if trail_time_to > 0 else ta_
                    if tighten_after > 0 or tighten_sched:
                        # Once the trade has run far enough in its favour,
                        # tighten the leash. Measured off pos["best"], which
                        # holds the excursion through bar i-1 -- never the
                        # current bar (see the note above).
                        # tighten_sched is a list of (threshold_atr, trail_atr)
                        # applied in order, so the leash can step in several
                        # stages as the trade grows.
                        exc = d * (pos["best"] - pos["entry"]) / max(pos["a0"], 1e-9)
                        if tighten_sched:
                            for thr, tv in tighten_sched:
                                if exc >= thr:
                                    ta_ = tv
                        elif exc >= tighten_after:
                            ta_ = tighten_to
                    cand = (h[i - 1] - a * ta_ if d > 0
                            else l[i - 1] + a * ta_)
                elif trail_mode == "donchian":
                    cand = lowN[i] if d > 0 else highN[i]
                elif trail_mode == "ema" and ema is not None:
                    cand = ema[i]
                elif trail_mode == "step":
                    # profit measured in ATR decides how tight the leash is:
                    # trail_from at entry, easing to trail_to by step_span ATR
                    prog = abs(pos["best"] - pos["entry"]) / max(a, 1e-9)
                    frac = min(1.0, prog / max(step_span, 1e-9))
                    mult = step_from + (step_to - step_from) * frac
                    cand = pos["best"] - d * a * mult
                elif trail_mode == "structure":
                    # a low only QUALIFIES once its bar has closed through the
                    # EMA; it only ARMS once a later bar reclaims the high that
                    # preceded it. Both conditions use bar i-1 or earlier, so
                    # nothing here can see the bar it is about to be tested on.
                    e = ema_s[i - 1]
                    if d > 0:
                        if c[i - 1] < e:                  # closed below the EMA
                            pos["cand"] = (l[i - 1] if np.isnan(pos["cand"])
                                           else min(pos["cand"], l[i - 1]))
                            if np.isnan(pos["ref"]):
                                pos["ref"] = h[i - 1]
                        elif not np.isnan(pos["cand"]) and h[i - 1] > pos["ref"]:
                            cand = pos["cand"]            # reclaimed -> arm it
                            pos["cand"] = np.nan; pos["ref"] = np.nan
                            pos["swings"] += 1
                    else:
                        if c[i - 1] > e:
                            pos["cand"] = (h[i - 1] if np.isnan(pos["cand"])
                                           else max(pos["cand"], h[i - 1]))
                            if np.isnan(pos["ref"]):
                                pos["ref"] = l[i - 1]
                        elif not np.isnan(pos["cand"]) and l[i - 1] < pos["ref"]:
                            cand = pos["cand"]
                            pos["cand"] = np.nan; pos["ref"] = np.nan
                            pos["swings"] += 1
                    # "after swing 3-4, switch to aggressive candle-low trailing"
                    if struct_aggr and pos["swings"] >= struct_swings:
                        agg = (l[i - 1] if d > 0 else h[i - 1])
                        cand = agg if np.isnan(cand) else (
                            max(cand, agg) if d > 0 else min(cand, agg))
                elif trail_mode == "giveback":
                    # BUG FOUND 2026-07-31: without the arming threshold the
                    # excursion is zero at entry, so the stop snapped to the
                    # entry price on the second bar and the mode scored a 1%
                    # win rate over 2,300 trades. It must not arm until the
                    # trade has actually run somewhere.
                    run_ = abs(pos["best"] - pos["entry"])
                    if run_ >= a * giveback_arm:
                        cand = pos["best"] - d * run_ * giveback_frac
                if not np.isnan(cand):
                    pos["stop"] = (max(pos["stop"], cand) if d > 0
                                   else min(pos["stop"], cand))
            if be_atr > 0 and not pos["be"]:
                if (abs(pos["best"] - pos["entry"]) >= a * be_atr):
                    pos["stop"] = (max(pos["stop"], pos["entry"]) if d > 0
                                   else min(pos["stop"], pos["entry"]))
                    pos["be"] = True

            # ---------- resolve the bar -------------------------------
            hit_stop = (l[i] <= pos["stop"]) if d > 0 else (h[i] >= pos["stop"])
            if hit_stop:
                px = pos["stop"]
                px = min(px, o[i]) if d > 0 else max(px, o[i])
                px -= d * slippage
                if close_part(pos, i, px, pos["qty"], "stop"):
                    pos = None; last_exit = i
                    continue
            done = False
            for key, tgt, frac in (("tp1_done", pos["tp1"], tp1_pct),
                                   ("tp2_done", pos["tp2"], tp2_pct)):
                if done or pos[key] or np.isnan(tgt):
                    continue
                # the asymmetry rule: banking removes exactly the size that
                # captures a large move, so it can only be applied where there
                # is no large move to capture -- the counter-trend side
                if tp_shorts_only and d > 0:
                    continue
                reached = (h[i] >= tgt) if d > 0 else (l[i] <= tgt)
                if not reached:
                    continue
                pos[key] = True
                qout = pos["q0"] * frac
                qout = qout if frac_qty else float(np.floor(qout))
                lim = 1e-8 if frac_qty else 1
                qout = min(qout, pos["qty"]) if qout >= lim else pos["qty"]
                if close_part(pos, i, tgt - d * slippage, qout,
                              "tp1" if key == "tp1_done" else "tp2"):
                    pos = None; last_exit = i
                    done = True
                    break
                if key == "tp1_done" and tp_be:
                    pos["stop"] = (max(pos["stop"], pos["entry"]) if d > 0
                                   else min(pos["stop"], pos["entry"]))
            if done:
                continue
            # excursion updated only now that this bar is fully resolved
            pos["best"] = max(pos["best"], h[i]) if d > 0 else min(pos["best"], l[i])

        cd = max(cooldown, cooldown_loss if LASTLOSS[0] else cooldown_win)
        if reentry and not LASTLOSS[0]:
            # TREND-CONTINUATION RE-ENTRY. The cooldown exists to stop the
            # system re-buying the same chop it was just stopped out of. That
            # reasoning does not apply when the previous trade was a WINNER and
            # the direction filters still agree -- there the trail simply caught
            # a pullback in a trend that is still standing. Waive the cooldown
            # in exactly that case; a losing exit still serves the full wait.
            cd = 0
        if pos is not None or np.isnan(a) or a <= 0 or i - last_exit < cd:
            continue
        d = 1 if sigL[i] else (-1 if (sigS[i] and not long_only) else 0)
        if d == 0:
            continue
        sdist = a * stop_atr
        entry = c[i] + d * slippage
        eff = risk_pct if d > 0 else risk_pct * short_risk
        if dd_trigger > 0:
            # DRAWDOWN-RESPONSIVE SIZING (Randy McKay / Michael Platt / Turtle
            # unit reduction). While equity is more than `dd_trigger` below its
            # own running peak, cut risk to `dd_scale` of normal. Restored once
            # the drawdown recovers inside `dd_recover`. Uses only realised
            # equity to date -- no lookahead.
            ddnow = (peak_eq - eq) / peak_eq if peak_eq > 0 else 0.0
            if ddnow >= dd_trigger:
                derisked[0] = True
            elif ddnow <= dd_recover:
                derisked[0] = False
            if derisked[0]:
                eff *= dd_scale
        if streak_step > 0:
            # Progressive risk after consecutive wins, capped. STREAK[0] counts
            # consecutive winning closes and resets on any loss.
            eff *= min(1.0 + streak_step * STREAK[0], streak_cap)
        if risk_series is not None:
            # per-bar risk MULTIPLIER (1.0 = unchanged). Applied only at entry,
            # so a position's size is fixed by the regime at the moment it was
            # opened and never re-scaled mid-trade.
            rm = float(risk_series[i])
            eff *= rm if np.isfinite(rm) else 1.0
        qty = float(max(min(eq * eff / 100.0 / sdist, eq * max_lev / c[i]), 0))
        qty = qty if frac_qty else float(np.floor(qty))
        if qty < (1e-8 if frac_qty else 1):
            continue
        pos = {"dir": d, "entry": entry, "qty": qty, "q0": qty, "bar": i,
               "a0": a, "r0": qty * sdist, "orisk": 1.0,
               "cand": np.nan, "ref": np.nan, "swings": 0,
               "stop": entry - d * sdist, "stop0": entry - d * sdist,
               "best": entry, "banked": 0.0,
               "tp1": _grid_target(tp_grid, i, entry, d, 0)
                      if tp_grid is not None
                      else _target(entry, d, a, tp1_mode, tp1_val, sdist),
               "tp2": _grid_target(tp_grid, i, entry, d, 1)
                      if tp_grid is not None
                      else _target(entry, d, a, tp2_mode, tp2_val, sdist),
               "tp1_done": False, "tp2_done": False, "be": False,
               "adds": 0, "last_add": entry}
    return trades


def stats(trades, equity0=10000.0):
    if not trades:
        return {"n": 0, "wr": np.nan, "pf": np.nan, "net_pct": 0.0,
                "maxdd_pct": np.nan, "avg_bars": np.nan, "rdd": np.nan}
    p = np.array([t["pnl"] for t in trades])
    gw, gl = p[p > 0].sum(), -p[p < 0].sum()
    curve = equity0 + np.cumsum(p)
    peak = np.maximum.accumulate(curve)
    dd = float(((peak - curve) / peak).max() * 100)
    net = float(p.sum() / equity0 * 100)
    return {"n": len(p), "wr": float((p > 0).mean() * 100),
            "pf": float(gw / gl) if gl > 0 else float("inf"),
            "net_pct": net, "maxdd_pct": dd,
            "avg_bars": float(np.mean([t["bars_held"] for t in trades])),
            "rdd": net / dd if dd > 0 else np.nan}
