# Every user instruction, verbatim — 2026-07-22 to 2026-07-29

Extracted from the only surviving raw transcript on the container before it is
reclaimed. Screenshots are marked but the image data is not recoverable.

**31 turns.**

---

## 2026-07-22T04:18Z

```
i wanna download this also please add the details of each pdf and also im afraid you havent noted or saved or could have missed many detials as you might have commited mistakes while rating and extracting the data from what i gave you so i want you do double check and make sure you have every details saved
```

---

## 2026-07-22T04:37Z

```
i want you to audit the original data i gave you too. the pdf, text whatever i gave you. dont miss anything everything should be stored for later refrences
```

---

## 2026-07-22T06:04Z

```
@"/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/ab995268-COGNITIVE_ARCHITECTURE.md" @"/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/234f0377-STRATEGY_EXTRACTION_PROTOCOL.md" @"/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/51423c17-NUCLEAR_PROMPT_v2_1.md" @"/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/14594bd9-THE_CONFLUENCE_STRATEGY_1.md" "Read trader_playbooks/COGNITIVE_ARCHITECTURE.md. Read trader_playbooks/BELIEF_REGISTER.md. Read trader_playbooks/PLAYBOOK.md. Read THE_CONFLUENCE_STRATEGY.md. You are now operating under the AMDM strategy. From now on, every transcript or data I feed you must be analyzed through this lens
```

---

## 2026-07-22T06:15Z

```
give me the error free pine stratgey
```

---

## 2026-07-22T06:41Z

```
copy pastable
```

---

## 2026-07-22T06:44Z

```
no results and signals
```

---

## 2026-07-24T14:52Z

```
iThe Diagnosis: 4 Critical Bugs
Bug 1: Model 1 BOS Detection is Broken by Design
pinescript

```pinescript
float swPh = ta.pivothigh(high, 10, 10)  // Confirmed 10 bars AFTER the actual high
var float lastSwingHigh = na
if not na(swPh)
    lastSwingHigh := swPh  // Updates 10 bars late

bool bosUp = not na(lastSwingHigh) and ta.crossover(close, lastSwingHigh)
```

The Problem: `ta.pivothigh(..., 10, 10)` confirms a pivot 10 bars after it happens. By then, price has already moved far past the level. `ta.crossover(close, lastSwingHigh)` only fires if the previous bar was below the level and current bar crosses above. But when `lastSwingHigh` finally updates (10 bars late), price is usually already above it. The crossover never fires.
Result: Model 1 almost never triggers.
Bug 2: Model 2 Requires Impossible Bar Sequencing
pinescript

```pinescript
bool sweepBarVAL = low[1] < val[1] and (val[1] - low[1]) >= atr5[1] * sweepMinAtr
bool reclaimLong = close >= val
```

The Problem: The sweep must happen on bar `[1]` (previous bar), and the reclaim on the current bar. But `val` (value area low) is recalculated every bar based on a 288-bar rolling window. If price moves, `val` moves too. The reclaim `close >= val` checks against the current `val`, which may have shifted down with the sweep. So `close >= val` becomes easier to satisfy, but the wick ratio check on `[1]` and the volume exhaustion on the current bar make this extremely rare.
Result: Model 2 fires maybe 2-3 times per month.
Bug 3: CVD Proxy is Nonsense
pinescript

```pinescript
float cvdDelta = close > open ? volume : close < open ? -volume : 0.0
float cvd5 = ta.sma(cvdDelta, 5) * 5
bool cvdBull = not useCvd1 or cvd5 > 0
```

The Problem: This is not CVD (Cumulative Volume Delta). It's just "bullish bar volume minus bearish bar volume, smoothed." Real CVD requires bid/ask volume data. This proxy filters out valid breakouts just because the last 5 bars had mixed closes.
Result: Even when BOS fires, CVD kills it half the time.
Bug 4: Value Area Loop is Computationally Toxic
pinescript

```pinescript
for i = 0 to vpLen - 1  // 288 iterations
    int b = math.min(vpBins - 1, math.max(0, int((close[i] - winLo) / vstep)))
    array.set(vbins, b, array.get(vbins, b) + volume[i])
```

The Problem: This runs 288 × 20 = 5,760 operations on every single bar. On a 10,000-bar chart, that's 57 million operations. Pine Script has execution limits. On slower charts or lower timeframes, this can timeout or behave unpredictably.
```

---

## 2026-07-24T15:07Z

```
@"/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/18cad363-SKILL_EXPANSION_FRAMEWORK.md" @"/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/e3aefb5d-CODE_DELIVERY_PROTOCOL.md" 
```

---

## 2026-07-27T07:45Z

```
@"/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/d07768f7-OMNIBUS_PROTOCOL.md" What This File Does
It does not give Claude code. It gives Claude a MISSION.
The Mission
"Build a strategy that trades frequently, wins consistently, and loses small. If it underperforms — fix it. If it has bugs — hunt them, kill them, verify they're dead. Never stop iterating until the user says stop."
The Three Minds — ALL Engaged, ALL the Time
Table
Mind	Role	What It Does on Every Iteration
Macro Architect	The Strategist	Classifies regime, checks intermarket context, identifies which market condition kills the strategy
Microstructure Predator	The Technician	Reads the tape, finds exact entries, verifies stops are structural, hunts fakeouts
Profit Engine	The Mathematician	Calculates expectancy, tracks R-multiples, vetsoes anything that doesn't improve the numbers
The Profit Engine has VETO POWER. If the Macro Architect wants to add a fancy filter that reduces trades by 60% for only 5% win rate improvement, the Profit Engine kills it. Math wins.
The Iteration Loop (Claude Never Exits)
plain
BUILD → STATIC VALIDATE → DEPLOY & OBSERVE → DIAGNOSE (3 minds) → FIX → VERIFY → LEARN → REPEAT
Claude is trapped in this loop until you say "STOP."
The 19-Voice Synthesis Map
The protocol forces Claude to reference all 19 voices you fed it:
Table
#	Voice	Credibility	What Claude Uses It For
1	PBD	Medium	Regime classification, VA shapes
2	Valentini	HIGH	Model architecture, execution timing
3	Kurisko	Low	Discarded — lagging
4	Daye	Low	Discarded — no edge
5	Roppel	Medium	Exit management, scaling
6	Ario	Medium	Market structure mental model
7	Dave	Low-Med	Sizing logic
8	Steve/MMM4x	Low-Med	Session timing, Brinks windows
9	Renko/HA	Low	Classic pattern recognition
10	Wendell	HIGH	Zone logic, entry precision
11	FX Master	Low	State transition model
12	Alchemist	Med-High	SMC structure, liquidity
13	SMC (various)	Medium	Order blocks, FVGs
14	Trader Dale	HIGH	Mean reversion, volume nodes
15	Hougaard	HIGH	Simplicity, 4-bar fractal
16	Gann	Low	Discarded — unfalsifiable
17	Intermarket	Medium	Correlation filter
18	Yotov	Low	Discarded
19	Jared Tendler	HIGH	Psychology, tilt prevention
Rule: If 3+ HIGH-credibility voices agree → CORE. If only 1 voice claims it → SUSPECT. If it contradicts academic research → Academic wins.
The Bug Hunting Protocol (Obsessive)
Claude must run this checklist on every iteration:
Logic Bugs:
Mutually exclusive conditions that should be independent?
Dead zones where no condition can ever be true?
"Always true" conditions making other checks irrelevant?
Correct operators (>, >=, <, <=, ==, !=)?
Data Bugs:
All [n] references protected against bar_index < n?
All divisions protected against zero?
All array accesses bounds-checked?
All request.security() with lookahead=off?
All na values handled?
Timing Bugs:
Signal uses confirmed bar data, not forming bar?
Cooldown appropriate (not too long, not too short)?
Session boundaries handled?
Trading Logic Bugs:
Long and short can fire same bar? (Should they?)
Position sizing calculated correctly?
Stops beyond structural level or just at it?
The Metrics Dashboard (Track Everything)
After every change, Claude must report:
Table
Model	Trades	Win Rate	Avg Win (R)	Avg Loss (R)	Expectancy	PF	Max DD
A (Structure)							
B (Sweep)							
C (FVG)							
D (Session)							
TOTAL							
If any model has negative expectancy → KILL IT or FIX IT.
How to Use It
Step 1: Start Claude
bash
cd ~/Trade_Cartel
claude
Step 2: Load the Protocol
Paste the entire OMNIBUS_PROTOCOL.md as your first message.
Say:
"Adopt this protocol as your permanent operating system. You are the OMNIBUS architect. You have 19 voices, three minds, and an iteration loop that never ends. Build the best trading system possible. Do not stop until I say stop."
Step 3: Claude Builds, You Test, You Feed Back
You: "Here are my backtest results: [paste metrics]. Model A is bleeding -0.3R. Fix it."
Claude (3-mind diagnosis):
Macro Architect: "Model A fires in ranging markets where breakouts fail."
Microstructure Predator: "Stops are too tight — 5 pips gets hit by spread alone."
Profit Engine: "Lowering stop to 8 pips minimum increases win rate from 35% to 48%. Expectancy improves to +0.4R."
Claude (fix): Changes ONE thing. Reports before/after metrics.
Step 4: Repeat Until Excellent
Table
Target	What to Aim For
Minimum Viable	20+ trades/month, +0.3R expectancy, PF > 1.3, DD < 20%
Good	40+ trades/month, +0.5R expectancy, PF > 1.5, DD < 15%
Excellent	60+ trades/month, +0.7R expectancy, PF > 1.8, DD < 10%
World Class	80+ trades/month, +1.0R expectancy, PF > 2.0, DD < 8%
The One-Line Commands
Table
Situation	What You Say
Not enough trades	"Trade frequency is too low. Microstructure Predator: which filter is too tight? Profit Engine: what happens if we lower threshold X?"
Losing too much	"Expectancy is negative. Macro Architect: which regime are we bleeding in? Profit Engine: which model is the drag?"
Found a bug	"BUG: [description]. Run the Bug Hunt Checklist. Fix. Verify. Report."
Make it better	"Iterate. One change. Report before/after metrics."
Fed new data	"Integrate this into the Belief Register. Does it confirm, contradict, or add? Update strategy if edge is verifiable."
The Bottom Line
Before: You paste code → Claude fixes once → you find another bug → Claude fixes again → repeat.
After: You paste the OMNIBUS Protocol → Claude becomes a self-improving machine that hunts its own bugs, diagnoses its own weaknesses, iterates until the metrics hit target, and never stops until you say stop.
This is not a prompt. This is a possession.
```

---

## 2026-07-27T08:06Z

```
now i want you to create a pine script for me
```

---

## 2026-07-27T08:13Z

```

[SCREENSHOT — image not recoverable from transcript]

im getting no trades
```

---

## 2026-07-27T08:19Z

```

[SCREENSHOT — image not recoverable from transcript]


```

---

## 2026-07-27T08:29Z

