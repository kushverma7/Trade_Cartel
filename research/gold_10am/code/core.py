"""Core library for the Gold 10AM study: loading, Melbourne conversion,
5-minute construction, setup detection, the four logics, and 1-minute path
resolution.

TIME RULE (BUG-037 avoidance): every conversion goes through
zoneinfo.ZoneInfo("Australia/Melbourne") per timestamp. No fixed offset, no
`+10`, no `+11`, anywhere in this file. AEST/AEDT is decided by the tz
database for the actual historical date.

LEVEL RULE (BUG-039 avoidance): dOpen is the open of the Melbourne 09:50
5-minute bucket and nothing else. It is never a "daily open", never a proxy,
never resolved by name. If the 09:50 bucket does not exist, the day has NO
setup and is recorded as missing, not substituted.

STOP RULE (BUG-040 avoidance): a stop must be strictly adverse to the entry.
Any trade whose stop is on the favourable side is refused, loudly.
"""
import os, csv, gzip, datetime as dt
from zoneinfo import ZoneInfo

MEL = ZoneInfo("Australia/Melbourne")
UTC = dt.timezone.utc
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
PROC = os.path.join(HERE, "..", "data", "processed")

REF_MIN = 9 * 60 + 50      # 09:50 Melbourne
BODY_MIN = 10 * 60         # 10:00 Melbourne


# ----------------------------------------------------------------- loading
def load_1m(path):
    """-> list of (utc_datetime, o, h, l, c, v), ascending, deduplicated."""
    out, seen = [], set()
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", newline="") as f:
        for row in csv.DictReader(f):
            t = dt.datetime.fromisoformat(row["timestamp"])
            if t.tzinfo is None:
                t = t.replace(tzinfo=UTC)
            t = t.astimezone(UTC)
            if t in seen:
                continue
            seen.add(t)
            out.append((t, float(row["open"]), float(row["high"]),
                        float(row["low"]), float(row["close"]),
                        float(row.get("volume") or 0)))
    out.sort(key=lambda r: r[0])
    return out


def to_melbourne(rows):
    """Attach Melbourne local time. -> list of dicts with utc/local/date/minute."""
    out = []
    for t, o, h, l, c, v in rows:
        lt = t.astimezone(MEL)
        out.append(dict(utc=t, local=lt, date=lt.date(),
                        minute=lt.hour * 60 + lt.minute,
                        open=o, high=h, low=l, close=c, volume=v,
                        dst=bool(lt.dst())))
    return out


