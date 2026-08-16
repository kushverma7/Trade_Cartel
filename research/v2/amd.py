"""AMD + 1 FVG Distribution Signal — exact port, tested on AU200.

PORT, DON'T REIMPLEMENT. Signal layer is line-for-line from the supplied v5.
The indicator has no exits, so exits are swept; the signal layer is untouched.

STEP 0 (mandatory, R1): the three sessions are defined in America/New_York.
On an Australian index that places DISTRIBUTION in the Melbourne night. Report
bar coverage for each window BEFORE reporting any performance number.
"""
import sys, csv, datetime as dt, zoneinfo, math, itertools, statistics as st
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import engine
from collections import defaultdict

UTC = dt.timezone.utc
NY = zoneinfo.ZoneInfo("America/New_York")
MEL = zoneinfo.ZoneInfo("Australia/Melbourne")
U = "/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/"


def load(path, agg_1m=False):
    rows = []
    for r in csv.DictReader(open(path)):
        t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
        rows.append([t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])])
    rows.sort(key=lambda x: x[0])
    if not agg_1m:
        return [tuple(r) for r in rows]
    out, cur, key = [], None, None
    for t, o, h, l, c in rows:
        k = int(t.timestamp()) // 300
        if k != key:
            if cur:
                out.append(tuple(cur))
            key, cur = k, [t, o, h, l, c]
        else:
            cur[2] = max(cur[2], h); cur[3] = min(cur[3], l); cur[4] = c
    if cur:
        out.append(tuple(cur))
    return out


def in_win(mn, start, end):
    """minutes-past-midnight in session tz; window may cross midnight."""
    return (start <= mn < end) if start < end else (mn >= start or mn < end)


ACC = (19 * 60, 1 * 60)        # 1900-0100
MAN = (1 * 60, 7 * 60)         # 0100-0700
DIS = (7 * 60, 13 * 60)        # 0700-1300


