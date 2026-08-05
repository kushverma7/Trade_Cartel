"""
How gold actually behaves at major levels. MEASUREMENT ONLY -- no rules, no
optimisation, no contact with the G1* system.

NON-REPAINTING CONSTRUCTION, STATED BEFORE ANY NUMBER IS PRODUCED
  Every level a bar is tested against is fully determined by data that closed
  BEFORE that bar opened:
    PDH/PDL, PWH/PWL   previous COMPLETED day/week, mapped forward with a
                       groupby-shift. The current day's own extremes never
                       enter its own levels.
    Daily/Weekly Open  the open of the period in progress, which is known at
                       that period's first bar and constant thereafter.
    Round numbers      a fixed price grid. Which grid line a bar is tested
                       against is chosen from the PREVIOUS bar's close, so the
                       bar cannot select its own level.
    ATR (tolerance)    ATR(14) as of the PREVIOUS bar.
    Regime             21-day EMA (1008 bars) as of the PREVIOUS bar.
  Event classification reads the current bar's own high/low/close, which is
  correct -- that is the event being classified, not a predictor of it. Forward
  statistics start at i+1.

THE CONTROL, AND WHY IT IS BUILT THIS WAY
  A random level is not a uniformly random price. Real levels sit near price,
  so they are touched often; a uniformly random price is touched almost never,
  and comparing against it would flatter every real family enormously for a
  reason that has nothing to do with the level mattering.

  The control here is a PHASE-SHIFTED level: each real level is displaced by a
  random offset drawn from +/-(1.5 .. 4.0) ATR, redrawn per level instance.
  That preserves the level's distance-from-price distribution, its touch
  frequency and the whole geometry of the test, and destroys only the one thing
  under examination -- whether THAT price is special. If a family cannot beat
  its own phase-shifted twin, it carries no information.

DIRECTION CONVENTION, so the signs are checkable
  side = sign(prev_close - L). Price above the level => side +1, level is
  support.
    TOUCH   hypothesised direction is the bounce: d = side
    SWEEP   wick pierces, close returns => the fade: d = side
    BREAK   close beyond the level => the continuation: d = -side
    RETEST  price returns to a level broken earlier => continuation of that
            break: d = the original break direction
  Forward return, MFE and MAE are all measured in that direction and expressed
  in ATR at the event bar, so a 2019 event and a 2026 event are comparable.

WHAT "TOUCH NUMBER" MEANS HERE
  Counted per level VALUE, incremented on each event, and reset once price has
  closed more than 5 ATR away from the level. That is the operational reading
  of "in the current swing": a level price has walked away from and later
  returns to starts a fresh count.
"""
import argparse
import numpy as np, pandas as pd

from backtest.io import load_csv
from backtest import exit_lab

HZ = (4, 8, 16, 32, 64)
TOLS = (0.25, 0.50, 0.75)
MINN = 100                      # below this a cell is flagged low-confidence
RESET_ATR = 5.0
RETEST_WINDOW = 96              # bars a broken level stays "live" for a retest
SEED = 20260805


# ------------------------------------------------------------------ levels
def build_levels(df):
    """Every level family as a per-bar price. All strictly backward-looking."""
    idx = df.index
    out = {}
    day = pd.Series(idx.date, index=idx)
    wk = pd.Series(idx.to_period("W"), index=idx)

    for tag, key in (("D", day), ("W", wk)):
        g = df.groupby(key)
        hi, lo, op = g["high"].max(), g["low"].min(), g["open"].first()
        out[f"P{tag}H"] = key.map(hi.shift(1)).to_numpy(float)
        out[f"P{tag}L"] = key.map(lo.shift(1)).to_numpy(float)
        # the open of the period IN PROGRESS: known at its first bar, constant after
        out[f"{tag}O"] = key.map(op).to_numpy(float)

    c = df["close"].to_numpy(float)
    prev = np.r_[c[0], c[:-1]]                       # previous close, no lookahead
    for step, nm in ((50, "R50"), (100, "R100"), (500, "R500")):
        lo = np.floor(prev / step) * step
        hi = lo + step
        # the grid line nearer the previous close -- chosen without this bar's data
        out[nm] = np.where(prev - lo <= hi - prev, lo, hi)
    return out


