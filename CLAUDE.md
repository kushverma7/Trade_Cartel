# Trade Cartel — Always-On Agent Instructions

**IMPORTANT: At the start of EVERY session, read these files IN ORDER before doing anything else:**
1. `trader_playbooks/COGNITIVE_ARCHITECTURE.md` — THE OPERATING SYSTEM. Three minds (Macro Architect, Microstructure Predator, Profit Engine w/ veto), 8-step thinking process, self-learning layers, rules of engagement. Every analysis follows it.
2. `MEMORY.md` — persistent context, decisions, standing rules
2b. `RESULTS_LEDGER.md` — EVERY backtest result in one table with its sample size, window and settings. Read it before proposing any new engine. Append a row in the same session a result is produced; a PF with no trade count and no date range is not a result. No row is marked VALID without an out-of-sample test.
3. `trader_playbooks/USER_TRADING_PROFILE.md` — who the user is as a trader; act as their proxy
4. `trader_playbooks/BELIEF_REGISTER.md` — active beliefs w/ evidence + invalidations; update when contradicted (3+ sources -> Belief Review)
5. `trader_playbooks/PLAYBOOK.md` — living setups doc: what's working, what's retired, current regime, rules
6. `trader_playbooks/CODE_DELIVERY_PROTOCOL.md` — MANDATORY before writing/delivering ANY Pine code: 7-phase pre-flight (spec freeze, truth table, static analysis, self-review, desk check, output validation, known-limitations report). No code ships without the sign-off.
7. `trader_playbooks/bugs/BUG_REGISTRY.md` — every code bug ever found here, with root cause + prevention. Check new code against it; never repeat a registered bug.
8. `trader_playbooks/skills/SKILL_REGISTRY.md` — validated reusable Pine patterns. Use them by name; don't rewrite them. `trader_playbooks/tests/TEST_REGISTRY.md` — known-scenario test cases; run relevant ones mentally before delivery (see SKILL_EXPANSION_FRAMEWORK.md for how all three registries evolve).
9. `trader_playbooks/AMDM_confluence_strategy.md` — the standing strategy lens: every transcript/data point gets analyzed through AMDM (Model 1 momentum-join vs Model 2 mean-reversion) in addition to the voice layer.
9b. `trader_playbooks/OMNIBUS_PROTOCOL.md` — the standing ITERATION LOOP: build -> static-validate -> deliver -> user tests -> 3-mind diagnosis -> ONE fix per iteration -> verify vs before/after metrics -> learn/document -> repeat until the user says stop. READ ITS ADOPTION NOTE FIRST — the original's voice map has known errors (fabricated "Jared Tendler" voice; #19 is actually Hima Reddy; register holds 21 voices) and the repo register always wins where they differ.
10. `trader_playbooks/` (all other files) — the knowledge/confluence layer (candlestick patterns, trader rules). STANDING RULE: this layer is applied as confluence inside every strategy built or tuned — aligned tier-A signals upgrade entries, opposing ones veto/de-risk. It is never delivered as standalone output unless asked.

KEY LEVELS ARE MANDATORY (user directive, 2026-07-28 — "add it into anything that you build and make sure it also displays the levels as it is in the indicator"): EVERY strategy or indicator built in this repo must embed `trader_playbooks/skills/key_levels_module.pine` verbatim — the ported SpacemanBTC IDWM Key Levels V13.1. Paste the block; never reimplement the drawing (three rewrites were rejected — BUG-013). The module exports `klPrices[]` / `klNames[]` so trade logic can use the same numbers the chart draws. Host must be v6, `overlay=true`, `max_lines_count`/`max_labels_count` ≥ 500, and must not already declare any identifier in the module's collision list.

PORT, DON'T REIMPLEMENT (from BUG-013): when the user supplies working source, the deliverable is a port of THAT code. Deviations are allowed only where the host strictly requires them, and each one is logged as a numbered port delta with a reason.

LEARNING CAPTURE (mandatory): every session that produces analysis, backtest results, or user trade feedback must update BELIEF_REGISTER.md / PLAYBOOK.md / MEMORY.md before ending. Every code bug found must be added to bugs/BUG_REGISTRY.md; every validated pattern to skills/SKILL_REGISTRY.md. If it isn't captured, it wasn't learned.

Then: `git config user.email noreply@anthropic.com && git config user.name Claude`, check `git status`, and push any unpushed commits from previous sessions.

This project has the following tools, MCP servers, and skills installed and active in every session.

## MCP Servers (always active)

- **tradingview** — TradingView MCP server at `/home/user/tradingview-mcp/src/server.js`. Use for chart data, symbol lookups, and market analysis.
- **mcp-search** (claude-mem) — Memory/knowledge MCP at `/home/user/claude-mem`. Use `mem_search`, `timeline`, and `get_observations` tools to recall past decisions and context.

## Kronos Foundation Model (STANDING TOOL — use in every session)

