# Audit — "Micro-Q3 Smoother — GOLD [Recovered Research Logic]"

Pine v6 strategy, audited 2026-08-23 against the Dukascopy XAUUSD tick engine
(`research/microq3/code/engine.py`), which is the ground truth the script's
header numbers came from. Source archived verbatim at
`research/microq3/pine/micro_q3_smoother_v1.pine`.

Reproduce with:

```
MICROQ3_DATA=research/microq3/data          python3 research/microq3/code/pine_smoother_audit.py
MICROQ3_DATA=research/microq3/data_holdout  python3 research/microq3/code/pine_smoother_audit.py
MICROQ3_DATA=research/microq3/data          python3 research/microq3/code/pine_exec_audit.py
MICROQ3_DATA=research/microq3/data          python3 research/microq3/code/pine_fragility.py
```

---

## Verdict

The script is a faithful and careful transcription of the *stated* spec, and its
header numbers do reconcile against the tick engine. Two things are wrong with
it, one mechanical and one presentational, and the mechanical one is a repeat of
a defect already registered in this repo.

| | Finding | Severity |
|---|---|---|
| 1 | **BUG-047** — the quarter filter is wired as a search, not a filter | **defect** |
| 2 | `restrictWindow = true` by default hides the year that fails | **misleading** |
| 3 | Header claims presented as validated; they are in-sample only | **misleading** |
| 4 | Quarter filter is known-inert on gold (H105) — the script is built around it | design |
| 5 | Zero commission / zero slippage / mid fills | minor, measured |
| 6 | Dashboard hardcodes parameter strings that inputs can change | cosmetic |
| 7 | Stale-anchor path exists if the 18:45 bar is missing | latent |

Everything else checks out — see **What is correct** at the bottom.

---

## 1. BUG-047 — the quarter filter is a search, not a filter

```pine
tradePermission = inResearchWindow and insideSignalWindow and quarterOK and
     strategy.position_size == 0 and not tradedThisAnchor      // line 431

aShort = enableAShort and tradePermission and not na(bodyLow) and close < bodyLow
```

`tradedThisAnchor` is set only inside the entry blocks (lines 512, 546), so it is
set only when a trade actually fires. If the first completed close beyond the
synthetic body sits more than $6.25 from a $25 level, nothing fires, the day
stays open, and the script keeps testing 19:10, 19:15, 19:20 … until a break
lands near a quarter.

The researched rule takes the **first** break and, if it fails the quarter test,
**consumes the day** (`microq3.py`, the `continue` after the `qdist` test).

Measured on the same ticks, same fills, same SL 15.50 / TP 25.50, same 12h stop.
The Pine cannot reproduce the research's `spread <= 1.50` filter, so the clean
comparison is the middle row against the bottom row — same filters, only the
selection rule differs.

**In-sample (2025-08-20 → 2026-08-20)**

| rule | n | PF | WR | net $ | maxDD |
|---|---|---|---|---|---|
| researched, spread ≤ 1.50 | 25 | **4.894** | 72.0% | +368.6 | 15.9 |
| researched, no spread filter | 34 | 2.869 | 61.8% | +351.7 | 46.9 |
| **Pine as written** | **45** | **2.149** | 55.6% | +343.5 | **62.7** |

**Holdout (2024-08-20 → 2025-08-20)**

| rule | n | PF | WR | net $ | maxDD |
|---|---|---|---|---|---|
| researched, spread ≤ 1.50 | 11 | 1.257 | 54.5% | +20.3 | 41.4 |
| researched, no spread filter | 12 | 1.049 | 50.0% | +4.6 | 57.1 |
| **Pine as written** | **17** | 1.649 | 58.8% | +71.4 | 41.4 |

Two structural facts about the extra trades:

- **The bug is purely additive here.** On all 34 in-sample and 12 holdout shared
  days, the Pine takes the *same* break as the reference — 0 substitutions. It
  never replaces a good trade; it only appends days the reference declined.
