# STRATEGY EXTRACTION PROTOCOL
## How the System Builds Strategies from Trader Data
### Version 1.0 | Supplement to COGNITIVE_ARCHITECTURE.md

---

## THE SHORT ANSWER

**Yes — but with boundaries.**

The system can extract, structure, critique, and formalize a strategy from a trader's style or data. It **cannot** validate that the edge is real without your backtest data. Strategy extraction is Step 1. Validation is Step 2 (your job).

---

## WHAT THE SYSTEM DOES (Automatic)

When you paste a trader's style, rules, or track record, the system runs this extraction pipeline:

### 1. RULE EXTRACTION
Pulls out every concrete rule the trader uses:
- Entry conditions (price, indicator, pattern, session)
- Stop loss logic (fixed, structural, ATR-based, time-based)
- Target logic (fixed R, next liquidity pool, structure break)
- Position sizing (fixed %, conviction-based, Kelly, martingale?)
- Timeframe(s) and session preference
- Filters (trend direction, volatility, news avoidance)

### 2. STRATEGY FORMALIZATION
Structures the extracted rules into a standardized playbook entry:
```
SETUP: [Name]
CONDITIONS:
  - [Exact condition 1]
  - [Exact condition 2]
ENTRY: [Exact trigger]
STOP: [Exact stop logic]
TARGET: [Exact target logic]
SIZE: [Exact sizing logic]
TIMEFRAME: [Chart time]
SESSION: [When to trade]
MAX TRADES/DAY: [Limit]
FILTERS: [What disqualifies the setup]
```

### 3. GAP & CONTRADICTION DETECTION
Identifies what's missing or contradictory:
- "Trader says 'cut losers fast' but doesn't define 'fast.' Is it 5 pips? 1R? Time-based?"
- "Trader claims 70% win rate but only shows 3 months of data. Insufficient sample."
- "Entry rule uses a 50 EMA, but stop rule ignores the EMA. Disconnected logic."
- "No mention of max daily loss. This is a blow-up risk."

### 4. EXPECTANCY CALCULATION (If Data Provided)
If you give the system:
- Win rate
- Average win (in R or $)
- Average loss (in R or $)
- Sample size

It calculates:
```
Expectancy = (Win% × Avg Win) − (Loss% × Avg Loss)
```
And renders a verdict: **Profitable / Unprofitable / Marginal / Insufficient Data**

### 5. BACKTEST PLAN GENERATION
Creates a specific, testable plan:
- Exact rules to code (or manually test)
- Assets and timeframes to test
- Date range needed for statistical significance (min 100 trades)
- Metrics to track: win rate, R:R, max drawdown, profit factor, Sharpe
- Acceptance criteria: "If expectancy > +0.5R per trade and max DD < 10%, promote to live."

### 6. PLAYBOOK INTEGRATION
If the strategy passes your backtest, the system adds it to PLAYBOOK.md with:
- Status: UNTESTED → BACKTESTING → VALIDATED → FLAGSHIP
- Performance log (updated as you feed results)
- Market conditions where it works vs. fails
- Correlation check: "Does this overlap with existing Setup X?"

---

## WHAT YOU MUST DO (Manual)

The system is an architect. You are the builder and inspector.

| Task | Who Does It | Why |
|------|-------------|-----|
| Extract rules from transcript | System | Pattern recognition |
| Identify gaps/contradictions | System | Critical analysis |
| Backtest the strategy | **You** | System has no historical data |
| Forward-test on demo | **You** | Real-time validation |
| Feed results back to system | **You** | Closes the learning loop |
| Decide to trade live | **You** | Capital is yours |

---

## THE HONEST LIMITATIONS

### 1. The Trader Might Be Lying
The system cannot verify if a YouTuber's "90% win rate" is real. It will:
- Flag "unverified claim"
- Calculate what the expectancy *would be* if true
- Require your independent backtest before validation

### 2. Vague Rules Cannot Be Backtested
If the trader says "I enter when price feels right," the system will:
- Flag as "unformalizable"
- Ask you to define "feels right" in measurable terms
- Or tag the strategy as "discretionary / intuition-based — requires 24+ months of data to validate"

### 3. The System Cannot Run Backtests
Claude Code can write Python backtesting code (using `backtrader`, `vectorbt`, or raw pandas), but it cannot:
- Access historical tick data natively
- Run the code for you (actually, it can run Python, but YOU need the data)
- Know if your data source is clean

**Workaround:** The system generates the backtest script. You run it with your data.

### 4. Market Regime Dependency
A strategy that worked in 2023 may fail in 2026. The system will:
- Ask: "What regime did this trader trade in?"
- Flag regime-specific edges
- Require out-of-sample testing (data the trader never saw)

