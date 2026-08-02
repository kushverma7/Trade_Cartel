# AICartel Trading System — Complete Trade Guide
**Version 2.0 | Indicators: NQ Master CLC System + Crypto Scalp Model v1**

---

## INDICATOR 1 — NQ Master CLC System

### What It Is
Order flow indicator for NQ/ES futures. Combines 3 elite trader frameworks into one scoring system. Does NOT auto-trade — it reads market structure and tells you when conditions align.

**Sources:**
- Fabio Valentini — Auction Market Theory, VWAP SD bands, CVD, aggression bubbles
- Marco Acetony — Qualifying sweep rule, Order Block traps, retail liquidity hunts
- Carmine Rosato — CLC framework (Context + Location + Confirmation), Zero Prints, 3-Loss Rule

---

### Chart Setup
| Setting | Value |
|---------|-------|
| Instrument | NQ1!, ES1!, MNQ1!, MES1! |
| Timeframe | 1m or 5m (entry) — check 15m for context |
| Session | NY 09:30–11:30 EST only |
| Supertrend | Period 14, Mult 3.0 |
| VWAP | Daily reset, 1SD / 2SD / 3SD bands |

---

### The CLC Framework — 3 Pillars (Each = 1 Point, Max 3)

#### PILLAR 1 — CONTEXT (Macro Direction)
**Question: Is the macro trend aligned with my trade?**

- Supertrend direction (14/3.0) = bull or bear
- Bull context = ST green (price above ST line)
- Bear context = ST red (price below ST line)
- **A-grade requires context match. B-grade can skip it.**
- Check 15m chart for context. Enter on 1m–5m.

#### PILLAR 2 — LOCATION (Where Are We?)
**Question: Is price at a meaningful structural level?**

Location = TRUE if ANY of:
- Liquidity sweep of recent 20-bar high/low (Marco rule: sweep REQUIRED)
- Price at VWAP Lower 1SD (support in bull trend)
- Price at VWAP Lower 2SD (extended — high-value long zone)
- Price at VWAP Upper 1SD (resistance in bear trend)
- Price at VWAP Upper 2SD (extended — high-value short zone)

**Zero Print zones** (Carmine): Purple boxes on chart = volume voids. Price always returns to fill them. These are automatic location points.

#### PILLAR 3 — CONFIRMATION (Order Flow Agrees)
**Question: Are the buyers/sellers actually showing up?**

Confirmation = TRUE if:
- CVD rising (delta buying pressure building) AND
- Aggression bubble firing (vol spike + strong body candle) OR sweep just occurred

**Delta Outlier** = diamond marker = single bar with 2.5x normal delta = Carmine's A+ entry. Highest confidence confirmation possible.

---

### Signal Grades

| Grade | Points | What It Means | Action |
|-------|--------|---------------|--------|
| A-LONG / A-SHORT | 3/3 | All 3 pillars aligned | Full size entry |
| B-LONG / B-SHORT | 2/3 | Location + Confirm met, no macro context | Half size, tight stop |
| No signal | 0–1 | Conditions not met | Stay flat |

---

### Entry Rules

**A-Grade Long (3/3):**
1. Supertrend = BULL (green, price above)
2. Price swept recent low OR at VWAP 1SD/2SD support
3. CVD rising + aggression bubble (or delta outlier diamond)
4. In NY session window (blue background)
5. NOT flagged as 3-loss level

**A-Grade Short (3/3):**
1. Supertrend = BEAR (red, price below)
2. Price swept recent high OR at VWAP 1SD/2SD resistance
3. CVD falling + aggression bubble (or delta outlier diamond)
4. In NY session window
5. NOT flagged as 3-loss level

**Entry timing:** Enter on close of the signal bar OR limit at the swept level.

---

### Stop Loss Placement
- Long: Below the swept low − 0.1× ATR buffer
- Short: Above the swept high + 0.1× ATR buffer
- If no sweep: Below/above the signal bar low/high + 0.1× ATR

---

### Take Profit Rules

