# RESEARCH PROTOCOL — Operating Method for All Strategy Research
# Adopted 2026-08-02. Governs every backtest, audit, and archive sweep
# in this repository going forward.

---

## 0. THE PRIMARY RULE

A number that agrees with expectation gets MORE scrutiny, not less.
The failure mode is not malice — it is motivated reading of ambiguous
output. Every result that looks good triggers an extra verification pass.

---

## 1. FIVE PRE-BELIEF CHECKS

Before treating any backtest number as real:

1. **Reproduce a known result.** Run the same config on a window whose
   answer you already know. If you get a different number, stop — something
   in the pipeline changed and the new result is not comparable.
2. **Check units.** State the unit of every parameter explicitly in a comment.
   Slippage, stop distance, ATR multiplier: all three have caught errors here.
   (BUG-021: slippage=0.005 is 40× too low for XAUUSD.)
3. **Check the tails.** Look at the worst drawdown, the worst consecutive
   run, the max single loss. If any tail is implausible, the exit logic or
   fill model has a bug.
4. **Check target÷stop in ATR.** Before any engine is built, compute the
   median distance from entry to the intended target, divided by the stop
   distance. If T/S < 1.0, the strategy loses before any trade fires (BUG-017).
5. **Sanity-check the shape.** Plot the equity curve. A curve that rises
   monotonically without any drawdown is not a result — it is a bug.
   A curve that drops hard in one window and recovers identically in another
   is fitting that window.

---

## 2. RESULT REPORTING STANDARD

Every result recorded in RESULTS_LEDGER.md must include:
- Instrument and timeframe
- Start date and end date (or bar count)
- Trade count (`n`)
- Win rate
- Profit factor
- Net return
- Maximum drawdown
- Slippage used (in price points, with a unit comment)
- Whether the window is in-sample or out-of-sample

A PF with no trade count and no date range is not a result. It is a claim.
Claims are not entered in the ledger.

---

## 3. VALIDATION BATTERY (MANDATORY BEFORE SHIPPING)

A result is not valid until it clears all three gates:

**Gate 1 — Random null at matched sample size.**
Build a coin-flip entry through the SAME filter stack (same regime gate,
same SMA gate, same cooldown, same sizing). Only the entry DIRECTION is
random. Run ≥ 300 trials. The strategy must beat the null's 95th percentile
PF. If n < 100, the noise band is too wide to see through — the strategy is
untestable at this sample size. (BUG-023: the null must use identical filters.)

**Gate 2 — Deflated Sharpe Ratio.**
Compute DSR accounting for the actual number of configurations tried
(not 1, not the number of parameters — the number of distinct configs
evaluated, including informal "let me try X" passes). DSR ≥ 0.95 required.
At 17 trials and n=521, a result needs SR/trade ≥ 0.179, which at 44% WR
is roughly PF 1.45. PF between 1.0 and 1.4 on this sample size is
indistinguishable from search noise.

**Gate 3 — Buy and hold.**
Compare net return to buying and holding the instrument over the identical
window. A strategy that underperforms buy-and-hold while carrying execution
risk and round-trip costs has not demonstrated an edge.

---

## 4. BUG CLASSES TO CHECK EVERY SESSION

Before writing or delivering any code, mentally run through these:

| Class | Check |
|---|---|
| BUG-004 | All `ta.*` calls are unconditional (never inside if/for) |
| BUG-012 | Margin is 100% (not default 0%); display Signals/Filled/Fill rate |
| BUG-013 | If user supplied source, PORT it — do not reimplement |
| BUG-014 | Every strategy.exit that owns part of a position has its own stop |
| BUG-017 | median(target_distance)/stop_distance > 1.5 before building level-TP engine |
| BUG-019 | Excursion updated AFTER stop resolves, not before |
| BUG-020 | Trail arm threshold ≤ 50th percentile of winner excursion distribution |
| BUG-021 | Slippage in price points with unit comment; XAUUSD = 0.20pt |
| BUG-022 | Edit both long AND short branches; grep for all occurrences |
| BUG-023 | Null differs from strategy in exactly ONE thing (entry direction) |

Full registry: `trader_playbooks/bugs/BUG_REGISTRY.md`

---

## 5. ARCHIVE SWEEP CLASSIFICATION

Every source gets one of these five statuses:

| Status | Meaning |
|---|---|
| FULLY TRACED | Source → extracted to playbook → built into code → measured in backtest |
| BUILT-NEVER-MEASURED | Code exists, no backtest row |
| EXTRACTED-NEVER-BUILT | In the playbook, not in any code |
| ARCHIVED-NEVER-EXTRACTED | File exists in sources/, content not yet distilled |
| DELIBERATELY-EXCLUDED | Read, reviewed, and recorded as not worth building |

"Eight exit mechanics extracted and implemented in zero engines" is a FINDING,
not a backlog item. Each one requires a deliberate decision: build it, or
record why it was not built. The finding as of 2026-08-02:

| # | Mechanic | Source | Status |
|---|---|---|---|
| 1 | Doji-tightens-stop | Hougaard §8 | EXTRACTED-NEVER-BUILT |
| 2 | Volume-spike-near-S/R tighten/exit | Hougaard §8 | EXTRACTED-NEVER-BUILT |
| 3 | Scale-out 1/3@~20pts / 1/3@next-high-BE / 1/3 runner | Hougaard §8 (Mark Douglas method) | EXTRACTED-NEVER-BUILT |
| 4 | Scale-in only when position 1 can go to breakeven | Hougaard §8 | EXTRACTED-NEVER-BUILT |
| 5 | Full exit at previous POC (reverts ~70% of time) | Valentini exit mechanics | EXTRACTED-NEVER-BUILT |
| 6 | Failed-auction-at-target while in profit → secure | Valentini exit mechanics | EXTRACTED-NEVER-BUILT |
| 7 | 3-5-7 scaled stop (exit 1/3 @ -3%, -5%, -7%) | Roppel risk architecture | EXTRACTED-NEVER-BUILT |
| 8 | Cushion protocol (no cushion = tight; cushion = play) | Roppel risk architecture | EXTRACTED-NEVER-BUILT |

None of these eight have been tested. The champion (`gold_trend_strategy.pine`)
uses a chandelier ATR trail only. The exit IS the system — these eight are
candidates to test as modifications to the champion's exit layer.

---

## 6. THE EXIT IS THE EDGE

The champion's own "every bar the gate allows" test (no trigger, OOS PF 1.914)
confirms: the entry has no measurable edge. The Chandelier ATR trail is where
the money is made. Before testing any new entry rule, test whether modifying the
exit improves on the champion's OOS PF 1.588 first — the bar is already high.

Order of research priority:
1. Out-of-sample test of any new exit modification on the 2023–2026 hold-out
2. Voice score ≥ 6 filter transfer from 15m predecessor to 30m champion (EV-3)
3. Aggressive/Maximum risk profiles re-run at 0.20pt slippage (EV-1)
4. slope_both=True DSR test (EV-2)
5. New entry mechanisms — only after #1–4 are complete

---

## 7. NEVER OPTIMIZE PROFIT FACTOR ALONE

Report PF AND return. A strategy with PF 1.6 and −5% return is worse than
PF 1.4 and +60% return. The champion scores PF 1.588 / +60.9% OOS.

---

## 8. SECURITY CONSTRAINT (NON-NEGOTIABLE)

Never let a live credential enter git history.
- Secrets go in a gitignored, mode-600 `.env` — never on argv, never logged.
- API keys, broker tokens, account numbers: `.env` only.
- Before every commit: `git diff --staged | grep -i "key\|token\|secret\|password"`.
  If anything matches, abort and move the secret to `.env`.

---

## 9. PORT, DON'T REIMPLEMENT (BUG-013)

When the user supplies working source code, the deliverable is a port of
THAT code. Log every deviation as a numbered delta with a reason. A "this
looks like it should be equivalent" rewrite is not a port — it is a new
implementation that has not been validated against the original.

Deviations allowed only where the host (Pine v6) strictly requires them.

---

## 10. CAPTURE, OR IT DID NOT HAPPEN

Every session that produces analysis, backtest results, or user trade
feedback must update before ending:
- `RESULTS_LEDGER.md` — every new backtest row
- `BELIEF_REGISTER.md` — any belief contradicted or reinforced by new data
- `PLAYBOOK.md` — any strategy update or retirement
- `MEMORY.md` — session findings and next action

Every code bug found: `trader_playbooks/bugs/BUG_REGISTRY.md`
Every validated pattern: `trader_playbooks/skills/SKILL_REGISTRY.md`

If it isn't captured, it wasn't learned.
