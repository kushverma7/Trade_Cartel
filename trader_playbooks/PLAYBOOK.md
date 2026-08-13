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

=== OMNIBUS FOUR-MODEL ENGINE — ITERATION LOG (2026-07-22) ===
strategies/omnibus_four_model_engine.pine. Built to the OMNIBUS
protocol's A/B/C/D architecture with per-model tester-derived metrics.

**Iteration 1 (zero trades):** signal labels drew but the tester
recorded nothing -> BUG-012: Pine v6 defaults strategy margin to 100%;
risk-percent sizing on tight gold stops requested multi-million-dollar
notional and every order was silently skipped. Fixed with margin 5%
(20:1) + leverage-capped qty in BOTH this engine and the AMDM
strategy (shared sizing chassis). Lesson registered: "labels but no
trades = execution rejection, not signal logic."

**Iteration 2 (first real dataset, Jun 1 - Jul 27 2026, XAUUSD 5m
OANDA, 100K):** 298 trades (~150/month), WR 40.6%, PF 0.843, -13.01%,
max DD 16.01%. Profit Engine: breakeven WR for the 1R/2R split exit is
exactly 40% -- system is a pre-cost coin flip being ground down by
~300 trades of commission/slippage (pre-mortem scenario 3). Visible
tape: Model C (FVG) is the churn driver (dense C-L/C-S clusters,
largest visible losses all C), consistent with its 0.2xATR min gap
being spread-sized on 5m gold (~$0.30-0.50). ONE change: C min gap
0.2 -> 0.5 ATR (input-only, user can flip on-chart). Expected: trade
count down materially, C quality up, cost drag down. Per-model
dashboard numbers requested from the user to drive iteration 3
kill/fix decisions with real per-model splits instead of tape reads.

=== KEY-LEVEL STRATEGY LINE — ITERATION LOG (2026-07-27) ===
User parked OMNIBUS iteration for a key-level-centric plan. Three
tests, one pattern:
- key_to_key_strategy.pine (level-touch entries): 245 trades, WR
  26.1%, PF 0.886, -10.87%, DD 23.15%.
- trendline_key_level_strategy.pine v1 (OLS trendline lookback-5
  entries, key-level exits, stop-and-reverse, all hours): 382 trades,
  WR 40.8%, PF 0.882, -11.72%, DD 20.68%.
- (OMNIBUS four-model for reference: 298 trades, PF 0.843.)

DIAGNOSIS (three minds + voice register): PF pinned at 0.84-0.89
across three different entry architectures = the entry variant is not
the problem. 250-380 trades/2mo in BOTH directions at ALL hours on 5m
gold is noise trading; costs grind the coin flip down. The register's
strongest un-applied confluence: HTF TREND GATE -- Hougaard #15's
89-period HTF MA bias (HIGH credibility, audited), Valentini #2
momentum-join (HIGH, verified), Roppel #5 trend-following, plus
Dave/FX-Master/Steve counter-trend warnings. The v1 engine
stop-and-reversed every flip: half of all trades were counter-trend
by construction.

ITERATION 2 (one logic change + display fix): added HTF trend bias
gate (longs only above / shorts only below the 1H EMA-89) to
trendline_key_level_strategy.pine. Expected: counter-trend bleed
removed, PF up.

ITERATION 2 RESULT — FAILED, REVERTED: 301 trades, WR 39.2%,
PF 0.819 (worse than v1's 0.882), -13.34%, DD 15.69%. Per the OMNIBUS
verify rule (metrics worsened -> revert), useTrendBias default is
back to OFF, kept as an A/B toggle labeled with the result. Register
note: the Hougaard-89/momentum-join bias thesis did NOT transfer to
this 5m trendline-flip engine on this window -- second time a
"logical" trend filter failed empirically here (ADX veto on the
topbottom engine was the first). Pattern worth a belief entry if a
third instance appears.

ITERATION 3 (display only, no logic change): the level display was
also wrong twice -- plot() series lines instead of the SpacemanBTC
look the user asked for. Replaced the whole level display with a
PORT OF THE ACTUAL SPACEMAN DRAWING ENGINE: anchored line.new from
each level's own origin time to right of the last bar, right-edge
text labels, and the original's f_LevelMerge (same-price levels share
one combined label, e.g. "Weekly Open / Daily Open"). All 28 tracked
levels drawn: D/W/M opens + prev H/L/mids, Q/Y opens, Monday range,
prev 4H, Asia/London/NY H/L/O. Re-test pending.

