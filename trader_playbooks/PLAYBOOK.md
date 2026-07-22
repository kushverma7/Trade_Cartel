# PLAYBOOK v2026-07-19
# Living document per COGNITIVE_ARCHITECTURE.md Mechanism 2.
# Review after every ~20 analyzed trades. Evolve, don't hoard.

=== SCALP SETUPS ===

1. **Session Trendline Breakout** (candidate, NOT proven)
   - Conditions: XAUUSD 5m, OLS trendline (lookback 22), London 03:00-05:00
     or NY-open 08:30-11:00 NY time only
   - Entry: close breaks optimized trendline; Stop: 1.2x ATR(14); Target: 2x ATR
   - Evidence: **RETRACTED (2026-07-20)** — the PF 3.656 backtest was on
     only ~2 months / 117 trades (free-plan data limit), too small to call
     evidence. No sizing upgrade or "flagship" label until re-tested on a
     real sample (6-12mo+, 300+ trades, paid feed). Files:
     strategies/gold_scalper_final.pine
   - Sizing: exploratory only until re-validated. Confluence upgrade
     (aligned tier-A candle pattern) still applies once evidence exists.

2. **HTF Wall Reclaim** (Reversal Sniper v3 — unproven, testing)
   - Conditions: flush >= 0.3 ATR beyond prev day/week H/L or Asia range,
     then reclaim close back inside within 5 bars
   - Entry: reclaim close; Stop: behind 4-bar extreme; TP 1R/2R split
   - Status: v3 awaiting backtest. v2 variant RETIRED (see What's Not Working).

3. **CPI Confirm-Continuation** (news harness)
   - Conditions: 8:30 ET event candle >= 2x ATR50; later close breaks its extreme
   - Entry: break close; Stop: opposite extreme + 0.2 ATR; TP 1.5R; time exit
   - Status: mode won the decisive 2025-26 CPI days in event match; needs tester run.

=== WHAT'S WORKING NOW ===
- Session filter (B1) — apply everywhere by default
- Flip execution on trendline signals (always-in) — stats pending user backtest

=== WHAT'S NOT WORKING ===
- Auto 5m supply/demand zone reclaims (PF 0.731, retired)
- Naked patterns, 24/7 trading, high trade counts

=== MARKET CONDITIONS ===
- Regime notes (2026-07): gold whipsawed by Iran conflict + inflation swings
  ($4,594 Jan -> $5,177 Mar -> $4,164 Jun). Event-driven regime: session
  discipline and news windows matter more than trend-following.

=== MASTER ENGINE (final synthesis, 2026-07-19) ===
indicators/trade_cartel_master_engine.pine
- Core: candidate trendline breakout (untested at scale) (22) + optional H7 full-body confirm
- Confluence vote 0-12: session [B1] +2, out-of-balance regime [PBD] +2,
  tier-A candle [Nison] +2, aggression [Valentini] +2, VWAP side (not
  beyond 2SD) +2, fresh level [H8] +2
- Grades: 8+ = A+, 5-7 = B, below = suppressed (grey x with tooltip)
- Hard vetoes: opposing tier-A candle, recent CVD divergence against,
  8:25-8:45 ET news window, over-rejected level
- Dashboard shows all layer states live; alerts per grade

=== CLEAN SIGNAL ENGINE (distilled variant, 2026-07-20) ===
indicators/trade_cartel_clean_signal_engine.pine
- Same core + same confluence layers as MASTER ENGINE above (session
  [B1], value-area regime [PBD], tier-A candle [Nison], fresh level
  [H8], CVD divergence veto, news blackout [B3]) -- NOT a new voice,
  same building blocks, restructured as a HARD AND-GATE instead of a
  0-12 partial score. Every enabled filter must agree -> fewer, more
  selective signals than the Master Engine's B-grade tier, addressing
  user feedback that OR-combined signals fired too often to call
  "clean." (Dropped: aggression/VWAP layers, to keep the gate leaner
  -- can be re-added if the stricter version proves too sparse.)
- TP1/TP2/SL lines auto-drawn on every signal: SL = entry -+ ATR x
  stopAtrMult (default 1.2), TP1 = 1R, TP2 = 2R off that stop distance
  -- matches this project's standing scale-out convention (1/3 @ 1R,
  1/3 @ 2R, 1/3 runner). User-configurable multiples.
- **User feedback (2026-07-20, ran live on chart)**: wrong signal
  philosophy for what the user wanted -- this engine's core is a
  trendline BREAKOUT (continuation), which by design never catches
  tops/bottoms, and fires too rarely. Led directly to the new
  TOP/BOTTOM engine below.

