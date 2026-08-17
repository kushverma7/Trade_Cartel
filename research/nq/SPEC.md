# Mechanical interpretation — for approval before anything runs

Every rule below is stated as code will execute it. Where your description
admitted more than one reading I have **flagged it and picked a default**;
where it cannot be coded objectively at all I have marked it **SUBJECTIVE**
and it is excluded from the strategy rather than quietly invented.

---

## A. Ambiguities that need your decision

These change results materially. I have chosen a default for each so the run
is not blocked, but they are the first things to correct.

**A1 — What is "the day" for a futures instrument?**
NQ trades 18:00–17:00 ET. "Daily Open" and "Previous Day High/Low" therefore
have two defensible definitions:
- `futures` (DEFAULT): the day begins 18:00 ET. Matches the CME session.
- `cash`: the day begins 09:30 ET. Matches the equity index.
These give different levels on most days. **This is the exact class of error
that produced BUG-039 in this repo** — a level referenced by name that resolved
to two different prices — so the engine computes BOTH and reports both.

**A2 — Session times.** Defaults, all New York time, all configurable:
- Asia: 20:00 → 00:00
- London: 03:00 → 08:00
- New York: 09:30 → 16:00
There is no single industry standard. Changing these changes every session
level and therefore every cluster.

**A3 — "Previous completed 4H".** 4H bars are anchored to 18:00 ET
(18:00, 22:00, 02:00, 06:00, 10:00, 14:00). An 00:00-anchored alternative is
also run so the choice is visible rather than assumed.

**A4 — Quarter grid.** Your spec is unambiguous and is implemented literally:
majors every 1000, larges every 250, halves every 500, one-shot zone ±25.
No interpretation needed.

**A5 — "Middle of nowhere".** Coded as: no cluster scoring ≥ `min_score`
within `approach_pts` of the close. Swept over several thresholds.

**A6 — Displacement measured on the BODY.** Your section 6 says
"candle body >= X × ATR(14)". Implemented as `|close-open| >= X * ATR(14)`,
not the full range. ATR is computed on the execution timeframe, Wilder, and
uses only completed bars.

---

## B. Rules that CANNOT be coded — flagged, not invented

**B1 — "VIX rejecting an important resistance/pivot area" (§9 model B).**
Objective part: VIX direction over N bars, and VIX within a tolerance of its
own confirmed pivot. That much is coded. What is *not* codable is "important"
— which of VIX's pivots matter is a judgement. **Reported as a weak proxy,
and §9 model A (simple inverse) is reported separately and treated as the
honest test.**

**B2 — "Trail remainder using structure" (§13 model 3).**
Coded as: trail the stop to the most recent *confirmed* swing in the trade's
favour, updated only when a new swing confirms. This is one of several
defensible readings. Flagged.

**B3 — "Relevant structural invalidation" (§13 C/D).**
Coded as an opposing MSS, i.e. a close beyond the most recent confirmed swing
against the position. Distinct from the stop.

**B4 — "Clear rejection" (Model C, §8).**
Coded as a wick beyond the cluster of at least `wick_frac` of the bar's range,
with the close back inside. The threshold is arbitrary and is swept.

---

## C. The state machine (§15)

```
0 WAITING            no qualifying cluster within approach_pts
1 APPROACHING        cluster in range, nothing has happened yet
2 SWEPT              price traded beyond the cluster by >= sweep_min
                     and <= sweep_max, within the reclaim window
3 AWAITING MSS       reclaim confirmed (close back through the level)
4 MSS CONFIRMED      close beyond the last CONFIRMED opposing swing,
                     with displacement if required
5 AWAITING RETEST    price must return within retest_tol of the level
6 ENTRY              retest held; order fills at that bar's CLOSE
7 ACTIVE             direction persists (§13) until stop, target,
                     opposing MSS or structural invalidation
8 EXIT               then reset to 0
```
One liquidity event produces **one** setup. The machine cannot re-enter from
the same sweep; it must return to state 0 first (§14).

## D. No-lookahead guarantees (§ your opening constraints)

1. A swing at bar `i` with pivot strength `k` is **not visible until bar
   `i+k`**. The engine stamps every swing with its confirmation index and
   refuses to read it earlier. This is asserted in code, not assumed.
2. Higher-timeframe values are stamped with the close time of their bar and
   are only readable strictly after it.
3. Entries fill at the **close of the signal bar**. Exits resolve on
   subsequent bars only.
4. Within an exit bar the **adverse extreme is always taken first**. On a bar
   that touches both stop and target, the trade loses.
5. Stops never widen. There is no code path that moves a stop away from entry.
6. A self-test suite must pass before any sweep is permitted to run: a
   zero-cost direction null (expect t≈0), an injected-edge recovery, cost
   monotonicity, and a random-walk test (expect PF≈1.0). These four caught two
   separate bugs in this repo's other engines.

## E. Overfitting control (§20)

- **Walk-forward**, not a single split. Rolling windows: optimise on N months,
  validate on the following M, step forward, never look back.
- Every reported in-sample optimum carries its multiple-testing bar
  `t >= sqrt(2 ln K)` for the K cells actually searched.
- A **shuffle null** compared against the search **maximum**, not its mean.
- If out-of-sample collapses, the collapse is the headline.

## F. Cost model (§21)
Per side: `commission + slippage_ticks * 0.25 * multiplier`. Swept at 0, 1, 2
and 4 ticks. NQ multiplier $20/point; results reported in **points and R** so
they stay contract-size agnostic. Costs charged on every fill including each
partial.
