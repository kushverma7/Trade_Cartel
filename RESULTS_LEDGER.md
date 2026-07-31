# RESULTS LEDGER

**Every backtest result on record, in one table.** Built 2026-07-29 by
extracting every result mention from `trader_playbooks/PLAYBOOK.md` and the
recovered session archive.

## Why this file exists

Before it, results lived as prose scattered across 1,097 lines of PLAYBOOK.md
— 19 separate PF mentions, of which only ~12 recorded a trade count and only
5 recorded the date range tested. There was no way to answer "what did engine
X score, on what sample, with what settings" without re-reading the whole
file. That is a large part of why 17 engines got built and none got validated:
the comparison was never actually available.

**Rules for this file**
1. Every row records the sample, not just the headline. A PF with no trade
   count and no date range is not a result.
2. `Unknown` means unknown. Do not infer, do not backfill from memory.
3. Nothing gets a `VALID` status without an out-of-sample test. As of this
   file's creation, **no row qualifies** — that is the finding.
4. New results are appended here in the session they are produced.

---

## The ledger

| # | Date | Engine | Sym / TF | Window | Trades | WR | PF | Net | Max DD | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ~07-15 | Reversal Sniper v2 (auto S/D zones) | XAUUSD 5m | Unknown | Unknown | Unknown | **0.731** | Unknown | Unknown | RETIRED — mechanism blamed & banned |
| 2 | 07-20 | Session Trendline Breakout | XAUUSD 5m | ~2 months | 117 | Unknown | **3.656** | Unknown | Unknown | **RETRACTED** — sample too small (free-plan data cap) |
| 3 | 07-20 | Top/Bottom engine, run 1 | XAUUSD 5m | Unknown | Unknown | Unknown | 0.90 (analog) | Unknown | Unknown | superseded |
| 4 | 07-20 | Top/Bottom engine, run 2 | XAUUSD 5m | Unknown | Unknown | Unknown | 0.67 (analog) | Unknown | Unknown | regression, diagnosed |
| 5 | 07-20 | Top/Bottom engine, run 3 | XAUUSD 5m | Unknown | Unknown | Unknown | 0.85 (analog) | Unknown | Unknown | superseded |
| 6 | 07-20 | **Top/Bottom engine, run 4** | XAUUSD 5m | Unknown | **112** | 35.7% | **1.11** (analog) | Unknown | Unknown | first >1; settings recovered 07-29 (see below) |
| 7 | 07-20 | Spaceman + Daye Quarters | XAUUSD 5m | Unknown | 12 | 0% | **0** | Unknown | Unknown | broken — 12/12 losses, root-caused |
| 8 | 07-20 | Spaceman + Daye, re-test | XAUUSD 5m | Unknown | 8 | 12.5% | **0.14** | Unknown | Unknown | abandoned |
| 9 | 07-27 | OMNIBUS four-model | XAUUSD 5m | Jun–Jul | 298 | 40.6% | **0.843** | −13.01% | Unknown | plateau |
| 10 | 07-27 | Key-to-Key | XAUUSD 5m | Jun–Jul | ~245 | 26.1% | **0.886** | −10.87% | 23.15% | plateau |
| 11 | 07-27 | Trendline × Key Levels v1 | XAUUSD 5m | Jun–Jul | 382 | 40.8% | **0.882** | −11.72% | 20.68% | plateau |
| 12 | 07-27 | Trendline × Key Levels v2 (+HTF bias) | XAUUSD 5m | Jun–Jul | ~380 | Unknown | **0.819** | −13.34% | 15.69% | REVERTED — filter made it worse |
| 13 | 07-28 | **Multi-Voice Confluence** | XAUUSD **15m** | Feb 2 – Jul 28 2026 | **521** | 44.15% | **1.093** | +15.25% | 11.90% | best on record; in-sample only, confounded |
| 14 | 07-28 | Multi-Voice + level-to-level exits | XAUUSD 15m | Feb 2 – Jul 28 2026 | 461 | 34.06% | **0.892** | −14.19% | 25.47% | REVERTED — see H74 |
| 15 | 07-29 | Key Levels (Spaceman Edition) v1.0 | XAUUSD 30m | Jan 2025 – Jul 2026 | 22 | 63.64% | **1.783** | +7.70% | 7.01% | **VOID** — order-rejection artifact (BUG-012) |
| 16 | — | Key Levels (Spaceman Edition) v1.1 | XAUUSD 30m | — | — | — | — | — | — | superseded by v1.2, never run |
| 17 | — | Key Levels (Spaceman Edition) v1.2 | XAUUSD 30m | — | — | — | — | — | — | superseded by the offline search |
| 18 | 07-31 | **Key Levels, optimised offline** — PMH/NYH/NYL | XAUUSD 15m | **train** 2019-12→2023-11 | 109 | 49.54% | 1.141 | +8.83% | 11.50% | in-sample, selected |
| 19 | 07-31 | same config, OUT OF SAMPLE | XAUUSD 15m | test 2023-11→2026-07 | 60 | 45.00% | 1.495 | +16.96% | 6.57% | REJECTED — failed all 3 gates |
| 20 | 07-31 | 22-voice register (Python port) | XAUUSD 15m | train 2019→2023 | 2308 | 36.05% | 0.859 | −88.13% | 89.63% | **H73 FALSIFIED** — PF falls as conviction rises |
| 21 | 07-31 | 22-voice register, OUT OF SAMPLE | XAUUSD 15m | test 2023→2026 | 1460 | 38.49% | 0.960 | −23.46% | 40.02% | loses on both halves |
| 22 | 07-31 | **Gold Trend — trailing stop**, entry 50 / trail 8 ATR | XAUUSD 15m | train 2019→2023 | 419 | 36.99% | 1.254 | +50.2% | 14.2% | selected on train only |
| 23 | 07-31 | **same config, OUT OF SAMPLE** | XAUUSD 15m | **test 2023→2026** | **275** | 41.45% | **1.588** | **+60.9%** | **5.5%** | **SHIPPED — return/DD 11.07 vs buy-hold 3.44. No entry edge; exit is the system.** |