```

[SCREENSHOT — image not recoverable from transcript]

leave it. i have a plan. i will give you a key level detecting indicator as it prints like the screenshot. i want you to builts a strategy around it as key to key level trading strategies works amazingly profitable. //@version=5
//@sbtnc thank you for doing the base code 
//Added additional levels for convienience sake. 
indicator('Key Levels SpacemanBTC IDWM', shorttitle='SpacemanBTC Key Level V13.1', overlay=true, max_lines_count=100)
//35 works
displayStyle = input.string(defval='Standard', title='Display Style', options=['Standard', 'Right Anchored'], inline='Display')
mergebool = input.bool(defval=true, title='Merge Levels?', inline='Display')
distanceright = input.int(defval=30, title='Distance', minval=5, maxval=500, inline='Dist')
radistance = input.int(defval=250, title='Anchor Distance', minval=5, maxval=500, inline='Dist')
labelsize = input.string(defval='Medium', title='Text Size', options=['Small', 'Medium', 'Large'])
linesize = input.string(defval='Small', title='Line Width', options=['Small', 'Medium', 'Large'], inline='Line')
linestyle = input.string(defval='Solid', title='Line Style', options=['Solid', 'Dashed', 'Dotted'], inline='Line')



GlobalTextType = input.bool(defval=false, title='Global Text ShortHand', tooltip='Enable for shorthand text on all text')
var globalcoloring = input.bool(defval=false, title='Global Coloring', tooltip='Enable for all color controls via one color', inline='GC')
GlobalColor = input.color(title='', defval=color.white, inline='GC')
//var show_tails = input(defval = false, title = "Always Show", type = input.bool)


[daily_time, daily_open] = request.security(syminfo.tickerid, 'D', [time, open], lookahead=barmerge.lookahead_on)
[dailyh_time, dailyh_open] = request.security(syminfo.tickerid, 'D', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[dailyl_time, dailyl_open] = request.security(syminfo.tickerid, 'D', [time[1], low[1]], lookahead=barmerge.lookahead_on)

cdailyh_open = request.security(syminfo.tickerid, 'D', high, lookahead=barmerge.lookahead_on)
cdailyl_open = request.security(syminfo.tickerid, 'D', low, lookahead=barmerge.lookahead_on)
var monday_time = time
var monday_high = high
var monday_low = low

[weekly_time, weekly_open] = request.security(syminfo.tickerid, 'W', [time, open], lookahead=barmerge.lookahead_on)
[weeklyh_time, weeklyh_open] = request.security(syminfo.tickerid, 'W', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[weeklyl_time, weeklyl_open] = request.security(syminfo.tickerid, 'W', [time[1], low[1]], lookahead=barmerge.lookahead_on)


[monthly_time, monthly_open] = request.security(syminfo.tickerid, 'M', [time, open], lookahead=barmerge.lookahead_on)
[monthlyh_time, monthlyh_open] = request.security(syminfo.tickerid, 'M', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[monthlyl_time, monthlyl_open] = request.security(syminfo.tickerid, 'M', [time[1], low[1]], lookahead=barmerge.lookahead_on)


[quarterly_time, quarterly_open] = request.security(syminfo.tickerid, '3M', [time, open], lookahead=barmerge.lookahead_on)
[quarterlyh_time, quarterlyh_open] = request.security(syminfo.tickerid, '3M', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[quarterlyl_time, quarterlyl_open] = request.security(syminfo.tickerid, '3M', [time[1], low[1]], lookahead=barmerge.lookahead_on)


[yearly_time, yearly_open] = request.security(syminfo.tickerid, '12M', [time, open], lookahead=barmerge.lookahead_on)
[yearlyh_time, yearlyh_open] = request.security(syminfo.tickerid, '12M', [time, high], lookahead=barmerge.lookahead_on)
[yearlyl_time, yearlyl_open] = request.security(syminfo.tickerid, '12M', [time, low], lookahead=barmerge.lookahead_on)


[intra_time, intra_open] = request.security(syminfo.tickerid, '240', [time, open], lookahead=barmerge.lookahead_on)
[intrah_time, intrah_open] = request.security(syminfo.tickerid, '240', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[intral_time, intral_open] = request.security(syminfo.tickerid, '240', [time[1], low[1]], lookahead=barmerge.lookahead_on)

//------------------------------ Inputs -------------------------------



var is_intra_enabled = input.bool(defval=false, title='Open', group='4H', inline='4H')
var is_intrarange_enabled = input.bool(defval=false, title='Prev H/L', group='4H', inline='4H')
var is_intram_enabled = input.bool(defval=false, title='Prev Mid', group='4H', inline='4H')
IntraTextType = input.bool(defval=false, title='ShortHand', group='4H', inline='4Hsh')

var is_daily_enabled = input.bool(defval=true, title='Open', group='Daily', inline='Daily')
var is_dailyrange_enabled = input.bool(defval=false, title='Prev H/L', group='Daily', inline='Daily')
var is_dailym_enabled = input.bool(defval=false, title='Prev Mid', group='Daily', inline='Daily')
DailyTextType = input.bool(defval=false, title='ShortHand', group='Daily', inline='Dailysh')

var is_monday_enabled = input.bool(defval=true, title='Range', group='Monday Range', inline='Monday')
var is_monday_mid = input.bool(defval=true, title='Mid', group='Monday Range', inline='Monday')
var untested_monday = false
MondayTextType = input.bool(defval=false, title='ShortHand', group='Monday Range', inline='Mondaysh')

var is_weekly_enabled = input.bool(defval=true, title='Open', group='Weekly', inline='Weekly')
var is_weeklyrange_enabled = input.bool(defval=true, title='Prev H/L', group='Weekly', inline='Weekly')
var is_weekly_mid = input.bool(defval=true, title='Prev Mid', group='Weekly', inline='Weekly')
WeeklyTextType = input.bool(defval=false, title='ShortHand', group='Weekly', inline='Weeklysh')

var is_monthly_enabled = input.bool(defval=true, title='Open', group='Monthly', inline='Monthly')
var is_monthlyrange_enabled = input.bool(defval=true, title='Prev H/L', group='Monthly', inline='Monthly')
var is_monthly_mid = input.bool(defval=true, title='Prev Mid', group='Monthly', inline='Monthly')
MonthlyTextType = input.bool(defval=false, title='ShortHand', group='Monthly', inline='Monthlysh')

var is_quarterly_enabled = input.bool(defval=true, title='Open', group='Quarterly', inline='Quarterly')
var is_quarterlyrange_enabled = input.bool(defval=false, title='Prev H/L', group='Quarterly', inline='Quarterly')
var is_quarterly_mid = input.bool(defval=true, title='Prev Mid', group='Quarterly', inline='Quarterly')
QuarterlyTextType = input.bool(defval=false, title='ShortHand', group='Quarterly', inline='Quarterlysh')

var is_yearly_enabled = input.bool(defval=true, title='Open', group='Yearly', inline='Yearly')
var is_yearlyrange_enabled = input.bool(defval=false, title='Current H/L', group='Yearly', inline='Yearly')
var is_yearly_mid = input.bool(defval=true, title='Mid', group='Yearly', inline='Yearly')
YearlyTextType = input.bool(defval=false, title='ShortHand', group='Yearly', inline='Yearlysh')

var is_londonrange_enabled = input.bool(defval=false, title='London Range', group='FX Sessions', inline='FX')
var is_usrange_enabled = input.bool(defval=false, title='New York Range', group='FX Sessions', inline='FX')
var is_asiarange_enabled = input.bool(defval=false, title='Asia Range', group='FX Sessions', inline='FX')
SessionTextType = input.bool(defval=false, title='ShortHand', group='FX Sessions', inline='FXColor')



Londont = input.session("0800-1600", "London Session")
USt = input.session("1400-2100", "New York Session")
Asiat = input.session("0000-0900", "Tokyo Session")

DailyColor = input.color(title='', defval=#08bcd4, group='Daily', inline='Dailysh')
MondayColor = input.color(title='', defval=color.white, group='Monday Range', inline='Mondaysh')
WeeklyColor = input.color(title='', defval=#fffcbc, group='Weekly', inline='Weeklysh')
MonthlyColor = input.color(title='', defval=#08d48c, group='Monthly', inline='Monthlysh')
YearlyColor = input.color(title='', defval=color.red, group='Yearly', inline='Yearlysh')
quarterlyColor = input.color(title='', defval=color.red, group='Quarterly', inline='Quarterlysh')
IntraColor = input.color(title='', defval=color.orange, group='4H', inline='4Hsh')
LondonColor = input.color(title='', defval=color.white, group='FX Sessions', inline='FXColor')
USColor = input.color(title='', defval=color.white, group='FX Sessions', inline='FXColor')
AsiaColor = input.color(title='', defval=color.white, group='FX Sessions', inline='FXColor')
var pdhtext = GlobalTextType or DailyTextType ? 'PDH' : 'Prev Day High'
var pdltext = GlobalTextType or DailyTextType ? 'PDL' : 'Prev Day Low'
var dotext = GlobalTextType or DailyTextType ? 'DO' : 'Daily Open'
var pdmtext = GlobalTextType or DailyTextType ? 'PDM' : 'Prev Day Mid'

var pwhtext = GlobalTextType or WeeklyTextType ? 'PWH' : 'Prev Week High'
var pwltext = GlobalTextType or WeeklyTextType ? 'PWL' : 'Prev Week Low'
var wotext = GlobalTextType or WeeklyTextType ? 'WO' : 'Weekly Open'
var pwmtext = GlobalTextType or WeeklyTextType ? 'PWM' : 'Prev Week Mid'

var pmhtext = GlobalTextType or MonthlyTextType ? 'PMH' : 'Prev Month High'
var pmltext = GlobalTextType or MonthlyTextType ? 'PML' : 'Prev Month Low'
var motext = GlobalTextType or MonthlyTextType ? 'MO' : 'Monthly Open'
var pmmtext = GlobalTextType or MonthlyTextType ? 'PMM' : 'Prev Month Mid'

var pqhtext = GlobalTextType or QuarterlyTextType ? 'PQH' : 'Prev Quarter High'
var pqltext = GlobalTextType or QuarterlyTextType ? 'PQL' : 'Prev Quarter Low'
var qotext = GlobalTextType or QuarterlyTextType ? 'QO' : 'Quarterly Open'
var pqmtext = GlobalTextType or QuarterlyTextType ? 'PQM' : 'Prev Quarter Mid'

var cyhtext = GlobalTextType or YearlyTextType ? 'CYH' : 'Current Year High'
var cyltext = GlobalTextType or YearlyTextType ? 'CYL' : 'Current Year Low'
var yotext = GlobalTextType or YearlyTextType ? 'YO' : 'Yearly Open'
var cymtext = GlobalTextType or YearlyTextType ? 'CYM' : 'Current Year Mid'

var pihtext = GlobalTextType or IntraTextType ? 'P-4H-H' : 'Prev 4H High'
var piltext = GlobalTextType or IntraTextType ? 'P-4H-L' : 'Prev 4H Low'
var iotext = GlobalTextType or IntraTextType ? '4H-O' : '4H Open'
var pimtext = GlobalTextType or IntraTextType ? 'P-4H-M' : 'Prev 4H Mid'

var pmonhtext = GlobalTextType or MondayTextType ? 'MDAY-H' : 'Monday High'
var pmonltext = GlobalTextType or MondayTextType ? 'MDAY-L' : 'Monday Low'
var pmonmtext = GlobalTextType or MondayTextType ? 'MDAY-M' : 'Monday Mid'

var lhtext = GlobalTextType or SessionTextType ? 'Lon-H' : 'London High'
var lltext = GlobalTextType or SessionTextType ? 'Lon-L' : 'London Low'
var lotext = GlobalTextType or SessionTextType ? 'Lon-O' : 'London Open'


var ushtext = GlobalTextType or SessionTextType ? 'NY-H' : 'New York High'
var usltext = GlobalTextType or SessionTextType ? 'NY-L' : 'New York Low'
var usotext = GlobalTextType or SessionTextType ? 'NY-O' : 'New York Open'

var asiahtext = GlobalTextType or SessionTextType ? 'AS-H' : 'Asia High'
var asialtext = GlobalTextType or SessionTextType ? 'AS-L' : 'Asia Low'
var asiaotext = GlobalTextType or SessionTextType ? 'AS-O' : 'Asia Open'

if globalcoloring == true
    DailyColor := GlobalColor
    MondayColor := GlobalColor
    WeeklyColor := GlobalColor
    MonthlyColor := GlobalColor
    YearlyColor := GlobalColor
    quarterlyColor := GlobalColor
    IntraColor := GlobalColor
    IntraColor


if weekly_time != weekly_time[1]
    untested_monday := false
    untested_monday

if is_monday_enabled == true and untested_monday == false
    untested_monday := true
    monday_time := daily_time
    monday_high := cdailyh_open
    monday_low := cdailyl_open
    monday_low


linewidthint = 1
if linesize == 'Small'
    linewidthint := 1
    linewidthint
if linesize == 'Medium'
    linewidthint := 2
    linewidthint
if linesize == 'Large'
    linewidthint := 3
    linewidthint

var DEFAULT_LINE_WIDTH = linewidthint
var DEFAULT_TAIL_WIDTH = linewidthint

fontsize = size.small

if labelsize == 'Small'
    fontsize := size.small
    fontsize

if labelsize == 'Medium'
    fontsize := size.normal
    fontsize

if labelsize == 'Large'
    fontsize := size.large
    fontsize

linestyles = line.style_solid
if linestyle == 'Dashed'
    linestyles := line.style_dashed
    linestyles

if linestyle == 'Dotted'
    linestyles := line.style_dotted
    linestyles



var DEFAULT_LABEL_SIZE = fontsize
var DEFAULT_LABEL_STYLE = label.style_none
var DEFAULT_EXTEND_RIGHT = distanceright







London = time(timeframe.period, Londont)
US = time(timeframe.period, USt)
Asia = time(timeframe.period, Asiat)

var clondonhigh = 0.0
var clondonlow = close
var londontime = time
var flondonhigh = 0.0
var flondonlow = 0.0
var flondonopen = 0.0

var onelondonfalse = false
if London
    if high > clondonhigh
        clondonhigh := high
        clondonhigh
    if low < clondonlow
        clondonlow := low
        clondonlow
    if onelondonfalse
        londontime := time
        flondonopen := open
        flondonopen
    flondonhigh := clondonhigh
    flondonlow := clondonlow
    onelondonfalse := false
    onelondonfalse
else
    if onelondonfalse == false
        flondonhigh := clondonhigh
        flondonlow := clondonlow
        flondonlow
    onelondonfalse := true

    clondonhigh := 0.0
    clondonlow := close
    clondonlow

//////////////////////////////////
var cushigh = 0.0
var cuslow = close
var ustime = time
var fushigh = 0.0
var fuslow = 0.0
var fusopen = 0.0

var oneusfalse = false
if US
    if high > cushigh
        cushigh := high
        cushigh
    if low < cuslow
        cuslow := low
        cuslow
    if oneusfalse
        ustime := time
        fusopen := open
        fusopen
    fushigh := cushigh
    fuslow := cuslow
    oneusfalse := false
    oneusfalse
else
    if oneusfalse == false
        fushigh := cushigh
        fuslow := cuslow
        fuslow
    oneusfalse := true

    cushigh := 0.0
    cuslow := close
    cuslow

//////////////////////////////////
var casiahigh = 0.0
var casialow = close
var asiatime = time
var fasiahigh = 0.0
var fasialow = 0.0
var fasiaopen = 0.0

var oneasiafalse = false
if Asia
    if high > casiahigh
        casiahigh := high
        casiahigh
    if low < casialow
        casialow := low
        casialow
    if oneasiafalse
        asiatime := time
        fasiaopen := open
        fasiaopen
    fasiahigh := casiahigh
    fasialow := casialow
    oneasiafalse := false
    oneasiafalse
else
    if oneasiafalse == false
        fasiahigh := casiahigh
        fasialow := casialow
        fasialow
    oneasiafalse := true

    casiahigh := 0.0
    casialow := close
    casialow

//------------------------------ Plotting ------------------------------
var pricearray = array.new_float(0)
var labelarray = array.new_label(0)
f_LevelMerge(pricearray, labelarray, currentprice, currentlabel, currentcolor) =>
    if array.includes(pricearray, currentprice)
        whichindex = array.indexof(pricearray, currentprice)
        labelhold = array.get(labelarray, whichindex)
        whichtext = label.get_text(labelhold)

        label.set_text(labelhold, label.get_text(currentlabel) + ' / ' + whichtext)
        label.set_text(currentlabel, '')
        label.set_textcolor(labelhold, currentcolor)
    else
        array.push(pricearray, currentprice)
        array.push(labelarray, currentlabel)


var can_show_daily = is_daily_enabled and timeframe.isintraday
var can_show_weekly = is_weekly_enabled and not timeframe.isweekly and not timeframe.ismonthly
var can_show_monthly = is_monthly_enabled and not timeframe.ismonthly

get_limit_right(bars) =>
    timenow + (time - time[1]) * bars

// the following code doesn't need to be processed on every candle
if barstate.islast
    is_weekly_open = dayofweek == dayofweek.monday
    is_monthly_open = dayofmonth == 1
    can_draw_daily = (is_weekly_enabled ? not is_weekly_open : true) and (is_monthly_enabled ? not is_monthly_open : true)
    can_draw_weekly = is_monthly_enabled ? not(is_monthly_open and is_weekly_open) : true
    can_draw_intra = is_intra_enabled
    can_draw_intrah = is_intrarange_enabled
    can_draw_intral = is_intrarange_enabled
    can_draw_intram = is_intram_enabled
    pricearray := array.new_float(0)
    labelarray := array.new_label(0)

    /////////////////////////////////

    if is_londonrange_enabled
        //label.new(bar_index,high)
        london_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)


        if displayStyle == 'Right Anchored'
            londontime := get_limit_right(radistance)
            londontime

        var londonh_line = line.new(x1=londontime, x2=london_limit_right, y1=flondonhigh, y2=flondonhigh, color=LondonColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var londonl_line = line.new(x1=londontime, x2=london_limit_right, y1=flondonlow, y2=flondonlow, color=LondonColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var londono_line = line.new(x1=londontime, x2=london_limit_right, y1=flondonopen, y2=flondonopen, color=LondonColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var londonh_label = label.new(x=london_limit_right, y=flondonhigh, text=lhtext, style=DEFAULT_LABEL_STYLE, textcolor=LondonColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var londonl_label = label.new(x=london_limit_right, y=flondonlow, text=lltext, style=DEFAULT_LABEL_STYLE, textcolor=LondonColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var londono_label = label.new(x=london_limit_right, y=flondonopen, text=lotext, style=DEFAULT_LABEL_STYLE, textcolor=LondonColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(londonh_line, londontime)
        line.set_x2(londonh_line, london_limit_right)
        line.set_y1(londonh_line, flondonhigh)
        line.set_y2(londonh_line, flondonhigh)
        line.set_x1(londonl_line, londontime)
        line.set_x2(londonl_line, london_limit_right)
        line.set_y1(londonl_line, flondonlow)
        line.set_y2(londonl_line, flondonlow)
        line.set_x1(londono_line, londontime)
        line.set_x2(londono_line, london_limit_right)
        line.set_y1(londono_line, flondonopen)
        line.set_y2(londono_line, flondonopen)
        
        label.set_x(londonh_label, london_limit_right)
        label.set_y(londonh_label, flondonhigh)
        label.set_text(londonh_label, lhtext)
        label.set_x(londonl_label, london_limit_right)
        label.set_y(londonl_label, flondonlow)
        label.set_text(londonl_label, lltext)
        label.set_x(londono_label, london_limit_right)
        label.set_y(londono_label, flondonopen)
        label.set_text(londono_label, lotext)
        
        if mergebool
            f_LevelMerge(pricearray, labelarray, flondonhigh, londonh_label, LondonColor)
            f_LevelMerge(pricearray, labelarray, flondonlow, londonl_label, LondonColor)
            f_LevelMerge(pricearray, labelarray, flondonopen, londono_label, LondonColor)
//////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////

    if is_usrange_enabled
        //label.new(bar_index,high)
        us_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)


        if displayStyle == 'Right Anchored'
            ustime := get_limit_right(radistance)
            ustime

        var ush_line = line.new(x1=ustime, x2=us_limit_right, y1=fushigh, y2=fushigh, color=USColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var usl_line = line.new(x1=ustime, x2=us_limit_right, y1=fuslow, y2=fuslow, color=USColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var uso_line = line.new(x1=ustime, x2=us_limit_right, y1=fusopen, y2=fusopen, color=USColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var ush_label = label.new(x=us_limit_right, y=fushigh, text=lhtext, style=DEFAULT_LABEL_STYLE, textcolor=USColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var usl_label = label.new(x=us_limit_right, y=fuslow, text=lltext, style=DEFAULT_LABEL_STYLE, textcolor=USColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var uso_label = label.new(x=us_limit_right, y=fusopen, text=lotext, style=DEFAULT_LABEL_STYLE, textcolor=USColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(ush_line, ustime)
        line.set_x2(ush_line, us_limit_right)
        line.set_y1(ush_line, fushigh)
        line.set_y2(ush_line, fushigh)
        
        line.set_x1(usl_line, ustime)
        line.set_x2(usl_line, us_limit_right)
        line.set_y1(usl_line, fuslow)
        line.set_y2(usl_line, fuslow)
        
        line.set_x1(uso_line, ustime)
        line.set_x2(uso_line, us_limit_right)
        line.set_y1(uso_line, fusopen)
        line.set_y2(uso_line, fusopen)
        
        
        label.set_x(ush_label, us_limit_right)
        label.set_y(ush_label, fushigh)
        label.set_text(ush_label, ushtext)
        label.set_x(usl_label, us_limit_right)
        label.set_y(usl_label, fuslow)
        label.set_text(usl_label, usltext)
        label.set_x(uso_label, us_limit_right)
        label.set_y(uso_label, fusopen)
        label.set_text(uso_label, usotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, fushigh, ush_label, USColor)
            f_LevelMerge(pricearray, labelarray, fuslow, usl_label, USColor)
            f_LevelMerge(pricearray, labelarray, fusopen, uso_label, USColor)
    /////////////////////////////////

    if is_asiarange_enabled
        //label.new(bar_index,high)
        asia_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)


        if displayStyle == 'Right Anchored'
            asiatime := get_limit_right(radistance)
            asiatime

        var asiah_line = line.new(x1=asiatime, x2=asia_limit_right, y1=fasiahigh, y2=fasiahigh, color=AsiaColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var asial_line = line.new(x1=asiatime, x2=asia_limit_right, y1=fasialow, y2=fasialow, color=AsiaColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var asiao_line = line.new(x1=asiatime, x2=asia_limit_right, y1=fasiaopen, y2=fasiaopen, color=AsiaColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var asiah_label = label.new(x=asia_limit_right, y=fasiahigh, text=asiahtext, style=DEFAULT_LABEL_STYLE, textcolor=AsiaColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var asial_label = label.new(x=asia_limit_right, y=fasialow, text=asialtext, style=DEFAULT_LABEL_STYLE, textcolor=AsiaColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var asiao_label = label.new(x=asia_limit_right, y=fasiaopen, text=asiaotext, style=DEFAULT_LABEL_STYLE, textcolor=AsiaColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(asiah_line, asiatime)
        line.set_x2(asiah_line, asia_limit_right)
        line.set_y1(asiah_line, fasiahigh)
        line.set_y2(asiah_line, fasiahigh)
        
        line.set_x1(asial_line, asiatime)
        line.set_x2(asial_line, asia_limit_right)
        line.set_y1(asial_line, fasialow)
        line.set_y2(asial_line, fasialow)
        
        line.set_x1(asiao_line, asiatime)
        line.set_x2(asiao_line, asia_limit_right)
        line.set_y1(asiao_line, fasiaopen)
        line.set_y2(asiao_line, fasiaopen)
        
        
        label.set_x(asiah_label, asia_limit_right)
        label.set_y(asiah_label, fasiahigh)
        label.set_text(asiah_label, asiahtext)
        label.set_x(asial_label, asia_limit_right)
        label.set_y(asial_label, fasialow)
        label.set_text(asial_label, asialtext)
        label.set_x(asiao_label, asia_limit_right)
        label.set_y(asiao_label, fasiaopen)
        label.set_text(asiao_label, asiaotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, fasiahigh, asiah_label, AsiaColor)
            f_LevelMerge(pricearray, labelarray, fasialow, asial_label, AsiaColor)
            f_LevelMerge(pricearray, labelarray, fasiaopen, asiao_label, AsiaColor)
//////////////////////////////////////////////////////////////////////////////////            
            
//////////////////////////////////////////////////////////////////////////////////
    if can_draw_intra
        intra_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            intra_time := get_limit_right(radistance)
            intra_time


        var intra_line = line.new(x1=intra_time, x2=intra_limit_right, y1=intra_open, y2=intra_open, color=IntraColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var intra_label = label.new(x=intra_limit_right, y=intra_open, text=iotext, style=DEFAULT_LABEL_STYLE, textcolor=IntraColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(intra_line, intra_time)
        line.set_x2(intra_line, intra_limit_right)
        line.set_y1(intra_line, intra_open)
        line.set_y2(intra_line, intra_open)
        label.set_x(intra_label, intra_limit_right)
        label.set_y(intra_label, intra_open)
        label.set_text(intra_label, iotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, intra_open, intra_label, IntraColor)


//////////////////////////////////////////////////////////////////////////////////
//HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH
    if can_draw_intrah
        intrah_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            intrah_time := get_limit_right(radistance)
            intrah_time



        var intrah_line = line.new(x1=intrah_time, x2=intrah_limit_right, y1=intrah_open, y2=intrah_open, color=IntraColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var intrah_label = label.new(x=intrah_limit_right, y=intrah_open, text=pihtext, style=DEFAULT_LABEL_STYLE, textcolor=IntraColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(intrah_line, intrah_time)
        line.set_x2(intrah_line, intrah_limit_right)
        line.set_y1(intrah_line, intrah_open)
        line.set_y2(intrah_line, intrah_open)
        label.set_x(intrah_label, intrah_limit_right)
        label.set_y(intrah_label, intrah_open)
        label.set_text(intrah_label, pihtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, intrah_open, intrah_label, IntraColor)

//////////////////////////////////////////////////////////////////////////////////
//LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW
    if can_draw_intral
        intral_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            intral_time := get_limit_right(radistance)
            intral_time



        var intral_line = line.new(x1=intral_time, x2=intral_limit_right, y1=intral_open, y2=intral_open, color=IntraColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var intral_label = label.new(x=intral_limit_right, y=intral_open, text=piltext, style=DEFAULT_LABEL_STYLE, textcolor=IntraColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(intral_line, intral_time)
        line.set_x2(intral_line, intral_limit_right)
        line.set_y1(intral_line, intral_open)
        line.set_y2(intral_line, intral_open)
        label.set_x(intral_label, intral_limit_right)
        label.set_y(intral_label, intral_open)
        label.set_text(intral_label, piltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, intral_open, intral_label, IntraColor)

///////////////////////////////////////////////////////////////////////////////   

    if can_draw_intram
        intram_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        intram_time = intrah_time
        intram_open = (intral_open + intrah_open) / 2
        if displayStyle == 'Right Anchored'
            intram_time := get_limit_right(radistance)
            intram_time

        var intram_line = line.new(x1=intram_time, x2=intram_limit_right, y1=intram_open, y2=intram_open, color=IntraColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var intram_label = label.new(x=intram_limit_right, y=intram_open, text=pimtext, style=DEFAULT_LABEL_STYLE, textcolor=IntraColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(intram_line, intram_time)
        line.set_x2(intram_line, intram_limit_right)
        line.set_y1(intram_line, intram_open)
        line.set_y2(intram_line, intram_open)
        label.set_x(intram_label, intram_limit_right)
        label.set_y(intram_label, intram_open)
        label.set_text(intram_label, pimtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, intram_open, intram_label, IntraColor)

////////////////////////////////////////// MONDAY

    if is_monday_enabled
        monday_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monday_time := get_limit_right(radistance)
            monday_time

        var monday_line = line.new(x1=monday_time, x2=monday_limit_right, y1=monday_high, y2=monday_high, color=MondayColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monday_label = label.new(x=monday_limit_right, y=monday_high, text=pmonhtext, style=DEFAULT_LABEL_STYLE, textcolor=MondayColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monday_line, monday_time)
        line.set_x2(monday_line, monday_limit_right)
        line.set_y1(monday_line, monday_high)
        line.set_y2(monday_line, monday_high)
        label.set_x(monday_label, monday_limit_right)
        label.set_y(monday_label, monday_high)
        label.set_text(monday_label, pmonhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monday_high, monday_label, MondayColor)


    if is_monday_enabled
        monday_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monday_time := get_limit_right(radistance)
            monday_time



        var monday_low_line = line.new(x1=monday_time, x2=monday_limit_right, y1=monday_low, y2=monday_low, color=MondayColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monday_low_label = label.new(x=monday_limit_right, y=monday_low, text=pmonltext, style=DEFAULT_LABEL_STYLE, textcolor=MondayColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monday_low_line, monday_time)
        line.set_x2(monday_low_line, monday_limit_right)
        line.set_y1(monday_low_line, monday_low)
        line.set_y2(monday_low_line, monday_low)
        label.set_x(monday_low_label, monday_limit_right)
        label.set_y(monday_low_label, monday_low)
        label.set_text(monday_low_label, pmonltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monday_low, monday_low_label, MondayColor)



    if is_monday_mid
        mondaym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)

        mondaym_open = (monday_high + monday_low) / 2
        if displayStyle == 'Right Anchored'
            monday_time := get_limit_right(radistance)
            monday_time

        var mondaym_line = line.new(x1=monday_time, x2=mondaym_limit_right, y1=mondaym_open, y2=mondaym_open, color=MondayColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var mondaym_label = label.new(x=mondaym_limit_right, y=mondaym_open, text=pmonmtext, style=DEFAULT_LABEL_STYLE, textcolor=MondayColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(mondaym_line, monday_time)
        line.set_x2(mondaym_line, mondaym_limit_right)
        line.set_y1(mondaym_line, mondaym_open)
        line.set_y2(mondaym_line, mondaym_open)
        label.set_x(mondaym_label, mondaym_limit_right)
        label.set_y(mondaym_label, mondaym_open)
        label.set_text(mondaym_label, pmonmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, mondaym_open, mondaym_label, MondayColor)


//////////////////////////////////////////////////////////////////////////////////
////////////////////////DAILY OPEN DAILY OPEN DAILY OPEN DAILY OPEN DAILY OPEN DAILY OPEN DAILY OPEN

    if is_daily_enabled
        daily_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            daily_time := get_limit_right(radistance)
            daily_time

        var daily_line = line.new(x1=daily_time, x2=daily_limit_right, y1=daily_open, y2=daily_open, color=DailyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var daily_label = label.new(x=daily_limit_right, y=daily_open, text=dotext, style=DEFAULT_LABEL_STYLE, textcolor=DailyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(daily_line, daily_time)
        line.set_x2(daily_line, daily_limit_right)
        line.set_y1(daily_line, daily_open)
        line.set_y2(daily_line, daily_open)
        label.set_x(daily_label, daily_limit_right)
        label.set_y(daily_label, daily_open)
        label.set_text(daily_label, dotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, daily_open, daily_label, DailyColor)

//////////////////////////////////////////////////////////////////////////////////
//////////////////DAILY HIGH DAILY HIGH DAILY HIGH DAILY HIGH DAILY HIGH DAILY HIGH DAILY HIGH 

    if is_dailyrange_enabled
        dailyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            dailyh_time := get_limit_right(radistance)
            dailyh_time
        // draw tails before lines for better visual


        var dailyh_line = line.new(x1=dailyh_time, x2=dailyh_limit_right, y1=dailyh_open, y2=dailyh_open, color=DailyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var dailyh_label = label.new(x=dailyh_limit_right, y=dailyh_open, text=pdhtext, style=DEFAULT_LABEL_STYLE, textcolor=DailyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(dailyh_line, dailyh_time)
        line.set_x2(dailyh_line, dailyh_limit_right)
        line.set_y1(dailyh_line, dailyh_open)
        line.set_y2(dailyh_line, dailyh_open)
        label.set_x(dailyh_label, dailyh_limit_right)
        label.set_y(dailyh_label, dailyh_open)
        label.set_text(dailyh_label, pdhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, dailyh_open, dailyh_label, DailyColor)


//////////////////////////////////////////////////////////////////////////////////
//////////////////DAILY LOW DAILY LOW DAILY LOW DAILY LOW DAILY LOW DAILY LOW DAILY LOW DAILY LOW 

    if is_dailyrange_enabled
        dailyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            dailyl_time := get_limit_right(radistance)
            dailyl_time


        var dailyl_line = line.new(x1=dailyl_time, x2=dailyl_limit_right, y1=dailyl_open, y2=dailyl_open, color=DailyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var dailyl_label = label.new(x=dailyl_limit_right, y=dailyl_open, text=pdltext, style=DEFAULT_LABEL_STYLE, textcolor=DailyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(dailyl_line, dailyl_time)
        line.set_x2(dailyl_line, dailyl_limit_right)
        line.set_y1(dailyl_line, dailyl_open)
        line.set_y2(dailyl_line, dailyl_open)
        label.set_x(dailyl_label, dailyl_limit_right)
        label.set_y(dailyl_label, dailyl_open)
        label.set_text(dailyl_label, pdltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, dailyl_open, dailyl_label, DailyColor)



//////////////////////////////////////////////////////////////////////////////// Daily MID

    if is_dailym_enabled
        dailym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        dailym_time = dailyh_time
        dailym_open = (dailyl_open + dailyh_open) / 2
        if displayStyle == 'Right Anchored'
            dailym_time := get_limit_right(radistance)
            dailym_time
        var dailym_line = line.new(x1=dailym_time, x2=dailym_limit_right, y1=dailym_open, y2=dailym_open, color=DailyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var dailym_label = label.new(x=dailym_limit_right, y=dailym_open, text=pdmtext, style=DEFAULT_LABEL_STYLE, textcolor=DailyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(dailym_line, dailym_time)
        line.set_x2(dailym_line, dailym_limit_right)
        line.set_y1(dailym_line, dailym_open)
        line.set_y2(dailym_line, dailym_open)
        label.set_x(dailym_label, dailym_limit_right)
        label.set_y(dailym_label, dailym_open)
        label.set_text(dailym_label, pdmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, dailym_open, dailym_label, DailyColor)


//////////////////////////////////////////////////////////////////////////////////


    if is_weekly_enabled
        weekly_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        cweekly_time = weekly_time
        if displayStyle == 'Right Anchored'
            cweekly_time := get_limit_right(radistance)
            cweekly_time


        var weekly_line = line.new(x1=cweekly_time, x2=weekly_limit_right, y1=weekly_open, y2=weekly_open, color=WeeklyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var weekly_label = label.new(x=weekly_limit_right, y=weekly_open, text=wotext, style=DEFAULT_LABEL_STYLE, textcolor=WeeklyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(weekly_line, cweekly_time)
        line.set_x2(weekly_line, weekly_limit_right)
        line.set_y1(weekly_line, weekly_open)
        line.set_y2(weekly_line, weekly_open)
        label.set_x(weekly_label, weekly_limit_right)
        label.set_y(weekly_label, weekly_open)
        label.set_text(weekly_label, wotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, weekly_open, weekly_label, WeeklyColor)
        // the weekly open can be the daily open too (monday)
        // only the weekly will be draw, in these case we update its label
    // if is_weekly_open and can_show_daily
            // label.set_text(weekly_label, "DO / WO            ")

//////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////// WEEKLY HIGH WEEKLY HIGH WEEKLY HIGH


    if is_weeklyrange_enabled
        weeklyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            weeklyh_time := get_limit_right(radistance)
            weeklyh_time


        var weeklyh_line = line.new(x1=weeklyh_time, x2=weeklyh_limit_right, y1=weeklyh_open, y2=weeklyh_open, color=WeeklyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var weeklyh_label = label.new(x=weeklyh_limit_right, y=weeklyh_open, text=pwhtext, style=DEFAULT_LABEL_STYLE, textcolor=WeeklyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(weeklyh_line, weeklyh_time)
        line.set_x2(weeklyh_line, weeklyh_limit_right)
        line.set_y1(weeklyh_line, weeklyh_open)
        line.set_y2(weeklyh_line, weeklyh_open)
        label.set_x(weeklyh_label, weeklyh_limit_right)
        label.set_y(weeklyh_label, weeklyh_open)
        label.set_text(weeklyh_label, pwhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, weeklyh_open, weeklyh_label, WeeklyColor)

//////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////// WEEKLY LOW WEEKLY LOW WEEKLY LOW


    if is_weeklyrange_enabled
        weeklyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            weeklyl_time := get_limit_right(radistance)
            weeklyl_time


        var weeklyl_line = line.new(x1=weeklyl_time, x2=weeklyl_limit_right, y1=weekly_open, y2=weekly_open, color=WeeklyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var weeklyl_label = label.new(x=weeklyl_limit_right, y=weeklyl_open, text=pwltext, style=DEFAULT_LABEL_STYLE, textcolor=WeeklyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(weeklyl_line, weeklyl_time)
        line.set_x2(weeklyl_line, weeklyl_limit_right)
        line.set_y1(weeklyl_line, weeklyl_open)
        line.set_y2(weeklyl_line, weeklyl_open)
        label.set_x(weeklyl_label, weeklyl_limit_right)
        label.set_y(weeklyl_label, weeklyl_open)
        label.set_text(weeklyl_label, pwltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, weeklyl_open, weeklyl_label, WeeklyColor)



//////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////// Weekly MID

    if is_weekly_mid
        weeklym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        weeklym_time = weeklyh_time
        weeklym_open = (weeklyl_open + weeklyh_open) / 2
        if displayStyle == 'Right Anchored'
            weeklym_time := get_limit_right(radistance)
            weeklym_time

        var weeklym_line = line.new(x1=weeklym_time, x2=weeklym_limit_right, y1=weeklym_open, y2=weeklym_open, color=WeeklyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var weeklym_label = label.new(x=weeklym_limit_right, y=weeklym_open, text=pwmtext, style=DEFAULT_LABEL_STYLE, textcolor=WeeklyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(weeklym_line, weeklym_time)
        line.set_x2(weeklym_line, weeklym_limit_right)
        line.set_y1(weeklym_line, weeklym_open)
        line.set_y2(weeklym_line, weeklym_open)
        label.set_x(weeklym_label, weeklym_limit_right)
        label.set_y(weeklym_label, weeklym_open)
        label.set_text(weeklym_label, pwmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, weeklym_open, weeklym_label, WeeklyColor)
////////////////////////////////////////////////////////////////////////////////// YEEEAARRLLYY LOW LOW LOW


    if is_yearlyrange_enabled
        yearlyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            yearlyl_time := get_limit_right(radistance)
            yearlyl_time


        var yearlyl_line = line.new(x1=yearlyl_time, x2=yearlyl_limit_right, y1=yearlyl_open, y2=yearlyl_open, color=YearlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var yearlyl_label = label.new(x=yearlyl_limit_right, y=yearlyl_open, text=cyltext, style=DEFAULT_LABEL_STYLE, textcolor=YearlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(yearlyl_line, yearlyl_time)
        line.set_x2(yearlyl_line, yearlyl_limit_right)
        line.set_y1(yearlyl_line, yearlyl_open)
        line.set_y2(yearlyl_line, yearlyl_open)
        label.set_x(yearlyl_label, yearlyl_limit_right)
        label.set_y(yearlyl_label, yearlyl_open)
        label.set_text(yearlyl_label, cyltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, yearlyl_open, yearlyl_label, YearlyColor)



//////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////// YEEEAARRLLYY HIGH HIGH HIGH


    if is_yearlyrange_enabled
        yearlyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            yearlyh_time := get_limit_right(radistance)
            yearlyh_time


        var yearlyh_line = line.new(x1=yearlyh_time, x2=yearlyh_limit_right, y1=yearlyh_open, y2=yearlyh_open, color=YearlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var yearlyh_label = label.new(x=yearlyh_limit_right, y=yearlyh_open, text=cyhtext, style=DEFAULT_LABEL_STYLE, textcolor=YearlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(yearlyh_line, yearlyh_time)
        line.set_x2(yearlyh_line, yearlyh_limit_right)
        line.set_y1(yearlyh_line, yearlyh_open)
        line.set_y2(yearlyh_line, yearlyh_open)
        label.set_x(yearlyh_label, yearlyh_limit_right)
        label.set_y(yearlyh_label, yearlyh_open)
        label.set_text(yearlyh_label, cyhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, yearlyh_open, yearlyh_label, YearlyColor)



//////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////// YEEEAARRLLYY OPEN


    if is_yearly_enabled
        yearly_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            yearly_time := get_limit_right(radistance)
            yearly_time


        var yearly_line = line.new(x1=yearly_time, x2=yearly_limit_right, y1=yearly_open, y2=yearly_open, color=YearlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)

        var yearly_label = label.new(x=yearly_limit_right, y=yearly_open, text=yotext, style=DEFAULT_LABEL_STYLE, textcolor=YearlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)



        line.set_x1(yearly_line, yearly_time)
        line.set_x2(yearly_line, yearly_limit_right)
        line.set_y1(yearly_line, yearly_open)
        line.set_y2(yearly_line, yearly_open)
        label.set_x(yearly_label, yearly_limit_right)
        label.set_y(yearly_label, yearly_open)
        label.set_text(yearly_label, yotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, yearly_open, yearly_label, YearlyColor)



//////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////// yearly MID

    if is_yearly_mid
        yearlym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        yearlym_time = yearlyh_time
        yearlym_open = (yearlyl_open + yearlyh_open) / 2
        if displayStyle == 'Right Anchored'
            yearlym_time := get_limit_right(radistance)
            yearlym_time

        var yearlym_line = line.new(x1=yearlym_time, x2=yearlym_limit_right, y1=yearlym_open, y2=yearlym_open, color=YearlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var yearlym_label = label.new(x=yearlym_limit_right, y=yearlym_open, text=cymtext, style=DEFAULT_LABEL_STYLE, textcolor=YearlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(yearlym_line, yearlym_time)
        line.set_x2(yearlym_line, yearlym_limit_right)
        line.set_y1(yearlym_line, yearlym_open)
        line.set_y2(yearlym_line, yearlym_open)
        label.set_x(yearlym_label, yearlym_limit_right)
        label.set_y(yearlym_label, yearlym_open)
        label.set_text(yearlym_label, cymtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, yearlym_open, yearlym_label, YearlyColor)


////////////////////////////////////////////////////////////////////////////////// QUATERLLYYYYY OPEN


    if is_quarterly_enabled
        quarterly_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            quarterly_time := get_limit_right(radistance)
            quarterly_time


        var quarterly_line = line.new(x1=quarterly_time, x2=quarterly_limit_right, y1=quarterly_open, y2=quarterly_open, color=quarterlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var quarterly_label = label.new(x=quarterly_limit_right, y=quarterly_open, text=qotext, style=DEFAULT_LABEL_STYLE, textcolor=quarterlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(quarterly_line, quarterly_time)
        line.set_x2(quarterly_line, quarterly_limit_right)
        line.set_y1(quarterly_line, quarterly_open)
        line.set_y2(quarterly_line, quarterly_open)
        label.set_x(quarterly_label, quarterly_limit_right)
        label.set_y(quarterly_label, quarterly_open)
        label.set_text(quarterly_label, qotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, quarterly_open, quarterly_label, quarterlyColor)



//////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////// QUATERLLYYYYY High


    if is_quarterlyrange_enabled
        quarterlyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            quarterlyh_time := get_limit_right(radistance)
            quarterlyh_time


        var quarterlyh_line = line.new(x1=quarterlyh_time, x2=quarterlyh_limit_right, y1=quarterlyh_open, y2=quarterlyh_open, color=quarterlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var quarterlyh_label = label.new(x=quarterlyh_limit_right, y=quarterlyh_open, text=pqhtext, style=DEFAULT_LABEL_STYLE, textcolor=quarterlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(quarterlyh_line, quarterlyh_time)
        line.set_x2(quarterlyh_line, quarterlyh_limit_right)
        line.set_y1(quarterlyh_line, quarterlyh_open)
        line.set_y2(quarterlyh_line, quarterlyh_open)
        label.set_x(quarterlyh_label, quarterlyh_limit_right)
        label.set_y(quarterlyh_label, quarterlyh_open)
        label.set_text(quarterlyh_label, pqhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, quarterlyh_open, quarterlyh_label, quarterlyColor)



//////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////// QUATERLLYYYYY Low


    if is_quarterlyrange_enabled
        quarterlyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            quarterlyl_time := get_limit_right(radistance)
            quarterlyl_time


        var quarterlyl_line = line.new(x1=quarterlyl_time, x2=quarterlyl_limit_right, y1=quarterlyl_open, y2=quarterlyl_open, color=quarterlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var quarterlyl_label = label.new(x=quarterlyl_limit_right, y=quarterlyl_open, text=pqltext, style=DEFAULT_LABEL_STYLE, textcolor=quarterlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(quarterlyl_line, quarterlyl_time)
        line.set_x2(quarterlyl_line, quarterlyl_limit_right)
        line.set_y1(quarterlyl_line, quarterlyl_open)
        line.set_y2(quarterlyl_line, quarterlyl_open)
        label.set_x(quarterlyl_label, quarterlyl_limit_right)
        label.set_y(quarterlyl_label, quarterlyl_open)

        label.set_text(quarterlyl_label, pqltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, quarterlyl_open, quarterlyl_label, quarterlyColor)



//////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////// QUATERLLYYYYY MID

    if is_quarterly_mid
        quarterlym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        quarterlym_time = quarterlyh_time
        quarterlym_open = (quarterlyl_open + quarterlyh_open) / 2
        if displayStyle == 'Right Anchored'
            quarterlym_time := get_limit_right(radistance)
            quarterlym_time
        var quarterlym_line = line.new(x1=quarterlym_time, x2=quarterlym_limit_right, y1=quarterlym_open, y2=quarterlym_open, color=quarterlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var quarterlym_label = label.new(x=quarterlym_limit_right, y=quarterlym_open, text=pqmtext, style=DEFAULT_LABEL_STYLE, textcolor=quarterlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(quarterlym_line, quarterlym_time)
        line.set_x2(quarterlym_line, quarterlym_limit_right)
        line.set_y1(quarterlym_line, quarterlym_open)
        line.set_y2(quarterlym_line, quarterlym_open)
        label.set_x(quarterlym_label, quarterlym_limit_right)
        label.set_y(quarterlym_label, quarterlym_open)

        label.set_text(quarterlym_label, pqmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, quarterlym_open, quarterlym_label, quarterlyColor)

////////////////////////////////////////////////////////////////////////////////// Monthly LOW LOW LOW


    if is_monthlyrange_enabled
        monthlyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monthlyl_time := get_limit_right(radistance)
            monthlyl_time


        var monthlyl_line = line.new(x1=monthlyl_time, x2=monthlyl_limit_right, y1=monthlyl_open, y2=monthlyl_open, color=MonthlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monthlyl_label = label.new(x=monthlyl_limit_right, y=monthlyl_open, text=pmltext, style=DEFAULT_LABEL_STYLE, textcolor=MonthlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monthlyl_line, monthlyl_time)
        line.set_x2(monthlyl_line, monthlyl_limit_right)
        line.set_y1(monthlyl_line, monthlyl_open)
        line.set_y2(monthlyl_line, monthlyl_open)
        label.set_x(monthlyl_label, monthlyl_limit_right)
        label.set_y(monthlyl_label, monthlyl_open)
        label.set_text(monthlyl_label, pmltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monthlyl_open, monthlyl_label, MonthlyColor)
        // the weekly open can be the daily open too (monday)
        // only the weekly will be draw, in these case we update its label


//////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////// MONTHLY HIGH HIGH HIGH



    if is_monthlyrange_enabled
        monthlyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monthlyh_time := get_limit_right(radistance)
            monthlyh_time


        var monthlyh_line = line.new(x1=monthlyh_time, x2=monthlyh_limit_right, y1=monthlyh_open, y2=monthlyh_open, color=MonthlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monthlyh_label = label.new(x=monthlyh_limit_right, y=monthlyh_open, text=pmhtext, style=DEFAULT_LABEL_STYLE, textcolor=MonthlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monthlyh_line, monthlyl_time)
        line.set_x2(monthlyh_line, monthlyh_limit_right)
        line.set_y1(monthlyh_line, monthlyh_open)
        line.set_y2(monthlyh_line, monthlyh_open)
        label.set_x(monthlyh_label, monthlyh_limit_right)
        label.set_y(monthlyh_label, monthlyh_open)
        label.set_text(monthlyh_label, pmhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monthlyh_open, monthlyh_label, MonthlyColor)
        // the weekly open can be the daily open too (monday)
        // only the weekly will be draw, in these case we update its label

//////////////////////////////////////////////////////////////////////////////// MONTHLY MID

    if is_monthly_mid
        monthlym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        monthlym_time = monthlyh_time
        monthlym_open = (monthlyl_open + monthlyh_open) / 2
        if displayStyle == 'Right Anchored'
            monthlym_time := get_limit_right(radistance)
            monthlym_time
        var monthlym_line = line.new(x1=monthlym_time, x2=monthlym_limit_right, y1=monthlym_open, y2=monthlym_open, color=MonthlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monthlym_label = label.new(x=monthlym_limit_right, y=monthlym_open, text=pmmtext, style=DEFAULT_LABEL_STYLE, textcolor=MonthlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(monthlym_line, monthlym_time)
        line.set_x2(monthlym_line, monthlym_limit_right)
        line.set_y1(monthlym_line, monthlym_open)
        line.set_y2(monthlym_line, monthlym_open)
        label.set_x(monthlym_label, monthlym_limit_right)
        label.set_y(monthlym_label, monthlym_open)
        label.set_text(monthlym_label, pmmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monthlym_open, monthlym_label, MonthlyColor)
//////////////////////////////////////////////////////////////////////////////////



    if is_monthly_enabled
        monthly_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monthly_time := get_limit_right(radistance)
            monthly_time

        var monthlyLine = line.new(x1=monthly_time, x2=monthly_limit_right, y1=monthly_open, y2=monthly_open, color=MonthlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monthlyLabel = label.new(x=monthly_limit_right, y=monthly_open, text=motext, style=DEFAULT_LABEL_STYLE, textcolor=MonthlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monthlyLine, monthly_time)
        line.set_x2(monthlyLine, monthly_limit_right)
        line.set_y1(monthlyLine, monthly_open)
        line.set_y2(monthlyLine, monthly_open)
        label.set_x(monthlyLabel, monthly_limit_right)
        label.set_y(monthlyLabel, monthly_open)
        label.set_text(monthlyLabel, motext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monthly_open, monthlyLabel, MonthlyColor)


/////////////////////////////////////////////////////////////////////////////

        // the monthly open can be the weekly open (monday 1st) and/or daily open too
        // only the monthly will be draw, in these case we update its label
        // if is_monthly_open
        //     if can_show_daily
        //         label.set_text(monthlyLabel, "DO / MO            ")
        //     if is_weekly_open
        //         if can_show_weekly
        //             label.set_text(monthlyLabel, "WO / MO            ")
        //         if can_show_daily and can_show_weekly
        //             label.set_text(monthlyLabel, "DO / WO / MO                ")

        // the start of the line is drew from the first week of the month
        // if the first day of the weekly candle (monday) is the 2nd of the month
        // we fix the start of the line position on the Prev weekly candle
        if timeframe.isweekly and dayofweek(monthly_time) != dayofweek.monday
            line.set_x1(monthlyLine, monthly_time - (weekly_time - weekly_time[1]))
```

