# BUG REGISTRY
Permanent record of every code bug found in this project, per
SKILL_EXPANSION_FRAMEWORK.md Part III. Read this BEFORE writing any new
Pine code. If new code resembles an affected pattern, explicitly state
how it avoids the registered bug.

Seeded 2026-07-22 from the project's full session history — these are
all REAL bugs that actually occurred here, not hypotheticals.

---

### BUG-001: Empty-array `for` loop executes once anyway
- **Date Found:** ~2026-07-20 (recurred in 2+ engines)
- **Severity:** High (runtime error)
- **Symptom:** "Index out of bounds" runtime errors on chart load
- **Root Cause:** `for i = 0 to array.size(arr) - 1` still executes once
  with i=0 when the array is empty (size-1 = -1; Pine's for loop runs
  start-to-end inclusive even when end < start with default step)
- **Fix:** Guard with `if array.size(arr) > 0` BEFORE the loop
- **Prevention:** Phase 3 checklist "every array access bounds-checked"
- **Affected Files:** hima_reddy_gann_engine.pine (zone-box deletion),
  spaceman_yotov_quarters_engine.pine (gridLines deletion)
- **Status:** Fixed in both; pattern now standard

### BUG-002: Nested function declaration
- **Date Found:** 2026-07-20
- **Severity:** Critical (compile error)
- **Symptom:** Pine compiler rejects the script
- **Root Cause:** A function body tried to declare an inner helper
  function — Pine does not support nested function declarations
- **Fix:** Inline the per-item logic with arrays + a guarded loop
- **Prevention:** Phase 2 rule "one function, one purpose," flat scope
- **Affected Files:** spaceman_yotov_quarters_engine.pine
  (f_nearestSpacemanLevel), caught before user test
- **Status:** Fixed

### BUG-003: `label.new()` with `location=` + explicit x/y
- **Date Found:** ~2026-07-19
- **Severity:** Critical (compile error)
- **Symptom:** Compile error on label calls
- **Root Cause:** `label.new()` does not accept a `location=` parameter
  when explicit x/y coordinates are passed
- **Fix:** Drop `location=`, use `style=` + explicit y anchor
- **Prevention:** Phase 5 "code compiles" check
- **Affected Files:** hima_reddy_gann_engine.pine
- **Status:** Fixed

### BUG-004: `ta.crossover`/`ta.crossunder` inside conditionals
- **Date Found:** ~2026-07-19
- **Severity:** High (inconsistent signals + compiler warning)
- **Symptom:** "should be called on each calculation for consistency"
  warning; signals inconsistent
- **Root Cause:** ta.* cross functions nested inside conditional blocks
  don't evaluate every bar, breaking their internal state
- **Fix:** Persist the comparison series via `var float` inside the
  conditional, call the cross function unconditionally at top level
- **Prevention:** Phase 1 data-dependency graph
- **Affected Files:** multiple engines
- **Status:** Fixed; pattern now standard

### BUG-005: Stop referenced the swept LEVEL, not the sweep EXTREME
- **Date Found:** 2026-07-20 (live test: 12/12 losses, PF-analog 0)
- **Severity:** Critical (logic — every trade lost)
- **Symptom:** 100% stop-out rate on JUDAS sweep signals
- **Root Cause:** `trkStop` referenced `pdLow`/`pdHigh` — the level
  BEING swept, already pierced by definition (signal requires
  `low < pdLow`), so the stop sat INSIDE the sweep zone
- **Fix:** Reference the actual sweep-bar wick extreme (`low`/`high`,
  or `low[1]`/`high[1]` for two-bar patterns) plus ATR buffer
- **Prevention:** Phase 4 bar-by-bar desk check of the entry bar
- **Affected Files:** spaceman_daye_quarters_engine.pine; the same
  near-miss was caught pre-delivery in amdm engines twice
- **Status:** Fixed; documented as a named anti-pattern