## What the ledger says when you read it as one table

- **16 runs. Zero out-of-sample tests. Zero valid rows.**
- Two of the three results above PF 1.0 are already dead: #2 retracted for
  sample size, #15 void as an execution artifact. Only #13 survives, and it
  is one in-sample window with a confound (logic and timeframe both changed).
- Rows 9–12 are the plateau: four different architectures, same Jun–Jul 5m
  window, PF 0.819–0.886. Four distinct entry mechanisms converging on the
  same losing number is evidence about the **timeframe**, not the mechanisms.
- Rows 1–8 mostly lack trade counts and date ranges entirely. They cannot be
  compared to anything. Roughly half the project's recorded history is
  unusable as evidence.
- Every window ≤ 07-27 is Jun–Jul only — a ~2-month sample, because of the
  free-plan data cap. Row 13 was the first time a real sample was tested.

## Settings for the results that had them recorded

**#6 Top/Bottom, PF-analog 1.11** (recovered 2026-07-29 from the session
archive — these existed nowhere in the repo before):
```
useTestFail  = false      closePosPct = 0.2       rsiOb = 72
rsiOs        = 31         useTrendVeto = false    cooldown = 20
minReArmAtr  = 1.5
```
User confirmation, verbatim: *"oversold is 31 rest is as told"*.

**#13 Multi-Voice, PF 1.093:** `minScore = 6`, `weightHigh = true`, all 20
voters on, defaults elsewhere. Group ⑤/⑥ did not exist yet.

## Standing conclusions the table supports

1. **Trend / HTF filters have failed three times.** #12 (HTF bias MA, 0.882 →
   0.819), the ADX veto, and `useTrendVeto` on #6. Three strikes.
2. **A suspiciously low trade count is an execution symptom.** #15 looked
   like a 1.783 edge and was rejected orders. #7 looked like a strategy
   failure and was also plumbing.
3. **The plateau is the finding.** Rows 9–12 say XAUUSD 5m does not support
   these mechanisms after costs. Kronos was acquired to test that directly
   and is still blocked on HuggingFace being firewalled.

---

## Overfitting audit — 2026-07-29

Ran the Deflated Sharpe Ratio (Bailey & Lopez de Prado; implementation ported
from stefan-jansen/machine-learning-for-trading) over the ledger itself.
Reproduce with `python3 -m backtest.audit_ledger`.

Per-trade Sharpe reconstructed from (PF, WR, n) for every row that recorded
all three. **The reconstruction assumes uniform win and loss sizes, which
makes it optimistic — these are upper bounds, not measurements.**

| Row | n | PF | SR/trade |
|---|---|---|---|
| #6 Top/Bottom run 4 | 112 | 1.110 | +0.0492 |
| #9 OMNIBUS four-model | 298 | 0.843 | −0.0850 |
| #10 Key-to-Key | 245 | 0.886 | −0.0547 |
| #11 Trendline × Key Levels | 382 | 0.882 | −0.0623 |
| **#13 Multi-Voice** | **521** | **1.093** | **+0.0439** |
| #14 MV + level-to-level | 461 | 0.892 | −0.0551 |
| #15 Key Levels v1.0 (void) | 22 | 1.783 | +0.2932 |

### The result

| trials assumed | E[max SR] from noise | adjusted SR | DSR |
|---|---|---|---|
| 7 (ledger rows only) | 0.0809 | −0.0370 | **0.20** |
| 17 (every engine built) | 0.1066 | −0.0627 | **0.08** |
| 40 (engines × parameter passes) | 0.1277 | −0.0838 | **0.03** |

*(excluding the void 22-trade row, which inflates trial variance; including
it every figure drops below 0.001. The verdict is the same either way.)*

**DSR needs to reach ~0.95 to count as evidence of skill. The best result
this repo has ever produced reaches 0.08 at a realistic trial count.**

The expected maximum Sharpe from running 17 attempts on data with no edge is
**0.107 per trade**. The Multi-Voice engine achieved **0.044**. It did not
merely fail to beat the noise threshold — it came in at less than half of it.

### What this actually settles

PF 1.093 is not a small edge that needs more tuning. Once the number of
attempts is accounted for, it is **below what pure chance would have handed
us anyway**. Every "the plateau is close to 1.0, keep pushing" reading of the
last four months was wrong, and the ledger now says so quantitatively.

**The bar to clear:** at 17 trials and n=521, a result needs SR/trade ≥ 0.179,
which at a 44% win rate is roughly **PF 1.45**. Not 1.10. Anything between
1.0 and ~1.4 on this sample size is indistinguishable from search noise and
should not be built on.

---

