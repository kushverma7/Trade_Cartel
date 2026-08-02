# INDICATOR FORENSICS & HYBRID SYNTHESIS — MASTER BRIEF v2
## Optimised for Kush's Live MCP Stack

---

## ENVIRONMENT
```
vibe-trading      ✅  22 tools, 7 backtest engines  ← PRIMARY BACKTEST
quantconnect-mcp  ✅  60+ endpoints                 ← SECONDARY / VALIDATION
yahoo-finance-mcp ✅  Historical OHLCV               ← DATA SOURCE
financekit-mcp    ✅  Yahoo Finance + CoinGecko      ← DATA FALLBACK
tradingview-mcp   ✅  Multi-market screener          ← ASSET DISCOVERY
financial-datasets-mcp ✅ Fundamentals + price      ← SUPPLEMENTARY DATA
portfolio-mcp     ✅  VaR, Sharpe, Monte Carlo       ← RISK METRICS
```

**Git push is blocked (proxy 403) — do NOT attempt git operations. Save all outputs locally.**

---

## MISSION
Parse every Pine Script indicator in `./indicators/`, translate logic to backtestable signals,
run all combinations across assets and timeframes using the live MCP stack, and synthesise
a single hybrid Pine Script v6 strategy with the highest validated OOS Profit Factor.

**No constraints on instrument, timeframe, or parameter settings.**

---

## PHASE 1 — INDICATOR DISSECTION

### 1.1 Parse all `.pine` files in `./indicators/`
Extract and save to `./output/manifest/indicators_manifest.json`:
- Indicator name, series, version
- Signal components (each named block of logic)
- Entry conditions (exact boolean expressions)
- Exit conditions (TP levels, SL method, flip logic)
- Parameters with defaults
- Timeframe assumptions
- Instrument assumptions

### 1.2 Build signal_components.json
Flat registry of every unique signal primitive found across ALL indicators:
- Supertrend (list every ATR/mult combo found)
- EMA/SMA/WMA (all lengths)
- RSI variants
- MACD variants
- Nadaraya-Watson / RQK
- Range Filter
- AlphaTrend, Andean Trend
- VWAP
- ADX, ATR gates
- Any custom/proprietary logic

### 1.3 Flag duplicates
Mark any indicators sharing >70% identical logic — test only one representative per cluster.

---

## PHASE 2 — ASSET & TIMEFRAME UNIVERSE

### 2.1 Use tradingview-mcp screener to identify liquid instruments
Run screener for:
- Spot metals: XAUUSD, XAGUSD
- Futures: GC1!, SI1!, ES1!, NQ1!
- Crypto: BTCUSD, ETHUSD, SOLUSD
- Forex majors: EURUSD, GBPUSD, USDJPY
Filter: average volume > 50th percentile, ATR% > 0.3%

### 2.2 Fetch historical data via yahoo-finance-mcp
For each instrument that passes screener:
- Timeframes to test: 15m, 1H, 4H, 1D
- Target: minimum 3 years of data (>5000 bars on 1H)
- Fallback to financekit-mcp if yahoo fails
- Log available data ranges to `./output/logs/data_inventory.json`

**Priority assets (always include):**
1. XAUUSD / GC=F — 15m, 1H, 4H, 1D
2. ES=F — 15m, 1H
3. ETH-USD — 15m, 1H

---

## PHASE 3 — BACKTESTING VIA VIBE-TRADING MCP

### 3.1 Primary engine: vibe-trading (7 backtest engines)
Use vibe-trading MCP tools to run each signal combination.

**Translate Pine Script logic to vibe-trading format:**
```python
# For each combo in combination_list:
# 1. Compute entry signals as boolean series
# 2. Define SL/TP rules
# 3. Submit to vibe-trading backtest engine
# 4. Retrieve results
```

**Test matrix per combination:**
| SL Method         | TP Method         |
|-------------------|-------------------|
| Supertrend line   | Opposite signal   |
| 1.5× ATR14        | 2:1 RR            |
| 2.0× ATR14        | 3:1 RR            |

= 9 exit variants per combo per asset per timeframe

### 3.2 Position sizing (all tests)
- Risk per trade: 1% of equity
- Initial capital: $10,000
- Include spread: 2pts Gold, 0.5pts indices, 0.1% crypto

### 3.3 Secondary validation: quantconnect-mcp
For any combo achieving OOS PF > 1.8 via vibe-trading:
- Rerun on QuantConnect for independent confirmation
- Use QuantConnect's walk-forward optimiser
- Flag any result that QuantConnect cannot reproduce

### 3.4 Risk metrics: portfolio-mcp
For shortlisted combos, fetch:
- VaR (95%, 99%)
- Sharpe ratio
- Monte Carlo drawdown distribution (1000 simulations)

---

## PHASE 4 — COMBINATION SEARCH

### 4.1 Tier 1 — Single indicators as-is
Run each parsed indicator exactly as written (translated to vibe-trading format).
This is the baseline.

### 4.2 Tier 2 — 2-component combos
All pairs from signal_components.json:
- Entry signal A + Filter B
- Entry signal A + Exit B
- Filter A + Entry signal B (reversed roles)

### 4.3 Tier 3 — 3-component combos (top performers only)
Take top 20% of Tier 2 results by OOS PF.
Extend each with one additional component from signal_components.json.

### 4.4 Parameter sweep (top 10% of all combos)
Coarse grid over key parameters — use vibe-trading optimiser if available:
```
Supertrend:  ATR [7,10,14] × Mult [1.5,2.0,3.0,4.0,7.0]
EMA:         [20,50,100,200]
RSI:         Len [7,14] × OB/OS [60/40, 65/35, 70/30]
ADX thresh:  [15,20,25]
MACD:        [8/17/9, 12/26/9]
```

