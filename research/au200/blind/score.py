"""Scoring for the blind test. RUN ONLY AFTER ANSWERS ARE LOCKED.

Comparisons, all pre-registered:
  1. manual TAKEs vs original Logic A on the same 120 charts
  2. manual TAKEs vs random direction (permutation)
  3. manual TAKEs vs a random subset of Logic A of the same size (bootstrap)
Outcome is the frozen +-20 first passage. Nothing here is tunable.
"""
import json, random, math, statistics as st, sys, collections


def load_key(p="research/au200/blind/ANSWER_KEY.json"):
    return {r["id"]: r for r in json.load(open(p))}


def parse(ans_text):
    """'001 L 2' per line -> {id: (dir, conf)}"""
    out = {}
    for ln in ans_text.strip().splitlines():
        t = ln.replace(",", " ").split()
        if len(t) < 2:
            continue
        cid = t[0].zfill(3); d = t[1].upper()[0]
        if d not in "LSN":
            continue
        c = int(t[2]) if len(t) > 2 and t[2].isdigit() else None
        out[cid] = (d, c)
    return out


def outcome(rec, direction):
    """+-20 first passage for a chosen direction. None = unresolved/ambiguous."""
    t = rec["touch20"]
    if t in ("NONE", "AMB"):
        return None
    return 1 if ((t == "UP") if direction == "L" else (t == "DOWN")) else 0


def score(key, ans, cost=1.0):
    takes = [(i, d, c) for i, (d, c) in ans.items() if d in "LS"]
    res = []
    for i, d, c in takes:
        o = outcome(key[i], d)
        if o is not None:
            res.append((i, d, c, o))
    n = len(res); w = sum(r[3] for r in res)
    return dict(n_take=len(takes), n_none=sum(1 for d, _ in ans.values() if d == "N"),
                n_dec=n, wins=w, wr=(100 * w / n if n else float("nan")),
                exp=((w * 20 - (n - w) * 20) / n if n else float("nan")),
                expc=((w * (20 - cost) - (n - w) * (20 + cost)) / n if n else float("nan")),
                rows=res)


def permutation(key, ans, runs=10000, seed=5):
    """Null: same charts selected, direction chosen at random."""
    rng = random.Random(seed)
    ids = [i for i, (d, _) in ans.items() if d in "LS" and key[i]["touch20"] not in ("NONE", "AMB")]
    actual = score(key, ans)["wr"]
    sims = []
    for _ in range(runs):
        w = sum(outcome(key[i], "L" if rng.random() < .5 else "S") for i in ids)
        sims.append(100 * w / len(ids))
    sims.sort()
    return actual, st.mean(sims), st.pstdev(sims), \
        (sum(1 for s in sims if s >= actual) + 1) / (runs + 1)


def bootstrap_logicA(key, ans, runs=10000, seed=9):
    """Null: a random subset of Logic A of the same size, taken as signalled."""
    rng = random.Random(seed)
    pool = [r for r in key.values() if r["touch20"] not in ("NONE", "AMB")]
    k = score(key, ans)["n_dec"]
    actual = score(key, ans)["wr"]
    sims = []
    for _ in range(runs):
        s = rng.sample(pool, min(k, len(pool)))
        w = sum(1 if ((r["touch20"] == "UP") if r["logicA"] == "LONG" else (r["touch20"] == "DOWN")) else 0
                for r in s)
        sims.append(100 * w / len(s))
    sims.sort()
    return actual, st.mean(sims), st.pstdev(sims), \
        (sum(1 for s in sims if s >= actual) + 1) / (runs + 1)
