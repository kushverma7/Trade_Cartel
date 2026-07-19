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

## Pending: material from user (book chapters, trader transcripts)

Every new scenario from supplied material gets:
1. an entry in this file (definition -> context -> confirmation)
2. a module in the engine (label + alertcondition, bar-close evaluation)