HONEST STATUS after 4 architectures x 5 tests: every variant lands
PF 0.82-0.89 on this same Jun-Jul window. No entry logic tried so far
has a pre-cost edge on 5m gold stop-and-reverse signals. The next
serious moves are structural, not parameter nudges: (a) test on 15m
where noise/cost ratio improves, (b) cut trade count hard (session +
cooldown + room all together), or (c) accept this signal family is
edgeless and return to the topbottom engine lineage (the only one
that ever crossed PF 1.0 live).

=== AMDM CONFLUENCE STRATEGY ADOPTED (2026-07-22) ===
User uploaded a complete external synthesis package and adopted the
**Auction-Momentum Dual Model (AMDM)** as the project's standing
strategy lens. Full spec: `trader_playbooks/AMDM_confluence_strategy.md`
(includes an audit note flagging unverified academic citations —
see MEMORY.md's "AMDM Strategy Lens Active" entry for the full context).

STATUS: SYNTHESIZED / UNTESTED. Two-model regime-switched system:
- **Model 1 (Momentum-Join)**: trades outside prior value area / high
  ATR, BOS + volume + CVD confirmation. Draws on Valentini #2, Hougaard
  #15, Wendell #10.
- **Model 2 (Mean-Reversion)**: trades inside prior value area / low
  ATR, sweep + rejection + volume-exhaustion at VAH/VAL. Draws on PBD
  #1, Trader Dale #14, Wendell #10, and this repo's own topbottom
  engine (the only engine here with a small-sample positive live-test
  result, and the direct model for Model 2's mechanics).
- Model selection via a real-time decision tree keyed on ATR, position
  relative to value area, news calendar, and DXY correlation.
- 0-12 confluence scoring (macro/intermarket/HTF structure/LTF
  entry/RR/session timing) maps to position size, consistent with
  COGNITIVE_ARCHITECTURE.md's existing scoring convention.

Engine: `indicators/amdm_confluence_engine.pine` (visual/chart version)
and `strategies/amdm_confluence_strategy.pine` (Strategy Tester version
-- same detection logic wired into strategy.entry/exit with risk-percent
position sizing off the 0-12 confluence score, daily loss-limit/trade-
count circuit breakers, and a time-stop flatten). See both files'
headers for what's built vs. simplified (e.g. no true footprint/delta
data on this project's feed -- CVD confirmation uses the existing
candle-direction proxy, not real bid/ask delta; the strategy version
also documents one known gap -- no breakeven-stop-move after TP1,
flagged rather than shipped half-correct).

Next steps per the strategy's own Part IV backtest plan: minimum 100
manually-tracked trades across 3+ months before any status upgrade past
SYNTHESIZED/UNTESTED.

**Live-test result #1 (2026-07-22): zero trades/signals.** Root-cause
diagnosis (real bugs, not parameter tuning):
1. Model 2's volume gate was self-contradictory -- required volume
   simultaneously >120% AND <100% of the 20-bar average on the SAME
   candle, which can never be true, so Model 2 could never fire at
   all. Fixed by splitting across two bars (sweep+high-vol+rejection
   on bar[1], reclaim+exhaustion-vol on the signal bar), which is what
   the source doc's own "sweep candle... reclaim candle" language
   actually describes. Stop now references the sweep bar's wick.
2. Model 1's stop-distance check hard-REJECTED any BOS whose swing
   pivot sat further than 1.2x ATR away instead of clamping the stop
   -- but that's the normal state right after a real breakout, so most
   genuine Model 1 setups were silently vetoed. Now clamps into
   [min,max] x ATR (same convention as reversal_sniper_strategy.pine).
3. The FX-pip->dollar ATR regime conversion was a guessed constant;
   replaced with direct dollar thresholds + a live H1-ATR dashboard
   readout so the user can tune the regime split to the chart's actual
   volatility instead of trusting a multiplier picked blind.
4. Strategy version only: the confluence score was stacking a second
   silent entry gate on top of the model conditions; now scales size
   (0.5-1.5%) instead of blocking, with minScoreToTrade defaulted to 0
   during testing (raise it back once trades are confirmed flowing).
Both files also gained per-gate diagnostic dashboard rows so any future
"no signals" report shows WHICH gate is blocking, on-chart. Re-test
pending.

**Round 2 (2026-07-22, external code review supplied by user).** Four
claims assessed per the receiving-code-review discipline (verify, don't
blindly agree):
1. CONFIRMED -- pivot-based BOS was structurally mute: ta.pivothigh
   (10,10) confirms the swing level 10 bars after it forms, by which
   time price is already past it, so ta.crossover almost never fired.
   Replaced with a real-time Donchian-style breakout (close crossing
   the prior N-bar high/low, [1]-offset, non-repainting). This was the
   dominant remaining cause of Model 1 silence.
2. CONFIRMED (the moving-reference half) -- Model 2's reclaim compared
   against the CURRENT bar's recalculated rolling value area, which
   shifts with the very move being judged. Now frozen to the sweep
   bar's level (val[1]/vah[1]).
3. PARTIALLY ACCEPTED -- the CVD proxy was never claimed to be real
   CVD (documented limitation), but the redundancy critique is right:
   it mostly double-counts the BOS candle's own direction. Defaulted
   OFF, kept as an optional stricter toggle.
4. REJECTED ON THE MATH, noted on the substance -- reviewer claimed
   288x20 = 5,760 ops/bar; the loops are sequential, not nested
   (~300 ops/bar), same pattern as trader_dale_volume_profile_engine
   at no observed cost. No change made; logged so the claim isn't
   re-litigated later.
Re-test pending after round 2.

=== REGISTER-USAGE AUDIT + MULTI-VOICE ENGINE (2026-07-27) ===
User asked, fairly: "how are you using all the data I fed you?"
Ran the audit instead of answering from memory. Result was damning:
- 72 hypotheses on file; only 8 (H1 H4 H7 H8 H10 H20 H22 H24) ever
  referenced in ANY .pine; ZERO in the five engines built this session.
- 12 voices "cited" in this session's engine headers -- all in COMMENTS
  justifying design choices, none as coded mechanics.
- 37 indicator engines exist encoding the voices' mechanics; essentially
  none had been combined into a strategy.
Conclusion: the register was being name-dropped, not mined. Every
recent engine implemented ~5 generic mechanics that could have been
written without the user's data at all.

FIX: strategies/multivoice_confluence_engine.pine. Each voice with a
mechanically codeable hypothesis casts an INDEPENDENT VOTE (+1/-1/0);
a trade requires N-of-M agreement. This is the register's own
corroboration-tally logic executed in code, and COGNITIVE_ARCHITECTURE's
conviction score actually implemented. 20 voters wired:
  V1 H48 Hougaard 4-bar fractal (HIGH, 2x weight)
  V2 H22 three-failed-visit count
  V3 H71 Hima 2-bar test-failure (as ONE vote, respecting the source's
         "not a standalone entry" caveat found in the earlier audit)
  V4 H63 Gann Signal Day
  V5 H37 role inversion (SBR/RBS)
  V6 H36 IDM-gated BOS
  V7 H44 liquidity grab vs BOS geometry
  V8 H46 HVN/volume cluster
  V9 H30 Wendell fresh zone + departure (HIGH, 2x)
  V10 H49 mid-trend divergence = continuation (HIGH, 2x)
  V11 H16 volume tsunami (HIGH, 2x)
  V12 H35 EMA stack bunching
  V13 H23 ADR thirds
  V14 H5 momentum-join (HIGH, 2x)
  V15 H17 leg-size regime
  V16 H70 eighths retracement
  V17 H8 rejection-count weakening
  V18 Nison tier-A candle
  V19 Spaceman key-level sweep
  V20 H10 session structure
Every voter is individually toggleable, so a failing voice can be A/B'd
out and the register updated with real evidence -- which is what the
BELIEF_REGISTER contradiction tallies were always supposed to consume.
Live vote table on chart shows which voices agree in real time.
Declared-not-faked: H14 SMT needs a correlated symbol; H45/H47 need
true volume profile; H51-H62 Gann geometry needs non-mechanical anchor
selection. STATUS: UNTESTED.

=== *** FIRST PROFITABLE RESULT — MULTI-VOICE ENGINE (2026-07-28) *** ===
strategies/multivoice_confluence_engine.pine, XAUUSD **15m** OANDA,
Feb 2 - Jul 28 2026, 10K account, default minScore=6:
  Trades 521 | Win rate 44.15% (230/521) | PF 1.093
  Net +$1,525.21 (+15.25%) | Max DD $1,353.65 (11.90%)

CONTEXT: this is the FIRST engine in this repo to finish profitable,
and on the largest sample ever run here (~6 months / 521 trades vs the
~2 month / 117-380 trade runs behind every prior number). Prior best
was PF 0.886. The six preceding engines all landed PF 0.82-0.89.

WHAT CHANGED (two variables, stated honestly):
  1. Signal logic: 20 independent voice-votes requiring N-of-M
     agreement, instead of one hand-picked entry mechanic.
  2. Timeframe: 15m instead of 5m.
Both moved together, so the win is not yet cleanly attributable. The
15m move was itself one of the three structural options logged after
the PF 0.82-0.89 plateau, so both changes were principled -- but a
5m re-run of THIS engine is the clean way to separate them.

MATH CHECK: with the 50%@1R / 50%@2R split, avg win ~1.5R, so
breakeven WR = 1/(1+1.5) = 40%. Observed 44.15% sits above it, which
is consistent with PF 1.093 -- the result is internally coherent, not
a reporting artifact.

STATUS: still NOT "proven". PF 1.093 is thin, one symbol, one window,
in-sample. Per the standing rule it stays a CANDIDATE until it holds
out-of-sample. But it is the first candidate with real evidence behind
it, and the first data point supporting the register's core premise:
corroboration across independent voices beats any single voice.

NEXT ITERATION (the decisive test): raise minScore 6 -> 8 -> 10, one
input, nothing else touched. If the voting logic carries real signal,
PF should RISE as conviction rises (fewer, better trades). If PF is
flat or falls as minScore climbs, the votes are noise that happens to
average out, and the edge is coming from somewhere else. This single
test validates or kills the multi-voice premise.

---

## KEY LEVELS MADE MANDATORY — VERBATIM PORT (2026-07-28)

User directive: *"please include the indicator i will give you. and add
it into anything that you build and make sure it also displays the levels
as it is in the indicator."*

**What changed.** The SpacemanBTC IDWM Key Levels V13.1 source the user
supplied is now ported verbatim to
`trader_playbooks/skills/key_levels_module.pine` and embedded in all six
strategies: multivoice_confluence_engine, confluence_sniper,
trendline_key_level, key_to_key, omnibus_four_model, amdm_confluence.
`trendline_key_level` and `confluence_sniper` had hand-rolled key-level
blocks — those were deleted and replaced wholesale, not merged.

**Why verbatim and not a rewrite.** Logged as BUG-013. Three separate
reimplementations were rejected by the user in three consecutive
messages. Each failed for a different reason (`plot()` series geometry;
create-early/mutate-later not rendering in a strategy; a `timenow`
projection that pushed labels off-screen). The supplied source had
already solved all three. Three rejections on the same point meant the
APPROACH was wrong, not the implementation.

**Port deltas — the only five changes made to the source:**
1. `//@version=5` → host's `//@version=6`.
2. `indicator(...)` declaration dropped; host `strategy(...)` carries
   `overlay=true`, `max_lines_count=500`, `max_labels_count=500`.
3. Input group titles prefixed `KL ` so they never collide with a host's
   own groups.
4. Added `klPrices[]` / `klNames[]` export so trade logic can consume the
   exact levels the chart draws. Drawing behaviour untouched.
5. `London/US/Asia` made explicitly `bool` via `not na(time(...))` —
   the source relied on v5's int→bool coercion. Provably identical.

Defaults, colours, label text, merge behaviour, line geometry and the
source's own quirks (US labels created with London text then corrected;
`weeklyl_line` created at the wrong y then corrected; `monthlyh_line`
x1 taken from `monthlyl_time`; yearly H/L using current-year values) are
all preserved deliberately — the user's chart looks the way it does
because of them.

