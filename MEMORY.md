# Trade Cartel — Persistent Session Memory

This file is read at the start of every session to restore full context.
Update it whenever new decisions, results, or discoveries are made.

---

## User

- Name: Kush Verma
- Email: kushverma1999@gmail.com
- GitHub: kushverma7
- Repo: kushverma7/Trade_Cartel
- Working branch: claude/confident-fermi-qku0ic
- OS: Mac (runs Claude Code locally) + cloud remote sessions
- TradingView: active, no Premium (limited to ~2 months history on 5m)
- Platform also used: London Strategic Edge (Brue scripting language)

---

## Git & Push

- RESOLVED (2026-07-19): the 403s were caused by NO GitHub App installed
  (only "Authorized"). User installed the Claude GitHub App for
  Trade_Cartel — `git push -u origin claude/confident-fermi-qku0ic` now
  works directly from cloud sessions. No PAT needed anymore.
- Always run: `git config user.email noreply@anthropic.com && git config user.name Claude` before committing
- Hook at ~/.claude/stop-hook-git-check.sh fires on session end — it checks for unverified commits and untracked files

---

## Gold Scalping Strategy — Key Results

### Best Pine Script backtest found
- Symbol: XAUUSD (5m chart)
- Period tested: May 18 – Jul 14 2026 (~2 months, limited by no TradingView Premium)
- **Lookback 22, session filter ON** → **PF 3.656 | Win 51.28% (60/117 trades) | Max DD $1.35 / 0.01%** | Net PnL +$34.19
- Settings: ATR stop 1.2×, TP 2.0×, London open (3–5am ET) + NY open (8:30–11am ET)
- Lookback 18 and filter OFF variants were requested but user did not report results back

### Backtest log
- 2026-07-16 Reversal Sniper Strategy v1 defaults, XAUUSD 5m OANDA, May 25-Jul 16: **PF 0.731 | Win 31.31% (98/313) | -5.26%** — FAILED. Leak: reclaim path fired on auto S/D zone breaks (zones regenerate constantly on LTF → longs into downtrends). Fixed: reclaim HTF walls only + 0.3 ATR flush depth + stopLkb 4. Re-test pending.

### Strategy files in repo
- `strategies/gold_confluence_engine.pine` — **FLAGSHIP** (v6, 430 lines). 4-layer confluence: HTF key levels (daily/weekly open, prev D/W H/L) + gold round numbers ($2.5/$5) + pivot-confirmed supply/demand zones + dual triggers (proven trendline breakout OR liquidity sweep/SFP). Asia range sweeps, level-aware stops/targets, R:R veto, confluence score table, EOD flat. All non-repainting. UNTESTED — needs backtest.
- `strategies/gold_scalper_final.pine` — simpler proven-baseline strategy (v6). Trendline-breakout core (lookback 22, sessions, ATR 1.2x/2.0x) + toggleable filters, all default OFF = exact proven PF 3.656 baseline. Test protocol: enable ONE filter at a time, re-backtest, keep only what raises PF.
- `strategies/gold_scalper_pro_merged.pine` — v6 merged blueprint from Kimi.ai PDF (SMC + levels + quarter theory), untested
- `strategies/trendline_breakout_gold_optimized.pine` — Pine Script v5, full OLS trendline breakout
- (Brue port deleted at user request)

---

## Pine Script Strategy Notes

- Non-repainting: all calculations use `close[1]`, `high[1]`, `low[1]` — never current bar
- OLS linear regression → find pivot → optimize slope (30-step binary search)
- ATR filter: skip if ATR < baseline×0.6 or ATR > baseline×2.5 (avoids dead periods and news spikes)
- Session filter: `time(timeframe.period, "0300-0500,0830-1100", "America/New_York")`
- Commission: $0.07/oz, slippage: 5 ticks
- Best lookback range to test: 10–25 on 5m, 15–30 on 3m, 20–35 on 1m
- Warning: OANDA feed gives "non-standard chart" warning — use Pepperstone or GC1! futures feed instead

---

## Brue (London Strategic Edge) Syntax — Confirmed Facts

- `strategy()` valid kwargs: overlay, precision, capital, initial_capital, commission, commission_type, slippage, pyramiding, **default_qty** (NOT default_qty_value), default_qty_type, currency, symbol, timeframe, mode, broker, account, password
- `persist` = Pine Script's `var` (cross-bar state)
- `in_session("london")` and `in_session("new_york")` for session filtering
- `entry("Long", long)` / `exit("Long X", from_entry="Long", stop=..., limit=...)`
- `shape(condition, arrow_up, location=below_bar, color=aqua, size=small, text="BUY")`
- `bgcolor(condition ? color(green, 92) : na, title="...")`
- NO em dashes `—`, NO Unicode box chars `──`, NO `×` — ASCII only in all strings and comments
- Copying code from chat HTML encodes `<` as `&lt;` — always use the artifact Copy All button or download the .brue file

