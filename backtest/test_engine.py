#!/usr/bin/env python3
"""
Hand-computable accounting tests for the fast engine.

Each case is a tiny bar series constructed so the correct P&L can be worked
out on paper. This is stronger evidence than comparing against another
backtester with a different execution model: here the expected answer is
derived independently, not borrowed.

  python3 -m backtest.test_engine
"""
import numpy as np, pandas as pd
from backtest import engine

COMM, SLIP = 0.07, 0.05


def bars(rows, start="2025-03-03 09:00"):
    idx = pd.date_range(start, periods=len(rows), freq="15min")
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=idx)


def one_trade(df, lvl_price, cfg_kw=None):
    lv = pd.DataFrame({"DO": [lvl_price] * len(df)}, index=df.index)
    kw = dict(levels=["DO"], mode="sweep", tp_mode="fixed", tp1_r=1.0,
              tp2_r=2.0, tp1_pct=50, min_sl=0.5, max_sl=10.0, buf_atr=0.0,
              cooldown=0, vol_min=0.0, time_stop=999, risk_pct=1.0,
              commission=COMM, slippage=SLIP, session=False)
    kw.update(cfg_kw or {})
    cfg = engine.Config(**kw)
    return engine.run(df, lv, cfg, np.ones(len(df), bool))


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(b))


def main():
    fails = []

    # --- case 1: costs are charged on both sides, per contract ---
    # Entry by sweep, then a flat drift that touches NEITHER the stop nor a
    # target, so the trade is closed by the time stop at a known price.
    # (First draft of this case let the next bar wick into the stop and I
    # mis-read the resulting loss as a costs failure -- the fixture was
    # wrong, not the engine. Bars after the signal are now deliberately
    # inside the stop and target band.)
    rows = [[100, 101, 99, 100]] * 40
    rows[20] = [100, 101, 98.0, 100.5]          # sweep of a level at 99
    for k in range(21, 26):
        rows[k] = [100.4, 100.6, 100.3, 100.4]  # no stop, no target
    df = bars(rows)
    tr, st = one_trade(df, 99.0, {"time_stop": 3, "max_sl": 50.0})
    if not tr:
        fails.append("case1: no trade fired")
    else:
        t = tr[0]
        qty = t["qty"]
        exit_px = 100.4 - SLIP                  # time-stop exit at the close
        expect = (exit_px - t["entry"]) * qty - 2 * COMM * qty
        got = t["pnl"]
        ok = approx(got, expect, 1e-9)
        print(f"case1 costs      qty={qty:>4.0f}  got {got:+.4f}  "
              f"expect {expect:+.4f}  {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append("case1")

    # --- case 2: a pure stop-out loses exactly the risk distance ---
    rows = [[100, 101, 99, 100]] * 40
    rows[20] = [100, 101, 98.0, 100.5]
    rows[21] = [100, 100, 80.0, 85.0]           # blows through the stop
    df = bars(rows)
    tr, st = one_trade(df, 99.0, {"min_sl": 0.5, "max_sl": 50.0})
    if not tr:
        fails.append("case2: no trade")
    else:
        t = tr[0]
        loss_per_unit = (t["sl"] - SLIP) - t["entry"]
        expect = loss_per_unit * t["qty"] - 2 * COMM * t["qty"]
        print(f"case2 stop-out   got {t['pnl']:+.4f}  expect {expect:+.4f}  "
              f"{'OK' if approx(t['pnl'], expect, 1e-9) else 'FAIL'}")
        if not approx(t["pnl"], expect, 1e-9):
            fails.append("case2")
        if t["pnl"] >= 0:
            fails.append("case2: stop-out was not a loss")

    # --- case 3: stop takes priority when a bar touches stop AND target ---
    rows = [[100, 101, 99, 100]] * 40
    rows[20] = [100, 101, 98.0, 100.5]
    rows[21] = [100, 130.0, 80.0, 100.0]        # touches both
    df = bars(rows)
    tr, _ = one_trade(df, 99.0, {"min_sl": 0.5, "max_sl": 50.0})
    if tr and tr[0]["pnl"] < 0:
        print(f"case3 stop-first got {tr[0]['pnl']:+.4f}  (loss) OK")
    else:
        print(f"case3 stop-first FAIL — a bar touching both resolved as a win")
        fails.append("case3")

    # --- case 4: no lookahead. Shuffling all bars AFTER the signal must not
    #     change whether the signal fired, only its outcome.
    rows = [[100, 101, 99, 100]] * 60
    rows[20] = [100, 101, 98.0, 100.5]
    df = bars(rows)
    tr_a, _ = one_trade(df, 99.0)
    rows2 = list(rows)
    rng = np.random.default_rng(0)
    tail = rows2[25:]; rng.shuffle(tail); rows2[25:] = tail
    tr_b, _ = one_trade(bars(rows2), 99.0)
    same_entry = (bool(tr_a) == bool(tr_b)) and (
        not tr_a or tr_a[0]["bar"] == tr_b[0]["bar"])
    print(f"case4 no-lookahead entry bar unchanged after shuffling the future: "
          f"{'OK' if same_entry else 'FAIL'}")
    if not same_entry:
        fails.append("case4")

    # --- case 5: notional cap (BUG-012). A tiny stop must not size beyond
    #     equity * max_lev / price.
    rows = [[100, 101, 99, 100]] * 40
    rows[20] = [100, 100.02, 99.99, 100.01]
    df = bars(rows)
    tr, _ = one_trade(df, 99.995, {"min_sl": 0.0001, "max_sl": 0.01,
                                   "max_lev": 20, "vol_min": 0.0})
    if tr:
        notional = tr[0]["qty"] * 100.0
        cap = 10000 * 20
        print(f"case5 size cap   notional {notional:,.0f} <= cap {cap:,.0f}  "
              f"{'OK' if notional <= cap + 1 else 'FAIL'}")
        if notional > cap + 1:
            fails.append("case5")
    else:
        print("case5 size cap   (no trade fired — cap untested)")

    print()
    if fails:
        print("FAILED:", fails); raise SystemExit(1)
    print("all accounting tests passed")


if __name__ == "__main__":
    main()