### BUG-006: Re-arm gate with always-true OR condition
- **Date Found:** 2026-07-20 (live test: clustering persisted, PF 0.67)
- **Severity:** High (logic — filter did nothing)
- **Symptom:** Signal clustering persisted despite a "fix"
- **Root Cause:** `(wallIdentityChanged OR priceMovedEnough)` — wall
  identity changes trivially (a different wall TYPE becoming nearest by
  a cent counts), so the OR was true almost every bar and the gate
  never blocked anything
- **Fix:** Drop the trivially-true path; gate on price distance alone
- **Prevention:** Phase 0 truth table — enumerate when each OR branch
  is true; if one branch is nearly-always true, the gate is dead
- **Affected Files:** trade_cartel_topbottom_engine.pine
- **Status:** Fixed (took 3 iterations; iterations 1-2 were guesses,
  iteration 3 was the diagnosis — see PLAYBOOK.md)

### BUG-007: Self-contradictory volume gate (impossible AND)
- **Date Found:** 2026-07-22 (live test: zero trades ever)
- **Severity:** Critical (logic — model could never fire)
- **Symptom:** Model 2 produced zero trades, period
- **Root Cause:** Required volume >120% AND <100% of the same average
  on the SAME bar — mathematically impossible
- **Fix:** Split across two bars: sweep+high-volume on bar[1],
  reclaim+exhaustion-volume on bar[0], per the source doc's own
  two-candle language
- **Prevention:** Phase 0 truth table MUST include volume conditions —
  an all-false output column means the logic is broken
- **Affected Files:** amdm_confluence_engine.pine,
  amdm_confluence_strategy.pine
- **Status:** Fixed in round 1

### BUG-008: Pivot-confirmed BOS fires 10 bars late (never crosses)
- **Date Found:** 2026-07-22 (external review, confirmed on inspection)
- **Severity:** High (logic — model nearly mute)
- **Symptom:** Model 1 rarely/never fired
- **Root Cause:** `ta.pivothigh(10,10)` confirms the swing level 10
  bars AFTER it forms; by then price is already past it, so
  `ta.crossover(close, level)` almost never triggers
- **Fix:** Real-time Donchian-style breakout: close crossing the prior
  N-bar `ta.highest/lowest` with [1]-offset — no confirmation lag,
  non-repainting
- **Prevention:** Phase 1 "first 3 bars" walkthrough + asking "WHEN
  does this variable update relative to when the event happens?"
- **Affected Files:** amdm_confluence_engine.pine,
  amdm_confluence_strategy.pine
- **Status:** Fixed in round 2

### BUG-009: Hard-reject stop-distance gate instead of clamp
- **Date Found:** 2026-07-22
- **Severity:** High (logic — silently vetoed valid setups)
- **Symptom:** Contributed to zero Model 1 trades
- **Root Cause:** Any BOS whose stop distance exceeded maxATR was
  REJECTED — but stop distance is naturally wide right after a real
  breakout, so the filter killed exactly the setups it should catch
- **Fix:** CLAMP the distance into [min,max] × ATR instead of
  rejecting the trade
- **Prevention:** Phase 0 edge case #4 (news spike / extended bar)
- **Affected Files:** amdm engines (both)
- **Status:** Fixed in round 1

### BUG-010: Reclaim checked against a moving reference level
- **Date Found:** 2026-07-22 (external review, confirmed)
- **Severity:** Medium (logic — made valid signals rarer/incoherent)
- **Symptom:** Model 2 signals extremely rare even after BUG-007 fix
- **Root Cause:** Sweep judged against bar[1]'s value area but reclaim
  against the CURRENT bar's recalculated rolling value area — the
  reference shifts with the very move being evaluated
- **Fix:** Freeze both checks to the sweep bar's level (val[1]/vah[1])
- **Prevention:** Phase 1 variable lifecycle map — "which bars does
  this reference update on?"
- **Affected Files:** amdm engines (both)
- **Status:** Fixed in round 2

