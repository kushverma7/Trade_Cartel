# Research Protocol Prompt — how to run a clean session in this repo

The third of the three prompts. `SESSION_HANDOFF_PROMPT.md` audits the
strategies. `ARCHIVE_SWEEP_PROMPT.md` audits the sources. This one is the
method — the procedure that makes a session's output trustworthy, written
from the specific ways this project has produced wrong answers before.

Give this to any session doing research here, in addition to whichever task
prompt applies.

---

## PROMPT — COPY FROM HERE

You are doing quantitative trading research in `kushverma7/Trade_Cartel`
(branch `claude/confident-fermi-qku0ic`), XAUUSD, mostly 15m/30m. I am Kush
Verma and I will act on what you tell me with real money, so a wrong number
delivered confidently costs me more than no number at all.

This project has produced wrong answers 23 recorded times. Every one was
caught late, by contradiction, not by review. **The rules below are not
general good practice — each one exists because a specific failure here got
past a session that believed it was being careful.** Follow them literally.

### 0. Read before you touch anything

`CLAUDE.md` (overrides your defaults) → `COGNITIVE_ARCHITECTURE.md` (the
three-mind process) → `MEMORY.md` (last section is the handoff) →
`RESULTS_LEDGER.md` (what has already been measured) →
`trader_playbooks/bugs/BUG_REGISTRY.md` (all 23, read in full) →
`CODE_DELIVERY_PROTOCOL.md` (the 7-phase pre-flight, mandatory before any
Pine ships).

Reading the bug registry is not optional context. It is the checklist you
will be held to in section 4.

### 1. The one rule that catches most of it

**A number that agrees with your expectation gets more scrutiny than one
that doesn't.**

Every serious error here was found by a contradiction someone chose to
investigate instead of explain away:

- a new engine couldn't reproduce an old engine's known result → intrabar
  lookahead (BUG-019)
- profit factor matched TradingView but the worst loss was half as bad →
  the fill model ignored gaps (BUG-018)
- live PF 0.702 against research PF 1.385 on identical settings → the
  research port modelled 18 levels where the Pine drew 36 (BUG-017)
- a trailing mode scored a 1% win rate over 2,307 trades → it never armed
  (BUG-020)
- the random-entry control arm returned +524% on its own → the null was
  measuring the wrong thing (BUG-023)

In every case the "explain it away" reading was available and plausible.
When two things that should agree don't, **stop and find out why before
doing anything else.** Do not tune, do not proceed, do not note it as a
curiosity.

### 2. Before you believe any number you produced

Run these five checks. They take minutes and they are the difference
between a result and a guess.

1. **Reproduce a known result first.** Before trusting a new or modified
   engine, make it reproduce a row already in `RESULTS_LEDGER.md`. If it
   can't, the difference is a bug in the new engine until proven otherwise.
   The baseline is PF 1.333 / +152.5% / 921 trades.
2. **Check the units.** Compute the number in the instrument's own terms and
   say it out loud. Pine `slippage` is in TICKS: on XAUUSD mintick is 0.001,
   so `slippage=200` is 0.20 points and `slippage=5` is 0.005 points — a 40×
   error that flattered every run made with it (BUG-021). Do this per symbol.
3. **Check the tails, not the averages.** Compare worst loss, best win, and
   longest hold against the platform — not just PF and net. An average can
   agree while the model of a bad day is completely wrong (BUG-018).
4. **Check target ÷ stop, in ATR.** Any target rule: compute the median
   distance from entry to target in ATR and divide by the stop distance in
   ATR. Below 1.0 the structure loses before a single trade is placed
   (BUG-017). State the ratio in the ledger row.
5. **Sanity-check the shape.** A win rate near 1% or near 99%, a profit
   factor above 3 on a large sample, an equity curve with no drawdown — these
   are bug signatures, not discoveries. Investigate before recording.

### 3. What counts as a result

A profit factor on its own is not a result. A row does not enter
`RESULTS_LEDGER.md` without: **trade count, date range, timeframe, slippage
and commission, and the settings that produced it.** Append the row in the
same session the number is produced — not at the end, not next time.

Nothing is marked VALID without an out-of-sample test. For anything you want
to call an edge, all of:

1. **Corrected null** — randomise the entry TIMING while applying the
   IDENTICAL filter set. The null must differ from the strategy in exactly
   one respect: the thing being tested. Write down what it holds constant
   before you run it. If the random arm is itself profitable, either the null
   is wrong or the edge is not where you think it is (BUG-023).
2. **Deflated Sharpe** (`backtest/overfit.py`) with the trial count you
   actually ran, not a flattering one.
3. **PBO via CSCV** (same module).
4. **Year by year**, including the losing years.
5. **Walk-forward slices**, all reported.
6. **Cost stress** (`backtest/stress_test.py`): commission +50%, double
   spread, slippage at 0.20 / 0.50 / 1.00 points. If the edge dies at 0.50,
   say so in the same breath as the headline number.

Current champion to beat: `strategies/gold_trend_strategy.pine` — XAUUSD
30m, Balanced, 0.20 pt slippage, PF 1.583 / +1,591.7% / 33.63% DD, 2,370
orders, Aug 2019–Aug 2026, confirmed live on TradingView. Match its window
and costs or the comparison is meaningless.

### 4. Bug classes to check every new build against

All 23 are in the registry with root causes. They cluster into eight
classes; check your work against each class, not each instance.

