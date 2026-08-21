==============================================================================
GOLD / XAUUSD  -  RAW TICK DATASET  -  DUKASCOPY  -  ONE YEAR
==============================================================================

SOURCE
    Dukascopy Bank SA historical tick feed (authentic BI5 hourly tick files)
    https://datafeed.dukascopy.com/datafeed/XAUUSD/{YYYY}/{MM0}/{DD}/{HH}h_ticks.bi5
    MM0 is Dukascopy's zero-indexed month: January=00 ... December=11.
    Downloaded straight from that feed. Not candles, not 1-minute bars, not
    another broker, not a vendor mirror, not a resampled product.

SYMBOL
    XAUUSD  (spot gold vs US dollar)

DATA TYPE
    Raw tick / quote data - every bid/ask update Dukascopy published.

REQUESTED MELBOURNE PERIOD
    2025-08-21 00:00:00.000
    to
    2026-08-20 23:59:59.999   (Australia/Melbourne)

UTC REQUEST BOUNDARIES
    2025-08-20 14:00:00.000 UTC   (Melbourne +1000 AEST)
    to
    2026-08-20 13:59:59.999 UTC   (Melbourne +1000 AEST)

    Computed with zoneinfo, not a fixed offset. The window spans BOTH
    Australian offsets, so a hard-coded UTC+10 would have been wrong for
    182 days of it. The two transitions inside the period:
        2025-10-05  02:00 -> 03:00 Melbourne   AEST +10:00 -> AEDT +11:00
        2026-04-05  03:00 -> 02:00 Melbourne   AEDT +11:00 -> AEST +10:00
    Both endpoints fall in AEST (+10). Every Australian offset is a whole
    number of hours, so both boundaries land exactly on a UTC hour. The
    boundary filter was still applied explicitly after assembling the whole
    hourly download, and is reported below.

TOTAL TICKS
    91,629,949

FIRST TICK UTC            2025-08-20T14:00:00.001Z
LAST TICK UTC             2026-08-20T13:59:59.926Z
FIRST TICK MELBOURNE      2025-08-21T00:00:00.001
LAST TICK MELBOURNE       2026-08-20T23:59:59.926

COLUMNS
    1  timestamp_utc        timestamp[ms, tz=UTC]  instant of the quote
    2  timestamp_melbourne  timestamp[ms]          Australia/Melbourne WALL CLOCK,
                                                   DST-correct (AEST+10 / AEDT+11).
                                                   Stored NAIVE deliberately so any
                                                   reader shows the literal local
                                                   time rather than re-rendering a
                                                   UTC instant.
    3  bid                  double                 bid price, USD/oz
    4  ask                  double                 ask price, USD/oz
    5  bid_volume           float                  Dukascopy native units
    6  ask_volume           float                  Dukascopy native units
    7  mid                  double                 (bid + ask) / 2   [derived]
    8  spread               double                 ask - bid         [derived]

TIMESTAMP PRECISION
    MILLISECOND - the native precision of the Dukascopy BI5 record, which
    stores a millisecond offset from the start of each hour. Nothing is
    rounded to seconds or minutes: 91,629,949 rows are stored at ms
    resolution and sub-second components are present throughout.

BID/ASK
    YES - both stored unmodified at full source precision. mid and spread
    are ADDED columns, never substitutes; bid and ask remain in the data.

VOLUME
    bid_volume, ask_volume  (both present on every tick)
    Dukascopy's own units - a retail aggregator's book, not exchange volume.

PARQUET COMPRESSION
    ZSTD (level 9), Parquet format version 2.6

FILE SIZE
    1,003,329,131 bytes   (956.85 MiB)

SHA256
    f5be07253e91d1112005294e5c0714b4b295c432b07044e0982ac4328635b96c

------------------------------------------------------------------------------
DATA QUALITY
------------------------------------------------------------------------------
DUPLICATE EXACT ROWS          0
DUPLICATE TIMESTAMPS          0
    Distinct quotes that share a millisecond. Dukascopy timestamps to the
    millisecond and gold updates faster than that, so these are legitimate
    separate quotes, NOT duplicates. They are retained.
