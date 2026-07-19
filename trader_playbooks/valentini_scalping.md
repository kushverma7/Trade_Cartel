# Valentini Momentum-Join Scalping — extracted 2026-07-19
# Source: podcast transcript. Fabio Valentini, Robbins World Cup scalper,
# VERIFIED track record: 68% / 88% / 218% quarterly, ~500 trades/quarter,
# NASDAQ futures, footprint/orderflow. Highest-credibility source so far.

## Doctrine
- NEVER catch the falling knife. No entries at extremes. Join AFTER
  volume aggression + price follow-through confirm the pressure.
- He TESTED the trapped-traders/liquidity-sweep model: lower win rate
  than momentum-join. [Contradiction tally vs our reclaim family: 1]
- Win rate over home runs: ~50% WR at min 1:2 RR beats lottery R:R.
  Reversal WR 40% < trend-join 50-60% (his measured sample, 500+).

## The checklist (all boxes or no trade)
1. Day bias: 15m structure / initial-balance breakout direction
2. Point of interest: ONE level (max-volume line inside a demand zone)
3. Volume aggression AT the POI (footprint; we proxy: vol surge + body)
4. Price follow-through in bias direction
5. VWAP SD location sensible (not chasing into 2nd SD)
6. Time window OK (he SKIPS the volatile open; trades post-IB)

## VWAP statistics (his measured numbers)
- Session reaches 3rd SD in only ~7% of sessions -> take profit, never
  hold for it
- Beyond 2nd SD -> high-probability revert to VWAP/POC
- Reversal trades ONLY when: day already in profit AND beyond 2nd SD
  AND targeting fair value (VWAP/POC)
- Mid/late-session rebalance: explosive days retrace to ~50% / fair
  value in 3rd-4th quarter of session

## Risk protocol
- Base risk 0.25%/trade, minimum 1:2 RR
- Intraday compounding: bank the morning, escalate size with profits
  only ("exponential days" -> his 218% quarter)
- HARD STOP: 3 losses in a day = done (market not in model's regime)
- One position at a time; fragment entries, common stop
- TP at statistical expected move (avg session range), not aspiration
- Trail behind structure; exit early ONLY if structure break is
  CONFIRMED by opposing volume, else treat as fakeout and hold BE

## Timeframe stack
15m bias -> 1m structure -> 15s / 20-tick range bars execution

## Implementation
indicators/valentini_momentum_engine.pine — JOIN (bias+POI pullback+
aggression) and REVERT (late-session 2SD re-entry toward VWAP).
Aggression = proxy (no footprint data in Pine) — stated honestly.

## Confluence mapping
- 3-stop breaker == Cognitive Architecture Hot/Cold protocol
- Confirmation-before-entry == 3rd independent source (CPI continuation,
  reclaim close, PBD close-count)
- TENSION: skips session open; our gold edge trades 8:30-11. Different
  asset; B1 backtested, stands.
- TENSION: rejects sweep-reversal models. Logged against B2/v3 reclaim.
