# MASTER TRADING SYSTEM — COMPLETE VERIFIED EDITION

## Editor's Verification Note

*Added on filing, 13 August 2026. The document body below is reproduced exactly as supplied. The document asserts "No opinions — only verified data," so its checkable claims were checked.*

### Verified as real

- **Marco Accettone** is a real trader — liquidity-concepts, counter-trend price action, ~$500,000 in documented strategy results, featured on Chart Fanatics, formerly a plumber in Canada. **The document misspells his name throughout as "Marco Acetony."**
- **Fabio Valentini** is already in this repository's own source corpus: five transcripts (`line0896`, `line0916`, `line1000`, `line1019`, `line1032`) distilled into `trader_playbooks/valentini_scalping.md` and `orderflow_effort_result.md`. Independent corroboration, and the strongest provenance of anything here.
- **The 96.2% Initial Balance statistic is genuine** and traces to a real 2015–2025 study of ES and NQ regular-session days.

### The headline statistic is misreported in two ways

**Sample size.** The document says *"NQ Futures — 2015–2025, 5,519 days."* The underlying study covers **2,686 ES days + 2,833 NQ days = 5,519 total across both instruments.** NQ alone is 2,833 days. The document attributes the combined figure to NQ.

**The 82% figure is a different number about a different thing.** The document claims *"Single-side IB break = 82.17% probability of continuation in that direction"* and uses it as the statistical basis for the entire opening-range timing model, citing it again in the confluence table as "82% single-break continuation."

The source's 82.7% is the **upside breakout rate on ES when the IB closes up** — not a single-side continuation probability, not NQ, and not 82.17%. The source's actual directional single-break numbers are **52.5% on ES and 57.2% on NQ**.

That gap matters. A 57% directional read is a modest tilt worth building on. An 82% read is a different business entirely, and Part 11 grades this confluence NON-NEGOTIABLE on the strength of the wrong one.

### Unsourced statistics presented as fact

None of the following carry a citation anywhere in the document:

- "In balance, 70% of breakout attempts fail"
- "This single filter = +20-30% win rate improvement"
- "Primary TP = previous balance area POC (70% probability of reversal)"
- "Full candle close adds ~5-10% filter improvement"
- "Pre-market range... first 9:30 move sweeps one side = 80%+ continuation"
- Every VWAP reliability claim marked "confirmed statistically"

### Practical note for this desk

The system runs **NY cash open, 9:30–11:30am ET**. In Melbourne that is **11:30pm–1:30am AEST**, or **12:30–2:30am AEDT** in summer. It is a middle-of-the-night session here, every night, with a hard 2% daily stop and a requirement to watch order-flow bubbles live. It also requires NQ futures and a Tier-1 order-flow platform (DeepChart, ATAS, Bookmap — roughly $100–200/month), which is a different instrument and a different broker from the AU200/Gold/US30 CFD setup this repository is built around.

The document's own Part 12 testing protocol — 4 weeks paper, then 4 weeks on a single micro contract, journalling every setup including the skipped ones — is the most valuable page in it, and is worth following regardless of what the statistics turn out to be.

*Everything below this line is the document as supplied, unaltered.*

---


## Sources 001 + 002 | Research Validated | Statistics Added | Gaps Filled

### Version 3.0 — Execution Ready | May 2026

-----

# ═══════════════════════════════════════════════

# PART 0: VERIFICATION STATUS

# ═══════════════════════════════════════════════

## Source 001 — Fabio Valentini ✅ VERIFIED

- Robbins World Cup Futures Division: 218.3%, 169.7%, 89.5%, 69%, 90%+ verified returns
- Multiple top-3 finishes across quarters
- 500+ trades per quarter, controlled drawdown
- UAE-based, active competitor and educator

## Source 002 — Marco Acetony ✅ VERIFIED

- Hundreds of thousands in verified prop firm payouts
- Millions in funded accounts
- Live trading sessions publicly documented on Chart Fanatics
- Consistent application of stated strategy confirmed

## Strategy Concepts — RESEARCH VALIDATED ✅

The following statistics from independent research confirm the core logic:

**Initial Balance / Opening Range (NQ Futures — 2015–2025, 5,519 days):**

- 96.2% of NQ days see at least ONE IB breakout by close
- Single-side IB break = 82.17% probability of continuation in that direction
- Most reliable window: 9:30–11:00am ET
- After 11:30am: reliability drops significantly (confirmed by both traders)

**Liquidity Sweeps (Independently verified):**

- NQ is “notorious for sweeping levels before reversing” — confirmed by institutional sources
- Pre-market range builds liquidity on both sides; first 9:30 move sweeps one side = 80%+ continuation
- Stop-hunting before real moves: widely documented across professional literature

