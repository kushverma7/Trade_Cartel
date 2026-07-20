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