**Deliberately NOT changed: any trade logic.** The module is display +
export only. That keeps the pending conviction test clean.

**Verification done:** static duplicate-declaration and function-name
collision scan across all six hosts — zero collisions. Dead inputs left
behind by the removed blocks (`showLevels` in two files) were deleted.
**Not yet verified:** the visual on the user's chart, and that all six
compile in the TradingView editor. Those need the user.

**NEXT ITERATION IS UNCHANGED.** Still the decisive test: on
multivoice_confluence_engine, raise `Min Conviction Score To Trade`
6 → 8 → 10, nothing else touched, and compare against the baseline
(521 trades / WR 44.15% / PF 1.093 / +15.25% / DD 11.90%). Rising PF
validates H73; flat or falling PF kills it and points the edge at the
5m→15m timeframe change instead.

---

## ITERATION: KEY LEVELS BECOME LOAD-BEARING (2026-07-28)

User: *"make sure you are using it as a confluence for the entry and exit
from key level to key level and also use other confluences for accuracy.
take time frame support also if that improves"*

Until now the Spaceman module only DREW. This iteration moves it above the
trade logic so `klPrices[]` is populated before any vote is cast, and wires
it into four places on `multivoice_confluence_engine.pine`:

| Where | Before | Now | Toggle (group ⑤) |
|---|---|---|---|
| V19 sweep+reclaim | 4 hand-picked levels (PDH/PDL/DO/WO) | full drawn level set (~20-36 levels) | `klFullSweep` ON |
| New V21 | — | break-and-retest of a real key level (H37 role inversion) | `vOn21` ON |
| TP1 / TP2 | fixed 1R / 2R | next key level >= minTP1R away, then the one beyond | `useKLTargets` ON |
| Stop | adverse wick + ATR buffer | further of (adverse wick, beyond the defended key level) | `useKLStops` ON |

