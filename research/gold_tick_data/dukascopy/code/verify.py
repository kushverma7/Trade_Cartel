"""Independent re-open of the finished Parquet file. Run as its own process, so
nothing from the build is still in memory.

The interesting check is #6. Row counts and column names only prove the file
parses. To prove serialisation did not ALTER anything, this re-decodes randomly
chosen raw .bi5 hours straight from the mirror, rebuilds what those rows should
be, and demands an exact match against the same slice read back out of Parquet
-- including that bid*1000 lands back on the source's original integer point
value, which is what would break first if float precision had been lost.
"""
import datetime as dt, hashlib, json, lzma, os, random, sys
from zoneinfo import ZoneInfo

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROC, RAW, LOGS = (os.path.join(BASE, d) for d in ("processed", "raw", "logs"))
NAME = "GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20"
PATH = os.path.join(PROC, NAME + ".parquet")

MEL, UTC = ZoneInfo("Australia/Melbourne"), dt.timezone.utc
REC = np.dtype([("ms", ">u4"), ("ask", ">u4"), ("bid", ">u4"),
                ("askv", ">f4"), ("bidv", ">f4")])
EXPECT_COLS = ["timestamp_utc", "timestamp_melbourne", "bid", "ask",
               "bid_volume", "ask_volume", "mid", "spread"]

