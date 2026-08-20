"""10 AM Body Break — execution and the primary model matrix.

Baseline exits are all CLOSE-based (opposite body close, daily-open close,
session end), so they are execution-unambiguous: there is no intrabar path to
guess and no optimistic fill assumption. Ambiguity is only introduced by fixed
targets, which are tested separately and flagged.
"""
from __future__ import annotations
import sys, os, csv, math, statistics as st, datetime as dt
sys.path.insert(0, os.path.dirname(__file__))
import strategy as S
from collections import defaultdict

CUT = S.CUTOFF


def bars_after(d, m):
    return [b for b in d.bars if b.m > m and b.m <= CUT]


def excursion(d, side, entry, frm_m, to_m):
    """MFE/MAE in points between two bar minutes, plus the time each occurred."""
    mfe = mae = 0.0; tf = ta = None
    for b in d.bars:
        if b.m <= frm_m or b.m > to_m:
            continue
        up = (b.h - entry) if side > 0 else (entry - b.l)
        dn = (entry - b.l) if side > 0 else (b.h - entry)
        if up > mfe: mfe, tf = up, b.m
        if dn > mae: mae, ta = dn, b.m
    return mfe, tf, mae, ta


def exit_at(d, side, from_m, mode):
    """Returns (exit_bar, reason). All close-based -> unambiguous."""
    for b in bars_after(d, from_m):
        if mode == "body" and ((side > 0 and b.c < d.body_lo) or (side < 0 and b.c > d.body_hi)):
            return b, "opposite_body"
        if mode == "dailyopen" and ((side > 0 and b.c < d.daily_open) or (side < 0 and b.c > d.daily_open)):
            return b, "daily_open"
    last = [b for b in d.bars if b.m <= CUT]
    return (last[-1], "session") if last else (None, "none")


def run(days, logic="A", cvar="none", cost=0.0):
    """cvar: none | C1 | C2 | C3A | C3B | C3C | C1D"""
    out = []
    for d in days:
        sig = S.logic_a(d) if logic == "A" else S.logic_b(d)
        if not sig:
            continue
        side, ebar = sig
        entry, em = ebar.c, ebar.m
        rec = dict(date=d.date, logic=logic, cvar=cvar, side=side,
                   daily_open=d.daily_open, body_hi=d.body_hi, body_lo=d.body_lo,
                   body_size=d.body_hi - d.body_lo, sidecls=d.side,
                   dist=(d.body_lo - d.daily_open) if d.side == "ABOVE" else (d.daily_open - d.body_hi),
                   entry_m=em, entry=entry, legs=[])
        flip = S.first_flip(d, side, em)
        rec["flip_m"] = flip.m if flip else None
        rec["flip_px"] = flip.c if flip else None
        if flip:
            mfe_b, tmfe_b, mae_b, _ = excursion(d, side, entry, em, flip.m)
            rec["mfe_before_flip"] = mfe_b
            rec["time_to_mfe"] = (tmfe_b - em) if tmfe_b else None
            rec["profit_at_flip"] = side * (flip.c - entry)
            rec["giveback"] = mfe_b - rec["profit_at_flip"]
            rec["mfe_to_flip_min"] = (flip.m - tmfe_b) if tmfe_b else None

        # ---- leg 1: the original trade ----
        if cvar == "none" or flip is None:
            xb, why = exit_at(d, side, em, "session")
            end_m = xb.m
        else:
            xb, why, end_m = flip, "flip", flip.m
        mfe, tmfe, mae, tmae = excursion(d, side, entry, em, end_m)
        g = side * (xb.c - entry)
        rec["legs"].append(dict(side=side, entry=entry, entry_m=em, exit=xb.c,
                                exit_m=end_m, reason=why, gross=g, mfe=mfe, mae=mae,
                                tmfe=tmfe, tmae=tmae, kind="original"))

        # ---- leg 2: what the flip becomes ----
        if flip is not None and cvar not in ("none", "C2"):
            f_side = -side
            f_entry_bar = flip
            if cvar in ("C3A", "C3B", "C3C"):
                f_entry_bar = S.confirm(d, flip, f_side, cvar[-1])
            if f_entry_bar is not None and f_entry_bar.m < CUT:
                fe, fm = f_entry_bar.c, f_entry_bar.m
                fx, fwhy = exit_at(d, f_side, fm, "session")
                # ---- leg 3: Logic D re-entry after a failed flip ----
                if cvar == "C1D":
                    fail = S.first_flip(d, f_side, fm)
                    if fail is not None:
                        fmfe, ftm, fmae, fam = excursion(d, f_side, fe, fm, fail.m)
                        rec["legs"].append(dict(side=f_side, entry=fe, entry_m=fm,
                                                exit=fail.c, exit_m=fail.m, reason="flip_failed",
                                                gross=f_side*(fail.c-fe), mfe=fmfe, mae=fmae,
                                                tmfe=ftm, tmae=fam, kind="flip"))
                        rx, rwhy = exit_at(d, side, fail.m, "session")
                        rmfe, rtm, rmae, ram = excursion(d, side, fail.c, fail.m, rx.m)
                        rec["legs"].append(dict(side=side, entry=fail.c, entry_m=fail.m,
                                                exit=rx.c, exit_m=rx.m, reason=rwhy,
                                                gross=side*(rx.c-fail.c), mfe=rmfe, mae=rmae,
                                                tmfe=rtm, tmae=ram, kind="reentry"))
                        rec["flip_failed"] = True
                        out.append(_finish(rec, cost)); continue
                fmfe, ftm, fmae, fam = excursion(d, f_side, fe, fm, fx.m)
                rec["legs"].append(dict(side=f_side, entry=fe, entry_m=fm, exit=fx.c,
                                        exit_m=fx.m, reason=fwhy, gross=f_side*(fx.c-fe),
                                        mfe=fmfe, mae=fmae, tmfe=ftm, tmae=fam, kind="flip"))
        out.append(_finish(rec, cost))
    return out


