"""
Opening Range Breakout — the rule book, tested in its own priority order.

WHY THIS ONE IS DIFFERENT FROM THE LAST THREE
  The level/pivot rule books all rested on "price reacts at this line". Eleven
  components of that family were tested this session and none survived an
  independent control. ORB rests on something else: that the first N minutes
  of a session define a range whose BREAK carries directional information.
  That is a claim about session structure, not about a line, so a fresh test
  is warranted rather than an assumption inherited from the previous result.

SESSION HANDLING, AND WHY IT IS DONE TWO DIFFERENT WAYS
  US30  the supplied series is SESSION data (~23 bars/day at 15m, about 5.8
        hours), so the first bar of each trading day IS the cash open. The
        opening range is taken from the data's own first bars. This is
        DST-proof by construction -- no UTC arithmetic to get wrong.
  GOLD  trades ~16 hours a day in this series, so there is no natural open.
        The session start must be named explicitly in UTC, and the rule book
        asks for both London and New York to be tried.

        DST CAVEAT, STATED NOT BURIED: a fixed UTC hour drifts one hour
        against local session time twice a year. On gold this means the
        "London open" is 08:00 local in winter and 09:00 local in summer.
        This is the same class of error as the AU200 archive's hardcoded
        UTC+10 (logged in its audit). It is not corrected here because the
        rule book specifies UTC-style fixed times; it is a known limitation
        of these gold numbers, not of the US30 ones.

COSTS
  This repo's standard: 0.20 pt slippage per side, applied on entry and exit.
"""
import argparse

import numpy as np
import pandas as pd

from backtest.io import load_csv

SLIP = 0.20


def _atr(df, n=14):
    h, l, c = df["high"].values, df["low"].values, df["close"].values
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1.0 / n, adjust=False).mean().values


def sessions(df, start_utc=None):
    """Yield (day, first_bar_index, last_bar_index) for each trading day."""
    d = pd.Series(df.index.date, index=df.index)
    hh = df.index.hour + df.index.minute / 60.0
    out = []
    for day, idx in d.groupby(d).groups.items():
        pos = np.searchsorted(df.index.values, np.array(idx, dtype="datetime64[ns]"))
        if start_utc is not None:
            keep = pos[hh.values[pos] >= start_utc]
            if len(keep) == 0:
                continue
            pos = keep
        if len(pos) >= 8:
            out.append((day, int(pos[0]), int(pos[-1])))
    return out


def run(df, or_bars=2, stop_mode="structure", target="2R", cutoff_bars=None,
        start_utc=None, atr_mult=1.0, one_per_dir=True, offset=0, fade=False):
    """One pass of the ORB rule book. Returns a trade table in R multiples.

    `offset`  THE MATCHED CONTROL. Build the range from `offset` bars later in
              the same session instead of from the open. Identical bar count,
              identical break logic, identical stop and target geometry -- the
              ONLY thing removed is that the range is the session's opening
              range. If offset>0 pays the same, the edge is "break of any
              recent range", not "break of the OPENING range".
    `fade`    take the opposite side of the same break, same geometry.
    """
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    A = _atr(df)
    rows = []
    for day, i00, i1 in sessions(df, start_utc):
        i0 = i00 + offset
        if i0 + or_bars >= i1:
            continue
        orh = h[i0:i0 + or_bars].max()
        orl = l[i0:i0 + or_bars].min()
        orw = orh - orl
        if orw <= 0:
            continue
        mid = (orh + orl) / 2.0
        a = A[i0 + or_bars]
        done = {1: False, -1: False}
        last = i1 if cutoff_bars is None else min(i1, i0 + cutoff_bars)
        for i in range(i0 + or_bars, last + 1):
            for brk, lvl in ((1, orh), (-1, orl)):
                if done[brk] or (c[i] <= lvl if brk > 0 else c[i] >= lvl):
                    continue
                if one_per_dir:
                    done[brk] = True
                d = -brk if fade else brk
                entry = c[i] + d * SLIP
                if stop_mode == "structure":
                    stop = orl if brk > 0 else orh
                elif stop_mode == "midpoint":
                    stop = mid
                else:                                   # atr
                    stop = lvl - brk * atr_mult * a
                risk = abs(entry - stop)
                if risk <= 0:
                    continue
                if fade:                                # mirror the geometry
                    stop = entry - d * risk
                if target.endswith("R"):
                    tgt = entry + d * float(target[:-1]) * risk
                else:                                   # measured move
                    tgt = entry + d * float(target) * orw
                res = np.nan
                for j in range(i + 1, i1 + 1):
                    hit_t = (h[j] >= tgt) if d > 0 else (l[j] <= tgt)
                    hit_s = (l[j] <= stop) if d > 0 else (h[j] >= stop)
                    if hit_t and hit_s:
                        # BUG-020 class: an ambiguous bar must resolve to the
                        # LOSS, not fall through to a session-close mark. The
                        # first version fell through, which paid BOTH the break
                        # and its own mirror image -- the tell that found this.
                        res = -(risk + 2 * SLIP) / risk; break
                    if hit_t:
                        res = (abs(tgt - entry) - 2 * SLIP) / risk; break
                    if hit_s:
                        res = -(risk + 2 * SLIP) / risk; break
                if not np.isfinite(res):                # rule book: time exit
                    res = (d * (c[i1] - entry) - 2 * SLIP) / risk
                rows.append({"day": day, "i": i, "dir": d, "R": res,
                             "orw_atr": orw / a if a > 0 else np.nan})
    return pd.DataFrame(rows)


