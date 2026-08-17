# Data required to run this backtest

I have none of it. This repo contains AU200, US30 and XAUUSD only. There is no
NQ, no VIX and no equity data, and this container has no market-data access.
Nothing below has been run.

## 1. NQ price data — REQUIRED

One file per execution timeframe. Continuous back-adjusted futures preferred;
if you supply an unadjusted contract series, say so, because roll gaps create
false sweeps and I will need to filter roll dates.

| file | timeframe | minimum span |
|---|---|---|
| `nq_1m.csv`  | 1 minute  | 2 years (5 preferred) |
| `nq_5m.csv`  | 5 minute  | 5 years |
| `nq_15m.csv` | 15 minute | 5 years |
| `nq_30m.csv` | 30 minute | 5 years |

Higher timeframes (4H, daily, weekly, monthly) are **derived from the lowest
supplied timeframe**, not supplied separately. Resampling them myself is the
only way to guarantee the HTF bar boundaries match the execution series and
that no HTF value is visible before its bar completes.

### Format — exactly this
```
timestamp,open,high,low,close,volume
2024-01-02 14:30:00+00,16850.25,16862.00,16845.50,16858.75,4821
```
- `timestamp`: ISO 8601 **with UTC offset**. If your export is exchange-local
  with no offset, say which timezone it is and whether it observes DST.
  A naive timestamp is the single most common cause of a wrong session map.
- Bar timestamps must denote the bar's **OPEN**. If they denote the close, tell
  me — this is BUG-038 in our registry and it silently destroys results.
- Prices in index points. NQ tick = 0.25.
- Rows sorted ascending, no duplicates, gaps allowed.

## 2. VIX — REQUIRED for section 9, optional otherwise
`vix_daily.csv` and, if you have it, `vix_5m.csv`, same format.
Daily-only means the VIX test runs at daily resolution and the "VIX at its own
technical level" model is weak; I will report it as such rather than pretend.

## 3. Magnificent 7 — REQUIRED for section 10
`aapl.csv`, `msft.csv`, `nvda.csv`, `amzn.csv`, `meta.csv`, `googl.csv`,
`tsla.csv` — daily minimum, intraday better, same format. Split/dividend
adjusted, and tell me which, since unadjusted splits create fake momentum.

## 4. Optional but valuable
- `nq_roll_dates.csv` (one `date` column) if the series is unadjusted.
- Real bid/ask spread samples. Every cost figure otherwise is an assumption,
  which is the single largest unresolved risk in every result in this repo.

## Where to put them
`data/nq/` in this repo. **Commit them** — the uploads directory is ephemeral
and was cleared mid-session on 2026-08-16, destroying every file uploaded
before that point.
