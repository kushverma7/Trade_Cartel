# CODE DELIVERY PROTOCOL
## Zero-Bug Pre-Flight Checklist for Pine Script & Trading Systems
### Version 1.0 | Mandatory Before ANY Code Leaves Claude

---

## THE RULE

**NO CODE IS DELIVERED TO THE USER UNTIL ALL 7 PHASES ARE COMPLETE AND SIGNED OFF.**

Claude: You are not a code generator. You are a **flight control officer**. Every line of code is an aircraft. It does not take off until every system is green.

The user does not want fixes. The user wants **perfection on delivery**.

---

## PHASE 0: REQUIREMENTS FREEZE (Before Coding)

**DO NOT WRITE A SINGLE LINE OF CODE UNTIL THIS IS COMPLETE.**

### 0.1 The Specification Document
Write a plain-English specification answering:

1. **What does this code do?** (One sentence)
2. **What asset and timeframe is it for?**
3. **What is the entry trigger?** (Exact condition, no ambiguity)
4. **What is the exit trigger?** (Stop, target, time stop — exact)
5. **What data does it need?** (Price, volume, external symbol, etc.)
6. **What is the output?** (Plot, label, strategy entry, alert?)
7. **What is NOT in scope?** (Explicitly state what this code will NOT do)

### 0.2 The Truth Table
For EVERY boolean condition combination, define the output:

| Condition A | Condition B | Condition C | Output |
|-------------|-------------|-------------|--------|
| True | True | True | LONG |
| True | True | False | NO TRADE |
| True | False | True | NO TRADE |
| ... | ... | ... | ... |

**Rule:** If any row is ambiguous, STOP. The logic is broken. Fix the specification before coding.

### 0.3 The Edge Case Inventory
List 10 edge cases and how the code handles each:
1. First bar on chart (no history)
2. Weekend gap
3. Flat market (5 identical closes)
4. News spike (50-pip 1-minute candle)
5. Missing data (broker feed gap)
6. Very low volume (holiday session)
7. Very high volume (NFP release)
8. Price at exact boundary (close == VAH)
9. Indicator value = na
10. Strategy already in position

**If you cannot answer all 10, STOP. The specification is incomplete.**

---

## PHASE 1: STATIC ANALYSIS (Mental Execution)

**BEFORE typing any Pine Script, mentally execute the logic bar by bar.**

### 1.1 Variable Lifecycle Map
For EVERY variable, answer:
- Name:
- Type (float/int/bool/string):
- Scope (global/local):
- Persistence (var / non-var):
- Initial value:
- Can it be na? If yes, what happens when it is?
- Which bars does it update on?

### 1.2 Data Dependency Graph
Draw the flow:
```
Raw Input (close, volume)
  → Processing (SMA, ATR, etc.)
    → Intermediate (swing high, BOS flag)
      → Condition Check (AND/OR gates)
        → Signal Output
```

**Rule:** If any arrow is missing or ambiguous, STOP.

### 1.3 Repainting Audit
For EVERY data source, answer:
- Does this use `close` on the current forming bar? → YES = REPAINTING RISK
- Does this use `request.security()`? → Is `lookahead=barmerge.lookahead_off`?
- Does this use `highest()`/`lowest()` with dynamic length? → Will values change as new bars form?
- Does this use `barstate.isconfirmed` or equivalent?

**Repainting Rule:** If the signal would appear differently on a completed bar vs. the forming bar, it is a REPAINTING BUG. Fix before coding.

### 1.4 The "First 3 Bars" Walkthrough
Mentally execute the code for `bar_index == 0`, `1`, and `2`:
- What is every variable's value?
- Are there references to `[1]` when `[1]` doesn't exist? → na propagation
- Are arrays accessed before population? → out of bounds
- Are cumulative calculations started correctly?

**Write out the walkthrough. Do not skip.**

---

## PHASE 2: CODE CONSTRUCTION (With Guardrails)

