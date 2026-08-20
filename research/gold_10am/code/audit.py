"""Data audit for the Gold 10AM study. Runs BEFORE any backtest.

Establishes what the feed actually contains, then answers the single question
that decides whether the strategy is even reconstructable: does a Melbourne
09:50 and 10:00 candle exist on every trading day, and does that change
between AEST and AEDT?

Nothing here fills, substitutes or smooths. A missing candle is a finding.
"""
import os, sys, json, gzip, csv, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

RAW = os.path.join(core.RAW, "xauusd_1m_bid_dukascopy.csv.gz")
OUT = os.path.join(core.HERE, "..", "results")
TAB = os.path.join(core.HERE, "..", "tables")


def integrity(rows):
    """rows: raw (utc,o,h,l,c,v)."""
    bad_ohlc = zero = 0
    dup = 0
    seen = set()
    gaps = []
    prev = None
    for t, o, h, l, c, v in rows:
        if t in seen:
            dup += 1
        seen.add(t)
        if min(o, h, l, c) <= 0:
            zero += 1
        if not (h >= max(o, c) and l <= min(o, c) and h >= l):
            bad_ohlc += 1
        if prev is not None:
            d = (t - prev).total_seconds() / 60.0
            if d > 1:
                gaps.append((prev, t, d))
        prev = t
    return dict(n=len(rows), first=rows[0][0].isoformat(), last=rows[-1][0].isoformat(),
                duplicates=dup, zero_price_rows=zero, invalid_ohlc_rows=bad_ohlc,
                gap_count=len(gaps)), gaps


def daily_break(mrows):
    """Which Melbourne minutes-of-day are systematically absent?
    Counts, per minute-of-day, how many Melbourne weekdays have that minute."""
    days = set()
    have = collections.Counter()
    for r in mrows:
        days.add(r["date"])
        have[r["minute"]] += 1
    return days, have


def coverage(days5, mrows):
    """Per-day availability of the 09:50 and 10:00 5-minute buckets."""
    rows = []
    minute_days = core.minutes_by_day(mrows)
    for d in sorted(days5):
        bars = days5[d]
        m = {b["minute"]: b for b in bars}
        ref = m.get(core.REF_MIN)
        body = m.get(core.BODY_MIN)
        dstflag = bars[0]["dst"]
        rows.append(dict(date=d.isoformat(), weekday=d.strftime("%a"),
                         dst="AEDT" if dstflag else "AEST",
                         year=d.year, month=f"{d.year}-{d.month:02d}",
                         ref=ref is not None, body=body is not None,
                         ref_minutes=ref["n_min"] if ref else 0,
                         body_minutes=body["n_min"] if body else 0,
                         n_bars=len(bars),
                         n_minutes=len(minute_days.get(d, []))))
    return rows


def group(rows, key, pred_fields=("ref", "body")):
    g = collections.OrderedDict()
    for r in rows:
        k = r[key]
        b = g.setdefault(k, dict(days=0, ref=0, body=0, both=0, neither=0))
        b["days"] += 1
        b["ref"] += bool(r["ref"]); b["body"] += bool(r["body"])
        b["both"] += bool(r["ref"] and r["body"])
        b["neither"] += (not r["ref"] and not r["body"])
    return g


def pct(a, b):
    return f"{100.0*a/b:.2f}%" if b else "—"


def main():
    print("loading 1-minute bid data ...", flush=True)
    raw = core.load_1m(RAW)
    integ, gaps = integrity(raw)
    print(json.dumps(integ, indent=2))

    mrows = core.to_melbourne(raw)
    weekend = sum(1 for r in mrows if r["local"].weekday() >= 5)
    bars5 = core.build_5m(mrows)
    days5 = core.by_day(bars5)

    days, have = daily_break(mrows)
    # a "trading day" = a Melbourne calendar date with any data at all
    total_days = len(days5)

    cov = coverage(days5, mrows)
    both = sum(1 for r in cov if r["ref"] and r["body"])
    refok = sum(1 for r in cov if r["ref"])
    bodyok = sum(1 for r in cov if r["body"])

    os.makedirs(TAB, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(TAB, "coverage_by_day.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(cov[0].keys())); w.writeheader(); w.writerows(cov)

    # the daily maintenance window, measured not assumed
    ndays_wd = len({r["date"] for r in mrows if r["local"].weekday() < 5})
    thin = sorted((m, c) for m, c in have.items() if c < 0.5 * ndays_wd)
    thin_minutes = [m for m, c in thin]

    summary = dict(
        integrity=integ,
        weekend_minute_rows=weekend,
        melbourne_days=total_days,
        coverage=dict(total_days=total_days,
                      ref_0950=refok, body_1000=bodyok, both=both,
                      ref_missing=total_days - refok,
                      body_missing=total_days - bodyok,
                      both_missing=sum(1 for r in cov if not r["ref"] and not r["body"]),
                      ref_pct=pct(refok, total_days), body_pct=pct(bodyok, total_days),
                      both_pct=pct(both, total_days)),
        by_year={str(k): v for k, v in group(cov, "year").items()},
        by_month={str(k): v for k, v in group(cov, "month").items()},
        by_dst={str(k): v for k, v in group(cov, "dst").items()},
        by_weekday={str(k): v for k, v in group(cov, "weekday").items()},
        thin_minutes_of_day=thin_minutes,
        largest_gaps=[(a.isoformat(), b.isoformat(), d) for a, b, d in
                      sorted(gaps, key=lambda g: -g[2])[:15]],
    )
    with open(os.path.join(OUT, "audit.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\nMelbourne days with data : {total_days}")
    print(f"09:50 bucket present     : {refok}  ({pct(refok,total_days)})")
    print(f"10:00 bucket present     : {bodyok}  ({pct(bodyok,total_days)})")
    print(f"BOTH present             : {both}  ({pct(both,total_days)})")
    print("\nBy DST period:")
    for k, v in summary["by_dst"].items():
        print(f"  {k}: days={v['days']:>4}  09:50={v['ref']:>4} ({pct(v['ref'],v['days'])})"
              f"  10:00={v['body']:>4} ({pct(v['body'],v['days'])})  both={v['both']:>4}")
    print("\nBy year:")
    for k, v in summary["by_year"].items():
        print(f"  {k}: days={v['days']:>4}  both={v['both']:>4} ({pct(v['both'],v['days'])})")
    if thin_minutes:
        lo, hi = min(thin_minutes), max(thin_minutes)
        print(f"\nSystematically thin Melbourne minutes-of-day: {len(thin_minutes)} "
              f"spanning {lo//60:02d}:{lo%60:02d}..{hi//60:02d}:{hi%60:02d}")
    print("\nwrote results/audit.json and tables/coverage_by_day.csv")


if __name__ == "__main__":
    main()