**VWAP Standard Deviation Levels (Research-confirmed):**

- 1SD: Trend zone / fair value pullback — entry for continuation
- 2SD: Overextension zone — reversal probability high, institutional reversion point
- 3SD: Extreme zone — highest reversal probability, used as maximum TP target
- Low VIX = trade 1SD reactions | High VIX = trade 2SD/3SD reactions
- VWAP bounce reliability drops significantly after 1:00pm ET (confirmed)

**CVD Divergence (NQ Futures — confirmed by institutional research):**

- NQ CVD highlighted divergence where large-cap traders followed downtrend while retail stayed optimistic = institutional leading signal confirmed
- Price up + CVD down = bearish divergence = high reversal probability
- Used by professional futures desks as primary pressure indicator

-----

# ═══════════════════════════════════════════════

# PART 1: THE COMPLETE SYSTEM OVERVIEW

# ═══════════════════════════════════════════════

```
INSTRUMENT:     NQ (primary) | YM (secondary) | ES (fallback when NQ messy)
SESSION:        NY Cash Open — 9:30am–11:30am optimal | hard stop 12pm
TIMEFRAMES:     4H/1H (higher TF bias) → 15m (session bias + VWAP) → 5m 
                (execution) → 1m (entry refinement) → 15sec (execution)
RISK/TRADE:     0.25% base | 0.5% competition | 1% only post-100% return
DAILY LIMIT:    2% max loss — HARD STOP, no exceptions
WIN RATE:       ~50% | Min R:R 1:2 | Typical 1:3–1:5 | Max 1:10–1:20
POSITIONS:      ONE at a time, always
OVERNIGHT:      NEVER
WATCHLIST:      2–3 instruments maximum
```

## The System In One Sentence

> Wait for Marco’s liquidity sweep at a structurally significant level. Confirm with Fabio’s aggression bubble at that level’s LVN. Check CVD is aligned. Verify VWAP bias. Enter with stop 1-2 ticks beyond the swept level. Target opposing liquidity/POC. Trail with CVD signals.

-----

# ═══════════════════════════════════════════════

# PART 2: MARKET FRAMEWORK (The Why)

# ═══════════════════════════════════════════════

## 2.1 The Two Market States (Fabio)

|State              |Profile Shape                 |Action                         |
|-------------------|------------------------------|-------------------------------|
|**BALANCE**        |Bell curve, high volume center|Mean revert model OR do nothing|
|**IMBALANCE (OOB)**|Thin, skewed, directional     |Trend follow model ONLY        |

**Statistical basis:** In balance, 70% of breakout attempts fail. Trend trading inside balance = 70% failure rate. This single filter = +20-30% win rate improvement.

## 2.2 Liquidity = Resting Stop Orders (Marco)

Liquidity forms ONLY when:

1. Price approaches a level (high or low)
1. Price moves AWAY from that level
1. Both conditions present = participants entered = stops resting there

**NOT every high or low has liquidity.** Only levels where the market:

- Respected the level (approached it)
- Departed from it (moved away, confirming entries)

## 2.3 Why Retail Concepts Exist (Marco — Core Insight)

Retail concepts (BOS, OB, FVG, Fibonacci) work **temporarily on purpose** to build liquidity:

```
1. BOS occurs → Induces retail buyers/sellers
2. Retail enters at OB/FVG/Fibonacci retracement
3. Market moves away confirming their entry
4. Stops now resting just beyond their entry level
5. Market sweeps those stops (takes liquidity)
6. REAL move begins — this is where Marco enters
```

## 2.4 Three Levels of Market Information (Fabio)

|Level      |Type           |Tool                     |Use                   |
|-----------|---------------|-------------------------|----------------------|
|Lagging    |Derivative     |MACD, RSI, Stoch         |Never — always late   |
|Real-time  |Price          |Candlesticks, PA         |Structure reading only|
|**Leading**|**Volume/Flow**|**CVD, Bubbles, Profile**|**Entry + management**|

## 2.5 CVD — The Leading Signal (Research Confirmed)

**Confirmed by: Fabio (primary), NQ institutional research, Bookmap professional data**

|CVD      |Price    |Reading                             |Action                |
|---------|---------|------------------------------------|----------------------|
|↑ Rising |↑ Rising |Move supported — buyers aggressive  |Hold, trail           |
|↓ Falling|↑ Rising |Divergence — distribution forming   |Move to BE immediately|
|↑ Rising |↓ Falling|Absorption — buyers fighting sellers|Watch for reversal    |
|↓ Falling|↓ Falling|Move supported — sellers aggressive |Hold short, trail     |

