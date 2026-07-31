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

---

## BUG-017 — A "next key level" target that is closer than the noise

**Found:** 2026-07-31, by a live TradingView run contradicting research.
**Severity:** destroys the system it is added to.

**Symptom:** PF 0.702 and −2.99% live, against PF 1.385 and +3.54% from
the research engine on the same window and settings. Win rate rose to
56.92% while the profit factor fell below 1 — the signature of a target
that is too close to a stop that is too far.

**Root cause:** the key-level module draws 36 levels, including every
range's midpoint. On XAUUSD 15m the median distance from price to the next
level ahead is **0.46 ATR**. The trailing stop is **6 ATR** behind. Taking
75% of the position off at the next level therefore risks 6 to make 0.46.
No hit rate rescues that structure.

The research engine missed it because `backtest/levels.py` modelled only
18 of the 36 levels, so its median target sat 0.70 ATR out — still far too
close, but in a different enough regime that the shorts-only restriction
masked the damage.

**Prevention — check before shipping any level- or grid-based target:**
1. Compute the median distance from entry to target, IN ATR.
2. Compare it to the stop distance in ATR. If target/stop < 1.0, the
   structure is losing before a single trade is placed. State the ratio
   in the ledger row.
3. When a Pine module exports the levels, count them. Do not assume the
   research port has the same set — `array.size(klPrices)` versus
   `len(LEVEL_NAMES)` is a two-second check that would have caught this.

**Related:** the same arithmetic is why every pre-2026-07 engine in this
repo lost — fixed 1R/2R targets against wide stops. This is that mistake
returning in a new costume.

---

## BUG-018 — Backtest filled every stop exactly at the stop price

**Found:** 2026-07-31, while cross-checking a 30m TradingView run.
**Severity:** understates the worst loss by ~2x; flatters PF.

**Symptom:** Python's largest loss on the window was 124.16 where
TradingView reported 240.77, while profit factor, largest win and average
hold all agreed closely.

**Root cause:** `trend.py` computed the stop fill as `stop - dir*slippage`
unconditionally. A bar that OPENS beyond the stop fills at the open, not
at the stop. Gold gaps over weekends and around data releases, so this is
not an edge case.

**Fix:** `gap_fill=True` takes `min(stop, open)` for longs and
`max(stop, open)` for shorts. Worst loss becomes 241.22 against
TradingView's 240.77.

**Prevention:** when an engine and a platform agree on profit factor but
disagree on the WORST trade, suspect the fill model, not the logic. Compare
the tails, not just the aggregates — an average can agree while the model
of a bad day is completely wrong.
