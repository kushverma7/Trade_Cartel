"""
The four-step liquidity methodology, coded mechanically for AU200.

THE RULE AS POSTED (screenshots, NQ 15m)
  Step 1  Context: price approaching a higher-timeframe pivot zone -- major
          supply/demand, previous highs/lows, support/resistance, weekly /
          daily / 4H pivots. "Is price approaching an important area? If not,
          no trade."
  Step 2  Liquidity: price must move BEYOND that zone -- sweep the previous
          high or low, push through supply or demand. Never chase the break;
          the move exists to trigger stops.
  Step 3  Structure shift: proof the move is failing -- higher low after a
          sell-side sweep, lower high after a buy-side sweep, break of the
          opposing structure, or strong displacement away from the grab.
          "Without a structure shift, no trade."
  Step 4  Retest: do not enter during the sweep. Wait for price to return to
          the defended area and trade the reaction off the retest.
  Plus:   VIX inverse confirmation, VIX at its own pivot, Magnificent Seven
          agreeing, and risk-to-reward of at least 2:1.

WHAT IS AND IS NOT TESTABLE HERE, STATED BEFORE ANY NUMBER
  TESTABLE on the data in this repo: steps 1-4 in full, plus the 2:1 RR floor.
  NOT TESTABLE: the VIX confirmation and the Magnificent Seven confirmation.
  There is no VIX series in this environment, and the equity-index VIX is not
  the right instrument for AU200 in any case (the ASX analogue is the A-VIX,
  which is also absent). The Magnificent Seven are US single stocks with no
  mechanical mapping to an Australian index.
  Consequence: this file tests the METHOD'S SKELETON, not the author's full
  process. If the skeleton has no edge that does not prove the full process has
  none -- but it does show whether the mechanical core carries anything, which
  is the part that could ever be automated.

RELATION TO WORK ALREADY DONE
  The gold level study measured raw sweep-fading across nine level families and
  found nothing (best |t| 2.60 of 40 tests; sweep win rates 47.7-53.3% against a
  displaced-level control). THIS rule is strictly stricter: it additionally
  demands a structure shift and a retest before entering. That is a different
  hypothesis and is why it is worth running rather than inheriting the old kill.
"""
import numpy as np, pandas as pd


def swings(h, l, left=3, right=3):
    """Confirmed swing highs/lows. A pivot at i is only KNOWN at i+right, so the
    arrays return the value dated to the bar on which it becomes usable."""
    n = len(h)
    sh = np.full(n, np.nan); sl = np.full(n, np.nan)
    for i in range(left, n - right):
        w = h[i - left:i + right + 1]
        if h[i] == w.max() and (w == h[i]).sum() == 1:
            sh[i + right] = h[i]
        w = l[i - left:i + right + 1]
        if l[i] == w.min() and (w == l[i]).sum() == 1:
            sl[i + right] = l[i]
    return sh, sl


def htf_levels(df):
    """Step 1 zones: previous day/week/4H extremes. All strictly backward."""
    idx = df.index
    out = {}
    day = pd.Series(idx.date, index=idx)
    wk = pd.Series(idx.to_period("W"), index=idx)
    h4 = pd.Series(idx.floor("4h"), index=idx)
    for tag, key in (("D", day), ("W", wk), ("H4", h4)):
        g = df.groupby(key)
        out[f"P{tag}H"] = key.map(g["high"].max().shift(1)).to_numpy(float)
        out[f"P{tag}L"] = key.map(g["low"].min().shift(1)).to_numpy(float)
    return out


