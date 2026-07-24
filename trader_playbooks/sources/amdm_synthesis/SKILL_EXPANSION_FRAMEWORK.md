# SKILL EXPANSION FRAMEWORK
## How to Make Claude Smarter, More Accurate, and Self-Improving
### Version 1.0 | For trader_playbooks/ Skill Library

---

## PHILOSOPHY

Claude does not learn between sessions. But **YOU can make it smarter** by:
1. Building a **skill library** it reads every time
2. Creating **test cases** it validates against
3. Maintaining a **bug registry** it checks before coding
4. Iterating through **feedback loops** that refine its output

This document is the operating manual for turning Claude from a "helpful assistant" into a "specialized trading systems engineer."

---

## PART I: THE SKILL LIBRARY

### What Is a Skill?
A skill is a **reusable, validated code pattern** that Claude can import and use. It is not a strategy. It is a **building block**.

### Skill Library Structure
```
trader_playbooks/
  skills/
    SKILL_REGISTRY.md          # Index of all skills
    safe_arrays.pine           # Array bounds checking patterns
    anti_repaint.pine          # Confirmed-bar signal patterns
    session_filters.pine       # Timezone/session detection
    risk_sizing.pine           # Position sizing formulas
    volume_profile_proxy.pine  # Fast VAH/VAL/POC calculation
    swing_detection.pine       # Responsive swing high/low
    debug_dashboard.pine       # Diagnostic table template
    scale_out_engine.pine      # Multi-target exit logic
```

### How to Create a New Skill

**Step 1: Extract the Pattern**
When Claude writes a piece of code that works well, extract the reusable part.

Example: The corrected swing detection from AMDM v2:
```pinescript
// SKILL: Responsive Swing Detection
// Extracted from AMDM v2, validated on XAUUSD 5m
// Replaces lagging ta.pivothigh with immediate rolling levels

float swingHigh(int len) => ta.highest(high, len)
float swingLow(int len)  => ta.lowest(low, len)

bool breakUp(int len)   => close > swingHigh(len)[1] and close[1] <= swingHigh(len)[1]
bool breakDown(int len) => close < swingLow(len)[1]  and close[1] >= swingLow(len)[1]
```

**Step 2: Validate the Skill**
Before adding to the library, the skill must pass:
- [ ] Works on 3+ different assets
- [ ] Works on 3+ different timeframes
- [ ] No repainting
- [ ] No na propagation
- [ ] Documented edge cases

**Step 3: Register the Skill**
Add to `SKILL_REGISTRY.md`:
```markdown
| Skill | File | Purpose | Validation Status | Used By |
|-------|------|---------|-------------------|---------|
| Responsive Swing | swing_detection.pine | Immediate BOS detection | Validated: XAUUSD, EURUSD, ES on 5m/15m/1H | AMDM v2 |
```

**Step 4: Load Skills at Session Start**
When starting Claude, paste:
> "Read all files in trader_playbooks/skills/. You may use these patterns directly. Do not rewrite them. Reference them by name."

---

## PART II: THE TEST CASE LIBRARY

### What Is a Test Case?
A test case is a **known scenario with a known correct output**. It is the ground truth Claude validates against.

### Test Case Library Structure
```
trader_playbooks/
  tests/
    TEST_REGISTRY.md
    test_sweep_reclaim.md      # Known sweep+reclaim scenarios
    test_bos_confirmation.md   # Known BOS true/false scenarios
    test_session_detection.md  # Known session boundary scenarios
    test_position_sizing.md    # Known sizing math scenarios
```

### Test Case Format
```markdown
# TEST: Sweep + Reclaim at VAL
## Scenario
- Asset: XAUUSD
- Date: 2026-07-15
- Time: 09:30 GMT (London)
- Price action: Low wicks below VAL by 4 pips, body closes back above VAL
- Volume: Sweep candle 135% of 20-bar avg, reclaim candle 85% of avg

## Expected Output
- Signal: LONG (Model 2)
- Entry: Close of reclaim candle
- Stop: Below sweep wick low
- Confluence Score: 7/12

## Actual Output (from Claude vX)
- [Fill in after running]

## Pass/Fail
- [ ] Signal correct
- [ ] Entry correct
- [ ] Stop correct
- [ ] Score correct
```