STRUCT = ("PDH", "PDL", "PWH", "PWL", "DO", "WO")
ROUND = ("R50", "R100", "R500")


def confluence(levels, atr, tol):
    """How many STRUCTURAL levels sit within tolerance of each round number."""
    out = {}
    band = tol * atr
    for rn in ROUND:
        L = levels[rn]
        cnt = np.zeros(len(L), int)
        for s in STRUCT:
            cnt += (np.abs(levels[s] - L) <= band).astype(int)
        out[rn] = cnt
    return out


# ------------------------------------------------------------------ events
def classify(df, L, atr, tol):
    """Event type, direction, touch number and sweep depth for one level series.

    Returns arrays aligned to df. ev: 0 none, 1 touch, 2 sweep, 3 break, 4 retest.
    """
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    n = len(c)
    prev = np.r_[c[0], c[:-1]]
    band = tol * atr

    ev = np.zeros(n, np.int8)
    d = np.zeros(n, np.int8)
    tn = np.zeros(n, np.int16)
    depth = np.full(n, np.nan)

    side = np.sign(prev - L)
    side[side == 0] = 1

    # vectorised primitives
    pierce_up = h > L + band
    pierce_dn = l < L - band
    close_up = c > L + band
    close_dn = c < L - band
    inband = (l <= L + band) & (h >= L - band)

    # stateful parts: touch counter and the broken-level register
    counts = {}
    broke_at = {}          # level value -> (bar, direction)
    lastkey = None
    for i in range(n):
        Li = L[i]
        if not np.isfinite(Li) or not np.isfinite(atr[i]) or atr[i] <= 0:
            continue
        key = round(float(Li), 4)
        if key != lastkey:
            lastkey = key
        # reset the counter once price has walked away from this level
        if abs(c[i] - Li) > RESET_ATR * atr[i]:
            counts.pop(key, None)

        s = int(side[i])
        got = 0
        if s > 0:                                    # price above: level is support
            if close_dn[i]:
                got, dd = 3, -1                      # clean break down
            elif pierce_dn[i]:
                got, dd = 2, +1                      # swept low, closed back up
                depth[i] = (L[i] - band[i] - l[i]) / atr[i]
            elif inband[i]:
                got, dd = 1, +1
        else:                                        # price below: level is resistance
            if close_up[i]:
                got, dd = 3, +1
            elif pierce_up[i]:
                got, dd = 2, -1
                depth[i] = (h[i] - L[i] - band[i]) / atr[i]
            elif inband[i]:
                got, dd = 1, -1
        if not got:
            continue

        # a return to a level broken within the window is a RETEST, not a touch
        if got == 1 and key in broke_at:
            b, bd = broke_at[key]
            if i - b <= RETEST_WINDOW:
                got, dd = 4, bd
            else:
                broke_at.pop(key, None)
        if got == 3:
            broke_at[key] = (i, dd)

        counts[key] = counts.get(key, 0) + 1
        ev[i], d[i], tn[i] = got, dd, min(counts[key], 3)
    return ev, d, tn, depth


# ------------------------------------------------------------- forward path
def forward_stats(df, atr):
    """Pre-compute, for every bar and horizon, the signed return / MFE / MAE
    in ATR for BOTH directions. Done once and reused by every family."""
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    n = len(c)
    S = pd.Series
    out = {}
    for k in HZ:
        fwd_c = np.r_[c[k:], np.full(k, np.nan)]
        # extremes over bars i+1 .. i+k
        rmax = S(h).rolling(k).max().shift(-k).to_numpy()
        rmin = S(l).rolling(k).min().shift(-k).to_numpy()
        out[k] = dict(ret=(fwd_c - c) / atr,
                      up_mfe=(rmax - c) / atr, up_mae=(c - rmin) / atr,
                      dn_mfe=(c - rmin) / atr, dn_mae=(rmax - c) / atr)
    return out