---

## TradingView MCP

- Only works when Claude Code runs LOCALLY on same machine as TradingView Desktop
- TradingView must be open with `--remote-debugging-port=9222`
- Does NOT work from cloud/remote Claude Code sessions
- MCP config in .mcp.json uses `npx -y tradingview-mcp` (cross-platform)

---

## Installed Tools & Locations

| Tool | Path | How to use |
|------|------|------------|
| tradingview-mcp | `/home/user/tradingview-mcp` | MCP server, auto-active |
| claude-mem | `/home/user/claude-mem` | MCP server (mcp-search), auto-active |
| AI-Trader | `/home/user/AI-Trader` | Scripts for signals/copy-trading |
| Vibe-Trading | `/home/user/Vibe-Trading` | CLI: `vibe-trading "<query>"` |
| caveman | `/home/user/caveman` | Git workflow skills |
| superpowers | `/home/user/superpowers` | Methodology skills |
| scientific-agent-skills | `/home/user/scientific-agent-skills` | 149 sci skills |
| awesome-agent-skills | `/home/user/awesome-agent-skills` | Skill index |

---

## Always Do at Session Start

1. Read this file (MEMORY.md)
2. Read CLAUDE.md for tool/skill instructions
3. Run `git config user.email noreply@anthropic.com && git config user.name Claude`
4. Check `git status` — commit anything untracked before starting new work

---

## STANDING RULE: Internal Knowledge Base as Confluence (2026-07-19)

User directive: material supplied by the user (books, trader transcripts,
patterns, scenarios) is NOT to be delivered back as standalone indicators.
Instead it becomes a PERMANENT internal knowledge layer that I apply as
confluence inside every strategy/indicator I build or tune, to raise
accuracy.

How it works:
1. Knowledge lives in `trader_playbooks/` (mechanical rules, context
   requirements, reliability tiers). Currently: candlestick_patterns.md
   (16 Nison patterns + context gates, Bulkowski tiers).
2. When building or improving ANY strategy: consult playbooks, add
   relevant rules as confluence conditions (e.g., entry requires or is
   upgraded by a tier-A candlestick agreeing with the signal direction;
   counter-signal patterns veto or de-risk).
3. Weighting by tier: A patterns = full confluence vote; B = only with
   trend+location context; C = ignore unless user asks.
4. `indicators/candlestick_engine.pine` remains in repo as the reference
   implementation of the pattern logic, to be inlined into strategies as
   needed — not as a user-facing deliverable.
5. Future user-supplied material gets the same treatment: extract ->
   playbook -> confluence integration -> report accuracy impact from
   backtest, not code dumps (unless user asks for the code).

---

## COGNITIVE ARCHITECTURE ADOPTED (2026-07-19)

User supplied trader_playbooks/COGNITIVE_ARCHITECTURE.md (v3.1) — now the
operating system for all trading work. Key active protocols:
- Three minds on every analysis; Profit Engine has veto
- Conviction scoring 0-12 -> sizing (0-4 none / 5-7 B / 8-10 A / 11-12 A+)
- Expectancy over win rate; unverified edge = exploratory size only
- Pre-mortem on high-conviction trades (>40% combined fail prob -> shrink)
- Scale-out 1/3@1R, 1/3@2R, 1/3 runner; never all-in/all-out
- Flip protocol: thesis invalidated in-trade -> reverse, no ego
- BELIEF_REGISTER.md and PLAYBOOK.md are live docs; update on evidence
- Absolute rules: no fabricated data, no trade without stop, no averaging
  down, always state the counter-case, calibrated confidence only

---

## STANDING RULE: One "Brain" Per Voice, Never Discard Source (2026-07-20)

User directive, applies to every future transcript/PDF/document processed:
1. **Never discard or "unsee" source material**, even when parts are too
   garbled/ambiguous to confidently codify. Preserve the raw text alongside
   the interpretation attempt in the relevant trader_playbooks/*.md file
   (see alchemist_smc_concepts.md section 9 for the pattern: quote the
   confusing original, explain why it wasn't built, keep it on record for
   a later source to potentially clarify). Future analysis may connect
   dots across sources that aren't obvious yet.
2. **One engine (.pine) file per voice/school — extend in place, never
   fork a new file for the same author's later material.** Already the
   pattern in practice: mm_cycle_engine.pine (Steve/MMM4x, extended for
   the Nick/GP v2 transcript), quarterly_theory_engine.pine (extended
   twice across two videos). Apply this strictly going forward — when a
   new transcript arrives, first check whether it's the same author/
   lineage as an existing playbook before creating anything new.
