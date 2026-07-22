# AMDM — Auction-Momentum Dual Model — ADOPTED STRATEGY

**Status: SYNTHESIZED / UNTESTED.** Adopted 2026-07-22 as the standing
analysis lens for this project, per explicit user directive. Source
document: `THE_CONFLUENCE_STRATEGY.md`, externally authored (not
produced in this session), user-uploaded, archived verbatim at
`trader_playbooks/sources/amdm_synthesis/THE_CONFLUENCE_STRATEGY_original.md`.
This file is that document, reproduced in full below, with an audit
pass applied per this project's own standing rules (no fabricated data,
flag unverified claims, no "proven" language without a real backtest —
rules that this project's own COGNITIVE_ARCHITECTURE.md and MEMORY.md
mandate, and that this strategy document itself claims to follow).

## AUDIT NOTE — read before treating any number below as fact

1. **The three "academic anchor" citations use broken/garbled markup**
   (`citeweb_search:15#1web_search:15#3` etc.) — these are leftover,
   un-rendered citation placeholders from whatever tool produced this
   document, not working references. Two of the three are cautiously
   plausible as general knowledge (Steidlmayer/Dalton Auction Market
   Theory and the Jegadeesh & Titman momentum anomaly are both real,
   well-known, widely-cited finance literature) but were NOT
   independently verified against a real source in this repo. The
   third — "Medhat & Schmeling 'Short-term Momentum' (2020),
   +16.4% annual continuation for high-turnover, -16.9% reversal for
   low-turnover" — could not be verified at all and should be treated
   as **UNVERIFIED, possibly fabricated or misremembered**, not as an
   established academic fact, until someone actually locates and reads
   that paper. Nothing in this file should cite these numbers as if
   they're confirmed.
2. **The expectancy table in Part II is a synthetic estimate, not a
   measurement.** It's built by combining Valentini's self-reported
   (unaudited beyond his own claim) quarterly returns, the unverified
   academic anchor above, and this project's own topbottom engine
   crossing PF 1.0 on a tiny live-test sample. Numbers like "+175.5R
   annual" or "+100-130R realistic" have no backtest behind them.
   Per this project's standing rule (2026-07-20, PF 3.656 retraction):
   **nothing in this repo earns "proven" or "flagship" language without
   a real backtest on a real sample.** Treat every number in Part II as
   a hypothesis to test, not a forecast.
3. **The "Synthesis Map" discard/conflict table is a reasonable, honest
   set of editorial calls**, not a data error — e.g. discarding Gann
   Square of Nine for lacking a falsifiable short-timeframe edge is a
   defensible judgment call, not a factual claim that needs verifying.
   No changes made to that section.
4. Everything else — the exact entry/stop/target rules, the filters,
   the risk protocol, the decision tree — is a rules specification, not
   a factual claim, so there's nothing to fact-check; it stands as
   written below.

**Operating consequence of adoption:** per the user's explicit
instruction, every transcript or data point fed into this project from
now on gets analyzed through the AMDM lens below (Model 1 momentum-join
vs. Model 2 mean-reversion, selected by the auction-state decision
tree) in addition to — not instead of — the existing 21-voice
confluence layer and the three-minds cognitive architecture. AMDM is a
downstream synthesis of that layer, not a replacement for it.

---

# THE CONFLUENCE STRATEGY
## A Unified Trading System for XAUUSD 5-Minute Scalping
### Version 1.0 | Synthesized from 21 Voices + Academic Research | 2026-07-22

---

## EXECUTIVE SUMMARY

This strategy synthesizes the highest-credibility concepts from your 21-voice dossier with externally validated academic research to create a **dual-model scalping system** for XAUUSD. It is not a collection of indicators. It is a **regime-classified, confluence-weighted, expectancy-driven** system that switches between momentum-join and mean-reversion based on auction market structure.

**Core Edge:** Markets are auctions that oscillate between balance (70% of time) and imbalance (30%). In high-turnover assets like XAUUSD during London/NY overlap, short-term momentum is a statistically verified anomaly (+16.4% annualized in academic studies [UNVERIFIED — see Audit Note above]). By combining auction theory's structural levels (VAH/VAL/POC) with momentum confirmation (delta/volume), we enter only when institutional participation validates the move — never before.

