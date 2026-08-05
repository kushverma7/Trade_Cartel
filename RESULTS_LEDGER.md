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

---

## Exit laboratory: six trailing algorithms, TP1/TP2 (2026-07-31)

User: *"find even better profit taking and trailing logic and also you can
make tp1 and tp2. also do not miss the found best results already."*

New engine `backtest/exit_lab.py`. It reproduces both existing engines as
special cases before anything new was trusted:

| | reference | exit_lab |
|---|---|---|
| trend.py trail + 2 adds | PF 1.626 / +660.2% / 17.68 | PF 1.635 / +679.9% / 17.01 |
| take_profit 4% / 4 ATR | PF 1.475 / +185.3% / 23.2 | **PF 1.475 / +185.3% / 23.2** |

**Two bugs were found and fixed in the new engine before any result was
read from it**, both of which would have produced false findings:

1. **Intrabar lookahead.** The best excursion was updated with the current
   bar's high BEFORE the stop was checked on that bar, so a bar could raise
   its own stop and then trigger it. It reported PF 1.183 and 45.2%
   drawdown against the true 1.635 and 17.01%.
2. **Give-back trail never armed.** With zero excursion at entry the stop
   snapped to the entry price on bar two; the mode scored a 1.0% win rate
   over 2,307 trades. Fixed with an arming threshold.

### Trailing algorithms, train half, Donchian entry + 2 adds

| trail | n | PF | net | maxDD | ret/DD |
|---|---|---|---|---|---|
| **chandelier 4.24 (shipped)** | 640 | 1.392 | +253.1% | 17.01 | 14.88 |
| **donchian 40-bar low** | 536 | 1.544 | +487.3% | 22.73 | 21.44 |
| donchian 45 | 506 | 1.427 | +347.2% | 23.45 | 14.81 |
| step 6.0→3.0 over 10 ATR | 667 | 1.380 | +252.8% | 20.25 | 12.49 |
| EMA 100 trail | 748 | 1.383 | +242.3% | 33.66 | 7.20 |
| give-back 20% (armed) | 1104 | 1.061 | +21.0% | 18.27 | 1.15 |

**The training peak at donchian-40 is not real.** Out of sample the whole
30–50 range performs and the ordering reverses — donchian 50 is best OOS
(PF 1.967) and 40 is mid-pack. A parameter whose neighbours are 30–50%
worse on train and indistinguishable out of sample is a fitted spike. 45
was shipped as the middle of the OOS plateau, not the training maximum.

### Final comparison, all three windows

| exit | TRAIN | OOS | FULL | losing slices |
|---|---|---|---|---|
| **chandelier 4.24** | 1.392 / +253.1% / 17.0 | **1.930** / +83.4% / 12.8 | 1.635 / +679.9% / 17.0 | **0/5** |
| **donchian 45** | 1.427 / +347.2% / 23.5 | 1.854 / +96.8% / 11.1 | 1.624 / **+935.9%** / 23.5 | 1/5 |
| donchian 50 | 1.396 / +289.2% / 26.0 | 1.967 / +111.9% / 14.5 | 1.637 / +853.0% / 26.0 | 1/5 |
| step 6→3 | 1.380 / +252.8% / 20.3 | 1.862 / +87.4% / 10.6 | 1.597 / +668.8% / 20.3 | 0/5 |

**Donchian 45 returns 38% more (+935.9% vs +679.9%) but return per unit of
drawdown is a dead heat: 39.9 against 40.0.** It is the same efficiency
taken at larger size, and it has one losing walk-forward slice (−6.0%)
where the chandelier has none. Shipped as a selectable mode, chandelier
still the default.

### TP1 / TP2: measured 20 ways, costs return every time

| config | PF | net | maxDD |
|---|---|---|---|
| no targets | 1.392 | **+253.1%** | 17.01 |
| TP1 8 ATR take 25% | 1.386 | +234.1% | 16.86 |
| TP1 4 / TP2 12, 25% each | 1.385 | +216.7% | 16.04 |
| TP1 4 ATR take 33% + breakeven | 1.286 | +134.2% | 18.43 |
| best shorts-only variant | 1.421 | +242.6% | 16.76 |

Every single one returns less. Out of sample the gap widens: PF 1.568 with
TP1 against 1.930 without. Even the **asymmetry rule fails here** — applying
targets only to the counter-trend side still costs return (+242.6% against
+253.1%), the first time that principle has not held in this project.

**What TP1/TP2 does buy is a smoother curve:** full-period drawdown
17.01% → 16.04%, and out-of-sample drawdown 12.79% → **8.38%**. That is a
real trade for someone who cares more about the ride than the total.

Shipped as functional controls in group ⑨, defaulted OFF, numbers in the
tooltip.

### Nothing already found was lost

The shipped defaults still produce the session's best result: 30m,
Donchian entry, EMA+SMA+slow-SMA confluence, chandelier 4.24, 2 adds every
3 ATR, no targets — **full period PF 1.635, +679.9%, drawdown 17.01%**,
against buy-and-hold's +179.1% at 29.08%.

---

## DE Hybrid V7 ported, exit rebuilt, shipped as a strategy (2026-07-31)

V7 keeps the V5 entry unchanged and grows the exit block from five OR-ed
conditions to **twelve**. Ported into `backtest/de_hybrid.py` behind a
`v7=True` flag. XAUUSD 30m, 6.7 years, gap-aware fills, same costs/sizing.

### V7 vs V6 as supplied

| build | n | PF | net | max DD |
|---|---|---|---|---|
| V6 (5 exits), no stop | 720 | 0.952 | −89.0% | 97.56% |
| **V7 (12 exits), no stop** | 720 | 0.969 | **−83.9%** | **98.37%** |
| V6 + 6 ATR stop | 698 | 0.970 | −1.5% | 8.27% |
| V7 + 6 ATR stop | 698 | 1.025 | +1.1% | 8.09% |

V7 is a marginal improvement on V6 and still break-even. **Average hold
fell from 3.0 bars to 2.3** — more exits OR-ed together means the earliest
one wins, and the earliest of twelve is earlier than the earliest of five.

### Which of the twelve fires (V7 + 6 ATR stop, 698 trades)

| exit | share | net |
|---|---|---|
| momentum loss | 28.8% | **−$2,069** |
| profit giveback | 28.2% | **+$2,607** |
| opposite sweep | 25.4% | −$271 |
| RSI divergence | 6.2% | −$301 |
| ATR spike | 5.7% | −$258 |
| BBSR fail | 2.3% | −$167 |
| **dynamic trail** | 2.1% | **+$770** (best per-trade) |
| EMA21 / EMA9x | 1.3% | −$197 |

Only two of the twelve pay. Of the seven NEW V7 exits, only the dynamic
trail is positive.

### Subtraction does not rescue it

| kept | TRAIN PF | OOS PF | FULL PF / net |
|---|---|---|---|
| all twelve | 1.036 | 0.992 | 1.025 / +1.1% |
| drop momentum (+sweep) | 1.122 | **0.839** | 1.061 / +3.1% |
| giveback + dynamic only | 0.908 | 1.186 | 0.928 / −5.8% |
| giveback only | 0.910 | 1.277 | 0.938 / −5.0% |

Best subtraction reaches PF 1.061 and goes NEGATIVE out of sample. The
architecture is the problem, not the parameter set.

### The replacement: one Donchian trail

V5 entry, no alternation, initial 4.24 ATR stop, stop rides the lowest low
of the last N bars. Selection on train, confirmed once on OOS, ranked by
the weaker half.

| exit | TRAIN | OOS | FULL | losing slices |
|---|---|---|---|---|
| V7's twelve + stop | 1.036 / +1.5% | 0.992 / −0.0% | 1.025 / +1.1% | — |
| chandelier 6.0 | 1.185 / +42.7% | 1.346 / +12.5% | 1.233 / +67.4% | 2/5 |
| donchian 60 | 1.239 / +95.1% | 1.331 / +18.8% | 1.275 / +147.7% | 0/5 |
| **donchian 160** | **1.508 / +119.8%** | **1.899 / +26.3%** | **1.635 / +198.1%** | **0/5** |
| target 3% / 4 ATR stop | 1.298 / +106.5% | 1.137 / +9.3% | 1.229 / +121.3% | 1/5 |
| TP1 2% + donch60 runner | 1.197 / +74.7% | 1.266 / +18.6% | 1.231 / +115.6% | 0/5 |

**PF 1.025 → 1.635. Net +1.1% → +198.1%. Drawdown 8.09% → 11.02%.**
Average hold 2.3 bars → 215.

**And it is a plateau, not a spike** — the check that killed two earlier
candidates:

| lookback | 80 | 100 | 120 | 140 | **160** | 200 | 250 |
|---|---|---|---|---|---|---|---|
| full PF | 1.256 | 1.234 | 1.359 | 1.522 | **1.635** | 1.522 | 1.355 |
| OOS PF | 1.344 | 1.362 | 1.796 | 1.935 | 1.899 | 1.687 | 1.512 |

Both halves rise and fall together across the whole range.

### Standing limit, unchanged

The V5 entry still carries no measurable edge: through this repo's trailing
exit it scores PF 1.213 against a matched random-entry median of 1.154,
inside the random range. **The exit was fixed; the entry was not, because
it cannot be.**

Shipped as `strategies/de_hybrid_strategy.pine` with position sizing,
costs, a margin guard, and the V7 exit block retained as an off-by-default
toggle with its attribution in the tooltip.

---

## The 22-voice knowledge layer applied to the shipped engine (2026-07-31)

User challenge: *"please make sure you have read the initial instructions
and also used the knowledge of the data i have given you."*

Fair. CLAUDE.md carries a STANDING RULE that the knowledge layer "is
applied as confluence inside every strategy built or tuned — aligned
tier-A signals upgrade entries, opposing ones veto/de-risk." **Nothing
built in this session had been tested against it.** `backtest/voices.py`
already has all 22 voices vectorised from an earlier session and it was
sitting unused. This row closes that gap.

XAUUSD 30m, 6.7 years, shipped engine (Donchian + confluence + 2 adds).

### As a veto gate — how many voices must agree with the trade

| gate | TRAIN PF / net | OOS PF / net / DD | FULL PF / net |
|---|---|---|---|
| none (shipped) | 1.370 / +239.6% | 1.879 / +66.2% / 12.88 | 1.626 / +660.2% |
| net ≥ 0 | 1.370 / +239.6% | 1.879 / +66.2% / 12.88 | 1.626 / +660.2% |
| net ≥ 4 | 1.357 / +225.0% | 1.906 / +66.4% / 10.97 | 1.616 / +621.4% |
| **net ≥ 6** | 1.372 / +215.5% | **1.954 / +67.3% / 10.44** | **1.641 / +599.2%** |
| net ≥ 8 | 1.156 / +64.6% | 2.020 / +45.4% | 1.369 / +190.3% |
| net ≥ 12 | 0.498 / −6.1% | 0.000 / −2.0% | 0.433 / −7.9% |

**The first real finding is that the gate barely bites.** At threshold 0 it
changes literally nothing, and at threshold 4 it removes 13 trades out of
799. The 22 voices almost always already agree with a Donchian breakout
that has cleared an EMA regime gate, a slope gate and two SMAs — **the
knowledge layer is largely redundant with the trend filters the engine
already has.** Most of the voices are trend-following in nature, so they
are measuring the same thing in different words.

At **net ≥ 6** it is a small, consistent risk improvement: out-of-sample
profit factor 1.879 → 1.954 and out-of-sample drawdown 12.88% → 10.44%,
for about 9% of the return. Full-period PF 1.626 → 1.641. Push past 8 and
it collapses.

### As a standalone ENTRY (replacing the breakout)

| voice score crosses | TRAIN PF / net | OOS PF / net | FULL PF / net |
|---|---|---|---|
| ±4 | 1.213 / +169.6% | 1.775 / **+96.7%** | 1.445 / +585.8% |
| ±6 | 1.242 / +172.6% | 1.684 / +73.9% | 1.468 / +552.1% |
| ±8 | 1.155 / +86.1% | 1.798 / +54.1% | 1.384 / +284.4% |

**The knowledge layer beats every other supplied entry.** Full-period PF
1.468 against the DE Hybrid's 1.213 and the SMA-200 cross's 0.920, and its
out-of-sample return (+96.7%) is the highest of any entry tested. It still
loses to the Donchian breakout inside the full engine (1.626), and it
carries a 28% drawdown against 17.7%.

### Individual voices as the gate

| voice | FULL PF / net |
|---|---|
| V18 tier-A candle must actively agree | **1.498** / +109.5% (n=275) |
| V19 key-level sweep must actively agree | 1.579 / +555.3% |
| V21 key-level break-retest must actively agree | 1.588 / +563.9% |

V18 has the highest per-trade quality of any single filter measured in
this project — but it cuts the trade count from 799 to 275 and the return
to a sixth, so it is quality per trade bought with most of the opportunity.

**Verdict: the voice layer is real but redundant here.** It is shipped
nowhere yet; `strategies/multivoice_confluence_engine.pine` (1,843 lines)
already contains all 22 voices in Pine, so porting the net ≥ 6 gate into
the strategy is a mechanical job if the out-of-sample drawdown improvement
is judged worth ~9% of return.

---

## VALIDATION CERTIFICATE — the champion put through all four tests (2026-07-31)

User: *"create a logically proven strategy... fix all the limitations and
mistakes."* This row is the proof that was never run on the current build.
Config: XAUUSD 30m, Donchian entry, EMA regime + slope, fast and slow SMA,
chandelier 4.24 trail, 2 adds every 3 ATR, gap-aware fills.

### 1. Random-timing null (30 seeds) — CORRECTED METHOD

The earlier null in this repo was **wrong**: `random_p` mode skips the
filters, so it compared entry+filters against nothing and flattered the
entry. The corrected null draws random entries from the SAME filtered bars
at a matched rate, so only the trigger differs.

| | PF | net |
|---|---|---|
| champion | **1.626** | +660.2% |
| random timing, same filters (median of 30) | 1.478 | +524.1% |
| random timing, range | 1.378 – 1.635 | +312.3% to +817.6% |

Champion percentile **93.3%**, beats 28/30. **The trigger is inside the
noise band.** The important half of that result: the random arm still
returns a median +524%. The edge is in the filters, exit and adds, and it
survives replacing the entry with a coin flip.

### 2. Deflated Sharpe Ratio

| trials assumed | DSR | adjusted SR |
|---|---|---|
| 1 | 1.0000 | +0.1163 |
| 50 | 0.9998 | +0.1002 |
| 500 | 0.9997 | +0.0948 |
| **1000** | **0.9996** | +0.0933 |

Observed Sharpe +0.1163 per trade over 799 trades, skew +3.89, kurtosis
22.1. **PASS at every trial count**, including one far above what this
session actually ran. Compare the July audit of the older engines: DSR
0.03–0.20 for the same test. Those were noise; this is not.

### 3. Probability of Backtest Overfitting (CSCV)

24 configurations × 78,695 bars, 252 symmetric splits: **PBO = 0.099**,
median logit +1.609. Below 0.5 means selection beats random; 0.099 means
it beats it comfortably.

### 4. Year by year

| year | n | WR | PF | net | maxDD | gold |
|---|---|---|---|---|---|---|
| 2020 | 104 | 20.2% | 1.596 | +44.8% | 14.73% | +24.9% |
| **2021** | 125 | 17.6% | **0.978** | **−1.5%** | 14.26% | −4.3% |
| 2022 | 124 | 25.0% | 1.269 | +16.1% | 9.48% | −0.3% |
| 2023 | 127 | 23.6% | 1.318 | +19.3% | 17.20% | +12.8% |
| 2024 | 128 | 21.1% | 1.482 | +31.3% | 12.14% | +27.1% |
| 2025 | 125 | 27.2% | 1.977 | +73.9% | 13.58% | +64.7% |
| 2026 | 54 | 29.6% | 2.094 | +26.0% | 5.32% | **−6.0%** |

**Six of seven years profitable; the worst is −1.5%.** 2026 is +26.0%
while gold fell 6.0%, which is the falling-market claim validated on real
bars rather than asserted.

### What this certificate does NOT claim

- It does not claim the entry predicts anything. Test 1 says the opposite.
- The parameters were chosen across this session with knowledge of both
  halves. DSR and PBO are the defence against that, and they pass, but a
  genuinely fresh sample would be better than either.
- 2021 is a losing year. Any run that starts inside a 2021-like regime
  will be underwater for a while.

---

## The PF-vs-frequency frontier — why "PF 4, daily" does not exist (2026-07-31)

User: *"but you told pf 4 i can deliver daily what about that?"*

**Record check first: no PF 4 was ever claimed, in this session or in the
repo.** The number is **PF 3.656**, and it was **RETRACTED on 2026-07-20 on
the user's own instruction** — before this session began. MEMORY.md line
48 records it in full:

> XAUUSD 5m, May 18 – Jul 14 2026 (~2 months, free-plan history limit)
> PF 3.656 | Win 51.28% (60/117 trades) | Max DD **$1.35** | Net PnL **+$34.19**

**That is the tell.** 117 trades produced thirty-four dollars with a
one-dollar-thirty-five drawdown. The position size was microscopic, so a
handful of ticks set the profit factor. PF is meaningless at that size and
that sample, which is exactly why the retraction rule exists and why no
strategy here may use "proven" language without 300+ trades.

### The frontier, measured

Same engine, 6.7 years, only timeframe and trail width varied. Sorted by
profit factor:

| TF | trail | trades | per week | PF | net | maxDD |
|---|---|---|---|---|---|---|
| 4h | 24.0 | 94 | **0.27** | **3.165** | +96.2% | 5.69% |
| 1h | 24.0 | 103 | 0.30 | 2.499 | +88.8% | 6.18% |
| 2h | 24.0 | 99 | 0.29 | 2.075 | +57.7% | 7.54% |
| 4h | 16.0 | 203 | 0.59 | 2.063 | +93.1% | 15.68% |
| **30m** | **6.0** | **799** | **2.31** | **1.626** | **+658.7%** | 17.72% |
| 15m | 6.0 | 873 | 2.52 | 1.463 | +650.7% | 27.51% |
| 30m | 3.0 | 1,471 | 4.25 | 1.074 | +39.9% | 29.67% |
| 15m | 3.0 | 1,578 | 4.56 | 1.039 | +22.3% | 46.09% |
| 1h | 3.0 | 1,350 | 3.90 | **0.932** | **−24.7%** | 41.78% |

**The trade-off is monotonic.** Out of 25 configurations:
- PF ≥ 3.0 : **one**, at 0.27 trades/week — one trade every 26 days
- PF ≥ 2.0 : four, all between 0.27 and 0.64 trades/week
- ≥ 4 trades/week : PF 0.93 to 1.07 — break-even or losing

### Why the two ends are opposed

A high profit factor requires letting winners run far past losers, which
requires a wide stop, which means few trades and long holds. Trading daily
requires a tight stop and short holds, which caps every winner and pays
costs constantly. **They are the same dial turned in opposite directions.**

**The highest profit factor obtainable on this instrument and this data is
3.165, and it trades once every 26 days for +96.2% over 6.7 years — a
seventh of what the 2.31-trades-per-week champion returns.**

PF 4 at daily frequency is not something that has not been found yet. The
frontier says it is not there.

### What to choose instead

| if you want | run | expect |
|---|---|---|
| maximum return | 30m, trail 6.0, 2 adds | PF 1.63, +659%, 17.7% DD, ~2 trades/wk |
| maximum PF / smoothest ride | 4h, trail 24.0 | PF 3.17, +96%, **5.7% DD**, ~1 trade/month |
| balance | 4h, trail 16.0 | PF 2.06, +93%, 15.7% DD, ~0.6 trades/wk |

All three are the same code with two inputs changed.

---

## FINAL: the risk ladder, measured and shipped (2026-07-31)

User: *"give me the final strategy that gives me the most profit and
return."* Same engine, same entry, same exit — only how hard it presses.
XAUUSD 30m, full 6.7 years, gap-aware fills, selection ranked on full-period
net return then checked year by year and walk-forward before shipping.

| profile | adds | risk | TRAIN net/dd | OOS net/dd | FULL net | FULL dd | PF | worst yr |
|---|---|---|---|---|---|---|---|---|
| Conservative | 3 ATR ×2 | 1.0% | +487%/29.8 | +202%/19.5 | **+660%** | 17.7% | 1.626 | −1.5% |
| **Balanced** | 1.5 ATR ×4 | 1.0% | +487%/29.8 | +202%/19.5 | **+2,307%** | 29.8% | 1.728 | −6.3% |
| Aggressive | 1.5 ATR ×4 | 1.5% | +1,035%/42.8 | +459%/29.0 | **+8,627%** | 42.8% | 1.769 | −12.1% |
| **Maximum** | 1.5 ATR ×4 | 2.0% | +1,739%/54.5 | +859%/36.9 | **+24,712%** | 54.5% | 1.764 | −22.5% |

**All four are positive in all five walk-forward slices. All four lose only
in 2021.** Return roughly triples at each rung and so does the pain.

Year by year, net% (max drawdown within the year):

| profile | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| Conservative | +44.8/14.7 | −1.5/14.3 | +16.1/9.5 | +19.3/17.2 | +31.3/12.1 | +73.9/13.6 | +26.0/5.3 |
| Balanced | +71.3/21.0 | −6.3/24.7 | +15.9/15.9 | +40.4/25.5 | +41.2/18.1 | +156.7/19.8 | +46.4/7.6 |
| Aggressive | +112.4/30.5 | −12.1/35.7 | +22.2/23.6 | +59.7/36.3 | +61.3/26.5 | +302.0/29.1 | +100.1/13.3 |
| Maximum | +147.0/38.8 | **−22.5/45.8** | +26.4/31.7 | +77.8/45.9 | +77.9/34.1 | +496.1/38.1 | +145.3/20.1 |

**Maximum spent 2021 down 22.5% with a 45.8% intra-year drawdown.** That is
the number that decides whether it is tradeable, not the +24,712%.

