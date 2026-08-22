"""Download the authentic Dukascopy XAUUSD raw tick stream, hour by hour.

SOURCE
    https://datafeed.dukascopy.com/datafeed/XAUUSD/{YYYY}/{MM0}/{DD}/{HH}h_ticks.bi5
    MM0 is Dukascopy's ZERO-INDEXED month (January = 00, August = 07). This is a
    quirk of their feed, not a typo. Our local mirror uses real calendar months
    and the manifest records the exact source URL for every file.

FILE FORMAT (verified empirically 2026-08-21 against 2025-08-20 14:00 UTC)
    LZMA1 "alone" stream (13-byte header, magic 5d 00 00 40 00). Decompresses to
    a whole number of 20-byte big-endian records, struct '>IIIff':
        uint32  milliseconds offset from the start of the hour
        uint32  ASK  in points   (XAUUSD divisor 1000 -> 3345255 = $3345.255)
        uint32  BID  in points
        float32 ask volume       (Dukascopy units: millions of base units)
        float32 bid volume
    Note the ASK precedes the BID in the record. Getting that backwards yields a
    permanently negative spread, which the audit would catch.

RESUME
    Every hour's outcome is appended to checkpoint.jsonl. A rerun reads that file
    first and re-requests only hours that are absent or previously errored. An
    interrupted run therefore costs at most the hours in flight, never the year.

EMPTY IS NOT MISSING
    Dukascopy answers HTTP 200 with zero bytes for an hour it has no ticks for
    (weekends, the daily maintenance break, holidays). That is a real answer and
    is recorded as status "empty" — distinct from "error". Nothing is silently
    skipped: an hour that never succeeds stays in the manifest as an error.
"""
import argparse, datetime as dt, hashlib, json, lzma, os, random, struct, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(BASE, "raw")
LOGS = os.path.join(BASE, "logs")
CHECKPOINT = os.path.join(LOGS, "checkpoint.jsonl")

SYMBOL = "XAUUSD"
URL = "https://datafeed.dukascopy.com/datafeed/{sym}/{y:04d}/{m0:02d}/{d:02d}/{h:02d}h_ticks.bi5"
UTC = dt.timezone.utc

# Inclusive UTC hour range. Derived from the Melbourne boundaries in build.py;
# both map onto whole UTC hours because every Australian offset is a whole hour.
# HOLDOUT YEAR. Exactly the twelve months preceding the audited sample, so the
# strategy specification frozen on 2026-08-22 has never been exposed to any of
# it -- not by this auditor and not by the submitting researcher.
START_HOUR = dt.datetime(2024, 8, 20, 14, tzinfo=UTC)
END_HOUR = dt.datetime(2025, 8, 20, 13, tzinfo=UTC)

MAX_ATTEMPTS = 6
BACKOFF = [2, 4, 8, 16, 32]

_lock = threading.Lock()
_throttle_until = 0.0


def hours():
    t, out = START_HOUR, []
    while t <= END_HOUR:
        out.append(t)
        t += dt.timedelta(hours=1)
    return out


def url_for(t):
    return URL.format(sym=SYMBOL, y=t.year, m0=t.month - 1, d=t.day, h=t.hour)


def raw_path(t):
    return os.path.join(RAW, f"{t:%Y}", f"{t:%m}", f"{t:%d}", f"{t:%H}h_ticks.bi5")


def decode(blob):
    """-> (n_ticks, first_ms, last_ms). Raises on a malformed stream."""
    out = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE).decompress(blob)
    if len(out) % 20:
        raise ValueError(f"decompressed {len(out)} bytes, not a multiple of 20")
    n = len(out) // 20
    if n == 0:
        return 0, None, None
    first = struct.unpack_from(">I", out, 0)[0]
    last = struct.unpack_from(">I", out, (n - 1) * 20)[0]
    return n, first, last


def load_checkpoint():
    done = {}
    if not os.path.exists(CHECKPOINT):
        return done
    with open(CHECKPOINT) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue  # torn final line from a killed process
            done[r["hour_utc"]] = r
    return done


def write_checkpoint(rec):
    with _lock:
        with open(CHECKPOINT, "a") as f:
            f.write(json.dumps(rec) + "\n")
            f.flush()
            os.fsync(f.fileno())


