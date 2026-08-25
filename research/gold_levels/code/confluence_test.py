"""Is a quarter level "stickier" because a True Open sits on it, or because of
where True Opens sit?

The reported result: a $25 crossing with no key level nearby continues 9.74% of
the time, but a crossing within 2.5 points of the True Daily/Session/Weekly Open
or the classic pivot continues only ~4-5%. Read as "confluence makes a level
twice as sticky".

There is a confound with exactly that signature. The True Daily Open is where
the day STARTED. A quarter sitting on it is a quarter in the middle of the day's
range, which price crosses repeatedly while it churns. A quarter far from every
anchor is one price only reaches by travelling, i.e. by trending. So "near an
anchor" is partly a proxy for "not currently trending", and stickiness follows
for free.

Control: keep the anchor's LOCATION statistics, break its identity. Compare the
real open against the same open displaced a few dollars (still mid-range, no
longer the open) and against a random other day's open transplanted here. If
displaced and transplanted anchors are just as sticky, the stickiness is about
position in the range, not about the open.
"""
import datetime as dt, numpy as np, pandas as pd
from zoneinfo import ZoneInfo

BASE = "/home/user/Trade_Cartel/research/gold_10am_flip/data"
MEL, NY = ZoneInfo("Australia/Melbourne"), ZoneInfo("America/New_York")
t = np.load(f"{BASE}/tk_t.npy", mmap_mode="r")
bid = np.load(f"{BASE}/tk_bid.npy", mmap_mode="r")
ask = np.load(f"{BASE}/tk_ask.npy", mmap_mode="r")
N = len(t)
mid = np.empty(N, np.float64)
for i in range(0, N, 4_000_000):
    mid[i:i + 4_000_000] = (bid[i:i + 4_000_000].astype(np.float64)
                            + ask[i:i + 4_000_000].astype(np.float64)) / 2000.0
tms = np.asarray(t)

# tick timestamps are NAIVE MELBOURNE wall clock (BUG-045); localise before NY
t0 = dt.datetime.fromtimestamp(int(tms[0]) / 1000, dt.timezone.utc).replace(tzinfo=None)
t1 = dt.datetime.fromtimestamp(int(tms[-1]) / 1000, dt.timezone.utc).replace(tzinfo=None)
print(f"ticks {N:,}   Melbourne {t0} .. {t1}")

# True Daily Open = 18:00 New York. Build the 18:00 NY instants across the span,
# convert each back to a naive-Melbourne epoch, and take the first tick at/after.
opens = []
d = t0.date() - dt.timedelta(days=1)
while d <= t1.date():
    ny = dt.datetime.combine(d, dt.time(18, 0), tzinfo=NY)
    mel = ny.astimezone(MEL).replace(tzinfo=None)
    ms = int(mel.replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    k = int(np.searchsorted(tms, ms, side="left"))
    if 0 < k < N - 1000 and abs(int(tms[k]) - ms) < 30 * 60_000:
        opens.append((ms, k, float(mid[k])))
    d += dt.timedelta(days=1)
print(f"true daily opens located: {len(opens)}")

S, TOL = 25.0, 2.5
cell = np.floor(mid / S).astype(np.int32)
ch = np.flatnonzero(np.diff(cell)) + 1
starts = np.concatenate([[0], ch]); k = cell[starts]
dk = np.concatenate([np.diff(k), [0]])
entered_up = np.concatenate([[False], np.diff(k) > 0])
ok = entered_up & (np.abs(dk) == 1)
idx = np.flatnonzero(ok)
ev_i = starts[idx]                       # tick index of each crossing
ev_lvl = k[idx] * S                      # the level crossed
ev_cont = dk[idx] > 0                    # continued to the next level
print(f"$25 crossing events: {len(idx):,}   immediate continuation {100*ev_cont.mean():.2f}%")

# the open in force at each crossing = the most recent 18:00 NY before it
o_idx = np.array([o[1] for o in opens]); o_px = np.array([o[2] for o in opens])
j = np.searchsorted(o_idx, ev_i, side="right") - 1
valid = j >= 0
ev_i, ev_lvl, ev_cont, j = ev_i[valid], ev_lvl[valid], ev_cont[valid], j[valid]
tdo = o_px[j]

rng = np.random.default_rng(3)
sham = o_px[rng.integers(0, len(o_px), len(j))]          # a random other day's open
# transplant it to this day: keep its distance from ITS OWN grid, put it here
sham_here = ev_lvl + (sham - np.floor(sham / S) * S) - S / 2 + (tdo - ev_lvl) * 0

print(f"\n{'='*96}")
print(f"IMMEDIATE CONTINUATION when the crossed $25 level is within ${TOL:g} of an anchor")
print(f"{'='*96}")
print(f"{'anchor':<34}{'near n':>9}{'near cont':>11}   {'far n':>9}{'far cont':>10}{'ratio':>8}")


def show(name, anchor):
    near = np.abs(ev_lvl - anchor) <= TOL
    a, b = ev_cont[near], ev_cont[~near]
    if near.sum() < 200:
        print(f"{name:<34}{int(near.sum()):>9}{'--':>11}   (too few)"); return
    print(f"{name:<34}{int(near.sum()):>9}{100*a.mean():>10.2f}%   {int((~near).sum()):>9}"
          f"{100*b.mean():>9.2f}%{a.mean()/b.mean():>8.2f}")


show("True Daily Open (18:00 NY)", tdo)
for d_ in (-10, -5, 5, 10):
    show(f"   ... displaced {d_:+g}", tdo + d_)
show("   ... a random other day's open", sham_here)