BID > ASK                     0
INVALID PRICE ROWS            0
    (null bid, null ask, bid<=0, ask<=0, or bid>ask)
ZERO SPREAD                   0
NEGATIVE SPREAD               0
EXTREME SPREAD (> $5.00)      40,300
TIMESTAMPS OUT OF ORDER       0

Spread distribution (USD):
    min 0.001   p01 0.390   median 0.670   mean 0.740
    p99 2.200   p99.99 8.647   max 15.000
Price range: bid 3,321.045 .. 5,596.805    ask 3,321.815 .. 5,599.715

NOTHING WAS DELETED. No tick was dropped for being unusual. Wide spreads,
zero-volume quotes and repeated prices are retained exactly as delivered and
reported here so you can filter them yourself if your model needs to.

------------------------------------------------------------------------------
DOWNLOAD COMPLETENESS
------------------------------------------------------------------------------
HOURS REQUESTED               8,760   (every UTC hour in the window)
HOURS WITH TICKS              5,911
EMPTY HOURS                   2,849
UNRESOLVED DOWNLOAD HOURS     0
    Zero. Every one of the 8,760 requested hours was fetched and answered.
    HTTP retries across the whole run: 263

EMPTY HOURS: EXPECTED CLOSED MARKET vs UNEXPECTED MISSING DATA

    An empty hour is a real answer from Dukascopy, not a failure. Gold trades
    24x5 and is SHUT for most empty hours, so each one is classified against
    the actual session calendar in NEW YORK time - the clock the settlement
    break and the weekly open/close follow.

    EXPECTED CLOSED-MARKET EMPTY PERIODS   2,849
         1,248   Saturday - market closed
           936   Sunday before the 18:00 NY weekly reopen
           364   Friday after the 17:00 NY weekly close
           200   daily 17:00-18:00 NY settlement break
            18   Christmas Day
            18   New Year's Day
            17   Good Friday
            10   Christmas Eve (early close)
             7   New Year's Eve (early close)
             6   eve of holiday: Good Friday
             4   US Juneteenth (early close)
             4   US Independence Day observed (early close)
             3   US Labor Day (early close)
             3   US Thanksgiving (early close)
             3   US Martin Luther King Jr. Day (early close)
             3   US Presidents' Day (early close)
             3   US Memorial Day (early close)
             2   day after US Thanksgiving (early close)

    UNEXPECTED MISSING DATA                0
        None. Every empty hour is attributable to a scheduled closure.

------------------------------------------------------------------------------
DATA GAPS
------------------------------------------------------------------------------
Intervals between consecutive ticks longer than 5 minutes:  264
    maintenance        199
    weekend             48
    holiday             11
    UNEXPLAINED          6

    6 gap(s) are NOT attributable to a weekend, the daily
    maintenance break, or a listed holiday. They total
    51.3 MINUTES across the entire year, the longest being
    20.5 minutes. Every one falls in a known thin-liquidity
    window - the first half hour after the Sunday reopen, the minutes
    just after a daily reopen, or the Black Friday overnight session -
    so they read as the book going quiet rather than as feed outages.
    They are listed rather than absorbed into the closure rules:
             20.5 min   2025-12-07T23:15:39.489000+00:00  ->  2025-12-07T23:36:08.877000+00:00
              7.8 min   2026-02-12T23:01:15.635000+00:00  ->  2026-02-12T23:09:05.076000+00:00
              7.2 min   2025-11-28T08:14:31.549000+00:00  ->  2025-11-28T08:21:41.605000+00:00
              5.5 min   2025-12-07T23:36:08.877000+00:00  ->  2025-12-07T23:41:37.675000+00:00
              5.3 min   2025-11-28T08:06:26.193000+00:00  ->  2025-11-28T08:11:45.389000+00:00
              5.0 min   2025-12-07T23:09:40.462000+00:00  ->  2025-12-07T23:14:41.323000+00:00
    These are periods Dukascopy itself published no ticks for. They are
    reported, not patched: no value is interpolated anywhere in this file.

