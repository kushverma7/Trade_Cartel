"""THE FROZEN SPECIFICATION, RUN ONCE ON DATA IT HAS NEVER SEEN.

No parameter is chosen here. Every value below is the one fixed on the audited
year before this data existed in the project:

  anchor        18:45-19:00 New York, 15 minutes, built from mid
  direction     bearish only, close < open
  body          1.00 <= |close-open| <= 6.25
  signal        first completed 5-minute close beyond a body edge, 19:00-19:30
  entry         first tick strictly after that candle; long at ask, short at bid
  quarter       |entry - nearest $25| <= 6.25
  spread        ask - bid <= 1.50 at entry
  exits         SL 15.50 / TP 25.50, tick-exact first passage
  liquidation   17:00 New York the following day

The anchor scan is reported alongside as a pre-declared diagnostic, not as a
selection: if 18:45 is again exceptional on unseen data that is evidence; if it
is unremarkable, that is evidence too. Nothing is re-fitted either way.
"""
import os, sys, numpy as np, pandas as pd
os.environ["MICROQ3_DATA"] = "research/microq3/data_holdout"
sys.path.insert(0, "research/microq3/code")
import engine as E
import microq3 as M
pd.set_option("display.width", 240)

print(f"holdout engine: {len(E.MIN):,} 1-minute NY bars across {len(E.DAYS)} NY days")
print(f"span: {pd.Timestamp(int(E.NY[0]),unit='ms')} -> {pd.Timestamp(int(E.NY[-1]),unit='ms')} NY\n")

AUD = dict(n=25, pf=5.125, exp=15.467, net=386.7, wr=76.0, mdd=15.86)
tr = M.signals()
d = M.apply(tr, 15.5, 25.5)
s = M.summarise(d)
print("=" * 96)
print("THE FROZEN STRATEGY ON THE UNSEEN YEAR")
print("=" * 96)
print(f"  {'':<26}{'audited 2025-26':>18}{'HOLDOUT 2024-25':>18}")
for k, lab, f in (("n", "trades", "{:.0f}"), ("pf", "profit factor", "{:.3f}"),
                  ("exp", "expectancy", "{:+.2f}"), ("net", "net points", "{:+.1f}"),
                  ("wr", "win rate %", "{:.1f}"), ("mdd", "max drawdown", "{:.1f}")):
    print(f"  {lab:<26}{f.format(AUD[k]):>18}{(f.format(s[k]) if s['n'] else '--'):>18}")
if s["n"]:
    print(f"\n  exits: {d.exit_reason.value_counts().to_dict()}")
    print(f"  legs : {d.kind.value_counts().to_dict()}")
    d.to_csv("research/microq3/results/holdout_ledger.csv", index=False)

    mo = d.assign(m=pd.to_datetime(d.t_entry).dt.to_period('M').astype(str)).groupby('m').pnl.agg(['count','sum'])
    print(f"\n  by month: {int((mo['sum']>0).sum())}/{len(mo)} positive")
    print("   " + "  ".join(f"{i}:{v:+.0f}" for i, v in mo['sum'].items()))

print("\n" + "=" * 96)
print("SELECTION FUNNEL ON THE UNSEEN YEAR")
print("=" * 96)
for tag, kw in (("bearish anchor + any break", dict(body_min=0, body_max=None, qdist=None, spread_max=None)),
                ("+ body 1.00-6.25", dict(qdist=None, spread_max=None)),
                ("+ within $6.25 of a $25 level", dict(spread_max=None)),
                ("+ spread <= $1.50 (FULL SPEC)", {})):
    st = M.summarise(M.apply(M.signals(**kw), 15.5, 25.5))
    print(f"  {tag:<34}{st['n']:>5}{st['pf']:>9.2f}{st['exp']:>9.2f}{st['net']:>9.1f}{st['mdd']:>9.1f}")

print("\n" + "=" * 96)
print("ANCHOR SCAN ON THE UNSEEN YEAR — pre-declared diagnostic, nothing re-fitted")
print("=" * 96)
rows = []
for st_ in range(17 * 60 + 45, 20 * 60 + 15, 5):
    x = M.summarise(M.apply(M.signals(anchor_start=st_, win_from=st_ + 15, win_to=st_ + 45), 15.5, 25.5))
    rows.append(dict(anchor=f"{st_//60:02d}:{st_%60:02d}", start=st_, **{k: x[k] for k in ("n","pf","exp","net","wr","mdd")}))
A = pd.DataFrame(rows); A.to_csv("research/microq3/results/holdout_anchor_scan.csv", index=False)
u = A[A.n >= 10]
print(A[["anchor","n","pf","exp","net","wr"]].to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
if len(u):
    row = A[A.start == 18*60+45]
    if len(row) and row.iloc[0].n >= 1:
        r = row.iloc[0]
        print(f"\n  18:45 on the unseen year: n={int(r.n)} PF={r.pf:.2f} exp={r.exp:+.2f}")
        print(f"  rank by PF among the {len(u)} anchors with n>=10: "
              f"{int((u.pf > r.pf).sum())+1} of {len(u)}   (it was 1 of 29 on the audited year)")
        print(f"  rank by expectancy: {int((u.exp > r.exp).sum())+1} of {len(u)}")
    print(f"  median PF across usable anchors: {u.pf.median():.2f}   mean expectancy {u.exp.mean():+.2f}")
