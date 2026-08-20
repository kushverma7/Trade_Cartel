"""
Dukascopy AU200 (AUSIDXAUD) historical tick downloader.
Downloads per-hour BI5 files, aggregates to 1-minute OHLCV, saves manifest.

URL format: https://datafeed.dukascopy.com/datafeed/AUSIDXAUD/{YYYY}/{MM}/{DD}/{HH}h_ticks.bi5
  - YYYY: 4-digit year
  - MM: 0-indexed month (Jan=00, Feb=01, ..., Dec=11)
  - DD: 2-digit day
  - HH: 2-digit hour (UTC)
  - Prices: uint32 / 1000 = index points

Tick record (big-endian, 20 bytes):
  uint32  ms_offset_in_hour
  uint32  ask_price * 1000
  uint32  bid_price * 1000
  float32 ask_volume
  float32 bid_volume

Timezone: raw timestamps are UTC. We convert to Australia/Melbourne.
"""

import os, sys, struct, lzma, time, json, logging, csv
import datetime as dt
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import pandas as pd
import numpy as np
import pytz

# ── Config ─────────────────────────────────────────────────────────────
SYM          = "AUSIDXAUD"
PRICE_DIV    = 1000.0
PRICE_MULT   = 1.0          # bid mid = (ask+bid)/2
RAW_DIR      = Path("/home/user/Trade_Cartel/research/au200_10am/data/raw")
PROCESSED_DIR= Path("/home/user/Trade_Cartel/research/au200_10am/data/processed")
LOG_DIR      = Path("/home/user/Trade_Cartel/research/au200_10am/logs")
MANIFEST_CSV = LOG_DIR / "download_manifest.csv"

# Date range (inclusive)
START_DATE = dt.date(2013, 1, 2)
END_DATE   = dt.date(2026, 8, 19)

# Melbourne DST-aware timezone
TZ_MEL = pytz.timezone("Australia/Melbourne")
TZ_UTC = pytz.utc

# For strategy we need Melbourne 09:30-23:30 which in UTC is:
# AEDT (UTC+11): 22:30 prev day - 12:30 current day
# AEST (UTC+10): 23:30 prev day - 13:30 current day
# Download UTC hours 21-14 next day to cover everything safely
# That means for each Melbourne date, we need UTC hours 21-14 (previous UTC day hours 21-23, current 0-14)

WORKERS      = 4          # concurrent download threads
RETRY_MAX    = 5
BASE_DELAY   = 2.0        # seconds between per-worker requests
BACKOFF_BASE = 2.0

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
    "Referer":    "https://www.dukascopy.com/",
    "Accept":     "*/*",
}
VERIFY_SSL = "/root/.ccr/ca-bundle.crt"

# ── Logging ────────────────────────────────────────────────────────────
LOG_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "download.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("dl")


# ── URL helpers ────────────────────────────────────────────────────────
def duka_url(utc_date: dt.date, hour: int) -> str:
    mm = utc_date.month - 1  # 0-indexed
    return (
        f"https://datafeed.dukascopy.com/datafeed/{SYM}/"
        f"{utc_date.year}/{mm:02d}/{utc_date.day:02d}/{hour:02d}h_ticks.bi5"
    )


def raw_path(utc_date: dt.date, hour: int) -> Path:
    return RAW_DIR / f"{utc_date.isoformat()}_{hour:02d}h.bi5"


# ── Manifest ──────────────────────────────────────────────────────────
def load_manifest() -> dict:
    """Return {(date_iso, hour): status} from manifest CSV."""
    m = {}
    if MANIFEST_CSV.exists():
        with open(MANIFEST_CSV) as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["date"], int(row["hour"]))
                m[key] = row["status"]
    return m


