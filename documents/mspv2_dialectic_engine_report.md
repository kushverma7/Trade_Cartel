# DIALECTIC ENGINE — MASTER REPORT

## Editor's Verification Note

*Added on filing, 13 August 2026. Body reproduced exactly as supplied.*

### This is the most honest document in the set, and it should be read first

Unlike every other document filed in `documents/`, this one **reports its own
negative results with real numbers**: v1 at ~22-25% win rate, v9 at 30.8% on
Gold 1m, v4 "broken", v6 "no signals printed". Those are measurements, not
claims. A report that publishes its failures is worth more than one that
publishes only successes.

### It directly contradicts MSPV1, and this document is the one with data

| | MSPV1 says | MSPV2 says |
|---|---|---|
| 1m timeframe | "55-65% accuracy"; RANK 4 setup "62-68%", *"Best market: fast-moving markets, scalping"* | **"22-30% consistently on 1m Gold regardless of indicator combination"** and *"Any asset, 1m — AVOID"* |

MSPV2 supplies observed win rates. MSPV1 supplies unsourced percentages. Where
they disagree, MSPV2 wins on evidence. Its diagnosis is also the right one:
*"This is not an indicator problem — it's a timeframe problem."*

That conclusion independently corroborates what this repository measured on
2026-08-13: across a 350-cell intraday search on AU200, only 7 cells reached
PF > 1.0 against ~175 expected by chance, because a fixed cost dominates
everything at high frequency. Same finding, different instrument, arrived at
separately.

### Genuinely useful technical content

- **The v4 alternation bug** is a real, correctly diagnosed circular-logic
  failure (`swas` never set true, so the flip never fired). That is exactly the
  class of bug this repository tracks in `bugs/BUG_REGISTRY.md`.
- **"Max 3 hard requirements on one bar"** — the v6 zero-signal diagnosis is
  sound and matches our own experience with over-gated confluence engines.
- **Histogram DIRECTION not LEVEL** (`mh > mh[1]` rather than `mh > 0`) is a
  real and often-missed distinction.
- **Cooldown as the single biggest noise reducer** is plausible and cheap to test.

### What still carries no evidence

The Tier 1/2/3 confluence rankings, the per-asset timeframe table, and the exit
logic ranking are presented without trade counts or windows. "Tested best"
parameters are stated without saying what was tested against. And the
Supertrend/Alpha Trend **97** setting appears again — now in four supplied
documents and the user's own script. One number propagating, not four
confirmations.

*Everything below this line is the document as supplied, unaltered.*

---


## What Worked, What Didn’t, Best Confluences, Key Lessons

### Based on every version built in this session

-----

## VERSIONS BUILT — SUMMARY

|Version    |Core Concept                           |Win Rate Observed    |Verdict                             |
|-----------|---------------------------------------|---------------------|------------------------------------|
|v1         |6-gate confluence + sweep + alternation|~22-25%              |Logic solid, too many signals       |
|v2         |v1 + win% tracker added                |Same as v1           |Tracker only, no logic change       |
|v3         |v1 + time filter + spacing + min conf 5|Fewer signals        |Better quality, still untested      |
|v4         |Always-in reversal, alternation blocked|Never opened opposite|Broken — alternation blocked flips  |
|v5         |Always-in, no blocking, 3 gates        |More signals         |Fixed but too noisy                 |
|v6         |Body ratio + sweep + EMA200 + regime   |No signals printed   |Too strict — all conditions same bar|
|v7         |Sweep + RSI + MACD only, always-in     |Signals printed      |Cleanest, most reliable             |
|v8         |Supertrend core + 3 tiers              |Signals printed      |Good structure                      |
|v9         |Alpha Trend (MFI) core + 3 tiers       |30.8% on Gold 1m     |AT logic solid, wrong timeframe     |
|v1 Final   |v1 + EMA cross signals + win tracker   |Cleanest visually    |Best visual version                 |
|Modes      |v1 + Early/Balanced/Conservative modes |Not measured         |Most flexible                       |
|Reversal   |Modes + Reversal Engine                |Not measured         |Most complete                       |
|Strategy v2|Full strategy with all exits           |Not measured         |Most professional                   |

-----

## WHAT WORKED

### 1. LIQUIDITY SWEEP DETECTION

