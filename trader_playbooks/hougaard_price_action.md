# TOM HOUGAARD — THE FIRST TRADING MANUAL
# Source: "The First Trading Manual: Foundation Course and Strategies"
# by Tom Hougaard (professional trader since well before 2018, states
# an audited multi-year trading competition track record -- one year
# turned ~£25k into ~£1m, no losing year under 100% return -- plus
# broker-side experience and media appearances), supplied 2026-07-20.
# INDEPENDENT voice #15.
# Credibility tier: MEDIUM-HIGH for this register -- audited
# competition results are a stronger evidentiary claim than most
# sources here (though still testimony, not something we've verified
# ourselves), broker-side pattern-recognition experience across
# "thousands of traders," explicit self-disclosure of net-worth swings
# and losing trades rather than only highlight reels. Still zero
# stats offered as a systematic backtest of the specific mechanics
# below -- every claim remains a hypothesis until our own data says so.

## 1. THE 4-BAR FRACTAL [the standout new mechanic — Dr. David Paul lineage]
- **Buy signal**: the CLOSE of the current bar is higher than BOTH (a)
  the HIGH of the previous bar and (b) the HIGH of the bar three back.
- **Sell signal**: the CLOSE of the current bar is lower than BOTH (a)
  the LOW of the previous bar and (b) the LOW of the bar three back.
- Works on any timeframe; higher timeframes carry more weight. Not a
  reversal-only tool -- fires on trend continuation as well as trend
  change, since it's purely a "closed stronger than recent structure"
  test. Explicitly described as reliable but not a Holy Grail -- "it
  will catch some sustained trend moves, but you will also have your
  fair share of small losses."
- Distinct from every existing structure-break mechanic in the
  register (which mostly key off swing highs/lows or S/D zones) --
  this one is a pure CLOSE-vs-two-reference-highs/lows test with no
  swing/pivot detection needed at all. Simplest and cheapest signal
  in the whole repo to compute.

## 2. DIVERGENCE AS TREND-CONTINUATION CONFIRMATION [distinctive framing]
- Classic price/oscillator (Stochastic in source) divergence -- but
  used here specifically to CONFIRM CONTINUATION of an established
  trend, not to call a reversal. Example given: market trending down,
  price makes a LOWER high, but the oscillator makes a HIGHER high
  (divergence) -- this is read as bullish pressure fading out, and the
  down-trend is expected to RESUME. The 4-Bar Fractal is then used as
  the entry trigger once the divergence has set up.
