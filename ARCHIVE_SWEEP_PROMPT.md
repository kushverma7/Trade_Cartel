# Archive Sweep — Source → Playbook → Code Traceability

Copy this into any session auditing what got dropped between PDFs and code.

---

## PROMPT — COPY FROM HERE

I am Kush Verma. The repository `kushverma7/Trade_Cartel` contains 21 trader
knowledge sources (transcripts, PDFs, ebooks), their extracted playbooks, and
36 indicator/strategy Pine files built from them. I want to know **what got
dropped between the source material and the code**, and whether any of what was
dropped is worth building.

### Step 1 — read first

Same order as SESSION_HANDOFF_PROMPT.md, sections 0-3. In particular:
- `RESULTS_LEDGER.md` — what has been measured; don't re-test what's already dead
- `trader_playbooks/bugs/BUG_REGISTRY.md` — especially BUG-017 (target geometry)
  and BUG-018 (gap-fill). Most unimplemented exit mechanics will need both checks.
- `trader_playbooks/sources/README.md` — the source inventory. File → voice → doc.
- `RESEARCH_PROTOCOL_PROMPT.md` — how to avoid producing a wrong answer.

### Step 2 — the classification frame

For EVERY source in `trader_playbooks/sources/`, classify as exactly one of:

| Status | Meaning |
|--------|---------|
| FULLY TRACED | Source → playbook → `voices.py` → H82 backtest measurement |
| BUILT-MEASURED-REJECTED | Indicator/strategy built, dedicated backtest run, found no edge |
| BUILT-NEVER-MEASURED | Indicator or voices.py entry exists, no standalone backtest |
| EXTRACTED-PARTIALLY-BUILT | Key mechanics in playbook, partially in `voices.py` or an indicator |
| ARCHIVED-NEVER-EXTRACTED | Source exists in `sources/` but no playbook was built from it |
| DELIBERATELY-EXCLUDED | Mechanic explicitly not built; record WHERE the exclusion is documented |

Use `RESEARCH_PROTOCOL_PROMPT.md` rule 5 (density ranking, grep the code,
never claim tracing without checking the implementation).

### Step 3 — known answer (run done 2026-08-02; verify it hasn't changed)

| Source | Playbook | Indicator | voices.py | Status | Notes |
|--------|---------|-----------|-----------|--------|-------|
| Hougaard | hougaard_price_action.md | hougaard_4bar_fractal_engine.pine | V1, V10 | FULLY TRACED | Tested H82: V18 single-filter PF 1.498, 275 trades |
| Valentini | valentini_scalping.md, orderflow_effort_result.md | valentini_momentum_engine.pine, effort_result_engine.pine | V11, V14 | FULLY TRACED | |
| Wendell | wendell_supply_demand.md | wendell_zone_engine.pine | V9 | FULLY TRACED | |
| Hima Reddy | hima_reddy_gann_methodology.md | hima_reddy_gann_engine.pine | V3, V16 | FULLY TRACED, **⚠ BUG** | V3 coded as entry signal; source says it's a MANAGEMENT tool for open positions. PLAYBOOK.md flagged 2026-07-22; NOT fixed in voices.py. See note A below. |
| Alchemist | alchemist_smc_concepts.md | alchemist_smc_engine.pine | V6 | FULLY TRACED | |
| Gann | gann_square_of_nine.md | gann_square_of_nine_engine.pine | V4 | FULLY TRACED | |
| Nison candlesticks | candlestick_patterns.md | candlestick_engine.pine | V18 | FULLY TRACED | Tier-A alone: PF 1.498, n=275, highest per-trade quality ever measured here |
| JEAFX Key Levels | jeafx_key_levels.md | key_levels_spaceman.pine | V19, V21 | FULLY TRACED | Targets: BUG-017 rejected. Entry/exit logic: V19/V21 tested H82. |
| Ario | ario_intent_reading.md | intent_reader.pine | V15 | FULLY TRACED | |
| Yotov Quarters | yotov_quarters_theory.md | spaceman_yotov_quarters_engine.pine | — | BUILT-MEASURED-REJECTED | Quarter targets fail: median target 0.46 ATR vs 6 ATR stop (BUG-017). |
| Dave Market Structure | dave_market_structure.md | dave_swing_count.pine | — | BUILT-MEASURED-REJECTED | omnibus PF 0.843. The 5m 2-month plateau, not a Dave-specific failure. |
| Daye Quarterly Theory | quarterly_theory.md | quarterly_theory_engine.pine, spaceman_daye_quarters_engine.pine | — | EXTRACTED-PARTIALLY-BUILT | Quarter TARGETS rejected. AMDX/Judas mechanic and Q-alternation rule (H15) NOT tested. See note B. |
| Roppel | roppel_trend_following.md | — | V22 (partial) | EXTRACTED-PARTIALLY-BUILT | Risk management doctrines (3-5-7 stop, CANSLIM shakeout+3) not built. V22 covers only the HTF trend gate. |
| Orderflow E/R | orderflow_effort_result.md | effort_result_engine.pine | V11 (partial) | EXTRACTED-PARTIALLY-BUILT | Valentini volume-tsunami proxy in V11; finer effort/result mechanics not built. |
| Intermarket Lag | intermarket_lag_trading.md | intermarket_lag_engine.pine | — | BUILT-NEVER-MEASURED | LOW credibility source ("100% profitable"). Rolling-correlation gate built but not dedicated-backtested. In omnibus (PF 0.843, confounded with 3 other models). |
| Steve/MMM4x | steve_mm_cycle.md | mm_cycle_engine.pine | — | BUILT-NEVER-MEASURED | **Highest-value untested source — see note C.** |
| Kurisko | kurisko_quad_rotation.md | kurisko_quad_rotation.pine | — | BUILT-NEVER-MEASURED | Quad stochastic (4-TF compressed) indicator built; never tested as a strategy filter. |
| PBD Logic | pbd_logic.md | pbd_logic_engine.pine | — | BUILT-NEVER-MEASURED | Auction market theory (P/b/D profile). Referenced in some strategies but never dedicated-backtested. |
| FX Master Pattern | fx_master_pattern.md | fx_master_pattern_engine.pine | — | BUILT-NEVER-MEASURED | Contraction→Expansion→Trend phase model. SEVENTH independent voice on the manipulation-leg concept. |
| Trader Dale | trader_dale_orderflow.md | trader_dale_volume_profile_engine.pine | V8 (partial) | BUILT-NEVER-MEASURED, **DATA CONSTRAINT** | Requires footprint/DOM data (per-price Bid/Ask volume). Standard OHLCV cannot supply it. V8 (HVN cluster) is the best available OHLCV proxy. Playbook explicitly flags this. |
| Renko/HA ABC | renko_ha_abc_scalper.md | renko_abc_scalper.pine | — | BUILT-NEVER-MEASURED | Chart-type specific (requires Renko/HA); not testable on raw OHLCV bars. |
| Pure PA/SMC | pure_pa_smc.md | pure_pa_smc_engine.pine | — | BUILT-NEVER-MEASURED | Anonymous course. Referenced in some strategies; no dedicated backtest. |
| Murphy (Tech. Analysis) | sources/murphy_tech_analysis_UNUSABLE_extraction.txt | — | — | ARCHIVED-NEVER-EXTRACTED | Extraction yielded ~30 words of unusable fragment. Never incorporated. Re-upload a cleaner copy if content wanted. |
| "Forex James" | sources/raw_transcripts/ | — | — | DELIBERATELY-EXCLUDED | Ruled NOT the same voice as Steve/MMM4x. Generic broker content, no repeatable mechanical model. Logged in PLAYBOOK.md and sources/README.md. |