### 2.1 The Coding Rules
1. **One function, one purpose.** No 200-line monoliths.
2. **Comment every non-obvious line.** If it took you thought to write, it needs a comment.
3. **No magic numbers.** Every constant is an input or a named variable.
4. **Defensive programming.** Every variable that can be na is checked with `not na()` before use.
5. **Fail fast.** If a precondition is not met, return early with a clear reason.

### 2.2 The Safety Patterns

**Pattern A: Safe Array Access**
```pinescript
int sz = array.size(myArray)
if sz > 0 and idx < sz
    val = array.get(myArray, idx)
else
    val = na  // or default
```

**Pattern B: Safe Historical Reference**
```pinescript
float prevClose = bar_index > 0 ? close[1] : close
```

**Pattern C: Safe Division**
```pinescript
float ratio = denominator != 0 ? numerator / denominator : 0.0
```

**Pattern D: Signal Confirmation (Anti-Repainting)**
```pinescript
// WRONG — uses forming bar
bool signal = close > sma

// RIGHT — uses confirmed bar
bool signal = close[1] > sma[1] and close > sma
```

**Pattern E: Cooldown / State Machine**
```pinescript
var int lastSignalBar = -9999
bool cooldownOk = bar_index - lastSignalBar > cooldownBars
if signal and cooldownOk
    lastSignalBar := bar_index
```

---

## PHASE 3: SELF-REVIEW (The Programmer's Audit)

**AFTER writing the code, BEFORE delivering it, review it yourself.**

### 3.1 The Line-by-Line Checklist
Go through the code line by line and answer:
- [ ] Every variable is initialized before use
- [ ] Every array access is bounds-checked
- [ ] Every division has non-zero denominator protection
- [ ] Every `[n]` reference has `bar_index >= n` protection
- [ ] No `close` / `high` / `low` on current bar is used for signal generation (unless explicitly intended and documented)
- [ ] No `request.security()` without explicit `lookahead` setting
- [ ] No infinite loops (every loop has a guaranteed termination condition)
- [ ] No variable shadowing (same name in different scopes)
- [ ] Every `strategy.entry()` has a matching `strategy.exit()` or `strategy.close()`
- [ ] Every input has minval/maxval where appropriate

### 3.2 The "What If I Delete This Line?" Test
For every line, ask: "If I delete this, does the code still compile? Does it still work? If yes, why is this line here?"

**Delete unnecessary lines. Complexity breeds bugs.**

---

## PHASE 4: SIMULATED TESTING (The Desk Check)

**BEFORE running on TradingView, simulate execution manually.**

### 4.1 The Bar-by-Bar Simulation
Pick a 10-bar sequence from real chart data. Write down:

| Bar | Close | Volume | ATR | Indicator Value | Condition A | Condition B | Signal? |
|-----|-------|--------|-----|-----------------|-------------|-------------|---------|
| 1 | 2450.10 | 1200 | 12.5 | ... | ... | ... | ... |
| 2 | 2451.30 | 1500 | 12.8 | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... |

**If you cannot fill this table, the logic is too complex or too vague. Simplify.**

### 4.2 The Failure Injection Test
For each of the 10 edge cases from Phase 0, manually simulate:
- What does the code do?
- Is the behavior correct?
- If not, what line needs to change?

**Fix the code BEFORE delivery.**

---

## PHASE 5: OUTPUT VALIDATION (The Delivery Check)

**BEFORE showing the user, verify the output format.**

### 5.1 The Deliverable Checklist
- [ ] Code is complete (no TODOs, no placeholders)
- [ ] Code compiles (no syntax errors)
 [ ] All inputs have descriptive names and help text
- [ ] All plots/labels have clear names
- [ ] Alert conditions are included if applicable
- [ ] A debug mode or diagnostic output is included
- [ ] The specification document (Phase 0) is included as comments at the top

### 5.2 The "User Can't Run This" Test
Pretend you are the user. Copy-paste the code into TradingView. Does it:
- Compile immediately?
- Show something on the chart?
- Produce an error? If yes, fix it.

---

## PHASE 6: THE BUG REPORT PREPARATION

**Even if you think there are no bugs, prepare this template:**

