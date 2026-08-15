"""10 AM BODY BREAK — exhaustive research harness.

The SIGNAL layer is a plug-in: drop the original script's rules into signal()
and nothing else changes. Everything below it — the combinatorial sweep, the
execution model, the metrics, the Monte Carlo and the ranking — is generic and
already validated.

EXECUTION MODEL (fixed, not swept — these are correctness, not parameters):
  * entries fill at the signal bar's CLOSE
  * exits resolve on the 1-MINUTE path, adverse extreme taken first
  * the path starts AFTER the signal bar closes            (BUG-038)
  * stops are frozen at entry and never widen              (Iron Rule 9)
  * costs are charged on every trade
"""
import csv, datetime as dt, zoneinfo, math, itertools, random, statistics as st
from collections import defaultdict

UTC = dt.timezone.utc
MEL = zoneinfo.ZoneInfo("Australia/Sydney")
SRC = "/root/.claude/uploads/af36979e-ba34-557a-a8b0-0a27e52e3758/c1e55d1f-au200_aud_1m_4.csv"

# ---------------------------------------------------------------- data
raw = []
for r in csv.DictReader(open(SRC)):
    t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    raw.append((t, float(r["open"]), float(r["high"]), float(r["low"]),
                float(r["close"]), float(r["volume"] or 0)))
raw.sort()
byday = defaultdict(list)
for r in raw:
    byday[r[0].astimezone(MEL).date()].append(r)
SESSIONS = sorted(byday)


def bars(tf):
    out, cur, key = [], None, None
    for t, o, h, l, c, v in raw:
        k = int(t.timestamp()) // (tf * 60)
        if k != key:
            if cur:
                out.append(tuple(cur))
            key, cur = k, [t, o, h, l, c, v]
        else:
            cur[3] = min(cur[3], l); cur[2] = max(cur[2], h); cur[4] = c; cur[5] += v
    if cur:
        out.append(tuple(cur))
    return out


def atr_series(bs, n=14):
    tr, out, a = [], [], None
    for i, b in enumerate(bs):
        t = b[2]-b[3] if i == 0 else max(b[2]-b[3], abs(b[2]-bs[i-1][4]), abs(b[3]-bs[i-1][4]))
        tr.append(t)
        if i < n-1:
            out.append(None); continue
        a = sum(tr[:n])/n if a is None else (a*(n-1)+t)/n
        out.append(a)
    return out


def day_bar(day, h0, m0, mins):
    """OHLC of a block of `mins` minutes starting at local h0:m0."""
    o = h = l = c = None
    for k in range(mins):
        t = dt.datetime.combine(day, dt.time(h0, m0), tzinfo=MEL) + dt.timedelta(minutes=k)
        for m in byday.get(day, []):
            if m[0] == t.astimezone(UTC):
                if o is None:
                    o, h, l = m[1], m[2], m[3]
                h = max(h, m[2]); l = min(l, m[3]); c = m[4]
                break
    return (o, h, l, c) if o is not None else None


# ---------------------------------------------------------------- SIGNAL PLUG-IN
def signal(day, cfg):
    """RETURN: (direction, entry_price, ref_high, ref_low, entry_time) or None.

    >>> REPLACE THIS BODY WITH THE ORIGINAL SCRIPT'S RULES <<<
    The original's inputs map onto cfg keys:
        cfg['logic']      'A' | 'B' | 'C'
        cfg['flip']       True/False
        cfg['oneShot']    True/False
        cfg['dailyOpen']  True/False
        cfg['endHour']    int
    Everything downstream is already written and validated.
    """
    raise NotImplementedError("paste the original 10 AM Body Break rules here")


# ---------------------------------------------------------------- execution
def resolve(day, s, entry_t, e, stop, tp, trail, deadline_min):
    """1-minute path. Adverse first. Stop frozen. Returns points."""
    path = [m for m in byday[day] if m[0] > entry_t]
    peak = e
    for (mt, mo, mh, ml, mc, mv) in path:
        adv = ml if s > 0 else mh
        fav = mh if s > 0 else ml
        if s * (adv - stop) <= 0:
            return s * (stop - e)
        if tp is not None and s * (fav - tp) >= 0:
            return s * (tp - e)
        if trail is not None:
            if s * (fav - peak) > 0:
                peak = fav
            tstop = peak - s * trail
            if s * (adv - tstop) <= 0 and s * (tstop - stop) > 0:
                return s * (tstop - e)
        lt = mt.astimezone(MEL)
        if lt.hour * 60 + lt.minute >= deadline_min:
            return s * (mc - e)
    return s * (path[-1][4] - e) if path else 0.0