### How to Use Test Cases
**Before delivering code, Claude must:**
1. Read the relevant test cases
2. Mentally execute the code against each scenario
3. Confirm the output matches expected
4. If mismatch → fix code, retest

**Command:**
> "Before delivering this code, run it against test cases: [list]. Confirm all pass. If any fail, fix and retest."

---

## PART III: THE BUG REGISTRY

### What Is the Bug Registry?
A **permanent record** of every bug found, with root cause and fix. Claude reads this before writing new code to avoid repeating mistakes.

### Bug Registry Structure
```
trader_playbooks/
  bugs/
    BUG_REGISTRY.md
```

### Bug Entry Format
```markdown
### BUG-001: Model 2 Volume Contradiction
- **Date Found:** 2026-07-22
- **Severity:** Critical
- **Symptom:** Model 2 produced zero trades
- **Root Cause:** Required volume >120% AND <100% on same bar (impossible)
- **Fix:** Split volume check across sweep bar [1] and reclaim bar [0]
- **Prevention:** Phase 0 truth table must include volume conditions
- **Affected Files:** AMDM_confluence_strategy.pine
- **Status:** Fixed in v2

### BUG-002: BOS Detection Lag
- **Date Found:** 2026-07-22
- **Severity:** High
- **Symptom:** Model 1 rarely fired
- **Root Cause:** ta.pivothigh(10,10) confirms 10 bars late; crossover never triggers
- **Fix:** Replaced with ta.highest() responsive break
- **Prevention:** Phase 1 "first 3 bars" walkthrough catches lag
- **Affected Files:** AMDM_confluence_strategy.pine
- **Status:** Fixed in v2
```

### How to Use the Bug Registry
**At session start:**
> "Read BUG_REGISTRY.md. Do not repeat any registered bug. If your code resembles an affected pattern, explicitly state how you avoid the bug."

**When a new bug is found:**
1. User documents it in BUG_REGISTRY.md
2. Next session, Claude reads it
3. Claude checks new code against the registry before delivery

---

## PART IV: THE FEEDBACK LOOP

### The Iteration Cycle

```
1. CLAUDE DELIVERS CODE
        ↓
2. USER TESTS ON CHART
        ↓
3. USER DOCUMENTS RESULTS
   - Works? → Add to test case library
   - Bug?  → Add to bug registry
   - Slow? → Add to performance notes
        ↓
4. USER FEEDS BACK TO CLAUDE
   "BUG-003 found: [description]. Fix required."
        ↓
5. CLAUDE FIXES + ADDS TO REGISTRY
        ↓
6. NEXT SESSION: CLAUDE READS REGISTRY
        ↓
7. CLAUDE'S CODE QUALITY IMPROVES
```

### Feedback Commands

| Situation | What to Paste |
|-----------|---------------|
| **Bug found** | "BUG-00X: [description]. Root cause: [analysis]. Add to BUG_REGISTRY.md and fix." |
| **Test passed** | "TEST-00X passed. Add to TEST_REGISTRY.md as validated." |
| **Performance issue** | "PERF-00X: [description]. Code is too slow/uses too many resources. Optimize." |
| **Clarification needed** | "CLARIFY-00X: [question]. Document answer in SKILL_REGISTRY.md." |

---

## PART V: THE VALIDATION SUITE

### Automated Validation (Where Possible)
For Pine Script, full automation is hard. But you can create **validation scripts**:

```pinescript
// validation_sweep_reclaim.pine
// This indicator plots EXPECTED signals for known test cases
// Run alongside the strategy to visually confirm alignment

// Known test case: 2026-07-15 09:30 GMT
bool expectedLong = (year == 2026 and month == 7 and dayofmonth == 15 and hour == 9 and minute == 30)
plotshape(expectedLong, "EXPECTED LONG", shape.triangleup, location.belowbar, color.green, size=size.small)
```

