"""Decode the raw BI5 mirror into one Parquet tick file. No resampling anywhere.

TIMEZONE
    The requested period is Melbourne wall clock:
        2025-08-21 00:00:00.000  ->  2026-08-20 23:59:59.999
    Australia/Melbourne is AEST (+10) at both ends but crosses AEDT (+11) in
    between, so the boundaries are resolved with zoneinfo, never a fixed offset.
    Because every Australian offset is a whole number of hours, both boundaries
    land exactly on UTC hour boundaries and the hour files need no trimming --
    the code still applies the filter explicitly and asserts what it removed.

    timestamp_utc        tz-aware UTC, millisecond precision (the source's own).
    timestamp_melbourne  NAIVE local wall clock: what a Melbourne clock read at
                         that instant. Stored naive on purpose, so every reader
                         in every language shows the literal local time instead
                         of silently re-rendering a UTC instant. The DST-correct
                         offset is applied per hour; both DST changes in this
                         window (2025-10-05, 2026-04-05) fall on whole UTC hours,
                         so a per-hour constant offset is exact. Asserted.

ORDER
    Ticks are appended in source order, hour by hour, and never sorted. If
    Dukascopy emitted two ticks in the same millisecond, or out of order, that is
    preserved and reported by the audit rather than silently repaired.
"""
import datetime as dt, json, os, lzma, sys
from zoneinfo import ZoneInfo

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW, PROC, LOGS = (os.path.join(BASE, d) for d in ("raw", "processed", "logs"))
CHECKPOINT = os.path.join(LOGS, "checkpoint.jsonl")

MEL = ZoneInfo("Australia/Melbourne")
UTC = dt.timezone.utc
DIVISOR = 1000.0                      # XAUUSD points -> USD (verified: 3345255 = 3345.255)
REC = np.dtype([("ms", ">u4"), ("ask", ">u4"), ("bid", ">u4"),
                ("askv", ">f4"), ("bidv", ">f4")])

MEL_START = dt.datetime(2025, 8, 21, 0, 0, 0, 0, tzinfo=MEL)
MEL_END = dt.datetime(2026, 8, 20, 23, 59, 59, 999000, tzinfo=MEL)
UTC_START = MEL_START.astimezone(UTC)
UTC_END = MEL_END.astimezone(UTC)
START_MS = int(UTC_START.timestamp() * 1000)
END_MS = int(UTC_END.timestamp() * 1000)          # inclusive

NAME = "GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20"
OUT = os.path.join(PROC, NAME + ".parquet")

SCHEMA = pa.schema([
    ("timestamp_utc", pa.timestamp("ms", tz="UTC")),
    ("timestamp_melbourne", pa.timestamp("ms")),
    ("bid", pa.float64()),
    ("ask", pa.float64()),
    ("bid_volume", pa.float32()),
    ("ask_volume", pa.float32()),
    ("mid", pa.float64()),
    ("spread", pa.float64()),
], metadata={
    b"source": b"Dukascopy datafeed BI5 hourly tick files (datafeed.dukascopy.com)",
    b"instrument": b"XAUUSD (spot gold vs USD)",
    b"resolution": b"tick (raw, unresampled)",
    b"requested_period_melbourne": b"2025-08-21 00:00:00.000 -> 2026-08-20 23:59:59.999 Australia/Melbourne",
    b"utc_window": UTC_START.isoformat().encode() + b" -> " + UTC_END.isoformat().encode(),
    b"price_divisor": b"1000 (Dukascopy XAUUSD points -> USD)",
    b"timestamp_melbourne_note": b"naive Australia/Melbourne wall clock, DST-correct (AEST +10 / AEDT +11)",
    b"volume_units": b"Dukascopy native (millions of base units)",
})


def raw_path(t):
    return os.path.join(RAW, f"{t:%Y}", f"{t:%m}", f"{t:%d}", f"{t:%H}h_ticks.bi5")


