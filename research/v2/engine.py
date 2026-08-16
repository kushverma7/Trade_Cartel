"""AU200 research engine v2. Built from scratch after BUG-039.

DESIGN RULES (each one exists because something went wrong without it):
  R1  Every reference level is named, and its coverage is asserted at load.
      A level defined on < 95% of sessions raises. No silent fall-through.
  R2  Entries fill at the signal bar's CLOSE. The exit path starts at the NEXT
      bar. (BUG-038)
  R3  The adverse extreme is tested before the favourable one, every bar.
  R4  Stops never widen. Trails advance on CLOSES, never on the extreme that
      the same bar might trade through. (BUG-036)
  R5  A minimum stop distance is enforced. A sub-point stop is not a trade.
  R8  The stop must lie strictly on the ADVERSE side of the entry. A reference
      level on the favourable side is a target, not a stop; accepting it makes
      resolve() exit instantly at a profit and report a 100% win rate.
  R9  metrics() refuses to return a result whose win rate is >90% or <10%, or
      whose PF exceeds 20. Those are bugs until proven otherwise, and a sweep
      must not be able to rank one.
  R6  Costs are charged per trade, both legs, always.
  R7  Nothing is reported without n, date range and the fill assumption.
"""
import csv, gzip, datetime as dt, zoneinfo, math, statistics as st, random
from collections import defaultdict

UTC = dt.timezone.utc
MEL = zoneinfo.ZoneInfo("Australia/Melbourne")
U = "/home/user/Trade_Cartel/data/"   # repo copy; the uploads dir is ephemeral

OPEN_MIN, CLOSE_MIN = 600, 960          # 10:00 .. 16:00 Melbourne cash session


