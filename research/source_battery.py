"""
Every exactly-specified claim in trader_playbooks/sources, tested at once.

WHY A BATTERY AND NOT SIX SCRIPTS
  The sources make dozens of claims; only some are specified precisely enough
  to be falsified. Testing them one at a time invites the mistake this desk has
  already made fifteen times: run a claim, see a positive number, believe it.
  Run them together against a shared null and the multiple-comparison problem
  becomes visible instead of invisible -- with 12 arms at the 5% level you
  expect roughly one "significant" result from pure noise, so a single lone
  survivor is not a finding.

THE CLAIMS AND WHERE THEY COME FROM
  PIN_BULL/PIN_BEAR    price_action_trading_pinbar_insidebar_fakey.txt:430
      "you want to see the pin bar tail be two/thirds the total pin bar length
      or more and the rest ... one/third or less". Coded literally.
  INSIDE_UP/INSIDE_DN  same source, line 342: inside bars as continuation in a
      strong trend, and as reversals at "major market turning points".
  FAKEY_UP/FAKEY_DN    same source, line 365: "a false break from an inside bar
      pattern" -- break the inside-bar range, close back inside.
  BIGPLAY_L/BIGPLAY_S  big_players_reversal_entry.txt, ported line for line
      including the ADX>40 gate and the DI ordering.
  DOLLAR_Q             gold_scalping_strategy_blueprint.txt: ".00 Major whole
      number: strongest S/R ... .25/.75 Minor quarter: weak S/R, often
      breached". This is a DIFFERENT claim from the $25/$50/$100 grid already
      tested and rejected -- it is the one-dollar grid.
  NY_OPEN_REV          same source: "Gold LOVES the daily open -- major
      reversals happen within 30 min of NY open".

THE NULL EACH ONE MUST BEAT
  A pattern's forward move is compared against the UNCONDITIONAL forward move
  over the same horizon, measured in ATR so the comparison survives gold going
  from $1500 to $3000. The test statistic is Welch's t on that difference. A
  pattern that merely moves in its own direction is not evidence -- gold drifts
  up, so every long-side pattern looks good against zero. The unconditional
  mean is the honest baseline.
"""
import numpy as np, pandas as pd

from backtest.io import load_csv

HORIZONS = (4, 8, 16, 32)          # 30m bars: 2h, 4h, 8h, 16h


# --------------------------------------------------------------------- helpers
def atr(df, n=14):
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()