def fetch_hour(t, session):
    """One hour. Retries with backoff; never raises."""
    global _throttle_until
    u = url_for(t)
    rec = {"hour_utc": t.isoformat(), "url": u, "retries": 0, "errors": []}
    for attempt in range(MAX_ATTEMPTS):
        wait = _throttle_until - time.time()
        if wait > 0:
            time.sleep(wait)
        try:
            r = session.get(u, timeout=90)
            if r.status_code == 200:
                blob = r.content
                if len(blob) == 0:
                    rec.update(status="empty", bytes=0, ticks=0, sha256=None,
                               first_ms=None, last_ms=None)
                    return rec
                n, first, last = decode(blob)          # validate before persisting
                p = raw_path(t)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                tmp = p + ".part"
                with open(tmp, "wb") as f:
                    f.write(blob)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, p)                      # atomic: no half files
                rec.update(status="ok", bytes=len(blob), ticks=n,
                           sha256=hashlib.sha256(blob).hexdigest(),
                           first_ms=first, last_ms=last)
                return rec
            if r.status_code == 404:
                rec.update(status="missing_404", bytes=0, ticks=0, sha256=None,
                           first_ms=None, last_ms=None)
                return rec
            if r.status_code in (429, 503, 502, 500):
                # Brief GLOBAL cool-off only. It pauses every worker, so a long
                # value converts one 503 into (workers x seconds) of lost
                # throughput -- at 30s and 16 workers this collapsed the run from
                # 12 hours/sec to 0.4. The real spacing comes from each worker's
                # own BACKOFF ladder, which staggers retries instead of
                # synchronising them.
                with _lock:
                    _throttle_until = max(_throttle_until, time.time() + 4)
            rec["errors"].append(f"HTTP {r.status_code}")
        except Exception as e:
            rec["errors"].append(f"{type(e).__name__}: {e}")
        rec["retries"] = attempt + 1
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(BACKOFF[attempt] + random.uniform(0, 1.5))
    rec.update(status="error", bytes=0, ticks=0, sha256=None, first_ms=None, last_ms=None)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--retry-errors", action="store_true",
                    help="also re-request hours previously recorded as error")
    a = ap.parse_args()

    os.makedirs(LOGS, exist_ok=True)
    os.makedirs(RAW, exist_ok=True)
    done = load_checkpoint()
    all_hours = hours()

    todo = []
    for t in all_hours:
        k = t.isoformat()
        r = done.get(k)
        if r is None:
            todo.append(t)
        elif r["status"] == "error" and a.retry_errors:
            todo.append(t)
        elif r["status"] == "ok" and not os.path.exists(raw_path(t)):
            todo.append(t)          # checkpointed but the file is gone

    print(f"hours in range   : {len(all_hours)}", flush=True)
    print(f"already resolved : {len(all_hours) - len(todo)}", flush=True)
    print(f"to fetch         : {len(todo)}", flush=True)
    if not todo:
        print("nothing to do")
        return

    t0 = time.time()
    n_done = n_ok = n_empty = n_err = 0
    ticks = 0
    session_local = threading.local()

    def worker(t):
        s = getattr(session_local, "s", None)
        if s is None:
            s = requests.Session()
            s.headers.update({"User-Agent": "Mozilla/5.0 (research tick archival)"})
            session_local.s = s
        rec = fetch_hour(t, s)
        write_checkpoint(rec)
        return rec

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(worker, t) for t in todo]
        for fu in as_completed(futs):
            rec = fu.result()
            n_done += 1
            st = rec["status"]
            n_ok += st == "ok"
            n_empty += st == "empty"
            n_err += st in ("error", "missing_404")
            ticks += rec.get("ticks") or 0
            if n_done % 200 == 0 or n_done == len(todo):
                el = time.time() - t0
                rate = n_done / el if el else 0
                eta = (len(todo) - n_done) / rate if rate else 0
                print(f"[{n_done}/{len(todo)}] ok={n_ok} empty={n_empty} err={n_err} "
                      f"ticks={ticks:,} {rate:.1f} hr/s eta={eta/60:.1f}m", flush=True)

    print(f"\nDONE in {(time.time()-t0)/60:.1f} min  ok={n_ok} empty={n_empty} err={n_err} ticks={ticks:,}")
    if n_err:
        print(f"WARNING: {n_err} hours unresolved — rerun with --retry-errors")
        sys.exit(2)


if __name__ == "__main__":
    main()