- **The appended trades are a coin flip.** Pooled across both years: n = 16,
  8 SL / 7 TP / 1 TIME, **WR 50.0%**, net +58.6, **t = +0.71**. With a 25.50
  target against a 15.50 stop, a random entry at 50% breaks even at PF ≈ 1.65;
  these score 1.46. The direction of the effect reverses between years
  (−8.3 on 11 in-sample, +66.8 on 5 out-of-sample), which is the signature of
  noise, and removing the single best trade halves the pooled number.

### Was waiting for the quarter worth anything?

On a substituted day the reference *saw* a break and rejected it for sitting too
far from a $25 line. That rejected trade is the honest control: if "wait for a
near-quarter break" carries information, the substitute must beat it.

| | wait for quarter | take the first break |
|---|---|---|
| in-sample, 11 days | −8.3 | −48.3 |
| holdout, 5 days | +66.8 | +74.9 |
| **pooled, 16 days** | **+58.5** | **+26.6** |

Waiting wins in-sample and loses out-of-sample. More telling: **13 of the 16
days resolve the same way either side** — the day's direction decides the
outcome, not the entry minute. The quarter is not selecting anything; it is
delaying entry into the same move.

---

## 2. `restrictWindow = true` hides the year that fails

Lines 101–121 default to the research year only (2025-08-20 → 2026-08-20 UTC).
Anyone who loads the script and presses go sees the in-sample year and nothing
else. The unseen year is already measured in this repo:

- PF **1.361** on 11 trades (ledger MQ02)
- the 18:45 anchor ranks **9th of 29** five-minute anchors out of sample; it
  ranked 1st in-sample (MQ03)
- Reality Check across 116,640 hypotheses: **p = 0.0662** (MQ07)

The default should be `false`, or the header should state the holdout result
next to the in-sample one.

---

## 3. The header numbers are in-sample only, and one is a rounding artefact

The header claims 25 trades / 72.0% / PF ≈ 4.887 / net ≈ +365.083. Against the
tick engine with the 12-hour clock applied I get **25 / 72.0% / PF 4.894 /
+368.6** — so the transcription is right and the spec is faithfully recovered.
(My earlier 5.125 in the ledger used the engine's longer session horizon; the
12h stop is what reconciles it.)

The claimed gross profit of 458.96 is exactly 18 × 25.50, i.e. the one
unresolved trade was booked at ≈ 0 rather than at its real time-stop value. That
is a rounding detail, not an error.

What the header does not say is that these are the numbers of the year the
parameters were chosen on.

---

## 4. The $25 quarter filter is inert on gold

The script's distinguishing feature is the quarter filter. Phase 12 of this
branch tested exactly that premise under phase-shift control: 192 cells
(2 years × 8 scales × 12 phases), and the largest round-vs-shifted effect
anywhere was **0.000211** — two hundredths of a percentage point (ledger QG03,
belief H105). At S = $25 specifically, 0 of 12 phases were profitable in either
year (QG07–QG09).

This does not make the strategy wrong; the quarter filter mostly acts as a
sample-size reducer here. It does mean the filter should not be described as the
mechanism.

---

## 5. Execution model — real, but smaller than it looks

The `strategy()` call declares no `commission_type`, no `commission_value` and no
`slippage`, and `process_orders_on_close = true` fills at the bar close, which is
a mid/last print. The research pays the real ask (long) or bid (short) and takes
real slippage past the stop. Measured entry spread on the 25 signals: median
**$0.947**, mean $0.996, max $1.484 — against a $15.50 stop.

Holding the entries fixed and changing only the fill model:

| fill model | PF | net $ |
|---|---|---|
| research: pay spread, credit target overshoot | 4.894 | +368.6 |
| research: pay spread, target as resting limit | 4.849 | +364.3 |
| Pine: mid fill, credit target overshoot | 4.914 | +369.9 |
| Pine: mid fill, target as resting limit | 4.856 | +364.5 |

**+$5.60 over 25 trades, ~1.5%.** Smaller than I expected, and the reason is
worth stating: with fixed $15.50 / $25.50 exits the spread does not change what
a win *pays*, only *which* trades win — and on this sample it flipped none.

