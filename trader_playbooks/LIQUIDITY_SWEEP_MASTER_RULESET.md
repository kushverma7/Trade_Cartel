# LIQUIDITY SWEEP → MSS → RETEST — MASTER RULE SET

**Version 2.0 — evidence-audited.**
Instruments: NQ (E-mini Nasdaq-100) | GC (COMEX Gold)

---

## PROVENANCE AND STATUS

**v1.0** was supplied by the user as `LIQUIDITY_SWEEP_MASTER_RULESET.pdf`
(2026-08-12). It is a complete, well-constructed rule set built from
institutional/prop/SMC practice. It was **not** built against this repo's
measured evidence base, and it was not available to the sessions that produced
that evidence.

**v2.0 is v1.0 audited against every measurement in this repository** —
`BELIEF_REGISTER.md` (H74–H81, the exponent-gap finding, the key-level battery),
`bugs/BUG_REGISTRY.md` (37 registered bugs), `RESULTS_LEDGER.md`, and
`MEMORY.md`. Roughly 80% of v1.0 survives intact or strengthened. Four rules are
**corrected against measured contradictions**, three are **reclassified from
rule to untested hypothesis**, and one whole section (the null control) is
**added because its absence is the most likely way this framework dies quietly**.

> ## ⛔ MEASURED 2026-08-12 — NOT VALID. DO NOT TRADE.
>
> This rule set has now been coded (`research/sweep_lab.py`) and run against
> every instrument in this repo. See RESULTS_LEDGER 2026-08-12. Summary:
>
> 1. **At its own settings it produces 0–1 trades in 6.7 years** on gold, US30
>    and AU200. It is not merely unvalidated — it is unexecutable.
> 2. **§5.3.1 and §1.2 are arithmetically incompatible.** The stop rule and the
>    sweep-depth rule force RISK to a median of 0.38–0.63 ATR_D against a cap of
>    0.32–0.35. 67–100% of setups breach the cap; **none** falls below the floor.
> 3. **Relaxed to a testable sample, no configuration beats a matched random
>    entry** through the identical exit engine, on any of the three instruments.
> 4. **On 5m — the spec's own execution timeframe — the entry is significantly
>    WORSE than random** (z = −3.56).
>
> The sections below are retained because the *diagnosis* is in them and several
> individual rules (§1.3, §4.2, the type-asymmetric exits) survive independently.
> **The rule set as a whole does not.** Corrections still required before this is
> worth another run are listed in Part 9.

**Status of the whole document: FALSIFIED AT THE SYSTEM LEVEL.** §7 is the
protocol that produced that verdict; Part 9 is what would have to change.

**Evidence asymmetry you must hold in mind throughout.** This repo contains
~157,000 bars of measured XAUUSD work across seven entry families and 30+ exit
configurations. It contains **zero measurements on NQ or any Nasdaq instrument**
(grep: 0 hits in `RESULTS_LEDGER.md` and `MEMORY.md`). Every GC rule below is
anchored to something measured on gold, if not always on this exact setup. Every
NQ rule is inherited theory. That distinction is marked per-rule and must not be
smoothed over — this repo has already measured that cross-instrument transfer
fails here (RSI(2) daily: US30 IS/OOS 1.81→3.52, the same logic on AU200
1.82→**0.49**).

---

## PART 0 — AUDIT VERDICT

| v1.0 rule | Repo evidence | Verdict |
|---|---|---|
| §1.3 stop anchored to **sweep extreme**, not the swept level | **BUG-005** — anchoring to the swept level gave 12/12 losses, PF-analog 0 | **CONFIRMED.** Keep verbatim. This is the single most load-bearing rule in the document. |
| §1.4 cluster displacement — never park a stop just beyond a level | `level_reaction.py`: real touches bounce 54.28% vs 49.06% matched control, z = +20.08, n = 73,579 | **CONFIRMED, and this is the repo's one endorsed use of key levels.** Levels are a map for stop placement, not a signal. |
| §1.3 wide stop = **hard reject**, never size down | **BUG-009** — hard-rejecting wide stops killed the setups it should have caught; the fix was to *clamp* | **RECONCILED, not overturned.** See §1.5 below. Different entry type; both rules are right in their own domain and the distinction must be stated in code or BUG-009 returns. |
| §2.3 Schedule A/B applied to **both** trade types | **H75** (CONFIRMED, 3 independent), **H79** (level targets help *counter-trend only*), exponent gap (MFE 0.558 vs MAE 0.493) | **CORRECTED.** The rule is type-asymmetric. See §2.3. This is the largest correction in the audit. |
| §2.2 target = **nearest** qualifying pool | **BUG-017** — a "next level" target closer than the noise destroyed a working system (PF 1.385 → 0.702) | **CORRECTED.** Select the nearest pool that *clears* the R gate, not the nearest pool then test. See §2.2. |
| §2.4.2 12-bar time stop | Exponent gap: the MFE/MAE asymmetry is ~1.09 at 50 bars and grows to 1.32 at 800 — profit accrues to **hold time** | **RECLASSIFIED to hypothesis.** Plausible for Type R, actively suspect for Type C. Must be ablated, not assumed. See §2.4.2. |
| §3.1 base risk 0.50% / 0.25% | G1* solved risk from a drawdown budget: **0.606% at a 25% DD budget, 0.475% at 20%** (5 seeds × 5,000 MC paths) | **CONFIRMED as a magnitude, upgraded as a method.** Derive it, don't assert it. Also flags a live conflict inside this repo — see §3.1. |
| §5.2 unfilled FVG mandatory | Untested here | **KEEP as the primary hypothesis.** v1.0 claims it is the highest-value filter; that claim is testable by ablation and must be tested, not inherited. |
| §5.5 GC substitutes (DXY + Silver) | Untested here | **KEEP, flagged as the largest unvalidated block.** Test specified in §8. |
| §8 validation protocol | **H78, BUG-023, BUG-035** | **INCOMPLETE — the critical omission.** No null control, no execution-assumption control, no cost spec. See §7. |

---

## PART 1 — STOP LOSS PLACEMENT

v1.0 §1 is adopted essentially as written. It is the strongest section of the
document and it agrees with the only stop-placement bug this repo has paid for.

### 1.1 Definitions

```
ATR_D      = ATR(14) Daily, computed on CLOSED daily bars only
ATR_X      = ATR(14) on execution timeframe (5m default)
SWEEP_EXT  = extreme wick of the candle that swept the ranked level
OB_ORIGIN  = open/low (long) or open/high (short) of the last opposing
             candle before displacement
ENTRY      = fill price on the retest
```

### 1.2 The rule

```
BUFFER_NQ = max( 0.50 * ATR_X , 0.045 * ATR_D , 10 pts )
BUFFER_GC = max( 0.70 * ATR_X , 0.060 * ATR_D , 2.0 pts )

LONG:   SL = min(SWEEP_EXT, OB_ORIGIN) - BUFFER
SHORT:  SL = max(SWEEP_EXT, OB_ORIGIN) + BUFFER

RISK = |ENTRY - SL|

VALIDITY GATE:
    0.08 * ATR_D  <=  RISK  <=  0.32 * ATR_D    (NQ)
    0.10 * ATR_D  <=  RISK  <=  0.35 * ATR_D    (GC)

RISK > cap    -> NO TRADE (see §1.5 — this is a reject, not a resize)
RISK < floor  -> widen SL to the floor
```

The stop sits beyond **both** the sweep extreme and the imbalance origin. v1.0
had this as a separate "structural override" (§1.5); folding it into the primary
formula as a `min`/`max` removes a branch that a coder can get asymmetrically
wrong — which is **BUG-022** (one direction updated, the other left stale).

### 1.3 Cluster displacement (mandatory)

After computing SL, scan a window of `0.06 * ATR_D` beyond it. If that window
contains a round number (NQ: every 50 pts; GC: every $5 and $10), a prior
day/week high or low, or an equal-high/equal-low pair — push the stop to
`0.03 * ATR_D` beyond the furthest such level, then **re-run the validity gate**.
If it now breaches the cap, no trade.

