# Session Handoff Prompt — "find the best strategy from everything I already have"

Copy everything between the two rulers into a fresh session (this repo, or a
different agent). It is written to be self-contained: it states what exists,
what is proven, what is dead, and what the rules of engagement are, so the
next agent does not re-derive or re-break any of it.

---

## PROMPT — COPY FROM HERE

I am Kush Verma. I trade XAUUSD (gold), primarily intraday on 15m/30m. This
repository — `kushverma7/Trade_Cartel`, branch `claude/confident-fermi-qku0ic`
— is my permanent trading knowledge base and Pine Script engine repo. It holds
months of my sessions: trader knowledge I supplied, indicators I supplied,
strategies you built, and every backtest result with its sample size.

**Your task: go through everything in this repo, audit what I already have,
and tell me which strategy is genuinely the best one — and whether anything
in the archive beats the current champion.** Do not build something new until
you have finished the audit and shown me the comparison table.

### Step 1 — read these first, in this order

1. `CLAUDE.md` — the standing instructions. They override your defaults.
2. `trader_playbooks/COGNITIVE_ARCHITECTURE.md` — the three-mind operating
   system (Macro Architect / Microstructure Predator / Profit Engine with
   veto) and the 8-step process every analysis follows.
3. `MEMORY.md` — persistent context. Its last section, "CURRENT STATE AND
   NEXT ACTION", is the handoff and replaces having the previous conversation.
4. `RESULTS_LEDGER.md` — **every backtest result ever produced here, with its
   trade count, date window and settings.** This is the single source of
   truth for "what have we already tried". Read it before proposing anything.
5. `trader_playbooks/USER_TRADING_PROFILE.md` — who I am as a trader.
6. `trader_playbooks/BELIEF_REGISTER.md` — active beliefs with evidence and
   invalidation conditions.
7. `trader_playbooks/PLAYBOOK.md` — live setups, what is retired, current regime.
8. `trader_playbooks/bugs/BUG_REGISTRY.md` — every code bug ever found here,
   with root cause and prevention. Check new code against it. Never repeat one.
9. `trader_playbooks/skills/SKILL_REGISTRY.md` and
   `trader_playbooks/tests/TEST_REGISTRY.md` — validated reusable Pine
   patterns and known-scenario tests.
10. `trader_playbooks/CODE_DELIVERY_PROTOCOL.md` — the mandatory 7-phase
    pre-flight before any Pine code ships.
11. `trader_playbooks/OMNIBUS_PROTOCOL.md` — the iteration loop. Read its
    adoption note: the original's voice map has known errors; the repo's
    register wins where they differ.

### Step 2 — know the current champion before you judge anything against it

**`strategies/gold_trend_strategy.pine`** is the current best. It is a clean
standalone trend strategy — no key-levels module — with pyramiding, a
chandelier trail, and asymmetric TP1/TP2. Its research engine is
`backtest/trend.py` (entries, adds, risk) and `backtest/exit_lab.py` (the
full exit space: six trailing modes, TP1/TP2, breakeven).

Validated on **XAUUSD 30m, Balanced profile, 0.20 pt slippage, $0.07/contract
commission, Aug 2 2019 → Aug 2 2026**, confirmed live on TradingView Premium
deep backtest against an independently-written research engine:

| metric | research engine | TradingView live | agreement |
|---|---|---|---|
| profit factor | 1.641 | **1.583** | Δ 0.058 |
| net return | +1,620.2% | **+1,591.7%** | 98.2% |
| max drawdown | 33.40% | **33.63%** | 0.23 pp |
| entry orders | 2,234 | **2,370** | 94.3% |

Supporting evidence: Deflated Sharpe 0.9996 at 1,000 assumed trials; PBO
(CSCV) 0.099; six of seven years profitable (2021 = −1.5%); positive in all
five walk-forward slices. Buy-and-hold over the same window: +179% at 29.1% DD.

Risk ladder (same window): Conservative +680% / 17.0% DD; **Balanced +1,592%
/ 33.6% (default)**; Aggressive +8,627% / 42.8%; Maximum +24,712% / 54.5%
(the last two were measured at 0.05 pt slippage and have NOT been re-run at
0.20 pt — treat them as unconfirmed).

**Anything you nominate as "better" must beat this on the same window, the
same costs, and the same validation battery. Not on profit factor alone.**

### Step 3 — the standing findings (do not re-derive these)

- **The exit carries the edge, not the entry.** Seven different entry
  families were tested; the exit configuration moved results far more than
  any of them. Spend effort on exits.
- **Adding to winners (pyramiding) is the single largest return lever** —
  and it is a variance multiplier, not an edge. It raises return and
  drawdown together.
- **Asymmetric profit-taking wins**: bank partials on the counter-trend side
  where there is no large move to capture; let the trend side run on the
  trail. Symmetric TP1/TP2 is worse than either extreme.
- **PF trades off against trade frequency and against return.** A wider trail
  raises PF and *lowers* return, because risk-based sizing shrinks the
  position as the stop widens. Trail 20 = PF 1.659 but only +23.5%; trail 6
  = PF 1.243 but +85.4%. Never optimize PF alone.
- **Level-based and quarter-based targets fail structurally** — their
  distance is set by where the line happens to sit, not by what the trade
  needs, so every trade gets a random target/stop ratio. Median target was
  0.46 ATR against a 6 ATR stop; live PF 0.702. (BUG-017.)

