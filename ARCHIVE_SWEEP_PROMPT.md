# Archive Sweep Prompt — "go through every source and find what we missed"

Companion to `SESSION_HANDOFF_PROMPT.md`. That one audits the *strategies*.
This one audits the *sources* — every PDF, text extraction, and raw pasted
transcript in the archive — and traces each one forward to see where the
chain from "material I supplied" to "measured result" actually breaks.

Copy everything between the two rulers.

---

## PROMPT — COPY FROM HERE

I am Kush Verma. I trade XAUUSD (gold), intraday on 15m/30m. This repo,
`kushverma7/Trade_Cartel` on branch `claude/confident-fermi-qku0ic`, is the
permanent archive of months of my sessions. Over that time I uploaded books,
PDFs, course extractions and pasted long transcripts of trader interviews and
mentor calls. Those were turned into playbooks, then into Pine indicators,
then into strategies, then into backtests.

**My concern: material got dropped somewhere along that chain.** A source got
archived but never extracted. A playbook got written but never built. An
indicator got built but never backtested. I want to know exactly where the
chain breaks, on every source, and what is worth recovering.

**This is an audit, not a build.** Do not write a new strategy until you have
delivered the traceability table in Step 5. Read first, then report.

### Step 0 — standing instructions

Read `CLAUDE.md` first; it overrides your defaults. Then
`trader_playbooks/COGNITIVE_ARCHITECTURE.md` (the three-mind process),
`MEMORY.md` (its last section is the session handoff), and
`trader_playbooks/STRATEGY_EXTRACTION_PROTOCOL.md` (how a source is supposed
to become a strategy — this defines what "properly extracted" means, and it
is the standard you are auditing against).

### Step 1 — the archive, as it actually stands

`trader_playbooks/sources/README.md` is the manifest. It maps every source to
the playbook it fed. **Treat it as a claim to be verified, not as truth** — it
was written by the same process that may have dropped things.

**Books, PDFs and text extractions** (`trader_playbooks/sources/`):

| file | size | claimed destination |
|---|---|---|
| `price_action_patterns_ebook_joshtrade.pdf` | 9.4 MB | "Candlestick / Chart Pattern" |
| `alchemist_concepts_forex_trading.pdf` | 4.5 MB | `alchemist_smc_concepts.md` |
| `quarterly_theory_daye_compiled.pdf` | 1.8 MB | `quarterly_theory.md` |
| `chart_pattern_cheat_sheet.pdf` | 995 KB | "Candlestick / Chart Pattern" |
| `trading_the_gann_square_of_nine.pdf` | 884 KB | `gann_square_of_nine.md` |
| `wd_gann_master_commodities_course.txt` | 815 KB | `gann_square_of_nine.md` (*cross-ref only*) |
| `quarterly_theory_daye_compiled_ransh2806.pdf` | 508 KB | `quarterly_theory.md` |
| `big_secret_of_intermarket_trading.pdf` | 475 KB | `intermarket_lag_trading.md` |
| `key_levels_guide.pdf` | 233 KB | `jeafx_key_levels.md` |
| `hima_reddy_trading_methodologies_of_wd_gann.txt` | 225 KB | `hima_reddy_gann_methodology.md` |
| `hougaard_trading_manual.txt` | 214 KB | `hougaard_price_action.md` |
| `trader_dale_order_flow_trading_setups.txt` | 140 KB | `trader_dale_orderflow.md` |
| `quarterly_theory_daye_compiled_ransh2806.txt` | 27 KB | `quarterly_theory.md` |
| `candlestick_book.txt` | 23 KB | `candlestick_patterns.md` |
| `yotov_quarters_theory_2012_glossary.txt` | 20 KB | `yotov_quarters_theory.md` |
| `pure_price_action_market_structure_smart_money.txt` | 15 KB | `pure_pa_smc.md` |
| `murphy_technical_analysis_UNUSABLE_extraction.txt` | 715 B | **never incorporated** |

The PDFs need real reading, not `grep`. Use the `sci-pdf` or `pdf` skill to
extract text properly; several have image-only or broken text layers, which is
exactly how content gets silently lost.

**Raw transcripts** — 21 files in `trader_playbooks/sources/raw_transcripts/`,
named `line<N>_<date>.txt`. These are the mentor calls and interviews I pasted
into chat. The README maps them to voices #1–#11 and #18. One pair
(`line1675`, `line1694`, "Forex James") was read and deliberately excluded as
having no mechanical model — verify that call was right rather than assuming.

**Also present and NOT in the manifest**:
`trader_playbooks/sources/trade_cartel_source_dossier.html`. Find out what it
is and whether it contains anything the manifest doesn't.

### Step 2 — the four suspects I already found

Start here; these are concrete, not hypothetical.

1. **`price_action_patterns_ebook_joshtrade.pdf` (9.4 MB) and
   `chart_pattern_cheat_sheet.pdf` (995 KB)** both claim to feed "Candlestick
   / Chart Pattern" — but `trader_playbooks/` contains
   `candlestick_patterns.md` and **no chart-pattern playbook at all**. There is
   a `chart_pattern_engine.pine` in `indicators/`. So either the extraction
   exists somewhere unlisted, or 10 MB of chart-pattern material went into an
   indicator without ever being written up. Find out which.
2. **`wd_gann_master_commodities_course.txt` (815 KB)** is listed as a
   "cross-ref" to a playbook built mainly from a different, smaller source.
   815 KB reduced to a cross-reference is the signature of an under-read
   source. Read it and report what is in it that is not in
   `gann_square_of_nine.md` or `hima_reddy_gann_methodology.md`.