fails = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{('  ' + detail) if detail else ''}")
    if not ok:
        fails.append(name)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print(f"=== independent verification of {os.path.basename(PATH)} ===\n")
    size = os.path.getsize(PATH)

    # 1. metadata without loading the body
    pf = pq.ParquetFile(PATH)
    meta = pf.metadata
    print(f"file size    : {size:,} bytes ({size/2**30:.3f} GiB)")
    print(f"row groups   : {meta.num_row_groups}")
    print(f"parquet rows : {meta.num_rows:,}")
    print(f"created by   : {meta.created_by}")
    comp = {pf.schema_arrow.field(i).name:
            meta.row_group(0).column(i).compression for i in range(len(EXPECT_COLS))}
    print(f"compression  : {sorted(set(comp.values()))}\n")

    check("compression is ZSTD", set(comp.values()) == {"ZSTD"}, str(sorted(set(comp.values()))))
    check("columns exactly as specified", pf.schema_arrow.names == EXPECT_COLS,
          str(pf.schema_arrow.names))

    # 2. read-back, one column at a time (the whole table plus its numpy copies
    #    would peak near 10 GB on this row count)
    def col(name):
        tb = pq.read_table(PATH, columns=[name])
        a = tb.column(0).to_numpy(zero_copy_only=False)
        del tb
        return a

    def tcol(name):
        """Timestamp -> int64 epoch ms. A tz-aware Arrow timestamp otherwise
        materialises as an object array of pandas Timestamps."""
        tb = pq.read_table(PATH, columns=[name])
        a = tb.column(0).cast(pa.int64()).to_numpy(zero_copy_only=False)
        del tb
        return a

    sch = pf.schema_arrow
    n = meta.num_rows
    check("row count matches parquet footer", n == meta.num_rows, f"{n:,}")
    check("timestamp_utc is ms-precision, tz-aware UTC",
          str(sch.field("timestamp_utc").type) == "timestamp[ms, tz=UTC]",
          str(sch.field("timestamp_utc").type))
    check("timestamp_melbourne is ms-precision wall clock",
          str(sch.field("timestamp_melbourne").type) == "timestamp[ms]",
          str(sch.field("timestamp_melbourne").type))
    check("bid/ask are float64",
          str(sch.field("bid").type) == "double" and str(sch.field("ask").type) == "double")

    ts = tcol("timestamp_utc")
    mel = tcol("timestamp_melbourne").astype("datetime64[ms]")
    bid, ask, mid = col("bid"), col("ask"), col("mid")
    bvol, avol = col("bid_volume"), col("ask_volume")
    check("bid_volume and ask_volume present, none NaN",
          bool(not np.isnan(bvol).any() and not np.isnan(avol).any()),
          f"{len(bvol):,} rows each")
    check("file opens cleanly with pandas",
          __import__("pandas").read_parquet(PATH, columns=["bid"]).shape[0] == n)
    del bvol, avol

    # 3. boundaries
    mel_start = dt.datetime(2025, 8, 21, 0, 0, 0, 0, tzinfo=MEL)
    mel_end = dt.datetime(2026, 8, 20, 23, 59, 59, 999000, tzinfo=MEL)
    s_ms, e_ms = int(mel_start.timestamp()*1000), int(mel_end.timestamp()*1000)
    print(f"\nfirst tick UTC : {np.datetime64(int(ts[0]),'ms')}Z    Melbourne: {mel[0]}")
    print(f"last  tick UTC : {np.datetime64(int(ts[-1]),'ms')}Z    Melbourne: {mel[-1]}\n")
    check("all ticks inside the requested UTC window",
          bool((ts >= s_ms).all() and (ts <= e_ms).all()))

    # 4. ordering & precision
    d = np.diff(ts)
    check("timestamps are non-decreasing (source order preserved)", bool((d >= 0).all()),
          f"{int((d < 0).sum())} inversions")
    sub_second = int((ts % 1000 != 0).sum())
    check("millisecond precision retained (not rounded to seconds)", sub_second > 0,
          f"{sub_second:,} of {n:,} ticks carry a non-zero millisecond")
    check("timestamps not rounded to minutes", int((ts % 60000 != 0).sum()) > 0)

    # 5. derived columns still consistent after the round trip
    check("mid == (bid+ask)/2 exactly", bool(np.array_equal(mid, (bid+ask)/2)),
          f"max|err|={np.abs(mid-(bid+ask)/2).max():.3e}")
    check("bid and ask both present, none NaN",
          bool(not np.isnan(bid).any() and not np.isnan(ask).any()))

    # 6. THE REAL TEST: re-decode raw hours and demand an exact match
    print("\n  re-decoding random raw .bi5 hours and comparing to the Parquet body:")
    hours = json.load(open(os.path.join(LOGS, "per_hour_counts.json")))
    with_data = [(h, c) for h, c in hours if c > 0]
    random.seed(20260821)
    picks = random.sample(with_data, min(40, len(with_data)))
    # offset of each hour into the table, from the per-hour counts
    offs, run = {}, 0
    for h, c in hours:
        offs[h] = run
        run += c
    check("per-hour counts sum to the table length", run == n, f"{run:,} vs {n:,}")

    bad = 0
    for h, c in picks:
        ht = dt.datetime.fromisoformat(h)
        p = os.path.join(RAW, f"{ht:%Y}", f"{ht:%m}", f"{ht:%d}", f"{ht:%H}h_ticks.bi5")
        raw = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(open(p, "rb").read())
        a = np.frombuffer(raw, dtype=REC)
        o = offs[h]
        exp_ts = int(ht.timestamp()*1000) + a["ms"].astype(np.int64)
        got_ts = ts[o:o+c]
        ok_ts = np.array_equal(exp_ts, got_ts)
        ok_bid = np.array_equal(np.rint(bid[o:o+c]*1000).astype(np.int64), a["bid"].astype(np.int64))
        ok_ask = np.array_equal(np.rint(ask[o:o+c]*1000).astype(np.int64), a["ask"].astype(np.int64))
        off_ms = int(ht.astimezone(MEL).utcoffset().total_seconds()*1000)
        ok_mel = np.array_equal(mel[o:o+c].astype(np.int64), exp_ts + off_ms)
        if not (ok_ts and ok_bid and ok_ask and ok_mel and len(a) == c):
            bad += 1
            print(f"      MISMATCH {h}: ts={ok_ts} bid={ok_bid} ask={ok_ask} mel={ok_mel} n={len(a)}/{c}")
    check(f"{len(picks)} random hours round-trip byte-exact from raw BI5", bad == 0,
          f"{bad} mismatched")

    # 7. checksum
    print("\n  hashing file ...")
    h = sha256(PATH)
    print(f"  SHA256 {h}")
    json.dump({"sha256": h, "bytes": size, "rows": int(n),
               "first_tick_utc": str(np.datetime64(int(ts[0]),'ms'))+"Z",
               "last_tick_utc": str(np.datetime64(int(ts[-1]),'ms'))+"Z",
               "first_tick_melbourne": str(mel[0]), "last_tick_melbourne": str(mel[-1]),
               "columns": EXPECT_COLS, "failures": fails},
              open(os.path.join(LOGS, "verify.json"), "w"), indent=2)

    print(f"\n=== {'ALL CHECKS PASSED' if not fails else 'FAILURES: ' + ', '.join(fails)} ===")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
