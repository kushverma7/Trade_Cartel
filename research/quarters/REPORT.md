# The Quarters Theory, backtested on gold

**Data.** Two independent Dukascopy XAUUSD tick years — **91,629,949 ticks**
(2025-08-21 → 2026-08-20, price range $3,321.45–$5,598.26) and **64,093,055
ticks** (2024-08-20 → 2025-08-20). Real bid/ask throughout.

**Method.** Yotov's rules are all fractions of the large quarter **S** —
tolerance 0.10S, hesitation zone 0.30S, half point 0.50S, target 1.00S — so the
system is scale-free and ports to gold by choosing S. Gold has no pip
convention, so **S is a researcher degree of freedom**: every scale is tested,
and every scale is tested against **11 phase-shifted grids of identical
spacing**. A shifted grid sees the same data, the same drift and the same
volatility, so anything the round grid does that a shifted grid does not is
attributable to roundness and nothing else. This is the GL03 control applied to
Yotov's own premise.

**Scope limit, stated up front.** This is a **gold** test. Yotov's claim is
about **FX**. Test 1's result is market-agnostic mathematics and transfers;
Tests 2 and 3 are gold-specific and do not settle the FX claim.

---

## Test 1 — the first-passage asymmetry

*From a crossing of quarter point Q, does price reach Q+S before Q−S? H99
predicts **0.500** for a driftless walk starting at a boundary — on any grid, in
any market, in simulated noise. Yotov's premise requires the round grid to beat
that.*

### The round grid is indistinguishable from any other phase

| year | S | n (round) | **ROUND** | shifted mean | shifted sd | shifted range |
|---|---|---|---|---|---|---|
| 2025-26 | $2.50 | 2,475,146 | 0.5231 | 0.5232 | 0.00005 | 0.5231–0.5232 |
| 2025-26 | $5.00 | 1,243,408 | 0.5123 | 0.5123 | 0.00009 | 0.5122–0.5125 |
| 2025-26 | $12.50 | 496,281 | 0.5052 | 0.5052 | 0.00004 | 0.5051–0.5052 |
| 2025-26 | $25.00 | 240,876 | 0.5027 | 0.5027 | 0.00007 | 0.5026–0.5028 |
| 2025-26 | $100.00 | 52,589 | 0.5010 | 0.5008 | 0.00004 | 0.5007–0.5009 |
| 2025-26 | $250.00 | 21,160 | 0.5005 | 0.5004 | 0.00008 | 0.5003–0.5005 |
| 2024-25 | $2.50 | 892,147 | 0.5100 | 0.5100 | 0.00005 | 0.5099–0.5100 |
| 2024-25 | $12.50 | 180,597 | 0.5021 | 0.5021 | 0.00004 | 0.5021–0.5022 |
| 2024-25 | $25.00 | 86,485 | 0.5012 | 0.5011 | 0.00007 | 0.5010–0.5012 |

The round grid ranks 1/12 at some scales and 9/12 at others, but the entire
spread across twelve phases is **two parts in ten thousand**. There is nothing
to rank.

### And the excess over 0.500 is a tick artefact, not the market

Prices move in discrete jumps, so the tape lands some distance *past* the line
it crosses. That head start biases the race toward continuation by
**overshoot / 2S**. If that is the whole story, the bias must scale as 1/S and
the mean overshoot must be flat in S. Both hold, and the prediction is
quantitative:

| year | S | mean overshoot | predicted excess | observed excess | ratio |
|---|---|---|---|---|---|
| 2025-26 | $2.50 | $0.1207 | 0.0241 | 0.0231 | **0.96** |
| 2025-26 | $5.00 | $0.1243 | 0.0124 | 0.0123 | **0.99** |
| 2025-26 | $10.00 | $0.1267 | 0.0063 | 0.0065 | **1.03** |
| 2025-26 | $12.50 | $0.1274 | 0.0051 | 0.0052 | **1.02** |
| 2025-26 | $25.00 | $0.1270 | 0.0025 | 0.0027 | **1.06** |
| 2024-25 | $2.50 | $0.0511 | 0.0102 | 0.0100 | **0.98** |
| 2024-25 | $10.00 | $0.0522 | 0.0026 | 0.0026 | **1.00** |
| 2024-25 | $25.00 | $0.0526 | 0.0011 | 0.0012 | **1.14** |

Mean overshoot is constant in S to within 5% across a hundredfold range of S,
and 2.5× larger in the higher-priced, more volatile year — exactly as the
mechanism requires. The ratio drifts above 1 only where the excess is
vanishingly small (S ≥ $50, excess < 0.002).

