# Why the champion works, what the Market Wizards say, and what to do next

Written 2026-08-03, after twelve entry systems failed their controls in one
session and the champion `strategies/gold_trend_strategy.pine` did not.

**Sourcing note, stated up front.** Part 1 is derived from the code and from
`RESULTS_LEDGER.md` — every number is traceable. Part 2 is **not** in this
repo. `trader_playbooks/` contains 22 voices, but they are retail educators
(Ario, Dave, JeaFX, Wendell, Hougaard, Roppel…), a different population from
Schwager's interviewees; the only mention of *Market Wizards* anywhere in the
repo is `roppel_trend_following.md` listing it as a book he recommends. So Part
2 comes from training knowledge of the Schwager books, and quotes are marked
for how confident I am in the wording. No page citations, because I cannot
verify them here.

---

# PART 1 — Reverse-engineering the winner

## 1. The exact entry logic

Four conditions, all of which must be true on the same bar
(`gold_trend_strategy.pine:287-291`):

| # | condition | code | effective setting on 30m |
|---|---|---|---|
| trigger | close breaks the Donchian extreme of the prior N bars | `close > ta.highest(high, entryLenE)[1]` | N = 24 bars ≈ 12 hours |
| regime | close on the correct side of a long EMA | `close > ta.ema(close, regimeLenE)` | 1008 bars ≈ 21 days |
| filter 1 | close on the correct side of a fast SMA | `close > ta.sma(close, smaLenE)` | 384 bars ≈ 8 days |
| filter 2 | close on the correct side of a slow SMA | `close > ta.sma(close, sma2LenE)` | 1008 bars ≈ 21 days |

Shorts add a fifth: the regime EMA must be **falling**
(`regimeMa < regimeMa[slopeLenE]`, 96 bars ≈ 2 days). Longs are not gated on
slope by default — a deliberate asymmetry, with the toggle at line 169.

Plus a 3-bar cooldown after any exit, and one position at a time.

**All lookbacks are derived from the timeframe, not hardcoded**
(`:255-261`). `[1]` on every Donchian call means no bar can trigger on its own
extreme. Sizing is `equity × risk% / stopDist`, so position size falls as the
stop widens.

## 2. The exact exit logic

**There is one exit and it is a trailing stop.** `:317-322`:

```pine
if strategy.position_size > 0
    float cand = high[1] - atr * trailMultE     // chandelier
    trailStop := na(trailStop) ? cand : math.max(trailStop, cand)
```

- Ratchets one way only. `math.max` for longs, `math.min` for shorts.
- Anchored to `high[1]`, the **previous** bar's extreme. BUG-019 was exactly
  this bug in another engine; here it is correct by construction.
- Width `6.0 × sqrt(15/tf)` → **4.24 ATR on 30m**, ≈ 15.7 points of gold.
- **No profit target. No time stop. No breakeven move. No partial exits.**
  Every one of those exists in the file as a toggle and every one is
  **defaulted OFF with its losing numbers in its own tooltip.**

Adds: every 1.5 ATR of favourable movement, up to 4, each sized at the
original risk (`:335-346`). They share the one trailing stop.

## 3. What separates it from the twelve that failed

Not the entry — it's the same family. The Donchian breakout the champion uses
is a *more* naive trigger than most of the twelve. The differences are
structural, and they are all on the exit-and-cost side:

| | the twelve failures | the champion |
|---|---|---|
| stop width | 0.5 – 1.5 ATR | **4.24 ATR** |
| target | fixed 1.5R / 2R / next level | **none — trail only** |
| hold | 3 bars (kl_reverse), ≤96 bars capped | **44 bars average, uncapped** |
| win rate | 40 – 57% | **23.0%** |
| payoff | 1.2 – 1.4× | **5.45×** |
| trades/yr | 280 – 460 | **117** |
| cost as % of risk | 7 – 22% | **2.55%** |

## 4. Which components are responsible — measured, not assumed

The file's own random-timing null (`RESULTS_LEDGER.md:1056-1073`) answers this
directly. Random entries drawn from the **same filtered bars** at a matched
rate, pushed through the identical exit, filters, sizing and adds:

