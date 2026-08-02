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