Longest gaps overall:
       4381.2 min  holiday      2026-04-02T20:58:58.311000+00:00 -> 2026-04-05T22:00:11.413000+00:00
       3181.1 min  holiday      2026-07-03T16:58:58.207000+00:00 -> 2026-07-05T22:00:01.514000+00:00
       3181.0 min  holiday      2026-06-19T16:58:59.181000+00:00 -> 2026-06-21T22:00:01.445000+00:00
       3076.0 min  holiday      2025-11-28T19:43:59.978000+00:00 -> 2025-11-30T23:00:01.135000+00:00
       3000.0 min  weekend      2025-10-31T20:59:58.982000+00:00 -> 2025-11-02T23:00:00.693000+00:00
       2946.6 min  weekend      2026-01-30T21:59:51.954000+00:00 -> 2026-02-01T23:06:26.655000+00:00
       2941.1 min  weekend      2026-07-24T20:59:01.103000+00:00 -> 2026-07-26T22:00:04.075000+00:00
       2941.0 min  weekend      2026-07-17T20:59:02.662000+00:00 -> 2026-07-19T22:00:03.067000+00:00
       2941.0 min  weekend      2026-08-14T20:59:01.732000+00:00 -> 2026-08-16T22:00:02.399000+00:00
       2941.0 min  weekend      2026-07-31T20:59:02.882000+00:00 -> 2026-08-02T22:00:01.623000+00:00

------------------------------------------------------------------------------
COVERAGE BREAKDOWN  (Australia/Melbourne calendar)
------------------------------------------------------------------------------
Days requested:  365
Days with data:  312
Days with none:  53   (weekends and holidays - itemised below)

Ticks per day with data:
    mean         293,686
    median       281,549
    min           24,535   (2026-07-04)
    max          817,963   (2026-01-30)

BY YEAR
    year              ticks   trading days
    2025         30,760,509            114
    2026         60,869,440            198

BY MONTH  (use this to spot a missing chunk at a glance)
    month                ticks   days    ticks/day
    2025-08          1,295,544      9      143,949
    2025-09          5,720,031     26      220,001
    2025-10          9,257,323     27      342,863
    2025-11          6,676,705     25      267,068
    2025-12          7,810,906     27      289,292
    2026-01          9,319,889     27      345,181
    2026-02          7,538,339     24      314,097
    2026-03          9,230,163     26      355,006
    2026-04          7,506,250     25      300,250
    2026-05          8,481,206     26      326,200
    2026-06          8,109,612     26      311,908
    2026-07          7,425,625     27      275,023
    2026-08          3,258,356     17      191,668

Days with no data at all, and why:
    2025-08-24   Sunday
    2025-08-31   Sunday
    2025-09-07   Sunday
    2025-09-14   Sunday
    2025-09-21   Sunday
    2025-09-28   Sunday
    2025-10-05   Sunday
    2025-10-12   Sunday
    2025-10-19   Sunday
    2025-10-26   Sunday
    2025-11-02   Sunday
    2025-11-09   Sunday
    2025-11-16   Sunday
    2025-11-23   Sunday
    2025-11-30   Sunday
    2025-12-07   Sunday
    2025-12-14   Sunday
    2025-12-21   Sunday
    2025-12-28   Sunday
    2026-01-04   Sunday
    2026-01-11   Sunday
    2026-01-18   Sunday
    2026-01-25   Sunday
    2026-02-01   Sunday
    2026-02-08   Sunday
    2026-02-15   Sunday
    2026-02-22   Sunday
    2026-03-01   Sunday
    2026-03-08   Sunday
    2026-03-15   Sunday
    2026-03-22   Sunday
    2026-03-29   Sunday
    2026-04-04   Saturday
    2026-04-05   Sunday
    2026-04-12   Sunday
    2026-04-19   Sunday
    2026-04-26   Sunday
    2026-05-03   Sunday
    2026-05-10   Sunday
    2026-05-17   Sunday
    2026-05-24   Sunday
    2026-05-31   Sunday
    2026-06-07   Sunday
    2026-06-14   Sunday
    2026-06-21   Sunday
    2026-06-28   Sunday
    2026-07-05   Sunday
    2026-07-12   Sunday
    2026-07-19   Sunday
    2026-07-26   Sunday
    2026-08-02   Sunday
    2026-08-09   Sunday
    2026-08-16   Sunday

