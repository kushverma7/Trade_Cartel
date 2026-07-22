# Hima Reddy — The Trading Methodologies of W.D. Gann (2013, FT Press) — voice #19
# Source: full book text, user-supplied, read in full (3699 lines).
# Credibility: MEDIUM. Named, published, CMT-credentialed author reinterpreting
# Gann's own writings (primarily "How to Make Profits Trading in Commodities").
# Worked examples throughout with real tickers/dates/prices, but no aggregate
# track record or backtest statistics offered for the methodology as a whole.
#
# NAMING NOTE: this is a DIFFERENT voice from indicators/gann_square_of_nine_engine.pine
# (voice #16, Gann's own Square of Nine / angle / time-cycle material, plus
# TradingFives). Reddy explicitly states this book covers Gann's TRADING
# methodology only and deliberately excludes his forecasting/Square-of-Nine/
# geometric-angle work — zero overlap with voice #16's engine. One brain per
# voice/school — do not merge into gann_square_of_nine_engine.pine.
#
# IMPORTANT CORRECTION TO THE TRIGGERING SCREENSHOTS: the user supplied chart
# screenshots from a Telegram channel ("t.me/Wdgann sandipTradingViewindicators")
# showing "WDGANN SANDIP GANN BOX" rectangular BUY ZONE / SELL ZONE bands, a
# multi-timeframe RSI table, and colored candles, with "DEMO CALL" + phone
# number promotional framing (same low-credibility profile as the earlier
# "Big Secret of Intermarket Trading" PDF, voice #17). CONFIRMED via full read
# of this book: the term "Gann Box" appears NOWHERE in it, and the book never
# describes a rectangular/banded geometric price-time grid comparable to what
# is commonly marketed as a "Gann Box." The zone-box visual in those
# screenshots is a third-party proprietary layer, NOT sourced from this book
# or from Gann's own writings as documented here. The engine built from this
# voice uses REAL documented mechanics (eighths retracement zones, RSI
# confluence) to produce a visually similar zone/RSI-table look, without
# claiming to replicate the undocumented "Sandip Yadav Gann Box" formula.

## 1. Eighths Retracement (the core price tool)
Divide any swing A->B into 8 equal parts: 0, 12.5, 25, 37.5, 50, 62.5, 75,
87.5, 100%. The 50% level is explicitly Gann's single most important
retracement (Buying/Selling Point #7 is built entirely around it).
- Two projection methods once a pullback to point C forms: re-project the
  full eighths grid from B, OR re-project it from C. Both produce useful
  forward resistance/support in the book's worked examples (INTC, AUDUSD).
- **Closing-price variant**: anchor the grid to the highest CLOSE and lowest
  CLOSE of the swing (not the raw high/low) -- "the closing price is where
  buyers and sellers agreed on value." Worked example ($XAU weekly) shows a
  close-anchored resistance level tested within 3 cents nearly 3 years later.
- **Time-domain generalization**: 50% (and the eighths) also applies to the
  DURATION of a move, projected forward as a time-turn zone, and to a single
  bar's own high-low range, and to a sideways range's boundaries.
- **RSI-applied variant (genuinely novel, not just OB/OS thresholds)**: RSI
  is treated as its own price-like series and gets the SAME eighths
  retracement geometry applied to its own swings, plus the SAME
  buying/selling-point time-exceedance logic applied to its own rallies/
  declines. Williams %R gets identical treatment. Worked example (Sugar
  futures): RSI's own decline 62.66->22.53, subsequent RSI rally's time
  duration compared to RSI's own prior rally (Buying Point #5 logic, applied
  in RSI-space), then RSI's pullback tested "43.96, the 50% retracement of
  the 22.43/61.83 [RSI] section up."

## 2. Gann Buying Points (#1-#9) and Selling Points (#1-#9, mirror image)
Full text in Appendix C of the source; summarized here (see book for exact
worked examples with tickers/dates):
1. Buy/sell at OLD BOTTOMS/OLD TOPS with a tight stop (3 sub-variants by how
   price behaves relative to the old level: holds above/at/slightly-through).
2. Safer point: buy when price crosses a series of prior weekly tops (sell:
   breaks a series of prior weekly bottoms).
3. Safest point: buy on a secondary reaction AFTER crossing prior tops AND
   the rally exceeded the greatest rally during the preceding decline (sell:
   mirror, secondary rally after breaking prior bottoms).
4. Buy when the first rally off the bottom exceeds in TIME the greatest
   rally of the preceding bear campaign (sell: mirror on time of decline).
5. Buy when the rally off the bottom exceeds in time the LAST rally before
   the extreme low (sell: mirror).
6. Buy after a breakaway point is crossed (runaway-move entry).
7. Buy at 50% retracement of the last move down / of the extreme range
   (sell: mirror, 50% retracement of the last move up).
8. Buy against double/triple bottoms, or on 1st/2nd/3rd higher bottom, add a
   2nd lot after crossing the previous top (sell: mirror -- double/triple
   tops, lower tops/bottoms).
