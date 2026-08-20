"""Blind-test participant: classical candlestick reading, encoded from
trader_playbooks/candlestick_patterns.md. NO discretion, NO peeking.

Uses ONLY bars from 09:00 to the decision point (the Logic A entry candle
close). It never sees the key, the outcome, or any later bar.

Patterns and tiers taken verbatim from the playbook table:
  tier A  Bullish/Bearish Engulfing, Morning/Evening Star,
          Three White Soldiers / Three Black Crows
  tier B  Hammer, Shooting Star, Piercing Line, Dark Cloud Cover
  tier C  Harami (bull/bear), Tweezer top/bottom, Doji
Nison context rules applied as the playbook requires, not as suggestions:
  1 trend prerequisite   2 location at a swing   4 size vs average body
Confidence maps to tier: A -> 3, B -> 2, C -> 1. Doji or no pattern -> N.
Conflicting bull and bear signals of equal tier -> N (indecision).
"""
import sys, json, datetime as dt, statistics as st
sys.path.insert(0, "research/au200")
import phase1 as P1

CTX = 540
SHADOW_MULT = 2.0      # corroborated twice in the playbook
BIG_BODY = 1.0         # engulfing/star bodies vs mean body
DOJI = 0.10
LOC_ATR = 1.0
SWING_LEN = 10
TREND_LEN = 10


def body(b): return abs(b[3] - b[0])
def rng(b): return max(b[1] - b[2], 1e-9)
def bull(b): return b[3] > b[0]
def bear(b): return b[3] < b[0]
def upsh(b): return b[1] - max(b[0], b[3])
def dnsh(b): return min(b[0], b[3]) - b[2]


def context(bars):
    """Returns (trend, at_low, at_high). bars = OHLC tuples up to decision."""
    cl = [b[3] for b in bars]
    n = len(cl)
    k = min(TREND_LEN, n - 1)
    trend = 0
    if k >= 3:
        ema, a = cl[0], 2 / (20 + 1)
        for c in cl:
            ema = ema + a * (c - ema)
        slope = cl[-1] - cl[-1 - k]
        if slope > 0 and cl[-1] > ema: trend = 1
        elif slope < 0 and cl[-1] < ema: trend = -1
    w = bars[-min(SWING_LEN, n):]
    hi = max(b[1] for b in w); lo = min(b[2] for b in w)
    trs = [max(b[1] - b[2], abs(b[1] - bars[i - 1][3]), abs(b[2] - bars[i - 1][3]))
           for i, b in enumerate(bars) if i > 0]
    atr = st.mean(trs[-14:]) if len(trs) >= 3 else st.mean(trs) if trs else rng(bars[-1])
    c = bars[-1][3]
    return trend, (c - lo) <= LOC_ATR * atr, (hi - c) <= LOC_ATR * atr