Room handling follows BUG-009: if no key level sits in range, the fixed R
targets take over rather than the trade being rejected. A hard
"no level = no trade" variant exists as `klRoomGate`, default OFF.

**Multi-timeframe shipped OFF on purpose.** Group ⑥ adds V22 (HTF trend
vote) and `htfGate` (hard veto). Both default false. Reason stated in the
code: this repo has now had TWO "logical" higher-timeframe/trend filters
make results WORSE (the ADX veto, and the HTF bias MA that took the
trendline engine from PF 0.882 to 0.819). The user asked for timeframe
support "if that improves" — so it ships as a measurable A/B toggle, not
as an assumed win. It is not claimed to help until a run says it does.

**Confound warning, stated up front.** This iteration changes FOUR things
at once (V19 scope, V21, TP logic, SL logic). That breaks the OMNIBUS
one-change rule, deliberately, because the user asked for the whole
level-to-level architecture rather than a single tweak. The consequence is
real: if PF moves, we will not know which of the four moved it. Every one
is individually toggleable specifically so the attribution can be
recovered afterwards, one switch at a time.

### Test order (do these in sequence, one switch per run)
Baseline to beat: **521 trades / WR 44.15% / PF 1.093 / +15.25% / DD 11.90%**
(XAUUSD 15m, Feb 2 - Jul 28 2026, minScore 6).

