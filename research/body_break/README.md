# 10 AM Body Break — Phase 1 result: BLOCKED ON DATA

Phase 1 of the spec is data validation, with the instruction "do NOT continue
if signal generation does not match". It does not get that far: **neither
market can be tested as specified.** Nothing has been backtested.

## Gold — cannot be tested at all
The spec requires **5-minute candles only**. This repo holds
`data/xauusd_15m.csv.gz` — 157,366 rows, 2019-12-01 to 2026-07-30, modal bar
spacing **15 minutes**. There is no 5-minute gold data. A 15-minute series
cannot produce a 09:50 candle or a 10:00 candle, so every rule in the model is
undefined on it. Not "approximate" — undefined.

## AU200 — the 09:50 reference candle is almost entirely absent
`data/au200_5m.csv.gz`: 139,898 rows, 1,635 sessions, 2020-08-05 to 2026-08-04,
zero duplicate timestamps.

| | sessions | share |
|---|---|---|
| total | 1,635 | |
| with a 10:00 candle | 1,514 | 92.6% |
| **with a 09:50 candle** | **173** | **10.6%** |
| testable (both present) | 173 | 10.6% |

The spec is explicit: `DAILY_OPEN` is the OPEN of the 09:50 candle and must not
be substituted with the midnight open, session open, 10:00 open or previous
close. On 89.4% of sessions that candle does not exist in this data, so those
days are excluded and counted rather than silently filled.

**The 173 testable days are also not distributed usably:**

| year | testable sessions |
|---|---|
| 2023 | 2 |
| 2024 | 2 |
| 2025 | 21 |
| 2026 | 148 |

86% of the sample is 2026. The spec's minimum is 3 years and its stated
preference is 5+; year-by-year validation, monthly seasonality, the 70/30
out-of-sample split and drawdown-across-regimes are all impossible on this.
Sides break down ABOVE 70 / BELOW 52 / STRADDLE 51, so Logic A applies to about
122 days in total — before any flip, exit or subgroup analysis divides it
further.

## Why 09:50 is missing
09:50 Melbourne is the ASX **pre-open auction**, not continuous trading. The
OANDA AU200AUD export used here only prints a bar there when the CFD feed
happens to quote during the auction. Your TradingView chart evidently shows it
far more often than this export does, which is itself a discrepancy worth
resolving before trusting any reproduction.

## What was still produced
- `strategy.py` — the exact rules: 09:50 open as DAILY_OPEN with no
  substitution, body from `max/min(open, close)`, Logic A first-close-beyond
  with one signal per day and a 16:00 cutoff, Logic B, one flip per day, and
  the three C3 confirmations (A two consecutive closes, B next candle in the
  flip direction, C break of the flip candle's extreme).
- `data_validation.py` — the coverage audit above plus the ten-day table.

The ten-day validation table is printed and ready to check against TradingView.
Run `python3 research/body_break/data_validation.py`. If those rows match your
indicator, signal generation is correct and only the data is the problem.

## What is needed to proceed
1. **XAUUSD 5-minute**, 5+ years.
2. **AU200 5-minute including the 09:50 pre-open bar**, 5+ years — or
   confirmation that your feed carries it, in which case export from there.

London Strategic Edge is the obvious source for both: its documented categories
include commodities and indices, and `client.candles(symbol, "5m", start=...)`
supplies exactly this shape. Two environmental blockers remain — `LSE_API_KEY`
is not set in this container, and `api.londonstrategicedge.com` returns 403 at
the egress proxy. Clearing those unblocks this project.

## What was NOT done, deliberately
No backtest, no MFE/MAE tables, no flip analysis, no exit study, no rankings.
Running them on 173 days weighted 86% into one year would produce numbers that
look like answers and are not. That is the failure this repo already recorded
as BUG-039, where a result built on an unrepresentative subset survived a
3,640-cell sweep and then died in live trading.
