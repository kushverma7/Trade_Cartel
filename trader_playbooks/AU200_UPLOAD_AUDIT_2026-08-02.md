# AU200 Upload Audit — 2026-08-02

Ten documents uploaded, all read in full (both PDFs extracted with pypdf, not
grepped). Nine describe the same underlying system — Dialectic Engine v4 on
AU200 AUD 5m — measured different ways. The tenth, `MASTER_BLUEPRINT.md`, is
a methodology document and is the most valuable item in the set.

## The same system, reported nine ways

| document | period | config | N | WR | PF | net pts | max DD |
|---|---|---|---|---|---|---|---|
| `au200_opening_system_report` (High-WR) | 2016–2026 | 9:50+9:55+10:00, TP10/SL15 | 242 | 75.6% | 1.74 | +703 | −55 |
| `au200_opening_system_report` (Max-Net) | 2016–2026 | same, TP20/SL15 | 242 | 59.1% | 1.72 | +1133 | −123 |
| `au200_open_trade_report` (High-WR) | 2016–2026 | Tue+Fri, TP10 | 87 | 79.3% | 2.16 | +333 | −53 |
| `au200_open_trade_report` (Max-Net) | 2016–2026 | Tue+Fri, TP20 | 87 | 65.5% | 2.26 | +603 | −48 |
| `au200_opening_trail_system_report` | 2019–2026 | 10:00, TP1=10 half + trail 30 | 141 | 56.7% | 4.59 | +2474 | −69 |
| `au200_ultimate_opening_system_report` | 2019–2026 | 3 bars, TP1=10 half + trail 30 | 170 | 56.5% | 4.52 | +2817 | −80 |
| `au200_master_day_trading_system` TREND | 2016–2026 | 13 windows, SL15, no TP | 309 | 42.1% | 1.85 | +3406 | **−407** |
| `au200_master_day_trading_system` SCALP | 2016–2026 | ATR≥6 + TP30 | 96 | 47.9% | 1.67 | +534 | −118 |
| `au200_de_v4_monthly_breakdown` | 2019–2026 | V2 windows, SL15 | 213 | 42.7% | 1.85 | +2691 | **−407** |
| `master_strategy_blueprint` baseline | 2021–2024 | confluence v2 15m score≥4 | 980 | 37.3% | **1.116** | — | 17.9% |

Read the first and last rows together. The same research programme produced
a headline of PF 4.52 and an internal baseline of PF 1.116. Only the second
one carries a sample worth the name.

## Six findings, each provable from the documents themselves

### 1. The drawdown is understated roughly five-fold

The trail and ultimate reports claim max drawdown of −69 and −80 points. The
monthly breakdown and the master system, covering overlapping data on the
same base engine, both report **−407 points**. At $100/pt that is $8,050
claimed against $40,700 measured.

This is not an inference across documents — the ultimate report contradicts
itself internally. Its headline says −80pts while its own drawdown chart
carries a y-axis running to −400pts. The trail report does the same: −69pts
stated, chart axis to −300pts.

### 2. Every loss is identical, which is impossible

`au200_opening_system_report` states, for 242 trades: Max Loss −16pts, **Min
Loss −16pts**. All 59 losses in High-WR mode and all 99 in Max-Net mode are
exactly −16.0. Every win is exactly +9.0 or +19.0.

That is a synthetic fill model: the stop is assumed to fill at exactly 15pts
plus 1pt cost, always. No gaps, no slippage, no partial fills — on the ASX
opening bar, the single gappiest bar of the session, which is the only bar
the system trades.

The same document set disproves it. The monthly breakdown, same instrument
and same base engine, records average monthly losses of −122.0 (Jun 2020),
−119.6 (Mar 2023), −108.0 (Jun 2024), −85.5 (Oct 2023), −83.1 (Mar 2020).
Losses of eight times the stop distance demonstrably occur in this data. A
report claiming a −16pt worst case over 242 trades is therefore not measuring
the same market. This is BUG-018 exactly.

### 3. 75% of seven years' profit comes from five months

From the monthly breakdown, total +2691 pts over 213 trades:

| month | net pts | share of total |
|---|---|---|
| Jun 2022 | +794.9 (4 trades) | 29.5% |
| Apr 2025 | +366.9 (1 trade) | 13.6% |
| Nov 2020 | +343.8 (1 trade) | 12.8% |
| Feb 2025 | +263.5 (1 trade) | 9.8% |
| Mar 2025 | +252.7 (3 trades) | 9.4% |
| **five months, 10 trades** | **+2021.8** | **75.1%** |