def save_manifest_row(date_iso: str, hour: int, status: str, ticks: int, retries: int):
    exists = MANIFEST_CSV.exists()
    with open(MANIFEST_CSV, "a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["date", "hour", "status", "ticks", "retries", "ts"])
        w.writerow([date_iso, hour, status, ticks, retries, dt.datetime.utcnow().isoformat()])


# ── Downloader ────────────────────────────────────────────────────────
def download_hour(utc_date: dt.date, hour: int) -> tuple:
    """Download one hour file. Returns (status, tick_count, retries)."""
    url  = duka_url(utc_date, hour)
    path = raw_path(utc_date, hour)
    retries = 0

    if path.exists() and path.stat().st_size > 0:
        # Already downloaded; count ticks from file size
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
            data = lzma.decompress(raw)
            return "cached", len(data) // 20, 0
        except Exception:
            path.unlink(missing_ok=True)  # corrupt — redownload

    delay = BASE_DELAY
    for attempt in range(RETRY_MAX):
        retries = attempt
        try:
            r = requests.get(url, headers=HEADERS, timeout=30, verify=VERIFY_SSL)
            if r.status_code == 200:
                if len(r.content) < 10:
                    # Valid empty file (no ticks this hour)
                    return "empty", 0, retries
                data = lzma.decompress(r.content)
                n_ticks = len(data) // 20
                with open(path, "wb") as fh:
                    fh.write(r.content)
                return "ok", n_ticks, retries
            elif r.status_code in (404,):
                return "missing", 0, retries
            elif r.status_code in (429, 503, 502, 500):
                log.warning(f"HTTP {r.status_code} for {url} — retry {attempt+1}")
                time.sleep(delay)
                delay = min(delay * BACKOFF_BASE, 120.0)
            else:
                return f"http_{r.status_code}", 0, retries
        except requests.exceptions.Timeout:
            log.warning(f"Timeout for {url} — retry {attempt+1}")
            time.sleep(delay)
            delay = min(delay * BACKOFF_BASE, 120.0)
        except Exception as e:
            log.warning(f"Error for {url}: {e} — retry {attempt+1}")
            time.sleep(delay)
            delay = min(delay * BACKOFF_BASE, 60.0)

    return "failed", 0, retries


# ── Work item generator ───────────────────────────────────────────────
def generate_work_items(manifest: dict) -> list:
    """
    Generate (utc_date, hour) tuples to download.
    For each Melbourne calendar date we need UTC hours 21-14 (next UTC day).
    We skip weekends (Melbourne Sat/Sun) since AU200 doesn't trade then.
    """
    items = []
    mel_date = START_DATE
    one_day  = dt.timedelta(days=1)

    while mel_date <= END_DATE:
        # Skip Melbourne weekends
        # Convert Melbourne midnight to UTC to check weekday accurately
        mel_midnight = TZ_MEL.localize(dt.datetime(mel_date.year, mel_date.month, mel_date.day, 0, 0, 0))
        if mel_midnight.weekday() >= 5:  # 5=Sat, 6=Sun
            mel_date += one_day
            continue

        # UTC hours needed for this Melbourne date:
        # Melbourne 09:00 in UTC:
        #   AEDT (UTC+11): prior day 22:00 UTC
        #   AEST (UTC+10): prior day 23:00 UTC
        # Melbourne 23:00 in UTC:
        #   AEDT: 12:00 UTC same day
        #   AEST: 13:00 UTC same day
        # To be safe: prior UTC day hours 21-23 + current UTC day hours 00-14

        utc_date_prev = mel_date - one_day
        utc_date_curr = mel_date

        for hour in range(21, 24):  # prev UTC day: 21, 22, 23
            key = (utc_date_prev.isoformat(), hour)
            if manifest.get(key) not in ("ok", "empty", "missing", "cached"):
                items.append((utc_date_prev, hour))

        for hour in range(0, 15):   # current UTC day: 00-14
            key = (utc_date_curr.isoformat(), hour)
            if manifest.get(key) not in ("ok", "empty", "missing", "cached"):
                items.append((utc_date_curr, hour))

        mel_date += one_day

    return items


# ── Tick parser ───────────────────────────────────────────────────────
def parse_bi5(utc_date: dt.date, hour: int) -> pd.DataFrame:
    """Parse one hour BI5 file into a DataFrame of ticks."""
    path = raw_path(utc_date, hour)
    if not path.exists():
        return pd.DataFrame()
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        if len(raw) < 10:
            return pd.DataFrame()
        data = lzma.decompress(raw)
    except Exception:
        return pd.DataFrame()

    n = len(data) // 20
    if n == 0:
        return pd.DataFrame()

    arr = np.frombuffer(data[:n * 20], dtype=">u4,>u4,>u4,>f4,>f4")
    ms_offsets = arr["f0"].astype(np.int64)
    ask_price  = arr["f1"] / PRICE_DIV
    bid_price  = arr["f2"] / PRICE_DIV

    # Reconstruct UTC timestamp
    hour_start_ms = int(
        dt.datetime(utc_date.year, utc_date.month, utc_date.day, hour, 0, 0,
                    tzinfo=TZ_UTC).timestamp() * 1000
    )
    ts_ms = hour_start_ms + ms_offsets
    mid   = (ask_price + bid_price) / 2.0

    return pd.DataFrame({
        "ts_utc_ms": ts_ms,
        "ask": ask_price,
        "bid": bid_price,
        "mid": mid,
    })


# ── 1-minute aggregation ──────────────────────────────────────────────
def ticks_to_1m(ticks: pd.DataFrame) -> pd.DataFrame:
    """Aggregate tick DataFrame to 1-minute OHLCV."""
    if ticks.empty:
        return pd.DataFrame()

    ticks = ticks.copy()
    ticks["ts_utc"] = pd.to_datetime(ticks["ts_utc_ms"], unit="ms", utc=True)
    ticks = ticks.set_index("ts_utc").sort_index()
    # Use bid mid for price (typical for indices)
    price = ticks["mid"]

    ohlcv = price.resample("1min").agg(
        open="first", high="max", low="min", close="last"
    ).dropna()
    ohlcv["volume"] = ticks["mid"].resample("1min").count()
    return ohlcv


# ── Main download loop ────────────────────────────────────────────────
def run_download():
    log.info(f"=== AUSIDXAUD Downloader Start: {START_DATE} → {END_DATE} ===")
    manifest = load_manifest()
    items    = generate_work_items(manifest)
    log.info(f"Work items to download: {len(items)}")

    completed = 0
    errors    = 0

    def worker(item):
        utc_date, hour = item
        status, ticks, retries = download_hour(utc_date, hour)
        save_manifest_row(utc_date.isoformat(), hour, status, ticks, retries)
        time.sleep(BASE_DELAY)  # polite rate limit per worker
        return utc_date, hour, status, ticks

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(worker, item): item for item in items}
        for i, fut in enumerate(as_completed(futs), 1):
            utc_date, hour, status, ticks = fut.result()
            if status in ("ok", "cached"):
                completed += 1
            elif status in ("failed",):
                errors += 1
            if i % 100 == 0:
                log.info(f"Progress: {i}/{len(items)} | ok={completed} | err={errors}")

    log.info(f"Download complete: {completed} ok, {errors} failed out of {len(items)}")


