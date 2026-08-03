"""
MAE / MFE derivation — set the stop and the first target from what trades in
THIS market actually do, instead of guessing a multiple.

Adopted 2026-08-02 from `MASTER_BLUEPRINT.md` Stage 5, which was uploaded with
the AU200 archive and is the one methodological idea in that set worth taking.
See trader_playbooks/AU200_UPLOAD_AUDIT_2026-08-02.md.

WHY THIS MATTERS HERE
  BUG-017 is this repo's most expensive recurring mistake: a target whose
  distance is set by where a LINE happens to sit rather than by what the trade
  needs. Key levels, quarter grids and fixed point targets all fail the same
  way -- each trade gets an essentially random target/stop ratio, and no hit
  rate rescues a structure that risks 6 to make 0.46.

  Excursion-derived levels invert that. The stop comes from how far trades
  actually go against you before working, and the target from how far they
  actually run. The ratio is then a property of the market, not of a line.

DEFINITIONS (both in ATR at entry, so they are scale- and timeframe-free)
  MAE  maximum adverse excursion   - worst unrealised loss during the trade
  MFE  maximum favourable excursion - best unrealised gain during the trade

THE STOP IS DERIVED FROM WINNERS ONLY, AND THAT IS DELIBERATE
  The classic Sweeney construction asks: how far did the trades that
  eventually WORKED go against me first? A stop placed beyond the 80th
  percentile of winners' MAE keeps 80% of winners alive. Measuring MAE over
  all trades instead just rediscovers the stop you already used, because
  losers' MAE is capped by that stop -- a circularity worth naming, since it
  makes the number look stable for the wrong reason.

  To avoid that circularity entirely this module measures excursions under a
  DELIBERATELY WIDE stop (default 12 ATR) and a hold cap, so the recorded MAE
  is the market's, not the exit rule's.

READ THE OUTPUT AS A DIAGNOSTIC, NOT AS SETTINGS TO PASTE
  P80(MFE) is a target only one trade in five reaches. That is the right
  anchor for a RUNNER, not for TP1. The blueprint says "TP1"; the data here
  says otherwise, and the table prints several percentiles so the choice is
  visible rather than assumed.

MEASURED RESULT, 2026-08-02 — THE BLUEPRINT'S METHOD DOES NOT DO WHAT IT CLAIMS
  Tested on XAUUSD 15m/30m/60m, 2019-2026. The derived stop is NOT a property
  of the market. It tracks whatever measurement parameter you picked:

      wide stop 12 ATR -> derived 12.85     hold  50 bars ->  6.5 ATR
      wide stop 25 ATR -> derived 25.40     hold 100 bars ->  9.1
      wide stop 50 ATR -> derived 34.33     hold 400 bars -> 17.1
                                            hold 800 bars -> 26.3

  MAE is right-censored by any stop, and uncensored it grows with holding
  time. Log-log fit over hold length gives an exponent of 0.493 for MAE
  against 0.500 for a pure random walk. In other words the adverse side of
  this entry is statistically indistinguishable from diffusion, and "P80 of
  MAE" is a restatement of how long you held, not a discovered stop.

  Do not use this module to pick a stop. It cannot.

WHAT IT IS ACTUALLY FOR — THE EXPONENT GAP
  MFE fits an exponent of 0.558 against MAE's 0.493. The favourable side
  compounds FASTER than the adverse side, by +0.065.

  That gap is the whole edge, and it belongs to HOLD TIME rather than to the
  entry. At short holds the ratio of P80 MFE to P80 MAE is 1.08-1.10, which
  is no edge at all; by 800 bars it reaches 1.32. So:

    - a fixed target caps the trade in the low-ratio regime and throws the
      asymmetry away. This is why every fixed-target configuration in this
      repo, and every one in the uploaded AU200 archive, lost.
    - a trailing exit is what harvests the exponent gap.
    - early profit-taking is actively destructive, which independently
      reproduces the AU200 archive's own measurement: TP1 at an EMA8 pierce
      returned 14.6% WR and -$427,792 while holding the same signals to end
      of day returned 83.3% and +$1,170,926.

  This is the quantitative statement of this repo's oldest standing finding:
  THE EXIT CARRIES THE EDGE, NOT THE ENTRY. The entry supplies an exponent of
  0.493 -- a coin flip. Time supplies 0.065.
"""
import argparse

