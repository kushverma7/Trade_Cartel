"""Build NY-time tick arrays and 1-minute NY bars from the MASTER parquet.

Provenance note that drives this whole audit: the arrays used by the earlier
10AM work (research/gold_10am_flip/data/tk_*.npy) hold 52,223,814 ticks and are
TRUNCATED to Melbourne hours 09:00-23:59 -- hours 00-08 are empty. The master
parquet holds all 91,629,949. Since 18:45 New York is 08:45 Melbourne for the
half of the year when Melbourne is on AEST and New York on EDT, an anchor built
from those arrays silently loses that half of the sample. This script therefore
reads the master file.

Timezone handling: the parquet carries a genuinely tz-aware UTC column, so the
conversion to America/New_York is a single tz_convert and never touches the
naive Melbourne column (BUG-045). DST is handled by the tz database.
"""
import numpy as np, pyarrow.parquet as pq, pandas as pd, os

SRC = "research/gold_tick_data/dukascopy/processed/GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20.parquet"
OUT = "research/microq3/data"
os.makedirs(OUT, exist_ok=True)

f = pq.ParquetFile(SRC)
N = f.metadata.num_rows
ny_ms = np.empty(N, np.int64)
bid_i = np.empty(N, np.int32)      # price * 1000, exact integer from the feed
ask_i = np.empty(N, np.int32)
pos = 0
for b in f.iter_batches(batch_size=2_000_000, columns=["timestamp_utc", "bid", "ask"]):
    ts = b.column("timestamp_utc").to_numpy(zero_copy_only=False)   # datetime64[ms] UTC
    idx = pd.DatetimeIndex(ts).tz_localize("UTC").tz_convert("America/New_York")
    # NY WALL CLOCK as epoch-ms (naive), used only for bucketing into NY calendar bars
    wall = idx.tz_localize(None).values.astype("datetime64[ms]").astype(np.int64)
    n = len(wall)
    ny_ms[pos:pos + n] = wall
    bid_i[pos:pos + n] = np.rint(b.column("bid").to_numpy(zero_copy_only=False) * 1000).astype(np.int32)
    ask_i[pos:pos + n] = np.rint(b.column("ask").to_numpy(zero_copy_only=False) * 1000).astype(np.int32)
    pos += n
assert pos == N, (pos, N)
print(f"ticks: {N:,}")
print(f"NY wall clock: {pd.Timestamp(ny_ms[0], unit='ms')} -> {pd.Timestamp(ny_ms[-1], unit='ms')}")

# The NY wall clock runs backwards across the Nov DST fall-back (01:00-02:00 repeats).
# True UTC order is what execution must follow, so keep the arrays in UTC order and
# carry the NY wall clock purely as a LABEL for bucketing.
d = np.diff(ny_ms)
back = int((d < 0).sum())
print(f"NY wall-clock non-monotonic steps (expected at the Nov fall-back): {back}")
if back:
    k = int(np.argmin(d))
    print(f"   first at tick {k}: {pd.Timestamp(ny_ms[k],unit='ms')} -> {pd.Timestamp(ny_ms[k+1],unit='ms')}")

np.save(f"{OUT}/ny_ms.npy", ny_ms)
np.save(f"{OUT}/bid_i.npy", bid_i)
np.save(f"{OUT}/ask_i.npy", ask_i)

# ---- 1-minute NY bars, from MID, BID and ASK, plus tick-index boundaries ----
minute = ny_ms // 60_000
# ticks are in UTC order; within a repeated NY hour two different real minutes share
# a label, so group on RUNS of equal label rather than on the label itself
newrun = np.empty(len(minute), bool); newrun[0] = True
np.not_equal(minute[1:], minute[:-1], out=newrun[1:])
starts = np.flatnonzero(newrun)
ends = np.append(starts[1:], len(minute))
lab = minute[starts]
mid_i = (bid_i.astype(np.int64) + ask_i.astype(np.int64)) // 2

def ohlc(arr):
    o = arr[starts]; c = arr[ends - 1]
    hi = np.maximum.reduceat(arr, starts); lo = np.minimum.reduceat(arr, starts)
    return o, hi, lo, c

bars = {"minute": lab, "i0": starts, "i1": ends, "n": ends - starts}
for nm, a in (("mid", mid_i), ("bid", bid_i.astype(np.int64)), ("ask", ask_i.astype(np.int64))):
    o, hi, lo, c = ohlc(a)
    bars[f"{nm}_o"], bars[f"{nm}_h"], bars[f"{nm}_l"], bars[f"{nm}_c"] = o, hi, lo, c
df = pd.DataFrame(bars)
df.to_parquet(f"{OUT}/bars_1m_ny.parquet", index=False)
print(f"1-minute NY bars: {len(df):,}  (runs, so a repeated DST hour stays two separate bars)")

# coverage of the anchor window, the thing the truncated arrays would have lost
mn = df.minute.to_numpy()
hhmm = (mn % 1440)
inwin = ((hhmm >= 18 * 60 + 45) & (hhmm < 19 * 60)).sum()
print(f"1-minute bars inside 18:45-19:00 NY: {inwin}  (15 x ~261 weekdays would be ~3,900)")
