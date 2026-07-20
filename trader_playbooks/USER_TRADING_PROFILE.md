# USER TRADING PROFILE — "Act As Me" Reference
# Loaded every session. This is who I'm trading-thinking for.

## Identity & Market
- Gold (XAUUSD) scalper, 5m primary chart; also tests 1m/30m/1H
- TradingView free plan: ~2 months of 5m history, no Premium
- Pepperstone feed preferred over OANDA for gold backtests
- Executes manually; signals must fire in REAL TIME (bar close + alerts)

## Candidate edges (NOT proven — small-sample result retracted 2026-07-20)
- Trendline breakout (OLS, lookback 22) + London/NY-open session filter:
  PF 3.656 on XAUUSD 5m was the small-sample result (~2 months, 117
  trades) previously called "proven" -- user explicitly retracted this
  as evidence, sample too small. Kept as the current default to
  re-test on a larger sample, not because it's validated.
- Session filter (03:00-05:00, 08:30-11:00 NY time) is still the
  working hypothesis for strongest accuracy lever, but also unvalidated
  at meaningful sample size -- treat as a lead to re-test, not a fact.

## Disproven / burned by (do not repeat)
- Reversal Sniper v2 auto-zone reclaims on 5m: PF 0.731, 313 trades —
  zone churn produced false failed-breakdowns; fixed in v3 (HTF walls,
  0.3 ATR min flush, wider stops)
- Naked patterns without context filters
- Overtrading: high trade counts = red flag, prefer fewer/cleaner

## Standards (apply to every build)
- Non-repainting is non-negotiable: closed-bar math only
- Realistic costs: commission cash-per-contract 0.07, slippage 5-10
- Honest reporting: PF, win rate, trade count, drawdown; call out
  small-sample results as anecdotes
- One strategy = one file in strategies/, indicators in indicators/
- Everything committed + pushed to kushverma7/Trade_Cartel

## Preferences
- Wants copy-pastable Pine v6 text in chat (also keep files in repo)
- Flip strategies: BUY reverses short, SELL reverses long
- News awareness: CPI/8:30 ET events — flat into print, trade
  confirmation after (Confirm Continuation mode default)
- Real-time alerts wired via alertcondition, "Once Per Bar Close"

## Knowledge layer (confluence — STANDING RULE, see MEMORY.md)
- trader_playbooks/candlestick_patterns.md: 16 Nison patterns, tiered
  A/B/C by Bulkowski reliability. A = full vote, B = needs trend +
  location, C = ignore by default
- Apply as confluence in every new/updated strategy: aligned A-pattern
  upgrades entry; opposing A-pattern vetoes or de-risks
- Future material (books, trader transcripts) extends this layer via
  playbook extraction -> confluence integration -> backtest verdict

## How to act like the user
1. Default instrument/timeframe: XAUUSD 5m unless told otherwise
2. Judge every idea by backtest evidence, not story
3. Prefer session-filtered, low-frequency, confirmed entries
4. Protect the downside first: stops behind structure, disaster stops
   on flip systems, time exits on news trades
5. When results are bad, say so plainly and propose the next test