=== TOP/BOTTOM REVERSAL ENGINE (2026-07-20) ===
indicators/trade_cartel_topbottom_engine.pine
- Different signal philosophy from both engines above: reversal/
  exhaustion catcher, not a breakout/continuation system. Synthesizes
  the most corroborated reversal ideas across the knowledge base: the
  wall+sweep+RSI-exhaustion+rejection-candle stack (reversal_sniper_
  strategy.pine), Hima Reddy's 2-bar test-failure rule (voice #19),
  old-top/old-bottom Buying/Selling Point #1 (Hima Reddy), and tier-A
  reversal candlesticks (hammer/shooting star/engulfing) as an
  opposing-candle veto.
- Walls: prev day/week H/L, Asia range, round numbers, and a FROZEN
  recent swing pivot (replaced only when price closes through it --
  deliberately NOT an auto-regenerating zone). This project's own
  MEMORY.md documents that auto S/D zones caused the original PF 0.731
  failure (zones regenerate too often on LTF gold, turning trend
  pauses into fake reversals) -- excluded here on purpose.
- "Avoid the chop" = two mechanisms: (1) ATR regime filter, skip
  abnormally low-volatility/dead periods; (2) room-to-opposing-wall
  filter, require real ATR-scaled distance so a "reversal" has
  somewhere to actually go. The wall+trigger+RSI+rejection stack is
  itself chop-resistant since random noise rarely satisfies all four
  simultaneously.
- Same TP1/TP2/SL line + hit-tracker pattern as the Clean Signal
  Engine, for consistency across the repo's newer engines.
- "Most corroborated ideas" -- NOT a claim of backtested performance.
  UNTESTED at scale, same standing rule as everything else.
- **User feedback (2026-07-20, ran live on chart, 252 resolved
  trades)**: (1) signals clustered tightly at the same support/
  resistance during a grind -- bar-count cooldown alone didn't stop a
  wall from refiring since the wall itself doesn't move. (2) PF-analog
  ~0.90 (78 TP2 wins x 2R vs 174 SL losses x 1R = -18R net); win rate
  30.95% was just under the 33.3% breakeven needed for a 2:1 payoff.
  Fixes applied: distance-based re-arm (require price to move
  minReArmAtr x ATR away from the LAST signal's price before a new one
  of either direction can fire -- addresses clustering directly),
  added the ADX "never fade a strong trend" veto that was already
  proven out in reversal_sniper_strategy.pine but missing from this
  engine's first version (should improve win rate by not calling
  reversals against strong momentum), cooldown raised 8->20 bars.
  Re-test pending -- no new PF/WR numbers yet.
- **Second live run (2026-07-20)**: PF-analog got WORSE (0.67 vs 0.90
  before), trade count dropped 252->92. The ADX trend veto's
  assumption ("never fade a strong trend improves reversal quality")
  did NOT hold on this data -- likely because some pullback-catches
  inside an active trend were actually contributing wins, and the
  veto removed those along with genuinely bad countertrend fades.
  Flagged honestly rather than guessing another "logical" fix:
  **useTrendVeto now defaults OFF**, kept as a toggle for the user to
  A/B test explicitly rather than trusting theory-based reasoning that
  just got falsified. Clustering also wasn't fully fixed by the
  distance-based re-arm (gold's 5m ATR is small enough that price can
  move >1.5xATR while still bouncing around the SAME wall) --
  replaced with an IDENTITY-based re-arm: block a new signal against
  the same wall value that produced the last signal in that direction
  until the wall itself changes (or price moves far enough as a
  secondary guard). Re-test pending.
