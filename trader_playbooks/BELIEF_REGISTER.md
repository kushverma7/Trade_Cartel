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
- REWORK CANDIDATE LOGGED (2026-07-20, H30): Wendell/OTA zone rules
  (voice #10) give the precise quality filters v2 lacked -- freshness
  (untested-only), basing-candle-count cap, departure-strength filter,
  retest-depth confirmation. indicators/wendell_zone_engine.pine
  implements all four. Backtest this BEFORE writing off S/D zones
  entirely -- v2's failure may be a rules-implementation gap, not
  proof the concept fails on gold.

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

**H20. Brinks windows: a hammer completing the second leg of an M/W at the
03:30-03:45 or 09:30-09:45 ET candle marks a high-probability reversal (Steve/
MMM4x — INDEPENDENT voice #8, LOW-MED credibility: seminar seller, "90%" is
marketing, mechanics falsifiable).** Partially overlaps QT manipulation windows
and B1 session opens by a different route. Test: BRINKS signal outcomes on gold
15m vs identical hammers at random times (time factor isolated).

**H21. Stop hunts exhaust within a bounded zone beyond the accumulation range
(FX 25-50 pips; gold scale unknown — measure it).** Test: distribution of sweep
depths beyond the Asia range on XAUUSD; if bounded, zone tier 2 becomes a
fade-entry map and a stop-placement rule.

**H22. Three failed visits to a level (wicks ok, no body break) = reversal
imminent; a locked (30-90 min unbroken) day extreme is safe to trade away
from (Steve).** Converges with H8 rejection-weakening from the OPPOSITE
direction: H8 says rejected levels weaken continuation entries; H22 says the
third rejection is itself the fade trigger. Same observable, two uses. Test:
3-TAP signal WR on gold vs 1st/2nd taps.

**H23. Daily movement structures into 3 levels of ~ADR/3 each, with levels 1
and 3 aggressive (MM-driven) and level 2 drift; level 3 = reversal watch;
weekly = 3-day unidirectional cycle with a Tue-Thu midweek reversal (Steve).**
Rhymes with Q-alternation (H15) and Dave's runaway-count caution (H18) without
sharing lineage. Test: does gold's daily range actually partition into thirds
with reversal clustering after the third burst?

**H24. Time-stop: a trade showing no meaningful profit within ~2 hours has a
broken thesis and should be scratched (Steve, "not negotiable").** First
explicit time-stop in the register; directly portable to every strategy as
an exit wrapper. Test: A/B the master strategy with/without a 24-bar (5m)
time-stop on flat trades.

**H25. The ABC/123 swing-failure structure (fail to extend, break the prior
swing extreme) is a portable reversal AND continuation trigger, independent
of the instrument's noise level, when read off a noise-filtered construct
(Steve's price action / Renko mentor — INDEPENDENT voice #9, LOW credibility:
anecdotal PnL only).** This is the FIFTH independent voice landing on the
same break-of-structure shape (PBD break-in, QT Judas, Dave sweep-prerequisite,
Steve/MMM4x stop-hunt-reverse, now this). Promotion candidate for Belief
Review once our own backtest confirms on gold.

**H26. A "floating" candle/brick — the first bar to fully clear a moving-
average cluster after a structure break — is a valid, low-lag continuation
trigger (voice #9).** Directly codeable (renko_abc_scalper.pine). Test:
compare FLOAT-only signals vs ABC+FLOAT confluence signals for WR/PF on gold.

**H27. Counter-trend/counter-color run counting (tolerate ~3-4 opposing
bars as retracement, treat the 5th as thesis-broken) is a portable exit
rule (voice #9).** Converges with H8 (Valentini rejection-weakening) and
Dave's swing-maturity counts (H18) from a third independent angle — three
schools now count consecutive opposing structure as a decision trigger,
each with a different threshold (3, 3-4, 4-6). Test: does a fixed
counter-run exit outperform ATR-stop-only on the trendline core?

**H28. Nested-scale entries (coarse structure sets bias, fine structure
gives the entry with materially less stop distance) reduce risk without
changing the trade thesis (voice #9, his repeated point).** Not new in
principle -- multi-timeframe alignment (already 3 independent, see ledger)
-- but this is the first source proposing it via CONSTRUCT GRANULARITY
(box size) rather than time compression. Worth testing as an alternative
framing for the master engine's MTF layer.

**H29. Gold does not follow the clean ABC/123 float the way FX majors do --
"bipolar," chops for days then moves violently (voice #9's own STUDENT,
inside the transcript, contradicting his mentor in real time).** This is a
user-adjacent skeptical data point, not a school claim -- logged because it
directly bears on whether ANY of the ABC/123-family engines (this one, PBD,
Dave, QT Judas) transfers to gold at standard settings, or needs regime-
adaptive box/ATR sizing. Test before trusting float signals sized on FX-
calibrated brick constants.

**H30. Supply/demand zone quality is separable and filterable: freshness
(untested only), basing-candle count (fewer = stronger), departure speed/
size (bigger = stronger), and retest penetration depth (shallower = 
stronger leftover interest) (Wendell/OTA — INDEPENDENT voice #10, MEDIUM-
HIGH credibility: institutional education firm, ex-hedge-fund instructor,
explicit order-flow rationale, no backtest in source).** This is the
direct rework target for B2. Test: backtest wendell_zone_engine.pine
signals (DEMAND/SUPPLY shallow-retest touches) standalone on XAUUSD 5m;
compare PF against the retired v2 zone logic (0.731) and against B2's
invalidation bar (PF > 1.5).

**H31. Institutional zones are "walls" (higher-timeframe, hold/reverse
price) vs "chairs" (lower-timeframe, momentum pushes through); only trade
the timeframe you're on when price is AT one of its own fresh zones --
otherwise no trade regardless of setup quality ("don't trade in the
middle") (Wendell/OTA).** Converges with existing MTF-alignment
corroboration (now 5 independent: Cognitive Architecture, Valentini,
Kurisko, voice #9 Renko nesting, now Wendell walls/chairs) from yet
another angle -- but adds a hard NO-TRADE rule the others don't state
explicitly. Test: does gating the master engine to fire only when price
sits inside a wendell zone reduce trade count and raise PF, vs the
existing session-gate-only baseline?

**H32. Trend-cycle re-entry probability decays with each successive
re-entry after HTF bias confirms; the FIRST confirmed entry in a new
trend deserves the largest position size of the sequence (FX Master
Pattern school — INDEPENDENT voice #11, LOW-MED credibility: course/
software seller, mechanics kept, "belief-driven markets" philosophy
discarded).** New idea: existing scale-out rules govern exiting ONE
trade; this governs sizing ACROSS a sequence of same-trend re-entries.
Test: does entry-count-since-bias-confirm correlate with WR/R on gold
signals from any of our structure-break engines (PBD, Dave, QT Judas,
Wendell)? If yes, becomes a master-engine size multiplier.

**H33. Classifying the pre-news phase (contraction / expansion / trend)
predicts whether a scheduled release produces a real event candle,
independent of surprise size (voice #11's explicit position: news is
an accelerant of the CURRENT phase, not a separate regime).** Directly
testable against B4 (surprise size drives the move) on our existing
CPI event study: does pre-print phase classification add predictive
power beyond surprise magnitude alone? If not, B4 stands unchallenged;
if yes, phase-aware news filtering becomes a master-engine input.

**H34. Peak-to-peak FULL-ADR box stacking (1x/2x/3x from a locked
extreme, distinct from the existing ADR/3 per-level count) marks
consolidation/reversal zones (same lineage as voice #8/Steve — a
student mentoring call, NOT counted as a new independent voice).**
Test: does price actually cluster/consolidate at 1x/2x/3x full-ADR
distance from a locked peak on XAUUSD, independent of the ADR/3 level
count already coded? If both measures show real clustering, they may
be capturing the same effect at different granularities -- compare
directly rather than assume additive value.

**H35. EMA-stack bunching (13/50/200 within ~0.5x ATR of each other)
predicts low-quality chop; fanned/separated EMAs predict tradeable
trend (same lineage as voice #8).** Simple, cheap filter. Test: WR/PF
of every existing structure-break signal (PBD, Dave, QT Judas, Wendell,
this engine's own BRINKS/3-TAP) gated by emaBunched == false vs
ungated, on gold.

**H36. Break of structure is only reliable once the inducement (a
pullback swing that traps traders before it gets swept) has actually
been cleared -- an unconfirmed break lacking a swept IDM is lower
conviction (Alchemist/"White Seraph" PDF -- INDEPENDENT voice #12 for
the SMC market-structure layer, LOW-MED credibility: anonymous poster,
zero stats, heavily garbled machine translation on several sections).**
Distinct from every other sweep-reversal mechanic already in the
register (session-window JUDAS, zone-freshness Wendell, swing-maturity
Dave) -- this one gates the STRUCTURE BREAK ITSELF, on any swing,
regardless of session or zone. Test: WR/PF of IDM-confirmed BOS
(alchemist_smc_engine.pine "BOS IDM✓") vs unconfirmed breaks ("BOS no
IDM") on gold -- if confirmed breaks meaningfully outperform, IDM
gating becomes a hard veto candidate for every structure-break signal
in the master engine, not just this one.

**H37. A broken support/resistance level's ROLE inverts on retest
(SBR/RBS) -- this is a property distinct from zone freshness (Wendell,
H30): a level can be "spent" (no longer fresh) while its FLIPPED role
is still valid, or vice versa (Alchemist, voice #12).** Test: does
tagging the first post-flip retest specifically (vs. treating it as
just another zone touch) add signal quality beyond Wendell's freshness
score alone?

**H38. The Quasimodo 5-point swing-failure pattern (HH-HL-break to
fresh LL-retracement fails to reclaim the original HH-reversal) is a
higher-confirmation variant of plain break-of-structure, distinguished
by the extra "failed reclaim" step (Alchemist, voice #12).** Test:
does QML's extra confirmation step raise WR relative to a plain
ABC/123 (voice #9) or PBD break-in signal at the cost of fewer total
signals (fewer, better vs. more, noisier)?

INTRA-SCHOOL NOTE (voice #4/#13, 2026-07-20): the Alchemist PDF's
Quarterly Theory section (AMDX/XAMD, 90-min cycle table, Asia-range
liquidity, SMT-x-QT) is the SAME ICT-derived Quarterly Theory material
already in quarterly_theory.md -- a different teacher independently
arriving at (or teaching from) the identical framework. Logged as
same-school corroboration, NOT tallied as a new independent voice or
added to any corroboration count -- only the genuinely distinct SMC
market-structure content (IDM, SBR/RBS, QML) earned voice #12 status.
The PDF's own 90-minute table is column-garbled by translation and was
NOT used to re-derive engine timings; the existing clean primary-
source video remains authoritative there.

NOT BUILT, KEPT ON RECORD (per standing instruction to never discard
source material even when too garbled to codify): the Alchemist PDF's
"OCL" (Open-Close Level, described inconsistently across its two
source pages as a fixed-period moving average forming either a "P-P"
or "D-P D-P" pattern relative to HTF order blocks), "Fibo Circle," and
"Fibo Storyline" sections are preserved verbatim with the garbled
source language in alchemist_smc_concepts.md section 9, flagged as
unimplemented rather than deleted or paraphrased away -- if a future
source clarifies any of these concepts, the original text is still
there to cross-reference against.

EXECUTION-RISK NOTE (not a market-structure hypothesis, no H-number —
logged for completeness, see PLAYBOOK.md "Execution / Broker Risk"):
2026-07-20 "Forex James" broker-risk source argues scalping maximizes
exposure to broker-side slippage/requote manipulation and specifically
flags volatile-news fills (our CPI harness's exact operating window)
as worst-case for slippage. Backtests in this repo assume clean fills
and fixed commission/slippage constants (MEMORY.md: $0.07/oz, 5 ticks)
-- live execution around 8:30 ET prints should be expected to run
worse than backtest. No belief promoted/demoted; flagged as a live-
execution caveat on B3/B4 (CPI beliefs) and on the whole scalping
approach generally.

**H39. Missing candlestick patterns (Kicker, Marubozu, Three Inside/
Outside Up/Down, Rising/Falling Three Methods, Inverted Hammer/Hanging
Man, Dragonfly/Gravestone Doji, Spinning Top, Long-Legged Doji) carry
the same tiered reliability logic as the original Nison set — Kicker
and Marubozu in particular are historically well-regarded (Bulkowski)
despite being rare ("@Thechartcornerr" cheat sheet — public-domain
classical TA, names-only source, same credibility tier as the
original candlestick_patterns.md).** Extends the existing candlestick
engine in place, not a new voice. Test: do Kicker/Marubozu signals
(tier A/B) actually outperform tier-C additions (Spinning Top, plain
Long-Legged Doji) on gold, matching the reliability ranking assumed
here from general TA literature rather than this specific source?

**H40. Classic multi-swing chart patterns (Double/Triple Top/Bottom,
Head & Shoulders, triangles, wedges, flags, pennants, rectangles) add
signal beyond the single-candle and swing-structure patterns already
in the register (same source as H39).** Genuinely new pattern
CATEGORY for this repo (multi-pivot geometric patterns vs single-bar
candles or simple 2-3 point swing structures). Test: overlap and
incremental value vs. existing structure-break family (7+ sources) —
do chart-pattern breakouts fire at meaningfully different times/
locations than PBD/Dave/Wendell/Alchemist signals, or mostly restate
them in slower form? Cup & Handle and Diamond Top/Bottom explicitly
NOT built (no robust mechanical trigger without curve-fitting) —
logged, not guessed at.

**H41. A structural swing point is only STRONG once price breaks the
most recent OPPOSITE-type S/D zone; rejection without that break marks
it WEAK, and weakness never resolves retroactively (Pure PA/SMC —
INDEPENDENT voice #13, LOW-MED-to-MED credibility: no verified stats,
unusually precise mechanics).** A third distinct lens on structure
quality alongside Dave's swing-maturity count (H18) and Alchemist's
IDM-gated BOS (H36) -- three schools, three different tests for
"is this swing point trustworthy." Test: does STRONG-tagged structure
(pure_pa_smc_engine.pine) predict continuation better than untagged
breaks, independent of IDM or swing-count gating?

**H42. A valid S/D zone requires THREE factors together: IFC (a real
3-candle gap), a structure break/CHoCH, and a liquidity grab on the
way -- missing any one lowers probability (Pure PA/SMC, voice #13).**
Different checklist axis than Wendell's freshness/candle-count/
departure-speed (H30) -- this is about what the impulse LEFT BEHIND,
not how the base formed. Test: does a 3-factor-confirmed zone
(pure_pa_smc_engine.pine "DEM/SUP (fresh)") outperform a Wendell zone
lacking IFC confirmation, on gold?

**H43. Market regime can be tracked as "who's in control" -- whichever
side (supply/demand) most recently WON a zone interaction (broke the
opposing zone vs got rejected by it) -- and only the controlling side
should be traded without a confirmed flip (Pure PA/SMC, voice #13).**
A fourth distinct regime-classification construct in the register
(alongside PBD balance/imbalance, EMA-stack bias, HTF bias in FX
Master Pattern) -- this one is defined purely by the outcome of the
last zone fight. Test: does gating any structure-break signal by
"controlling side agrees" raise WR vs ungated, on gold?

**H44. Liquidity grabs and BOS are geometrically distinguishable: a
grab is a single wick-dominant candle, a real BOS is a body-close
break (often multi-candle) (Pure PA/SMC, voice #13).** Converges with
Steve/MMM4x's (voice #8) wick-vs-body-close distinction from an
unrelated lineage -- same observable, independently arrived at twice.
Already implemented as the lqGrabUp/lqGrabDn veto on BOS signals in
pure_pa_smc_engine.pine (a wick-dominant candle does NOT count as a
confirmed BOS). Test: does filtering out wick-dominant "BOS" claims
reduce false signals on gold?

INTRA-SCHOOL NOTE (H30, H13, 2026-07-20): Pure PA/SMC's mitigated/
unmitigated zone concept and its full MTF top-down workflow (H4 bias
-> 15m zones -> 5m refine -> 1m execute) are the SAME underlying ideas
as Wendell's zone-freshness (H30) and the register's dominant MTF-
alignment idea (now 7 independent constructions) -- logged as
corroboration there, not double-counted. The one genuine extension:
this source applies "unmitigated" to TP SELECTION as well as entries,
which Wendell's source doesn't make explicit.

INTRA-SCHOOL NOTE (H40, 2026-07-20): "Josh Trade"/Suraj Saini ebook is
the same 13 chart patterns as the "@Thechartcornerr" cheat sheet (H40)
-- same public-domain classical TA, different creator, no new pattern
types. Extended chart_pattern_engine.pine in place: measured-move
targets (explicit source rule for symmetrical triangles, generalized
to every pattern), optional volume-confirmation filter, and neckline/
boundary retest tagging. Not tallied as a new voice or new H-number --
same subject, genuinely useful implementation upgrade rather than new
theory. Test: do the new measured-move targets actually get hit more
often than a fixed-ATR target on the same breakout signals, on gold?

**H45. A volume-weighted price histogram's shape (D/P/b/Thin) classifies
regime: balanced POC near the middle = accumulation before a move
(D), POC skewed toward the range top/bottom = trending/rotating (P/b),
thin and even = strong trend with little accumulation time (Trader
Dale — INDEPENDENT voice #14, MEDIUM credibility: stated formal
finance credentials, no independently verified track record).**
Directly comparable to PBD's close-cluster value area (voice #3) --
same underlying concept, different weighting (volume vs. close-count).
Test: does the volume-weighted version (trader_dale_volume_profile_
engine.pine) classify regime more accurately than PBD's close-count
proxy on gold? If so, prefer it as the master engine's regime layer.

**H46. Heavy-volume price zones (HVN/Volume Clusters) work as S/R
because of accumulated positions being defended on retest, but ONLY
on the FIRST test -- later tests are explicitly lower probability
(Trader Dale, voice #14).** This is the SAME "leftover orders" logic
already dominant in the register (PBD, Wendell, MM Cycle) now
independently re-derived a fourth time with real volume as the
selection criterion instead of price structure or close-clustering.
The "first-test-only" rule specifically converges with Wendell's
freshness-decays-on-each-retest concept (H30) and Wendell's own
zone-quality checklist. Test: does volume-weighted HVN selection find
different (better or worse) zones than Wendell's candle-count/
departure-speed criteria on the same gold data?

**H47. Stop-loss placement in a low-volume pocket just beyond the
nearest heavy-volume zone is more informative than a fixed-distance
stop: if price actually reaches the low-volume area, that itself
signals real momentum against the trade, not noise (Trader Dale,
voice #14).** New, portable SL-placement idea -- distinct from every
existing stop rule in the register (ATR multiples, day-extreme
stops, scaled thirds). Paired with an explicit ADR-width guard
(10-20% of ADR) that's directly compatible with the ADR-based sizing
framework already used by Steve/MMM4x (voice #8). Test: A/B this SL
method against the master strategy's existing ATR-based stop.

**H48. The 4-Bar Fractal (close beats both the prior bar's and the
bar-3-back's high/low) is a reliable, cheap structure signal on any
timeframe (Hougaard, voice #15 — MEDIUM-HIGH credibility for this
register: audited multi-year trading-competition results cited).**
The simplest signal in the entire repo (no pivot/swing detection
needed at all). Test: standalone WR/PF of hougaard_4bar_fractal_
engine.pine's 4BF signals on gold, and specifically whether it adds
anything beyond the existing (heavier) structure-break family, or is
largely redundant with it.

**H49. Price/oscillator divergence occurring MID-TREND (not at a
fresh swing extreme) predicts trend CONTINUATION, not reversal
(Hougaard, voice #15).** Directly contradicts the standard reading of
divergence used everywhere else in this repo (Kurisko's SUPER
reversal signal, the CVD-at-S/R reversal veto in the master engine
and Trader Dale's Cumulative Delta Divergence, voice #14) -- all of
which treat the SAME observable (price/indicator disagreement) as a
reversal tell. UNRESOLVED TENSION, explicitly logged rather than
silently favoring either reading: the two claims may both be correct
in different contexts (divergence AT a fresh extreme = reversal tell;
divergence mid-trend, away from any extreme = continuation tell), but
this needs our own data to settle, not assumption. Test: split
divergence signals by whether they occur at a fresh swing extreme vs.
mid-trend, and check whether the two subsets actually predict opposite
outcomes on gold as this framing implies.

**H50. Position-sizing has a portable "scale-in" rule to complement
the register's existing scale-out convention: the first add to a
winner should only happen where the ORIGINAL position's stop can move
to breakeven, and that breakeven level becomes the stop for the
second position too -- so total risk never increases as size is added
(Hougaard, voice #15).** New, distinct from the existing 1/3@1R
scale-out rule (which governs exits) and from Roppel's scaled-stop
idea (which governs stop placement) -- this one governs entries added
mid-trade. Test: A/B a scale-in variant of the master strategy against
the existing single-entry, single-exit-ladder approach.

INTRA-SCHOOL NOTE (2026-07-20): Hougaard's fade-the-short-term-in-
direction-of-the-long-term-trend, ranging-to-trending-to-ranging
regime alternation, and fake-out/ABCD sweep-reversal shape are all
restatements of ideas already dominant in this register (MTF
alignment now 8 independent constructions; Q-alternation/contraction-
expansion-trend regime cycling now a 3rd independent arrival; sweep-
reversal now past 8 sources). Logged as corroboration, not new
H-numbers or a new voice tally entry for those specific ideas -- only
H48-H50 above are genuinely new mechanics from this source.

**H51. Square-of-Nine horizontal price levels (successive 90/180-degree
rotations of `(SQRT(N)+factor)^2` from a major swing pivot) act as
support/resistance (Gann Square of Nine, voice #16 -- LOW-MEDIUM
credibility, see playbook: Gann's own track record is unverified
folklore, the technique itself is real math independently credited
to Carl Futia for the degree-conversion formula).** Genuinely new
mechanism -- nothing else in this register derives levels from a
square-root spiral. Untested whether the source's 3-digit-price-
normalization convention (built for equity indices) transfers to
XAUUSD's 4-digit price level -- flagged as the single biggest
transferability risk, toggle exists to disable.

**H52. Square-of-Nine vertical time spacing (`round(sqrt(3-digit
anchor price))` bars, constant regardless of timeframe) marks
time-based reaction points (Gann Square of Nine, voice #16).** New
time-cycle idea, distinct from every existing time-window rule in
this register (session windows, quarterly-theory clocks) -- this one
derives its cycle length from price itself, not from a clock. Every
worked example in the source is hourly/daily/weekly on equity
indices; applying it to 5m gold bars is a much bigger timeframe jump
than any other source folded into this repo so far -- explicitly
untested.

**H53. A Square-of-Nine "Roadmap Chart" diagonal channel (3 parallel
lines, same slope, anchored off a major pivot) contains price for the
life of a trend; a 2-consecutive-close penetration of the OUTER
channel bound signals the trend may be changing (Gann Square of Nine,
voice #16).** New channel-based trend-invalidation idea. The
2-consecutive-close confirmation requirement is the same discipline
already used elsewhere in this repo (e.g. the master engine's
close-confirmed structure breaks) -- weak methodological corroboration
of "confirm on close, not on a single wick," not a new count for that
existing idea since the underlying construct (a Gann channel) is
itself new.

**H54. "Squaring price and time" -- converting a price range and an
elapsed bar/day count to degrees via `MOD((SQRT(N)*180)-225,360)` and
checking whether they land within a few degrees of a 90-degree
multiple of each other -- marks high-probability turning points (Gann
Square of Nine, voice #16, formula credited to Carl Futia).** New
mechanism. The source is explicit this is confluence, not a
standalone trigger: "most trend changes coincide with SOME squaring,
but not every squaring produces a trend change." Consistent with this
repo's whole design (every engine here is observation-layer
confluence, never solo).

**H55. Bar-counts since a major pivot landing on Gann's own
"squares 1-19" watchlist (16, 25, 36, 49, 64, 81, 100, 121, 144, 169,
196, 225, 256, 289, 324, 361 -- from his own 1953 signed appendix
note, recovered from the scanned facsimile image, not the garbled
text extraction) mark watch points for a change in trend (W.D. Gann
himself, via the Square of Nine appendix).** The one piece of Gann's
own numerology-framed appendix material (Master Numbers 3/5/7/9/12,
Biblical references, "Great Yearly Time Cycle") that reduces to a
falsifiable, implementable mechanic independent of the numerology
framing -- everything else in that appendix is preserved verbatim in
the playbook but explicitly not built (no falsifiable trigger).

INTRA-SCHOOL NOTE (2026-07-20, Gann appendix): the "gravity center /
halfway point" concept in Gann's own 1953 note (midpoint of a price
range or of the Master Square of 144 as a location where countertrend
moves start/end) is weak corroboration of the existing 50%-
equilibrium marker (Pure PA/SMC engine, H44) from a totally
independent, ~90-year-older source -- not counted as a new voice or
a new H-number for that specific idea, since it restates rather than
extends it.

**H56. Cup & Handle (and its inverse) is a tradeable continuation
pattern: two similar-height "rim" pivots over a wide/deep rounded
trough, followed by a short shallow secondary dip at the rim (the
"handle"), resolving in a breakout through the rim in the trough's
original direction ("@Thechartcornerr" chart-pattern cheat sheet,
image content missed in the original text-only pass).** Same
credibility tier as every other pattern in this family (public-domain
classical TA, no track record offered). Notable for what it corrects
about our own process, not just the market: the first pass on this
source read text/labels only and concluded the pattern was "too
subjective to codify reliably" -- re-rendering and viewing the actual
page images showed the diagram gives exactly the same kind of
informal-but-usable geometric definition every other pattern in this
file already runs on (width/depth minimums standing in for
"rounded," same treatment `headMinAtr` gives "prominent" on Head &
Shoulders). Implemented in chart_pattern_engine.pine v3.

**H57. Diamond Top / Diamond Bottom is a tradeable reversal pattern:
a broadening (expanding highs/lows) formation immediately followed by
a narrowing symmetrical triangle sharing its widest point, breakout
direction determines top vs bottom ("@Thechartcornerr" cheat sheet,
same missed-image correction as H56).** Structurally this is two
already-implemented shapes (a broadening formation + a symmetrical
triangle) chained together, not a genuinely novel geometry -- lowers
the bar for confidence that this is buildable without curve-fitting.
Implemented in chart_pattern_engine.pine v3, gated on tracking 6
pivots per side to see both the broadening and narrowing halves.

**H58. Head & Shoulders breakdown probability increases specifically
when the neckline slopes flat-to-down AND the right shoulder is
smaller than or equal to the left shoulder (Josh Trade/Suraj Saini
ebook, page 25 text, precise and quotable -- re-surfaced on full
re-review, not missed from images this time, just not previously
cross-checked against the engine's actual H&S gating logic).** A
genuine refinement the existing engine never checked (it only verified
head prominence over both shoulders). Implemented as an informational
`hnsHighProb` tag on the existing H&S signal rather than a hard gate,
matching the source's own "probability increases" framing rather than
a binary requirement -- test whether gating on it improves precision
before promoting it to a hard filter.

**H59. Chart-pattern targets should be measured as a fixed multiple of
initial risk (dominant ratio 1:3, one example 1:4), anchored at the
post-breakout RETEST bar, rather than as the pattern's own geometric
height projected from the breakout bar (Josh Trade/Suraj Saini ebook,
worked real-chart examples -- re-surfaced on full re-review).**
DIRECTLY COMPETING with the already-implemented v2 measured-move
target convention used by every pattern in chart_pattern_engine.pine
(and, more broadly, with this project's general habit of pattern-
height/swing-based target measurement). Not adjudicated here --
implemented as a selectable alternate (`showRR`, off by default) so
the two methodologies can be A/B tested against each other on our own
data rather than one silently overriding the other.

INTRA-SESSION PROCESS NOTE (2026-07-20): a user prompt to re-review
EVERY previously-processed source's page IMAGES (not just their
extracted text) surfaced H56-H59 above, plus corrections to the
Quarterly Theory and Gann engines logged elsewhere in this file. Root
cause: several PDF sources were processed with text-only extraction
(pypdf) at times when the page-image rendering path wasn't available,
and that limitation was not revisited once the workaround (pymupdf
page rendering) became routine later in the project. Two large,
heavily-illustrated sources (Alchemist SMC PDF, 70pp; Josh Trade
ebook, 34pp) were re-swept via background research agents rather than
read inline, given their size -- their findings are logged separately
where applied. Standing takeaway: when a source is described as
"garbled," "too subjective," or "unclear from text," that is a
statement about the text-extraction pass, not necessarily about the
source itself -- always check whether an unrendered image is the
actual reason before concluding a mechanic can't be built.

**H60. Fibo Storyline: retracing into a dense 0.618-0.822 band of a
custom (non-standard) Fibonacci ratio set, on the dominant swing leg,
marks a high-probability continuation entry ("White Seraph"/Alchemist
PDF, voice #12 -- LOW-MEDIUM credibility, anonymous, zero stats, poor
machine translation).** RECLASSIFIED from "not built" after re-
reviewing the source's page images turned up its exact tool-settings
screenshot (ratio set: 0, .109, .127, .145, .214, .232, .25, .618,
.636, .654, .786, .804, .822, 1) -- the text/caption extraction alone
had preserved none of these numbers. A second stage ("adding wood"):
after the first entry, shifting to a lower timeframe and taking a
second Fib-zone entry as the trend continues -- implemented here as a
same-timeframe re-application instead of a literal timeframe shift,
flagged as a simplification. Distinct from every other fib-based idea
in this register (none use this specific ratio set or a two-stage
same-leg-family scale-in).

**H61. Fibo Circle: a Fibonacci EXTENSION (ratios 1.893 and 2.0) of
the small internal retracement that forms just after a dominant swing
leg projects a retest-entry level in the direction of that leg
("White Seraph"/Alchemist PDF, voice #12, same credibility tier as
H60).** Also reclassified from "too vague" after the page-image
re-review recovered the source's own stated extension ratios (1.893,
2.0 -- both non-standard, not the usual 1.618/2.618). Conceptually
adjacent to this register's other measured-move/extension ideas
(chart-pattern targets, QT price-time squaring) but the specific
mechanism -- extending an INTERNAL post-leg retracement rather than
the leg itself -- is new.

Both H60 and H61 sit in the same lower-confidence tier as the rest of
this source (translated, not fully unambiguous even after the image
re-review per the research agent's own report) -- shipped off by
default in alchemist_smc_engine.pine, meant for standalone A/B testing
before any confluence-stack inclusion.

**H62. Trend position measured against a fixed-rate geometric angle
fan (1x1/2x1/4x1/8x1, "the death angle" at 45°) predicts trend
strength/weakness -- holding above steeper angles is a stronger
position, breaking below any held angle indicates a decline to the
next angle below it (W.D. Gann, "Master Commodities Course," voice
#16, same LOW-MEDIUM credibility tier as the rest of this source).**
Genuinely new mechanism relative to everything already in this
register -- nothing else here derives a trend-strength LADDER (not
just a single line) from a fixed price-per-time rate. This is the one
piece of classical "Gann Angles" the earlier TradingFives book
explicitly declined to cover ("we make no claims... W.D. Gann made
all his charts by hand"). The 1x1 rate itself is NOT source-given for
gold -- implemented as `ATR(14) x 0.25` by default, our own
convention matching Gann's own stated discretion ("pick a scale where
the 45° looks right"), not a literal transcription. Untested whether
an angle fan calibrated this way behaves sensibly on 5m gold at all;
every worked example in the source is daily/weekly/monthly grain,
cotton, or egg futures.

**H63. A single bar making a new N-bar extreme that closes in the
weak half of its own range (or beyond the open) is a standalone
reversal signal, no confirmation bar required ("Signal Day," W.D.
Gann, same source as H62).** Notable for what it CONTRADICTS about
this repo's own design discipline, not just the market: nearly every
other single-bar/pattern signal in this register requires a
confirmation close (the confirmation-before-entry family is the
STRONGEST idea here, 8+ independent sources) — Signal Day is Gann's
own explicit exception, treated as immediately actionable. Implemented
as its own tagged signal, NOT folded into the confirmation-required
default path, so it can be A/B tested on its own terms rather than
diluted by a discipline the source itself doesn't apply to it.

**H64. UNRESOLVED TENSION: a level tested a FOURTH time nearly always
breaks through, not fades again (W.D. Gann, same source as H62-H63)
— directly opposed to every double/triple-tap fade idea already in
this register (MM Cycle's 3-tap fade H22, PBD, Wendell), all of which
treat the 3rd tap as the STRONGEST fade signal and say nothing about
a 4th.** Not adjudicated here. Possible reconciliation: the existing
3-tap-fade sources may simply not have tested what happens on a 4th
touch (survivorship in the data they drew from, not necessarily a
real contradiction) — or Gann's rule may be right and the existing
3-tap conviction ceiling should itself be revisited. Flagged for our
own backtest: track win rate specifically on trades taken AT a 4th
touch of a level vs. the existing 3rd-touch-fade baseline.

INTRA-SCHOOL NOTE (Gann, 2026-07-20): the Master Commodities Course's
extensive numbered trading-rule lists (29-rule Trend Line/3-Day-Chart
system, pyramiding rules, money-management sizing) are structurally
close to this register's existing swing/structure-break family (IDM-
gated BOS, Dave's swing count, MM Cycle's tap-fade) and to the
existing scale-in idea (H50) -- logged as corroboration of those
existing mechanisms, not new H-numbers, since the numeric thresholds
(cents-per-bushel, dollars-per-contract, 1940s-50s commodity scale)
don't transfer to XAUUSD and the underlying structural idea (trade
with the swing chart's main trend, add on favorable moves, cut on the
first break of the last swing point) is already represented. The
extensive Great/Minor Time Cycle and seasonal-anniversary material
(90/60/49-50/30/20/13-year cycles; commodity-specific planting/
harvest/crop-report calendars) is explicitly agricultural-commodity
seasonality with no mechanical analogue for a non-seasonal, 24/7-traded
metal -- preserved in the playbook per the never-discard rule but not
built, and not logged as a hypothesis since applying it to gold would
be fabrication, not extension. The Hexagon Chart, Master 12/144
squares, and letter-count-modulus squares (Chapter 17-19) are genuinely
new geometric constructions but sit well past this register's
falsifiability bar without a clearer trigger than what the existing
squares-1-to-19 watchlist already provides -- documented, not built.

**H65. A rolling-correlation-confirmed cross-asset lag (gold hasn't
caught up to a reference asset's recent move, measured in ATRs) marks
a directional catch-up opportunity ("The Big Secret of Intermarket
Trading," anonymous PDF/lead-gen funnel, voice #17 -- LOW credibility:
explicit "100% profitable"/"100% winning trades" marketing language,
zero track record, every source example is a hindsight-annotated
screenshot with no actual specified trigger rule, and the source's own
text captions don't reliably match the chart images underneath them).**
Genuinely new mechanism -- the closest existing idea (SMT divergence,
Quarterly Theory) is a snapshot comparison at a specific sweep moment;
this is a continuous rolling-correlation-gated magnitude-gap
comparison instead, structurally different. Built as OUR OWN sober
operationalization of the underlying (real, well-known) intermarket
lead-lag concept, not a transcription of the source's method, since
the source doesn't actually give one -- added a correlation-strength
gate (default |corr| >= 0.5 over 100 bars) the source never applies at
all, since every one of its claimed examples could equally be a
cherry-picked week where an otherwise-inconsistent correlation
happened to hold. The source's specific claimed lag durations (1h,
3h, 20h across different pairs) are NOT hard-coded -- asserted from a
handful of screenshots, not measured, hard-coding them would fabricate
precision the source doesn't have. `lagWindow` is a plain user input
instead. Test standalone; this is one of the lower-confidence engines
in the repo by source quality alone, independent of whether the
underlying mechanism eventually proves out.

**H66. A static, non-recalculated grid of round-number price levels
(large quarters = 1/4-divisions of a fixed range between "major whole
numbers," small quarters = 1/4-divisions of a finer sub-range) acts as
support/resistance, and a move is considered to have "successfully
completed" once price comes within one small-quarter width of the
targeted level, whether short of it or overshooting past it (Ilian
Yotov, "The Quarters Theory," voice #18 -- LOW-MEDIUM
credibility: named published author, but zero backtested statistics
in either source transcript).** Genuinely new mechanism: nothing else
in this register derives levels purely from modulo arithmetic on
absolute price with zero reference to swing history, pivots, or
market structure at all -- closest existing idea (round numbers as
magnets, Valentini/Roppel, 2 independent sources) is a much looser
"round numbers matter" observation, not a precise nested 4-way
division with a stated completion tolerance. NAMING COLLISION: this
is UNRELATED to the existing "Quarterly Theory" (voice #4, Trader
Daye/ICT lineage, time-based) despite the near-identical name --
different author, different book, different mechanism entirely. Scale
chosen for gold ($100 major handle, our own convention) is untested;
every source example is a G7 FX pair, gold is never mentioned.

**H67. A "reversal trigger wave" that breaks the most recent counter-
trend swing extreme starts a new trend cycle; each subsequent same-
direction wave must exceed the prior same-direction wave's extreme to
extend the cycle, and failing to do so signals an opposing reversal
trigger wave is likely forming (Ilian Yotov's "Trend Waves," same
source as H66).** The trigger condition itself corroborates this
register's existing structure-break/BOS family (yet another
independent construction of "break of the last counter-trend extreme
= trend change") -- not counted as a new H-number for that piece. What
IS new: the wave-numbering/naming scheme (Reversal Trigger ->
Progressive -> Conclusive -> unlimited Consecutive waves, explicitly
REJECTING Elliott's fixed 5-wave-plus-ABC structure and any notion of
"complex" sub-waves) and, most notably, the **100%-retracement rule**:
a correction that retraces more than 100% of the wave it follows stops
being a correction and becomes a new reversal trigger wave in the
opposite direction, restarting the count. This is a crisp, falsifiable
rule not present anywhere else in the register.

**H68. A large quarter target that takes longer than an expected bar
budget to reach ("3-Day Rule," Ilian Yotov's official published
glossary, v2 correction pass on H66/H67, same LOW-MEDIUM credibility)
signals exhaustion of the move and increased odds of reversal before
completion; separately, three or more consecutive large-quarter
completions in the same direction ("Large Quarter Corrections") signal
overbought/oversold risk independent of the Trend Wave count in H67.**
Both are new, distinct, falsifiable timing/exhaustion rules not derivable
from H66/H67 alone -- the webinar transcripts never mentioned either.
The "3 days" duration is FX-session language from the source and has
been translated to a bar-count budget (`maxBarsToComplete`, default 864)
as OUR OWN untested convention, not a source-given number, exactly like
the H66 gold price-scale adaptation. Also clarified by this v2 pass but
NOT logged as a separate H-number (definitional, not a new falsifiable
mechanism): the glossary distinguishes THREE separate "half point"
concepts -- Half Point (of a small quarter), Half Point of a Large
Quarter (the new $50-scale midpoint added to the grid this pass), and
Major Half Point (already built under H66) -- and separately distinguishes
"Extended Trend Wave Cycle" (wave count > 3, what H67/`isExtended` already
measures) from "Extended Trend Waves" (a single wave lasting more than 5
consecutive bars, a duration-based definition NOT built). The glossary's
Time Stops concept corroborates this register's existing H24
(time-based invalidation) rather than adding a new mechanism.

**H69. A moving average's responsiveness should itself be gated by
proximity to structure: dampening an adaptive MA's smoothing constant
near an HTF key level, then treating a crossover between the damped
and undamped versions of the SAME MA as a "level acceptance" signal,
should outperform either a plain KAMA cross or a static key-level
touch alone (source: two user-supplied Pine snippets, not a trader
school -- "KL Adaptive MA" unattributed + "Key Levels SpacemanBTC IDWM
V13.1" by @sbtnc for the level computation only).** Genuinely new
mechanism for this register: every other engine here treats HTF levels
as static trigger lines (touch/sweep/reject); this is the first case
of a key level modulating an indicator's INTERNAL math (its
adaptivity) rather than gating an entry directly. Adjacent to but
distinct from the confirmation-before-entry family (the cross itself
functions as the confirmation) and from the "wall" location-gate
family used in reversal_sniper_strategy.pine (same location logic,
applied to an MA signal instead of a candle pattern). UNTESTED --
brand new construct, zero backtest, built same day as creation. Per
the 2026-07-20 standing rule, this does not get sizing weight or
"proven" language until backtested on a real sample.

**H70. Dividing a price swing into eighths (0/12.5/25/37.5/50/62.5/75/
87.5/100%) produces more useful support/resistance than standard
Fibonacci ratios, with the 50% level as the single most significant
point; the SAME eighths-retracement geometry applied to RSI's own
swings (not just static 70/30 thresholds) adds genuine confluence
(Hima Reddy, "The Trading Methodologies of W.D. Gann," voice #19,
MEDIUM credibility -- named CMT-credentialed author, worked chart
examples, no aggregate backtest stats).** Distinct from every existing
retracement idea in this register (the Fibo Storyline/Circle custom
ratio sets, voice #12) -- eighths are a flat linear division, not a
golden-ratio-derived set, and applying the SAME grid to an oscillator's
own path (not just the price chart) is a genuinely new technique here.
Gold-scale caveat does not apply -- this is a pure percentage/ratio
construction, no source-specific price scale to adapt.

**H71. A key level that is tested (price probes through it) but the
bar/period closes back on the original side within a 2-bar window
often signals the level HOLDS and the prior trend continues (same
source as H70, "test failure" concept).** Corroborates this register's
existing confirmation-before-entry family but with a crisp, falsifiable
TIME BOUND (2 bars) not present in any prior confirmation-family
source -- most other sources here require "a confirmation candle"
without specifying how many bars the market has to fail the test.

**H72. A trendline's reliability can be paired with a PARALLEL channel
line, not anchored to a second trendline touch but to the OPPOSITE
price extreme of the trendline's own origin bar, projected forward in
time as an early reversal alert (same source as H70/H71).** Genuinely
new construction in this register -- every other trendline/channel
idea here (the OLS trendline breakout core, the Fibo/quarters
projections) anchors channels to a second independently-confirmed
point, not to the origin bar's own opposite extreme. Also of note:
this source independently corroborates H64's tension (a level tested
3 times is MORE likely to break on the 4th test than hold) via Gann's
own "tested three times" critique of standard trendlines, cited
directly by Reddy -- 3rd independent corroboration of that side of the
H64 tension, still not adjudicated against the register's dominant
3-tap-fade family.

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

INTRA-SCHOOL NOTE (Quarterly Theory, v6, 2026-07-20): re-review of the
primary compiled QT PDF found one embedded table graphic ("A little time
table") the original text-extraction pass had silently dropped -- pypdf
only pulls a page's text layer, and this table exists solely as a
picture. Rendering the page directly (pymupdf) recovered it. Confirmed
the Week/Month quarter mappings already coded are correct. Added a
genuinely new detail: the source's YEARLY quarters are asymmetric
(Q1=Jan-Apr, Q2=Apr-May containing the 1-April true open, Q3=May-Nov,
Q4=Dec-only) -- not previously documented beyond "true open = first
Monday of April." quarterly_theory_engine.pine now plots a
`trueYearOpen` marker. Also surfaced an unresolved discrepancy: the same
table's "Day" row cell formatting doesn't cleanly match the already-
coded 4-way Asia/London/NY-AM/NY-PM day-quarter split from the primary
spoken source (v3) -- flagged, not silently resolved either direction
since a cramped cheat-sheet table cell is weaker evidence than the
primary video it's compiled from.

INTRA-SCHOOL NOTE (voice #8, 2026-07-20): a second transcript (student
mentoring call, "Nick" and "GP") teaches the SAME school as Steve/MMM4x —
one participant explicitly attributes the "big fat M/W" terminology to
Steve by name. Logged as a v2 elaboration of voice #8 in steve_mm_cycle.md
and folded into mm_cycle_engine.pine (EMA stack, peak-to-peak full-ADR
box stack, TDI shark-fin proxy, railroad tracks, ID50 reentry, standard
pivots) — deliberately NOT counted as a new independent voice or added
to any corroboration tally. Same-lineage sources restate/elaborate; only
genuinely independent lineages should move the corroboration counts,
or the register's "independent voices" become a vanity metric instead
of real evidentiary weight.

INTRA-SCHOOL NOTE v2 (H13, 2026-07-20): second primary-source video, same
lineage, adds exact 90-min sub-quarter windows for all 4 sessions (engine
now marks them) and the precise AMDX vs XAMD quarter-to-phase mapping
(previously only "shifted one quarter" — now: AMDX Q1=Accumulate/Q2=
Manipulate/Q3=Distribute/Q4=X; XAMD Q1=X/Q2=Accumulate/Q3=Manipulate/Q4=
Distribute). Also states Friday is excluded from the weekly quarter count
("its own specific function," unexplained) — independently echoes Steve/
MMM4x's (voice #8) unrelated Friday-is-different rule. Engine's AMDX/XAMD
label is our own range-based heuristic proxy for the source's stated
judgment call, not a rule from the source — flagged as such in-code.

INTRA-SCHOOL NOTE v3 (H13, 2026-07-20): "857483891QuarterlyTheory" PDF
re-supplied with a working text layer (same document previously logged
as "compilation #2, mostly images" with an unrecoverable text layer) --
CONFIRMS the v2 additions (TF pairing model, PSP, SSMT, "every Q open is
a True Open") were extracted correctly the first time, no corrections
needed. Adds one new engine-worthy detail: a full-grade PSP/SMT requires
an ASSET TRIAD (two failed-confirmation references), not just one --
engine gained an optional 2nd reference symbol (`useTriad` toggle,
default DXY, off by default) so the stricter triad version can be A/B'd
against the existing single-reference SMT. "iFVG" mentioned as a PSP-
entry comparison but not detailed in source -- preserved, not built.
No new H-number (this is a same-lineage confirmation + engine
refinement, not a new independent claim).

## Contradiction Tallies (3+ independent -> Belief Review)
- Break-of-structure / swing-failure / manipulation-leg family (B2 fix,
  PBD break-in, now including plain ABC/123, Wendell drop-base-rally/
  rally-base-drop, and voice #11's Expansion phase): 7 SUPPORT (PBD
  break-in, QT Judas swing, Dave sweep-prerequisite, Steve/MMM4x stop-
  hunt-reverse, voice #9 ABC/123, voice #10 Wendell zones, voice #11
  Expansion-phase whipsaw) vs 1 AGAINST (Valentini). Note: voice #11's
  version is a full PHASE (bidirectional, can run for many bars) rather
  than a single sweep-and-reclaim event — same underlying claim (price
  fakes out both sides before the real move), looser mechanics. THRESHOLD
  CROSSED, decisively: register-supported doctrine, final promotion
  pending our own backtest of Reversal Sniper v3 / JUDAS / Wendell zones
  on gold.
  WEAK CORROBORATION LOGGED, not tallied as a full voice (2026-07-20):
  a short "Forex James" YouTube-style clip on fakeouts/stop-hunts/
  big-candle induction restates this exact family with zero new
  falsifiable mechanics -- no timing windows, no pip/ATR thresholds,
  no multi-candle criteria beyond what's already coded in Wendell
  zones, Dave swing structure, MM Cycle, QT Judas, and effort/result.
  No new playbook or engine created; would be pure duplication of
  existing code. Counted as informal reinforcement only, NOT as an
  8th independent voice -- per register discipline, corroboration
  counts should track genuinely new mechanics, not every video that
  restates the same idea in general terms.
- Consecutive-opposing-bar counting as a decision trigger (entry OR exit):
  3 independent, 3 different thresholds (Valentini ~3 rejections -> stand
  down, Dave 4-6 matured swings -> reversal permitted, voice #9 4 counter-
  bricks -> exit). Same observable, three uses (entry veto, entry permit,
  exit). Worth its own comparison study once master engine has all three
  wired in.
- Static S/R levels as standalone edge: 1 AGAINST (Steve: consolidation zones
  are manufactured to bait line-drawers) vs level-based entries used by PBD
  (value areas) and Dave (POIs). Note: Steve still trades LEVELS (day extremes,
  Asia range) — his objection is to historical S/R lines, so the tension is
  narrower than it looks. Watch, don't act.
- H5 momentum-over-reversal: CONTESTED 2v2 — support: Valentini (measured),
  Roppel ("never buy weakness"); counter: Kurisko (confirmed divergence
  reversals), QT school (true-open reversals). Only our own backtest splits this.

## Corroboration Ledger (independent sources per idea)
- Confirmation-before-entry family: 4 independent (our CPI event study,
  PBD close-count, Valentini break-and-test, Kurisko confirmed turn).
  STRONGEST idea in the register.
- Multi-timeframe alignment before sizing: 8 independent (Cognitive
  Architecture, Valentini 15m->1m->15s stack, Kurisko quad bands, voice #9
  nested Renko brick-size stack, Wendell walls-vs-chairs, voice #11's
  HTF-bias/LTF-entry pattern, voice #13's H4-direction/15m-zone/5m-refine/
  1m-execute cascade, Hougaard's fade-short-term-in-direction-of-long-term
  — eight schools, eight different mechanics, same structural conclusion:
  never size a trade without checking a higher timeframe first).
- Confirmation-before-entry: now 8 independent (add Steve's confirmed-hammer-
  close + zone-shift confirmation to CPI study, PBD, Valentini, Kurisko, QT,
  Ario, Dave).
- B1 session windows: +1 independent (Steve's 03:30 London / 09:30 NY-equities
  anchors land inside our backtested windows via a completely different theory).
- First-NY-hour caution: 2 independent (Valentini, Dave) — formal A/B needed
  vs our backtested 8:30-11 B1 window (does excluding 9:30-10:30 help?).
  COUNTERPOINT: Steve puts his 2nd-best entry AT 09:30-09:45 — 2v1 contested.
- Flat-by-end-of-day / no weekend carry: 2 independent (Steve hard rule;
  user profile scalping style) — already our default, now register-backed.
- Time-stop on flat trades: 1 source (Steve, H24) — new idea, cheap to test.
- H8 rejection-weakening / failure counting: 2 independent (Valentini
  live rules; Ario stacked-wick failure counting).
- B1 session windows (London + NY open): independent corroboration from
  Quarterly Theory Q2-expansion mapping (different reasoning, same windows).
- Cushion-based risk escalation (risk profits, protect principal): 2
  independent (Valentini, Roppel).
- Round numbers as magnets/failure points: 2 independent (Valentini, Roppel).
- Absorption (heavy two-sided volume without price progress = reversal
  tell): 2 independent (Valentini's effort/result volume+wick proxy,
  Trader Dale's Confirmation Setup #2) — same concept, same underlying
  data limitation (both are proxies for footprint data we don't have).
- Price/CVD divergence at S/R as a reversal confirmation: 2 independent
  (Valentini's CVD-divergence veto in the master engine, Trader Dale's
  Cumulative Delta Divergence, Confirmation Setup #4) — Trader Dale's
  book independently validates the CVD-from-candle-direction proxy's
  design intent by explaining the real footprint data it approximates.
- "Leftover orders defend on retest, first test only" family (S/R
  zone mechanism): now 4 independent constructions (PBD value area,
  Wendell zone freshness, MM Cycle stop-hunt zones, Trader Dale's
  volume-weighted HVN) — same causal story, four different selection
  criteria (auction close-count, candle-count/departure-speed, time-
  of-day/ADR geometry, real traded volume).

## Retired Beliefs
(none yet)

---

## H73. Multi-voice corroboration beats single-mechanic entries.
Requiring N-of-M independent voice-votes (each a distinct trader's
codeable hypothesis) produces better expectancy than any one entry
mechanic chosen by hand.

**Evidence FOR (2026-07-28, first real test):**
multivoice_confluence_engine.pine, XAUUSD 15m, Feb 2 - Jul 28 2026:
521 trades, WR 44.15%, PF 1.093, +15.25%, max DD 11.90%.
Six single-mechanic engines on the same repo, same asset, tested over
Jun-Jul: OMNIBUS four-model 0.843, key-to-key 0.886, trendline x key
levels 0.882, trendline+HTF-bias 0.819, clean-signal and top/bottom
variants 0.67-1.11 (only the topbottom engine's tuned 40-trade run
ever exceeded 1.0, on a sample far too small to count).

**Confound (stated, not hidden):** the multi-voice run also moved 5m
-> 15m. Timeframe and logic changed together. A 15m single-mechanic
control run, or a 5m multi-voice run, is required to attribute the
gain. Until then this is SUPPORTED, not CONFIRMED.

**Invalidation:** if raising minScore (more voices required to agree)
does NOT improve PF, the votes are not carrying independent signal and
this hypothesis fails regardless of the headline number.

**Register impact:** this is the first empirical support for the
premise the whole 21-voice register was built on. It also retroactively
explains the PF 0.82-0.89 plateau: those engines each implemented ~5
generic mechanics and cited the register in comments only (see the
2026-07-27 register-usage audit).

---

### H74 — Level-to-level exits require level spacing commensurate with the timeframe's ATR
- **Status:** SUPPORTED (one run, one instrument, one timeframe)
- **Claim:** Using drawn key levels to set stop distance and take-profit
  targets only works when the typical gap between adjacent levels is on
  the same order as the timeframe's ATR. Where levels are far apart
  relative to the bar range, level-derived stops get clamped to the risk
  ceiling and level-derived targets move out of reach within the holding
  period, so win rate collapses even though entry quality is unchanged.
- **Evidence:** XAUUSD 15m, Feb 2 – Jul 28 2026. Turning on key-level
  stops + key-level targets together took the Multi-Voice engine from
  PF 1.093 / WR 44.15% / +15.25% to PF 0.892 / WR 34.06% / −14.19%, with
  trade count essentially unchanged (521 → 461). Entries held; exits
  broke. The drawn set on 15m gold is dominated by D/W/M/Q/Y levels.
- **Mechanism:** stop = max(adverse wick, distance to nearest level) gets
  clamped at maxStopAtr; TP1 = minTP1R × that inflated stop; the pair
  compounds into a round trip the 48-bar time stop cannot survive.
- **Invalidation:** if `useKLStops` OFF with `useKLTargets` still ON
  recovers PF toward 1.09, the claim narrows to stops only and targets
  are exonerated. If neither recovers, the entry-side changes
  (`klFullSweep`, `vOn21`) are implicated instead and H74 is wrong about
  the mechanism.
- **Consequence if it holds:** level-to-level belongs on a timeframe
  whose ATR is comparable to level spacing (1H/4H for D/W/M levels), or
  needs intraday levels (session H/L, 4H, prev-day) enabled and the
  higher-degree ones excluded from the stop/target calculation.
- **Relation to H73:** independent. H73 (multi-voice corroboration) is
  still untested — its own decisive test (minScore 6→8→10) has still not
  been run, and this result does not bear on it because entries barely
  changed.

---

### H75 — Any profit target degrades a trailing-stop trend system
- **Status:** CONFIRMED (tested at four take-sizes and four grid scales,
  on two independent halves plus the full 6.7 years)
- **Claim:** Scaling out at a fixed price target reduces both total return
  AND profit factor while INCREASING drawdown, in any system whose returns
  come from a right-tailed distribution of winners. The take removes
  exactly the position size that would have captured the large move, while
  the remainder still absorbs a full stop on losers.
- **Evidence:** XAUUSD 15m, entry 50 / trail 6 ATR / SMA gate, full period:

  | take at the 250-pt quarter | PF | net | max DD |
  |---|---|---|---|
  | none | 1.134 | +58.0% | 27.4% |
  | 25% | 1.102 | +40.9% | 33.8% |
  | 40% | 1.050 | +18.2% | 40.6% |
  | 50% | 1.028 | +10.0% | 43.3% |
  | 60% | 1.017 | +5.9% | 45.1% |

  Monotonic in both directions. Rescaling the grid did not rescue it:
  quarters of 100 / 50 / 25 points all landed at full-period PF 1.08-1.09
  against 1.172 with no target at all.
- **This is the third independent confirmation.** The fixed 1R/2R targets
  in all 17 earlier engines (PF 0.82-0.89), the level-to-level TP1/TP2
  experiment (H74, PF 1.093 -> 0.892), and now quarter-point scaling. The
  same mechanism each time: capping winners.
- **Invalidation:** a target that IMPROVES net return and profit factor
  simultaneously on both halves. Nothing tested has come close.

### H76 — Yotov's quarter grid is the wrong scale for 15m gold
- **Status:** CONFIRMED (arithmetic, not opinion)
- **Claim:** Yotov's 250-point large quarters describe multi-week FX swings.
  On 15m XAUUSD the median ATR(14) is 2.58 points, so a 6-ATR trailing stop
  sits about 15 points from price — **a 250-point quarter is 16x wider than
  the entire distance the system risks.** The quarter is almost never
  reached before the trail fires.
- **Proof:** using quarter points as a stop anchor produced results
  byte-identical to the ATR trail alone (full-period PF 1.172, +88.9%,
  DD 27.6% in both cases). The quarter constraint never once bound.
- **Consequence:** quarter theory is not wrong, it is out of scale here. It
  would need a daily or 4H chart to have anything to say. Applying it to a
  15m system is a category error, and rescaling the grid to fit the
  timeframe destroys the structure the theory rests on (major handles,
  1000-point ranges) while still failing on the numbers.

---

### H77 — Quarter-round price levels work as counter-trend profit targets, at the right scale
- **Status:** CONFIRMED (better on train, test, full period, and on both
  return and drawdown; graded smoothly across grid scales)
- **Source:** JEAFX Key Levels guide — plot only `.00/.25/.50/.75`, used as
  reversal areas.
- **Claim:** Banking the counter-trend leg at quarter-round levels improves a
  trailing-stop trend system, provided the grid spacing is roughly 1-4x the
  instrument's ATR on the traded timeframe.
- **Evidence:** XAUUSD 15m, entry 50 / trail 6 ATR / SMA750 / EMA2000 gate,
  banking 50% of SHORTS at the grid:

  | grid | full PF | net | max DD | return/DD |
  |---|---|---|---|---|
  | none | 1.186 | +87.0% | 23.2% | 3.75 |
  | **2.50** | **1.261** | **+110.6%** | **19.0%** | **5.81** |
  | 5.00 | 1.256 | +108.7% | 19.7% | 5.52 |
  | 25.00 | 1.211 | +93.7% | 22.4% | 4.18 |

- **Why 2.50 on gold:** JEAFX's quarters of a round number applied to gold's
  10-unit handles. Median ATR is 2.58, so the grid is ~1x ATR — the same
  order as the source's EURUSD example (25 pips vs ~10-pip ATR).
- **Relation to H75:** does NOT contradict it. Banking the WITH-trend side on
  this same grid still destroys the system (+87% -> +29-41%). The asymmetry
  is the mechanism.
- **Relation to H76:** the direct counterpoint. Yotov's 250-point quarters
  never bind on 15m gold; JEAFX's 2.50-point quarters work well. Same
  concept, 100x apart in scale. **Scale, not the level theory, is what
  determines usability on a timeframe.**
- **Invalidation:** if the improvement vanishes on another instrument whose
  grid is set by the same ATR-ratio rule, this is gold-specific fitting
  rather than a level effect.

---

## H78 — A key-level touch carries no directional information (XAUUSD 15m)

**Status: SUPPORTED, strongly.** Tested 2026-07-31 on 157,366 bars after
the user asked to enter, exit and reverse on key levels.

Fading a level and breaking a level were both tested as the entry, across
three separation gaps, on the 18 levels the SpacemanBTC module draws.
Every configuration loses. **With costs set to zero, every configuration
still lands on PF 1.00** (reverse 0.984/0.951/1.000; break 1.017/0.987/
1.003). That rules out cost drag as the explanation — the touch itself
predicts nothing.

- **Why this matters:** it is the same conclusion the random-entry null
  produced for the breakout engine, arrived at from the opposite
  direction. Entry rules on this instrument and timeframe do not carry
  edge. Exits do.
- **Consistent with:** H73 (the edge is the exit structure).
- **Invalidation:** a level-touch entry that beats a matched random entry
  through identical exits, on out-of-sample data, at any timeframe.

## H79 — Levels are useful as an exit, and only on the counter-trend side

**Status: SUPPORTED (small effect).** Same session, same data.

Closing 75% of the position at the nearest drawn level ahead of it, on the
SHORT side only, improved both halves: train PF 1.244 → 1.289, OOS 1.580 →
1.610, full period 1.333 → 1.379 with drawdown 13.6% → 12.3%.

Doing it on BOTH sides collapses the full period to PF 1.023 / +5.9%.
Reversing at the level on both sides — the literal request — is the worst
configuration measured: train PF 0.932, net −14.8%.

- **This is the third independent confirmation of the asymmetry rule**
  (Yotov grid, Daye Q4, now the drawn levels). Any profit-taking device
  removes exactly the size that would have captured the large move, so it
  can only be applied where there is no large move to capture — the
  counter-trend side.
- **Real levels ≈ synthetic grid:** 1.289 vs 1.297 train, 1.610 vs 1.598
  OOS. The drawn levels are the default for legibility, not performance.
- **Invalidation:** the effect not surviving on another instrument, or
  vanishing once the ~30 configurations swept here are accounted for. The
  gain is +0.03 to +0.045 PF; that is inside the range a 30-trial search
  can manufacture, so this belief is held loosely.

## H80 — Two trend horizons agreeing is a drawdown filter, not a return filter

**Status: SUPPORTED.** Tested 2026-07-31, 157,366 bars, train/OOS split.

Requiring BOTH a fast SMA (750, ~8 days) and a slow one (2000, ~3 weeks)
to be on the trade's side, on top of the EMA2000 regime gate:

- full period PF 1.379 → 1.421, net +155.9% → +157.7%, **drawdown 12.30%
  → 9.63%**, return/drawdown 12.68 → **16.36**
- train PF 1.289 → 1.335, drawdown 12.3% → 9.6%
- OOS PF 1.610 → 1.624

**Return barely moved. The drawdown fell by a fifth.** That is the correct
way to describe every filter in this project — they remove bad exposure,
they do not find good entries.

- **The agreement is the signal, not the slower average.** SMA2000 used
  INSTEAD of SMA750 is worse (train 1.181 vs 1.289). Requiring only one of
  the two is much worse (1.149). The two horizons disagreeing is what
  marks the choppy middle of a range, and that is what gets skipped.
- **Consistent with H73/H78:** the entry still contributes nothing. This
  filter works by not trading, not by predicting.
- **Rejected variant:** requiring 1 of 2 and doubling size when both agree
  lifts train net to +146.1% but takes drawdown to 21.8% and PF to 1.197.
  That is leverage dressed as confluence.
- **Invalidation:** the drawdown reduction failing to appear on another
  instrument, or the two lengths needing re-tuning per market — that would
  make it fitting rather than a horizon-disagreement effect.

## H81 — Pyramiding is the largest return lever here, and it is not an edge

**Status: SUPPORTED as a return lever, EXPLICITLY NOT as an edge.**
Tested 2026-07-31 on XAUUSD 30m, 6.7 years, five-slice walk-forward.

Adding 2 units every 3 ATR of favourable movement, sharing the trailing
stop, improved **all five consecutive walk-forward slices**. Full period
+192.6% → +660.2% with drawdown 9.83% → 17.68%; return per drawdown 19.58
→ 37.33.

**Why it is not an edge:** run through RANDOM entries on 20 seeds it lifts
the median from 6.8% to 25.3% but takes the outcome spread from 6.8 to
29.5 and the worst seed from −3.5% to −30.2%. It multiplies whatever the
entry produces. On the TRAIN half, plain leverage at 3% risk beats it at
matched drawdown; only on OOS does pyramiding win on both axes.

- **Consistent with H73/H78/H80:** everything that works in this project
  is position management. Nothing that works is prediction.
- **Correction to an earlier belief:** "wider trail is better" was measured
  on PROFIT FACTOR only. On RETURN it is false — trail 20 ATR gives PF
  1.659 but only +23.5% against trail 6's 1.243 and +85.4%, because
  risk-based sizing shrinks the position as the stop widens.
- **Invalidation:** a walk-forward slice where adds make things worse, or
  the effect disappearing once the parameters are chosen on a train half
  and tested once. The current parameters were picked having seen all five
  slices, so that test has not been run.

## H82 — The 22-voice knowledge layer is real but redundant with simple trend filters

**Status: SUPPORTED.** Tested 2026-07-31 for the first time against the
current engine, after the user pointed out the knowledge layer was going
unused.

- **As a veto it barely bites.** At a net-score threshold of 0 it changes
  nothing at all; at 4 it removes 13 trades from 799. The voices almost
  always already agree with a breakout that has cleared an EMA regime
  gate, a slope gate and two SMAs. Most of the register is trend-following
  in nature, so it is re-measuring what the filters already measure.
- **At net ≥ 6 it is a genuine risk improvement:** out-of-sample PF 1.879
  → 1.954, out-of-sample drawdown 12.88% → 10.44%, for ~9% of the return.
- **As a standalone ENTRY it beats every other supplied entry** — full PF
  1.468 against the DE Hybrid's 1.213 and the SMA-200 cross's 0.920, with
  the best out-of-sample return of any entry tested (+96.7%). It still
  loses to the Donchian breakout inside the full engine.
- **V18 (Nison tier-A candle) has the best per-trade quality measured in
  this project** (PF 1.498 as a hard gate) at the cost of two-thirds of the
  trades.

**Why this matters beyond the numbers:** the knowledge layer was assumed
to be additive and was never measured against a competent baseline. It is
additive against a WEAK baseline and redundant against a good one. That is
the correct way to describe every confluence idea in this repo.

**Invalidation:** a voice subset that improves BOTH return and drawdown on
both halves. The greedy subset search was never run against the current
engine — only the whole-register net score was.

---

## The knowledge layer's EXIT rules have never been tested — only its entries

**Established 2026-08-02**, by a transcript-to-code traceability sweep.

Every confluence claim measured in this repo so far has been an ENTRY
claim: does voice X's signal improve the entry. The finding above — that
the voices are additive against a weak baseline and redundant against a
good one — is therefore a statement about entries only, and it has been
quietly generalised to the whole knowledge layer. That generalisation is
unsupported.

The sweep checked eight named exit mechanics that ARE correctly extracted
into the playbooks against their presence in `backtest/*.py`:

| mechanic | in playbooks | in any engine |
|---|---|---|
| 21-EMA confirmed structure trail | yes | **no** |
| swing-count regime switch | yes (3 docs) | **no** |
| impulse-candle low trail | yes | **no** |
| average daily range partial | yes (2 docs) | **no** |
| previous-POC full exit | yes (9 docs) | **no** |
| previous-daily-high first target | yes | **no** |
| absorption-triggered exit | yes (4 docs) | **no** |
| three-loss daily halt | yes | **no** |

Eight for eight. The engines implement six trailing modes, none of which
came from the knowledge layer — all six are generic quantitative forms
(ATR, Donchian, EMA, step, giveback, none).

**Why this matters:** this repo's single most robust finding is that the
EXIT carries the edge, not the entry. The knowledge layer was mined
exclusively for the thing that does not carry the edge, and its exit
content — the part that would matter most — sits unbuilt in the playbooks.

**Invalidation:** implement the structure trail (below) and find it does
not beat the chandelier trail on the same window and costs. That is a real
possibility and it is the point of testing it.

**Highest-value untested candidate — Dave's 21-EMA structure trail**
(`dave_market_structure.md:108-111`, source `raw_transcripts/line1200`):
the stop trails ONLY to swing lows that (a) closed below the 21 EMA and
(b) were then followed by price taking out the previous high. Lows that
did not close through the EMA are ignored, so ordinary noise does not
tighten the stop. Breakeven is defined mechanically: move to breakeven
when price takes out the high that put in the low. After the third or
fourth swing the mode switches to aggressive — trail behind bullish candle
lows, anticipating reversal.

This is structurally different from all six implemented modes: it tightens
on SWING COUNT, not on ATR progress (the `step` mode) or on a fraction of
excursion (`giveback`). The source demonstrates it holding 4.7R, 4.8R and
8R runs on 15m charts. It is a two-regime trail — loose while the trend is
young, aggressive once it is old — which is exactly the shape the `step`
mode approximates with a cruder proxy.

**Second candidate — Valentini's volatility-anchored partial**
(`raw_transcripts/line0896`, and NOT currently in `valentini_scalping.md`
— an extraction miss): take the first partial at the instrument's AVERAGE
session range rather than at a fixed R multiple. Stated verbatim: "if I
know on average EU is moving 15 pips every London session, why wait for 20
or 25? I take it at 15." Full position closes at the average daily range.
The rationale is measured, not stylistic — he reports the probability of
reaching the third standard deviation in a session is 7%, so targets
beyond it are priced wrong.

This directly addresses BUG-017's failure mode. A level-based target fails
because its distance is set by where a line happens to sit. An ADR-anchored
target sets distance from the instrument's own realised volatility, so the
target/stop ratio is stable across trades instead of random. It is the
same family as the ATR target already in the engine but anchored to
SESSION range rather than bar range — which is the horizon the trade is
actually held over.

---

## The edge is an exponent gap, and it belongs to hold time, not to the entry

**Established 2026-08-02**, `backtest/mae_mfe.py`, XAUUSD 15m/30m/60m,
2019-2026, Donchian-100 breakout entries, no stop, excursions in ATR at entry.

Adopting `MASTER_BLUEPRINT.md`'s MAE/MFE derivation and testing it produced a
negative result on the method and a positive one on the market.

**The method fails.** The "optimal stop derived from the 80th percentile of
MAE" is not a market property. It tracks whatever measurement parameter was
chosen — measurement stop 12/25/50 ATR yields 12.85/25.40/34.33; hold cap
50/100/400/800 bars yields 6.5/9.1/17.1/26.3 ATR. MAE is right-censored by
any stop, and uncensored it simply diffuses.

**The market result.** Fitting log(excursion) against log(hold):

| series | exponent | reference |
|---|---|---|
| MAE | **0.493** | pure random walk = 0.500 |
| MFE | **0.558** | |
| gap | **+0.065** | |

The adverse side of a breakout entry on gold is statistically
indistinguishable from a random walk. The favourable side compounds faster.
P80 MFE / P80 MAE by hold: 1.09, 1.10, 1.08, 1.18, 1.32 at 50/100/200/400/800
bars — no asymmetry at short holds, growing with time.

**Why this matters more than any entry test we have run.** It is the
quantitative form of this project's oldest finding. The entry contributes an
exponent of 0.493 — a coin flip on geometry. Hold time contributes 0.065.
Everything this repo has measured follows from it:

- fixed targets cap the trade in the low-ratio regime and discard the
  asymmetry, which is why every fixed-target configuration here lost, and why
  every fixed-TP configuration in the uploaded AU200 archive was negative
  across the entire sweep (PF 0.85-0.89, all combinations).
- trailing exits harvest the gap, which is why the exit dominates the entry
  across all seven entry families tested.
- early profit-taking is destructive, independently reproduced by the AU200
  archive: TP1 at an EMA8 pierce gave 14.6% WR and -$427,792 while holding
  the same signals to end of day gave 83.3% and +$1,170,926.

**Invalidation:** an entry whose MAE exponent is materially below 0.49 — that
would be an entry with genuine geometric edge, and it would change where
effort should go. None of the seven families tested here has shown one.

**Caveat:** measured on one entry family (Donchian-100) and one instrument.
The exponent gap should be re-measured per entry before being assumed. The
module prints it on every run for exactly that reason.

---

## Pivot-range WIDTH forecasts next-session directionality — on the London/NY overlap only

**Established 2026-08-02.** `backtest/pivots.py`, XAUUSD 15m aggregated to
sessions, 2019-12 to 2026-07, 1,659 sessions. Source: Frank Ochoa (PivotBoss),
"Profiting with Pivot-Based Concepts", archived in `sources/`.

**The source deserves no credit for evidence.** It is a 48-slide sales deck
ending on a $69.96 book offer and three testimonials. Zero statistics, zero
sample sizes, and every claim illustrated with a hand-annotated chart marked
"Buy Here". Same category as voice #11 (FX Master Pattern), which this
register already rejected for hindsight annotation. It was tested anyway
because its central mechanism is mechanical and because it fills the one gap
this repo had — floor pivots existed nowhere before this.

**Three of its four testable claims FAIL on XAUUSD:**

| claim | result |
|---|---|
| narrow width -> trending, on a 24h day | +0.026 efficiency, t=+1.41 — noise |
| "Inside Value is the MOST explosive relationship" | ranks **4th of 6**; inside minus rest = −0.016, t=−0.25 |
| the 7 two-day relationships discriminate | next-range 1.016–1.059, next-efficiency 0.446–0.485 — all inside noise |
| pivot width beats simply using yesterday's range | corr with next range +0.045 vs +0.037, and the two are 0.754 correlated — the construction adds ~nothing |

**One claim survives, and only on one session.** Session definition decides it:

| session | corr(width, next efficiency) | narrow − wide | t |
|---|---|---|---|
| 24h UTC day | −0.042 | +0.026 | +1.41 |
| NY RTH 13:30–20:00 | −0.018 | +0.005 | +0.29 |
| London 08:00–16:30 | −0.042 | +0.041 | +2.28 |
| **LDN/NY overlap 13:30–16:30** | **−0.075** | **+0.055** | **+3.07** |

**It survives the checks that matter:**
- **Parameter stability** (blueprint Stage 6.5): 30 combinations, 6 lookbacks
  × 5 quantile pairs. Every t-stat positive, range +2.20 to +3.80. A broad
  hill, not a spike.
- **Out of sample**: first half +0.0504 (t=+2.00), second half +0.0526
  (t=+2.06). Near-identical halves.

**Disclosure of search.** Four session definitions were tested and the best
reported. Bonferroni at 4 trials still clears p<0.01. The quantile pair and
lookback were NOT searched for significance — the stability grid above shows
the result is insensitive to both.

**What this is and is not.** It is a REGIME FORECASTER: a narrow prior pivot
range precedes a more directional session. Effect is ~+0.05 of efficiency on
a base of ~0.45, about 11% relative. It is **not** an entry, **not** a target,
and **has not been shown to make money** — directional efficiency is not
profit.

**Why it matters anyway.** It is the first level-derived quantity in this repo
that survives a real test, and it lands in exactly the category the levels
inventory identified as the only viable one. Combined with the exponent-gap
finding (MAE diffuses at 0.493; the edge is +0.065 and accrues to HOLD TIME),
a narrow prior pivot range is a candidate **hold-extension trigger**: on those
sessions, widen the trail or suppress the partial, because the session is more
likely to run.

**Invalidation:** apply it as a hold-extender to `gold_trend_strategy.pine`
and find no improvement in return or drawdown against the unmodified champion
on the same window and costs. That is the next measurement, and it is the one
that decides whether this is tradeable or merely true.

---

## Inside bars: statistically real at every timeframe, economic only from 4H up

**Established 2026-08-02.** Source: an uploaded Nial-Fuller-style price-action
deck (`sources/price_action_trading_pinbar_insidebar_fakey.pdf`), tested on
XAUUSD 2019-12 to 2026-07. Inside bar = high <= prior high AND low >= prior
low; trade the first break of the mother bar within 3 bars; measure the
ATR-normalised move 5 bars later.

The inside bar was the one setup in that deck with **zero coverage anywhere in
this repo** — not in a playbook, not in an indicator. Pin bar is already
covered as hammer/shooting star (2 playbooks), and "fakey" is sweep+reclaim
under another name (sweep appears in 23 playbooks and 12 indicators).

| timeframe | inside rate | breakout win% | edge (ATR) | t | edge $ | net of cost |
|---|---|---|---|---|---|---|
| 15m | 14.9% | 49.4% | 0.033 | 2.65 | 0.09 | **−0.45** |
| 30m | 15.3% | 50.1% | 0.058 | 3.28 | 0.21 | **−0.33** |
| 1H | 16.4% | 50.4% | 0.070 | 2.86 | 0.37 | **−0.17** |
| 4H | 20.7% | 52.6% | 0.156 | 3.69 | 1.61 | **+1.07** |
| 1D | 21.5% | 55.3% | 0.375 | 4.02 | 9.41 | **+8.87** |

Cost model is this repo's standard: 0.20 pt slippage plus $0.07 commission
per side, $0.54 per round turn.

**The edge is real and it is monotonic in timeframe** — 0.033 ATR at 15m
rising eleven-fold to 0.375 at daily, with t between 2.65 and 4.02 throughout.
It is also, intraday, far too small to trade: at 15m the edge is 9 cents
against 54 cents of cost.

**The deck's conclusion is right and its stated reason is wrong.** It says
inside bars "grow too numerous below the daily chart", implying frequency is
the problem. Frequency as a RATE actually rises with timeframe (14.9% at 15m
to 21.5% daily); only the absolute count falls (23,442 to 445). The real
reason low timeframes fail is that the per-signal edge shrinks faster than
costs do. Right answer, wrong mechanism — worth separating, because the wrong
mechanism would lead someone to "fix" it by filtering for rarer inside bars,
which would not help.

**Relevance to this desk is limited and should be stated plainly.**
`USER_TRADING_PROFILE.md` has the user on 5m/15m/30m. On those timeframes this
setup loses to costs. It becomes tradeable only at 4H and daily, which is a
different trading style, not a tweak.

**Where it could still matter:** as a CONFLUENCE input rather than a signal —
an inside bar on the 4H or daily as a state flag while trading 30m. That is
untested and is the only version worth testing here.

**Invalidation:** show a 15m/30m inside-bar variant whose per-signal edge
exceeds 0.21 ATR, which is what it would take to clear costs with margin.
Nothing in the deck suggests one exists.

**UPDATE 2026-08-02 — the pivot-width regime does NOT convert into P&L via
trail-widening.** Tested as H-PIVOT-HOLD (see RESULTS_LEDGER). Widening the
chandelier trail by 1.25x / 1.5x / 2.0x on narrow-pivot sessions gained
+46.8pp net on the full sample, +18.0pp on the first half, and **lost 18.4pp
out of sample**, with a non-monotonic response to the multiplier. Rejected.

The forecasting claim stands; the trading claim does not. That distinction is
the point — this register now separates "true" from "tradeable", and this
belief is the former only.

**UPDATE 2026-08-02 — the first of the eight unbuilt exit mechanics has now
been built and tested.** Dave's 21-EMA structure trail is implemented as
`exit_lab.trail_mode="structure"`. Result (H-STRUCT-TRAIL in RESULTS_LEDGER):
rejected as a return improvement — +107.2pp on the full sample, +58.1pp on the
first half, **−65.5pp out of sample** — but drawdown falls in 9 of 9
slice x variant combinations (−2.68 to −20.51pp), which is robust and coherent
with the mechanism (it cycles ~2x faster and trades return for smoothness).

**This updates the parent belief.** "The knowledge layer's exit rules have
never been tested" is now false for one of the eight. The first one tested
produced a genuine risk effect and no return effect. That is weak evidence
that the remaining seven are worth building — and stronger evidence that they
should be judged on drawdown and ret/DD, not on return alone.

---

## Key levels DO carry information — and it lives where you cannot monetise it

**Established 2026-08-02.** `backtest/level_reaction.py`. XAUUSD 30m,
2019-12 to 2026-07, 33 level types from `levels.py` (dense), 73,000-80,000
touches per configuration. First-passage test: from a level touch, does price
travel R ATR back the way it came (bounce) or R ATR through (break) first?
Every real touch matched against a control price drawn uniformly from the
SAME bar's range — same volatility, same trend, genuinely touched, differing
only in whether it is a real level.

| R (ATR) | n | real bounce | control | z | breakeven needed | clears cost? |
|---|---|---|---|---|---|---|
| 0.5 | 73,579 | **54.28%** | 49.06% | **+20.08** | 64.59% | no |
| 1.0 | 80,067 | **52.79%** | 49.18% | **+14.47** | 57.29% | no |
| 1.5 | 80,675 | **52.01%** | 49.55% | **+9.87** | 54.86% | no |
| 2.0 | 79,902 | **51.33%** | 49.56% | **+7.06** | 53.65% | no |
| 3.0 | 73,114 | **50.91%** | 49.52% | **+5.31** | 52.43% | no |

Breakeven assumes a symmetric R-for-R trade at this repo's standard cost
($0.54 round turn = 0.146 ATR at the median 30m ATR of $3.70).

**The levels are real.** Every configuration beats its matched control, with
z from +5.31 to +20.08 on 73k-80k samples. This is the first positive,
properly-controlled measurement of key levels in this project, and it
contradicts the loose reading of BUG-017 that "levels don't work". They do.
Price genuinely holds at them more often than at an arbitrary price in the
same bar.

**And it is uniformly uneconomic as a bounce trade.** The gap to breakeven is
10.31pp at R=0.5, narrowing to 1.52pp at R=3.0, and never closes.

**The reason is the important part.** Two decay curves run in opposite
directions:

- The LEVEL edge is strongest close in (54.28% at 0.5 ATR) and decays with
  distance (50.91% at 3.0). Support and resistance grip locally and lose hold
  as price travels — exactly what a real S/R effect should look like.
- The COST bar behaves the other way: it is punishing at small R (64.59%
  needed) and mild at large R (52.43%).

So the information sits precisely where the spread eats it, and the money
sits precisely where the levels stop working. That is a structural mismatch,
not a tuning problem, and no choice of R resolves it.

**This explains BUG-017 mechanically.** The key-level target build did not
fail because levels are meaningless. It failed because a level's information
lives at a distance too short to pay for the round turn — a median target of
0.46 ATR against a 6 ATR stop was trading exactly the region where the edge
is real and the costs are fatal.

**It also sits in direct opposition to the exponent-gap finding.** That says
profit accrues to HOLD TIME and long distances (MFE exponent 0.558 vs MAE
0.493). Levels say information accrues to SHORT distances. A strategy cannot
serve both, which is why every level-target build in this repo and in the
uploaded archive lost.

**What this licenses, and what it does not.**
- NOT a signal generator. A level touch is not a trade at any R tested.
- IS a map. It is genuine information about where price is more likely to
  pause, which is legitimately useful for stop PLACEMENT (do not park a stop
  just beyond a level), for position sizing into confluence, and for deciding
  not to enter into a wall of stacked levels.
- The one untested use consistent with both findings: levels as a
  CONFLUENCE-COUNT regime variable rather than a price. How many levels sit
  within X ATR of price is a different quantity from where any single one is,
  and it has never been measured here.

**Invalidation:** a level subset (single type, or a confluence threshold)
whose bounce rate exceeds breakeven at any R. The per-type breakdown has not
been run and is the obvious next test — the aggregate could be hiding a
strong minority.

**UPDATE 2026-08-02 — the four standard key-level claims all fail on XAUUSD.**
Tested in `backtest/level_claims.py` over 81,396 touches (see RESULTS_LEDGER):
untested-beats-retested is false; confluence-is-stronger is false and slightly
backwards; 1:2 and 1:3 targets do not rescue a level fade; and sweep-and-
reclaim, while a REAL phenomenon (33.13% vs 27.99% hit rate), loses its whole
advantage to the wider entry-to-stop distance a sweep bar creates.

This kills the "confluence count as a regime variable" idea proposed in the
levels inventory two entries above. It was speculation and it is now measured
and negative.

The parent finding stands and is now sharper: levels carry real information
(z up to +20 vs matched control) that is not convertible into a trade at any
distance, hit-rate cohort or payoff ratio tested. They are a map. The edge has
to come from the exit engine.

**UPDATE 2026-08-02 (final on key levels) — with-trend entries tested, and the
edge is the bias filter, not the level.** The methodology's own recommended
form (bias from weekly+monthly open, buy support in an uptrend, stop beyond
the level, 2R target) beats fading at every timeframe and CLEARS costs at 4H
(+0.085 ATR) and daily (+0.261), holding out of sample.

But a matched control — same bias, same risk, entry at a RANDOM bar — scores
HIGHER in all four comparisons (4H +0.135 vs +0.085; daily longs +0.535 vs
+0.490). The levels subtract. On daily, longs are +0.490 and shorts −0.108,
in a market that rose 182% across the sample.

**Closing position on key levels.** They carry genuine information (z up to
+20 against a matched control) and there is no tested configuration in which
that information becomes money. Fade, with-trend, sweep-and-reclaim,
confluence, first-touch, 1:2, 1:3, 30m/4H/daily — all either lose or lose to
their own control. Use the indicator as a map: stop placement, context,
knowing where the crowd is. The edge must come from the exit engine, which is
where this repo has measured it all along.

---

## The CPR/value regime works as an ENTRY GATE, not as a level to trade

**Established 2026-08-02**, `backtest/rulebook_v2.py` plus its control.
XAUUSD 30m, 2019-2026, 8,483 gated trades against a 24,779-trade control.

A momentum entry (strong-bodied candle closing beyond the central pivot
range) filtered by "Inside Value OR narrow CPR" returns +0.040R per trade at
PF 1.07. The same entry with the CPR gate REMOVED returns −0.059R at PF 0.92.
**The gate is worth +0.099R per trade and it beats its control in both halves
of the sample** (0.98 vs 0.89 first half, 1.17 vs 0.95 out of sample).

**This is the first thing in this investigation that survived a control.**
Everything else died on one: level bounces, sweep-and-reclaim, confluence,
untested levels, with-trend level entries, and the pivot-width hold extension.

**It joins up two earlier findings rather than contradicting them.** Pivot
range width is genuine information about the coming session (t=+3.07 on the
LDN/NY overlap, parameter-stable, replicates out of sample). It could not be
converted into P&L by widening a trail. It CAN be converted by using it to
decide when a momentum entry is worth taking. The information was always
about REGIME, and a regime signal belongs on the entry gate, not on the price
you trade or the leash you use.

**What it is not.** PF 1.07 at +0.04R per trade, 3.4 trades/day, with a 304R
maximum drawdown, is a component and not a system. The two halves agree in
direction against the control but disagree sharply in level (−52.9R then
+389.4R), and that instability is not yet explained.

**Invalidation:** run it on a second instrument, or on a properly out-of-
sample period, and find the gate no longer beats its ungated control. That is
the next test and it has not been run.

**UPDATE 2026-08-02 (final) — the CPR gate is REJECTED on the second-instrument
test.** US30 data added; the gate's ungated control beats it on both US30
timeframes (30m: PF 1.10 control vs 1.04 gated; 60m: 1.04 vs 0.93), and the
gated arm flips sign between halves on both. The gold result — +0.099R over
control, monotonic across five "narrow" definitions, positive on four
timeframes — did not generalise.

**The methodological lesson is the durable output.** Timeframe robustness on a
single instrument is NOT evidence of generality: resampled bars are not
independent observations. This belief was raised on within-instrument evidence
that looked strong by every internal check available, and one genuinely
independent test overturned it. Any future component should face a second
instrument BEFORE it is written up as surviving.

Closing count for the key-level / pivot / rule-book investigation: eleven
distinct claims or components tested, zero surviving a properly independent
control.

---

## B-0xx — The opening range does not carry special information on these two instruments

**Claim tested (2026-08-03):** the first N minutes of a session define a range
whose break is directionally informative.

**Evidence against.**
1. On US30 the matched control — an identically sized range built 2 to 16 bars
   later in the same session, traded by identical rules — pays +0.030R against
   the opening range's +0.107R in the best cell, a gap of z = +1.47 after
   ~50 cells were searched. In the full (uncut) versions the later ranges pay
   MORE than the opening one at 60m (+0.036 at offset 12 vs +0.019 at offset 0).
2. On gold all twelve base configurations lose, and so does the fade of each.
   Both directions losing is the signature of no information, only cost.

**What this does NOT claim.** ORB is not shown to be worthless generally. It is
shown not to clear costs on XAUUSD spot at 377–464 trades/year, and not to beat
a same-session control on US30 cash at this sample size. Instruments with a
hard cash open and a genuine overnight gap — single-name equities — are a
different population and were not tested.

**Invalidation:** an ORB variant that beats the offset control by z > 3 on one
instrument AND is non-negative on the other.

**Standing consequence for method (this is the durable part).** Twelve
components across level, pivot, rule-book and ORB families have now been tested
this session against independent controls. Zero survived. Four of those were
positive results of mine that the control reversed. The register's operating
assumption is now: **on XAUUSD 15m–60m, no entry-timing rule tested in this
repo has beaten a cost-matched control.** The one measured effect that has
survived every version of scrutiny is the exponent gap — profit accrues to hold
time, not to entry precision — and it was re-observed again here in Priority 5,
where expectancy rose monotonically from 1R to 3R targets on both range sizes.
Future work should be aimed at exits and position holding, not at another
entry filter.

---

## B-0xx — RETRACTED: "wider trailing stops are monotonically better"

**Was believed because** `gold_trend_strategy.pine` stated it in its own
"WHAT ACTUALLY MAKES THE MONEY" header: 2 ATR → PF 1.05, 6 ATR → 1.60,
14 ATR → 1.75. It was the single most-cited number in this repo's exit work and
it motivated a whole priority of research.

**Measured 2026-08-03, three ways, and it does not reproduce.** PF is
hump-shaped with a maximum at 4.24–5.0 ATR:

| trail | coupled | trail-only | adds off |
|---|---|---|---|
| 3.0 | 1.164 | 1.173 | 1.152 |
| **4.24** | **1.646** | **1.646** | 1.389 |
| 5.0 | 1.554 | 1.576 | **1.429** |
| 6.0 | 1.429 | 1.417 | 1.344 |
| 14.0 | 1.525 | 1.553 | 1.397 |
| 20.0 | 1.619 | 1.359 | 1.322 |

**What survives.** The *direction* of the original insight is intact — 3.0 ATR
is far worse than 4.24 (PF 1.16 vs 1.65), so trails inside the noise band still
destroy the system, and Eckhardt's argument still holds. What dies is the
extrapolation: there is an optimum, the shipped value is on it, and past it
wider trails raise average R while cutting the sample 3–8× and taking drawdown
to 65–76%.

**Also retracted:** the claim (mine, in `WIZARDS_SYNTHESIS.md`) that the trail
sweep was *confounded* by risk-based sizing. The leverage cap binds on **0.0%**
of bars at every width from 3 to 20 ATR. Sizing is purely risk-based; a smaller
position at a wider stop is what constant-fractional risk means, not an
artifact.

**Standing consequence.** A number quoted inside a shipped artefact's own
header is not evidence. This one had been repeated across MEMORY.md, the
synthesis doc and two sessions of planning without anyone re-running it.
Re-measure before building on a documented figure.

---

## B-0xx — Cutting the short side on gold is a bull-market artifact, not an edge

**Tempting because** with the trail-tightening adopted, `short_risk` 0.75 → 0.50
gave the best risk-adjusted numbers in the project: PF 1.866, MAR 2.56 at
31.87% drawdown, halves 1.39/1.97, and clearly positive excess over the
leverage curve (+0.088).

**Rejected on three measurements (2026-08-03):**
1. Standalone by direction on gold, shorts are the BETTER book —
   **PF 1.891 against longs' 1.806** — and supply 35% of net profit.
2. Cutting shorts degrades profit factor in **precisely gold's two down years**
   (2021 0.98→0.92, 2026 2.00→1.93) and improves only rising ones.
3. On US30 it is monotonically harmful: MAR 1.14 / 1.06 / 0.98 / 0.88 as short
   risk falls 1.0 / 0.75 / 0.5 / 0.25.

**The general rule this is an instance of.** Gold rose 1450 → 4100 across this
sample. Any parameter that reduces short exposure will therefore test well, and
will test well *for a reason that has nothing to do with edge*. Before adopting
any change that shifts directional balance, check it against the down years in
isolation and against a second instrument. A whole-sample metric cannot see
this failure mode.

**Standing consequence.** MAR is not scale-invariant either: dialling risk
0.70% → 1.60% moves the baseline's MAR 2.32 → 2.86 with no change in edge. Any
future candidate must be scored as EXCESS over the baseline's own MAR-vs-
drawdown curve at the candidate's drawdown. Six configurations in this session
"beat the baseline" on MAR and every one was leverage.

---

## B-0xx — Quarterly Theory was rejected on the wrong definitions; the corrected definitions reject it too

**How the error happened.** `research/levels_qt.py` encoded Quarterly Theory
from memory. The two source documents were sitting in
`trader_playbooks/sources/` unread while the study ran, and the negative
finding was reported as settled. Read afterwards, they contradict the code in
four places:

| # | Source says | levels_qt.py did |
|---|---|---|
| 1 | Weekly Q1=**Tuesday** … Q4=Friday; "Tuesday midnight open is the True Weekly Open" | Mon/Tue/Wed/Thu — off by one whole day |
| 2 | Daily Q1 18:00–00:00 … Q4 12:00–18:00 **New York time** | Same numbers applied to a UTC index — a 4–5h shift |
| 3 | **Two** AMD forms (Form 2 shifts every phase one quarter later) | Form 1 only |
| 4 | Session quarters are Range Formation / **Expansion** / Continuation / Reversal | Treated as accumulation/manipulation |

**Re-run on the source definitions (`research/qt_corrected.py`), both timezone
readings the source itself gives — it is internally inconsistent, daily in NY
time and its 90-minute table in UTC.**

**Result 1 — the weekly cycle is empty.** Against 20 return-shuffled surrogates
(`research/qt_null.py`) every weekly statistic sits inside ±3σ. The largest
z is −2.62. There is no weekly quarter structure of any kind.

**Result 2 — the big z-scores are geometry, not theory.** "Sweep the high in Q3
and the cycle reverses only 25% of the time" reads as z = −16. The surrogate
reproduces it: if a cycle sets its extreme in a *late* quarter there is no time
left to move away from it. Reversal rate falling with sweep-quarter lateness is
what a driftless random walk does.

**Result 3 — what *is* real is session volatility, which QT mislabels.** In the
NY-anchored daily cycle, Q3 (06:00–12:00 NY) sets the daily high 36.5% of the
time against a surrogate 18.8% (z = +17.4). That is real and large. But Form 1
names Q2 the manipulation quarter, and Q2 sets the high only 15.0%. The theory
points at the wrong quarter; the effect is "the NY morning is where the day's
extreme forms", which needs no cycle framework.

**Result 4 — the one profitable arm is a day-of-week effect that fails its
control.** Weekly Q4 gated the champion to PF 1.825 vs 1.626, holding in both
halves. Weekly Q4 *is Friday*: the corrected cycle is a relabelling of
Tue/Wed/Thu/Fri and cannot differ from a bare weekday sweep. Dialled to a
matched 25% drawdown (`research/qt_friday.py`):

| arm | risk% | n | PF | net | net/DD |
|---|---|---|---|---|---|
| champion, all days | 0.72 | 789 | 1.589 | +678.5% | **27.26** |
| Friday only | 1.11 | 224 | 1.832 | +411.0% | 16.44 |
| drop Friday | 0.43 | 709 | 1.432 | +134.8% | 5.39 |

Friday has the better *per-trade* quality and still compounds less, because it
trades 28% as often. Higher PF at fewer trades is not an improvement.
Separately worth knowing: **removing Friday guts the system** (net/DD 27 → 5),
so Friday carries a disproportionate share of the edge even though it cannot be
traded alone.

**Verdict: REJECT Quarterly Theory, now on its own definitions.** The earlier
rejection was right for the wrong reasons, which is not the same as being right.

**Standing consequence — the one that actually costs money.** A negative
finding reached without reading the source is not a finding. Before any study
of a named methodology, read the uploaded source first and code from it, not
from recall. The sources are in `trader_playbooks/sources/` under normalised
filenames; the original numeric-prefixed upload names do not exist on disk.

---

## B-0xx — Every falsifiable pattern claim in the uploaded sources fails its unconditional baseline

`research/source_battery.py` codes each exactly-specified claim in
`trader_playbooks/sources/` and compares its forward move, in ATR, against the
**unconditional** forward move over the same horizon. The unconditional
baseline matters: gold rose 1450 → 4100 across the sample, so every long-side
pattern beats zero and none of that is edge.

**40 tests (10 arms × 4 horizons). Survivors at |t| > 3: zero.**

| claim | source | result |
|---|---|---|
| Pin bar, tail ≥ ⅔ of range, body ≤ ⅓ | pinbar/insidebar/fakey p.430 | bull t ≈ 0; **bear is inverted** — bearish pins are followed by *up* moves (t = −2.87 at 32 bars, n = 4078) |
| Inside bar, continuation and reversal | same, p.342 | \|t\| ≤ 1.1 at every horizon |
| Fakey — false break of the inside bar | same, p.365 | best t = +1.92; nothing at 4 bars |
| "Big Players Entry" indicator, ported line-for-line incl. ADX > 40 | big_players_reversal_entry.txt | **negative as specified**: −0.48 ATR at 32 bars (t = −2.06). It buys 33-bar lows while DI− dominates — buying into confirmed downtrends |

**The dollar-quarter grid is dead flat, and this one is decisive.**
`gold_scalping_strategy_blueprint.txt` claims ".00 strongest S/R … .25/.75 weak,
often breached". Rejection rate at each sub-level, n ≈ 78,000 touches each:

| level | .00 | .25 | .50 | .75 |
|---|---|---|---|---|
| reject rate | 0.7009 | 0.7022 | 0.7023 | 0.7002 |

A 0.2-point spread on 78k samples. The four sub-levels are indistinguishable.
Note this is a *different* claim from the $25/$50/$100 grid already rejected —
this is the one-dollar grid — and it fails the same way.

**"Gold LOVES the daily open — major reversals within 30 min of NY open" is
half right and the wrong half is the tradeable one.** 09:30–10:30 NY:

| | mean \|move\| | sign-flip rate |
|---|---|---|
| NY open window | **4.998** | 0.4974 |
| all other bars | 2.528 | 0.5163 |

Volatility genuinely doubles. But the flip rate is *lower* than elsewhere — the
NY open is an **expansion** window, not a reversal window. Fading it is trading
against the one thing the data says clearly. This corroborates the champion,
which is a breakout system.

**Standing consequence.** Sixteen independent families of entry/level ideas
have now failed controls in this repo. The prior on the seventeenth should be
set accordingly: the champion's edge is in its *exit* (a 4.24-ATR chandelier on
a 6.36:1 payoff), and no amount of entry pattern-matching from the source
library has moved it.

---

## B-0xx — The long-form books: two claims are significant, both with the sign against the author

`research/source_battery2.py` covers the rules stated in prose across the
long-form sources — Person's candlesticks, Ochoa's pivots, Hougaard's manual,
Trader Dale's volume profile — anything exact enough to falsify. Directional
arms go through the same Welch-t-against-the-unconditional harness as battery 1.
Regime claims do **not**: they do not predict direction, they claim to say when a
breakout system should be trading, so they are run as champion gates at matched
25% drawdown.

**Directional survivors at |t| > 3: 6 of 40. Every one is a refutation.**

**1. Ochoa's headline rule is a significant loser.** "Buy support in a bull
trend" — price trading into S1 while above the 89MA — returns **−0.196 ATR** at
32 bars against an unconditional **+0.323** (edge −0.519, **t = −4.92**,
n = 1911). Buying dips at pivot support in gold's uptrend underperforms buying
nothing. The rule is not merely absent; it is inverted and significant.

**2. Hougaard's 89MA separates drift, but not in a way that can be shorted.**

| state | forward move at 32 bars | n |
|---|---|---|
| above 89MA | **+0.448 ATR** | 42,814 |
| unconditional | +0.323 ATR | — |
| below 89MA | **+0.162 ATR** | 35,761 |

t = +4.46 and +5.54 — real and large. But note what it says: below the 89MA gold
*still drifts up*, only slower. The four "significant" below-89 rows are
significant in the short direction only because slower-up beats faster-up when
you flip the sign. **A short taken on that signal still loses to the drift.**
This is the B-0xx bull-market artifact in a new costume, and the gate confirms
it: net/DD 16.10 against the ungated 27.26.

**3. Ochoa's pivot-width claim points the right way and is noise.** "Unusually
narrow pivot range forecasts trending and breakout markets; unusually wide
forecasts sideways trading." Day trend-efficiency, |close−open| / (high−low),
by pivot-width quintile over 2,071 days:

| narrowest | narrow | mid | wide | widest |
|---|---|---|---|---|
| 0.4596 | 0.4539 | 0.4542 | 0.4514 | 0.4383 |

Monotone in the predicted direction. **Spearman ρ = −0.027, p = 0.22; narrowest
vs widest Welch t = +1.17, p = 0.24.** This is the most interesting claim in the
library for this desk — the champion *is* a breakout system, so a free
breakout-day gate would be worth real money — and it is 2 points of efficiency
that cannot be separated from chance.

**Everything else is flat.** Person's HCD/LCD (doji plus a confirming close) and
his Jack Hammer (lower shadow ≥ 2× body, then a close above the hammer's high)
both come in at |t| ≤ 2.1 — and note these are *stricter* than battery 1's pin
bar, since Person requires a confirmation bar, so the confirmation adds nothing.
Trader Dale's volume-profile POC, built as a rolling 10-day 60-bin profile ending
at the previous bar, reaches |t| = 2.60 once out of eight tests.

**Not one regime gate beats the ungated champion at matched drawdown:**

| gate | risk% | n | PF | net | net/DD |
|---|---|---|---|---|---|
| **ungated** | 0.72 | 789 | 1.589 | +678.5% | **27.26** |
| Dale: > 1 ATR from POC | 0.68 | 766 | 1.599 | +592.1% | 23.67 |
| Hougaard: > 1 ATR from 89MA | 0.61 | 748 | 1.559 | +402.7% | 16.10 |
| Ochoa: inside value only | 2.56 | 74 | 1.939 | +266.6% | 10.62 |
| Ochoa: narrow pivot only | 0.69 | 416 | 1.794 | +261.9% | 10.51 |
| Ochoa: wide pivot only | 0.53 | 388 | 1.283 | +57.6% | 2.31 |
| Ochoa: higher/lower value | 0.33 | 599 | 1.212 | +34.4% | 1.37 |

Three gates post a **higher profit factor** than the ungated champion and every
one of them compounds less. That is the same trap as the Friday result, and it
is now the third time this pattern has appeared: **PF rises whenever a filter
removes trades, because the survivors are the easy ones. Read net/DD.**

**Recorded as untestable rather than silently dropped:** Dale's Order Flow
confirmation step needs a bid/ask ladder this desk does not have;
`agent_2_1_cluster_detector` is SEC Form 4 insider clustering on US equities
with no application to XAUUSD; the Gann material states no falsifiable
mechanical rule; Hougaard's discretionary crowd-reading is by construction not
mechanical. Those four are gaps in coverage, not passes.

---

## B-0xx — The Bollinger squeeze gate: the first candidate in eighteen families to beat the baseline, and the control that would settle it cannot be run

**The claim (user's scalping checklist, item 6, quoting Bollinger).** "Periods
of low volatility are often followed by periods of high volatility ... a
narrowing of the bands can foreshadow a significant advance or decline."

**Part 1 — the market claim is TRUE and large.** Bandwidth = 2·2σ₂₀/MA₂₀,
quintiled over 78,673 bars. Forward 20-bar price range, in ATR:

| band | squeeze | tight | mid | loose | wide |
|---|---|---|---|---|---|
| forward 20-bar range (ATR) | **6.69** | 5.72 | 5.03 | 4.61 | 4.13 |

Monotone, and the squeeze band delivers **62% more forward range** than the
wide band. Note this is not the trivial mean-reversion of bandwidth itself
(bandwidth is bounded below so it must rise from a low) — it is the *price
range that follows*, which is the thing Bollinger actually claimed.

**Part 2 — gating the champion on it, at matched 25% drawdown.**

| arm | risk% | n | WR | PF | net | **net/DD** |
|---|---|---|---|---|---|---|
| baseline champion | 0.72 | 789 | 21.7% | 1.589 | +678.5% | **27.26** |
| **squeeze gate (bw < 40th pct)** | 0.96 | 458 | 24.2% | 1.863 | +1163.9% | **46.53** |
| no-squeeze (complement, control) | 0.60 | 524 | 21.0% | 1.397 | +112.0% | 4.49 |

+71% on the metric that decides, and the complement collapses. Nothing in
seventeen prior families has done this.

### The controls

| # | control | result |
|---|---|---|
| 1 | **halves** | PASS — improves in both: h1 1.180→1.420, h2 1.799→2.151 |
| 2 | **down years** | MIXED — 2021 0.900→1.002, 2022 1.093→1.376 (both DOWN years improve, so it is not the bull-market artifact). But **2023 degrades, 1.294→1.034**, and 2026 has n=6 and is meaningless |
| 3 | **US30, second instrument** | **CANNOT BE RUN** — see below |
| 4 | **threshold** | PASS, and strongly — a plateau, not a cliff: 30th 27.6, 40th 46.5, 50th 47.7, 60th 41.9. Only the 20th (n=243) falls away |
| 5 | **is it Bollinger or just low vol?** | PASS, and this is the surprise — ATR-rank gating does **not** reproduce it: 10.22 / 11.15 / 8.20 at the 30th/40th/50th percentile. corr(bandwidth rank, ATR rank) = +0.54. The σ-over-price construction is doing work that an ATR filter does not |
| 6 | **quality vs leverage** | PASS — payoff 2.10:1 → **2.55:1** and win rate 21.8% → 24.7%. The trades are genuinely better, not merely larger |

### Why control 3 could not be run, stated rather than glossed

US30 has 28,591 30-minute bars against gold's 78,693, and **the champion has no
edge on it in this dataset at all**: baseline PF 0.657 on n=34 (bars mode) and
0.656 on n=38 (clock mode). You cannot ask whether a filter improves a system
that has no edge to improve, and n≈35 could not answer it if you could. The
squeeze gate scores 0.633 / 0.472 there, which is noise around a broken
baseline and must not be read as a failure any more than as a pass.

**This is the control that has killed the most candidates in this project.**
Its absence is the single largest open risk on this finding, and no amount of
passing the other five substitutes for it.

### Standing status

**PROMOTED TO CANDIDATE, NOT ADOPTED.** It has cleared more than anything
before it, including the control that distinguishes it from a generic
volatility filter. It has not cleared the second instrument, and it degrades in
one of four up years. Adoption requires either a US30 dataset the champion
actually works on, or a third instrument.

---

## B-0xx — The rest of the scalping checklist and the MTF trend-break plan: every new element loses

All at matched 25% drawdown, baseline net/DD 27.26.

| element | source | net/DD | verdict |
|---|---|---|---|
| volume spike on the break | checklist item 1 | 10.87 | **worse than its own control** (no-spike: 13.42) — the spike is a negative filter |
| 4h trend agreement (directional) | MTF plan §3 | 11.30 | PF rises to 1.688, compounding halves |
| 4h agreement + squeeze | combined | 12.68 | the 4h gate **damages** the squeeze finding (46.53 → 12.68) |
| candle confirmation on the break | MTF plan §4.3 | 6.35 | engulfing/pin gating cuts n to 322 and gains nothing |
| hard 2R target, 100% of size | MTF plan §5 | 25.60 | worse |
| hard 2R target, 50% of size | MTF plan §5 | 27.13 | indistinguishable |
| TP at each pivot level, 25/25% | checklist item 5 | 24.30 | worse |
| TP at each pivot level, 33/33% | checklist item 5 | 22.16 | worse |
| TP at pivots + breakeven move | checklist item 5 | 7.06 | **the BE move is destructive** — WR rises 23.7%→28.6% and net collapses |
| **stop just below the broken level** | checklist item 3 / MTF §5 | **2.71** | **the worst result of the session** |

**Why the level-as-stop fails, measured.** The checklist says the flipped level
"can also act as a STOP LOSS". The median distance from a breakout close back to
the level it just broke is **0.38 ATR** (10th pct 0.06, 90th pct 1.26). The
champion's stop is 4.24 ATR. A stop at the broken level sits *inside the noise*:
win rate falls to 10.0% and net/DD to 2.71. This is a concrete, quantified
reason, not a preference.

**The breakeven move deserves its own note** because it is the most commonly
recommended risk practice in retail material and it is the second-worst result
here. It does exactly what it promises — win rate up 4.9 points — and it costs
96% of the return, because it removes the trades that were going to become the
6:1 winners this system lives on. On a 21.7%-win-rate trend system, protecting
the middle of the distribution destroys the tail that pays for everything.

**The reversals note supplied alongside states no mechanical rule** — it defines
what a reversal is and warns they are hard to predict. Recorded as received;
there is nothing in it to falsify.

---

## B-0xx — The MTI set: "never risk more than 2-5% per trade" would have destroyed the account

Five PDFs from Market Traders Institute, ~145 pages. **Two of the five duplicate
each other byte-for-byte** (`15_FXProfit_Hacks.pdf` and `...Hacks1.pdf`, both
extracting to md5 `2da1a431dd8d9e34b34ecde7af49ba8c`). Of the remaining ~145
distinct pages, **four claims are specified precisely enough to falsify.** The
rest is psychology, workflow advice, and a vendor pitch. That is the finding for
those documents, not a shortfall in the testing.

### Hack #4, and this one matters because it is about a real account

"Never risk more than two to five percent of your overall account in any given
trade." The champion, solved to a 25% drawdown budget, risks **0.72%**. MTI's
floor is 2.8× that; its ceiling is 6.9×.

| risk/trade | n | PF | net | **max DD** | equity multiple |
|---|---|---|---|---|---|
| 0.50% | 786 | 1.555 | +303.7% | 17.70% | ×4.0 |
| **0.72% (champion)** | 789 | 1.588 | +665.9% | **24.67%** | ×7.7 |
| 1.00% | 789 | 1.626 | +1,511.9% | 35.25% | ×16.1 |
| 2.00% | 789 | 1.651 | +10,840.4% | **66.58%** | ×109 |
| 3.00% | 789 | 1.574 | +26,586.4% | **81.24%** | ×267 |
| 4.00% | 789 | 1.469 | +30,211.5% | **89.23%** | ×303 |
| 5.00% | 789 | 1.390 | +26,694.6% | **94.45%** | ×268 |

**MTI's recommended floor of 2% costs a 66.6% drawdown. Its ceiling of 5% costs
94.45%** — an account down 94% needs a 1,700% gain to recover, and no one keeps
trading a system through that. The advice is written for a market and a win rate
it does not name; applied to a 21.7%-win-rate trend system on gold it is not
conservative, it is ruinous.

**Note the second-order effect:** profit factor peaks at 2% (1.651) and then
*falls* to 1.390 at 5%. Beyond a point, extra size stops buying return and only
buys drawdown — the terminal multiple is lower at 5% (×268) than at 4% (×303).
Over-leverage does not merely add risk; past the peak it destroys return too.

**Standing consequence.** Percentage-risk advice is meaningless without the win
rate and payoff it was calibrated on. This desk sizes from a **drawdown budget**
(binary-search risk% to hit the target DD), which is the same statement made in
the units that decide survival. Any future "risk X% per trade" rule gets
converted to its drawdown before it is considered.

### The other three claims

| claim | source | result |
|---|---|---|
| StochRSI outside 80/20 "is expected to u-turn" | Hack #6 | **no.** 16 tests, best \|t\| = 1.38. The oversold-long arm is *negative* at 32 bars (t = −2.04): oversold gold drifts up **less** than unconditional |
| "When one session ends and another begins, the opposite reversal point typically forms" | Hack #11 | **no.** NY open sets the day's extreme far more often (0.086 vs 0.049) but its flip rate is **lower** (0.509 vs 0.516). Same result as the earlier NY-open test: expansion, not reversal |
| "Wildcard candlesticks the closer we get to the end of the month" | 25 Tips #5 | **no.** Last three days: mean range 0.9903 ATR and flip rate 0.5116, against 0.9836 and 0.5161 for the rest. Indistinguishable |

Hack #1 (multiple timeframes) and Hack #3 (candlestick formations) were already
refuted this session at matched drawdown — 11.30 and 6.35 against 27.26.

**Tip #14, "you will never go broke taking a profit," is directly contradicted
by this session's own measurements**: the breakeven move scored net/DD 7.06
against 27.26, and hard 2R/3R targets 25.1–27.1. On a 21.7%-win-rate system,
taking profits early is exactly how you go broke slowly.

---

## H82 — The AU200 10:00 hour moves enough for a 10-point target; the direction is a coin flip

**Evidence (our own, outranks testimony):** 397 sessions of 1-minute OANDA
AU200AUD, 2025-01-13 .. 2026-08-07. From the 10:00 close to the 11:00 close:
53.1% up / 45.4% down; median absolute move **13.0 points**; **64.6% of sessions
move >= 10 points** inside that single hour.

**Belief:** the magnitude the user observes at the open is real and repeatedly
verified. The *side* carries no information from any filter tested to date.

**Invalidation:** a filter that calls the side of that hour above ~57% out of
sample, on n >= 200, net of measured spread.

**Consequence:** stop testing exits on this setup. Every exit family has now been
swept (fixed time 1h/2h/to-close, TP/SL grids 10/15/20/30, trailing at multiple
distances, and the user's own one-bar hold). The binding constraint is entry.

---

## H83 — EMA200 + RSI(50) + SuperTrend(3.1, 97) does not call the side of the AU200 open

**Evidence:** user-frozen spec, entries at the 10:00 candle close, exit at the
next bar's close, four timeframes. Gross PF 30m 0.784 / 45m 0.780 / 1H 1.123 /
2H 0.983; net of 2 pts cost all below 1.0. **Null test:** ignoring the filter
entirely and going long on the same days beats the filtered signal on 30m
(+1.47 vs -1.27), 45m (+0.82 vs -1.77) and 2H (+0.76 vs -0.16).

**Independently replicated:** user ran the same script on 30m over a different
window on TradingView and returned PF 0.544 / 37.20% win against our 0.537 /
37.8%.

**Status:** the three-indicator filter is REJECTED for this setup. 1H is the one
cell where it adds anything (+0.58/trade over always-long) and is not itself
significant.

**Invalidation:** a longer sample (2019-2026 1-minute data) showing 1H gross
PF > 1.2 with n > 400.

---

## H84 — Reported performance is a claim about the execution model, not about the market

**Evidence:** five separate "champions" in this project have now turned out to be
execution artifacts (0.5-pt trail path, 15m->5m lookahead, SMA50/200 noise,
BUG-035 execution lookahead, BUG-036 tick-unit trail). In the BUG-036 case the
identical entries scored PF 2.75 under the platform's intrabar guess and PF 0.31
under 1-minute path resolution.

**Belief:** a profit factor is a joint statement about a signal AND a fill
assumption. Quoting one without the other is meaningless. The fill assumption
must be stated with every result and is the first thing to attack.

**Practical test that settles it:** reduce the strategy to a close-to-close
construction. That has no intrabar path, so an independent simulator and the
platform must agree. If they don't, one is broken.

**Invalidation:** none expected; this is now a standing methodological belief.

---

## H85 — External research documents require verification before they enter the knowledge base

**Evidence:** four uploaded research documents were fact-checked this session.
Every one mixed genuine, checkable infrastructure with fabricated specifics:
an SEC insider-trading case that does not exist (with invented fines), Form 4
filings attributed to an executive under a title she does not hold, precise
accuracy percentages (70% AAPL, 75% NVDA) with no source, a leak misdated by
four years with the document count more than doubled, and a real Initial Balance
statistic whose sample (5,519 ES+NQ days) was reattributed to NQ alone (2,833)
with its 82.7% ES figure restated as an unrelated 82.17% NQ continuation rate.

**Belief:** plausible, well-formatted research documents in this domain
frequently contain invented specifics that inherit credibility from the real
material around them. The mix is the hazard, not the falsehood alone.

**Rule:** before any external document informs a strategy, check names, dates,
case numbers, sample sizes and URLs. File it in `documents/` with an Editor's
Verification Note recording what was checked. Do not promote to
`trader_playbooks/` (which is read every session) until verified.

**Corroborates:** the source-hierarchy principle already in the repo — primary
records outrank scholarly analysis outrank synthesis outrank commentary. The
AU200-BASE trade list (primary) beating the TradingView dashboard (derived) is
the same principle proving itself on our own data.

---

## H86 — Longer timeframes carry structural edge; sub-15m does not, and the cause is cost not indicators

**Evidence, from three independent routes:**

1. **This repo's own measurement (2026-08-13):** a 350-cell achievable-fill
   search on AU200 around the open returned **7 of 350 cells above PF 1.0**
   against ~175 expected by chance. A fixed ~2-point round trip at ~1 trade/day
   dominated every cell. Separately, the only system here that has survived all
   controls is a **daily** z-reversion engine (PF 2.31, 7/7 years).
2. **MSPV2 (externally supplied, reports its own negatives):** win rates of
   **22-30% on 1m Gold regardless of indicator combination**, concluding *"this
   is not an indicator problem, it's a timeframe problem"*, and grading 1m as
   AVOID for any asset.
3. **AlgoAlpha Trend Targets report (externally supplied):** daily Sharpe an
   order of magnitude above hourly across 8 assets — though see the verification
   note, as its annualisation is inconsistent and the cells are in-sample.

**Belief:** the binding constraint at high frequency is transaction cost, not
signal quality. Adding indicators to a sub-15m system cannot fix a cost problem.
Three different instruments (AU200, XAUUSD, BTC/equities), three different
methods, same conclusion — this is genuine corroboration, not correlated sources.

**Invalidation:** an intraday system that clears cost on a measured (not
assumed) spread, out of sample, with n > 200.

**Consequence:** before another intraday round, **measure the spread**. If the
real AU200 cost at 10:00 is 1 point rather than 2, several borderline cells
change sign and the 350-cell sweep must be re-run. That measurement now gates
the whole family.

---

## H87 — Scattered optimal parameters across assets is evidence against an edge, not a reason to optimise per asset

**Evidence:** the AlgoAlpha report searched 36 parameter combinations per
asset/timeframe, found optima scattered across the entire grid (Factor 8-14,
ATR 60-120, WMA 20-60, "no single value dominating"), and concluded this
"underscores the necessity of tailored optimization for each trading instrument."

**Belief:** that inference is backwards. A real effect produces a **plateau** —
neighbouring parameters perform similarly and the same neighbourhood works
across related instruments. A **spike** that lands somewhere different for every
asset is what noise looks like after optimisation. This repository already uses
plateau-versus-spike as a control; this document is a clean external example of
the failure mode.

**Rule:** when a source reports per-asset optimal parameters, check whether the
neighbourhood is flat. If the report does not show the neighbourhood, treat the
headline number as the maximum of the search, not as a performance estimate.

---

## H88 — Stacking confluences raises in-sample appearance and lowers evidence; it does not raise win probability

**Claim under test:** "More conditions aligned = mathematically higher
probability" (four-trader hybrid v3.0, Absolute Law #2, requiring 4-5
simultaneous confluences).

**Evidence against, from three externally-supplied documents that measured it:**

- **MSPV2:** *"v6 printed zero signals because it required 4+ conditions all true
  simultaneously on one candle... Lesson: max 3 hard requirements on one bar."*
- **MSPV1:** *"FAIL 6: Too many conditions = no signals... fired 0-2 signals per
  day on 15m XAUUSD. Too few signals to validate statistically."*
- **MSVPSYSTEM:** *"More than 7 = almost never fires."*

**Evidence from this repository:** the over-gated confluence engines
(`omnibus_four_model_engine`, `multivoice_confluence_engine`) exhibited the same
behaviour, and the 350-cell AU200 sweep showed that cells surviving the most
filters were not the cells with the best out-of-sample behaviour.

**Belief:** each additional required condition shrinks the sample and increases
selection bias. Conditions bought in-sample by adding filters are the cheapest
and least reliable kind of edge. A rule requiring 4-5 simultaneous conditions in
a two-hour daily window will not accumulate a testable sample in reasonable time.

**Correct formulation:** conditions should be *independent* and each should be
justified separately against its own null. Three independent conditions beat
seven correlated ones. Count independence, not confluences.

**Invalidation:** a system whose win rate rises monotonically with condition
count *out of sample*, with the trade count reported at each level.

**Note:** this belief is now supported by four separate documents in the same
supplied series, each of which measured the failure and then had its conclusion
reversed by the next version. The series does not propagate its own findings
forward.