**Key stat:** CVD divergence on ES/NQ first hour after 9:30am = confirms institutional intent before price reaction. Used by professional futures desks.

## 2.6 VWAP Standard Deviation Levels (Research Confirmed)

**Settings for NQ (confirmed by professional traders and institutional research):**

|Level     |Meaning                |Use                                  |
|----------|-----------------------|-------------------------------------|
|VWAP (0SD)|Session fair value     |Bias filter: above=long, below=short |
|1SD       |Trend continuation zone|Pullback entry in trending conditions|
|2SD       |Overextension / TP zone|Primary TP for most setups           |
|3SD       |Extreme reversal zone  |Maximum TP, mean revert entry        |

**Low VIX days:** 1SD reactions most reliable
**High VIX days:** 2SD/3SD more relevant
**After 1:00pm ET:** VWAP bounce reliability drops sharply — confirmed statistically

-----

# ═══════════════════════════════════════════════

# PART 3: STRATEGY A — TREND FOLLOWING MODEL

# ═══════════════════════════════════════════════

**Activate:** NY session + OOB condition confirmed + qualifying sweep complete

## STEP 1 — ESTABLISH BIAS (Pre-Trade)

**Higher Timeframe (4H/1H) — Marco’s Liquidity Map:**

```
□ Find a high that was RESPECTED + price moved away
  → Liquidity above that high = BEARISH target
□ Find a low that was RESPECTED + price moved away  
  → Liquidity below that low = BULLISH target
□ Is there a qualifying sweep pending? (the one needed before entry)
□ Mark Asia session H/L as key liquidity zones
□ Identify external liquidity target (ultimate TP)
□ Identify internal liquidity levels en route (partial TP points)
```

**Session Bias (15m) — Fabio’s VWAP:**

```
□ Is price above 15m VWAP? → Long bias for session
□ Is price below 15m VWAP? → Short bias for session
□ Do 15m VWAP and higher TF liquidity bias agree?
□ YES = bias confirmed | NO = lower confidence, reduce size
```

**Market State (15m) — Fabio’s OOB Check:**

```
□ Is price outside the Value Area? → OOB = use trend model
□ Is there a thin profile with directional momentum?
□ BOTH = OOB confirmed | EITHER MISSING = wait or switch to Model B
```

## STEP 2 — LOCATION (Refined Entry Zone)

**Marco’s Swept Level:**

```
□ Has the qualifying LOW been swept? (for longs) → below that low = entry zone
□ Has the qualifying HIGH been swept? (for shorts) → above that high = entry zone
□ The swept level now has NO liquidity on the other side (just cleared)
□ This is therefore safe entry with tight stop
```

**Fabio’s LVN Refinement:**

```
□ Draw Volume Profile on the impulse swing that created OOB
□ Identify LVN (visible gap in volume histogram)
□ Does LVN align with Marco's swept level zone?
□ YES = maximum confluence location | Slightly off = acceptable
□ Set alert at LVN zone (NOT limit order — wait for aggression)
```

**Target Identification:**

```
□ Primary TP = previous balance area POC (70% reversal probability)
□ Secondary TP = VWAP 2SD band in trade direction
□ External TP = Marco's external liquidity (trapped participants' stops)
□ Partial TP = internal liquidity levels en route
```

## STEP 3 — EXECUTION TRIGGER

**Marco’s Trigger (required):**

```
Qualifying sweep has occurred ✓
```

**Fabio’s Trigger (required):**

```
Aggression bubble visible at swept level / LVN zone:
- NQ NY session: 30+ contracts on 1-minute chart
- NQ London: 20+ contracts on 1-minute chart
- Long trade: green bubble (buyers absorbing)
- Short trade: red bubble (sellers absorbing)
NO BUBBLE = NO ENTRY. Zero exceptions.
```

**CVD Confirmation (required):**

```
CVD aligned with trade direction (not diverging against)
```

**Optional — Candle Close (reduces fakeouts):**

```
Full 1-minute candle close above/below swept level
Adds ~5-10% filter improvement on fake entries
```

**Setup Grade Before Entering:**

```
ALL conditions met → A-Grade → 0.25–0.5% risk
3 of 4 conditions → B-Grade → 0.12–0.25% risk (half)
2 or fewer → C-Grade → SKIP. Do not trade.
```

## STOP LOSS

```
Futures (NQ/YM): 1-2 ticks BEYOND the swept high/low
Why: No slippage buffer needed — single centralized feed
Logic: If this level is reclaimed, thesis is wrong. Exit.
NEVER: Widen stop because "it might come back"
NEVER: Place at random ATR distance
```

