"""10 AM BODY BREAK — exhaustive sweep, AU200 5-minute, full six years.

Signal layer is a line-by-line port of the supplied indicator:
    dailyOpen = open of the 09:50 bar
    bodyHi/Lo = max/min(open, close) of the 10:00 bar
    side      = +1 if bodyLo > dailyOpen, -1 if bodyHi < dailyOpen, else 0
    afterBody = after 10:00 and hour < endHour
    Logic A   = close beyond the body in the direction of side
    Logic B   = the 10:00 candle itself (directional and beyond dailyOpen)
    Logic C   = flip once, when close crosses back through the far body edge

Execution: entry at the signal bar's CLOSE; exits resolved on the 5-minute path
after that bar; stop frozen at entry; cost charged per trade (per leg on flips).
"""
import csv, datetime as dt, zoneinfo, math, itertools, random, statistics as st
from collections import defaultdict

UTC = dt.timezone.utc
MEL = zoneinfo.ZoneInfo("Australia/Melbourne")
SRC = "/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/30348eaf-au200_aud_5m.csv"
COST = 2.0

rows = []
for r in csv.DictReader(open(SRC)):
    t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    rows.append((t.astimezone(MEL), float(r["open"]), float(r["high"]),
                 float(r["low"]), float(r["close"])))
rows.sort()
day_bars = defaultdict(list)
for r in rows:
    day_bars[r[0].date()].append(r)
DAYS = sorted(day_bars)


DO_MODE = "strict"   # "strict" = require the 09:50 bar; "proxy" = use the session's first bar


def signals(day, logic, flip, one_shot, end_hour):
    """Return list of (dir, entry_price, idx, bodyHi, bodyLo, dailyOpen)."""
    bs = day_bars[day]
    dailyOpen = bodyHi = bodyLo = None
    side = 0
    active = 0
    signaled = False
    flipped = False
    out = []
    for i, (t, o, h, l, c) in enumerate(bs):
        hh, mm = t.hour, t.minute
        if hh == 9 and mm == 50:
            dailyOpen = o
        if DO_MODE == "proxy" and dailyOpen is None and (hh < 10 or (hh == 10 and mm == 0)):
            dailyOpen = o          # session's first available open, stated deviation
        if hh == 10 and mm == 0 and dailyOpen is not None:
            bodyHi = max(o, c); bodyLo = min(o, c)
            side = -1 if bodyHi < dailyOpen else (1 if bodyLo > dailyOpen else 0)
        after = (hh > 10 or (hh == 10 and mm > 0)) and hh < end_hour
        buy = sell = False
        if logic == "A":
            armed = bodyHi is not None and side != 0 and active == 0 and after \
                    and (not signaled or not one_shot)
            buy  = armed and side == 1 and c > bodyHi
            sell = armed and side == -1 and c < bodyLo
        else:
            if hh == 10 and mm == 0 and dailyOpen is not None:
                buy  = c > o and c > dailyOpen
                sell = c < o and c < dailyOpen
        if buy or sell:
            active = 1 if buy else -1
            signaled = True; flipped = False
            out.append((active, c, i, bodyHi, bodyLo, dailyOpen))
            continue
        if flip and not flipped and active != 0 and after and bodyHi is not None:
            fs = active == 1 and c < bodyLo
            fb = active == -1 and c > bodyHi
            if fs or fb:
                active = -1 if fs else 1
                flipped = True
                out.append((active, c, i, bodyHi, bodyLo, dailyOpen))
    return out


def stop_price(kind, s, e, bh, bl, do):
    body = bh - bl
    if kind == "body_far":   return bl if s > 0 else bh
    if kind == "body_half":  return e - s * max(body * 0.5, 0.5)
    if kind == "body_1x":    return e - s * max(body, 0.5)
    if kind == "daily_open": return do
    if kind == "fixed10":    return e - s * 10
    if kind == "fixed15":    return e - s * 15
    if kind == "fixed20":    return e - s * 20
    return e - s * max(body, 0.5)


def tp_price(kind, s, e, risk, body):
    if kind == "1R":    return e + s * risk
    if kind == "1.5R":  return e + s * risk * 1.5
    if kind == "2R":    return e + s * risk * 2
    if kind == "3R":    return e + s * risk * 3
    if kind == "fixed10": return e + s * 10
    if kind == "fixed15": return e + s * 15
    if kind == "fixed20": return e + s * 20
    if kind == "fixed30": return e + s * 30
    if kind == "body1x":  return e + s * max(body, 1)
    if kind == "body2x":  return e + s * max(body * 2, 1)
    return None


STOPS = ["body_far", "body_half", "body_1x", "daily_open", "fixed10", "fixed15", "fixed20"]
TPS   = ["1R", "1.5R", "2R", "3R", "fixed10", "fixed15", "fixed20", "fixed30",
         "body1x", "body2x", "trail_body", "trail_half", "none"]