One correction to my own reference number while I was in here: `microq3.apply()`
books `fav[j]`, the first real quote at or beyond the target, so it **credits
favourable target overshoot** — unlike `research/quarters/code/system.py`, which
treats the target as a resting limit. That is worth +$4.26 over 25 trades, and
it is optimism in the research baseline, not in the Pine.

### The number that actually matters: the sample is two trades wide

The Pine will run on TradingView's XAUUSD feed, not Dukascopy. Recomputing each
trade's adverse excursion *before* its exit (the `mae` column in `apply()` spans
the whole session, so it is the wrong statistic for this):

| date | worst before target | room left |
|---|---|---|
| 2025-12-15 | −15.41 | **$0.09** |
| 2026-07-14 | −15.37 | **$0.13** |
| 2025-10-21 | −9.59 | $5.91 |
| … 15 more, all ≥ $7.64 | | |

**Two of the 18 winners survived by nine and thirteen cents.** On a different
price feed those are coin flips. No loser came within $12.92 of its target, so
the losses are decisive but two of the wins are not.

| flip the closest calls to stops | PF | WR | net $ |
|---|---|---|---|
| as researched | 4.894 | 72.0% | +368.6 |
| closest 1 → stop | 3.973 | 68.0% | +327.5 |
| closest 2 → stop | **3.280** | 64.0% | +286.5 |
| closest 3 → stop | 2.734 | 60.0% | +244.7 |

A bootstrap over the 25 trades (20,000 draws) gives PF median 4.91, 5th–95th
2.47–12.10. That measures *sampling* error only — it cannot see selection, so it
says nothing about whether the rule repeats. The holdout is what says that, and
it says 1.257.

---

## 5b. The equity curve

`research/microq3/results/pine_equity_curve.png`, built by
`research/microq3/code/pine_equity.py`. Per-trade ledgers at
`results/equity_pine.csv`, `equity_ref_nospread.csv`, `equity_ref.csv`.

| | n | PF | WR | net $ | maxDD $ | net/maxDD |
|---|---|---|---|---|---|---|
| **Pine as written** | 45 | 2.15 | 55.6% | +343.5 | **62.7** | 5.48 |
| researched, no spread filter | 34 | 2.87 | 61.8% | +351.7 | 46.9 | 7.49 |
| researched, spread ≤ 1.50 | 25 | 4.89 | 72.0% | +368.6 | **15.9** | 23.24 |

The three curves end within $25 of each other and separate almost entirely on
the path. The Pine's extra 11 trades add no money (−$8.3) and quadruple the
maximum drawdown against the header's version.

**What the curve says in the strategy's favour:**

- **No single trade carries it.** Top trade = 7.6% of net, top 5 = 38%. With
  fixed ±$25.50 / −$15.50 exits that is structural — no winner *can* dominate —
  so read it as "the fixed exits did their job", not as evidence of robustness.
- **Both halves work.** First half (17 trades to 2026-02-18) PF 2.08; second
  half (28 trades) PF 2.19. The year is not one good quarter.

**What the curve says against it:**

- **172 of 355 days under water**, including a single 73-day drawdown
  (2026-02-08 → 2026-04-22) that took $62.70 — 18% of the year's entire profit,
  and 4× the researched version's worst.
- **The trade stream is thin and lumpy** — median 5 days between trades, max
  33, seven gaps over a fortnight. At 45 trades a year there is no month in
  which the curve carries statistical weight.
- **Nearly all of the second half's gain lands in April–May 2026** (+$200.2 of
  +$343.5, 58%), against a flat +$115 across the preceding eight months.

## 6. Dashboard desync (cosmetic)

Rows 5–7 print `"$1–$6.25"`, `"$25 ± $6.25"` and `"15.5 / 25.5"` as string
literals (lines 905, 920, 935) while `minimumBody`, `maximumBody`,
`quarterStep`, `maxQuarterDistance`, `stopPoints` and `targetPoints` are all
user-editable inputs. Change an input and the dashboard lies. Use
`str.tostring()` on the inputs.

---

## 7. Stale-anchor path (latent, does not fire on this data)