def _open(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def _load(path):
    by = defaultdict(list)
    for r in csv.DictReader(_open(path)):
        t = dt.datetime.strptime(r["timestamp"][:19], "%Y-%m-%d %H:%M:%S")\
              .replace(tzinfo=UTC).astimezone(MEL)
        by[t.date()].append((t.hour * 60 + t.minute, float(r["open"]), float(r["high"]),
                             float(r["low"]), float(r["close"]), float(r["volume"] or 0)))
    for d in by:
        by[d].sort()
    return by


class Data:
    def __init__(self, path=U + "au200_5m.csv.gz", tf=5):
        raw = _load(path)
        self.tf = tf
        self.bars = {}
        for d, bs in raw.items():
            cash = [b for b in bs if OPEN_MIN <= b[0] < CLOSE_MIN]
            if cash and cash[0][0] == OPEN_MIN and len(cash) >= (360 // tf) * 0.9:
                self.bars[d] = cash
        self.days = sorted(self.bars)
        # ---- reference levels, with coverage assertions (R1) ----
        self.ref = {}
        prev = None
        rng_hist = []
        for d in self.days:
            bs = self.bars[d]
            r = {}
            if prev is not None:
                p = self.bars[prev]
                r["prev_close"] = p[-1][4]
                r["prev_high"] = max(b[2] for b in p)
                r["prev_low"] = min(b[3] for b in p)
                r["prev_mid"] = (r["prev_high"] + r["prev_low"]) / 2
            r["open10"] = bs[0][1]
            r["adr"] = st.mean(rng_hist[-14:]) if len(rng_hist) >= 14 else None
            self.ref[d] = r
            rng_hist.append(max(b[2] for b in bs) - min(b[3] for b in bs))
            prev = d
        self.days = [d for d in self.days if "prev_close" in self.ref[d]
                     and self.ref[d]["adr"] is not None]
        for k in ("prev_close", "prev_high", "prev_low", "prev_mid", "open10", "adr"):
            cov = sum(1 for d in self.days if self.ref[d].get(k) is not None)
            if cov < 0.95 * len(self.days):
                raise AssertionError(f"R1 violated: level '{k}' defined on "
                                     f"{cov}/{len(self.days)} sessions")
        print(f"[engine] {path.split('/')[-1]}  tf={tf}m  sessions={len(self.days)}  "
              f"{self.days[0]} .. {self.days[-1]}")
        print(f"[engine] all reference levels defined on >=95% of sessions (R1 ok)")


# ------------------------------------------------------------------ execution
def resolve(bars, i, s, entry, stop, tp, trail, be_at, deadline, cost):
    """R2-R6. Returns (points_net, exit_reason, bars_held)."""
    peak = entry
    cur = stop
    moved_be = False
    for j in range(i + 1, len(bars)):
        mn, o, h, l, c, v = bars[j]
        adv = l if s > 0 else h
        fav = h if s > 0 else l
        if s * (adv - cur) <= 0:                                   # R3: adverse first
            return s * (cur - entry) - cost, "stop", j - i
        if tp is not None and s * (fav - tp) >= 0:
            return s * (tp - entry) - cost, "tp", j - i
        if be_at is not None and not moved_be and s * (fav - (entry + s * be_at)) >= 0:
            if s * (entry - cur) > 0:
                cur = entry                                        # R4: only tighter
            moved_be = True
        if trail is not None:
            if s * (c - peak) > 0:
                peak = c                                           # R4: closes only
            t = peak - s * trail
            if s * (t - cur) > 0:
                cur = t
        if mn >= deadline:
            return s * (c - entry) - cost, "time", j - i
    return s * (bars[-1][4] - entry) - cost, "eod", len(bars) - 1 - i


# ------------------------------------------------------------------ signals
def sig_gap(D, d, p):
    """Overnight gap vs the previous cash close, measured at the 10:00 open."""
    r = D.ref[d]
    g = r["open10"] - r["prev_close"]
    thr = p["gap_thr"] * (r["adr"] if p["gap_rel"] else 1.0)
    if abs(g) < thr:
        return []
    s = (1 if g > 0 else -1) * (1 if p["mode"] == "cont" else -1)
    i = p["delay"] // D.tf
    if i >= len(D.bars[d]):
        return []
    return [(s, i, {"ref": r["prev_close"]})]


def sig_orb(D, d, p):
    """Opening-range break or fade, range built over the first `or_min` minutes."""
    bs = D.bars[d]
    k = p["or_min"] // D.tf
    if k >= len(bs):
        return []
    hi = max(b[2] for b in bs[:k])
    lo = min(b[3] for b in bs[:k])
    if hi - lo < p["or_floor"]:
        return []
    for j in range(k, len(bs)):
        if bs[j][0] >= p["cutoff"]:
            break
        c = bs[j][4]
        if c > hi:
            return [((1 if p["mode"] == "cont" else -1), j, {"ref": lo if p["mode"] == "cont" else hi,
                                                             "hi": hi, "lo": lo})]
        if c < lo:
            return [((-1 if p["mode"] == "cont" else 1), j, {"ref": hi if p["mode"] == "cont" else lo,
                                                             "hi": hi, "lo": lo})]
    return []


def sig_body(D, d, p):
    """The original 10 AM Body Break, re-anchored to the previous cash close."""
    bs, r = D.bars[d], D.ref[d]
    ref = r["prev_close"]
    b = bs[0]
    bh, bl = max(b[1], b[4]), min(b[1], b[4])
    side = -1 if bh < ref else (1 if bl > ref else 0)
    if side == 0:
        return []
    for j in range(1, len(bs)):
        if bs[j][0] >= p["cutoff"]:
            break
        c = bs[j][4]
        if side == 1 and c > bh:
            return [(1, j, {"ref": ref, "hi": bh, "lo": bl})]
        if side == -1 and c < bl:
            return [(-1, j, {"ref": ref, "hi": bh, "lo": bl})]
    return []


def sig_pdhl(D, d, p):
    """Break or fade of the previous cash session's high / low."""
    bs, r = D.bars[d], D.ref[d]
    for j in range(len(bs)):
        if bs[j][0] >= p["cutoff"]:
            break
        c = bs[j][4]
        if c > r["prev_high"]:
            return [((1 if p["mode"] == "cont" else -1), j, {"ref": r["prev_high"]})]
        if c < r["prev_low"]:
            return [((-1 if p["mode"] == "cont" else 1), j, {"ref": r["prev_low"]})]
    return []


SIGNALS = {"gap": sig_gap, "orb": sig_orb, "body": sig_body, "pdhl": sig_pdhl}


# ------------------------------------------------------------------ backtest
def backtest(D, p, days=None):
    fn = SIGNALS[p["sig"]]
    out = []
    for d in (days if days is not None else D.days):
        bs = D.bars[d]
        r = D.ref[d]
        for s, i, lv in fn(D, d, p):
            e = bs[i][4]
            adr = r["adr"]
            k = p["stop"]
            if k == "ref":            sp = lv["ref"]
            elif k == "adr0.25":      sp = e - s * adr * 0.25
            elif k == "adr0.5":       sp = e - s * adr * 0.5
            elif k == "adr0.75":      sp = e - s * adr * 0.75
            elif k == "fixed10":      sp = e - s * 10
            elif k == "fixed20":      sp = e - s * 20
            elif k == "fixed30":      sp = e - s * 30
            elif k == "or":           sp = lv.get("lo" if s > 0 else "hi", lv["ref"])
            else:                     raise ValueError(k)
            if s * (e - sp) <= 0:                                  # R8
                continue
            risk = abs(e - sp)
            if risk < p["min_risk"] or risk > p["max_risk"]:       # R5
                continue
            x = p["exit"]
            tp = trail = None
            if   x == "1R":   tp = e + s * risk
            elif x == "1.5R": tp = e + s * risk * 1.5
            elif x == "2R":   tp = e + s * risk * 2
            elif x == "3R":   tp = e + s * risk * 3
            elif x == "adr0.5": tp = e + s * adr * 0.5
            elif x == "adr1.0": tp = e + s * adr * 1.0
            elif x == "trail_adr0.3": trail = adr * 0.3
            elif x == "trail_adr0.5": trail = adr * 0.5
            elif x == "time": pass
            else: raise ValueError(x)
            pnl, why, held = resolve(bs, i, s, e, sp, tp, trail,
                                     p.get("be"), p["deadline"], p["cost"])
            out.append(dict(day=d, s=s, pnl=pnl, risk=risk, why=why, held=held, entry=bs[i][0]))
    return out


def metrics(tr, min_n=40, strict=True):
    if len(tr) < min_n:
        return None
    p = [t["pnl"] for t in tr]
    win = 100 * sum(1 for v in p if v > 0) / len(p)
    if strict and (win > 90.0 or win < 10.0):                      # R9
        return None
    g = sum(v for v in p if v > 0); l = -sum(v for v in p if v <= 0)
    eq = pk = dd = 0.0
    for v in p:
        eq += v; pk = max(pk, eq); dd = max(dd, pk - eq)
    yr = defaultdict(float)
    for t in tr:
        yr[t["day"].year] += t["pnl"]
    m = sum(p) / len(p); sd = st.pstdev(p) or 1e-9
    pf = g / l if l > 0 else 99.0
    if strict and pf > 20.0:                                       # R9
        return None
    return dict(n=len(p), pf=pf, win=win,
                net=sum(p), avg=m, dd=dd, t=m / sd * math.sqrt(len(p)),
                mar=(sum(p) / dd if dd > 0 else 99.0),
                yp=sum(1 for v in yr.values() if v > 0), ny=len(yr),
                avgR=sum(t["pnl"] / t["risk"] for t in tr) / len(tr))
