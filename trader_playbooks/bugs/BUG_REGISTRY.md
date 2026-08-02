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

---

## BUG-019 — Intrabar lookahead: excursion updated before the stop check

**Found:** 2026-07-31, by `exit_lab.py` failing to reproduce a known result.
**Severity:** halves reported drawdown; invalidates every run made with it.

**Symptom:** the new exit engine reported PF 1.183 at 45.2% drawdown where
the established configuration was PF 1.635 at 17.01%. The numbers were not
merely different, they were incompatible.

**Root cause:** the per-bar block updated `pos["best"]` from bar *i*'s own
high BEFORE resolving the stop on bar *i*. A trailing stop anchored to
`best` therefore rose using information from inside the bar it was then
tested against — the stop got to see the bar's high before deciding whether
the bar's low took it out.

**Fix:** `pos["best"]` is updated at the END of the bar block, after the
stop and both targets are resolved. The ordering is now load-bearing and
carries a comment saying so.

**Prevention:** in any bar-loop engine, write the order of operations down
before coding it: (1) move stop using data through bar i-1, (2) resolve
bar i, (3) update state with bar i. Any state a stop depends on must be
one bar stale. If a new engine cannot reproduce an old engine's known
result, do not tune it — find the ordering difference first.

---

## BUG-020 — Trailing mode that arms at zero excursion

**Found:** 2026-07-31, in the `giveback` trailing mode.
**Severity:** silently produces a 1% win rate; looks like a bad idea
rather than a bug.

**Symptom:** the give-back-a-fraction-of-the-run trail scored a 1% win rate
over 2,307 trades. The obvious reading — "this mode simply does not work" —
was wrong.

**Root cause:** excursion is zero at entry, so `best - run * frac` evaluates
to the entry price on the trade's second bar. The stop snapped to breakeven
immediately and every trade was scratched by normal noise. The mode never
actually ran.

**Fix:** `giveback_arm` — the trail does not engage until the trade has run
at least N ATR from entry. Before that the original stop stands.

**Prevention:** any trail defined as a function of profit must state what it
does at zero profit. Evaluate the formula at entry by hand before running
it. A near-zero or near-100% win rate is a bug signature, not a result —
investigate it before recording it as a finding.

---

## BUG-021 — Pine `slippage` is in TICKS, not points

**Found:** 2026-08-01, during cost-stress testing.
**Severity:** flattered every backtest that used the wrong value; ~40x
under-modelled cost.

**Symptom:** a research engine charging 0.05 points per side agreed with a
TradingView run declaring `slippage = 5`. The agreement was a coincidence
of two different mistakes.

**Root cause:** `strategy(slippage = N)` counts N **ticks**, not points.
XAUUSD on OANDA quotes three decimals, so mintick is 0.001 and `slippage=5`
models 0.005 points — roughly a fortieth of a realistic retail gold fill.
A correct 0.20 point fill is `slippage = 200`.

**Fix:** `slippage = 200` in the strategy declaration, with the arithmetic
written into the code comment so it cannot be silently reverted. The
corrected run returned +1,591.7% against +3,533.9% at the wrong value.

**Prevention:** before trusting any cost figure, compute
`slippage_input * syminfo.mintick` and confirm it is the intended number of
POINTS. Do this per symbol — mintick differs. Any headline result produced
before this check is provisional.

---

## BUG-022 — Asymmetric edit: one direction updated, the other left stale

**Found:** 2026-07-31, adding TP1/TP2 to the entry logic.
**Severity:** shorts trade against a previous configuration's levels.

**Symptom:** the long entry branch assigned the new TP1/TP2 state; the short
branch did not, because the edit anchor matched only once after a prior
change had already altered the short block's text.

**Root cause:** paired long/short blocks are near-identical, so a
single-anchor edit lands on one of them and reports success. Nothing in the
compile or the run flags the other side.

**Fix:** both branches assign every per-trade state variable, and a symmetry
check now enumerates those variables across both directions.

**Prevention:** after any edit to directional trade state, list every
per-trade variable and confirm it is assigned in BOTH branches. Never trust
a successful single edit on symmetric code. This is the class of bug that
BUG-011 (inverted SuperTrend conditions) also belongs to.

---

## BUG-023 — A null hypothesis that skipped the filters it was testing

**Found:** 2026-08-01, on re-reading the significance test.
**Severity:** methodological; invalidated every earlier significance claim.

**Symptom:** the strategy sat far outside the random-entry distribution and
was described as clearly significant.

**Root cause:** the `random_p` arm randomised entries but did NOT apply the
regime, slope and cooldown filters the real strategy uses. It compared
"entry logic plus filters plus exit" against "nothing", so it measured the
whole system against noise rather than measuring the ENTRY against noise.
The random arm still returned +524% on its own, which was the clue.

**Fix:** the null randomises entry TIMING while applying the identical
filter set. Under the corrected null the champion sits at the 93.3rd
percentile — inside noise. That is now stated in the ledger rather than
buried.

**Prevention:** a null must differ from the strategy in exactly ONE
respect — the thing being tested. Write down what the null holds constant
before running it. If the random arm is itself profitable, the null is
wrong or the edge is not where you think it is.