# ------------------------------------------------------- 5-minute buckets
def build_5m(mrows):
    """Melbourne-aligned 5-minute candles. A bucket is emitted only if at least
    one constituent minute exists, and records how many of its five minutes
    were actually present (`n_min`). Nothing is forward-filled."""
    b = {}
    for r in mrows:
        key = (r["date"], r["minute"] // 5 * 5)
        cur = b.get(key)
        if cur is None:
            b[key] = dict(date=key[0], minute=key[1], open=r["open"], high=r["high"],
                          low=r["low"], close=r["close"], volume=r["volume"],
                          n_min=1, dst=r["dst"], first_utc=r["utc"], last_utc=r["utc"])
        else:
            cur["high"] = max(cur["high"], r["high"])
            cur["low"] = min(cur["low"], r["low"])
            cur["close"] = r["close"]
            cur["volume"] += r["volume"]
            cur["n_min"] += 1
            cur["last_utc"] = r["utc"]
    return [b[k] for k in sorted(b)]


def by_day(bars5):
    d = {}
    for x in bars5:
        d.setdefault(x["date"], []).append(x)
    for k in d:
        d[k].sort(key=lambda x: x["minute"])
    return d


def minutes_by_day(mrows):
    d = {}
    for r in mrows:
        d.setdefault(r["date"], []).append(r)
    for k in d:
        d[k].sort(key=lambda x: x["minute"])
    return d


# ------------------------------------------------------------ the setup
def setup(day_bars):
    """-> dict or None. Implements the brief exactly:
       dOpen = open of the 09:50 5m bucket
       bHi/bLo = max/min(open, close) of the 10:00 5m bucket
       side  = close(10:00) > dOpen ? +1 : -1
    """
    ref = next((b for b in day_bars if b["minute"] == REF_MIN), None)
    body = next((b for b in day_bars if b["minute"] == BODY_MIN), None)
    if ref is None or body is None:
        return None
    d_open = ref["open"]
    b_hi = max(body["open"], body["close"])
    b_lo = min(body["open"], body["close"])
    return dict(date=day_bars[0]["date"], d_open=d_open, b_hi=b_hi, b_lo=b_lo,
                side=1 if body["close"] > d_open else -1,
                body=body, ref=ref, dst=body["dst"])


# ------------------------------------------------------------ the logics
# A_SHORT : side -1, later 5m close < bLo AND < dOpen        -> short
# A_LONG  : side +1, later 5m close > bHi AND > dOpen        -> long   (control)
# FLIP_L  : side -1, later 5m close > bHi AND > dOpen        -> long
# FLIP_S  : side +1, later 5m close < bLo AND < dOpen        -> short
LOGICS = ("A_SHORT", "A_LONG", "FLIP_L", "FLIP_S")
DIRECTION = {"A_SHORT": -1, "A_LONG": 1, "FLIP_L": 1, "FLIP_S": -1}


def triggers(su, day_bars, last_minute=None):
    """All logic triggers for one day, in chronological order.
    Signal bars are strictly AFTER the 10:00 body bar. Entry is the signal
    bar's CLOSE (process_orders_on_close=true).
    Returns list of dicts: logic, minute, entry, bar."""
    out = []
    for b in day_bars:
        if b["minute"] <= BODY_MIN:
            continue
        if last_minute is not None and b["minute"] > last_minute:
            break
        c = b["close"]
        up = c > su["b_hi"] and c > su["d_open"]
        dn = c < su["b_lo"] and c < su["d_open"]
        if su["side"] == -1:
            if dn:
                out.append(dict(logic="A_SHORT", minute=b["minute"], entry=c, bar=b))
            if up:
                out.append(dict(logic="FLIP_L", minute=b["minute"], entry=c, bar=b))
        else:
            if up:
                out.append(dict(logic="A_LONG", minute=b["minute"], entry=c, bar=b))
            if dn:
                out.append(dict(logic="FLIP_S", minute=b["minute"], entry=c, bar=b))
    return out


def first_trigger(su, day_bars, logics, last_minute=None):
    """Daily state machine: no pyramiding, enter only while flat, each logic
    may fire at most once per day. Because a position is held until its own
    exit, the base convention is ONE trade per day per enabled logic set:
    the first trigger among `logics` wins; later triggers of the SAME logic
    are ignored; a trigger of a DIFFERENT enabled logic is taken only after
    the first trade has closed (the caller supplies that via `exit_minute`).
    For single-logic studies this is simply 'first trigger of the day'."""
    for t in triggers(su, day_bars, last_minute):
        if t["logic"] in logics:
            return t
    return None


# ------------------------------------------------- 1-minute path resolution
def path_after(day_minutes, from_minute):
    """1-minute bars strictly after the signal bar's close.
    The signal bar closes at (from_minute + 5); the path therefore starts at
    the first minute >= from_minute + 5. No lookahead into the signal bar."""
    start = from_minute + 5
    return [m for m in day_minutes if m["minute"] >= start]


def resolve(entry, side, sl_dist, tp_dist, path, eod_minute=None):
    """Walk the 1-minute path. Returns a dict with the outcome, MAE, MFE, and
    an explicit ambiguity flag when stop and target fall inside the SAME
    1-minute bar (ordering unknowable at this resolution).

    side +1 long, -1 short. sl_dist/tp_dist are POSITIVE dollar distances.
    R4: the stop never widens. R8: the stop is strictly adverse.
    """
    if sl_dist <= 0 or tp_dist <= 0:
        raise ValueError("R8: sl and tp distances must be positive")
    stop = entry - side * sl_dist
    targ = entry + side * tp_dist
    mae = 0.0; mfe = 0.0; t_mae = None; t_mfe = None
    for k, m in enumerate(path):
        if eod_minute is not None and m["minute"] > eod_minute:
            break
        # adverse/favourable excursion in dollars, measured from entry
        adv = (entry - m["low"]) if side > 0 else (m["high"] - entry)
        fav = (m["high"] - entry) if side > 0 else (entry - m["low"])
        if adv > mae:
            mae, t_mae = adv, k + 1
        if fav > mfe:
            mfe, t_mfe = fav, k + 1
        hit_sl = (m["low"] <= stop) if side > 0 else (m["high"] >= stop)
        hit_tp = (m["high"] >= targ) if side > 0 else (m["low"] <= targ)
        if hit_sl and hit_tp:
            return dict(outcome="ambiguous", pnl_pess=-sl_dist, pnl_opt=tp_dist,
                        bars=k + 1, mae=mae, mfe=mfe, t_mae=t_mae, t_mfe=t_mfe,
                        exit_minute=m["minute"])
        if hit_sl:
            return dict(outcome="stop", pnl_pess=-sl_dist, pnl_opt=-sl_dist,
                        bars=k + 1, mae=mae, mfe=mfe, t_mae=t_mae, t_mfe=t_mfe,
                        exit_minute=m["minute"])
        if hit_tp:
            return dict(outcome="target", pnl_pess=tp_dist, pnl_opt=tp_dist,
                        bars=k + 1, mae=mae, mfe=mfe, t_mae=t_mae, t_mfe=t_mfe,
                        exit_minute=m["minute"])
    if not path:
        return dict(outcome="nopath", pnl_pess=0.0, pnl_opt=0.0, bars=0,
                    mae=0.0, mfe=0.0, t_mae=None, t_mfe=None, exit_minute=None)
    last = path[-1]["close"]
    pnl = (last - entry) * side
    return dict(outcome="eod", pnl_pess=pnl, pnl_opt=pnl, bars=len(path),
                mae=mae, mfe=mfe, t_mae=t_mae, t_mfe=t_mfe,
                exit_minute=path[-1]["minute"])


def first_passage(entry, side, x, path, eod_minute=None):
    """Which symmetric barrier +/-x is touched FIRST. -> ('fav'|'adv'|'amb'|'none', minutes)"""
    up = entry + x; dn = entry - x
    for k, m in enumerate(path):
        if eod_minute is not None and m["minute"] > eod_minute:
            break
        hu = m["high"] >= up
        hd = m["low"] <= dn
        if hu and hd:
            return ("amb", k + 1)
        if hu:
            return ("fav" if side > 0 else "adv", k + 1)
        if hd:
            return ("adv" if side > 0 else "fav", k + 1)
    return ("none", None)


# --------------------------------------------------------------- metrics
def metrics(pnls, absurd_check=True):
    n = len(pnls)
    if n == 0:
        return dict(n=0)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    be = [p for p in pnls if p == 0]
    gw = sum(wins); gl = -sum(losses)
    eq = 0.0; peak = 0.0; dd = 0.0
    for p in pnls:
        eq += p; peak = max(peak, eq); dd = max(dd, peak - eq)
    m = dict(n=n, wins=len(wins), losses=len(losses), be=len(be),
             win_pct=100.0 * len(wins) / n,
             gross_win=gw, gross_loss=gl, net=sum(pnls),
             avg=sum(pnls) / n,
             avg_win=(gw / len(wins)) if wins else 0.0,
             avg_loss=(-gl / len(losses)) if losses else 0.0,
             best=max(pnls), worst=min(pnls),
             pf=(gw / gl) if gl > 0 else float("inf"),
             max_dd=dd)
    m["payoff"] = (m["avg_win"] / abs(m["avg_loss"])) if m["avg_loss"] else float("inf")
    m["expectancy"] = m["avg"]
    m["recovery"] = (m["net"] / dd) if dd > 0 else float("inf")
    if absurd_check and n >= 30:
        # R9 absurdity assertion — a tripped flag is a bug until proven otherwise
        m["absurd"] = (m["win_pct"] > 90 or m["win_pct"] < 10
                       or (m["pf"] != float("inf") and m["pf"] > 20))
    else:
        m["absurd"] = False
    return m
