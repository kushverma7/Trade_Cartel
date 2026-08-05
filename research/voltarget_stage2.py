"""
Stage 2: the adoption bar applied to the surviving volatility-targeting arms.

Stage 1 left exactly one family standing -- variant B, entry volatility
targeting multiplied by the existing G1 regime multiplier. Pure VT (variant A)
was neutral to negative, and the soft open-volatility ceiling (variant C) did
the one thing the brief said to watch for: win rate jumped to 30% and the top
ten trades' share of gross profit collapsed from 39.5% to 24.2%. It cut the
right tail.

This file runs the four adoption-bar tests stage 1 could not:

  BAR 3  PLATEAU. A single lookback that works is a fitted number. The
         estimator's lookback is swept across neighbouring values, and the
         result must be flat across them rather than spiking at one.

  BAR 5  US30 TRANSFER. Same logic, only the sizing target re-solved. Note in
         advance: the raw champion has no edge on the US30 file in this repo,
         so this test may return no information rather than a verdict. That
         possibility is reported honestly instead of being read as a pass.

  BAR 6  RIGHT-TAIL AMPUTATION, diagnosed explicitly rather than asserted.
         The system's edge is concentrated in a handful of trades, so the
         question is not whether the candidate has a good average but whether
         the largest winners survive it. Every trade is matched between the
         baseline and the candidate BY ENTRY BAR -- the entry logic is
         untouched, so the same signals fire and the pairs are exact -- and the
         change in the biggest winners is read off directly.

  LEFT vs RIGHT. The same matched pairs answer the question the brief actually
  asks: does volatility targeting reduce the left tail, the right tail, or
  both? Sizing changes are symmetric by construction, so an arm that shrinks
  losses must shrink wins too; what matters is the RATIO.
"""
import numpy as np, pandas as pd

from backtest import exit_lab
from research.voltarget import (Book, vt_series, evaluate, show, COLS,
                                montecarlo, BPD)


def matched(base_tr, cand_tr):
    """Pair trades by entry bar. Entry logic is unchanged, so pairing is exact."""
    b = {t["bar"]: t for t in base_tr}
    c = {t["bar"]: t for t in cand_tr}
    keys = sorted(set(b) & set(c))
    return (np.array([b[k]["pnl"] for k in keys]),
            np.array([c[k]["pnl"] for k in keys]), len(b), len(c), len(keys))


def tail_report(name, bp, cp):
    """Where does the candidate's money come from, relative to the baseline?"""
    out = {"arm": name}
    for tag, lo, hi in (("top1%", 0.99, 1.0), ("top5%", 0.95, 1.0),
                        ("top10%", 0.90, 1.0)):
        qb, qc = np.quantile(bp, lo), np.quantile(cp, lo)
        out[f"{tag}_base"] = bp[bp >= qb].sum()
        out[f"{tag}_cand"] = cp[cp >= qc].sum()
    out["bot10%_base"] = bp[bp <= np.quantile(bp, 0.10)].sum()
    out["bot10%_cand"] = cp[cp <= np.quantile(cp, 0.10)].sum()
    out["gross_win_base"] = bp[bp > 0].sum(); out["gross_win_cand"] = cp[cp > 0].sum()
    out["gross_loss_base"] = -bp[bp < 0].sum(); out["gross_loss_cand"] = -cp[cp < 0].sum()
    return out