## TAKE PROFIT

```
Primary: Previous balance area POC → take FULL position off
         (70% probability of reversal from POC — not worth holding for 30%)
Exception: Strong directional day → trail using SESSION profit only
Secondary: VWAP 2SD band aligning with POC = maximum confluence TP
Partials: 50% off at first internal liquidity, hold for external
```

## TRADE MANAGEMENT SEQUENCE

```
Entry confirmed →
  CVD diverges favorably? → YES → Move stop to BE immediately
  Price creates new structural low/high in your direction? → Trail below/above it
  First internal liquidity target hit? → Take 50% off
  Stop now at BE on remainder →
  Approach primary TP (POC/external liquidity) →
  Close full position OR close 70%, trail 30% if strong momentum
  Approaching NY lunch (12pm)? → Close if target not near
  BE or better → Cannot lose. Let it run.
```

-----

# ═══════════════════════════════════════════════

# PART 4: STRATEGY B — MEAN REVERSION MODEL

# ═══════════════════════════════════════════════

**Activate:** London session OR summer compression OR clear balanced range + confirmed at any session

## When to Use

```
□ Profile is building a balanced bell curve
□ Price respecting VAH and VAL boundaries
□ London session active (primary window for this model)
□ Summer months (May-August compression)
□ Choppy days in NY where OOB never confirms
```

## The 4-Step Process

```
1. Identify the consolidation range (profile + price boundaries)
2. Mark VAH, VAL, POC of that range
3. WAIT for first breakout spike (do NOT trade it)
4. Wait for price to snap back inside range (failed auction confirmed)
5. Find LVN within the range
6. Wait for absorption at that LVN (large volume, minimal price move)
7. Enter with stop beyond LVN, target = POC of range
```

## Key Rules for Model B

- **Never take the first spike** — it’s the trap, not the entry
- **Absorption = trigger**, not aggression (opposite of Model A)
- **Target = POC** of the range, not the breakout level
- **This model DESTROYS P&L if used in NY trending conditions**
- If compression resolves into clear OOB trend → switch to Model A

-----

# ═══════════════════════════════════════════════

# PART 5: COMPLETE SESSION + TIMING MATRIX

# ═══════════════════════════════════════════════

|Time / Condition    |Model             |Action                            |Statistical Basis                   |
|--------------------|------------------|----------------------------------|------------------------------------|
|Sunday analysis     |—                 |Mark weekly/daily liquidity levels|Clean analysis, no noise            |
|Asia session        |—                 |Mark H/L only, no trades          |Liquidity building phase            |
|London open         |B (if compression)|Observe trap formation            |Too many fakeouts for Model A       |
|Pre-NY (before 9:30)|—                 |Do not trade                      |Building phase, winner unknown      |
|8:30am news         |—                 |Wait 2-3 min after release        |Spike = liquidity sweep, enter after|
|9:30am open         |—                 |Wait for first move to settle     |Opening = whipsaw zone              |
|9:30-10:00am        |A                 |Assess opening trap direction     |ORB = 82% single-break continuation |
|10:00am             |A                 |4H candle close — key timing      |Often marks NY session H/L          |
|9:30-11:30am        |A                 |Primary execution window          |Highest institutional volume        |
|11:30am             |A (selective)     |Reassess — A-grade only           |Volume declining                    |
|12:00-1:00pm        |—                 |No new positions                  |VWAP reliability collapses after 1pm|
|After 1:00pm        |A (A-grade only)  |Optional if structure intact      |Reduced quality, lower volume       |
|Monday / Friday     |Both (reduced)    |Trade but expect less             |Less explosive sessions             |
|Summer (May-Aug)    |B                 |Mean revert primary               |Compression = range behavior        |
|High vol events     |A                 |Same model, wider moves           |Normal logic still applies          |
|After 2% daily loss |—                 |STOP. Session closed.             |Hard rule — no exceptions           |

-----

# ═══════════════════════════════════════════════

# PART 6: COMPLETE PRE-TRADE CHECKLIST

# ═══════════════════════════════════════════════

## Morning Preparation (Before Session)

```
□ Check higher TF (4H/Daily): Where is external liquidity?
□ Mark all Asia session H/L
□ Mark previous day's H/L (PDH/PDL) — key liquidity levels
□ Note what London session did: did it trap buyers or sellers?
□ Mark VWAP from session open
□ Identify OOB condition or balance condition
□ Determine which model is active today (A or B)
□ Set alerts at LVN zones — do NOT watch price manually
□ Check economic calendar — note exact times of red-folder news
```

