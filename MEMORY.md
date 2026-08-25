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

### RETRACTED (2026-07-20): small-sample backtest no longer treated as proven
- User instruction: discard the "PF 3.656" result below as evidence — sample
  was only ~2 months / 117 trades (TradingView free-plan history limit on
  5m), too small to call any strategy "proven" or a "flagship" on. The
  number is kept below for the record (never-discard standing rule) but
  MUST NOT be cited as validation anywhere going forward. **Every strategy
  in this repo is currently UNTESTED at a sample size that means anything.**
  No strategy gets "proven"/"flagship" language again until backtested on
  a real sample (target: 6-12+ months, 300+ trades minimum) via a paid
  data feed (Pepperstone/GC1! futures, not the free-plan OANDA feed).

### Retracted backtest (small sample, not evidence)
- Symbol: XAUUSD (5m chart)
- Period tested: May 18 – Jul 14 2026 (~2 months, limited by no TradingView Premium)
- Lookback 22, session filter ON → PF 3.656 | Win 51.28% (60/117 trades) | Max DD $1.35 / 0.01% | Net PnL +$34.19
- Settings: ATR stop 1.2×, TP 2.0×, London open (3–5am ET) + NY open (8:30–11am ET)
- Lookback 18 and filter OFF variants were requested but user did not report results back

### Backtest log
- 2026-07-16 Reversal Sniper Strategy v1 defaults, XAUUSD 5m OANDA, May 25-Jul 16: **PF 0.731 | Win 31.31% (98/313) | -5.26%** — FAILED. Leak: reclaim path fired on auto S/D zone breaks (zones regenerate constantly on LTF → longs into downtrends). Fixed: reclaim HTF walls only + 0.3 ATR flush depth + stopLkb 4. Re-test pending. (Sample size caveat above applies here too — 313 trades on 2 months is still thin.)

### Strategy files in repo (all UNTESTED at meaningful sample size — see retraction above)
- `strategies/gold_confluence_engine.pine` — 4-layer confluence: HTF key levels (daily/weekly open, prev D/W H/L) + gold round numbers ($2.5/$5) + pivot-confirmed supply/demand zones + dual triggers (trendline breakout OR liquidity sweep/SFP). Asia range sweeps, level-aware stops/targets, R:R veto, confluence score table, EOD flat. All non-repainting. Needs a real backtest.
- `strategies/gold_scalper_final.pine` — trendline-breakout core (lookback 22, sessions, ATR 1.2x/2.0x) + toggleable filters. The lookback-22/session-ON default combo is the retracted small-sample setting, kept as the default to re-test on a larger sample, not because it's proven. Test protocol: enable ONE filter at a time, re-backtest, keep only what raises PF on a real sample.
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

---

## STANDING RULE: AMDM Strategy Lens Active (2026-07-22)

User uploaded a full external synthesis package (COGNITIVE_ARCHITECTURE
v3.1 clean copy, STRATEGY_EXTRACTION_PROTOCOL.md, a "NUCLEAR_PROMPT"
operating directive, and THE_CONFLUENCE_STRATEGY.md) and adopted the
**Auction-Momentum Dual Model (AMDM)** as the standing strategy lens.
Full doc: `trader_playbooks/AMDM_confluence_strategy.md`. Originals
archived at `trader_playbooks/sources/amdm_synthesis/`.

1. **From now on, every transcript/data point fed into this project is
   analyzed through the AMDM lens** (Model 1 momentum-join vs. Model 2
   mean-reversion, switched by auction-state) in ADDITION to the
   existing 21-voice confluence layer and three-minds architecture —
   AMDM is a downstream synthesis, not a replacement.
2. **Operating mode: no clarifying questions before acting.** The
   user's directive is explicit ("NO MORE QUESTIONS... do not ask what
   I want") — proceed autonomously on synthesis/build tasks using
   existing repo context, defaulting to reasonable judgment calls
   (documented, not silently made) rather than pausing to ask. This does
   NOT override the separate, harness-level rule about confirming truly
   risky/irreversible actions (force-push, deleting work, etc.) — it
   only removes discretionary "what do you prefer" questions from the
   trading-analysis workflow.
3. **Honesty rules apply to user-supplied synthesis documents too, not
   just extracted playbooks.** AMDM's source document contained broken
   citation markup and at least one unverifiable academic claim
   ("Medhat & Schmeling +16.4%") — flagged in place in
   AMDM_confluence_strategy.md's Audit Note rather than silently
   repeated as fact. The project's "never fabricate data" rule applies
   to everything that becomes part of the standing operating context,
   regardless of source.
4. **AMDM status: SYNTHESIZED / UNTESTED**, same as every other
   strategy in this repo. No backtest exists yet. Nothing changes about
   the PF 3.656 retraction or the "no proven/flagship language without
   a real backtest" rule.

---

## STANDING RULE: Code Delivery Protocol + Registries Active (2026-07-22)

User uploaded and adopted two more framework docs (archived at
`trader_playbooks/sources/amdm_synthesis/`, installed at
`trader_playbooks/CODE_DELIVERY_PROTOCOL.md` and
`trader_playbooks/SKILL_EXPANSION_FRAMEWORK.md`):

1. **CODE_DELIVERY_PROTOCOL.md is mandatory for all Pine code.** The
   7-phase pre-flight (spec freeze + truth table, static analysis with
   a first-3-bars walkthrough, guarded construction, line-by-line
   self-review, bar-by-bar desk check, output validation, and a
   known-limitations report delivered WITH the code) runs before any
   code reaches the user. If time pressure forces a draft, it ships
   with an explicit DRAFT warning, never silently.