**This rule has the strongest independent support of anything in the document,
and it did not come from SMC.** `backtest/level_reaction.py` measured 73,579
level touches on XAUUSD 30m against a matched control drawn from the same bar's
range: real levels bounce 54.28% vs 49.06%, z = +20.08. The effect is strongest
close in (54.28% at 0.5 ATR) and decays with distance (50.91% at 3.0 ATR). That
is a real, local S/R grip — uneconomic to *trade* (the repo tested every
configuration and none clears cost) but exactly the right size to *ruin a stop*
parked inside it.

The repo's closing position on key levels is: **"Use the indicator as a map:
stop placement, context, knowing where the crowd is."** §1.3 is that sentence
turned into an executable rule, and it is the only monetisable use of key levels
this repo has found in eight months of trying.

### 1.4 NQ vs GC

| Parameter | NQ | GC | Rationale |
|---|---|---|---|
| ATR_X buffer | 0.50 | 0.70 | Gold's wick-to-body ratio at levels is higher; thinner liquidity outside 03:00–11:00 ET means raids overshoot further |
| ATR_D floor | 0.08 | 0.10 | GC tick value is 2× NQ's; spread widening on prints is more punitive |
| ATR_D cap | 0.32 | 0.35 | Gold's structural swings are proportionally larger |
| Round-number scan | 50 / 100 pt | $5 / $10 handle | Observed clustering |
| Extra | — | No stops within $1.50 of the LBMA PM fix reference during 09:55–10:05 ET | Fix flow is non-structural |

**Confidence:** the GC column is directionally supported by this repo's gold
work. The NQ column is inherited from v1.0 and is unmeasured. Both must be
re-derived from the MAE distribution in validation (§7) rather than trusted.

### 1.5 Why hard-reject here, and why BUG-009 is not being repeated

BUG-009 recorded that a hard stop-distance rejection "killed exactly the setups
it should catch," and the fix was to clamp into `[min, max] × ATR`. v1.0 §1.3
says the opposite: reject, never resize. **These do not actually conflict, and
the distinction must be written into the code or the next engineer will "fix"
this back into BUG-009.**

- **BUG-009's context was a breakout/BOS entry taken on the break itself.**
  There, a wide stop is *intrinsic to a valid signal* — a real breakout displaces
  before you can be positioned. Rejecting wide stops rejected the good trades.
- **This framework has no market-chase entry.** Every entry is a retest at the
  origin of displacement (Step 4). Here a wide stop is *diagnostic of a defective
  setup*: either the sweep was not a clean raid, the displacement leg is oversized
  (you are late), or the retest never came deep enough. All three are structurally
  low-expectancy populations.

Sizing down converts a bad trade into a smaller bad trade and keeps a
negative-expectancy population in the sample. Rejecting removes it. The cap is
what keeps the left tail of the R-distribution thin.

**Coding requirement:** the cap must be implemented as a rejection with a logged
reason code, and the code comment must cite BUG-009 and this paragraph.

---

## PART 2 — TAKE PROFIT AND TRADE MANAGEMENT

**This is the section the repo's evidence changes most.**

### 2.1 The governing finding

`backtest/mae_mfe.py`, XAUUSD 15m/30m/60m, 2019–2026, fitting `log(excursion)`
against `log(hold)`:

| series | exponent | reference |
|---|---|---|
| MAE | **0.493** | pure random walk = 0.500 |
| MFE | **0.558** | |
| gap | **+0.065** | |

The adverse side of an entry is statistically indistinguishable from a random
walk. The favourable side compounds faster — and the asymmetry **grows with hold
time**: P80 MFE / P80 MAE runs 1.09, 1.10, 1.08, 1.18, 1.32 at 50/100/200/400/800
bars. There is no asymmetry at short holds.

Everything below follows from that, and so does every exit result in this repo:

- **H75 (CONFIRMED, three independent confirmations):** any fixed profit target
  degrades a trailing system. Monotonic in take size — 25/40/50/60% off at a
  target gave PF 1.102/1.050/1.028/1.017 against **1.134 with no target**, with
  drawdown rising 27.4% → 45.1% simultaneously. Rescaling the target grid did not
  rescue it.
- **The uploaded AU200 archive reproduced it independently:** TP1 at an EMA8
  pierce gave 14.6% WR and −$427,792; holding the same signals to end of day gave
  83.3% and **+$1,170,926**.
- **H79:** closing 75% at the nearest drawn level improved results **on the
  counter-trend (short) side only** — train PF 1.244 → 1.289, OOS 1.580 → 1.610.
  Doing it on **both** sides collapsed the full period to PF 1.023.

> **The mechanism, stated once:** any profit-taking device removes exactly the
> position size that would have captured the large move. It can therefore only be
> applied where there is no large move to capture — the counter-trend side.

### 2.2 Target selection — corrected

Determine the **Primary Draw** before entry, from this ranked list:

1. Opposing side of the same ranked HTF level that was swept (swept PDL → target PDH)
2. Untested Prior Day High/Low or Prior Week High/Low
3. Opposing session extreme (Asia high/low, London high/low)
4. Equal highs / equal lows (unmitigated)
5. Nearest unfilled HTF (1H/4H) Fair Value Gap
6. Daily / 4H opening price if untouched

**CORRECTION to v1.0.** v1.0 says "take the nearest qualifying pool," then applies
the R gate. That ordering systematically selects the closest target and is the
exact structure of **BUG-017**, where a "next key level" target sat a median
0.46 ATR away against a 6 ATR stop — risking 6 to make 0.46, at PF 1.385 → 0.702
live. No hit rate rescues that.

```
CORRECTED RULE:
  Walk the ranked list outward. The Primary Draw is the NEAREST pool that
  CLEARS the minimum-R gate. If no pool in the list clears it -> NO TRADE.

MINIMUM-R GATE (non-negotiable):
  R_available = |PrimaryDraw - ENTRY| / RISK
  Type R (reversal):     R_available >= 2.5
  Type C (continuation):  n/a — Type C has no target (see §2.3)

OBSTRUCTION CHECK (corrected):
  If an opposing ranked level of EQUAL OR HIGHER rank sits between entry and
  the Primary Draw, that level becomes the Primary Draw; re-run the gate.
  Lower-ranked levels do not promote.
```

The rank qualifier on the obstruction check is new. v1.0's unqualified version
promotes any intervening level, which on a 5m chart against a dense level set
walks the target straight back into BUG-017's failure geometry.

**Mandatory pre-ship arithmetic (BUG-017 prevention, verbatim from the registry):**
before this rule is coded or traded, compute the **median entry-to-target
distance in ATR** and the **median stop distance in ATR** across the signal
population. **State the ratio in the RESULTS_LEDGER row.** If target/stop < 1.0
the structure is losing before a single trade is placed. Also count the levels:
`array.size(klPrices)` versus the research port's level count — the research
engine in BUG-017 modelled 18 of 36 levels and that discrepancy hid the defect.

### 2.3 Scaling — type-asymmetric (the main correction)

v1.0 offers Schedule A (no partials) and Schedule B (40/35/25 scale-out) and
applies the choice to the whole system. **That is the wrong axis.** The repo's
evidence says the correct split is not "expectancy vs variance" but
**counter-trend vs with-trend**.

#### Type R (reversal — counter-trend, fading a swept HTF level)

```
TYPE R EXIT:
  100% of position exits at the Primary Draw (§2.2), or at the stop.
  Stop management per §2.4. No partials, no trailing before 2R.
```

A hard level target is **correct** here and is supported by H79: this is the
counter-trend side, where there is no large move to capture and banking at the
opposing pool measurably improved both halves of a 6.7-year sample. v1.0's
Schedule A is right for Type R.

#### Type C (continuation / expansion — with-trend)

```
TYPE C EXIT:
  NO fixed target. NO partials. NO Primary Draw requirement.
  Exit is the trailing stop alone (§2.4.3), armed from entry.
  Trail width: to be solved per instrument in validation (§7).
  Prior: gold's measured optimum on a 15m trend engine is 4.24-5.0 ATR
  and PF is HUMP-SHAPED, not monotonic in width.
```

