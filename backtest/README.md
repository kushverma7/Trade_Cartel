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
| `io.py` | TradingView CSV export loader |
| `synth.py` | synthetic bars, for plumbing checks only |
| `validate_bt.py` | **INCOMPLETE** — backtrader wiring only, see its header |

## The one thing missing: your bars

No market-data host is reachable from this container — Yahoo, Stooq,
AlphaVantage, TwelveData, Binance and tradingview.com all fail; only PyPI is
allowed. So the search cannot start without data.

**TradingView → right-click the chart → Export chart data → CSV.** Drop the
file anywhere in the repo and run:

```
python3 -m backtest.optimize --csv XAUUSD_15.csv
```

Any column spelling TradingView emits will load; unix or ISO timestamps both
work. Export the longest history your plan allows — the split halves it, and
a test block under ~30 trades cannot conclude anything.

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