def aggregate(mask, d, fw, label, extra=None):
    """The measurement block for one cell."""
    rows = []
    for k in HZ:
        f = fw[k]
        m = mask & np.isfinite(f["ret"])
        nn = int(m.sum())
        if nn == 0:
            continue
        dd = d[m]
        ret = f["ret"][m] * dd
        mfe = np.where(dd > 0, f["up_mfe"][m], f["dn_mfe"][m])
        mae = np.where(dd > 0, f["up_mae"][m], f["dn_mae"][m])
        rec = dict(cell=label, horizon=k, n=nn,
                   mean_ret=float(np.nanmean(ret)),
                   med_ret=float(np.nanmedian(ret)),
                   mfe=float(np.nanmean(mfe)), mae=float(np.nanmean(mae)),
                   mfe_mae=float(np.nanmean(mfe) / max(np.nanmean(mae), 1e-9)),
                   p_mfe_gt1=float(np.nanmean(mfe > 1)),
                   p_mae_gt1=float(np.nanmean(mae > 1)),
                   winrate=float(np.nanmean(ret > 0)),
                   low_conf=nn < MINN)
        if extra:
            rec.update(extra)
        rows.append(rec)
    return rows


# Displacements used for the control, as a FRACTION OF PRICE. At 30m gold an
# ATR is roughly 0.15-0.25% of price, so these sit about 1.5-4 ATR away -- close
# enough that the displaced level is touched at a comparable rate, far enough
# that it is a different price.
CONTROL_DELTAS = (+0.0035, -0.0035, +0.0060, -0.0060)