### BUG-011: Inverted SuperTrend trailing conditions
- **Date Found:** 2026-07-21 (caught pre-delivery in self-review)
- **Severity:** Critical (logic — bands would trail backwards)
- **Symptom:** N/A (caught before user test)
- **Root Cause:** `finalUpper`/`finalLower` carry-forward conditions
  were written inverted on first draft
- **Fix:** Corrected to the canonical construction before delivery
- **Prevention:** Phase 4 desk check against a known-good reference
  implementation
- **Affected Files:** trade_cartel_supertrend_engine.pine (since
  removed from repo for unrelated scope reasons)
- **Status:** Fixed then file removed

### BUG-012: Silent order rejection — risk sizing vs. default 100% margin
- **Date Found:** 2026-07-22 (live test: labels drew, zero trades in tester)
- **Severity:** Critical (execution — every order skipped)
- **Symptom:** Signal labels appear on the chart but the Strategy
  Tester reports "This report requires trade data" — zero trades. The
  label proving the entry code path ran is the diagnostic tell.
- **Root Cause:** Pine v6 strategies default `margin_long`/`margin_short`
  to 100% (no leverage). Risk-percent sizing (`equity x risk% / stop
  distance`) on a tight gold stop demands multi-million-dollar
  notional on a 5-figure account; TradingView SILENTLY skips any
  order exceeding buying power — no error, no log.
- **Fix:** Declare `margin_long=5, margin_short=5` (20:1, typical gold
  CFD) AND hard-cap qty at `equity x maxLeverage / close` so sizing
  can never demand more notional than the account holds.
- **Prevention:** Phase 0 edge-case inventory gains a permanent entry:
  "what is the LARGEST position this sizing formula can request, and
  can the tester actually fill it?" Any strategy using qty= sizing
  must declare margins explicitly.
- **Which Mind Found It:** Profit Engine (label-vs-tester divergence
  pointed at execution, not signal logic)
- **Affected Files:** omnibus_four_model_engine.pine,
  amdm_confluence_strategy.pine (same sizing chassis)
- **Status:** Fixed in both

---