| arm | PF | net |
|---|---|---|
| champion | 1.626 | +660.2% |
| random timing, median of 30 seeds | **1.478** | **+524.1%** |
| random timing, range | 1.378 – 1.635 | +312.3% to +817.6% |

**The champion sits at the 93.3rd percentile of its own null — inside the
noise band.** Replace the entry with a coin flip and it still returns +524%.

Attribution, in order of measured contribution:

1. **Trail width.** 2 ATR → PF 1.05. 6 ATR → 1.60. 14 ATR → 1.75. This is the
   single largest variable in the system.
2. **Adds to winners.** +192.6% → +679.9%. Improves all five walk-forward
   slices. But through random entries it takes the worst seed from −3.5% to
   −30.2% — **a leverage multiplier, not an edge.**
3. **The two-SMA agreement filter.** PF 1.379 → 1.421, drawdown 12.30% →
   **9.63%**. Requiring only one of the two averages is much worse (1.149), and
   substituting a slower average for the fast one is also worse. It is the
   *disagreement between horizons* that marks chop.
4. **The short-slope gate.** What makes it profitable in falling markets
   (2026: +26.0% while gold fell 6.0%).
5. **The entry trigger.** Contributes +0.148 of profit factor over a coin flip,
   which is inside the seed-to-seed spread. **Nearest thing to zero.**

## 5. The real weaknesses

1. **Execution quality is the largest single risk, larger than any parameter.**
   0.20 pt → PF 1.641. 0.50 pt → 1.452. 1.00 pt → 1.141. **1.50 pt → 0.888,
   dead.** The whole system lives in a 7× cost band, and a retail gold spread
   during a news minute can cross it.
2. **A 23% win rate means long losing streaks are normal.** At p=0.23 the
   expected longest losing run in 787 trades is roughly 12–13 in a row, and
   runs of 18+ are not rare. Nothing in the backtest tells the user how that
   feels. This is the most likely cause of live abandonment.
3. **Drawdown is understated relative to lived experience.** 33.63% is
   end-of-bar on closed equity. Intra-trade, with 4 adds live and a 4.24 ATR
   trail, open drawdown is worse. The Maximum profile records a 45.8%
   *intra-year* drawdown against a 22.5% year-end figure.
4. **Parameters were chosen with knowledge of both halves.** DSR 0.9996 and
   PBO 0.099 defend against this and they pass, but they are statistical
   defences, not a fresh sample. The certificate says so itself.
5. **One instrument, one asset class.** This is the exact failure mode that
   killed rule book V3 yesterday. **The champion has never been run on US30**,
   and `data/us30_15m.csv.gz` now exists. This is the biggest open hole.
6. **Regime dependence.** Gold rose 1450 → 4100 across the sample. The
   strategy beat buy-and-hold and made money in gold's down years, so it is not
   merely long beta — but it has never seen a multi-year gold bear market.
7. **`margin_long = 5` with `pyramiding = 5`** permits real leverage. The
   notional cap (`maxLev = 20`) is the only thing standing between a 4-add
   position and a margin call.

## 6. Where the edge actually comes from

Ranked by measured contribution:

**Exit management (dominant) > hold time (inseparable from it) > filters
(risk reduction) > sizing/adds (amplifier, not edge) > entry timing (~zero).**

The arithmetic, which is the cleanest statement of the whole thing:

```
win rate 23.0%,  payoff 5.45×,  expectancy +0.482 avg-loss units per trade
break-even win rate at that payoff: 15.5%
```

**It can be wrong 77% of the time and still compound, and it has 7.5 points of
win-rate cushion before it stops working.** Every failed system needed to be
right 40–57% of the time and had one or two points of cushion.

---

# PART 2 — What the Market Wizards actually say

Drawn from Schwager's *Market Wizards* (1989), *The New Market Wizards* (1992),
*Stock Market Wizards* (2001), *Hedge Fund Market Wizards* (2012) and *Unknown
Market Wizards* (2020). Weighted toward futures/FX/index traders with long
records and rule-based approaches, as asked.