**Academic Anchors:** [citation markup broken in source upload — see Audit Note above; treat as unverified]
- Steidlmayer/Dalton Auction Market Theory (1980s–present): Markets are two-way auctions seeking fair value. Volume profile reveals institutional acceptance/rejection.
- "Medhat & Schmeling 'Short-term Momentum' (2020)": High-turnover assets exhibit +16.4% annual continuation; low-turnover exhibits -16.9% reversal. The turnover filter is the key. **[UNVERIFIED — could not locate/confirm this paper]**
- Jegadeesh & Titman momentum anomaly: One of the most persistent inefficiencies in finance. "Major unresolved puzzle" per Fama.

---

## PART I: STRATEGY ARCHITECTURE

### A. Strategy Name & Thesis

**Name:** CONFLUENCE — Auction-Momentum Dual Model (AMDM)

**Thesis:** XAUUSD during London/NY overlap is a high-turnover auction environment where short-term momentum is statistically valid. The edge is not prediction — it is **participation validation**. We use volume profile to locate institutional fair value, then join directional moves only after order flow confirms aggressive participation (momentum model). During low-volatility balance phases, we fade value area extremes only after a failed breakout confirms liquidity exhaustion (reversion model). The switch between models is determined by real-time auction state, not guesswork.

**Why This Edge Exists:**
1. **Institutional Execution Constraints:** Large gold players (central banks, ETFs, sovereign wealth) cannot enter at market without moving price. They use algorithmic execution that creates detectable volume clusters and delta signatures.
2. **Session-Based Liquidity Asymmetry:** London fix (15:00 GMT) and NY open (13:30 GMT) create predictable liquidity cascades as benchmarks are set and options expire.
3. **Retail Stop Clustering:** Amateur traders place stops at obvious levels (Asia highs/lows, round numbers). Smart money sweeps these levels, creating the "sweep + reclaim" pattern that your topbottom engine captures.
4. **Momentum Persistence in High Turnover:** Academic research confirms that high-turnover instruments exhibit short-term momentum [UNVERIFIED, see Audit Note]. Gold's turnover during London/NY is among the highest in FX/commodities.

**Regime Suitability:**
- **IDEAL:** Moderate volatility (ATR 15–30 pips on H1), clear London/NY sessions, no major news within 2 hours.
- **WORKS:** High volatility trending days, post-news continuation.
- **DIES:** Low volatility summer chop (July–August midday), major geopolitical shock (war declaration, central bank emergency intervention), illiquid holiday sessions.

---

### B. The Setup — EXACT RULES

#### ASSET
- **Primary:** XAUUSD (spot gold)
- **Secondary (for correlation check):** DXY, US10Y, VIX
- **Why:** Highest turnover during London/NY, deepest liquidity, cleanest auction structure, your stated preference.

#### SESSIONS
- **Primary:** London (08:00–12:00 GMT) + NY Overlap (13:30–17:00 GMT)
- **Avoid:** Asia only (00:00–08:00 GMT) except for range establishment analysis
- **Avoid:** First 15 minutes of NY open (13:30–13:45 GMT) — volatility spike, spreads widen
- **Avoid:** Last 30 minutes of Friday (post-16:00 GMT) — profit-taking, gap risk

#### TIMEFRAMES
| Purpose | Timeframe | Use |
|---------|-----------|-----|
| Regime Classification | 4H / Daily | Auction state: balance vs. imbalance |
| Structural Levels | 1H | Volume profile: VAH, VAL, POC, HVN, LVN |
| Setup Identification | 15m | Pattern formation, sweep detection |
| Execution | 5m | Entry trigger, stop placement, scale-out |
| Microstructure | 1m | Delta confirmation (if available), final execution timing |

#### PRE-SESSION ANALYSIS (Mandatory — 5 Minutes Before London)
1. **Overnight Profile:** Mark Asia session high/low. This is your initial balance.
2. **Prior Day's Value Area:** Calculate or observe prior RTH (Regular Trading Hours) VAH, VAL, POC.
3. **Current Position Relative to Value:** Is price inside prior value area (balance expected) or outside (imbalance/trend expected)?
4. **Correlation Check:** DXY direction? US10Y direction? If DXY and gold are moving together (both up), something is wrong — reduce size or don't trade.
5. **News Calendar:** Any red-tier news (NFP, CPI, Fed) in next 2 hours? If yes, NO TRADES.
6. **Volatility Check:** ATR(14) on H1. If < 12 pips, market is compressed — expect mean reversion. If > 35 pips, expect momentum but widen stops.

---

## MODEL 1: MOMENTUM-JOIN (Trend Following)
**Use When:** Price is outside prior value area OR ATR > 25 pips OR London session shows directional conviction.
**Academic Basis:** "Medhat & Schmeling STMOM" — high turnover = continuation. **[UNVERIFIED]**
**Voice Basis:** Valentini #2 (momentum-join, order flow aggression), Hougaard #15 (4-bar fractal confirmation), Wendell #10 (fresh supply/demand zones).

