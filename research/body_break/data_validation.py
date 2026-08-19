"""PHASE 1 — data validation. Nothing runs until this passes.

Produces (a) the coverage audit, and (b) the 10-day table to check by eye
against the TradingView indicator before any backtest is believed.
"""
import sys, os, csv, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
from collections import Counter
import strategy as S


def audit(path, label):
    raw = S.load(path)
    byday = raw["days"]
    days = sorted(byday)
    built = {d: S.build_day(d, byday[d]) for d in days}
    testable = [d for d in days if built[d].side != "UNTESTABLE"]
    sides = Counter(built[d].side for d in days)
    # missing-bar estimate inside the cash window on testable days
    missing = 0
    for d in testable:
        ms = {b.m for b in byday[d].bars} if hasattr(byday[d], "bars") else {b.m for b in byday[d]}
        expect = {m for m in range(S.BODY_MIN, S.CUTOFF, 5)}
        missing += len(expect - ms)
    print(f"\n{'='*72}\n{label}\n{'='*72}")
    print(f"  sessions                     : {len(days)}   {days[0]} .. {days[-1]}")
    print(f"  duplicate timestamps         : {raw['duplicates']}")
    print(f"  timezone conversion          : per-bar UTC -> zoneinfo Australia/Melbourne (DST correct)")
    print(f"  TESTABLE (09:50 AND 10:00)   : {len(testable)}  ({100*len(testable)/len(days):.1f}%)")
    for k in ("ABOVE", "BELOW", "STRADDLE", "UNTESTABLE"):
        print(f"    side {k:11}          : {sides.get(k,0)}")
    if testable:
        yr = Counter(d.year for d in testable)
        print(f"  testable by year             : {dict(sorted(yr.items()))}")
        print(f"  missing 5-min bars 10:00-16:00 on testable days: {missing}")
    return built, testable


def validation_table(built, testable, n=10):
    print(f"\n  TEN-DAY VALIDATION TABLE — compare each row against TradingView")
    print(f"  {'date':11} {'09:50 open':>10} {'10:00 o':>9} {'10:00 c':>9} "
          f"{'bodyHi':>9} {'bodyLo':>9} {'side':9} {'A time':>7} {'A dir':>6} "
          f"{'B dir':>6} {'flip':>7} {'fdir':>5}")
    step = max(1, len(testable) // n)
    for d in testable[::step][:n]:
        D = built[d]
        a = S.logic_a(D); b = S.logic_b(D)
        at = f"{a[1].m//60:02d}:{a[1].m%60:02d}" if a else "-"
        ad = ("LONG" if a[0] > 0 else "SHORT") if a else "-"
        bd = ("LONG" if b[0] > 0 else "SHORT") if b else "-"
        ft, fd = "-", "-"
        if a:
            f = S.first_flip(D, a[0], a[1].m)
            if f:
                ft = f"{f.m//60:02d}:{f.m%60:02d}"
                fd = "SELL" if a[0] > 0 else "BUY"
        print(f"  {str(d):11} {D.daily_open:>10.2f} {D.body_open:>9.2f} {D.body_close:>9.2f} "
              f"{D.body_hi:>9.2f} {D.body_lo:>9.2f} {D.side:9} {at:>7} {ad:>6} {bd:>6} "
              f"{ft:>7} {fd:>5}")


if __name__ == "__main__":
    ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    jobs = [(os.path.join(ROOT, "au200_5m.csv.gz"), "AU200 5-minute  (repo copy, OANDA AU200AUD export)")]
    gold5 = os.path.join(ROOT, "xauusd_5m.csv.gz")
    if os.path.exists(gold5):
        jobs.append((gold5, "XAUUSD 5-minute"))
    else:
        print("\nXAUUSD 5-minute: NOT PRESENT. data/ holds xauusd_15m.csv.gz only.")
        print("The spec requires 5-minute candles, so GOLD CANNOT BE TESTED AT ALL.")
    for path, label in jobs:
        built, testable = audit(path, label)
        if testable:
            validation_table(built, testable)
        if len(testable) < 300:
            print(f"\n  *** PHASE 1 FAIL: {len(testable)} testable sessions is below the "
                  f"3-year minimum in the spec. Backtest NOT run. ***")