**Confidence marking:** ⟦Q⟧ = wording I am confident is close to verbatim.
⟦P⟧ = paraphrase of a position the trader clearly held. Anything I am unsure
of, I have left out rather than guessed.

## A. Highest-conviction ENTRY principles

**A1. Entry matters least. Said explicitly, by multiple traders.**
- Bill Eckhardt ⟦P⟧: the entry-heavy bias of most traders' systems is a
  reflection of psychology, not of where returns come from; he argued exits
  and sizing dominate.
- Ed Seykota ⟦Q⟧: *"The elements of good trading are: (1) cutting losses,
  (2) cutting losses, and (3) cutting losses."* Note what is absent from a
  three-item list of the elements of good trading.
- Richard Dennis ⟦Q⟧, on the Turtles: *"I always say that you could publish
  trading rules in the newspaper and no one would follow them."* The claim is
  that the rules are not the scarce thing.

**A2. Buy strength, not weakness.** The Turtle entry was a **Donchian channel
breakout** — buying a 20- or 55-day *new high*. Dennis, Eckhardt, Jerry Parker,
Bill Dunn all traded breakout-style continuation.

**A3. Know your exit before you enter.** Bruce Kovner ⟦Q⟧: *"I know where I'm
getting out before I get in."* Kovner ⟦P⟧ also sized by where the stop had to
go — placing it beyond where the market's noise could reach, then sizing to fit
the risk, rather than placing the stop to fit a desired size.

**A4. Comfort is a contra-indicator.** Eckhardt ⟦P⟧: what feels good is usually
wrong; entering on a pullback into support *feels* safe, which is why it is
crowded and cheap.

## B. Highest-conviction EXIT principles

**B1. Cut losses fast — but "fast" means *decisively*, not *tightly*.** This is
the most repeated principle in the entire series and the one most often
misread. Seykota, Marcus, Dennis, Jones, Kovner all say cut losses. But the
same traders used **very wide stops**: the Turtles' was 2N (2 ATR) on the
*initial* unit and effectively wider as units were added; Dunn's DUNN Capital
ran wider still and tolerated 40–60% drawdowns. Eckhardt ⟦P⟧ made the mechanism
explicit — a stop inside the market's noise band converts random fluctuation
into a realised loss.

**B2. Do not take profits early. Stated more forcefully than almost anything
else in the books.** Eckhardt ⟦P⟧ attacked *"you can't go broke taking a
profit"* directly as one of the most damaging pieces of conventional advice.
Seykota's ⟦Q⟧ *"ride winners"* is half of his best-known pair. Marcus ⟦P⟧
attributed his largest gains to the few positions he held far longer than was
comfortable.

**B3. Asymmetry is the whole business.** Soros ⟦Q⟧, quoted by Druckenmiller:
*"It's not whether you're right or wrong that's important, but how much money
you make when you're right and how much you lose when you're wrong."* Paul
Tudor Jones ⟦P⟧ described looking for roughly 5:1 payoffs, on the logic that at
5:1 he could be wrong four times in five and lose nothing.

**B4. A low win rate is normal and is not a defect.** Eckhardt ⟦P⟧: the desire
for a high hit rate is one of the most destructive instincts a trader has, and
systems are routinely damaged by "fixing" it. Multiple trend followers in the
series report win rates in the 30s.

## C. Trade-management rules

**C1. Add to winners, never to losers.** ⟦P⟧ Turtle mechanics: pyramid every
½N of favourable movement, up to 4 units, moving the stop up with each add so
total open risk stays bounded. Druckenmiller ⟦P⟧: when a position is right,
press it hard — that is where the year is made.

**C2. Volatility-based sizing, not conviction-based.** ⟦P⟧ The Turtles' N was
ATR; units were sized so 1N of movement equalled a fixed fraction of equity.
Kovner sized by stop distance. Ed Thorp (HFMW) ⟦P⟧ argued the same from Kelly.

**C3. Reduce size in a drawdown.** Randy McKay ⟦P⟧ and Michael Platt (HFMW)
⟦P⟧ both cut exposure hard when losing — Platt describes halving a position at
a fixed loss threshold. The Turtles reduced unit size after equity drawdowns.

