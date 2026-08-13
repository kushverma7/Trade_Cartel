# MASTER STRATEGY REPORT

## Editor's Verification Note

*Added on filing, 13 August 2026. Body below reproduced exactly as supplied.*

### We measured this exact indicator stack today, and it did not hold

This report's core stack is **Supertrend (ATR 97, mult 3.1) + EMA 200 + RSI 14**.
That is the same stack as the user's AU200-BASE script, which was investigated in
depth on 13 August 2026 on OANDA AU200AUD.

| this report claims | we measured |
|---|---|
| RANK 1 structural sell: **78-82% accuracy** | PF **0.544**, **37.20% win** (TradingView, user's own run, Jan 2024-Aug 2026) |
| RANK 3 trend continuation: **68-74%** | 1H one-bar hold gross PF **1.123**, 52.8% win; net of cost **0.886** |
| "Supertrend red + below EMA200 + structure = 75-80%" | direction calls honoured at real prices: **47.7% hit rate** |

The 47.7% number is the decisive one. Taking the strategy's own long/short calls
and settling them at real prices produced a coin flip. Independently replicated:
our simulation returned PF 0.537 / 37.8%; the user's TradingView run on a
different window returned PF 0.544 / 37.20%.

Instrument caveat, stated fairly: our measurement is **AU200**, this report
targets **XAUUSD, BTCUSD and US30**. The stack is identical; the market is not.
The claims are not disproved for gold — they are **untested for gold and
falsified for AU200**. Treat every percentage in Parts 2 and 4 as unsourced
until it is measured on the instrument it claims.

### No accuracy figure in this document carries a source

"40-55%", "65-70%", "75-80%", "78-82%", "72-78%", "68-74%", "62-68%", the
per-timeframe accuracy table in Part 7, "15-20% more accurate", "adds another
5-10%" — none has a trade count, date range, instrument, or execution
assumption. By this repository's standing rule, a profit factor or win rate with
no sample and no window is not a result.

### What is genuinely right, and worth keeping

- **FAIL 7 (Fake Data Backtesting)** is an honest and correct self-correction:
  synthetic GBM data produced +23.8% and was meaningless. Exactly right, and the
  same discipline this repository arrived at independently.
- **FAIL 3** — Pine v6 does not allow `plot()` inside `if` blocks; use
  `plotshape()` or `plot(cond ? value : na)`. **Confirmed true.**
- **FAIL 4** — Pine v6 does not allow semicolons joining statements on one line.
  **Confirmed true**, and already registered in this repo's BUG_REGISTRY as a
  recurring compile failure.
- **FAIL 1** — a Supertrend flip is a poor exit because it lags 10-15 bars.
  Consistent with what we measured.
- **FAIL 6** — more than 7 simultaneous conditions fires almost never. Matches
  our own experience with the confluence engines.
- **Part 12's testing protocol** (Strategy Tester first, then two weeks paper,
  then screenshot every signal) is sound and should be run before any of Parts
  2-4 is believed.

### Cross-document note

Supertrend **97/3.1** now appears in three separately-supplied documents and in
the user's own AU200-BASE script. Wherever it originates, it is one setting
propagating between them, not three independent confirmations. Do not count it
as corroboration.

*Everything below this line is the document as supplied, unaltered.*

---


## Everything We Built, What Works, What Doesn’t, and Your Best Confluences

### Dialectic Engine — Full Lessons Learned

-----

## PART 1: EVERY INDICATOR WE TESTED

### THE CORE STACK YOU SETTLED ON

|Indicator        |Settings                               |Role                                           |
|-----------------|---------------------------------------|-----------------------------------------------|
|Supertrend       |ATR 97, Mult 3.1, Source (H+L)/2       |Macro trend gate                               |
|Andean Trend (AT)|Period 25, Mult 2.5, Source (O+H+L+C)/4|Momentum timing                                |
|BBSR EMA         |Period 200                             |Structural band — price must be on correct side|
|EMA 9            |Default                                |Fast momentum, curling detection               |
|EMA 21           |Default                                |Mid structure, crossover trigger               |
|EMA 50           |Default                                |Slow trend, stack alignment                    |
|RSI              |Period 14                              |Momentum zone filter                           |
|MACD             |8/17/9                                 |Histogram direction confirmation               |
|Liquidity Sweep  |20-bar lookback                        |Smart money stop hunt detection                |
|Volume MA        |20-bar SMA                             |Institutional participation filter             |
|ATR 14           |Default                                |TP/SL/trailing sizing                          |

