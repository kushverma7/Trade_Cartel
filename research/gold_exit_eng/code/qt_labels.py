"""Map each verified 10AM trade onto its Quarterly-Theory phase in NEW YORK time.

Daye's cycle, as described: the daily cycle runs Q1 18:00-00:00, Q2 00:00-06:00,
Q3 06:00-12:00, Q4 12:00-18:00 New York. Each six-hour block splits into four
90-minute quarters, and each of those into four 22.5-minute micro quarters.

Labels are computed from the signal bar's actual instant, converted with
zoneinfo so US DST is handled, never a fixed offset. That matters here more than
usual: the whole claim under test is that Melbourne and New York changing DST on
different dates moves the 10:00 Melbourne candle between QT phases.
"""
import sys, datetime as dt, numpy as np, pandas as pd
from zoneinfo import ZoneInfo
sys.path.insert(0, "code")
NY = ZoneInfo("America/New_York")


MEL = ZoneInfo("Australia/Melbourne")


def qt(ts_ms):
    """-> (daily_q, q90, micro, ny_hhmm).

    ts_ms is the NAIVE MELBOURNE WALL CLOCK stored as epoch milliseconds -- the
    same convention as the dataset's timestamp_melbourne column. It is NOT a UTC
    instant. Reading it as one silently shifts every label by 10 or 11 hours and
    puts the trades in the wrong quarter entirely, which is exactly what the
    first run of this file did. Localise to Melbourne first, THEN convert to New
    York, so both DST calendars are applied in the right order."""
    naive = dt.datetime.fromtimestamp(ts_ms / 1000, dt.timezone.utc).replace(tzinfo=None)
    n = naive.replace(tzinfo=MEL).astimezone(NY)
    # minutes since 18:00 NY, wrapping the 24h cycle
    m = (n.hour * 60 + n.minute + n.second / 60) - 18 * 60
    if m < 0:
        m += 1440
    dq = int(m // 360) + 1                      # 6-hour quarter, 1..4
    within = m - (dq - 1) * 360
    q90 = int(within // 90) + 1                 # 90-minute quarter, 1..4
    within90 = within - (q90 - 1) * 90
    mic = int(within90 // 22.5) + 1             # 22.5-minute micro quarter, 1..4
    return dq, q90, mic, n.hour * 100 + n.minute