Walk-forward validation: 5 folds — NOT simple in-sample curve fitting.
**Reject any combo where OOS PF < 0.85 × IS PF.**

---

## PHASE 5 — SCORING & QUALIFICATION

### 5.1 Disqualification gates (fail ANY = disqualified)
- Total trades < 50 (statistically meaningless)
- OOS trades < 30
- OOS Profit Factor < 1.5
- Max drawdown > 25%
- OOS PF degradation vs IS > 20%
- Logic contains flip exits

### 5.2 results_matrix.csv columns
```
combo_id, components, asset, timeframe, sl_method, tp_method,
total_trades, win_rate_pct, profit_factor_is, profit_factor_oos,
avg_rr, max_drawdown_pct, calmar_ratio, sharpe_ratio,
var_95, avg_trade_bars, oos_degradation_pct,
params_used, qualified, elite_flag, disqualified_reason
```

### 5.3 Tier labels
- `QUALIFIED`: passes all gates
- `ELITE`: OOS PF > 2.0
- `DISQUALIFIED`: fails any gate (include reason)

### 5.4 Benchmark to beat
From prior validated work:
**Daily ST(200/2.0) + AlphaTrend(14/2.0) + EMA200 = PF 1.44, 148 trades, 7yr**
Any QUALIFIED combo below PF 1.44 OOS is not an improvement.

---

## PHASE 6 — HYBRID SYNTHESIS

### 6.1 Identify the winning cluster
From top 5 QUALIFIED combos:
- Components appearing in 3+ = CORE (must include)
- Components appearing in 1-2 = OPTIONAL (include if additive)
- Best SL method (by avg Calmar across top 5)
- Best TP method (by avg PF across top 5)
- Best asset + TF combo

### 6.2 Write HYBRID_STRATEGY.pine (Pine Script v6)
```pine
//@version=6
// ═══════════════════════════════════════════════
// HYBRID STRATEGY [AUTO-SYNTHESISED]
// Generated: [date]
// Core components: [list]
// Backtest OOS PF: [value] | Asset: [asset] | TF: [tf]
// Trades: [n] | WR: [pct]% | Max DD: [pct]%
// ═══════════════════════════════════════════════
indicator("HYBRID", overlay=true)
```

**Pine Script v6 requirements:**
- All parameters as `input.*` with validated defaults from backtest
- Full long + short logic
- Entry: `plotshape()` with "BUY" / "SELL" labels
- SL reference line: `plot()` in contrasting color
- Info table (position.top_right): each component state + current signal
- Three `alertcondition()`: long, short, combined
- Comments on every block explaining its role
- NO flip exits
- NO v4/v5 deprecated syntax (`security()` → `request.security()`, etc.)

### 6.3 Write HYBRID_BACKTEST_REPORT.md
Structure:
```markdown
# Hybrid Strategy Backtest Report

## TL;DR
[3 sentences: what it is, what it does, what it delivered]

## Component Breakdown
[Each component, why it's included, what it contributes]

## Full Statistics
[IS and OOS side by side]

## Equity Curve
[Monthly returns table]

## Worst 10 Drawdown Periods
[Date, depth, duration, recovery]

## Robustness Check
[PF across ±20% parameter variation]

## Live Trading Settings
[Exact inputs to use, alerts to set, risk rules]

## Known Weaknesses
[Market regimes where this underperforms]
```

---

## OUTPUT FILE STRUCTURE

```
./output/
├── manifest/
│   ├── indicators_manifest.json
│   └── signal_components.json
├── logs/
│   ├── data_inventory.json
│   └── pipeline.log
├── results_matrix.csv
├── summary_report.md
├── HYBRID_STRATEGY.pine
└── HYBRID_BACKTEST_REPORT.md
```

**Save all outputs locally. No git push.**

---

## EXECUTION COMMANDS

```bash
# Full pipeline
python run_forensics.py --phase all

# Step by step
python run_forensics.py --phase dissect    # Phase 1
python run_forensics.py --phase universe   # Phase 2
python run_forensics.py --phase backtest   # Phase 3-4
python run_forensics.py --phase score      # Phase 5
python run_forensics.py --phase synthesise # Phase 6
```

---

## ABSOLUTE RULES (never violate)

1. **No git push** — proxy blocked, save locally only
2. **No flip exits** — never exit + immediately reverse on same bar
3. **Walk-forward validation only** — IS optimisation alone means nothing
4. **OOS PF is the only truth** — IS results are reference only
5. **Minimum 50 trades** — below this, disqualify, do not present
6. **Pine Script v6 only** — no deprecated v4/v5 syntax
7. **Log every run** — every combo result goes in results_matrix.csv
8. **Use the MCP stack** — vibe-trading for backtests, QC for validation,
   yahoo-finance for data. Do not build from scratch what MCPs provide.
9. **If an MCP tool fails** — log the error, try the fallback MCP,
   continue pipeline. Do not halt.

---

## MCP TOOL PRIORITY MAP

| Need                   | Primary MCP           | Fallback              |
|------------------------|-----------------------|-----------------------|
| Backtesting            | vibe-trading          | quantconnect-mcp      |
| Historical OHLCV       | yahoo-finance-mcp     | financekit-mcp        |
| Asset universe         | tradingview-mcp       | yahoo-finance-mcp     |
| Risk metrics           | portfolio-mcp         | calculate manually    |
| Crypto data            | ccxt-mcp              | financekit-mcp        |
| QC validation          | quantconnect-mcp      | vibe-trading second run |

