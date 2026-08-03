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
