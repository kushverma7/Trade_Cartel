# PLAYBOOK v2026-07-19
# Living document per COGNITIVE_ARCHITECTURE.md Mechanism 2.
# Review after every ~20 analyzed trades. Evolve, don't hoard.

=== SCALP SETUPS ===

1. **Session Trendline Breakout** (flagship)
   - Conditions: XAUUSD 5m, OLS trendline (lookback 22), London 03:00-05:00
     or NY-open 08:30-11:00 NY time only
   - Entry: close breaks optimized trendline; Stop: 2x ATR(14); Target: 4x ATR
   - Evidence: PF 3.656 backtest. Files: strategies/trendline_breakout_fixed.pine
   - Sizing: A-setup. Confluence upgrade: aligned tier-A candle pattern.

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
- Core: proven trendline breakout (22) + optional H7 full-body confirm
- Confluence vote 0-12: session [B1] +2, out-of-balance regime [PBD] +2,
  tier-A candle [Nison] +2, aggression [Valentini] +2, VWAP side (not
  beyond 2SD) +2, fresh level [H8] +2
- Grades: 8+ = A+, 5-7 = B, below = suppressed (grey x with tooltip)
- Hard vetoes: opposing tier-A candle, recent CVD divergence against,
  8:25-8:45 ET news window, over-rejected level
- Dashboard shows all layer states live; alerts per grade

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
  material. STANDING RULE (2026-07-20): one engine file per voice/
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
  Cup & Handle and Diamond Top/Bottom explicitly not built (no robust
  mechanical trigger without curve-fitting noise).
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