def signals(df, sweep_win=8, shift_win=12, retest_win=24, left=3, right=3,
            long_only=False):
    """Returns entry direction per bar, plus the stop level for each entry.

    The state machine is strictly forward-only:
      ARMED     a sweep of an HTF level printed (wick beyond, close back inside)
      SHIFTED   within `shift_win` bars a confirmed swing prints on the correct
                side of the sweep -- a higher low after a sell-side sweep, a
                lower high after a buy-side sweep
      ENTER     within `retest_win` bars price returns to the defended level
                and closes back in the trade's direction
    Every component uses only confirmed, closed-bar information.
    """
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    n = len(c)
    L = htf_levels(df)
    sh, sl = swings(h, l, left, right)
    prev_c = np.r_[c[0], c[:-1]]

    d = np.zeros(n, np.int8)
    stop = np.full(n, np.nan)

    # sweep detection against every HTF level, both sides
    for i in range(n):
        pass  # placeholder; state machine below is the real pass

    state = None
    for i in range(n):
        if state is not None:
            age = i - state["bar"]
            if state["phase"] == "armed":
                if age > shift_win:
                    state = None
                else:
                    if state["dir"] > 0:
                        # sell-side sweep -> need a confirmed HIGHER LOW
                        if np.isfinite(sl[i]) and sl[i] > state["extreme"]:
                            state.update(phase="shifted", bar=i, pivot=sl[i])
                    else:
                        if np.isfinite(sh[i]) and sh[i] < state["extreme"]:
                            state.update(phase="shifted", bar=i, pivot=sh[i])
            elif state["phase"] == "shifted":
                if age > retest_win:
                    state = None
                else:
                    lv = state["level"]
                    back = (l[i] <= lv and c[i] > lv) if state["dir"] > 0 else \
                           (h[i] >= lv and c[i] < lv)
                    if back and not (long_only and state["dir"] < 0):
                        d[i] = state["dir"]
                        stop[i] = (state["extreme"] if state["dir"] > 0
                                   else state["extreme"])
                        state = None
                    elif ((c[i] < state["extreme"]) if state["dir"] > 0
                          else (c[i] > state["extreme"])):
                        state = None          # the sweep low/high gave way
        if state is None:
            for nm, lv in L.items():
                v = lv[i]
                if not np.isfinite(v):
                    continue
                if l[i] < v and c[i] > v and prev_c[i] > v:
                    state = dict(phase="armed", dir=1, bar=i, level=v,
                                 extreme=l[i], src=nm)
                    break
                if h[i] > v and c[i] < v and prev_c[i] < v:
                    state = dict(phase="armed", dir=-1, bar=i, level=v,
                                 extreme=h[i], src=nm)
                    break
    return d, stop


def run_rr(df5, d15, stop15, sig_index, slip=1.0, comm=1.0, rr=2.0,
           min_stop=10.0, max_bars=0):
    """Walk the 5m path. Stop beyond the sweep extreme, target rr x risk.

    Fills at the 5m bar OPEN on the bar the 15m signal becomes knowable
    (index shifted one full 15m bar), gap-aware stops -- the same discipline
    the engine integrity gate established.
    """
    o, h, l, c = (df5[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    sig = pd.Series(d15, index=sig_index)
    stp = pd.Series(stop15, index=sig_index)
    sig.index = sig.index + pd.Timedelta(minutes=15)
    stp.index = stp.index + pd.Timedelta(minutes=15)
    S = sig.reindex(df5.index).fillna(0).to_numpy().astype(np.int8)
    P = stp.reindex(df5.index).to_numpy()
    day = df5.index.normalize().to_numpy()
    tr = []; pos = None
    for i in range(1, len(c)):
        if pos is not None:
            dd = pos["d"]
            hit_s = (l[i] <= pos["stop"]) if dd > 0 else (h[i] >= pos["stop"])
            hit_t = (h[i] >= pos["tgt"]) if dd > 0 else (l[i] <= pos["tgt"])
            if hit_s:
                fill = min(pos["stop"], o[i]) if dd > 0 else max(pos["stop"], o[i])
                tr.append(dict(pnl=dd * (fill - dd * slip - pos["e"]) - 2 * comm,
                               day=pos["day"], why="stop"))
                pos = None; continue
            if hit_t:
                tr.append(dict(pnl=dd * (pos["tgt"] - dd * slip - pos["e"]) - 2 * comm,
                               day=pos["day"], why="target"))
                pos = None; continue
            if max_bars and (i - pos["bar"]) >= max_bars:
                tr.append(dict(pnl=dd * (o[i] - dd * slip - pos["e"]) - 2 * comm,
                               day=pos["day"], why="time"))
                pos = None; continue
        if pos is None and S[i] != 0 and np.isfinite(P[i]):
            dd = int(S[i]); e = o[i] + dd * slip
            risk = abs(e - P[i])
            if risk < min_stop:
                continue                      # no sub-10-point stops, per protocol
            pos = dict(d=dd, e=e, stop=P[i], tgt=e + dd * rr * risk,
                       bar=i, day=day[i])
    return pd.DataFrame(tr)