def coverage(bars, tag):
    """How many AMD cycles have bars in each window, and how many bars."""
    cyc = defaultdict(lambda: dict(a=0, m=0, d=0))
    for t, o, h, l, c in bars:
        nt = t.astimezone(NY)
        mn = nt.hour * 60 + nt.minute
        # a cycle is keyed by the NY date on which its accumulation STARTS
        key = nt.date() if mn >= 19 * 60 else nt.date() - dt.timedelta(days=1)
        if in_win(mn, *ACC): cyc[key]["a"] += 1
        elif in_win(mn, *MAN): cyc[key]["m"] += 1
        elif in_win(mn, *DIS): cyc[key]["d"] += 1
    full = [k for k, v in cyc.items() if v["a"] and v["m"] and v["d"]]
    print(f"\n=== COVERAGE — {tag} ===")
    print(f"  AMD cycles touched by any bar          : {len(cyc)}")
    print(f"  cycles with bars in ALL THREE windows  : {len(full)}"
          f"   ({100*len(full)/max(1,len(cyc)):.1f}%)   <-- the only testable ones")
    for k, nm in (("a", "accumulation 1900-0100 NY"), ("m", "manipulation 0100-0700 NY"),
                  ("d", "distribution  0700-1300 NY")):
        got = [v[k] for v in cyc.values() if v[k]]
        print(f"    {nm}: present on {len(got):5d} cycles, "
              f"median {int(st.median(got)) if got else 0} bars"
              f" (a complete 5m window would be {(360 if k!='a' else 360)//5})")
    if full:
        ex = sorted(full)[len(full)//2]
        print(f"  Melbourne local equivalent on {ex}:")
        for k, nm, w in (("a", "accumulation", ACC), ("m", "manipulation", MAN),
                         ("d", "distribution", DIS)):
            s = dt.datetime.combine(ex, dt.time(w[0]//60, w[0] % 60), tzinfo=NY)
            e = s + dt.timedelta(minutes=(w[1]-w[0]) % 1440)
            print(f"    {nm:13} {s.astimezone(MEL):%H:%M} -> {e.astimezone(MEL):%H:%M} Melbourne")
    return sorted(full), cyc


def signals(bars, cycles, require_reentry=True):
    """Line-for-line port. Returns list of (cycle, dir, index_into_bars)."""
    keyof = []
    for t, o, h, l, c in bars:
        nt = t.astimezone(NY)
        mn = nt.hour * 60 + nt.minute
        keyof.append((nt.date() if mn >= 19*60 else nt.date() - dt.timedelta(days=1), mn))
    want = set(cycles)
    accumHigh = accumLow = None
    sweepDir = 0
    signalDone = False
    curcyc = None
    out = []
    for i, (t, o, h, l, c) in enumerate(bars):
        key, mn = keyof[i]
        inA, inM, inD = in_win(mn, *ACC), in_win(mn, *MAN), in_win(mn, *DIS)
        if inA and key != curcyc:                       # accumStart
            curcyc = key
            accumHigh, accumLow = h, l
            sweepDir, signalDone = 0, False
        if inA and key == curcyc:
            accumHigh = h if accumHigh is None else max(accumHigh, h)
            accumLow = l if accumLow is None else min(accumLow, l)
        if key != curcyc:
            continue
        highSweep = accumHigh is not None and h > accumHigh and (not require_reentry or c < accumHigh)
        lowSweep = accumLow is not None and l < accumLow and (not require_reentry or c > accumLow)
        if inM and sweepDir == 0:
            if highSweep:
                sweepDir = 1
            elif lowSweep:
                sweepDir = -1
        if i >= 2:
            bullFVG = l > bars[i-2][2]
            bearFVG = h < bars[i-2][3]
        else:
            bullFVG = bearFVG = False
        if inD and not signalDone and key in want:
            if sweepDir == -1 and bullFVG:
                signalDone = True
                out.append((key, 1, i))
            elif sweepDir == 1 and bearFVG:
                signalDone = True
                out.append((key, -1, i))
    return out


# ------------------------------------------------------------------ execution
def run(bars, sigs, stop_k, exit_k, be, cost=2.0, atr=None):
    """Entry at the signal bar's CLOSE. Path starts the NEXT bar (R2).
    Adverse extreme first (R3). Stop frozen, trail on closes (R4).
    Deadline = end of the distribution window, 13:00 New York."""
    tr = []
    for key, s, i in sigs:
        t, o, h, l, c = bars[i]
        e = c
        a = atr[i] if atr and atr[i] else None
        # the FVG's far edge, per the indicator's own box geometry
        fvg_far = bars[i-2][2] if s > 0 else bars[i-2][3]
        if   stop_k == "fvg_far":  sp = fvg_far
        elif stop_k == "fvg_far2": sp = fvg_far - s * 2
        elif stop_k == "bar_far":  sp = l if s > 0 else h
        elif stop_k == "atr0.5":   sp = e - s * (a or 10) * 0.5
        elif stop_k == "atr1.0":   sp = e - s * (a or 10) * 1.0
        elif stop_k == "fixed15":  sp = e - s * 15
        elif stop_k == "fixed30":  sp = e - s * 30
        if s * (e - sp) <= 0:                                   # R8
            continue
        risk = abs(e - sp)
        if risk < 3.0 or risk > 80.0:                           # R5
            continue
        tp = trail = None
        if   exit_k == "1R":   tp = e + s * risk
        elif exit_k == "1.5R": tp = e + s * risk * 1.5
        elif exit_k == "2R":   tp = e + s * risk * 2
        elif exit_k == "3R":   tp = e + s * risk * 3
        elif exit_k == "fixed20": tp = e + s * 20
        elif exit_k == "atr1.0":  tp = e + s * (a or 10)
        elif exit_k == "trail_atr0.5": trail = (a or 10) * 0.5
        elif exit_k == "trail_atr1.0": trail = (a or 10) * 1.0
        elif exit_k == "session": pass
        peak, cur, pnl = e, sp, None
        for j in range(i + 1, len(bars)):
            t2, o2, h2, l2, c2 = bars[j]
            nt = t2.astimezone(NY)
            mn = nt.hour * 60 + nt.minute
            adv = l2 if s > 0 else h2
            fav = h2 if s > 0 else l2
            if s * (adv - cur) <= 0:
                pnl = s * (cur - e) - cost; break
            if tp is not None and s * (fav - tp) >= 0:
                pnl = s * (tp - e) - cost; break
            if be and s * (fav - (e + s * risk * 0.5)) >= 0 and s * (e - cur) > 0:
                cur = e
            if trail is not None:
                if s * (c2 - peak) > 0:
                    peak = c2
                t3 = peak - s * trail
                if s * (t3 - cur) > 0:
                    cur = t3
            if not in_win(mn, *DIS):                 # distribution window closed
                pnl = s * (c2 - e) - cost; break
        if pnl is None:
            pnl = s * (bars[-1][4] - e) - cost
        tr.append(dict(day=key, s=s, pnl=pnl, risk=risk))
    return tr


def atr_series(bars, n=14):
    tr, out, a = [], [], None
    for i, b in enumerate(bars):
        x = b[2] - b[3] if i == 0 else max(b[2]-b[3], abs(b[2]-bars[i-1][4]), abs(b[3]-bars[i-1][4]))
        tr.append(x)
        if i < n - 1:
            out.append(None); continue
        a = sum(tr[:n]) / n if a is None else (a * (n - 1) + x) / n
        out.append(a)
    return out


STOPS = ["fvg_far", "fvg_far2", "bar_far", "atr0.5", "atr1.0", "fixed15", "fixed30"]
EXITS = ["1R", "1.5R", "2R", "3R", "fixed20", "atr1.0", "trail_atr0.5", "trail_atr1.0", "session"]