------------------------------------------------------------------------------
VERIFICATION PERFORMED
------------------------------------------------------------------------------
The Parquet file was closed, then reopened by a SEPARATE process, which
confirmed:
     1. row count matches the Parquet footer
     2. first row matches the audit
     3. last row matches the audit
     4. timestamps are non-decreasing (source order preserved, never sorted)
     5. millisecond precision retained - not rounded to seconds or minutes
     6. bid present and non-null on every row
     7. ask present and non-null on every row
     8. mid == (bid+ask)/2 exactly after the round trip
     9. bid_volume and ask_volume present and non-null on every row
    10. no accidental downsampling - the row count equals the sum of the
        per-hour tick counts taken from the raw BI5 files
    11. every tick falls inside the requested Melbourne/UTC boundaries
    12. the file opens cleanly with pyarrow and pandas

    Plus the check that actually proves serialisation altered nothing: 40
    randomly chosen hours were re-decoded straight from the raw .bi5 files
    and compared row-for-row against the Parquet body - including that
    bid*1000 returns the source's original integer point value, which is
    what would fail first if float precision had been lost.

    RESULT: ALL CHECKS PASSED

------------------------------------------------------------------------------
HOW TO READ IT  (self-contained: no Dukascopy access, no API key, no
downloader, no repository and no special environment required)
------------------------------------------------------------------------------
    import pandas as pd
    df = pd.read_parquet('GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20.parquet')

    # lazily, if the whole year will not fit in memory:
    import pyarrow.parquet as pq
    pf = pq.ParquetFile('GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20.parquet')
    for batch in pf.iter_batches(batch_size=1_000_000):
        ...

    # or with DuckDB, no load at all:
    SELECT * FROM 'GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20.parquet'
    WHERE timestamp_melbourne >= TIMESTAMP '2026-01-01';

    Only a standard Parquet reader is needed. ZSTD is built into pyarrow,
    polars, duckdb, pandas and Spark.

------------------------------------------------------------------------------
PROVENANCE
------------------------------------------------------------------------------
    Raw source mirror: 359.95 MiB of untouched Dukascopy .bi5 bytes,
    exactly as served, kept at raw/YYYY/MM/DD/HHh_ticks.bi5.
    A SHA256 for every hourly file is in logs/manifest_by_hour.csv, and
    logs/manifest_by_day.csv is the per-day roll-up with status, tick counts,
    first/last timestamps, retry counts and errors. The mirror can therefore
    be re-verified byte-for-byte without re-downloading it.
    Built: 2026-08-21 03:15:46 UTC

------------------------------------------------------------------------------
NOTES AND CAVEATS
------------------------------------------------------------------------------
    * XAUUSD is OTC spot gold. There is no consolidated tape, so tick counts
      and spreads reflect DUKASCOPY's liquidity, not the whole market's.
      Another broker's tick stream for the same period will differ.
    * Volumes are Dukascopy's own units from a retail aggregator's book.
      Treat them as relative activity, not as exchange volume.
    * Gold halts daily for the NY 17:00-18:00 settlement break. Its Melbourne
      clock time moves with BOTH the US and Australian DST calendars, so it
      sits at 07:00-08:00, 08:00-09:00 or 09:00-10:00 Melbourne depending on
      the date. Do not assume one fixed local window.
    * Ticks are quote updates, not trades. A tick means the bid or ask moved.
==============================================================================