Shipped as a one-click "Risk profile" selector in group ⓿, defaulting to
**Balanced** — 3.5× Conservative's return for 12 points more drawdown, and
the best return-per-drawdown step on the ladder. Maximum is one click away
and its cost is written into the tooltip.

**Caveat that travels with these numbers:** the higher rungs compound
aggressively, so their full-period figures are dominated by the last two
years. Balanced's +2,307% is not a claim about a fixed-size account — it is
1% risk compounding for 6.7 years, and it assumes every fill and every
gap behaved as modelled.

**Bug caught during this build (not shipped):** the first attempt at the
profile tooltip wrote real newlines into a Pine string literal instead of
escaped `\n`, breaking the string across 6 lines. `pine_lint` flagged it as
74 undeclared identifiers. That check exists because of BUG-015 and it paid
for itself again.

---

## EXPERT AUDIT: 35 entry × exit combinations, plus three structural audits (2026-07-31)

User: *"go full expert mode and find out any mistakes and improvement."*
Seven entry families × five exit families, ranked by the WEAKER of
train/OOS profit factor so nothing tops the list on a train-only fluke.
XAUUSD 30m, Balanced add schedule (1.5 ATR × 4, 1% risk), gap-aware fills.

### Best combinations, out-of-sample half

| entry | exit | OOS PF | OOS net | OOS DD | n | WR |
|---|---|---|---|---|---|---|
| Donchian 24 | **Donchian 160 trail** | 2.107 | +189.5% | 37.69% | 60 | 21.7% |
| Squeeze→breakout | Donchian 160 trail | 2.523 | +256.3% | 30.04% | 48 | 25.0% |
| **Pullback to fast SMA** | Donchian 160 trail | **2.764** | +243.8% | 25.09% | 54 | 22.2% |
| *Every bar the gate allows* | Donchian 160 trail | 1.914 | +162.1% | 36.21% | 73 | 17.8% |
| Donchian 24 | **Step 6→3 ATR** | 2.054 | +252.0% | **12.68%** | 149 | 29.5% |
| **Donchian 24 (shipped)** | **Chandelier 4.24 (shipped)** | **2.065** | **+212.1%** | 19.06% | 152 | 27.0% |

**The headline OOS numbers are misleading and I am not going to ship on
them.** The top rows carry 48–60 out-of-sample trades. Run over the full
period and five walk-forward slices they fall apart:

| combination | FULL PF | FULL net | FULL DD | losing slices | losing years |
|---|---|---|---|---|---|
| **shipped (Donchian + chandelier)** | 1.746 | +2,432% | 28.55% | **0/5** | **1/7** |
| Donchian + step 6→3 | 1.728 | +2,229% | 33.68% | 1/5 | 1/7 |
| Donchian + chandelier + BE | 1.715 | +2,143% | 28.60% | 0/5 | 1/7 |
| Donchian + Donchian 45 | 1.692 | +3,729% | 35.91% | 1/5 | 2/7 |
| Squeeze + step | 1.630 | +626% | 38.72% | 1/5 | 1/7 |
| Pullback + Donchian 45 | 1.530 | +829% | 30.92% | 1/5 | 2/7 |
| Donchian + Donchian 160 | **2.026** | +3,327% | **61.51%** | 1/5 | 1/7 |

**Nothing beat the shipped build on the criteria that predict live
behaviour.** It is the only combination with zero losing slices AND the
best return-per-drawdown (85.2) among the zero-loss options.

### Audit 1 — cooldown after an exit (SHIPPED)

The build could re-enter on the bar after a stop-out. Swept 0/3/10/24/48:

| cooldown | FULL PF | net | DD | OOS PF |
|---|---|---|---|---|
| 0 (before) | 1.746 | +2,432% | 28.55% | 2.065 |
| **3** | **1.751** | **+2,533%** | **27.72%** | 2.015 |
| 24 | 1.758 | +2,387% | 30.40% | **2.098** |
| 48 | 1.667 | +1,094% | 37.75% | 2.148 |

3 bars is a free improvement — more return, less drawdown, nothing worse.
**Shipped as the new default.**

### Audit 2 — the slope asymmetry (SHIPPED AS A TOGGLE, OFF)

Shorts required a falling EMA; longs were gated on nothing. Never tested.

| | FULL PF | net | DD | losing slices | losing years |
|---|---|---|---|---|---|
| as shipped | 1.746 | +2,432% | 28.55% | 0/5 | 1/7 |
| longs also need rising EMA | **1.778** | +2,456% | 33.78% | **1/5** | **0/7** |

**It trades a bad year for a bad quarter** — the losing calendar year
disappears, but a walk-forward slice turns negative and drawdown rises
5 points. Genuine trade-off, so it is a toggle, defaulted off.

### Audit 3 — is the short side worth trading?

| | FULL PF | net | DD | losing slices | losing years |
|---|---|---|---|---|---|
| long + short | 1.746 | +2,432% | 28.55% | 0/5 | 1/7 |
| LONG ONLY | **1.837** | +1,949% | **26.98%** | 0/5 | 1/7 |
| **SHORT ONLY** | **1.076** | **+14.0%** | 26.06% | **2/5** | **3/7** |

**The short side is barely profitable alone — PF 1.076 and +14% over 6.7
years — and yet removing it costs +483% of return.** Shorts earn when longs
cannot, so they compound the whole even though they are near-worthless in
isolation. That is a diversification effect, not an edge, and it is the
correct reason to keep them.

### Confirmation of the standing finding

"Every bar the gate allows" — no entry trigger at all, just enter whenever
the filters permit — scores OOS PF 1.914 with the Donchian 160 trail. The
trigger continues to contribute close to nothing. Seven entry families
tested and the ranking is driven by the EXIT in every case.

---

## ✅ DEEP BACKTEST — the cross-validation this project has been missing (2026-08-02)

The user ran the shipped build on TradingView **Premium Deep Backtesting**,
XAUUSD 30m, **Mar 20 2019 → Aug 2 2026**, Balanced profile. This is the
first time any result here has been checked against the full history rather
than the few thousand bars a chart happens to load.

| | Python (Dec 2019 → Jul 2026) | **TradingView (Mar 2019 → Aug 2026)** |
|---|---|---|
| profit factor | 1.751 | **1.694** |
| max drawdown | 27.72% | **26.10%** |
| net return | +2,533% | **+3,533.86%** |
| Sharpe | — | 0.356 |
| buy & hold (same window) | — | +325.96% max |
| outperformance | — | **+3,327.69%** |

**Profit factor agrees to 0.057. Drawdown agrees to 1.6 percentage points.**
The engine and the platform now describe the same system. Everything in this
ledger measured with `gap_fill=True` can be treated as representative.

### The return gap is the window, not an error

TradingView's deep range starts **9 months earlier** (Mar 2019 vs Dec 2019)
and ends 2 days later. At 1% risk compounding, nine extra months of a rising
gold market at the START of the curve multiplies everything after it. The
+2,533% → +3,534% difference is that, not a modelling failure.

### The trade count reconciles exactly

TradingView reported 2,517 trades; Python reports 789 positions. Both are
right and they measure different things:

| | |
|---|---|
| Python positions | 789 |
| average adds per position | 1.85 (max 4) |
| **total entry ORDERS placed** | **2,246** |
| TradingView closed records | 2,517 (10.8% above) |

**TradingView closes each ENTRY ORDER separately**, so a position that added
three times logs four closed trades. The residual 10.8% is partial closes
and the longer window. Same reason the win rates differ — 39.4% per ORDER on
TradingView against 21.7% per POSITION in Python. A pyramided position whose
early units are stopped for a loss while the runner wins can be one losing
position made of several winning orders.

**This is a documentation gap, not a bug**: the dashboard in the Pine shows
856 trades because it reads `strategy.closedtrades`, which counts orders,
while every ledger row here counts positions. Any future comparison must say
which one it means.

### Status of the project's central claim

The system is now validated end to end: research engine → Pine → TradingView
deep backtest over 7.4 years, PF 1.694, +3,534%, 26.10% drawdown, against
buy-and-hold's +325.96%. The claim that survived every test is unchanged and
is worth restating: **the entry contributes nothing measurable; the money is
in the trailing exit, the regime filters and adding to winners.**

---

## ⚠ COST STRESS TESTS — and a slippage-unit error in the shipped Pine (2026-08-02)

Three tests were proposed: commission +50%, double the spread, and
realistic gold slippage. All three were run on the Balanced profile over
the full period. Two pass comfortably. The third found the strategy's
biggest vulnerability AND a mistake in my own Pine defaults.

### Test 1 — commission +50%: PASSES

| commission | PF | net | drawdown |
|---|---|---|---|
| $0.07 (baseline) | 1.751 | +2,533% | 27.72% |
| $0.105 (+50%) | 1.723 | +2,279% | 29.29% |
| $0.14 (×2) | 1.699 | +2,063% | 31.93% |
| $0.35 (×5) | 1.535 | +1,116% | 52.69% |

Commission is not the binding constraint. Even 5× survives.

### Test 2 — double the spread: PASSES

| slippage | PF | net | drawdown |
|---|---|---|---|
| 0.05 pt | 1.751 | +2,533% | 27.72% |
| 0.10 pt (×2) | 1.714 | +2,274% | 28.85% |

### Test 3 — realistic gold slippage: THIS IS THE VULNERABILITY

| slippage | PF | net | **drawdown** |
|---|---|---|---|
| 0.20 pt | 1.641 | +1,620% | 33.40% |
| 0.50 pt | 1.452 | +715% | **52.23%** |
| 1.00 pt | 1.141 | +109% | **76.08%** |
| 1.50 pt | **0.888** | **−54%** | 88.18% |

**Break-even is roughly 1.2–1.5 points of slippage.** Return falls 23× from
0.05 to 1.0 points, and drawdown nearly triples.

**Why so sensitive:** pyramiding. Each position places ~2.85 entry orders
plus exits, so ~3,000 fills across the sample. Every fill pays the spread.
The feature that produced the returns is also what makes execution quality
the dominant risk.

Combined (commission +50% AND slippage): 0.2 pt → PF 1.624 / +1,507%;
0.5 pt → 1.428 / +656%; 1.0 pt → 1.107 / +80%.

### The error this exposed in the shipped Pine

**`slippage` in Pine is in TICKS, not points.** XAUUSD/OANDA quotes three
decimals, so mintick is 0.001:

| | ticks | points |
|---|---|---|
| shipped Pine (wrong) | 5 | **0.005** |
| research model | — | 0.05 |
| realistic retail fill | 200 | 0.20 |

**The deep backtest that returned PF 1.694 and +3,534% modelled slippage
about 40× smaller than a real fill.** Corrected: `slippage = 200`. At that
setting the honest expectation is **PF ~1.64, +1,620%, 33.4% drawdown** —
not +3,534%.

The 15m data behaves the same way, and the early years suffer most because
a fixed point cost is a larger share of price at gold 1,800 than at 4,050.

**Action for the user:** set `slippage` to your broker's actual gold spread
in ticks (0.2 pt = 200, 0.5 pt = 500) before trusting any number the script
reports, and re-run the deep backtest.

---

## ✅✅ FINAL VALIDATION — corrected slippage, window-matched (2026-08-02)

The user re-ran the deep backtest with the corrected `slippage = 200`
(0.20 points). Window Apr 2 2020 → Aug 2 2026, Balanced profile.

| | research engine | **TradingView deep** | delta |
|---|---|---|---|
| profit factor | 1.634 | **1.579** | **0.055** |
| max drawdown | 33.09% | **32.98%** | **0.11 pp** |
| net return | +983.6% | **+865.4%** | — |
| entry orders | 2,160 | **2,157** | **3 orders** |
| win rate | 21.8% (position) | 38.90% (order) | accounting |

**Drawdown agrees to a tenth of a percentage point. Order count agrees to
three orders out of 2,157.** This is the cleanest cross-validation this
project has produced, and it was only possible once the slippage units were
fixed and the windows were matched.

The remaining net-return gap is the two months TradingView runs past the
end of the research data, plus fill-price convention on the pyramid adds.

### What the corrected numbers actually are

The honest headline is no longer +3,534%. At a realistic 0.20 pt fill:

| profile | net | drawdown | PF |
|---|---|---|---|
| Conservative | +680% | 17.01% | 1.635 |
| **Balanced (shipped)** | **+1,620%** | **33.40%** | **1.641** |

against buy-and-hold's +179.1% at 29.08% drawdown over the same period.

### Why the two deep backtests disagreed with each other

| run | slippage | window | result |
|---|---|---|---|
| first | 5 ticks = 0.005 pt | Mar 2019 → Aug 2026 | PF 1.694, +3,534% |
| second | 200 ticks = 0.20 pt | Apr 2020 → Aug 2026 | PF 1.579, +865% |

Two variables moved at once — cost and window — which is why the second
looked so much worse. Isolating them: the slippage correction costs about
40% of the return; the 13 months of missing 2019–20 data costs most of the
rest. Neither is a defect in the strategy.

**Status: validated.** Research engine, Pine implementation and TradingView
agree on profit factor, drawdown and order count at realistic costs.

---

## 🏁 DEFINITIVE VALIDATION — 7 years, realistic costs (2026-08-02)

Deep backtest, XAUUSD 30m, Balanced profile, `slippage = 200` (0.20 pt),
**Aug 2 2019 → Aug 2 2026**.

| metric | research | **TradingView** | delta |
|---|---|---|---|
| profit factor | 1.641 | **1.583** | 0.058 |
| net return | +1,620.2% | **+1,591.7%** | **28.5 pp (98.2% accurate)** |
| max drawdown | 33.40% | **33.63%** | **0.23 pp** |
| entry orders | 2,234 | **2,370** | 136 (94.3% accurate) |
| win rate | 21.8% per position | 38.65% per order | accounting difference |

**Net return agrees to 98.2% and drawdown to a quarter of a percentage
point, over seven years and 2,370 orders.** The research engine, the Pine
file and TradingView's engine now describe the same system at costs a
retail account could actually pay.

The residual 136 orders (5.7%) is the four months of 2019 that TradingView
covers and the research data does not, plus partial-close accounting.

### The three deep backtests in sequence

| run | slippage | window | PF | net | note |
|---|---|---|---|---|---|
| 1 | 0.005 pt | Mar 2019–Aug 2026 | 1.694 | +3,534% | slippage 40× too small |
| 2 | 0.20 pt | Apr 2020–Aug 2026 | 1.579 | +865% | short window |
| **3** | **0.20 pt** | **Aug 2019–Aug 2026** | **1.583** | **+1,592%** | **full and correct** |

Run 1 was optimistic on cost. Run 2 was correct on cost but lost 13 months
of history. Run 3 is both correct — and it lands within 2% of what the
research predicted.

### Final shipped figures

XAUUSD 30m, 0.20 pt slippage, $0.07/contract commission, 7 years:

| profile | net | max drawdown | PF |
|---|---|---|---|
| Conservative | +680% | 17.0% | 1.635 |
| **Balanced (default)** | **+1,592%** *(live)* | **33.6%** *(live)* | **1.583** *(live)* |
| buy & hold | +179% | 29.1% | — |

**This row closes the project's central question.** A strategy that was
retracted in July for resting on 117 trades and $34 of profit is now
validated on 2,370 orders across seven years, at realistic fills, by an
independent engine, with a deflated Sharpe of 0.9996 and a PBO of 0.099.

---

## H-PIVOT-HOLD — widen the trail on narrow-pivot sessions — **REJECTED**

**2026-08-02.** `backtest/test_pivot_hold.py`. XAUUSD 30m, 2019-12 to 2026-07,
Donchian-50 entry, chandelier trail 8.49 ATR (6.0 scaled by sqrt(30/15)),
pyramiding 1.5 ATR / max 4, risk 1.0% / short 0.75, cooldown 3,
commission $0.07 and slippage 0.20 pt per side. Narrow = prior LDN/NY-overlap
pivot width in the bottom quartile of a rolling 60 sessions (23.0% of bars).

| slice | config | n | PF | net | maxDD | ret/DD |
|---|---|---|---|---|---|---|
| FULL | base (fixed trail) | 466 | 1.218 | +172.0% | 70.22% | 2.45 |
| FULL | widen x1.25 on narrow | 455 | 1.166 | +120.7% | 68.91% | 1.75 |
| FULL | widen x1.5 on narrow | 449 | 1.239 | +218.9% | 71.61% | 3.06 |
| FULL | widen x2.0 on narrow | 448 | 1.241 | +217.7% | 72.39% | 3.01 |
| 1st half | base | 244 | 0.968 | −14.8% | 61.57% | −0.24 |
| 1st half | widen x1.5 | 232 | 1.006 | +3.2% | 61.83% | 0.05 |
| **2nd half (OOS)** | **base** | **220** | **1.615** | **+238.5%** | **28.35%** | **8.41** |
| **2nd half (OOS)** | **widen x1.5** | **215** | **1.569** | **+220.1%** | **29.68%** | **7.42** |
| **2nd half (OOS)** | **widen x2.0** | **215** | **1.569** | **+220.0%** | **29.75%** | **7.40** |

**VERDICT: REJECTED.** The full-sample gain (+46.8pp net at x1.5) comes
entirely from the first half (+18.0pp) and **reverses out of sample**
(−18.4pp net, −0.046 PF, +1.33pp drawdown). Every widening multiple is worse
than the fixed trail on the OOS half.

**A second tell, independent of the split.** The response is not monotonic in
the multiplier: x1.25 is far WORSE than base everywhere (−51.4pp full,
−61.2pp OOS) while x1.5 and x2.0 land on top of each other. A real mechanism
would strengthen with the multiplier. This is noise.

**IMPORTANT LIMITATION, stated up front.** The base here is NOT the validated
champion. It reproduces at PF 1.218 / +172.0% / 70.22% DD on 466 entries,
against the champion's PF 1.583 / +1,591.7% / 33.63% on 2,370. It omits the
EMA regime gate, the 750/2000 SMA confluence layer, the slope gate and
TP1/TP2. So this rejects the hypothesis **on a simplified proxy of the
champion**, not on the champion itself.

That caveat does not rescue the result. The hypothesis predicted a directional
improvement from a regime signal; on the OOS half the sign is wrong at every
multiple tested. A better base would have to reverse the sign, not merely
raise the level.

**What survives.** The pivot-width finding itself is unaffected — narrow
pivot ranges really do precede more directional sessions (t=+3.07, stable,
replicates OOS). What is now measured is that this does **not** convert into
P&L through trail-widening. Forecasting directionality and making money from
it are different claims, and only the first is supported.

---

## H-STRUCT-TRAIL — Dave's 21-EMA confirmed structure trail — **REJECTED as a replacement, one real effect kept**

**2026-08-02.** `backtest/exit_lab.py` `trail_mode="structure"` (built this
session; the mechanic had sat correctly extracted in
`dave_market_structure.md:107-111` and implemented in zero engines since July).
XAUUSD 30m, 2019-12 to 2026-07, Donchian-50 entry, stop 6 ATR, pyramiding
1.5 ATR / max 4, risk 1.0% / short 0.75, cooldown 3, $0.07 commission and
0.20 pt slippage per side. Baseline is the chandelier at 8.49 ATR.

| slice | exit | n | PF | net | maxDD | ret/DD |
|---|---|---|---|---|---|---|
| FULL | chandelier | 466 | 1.218 | +172.0% | 70.22% | 2.45 |
| FULL | structure aggr@3 | 852 | 1.221 | +260.8% | 59.69% | 4.37 |
| FULL | structure aggr@4 | 817 | 1.234 | +279.2% | **49.71%** | **5.62** |
| FULL | structure no-aggr | 800 | 1.170 | +169.3% | 57.23% | 2.96 |
| 1st half | chandelier | 244 | 0.968 | −14.8% | 61.57% | −0.24 |
| 1st half | structure aggr@4 | 410 | 1.078 | +43.3% | 49.71% | 0.87 |
| **OOS** | **chandelier** | **220** | **1.615** | **+238.5%** | **28.35%** | **8.41** |
| **OOS** | **structure aggr@3** | **420** | **1.417** | **+184.3%** | **24.54%** | **7.51** |
| **OOS** | **structure aggr@4** | **401** | **1.403** | **+173.0%** | **25.67%** | **6.74** |
| **OOS** | **structure no-aggr** | **392** | **1.340** | **+124.8%** | **24.76%** | **5.04** |

**VERDICT on return: REJECTED.** The full-sample gain (+107.2pp at aggr@4)
comes from the first half (+58.1pp) and reverses out of sample (−65.5pp,
PF −0.212). Risk-adjusted it also loses OOS: ret/DD 6.74 against the
chandelier's 8.41. It is not a replacement for the champion's exit.

**One effect IS robust and should be recorded rather than discarded.**
Drawdown falls in **9 of 9** slice x variant combinations, by 2.68 to 20.51
percentage points, with no exception and no sign flip:

| | aggr@3 | aggr@4 | no-aggr |
|---|---|---|---|
| FULL | −10.53 | −20.51 | −12.99 |
| 1st half | −2.71 | −11.85 | −4.73 |
| OOS | −3.81 | −2.68 | −3.59 |

Unlike H-PIVOT-HOLD, the response here is also coherent: the structure trail
roughly doubles trade count (466 -> ~820) because it cycles faster, and it
gives up return for a materially smoother equity curve. That is a real
trade-off, not noise.

**Where it may belong.** The champion ships a Conservative profile precisely
for drawdown-averse use (+680% at 17.0% DD). A lower-return, lower-drawdown
exit is exactly that profile's shape. Testing `trail_mode="structure"` inside
Conservative — rather than as a Balanced replacement — is the follow-up this
result justifies. It has NOT been run.

**Same limitation as H-PIVOT-HOLD:** the base is a simplified proxy of the
champion (PF 1.218 / 466 entries vs 1.583 / 2,370), missing the EMA regime
gate, the 750/2000 SMA confluence, the slope gate and TP1/TP2.

---