**Verdict: H99 confirmed on gold at every scale.** P(continuation) = 0.500 plus
a discretisation artefact of the crossing definition. There is no directional
information in a quarter-point crossing, round or otherwise.

---

## Test 2 — do swing extremes cluster near quarter points?

*This tests Yotov's rhetorical core. Throughout webinars 2 and 5 he points at a
daily or weekly extreme and asks whether it is a coincidence that it sits close
to a quarter point — 1.4257 is "only 7 pips" from 1.4250. The completion rule
counts anything within 0.10S as a hit, and that band is **20% of the price
axis** by construction.*

Daily and weekly extremes of mid, both years pooled:

| kind | S | n | **ROUND** | shifted mean | shifted range | rank | p vs 20% |
|---|---|---|---|---|---|---|---|
| daily | $12.50 | 1252 | 0.187 | 0.201 | 0.171–0.220 | 10/12 | 0.884 |
| daily | $25 | 1252 | 0.197 | 0.198 | 0.161–0.232 | 7/12 | 0.606 |
| daily | **$50** | 1252 | **0.225** | 0.199 | 0.179–0.224 | **1/12** | **0.015** |
| daily | $100 | 1252 | 0.201 | 0.199 | 0.177–0.225 | 4/12 | 0.466 |
| daily | $250 | 1252 | 0.196 | 0.203 | 0.164–0.252 | 7/12 | 0.659 |
| weekly | $12.50 | 214 | 0.192 | 0.200 | 0.168–0.229 | 6/12 | 0.647 |
| weekly | $25 | 214 | 0.187 | 0.200 | 0.168–0.238 | 8/12 | 0.710 |
| weekly | **$50** | 214 | **0.252** | 0.201 | 0.168–0.243 | **1/12** | **0.036** |
| weekly | $100 | 214 | 0.220 | 0.196 | 0.164–0.224 | 2/12 | 0.260 |
| weekly | $250 | 214 | 0.192 | 0.203 | 0.159–0.266 | 6/12 | 0.647 |

Eight of ten cells sit at the 20% base rate with the round grid mid-pack. Two
cells clear p < 0.05 — both at S = $50 — but **ten cells were tested**, so the
family-wise corrected p values are 0.15 and 0.36. Neither survives.

### Does the round grid's advantage replicate out of sample?

| kind | S | 2025-26 rank | 2024-25 rank | |
|---|---|---|---|---|
| daily | $12.50 | 9/12 | 11/12 | |
| daily | $25 | 6/12 | 8/12 | |
| daily | **$50** | **1/12** | **3/12** | the only cell that holds up |
| daily | $100 | 1/12 | 9/12 | |
| daily | $250 | 5/12 | 6/12 | |
| weekly | $12.50 | 1/12 | **12/12** | **inverts** |
| weekly | $25 | 4/12 | 12/12 | |
| weekly | $50 | 1/12 | 6/12 | |
| weekly | $100 | 2/12 | 4/12 | |
| weekly | $250 | 2/12 | **11/12** | **inverts** |

Weekly $12.50 goes from best-of-twelve to worst-of-twelve between years; weekly
$250 from 2nd to 11th. That is the **BUG-046** signature — an effect that exists
in one draw and inverts in the next. **Daily S = $50 is the single cell that
ranks top-3 in both years**, and it is one cell out of ten with a corrected
p of 0.15. Reported because it is the only thing here pointing the right way,
not because it is evidence.

**Verdict: extremes land near quarter points at the rate chance dictates, and
the round grid does not beat grids of identical spacing placed elsewhere.**

---

## Test 3 — the Hesitation Zone system, tick-exact

*Results pending — see `results/system.log`, `controls.log`, `barclose.csv`.*

---

## Reproducing

```
python3 research/quarters/code/run_asymmetry.py   # Test 1
python3 research/quarters/code/overshoot.py       # why the excess exists
python3 research/quarters/code/run_extremes.py    # Test 2
python3 research/quarters/code/run_system.py      # Test 3: round vs 11 phases
python3 research/quarters/code/run_controls.py    # entry-at-level, zero-cost, inverted
python3 research/quarters/code/run_barclose.py    # H1/D1 close trigger
python3 research/quarters/code/summarise.py       # the tables above
```

Engine verified by hand against the raw tape: a long (Q $3,900, trigger $3,930,
entry $3,930.335 paying the ask, target $4,000, stop $3,900) and a short
(Q $4,300, trigger $4,270, entry $4,268.084 paying the bid, target $4,200)
reconcile to the cent on entry side, P&L and risk.