---

## BUG-024 — Yearly high/low leak future data into the mandatory key-levels module

**Found:** 2026-08-02, by auditing an uploaded third-party code review
(`gold_scalping_strategy_blueprint.pdf`) against
`trader_playbooks/skills/key_levels_module.pine`.
**Severity:** silently optimistic backtests in every strategy that trades a
yearly level. No effect on live/forward trading.

**Symptom:** none visible. Backtests using the yearly range simply look
better than they should.

**Root cause.** The module makes 20 `request.security()` calls, all with
`lookahead=barmerge.lookahead_on`. That is NOT wrong by itself — paired with
a `[1]` offset it is the standard non-repainting idiom, and 10 of the calls
do exactly that. Six more request `open`, which is known at the start of the
period and so is also safe.

Four calls are neither:

```
L83  cdailyh_open = request.security(..., 'D',   high,          lookahead_on)
L84  cdailyl_open = request.security(..., 'D',   low,           lookahead_on)
L102 [yearlyh_time, yearlyh_open] = request.security(..., '12M', [time, high], lookahead_on)
L103 [yearlyl_time, yearlyl_open] = request.security(..., '12M', [time, low],  lookahead_on)
```

A period's high and low are not known until the period closes. With
`lookahead_on` and no `[1]`, a historical bar receives the COMPLETED period's
extreme — future information.

Note the asymmetry that identifies it as a slip rather than a design: every
other timeframe (D, W, M, 3M, 240) uses `[time[1], high[1]]` for its
high/low. Only the yearly pair omits the offset.

**Blast radius.** `cdailyh_open`/`cdailyl_open` are drawn on the chart but
never reach `f_klPush`, so they do not enter `klPrices[]` and cannot affect
trade logic. The yearly pair does reach it, at lines 375–377, along with a
midpoint derived from both:

```
f_klPush(is_yearlyrange_enabled, yearlyh_open, cyhtext)
f_klPush(is_yearlyrange_enabled, yearlyl_open, cyltext)
f_klPush(is_yearly_mid, (yearlyh_open + yearlyl_open) / 2, cymtext)
```

Three exported levels — yearly high, yearly low, yearly mid — carry future
information into any strategy that reads `klPrices[]`. Eight repo strategies
embed the module: `gold_trend_trailing`, `key_to_key_strategy`,
`trendline_key_level_strategy`, `key_levels_spaceman_edition`,
`multivoice_confluence_engine`, `amdm_confluence_strategy`,
`omnibus_four_model_engine`, `confluence_sniper_strategy`.

**`strategies/gold_trend_strategy.pine` — the validated champion — does NOT
embed the module.** Its PF 1.583 / +1,591.7% result is unaffected.

**Inherited, not introduced.** Verified 2026-08-02 against the user-supplied
original (`indicators/key_levels_spaceman.pine`, and the copy inside
`sources/all_indicators_dump.txt`): lines 48-49 of the original are identical
to lines 102-103 of the module. The port did not cause this. The module's
four logged port deltas are all unrelated and all compliant.

**Fix — and why the obvious one is wrong.** The tempting change is to bring
the yearly pair into line with every other timeframe:

```
[yearlyh_time, yearlyh_open] = request.security(..., '12M', [time[1], high[1]], lookahead_on)
```

**Do not do this.** Every other timeframe deliberately shows the PREVIOUS
period's extreme — that is what makes them PDH/PDL, previous-week high/low
and so on, which is the whole point of those levels. The yearly pair shows
the CURRENT year's running range, which is a different level and is what the
user sees on the indicator. Rewriting it would silently replace a level with
a different level and change the drawing, violating the standing "displays
the levels as it is in the indicator" directive.

The leak is not in the drawing — live and forward trading have no future to
look at. It exists only when a BACKTEST reads those values through
`klPrices[]`. So the fix belongs at the export, not at the request:

- Preferred: gate lines 375-377 behind a `kl_export_yearly` input defaulting
  to **false**, so the yearly high, low and mid still draw but never enter
  `klPrices[]`. One new input, three guarded lines, drawing untouched.
- Or, in any strategy that consumes `klPrices[]`, skip entries whose name
  matches the yearly set.

Either way, log it as port delta 5 with this reason.

Also: do NOT strip `lookahead_on` from the module wholesale — the uploaded
review recommends exactly that, and it would introduce repainting on the ten
calls that are currently correct.

**Prevention:** `lookahead_on` is safe only when the requested expression is
already historical (`[1]`-offset) or is knowable at period start (`open`).
Any `high`, `low`, or `close` requested for the CURRENT period with
`lookahead_on` is a future leak. Grep for
`request.security` and classify each call before trusting a backtest; the
check takes a minute and is now part of the pre-flight.

---

## BUG-025 — Victor Aimstar: long and short conditions are the SAME expression

**Found:** 2026-08-02, verifying an uploaded audit against
`indicators/victor_aimstar_past_strategy_v1.pine`.
**Severity:** with QQE Mod selected, the strategy is incoherent — longs and
shorts fire together.

