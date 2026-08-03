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