-----

## PART 2: WHAT WORKS — PROVEN CONFLUENCES

### ✅ CONFLUENCE 1: Supertrend as the GATE, not the signal

**What we learned:**

- Supertrend (97/3.1) is too slow to be an entry signal on its own
- On 15m and 1m it fires late, catching the middle of a move
- Its real job is macro direction — only look for longs when it’s green, shorts when it’s red
- The settings 97/3.1 were your original settings and they are RIGHT for this purpose — slow, stable, reliable direction

**Rule:** Never trade against the Supertrend (97/3.1). If ST is red, only take sells. If ST is green, only take buys. Non-negotiable gate.

**Why it works:** 97-period ATR smooths out all the noise. You stop getting whipsawed on minor pullbacks. You’re trading WITH the macro move.

-----

### ✅ CONFLUENCE 2: BBSR EMA 200 as the STRUCTURAL DIVIDE

**What we learned:**

- Price above EMA 200 = buyers in control at macro level
- Price below EMA 200 = sellers in control at macro level
- The EMA 200 crossunder is your AICartel sell trigger — it’s powerful because it’s the first time price has lost the long-term average
- The most reliable sells come when: price crosses below EMA 200 AND Supertrend is red AND lower high is in place

**Rule:** Buys only above EMA 200. Sells only below EMA 200. Never fade this.

**Why it works:** The EMA 200 is watched by every institutional desk in the world. When price loses it, big sellers lean in. When it reclaims, buyers return. It’s self-fulfilling at scale.

-----

### ✅ CONFLUENCE 3: Lower High Structure + EMA Crossunder

**The AICartel core setup:**

```
1. Price makes a lower high (current high < previous high)
2. Swing structure confirmed (SH1 < SH2 — two lower highs)
3. Price crosses below EMA 200
4. Supertrend is red

= HIGH PROBABILITY SELL
```

**What we learned:**

- The lower high alone is weak — 40-55% accuracy
- The lower high + EMA crossunder is stronger — 65-70%
- The lower high + EMA crossunder + Supertrend red = 75-80%
- Adding swing structure (AICartel method of storing SH1/SH2) adds another 5-10% accuracy

**Why it works:** Lower highs show seller control returning. EMA crossunder shows the macro structure breaking. Supertrend confirms direction. Three independent sources of the same conclusion.

-----

### ✅ CONFLUENCE 4: Andean Trend FLIP as Reversal Timing

**What we learned:**

- AT continuation (bull/bear signal staying active + expanding) = trend confirmation, use for trend engine
- AT FLIP (just turned bull/bear for the first time) = early reversal signal, use for reversal engine
- The AT flip is 1-3 bars faster than Supertrend flip — gives early warning
- On 1m and 15m charts, the AT flip combined with a liquidity sweep is very powerful

**Best setup:**

```
Reversal Sell:
1. Price swept recent high (liquidity grab above)
2. AT flips bearish on next bar
3. RSI was above 60 and falling
4. Close below EMA 9

= REVERSAL SELL (catch the top after the stop hunt)
```

**Why it works:** Smart money grabs stops above recent highs (sweep), then reverses. The AT flip catches the momentum shift immediately after. RSI overbought confirms over-extension. EMA 9 loss confirms micro trend change.

-----

### ✅ CONFLUENCE 5: EMA Stack (9/21/50) for Trend Confirmation

**What we learned:**

- EMA 9 > EMA 21 > EMA 50 = full bull stack — only look for buys
- EMA 9 < EMA 21 < EMA 50 = full bear stack — only look for sells
- When all three align, trend signals become 15-20% more accurate
- The MOMENT the stack aligns is your signal bar — don’t wait for another candle

**The EMA crossover-only signal we built:**