def detect(bars):
    """Return list of (pattern, direction, tier) found on the LAST candle."""
    if len(bars) < 4:
        return []
    a, b, c = bars[-3], bars[-2], bars[-1]
    mb = st.mean([body(x) for x in bars[-20:]]) or 1e-9
    trend, at_low, at_high = context(bars)
    out = []
    big = body(c) >= BIG_BODY * mb

    # --- tier A ---
    if bear(b) and bull(c) and c[3] >= b[0] and c[0] <= b[3] and big and trend < 0:
        out.append(("Bullish Engulfing", 1, "A"))
    if bull(b) and bear(c) and c[3] <= b[0] and c[0] >= b[3] and big and trend > 0:
        out.append(("Bearish Engulfing", -1, "A"))
    if (bear(a) and body(a) >= BIG_BODY * mb and body(b) < 0.5 * body(a)
            and bull(c) and c[3] > (a[0] + a[3]) / 2 and trend < 0):
        out.append(("Morning Star", 1, "A"))
    if (bull(a) and body(a) >= BIG_BODY * mb and body(b) < 0.5 * body(a)
            and bear(c) and c[3] < (a[0] + a[3]) / 2 and trend > 0):
        out.append(("Evening Star", -1, "A"))
    if (all(bull(x) for x in (a, b, c))
            and all(x[1] - x[3] <= 0.25 * rng(x) for x in (a, b, c))
            and a[0] <= b[0] <= a[3] and b[0] <= c[0] <= b[3]):
        out.append(("Three White Soldiers", 1, "A"))
    if (all(bear(x) for x in (a, b, c))
            and all(x[3] - x[2] <= 0.25 * rng(x) for x in (a, b, c))
            and a[3] <= b[0] <= a[0] and b[3] <= c[0] <= b[0]):
        out.append(("Three Black Crows", -1, "A"))

    # --- tier B ---
    if (dnsh(c) >= SHADOW_MULT * body(c) and upsh(c) <= 0.25 * rng(c)
            and min(c[0], c[3]) >= c[2] + (2 / 3) * rng(c) and trend < 0 and at_low):
        out.append(("Hammer", 1, "B"))
    if (upsh(c) >= SHADOW_MULT * body(c) and dnsh(c) <= 0.25 * rng(c)
            and max(c[0], c[3]) <= c[2] + (1 / 3) * rng(c) and trend > 0 and at_high):
        out.append(("Shooting Star", -1, "B"))
    if bear(b) and bull(c) and c[0] < b[2] and c[3] > (b[0] + b[3]) / 2 and trend < 0:
        out.append(("Piercing Line", 1, "B"))
    if bull(b) and bear(c) and c[0] > b[1] and c[3] < (b[0] + b[3]) / 2 and trend > 0:
        out.append(("Dark Cloud Cover", -1, "B"))

    # --- tier C ---
    if bear(b) and body(b) >= BIG_BODY * mb and max(c[0], c[3]) <= max(b[0], b[3]) \
            and min(c[0], c[3]) >= min(b[0], b[3]) and trend < 0:
        out.append(("Bullish Harami", 1, "C"))
    if bull(b) and body(b) >= BIG_BODY * mb and max(c[0], c[3]) <= max(b[0], b[3]) \
            and min(c[0], c[3]) >= min(b[0], b[3]) and trend > 0:
        out.append(("Bearish Harami", -1, "C"))
    tol = 0.10 * rng(c)
    if abs(b[2] - c[2]) <= tol and bull(c) and trend < 0 and at_low:
        out.append(("Tweezer Bottom", 1, "C"))
    if abs(b[1] - c[1]) <= tol and bear(c) and trend > 0 and at_high:
        out.append(("Tweezer Top", -1, "C"))
    if body(c) <= DOJI * rng(c):
        out.append(("Doji", 0, "C"))
    return out


TIER_CONF = {"A": 3, "B": 2, "C": 1}


def classify(bars):
    pats = detect(bars)
    if not pats:
        return "N", 2, []
    bulls = [p for p in pats if p[1] > 0]
    bears = [p for p in pats if p[1] < 0]
    doji = [p for p in pats if p[1] == 0]
    bestb = max((TIER_CONF[p[2]] for p in bulls), default=0)
    bests = max((TIER_CONF[p[2]] for p in bears), default=0)
    if bestb == bests:                       # conflict or nothing directional
        return "N", (3 if doji else 2), pats
    if bestb > bests:
        return "L", bestb, pats
    return "S", bests, pats


if __name__ == "__main__":
    key = json.load(open("research/au200/blind/ANSWER_KEY.json"))
    days = P1.load()
    ans = {}
    for r in key:
        d = dt.date.fromisoformat(r["date"])
        D = days[d]
        bars = [D[m] for m in sorted(D) if CTX <= m <= r["entry_m"]]   # decision point only
        dirn, conf, pats = classify(bars)
        ans[r["id"]] = dict(answer=f"{dirn}{conf}",
                            patterns=[f"{p[0]}({p[2]})" for p in pats])
    json.dump(ans, open("research/au200/blind/CLAUDE_ANSWERS.json", "w"), indent=1)
    from collections import Counter
    c = Counter(v["answer"][0] for v in ans.values())
    cc = Counter(v["answer"] for v in ans.values())
    print(f"classified {len(ans)} charts using ONLY bars up to the decision point")
    print(f"  LONG {c['L']}   SHORT {c['S']}   NO TRADE {c['N']}")
    print(f"  breakdown: {dict(sorted(cc.items()))}")
    pc = Counter(p for v in ans.values() for p in v["patterns"])
    print(f"  patterns fired: {dict(pc.most_common())}")