**This overturns v1.0's §2.2 min-R gate of 2.0R/2.2R for continuations, and its
Schedule B runner mechanic, for Type C only.** Applying a target to the
with-trend side is the single most reliably negative intervention measured in
this repository — H75 at four take-sizes and four grid scales, H79's both-sides
collapse to PF 1.023, BUG-017 live, the AU200 archive's −$427k vs +$1.17M, and
the mechanism explained by the exponent gap. Five independent confirmations.
There is no result anywhere in this repo on the other side of it.

**On the trail width prior:** a previously-cited claim that "wider trailing stops
are monotonically better" (2/6/14 ATR → PF 1.05/1.60/1.75) was **RETRACTED**
2026-08-03 — it does not reproduce. The true shape is a hump peaking at 4.24–5.0
ATR (PF 1.646 at 4.24 vs 1.164 at 3.0 and 1.429 at 6.0). Trails inside the noise
band still destroy the system; the extrapolation to ever-wider trails is dead.
**Do not inherit 4.24 for NQ or for a 5m timeframe — solve it, and expect a hump.**

#### If a prop-firm trailing drawdown makes an unbanked Type C untradeable

That is a legitimate constraint, and it is a *funding* constraint, not an edge
claim. Handle it honestly: **do not trade Type C**, or trade it at reduced risk.
Do not add a target to it and call the result the strategy's expectancy — v1.0
estimates the give-up at 15–25% of PF; this repo measured it at 40–90% of *net*
on the cases above. Quantify it on your own data before choosing.

### 2.4 Stop management

#### 2.4.1 Break-even

```
MOVE TO BREAK-EVEN only when BOTH:
  (a) Unrealised >= 1.2R (NQ) / 1.3R (GC), AND
  (b) A new swing point has formed in trade direction on the execution TF
      (long: a Higher Low holding >= 2 closes; short: a Lower High)

Then: SL -> (new swing point -/+ BUFFER), which will be at or better than BE.
NEVER move SL to the exact entry price.
```

Adopted from v1.0 and independently supported. A retest entry sits at the origin
of displacement; price returning to that origin is normal behaviour, not
invalidation, so mechanical 1R-to-BE scratches valid trades. **BUG-020** is the
same failure in its purest form: a give-back trail that armed at zero excursion
snapped to breakeven on bar two and produced a **1% win rate over 2,307 trades** —
which looked like a bad idea rather than the bug it was. Any stop rule defined as
a function of profit must state what it does at zero profit; evaluate it by hand
at entry before running it.

#### 2.4.2 Time stop — RECLASSIFIED to hypothesis

```
HYPOTHESIS (not yet a rule):
  If R_achieved < 0.5R after 12 bars (NQ) / 15 bars (GC)
  AND no new swing has formed in trade direction
  -> EXIT AT MARKET.

  Applies to TYPE R ONLY. Do NOT apply to Type C.
```

v1.0 asserts this "typically removes 12–20% of trades and improves PF more than
any entry filter." That may well be true for a counter-trend setup where a valid
raid resolves quickly. But it runs directly against the exponent-gap finding —
the MFE/MAE asymmetry that *is* the edge does not exist at short holds and only
emerges with time (1.09 at 50 bars → 1.32 at 800). A time stop is a mechanism for
capping hold time, and this repo's central measured finding is that hold time is
where the money is.

The two are reconcilable: the time stop is conditioned on *structure* (`AND no
new swing formed`), so it cuts dead trades rather than developing ones. But the
burden of proof sits with the time stop, not against it.

**Required before this becomes a rule:** ablate it (§7). If ΔPF < 5%, delete it.
Never apply it to Type C, whose entire edge is hold time.

#### 2.4.3 Structure trailing

```
TYPE R: no trail below 2R. Above 2R, on each new CONFIRMED swing:
          SL -> swing point -/+ BUFFER
TYPE C: trail armed from entry (this IS the exit).

Trail on CLOSED swings only. Never trail intrabar.
```

**"Never trail intrabar" is not style advice — it is BUG-019.** An exit engine
that updated the running excursion from bar *i*'s own high *before* resolving the
stop on bar *i* reported PF 1.183 at 45.2% drawdown where the true configuration
was PF 1.635 at 17.01%. The stop got to see the bar's high before deciding
whether the bar's low took it out.

**Mandatory order of operations in any implementation:** (1) move the stop using
data through bar *i−1*; (2) resolve bar *i*; (3) update state with bar *i*. Any
state a stop depends on must be one bar stale. This ordering is load-bearing and
must carry a comment saying so.

#### 2.4.4 Session-end flat

```
NQ: flat by 15:45 ET unless >= 2R and trailing.
GC: flat by 13:30 ET (COMEX floor close) unless >= 2R and trailing.
ABSOLUTE: no position held through the 17:00 ET maintenance break.
```

*Correction to v1.0:* the COMEX gold floor close is **13:30 ET**, not 13:00.
v1.0's own §4.2 session table is internally consistent with 13:30.

**Note the tension with §2.1, and hold it consciously.** A session-end flat is a
time stop by another name, and the exponent gap says hold time pays. It is
retained because overnight gap risk bypasses stops entirely (**BUG-032** — stop
fills not gap-aware) and because this is a defined intraday system. But if Type C
validates, "hold Type C overnight with a gap-aware stop" is the first extension
worth testing, and it should be tested rather than assumed away.

---

## PART 3 — RISK AND POSITION SIZING

### 3.1 Base risk

```
A-grade (score >= 8):   0.50% of account
B-grade (score 6-7):    0.25% of account
Score < 6:              NO TRADE
```

No C-grade, and **no size above 0.50%**. Confirmation strength reduces size; it
never increases it. This is asymmetric on purpose: confidence is a poor predictor
of outcome, while the *absence* of confirmation is a reliable predictor of
degraded outcome.

**The magnitude is confirmed by measurement, and the method is an upgrade on
v1.0.** G1* did not assert a risk figure — it solved for one against a stated
drawdown budget using 5 seeds × 5,000 Monte Carlo paths: **0.606% at a 25% DD
budget, 0.475% at 20%**. v1.0's 0.50% lands inside that band, which is
reassuring, but the method is what should be inherited:

```
STANDING METHOD: state the max-drawdown budget FIRST, then solve risk% to it
by Monte Carlo on the validated trade distribution. Do not assert a risk %.
```

**Two live conflicts inside this repo, flagged rather than silently resolved:**

1. **`COGNITIVE_ARCHITECTURE.md` §Profit Engine 2 assigns 1–2% to A setups and
   2–4% to A+ setups.** That is 4–8× the figure both v1.0 and G1*'s Monte Carlo
   arrive at. The repo's own measured note on the MTI material is blunt: *"never
   risk more than 2–5% per trade" would have destroyed the account.* **v2.0 sizes
   at 0.50% max.** COGNITIVE_ARCHITECTURE's conviction-sizing table should be
   amended to the DD-budget method.
2. **`COGNITIVE_ARCHITECTURE.md` §Profit Engine 5 mandates a scale-out protocol**
   (1/3 at 1R, 1/3 at 2R, 1/3 runner). H75 CONFIRMED, H79, BUG-017, the exponent
   gap and the AU200 archive all contradict this on the with-trend side. It is
   defensible for Type R only. **The word "Mandatory" in that heading is not
   supported by anything measured here** and should be qualified.

### 3.2 Confirmation multipliers (multiplicative on base)

**NQ:**

| Condition | Multiplier |
|---|---|
| VIX inverse + reacting from a level, AND Mag7 ≥ 5/7 | 1.00 |
| One leg partial (VIX inverse but not at a level, OR Mag7 = 4/7) | 0.50 |
| Both legs partial | 0.00 — no trade |
| Mag7 ≥ 5/7 but NVDA, MSFT and AAPL all against direction | 0.00 — no trade |
| VIX > 28 absolute, or VIX intraday change > +8% | 0.50, reversal-only |
| VIX > 35 | 0.00 — regime break; retests fail in panic tape |

**GC:**

| Condition | Multiplier |
|---|---|
| DXY inverse-confirmed AND Silver aligned | 1.00 |
| One of the two only | 0.50 |
| Neither | 0.00 — no trade |

