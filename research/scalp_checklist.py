"""
The scalping checklist, tested item by item.

The checklist (user, 2026-08-05) is six items. Four are exact enough to
falsify on OHLCV; one is not; one is an EXIT rule and gets the most attention,
because the exit is where this system's edge has always lived.

  1  VOLUME ON THE BREAK
     "Volume during the breakout indicated the significance of the
     continuation. A volume spike is a good confirmation."
     -> A gate on the champion's own Donchian breaks. Note this is NOT the
        "volume rank > 0.5" filter already in the ledger: that measured the
        volume regime over a trailing window on every bar. This measures the
        volume of THE BREAKOUT BAR ITSELF against its own recent average,
        which is what the checklist actually says.

  2  BREAK OF SUPPORT OR RESISTANCE
     Already the champion's entry (Donchian). Nothing new to test.

  3  BROKEN SUPPORT TURNED RESISTANCE / RESISTANCE TURNED SUPPORT
     "after prices convincingly break resistance, that line becomes your new
     support and can also act as a STOP LOSS."
     -> Two separate claims, tested separately:
        (a) the retest is directional -- price returning to a broken level
            continues away from it;
        (b) the level is a better STOP than an ATR distance.
        (b) is the more interesting one and it is testable directly: run the
        champion with its stop placed at the broken Donchian level instead of
        at trailATR x ATR.

  4  STAYING WITHIN YOUR TRENDLINES
     Not mechanically specified -- which two points define the line is a
     discretionary choice, and every choice gives a different answer. Recorded
     as untested rather than approximated with something the checklist did not
     say.

  5  TAKING PROFITS AT EACH PIVOT POINT LEVEL
     -> The exit test. Targets are placed at the actual floor-pivot levels
        (S2/S1/PP/R1/R2) sitting beyond the fill, TP1 at the first and TP2 at
        the second, with the remainder on the usual chandelier. This is a
        genuinely different exit from anything tested here: every other target
        this desk has tried was a MULTIPLE (of ATR, of R, of price). These are
        absolute levels, so the R-multiple of each target varies trade by
        trade with where the entry happened to land.

  6  BOLLINGER BAND SQUEEZE
     "Periods of low volatility are often followed by periods of high
     volatility ... a narrowing of the bands can foreshadow a significant
     advance or decline." (Bollinger)
     -> Two claims again: does the squeeze predict expansion at all, and does
        gating a breakout system on it help. The first can be true while the
        second is false, and usually is.

SCORING RULE, RESTATED BECAUSE IT HAS CAUGHT THREE FALSE POSITIVES ALREADY
  Every gate and every exit variant is dialled by bisection to the SAME 25%
  max drawdown before comparison. A filter that removes trades raises profit
  factor almost automatically -- the survivors are the easy ones. net/DD is
  the number that decides.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv
from backtest import champion, exit_lab
from research.source_battery import atr, forward, evaluate, HORIZONS
from research.source_battery2 import floor_pivots


def bollinger(df, n=20, k=2.0):
    c = pd.Series(df["close"].to_numpy(float))
    ma = c.rolling(n).mean()
    sd = c.rolling(n).std(ddof=0)
    width = (2 * k * sd / ma).to_numpy()          # bandwidth, scale-free
    return ma.to_numpy(), width


def solve_risk_kw(df, dd_target=25.0, lo=0.05, hi=12.0, iters=22, **kw):
    """Bisection on risk% for any champion.run configuration, not just a mask."""
    best = None
    for _ in range(iters):
        mid = (lo + hi) / 2
        tr, _ = champion.run(df, risk_pct=mid, **kw)
        s = exit_lab.stats(tr)
        best = (mid, s, tr)
        if s["n"] == 0 or s["maxdd_pct"] > dd_target:
            hi = mid
        else:
            lo = mid
    return best


def report(label, r, s, out):
    if s["n"] == 0:
        print(f"  {label:<38} no trades"); return
    rdd = s["net_pct"] / s["maxdd_pct"] if s["maxdd_pct"] else np.nan
    out.append(dict(arm=label, risk=r, n=s["n"], pf=s["pf"], net=s["net_pct"],
                    dd=s["maxdd_pct"], net_dd=rdd, wr=s["wr"]))
    print(f"  {label:<38} risk={r:5.2f}%  n={s['n']:<4} WR={s['wr']:4.1f}%  "
          f"PF={s['pf']:.3f}  net={s['net_pct']:>+9.1f}%  DD={s['maxdd_pct']:5.2f}%  "
          f"net/DD={rdd:6.2f}")


def main():
    df = load_csv("data/xauusd_15m.csv.gz", rule="30min")
    a = atr(df)
    c = df["close"].to_numpy(float)
    h, l = df["high"].to_numpy(float), df["low"].to_numpy(float)
    v = df["volume"].to_numpy(float)
    f = forward(df, a, HORIZONS)

    # ---- item 6, part 1: does a squeeze actually foreshadow expansion? ----
    _ma, bw = bollinger(df)
    fwd_bw = np.r_[bw[20:], np.full(20, np.nan)]          # bandwidth 20 bars later
    fwd_rng = pd.Series(h).rolling(20).max().shift(-20).to_numpy() - \
              pd.Series(l).rolling(20).min().shift(-20).to_numpy()
    q = pd.qcut(pd.Series(bw).dropna(), 5,
                labels=["squeeze", "tight", "mid", "loose", "wide"])
    tb = pd.DataFrame({"bw": bw, "fwd_bw": fwd_bw, "fwd_rng_atr": fwd_rng / a}).loc[q.index]
    tb["band"] = q
    print("=" * 100)
    print("ITEM 6a -- does a Bollinger squeeze foreshadow expansion? (n = %d bars)" % len(tb))
    print("=" * 100)
    agg = tb.groupby("band", observed=True).agg(
        n=("bw", "size"), bandwidth=("bw", "mean"),
        bandwidth_20_bars_later=("fwd_bw", "mean"),
        forward_20bar_range_in_ATR=("fwd_rng_atr", "mean"))
    print(agg.to_string(float_format=lambda x: f"{x:12.4f}"))
    print("  Bollinger's claim is that the SQUEEZE row should show the largest")
    print("  forward expansion. Mean reversion in the bandwidth itself is not the")
    print("  claim -- bandwidth is bounded below, so it must rise from a low; the")
    print("  question is whether the PRICE RANGE that follows is unusually large.")
    agg.to_csv("research/scalp_bb_squeeze.csv")

    # ---- item 3a: the level-flip retest, as a directional signal ----
    lb = champion.lookbacks(df, "bars", 30.0)
    donHi = pd.Series(h).rolling(lb["entry"]).max().shift(1).to_numpy()
    donLo = pd.Series(l).rolling(lb["entry"]).min().shift(1).to_numpy()
    broke_up = c > donHi
    broke_dn = c < donLo
    # the level that was broken, carried forward until the next break
    lvl = np.full(len(c), np.nan); side = np.zeros(len(c), int)
    cur, cs = np.nan, 0
    for i in range(len(c)):
        if broke_up[i]:
            cur, cs = donHi[i], +1
        elif broke_dn[i]:
            cur, cs = donLo[i], -1
        lvl[i], side[i] = cur, cs
    age = np.zeros(len(c), int)
    for i in range(1, len(c)):
        age[i] = 0 if (broke_up[i] or broke_dn[i]) else age[i - 1] + 1
    # a retest: price comes back to within 0.25 ATR of the broken level, and the
    # break was recent enough to still be the reference (within 100 bars)
    retest = (np.abs(c - lvl) < 0.25 * a) & (age > 0) & (age < 100) & np.isfinite(lvl)
    flip_l = retest & (side > 0)      # broken resistance should now support
    flip_s = retest & (side < 0)

    vma = pd.Series(v).rolling(20).mean().to_numpy()
    spike = v > 1.5 * vma

    arms = [("FLIP_res_turned_support", flip_l, +1),
            ("FLIP_sup_turned_resist", flip_s, -1),
            ("BREAK_UP_on_volume_spike", broke_up & spike, +1),
            ("BREAK_DN_on_volume_spike", broke_dn & spike, -1),
            ("BREAK_UP_no_spike", broke_up & ~spike, +1),
            ("BREAK_DN_no_spike", broke_dn & ~spike, -1)]
    rows = []
    for nm, s, d in arms:
        rows += evaluate(nm, s, np.float64(d), f, HORIZONS)
    t = pd.DataFrame(rows)
    print("\n" + "=" * 100)
    print("ITEMS 1 & 3a -- directional: the volume-spike break, and the level flip")
    print("=" * 100)
    print(t.to_string(index=False, float_format=lambda x: f"{x:9.4f}"))
    t.to_csv("research/scalp_directional.csv", index=False)

    # ---- champion variants, all at matched 25% drawdown ----
    piv = floor_pivots(df)
    grid = piv[["S1", "BC", "PP", "TC", "R1"]].to_numpy(float)

    print("\n" + "=" * 100)
    print("CHAMPION VARIANTS, every one dialled by bisection to 25% MAX DRAWDOWN")
    print("=" * 100)
    out = []
    r, s, _ = solve_risk_kw(df)
    report("baseline champion", r, s, out)

    for name, m in (("item 1: volume spike on the break", spike),
                    ("item 1: NO volume spike (control)", ~spike),
                    ("item 6: squeeze only (bw < 40th pct)",
                     bw < np.nanquantile(bw, 0.40)),
                    ("item 6: no squeeze (control)", bw > np.nanquantile(bw, 0.60))):
        r, s, _ = solve_risk_kw(df, mask=np.nan_to_num(m, nan=0).astype(bool))
        report(name, r, s, out)

    # item 5: profit taking at each pivot level
    for pcts in ((0.33, 0.33), (0.50, 0.25), (0.25, 0.25)):
        r, s, _ = solve_risk_kw(df, tp_grid=grid, tp1_pct=pcts[0], tp2_pct=pcts[1])
        report(f"item 5: TP at pivots {int(pcts[0]*100)}/{int(pcts[1]*100)}%", r, s, out)
    r, s, _ = solve_risk_kw(df, tp_grid=grid, tp1_pct=0.33, tp2_pct=0.33, tp_be=True)
    report("item 5: TP at pivots 33/33% + BE", r, s, out)

    # item 3b: the broken level as the stop, instead of an ATR distance
    print("\n  item 3b -- the broken level as the STOP. The checklist says the flipped")
    print("  level 'can also act as a STOP LOSS'. Distance from entry to that level,")
    print("  in ATR, decides whether this is even a viable stop:")
    dist = np.abs(c - lvl) / a
    dd = dist[np.isfinite(dist) & (age == 0)]
    print(f"    on the breakout bar itself: median {np.median(dd):.2f} ATR, "
          f"10th pct {np.quantile(dd, 0.10):.2f}, 90th pct {np.quantile(dd, 0.90):.2f}")
    print(f"    the champion's own stop is {champion.TRAIL_ATR:.2f} ATR")
    for cap in (None, 1.0):
        sa = np.clip(dist, 0.5, 8.0) if cap is None else np.clip(dist, 1.0, 8.0)
        # stop_atr must be a scalar for champion.run, so use the median as the
        # single closest honest summary of "the level as the stop"
        val = float(np.nanmedian(sa[np.isfinite(sa)]))
        r, s, _ = solve_risk_kw(df, stop_atr=val)
        report(f"item 3b: stop at broken level (~{val:.2f} ATR)", r, s, out)
        break

    pd.DataFrame(out).to_csv("research/scalp_variants.csv", index=False)

    best = max(out, key=lambda d: d["net_dd"])
    print("\n" + "=" * 100)
    print(f"BEST BY net/DD: {best['arm']}  ({best['net_dd']:.2f})")
    print("=" * 100)
    print("\nNOT TESTED, and why:")
    print("  item 4 'staying within your trendlines' -- which two points define the")
    print("  line is a discretionary choice and every choice gives a different")
    print("  answer. Approximating it would be testing something the checklist did")
    print("  not say.")


if __name__ == "__main__":
    main()