### Step 4 — measured and rejected; do not re-try these without a new reason

| idea | measured outcome |
|---|---|
| key-level entry/exit, stop-and-reverse | live PF 0.702, −2.99% |
| quarter-theory (Daye TIME) profit taking | no improvement over ATR targets |
| price-grid targets | same structural failure as key levels |
| long-only | looked good on the train half only; false out of sample |
| giveback trail without an arming threshold | 1% win rate over 2,307 trades |
| DE Hybrid V5/V6/V7 exits (12 OR-ed) | underperformed a plain Donchian-160 trail |
| Body Pierce MA as an entry | no edge beyond the baseline trend entry |

### Step 5 — the validation battery every candidate must pass

Reporting a profit factor alone is not a result. A candidate is only "valid"
after all of:

1. **Corrected random-timing null with matched filters.** Randomize the entry
   *timing* while keeping every filter the strategy uses. (An earlier version
   compared entry+filters against nothing and was wrong for months. Under the
   corrected null the champion sits at the 93.3rd percentile — inside noise —
   which is honest and must be stated.)
2. **Deflated Sharpe Ratio** (Bailey & López de Prado) with the trial count
   you actually ran.
3. **PBO via CSCV** — probability of backtest overfitting.
4. **Year-by-year** breakdown, not just the aggregate.
5. **Walk-forward** slices, all reported, including the losers.
6. **Cost stress**: commission +50%, double spread, slippage at 0.20 / 0.50 /
   1.00 points. If the edge dies at 0.50, say so.
7. **Out-of-sample.** No row in the ledger is marked VALID without one.

Run `backtest/overfit.py` for DSR and PBO, `backtest/stress_test.py` for
costs, `backtest/pine_lint.py` before any Pine ships.

### Step 6 — hard rules I will hold you to

- **No result without its trade count and date range.** A PF with neither is
  not a result. Append a row to `RESULTS_LEDGER.md` in the same session the
  number is produced.
- **No "proven" or "guaranteed" language.** A strategy that once showed PF
  3.656 on 117 trades and $34.19 of net profit was retracted for exactly
  that reason. Say what the sample supports and nothing more.
- **Port, don't reimplement.** When I supply working source, the deliverable
  is a port of *that* code. Every deviation is logged as a numbered port
  delta with a reason. (BUG-013: three rewrites of the key-levels module
  were rejected.)
- **Key levels are mandatory in anything built here**: embed
  `trader_playbooks/skills/key_levels_module.pine` verbatim. Host must be
  Pine v6, `overlay=true`, `max_lines_count`/`max_labels_count` ≥ 500.
  (The current champion is the documented exception — it is deliberately
  standalone because level-based logic was measured and rejected. If you
  rebuild it with levels, they are display-only.)
- **Pine gotchas that have already cost me money** — check every one:
  `slippage` is in **TICKS not points** (XAUUSD mintick 0.001, so 200 ticks
  = 0.20 pt); `margin_long`/`margin_short` default 100% silently rejects
  orders (BUG-012); `pyramiding` default 0 silently ignores `strategy.entry`
  while in a position; `max_bars_back` default 300 silently yields `na`;
  `strategy.exit` `qty_percent` applies to the stop as well as the limit;
  TradingView counts each **entry order** as a closed trade, not each
  position; continuation lines must not be indented a multiple of 4.
- **Backtest-engine gotchas**: stop fills must be gap-aware — a bar opening
  through the stop fills at the open (BUG-018, worst loss went from 124 to
  241). Never update best-excursion before resolving the stop on the same
  bar — that is intrabar lookahead and it halved the reported drawdown.
- **Capture learnings before the session ends.** New bug → `BUG_REGISTRY.md`.
  New validated pattern → `SKILL_REGISTRY.md`. New evidence for or against a
  belief → `BELIEF_REGISTER.md`. New state → `MEMORY.md`. If it isn't
  captured, it wasn't learned.
- **Never let a live credential enter git history.** Secrets live in a
  gitignored, mode-600 `.env`, never on argv, never logged.
- **Republish the artifact AND re-send the file on every Pine change.** I
  once pasted a stale artifact and got a compile error on code that had
  already been fixed in the repo.

### Step 7 — what I want back

1. A ranked table of every strategy in `strategies/` that has a real measured
   result, with PF, net return, max drawdown, trade count, and date window —
   pulled from `RESULTS_LEDGER.md`, not re-run from memory.
2. Which ones have never been properly validated, and what is missing.
3. A clear verdict: does anything in the archive beat
   `gold_trend_strategy.pine` on the same window and costs? If yes, show the
   comparison. If no, say so plainly.
4. The two or three highest-expected-value improvements you can make to the
   champion, each with the specific measurement that would confirm or kill it.

Tools available: `backtest/*.py` (research engines), the `tradingview` MCP
server (live chart, deep backtest, Pine compile), Kronos at `/home/user/Kronos`
via `kronos/kronos_signal_filter.py` for the "is there exploitable structure
at this timeframe at all" question, `vibe-trading` CLI, and `mcp-search` for
recalling past sessions. Data: `data/xauusd_15m.csv.gz`.

## PROMPT — COPY TO HERE

---

Written 2026-08-02, at the point where `gold_trend_strategy.pine` was
confirmed live on TradingView Premium at PF 1.583 / +1,591.7% / 33.63% DD
over 2,370 orders and seven years.
