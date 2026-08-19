"""AU200 Phase 1 — original strategy, unmodified. Dukascopy E_XJO-ASX 5m.

CONVENTIONS, stated so nothing is ambiguous:
  DAILY_OPEN   = open of the exact 09:50 Melbourne 5-minute candle.
  BODY_HIGH/LOW= max/min(open, close) of the exact 10:00 candle. Wicks unused.
  Logic A      = first completed close beyond the body, checked from 10:05.
  ENTRY CUTOFF = a signal is accepted on candles up to and including 15:50.
                 A 15:55 signal is rejected because the mandatory 15:55 exit
                 would close it at its own close, producing a degenerate
                 zero-point trade. Documented, not silent.
  SESSION EXIT = the 15:55 candle CLOSE. Mandatory. Nothing carries past it.
  MFE/MAE      = always measured from entry to the 15:55 close, regardless of
                 which exit model is being tested (per spec).
  POINTS       = 1 AU200 point = 1.0 index-price movement.
"""
import csv, gzip, math, random, datetime as dt, statistics as st
from zoneinfo import ZoneInfo
from collections import defaultdict, Counter

UTC = dt.timezone.utc
MEL = ZoneInfo("Australia/Melbourne")
REF, BODY, LAST_ENTRY, SESS_EXIT = 590, 600, 950, 955
SRC = "data/au200_duka_5m.csv.gz"


def load(path=SRC):
    days = defaultdict(dict)
    for r in csv.DictReader(gzip.open(path, "rt")):
        t = dt.datetime.fromisoformat(r["timestamp"]).astimezone(MEL)
        days[t.date()][t.hour * 60 + t.minute] = (
            float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
    return days


def setup(D):
    """Returns (daily_open, body_hi, body_lo, side) or None if untestable."""
    if REF not in D or BODY not in D:
        return None
    do = D[REF][0]
    o, _, _, c = D[BODY]
    bh, bl = max(o, c), min(o, c)
    side = "ABOVE" if bl > do else ("BELOW" if bh < do else "STRADDLE")
    return do, bh, bl, side


def sess_bars(D):
    return sorted(m for m in D if BODY < m <= SESS_EXIT)


def logic_a(D, s):
    do, bh, bl, side = s
    if side == "STRADDLE":
        return None
    for m in sess_bars(D):
        if m > LAST_ENTRY:
            break
        c = D[m][3]
        if side == "ABOVE" and c > bh:
            return 1, m, c
        if side == "BELOW" and c < bl:
            return -1, m, c
    return None


def logic_b(D, s):
    do, bh, bl, _ = s
    o, _, _, c = D[BODY]
    if c > o and c > do:
        return 1, BODY, c
    if c < o and c < do:
        return -1, BODY, c
    return None


def first_flip(D, s, side, after_m):
    """First close beyond the OPPOSITE body edge. One per day."""
    _, bh, bl, _ = s
    for m in sess_bars(D):
        if m <= after_m or m > LAST_ENTRY:
            continue
        c = D[m][3]
        if side > 0 and c < bl:
            return m, c
        if side < 0 and c > bh:
            return m, c
    return None


def excursion(D, side, entry, frm, to):
    mfe = mae = 0.0
    tf = ta = None
    for m in sess_bars(D):
        if m <= frm or m > to:
            continue
        _, h, l, _ = D[m]
        up = (h - entry) if side > 0 else (entry - l)
        dn = (entry - l) if side > 0 else (h - entry)
        if up > mfe: mfe, tf = up, m
        if dn > mae: mae, ta = dn, m
    return mfe, tf, mae, ta


def run(days, model, cost=0.0):
    """model: A | A_C2 | A_CFLIP | B"""
    out = []
    for d in sorted(days):
        D = days[d]
        s = setup(D)
        if s is None or SESS_EXIT not in D:
            continue
        sig = logic_b(D, s) if model == "B" else logic_a(D, s)
        if not sig:
            continue
        side, em, entry = sig
        # MFE/MAE always to session end, per spec
        mfe, tmfe, mae, tmae = excursion(D, side, entry, em, SESS_EXIT)
        fl = first_flip(D, s, side, em)
        legs = []
        if model in ("A", "B"):
            legs.append((side, entry, em, D[SESS_EXIT][3], SESS_EXIT, "session"))
        elif model == "A_C2":
            if fl:
                legs.append((side, entry, em, fl[1], fl[0], "C2"))
            else:
                legs.append((side, entry, em, D[SESS_EXIT][3], SESS_EXIT, "session"))
        else:  # A_CFLIP
            if fl:
                legs.append((side, entry, em, fl[1], fl[0], "flip_exit"))
                legs.append((-side, fl[1], fl[0], D[SESS_EXIT][3], SESS_EXIT, "session"))
            else:
                legs.append((side, entry, em, D[SESS_EXIT][3], SESS_EXIT, "session"))
        gross = sum(sd * (xp - ep) for sd, ep, _, xp, _, _ in legs)
        rec = dict(date=d, side=side, entry=entry, entry_m=em, legs=legs,
                   gross=gross, net=gross - cost * len(legs),
                   mfe=mfe, mae=mae, tmfe=tmfe, tmae=tmae,
                   exit_m=legs[-1][4], reason=legs[0][5],
                   hold=legs[-1][4] - em, body=s[1] - s[2], sidecls=s[3])
        if fl:
            fm, fp = fl
            mb, tb, ab, _ = excursion(D, side, entry, em, fm)
            fs = -side
            fm2, _, fa2, _ = excursion(D, fs, fp, fm, SESS_EXIT)
            rec.update(flip_m=fm, flip_px=fp, mfe_before_flip=mb, mae_before_flip=ab,
                       time_to_flip=fm - em, flip_mfe=fm2, flip_mae=fa2,
                       profit_at_flip=side * (fp - entry))
        out.append(rec)
    return out


def stats(rr):
    if not rr:
        return None
    p = [r["net"] for r in rr]
    w = [x for x in p if x > 0]; l = [x for x in p if x <= 0]
    eq = pk = dd = 0.0
    for x in p:
        eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    return dict(n=len(p), nl=sum(1 for r in rr if r["side"] > 0),
                ns=sum(1 for r in rr if r["side"] < 0),
                win=100 * len(w) / len(p),
                avgw=st.mean(w) if w else 0.0, avgl=st.mean(l) if l else 0.0,
                exp=st.mean(p), med=st.median(p),
                pf=(sum(w) / abs(sum(l))) if l and sum(l) else float("inf"),
                net=sum(p), dd=dd,
                hold=st.median([r["hold"] for r in rr]),
                mfe=st.mean([r["mfe"] for r in rr]), mfem=st.median([r["mfe"] for r in rr]),
                mae=st.mean([r["mae"] for r in rr]), maem=st.median([r["mae"] for r in rr]),
                t=st.mean(p) / (st.pstdev(p) or 1e-9) * math.sqrt(len(p)))
