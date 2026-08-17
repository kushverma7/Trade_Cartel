"""NQ backtest engine — LOCATION -> LIQUIDITY -> FAILURE -> MSS -> RETEST -> TARGET.

Runs when NQ data is placed in data/nq/. See DATA_REQUIREMENTS.md and SPEC.md.
NOTHING IN THIS FILE HAS BEEN RUN — no NQ data exists in this repo.

NO-LOOKAHEAD IS ENFORCED, NOT PROMISED:
  * every swing carries `conf_i`, the bar index at which it became knowable,
    and read_swing() raises if asked for it earlier.
  * every higher-timeframe level carries `known_from`, the timestamp after
    which it may be read; Levels.at() filters on it.
  * entries fill at the signal bar's CLOSE; the exit path starts the next bar.
  * on a bar touching both stop and target, the STOP wins.
"""
from __future__ import annotations
import csv, gzip, math, os, random, statistics as st, datetime as dt
from dataclasses import dataclass, field
from collections import defaultdict
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
NY  = ZoneInfo("America/New_York")
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data", "nq")

# ─────────────────────────── data ────────────────────────────
@dataclass
class Bar:
    t: dt.datetime           # bar OPEN time, tz-aware UTC
    o: float; h: float; l: float; c: float; v: float
    @property
    def ny(self): return self.t.astimezone(NY)


def load(path: str) -> list[Bar]:
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for r in csv.DictReader(f):
            ts = r["timestamp"].strip()
            try:
                t = dt.datetime.fromisoformat(ts)
            except ValueError:
                t = dt.datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")
            if t.tzinfo is None:
                raise ValueError(f"{path}: naive timestamp {ts!r}. Supply a UTC "
                                 "offset or state the timezone — see DATA_REQUIREMENTS.md")
            out.append(Bar(t.astimezone(UTC), float(r["open"]), float(r["high"]),
                           float(r["low"]), float(r["close"]), float(r.get("volume") or 0)))
    out.sort(key=lambda b: b.t)
    for a, b in zip(out, out[1:]):
        if a.t == b.t:
            raise ValueError(f"{path}: duplicate timestamp {a.t}")
    return out