**Symptom:** none at compile. The selector simply behaves nonsensically when
one of its eight options is chosen.

**Root cause.** The leading-indicator selector assigns a long condition and a
short condition per branch. Every other branch pairs opposites
(`uprf`/`downrf`, `rqkuptrend`/`rqkdowntrend`, `rd_long`/`rd_short`). The QQE
branch does not:

```
else if leadingindicator == 'QQE Mod'
    leadinglongcond  := isqqeabove
    leadingshortcond := isqqeabove      // should be isqqebelow
```

`isqqebelow` is computed correctly three ways higher in the file (lines
3906/3909/3912) and then never used in this branch. So the short leg fires on
bullish QQE, simultaneously with the long leg.

The uploaded review called this "QQE Mod short condition bug —
`leadingshortcond := isqqeabove` should be `isqqebelow`", which is right, but
understates it: this is not an inverted signal, it is the *same* signal on
both sides, so the two legs cannot disagree at all.

**Fix:** `leadingshortcond := isqqebelow`. One token.

**Prevention:** any selector or state machine that assigns paired
directional conditions must be checked branch by branch, with the pairs
listed side by side. A single branch out of eight is invisible on a read-through.
This is the BUG-022 symmetry class applied to a dispatch table rather than to
an edit.

---

## BUG-026 — BigBeluga SMC: integer division makes the ATR divisor zero

**Found:** 2026-08-02, same audit pass.
**Severity:** silently disables the volume/ATR sizing whenever the user raises
one input above its default.

**Root cause.** `indicators/bigbeluga_smart_money_concepts.pine:304`:

```
float atr = (ta.atr(200) / (5/len))
```

with `len = input.int(5, "", inline="atr", group=VBG, minval=1)`.

Both operands of `5/len` are integers, so Pine performs integer division:

| len | 5/len | result |
|---|---|---|
| 1 | 5 | atr/5 |
| 2 | 2 | atr/2 — should be atr/2.5 |
| 3 | 1 | atr/1 — should be atr/1.67, 40% wrong |
| 5 | 1 | atr/1 — correct |
| **≥6** | **0** | **division by zero** |

The default (5) happens to work, which is why it has never been noticed. Any
value of 6 or above produces a zero divisor; 2 and 3 produce quietly wrong
scaling.

**Fix:** force float arithmetic — `ta.atr(200) * len / 5.0`, matching the
uploaded review's correction, or `(5.0/len)` at minimum.

**Prevention:** in Pine, `int / int` is integer division. Any division where
both operands could be integers and the result is meant to be fractional must
carry an explicit `.0`. Grep new code for `/ (` followed by an int input
before shipping.

---

## BUG-027 — Quarter-grid proximity "filter" is a constant, and its target is 15x too close

**Found:** 2026-08-02, testing `gold_scalping_strategy_blueprint.pdf`'s
Quarter Theory module against `data/xauusd_15m.csv.gz`.
**Severity:** the module contributes nothing as a filter and loses money as a
target. Both halves fail.

**The filter half.** The blueprint proposes:

```
bool nearWholeNumber = distToWhole < atr * 0.3
bool nearQuarter     = distToMajorQuarter < atr * 0.2
```

`distToWhole` cannot exceed 0.50 by construction — it is the distance to the
nearest integer. So whenever `atr * 0.3 > 0.5`, i.e. ATR > $1.67, the
condition is unconditionally true.

Measured on this repo's own XAUUSD 15m history (median ATR $2.58, price range
$1,454–$5,586):

| gate | unconditionally true on |
|---|---|
| `nearWholeNumber` (ATR×0.3 > 0.50) | **79.8% of bars** |
| `nearQuarter` (ATR×0.2 > 0.25) | **93.6% of bars** |

It is not a filter. On four bars in five it is the literal constant `true`,
and it degrades to a real filter only in the quietest 20% of the sample —
precisely the regime a scalper should be sitting out. BUG-006 class
(always-true gate), but arrived at through a units mismatch rather than a
logic slip: a 0.25 grid was designed for an instrument priced in single
dollars and applied to one that moves $2.58 per 15 minutes.

**The target half.** The blueprint sets "Target 1: next quarter level (1:1
R/R)" against a "Stop: 1.5x ATR". Applying BUG-017's mandatory pre-ship
check:

```
median target distance / stop distance = 0.25 / (1.5 x 2.58) = 0.065
```

BUG-017 requires this ratio to exceed 1.0 or the structure loses before a
single trade is placed. The key-level build that produced live PF 0.702 and
−2.99% scored **0.077**. This scores **0.065** — 15% worse than the
configuration this project already measured as a failure.

The "1:1 R/R" label attached to it is simply false: a $0.25 target against a
$3.87 stop is 1:15.5 against.

**Prevention:** any price-grid rule must be checked against the instrument's
ATR in the same units before it is coded, not after. Two one-line checks:
(1) can the gate's threshold exceed the metric's maximum possible value? (2)
what is target/stop in ATR? Both were available before writing any Pine.

**Related:** BUG-017, and the standing finding that level- and grid-based
targets fail structurally because their distance is set by where a line
happens to sit rather than by what the trade needs.
