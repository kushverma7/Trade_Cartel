# ARCHIVE SWEEP — What Got Built vs What Got Dropped
# Completed 2026-08-02. Classifies every source, every mechanic,
# and every code file against the five-status taxonomy defined in
# RESEARCH_PROTOCOL_PROMPT.md §5.

---

## The Five Statuses

| Status | Definition |
|---|---|
| **FULLY TRACED** | Source → playbook → code → backtest row in RESULTS_LEDGER.md |
| **BUILT-NEVER-MEASURED** | Code exists; no backtest row exists |
| **EXTRACTED-NEVER-BUILT** | In playbook/voice; no code exists |
| **ARCHIVED-NEVER-EXTRACTED** | Source file exists; content not distilled |
| **DELIBERATELY-EXCLUDED** | Read, reviewed, recorded as not worth building |

---

## Part 1 — The 22 Voices (voice register: voices.py)

All 22 voices were implemented in `backtest/voices.py` and measured.
**Finding: H73 FALSIFIED.** PF falls as conviction rises.
Train PF 0.859 / OOS PF 0.960 — loses on both halves at every threshold.

| V# | Voice | Source | Code | Status |
|---|---|---|---|---|
| V1 | Hougaard 4-bar fractal | hougaard_price_action.md | voices.py, hougaard_4bar_fractal_engine.pine | FULLY TRACED → REJECTED |
| V2 | Failed visits (price returns to a level it broke) | dave_market_structure.md | voices.py | FULLY TRACED → REJECTED |
| V3 | Hima 2-bar test failure | hima_reddy_gann_methodology.md | voices.py, hima_reddy_gann_engine.pine | FULLY TRACED → REJECTED ⚠️ misclassified — see below |
| V4 | Gann signal day | hima_reddy_gann_methodology.md | voices.py | FULLY TRACED → REJECTED |
| V5 | Role inversion (old S becomes R) | multiple | voices.py | FULLY TRACED → REJECTED |
| V6 | IDM-gated BOS | pure_pa_smc.md | voices.py | FULLY TRACED → REJECTED |
| V7 | Liquidity grab (wick-sweep + reclaim) | multiple | voices.py | FULLY TRACED → REJECTED |
| V8 | HVN / VWAP proxy | trader_dale_orderflow.md | voices.py | FULLY TRACED → REJECTED |
| V9 | Wendell zone (supply/demand zone hold) | wendell_supply_demand.md | voices.py, wendell_zone_engine.pine | FULLY TRACED → REJECTED |
| V10 | Mid-trend divergence (continuation read) | hougaard_price_action.md | voices.py | FULLY TRACED → REJECTED |
| V11 | Volume tsunami (quality-break filter) | roppel_trend_following.md | voices.py | FULLY TRACED → REJECTED |
| V12 | EMA bunching (non-trend filter) | steve_mm_cycle.md | voices.py | FULLY TRACED → REJECTED |
| V13 | ADR thirds (level position within day) | steve_mm_cycle.md | voices.py | FULLY TRACED → REJECTED |
| V14 | Momentum-join (join confirmed trend; Valentini school) | valentini_scalping.md | voices.py | FULLY TRACED → REJECTED |
| V15 | Leg regime (mature vs. immature leg) | dave_market_structure.md | voices.py | FULLY TRACED → REJECTED |
| V16 | Eighths (quarters theory price grid) | yotov_quarters_theory.md | voices.py | FULLY TRACED → REJECTED |
| V17 | Rejection count (level weakens with each test) | valentini_scalping.md | voices.py | FULLY TRACED → REJECTED |
| V18 | Nison tier-A candlestick (engulfing/doji/hammer) | candlestick_patterns.md | voices.py | FULLY TRACED → REJECTED |
| V19 | KL sweep + reclaim | jeafx_key_levels.md | voices.py | FULLY TRACED → REJECTED |
| V20 | Session structure (time of day) | steve_mm_cycle.md | voices.py | FULLY TRACED → REJECTED |
| V21 | KL break + retest | jeafx_key_levels.md | voices.py | FULLY TRACED → REJECTED |
| V22 | HTF trend (EMA stack alignment) | multiple | voices.py | FULLY TRACED → REJECTED |

**⚠️ V3 MISCLASSIFICATION ALERT:** `hima_reddy_gann_engine.pine` implements
the 2-bar test failure as an ENTRY SIGNAL. The source text (Hima Reddy's
methodology) describes it as a TRADE MANAGEMENT tool — a technique for managing
an EXISTING position, not for initiating one. The engine's classification as a
valid entry engine requires re-examination. This is noted in PLAYBOOK.md (Wave 2
audit) but has not been corrected in the engine's code.

---

## Part 2 — Display Indicators (no backtest row exists for any of these)