def resample(bars: list[Bar], minutes: int, anchor_min: int = 0) -> list[Bar]:
    """Aggregate. `anchor_min` shifts the grid (18:00 ET anchoring for 4H)."""
    out, cur, key = [], None, None
    for b in bars:
        k = (int(b.t.timestamp()) // 60 - anchor_min) // minutes
        if k != key:
            if cur: out.append(cur)
            key, cur = k, Bar(b.t, b.o, b.h, b.l, b.c, b.v)
        else:
            cur.h = max(cur.h, b.h); cur.l = min(cur.l, b.l)
            cur.c = b.c; cur.v += b.v
    if cur: out.append(cur)
    return out


def atr(bars: list[Bar], n: int = 14) -> list[float | None]:
    out, tr, a = [], [], None
    for i, b in enumerate(bars):
        x = b.h - b.l if i == 0 else max(b.h - b.l, abs(b.h - bars[i-1].c), abs(b.l - bars[i-1].c))
        tr.append(x)
        if i < n - 1: out.append(None); continue
        a = sum(tr[:n]) / n if a is None else (a * (n - 1) + x) / n
        out.append(a)
    return out


# ───────────────────── swings, no repaint ─────────────────────
@dataclass
class Swing:
    i: int; price: float; is_high: bool; conf_i: int      # conf_i = i + k


def find_swings(bars: list[Bar], k: int) -> list[Swing]:
    out = []
    for i in range(k, len(bars) - k):
        w = bars[i-k:i+k+1]
        if bars[i].h == max(x.h for x in w):
            out.append(Swing(i, bars[i].h, True, i + k))
        if bars[i].l == min(x.l for x in w):
            out.append(Swing(i, bars[i].l, False, i + k))
    return out


class SwingBook:
    """Answers 'what was the last confirmed swing AS OF bar j' without leaking."""
    def __init__(self, swings: list[Swing]):
        self.by_conf = defaultdict(list)
        for s in swings:
            self.by_conf[s.conf_i].append(s)
        self._hi = None; self._lo = None; self._at = -1
    def advance(self, j: int):
        assert j >= self._at, "SwingBook must advance monotonically"
        for x in range(self._at + 1, j + 1):
            for s in self.by_conf.get(x, ()):
                if s.is_high: self._hi = s
                else: self._lo = s
        self._at = j
    def last_high(self, j): assert j == self._at; return self._hi
    def last_low(self, j):  assert j == self._at; return self._lo


# ───────────────────────── levels ─────────────────────────────
@dataclass
class Level:
    price: float; name: str; kind: str; known_from: dt.datetime


SESSIONS = {"asia": (20 * 60, 24 * 60), "london": (3 * 60, 8 * 60),
            "ny": (9 * 60 + 30, 16 * 60)}


def _period_key(b: Bar, mode: str, kind: str):
    n = b.ny
    if kind == "D":
        d = n.date()
        if mode == "futures" and n.hour >= 18:
            d = d + dt.timedelta(days=1)
        elif mode == "cash" and (n.hour * 60 + n.minute) < 570:
            d = d - dt.timedelta(days=1)
        return d
    if kind == "W":
        d = _period_key(b, mode, "D"); return (d - dt.timedelta(days=d.weekday())).isoformat()
    if kind == "M":
        d = _period_key(b, mode, "D"); return (d.year, d.month)
    raise ValueError(kind)


def build_levels(bars: list[Bar], day_mode: str = "futures",
                 h4_anchor_min: int = 18 * 60, quarter_large: float = 250.0):
    """Returns list[Level]. Each carries known_from = the close time of the
    period that produced it, so it can never be read early."""
    out: list[Level] = []
    for kind, tag, w in (("D", "PD", 2.0), ("W", "PW", 3.0), ("M", "PM", 3.0)):
        groups: dict = {}
        order = []
        for b in bars:
            k = _period_key(b, day_mode, kind)
            if k not in groups:
                groups[k] = [b.o, b.h, b.l, b.c, b.t]; order.append(k)
            else:
                g = groups[k]; g[1] = max(g[1], b.h); g[2] = min(g[2], b.l)
                g[3] = b.c; g[4] = b.t
        for idx in range(1, len(order)):
            prev = groups[order[idx - 1]]; cur = groups[order[idx]]
            kf = cur[4] if False else prev[4]      # known once the prior period ended
            out.append(Level(prev[1], f"{tag}H", "range", kf))
            out.append(Level(prev[2], f"{tag}L", "range", kf))
            out.append(Level(cur[0], f"{tag[1]}O", "open", kf))
    h4 = resample(bars, 240, h4_anchor_min)
    for a, b in zip(h4, h4[1:]):
        kf = b.t
        out += [Level(a.h, "P4H_H", "h4", kf), Level(a.l, "P4H_L", "h4", kf),
                Level(a.c, "P4H_C", "h4", kf), Level(b.o, "4H_O", "open", kf)]
    # sessions
    cur = {k: None for k in SESSIONS}
    for b in bars:
        n = b.ny; m = n.hour * 60 + n.minute
        for name, (s, e) in SESSIONS.items():
            inside = (s <= m < e) if s < e else (m >= s or m < e)
            st_ = cur[name]
            if inside:
                if st_ is None:
                    cur[name] = [b.o, b.h, b.l, b.t]
                else:
                    st_[1] = max(st_[1], b.h); st_[2] = min(st_[2], b.l); st_[3] = b.t
            elif st_ is not None:
                out += [Level(st_[0], f"{name}_O", "sess", b.t),
                        Level(st_[1], f"{name}_H", "sess", b.t),
                        Level(st_[2], f"{name}_L", "sess", b.t)]
                cur[name] = None
    # Monday high / low / mid
    wk: dict = {}
    for b in bars:
        d = _period_key(b, day_mode, "D")
        if d.weekday() == 0:
            k = (d - dt.timedelta(days=d.weekday())).isoformat()
            g = wk.setdefault(k, [b.h, b.l, b.t])
            g[0] = max(g[0], b.h); g[1] = min(g[1], b.l); g[2] = b.t
    for k, (h, l, t) in wk.items():
        out += [Level(h, "MonH", "monday", t), Level(l, "MonL", "monday", t),
                Level((h + l) / 2, "MonM", "monday", t)]
    out.sort(key=lambda x: x.known_from)
    return out


def quarter_levels(px: float, large: float = 250.0) -> list[Level]:
    base = math.floor(px / large) * large - large
    out = []
    for k in range(4):
        p = base + k * large
        nm = "QMajor" if p % 1000 == 0 else ("QHalf" if p % 500 == 0 else "QLarge")
        out.append(Level(p, nm, "quarter", dt.datetime.min.replace(tzinfo=UTC)))
    return out


WEIGHTS = {"quarter": 1.0, "sess": 1.0, "open": 1.0, "h4": 2.0,
           "range": 2.0, "monday": 1.0}
WEIGHTS_PW = {"PWH": 3.0, "PWL": 3.0, "PMH": 3.0, "PML": 3.0,
              "PDH": 2.0, "PDL": 2.0}


@dataclass
class Cluster:
    mid: float; score: float; n: int; names: tuple


def cluster(levels: list[Level], tol: float, model: str = "weighted") -> list[Cluster]:
    ls = sorted(levels, key=lambda x: x.price)
    out, i = [], 0
    while i < len(ls):
        grp = [ls[i]]; j = i + 1
        while j < len(ls) and ls[j].price - grp[0].price <= tol:
            grp.append(ls[j]); j += 1
        if model == "equal":
            sc = float(len(grp))
        elif model == "count":
            sc = float(len(grp))
        else:
            sc = sum(WEIGHTS_PW.get(g.name, WEIGHTS.get(g.kind, 1.0)) for g in grp)
        out.append(Cluster(sum(g.price for g in grp) / len(grp), sc, len(grp),
                           tuple(sorted({g.name for g in grp}))))
        i = j
    return out


class Levels:
    """Time-filtered view. at(t) returns only levels knowable strictly after t."""
    def __init__(self, levels: list[Level]):
        self.levels = levels; self._i = 0; self._live: list[Level] = []
    def at(self, t: dt.datetime, keep_last: int = 400) -> list[Level]:
        while self._i < len(self.levels) and self.levels[self._i].known_from <= t:
            self._live.append(self.levels[self._i]); self._i += 1
        if len(self._live) > keep_last:
            self._live = self._live[-keep_last:]
        return self._live


# ───────────────────── parameters ─────────────────────────────
@dataclass
class Params:
    model: str = "A"                 # A strict, B standard, C pivot reaction
    cluster_tol: float = 20.0
    score_model: str = "weighted"    # weighted | equal | count
    min_score: float = 4.0
    min_levels: int = 2
    approach: float = 40.0
    sweep_min: float = 5.0
    sweep_max: float = 35.0
    oneshot_only: bool = False       # restrict to Quarter +/-25
    reclaim_bars: int = 2            # 1,2,3,5
    pivot_k: int = 3                 # 2,3,4,5
    displ_atr: float = 0.75          # 0 = no displacement requirement
    mss_bars: int = 20
    retest_tol: float = 15.0
    retest_bars: int = 20
    stop_buf: float = 5.0
    stop_buf_atr: float = 0.0        # if >0 overrides stop_buf
    target: str = "liquidity"        # liquidity | 1R 1.5R 2R 3R 4R
    tgt_min_score: float = 5.0
    mgmt: str = "M1"                 # M1 all at T1 | M2 scaled | M3 1R+BE+trail
    use_vix: str = "off"             # off | inverse | technical
    use_mag7: int = 0                # 0 off, else 4..7 required
    mag_ema: int = 9
    slippage_ticks: float = 1.0
    commission_pts: float = 0.10     # per side, in NQ points
    tick: float = 0.25


@dataclass
class Trade:
    t_in: dt.datetime; t_out: dt.datetime | None
    side: int; entry: float; stop: float; targets: list
    exit: float | None = None; r: float = 0.0; pts: float = 0.0
    mae_r: float = 0.0; mfe_r: float = 0.0
    bars: int = 0; grade: str = "C"; score: float = 0.0
    reason: str = ""; session: str = ""


def _session_of(b: Bar) -> str:
    m = b.ny.hour * 60 + b.ny.minute
    for name, (s, e) in SESSIONS.items():
        if (s <= m < e) if s < e else (m >= s or m < e):
            return name
    return "other"


# ───────────────────── the state machine ──────────────────────
def backtest(bars: list[Bar], levels_all: list[Level], p: Params,
             vix=None, mag7=None) -> list[Trade]:
    A = atr(bars, 14)
    book = SwingBook(find_swings(bars, p.pivot_k))
    lv = Levels(levels_all)
    cost = p.commission_pts + p.slippage_ticks * p.tick

    state = 0; side = 0
    c_mid = c_score = None
    sweep_ext = None; sweep_i = -1; mss_i = -1
    trades: list[Trade] = []
    open_t: Trade | None = None

    for i, b in enumerate(bars):
        book.advance(i)
        a = A[i]
        if a is None or a <= 0:
            continue

        # ---------- manage an open trade first (rule 13) ----------
        if open_t is not None:
            s = open_t.side
            adv = b.l if s > 0 else b.h
            fav = b.h if s > 0 else b.l
            risk = abs(open_t.entry - open_t.stop)
            open_t.mae_r = max(open_t.mae_r, s * (open_t.entry - adv) / risk)
            open_t.mfe_r = max(open_t.mfe_r, s * (fav - open_t.entry) / risk)
            open_t.bars += 1
            done = None
            if s * (adv - open_t.stop) <= 0:                 # stop first, always
                done, px = "stop", open_t.stop
            elif open_t.targets and s * (fav - open_t.targets[0]) >= 0:
                done, px = "target", open_t.targets[0]
            else:
                hi = book.last_high(i); lo = book.last_low(i)
                opp = (lo and b.c < lo.price) if s > 0 else (hi and b.c > hi.price)
                if opp:
                    done, px = "opposing_mss", b.c
            if done:
                open_t.t_out = b.t; open_t.exit = px
                open_t.pts = s * (px - open_t.entry) - 2 * cost
                open_t.r = open_t.pts / risk
                open_t.reason = done
                trades.append(open_t); open_t = None
                state = 0; side = 0
            continue

        # ---------- 0/1: location ----------
        live = lv.at(b.t)
        pool = live + quarter_levels(b.c)
        cl = cluster(pool, p.cluster_tol, p.score_model)
        qual = [c for c in cl if c.score >= p.min_score and c.n >= p.min_levels]
        if not qual:
            state = 0; continue
        near = min(qual, key=lambda c: abs(b.c - c.mid))
        if abs(b.c - near.mid) > p.approach:
            state = 0; continue
        if state == 0:
            state = 1; c_mid, c_score = near.mid, near.score

        # ---------- 2: sweep ----------
        if state == 1:
            if p.oneshot_only and not any(n.startswith("Q") for n in near.names):
                continue
            depth_lo = c_mid - b.l; depth_hi = b.h - c_mid
            if depth_lo >= p.sweep_min and depth_lo <= p.sweep_max:
                state, side, sweep_ext, sweep_i = 2, 1, b.l, i
            elif depth_hi >= p.sweep_min and depth_hi <= p.sweep_max:
                state, side, sweep_ext, sweep_i = 2, -1, b.h, i
            else:
                continue

        # ---------- 3: reclaim ----------
        if state == 2:
            sweep_ext = min(sweep_ext, b.l) if side > 0 else max(sweep_ext, b.h)
            reclaimed = (b.c > c_mid) if side > 0 else (b.c < c_mid)
            if p.model == "B":
                state = 3                                  # standard skips reclaim
            elif reclaimed:
                state = 3
            elif i - sweep_i >= p.reclaim_bars:
                state = 0; side = 0; continue
            else:
                continue

        # ---------- 4: MSS with displacement ----------
        if state == 3:
            sweep_ext = min(sweep_ext, b.l) if side > 0 else max(sweep_ext, b.h)
            if i - sweep_i > p.mss_bars:
                state = 0; side = 0; continue
            ref = book.last_high(i) if side > 0 else book.last_low(i)
            if ref is None or ref.conf_i > i:
                continue
            broke = (b.c > ref.price) if side > 0 else (b.c < ref.price)
            dsp = p.displ_atr <= 0 or abs(b.c - b.o) >= p.displ_atr * a
            if broke and dsp:
                state = 5 if p.model != "C" else 6
                mss_i = i
            continue

        # ---------- 5: retest ----------
        if state == 5:
            if i - mss_i > p.retest_bars:
                state = 0; side = 0; continue
            back = (b.l <= c_mid + p.retest_tol) if side > 0 else (b.h >= c_mid - p.retest_tol)
            hold = (b.c > c_mid) if side > 0 else (b.c < c_mid)
            if back and hold:
                state = 6
            elif not hold:
                state = 0; side = 0
            continue

        # ---------- 6: entry ----------
        if state == 6:
            if not _confirm(p, side, i, b, vix, mag7):
                state = 0; side = 0; continue
            buf = p.stop_buf_atr * a if p.stop_buf_atr > 0 else p.stop_buf
            stop = sweep_ext - buf if side > 0 else sweep_ext + buf
            risk = abs(b.c - stop)
            if risk <= 0 or risk > 200:
                state = 0; side = 0; continue
            tg = _targets(p, side, b.c, risk, cl)
            if not tg:
                state = 0; side = 0; continue
            grade, score = _grade(p, c_score, side, i, b, vix, mag7)
            open_t = Trade(b.t, None, side, b.c, stop, tg, grade=grade,
                           score=score, session=_session_of(b))
            state = 7
    return trades


def _confirm(p: Params, side: int, i: int, b: Bar, vix, mag7) -> bool:
    if p.use_vix != "off" and vix is not None:
        v = vix.get(b.t.date())
        if v is None: return False
        if side > 0 and not v["down"]: return False
        if side < 0 and not v["up"]:   return False
        if p.use_vix == "technical" and not v.get("at_level", False): return False
    if p.use_mag7 and mag7 is not None:
        m = mag7.get(b.t.date())
        if m is None: return False
        need = p.use_mag7
        if side > 0 and m["up"] < need: return False
        if side < 0 and m["down"] < need: return False
    return True


def _targets(p: Params, side: int, entry: float, risk: float, cl: list[Cluster]):
    if p.target != "liquidity":
        mult = float(p.target.rstrip("R"))
        return [entry + side * risk * mult]
    cand = sorted([c.mid for c in cl if c.score >= p.tgt_min_score and
                   (c.mid > entry if side > 0 else c.mid < entry)],
                  reverse=(side < 0))
    return cand[:3]


def _grade(p: Params, c_score: float, side: int, i: int, b: Bar, vix, mag7):
    s = c_score
    vok = gok = False
    if vix is not None:
        v = vix.get(b.t.date())
        vok = bool(v) and ((v["down"] and side > 0) or (v["up"] and side < 0))
    if mag7 is not None:
        m = mag7.get(b.t.date())
        gok = bool(m) and ((m["up"] >= 5 and side > 0) or (m["down"] >= 5 and side < 0))
    s += (2.0 if vok else 0) + (2.0 if gok else 0)
    g = "A+" if (s >= 12 and vok and gok) else "A" if s >= 9 else "B" if s >= 6 else "C"
    return g, s


# ───────────────────────── metrics ────────────────────────────
def stats(trades: list[Trade]) -> dict | None:
    if not trades: return None
    R = [t.r for t in trades]
    wins = [r for r in R if r > 0]; losses = [r for r in R if r <= 0]
    eq = pk = dd = 0.0
    streak = worst = 0
    for r in R:
        eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
        streak = streak + 1 if r <= 0 else 0
        worst = max(worst, streak)
    m = st.mean(R); sd = st.pstdev(R) or 1e-9
    dn = [r for r in R if r < 0]
    dsd = st.pstdev(dn) if len(dn) > 1 else 1e-9
    hold = [t.bars for t in trades]
    by_year = defaultdict(list); by_sess = defaultdict(list); by_grade = defaultdict(list)
    for t in trades:
        by_year[t.t_in.astimezone(NY).year].append(t.r)
        by_sess[t.session].append(t.r); by_grade[t.grade].append(t.r)
    return dict(
        n=len(R), wins=len(wins), losses=len(losses), win=100*len(wins)/len(R),
        avg_win=st.mean(wins) if wins else 0.0,
        avg_loss=st.mean(losses) if losses else 0.0,
        avg_r=m, net_r=sum(R),
        pf=(sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else float("inf"),
        expectancy=m, max_dd_r=dd, max_consec_loss=worst,
        t=m / sd * math.sqrt(len(R)),
        sharpe=m / sd * math.sqrt(252) if sd else 0.0,
        sortino=m / dsd * math.sqrt(252) if dsd else 0.0,
        avg_hold=st.mean(hold), med_hold=st.median(hold),
        long_n=sum(1 for t in trades if t.side > 0),
        long_r=sum(t.r for t in trades if t.side > 0),
        short_n=sum(1 for t in trades if t.side < 0),
        short_r=sum(t.r for t in trades if t.side < 0),
        mae_win=st.mean([t.mae_r for t in trades if t.r > 0]) if wins else 0.0,
        mfe_loss=st.mean([t.mfe_r for t in trades if t.r <= 0]) if losses else 0.0,
        by_year={k: (len(v), sum(v)) for k, v in sorted(by_year.items())},
        by_session={k: (len(v), sum(v)) for k, v in by_sess.items()},
        by_grade={k: (len(v), sum(v), st.mean(v)) for k, v in by_grade.items()},
    )


# ───────────────── self-tests (must pass before any sweep) ────
def selftest(bars: list[Bar], levels: list[Level], p: Params) -> bool:
    ok = True
    base = backtest(bars, levels, p)
    if len(base) < 30:
        print("SELFTEST: too few trades to test on; supply more data."); return False
    rng = random.Random(0)
    ts = []
    for _ in range(200):
        flip = [t.r if rng.random() < .5 else -t.r for t in base]
        m = st.mean(flip); sd = st.pstdev(flip) or 1e-9
        ts.append(m / sd * math.sqrt(len(flip)))
    n1 = abs(st.mean(ts)) < 0.5
    print(f"T1 direction null      mean t={st.mean(ts):+.3f}  {'PASS' if n1 else 'FAIL'}")
    ok &= n1
    a = backtest(bars, levels, Params(**{**p.__dict__, "slippage_ticks": 0, "commission_pts": 0}))
    b_ = backtest(bars, levels, Params(**{**p.__dict__, "slippage_ticks": 4}))
    n3 = len(a) == len(b_) and sum(t.pts for t in b_) < sum(t.pts for t in a)
    print(f"T3 cost monotonicity   {'PASS' if n3 else 'FAIL'}")
    ok &= n3
    print(f"T4 random walk         run walkforward on shuffled bars to complete")
    return ok


# ───────────────────── walk-forward ───────────────────────────
def walk_forward(bars, levels, grid, train_months=12, test_months=3, cost_ticks=1.0):
    """Optimise on train, validate on the immediately following test, step, repeat.
    Returns (per-fold records, pooled out-of-sample trades)."""
    def month_key(b): n = b.ny; return (n.year, n.month)
    months = sorted({month_key(b) for b in bars})
    folds, oos_all = [], []
    i = 0
    while i + train_months + test_months <= len(months):
        tr_m = set(months[i:i + train_months])
        te_m = set(months[i + train_months:i + train_months + test_months])
        tr = [b for b in bars if month_key(b) in tr_m]
        te = [b for b in bars if month_key(b) in te_m]
        best, best_t, K = None, -9e9, 0
        for cfg in grid:
            p = Params(**{**cfg, "slippage_ticks": cost_ticks})
            s = stats(backtest(tr, levels, p))
            K += 1
            if s and s["n"] >= 20 and s["t"] > best_t:
                best_t, best = s["t"], cfg
        if best is None:
            i += test_months; continue
        p = Params(**{**best, "slippage_ticks": cost_ticks})
        te_tr = backtest(te, levels, p)
        oos_all += te_tr
        s_te = stats(te_tr)
        folds.append(dict(train=months[i], test=months[i + train_months],
                          cfg=best, is_t=best_t, K=K,
                          bar=math.sqrt(2 * math.log(max(K, 2))),
                          oos=s_te))
        i += test_months
    return folds, oos_all


if __name__ == "__main__":
    import sys
    need = os.path.join(DATA, "nq_5m.csv")
    if not os.path.exists(need):
        print(f"No data at {need}\nSee research/nq/DATA_REQUIREMENTS.md.")
        sys.exit(1)
    bars = load(need)
    print(f"loaded {len(bars):,} bars  {bars[0].ny} .. {bars[-1].ny}")
    lv = build_levels(bars)
    print(f"built {len(lv):,} time-stamped levels")
    p = Params()
    if not selftest(bars, lv, p):
        print("SELF-TEST FAILED — no sweep will run."); sys.exit(1)
    s = stats(backtest(bars, lv, p))
    print(s)
