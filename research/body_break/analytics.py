"""Phase 2 analytics for Logic A. No new indicators, no new concepts."""
import sys, os, math, statistics as st
sys.path.insert(0, os.path.dirname(__file__) or ".")
import strategy as S, backtest as B
from collections import defaultdict

def pct(v, q):
    if not v: return float("nan")
    s = sorted(v); i = int(q * (len(s) - 1))
    return s[i]

def block(p):
    """p = list of net points"""
    if not p: return None
    w = [x for x in p if x > 0]; l = [x for x in p if x <= 0]
    eq = pk = dd = 0.0
    for x in p:
        eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    m = st.mean(p); sd = st.pstdev(p) or 1e-9
    return dict(n=len(p), win=100*len(w)/len(p), exp=m,
                pf=(sum(w)/abs(sum(l))) if l and sum(l) else float("inf"),
                net=sum(p), dd=dd, t=m/sd*math.sqrt(len(p)),
                avgw=st.mean(w) if w else 0.0, avgl=st.mean(l) if l else 0.0,
                medw=st.median(w) if w else 0.0, medl=st.median(l) if l else 0.0)

def load_days(path):
    raw = S.load(path)
    ds = [S.build_day(d, raw["days"][d]) for d in sorted(raw["days"])]
    return [d for d in ds if d.side != "UNTESTABLE"]

def vol_0950_1000(d):
    b = next((x for x in d.bars if x.m == S.REF_MIN), None)
    return (b.h - b.l) if b else None

def logic_a_recs(days, cost=0.30, cvar="none"):
    return B.run(days, "A", cvar, cost)