### Manual Validation Checklist
Every code delivery must include:
- [ ] 5 historical bar walkthrough (Phase 4 of Code Delivery Protocol)
- [ ] 1 known test case execution
- [ ] Visual confirmation on chart (3+ signals visible)
- [ ] No errors in Pine Editor
- [ ] No warnings in Pine Editor

---

## PART VI: EXPANDING CLAUDE'S CAPABILITIES

### Level 1: Pattern Recognition (Current)
Claude recognizes patterns from data you feed it.
**How to improve:** Feed more diverse data. More assets, more timeframes, more market conditions.

### Level 2: Pattern Synthesis (Current)
Claude combines patterns into strategies.
**How to improve:** Force cross-asset testing. "Does this pattern work on EURUSD? On ES? On BTC?"

### Level 3: Pattern Validation (Next)
Claude validates patterns against test cases.
**How to improve:** Build the test case library. Every new pattern gets 3+ test cases before inclusion.

### Level 4: Pattern Optimization (Next)
Claude optimizes patterns for performance (speed, resource usage).
**How to improve:** Add performance benchmarks. "This indicator must load in <2 seconds on 10,000 bars."

### Level 5: Pattern Innovation (Future)
Claude creates novel patterns by combining existing ones in non-obvious ways.
**How to improve:** Feed Claude adjacent fields (physics, biology, game theory) and ask for analogies.

---

## PART VII: THE SESSION STARTUP SEQUENCE

To maximize Claude's capability, run this sequence every session:

```
1. Load COGNITIVE_ARCHITECTURE.md
2. Load CODE_DELIVERY_PROTOCOL.md
3. Load SKILL_REGISTRY.md
4. Load BUG_REGISTRY.md
5. Load TEST_REGISTRY.md
6. State current project goal
7. Begin work
```

**One-line startup:**
> "Load all .md files in trader_playbooks/ and skills/. Adopt as operating system. Today's goal: [specific task]."

---

## PART VIII: THE HONEST LIMITATIONS

### What Claude Cannot Do (Even With This Framework)
1. **Access real-time market data** — It can only process what you feed it
2. **Run code** — It writes code; you run it
3. **Learn between sessions** — It reads files; it does not remember
4. **Guarantee zero bugs** — It reduces bugs; it cannot eliminate them
5. **Replace human judgment** — You must validate every output

### What This Framework Achieves
1. **Consistency** — Same quality every session
2. **Cumulative improvement** — Bugs decrease over time
3. **Faster delivery** — Reusable skills reduce coding time
4. **Higher confidence** — Test cases validate correctness
5. **Self-documentation** — Registry becomes knowledge base

---

## APPENDIX: QUICK COMMANDS

| Goal | Command |
|------|---------|
| Add new skill | "Extract [pattern] from [file] as a reusable skill. Validate on 3 assets. Add to SKILL_REGISTRY.md." |
| Add test case | "Create test case for [scenario]. Expected output: [details]. Add to TEST_REGISTRY.md." |
| Report bug | "BUG-00X: [description]. Root cause: [analysis]. Fix and add to BUG_REGISTRY.md." |
| Validate code | "Before delivering, run against TEST_REGISTRY.md cases [list]. Confirm all pass." |
| Optimize skill | "Skill [name] is too slow. Optimize for [metric]. Validate against existing tests." |
| Cross-asset test | "Test skill [name] on [asset 1], [asset 2], [asset 3]. Report results." |

---

## FINAL WORD

**Claude is a tool. You are the craftsman.**

This framework does not make Claude omniscient. It makes Claude **reliable, consistent, and improvable.**

Every session builds on the last. Every bug teaches a lesson. Every test case raises the bar.

**The goal is not perfection. The goal is continuous, measurable improvement.**

Build the library. Run the tests. Log the bugs. Feed the feedback.

The machine gets smarter every day.