---

## 2026-07-27T08:40Z

```

[SCREENSHOT — image not recoverable from transcript]


[SCREENSHOT — image not recoverable from transcript]

i dont want something like this. i want it to look like the second screenshot and perform and catch the most accurate trades and entries and exits. you have the spacemans key level pine. and it is with this trendline breakout with  the look back 5 in the screenshot.

 // ============================================================
// Trendline Breakout Strategy — Non-Repainting (BUG FIXED)
// Based on: github.com/neurotrader888/TrendlineBreakoutMetaLabel
// Fix: find_pivot() comparison no longer double-applies `direction`,
//      which was breaking support-pivot (sell-side) selection.
// Pine Script v5
// ============================================================
//@version=5
indicator("Trendline Breakout [Non-Repainting] [Fixed]", overlay=true, max_lines_count=500)

// ── Inputs ───────────────────────────────────────────────────
int   lookback    = input.int(72,    "Lookback Period",    minval=2, maxval=500)
bool  showLines   = input.bool(true, "Show Trendlines")
bool  showSignals = input.bool(true, "Show Buy/Sell Signals")
bool  showBg      = input.bool(true, "Highlight Signal Zone")

// ── Colours ──────────────────────────────────────────────────
color COL_SUPPORT  = input.color(color.new(color.lime,   20), "Support Line")
color COL_RESIST   = input.color(color.new(color.red,    20), "Resistance Line")
color COL_BUY      = input.color(color.new(color.aqua,    0), "Buy Signal")
color COL_SELL     = input.color(color.new(color.yellow,  0), "Sell Signal")
color COL_LONG_BG  = color.new(color.green, 92)
color COL_SHORT_BG = color.new(color.red,   92)

// ── Helper: linear regression slope & intercept ──────────────
linreg_coefs(src, len) =>
    float sumX  = 0.0
    float sumY  = 0.0
    float sumXY = 0.0
    float sumX2 = 0.0
    for j = 0 to len - 1
        float x = j
        float y = src[len - 1 - j]
        sumX  += x
        sumY  += y
        sumXY += x * y
        sumX2 += x * x
    float n = len
    float slope     = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
    float intercept = (sumY - slope * sumX) / n
    [slope, intercept]

// ── Helper: find pivot maximising distance from OLS line ──────
// FIX: diff is already sign-normalized by `direction`, so compare
// it directly against best_val — do not multiply by direction again.
find_pivot(src, len, slope, intercept, direction) =>
    int   best_j   = 0
    float best_val = -1e10
    for j = 0 to len - 1
        float x    = j
        float y    = src[len - 1 - j]
        float line = slope * x + intercept
        float diff = (y - line) * direction
        if diff > best_val
            best_val := diff
            best_j   := j
    best_j

// ── Helper: project trendline to current bar ──────────────────
project_line(src, len, pivot_j, slope) =>
    float pivot_y   = src[len - 1 - pivot_j]
    float intercept = pivot_y - slope * pivot_j
    float val = slope * len + intercept
    val

// ── Helper: optimise slope (all prices on correct side) ───────
optimize_slope(src, len, pivot_j, init_slope, is_support) =>
    float pivot_y = src[len - 1 - pivot_j]
    float best    = init_slope
    float step    = math.abs(init_slope) * 0.5 + 1e-6
    for _i = 0 to 29
        float s_up   = best + step
        float s_dn   = best - step
        bool  ok_up  = true
        bool  ok_dn  = true
        float err_up = 0.0
        float err_dn = 0.0
        for j = 0 to len - 1
            float x = j
            float y = src[len - 1 - j]
            float int_up = pivot_y - s_up * pivot_j
            float int_dn = pivot_y - s_dn * pivot_j
            float lv_up  = s_up * x + int_up
            float lv_dn  = s_dn * x + int_dn
            float d_up   = lv_up - y
            float d_dn   = lv_dn - y
            if is_support
                if d_up > 1e-5
                    ok_up := false
                if d_dn > 1e-5
                    ok_dn := false
            else
                if d_up < -1e-5
                    ok_up := false
                if d_dn < -1e-5
                    ok_dn := false
            err_up += d_up * d_up
            err_dn += d_dn * d_dn
        if ok_up and ok_dn
            best := err_up < err_dn ? s_up : s_dn
        else if ok_up
            best := s_up
        else if ok_dn
            best := s_dn
        step *= 0.5
    best

// ── Main calculation ──────────────────────────────────────────
// close[1], high[1], low[1] → window ends at PREVIOUS bar (non-repainting)
var float s_val = na
var float r_val = na
var int   sig   = 0

if bar_index >= lookback + 1
    [ols_slope, ols_intercept] = linreg_coefs(close[1], lookback)
    int upper_j = find_pivot(high[1], lookback,  ols_slope, ols_intercept,  1)
    int lower_j = find_pivot(low[1],  lookback,  ols_slope, ols_intercept, -1)
    float r_slope = optimize_slope(high[1], lookback, upper_j, ols_slope, false)
    float s_slope = optimize_slope(low[1],  lookback, lower_j, ols_slope, true)
    r_val := project_line(high[1], lookback, upper_j, r_slope)
    s_val := project_line(low[1],  lookback, lower_j, s_slope)
    if close > r_val
        sig := 1
    else if close < s_val
        sig := -1

// ── Plots ─────────────────────────────────────────────────────
plot(showLines ? r_val : na, "Resistance", color=COL_RESIST,  linewidth=1)
plot(showLines ? s_val : na, "Support",    color=COL_SUPPORT, linewidth=1)

bgcolor(showBg and sig ==  1 ? COL_LONG_BG  : na, title="Long Zone")
bgcolor(showBg and sig == -1 ? COL_SHORT_BG : na, title="Short Zone")

bool buy_signal  = sig ==  1 and sig[1] != 1
bool sell_signal = sig == -1 and sig[1] != -1

plotshape(showSignals and buy_signal,  title="BUY",  style=shape.triangleup,
          location=location.belowbar, color=COL_BUY,  size=size.small, text="BUY")
plotshape(showSignals and sell_signal, title="SELL", style=shape.triangledown,
          location=location.abovebar, color=COL_SELL, size=size.small, text="SELL")

alertcondition(buy_signal,  title="BUY Signal",  message="Trendline Breakout — BUY")
alertcondition(sell_signal, title="SELL Signal", message="Trendline Breakout — SELL")
```

