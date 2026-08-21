"""Audit the built tick file. Reports; never edits. Writes audit.json.

Two classifiers carry the weight here.

EMPTY HOURS. Dukascopy answers HTTP 200 with zero bytes for an hour it has no
ticks for. On a 24x5 instrument most of those are the market being shut, so
calling them all "missing data" would bury the ones that matter. Every empty
hour is therefore attributed against gold's actual session calendar -- which is
run in NEW YORK time, because that is the clock the settlement break and the
weekly open/close follow, and its Melbourne wall-clock time moves with two
separate DST calendars:
    EXPECTED    Saturday; Sunday before the 18:00 NY reopen; Friday from the
                17:00 NY close; the daily 17:00-18:00 NY settlement break; or a
                listed exchange holiday.
    UNEXPECTED  anything else -- a real hole in the feed. Listed individually.

GAPS. Same idea applied to the intervals between consecutive ticks, so a gap is
labelled weekend / maintenance / holiday / UNEXPLAINED rather than just counted.
"""
import datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROC, LOGS = os.path.join(BASE, "processed"), os.path.join(BASE, "logs")
NAME = "GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20"

MEL, NY, UTC = ZoneInfo("Australia/Melbourne"), ZoneInfo("America/New_York"), dt.timezone.utc
GAP_MIN = 5.0            # minutes; below this a quiet book is not a gap
EXTREME_SPREAD = 5.0     # USD; gold's median spread is ~0.6

# Gold's session calendar, in NEW YORK time -- the clock the settlement break
# and the weekly open/close actually follow. Two kinds of closure:
#   FULL_HOLIDAY  no trading at all on that NY calendar date.
#   EARLY_CLOSE   trading stops at the given NY hour and does not resume that day.
# Only dates that are genuine COMEX/spot-gold closures belong here: a wrong entry
# would EXCUSE a real outage, which is the failure mode that matters.
FULL_HOLIDAYS = {
    "2025-12-25": "Christmas Day",
    "2026-01-01": "New Year's Day",
    "2026-04-03": "Good Friday",
}
EARLY_CLOSE = {                       # NY hour from which the market is shut
    "2025-09-01": (13, "US Labor Day (early close)"),
    "2025-11-27": (13, "US Thanksgiving (early close)"),
    "2025-11-28": (13, "day after US Thanksgiving (early close)"),
    "2025-12-24": (13, "Christmas Eve (early close)"),
    "2025-12-31": (13, "New Year's Eve (early close)"),
    "2026-01-19": (13, "US Martin Luther King Jr. Day (early close)"),
    "2026-02-16": (13, "US Presidents' Day (early close)"),
    "2026-05-25": (13, "US Memorial Day (early close)"),
    "2026-06-19": (13, "US Juneteenth (early close)"),
    "2026-07-03": (13, "US Independence Day observed (early close)"),
}
# Kept for the README's day-level "why is this date missing" table.
HOLIDAYS = {**{d: v for d, v in FULL_HOLIDAYS.items()},
            **{d: v[1] for d, v in EARLY_CLOSE.items()}}

CLOSED_WEEKEND, CLOSED_MAINT, CLOSED_HOLIDAY = "weekend", "maintenance", "holiday"