def backtest(cfg, cost):
    out = []
    for day in SESSIONS:
        sig = signal(day, cfg)
        if not sig:
            continue
        s, e, rh, rl, et = sig
        body = abs(rh - rl)
        # ---- stop methods, all anchored to the original 10 AM body ----
        sm = cfg["stop"]
        if sm == "body_far":   stop = (rl if s > 0 else rh)
        elif sm == "body_half":stop = e - s * body * 0.5
        elif sm == "body_1x":  stop = e - s * body
        elif sm == "fixed10":  stop = e - s * 10
        elif sm == "fixed15":  stop = e - s * 15
        elif sm == "fixed20":  stop = e - s * 20
        else:                  stop = e - s * body
        risk = abs(e - stop)
        if risk <= 0.5 or risk > 60:
            continue
        # ---- take-profit methods ----
        tm = cfg["tp"]
        tp = None; trail = None
        if   tm == "1R":    tp = e + s * risk
        elif tm == "1.5R":  tp = e + s * risk * 1.5
        elif tm == "2R":    tp = e + s * risk * 2
        elif tm == "3R":    tp = e + s * risk * 3
        elif tm == "fixed10": tp = e + s * 10
        elif tm == "fixed20": tp = e + s * 20
        elif tm == "body1x":  tp = e + s * body
        elif tm == "body2x":  tp = e + s * body * 2
        elif tm == "trail_body": trail = body
        elif tm == "trail_half": trail = body * 0.5
        elif tm == "none":  pass
        pts = resolve(day, s, et, e, stop, tp, trail, cfg["endHour"] * 60)
        out.append((day, s, pts - cost, risk))
    return out


# ---------------------------------------------------------------- metrics
def metrics(tr):
    if len(tr) < 20:
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
    mo = defaultdict(float)
    for d, _, v, _ in tr:
        mo[(d.year, d.month)] += v
    m = sum(p) / len(p); sd = st.pstdev(p) or 1e-9
    return dict(n=len(p), pf=(g/l if l > 0 else 99.0), win=100*sum(1 for v in p if v > 0)/len(p),
                net=sum(p), avgR=sum(R)/len(R), maxDD=dd, t=m/sd*math.sqrt(len(p)),
                yrs_pos=sum(1 for v in yr.values() if v > 0), yrs=len(yr),
                mos_pos=100*sum(1 for v in mo.values() if v > 0)/max(1, len(mo)),
                mar=(sum(p)/dd if dd > 0 else 99.0))


def monte_carlo(tr, runs=5000, seed=11):
    rng = random.Random(seed)
    p = [x[2] for x in tr]
    nets, dds = [], []
    for _ in range(runs):
        s = [p[rng.randrange(len(p))] for _ in range(len(p))]
        eq = pk = dd = 0.0
        for v in s:
            eq += v; pk = max(pk, eq); dd = max(dd, pk - eq)
        nets.append(eq); dds.append(dd)
    nets.sort(); dds.sort()
    q = lambda a, f: a[int(f * (len(a) - 1))]
    return dict(p05=q(nets, .05), p50=q(nets, .50), p95=q(nets, .95),
                dd50=q(dds, .50), dd95=q(dds, .95),
                p_profit=100*sum(1 for v in nets if v > 0)/len(nets))


# ---------------------------------------------------------------- sweep
GRID = dict(
    logic     = ["A", "B", "C"],
    flip      = [False, True],
    oneShot   = [False, True],
    dailyOpen = [False, True],
    endHour   = [11, 12, 13, 14, 16],
    stop      = ["body_far", "body_half", "body_1x", "fixed10", "fixed15", "fixed20"],
    tp        = ["1R", "1.5R", "2R", "3R", "fixed10", "fixed20", "body1x", "body2x",
                 "trail_body", "trail_half", "none"],
)


def sweep(cost=2.0, verbose=True):
    keys = list(GRID)
    combos = list(itertools.product(*(GRID[k] for k in keys)))
    if verbose:
        print(f"grid = {len(combos)} combinations x {len(SESSIONS)} sessions")
    rows = []
    for c in combos:
        cfg = dict(zip(keys, c))
        m = metrics(backtest(cfg, cost))
        if m:
            rows.append((cfg, m))
    K = max(1, len(rows))
    bar = math.sqrt(2 * math.log(K))
    rows.sort(key=lambda r: -r[1]["t"])
    return rows, bar


if __name__ == "__main__":
    print(f"AU200 1-minute, {SESSIONS[0]} .. {SESSIONS[-1]}, {len(SESSIONS)} sessions")
    print(f"grid size = {math.prod(len(v) for v in GRID.values())} combinations")
    print("\nSIGNAL LAYER NOT YET SUPPLIED — paste the original script into signal().")