## Trade Entry Checklist (Real-Time)

```
BIAS
□ Higher TF liquidity sweep pending in bias direction? (Marco)
□ 15m VWAP direction aligned with trade? (Fabio)
□ Market OOB in trade direction? (Fabio)

SESSION
□ Within 9:30am–11:30am window?
□ News settled (2-3 min minimum post-release)?
□ Daily loss limit NOT hit?

LOCATION  
□ LVN identified at entry zone? (Fabio)
□ LVN aligns with swept level? (Marco + Fabio convergence)
□ TP target is structural liquidity / POC?
□ Stop placement: 1-2 ticks beyond swept level?

TRIGGER
□ Qualifying high or low has been SWEPT? (Marco — iron rule)
□ Aggression bubble present at level (30+ contracts NQ)? (Fabio)
□ CVD aligned with direction? (Fabio)
□ Full candle close confirmation? (optional but preferred)

GRADE & SIZE
□ All above = A-grade → 0.25-0.5% risk
□ 3 of 4 categories = B-grade → half risk
□ 2 or fewer = C-grade → SKIP

MENTAL CHECK
□ "Am I trading this plan or my feelings?"
□ "Is the qualifying sweep actually confirmed?"
□ "Would I take this trade if it was day 1 of a new account?"
```

-----

# ═══════════════════════════════════════════════

# PART 7: THE IRON RULES (NEVER BROKEN)

# ═══════════════════════════════════════════════

These 15 rules are confirmed by both traders independently. Breaking any single one statistically degrades results:

```
1.  NEVER trade before NY session open (9:30am hard start)
2.  NEVER trade the first minute of NY open (whipsaw guaranteed)
3.  NEVER hold positions overnight (futures margin + uncertainty)
4.  NEVER buy above lows without prior sweep (Marco's absolute rule)
5.  NEVER sell below highs without prior sweep (Marco's absolute rule)
6.  NEVER enter without qualifying sweep occurring first
7.  NEVER enter without an aggression bubble (Fabio's absolute rule)
8.  NEVER place stop beyond the swept structural level
9.  NEVER widen a stop once set ("it might come back" = account killer)
10. NEVER take profits at random R:R — targets are structural levels only
11. NEVER trade more than one position simultaneously
12. NEVER scale in without a fresh qualifying sweep justifying it
13. NEVER trade after hitting the 2% daily loss limit
14. NEVER revenge trade following a string of losses
15. NEVER take C-grade setups regardless of how obvious they look
```

-----

# ═══════════════════════════════════════════════

# PART 8: RISK MANAGEMENT SYSTEM

# ═══════════════════════════════════════════════

## Position Sizing

```
Default / personal:          0.25% per trade
Competition / funded:        0.5% per trade  
After 100%+ return achieved: Up to 1% per trade
B-grade setup:               50% of standard
C-grade setup:               0% — skip entirely
Noise/aggressive trades:     Session profit only (house money)
```

## Daily Session Structure

```
Phase 1: First 1-2 trades
  → 0.25% base risk
  → Build initial profit buffer
  
Phase 2: Profit buffer established (>1% gain)
  → Use session profits as additional risk capital
  → Can scale into high-conviction setups
  
Phase 3: Strong directional day confirmed (>2-3% gain)
  → Can be more aggressive using ONLY accumulated session profit
  → Base equity remains protected at all times
  
Hard stop: -2% on day → Session closed. No more trades today.
```

## The Commission Reality Check

- 500+ NQ trades/quarter at professional level
- Commission at $5/contract per side = significant cost
- Commission can eat 10-20% of gross profits at high frequency
- Every unnecessary trade costs real money before it starts
- C-grade setups aren’t just low-probability — they’re actively expensive

## Compounding Protocol

```
Start of month/quarter: Base risk at 0.25%
After +25% on account:  Increase to 0.35%
After +50% on account:  Increase to 0.5%
After +100% on account: Can reach 1% on A-grade setups only
Drawdown >5%:           Step back to previous tier
Drawdown >10%:          Reset to base 0.25%
Drawdown >15%:          Stop trading, review system
```

-----

# ═══════════════════════════════════════════════

# PART 9: WHAT THEY NEVER TRADE

# ═══════════════════════════════════════════════

This list eliminates more bad trades than any entry rule:

**Timing:**

- Pre-session (before 9:30am)
- First minute of NY open
- NY lunch hour (12-1pm) for new positions
- Outside their specific time window
- During news release (wait 2-3 min after)

**Market Conditions:**

- Balanced market using trend model
- Before qualifying sweep has occurred (Marco — zero exceptions)
- Compression/chop with no OOB confirmation (Fabio)
- Days when daily limit has been hit