def market_closed(n):
    """n: a NEW-YORK-local datetime. -> (bucket, reason) if gold is shut, else None.

    Gold's trading day runs 18:00 NY to 17:00 NY the next day, with a one-hour
    settlement break in between and a weekend shutdown from Friday 17:00 to
    Sunday 18:00. The 18:00 open belongs to the FOLLOWING calendar date, so the
    evening before a full holiday never opens -- that case is what made the
    Good Friday shutdown look unexplained under endpoint matching.
    """
    d, wd, h = n.date(), n.weekday(), n.hour          # Mon=0 .. Sun=6
    ds = d.isoformat()
    if wd == 5:
        return CLOSED_WEEKEND, "Saturday - market closed"
    if wd == 6 and h < 18:
        return CLOSED_WEEKEND, "Sunday before the 18:00 NY weekly reopen"
    if wd == 4 and h >= 17:
        return CLOSED_WEEKEND, "Friday after the 17:00 NY weekly close"
    if ds in FULL_HOLIDAYS:
        return CLOSED_HOLIDAY, f"holiday: {FULL_HOLIDAYS[ds]}"
    if ds in EARLY_CLOSE and h >= EARLY_CLOSE[ds][0]:
        return CLOSED_HOLIDAY, EARLY_CLOSE[ds][1]
    if h >= 18:
        nxt = (d + dt.timedelta(days=1)).isoformat()
        if nxt in FULL_HOLIDAYS:
            return CLOSED_HOLIDAY, f"eve of holiday: {FULL_HOLIDAYS[nxt]}"
    if h == 17:
        return CLOSED_MAINT, "daily 17:00-18:00 NY settlement break"
    return None


def classify_empty_hour(t_utc):
    """An hour Dukascopy returned zero bytes for. -> (EXPECTED|UNEXPECTED, why)."""
    n = t_utc.astimezone(NY)
    c = market_closed(n)
    if c:
        return "EXPECTED", c[1]
    return "UNEXPECTED", f"NY {n:%Y-%m-%d %a %H:%M} - no ticks published"


# A gap is EXPECTED when a scheduled closure accounts for essentially all of it.
# Measured, not pattern-matched: walk the gap minute by minute and count the
# minutes the market was actually open. A little open time at each end is normal
# -- the book thins before a close and takes a moment to quote after a reopen --
# so a small allowance is permitted, but a gap that overlaps NO closure at all is
# never excused however short it is.
OPEN_MINUTE_ALLOWANCE = 15