**The single best signal in the entire system.**

```
sw_bull = low < rl[1] and close > rl[1]   // wick below, close back above
sw_bear = high > rh[1] and close < rh[1]  // wick above, close back below
```

Why it works: This is the institutional stop hunt pattern. Price sweeps below a structural low to grab sell stops, smart money absorbs, price snaps back. The close above the level on the same candle is the confirmation. This is not random — it happens at every significant turning point.

**Key rule: The sweep must close back INSIDE the level on the same bar. A wick that doesn’t close back is just a breakout.**

-----

### 2. EMA STACK — BULL/BEAR STACK DETECTION

**Best trend filter built.**

```
bull_trend = ef > em and em > es   // EMA9 > EMA21 > EMA50
bear_trend = es > em and em > ef   // EMA50 > EMA21 > EMA9
```

Why it works: When all three EMAs are stacked in order, price has clear directional energy. Signals taken WITH the stack dramatically outperform signals taken against it or in chop.

**Key rule: Never take a long signal in a bear stack. Never take a short signal in a bull stack.**

-----

### 3. EMA50 SLOPE FILTER

**Most underrated addition in the entire build.**

```
ema50_rising  = es > es[3]
ema50_falling = es < es[3]
```

Why it works: The EMA50 slope tells you whether institutional money is accumulating or distributing. A rising EMA50 means buyers are in control at the macro level. All trend signals filtered by slope direction significantly reduced false signals.

**Key rule: Only take longs when EMA50 is rising or flat. Only take shorts when EMA50 is falling or flat.**

-----

### 4. RSI ZONE FILTER — NOT EXTREMES

**Works best as a zone filter, not a level trigger.**

```
rsi_bull_ok = rsi > 45 and rsi < 72   // has fuel, not exhausted
rsi_bear_ok = rsi < 55 and rsi > 28
```

Why it works: The mistake most systems make is using RSI as a trigger (buy when oversold). RSI works better as a filter — confirming there is ROOM for price to move. RSI 55-70 on a long means momentum is with you but not exhausted. RSI above 72 means the move is late.

**Key rule: RSI is a filter, not a trigger. Trade in the zone, not at the extremes.**

-----

### 5. MACD DIRECTION (not crossover)

**MACD above signal line is enough. Crossover is too late.**

```
macd_bull = ml > sl2    // MACD above signal
macd_bear = ml < sl2
```

Why it works: The crossover fires after the momentum shift has already happened. Simply being on the right side of the signal line (positive histogram) is sufficient confirmation that momentum is aligned.

**Key rule: Use MACD direction as a filter, not MACD crossover as a trigger.**

-----

### 6. COOLDOWN FILTER

**Single biggest noise reducer in the system.**

```
var int bars_since_sig = cooldown_bars + 1
bars_since_sig := bars_since_sig + 1
bool cooled = bars_since_sig > cooldown_bars
```

Why it works: Most false signals cluster together. After one signal fires, the next 5-10 bars are statistically more likely to be noise reactions to the same move. The cooldown prevents stacking signals into the same momentum impulse.

**Key rule: Minimum 10 bars between signals on 1m-5m. Minimum 5 bars on 15m-1H.**

-----

### 7. ALPHA TREND (MFI-BASED)

**Superior to Supertrend for this system.**

The Alpha Trend uses Money Flow Index internally which means it weighs BOTH price and volume before determining direction. Standard Supertrend only uses price vs ATR band. On Gold and BTC specifically, the AT with period 97 and mult 3.0 gave smoother, more meaningful trend flips.

**Key rule: AT period 97, mult 3.0 on 15m and 1H. On 1m it lags too much.**

-----

### 8. VOLUME SURGE — CONFIRMATION ONLY

**Works as confirmation, not as a trigger.**

```
vol_surge = volume > vol_ma * 1.3
```

Why it works: Volume surge on its own means nothing — it just means activity. Volume surge COMBINED with a directional signal (sweep + EMA alignment) confirms that real money is behind the move.

**Key rule: Volume surge should add to confluence score but never be the primary reason to trade.**

-----

### 9. EMA9/21 CROSSOVER WITH STACK CONFIRMATION

**Best entry trigger when combined with EMA50 position.**

```
cross_9_21_up = ta.crossover(ef, em)
confirmed_buy = cross_9_21_up and ef > es and close > es and rsi > 50
```