Ninety months of data; five of them carry three quarters of the result, and
four of those five are single-trade or near-single-trade months. Remove them
and the system is approximately flat. No validation gate in the blueprint
would pass this, and no position size can be chosen from it.

### 4. The master system's cover page contradicts its own charts

- Cover: "PF 2.85 Trend Mode". Its equity chart: "PF=1.85".
- Cover: "WR 75% Scalp Mode". Its equity chart: "WR=47.9%".
  The 75% figure is the TP=10 row of the TP-optimisation table while the PF
  and net come from the TP=30 row — the headline mixes two configurations.
- Cover: "0 Losing Years (10Y)". Its own annual bars show Trend 2019 = −22,
  and Scalp 2016 = −51, 2018 = −51, 2024 = −22.

### 5. The window selection is data mining, and the document says so

The master system presents "13 PROVEN ENTRY WINDOWS" chosen by hour × day ×
direction. That search space is 24 hours × 5 days × 3 directions. Cell sizes
in the winning table include N=11 (PF 5.78), N=12, N=13 (PF 5.31), N=16.
"01h Tue" is presented as an edge at a **23% win rate**.

Rule 6 — "Never trade 09:00–10:00 UTC. Proven trap. PF=0.09 over 10Y" — is a
filter derived by looking at the results and deleting the worst cell. That is
in-sample optimisation presented as a discovered law.

### 6. Nothing here passed the blueprint's own gates

`MASTER_BLUEPRINT.md` Stage 6 requires: ≥150 trades, PF ≥1.4, ≥55% profitable
months, a 1000-permutation Monte Carlo test at p<1%, a walk-forward test, a
walk-forward permutation test, and a parameter stability test. Its own status
line reads **"Permutation tests: PENDING (must run before going live)."**

No report in this set ran any of the five gates. Several fall below the trade
minimum. The blueprint was written and then not followed.

## What is genuinely valuable

### `MASTER_BLUEPRINT.md` — adopt two things from it

**(a) Bar-permutation Monte Carlo, and re-optimise on each permutation.** Its
Stage 6.2 permutes intrabar relatives and gaps independently while preserving
mean, variance, skew, kurtosis and gap structure, then **re-runs the
optimisation** on the permuted series and compares the resulting PF.

This is stronger than our corrected random-timing null (BUG-023). Ours tests
whether the entry beats noise. This tests whether **the whole search
procedure** beats noise — it prices in data-mining bias directly, which is
precisely the failure mode every document above exhibits. Worth building into
`backtest/overfit.py` alongside DSR and PBO.

**(b) MAE/MFE 80th-percentile derivation of SL and TP.** Stage 5 sets the stop
at the 80th percentile of maximum adverse excursion and TP1 at the 80th
percentile of maximum favourable excursion, both from realised trade data.

This is the correct answer to BUG-017. A level- or grid-based target fails
because its distance is set by where a line happens to sit. An
excursion-derived target sets distance from what trades in this market
actually do. It belongs in `exit_lab.py` as a target mode.

### `aicartel_trade_guide_nq_clc_and_csm.md` — new exit mechanics and two new voices

New exit rules not implemented in any engine here:

- **CVD divergence forces immediate breakeven** — price up while CVD falls
  moves a long to BE, non-negotiable. An exit trigger driven by
  order-flow disagreement rather than price.
- **VWAP standard-deviation target ladder** — TP1 at VWAP midline (40%), TP2
  at 2SD (40%), TP3 at 3SD (close all). This is volatility-anchored rather
  than line-anchored, the same family as the Valentini ADR partial logged in
  `BELIEF_REGISTER.md`, and it inherits the same reason for being sound.
- **Three-loss-per-level abandonment** — after a level rejects price three
  times, that level is dead for the day.
- **−2R daily halt**, and the Q1/Q2/Q3 90-minute session cycle in which a
  sweep must occur in Q2 for any Q3 entry to be valid.

Two trader voices not in the 21-voice register: **Marco Acetony** (qualifying
sweep rule, order-block traps) and **Carmine Rosato** (CLC framework, zero
prints, three-loss rule). Fabio Valentini is already voice #2.