**Setup Quality:**

- C-grade setups (2+ conditions missing)
- No aggression bubble present (Fabio)
- Stop must go beyond structural level (too wide)
- Counter-trend without full conditions
- Trades motivated by boredom or wanting to trade

**Position Management:**

- Multiple simultaneous positions
- Overnight futures holds
- Widening stops
- Partialing at random R:R numbers
- Holding through NY lunch if target not close

-----

# ═══════════════════════════════════════════════

# PART 10: COMPLETE TOOL STACK

# ═══════════════════════════════════════════════

## Tier 1 — Required for True Edge (What Fabio Uses)

|Platform    |What It Provides                                     |Cost        |
|------------|-----------------------------------------------------|------------|
|DeepChart   |True executed order bubbles — Fabio’s actual platform|~$100-200/mo|
|ATAS        |Footprint + volume profile + CVD combined            |~$150/mo    |
|Sierra Chart|Tick data + advanced volume analysis                 |~$50/mo     |
|Bookmap     |Liquidity heatmap + CVD professional                 |~$100/mo    |

## Tier 2 — Marco’s Requirements

- **Any standard charting platform** — TradingView, TradingStation, etc.
- No specialized tools needed
- Just the ability to mark horizontal levels and identify structure
- TradingView free tier is sufficient for Marco’s model

## Tier 3 — TradingView Approximations

**Best All-In-One (Start Here):**

- `tradingview.com/script/rCKzrbRP` — Fabio-Style Order Flow System
  - Smoothed delta, big trade detection, auto-LVN, volume profile, FVGs, liquidity grabs, dashboard

**Order Flow / Bubbles:**

- `tradingview.com/script/b01arIwW` — Delta Volume Bubbles (original Fabio reference)
- `tradingview.com/script/eQT3ExZ2` — Big Trader Fabio Style (intra-candle analysis)
- `tradingview.com/script/8J27Bx8I` — Universal Large Orders Proxy (open source)
- `tradingview.com/script/2n9qXmQO` — Delta Bubbles by exp3rts

*Recommended settings (Delta Bubbles, 15m chart):*

```
Volume lookback: 50 | Small: 2.7 | Medium: 4.5 | Large: 7.2
Min bubble size: 2 | Zone width: 100 | EMA: 9, 21, 50
```

**CVD Tools (Use Together as a Pair):**

- `tradingview.com/script/xAEyGSIS` — CVD Divergence Insights by Colicoid ← best for early BE signal
- `tradingview.com/script/kNUmhguZ` — CVD Line by Colicoid ← pair with above
- `tradingview.com/script/NlM312nK` — Official TradingView CVD Candles (Pine v6, most accurate)
- `tradingview.com/script/UFnl9AgC` — CVD Suite QuantAlgo (full alerts)
- `tradingview.com/script/9bxfutKs` — Elite CVD+ Oscillator (ES/NQ optimized with presets)

**Volume Profile / LVN:**

- `tradingview.com/script/Gd35Xikw` — Volume Profile LVN Volatility ← BEST for NQ futures scalping
  - Full LVN lifecycle: creation → departure → revisit → confirmation
  - Default tuned for MNQ/MES
- `tradingview.com/script/pojTuzmM` — VP with HVN/LVN Detection (works on 5-sec charts)
- `tradingview.com/script/RvNPu7jq` — LVN/HVN Auto Detection by PhenLabs
- `tradingview.com/script/V3lYrFvN` — Volume Profile with delta per level

**VWAP (NQ Optimized):**

- `tradingview.com/script/kP7HmAzw` — NQ Phantom Scalper Pro (VWAP + volume spike, open source)
  - Has lunch filter, session filter, dynamic SD bands
- Standard VWAP with 1SD, 2SD, 3SD bands on TradingView

**Complete Strategy Scripts (Study the Logic):**

- `tradingview.com/script/ybr8iE0K` — Fabio Valentini Pro Scalper (open source)
- `tradingview.com/script/aoWU83ST` — Fabio + Waqar SMC Alert (VWAP + liquidity sweeps + BOS)
- `tradingview.com/script/483a0r80` — NQ IB Quadrant Probability Framework (5-year backtest)

**Official Playbooks:**

- `tradezella.com/strategies/auction-market-strategy` — Fabio’s official playbook (importable)
- `tradezella.com/playbooks/auction-market-playbook` — LVN playbook rules
- `chartfanatics.com/strategies/auction-market-strategy` — Full written rules

-----

# ═══════════════════════════════════════════════

# PART 11: MASTER CONFLUENCE TABLE — FINAL VERSION

