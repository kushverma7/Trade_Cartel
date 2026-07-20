# Quarterly Theory (Trader Daye / ICT lineage) — extracted 2026-07-19
# Source: compiled PDF, user-supplied. INDEPENDENT SOURCE #4.
# EDGE STATUS: pure theory, ZERO stats or track record in source.
# ICT-derived material is partly unfalsifiable; only the testable
# time/price skeleton is implemented. Observation + confluence only.

## Codeable skeleton
1. Fractal time quarters. Daily (ET): Q1 Asia 18-00, Q2 London 00-06,
   Q3 NY AM 06-12, Q4 NY PM 12-18. Sessions subdivide into 90-min
   quarters; those into 22.5-min quarters.
2. True Opens (reference prices): Daily = 00:00 ET open, Weekly =
   Tuesday 00:00 open, NY AM = 07:30 open. Above/below = premium/
   discount frame; reversals cluster near them (claim).
3. AMDX phase template per cycle: Accumulate -> Manipulate (Judas
   swing = deliberate false move) -> Distribute -> Reverse/Continue.
   Alternate form XAMD (shifted one quarter).
4. Session quarter behavior: Q1 range/liquidity build, Q2 expansion,
   Q3 continuation/pullback, Q4 reversal/profit-taking. Asia = trap
   setting, London = strongest expansion, NY = continue/reverse.
5. SMT divergence: correlated asset fails to confirm a sweep ->
   sweep was manipulation. Levels: standard (daily+), session (SSMT),
   90-minute (90SSMT). For gold: silver or DXY(inverse) reference.
6. Strategy chain: identify quarter/phase -> SMT -> PD-array tap
   (OB/FVG in premium/discount) -> CONFIRMATION (structure shift or
   liquidity grab) -> stop beyond the grab, laddered TPs (1:3/1:6+).
7. Risk notes from source: 1-2%/trade, high-liquidity sessions only,
   not every quarter offers a trade.

## Register impact
- SWEEP-REVERSAL FAMILY: first independent SUPPORT (Judas swing IS
  sweep-then-reverse). Tally: 2 support (PBD, Quarterly) vs 1 against
  (Valentini).
- CONFIRMATION FAMILY: 5th independent source (even ICT school
  requires structure shift after the tap).
- B1 CORROBORATION: Q2 expansion windows = London open + NY open =
  exactly our backtested gold session windows, via different reasoning.

## Implementation
indicators/quarterly_theory_engine.pine — daily quarter shading, true
opens, prev-day liquidity lines, real SMT vs reference symbol (silver
default, DXY-inverse toggle), JUDAS sweep+reclaim+SMT signals, alerts.
NOTE: SMT needs the reference symbol available on user's data plan.

---

## v2 additions — second QT compilation (2026-07-19)
Source: community doc (mostly chart images; text layer extracted;
image examples not recoverable). Same school, richer mechanics.

- Q-ALTERNATION RULE [H15, highly testable]: consolidating Q ->
  expect expansion next Q; expanding Q -> expect consolidation next.
  Session form: Asia consolidates -> trade London; Asia expands ->
  skip London, trade NY. [engine: forecast label at each Q open]
- Every Q open is a True Open (not only Q2).
- TF pairing model: 1m entry <- 15m context, 5m <- 1h, 15m <- 4h.
- SSMT (sequential SMT): SMT across/just after a Q boundary =
  higher probability than generic SMT ("time factor engaged").
  Mapping: Monthly SSMT->4h PSP, Weekly->1h, Daily->15m,
  Session/90m->5m, Micro->1m. [engine: SSMT vs SMT label grades]
- PSP (Precision Swing Point): the swing candle formed at the SSMT
  (correlated triad diverges). ENTRY = CLOSE of that candle ->
  confirmation-before-entry family, 5th source holds here too.

---

## v3 — PRIMARY SOURCE (Trader Daye's own intro video, 2026-07-19)
Primary outranks compilations. Corrections + precision:

- TRUE WEEKLY OPEN = MONDAY 18:00 ET (compilation #1 said "Tuesday
  midnight" — garbled; Mon 18:00 IS the start of the Tuesday trading
  day in the 18:00-rollover convention). ENGINE CORRECTED.
- Session true opens = Q2 of each session's 90-min cycle:
  Asia 19:30, London 01:30, NY 07:30, PM 13:30 ET. All now plotted.
