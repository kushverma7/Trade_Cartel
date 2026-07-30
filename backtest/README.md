# Offline backtest + optimisation

Built after the user supplied `github.com/mementum/backtrader`. This exists
because every result in `RESULTS_LEDGER.md` is in-sample: TradingView gives
one number per manual run, so nothing has ever been tested on data it was
not fitted to. This runs the search offline, with a locked train/test split.

## What works right now

| File | Status |
|---|---|
| `levels.py` | 18 key-level types, non-lookahead by construction | 
| `engine.py` | fast bar-loop backtester, ~0.14s per 14k-bar run |
| `optimize.py` | greedy level selection + parameter grid, train/test split |
| `test_engine.py` | **5 accounting tests, all passing** |
| `io.py` | thin wrapper — all parsing goes through `inspect_csv.load` |
| `inspect_csv.py` | tolerant loader + file report; run this on any export FIRST |
| `overfit.py` | Deflated Sharpe + PBO (ported from ML4T / Lopez de Prado) |
| `audit_ledger.py` | applies DSR to this repo's own recorded results |
| `synth.py` | synthetic bars, for plumbing checks only |
| `validate_bt.py` | **INCOMPLETE** — backtrader wiring only, see its header |

## The one thing missing: your bars

No market-data host is reachable from this container — Yahoo, Stooq,
AlphaVantage, TwelveData, Binance and tradingview.com all fail; only PyPI is
allowed. So the search cannot start without data.

Two routes:

- **London Strategic Edge → /data/#builder → export.** The site is blocked
  from this container (403), so it has to come from your side.
- **TradingView → right-click the chart → Export chart data → CSV.**

Either way, drop the file in the repo and run the inspector first:

```
python3 -m backtest.inspect_csv YOURFILE.csv          # reports what it found
python3 -m backtest.optimize   --csv YOURFILE.csv     # runs the search
```

The loader handles comma/semicolon/tab delimiters, unix or ISO or day-first
timestamps, `O/H/L/C` and `Bid/Last/Price` aliases, comma decimal separators,
unnamed timestamp columns, and tick data (add `--resample 15min`).

Two silent-corruption bugs were found and fixed while testing it, both of the
kind that would have poisoned results without ever raising an error:

- pandas `format="mixed"` infers a date format **per element**, so a day-first
  file parsed `02/01` as 2 Jan and `13/01` as 13 Jan — no error, no NaN, and a
  January file read as spanning January to October. Now one consistent format,
  chosen by fewest-unparseable then verified monotonic.
- an unnamed first column holding the timestamps was not recognised, which is
  what `to_csv` and several exporters emit by default.

Export the longest history available. The split halves it, and a test block
under ~30 trades concludes nothing — as the demo run above shows, where 2,112
bars produced a train block of 30 trades and an unreadable test block of 24.

## What the optimiser does

1. **Greedy level selection on TRAIN.** 18 levels is 262,144 subsets; greedy
   reaches a good one in ~150 runs and each step is interpretable — you see
   which level was added and what it bought.
2. **Parameter grid on TRAIN**, level set held fixed (72 combos).
3. **Re-select levels** under the winning parameters.
4. **One evaluation on TEST.** Once. Nothing is tuned against it.

Re-running step 4 and adjusting in between destroys the split and turns the
result back into an in-sample number. That is the failure mode this whole
directory exists to prevent.

## Read this before trusting any output

On **synthetic random-walk data**, with no real structure whatsoever, the
optimiser found a configuration scoring **train PF 1.730** — and it decayed
to 1.264 out of sample.

Greedy search over 18 levels and 72 parameter combinations will manufacture
an impressive in-sample number out of pure noise. That is not a flaw in the
search; it is what search does. It is also, precisely, what has been
happening in this repo for four months: every ledger row is a train-set
number with no test set behind it.

The train figure is not the result. **The decay is the result.**