| Target | Level | Action |
|--------|-------|--------|
| TP1 | VWAP midline (if entered at 1SD) | Close 40%, move SL to BE |
| TP2 | VWAP 2SD band | Close 40%, trail remaining |
| TP3 | VWAP 3SD (extreme zone) | Close all — Fabio extreme exit rule |
| POC rule | 70% chance price revisits POC | Use as runner target |

**CVD divergence = move to BE immediately.** If price up but CVD falling → long to BE. If price down but CVD rising → short to BE. Non-negotiable.

---

### Exit Rules

| Signal | Action |
|--------|--------|
| CVD- label (bear divergence) | Move long stop to breakeven NOW |
| CVD+ label (bull divergence) | Move short stop to breakeven NOW |
| 2SD band reached | Take partial profit (TP2) |
| 3SD band reached | Exit everything (extreme) |
| 3-LOSS ABANDON label | Do not enter at this level — 3 failures already |

---

### The 3-Loss Rule (Carmine)
If price has rejected from the same level 3 times → **abandon that level for the day.**
The indicator tracks this automatically. Orange "3-LOSS ABANDON" label appears.
When it fires: skip the signal, move to next level.

---

### Zero Prints (Carmine)
Purple box = 3+ consecutive bars with volume below 15% of average.
These are volume voids. Price **always** returns to fill them.
Use as:
- Hidden support/resistance levels
- TP targets (if a zero print is above/below entry)
- Location confirmation (if price bounced off zero print zone)

---

### What to Ignore
- Signals outside blue session background (not NY session)
- Any signal when 3-LOSS ABANDON is showing for that direction
- B-grade signals when macro context is strongly against you (e.g. ST strongly bear, taking B-grade long)
- Signals at VWAP 3SD — that's an EXIT zone, not entry zone

---

### Dashboard — CLC Table (Top Right)
| Row | What It Shows |
|-----|---------------|
| CONTEXT | BULL / BEAR / NEUTRAL — Supertrend direction |
| LOCATION | BUY ZONE / SELL ZONE / NO ZONE |
| CONFIRM | BULL CONF / BEAR CONF / WAITING |
| SIGNAL | A-LONG 3/3 / B-LONG 2/3 / NO SIGNAL |
| VWAP ZONE | Which SD band price is in |
| CVD | BULL / BEAR / BEAR DIV-BE / BULL DIV-BE |
| 3-LOSS | CLEAN / LONG 1/3 / ABANDON LONG |
| SESSION | NY ACTIVE / CLOSED |
| ATR(14) | Current ATR value for sizing |

---

### Confluences That Make A Signals High Probability
Stack as many as possible:
1. A-grade CLC (3/3 pillars)
2. Delta outlier diamond fires on same bar
3. Price at VWAP 2SD (extended, mean-reversion setup)
4. Zero print zone just below/above entry
5. Sweep of a round number or previous day high/low
6. CVD direction matches trade (no divergence)
7. Aggression bubble same direction as trade

**5+ confluences = size up. 3–4 = normal size. 2 or less = skip.**

---

---

## INDICATOR 2 — Crypto Scalp Model v1 (CSM·v1)

### What It Is
Strategy (has built-in backtest) for crypto. Implements TIME → PRICE → CONFIRMATION framework. Verified 75% WR on BTCUSD 5m, Oct 2025–Jan 2026 sample.

**Core idea:** Every NY/London session open has 3 phases. Accumulation → Manipulation (fake-out sweep) → Distribution (real move). Enter only in phase 3, only after phase 2 sweep confirmed.

---

### Chart Setup
| Setting | Value |
|---------|-------|
| Instrument | BTCUSDT, ETHUSDT, any major crypto perp |
| Timeframe | 5m primary |
| Timezone | Australia/Melbourne (UTC+10) — change if not in Melbourne |
| NY Session | 21:30–01:30 Melbourne time |
| London Session | 18:00–20:00 Melbourne time |

**If not in Melbourne:** Change timezone to your city in settings → ① Session → Timezone.

---

### The Q1/Q2/Q3 Cycle — Core Framework

Every session has exactly 3 phases of 30 minutes each:

#### Q1 — Accumulation (Blue background, 0–30 min)
- Price consolidates, building a range
- Orange dashed lines lock in the Q1 high and low at end of Q1
- **Do nothing in Q1. Just watch and mark the range.**
- Wait for Q1 to finish before expecting any setup

#### Q2 — Manipulation (Purple background, 30–60 min)
- Smart money sweeps Q1 range to trap retail
- Bull sweep: wick BELOW Q1 low by ≥0.25× ATR, then close BACK ABOVE Q1 low — same bar
- Bear sweep: wick ABOVE Q1 high by ≥0.25× ATR, then close BACK BELOW Q1 high — same bar
- Teal circle = bull sweep confirmed. Red circle = bear sweep confirmed.
- **Sweep must happen in Q2. If no sweep in Q2, no trade that session.**
- A sweep that happens in Q3 is too late — the manipulation window has closed.

#### Q3 — Distribution/Entry (Green background, 60–90 min)
- Real directional move begins
- Entry window opens ONLY after Q1 sweep confirmed
- Need displacement + MSS to actually enter
- **This is the only phase where signals fire.**

---

### Entry Conditions (ALL must be true)

**Long entry:**
1. In Q3 phase (green background)
2. Q1 low was swept in Q2 (teal circle appeared)
3. Displacement candle: bull candle with body ≥ 0.6× ATR(14)
4. Market Structure Shift (MSS): that displacement candle breaks above recent 5-bar swing high
5. VWAP bias: close above VWAP (yellow line)
6. Midnight Open Bias: close BELOW 00:00 EST open price (longs prefer below midnight open)
7. Daily loss limit not hit (-2R rule)

**Short entry:**
1. In Q3 phase (green background)
2. Q1 high was swept in Q2 (red circle appeared)
3. Displacement candle: bear candle with body ≥ 0.6× ATR(14)
4. MSS: displacement candle breaks below recent 5-bar swing low
5. VWAP bias: close below VWAP
6. Midnight Open Bias: close ABOVE midnight open (shorts prefer above)
7. Daily loss limit not hit

---

### Stop Loss
- Long: Swept Q1 low level − 0.1× ATR buffer
- Short: Swept Q1 high level + 0.1× ATR buffer
- SL is shown as red line on chart while in trade

---

### Take Profit
| Target | Level | Action |
|--------|-------|--------|
| TP1 | 1:1 Risk (1R) | Close 60% of position, move SL to breakeven |
| Runner | Remaining 40% | Hold — let it run, SL at BE |
| Hard max | VWAP 2SD band | Exit remaining if reached |

**After TP1 hit:** Position is risk-free. SL is at breakeven. Let the runner work.

---

### The Midnight Open Bias
- 00:00 EST = new "day" anchor for crypto
- If price is BELOW midnight open → bias is long (shorts have been running)
- If price is ABOVE midnight open → bias is short (longs have been running)
- This filter removes counter-trend entries into already-extended moves
- **Turn it OFF** if you want more signals (less accurate)

---

### The -2R Daily Stop Rule
- If you hit 2 full losses in one session (−2R cumulative) → **no more trades that day**
- Red background = session stopped
- Dashboard shows "STOPPED" in red
- Iron rule — do not override

---

### SMT Divergence (Optional — Off by Default)
SMT = Smart Money Trap divergence.
- BTCUSD sweeps Q1 low but ETHUSD does NOT sweep its Q1 low
- This divergence = only BTC was manipulated = high-confidence long on BTC
- Enable in settings → ⑦ SMT → Enable SMT Filter → ON
- Comparison symbol default: BINANCE:ETHUSDT

**When enabled:** requires BOTH BTC sweep AND ETH NOT sweeping. Reduces signals but increases quality.

---

### Dashboard — CSM Table (Top Right)
| Row | What It Shows |
|-----|---------------|
| Phase | Q1 ACCUM / Q2 MANIP / Q3 ENTRY / -- |
| Q1 Sweep | BULL ✓ / BEAR ✓ / WAIT |
| VWAP Bias | LONG / SHORT |
| Midnight | BELOW (L) / ABOVE (S) / OFF |
| Daily PnL | Running R total for session |
| Session | ACTIVE / STOPPED |