# ── Build 1-minute CSV ────────────────────────────────────────────────
def build_1m_dataset():
    """Parse all downloaded BI5 files and write a 1-minute OHLCV CSV.gz"""
    log.info("Building 1-minute dataset from raw BI5 files...")
    manifest = load_manifest()

    # Collect all valid (date, hour) entries
    entries = []
    for (date_iso, hour), status in manifest.items():
        if status in ("ok", "cached"):
            entries.append((dt.date.fromisoformat(date_iso), int(hour)))
    entries.sort()
    log.info(f"Files to parse: {len(entries)}")

    chunks = []
    for utc_date, hour in entries:
        df = parse_bi5(utc_date, hour)
        if not df.empty:
            chunks.append(df)

    if not chunks:
        log.error("No tick data found!")
        return

    all_ticks = pd.concat(chunks)
    all_ticks = all_ticks.sort_values("ts_utc_ms").drop_duplicates("ts_utc_ms")
    log.info(f"Total ticks: {len(all_ticks):,}")

    m1 = ticks_to_1m(all_ticks)
    log.info(f"1-minute bars: {len(m1):,}")

    out_path = PROCESSED_DIR / "au200_1m_utc.csv.gz"
    m1.to_csv(out_path, compression="gzip")
    log.info(f"Saved: {out_path}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-only", action="store_true", help="Skip download, build from existing raw files")
    args = ap.parse_args()

    if not args.build_only:
        run_download()
    build_1m_dataset()
