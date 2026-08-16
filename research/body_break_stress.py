"""10 AM BODY BREAK — mandated stress tests against the baseline.

Signal generation is UNCHANGED throughout: Logic A, flip on, proxy daily open,
entry at the signal bar's close. Only stops, targets, filters, costs vary.
"""
import csv, datetime as dt, zoneinfo, math, random, statistics as st
from collections import defaultdict

UTC = dt.timezone.utc
MEL = zoneinfo.ZoneInfo("Australia/Melbourne")
SRC = "/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/30348eaf-au200_aud_5m.csv"

rows = []
for r in csv.DictReader(open(SRC)):
    t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    rows.append((t.astimezone(MEL), float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
rows.sort()
day_bars = defaultdict(list)
for r in rows:
    day_bars[r[0].date()].append(r)
DAYS = sorted(day_bars)

# ATR(14) on the continuous 5-minute series, indexed by (day, bar index)
ATR = {}
prev_close = None
tr_hist = []
a = None
for d in DAYS:
    for i, (t, o, h, l, c) in enumerate(day_bars[d]):
        tr = (h - l) if prev_close is None else max(h - l, abs(h - prev_close), abs(l - prev_close))
        tr_hist.append(tr)
        if len(tr_hist) >= 14:
            a = sum(tr_hist[:14]) / 14 if a is None else (a * 13 + tr) / 14
        ATR[(d, i)] = a
        prev_close = c


def signals(day, end_hour, flip=True, flip_cutoff=None):
    bs = day_bars[day]
    do = bh = bl = None
    side = active = 0
    flipped = False
    out = []
    for i, (t, o, h, l, c) in enumerate(bs):
        hh, mm = t.hour, t.minute
        if do is None and (hh < 10 or (hh == 10 and mm == 0)):
            do = o
        if hh == 10 and mm == 0 and do is not None:
            bh = max(o, c); bl = min(o, c)
            side = -1 if bh < do else (1 if bl > do else 0)
        after = (hh > 10 or (hh == 10 and mm > 0)) and hh < end_hour
        if bh is not None and side != 0 and active == 0 and after:
            if side == 1 and c > bh:
                active = 1; out.append((1, c, i, bh, bl, do)); continue
            if side == -1 and c < bl:
                active = -1; out.append((-1, c, i, bh, bl, do)); continue
        if flip and not flipped and active != 0 and after and bh is not None:
            if flip_cutoff is not None and hh >= flip_cutoff:
                continue
            if active == 1 and c < bl:
                active = -1; flipped = True; out.append((-1, c, i, bh, bl, do))
            elif active == -1 and c > bh:
                active = 1; flipped = True; out.append((1, c, i, bh, bl, do))
    return out


def backtest(cost=2.0, end_hour=16, stop="daily_open", exit_="trail_half",
             entry_after=None, entry_before=None, body_filter=None,
             flip=True, flip_cutoff=None, partial=False):
    # body-size percentiles, computed once over all eligible sessions
    bodies = []
    for d in DAYS:
        for s, e, i, bh, bl, do in signals(d, 16):
            bodies.append(bh - bl); break
    bodies.sort()
    med = bodies[len(bodies)//2] if bodies else 0
    p25 = bodies[len(bodies)//4] if bodies else 0
    p75 = bodies[3*len(bodies)//4] if bodies else 0

    out = []
    for day in DAYS:
        bs = day_bars[day]
        sigs = signals(day, end_hour, flip, flip_cutoff)
        for n, (s, e, idx, bh, bl, do) in enumerate(sigs):
            body = bh - bl
            if body_filter == "gt_median" and body <= med:      continue
            if body_filter == "iqr" and not (p25 <= body <= p75): continue
            tmin = bs[idx][0].hour * 60 + bs[idx][0].minute
            if entry_after is not None and tmin < entry_after:   continue
            if entry_before is not None and tmin >= entry_before: continue
            atr = ATR.get((day, idx)) or body
            if   stop == "daily_open":   sp = do
            elif stop == "daily_open+2": sp = do - s * 2
            elif stop == "body_far":     sp = bl if s > 0 else bh
            elif stop == "body_far+2":   sp = (bl - 2) if s > 0 else (bh + 2)
            elif stop == "atr0.8":       sp = e - s * atr * 0.8
            elif stop == "atr1.0":       sp = e - s * atr * 1.0
            elif stop == "atr1.2":       sp = e - s * atr * 1.2
            else:                        sp = do
            risk = abs(e - sp)
            if risk <= 0.5 or risk > 80:
                continue
            trail = None; tp = None
            if   exit_ == "trail_half": trail = body * 0.5
            elif exit_ == "trail_body": trail = body
            elif exit_ == "trail_atr1.0": trail = atr * 1.0
            elif exit_ == "trail_atr1.5": trail = atr * 1.5
            elif exit_ == "1.5R": tp = e + s * risk * 1.5
            elif exit_ == "2R":   tp = e + s * risk * 2
            elif exit_ == "2.5R": tp = e + s * risk * 2.5
            ptp = e + s * risk if partial else None
            stop_idx = sigs[n+1][2] if n+1 < len(sigs) else None
            pnl = None; peak = e; half = False; acc = 0.0; cur_stop = sp
            for j in range(idx+1, len(bs)):
                t, o, h, l, c = bs[j]
                if stop_idx is not None and j >= stop_idx:
                    pnl = acc + (0.5 if half else 1.0) * s * (bs[stop_idx][4] - e); break
                adv = l if s > 0 else h
                if s * (adv - cur_stop) <= 0:
                    pnl = acc + (0.5 if half else 1.0) * s * (cur_stop - e); break
                fav = h if s > 0 else l
                if ptp is not None and not half and s * (fav - ptp) >= 0:
                    acc += 0.5 * s * (ptp - e); half = True
                if tp is not None and s * (fav - tp) >= 0:
                    pnl = acc + (0.5 if half else 1.0) * s * (tp - e); break
                if trail is not None:
                    ts = peak - s * trail
                    if s * (ts - cur_stop) > 0:
                        cur_stop = ts
                    if s * (c - peak) > 0:
                        peak = c                      # peak advances on CLOSES only
                if t.hour >= end_hour:
                    pnl = acc + (0.5 if half else 1.0) * s * (c - e); break
            if pnl is None:
                pnl = acc + (0.5 if half else 1.0) * s * (bs[-1][4] - e)
            out.append((day, s, pnl - cost, risk))
    return out


def metrics(tr):
    if len(tr) < 30:
        return None
    p = [x[2] for x in tr]
    g = sum(v for v in p if v > 0); l = -sum(v for v in p if v <= 0)
    eq = pk = dd = 0.0
    for v in p:
        eq += v; pk = max(pk, eq); dd = max(dd, pk - eq)
    yr = defaultdict(float)
    for d, _, v, _ in tr:
        yr[d.year] += v
    m = sum(p)/len(p); sd = st.pstdev(p) or 1e-9
    return dict(n=len(p), pf=(g/l if l > 0 else 99.0), win=100*sum(1 for v in p if v > 0)/len(p),
                net=sum(p), dd=dd, mar=(sum(p)/dd if dd > 0 else 99.0),
                t=m/sd*math.sqrt(len(p)),
                yp=sum(1 for v in yr.values() if v > 0), ny=len(yr),
                avgR=sum(x[2]/x[3] for x in tr)/len(tr))


def row(lab, m, base=None):
    if not m:
        print(f"  {lab:44s}  <30 trades"); return
    flag = ""
    if base:
        flag = "  BEATS" if (m["pf"] > base["pf"] and m["t"] > base["t"] and m["mar"] > base["mar"]) else ""
    print(f"  {lab:44s} n={m['n']:4d} PF={m['pf']:6.3f} win={m['win']:5.1f}% net={m['net']:+8.1f} "
          f"DD={m['dd']:6.1f} MAR={m['mar']:6.2f} t={m['t']:+5.2f} yrs+={m['yp']}/{m['ny']}{flag}")


def monte(tr, runs=10000, seed=7):
    rng = random.Random(seed)
    p = [x[2] for x in tr]
    nets, dds = [], []
    start = 1000.0
    for _ in range(runs):
        s = [p[rng.randrange(len(p))] for _ in range(len(p))]
        eq = pk = dd = 0.0
        for v in s:
            eq += v; pk = max(pk, eq); dd = max(dd, pk - eq)
        nets.append(eq); dds.append(dd)
    nets.sort(); dds.sort()
    q = lambda arr, f: arr[int(f*(len(arr)-1))]
    tot = sum(p)
    dd15 = 0.15 * abs(tot) if tot != 0 else 1e9
    return dict(p05=q(nets,.05), p50=q(nets,.50), p95=q(nets,.95),
                dd50=q(dds,.50), dd95=q(dds,.95),
                p_profit=100*sum(1 for v in nets if v > 0)/runs,
                p_dd15=100*sum(1 for v in dds if v >= dd15)/runs)