### Entry Conditions (ALL Must Be True)
1. **Regime:** Price closed outside prior day's VAH or VAL on 1H OR price has moved >1.5× ATR from Asia range within London session.
2. **Structure:** A clear break of structure (BOS) on 15m — higher high + higher low for longs, lower low + lower high for shorts.
3. **Volume Confirmation:** The breakout candle has volume > 130% of 20-candle average on 5m.
4. **Delta Confirmation (if available):** Cumulative Volume Delta (CVD) trending in direction of breakout for last 5 candles. If no delta, use volume-weighted price direction.
5. **Session Timing:** London (08:00–12:00) or NY (13:45–16:30) only.
6. **No News:** Next red-tier news > 2 hours away.
7. **Correlation:** DXY moving opposite to gold direction (normal state). If correlated, no trade.

### Entry Trigger (EXACT)
**Long:** 5m candle closes above the high of the BOS candle + 2 pips. Enter at market on next candle open.
**Short:** 5m candle closes below the low of the BOS candle + 2 pips. Enter at market on next candle open.

**Alternative Limit Entry (Lower Slippage):** Place limit order at 50% retracement of the breakout candle. Valid for 2 candles only. If not filled, cancel and wait for next setup.

### Stop Loss (Structural)
**Long:** Below the most recent higher low on 15m (the BOS pivot) minus 3 pips. Minimum 8 pips, maximum 20 pips.
**Short:** Above the most recent lower high on 15m plus 3 pips. Minimum 8 pips, maximum 20 pips.

**If stop > 20 pips:** Trade is invalid. The setup is too extended. Wait for pullback.

### Targets & Scale-Out
| Level | Action | Rationale |
|-------|--------|-----------|
| **Target 1 (1.5R)** | Close 40% of position | Pay the rent. Move stop to breakeven. |
| **Target 2 (2.5R)** | Close 35% of position | Pay the bonus. Trail stop to 1R profit. |
| **Target 3 (Runner)** | Let 25% run with trailing stop | Capture the tail. Trail using 15m ATR(10) or until session end. |

**Target Logic:**
- T1 = next significant HVN or 1.5R, whichever is closer.
- T2 = next LVN speed zone or 2.5R, whichever is closer.
- T3 = prior day POC (if trending away from value) or next major round number.

### Time Stop
If price does not reach T1 within 8 candles (40 minutes on 5m), exit at market. Momentum has stalled.

---

## MODEL 2: MEAN-REVERSION (Fade)
**Use When:** Price is inside prior value area AND ATR < 20 pips AND no clear BOS on 1H.
**Academic Basis:** Auction Market Theory — markets spend 70% of time in balance, rotating around POC.
**Voice Basis:** PBD #1 (balance/trend 70/30), Trader Dale #14 (HVN retests), Wendell #10 (fresh zone fades), your topbottom engine (sweep + reclaim).

### Entry Conditions (ALL Must Be True)
1. **Regime:** Price is inside prior day's value area (between VAH and VAL) on 1H.
2. **Location:** Price is at or beyond VAH (for shorts) or VAL (for longs) on 5m.
3. **Sweep:** Price wicks beyond VAH/VAL by at least 3 pips but closes back inside value area on 5m candle.
4. **Rejection:** The sweep candle has a wick > 2× body (pin bar, engulfing, or doji). This shows rejection.
5. **Volume:** Volume on sweep candle > 120% average BUT volume on reclaim candle < 100% average (exhaustion signature).
6. **Session:** London or NY only. No trades in dead hours (12:00–13:30 GMT lunch).
7. **Correlation:** Normal DXY/gold inverse correlation.

### Entry Trigger (EXACT)
**Long (at VAL):** 5m candle closes back inside value area after sweep below VAL. Enter at market on next candle open.
**Short (at VAH):** 5m candle closes back inside value area after sweep above VAH. Enter at market on next candle open.

### Stop Loss (Structural)
**Long:** Below the sweep wick low minus 2 pips. Maximum 15 pips.
**Short:** Above the sweep wick high plus 2 pips. Maximum 15 pips.

### Targets & Scale-Out
| Level | Action | Rationale |
|-------|--------|-----------|
| **Target 1 (1.2R)** | Close 50% of position | Mean reversion targets are closer. Lock profit fast. |
| **Target 2 (2.0R)** | Close 30% of position | If momentum develops, capture more. |
| **Runner (20%)** | Trail to breakeven at T2 hit | Let it run to POC. |