---

## EXAMPLE WORKFLOW

### Input: You paste this transcript snippet
> "I trade gold on the 15-minute chart. I only trade London and NY. I wait for price to sweep the Asia high or low, then reclaim back inside the range. I enter on the reclaim candle close. My stop is 5 pips beyond the sweep wick. I target 2:1 R. I risk 1% per trade. I take max 3 trades per day. If I hit 2 losses, I stop for the day."

### System Output:

```
=== EXTRACTED STRATEGY ===
SETUP: Asia Sweep + Reclaim (Gold Scalp)

CONDITIONS:
  1. Asset: XAUUSD
  2. Timeframe: 15m
  3. Session: London (08:00–12:00 GMT) or NY (13:00–17:00 GMT)
  4. Price must sweep Asia high OR Asia low ( liquidity grab )
  5. Price must reclaim back inside Asia range on candle close

ENTRY: Close of the reclaim candle (15m)

STOP: 5 pips beyond the sweep wick (structural)
  - If long: Stop = Asia low − 5 pips
  - If short: Stop = Asia high + 5 pips

TARGET: 2:1 R (2 × risk distance)

SIZE: 1% risk per trade (fixed fractional)

FILTERS / RULES:
  - Max 3 trades per day
  - Stop trading after 2 consecutive losses (daily circuit breaker)

=== GAPS DETECTED ===
1. What defines "Asia range"? (High/low of 00:00–08:00 GMT? User must specify.)
2. What if the sweep happens at 07:55 GMT (pre-London)? Is that valid?
3. No mention of trend bias. Does this work in trending vs. ranging markets?
4. No max daily drawdown limit (only trade count limit).
5. No weekend/holiday rule.
6. No slippage assumption. Gold can gap 10+ pips on news.

=== EXPECTANCY ===
Status: UNVERIFIED
The trader did not provide win rate or track record.
To validate: Backtest minimum 100 trades across 6+ months.

=== BACKTEST PLAN ===
1. Data: XAUUSD 15m, 2023–2026
2. Define Asia range: 00:00–08:00 GMT high/low
3. Define sweep: Wick beyond Asia high/low, body reclaims inside
4. Entry: 15m close after reclaim
5. Stop: 5 pips beyond sweep extreme
6. Target: 2R
7. Filters: Only London + NY sessions, max 3 trades/day, stop after 2 losses
8. Metrics: Win rate, avg R:R, expectancy, max DD, profit factor
9. Acceptance: Expectancy > +0.3R, max DD < 15%, profit factor > 1.3

=== PLAYBOOK STATUS ===
Status: UNTESTED
Added to: PLAYBOOK.md → SCALP SETUPS → Asia Sweep Reclaim
Next action: Run backtest. Feed results.
```

---

## HOW TO FEED TRADE RESULTS BACK

After you backtest or trade the strategy, paste results like this:

```
=== FEEDBACK: Asia Sweep + Reclaim ===
Trades: 150
Win rate: 42%
Avg win: 2.0R
Avg loss: 1.0R
Expectancy: (0.42 × 2.0) − (0.58 × 1.0) = +0.26R
Max drawdown: 8R (approx 8%)
Profit factor: 1.21

Observations:
- Worked best in ranging markets (PF 1.45)
- Failed badly in strong trends (PF 0.89)
- London session outperformed NY (PF 1.34 vs 1.08)
- 2-loss circuit breaker saved 3R on choppy days
```

The system will:
1. Update the Playbook entry with real data
2. Revise status: UNTESTED → VALIDATED (if it passes) or GRAVEYARD (if it fails)
3. Update the Belief Register: "B6: Asia sweep reclaims work in ranging regimes, fail in trends"
4. Suggest modifications: "Add trend filter: only take setups when daily ADX < 25"

---

## THE BOTTOM LINE

The system is a **strategy factory**, not a **strategy validator**.

It turns vague trader talk into testable rules.
It finds the holes before you lose money.
It structures your learning so you don't forget what worked.

But **you must run the backtest.** No AI can skip that step.

---

## COMMAND CHEAT SHEET

| What you want | What you paste |
|---------------|----------------|
| Extract strategy from transcript | "Extract and formalize the strategy from this transcript. Identify gaps. Generate backtest plan." |
| Validate a strategy with data | "Here are my backtest results for [Setup Name]. Update Playbook and Belief Register." |
| Compare two strategies | "Compare Strategy A vs. Strategy B. Which has higher expectancy? Lower drawdown?" |
| Fix a broken strategy | "Setup X has positive expectancy in backtest but bleeds in live trading. Diagnose." |
| Build a hybrid strategy | "Combine the entry from Strategy A with the exit from Strategy B. Evaluate." |