## Key-level first-passage test vs matched control — levels REAL, not TRADEABLE

**2026-08-02.** `backtest/level_reaction.py`, XAUUSD 30m, 2019-12 to 2026-07,
33 level types, 73k-80k touches per row. Control = uniform random price inside
the same bar's range. Cost $0.54/round turn = 0.146 ATR at median ATR $3.70.

| R (ATR) | n | real | control | z | breakeven | clears |
|---|---|---|---|---|---|---|
| 0.5 | 73,579 | 54.28% | 49.06% | +20.08 | 64.59% | no |
| 1.0 | 80,067 | 52.79% | 49.18% | +14.47 | 57.29% | no |
| 1.5 | 80,675 | 52.01% | 49.55% | +9.87 | 54.86% | no |
| 2.0 | 79,902 | 51.33% | 49.56% | +7.06 | 53.65% | no |
| 3.0 | 73,114 | 50.91% | 49.52% | +5.31 | 52.43% | no |

Levels beat their control at every R (z +5.31 to +20.08). None clears cost.
Edge decays with distance; the cost bar decays the other way. See
BELIEF_REGISTER for the full reading.

**Method note.** The first version of this test scored the control at a 99.94%
bounce rate — impossible, and the tell that it was broken. The control had
been placed 2-6 ATR from price, so it was never touched and resolved on
whichever side was nearer. Fixed by drawing the control uniformly from inside
the touched bar's range. Recorded because an implausible control number is a
bug signature and this one was caught by looking at it rather than by
reporting it.

---

## The four key-level methodology claims, priced from the actual entry — ALL FOUR FAIL

**2026-08-02.** `backtest/level_claims.py`. XAUUSD 30m, 2019-12 to 2026-07,
33 level types, 81,396 touches. Fade the level: enter at the touch bar's
close, stop `stop_atr` ATR beyond the level, target `rr` x the resulting risk.
Cost $0.54 round turn = 0.146 ATR.

| stop / target | cohort | n | hit | risk (ATR) | breakeven | edge (ATR) |
|---|---|---|---|---|---|---|
| 0.5 / 2R | ALL touches | 69,959 | 30.54% | 0.76 | 39.70% | −0.210 |
| 0.5 / 2R | C1 first touch | 40,962 | 30.41% | 0.80 | 39.38% | −0.216 |
| 0.5 / 2R | C1 retest | 28,997 | 30.73% | 0.71 | 40.21% | −0.201 |
| 0.5 / 2R | **C2 swept + reclaimed** | 34,762 | **33.13%** | 0.90 | 38.72% | **−0.151** |
| 0.5 / 2R | C2 plain touch | 35,197 | 27.99% | 0.63 | 41.10% | −0.246 |
| 0.5 / 2R | C3 confluence ≥2 | 22,476 | 30.77% | 0.75 | 39.79% | −0.204 |
| 0.5 / 2R | C3 isolated | 23,396 | 31.14% | 0.78 | 39.57% | −0.197 |
| 1.0 / 2R | ALL | 75,625 | 32.12% | 1.13 | 37.62% | −0.187 |
| 1.0 / 3R | ALL | 74,780 | 23.40% | 1.11 | 28.29% | −0.217 |

**Every cohort at every geometry is negative.** 21 of 21 rows.

- **C1 "untested levels are higher probability" — FALSE.** First touch 30.41%
  against retest 30.73%. No difference at any geometry.
- **C2 "sweep then reclaim → reversal" — the phenomenon is REAL, the trade is
  not.** Swept touches do reverse more often than plain ones (33.13% vs
  27.99%) — the pattern is genuinely there. But a sweep bar closes far from
  the level, so the stop-beyond-the-level is 0.90 ATR away instead of 0.63.
  You pay for the better hit rate in wider risk, and the two cancel: −0.151
  against the plain touch's −0.246. Better, still losing.
- **C3 "confluence is stronger" — FALSE, and marginally backwards.** Stacked
  levels 30.77%, isolated 31.14%. This also kills my own earlier speculation
  that confluence COUNT was the promising untested use of levels.
- **C4 "target at least 1:2 or the next level" — FALSE.** 1:2 and 1:3 are both
  negative. Asymmetric payoffs do not rescue it.

### METHOD CORRECTION — the first run reported a false positive

The first version measured target and stop as distances from the LEVEL rather
than from the ENTRY. On that basis C2 appeared to CLEAR at all three
geometries, with edges of +0.243, +0.220 and +0.248 ATR on ~35,000 samples —
a large, consistent, entirely spurious result that was one step from being
reported as a tradeable ICT edge.

The flaw: a sweep-and-reclaim bar closes furthest from the level, so pricing
from the level handed exactly that cohort a free head start it does not get in
a real fill. Repricing from the entry turned +0.220 into −0.151.

**The lesson, worth more than the result:** when a subgroup wins, check
whether it wins because of the effect or because of how the measurement is
anchored. The tell here was that the winning cohort was the one whose entry
sits furthest from the reference price.

---

## With-trend entries at key levels — the edge is the BIAS FILTER, not the levels

**2026-08-02.** `backtest/level_with_trend.py`. XAUUSD, 2019-12 to 2026-07.
The methodology's own rule: bias = close above BOTH weekly and monthly open
(bullish) or below both (bearish); buy support in a bull bias, sell resistance
in a bear bias; stop 1 ATR beyond the level; target 2R from the entry. Cost
$0.54 round turn.

This is the version the sources actually recommend, and it had never been
tested here — `level_reaction.py` and `level_claims.py` both FADE the level.

### Step 1 — with-trend beats fading, and clears on higher timeframes

| timeframe | cost (ATR) | with-trend edge | OOS half | verdict |
|---|---|---|---|---|
| 30m | 0.146 | −0.122 | −0.115 | no |
| 4H | 0.052 | **+0.085** | **+0.081** | clears |
| 1D | 0.022 | **+0.261** | **+0.323** | clears |

With-trend beat the fade at every timeframe (30m: −0.122 vs the fade's
−0.187). The sources' directional advice is correct. And the gross edge grows
about tenfold from 30m to daily (+0.047 → +0.513 ATR on longs), the same shape
the inside-bar test found independently.

### Step 2 — the control kills it

Same bias, same risk distribution, same 2R target, entry at a RANDOM bar
instead of at a level:

| | level touch | random bar, same bias |
|---|---|---|
| 4H all | +0.085 | **+0.135** |
| 4H longs | +0.164 | **+0.222** |
| 1D all | +0.261 | **+0.268** |
| 1D longs | +0.490 | **+0.535** |

**The control beats the level in all four comparisons.** Every bit of the
higher-timeframe result comes from the bias filter and from gold rising 182%
across the sample. Touching a key level contributes nothing, and is if
anything marginally worse than entering at an arbitrary bar in the same
regime.

The long/short split says the same thing: on daily, longs +0.490 and shorts
−0.108. A "close above weekly and monthly open" filter is long almost all the
time in a market that went from $1,450 to $4,090. That is beta wearing the
costume of a setup.

**VERDICT.** The complete key-level programme — fade, with-trend, sweep,
confluence, untested-level, 1:2 and 1:3 targets, three timeframes — produces
no configuration in which the LEVEL itself adds measurable value. What does
add value is a trend filter, and it can be had without any levels at all.

**Third control-driven reversal this session.** A 99.94% bounce rate exposed a
broken control; entry-vs-level pricing overturned the sweep result; and now a
random-entry control overturns this one. Each positive died on its own
control. Logged because the pattern is the finding: on this desk, an
uncontrolled positive result has never survived.

---

## "Maximum Accuracy Level-to-Level Model" rule book — backtested as written, LOSES

**2026-08-02.** `backtest/rulebook.py`. XAUUSD 15m and 30m, 2019-12 to
2026-07. All bias filters (two-day value relationship, CPR width band,
opening relationship, HTF structure) applied as specified. Entry on break of
the signal candle extreme, stop beyond the level and the candle plus 0.25 ATR,
40% scaled at T1 with stop to breakeven, remainder to T2, minimum 1:2 R:R to
T1 enforced. Cost $0.07/side commission + 0.20 pt/side slippage.

### 30-minute

| setup | n | WR | avg R | PF | max DD | total |
|---|---|---|---|---|---|---|
| 1 trend-aligned bounce | 276 | 24.6% | **−0.450** | 0.45 | 124.1R | **−124.3R** |
| 2 inside value + narrow CPR breakout | **4** | — | — | — | — | too few |
| 3 gap fill to CPR | 115 | 35.7% | +0.022 | 1.03 | 25.3R | +2.5R |
| **combined** | **395** | **27.6%** | **−0.319** | **0.59** | **126.3R** | **−125.9R** |
| first half | 198 | 31.3% | −0.219 | 0.71 | 43.9R | −43.4R |
| second half (OOS) | 197 | 23.9% | −0.419 | 0.48 | 82.9R | −82.5R |

### 15-minute

| setup | n | WR | avg R | PF | max DD | total |
|---|---|---|---|---|---|---|
| 1 trend-aligned bounce | 415 | 23.6% | −0.341 | 0.59 | 147.7R | −141.3R |
| 2 inside value + narrow CPR breakout | **8** | — | — | — | — | too few |
| 3 gap fill to CPR | 158 | 34.8% | −0.068 | 0.90 | 24.9R | −10.8R |
| **combined** | **581** | **26.3%** | **−0.276** | **0.65** | **164.5R** | **−160.2R** |
| first half | 291 | 24.7% | −0.362 | 0.56 | 104.1R | −105.4R |
| second half (OOS) | 290 | 27.9% | −0.189 | 0.75 | 66.6R | −54.8R |

### Three findings

**1. Setup 1 is the loss, and its own stop rule causes it.** The rule book
says "stop beyond the level + signal candle extreme + small buffer". This repo
has already measured that a level's information is LOCAL — the bounce edge is
strongest at 0.5 ATR and gone by 3 ATR (see BELIEF_REGISTER). A stop placed
just beyond the level sits inside exactly the noise band the level generates,
which is why the win rate is 24% on a setup filtered to a minimum 1:2 payoff.
The rule that is supposed to define the risk is the rule that produces it.

**2. Setup 2 fires 4 times in seven years on 30m, 8 on 15m.** Inside Value AND
narrow CPR AND open-out-of-range is a triple filter that essentially never
resolves true. The rule book calls this its "highest expansion edge"; it
cannot be validated at any sample size worth the name, and any result quoted
on it would be noise. Selectivity has a floor below which a rule stops being
testable.

**3. Setup 3 is the only one near breakeven** — PF 1.03 on 30m, 0.90 on 15m.
The gap fill toward the CPR is the least level-dependent idea in the book (it
is a gap-fade with the pivot as a target), and it is the one that does not
lose. That is consistent with everything else measured here.

**Not tested, and not silently skipped:** Setup 4 (Virgin/Naked POC) and all
Money-Zone filters (VAH/POC/VAL) require a volume profile that `levels.py`
does not have; Setup 5's "low volume on the false break" cannot be honoured
because this dataset's volume is broker tick-count, not exchange volume; and
US30 was not tested because there is no US30 data in `data/`. Three of five
setups, four of four bias filters, one of two instruments.

---

## Rule book V2 — the three fixes work, and one component SURVIVES A CONTROL

**2026-08-02.** `backtest/rulebook_v2.py`. XAUUSD 30m, 2019-12 to 2026-07.
V2's changes implemented as written: stop floor of 1.5 x ATR(14) from the
invalidation point, "Inside Value OR narrow CPR" instead of the V1 triple
filter, rejection PLUS displacement required before entry, and a trailed
runner at 1.25 ATR instead of V1's fixed second target.

### V1 vs V2

| | V1 | V2 |
|---|---|---|
| combined PF | **0.59** | **1.00** |
| combined total | −125.9R | +47.9R |
| n | 395 | 17,425 |

The three fixes moved the rule book from clearly losing to breakeven. The
stop change is doing most of it, and it was the correct diagnosis: V1's stop
sat inside the 0.5 ATR band where this repo had already measured the level's
information to live.

### Per setup (V2)

| setup | n | WR | avg R | PF | max DD | total |
|---|---|---|---|---|---|---|
| 3 gap fill to CPR | 19 | — | — | — | — | too few (see note) |
| 1 confirmed bounce | 96 | 30.2% | −0.251 | 0.66 | 43.2R | −24.1R |
| 4 failed break/sweep | 8,827 | 35.7% | −0.030 | 0.95 | 513.2R | −266.8R |
| **2 relaxed expansion** | **8,483** | **40.0%** | **+0.040** | **1.07** | 304.4R | **+336.4R** |
| combined | 17,425 | 37.8% | +0.003 | 1.00 | 713.4R | +47.9R |

### The control — and Setup 2 passes it

Setup 2 fires 8,483 times, which raised the obvious suspicion that the CPR
conditions were decorative and a "strong body" momentum filter was doing all
the work. Tested directly: same stop geometry, same management, strong body
only, **no CPR gate at all**.

| | n | WR | avg R | PF | total |
|---|---|---|---|---|---|
| Setup 2, with CPR gate | 8,483 | 40.0% | **+0.040** | **1.07** | +336.4R |
| control, no CPR gate | 24,779 | 33.1% | **−0.059** | 0.92 | −1,454.0R |
| Setup 2 first half | 4,242 | 38.5% | −0.012 | 0.98 | −52.9R |
| Setup 2 OOS half | 4,241 | 41.5% | +0.092 | 1.17 | +389.4R |
| control first half | 12,390 | 32.7% | −0.081 | 0.89 | −998.0R |
| control OOS half | 12,389 | 33.5% | −0.037 | 0.95 | −456.0R |

**The gate adds +0.099R per trade, and it beats its control in BOTH halves**
(0.98 vs 0.89, and 1.17 vs 0.95). This is the first component tested in this
session that a control did not kill.

It is coherent with the earlier pivot finding rather than independent of it:
`BELIEF_REGISTER` already records that pivot-range WIDTH forecasts session
directionality (t=+3.07 on the LDN/NY overlap, stable, replicates OOS). That
information could not be monetised as a hold-extender (H-PIVOT-HOLD,
rejected). Here the same regime information works as an ENTRY GATE on a
momentum trade. Same signal, different job, and this job it does.

### Honest limits on this result

- **PF 1.07 is not a strategy.** +0.04R per trade at 3.4 trades/day, with a
  304R maximum drawdown. It is a measured edge component, not something to
  size.
- **The halves disagree in level** (−52.9R then +389.4R) even though they
  agree in direction against the control. That instability is unexplained.
- **Setup 3's sample collapsed from 115 (V1) to 19 (V2) because of MY
  implementation**, not the rule: I required the rejection close on the very
  next bar. That is stricter than "shows early rejection of the gap extreme".
  The rule book's own top-priority setup therefore remains effectively
  untested, and that is my error to fix, not a finding about the rule.
- Setup 4 (failed break/sweep) is negative at −0.030R, consistent with the
  earlier finding that sweep-and-reclaim is a real pattern whose advantage is
  eaten by the wider entry-to-stop distance it creates.

---

## Rule book V3 — Setup A confirmed robust; Setup B is structurally wrong for gold

**2026-08-02.** `backtest/rulebook_v3.py`. XAUUSD, 2019-12 to 2026-07. V3's
stated testing priorities, run in order.

### Priority 1 — Setup B (gap fill), rejection window restored