## BUG-013 — Reimplementing a supplied indicator instead of porting it
- **Symptom:** User supplied the SpacemanBTC Key Levels V13.1 source and
  asked for a strategy that "looks like the screenshot". Three separate
  attempts to redraw the levels were rejected by the user in three
  consecutive messages ("it still didnt have spaceman indicator showing",
  "even after telling you twice it still has no key levels", "it still
  hasnt shown the key levels").
- **Root cause:** Each attempt reimplemented the LOOK from memory rather
  than running the SOURCE. The three failure modes were, in order:
    v1 `plot()` series lines -- wrong geometry, no per-level labels.
    v2 drawings created early and mutated later -- did not render at all
       inside a strategy.
    v3 `xloc.bar_time` + a `timenow + 150min` projection -- labels landed
       past the visible range, so the levels existed but were off-screen.
  The supplied source already solved all three (anchored x1 per level,
  fresh creation inside `barstate.islast`, `timenow + (time-time[1])*30`,
  plus a label-merge pass). Every rewrite discarded that and re-derived
  it worse.
- **Fix:** Stop rewriting. Port the source verbatim into
  `trader_playbooks/skills/key_levels_module.pine`, change only what v6
  and host-embedding strictly require (5 documented port deltas), and
  paste that block into every strategy. Original quirks -- including the
  source's own bugs -- are preserved deliberately, because the user's
  chart looks the way it does because of them.
- **Prevention:** New CODE_DELIVERY_PROTOCOL rule. **When the user
  supplies working source, the deliverable is a PORT, not a rewrite.**
  Phase 1 (spec freeze) must record "supplied source exists -> port it",
  and any deviation from the supplied code must be listed explicitly as
  a numbered port delta with a stated reason. A visual requirement
  ("make it look like X") supplied together with X's source code is not
  a design brief; it is a copy instruction.
- **Which Mind Found It:** none. The user found it, three times, which is
  the actual finding: three rejections in a row on the same point should
  have triggered "my approach is wrong", not "my implementation needs
  another pass".
- **Affected Files:** trendline_key_level_strategy.pine,
  confluence_sniper_strategy.pine (both had hand-rolled blocks; both
  replaced wholesale), multivoice_confluence_engine.pine,
  key_to_key_strategy.pine, omnibus_four_model_engine.pine,
  amdm_confluence_strategy.pine (module added)
- **Status:** Fixed -- all six strategies now carry the verbatim module

---

## BUG-014 — Unstopped TP1 tranche (strategy.exit with limit but no stop)
- **Symptom:** Key Levels Strategy v1.0 showed largest loss $639.14 against
  largest profit $194.84 -- a 3.3x asymmetry the wrong way on a strategy
  whose fixed TP1 is 1.5R and whose max stop is 2.5xATR.
- **Root cause:** `strategy.exit("L1", "L", limit=tp1, qty=q1)` supplies a
  limit and no stop. Pine does not inherit the sibling exit's stop. So the
  TP1 tranche -- 60% of the position by default -- had NO stop loss and
  rode until the 36-bar time stop. Only the 40% L2 tranche was protected.
- **Fix:** every `strategy.exit` call that owns part of a position must
  carry `stop=`. Both tranches now do.
- **Prevention:** CODE_DELIVERY_PROTOCOL phase 3 gains a check: for each
  strategy.exit, assert BOTH a stop and a limit are present, or state
  explicitly why the tranche is intentionally unprotected. A quick grep
  catches it: any `strategy.exit(` line containing `limit=` but not `stop=`.
- **Which Mind Found It:** Profit Engine -- the win/loss size asymmetry did
  not match the declared R geometry, which pointed at exits before entries.
- **Affected Files:** key_levels_spaceman_edition.pine
- **Status:** Fixed in v1.1

---

## BUG-015 — Rolling extreme includes the current bar, so "retest" needs no break
- **Symptom:** "Break + Retest" mode fired on bars where no break had
  occurred.
- **Root cause:** `low12 = ta.lowest(low, 12)` includes the current bar.
  The condition `low12 < lv` was therefore satisfied by the retest bar's
  OWN wick dipping below the level, while `low > lv - tol` kept that wick
  shallow. Net effect: any bar that touched the level from above and closed
  above it qualified as a break-and-retest. The prior break was never
  required.
- **Fix:** `ta.lowest(low, n)[1]` / `ta.highest(high, n)[1]` so the lookback
  genuinely excludes the bar being evaluated.
- **Prevention:** this is BUG-008's family (WHEN does a variable update
  relative to the event it describes). New standing check: any rolling
  extreme used as "price was previously beyond X" evidence must carry a
  `[1]` offset, because the current bar is the thing being tested.
