"""
Quarterly Theory, re-tested against the SOURCE definitions.

WHY THIS FILE EXISTS
  `levels_qt.py` encoded Quarterly Theory from memory and got four things
  wrong. The user uploaded two source documents (857483891QuarterlyTheory.pdf
  and 877399584QuarterlyTheorybyTraderDaye...) which I had not read when the
  first study was run and reported as a negative finding. Read now, they say:

    1. WEEKLY  Q1=Tuesday, Q2=Wednesday, Q3=Thursday, Q4=Friday, and "Tuesday
       midnight open is considered the True Weekly Open".
       levels_qt used Mon/Tue/Wed/Thu -- off by one whole day.
    2. DAILY   Q1 18:00-00:00, Q2 00:00-06:00 (True Daily Open at 00:00),
       Q3 06:00-12:00, Q4 12:00-18:00 -- in NEW YORK time.
       levels_qt applied those numbers to a UTC index: a 4-5 hour shift, so
       every quarter straddled two of the intended ones.
    3. TWO FORMS, not one.
         Form 1  Q1 Accumulation, Q2 Manipulation, Q3 Distribution, Q4 Rev/Cont
         Form 2  Q1 Rev/Cont,     Q2 Accumulation, Q3 Manipulation, Q4 Distribution
       Only Form 1 was tested.
    4. SESSION quarters carry different semantics from the daily/weekly ones:
       Q1 Range Formation, Q2 EXPANSION, Q3 Continuation/Pullback,
       Q4 Reversal/Profit-Taking. Not accumulation/manipulation at all.

  A negative verdict reached on wrong definitions is not a verdict. This file
  re-runs it on the source definitions and reports whether the answer changes.

KNOWN INCONSISTENCY IN THE SOURCE, STATED NOT HIDDEN
  The same document gives the daily cycle in New York time but its 90-minute
  session table in UTC/London ("Asian (Tokyo) 00:00-06:00, London 07:00-13:00,
  New York 13:00-19:00"). The two cannot both be right. Both readings are run
  below (`--tz ny` and `--tz utc`) so the choice is visible rather than
  smuggled in.

WHAT WOULD COUNT AS EDGE
  The theory makes falsifiable claims. Each gets a null it must beat:
    A  a manipulation quarter should set the cycle's extreme MORE OFTEN than
       the 1-in-4 a structureless cycle gives.
    B  a manipulation quarter should REVERSE after sweeping: the cycle should
       close on the far side of the sweep more often than a coin flip.
    C  an expansion quarter should have a LARGER range than its siblings.
    D  price relative to the True Open should predict the rest of the cycle.
    E  gating champion entries by quarter should raise PF out of sample.
  A-D are properties of the market. E is the only one that pays.
"""
import argparse
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from backtest.io import load_csv
from backtest import champion, exit_lab

NY = ZoneInfo("America/New_York")


def to_local(idx, tz):
    """The index is tz-naive UTC. Localise, then convert if asked."""
    u = idx.tz_localize("UTC")
    return u if tz == "utc" else u.tz_convert(NY)


# --------------------------------------------------------------- cycle labels
def daily_quarters(loc):
    """Q1 18-00, Q2 00-06, Q3 06-12, Q4 12-18 local. Cycle starts at 18:00."""
    h = loc.hour
    q = np.select([(h >= 18), (h < 6), (h < 12), (h < 18)], [1, 2, 3, 4], default=0)
    # the cycle a bar belongs to is named by the DATE its Q2 falls on, so the
    # 18:00-00:00 Q1 rolls forward onto the next calendar day
    base = pd.Series(loc.date, index=loc)
    cyc = np.where(h >= 18, (pd.to_datetime(base) + pd.Timedelta(days=1)).dt.date, base)
    return q, pd.Series(cyc, index=loc).astype(str).to_numpy()


def weekly_quarters(loc):
    """Q1=Tue, Q2=Wed, Q3=Thu, Q4=Fri. True Weekly Open = Tuesday 00:00."""
    d = loc.dayofweek                      # Mon=0
    q = np.select([d == 1, d == 2, d == 3, d == 4], [1, 2, 3, 4], default=0)
    # cycle id: the Tuesday that opens this week's cycle
    tue = pd.to_datetime(pd.Series(loc.date, index=loc)) - pd.to_timedelta(
        (pd.Series(d, index=loc) - 1) % 7, unit="D")
    return q, tue.dt.date.astype(str).to_numpy()


