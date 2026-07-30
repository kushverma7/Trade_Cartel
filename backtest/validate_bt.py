#!/usr/bin/env python3
"""
WIRING CHECK for backtrader — NOT yet a faithful cross-validation.

STATUS: INCOMPLETE. Read this before quoting anything it prints.

The two do NOT agree, and the reason is a genuine execution-model
difference rather than an accounting error:

  fast engine  entry fills at the SIGNAL BAR CLOSE (matching the Pine
               build's process_orders_on_close=true), and stops/targets
               fill intrabar AT THEIR TRIGGER PRICE.
  backtrader   market orders fill at the NEXT BAR OPEN by default, and
               a market close does not fill at the stop price.

Making them comparable needs cheat-on-close plus real Stop/Limit child
orders with OCO handling. Until that is written, this script only proves
backtrader is installed, the data feed maps correctly, and trades execute
on the bars the engine thinks they do.

The accounting itself is instead verified by backtest/test_engine.py,
which checks the fast engine against hand-computed answers on constructed
bar series -- independent expectations rather than a second backtester
with different fill semantics.

One real bug this script already caught: backtrader's setcommission()
defaults to a PERCENTAGE scheme, so commission=0.07 was being read as 7%
of notional (~$280 a contract on gold instead of 7 cents), producing a
fake -43,000 discrepancy on the first run.

  python3 -m backtest.validate_bt --synthetic
"""
import argparse
import backtrader as bt
import numpy as np, pandas as pd
from backtest import engine, levels as L, io as bio, synth
from backtest.optimize import session_mask


class Replay(bt.Strategy):
    params = dict(plan=None, comm=0.07)

    def __init__(self):
        self.plan = {p["bar"]: p for p in self.p.plan}
        self.open_pos = None

    def next(self):
        i = len(self) - 1
        p = self.open_pos
        if p is not None:
            d, px_h, px_l = p["dir"], self.data.high[0], self.data.low[0]
            hit_stop = px_l <= p["sl"] if d > 0 else px_h >= p["sl"]
            hit_tp1 = px_h >= p["tp1"] if d > 0 else px_l <= p["tp1"]
            hit_tp2 = px_h >= p["tp2"] if d > 0 else px_l <= p["tp2"]
            if hit_stop:
                self.close(); self.open_pos = None
            else:
                if hit_tp1 and p["q1"] > 0:
                    self.sell(size=p["q1"]) if d > 0 else self.buy(size=p["q1"])
                    p["qty"] -= p["q1"]; p["q1"] = 0
                if hit_tp2 and p["qty"] > 0:
                    self.close(); self.open_pos = None
                elif p["qty"] <= 0:
                    self.open_pos = None
            if self.open_pos is not None and i - p["bar"] >= p["time_stop"]:
                self.close(); self.open_pos = None
        if self.open_pos is None and i in self.plan:
            pl = dict(self.plan[i])
            self.buy(size=pl["qty"]) if pl["dir"] > 0 else self.sell(size=pl["qty"])
            self.open_pos = pl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv"); ap.add_argument("--synthetic", action="store_true")
    a = ap.parse_args()
    df = synth.make(bars=20000) if a.synthetic else bio.load_csv(a.csv)
    lv = L.build(df); sess = session_mask(df.index)
    cfg = engine.Config(levels=["DO", "PDH", "PDL", "WO", "PWH", "PWL"])

    # capture the plan the fast engine executed
    trades, st = engine.run(df, lv, cfg, sess)
    plan = [dict(bar=t["bar"], dir=t["dir"], qty=t["qty"], q1=t["q1"],
                 sl=t["sl"], tp1=t["tp1"], tp2=t["tp2"],
                 time_stop=cfg.time_stop) for t in trades]
    print(f"fast engine : n={st['n']}  net {st['net']:+.2f}  PF {st['pf']:.3f}")

    cb = bt.Cerebro(stdstats=False)
    cb.adddata(bt.feeds.PandasData(dataname=df))
    cb.broker.setcash(cfg.equity0)
    # COMM_FIXED, not the default percentage scheme. Left at the default,
    # backtrader reads 0.07 as SEVEN PERCENT of notional -- which on gold is
    # ~$280 a contract instead of 7 cents. This exact mistake produced a
    # -43,000 "discrepancy" on the first run of this script.
    cb.broker.setcommission(commission=cfg.commission,
                            commtype=bt.CommInfoBase.COMM_FIXED,
                            stocklike=True)
    cb.broker.set_slippage_fixed(cfg.slippage)
    cb.addstrategy(Replay, plan=plan, comm=cfg.commission)
    start = cb.broker.getvalue()
    cb.run()
    end = cb.broker.getvalue()
    print(f"backtrader  : net {end - start:+.2f} on the same entry bars")
    gap = abs((end - start) - st["net"])
    rel = gap / max(abs(st["net"]), 1e-9) * 100
    print(f"difference  : {gap:.2f}  ({rel:.2f}% of net)")
    print("\nAgreement inside a few percent means the fast engine's fills, "
          "partial exits, commission and slippage accounting are sound. A "
          "large gap means the fast engine is wrong and every number it has "
          "produced should be thrown away.")


if __name__ == "__main__":
    main()