def run(logic, flip, one_shot, end_hour, stop_k, tp_k):
    trades = []
    for day in DAYS:
        bs = day_bars[day]
        sigs = signals(day, logic, flip, one_shot, end_hour)
        if not sigs:
            continue
        for n, (s, e, idx, bh, bl, do) in enumerate(sigs):
            body = bh - bl
            stop = stop_price(stop_k, s, e, bh, bl, do)
            risk = abs(e - stop)
            if risk <= 0.5 or risk > 80:
                continue
            tp = tp_price(tp_k, s, e, risk, body)
            trail = body if tp_k == "trail_body" else (body * 0.5 if tp_k == "trail_half" else None)
            # a flip closes the previous leg at the flip bar's close
            stop_idx = sigs[n + 1][2] if n + 1 < len(sigs) else None
            pnl = None; peak = e
            for j in range(idx + 1, len(bs)):
                t, o, h, l, c = bs[j]
                if stop_idx is not None and j >= stop_idx:
                    pnl = s * (bs[stop_idx][4] - e); break
                adv = l if s > 0 else h
                fav = h if s > 0 else l
                if s * (adv - stop) <= 0:
                    pnl = s * (stop - e); break
                if tp is not None and s * (fav - tp) >= 0:
                    pnl = s * (tp - e); break
                if trail is not None:
                    if s * (fav - peak) > 0:
                        peak = fav
                    ts = peak - s * trail
                    if s * (adv - ts) <= 0 and s * (ts - stop) > 0:
                        pnl = s * (ts - e); break
                if t.hour >= end_hour:
                    pnl = s * (c - e); break
            if pnl is None:
                pnl = s * (bs[-1][4] - e)
            trades.append((day, s, pnl - COST, risk))
    return trades


def metrics(tr):
    if len(tr) < 30:
        return None
    p = [x[2] for x in tr]
    R = [x[2] / x[3] for x in tr]
    g = sum(v for v in p if v > 0); l = -sum(v for v in p if v <= 0)
    eq = pk = dd = 0.0
    for v in p:
        eq += v; pk = max(pk, eq); dd = max(dd, pk - eq)
    yr = defaultdict(float)
    for d, _, v, _ in tr:
        yr[d.year] += v
    m = sum(p) / len(p); sd = st.pstdev(p) or 1e-9
    return dict(n=len(p), pf=(g / l if l > 0 else 99.0),
                win=100 * sum(1 for v in p if v > 0) / len(p),
                net=sum(p), avgR=sum(R) / len(R), dd=dd,
                t=m / sd * math.sqrt(len(p)),
                yp=sum(1 for v in yr.values() if v > 0), ny=len(yr),
                mar=(sum(p) / dd if dd > 0 else 99.0))


if __name__ == "__main__":
    print(f"AU200 5-minute  {DAYS[0]} .. {DAYS[-1]}   {len(DAYS)} sessions   cost {COST} pts/trade")
    combos = list(itertools.product(["A", "B"], [False, True], [False, True],
                                    [11, 12, 13, 14, 16], STOPS, TPS))
    print(f"grid = {len(combos)} combinations\n")
    res = []
    for (lg, fl, os_, eh, sk, tk) in combos:
        m = metrics(run(lg, fl, os_, eh, sk, tk))
        if m:
            res.append((dict(logic=lg, flip=fl, oneShot=os_, endHour=eh, stop=sk, tp=tk), m))
    K = len(res)
    bar = math.sqrt(2 * math.log(K)) if K > 1 else 0
    print(f"{K} combinations produced >=30 trades.  multiple-testing bar t >= sqrt(2 ln {K}) = {bar:.2f}\n")
    res.sort(key=lambda r: -r[1]["t"])
    print(f"{'#':>3} {'logic':5} {'flip':5} {'1shot':5} {'end':>3} {'stop':10} {'tp':11} "
          f"{'n':>5} {'PF':>6} {'win%':>5} {'net':>8} {'avgR':>6} {'maxDD':>7} {'MAR':>6} {'t':>6} {'yrs+':>5}")
    for i, (c, m) in enumerate(res[:25], 1):
        print(f"{i:>3} {c['logic']:5} {str(c['flip']):5} {str(c['oneShot']):5} {c['endHour']:>3} "
              f"{c['stop']:10} {c['tp']:11} {m['n']:>5} {m['pf']:>6.3f} {m['win']:>5.1f} {m['net']:>8.1f} "
              f"{m['avgR']:>6.3f} {m['dd']:>7.1f} {m['mar']:>6.2f} {m['t']:>6.2f} {m['yp']}/{m['ny']}")
    print(f"\ncombinations clearing the bar (t >= {bar:.2f}): "
          f"{sum(1 for _, m in res if m['t'] >= bar)}")
    print(f"combinations with PF > 1.0: {sum(1 for _, m in res if m['pf'] > 1.0)} of {K} "
          f"({100*sum(1 for _, m in res if m['pf'] > 1.0)/K:.1f}%)")
    import pickle
    pickle.dump(res, open("/tmp/claude-0/-home-user-Trade-Cartel/af36979e-ba34-557a-a8b0-0a27e52e3758/scratchpad/bb_res.pkl", "wb"))