- **Which Mind Found It:** Microstructure Predator (static read of the
  condition's truth table)
- **Affected Files:** key_levels_spaceman_edition.pine
- **Status:** Fixed in v1.1

---

## BUG-016 — Counters incremented on signals rather than fills
- **Symptom:** daily trade cap and cooldown throttled trades that were
  never actually filled.
- **Root cause:** `dayTrades += 1` sat inside the `if goLong` block, which
  fires when the ORDER IS PLACED, not when it fills. With BUG-012's silent
  margin rejection also present, the cap was being consumed by phantom
  trades and suppressing real ones.
- **Fix:** counters gated on `strategy.opentrades + strategy.closedtrades`
  actually increasing.
- **Prevention:** any counter that represents "trades taken" must read from
  strategy state, never from signal state. Corollary added to the dashboard
  standard: every engine now displays Signals / Filled / Fill rate, so an
  order-rejection gap is visible on the chart instead of being inferred
  from a suspiciously low trade count.
- **Which Mind Found It:** Profit Engine
- **Affected Files:** key_levels_spaceman_edition.pine
- **Status:** Fixed in v1.1

---

## BUG-017 — Level-based targets structurally break the R:R before any trade fires
- **Date Found:** 2026-07-31
- **Severity:** High (strategy design — makes whole class of engines unviable)
- **Symptom:** Key Levels (Spaceman Edition) strategies showed negative net even
  when individual entries looked selective; target/stop ratio was measured below 1.0.
- **Root Cause:** Median XAUUSD key level distance from price at entry is 0.46 ATR.
  The champion exit uses a 6 ATR trail. A 0.46 ATR target against a 6 ATR stop is
  R:R = 0.077 — the strategy loses before a single trade fires. This is structural: the
  geometry of "hit the nearest key level as TP" is incompatible with any ATR-scale
  trailing stop. Level-based TP only works when levels are farther away than the stop.
- **Fix:** Never use key levels as profit targets when the trailing stop is ATR-scale.
  Use key levels as ENTRIES (BOS/reclaim) or as STOP anchors only. If you must use a
  level as a target, verify that median(level_distance) / stop_distance > 1.5 BEFORE
  building the engine.
- **Prevention:** Pre-flight check added to CODE_DELIVERY_PROTOCOL: compute
  expected target/stop distance ratio on representative data before committing to an
  exit structure. A strategy with target/stop < 1.0 is rejected at design.
- **Which Mind Found It:** Profit Engine (DSR audit exposed the T:S mismatch)
- **Affected Files:** key_levels_spaceman_edition.pine (all versions), any engine using
  key levels as TP targets
- **Status:** Structural finding — no "fix" for v1.x; informs design of any future engine

---

## BUG-018 — Gap-fill stop execution: bar opening through stop fills at the open, not the stop
- **Date Found:** 2026-07-31
- **Severity:** Medium (P&L distortion on gap bars)
- **Symptom:** Python backtest showed better results than Pine on gap sessions.
  Specifically, days where price gapped through the trailing stop showed the backtest
  crediting a fill at the exact stop price rather than the open.
- **Root Cause:** Default backtest loop: `if low[i] <= stop: fill at stop`. On a gap
  bar where `open[i] < stop`, this credits a fill that was never available — the market
  opened below (or through) the stop, so the real fill is at the open.
- **Fix:** `gap_fill=True` in engine.py: when `open[i] <= stop` (for long), fill at
  `open[i]`, not at `stop`. This is the gap-aware fill path. Always enable in production.
- **Prevention:** gap_fill must default to True. Any new Python backtest that touches
  stop-loss execution must assert gap_fill is active. Gap-unaware results are labelled
  "(OPTIMISTIC — gap fills)" in any report that includes them.
- **Which Mind Found It:** Microstructure Predator (cross-validation against TradingView
  revealed the discrepancy on gap bars)
- **Affected Files:** backtest/engine.py, backtest/trend.py
- **Status:** Fixed — gap_fill=True is the default in engine.py

---

## BUG-019 — Intrabar lookahead: excursion updated before stop resolves
- **Date Found:** 2026-07-31
- **Severity:** Medium (corrupts giveback trail arm logic)
- **Symptom:** Giveback trail (fraction of best excursion) arms late or early
  inconsistently; measured WR < 2% on a giveback-trail run spanning 2,307 trades.
- **Root Cause:** The excursion high was updated at the TOP of the bar processing
  block, before the stop-check ran. On the bar that hit the stop, `best_excursion`
  had already been updated to `high[i]` (which might be the stop-triggering wick),
  inflating the excursion measurement and causing the trail to arm too early or at
  the wrong level.
- **Fix:** Update excursion at the END of the bar block, after all stop/exit logic
  has resolved. The stop check runs first on any bar; excursion update is last.
- **Prevention:** Rule added: any variable that measures the "best state the trade
  achieved" must be updated AFTER all exit conditions on that bar — exit-first,
  measure-second.
- **Which Mind Found It:** Profit Engine (1% WR over thousands of trades is a
  mechanical failure, not a market failure)
- **Affected Files:** backtest/engine.py, backtest/trend.py (giveback trail path)
- **Status:** Fix required in engine.py — update ordering must be audited

---

## BUG-020 — Giveback trail never arms: arm threshold exceeds realistic profit level
- **Date Found:** 2026-07-31
- **Severity:** High (feature completely non-functional)
- **Symptom:** Giveback trail mode ran 2,307 trades with WR ~1% — functionally
  identical to "no trail, always stopped out at the initial stop."
- **Root Cause:** `giveback_arm = 2.0` means the trail only activates after price
  has moved 2.0 ATR in favour. On 15m XAUUSD, the median winning trade never
  reached 2.0 ATR excursion. The trail mode was active in code but unreachable
  in the data.
- **Fix:** Set `giveback_arm` to a value less than or equal to the median winning
  trade excursion on the target instrument/timeframe. Measure the empirical
  excursion distribution first, then set the arm threshold at ≤ 50th percentile of
  winners. A trail that never arms is an untested trail.
- **Prevention:** Any trail mode with an arm threshold must be validated by logging
  "trail armed" events. If the arm rate is < 10% of winners, the threshold is mis-set.
  This check is now part of the exit_lab report.
- **Which Mind Found It:** Profit Engine (1% WR revealed the feature was never
  reaching active state)
- **Affected Files:** backtest/engine.py, backtest/trend.py (giveback_arm parameter)
- **Status:** Threshold needs recalibration; arm-rate logging needed

---

## BUG-021 — Slippage units: mintick confusion causes 40× understatement
- **Date Found:** 2026-07-31
- **Severity:** Critical (corrupts all cost modelling)
- **Symptom:** Deep backtest run 1 used slippage=0.005 and reported wildly
  optimistic returns (+8,627% Aggressive). Run 3 with corrected slippage returned
  results that match TradingView Pine validation.
- **Root Cause:** XAUUSD mintick = 0.001. Slippage in the Python engine is in
  POINTS (price units), not ticks. Setting slippage=0.005 means 0.005 points =
  5 ticks, not the intended ~200 ticks / 0.20 points. The correct value is
  slippage=0.20 (200 ticks at 0.001 each). Using slippage=0.005 understates
  transaction costs by a factor of 40×.
- **Fix:** For XAUUSD: slippage=0.20 (0.20 points per side). Always cross-check
  against Pine: Pine slippage is in TICKS (slippage=200 ticks × mintick=0.001 =
  0.20 points). The two must agree before a result is recorded.
- **Prevention:** Any new instrument's slippage setting must include a unit comment:
  `slippage=0.20  # XAUUSD: 200 ticks × $0.001/tick = $0.20/side`. Verify against
  the TradingView Pine slippage for the same instrument before first run.
- **Which Mind Found It:** Microstructure Predator (TradingView cross-validation
  exposed the gap)
- **Affected Files:** backtest/trend.py, all backtest/*.py scripts
- **Status:** Fixed in run 3 (the definitive validation); all prior runs at 0.005 are
  labelled "OPTIMISTIC — slippage 40× too low"

---

## BUG-022 — Edit symmetry: single-anchor edit hits one directional block only
- **Date Found:** 2026-07-31
- **Severity:** Medium (silent asymmetry between long and short sides)
- **Symptom:** A parameter change tested on long side fails to apply on short side;
  or short-side behaviour changes without the long side changing, because the edit
  anchor landed in only one directional branch.
- **Root Cause:** Pine strategies have separate long and short logic blocks. When
  editing a shared parameter (e.g. trail multiplier, stop distance), it is easy to
  edit one occurrence and miss the symmetric one in the other directional branch.
  The code compiles without error; the strategy runs with asymmetric behaviour.
- **Fix:** Whenever editing any per-trade variable, enumerate every place it appears
  in BOTH the long AND the short branch and update all occurrences. Use grep/search
  to find all instances of the variable name in the file before declaring the edit done.
- **Prevention:** CODE_DELIVERY_PROTOCOL phase 3 now includes: for every variable
  changed, grep the file for all occurrences and confirm the count of edits matches.
  Pine variables that differ by direction are named `longX` / `shortX` explicitly to
  make asymmetry visible.
- **Which Mind Found It:** Microstructure Predator (trailMultEE typo in
  gold_trend_trailing.pine was in the long block only — short block had a different
  but silent error)
- **Affected Files:** strategies/gold_trend_trailing.pine (trailMultEE vs trailMultE)
- **Status:** Fixed — trailMultEE corrected in both directional branches (2026-08-02)

---

## BUG-023 — Wrong null: random arm skips the strategy's filter set, making the null too easy to beat
- **Date Found:** 2026-07-31
- **Severity:** Critical (invalidates all prior stress-test results that used a naive null)
- **Symptom:** An early random-entry null showed the random strategy as profitable
  (PF > 1.0), which made it impossible to use as a baseline — a random strategy
  should not be systematically profitable. The real issue: the null skipped the regime
  filter, SMA filter, and cooldown that the real strategy applies, giving it access to
  more and different trades.
- **Root Cause:** The random null used coin-flip entry on every bar with the same
  trailing exit but WITHOUT the regime/trend/SMA gates. So the null and the strategy
  were trading DIFFERENT populations of bars. The null's PF reflected the properties
  of unfiltered bars, not a like-for-like test of entry skill.
- **Fix:** The random null must pass through IDENTICAL filters as the strategy being
  tested — same regime gate, same SMA gate, same cooldown, same position sizing.
  The ONLY difference between the null and the real strategy is: the null's entry
  direction is coin-flip, the real strategy's direction is signal-derived. Everything else
  is held constant. Now enforced in backtest/stress_test.py.
- **Prevention:** Null construction rule: the null differs from the strategy in exactly
  ONE thing. State that one thing explicitly in the stress test report. Any null that
  differs in more than one dimension is not a valid null.
- **Which Mind Found It:** Profit Engine (DSR calculation exposed the sample mismatch
  when the null's trade count differed substantially from the strategy's trade count)
- **Affected Files:** backtest/stress_test.py
- **Status:** Fixed in stress_test.py — null now passes through full filter stack

---

## Cross-cutting lessons (read these even if skimming)
1. **An entry gate that never fires is worse than a missing gate** —
   it looks like selectivity while being a dead switch. Truth-table
   every AND/OR stack (BUG-006, BUG-007).
2. **Ask WHEN a variable updates relative to the event it describes**
   — confirmation lag killed two different signal paths (BUG-008).
3. **Stops reference the actual adverse extreme, never the level that
   was broken/swept** (BUG-005).
4. **Clamp, don't reject, when a distance is merely large** (BUG-009).
5. **Rolling/recalculated references must be frozen when comparing
   across bars** (BUG-010).
6. **"Labels but no trades" = execution rejection, not signal logic**
   — check margin/qty first, not the entry conditions (BUG-012).
7. **If the user supplies source, port it -- do not reimplement it.**
   Three consecutive rejections of the same visual meant the approach
   was wrong, not the execution (BUG-013).
8. **A suspiciously LOW trade count is an execution symptom, not
   selectivity.** BUG-012 struck twice now. Every engine displays
   Signals / Filled / Fill rate so rejection can never masquerade as a
   high-quality filter again (BUG-012, BUG-016).
9. **Every strategy.exit that owns part of a position needs its own
   stop** -- siblings do not share one (BUG-014).
10. **Level-based TP only works when levels are farther away than the stop.**
    Measure median(level_distance)/stop_distance before committing to
    any level-as-target exit structure (BUG-017).
11. **A trail that never arms is an untested trail.** Calibrate the
    arm threshold against the empirical excursion distribution; verify
    arm-rate ≥ 10% of winners before declaring the mode live (BUG-020).
12. **State the slippage in price points with a unit comment.** For XAUUSD,
    slippage=0.20 = 200 ticks; slippage=0.005 is 40× too low (BUG-021).
13. **The null differs from the strategy in exactly ONE thing.** If the null
    trades a different bar population than the strategy, it is not a null —
    it is a different strategy (BUG-023).