def _finish(rec, cost):
    rec["gross"] = sum(l["gross"] for l in rec["legs"])
    rec["costs"] = cost * len(rec["legs"])
    rec["net"] = rec["gross"] - rec["costs"]
    rec["mfe"] = rec["legs"][0]["mfe"]
    rec["mae"] = rec["legs"][0]["mae"]
    return rec


def summarise(recs, label):
    if not recs:
        return None
    p = [r["net"] for r in recs]
    w = [x for x in p if x > 0]; l = [x for x in p if x <= 0]
    eq = pk = dd = 0.0
    for x in p:
        eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    m = st.mean(p); sd = st.pstdev(p) or 1e-9
    caps = [r["legs"][0]["gross"] / r["legs"][0]["mfe"]
            for r in recs if r["legs"][0]["mfe"] > 0 and r["legs"][0]["gross"] > 0]
    flips = [r for r in recs if r.get("flip_m") is not None]
    fw = [r for r in flips if len(r["legs"]) > 1 and r["legs"][1]["gross"] > 0]
    return dict(label=label, n=len(p), win=100*len(w)/len(p),
                avg_win=st.mean(w) if w else 0.0, avg_loss=st.mean(l) if l else 0.0,
                rr=(st.mean(w)/abs(st.mean(l))) if w and l and st.mean(l) else float("nan"),
                exp=m, pf=(sum(w)/abs(sum(l))) if l and sum(l) else float("inf"),
                net=sum(p), dd=dd, t=m/sd*math.sqrt(len(p)),
                mfe=st.mean([r["mfe"] for r in recs]), mfe_med=st.median([r["mfe"] for r in recs]),
                mae=st.mean([r["mae"] for r in recs]), mae_med=st.median([r["mae"] for r in recs]),
                capture=100*st.mean(caps) if caps else 0.0,
                flip_freq=100*len(flips)/len(p),
                flip_win=100*len(fw)/len(flips) if flips else float("nan"))