3. **`murphy_technical_analysis_UNUSABLE_extraction.txt`** — the extraction
   failed and the book was never incorporated. Say plainly whether that book's
   content would add anything the other 16 sources don't already cover. If yes,
   tell me to re-upload a clean copy; if no, say so and close it.
4. **Only 3 of 21 strategy files appear anywhere in `RESULTS_LEDGER.md`**
   (`de_hybrid_strategy.pine`, `gold_trend_trailing.pine`,
   `multivoice_confluence_engine.pine`). The other 18 in `strategies/` — and
   all 37 files in `indicators/` — have no recorded measurement. Some are
   superseded and that is fine. Some may never have been tested at all. That
   distinction is most of what I want out of this audit.

### Step 3 — trace every source forward

For each source, walk the chain and record where it stops:

```
source file → playbook .md → indicator .pine → strategy .pine → ledger row
```

For each link, the question is not "does a file exist" but "did the content
actually make it through". A playbook that names a source in its header but
contains none of its specific mechanics is a broken link, not a working one.
Each playbook should already carry an "Audit pass" addendum from the
2026-07-22 second-read audit — read those, and check whether they were
honest.

Classify every source as exactly one of:

- **FULLY TRACED** — reached a ledger row with a real trade count and date range
- **BUILT, NEVER MEASURED** — reached an indicator or strategy, no ledger row
- **EXTRACTED, NEVER BUILT** — reached a playbook, no code
- **ARCHIVED, NEVER EXTRACTED** — the file is here and nothing else happened
- **DELIBERATELY EXCLUDED** — a documented decision not to use it (say where
  that decision is recorded; if it isn't recorded anywhere, it isn't a
  decision, it's a drop)

### Step 4 — read for what was missed, not just whether it was read

For every source that is not FULLY TRACED, read the actual material and answer:
does it contain a **specific, mechanical, testable rule** that this repo has
never implemented? I am not interested in general market wisdom or in another
description of what a hammer candle looks like. I want rules with numbers in
them — entry conditions, exit conditions, filters, session times, ratios.

Judge each candidate against what is already known here, from
`trader_playbooks/BELIEF_REGISTER.md`, `PLAYBOOK.md` and `RESULTS_LEDGER.md`:

- The **exit carries the edge, not the entry** — seven entry families were
  tested and the exit configuration moved results far more than any of them.
  So an unimplemented *exit or trade-management* rule is worth much more than
  another entry signal. Weight your candidates accordingly.
- **Level-based and quarter-based targets already failed structurally**
  (BUG-017; live PF 0.702). Their distance is set by where the line sits, not
  by what the trade needs. Do not resurface a target rule with this shape
  unless the source solves that specific problem.
- The current champion is `strategies/gold_trend_strategy.pine`: XAUUSD 30m,
  Balanced, 0.20 pt slippage, PF 1.583 / +1,591.7% / 33.63% DD over 2,370
  orders, Aug 2019–Aug 2026, confirmed live on TradingView. Anything you
  propose is competing with that.

### Step 5 — what I want back

1. **The traceability table** — every source, its classification from Step 3,
   and where the chain broke. This is the main deliverable.
2. **A corrections list for `sources/README.md`** — every place the manifest
   claims a mapping that the content does not support.
3. **The recovery shortlist** — the specific unimplemented rules worth
   testing, ranked, each with: the source and where in it, the rule stated
   mechanically enough to code, why it isn't already covered, and the single
   measurement that would confirm or kill it. Exit and trade-management rules
   rank above entry rules. Be strict — I would rather have three real
   candidates than twenty padded ones.
4. **The closed list** — sources you read and are confident hold nothing new,
   so I never have to wonder about them again. Being able to close a source is
   as valuable to me as finding something in it.

### Step 6 — rules I will hold you to

- **No result without its trade count and date range.** A PF with neither is
  not a result. Every number you produce gets a row in `RESULTS_LEDGER.md` in
  the same session.
- **Do not claim you read a PDF you only grepped.** If a text layer is broken
  and you could not extract it, say so and name the file. A silent skip here
  is the exact failure this audit exists to find.
- **Do not pad the shortlist.** "This source contains nothing we don't have"
  is a valid and useful finding, and I want you to say it when it's true.
- **Port, don't reimplement** (BUG-013). When source material or my own
  supplied code specifies a mechanism, implement *that* mechanism; log every
  deviation as a numbered delta with a reason.
- **Never discard.** Low-value sources stay archived and get marked, never
  deleted. That is a standing rule in this repo.
- **Capture before ending.** New bug → `trader_playbooks/bugs/BUG_REGISTRY.md`.
  New validated pattern → `trader_playbooks/skills/SKILL_REGISTRY.md`. New
  evidence for or against a belief → `BELIEF_REGISTER.md`. Manifest
  corrections → `sources/README.md`. New state → `MEMORY.md`. If it isn't
  captured, it wasn't learned.

Tools: `sci-pdf` / `pdf` skills for real PDF extraction, `backtest/*.py` for
measurement, the `tradingview` MCP server for live charts and deep backtests,
`mcp-search` for recalling past sessions. Data: `data/xauusd_15m.csv.gz`.

## PROMPT — COPY TO HERE

---

Written 2026-08-02. The four suspects in Step 2 were found by inventorying the
archive at that date; if they have since been resolved, the rest of the sweep
still stands.