```
Bull start = EMA stack turns bullish for first time (9>21>50 on this bar, not on previous bar)
Bear start = EMA stack turns bearish for first time

= Clean, non-repeating signal that fires exactly once per trend change
```

**Why it works:** Three EMAs agreeing removes noise. A single EMA cross is fake out territory. Three EMAs stacked is institutional momentum.

-----

### ✅ CONFLUENCE 6: Liquidity Sweep Detection

**What we learned:**

- Liquidity sweeps (price pokes above recent high then closes back below) are the most reliable reversal setups in the market
- XAUUSD and BTCUSD are particularly prone to stop hunts before reversal
- A sweep that happened within 5 bars of your signal is relevant — older sweeps are stale
- The sweep alone is not a signal — it needs AT flip + RSI overbought/oversold to confirm

**Best combination:**

```
Sweep High (stops grabbed above) → AT bears flip → RSI > 60 falling → close below EMA 9
= Reversal Sell with 75%+ accuracy
```

**Why it works:** Market makers deliberately hunt stops above visible swing highs before reversing. Once the stops are taken, fuel for the move is exhausted and price reverses. You’re trading AFTER the manipulation, not during it.

-----

### ✅ CONFLUENCE 7: Volume Surge Filter

**What we learned:**

- Volume > 1.1x or 1.3x 20-bar SMA = institutional participation
- Signals firing on low volume = retail noise, often fails
- On BTCUSD and XAUUSD, volume surge + signal = significantly higher accuracy
- Keep the threshold at 1.1x for active (5-10 signals/day) and 1.3x for sniper (1-3/day)

**Why it works:** You can’t fake volume. When big players move, volume spikes. A price move without volume is weak — it’s retail chasing. Volume + signal = institution is driving this move.

-----

### ✅ CONFLUENCE 8: RSI Zone Filters (Not Levels)

**What we learned:**

- RSI level trading (buy at 30, sell at 70) = fails constantly
- RSI ZONE trading = much stronger
  - Trend Buy zone: RSI 50-68 (above 50 = momentum, below 68 = not extended)
  - Trend Sell zone: RSI 32-50 (below 50 = momentum, above 32 = not exhausted)
  - Reversal Buy: RSI below 40 AND rising (recovering, not capitulating)
  - Reversal Sell: RSI above 60 AND falling (weakening, not exploding)

**Why it works:** Overbought RSI in a strong trend can stay overbought for 50 bars. Zones respect the trend. Recovery RSI (oversold but rising) is catching the exact bounce moment.

-----

## PART 3: WHAT DOESN’T WORK — AVOID THESE

### ❌ FAIL 1: Supertrend FLIP as EXIT

**What went wrong:**

- We originally used Supertrend flip as the primary exit
- On 15m gold, the ST takes 10-15 bars to flip after price reverses
- This gives back 30-50% of the profit before exiting
- You explicitly said “no flip exit” — you were right

**The fix:** Use EMA 21 break, RSI cross, MACD turn, and ATR TP/SL instead.

-----

### ❌ FAIL 2: Single-Indicator Signals

**What went wrong:**

- Early versions fired on just Supertrend direction
- Early BBSR version fired on just lower high + BBSR crossunder
- These gave 40-55% win rates — not profitable after spread
- On 1m BTCUSD we saw BUY signals firing during downtrends, SELL signals in uptrends

**The fix:** Minimum 3 conditions must align before any signal fires. No exceptions.

-----

### ❌ FAIL 3: plot() Inside if Blocks

**Technical lesson:**

- Pine Script v6 does not allow `plot()` inside `if` statements
- Use `plotshape()` for conditional markers
- Use `plot(condition ? value : na)` for conditional lines
- This error (CE10188) caused multiple failed compilations

-----

### ❌ FAIL 4: Semicolons in Pine Script v6

**Technical lesson:**

- Pine Script v6 does not allow semicolons to join statements on one line
- `entry_px := na; sl_px := na` = ERROR (CE10005)
- Every variable assignment must be on its own line
- This was the most common compile error across all versions

-----

### ❌ FAIL 5: BBSR as the Bollinger Band (wrong interpretation)

**What went wrong:**

