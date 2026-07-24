# TEST REGISTRY
Known-scenario test cases per SKILL_EXPANSION_FRAMEWORK.md Part II.

**Currently empty of validated cases — deliberately.** A test case
needs a REAL chart scenario (asset, date, time, actual OHLCV values)
with a known correct output. Fabricating "expected outputs" from
imagination would violate this repo's no-fabricated-data rule and make
the suite worse than useless (validating against invented truth).

## How cases get added
1. User spots a clean example on a live chart (or replay) — e.g. a
   textbook sweep+reclaim at VAL that the engine SHOULD have caught,
   or a chop sequence it should have skipped.
2. User supplies: asset, timeframe, date/time, screenshot or OHLCV of
   the relevant bars, and what the correct call was.
3. The case is written up in `test_<pattern>.md` using the framework's
   format, with the expected output derived from the REAL bars.
4. Every subsequent engine change touching that pattern gets mentally
   executed against the case before delivery (Code Delivery Protocol
   Phase 4).

## Wanted first (highest value per the bug history)
- [ ] test_sweep_reclaim.md — one real VAL sweep+reclaim that should
      signal LONG, one fake-out that should NOT (guards BUG-005/007/010)
- [ ] test_bos_confirmation.md — one real breakout bar that should
      fire the bar it closes (guards BUG-008), one range-noise poke
      that should not
- [ ] test_session_detection.md — bars just inside/outside the London
      and NY windows in the user's actual chart timezone
- [ ] test_position_sizing.md — one worked sizing example: equity,
      risk%, stop distance -> expected qty (pure arithmetic, this one
      CAN be authored without chart data)

| Test | File | Guards Against | Status |
|------|------|----------------|--------|
| (none yet) | — | — | awaiting real chart scenarios from user |