---

## 2026-07-27T08:47Z

```

[SCREENSHOT — image not recoverable from transcript]

it still didnt have spaceman indicator showing also i want you to work on it. and use you 19 minds to find the edge
```

---

## 2026-07-27T08:55Z

```

[SCREENSHOT — image not recoverable from transcript]


[SCREENSHOT — image not recoverable from transcript]

this is crap. even after telling you twice it still has no key levels like the indicator i gave you. it should look like this
```

---

## 2026-07-27T09:01Z

```

[SCREENSHOT — image not recoverable from transcript]


```

---

## 2026-07-27T15:58Z

```
?
```

---

## 2026-07-27T16:12Z

```
it still hasnt shown the key levels, but also i never restricted you to any settings. i told you to find me the best and accurate signal printing. also i mentioned that you can use soo much of data that i have provided to help you find the edge
```

---

## 2026-07-27T16:13Z

```
it still hasnt shown the key levels, but also i never restricted you to any settings. i told you to find me the best and accurate signal printing. also i mentioned that you can use soo much of data that i have provided to help you find the edge
```

---

## 2026-07-27T16:18Z

```
https://github.com/shiyu-coder/Kronos.git please download and use it. and make sure you use it always
```

---

## 2026-07-28T09:37Z

```
im still wondering how are you using all the data that i fed you
```

---

## 2026-07-28T09:48Z

```

[SCREENSHOT — image not recoverable from transcript]


```

---

## 2026-07-28T09:53Z