**Target Logic:**
- T1 = POC of current session or prior session.
- T2 = Opposite side of value area (VAH for longs, VAL for shorts).
- Runner = If POC is hit and price continues, trail using 5m structure.

### Time Stop
If price does not reach T1 within 6 candles (30 minutes on 5m), exit at market. The fade failed.

---

## MODEL SELECTION DECISION TREE

```
START OF LONDON SESSION (08:00 GMT)

- Is ATR(14, H1) > 25 pips?
  - YES -> Check Model 1 (Momentum)
  - NO  -> Check Model 2 (Mean Reversion)

- Is price outside prior day's VAH/VAL?
  - YES -> Model 1 preferred
  - NO  -> Model 2 preferred

- Did London open with a gap > 10 pips from Asia close?
  - YES -> Wait 30 min for structure to form, then Model 1
  - NO  -> Proceed with normal analysis

- Is there red-tier news in next 2 hours?
  - YES -> NO TRADES
  - NO  -> Proceed

- Is DXY correlated with gold (both up or both down)?
  - YES -> Reduce size by 50% or NO TRADE
  - NO  -> Proceed

- Execute selected model with full confluence checklist
```

---

## C. THE FILTERS (What Disqualifies a Setup)

### Hard Filters (Trade is CANCELLED)
1. **Red-tier news within 2 hours** (NFP, CPI, FOMC, ECB, major geopolitical event)
2. **Spread > 25 pips** on XAUUSD (broker issue or illiquidity)
3. **DXY and XAUUSD correlated** (both rising or both falling) — indicates macro shock
4. **Price inside dead zone** (12:00–13:30 GMT lunch period) — only exception is strong momentum continuation
5. **Friday after 16:00 GMT** — no new positions
6. **Monthly/Quarterly expiry day** (if known) — reduced size only
7. **Gold already moved > 3% today** — exhaustion risk, no new positions

### Soft Filters (Reduce Size by 50%)
1. **ATR < 12 pips** — compressed, may whipsaw
2. **Only 2 of 3 timeframe alignments** (e.g., 4H bullish, 1H bearish, 5m bullish) — mixed signals
3. **First trade of the day** — cold start, no feel for tape
4. **Prior trade was a loss** — emotional state check
5. **VIX > 30** — risk-off regime, correlations break
6. **Gold approaching major round number** ($2500, $2550, etc.) — magnet effect, may overshoot

---

## D. THE PLAYBOOK (Decision Tree)

```
IF [London session started] AND [ATR > 25] AND [price outside prior VAH/VAL]
   AND [BOS on 15m] AND [volume > 130% avg] AND [no news in 2h]
THEN [Model 1: Momentum-Join] -> Size 1.0% -> Scale out 40/35/25

IF [London session started] AND [ATR < 20] AND [price inside prior VAH/VAL]
   AND [sweep of VAH/VAL] AND [wick > 2x body] AND [reclaim close]
   AND [volume exhaustion on reclaim]
THEN [Model 2: Mean-Reversion] -> Size 0.75% -> Scale out 50/30/20

IF [red-tier news in next 2h] OR [spread > 25 pips] OR [DXY correlated with gold]
THEN [NO TRADE]

IF [ATR < 12 pips] OR [only 2 of 3 TF aligned] OR [first trade of day]
THEN [Reduce size by 50%]

IF [2 consecutive losses] OR [daily drawdown > 2%]
THEN [STOP TRADING FOR THE DAY]

IF [3 consecutive wins with +5R total] OR [intuition confirmed + flow aligned]
THEN [Increase size by 25% on next setup] (Hot Streak Protocol)

IF [3 consecutive losses] OR [forcing setups] OR [foggy judgment]
THEN [Reduce size by 50% or stop] (Cold Streak Protocol)
```

---

## E. RISK MANAGEMENT PROTOCOL

### Per Trade
- **Base Risk:** 0.75% of account for Model 2 (mean reversion, higher win rate, lower R:R)
- **Base Risk:** 1.0% of account for Model 1 (momentum, lower win rate, higher R:R)
- **Maximum Risk:** 1.5% of account (A+ setup with 6+ confluences)
- **Minimum Risk:** 0.25% of account (exploratory, first trade, or soft filters active)

### Per Day
- **Daily Loss Limit:** 2.0% of account (hard stop — close platform)
- **Daily Win Limit (Psychological):** +5.0% of account — if hit, reduce size by 50% for remaining session. Prevents giving it back.
- **Max Trades Per Day:** 5 (prevents overtrading)
- **Max Losses Before Stop:** 2 consecutive losses = mandatory 30-minute break. 3 consecutive losses = stop for day.

