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

**H9. Effort/result classification (absorption, initiative, thin sweep, dry-up)
adds signal quality info (Valentini orderflow course — same source family).**
Volume+wick proxy built (effort_result_engine). Test: do THIN breakout candles
underperform DRIVE breakout candles on the trendline core? If yes, THIN becomes
a master-engine veto and DRIVE a scoring layer.

**H10. NY session structure: first-hour expansion -> midday rebalance -> power-hour
(15:00-16:00 ET) re-expansion, ~90% of expansion days (Valentini live, same source).**
Codeable. Master engine has optional power-hour window (default OFF, NASDAQ claim,
unverified on gold). Test: gold 5m trendline signals by session phase.

**H11. Side-equity divergence marks one-sided regimes (Valentini: shorts -1.7k vs
longs +67k in a rebuild week).** Test: split any strategy's long vs short PnL
curves; disable the bleeding side when curves diverge hard. Strategy-wrapper TODO.

**H12. Quad rotation (4 stochastic bands aligned) + divergence + confirmed turn
is a high-quality reversal entry (Kurisko — INDEPENDENT source #3).** His "95%"
claim is marketing; mechanics exact-coded in kurisko_quad_rotation.pine. Test:
SUPER signals vs plain divergence signals on XAUUSD 5m.

**H13. Time quarters + True Opens structure intraday behavior (Quarterly Theory —
INDEPENDENT source #4, ICT lineage).** Zero stats in source; testable claims:
reversals cluster near true opens; manipulation sweeps concentrate in Q2/NY-open
windows. Engine built for observation.

**H14. SMT divergence (gold sweeps, silver/DXY doesn't confirm) marks manipulation
sweeps worth fading.** Codeable, implemented with real second-symbol feed. Test:
JUDAS signals (sweep+reclaim+SMT) vs plain reclaims on XAUUSD 5m.

**H15. Q-alternation: consolidation quarters are followed by expansion quarters and
vice versa (QT school, doc #2).** Session form: Asia range size decides whether to
trade London or NY. Highly testable: classify each session's range vs average,
measure alternation frequency on gold. Engine posts a forecast label at each Q
open — score its hit rate visually before any deeper test.

**H16. Real breakouts carry a volume tsunami; hollow breakouts fail (H9 restated
with Roppel's independent support — 2 sources now: Valentini effort/result,
Roppel/O'Neil school).** Promotion path: one gold backtest showing DRIVE-quality
breaks outperform THIN breaks -> becomes a belief and a master-engine veto.

**H17. Leg-size ratio (avg up-leg vs down-leg) is a usable continuous regime
measure (Ario, educator — no track record).** Implemented as intent_reader
scoreboard. Test: does its BULL/BEAR/CONSOL state classify gold regimes better
than the close-cluster VA (PBD) regime? A/B as master-engine regime layer.

**H18. Swing maturity: reversals at POIs require ~4-6 matured swings; fewer =
don't fade (Dave — voice #7, explicitly falsifiable).** Implemented as counter
(dave_swing_count.pine). Test: WR of reversal signals (SUPER, JUDAS, reclaims)
at mature (4+) vs immature (<4) swing counts on gold. Could become a veto.
Refinements (same source): no fresh continuations after 3 swings; runaway count
(5-6+) = HTF in control, demand consolidation at the extreme before countering.

**H19. Time-based ranges: the 09:00/15:00 ET hourly candles act as POIs — bias
from subsequent closes, 50% taps reject, far-side sweeps reverse (Dave, same
source as H18).** Implemented (timebase_range.pine). Note: internally contradicts
his own price-over-time stance; externally aligns with QT true-open anchors.
Test: tap/sweep signal outcomes on gold vs random hourly candles as control.

## EVIDENCE LOG (our own backtests — outranks all testimony)
- 2026-07-19 TEST #1: Master Strategy, Full Confluence, XAUUSD 5m,
  May 25-Jul 18 2026: PF 1.001, WR 31.25% (30/96), DD 2.81%, +$48.
  DIAGNOSIS: session built as +2 score, not gate -> traded 24h; off-
  session B-grades diluted the edge. CONFIRMS B1 a third time from
  our own data: session must GATE. Strategy v1.1 adds hard gate +
  A+-only mode. Pending: gated re-run, Core Only control run.

INTRA-SCHOOL NOTE (H13): primary source (Daye video) corrects compilation #1 —
true weekly open is Monday 18:00 ET, not Tuesday midnight. Engine fixed. When
sources within a school conflict, the primary wins; logged as a reminder that
compilations garble.

## Contradiction Tallies (3+ independent -> Belief Review)
- Reclaim/sweep-reversal family (B2 fix, PBD break-in): 3 SUPPORT (PBD break-in,
  QT Judas swing, Dave sweep-prerequisite) vs 1 AGAINST (Valentini). THRESHOLD
  CROSSED: register-supported doctrine, final promotion pending our own backtest
  of Reversal Sniper v3 / JUDAS on gold.
- H5 momentum-over-reversal: CONTESTED 2v2 — support: Valentini (measured),
  Roppel ("never buy weakness"); counter: Kurisko (confirmed divergence
  reversals), QT school (true-open reversals). Only our own backtest splits this.

## Corroboration Ledger (independent sources per idea)
- Confirmation-before-entry family: 4 independent (our CPI event study,
  PBD close-count, Valentini break-and-test, Kurisko confirmed turn).
  STRONGEST idea in the register.
- Multi-timeframe alignment before sizing: 3 independent (Cognitive
  Architecture, Valentini 15m->1m->15s stack, Kurisko quad bands).
- Confirmation-before-entry: now 7 independent (add Dave's post-sweep
  close-confirmation to CPI study, PBD, Valentini, Kurisko, QT, Ario).
- First-NY-hour caution: 2 independent (Valentini, Dave) — formal A/B needed
  vs our backtested 8:30-11 B1 window (does excluding 9:30-10:30 help?).
- H8 rejection-weakening / failure counting: 2 independent (Valentini
  live rules; Ario stacked-wick failure counting).
- B1 session windows (London + NY open): independent corroboration from
  Quarterly Theory Q2-expansion mapping (different reasoning, same windows).
- Cushion-based risk escalation (risk profits, protect principal): 2
  independent (Valentini, Roppel).
- Round numbers as magnets/failure points: 2 independent (Valentini, Roppel).

## Retired Beliefs
(none yet)