def session_quarters(loc, tz):
    """Each 6h session split into four 90-minute quarters."""
    if tz == "utc":                         # the source's own 90m table
        starts = {"ASIA": 0, "LDN": 7, "NY": 13}
    else:                                   # NY-anchored blocks
        starts = {"ASIA": 18, "LDN": 3, "NY": 8}
    mins = loc.hour * 60 + loc.minute
    q = np.zeros(len(loc), int)
    cyc = np.full(len(loc), "", object)
    day = pd.Series(loc.date, index=loc).astype(str).to_numpy()
    for nm, s0 in starts.items():
        a = s0 * 60
        rel = (mins - a) % (24 * 60)
        m = rel < 360
        q = np.where(m, (rel // 90) + 1, q)
        cyc = np.where(m, day + "_" + nm, cyc)
    return q, cyc.astype(str)


CYCLES = {"daily": daily_quarters, "weekly": weekly_quarters}


def label(df, loc, name, tz):
    if name == "session":
        return session_quarters(loc, tz)
    return CYCLES[name](loc)


# ------------------------------------------------------- A/B/C: cycle anatomy
def anatomy(df, q, cyc, name):
    """Per-quarter: extreme-setting rate, range share, and post-sweep reversal.

    A structureless cycle sets its high in each quarter 25% of the time and
    carries 25% of the range in each. Deviations are the theory's claim.
    """
    d = pd.DataFrame({"q": q, "cyc": cyc, "h": df["high"].to_numpy(),
                      "l": df["low"].to_numpy(), "c": df["close"].to_numpy(),
                      "o": df["open"].to_numpy()}, index=df.index)
    d = d[d.q > 0]
    # keep only complete cycles (all four quarters present)
    full = d.groupby("cyc")["q"].nunique()
    d = d[d.cyc.map(full).eq(4)]
    if d.empty:
        return None

    g = d.groupby(["cyc", "q"])
    qh, ql = g["h"].max(), g["l"].min()
    qrange = (qh - ql).rename("rng")
    per = pd.concat([qh.rename("h"), ql.rename("l"), qrange], axis=1).reset_index()

    # which quarter set the cycle high / low
    hi_q = per.loc[per.groupby("cyc")["h"].idxmax()].set_index("cyc")["q"]
    lo_q = per.loc[per.groupby("cyc")["l"].idxmin()].set_index("cyc")["q"]
    tot = per.groupby("cyc")["rng"].sum()
    per["share"] = per["rng"] / per["cyc"].map(tot)

    rows = []
    n = len(hi_q)
    for k in (1, 2, 3, 4):
        rows.append(dict(cycle=name, q=k, n=n,
                         sets_high=float((hi_q == k).mean()),
                         sets_low=float((lo_q == k).mean()),
                         sets_extreme=float(((hi_q == k) | (lo_q == k)).mean()) / 2,
                         range_share=float(per.loc[per.q == k, "share"].mean())))
    return pd.DataFrame(rows), d


def reversal(d, sweep_q, name, tz):
    """B: after quarter `sweep_q` sets the cycle extreme, does the cycle close
    on the OTHER side? That is the manipulation-then-distribution claim.

    Null = 50%. Anything inside +/-2 standard errors is a coin flip.
    """
    g = d.groupby(["cyc", "q"])
    qh, ql = g["h"].max(), g["l"].min()
    per = pd.concat([qh.rename("h"), ql.rename("l")], axis=1).reset_index()
    hi_q = per.loc[per.groupby("cyc")["h"].idxmax()].set_index("cyc")["q"]
    lo_q = per.loc[per.groupby("cyc")["l"].idxmin()].set_index("cyc")["q"]
    # cycle open = open of Q1, cycle close = last close
    op = d[d.q == 1].groupby("cyc")["o"].first()
    cl = d.groupby("cyc")["c"].last()
    mid = (per.groupby("cyc")["h"].max() + per.groupby("cyc")["l"].min()) / 2

    out = []
    for side, who in (("high", hi_q), ("low", lo_q)):
        sel = who[who == sweep_q].index
        if len(sel) < 30:
            continue
        # swept the high in the manipulation quarter -> expect a DOWN close
        down = (cl[sel] < op[sel]) if side == "high" else (cl[sel] > op[sel])
        below_mid = (cl[sel] < mid[sel]) if side == "high" else (cl[sel] > mid[sel])
        p = float(down.mean()); m = len(sel)
        se = (0.25 / m) ** 0.5
        out.append(dict(cycle=name, tz=tz, sweep_q=sweep_q, swept=side, n=m,
                        reverse_close=p, z=(p - 0.5) / se,
                        close_past_mid=float(below_mid.mean())))
    return out


# ------------------------------------------------ D: true open premium/discount
def true_open_test(d, name, tz):
    """True Open = open of Q2. Does being above/below it predict the rest?"""
    to = d[d.q == 2].groupby("cyc")["o"].first()
    cl = d.groupby("cyc")["c"].last()
    # measured at the END of Q2, which is when the signal is actually usable
    q2c = d[d.q == 2].groupby("cyc")["c"].last()
    common = to.index.intersection(cl.index).intersection(q2c.index)
    if len(common) < 50:
        return None
    prem = (q2c[common] > to[common])
    fwd = cl[common] - q2c[common]
    return dict(cycle=name, tz=tz, n=int(len(common)),
                prem_n=int(prem.sum()),
                prem_up_rate=float((fwd[prem] > 0).mean()) if prem.sum() else np.nan,
                disc_up_rate=float((fwd[~prem] > 0).mean()) if (~prem).sum() else np.nan,
                prem_mean=float(fwd[prem].mean()) if prem.sum() else np.nan,
                disc_mean=float(fwd[~prem].mean()) if (~prem).sum() else np.nan)


# ------------------------------------------------------- E: the only paying test
def champion_gate(df30, loc30, tz, splits=2):
    """Gate champion entries by quarter, in-sample AND out-of-sample.

    A quarter that helps in one half and hurts in the other is noise, and the
    only way to see that is to split before looking.
    """
    base, _ = champion.run(df30)
    b = exit_lab.stats(base)
    rows = [dict(gate="ALL", cycle="-", q=0, **{k: b[k] for k in ("n", "wr", "pf", "net_pct", "maxdd_pct")})]
    half = len(df30) // 2
    for name in ("daily", "weekly", "session"):
        q, _cyc = label(df30, loc30, name, tz)
        for k in (1, 2, 3, 4):
            m = q == k
            if m.sum() < 200:
                continue
            tr, _ = champion.run(df30, mask=m)
            s = exit_lab.stats(tr)
            if s["n"] < 30:
                continue
            i1 = [t for t in tr if t["bar"] < half]
            i2 = [t for t in tr if t["bar"] >= half]
            s1, s2 = exit_lab.stats(i1), exit_lab.stats(i2)
            rows.append(dict(gate=f"{name}Q{k}", cycle=name, q=k,
                             n=s["n"], wr=s["wr"], pf=s["pf"],
                             net_pct=s["net_pct"], maxdd_pct=s["maxdd_pct"],
                             pf_h1=s1["pf"], n_h1=s1["n"],
                             pf_h2=s2["pf"], n_h2=s2["n"]))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/xauusd_15m.csv.gz")
    ap.add_argument("--tz", default="both", choices=["ny", "utc", "both"])
    ap.add_argument("--out", default="research/qt_corrected.csv")
    a = ap.parse_args()

    raw = load_csv(a.csv)
    df30 = load_csv(a.csv, rule="30min")
    tzs = ["ny", "utc"] if a.tz == "both" else [a.tz]

    anat, revs, tos = [], [], []
    for tz in tzs:
        loc = to_local(raw.index, tz)
        print(f"\n{'='*78}\nTIMEZONE READING: {tz.upper()}   bars={len(raw)}\n{'='*78}")
        for name in ("daily", "weekly", "session"):
            q, cyc = label(raw, loc, name, tz)
            res = anatomy(raw, q, cyc, name)
            if res is None:
                continue
            tab, d = res
            tab["tz"] = tz
            anat.append(tab)
            print(f"\n-- {name} cycle ({tz})  complete cycles={tab['n'].iloc[0]}")
            print("   q  sets_high  sets_low  range_share   (null 0.250 each)")
            for _, r in tab.iterrows():
                print(f"   Q{int(r.q)}   {r.sets_high:8.3f}  {r.sets_low:8.3f}   {r.range_share:8.3f}")
            # Form 1 says Q2 manipulates; Form 2 says Q3 does. Test both.
            for sq in (2, 3):
                for row in reversal(d, sq, name, tz):
                    revs.append(row)
                    print(f"   sweep Q{sq} {row['swept']:<4} n={row['n']:<5} "
                          f"reverse_close={row['reverse_close']:.3f} z={row['z']:+.2f}")
            t = true_open_test(d, name, tz)
            if t:
                tos.append(t)
                print(f"   TrueOpen: premium n={t['prem_n']}/{t['n']} up_rate={t['prem_up_rate']:.3f} "
                      f"| discount up_rate={t['disc_up_rate']:.3f}")

    for lst, path in ((anat, "research/qt_corrected_anatomy.csv"),
                      (revs, "research/qt_corrected_reversal.csv"),
                      (tos, "research/qt_corrected_trueopen.csv")):
        if lst:
            t = pd.concat(lst) if isinstance(lst[0], pd.DataFrame) else pd.DataFrame(lst)
            t.to_csv(path, index=False)
            print(f"wrote {path}")

    tz0 = tzs[0]
    loc30 = to_local(df30.index, tz0)
    print(f"\n{'='*78}\nE: CHAMPION GATED BY QUARTER ({tz0})  -- the only test that pays\n{'='*78}")
    g = champion_gate(df30, loc30, tz0)
    pd.set_option("display.width", 200)
    print(g.to_string(index=False, float_format=lambda v: f"{v:7.3f}"))
    g.to_csv(a.out, index=False)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