Its claim of "verified 75% WR on BTCUSD 5m, Oct 2025–Jan 2026" carries no
trade count and a four-month window. Recorded as an unverified claim.

## Verdict

Do not trade any configuration in these reports. The measured drawdown is
five times the stated figure, the fill model cannot reproduce losses the same
data demonstrably contains, and three quarters of the profit comes from ten
trades.

The DE v4 opening-bar concept is not thereby dead — the trail exit raises
profit factor in every single year versus the fixed target, which is a
consistent effect rather than a cherry-picked one, and it agrees with this
project's own finding that the exit carries the edge. It is worth rebuilding
from scratch under this repo's cost and validation standards. It is not worth
believing at the numbers shown.

---

# Addendum — batches 3 and 4 (code, grid, HalfTrend)

15 further files. Two duplicate pairs (`DE_v4_P1P2.pine`,
`daily_opening_report.pdf`) and one identical duplicate of
`es1_local_backtest.py` — archived once each.

## `es1_local_backtest.py` — seven defects, two of them fatal

1. **Equity accounting is broken (fatal).** Long entries do
   `equity -= cost` where `cost` is the full notional. Exits add back only
   the P&L (`equity += pnl`), never the principal. Every long permanently
   removes `close × qty` from equity. The equity curve, net profit, return
   percentage, drawdown and Sharpe are all meaningless.
2. **The data cannot exist (fatal).** `yfinance` serves roughly 60 days of
   5-minute history regardless of how the request is chunked. `START =
   "2019-01-01"` returns empty frames for all but the most recent window.
   Any "2019→2026 5m" result from this script is a few weeks of data
   wearing a seven-year label.
3. **TP1 partials are counted as whole trades.** Each TP1 fill appends its
   own row to `trades`, and win rate (line 365) and profit factor (379–381)
   both run over every row. A TP1 row is always positive, so every trade
   that reaches TP1 donates a guaranteed extra win and extra gross profit.
   BUG-016 in a new costume; it inflates both headline metrics.
4. **Position sizing carries a spurious factor of price.** Risk per share is
   `atr × mult`, but the sizer divides by `atr × mult × price`, making every
   position roughly `price`× too small.
5. **Assumed risk and actual risk differ by an order of magnitude.** Sizing
   assumes a stop at `1.5 × ATR`; the stop actually placed is
   `low − 0.1 × ATR`.
6. **Short entries never touch equity.** Longs deduct `cost` and are gated by
   `if cost <= equity`; shorts compute `rev` and discard it, with no
   affordability check. BUG-022 class — one direction edited, the mirror
   left behind.
7. **Stops fill exactly at the stop price** (lines 244, 253), no gap
   handling. BUG-018.

Also: the "3-loss rule" increments on any *signal* near a level, not on a
*loss*, and never resets after a win, so it does not implement the rule it
is named for.

## `halftrend_optimisation_results.csv` — 80% of the grid is duplicate rows

`channelDeviation` ∈ {1,2,3,4,5} yields byte-identical output for every
other setting — same signal count, same confirmation percentage. The
uploaded HalfTrend source shows why: `dev = channelDeviation * atr2` feeds
only `atrHigh`/`atrLow`, which are plotted bands. The flip logic uses
`highma`, `lowma`, `maxLowPrice` and `minHighPrice` and never reads `dev`.
The parameter provably cannot change a signal.

So 1,920 rows are 384 real configurations and 1,536 duplicates. Any
selection reporting a "best channelDeviation" is reporting noise.

Worse, the ranking metric is circular. `pct_confirmed` rises monotonically
with `confirmWindow` — 0.463, 0.591, 0.657, 0.726 for windows 1, 2, 3, 5 —
because a wider window mechanically catches more confirmations. Choosing
window 5 because it maximises confirmation rate selects a tautology.

And the file contains no profit factor, no net, no drawdown. It measures how
often an EMA agrees with HalfTrend. Agreement is not profitability; a filter
can agree 74% of the time and still remove every winner.

## `halftrend_au200_v6_final.pine`

- **ATR regime filter self-satisfies at every volatility high.**
  `atrHigh = ta.highest(atr14, atrRegWin)` includes the current bar, so
  `atrPct = (atr14 − atrLow)/(atrHigh − atrLow) × 100` equals 100 whenever
  ATR makes a new window high. The gate `atrPct >= atrRegPct` therefore
  always passes at exactly the moments it was meant to judge. BUG-015 class.
