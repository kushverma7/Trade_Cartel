# Levels & Pivots — complete inventory and strategy-feasibility assessment
**2026-08-02.** Final sweep before building a strategy from what exists.

## 1. What exists

### Price levels — three engines, three different level sets

| engine | count | notes |
|---|---|---|
| `backtest/levels.py` sparse | **18** | the default; what most research ran on |
| `backtest/levels.py` dense=True | **33** | added after BUG-017 to close the gap |
| `skills/key_levels_module.pine` | **36** | what the chart actually draws and exports |

Still mismatched, three ways: 18 vs 33 vs 36. BUG-017's prevention step
("count them") was written for exactly this and has not been completed.

`levels.py` sparse set: DO, PDH, PDL, WO, PWH, PWL, MO, PMH, PML, H4O, P4HH,
P4HL, MONH, MONL, LONH, LONL, NYH, NYL — daily/weekly/monthly opens, previous
period high/lows, 4H, Monday range, London and NY session ranges.

### Swing pivots — well covered
`ta.pivothigh` / `ta.pivotlow` appear in **32 Pine files**. Structural pivots
(BOS/CHoCH, swing counting, Wyckoff spring/upthrust) are thoroughly built.

### Classic floor-trader pivots — DO NOT EXIST
Searched for the defining formula `(H+L+C)/3` across every `.pine` and `.py`.
Three hits, all VWAP typical-price, none a pivot. **There is no PP/R1/R2/R3/
S1/S2/S3, no Camarilla, no Woodie, no Fibonacci pivot anywhere in this repo.**

This is a genuine coverage gap. Whether it is worth filling is answered in §3.

### Knowledge layer
Level-relevant playbooks: `jeafx_key_levels` (the level set itself),
`quarterly_theory` (Daye, TIME quarters), `yotov_quarters_theory` (PRICE
grid), `trader_dale_orderflow` (POC/VAH/VAL/HVN/LVN), `pbd_logic` (value
area), `alchemist_smc_concepts` and `pure_pa_smc` (order blocks, FVG).

**Volume-profile levels — POC, VAH, VAL — exist in the playbooks and in
several Pine engines but NOT in `levels.py`.** The research engine cannot
currently test the level family the knowledge layer talks about most.

### Strategies already built on levels — 7, of which 6 are unmeasured

| strategy | ledger row |
|---|---|
| `amdm_confluence_strategy` | none |
| `confluence_sniper_strategy` | none |
| `gold_confluence_engine` | none |
| `key_levels_spaceman_edition` | none |
| `key_to_key_strategy` | none |
| `multivoice_confluence_engine` | **1** |
| `trendline_key_level_strategy` | none |

Six built, never measured. That is the largest single block of unmeasured work
in the repo.

## 2. What is broken, and it is all now known

| id | defect | state |
|---|---|---|
| BUG-017 | level TARGETS are closer than the noise (0.077 target/stop) | measured, live PF 0.702 |
| BUG-024 | yearly H/L leak future data into `klPrices[]` | **fixed** (export gated) |
| BUG-027 | quarter-grid filter is a constant; target/stop 0.065 | measured, do not build |
| BUG-028 | `levels.py` CYH/CYL means current year, computes previous | **open** |
| — | 18 vs 33 vs 36 level-count mismatch | **open** |
| — | no volume-profile levels in the research engine | **open** |

## 3. The assessment: can a strategy be built from this?

**Yes — but not the strategy this repo keeps trying to build.**

Three independent measurements now converge on the same conclusion:

1. **BUG-017**: level targets on XAUUSD gave median target/stop 0.077 → live
   PF 0.702.
2. **BUG-027**: the uploaded quarter grid gave 0.065, and its proximity filter
   was unconditionally true on 79.8% of bars.
3. **The exponent gap** (`backtest/mae_mfe.py`, logged in BELIEF_REGISTER):
   MAE diffuses at 0.493 against a random walk's 0.500. **Entry geometry is a
   coin flip.** The edge is +0.065 of exponent and it accrues to HOLD TIME.

Read together these say something precise about what levels can do:

- **As targets: dead.** Measured twice, on two instruments, at two grid
  spacings. A level's distance is set by where the line sits, not by what the
  trade needs. Do not build this a third time.
- **As entries: near-worthless.** The MAE exponent says no entry, level-based
  or otherwise, materially changes the adverse-side geometry. Every entry
  family tested here has confirmed it.
- **As a reason to KEEP HOLDING: untested, and the only use consistent with
  the evidence.** The edge lives in hold time. A level is information about
  where price is likely to pause or accelerate. Used to EXTEND a hold — "do
  not trail tighter while price is between PDH and PWH", "do not take partial
  profit into an untested level" — it works with the exponent gap instead of
  against it.

**That inverts how all seven existing level strategies use levels.** Every one
of them uses levels to decide when to ENTER or when to TAKE PROFIT. Nothing in
this repo has ever tested a level as a hold-extender.

## 4. What is needed before building — the honest list

Ready now:
- 36 drawn levels, exported and now backtest-safe (BUG-024 gated)
- 33 dense research levels, non-lookahead by construction
- a validated champion to attach an exit modifier to (`gold_trend_strategy`,
  PF 1.583 / +1,591.7% / 33.63% DD, 2,370 orders)
- `exit_lab.py` with six trailing modes to modify
- `mae_mfe.py` to measure whether a hold-extender actually extends the hold

Must be fixed first:
1. **BUG-028** — decide whether CYH/CYL is the current or previous year and
   make both engines agree. Otherwise research and live measure different
   things, again.
2. **Reconcile 18/33/36.** Name-by-name, not count-by-count.
3. **Add volume-profile levels (POC/VAH/VAL) to `levels.py`** if the AMDM /
   Trader Dale layer is to be tested at all. It cannot be, today.

Not needed:
4. **Floor-trader pivots.** They are absent, and they are another price grid
   whose spacing is set by yesterday's range rather than by the trade. They
   would fail the BUG-017 gate for the same reason quarters did. Build them
   only as a hold-extender or a regime marker, never as a target — and only
   after 1-3 are done.

## 5. The one strategy worth building from all of this

**Champion + level-aware hold extension.** Take `gold_trend_strategy.pine`
unchanged. Add one rule: while an untested level lies ahead within N ATR in
the trade's direction, hold the existing trail wider (or suppress the partial).
Measure against the unmodified champion on the same window and costs.

It is falsifiable in one run, it risks nothing (the base is validated), it uses
the level set we already have, and it is the only use of levels consistent with
every measurement this project has made.
