"""Build the master trade ledger: every setup day, every logic, every trade,
with the full 1-minute path attached.

One row per (date, logic) — each logic is decomposed independently so a good
branch cannot hide a bad one. Combinations are assembled later from these rows
under the daily state machine.

Baseline exits reproduce the Pine implementation exactly:
    SL = 18 - cost/2  ->  $17.00
    TP = 40 - cost/2  ->  $39.00
on XAUUSD these are DOLLARS PER OUNCE, not points or pips.

Path metrics (MAE, MFE, first passage, forward returns) are computed once, on
1-minute data, independent of any SL/TP choice, so every later phase re-uses
the same paths instead of re-walking them.
"""
import os, sys, csv, json, gzip, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

PROC = core.PROC
TAB = os.path.join(core.HERE, "..", "tables")

BASE_SL = 17.0
BASE_TP = 39.0

FP_LEVELS = [1, 2, 3, 5, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 75, 100]
FWD_MIN = [1, 2, 3, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180]
FWD_BARS = [1, 2, 3, 4, 5, 6, 10, 12]


def atr_5m(day_bars, upto_minute, n=14):
    """True range ATR over the 5m bars strictly BEFORE upto_minute.
    Known at entry — no lookahead."""
    prior = [b for b in day_bars if b["minute"] < upto_minute]
    if len(prior) < 2:
        return None
    trs = []
    for i in range(1, len(prior)):
        h, l, pc = prior[i]["high"], prior[i]["low"], prior[i - 1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    trs = trs[-n:]
    return sum(trs) / len(trs) if trs else None


def main():
    print("loading ...", flush=True)
    raw = core.load_1m(os.path.join(core.RAW, "xauusd_1m_bid_dukascopy.csv.gz"))
    mrows = core.to_melbourne(raw)
    bars5 = core.build_5m(mrows)
    days5 = core.by_day(bars5)
    dmins = core.minutes_by_day(mrows)

    setups, ledger = [], []
    for d in sorted(days5):
        if d.weekday() >= 5:
            continue
        su = core.setup(days5[d])
        if su is None:
            continue
        body = su["body"]
        rng = body["high"] - body["low"]
        setups.append(dict(
            date=d.isoformat(), dst="AEDT" if su["dst"] else "AEST",
            weekday=d.strftime("%a"), year=d.year, month=f"{d.year}-{d.month:02d}",
            d_open=su["d_open"], b_hi=su["b_hi"], b_lo=su["b_lo"], side=su["side"],
            body_open=body["open"], body_close=body["close"],
            body_high=body["high"], body_low=body["low"],
            body_size=su["b_hi"] - su["b_lo"], body_range=rng,
            upper_wick=body["high"] - su["b_hi"], lower_wick=su["b_lo"] - body["low"],
            body_ratio=(su["b_hi"] - su["b_lo"]) / rng if rng > 0 else 0.0,
            close_vs_dopen=body["close"] - su["d_open"],
            open_vs_dopen=body["open"] - su["d_open"],
            bhi_vs_dopen=su["b_hi"] - su["d_open"], blo_vs_dopen=su["b_lo"] - su["d_open"],
            body_straddle=(su["b_lo"] < su["d_open"] < su["b_hi"]),
            full_straddle=(body["low"] < su["d_open"] < body["high"]),
            ref_range=su["ref"]["high"] - su["ref"]["low"],
            atr14=atr_5m(days5[d], core.BODY_MIN + 5) or 0.0,
        ))

        mins = dmins[d]
        eod = max(m["minute"] for m in mins)
        # every logic's FIRST trigger of the day, independently
        seen = set()
        for t in core.triggers(su, days5[d]):
            if t["logic"] in seen:
                continue
            seen.add(t["logic"])
            side = core.DIRECTION[t["logic"]]
            path = core.path_after(mins, t["minute"])
            base = core.resolve(t["entry"], side, BASE_SL, BASE_TP, path, eod)
            row = dict(
                date=d.isoformat(), logic=t["logic"], side=side,
                dst="AEDT" if su["dst"] else "AEST", weekday=d.strftime("%a"),
                year=d.year, month=f"{d.year}-{d.month:02d}",
                setup_side=su["side"], d_open=su["d_open"],
                b_hi=su["b_hi"], b_lo=su["b_lo"],
                entry_minute=t["minute"], entry=t["entry"],
                entry_time=f"{t['minute']//60:02d}:{t['minute']%60:02d}",
                bars_to_entry=(t["minute"] - core.BODY_MIN) // 5,
                dist_beyond=(t["entry"] - su["b_hi"]) if side > 0 else (su["b_lo"] - t["entry"]),
                sig_body=abs(t["bar"]["close"] - t["bar"]["open"]),
                sig_range=t["bar"]["high"] - t["bar"]["low"],
                atr14=atr_5m(days5[d], t["minute"]) or 0.0,
                path_len=len(path), eod_minute=eod,
                base_outcome=base["outcome"], base_pnl=base["pnl_pess"],
                base_pnl_opt=base["pnl_opt"], base_bars=base["bars"],
                base_exit_minute=base["exit_minute"],
                mae=base["mae"], mfe=base["mfe"],
                t_mae=base["t_mae"], t_mfe=base["t_mfe"],
            )
            # unconditional path metrics (no SL/TP): run to EOD
            full = core.resolve(t["entry"], side, 1e9, 1e9, path, eod)
            row["mae_full"] = full["mae"]; row["mfe_full"] = full["mfe"]
            row["t_mae_full"] = full["t_mae"]; row["t_mfe_full"] = full["t_mfe"]
            row["eod_pnl"] = full["pnl_pess"]
            for x in FP_LEVELS:
                w, k = core.first_passage(t["entry"], side, x, path, eod)
                row[f"fp_{x}"] = w
                row[f"fpt_{x}"] = k if k is not None else ""
            for n in FWD_MIN:
                sub = path[:n]
                row[f"fwd_{n}m"] = ((sub[-1]["close"] - t["entry"]) * side) if sub else ""
            for n in FWD_BARS:
                sub = path[:n * 5]
                row[f"fwd_{n}b"] = ((sub[-1]["close"] - t["entry"]) * side) if sub else ""
            ledger.append(row)

    os.makedirs(PROC, exist_ok=True); os.makedirs(TAB, exist_ok=True)
    with open(os.path.join(PROC, "setups.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(setups[0].keys())); w.writeheader(); w.writerows(setups)
    with open(os.path.join(PROC, "trades.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ledger[0].keys())); w.writeheader(); w.writerows(ledger)

    import collections
    c = collections.Counter(r["logic"] for r in ledger)
    print(f"setup days: {len(setups)}")
    print("trades per logic:", dict(c))
    for lg in core.LOGICS:
        p = [r["base_pnl"] for r in ledger if r["logic"] == lg]
        m = core.metrics(p)
        if m["n"]:
            print(f"  {lg:<8} n={m['n']:>4} win%={m['win_pct']:5.1f} PF={m['pf']:6.3f} "
                  f"net=${m['net']:>9.2f} exp=${m['expectancy']:>7.3f} absurd={m['absurd']}")
    print("wrote data/processed/setups.csv and trades.csv")


if __name__ == "__main__":
    main()