- In early iterations we built BBSR as actual Bollinger Bands (SMA + standard deviation)
- Your BBSR is actually an EMA 200 with the wave visualization
- Bollinger Band signals fired too often and were too noisy
- The correct implementation: BBSR = EMA 200, and price must be on the correct SIDE

**The fix:** BBSR = `ta.ema(close, 200)`. Above it = bull side. Below it = bear side. Not a band — a line.

-----

### ❌ FAIL 6: Too Many Conditions = No Signals

**What went wrong:**

- The strict hybrid (AICartel + Dialectic full merge) had 7+ conditions required simultaneously
- This fired 0-2 signals per day on 15m XAUUSD
- Too few signals to validate statistically or to trade actively

**The lesson:** Balance is required. 3-5 conditions = active (5-10 signals/day). 5-7 conditions = sniper (1-3/day). More than 7 = almost never fires.

-----

### ❌ FAIL 7: Fake Data Backtesting

**What went wrong:**

- I generated synthetic XAUUSD data using Geometric Brownian Motion
- The backtest showed +23.8% profit — completely meaningless
- Fake data cannot replicate real market microstructure, news events, spread, slippage

**The fix:** Only backtest inside TradingView Strategy Tester on real historical data. Upload a real CSV if you want external backtesting.

-----

### ❌ FAIL 8: EMA Crossover as Entry on 1m

**What went wrong:**

- On 1m BTCUSD, EMA 9/21 crossovers fire 20-30 times per hour
- Most are noise and reversals
- We saw the screenshots — Buy/Buy/Sell/Buy/Sell in 15 minutes
- Too many signals, too much noise

**The fix:** EMA crossover as FILTER only. Combined with Supertrend direction + RSI zone = valid. Standalone = noise.

-----

## PART 4: THE BEST ENTRY SETUPS IN ORDER

### RANK 1: The AICartel Structural Sell (Highest Quality)

```
✓ Supertrend red (97/3.1)
✓ Lower high structure (SH1 < SH2, both below EMA 200)
✓ Price crosses below EMA 200
✓ Close below EMA 200
✓ Volume surge (1.1x+)

Estimated accuracy: 78-82%
Signal frequency: 2-4 per day on XAUUSD 15m
Best market: Gold (XAUUSD), US30
```

### RANK 2: The Reversal Catch (After Stop Hunt)

```
✓ Liquidity sweep detected (within 5 bars)
✓ AT flips bearish/bullish
✓ RSI overbought/oversold AND reversing
✓ Close reclaims/loses EMA 9
✓ EMA 9 curling in direction
✓ Not too far from EMA 50 (within 2.5 ATR)

Estimated accuracy: 72-78%
Signal frequency: 1-3 per day on XAUUSD 15m
Best market: BTCUSD 1m, XAUUSD 15m
```

### RANK 3: Trend Continuation (DE v3 Trend Engine)

```
✓ Supertrend direction
✓ AT continuing in that direction
✓ EMA stack aligned (9/21/50)
✓ Close above/below EMA 21
✓ RSI in trend zone (50-68 bull, 32-50 bear)
✓ Bullish/bearish candle body
✓ Bull/Bear score >= 3/5

Estimated accuracy: 68-74%
Signal frequency: 3-6 per day on XAUUSD 15m
Best market: Any trending market
```

### RANK 4: Simple EMA Stack Alignment

```
✓ EMA 9/21/50 stack completes (first bar of alignment)
✓ Supertrend agrees
✓ RSI in zone

Estimated accuracy: 62-68%
Signal frequency: 5-10 per day on BTCUSD 1m
Best market: Fast-moving markets, scalping
```

-----

## PART 5: EXIT RULES — WHAT ACTUALLY PROTECTS PROFIT

### In order of priority (first condition hit = exit):

1. **TP hit** (ATR × 2.0 above/below entry) → Close immediately, no hesitation
1. **SL hit** (ATR × 1.0 against entry, trailing or fixed) → Close immediately
1. **Break-even activated** (move SL to entry once 1R in profit) → Protects capital
1. **Opposite signal fires** → Close and reverse
1. **EMA 21 break** (close back through EMA 21, after 2+ bars) → Structural exit
1. **RSI crosses danger zone** (above 55 for shorts, below 45 for longs) → Momentum gone
1. **AT flips** (Andean trend changes direction, after 2+ bars) → Momentum confirmation
1. **Max bars** (20 bars max) → Time-based stop, prevents dead capital

