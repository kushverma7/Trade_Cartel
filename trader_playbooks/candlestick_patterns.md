# Candlestick Playbook — Source Rules for the Real-Time Engine

Each entry: mechanical definition → context requirement → what confirms it.
Every pattern here is implemented in `indicators/candlestick_engine.pine`
and prints + alerts in real time on bar close.

Reliability tiers (from Bulkowski's quantified testing, honest ranking):
- **A** = statistically meaningful edge with confirmation
- **B** = works only with strong context (trend + location)
- **C** = popular but near coin-flip; included for completeness, off by default

## Reversal patterns (bullish)

| Pattern | Definition (mechanical) | Context required | Tier |
|---|---|---|---|
| Hammer | lower shadow >= 2x body; upper shadow <= 25% of range; body in top third | downtrend, at/near swing low | B |
| Bullish Engulfing | bear candle then bull candle whose body engulfs prior body | downtrend | A |
| Piercing Line | bear candle, then bull candle opening below prior low, closing above prior body midpoint | downtrend | B |
| Morning Star | big bear body, small body gapping/holding lower, bull body closing into first candle's body | downtrend | A |
| Bullish Harami | big bear body, then small body inside it | downtrend | C |
| Tweezer Bottom | two candles with (near-)equal lows, second closes bullish | downtrend, at support | C |
| Three White Soldiers | three consecutive bull bodies, each closing near its high, opens within prior body | after decline | A |

## Reversal patterns (bearish)

| Pattern | Definition (mechanical) | Context required | Tier |
|---|---|---|---|
| Shooting Star | upper shadow >= 2x body; lower shadow <= 25% of range; body in bottom third | uptrend, at/near swing high | B |
| Bearish Engulfing | bull candle then bear candle whose body engulfs prior body | uptrend | A |
| Dark Cloud Cover | bull candle, then bear candle opening above prior high, closing below prior body midpoint | uptrend | B |
| Evening Star | big bull body, small body gapping/holding higher, bear body closing into first candle's body | uptrend | A |
| Bearish Harami | big bull body, then small body inside it | uptrend | C |
| Tweezer Top | two candles with (near-)equal highs, second closes bearish | uptrend, at resistance | C |
| Three Black Crows | three consecutive bear bodies, each closing near its low, opens within prior body | after advance | A |

## Indecision / warning

| Pattern | Definition | Meaning | Tier |
|---|---|---|---|
| Doji | body <= 10% of range | trend exhaustion warning at extremes only | C alone, B at swing + trend |

## Nison's context rules (implemented as filters, not suggestions)

1. **Trend prerequisite**: a reversal pattern requires a trend to reverse.
   Engine: EMA(20) slope + close position over last `trendLen` bars.
2. **Location**: patterns matter at swings. Engine: within `locAtr` x ATR of
   the highest high / lowest low of the last `swingLen` bars.
3. **Confirmation**: optional next-candle confirmation (close beyond the
   pattern's extreme) — halves the signals, roughly doubles the quality.
4. **Size matters**: engulfing/star bodies must be >= `bigBody` x average
   body to exclude noise candles.

## v2 additions — "@Thechartcornerr" chart pattern cheat sheet (2026-07-20)
Source: visual-only PDF cheat sheet (Instagram-style account), names
and pattern shapes only -- no numeric criteria extractable (images
carry the actual geometry, text layer has labels only). Public-domain
classical TA, same treatment as the original Nison-derived table above:
apply well-established mechanical definitions to the named patterns.
No new context rules; same trend/location/confirmation filters apply.

## Reversal patterns (bullish) — additions

| Pattern | Definition (mechanical) | Context required | Tier |
|---|---|---|---|
| Inverted Hammer | same shape as Shooting Star (upper shadow >= 2x body, small/no lower shadow) | downtrend, at swing low | C |
| Dragonfly Doji | doji body, upper shadow <= 10% of range, lower shadow >= 60% of range | downtrend, at swing low | C |
| Bullish Spinning Top | small body (<=30% of range), both shadows roughly equal and substantial (each >=25% of range) | downtrend, at swing low | C |
| Bullish Marubozu | body >= 90% of range (near-zero shadows), bull | works as a momentum/strength candle anywhere; stronger at a breakout | B |
| Bullish Long-Legged Doji | doji body, BOTH shadows long (each >= 35% of range) | downtrend, at swing low | C |
| Bullish Kicker | bear (or flat) candle, then a bull candle whose LOW opens above the prior candle's HIGH (zero body overlap) | any -- rare, self-confirming by the gap | A |
| Rising Three Methods | big bull body, then 3 small candles (any color) staying within that body's range, then a bull candle closing above the first candle's high | uptrend continuation (mid-trend, not at a swing extreme) | B |
| Three Inside Up | bear candle, smaller bull candle inside it (harami), then a third bull candle closing above the first candle's open | downtrend, at swing low | B |
| Three Outside Up | bear candle, bull engulfing candle, then a third bull candle closing above the engulfing candle's close | downtrend, at swing low | B |

## Reversal patterns (bearish) — additions

| Pattern | Definition (mechanical) | Context required | Tier |
|---|---|---|---|
| Hanging Man | same shape as Hammer (lower shadow >= 2x body, small/no upper shadow) | uptrend, at swing high | C |
| Gravestone Doji | doji body, lower shadow <= 10% of range, upper shadow >= 60% of range | uptrend, at swing high | C |
| Bearish Spinning Top | small body (<=30% of range), both shadows roughly equal and substantial | uptrend, at swing high | C |
| Bearish Marubozu | body >= 90% of range (near-zero shadows), bear | works anywhere; stronger at a breakdown | B |
| Bearish Long-Legged Doji | doji body, BOTH shadows long (each >= 35% of range) | uptrend, at swing high | C |
| Bearish Kicker | bull (or flat) candle, then a bear candle whose HIGH opens below the prior candle's LOW (zero body overlap) | any -- rare, self-confirming by the gap | A |
| Falling Three Methods | big bear body, then 3 small candles staying within that body's range, then a bear candle closing below the first candle's low | downtrend continuation (mid-trend) | B |
| Three Inside Down | bull candle, smaller bear candle inside it (harami), then a third bear candle closing below the first candle's open | uptrend, at swing high | B |
| Three Outside Down | bull candle, bear engulfing candle, then a third bear candle closing below the engulfing candle's close | uptrend, at swing high | B |

## Pending: material from user (book chapters, trader transcripts)

Every new scenario from supplied material gets:
1. an entry in this file (definition -> context -> confirmation)
2. a module in the engine (label + alertcondition, bar-close evaluation)

---

## CLASSIC CHART PATTERNS (multi-swing geometric patterns)
Source: same "@Thechartcornerr" cheat sheet. Distinct category from
candlesticks (single/few-bar) -- these are built from pivot-confirmed
swing sequences over many bars. Public-domain classical TA (Edwards &
Magee / Bulkowski lineage), implemented in
indicators/chart_pattern_engine.pine (new file -- distinct source/
subject from the candlestick engine, not an extension of it).

### Implemented (well-defined swing geometry)
| Pattern | Definition | Signal |
|---|---|---|
| Double Top | two pivot highs within a tolerance band, separated by a pivot low (the "neckline") | short on neckline break |
| Double Bottom | mirror: two pivot lows within tolerance, separated by a pivot high | long on neckline break |
| Triple Top | three pivot highs within tolerance | short on neckline break |
| Triple Bottom | mirror | long on neckline break |
| Head & Shoulders | three pivot highs, middle one clearly the highest, neckline connects the two troughs between them | short on neckline break |
| Inverse Head & Shoulders | mirror (middle pivot low is the lowest) | long on neckline break |
| Ascending Triangle | flat resistance (pivot highs within tolerance) + rising support (higher pivot lows) | long on resistance break |
| Descending Triangle | flat support + falling resistance (lower pivot highs) | short on support break |
| Symmetrical Triangle | converging trendlines, one rising from higher lows, one falling from lower highs | breakout direction = signal direction |
| Rising Wedge | both trendlines rising, converging (compressing range while still climbing) | typically resolves DOWN (bearish) despite the up-slope |
| Falling Wedge | both trendlines falling, converging | typically resolves UP (bullish) despite the down-slope |
| Bull/Bear Flag | sharp impulse ("pole") followed by a short, roughly-parallel counter-sloped channel | breakout continues the pole's direction |
| Bull/Bear Pennant | sharp impulse ("pole") followed by a short converging-triangle consolidation | breakout continues the pole's direction |
| Bull/Bear Rectangle | horizontal channel (flat top AND flat bottom) | breakout direction = signal direction |

### NOT implemented -- too subjective to codify reliably
- **Cup & Handle / Inverted Cup & Handle**: requires detecting a smooth
  ROUNDED (not V-shaped) base plus a small secondary pullback "handle"
  -- no robust, unambiguous mechanical trigger exists for the rounding
  shape without curve-fitting bar-by-bar noise. Not built; flagged per
  standing rule rather than shipping an unreliable detector.
- **Diamond Top / Diamond Bottom**: a broadening structure that then
  narrows (volatility expansion then contraction) -- same problem,
  no clean swing-count trigger distinguishes a real diamond from
  ordinary chop. Not built.
Both remain documented here in case a future source specifies exact,
implementable criteria.