| rejection window | n | WR | avg R | PF |
|---|---|---|---|---|
| 1 bar (V2's crippled version) | 18 | — | — | — |
| 3 bars | 19 | — | — | — |
| **6 bars (V3's fix)** | **20** | 50.0% | +0.010 | 1.04 |
| 10 bars | 20 | 50.0% | +0.010 | 1.04 |

**Loosening the window did NOT restore the sample.** 18 → 20 trades. So my V2
implementation was not the cause, and my earlier apology for it was aimed at
the wrong thing.

The real cause is structural: **gold barely gaps.** XAUUSD trades nearly 24
hours, so a "moderate overnight gap" of 0.5–3.0 ATR that also leaves the CPR
as a magnet occurs about 20 times in seven years. Setup B is an *index*
setup — it assumes a cash close and a real overnight session, which US30 has
and gold does not. It is not testable on this instrument at any window, and it
should be tested on US30 or dropped.

### Priority 2a — does the CPR gate hold across timeframes?

| timeframe | n | WR | avg R | PF | total |
|---|---|---|---|---|---|
| 15m | 10,379 | 42.6% | +0.044 | 1.09 | +458.7R |
| **30m** | **4,986** | **41.9%** | **+0.080** | **1.15** | **+398.8R** |
| 60m | 2,500 | 38.7% | +0.017 | 1.03 | +43.7R |
| 4H | 667 | 38.5% | +0.077 | 1.13 | +51.4R |

Positive on all four. Weaker evidence than a second instrument would be —
the bars overlap, so these are not independent — but real.

**V3's two-day bias alignment doubled the edge.** V2's Setup 2 returned
+0.040R at PF 1.07 on 30m; adding V3's requirement that direction agree with
the two-day relationship gives **+0.080R at PF 1.15** on the same data.

### Priority 2b — session restriction CONTRADICTS the rule book

| session | n | avg R | PF | total |
|---|---|---|---|---|
| all hours | 4,986 | +0.080 | 1.15 | **+398.8R** |
| LDN/NY overlap 13:30–16:30 | 643 | +0.024 | 1.05 | +15.4R |
| NY first 90m | 326 | +0.029 | 1.06 | +9.3R |
| London 08:00–12:00 | 839 | +0.111 | 1.20 | +92.7R |

V3 says "prefer London–New York overlap and first 90 minutes of New York."
On this instrument **both make it worse** — the overlap cuts per-trade edge
from +0.080 to +0.024. London alone is the best per-trade (+0.111) but that is
a 1-of-4 pick and should be treated as a hypothesis, not a setting. Every
session restriction cuts total return by 75–95% by discarding trades.

### Priority 2c — "narrow" is parameter-stable and MONOTONIC

| narrow definition | n | avg R | PF | total |
|---|---|---|---|---|
| bottom 20% | 3,485 | **+0.115** | **1.22** | +399.5R |
| bottom 25% | 4,033 | +0.082 | 1.15 | +330.0R |
| bottom 33% | 4,986 | +0.080 | 1.15 | +398.8R |
| bottom 40% | 5,580 | +0.058 | 1.10 | +322.7R |
| bottom 50% | 6,611 | +0.042 | 1.07 | +279.1R |

Monotonic: the narrower the CPR, the stronger the edge. That is what a real
mechanism looks like, not a spike. Total R is flat from 20% to 33%, so the
tighter definition is free.

### Best stable configuration, and its control

| | n | WR | avg R | PF | total |
|---|---|---|---|---|---|
| Setup A, narrow 20%, all hours | 3,485 | 42.6% | +0.115 | 1.22 | +399.5R |
| first half | 1,743 | 40.5% | +0.046 | 1.08 | +80.5R |
| OOS half | 1,742 | 44.7% | +0.183 | 1.36 | +319.0R |
| **control: no gate, no bias** | 21,726 | 39.2% | +0.014 | 1.02 | +306.2R |
| control first half | 10,863 | 38.3% | −0.011 | 0.98 | −121.5R |
| control OOS half | 10,863 | 40.1% | +0.039 | 1.07 | +427.7R |

The gate beats its control on per-trade edge in both halves (+0.046 vs −0.011,
and +0.183 vs +0.039) while using one sixth of the trades and one seventh of
the drawdown.

**The caution that must travel with this.** Both the gate and its control are
much stronger in the second half than the first. Something regime-level is
inflating the recent half for both arms, and until that is understood the OOS
figures should not be read as forward expectations. The gate's advantage over
its control is the durable part; the level of either arm is not.

---

## THE SECOND-INSTRUMENT TEST — the CPR gate does NOT replicate on US30

**2026-08-02.** US30 15m data added (`data/us30_15m.csv.gz`, 56,165 bars,
2019-12-02 to 2026-07-30, same window as the gold series, validated by
`inspect_csv`: no duplicates, no NaNs, OHLC sane). This is the test named as
decisive in the V3 write-up, and it comes back negative.

### Setup A (CPR-gated momentum), narrow = bottom 20%

| instrument / tf | arm | n | WR | avg R | PF | total |
|---|---|---|---|---|---|---|
| **US30 30m** | **gated** | 1,251 | 34.8% | **+0.026** | **1.04** | +32.6R |
| US30 30m | control (ungated) | 8,473 | 37.7% | **+0.057** | **1.10** | +484.9R |
| **US30 60m** | **gated** | 690 | 34.5% | **−0.046** | **0.93** | −31.9R |
| US30 60m | control (ungated) | 4,647 | 36.1% | **+0.025** | **1.04** | +114.6R |

**The control beats the gate on both US30 timeframes.** On gold the gate beat
its control by +0.099R and looked parameter-monotonic across five settings and
positive across four timeframes. None of that survives the move to a second
instrument.

The gated arm also flips sign between halves on both US30 timeframes
(30m: +0.123 then −0.071; 60m: +0.109 then −0.201), which the gold version
did not do.

**Verdict: the CPR gate is rejected.** The gold result was almost certainly
instrument-specific or an artifact that the within-instrument tests were too
weak to catch. Timeframe robustness on one instrument is NOT a substitute for
a second instrument, and this pair of results is the evidence for that
methodological point.

### Setup B (gap fill) on the instrument it was designed for

| instrument / tf | n | WR | avg R | PF | total |
|---|---|---|---|---|---|
| US30 15m | 89 | 47.2% | +0.011 | 1.03 | +1.0R |
| US30 30m | 69 | 52.2% | −0.030 | 0.87 | −2.1R |
| XAUUSD 15m | 32 | 34.4% | −0.248 | 0.42 | −7.9R |
| XAUUSD 30m | 20 | 50.0% | +0.010 | 1.04 | +0.2R |

US30 does produce 3-4x the sample gold does (89 vs 32 on 15m), which confirms
the structural read — the index gaps, gold does not. But the setup is flat to
negative even on its home instrument: +1.0R over 89 trades on 15m, −2.1R over
69 on 30m. Nothing here is tradeable, and the sample is still too small to
call it either way with confidence.

### Where the rule book stands after three versions

| version | best result | killed by |
|---|---|---|
| V1 | PF 0.59 combined | stop inside the level's noise band |
| V2 | PF 1.00 combined; Setup 2 PF 1.07 beat its control | — |
| V3 | Setup A PF 1.22 on gold, monotonic, 4 timeframes | **second instrument** |

Every component has now failed a control at some level of scrutiny. The V1→V3
progression was real and well-reasoned — the stop-floor fix and the two-day
bias alignment each produced genuine measured improvement — but the surviving
component did not generalise.

---

## Opening Range Breakout rule book — XAUUSD + US30, tested 2026-08-03

`backtest/orb.py`. US30 15m, 56,165 bars, 2019-12-02 to 2026-07-30. Gold 15m,
same window. Costs 0.20 pt slippage per side. Session handling: US30 uses the
data's own first bars per day (session series, DST-proof); gold needs an
explicit UTC start, and the fixed-hour DST drift is a stated limitation of the
gold numbers only.

**All figures below are POST-BUG-029.** The first run of this module was
inflated throughout by ambiguous bars marking out at the session close; the
pre-fix numbers are void and are not recorded here as results.

### Priority 1 — base ORB, US30, structure stop

| range | 1.5R | 2R |
|---|---|---|
| 15m | PF 0.96, avgR −0.019, n=2498 | PF 0.99, avgR −0.005, n=2498 |
| 30m | PF 1.02, avgR +0.006, n=2182 | PF 1.05, avgR +0.020, n=2182 |
| 60m | PF 1.03, avgR +0.010, n=1888 | PF 1.06, avgR +0.019, n=1888 |

### Priority 2 — same on gold

Twelve configurations (London 08:00 and NY 13:30 UTC × 15/30/60m × 1.5R/2R).
**All twelve negative**, PF 0.77 to 0.88, avgR −0.046 to −0.148. The fade is
also negative (−0.118 to −0.206), which is the signature of no directional
information at all, only cost and geometry being paid at 377–464 trades/year.

### Priorities 3–5 — US30 only, since gold had nothing to filter

| test | finding |
|---|---|
| 3 time cutoff | tighter is better at 60m, worse at 15m |
| 4 stop | midpoint is worse than full-range everywhere; ATR ≈ structure |
| 5 target | expectancy rises monotonically with target distance (1R → 3R) at both range sizes; measured-move targets lose to fixed R |

The Priority-5 monotonicity is a re-observation of this repo's exponent gap
(MFE 0.558 vs MAE 0.493), not new evidence: further targets pay because the
edge is in hold time.

### The one cell worth chasing, and its control

US30, 60m range, break must occur on the FIRST bar after the range:

| arm | n | WR | avgR | PF |
|---|---|---|---|---|
| rule book (opening hour) | 396 | 51.3% | **+0.107** | 1.31 |
| first half / OOS half | 198/198 | 53.0/49.5% | +0.075 / +0.140 | 1.24 / 1.38 |
| matched control (same range size, same 1-bar trigger, built 2–16 bars later) | 2330 | — | +0.030 | ~1.08 |
| fade | 396 | 40.2% | −0.088 | 0.79 |
| gold, same cell, LDN / NY | 449/493 | — | −0.088 / −0.038 | 0.86 / 0.89 |

Neighbours decay smoothly (cutoff 4/5/6/7 → +0.107/+0.053/+0.054/+0.029), so
it is a hill, not a spike. The fade being the near-mirror says the effect is
directional rather than an accounting artifact this time.

**But:** gap over the matched control **+0.077R, z = +1.47**, found after
searching roughly 50 grid cells. The treatment's own t-stat against zero is
+2.21. Neither clears a threshold appropriate to that much searching. And gold
is negative, so it fails the stated bar of "positive on both, or strong on one
with acceptable robustness on the other".

**STATUS: NOT VALID.** Recorded as the twelfth component tested this session
and the twelfth to fail its control.

---

## PRIORITY 1 — the champion on a second instrument (2026-08-03)

`backtest/champion.py` (new harness: the Pine's signal stack + exit_lab's
gap-aware fills, cooldown and pyramiding). Gold 30m 78,695 bars, US30 30m
28,591 bars, same window 2019-12 to 2026-07. Costs 0.07 commission + 0.20 pt
slippage per side.

**Harness fidelity:** reproduces the certificate to n=789 vs 799, Balanced PF
1.658 vs 1.641, Conservative PF 1.575 vs 1.626, average hold 44 bars vs 44.
Close enough to test with; not identical, and the residual is fill detail.

### Two defects found before any result was valid

1. **`np.floor` on position size silently rejected 788 of 789 US30 entries.**
   At $10k equity and 1% risk, one gold contract near $2,000 is affordable and
   one US30 contract near $35,000 is not, so the run reported **"n=1"** rather
   than an error. BUG-012 family. Fixed with an opt-in `frac_qty` flag; it
   defaults OFF so every prior ledger row reproduces unchanged, and both
   instruments run with it ON so the comparison is like-for-like. On gold it
   moves PF by 0.002.
2. **"Unchanged settings" is ambiguous across these two instruments.** Every
   lookback is in BARS and the Pine's auto-scale converts calendar targets to
   bars assuming continuous trading — true for gold (46 bars/day at 30m),
   false for US30 cash (13 bars/day). Both readings are reported.

### Result — Balanced profile

| | n | WR | PF | net | maxDD | ret/DD | avgR | hold | halves (PF) |
|---|---|---|---|---|---|---|---|---|---|
| **GOLD 30m** | 789 | 21.5% | **1.658** | +2,114.5% | 35.67% | 59.3 | +0.91 | 44 | 1.181 / 1.819 |
| **US30 30m BARS** (literal unchanged integers) | 316 | 21.8% | **1.304** | +163.5% | 18.31% | 8.9 | +0.28 | 38 | **1.415 / 1.248** |
| **US30 30m CLOCK** (same calendar horizons) | 529 | 20.2% | 1.008 | +4.9% | 50.59% | 0.1 | +0.01 | 36 | 1.219 / **0.860** |

Conservative profile agrees: US30 BARS PF 1.354, both halves positive
(1.376 / 1.339); US30 CLOCK PF 1.001 with a negative second half (0.856).
Core engine with adds switched off: gold PF 1.397, US30 BARS 1.336, US30 CLOCK
1.019.

### Is BARS-mode a lucky point? No — it sits on a monotone hill

Sweeping every filter horizon by a common multiple *k* of the clock-matched
value (US30 BARS-mode is k≈3.7):

| k | US30 PF | US30 DD | US30 halves | GOLD PF |
|---|---|---|---|---|
| 0.5 | 1.020 | 55.8% | 1.261 / 0.847 | 1.378 |
| 1.0 | 1.008 | 50.6% | 1.219 / 0.860 | 1.627 |
| 2.0 | 1.193 | 28.0% | 1.526 / 1.042 | 1.643 |
| 3.0 | 1.258 | 22.9% | 1.480 / 1.151 | 1.552 |
| **3.7** | **1.310** | 21.1% | 1.394 / 1.270 | 1.461 |
| 5.0 | 1.340 | 15.5% | 1.417 / 1.304 | 1.557 |
| 7.0 | 1.242 | 24.3% | 1.298 / 1.208 | 1.975 |

US30 rises monotonically to k=5 and falls after — a broad hill, with both
halves positive across k=2 through 7. Gold peaks near its native k=1–2. **The
two instruments have genuinely different natural filter horizons**, and the
unchanged integers land US30 on its hill by coincidence rather than by fitting.

### Random-timing null (30 seeds, entry replaced by a coin flip on the same filtered bars)

| | champion PF | random median PF | random range | percentile |
|---|---|---|---|---|
| GOLD | 1.658 | 1.535 | 1.368 – 1.774 | 83.3% (25/30) |
| **US30** | **1.304** | **1.079** | 0.970 – 1.186 | **100.0% (30/30)** |

**The Donchian entry carries real information on US30 and almost none on
gold.** On US30 the champion beats every one of 30 random-entry seeds and the
random median (+42.3%) barely beats buy-and-hold (+85.0% — it does not). On
gold the random median already returns +1,795%.

### Verdict: PASS — the first cross-instrument survival in this repo

Not a clean pass, and the qualifier is load-bearing:

- **What transferred:** the architecture. Low win rate (21.8% vs 21.5%), long
  holds (38 bars vs 44), positive expectancy, both halves positive, lower
  drawdown than gold, and it beats US30 buy-and-hold (+163.5% vs +85.0%).
- **What did not:** the calendar horizon. Clock-matched filters give PF 1.008
  with a losing second half. US30 needs filters ~3–5× slower in real time.
- **Honest read on magnitude:** US30's PF 1.304 and avgR +0.28 are materially
  weaker than gold's 1.658 / +0.91. This is not a second gold. It is evidence
  the *design* generalises, not that the *numbers* do.

**Recommendation: KEEP, unchanged.** No re-fitting to US30 — the instrument
test was a validation, not an optimisation, and turning it into one would
destroy what it just established.

---

## PRIORITY 1 (Gold) — trail width, decoupled from position sizing (2026-08-03)

XAUUSD 30m, 78,695 bars, Balanced adds, 0.20 pt slippage. `backtest/champion.py`.

### Harness fix first

`champion.py` was not passing `stop_atr`, so exit_lab's default of 4.0 was
used while the trail ran at 4.24. The Pine ties them (`stopDist =
atr * trailMultE` sets the opening stop AND `qty`). Fixed. Fidelity to the
certificate improved: PF 1.646 vs 1.641, net +1,779.5% vs +1,620%, DD 34.01%
vs 33.40%. The Priority-1 US30 verdict is unchanged (PF 1.305, halves
1.415/1.248).

### The premise of this priority was wrong

The brief (and my own synthesis doc) said the existing sweep is confounded
because a wider trail shrinks the position. **Measured: the leverage cap binds
on 0.0% of bars at every trail width from 3 to 20 ATR.** Position size is
purely risk-based throughout. Shrinking size as the stop widens is not a
distortion — it is what constant-fractional-risk sizing *is*. There was no
confound to remove. Retracting that claim in `WIZARDS_SYNTHESIS.md`.

### A. Coupled (Pine-faithful: stop_atr = trail_atr, constant % risk)

| trail | n | WR | PF | net | maxDD | ret/DD | avgR | hold | halves |
|---|---|---|---|---|---|---|---|---|---|
| 3.0 | 1098 | 16.3% | 1.164 | +176.7% | 66.78% | 2.7 | +0.16 | 22 | 1.022/1.324 |
| **4.24 (shipped)** | 789 | 21.5% | **1.646** | **+1,779.5%** | 34.01% | **52.3** | **+0.85** | 44 | 1.184/1.814 |
| 5.0 | 682 | 22.9% | 1.554 | +1,360.6% | 39.73% | 34.2 | +0.66 | 57 | 1.206/1.694 |
| 6.0 | 575 | 23.7% | 1.429 | +579.1% | 39.18% | 14.8 | +0.43 | 78 | 1.153/1.578 |
| 8.0 | 412 | 27.4% | 1.463 | +348.2% | 37.77% | 9.2 | +0.42 | 128 | 1.080/1.677 |
| 12.0 | 240 | 27.1% | 1.460 | +142.6% | 42.16% | 3.4 | +0.38 | 257 | 0.962/1.860 |
| 16.0 | 153 | 34.0% | 1.616 | +141.0% | 21.03% | 6.7 | +0.45 | 438 | 1.144/1.895 |
| 20.0 | 104 | 35.6% | 1.619 | +105.0% | 15.78% | 6.7 | +0.45 | 674 | 1.501/1.679 |

### B. Decoupled (stop_atr pinned at 4.24 — identical size and initial risk in every arm)

| trail | n | PF | net | maxDD | ret/DD | avgR | hold |
|---|---|---|---|---|---|---|---|
| 3.0 | 1098 | 1.173 | +124.6% | 52.32% | 2.4 | +0.16 | 22 |
| **4.24** | 789 | **1.646** | +1,779.5% | **34.01%** | **52.3** | +0.85 | 44 |
| 5.0 | 688 | 1.576 | **+2,129.9%** | 46.36% | 45.9 | +0.82 | 56 |
| 8.0 | 491 | 1.430 | +795.7% | 58.94% | 13.5 | +0.53 | 100 |
| 14.0 | 303 | 1.553 | +617.3% | 76.37% | 8.1 | +1.01 | 194 |
| 16.0 | 273 | 1.576 | +1,034.4% | 65.66% | 15.8 | +1.18 | 221 |
| 20.0 | 242 | 1.359 | +397.8% | 69.22% | 5.8 | +0.58 | 264 |

### C. Decoupled, adds OFF — the pure exit measurement

| trail | n | PF | net | maxDD | ret/DD | halves |
|---|---|---|---|---|---|---|
| 3.0 | 1098 | 1.152 | +47.2% | 15.56% | 3.0 | 1.109/1.191 |
| 4.24 | 789 | 1.389 | +174.1% | 10.45% | 16.7 | 1.393/1.386 |
| **5.0** | 688 | **1.429** | **+208.5%** | 11.35% | **18.4** | **1.439/1.423** |
| 8.0 | 491 | 1.341 | +113.4% | 19.43% | 5.8 | 1.131/1.494 |
| 14.0 | 303 | 1.397 | +86.1% | 26.15% | 3.3 | 0.861/1.777 |
| 20.0 | 242 | 1.322 | +63.1% | 26.20% | 2.4 | 0.958/1.595 |

### CORRECTION: the Pine header's trail claim does not reproduce

`gold_trend_strategy.pine:82-84` states *"stop width is the dominant variable:
2 ATR -> PF 1.05, 6 ATR -> 1.60, 14 ATR -> 1.75"*, i.e. monotonically better as
it widens. **That is not what the current build measures in any of the three
panels.** Coupled: 4.24 → 1.646 against 14.0 → 1.525. Decoupled: 4.24 → 1.646
against 14.0 → 1.553. Pure exit: peak at 5.0 → 1.429, 14.0 → 1.397. PF is
hump-shaped with a maximum at 4.24–5.0 and it *falls* beyond it.

The header's figures presumably came from an earlier config; whatever produced
them, **wider is not monotonically better in the shipped system**, and the
belief that motivated this whole priority is false. Recorded in
BELIEF_REGISTER.md.

### The stop_atr axis is leverage, not edge

| config | n | PF | net | maxDD |
|---|---|---|---|---|
| stop 8.00, risk 1.000% | 788 | 1.585 | +438.5% | 18.12% |
| stop 4.24, risk 0.530% (leverage-matched) | 789 | 1.585 | +437.3% | 18.40% |
| stop 3.00, risk 1.000% | 818 | 1.675 | +4,503.1% | 50.85% |
| stop 4.24, risk 1.413% (leverage-matched) | 789 | 1.677 | +4,650.8% | 47.23% |

Because `qty = risk% / (ATR × stop_atr)`, moving `stop_atr` is arithmetically
identical to moving `risk%`. The pairs match to 0.002 of PF. **Anything the
stop axis appears to offer is already available on the risk-profile dial**, and
presenting it as an improvement would be presenting leverage as edge.

### Verdict: KEEP 4.24 UNCHANGED

- Trail 4.24 is the best or joint-best column at **every** stop width from 3.0
  to 8.0 — a ridge across five independent rows, not a fitted point.
- It has the best return/drawdown (52.3) and the highest coupled PF (1.646).
- The only arm that beats it on any metric is trail 5.0 in the adds-off panel
  (PF 1.429 vs 1.389, ret/DD 18.4 vs 16.7, and the most stable halves in the
  entire table at 1.439/1.423) — but that advantage **reverses** once adds are
  switched on, which is how the system actually ships.
- Wider trails (12–20 ATR) do raise avgR, exactly as the exponent gap predicts,
  but they cut the sample 3–8× and push drawdown to 65–76%. The extra R is real
  and unusable.

**Recommendation: KEEP. Discard the "wider is better" hypothesis. No change to
the shipped trail width.** Net profitability was not improved by this priority,
and the honest result is that the parameter was already at its optimum.

---

## PRIORITY 2 (Gold) — pyramiding rework (2026-08-03)

XAUUSD 30m, 789 trades, trail fixed at 4.24 ATR throughout. **All figures
post-BUG-030**; the pre-fix numbers (including the champion's own baseline at
PF 1.646 / +1,779.5%) are void.

### Current behaviour, measured

| adds | n | share | WR | mean P&L | total P&L |
|---|---|---|---|---|---|
| 0 | 229 | 29.0% | 0.0% | −$340 | −$77,802 |
| 1 | 167 | 21.2% | 0.0% | −$525 | −$87,728 |
| 2 | 111 | 14.1% | 0.9% | −$554 | −$61,461 |
| 3 | 72 | 9.1% | 1.4% | −$429 | −$30,913 |
| **4** | **210** | **26.6%** | **80.0%** | **+$2,075** | **+$435,851** |

**Every profitable dollar comes from the 4-add cohort.** The other 71% of
trades lose $257,904 between them. Adds are not an amplifier bolted onto the
edge — the fully-pyramided trade *is* the edge, and everything else is the cost
of finding it.

Open risk, peak per trade as a multiple of the initial budget: median **2.16R**,
p90 4.19R, max 5.50R. **71.0% of trades exceed 1R and 54.6% exceed 2R.** The
brief's premise is confirmed.

### Results

| method | n | WR | PF | net | maxDD | ret/DD | avgR | adds/win | med open risk |
|---|---|---|---|---|---|---|---|---|---|
| **fixed 100% of q0 / entry-ATR** | 789 | 21.3% | **1.647** | **+1,996.3%** | **32.17%** | **62.06** | +0.86 | 3.99 | 2.07R |
| fixed 75% of q0 | 789 | 21.9% | 1.608 | +1,232.0% | 25.47% | 48.36 | +0.70 | 3.97 | 1.73R |
| **CURRENT (baseline)** | 789 | 21.5% | 1.623 | +1,616.7% | 36.52% | 44.27 | +0.79 | 3.98 | 2.16R |
| decay 0.85/add | 789 | 22.6% | 1.581 | +1,196.6% | 29.63% | 40.38 | +0.68 | 3.97 | 2.04R |
| fixed 50% of q0 | 789 | 22.9% | 1.562 | +716.3% | 20.64% | 34.70 | +0.54 | 3.96 | 1.37R |
| Conservative 3.0×2 | 789 | 22.9% | 1.561 | +550.8% | 18.77% | 29.35 | +0.53 | 1.94 | 1.26R |
| bounded ≤3.0R | 789 | 27.4% | 1.447 | +790.4% | 32.47% | 24.34 | +0.47 | 3.70 | 2.60R |
| bounded ≤2.0R | 789 | 28.8% | 1.418 | +391.9% | 20.36% | 19.25 | +0.35 | 3.66 | 1.60R |
| no adds | 789 | 37.1% | 1.389 | +174.1% | 10.45% | 16.66 | +0.26 | 0 | 1.00R |
| **bounded ≤1.0R (Turtle)** | 789 | 33.2% | 1.391 | **+195.7%** | 14.12% | 13.86 | +0.28 | 3.38 | 1.00R |
| current + breakeven gate | 789 | 14.2% | 1.577 | +525.2% | 33.77% | 15.55 | +0.56 | 3.92 | 1.00R |

### The Turtle-style fix fails, and it fails for a structural reason

Bounding total open risk at 1R returns **+195.7% against the no-adds +174.1%**.
Holding open risk constant is arithmetically almost the same thing as not
adding: the trail sits ~4.24 ATR below price, so each add's marginal risk is
roughly a full unit, and "keep the total at 1R" leaves nothing to add with.
Every budget level from 1.0R to 3.0R is worse than the baseline on return per
unit of drawdown (13.86–24.34 against 44.27).

**This kills the recommendation I ranked #3 in `WIZARDS_SYNTHESIS.md`**, which
cited the Turtles' bounded-risk rule. The principle is sound for a diversified
100-market portfolio where each position is one of many; on a single instrument
where 26.6% of trades carry 100% of the profit, capping the winner's size caps
the strategy. Logged in BELIEF_REGISTER.md.

### The one improvement, and its control

**Size each add at the original position size (equivalently: on the ATR at
entry) instead of on the current ATR.** Identical results either way, because
`q0 = equity·risk/(ATR_entry·stop_atr)`.

| | PF | net | maxDD | ret/DD |
|---|---|---|---|---|
| CURRENT | 1.623 | +1,616.7% | 36.52% | 44.27 |
| **candidate** | **1.647** | **+1,996.3%** | **32.17%** | **62.06** |

Better on all four. Why it works: ATR *expands* during the trends this system
lives on, so current-ATR sizing shrinks each add exactly where the trade is
working hardest. Entry-ATR sizing does not.

**Control — is it just leverage?** This is the trap Priority 1 caught on the
stop axis, where leverage-matched pairs agreed to 0.002 of PF.

| | PF | net | maxDD |
|---|---|---|---|
| baseline, risk 0.85% | 1.607 | +1,094.2% | 31.27% |
| **candidate, risk 1.00%** | **1.647** | **+1,996.3%** | 32.17% |

At matched drawdown the candidate returns **+1,996% against +1,094%** with a
higher profit factor. Pure leverage does not move PF; this does. **Not
leverage.**

**Control — second instrument.** US30 bars-mode: PF 1.274 vs baseline 1.243,
net +117.2% vs +104.0%, ret/DD 4.33 vs 4.12, both halves stable. Small, same
sign, no contradiction.

**Caveat, stated:** the fraction keeps paying past 100% (125% → PF 1.678,
200% → 1.727) with drawdown rising to 59.7%. Beyond 100% it *is* mostly the
risk dial. 100% is recommended as the principled point — one add equals one
original unit — not as a swept optimum.

### Verdict

| method | recommendation |
|---|---|
| **fixed 100% of q0 (entry-ATR sizing)** | **ADOPT** — beats baseline on PF, net, drawdown and ret/DD at matched risk, holds on US30 |
| current (current-ATR sizing) | REPLACE |
| risk-bounded / Turtle | **DISCARD** — collapses to no-adds on gold |
| breakeven gate | DISCARD — ret/DD 15.55 vs 44.27 |
| decay per add | DISCARD — strictly worse than flat |
| spacing 1.5 ATR, max 4 | KEEP — best of 16 spacing × max-adds combinations |

**Open risk is NOT fixed by this, and the honest finding is that it cannot be.**
The candidate cuts median peak open risk only 2.16R → 2.07R. Every variant that
genuinely bounded open risk at 1R (bounded, BE gate) destroyed between 67% and
88% of the return. On this instrument, *carrying 2–3R of open risk on the trades
that are working is the mechanism*, not a flaw in the implementation. The
control for that risk is the risk-profile dial, not the add rule.

---

## PRIORITY 3 (Gold) — secondary improvements (2026-08-03)

New baseline = champion + entry-ATR add sizing: **PF 1.647, +1,996.3%, DD
32.17%, ret/DD 62.06, WR 21.3%, avgR +0.86, n=789.** Trail fixed at 4.24 ATR.

**Adoption bar, fixed before any result was seen:** beat baseline on PF *and*
return/drawdown, both halves ≥1.0 and not degraded, be a plateau rather than a
spike, and survive a leverage-matched control.

### Areas tested and their outcomes

| area | range | outcome |
|---|---|---|
| 1. breakout lookback | 8–96 bars | **REJECT.** 24 (shipped) has the best ret/DD at 62.06; 32 has marginally higher PF (1.673) at ret/DD 39.0. Hump centred on the shipped value. |
| 2a. fast SMA | 192–768 | **REJECT** on control (below) |
| 2b. regime EMA | 504–2016 | **REJECT.** 1008 (shipped) best on ret/DD. |
| 2c. slow SMA | 400–3000 | **ADOPT ~630** |
| 2d. slope lookback | 24–384 | **REJECT.** 96 (shipped) best on every metric. |
| 3. volatility regime filter | 16 variants | **REJECT — all 16.** Every ATR-percentile and ATR-vs-median gate scored below baseline on ret/DD (3.6–56.1 against 62.06). |
| 4. cooldown | 0–48, plus loss-only | **ADOPT 24** |
| 5. max adds / spacing | 2–8 adds, 1.0–2.0 ATR | **REJECT.** 4 adds at 1.5 ATR remains best after control. |

### The leverage-matched control did most of the work

Each candidate at 1.0% risk against the baseline dialled to the *same
drawdown*. A change that is only leverage shows the same net at the same DD.

| candidate | PF | net | DD | baseline at same DD | verdict |
|---|---|---|---|---|---|
| sma 192 | 1.757 | +2,761.9% | 42.26% | +4,138.9% | **REJECT** |
| **sma2 2016** | **1.858** | +2,444.9% | 39.14% | **+3,692.8%** | **REJECT** |
| sma 288 | 1.712 | +2,324.8% | 33.14% | +2,272.1% | reject (+2.3%, noise) |
| max adds 5 | 1.680 | +2,229.8% | 41.80% | +4,138.9% | REJECT |
| spacing 1.0 ATR | 1.658 | +3,305.8% | 36.56% | +2,914.4% | reject (PF falls) |
| **cooldown 24** | 1.699 | **+2,526.3%** | 32.30% | +1,996.3% | **ADOPT** |
| **sma2 756** | 1.659 | **+2,615.8%** | 32.28% | +1,996.3% | **ADOPT** |

`sma2 2016` is the cautionary row: **PF 1.858, the highest in the entire study,
and it still fails** — the baseline levered to the same drawdown returns 51%
more. Profit factor alone would have adopted it.

### The two survivors stack, and the region is broad

Return/drawdown across a 6×6 grid (baseline = 62.06):

| cd \ sma2 | 400 | 504 | 630 | 756 | 880 | 1008 |
|---|---|---|---|---|---|---|
| 12 | 109.8 | 97.8 | 104.5 | 94.7 | 78.7 | 72.1 |
| 20 | 114.2 | 105.4 | 107.9 | 102.0 | 86.3 | 73.9 |
| 24 | 120.4 | 113.1 | **118.0** | 112.7 | 90.7 | 78.2 |
| 28 | 129.2 | 121.6 | 122.3 | 119.6 | 100.6 | 83.6 |
| 32 | 123.1 | 117.0 | 123.4 | 117.9 | 96.1 | 79.2 |

**36 of 36 cells beat the baseline** (min 68.2, median 101.3). That is a
plateau, not a fitted cell.

### ADOPTED CONFIGURATION — cooldown 24, slow SMA 630 (plateau centre, not the peak)

| | n | WR | PF | net | maxDD | ret/DD | avgR | halves |
|---|---|---|---|---|---|---|---|---|
| baseline | 789 | 21.3% | 1.647 | +1,996.3% | 32.17% | 62.06 | +0.86 | 1.21/1.80 |
| **adopted** | 733 | 21.7% | **1.714** | **+3,854.7%** | 32.65% | **118.05** | **+1.07** | **1.31/1.82** |

The peak cell (cd 28 / sma2 400) scores ret/DD 129.2 and is deliberately **not**
taken — 24/630 is the middle of the plateau.

**US30 confirmation, unchanged:** baseline PF 1.274 / +117.2% / DD 27.07% /
ret/DD 4.33 → adopted PF 1.333 / +155.5% / **DD 19.24%** / ret/DD **8.08**.
Both changes help individually and stack on the second instrument too.

**Caveat on the half-split:** per-half drawdown figures are not meaningful
(each half's equity curve is re-based, so the second half's DD is computed
against a much larger book). The per-half **profit factors** are the valid
comparison, and they improve on both halves.

### Pine updated

1. `coolDown` default 3 → **24**
2. slow-SMA calendar target 21d → **13d** (630 bars on 30m)
3. adds now sized on the **ATR at entry** (`atrEntry`) rather than current ATR

`pine_lint`: CLEAN.

---

## PRIORITY 4 (Gold) — aggressive exploration (2026-08-03)

Baseline: PF 1.714, +3,854.7%, DD 32.65%, ret/DD 118.05, n=733.

### A METRIC WARNING THAT CHANGES HOW THESE ARE READ

**Return/drawdown is not scale-invariant under compounding.** Dialling the
baseline's risk from 0.85% to 1.60% — changing nothing else — moves it:

| risk | net | CAGR | maxDD | ret/DD | **MAR (CAGR/DD)** |
|---|---|---|---|---|---|
| 0.85% | +2,364.7% | 61.8% | 28.33% | 83 | 2.18 |
| 1.00% | +3,854.7% | 73.7% | 32.65% | **118** | 2.26 |
| 1.15% | +6,086.0% | 85.8% | 36.79% | 165 | 2.33 |
| 1.30% | +9,311.6% | 97.9% | 40.73% | 229 | 2.40 |
| 1.60% | +19,429.0% | 120.8% | 48.09% | **404** | 2.51 |

The target of "ret/DD materially above 118" is reachable by turning one dial
and adding no edge at all. Everything below is therefore judged on **MAR at
matched drawdown**, and the raw ret/DD is reported only for continuity.

### ADOPTED — tighten the trail after a large favourable excursion

Once a trade has run 20 ATR (measured on the ATR at entry) in its favour, the
chandelier tightens from 4.24 ATR to 2.0. It is not a target and not a tight
stop: it engages only on trades already deep in profit and the exit is still a
trail.

| | PF | net | CAGR | maxDD | MAR | halves |
|---|---|---|---|---|---|---|
| baseline (risk 1.0%) | 1.714 | +3,854.7% | 73.7% | 32.65% | 2.26 | 1.31/1.82 |
| **tightened (risk 1.0%)** | **1.834** | **+5,921.9%** | 85.1% | 33.80% | **2.52** | **1.35/1.94** |
| baseline levered to the same DD | ~1.716 | ~+4,500% | ~78% | ~33.8% | ~2.28 | — |

**Evidence it is real, not a fit:**
- Swept 10–30 ATR × 1.5–3.0 tightening: **21 of 28 cells beat baseline**, and
  everything from 18 ATR upward is a plateau (ret/DD 140–185). 20→2.0 is inside
  the plateau, not its peak.
- Beats the leverage-matched baseline on net, PF and MAR simultaneously.
- **Improves the profit factor in 5 of 8 calendar years** (2021 0.90→0.98,
  2022 1.17→1.20, 2023 1.43→1.57, 2025 1.99→2.11, 2026 1.86→2.00), roughly
  neutral in the other three. The gain is not one trade.
- **US30, unchanged:** PF 1.469 vs 1.351, net +247.0% vs +168.4%, at an
  identical 19.32% drawdown.

### REJECTED — volatility-targeted sizing (risk ∝ median ATR% / current ATR%)

Looked strong on gold (+4,783.2%, ret/DD 141.6) and fails on inspection:
- **Profit factor is unchanged: 1.715 against the baseline's 1.714.** An
  unchanged PF with a higher return is the signature of leverage, not edge.
- MAR 2.35 at 33.79% DD against a matched baseline's ~2.28 — a rounding error.
- **It is negative on US30:** PF 1.296 vs 1.351, net +146.0% vs +168.4%.

Stacked with the tightening it does add return (+7,308.1%, MAR 2.60), but the
increment over the tightening alone is what the risk dial would have given.
**Not adopted.**

### Everything else tested

| idea | result | verdict |
|---|---|---|
| inverse vol-targeting (risk up when vol is high) | ret/DD 97–104 | REJECT |
| step risk by ATR percentile (6 variants) | MAR ≤ 2.35, PF falls | REJECT |
| separate cooldown after wins vs losses (9 variants) | all below baseline | REJECT |
| Donchian-low trail | PF 1.573, DD 45.27% | REJECT |
| continuous step trail 4.24→2.0 over 20 ATR | PF 1.425, DD 44.50% | REJECT — the *threshold* works, the gradient does not |
| asymmetric adds, pyr_risk 1.25 / 0.75 | 1.25 is leverage; 0.75 is de-risking | REJECT |
| long-only | PF 1.816 but DD 38.26%, net +2,599.8% | REJECT — a regime bet |
| tighten after 6–12 ATR | PF 1.36–1.75, below baseline | REJECT — too early is a tight stop |

### Optional secondary — short risk 0.75 → 0.50, only in combination

With the tightening adopted, cutting short size improves everything:
PF **1.866**, net +5,212.0%, DD **31.87%**, MAR **2.56**, halves **1.39/1.97** —
the best half-stability in the entire project. At risk 1.15% it gives net
**+8,586.8%** at 35.88% DD, MAR **2.66**.

**Flagged, not adopted by default.** Shrinking the short side is a partial
version of the long-only regime bet the Pine's own header warns about, the
optimum moved (0.75 → 0.50) only *after* the tightening was added, and gold
rose 1450→4100 across this sample. It is offered as a dial with that caveat
attached.

### The risk that no configuration removes

Profit is extremely concentrated: **the top 10 trades are 95.2% of net profit**
(baseline 91.2%), and the largest single trade doubles from $59,828 to
$117,991 under the tightening. This is inherent to trend following with
compounding, but it means live results will diverge from the backtest far more
than the trade count of 733 suggests.

### Final recommendation

| rank | configuration | PF | net | maxDD | MAR |
|---|---|---|---|---|---|
| **1** | baseline + tighten 20→2.0 | **1.834** | **+5,921.9%** | 33.80% | **2.52** |
| 2 | + short risk 0.50 (regime caveat) | 1.866 | +5,212.0% | 31.87% | 2.56 |
| 3 | + short risk 0.50 at risk 1.15% | 1.868 | +8,586.8% | 35.88% | 2.66 |

**#1 is what is shipped in the Pine** (`tightAfter=20`, `tightTo=2.0`).
#2 and #3 are left as dials.

---

## PRIORITY 5 (Gold) — maximum-performance push: NOTHING ADOPTED (2026-08-03)

Baseline: PF 1.834, +5,921.9%, DD 33.80%, CAGR 85.1%, **MAR 2.52**.
Roughly 50 configurations tested across five directions. **None produced
meaningful excess. The recommendation is to ship the Priority-4 build
unchanged.**

### The measurement that makes this readable — and that invalidates MAR too

Priority 4 noted that return/drawdown inflates with leverage. **MAR does the
same, just more slowly.** Dialling only `risk_pct`:

| risk | maxDD | MAR |
|---|---|---|
| 0.70% | 24.74% | 2.32 |
| 1.00% | 33.80% | **2.52** |
| 1.15% | 38.02% | 2.61 |
| 1.30% | 42.02% | 2.71 |
| 1.60% | 49.45% | 2.86 |

So every candidate is scored on **EXCESS = its MAR − the baseline's MAR at the
same drawdown**. Only positive excess is edge. Without this, six of the
configurations below "beat the baseline" and every one of them is leverage.

### Results, by excess

| direction | best variant | net | maxDD | MAR | **EXCESS** |
|---|---|---|---|---|---|
| tighten amount | 20 → 1.5 (vs 2.0) | +6,241.8% | 33.79% | 2.56 | **+0.044** |
| multi-stage tightening | 20→2.0, 50→1.0 | +6,030.3% | 33.80% | 2.53 | +0.015 |
| streak-progressive risk | +0.2/win, cap 1.5 | +6,174.9% | 34.30% | 2.51 | −0.014 |
| tighten threshold | 25 ATR | +5,836.5% | 33.82% | 2.50 | −0.013 |
| pyramid trail-gate | stop moved 1.0 ATR | +5,272.3% | 34.80% | 2.35 | −0.17 |
| more adds | max 5 | +6,401.2% | 39.17% | 2.23 | −0.415 |
| trend-continuation re-entry | waive cooldown after wins | +4,796.3% | 35.94% | 2.21 | −0.356 |
| Donchian / hybrid trail | n=30 | +2,864.7% | 42.47% | 1.56 | −1.155 |
| volatility-adaptive trail | any of 6 | ≤+2,779% | — | ≤2.03 | −0.45 to −1.68 |

**The single best result in the entire push is +0.044 MAR — a 1.7% improvement
found after ~50 configurations.** It is a genuine local hill (0.75 → −0.023,
1.0 → −0.019, 1.25 → +0.034, **1.5 → +0.044**, 1.75 → +0.012, 2.0 → 0.000) but
US30 is indifferent to it (MAR 1.07 vs 1.06). At that effect size and that
search count it is not distinguishable from noise. **Not adopted; recorded so
it is not re-searched.**

### The one candidate that looked real, and why it was rejected

`short_risk` 0.75 → 0.50 was the only variant with clearly positive excess
(+0.088, rising to +0.121 when levered). It was flagged in Priority 4 as a
possible regime bet. Three tests settled it:

1. **The short side is the BETTER side.** Standalone on gold: longs n=484,
   PF 1.806, +$384,477. **Shorts n=253, PF 1.891, +$207,712.** Shorts have a
   higher profit factor than longs and contribute 35% of net profit. Cutting
   them is cutting the more efficient book.
2. **It degrades exactly the years the strategy exists for.** Profit factor by
   year, short 0.75 → 0.50: 2021 **0.98 → 0.92**, 2026 **2.00 → 1.93** — gold's
   only two down years (−4.3% and −6.0%). Every year it improves is a rising
   year (2020, 2023, 2024, 2025).
3. **It reverses on US30**: MAR 1.14 → 1.06 → 0.98 → 0.88 as short risk falls
   from 1.0 to 0.25. Monotonically harmful.

**REJECTED.** It buys +0.088 MAR on a sample where gold went 1450 → 4100, and
pays for it in the falling markets the long+short design exists to handle.

### Honest assessment

- **Robustness of the shipped build is unchanged and good:** profit factor
  improves in 5 of 8 calendar years versus the pre-tightening version, both
  halves are strongly positive (1.35 / 1.94), and the tightening confirms on
  US30 at identical drawdown.
- **Concentration is the unfixed risk:** the top 10 trades remain ~95% of net
  profit. Nothing tested changed that, and nothing can without destroying the
  edge — it is the same structural fact recorded in Priority 2, where the
  4-add cohort carried 100% of the profit.
- **The system is at a local optimum.** Trail width (P1), add sizing (P2),
  cooldown and slow SMA (P3), tightening threshold (P4) have each now been
  swept and each sits on a plateau. Two consecutive priorities of aggressive
  search have returned one adoption and then none.

### Recommendation

**Adopt nothing. Ship the Priority-4 configuration.** The remaining levers on
gold are the risk dial — which is a decision about tolerable drawdown, not a
research finding — and time. Further parameter search on this instrument has
negative expected value: the search count is now high enough that a +0.04 MAR
result is the expected best outcome of pure noise.

---

## TRADINGVIEW DEEP BACKTEST of the Priority-5 build (2026-08-03) — VALIDATED

User ran the shipped file. XAUUSD 30m OANDA, Jan 2 2020 – Aug 3 2026, DEEP
mode, $10k, defaults.

| | research (same window) | **TradingView DEEP** | delta |
|---|---|---|---|
| profit factor | 1.827 | **1.788** | −2.1% |
| net return | +3,766.0% | **+4,054.6%** | **+7.7%** |
| max drawdown | 33.79% | **30.85%** | **−2.94 pp** |
| CAGR | 74.2% | 76.1% | +1.9 pp |
| MAR | 2.20 | **2.47** | +0.27 |
| entry orders | 2,034 | **2,020** | **−0.7%** |

**TradingView came in BETTER than the research model on net return, drawdown
and MAR, and 2.1% under on profit factor.**

### The strongest single line in this table is the order count

2,034 modelled against 2,020 reported — **0.7% over two thousand orders**. The
entry trigger, the three filters, the 24-bar cooldown and the four-deep pyramid
ladder are all firing on the same bars in both engines. That is a structural
match, not a coincidence of aggregates.

### A prediction I got wrong, and why

I told the user to expect "PF ~1.77 and +5,800%". Profit factor was right
(1.788). **The net-return figure was wrong and avoidably so: I quoted the
+5,922% from a window starting 2019-12-01, while TradingView's deep test starts
2020-01-02.** December 2019 alone is worth +5,922% → +3,766% — it sat at the
front of the compounding chain, so removing one month removes 36% of the final
figure. Corrected expectation for that window was ~+3,766%, and the actual
+4,054.6% beat it.

**Lesson for this ledger: never quote a compounded net return without its start
date.** In a system that compounds ~76% a year, the first month is worth more
than any parameter measured in this entire session.

### Reconciling the win rate — the two numbers are not in conflict

- TradingView: **40.15% (811/2,020)** — counted per **entry order**, so each of
  the four pyramid adds inside a winning position is tallied as its own winner.
- Research: **21.7% (160/737)** — counted per **round-trip position**.
- 2,034 orders ÷ 729 positions = **2.79 entries per position**, which is exactly
  what reconciles the two.

The tradeable number — the one that governs how long a losing streak feels —
is **21.7%**, not 40.15%.

### Sharpe 0.392 is expected here and is not the metric to judge on

Sharpe punishes the upside skew this system is built to harvest: the top 10
positions are ~95% of net profit, so the return distribution has a fat right
tail and Sharpe reads it as volatility. MAR 2.47 with a 30.85% drawdown is the
figure that matches lived experience. A trend follower with a 22% win rate will
essentially always show a mediocre Sharpe.

### Status

**The research engine, the Pine file and TradingView's own engine now agree on
the current build to within 2.1% on profit factor and 0.7% on order count.**
The August 2 validation was the first time this project reached that standard;
this is the second, on a build carrying four subsequent changes.

---

## PRE-LIVE VALIDATION CHECKLIST — run against the research engine (2026-08-03)

A checklist supplied by the user (from another session). Items answerable from
the research engine were run rather than left as manual TradingView steps.

| # | check | result |
|---|---|---|
| 1 | buy & hold | **PASS** — +5,921.9% at 33.80% DD against gold's +179.1% at 29.08%. 33x. |
| 2 | long vs short | **PASS** — shorts are the *better* book: PF **1.891** vs longs' 1.806, 35.1% of net profit. Not dead weight. |
| 3 | per-year / OOS split | **PASS** — train 2020-01→2023-12 PF 1.351 / +365.2%; **OOS 2024-01→2026-07 PF 1.976 / +739.4% at 20.80% DD**. OOS is the stronger half. Caveat below. |
| 4 | parameter robustness | **MIXED — see below** |
| 5 | fill realism | **ALREADY SET IN CODE** — `process_orders_on_close=true`, `calc_on_every_tick=false`. Bar magnifier is a TradingView-side toggle; recommended ON. |
| 6 | repaint | **PASS** — audited structurally, not by eye |
| 7 | sanity (capital/leverage) | see the account-size row; $25,000 minimum at current gold prices |
| + | Monte Carlo | **run — and it is the most useful item on the list** |

### 3 — the honest caveat on out-of-sample

The OOS half is the *better* half (PF 1.976 vs 1.351), which is the right
direction. But **every parameter in this build was selected with knowledge of
the full sample**, so 2024-26 is not virgin data. DSR 0.9996 and PBO 0.099 are
the defences against that and they pass; a genuinely fresh sample would still
be better than either. Forward performance from 2026-08-03 is the only true
out-of-sample this project will ever get.

### 4 — robustness is asymmetric, and this is worth knowing

Donchian ±20% and trail ±0.5, 15 cells. **All 15 stay profitable; none inverts.**
But the two dimensions behave very differently:

| | range tested | PF range | verdict |
|---|---|---|---|
| Donchian length | 19 – 29 (24 ±20%) | 1.781 – 1.859 | **flat, ±3%** |
| trail multiple | 3.74 – 4.74 (4.24 ±0.5) | 1.418 – 1.859 | **sharp, −19% / −12%** |

Fine sweep of the trail, coupled and with position size pinned:

| trail | 3.50 | 3.74 | 4.00 | **4.24** | 4.50 | 4.74 | 5.00 |
|---|---|---|---|---|---|---|---|
| PF (coupled) | 1.409 | 1.487 | 1.548 | **1.834** | 1.755 | 1.607 | 1.610 |
| PF (size pinned) | 1.411 | 1.498 | 1.549 | **1.834** | 1.768 | 1.631 | 1.618 |

Both columns dip either side of 4.24, so **it is a genuine ridge, not an
artifact of trail width also setting position size.** The entry length can be
mis-set by 20% with no consequence; the trail cannot. This does not invalidate
the build — Priority 1 swept 3–20 ATR and 4.24 won on a hill — but it is the
one parameter that must be got right, and it is the one most exposed to a
broker whose ATR differs from OANDA's.

### Monte Carlo — the actual drawdown is on the LUCKY side

Resampling per-trade **equity-relative returns** (shuffling raw dollars would be
wrong under compounding — late trades are 40x larger than early ones):

| | actual | median | 95th pct | worst |
|---|---|---|---|---|
| max drawdown, order shuffled | **33.80%** | 35.5% | 49.1% | 71.2% |
| max drawdown, bootstrapped | **33.80%** | 35.5% | 52.5% | 83.1% |

- **3.8%** of reorderings of the *same trades* exceed a 50% drawdown; 0.3% exceed 60%.
- Bootstrap net return: 5th percentile **+721%**, median +5,913%, 95th +45,625%.
- Runs ending negative: **1 in 3,000**.

**Read: 33.80% is a fortunate ordering, not a ceiling.** The trade distribution
supports drawdowns near 50% without anything being wrong. Size the account for
that, not for the backtest's headline number.

### 6 — repaint audit (structural, not visual)

| construct | count | note |
|---|---|---|
| `request.security` | 0 | no HTF calls, so no lookahead vector |
| `barstate.isrealtime` / `varip` / `timenow` | 0 | no realtime-only branches |
| `ta.highest` / `ta.lowest` | 4, **all `[1]`-offset** | a bar cannot set its own trigger |
| chandelier anchor | `high[1]` / `low[1]` | cannot move its own stop then hit it |
| `bestPx` update | line 505, **after** all `strategy.exit` calls | excursion always reads through bar i−1 |

The only textual match for "lookahead" is a comment recording BUG-019. Nothing
in this script can repaint; the reload test on TradingView should confirm it,
and if it does not, the cause is data revision on the broker feed, not the code.

---

## DRAWDOWN-CONSTRAINED FRONTIER — PF >= 1.75 at DD <= 25% (2026-08-04)

User goal: profit factor >= 1.75 (ideally >= 1.80) with max drawdown <= 25%,
maximising net return inside that box. **Answer: yes, achievable, and almost
entirely with the risk dial.**

### 1. Pure risk-% scaling — the simple leverage effect

Nothing changed except `risk_pct`:

| risk % | PF | net | maxDD | CAGR | MAR |
|---|---|---|---|---|---|
| 0.30 | 1.763 | +299.4% | 11.23% | 23.1% | 2.06 |
| 0.50 | 1.786 | +831.3% | 18.19% | 39.8% | 2.19 |
| 0.60 | 1.799 | +1,290.8% | 21.51% | 48.5% | 2.25 |
| **0.70** | **1.810** | **+1,947.6%** | **24.74%** | 57.4% | 2.32 |
| 0.85 | 1.825 | +3,464.3% | 29.38% | 71.0% | 2.42 |
| **1.00 (shipped)** | **1.834** | **+5,921.9%** | **33.80%** | 85.1% | 2.52 |
| 1.30 | 1.835 | +15,645.6% | 42.02% | 113.8% | 2.71 |

**Profit factor is almost invariant to risk — 1.763 to 1.837 across a 4x range —
while drawdown moves 11% to 42%.** The dial buys drawdown reduction at nearly no
cost in profit factor. It costs RETURN, and that is the entire trade-off.

### 2. Frontier: 208 structural configs, risk solved to hit DD = 25% exactly

Every row below is dialled to the same 25% drawdown budget, so net return is
directly comparable. 2,496 backtests executed.

| # | risk % | adds | spacing | tightening | n | WR | PF | net | DD | MAR | halves |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **D** | 0.739 | 4 | 1.50 | 30 → 1.5 | 733 | 21.7% | 1.759 | **+2,218.2%** | 24.99% | **2.41** | 1.40/1.88 |
| | 0.739 | 4 | 1.50 | 30 → 2.0 | 733 | 21.7% | 1.752 | +2,139.0% | 24.99% | 2.38 | 1.39/1.88 |
| **B** | 0.708 | 4 | 1.50 | 20 → 1.5 | 738 | 21.7% | **1.819** | +2,097.6% | 24.98% | 2.36 | 1.42/1.95 |
| **A** | 0.708 | 4 | 1.50 | **20 → 2.0** | 737 | 21.7% | **1.811** | +2,010.4% | 24.99% | 2.32 | 1.41/1.95 |
| | 0.708 | 4 | 1.50 | 20 → 2.5 | 736 | 21.7% | 1.778 | +1,925.7% | 24.99% | 2.29 | 1.40/1.91 |
| **C** | 0.662 | 4 | 1.50 | 15 → 2.0 | 743 | 21.4% | **1.844** | +1,563.8% | 24.98% | 2.10 | 1.40/2.01 |

Only **15 of 208** configs clear PF >= 1.75 at DD <= 25%; only **4** clear
PF >= 1.80. **All 15 use 4 adds**, and 11 of 15 use 1.5 ATR spacing — the
shipped structure. Fewer adds or wider spacing cannot reach the frontier.

### 3. The drawdown number is not what it looks like

Monte Carlo (3,000 reorderings) on each candidate:

| config | backtest DD | median | 75th | 95th | P(DD > 30%) |
|---|---|---|---|---|---|
| **A** 0.708, 20→2.0 | 24.99% | 26.4% | 30.6% | 37.8% | **27.3%** |
| B 0.708, 20→1.5 | 24.98% | 26.4% | 30.4% | 38.2% | 27.5% |
| **C** 0.662, 15→2.0 | 24.97% | **24.8%** | **28.6%** | **36.5%** | **19.0%** |
| D 0.739, 30→1.5 | 24.99% | 27.2% | 31.6% | 39.3% | 32.5% |
| baseline 1.00% | 33.80% | 35.5% | 40.6% | 49.3% | 81.7% |

**A 25% backtest drawdown is a ~26% median expectation with a 27% chance of
exceeding 30%.** Config C is the only candidate whose median reordering stays
under 25%, because tightening earlier (15 ATR) genuinely cuts tail risk rather
than just reducing size.

### 4. Recommended: config A — risk 0.708%, everything else unchanged

| window | n | PF | net | DD | MAR |
|---|---|---|---|---|---|
| TRAIN | 437 | 1.375 | +291.9% | 24.99% | 1.63 |
| VALIDATION | 148 | 1.493 | +51.6% | 17.43% | 2.10 |
| TEST (untouched) | 142 | 2.083 | +149.8% | 15.04% | 6.58 |
| FULL | 737 | 1.811 | +2,010.7% | 24.99% | 2.32 |

Worst year 2021 at PF 1.00 (+$46, flat). No losing year at this risk level.

**Why A over B and D:** B's advantage (+0.008 PF) is the `tighten_to` 1.5 cell
already recorded as +0.044 MAR excess, i.e. noise. D buys +10% net for a 32.5%
chance of breaching 30% drawdown. **A is the shipped strategy with one number
changed and nothing else touched.**

**If the 25% ceiling is hard rather than a preference, take C** — PF 1.844, the
highest of any candidate, +1,564%, and the only one whose *median* Monte Carlo
drawdown is still under 25%.

### 5. Direct answer

**Yes — PF ≈ 1.81 at 24.99% drawdown is achievable, and PF 1.844 at 24.97%.**
No lowering of profit factor is required to reach the drawdown target. The cost
is return: **+2,010% instead of +5,922%**, i.e. roughly a third, because
drawdown and return scale together and profit factor does not scale at all.

---

## PUSHING THE 25% DRAWDOWN FRONTIER — one genuine gain, several rejections (2026-08-04)

Starting point: config A (PF 1.811) and C (PF 1.844), both at ~25% drawdown.
Target: beat PF 1.844 without degrading the Monte Carlo drawdown distribution.

### Rejected — measured, not assumed

| idea | result | verdict |
|---|---|---|
| **Size shorts UP** (they have the higher PF: 1.891 vs longs' 1.806) | short_risk 0.75→0.9→1.0→1.25→1.5 gives PF 1.844→1.828→1.818→1.790→1.762, **monotonically worse** | REJECT |
| **Drawdown-responsive sizing** (cut risk while underwater — the McKay/Platt rule) | 12 variants; best is −20%→×0.5 at PF 1.845 against C's 1.844. A rounding difference. | REJECT |
| **Earlier/harder tightening** (8–12 ATR) | 12→2.0 gives PF 1.788, 10→2.0 gives 1.737, 8→2.0 gives 1.556 | REJECT |
| Cooldown 34+ | PF 1.922 but Monte Carlo median jumps 25.3%→27.7% and P(DD>30%) 21%→35% | REJECT |

The short-sizing result is worth stating plainly: **the short book has the
higher profit factor and sizing it up still makes the system worse.** Position
sizing and per-trade quality are not the same lever.

### ADOPTED — cooldown 24 → 30 (config E)

Cooldown was previously optimised at risk 1.0% on return/drawdown (Priority 3
chose 24). Under a **drawdown budget** the optimum moves, because a longer
cooldown removes below-average trades rather than merely reducing size.

Risk re-solved to 25% drawdown at every setting, so all rows are comparable:

| cooldown | risk % | n | PF | net | MAR | MC median | MC p95 | P(DD>30%) | years+ |
|---|---|---|---|---|---|---|---|---|---|
| 24 (C) | 0.662 | 743 | 1.844 | +1,563.8% | 2.10 | 24.8% | 35.8% | 20.6% | 8/8 |
| 26 | 0.662 | 735 | 1.857 | +1,551.0% | 2.10 | 25.0% | 36.3% | 20.2% | 8/8 |
| 28 | 0.677 | 723 | 1.877 | +1,676.7% | 2.16 | 25.2% | 36.5% | 21.0% | 8/8 |
| **30 (E)** | **0.705** | **711** | **1.945** | **+1,874.2%** | **2.26** | **25.3%** | **36.8%** | **21.4%** | 7/8 |
| 32 | 0.718 | 699 | 1.963 | +2,079.2% | 2.36 | 25.3% | 36.3% | 22.3% | 7/8 |
| 34 | 0.777 | 690 | 1.922 | +2,240.9% | 2.42 | **27.7%** | 39.3% | **35.3%** | 7/8 |

**26–32 is a plateau; 34 breaks it.** 30 is taken as the interior of the
plateau, not the peak (32 scores higher and is deliberately not chosen).

### Config E against A and C

| | risk % | n | WR | PF | net | DD | MAR | MC med | P(>30%) | years+ |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 0.708 | 737 | 21.7% | 1.811 | +2,010.4% | 24.99% | 2.32 | 26.2% | 26.3% | 8/8 |
| C | 0.662 | 743 | 21.4% | 1.844 | +1,563.8% | 24.98% | 2.10 | 24.8% | 20.6% | 8/8 |
| **E** | 0.705 | 711 | 21.7% | **1.945** | +1,874.2% | 24.98% | 2.26 | 25.3% | 21.4% | **7/8** |
| E' (22% budget) | 0.613 | 711 | 21.7% | 1.922 | +1,288.5% | 21.99% | 2.20 | **22.4%** | **9.7%** | 7/8 |
| E'' (20% budget) | 0.553 | 711 | 21.7% | 1.906 | +998.3% | 20.00% | **20.4%** | **5.0%** | 7/8 |

Splits at solved risk: E gives TRAIN 1.326 / VALID 1.623 / **TEST 2.306**
against C's 1.336 / 1.527 / 2.171 — better on both out-of-sample windows.
US30 control: cooldown 30 gives PF 1.469 against cooldown 24's 1.422.

### The cost, stated

**E turns 2021 from flat (+$46) into a small loss (−$1,296), so years-positive
falls from 8/8 to 7/8.** That is the price of +0.10 profit factor. It is a real
trade-off, not a free win.

### Recommendation

**Adopt E (cooldown 30) if the objective is profit factor; keep C if an
unbroken record of positive years matters more.** For the 20–22% drawdown zone
the user preferred, **E'' is the strongest result in this entire project on a
risk-adjusted basis**: PF 1.906 at a 20.00% drawdown, with a Monte Carlo median
of 20.4% and only a 5.0% chance of exceeding 30%. It returns +998% rather than
+5,922%, which is the honest price of that safety.

---

## LEVELS, QUARTERLY THEORY AND THE $25 GRID — full examination (2026-08-04)

**Rules and configurations executed: 51 distinct** (24 level types, 3 quarter
grids, 16 combined phase×level rules, 8 champion overlays) plus controls
(6 regime splits, 5 half-sample splits, 3 corrected nulls at 200 simulations
each, 30-seed direction randomisation). Data: XAUUSD 30m, 78,695 bars.
All levels built strictly from prior information; entries at the next bar's
open; conservative same-bar handling throughout.

### Part 1 — Level strength: no level type carries information

24 level types ranked by forward MFE/MAE after first touch (48-bar window):

| level | touches | MFE | MAE | MFE/MAE | hold% | sweep% |
|---|---|---|---|---|---|---|
| NYL | 2,593 | 3.10 | 2.79 | 1.110 | 50.6% | 50.4% |
| ASIAL | 2,577 | 3.76 | 3.42 | 1.100 | 51.5% | 51.1% |
| PDL | 2,443 | 3.07 | 2.94 | 1.045 | 52.4% | 52.1% |
| PDH | 2,817 | 2.98 | 3.26 | 0.914 | 50.5% | 50.3% |
| **Q25** | 6,274 | 2.93 | 3.13 | **0.938** | 54.8% | 54.6% |
| **Q50** | 3,221 | 2.84 | 3.20 | **0.888** | 51.9% | 51.8% |
| **Q100** | 1,692 | 2.82 | 3.21 | **0.879** | 51.3% | 51.2% |

**Median MFE/MAE across all 24 types: 0.963. Only 1 of 24 exceeds 1.10.**
Hold rates are 47–54% everywhere — coin flips. **The quarter grids are the
worst three level types tested**, all below 0.94.

**The one apparent signal is a regime artifact.** Lows outscored highs
throughout, which looked like "support holds". Split by regime:

| | UP years (2020/23/24/25) | DOWN years (2021/22/26) |
|---|---|---|
| lows (support) | **1.135** | 0.981 |
| highs (resistance) | 0.847 | 0.996 |

Support "holding" is gold's uptrend. In falling years both converge on 1.00.

### Part 2 — Quarterly Theory: the central claims do not hold

| claim | measured | verdict |
|---|---|---|
| Q3 produces the largest expansion | session **12.4%** (smallest of four); daily 14.5%; weekly 23.6% — random is 25% | **FALSE** |
| Q2 Judas sweep predicts Q3 direction | Q3 closes down 48.9% (session), 46.7% (daily) after a Q2 high sweep | **coin flip** |
| Q4 continuation | continues Q3's direction 46.6–48.9% | **coin flip** |
| Q2 sweeps Q1's extreme | 50.1% high / 45.8% low (session); 62.5% / 57.3% (daily) | true but uninformative |

The one strong pattern — daily Q4 holding 35.9% of the day's range, largest
68.9% of the time — is **12:00–18:00 UTC, i.e. the New York session.** It is
session volatility relabelled, not a time-cycle discovery.

### Part 3 — Quarter numbers: sweep-and-reclaim loses after costs

| grid | n | /yr | MFE/MAE | sweep depth | 48-bar return | **net of cost** | win% |
|---|---|---|---|---|---|---|---|
| $25 | 7,120 | 1,069 | 1.030 | 0.50 ATR | +0.098 | **−0.048** | 49.9% |
| $50 | 3,533 | 530 | 1.027 | 0.54 ATR | +0.135 | **−0.011** | 50.6% |
| $100 | 1,774 | 266 | 1.009 | 0.56 ATR | +0.126 | **−0.020** | 49.8% |

All three negative after costs. Consistent with BUG-027, which found the same
family's filter to be a constant on 79.8% of bars.

### Part 4 — Combined patterns: they are a long-bias filter, not an edge

9 of 14 phase×level rules appeared to clear costs — and **every positive one was
a reclaim of a HIGH, every negative one a LOW.** Composition check:
**98.3% of the "session ASIAH" signals are LONGS** (1.7% short).

Against the corrected null (long at a random bar in the same Q2 window — the
level removed and nothing else changed):

| pattern | treatment | control median | percentile |
|---|---|---|---|
| session ASIAH | +0.765 | +0.305 | 100% |
| daily ASIAH | +0.748 | +0.383 | 100% |
| session NYH | +0.623 | +0.296 | 96% (inside noise) |

Two clear the null on a 48-bar hold. **But the sanity row governs the reading:
an unconditional long in ANY Q2 window returns +0.459 to +0.520 ATR.** The whole
family is measuring gold's drift, filtered to be long.

### Part 5 — VERDICT: not one overlay improves the champion

All re-solved to a 25% drawdown budget so they are directly comparable to E:

| overlay | coverage | n | PF | net | MAR | MC median | P(DD>30%) |
|---|---|---|---|---|---|---|---|
| **E (no overlay)** | 100% | 711 | **1.945** | +1,877% | **2.26** | 25.4% | 21.8% |
| ASIAH reclaim, any time | 17.5% | 322 | 1.894 | +245% | 0.82 | 13.2% | 0.0% |
| ASIAH reclaim in daily Q2 | 14.9% | 283 | 1.934 | +176% | 0.66 | 11.8% | 0.0% |
| NYH reclaim | 16.5% | 411 | 1.729 | +478% | 1.21 | 23.0% | 13.1% |
| PDH reclaim | 15.6% | 397 | 1.730 | +170% | 0.64 | 13.4% | 0.1% |
| Q50 reclaim | 15.2% | 288 | 1.945 | +2,806% | 2.64 | **31.3%** | **58.3%** |
| any daily Q2 bar | 26.2% | 345 | 1.848 | +735% | 1.50 | 25.0% | 22.1% |
| any session Q2 bar | 26.0% | 496 | 1.665 | +239% | 0.80 | 16.3% | 0.6% |

**Zero overlays beat E on profit factor. Every one destroys MAR** (2.26 → 0.50–1.50)
by cutting the sample 30–80%. The low Monte Carlo drawdowns on the ASIAH rows
are not superiority — they are what trading a fifth as often at half the risk
looks like.

The Q50 row is the trap: it ties on PF and beats on MAR, and its Monte Carlo is
**catastrophic — median 31.3% against a 25% backtest path, with a 58.3% chance
of exceeding 30%.** Its historical drawdown is luck. Rejected on exactly the
criterion the brief specified.

### Final verdict

**No robust additive edge exists in level-to-level behaviour, Quarterly Theory,
or the $25/$50/$100 grid on this instrument at this timeframe.** This is now the
thirteenth through fifteenth independent family of level-based ideas to fail
controls in this project. The champion is unchanged; **config E and E'' stand.**

The single most useful positive finding is diagnostic rather than tradeable:
gold's forward drift over 48 bars is large enough (+0.46 to +0.52 ATR) that
**any** long-biased filter will appear profitable on this sample. That is the
mechanism that has made level studies look promising here for months.

---

## MAXIMUM PUSH ON THE REMAINING DEGREES OF FREEDOM (2026-08-04)

~85 configurations, each re-solved to BOTH a 25% and 20% drawdown budget, with
2,000-path Monte Carlo and a pre-2025 profit factor as the regime control.
Baseline config E: PF 1.945 / MAR 2.26 / MC median 25.3% / P(DD>30%) 21.5% /
pre-2025 PF 1.459.

### What failed

| direction | best result | verdict |
|---|---|---|
| Volatility regime filter on ENTRIES | vol rank >0.67: PF 2.018 but MAR 1.16, n cut to 373, pre-2025 PF 1.309 | REJECT — buys PF by trading half as often |
| Path-dependent trail (different width after first add) | 4.24 is optimal; 3.0 gives PF 1.335, 6.0 gives 1.569 | REJECT |
| Time-based trail tightening | best equals baseline; 48-bar version MC median 31.2% | REJECT |
| Re-entry / continuation | reentry on: PF 1.825, MAR 2.02, MC 26.5% | REJECT |
| Win-specific cooldown | identical to baseline (cooldown 30 already dominates) | no effect |
| Long/short asymmetric TRAIL width | shorts 3.5: PF 1.885 at MAR 1.49; every variant below E | REJECT |

### What worked — one effect, found three independent ways

**Scale risk UP when the market is trending hard or volatility is expanding,
DOWN otherwise.** Three unrelated definitions agree:

| definition | PF (25% budget) | vs E |
|---|---|---|
| trend strength \|close−EMA\| > 6 ATR → ×1.4 else ×0.8 (**F1**) | 2.044 | +0.099 |
| ATR(20)/ATR(200) > 1.05 → ×1.4 else ×0.6 (**F2**) | 1.974 | +0.029 |
| ATR percentile > 0.5 → ×1.3 else ×0.7 (**F3**) | 1.989 | +0.044 |
| adds allowed only when vol rank > 0.33 (**F4**) | 1.953 | +0.008 |

F1 is a **plateau, not a spike**: thresholds 3/4/5/6/7/8/10 ATR give PF 1.954,
1.954, 2.002, 2.044, 2.038, 2.046, 2.054 — every one above baseline. Scale
factors 1.2/0.9 → 1.6/0.7 give 1.996 → 2.089 monotonically.

### Candidates at both budgets

| config | budget | PF | net | MAR | MC med | P(>30%) | pre-2025 PF | years+ |
|---|---|---|---|---|---|---|---|---|
| **E** | 25% | 1.945 | +1,875% | 2.26 | 25.3% | 21.5% | 1.459 | 7/8 |
| **G1** F1×F2 | 25% | **2.005** | +2,457% | **2.51** | **24.8%** | **19.0%** | **1.513** | 7/8 |
| G2 F1×F3 | 25% | 2.086 | +2,519% | 2.53 | 25.7% | 24.0% | 1.460 | 7/8 |
| G4 F1+gated adds | 25% | 2.049 | +4,146% | **3.03** | 26.7% | 29.0% | 1.600 | 7/8 |
| G5 F1×F2+gated | 25% | 2.009 | +3,732% | 2.92 | 25.9% | 24.0% | **1.631** | 7/8 |
| **E** | 20% | 1.906 | +997% | 2.17 | 20.4% | 5.0% | 1.472 | 7/8 |
| **G1** | 20% | **1.967** | +1,250% | **2.39** | **20.0%** | 5.0% | **1.528** | 7/8 |
| G4 | 20% | **2.023** | +1,938% | **2.86** | 21.4% | 7.0% | 1.612 | **8/8** |
| G5 | 20% | 1.992 | +1,765% | 2.76 | 20.8% | 5.0% | **1.647** | 7/8 |

**G1 strictly dominates E on gold at both budgets** — higher PF, higher MAR,
*lower* Monte Carlo median and tail, better pre-2025 profit factor.

### The control that limits the claim

**US30, 25% budget:**

| config | PF | net | MAR |
|---|---|---|---|
| E | 1.469 | +320.2% | 0.96 |
| **G1** | **1.472** | +344.3% | **1.00** |
| G4 | 1.407 | +168.0% | 0.64 |

**G1 is neutral on the second instrument (+0.003 PF) and G4 is harmful
(−0.062).** Every previously adopted change — entry-ATR add sizing, cooldown 30
— showed a clear same-sign gain on US30. This one does not.

Year by year at the 20% budget, worst year: E 0.94, **G1 0.89**, G4 1.00,
G5 0.94. G1 makes 2021 slightly worse; G4 is the only config with no losing year.

### Recommendation

**G1 — ADOPT WITH A QUALIFIER.** On gold it improves every metric asked for,
including the Monte Carlo distribution, and the underlying effect is a plateau
across three independent definitions rather than one tuned cell. But it is
**neutral, not confirmed, on the second instrument**, and it slightly worsens
the worst year. That is weaker evidence than the previous two adoptions carried.

**G4 — REJECT.** The best MAR (3.03) and the only 8/8-year record, but its Monte
Carlo is worse (26.7% median, 29% tail) and it is the worst of the three on
US30. It buys return with concentration.

**Honest summary: the frontier moved a little and the evidence is thinner than
last time.** PF 1.945 → 2.005 at 25%, 1.906 → 1.967 at 20%, with a genuinely
better drawdown distribution. Roughly 85 configurations were searched to find a
3% profit-factor gain, which is close to what noise alone would produce at that
search count; the plateau structure and the pre-2025 improvement are the reasons
to believe it anyway.

---

## CAN THE WIN RATE BE RAISED? 37 filters tested (2026-08-04)

User request: raise the 21.7% win rate by filtering. Baseline config E at the
20% drawdown budget: n=711, WR 21.7%, PF 1.906, net +996%, MAR 2.17.

**24 of 37 filters raised the win rate. 18 of those 24 REDUCED risk-adjusted
return.** Full results in `research/winrate_filters.csv`.

### The trade-off, at its clearest

| | win rate | Δ | MAR | net |
|---|---|---|---|---|
| baseline | 21.7% | — | 2.17 | +996% |
| **breakeven stop after TP1** | **31.0%** | **+9.3** | **0.44** | **+76%** |

The single largest win-rate gain available costs **92% of the return**. Every
mechanism that banks profit early converts the fat right tail into a nicer hit
rate — which is the whole edge, traded away.

### The six that raised win rate AND MAR

| filter | n | WR | PF | net | MAR |
|---|---|---|---|---|---|
| **trend: \|close−EMA\| > 6 ATR** | 571 | **24.2%** | **2.278** | +1,310% | **2.44** |
| exclude New York 16–21 | 688 | 21.8% | 1.946 | +1,297% | 2.43 |
| volume rank > 0.5 | 640 | 22.0% | 1.995 | +1,276% | 2.41 |
| trend > 3 ATR | 669 | 22.4% | 1.997 | +1,242% | 2.39 |
| trend > 2 ATR | 686 | 21.7% | 1.957 | +1,197% | 2.35 |

The trend-strength family is a plateau (1/2/3/4/6 ATR all keep or improve MAR),
which is the argument for it being real rather than fitted.

### The control that limits all six

| filter | gold MAR | TEST PF | **US30 MAR** |
|---|---|---|---|
| no filter | 2.17 | 2.206 | **0.95** |
| trend > 6 ATR | 2.44 | 2.880 | **0.69** |
| volume rank > 0.5 | 2.41 | 2.553 | **0.55** |
| exclude NY 16–21 | 2.43 | 2.288 | **0.74** |

**Every one improves gold and degrades US30.** All five survive the regime
split (trend > 6 ATR: DOWN-year PF 2.251 against baseline 1.767) and all
improve the untouched gold test window — but not one is corroborated on the
second instrument. That is the signature of gold-specific fitting.

### Verdict

**REJECT all six as additions.** The best of them, trend > 6 ATR, is also the
same variable config G1 already uses for risk scaling — filtering *and* scaling
on one measurement concentrates the whole improvement in the quantity that has
repeatedly come back neutral-to-negative on the second instrument. Do one or
neither, never both.

**The structural answer.** Break-even win rate is 13.1% and the system runs at
21.7%, an 8.6-point cushion. The 21.7% exists *because* the payoff is 6.36:1;
they are the same fact stated twice. Buying 2.5 points of win rate is worth
about +0.27 MAR — real but small. Buying 9 points costs 92% of the return.

If a low hit rate is uncomfortable to trade rather than mathematically
suboptimal, the fix is the **20% drawdown budget**, not a filter.

---

## 2026-08-05 — Source-library deep research (corrected Quarterly Theory + pattern battery)

Data: `data/xauusd_15m.csv.gz`, resampled 30m, 2019-12-01 → sample end
(157,366 15m bars / 78,693 30m bars). Champion settings unchanged
(trail 4.24 ATR, short_risk 0.75, cooldown 3, comm 0.07, slip 0.20).

### Champion gated by corrected quarter (`research/qt_corrected.csv`)

| gate | n | WR% | PF | net% | DD% | PF h1 | PF h2 | verdict |
|---|---|---|---|---|---|---|---|---|
| ALL (ungated) | 789 | 21.67 | **1.626** | 1511.9 | 35.25 | — | — | baseline |
| daily Q1 (18–00 NY) | 330 | 21.21 | 1.380 | 128.9 | 49.19 | 0.945 | 1.857 | worse |
| daily Q2 (00–06 NY) | 436 | 25.46 | 1.519 | 564.9 | 37.28 | 1.281 | 1.655 | worse |
| daily Q3 (06–12 NY) | 552 | 21.38 | 1.463 | 377.9 | 45.61 | 1.135 | 1.697 | worse |
| daily Q4 (12–18 NY) | 293 | 19.80 | 1.201 | 57.2 | 34.23 | 1.066 | 1.351 | worse |
| weekly Q1 = Tue | 242 | 23.14 | 1.114 | 22.5 | 40.45 | 0.876 | 1.385 | worse |
| weekly Q2 = Wed | 264 | 18.56 | 1.065 | 17.5 | 37.12 | 1.150 | 0.971 | worse |
| weekly Q3 = Thu | 244 | 23.36 | 1.392 | 177.7 | 36.48 | 1.532 | 1.242 | worse |
| weekly Q4 = **Fri** | 224 | 22.32 | **1.825** | 332.6 | 22.21 | 1.570 | 1.960 | see DD-match |
| session Q1 | 463 | 21.60 | 1.408 | 243.4 | 42.08 | 1.151 | 1.618 | worse |
| session Q2 | 453 | 21.85 | 1.556 | 449.8 | 40.83 | 1.136 | 1.819 | worse |
| session Q3 | 412 | 21.60 | 1.529 | 374.4 | 38.98 | 1.153 | 1.764 | worse |
| session Q4 | 284 | 23.24 | 1.593 | 215.3 | 43.20 | 1.154 | 2.027 | worse |

Twelve arms scanned; one beat baseline PF. That is what noise produces.

### Drawdown-matched control on the survivor (`research/qt_friday.py`)

Risk% solved by bisection so all three arms land on 25% max DD.

| arm | risk% | n | PF | net% | DD% | **net/DD** |
|---|---|---|---|---|---|---|
| champion, all days | 0.72 | 789 | 1.589 | +678.5 | 24.89 | **27.26** |
| Friday only | 1.11 | 224 | 1.832 | +411.0 | 25.00 | 16.44 |
| drop Friday | 0.43 | 709 | 1.432 | +134.8 | 25.00 | 5.39 |

**REJECTED.** Friday-only has the higher PF and compounds 40% less at equal
risk. Dropping Friday costs 80% of the risk-adjusted return.

### Surrogate null on QT anatomy (`research/qt_null.py`, 20 return-shuffled paths)

| cycle | statistics beyond ±3σ | reading |
|---|---|---|
| weekly | **0 of 8** | no structure at all |
| daily | Q3 sets high 0.365 vs surrogate 0.188 (z **+17.4**) | real, but it is session volatility, not QT's Q2 manipulation (Q2 = 0.150) |
| session | Q1 +6.5, Q2 +5.7, Q4 −12.5 | real; the sweep-reversal z-scores are reproduced by the surrogate, i.e. geometry |

### Pattern battery (`research/source_battery.csv`) — 10 arms × 4 horizons

Forward move in ATR vs the **unconditional** move, Welch t. **Survivors at
|t| > 3: 0 of 40.** Strongest results: PIN_BEAR t = −2.87 (inverted — bearish
pins precede up moves), BIGPLAY_L_adx −0.484 ATR at 32 bars (t = −2.06,
negative as specified), FAKEY_UP +1.92 at 32 bars.

### Dollar-quarter grid (`research/source_dollar_quarter.csv`)

| level | .00 | .25 | .50 | .75 |
|---|---|---|---|---|
| touches | 78,033 | 77,985 | 77,939 | 77,973 |
| reject rate | 0.7009 | 0.7022 | 0.7023 | 0.7002 |

Blueprint claim (".00 strongest, .25/.75 often breached") **REJECTED** on
n ≈ 78k per level. Spread is 0.2 points.

### NY open (`research/source_ny_open.csv`)

| window | n | mean abs move | sign-flip rate |
|---|---|---|---|
| 09:30–10:30 NY | 3,436 | **4.998** | 0.4974 |
| all other bars | 75,257 | 2.528 | 0.5163 |

Volatility doubles; reversals are *less* frequent than baseline. "Major
reversals at the NY open" **REJECTED**; it is an expansion window.

**Net effect on the shipped system: none. No change adopted.**

### 2026-08-05 (b) — Long-form source battery (`research/source_battery2.py`)

Same data and champion settings as the 08-05 block above.

**Directional arms — forward move in ATR vs the unconditional move, Welch t.
10 arms × 4 horizons. Survivors at |t| > 3: 6, all refutations.**

| arm | horizon | n | mean ATR | uncond | edge | t |
|---|---|---|---|---|---|---|
| OCHOA_S1_in_uptrend | 32 | 1911 | −0.196 | +0.323 | **−0.519** | **−4.92** |
| HOUGAARD_above89 | 32 | 42814 | +0.448 | +0.323 | +0.125 | +4.46 |
| HOUGAARD_above89 | 16 | 42814 | +0.233 | +0.160 | +0.073 | +3.78 |
| HOUGAARD_below89 | 32 | 35761 | +0.162 (raw) | +0.323 | +0.161 short | +5.54 |
| HOUGAARD_below89 | 16 | 35777 | +0.067 (raw) | +0.160 | +0.093 short | +4.63 |
| HOUGAARD_below89 | 8 | 35780 | +0.035 (raw) | +0.081 | +0.047 short | +3.38 |
| PERSON_HCD_long | all | 4133 | — | — | — | \|t\| ≤ 2.0 |
| PERSON_JACKHAMMER | all | 1515 | — | — | — | \|t\| ≤ 1.3 |
| PERSON_SHOOTSTAR | all | 1244 | — | — | — | \|t\| ≤ 1.6 |
| DALE_POC_support/resist | all | ~1400 | — | — | — | best \|t\| 2.60 |
| OCHOA_R1_in_downtrend | all | 1675 | — | — | — | \|t\| ≤ 1.34 |

The below-89MA rows are significant only because gold's drift is *slower* there,
not negative. A short on that signal still loses to the drift.

**Ochoa pivot-width claim (`research/source_pivot_width.csv`), 2,071 days**

| band | narrowest | narrow | mid | wide | widest |
|---|---|---|---|---|---|
| days | 415 | 414 | 414 | 414 | 414 |
| mean trend-efficiency | 0.4596 | 0.4539 | 0.4542 | 0.4514 | 0.4383 |

Spearman ρ = −0.0267, **p = 0.2247**. Narrowest vs widest Welch t = +1.172,
**p = 0.2415**. Right direction, not significant.

**Regime gates at matched 25% DD (`research/source_regime_gates.csv`)**

| gate | risk% | n | PF | net% | DD% | net/DD |
|---|---|---|---|---|---|---|
| **champion, ungated** | 0.72 | 789 | 1.589 | +678.5 | 24.89 | **27.26** |
| Dale: >1 ATR from POC | 0.68 | 766 | 1.599 | +592.1 | 25.01 | 23.67 |
| Hougaard: >1 ATR from 89MA | 0.61 | 748 | 1.559 | +402.7 | 25.02 | 16.10 |
| Ochoa: inside value only | 2.56 | 74 | 1.939 | +266.6 | 25.10 | 10.62 |
| Ochoa: narrow pivot only | 0.69 | 416 | 1.794 | +261.9 | 24.91 | 10.51 |
| Ochoa: wide pivot only | 0.53 | 388 | 1.283 | +57.6 | 24.94 | 2.31 |
| Ochoa: higher/lower value | 0.33 | 599 | 1.212 | +34.4 | 25.02 | 1.37 |

Three gates beat the champion on PF; all seven lose on net/DD.

**Net effect on the shipped system: none. No change adopted.**

**Coverage gaps, stated:** Dale's Order Flow confirmation (needs a bid/ask
ladder), `agent_2_1_cluster_detector` (SEC Form 4 equities, no XAUUSD
application), the Gann material (no falsifiable mechanical rule in the text),
Hougaard's discretionary content (not mechanical).

### 2026-08-05 (c) — Scalping checklist, MTF trend-break plan, Bollinger squeeze

Data and champion settings as above. **Every arm dialled by bisection to 25%
max drawdown before comparison.** Scripts: `research/scalp_checklist.py`,
`research/mtf_plan.py`, `research/squeeze_controls.py`.

**Bollinger squeeze foreshadows expansion — CONFIRMED** (`scalp_bb_squeeze.csv`,
78,673 bars, quintiles ~15,735 each)

| band | squeeze | tight | mid | loose | wide |
|---|---|---|---|---|---|
| bandwidth | 0.0031 | 0.0050 | 0.0069 | 0.0100 | 0.0204 |
| forward 20-bar range (ATR) | **6.69** | 5.72 | 5.03 | 4.61 | 4.13 |

**Champion variants at matched 25% DD** (`scalp_variants.csv`, `mtf_plan.csv`)

| arm | risk% | n | WR% | PF | net% | net/DD |
|---|---|---|---|---|---|---|
| **squeeze gate, bw < 40th pct** | 0.96 | 458 | 24.2 | 1.863 | +1163.9 | **46.53** |
| baseline champion | 0.72 | 789 | 21.7 | 1.589 | +678.5 | 27.26 |
| hard 2R target, 50% of size | 0.75 | 789 | 21.9 | 1.573 | +675.2 | 27.13 |
| hard 2R target, 100% | 0.78 | 789 | 23.1 | 1.539 | +642.8 | 25.60 |
| TP at pivots 25/25% | 0.74 | 796 | 22.6 | 1.561 | +607.9 | 24.30 |
| TP at pivots 33/33% | 0.71 | 799 | 23.7 | 1.572 | +553.9 | 22.16 |
| hard 3R target, 50% | 0.70 | 789 | 21.7 | 1.593 | +630.0 | 25.13 |
| TP at pivots 50/25% | 0.68 | 792 | 22.0 | 1.543 | +440.0 | 17.77 |
| 4h agree + squeeze | 0.69 | 343 | 25.1 | 1.817 | +316.6 | 12.68 |
| 4h trend agreement | 0.52 | 598 | 22.7 | 1.688 | +282.1 | 11.30 |
| volume spike on break | 0.60 | 647 | 22.7 | 1.521 | +271.3 | 10.87 |
| NO volume spike (control) | 0.63 | 610 | 21.8 | 1.590 | +335.3 | 13.42 |
| TP at pivots 33/33% + BE | 0.59 | 967 | 28.6 | 1.389 | +176.8 | 7.06 |
| candle confirmation | 0.95 | 322 | 24.2 | 1.356 | +159.0 | 6.35 |
| no squeeze (control) | 0.60 | 524 | 21.0 | 1.397 | +112.0 | 4.49 |
| **stop at broken level (~0.86 ATR)** | 0.08 | 1234 | 10.0 | 1.346 | +67.8 | **2.71** |
| 4h DISagreement (control) | 0.73 | 361 | 19.7 | 1.154 | +41.6 | 1.66 |

**Squeeze-gate controls** (`squeeze_controls.csv`)

| control | result | verdict |
|---|---|---|
| halves | h1 1.180→1.420, h2 1.799→2.151 | PASS |
| down years | 2021 0.900→1.002, 2022 1.093→1.376; **2023 1.294→1.034**; 2026 n=6 | MIXED |
| **US30** | baseline PF 0.657 (n=34, bars) / 0.656 (n=38, clock) | **UNINFORMATIVE — champion has no edge on this US30 data** |
| threshold | 20th 2.45 / 30th 27.64 / 40th 46.53 / 50th 47.68 / 60th 41.86 / 70th 26.62 | PASS (plateau) |
| ATR-rank discriminant | 30th 10.22 / 40th 11.15 / 50th 8.20; corr(bw rank, ATR rank) = +0.54 | PASS — not reproduced by ATR |
| quality vs leverage | payoff 2.10:1 → 2.55:1, WR 21.8% → 24.7% | PASS |

**Directional arms** (`scalp_directional.csv`): FLIP_res_turned_support reaches
t = +5.02 at 16 bars (n = 6122) but its short-side mirror is flat (t ≤ 0.62) —
the asymmetry signature of gold's drift, so it is not claimed. Volume-spike
breaks: best |t| = 2.90 of 8 tests.

**Status: squeeze gate = CANDIDATE, not adopted. Shipped system unchanged.**
Blocking requirement: a second instrument the champion actually works on.

**Untested, stated:** checklist item 4 (trendlines) is not mechanically
specified; the reversals note contains no falsifiable rule.

### 2026-08-05 (d) — Market Traders Institute set (`research/mti_hacks.py`)

Five PDFs, ~145 pages, two of them byte-identical duplicates. Four falsifiable
claims total.

**Hack #4 — position sizing (`research/mti_risk_sizing.csv`)**

| risk/trade | n | PF | net% | max DD% | equity multiple |
|---|---|---|---|---|---|
| 0.50 | 786 | 1.555 | +303.7 | 17.70 | 4.04 |
| **0.72 (champion @ 25% DD)** | 789 | 1.588 | +665.9 | **24.67** | 7.66 |
| 1.00 | 789 | 1.626 | +1,511.9 | 35.25 | 16.12 |
| 2.00 | 789 | 1.651 | +10,840.4 | 66.58 | 109.40 |
| 3.00 | 789 | 1.574 | +26,586.4 | 81.24 | 266.86 |
| 4.00 | 789 | 1.469 | +30,211.5 | 89.23 | 303.11 |
| 5.00 | 789 | 1.390 | +26,694.6 | **94.45** | 267.95 |

PF peaks at 2% and falls thereafter; terminal multiple peaks at 4% and falls at
5%. Past the peak, extra size costs return as well as drawdown.

**Hack #6 — StochRSI(14,14,3,3) mean reversion (`mti_stochrsi.csv`)**
16 tests, best |t| = 1.38. STOCHRSI_oversold_long at 32 bars: −0.076 ATR edge,
t = −2.04 (n = 19,205) — oversold gold drifts up *less* than unconditional.

**Hack #11 — session-boundary reversal** (first 2h of each NY-anchored session)

| window | bars | sets day extreme | flip rate |
|---|---|---|---|
| Asia open 18:00 | 6,868 | 0.056 (vs 0.052) | 0.530 (vs 0.514) |
| London open 03:00 | 6,872 | 0.043 (vs 0.053) | 0.520 (vs 0.515) |
| NY open 08:00 | 6,872 | **0.086** (vs 0.049) | **0.509** (vs 0.516) |

NY open sets extremes far more often and reverses *less*. Expansion, not
reversal — corroborates the 08-05 (a) NY-open result.

**25 Tips #5 — month-end "wildcard" candles**

| window | n | mean range (ATR) | flip rate |
|---|---|---|---|
| last 3 days of month | 10,223 | 0.9903 | 0.5116 |
| rest of month | 68,472 | 0.9836 | 0.5161 |

**Net effect on the shipped system: none. No change adopted.**

### 2026-08-05 (e) — Volatility targeting as a sizing lever (`research/voltarget*.py`)

Locked spec unchanged: Donchian 12h + EMA regime + dual SMA (shorts need falling
slope) | chandelier 4.24 ATR → 2.0 after +15 ATR | no targets/time stops/BE |
4 adds × 1.5 ATR on entry ATR | cooldown 30 | sma2 630 | closed-bar only.
Gold 78,695 30m bars, 2019-12-01 → 2026-07-30 (6.66y). Every arm bisected to the
drawdown budget. MC = 2,000 shuffles of equity-relative returns.

**IMPLEMENTATION PROOF:** `A: VT ATR14` reproduces Config E to every digit
(risk 0.706, PF 1.945, MAR 2.263). A 4.24×ATR14 stop makes ATR14-targeting a
constant multiplier, absorbed by the bisection. Expected and observed.

**Main table, 25% budget**

| arm | risk% | n | PF | CAGR | MAR | MC med | P(DD>30%) | PF pre-2025 | top10 share |
|---|---|---|---|---|---|---|---|---|---|
| E (baseline) | 0.706 | 711 | 1.945 | 56.6 | 2.263 | 25.35 | 21.55% | 1.459 | 39.5% |
| G1 (baseline) | 0.708 | 711 | 2.014 | 61.4 | **2.456** | 25.23 | 21.00% | 1.483 | 41.2% |
| **G1\* (mult also on adds)** | 0.606 | 711 | 2.175 | 60.8 | 2.431 | **22.47** | **10.55%** | **1.520** | 41.4% |
| B: VT ATR20 × G1 | 0.615 | 711 | 2.154 | 60.1 | 2.402 | 22.94 | 11.95% | 1.496 | 41.4% |
| B: VT SD20d × G1 | 0.640 | 711 | 2.197 | 61.4 | 2.457 | 24.12 | 16.35% | 1.444 | 45.8% |
| A: VT SD20d | 0.764 | 711 | 1.964 | 57.4 | 2.295 | 27.00 | 31.00% | 1.398 | 42.0% |
| A: VT EWMA(0.94) | 0.687 | 711 | 1.998 | 55.7 | 2.228 | 24.58 | 18.15% | 1.458 | 40.3% |
| **A\*: VT ATR20 alone** | 0.716 | 711 | 1.919 | 55.5 | **2.218** | 26.01 | 24.40% | 1.435 | 39.3% |
| A: VT ATR50 | 0.711 | 711 | 1.862 | 51.0 | 2.042 | 26.06 | 24.85% | 1.394 | 37.5% |
| C: G1 + open-vol cap 4% | 1.017 | 713 | 1.631 | 47.2 | 1.888 | 29.78 | 48.45% | 1.297 | 33.5% |
| C: G1 + open-vol cap 2% | 0.954 | 717 | 1.507 | 26.6 | **1.077** | 23.13 | 11.75% | 1.208 | **24.2%** |

20% budget preserves every ordering (E 2.166 / G1 2.345 / G1\* 2.312 / B ATR20
2.287 / A\* 2.128). Full table in `voltarget_gold.csv`.

**DISCRIMINANT (`voltarget_discriminant.csv`) — the finding.** Volatility
targeting ISOLATED is negative: A\* MAR 2.218 against E's 2.263. The entire gain
attributed to "variant B" comes from `risk_series_adds`, i.e. applying G1's
existing regime multiplier to the pyramid adds. Layering VT on top makes every
metric slightly worse (2.431 → 2.402).

**Right tail, matched by entry bar (`voltarget_tails.csv`), ratios vs G1**

| arm | top1% | top5% | top10% | bot10% | gross win | gross loss | win/loss |
|---|---|---|---|---|---|---|---|
| G1\* | 0.915 | 0.924 | 0.917 | 0.829 | 0.907 | 0.840 | **1.080** |
| B: VT ATR20 × G1 | 0.895 | 0.902 | 0.894 | 0.816 | 0.886 | 0.829 | 1.069 |
| B: VT SD20d × G1 | 1.037 | 0.966 | 0.941 | 0.895 | 0.925 | 0.848 | 1.091 |
| **C: open-vol cap 2%** | **0.141** | **0.176** | **0.201** | 0.229 | 0.243 | 0.323 | **0.751** |

Variant C amputates the right tail: top 1% of trades retain 14% of their
baseline contribution, win rate jumps 21.7%→30.0%, top-10 share 39.5%→24.2%.
Textbook confirmation of hard finding #2.

**US30 transfer (`voltarget_us30.csv`, `g1star_us30.csv`) — the killer**

| arm | n | PF | MAR | MC med | P(DD>30%) | PF pre-2025 |
|---|---|---|---|---|---|---|
| E | 274 | 1.469 | **0.963** | 26.57 | **30.75%** | **2.051** |
| G1 | 274 | 1.455 | 0.962 | 27.60 | 36.05% | 1.907 |
| G1\* | 274 | 1.409 | 0.909 | 30.63 | **53.30%** | 1.744 |
| B: VT ATR20 × G1 | 274 | 1.408 | 0.903 | 30.73 | 53.70% | 1.725 |
| B: VT SD20d × G1 | 274 | 1.368 | 0.722 | 30.58 | 53.50% | 1.542 |

Every candidate degrades US30 on MAR, MC median, tail probability and pre-2025
PF. P(DD>30%) roughly doubles. **Adoption bar 5 fails for all of them.**

**CORRECTION TO A PRIOR ENTRY.** The 08-05 (c) note that "the champion has no
edge on US30 (PF 0.657, n=34)" described the RAW champion. The LOCKED Config E
gives **n=274, PF 1.487, +272.8%** on the same file at a flat 1% risk. The
second-instrument control IS informative under Config E — which also means the
Bollinger squeeze gate can and should be re-tested there.

**Plateau (`voltarget_plateau.csv`, `g1star_plateau.csv`)** — ATR family is a
clean monotone plateau (MAR 2.431 → 2.251 across ATR14→ATR40, no spike). But
G1\*'s own thresholds are on a SLOPE, not a peak: expThr 1.00→1.20 rises
monotonically 2.475 → 2.759, and mult 1.5/0.75 gives 2.478. Chasing that is
re-optimisation (hard finding #10) and was not pursued.

**DECISION: REJECT all volatility-targeting variants (A, B, C). No change to the
shipped system.** G1\* deferred pending a US30 result that does not degrade.

### 2026-08-05 (f) — GOLD ONLY. G1* ADOPTED; volatility targeting still rejected

User directive: "you are only working on gold remove us30." Adoption bar 5
(second-instrument transfer) withdrawn. Replaced with three gold-only controls.

**Headline, gold, both budgets (`research/g1star_goldonly.csv`)**

| arm | budget | risk% | n | PF | CAGR | MAR | MC med | P(DD>30%) | PF pre-2025 | TRAIN/VALID/TEST |
|---|---|---|---|---|---|---|---|---|---|---|
| E | 25% | 0.706 | 711 | 1.945 | 56.6 | 2.263 | 25.35 | 21.55% | 1.459 | 1.486/1.274/2.274 |
| G1 | 25% | 0.708 | 711 | 2.014 | 61.4 | **2.456** | 25.23 | 21.00% | 1.483 | 1.497/1.298/2.337 |
| **G1\*** | 25% | 0.606 | 711 | **2.175** | 60.8 | 2.431 | **22.47** | **10.55%** | **1.520** | **1.576/1.309/2.588** |
| E | 20% | 0.553 | 711 | 1.906 | 43.3 | 2.166 | 20.37 | 5.30% | 1.472 | 1.521/1.281/2.298 |
| G1 | 20% | 0.555 | 711 | 1.970 | 46.9 | **2.345** | 20.27 | 5.15% | 1.496 | 1.535/1.305/2.364 |
| **G1\*** | 20% | 0.475 | 711 | **2.114** | 46.2 | 2.312 | **17.94** | **1.55%** | **1.536** | **1.619/1.316/2.611** |

**Control 1 — year by year (`g1star_years.csv`)**

| year | change | E | G1 | G1\* |
|---|---|---|---|---|
| 2020 | +24.9% | 2.005 | 2.098 | 2.301 |
| **2021** | **−4.3%** | 0.924 | 0.910 | 0.913 |
| **2022** | **−0.3%** | 1.168 | 1.184 | **1.189** |
| 2023 | +12.8% | 1.585 | 1.562 | 1.588 |
| 2024 | +27.1% | 1.654 | 1.720 | 1.740 |
| 2025 | +64.7% | 2.390 | 2.415 | 2.607 |
| **2026** | **−6.0%** | 2.311 | 2.398 | **2.761** |

Improves in two of three down/flat years, including the largest (2026, +0.363
PF). Not a bull-market artifact.

**Control 2 — anchored walk-forward, 6 folds (`g1star_wf.csv`)**

| fold | n | E | G1 | G1\* |
|---|---|---|---|---|
| **1** | 77 | 1.010 | 0.986 | **0.879** |
| 2 | 74 | 1.865 | 1.890 | 2.073 |
| 3 | 72 | 1.175 | 1.235 | 1.286 |
| 4 | 71 | 2.092 | 2.107 | 2.204 |
| 5 | 73 | 2.509 | 2.627 | 2.913 |
| 6 | 68 | 2.285 | 2.323 | 2.602 |

Fold 1 degrades. Five of six improve.

**Control 3 — MC seed stability, 5 seeds × 5,000 paths (`g1star_mc.csv`)**

| arm | MC median | P(DD>30%) | range |
|---|---|---|---|
| E | 25.36 ± 0.029 | 21.66% ± 0.315 | 21.06–21.92 |
| G1 | 25.26 ± 0.037 | 21.12% ± 0.446 | 20.34–21.62 |
| **G1\*** | **22.43 ± 0.016** | **9.85% ± 0.306** | **9.48–10.22** |

Non-overlapping by ~10 standard deviations. The tail improvement is a property
of the return distribution, not of a seed.

**DECISION — ADOPT G1\* on gold.** Bars 1,2,3,4,6 pass; bar 5 withdrawn.
Spec and `strategies/gold_trend_G1.pine` updated (lint CLEAN, state machine
desk-checked). Risk presets re-solved: **0.606% at 25% DD, 0.475% at 20%**.

**Volatility targeting REMAINS REJECTED** — variant A fails on gold alone
(MAR 2.218 vs E 2.263) and never depended on US30.

**On the record:** G1\* failed US30 before withdrawal (P(DD>30%) 36% → 53%).
The supported claim is "better on gold", not "better".

### 2026-08-05 (g) — Standalone PWH/PWL break strategy: REJECTED

Gold 30m, 78,695 bars, 2019-12-01 → 2026-07-30 (6.66y, 349 weeks). PWH/PWL
verified non-repainting (constant within week, equal to prior completed week's
extreme for all 349 weeks). Costs 0.07/oz/side + 0.20 slippage. No pyramiding.
Fixed-fractional sizing bisected to the DD budget. `research/pwh_break.py`.

**BUG FOUND BEFORE ANY RESULT:** first signal condition `prev_close <= L + band`
fired on bars whose previous close was already inside the band on the far side
— continuation bars, not fresh breaks. 637 PWH up-breaks at tol 0.5 against the
study's 274, a **2.3× inflation**. Corrected to `prev_close < L` strictly.
Counts now reconcile exactly with the study (274+176=450 at tol 0.5,
408+295=703 at 0.25).

**DEFINITION FORK:** the study's surviving cell was `PWH break` in the break
direction — BOTH directions. The brief pairs PWH-up with PWL-down, and
`PWL break` scored edge_mm −0.008 and was rejected. Three variants run:
V1 = brief, V2 = surviving cell, V3 = long-only PWH-up.

**Top arms, 25% DD budget** (144 arms total, `research/pwh_break.csv`)

| arm | risk% | n | WR | PF | CAGR | MAR | MC med | P(DD>30%) | pre-2025 | 2021 | 2022 | 2026 | top10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V1 t0.5 time64+4ATR | 3.57 | 330 | 47.6 | 1.368 | 32.2 | **1.287** | 36.18 | **82.96%** | 1.283 | 1.051 | 1.343 | 1.213 | 59.4% |
| **V3 t0.5 trail 5ATR** | 3.13 | 192 | 44.8 | **1.840** | 29.0 | 1.159 | 20.99 | **6.96%** | **1.865** | **0.496** | 1.175 | 1.406 | 61.4% |
| V1 t0.5 trail 5ATR | 3.60 | 322 | 41.6 | 1.390 | 27.9 | 1.115 | 32.94 | 67.13% | 1.430 | 0.759 | 1.420 | 1.208 | 65.9% |
| V2 t0.25 3R tgt | 1.95 | 335 | 32.8 | 1.343 | 25.7 | 1.028 | 30.30 | 51.93% | 1.321 | 0.889 | 1.097 | 1.016 | 47.3% |
| V2 t0.5 trail 5ATR | 2.19 | 245 | 41.6 | 1.561 | 16.6 | 0.663 | 19.28 | 3.38% | 1.547 | 0.727 | 1.179 | 0.923 | 61.5% |

20% budget preserves the ordering (V1 time64 1.276, V3 trail5 1.134).

**CONTROL 1 — displaced weekly levels, 14 replicates, each re-solved to 25% DD**

| arm | real MAR | control mean | sd | min | max | percentile |
|---|---|---|---|---|---|---|
| V3 t0.5 trail 5ATR | 1.159 | 0.680 | 0.431 | 0.269 | **1.978** | 92.9th (1/14 beat it) |
| V1 t0.5 time64 | 1.287 | 0.241 | 0.356 | −0.057 | **1.304** | 92.9th (1/14 beat it) |
| V2 t0.5 trail 5ATR | 0.663 | 0.230 | 0.157 | 0.009 | 0.529 | 100th (0/14) |

**CONTROL 2 — buy and hold:** net +179.1%, CAGR 16.67%, DD 29.08%, MAR 0.573.

**RIGHT TAIL, V3 t0.5 trail 5ATR (n=192)**

| | % of gross profit | **% of NET** |
|---|---|---|
| top 1 trade | 7.0 | 15.3 |
| top 5 trades | 26.5 | **58.0** |
| top 10 trades | 41.8 | **91.6** |
| top 10% (19) | 61.4 | **134.5** |

Removing the best 5 of 192 trades cuts net to **42%** of original.

**Walk-forward, V3:** folds 1.775 / 2.615 / 2.224 / 2.321 / 2.783 / 1.212 — all
above 1, but n=16–25 per fold.

**Cost sensitivity, V3 (risk fixed 3.127%):** MAR 1.435 at zero cost → 1.159 at
0.07+0.20 → 0.980 at 0.07+0.40 → 0.831 at 0.07+0.60. Costs consume **19% of
MAR** at the desk's standard assumption and break even against buy-and-hold at
roughly double slippage.

**VERDICT: REJECT.** Bars 1 and 5 pass; bar 2 marginal; bars 3 and 4 fail.
The measurement edge was REAL but too thin and too concentrated to trade
standalone.

---

## 2026-08-05 (h) — AU200 (AUS200 CFD): all families re-tested under one protocol

**Data (recovered mid-session).** `data/au200_5m.csv.gz`, 139,898 5-minute bars,
2020-08-05 → 2026-08-04 Australia/Sydney, 6.00 years, 1,635 dates. This is the
**CapitalCom feed of Archive 2**, not Archive 3's 212,177-bar London-Strategic-Edge
feed — so Archive 3's candidates get a genuine independent test here.

Verified at load: median bar step 5.0 min; smallest close increment **0.02 pt**
(archives claim 0.1 — see bugs); **92.6% of dates carry a bar stamped exactly
10:00 local** under Australia/Sydney.

**Feed-coverage break, confirmed:** 6 distinct hours present per year 2020-2022,
23 from 2023. Any all-day walk-forward straddling 2023 compares two different
data-generating processes.

Costs: slippage floor **1.0 pt/side**, commission 0.50 AUD/order, point value 100 AUD.

### PASS 1 — baseline, 1.0 pt/side (`research/au200_pass1.csv`)

| arm | exit | n | WR% | PF | net pts | maxDD | top10 %net | yrs+ |
|---|---|---|---|---|---|---|---|---|
| A gap+ST+TBT (long) | trail no-flip | 439 | 23.9 | **1.165** | 650 | 472 | 204.2 | 4/7 |
| A gap only | trail no-flip | 1117 | 24.8 | 1.160 | 1655 | 525 | 121.3 | 5/7 |
| C AU200-BASE | flip | 1743 | 25.9 | 1.153 | 2501 | 712 | 79.3 | 5/7 |
| C AU200-BASE | trail no-flip | 992 | 24.2 | 1.151 | 1423 | 733 | 135.1 | 5/7 |
| A gap+ST+TBT (long) | flip | 856 | 24.7 | 1.133 | 1053 | 571 | 177.1 | 5/7 |
| D ST-flip+ADX25 | flip | 2898 | 25.9 | 1.106 | 2516 | 964 | 77.4 | 4/7 |
| A gap only | flip | 1977 | 25.0 | 1.077 | 1454 | 1467 | 149.1 | 4/7 |
| D TB morning scalper | flip | 1705 | 24.0 | **0.987** | −212 | 1147 | −884 | 3/7 |
| **CONTROL random-in-window** | flip | 1719 | 22.8 | **0.914** | −1401 | 2102 | — | 2/7 |
| **CONTROL buy & hold** | — | 1 | — | — | **+3,013** | — | — | — |

**Every 3-layer ATR exit arm returned PF < 1.0** (0.852–0.995). That exit
protocol is refuted on this feed.

### PASS 4a — SLIPPAGE SENSITIVITY (decisive)

| arm | exit | PF@1.0 | PF@1.5 | PF@2.0 | PF@2.5 | PF@3.0 | net@2pt |
|---|---|---|---|---|---|---|---|
| C AU200-BASE | flip | 1.153 | 1.030 | 0.908 | 0.812 | 0.734 | −1,808 |
| C AU200-BASE | no-flip | 1.151 | 1.018 | 0.904 | 0.755 | 0.610 | −933 |
| A gap+ST+TBT long | no-flip | 1.165 | 0.975 | 0.862 | 0.756 | 0.590 | −581 |
| A gap only | no-flip | 1.160 | 1.062 | 0.905 | 0.735 | 0.585 | −1,037 |
| A gap+ST+TBT long | flip | 1.133 | 1.014 | 0.872 | 0.802 | 0.691 | −1,229 |
| D ST-flip+ADX25 | flip | 1.106 | 0.992 | 0.844 | 0.754 | 0.627 | −4,649 |

**Arms above PF 1.0 at 2.0 pt/side: ZERO.** Every candidate breaks even between
1.0 and 1.5 pt of slippage.

### PASS 4b — year by year at 1.0 pt/side

| arm | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| C AU200-BASE | 1.11 | 1.30 | 1.32 | 1.00 | 1.18 | **0.96** | 1.34 |
| D ST-flip+ADX25 | **0.95** | 1.19 | 1.39 | **0.88** | 1.22 | 1.27 | **0.85** |
| A gap only | 1.33 | 1.43 | 1.25 | **0.83** | **0.96** | 1.13 | **0.79** |
| A gap+ST+TBT long | 1.60 | 1.02 | 1.11 | **0.90** | 1.36 | 1.06 | **0.94** |

### PASS 4c — time-based OOS (train to 2023-07, test from 2023-08)

| arm | exit | IS n | IS PF | OOS n | OOS PF | degradation |
|---|---|---|---|---|---|---|
| A gap+ST+TBT long | flip | 453 | 1.121 | 403 | **1.151** | −2.7% |
| C AU200-BASE | flip | 736 | 1.190 | 1007 | **1.125** | 5.5% |
| D ST-flip+ADX25 | flip | 1255 | 1.210 | 1643 | 1.009 | 16.6% |
| A gap only | flip | 842 | 1.184 | 1135 | 0.994 | 16.0% |
| C AU200-BASE | no-flip | 437 | 1.337 | 555 | 1.000 | 25.2% |
| A gap only | no-flip | 535 | 1.380 | 582 | 0.958 | 30.6% |
| A gap+ST+TBT long | no-flip | 252 | 1.363 | 187 | 0.832 | 39.0% |

**The flip mechanism HOLDS out of sample; the no-flip trail does not.** This
overturns Archive 3's claim that flip-recovery "degraded out of sample".

### PASS 4d — concentration and Monte Carlo (5 seeds × 2,000 reshuffles)

| arm | exit | n | PF | top5 %net | top10 %net | MC med DD |
|---|---|---|---|---|---|---|
| C AU200-BASE | flip | 1743 | 1.153 | **44.9** | **79.3** | 861 |
| D ST-flip+ADX25 | flip | 2898 | 1.106 | 44.9 | 77.4 | 1079 |
| A gap only | no-flip | 1117 | 1.160 | 70.9 | 121.3 | 777 |
| A gap+ST+TBT long | flip | 856 | 1.133 | 110.9 | 177.1 | 723 |
| A gap+ST+TBT long | no-flip | 439 | 1.165 | 130.9 | **204.2** | 501 |

Values above 100% mean the rest of the book is net negative.

### VERDICT: NO AU200 SYSTEM CLEARS THE ADOPTION BAR

| bar | best arm (C AU200-BASE + flip) |
|---|---|
| 1. Positive expectancy after realistic costs | **FAIL** — dies at 1.5 pt/side |
| 2. Holds in time-based OOS | PASS (1.190 → 1.125) |
| 3. Not driven by outliers | MARGINAL — top 10 of 1,743 carry 79.3% of net |
| 4. Plateau not spike | NOT REACHED (gated on bar 1) |
| 5. Not one lucky year | MARGINAL — 5/7 years positive, 2025 at 0.96 |

Also: **no arm beats buy-and-hold** (+3,013 pts) on net points.

### TBT+Flip (Archive 3, PF 2.21) — cost reconstruction

Published at **0 pts slippage**. From its own aggregates (PF 2.21, WR 9.9%,
net +12,249, fixed 5-pt stop ⇒ n_loss = gross_loss/5): n ≈ 2,247 legs,
gross win 22,372, gross loss 10,123, avg win 100.6 pts.

| slippage/side | net pts | PF |
|---|---|---|
| 0.0 | 12,227 | 2.205 |
| 1.0 | 7,732 | 1.545 |
| 2.0 | 3,238 | 1.177 |
| 2.72 | 0 | 1.000 |
| 3.0 | −1,256 | 0.944 |

Break-even ≈ **2.72 pt/side**; trade count is inferred, and at 1.5× the inferred
n break-even falls to 1.81 pt.