def stats(t, label, quiet=False):
    if len(t) < 25:
        if not quiet:
            print(f"  {label:<38} n={len(t):>5}  (too few)")
        return None
    R = t["R"].values
    w, lo = R[R > 0], R[R <= 0]
    pf = w.sum() / abs(lo.sum()) if len(lo) and lo.sum() != 0 else np.inf
    eq = np.cumsum(R); dd = float((np.maximum.accumulate(eq) - eq).max())
    yrs = (pd.to_datetime(t["day"].max()) - pd.to_datetime(t["day"].min())).days / 365.25
    print(f"  {label:<38} n={len(R):>5} ({len(R) / max(yrs, .1):4.0f}/yr)  "
          f"WR={100 * (R > 0).mean():5.1f}%  avgR={R.mean():+6.3f}  "
          f"PF={pf:5.2f}  DD={dd:6.1f}R  tot={R.sum():+7.1f}R")
    return R.mean()


def halves(t, label):
    stats(t, label)
    if len(t) >= 60:
        mid = t["i"].median()
        stats(t[t["i"] <= mid], "    first half")
        stats(t[t["i"] > mid], "    OOS half")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", default="all")
    a = ap.parse_args()
    us = load_csv("data/us30_15m.csv.gz")
    gd = load_csv("data/xauusd_15m.csv.gz")
    per = {15: 1, 30: 2, 60: 4}                 # bars per range duration
    st = a.stage

    if st in ("all", "1"):
        print("\n" + "=" * 78)
        print("PRIORITY 1 — base ORB on US30, structure stop, 1.5R and 2R")
        print("=" * 78)
        for mins, nb in per.items():
            for tgt in ("1.5R", "2R"):
                stats(run(us, or_bars=nb, target=tgt),
                      f"US30  OR={mins}m  structure  {tgt}")

    if st in ("all", "2"):
        print("\n" + "=" * 78)
        print("PRIORITY 2 — same on Gold, London (08:00) and New York (13:30) UTC")
        print("=" * 78)
        for nm, s in (("LDN", 8.0), ("NY ", 13.5)):
            for mins, nb in per.items():
                for tgt in ("1.5R", "2R"):
                    stats(run(gd, or_bars=nb, target=tgt, start_utc=s),
                          f"GOLD {nm} OR={mins}m  structure  {tgt}")

    if st in ("all", "ctl"):
        print("\n" + "=" * 78)
        print("THE CONTROL — is it the OPENING range, or any range? (US30, 2R)")
        print("  offset=0 is the rule book. offset>0 builds the SAME size range")
        print("  from later in the same session and trades it the SAME way.")
        print("=" * 78)
        for nb, mins in ((1, 15), (4, 60)):
            for off in (0, 2, 4, 8, 12):
                stats(run(us, or_bars=nb, target="2R", offset=off),
                      f"US30 OR={mins}m  range starts +{off} bars")
        print("\n  FADE the break instead (same bars, mirrored geometry)")
        stats(run(us, or_bars=1, target="2R", fade=True), "  US30 OR=15m fade")
        stats(run(gd, or_bars=1, target="2R", start_utc=8.0, fade=True),
              "  GOLD LDN OR=15m fade")
        stats(run(gd, or_bars=1, target="2R", start_utc=13.5, fade=True),
              "  GOLD NY  OR=15m fade")
        print("\n  HALF-SAMPLE SPLIT of the best Priority-1 config")
        halves(run(us, or_bars=1, target="2R"), "US30 OR=15m 2R")

    if st in ("all", "3"):
        print("\n" + "=" * 78)
        print("PRIORITY 3 — time cutoff (bars after the open that may trigger)")
        print("=" * 78)
        for nb, mins in ((1, 15), (4, 60)):
            for cut in (4, 8, 12, 16, None):
                stats(run(us, or_bars=nb, target="2R", cutoff_bars=cut),
                      f"US30 OR={mins}m  cutoff={cut if cut else 'none':>4}")

    if st in ("all", "4"):
        print("\n" + "=" * 78)
        print("PRIORITY 4 — midpoint stop vs full-range stop vs ATR stop")
        print("=" * 78)
        for nb, mins in ((1, 15), (4, 60)):
            for sm in ("structure", "midpoint", "atr"):
                stats(run(us, or_bars=nb, target="2R", stop_mode=sm),
                      f"US30 OR={mins}m  stop={sm}")

    if st in ("all", "5"):
        print("\n" + "=" * 78)
        print("PRIORITY 5 — measured move (x range width) vs fixed R")
        print("=" * 78)
        for nb, mins in ((1, 15), (4, 60)):
            for tgt in ("1R", "2R", "3R", "1.0", "2.0", "3.0"):
                lab = f"{tgt} risk" if tgt.endswith("R") else f"{tgt}x range"
                stats(run(us, or_bars=nb, target=tgt), f"US30 OR={mins}m  {lab}")


if __name__ == "__main__":
    main()