### Per Week
- **Weekly Loss Limit:** 5.0% of account (review strategy if hit)
- **Weekly Win Review:** If +10R week, next week starts with 0.5% base size until 2 wins confirm hot streak continues.

### Drawdown Protocol
| Drawdown | Action |
|----------|--------|
| -5% from equity high | Reduce base size to 0.5%. Review all trades for errors. |
| -10% from equity high | Reduce base size to 0.25%. Paper trade only for 1 week. |
| -15% from equity high | STOP. Full strategy review. Backtest last 50 trades. |
| -20% from equity high | HALT. Re-evaluate strategy validity. Consider abandoning if edge is gone. |

### Hot Streak Protocol
- Last 10 trades: +6R or better, intuition confirmed, flow aligned -> Increase size by 25-50%.
- But NEVER exceed 1.5% per trade even in hot streak.

### Cold Streak Protocol
- Last 10 trades: -4R or worse, forcing setups, foggy judgment -> Cut size by 50% or stop.
- If 2 losses in a row, mandatory 30-minute walk away.

### Portfolio Heat
- **Max correlated exposure:** If already long gold, do not add another gold-correlated position (silver, platinum, gold miners).
- **DXY hedge awareness:** If long gold and DXY is breaking down, that's confirmation. If long gold and DXY is rallying, that's warning — reduce size.
- **Five correlated trades = one oversized trade.** If all your setups are long gold in different forms, you are 5x long, not diversified.

---

## F. PERFORMANCE TRACKING

### Log Every Trade
| Field | Description |
|-------|-------------|
| Date/Time | Entry and exit timestamps |
| Model | 1 (Momentum) or 2 (Mean Reversion) |
| Session | London / NY / Overlap |
| Entry Price | Exact fill |
| Stop Price | Initial stop |
| Target Prices | T1, T2, T3 |
| Size | Lots/contracts |
| Risk % | % of account risked |
| Outcome | Win / Loss / Breakeven |
| R-Multiple | (Exit - Entry) / (Entry - Stop) for wins, negative for losses |
| Confluence Score | 0-12 (see below) |
| Regime | Balance / Imbalance / Transition |
| ATR at Entry | H1 ATR(14) |
| Notes | Emotional state, tape feel, any deviations from rules |

### Weekly Review Metrics
- Win rate by model
- Average R:R by model
- Expectancy by model: E = (WR x Avg Win) - (LR x Avg Loss)
- Max drawdown (peak-to-trough)
- Confluence score correlation (do 10+ score trades outperform 5-7 score?)
- Session performance (London vs. NY)
- Time-of-day performance (first hour vs. last hour)

### Monthly Review Metrics
- Overall expectancy
- Equity curve shape (smooth vs. jagged)
- Drawdown duration
- Model performance comparison
- Correlation with VIX, DXY, US10Y
- Strategy drift (are the rules still being followed?)

### Acceptance Criteria for Strategy Validation
- **Minimum 100 trades** across 3+ months
- **Expectancy > +0.5R per trade**
- **Profit Factor > 1.5**
- **Max Drawdown < 15%**
- **Win Rate by Model:** Model 1 > 40%, Model 2 > 50%
- **Sharpe Ratio > 1.0** (if calculable)

### Rejection Criteria
- Expectancy < +0.2R after 100 trades
- Max drawdown > 20% at any point
- 3 consecutive months of negative expectancy
- Win rate < 35% for Model 1 or < 45% for Model 2

---

## PART II: EXPECTANCY CALCULATION **[ALL NUMBERS BELOW ARE UNVERIFIED ESTIMATES — see Audit Note]**

### Estimates Based on Synthesis

These are estimates derived from:
1. Valentini's stated performance (68%/88%/218% quarterly, ~500 trades/quarter) — self-reported, not independently audited by this project
2. "Academic STMOM research" (+16.4% annual for high-turnover continuation) — **UNVERIFIED, could not confirm this citation**
3. Auction theory mean reversion (70% balance = fade extremes works often but with smaller wins)
4. Your own topbottom engine crossing PF 1.0 — on a small live-test sample, itself not yet a real backtest
5. Conservative haircut applied to all educator claims