def wilder_adx(df, n=14):
    """The indicator's own smoothing, not ta.rma -- ported from the source."""
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.r_[c[0], c[:-1]]; ph = np.r_[h[0], h[:-1]]; pl = np.r_[l[0], l[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    dmp = np.where(h - ph > pl - l, np.maximum(h - ph, 0), 0.0)
    dmm = np.where(pl - l > h - ph, np.maximum(pl - l, 0), 0.0)

    def smooth(x):
        out = np.zeros_like(x); acc = 0.0
        for i, v in enumerate(x):
            acc = acc - acc / n + v
            out[i] = acc
        return out

    st, sp, sm = smooth(tr), smooth(dmp), smooth(dmm)
    with np.errstate(divide="ignore", invalid="ignore"):
        dip = np.where(st > 0, sp / st * 100, 0.0)
        dim = np.where(st > 0, sm / st * 100, 0.0)
        dx = np.where(dip + dim > 0, abs(dip - dim) / (dip + dim) * 100, 0.0)
    return pd.Series(dx).rolling(n).mean().to_numpy(), dip, dim


# --------------------------------------------------------------------- patterns
def pin_bars(df, tail_frac=2 / 3):
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    rng = h - l
    ok = rng > 0
    body_hi, body_lo = np.maximum(o, c), np.minimum(o, c)
    lower = np.where(ok, (body_lo - l) / np.where(ok, rng, 1), 0)
    upper = np.where(ok, (h - body_hi) / np.where(ok, rng, 1), 0)
    body = np.where(ok, (body_hi - body_lo) / np.where(ok, rng, 1), 1)
    bull = ok & (lower >= tail_frac) & (body <= 1 / 3)
    bear = ok & (upper >= tail_frac) & (body <= 1 / 3)
    return bull, bear


def inside_bars(df):
    h, l = (df[k].to_numpy(float) for k in ("high", "low"))
    ph, pl = np.r_[np.nan, h[:-1]], np.r_[np.nan, l[:-1]]
    return np.nan_to_num((h <= ph) & (l >= pl), nan=0).astype(bool), ph, pl


def fakey(df):
    """False break of the mother bar: bar i+1 breaks the inside bar's range and
    closes back inside it. Signal fires in the direction OPPOSITE the break."""
    ins, _ph, _pl = inside_bars(df)
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    ih = np.where(ins, h, np.nan); il = np.where(ins, l, np.nan)
    pih, pil = np.r_[np.nan, ih[:-1]], np.r_[np.nan, il[:-1]]
    up = (l < pil) & (c > pil)        # broke below, closed back in -> long
    dn = (h > pih) & (c < pih)        # broke above, closed back in -> short
    return np.nan_to_num(up, nan=0).astype(bool), np.nan_to_num(dn, nan=0).astype(bool)


def big_players(df, periodL=33, adxlen=14, adx_filter=True):
    """Ported from big_players_reversal_entry.txt, including its quirks.

    Note what the source actually asks for: BUY when price prints a 33-bar LOW
    while DI-minus dominates and ADX > 40. That is buying into a confirmed
    downtrend at its low. The Pine calls it a "Big Player" entry; whether the
    market agrees is the question.
    """
    c, h, l = (df[k].to_numpy(float) for k in ("close", "high", "low"))
    S = pd.Series
    e5 = S(c).ewm(span=5, adjust=False).mean().to_numpy()
    lo33 = S(l).rolling(periodL).min().to_numpy()
    hi33 = S(h).rolling(periodL).max().to_numpy()
    vl2 = S(np.where(l <= lo33, e5, 0.0)).ewm(span=3, adjust=False).mean().to_numpy() * 40
    vh2 = S(np.where(h >= hi33, e5, 0.0)).ewm(span=3, adjust=False).mean().to_numpy() * 40
    vl3 = np.where(vl2 > 100, vl2 * 0.312, vl2)
    vh3 = np.where(vh2 > 100, vh2 * 0.312, vh2)
    rising_l = np.r_[False, vl3[1:] > vl3[:-1]]
    rising_h = np.r_[False, vh3[1:] > vh3[:-1]]
    up_c = np.r_[False, c[1:] > c[:-1]]
    dn_c = np.r_[False, c[1:] < c[:-1]]
    adx, dip, dim = wilder_adx(df, adxlen)
    if adx_filter:
        L = rising_l & up_c & (adx > 40) & (dim > dip)
        Sg = rising_h & dn_c & (adx > 40) & (dim < dip)
    else:
        L, Sg = rising_l & up_c, rising_h & dn_c
    return np.nan_to_num(L, nan=0).astype(bool), np.nan_to_num(Sg, nan=0).astype(bool)


# ------------------------------------------------------------------ the tester
def forward(df, a, hz):
    """Forward close-to-close move in ATR units, per horizon."""
    c = df["close"].to_numpy(float)
    f = {}
    for k in hz:
        nxt = np.r_[c[k:], np.full(k, np.nan)]
        f[k] = (nxt - c) / a
    return f


def evaluate(name, sig, direction, f, hz):
    """Welch's t of the pattern's directional move against the unconditional one."""
    rows = []
    for k in hz:
        x = f[k] * direction
        m = sig & np.isfinite(x)
        if m.sum() < 30:
            continue
        s, u = x[m], x[np.isfinite(x)]
        se = (s.var(ddof=1) / len(s) + u.var(ddof=1) / len(u)) ** 0.5
        rows.append(dict(pattern=name, horizon=k, n=int(m.sum()),
                         mean_atr=float(s.mean()), uncond_atr=float(u.mean()),
                         edge_atr=float(s.mean() - u.mean()),
                         t=float((s.mean() - u.mean()) / se) if se > 0 else np.nan,
                         hit_rate=float((s > 0).mean())))
    return rows


def dollar_quarter(df, a):
    """Is .00 a stronger level than .25/.50/.75, as the blueprint claims?

    Strength is measured as REJECTION: of the bars whose range crosses a grid
    level, how often does the bar close back on the side it came from? A level
    that is 'strongest S/R' should reject more than a level that is 'often
    breached'. All four sub-levels are measured the same way, so the comparison
    is internal and needs no external null.
    """
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    rows = []
    for frac, tag in ((0.00, ".00"), (0.25, ".25"), (0.50, ".50"), (0.75, ".75")):
        lv = np.floor(l) + frac
        lv = np.where(lv < l, lv + 1.0, lv)          # first such level at/above the low
        touched = (lv >= l) & (lv <= h)
        # approached from below -> rejection means closing back below
        from_below = touched & (o < lv)
        from_above = touched & (o > lv)
        rej = ((from_below & (c < lv)) | (from_above & (c > lv)))
        n = int(touched.sum())
        rows.append(dict(level=tag, n_touch=n,
                         reject_rate=float(rej[touched].mean()) if n else np.nan,
                         mean_atr_at_touch=float(np.nanmean(a[touched])) if n else np.nan))
    return pd.DataFrame(rows)


def ny_open_reversal(df, loc):
    """'Major reversals happen within 30 min of NY open.'

    Operationalised: compare the |return| and the sign-flip rate of the two
    bars after 09:30 NY against the same statistics for all other bars. A
    reversal claim needs BOTH -- bigger moves alone is just a volatility fact,
    which is already well known and not tradeable on its own.
    """
    c = df["close"].to_numpy(float)
    r = np.r_[np.nan, np.diff(c)]
    mins = loc.hour * 60 + loc.minute
    win = (mins >= 9 * 60 + 30) & (mins < 10 * 60 + 30)
    prev_up = np.r_[np.nan, r[:-1]] > 0
    flip = (r > 0) != prev_up
    ok = np.isfinite(r) & np.isfinite(np.r_[np.nan, r[:-1]])
    return pd.DataFrame([
        dict(window="NY open 09:30-10:30", n=int((win & ok).sum()),
             mean_abs=float(np.nanmean(abs(r[win & ok]))),
             flip_rate=float(flip[win & ok].mean())),
        dict(window="all other bars", n=int((~win & ok).sum()),
             mean_abs=float(np.nanmean(abs(r[~win & ok]))),
             flip_rate=float(flip[~win & ok].mean())),
    ])


def main():
    from research.qt_corrected import to_local
    df = load_csv("data/xauusd_15m.csv.gz", rule="30min")
    a = atr(df)
    loc = to_local(df.index, "ny")
    f = forward(df, a, HORIZONS)

    pb, pr = pin_bars(df)
    ins, _, _ = inside_bars(df)
    fu, fd = fakey(df)
    bl, bs = big_players(df)
    bl0, bs0 = big_players(df, adx_filter=False)
    c = df["close"].to_numpy(float)
    up_bar = np.r_[False, c[1:] > c[:-1]]

    arms = [
        ("PIN_BULL", pb, +1), ("PIN_BEAR", pr, -1),
        ("INSIDE_then_up", ins & up_bar, +1), ("INSIDE_then_dn", ins & ~up_bar, -1),
        ("FAKEY_UP", fu, +1), ("FAKEY_DN", fd, -1),
        ("BIGPLAY_L_adx", bl, +1), ("BIGPLAY_S_adx", bs, -1),
        ("BIGPLAY_L_noadx", bl0, +1), ("BIGPLAY_S_noadx", bs0, -1),
    ]
    rows = []
    for nm, s, d in arms:
        rows += evaluate(nm, s, d, f, HORIZONS)
    t = pd.DataFrame(rows)

    print("=" * 100)
    print("PATTERN BATTERY -- forward move vs the UNCONDITIONAL move, in ATR")
    print("  |t| > 3 is the bar to clear. Ten arms x four horizons = 40 tests, so")
    print("  |t| around 2 is expected several times from noise alone.")
    print("=" * 100)
    print(t.to_string(index=False, float_format=lambda v: f"{v:9.4f}"))
    t.to_csv("research/source_battery.csv", index=False)

    print("\n" + "=" * 100)
    print("DOLLAR-QUARTER GRID -- blueprint says .00 strongest, .25/.75 'often breached'")
    print("=" * 100)
    dq = dollar_quarter(df, a)
    print(dq.to_string(index=False, float_format=lambda v: f"{v:10.4f}"))
    dq.to_csv("research/source_dollar_quarter.csv", index=False)

    print("\n" + "=" * 100)
    print("NY OPEN -- blueprint says major reversals within 30 min of the open")
    print("=" * 100)
    ny = ny_open_reversal(df, loc)
    print(ny.to_string(index=False, float_format=lambda v: f"{v:10.4f}"))
    ny.to_csv("research/source_ny_open.csv", index=False)

    surv = t[t.t.abs() > 3]
    print("\n" + "=" * 100)
    print(f"SURVIVORS at |t| > 3: {len(surv)} of {len(t)} tests")
    print("=" * 100)
    print(surv.to_string(index=False, float_format=lambda v: f"{v:9.4f}") if len(surv)
          else "  none -- no pattern in these sources beats its unconditional baseline.")


if __name__ == "__main__":
    main()