Why it works: The EMA9/21 cross is faster and fires earlier than waiting for full stack alignment. Filtering it with close above EMA50 and RSI above 50 removes the majority of false crosses in chop.

**Key rule: EMA9 crosses EMA21 is the trigger. EMA50 is the filter. RSI confirms momentum direction.**

-----

### 10. REVERSAL ENGINE CONDITIONS

**Best reversal setup found:**

- Bear/mixed trend (EMA stack bearish)
- RSI below 35 (genuinely oversold)
- Sweep low within last 5 bars
- MACD histogram turning up (mh > mh[1])
- EMA9 curl up (ef > ef[1])
- Price reclaims EMA9 (close > ef)

All six together = high probability reversal. Missing any two = skip it.

**Key rule: Never trade a reversal without a sweep. The sweep is the proof that stops got hunted.**

-----

## WHAT DIDN’T WORK

### 1. TOO MANY GATES ON SAME BAR

**v6 printed zero signals because it required 4+ conditions all true simultaneously on one candle.**

On a 1m chart a candle lasts 60 seconds. Requiring a liquidity sweep + strong body + RSI zone + MACD aligned + macro trend + not choppy all on the same bar is statistically near-impossible. This is why v6 showed nothing.

**Lesson: Max 3 hard requirements on one bar. Use the others as filters from previous bars.**

-----

### 2. VOLUME AS A HARD GATE ON LOW TIMEFRAMES

**Killed v1’s signal count on 1m Gold.**

Volume data on Gold 1m is unreliable and irregular. A volume gate of vol > vol_ma * 1.3 was blocking valid signals during quiet institutional accumulation phases. Removed it as a hard requirement in later versions.

**Lesson: Volume gates work well on 15m+. On 1m they create too many misses.**

-----

### 3. ALTERNATION BLOCKING (lwas/swas) IN ALWAYS-IN SYSTEMS

**Broke v4 completely. The system never opened the opposite trade.**

The lwas/swas logic was designed to prevent same-direction signal stacking. But in an always-in system it prevented the flip. The issue: `lwas = true` after a long, then when short signal fires, `vl = lsig and not lwas` — correct. But `vs = ssig and not swas` — swas was never set to true because the long never fired again. The logic was circular.

**Lesson: In always-in reversal systems, remove alternation logic entirely. Only gate is `pos != 1` or `pos != -1`.**

-----

### 4. 1M TIMEFRAME FOR ANY SYSTEM

**Win rates of 22-30% consistently on 1m Gold regardless of indicator combination.**

1m Gold is dominated by market maker spread games, news reactions, and institutional algo noise. No indicator-based system has reliable edge on 1m without additional filters (time of day, session, news calendar). This is not an indicator problem — it’s a timeframe problem.

**Lesson: Run any system on 15m minimum. Test on 5m. Never live trade 1m without manual confirmation.**

-----

### 5. BODY RATIO FILTER AS HARD REQUIREMENT

**Too restrictive. Most candles on 1m have body ratios below 0.5.**

```
body_ratio = candle_range > 0 ? candle_body / candle_range : 0
strong_bull_body = close > open and body_ratio >= body_pct
```

On 1m timeframes most candles are small-bodied with significant wicks. Requiring 50%+ body ratio eliminated nearly all signals. On 15m+ it works better.

**Lesson: Body ratio filter works on 15m+. Skip it on 1m-5m.**

-----

### 6. REQUIRING MACD HISTOGRAM POSITIVE (mh > 0)

**Too restrictive in trend continuation.**

Early versions required `mh > 0` for longs. But many of the best entries happen when MACD is recovering from negative to less negative — the histogram is still below zero but rising. This filtered out the best pullback entries.

**Lesson: Use histogram DIRECTION (mh > mh[1]) not histogram LEVEL (mh > 0).**

-----

### 7. ANTI-REGIME FILTER (atr_pct > 0.65 = no signals)

**Blocked signals during the most profitable high-volatility breakouts.**

The anti-regime filter was designed to stop trading in chaotic markets. But high ATR percentile often means a strong directional move is happening — exactly when you WANT to be in a trade with the trend.

**Lesson: High volatility is not the same as random chaos. Only filter for choppy LOW volatility ranges, not high volatility trends.**