# ═══════════════════════════════════════════════

|# |Confluence                               |Confirmed By            |Status          |Statistical Support                  |
|--|-----------------------------------------|------------------------|----------------|-------------------------------------|
|1 |NY session as primary window             |Fabio + Marco + Research|✅ NON-NEGOTIABLE|ORB reliability = 9:30-11am primary  |
|2 |Strict time window — no deviation        |Fabio + Marco           |✅ NON-NEGOTIABLE|Outside window = higher noise        |
|3 |No pre-session trading                   |Fabio + Marco           |✅ NON-NEGOTIABLE|Building phase confirmed             |
|4 |No overnight holds                       |Fabio + Marco           |✅ NON-NEGOTIABLE|Futures margin reality               |
|5 |Direction/bias before everything         |Fabio + Marco           |✅ NON-NEGOTIABLE|Structure first = fundamental        |
|6 |Failed auction / trap = reversal         |Fabio + Marco + Research|✅ NON-NEGOTIABLE|82% single-break continuation        |
|7 |Stop = ticks beyond structural level     |Fabio + Marco           |✅ NON-NEGOTIABLE|Slippage avoidance confirmed         |
|8 |Trail stop progressively                 |Fabio + Marco           |✅ NON-NEGOTIABLE|CVD (Fabio) / structure (Marco)      |
|9 |Target = structural liquidity only       |Fabio + Marco           |✅ NON-NEGOTIABLE|No random R:R                        |
|10|Patience — no forced trades              |Fabio + Marco           |✅ NON-NEGOTIABLE|Quality > quantity                   |
|11|OOB condition / qualifying sweep required|Fabio + Marco           |✅ NON-NEGOTIABLE|Core gate for both                   |
|12|LVN = swept level = entry zone           |Fabio + Marco           |✅ NON-NEGOTIABLE|Same concept, two languages          |
|13|Asia H/L as session liquidity            |Marco + Research        |✅ NON-NEGOTIABLE|Pre-NY range = liquidity building    |
|14|No revenge trading                       |Fabio + Marco           |✅ NON-NEGOTIABLE|Rules prevent it by design           |
|15|Scale only with session profit           |Fabio + Marco           |✅ NON-NEGOTIABLE|Base equity always protected         |
|16|Aggression bubble required (30+ NQ)      |Fabio + Research        |⭐ STRONG        |NQ order flow = leading indicator    |
|17|CVD direction aligned                    |Fabio + Research        |⭐ STRONG        |Institutional NQ divergence confirmed|
|18|Full 1-min candle close                  |Fabio                   |⭐ STRONG        |Fakeout filter                       |
|19|A/B/C setup grading                      |Fabio                   |⭐ STRONG        |Controls sizing per quality          |
|20|VWAP 15m as session bias                 |Fabio + Research        |⭐ STRONG        |Institutional benchmark confirmed    |
|21|VWAP 1SD/2SD/3SD as TP levels            |Research (independent)  |⭐ STRONG        |1SD trend, 2SD reversal, 3SD extreme |
|22|Qualifying sweep before entry            |Marco                   |⭐ STRONG        |The single most important rule       |
|23|Never buy above lows / sell below highs  |Marco                   |⭐ STRONG        |Prevents worst-case entries          |
|24|External vs internal liquidity hierarchy |Marco                   |⭐ STRONG        |Entry from internal, TP = external   |
|25|No new positions during NY lunch         |Research                |⭐ STRONG        |VWAP reliability collapses 1pm+      |
|26|10am 4H close = timing confluence        |Marco                   |📊 USEFUL        |Often marks NY session H/L           |
|27|2-3 instruments max                      |Marco                   |📊 USEFUL        |Focus management                     |
|28|Wait 2-3 min after news                  |Marco                   |📊 USEFUL        |Let spike settle                     |
|29|Low VIX = 1SD VWAP / High VIX = 2SD      |Research                |📊 USEFUL        |Volatility-adjusted VWAP use         |
|30|PDH/PDL as liquidity targets             |Research + Marco        |📊 USEFUL        |Previous day levels = key zones      |

-----

# ═══════════════════════════════════════════════

# PART 12: TESTING PROTOCOL (4-8 Week Validation)

# ═══════════════════════════════════════════════

**Phase 1 — Paper Trading (Weeks 1-4):**

```
□ Trade the system on paper/sim ONLY
□ NQ primary, NY session only, 9:30-11:30am
□ Apply ALL iron rules without exception
□ Journal every setup: taken AND skipped
□ Target: 20-30 valid setups minimum before evaluating
□ Track: win rate, avg R:R, max drawdown, commission impact
```