**C4. Uncorrelated streams beat a better single system.** Ray Dalio (HFMW)
⟦P⟧ calls this the "Holy Grail": adding independent return streams improves
return/risk far more than improving any one of them.

## D. Risk & psychology that bear directly on entry/exit

**D1. Fixed fractional risk, small.** Larry Hite ⟦Q⟧: *"Never risk more than
1% of total equity on any trade."* Broadly echoed across the trend followers.

**D2. Defence before offence.** Paul Tudor Jones ⟦Q⟧: *"Don't focus on making
money; focus on protecting what you have."* Jones ⟦P⟧ also: he thinks about
losing money, not making it.

**D3. Know where you're wrong, not where it's going.** Colm O'Shea (HFMW)
⟦P⟧: he has no idea where the market is going, but he always knows the level
at which his thesis is void.

**D4. The system fails at the point where it is uncomfortable to follow.**
⟦P⟧ Universal in the series. Dennis's newspaper line, Seykota's ⟦Q⟧ *"everybody
gets what they want out of the market"*, Eckhardt's whole framework.

## Where these directly contradict what we tested and killed

| what we tested | which principle contradicts it |
|---|---|
| stops at 0.5–1.5 ATR beyond a level | **B1.** Eckhardt's noise-band argument. Our measured cost/risk of 7–22% is the same statement in money. |
| fixed 1.5R / 2R targets | **B2.** The most forcefully stated exit principle in the books. And our own data: 20 target configurations, all worse than none. |
| level touches / bounce fades | **A2, A4.** Turtles bought new highs. Eckhardt: comfortable = crowded. |
| optimising the win rate up from 40% to 57% | **B4.** Eckhardt says explicitly this is the wrong direction. |
| ORB with a session time cutoff | **B2.** A cutoff is a time-based profit cap. Note the Turtle entry *is* a breakout — the breakout is not the problem, the **bounded hold** is. |
| twelve rounds of entry-filter work | **A1.** All of it. |
| shipping on gold alone | **C4.** Dalio's Holy Grail is the direct counter. |

**Honest caveat.** Nearly every trader above traded a diversified portfolio of
20–100 futures markets. Single-instrument intraday gold is *not* the setting
they describe, and their sizing rules assume diversification we do not have.
The exit and payoff principles transfer cleanly; the sizing ones transfer only
partially.

---

# PART 3 — Synthesis

## 1. Diagnosis: why the champion worked and the twelve did not

They were not different strategies. They were the **same class of strategy at
different points on the cost-to-risk curve.**

```
system                         cost/risk  trades/yr   drag R/yr
CHAMPION (chandelier 4.24 ATR)     2.55%        117         3.0
ORB US30 60m                       1.70%        284         4.8
ORB gold LDN 15m                   1.70%        464         7.9
rulebook V1-V3 (1.5 ATR floor)     7.20%        300        21.6
level tests (0.5-1.0 ATR)         15.00%        400        60.0
```

At 1% risk per trade, the right-hand column is also *percent of equity paid to
the broker per year*. **The champion pays 3% a year in slippage. The level
systems pay 60%.** No entry rule discovered in this repo has ever been worth 57
points of annual return, so none of them could have worked, and the twelve
control failures were the arithmetic asserting itself.

Wide stop → large payoff → cost becomes negligible → the system survives being
wrong 77% of the time. That is the entire mechanism, and it is Eckhardt's
noise-band argument (**B1**) measured in dollars.

This also explains the exponent gap independently. MFE diffusion 0.558 vs MAE
0.493 says favourable excursion grows *faster than* random with hold time while
adverse excursion grows *slower*. A strategy can only collect that by holding.
The twelve capped their holds at 2R or a session close; the champion does not
cap at all. **The exponent gap and the champion are the same finding stated two
ways.**

## 2. Testable entry improvements

Set against a strong prior: the null says the entry contributes +0.148 PF
against a coin flip, inside the seed spread. **These are low-expectation and
should be run last.**

