"""
Build the AU200 1-minute and 5-minute Melbourne-aligned datasets.
Reads raw dukascopy CSV files, combines, converts UTC→Melbourne, resamples.
"""

import os, glob, warnings
import pandas as pd
import numpy as np
import pytz
from pathlib import Path

warnings.filterwarnings('ignore')

RAW_DIR   = Path("/home/user/Trade_Cartel/research/au200_10am/data/raw")
PROC_DIR  = Path("/home/user/Trade_Cartel/research/au200_10am/data/processed")
LOG_DIR   = Path("/home/user/Trade_Cartel/research/au200_10am/logs")

PROC_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

TZ_MEL = pytz.timezone("Australia/Melbourne")
TZ_UTC = pytz.utc


def load_raw_csvs() -> pd.DataFrame:
    """Load and combine all raw CSV files."""
    files = sorted(RAW_DIR.glob("ausidxaud_m1_*.csv"))
    print(f"Found {len(files)} raw CSV files")

    chunks = []
    for fp in files:
        df = pd.read_csv(fp)
        if df.empty or 'timestamp_ms' not in df.columns:
            continue
        # Filter out empty/invalid rows
        df = df.dropna(subset=['open','high','low','close'])
        df = df[df['open'] > 0]
        chunks.append(df)
        print(f"  {fp.name}: {len(df):,} rows, price range [{df['close'].min():.0f}-{df['close'].max():.0f}]")

    if not chunks:
        raise ValueError("No valid CSV data found!")

    all_data = pd.concat(chunks, ignore_index=True)
    print(f"\nTotal raw rows: {len(all_data):,}")
    return all_data


def build_1m_utc(raw: pd.DataFrame) -> pd.DataFrame:
    """Build clean 1-minute UTC-indexed DataFrame."""
    raw = raw.copy()

    # Convert timestamp_ms to UTC datetime
    raw['dt_utc'] = pd.to_datetime(raw['timestamp_ms'], unit='ms', utc=True)
    raw = raw.set_index('dt_utc').sort_index()

    # Remove duplicates (keep last)
    raw = raw[~raw.index.duplicated(keep='last')]

    # Check OHLC integrity
    bad_ohlc = ((raw['high'] < raw['open']) | (raw['high'] < raw['close']) |
                (raw['low']  > raw['open']) | (raw['low']  > raw['close']))
    if bad_ohlc.any():
        print(f"  Warning: {bad_ohlc.sum()} rows with bad OHLC — fixing")
        # Fix: adjust high/low to be valid
        raw.loc[bad_ohlc, 'high'] = raw.loc[bad_ohlc, ['open','high','low','close']].max(axis=1)
        raw.loc[bad_ohlc, 'low']  = raw.loc[bad_ohlc, ['open','high','low','close']].min(axis=1)

    # Check for zero/negative prices
    zero_price = (raw['close'] <= 0) | (raw['open'] <= 0)
    if zero_price.any():
        print(f"  Warning: {zero_price.sum()} rows with zero/negative prices — dropping")
        raw = raw[~zero_price]

    # Check for implausible prices (outside 3000-15000 range for AU200)
    out_range = (raw['close'] < 3000) | (raw['close'] > 15000)
    if out_range.any():
        print(f"  Warning: {out_range.sum()} rows with out-of-range AU200 prices — dropping")
        raw = raw[~out_range]

    cols = ['open','high','low','close','volume']
    return raw[cols].copy()


def build_1m_melbourne(df_utc: pd.DataFrame) -> pd.DataFrame:
    """Convert UTC 1-minute data to Melbourne timezone."""
    # Convert timezone
    df_mel = df_utc.copy()
    df_mel.index = df_mel.index.tz_convert(TZ_MEL)
    df_mel.index.name = 'dt_mel'
    return df_mel


def build_5m_melbourne(df_1m_mel: pd.DataFrame) -> pd.DataFrame:
    """
    Build Melbourne-aligned 5-minute OHLCV bars.

    KEY: Must align to Melbourne midnight so that 09:50, 10:00 are bar timestamps.
    Python's resample('5min') with a UTC-based index will not give Melbourne alignment.
    We align to Melbourne midnight explicitly.
    """
    df = df_1m_mel.copy()

    # The index is already in Melbourne time.
    # pd.Grouper with freq='5T' and label='left', closed='left' will use
    # whatever offset the index is in. Since we're in Melbourne TZ,
    # this gives Melbourne-aligned bars naturally.

    resampled = df.resample('5min', label='left', closed='left').agg(
        open=('open', 'first'),
        high=('high', 'max'),
        low=('low', 'min'),
        close=('close', 'last'),
        volume=('volume', 'sum'),
        n_bars=('close', 'count'),
    ).dropna(subset=['open','close'])

    # Only keep bars with at least 1 underlying 1-minute bar
    resampled = resampled[resampled['n_bars'] > 0]

    # Verify 09:50 and 10:00 alignment
    sample = resampled[resampled.index.time == pd.Timestamp('09:50').time()]
    print(f"  Sample 09:50 bars: {len(sample)} (first few times: {sample.index[:3].tolist()})")
    sample2 = resampled[resampled.index.time == pd.Timestamp('10:00').time()]
    print(f"  Sample 10:00 bars: {len(sample2)}")

    return resampled


