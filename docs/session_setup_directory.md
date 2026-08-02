# Session Setup Directory
## Plugins (install via Claude Code CLI)

```bash
# Install all 3 plugins
claude plugin install github:JuliusBrussee/caveman
claude plugin install github:obra/superpowers
claude plugin install github:thedotmack/claude-mem
```

| Plugin | Repo | Version | Purpose |
|--------|------|---------|---------|
| caveman | https://github.com/JuliusBrussee/caveman | 655b7d9c | Ultra-compressed comms, saves ~75% tokens |
| superpowers | https://github.com/obra/superpowers | 5.1.0 | Brainstorming, planning, TDD, debugging workflows |
| claude-mem | https://github.com/thedotmack/claude-mem | 13.5.6 | Session memory, observations, corpus search |

---

## Skills Available (from plugins above)

### caveman skills
| Skill | Trigger | Purpose |
|-------|---------|---------|
| caveman | `/caveman` | Terse caveman mode (lite/full/ultra) |
| caveman-commit | `/caveman-commit` | Compressed commit messages |
| caveman-compress | `/caveman-compress FILE` | Compress CLAUDE.md/todo files |
| caveman-review | `/caveman-review` | Compressed code review |
| caveman-help | `/caveman-help` | List all caveman commands |
| cavecrew | `/cavecrew` | Spawn subagents (investigator/builder/reviewer) |

### superpowers skills
| Skill | Purpose |
|-------|---------|
| brainstorming | Design before code — REQUIRED before new features |
| writing-plans | Implementation plan after brainstorming |
| executing-plans | Follow implementation plan step by step |
| systematic-debugging | Debug workflow |
| test-driven-development | TDD workflow |
| verification-before-completion | Verify before marking done |
| code-review / receiving-code-review | PR review workflows |
| finishing-a-development-branch | Branch cleanup checklist |

### claude-mem skills
| Skill | Purpose |
|-------|---------|
| mem-search | Search session memory |
| standup | Daily standup from memory |
| babysit | Monitor background tasks |
| learn-codebase | Auto-document codebase into memory |
| timeline-report | Timeline of work done |
| make-plan | Plan from memory context |
| smart-explore | Context-aware codebase exploration |

---

## MCP Servers (configured in Claude Code on Web session settings)

These are injected by the cloud harness — not installed via CLI.
Configure at: https://code.claude.com when creating/editing a session.

| Server | npm/pip package | Purpose |
|--------|----------------|---------|
| tradingview-desktop | (desktop app bridge) | Control live TradingView chart — 78 tools |
| tradingview-mcp | tradingview-mcp | Screener — crypto + stocks (Binance, NASDAQ, EGX, etc.) |
| alpaca-mcp | alpaca-mcp | Alpaca brokerage — orders, positions, market data |
| ccxt-mcp | ccxt-mcp | Crypto OHLCV via CCXT (multi-exchange) |
| finance-mcp | finance-mcp | General finance research + code execution |
| financial-datasets-mcp | financial-datasets-mcp | Stock/crypto fundamentals + SEC filings |
| ibkr-mcp | ibkr-mcp | Interactive Brokers — account, contracts, market data |
| optionsflow-mcp | optionsflow-mcp | Options strategy analysis |
| portfolio-mcp | portfolio-mcp | Portfolio optimization + Monte Carlo |
| quantconnect-mcp | quantconnect-mcp | QuantConnect cloud backtesting |
| yahoo-finance-mcp | yahoo-finance-mcp | Yahoo Finance — prices, options, news |
| github (built-in) | built-in to Claude Code on Web | GitHub API — PRs, issues, files |

---

## settings.json (user-level: ~/.claude/settings.json)

Current config:
```json
{
  "enabledPlugins": {
    "caveman@caveman": true,
    "superpowers@superpowers-dev": true,
    "claude-mem@thedotmack": true
  },
  "extraKnownMarketplaces": {
    "caveman": { "source": { "source": "github", "repo": "JuliusBrussee/caveman" } },
    "superpowers-dev": { "source": { "source": "github", "repo": "obra/superpowers" } }
  },
  "env": {
    "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"
  }
}
```

---

## Session Flavours (copy-paste prompt prefixes)

### Trading / Backtest session
```
Use caveman mode (full). Focus: Python backtesting, Pine Script v6, AU200 5m strategy.
MCP priority: tradingview-desktop > yahoo-finance-mcp > ccxt-mcp.
No git push.
```

### Research session
```
Use caveman mode (lite). Focus: deep research + web search.
Skills: deep-research, mem-search.
```

### Dev / Code session
```
Use caveman mode (full). TDD workflow.
Skills: brainstorming > writing-plans > executing-plans > verification-before-completion.
```

### Minimal / clean session
```
No caveman. No memory. Standard Claude Code defaults.
Plugins: none active.
```