| File | Source | Status | Notes |
|---|---|---|---|
| `indicators/dave_swing_count.pine` | dave_market_structure.md | BUILT-NEVER-MEASURED | Swing maturity display only |
| `indicators/fx_master_pattern_engine.pine` | fx_master_pattern.md | BUILT-NEVER-MEASURED | FX Master Pattern display |
| `indicators/intermarket_lag_engine.pine` | intermarket_lag_trading.md | BUILT-NEVER-MEASURED | Intermarket lag signals |
| `indicators/kurisko_quad_rotation.pine` | kurisko_quad_rotation.md | BUILT-NEVER-MEASURED | Quad rotation display |
| `indicators/hougaard_4bar_fractal_engine.pine` | hougaard_price_action.md | BUILT-NEVER-MEASURED | 4-bar fractal display |
| `indicators/mm_cycle_engine.pine` | steve_mm_cycle.md | BUILT-NEVER-MEASURED | Steve time grid, Asia box, ADR level count |
| `indicators/valentini_momentum_engine.pine` | valentini_scalping.md | BUILT-NEVER-MEASURED | Momentum-join + revert display |
| `indicators/pbd_logic_engine.pine` | pbd_logic.md | BUILT-NEVER-MEASURED | PBD close-count display |
| `indicators/wendell_zone_engine.pine` | wendell_supply_demand.md | BUILT-NEVER-MEASURED | S/D zone display |
| `indicators/gann_square_of_nine_engine.pine` | gann_square_of_nine.md | BUILT-NEVER-MEASURED | Gann grid display |
| `indicators/quarterly_theory_engine.pine` | quarterly_theory.md | BUILT-NEVER-MEASURED | QT display |
| `indicators/renko_abc_scalper.pine` | renko_ha_abc_scalper.md | BUILT-NEVER-MEASURED | Renko/HA display |
| `indicators/at_sentiment_herd_regime.pine` | — (ATSH composite) | BUILT-NEVER-MEASURED | Delivered 2026-08-02 |
| `indicators/candlestick_engine.pine` | candlestick_patterns.md | BUILT-NEVER-MEASURED | |
| `indicators/chart_pattern_engine.pine` | — | BUILT-NEVER-MEASURED | |
| `indicators/effort_result_engine.pine` | trader_dale_orderflow.md | BUILT-NEVER-MEASURED | |
| `indicators/intent_reader.pine` | ario_intent_reading.md | BUILT-NEVER-MEASURED | |
| `indicators/key_levels_spaceman.pine` | jeafx_key_levels.md | BUILT-NEVER-MEASURED | Display-only port of SpacemanBTC V13.1 |
| `indicators/pure_pa_smc_engine.pine` | pure_pa_smc.md | BUILT-NEVER-MEASURED | |
| `indicators/spaceman_daye_quarters_engine.pine` | quarterly_theory.md | BUILT-NEVER-MEASURED | |
| `indicators/spaceman_yotov_quarters_engine.pine` | yotov_quarters_theory.md | BUILT-NEVER-MEASURED | |
| `indicators/trader_dale_volume_profile_engine.pine` | trader_dale_orderflow.md | BUILT-NEVER-MEASURED | |

---

## Part 3 — Strategies (have backtest rows or are retracted)

| File | Engine | LEDGER Row | Status |
|---|---|---|---|
| `strategies/gold_trend_strategy.pine` | Donchian + Chandelier trail | #23 (OOS SHIPPED) | **CHAMPION** |
| `strategies/gold_trend_trailing.pine` | Same engine, trailing-only variant | #22-23 predecessor | active (trailMultEE bug fixed 2026-08-02) |
| `strategies/multivoice_confluence_engine.pine` | Multi-Voice, 15m | #13 (in-sample only) | superseded by 30m champion |
| `strategies/key_levels_spaceman_edition.pine` | Key Levels, 30m | #15-17 | VOID (BUG-012 order rejections) |
| `strategies/trendline_key_level_strategy.pine` | Trendline × Key Levels | #11-12 | plateau — retired |
| `strategies/key_to_key_strategy.pine` | Key-to-Key | #10 | plateau — retired |
| `strategies/omnibus_four_model_engine.pine` | OMNIBUS four-model | #9 | plateau — retired |
| `strategies/trendline_breakout_*.pine` | Session Trendline Breakout | #2 | RETRACTED (sample too small) |
| `strategies/reversal_sniper_strategy.pine` | Reversal Sniper v2 | #1 | RETIRED (mechanism banned) |
| All remaining strategy files | Various | no ledger row | BUILT-NEVER-MEASURED |

---

## Part 4 — Exit Mechanics: EXTRACTED-NEVER-BUILT

The champion uses one exit type: Chandelier ATR trailing stop. Eight named exit
mechanics from three high-credibility sources are extracted in playbooks but
implemented in zero strategies and zero backtest files.