import numpy as np
import pandas as pd

FIELDS = ("open", "high", "low", "close")


def _atr(h, l, c, n=14):
    pc = np.roll(c, 1); pc[0] = c[0]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1.0 / n, adjust=False).mean().to_numpy()


def excursions(df, entry_n=100, atr_n=14, wide_stop_atr=12.0, max_hold=500,
               long_only=False, cooldown=0):
    """Walk every breakout entry forward under a wide stop, recording MAE/MFE.

    Returns one row per trade with excursions expressed in ATR at entry.
    """
    o, h, l, c = (df[k].to_numpy(float) for k in FIELDS)
    n = len(c)
    A = _atr(h, l, c, atr_n)
    hi = pd.Series(h).rolling(entry_n).max().shift(1).to_numpy()
    lo = pd.Series(l).rolling(entry_n).min().shift(1).to_numpy()

    rows = []
    i = max(entry_n, atr_n) + 1
    last_exit = -10 ** 9
    while i < n:
        a = A[i]
        if np.isnan(a) or a <= 0 or i - last_exit < cooldown:
            i += 1; continue
        d = 1 if (not np.isnan(hi[i]) and c[i] > hi[i]) else (
            -1 if (not long_only and not np.isnan(lo[i]) and c[i] < lo[i]) else 0)
        if d == 0:
            i += 1; continue

        entry = c[i]
        stop = entry - d * a * wide_stop_atr
        mae = 0.0; mfe = 0.0
        j = i + 1
        why = "hold_cap"
        while j < n and j - i <= max_hold:
            # excursions measured on the bar's extremes, in ATR at entry
            adv = (entry - l[j]) if d > 0 else (h[j] - entry)
            fav = (h[j] - entry) if d > 0 else (entry - l[j])
            mae = max(mae, adv / a)
            mfe = max(mfe, fav / a)
            hit = (l[j] <= stop) if d > 0 else (h[j] >= stop)
            if hit:
                why = "wide_stop"; break
            j += 1
        rows.append({"bar": i, "dir": d, "mae_atr": mae, "mfe_atr": mfe,
                     "bars_held": j - i, "why": why,
                     "ret_atr": (c[min(j, n - 1)] - entry) * d / a})
        last_exit = j
        i = j + 1
    return pd.DataFrame(rows)


def derive(ex, pct=80.0, winner_mfe_atr=1.0):
    """Turn an excursion table into candidate stop / target levels."""
    win = ex[ex.mfe_atr >= winner_mfe_atr]
    out = {
        "n_trades": len(ex),
        "n_winners": len(win),
        "stop_from_winner_mae": float(np.percentile(win.mae_atr, pct)) if len(win) else np.nan,
        "stop_from_all_mae": float(np.percentile(ex.mae_atr, pct)),
        "target_at_pct": float(np.percentile(ex.mfe_atr, pct)),
    }
    out["target_stop_ratio"] = (out["target_at_pct"] / out["stop_from_winner_mae"]
                                if out["stop_from_winner_mae"] else np.nan)
    return out


