"""Phase 3 — buffered structural exit. Logic A entry UNCHANGED. No flip. No TP."""
import sys, os, math, statistics as st
sys.path.insert(0, os.path.dirname(__file__) or ".")
import strategy as S, analytics as A
from collections import defaultdict

CUT = S.CUTOFF

def build(path):
    raw = S.load(path)
    days = [S.build_day(d, raw["days"][d]) for d in sorted(raw["days"])]
    days = [d for d in days if d.side != "UNTESTABLE"]
    # continuous ATR(14) on 5m bars — value at bar i uses bars < i only
    flat = []
    for d in sorted(raw["days"]):
        for b in raw["days"][d]:
            flat.append((d, b))
    flat.sort(key=lambda x: x[1].t)
    atr = {}
    tr, a, prev = [], None, None
    for d, b in flat:
        atr[(d, b.m)] = a                      # value BEFORE this bar -> no lookahead
        x = (b.h - b.l) if prev is None else max(b.h - b.l, abs(b.h - prev), abs(b.l - prev))
        tr.append(x)
        if len(tr) >= 14:
            a = sum(tr[:14]) / 14 if a is None else (a * 13 + x) / 14
        prev = b.c
    return days, atr

def r0950(d):
    b = next((x for x in d.bars if x.m == S.REF_MIN), None)
    r = (b.h - b.l) if b else None
    return r if r and r > 0 else None

def run(days, atr, mode="none", buf=0.0, cost=0.30):
    """mode: none | body | r0950 | atr   (buf ignored when mode='none')"""
    out = []
    for d in days:
        sig = S.logic_a(d)
        if not sig:
            continue
        side, eb = sig
        e, em = eb.c, eb.m
        bsz = d.body_hi - d.body_lo
        if mode == "none":
            lvl = None
        else:
            if mode == "body":   unit = bsz
            elif mode == "r0950": unit = r0950(d)
            else:                unit = atr.get((d.date, em))
            if unit is None or unit <= 0:
                continue
            lvl = (d.body_lo - unit * buf) if side > 0 else (d.body_hi + unit * buf)
        xb, why = None, "session"
        seg = [b for b in d.bars if em < b.m <= CUT]
        mfe = mae = 0.0
        for b in seg:
            up = (b.h - e) if side > 0 else (e - b.l)
            dn = (e - b.l) if side > 0 else (b.h - e)
            mfe = max(mfe, up); mae = max(mae, dn)
            if lvl is not None and ((b.c < lvl) if side > 0 else (b.c > lvl)):
                xb, why = b, "buffered_C2"; break
        if xb is None:
            xb = seg[-1] if seg else eb
        gross = side * (xb.c - e)
        # excursion measured only up to the exit
        mfe = mae = 0.0
        for b in seg:
            if b.m > xb.m: break
            mfe = max(mfe, (b.h - e) if side > 0 else (e - b.l))
            mae = max(mae, (e - b.l) if side > 0 else (b.h - e))
        # what happened AFTER the exit, in the original direction
        post = 0.0; back_entry = False; back_body = False
        for b in seg:
            if b.m <= xb.m: continue
            post = max(post, (b.h - e) if side > 0 else (e - b.l))
            if (b.c > e) if side > 0 else (b.c < e): back_entry = True
            if (b.c > d.body_hi) if side > 0 else (b.c < d.body_lo): back_body = True
        out.append(dict(date=d.date, side=side, entry=e, entry_m=em, exit=xb.c, exit_m=xb.m,
                        why=why, gross=gross, net=gross - cost, mfe=mfe, mae=mae,
                        hold=xb.m - em, body=bsz, unit=(None if mode=="none" else unit),
                        post=post, back_entry=back_entry, back_body=back_body,
                        vol=r0950(d)))
    return out

def stats(rr):
    if not rr: return None
    p = [r["net"] for r in rr]
    w = [x for x in p if x > 0]; l = [x for x in p if x <= 0]
    eq = pk = dd = 0.0
    for x in p:
        eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    caps = [r["gross"]/r["mfe"] for r in rr if r["mfe"] > 0 and r["gross"] > 0]
    return dict(n=len(p), win=100*len(w)/len(p),
                avgw=st.mean(w) if w else 0.0, medw=st.median(w) if w else 0.0,
                avgl=st.mean(l) if l else 0.0, medl=st.median(l) if l else 0.0,
                pf=(sum(w)/abs(sum(l))) if l and sum(l) else float("inf"),
                exp=st.mean(p), net=sum(p), dd=dd,
                mfe=st.mean([r["mfe"] for r in rr]), mfem=st.median([r["mfe"] for r in rr]),
                mae=st.mean([r["mae"] for r in rr]), maem=st.median([r["mae"] for r in rr]),
                cap=100*st.mean(caps) if caps else 0.0,
                hold=st.mean([r["hold"] for r in rr]), holdm=st.median([r["hold"] for r in rr]),
                exit_c2=100*sum(1 for r in rr if r["why"]=="buffered_C2")/len(rr),
                worst=min(p))
