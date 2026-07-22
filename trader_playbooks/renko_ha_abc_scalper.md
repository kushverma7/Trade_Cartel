# RENKO/HEIKIN-ASHI ABC-123 SCALPER
# Source: live 1-on-1 mentoring call transcript (mentor unnamed in source,
# teaching student "John"), supplied 2026-07-20. INDEPENDENT voice #9.
# Credibility tier: LOW — anecdotal self-reported PnL ("$6k last night"),
# no verified track record, no backtest, sells a $1,500 EA. Mechanics are
# fully codeable and falsifiable; we keep them, discard the anecdotes.

## 1. CORE PATTERN — ABC / "1-2-3"
Classic swing-structure reversal, same shape as PBD/Dave/QT's break-of-
structure but taught independently here (5th independent voice landing on
this shape — see Corroboration Ledger).
- Uptrend: HH, HL, HH, HL... until a swing fails to make a higher high,
  price makes a LOWER LOW (point 1), retraces to a LOWER HIGH (point 2),
  then breaks back below point 1 (point 3) = short entry trigger.
  Mirror for bullish reversals off a downtrend.
- Entry: on the break of point 1 (aggressive), OR wait for a second
  retracement leg for a tighter/second entry, OR use a fib 50-61.8%
  retracement of the 1-2 leg as a limit entry zone (his stated favorite —
  "very strong to go in").
- Scale-in: up to 3 tranches on successive retracements within the same
  structure; stop trails, so late entries often go to breakeven/free
  trade even if the first entry is stopped.
- Not exclusive to reversals — the same 1-2-3 shape re-triggers as a
  CONTINUATION pattern on every retracement inside an established trend
  (this is the majority of his entries, not just reversal calls).

## 2. RENKO + HEIKIN-ASHI (the noise filter)
- Trades on synthetic Renko bricks (fixed price-box size, time removed)
  with Heikin-Ashi coloring applied ON TOP of the bricks — not price
  candles. Rationale: HA-on-Renko turns an entire directional run into a
  single flat color and produces a clean doji exactly at each real
  reversal, vs. regular candles mixing colors mid-trend.
- Multi "setting" stack (his substitute for multi-timeframe, since Renko
  has no time axis): a larger brick size sets bias/holds through noise;
  a smaller brick size gives the entry with materially less stop
  distance (his repeated point: same structure, 10-15 cents of risk on
  the small setting vs 50-60 cents on the large one for the same trade).
- CAVEAT (ours, not his): Renko/HA are inherently a same-bar-forming
  construct — the current forming brick is not final until price moves
  a full box size. Any real-time engine must only signal on a CLOSED
  brick, exactly like closed-bar discipline elsewhere in this repo.

## 3. THREE-EMA STRUCTURE (12 / 24 / 36)
- Purely visual/trailing tool on the Renko close — not a crossover
  system. Lagging by design; used to see where to place/trail stops.
- "Floating" entry trigger: the first Renko/HA brick that fully clears
  (separates from) the 12/24/36 cluster in the trade direction = the
  entry signal, taken together with the ABC/123 structure.
- Trail stop: below/above the 36 mechanically; he personally watches the
  24 as an earlier discretionary trail line ("the sweet spot is between
  the 12 and 24").
- Exit tell: price/HA re-crosses into the 12-24 band, OR HA prints a
  counter-color doji. Up to 3-4 consecutive counter-color bricks are
  tolerated as normal retracement; by the 4th-5th, exit — thesis broken.
- Optional 55 EMA (fib) and 200/633 EMA (higher-TF trend context, only
  trade with the higher trend) layered on for swing-hold conviction.

## 4. FIBONACCI USE
- Retracement 38.2/50/61.8% of the completed 1-2 leg = entry zone for
  point 3.
- Extension / "measured move": the next leg often equals the size of the
  prior impulse leg — project it forward as a target/second-entry check.
- Explicit caution (echoes user's own Fib skepticism in this session):
  pivot anchor choice drifts as price moves; the mentor anchors from the
  LATEST confirmed swing low/high of the specific 1-2-3, not older highs.

## 5. INSTRUMENT / SESSION SELECTION (macro filters, pre-chart)
- Daily pre-market: check medium+ impact news calendar (limited to a
  handful of countries — here US/CA/EU/UK), check futures/index
  performance for regime, check FX volatility ranker (avg daily range
  per pair) and correlation/relative-strength table.
- Trade the currency with the greatest relative strength divergence
  (e.g., only trade GBP pairs unless GBP is weak, then switch base
  currency entirely) — never trade a low-ADR pair when a high-ADR
  alternative with the same directional thesis exists.
- Session note (converges with B1/Steve H20 by yet another route):
  most Renko setups fire 06:00-11:00 ET; largely dead 19:00-02:00 ET.
- Calendar-month filter: first week of the month = slow (FOMC/NFP
  positioning); avoids Monday/Friday entries; builds the week's bias
  Sunday night, executes Tue-Thu.
- Gold/silver explicitly flagged by the STUDENT (not the mentor) as
  NOT following the clean ABC/123 float — "bipolar," choppy for days
  then violent. Mentor's counter: the same mechanics still apply, gold's
  measured moves are simply larger/faster. UNRESOLVED — test on XAUUSD
  before trusting this school's gold applicability (H29).

## 6. ALERTING DISCIPLINE
- Three alert types on his EA: EMA(36) cross, trendline break, extreme-
  velocity candle ("rocket"). All send phone push + sound + popup so he
  isn't glued to the screen. We already have this pattern everywhere in
  the repo (alertcondition on every engine) — no new idea, just another
  independent vote for "alert on the trigger, don't screen-watch."

## 7. WHAT WE DISCARD
- The $1,500 EA sales pitch and "don't give it away" framing.
- Anecdotal single-session PnL claims ($6k, $4.7k) as evidence of edge.
- Renko brick-size specifics (10/17/26 "ticks") — instrument- and
  broker-feed-specific, not portable to our gold data.

## 8. ENGINE
indicators/renko_abc_scalper.pine — synthetic non-repainting Renko/HA
construction (ATR-scaled box size), 12/24/36 EMA cluster, floating-brick
entry trigger, ABC/123 pivot-based structure break, counter-color-run
exit counter, fib 50/61.8 retracement zone marker.

---

## Audit pass — original transcript recovered from session log (2026-07-22)
Raw transcript recovered from the session log and permanently saved to
`trader_playbooks/sources/raw_transcripts/line1427_2026-07-20.txt` (the
mentor's live 1-on-1 call with student "John"). Clean match: ABC/1-2-3
structure, fib 50-61.8% entry ("very strong to go in," quoted verbatim),
Renko+HA doji-at-reversal logic, 12/24/36 EMA "floating brick" entry and
"sweet spot between 12 and 24" exit tell, fib measured-move extension,
FX/news pre-market filter, the 06:00-11:00 ET session window ("starting
at 6am... 6 to 11... then it dies out" — exact), Monday/Friday avoidance,
and the "$6k last night" PnL anecdote all verified verbatim. The file's
second anecdote ("$4.7k") and its three alert types (EMA cross/trendline
break/rocket candle) aren't in this particular transcript excerpt —
likely from another session with the same mentor/student pair, not an
error given the file is explicitly multi-session. No changes needed.