### Step 4 — the three highest-priority gaps

**Note A — Hima Reddy V3 miscoding (correctness issue, not a research gap):**
`voices.py` V3 fires the 2-bar test-failure pattern as a bidirectional ENTRY
signal. The source says explicitly: "not a signal meant to be targeted for
market entry" — it is a trade-management tool for an already-open position.
If V3 is frequently the swing vote in the net ≥ 6 gate, the gate's measured
improvement (OOS PF 1.879 → 1.954) is partly from a mis-coded voter. To fix:
recode V3 to return `+1/-1` only when a position IS open and the test
confirms the direction, `0` always otherwise. Then re-run H82 with the
corrected voices. Expected: small reduction in the gate's reach (fewer `0`
bars become `±1`), outcome on the gate measurement unknown until run.

**Note B — Daye Q-alternation rule (H15, never tested):**
The Q-alternation rule states: a consolidating quarter implies an expanding
next quarter; an expanding quarter implies a consolidating next. In practice:
if the previous 90-minute quarter's ATR is below the 20-bar median, enter the
next quarter; if above (expanding), skip. This is a pure session-time
volatility filter, no price prediction. One command to test: add a
`q_filter` flag to `backtest/trend.py` that gates entries to bars where the
prior session-quarter ATR is below the rolling median. Check: target÷stop
ratio must still be ≥ 1.0 after the filter (a volatility filter that selects
quieter bars may also select worse R:R setups — verify before concluding).

**Note C — Steve/MMM4x Brinks windows (highest-EV untested mechanic):**
Two specific time windows are claimed as highest-probability entry zones:
03:30–03:45 ET (London Brinks) and 09:30–09:45 ET (NY Brinks). The model's
logic: the real move starts from the stop-hunt hammer/spike at these times.
The champion already uses session filtering; narrowing to Brinks windows is
a one-parameter tweak. To test: add `brinks_filter = True` to
`backtest/trend.py` that restricts entries to bars in those two 15-minute
windows. Two gates in one: (1) confirms the champion's session finding, or
(2) narrows entries to higher-quality setups, improving PF and R:R.
Weakness: may thin trade count below the noise threshold. Check n after
applying; if below 300, the result is noise.

Steve also supplies a 2-hour scratch rule: "a trade showing no substantial
profit within 2 hours is scratched." This is a time-based exit — the kind
of thing this project has confirmed works (exits > entries). To test: add
a `scratch_hours` parameter to `backtest/exit_lab.py` that closes any
position still at breakeven or below after N bars (N = 4 at 30m). Check
before/after on the champion's default config: does it cut losers early
enough to raise PF, or does it cut winners before they develop? The answer
is in the exit attribution numbers `backtest/exit_lab.py` already produces.

### Step 5 — what to do with BUILT-NEVER-MEASURED sources

Do NOT build a new strategy from them. The right path is the one the voices.py
framework established: extract the mechanic as a binary filter (+1/-1/0),
add it to `voices.py`, and run the voices test (H82) with it included. If the
voice raises the measured gate improvement (OOS PF, OOS DD), it earns inclusion
in the shipped engine. If not, it is logged as tested and rejected.

The one exception is Steve/MMM4x's time grid (note C above), which is a
session filter, not a binary price signal — add it directly to `trend.py`.

## PROMPT — COPY TO HERE

---

Written 2026-08-02.