- **Pine semantics** (001–004): empty-array `for` runs once; no nested
  function declarations; `label.new()` with `location=` plus explicit x/y;
  `ta.crossover`/`ta.crossunder` inside a conditional evaluate wrong.
- **Silent order rejection** (012): `margin_long`/`margin_short` default to
  100% and reject risk-sized orders with no error. `pyramiding` defaults to
  0 and silently ignores `strategy.entry` while in a position.
  `max_bars_back` defaults to 300 and silently yields `na`. **Read fill rate
  before any other metric** — anything below ~100% means orders are being
  dropped and no other number means anything.
- **Reference drift** (005, 010, 015): a stop or a retest must reference the
  value at the moment of the event, not a rolling series that keeps moving.
  A rolling extreme that includes the current bar makes "retest" require no
  break at all.
- **Impossible or always-true gates** (006, 007): conditions that can never
  be false, or `AND`s that can never be satisfied. Write the truth table.
- **Timing** (008, 016): pivot-confirmed signals fire N bars late and may
  never cross; counters must increment on FILLS, not on signals.
- **Exit integrity** (014, 019, 020): every tranche needs a stop, not just a
  limit; state a trailing stop depends on must be one bar stale — update
  excursion at the END of the bar block, after the stop resolves; any trail
  defined as a function of profit must state what it does at ZERO profit.
- **Target geometry** (009, 017): clamp a bad stop distance, don't
  hard-reject it; and see check 4 above.
- **Edit symmetry** (011, 022): long and short blocks are near-identical, so
  a single-anchor edit lands on one and reports success. After any change to
  directional trade state, enumerate every per-trade variable and confirm it
  is assigned in BOTH branches.

Run `backtest/pine_lint.py` before any Pine ships. It catches undeclared
identifiers and trailing commas. It does not catch anything above.

### 5. When tracing a source through to code

This is how the repo's real gaps were found, and it works:

1. Rank the candidate files by DENSITY of the thing you're looking for
   (matches per kB), not by raw hit count — a long file always wins on
   raw count and tells you nothing.
2. Read the dense files properly. For PDFs use the `sci-pdf` or `pdf`
   skill — several sources here have broken text layers, which is exactly
   how content gets silently lost. **Never claim you read a PDF you only
   grepped.** If extraction failed, name the file and say so.
3. Then check the mechanic against the CODE, not against the playbook. The
   question is never "is this documented" — it is "does an engine implement
   it". A grep of `backtest/*.py` and `strategies/*.pine` for the mechanic's
   name settles it in seconds. This check is what revealed that eight named
   exit mechanics are correctly extracted and implemented in zero engines.
4. Classify each source: FULLY TRACED / BUILT-NEVER-MEASURED /
   EXTRACTED-NEVER-BUILT / ARCHIVED-NEVER-EXTRACTED / DELIBERATELY-EXCLUDED
   (and say where that exclusion is recorded — if it isn't recorded, it is a
   drop, not a decision).

### 6. Weighting — where research effort is worth spending

- **The exit carries the edge, not the entry.** Seven entry families were
  tested; exit configuration moved results far more than any of them. An
  unimplemented exit or trade-management rule is worth more than another
  entry signal. Weight candidates accordingly.
- **Adds to winners are the largest return lever, and pure variance** — they
  raise return and drawdown together. Never present one without the other.
- **Never optimise profit factor alone.** PF trades off against return: a
  wider trail raises PF and LOWERS return, because risk-based sizing shrinks
  the position as the stop widens. Trail 20 = PF 1.659 at +23.5%; trail 6 =
  PF 1.243 at +85.4%. Report both, always.
- **Level- and quarter-based targets already failed structurally** (BUG-017).
  Do not resurface a target rule of that shape unless it solves the
  distance-is-set-by-the-line problem.

### 7. How to report

- State what the sample supports and nothing more. No "proven", no
  "guaranteed". A PF of 3.656 on 117 trades and $34.19 of net profit was
  retracted here for exactly that reason.
- Report failures in the same voice as successes. "This source contains
  nothing we don't already have" and "the edge dies at 0.50 slippage" are
  valuable findings, not admissions.
- If you skipped something, say what and why. A silent skip is the failure
  mode this whole protocol exists to prevent.
- Don't pad a shortlist. Three real candidates beat twenty padded ones.
- **Port, don't reimplement** (BUG-013). When I supply working source, the
  deliverable is a port of THAT code; log every deviation as a numbered
  delta with a reason. Three rewrites of the key-levels module were rejected.
- **Republish the artifact AND re-send the file on every Pine change.** I
  once pasted a stale artifact and got a compile error on code that had
  already been fixed in the repo.
- **Never let a live credential enter git history.** Secrets go in a
  gitignored, mode-600 `.env` — never on argv, never logged.

### 8. Before the session ends

Capture, or it did not happen. New bug → `bugs/BUG_REGISTRY.md` with root
cause AND prevention. New validated pattern → `skills/SKILL_REGISTRY.md`.
Evidence for or against a belief → `BELIEF_REGISTER.md`. Every number →
`RESULTS_LEDGER.md`. Manifest corrections → `sources/README.md`. New state →
`MEMORY.md`. Then commit and push.

## PROMPT — COPY TO HERE

---

Written 2026-08-02, after a sweep that found five fixed-but-unregistered
bugs and eight extracted-but-unbuilt exit mechanics. Both categories existed
because earlier sessions were careful about code and careless about capture.