9. Rapid-move rule: in the last stage of a bull run, buy on 2-day reactions
   with a tight (1-2 cent) trailing stop under each day's low (sell: mirror
   in a rapid decline).

## 3. Triple/Double Top/Bottom -- 3-tier entry structure
Confirmation = a full CLOSING break of the constituent pivot(s). Three
risk/safety tiers, keyed to which internal pivot has been broken (worked
MU/AMX examples give exact prices at each tier -- aggressive/safer/safest).
General principle: the longer the duration between the lows/highs of the
pattern, the more significant the subsequent move (AMX: 20 weeks between
double-bottom lows -> ~2-year advance that followed).

## 4. Test-Failure Concept (crisp, 2-bar window, high confluence value)
A key support/resistance level is TESTED (price probes through it intrabar/
intraperiod) but the bar/period **closes back on the original side** within
a 2-bar window following the test -> "test failure" -> often signals the
level HOLDS and the prior trend/bias continues. Exact worked examples (BAC
weekly/daily) given for both bearish test failure (resistance holds) and
bullish test failure (support holds). This is a real, falsifiable,
codeable confluence rule.

## 5. Trendline Channel (parallel-line "alert" construction)
Standard trendline: 2 points tentative, 3rd touch confirms (cites Murphy).
Gann's own critique (invoked by Reddy): a trendline tested 3 times is MORE
likely to break on the 4th test than hold -- consistent with this repo's
existing 3-tap-fade family, opposing tension already logged as H64.
**Channel construction (Reddy's own extension, genuinely new)**: take the
trendline's ORIGIN bar; project a line PARALLEL to the trendline starting
from the OPPOSITE extreme of that same origin bar (if the trendline is
drawn off the origin bar's low, the parallel is drawn off that bar's high,
and vice versa). This parallel line, projected forward in time, is the
"alert" -- a later swing point forming near/at the projected parallel flags
a probable reversal zone. Exact worked example (GOOG): rising trendline
origin bar low $433.63 (July 1, 2010, high of that SAME bar = $448.40);
parallel projected from $448.40 "alerted the trader" to the $490.86 low
that formed 13+ months later (Aug 19, 2011).

## 6. Trade & Capital Management (Chapter 6 -- concrete, worked numbers)
- Risk cap: 2% of capital per trade (Reddy's practical number; Gann's own
  literal rule was <=10%/trade, "divide capital into 10 equal parts").
- **Scale up** only after the account DOUBLES: withdraw half the profit to
  a surplus fund, recompute 2% risk off the new (smaller) balance.
- **Scale down** after 3 CONSECUTIVE LOSSES: recompute 2% risk off the
  reduced balance immediately, cascading down further after each additional
  3-loss run.
- Money stop (pure $ risk) vs. Logical stop (price-structure-based) -- use
  logical stops, but skip the trade entirely if the logical stop's distance
  breaks your max-risk cap rather than loosening the risk rule.
- **Breakeven rule**: once open profit >= the original initial risk, move
  stop to breakeven.
- **Fourths trailing-stop method** (range/band trading): divide the range
  into 4; at 1/4 reached -> stop to breakeven; at 1/2 reached -> stop to
  just beyond the 1/4 level; at 3/4 reached -> stop to just beyond 1/2.
- **2-bar trailing-stop rule for runaway moves** (the most concrete/codeable
  management rule in the book): in a strong trend, a single-bar pullback
  that breaks the prior bar's low/high is NOT a trend-change signal --
  normal noise. The valid trailing-stop reference is the extreme of the bar
  TWO bars back (excluding the current bar), offset by a small buffer. Only
  a break of THAT level is a genuine warning. Exact worked SN12 soybean
  example shows the 2-bar method holding a trade through a 1-bar dip that
  would have stopped out a naive 1-bar trailing method, capturing
  significantly more of the move.
- 5 formal exit types: breakeven stop, trailing stop, target hit, original
  stop hit (loss), manual exit on loss of valid indication.
- Pyramiding: only add to a position already in profit, only in a strongly
  trending market, only after price crosses a resistance level (longs) or
  breaks a distribution zone (shorts) -- never average down, never pyramid
  on an unconfirmed/flat move.

## 7. Gann's 28 Rules (Appendix A/B, affirmative-rephrased by Reddy)
Full numbered list preserved verbatim in BELIEF_REGISTER cross-reference
notes / this file's git history. Concrete/falsifiable highlights not
already covered above: never average a loss (#13), never cancel a stop once
placed (#16), reduce size after a loss / never increase (#27), avoid
increasing size after a long win streak until account structurally doubles
(#24), never hedge -- exit at market instead of offsetting with an opposite
position in a different but related commodity (#22).

## 8. Other genuinely new, falsifiable pieces
- **Sectioned-move weakness heuristic**: a bullish/bearish move built from
  MULTIPLE discrete sections (rather than one impulsive move) is
  structurally weaker -- explicitly tied to the test-failure concept as an
  early warning a setup may be failing (GLW worked example: 2 bearish test
  failures at the same resistance before a reversal).
- **Cross-timeframe flexibility**: if section/swing structure is unclear on
  the current timeframe, shift to a faster or slower chart rather than
  forcing a read on ambiguous structure.
- **Closing-price-only (line chart) technique** to clarify ambiguous swing
  structure before applying eighths retracements.
- Calendar-month seasonality tabulation (Ch.8/Appendix E, forecasting-
  adjacent, explicitly a SOFT filter not a standalone signal) -- NOT built,
  out of scope for a 5m gold scalping engine per the same reasoning already
  applied to Gann's own seasonal/anniversary material in voice #16.

## What's built (indicators/hima_reddy_gann_engine.pine)
- Auto-detected swing A->B (pivot-confirmed) eighths retracement grid, with
  a small tolerance ZONE band around each level (our own convention for the
  "zone" visual, since the book only describes single retracement LINES --
  flagged explicitly, not claimed as sourced).
- RSI(14) with the SAME eighths retracement grid applied to RSI's own
  A->B swing (the book's RSI-applied-retracement variant) + a
  multi-timeframe RSI status table (1m/5m/15m/1H/4H/1D).
- 50%-retracement buy/sell signal (Buying/Selling Point #7).
- Test-failure detector (2-bar close-back-through rule, both directions).
- Trendline channel: origin-bar-opposite-extreme parallel projection with
  alert on a later swing forming near the projected line.
- 2-bar trailing-stop reference plotted for trade management once a signal
  fires (informational, matches the book's most concrete exit rule).
- Double/triple top-bottom break flagged as a single confirmed-break signal
  (the book's 3-tier risk structure is simplified to one clean trigger here
  for codability -- the tiering itself is a discretionary risk choice, not
  a different market fact).
- NOT built: time-domain eighths (needs a bar-duration UI this repo doesn't
  have elsewhere), closing-price-anchor variant (toggle-able extension, low
  priority), fourths trailing-stop range method (redundant with the 2-bar
  method for a 5m scalping context), seasonality tabulation (out of scope,
  same reasoning as voice #16), all 18 numbered buying/selling points
  individually (several require subjective "safer/safest" tier judgment --
  only the clearest, most falsifiable ones (#4/#5 time-exceedance, #7 50%,
  #8 double/triple break) are coded as discrete signals; the rest are
  documented here for confluence reading, not auto-signaled).

## Register impact
H70 (eighths retracement + RSI-applied variant), H71 (test-failure 2-bar
rule), H72 (trendline channel parallel-from-origin-bar construction). See
BELIEF_REGISTER.md for full writeups.

---

## Audit pass against original source text (2026-07-22)
Re-read the full book. Found one load-bearing caveat that was dropped and
several omissions:

- **IMPORTANT — test-failure is NOT an entry signal in the source**: the
  book explicitly states (the 2-bar test-failure pattern) "is not a signal
  that is meant to be targeted for market entry" — it's a trade-management/
  exit-warning tool for an ALREADY-OPEN position, not an entry trigger.
  This playbook's own "what's built" section describes a test-failure
  detector firing signals in both directions without this constraint —
  risking exactly the misuse the source warns against. This engine (and
  any downstream engine reusing this rule, e.g. the Top/Bottom engine's
  `useTestFail` toggle) should be reviewed against this caveat.
- **Wrong — Buying/Selling Points mirror by concept, not by number**:
  playbook's "(sell: mirror)" notation implies same-numbered symmetry.
  Actual mirroring isn't 1:1 by index — Buying Point #5 (time-exceedance
  vs. last rally) mirrors Selling Point #6, not #5.
- **Missing — Gann's documented track record**: source cites the 1909
  Wyckoff/Gilley account — 286 observed trades, 264 winners, 92% —  one of
  the book's key credibility anchors, not mentioned anywhere.
- **Missing — the 8-phase trade cycle**: Trend assessment -> Signal
  observation -> Risk assessment -> Order placement -> Trade initiation ->
  Trade management -> Trade exit -> Review. This is the organizing
  structure the built material is drawn from but the framework itself
  isn't captured.
- **Missing — concrete stop-loss distance rule (Gann Rule #2)**: 1-3
  cents (max 5) for commodities generally, 20-40 points (max 60) for
  cotton, 3-5 points for stocks. The capital-management section covers
  %-risk but drops this price-distance rule.
- **Missing — Gann Rule #8, portfolio-level cap**: aggregate risk <10% of
  capital per MARKET (not just per trade), explicitly allowing
  diversification across 2-3 commodities/4-5 stocks. Only the per-trade
  10% rule made it in.

Verified accurate: eighths retracement mechanics, 28-rules citations
(#13/#16/#22/#24/#27), trendline channel/GOOG example, fourths trailing-
stop, breakeven rule, pyramiding rules. Not yet ported to the engine —
the test-failure caveat especially should be addressed before further
tuning of engines that use it.