- True year open = first Monday of April; true month open = second
  Monday. Monthly counting uses first FULL week; partial = distortion.
- Trading rule (crisp): bullish in a cycle -> buy BELOW its true
  open; bearish -> sell ABOVE it. Key levels rest beyond true opens.
- Q1 is the barometer (his words): Q1 overextended -> Q2 consolidates;
  Q1 tight -> Q2 expands. Confirms H15 is faithful to the original.
- PD-array TF pairing (full map): 1m->15m, 5m->1H, 15m->4H, 1H->D,
  4H->W.
- Lineage note: he states openly it is reverse-engineered ICT. Still
  zero statistics offered in the primary source either.

---

## v4 — second full video, same primary lineage (2026-07-20)
Fuller restatement with two genuinely new, codeable pieces:

- **Exact 90-minute sub-quarters for all four sessions (ET)**, not just
  the daily quarters:
  - Asia:   6:00-7:30p / 7:30-9:00p / 9:00-10:30p / 10:30p-12:00a
  - London: 12:00-1:30a / 1:30-3:00a / 3:00-4:30a / 4:30-6:00a
  - NY AM:  6:00-7:30a / 7:30-9:00a / 9:00-10:30a / 10:30a-12:00p
  - PM:     12:00-1:30p / 1:30-3:00p / 3:00-4:30p / 4:30-6:00p
  Each session's Q2 (2nd 90-min block) = that session's true open,
  confirming what was already coded (19:30/01:30/07:30/13:30).
