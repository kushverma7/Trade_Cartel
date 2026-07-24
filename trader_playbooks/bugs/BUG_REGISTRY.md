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
