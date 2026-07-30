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

## London Strategic Edge — one setting away

Their official client is on PyPI, which is one of the few hosts this
container CAN reach, so it is installed: `pip install lse-data` (v0.14.0).
`backtest/lse_client.py` wraps it.

```
python3 -m backtest.lse_client --check
python3 -m backtest.lse_client --symbol XAU/USD --tf 15m \
    --start 2021-01-01 --save data/xau_15m.csv.gz
```

The API gives `candles()` (paged OHLCV, 1s to 1mo resolutions, FX back to
2009) and `history()` (server-side bulk export that builds the file, polls
the job and downloads with resume — the route for tick data or very long
ranges).

**This removes the file-size problem entirely.** Data lands directly in the
container from the API; nothing has to be carried through chat. The size
limit only ever existed because the file was being moved by hand.

### The blocker is egress policy, not the key

```
LSEError [0] request failed before an HTTP response:
Tunnel connection failed: 403 Forbidden
```

The session's egress proxy refuses the CONNECT tunnel to
`api.londonstrategicedge.com`. The request never leaves the container, so the
key never reaches their server — `authenticated` reads False for that reason
and no credential can change it. Add `londonstrategicedge.com` and
`api.londonstrategicedge.com` to the environment's network allowlist:
https://code.claude.com/docs/en/claude-code-on-the-web

### Credential handling

Read from `LSE_API_KEY`, falling back to a gitignored, mode-600 `.env`. Never
passed on argv (visible in the process table), never logged, never committed —
verified absent from the working tree and from every commit.

`.env` dies with this container. For persistence set `LSE_API_KEY` in the
environment's own variable settings; the client prefers it over `.env`.

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
