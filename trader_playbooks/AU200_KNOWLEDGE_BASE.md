# AU200 Knowledge Base
**Compiled:** 2026-08-04  
**Status:** WORKING DOCUMENT — most findings are unverified. Read the status tag on every item.

## Source legend
- `[CODE]` — read directly from a Pine file in this session
- `[SCREENSHOT]` — visible in the "Research claims verification" session report (unverified, no cost model confirmed, no drawdown column)
- `[SUMMARY]` — from context-compaction summaries; code exists but was lost to container reclamation
- `[ASSUMPTION]` — inferred, not measured
- `[MISSING]` — data does not exist anywhere in the record

---

## 1. Instrument Characteristics

**Symbol and provider**  
`[CODE]` AUS200 CFD, described in strategy headers as "AUS200 CFD, 5m chart".  
`[CODE]` au200_tbt_flip_backtest.pine header: "SETUP: AUS200 CFD, 5m chart, Timezone = Australia/Sydney (CRITICAL)".  
`[MISSING]` Broker/data provider not specified in any file. The Brue (London Strategic Edge) platform is mentioned in the user profile as an alternative execution platform.

**mintick**  
`[ASSUMPTION]` AU200 CFD quotes in whole index points; mintick is likely 1 point.  
`[MISSING]` This has NOT been read off the chart as required by the research protocol. Until confirmed, all slippage calculations in ticks are unknown. BUG-021 applies: Pine `slippage` parameter is in ticks, not points. If mintick=1, then slippage=1 means 1 point per fill; if mintick=0.1, slippage=1 means 0.1 points.

**Point value**  
`[SCREENSHOT]` The report states "$100/pt/lot". This is the dollar value per index point.  
`[MISSING]` Not confirmed in any Pine file in the repo.

**Volatility and ATR**  
`[MISSING]` No measured ATR for AU200 exists in this record. The gap from 15pt SL and 30pt trail in au200_base_flip_v1.pine implies ATR is assumed to be in the 15–50pt range on 5m bars, but this is an inference from parameter choices, not a measurement.

**Gap behaviour**  
`[CODE]` au200_tbt_flip_backtest.pine uses a gap-direction entry: `gap_pts = open - close[1]`, trading the direction of the opening gap at 10:00 AEST. This presupposes that meaningful gaps occur regularly at the session open.  
`[MISSING]` No gap statistics (frequency, typical size, fill rate) are measured or documented.