def classify_gap(a_utc, b_utc):
    total = int((b_utc - a_utc).total_seconds() // 60)
    an, bn = a_utc.astimezone(NY), b_utc.astimezone(NY)
    off_a, off_b = an.utcoffset(), bn.utcoffset()
    fixed = off_a if off_a == off_b else None      # US DST shift inside the gap?

    open_min, buckets = 0, {}
    step = 1
    for k in range(1, max(total, 1)):
        t = a_utc + dt.timedelta(minutes=k * step)
        if t >= b_utc:
            break
        n = (t + fixed).replace(tzinfo=NY) if fixed is not None else t.astimezone(NY)
        c = market_closed(n)
        if c is None:
            open_min += 1
        else:
            buckets[c] = buckets.get(c, 0) + 1

    if buckets and open_min <= OPEN_MINUTE_ALLOWANCE:
        # A shutdown that spans a holiday AND the weekend around it has more
        # weekend minutes than holiday minutes, but "holiday" is the informative
        # label, so it wins; the daily break only wins when nothing else applies.
        for pref in (CLOSED_HOLIDAY, CLOSED_WEEKEND, CLOSED_MAINT):
            hits = {k: v for k, v in buckets.items() if k[0] == pref}
            if hits:
                (bucket, reason), _ = max(hits.items(), key=lambda kv: kv[1])
                return bucket, f"{reason}; {open_min} open minute(s) inside the gap"
    return "UNEXPLAINED", (f"NY {an:%Y-%m-%d %a %H:%M} -> {bn:%Y-%m-%d %a %H:%M}; "
                           f"{open_min} of {total} minutes were open-market")


def checkpoint_summary():
    """Download-side truth: how many hours were requested, empty, unresolved."""
    recs = {}
    with open(os.path.join(LOGS, "checkpoint.jsonl")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            prev = recs.get(r["hour_utc"])
            if prev is None or prev["status"] not in ("ok", "empty") \
                    or r["status"] in ("ok", "empty"):
                recs[r["hour_utc"]] = r
    empties, unresolved = [], []
    for k in sorted(recs):
        r = recs[k]
        if r["status"] == "empty":
            cls, why = classify_empty_hour(dt.datetime.fromisoformat(k))
            empties.append({"hour_utc": k, "class": cls, "reason": why})
        elif r["status"] != "ok":
            unresolved.append({"hour_utc": k, "status": r["status"],
                               "retries": r.get("retries", 0),
                               "errors": r.get("errors", [])})
    return recs, empties, unresolved


def main():
    path = os.path.join(PROC, NAME + ".parquet")
    print(f"reading {path}")
    n = pq.ParquetFile(path).metadata.num_rows
    print(f"rows: {n:,}\n")

    # Load ONE column at a time. Holding the whole 8-column Arrow table plus its
    # numpy copies would peak near 10 GB on 91.6M rows; column-wise reads keep the
    # transient cost to a single column and the resident cost to the arrays kept.
    def col(name):
        tb = pq.read_table(path, columns=[name])
        a = tb.column(0).to_numpy(zero_copy_only=False)
        del tb
        return a

    def tcol(name):
        """Timestamp column -> int64 epoch milliseconds.

        A tz-aware Arrow timestamp lands in numpy as an OBJECT array of pandas
        Timestamps, which is both ~10x the memory and unusable for arithmetic.
        Casting inside Arrow to int64 first gives the exact underlying epoch-ms
        value and skips the object round trip entirely."""
        tb = pq.read_table(path, columns=[name])
        a = tb.column(0).cast(pa.int64()).to_numpy(zero_copy_only=False)
        del tb
        return a

    ts = tcol("timestamp_utc")                                  # epoch ms, UTC
    mel = tcol("timestamp_melbourne").astype("datetime64[ms]")  # local wall clock
    bid, ask = col("bid"), col("ask")
    bv, av = col("bid_volume"), col("ask_volume")
    mid, spread = col("mid"), col("spread")

    R = {}
    R["total_ticks"] = int(n)
    R["first_tick_utc"] = str(np.datetime64(int(ts[0]), "ms")) + "Z"
    R["last_tick_utc"] = str(np.datetime64(int(ts[-1]), "ms")) + "Z"
    R["first_tick_melbourne"] = str(mel[0])
    R["last_tick_melbourne"] = str(mel[-1])

    # ---- ordering / duplicates -------------------------------------------
    d = np.diff(ts)
    R["timestamps_out_of_order"] = int((d < 0).sum())
    R["duplicate_timestamps"] = int((d == 0).sum())
    # Only ticks sharing a millisecond can possibly be exact duplicates, so
    # compare just those pairs, field by field, vectorised. Materialising a
    # 91.6M x 5 key matrix (or looping in Python) is neither affordable here.
    i = np.flatnonzero(d == 0)
    if i.size:
        same = ((bid[i] == bid[i + 1]) & (ask[i] == ask[i + 1]) &
                (bv[i] == bv[i + 1]) & (av[i] == av[i + 1]))
        dup_idx = (i[same] + 1)
    else:
        dup_idx = np.empty(0, dtype=np.int64)
    R["exact_duplicate_rows"] = int(dup_idx.size)
    R["exact_duplicate_row_indices_sample"] = [int(x) for x in dup_idx[:20]]

    # ---- field validity ---------------------------------------------------
    R["missing_bid"] = int(np.isnan(bid).sum())
    R["missing_ask"] = int(np.isnan(ask).sum())
    R["missing_bid_volume"] = int(np.isnan(bv).sum())
    R["missing_ask_volume"] = int(np.isnan(av).sum())
    R["bid_le_zero"] = int((bid <= 0).sum())
    R["ask_le_zero"] = int((ask <= 0).sum())
    R["bid_gt_ask"] = int((bid > ask).sum())
    R["zero_spread"] = int((spread == 0).sum())
    R["extreme_spread_gt_%.1f" % EXTREME_SPREAD] = int((spread > EXTREME_SPREAD).sum())
    R["negative_spread"] = int((spread < 0).sum())
    R["mid_recompute_max_abs_error"] = float(np.abs(mid - (bid + ask) / 2).max())
    invalid = (np.isnan(bid) | np.isnan(ask) | (bid <= 0) | (ask <= 0) | (bid > ask))
    R["invalid_price_rows"] = int(invalid.sum())

    R["spread_stats"] = {
        "min": float(spread.min()), "p01": float(np.percentile(spread, 1)),
        "median": float(np.median(spread)), "mean": float(spread.mean()),
        "p99": float(np.percentile(spread, 99)),
        "p99_99": float(np.percentile(spread, 99.99)), "max": float(spread.max()),
    }
    R["price_range"] = {"bid_min": float(bid.min()), "bid_max": float(bid.max()),
                        "ask_min": float(ask.min()), "ask_max": float(ask.max())}
    R["volume_stats"] = {
        "bid_volume_min": float(bv.min()), "bid_volume_max": float(bv.max()),
        "bid_volume_mean": float(bv.mean()), "bid_volume_zero_count": int((bv == 0).sum()),
        "ask_volume_min": float(av.min()), "ask_volume_max": float(av.max()),
        "ask_volume_mean": float(av.mean()), "ask_volume_zero_count": int((av == 0).sum()),
    }

    # ---- coverage by Melbourne calendar day -------------------------------
    mel_day = mel.astype("datetime64[D]")
    days, counts = np.unique(mel_day, return_counts=True)
    d0, d1 = np.datetime64("2025-08-21", "D"), np.datetime64("2026-08-20", "D")
    requested = int((d1 - d0).astype(int)) + 1
    R["days_requested_melbourne"] = requested
    R["days_with_data"] = int(len(days))
    R["ticks_per_day"] = {
        "mean": float(counts.mean()), "median": float(np.median(counts)),
        "min": int(counts.min()), "max": int(counts.max()),
        "min_day": str(days[counts.argmin()]), "max_day": str(days[counts.argmax()]),
    }
    present = set(days.astype(str))
    allday = {str(d0 + np.timedelta64(i, "D")) for i in range(requested)}
    missing_days = sorted(allday - present)
    R["days_with_no_data"] = missing_days
    R["days_with_no_data_count"] = len(missing_days)
    R["missing_day_reasons"] = {
        dd: ("Saturday" if dt.date.fromisoformat(dd).weekday() == 5 else
             "Sunday" if dt.date.fromisoformat(dd).weekday() == 6 else
             HOLIDAYS.get(dd, "UNEXPLAINED"))
        for dd in missing_days}

    # ---- per-year and per-month breakdown (Melbourne calendar) ------------
    dstr = days.astype(str)
    by_year, by_month = {}, {}
    for ds, c in zip(dstr, counts):
        y, m = ds[:4], ds[:7]
        a = by_year.setdefault(y, {"ticks": 0, "trading_days": 0})
        a["ticks"] += int(c); a["trading_days"] += 1
        b = by_month.setdefault(m, {"ticks": 0, "trading_days": 0})
        b["ticks"] += int(c); b["trading_days"] += 1
    R["by_year"] = by_year
    R["by_month"] = dict(sorted(by_month.items()))

    # ---- download-side accounting ----------------------------------------
    recs, empties, unresolved = checkpoint_summary()
    exp = [e for e in empties if e["class"] == "EXPECTED"]
    unexp = [e for e in empties if e["class"] == "UNEXPECTED"]
    R["hours_requested"] = len(recs)
    R["hours_with_ticks"] = sum(r["status"] == "ok" for r in recs.values())
    R["hours_empty"] = len(empties)
    R["hours_empty_expected_closed_market"] = len(exp)
    R["hours_empty_unexpected"] = len(unexp)
    R["hours_empty_unexpected_list"] = unexp[:200]
    R["unresolved_download_hours"] = len(unresolved)
    R["unresolved_download_hours_list"] = unresolved
    ereason = {}
    for e in exp:
        # Group on the WHOLE reason. Splitting on ":" truncated "Sunday before
        # the 18:00 NY weekly reopen" to "Sunday before the 18".
        k = e["reason"]
        if k.startswith("holiday: "):
            k = k[len("holiday: "):]
        ereason[k] = ereason.get(k, 0) + 1
    R["empty_hour_reasons"] = dict(sorted(ereason.items(), key=lambda x: -x[1]))

    # ---- gaps -------------------------------------------------------------
    thresh = int(GAP_MIN * 60_000)
    gi = np.flatnonzero(d > thresh)
    buckets, gaps = {}, []
    for i in gi:
        a = dt.datetime.fromtimestamp(ts[i] / 1000, UTC)
        b = dt.datetime.fromtimestamp(ts[i + 1] / 1000, UTC)
        label, detail = classify_gap(a, b)
        buckets[label] = buckets.get(label, 0) + 1
        gaps.append({"start_utc": a.isoformat(), "end_utc": b.isoformat(),
                     "start_melbourne": str(a.astimezone(MEL).replace(tzinfo=None)),
                     "minutes": round(int(d[i]) / 60000, 2),
                     "class": label, "detail": detail})
    R["gap_threshold_minutes"] = GAP_MIN
    R["gaps_total"] = len(gaps)
    R["gaps_by_class"] = buckets
    ug = sorted([g for g in gaps if g["class"] == "UNEXPLAINED"], key=lambda g: -g["minutes"])
    R["gaps_unexplained_count"] = len(ug)
    R["gaps_unexplained_total_minutes"] = round(sum(g["minutes"] for g in ug), 2)
    R["gaps_unexplained_longest_minutes"] = round(max((g["minutes"] for g in ug), default=0), 2)
    R["gaps_unexplained_top50"] = ug[:50]
    R["gaps_longest_10"] = sorted(gaps, key=lambda g: -g["minutes"])[:10]

    json.dump(R, open(os.path.join(LOGS, "audit.json"), "w"), indent=2)
    json.dump(gaps, open(os.path.join(LOGS, "gaps_all.json"), "w"), indent=2)

    for k in ("total_ticks", "first_tick_utc", "last_tick_utc", "first_tick_melbourne",
              "last_tick_melbourne", "days_requested_melbourne", "days_with_data",
              "ticks_per_day", "timestamps_out_of_order", "duplicate_timestamps",
              "exact_duplicate_rows", "missing_bid", "missing_ask", "bid_gt_ask",
              "invalid_price_rows", "zero_spread", "negative_spread",
              "extreme_spread_gt_5.0", "mid_recompute_max_abs_error", "spread_stats",
              "price_range", "by_year", "hours_requested", "hours_with_ticks",
              "hours_empty", "hours_empty_expected_closed_market",
              "hours_empty_unexpected", "unresolved_download_hours",
              "days_with_no_data_count", "gaps_total", "gaps_by_class",
              "gaps_unexplained_count"):
        print(f"{k:36s} {R[k]}")
    print("\nmonthly:")
    for m, v in R["by_month"].items():
        print(f"  {m}  {v['ticks']:>12,} ticks  {v['trading_days']:>3} days")
    print("\nlongest gaps:")
    for g in R["gaps_longest_10"]:
        print(f"  {g['minutes']:>9.1f} min  {g['class']:<12s} {g['start_utc']} -> {g['end_utc']}  {g['detail']}")
    if ug:
        print(f"\nUNEXPLAINED gaps ({len(ug)}), longest 15:")
        for g in ug[:15]:
            print(f"  {g['minutes']:>9.1f} min  {g['start_utc']} -> {g['end_utc']}  {g['detail']}")
    if unexp:
        print(f"\nUNEXPECTED empty hours ({len(unexp)}), first 20:")
        for e in unexp[:20]:
            print(f"  {e['hour_utc']}  {e['reason']}")
    print("\n-> logs/audit.json, logs/gaps_all.json")


if __name__ == "__main__":
    main()