- This is the OPPOSITE use-case from how divergence appears elsewhere
  in this register (Kurisko's quad rotation reversal signals, CVD
  divergence at S/R in the master engine and Trader Dale's book,
  voice #14) -- those all treat price/indicator divergence as a
  REVERSAL tell. Hougaard treats it as a trend-continuation tell when
  it occurs mid-trend rather than at a fresh extreme. Both readings
  may be correct in different contexts (at a fresh S/R extreme vs.
  mid-trend pullback) -- logged as a genuine, testable tension, not
  resolved here.

## 3. 3-BAR SWING (simple mechanical trend state)
- Track the highest high and lowest low of the last 3 bars (3 days on
  the daily chart in source, but stated to work on any timeframe with
  more frequent/less reliable signals on lower ones).
- If price closes below that 3-bar low, trend = down. If price closes
  above that 3-bar high, trend = up. Recompute the reference window
  forward from wherever the trend last flipped.
- Deliberately simpler than every other trend-state mechanic already
  in the register (Dave's swing maturity count, EMA-stack levels,
  QT's AMDX phases, etc.) -- offered as a lightweight, cheap-to-compute
  HTF bias filter, not a replacement for the more detailed ones.

## 4. 89-PERIOD MOVING AVERAGE FOR HTF BIAS
- On the weekly chart specifically, price above the 89-period MA =
  uptrend, below = downtrend; if it's ambiguous, the market is
  accepted as non-trending on that timeframe (no bias forced).
  A specific, simple, portable HTF-bias convention worth having as an
  option alongside the register's existing EMA-stack (H35) and 89 is
  close to but not identical to a Fibonacci number (89 IS a Fibonacci
  number, in fact -- consistent with a lot of retail TA convention).

## 5. FADE THE SHORT-TERM TREND IN THE DIRECTION OF THE LONG-TERM TREND
- Explicit MTF philosophy: if daily trend is up and the 60-min trend
  is down, take the countertrend (on the 60-min) trade IN THE
  DIRECTION of the daily trend -- i.e. buy the 60-min dip. This is the
  SAME idea as the register's dominant MTF-alignment corroboration
  (now 7 independent constructions) -- logged as an 8th, not built as
  new code.
- Explicit caution attached: a confirmed trend change on a LOWER
  timeframe does NOT imply a confirmed trend change on a HIGHER
  timeframe -- a specific, sharp statement of a principle this
  register already assumes but rarely states this explicitly.

## 6. FAKE-OUT / FAKE-DOWN + THE ABCD PATTERN
- Trendline drawn across 3-4 tops (or bottoms); price sweeps beyond an
  old low/high (the "fake"), then reverses back through the trendline
  -- entry on the trendline reclaim. Explicitly the SAME sweep-then-
  reverse shape dominant across this register (now well past 8
  independent sources: PBD, QT Judas, Dave, Steve/MMM4x, voice #9,
  Wendell, voice #11, Alchemist, Pure PA/SMC, Trader Dale). Logged as
  further corroboration, not a new mechanic -- the specific "trendline
  reclaim after a swept extreme" combination is a minor variant worth
  noting but not separately coded (the existing trendline_breakout
  core plus any of the register's sweep detectors already covers this
  shape jointly).
- ABCD: a simple 2-leg corrective pattern (down-up-down or up-down-up)
  inside a larger trend, explicitly framed as normal retracement
  behavior, not a reversal signal by itself -- corroborates the
  register's "trends persist, corrections are shallow until proven
  otherwise" framing (Cognitive Architecture, principle 2 in section 7
  below).

## 7. PRICE BEHAVIOUR PRINCIPLES (Hougaard's stated axioms, not new
mechanics but worth recording as a distinct voice's independent
arrival at ideas this register already holds)
- "Value doesn't exist" -- price is never cheap or expensive in an
  absolute sense; a falling price is not evidence of a bargain,
  because trends persist. Converges with the register's existing
  "don't fight a confirmed trend" family.
- Trending markets have higher odds of continuing than reversing; a
  big trend rarely stops without a warning sign (price/volume spike,
  media euphoria, or a shift into a range).
- "90% of the move comes in the last 10% of the trend, time-wise" --
  a specific, quotable claim about trend acceleration near
  exhaustion, attributed to his own mentor. Untested by us.
- Markets alternate between ranging and trending regimes -- same
  underlying idea as Q-alternation (H15, QT school) and the FX Master
  Pattern's contraction/expansion/trend cycle (voice #11), independently
  re-derived a third time.

## 8. TRADE MANAGEMENT (portable, not separately coded)
- **Engulfing entry aggressiveness, 3 tiers** (portable to ANY pattern-
  based signal in this repo, not just engulfing): (1) aggressive --
  enter anticipating the pattern will complete, bail if it doesn't;
  (2) normal -- wait for the pattern to fully close before entering;
  (3) cautious -- wait for the NEXT bar to trade through the pattern's
  extreme before entering. A clean, reusable framework for trading off
  the SAME signal at different conviction/risk levels -- worth
  adopting as a general option across engines rather than hard-coding
  per-pattern, since it applies uniformly.
- **Engulfing-style exit management**: move to breakeven if the trade
  runs immediately in your favor; trail progressively if a real trend
  develops; TIGHTEN the stop specifically when a reversal-type candle
  (their example: doji) prints against the position; tighten or take
  profit if volume spikes into an approaching S/R zone. The doji-
  tightens-the-stop and volume-spike-near-S/R rules are concrete,
  portable management triggers not explicitly stated elsewhere in the
  register.
- **Scaling in, specific rule**: the first add to a winning position
  should only happen at a point where the stop on the FIRST position
  can move to breakeven -- and that becomes the stop for the SECOND
  position too, so total risk never increases as you add. Distinct
  from (and complementary to) the register's existing scale-OUT
  convention (1/3 @ 1R, 1/3 @ 2R, runner) -- this is the mirror-image
  scale-IN rule, not previously captured.
- **"Either you're in or you're out"**: Hougaard's own personal
  preference is explicitly NOT the standard scale-out convention --
  he treats position sizing as a single all-in/all-out decision per
  his own risk tolerance, and states this is a psychological
  preference, not a mathematically superior method. Logged as a
  registered COUNTERPOINT to the scale-out convention already in
  PLAYBOOK.md, not a replacement.

## 9. NOT BUILT — manual/qualitative techniques
- **Copy-trendline technique**: draw one trendline, then copy its
  exact slope onto a different high/low on the chart to project a
  parallel support/resistance line. A genuinely interesting manual
  charting trick, but not something to automate as an alert -- it
  requires human judgment about which two points to anchor to.
  Documented, not coded.
- **Trading psychology material** (fear of being wrong/losing money/
  missing out/leaving money on the table; energy management; "the
  need to be right" vs. "handling losses defines a trader more than
  hit-rate," which directly corroborates the Cognitive Architecture's
  own expectancy-over-win-rate principle; deliberate practice /
  10,000-hours framing) -- not mechanical, not coded, but consistent
  with and reinforcing the psychology layer already mandated by
  COGNITIVE_ARCHITECTURE.md. No new standing rule added since nothing
  here contradicts or extends what's already adopted.

## 10. ENGINE
indicators/hougaard_4bar_fractal_engine.pine — the 4-Bar Fractal
entry signal, the 3-Bar Swing trend-state flag, an 89-period HTF MA
bias filter, and a Stochastic/price divergence-as-continuation tag
that upgrades a same-direction Fractal signal when it fires mid-trend
with supporting divergence. All bar-close, non-repainting.