def audit_dataset(df_1m: pd.DataFrame, df_5m: pd.DataFrame):
    """Generate data audit report."""
    print("\n" + "="*60)
    print("DATA AUDIT REPORT")
    print("="*60)

    print(f"\nInstrument:       AUSIDXAUD (Dukascopy AU200 CFD)")
    print(f"Source:           dukascopy-node m1 timeframe")
    print(f"Data start (UTC): {df_1m.index[0]}")
    print(f"Data end   (UTC): {df_1m.index[-1]}")
    print(f"1-minute bars:    {len(df_1m):,}")
    print(f"5-minute bars:    {len(df_5m):,}")

    # Price range
    print(f"\nPrice range:      {df_1m['low'].min():.1f} – {df_1m['high'].max():.1f}")
    print(f"Typical mid:      {df_1m['close'].mean():.0f}")

    # Timezone info
    print(f"\nTimezone raw:     UTC")
    print(f"Melbourne TZ:     Australia/Melbourne (AEST/AEDT with proper DST)")
    print(f"DST handling:     pytz with tz_convert (not fixed offset)")

    # Melbourne trading day analysis
    mel_index = df_5m.index
    mel_dates = mel_index.normalize()  # Melbourne date component
    unique_dates = mel_dates.unique()
    print(f"\nUnique Melbourne dates: {len(unique_dates)}")

    # Count sessions with 09:50 and 10:00 bars
    has_0950 = df_5m[df_5m.index.time == pd.Timestamp('09:50').time()].index.normalize().unique()
    has_1000 = df_5m[df_5m.index.time == pd.Timestamp('10:00').time()].index.normalize().unique()
    has_both = has_0950.intersection(has_1000)

    print(f"Sessions with 09:50 bar: {len(has_0950)} ({100*len(has_0950)/len(unique_dates):.1f}%)")
    print(f"Sessions with 10:00 bar: {len(has_1000)} ({100*len(has_1000)/len(unique_dates):.1f}%)")
    print(f"Sessions with BOTH:      {len(has_both)} ({100*len(has_both)/len(unique_dates):.1f}%)")

    # Duplicates
    dups = df_1m.index.duplicated().sum()
    print(f"\nDuplicate timestamps:    {dups}")

    # Missing 1-minute bars within trading hours (rough check)
    # Expected: roughly 252 days × ~400 mins = ~100,800 bars/year

    # Year-by-year breakdown
    print("\n--- Year-by-Year 5-minute bar counts ---")
    by_year = df_5m.groupby(df_5m.index.year)
    for yr, grp in by_year:
        n_days = grp.index.normalize().nunique()
        n_0950 = (grp.index.time == pd.Timestamp('09:50').time()).sum()
        n_1000 = (grp.index.time == pd.Timestamp('10:00').time()).sum()
        print(f"  {yr}: {len(grp):6,} bars, {n_days:3} days, {n_0950:3} 09:50 bars, {n_1000:3} 10:00 bars")

    # Large price gaps
    closes = df_1m['close']
    gaps = (closes.pct_change().abs() * 100).dropna()
    big_gaps = gaps[gaps > 1.0]
    print(f"\nLarge price gaps (>1%): {len(big_gaps)}")
    if len(big_gaps) > 0:
        print(f"  Top 5 gaps:")
        for ts, val in big_gaps.nlargest(5).items():
            print(f"    {ts}: {val:.2f}%")

    # Candle timestamp convention
    print(f"\nCandle timestamp convention: LEFT (bar opens at labeled timestamp)")
    print(f"  e.g., 09:50 bar covers 09:50:00–09:54:59 Melbourne time")
    print(f"  e.g., 10:00 bar covers 10:00:00–10:04:59 Melbourne time")

    print("\n" + "="*60)


def main():
    print("=== Building AU200 Dataset ===\n")

    # Load raw
    raw = load_raw_csvs()

    # Build 1-minute UTC
    print("\nBuilding 1-minute UTC series...")
    df_1m_utc = build_1m_utc(raw)
    print(f"  1-minute UTC bars: {len(df_1m_utc):,}")

    # Save 1-minute UTC
    out1m_utc = PROC_DIR / "au200_1m_utc.csv.gz"
    df_1m_utc.to_csv(out1m_utc, compression='gzip')
    print(f"  Saved: {out1m_utc}")

    # Convert to Melbourne
    print("\nConverting to Melbourne timezone...")
    df_1m_mel = build_1m_melbourne(df_1m_utc)
    print(f"  1-minute Melbourne bars: {len(df_1m_mel):,}")

    # Save 1-minute Melbourne
    out1m_mel = PROC_DIR / "au200_1m_melbourne.csv.gz"
    df_1m_mel.to_csv(out1m_mel, compression='gzip')
    print(f"  Saved: {out1m_mel}")

    # Build 5-minute Melbourne
    print("\nBuilding 5-minute Melbourne bars...")
    df_5m_mel = build_5m_melbourne(df_1m_mel)
    print(f"  5-minute Melbourne bars: {len(df_5m_mel):,}")

    # Save 5-minute Melbourne
    out5m = PROC_DIR / "au200_5m_melbourne.csv.gz"
    df_5m_mel.to_csv(out5m, compression='gzip')
    print(f"  Saved: {out5m}")

    # Data audit
    audit_dataset(df_1m_mel, df_5m_mel)

    print("\nDataset build complete!")
    return df_1m_mel, df_5m_mel


if __name__ == "__main__":
    df_1m, df_5m = main()
