"""AU200 Phase 3 — the opposite-side sweep hypothesis. ONE hypothesis, three
pre-registered definitions, frozen +-20 outcome. Logic A entry untouched.

Classification uses ONLY bars strictly between the 10:00 candle close and the
Logic A entry candle. Nothing after entry, nothing about the outcome.
"""
import sys, math, statistics as st
sys.path.insert(0, "research/au200")
import phase1 as P1, phase2 as P2


def classify(D, s, side, entry_m, bump=0.0):
    """Return dict of S1/S2/S3 flags. bump perturbs BOTH body edges outward
    (feed-robustness diagnostic only)."""
    do, bh, bl, _ = s
    bh_, bl_ = bh + bump, bl - bump
    opp = bl_ if side > 0 else bh_
    pre = [m for m in sorted(D) if 600 < m < entry_m]
    s1 = s2 = s3 = False
    closed_through = False
    reclaimed = False
    for m in pre:
        o, h, l, c = D[m]
        if side > 0:
            if l <= opp:
                s1 = True
            if l < opp and c >= opp:
                s2 = True
            if c < opp:
                closed_through = True
            elif closed_through and c > opp:
                reclaimed = True
        else:
            if h >= opp:
                s1 = True
            if h > opp and c <= opp:
                s2 = True
            if c > opp:
                closed_through = True
            elif closed_through and c < opp:
                reclaimed = True
    s3 = closed_through and reclaimed
    return dict(S1=s1, S2=s2, S3=s3)


def build(days, m1, bump=0.0):
    """One row per Logic A trade with flags, volatility controls and outcome."""
    rows = []
    for d in sorted(days):
        D = days[d]
        s = P1.setup(D)
        if s is None or P1.SESS_EXIT not in D:
            continue
        a = P1.logic_a(D, s)
        if not a:
            continue
        side, em, entry = a
        do, bh, bl, _ = s
        o10, h10, l10, c10 = D[P1.BODY]
        pre = [m for m in sorted(D) if P1.REF <= m <= em]
        prng = (max(D[m][1] for m in pre) - min(D[m][2] for m in pre)) if pre else 0.0
        flags = classify(D, s, side, em, bump)
        path = [b for b in m1.get(d, []) if em + 5 <= b[0] <= P1.SESS_EXIT]
        touch, tmin = P2.first_touch(path, entry, 20)
        out = None
        if touch not in ("NONE", "AMB"):
            out = 1 if ((touch == "UP") if side > 0 else (touch == "DOWN")) else 0
        mfe = mae = 0.0
        t20 = None
        for m, oo, hh, ll, cc in path:
            up = (hh - entry) if side > 0 else (entry - ll)
            dn = (entry - ll) if side > 0 else (hh - entry)
            mfe = max(mfe, up); mae = max(mae, dn)
            if t20 is None and up >= 20:
                t20 = m - em
        rows.append(dict(date=d, side=side, entry=entry, entry_m=em, out=out,
                         tfirst=(tmin - em) if tmin else None, t20=t20,
                         mfe=mfe, mae=mae, touch=touch,
                         rng1000=h10 - l10, body=bh - bl, pre_range=prng, **flags))
    return rows


def prop_test(w1, n1, w2, n2):
    """Two-proportion z test + odds ratio with 95% CI."""
    if min(n1, n2) < 5 or w1 in (0, n1) or w2 in (0, n2):
        return dict(diff=float("nan"), OR=float("nan"), lo=float("nan"),
                    hi=float("nan"), p=float("nan"))
    p1, p2 = w1 / n1, w2 / n2
    pp = (w1 + w2) / (n1 + n2)
    se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se if se > 0 else 0.0
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    a, b_, c, d_ = w1, n1 - w1, w2, n2 - w2
    OR = (a * d_) / (b_ * c)
    sel = math.sqrt(1 / a + 1 / b_ + 1 / c + 1 / d_)
    return dict(diff=100 * (p1 - p2), OR=OR, lo=math.exp(math.log(OR) - 1.96 * sel),
                hi=math.exp(math.log(OR) + 1.96 * sel), p=p)