1. **Everything as shipped** (group ⑤ all ON, group ⑥ OFF) vs baseline.
   -> tells you whether level-to-level beats fixed-R overall.
2. `useKLTargets` OFF only. -> isolates the exit change.
3. `klFullSweep` OFF only. -> isolates the entry-scope change.
4. `vOn21` OFF only. -> isolates the new voter.
5. `useKLStops` OFF only. -> isolates the stop change.
6. Then the conviction test that is still outstanding: minScore 6 -> 8 -> 10.
7. Only then MTF: `vOn22` ON, then `htfGate` ON, each alone.

If step 1 is worse than baseline, revert to baseline settings before
tuning anything else -- that is the loop rule and it has already saved
this repo once (the HTF bias reversion).

STATUS: shipped, statically validated (no duplicate identifiers, no
use-before-declare, no nested function declarations, no ta.* in a
dynamically-conditional branch). NOT yet run by the user. No performance
claim is made until it is.

### STEP 01 RESULT — LEVEL-TO-LEVEL AS SHIPPED: REJECTED (2026-07-28)

XAUUSD 15m, Feb 2 – Jul 28 2026, minScore 6, group ⑤ all ON, group ⑥ OFF.

| Metric | Baseline | Level-to-level | Delta |
|---|---|---|---|
| Trades | 521 | 461 | −60 (−11%) |
| Win rate | 44.15% | **34.06%** | **−10.09 pts** |
| Profit factor | 1.093 | **0.892** | −0.20 |
| Net | +15.25% | **−14.19%** | −29.4 pts |
| Max DD | 11.90% | **25.47%** | +13.6 pts |