- **Third live run (2026-07-20)**: PF-analog 0.85 (up from 0.67 after
  reverting the ADX veto default, but still below both 1.0 and the
  first run's 0.90) -- 130 SL / 55 TP2, win rate 29.7%. Clustering was
  STILL visible on-chart despite the take-2 identity-based re-arm.
  Root cause found: take 2 gated on (wallChanged OR priceMovedEnough)
  -- wall IDENTITY changes almost trivially (a different wall TYPE
  becoming nearest by a cent counts as "changed"), so that OR was true
  almost every bar and never actually blocked repeat signals. Fixed by
  dropping the wall-identity path and gating on price distance ALONE
  (the harder-to-trivially-satisfy measure of whether price actually
  left the zone). Re-test pending -- this is the clearest diagnosis so
  far; prior "fixes" were papering over a genuine logic bug, not a
  parameter-tuning problem.
- Lightweight hit-tracker (not a full trade simulator like the Hima
  Reddy engine's): counts SL-hits vs TP2-hits, tracks whether TP1 was
  touched en route, reports TP1/TP2 reach rate -- non-repainting,
  evaluated on closed bars only, checks start the bar AFTER signal.
- "Best filters" = most independently corroborated ideas in this
  project's knowledge base reused here, NOT a claim of backtested
  performance. UNTESTED, same standing rule as everything else.
- **Fourth live run (2026-07-20) -- FIRST PF>1 RESULT THIS SESSION**:
  PF-analog **1.11**, win rate **35.7% (40/112 trades)** -- the first
  configuration to cross both 1.0 PF and the 33.3% breakeven for a 2:1
  payoff, after every prior variant (0.90/0.67/0.85/0.82) stayed under
  both. Three changes together, confirmed via TradingView's own Inputs
  panel screenshot (not inferred): **2-Bar Test-Failure Trigger turned
  OFF** (sweep-only, not sweep-or-test-fail), **Close In Far % Of
  Range tightened 0.35->0.2** (much stronger rejection candle
  required), **RSI Overbought 66->72 / Oversold 34->31** (genuine
  extremes only, not mild OB/OS). All three now set as the new
  defaults. Caveat, per the 2026-07-20 standing rule: 112 trades is a
  real sample and a real directional result, but it's still on the
  free-plan short data window (~2 months) -- this is evidence of a
  promising direction, not a "proven" edge. Re-test on a longer/paid
  data feed before this earns "proven" or gets sizing weight. Isolating
  which of the three changes did the most work (vs. sweep-only alone,
  vs. tighter rejection alone, vs. tighter RSI alone) has not been done
  -- worth a follow-up single-variable test if pursuing this further.

=== SPACEMAN MERGES (2 separate engines, 2026-07-20) ===
User request: merge "Key Levels SpacemanBTC IDWM V13.1" (@sbtnc, level
computation only, first reused in kama_key_level_signal_engine.pine)
with the project's two DIFFERENT "quarter theory" sources, built as
TWO SEPARATE engines per explicit instruction -- not one combined tool.

indicators/spaceman_daye_quarters_engine.pine (merge #1, TIME-based):
- Merges SpacemanBTC's True-Open-equivalent levels (daily/weekly/
  monthly/quarterly opens, prev week H/L, Monday range) with Trader
  Daye's Quarterly Theory (voice #4) JUDAS sweep+reclaim+SMT signal --
  this repo's existing, most-refined time-based reversal mechanic,
  reused as-is from quarterly_theory_engine.pine.
- The actual merge: TP1/TP2 are the NEAREST Spaceman levels ahead of
  the entry in trade direction (True Weekly Open, PWH/PWL, Monday
  range, monthly/quarterly opens), sorted by distance, with an ATR
  fallback only if no level exists ahead -- replacing the original
  engine's lack of any defined exit with a level-driven target.
- Fixed the nested-function issue during writing (Pine doesn't allow
  a function declared inside another function) before it could ship
  as a compile error.
- **Live test found a real bug (2026-07-20)**: 12/12 trades hit SL,
  0% touched even TP1. Root cause: the stop referenced pdLow/pdHigh
  (the level BEING swept) instead of the actual sweep extreme (this
  bar's low/high, which is what pierced pdLow/pdHigh to trigger the
  signal). Since a sweep by definition already goes past pdLow/pdHigh,
  using it as the stop reference placed the stop INSIDE the sweep
  zone rather than beyond it -- effectively guaranteeing an immediate
  stop-out on any retest. Fixed: stop now references low/high (the
  actual sweep extreme) with the ATR buffer applied from there.
- **Re-test result (2026-07-20)**: 7 SL / 1 TP2 (8 trades), PF-analog
  0.14 -- real improvement over 0/12 (confirms the stop-reference fix
  wasn't a wash), but still clearly not working. Notable signature:
  TP1 and TP2 reach rate are BOTH exactly 12.5% -- meaning every one
  of the 7 losses never touched TP1 at all before stopping out. That's
  different from "stop too tight on a retest" (which would show some
  TP1 touches before eventual losses); it points to either low-quality
  JUDAS entries on this data, or the stop buffer (stopBufAtr=0.2)
  still being too tight against normal post-sweep noise even with the
  correct reference point. Sample is only 8 trades -- too small to
  commit to either theory. Next test, not yet run: widen stopBufAtr
  (e.g. 0.2 -> 0.5-1.0) and re-check whether TP1 starts getting
  touched before losses, which would isolate stop-tightness as the
  cause vs. entry quality.

indicators/spaceman_yotov_quarters_engine.pine (merge #2, PRICE-based):
- Merges SpacemanBTC's structural levels with Yotov's Quarters Theory
  (voice #18) large-quarter price grid. Core hypothesis: a pure
  price-ratio level (Yotov, no market-structure input at all) is a
  stronger reversal candidate when it ALSO coincides with an
  independently-derived structural level (Spaceman) -- two unrelated
  frameworks agreeing is real confluence, not something either alone
  would surface.
- Signal: large-quarter zone touched + confluent with a Spaceman level
  (within an ATR tolerance) + rejection candle + RSI side. TP1/TP2 =
  the next 1-2 large-quarter levels in trade direction (Yotov's own
  grid spacing), SL = beyond the zone with an ATR buffer.

Both: TP1/TP2/SL lines + hit-tracker, same pattern as the Clean Signal
/ Top-Bottom / Hima Reddy engines built earlier this session. "Best
entry/exit" = the most-refined existing mechanics in this repo reused
here, NOT a claim of backtested performance. UNTESTED, no "proven"
language, per the 2026-07-20 standing rule.

=== UPDATED RULES ===
- Flat into CPI/8:30 prints; trade the confirmation after (B3)
- Every strategy ships with: non-repainting math, realistic costs,
  per-scenario alerts on bar close
- Conviction scoring (0-12) maps to size: 0-4 no trade, 5-7 = 0.5%,
  8-10 = 1-2%, 11-12 = 2-4% (Cognitive Architecture, Profit Engine)
- Scale-out standard: 1/3 @ 1R, 1/3 @ 2R, 1/3 runner w/ BE stop
- Scaled-stop option (Roppel 3-5-7 adapted): exit thirds at 0.5R /
  0.75R / 1R adverse instead of full size at the stop — for future
  strategy wrappers, A/B against single stop
- Cushion protocol: escalate risk only against banked profit (day or
  year level); no cushion = minimum size [2 independent sources]
- CANDIDATE (H50, Hougaard): scale-IN mirror of the scale-out rule --
  the first add to a winner only at a point where the original
  position's stop can move to breakeven, and that becomes the stop
  for the added position too (total risk never increases as size is
  added). A/B against single-entry before adopting.
- CANDIDATE (H24, Steve/MMM4x): time-stop — scratch any trade with no
  meaningful profit after ~2h (24 bars on 5m). A/B on master strategy
  before adoption.

=== EXECUTION / BROKER RISK (operational, not a trading school) ===
Source: "Forex James" broker-risk video, 2026-07-20. Not chart-pattern
content — no playbook/engine created, logged here as standing
operational hygiene:
- Slippage/requotes scale with volatility; some brokers profit MORE
  from slippage than from spread/commission — direct financial
  incentive to slip retail traders on volatile prints (CPI etc.).
  Relevant to our own CPI harness: expect worse fills than backtest
  assumes around 8:30 ET event candles specifically.
- Recommends WIDER stops over mental stops (mental stops = emotional
  cutting, and predictable-distance hard stops are themselves a
  target — same "stop-hunt geometry" concept as voice #8/Steve, from
  a totally different angle: broker-side incentive rather than
  market-structure manipulation).
- Document slippage with screenshots; switch brokers if unresolved.
- Broker due diligence before committing capital: refund/withdrawal
  speed test, execution latency test (source flags 10-second fills as
  bad), avoid picking a broker on cost alone or on reviews (reviewers
  are frequently paid, competitors leave bad-faith negative reviews).
- **DIRECT TENSION WITH THIS PROJECT'S CORE IDENTITY**: source argues
  scalping (short timeframes, tight stops) maximizes exposure to
  broker-side manipulation/slippage, and recommends swing/longer-term
  holds specifically to reduce it. Trade Cartel is a 5m gold SCALPING
  system by design (user's stated trading profile). This is not a
  reason to abandon the approach, but it is a real, named risk that
  should factor into position sizing and broker selection for live
  execution — flagged explicitly rather than silently absorbed.
- Pure PA/SMC source (voice #13, 2026-07-20) risk rules, consistent
  with and adding to the above: 1% risk/trade, hard stop at -2%/day
  (then stop trading and backtest the mistakes), always flat before
  session end (corroborates Steve/MMM4x's identical rule), immediate
  move to breakeven ahead of high-impact news if already in a
  position, and spread buffering — widen both the entry limit AND the
  stop loss by the spread amount when spreads run wide, to avoid
  missed fills or premature stop-outs. Their 1.5-2 pip fixed stops are
  NOT a generic sizing rule to copy — that only makes sense paired
  with their precision 1m-refined zone entries, not looser setups.

=== KNOWLEDGE ENGINES (observation layer) ===
- indicators/mm_cycle_engine.pine (voice #8, Steve/MMM4x): ET time grid
  w/ Brinks windows 03:30-03:45 & 09:30-09:45, Asia-range stop-hunt
  zone tiers, 3-tap fade signals, ADR-thirds level counter, H/L lock
  timer. Hypotheses H20-H24 — observe/score before any sizing. v2
  (same lineage, not a new voice): EMA 5/13/50/200/800 level stack,
  peak-to-peak full-ADR box stack, TDI shark-fin proxy, railroad-track
  tags, ID50 rotation reentry, standard daily pivots. H34-H35.
- indicators/renko_abc_scalper.pine (voice #9, Renko/HA mentor): synthetic
  non-repainting Renko+HA construct, 12/24/36 EMA cluster, ABC/123
  swing-failure structure break, "floating brick" entry trigger,
  counter-color run exit counter. Hypotheses H25-H29 — H29 flags gold
  applicability as unresolved (source's own student doubted it).
- indicators/wendell_zone_engine.pine (voice #10, Online Trading Academy):
  precise proximal/distal S/D zone construction, freshness filter
  (untested-only), basing-candle-count cap, departure-strength filter,
  retest-depth confirmation, HTF wall / LTF chair overlay. H30-H31 —
  **direct rework candidate for B2** (our failed auto-zone logic, PF
  0.731); backtest before concluding S/D zones don't work on gold.
- indicators/fx_master_pattern_engine.pine (voice #11, FX Master
  Pattern school): contraction-box + average-price phase detection run
  on both LTF and HTF (via the request.security function-call
  pattern), HTF-bias-confirmed cross-back entries, first-vs-later
  opportunity counter (H32 sizing decay). H32-H33.
- indicators/alchemist_smc_engine.pine (voice #12, "White Seraph" SMC
  glossary): IDM-gated BOS/CHOCH (structure break only trusted after
  its inducement pullback is swept), SBR/RBS support/resistance
  role-flip retest tagging, Quasimodo (QML) 5-point swing-failure
  pattern. H36-H38. The PDF's Quarterly Theory content was folded into
  the EXISTING quarterly_theory.md/engine as same-lineage corroboration,
  not duplicated here -- this file is only the genuinely new SMC
  material.
  v2 (2026-07-20, re-review of the source PDF's page IMAGES, not just
  text -- see BELIEF_REGISTER H60-H61): Fibo Storyline (custom
  ratio-set retracement KEY-zone entry + same-timeframe scale-in) and
  Fibo Circle (1.893x/2.0x extension of an internal post-leg
  retracement, KEY-level retest entry) RECLASSIFIED from "too garbled
  to codify" to built, both off by default as a lower-confidence tier.
  OCL remains not built -- geometry is now clear (HTF candle level ->
  inducement trendline -> LTF order block) but the anchor-candle
  selection rule is still unstated by the source.
  STANDING RULE (2026-07-20): one engine file per voice/
  school, extended in place for future transcripts from the same
  source -- never fork a new .pine for the same author.
- indicators/candlestick_engine.pine EXTENDED (2026-07-20,
  "@Thechartcornerr" cheat sheet): added Kicker, Marubozu, Three
  Inside/Outside Up/Down, Rising/Falling Three Methods, Inverted
  Hammer/Hanging Man, Dragonfly/Gravestone Doji, Spinning Top,
  Long-Legged Doji -- same file, same subject, extended in place
  rather than forked. H39.
- indicators/chart_pattern_engine.pine (NEW -- genuinely new pattern
  category, not an extension of candlesticks): Double/Triple Top/
  Bottom, Head & Shoulders (+inverse), Ascending/Descending/
  Symmetrical Triangle, Rising/Falling Wedge, Bull/Bear Flag, Bull/
  Bear Pennant, Bull/Bear Rectangle -- pivot-buffer-based multi-swing
  geometric pattern detection with neckline/breakout triggers. H40.
  v2 (2026-07-20, "Josh Trade" ebook, extended in place): measured-
  move price targets w/ target lines, optional volume-confirmation
  filter (default off), neckline/boundary retest tagging.
  v3 (2026-07-20, re-review of BOTH sources' page IMAGES, not just
  text -- see BELIEF_REGISTER H56-H59): Cup & Handle / Inverted Cup &
  Handle and Diamond Top/Bottom RECLASSIFIED from "not built" to
  built (rim-pivot + trough-depth + shallow-handle heuristic; chained
  broadening-then-narrowing pivot-slope heuristic, respectively) --
  the "too subjective" call was actually a missed-diagram problem, not
  a real limit. Also added: H&S high-probability tag (flat/down
  neckline + right shoulder <= left shoulder, informational, doesn't
  gate the signal), and an optional fixed-R:R target mode (`showRR`,
  default off, dominant ratio 1:3 from source's worked examples,
  anchored at the retest bar) as an A/B alternative to the v2
  measured-move target convention.
- indicators/pure_pa_smc_engine.pine (voice #13, Pure PA/SMC): IFC
  (3-candle gap) detection, strong/weak structural point
  classification (opposite-zone break test, non-retroactive), single
  freshest zone per side w/ mitigated status, "who's in control"
  regime flag, S/D flip detector, liquidity-grab-vs-BOS candle
  geometry, equilibrium 50% entry marker. H41-H44.
- indicators/trader_dale_volume_profile_engine.pine (voice #14,
  Trader Dale): rolling volume-weighted price histogram (POC, value
  area, D/P/b/Thin shape classification), generalized HVN/Volume-
  Cluster zone detector w/ first-test-only retests, volume-based TP
  target + low-volume-area SL w/ ADR-width guard, wick-based
  Unfinished Business proxy (explicitly NOT true footprint data).
  H45-H47. True footprint concepts (Imbalances, Big Limit Orders,
  Trades Filter) require Bid/Ask-split + per-trade size data we don't
  have -- not built, flagged in the playbook.
- indicators/hougaard_4bar_fractal_engine.pine (voice #15, Tom
  Hougaard): 4-Bar Fractal (close beats prior bar's AND bar-3-back's
  high/low -- simplest signal in the repo), 3-Bar Swing trend state,
  89-period HTF MA bias, divergence-as-continuation tag (mid-trend
  divergence read as continuation, NOT reversal -- an unresolved
  tension against every other divergence idea already in the repo).
  H48-H50.
- indicators/gann_square_of_nine_engine.pine (voice #16, Gann Square
  of Nine / TradingFives + W.D. Gann's own 1953 appendix note): major-
  pivot-anchored Roadmap Chart (horizontal rotation levels via
  (SQRT(N)+factor)^2, vertical time grid at round(sqrt(3-digit anchor
  price)) bars, 3-line diagonal channel with 2-consecutive-close
  breach alert), price/time squaring detector at confirmed swing
  pivots (degree-conversion formula credited to Carl Futia), Gann's
  own squares-1-to-19 bar-count watchlist. H51-H55. LOW-MEDIUM
  credibility (Gann's own track record is unverified folklore; the
  math itself is real and independently sourced). Biggest open
  question: the source's 3-digit price-normalization convention was
  built for equity indices, never validated on a 4-digit commodity
  price or anything close to a 5m timeframe -- toggle exists to
  disable, flagged untested rather than assumed to transfer. Master-
  144 numerology (Master Numbers 3/5/7/9/12, Biblical references) from
  Gann's own appendix explicitly NOT built -- no falsifiable trigger,
  preserved verbatim in trader_playbooks/gann_square_of_nine.md per
  standing rule.
  v2 (2026-07-20, "The W.D. Gann Master Commodities Course" -- Gann's
  own original grain/cotton/egg/soybean courses, 16,230 lines, read in
  full; SAME voice, extended in place): true Gann Angle fan (1x1/2x1/
  4x1/8x1 + weak-side mirrors) from the shared major-pivot anchor,
  ATR-scaled 1x1 rate (our own convention, source is explicitly
  discretionary about scale), angle-position trend-strength readout,
  "death angle" (1x1) break alert; Signal Day single-bar reversal tag
  (new N-bar extreme closing in the weak half of its range, no
  confirmation bar -- an explicit exception to this project's usual
  confirmation-before-entry default, kept as its own separate signal
  rather than folded in); a second, source-distinct minor time-rule
  bar-count watchlist (7/10/14/20/21/28/30/45/49/63/66/70/84/90) tied
  to the most recent swing pivot rather than the major anchor. H62-H64.
  Large amounts of course material deliberately NOT built (29+ numbered
  trading/pyramiding rules -- corroborates the existing swing/
  structure-break family rather than adding new code, since the
  numeric thresholds are 1940s-50s commodity-dollar-specific; decades
  of seasonal/anniversary time cycles -- explicitly agricultural,
  no analogue for a non-seasonal 24/7 metal; Hexagon Chart, Master
  12/144 squares, letter-count-modulus squares -- genuinely new
  geometry but past this register's falsifiability bar without a
  clearer trigger; astrological forecasting content -- out of scope
  regardless of source credibility). Full writeup in
  trader_playbooks/gann_square_of_nine.md section 11.
- indicators/intermarket_lag_engine.pine (voice #17, "The Big Secret
  of Intermarket Trading," anonymous lead-gen PDF): rolling-
  correlation-gated (ta.correlation, default |corr|>=0.5/100 bars)
  ATR-normalized catch-up-gap detector vs. a reference asset (default
  DXY, inverse). H65. LOW credibility source (explicit "100%
  profitable"/"100% winning trades" marketing language, zero track
  record, every example a hindsight-annotated screenshot with no
  actual specified trigger) -- the correlation gate and ATR
  normalization are OUR OWN addition, not in the source, since the
  source gives no falsifiable rule at all, only retrospective
  chart-boxing. Source's specific claimed lag durations (1-20h across
  different pairs) explicitly NOT hard-coded -- asserted from a
  handful of screenshots, not measured.
- indicators/quarters_theory_price_engine.pine (voice #18, Ilian
  Yotov's "The Quarters Theory," two AllThingsForex webinar
  transcripts): static price grid (large/small quarter levels via
  modulo arithmetic on absolute price, no swing/pivot anchor at all --
  "successful completion" = within one small-quarter width of the
  target), major-range-transition confirm/fail tracking, and a
  separate Trend Wave cycle counter (Reversal Trigger / Progressive /
  Conclusive / Consecutive wave labeling, wave-failure flag, the
  100%-retracement-becomes-a-new-reversal-trigger rule). H66-H67.
  LOW-MEDIUM credibility (named published author, zero backtested
  stats offered). **NAMING COLLISION WARNING**: completely unrelated
  to quarterly_theory_engine.pine (voice #4, Trader Daye/ICT lineage,
  TIME-based) despite the near-identical name -- this one is purely
  PRICE-based, no session/time component at all. Gold scale ($100
  major handle) is our own convention, untested -- every source
  example is a G7 FX pair. **v2 (2026-07-20, corrected author name
  from a fabricated "Ilan Levy-Mayer" to the real Ilian Yotov after
  the book's official Glossary of Terms was supplied)**: added Half
  Point of a Large Quarter grid lines (the midpoint of each $25 large
  quarter, distinct from the Major Half Point), the 3-Day Rule
  exhaustion timer (`sigExhausted` -- bar-count budget to reach a
  target large quarter, our own translation of the source's "3 FX
  days," untested), and a Large Quarter Corrections counter
  (`sigLQC` -- overbought/oversold flag after 3+ consecutive
  same-direction large-quarter completions). H68.
- indicators/kama_key_level_signal_engine.pine (NEW, 2026-07-20 --
  not a trader-school voice, built from two user-supplied Pine
  snippets rather than a book/transcript): plain KAMA (Kaufman
  Adaptive Moving Average, classical indicator not previously in this
  repo) vs. a level-damped KAMA variant ("KL Adaptive MA," adaptive
  smoothing constant multiplied by a proximity factor that shrinks
  toward 0 near an HTF key level) -- NEW signal, not in either source:
  buy/sell fires only when the plain KAMA crosses the level-damped
  KAMA AND that cross happens within proximity of an actual key level
  (daily/weekly open, PDH/PDL, PWH/PWL, Monday range, Asia/London/NY
  session range -- level computation reused from "Key Levels
  SpacemanBTC IDWM V13.1" by @sbtnc, only the non-repainting level
  math, not the original's 500+ line drawing/merge display layer).
  Suggested stop (beyond the triggering level) and target (ATR
  multiple) plotted for reference, informational only -- indicator,
  not a strategy() wrapper, no executed orders. H69. UNTESTED, brand
  new construct, no backtest -- per the 2026-07-20 standing rule nothing
  here is "proven" or "flagship" until backtested on a real sample.
- indicators/hima_reddy_gann_engine.pine (voice #19, Hima Reddy's "The
  Trading Methodologies of W.D. Gann," 2013 -- DIFFERENT voice from
  gann_square_of_nine_engine.pine/voice #16, Gann's own Square-of-Nine
  material, zero overlap): auto-detected swing eighths retracement
  grid (0/12.5/25/37.5/50/62.5/75/87.5/100%) with a tolerance-zone band
  around each level (our own convention, source only describes single
  lines), RSI with the SAME eighths geometry applied to its own swings
  (the book's RSI-applied-retracement variant) as a confluence gate,
  50%-retracement buy/sell signal (Buying/Selling Point #7), 2-bar
  test-failure detector, double/triple top-bottom break signal,
  time-exceedance confluence flag (Points #4/#5), trendline + parallel
  channel (anchored to the trendline's origin bar's OPPOSITE extreme,
  not a second touch), 2-bar trailing-stop reference (the book's most
  concrete exit rule), multi-timeframe RSI status table. H70-H72.
  MEDIUM credibility. **CONFIRMED CORRECTION**: the "Gann Box" BUY
  ZONE/SELL ZONE styling from the triggering Telegram screenshots
  (t.me/Wdgann sandipTradingViewindicators) is NOT sourced from this
  book -- full read confirms the term never appears and the book never
  describes a rectangular geometric price-time grid; that styling is a
  third-party proprietary layer (same low-credibility marketing
  profile as voice #17), not replicated here. This engine's zone/RSI-
  table visual language is built from the book's real documented
  mechanics instead. UNTESTED, brand new construct, no backtest.

=== SOURCE VERIFICATION AUDIT (2026-07-22) ===
User flagged a concern that earlier extraction passes may have dropped
or misrepresented details from the source PDFs/transcripts. Ran a real
second-read audit: for every source file still held in this session's
upload storage, an independent reviewing pass (no access to the
original extraction's reasoning) re-read the FULL source and diffed it
against the corresponding playbook.md.

10 sources audited (voices #4, #12, #13, #14, #15, #16, #17, #18, #19,
Candlestick Playbook). Result: zero fabricated facts found in any of
the 10. Findings were overwhelmingly omissions (concrete numbers,
named sub-concepts, worked examples that didn't make it into the
distilled version), not wrong facts. Two exceptions worth flagging
here specifically:
- **#17 Intermarket Lag**: one real numeric error — two distinct lag
  figures (~3h JPY->NASDAQ100, ~1h JPY->crude oil) had been merged
  into an imprecise "1-3h" range. Fixed.
- **#19 Hima Reddy Gann — ACTION NEEDED**: the source explicitly states
  its 2-bar test-failure pattern is a trade-MANAGEMENT tool for an
  already-open position, "not a signal meant to be targeted for market
  entry." The built engine (hima_reddy_gann_engine.pine) currently
  fires it as a bidirectional entry signal, and the Top/Bottom engine's
  `useTestFail` toggle reuses the same mechanic as an entry trigger.
  This should be reviewed/reconciled before further tuning either
  engine on this signal.

All fixes landed as dated addenda in the relevant playbook.md files
(same versioned-addendum pattern already used for Quarterly Theory's
v2-v8 passes) — nothing was silently overwritten. None of the fixes
have been ported into the .pine engines yet.

11 voices (#1 PBD, #2 Valentini/orderflow, #3 Kurisko, #5 Roppel, #6
Ario, #7 Dave, #8 Steve/MMM4x, #9 Renko/HA, #10 Wendell, #11 FX Master
Pattern) have NO retained source file in this session's storage — they
were pasted as chat text in earlier sessions and the raw text isn't
recoverable now. These could not be re-diffed against original wording;
only internal consistency was checkable. If a real re-audit of these is
wanted, the user needs to re-supply the original material.

Full audit findings, source-file inventory (filenames/sizes/authors),
and this log are also published as an artifact/downloadable HTML
report ("Trade Cartel — Source Dossier").

=== SOURCE VERIFICATION AUDIT, WAVE 2 — the 11 "unauditable" voices (2026-07-22) ===
User asked for the remaining 11 voices to be covered too and for
everything to be permanently stored. Recovered the actual raw pasted
transcripts for all 11 from this session's own log file (the container's
uploads folder is ephemeral, but the underlying session transcript
retains every message verbatim even across multiple auto-compactions) —
23 large pasted-text messages found, 2 exact duplicates, 21 unique
transcripts recovered and saved permanently to
`trader_playbooks/sources/raw_transcripts/` (see its README for the
file->voice mapping). Every original PDF/txt upload from wave 1 was also
copied into `trader_playbooks/sources/` for the same reason — session
uploads do not survive container reclamation, playbooks do.

Ran the same independent second-read audit as wave 1 on all 11: #1 PBD,
#2 Valentini + orderflow companion, #3 Kurisko, #5 Roppel, #6 Ario, #7
Dave, #8 Steve/MMM4x, #9 Renko/HA ABC, #10 Wendell, #11 FX Master
Pattern — plus incidental re-confirmation of #4 Daye and #18 Yotov via
duplicate transcripts. Combined with wave 1, **all 21 voices are now
audited against original source material.**

Two real fabrications/errors found and corrected (not just omissions):
- **#10 Wendell**: playbook stated "7-9 candles at the base" as Wendell's
  basing-candle-count threshold. The source only gives ONE worked
  example, an 8-day base counted live on the chart as 7 days — there is
  no "9" anywhere in the transcript. The range was invented by an
  earlier extraction pass. Corrected in wendell_supply_demand.md to "7
  (the one worked example)."
- **#7 Dave**: playbook's own header claimed "$700->$89k in 3 weeks,
  publicly verified." None of the three recovered transcript segments
  (one continuous session) contain this claim — they instead describe
  losing down to $600 with a stated goal of rebuilding to $20k over 4
  months. The $89k figure likely came from a video title/description
  that was never actually pasted into this project. Header corrected to
  flag this as UNVERIFIED against the actual source pending re-check.

Roughly 60 further omitted details (concrete numbers, named setups,
worked examples, book/influence lists, risk-sizing schedules) were
added back as dated addenda across all 11 files — see each playbook's
own "Audit pass" section for specifics. Highlights: Valentini's actual
named setup ("AAA"/"Triple A") and P-shape pattern were missing
entirely; Roppel's CANSLIM-lineage answer and full book/influence list
were dropped; Steve/MMM4x's "weekly net change allowance" dealer-cap
claim (a falsifiable Friday-mean-reversion mechanism) was never
captured at all.

One source explicitly found and NOT built: "Forex James" (2 transcripts,
checked against Steve/MMM4x on a same-voice theory, ruled out — zero
shared mechanics). Generic market-maker/broker content with no
repeatable counting system. Archived per the never-discard rule,
deliberately not given a voice number or engine — logged here so it's
findable later rather than silently dropped.

Zero fabricated NEW facts found in any of the 11 (same result as wave
1) beyond the two corrections above, which were pre-existing errors
from before this audit, not something this pass introduced. Nothing
ported to engines yet.
