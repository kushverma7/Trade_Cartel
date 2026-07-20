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
- Multi-timeframe alignment before sizing: 7 independent (Cognitive
  Architecture, Valentini 15m->1m->15s stack, Kurisko quad bands, voice #9
  nested Renko brick-size stack, Wendell walls-vs-chairs, voice #11's
  HTF-bias/LTF-entry pattern, voice #13's H4-direction/15m-zone/5m-refine/
  1m-execute cascade — seven schools, seven different mechanics, same
  structural conclusion: never size a trade without checking a higher
  timeframe first).
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

## Retired Beliefs
(none yet)