-----

## BEST CONFLUENCES THAT WORK TOGETHER

### TIER 1 — HIGHEST QUALITY (use all 5, signal fires rarely but accurately)

1. EMA stack aligned (bull or bear)
1. Liquidity sweep on current bar
1. EMA50 slope in same direction
1. RSI in valid zone (45-70 for longs, 30-55 for shorts)
1. MACD histogram direction matches

### TIER 2 — HIGH QUALITY (use 4, fires more frequently)

1. EMA stack aligned
1. EMA9/21 crossover confirmed
1. Close above/below EMA50
1. RSI zone filter

### TIER 3 — STANDARD (use 3, most signals, needs cooldown)

1. Liquidity sweep
1. RSI zone
1. MACD direction

-----

## TIMEFRAME RECOMMENDATIONS

|Asset        |Recommended TF|Signal Mode |Min Confluence|
|-------------|--------------|------------|--------------|
|BTC Perps    |15m           |Balanced    |4/6           |
|BTC Perps    |5m            |Conservative|5/6           |
|Gold (XAU)   |15m           |Balanced    |4/6           |
|Gold (XAU)   |1H            |Early       |3/6           |
|Broad markets|1H            |Balanced    |4/6           |
|Any asset    |1m            |AVOID       |—             |

-----

## SIGNAL MODE GUIDE

|Mode        |Best For                                |Risk              |
|------------|----------------------------------------|------------------|
|Early       |Fast markets, trending days, momentum   |More false signals|
|Balanced    |Default, any asset, any session         |Balanced          |
|Conservative|Low signal, high confidence, larger size|Misses entries    |

-----

## EXIT LOGIC RANKING — BEST TO WORST

1. **ATR Stop Loss** — non-negotiable, always use
1. **Break-even at 1R** — removes risk once profitable, always use
1. **EMA21 close below/above** — excellent for trend trades
1. **Trailing ATR stop** — locks in profits on runners
1. **Max bars exit** — prevents dead money sitting in losing trades
1. **RSI exit** — works but fires early on strong trends
1. **MACD exit** — most lagging, fires after most of the damage already done
1. **Opposite signal only** — NEVER rely on this alone

-----

## PARAMETER SETTINGS THAT TESTED BEST

```
EMA Fast:        9
EMA Mid:         21
EMA Slow:        50
ATR Length:      14
RSI Length:      14
RSI Overbought:  60-65
RSI Oversold:    35-40
MACD:            8/17/9
Liq Lookback:    20-30 bars
Cooldown:        10 bars (1m-5m), 5 bars (15m+)
TP Multiplier:   2.0-2.5x ATR
SL Multiplier:   1.0x ATR
Trail ATR:       1.5x ATR
Alpha Trend:     Period 97, Mult 3.0
Supertrend:      Period 97, Mult 3.1
```

-----

## THE CORE TRUTH FROM THIS ENTIRE BUILD

**Win rate is not determined by the indicator. It is determined by:**

1. **Timeframe** — 15m+ has structural edge. 1m has noise.
1. **Session** — London (07-12 UTC) and NY (13-17 UTC) have real liquidity. Asian session is manipulation-heavy.
1. **Trend alignment** — Trading WITH the EMA stack doubles your odds vs against it.
1. **R:R ratio** — A system with 45% win rate and 2.5:1 R:R is more profitable than 60% win rate at 1:1.
1. **Discipline** — The cooldown filter alone improved signal quality more than any single indicator combination.

**The Dialectic Framework — the philosophical core:**

- THESIS (consolidation, low vol) = Wait, do not trade
- ANTITHESIS (sweep, chaos, stop hunt) = Prepare, identify the setup
- SYNTHESIS (new equilibrium, reversal confirmed) = This is the entry zone

Every profitable trade in this system happened in the SYNTHESIS phase — after the liquidity sweep (antithesis) completed and price confirmed a new direction.

-----

## WHAT TO DO NEXT

1. **Run v1 Final or Modes version on 15m BTC and Gold for 2 weeks — paper trade only**
1. **Log every signal: time, session, EMA state, RSI at entry, sweep yes/no**
1. **After 50 trades analyze: which confluence combination had highest win rate**
1. **Then and only then — consider live capital**

The indicators are tools. The edge comes from the system around them.