- **AMDX vs XAMD, exact quarter-to-phase mapping** (previously only
  described as "shifted one quarter" — now precise):
  - AMDX: Q1=Accumulate (tight range) -> Q2=Manipulate (Judas swing) ->
    Q3=Distribute (trend already set, easiest phase to trade) ->
    Q4=X (continuation OR reversal, resolved at HTF PD arrays/key levels).
  - XAMD: Q1=X (continuation/reversal of the PRIOR cycle) -> Q2=Accumulate
    (uses that quarter's true open as the reference even though
    accumulation, not manipulation, happens here — true opens are
    static regardless of phase) -> Q3=Manipulate (Judas swing, referenced
    to Q2's true open) -> Q4=Distribute.
- Weekly quarters explicit: Mon=Q1, Tue=Q2, Wed=Q3, Thu=Q4 — **Friday is
  excluded**, stated to have "its own specific function" (source doesn't
  elaborate; matches Steve/MMM4x's independent friday-is-different rule
  from voice #8 — different lineage, same observation).
- Liquidity/PD-array induction restated as one line: liquidity is
  induced when price breaches old highs/lows while trading into a
  higher-timeframe key level — this is the SMT/JUDAS mechanism already
  coded, now stated as the general case.
- Still zero statistics. Same primary source lineage as v3 (reverse-
  engineered ICT, openly stated).

---

## v5 — "857483891QuarterlyTheory" PDF, re-supplied with a working text
layer (2026-07-20). This is the SAME document referenced earlier as
"compilation #2, mostly images" (the first upload's text layer was
mostly unrecoverable) -- this copy has extractable text and CONFIRMS
the v2 additions were captured correctly: same TF pairing model (1m->
15m, 5m->1h, 15m->4h), same PSP (Precision Swing Point) definition,
same SSMT concept, same "every Q open is a True Open" claim, same
Daye attribution. No contradictions found against what's already coded.

Two genuinely new details this cleaner copy adds:
- **Asset TRIAD requirement**: "a PSP can only be formed when this
  formation does not correlate with an asset triad" -- meaning a
  full-grade PSP/SMT check should fail to confirm against TWO
  correlated references, not just one. Previous engine only checked a
  single reference (silver for gold). Added as an OPTIONAL 2nd
  reference (default DXY, inverse) that must ALSO fail to confirm the
  sweep before a triad-confirmed SMT arms -- default OFF to preserve
  existing single-reference behavior; toggle on to test the stricter
  version.
- **iFVG mention**: "very similar to how to properly use iFVG" (inverse
  Fair Value Gap) as a comparison for PSP entry timing. Not detailed
  further in source -- NOT implemented, flagged and preserved per
  standing rule rather than guessed at. If a future source explains
  iFVG mechanics clearly, cross-reference back here.

## v5 ENGINE UPDATE
quarterly_theory_engine.pine: added `useTriad` toggle + `refSym2`/
`refInv2` inputs. When enabled, BOTH references must fail to confirm
a sweep before SMT/SSMT/JUDAS signals arm (stricter, fewer signals,
matches the source's literal "triad" requirement). Off by default.

---

## v6 — "the little time table" image, recovered from the primary
compiled PDF (2026-07-20 re-review). This project's own text extraction
had already pulled everything readable from this document's text layer;
what it silently dropped was a single embedded table graphic ("A little
time table") that only exists as an image, one page before the
"Compiled by @ransh28.06" credit page. Recovered by rendering the PDF
page directly instead of relying on the text layer.

The table gives the Year/Month/Week/Day/Intraday(M90) quarter mapping
in one place. Cross-checked against everything already coded:

- **Week row confirms existing v3 correction exactly**: Mon=Q1,
  Tue(Monday 18:00=true week open)=Q2, Wed=Q3, Thu=Q4. No change.
- **Month row confirms existing rule**: Wk1(full week)=Q1, Week2(2nd
  Monday=true month open)=Q2, Wk3=Q3, Wk4=Q4. No change.
- **Year row is GENUINELY NEW** — previously the playbook only stated
  "true year open = first Monday of April" with no documented Q-boundary
  shape. The table gives an ASYMMETRIC yearly quarter split, not
  calendar quarters: Q1 = Jan-Apr, Q2 = Apr-May (contains the true open,
  1 April), Q3 = May-Nov (seven months — most of the year lives in one
  "quarter"), Q4 = Dec only ("resets yearly range"). Added a
  `trueYearOpen` marker (April 1 ET) to the engine; the lopsided
  Q-boundaries themselves are NOT drawn (too coarse to matter for a 5m
  scalping engine and the source gives no session-level trading
  instruction tied to them) but are recorded here per the never-discard
  standing rule.
- **Day row is AMBIGUOUS, flagged rather than resolved**: the table's
  "Day" row reads Q1=Asia(6-12am), Q2=LO(12-6am), Q3="NY(6am-12pm)/PM
  (12-6pm)" (both NY sessions crammed into one cell), Q4="LC" (undefined
  abbreviation, likely "Late Close"). This does NOT cleanly match the
  already-coded 4-way Asia/London/NY-AM/NY-PM day-quarter split (which
  comes from the primary source's own spoken video, v3, and is more
  detailed/reliable than this compiled cheat-sheet's cramped table
  formatting). Not changing the engine off a plausibly-garbled
  table cell — logged as a discrepancy between two same-lineage sources
  for future reconciliation, not adjudicated here.
- Q1-Q4 phase-shorthand column headers in the table (A|O, M|H/L, D|L/H,
  C) are consistent with the already-coded AMDX mapping (Accumulate,
  Manipulate/High-Low, Distribute/Low-High, Continuation) -- no change.

No other pages in this PDF had recoverable image content beyond
decorative checkmark/pin/target emoji glyphs (which pypdf's image
detector flags as "images" but carry no diagram information) --
confirmed by rendering every image-bearing page.

---

## v7 — re-upload verification, plain-text compiled doc (2026-07-20)
Source: "Quarterly Theory by Trader Daye & Compiled by @ransh28.06" (.txt).
Same author credit as the original compiled-PDF source this playbook is
built from. Full read confirms: fractal time quarters (yearly/monthly/
weekly/daily/session/90-min), True Opens, AMDX/XAMD phase mapping (both
forms), session quarter behavior (Q1 range, Q2 expansion, Q3 continuation/
pullback, Q4 reversal/profit-take), Standard/SSMT/90SSMT SMT divergence
taxonomy, and the full PD-array entry strategy chain (quarter/phase ->
SMT scan -> PD-array tap -> inversion/liquidity-grab confirmation ->
laddered SL/TP, 1:3/1:6/1:10 example) all match what's already coded
in indicators/quarterly_theory_engine.pine and documented above. No
contradictions, no genuinely new codeable mechanic. One descriptive-only
addition not previously logged verbatim (source's own "Critiques and
Limitations" section: requires deep market understanding, works best in
London/NY hours not Asia, execution complexity/needs real-time True
Open confirmation) -- not falsifiable/codeable, no H-number, recorded
here as source-stated caveats only. No engine changes, no new
BELIEF_REGISTER entries.