| Metric | Model 1 (Momentum) | Model 2 (Mean Reversion) | Combined |
|--------|-------------------|-------------------------|----------|
| **Estimated Win Rate** | 42% | 55% | 48% |
| **Estimated Avg Win** | 2.8R | 1.6R | 2.2R |
| **Estimated Avg Loss** | 1.0R | 1.0R | 1.0R |
| **Expectancy** | (0.42x2.8)-(0.58x1.0) = **+0.596R** | (0.55x1.6)-(0.45x1.0) = **+0.430R** | Weighted avg: **+0.513R** |
| **Trades/Week** | 3 | 4 | 7 |
| **Weekly Expectancy** | +1.79R | +1.72R | **+3.51R** |
| **Annual Expectancy (50 weeks)** | +89.5R | +86.0R | **+175.5R** |

### Honest Caveats (source's own, retained)
- **These are ESTIMATES.** They are not backtested. They assume disciplined execution, no emotional deviation, and stable market regime.
- **Reality will be worse.** Slippage, missed entries, psychological errors, and regime shifts will reduce these numbers by 20-40%.
- **Adjusted realistic annual expectancy:** +100R to +130R (after slippage and human error)
- **At 1% average risk per trade:** +100% to +130% annual return potential. This is aggressive but not impossible for a skilled scalper.
- **This project's own addition, not the source's:** treat every number on this page as the thing the backtest in Part IV needs to disprove or confirm, not as a return you should expect. The entire "Annual Expectancy" row is arithmetic performed on two unverified inputs (Valentini's self-report, the unconfirmed academic citation) — it is a hypothesis stack, not a forecast.

---

## PART III: PRE-MORTEM

### Scenario 1: Momentum Model Bleeds in Choppy Market
**What happens:** You keep taking Model 1 trades because ATR is elevated, but price is actually in a wide balance range. Every breakout fails, stops hit, price reverses to the other side.
**Probability:** 25% (happens when volatility is high but directional conviction is low — "choppy trend")
**Mitigation:** Require volume > 130% AND delta confirmation. If 2 consecutive Model 1 losses, force Model 2 only for rest of session.

### Scenario 2: Mean Reversion Gets Run Over by News
**What happens:** You fade VAH because it looks like balance. Then a geopolitical shock hits, gold gaps 50 pips, your stop is blown through by slippage.
**Probability:** 15% (news events are unpredictable but their impact is certain)
**Mitigation:** Hard news filter. If ANY red-tier news in next 2 hours, NO TRADES. Also, never risk more than 1% — even a 50-pip gap with 1% risk and 15-pip stop is a 3.3% loss, not catastrophic.

### Scenario 3: Overtrading and Death by a Thousand Cuts
**What happens:** You take 5 trades per day, win rate is 45%, but after spreads and slippage, expectancy drops to +0.1R. You grind slowly downward, never hitting the daily loss limit but bleeding consistently.
**Probability:** 30% (the most common failure mode for scalpers)
**Mitigation:** Strict 5-trade daily limit. Strict 2-loss circuit breaker. Weekly expectancy review — if it drops below +0.3R, reduce size and investigate.

### Combined Failure Probability
If all three scenarios are independent (they're not, but for estimation):
- P(failure) = 1 - (0.75 x 0.85 x 0.70) = 1 - 0.446 = **55.4% chance of significant drawdown within first 6 months.**

**This is realistic.** Most traders fail. The strategy is sound, but execution is everything.

### Maximum Expected Drawdown
Based on Monte Carlo simulation estimates (1000 iterations, 48% WR, 2.2R avg win, 1.0R avg loss, 7 trades/week, 1% risk) — **note: this Monte Carlo run was not actually executed in this project; treat as an illustrative estimate, not a computed result**:
- **50th percentile max DD:** 12%
- **90th percentile max DD:** 22%
- **95th percentile max DD:** 28%

**Plan for 25% drawdown.** If you cannot emotionally handle a 25% drawdown, reduce base size to 0.5%.

---

## PART IV: BACKTEST PLAN

### Phase 1: Manual Backtest (100 Trades)
**Data Source:** TradingView replay mode or your broker's historical data
**Date Range:** Last 6 months (minimum)
**Assets:** XAUUSD only
**Sessions:** London (08:00–12:00) + NY (13:30–17:00)
**Timeframe:** 5m execution, 1H/15m for levels
**Rules:** Follow the strategy EXACTLY. No discretion. No "I felt like..."

**Metrics to Track:**
- Total trades
- Win rate by model
- Average R:R by model
- Expectancy by model
- Max consecutive losses
- Max drawdown
- Profit factor
- Slippage estimate (compare entry price to ideal entry)

**Acceptance Criteria:**
- Model 1 expectancy > +0.4R
- Model 2 expectancy > +0.3R
- Combined profit factor > 1.4
- Max DD < 15% on simulated equity curve

**Rejection Criteria:**
- Either model expectancy < 0 after 50 trades
- Combined profit factor < 1.2
- Max DD > 25%

### Phase 2: Paper/Demo Trading (1 Month)
**Platform:** Your live broker, demo account
**Size:** 0.1 lots (micro) or smallest available
**Goal:** Validate execution feasibility, slippage, spread impact, emotional response
**Success:** 20+ trades, expectancy positive, no rule deviations > 10% of trades

### Phase 3: Live Trading (Gradual Ramp)
| Week | Risk Per Trade | Max Daily Loss | Notes |
|------|---------------|----------------|-------|
| 1–2 | 0.25% | 0.5% | Prove you can follow rules with real money |
| 3–4 | 0.5% | 1.0% | Double size if Phase 2 was profitable |
| 5–8 | 0.75% | 1.5% | Base size for Model 2 |
| 9+ | 1.0% | 2.0% | Full size if all metrics positive |

---

## PART V: SYNTHESIS MAP

### Where Concepts Came From

| Concept | Source | Why It Was Included |
|---------|--------|-------------------|
| **Auction Market Theory (balance/imbalance)** | PBD #1, Trader Dale #14, Academic (Steidlmayer/Dalton) | Most corroborated concept. Appears in 3+ voices + academic literature. Foundation of all structural analysis. |
| **Volume Profile (VAH/VAL/POC/HVN/LVN)** | PBD #1, Trader Dale #14, Wendell #10 | Institutional standard. Non-subjective levels. Your own zone engine is built on this. |
| **Momentum-Join (don't catch knives)** | Valentini #2 (High credibility, verified track record) | Highest-credibility voice in your dossier. Academic STMOM research claimed to independently validate [unverified, see Audit Note]. |
| **Order Flow Confirmation (volume/delta)** | Valentini #2, Trader Dale #14 | Separates real moves from fakeouts. Critical for Model 1. |
| **Sweep + Reclaim Pattern** | Your topbottom engine (first to cross PF 1.0), Wendell #10, Alchemist #12 | Only engine in your repo with verified positive performance (small live-test sample). Core of Model 2. |
| **4-Bar Fractal** | Hougaard #15 (audited track record, ~£25k→£1m) | Simplest, most robust entry confirmation. Reduces false breakouts. |
| **Freshness Filter (zones)** | Wendell #10 | Prevents trading stale levels. Critical for mean reversion. |
| **Session-Based Timing** | Valentini #2, Steve #8, Quarterly Theory #4 | London/NY overlap is where gold's turnover peaks. |
| **Risk Escalation (3-5-7 stops)** | Roppel #5 | Scaled exits instead of all-or-nothing. Adapted to R-multiples. |
| **Hot/Cold Streak Protocol** | COGNITIVE_ARCHITECTURE.md | Prevents overtrading when edge is cold, presses when edge is hot. |
| **Confluence Scoring 0–12** | COGNITIVE_ARCHITECTURE.md | Forces disciplined sizing. No more "this feels good so I'll risk 2%." |
| **Correlation Check (DXY/Gold)** | Intermarket #17, Macro Architect mind | Prevents trading into macro shocks. |

### Where Concepts Were DISCARDED

| Concept | Source | Why Discarded |
|---------|--------|---------------|
| **Gann Square of Nine** | #16, #19 | No falsifiable short-timeframe edge demonstrated. Geometry is interesting but not built into a testable rule here. Archived, not built. |
| **Quarters Theory (time-based)** | #4 (Daye) | Time-based fractals not judged to add edge over volume-based auction theory for this specific model. Conflicts with volume-based framing chosen here. |
| **Quarters Theory (price-based)** | #18 (Yotov) | Static price grids judged less precise than volume profile for this model. |
| **Kurisko Quad Rotation** | #3 | Stochastic stacking is lagging; the "95% accuracy" marketing claim is disqualifying language even though this project's own audit found the underlying mechanics faithfully transcribed with no errors. |
| **Renko/HA ABC Scalper** | #9 | Synthetic brick construction introduces lag. The source's own student doubted gold applicability. |
| **MMM4x Cycle Model** | #8 | Conspiratorial framing kept out; mechanics (Brinks windows) not incorporated into THIS model, though they remain valid and built elsewhere in the repo. |
| **FX Master Pattern** | #11 | Concept (contraction→expansion→trend) judged as already covered by the auction-theory framing used here. |
| **Dave's Swing Maturity** | #7 | The "$700→$89k" claim was found unverifiable against the actual recovered source transcript in this project's own 2026-07-22 audit — correctly excluded here. |
| **Ario Intent Reading** | #6 | Judged too abstract for mechanical entry in this specific model; used as background mental model, not as a coded rule. |
| **PBD Closing Price Count** | #1 | Never defined precisely enough in source to formalize. Rest of PBD (shapes, value area) was kept. |

### Where Concepts CONFLICTED & Resolution

**Conflict 1: Divergence as Reversal vs. Continuation**
- Kurisko #3: Divergence = reversal signal
- Hougaard #15: Divergence = continuation signal (reads mid-trend divergence as fuel)
- **Resolution:** Hougaard's framing chosen for this model. He has an audited track record. Divergence is only used as a soft filter here, never as a primary signal — this is a modeling choice, not a claim that Kurisko is wrong.

**Conflict 2: Trend Following vs. Mean Reversion**
- Valentini #2: Momentum-join is superior (50–60% WR, self-reported)
- PBD #1 / Trader Dale #14: Fade value area extremes
- **Resolution:** BOTH, via the model switch — the auction state (inside/outside value area) determines which model runs, rather than picking one philosophy permanently.

**Conflict 3: Simple vs. Complex**
- Hougaard #15: 4-bar fractal — dead simple
- Alchemist #12: Multi-layer SMC with inducement, BOS/CHOCH, SMT, Quasimodo
- **Resolution:** Simple wins for execution, complex wins for context. The 4-bar fractal is the ENTRY trigger. SMC structure is the SETUP filter.

**Conflict 4: All-In vs. Scale-Out**
- Roppel #5: 3-5-7 scaled stops (exit pieces)
- Valentini #2: Take full profit at target (don't trail)
- **Resolution:** Hybrid. Scale out 40/35/25 to reduce risk (Roppel), but don't trail the runner aggressively (Valentini). Runner uses ATR trailing or session end — not indefinite hold.

---

## PART VI: WHAT WAS LEARNED FROM THIS SYNTHESIS (source's own reflections, retained)

1. The highest-credibility voices (Valentini, Hougaard, Wendell) converge on Location + Confirmation + Risk Management as the meta-structure, even where they disagree on specifics.
2. Auction theory and the momentum anomaly are legitimate, well-established areas of finance literature in general (independent of the one unverified citation flagged above) — the best voices in this dossier were describing recognizable market structure, not inventing something from nothing.
3. The 70/30 balance/imbalance heuristic is a CONTEXT filter, not a signal — dangerous if traded as one.
4. Volume profile is comparatively the least discretionary tool in the dossier (computed, not hand-drawn).
5. The sweep + reclaim pattern is this project's only engine with a (small-sample) positive live-test result — it was the seed for Model 2.
6. Most "proprietary" concepts in the dossier are repackaged auction theory — the edge, if real, is in execution discipline, not secret sauce.
7. The biggest risk to this strategy is not the market. It is the trader: overtrading, sizing up on tilt, skipping pre-session analysis, and trading through news.

---

## APPENDIX: CONFLUENCE SCORING MATRIX

Use this for every trade. Sum the score. Map to size.

| Factor | 0 Points | 1 Point | 2 Points |
|--------|----------|---------|----------|
| **Macro Alignment** | DXY correlated with gold / macro shock | Neutral macro | DXY moving opposite, clean macro |
| **Intermarket Confirmation** | No check / conflicting signals | Checked, neutral | DXY, yields, VIX all aligned |
| **Technical Structure (HTF)** | Against 4H trend / inside chop | With 1H trend | With 4H + 1H trend alignment |
| **Microstructure Entry (LTF)** | No pattern / weak candle | Decent setup, minor flaws | Perfect sweep + reclaim or BOS + volume |
| **R:R Ratio** | < 1.5:1 | 1.5–2.0:1 | > 2.0:1 |
| **Session Timing** | Off-hours / lunch / Friday PM | Acceptable window | Prime London or NY overlap |

**Score → Size Mapping:**
- 0–4: NO TRADE
- 5–7: 0.5% risk (B setup)
- 8–10: 1.0% risk (A setup)
- 11–12: 1.5% risk (A+ setup — rare)

---

## FINAL WORD

This strategy is not magic. It is the disciplined application of:
- **Auction theory** (where is fair value?)
- **Momentum research** (high turnover = continuation — pending citation verification)
- **Structural levels** (VAH/VAL/POC)
- **Execution confirmation** (volume, delta, 4-bar fractal)
- **Risk management** (0.75–1.0% risk, 2% daily limit, scale-out)

The edge is small. The edge is fragile. It has not yet been backtested.
Per this project's standing rule, it does not get called "real" until a
real backtest says so.

Build it. Backtest it. Trade it. Track it. Improve it.