`synthOpen`, `anchorReady`, `anchorValid` and `tradedThisAnchor` are `var` and
are reset **only** on the 18:45 bar (line 308). Line 334 then builds the body on
the 18:55 bar guarded by `not na(synthOpen)`. If a session is missing its 18:45
bar but has its 18:55 bar, `synthOpen` still holds a **previous day's** open and
a synthetic body is built across days.

Measured on both tick years: 258 days with an 18:45 candle, 258 with an 18:55
candle, **0 days with 18:55 but not 18:45**. So this never fires on Dukascopy.
It is still worth guarding, because TradingView's own feed has different gap
behaviour and the guard costs one condition:

```pine
if isAnchorLast and not na(synthOpen) and na(anchorEndTime)
```

or better, stamp the anchor's date and require it to match.

Related: the research requires ≥ 5 one-minute bars inside 18:45–19:00 before it
will trust the anchor (`a["nmin"]`). The Pine has no data-quality gate. Measured
occurrences on this data: **0**. Also latent.

---

## What is correct

Verified line by line, not assumed:

- **Signal window matches exactly.** `minsAfterAnchor = (time_close −
  anchorEndTime)/60000` with `anchorEndTime` stamped on the 18:55 bar (= 19:00),
  tested `>= 5 and <= 30`, gives eligible closes 19:05 … 19:30 — six candles.
  The research's `five_min_candles(day, 19*60, 19*60+30)` yields candles
  *starting* 19:00 … 19:25, i.e. closing 19:05 … 19:30. Identical.
- **Mintick-agnostic risk conversion** — `stopPoints / syminfo.mintick` with a
  `math.max(1, ...)` floor, so the script survives a feed with a different tick
  size instead of silently sizing wrong.
- **The 5-minute guard** (`runtime.error` on `timeframe.in_seconds() != 300`) —
  the whole spec is 5-minute-specific and this makes misuse loud.
- **Synthetic body construction** — open of the 18:45 bar, close of the 18:55
  bar, `bodyHigh`/`bodyLow` from max/min. Matches the research's
  `candle(day, 18:45, 19:00)` open/close.
- **No look-ahead.** Every decision uses the completed bar's `close`;
  `process_orders_on_close` fills on that same close.
- **Research-window timestamps** match the audited year.
- **Time stop** starts the clock at `time_close` of the entry bar and is checked
  against `activeEntryTime + maxHoldMs`, reset when flat. Correct, and 12h is
  what reconciles the header PF.
- **`pyramiding = 0`** plus the `strategy.position_size == 0` guard means the
  tick-based `strategy.exit` distances are always measured from a single entry.

---

## Recommended changes, in priority order

1. **Fix BUG-047.** Set the "day is spent" flag when the *break* happens, not
   when the *trade* happens:

   ```pine
   brokeOut = insideSignalWindow and not tradedThisAnchor and
        ((not na(bodyLow) and close < bodyLow) or (not na(bodyHigh) and close > bodyHigh))
   aShort   = enableAShort and inResearchWindow and brokeOut and quarterOK and
        strategy.position_size == 0 and close < bodyLow
   flipLong = enableFlipLong and inResearchWindow and brokeOut and quarterOK and
        strategy.position_size == 0 and close > bodyHigh
   if brokeOut
       tradedThisAnchor := true          // spend the day on the BREAK
   ```

   This reproduces the researched selection exactly.
2. **Default `restrictWindow` to `false`**, or put the holdout number in the
   header beside the in-sample one.
3. **Declare costs** — `commission_type = strategy.commission.cash_per_contract`
   and a `slippage` — even though it is only worth ~1.5% here. It stops the next
   reader from having to measure it.
4. **Guard the stale anchor** and add a data-quality gate on the anchor bars.
5. **Bind the dashboard strings to the inputs.**

## Registry impact

- **BUG-047** — second confirmed occurrence in this repo (first: 10AM Quarter
  Matrix v1, Phase 7). Registry entry updated with this instance and with the
  measured cost.
- **H105** (the $25 gold quarter grid is inert under phase-shift control) —
  unchanged, and this audit is a third setting where it holds.
- Ledger rows **PS01–PS08**.