**Reverted. Baseline settings stand as the current best configuration.**

#### Diagnosis (three minds)

The signature is specific and it is NOT an entry problem. Trade count fell
only 11%, so the voters are still firing on roughly the same bars. What
collapsed is the win rate — 10 full points, from comfortably above the
40% breakeven for a 50%@1R / 50%@2R split to well below it. When entries
hold steady and win rate craters, the fault is in the EXIT geometry.

**Prime suspect: `useKLStops`.** The stop was set to the further of the
adverse wick or beyond the nearest key level. On 15m gold the drawn set is
dominated by D/W/M/Q/Y levels, which are far apart relative to a 15m ATR.
So `close − f_klBelow(close)` was routinely larger than `maxStopAtr`, and
the clamp pinned the stop at its 2.5×ATR ceiling on a large share of
trades — roughly double the baseline's typical wick-based stop.

**Second-order consequence, and this is the real damage:** TP1 is defined
as the next key level at least `minTP1R × rd` away. Doubling `rd` doubled
the minimum target distance too. The trade now needs ~2.5×ATR to reach
TP1 and ~5×ATR for the round trip, inside a 48-bar time stop. The 50%
scale-out at TP1 that was carrying the baseline's win rate mostly stopped
filling, while the wider stop kept getting hit. Wider stop AND further
target is the worst pairing available, and the two changes amplified each
other rather than being independent.

**Not yet exonerated:** `klFullSweep` and `vOn21` widen entry criteria and
could account for some of the 60 lost trades and some WR dilution. They
are lower suspects because the trade count barely moved.

#### What this does and does not prove

It does NOT falsify "trade key level to key level". It falsifies THIS
implementation of it, and names the mechanism: letting the level dictate
stop distance on a timeframe where the levels are far apart relative to
the bar range. A level-to-level exit only works if the level spacing is
commensurate with the timeframe's ATR. That is a testable statement and
it is the next thing worth checking.

#### Revised next runs (diagnosis-driven, replaces the old 02-05 order)

- **Run A — CONTROL, do this first.** All four group ⑤ toggles OFF, group
  ⑥ OFF, minScore 6. Must reproduce ≈521 / 44.15% / 1.093. If it does not,
  the refactor itself changed baseline behaviour and every other result in
  this section is meaningless. This run validates the toggle framework,
  not the strategy.
- **Run B — the suspect, alone.** `useKLStops` OFF, everything else in ⑤
  left ON. If PF recovers toward 1.09 this confirms the stop change as the
  cause and clears the targets.
- **Run C** — if B does not recover: `useKLTargets` OFF too, leaving only
  the entry-side changes (`klFullSweep`, `vOn21`) on.

Only after the culprit is isolated does the outstanding minScore 6→8→10
conviction test get run, and MTF after that.


---

## KEY LEVELS STRATEGY (SPACEMAN EDITION) — v1.0 RESULT VOIDED (2026-07-29)

User supplied a separate 30m engine reporting XAUUSD, Jan 2 2025 - Jul 29
2026: **22 trades / WR 63.64% / PF 1.783 / +7.70% / max DD 7.01%**.

**The 1.783 is not an edge. It is an order-rejection artifact.**

v1.0 declared no `margin_long`/`margin_short`, so Pine v6 defaulted both to
100%. Sizing was `qty = round(equity * risk% / slDist)` = `round(100/slDist)`.
On 30m gold slDist runs ~$6-37, giving qty 3-17 contracts = $12,000-$68,000
notional against $10,000 equity. Every one of those exceeds buying power and
TradingView skips them silently. The chart plots roughly four signals per
five days -- hundreds across the tested range -- yet only 22 filled. The 22
that filled are the ones that happened to size smallest, i.e. the
WIDEST-STOP trades. That is a biased subsample, and its profit factor
describes the rejection filter, not the strategy.

