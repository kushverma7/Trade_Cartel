"""ONE-YEAR IN-SAMPLE OPTIMISATION. 2025-08-21 to 2026-08-20 ONLY.

EVERY NUMBER PRODUCED BY THIS FILE IS IN-SAMPLE. Nothing here is a forecast.

Exhaustive grid over the structural QT dimensions. Cheap statistics are computed
for every cell; the full smoothness set (drawdown, Ulcer, R-squared, streak,
monthly consistency, exit mix) is computed only for candidates that survive a
minimum trade count, so the search stays honest about sample size at every tier.
"""
import sys, itertools, numpy as np, pandas as pd
sys.path.insert(0, "research/insample/code")
pd.set_option("display.width", 260)

C = pd.read_parquet("research/insample/results/cycles_resolved.parquet")
C["pnl_R"] = pd.to_numeric(C.pnl_R_q3q4, errors="coerce")
C["why"] = C.why_q3q4
C = C.dropna(subset=["pnl_R"]).reset_index(drop=True)
P = C.pnl_R.to_numpy(float)
MON = pd.to_datetime(C.date).dt.to_period("M").astype(str).to_numpy()
print(f"ONE-YEAR IN-SAMPLE universe: {len(C)} cycles, "
      f"base PF {P[P>0].sum()/-P[P<0].sum():.3f}, base exp {P.mean():+.3f}R")

GRID = dict(
    q2_eff_max=[0.30, 0.325, 0.35, 0.375, 0.40, 0.425, 0.4375, 0.45, 0.475, 0.50, 0.55, 0.60, 9.0],
    dfr_max=[0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 9.0],
    q1_eff_min=[0.0, 0.20, 0.30, 0.40, 0.50],
    rr_max=[0.75, 1.00, 1.50, 2.00, 99.0],
    sweep_max=[0.075, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30, 0.50, 9.0],
    act=[(0.0, 1.0), (0.0, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 1.0),
         (0.20, 0.70), (0.20, 0.80), (0.30, 0.80)],
    cyc=["ALL", "D1", "D2", "D3", "D4", "D123"],
    swp=["any", "single", "both"],
)
F = {k: C[k].to_numpy(float) for k in ("q2_eff", "dfr_over_q1", "q1_eff", "rr",
                                       "sweep_depth", "act_pct")}
F["q2_eff"] = np.nan_to_num(F["q2_eff"], nan=9.9)
F["act_pct"] = np.nan_to_num(F["act_pct"], nan=-1.0)
CYC = C.cycle.to_numpy(); SWP = C.sweep.to_numpy()
CYCM = {"ALL": np.ones(len(C), bool), "D123": CYC != "D4",
        **{d: CYC == d for d in ("D1", "D2", "D3", "D4")}}
SWPM = {"any": np.ones(len(C), bool), "single": SWP != "both", "both": SWP == "both"}

keys = ["q2_eff_max", "dfr_max", "q1_eff_min", "rr_max", "sweep_max", "act", "cyc", "swp"]
# Nested incremental masks with early termination. The filters are monotone, so a
# branch that already has fewer than 10 trades can never gain any deeper in.
rows = []
MIN_N = 10
for cyc in GRID["cyc"]:
    m1 = CYCM[cyc]
    if m1.sum() < MIN_N: continue
    for swp in GRID["swp"]:
        m2 = m1 & SWPM[swp]
        if m2.sum() < MIN_N: continue
        for a0, a1 in GRID["act"]:
            m3 = m2 if (a0, a1) == (0.0, 1.0) else m2 & (F["act_pct"] >= a0) & (F["act_pct"] <= a1)
            if m3.sum() < MIN_N: continue
            for q2e in GRID["q2_eff_max"]:
                m4 = m3 & (F["q2_eff"] <= q2e)
                if m4.sum() < MIN_N: continue
                for dfr in GRID["dfr_max"]:
                    m5 = m4 & (F["dfr_over_q1"] <= dfr)
                    if m5.sum() < MIN_N: continue
                    for q1e in GRID["q1_eff_min"]:
                        m6 = m5 & (F["q1_eff"] >= q1e)
                        if m6.sum() < MIN_N: continue
                        for rr in GRID["rr_max"]:
                            m7 = m6 & (F["rr"] <= rr)
                            if m7.sum() < MIN_N: continue
                            for swd in GRID["sweep_max"]:
                                m = m7 & (F["sweep_depth"] <= swd)
                                n = int(m.sum())
                                if n < MIN_N: continue
                                p = P[m]
                                gl = -p[p < 0].sum()
                                rows.append((n, (p[p > 0].sum() / gl) if gl > 0 else np.inf,
                                             p.mean(), p.sum(), 100 * (p > 0).mean(),
                                             q2e, dfr, q1e, rr, swd, (a0, a1), cyc, swp))
