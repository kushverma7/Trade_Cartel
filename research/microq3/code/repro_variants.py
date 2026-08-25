"""Which construction choice explains the gap to the reported numbers?

Reported: 25 trades, PF 4.89, net +365.1, exp +14.60, WR ~72%, maxDD ~15.5.
The trade COUNT reproduces exactly, so any difference is in fills or exits, not
selection. These are the choices the specification leaves open.
"""
import sys, pandas as pd
sys.path.insert(0, "research/microq3/code")
import microq3 as M

rows = []
def add(tag, tr, sl=15.5, tp=25.5):
    d = M.apply(tr, sl, tp); s = M.summarise(d)
    rows.append(dict(variant=tag, n=s["n"], pf=s["pf"], net=s["net"], exp=s["exp"],
                     wr=s["wr"], mdd=s["mdd"],
                     tp_n=int((d.exit_reason == "TP").sum()),
                     sl_n=int((d.exit_reason == "SL").sum()),
                     eod_n=int((d.exit_reason == "EOD").sum())))

# candle construction: mid / bid / ask
for px in ("mid", "bid", "ask"):
    add(f"candles from {px.upper()}", M.signals(px=px))

# EOD liquidation rule
base = M.signals()
for hm, nm in ((17 * 60, "17:00 NY next day (settlement)"),
               (16 * 60, "16:00 NY next day"),
               (0, "00:00 NY (end of Q1)"),
               (9 * 60, "09:00 NY next day")):
    add(f"EOD {nm}", M.signals(eod_hm=hm))

# time stop instead of an EOD ride
for tsm in (60, 120, 240, 480):
    d = M.apply(base, 15.5, 25.5, time_stop_min=tsm); s = M.summarise(d)
    rows.append(dict(variant=f"time stop {tsm}m", n=s["n"], pf=s["pf"], net=s["net"],
                     exp=s["exp"], wr=s["wr"], mdd=s["mdd"],
                     tp_n=int((d.exit_reason == "TP").sum()),
                     sl_n=int((d.exit_reason == "SL").sum()),
                     eod_n=int((d.exit_reason == "TIME").sum())))

df = pd.DataFrame(rows)
df.to_csv("research/microq3/results/repro_variants.csv", index=False)
pd.set_option("display.width", 200)
print("REPORTED:  n=25  PF=4.890  net=+365.1  exp=+14.60  WR~72%  maxDD~15.5\n")
print(df.to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