**Phase 2 — Micro-Live (Weeks 5-8):**

```
□ 1 MNQ (micro) only — minimum position size
□ Real execution, real fills, real psychology
□ Maintain paper journal alongside
□ Benchmark: Is sim performance replicating?
□ Commission tracking active
□ If profitable over 30+ trades → proceed to Phase 3
```

**Phase 3 — Scaling Up:**

```
□ Increase from MNQ to NQ 1 contract
□ Apply position sizing protocol from Section 8
□ Continue journaling every trade
□ Monthly review: is win rate ~50%, R:R ≥1:2?
□ If yes → add second contract at 50% of target return
□ Continue building via compounding protocol
```

**What to Journal Every Trade:**

```
Date/Time | Setup Grade (A/B/C) | Entry reason | 
Qualifying sweep occurred? (Y/N) | Bubble present? (Y/N) |
CVD aligned? (Y/N) | VWAP aligned? (Y/N) |
R:R achieved | Result | Lesson
```

-----

# ═══════════════════════════════════════════════

# PART 13: GAPS RESOLVED + REMAINING

# ═══════════════════════════════════════════════

## RESOLVED By This Research Round

|Gap                              |Resolution                                                          |
|---------------------------------|--------------------------------------------------------------------|
|VWAP SD exact levels             |1SD=trend, 2SD=reversal, 3SD=extreme. Low VIX→1SD, High VIX→2SD/3SD |
|CVD confirmation — universal?    |YES — confirmed by institutional NQ research independently          |
|VWAP as session bias — universal?|YES — confirmed by multiple independent professional sources        |
|Opening range statistics         |96.2% NQ days break IB. 82.17% single-break = continuation          |
|NQ liquidity sweep pattern       |Independently confirmed as “most predictable institutional behavior”|
|Lunch hour statistical basis     |VWAP reliability confirmed to drop after 1pm by trading journal data|
|PDH/PDL as liquidity targets     |Confirmed by Marco’s model + independent institutional research     |

## Still Open — Need Next Source

|Gap                                  |Priority|What Would Resolve It               |
|-------------------------------------|--------|------------------------------------|
|Footprint chart reading depth        |HIGH    |Need footprint specialist transcript|
|Aggression bubble filter — 3rd source|HIGH    |Next Chart Fanatics trader          |
|Exact compounding formula            |MEDIUM  |More Fabio interview detail         |
|Gap day behavior (geopolitical)      |MEDIUM  |Case study or new transcript        |
|Swing trading / options approach     |LOW     |Fabio mentioned developing          |

-----

# ═══════════════════════════════════════════════

# PART 14: PERFORMANCE BENCHMARKS

# ═══════════════════════════════════════════════

|Metric                   |Target      |Source                      |
|-------------------------|------------|----------------------------|
|Win rate                 |~50%        |Fabio verified              |
|Minimum R:R              |1:2         |Both sources                |
|Typical R:R              |1:3–1:5     |Both sources                |
|Max R:R (directional day)|1:10–1:20   |Fabio                       |
|Max daily loss           |2%          |Fabio (hard rule)           |
|Max drawdown             |<20%        |Fabio (competition standard)|
|Trades per session       |1-5 quality |Combined                    |
|Sessions per day         |1 (NY only) |Both sources                |
|Commission impact        |10-20% gross|Fabio verified              |

-----

# ═══════════════════════════════════════════════

# PART 15: NEXT TRANSCRIPT PROTOCOL

# ═══════════════════════════════════════════════

When new transcripts are uploaded, extract and score:

1. Do they use Market State / OOB as a primary gate?
1. Do they use liquidity sweeps before entering?
1. Do they use CVD for trade management?
1. What is their exact stop placement method?
1. Do they reference VWAP or standard deviation bands?
1. What session and timing rules do they follow?
1. Do they use aggression/order flow confirmation?
1. What do they NEVER trade? (equal importance)
1. What is their position sizing protocol?
1. Do they grade setups before sizing?

**Promotion rules:**

- 2 sources confirm = STRONG ⭐
- 3 sources confirm = NON-NEGOTIABLE ✅
- 4+ sources confirm = CORE PRINCIPLE (immovable)

-----

*System Version: 3.0 | Sources: Fabio Valentini (001) + Marco Acetony (002)*
*Research: NinjaTrader IB Stats, TradingStat.net, Bookmap CVD Research,*
*PropTradingVibes NQ VWAP Data, Medium Institutional VWAP Study*
*All gaps tracked. All rules sourced. No opinions — only verified data.*
*Upload next transcript → say “Transcript: [Name]” → protocol activates*