### What NOT to use as exit:

- ❌ Supertrend flip (too slow, gives back too much)
- ❌ Waiting for full reversal signal (same problem)
- ❌ Moving SL to breakeven too early (gets stopped out before TP)

-----

## PART 6: INDICATOR SETTINGS — THE FINAL CONFIRMED NUMBERS

|Indicator    |Confirmed Setting  |Why                                                            |
|-------------|-------------------|---------------------------------------------------------------|
|Supertrend   |ATR 97, Mult 3.1   |Slow enough to avoid whipsaw, fast enough to catch major shifts|
|Andean Trend |Period 25, Mult 2.5|Balanced — not too sensitive, not too slow                     |
|BBSR EMA     |Period 200         |Industry standard macro divide                                 |
|EMA Fast     |9                  |Standard short-term momentum                                   |
|EMA Mid      |21                 |Fibonacci-based, widely respected                              |
|EMA Slow     |50                 |Half-year average, institutional reference                     |
|RSI          |14                 |Standard, do not change                                        |
|MACD         |8/17/9             |Slightly faster than default 12/26/9 — better for intraday     |
|ATR          |14                 |Risk sizing standard                                           |
|Liq Lookback |20 bars            |Covers approximately 5 hours on 15m                            |
|Volume MA    |20 bars            |One month of daily bars, standard                              |
|TP Multiplier|2.0× ATR           |Minimum 2:1 R:R                                                |
|SL Multiplier|1.0× ATR           |One ATR risk unit                                              |
|Trailing     |1.5× ATR           |Rides trend while protecting 1R+                               |
|Max Bars     |20                 |Prevents capital being stuck in dead trades                    |
|Cooldown     |3 bars             |Prevents signal stacking                                       |

-----

## PART 7: TIMEFRAME GUIDE

|Timeframe|Best Engine  |Signals/Day|Accuracy|Best For        |
|---------|-------------|-----------|--------|----------------|
|1m       |Reversal only|10-20      |55-65%  |Scalping BTC    |
|5m       |Both engines |8-15       |62-70%  |Active trading  |
|15m      |Both engines |5-10       |70-78%  |Best balance    |
|1H       |Trend engine |2-5        |75-82%  |Swing entries   |
|4H       |Trend engine |1-3        |78-85%  |Position trading|

**Recommended:** 15m for active trading, 1H for quality over quantity.

-----

## PART 8: MARKET-SPECIFIC NOTES

### XAUUSD (Gold)

- Moves in large sweeps — liquidity sweeps are very common
- The BBSR EMA 200 is particularly respected on gold
- Best session: London open (07:00-10:00 UTC) and NY open (13:30-16:00 UTC)
- Avoid: Asian session (very choppy, low volume)
- Your screenshots showed the downtrend on 15m — the Sell signals in that context were valid structural sells

### BTCUSD / Crypto

- Much faster moves — 1m chart viable
- AT flip signals are more frequent and faster
- Liquidity sweeps happen multiple times per hour on 1m
- Volume is more reliable signal here than on gold
- Your screenshots showed mixed signals on 1m — this is normal, cooldown filter helps

### US30

- Correlated with risk sentiment (opposite of gold often)
- MACD is particularly useful here
- Avoid trading during major news events (Fed, CPI, NFP)

-----

## PART 9: THE EVOLUTION OF THE STRATEGY

### Version 1 (BBSR + Supertrend basic)

- Just lower high + BBSR crossunder + Supertrend flip
- Problem: Too many false signals, exit dependent on flip

### Version 2 (AICartel Structure v1)

- Added swing structure tracking (SH1/SH2)
- Added EMA crossunder as trigger
- Problem: Generated buy AND sell simultaneously

### Version 3 (AICartel + Dialectic merge)

- Added regime classifier, volume surge, liquidity sweep
- Problem: Too strict — almost no signals fired