- **E1. Widen the breakout, don't tighten it.** Turtles used 20-day and 55-day.
  Ours is ~12 hours. Sweep 24h / 48h / 5-day equivalents. Wider = fewer trades
  = less drag. *Prediction: flat to mildly positive; fewer trades is the real
  gain.* Cheap to test.
- **E2. Turtle failed-breakout rule.** Skip the entry if the *previous*
  breakout in the same direction was a winner. This is a genuine Turtle rule
  (⟦P⟧) with a real rationale, and it is not a filter we have tested.
- **E3. Kill the entry entirely and go time-based.** Enter in the filter
  direction every N bars while flat. If this matches the champion, it settles
  the question permanently and simplifies the system.

## 3. Testable exit improvements

This is where the evidence says to work.

- **X1. Widen the trail past 4.24 ATR and hold size constant.** The file
  already shows PF rising monotonically to 14 ATR while *return* falls — but
  return falls only because risk-based sizing shrinks the position. **Decouple
  them:** fix the position size, then sweep the trail 4 → 20 ATR. The current
  test confounds trail width with position size and cannot answer the question.
  **This is the single highest-value experiment available.**
- **X2. Two-stage trail (Turtle-style).** Initial stop wide and fixed; switch
  to the ratcheting chandelier only after 1N of favourable movement. Currently
  the ratchet is live from bar one.
- **X3. Move the stop up with each add so total open risk stays bounded**
  (**C1**). Right now 4 adds share one trail, so open risk *grows* with each
  add — the opposite of the Turtle rule, and a plausible contributor to the
  intra-trade drawdown gap.
- **X4. Regime-conditional trail width.** Widen in high ATR percentile, tighten
  in low. Tests whether the fixed multiple is leaving money on the table.
- **X5. Drawdown-responsive sizing** (**C3**): halve risk after −10% equity,
  restore at a new high. Pure risk-management; should cut drawdown at a small
  return cost.

## 4. Ranked — top 5 changes by probability of improving robustness/expectancy

| rank | change | why it ranks here | effort |
|---|---|---|---|
| **1** | **Run the champion unchanged on US30 15m/30m** | The one test that killed rule book V3 and the one the champion has never faced. Data exists. **Dalio's C4** and our own hardest-won methodological rule both point here. Nothing else should ship before this. | low |
| **2** | **X1 — decouple trail width from position size, sweep 4→20 ATR** | Trail width is the measured dominant variable and the current sweep is confounded. Highest-value single experiment. | low |
| **3** | **X3 — bound total open risk across adds** | Adds are the biggest return lever *and* took the worst random seed to −30.2%. This is the known fix from the source that invented the technique. Targets the system's real risk, not its return. | medium |
| **4** | **X5 + C3 — drawdown-responsive sizing** | Attacks weakness #2 (a 23% win rate means 12–18 loss streaks) and weakness #3 (understated lived drawdown). Improves the odds the user still trades it in month nine. | low |
| **5** | **E1 — widen the breakout lookback** | The only entry change with a cost-side rationale rather than a prediction rationale: fewer trades cuts drag. | low |

Explicitly **not** on this list: a thirteenth entry filter, a profit target in
any form, key levels anywhere in the trade logic, and tightening any stop.

## 5. What the elite traders say about our situation specifically

The literature is unusually direct here, and it agrees with our own
measurements rather than merely rhyming with them:

- **A1** (Eckhardt, Seykota, Dennis) says entry work is where traders go to
  avoid the harder problem. Our random-timing null measured exactly that: the
  entry is worth +0.148 PF and the exit is worth the other +524% of return.
- **B4** (Eckhardt) says the instinct to raise the win rate is destructive. We
  spent twelve systems trying to get from 40% to 55% while holding the champion
  that wins 23% of the time.
- **C4** (Dalio) says a second uncorrelated stream beats a better single
  system. US30 data is sitting in the repo, untested against the champion.

**The verdict is that entry research should stop, and it should stop for a
measured reason and not a fashionable one:** in this repo, on this instrument,
at these costs, no entry rule has ever been worth what it costs to trade it.
The next round belongs to the exit (X1, X3), to sizing (X5), and to the second
instrument.