- **No `margin_long`/`margin_short` set**, so both default to 100%. With
  `default_qty_value=1` on a ~8,000-point index against `initial_capital =
  10000`, this sits squarely in BUG-012 territory. Read fill rate before
  believing any metric from this file.

## `au200_flip_engine_report.pdf`

Confirms the drawdown contradiction a third time: states max drawdown
−$8,050 while its own drawdown chart runs to −400pts.

Its content is interesting though — reversing at the stop instead of going
flat adds $255,530 net across 317 trades, at the cost of 0.83 profit factor.
That is a real exit-side finding, and it is the only measured comparison in
the whole upload set that isolates a single variable.

## Genuinely valuable: `HalfTrend_DMI_Strategy_Report.docx`

A complete, unambiguous mechanical specification (Booming Bulls / Anish
Singh Thakur): ADX(13,13) read from 15m must exceed 23; +DI vs −DI sets
permitted direction; HalfTrend flip on the 5m close is both entry and exit;
maximum two stop losses per day.

The stated reason for preferring HalfTrend over SuperTrend is the valuable
part, and it is structural rather than stylistic: SuperTrend flips when
price touches the line, HalfTrend requires channel confirmation, so it holds
through pullbacks instead of whipsawing out. That is an exit-side mechanism,
which is where this repo has measured the edge to be.

**Three uploads disagree about flip exits.** The DMI report's exit *is* a
flip. `indicator_forensics_brief_v2.md` lists "NO flip exits" as absolute
rule 2 and disqualifies any combination containing one. The flip engine
report measures flipping as worth +$255,530. Nobody reconciled them.

## Indicators archived

Twelve Pine files to `indicators/aicartel_2026-08-02/`: Dialectic Engine v1,
v4 Flip, v4 Trendline, v4 P1P2, v5, v6 Fib TP Manager, V15 Final, AC FUSION,
AICartel Scalper, Super Scalper, Fabio+Marco Entry/Exit, HalfTrend EMA
Stack, plus the two AU200 HalfTrend builds. Dialectic Engine v1's sweep
detection is correctly written — it compares against `rh[1]`/`rl[1]`,
avoiding BUG-015.

---

# Addendum — batch 5

## `au200_trading_system_requirements.pdf` — the most important document in the set

This is a previous session's handoff. It is the only document that states the
system honestly and completely: DE v4's exact parameters (SuperTrend 97/3.1,
AlphaTrend 14/1.0, EMA 9/21/50/200, RSI 14 with bull zone 45–70 and bear zone
30–55, MACD 8/17/9), the hard gate, the 3-of-5 confluence score, and the
instrument facts (Capital.com AU200, $100/pt, 1pt commission, $50,000 initial,
1 contract fixed).

Its section 7, "WHAT WAS WRONG WITH EVERY VERSION BUILT", is a bug list that
was never registered anywhere:

1. UT Bot was the wrong engine entirely — DE v4 is the real system. **This
   retroactively disqualifies the nine-row UT Bot table** discussed earlier in
   this session.
2. Hardcoded UTC+10 fires an hour early from October to April; must use the
   `Australia/Sydney` timezone so daylight saving is handled.
3. Inverted flip stop-loss signs in `ema_hybrid_v2` produced 5,000+ cascading
   trades. That is BUG-011 recurring.
4. `process_orders_on_close=true` filled entry and exit on the same bar close;
   the rule requires filling at the next bar's open.
5. An EMA200+RSI approximation was substituted for the real DE v4 engine.
6. A one-month backtest was presented as representative.

### The smoking gun was found and read backwards

The document states:

> "Every winning trade = exactly +9 pts after commission (TP hit). Every
> losing trade = exactly −16 pts after commission (SL hit). **This confirms
> clean fixed TP/SL exits with no partial fills.**"

It confirms the opposite. Identical fills across 242 trades on the ASX
opening bar prove that gaps and slippage were never modelled — a real
opening-bar sample cannot produce 59 losses of exactly −16.0. The previous
session found the defect, looked straight at it, and recorded it as evidence
of correctness. This is the single most consequential error in the archive.

### Its Master System figures match no other document

| metric | `master_system.pdf` chart | requirements doc |
|---|---|---|
| N | 309 | 328 |
| WR | 42.1% | 38.4% |
| PF | 1.85 | 2.85 |
| net | +3406 pts | +4844 pts |
| max DD | −407 pts | −184 pts |

