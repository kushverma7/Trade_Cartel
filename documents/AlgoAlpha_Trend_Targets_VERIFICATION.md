# AlgoAlpha "Trend Targets" — Editor's Verification Note

*Filed 13 August 2026 alongside `AlgoAlpha_Trend_Targets_Research_Report.pdf`,
which is kept as supplied. This note records what the report's numbers can and
cannot support.*

## The optimization table is in-sample, and that is fatal to it as evidence

The stated method: a grid of **Supertrend Factor [8, 10, 12, 14] x ATR Period
[60, 90, 120] x WMA Length [20, 40, 60]** — **36 combinations** — searched per
asset per timeframe to **maximise the Sharpe Ratio**. Eight assets, three
timeframes, 24 cells.

**Every number in that table is the best of 36 tries, with no out-of-sample
test, no walk-forward, and no null.** That is not a performance estimate; it is
the maximum of 36 draws. With 36 attempts, the best cell looks impressive even
when the true edge is zero. This repository's standing bar for a search of size
K is `t >= sqrt(2 ln K)`; for K=36 that is **2.68**, and nothing here is reported
in units that can be compared against it.

## Parameter instability is presented as a feature; it is the warning sign

The report observes that optimal Factor ranges 8-14 "with no single value
dominating", ATR Period 60-120, and WMA 20-60 — and concludes this "underscores
the necessity of tailored optimization for each trading instrument."

That reads the evidence backwards. **Scattered optima across assets are the
classic signature of curve-fitting.** A real effect produces a *plateau* — nearby
parameter values perform similarly, and the same neighbourhood works across
related instruments. A spike that lands somewhere different for every asset is
what noise looks like when you optimise on it. The report's own strongest
observation is its strongest argument against itself.

## What is missing entirely

- **No date range.** "Historical data" is the only description of the window.
- **No trade count** in any cell.
- **No transaction costs.** No spread, commission or slippage anywhere in the
  methodology. On this desk, a 2-point cost assumption was the single factor
  that killed a 350-cell intraday search on 2026-08-13.
- **No equity curve, drawdown, or win rate.**

## A note on the Sharpe figures themselves

The stated calculation is "annualized returns and standard deviation of **daily**
returns" — an inconsistent pairing when the tested timeframes are 1h and 4h. The
reported values scale strongly with timeframe (1h: 0.02-0.09; 4h: 0.09-0.37;
1d: 0.61-1.17), which is what you would expect from an annualisation convention
applied inconsistently across bar sizes rather than from a genuine timeframe
effect. **The cross-timeframe comparison — the report's headline conclusion — is
not safe on these numbers.**

## What survives, and is worth keeping

**The direction of the conclusion is corroborated elsewhere, independently.**
"Longer timeframes work, short ones do not" is arrived at by three separate
routes now:

- This report: daily Sharpe an order of magnitude above hourly.
- **MSPV2** (`documents/mspv2_dialectic_engine_report.md`): 22-30% win rates on
  1m Gold *regardless of indicator combination* — "not an indicator problem,
  a timeframe problem."
- **This repository's own results**: the only system that has survived every
  control is a **daily** z-reversion engine; the 350-cell intraday search on
  AU200 returned 7 of 350 cells above PF 1.0 against ~175 expected by chance.

Three different instruments, three different methods, same conclusion. That is
real corroboration — unlike the confluence tables elsewhere in `documents/`,
which count correlated sources.

**The mechanical description (sections 2-3) is sound**: double-smoothed
Supertrend (WMA then EMA), consolidation-based rejection logic, ATR-scaled SL
with TP levels as multiples of stop distance. That is a clear, implementable
specification and the most useful part of the document.

## Applicability here

Tested on BTC, ETH, SOL, NVDA, TSLA, AAPL, SPY, QQQ. **No overlap** with
AU200, Gold or US30. Nothing in the table transfers; the mechanism might.

## If this is to be tested properly

1. Fix one parameter set from the *middle* of the plateau, not the optimum.
2. Split the window: fit on the first 60%, report only the last 40%.
3. Include a measured spread.
4. Report trade count and date range with every figure.
5. Run the same grid on shuffled returns; the real result must beat the shuffled
   maximum, not the shuffled mean.