print(f"cells evaluated with >= {MIN_N} trades: {len(rows):,}")
S = pd.DataFrame(rows, columns=["n", "pf", "exp", "net", "wr"] + keys)
print(f"cells with >= 10 trades: {len(S):,}")
S.to_parquet("research/insample/results/search_all.parquet", index=False)


def full(m):
    p = P[m]
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    dd = pk - eq
    b = k = 0
    for v in p:
        b = b + 1 if v <= 0 else 0; k = max(k, b)
    mo = pd.Series(p).groupby(MON[m]).sum()
    w = C.why.to_numpy()[m]
    gl = -p[p < 0].sum()
    return dict(n=len(p), pf=(p[p > 0].sum() / gl if gl > 0 else np.inf), exp=p.mean(),
                net=p.sum(), wr=100 * (p > 0).mean(), mdd=float(dd.max()),
                ulcer=float(np.sqrt((dd ** 2).mean())),
                r2=float(np.corrcoef(np.arange(len(eq)), eq)[0, 1] ** 2) if len(eq) > 2 else np.nan,
                streak=k, mo_pos=int((mo > 0).sum()), mo=len(mo),
                tp=int((w == "TP").sum()), sl=int((w == "SL").sum()), time=int((w == "TIME").sum()),
                time_R=float(p[w == "TIME"].sum()))


def mask_of(r):
    m = CYCM[r.cyc] & SWPM[r.swp]
    m &= F["q2_eff"] <= r.q2_eff_max
    m &= F["dfr_over_q1"] <= r.dfr_max
    m &= F["q1_eff"] >= r.q1_eff_min
    m &= F["rr"] <= r.rr_max
    m &= F["sweep_depth"] <= r.sweep_max
    if (r.act[0], r.act[1]) != (0.0, 1.0):
        m &= (F["act_pct"] >= r.act[0]) & (F["act_pct"] <= r.act[1])
    return m


def show(title, sub, by, asc=False, k=1):
    if len(sub) == 0:
        print(f"\n{title}\n  (nothing qualifies)"); return None
    r = sub.sort_values(by, ascending=asc).iloc[0]
    s = full(mask_of(r))
    print(f"\n{title}")
    print(f"  rule: cyc={r.cyc} sweep={r.swp} Q2eff<={r.q2_eff_max:g} DFR<={r.dfr_max:g} "
          f"Q1eff>={r.q1_eff_min:g} RR<={r.rr_max:g} sweepdepth<={r.sweep_max:g} act={r.act}")
    print(f"  n={s['n']}  PF={s['pf']:.2f}  exp={s['exp']:+.3f}R  net={s['net']:+.2f}R  "
          f"WR={s['wr']:.1f}%  DD={s['mdd']:.2f}R  Ulcer={s['ulcer']:.2f}  R2={s['r2']:.3f}  "
          f"streak={s['streak']}  months+={s['mo_pos']}/{s['mo']}")
    print(f"  exits: TP {s['tp']}  SL {s['sl']}  TIME {s['time']}  "
          f"(time exits = {s['time_R']:+.2f}R of {s['net']:+.2f}R)")
    return s


print("\n" + "=" * 122)
print("TRADE-COUNT TIERS — highest PF at each minimum sample size   [ALL IN-SAMPLE]")
print("=" * 122)
for tier in (10, 15, 20, 25, 30, 40, 50, 75):
    show(f"--- highest PF with n >= {tier} ---", S[S.n >= tier], "pf")