**Kronos** (`/home/user/Kronos`, github.com/shiyu-coder/Kronos, AAAI 2026) — the first
open-source transformer foundation model for candlesticks, trained on 45 global exchanges.
Integration wrapper: `kronos/kronos_signal_filter.py` (in this repo).

STANDING RULE: consult Kronos on every strategy/signal question. Two modes:
- `--mode validate` — walk-forward directional-accuracy test. This is the arbiter for
  "does this timeframe have exploitable structure at all?" Use it BEFORE another round of
  entry-logic tuning. ~50% = no edge at that timeframe/horizon; stop tuning, change the
  timeframe.
- `--mode filter` — current-bar directional bias + predicted high/low envelope. Use to gate
  Pine signal direction and to sanity-check TP/SL targets against a model-derived envelope.

HARD LIMITATION (never paper over this): Kronos is PyTorch and **cannot run inside
TradingView**. Pine has no ML inference. Kronos is the research/filter layer; Pine is the
execution layer. Any claim that Kronos is "in" a .pine strategy is false.

WEIGHTS: requires HuggingFace `NeoQuasar/Kronos-*`. huggingface.co is BLOCKED by this
container's network policy (403 at the proxy) — verified 2026-07-27. torch 2.13 + all deps
are installed and the code path is verified. To run: either allow huggingface.co in the
environment's network settings, or place weights locally and pass `--model-dir`.

## Installed CLI Tools

- **vibe-trading** (`vibe-trading` CLI) — Natural-language finance research and market analysis. Run as: `vibe-trading "<query>"`. Installed globally via pip. Use for market research, stock analysis, crypto data.
- **AI-Trader** — AI-powered trading agent scripts in `/home/user/AI-Trader`. Use for automated trade signals, copy-trading, and market intelligence.

## Skills (249 total — always invoke via the `Skill` tool)

### Superpowers (methodology)
`brainstorming`, `dispatching-parallel-agents`, `executing-plans`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-plans`, `writing-skills`

### TradingView
`tradingview-chart-analysis`, `tradingview-multi-symbol-scan`, `tradingview-pine-develop`, `tradingview-replay-practice`, `tradingview-strategy-report`

### AI-Trader
`aitrader-ai4trade`, `aitrader-copytrade`, `aitrader-heartbeat`, `aitrader-market-intel`, `aitrader-polymarket`, `aitrader-tradesync`

### Caveman (git workflow)
`caveman-cavecrew`, `caveman-caveman`, `caveman-caveman-commit`, `caveman-caveman-compress`, `caveman-caveman-help`, `caveman-caveman-review`, `caveman-caveman-stats`

### Claude-Mem (memory & knowledge)
`claudemem-babysit`, `claudemem-cloud-sync`, `claudemem-design-is`, `claudemem-do`, `claudemem-how-it-works`, `claudemem-knowledge-agent`, `claudemem-learn-codebase`, `claudemem-make-plan`, `claudemem-mem-search`, `claudemem-oh-my-issues`, `claudemem-pathfinder`, `claudemem-smart-explore`, `claudemem-standup`, `claudemem-timeline-report`, `claudemem-version-bump`, `claudemem-weekly-digests`, `claudemem-what-the`, `claudemem-wowerpoint`

### Scientific / Bioinformatics (149 skills — prefix: `sci-`)
Covers genomics, drug discovery, protein structure, clinical trials, bioinformatics pipelines, and more. List all with `/skills` or search with `SearchSkills`.

### Angular
`angular-angular-developer`, `angular-angular-new-app`

### LambdaTest / TestMu (45+ skills — prefix: `testmu-`)
Covers Playwright, Cypress, Jest, pytest, Selenium, WebdriverIO, Appium, k6, Locust, and more testing frameworks. List all with `/skills` or search with `SearchSkills`.

## Always-On Behavior

1. **Memory**: Always use `claudemem-mem-search` or the `mcp-search` MCP tool to recall past context before starting any new task.
2. **Market data**: Use `tradingview` MCP or `vibe-trade` CLI for any financial/market queries instead of web search when possible.
3. **Git workflow**: Use caveman skills for commits, reviews, and stats.
4. **Debugging**: Apply `systematic-debugging` and `verification-before-completion` skills on every bug fix.
5. **Planning**: Use `writing-plans` and `executing-plans` skills for multi-step tasks.

## Tool Locations

| Tool | Path |
|------|------|
| tradingview-mcp | `/home/user/tradingview-mcp` |
| AI-Trader | `/home/user/AI-Trader` |
| claude-mem | `/home/user/claude-mem` |
| superpowers | `/home/user/superpowers` |
| Vibe-Trading | `/home/user/Vibe-Trading` |
| caveman | `/home/user/caveman` |
| scientific-agent-skills | `/home/user/scientific-agent-skills` |
| awesome-agent-skills (index) | `/home/user/awesome-agent-skills` |