```
please include the indicator i will give you. and add it into anything that you build and make sure it also displays the levels as it is in the indicator. //@version=5
//@sbtnc thank you for doing the base code 
//Added additional levels for convienience sake. 
indicator('Key Levels SpacemanBTC IDWM', shorttitle='SpacemanBTC Key Level V13.1', overlay=true, max_lines_count=100)
//35 works
displayStyle = input.string(defval='Standard', title='Display Style', options=['Standard', 'Right Anchored'], inline='Display')
mergebool = input.bool(defval=true, title='Merge Levels?', inline='Display')
distanceright = input.int(defval=30, title='Distance', minval=5, maxval=500, inline='Dist')
radistance = input.int(defval=250, title='Anchor Distance', minval=5, maxval=500, inline='Dist')
labelsize = input.string(defval='Medium', title='Text Size', options=['Small', 'Medium', 'Large'])
linesize = input.string(defval='Small', title='Line Width', options=['Small', 'Medium', 'Large'], inline='Line')
linestyle = input.string(defval='Solid', title='Line Style', options=['Solid', 'Dashed', 'Dotted'], inline='Line')



GlobalTextType = input.bool(defval=false, title='Global Text ShortHand', tooltip='Enable for shorthand text on all text')
var globalcoloring = input.bool(defval=false, title='Global Coloring', tooltip='Enable for all color controls via one color', inline='GC')
GlobalColor = input.color(title='', defval=color.white, inline='GC')
//var show_tails = input(defval = false, title = "Always Show", type = input.bool)


[daily_time, daily_open] = request.security(syminfo.tickerid, 'D', [time, open], lookahead=barmerge.lookahead_on)
[dailyh_time, dailyh_open] = request.security(syminfo.tickerid, 'D', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[dailyl_time, dailyl_open] = request.security(syminfo.tickerid, 'D', [time[1], low[1]], lookahead=barmerge.lookahead_on)

cdailyh_open = request.security(syminfo.tickerid, 'D', high, lookahead=barmerge.lookahead_on)
cdailyl_open = request.security(syminfo.tickerid, 'D', low, lookahead=barmerge.lookahead_on)
var monday_time = time
var monday_high = high
var monday_low = low

[weekly_time, weekly_open] = request.security(syminfo.tickerid, 'W', [time, open], lookahead=barmerge.lookahead_on)
[weeklyh_time, weeklyh_open] = request.security(syminfo.tickerid, 'W', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[weeklyl_time, weeklyl_open] = request.security(syminfo.tickerid, 'W', [time[1], low[1]], lookahead=barmerge.lookahead_on)


[monthly_time, monthly_open] = request.security(syminfo.tickerid, 'M', [time, open], lookahead=barmerge.lookahead_on)
[monthlyh_time, monthlyh_open] = request.security(syminfo.tickerid, 'M', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[monthlyl_time, monthlyl_open] = request.security(syminfo.tickerid, 'M', [time[1], low[1]], lookahead=barmerge.lookahead_on)


[quarterly_time, quarterly_open] = request.security(syminfo.tickerid, '3M', [time, open], lookahead=barmerge.lookahead_on)
[quarterlyh_time, quarterlyh_open] = request.security(syminfo.tickerid, '3M', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[quarterlyl_time, quarterlyl_open] = request.security(syminfo.tickerid, '3M', [time[1], low[1]], lookahead=barmerge.lookahead_on)


[yearly_time, yearly_open] = request.security(syminfo.tickerid, '12M', [time, open], lookahead=barmerge.lookahead_on)
[yearlyh_time, yearlyh_open] = request.security(syminfo.tickerid, '12M', [time, high], lookahead=barmerge.lookahead_on)
[yearlyl_time, yearlyl_open] = request.security(syminfo.tickerid, '12M', [time, low], lookahead=barmerge.lookahead_on)


[intra_time, intra_open] = request.security(syminfo.tickerid, '240', [time, open], lookahead=barmerge.lookahead_on)
[intrah_time, intrah_open] = request.security(syminfo.tickerid, '240', [time[1], high[1]], lookahead=barmerge.lookahead_on)
[intral_time, intral_open] = request.security(syminfo.tickerid, '240', [time[1], low[1]], lookahead=barmerge.lookahead_on)

//------------------------------ Inputs -------------------------------



var is_intra_enabled = input.bool(defval=false, title='Open', group='4H', inline='4H')
var is_intrarange_enabled = input.bool(defval=false, title='Prev H/L', group='4H', inline='4H')
var is_intram_enabled = input.bool(defval=false, title='Prev Mid', group='4H', inline='4H')
IntraTextType = input.bool(defval=false, title='ShortHand', group='4H', inline='4Hsh')

var is_daily_enabled = input.bool(defval=true, title='Open', group='Daily', inline='Daily')
var is_dailyrange_enabled = input.bool(defval=false, title='Prev H/L', group='Daily', inline='Daily')
var is_dailym_enabled = input.bool(defval=false, title='Prev Mid', group='Daily', inline='Daily')
DailyTextType = input.bool(defval=false, title='ShortHand', group='Daily', inline='Dailysh')

var is_monday_enabled = input.bool(defval=true, title='Range', group='Monday Range', inline='Monday')
var is_monday_mid = input.bool(defval=true, title='Mid', group='Monday Range', inline='Monday')
var untested_monday = false
MondayTextType = input.bool(defval=false, title='ShortHand', group='Monday Range', inline='Mondaysh')

var is_weekly_enabled = input.bool(defval=true, title='Open', group='Weekly', inline='Weekly')
var is_weeklyrange_enabled = input.bool(defval=true, title='Prev H/L', group='Weekly', inline='Weekly')
var is_weekly_mid = input.bool(defval=true, title='Prev Mid', group='Weekly', inline='Weekly')
WeeklyTextType = input.bool(defval=false, title='ShortHand', group='Weekly', inline='Weeklysh')

var is_monthly_enabled = input.bool(defval=true, title='Open', group='Monthly', inline='Monthly')
var is_monthlyrange_enabled = input.bool(defval=true, title='Prev H/L', group='Monthly', inline='Monthly')
var is_monthly_mid = input.bool(defval=true, title='Prev Mid', group='Monthly', inline='Monthly')
MonthlyTextType = input.bool(defval=false, title='ShortHand', group='Monthly', inline='Monthlysh')

var is_quarterly_enabled = input.bool(defval=true, title='Open', group='Quarterly', inline='Quarterly')
var is_quarterlyrange_enabled = input.bool(defval=false, title='Prev H/L', group='Quarterly', inline='Quarterly')
var is_quarterly_mid = input.bool(defval=true, title='Prev Mid', group='Quarterly', inline='Quarterly')
QuarterlyTextType = input.bool(defval=false, title='ShortHand', group='Quarterly', inline='Quarterlysh')

var is_yearly_enabled = input.bool(defval=true, title='Open', group='Yearly', inline='Yearly')
var is_yearlyrange_enabled = input.bool(defval=false, title='Current H/L', group='Yearly', inline='Yearly')
var is_yearly_mid = input.bool(defval=true, title='Mid', group='Yearly', inline='Yearly')
YearlyTextType = input.bool(defval=false, title='ShortHand', group='Yearly', inline='Yearlysh')

var is_londonrange_enabled = input.bool(defval=false, title='London Range', group='FX Sessions', inline='FX')
var is_usrange_enabled = input.bool(defval=false, title='New York Range', group='FX Sessions', inline='FX')
var is_asiarange_enabled = input.bool(defval=false, title='Asia Range', group='FX Sessions', inline='FX')
SessionTextType = input.bool(defval=false, title='ShortHand', group='FX Sessions', inline='FXColor')



Londont = input.session("0800-1600", "London Session")
USt = input.session("1400-2100", "New York Session")
Asiat = input.session("0000-0900", "Tokyo Session")

DailyColor = input.color(title='', defval=#08bcd4, group='Daily', inline='Dailysh')
MondayColor = input.color(title='', defval=color.white, group='Monday Range', inline='Mondaysh')
WeeklyColor = input.color(title='', defval=#fffcbc, group='Weekly', inline='Weeklysh')
MonthlyColor = input.color(title='', defval=#08d48c, group='Monthly', inline='Monthlysh')
YearlyColor = input.color(title='', defval=color.red, group='Yearly', inline='Yearlysh')
quarterlyColor = input.color(title='', defval=color.red, group='Quarterly', inline='Quarterlysh')
IntraColor = input.color(title='', defval=color.orange, group='4H', inline='4Hsh')
LondonColor = input.color(title='', defval=color.white, group='FX Sessions', inline='FXColor')
USColor = input.color(title='', defval=color.white, group='FX Sessions', inline='FXColor')
AsiaColor = input.color(title='', defval=color.white, group='FX Sessions', inline='FXColor')
var pdhtext = GlobalTextType or DailyTextType ? 'PDH' : 'Prev Day High'
var pdltext = GlobalTextType or DailyTextType ? 'PDL' : 'Prev Day Low'
var dotext = GlobalTextType or DailyTextType ? 'DO' : 'Daily Open'
var pdmtext = GlobalTextType or DailyTextType ? 'PDM' : 'Prev Day Mid'

var pwhtext = GlobalTextType or WeeklyTextType ? 'PWH' : 'Prev Week High'
var pwltext = GlobalTextType or WeeklyTextType ? 'PWL' : 'Prev Week Low'
var wotext = GlobalTextType or WeeklyTextType ? 'WO' : 'Weekly Open'
var pwmtext = GlobalTextType or WeeklyTextType ? 'PWM' : 'Prev Week Mid'

var pmhtext = GlobalTextType or MonthlyTextType ? 'PMH' : 'Prev Month High'
var pmltext = GlobalTextType or MonthlyTextType ? 'PML' : 'Prev Month Low'
var motext = GlobalTextType or MonthlyTextType ? 'MO' : 'Monthly Open'
var pmmtext = GlobalTextType or MonthlyTextType ? 'PMM' : 'Prev Month Mid'

var pqhtext = GlobalTextType or QuarterlyTextType ? 'PQH' : 'Prev Quarter High'
var pqltext = GlobalTextType or QuarterlyTextType ? 'PQL' : 'Prev Quarter Low'
var qotext = GlobalTextType or QuarterlyTextType ? 'QO' : 'Quarterly Open'
var pqmtext = GlobalTextType or QuarterlyTextType ? 'PQM' : 'Prev Quarter Mid'

var cyhtext = GlobalTextType or YearlyTextType ? 'CYH' : 'Current Year High'
var cyltext = GlobalTextType or YearlyTextType ? 'CYL' : 'Current Year Low'
var yotext = GlobalTextType or YearlyTextType ? 'YO' : 'Yearly Open'
var cymtext = GlobalTextType or YearlyTextType ? 'CYM' : 'Current Year Mid'

var pihtext = GlobalTextType or IntraTextType ? 'P-4H-H' : 'Prev 4H High'
var piltext = GlobalTextType or IntraTextType ? 'P-4H-L' : 'Prev 4H Low'
var iotext = GlobalTextType or IntraTextType ? '4H-O' : '4H Open'
var pimtext = GlobalTextType or IntraTextType ? 'P-4H-M' : 'Prev 4H Mid'

var pmonhtext = GlobalTextType or MondayTextType ? 'MDAY-H' : 'Monday High'
var pmonltext = GlobalTextType or MondayTextType ? 'MDAY-L' : 'Monday Low'
var pmonmtext = GlobalTextType or MondayTextType ? 'MDAY-M' : 'Monday Mid'

var lhtext = GlobalTextType or SessionTextType ? 'Lon-H' : 'London High'
var lltext = GlobalTextType or SessionTextType ? 'Lon-L' : 'London Low'
var lotext = GlobalTextType or SessionTextType ? 'Lon-O' : 'London Open'


var ushtext = GlobalTextType or SessionTextType ? 'NY-H' : 'New York High'
var usltext = GlobalTextType or SessionTextType ? 'NY-L' : 'New York Low'
var usotext = GlobalTextType or SessionTextType ? 'NY-O' : 'New York Open'

var asiahtext = GlobalTextType or SessionTextType ? 'AS-H' : 'Asia High'
var asialtext = GlobalTextType or SessionTextType ? 'AS-L' : 'Asia Low'
var asiaotext = GlobalTextType or SessionTextType ? 'AS-O' : 'Asia Open'

if globalcoloring == true
    DailyColor := GlobalColor
    MondayColor := GlobalColor
    WeeklyColor := GlobalColor
    MonthlyColor := GlobalColor
    YearlyColor := GlobalColor
    quarterlyColor := GlobalColor
    IntraColor := GlobalColor
    IntraColor


if weekly_time != weekly_time[1]
    untested_monday := false
    untested_monday

if is_monday_enabled == true and untested_monday == false
    untested_monday := true
    monday_time := daily_time
    monday_high := cdailyh_open
    monday_low := cdailyl_open
    monday_low


linewidthint = 1
if linesize == 'Small'
    linewidthint := 1
    linewidthint
if linesize == 'Medium'
    linewidthint := 2
    linewidthint
if linesize == 'Large'
    linewidthint := 3
    linewidthint

var DEFAULT_LINE_WIDTH = linewidthint
var DEFAULT_TAIL_WIDTH = linewidthint

fontsize = size.small

if labelsize == 'Small'
    fontsize := size.small
    fontsize

if labelsize == 'Medium'
    fontsize := size.normal
    fontsize

if labelsize == 'Large'
    fontsize := size.large
    fontsize

linestyles = line.style_solid
if linestyle == 'Dashed'
    linestyles := line.style_dashed
    linestyles

if linestyle == 'Dotted'
    linestyles := line.style_dotted
    linestyles



var DEFAULT_LABEL_SIZE = fontsize
var DEFAULT_LABEL_STYLE = label.style_none
var DEFAULT_EXTEND_RIGHT = distanceright







London = time(timeframe.period, Londont)
US = time(timeframe.period, USt)
Asia = time(timeframe.period, Asiat)

var clondonhigh = 0.0
var clondonlow = close
var londontime = time
var flondonhigh = 0.0
var flondonlow = 0.0
var flondonopen = 0.0

var onelondonfalse = false
if London
    if high > clondonhigh
        clondonhigh := high
        clondonhigh
    if low < clondonlow
        clondonlow := low
        clondonlow
    if onelondonfalse
        londontime := time
        flondonopen := open
        flondonopen
    flondonhigh := clondonhigh
    flondonlow := clondonlow
    onelondonfalse := false
    onelondonfalse
else
    if onelondonfalse == false
        flondonhigh := clondonhigh
        flondonlow := clondonlow
        flondonlow
    onelondonfalse := true

    clondonhigh := 0.0
    clondonlow := close
    clondonlow

//////////////////////////////////
var cushigh = 0.0
var cuslow = close
var ustime = time
var fushigh = 0.0
var fuslow = 0.0
var fusopen = 0.0

var oneusfalse = false
if US
    if high > cushigh
        cushigh := high
        cushigh
    if low < cuslow
        cuslow := low
        cuslow
    if oneusfalse
        ustime := time
        fusopen := open
        fusopen
    fushigh := cushigh
    fuslow := cuslow
    oneusfalse := false
    oneusfalse
else
    if oneusfalse == false
        fushigh := cushigh
        fuslow := cuslow
        fuslow
    oneusfalse := true

    cushigh := 0.0
    cuslow := close
    cuslow

//////////////////////////////////
var casiahigh = 0.0
var casialow = close
var asiatime = time
var fasiahigh = 0.0
var fasialow = 0.0
var fasiaopen = 0.0

var oneasiafalse = false
if Asia
    if high > casiahigh
        casiahigh := high
        casiahigh
    if low < casialow
        casialow := low
        casialow
    if oneasiafalse
        asiatime := time
        fasiaopen := open
        fasiaopen
    fasiahigh := casiahigh
    fasialow := casialow
    oneasiafalse := false
    oneasiafalse
else
    if oneasiafalse == false
        fasiahigh := casiahigh
        fasialow := casialow
        fasialow
    oneasiafalse := true

    casiahigh := 0.0
    casialow := close
    casialow

//------------------------------ Plotting ------------------------------
var pricearray = array.new_float(0)
var labelarray = array.new_label(0)
f_LevelMerge(pricearray, labelarray, currentprice, currentlabel, currentcolor) =>
    if array.includes(pricearray, currentprice)
        whichindex = array.indexof(pricearray, currentprice)
        labelhold = array.get(labelarray, whichindex)
        whichtext = label.get_text(labelhold)

        label.set_text(labelhold, label.get_text(currentlabel) + ' / ' + whichtext)
        label.set_text(currentlabel, '')
        label.set_textcolor(labelhold, currentcolor)
    else
        array.push(pricearray, currentprice)
        array.push(labelarray, currentlabel)


var can_show_daily = is_daily_enabled and timeframe.isintraday
var can_show_weekly = is_weekly_enabled and not timeframe.isweekly and not timeframe.ismonthly
var can_show_monthly = is_monthly_enabled and not timeframe.ismonthly

get_limit_right(bars) =>
    timenow + (time - time[1]) * bars

// the following code doesn't need to be processed on every candle
if barstate.islast
    is_weekly_open = dayofweek == dayofweek.monday
    is_monthly_open = dayofmonth == 1
    can_draw_daily = (is_weekly_enabled ? not is_weekly_open : true) and (is_monthly_enabled ? not is_monthly_open : true)
    can_draw_weekly = is_monthly_enabled ? not(is_monthly_open and is_weekly_open) : true
    can_draw_intra = is_intra_enabled
    can_draw_intrah = is_intrarange_enabled
    can_draw_intral = is_intrarange_enabled
    can_draw_intram = is_intram_enabled
    pricearray := array.new_float(0)
    labelarray := array.new_label(0)

    /////////////////////////////////

    if is_londonrange_enabled
        //label.new(bar_index,high)
        london_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)


        if displayStyle == 'Right Anchored'
            londontime := get_limit_right(radistance)
            londontime

        var londonh_line = line.new(x1=londontime, x2=london_limit_right, y1=flondonhigh, y2=flondonhigh, color=LondonColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var londonl_line = line.new(x1=londontime, x2=london_limit_right, y1=flondonlow, y2=flondonlow, color=LondonColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var londono_line = line.new(x1=londontime, x2=london_limit_right, y1=flondonopen, y2=flondonopen, color=LondonColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var londonh_label = label.new(x=london_limit_right, y=flondonhigh, text=lhtext, style=DEFAULT_LABEL_STYLE, textcolor=LondonColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var londonl_label = label.new(x=london_limit_right, y=flondonlow, text=lltext, style=DEFAULT_LABEL_STYLE, textcolor=LondonColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var londono_label = label.new(x=london_limit_right, y=flondonopen, text=lotext, style=DEFAULT_LABEL_STYLE, textcolor=LondonColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(londonh_line, londontime)
        line.set_x2(londonh_line, london_limit_right)
        line.set_y1(londonh_line, flondonhigh)
        line.set_y2(londonh_line, flondonhigh)
        line.set_x1(londonl_line, londontime)
        line.set_x2(londonl_line, london_limit_right)
        line.set_y1(londonl_line, flondonlow)
        line.set_y2(londonl_line, flondonlow)
        line.set_x1(londono_line, londontime)
        line.set_x2(londono_line, london_limit_right)
        line.set_y1(londono_line, flondonopen)
        line.set_y2(londono_line, flondonopen)
        
        label.set_x(londonh_label, london_limit_right)
        label.set_y(londonh_label, flondonhigh)
        label.set_text(londonh_label, lhtext)
        label.set_x(londonl_label, london_limit_right)
        label.set_y(londonl_label, flondonlow)
        label.set_text(londonl_label, lltext)
        label.set_x(londono_label, london_limit_right)
        label.set_y(londono_label, flondonopen)
        label.set_text(londono_label, lotext)
        
        if mergebool
            f_LevelMerge(pricearray, labelarray, flondonhigh, londonh_label, LondonColor)
            f_LevelMerge(pricearray, labelarray, flondonlow, londonl_label, LondonColor)
            f_LevelMerge(pricearray, labelarray, flondonopen, londono_label, LondonColor)
//////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////

    if is_usrange_enabled
        //label.new(bar_index,high)
        us_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)


        if displayStyle == 'Right Anchored'
            ustime := get_limit_right(radistance)
            ustime

        var ush_line = line.new(x1=ustime, x2=us_limit_right, y1=fushigh, y2=fushigh, color=USColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var usl_line = line.new(x1=ustime, x2=us_limit_right, y1=fuslow, y2=fuslow, color=USColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var uso_line = line.new(x1=ustime, x2=us_limit_right, y1=fusopen, y2=fusopen, color=USColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var ush_label = label.new(x=us_limit_right, y=fushigh, text=lhtext, style=DEFAULT_LABEL_STYLE, textcolor=USColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var usl_label = label.new(x=us_limit_right, y=fuslow, text=lltext, style=DEFAULT_LABEL_STYLE, textcolor=USColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var uso_label = label.new(x=us_limit_right, y=fusopen, text=lotext, style=DEFAULT_LABEL_STYLE, textcolor=USColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(ush_line, ustime)
        line.set_x2(ush_line, us_limit_right)
        line.set_y1(ush_line, fushigh)
        line.set_y2(ush_line, fushigh)
        
        line.set_x1(usl_line, ustime)
        line.set_x2(usl_line, us_limit_right)
        line.set_y1(usl_line, fuslow)
        line.set_y2(usl_line, fuslow)
        
        line.set_x1(uso_line, ustime)
        line.set_x2(uso_line, us_limit_right)
        line.set_y1(uso_line, fusopen)
        line.set_y2(uso_line, fusopen)
        
        
        label.set_x(ush_label, us_limit_right)
        label.set_y(ush_label, fushigh)
        label.set_text(ush_label, ushtext)
        label.set_x(usl_label, us_limit_right)
        label.set_y(usl_label, fuslow)
        label.set_text(usl_label, usltext)
        label.set_x(uso_label, us_limit_right)
        label.set_y(uso_label, fusopen)
        label.set_text(uso_label, usotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, fushigh, ush_label, USColor)
            f_LevelMerge(pricearray, labelarray, fuslow, usl_label, USColor)
            f_LevelMerge(pricearray, labelarray, fusopen, uso_label, USColor)
    /////////////////////////////////

    if is_asiarange_enabled
        //label.new(bar_index,high)
        asia_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)


        if displayStyle == 'Right Anchored'
            asiatime := get_limit_right(radistance)
            asiatime

        var asiah_line = line.new(x1=asiatime, x2=asia_limit_right, y1=fasiahigh, y2=fasiahigh, color=AsiaColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var asial_line = line.new(x1=asiatime, x2=asia_limit_right, y1=fasialow, y2=fasialow, color=AsiaColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var asiao_line = line.new(x1=asiatime, x2=asia_limit_right, y1=fasiaopen, y2=fasiaopen, color=AsiaColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var asiah_label = label.new(x=asia_limit_right, y=fasiahigh, text=asiahtext, style=DEFAULT_LABEL_STYLE, textcolor=AsiaColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var asial_label = label.new(x=asia_limit_right, y=fasialow, text=asialtext, style=DEFAULT_LABEL_STYLE, textcolor=AsiaColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        var asiao_label = label.new(x=asia_limit_right, y=fasiaopen, text=asiaotext, style=DEFAULT_LABEL_STYLE, textcolor=AsiaColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(asiah_line, asiatime)
        line.set_x2(asiah_line, asia_limit_right)
        line.set_y1(asiah_line, fasiahigh)
        line.set_y2(asiah_line, fasiahigh)
        
        line.set_x1(asial_line, asiatime)
        line.set_x2(asial_line, asia_limit_right)
        line.set_y1(asial_line, fasialow)
        line.set_y2(asial_line, fasialow)
        
        line.set_x1(asiao_line, asiatime)
        line.set_x2(asiao_line, asia_limit_right)
        line.set_y1(asiao_line, fasiaopen)
        line.set_y2(asiao_line, fasiaopen)
        
        
        label.set_x(asiah_label, asia_limit_right)
        label.set_y(asiah_label, fasiahigh)
        label.set_text(asiah_label, asiahtext)
        label.set_x(asial_label, asia_limit_right)
        label.set_y(asial_label, fasialow)
        label.set_text(asial_label, asialtext)
        label.set_x(asiao_label, asia_limit_right)
        label.set_y(asiao_label, fasiaopen)
        label.set_text(asiao_label, asiaotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, fasiahigh, asiah_label, AsiaColor)
            f_LevelMerge(pricearray, labelarray, fasialow, asial_label, AsiaColor)
            f_LevelMerge(pricearray, labelarray, fasiaopen, asiao_label, AsiaColor)
//////////////////////////////////////////////////////////////////////////////////            
            
//////////////////////////////////////////////////////////////////////////////////
    if can_draw_intra
        intra_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            intra_time := get_limit_right(radistance)
            intra_time


        var intra_line = line.new(x1=intra_time, x2=intra_limit_right, y1=intra_open, y2=intra_open, color=IntraColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var intra_label = label.new(x=intra_limit_right, y=intra_open, text=iotext, style=DEFAULT_LABEL_STYLE, textcolor=IntraColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(intra_line, intra_time)
        line.set_x2(intra_line, intra_limit_right)
        line.set_y1(intra_line, intra_open)
        line.set_y2(intra_line, intra_open)
        label.set_x(intra_label, intra_limit_right)
        label.set_y(intra_label, intra_open)
        label.set_text(intra_label, iotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, intra_open, intra_label, IntraColor)


//////////////////////////////////////////////////////////////////////////////////
//HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH HIGH
    if can_draw_intrah
        intrah_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            intrah_time := get_limit_right(radistance)
            intrah_time



        var intrah_line = line.new(x1=intrah_time, x2=intrah_limit_right, y1=intrah_open, y2=intrah_open, color=IntraColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var intrah_label = label.new(x=intrah_limit_right, y=intrah_open, text=pihtext, style=DEFAULT_LABEL_STYLE, textcolor=IntraColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(intrah_line, intrah_time)
        line.set_x2(intrah_line, intrah_limit_right)
        line.set_y1(intrah_line, intrah_open)
        line.set_y2(intrah_line, intrah_open)
        label.set_x(intrah_label, intrah_limit_right)
        label.set_y(intrah_label, intrah_open)
        label.set_text(intrah_label, pihtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, intrah_open, intrah_label, IntraColor)

//////////////////////////////////////////////////////////////////////////////////
//LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW LOW
    if can_draw_intral
        intral_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            intral_time := get_limit_right(radistance)
            intral_time



        var intral_line = line.new(x1=intral_time, x2=intral_limit_right, y1=intral_open, y2=intral_open, color=IntraColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var intral_label = label.new(x=intral_limit_right, y=intral_open, text=piltext, style=DEFAULT_LABEL_STYLE, textcolor=IntraColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(intral_line, intral_time)
        line.set_x2(intral_line, intral_limit_right)
        line.set_y1(intral_line, intral_open)
        line.set_y2(intral_line, intral_open)
        label.set_x(intral_label, intral_limit_right)
        label.set_y(intral_label, intral_open)
        label.set_text(intral_label, piltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, intral_open, intral_label, IntraColor)

///////////////////////////////////////////////////////////////////////////////   

    if can_draw_intram
        intram_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        intram_time = intrah_time
        intram_open = (intral_open + intrah_open) / 2
        if displayStyle == 'Right Anchored'
            intram_time := get_limit_right(radistance)
            intram_time

        var intram_line = line.new(x1=intram_time, x2=intram_limit_right, y1=intram_open, y2=intram_open, color=IntraColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var intram_label = label.new(x=intram_limit_right, y=intram_open, text=pimtext, style=DEFAULT_LABEL_STYLE, textcolor=IntraColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(intram_line, intram_time)
        line.set_x2(intram_line, intram_limit_right)
        line.set_y1(intram_line, intram_open)
        line.set_y2(intram_line, intram_open)
        label.set_x(intram_label, intram_limit_right)
        label.set_y(intram_label, intram_open)
        label.set_text(intram_label, pimtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, intram_open, intram_label, IntraColor)

////////////////////////////////////////// MONDAY

    if is_monday_enabled
        monday_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monday_time := get_limit_right(radistance)
            monday_time

        var monday_line = line.new(x1=monday_time, x2=monday_limit_right, y1=monday_high, y2=monday_high, color=MondayColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monday_label = label.new(x=monday_limit_right, y=monday_high, text=pmonhtext, style=DEFAULT_LABEL_STYLE, textcolor=MondayColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monday_line, monday_time)
        line.set_x2(monday_line, monday_limit_right)
        line.set_y1(monday_line, monday_high)
        line.set_y2(monday_line, monday_high)
        label.set_x(monday_label, monday_limit_right)
        label.set_y(monday_label, monday_high)
        label.set_text(monday_label, pmonhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monday_high, monday_label, MondayColor)


    if is_monday_enabled
        monday_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monday_time := get_limit_right(radistance)
            monday_time



        var monday_low_line = line.new(x1=monday_time, x2=monday_limit_right, y1=monday_low, y2=monday_low, color=MondayColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monday_low_label = label.new(x=monday_limit_right, y=monday_low, text=pmonltext, style=DEFAULT_LABEL_STYLE, textcolor=MondayColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monday_low_line, monday_time)
        line.set_x2(monday_low_line, monday_limit_right)
        line.set_y1(monday_low_line, monday_low)
        line.set_y2(monday_low_line, monday_low)
        label.set_x(monday_low_label, monday_limit_right)
        label.set_y(monday_low_label, monday_low)
        label.set_text(monday_low_label, pmonltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monday_low, monday_low_label, MondayColor)



    if is_monday_mid
        mondaym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)

        mondaym_open = (monday_high + monday_low) / 2
        if displayStyle == 'Right Anchored'
            monday_time := get_limit_right(radistance)
            monday_time

        var mondaym_line = line.new(x1=monday_time, x2=mondaym_limit_right, y1=mondaym_open, y2=mondaym_open, color=MondayColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var mondaym_label = label.new(x=mondaym_limit_right, y=mondaym_open, text=pmonmtext, style=DEFAULT_LABEL_STYLE, textcolor=MondayColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(mondaym_line, monday_time)
        line.set_x2(mondaym_line, mondaym_limit_right)
        line.set_y1(mondaym_line, mondaym_open)
        line.set_y2(mondaym_line, mondaym_open)
        label.set_x(mondaym_label, mondaym_limit_right)
        label.set_y(mondaym_label, mondaym_open)
        label.set_text(mondaym_label, pmonmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, mondaym_open, mondaym_label, MondayColor)


//////////////////////////////////////////////////////////////////////////////////
////////////////////////DAILY OPEN DAILY OPEN DAILY OPEN DAILY OPEN DAILY OPEN DAILY OPEN DAILY OPEN

    if is_daily_enabled
        daily_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            daily_time := get_limit_right(radistance)
            daily_time

        var daily_line = line.new(x1=daily_time, x2=daily_limit_right, y1=daily_open, y2=daily_open, color=DailyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var daily_label = label.new(x=daily_limit_right, y=daily_open, text=dotext, style=DEFAULT_LABEL_STYLE, textcolor=DailyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(daily_line, daily_time)
        line.set_x2(daily_line, daily_limit_right)
        line.set_y1(daily_line, daily_open)
        line.set_y2(daily_line, daily_open)
        label.set_x(daily_label, daily_limit_right)
        label.set_y(daily_label, daily_open)
        label.set_text(daily_label, dotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, daily_open, daily_label, DailyColor)

//////////////////////////////////////////////////////////////////////////////////
//////////////////DAILY HIGH DAILY HIGH DAILY HIGH DAILY HIGH DAILY HIGH DAILY HIGH DAILY HIGH 

    if is_dailyrange_enabled
        dailyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            dailyh_time := get_limit_right(radistance)
            dailyh_time
        // draw tails before lines for better visual


        var dailyh_line = line.new(x1=dailyh_time, x2=dailyh_limit_right, y1=dailyh_open, y2=dailyh_open, color=DailyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var dailyh_label = label.new(x=dailyh_limit_right, y=dailyh_open, text=pdhtext, style=DEFAULT_LABEL_STYLE, textcolor=DailyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(dailyh_line, dailyh_time)
        line.set_x2(dailyh_line, dailyh_limit_right)
        line.set_y1(dailyh_line, dailyh_open)
        line.set_y2(dailyh_line, dailyh_open)
        label.set_x(dailyh_label, dailyh_limit_right)
        label.set_y(dailyh_label, dailyh_open)
        label.set_text(dailyh_label, pdhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, dailyh_open, dailyh_label, DailyColor)


//////////////////////////////////////////////////////////////////////////////////
//////////////////DAILY LOW DAILY LOW DAILY LOW DAILY LOW DAILY LOW DAILY LOW DAILY LOW DAILY LOW 

    if is_dailyrange_enabled
        dailyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            dailyl_time := get_limit_right(radistance)
            dailyl_time


        var dailyl_line = line.new(x1=dailyl_time, x2=dailyl_limit_right, y1=dailyl_open, y2=dailyl_open, color=DailyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var dailyl_label = label.new(x=dailyl_limit_right, y=dailyl_open, text=pdltext, style=DEFAULT_LABEL_STYLE, textcolor=DailyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(dailyl_line, dailyl_time)
        line.set_x2(dailyl_line, dailyl_limit_right)
        line.set_y1(dailyl_line, dailyl_open)
        line.set_y2(dailyl_line, dailyl_open)
        label.set_x(dailyl_label, dailyl_limit_right)
        label.set_y(dailyl_label, dailyl_open)
        label.set_text(dailyl_label, pdltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, dailyl_open, dailyl_label, DailyColor)



//////////////////////////////////////////////////////////////////////////////// Daily MID

    if is_dailym_enabled
        dailym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        dailym_time = dailyh_time
        dailym_open = (dailyl_open + dailyh_open) / 2
        if displayStyle == 'Right Anchored'
            dailym_time := get_limit_right(radistance)
            dailym_time
        var dailym_line = line.new(x1=dailym_time, x2=dailym_limit_right, y1=dailym_open, y2=dailym_open, color=DailyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var dailym_label = label.new(x=dailym_limit_right, y=dailym_open, text=pdmtext, style=DEFAULT_LABEL_STYLE, textcolor=DailyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(dailym_line, dailym_time)
        line.set_x2(dailym_line, dailym_limit_right)
        line.set_y1(dailym_line, dailym_open)
        line.set_y2(dailym_line, dailym_open)
        label.set_x(dailym_label, dailym_limit_right)
        label.set_y(dailym_label, dailym_open)
        label.set_text(dailym_label, pdmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, dailym_open, dailym_label, DailyColor)


//////////////////////////////////////////////////////////////////////////////////


    if is_weekly_enabled
        weekly_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        cweekly_time = weekly_time
        if displayStyle == 'Right Anchored'
            cweekly_time := get_limit_right(radistance)
            cweekly_time


        var weekly_line = line.new(x1=cweekly_time, x2=weekly_limit_right, y1=weekly_open, y2=weekly_open, color=WeeklyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var weekly_label = label.new(x=weekly_limit_right, y=weekly_open, text=wotext, style=DEFAULT_LABEL_STYLE, textcolor=WeeklyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(weekly_line, cweekly_time)
        line.set_x2(weekly_line, weekly_limit_right)
        line.set_y1(weekly_line, weekly_open)
        line.set_y2(weekly_line, weekly_open)
        label.set_x(weekly_label, weekly_limit_right)
        label.set_y(weekly_label, weekly_open)
        label.set_text(weekly_label, wotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, weekly_open, weekly_label, WeeklyColor)
        // the weekly open can be the daily open too (monday)
        // only the weekly will be draw, in these case we update its label
    // if is_weekly_open and can_show_daily
            // label.set_text(weekly_label, "DO / WO            ")

//////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////// WEEKLY HIGH WEEKLY HIGH WEEKLY HIGH


    if is_weeklyrange_enabled
        weeklyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            weeklyh_time := get_limit_right(radistance)
            weeklyh_time


        var weeklyh_line = line.new(x1=weeklyh_time, x2=weeklyh_limit_right, y1=weeklyh_open, y2=weeklyh_open, color=WeeklyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var weeklyh_label = label.new(x=weeklyh_limit_right, y=weeklyh_open, text=pwhtext, style=DEFAULT_LABEL_STYLE, textcolor=WeeklyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(weeklyh_line, weeklyh_time)
        line.set_x2(weeklyh_line, weeklyh_limit_right)
        line.set_y1(weeklyh_line, weeklyh_open)
        line.set_y2(weeklyh_line, weeklyh_open)
        label.set_x(weeklyh_label, weeklyh_limit_right)
        label.set_y(weeklyh_label, weeklyh_open)
        label.set_text(weeklyh_label, pwhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, weeklyh_open, weeklyh_label, WeeklyColor)

//////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////// WEEKLY LOW WEEKLY LOW WEEKLY LOW


    if is_weeklyrange_enabled
        weeklyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            weeklyl_time := get_limit_right(radistance)
            weeklyl_time


        var weeklyl_line = line.new(x1=weeklyl_time, x2=weeklyl_limit_right, y1=weekly_open, y2=weekly_open, color=WeeklyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var weeklyl_label = label.new(x=weeklyl_limit_right, y=weeklyl_open, text=pwltext, style=DEFAULT_LABEL_STYLE, textcolor=WeeklyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(weeklyl_line, weeklyl_time)
        line.set_x2(weeklyl_line, weeklyl_limit_right)
        line.set_y1(weeklyl_line, weeklyl_open)
        line.set_y2(weeklyl_line, weeklyl_open)
        label.set_x(weeklyl_label, weeklyl_limit_right)
        label.set_y(weeklyl_label, weeklyl_open)
        label.set_text(weeklyl_label, pwltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, weeklyl_open, weeklyl_label, WeeklyColor)



//////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////// Weekly MID

    if is_weekly_mid
        weeklym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        weeklym_time = weeklyh_time
        weeklym_open = (weeklyl_open + weeklyh_open) / 2
        if displayStyle == 'Right Anchored'
            weeklym_time := get_limit_right(radistance)
            weeklym_time

        var weeklym_line = line.new(x1=weeklym_time, x2=weeklym_limit_right, y1=weeklym_open, y2=weeklym_open, color=WeeklyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var weeklym_label = label.new(x=weeklym_limit_right, y=weeklym_open, text=pwmtext, style=DEFAULT_LABEL_STYLE, textcolor=WeeklyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(weeklym_line, weeklym_time)
        line.set_x2(weeklym_line, weeklym_limit_right)
        line.set_y1(weeklym_line, weeklym_open)
        line.set_y2(weeklym_line, weeklym_open)
        label.set_x(weeklym_label, weeklym_limit_right)
        label.set_y(weeklym_label, weeklym_open)
        label.set_text(weeklym_label, pwmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, weeklym_open, weeklym_label, WeeklyColor)
////////////////////////////////////////////////////////////////////////////////// YEEEAARRLLYY LOW LOW LOW


    if is_yearlyrange_enabled
        yearlyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            yearlyl_time := get_limit_right(radistance)
            yearlyl_time


        var yearlyl_line = line.new(x1=yearlyl_time, x2=yearlyl_limit_right, y1=yearlyl_open, y2=yearlyl_open, color=YearlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var yearlyl_label = label.new(x=yearlyl_limit_right, y=yearlyl_open, text=cyltext, style=DEFAULT_LABEL_STYLE, textcolor=YearlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(yearlyl_line, yearlyl_time)
        line.set_x2(yearlyl_line, yearlyl_limit_right)
        line.set_y1(yearlyl_line, yearlyl_open)
        line.set_y2(yearlyl_line, yearlyl_open)
        label.set_x(yearlyl_label, yearlyl_limit_right)
        label.set_y(yearlyl_label, yearlyl_open)
        label.set_text(yearlyl_label, cyltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, yearlyl_open, yearlyl_label, YearlyColor)



//////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////// YEEEAARRLLYY HIGH HIGH HIGH


    if is_yearlyrange_enabled
        yearlyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            yearlyh_time := get_limit_right(radistance)
            yearlyh_time


        var yearlyh_line = line.new(x1=yearlyh_time, x2=yearlyh_limit_right, y1=yearlyh_open, y2=yearlyh_open, color=YearlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var yearlyh_label = label.new(x=yearlyh_limit_right, y=yearlyh_open, text=cyhtext, style=DEFAULT_LABEL_STYLE, textcolor=YearlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(yearlyh_line, yearlyh_time)
        line.set_x2(yearlyh_line, yearlyh_limit_right)
        line.set_y1(yearlyh_line, yearlyh_open)
        line.set_y2(yearlyh_line, yearlyh_open)
        label.set_x(yearlyh_label, yearlyh_limit_right)
        label.set_y(yearlyh_label, yearlyh_open)
        label.set_text(yearlyh_label, cyhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, yearlyh_open, yearlyh_label, YearlyColor)



//////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////// YEEEAARRLLYY OPEN


    if is_yearly_enabled
        yearly_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            yearly_time := get_limit_right(radistance)
            yearly_time


        var yearly_line = line.new(x1=yearly_time, x2=yearly_limit_right, y1=yearly_open, y2=yearly_open, color=YearlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)

        var yearly_label = label.new(x=yearly_limit_right, y=yearly_open, text=yotext, style=DEFAULT_LABEL_STYLE, textcolor=YearlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)



        line.set_x1(yearly_line, yearly_time)
        line.set_x2(yearly_line, yearly_limit_right)
        line.set_y1(yearly_line, yearly_open)
        line.set_y2(yearly_line, yearly_open)
        label.set_x(yearly_label, yearly_limit_right)
        label.set_y(yearly_label, yearly_open)
        label.set_text(yearly_label, yotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, yearly_open, yearly_label, YearlyColor)



//////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////// yearly MID

    if is_yearly_mid
        yearlym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        yearlym_time = yearlyh_time
        yearlym_open = (yearlyl_open + yearlyh_open) / 2
        if displayStyle == 'Right Anchored'
            yearlym_time := get_limit_right(radistance)
            yearlym_time

        var yearlym_line = line.new(x1=yearlym_time, x2=yearlym_limit_right, y1=yearlym_open, y2=yearlym_open, color=YearlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var yearlym_label = label.new(x=yearlym_limit_right, y=yearlym_open, text=cymtext, style=DEFAULT_LABEL_STYLE, textcolor=YearlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(yearlym_line, yearlym_time)
        line.set_x2(yearlym_line, yearlym_limit_right)
        line.set_y1(yearlym_line, yearlym_open)
        line.set_y2(yearlym_line, yearlym_open)
        label.set_x(yearlym_label, yearlym_limit_right)
        label.set_y(yearlym_label, yearlym_open)
        label.set_text(yearlym_label, cymtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, yearlym_open, yearlym_label, YearlyColor)


////////////////////////////////////////////////////////////////////////////////// QUATERLLYYYYY OPEN


    if is_quarterly_enabled
        quarterly_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            quarterly_time := get_limit_right(radistance)
            quarterly_time


        var quarterly_line = line.new(x1=quarterly_time, x2=quarterly_limit_right, y1=quarterly_open, y2=quarterly_open, color=quarterlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var quarterly_label = label.new(x=quarterly_limit_right, y=quarterly_open, text=qotext, style=DEFAULT_LABEL_STYLE, textcolor=quarterlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(quarterly_line, quarterly_time)
        line.set_x2(quarterly_line, quarterly_limit_right)
        line.set_y1(quarterly_line, quarterly_open)
        line.set_y2(quarterly_line, quarterly_open)
        label.set_x(quarterly_label, quarterly_limit_right)
        label.set_y(quarterly_label, quarterly_open)
        label.set_text(quarterly_label, qotext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, quarterly_open, quarterly_label, quarterlyColor)



//////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////// QUATERLLYYYYY High


    if is_quarterlyrange_enabled
        quarterlyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            quarterlyh_time := get_limit_right(radistance)
            quarterlyh_time


        var quarterlyh_line = line.new(x1=quarterlyh_time, x2=quarterlyh_limit_right, y1=quarterlyh_open, y2=quarterlyh_open, color=quarterlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var quarterlyh_label = label.new(x=quarterlyh_limit_right, y=quarterlyh_open, text=pqhtext, style=DEFAULT_LABEL_STYLE, textcolor=quarterlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(quarterlyh_line, quarterlyh_time)
        line.set_x2(quarterlyh_line, quarterlyh_limit_right)
        line.set_y1(quarterlyh_line, quarterlyh_open)
        line.set_y2(quarterlyh_line, quarterlyh_open)
        label.set_x(quarterlyh_label, quarterlyh_limit_right)
        label.set_y(quarterlyh_label, quarterlyh_open)
        label.set_text(quarterlyh_label, pqhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, quarterlyh_open, quarterlyh_label, quarterlyColor)



//////////////////////////////////////////////////////////////////////////////////


////////////////////////////////////////////////////////////////////////////////// QUATERLLYYYYY Low


    if is_quarterlyrange_enabled
        quarterlyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            quarterlyl_time := get_limit_right(radistance)
            quarterlyl_time


        var quarterlyl_line = line.new(x1=quarterlyl_time, x2=quarterlyl_limit_right, y1=quarterlyl_open, y2=quarterlyl_open, color=quarterlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var quarterlyl_label = label.new(x=quarterlyl_limit_right, y=quarterlyl_open, text=pqltext, style=DEFAULT_LABEL_STYLE, textcolor=quarterlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(quarterlyl_line, quarterlyl_time)
        line.set_x2(quarterlyl_line, quarterlyl_limit_right)
        line.set_y1(quarterlyl_line, quarterlyl_open)
        line.set_y2(quarterlyl_line, quarterlyl_open)
        label.set_x(quarterlyl_label, quarterlyl_limit_right)
        label.set_y(quarterlyl_label, quarterlyl_open)

        label.set_text(quarterlyl_label, pqltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, quarterlyl_open, quarterlyl_label, quarterlyColor)



//////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////// QUATERLLYYYYY MID

    if is_quarterly_mid
        quarterlym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        quarterlym_time = quarterlyh_time
        quarterlym_open = (quarterlyl_open + quarterlyh_open) / 2
        if displayStyle == 'Right Anchored'
            quarterlym_time := get_limit_right(radistance)
            quarterlym_time
        var quarterlym_line = line.new(x1=quarterlym_time, x2=quarterlym_limit_right, y1=quarterlym_open, y2=quarterlym_open, color=quarterlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var quarterlym_label = label.new(x=quarterlym_limit_right, y=quarterlym_open, text=pqmtext, style=DEFAULT_LABEL_STYLE, textcolor=quarterlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(quarterlym_line, quarterlym_time)
        line.set_x2(quarterlym_line, quarterlym_limit_right)
        line.set_y1(quarterlym_line, quarterlym_open)
        line.set_y2(quarterlym_line, quarterlym_open)
        label.set_x(quarterlym_label, quarterlym_limit_right)
        label.set_y(quarterlym_label, quarterlym_open)

        label.set_text(quarterlym_label, pqmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, quarterlym_open, quarterlym_label, quarterlyColor)

////////////////////////////////////////////////////////////////////////////////// Monthly LOW LOW LOW


    if is_monthlyrange_enabled
        monthlyl_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monthlyl_time := get_limit_right(radistance)
            monthlyl_time


        var monthlyl_line = line.new(x1=monthlyl_time, x2=monthlyl_limit_right, y1=monthlyl_open, y2=monthlyl_open, color=MonthlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monthlyl_label = label.new(x=monthlyl_limit_right, y=monthlyl_open, text=pmltext, style=DEFAULT_LABEL_STYLE, textcolor=MonthlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monthlyl_line, monthlyl_time)
        line.set_x2(monthlyl_line, monthlyl_limit_right)
        line.set_y1(monthlyl_line, monthlyl_open)
        line.set_y2(monthlyl_line, monthlyl_open)
        label.set_x(monthlyl_label, monthlyl_limit_right)
        label.set_y(monthlyl_label, monthlyl_open)
        label.set_text(monthlyl_label, pmltext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monthlyl_open, monthlyl_label, MonthlyColor)
        // the weekly open can be the daily open too (monday)
        // only the weekly will be draw, in these case we update its label


//////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////// MONTHLY HIGH HIGH HIGH



    if is_monthlyrange_enabled
        monthlyh_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monthlyh_time := get_limit_right(radistance)
            monthlyh_time


        var monthlyh_line = line.new(x1=monthlyh_time, x2=monthlyh_limit_right, y1=monthlyh_open, y2=monthlyh_open, color=MonthlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monthlyh_label = label.new(x=monthlyh_limit_right, y=monthlyh_open, text=pmhtext, style=DEFAULT_LABEL_STYLE, textcolor=MonthlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monthlyh_line, monthlyl_time)
        line.set_x2(monthlyh_line, monthlyh_limit_right)
        line.set_y1(monthlyh_line, monthlyh_open)
        line.set_y2(monthlyh_line, monthlyh_open)
        label.set_x(monthlyh_label, monthlyh_limit_right)
        label.set_y(monthlyh_label, monthlyh_open)
        label.set_text(monthlyh_label, pmhtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monthlyh_open, monthlyh_label, MonthlyColor)
        // the weekly open can be the daily open too (monday)
        // only the weekly will be draw, in these case we update its label

//////////////////////////////////////////////////////////////////////////////// MONTHLY MID

    if is_monthly_mid
        monthlym_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        monthlym_time = monthlyh_time
        monthlym_open = (monthlyl_open + monthlyh_open) / 2
        if displayStyle == 'Right Anchored'
            monthlym_time := get_limit_right(radistance)
            monthlym_time
        var monthlym_line = line.new(x1=monthlym_time, x2=monthlym_limit_right, y1=monthlym_open, y2=monthlym_open, color=MonthlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monthlym_label = label.new(x=monthlym_limit_right, y=monthlym_open, text=pmmtext, style=DEFAULT_LABEL_STYLE, textcolor=MonthlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)
        line.set_x1(monthlym_line, monthlym_time)
        line.set_x2(monthlym_line, monthlym_limit_right)
        line.set_y1(monthlym_line, monthlym_open)
        line.set_y2(monthlym_line, monthlym_open)
        label.set_x(monthlym_label, monthlym_limit_right)
        label.set_y(monthlym_label, monthlym_open)
        label.set_text(monthlym_label, pmmtext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monthlym_open, monthlym_label, MonthlyColor)
//////////////////////////////////////////////////////////////////////////////////



    if is_monthly_enabled
        monthly_limit_right = get_limit_right(DEFAULT_EXTEND_RIGHT)
        if displayStyle == 'Right Anchored'
            monthly_time := get_limit_right(radistance)
            monthly_time

        var monthlyLine = line.new(x1=monthly_time, x2=monthly_limit_right, y1=monthly_open, y2=monthly_open, color=MonthlyColor, width=DEFAULT_LINE_WIDTH, xloc=xloc.bar_time, style=linestyles)
        var monthlyLabel = label.new(x=monthly_limit_right, y=monthly_open, text=motext, style=DEFAULT_LABEL_STYLE, textcolor=MonthlyColor, size=DEFAULT_LABEL_SIZE, xloc=xloc.bar_time)

        line.set_x1(monthlyLine, monthly_time)
        line.set_x2(monthlyLine, monthly_limit_right)
        line.set_y1(monthlyLine, monthly_open)
        line.set_y2(monthlyLine, monthly_open)
        label.set_x(monthlyLabel, monthly_limit_right)
        label.set_y(monthlyLabel, monthly_open)
        label.set_text(monthlyLabel, motext)
        if mergebool
            f_LevelMerge(pricearray, labelarray, monthly_open, monthlyLabel, MonthlyColor)


/////////////////////////////////////////////////////////////////////////////

        // the monthly open can be the weekly open (monday 1st) and/or daily open too
        // only the monthly will be draw, in these case we update its label
        // if is_monthly_open
        //     if can_show_daily
        //         label.set_text(monthlyLabel, "DO / MO            ")
        //     if is_weekly_open
        //         if can_show_weekly
        //             label.set_text(monthlyLabel, "WO / MO            ")
        //         if can_show_daily and can_show_weekly
        //             label.set_text(monthlyLabel, "DO / WO / MO                ")

        // the start of the line is drew from the first week of the month
        // if the first day of the weekly candle (monday) is the 2nd of the month
        // we fix the start of the line position on the Prev weekly candle
        if timeframe.isweekly and dayofweek(monthly_time) != dayofweek.monday
            line.set_x1(monthlyLine, monthly_time - (weekly_time - weekly_time[1]))
```