This is **BUG-012 for the second time**. The prevention written after the
first occurrence ("labels but no trades = execution rejection") did not
generalise, because this time there WERE trades -- just far too few. New
prevention: every engine now shows Signals / Filled / Fill rate on the
dashboard, so the gap is visible rather than inferred.

Three further defects found in the same read:
- **BUG-014** -- the TP1 tranche had `limit=` and no `stop=`, so 60% of
  every position was unprotected until the time stop. This is why largest
  loss ($639.14) is 3.3x largest profit ($194.84) on a 1.5R target.
- **BUG-015** -- `ta.lowest(low, 12)` includes the current bar, so
  "Break + Retest" never required a break.
- **BUG-016** -- `dayTrades` counted signals, not fills, so the daily cap
  was consumed by rejected orders.

**Statistical note, independent of all four bugs.** WR 63.64% on n=22 has a
95% confidence interval of roughly 41%-82%. Total PnL $769.65 against a
largest single loss of $639.14 means one more max-size loser removes 83% of
the gain. Even with perfect execution, 22 trades would not support a
conclusion.

### Shipped: v1.1
All four fixed. Level set, entry conditions, session filter, TP/SL geometry
and every default left untouched so the comparison isolates execution.
The mandatory Spaceman key-level module is embedded (display only; the
strategy trades its own `sigLevels[]` subset, deliberately renamed to avoid
colliding with the module's `klPrices[]`).

**Next run:** paste v1.1, change nothing, and read the dashboard's
**Fill rate** row BEFORE looking at PF. Below 90% and shown red means orders
are still being rejected and no performance number is meaningful yet. Once
fill rate is ~100%, report trade count / WR / PF / net / max DD -- and the
trade count is the number that decides whether v1.0's result was ever real.

---

## VOTER SCORECARD — answering "which combo" without guessing (2026-07-29)

User: *"based on everything you have i want you to work on a indicators
settings and find out which combo works the best."*

**The honest constraint first.** 22 voters is 4,194,304 subsets. That is not
answerable by proposing combos, and every combo I proposed by taste would be
another entry in RESULTS_LEDGER with no way to attribute the result. I also
have no market-data access from this container (no TradingView MCP in the
session; Yahoo, Binance and tradingview.com all fail outbound), so I cannot
run the sweep myself.

**So the engine was instrumented instead of guessed at.** At each entry the
agreement of every voice with the trade direction is recorded (+1 for, -1
against, 0 abstain). On close, the trade's P&L is attributed to both the
agreeing and the opposing group. One backtest now yields, for all 22 voices:

| Column | Meaning |
|---|---|
| N | closed trades the voice voted FOR (greyed below 30) |
| PF agree | profit factor of trades it backed |
| PF oppose | profit factor of trades it objected to |
| **EDGE** | **agree − oppose** |

**EDGE is the metric, not PF agree.** A voice that votes on nearly every
trade will show a PF close to the engine's overall PF and look fine. What
makes a voice useful is that outcomes are BETTER when it agrees than when it
objects. EDGE <= 0 means the voice carries no directional information, and
predicts that switching it off will not hurt -- a claim testable in one run.

Pure instrumentation: no entry, exit or sizing logic changed. `voteNow` is a
`var` array overwritten in place rather than rebuilt with `array.from` each
bar, so ~20,000 bars do not each allocate.

### Procedure (3 runs total)
1. Run as shipped: minScore 6, all voters on, **group ⑤ toggles OFF** (that
   configuration was reverted -- see the step-01 entry above). Read the
   scorecard at bottom-left.
2. Turn off every voice with EDGE <= 0. Re-run. If headline PF rises, the
   combo is measured rather than assumed.
3. Only THEN raise minScore. The outstanding 6 -> 8 -> 10 test is only
   meaningful once the voter set is clean; with fewer voices the useful
   threshold will not be 6.

Append every one of these to RESULTS_LEDGER.md with N, window and settings.

### Still outstanding, and better than all of the above
An offline sweep on exported bars, with a train/test split. If the user
exports XAUUSD 15m (right-click chart -> Export chart data -> CSV) I can run
the full subset search in Python and return settings that survived
out-of-sample. That is the only version of "best combo" that would earn a
VALID row in the ledger. The scorecard is the in-TradingView route to the
same place, and it is available now.

---

## KEY LEVELS v1.2 — LEVEL SCORECARD (2026-07-29)

User re-pasted the Key Levels (Spaceman Edition) source, in the context of
"find out which combo works best". Read as: run the settings search on THIS
engine rather than the multi-voice one.

**The pasted build was v1.0 — all four defects still present.** Optimising
settings on it would have tuned the order-rejection filter (22 fills out of
hundreds of signals, BUG-012) rather than the strategy. v1.2 therefore
carries the v1.1 fixes plus the instrumentation.

**Why instrumentation again rather than proposed combos.** The 15 level
toggles alone are 32,768 combinations, before entry mode (3), tolerance,
buffer, min/max SL, cooldown, vol filter, TP mode, TP1/TP2 R, TP1 %, min TP
distance, session windows and the four risk inputs. No hand-picked shortlist
through that space is evidence; it is preference wearing a number.

So each trade is now tagged at entry with the level TYPE it was taken at
(18 ids carried in a `sigIds` array parallel to `sigLevels`) and with which
trigger fired it. On close the P&L is attributed back. One run produces a
ranked table: N / WR / PF for all 18 level types, plus the same three for
Sweep+Reclaim vs Break+Retest measured on the same sample -- which settles
the Entry Mode dropdown with evidence instead of taste.

N < 20 renders grey. Same guard as the multi-voice scorecard, same reason:
a 22-trade PF of 1.783 already fooled this project once.

### Procedure
1. Turn ON every level, Entry Mode = Both, longest window the plan allows.
   **Read Fill rate FIRST.** Not ~100% means orders are still being
   rejected and no other number is meaningful.
2. Switch off every level with PF < 1.0 at N >= 20; set Entry Mode to the
   winning mode. Re-run.
3. Only then touch tolerances, stops, targets -- one at a time, each result
   appended to RESULTS_LEDGER.md with N and window.

**Known limit, stated up front:** a run under ~100 trades cannot rank 18
levels -- each gets a handful and the table is all grey. The rarer levels
(4H, London, NY ranges) may never reach a readable N on a short window. That
is a real constraint of the method, not a reason to read thin rows anyway.

Pure instrumentation beyond the v1.1 fixes: entry conditions, level set,
session filter, TP/SL geometry and all defaults unchanged.

---

## AU200 OPEN — FAMILY CLOSED ON EXITS, OPEN ON ENTRIES (2026-08-13)

**What was tested.** Everything the user asked for around the 10:00 Melbourne
candle and the daily open, at achievable fills only, cost included:

| family | result |
|--------|--------|
| User's AU200-BASE trailing version | PF 2.0-3.4 reported; **artifact** (BUG-036) |
| Same entries, 9 different honest exits | all negative, PF 0.31-0.66 |
| User-frozen one-bar fixed hold, 4 TFs | gross 0.78-1.12; net of cost all < 1.0 |
| 350-cell sweep (gap / opening range / daily-open / exits) | 0 of 350 clear the noise bar |

**Regime note.** The 2-point round-trip cost is the binding constraint at ~1
trade/day. Only 7 of 350 cells reach PF > 1.0 against ~175 expected by chance —
the cost, not the signal, is setting the outcome for this whole family.

**Status: exits CLOSED, entries OPEN.** Nine exit rules on fixed entries and a
full exit sweep inside the 350-cell grid all failed. Do not spend another
iteration on exits for this setup. The one live cell is **1H, one-bar hold**:
gross-positive in both windows, beats always-long by +0.58/trade, roughly 2
points short of tradeable.

**What to do next, in order.**
1. Measure the real spread from Dukascopy bid/ask. If it is 1 point rather than
   2, several cells change sign and the 350-cell sweep must be re-run.
2. Only then, search entry filters on the 1H cell. Target: call the side of the
   10:00->11:00 hour above 57% out of sample.
3. Anything that reports a win rate above 90%, a drawdown under 1% of equity, or
   a straight equity curve gets its fills audited before its PF is read.