### 3.3 Position size

```
Contracts = FLOOR( (Account * Risk%) / (RISK_points * PointValue) )

NQ: PointValue = $20   (MNQ = $2)
GC: PointValue = $100  (MGC = $10)

Contracts == 0        -> use the micro contract
Contracts_micro == 0  -> NO TRADE. Never round up.
```

**On the observed 40-contract NQ size.** At $20/point, 40 NQ contracts is $800
per index point; against a representative 45-point stop that is **$36,000 of risk
on one trade**. At 0.50% risk that implies a ~$7.2M account. If the account is
not of that order, the observed size is a simulated/prop-evaluation account or
the trader is running 5–20× the risk specified here. **Copy the logic, derive the
size from your own equity.** Position size is the one variable in this framework
that must never be inherited from someone else's screenshots — v1.0 is exactly
right about this and it deserves repeating.

### 3.4 Loss limits

```
DAILY
  Max loss:          -1.5R  (= 0.75% at base risk)
  Max full stops:     2 consecutive -> stop for the day
  Max trades:         3 total, max 2 per instrument
  After 1 full stop:  next trade must be A-grade only

WEEKLY
  -4R -> half size for the remainder of the week
  -6R -> flat for the week

MONTHLY
  -6% -> stop, full system review, no discretionary override

OPEN RISK
  Total concurrent open risk <= 1.0R across all instruments.
  NQ and GC driven by the same catalyst (CPI, FOMC, NFP, geopolitical/energy)
  count as ONE position for this limit.
```

The 3-trade daily cap is a **quality** mechanism, not a discipline mechanism:
setup quality degrades sharply with count, because the fourth setup of a day is
almost always a lower-ranked level in a worse session window.

**Implementation note — BUG-016:** these counters must increment on **fills**,
not on signals. A registered bug in this repo had the daily cap throttling trades
that were never actually filled.

---

## PART 4 — EXECUTION TIMEFRAME AND SESSION FILTERS

### 4.1 Timeframe stack

```
BIAS / LEVELS:  Weekly, Daily
INTERMEDIATE:   4H, 1H     (level ranking, dealing range, premium/discount)
EXECUTION:      5m         (sweep, MSS, displacement, FVG)
REFINEMENT:     1m         (fill placement and SL precision ONLY)
```

5m is the right execution timeframe for this style: 1m produces too many false
MSS events (displacement thresholds become meaningless), 15m loses retest
granularity because the FVG is often filled inside one candle, so entry and stop
cannot be separated cleanly. **Never define structure on 1m.**

**Escalation rule:** when the swept level is Weekly or Monthly rank, confirm the
MSS on 15m and execute the retest on 5m. Bigger pools require proportionally
bigger structural confirmation.

**⚠ A practical blocker on the timeframe choice, stated because it decides
whether this system can be validated at all.** The user's profile records
*TradingView free plan: ~2 months of 5m history*. §7 requires ≥200 trades per
instrument **per type**. A filter stack that removes 30–40% (FVG) plus 12–20%
(time stop) of raw signals will not produce 400 NQ trades in two months of 5m
data — the requirement is closer to 18–24 months per instrument.

**Consequence: this system cannot be validated on TradingView.** It must be
validated in `backtest/` on imported 5m data, using the Python harness that is
already cross-validated against Pine (identical trade count and win rate, PF
within 0.017). Sourcing ≥2 years of 5m NQ and GC data is a **prerequisite**, not
a detail — and it should be settled before any Pine is written.

### 4.2 Session windows (all times ET)

**NQ:**

| Window | Rating | Notes |
|---|---|---|
| 02:00–05:00 | B | London raids on the Asia range; lower follow-through |
| 08:30–09:20 | C — conditional | Post-data only; requires a CLOSED 5m candle after the print |
| 09:30–11:00 | **A — primary** | NY AM. Highest displacement quality, deepest liquidity |
| 10:00–11:00 | **A+** | Highest-conviction sub-window for reversals |
| 11:00–12:00 | B | Continuation only |
| 12:00–13:30 | **F — no trade** | Lunch. Structure unreliable, displacement fake |
| 13:30–15:00 | B | PM; continuation preferred |
| 15:00–15:45 | C | Manage only; no new entries after 15:30 |

**GC:**

| Window | Rating | Notes |
|---|---|---|
| 03:00–06:00 | **A — primary** | London open. The Asia-range sweep is gold's canonical setup |
| 08:20–11:00 | **A — primary** | COMEX open through NY AM |
| 09:55–10:05 | **F — no entry** | LBMA PM fix; non-structural spikes |
| 11:00–13:30 | C | Manage only |
| 13:30–03:00 | **F** | Illiquid, wick-driven, stops unreliable |

**This is the best-supported filter in the entire document for gold.** B1 in the
belief register — *"session filter is the strongest edge lever on XAUUSD 5m"* — is
HIGH conviction and has been confirmed three times, including from this repo's
own data: the same trendline logic scored **PF 0.85 traded 24/7 and PF 3.656
restricted to London + NY-open**. TEST #1 diagnosed the failure mode precisely:
the session was built as a **+2 score contributor rather than a hard gate**, so
the engine traded 24h and off-session B-grades diluted the edge.

```
STANDING RULE: the session filter is a GATE, never a score contributor.
```

Note the session windows that produced B1's result (03:00–05:00 and 08:30–11:00
NY) are close to but not identical with v1.0's GC A-windows (03:00–06:00,
08:20–11:00). Resolve by measurement in §7, not by preference.

*Also note:* the 3.656 figure is from ~117 trades over ~2 months and was
**explicitly retracted by the user as evidence** — sample too small. It is kept
as the reason to re-test the session gate, not as proof of its size.

### 4.3 Hard no-trade windows (both instruments)

```
- FOMC statement day: no entries 13:45-15:30 ET
- CPI / PPI / NFP / Core PCE: no entries until a 5m candle has CLOSED
  after the print (08:35 or 08:45 ET at the earliest)
- First 5 minutes of the cash open (09:30-09:35)
- Sunday reopen 18:00-20:00 ET
- Daily maintenance break 17:00-18:00 ET
- Contract rollover day and the session prior
- US half-days and the session before major US holidays
- Fed Chair testimony windows
- GC additionally: scheduled OPEC and major geopolitical/energy headlines
```

**Supported by B3 and B4.** A matched study of 7 CPI events 2025–2026 found
follow won 3, fade won 2, muted 1, unclear 1 — *"CPI direction is unknowable
pre-print; the tradeable edge is post-spike."* The framework requires a sweep
with rejection and a **closed-candle** MSS; a data spike produces the visual
signature of both without the underlying auction mechanic. Waiting one closed 5m
candle costs a small number of good trades and removes a large number of
catastrophic ones.

---

## PART 5 — ROBUSTNESS FILTERS

Each is objectively testable and **each must survive ablation in §7.** v1.0's own
standard — *any filter contributing <5% PF improvement is complexity without
edge; delete it* — is correct and is adopted as binding.

### 5.1 Displacement quality (mandatory)

```
The MSS candle (or 2-candle displacement leg) must satisfy ALL:
  1. Range >= 1.5 * ATR_X
  2. Body / Range >= 0.60
  3. CLOSES beyond the broken structure point (not merely wicks through)
  4. Volume >= 1.4 * SMA(volume, 20)      [futures volume is reliable; use it]
```

Criterion 3 is not optional and is the guard against **BUG-035** — see §6.

### 5.2 Fair Value Gap requirement (mandatory)

```
The displacement leg MUST leave an unfilled FVG on the execution TF.
FVG width >= 0.20 * ATR_X.
No FVG -> NO TRADE.
```