2. **Three registries are live and load at session start:**
   - `bugs/BUG_REGISTRY.md` — seeded with the project's 11 real
     historical bugs (BUG-001..011) + 5 cross-cutting lessons. Every
     new bug gets an entry; new code is checked against it.
   - `skills/SKILL_REGISTRY.md` + `skills/*.pine` — reusable patterns
     with HONEST validation statuses (nothing marked "validated on 3+
     assets" until that test has actually been run).
   - `tests/TEST_REGISTRY.md` — deliberately empty of cases until the
     user supplies real chart scenarios; expected outputs are never
     fabricated from imagination (would poison the suite).
3. **Truth-table rule (from BUG-006/007):** any AND/OR condition stack
   in signal logic gets its combinations enumerated before delivery —
   an all-false output column or a nearly-always-true OR branch means
   the logic is dead and must be fixed at spec level.

---

## STANDING RULE: OMNIBUS Iteration Loop Active (2026-07-22)

User adopted OMNIBUS_PROTOCOL.md (installed at
`trader_playbooks/OMNIBUS_PROTOCOL.md` with a corrections preamble;
original archived in sources/amdm_synthesis/). Operating consequences:

1. **The iteration loop is the default work mode** for strategy/engine
   work: build -> static-validate -> deliver -> user tests on chart ->
   3-mind diagnosis of results -> ONE change per iteration -> verify
   against before/after metrics -> document -> repeat. Never declare
   "good enough"; iterate until the user says stop.
2. **One change per iteration, always** — if metrics worsen, revert
   rather than stack a second guess on top (this codifies what the
   topbottom engine's ADX-veto episode already taught).
3. **Profit Engine veto:** any proposed filter/complexity must state
   its expected metric impact; if a change cuts trade frequency
   drastically for marginal win-rate gain, it dies.
4. **Metrics dashboard reporting** after every user-reported test:
   per-model, per-session where available; negative-expectancy
   models get fixed or killed, not tolerated.
5. **CRITICAL CORRECTION carried in the adoption note:** the
   protocol's voice map lists a fabricated "#19 Jared Tendler (HIGH)"
   voice — NO Tendler material exists in this project; voice #19 is
   Hima Reddy, and the register holds 21 voices. The audited per-voice
   playbook headers always outrank the protocol's quick-reference map.
   "Discarded" in that map means excluded from AMDM specifically, not
   removed from the repo (never-discard rule unchanged).

---

## STANDING RULE: Kronos Foundation Model Adopted (2026-07-27)

User directive: download github.com/shiyu-coder/Kronos and "use it always."
Cloned to `/home/user/Kronos`; wrapper at `kronos/kronos_signal_filter.py`.

1. **Kronos is consulted on every strategy/signal question from now on** —
   `--mode validate` before any further entry-logic tuning (it answers
   "does this timeframe have structure at all?"), `--mode filter` for
   directional bias + a predicted high/low envelope to check TP/SL against.
2. **Hard limitation, never paper over:** Kronos is a PyTorch transformer
   and CANNOT run inside TradingView Pine. Kronos = research/filter layer,
   Pine = execution layer. Never claim Kronos is "inside" a .pine file.
3. **Environment blocker (verified 2026-07-27):** huggingface.co returns 403
   at the container proxy, so the NeoQuasar/Kronos-* pretrained weights
   cannot be downloaded here. torch 2.13 + deps installed, code path
   verified, CSV loader tested. Unblock by allowing huggingface.co in the
   environment's network policy, or supply weights via `--model-dir`.
4. **First job for Kronos once weights land:** run `--mode validate` on the
   same XAUUSD 5m Jun-Jul window used for the six PF 0.82-0.89 engine tests.
   If directional accuracy is ~50%, that is the answer to why every entry
   architecture landed at the same PF, and the decision becomes "change
   timeframe," not "tune again."

---

## Recovered 2026-07-29 — facts that had been lost

Full detail: `trader_playbooks/sources/session_archive/`.

### Session-data reality (know this before trusting "I remember")
- Raw transcripts on the container covered **only 2026-07-22 → 07-29**.
  Everything before **2026-07-13** (first commit) is unrecoverable from my side.
- **claude-mem has never held any data** — no database has ever existed on the
  box. The CLAUDE.md instruction to search it at session start has always been
  a no-op. Continuity has rested entirely on this file and the playbooks.
- `/root/.claude/` does not survive session reclamation. **Only git persists.**
  Anything that matters is committed in the session it happens.

### The first PF>1 configuration (was missing from the repo entirely)
`trade_cartel_topbottom_engine.pine`, PF-analog **1.11**:
`useTestFail=false` · `closePosPct=0.2` · `rsiOb=72` · `rsiOs=31` ·
`useTrendVeto=false` · `cooldown=20` · `minReArmAtr=1.5`
User confirmation, verbatim: *"oversold is 31 rest is as told"*.

### STANDING RULE — three strikes on trend filters
Three independent results now say a higher-timeframe / trend veto makes
things WORSE, not better:
1. `useTrendVeto` on the topbottom engine — input label carries the warning
2. ADX veto — reverted
3. HTF bias MA on the trendline engine — PF 0.882 → 0.819, reverted
Do not add a fourth without a specific reason why it differs from these
three, and ship it default-OFF as an A/B toggle if it is added at all.

### STANDING RULE — a screenshot is not a specification
Two corrections from the user, same root failure:
- *"i never told you to create supertrend or similar settings, i dont you to
  make sure it only presents signals like the screenshot."* → a chart image is
  a request to **restyle an existing engine's display**, not to build a new
  algorithm.
- *"i never restricted you to any settings. i told you to find me the best and
  accurate signal printing."* → **a number visible in a screenshot is not a
  constraint.** Do not copy it and then defend it.

### OPEN THREAD — unanswered since before 22 July
After the SuperTrend correction I asked **which engine the user wanted
restyled** to the clean line + Buy/Sell-label look. That question was never
answered; it fell off when the context compacted. Still open.

---

# ►► CURRENT STATE AND NEXT ACTION (2026-07-31)

Read this before doing anything. It replaces having the previous
conversation.

## Where the project actually stands

**Every result ever produced here is below the noise threshold.** Not close
to working, not needing another tuning pass. See RESULTS_LEDGER.md: 17 runs,
zero out-of-sample tests, and a Deflated Sharpe of 0.08 on the best of them
against a 0.95 bar. The expected best Sharpe from 17 attempts on data with no
edge is 0.107/trade; the best engine achieved 0.044 — less than half of it.

**Do not build an 18th engine.** That instinct is what produced the ledger.

## The bar, concretely

At n=521 and a 44% win rate a result must reach **PF ~1.45** to clear DSR
0.95. Anything between 1.0 and 1.4 at this sample size is search noise.

## What is built and working (all committed)

- `backtest/` — offline stack: non-lookahead level construction, fast engine
  (0.14s per 14k bars), greedy optimiser with a LOCKED train/test split,
  deflated Sharpe + PBO, tolerant CSV loader (gz/zip/chunked/any date format).
- `backtest/test_engine.py` — 5 hand-computed accounting tests, all passing.
  Run these first if anything is ever changed in the engine.
- `backtest/lse_client.py` — wraps the official `lse-data` PyPI client.
- Pine engines in `strategies/` with per-voter and per-level scorecards, so
  one TradingView run ranks all contributors instead of guessing combos.

## The single blocker: no market data

The sandbox sits behind a policy-enforcing egress proxy. Only PyPI, npm,
crates, Go proxy and Anthropic are reachable. Every market-data host —
londonstrategicedge.com, huggingface.co, Yahoo, Stooq, Binance,
tradingview.com — fails at the CONNECT tunnel. **This is environment network
policy, not authentication.** `pip install` works, which is why the official
LSE client and backtrader installed fine.

Two ways forward:
1. Allowlist `londonstrategicedge.com`, `api.londonstrategicedge.com` and
   `huggingface.co` in the environment's network settings, then
   `python3 -m backtest.lse_client --check`. This also revives Kronos.
2. Export XAUUSD 15m from the LSE builder, gzip, drop in the repo, then
   `python3 -m backtest.inspect_csv <file>`.

## The order of work once data exists

Do NOT start with the optimiser. Greedy search produced PF 1.73 and PF 2.49
on synthetic random-walk data — search manufactures in-sample winners out of
noise, reliably.

1. Kronos `--mode validate` — does XAUUSD 15m have directional structure at
   all? ~50% means stop tuning entries and change timeframe.
2. Baselines — buy-and-hold, and random entries with identical stops and
   targets. No engine here has ever been compared against either.
3. Only then `python3 -m backtest.optimize --csv <file>`, and judge the
   OUT-OF-SAMPLE number against PF 1.45.

## Credentials

The LSE API key lived in a gitignored `.env` which does NOT survive a new
container. For persistence set `LSE_API_KEY` in the environment's own
variable settings — `backtest/lse_client.py` prefers it over `.env`.

## STANDING RULE: Verify push BEFORE doing the work (2026-08-02)

**Earned twice, the same way, in three days.** A session built the AU200
research files (`research/au200_indicator_v1.pine`,
`au200_base_flip_v1.pine`, `au200_tbt_flip_backtest.pine`,
`top_bottom_entry_v1.pine`, `top_bottom_strategy_v1.pine`), committed them
LOCALLY, hit a 403 on push, carried on working, and lost all of it when the
container was reclaimed. A second session then produced a nine-row AU200
results table with PFs of 3.46 to 7.11 and pushed none of it — so the report
survives only as a screenshot with no code, no data, and no way to check a
single number in it.

Containers here are ephemeral. Local commits are not saved work. **Only
pushed git objects persist.**

**The rule:** at the START of every session, before any real work, make a
trivial commit and push it. If the push 403s or otherwise fails, fix that
FIRST — it is a blocker, not a nuisance to deal with later. Then push again
at every natural checkpoint, not at the end. A 403 discovered after four
hours of research costs four hours; discovered in the first minute it costs
nothing.

**Corollary for reports:** a results table whose code was never pushed is
not a finding, it is a rumour. Do not record it in RESULTS_LEDGER.md, do not
act on it, do not carry it forward into another session's assumptions.

---

## Standing discipline (earned the hard way)

- A PF with no trade count and no date range is not a result.
- A suspiciously LOW trade count is an execution symptom, not selectivity
  (BUG-012 struck twice; every engine now shows Signals/Filled/Fill rate).
- Trend and HTF filters have made results worse three separate times.
- A screenshot is not a specification.
- If the user supplies source, port it — do not reimplement it.


---

# ►► SESSION 2026-07-31 (later) — key levels wired into the trade logic

The user asked, from a chart screenshot: *"i want you to enter and exit the
trade on key levels. reverse the signal as it touches the key level."*

**What was measured** (full detail in RESULTS_LEDGER.md, beliefs H78/H79):

- Level touch as the ENTRY has no edge in either direction. Fade and break
  both lose, and both sit on PF 1.00 **with costs zeroed**. Entry stays on
  the breakout. `backtest/kl_reverse.py` is the engine that showed this;
  keep it, do not re-derive it.
- Level touch as the EXIT, counter-trend side only, closing 75%: train PF
  1.244 → 1.289, OOS 1.580 → 1.610, full period 1.333 → 1.379 with a
  smaller drawdown. Small but consistent across both halves.
- **Reversing at the level on both sides is the worst config tested**
  (train PF 0.932, net −14.8%). Shipped as a toggle, defaulted OFF, with
  the numbers in its tooltip. If the user turns it on and reports a bad
  result, that is the expected outcome, not a bug.

**Structural change to `gold_trend_trailing.pine`:** the whole strategy
block was moved BELOW the embedded key-levels module. The module fills
`klPrices[]` as it draws; code above it reads the previous bar's array.
Nothing about the module itself was touched. Do not move the strategy back
above it.

**`backtest/trend.py` gained `kl` / `kl_take` / `kl_flip` / `kl_tol_atr` /
`kl_shorts_only`**, all defaulted off, so every ledger row still
reproduces. Verified: baseline is still PF 1.333 / +152.5% / 921 trades,
and all five accounting tests pass.

**Delivery reminder learned this session:** the repo file being fixed is
not the same as the user having the fix. The `trailMultEE` compile error
reached the user because the artifact was never republished after the sed
fix. Republish the artifact AND re-send the file every time the Pine
changes.


---

# ►► SESSION 2026-07-31 (third pass) — confluence merged

User: *"i was keep key levels and SMA 2000 also a confluence. see what can
u do and merge them together."*

**Shipped:** a second SMA (2000, ~3 weeks) must agree with the fast one
(750) and with the EMA2000 regime gate before any entry. Key levels stay
as the EXIT. Full period PF 1.379 → 1.421, drawdown 12.30% → 9.63%,
return/drawdown 12.68 → 16.36. Both halves agree. Belief H80.

**Rejected, with numbers in the tooltips so they are not re-tried blind:**
- SMA2000 replacing SMA750 (train PF 1.181 vs 1.289)
- requiring only 1 of the 2 SMAs (1.149)
- key level near the ENTRY as a confluence (full-period net +157.7% →
  +120.9%, same at 0.5/1.0/2.0 ATR — not a tuning problem)
- sizing up when both agree (+146% train net but 21.8% drawdown; leverage,
  not edge)

**The dashboard now shows a live confluence read-out** (LONG 3/3 /
SHORT 3/3 / none, which filters agree, and the next key level) because the
user trades this manually as well as backtesting it.

`backtest/trend.py` gained `sma2_len`, `sma2_mode`, `conf_min`,
`conf_size`, `kl_entry_atr` — all off by default; baseline still PF 1.333
/ +152.5% / 921 trades and all five accounting tests pass.


---

# ►► SESSION 2026-07-31 (fourth pass) — LIVE CONTRADICTED THE RESEARCH

The user ran the confluence build on TradingView, Feb 2 - Jul 31 2026:
**PF 0.702, -2.99%, 65 records, largest win 92.94 vs largest loss 120.38.**
Python on the identical window and settings: PF 1.385, +3.54%, largest win
239.48 vs largest loss 95.00.

**In a system with no profit target the largest winner MUST dwarf the
largest loser.** TradingView reports the opposite. That is the tell, and it
is worth more than either profit factor: it says winners are being cut.

**What was found:** the Pine module exports 36 levels; levels.py had 18.
Median distance to the next level ahead is 0.46 ATR on the real set against
a 6 ATR stop. A 75% take there risks 6 to make 0.46. Logged as BUG-017 with
a three-step pre-ship check (compute target/stop in ATR; if < 1.0 the
structure loses before any trade).

**What was NOT resolved, and must not be claimed as resolved:** re-running
Python against the true 33-level set still returns PF 1.385 on that window.
The density finding explains HOW a level exit destroys a trend system; it
does not close the +3.54% vs -2.99% gap. Remaining suspects, in order:
Pine's strategy.close(qty_percent=) interacting with a live strategy.exit
on the same entry ID; current-period vs previous-period level values in the
module's 4H/session levels; fractional-contract handling (Pine closes 1.5
of a 2-lot, Python floors to 1).

**RESOLVING THIS NEEDS TRADINGVIEW'S TRADE LIST**, which this container
cannot read. Ask the user to export it, or run the MCP on their Mac.

**Shipped defaults changed:** useKL now OFF in both builds; klMinAtr added
(default 3.0 ATR) so a re-enabled level exit skips targets that are too
close. The default configuration is now the one that cross-validated
cleanly earlier (Python +6.94% vs TradingView +7.57% on this same window).

**Also worth knowing:** SMA2000 confluence HURTS this particular window
(+3.47% with it vs +6.06% without) even though it improves full-period
drawdown. It is a train-period improvement the recent falling market does
not like. Left ON because the full-period and both-halves evidence supports
it, but flag it if the user reports more weak recent results.


---

# ►► SESSION 2026-07-31 (fifth pass) — return review

User asked for a full-session review to increase returns.

**Shipped, XAUUSD 30m, full 6.7 years, gap-aware fills:**
+660.2% at 17.68% drawdown, PF 1.626, against buy-and-hold +179.1% at
29.08%. **First config in this project to beat buy-and-hold on raw return
as well as on risk.**

**What produced it:** pyramiding (H81) — add 2 units every 3 ATR of
favourable move, shared trailing stop. Improved all five walk-forward
slices. Also 30m over 15m (better PF, return AND drawdown in both halves).

**Corrections made to earlier claims — do not repeat the old versions:**
- "Wider trail is better" was PF-only. On RETURN it is FALSE: trail 20 ATR
  gives PF 1.659 but +23.5% against trail 6's 1.243 and +85.4%. Risk-based
  sizing shrinks the position as the stop widens.
- Every number in the ledger before BUG-018 used exact-stop fills and is
  optimistic. Use gap_fill=True from now on.

**Honest limits on the headline number:** the pyramid parameters were
chosen after seeing all five walk-forward slices, so those slices are not
out-of-sample for that choice. What supports it is that all six variants
improved all five slices. Pyramiding is a VARIANCE MULTIPLIER, not an
edge — on random entries it triples the median and quadruples the spread.

**Pine note:** `pyramiding=5` had to be added to the strategy() header.
Pine's default of 0 SILENTLY IGNORES strategy.entry while a position is
open — the adds would have placed no orders and raised no error.


---

# ►► SESSION 2026-07-31 (sixth pass) — knowledge layer finally measured

The user asked whether the instructions and the supplied knowledge had
actually been used. **They had not been, in this session.** Everything
built was quantitative; `backtest/voices.py` held all 22 register voices
vectorised and untouched. Corrected, measured, logged as H82.

Finding: the voice layer is REDUNDANT with the engine's trend filters. A
net-score veto at threshold 0 changes nothing; at 4 it removes 13 of 799
trades. At net >= 6 it is a real but small risk gain (OOS PF 1.879 ->
1.954, OOS drawdown 12.88% -> 10.44%) costing ~9% of return. As a
STANDALONE ENTRY the voice score beats every other supplied entry (full PF
1.468 vs DE Hybrid 1.213 vs SMA-200 cross 0.920).

**Standing correction for future sessions:** apply the knowledge layer at
BUILD time, not when challenged. The rule is in CLAUDE.md and it was
skipped for six passes.

**USER NOW HAS TRADINGVIEW PREMIUM (2026-07-31).** That unlocks DEEP
BACKTESTING in the Strategy Tester, which is the missing piece for
cross-validation: until now every live run covered only the bars the chart
had loaded (Feb-Jul 2026, or Jan 2025-Jul 2026), never the 6.7 years the
research uses. Ask for a deep backtest over the full range before trusting
or doubting any Pine-vs-Python gap. Premium also raises intraday history to
20k bars and allows 400 alerts.

---

# ►► CURRENT STATE AND NEXT ACTION (2026-08-02, supersedes the 07-31 block)

## Where the project stands

`strategies/gold_trend_strategy.pine` is the validated champion and is
UNCHANGED by this session's work. XAUUSD 30m, Balanced, 0.20 pt slippage:
**PF 1.583 / +1,591.7% / 33.63% DD over 2,370 orders, Aug 2019 – Aug 2026**,
confirmed live on TradingView Premium against an independent research engine
(net return agreed to 98.2%, drawdown to 0.23pp). DSR 0.9996, PBO 0.099.
It embeds no key levels, uses no price grid, and tests stops against low/high
— so none of the defects below touch it.

## What this session did

**1. Wrote four prompts** (repo root, all copy-pastable and self-contained):
`SESSION_HANDOFF_PROMPT.md` (which strategy is best),
`ARCHIVE_SWEEP_PROMPT.md` (what got dropped between source and code),
`RESEARCH_PROTOCOL_PROMPT.md` (how not to produce a wrong number),
`RECOVERY_PUSH_PROMPT.md` (push before the container is reclaimed).

**2. Audited 73 uploaded files** — reconciled by hash: 61 unique, 12
duplicates, everything archived. Full writeup in
`trader_playbooks/AU200_UPLOAD_AUDIT_2026-08-02.md`. Headline: the entire
AU200 programme is unsafe. Nine documents describe one system at PF 1.74 to
5.41 while its own internal baseline is PF 1.116 on 980 trades; drawdown is
understated ~5x; 75% of seven years' profit comes from five months and ten
trades; and with flips disabled the base system returns PF 0.79 and
−$369,270. Do not trade any configuration from it.

**3. Registered BUG-019 … BUG-027.** 019-023 were this project's own
fixed-but-never-logged findings. 024-027 came from the uploads:

| id | where | defect |
|---|---|---|
| 024 | `skills/key_levels_module.pine` | yearly H/L leak future data into `klPrices[]` |
| 025 | `victor_aimstar_past_strategy_v1.pine` | long and short conditions were the same expression |
| 026 | `bigbeluga_smart_money_concepts.pine` | `5/len` int-divides to zero for len>=6 |
| 027 | uploaded Quarter Theory module | filter is a constant on 79.8% of bars; target/stop 0.065 |

**4. Fixed 024, 025, 026** and propagated the 024 gate to all eight
strategies that embed the module. pine_lint clean on all nine files.

## Standing corrections earned this session

- **Verify a third-party audit before acting on it.** The uploaded blueprint
  called all 20 `request.security()` calls in the key-levels module
  repainting. Ten use the correct `[1]`-offset idiom; stripping `lookahead_on`
  as advised would have BROKEN them. Only four leak, and only two reach trade
  logic.
- **A misleading comment is not evidence.** The AU200 flip stop is labelled
  "profit side" and commented "inverted" while the arithmetic is correct. An
  earlier claim in this session that the flip booked guaranteed wins was
  wrong and was retracted. Read the code, not the label.
- **Hash before reading.** 12 of 73 uploads were duplicates.

## Next actions, in order

1. **Re-run the eight key-level strategies** now that BUG-024 is gated. Any
   prior ledger row for them was computed with the yearly leak live and is
   optimistic. `gold_trend_trailing.pine` has a ledger row and needs one.
2. **Build the two methods worth adopting** from `MASTER_BLUEPRINT.md`:
   (a) bar-permutation Monte Carlo that RE-OPTIMISES on each permutation —
   stronger than our corrected null because it prices in data-mining bias;
   into `backtest/overfit.py`. (b) MAE/MFE 80th-percentile derivation of stop
   and TP1 — the correct structural answer to BUG-017; into `exit_lab.py`.
3. **Test the two unbuilt exit rules already logged in BELIEF_REGISTER.md**:
   Dave's 21-EMA confirmed structure trail, and Valentini's ADR-anchored
   partial. Both are exits, which is where this repo has measured the edge.
4. **A-grade-only filtering** is the one directly actionable finding from the
   uploads: in the AICartel CLC backtest, 3/3 signals returned +4.08R while
   2/3 returned −4.61R. Worth testing as a general confluence-threshold rule.

## Unfinished

`gold_confluence_engine_1.pine` (uploaded, archived) is the most technically
literate file in the upload set — it independently found BUG-027's units
problem and documents the lookahead idiom correctly. Its $5 and $10 gold
grids clear the BUG-017 gate (1.29 and 2.58); its $2.5 minor grid does not
(0.646) and should be dropped from targeting. It has never been backtested.

---

# ►► CURRENT STATE AND NEXT ACTION (2026-08-03, supersedes the 08-02 block)

## What happened this session

Four rule books were tested end to end: the Level-to-Level Model V1, V2 and V3,
then the ORB rule book. Twelve distinct components across them. **Zero survived
an independent control.** Four of the twelve were positive results of mine that
the control then reversed.

- V1 PF 0.59 → V2 PF 1.00 → V3 Setup A PF 1.22 on gold, monotonic across five
  settings and positive on four timeframes — then killed by the **second
  instrument**. On US30 the ungated control beat the CPR gate on both
  timeframes and the gated arm flipped sign between halves.
- ORB: gold negative in all twelve base configurations AND negative when faded.
  US30 marginally positive. Best cell beats its matched control by z = +1.47
  after ~50 cells searched. Not valid. Full numbers in RESULTS_LEDGER.md.

## Two rules that came out of it, both now standing

1. **Timeframe robustness is not generality.** Resampled bars are not
   independent observations. A result that holds on 15m/30m/60m/4H of one
   symbol has been tested once, not four times. Only a second instrument counts.
   (This is what V3 tripped over.)
2. **Run the mirror.** For any directional strategy, run the same entries with
   direction flipped and geometry mirrored. The two avgR figures should sum to
   about minus two costs. Both positive = an accounting leak. This is how
   BUG-029 was found, and it found it faster than reading the code would have.

## The one thing that keeps surviving

The exponent gap — MAE diffusion 0.493 vs MFE 0.558 on XAUUSD, against 0.500
for a pure random walk. It was re-observed independently again in ORB Priority
5: expectancy rose monotonically from 1R to 3R targets at both range sizes.
Every entry-timing rule tested in this repo has failed a cost-matched control;
the hold-time asymmetry has not.

## NEXT ACTION — stop testing entries

The evidence says the next session should work on **exits and position holding
applied to the already-validated engine**, not on a thirteenth entry filter.
The champion `strategies/gold_trend_strategy.pine` (PF 1.583, +1,591.7%,
33.63% DD) is untouched by any of this work and embeds no key levels, so it is
unaffected by BUG-024. `backtest/exit_lab.py` already has the two tools needed:
a per-bar ATR trail override and the structure trail.

Still open from before, in priority order:
1. Re-run the eight key-level strategies now that BUG-024's yearly export is gated.
2. Resolve BUG-028 — decide whether CYH/CYL means current-year running or
   previous-year static, and make `levels.py` and the Pine module agree.
3. Add volume-profile levels (POC/VAH/VAL) to `levels.py`; reconcile the
   18/33/36 level-count mismatch.

---

# ►► CURRENT STATE AND NEXT ACTION (2026-08-05, supersedes the 08-03 block)

## What happened this session

The user asked for **deeper research on every file, PDF, text and transcript
supplied**. Two things came out of it.

### 1. A methodology error was found and corrected

The Quarterly Theory study delivered earlier as a negative finding was run
**without reading the two QT source PDFs**, which were on disk the whole time in
`trader_playbooks/sources/` under normalised names
(`quarterly_theory_daye_compiled*.pdf`) — not under the numeric-prefixed upload
names, which is why an earlier search for them came back empty. Read now, they
contradict `research/levels_qt.py` in four places: weekly cycle is Tue–Fri not
Mon–Thu; daily blocks are New York time not UTC; there are two AMD forms not
one; session quarters are expansion, not manipulation.

Re-run on the source definitions with a surrogate null and a drawdown-matched
control (`research/qt_corrected.py`, `qt_null.py`, `qt_friday.py`), **the
rejection stands** — but it now rests on the right definitions. Details in
BELIEF_REGISTER and RESULTS_LEDGER.

Three things worth carrying forward:
- The weekly cycle has **no structure at all** against surrogates (max |z| 2.62).
- The daily cycle's real effect is that the **NY morning (06:00–12:00 NY) sets
  the day's high 36.5% of the time** (surrogate 18.8%, z +17.4). Real and large,
  but it is session volatility; QT names the wrong quarter.
- **Friday carries a disproportionate share of the champion's edge** — removing
  it drops net/DD from 27.3 to 5.4 — yet trading Friday alone compounds 40% less
  at matched risk. Do not filter on it in either direction.

### 2. Every falsifiable claim in the source library was batch-tested

`research/source_battery.py` — 10 arms × 4 horizons, forward move in ATR against
the **unconditional** move. **Zero survivors at |t| > 3.** Pin bars, inside
bars, fakeys, and the ported "Big Players Entry" indicator all fail; the Big
Players indicator is *negative* as specified. The one-dollar quarter grid
(.00/.25/.50/.75) is flat to four decimal places on ~78,000 touches per level.
The NY-open claim is inverted: volatility doubles but reversals become *less*
frequent — it is an expansion window, which corroborates the breakout champion
rather than contradicting it.

**Sixteen independent families of entry/level ideas have now failed controls.**
The shipped system is unchanged; nothing was adopted.

## Standing rules added

1. **Read the uploaded source before studying a named methodology.** Code from
   the document, not from recall. A negative finding reached without reading the
   source is not a finding.
2. **Source files live in `trader_playbooks/sources/` under normalised
   filenames.** The original numeric-prefixed upload names are not on disk;
   searching for them returns nothing and that is not evidence of absence.
3. **Higher PF at fewer trades is not an improvement.** Compare at matched
   drawdown and read net/DD.

## Next action

- The user said "Wait i will give you the data" regarding **5-minute gold**.
  That data has not arrived. When it does, run the champion's timeframe study on
  5m and 15m.
- Remaining unexamined sources, in descending value:
  `wd_gann_master_commodities_course.txt` (815KB),
  `hima_reddy_trading_methodologies_of_wd_gann.txt` (225KB),
  `hougaard_trading_manual.txt` (214KB),
  `trader_dale_order_flow_trading_setups.txt` (140KB),
  `all_indicators_dump.txt` (359KB), `ochoa_profiting_with_pivot_based_concepts`,
  `john_person_candlesticks_cbot_2006`, `key_levels_guide`,
  `agent_2_1_cluster_detector_training`, and `sources/raw_transcripts/` (21 files).
  Extract only *exactly-specified* rules from each and add them as arms to
  `research/source_battery.py` — the harness and the null are already built.

## Update, same session — the remaining sources are now done

`research/source_battery2.py` covered the long-form books (Person, Ochoa,
Hougaard, Trader Dale). **6 of 40 directional arms cleared |t| > 3 and every one
is a refutation, not a find:**

- **Ochoa's headline rule — "buy support in a bull trend" — is a significant
  loser** on gold 30m: −0.196 ATR at 32 bars against +0.323 unconditional
  (t = −4.92, n = 1911).
- **Hougaard's 89MA is real but unshortable.** Above it gold drifts +0.448 ATR
  per 32 bars, below it +0.162, unconditional +0.323. Below the 89MA the drift
  is *slower, not negative* — a short on that signal still loses. Same
  bull-market artifact as B-0xx in new clothes.
- **Ochoa's pivot-width claim** (narrow pivot range → breakout day) points the
  direction he predicts and is **not significant**: ρ = −0.027, p = 0.22 over
  2,071 days. This was the most promising claim in the library, since the
  champion is a breakout system.
- Person's HCD and Jack Hammer add nothing over the pin bar already tested,
  even though they require a confirmation bar.

**No regime gate beat the ungated champion at matched 25% drawdown.** Three of
seven posted a *higher profit factor* and all seven compounded less.

## The rule that keeps re-earning itself

**A filter that removes trades raises profit factor almost automatically — the
survivors are the easy ones. Score at matched drawdown and read net/DD.** This
has now caught three separate false positives (the Friday gate, the narrow-pivot
gate, the inside-value gate). Treat any "PF went up" claim as unproven until the
drawdown-matched number is on the table.

## Coverage gaps, stated rather than hidden

Not everything in the library is testable here, and these are gaps, not passes:
Trader Dale's Order Flow confirmation step needs a bid/ask ladder this desk does
not have; `agent_2_1_cluster_detector` is SEC Form 4 insider clustering on US
equities with no XAUUSD application; the Gann material states no falsifiable
mechanical rule; Hougaard's discretionary crowd-reading is not mechanical by
construction.

## Next action (revised)

The source library is exhausted for testable content. **Seventeen independent
families of entry, level and regime ideas have now failed controls.** Further
entry research against this library has a poor prior; if more work is wanted,
the productive direction is the exit and the sizing, which is where the
champion's edge has always been.

5-minute gold work is dropped at the user's instruction (2026-08-05).

## Update 3, same session — the first real candidate in eighteen families

The user supplied a scalping checklist, a reversals note, and a multi-timeframe
trend-break plan. One item out of all of it beat the baseline.

### THE BOLLINGER SQUEEZE GATE — candidate, NOT adopted

Gate the champion's entries to bars where Bollinger bandwidth (2·2σ₂₀/MA₂₀)
sits in the bottom 40%. At matched 25% drawdown: **net/DD 46.53 against the
baseline's 27.26**, PF 1.589 → 1.863, and the complement collapses to 4.49.

Passed: halves (both), threshold plateau (30–60th pct all strong, so the number
was not fitted), per-trade quality (payoff 2.10:1 → 2.55:1, not leverage), and
critically the **ATR-rank discriminant** — gating on plain ATR rank does NOT
reproduce it (10.22 vs 46.53, corr +0.54). The σ-over-price construction is
doing real work an ATR filter does not.

**Blocked on the second-instrument control, which could not be run.** The
champion has no edge on the US30 data in this repo at all: baseline PF 0.657 on
n=34. You cannot test whether a filter improves a system that has no edge. This
is the control that has killed the most candidates here, and its absence is the
whole open risk. Also note 2023 degrades (PF 1.294 → 1.034).

**NEXT ACTION: get a second instrument the champion works on** — more US30
history, or silver/EURUSD/NAS100 30m. That single test decides whether the
squeeze gate ships. Nothing else on the list matters more.

### Two retail practices measured and found destructive

- **Stop at the broken level** ("broken resistance becomes support, use it as
  your stop"): net/DD **2.71** vs 27.26. Reason, measured: the median distance
  from a breakout close back to the level it just broke is **0.38 ATR** against
  the champion's 4.24 ATR stop. The stop sits inside the noise; WR falls to 10%.
- **Breakeven move after TP1**: net/DD **7.06**. It works as advertised — WR
  23.7% → 28.6% — and costs 96% of the return. On a 21.7%-win-rate trend system,
  protecting the middle of the distribution destroys the 6:1 tail that pays for
  everything. Expect to be asked for this repeatedly; the number is the answer.

### Also refuted at matched drawdown

Volume spike on the break (10.87 — worse than its own no-spike control at
13.42), 4h trend agreement (11.30), 4h + squeeze combined (12.68 — the 4h gate
*damages* the squeeze finding), candle confirmation (6.35), hard 2R/3R targets
(25–27, indistinguishable to worse), take-profit at each pivot level (17.8–24.3).

### Code change

`backtest/exit_lab.py` gained `tp_grid` + `_grid_target()`: TP1/TP2 placed at
the first and second ABSOLUTE levels beyond the fill, rather than a multiple of
ATR/R/price. Every prior target in this repo was a multiple. Defaults to None,
so every existing ledger row reproduces unchanged.

## Update 4, same session — the MTI five-PDF set, and a sizing answer worth keeping

~145 pages, two files byte-identical duplicates, four falsifiable claims. Three
fail. The fourth is the most directly useful number produced this session.

**"Never risk more than 2-5% per trade" (FX Profit Hacks #4) applied to this
champion:** 2% → **66.6% drawdown**; 5% → **94.45%**. The champion's own solved
risk at a 25% drawdown budget is **0.72%**. MTI's floor is 2.8x that.

Also: PF peaks at 2% (1.651) then falls to 1.390 at 5%, and the terminal equity
multiple peaks at 4% (x303) and falls at 5% (x268). **Past the peak, extra
leverage costs return as well as drawdown.** Useful when the user next asks
about leverage or a 200% account.

**Standing rule added:** percentage-risk advice is meaningless without the win
rate and payoff it was calibrated on. Convert any "risk X%" rule to its implied
drawdown before considering it. This desk sizes from a drawdown budget, which is
the same statement in the units that decide survival.

Refuted: StochRSI mean reversion (best |t| 1.38 of 16 tests), session-boundary
reversals (NY open sets extremes 0.086 vs 0.049 but flips LESS, 0.509 vs 0.516 —
expansion again), month-end "wildcard" candles (0.9903 vs 0.9836 ATR).

Noted for the record: MTI's Tip #14 "you will never go broke taking a profit" is
contradicted by this session's own numbers — the breakeven move scored net/DD
7.06 against 27.26.

**The blocking item is unchanged and unaffected by any of this: a second
instrument the champion works on, to settle the Bollinger squeeze gate.**

## Update 5 — GOLD ONLY from 2026-08-05, and G1* is adopted

**Standing scope change (user directive): US30 is removed. Gold only.** Do not
run second-instrument transfer tests unless the user reinstates them.

### What was adopted

**G1\*** — G1's regime multiplier, previously applied to the OPENING unit only,
now also scales every pyramid add, using the multiplier **captured at entry**.
One line of change. Entry, exit, trail, add triggers, spacing, cooldown all
untouched. Trade count 711, long share 65.68%, mean adds 1.809 — **identical**
to G1. Same trades, same paths, different add size.

At a 25% DD budget: PF 2.014 → **2.175**, MC median DD 25.26 → **22.43**,
**P(DD>30%) 21.12% ± 0.45 → 9.85% ± 0.31** (5 seeds × 5,000 paths,
non-overlapping ranges), pre-2025 PF 1.483 → **1.520**, TRAIN/VALID/TEST
1.497/1.298/2.337 → **1.576/1.309/2.588**. MAR 2.456 → 2.431 (−1%).

Risk presets re-solved: **0.606% at 25% DD, 0.475% at 20%.**
`strategies/gold_trend_G1.pine` updated, lint CLEAN, state machine desk-checked.

### What was rejected

**Volatility targeting, all three variants.** Isolated VT is NEGATIVE on gold
(MAR 2.218 vs E's 2.263) across six estimators. The soft open-volatility ceiling
amputated the right tail exactly as hard finding #2 predicts — top 1% of trades
kept 14% of their contribution, win rate jumped 21.7% → 30.0%.

### The methodological lesson worth keeping

The VT gain was an ILLUSION created by a new engine flag. `risk_series` had
never applied to pyramid adds; turning that on to make VT coherent also changed
G1, and the entire "VT × G1" improvement was the adds change, not VT.

**It was caught by an identity control**: `VT ATR14` must reproduce Config E
exactly (a 4.24×ATR14 stop makes ATR14-targeting a constant multiplier). It did.
`VT ATR14 × G1` must therefore reproduce G1 exactly. **It did not** — and that
gap was the whole finding. **Build an arm whose answer you already know into
every sweep.** It cost one row and it separated a real effect from a plumbing
change.

### Caveats on record for G1*

1. It **failed US30** before withdrawal (P(DD>30%) 36% → 53%). The supported
   claim is "better on gold", not "better".
2. Walk-forward fold 1 of 6 degrades (1.010 → 0.879, n=77); folds 2–6 improve.
3. 2021 degrades marginally (0.924 → 0.913); 2022 and 2026 improve.
4. G1's thresholds sit on a **rising slope**, not a peak (expThr 1.00→1.20 gives
   MAR 2.475→2.759). The adopted 1.10 is the conservative point, BELOW the
   slope. Do not chase it — that is re-optimisation, hard finding #10.

### Open item

The **Bollinger squeeze gate** (net/DD 46.53 vs 27.26) was logged as blocked
pending a second instrument. Under gold-only rules that blocker is void, but so
is the resolution: it must now clear the same gold-only bar G1* just cleared —
down years, anchored walk-forward, MC seed stability, right-tail diagnosis.
It has NOT been run against that bar. Do that before it is considered again.

---

# ►► CURRENT STATE AND NEXT ACTION (2026-08-06, supersedes the 08-05 block)

## What happened this session

User asked for a hybrid across AU200 / Gold / US30, "free hand without any
restriction", then clarified mid-turn: **"create what i asked you not to worry
about my portfolio"** (a portfolio-allocation study had been started and was
dropped), and then **"you can create one for each"** — separate per-instrument
systems are acceptable, a single unified strategy was not required.

**The hybrid was built, tested and REJECTED.** See RESULTS_LEDGER 2026-08-06.
The idea: measure each instrument's own rolling lag-1 autocorrelation and let it
select trend vs fade, same threshold everywhere. Every 4H arm came in below
PF 1.0; the daily arms had n=10–20. The regime switch also failed its own
pre-stated diagnostic (it put AU200 in TREND 31% of the time and lost 1,468 pts
there). Rolling autocorrelation on 500 bars is too noisy to route an engine.
**Family closed — do not re-open without a materially different regime proxy.**

**BUG-033 found and registered.** The hybrid's v1 produced n=4585, WR 0.2%.
That was stop-out re-entry churn: the signal-state pass did not know the executor
had already stopped out, so it re-entered the identical trade every bar. New
standing harness assertion: **WR below 10% or above 90%, or trades exceeding
~25% of bars, is a bug until proven otherwise — check it before reading the PF.**
Note this bug class makes results WORSE, so null/mirror/slippage controls all
pass while it silently buries real edges. Rebuilt clean in
`research/adaptive_sim.py`.

## The three shipped systems — one per instrument

| Instrument | File | TF | n | PF @2x slip | yrs+ | IS/OOS |
|-----------|------|----|---|------|------|--------|
| GOLD | `strategies/gold_trend_G1.pine` (G1\*) | 15m | 711 | PF 2.157 @25% DD, MAR 2.511 | — | — |
| US30 | `strategies/us30_rsi2_daily.pine` | 1D | 77 | 2.255 | 7/7 | 1.81→3.52 |
| AU200 | `strategies/au200_zrev_daily.pine` | 1D | 71 | 2.306 | 7/7 | 2.39→2.16 |

All three lint CLEAN. **US30 and AU200 now embed the Key Levels module** per the
standing directive; they previously did not (that was a live CLAUDE.md
violation — check any older strategy file for the same gap).

New this session: `au200_zrev_daily.pine`. **`au200_zrev_4h.pine` is SUPERSEDED**
and marked so in its header — on the rebuilt harness that 4H cell scores PF 1.25
with top-10 concentration of 199%, meaning it loses money net of its ten best
trades. AU200's reversion edge lives on the DAILY, not 4H.

Cross-instrument transfer FAILED: RSI(2) daily applied to AU200 gives IS/OOS
1.82→0.49, and on gold gives +303 pts over 7 years. This is precisely why three
separate systems shipped rather than one.

## Standing caveats to repeat to the user, unprompted

n = 71 and 77 trades over 6–7 years is about one trade a month each; top-10
concentration is ~70% on both; six to seven years is one broad regime and the
variance ratios motivating the whole reversion family are measured on that same
window. These are daily systems and will feel inactive to trade.

## NEXT ACTION

1. User forward-tests / paper-trades the two daily systems. They are low
   frequency, so expect months before the sample means anything — say so rather
   than reading early results.
2. Still open from 08-05: the **Bollinger squeeze gate remains a CANDIDATE** and
   needs the gold-only bar (down years, anchored walk-forward, MC seed
   stability, right-tail).
3. Do NOT re-open the adaptive/regime-switching hybrid family without a
   genuinely different regime proxy — noisy rolling autocorrelation is settled.
4. Audit the remaining `strategies/*.pine` for the missing Key Levels module;
   `gold_confluence_engine.pine` also fails lint with 38 undeclared identifiers
   (pre-existing, untouched this session).

---

# ►► CURRENT STATE AND NEXT ACTION (2026-08-13)
# Supersedes the 2026-07-31 handoff above. Read this first.

## What happened this session, in one line

The user's own AU200-BASE strategy showed PF 2.0–3.4 on TradingView across four
timeframes. It was a units bug in one line. Cleaned up, the identical entries
score PF 0.544 — **and the user's own platform reproduced that number**, which
is the first time this project has had an independent replication of a negative
result.

## The AU200-BASE investigation (the model for how to do this)

The user supplied **exported trade lists** (CSV, one row per fill) from
Capital.com and OANDA at 15m/30m/45m/1H/2H. Those lists, not the dashboard,
settled everything. Sequence:

1. **Entries verified legitimate.** Every 10:00 entry filled at the signal bar's
   CLOSE — matched raw 1-minute OANDA data 100% within 1 point, median gap 0.00.
   That is `process_orders_on_close`, not lookahead. **I was initially wrong to
   suspect the entries.**
2. **Exits were the problem.** 99.0% of winners filled within 1 point of that
   bar's own high (longs) / low (shorts); 100% of losers booked exactly -22.0.
   Booked exits averaged **+10.0 points better than the real price at exit time**.
3. **The decisive test:** take the strategy's own direction calls, honour them at
   real prices. **47.7% hit rate, -2.36 pts/trade.** The entries were a coin
   flip; 100% of reported profit lived in the exit fill.
4. **Cause found in the source:** `trail_points`/`trail_offset` are in TICKS and
   their roles were swapped. On AU200 (mintick 0.1) the inputs 30/5 meant
   *arm at 3 points, trail 0.5 points behind the high*. See BUG-036.
5. **Replication:** user ran the clean one-bar-hold version on 30m over
   Jan 2024–Aug 2026. TradingView returned **PF 0.544, 37.20% win**. My
   simulation said **PF 0.537, 37.8%**. Two implementations, different feeds,
   different windows, agreeing to 0.007 of a profit factor.

## New standing rules (earned today)

**1. A trade list outranks a dashboard.** The exported CSV is primary evidence
(entry price, exit price, P&L per trade). The summary panel is a derived
statistic. When they disagree, the CSV wins. Ask for the trade list export
before arguing about a PF.

**2. Close-to-close is the only execution-unambiguous construction.** A strategy
that enters at one bar's close and exits at another bar's close has no intrabar
path to guess, so the platform and an independent simulator MUST agree. Any
disagreement is a bug in one of them. Use this construction to settle disputes.

**3. Any exit finer than the bar is unmeasured, not edged.** A trailing distance
below ~1x the chart's average bar range cannot be resolved without a bar
magnifier. TradingView fills the gap by walking the bar monotonically to its
extreme. Treat such results as unmeasured. (BUG-036.)

**4. Extend the absurdity assertion.** Already: WR <10% or >90% is a bug.
Now also: **drawdown under 1% of equity, or a visually straight multi-year
equity curve, is a bug until proven otherwise.** AU200-BASE had all three.

**5. Never use a fixed UTC offset for session logic.** `hour(time,"UTC+10")` is
11 AM Melbourne from October to April. Always the named zone
`"Australia/Sydney"`. (BUG-037.) This also means any "10:00 only" filter on a
fixed-offset script is silently a *winter-half-of-the-year* filter.

**6. Verify uploaded documents before acting on them.** Four external research
documents were filed this session. Every one mixed real, checkable infrastructure
with fabricated specifics — invented SEC cases with invented fines, invented
Form 4 filings from misnamed executives, precise accuracy percentages with no
source. Check names, dates, case numbers and URLs before treating any of it as
input. See `documents/` — each carries an Editor's Verification Note.

## Results added to RESULTS_LEDGER this session

- **AU200 10:00 candle + one-bar fixed hold** (user-frozen spec): NOT VALID.
  Gross PF 30m 0.784 / 45m 0.780 / **1H 1.123** / 2H 0.983. Net of 2 pts cost all
  below 1.0. On 3 of 4 timeframes, ignoring the filter and going long beats it.
  1H is the only cell gross-positive in both windows and is the one worth
  revisiting. Entry reconstruction validated: **100% direction agreement with
  the user's trade list on all 182 shared days.**
- **350-cell achievable-fill search** around the 10:00 candle and daily open
  (gap fade/continue, opening range, daily-open relation, exit sweeps):
  **NOTHING FOUND.** Zero cells clear t >= sqrt(2 ln 350) = 3.42. Only 7 of 350
  are even PF > 1.0 against ~175 expected by chance — the 2-point cost dominates
  the whole family at ~1 trade/day. Best cell +1.17 pts/day vs the 10 requested.

## The 10-points-a-day answer, settled

Not reachable from an intraday setup. Nothing in 350 rules, nor any strategy
tested this session, produces it. The honest route is **size on the validated
daily z-reversion**: ~696 pts/year at 1 unit with 482-point max drawdown, so
10 pts/day (~2,500/yr) needs ~3.6x size and ~1,730 points of drawdown. That is
about six months of average profit erased in one drawdown. The user has been
told this plainly.

## What IS true about the 10:00 candle (keep this)

Measured on 397 sessions of 1-minute OANDA data:
- 10:00 close -> 11:00 close: **53.1% up / 45.4% down** — no directional edge
- Median absolute move in that hour: **13.0 points**
- Sessions moving **>= 10 points** in that hour: **64.6%**

The move the user sees is real. The side is a coin flip. The open remains the
right place to look; EMA200 + RSI50 + SuperTrend is not the right filter.

## documents/ — non-trading corpus (NEW this session)

`documents/` holds material that is NOT part of the trading system and is
deliberately outside the CLAUDE.md always-on reading order. Six documents, each
with a verification note where warranted. Builders are reusable:

- `research/build_report_pdf.py` — markdown -> typeset PDF (serif body, sans
  headings, tables, colour-coded assessment marks). One command, any markdown.
- `research/build_corpus_pdf_exact.py` — every source file -> one verified PDF.
- `research/build_transcripts_pdf.py` — transcripts/playbooks companion volume.
- `research/build_quarters_theory_pdf.py` — topic-scoped collection.

All corpus builders typeset in full-Unicode monospace, hard-wrap at the column
width, and **assert at render time that unwrapping reproduces the source
character-for-character**. Verified: 70/70 text files and 507 original PDF pages
present exactly; 403/403 Quarters-Theory references captured.

## NEXT ACTION

1. **1H is the only live thread from the open.** It came back gross-positive in
   both windows and beats always-long. It is ~2 points/trade short of tradeable.
   The gap must come from a better entry filter — the exit is now as clean as an
   exit can be. Do not spend another round on exits.
2. **User is downloading Dukascopy AUS.IDX/AUD data** — UTC, 10-second or tick,
   BID and ASK as separate files. Two jobs: (a) measure the REAL spread at 10:00,
   which decides several borderline results including the 350-cell sweep, and
   (b) test the literal claim that the 9:59 candle's state at the 50-second mark
   predicts the 10:00 candle. Job (a) needs ~3 days; job (b) needs a month+.
3. **The 2-point cost assumption is the single most load-bearing unverified
   number in this project.** It killed the 350-cell search on its own. Replace
   it with a measurement the moment the bid/ask files arrive.
4. Do NOT re-open: the adaptive/regime-switching hybrid; the AU200 4H reversion
   cell; exit-tuning on the 10:00 candle.

---

## ►► CORRECTION, same day (2026-08-13, later)

**I under-used the supplied data.** Every AU200 figure in the handoff above was
computed on `au200_aud_1m_4.csv` — 444 sessions, 19 months. The uploads also
contain **`au200_aud_5m.csv`: 1,635 sessions, 2020-08-05 to 2026-08-04, six
years.** Also present and NOT used (user instruction 2026-08-13: "work only on
au200"): `xau_usd_15m.csv` (6.7 yrs), `us30_usd_15m.csv` (6.7 yrs),
`au200_aud_15m.csv` (6.0 yrs).

**What the full sample changes:** the 10:00 candle + one-bar 1H hold, which the
handoff calls "the one live thread", goes from PF 1.105 gross on 444 sessions to
**PF 0.944 gross on 1,635 sessions**, and net of cost is negative in **0 of 7
years** with t = -3.62. See H83 REVISED.

**Therefore the NEXT ACTION list above is wrong on point 1.** The 1H cell is not
a live thread; it is significantly negative on six years. Do not spend another
round on an entry filter for it.

**Everything else in the handoff still stands** — BUG-035/036/037/038, the
AU200-BASE replication, the evidence hierarchy — because those were about
execution mechanics, not sample size.

**Standing rule:** state the date range and session count of the file used with
every result, and check the data directory for a longer file on the same
instrument before running anything.


## 2026-08-16 — RETRACTION: the 10 AM Body Break result is void (BUG-039)

I delivered `strategies/au200_10am_body_break.pine` claiming PF 5.032 / 63.3%
win / n=327. Kush ran it on TradingView (OANDA AU200AUD, 5m, last 365 days, deep
backtest) and got **PF 0.444 / 26.79% win / n=280 / -353.95 AUD**. The live run
is right and my simulation was wrong.

Cause: "the daily open" was three different price levels. My Python proxy took
the first bar with hour < 10, which on the 544 sessions that carry overnight bars
is the **00:00 Melbourne** open — a median 15.5 points from the 10:00 open — and
on the other 1091 cash-only sessions is the 10:00 bar's own open, which forces
`side = 0` and produces no trades. The Pine's `request.security(...,"D",open)` on
OANDA rolls near **07:00 Melbourne**, a median **0.0 points** from the 10:00 open,
so the live stop sat on the entry. Full write-up in bugs/BUG_REGISTRY.md
(BUG-039) and RESULTS_LEDGER.md.

Re-tested with the anchor made an explicit input: 00:00 gives PF 2.672 (not
5.032 — my own harness was not reproducible), 07:00 gives PF 1.346 with t=+1.27
against a multiple-testing bar of 3.9. **Nothing found.**

Standing rule added: a level referenced by name is not a level. Before any
sweep, measure the simulator's series against the Pine's and report the median
absolute difference, plus how many sessions the proxy is even defined on.

Deliverable from this: `strategies/au200_10am_body_break_diag.pine` — same rules,
but the reference level is a dropdown (security daily / 10:00 / 07:00 / 00:00),
a minimum-risk guard is added, and an on-chart table prints the security daily
open, the 10:00 open and the gap between them so the divergence is visible.

### SUPERSEDED HANDOFF (2026-08-16)
- The 10 AM Body Break is CLOSED as a source of edge on AU200 unless the 00:00
  anchor can be justified as a real overnight-gap filter and tested on data that
  covers overnight bars for all sessions (the current file covers 544 of 1635).
- Still outstanding: the AU200 spread at 10:00 is unmeasured. Every cost
  assumption in this repo (2 pts) is an assumption. Dukascopy bid/ask download
  gates re-running the 350-cell opening-range sweep.
- Ask Kush for the trade-list CSV export from the live run if we ever revisit
  this, to confirm the entry prices match the 07:00-anchor reconstruction.


## 2026-08-16 (later) — v2 rebuild complete. The 10:00 candle is dead, measured.

Kush's instruction was "go from scratch and do the real work and get me the same
PF as promised any how". I told him I would not manufacture the number and would
report whatever the data held. It held nothing.

Built `research/v2/` from zero. Nine numbered engine rules, four mandatory
self-tests (zero-cost null, injected-edge recovery, cost monotonicity, random
walk). BUG-040 caught by the harness on the first run — a fade signal with the
stop at the reference level put the stop on the PROFITABLE side, producing PF 99
and a 100% win rate. Now blocked by R8; R9 makes metrics() refuse absurd results
outright, so the absurdity assertion is enforced in code rather than by my memory.

Three sweeps, 10,530 cells, zero clearing their multiple-testing bars. The
closing evidence on the 10:00 candle specifically:
  * gross expectancy at ZERO cost: -0.26 to +0.50 pts, all |t| < 1.5, sign flips
    between horizons. Not a cost problem. No signal.
  * directional accuracy vs the next 1/2/3/6/12/24/71 bars: 46.05% .. 50.46%,
    never significantly above chance. The one significant reading is BELOW 50%.
  * shuffle null vs the search MAXIMUM: best real cell t=+0.70; 7 of 12
    coin-flip searches beat it.

STANDING CONCLUSION: the direction of the AU200 10:00 candle carries no
information at any horizon from 5 minutes to the close. Every stop/target/trail/
filter variation is a transformation of a zero-expectancy signal. Do not accept
another 10:00-candle proposal without new evidence that contradicts these three
measurements specifically.

Only survivor worth an hour: gap continuation (|gap| > 0.25 ADR), stop 30,
trail 0.3 x ADR, BE at half-risk. n=773, PF 1.154 full sample, OOS PF 1.244,
6/7 years. BUT t=1.46 against a bar of 4.19; the exit dimension is a SPIKE
(every alternative ~1.00, only trail_adr0.3 reaches 1.154); and it dies on cost
(PF 1.013 at 3.0 pts, 0.893 at 4.0). MC P(profit) 92.8% at 2pt, 54.8% at 3pt.

### CURRENT STATE AND NEXT ACTION
1. MEASURE THE SPREAD. Dukascopy bid/ask for AU200 around 10:00 Melbourne. It is
   the highest-value hour available: the only surviving result flips from viable
   to worthless between 2.0 and 3.0 points, so the measurement either revives it
   or kills it, and nothing else moves as much.
2. Ask Kush how often his TradingView feed carries the 09:50 pre-open bar. My
   exports have it on 11% of sessions; his live chart plainly has more. Sweep B's
   173-session sample is a floor.
3. TradingView MCP is UNREACHABLE from this cloud container — it addresses
   localhost and we are not on his machine. Do not promise live chart reads here.
4. Report published: reports/au200_10am_rebuild.html
   https://claude.ai/code/artifact/39222dfc-6238-49e6-b959-bb1505e6f5d6


## 2026-08-16 (later still) — the written strategy tested. Cost, not concept.

Kush supplied two handwritten pages and then a full 20-section written
strategy ("Do not trade the level. Trade the reaction to the level"). Ported to
Pine (strategies/reaction_to_the_level.pine) and to Python
(research/v2/reaction.py), then swept: 756 cells, 669 with enough trades,
**0 clearing the t>=3.61 bar and 0 with PF > 1.0.**

THREE FINDINGS WORTH CARRYING FORWARD:

1. **His section 14/20 checklist filters the WRONG WAY.** Requiring more
   confirmations is monotonically worse on two of three triggers (retest:
   PF 0.702 at conf>=0 down to 0.589 at conf>=6). This is the second
   independent confirmation in this repo that "require more confluence" hurts
   — the first was the four-trader hybrid's Absolute Law #2. Treat any future
   "more confirmations = better quality" claim as contradicted until shown
   otherwise on that specific setup.

2. **His section 6 retest rule is RIGHT.** Retest (PF 0.705) beats
   close-beyond (0.679) beats next-candle (0.642). Small but consistent. Give
   him credit for it — it is the rule he was most insistent about and it is
   the best of the three.

3. **The diagnosis differs from the 10:00 candle.** There, gross expectancy
   was ZERO (H89) — nothing to buy at any price. Here gross is **+0.26 points
   per trade** against a 2.0-point cost. The concept is not empty; it is
   roughly 8x too small to pay the toll at ~1 trade/session. Direction-flip
   control confirms the rules are not backwards (inverted is worse still).

### CURRENT STATE AND NEXT ACTION
- THE SPREAD MEASUREMENT NOW GATES THREE SEPARATE RESULTS (gap continuation,
  AMD FVG, and this). It is unambiguously the highest-value next task. Needs
  Dukascopy bid/ask for AU200 at BOTH the 10:00 cash open and overnight
  21:00-03:00, since AMD trades the night book.
- Second lever for this strategy specifically: frequency is wrong, not logic.
  A +0.26 pt/trade edge needs either a much cheaper fill or setups with much
  larger expected moves. More filters will not fix it and demonstrably make it
  worse.
- DATA: the uploads directory was cleared mid-session. All price data now comes
  from data/*.csv.gz committed in the repo. engine.py points there. Do not
  reference /root/.claude/uploads paths again.
- Gold is only available at 15m in the repo (data/xauusd_15m.csv.gz); there is
  no gold 5m, so the "or gold 5 mins" option could not be honoured.


### CURRENT STATE AND NEXT ACTION (2026-08-20)

**Two threads are live. Read both before doing anything.**

**1. MANUAL VISUAL TEST — PAUSED AT CHART 089, NOT ABANDONED.**
The user is personally classifying all 120 blind AU200 charts. 88 responses are
recorded in `research/au200/blind/MANUAL_RESPONSES.md` (001-088). Chart 089 was
sent and is unanswered. The answer key is frozen and UNOPENED.
Procedure when it resumes: send `research/au200/blind/charts_v2/NNN.png`, record
`| NNN | XX |`, commit, send the next. **Zero feedback. No partial scoring. No
comment on any pattern in the answers.** After 120, freeze the file and wait for
the literal command "LOCK AND SCORE MANUAL TEST" before opening the key.
Post-lock the user also wants: comparison against ChatGPT's independent
classifications, a re-check against the candlestick books, and investigation of
disagreements.

**2. GOLD 10AM STUDY — COMPLETE. Verdict NO EVIDENCE OF GOLD EDGE.**
`research/gold_10am/`, 34 phases, report in `report/`, ledger G01-G26. See
RESULTS_LEDGER.md for the numbers and H91/H92/H93 for the beliefs.

**Standing facts learned this session:**
- **dukascopy.com is reachable and gives BID AND ASK separately.** That is how
  the gold spread finally got measured ($0.630 median). The identical route will
  measure the AU200 spread, which still gates three results (H90, gap
  continuation, AMD FVG). This is now a small job. DO IT.
- **api.londonstrategicedge.com is reachable now (401, not the old 403 tunnel
  refusal). What is missing is LSE_API_KEY** — this container never had it.
  `research/gold_10am/code/fetch.py --source lse` re-runs the whole gold study
  against the vault the moment a key is exported. Do NOT reuse the key pasted on
  2026-08-17: public repo, was to be rotated.
- **Gold's ATR moved 5.7x inside two years** (median pre-entry 5m ATR $0.82 in
  2024, $4.68 in 2026). Any fixed-dollar exit compared across this window is
  comparing two different instruments. Normalise.
- **The gold maintenance break is at NY 17:00-18:00 and its Melbourne clock time
  is set by TWO DST calendars.** 07:00-08:00 (AEST+EDT), 08:00-09:00 (AEDT+EDT),
  09:00-10:00 (AEDT+EST). The third case kills 09:50 completely, Nov-Mar.

---

## 2026-08-21 — GOLD TICK DATASET: one verified year of Dukascopy XAUUSD ticks

**Data acquisition only. No strategy research was run — the user was explicit
about that twice.**

### What now exists
`research/gold_tick_data/dukascopy/` — a 91,629,949-tick XAUUSD dataset covering
2025-08-21 00:00:00.000 → 2026-08-20 23:59:59.999 **Australia/Melbourne**.
- `processed/GOLD_XAUUSD_DUKASCOPY_TICKS_2025-08-21_to_2026-08-20.parquet`
  957 MiB, ZSTD-9, 8 columns, ms precision.
  SHA256 `f5be07253e91d1112005294e5c0714b4b295c432b07044e0982ac4328635b96c`
- `code/` — fetch_ticks / build / audit / verify / manifest / make_readme.
  The whole thing rebuilds from Dukascopy in ~15 minutes.
- **The Parquet and the 373 MB raw .bi5 mirror are NOT in git** (user directive:
  "keep it as a generated data artifact"). They live on EPHEMERAL container disk
  and are gone when the container recycles. `logs/manifest_by_hour.csv` holds a
  SHA256 per raw hourly file so the mirror is re-verifiable without re-fetching.
- Delivered to the user as 39 x 25 MiB lossless byte-split parts (the chat
  channel caps uploads at 30 MiB), with REASSEMBLE.txt and per-part checksums.
  Concatenation was verified to reproduce the master SHA256 exactly.

### STANDING FACT: the raw Dukascopy tick route works from this container
`https://datafeed.dukascopy.com/datafeed/{SYM}/{YYYY}/{MM0}/{DD}/{HH}h_ticks.bi5`
- **MM0 is ZERO-INDEXED** (January=00, August=07). This is the single most
  common way to fetch the wrong month.
- LZMA1 "alone" format. Decompresses to 20-byte big-endian records `>IIIff`:
  ms-offset-into-hour, **ASK, then BID**, ask volume, bid volume.
  **Ask precedes bid.** Reversing them yields a permanently negative spread.
- XAUUSD divisor is **1000** (3345255 → $3345.255). Verified empirically.
- Dukascopy answers **HTTP 200 with zero bytes** for an hour it has no ticks
  for. That is a real answer, not a failure. Treating empty as missing would
  have condemned 2,849 of 8,760 hours.
- Throughput is bursty token-bucket: 12 hours/sec in bursts, with stalls. 24
  workers is the sweet spot; a 25th connection gets reset. Whole year ≈ 15 min.

### Measured facts about gold worth keeping
- **Median spread $0.670** (mean $0.740, p99 $2.20, max $15.00) across 91.6M
  ticks. This independently corroborates the $0.630 median measured in the
  gold_10am study off the same feed — two separate measurements, same answer.
  H90 and the three results the spread gates can now use a real number.
- Gold ran **$3,321 → $5,597** over the year. Any fixed-dollar exit compared
  across this window is comparing two different instruments (compounds the ATR
  point already in the register).
- 91.6M ticks / 312 trading days = mean 293,686 ticks/day, median 281,549.
  Min 24,535 (2026-07-04, Independence Day). Max 817,963 (2026-01-30).
- 2025: 30,760,509 ticks / 114 days. 2026: 60,869,440 ticks / 198 days.

### Data quality — all zero
Exact duplicate rows, duplicate timestamps, out-of-order timestamps, missing
bid/ask, invalid price rows, bid>ask, zero spread, negative spread: **0 each**.
Unresolved download hours: **0** (all 8,760 requested and answered; one hour
needed a --retry-errors sweep after six 503s). Unexpected empty hours: **0**.
Six unexplained gaps totalling **51 minutes across the whole year**, all in
known thin-liquidity windows. This is a clean feed.

### The methodological point worth carrying
The gap classifier initially called the 73-hour **Good Friday** shutdown
"unexplained" because it matched only the gap's ENDPOINTS (Thursday and Sunday)
against a holiday list, and Good Friday is neither endpoint. It passed eight
unit tests first — every one of which happened to be a case where endpoint
matching worked. Fixed by measuring instead: walk the interval minute by minute
against a real session calendar in **New York** time and count genuinely-open
minutes. See BUG-044. Two more bugs registered: BUG-042 (a global back-off costs
worker-count x its duration, and silently destroyed throughput while every
request still succeeded) and BUG-043 (NumPy 2.x rejects np.int64 in
np.datetime64()).

### CURRENT STATE AND NEXT ACTION (2026-08-21)
- **The dataset is finished, verified and delivered. Strategy research on it has
  NOT started and must not start until the user asks.**
- The three live threads from 2026-08-20 are untouched and still open: the manual
  visual test PAUSED AT CHART 089, and the gold 10am study's NO-EDGE verdict.
- The AU200 spread measurement still gates H90 / gap continuation / AMD FVG. The
  identical BI5 route now proven here will measure it — `E_XJO-ASX`, same
  decoder, same fetcher with a different symbol. That remains a small job.

---

### CURRENT STATE AND NEXT ACTION (2026-08-21, late — supersedes the block above)

The dataset block above is still accurate. What changed: **strategy research on
the dataset did start**, at the user's explicit request, and has run through six
phases. All of it is committed and pushed to `claude/gold-tick-data-dukascopy-r3xu10`
(PR #7, open draft, head `350a9da`, no CI in this repo).

**What was asked and delivered, in order:** the 10AM logics tested tick-exactly;
MFE/MAE excursions and practical TP/SL; a TP1 partial with a trailed runner;
exit engineering against a LOCKED entry universe (the user split the research
with a second researcher who owns entry work — I own exits and verification);
a Quarterly Theory cross-check; and a price-level study covering quarters,
round numbers, key levels and pivots.

**The standing verdict on the strategy.** One thing survives its control:
displacement from the 10:00 open beats random entry (z = 5.81). Everything else
tested does not. The 10:00 candle BODY is inert (permutation p = 0.571). The
exit surface is a broad flat plateau (SL 12–18 x TP 22–32) and re-optimising it
in walk-forward is WORSE than freezing it (PF 1.03 vs 1.77). Five separate
candidate entry upgrades — per-direction exits, time stops, break-even, $25
quarter proximity, level confluence — each failed its own control.

**The method that keeps paying, and the way it fails.** Every claim gets a
control that preserves the geometry and severs only the claimed cause:
permutation of the candle body, shuffled pairing for ratio ladders, phase shift
for level grids, sham levels for pivots, random subsets for filters. Three
"findings" died to these this session, including one of my own (BUG-046: a sham
drawn ONCE is a random variable; a low draw reads as a good result). Two closed
forms explain results that looked like market structure: the acceptance ladder
is gambler's ruin x/S (H99), and the Q1->Q2 compression ladder is ratio
selection (H97).

**Captured:** H94–H100, GF01–GF07, GL01–GL06, BUG-042 through BUG-046.

**NEXT ACTION — do not start unprompted:**
1. **Unreconciled:** the collaborator reports PF 2.115 on a 59-trade set; the
   same 59 trades measure 1.813 here, net +349 vs +435, max DD 70.9 vs 45.
   Selection matches EXACTLY, so the gap is fills or exit handling. Flagged to
   the user; needs their fill details. Do not chase it unilaterally.
2. **Deferred by the user, not cancelled:** XAGUSD silver, resumable from hour
   239/8760 via checkpoint (~15 min). XPTUSD and COPPER both 404 on this feed,
   so there is no metals triad.
3. Recorded but NOT acted on, per the entry-rule freeze: A_LONG is 91 of 131
   signals, but FLIP_SHORT carries a higher win rate at small targets.
4. Still open from 2026-08-20: the manual visual test PAUSED AT CHART 089, and
   the AU200 spread measurement gating H90 (`E_XJO-ASX`, same BI5 route).

**The real next test is data neither researcher has seen.** Everything above is
one year, and it has now been looked at many times.
