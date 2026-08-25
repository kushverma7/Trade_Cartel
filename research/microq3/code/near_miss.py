"""Near-miss study and filter waterfall. NO THRESHOLD IS SELECTED HERE.

Every bearish 18:45-19:00 NY anchor is taken, the first body break is found with
NO window cap, and each of the four filters is evaluated and recorded as a flag.
Trades are then GROUPED by which filters they fail. The exits are frozen at
SL 15.50 / TP 25.50 throughout; nothing in this file tunes anything.

The question it answers: if a filter carries predictive information, the trades
that fail ONLY that filter must be measurably worse than the trades that pass
everything. If they are not, the filter is selecting noise.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "research/microq3/code")
import engine as E
from engine import PTS

SL, TP = 15.5, 25.5
ANCHOR, ALEN = 18 * 60 + 45, 15
WIN_FROM, WIN_CAP, WIN_FAR = 19 * 60, 19 * 60 + 30, 23 * 60
BODY_MIN, BODY_MAX, QD, SPR = 1.00, 6.25, 6.25, 1.50
pd.set_option("display.width", 260)


def universe():
    rows = []
    for day in E.DAYS:
        day = int(day)
        a = E.candle(day, ANCHOR, ANCHOR + ALEN, "mid")
        if a is None or a["nmin"] < 5:
            continue
        o, c = a["o"] / PTS, a["c"] / PTS
        if c >= o:                                   # bearish anchors only
            continue
        body = o - c
        bhi, blo = o, c
        hit = None
        for cd in E.five_min_candles(day, WIN_FROM, WIN_FAR, "mid"):
            cc = cd["c"] / PTS
            if cc < blo:
                hit = (cd, False); break
            if cc > bhi:
                hit = (cd, True); break
        if hit is None:
            continue
        cd, long_ = hit
        k0 = int(np.searchsorted(E.NY, cd["t_close"], "right"))
        kend = E.session_end_index(day, 17 * 60)
        if kend is None or k0 >= kend:
            continue
        bid, ask = int(E.BID[k0]) / PTS, int(E.ASK[k0]) / PTS
        entry = ask if long_ else bid
        r = entry % 25.0
        dq = min(r, 25.0 - r)
        res = E.resolve(k0, kend, long_, SL, TP)
        raw = E.resolve(k0, kend, long_, 1e6, 1e6)     # unrestricted excursions
        if res is None or raw is None:
            continue
        rows.append(dict(
            date=pd.Timestamp(day * 86400000, unit="ms").date(),
            kind="FLIP_LONG" if long_ else "A_SHORT",
            body=body, spread=ask - bid, dist25=dq, sig_hm=cd["hm_start"],
            ok_body=(BODY_MIN <= body <= BODY_MAX),
            ok_spread=(ask - bid <= SPR),
            ok_q=(dq <= QD),
            ok_win=(cd["hm_start"] < WIN_CAP),
            pnl=res["pnl"], reason=res["reason"],
            mfe=raw["mfe"], mae=abs(raw["mae"])))
    return pd.DataFrame(rows)


U = universe()
U["nfail"] = 4 - U[["ok_body", "ok_spread", "ok_q", "ok_win"]].sum(axis=1)
U["month"] = pd.to_datetime(U.date).dt.to_period("M").astype(str)
U.to_csv("research/microq3/results/near_miss_universe.csv", index=False)
print(f"bearish 18:45 anchors that produce a break: {len(U)}\n")


def block(name, d):
    if len(d) == 0:
        return dict(group=name, n=0)
    p = d.pnl.to_numpy()
    eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
    mo = d.groupby("month").pnl.sum()
    return dict(group=name, n=len(d),
                p_tp=100 * (d.reason == "TP").mean(),
                pf=(p[p > 0].sum() / -p[p < 0].sum()) if (p < 0).any() else np.inf,
                exp=p.mean(), net=p.sum(),
                mfe50=d.mfe.median(), mfe75=d.mfe.quantile(.75), mfe90=d.mfe.quantile(.90),
                mae50=d.mae.median(), mae75=d.mae.quantile(.75), mae90=d.mae.quantile(.90),
                mdd=float((pk - eq).max()),
                mo_pos=f"{int((mo > 0).sum())}/{len(mo)}")


G = [
    block("PASS ALL FILTERS", U[U.nfail == 0]),
    block("FAIL BODY ONLY", U[(U.nfail == 1) & (~U.ok_body)]),
    block("FAIL SPREAD ONLY", U[(U.nfail == 1) & (~U.ok_spread)]),
    block("FAIL $25 DISTANCE ONLY", U[(U.nfail == 1) & (~U.ok_q)]),
    block("FAIL SIGNAL WINDOW ONLY", U[(U.nfail == 1) & (~U.ok_win)]),
    block("FAIL TWO FILTERS", U[U.nfail == 2]),
    block("FAIL THREE OR MORE", U[U.nfail >= 3]),
    block("ALL BEARISH ANCHORS", U),
]
T = pd.DataFrame(G)
T.to_csv("research/microq3/results/near_miss_groups.csv", index=False)
print("=" * 150)
print("NEAR-MISS STUDY — exits frozen at SL 15.50 / TP 25.50. P(TP) = reached +25.5 before -15.5.")
print("=" * 150)
hdr = (f"{'group':<26}{'n':>4}{'P(TP)':>8}{'PF':>8}{'exp':>8}{'net':>9}"
       f"{'MFE 50':>8}{'75':>7}{'90':>7}{'MAE 50':>8}{'75':>7}{'90':>7}{'maxDD':>8}{'months+':>9}")
print(hdr)
for r in G:
    if r["n"] == 0:
        print(f"{r['group']:<26}{0:>4}   (no trades in this group)"); continue
    print(f"{r['group']:<26}{r['n']:>4}{r['p_tp']:>7.0f}%{r['pf']:>8.2f}{r['exp']:>8.2f}{r['net']:>9.1f}"
          f"{r['mfe50']:>8.1f}{r['mfe75']:>7.1f}{r['mfe90']:>7.1f}"
          f"{r['mae50']:>8.1f}{r['mae75']:>7.1f}{r['mae90']:>7.1f}{r['mdd']:>8.1f}{r['mo_pos']:>9}")

print("\n" + "=" * 150)
print("WATERFALL — filters added in the submitted order")
print("=" * 150)
FIL = [("unfiltered bearish anchor", None),
       ("+ body filter", "ok_body"),
       ("+ quarter proximity", "ok_q"),
       ("+ spread filter", "ok_spread"),
       ("+ 30-minute expiry", "ok_win")]


def waterfall(order, tag):
    print(f"\n  {tag}")
    print(f"    {'step':<34}{'n':>5}{'WR':>7}{'PF':>8}{'exp':>8}{'maxDD':>8}{'d exp':>8}")
    m = pd.Series(True, index=U.index); prev = None
    for nm, col in order:
        if col is not None:
            m = m & U[col]
        d = U[m]; p = d.pnl.to_numpy()
        if len(p) == 0:
            print(f"    {nm:<34}{0:>5}"); continue
        eq = np.cumsum(p); pk = np.maximum.accumulate(np.concatenate([[0.], eq]))[1:]
        pf = (p[p > 0].sum() / -p[p < 0].sum()) if (p < 0).any() else np.inf
        de = "" if prev is None else f"{p.mean()-prev:>+8.2f}"
        print(f"    {nm:<34}{len(p):>5}{100*(p>0).mean():>6.0f}%{pf:>8.2f}{p.mean():>8.2f}"
              f"{float((pk-eq).max()):>8.1f}{de:>8}")
        prev = p.mean()


waterfall(FIL, "submitted order: body -> quarter -> spread -> expiry")
REV = [("unfiltered bearish anchor", None),
       ("+ 30-minute expiry", "ok_win"),
       ("+ spread filter", "ok_spread"),
       ("+ quarter proximity", "ok_q"),
       ("+ body filter", "ok_body")]
waterfall(REV, "reversed order: expiry -> spread -> quarter -> body")

print("\n  MARGINAL CONTRIBUTION — each filter added LAST, to the other three")
print(f"    {'filter added last':<34}{'n before':>10}{'n after':>9}{'exp before':>12}{'exp after':>11}{'d exp':>8}")
cols = ["ok_body", "ok_q", "ok_spread", "ok_win"]
names = {"ok_body": "body", "ok_q": "quarter proximity", "ok_spread": "spread", "ok_win": "30-minute expiry"}
for c in cols:
    others = [x for x in cols if x != c]
    m0 = U[others].all(axis=1)
    m1 = m0 & U[c]
    a, b = U[m0].pnl.to_numpy(), U[m1].pnl.to_numpy()
    print(f"    {names[c]:<34}{len(a):>10}{len(b):>9}{a.mean():>12.2f}{b.mean():>11.2f}{b.mean()-a.mean():>+8.2f}")