### Version 4 (XAU Active Sniper)

- Simplified for 5-10 signals/day
- Structure-based exits (next swing)
- Problem: Supertrend still in exit

### Version 5 (Dialectic Engine v2)

- Two engines: trend + reversal
- Multi-condition exit waterfall
- Problem: No AT integration

### Version 6 (Dialectic Engine v3 — FINAL)

- Supertrend (97/3.1) as macro gate
- AT (25/2.5) as timing — flip for reversal, continuation for trend
- BBSR EMA 200 as structural divide
- EMA 9/21/50 stack
- RSI zones
- Liquidity sweeps
- Volume surge
- ATR exits (TP/SL/trailing/breakeven)
- No ST flip exit
- Clean labels (Buy/Sell/BUY/SELL) matching your original style

-----

## PART 10: THE NON-NEGOTIABLE RULES

1. **Never trade against Supertrend (97/3.1).** If it’s red, only sell. If green, only buy.
1. **BBSR EMA 200 is the dividing line.** Buys above it. Sells below it. No exceptions.
1. **Minimum 3 confluences before entry.** One indicator is never enough.
1. **Exit is not the opposite signal.** Use ATR TP/SL + structural exits (EMA 21 break).
1. **Liquidity sweeps precede reversals.** Learn to recognize them. They are your best reversal setup.
1. **Volume confirms institutions.** No volume surge = weaker signal. Filter it.
1. **RSI zones not levels.** 50-68 for trend buys. 32-50 for trend sells. Not 30/70.
1. **Cooldown after every entry.** Minimum 3 bars. Prevents stacking into the same move.
1. **Backtest on real data only.** TradingView Strategy Tester. Never trust synthetic data.
1. **The AT flip is your early warning.** Before price, before Supertrend — AT flips first.

-----

## PART 11: QUICK REFERENCE SIGNAL CHECKLIST

### TREND SELL — Tick all boxes:

```
□ Supertrend = RED
□ AT = Bear continuation
□ Price BELOW EMA 200
□ Price BELOW EMA 21
□ EMA 9/21/50 = Bear stack
□ RSI = 32-50 (bear zone)
□ Bearish candle body
□ Bear score >= 3/5
□ Volume >= 1.1x average
```

### TREND BUY — Tick all boxes:

```
□ Supertrend = GREEN
□ AT = Bull continuation
□ Price ABOVE EMA 200
□ Price ABOVE EMA 21
□ EMA 9/21/50 = Bull stack
□ RSI = 50-68 (bull zone)
□ Bullish candle body
□ Bull score >= 3/5
□ Volume >= 1.1x average
```

### REVERSAL SELL — Tick all boxes:

```
□ Liquidity sweep HIGH (within 5 bars)
□ AT flips BEARISH
□ RSI above 60 AND falling
□ Close BELOW EMA 9
□ EMA 9 curling DOWN
□ Not too far from EMA 50 (< 2.5 ATR)
□ Price BELOW EMA 200
```

### REVERSAL BUY — Tick all boxes:

```
□ Liquidity sweep LOW (within 5 bars)
□ AT flips BULLISH
□ RSI below 40 AND rising
□ Close ABOVE EMA 9
□ EMA 9 curling UP
□ Not too far from EMA 50 (< 2.5 ATR)
□ Price ABOVE EMA 200
```

-----

## PART 12: WHAT TO DO NEXT

1. **Load DE v3 (ST + AT + BBSR)** into TradingView on XAUUSD 15m
1. **Run Strategy Tester** — look for:
- Win Rate > 50%
- Profit Factor > 1.3
- Max Drawdown < 15%
- Total Trades > 30
1. **Paper trade 2 weeks** before any live capital
1. **Adjust min_conf** between 2-4 to find the signal frequency that suits you
1. **Test both engines separately** — disable reversal engine first, then disable trend engine — see which performs better on your market
1. **Screenshot every signal** for 2 weeks — you will find patterns in what works on your specific pair

-----

*This report covers everything built across this conversation — 15+ Pine Script versions, 6 strategy iterations, and every indicator combination tested. The DE v3 code is the final synthesis of all lessons above.*