Every figure differs. The requirements doc took PF from the master system's
cover page — the same cover shown above to contradict its own chart — and a
drawdown that appears nowhere in either.

## `au200_backtest_report.pdf` — the honest one, and it fails

A from-scratch Python backtest of the two AICartel systems, 14 Apr – 12 Jun
2026, ~60 days.

**NQ Master CLC:** 41 trades, WR 58.5%, **PF 1.10**, net **−0.53R**,
expectancy **−0.013R per trade**, Sharpe **−0.14**. And costs were set to
**zero** — "Commission: None (conservative), Slippage: None". A system with
negative expectancy in R at zero cost is a losing system once costs exist.

Two genuinely useful breakdowns, and they are the most actionable numbers in
the entire upload set because they isolate one variable each:

- **B-grade signals destroy the edge.** A-grade (3/3) returned +4.08R over 25
  trades; B-grade (2/3) returned **−4.61R over 16**. The half-size 2-of-3
  signal is not a smaller version of the edge, it is the opposite of it.
- **Shorts were net negative**: longs +$7,292 over 21 trades, shorts −$5,515
  over 20.

**Crypto Scalp Model v1:** PF 5.24 on **five trades**. The trade guide's
claim of "verified 75% WR on BTCUSD 5m" rests on this. Recorded as an
unverified claim with n=5.

## `big_players_reversal_entry.txt` — inverted DI, deliberately or not

The signal conditions read:

```
BUY  : varl3 > varl3[1] and close > close[1] and ADX > 40 and DIMinus > DIPlus
SELL : varh3 > varh3[1] and close < close[1] and ADX > 40 and DIMinus < DIPlus
```

A buy requires **bearish** directional pressure and a sell requires **bullish**
pressure. That is the reverse of conventional DMI use, and the reverse of the
HalfTrend+DMI report in this same upload set, which states "+DI > −DI → only
LONG permitted."

For a reversal indicator this may be intentional — buying into peak bearish
pressure is a defensible mean-reversion premise. But it is undocumented, and
anyone porting this into a trend system inherits inverted signals (BUG-011).
Which it is must be settled before use, not assumed.

Also carries unexplained magic constants (`* 40`, `* 0.312`, `> 100`), an
unusually high `ADX > 40` gate, and a promotional Telegram table — it is an
unvetted public script, not validated work.

---

# Second pass — what the first pass missed

The first pass read the PDFs and markdown in full but only **grep-scanned** the
Pine files and never opened `AU200_Strategy_Report.pdf`,
`daily_opening_report.pdf` or `au200_trail_strategy.pine`. Corrected here.

## CORRECTION: the flip stop is NOT inverted in the archived Pine

`AU200_Strategy_Report.pdf` describes the flip mechanism as an inverted stop:

> "Flip formula: nsl = xp + nd × sl × mult. Long stopped → flip SHORT → SL
> placed BELOW entry (xp − 22.5) → fires as immediate take-profit. The SL is
> already in profit territory the moment the flip opens. That is why WR is
> 95%+."

A stop below entry on a short is indeed a guaranteed take-profit, and that
would fully explain a 95.6% flip win rate. **But the archived Pine does not
do this.** In `01_AU200_MASTER_SYSTEM.pine` and `05_AU200_UTBOT_OPENING.pine`:

```
// long stopped -> flip short
_sl_cur := _flip_ep + flip_sl      // ABOVE entry, for a SHORT — correct
_st     := -1

// short stopped -> flip long
_sl_cur := _flip_ep3 - flip_sl     // BELOW entry, for a LONG — correct
_st     := 1
```

Both signs are conventionally correct. The misleading part is cosmetic: the
input is labelled "Flip SL pts (profit side)" and a comment reads
"// inverted", while the arithmetic is standard.