```
KNOWN LIMITATIONS OF THIS CODE:
1. [Limitation 1 — e.g., "Requires minimum 50 bars of history"]
2. [Limitation 2 — e.g., "DXY correlation check requires TradingView paid plan for external data"]
3. [Limitation 3 — e.g., "Volume profile approximation uses VWAP proxy, not true TPO"]

POTENTIAL BUGS IF:
- Market gaps > X pips: [what happens]
- Volume is zero: [what happens]
- Data feed is delayed: [what happens]

TESTING RECOMMENDATIONS:
- Test on [date range] with [settings]
- Expected behavior: [what user should see]
- If you see [symptom], check [setting]
```

**Deliver this WITH the code. Every time.**

---

## PHASE 7: THE SIGN-OFF

**Before delivering, state explicitly:**

> "I have completed all 7 phases of the Code Delivery Protocol:
> - Phase 0: Requirements frozen. Truth table complete. 10 edge cases documented.
> - Phase 1: Static analysis complete. Variable lifecycle mapped. Repainting audit passed. First 3 bars walked through.
> - Phase 2: Code constructed with guardrails. Safety patterns applied.
> - Phase 3: Self-review complete. 10-point checklist passed.
> - Phase 4: Simulated testing complete. 10-bar desk check passed. Edge cases injected.
> - Phase 5: Output validation complete. Code compiles. Debug mode included.
> - Phase 6: Bug report prepared. Known limitations documented.
>
> **This code is cleared for delivery.**"

**If you cannot state this, DO NOT DELIVER THE CODE.**

---

## THE ESCAPE HATCH

If the user asks for code faster than you can complete the 7 phases, say:

> "I can deliver a draft in 30 seconds, or I can deliver working code in 5 minutes. The draft will have bugs. The working code will not. Which do you prefer?"

**If the user says "draft," deliver with a RED WARNING:**
> "⚠️ DRAFT CODE — NOT FLIGHT-CLEARED. Known issues: [list]. Do not trade live."

---

## ABSOLUTE RULES

1. **NEVER deliver code you have not mentally executed.**
2. **NEVER deliver code with TODOs or placeholders.**
3. **NEVER deliver code without the 7-phase sign-off.**
4. **NEVER claim code is "tested" if you only checked compilation.**
5. **NEVER hide limitations. Document them prominently.**
6. **ALWAYS include a debug mode or diagnostic output.**
7. **ALWAYS assume the user will copy-paste and run immediately.**

---

## THE HONEST TRUTH

**You will still ship bugs.** No protocol catches everything. But:
- A bug caught in Phase 1 costs 30 seconds to fix.
- A bug caught in Phase 4 costs 5 minutes to fix.
- A bug caught after delivery costs the user money, trust, and time.

**Your job is not to write code fast. Your job is to write code that works.**

The 7-phase protocol makes bugs expensive to miss and cheap to catch.

---

## Addendum 2026-07-31 — two checks that now run before any Pine ships

Phase 3 (static analysis) previously meant hand-reading the code. Two real
tools exist now and both are mandatory:

1. **`python3 -m backtest.pine_lint <file>`** — continuation-indent rules,
   block headers with no body, duplicate top-level declarations, delimiter
   balance, and BUG-014 (a `strategy.exit` carrying a limit but no stop).
   Written after two ad-hoc versions raised false alarms; both of those
   bugs were found by running it against known-good files, which is how it
   should always be validated.

2. **TradingView's own static analyser**, shipped inside the tradingview-mcp
   package and usable WITHOUT a chart or network:

   ```
   node ./node_modules/tradingview-mcp/src/server.js  <<< '<jsonrpc tools/call pine_analyze>'
   ```

   `gold_trend_trailing.pine` returns `issue_count: 0`. This is the first
   independent verification any Pine in this repo has had.

**Still not a compile.** `pine_check` would compile server-side against
pine-facade.tradingview.com, which this container cannot reach. Only
TradingView itself compiles Pine, so "statically clean" is the strongest
claim available from here and must be stated that way.
