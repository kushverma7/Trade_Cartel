# Gold Trend — Final Strategy Specification

Deliverable 20 of the research protocol. Produced only because the evidence
supports it: moderate evidence of a robust edge, with the stated fragilities.

**Instrument:** XAUUSD (spot gold), OANDA feed
**Timeframe:** 30-minute. Signals evaluate on CLOSED bars only.
**Two shipped configurations:** E (settled) and G1 (E + regime-scaled entry risk).

---

## 1. Entry rules

A position is opened at the close of a bar on which ALL of the following are
true. Nothing is evaluated intrabar.

**LONG:**
1. `close > highest(high, 24)[1]` — breaks the prior 12 hours' high, with the
   `[1]` offset so a bar cannot trigger on its own extreme
2. `close > EMA(close, 1008)` — above the 21-day regime mean
3. `close > SMA(close, 384)` — above the 8-day mean
4. `close > SMA(close, 630)` — above the 13-day mean
5. Flat, and at least 30 bars have passed since the last exit

**SHORT:** all four mirrored to `<`, **plus a fifth condition** —
`EMA(1008) < EMA(1008)[96]`, i.e. the regime mean must be actively FALLING.
This asymmetry is deliberate and measured: price sits below a flat mean
constantly during uptrend pullbacks, and un-gated shorts bleed the edge.

All lookbacks are derived from the chart timeframe, so the strategy cannot
silently change meaning when moved between 15m and 30m.

---

## 2. Exit rules

**There is exactly one exit: a ratcheting chandelier trailing stop.**

- Initial stop: `4.24 × ATR(14)` from entry
- Trail: anchored to the PREVIOUS bar's extreme (`high[1]` / `low[1]`), so a bar
  can never move its own stop and then hit it
- Ratchets in the trade's favour only, never loosens
- **Tightening:** once the trade has run **15 × ATR(entry)** in its favour, the
  trail tightens from 4.24 to **2.0 × ATR**

## 3. Stop-loss
4.24 × ATR(14), replaced by the trail from the first bar onward. Deliberately
wide: a stop inside the market's own noise band converts random fluctuation
into a realised loss, and the cost-to-risk ratio at tighter stops is fatal.

## 4. Profit target
**NONE.** Twenty target configurations were tested and every one reduced
returns. An independent 103-cell target/stop grid put the optimum at the
boundary even after extending targets to 12 ATR — the mathematical statement of
"no target".

## 5. Time exit
**NONE.** Time-based tightening was tested at 48/96/144/192 bars and was neutral
at best, harmful at worst.

## 6. Maximum holding period
**Unbounded.** Average hold is 20.7 hours; winners 40 hours, losers 15. Capping
the hold destroys the edge, which accrues to hold time rather than entry timing
(MFE/MAE rises from 0.97 at a 3-bar hold to 1.16 at 50 bars).

## 7. Position sizing and pyramiding
- **Risk per trade is solved from a drawdown budget, not chosen.**
  - Config E: 0.705% (25% budget) or 0.553% (20% budget)
  - Config G1: 0.723% (25% budget) or 0.567% (20% budget)
- `qty = equity × risk% / (4.24 × ATR)`
- **Adds: 4 maximum, every 1.5 ATR of favourable movement, each sized on the
  ATR AT ENTRY** (not the current ATR — current-ATR sizing shrinks the add
  exactly when volatility expands, which is when the trade is working)
- Notional cap 20×; the full 4-add stack is ~3.65× account leverage

**Config G1 only** — the opening position (NOT the adds) is multiplied by:
```
f1 = 1.4 if |close − EMA(1008)| / ATR > 6.0     else 0.8
f2 = 1.4 if SMA(ATR,20) / SMA(ATR,200) > 1.05   else 0.6
multiplier = clip(f1 × f2, 0.5, 2.0)
```

## 8. Session filter
**NONE — deliberately.** New York (16:00–21:00 UTC) is the only losing session
(+0.041 ATR raw, negative after costs), but it was **not** validated out of
sample, so per the protocol it is not applied.

## 9. Long and short treatment
Both traded. Shorts sized at **0.75×** long risk and gated on a falling regime
EMA. Shorts are the BETTER book on a per-trade basis (PF 1.891 vs longs' 1.806,
35% of net profit); cutting or sizing them up were both tested and both made
the system worse.

## 10. Trading cost assumptions
- Slippage **0.20 points per side** — set this to YOUR broker's real spread
- Commission $0.07 per contract per side
- **Break-even is ~1.6 points of slippage.** At 0.50 pt returns fall sharply;
  at 1.50 pt the system is dead
- **Overnight financing is NOT modelled.** At 38.7% time in market and ~2.6×
  time-weighted leverage, financing at 2–8% annual costs an estimated
  **2–8% of equity per year**, which is 2–9% of the CAGR. Every figure in the
  research should be read as that much optimistic

## 11. When NOT to trade this
1. **Account below ~$25,000** at current gold prices — whole-ounce granularity
   means a $5,000 account takes a fraction of its signals and loses money.
   Unless your broker offers 0.001 lots / micro-gold, in which case $10,000 works
2. **If your gold spread exceeds ~1.0 point** — the margin to break-even is gone
3. **If you cannot pyramid.** At a fixed lot size the average trade is
   **−4.01 points**. The adds are the edge, not an enhancement
4. **If you will intervene.** Skipping signals destroys it — 26.7% of positions
   carry 100% of the profit
5. **If you cannot sit through a 25-trade losing run** or a ~50% drawdown. The
   backtested drawdown is a lucky path; the Monte Carlo median is worse
6. **On any instrument other than XAUUSD or US30 without re-testing.** Two
   instruments is not evidence of generality

---

## Evidence grade: MODERATE evidence of a robust edge

Supporting: survives a corrected random-entry null (93rd percentile on gold,
100th on US30); DSR 0.9996; PBO 0.099; TradingView deep backtest agrees to 2.1%
on PF and 0.7% on order count; a 4,500-combination search re-finds the shipped
parameters; quarterly re-optimisation performs WORSE than leaving it alone.

Against: **10 of 737 trades separate it from break-even and 20 make it a
loser**; the untouched test window contains gold's largest trend of the sample;
parameters were selected across earlier rounds with knowledge of the full
sample, so the out-of-sample is not virgin; overnight financing unmodelled;
never seen a multi-year gold bear market.
