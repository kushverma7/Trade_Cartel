"""ONE-YEAR IN-SAMPLE — raw-tick execution and the benchmark reproduction.

FILL CONVENTION (mandatory, applied everywhere):
  long enters ASK and is marked out on BID; short enters BID, marked out on ASK.
  TARGET is a resting limit at the exact structural price -- it fills AT the
  target and favourable overshoot is NEVER credited.
  STOP is market-triggered at the real next executable quote, so its loss is
  whatever the book showed, including slippage past the level.
  If neither is reached, the trade is liquidated by the structural rule and the
  P&L contributed by those unresolved trades is reported separately.

All P&L is in R, where 1R = |entry - structural stop| for that cycle.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/goldmap/code")
from qt_engine import Book, PTS
pd.set_option("display.width", 250)

C = pd.read_parquet("research/insample/results/cycles.parquet")
B = Book("research/microq3/data", "2025-26")
HOR = {"q3": 5400, "q3q4": 10800, "cycle": 10800, "h6": 21600}


def resolve(hold="q3q4"):
    n = len(C)
    out = dict(pnl_R=np.full(n, np.nan), why=np.array(["--"] * n, dtype=object),
               mfe_R=np.zeros(n), mae_R=np.zeros(n), hold_min=np.zeros(n))
    span = HOR[hold]
    for i, (k0, long_, entry, stop, target, risk, t0) in enumerate(zip(
            C.k0, C.long, C.entry, C.stop, C.target, C.risk, C.t_entry)):
        k1 = int(np.searchsorted(B.ny, t0 + span * 1000, "right"))
        k1 = min(k1, len(B.ny))
        if k1 - k0 < 5:
            continue
        e_i = int(B.ask[k0]) if long_ else int(B.bid[k0])
        ex = B.bid[k0:k1] if long_ else B.ask[k0:k1]
        fav = (ex.astype(np.int64) - e_i) if long_ else (e_i - ex.astype(np.int64))
        tms = B.ny[k0:k1]
        rmax = np.maximum.accumulate(fav); rmin = np.minimum.accumulate(fav)
        m = len(fav)
        tp_pts = abs(target - entry); sl_pts = abs(entry - stop)
        i_tp = int(np.searchsorted(rmax, int(round(tp_pts * PTS)), "left"))
        i_sl = int(np.searchsorted(-rmin, int(round(sl_pts * PTS)), "left"))
        out["mfe_R"][i] = rmax[-1] / PTS / risk
        out["mae_R"][i] = rmin[-1] / PTS / risk
        if i_tp < m and i_tp <= i_sl:
            pnl, why, j = tp_pts, "TP", i_tp                 # resting limit AT the target
        elif i_sl < m:
            pnl, why, j = fav[i_sl] / PTS, "SL", i_sl        # market stop, real quote
        else:
            pnl, why, j = fav[-1] / PTS, "TIME", m - 1
        out["pnl_R"][i] = pnl / risk
        out["why"][i] = why
        out["hold_min"][i] = (int(tms[j]) - t0) / 60000.0
    return pd.DataFrame(out, index=C.index)


def stats(d):
    p = pd.to_numeric(d.pnl_R, errors="coerce").dropna().to_numpy(dtype=float)
    if len(p) == 0:
        return None
    gp, gl = p[p > 0].sum(), -p[p < 0].sum()
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    dd = pk - eq
    b = m = 0
    for v in p:
        b = b + 1 if v <= 0 else 0; m = max(m, b)
    x = np.arange(len(eq))
    r2 = float(np.corrcoef(x, eq)[0, 1] ** 2) if len(eq) > 2 else np.nan
    dd_ = d.assign(_p=pd.to_numeric(d.pnl_R, errors="coerce")).dropna(subset=["_p"])
    mo = dd_.groupby(pd.to_datetime(dd_.date).dt.to_period("M"))._p.sum()
    return dict(n=len(p), pf=(gp / gl if gl > 0 else np.inf), exp=p.mean(), net=p.sum(),
                wr=100 * (p > 0).mean(), mdd=float(dd.max()),
                ulcer=float(np.sqrt((dd ** 2).mean())), r2=r2, streak=m,
                months_pos=int((mo > 0).sum()), months=len(mo),
                tp=int((d.why == "TP").sum()), sl=int((d.why == "SL").sum()),
                time=int((d.why == "TIME").sum()),
                time_R=float(d.pnl_R[d.why == "TIME"].sum()))


if __name__ == "__main__":
    for hold in ("q3", "q3q4"):
        R = resolve(hold)
        for c in R.columns:                       # per column, so dtypes survive
            C[f"{c}_{hold}"] = R[c].to_numpy()
    C.to_parquet("research/insample/results/cycles_resolved.parquet", index=False)
    D = C.rename(columns={"pnl_R_q3q4": "pnl_R", "why_q3q4": "why"})
    print("ONE-YEAR IN-SAMPLE, 2025-08-21 to 2026-08-20. Liquidation: end of Q4 (Q3+Q4).\n")
    s = stats(D)
    print(f"UNFILTERED UNIVERSE: n={s['n']}  PF={s['pf']:.3f}  exp={s['exp']:+.3f}R  "
          f"net={s['net']:+.2f}R  WR={s['wr']:.1f}%  maxDD={s['mdd']:.2f}R")
    print(f"  exits: TP {s['tp']}  SL {s['sl']}  TIME {s['time']}  "
          f"(time exits contribute {s['time_R']:+.2f}R of the {s['net']:+.2f}R)\n")

    print("=" * 122)
    print("BENCHMARK REPRODUCTION — the other researcher's four models, rebuilt from raw data")
    print("=" * 122)
    print(f"  {'model':<34}{'n':>5}{'PF':>9}{'exp R':>9}{'net R':>9}{'WR':>8}"
          f"{'maxDD':>8}{'R2':>7}{'strk':>6}{'mo+':>7}  reported")
    MODELS = {
        "A  Q2eff<=.40, DFR<=.80, RR<=1": (D.q2_eff <= 0.40) & (D.dfr_over_q1 <= 0.80) & (D.rr <= 1.00),
        "B  A + Q1eff>=.20, Q2eff<=.425": (D.q2_eff <= 0.425) & (D.dfr_over_q1 <= 0.80) & (D.rr <= 1.00) & (D.q1_eff >= 0.20),
        "C  sweep<=.20, DFR<=.80": (D.sweep_depth <= 0.20) & (D.dfr_over_q1 <= 0.80),
        "D  C + activity 20-70%": (D.sweep_depth <= 0.20) & (D.dfr_over_q1 <= 0.80) & (D.act_pct.between(0.20, 0.70)),
        "MaxPF  D1, Q2ret>=.05, Q1eff>=.5, RR>=.5":
            (D.cycle == "D1") & (D.q2_dir_ret >= 0.05) & (D.q1_eff >= 0.50) & (D.rr >= 0.50),
    }
    REP = {"A  Q2eff<=.40, DFR<=.80, RR<=1": "26 tr, PF 5.29, +0.405R, DD 1.00R, R2 .981",
           "B  A + Q1eff>=.20, Q2eff<=.425": "22 tr, PF 8.10, +0.469R, DD 1R, R2 .976",
           "C  sweep<=.20, DFR<=.80": "28 tr, PF 5.05, +1.231R, +34.46R",
           "D  C + activity 20-70%": "15 tr, PF 10.25, +1.852R, DD 2.75R",
           "MaxPF  D1, Q2ret>=.05, Q1eff>=.5, RR>=.5": "15 tr, PF 28.58, +0.926R, DD 0.28R"}
    for nm, m in MODELS.items():
        s = stats(D[m])
        if s is None:
            print(f"  {nm:<34}{0:>5}   (no trades)"); continue
        print(f"  {nm:<34}{s['n']:>5}{s['pf']:>9.2f}{s['exp']:>+9.3f}{s['net']:>+9.2f}"
              f"{s['wr']:>7.1f}%{s['mdd']:>8.2f}{s['r2']:>7.3f}{s['streak']:>6}"
              f"{s['months_pos']:>4}/{s['months']:<2}  {REP[nm]}")