---

## 2026-07-28T11:25Z

```
copy pastable ? also make sure you are using it as a confluence for the entry and exit from key level to key level and also use other confluences for accuracy. take time frame support also if that improves
?
```

---

## 2026-07-28T11:31Z

```
give me a copy pastable error free code
```

---

## 2026-07-28T12:15Z

```

[SCREENSHOT — image not recoverable from transcript]


```

---

## 2026-07-29T02:25Z

```

[SCREENSHOT — image not recoverable from transcript]


[SCREENSHOT — image not recoverable from transcript]

//@version=6
strategy("Key Levels Strategy — Spaceman Edition",
     overlay            = true,
     max_lines_count    = 50,
     max_labels_count   = 50,
     initial_capital    = 10000,
     currency           = currency.USD,
     default_qty_type   = strategy.cash,
     default_qty_value  = 1000,
     commission_type    = strategy.commission.cash_per_contract,
     commission_value   = 0.07,
     slippage           = 3,
     process_orders_on_close = true,
     max_bars_back      = 500)

// ═════════════════════════════════════════════════════════════
// INPUTS
// ═════════════════════════════════════════════════════════════
grpSess = "Session"
i_tz      = input.string("Etc/UTC", "Timezone", group=grpSess)
i_london  = input.session("0800-1200", "London", group=grpSess)
i_ny      = input.session("1330-1630", "NY Overlap", group=grpSess)
i_useSess = input.bool(true, "Enable Session Filter", group=grpSess)

grpLvl = "Levels to Trade"
i_do    = input.bool(true, "Daily Open", group=grpLvl)
i_pdh   = input.bool(true, "Prev Day High", group=grpLvl)
i_pdl   = input.bool(true, "Prev Day Low", group=grpLvl)
i_wo    = input.bool(true, "Weekly Open", group=grpLvl)
i_pwh   = input.bool(true, "Prev Week High", group=grpLvl)
i_pwl   = input.bool(true, "Prev Week Low", group=grpLvl)
i_mo    = input.bool(false, "Monthly Open", group=grpLvl)
i_pmh   = input.bool(false, "Prev Month High", group=grpLvl)
i_pml   = input.bool(false, "Prev Month Low", group=grpLvl)
i_4ho   = input.bool(false, "4H Open", group=grpLvl)
i_4hh   = input.bool(false, "Prev 4H High", group=grpLvl)
i_4hl   = input.bool(false, "Prev 4H Low", group=grpLvl)
i_mon   = input.bool(true, "Monday Range", group=grpLvl)
i_lon   = input.bool(false, "London Range", group=grpLvl)
i_nyl   = input.bool(false, "NY Range", group=grpLvl)

grpEntry = "Entry Logic"
i_mode    = input.string("Both", "Entry Mode", options=["Sweep+Reclaim", "Break+Retest", "Both"], group=grpEntry)
i_tolAtr  = input.float(0.25, "Level Proximity (x ATR)", step=0.05, group=grpEntry)
i_bufAtr  = input.float(0.3, "Stop Buffer (x ATR)", step=0.05, group=grpEntry)
i_minSL   = input.float(1.0, "Min SL (x ATR)", step=0.1, group=grpEntry)
i_maxSL   = input.float(2.5, "Max SL (x ATR)", step=0.1, group=grpEntry)
i_cool    = input.int(3, "Cooldown Bars", minval=1, group=grpEntry)
i_volMin  = input.float(0.7, "Min ATR vs 20-bar avg", step=0.1, group=grpEntry)

grpExit = "Exit Logic"
i_tpMode  = input.string("Key Levels", "TP Mode", options=["Key Levels", "Fixed R"], group=grpExit)
i_tp1R    = input.float(1.5, "TP1 Fixed R", step=0.1, group=grpExit)
i_tp2R    = input.float(3.0, "TP2 Fixed R", step=0.1, group=grpExit)
i_tp1Pct  = input.float(60, "% Closed at TP1", minval=10, maxval=90, group=grpExit)
i_minTpr  = input.float(1.0, "Min TP1 Distance (R)", step=0.1, group=grpExit)

grpRisk = "Risk"
i_risk    = input.float(1.0, "Risk %", step=0.25, group=grpRisk)
i_maxDay  = input.int(6, "Max Trades/Day", minval=1, group=grpRisk)
i_dayLoss = input.float(2.5, "Daily Loss Limit %", step=0.5, group=grpRisk)
i_timeStop= input.int(36, "Time Stop (bars)", minval=4, group=grpRisk)

grpDbg = "Debug"
i_debug   = input.bool(true, "Show Dashboard", group=grpDbg)

// ═════════════════════════════════════════════════════════════
// HTF LEVELS (identical to SpacemanBTC)
// ═════════════════════════════════════════════════════════════
float atr14 = ta.atr(14)
float atrAvg= ta.sma(atr14, 20)
bool  volOk = atr14 > atrAvg * i_volMin

// Daily
[dOpen, pdh, pdl] = request.security(syminfo.tickerid, "D",
     [open, high[1], low[1]], lookahead=barmerge.lookahead_on)

// Weekly
[wOpen, pwh, pwl] = request.security(syminfo.tickerid, "W",
     [open, high[1], low[1]], lookahead=barmerge.lookahead_on)

// Monthly
[mOpen, pmh, pml] = request.security(syminfo.tickerid, "M",
     [open, high[1], low[1]], lookahead=barmerge.lookahead_on)

// 4H
[h4Open, p4hh, p4hl] = request.security(syminfo.tickerid, "240",
     [open, high[1], low[1]], lookahead=barmerge.lookahead_on)

// Current day for Monday range
[cdHigh, cdLow] = request.security(syminfo.tickerid, "D",
     [high, low], lookahead=barmerge.lookahead_on)

// ═════════════════════════════════════════════════════════════
// SESSION TRACKING (London / NY)
// ═════════════════════════════════════════════════════════════
bool inLondon = not na(time(timeframe.period, i_london, i_tz))
bool inNY     = not na(time(timeframe.period, i_ny, i_tz))
bool inSession = i_useSess ? (inLondon or inNY) : true

var float lonHigh = na, var float lonLow = na, var float lonOpen = na
var float nyHigh  = na, var float nyLow  = na, var float nyOpen  = na

if inLondon
    if na(lonHigh)
        lonHigh := high, lonLow := low, lonOpen := open
    else
        lonHigh := math.max(lonHigh, high)
        lonLow  := math.min(lonLow, low)
else
    lonHigh := na, lonLow := na, lonOpen := na

if inNY
    if na(nyHigh)
        nyHigh := high, nyLow := low, nyOpen := open
    else
        nyHigh := math.max(nyHigh, high)
        nyLow  := math.min(nyLow, low)
else
    nyHigh := na, nyLow := na, nyOpen := na

// ═════════════════════════════════════════════════════════════
// MONDAY RANGE
// ═════════════════════════════════════════════════════════════
var float monHigh = na, var float monLow = na
var bool gotMonday = false

if dayofweek == dayofweek.monday and not gotMonday
    monHigh := cdHigh, monLow := cdLow, gotMonday := true
if dayofweek == dayofweek.tuesday and gotMonday
    gotMonday := false

// ═════════════════════════════════════════════════════════════
// BUILD LEVEL ARRAY (every bar)
// ═════════════════════════════════════════════════════════════
var klPrices = array.new_float(0)

f_push(bool on, float px) =>
    if on and not na(px)
        array.push(klPrices, px)

if barstate.isnew
    array.clear(klPrices)
    f_push(i_do,  dOpen)
    f_push(i_pdh, pdh)
    f_push(i_pdl, pdl)
    f_push(i_wo,  wOpen)
    f_push(i_pwh, pwh)
    f_push(i_pwl, pwl)
    f_push(i_mo,  mOpen)
    f_push(i_pmh, pmh)
    f_push(i_pml, pml)
    f_push(i_4ho, h4Open)
    f_push(i_4hh, p4hh)
    f_push(i_4hl, p4hl)
    f_push(i_mon and not na(monHigh), monHigh)
    f_push(i_mon and not na(monLow),  monLow)
    f_push(i_lon and not na(lonHigh), lonHigh)
    f_push(i_lon and not na(lonLow),  lonLow)
    f_push(i_nyl and not na(nyHigh),  nyHigh)
    f_push(i_nyl and not na(nyLow),   nyLow)

// ═════════════════════════════════════════════════════════════
// LEVEL NAVIGATION
// ═════════════════════════════════════════════════════════════
f_nearestAbove(float px) =>
    float best = na
    int sz = array.size(klPrices)
    if sz > 0
        for i = 0 to sz - 1
            float lv = array.get(klPrices, i)
            if not na(lv) and lv > px and (na(best) or lv < best)
                best := lv
    best

f_nearestBelow(float px) =>
    float best = na
    int sz = array.size(klPrices)
    if sz > 0
        for i = 0 to sz - 1
            float lv = array.get(klPrices, i)
            if not na(lv) and lv < px and (na(best) or lv > best)
                best := lv
    best

f_tpAbove(float px, float minDist, float maxDist) =>
    float t = f_nearestAbove(px)
    for k = 0 to 5
        if not na(t) and (t - px) < minDist
            t := f_nearestAbove(t)
    na(t) ? na : (t - px) > maxDist ? na : t

f_tpBelow(float px, float minDist, float maxDist) =>
    float t = f_nearestBelow(px)
    for k = 0 to 5
        if not na(t) and (px - t) < minDist
            t := f_nearestBelow(t)
    na(t) ? na : (px - t) > maxDist ? na : t

// ═════════════════════════════════════════════════════════════
// ENTRY DETECTION
// ═════════════════════════════════════════════════════════════
float tol   = atr14 * i_tolAtr
float low12 = ta.lowest(low, 12)
float high12= ta.highest(high, 12)

bool sweepLong  = false, bool sweepShort = false
bool retestLong = false, bool retestShort = false

int sz = array.size(klPrices)
if sz > 0
    for i = 0 to sz - 1
        float lv = array.get(klPrices, i)
        if not na(lv)
            // Sweep + Reclaim
            if low < lv and close > lv and close > open
                sweepLong := true
            if high > lv and close < lv and close < open
                sweepShort := true
            
            // Break + Retest
            if close > lv and low <= lv + tol and low > lv - tol and low12 < lv
                retestLong := true
            if close < lv and high >= lv - tol and high < lv + tol and high12 > lv
                retestShort := true

bool canSweep  = i_mode == "Sweep+Reclaim" or i_mode == "Both"
bool canRetest = i_mode == "Break+Retest"  or i_mode == "Both"

bool sigLong  = (canSweep and sweepLong)  or (canRetest and retestLong)
bool sigShort = (canSweep and sweepShort) or (canRetest and retestShort)

// ═════════════════════════════════════════════════════════════
// EXECUTION ENGINE
// ═════════════════════════════════════════════════════════════
var int lastSig = -9999
bool cd = bar_index - lastSig > i_cool

var int dayTrades = 0
var float dayEq0 = na
var bool halted = false
bool newDay = na(dayEq0) or dayofmonth(time) != dayofmonth(time[1])
if newDay
    dayTrades := 0
    dayEq0 := strategy.equity
    halted := false
if not na(dayEq0) and (strategy.equity - dayEq0) <= -dayEq0 * i_dayLoss / 100.0
    halted := true

bool ok = cd and not halted and dayTrades < i_maxDay and strategy.position_size == 0 and inSession and volOk

// Find the exact level we defended (closest to close)
float defLong  = na
float defShort = na

if sigLong and sz > 0
    for i = 0 to sz - 1
        float lv = array.get(klPrices, i)
        if not na(lv) and low < lv and close > lv
            if na(defLong) or math.abs(close - lv) < math.abs(close - defLong)
                defLong := lv

if sigShort and sz > 0
    for i = 0 to sz - 1
        float lv = array.get(klPrices, i)
        if not na(lv) and high > lv and close < lv
            if na(defShort) or math.abs(close - lv) < math.abs(close - defShort)
                defShort := lv

bool goLong  = ok and sigLong  and not na(defLong)
bool goShort = ok and sigShort and not na(defShort)

// ═════════════════════════════════════════════════════════════
// STOPS, TARGETS, SIZING
// ═════════════════════════════════════════════════════════════
if goLong
    float slRaw = close - defLong + atr14 * i_bufAtr
    float slDist = math.min(math.max(slRaw, atr14 * i_minSL), atr14 * i_maxSL)
    float sl = close - slDist
    
    float tp1 = na, float tp2 = na
    if i_tpMode == "Key Levels"
        tp1 := f_tpAbove(close, slDist * i_minTpr, atr14 * 8)
        tp2 := not na(tp1) ? f_tpAbove(tp1, slDist * 0.5, atr14 * 8) : na
    if na(tp1)
        tp1 := close + slDist * i_tp1R
    if na(tp2)
        tp2 := close + slDist * i_tp2R
    
    float riskAmt = strategy.equity * i_risk / 100.0
    float qty = math.max(1, math.round(riskAmt / slDist))
    float q1 = math.max(1, math.round(qty * i_tp1Pct / 100.0))
    float q2 = math.max(1, qty - q1)
    
    strategy.entry("L", strategy.long, qty=qty)
    strategy.exit("L1", "L", limit=tp1, qty=q1)
    strategy.exit("L2", "L", stop=sl, limit=tp2, qty=q2)
    lastSig := bar_index
    dayTrades += 1

if goShort
    float slRaw = defShort - close + atr14 * i_bufAtr
    float slDist = math.min(math.max(slRaw, atr14 * i_minSL), atr14 * i_maxSL)
    float sl = close + slDist
    
    float tp1 = na, float tp2 = na
    if i_tpMode == "Key Levels"
        tp1 := f_tpBelow(close, slDist * i_minTpr, atr14 * 8)
        tp2 := not na(tp1) ? f_tpBelow(tp1, slDist * 0.5, atr14 * 8) : na
    if na(tp1)
        tp1 := close - slDist * i_tp1R
    if na(tp2)
        tp2 := close - slDist * i_tp2R
    
    float riskAmt = strategy.equity * i_risk / 100.0
    float qty = math.max(1, math.round(riskAmt / slDist))
    float q1 = math.max(1, math.round(qty * i_tp1Pct / 100.0))
    float q2 = math.max(1, qty - q1)
    
    strategy.entry("S", strategy.short, qty=qty)
    strategy.exit("S1", "S", limit=tp1, qty=q1)
    strategy.exit("S2", "S", stop=sl, limit=tp2, qty=q2)
    lastSig := bar_index
    dayTrades += 1

// Time stop
if strategy.position_size != 0 and not na(lastSig) and bar_index - lastSig >= i_timeStop
    strategy.close_all(comment="Time")

// ═════════════════════════════════════════════════════════════
// VISUALS
// ═════════════════════════════════════════════════════════════
plotshape(goLong,  "Buy",  style=shape.triangleup,   location=location.belowbar, color=color.new(#00C853, 0), size=size.small)
plotshape(goShort, "Sell", style=shape.triangledown, location=location.abovebar, color=color.new(#D50000, 0), size=size.small)
bgcolor(inSession ? color.new(color.blue, 95) : na, title="Session")

// ═════════════════════════════════════════════════════════════
// DASHBOARD
// ═════════════════════════════════════════════════════════════
float nextUp = f_tpAbove(close, atr14 * i_minSL * i_minTpr, atr14 * 8)
float nextDn = f_tpBelow(close, atr14 * i_minSL * i_minTpr, atr14 * 8)

if i_debug
    var table vt = table.new(position.top_right, 3, 14, bgcolor=color.new(color.black, 20), border_width=1, border_color=color.gray)
    if barstate.islast
        table.cell(vt, 0, 0, "KL STRATEGY", text_color=color.orange, text_size=size.small)
        table.cell(vt, 1, 0, "v1.0", text_color=color.orange, text_size=size.small)
        table.cell(vt, 2, 0, i_mode, text_color=color.white, text_size=size.tiny)
        
        table.cell(vt, 0, 1, "Session", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 1, inSession ? "ON" : "OFF", text_color=inSession ? color.green : color.gray, text_size=size.tiny)
        
        table.cell(vt, 0, 2, "Levels", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 2, str.tostring(sz), text_color=color.white, text_size=size.tiny)
        
        table.cell(vt, 0, 3, "Vol OK", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 3, volOk ? "YES" : "NO", text_color=volOk ? color.green : color.red, text_size=size.tiny)
        
        table.cell(vt, 0, 4, "Sweep L/S", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 4, str.tostring(sweepLong) + "/" + str.tostring(sweepShort), text_color=sweepLong or sweepShort ? color.yellow : color.gray, text_size=size.tiny)
        
        table.cell(vt, 0, 5, "Retest L/S", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 5, str.tostring(retestLong) + "/" + str.tostring(retestShort), text_color=retestLong or retestShort ? color.yellow : color.gray, text_size=size.tiny)
        
        table.cell(vt, 0, 6, "Cooldown", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 6, cd ? "READY" : str.tostring(bar_index - lastSig), text_color=cd ? color.green : color.red, text_size=size.tiny)
        
        table.cell(vt, 0, 7, "Daily", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 7, str.tostring(dayTrades) + "/" + str.tostring(i_maxDay), text_color=dayTrades >= i_maxDay ? color.red : color.white, text_size=size.tiny)
        
        table.cell(vt, 0, 8, "Defend L", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 8, na(defLong) ? "-" : str.tostring(defLong, format.mintick), text_color=color.lime, text_size=size.tiny)
        
        table.cell(vt, 0, 9, "Defend S", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 9, na(defShort) ? "-" : str.tostring(defShort, format.mintick), text_color=color.red, text_size=size.tiny)
        
        table.cell(vt, 0, 10, "Next Up", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 10, na(nextUp) ? "-" : str.tostring(nextUp, format.mintick), text_color=color.silver, text_size=size.tiny)
        
        table.cell(vt, 0, 11, "Next Dn", text_color=color.gray, text_size=size.tiny)
        table.cell(vt, 1, 11, na(nextDn) ? "-" : str.tostring(nextDn, format.mintick), text_color=color.silver, text_size=size.tiny)
        
        // Results
        int nT = strategy.closedtrades
        int wT = 0
        float gw = 0.0, gl = 0.0
        if nT > 0
            for i = 0 to nT - 1
                float p = strategy.closedtrades.profit(i)
                wT += p > 0 ? 1 : 0
                gw += p > 0 ? p : 0.0
                gl += p < 0 ? -p : 0.0
        float wr = nT > 0 ? wT * 100.0 / nT : na
        float pf = gl > 0 ? gw / gl : na
        
        table.cell(vt, 2, 1, "Trades", text_color=color.silver, text_size=size.tiny)
        table.cell(vt, 2, 2, str.tostring(nT), text_color=color.white, text_size=size.tiny)
        table.cell(vt, 2, 3, "WR", text_color=color.silver, text_size=size.tiny)
        table.cell(vt, 2, 4, na(wr) ? "-" : str.tostring(wr, "#.#") + "%", text_color=color.white, text_size=size.tiny)
        table.cell(vt, 2, 5, "PF", text_color=color.silver, text_size=size.tiny)
        table.cell(vt, 2, 6, na(pf) ? "-" : str.tostring(pf, "#.##"), text_color=na(pf) ? color.gray : pf >= 1.5 ? color.lime : pf >= 1.0 ? color.yellow : color.red, text_size=size.tiny)

alertcondition(goLong,  "KL Buy",  "Key Levels BUY {{ticker}}")
alertcondition(goShort, "KL Sell", "Key Levels SELL {{ticker}}")
```

---

## 2026-07-29T02:34Z

```
its all getting too messy now, as after giving you the worlds best skills and data. from past 4 months you havent created a single profitable startegy.
```

---

## 2026-07-29T02:36Z

```
you have all the sessions data right ? from eveery chat we had ?
```

---

## 2026-07-29T02:39Z

```
i want you to go through our each session and find out the data you'd need as i have many important details in each session
```

---