def shuffled_levels(levels, delta):
    """Parallel-displaced twin of each family: same identity through time,
    same break/retest lifecycle, wrong location.

    BUG-0xx, found 2026-08-05. The first version of this drew a fresh random
    offset for each contiguous run of a level value. That silently destroyed the
    RETEST population in the control -- a displaced level was broken, then took a
    new offset, so the broken-level register could never be hit again. The
    control produced 2 retests against the real families' 44,000, and the
    resulting "edge" for PWL/PDH retests (control MFE/MAE of 0.105 and 0.300, a
    physically implausible number) was an artifact of a one-observation control.

    Multiplying the whole series by (1 + delta) keeps each level's identity for
    exactly as long as the real one has it, so touches, breaks and retests are
    all generated by the same mechanism. Only the price is wrong, which is the
    single thing under test."""
    return {nm: L * (1.0 + delta) for nm, L in levels.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", default="30min")
    a = ap.parse_args()

    df = load_csv("data/xauusd_15m.csv.gz", rule=a.tf)
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    atr_raw = exit_lab._atr(h, l, c, 14)
    atr = np.r_[np.nan, atr_raw[:-1]]                 # PREVIOUS bar's ATR
    ema = pd.Series(c).ewm(span=1008, adjust=False).mean().shift(1).to_numpy()
    up_regime = c > ema
    year = np.array([t.year for t in df.index])

    print("=" * 104)
    print("DATA AND CONSTRUCTION")
    print("=" * 104)
    print(f"  XAUUSD {a.tf}, {len(df):,} bars, {df.index[0]} -> {df.index[-1]}")
    print(f"  price {c.min():.2f} .. {h.max():.2f} (low {l.min():.2f})")
    print(f"  ATR(14) used for tolerance is the PREVIOUS bar's: shift(1) applied")
    print(f"  regime = close vs 21-day EMA (1008 bars), also shifted")
    print(f"  above-EMA bars {100*np.nanmean(up_regime):.1f}%  "
          f"below {100*np.nanmean(~up_regime):.1f}%")
    print(f"  tolerances tested: {TOLS} x ATR   horizons: {HZ} bars")
    print(f"  NON-REPAINTING: PDH/PDL/PWH/PWL from completed periods only; round-")
    print(f"  number grid line selected from the PREVIOUS close; forward stats "
          f"start at i+1.")

    levels = build_levels(df)
    fw = forward_stats(df, atr)
    controls = [shuffled_levels(levels, dl) for dl in CONTROL_DELTAS]

    EVN = {1: "touch", 2: "sweep", 3: "break", 4: "retest"}
    rows, freq, depths = [], [], []

    for tol in TOLS:
        conf = confluence(levels, atr, tol)
        for nm in list(levels):
            srcs = [(levels, "real")] + [(cc, f"random{j}")
                                         for j, cc in enumerate(controls)]
            for src, tag in srcs:
                ev, d, tn, dep = classify(df, src[nm], atr, tol)
                for code, en in EVN.items():
                    m = ev == code
                    if m.sum() == 0:
                        continue
                    rows += aggregate(m, d, fw, f"{nm}|{en}",
                                      extra=dict(family=nm, event=en, tol=tol,
                                                 src=tag, cut="all"))
                    if tag == "real":
                        freq.append(dict(family=nm, event=en, tol=tol,
                                         n=int(m.sum()),
                                         pct_of_bars=100 * m.mean()))
                        if code == 2:
                            depths.append(dict(family=nm, tol=tol,
                                               mean_depth_atr=float(np.nanmean(dep[m])),
                                               med_depth_atr=float(np.nanmedian(dep[m]))))
                        # touch number
                        for t in (1, 2, 3):
                            mt = m & (tn == t)
                            if mt.sum():
                                rows += aggregate(mt, d, fw, f"{nm}|{en}|T{t}",
                                                  extra=dict(family=nm, event=en,
                                                             tol=tol, src="real",
                                                             cut=f"touch{t}"))
                        # regime split
                        for rn, rm in (("above_ema", up_regime), ("below_ema", ~up_regime)):
                            mr = m & rm
                            if mr.sum():
                                rows += aggregate(mr, d, fw, f"{nm}|{en}|{rn}",
                                                  extra=dict(family=nm, event=en,
                                                             tol=tol, src="real",
                                                             cut=rn))
            # confluence, round numbers only
            if nm in ROUND:
                ev, d, tn, dep = classify(df, levels[nm], atr, tol)
                for cs, cl in ((0, "single"), (1, "dual"), (2, "triple+")):
                    m = (ev > 0) & ((conf[nm] == cs) if cs < 2 else (conf[nm] >= 2))
                    for code, en in EVN.items():
                        mm = m & (ev == code)
                        if mm.sum():
                            rows += aggregate(mm, d, fw, f"{nm}|{en}|{cl}",
                                              extra=dict(family=nm, event=en,
                                                         tol=tol, src="real",
                                                         cut=cl))

    t = pd.DataFrame(rows)
    t.to_csv("research/level_profile.csv", index=False)
    pd.DataFrame(freq).to_csv("research/level_frequency.csv", index=False)
    pd.DataFrame(depths).to_csv("research/level_sweep_depth.csv", index=False)
    print(f"\n  wrote research/level_profile.csv  ({len(t):,} cells)")
    print(f"  wrote research/level_frequency.csv, research/level_sweep_depth.csv")

    # ---------------------------------------------------------------- drift
    base = []
    for k in HZ:
        r = fw[k]["ret"]
        base.append(dict(horizon=k, uncond_mean=float(np.nanmean(r)),
                         uncond_up_mfe=float(np.nanmean(fw[k]["up_mfe"])),
                         uncond_up_mae=float(np.nanmean(fw[k]["up_mae"])),
                         uncond_mfe_mae=float(np.nanmean(fw[k]["up_mfe"]) /
                                              np.nanmean(fw[k]["up_mae"]))))
    b = pd.DataFrame(base)
    b.to_csv("research/level_baseline.csv", index=False)
    print("\n" + "=" * 104)
    print("UNCONDITIONAL BASELINE -- what any level must beat before 'edge' is said")
    print("=" * 104)
    print(b.to_string(index=False, float_format=lambda v: f"{v:10.4f}"))


if __name__ == "__main__":
    main()