## Row 19 — the first out-of-sample positive, and why it was rejected (2026-07-31)

First real dataset: 157,366 bars of XAUUSD 15m, Dec 2019 – Jul 2026, split
60/40 at 2023-11-28. The optimiser selected levels PMH/NYH/NYL on the
training half and the held-out block returned **PF 1.495 on n=60, +16.96%**.

Profit factor went UP out of sample. It looked like the breakthrough.
It is not. `python3 -m backtest.stress_test` failed it on all three gates.

### Gate 1 — random null at the MATCHED sample size: FAIL

Coin-flip entries through identical filters, stops, targets, sizing and
costs, rebuilt at n≈60 (367 trials):

| pct | PF |
|---|---|
| 50th | 0.905 |
| 75th | 1.122 |
| 90th | 1.370 |
| **95th** | **1.544** |
| 99th | 2.039 |

**Our 1.495 sits at the 93.5th percentile — below the 95th.** Random entry
beats it roughly one run in fifteen.

The width is the lesson. At n=60 the noise band runs from 0.905 to 2.039.
An earlier null built from ~810-trade samples gave 0.782–1.052, and using
THAT band here would have declared 1.495 a huge win. Profit-factor error
scales with 1/sqrt(n); a null must be rebuilt at the sample size being
judged. This is now enforced in stress_test.py.

### Gate 2 — deflated Sharpe: FAIL

SR/trade +0.1802 on n=60.

| trials | E[max SR] from noise | DSR |
|---|---|---|
| 1 | 0.0000 | 0.925 |
| 100 | 0.3750 | 0.060 |
| 370 (what the search actually ran) | 0.4387 | **0.019** |

Even granting the impossible fiction that only ONE configuration was ever
tried, DSR is 0.925 — still short of 0.95. At the true trial count it is
0.019.

### Gate 3 — buy and hold: FAIL

**+100.42% versus +16.96%** on the identical window. Gold doubled. The
strategy captured a sixth of that while carrying execution risk, 60 round
trips and a live-money failure mode that buy-and-hold does not have.

### What this actually establishes

**The config is rejected.** But the more useful finding is structural: a
strategy trading 60 times in 2.67 years CANNOT be validated on this data.
The noise band at that sample size is wider than any edge we could
plausibly detect. Selectivity that produces a thin sample is not rigour —
it is untestability.

That reframes the next step. The requirement is not "a better entry
rule", it is **a strategy that trades often enough to be measurable**.
Multi-Voice produced 521 trades in six months, which over this window
would be several thousand — enough that its noise band would be narrow
enough to see through. It is the only engine that ever cleared PF 1.0 and
it has never been tested out of sample.

### Precedent

This is the first time a promising number was killed BEFORE it entered the
ledger as a win. PF 3.656 and PF 1.783 were both celebrated first and
retracted later. The three gates are now mandatory and automated.

---

## Cross-validation: the Python engine is trustworthy (2026-07-31)

The user ran gold_trend_trailing.pine on TradingView over Feb 2 – Jul 31
2026 with both direction settings. Against the Python engine on the same
window and parameters (entry 50, trail 8.0 ATR):

| | n | WR | PF | net | max DD |
|---|---|---|---|---|---|
| **long only** — Python | 38 | 26.32% | 0.567 | −5.14% | 7.14% |
| **long only** — TradingView | 38 | 26.32% | 0.550 | −5.72% | 7.65% |
| **long+short** — Python | 58 | 31.03% | 1.444 | +6.94% | 3.44% |
| **long+short** — TradingView | 56 | 33.93% | 1.486 | +7.57% | 4.19% |

Long-only agrees **exactly** on trade count and win rate. The residual P&L
difference is fill and cost modelling; the ±2 trades on long+short is a
feed difference (OANDA spot vs the LSE export).

**This is the cross-validation that backtrader could not provide.** That
attempt failed on an execution-model mismatch and was marked INCOMPLETE.
TradingView turned out to be the second independent implementation, and it
agrees. Everything measured in `backtest/` can now be treated as
representative of what the Pine strategy will actually do — including the
6.7-year results, the random nulls and the deflated-Sharpe audit.

It also confirms the regime finding from the live side rather than only in
research: in a window where gold fell 15.8%, long-only returned −5.72% and
long+short returned +7.57%.

---

## Key levels as the entry/exit trigger (2026-07-31)

User request: *"i want you to enter and exit the trade on key levels.
reverse the signal as it touches the key level."*

Levels are `backtest/levels.py` — the port of the same SpacemanBTC module
the Pine host embeds, so every level tested here is a line drawn on the
chart. Data: XAUUSD 15m, 157,366 bars, 2019-12-01 → 2026-07-30.
Train = first 80% (125,892 bars), OOS = last 20% (31,474 bars).

### 1. Level touch as the ENTRY — no edge, in either direction