**How AU200 differs from gold (XAUUSD)**  
`[MISSING]` No explicit comparison exists. Structural differences implied by the code:
- Session-anchored behaviour (market opens 10:00 AEST vs gold's 24h instrument)
- Fixed trading hours vs gold's Sunday–Friday continuous
- Index-level magnetics (round thousands, daily open) vs gold's macro-driven key levels
- AU200 appears to trade 1–6 setups per day; XAUUSD champion trades ~2.3 per week

---

## 2. Session Behaviour

**DST handling**  
`[CODE]` All AU200 Pine files use `"Australia/Sydney"` as the timezone string for session detection, not hardcoded `"UTC+10"`. This is the correct DST-aware implementation.  
`[SUMMARY]` An earlier version used `hour(time, "UTC+10")`, which fired 1 hour early during October–April (AEDT). This was identified and fixed as a DST bug before the files were lost.

**Active trading window**  
`[CODE]` au200_base_flip_v1.pine: entry window is `9:50 AM`, `9:55 AM`, `10:00 AM` AEST (user-configurable toggles).  
`[CODE]` au200_base_flip_v1.pine: EOD force-close at `12:00 PM` AEST.  
`[CODE]` au200_tbt_flip_backtest.pine: single entry bar at `hour == 10 and minute == 0` (10:00 AEST).  
`[SCREENSHOT]` The report header says "10:00–12:00" as the session label for the top-performing row.  
`[MISSING]` No data on performance outside 10:00–12:00. Whether afternoon sessions (12:00–16:00 AEST) or US-overlap periods add or subtract is untested.

**10:00 AEST gap entry rationale**  
`[CODE]` au200_tbt_flip_backtest.pine: at 10:00 AEST, a gap up (`open > close[1]`) signals long; gap down signals short. This is the primary entry trigger.  
`[MISSING]` No measured statistics on gap frequency, average gap size, or hit rate at 10:00 AEST specifically.

---

## 3. Strategies Built and Their Status

### 3a. AU200 Base + Flip (au200_base_flip_v1.pine)
**Source:** `[CODE]` — file was read in full before context compaction.

**Entry:**  
- Time window: 9:50, 9:55, or 10:00 AEST (user toggles)  
- Triple filter: EMA 200 + RSI 14 + SuperTrend(3.1, 97)  
- Long: close > EMA200 AND RSI > 50 AND SuperTrend bullish  
- Short: close < EMA200 AND RSI < 50 AND SuperTrend bearish  
- Entry requires `position_size == 0` and `_dir == 0` (flat state)

**Exit:**  
- Hard SL: 15 pts (input default)  
- Trail: 30 pts, arms after +5 pts of favourable movement  
- TP1: 20 pts, closes 50% of position, optional breakeven SL move after TP1  
- EOD: force-close all at 12:00 AEST  
- Flip engine: on SL hit, reverse direction. Flip SL = `sl_pts × flip_sl_mult` (default 2.0×, so 30 pts on the flip). Max 3 flips per entry.

**Parameters (defaults):**  
- SL: 15 pts | Trail: 30 pts | Trail trigger: 5 pts  
- TP1: 20 pts | TP1 close: 50% | TP1 breakeven: ON  
- Flip SL multiplier: 2.0 | Max flips: 3  
- EMA toggle: ON | RSI toggle: ON | SuperTrend toggle: ON

**Cost model in Pine:**  
`commission_type = strategy.commission.cash_per_contract, commission_value = 1`  
`currency = currency.AUD, initial_capital = 50000`  
`[MISSING]` Slippage parameter value — not confirmed.

**Backtest result:** `[MISSING]` No numbers exist. This strategy was never backtested.

**Concerns:**  
- `process_orders_on_close = true` means entries fill at bar close. On a 5m chart with an EOD close at 12:00, this bounds the maximum trade duration.  
- The flip SL is wider than the initial SL (30 vs 15 pts). This is intentional — it gives the flip room — but doubles the risk on the flip leg.  
- EMA200/RSI/SuperTrend triple filter was NOT tested. The user noted "this is the most profitable strategy yet" after seeing signals on the chart, but no backtest confirmed that impression.

---

### 3b. AU200 TBT + Flip System (au200_tbt_flip_backtest.pine)
**Source:** `[CODE]` — file was read in full.

**Entry:**  
- Bar: 10:00 AEST exactly (`hour == 10 and minute == 0`)  
- Direction: gap direction (`open - close[1] > 0` = long, `< 0` = short)  
- Filters: SuperTrend(10, 1.5) must agree AND TBT trendline direction must agree  
- TBT filter: pivot-high trendline must be descending + close crosses above (long); pivot-low trendline must be ascending + close crosses below (short)

**Exit:**  
- SL: 5 pts per leg (very tight)  
- Trail: 75 pts from peak, arms at +5 pts  
- Flips: up to 6 on SL hit; each flip reverses direction  
- TP1: 20 pts signal (visual only, not a hard exit in the current code)

**Parameters (defaults):**  
- SL: 5 pts | Trail: 75 pts | Trail trigger: 5 pts | Max flips: 6  
- TBT period: 10 | TBT filter: ON  
- TP1 signal threshold: 20 pts

**Cost model in Pine:**  
`commission_type = strategy.commission.cash_per_order, commission_value = 0.5`  
`slippage = 0` (explicitly zero)  
`[CONCERN]` slippage=0 is unrealistic.

**Claimed backtest result (from file header comment):**  
`[CODE but UNVERIFIED]` The strategy file header states:  
> "VERIFIED: PF=2.10, WR=9.7%, 8/8 yrs (2019-2026), Net=11,819pts"

**This is a comment in the Pine file, not a RESULTS_LEDGER row.** It has no trade count, no drawdown, no cost model confirmation, no DSR, no out-of-sample split. The research protocol does not recognise it as a result. It cannot be reproduced from this container (no AU200 data, no backtest engine).  

The 9.7% win rate is low but plausible for a trend-following system with a 5-pt SL and a 75-pt trail (15:1 reward/risk if it runs). However, that ratio is exactly the kind of structure that produces high reported PF from a small number of large wins — and is vulnerable to lookahead on the excursion update (BUG-019).

**BUG-019 concern:**  
`[CODE]` In the strategy's position management block:
```pine
if strategy.position_size > 0 and not na(v_ep)
    v_pk := math.max(v_pk, high)          // ← excursion updated HERE
    if (v_pk - v_ep) >= P_TRIG
        v_trail := true
    ...
    if low <= sl_p                         // ← stop checked AFTER
```
The excursion update (`v_pk := math.max(v_pk, high)`) precedes the stop check (`if low <= sl_p`) within the same bar block. This is BUG-019. On a bar that both reaches a new high AND takes out the stop, the code registers the high first (updating the trail), then resolves the stop — but the trade state at that moment has already been updated to a more favourable peak. This inflates the reported win rate because bars that should be stop-outs can be counted as partial wins.  
`[MISSING]` The magnitude of this effect on the reported 9.7% WR is unknown without re-running with the corrected order.

---

### 3c. Top & Bottom Entry Indicator (top_bottom_entry_v1.pine)
**Source:** `[CODE]` — file read in full.

**Type:** Indicator only (not a strategy). No backtest possible without converting.

**Mechanism:**  
- OLS linear regression over `lookback` bars (default 9) on `close[1]` (non-repainting)  
- Finds the highest pivot above the OLS line and the lowest pivot below it  
- Optimises the slope (30-step binary search) so all highs stay above the resistance line, all lows below the support line  
- BOT signal: `close > resistance_line + atr_mult × ATR14` (breakout above resistance)  
- TOP signal: `close < support_line - atr_mult × ATR14` (breakdown below support)

**Noise filters:**  
- ATR threshold: 0.3 × ATR14 (close must exceed line by this amount)  
- Cooldown: 3 bars minimum between signals  
- Alternating: must flip direction each signal (no consecutive BOT/BOT)

**Status:** `[SUMMARY]` Built and delivered. No backtest result exists.

---

### 3d. Top & Bottom Entry Strategy (top_bottom_strategy_v1.pine)
**Source:** `[CODE]` — file read in full.

Same trendline logic as the indicator, plus:
- Hard SL: 20 pts | Trail: 15 pts, arms at +5 pts  
- Exit on opposite signal (closes and reverses)  
- Commission: $1/contract, AUD, $50k initial capital  
- `process_orders_on_close = true`

**Status:** `[SUMMARY]` Built and committed. Push 403'd. File lost. No backtest result exists.

**BUG-019 concern:**  
`[CODE]` Same order-of-operations issue as TBT+Flip: trail management block updates `_best` before checking the stop on the same bar.

---

## 4. The Screenshot Report (Nine-Row Table)
**Source:** `[SCREENSHOT]` — from a separate session ("Research claims verification") that no longer has its files accessible. These numbers cannot be reproduced or verified from this container.

### What the table shows

| Strategy | N | WR | PF | Net 2019-2026 | T/day |
|---|---|---|---|---|---|
| UT Bot Session 10:00-12:00 | 4,893 | 67.7% | 4.07 | $5,142,420 | 2.52 |
| UT Bot + EMA Hybrid (v2 backtest) | 4,407 | 74.4% | 7.11 | $5,820,000 * | 2.27 |
| UT Bot OR Breakout (10:00-10:10) | 2,630 | 67.9% | 4.07 | $2,696,410 | 1.36 |
| ST+RSI Trail30 EMA filtered | 3,001 | 67.4% | 3.46 | $2,938,810 | 1.55 |
| ST only Trail30 no filter | 6,298 | 67.9% | 3.65 | $6,725,280 | 3.25 |
| EMA Trail system (best exit V1) | 2,752 | 39.6% | 1.06 | $68,336 | — |
| UT Bot + ST filter | 3,797 | 67.0% | 3.98 | $3,858,950 | 1.96 |
| UT Bot + ST+RSI filter | 2,430 | 67.1% | 4.02 | $2,483,050 | 1.25 |
| EMA zone filter F6 (EMA50+EMA200) | 3,034 | 68.7% | 4.39 | $3,309,180 | — |

*asterisk on row 2: "hybrid estimate from Python backtest engine"

### What is missing from every row
- Max drawdown: `[MISSING]` not in the table
- Slippage value: `[MISSING]` not confirmed
- Commission per side: `[MISSING]` not confirmed
- Starting equity: `[MISSING]` not stated
- Whether sizing is fixed lots or compounding: `[MISSING]`
- Year-by-year breakdown: `[MISSING]`
- Out-of-sample split: `[MISSING]`
- DSR and PBO: `[MISSING]`
- Which rows come from TradingView live vs Python estimate: only row 2 is flagged; the rest are not labelled

### What these numbers would mean if real
At $100/pt with a fixed 1-lot and $5.14M net over 7 years (4,893 trades), average net profit per trade is $1,051 = 10.5 points. With a WR of 67.7%, that requires average winner of approximately 5.5 pts and average loser of approximately 2.6 pts, OR a much wider winner with the same WR. Without knowing the stop and trail size, this cannot be sanity-checked.

### The win-rate clustering problem
Seven of nine strategies land at 67.0–68.7% WR. The exception is "EMA Trail system" at 39.6% (and PF 1.06 — the only entry that honestly reflects a trend-following shape). The one strategy with a realistic win rate for a trailing-stop system is also the only one that shows a realistic PF.

Convergence on 67–69% across strategies with different entry families is the signature of a shared exit element that always appears to win — most likely BUG-019 (excursion updated before stop resolution on the same bar). The 39.6% WR row either uses a different exit block or has the correct operation order, which would explain why it produces a different shape.

**This is the priority check.** Before any number from the seven high-WR rows is treated as real, the Pine file must be grepped for the relative line order of `v_pk :=` (or equivalent) versus the stop check.

---

## 5. Parameters Tested or Implied

### Stops
| Source | Stop | Notes |
|---|---|---|
| au200_base_flip_v1 | 15 pts initial, 30 pts on flip | Arbitrary; not ATR-scaled |
| au200_tbt_flip | 5 pts per leg | Very tight; 5/75 = 1:15 R:R if trail runs |
| top_bottom_strategy | 20 pts | Arbitrary |
| Screenshot rows | Unknown | Not in table |

### Trails
| Source | Trail | Trigger |
|---|---|---|
| au200_base_flip_v1 | 30 pts from peak | Arms at +5 pts |
| au200_tbt_flip | 75 pts from peak | Arms at +5 pts |
| top_bottom_strategy | 15 pts from peak | Arms at +5 pts |
| Screenshot "ST Trail30" rows | 30 pts (implied by name) | Unknown |

### Timeframe
`[CODE]` All Pine files specify 5m chart as the target.  
`[MISSING]` No timeframe comparison (15m, 30m, 1H) has been run for AU200. The XAUUSD project found 30m superior to 15m on every metric; whether that generalises to AU200 is unknown.

### Commission
`[CODE]` Two different commission models appear in the files:
- au200_base_flip_v1: `cash_per_contract, $1 AUD`
- au200_tbt_flip: `cash_per_order, $0.50`

These are inconsistent. Neither has been confirmed as matching an actual broker rate.

### Slippage
`[CODE]` au200_tbt_flip_backtest.pine: `slippage = 0` (explicitly zero — unrealistic).  
`[MISSING]` au200_base_flip_v1.pine: slippage parameter not visible in the read portion.  
`[MISSING]` Actual AU200 spread. BUG-021 applies: if mintick=1 point and slippage=1, that is 1 point per fill. If mintick=0.1, it is 0.1 points. mintick must be read from the chart before any number is trusted.

---

## 6. What Has Been Measured vs What Has Not

| Question | Status |
|---|---|
| Does any AU200 strategy have a RESULTS_LEDGER entry? | NO |
| Has any AU200 number gone through DSR + PBO + year-by-year? | NO |
| Has any AU200 strategy been validated against a TradingView live run? | NO |
| Is the TBT+Flip "VERIFIED PF 2.10" a validated result? | NO — Pine comment only, no ledger row, no cost model |
| Are the nine screenshot rows validated? | NO — no drawdown, no cost model, no OOS split |
| Has BUG-019 been checked in the AU200 exit blocks? | PARTIALLY — identified in two files by code review; magnitude unknown |
| Is the AU200 mintick confirmed? | NO |
| Is slippage modelled realistically in any AU200 file? | NO — one file sets slippage=0 explicitly |

---

## 7. Edge Hypotheses Worth Testing (with required checks first)

**Hypothesis 1 — The 10:00 AEST gap direction works**  
Source: au200_tbt_flip_backtest.pine header comment (PF 2.10, 8 years).  
What must happen first: (a) fix BUG-019 in the exit block, (b) set realistic slippage (mintick read from chart first), (c) run on TradingView with the corrected code, (d) compare largest win and largest loss to the research claim.

**Hypothesis 2 — Session restriction (10:00–12:00) is the primary edge, not the signal**  
Source: The screenshot's top row is "UT Bot Session 10:00–12:00" and the XAUUSD project found filters carry more edge than entry triggers. If the 10:00 gap direction carries no information, a random-entry null within 10:00–12:00 would return a similar result.  
What must happen first: corrected null (BUG-023 protocol — randomise entry timing within the same session filter).

**Hypothesis 3 — Flip engine adds return**  
Source: strategy design in au200_base_flip_v1 and au200_tbt_flip.  
What must happen first: run the strategy without flips, then with flips, report both. The XAUUSD project found pyramiding (adding to winners) is a variance multiplier not an edge; flipping is the same mechanic applied to losers and carries the same caveat.

**Hypothesis 4 — 5m is not the right timeframe**  
Source: XAUUSD project found 30m beat 15m on PF, return, AND drawdown. AU200 at 5m with 2–3 trades/day is likely in the same regime where noise dominates.  
What must happen first: test 15m and 30m versions of the same strategy. The comparison requires the same entry signal, same costs, same exit — only the bar size changes.

---

## 8. Risk and Execution Notes

**The most important unresolved risk**  
The AU200 work has now lost two sets of files to container reclamation because pushes failed. The research protocol's rule — "only git persists" — has been violated twice. Every future AU200 session must push before doing anything else.

**Cost sensitivity (inferred from XAUUSD findings)**  
The XAUUSD champion breaks even at approximately 1.2–1.5 points of slippage. AU200 with tighter stops (5–15 pts) and more trades per day (2.5 T/day vs 2.3/week for XAUUSD) would be more cost-sensitive, not less. At 2.5 trades/day × 250 trading days × 2 sides = 1,250 fills/year. At $100/pt, every 0.1 pt of unmodelled slippage costs $125/year — small individually, but at 1 pt/fill it is $12,500/year against a system whose average net winner (from the table) appears to be around $1,000.

**Flip engine risk**  
A flip on SL hit immediately opens an opposite position. In a fast-moving market (news spike, gap continuation) this can chain multiple losses: SL hit → flip → SL hit → flip, etc. The au200_tbt_flip allows 6 flips, the au200_base_flip allows 3. Without a drawdown figure per row, the actual worst-case exposure is unknown.

**Position sizing**  
`[MISSING]` No sizing model is confirmed for the AU200 screenshot rows. If the $5.14M net assumes fixed 1-lot, it is meaningful. If it is compounding, the headline number is dominated by the last year and tells you nothing about the early years.

---

## 9. What Must Happen Before Any AU200 Number Is Treated as a Result

In priority order:

1. Read `syminfo.mintick` off the AU200 chart. State the number.
2. Confirm the slippage input value. Compute `slippage × mintick` in index points.
3. Add a drawdown column to the table.
4. Grep every strategy file for the relative order of excursion update vs stop check (BUG-019).
5. If BUG-019 is confirmed, correct it and re-run. Discard the pre-correction numbers.
6. Run a corrected random-entry null within the same session filter.
7. Run DSR at the actual trial count (number of configurations swept to produce the nine rows).
8. Run year-by-year breakdown for the top row.
9. Enter one row into RESULTS_LEDGER.md (not before steps 1–8).

---

*This document records what is actually known. It does not record what was hoped, claimed in comments, or visible in a table with no cost model.*
