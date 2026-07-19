# BELIEF REGISTER
# Per COGNITIVE_ARCHITECTURE.md Layer 4. High-conviction market beliefs.
# Rules: never update on one data point; 3+ contradictions -> Belief Review;
# every belief carries evidence and an invalidation.

## Active Beliefs

**B1. Session filter is the strongest edge lever on XAUUSD 5m.**
- Evidence: trendline breakout PF 0.85 (24/7) -> 3.656 (London+NY-open only), same logic.
- Invalidation: 2 consecutive session-filtered backtests with PF < 1.
- Status: HIGH conviction (backtested).

**B2. Auto-generated 5m S/D zone reclaims are noise on gold.**
- Evidence: Reversal Sniper v2, PF 0.731 over 313 trades.
- Invalidation: reworked zone logic showing PF > 1.5 on matched sample.
- Status: HIGH conviction (backtested, painful).

**B3. CPI direction is unknowable pre-print; the tradeable edge is post-spike.**
- Evidence: matched 7 CPI events 2025-2026: follow won 3, fade won 2, muted 1, unclear 1.
- Invalidation: any indicator shown to predict CPI-day direction >60% over 20+ events.
- Status: MEDIUM-HIGH conviction (event study, small n).

**B4. In-line prints produce no event candle; surprise size drives gold's CPI move.**
- Evidence: Mar 11 2026 (in-line, muted, -0.3%) vs Jul 14 2026 (miss, +1.8%).
- Invalidation: repeated big moves on in-line prints.
- Status: MEDIUM conviction (few observations).

**B5. Candlestick patterns carry edge ONLY with trend + location context (Nison), and
tier-A (engulfing, stars, soldiers/crows) >> tier-C (harami, tweezers, doji).**
- Evidence: Bulkowski quantified testing; Nison context rules.
- Invalidation: our own backtests showing naked patterns outperforming filtered ones.
- Status: MEDIUM conviction (literature, not yet self-tested).

## Unconfirmed Hypotheses (await corroboration)

**H1. Confirm-Continuation is the best default CPI mode.** Won the decisive days in the
2025-26 event match; needs the user's 1H harness backtest across all ~11 events.

**H2. The flip system's side going into 8:30 news is near coin-flip.** Pre-news audit
indicator built; awaiting the user's table numbers.

**H3. Markets balance ~70% / trend ~30% (PBD transcript claim).** Asserted without
data by profile trader; plausible per auction theory folklore. Test: PBD engine's
D-regime bar share on XAUUSD 5m/1H. Do not size on it until measured.

**H4. Close-cluster value areas + P/b structures add filter value to the trendline
breakout.** Corroborating overlap: PBD break-in == our reclaim; close-count
confirmation == CPI continuation mode. Needs A/B backtest with/without PBD gate.

**H5. Momentum-join beats reversal-hunting for scalps (Valentini).** His measured
sample: trend-join WR 50-60% vs reversal WR 40%; rejected sweep models after
testing. Verified competition trader = strong testimony, but NASDAQ orderflow
context. Test on gold: JOIN vs REVERT signal performance in his engine.

**H6. ~2SD VWAP excursions revert to fair value; 3rd SD hit only ~7% of sessions
(Valentini's stats).** Directly codeable and testable on XAUUSD sessions.

**H7. Break-and-test (second drive) with full-body close beats first-drive entries
(Valentini live session).** Same source as H5 (no new tally), but now with exact
mechanics. Already converges with our confirmation family. Test: trendline
breakout A/B — enter on break close vs break->test->full-body re-close.

**H8. Setups weaken with each level rejection; ~3 rejections = stand down; good
entries go green immediately (Valentini live).** Codeable (engine v2 rejection
gate). Test: WR of JOIN signals at fresh vs over-rejected levels.

## Contradiction Tallies (3+ independent -> Belief Review)
- Reclaim/sweep-reversal family (B2 fix, PBD break-in): 1 contradiction
  (Valentini tested & rejected sweep models as lower-WR than momentum-join).

## Retired Beliefs
(none yet)