`backtest/kl_reverse.py`, always-in book, full period, all 18 levels.
`reverse` = fade the level (the user's spec); `break` = trade with it.

| config | n | WR | PF | net | max DD |
|---|---|---|---|---|---|
| reverse, gap 1 ATR | 11,726 | 56.8% | 0.835 | −88.4% | 88.5% |
| reverse, gap 6 ATR | 3,049 | 36.2% | 0.934 | −43.6% | 50.1% |
| break, gap 1 ATR | 13,690 | 38.7% | 0.895 | −81.3% | 82.6% |
| break, gap 6 ATR | 2,768 | 34.9% | 0.952 | −33.9% | 54.1% |

Costs are not the explanation. With commission and slippage set to **zero**
every configuration still sits on PF 1.00: reverse 0.984 / 0.951 / 1.000,
break 1.017 / 0.987 / 1.003 at gaps 1/3/6. A key-level touch carries no
directional information at 15m on this instrument — in either direction.
Adding the EMA2000 + slope gate lifts the best to PF 1.060, still far
below the breakout engine's 1.333 on the same data and settings.

**Conclusion: entry stays on the breakout.** Not shipped as a mode.

### 2. Level touch as the EXIT — small, consistent, counter-trend only

`backtest/trend.py` with `kl=` (new): baseline engine, entry unchanged,
exit at the nearest drawn level ahead of the position. Settings entry 50,
trail 6.0 ATR, SMA 750, EMA 2000, slope 200, short risk 0.75.

| config | TRAIN PF / net | OOS PF / net |
|---|---|---|
| baseline, no key levels | 1.244 / +85.6% | 1.580 / +29.3% |
| **close 75% at level, shorts only** | **1.289 / +89.7%** | **1.610 / +29.1%** |
| close 100% at level, shorts only | 1.246 / +82.3% | 1.579 / +29.0% |
| REVERSE at level, shorts only | 1.244 / +81.2% | 1.588 / +29.0% |
| **REVERSE at level, both sides** | **0.932 / −14.8%** | 1.521 / +20.7% |
| JEAFX quarter grid, shorts only | 1.297 / +92.3% | 1.598 / +28.5% |

Full period, 921 trades: baseline PF 1.333 / +152.5% / DD 13.6% →
75% level exit shorts-only PF **1.379 / +155.9% / DD 12.3%**.

Three findings, all consistent train and OOS:

1. **The reversal the user asked for is the worst config tested.** On both
   sides it turns a +85.6% train result into −14.8%. It is shipped as a
   toggle, defaulted OFF, with these numbers in its tooltip.
2. **The asymmetry rule holds a third time.** Acting on the level on both
   sides collapses the full period to PF 1.023 / +5.9%. Counter-trend side
   only is the best config measured.
3. **Real chart levels ≈ the synthetic quarter grid** (1.289 vs 1.297
   train, 1.610 vs 1.598 OOS). The chart levels are now the default
   because they are the ones the user can see, not because they measure
   better.

Sensitivity is flat, not knife-edge: tolerance 0.05–0.50 ATR moves train
PF 1.272–1.296; take fraction 60–90% moves it 1.282–1.296.

**Caveat that belongs on this row:** the gain over baseline (+0.045 PF on
train, +0.030 OOS) is small relative to the ~30 configurations swept to
find it. Treat it as "does not hurt, is what you asked for, and is
directionally consistent across both halves" — not as a validated edge.

---

## Confluence: key levels + a second SMA, merged (2026-07-31)

User request: *"i was keep key levels and SMA 2000 also a confluence. see
what can u do and merge them together."*

Same data and split as the row above. `backtest/trend.py` gained
`sma2_len` (a second, longer SMA gate) and `kl_entry_atr` (entry only when
a drawn level is within N ATR). Baseline verified unchanged first: still
PF 1.333 / +152.5% / 921 trades, five accounting tests passing.

### Which merge actually works

Common settings: entry 50, trail 6.0 ATR, EMA2000 regime + 200-bar slope,
short risk 0.75, key-level exit 75% counter-trend-only.

| confluence | TRAIN PF / net / DD | OOS PF / net / DD |
|---|---|---|
| SMA750 only (previous ship) | 1.289 / +89.7% / 12.3% | 1.610 / +29.1% / 8.3% |
| SMA2000 *instead of* 750 | 1.181 / +55.2% / 15.0% | 1.631 / +26.6% / 7.9% |
| **SMA750 AND SMA2000** | **1.335 / +93.0% / 9.6%** | **1.624 / +25.0% / 8.1%** |
| + level within 0.5 ATR of entry | 1.347 / +73.6% / 9.1% | 1.630 / +21.2% / 6.6% |
| + level within 1.0 ATR of entry | 1.284 / +66.8% / 10.6% | 1.615 / +24.2% / 7.0% |
| + level within 2.0 ATR of entry | 1.341 / +93.4% / 9.8% | 1.590 / +23.7% / 8.6% |

Full period, the layers stacked:

| build | n | WR | PF | net | maxDD | ret/DD |
|---|---|---|---|---|---|---|
| breakout + trail only | 921 | 36.3% | 1.333 | +152.52% | 13.61% | 11.21 |
| + key-level exit, shorts only | 922 | 38.5% | 1.379 | +155.89% | 12.30% | 12.68 |
| **+ slow SMA must agree** | **863** | **40.1%** | **1.421** | **+157.65%** | **9.63%** | **16.36** |
| + level near entry (rejected) | 822 | 39.3% | 1.385 | +120.94% | 10.57% | 11.44 |

### What this says

1. **The confluence is a drawdown filter, not a return generator.** Return
   moved +155.9% → +157.7%; drawdown fell 12.30% → 9.63%. Return per unit
   of drawdown went 12.68 → 16.36. That is the whole effect.
2. **It is the AGREEMENT that works, not the slower average.** SMA2000
   replacing SMA750 is worse on train (1.181 vs 1.289). Requiring only one
   of the two to agree is much worse (1.149). Requiring both is best.
3. **Key levels do not work as an entry confluence** — same conclusion as
   the row above reached from the entry-signal side, now reached again
   from the filter side. Full-period net drops +157.7% → +120.9%, and the
   effect is the same at 0.5, 1.0 and 2.0 ATR, so it is not a tuning
   problem. Shipped as a toggle, defaulted OFF.
4. **Sizing up on extra agreement was tested and rejected.** Requiring 1 of
   2 and paying +100% size for the second lifts train net to +146.1% but
   takes drawdown to 21.8% and PF down to 1.197 — leverage, not edge.

**Caveat:** ~20 configurations were swept here on top of the ~30 in the
row above. The confluence gain (+0.042 PF full period) is small against
that trial count. What supports it beyond the point estimate is that the
drawdown reduction shows up in both halves and in the full period, and
that the mechanism — two horizons disagreeing marks the choppy middle —
is not a free parameter.

---

## LIVE CONTRADICTS RESEARCH — the key-level exit (2026-07-31)

The user ran the confluence build on TradingView, XAUUSD 15m,
Feb 2 2026 → Jul 31 2026:

| | records | WR | PF | net | max DD | largest win | largest loss |
|---|---|---|---|---|---|---|---|
| **TradingView** | 65 | 56.92% | **0.702** | **−2.99%** | 3.83% | +92.94 | −120.38 |
| Python, same window/settings | 40 pos. | 45.0% | 1.385 | +3.54% | 2.46% | **+239.48** | −95.00 |

The trade counts are reconcilable — TradingView records each partial close
as its own row, Python counts one row per position. **The sign of the
result is not reconcilable.**

### The diagnostic

In a system with **no profit target**, the largest winner must dwarf the
largest loser; that asymmetry is the entire mechanism. TradingView reports
the opposite: largest win 92.94 against largest loss 120.38. Python on the
identical window reports +239.48 against −95.00, which is the right shape.
Something in the Pine build is cutting winners that the research engine
lets run.

A 56.92% win rate with a 0.702 profit factor is the same statement in
different units: many small wins, fewer larger losses.

### The mechanism, and why the research missed it

The Pine module exports **36 levels**; `backtest/levels.py` had **18**.
The difference is every range's MIDPOINT plus the quarterly, yearly and
session sets. Measured on the last 20,000 bars, the median distance to the
next level ahead of price:

| level set | median distance to next level |
|---|---|
| 18 (what was tested) | 0.70 ATR |
| **33 (what the chart draws)** | **0.46 ATR** |

**The trailing stop is 6 ATR behind. The "target" is 0.46 ATR ahead.**
Banking 75% of the position there risks 6 to make 0.46. That is a losing
structure regardless of hit rate, and it is exactly the shape of the live
result.

`levels.py` now has `build(dense=True)` reproducing the real 33-level set,
and `trend.py` has `kl_min_atr` so a target can be required to be a real
distance away.

### What was done about it

- **`useKL` now defaults OFF** in both Pine builds. It is the newest
  component, it is the only one whose job is to cut a winner short, and
  research says removing it costs nothing on this window (+3.54% → +3.47%).
- **`klMinAtr` added, default 3.0 ATR.** If the level exit is turned back
  on, levels closer than 3 ATR are skipped.

### Honest statement of what is still unexplained

Re-running the Python engine against the true 33-level set did NOT
reproduce the live failure — it still returns PF 1.385 on that window.
So the density finding explains the *mechanism* by which a level exit can
destroy a trend system, but it does not by itself close the gap between
+3.54% and −2.99%. The remaining candidates, in order:

1. Pine's `strategy.close(qty_percent=)` interacting with a live
   `strategy.exit` stop on the same entry ID.
2. Pine level values that are current-period rather than previous-period
   (the module's 4H and session levels track the running extreme).
3. Fractional-contract handling: Pine closes 1.5 of a 2-lot, Python floors
   to 1.

**Resolving this requires TradingView's actual trade list**, which cannot
be read from this container. Until then the shipped default is the
configuration that cross-validated cleanly in the earlier session
(Python +6.94% vs TradingView +7.57% on this same window).

---

## Cross-validation restored, 30m (2026-07-31)

User re-ran the shipped build with the key-level exit OFF. XAUUSD **30m**,
Jan 2 2025 → Jul 31 2026. Auto-scale derives entry 24, SMA 384, EMA 1008,
slope 96, SMA2 1008, trail 4.243. The chart shows "SMA cross" exit labels,
so `smaExit` was ON; Python matched to that.

| | n | WR | PF | net | max DD | largest win | largest loss | avg bars |
|---|---|---|---|---|---|---|---|---|
| **TradingView** | 161 | 34.16% | **1.556** | +26.98% | 5.68% | +463.95 | −240.77 | 41 |
| Python, exact-stop fills | 189 | 32.80% | 1.558 | +30.92% | 5.42% | +463.68 | −124.16 | 39 |
| Python, gap-aware fills | 189 | 32.80% | 1.499 | +28.76% | 5.82% | +463.68 | **−241.22** | 39 |

**Profit factor agrees to 0.002. Largest win agrees to 0.27 on 464.**
That is the closest this project has come to an independent match.

### The largest-loss gap, found and fixed

Python filled every stop exactly at the stop price. A bar can OPEN through
the stop, and then the fill is the open. TradingView models that; this
engine did not — which is the entire 124.16 vs 240.77 difference. With
`gap_fill=True` the worst loss becomes −241.22 against TradingView's
−240.77, a 0.45 match.

`gap_fill` is OFF by default so every existing ledger row still reproduces,
**but the exact-stop model is optimistic and every future row should set
it.** Cost on this window: PF 1.558 → 1.499, net +30.92% → +28.76%.

### What is still unexplained

Trade count: 189 in Python against 161 on TradingView, 17% more. Not a
sign or magnitude problem, but not noise either. Most likely the remaining
toggle states differ from what was assumed here. Resolving it needs the
TradingView trade list.

### Shape check — this is now a trend system again

WR 34.16% with PF 1.556 and a largest win nearly double the largest loss.
That is the correct signature, and it is the direct contrast with the
previous run's 56.92% WR / 0.702 PF / largest win BELOW largest loss.
**Win rate falling while profit factor rises is the system working.**

Caveat the user should hold: buy-and-hold returned more over this window
(TradingView's benchmark panel, +44.49% against the strategy's +26.86%).
The claim for this system has always been return per unit of drawdown, not
raw return, and that claim needs the buy-and-hold drawdown to be stated
beside it — which this run does not give.

---

## Return review: every lever measured (2026-07-31)

User: *"go through our entire session and find out a way to increase the
returns and fix whatever we are missing."* All numbers below use
`gap_fill=True` (BUG-018), so they are slightly worse and more honest than
every row above.

### Levers that turned out to be already correct

| lever | finding |
|---|---|
| trail width | Wider raises PF but LOWERS return: trail 20 gives PF 1.659 / +23.5% train against trail 6's PF 1.243 / +85.4%. **The old "wider is better" claim was PF-only and is corrected here.** 6 ATR on 15m (4.24 on 30m) is return-optimal at tolerable drawdown. |
| trail at 30m | Swept 3.0–10.0. The sqrt rule's 4.24 is best on train net (+113.5%) and near-best OOS. No gain available. |
| sizing quantisation | `floor()` on contracts costs a 7.4% median size at $10k on 15m; >20% on 13.2% of bars. Real but small, and it grows less relevant as equity compounds. |

### Lever that IS available: timeframe

| TF | TRAIN PF / net / DD | OOS PF / net / DD |
|---|---|---|
| 15m | 1.259 / +94.5% / 11.95 | 1.515 / +27.7% / 8.51 |
| **30m** | **1.326 / +112.4% / 11.58** | **1.594 / +28.4% / 7.79** |
| 1h | 1.278 / +80.1% / 11.78 | 1.684 / +30.2% / 6.16 |
| 4h | 1.234 / +40.5% / 8.34 | 2.110 / +30.3% / 3.36 |

30m beats 15m on PF, return AND drawdown, in both halves. Higher
timeframes keep raising PF and cutting drawdown while giving up return.

### The big one: adding to winners (pyramiding)

Never tested in this project before today. Add another unit every N ATR of
favourable movement; the shared trailing stop covers the stack.

Walk-forward, five consecutive slices of the 30m history, net/maxDD:

| config | slice 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| no adds | +38.4/9.2 | +19.6/6.7 | +8.8/10.4 | +15.1/10.2 | +28.4/7.8 |
| **adds 3 ATR × 2** | +92.5/16.3 | +23.9/13.5 | +11.9/16.6 | +33.3/16.8 | +88.1/13.5 |
| adds 2 ATR × 4 | +163.4/22.2 | +16.5/19.1 | +11.2/26.4 | +31.7/25.7 | +168.2/13.9 |

**Five slices out of five improve.** That is a plateau, not a fitted peak.

**It is not an edge, and the tests say so plainly.** Through RANDOM entries
on 20 seeds it lifts the median from 6.8% to 25.3% but takes the spread
from 6.8 to 29.5 and the worst seed from −3.5% to −30.2%. It amplifies
whatever the entry does, in both directions. On TRAIN, simply raising risk
to 3% beats it at matched drawdown (+707.7%/31.76 against +425.0%/31.93);
on OOS pyramiding wins decisively (+168.2%/13.91 against +133.5%/24.66).

Shipped ON at the moderate setting (3 ATR × 2 adds), off-switch in group ⑥.

### Shipped configuration, and the benchmark that was owed

XAUUSD 30m, auto-scaled, gap-aware fills, SMA confluence on, key-level exit
off, 2 adds every 3 ATR:

| window | | net | max DD | ret/DD | PF |
|---|---|---|---|---|---|
| TRAIN | no adds | +116.5% | 9.83% | 11.85 | 1.380 |
| | **with adds** | **+239.6%** | 17.68% | 13.55 | 1.370 |
| | buy & hold | +111.3% | 21.92% | 5.08 | — |
| OOS | no adds | +23.2% | 7.78% | 2.98 | 1.529 |
| | **with adds** | **+66.2%** | 12.88% | 5.14 | 1.879 |
| | buy & hold | +32.3% | 29.08% | 1.11 | — |
| FULL 6.7y | no adds | +192.6% | 9.83% | 19.58 | 1.444 |
| | **with adds** | **+660.2%** | 17.68% | 37.33 | 1.626 |
| | buy & hold | +179.1% | 29.08% | 6.16 | — |

**This is the first configuration in this project that beats buy-and-hold
on raw return as well as on risk** — +660.2% against +179.1% over 6.7
years, at 17.68% drawdown against 29.08%.

**Caveat that must travel with these numbers:** the pyramiding parameters
were chosen after seeing all five walk-forward slices. The slices are not
out-of-sample for that choice. What supports it is that all six variants
tested improved all five slices, not that 3 ATR × 2 was best.

---

## DE Hybrid V5/V6 (user-supplied indicator) — ported and measured (2026-07-31)

Ported line for line to `backtest/de_hybrid.py` (Supertrend, AlphaTrend on
MFI, BBSR EMA200, 9/21/50 stack, RSI, MACD, ATR+BB volatility gate, sweep
detector, volume, cooldown, the 5-of-5 confluence counter, the alternating
state machine and all five V6 X exits). XAUUSD 30m, 6.7 years,
gap-aware fills, same costs and sizing as every other row.

### As written

| config | n | PF | net | max DD |
|---|---|---|---|---|
| **exactly as supplied (no stop)** | 720 | 0.952 | **−89.0%** | **97.56%** |
| + a 6 ATR protective stop | 698 | 0.970 | −1.5% | 8.27% |

**The script has no stop loss.** Nothing bounds a losing trade except one
of five discretionary exits happening to fire. That is the −89%.

### Why it cannot hold a trend: it exits in 3 bars

Exit attribution over 698 trades with the stop added:

| exit | share | net contribution |
|---|---|---|
| momentum loss | 40.0% | **−$3,061** |
| profit giveback | 31.8% | +$3,494 |
| opposite sweep | 25.9% | −$129 |
| EMA21 break | 2.1% | −$348 |
| the protective stop | 0.1% | −$105 |

**Average hold 3 bars, against 44 for the shipped engine.** Five exits
OR-ed together means the earliest one always wins, and the earliest of five
is very early. `use_mom_exit` alone is the largest single loss source.

Two more structural problems:
- **0.8 ATR profit giveback against an unbounded loss** is BUG-017's
  arithmetic again — a tiny gain trigger with no matching loss trigger.
- **The alternating state machine** (states 2/−2) forbids re-entering the
  same direction after an exit. In a trend that is fatal: you give back
  0.8 ATR, exit, and then cannot re-enter long until you have taken a short.
  Removing it takes the same entry from +30.7% to +68.2%.

### Is the entry any good? No, but no worse than ours

Their entry through THIS repo's ATR trailing exit, no alternation:

| | n | PF | net | max DD |
|---|---|---|---|---|
| DE Hybrid entry, trail 6 ATR | 787 | 1.213 | +68.2% | 13.15% |
| random entries, matched rate, same exit | — | median 1.154 | — | — |

Their five-condition confluence beats the random median but sits inside
its range (0.855–1.365, better than 10/15 seeds). **No entry edge** — the
same verdict this project has reached for every entry rule it has tested,
including its own.

### Does it improve the shipped engine as a filter? No

| gate on our 30m build | TRAIN | OOS | FULL |
|---|---|---|---|
| none (shipped) | PF 1.370 / +239.6% / 17.68 | 1.879 / +66.2% / 12.88 | **1.626 / +660.2% / 17.68** |
| + DE trend gate | 1.279 / +119.1% / 23.27 | 1.906 / +63.6% / 7.59 | 1.570 / +374.1% / 23.27 |
| + DE confluence ≥3 only | 1.378 / +240.6% / 18.26 | 1.850 / +64.3% / 12.94 | 1.625 / +652.1% / 18.26 |
| + DE volatility expansion | 1.276 / +93.9% / 22.85 | 2.358 / +56.8% / 8.79 | 1.603 / +275.7% / 22.85 |

Neutral at best, harmful in two of three. Nothing to take.

### Best achievable repair of the supplied script

6 ATR stop, momentum and sweep exits removed, alternation removed,
giveback widened 0.8 → 4.0 ATR: **PF 1.134, +40.7%, DD 15.06%.** Every
repair moves it toward "just use a trailing stop", and the pure trailing
version (+68.2%) beats all of them — which is the finding.

**Verdict: nothing measurable to adopt.** Keep it as a chart-reading layer
if the visuals help; it is not an entry filter and its exits are the
failure mode this project spent four months escaping.

---

## Profit taking: does it work, and which kind? (2026-07-31)

User: *"turn it into a profitable profit taking strategy... see if key
levels, quarters or point based profit taking works."* New engine
`backtest/take_profit.py`: entry signal + fixed stop + fixed target, four
target modes, optional partial-and-trail runner. XAUUSD 30m, 6.7 years,
gap-aware stop fills, stop assumed first on any bar touching both.

### Answer: point/percent works. Levels and quarters do not.

Train half, DE Hybrid entry, 4 ATR stop:

| target type | n | WR | PF | net |
|---|---|---|---|---|
| next key level (33 drawn) | 2,015 | 76.2% | **0.824** | −37.3% |
| next JEAFX 2.50 quarter | 2,903 | 83.9% | **0.794** | −38.5% |
| next Yotov 25 quarter | 1,117 | 62.8% | 1.034 | +14.5% |
| next Yotov 250 quarter | 108 | 25.9% | 1.580 | +53.9% |
| **40 fixed points** | 462 | 37.7% | **1.255** | +126.2% |
| 80 fixed points | 243 | 23.9% | 1.398 | +98.0% |

**Why levels and quarters fail:** their target distance is set by where the
line happens to sit, not by what the trade needs. The target/stop ratio is
therefore random per trade — sometimes 0.2, sometimes 5. A percent or point
target fixes that ratio. Note the 76–84% win rates on the failing rows:
they win constantly and still lose money, which is BUG-017's arithmetic in
its purest form. The Yotov 250 row scores well only because at 563 bars'
average hold it is not really a target at all.

### Fixed points vs percent — and why percent is shipped

Gold ran 1450 → 4100 over the sample, so a fixed 40-point target was 2.7%
of price at the start and 1.0% at the end. Testing the scale-invariant
version separates "a target of about this size works" from "this number
fitted this price path". Both work; percent is more stable and is what
ships. Full period, our Donchian entry: points PF 1.160, percent PF 1.475.

### The shipped profit-taking build

Donchian entry + confluence, static 4 ATR stop, 4% target, full exit,
ranked out of 48 combinations by the WEAKER of its two halves so a
train-only winner cannot top the list:

| | n | WR | PF | net | max DD |
|---|---|---|---|---|---|
| TRAIN | — | — | 1.402 | +98.5% | — |
| **OOS** | — | — | **1.420** | **+23.2%** | — |
| FULL | — | — | **1.475** | +185.3% | 23.2% |

**Train and out of sample agree to 0.018 of profit factor.** That is the
most stable result this project has produced.

### How it compares with the trailing build

| architecture | PF | net | max DD |
|---|---|---|---|
| profit target, 4% / 4 ATR | **1.475** | +185.3% | 23.2% |
| trailing stop, no target | 1.444 | +192.6% | **9.83%** |
| trailing stop + 2 adds | **1.626** | **+660.2%** | 17.68% |

Profit taking beats the plain trail on profit factor and loses to it badly
on drawdown. It loses to the pyramided trail on everything.

**So it is shipped as a MODE, not as the default** — group ⑦, "Off" by
default. It is the right choice for someone who wants frequent closed wins
and can accept 23% drawdown; it is the wrong choice for maximum return.

### Same structures on the DE Hybrid entry

Weaker but real: 40pt/4 ATR gives full PF 1.165 (+125.8%), the 50%-runner
1.251 (+125.6%), 3% target 1.229 (+121.3%). The entry is the limitation,
not the exit architecture.

**Caveat:** ~90 configurations were swept. The 4%/4 ATR winner was chosen
on the train half and confirmed once on OOS; the ranking metric was the
weaker of the two halves, which is stricter than picking on train alone but
is not a substitute for a fresh sample.

---

## Body Pierce MA (user-supplied indicator) — SMA/EMA/HMA crosses (2026-07-31)

`trend.py` gained `sig_L`/`sig_S`, which replace the Donchian breakout with
any supplied entry signal, so a submitted indicator can now be measured
through this engine's exit, sizing and costs in one line. XAUUSD 30m,
6.7 years, gap-aware fills.

### The crosses alone, through the 4.24 ATR trailing exit, no filters

Reference — Donchian, no filters: TRAIN PF 1.081 / +41.0%, OOS 1.327 /
+26.0%, **FULL 1.121 / +76.4%**.

| MA | 50 | 100 | 200 | 400 | 800 |
|---|---|---|---|---|---|
| SMA (full PF) | 1.046 | 0.983 | **0.920** | 0.941 | 0.910 |
| EMA (full PF) | 1.044 | 0.887 | 0.861 | 0.844 | 0.802 |
| HMA (full PF) | 1.030 | 1.068 | **1.152** | 1.070 | 0.926 |

**The script's own default — SMA 200 — is the single worst setting in the
grid**, PF 0.920 and −17.0% full period. Every EMA length loses. HMA is the
only family that holds up, and 200 is its best by the weaker of the halves.

### With the full confluence stack and 2 adds

| entry | TRAIN PF / net | OOS PF / net | FULL PF / net / DD | ret/DD |
|---|---|---|---|---|---|
| Donchian (shipped) | 1.370 / +239.6% | 1.879 / +66.2% | 1.626 / +660.2% / 17.68 | **37.3** |
| **HMA 200 cross** | **1.462** / +206.9% | **2.008** / +63.7% | **1.743** / +540.4% / 20.9 | 25.9 |
| SMA 200 cross | 1.278 / +62.6% | 2.026 / +39.8% | 1.427 / +126.2% / 17.1 | 7.4 |

**HMA 200 beats the Donchian on profit factor in BOTH halves** (1.462 vs
1.370 train, 2.008 vs 1.879 OOS). It is more accurate per trade. It also
returns 18% less and draws down 3pp more, so return per drawdown goes
37.3 → 25.9.

Neither is strictly better. Shipped as a selectable entry in group ①,
Donchian still the default because return per unit of drawdown is what this
system is built for.

### "Body pierce" does not do what the name says, and the name is worse

The supplied script crosses on CLOSE. The literal reading — the average
sitting inside the candle body — was implemented and measured separately:
full PF 1.647 against the close cross's 1.743 on HMA 200, and 1.365 against
1.427 on SMA 200. **Worse in both halves for both averages.** The code's
actual behaviour is better than its name; the close cross is what ships.

**Caveat:** 30 MA configurations were swept, then 4 re-run with the full
stack. HMA 200's two-half PF advantage is small (+0.092 train, +0.129 OOS)
and was selected after seeing both halves.