---

### VWAP Levels — What They Mean
| Level | Meaning | Action |
|-------|---------|--------|
| VWAP (yellow) | Fair value | Bias long above, short below |
| 1SD+ (green thin) | Trend extension | Partial profit zone |
| 1SD- (green thin) | Trend support | Long entry zone |
| 2SD+ (green dots) | Overbought | TP2 zone for longs |
| 2SD- (green dots) | Oversold | TP2 zone for shorts |

---

### Confluences That Make CSM Signals High Probability
1. Sweep exactly at a previous session high/low (clean liquidity pool)
2. Sweep at a round number (e.g. BTC $63,000, $65,000)
3. SMT divergence (BTC sweeps, ETH doesn't)
4. Entry candle = inside Q3 first 3 bars (earlier = better)
5. VWAP 1SD support/resistance aligns with entry
6. Displacement candle body ≥ 0.8× ATR (stronger = better)
7. Midnight open bias strongly aligned (far below or above)

**3+ extra confluences = size up. Minimum 0 extra needed (base signal is enough).**

---

### Why Signals Don't Fire Every Session
Intentional. The system only fires on MANIPULATION sessions.
- Clean trending days (no sweep) = no signal = correct behavior
- Ranging days without a Q1 range breach = no signal = correct behavior
- Expect 2–5 valid setups per week, not per day
- Quality over quantity — each signal should be close to textbook

**What a perfect session looks like:**
1. Q1 forms a tidy 30-min consolidation range
2. Q2 first bar wicks sharply below Q1 low, closes above it (sweep confirmed)
3. Q3 first bar = strong bull displacement, breaks Q2 high (MSS)
4. Price is below midnight open and above VWAP
5. Entry → TP1 hit within 15–30 min → runner holds into session close

---

## How To Use Both Together

| Scenario | CSM | NQ CLC |
|----------|-----|--------|
| Trading crypto 5m | Primary system | Not applicable |
| Trading ES/NQ futures | Not applicable (futures, not crypto session structure) | Primary system |
| Reading market bias | Q1/Q2 sweep direction | Context pillar (ST direction) |
| Confirmation needed | Displacement + MSS in Q3 | CVD + aggression in session |
| Exit signals | VWAP 2SD + -2R rule | CVD divergence + 3SD extreme |
| Risk management | -2R daily hard stop | 3-loss rule per level |

**Never use CSM on ES/NQ.** The Q1/Q2/Q3 cycle is designed for crypto manipulation patterns.
**Never use NQ CLC for crypto.** Session times and delta mechanics differ.

---

## Risk Management — Both Systems

| Rule | Value |
|------|-------|
| Max daily loss | -2R (2 full risk units) |
| Position size | 1–2% account risk per trade |
| A-grade size | Normal size (1%) |
| B-grade size | Half size (0.5%) |
| After TP1 hit | Move SL to BE — trade is risk-free |
| 3 losses same level | Abandon level (NQ CLC rule) |
| After -2R hit | No more trades, close platform |

---

## Quick Reference Card

### CSM v1 — Entry Checklist
- [ ] Q1 formed a clear range (blue background done)
- [ ] Q2 sweep confirmed (teal/red circle)
- [ ] In Q3 (green background)
- [ ] Displacement candle fired (strong body)
- [ ] MSS break of recent swing
- [ ] VWAP bias aligned
- [ ] Midnight open bias aligned
- [ ] Session not stopped (-2R)

### NQ CLC — Entry Checklist
- [ ] In NY session (blue background)
- [ ] CLC table shows A-LONG or B-LONG
- [ ] CONTEXT = BULL (for longs)
- [ ] LOCATION = BUY ZONE
- [ ] CONFIRM = BULL CONF
- [ ] CVD = BULL (not diverging)
- [ ] 3-LOSS = CLEAN (not ABANDON)
- [ ] No active trade open

---

*Generated by AICartel Intelligence OS | Based on: Fabio Valentini, Marco Acetony, Carmine Rosato verified frameworks*