def main():
    gold = Book("data/xauusd_15m.csv.gz")

    # ---------------------------------------------------------------- BAR 3
    print("=" * 132)
    print("ADOPTION BAR 3 -- PLATEAU. Sweep the estimator lookback. A spike at one")
    print("  value is a fitted number; the arm must be flat across neighbours.")
    print("=" * 132)
    h, l, c = (gold.df[k].to_numpy(float) for k in ("high", "low", "close"))
    rows = []
    for n in (14, 16, 18, 20, 22, 25, 30, 40):
        sig = exit_lab._atr(h, l, c, n) / c * np.sqrt(BPD)
        m, _ = vt_series(gold.df, sig)
        rows.append(evaluate(gold, f"B: VT ATR{n} x G1", 25.0,
                             risk_series=m * gold.g1, risk_series_adds=True))
    r = pd.Series(np.r_[np.nan, np.diff(np.log(c))])
    for d in (10, 15, 20, 30, 40):
        sig = r.rolling(d * BPD).std(ddof=0).to_numpy() * np.sqrt(BPD)
        m, _ = vt_series(gold.df, sig)
        rows.append(evaluate(gold, f"B: VT SD{d}d x G1", 25.0,
                             risk_series=m * gold.g1, risk_series_adds=True))
    t = show(rows, "plateau sweep, 25% budget")
    t.to_csv("research/voltarget_plateau.csv", index=False)

    # ---------------------------------------------------------------- BAR 6
    print("\n" + "=" * 132)
    print("ADOPTION BAR 6 -- RIGHT-TAIL DIAGNOSIS, matched trade by trade")
    print("=" * 132)
    _rE, trE = gold.solve(25.0)
    _rG, trG = gold.solve(25.0, risk_series=gold.g1)
    cands = {}
    for nm in ("ATR20", "SD20d"):
        m, _ = vt_series(gold.df, gold.est[nm])
        _r, tr = gold.solve(25.0, risk_series=m * gold.g1, risk_series_adds=True)
        cands[f"B: VT {nm} x G1"] = tr
    m20, _ = vt_series(gold.df, gold.est["ATR20"])
    _r, trC = gold.solve(25.0, risk_series=gold.g1,
                         vol_daily=gold.est["ATR20"], open_vol_cap=2.0)
    cands["C: G1 + open-vol cap 2%"] = trC

    recs = []
    for nm, tr in cands.items():
        bp, cp, nb, nc, nk = matched(trG, tr)
        rec = tail_report(nm, bp, cp)
        rec["matched"] = nk; rec["n_base"] = nb; rec["n_cand"] = nc
        recs.append(rec)
    d = pd.DataFrame(recs)
    for tag in ("top1%", "top5%", "top10%", "bot10%", "gross_win", "gross_loss"):
        d[f"{tag}_x"] = d[f"{tag}_cand"] / d[f"{tag}_base"]
    print("  All ratios are CANDIDATE / G1-baseline on the SAME trades.")
    print("  A pure sizing change scales everything; the question is the ratio of")
    print("  ratios -- does it shrink losses more than it shrinks wins?\n")
    cols = ["arm", "matched", "top1%_x", "top5%_x", "top10%_x",
            "bot10%_x", "gross_win_x", "gross_loss_x"]
    d["win_vs_loss"] = d["gross_win_x"] / d["gross_loss_x"]
    print(d[cols + ["win_vs_loss"]].to_string(
        index=False, float_format=lambda v: f"{v:9.4f}"))
    d.to_csv("research/voltarget_tails.csv", index=False)
    print("\n  win_vs_loss > 1 means the arm keeps more of the winners than of the")
    print("  losers, which is the only asymmetry a sizing rule can legitimately buy.")

    # ---------------------------------------------------------------- BAR 5
    print("\n" + "=" * 132)
    print("ADOPTION BAR 5 -- US30 TRANSFER, identical logic, sizing target re-solved")
    print("=" * 132)
    us = Book("data/us30_15m.csv.gz")
    print(f"  US30: {len(us.df)} 30m bars, {us.df.index[0].date()} -> "
          f"{us.df.index[-1].date()} ({us.yrs:.2f}y)")
    urows = [evaluate(us, "E  (baseline)", 25.0),
             evaluate(us, "G1 (baseline)", 25.0, risk_series=us.g1)]
    for nm in ("ATR20", "SD20d"):
        m, _ = vt_series(us.df, us.est[nm])
        urows.append(evaluate(us, f"B: VT {nm} x G1", 25.0,
                              risk_series=m * us.g1, risk_series_adds=True))
    if all(x is None for x in urows):
        print("  Every US30 arm returned fewer than 60 trades. The transfer test")
        print("  CANNOT BE RUN on this file -- see the note below.")
    else:
        u = show([x for x in urows if x], "US30, 25% budget")
        u.to_csv("research/voltarget_us30.csv", index=False)
    sE = exit_lab.stats(us.run(1.0))
    print(f"\n  DIAGNOSTIC, unsized: the LOCKED config on US30 at a flat 1% risk"
          f" gives n={sE['n']}, PF={sE['pf']:.3f}, net={sE['net_pct']:+.1f}%.")
    print("  If that baseline has no edge, this test returns NO INFORMATION about")
    print("  the candidate -- a filter or a sizing rule cannot be shown to improve")
    print("  a system that does not work. That is not a pass and not a failure.")


if __name__ == "__main__":
    main()
