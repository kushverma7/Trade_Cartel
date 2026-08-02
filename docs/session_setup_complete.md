# Complete Session Setup Directory
## Quick Install — Plugins

```bash
claude plugin install github:JuliusBrussee/caveman
claude plugin install github:obra/superpowers
claude plugin install github:thedotmack/claude-mem
```

---

## Plugin 1 — Caveman (token compression)
**Repo:** https://github.com/JuliusBrussee/caveman  
**Install:** `claude plugin install github:JuliusBrussee/caveman`  
**Purpose:** Cuts ~75% tokens by dropping filler. Full technical substance kept.

### Skills
| Command | What it does |
|---------|-------------|
| `/caveman` or `/caveman lite\|full\|ultra` | Toggle terse mode. Full = default. Ultra = most compressed. |
| `/caveman-commit` | Write commit messages — conventional format, ≤50 char subject |
| `/caveman-compress FILEPATH` | Compress CLAUDE.md / todo files. Saves original as `.original.md` |
| `/caveman-review` | Code review — one line per finding, severity-tagged |
| `/caveman-help` | List all caveman commands |
| `/cavecrew` | Spawn subagents: investigator (find code), builder (1-2 file edit), reviewer (diff review) |

### Session prompt prefix
```
Use caveman mode full. Drop articles/filler/hedging. Technical substance exact.
```

---

## Plugin 2 — Superpowers (workflows)
**Repo:** https://github.com/obra/superpowers  
**Install:** `claude plugin install github:obra/superpowers`  
**Purpose:** Enforces proper design → plan → build discipline. Prevents vibe-coding.

### Skills
| Skill | When to use |
|-------|-------------|
| `brainstorming` | BEFORE any new feature/component. Mandatory. |
| `writing-plans` | After brainstorming approved. Creates step-by-step implementation plan. |
| `executing-plans` | Follow plan from writing-plans. |
| `systematic-debugging` | Bug investigation workflow. |
| `test-driven-development` | TDD — red/green/refactor. |
| `verification-before-completion` | Verify change works before marking done. |
| `requesting-code-review` | Prep PR for review. |
| `receiving-code-review` | Process reviewer feedback. |
| `finishing-a-development-branch` | Branch cleanup checklist before merge. |
| `dispatching-parallel-agents` | Run multiple agents concurrently. |
| `subagent-driven-development` | Delegate to subagents for large tasks. |
| `using-git-worktrees` | Parallel work across git worktrees. |

### Session prompt prefix (dev)
```
Use superpowers workflow. Brainstorm before code. TDD. Verify before done.
```

---

## Plugin 3 — Claude-Mem (session memory)
**Repo:** https://github.com/thedotmack/claude-mem  
**Install:** `claude plugin install github:thedotmack/claude-mem`  
**Purpose:** Persistent memory across sessions. Observations, timelines, corpus search.

### Skills
| Skill | What it does |
|-------|-------------|
| `mem-search` | Search past session observations |
| `standup` | Daily standup from memory |
| `babysit` | Monitor background tasks |
| `learn-codebase` | Auto-document codebase into memory |
| `timeline-report` | Timeline of all work done |
| `make-plan` | Generate plan from memory context |
| `smart-explore` | Context-aware codebase exploration |
| `knowledge-agent` | Answer questions from memory corpus |
| `oh-my-issues` | Surface open issues from memory |
| `pathfinder` | Find code paths from memory |
| `weekly-digests` | Weekly summary from observations |
| `wowerpoint` | Generate slides from memory |
| `version-bump` | Bump version with memory context |
| `design-is` | Capture design decisions into memory |
| `do` | Execute task with memory context |

### Session prompt prefix
```
Load memory context. Use mem-search before starting. Log observations as you work.
```

---

## MCP Servers

Configure at: **https://code.claude.com** → New Session → MCP Servers  
(Not CLI-installable — injected by cloud harness)

### Trading / Market Data
| Server | Purpose | Key tools |
|--------|---------|-----------|
| **tradingview-desktop** | Control live TradingView Desktop app | `chart_get_state`, `pine_set_source`, `pine_smart_compile`, `data_get_ohlcv`, `capture_screenshot`, `alert_create` |
| **tradingview-mcp** | Screener — crypto + stocks (Binance, NASDAQ, EGX, BIST, etc.) | `top_gainers`, `top_losers`, `bollinger_scan`, `volume_breakout_scanner`, `coin_analysis`, `multi_agent_analysis` |
| **ccxt-mcp** | Crypto OHLCV via CCXT (multi-exchange) | `get-historical-ohlcv`, `get-price`, `get-top-volumes`, `list-exchanges` |
| **yahoo-finance-mcp** | Yahoo Finance — prices, options, news | `get_historical_stock_prices`, `get_stock_info`, `get_option_chain`, `get_yahoo_finance_news` |
| **financial-datasets-mcp** | Fundamentals + SEC filings | `get_historical_stock_prices`, `get_income_statements`, `get_balance_sheets`, `get_sec_filings` |
| **cerebrus-pulse** | Crypto derivatives — funding, OI, liquidations | `cerebrus_funding`, `cerebrus_oi`, `cerebrus_liquidations`, `cerebrus_screener`, `cerebrus_sentiment` |