def table(ex):
    qs = [50, 60, 70, 75, 80, 85, 90, 95]
    return pd.DataFrame({
        "pct": qs,
        "MAE_atr": [np.percentile(ex.mae_atr, q) for q in qs],
        "MFE_atr": [np.percentile(ex.mfe_atr, q) for q in qs],
        "reach_rate": [f"{100 - q}%" for q in qs],
    })


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", default="data/xauusd_15m.csv.gz")
    ap.add_argument("--rule", default=None, help="pandas resample rule, e.g. 30min")
    ap.add_argument("--entry-n", type=int, default=100)
    ap.add_argument("--wide-stop", type=float, default=12.0)
    ap.add_argument("--max-hold", type=int, default=500)
    ap.add_argument("--pct", type=float, default=80.0)
    ap.add_argument("--long-only", action="store_true")
    a = ap.parse_args()

    from backtest.io import load_csv
    df = load_csv(a.csv, rule=a.rule)
    ex = excursions(df, entry_n=a.entry_n, wide_stop_atr=a.wide_stop,
                    max_hold=a.max_hold, long_only=a.long_only)

    print(f"\n{len(df):,} bars  ->  {len(ex)} breakout trades "
          f"(wide stop {a.wide_stop} ATR, hold cap {a.max_hold} bars)")
    print(f"  reached the wide stop: {(ex.why == 'wide_stop').sum()}"
          f"   hit the hold cap: {(ex.why == 'hold_cap').sum()}")

    print("\nEXCURSION DISTRIBUTION (ATR at entry)")
    print(table(ex).to_string(index=False, float_format=lambda v: f"{v:6.2f}"))

    d = derive(ex, pct=a.pct)
    print(f"\nDERIVED AT P{a.pct:.0f}")
    print(f"  stop  from winners' MAE : {d['stop_from_winner_mae']:.2f} ATR"
          f"   (keeps {a.pct:.0f}% of winners alive; n={d['n_winners']})")
    print(f"  stop  from ALL trades'   : {d['stop_from_all_mae']:.2f} ATR"
          f"   (circular if the sample used a tight stop -- see module docstring)")
    print(f"  target at that percentile: {d['target_at_pct']:.2f} ATR"
          f"   (reached by {100 - a.pct:.0f}% of trades)")
    print(f"  target / stop            : {d['target_stop_ratio']:.2f}"
          f"   (BUG-017 gate: must exceed 1.0)")

    print("\nWhat a TP1 should actually be: pick the percentile whose reach"
          "\nrate you want, not P80. The table above prices each choice.")

    # ---- the part that actually generalises -------------------------------
    print("\nDIFFUSION SCALING  (the levels above are hold-length artifacts;"
          "\nthis is the part that is a property of the market)")
    holds = [50, 100, 200, 400, 800]
    mae, mfe, keep = [], [], []
    for mh in holds:
        e = excursions(df, entry_n=a.entry_n, wide_stop_atr=999.0,
                       max_hold=mh, long_only=a.long_only)
        if len(e) < 25:
            continue
        keep.append(mh)
        mae.append(float(np.percentile(e.mae_atr, a.pct)))
        mfe.append(float(np.percentile(e.mfe_atr, a.pct)))
    if len(keep) >= 3:
        sm = float(np.polyfit(np.log(keep), np.log(mae), 1)[0])
        sf = float(np.polyfit(np.log(keep), np.log(mfe), 1)[0])
        print(f"  hold (bars) : {keep}")
        print(f"  P{a.pct:.0f} MAE     : {[round(v,1) for v in mae]}")
        print(f"  P{a.pct:.0f} MFE     : {[round(v,1) for v in mfe]}")
        print(f"  MFE/MAE     : {[round(b/m,2) for m,b in zip(mae,mfe)]}")
        print(f"\n  log-log slope   MAE {sm:.3f}   MFE {sf:.3f}"
              f"   (pure random walk = 0.500)")
        print(f"  exponent gap    {sf - sm:+.3f}")
        if sf - sm > 0.02:
            print("  -> the favourable side compounds FASTER than the adverse"
                  " side.\n     That gap is the edge, and it is a function of"
                  " HOLD TIME, not of\n     the entry. It is why a trailing"
                  " exit beats a fixed target here:\n     a fixed target caps"
                  " the trade in the low-ratio regime.")
        else:
            print("  -> no measurable asymmetry: both sides diffuse alike."
                  "\n     Holding longer buys nothing on this entry.")


if __name__ == "__main__":
    main()