**Rationale (v1.0's, and it is a good one):** an imbalance is the objective
footprint of aggressive, size-driven order flow. A structure break with no
imbalance is driven by absorption or by withdrawal of passive liquidity —
mechanically a different event with a materially worse forward distribution.

v1.0 claims this removes 30–40% of raw signals and is where most of the
improvement comes from. **That is the single most valuable testable claim in the
document and it has never been tested here.** It is the first ablation to run.

### 5.3 Sweep quality

```
1. Depth: 0.25-0.40 * ATR_D beyond the ranked level.
   HARD CAP: > 0.55 * ATR_D is a breakout, not a sweep -> stand aside.
2. Rejection: sweep candle closes back inside the level within 3 bars.
3. Speed: sweep -> MSS within 9 bars (NQ) / 12 bars (GC).
   A slow grind through a level is distribution, not a raid.
4. The swept level must be a DOCUMENTED ranked level from Step 1.
   Arbitrary swing points do not qualify.
```

**A measured caution on the sweep premise itself.** `backtest/level_claims.py`
tested sweep-and-reclaim over 81,396 XAUUSD touches. The phenomenon is **real** —
33.13% hit rate vs 27.99% baseline — but **it loses its entire advantage to the
wider entry-to-stop distance a sweep bar creates.** The same battery also found
that *untested-beats-retested is false* and *confluence-is-stronger is false and
slightly backwards*, both of which this framework relies on (Step 1 ranking,
§5.7 criteria 1–2, and the §5.7 confluence override).

That is not fatal — this framework enters on the **retest**, not on the reclaim
bar, which is precisely the mechanism that would recover the lost entry-to-stop
distance, and that is the sharpest reason to believe the retest requirement is
load-bearing. But it means **the framework's own premises have been measured
here and two of the four came back negative.** Rules 1, 2 and 4 above, and §5.7
criteria 1 and 2, must each earn their place by ablation rather than by
inheritance.

### 5.4 Retest quality

```
1. Retracement into the displacement leg: 50%-79% (equilibrium to OTE)
2. Retrace > 85% of the leg before entry -> INVALIDATE
3. At least one CLOSED candle with wick rejection into the zone.
   No blind limit fills.
4. Expiry: no retest within 15 bars of the MSS -> setup is dead.
```

**Rule 3 carries a lethal backtest hazard — see §6, BUG-035.** "Limit at the FVG"
and "closed rejection candle" are each individually defensible and are a
**lookahead when combined in a backtest**: filling at the zone price only on bars
whose close later proves rejection silently excludes every bar that touched the
zone and kept going. In the AU200 work this reversed the sign of 36 of 36
configurations — PF 1.166 (+11,746) became PF **0.663 (−31,860)**.

Live, you must choose one, and the two are different strategies:
- **(a) Resting limit at the FVG boundary** — no rejection candle required, worse
  average fill quality, no lookahead. Backtestable honestly.
- **(b) Market on the close of the confirmed rejection candle** — worse price by
  construction, but real.

**Rule: backtest both; ship the worse of the two.**

### 5.5 Correlation confirmation

**VIX rule, made non-discretionary (NQ):**

```
For an NQ LONG, within the 30 min preceding entry, VIX must:
  (a) sweep a prior swing HIGH on its own 5m chart, AND
  (b) print a bearish MSS (break of a prior swing low), AND
  (c) be reacting from a documented VIX level (prior day high, 1H/4H supply)
Mirror for shorts. Anything less = "partial" -> 0.50x.
```

**Mag 7 breadth, made non-discretionary (NQ):**

```
For each of AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA, score 1 if BOTH:
  - price is on the trade side of its session VWAP, AND
  - price is on the trade side of its prior day close
Require >= 5/7.
VETO: if NVDA, MSFT and AAPL are ALL against direction -> no trade
      regardless of count.
Optional: weight by index weight, require weighted score >= 0.55.
```

The top-3 veto is the important half. These three carry the plurality of index
weight, so an unweighted 5/7 can pass while the actual index driver opposes.

**GC substitutes — closing the gold gap.** GC has no VIX and no Mag 7. Gold's
directional drivers are the dollar and real yields, with silver as the breadth
analog:

```
1. DXY inverse confirmation (primary, replaces VIX):
   DXY must sweep its own opposing level and print an inverse MSS within
   the same 30-min window. Same standard as the VIX rule.
2. Silver (SI) alignment (replaces Mag 7):
   SI on the same side of its session VWAP and prior day close.
   GC/SI divergence at a level is the single most reliable warning that a
   gold "sweep" is a genuine breakout.
3. Yield check (regime, not trigger):
   ZN/ZB direction. Yields moving hard against the trade -> 0.50x.
```

**This is the largest unvalidated block in the document and it is worth real
work.** The mechanism is sound and matches the Macro Architect's intermarket map
(*yields up → DXY up → gold down*), and this repo has an
`intermarket_lag_trading.md` playbook it has never tested. But there is a
specific reason for caution: the correlation is conditional on regime, and a
conditional correlation used as a hard gate fails exactly when the regime turns —
which is when it matters. Test it as a **size modifier first** (as specified) and
only promote it to a gate if the ablation supports one.

### 5.6 Range-state filter (ADR exhaustion)

```
TodayRange_so_far / ADR(20):
  < 0.50      -> continuation favoured; reversals require A-grade
  0.50-1.20   -> both permitted
  > 1.20      -> REVERSAL ONLY, no continuations
  > 1.80      -> no new entries
```

Range exhaustion is one of the few genuinely stationary intraday effects.
Continuation trades taken after 1.2× ADR has printed have materially worse
forward distributions because the remaining distance to the day's realistic
extreme is compressed.

*Untested here, but note one adjacent negative:* this repo measured that **the
opening range does not carry special information on two instruments**. ADR
exhaustion is a different quantity from the opening range, so that result does
not refute it — but it is a caution against assuming intraday range statistics
are informative by default.

### 5.7 Setup grading rubric (10 points)

≥8 = A (full size), 6–7 = B (half size), <6 = no trade.

| # | Criterion | Pt |
|---|---|---|
| 1 | Level rank: Weekly/Monthly untested = 1; Daily zone or PDH/PDL = 0.5; session level only = 0 | 1 |
| 2 | Level is untested (first touch) | 1 |
| 3 | HTF premium/discount aligned (long in discount / short in premium of the Daily dealing range) | 1 |
| 4 | Displacement passes all four §5.1 criteria | 1 |
| 5 | Unfilled FVG present, ≥ 0.20 ATR_X | 1 |
| 6 | Sweep→MSS inside the speed window | 1 |
| 7 | Retest in the 50–79% band with wick rejection | 1 |
| 8 | Correlation confirmation full (VIX+Mag7, or DXY+SI) | 1 |
| 9 | Session window rated A | 1 |
| 10 | R_available ≥ 3.0 to Primary Draw (Type R only; Type C scores this as trend alignment on Daily AND 4H) | 1 |

**Criteria 1 and 2 are on notice.** `level_claims.py` measured
untested-beats-retested as **false** on 81,396 XAUUSD touches. They are retained
because they may behave differently inside this filter stack, but if the ablation
shows they contribute nothing, **delete them** rather than defending them.

**Confluence stack bonus — DOWNGRADED.** v1.0 permits a B-grade entry at a score
of 5 when ≥3 independent ranked levels coincide within 0.15 ATR_D, calling
multi-level confluence "the single strongest observable predictor of reaction
quality." **This repo measured the opposite:** confluence-is-stronger came back
**false and slightly backwards** over 81,396 touches, and the follow-up idea of
using confluence count as a regime variable was explicitly killed —
*"It was speculation and it is now measured and negative."*

```
CORRECTED: the confluence override is REMOVED from v2.0.
Score < 6 is no trade, with no exception.
It may be reinstated only if it clears an ablation on its own.
```

This is the one place v1.0 relaxes its own gate, and it relaxes it on the single
claim this repo has most directly measured as false.

### 5.8 Reversal vs continuation — separate populations

**These are two different strategies and must be logged, backtested and
evaluated separately.** Blending them is how a system with two mediocre edges
looks like one good edge in aggregate and then fails forward.

| | **Type R (reversal)** | **Type C (continuation / expansion)** |
|---|---|---|
| Definition | Sweep of a major HTF level against the intraday trend, reversing into the range | Sweep of internal liquidity (session low, PDL, intraday swing) in the direction of the established Daily/4H trend |
| HTF bias | May oppose intraday trend; must align with Daily dealing-range premium/discount | Must align with Daily **and** 4H trend — non-negotiable |
| Level rank required | Weekly / Monthly / Daily zone / PDH-PDL only | Any documented level, including session levels |
| Min score | 8 (A), or 6 at half size | 7 |
| Correlation gate | Full confirmation required | Mag7 ≥ 4/7 (or GC: one of DXY/SI) if Daily trend aligned |
| **Exit** | **Level target at Primary Draw, min 2.5R** | **Trailing stop only — NO target, NO partials** |
| Time stop | Hypothesis, Type R only | **Never** |
| ADR state | Preferred > 1.2× ADR | Required < 1.2× ADR |
| Session | A-windows only | A or B |
| Stop anchor | Beyond sweep extreme (and OB origin) | Beyond FVG origin / last opposing candle |
| Expected profile | Lower WR, capped R | **Lower WR, uncapped right tail** |

The exit row is the v2.0 correction and it is the reason the two types must be
separated: **they require structurally opposite exit engines.** v1.0 separates
them on entry criteria but gives them the same exit architecture, which is the
error H75/H79 identify.

Note the corrected expectation for Type C. v1.0 predicts "higher WR, lower R" for
continuations. Under a pure trailing exit, expect the opposite — a **low win rate
with a long right tail**. The repo's gold trend engine runs ~21.7% win rate at
PF 2.157. **A high win rate on Type C is a bug signature, not success** — the
standing harness assertion is that WR below 10% or above 90%, or trades exceeding
~25% of bars, is a bug until proven otherwise (BUG-033).

### 5.9 Absolute vetoes (any one = no trade)

```
- Level tested more than twice
- Sweep depth > 0.55 ATR_D
- No unfilled FVG
- Required stop breaches the ATR_D cap
- R_available below 2.5 (Type R)
- Daily/4H trend not aligned (Type C)
- Inside a hard no-trade window
- Outside a rated session window
- Daily loss limit or trade count reached
- Score < 6  (no confluence exception — see §5.7)
- Mag7 top-3-by-weight veto (NQ) / GC-SI divergence at the level (GC)
```

---

## PART 6 — IMPLEMENTATION HAZARD MAP

Every rule above mapped to the registered bug most likely to be reproduced while
coding it. **Per `CODE_DELIVERY_PROTOCOL.md`, new code is checked against
`BUG_REGISTRY.md` before delivery; this table is that check, pre-computed.**

| Spec rule | Bug it will reproduce | Guard |
|---|---|---|
| §1.2 stop placement | **BUG-005** stop referenced the swept LEVEL not the sweep EXTREME (12/12 losses) | Reference the sweep bar's actual wick; desk-check the entry bar |
| §1.2 long/short symmetry | **BUG-022** asymmetric edit — one direction updated, the other stale | Diff the two branches character-by-character |
| §1.5 cap as reject | **BUG-009** hard-reject killed valid setups | Reject *only* on retest entries; cite §1.5 in the comment |
| §2.2 target selection | **BUG-017** target closer than the noise (PF 1.385 → 0.702) | Report median target/stop ratio in ATR in the ledger row; count levels on both sides of the port |
| §2.4.3 trailing | **BUG-019** intrabar lookahead — excursion updated before the stop check (DD 17% → 45%) | State the order of operations; stop state must be one bar stale |
| §2.4.1 BE / any profit-function stop | **BUG-020** trail arming at zero excursion → 1% WR over 2,307 trades | Evaluate the formula by hand at entry |
| §5.4.3 retest fill | **BUG-035** fill at a level only the confirming close proves was reached (36/36 configs flipped negative) | Report every config at-level, at-close and at-next-open; **ship the worst** |
| §5.4 "price was previously beyond X" | **BUG-015** rolling extreme includes the current bar, so "retest" needs no break | Any such extreme carries a `[1]` offset |
| §3.4 daily counters | **BUG-016** counters incremented on signals, not fills | Increment on fill only |
| Cost model | **BUG-021** Pine `slippage` is in TICKS (~40× under-modelling) | Compute `slippage_input * syminfo.mintick`; confirm it is the intended POINTS, per symbol |
| Any trailing stop in Pine | **BUG-036** `trail_points`/`trail_offset` are in ticks and their roles swap easily | Unit-check both |
| Step 1 weekly/monthly levels | **BUG-024** yearly high/low leak future data in the key-levels module | Verify the module's lookahead guards |
| Session gating | **BUG-037** fixed UTC offsets ignore DST | Use exchange time; test across a DST boundary |
| Overnight / gap | **BUG-032** stop fills not gap-aware | Fill gapped stops at the open, not the stop price |
| Backtest stop fills | **BUG-018** every stop filled exactly at the stop price | Model adverse fills |
| Sizing in Pine | **BUG-012** silent order rejection — risk sizing vs default 100% margin | Use `strategy.percent_of_equity`; verify orders are not silently rejected |
| Re-entry after a stop | **BUG-033** signal state unaware the stop fired → n=4,585, WR 0.2% | WR <10% or >90%, or trades >25% of bars, is a bug until proven otherwise |

**Additional standing requirement:** per `CLAUDE.md`, any strategy or indicator
built in this repo must embed `trader_playbooks/skills/key_levels_module.pine`
**verbatim** (BUG-013 — three rewrites were rejected). Host must be Pine v6,
`overlay=true`, `max_lines_count`/`max_labels_count` ≥ 500.

---

## PART 7 — VALIDATION PROTOCOL v2

v1.0 §8's acceptance gates are adopted. **Three controls are added, and their
absence is the most likely way this framework fails silently.**

### 7.1 Acceptance gates (from v1.0, adopted)

| Gate | Threshold |
|---|---|
| Sample size | ≥ 200 trades per instrument, **per type** |
| Out-of-sample | ≥ 30% of data, never touched during tuning |
| Profit factor (OOS) | ≥ 1.50 |
| Expectancy | ≥ 0.25R per trade |
| Max consecutive losses | ≤ 8 |
| Max drawdown | ≤ 12R |
| Parameter sensitivity | PF > 1.25 across ±25% perturbation of **every** ATR multiple |
| Regime stability | Positive expectancy in ≥ 3 of 4 annual sub-periods |

### 7.2 THE THREE ADDED CONTROLS (mandatory, and this is the section that matters)

**Control 1 — Matched random-entry null. Run this FIRST.**

```
Take the validated exit engine. Replace the entry with a random entry
matched on: count, direction distribution, session window, and instrument.
Run the identical exit engine over it.

IF the sweep entry does not beat its matched random null OUT OF SAMPLE,
the entry rules contribute nothing and the result belongs to the exits.
```

**This is not a formality. It is the outcome this repo has obtained seven times
out of seven.** H78 tested level-touch entries across three separation gaps and
18 levels on 157,366 bars: *"With costs set to zero, every configuration still
lands on PF 1.00."* The random-entry null produced the same verdict for the
breakout engine from the opposite direction. The with-trend level study's own
matched control **scored higher than the level entries in all four comparisons**.
The exponent-gap finding explains why: the entry contributes an exponent of
0.493 against a random walk's 0.500.

The repository's standing conclusion is: **entry rules on this instrument do not
carry edge; exits do.** This framework's whole thesis is that a *stacked,
conditional* entry (sweep + MSS + FVG + retest) is different in kind from the
single-condition entries that have failed here. That thesis is testable in one
run, and it should be the first run, because everything downstream is wasted
effort if it fails. **Beware BUG-023 — a null hypothesis that skipped the filters
it was testing is not a null.**

**Control 2 — Three-execution reporting (BUG-035).**

```
Every configuration reports under THREE fill assumptions:
  at-level, at-close, at-next-open.
If they disagree materially, the at-level number is NOT a result.
SHIP THE WORST OF THE THREE.
```

BUG-035's warning is explicit and it applies directly to §5.4: *the synthetic
null, the mirror control, the parameter plateau and the IS/OOS split were all
computed with the SAME biased fill, so the bias applied uniformly and every
control passed.* **Control 1 cannot detect the problem Control 2 catches.** Both
are required.

**Control 3 — Identity arm.**

```
Build into every sweep an arm whose answer is already known, and verify
it reproduces the reference result EXACTLY.
```

From the G1*/volatility-targeting session, where an apparent improvement turned
out to be a plumbing change and not the effect being tested: *"Build an arm whose
answer you already know into every sweep. It cost one row and it separated a real
effect from a plumbing change."*

### 7.3 Cost model (specified, not assumed)

```
NQ: commission + 1 tick slippage per side minimum. Stress at 2x.
GC: commission + 1 tick slippage per side minimum. Stress at 2x.
Pine: slippage is in TICKS -> compute slippage_input * syminfo.mintick
      and confirm the resulting POINTS figure per symbol (BUG-021).
Headline result = the 2x-slippage number, not the frictionless one.
```

The repo's convention is to report at 2× slippage. A result that only survives at
1× is not shipped.

### 7.4 Required diagnostics

- **MAE distribution** — directly validates or refutes §1. If the 90th percentile
  of MAE on *winning* trades exceeds the buffer, the buffer is too tight. **Do
  not use the "optimal stop from the 80th percentile of MAE" method** — this repo
  measured it as not a market property: it tracks the measurement parameters
  (measurement stop 12/25/50 ATR yields 12.85/25.40/34.33; hold cap
  50/100/400/800 bars yields 6.5/9.1/17.1/26.3 ATR). Use MAE to *falsify* a
  buffer, never to derive one.
- **MFE distribution** — validates §2. Report the exponent gap per type. **If Type
  C's MAE exponent is not materially below 0.49, its entry has no geometric edge
  and the trail is the whole system** — which is a valid outcome, but it must be
  stated, not hidden.
- **Filter ablation** — remove each §5 filter individually, measure ΔPF. **<5%
  contribution → delete it.** Priority order: §5.2 FVG (v1.0's headline claim),
  §5.7 criteria 1–2 (measured false elsewhere), §2.4.2 time stop (contradicts the
  exponent gap), §5.5 correlation gates.
- **Type separation** — Type R and Type C must **each** clear the gates
  independently. Do not trade the blend.
- **Down-period check** — evaluate every directional parameter against gold's
  down years in isolation. *"Gold rose 1450 → 4100 across this sample. Any
  parameter that reduces short exposure will therefore test well, and will test
  well for a reason that has nothing to do with edge."*
- **Top-10 concentration** — report net profit excluding the ten best trades. The
  repo has shipped systems where this ran to 70%, and rejected one at 199%
  (it lost money net of its ten best trades).

### 7.5 Known failure modes

1. **Over-fitting ATR multiples to one volatility regime.** Gold ran 3,353 →
   5,627 → 4,450 inside twelve months. Anything tuned on the Q1 high-vol period
   fails in Q3.
2. **Survivorship in the screenshot sample.** The observed trades are the ones
   that were taken *and shared*. They are not a random draw from the setup
   population, and the 40-contract size in particular must not be inherited.
3. **Session blending.** Validate per session window, not in aggregate.
4. **A documented number is not evidence.** *"A number quoted inside a shipped
   artefact's own header is not evidence"* — a trailing-stop claim survived three
   sessions and two planning documents in this repo before anyone re-ran it, and
   it did not reproduce. **Every number in v1.0's §0 Premise C is in this
   category** — the price levels, the ATR estimates and the 25.5% realized-vol
   figure are unverified, and the ATRs must be recomputed daily regardless.
5. **Chasing a rising slope.** If a parameter's metric is still improving at the
   edge of the tested range, take the conservative point below it. Pushing to the
   peak is re-optimisation.

---

## PART 8 — WHAT IS ACTUALLY UNVALIDATED, RANKED

Honest status. **Nothing in this document has been tested.** Ranked by how much
of the framework collapses if the item fails:

| # | Item | If it fails |
|---|---|---|
| 1 | **The stacked entry beats a matched random null** (§7.2 Control 1) | The whole framework is an exit engine with decorative entry rules. Seven of seven prior entry families here have failed this. **Run it first.** |
| 2 | **Type C survives with no target** (§2.3) | Type C is untradeable under a prop drawdown constraint and the system is reversal-only |
| 3 | **The FVG filter earns its 30–40% rejection rate** (§5.2) | v1.0's headline claim is wrong and the filter stack is over-fitted to narrative |
| 4 | **≥2 years of 5m NQ and GC data can be sourced** (§4.1) | The system cannot be validated at all. **This is a prerequisite, not a task.** |
| 5 | **GC's DXY/Silver substitute works** (§5.5) | Gold trades at 0.50× permanently, or Step 5–6 is dropped for GC |
| 6 | **The time stop contributes ≥5% PF** (§2.4.2) | Delete it — it contradicts the exponent gap and must earn its place |
| 7 | **NQ behaves like the gold results at all** | Every NQ parameter must be re-derived. **This repo has measured cross-instrument transfer failing (1.82 → 0.49).** |
| 8 | Session windows match B1's measured windows (§4.2) | Re-derive by measurement; the difference is small but must be resolved by data |

---

## PART 9 — WHAT THE MEASUREMENT CHANGED

Run 2026-08-12. Full numbers in RESULTS_LEDGER; this is what they mean for the
rules above.

### 9.1 The three rules that must change before this is run again

**(a) The sweep-depth rule and the stop rule cannot both stand (§5.3.1 vs §1.2).**
Measured median RISK is 0.38–0.63 ATR_D against a cap of 0.32–0.35, because
RISK ≈ 0.5 × leg + buffer and the measured median leg is 0.50–1.06 ATR_D. Exactly
one of these is possible:

1. **Shallow the sweep** — read §5.3.1's "0.25–0.40 ATR" as **ATR_X**, not ATR_D.
   Measured median sweep depth then falls from 0.29 to 0.04 ATR_D and pass rate at
   the gate roughly doubles. This is almost certainly the intended reading: the
   original framework says "0.6–0.8 **Daily** ATR" for proximity and plain "ATR"
   for sweep depth, and only the ATR_X reading produces sweeps of a size a
   liquidity raid actually is.
2. **Raise the cap** to ~0.60 ATR_D and accept roughly double the per-trade risk,
   which halves position size for the same account risk.
3. **Move the stop anchor** off the sweep extreme and onto the FVG/OB origin —
   but this is what BUG-005 punished (12/12 losses), so it is the worst option.

**Recommendation: (1).** It is the only one that does not degrade another rule.

**(b) Report PF on R-multiples, not on points, whenever sizing is risk-derived.**
Gold's best rung scores PF 1.200 on points and **0.812 on R**, with mean R
−0.0801. Points-PF silently assumes constant contract size, which contradicts
§3.3. The points figure would have shipped a losing system.

**(c) 5 null seeds is not enough to estimate a null.** The same gold rung scored
z = +2.13 at 5 seeds and **z = +0.31 at 20**. The null's own dispersion was
under-estimated by 2.7×. **20 seeds minimum, and quote the actual's percentile
within the null distribution, not just z.**

### 9.2 What survived independently

- **§1.3 cluster displacement** — untouched by this result; it rests on the
  73,579-touch level-reaction measurement, not on this framework.
- **§4.2 session gating as a GATE** — untouched; rests on B1.
- **§2.3 type-asymmetric exits** — untouched; rests on H75/H79/exponent gap.
- **Execution honesty** — gold's three fill assumptions agree within 0.03R, so
  the engine has no execution lookahead. That is a property of the harness worth
  keeping.

### 9.3 The finding that generalises beyond this rule set

**Cost is the entire story on gold.** Mean R by cost multiple: **+0.0715 at ×0,
−0.0043 at ×1, −0.0801 at ×2, −0.2317 at ×4.** The raw signal has a small real
positive expectancy and the spread consumes precisely it.

This independently reproduces `level_reaction.py`'s conclusion from a completely
different direction — *the information sits precisely where the spread eats it,
and the money sits precisely where the levels stop working.* That study measured
it on level touches; this one measured it on a five-condition stacked entry built
on top of those levels. **The stacking did not move the signal out of the cost
band.** That is the sharpest reason to doubt the whole SMC-confluence family on
this instrument: adding conditions makes the population smaller without making
the per-trade edge bigger than the spread.

### 9.4 What was NOT tested, and must not be claimed

- **NQ was never tested.** No data; every vendor host is 403 at the proxy. Nothing
  here licenses a claim about NQ in either direction. US30 is a different index
  with different constituents and volatility, and this repo has already measured
  cross-instrument transfer failing (1.82 → 0.49).
- **Steps 5 and 6 were never tested.** No VIX, Mag7, DXY or Silver series. The
  measured population is a **superset** of the specified one, so the correlation
  gates could in principle remove the losers. That is the single strongest
  remaining defence of the framework and it is testable the moment those series
  are reachable — it is the first thing to run if the network policy changes.
- **The 5m NQ version specifically.** AU200 5m is the nearest evidence and it is
  the worst result of the three.

---

## APPENDIX A — EXECUTION CHECKLIST

Run in order. Any FAIL terminates.

```
PRE-SESSION
 [ ] Mark Weekly/Daily/4H levels, PDH/PDL/PWH/PWL, session extremes, D & 4H opens
 [ ] Rank each level (untested > once-tested > twice-tested)
 [ ] Compute ATR_D, ATR_X, ADR(20)          <- recompute daily, never inherit
 [ ] Identify the Daily dealing range; mark equilibrium (premium vs discount)
 [ ] Log the day's data calendar; mark no-trade windows
 [ ] Confirm account equity and today's risk budget

SETUP
 [ ] 1  Price within 0.6-0.8 ATR_D of a ranked level
 [ ] 2  Sweep 0.25-0.40 ATR_D beyond, capped 0.55; closes back inside <= 3 bars
 [ ] 3  MSS with displacement passing ALL four §5.1 criteria, inside speed window
 [ ] 3b Unfilled FVG >= 0.20 ATR_X left behind
 [ ] 4  Retest into 50-79% of the displacement leg with wick rejection, <= 15 bars
 [ ] 5  VIX inverse + at level (NQ) / DXY inverse + at level (GC)
 [ ] 6  Mag7 >= 5/7 with top-3 veto (NQ) / Silver aligned (GC)

GATES
 [ ] 7  Session window rated A or B  (GATE, not a score — see §4.2)
 [ ] 8  ADR state permits this setup TYPE
 [ ] 9  CLASSIFY TYPE R or TYPE C -> apply that column's thresholds AND EXIT ENGINE
 [ ] 10 Compute SL (§1.2), run cluster displacement (§1.3), check validity gate
 [ ] 11 TYPE R ONLY: walk out to the nearest pool CLEARING 2.5R; obstruction check
 [ ] 12 Score the setup (§5.7); assign grade.  NO CONFLUENCE OVERRIDE.
 [ ] 13 Apply confirmation multiplier; compute contracts (FLOOR, never round up)
 [ ] 14 Confirm total open risk <= 1.0R and daily limits not breached

EXECUTION
 [ ] Resting limit at the FVG boundary, OR market on the closed rejection candle
     — whichever the backtest validated. Not both, and not interchangeably.
 [ ] SL placed at fill. TYPE R: target placed at fill. TYPE C: no target.
 [ ] Log: timestamp, instrument, TYPE, score, level rank, ATR_D, ATR_X, sweep
     depth, R_available, target/stop ratio in ATR, size, and the reason for
     every point scored or not scored

MANAGEMENT
 [ ] TYPE R: time stop armed (12 bars NQ / 15 bars GC) — if validated
 [ ] TYPE C: trail armed FROM ENTRY. No target. No partials. No time stop.
 [ ] BE only at >= 1.2R (NQ) / 1.3R (GC) AND a new swing formed —
     anchored to STRUCTURE, never to the entry price
 [ ] Structure trail on CLOSED swings only, never intrabar (BUG-019)
 [ ] Session-end flat enforced (NQ 15:45 / GC 13:30 ET)
```

---

## APPENDIX B — STATE MACHINE

```
STATE: IDLE -> ARMED -> SWEPT -> SHIFTED -> PENDING_ENTRY -> IN_TRADE

IDLE:
    if dist_to_ranked_level <= 0.8 * ATR_D
       and session_rating in {A, B} and not in_no_trade_window:
           -> ARMED (record level_ref, level_rank, direction)

ARMED:
    if bar breaches level_ref by >= 0.25*ATR_D and <= 0.55*ATR_D:
        record sweep_extreme, sweep_bar_index -> SWEPT
    if breach > 0.55*ATR_D: -> IDLE            // breakout, not a sweep
    if bars_in_state > 24:  -> IDLE            // level went stale

SWEPT:
    if not closed_back_inside within 3 bars:   -> IDLE
    if MSS_confirmed and displacement_valid() and fvg_created():
        record fvg_hi, fvg_lo, displacement_hi, displacement_lo -> SHIFTED
    if bars_since_sweep > speed_window:        -> IDLE

SHIFTED:
    classify_type()                            // R or C — decides the EXIT ENGINE
    compute sl_price (§1.2), apply cluster_displacement (§1.3)
    if type == R:
        primary_draw = nearest pool clearing 2.5R   // NOT nearest pool
        if none: -> IDLE
    compute score (§5.7)
    if any_veto(): -> IDLE
    place resting limit at fvg entry level -> PENDING_ENTRY

PENDING_ENTRY:
    if retrace > 0.85 * displacement_leg: cancel -> IDLE
    if bars_since_mss > 15:               cancel -> IDLE
    if filled: -> IN_TRADE

IN_TRADE:
    // ORDER OF OPERATIONS IS LOAD-BEARING (BUG-019):
    // 1. move stop using data through bar i-1
    // 2. resolve bar i
    // 3. update state with bar i

    if type == R:
        arm time_stop(bars)                    // if validated
        if r_achieved >= 1.2 (NQ) / 1.3 (GC) and new_swing_formed():
            sl -> swing -/+ buffer
        if r_achieved >= 2.0: trail_on_closed_swings()
        exit 100% at primary_draw
    if type == C:
        trail_from_entry()                     // no target, no partials,
                                               // no time stop
    enforce session_end_flat()
```

---

## CHANGE LOG

**v2.0 (2026-08-12)** — audited v1.0 against the repository's measured evidence.

Corrections:
1. §2.3 — exits made **type-asymmetric**. Type C loses its target entirely
   (H75 CONFIRMED ×3, H79, exponent gap, BUG-017, AU200 archive — five
   independent confirmations, none against).
2. §2.2 — Primary Draw is the nearest pool that **clears** the R gate, not the
   nearest pool; obstruction check restricted to equal-or-higher rank (BUG-017).
3. §5.7 — **confluence override removed** (measured false and slightly backwards
   over 81,396 touches).
4. §2.4.2 — time stop **reclassified** from rule to hypothesis; barred from
   Type C (exponent gap).
5. §2.4.4 — COMEX floor close corrected to 13:30 ET.
6. §1.2 — structural override folded into the primary formula (BUG-022).
7. §1.5 — BUG-009 conflict reconciled explicitly rather than left latent.
8. §3.1 — risk % method upgraded to drawdown-budget solving; two conflicts with
   `COGNITIVE_ARCHITECTURE.md` flagged.
9. §5.8 — Type C's expected profile corrected to low-WR/long-tail; high WR
   flagged as a bug signature (BUG-033).

Additions:
10. **Part 6** — implementation hazard map, 17 rules → registered bugs.
11. **Part 7** — three mandatory controls: matched random null, three-execution
    reporting, identity arm. Plus a specified cost model.
12. **Part 8** — ranked list of what is unvalidated.
13. §4.1 — the TradingView data blocker, which decides whether this can be
    validated at all.

Retained from v1.0 essentially verbatim: all of §1 (stop placement), §3.2–3.4
(risk limits), §4.2–4.3 (sessions and no-trade windows), §5.1–5.6 (filters),
§5.9 (vetoes), the grading rubric's structure and the state machine's shape.

---

*This document describes a systematic trading framework and the reasoning behind
its parameters. It is analysis, not financial advice. Every parameter here is a
starting hypothesis requiring validation on your own data before risking capital.
No part of this rule set has been backtested.*