### Brokerage / Execution
| Server | Purpose | Key tools |
|--------|---------|-----------|
| **alpaca-mcp** | Alpaca paper/live trading | `place_stock_order`, `get_all_positions`, `get_account_info`, `get_stock_bars` |
| **ibkr-mcp** | Interactive Brokers | `get_ibkr_account`, `get_ibkr_positions`, `get_ibkr_market_data`, `get_ibkr_contract` |

### Analysis / Backtesting
| Server | Purpose | Key tools |
|--------|---------|-----------|
| **quantconnect-mcp** | QuantConnect cloud backtests | `create_project`, `create_backtest`, `read_backtest`, `compile_project`, `create_live_algorithm` |
| **portfolio-mcp** | Portfolio optimization + Monte Carlo | `create_portfolio`, `optimize_portfolio`, `run_monte_carlo`, `get_efficient_frontier`, `get_portfolio_metrics` |
| **optionsflow-mcp** | Options strategy analysis | `analyze_basic_strategies` |
| **finance-mcp** | General finance research + code execution | `execute_code`, `tavily_search`, `history_calculate` |

### Other
| Server | Purpose |
|--------|---------|
| **github** (built-in) | GitHub API — PRs, issues, files, branches |

---

## settings.json — Copy-Paste Config

Save to `~/.claude/settings.json` to replicate this setup:

```json
{
  "enabledPlugins": {
    "caveman@caveman": true,
    "superpowers@superpowers-dev": true,
    "claude-mem@thedotmack": true
  },
  "extraKnownMarketplaces": {
    "caveman": {
      "source": { "source": "github", "repo": "JuliusBrussee/caveman" }
    },
    "superpowers-dev": {
      "source": { "source": "github", "repo": "obra/superpowers" }
    }
  },
  "env": {
    "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"
  }
}
```

---

## Session Flavours — Copy-Paste Prompts

### Trading / Backtest (AU200, Pine Script, Python)
```
Use caveman mode full.
Focus: Python backtesting, Pine Script v6, AU200 5m HalfTrend strategy.
MCP priority: tradingview-desktop > yahoo-finance-mcp > ccxt-mcp.
No git push. Local commits only.
Repo context: HalfTrend v6 backtest results in results/, optimizer in runs/halftrend/.
```

### Crypto Research + Derivatives
```
Use caveman mode full.
Focus: crypto derivatives, funding rates, OI analysis.
MCP priority: cerebrus-pulse > ccxt-mcp > tradingview-mcp.
Use mem-search to load prior research before starting.
```

### Equity / Stock Research
```
Use caveman mode lite.
Focus: equity research, fundamentals, options.
MCP priority: financial-datasets-mcp > yahoo-finance-mcp > optionsflow-mcp.
Use deep-research skill for multi-source fact-checked reports.
```

### QuantConnect Cloud Backtesting
```
Use caveman mode full.
Focus: QuantConnect LEAN algorithm development and backtesting.
MCP: quantconnect-mcp.
No emojis in code (causes QuantConnect parse errors).
Follow QC algorithm class structure: Initialize() + OnData().
```

### Live Trading / Execution
```
Use caveman mode full.
Focus: order execution and position management.
MCP: alpaca-mcp (paper) or ibkr-mcp (live).
Confirm all orders before placing. No market orders without explicit approval.
```

### Portfolio Optimization
```
Use caveman mode lite.
Focus: portfolio construction, risk analysis, efficient frontier.
MCP: portfolio-mcp > yahoo-finance-mcp.
```

### Pure Dev / Code
```
Use caveman mode full.
Superpowers workflow: brainstorm > plan > execute > verify.
TDD. No code before design approved.
```

### Minimal / Clean (no compression)
```
Normal mode. No plugins active. Standard Claude Code defaults.
```

---

## CLAUDE.md Template (paste into repo root)

```markdown
# Project Context

## Instrument
OANDA:AU200AUD — Australian 200 index, 5m bars

## Strategy
HalfTrend v6 — results in results/halftrend_au200_v6_final.pine
Backtest: PF=2.113 | WR=31.5% | DD=-226pts | Score=17.8

## Key Files
- results/halftrend_au200_v6_final.pine — FINAL Pine Script v6
- runs/halftrend/au200_complete_optimizer.py — 1506-config optimizer
- results/filter_results.csv — filter sweep results
- results/exit_results.csv — exit sweep results
- docs/session-setup-complete.md — this setup guide

## Rules
- No git push (403 blocked)
- Local commits only
- Pine v6: shorttitle ≤10 chars, no string concat in plot titles
- ADX via ta.dmi(14,14) not ta.adx()
```

---

## One-Time New Session Checklist

- [ ] Clone repo: `git clone <repo>`
- [ ] Install plugins (3 commands above)
- [ ] Copy `settings.json` to `~/.claude/settings.json`
- [ ] Configure MCP servers at https://code.claude.com
- [ ] Add CLAUDE.md to repo root
- [ ] Start session with matching flavour prompt