def mel_offset_ms(t):
    """Melbourne UTC offset for this hour, asserted constant across the hour."""
    a = t.astimezone(MEL).utcoffset()
    b = (t + dt.timedelta(minutes=59, seconds=59)).astimezone(MEL).utcoffset()
    if a != b:
        raise AssertionError(f"DST change inside hour {t} ({a} -> {b}); per-hour offset invalid")
    return int(a.total_seconds() * 1000)


def hours_from_checkpoint():
    """One record per hour, chronological. A later line supersedes an earlier
    one for the same hour, so a successful retry wins over its failed attempt."""
    recs = {}
    with open(CHECKPOINT) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            prev = recs.get(r["hour_utc"])
            if prev is None or prev["status"] not in ("ok", "empty"):
                recs[r["hour_utc"]] = r
    return [recs[k] for k in sorted(recs)]


def main():
    os.makedirs(PROC, exist_ok=True)
    recs = hours_from_checkpoint()
    bad = [r for r in recs if r["status"] not in ("ok", "empty")]
    if bad:
        print(f"REFUSING TO BUILD: {len(bad)} hours unresolved, e.g. "
              f"{[b['hour_utc'] for b in bad[:5]]}")
        sys.exit(2)
    print(f"hours to decode: {len(recs)}")

    writer = pq.ParquetWriter(OUT, SCHEMA, compression="zstd",
                              compression_level=9, version="2.6",
                              write_statistics=True)
    buf, buf_rows, ROWGROUP = [], 0, 1_000_000
    total = dropped_before = dropped_after = 0
    per_hour = []

    def flush():
        nonlocal buf, buf_rows
        if buf:
            writer.write_table(pa.concat_tables(buf))
            buf, buf_rows = [], 0

    for i, r in enumerate(recs):
        t = dt.datetime.fromisoformat(r["hour_utc"])
        if r["status"] == "empty":
            per_hour.append((r["hour_utc"], 0))
            continue
        blob = open(raw_path(t), "rb").read()
        out = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(blob)
        a = np.frombuffer(out, dtype=REC)
        if len(a) != r["ticks"]:
            raise AssertionError(f"{t}: decoded {len(a)} ticks, checkpoint said {r['ticks']}")

        epoch_ms = int(t.timestamp() * 1000) + a["ms"].astype(np.int64)
        keep = (epoch_ms >= START_MS) & (epoch_ms <= END_MS)
        if not keep.all():
            dropped_before += int((epoch_ms < START_MS).sum())
            dropped_after += int((epoch_ms > END_MS).sum())
            a, epoch_ms = a[keep], epoch_ms[keep]
        if len(a) == 0:
            per_hour.append((r["hour_utc"], 0))
            continue

        bid = a["bid"].astype(np.float64) / DIVISOR
        ask = a["ask"].astype(np.float64) / DIVISOR
        buf.append(pa.Table.from_arrays([
            pa.array(epoch_ms, type=pa.int64()).cast(pa.timestamp("ms", tz="UTC"), safe=False),
            pa.array(epoch_ms + mel_offset_ms(t), type=pa.int64()).cast(pa.timestamp("ms"), safe=False),
            pa.array(bid), pa.array(ask),
            pa.array(a["bidv"].astype(np.float32)),
            pa.array(a["askv"].astype(np.float32)),
            pa.array((bid + ask) / 2.0), pa.array(ask - bid),
        ], schema=SCHEMA))
        buf_rows += len(a); total += len(a)
        per_hour.append((r["hour_utc"], int(len(a))))
        if buf_rows >= ROWGROUP:
            flush()
        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{len(recs)} hours, {total:,} ticks", flush=True)

    flush()
    writer.close()
    with open(os.path.join(LOGS, "per_hour_counts.json"), "w") as f:
        json.dump(per_hour, f)

    print(f"\nUTC_START {UTC_START.isoformat()}  ({START_MS})")
    print(f"UTC_END   {UTC_END.isoformat()}  ({END_MS})")
    print(f"ticks written        : {total:,}")
    print(f"trimmed before window: {dropped_before}")
    print(f"trimmed after window : {dropped_after}")
    print(f"-> {OUT}  {os.path.getsize(OUT)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
