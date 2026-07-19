# Trade Cartel — Always-On Agent Instructions

**IMPORTANT: At the start of EVERY session, read these files IN ORDER before doing anything else:**
1. `trader_playbooks/COGNITIVE_ARCHITECTURE.md` — THE OPERATING SYSTEM. Three minds (Macro Architect, Microstructure Predator, Profit Engine w/ veto), 8-step thinking process, self-learning layers, rules of engagement. Every analysis follows it.
2. `MEMORY.md` — persistent context, backtest results, decisions, standing rules
3. `trader_playbooks/USER_TRADING_PROFILE.md` — who the user is as a trader; act as their proxy
4. `trader_playbooks/BELIEF_REGISTER.md` — active beliefs w/ evidence + invalidations; update when contradicted (3+ sources -> Belief Review)
5. `trader_playbooks/PLAYBOOK.md` — living setups doc: what's working, what's retired, current regime, rules
6. `trader_playbooks/` (all other files) — the knowledge/confluence layer (candlestick patterns, trader rules). STANDING RULE: this layer is applied as confluence inside every strategy built or tuned — aligned tier-A signals upgrade entries, opposing ones veto/de-risk. It is never delivered as standalone output unless asked.

LEARNING CAPTURE (mandatory): every session that produces analysis, backtest results, or user trade feedback must update BELIEF_REGISTER.md / PLAYBOOK.md / MEMORY.md before ending. If it isn't captured, it wasn't learned.

Then: `git config user.email noreply@anthropic.com && git config user.name Claude`, check `git status`, and push any unpushed commits from previous sessions.

This project has the following tools, MCP servers, and skills installed and active in every session.

## MCP Servers (always active)

- **tradingview** — TradingView MCP server at `/home/user/tradingview-mcp/src/server.js`. Use for chart data, symbol lookups, and market analysis.
- **mcp-search** (claude-mem) — Memory/knowledge MCP at `/home/user/claude-mem`. Use `mem_search`, `timeline`, and `get_observations` tools to recall past decisions and context.

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
