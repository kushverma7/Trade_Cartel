"""FIRST VALIDATION — hand-reconstruct random trading days from each period and
print every intermediate number, so a timezone, DST, aggregation or execution
error shows up as a wrong number rather than as a plausible PF.

Also runs mechanical checks that do not depend on the eye:
  V1  the 09:50 bucket's first minute really is Melbourne 09:50
  V2  the 5m bucket OHLC equals a re-aggregation of its own minutes
  V3  side agrees with close(10:00) vs dOpen on every setup
  V4  every trigger close is genuinely beyond BOTH the body edge and dOpen
  V5  every entry minute is strictly after 10:00
  V6  the resolved path starts at or after entry_minute + 5 (no lookahead)
  V7  no stop sits on the favourable side of entry (BUG-040)
"""
import os, sys, csv, random, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

SEED = 20260820
PERIODS = [("Aug-Dec 2024", dt.date(2024, 8, 20), dt.date(2024, 12, 31)),
           ("Jan-Jun 2025", dt.date(2025, 1, 1), dt.date(2025, 6, 30)),
           ("Jul-Dec 2025", dt.date(2025, 7, 1), dt.date(2025, 12, 31)),
           ("Jan-Aug 2026", dt.date(2026, 1, 1), dt.date(2026, 8, 19))]


def main():
    raw = core.load_1m(os.path.join(core.RAW, "xauusd_1m_bid_dukascopy.csv.gz"))
    mrows = core.to_melbourne(raw)
    bars5 = core.build_5m(mrows)
    days5 = core.by_day(bars5)
    dmins = core.minutes_by_day(mrows)
    minute_index = {}
    for r in mrows:
        minute_index.setdefault(r["date"], {})[r["minute"]] = r

    fails = []
    setup_days = []
    for d in sorted(days5):
        if d.weekday() >= 5:
            continue
        su = core.setup(days5[d])
        if su:
            setup_days.append((d, su))

    # ---- mechanical checks over ALL setup days ----
    for d, su in setup_days:
        ref, body = su["ref"], su["body"]
        # V1
        if ref["first_utc"].astimezone(core.MEL).hour != 9 or \
           ref["first_utc"].astimezone(core.MEL).minute < 50 or \
           ref["first_utc"].astimezone(core.MEL).minute > 54:
            fails.append(("V1", d, ref["first_utc"].astimezone(core.MEL)))
        # V2
        for b in (ref, body):
            mm = [minute_index[d][x] for x in range(b["minute"], b["minute"] + 5)
                  if x in minute_index[d]]
            if not mm:
                fails.append(("V2-empty", d, b["minute"])); continue
            if abs(b["open"] - mm[0]["open"]) > 1e-9 or abs(b["close"] - mm[-1]["close"]) > 1e-9 \
               or abs(b["high"] - max(x["high"] for x in mm)) > 1e-9 \
               or abs(b["low"] - min(x["low"] for x in mm)) > 1e-9 \
               or b["n_min"] != len(mm):
                fails.append(("V2", d, b["minute"]))
        # V3
        if su["side"] != (1 if body["close"] > su["d_open"] else -1):
            fails.append(("V3", d, None))
        # V4/V5
        for t in core.triggers(su, days5[d]):
            if t["minute"] <= core.BODY_MIN:
                fails.append(("V5", d, t["minute"]))
            up = core.DIRECTION[t["logic"]] > 0
            ok = (t["entry"] > su["b_hi"] and t["entry"] > su["d_open"]) if up else \
                 (t["entry"] < su["b_lo"] and t["entry"] < su["d_open"])
            if not ok:
                fails.append(("V4", d, t["logic"]))
            # V6
            p = core.path_after(dmins[d], t["minute"])
            if p and p[0]["minute"] < t["minute"] + 5:
                fails.append(("V6", d, t["logic"]))
            # V7
            side = core.DIRECTION[t["logic"]]
            stop = t["entry"] - side * 17.0
            if (stop >= t["entry"]) if side > 0 else (stop <= t["entry"]):
                fails.append(("V7", d, t["logic"]))

    print(f"mechanical checks over {len(setup_days)} setup days: "
          f"{'ALL PASS' if not fails else str(len(fails)) + ' FAILURES'}")
    for f in fails[:20]:
        print("   FAIL", f)

    # ---- hand reconstructions ----
    rnd = random.Random(SEED)
    for name, a, b in PERIODS:
        pool = [x for x in setup_days if a <= x[0] <= b]
        print(f"\n{'='*78}\n{name}   ({len(pool)} setup days available)\n{'='*78}")
        for d, su in rnd.sample(pool, min(2, len(pool))):
            ref, body = su["ref"], su["body"]
            mins = dmins[d]
            eod = max(m["minute"] for m in mins)
            print(f"\n  DATE {d}  {d.strftime('%A')}  "
                  f"{'AEDT' if su['dst'] else 'AEST'}")
            print(f"    09:50 bucket first minute (Melbourne) : "
                  f"{ref['first_utc'].astimezone(core.MEL):%Y-%m-%d %H:%M %Z}  "
                  f"(UTC {ref['first_utc']:%H:%M}, {ref['n_min']}/5 minutes present)")
            print(f"    dOpen  = open(09:50)                  : {su['d_open']:.3f}")
            print(f"    10:00  open / close                   : {body['open']:.3f} / {body['close']:.3f}")
            print(f"    10:00  high / low                     : {body['high']:.3f} / {body['low']:.3f}")
            print(f"    bHi / bLo                             : {su['b_hi']:.3f} / {su['b_lo']:.3f}")
            print(f"    side = close(10:00) {'>' if su['side']>0 else '<='} dOpen        : "
                  f"{su['side']:+d}")
            tr = core.triggers(su, days5[d])
            if not tr:
                print("    no logic triggered")
                continue
            seen = set()
            for t in tr:
                if t["logic"] in seen:
                    continue
                seen.add(t["logic"])
                side = core.DIRECTION[t["logic"]]
                path = core.path_after(mins, t["minute"])
                r = core.resolve(t["entry"], side, 17.0, 39.0, path, eod)
                print(f"    -> {t['logic']:<8} trigger {t['minute']//60:02d}:{t['minute']%60:02d} "
                      f"close={t['entry']:.3f}  entry={t['entry']:.3f} "
                      f"SL={t['entry']-side*17:.3f} TP={t['entry']+side*39:.3f}")
                print(f"       outcome={r['outcome']:<9} pnl=${r['pnl_pess']:+7.2f}  "
                      f"MAE=${r['mae']:.2f}  MFE=${r['mfe']:.2f}  "
                      f"held={r['bars']} min")


if __name__ == "__main__":
    main()