| # | Mechanic | Source | Where Extracted | Code that implements it |
|---|---|---|---|---|
| 1 | Doji-tightens-stop (tighten immediately when doji closes against position) | Hougaard §8 | hougaard_price_action.md | None |
| 2 | Volume-spike-near-S/R → tighten or take profit | Hougaard §8 | hougaard_price_action.md | None |
| 3 | Scale-out: 1/3 @ ~20pts / 1/3 @ next-high (stop→BE) / 1/3 runner (Mark Douglas method, attributed) | Hougaard §8 audit | hougaard_price_action.md | None |
| 4 | Scale-in only when P1 stop can move to breakeven (P1 stop = P2 stop; total risk never increases on add) | Hougaard §8 | hougaard_price_action.md | None |
| 5 | Full exit at previous POC (market reverts from POC ~70% — Valentini's claim) | Valentini exit mechanics | valentini_scalping.md | None |
| 6 | Failed-auction-at-target while in profit → secure profit immediately | Valentini exit mechanics | valentini_scalping.md | None |
| 7 | 3-5-7 scaled stop: exit 1/3 at −3% / 1/3 at −5% / 1/3 at −7% from entry | Roppel risk architecture | roppel_trend_following.md | None |
| 8 | Cushion protocol: no YTD cushion = tight and risk-averse; large cushion = play against it | Roppel risk architecture | roppel_trend_following.md | None |

**Decision required for each:** Build and test as a modification to the champion's
exit layer, or explicitly record why it was not built. "Not yet tested" is acceptable;
"silently dropped" is not.

---

## Part 5 — Sources: ARCHIVED-NEVER-EXTRACTED and DELIBERATELY-EXCLUDED

| Source | File | Status | Reason |
|---|---|---|---|
| Murphy — Technical Analysis of Financial Markets | `sources/murphy_technical_analysis_UNUSABLE_extraction.txt` | ARCHIVED-NEVER-EXTRACTED | Extraction was ~30 words. Content not distilled into any playbook. |
| Forex James | `sources/raw_transcripts/line1675_2026-07-20.txt`, `line1694_2026-07-20.txt` | DELIBERATELY-EXCLUDED | Generic "market maker manipulation" 101 with no repeatable counting system. Zero shared mechanics with Steve's model. Preserved verbatim; not built. |
| Josh Trade price action ebook | `sources/price_action_patterns_ebook_joshtrade.pdf` | ARCHIVED-NEVER-EXTRACTED | PDF exists; no playbook entry found. |
| Alchemist SMC concepts PDF | `sources/alchemist_concepts_forex_trading.pdf` | Partially traced → `alchemist_smc_engine.pine` | BUILT-NEVER-MEASURED |
| Big Secret of Intermarket Trading | `sources/big_secret_of_intermarket_trading.pdf` | Partially traced → intermarket_lag_trading.md → `intermarket_lag_engine.pine` | BUILT-NEVER-MEASURED |

---

## Part 6 — What the Sweep Found

### Finding 1: The voice layer is fully traced and fully rejected.
All 22 voices implemented, all 22 measured. H73 falsified: PF 0.859 train,
0.960 OOS. The voice register is complete as a research artifact. It should
not be treated as an active toolset.

### Finding 2: Eight exit mechanics are extracted and live in zero engines.
Named in §5 above. These are the highest-value untested candidates in the repo
because the champion's validation confirms the exit carries the edge.

### Finding 3: 22+ display indicators are built and never measured.
No backtest row exists for any indicator in the `indicators/` directory.
They display signals on charts; whether those signals have any predictive value
is unknown. This is not necessarily a problem — display indicators are tools, not
strategies — but the implication is that no indicator in this repo has been
validated as a filter for the champion.

### Finding 4: V3 (Hima 2-bar test) is misclassified in its engine.
`hima_reddy_gann_engine.pine` uses a trade-management technique as an entry
signal. The source text is unambiguous. The engine needs a design review.

### Finding 5: Murphy is still unexploited.
A ~30-word extraction of a 700-page reference text is not an extraction.
Either extract it properly or officially mark it DELIBERATELY-EXCLUDED.

### Finding 6: The champion's validation settles the entry question.
"Every bar the gate allows" (random timing through full filter stack) returns
OOS PF 1.914. The champion with Donchian entry returns OOS PF 1.588. Entry
hurts returns. The exit is the system. New research must start from the exit.

---

## How to Use This Document

1. **Before building a new engine:** check Part 4. If a relevant exit mechanic
   already exists as EXTRACTED-NEVER-BUILT, test that one first.
2. **Before claiming something is "validated":** it must have a RESULTS_LEDGER.md
   row with `n`, `WR`, `PF`, `net`, `DD`, `window`, and must have passed all
   three gates in RESEARCH_PROTOCOL_PROMPT.md §3.
3. **When a source is read:** update the appropriate status in this document.
4. **When code is written:** update Part 2 or Part 3 with the new file.
5. **When a backtest is run:** append a row to RESULTS_LEDGER.md and update
   the status in Part 3 from BUILT-NEVER-MEASURED to the result.