So the inversion the PDF describes belongs to the Python engine
`ema_hybrid_v2` — which `au200_trading_system_requirements.pdf` independently
lists as a known bug ("Flip SL signs inverted in ema_hybrid_v2 — caused
5,000+ cascading trades") and which was never pushed. The nine-row table came
from that engine. The Pine files are the later, corrected builds.

## The real defect in the Pine: stops are tested against CLOSE, not LOW/HIGH

```
if close <= _sl_cur          // long stop
if close >= _sl_cur          // short stop
```

The stop is only honoured if the **close** violates it. A bar can trade fifty
points through the stop intrabar and, if it closes back on the right side,
the position survives untouched and the loss never appears.

This explains the identical-loss finding far better than any fill-model
assumption: losses cannot exceed the stop distance measured close-to-close,
so they collapse onto one value. It systematically understates every loss,
and on the ASX opening bar — the gappiest bar of the day — it understates
them most. Registered behaviour class: same family as BUG-018, but the cause
is the *test*, not the fill.

## `AU200_Strategy_Report.pdf` — never opened in the first pass

This is the source of the nine-row screenshot table, and it states the
decisive fact plainly:

> "Without flips, the system loses money. Flips are not a recovery tool —
> they ARE the strategy. The first entry (WR 35.4%) is bait."

| max flips | N | WR | PF | net |
|---|---|---|---|---|
| **0** | 2,714 | 37.8% | **0.79** | **−$369,270** |
| 1 | 3,878 | 56.9% | 2.23 | $2,181,130 |
| 2 | 4,893 | 67.7% | 4.07 | $5,142,420 |
| 3 | 5,906 | 73.3% | 5.41 | $7,339,270 |

**The underlying strategy loses money.** Every dollar of the headline comes
from the flip layer, whose win rate the report itself attributes to a stop
placed in profit territory. That is the whole nine-row table in one line.

Three further findings in it are genuinely useful:

- **EMA filters raise PF and lower net, every time** — +0.3 PF for −$1.4M to
  −$1.8M net across five filter variants. This independently reproduces this
  repo's own standing finding on a different instrument and a different
  engine. Cross-validation of "never optimise profit factor alone."
- **Fixed TP + flip was negative in every configuration tested** (PF 0.85–0.89
  across TP 10–20 × SL 10–20 × flips 0–3). Consistent with BUG-017.
- **Early profit-taking destroys trend systems**: TP1 at EMA8 pierce returned
  14.6% WR and −$427,792, while holding to end of day returned 83.3% WR and
  +$1,170,926 on the same signals.

It also **contradicts the rest of the archive on the ASX open**: it says
dropping the 9:50 bar gains $740k because "9:50 = ASX open, max noise, wide
spreads, false crossovers", while `au200_open_trade_report.pdf` claims
"tight spread at open (~1pt), ensuring accurate fills and reduced slippage"
and the ultimate/trail reports trade 9:50 deliberately.

## `TC_Opening_Session.pine` — the best-documented file in the entire upload

XAUUSD, 5m, 5.5 years, 1,415 days. Two setups with modest, plausible numbers
(London Close Fade 57.2% WR / +0.72pt expectancy; NY ORB with a ≤10pt
pre-range filter, 50% WR / +0.91pt), and — uniquely in this archive — an
explicit list of what was tested and removed:

> Judas Swing to Asia target: 1–2% WR · ORB without filter: 27–31% WR
> · Narrow Asia range filter: no improvement · Directional bias: 52% coin
> flip · NY following London: 52% coin flip

Negative results reported with numbers, on our own instrument. This is the
one file here that follows the repo's own standards, and its expectancies are
small enough to be credible.

## Other second-pass notes

- `au200_trail_strategy.pine` uses correct stop signs (`close − sl_pts` long,
  `close + sl_pts` short) and has no flip layer. It is the clean variant.
- `Dialectic_Engine_v4_Flip.pine`'s "flip" means *opposite signal exits the
  trade* — an exit rule, not the stop-and-reverse engine. Do not conflate them.
- `daily_opening_report.pdf` is a further variant: N=171, WR 76%, PF 1.78,
  +514pts, MaxDD −53pts. It belongs to the fixed-TP family (PF ~1.7–1.8), not
  the trail family (PF ~4.5).
- `STRATEGY_EXTRACTION_PROTOCOL.md` is byte-identical to the repo's copy.
- `THE_CONFLUENCE_STRATEGY.md` is this repo's own AMDM document. It is honest
  about itself — labels its expectancy table "ESTIMATES… not backtested",
  applies a 20–40% haircut, and states a 55.4% probability of significant
  drawdown in six months. It remains untested.
- `TC_Master_Strategy.pine` stacks eleven named methods into one 0–18.5 score.
  Its structure is sound (`ta.pivothigh/low`, `[1]`-offset Turtle and Wyckoff
  ranges avoid BUG-015) but the component weights are asserted, never
  measured, and nothing in the archive tests them.
