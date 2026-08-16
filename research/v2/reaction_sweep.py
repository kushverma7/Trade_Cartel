import sys, math, itertools, random, datetime as dt, statistics as st, pickle
sys.path.insert(0, "/home/user/Trade_Cartel/research/v2")
import reaction as R, engine

D = R.D
SPLIT = dt.date(2025, 1, 1)
IS = [d for d in D.days if d < SPLIT]
OOS = [d for d in D.days if d >= SPLIT]
print(f"[reaction] IS {len(IS)} sessions ({IS[0]}..{IS[-1]})   OOS {len(OOS)} ({OOS[0]}..{OOS[-1]})")

GRID = dict(
    min_conf = [0, 1, 2, 3, 4, 5, 6],
    mode     = ["close", "next", "retest"],
    setup    = ["break", "rejection", "both"],
    zone     = [10.0, 25.0, 40.0],
    target   = ["next", "R"],
    rr       = [2.0],
)
keys = list(GRID)
combos = [dict(zip(keys, c)) for c in itertools.product(*(GRID[k] for k in keys))]
# the R-multiple target needs its own rr values; expand only those cells
extra = []
for c in combos:
    if c["target"] == "R":
        for v in (1.5, 3.0):
            e = dict(c); e["rr"] = v; extra.append(e)
combos = combos + extra
print(f"[reaction] {len(combos)} cells")

res = []
for n, c in enumerate(combos):
    m = engine.metrics(R.run(days=IS, **c), min_n=60)
    if m:
        res.append((c, m))
    if n % 30 == 0:
        print(f"  .. {n+1}/{len(combos)}  kept {len(res)}", flush=True)

K = len(res)
BAR = math.sqrt(2 * math.log(K)) if K > 1 else 0
res.sort(key=lambda r: -r[1]["t"])
print(f"\n[reaction] {K} cells with >=60 IS trades.  bar t >= {BAR:.2f}")
print(f"[reaction] clearing it: {sum(1 for _, m in res if m['t'] >= BAR)}")
print(f"[reaction] PF > 1.0   : {sum(1 for _, m in res if m['pf'] > 1.0)} of {K} "
      f"({100*sum(1 for _,m in res if m['pf']>1.0)/K:.1f}%)")

print("\nTOP 12 BY IN-SAMPLE t, out-of-sample beside it")
print(f"{'conf':>4} {'mode':7} {'setup':10} {'zone':>5} {'target':7} | {'IS n':>5} {'IS PF':>6} "
      f"{'IS win':>6} {'IS t':>6} | {'OOS n':>5} {'OOS PF':>6} {'OOS t':>6}")
for c, m in res[:12]:
    mo = engine.metrics(R.run(days=OOS, **c), min_n=20)
    tg = c["target"] if c["target"] == "next" else f"{c['rr']}R"
    print(f"{c['min_conf']:>4} {c['mode']:7} {c['setup']:10} {c['zone']:>5.0f} {tg:7} | "
          f"{m['n']:>5} {m['pf']:>6.3f} {m['win']:>5.1f}% {m['t']:>6.2f} | " +
          (f"{mo['n']:>5} {mo['pf']:>6.3f} {mo['t']:>6.2f}" if mo else f"{'--':>5} {'--':>6} {'--':>6}"))

print("\n" + "=" * 78)
print("DOES THE SECTION-14 CHECKLIST HELP?  full sample, everything else fixed")
print("=" * 78)
for mode in ("close", "next", "retest"):
    print(f"  trigger = {mode}")
    for mc in range(0, 7):
        m = engine.metrics(R.run(min_conf=mc, mode=mode, setup="both"), min_n=40, strict=False)
        if m:
            print(f"    confirmations >= {mc}: n={m['n']:5d} PF={m['pf']:6.3f} "
                  f"win={m['win']:5.1f}% net={m['net']:+9.1f} avg={m['avg']:+6.2f} t={m['t']:+6.2f}")

print("\n" + "=" * 78)
print("DOES THE RETEST RULE (section 6) EARN ITS KEEP?  full sample, conf>=2")
print("=" * 78)
for mode in ("close", "next", "retest"):
    for setup in ("break", "rejection", "both"):
        m = engine.metrics(R.run(min_conf=2, mode=mode, setup=setup), min_n=40, strict=False)
        if m:
            print(f"  {mode:7} / {setup:10} n={m['n']:5d} PF={m['pf']:6.3f} win={m['win']:5.1f}% "
                  f"net={m['net']:+9.1f} t={m['t']:+6.2f} yrs+={m['yp']}/{m['ny']}")

print("\n" + "=" * 78)
print("GROSS vs NET — is this a cost problem or a signal problem?")
print("=" * 78)
for mode in ("close", "retest"):
    for cst in (0.0, 2.0, 3.0):
        m = engine.metrics(R.run(min_conf=2, mode=mode, cost=cst), min_n=40, strict=False)
        if m:
            print(f"  {mode:7} cost {cst:>3.1f}  n={m['n']:5d} PF={m['pf']:6.3f} "
                  f"avg={m['avg']:+6.3f} t={m['t']:+6.2f}")

print("\n" + "=" * 78)
print("DIRECTION FLIP — if the rules are backwards, the inverse should work")
print("=" * 78)
for mode in ("close", "next", "retest"):
    a = engine.metrics(R.run(min_conf=2, mode=mode), min_n=40, strict=False)
    b = engine.metrics(R.run(min_conf=2, mode=mode, flip=True), min_n=40, strict=False)
    if a and b:
        print(f"  {mode:7} as written PF={a['pf']:6.3f} t={a['t']:+6.2f}   "
              f"inverted PF={b['pf']:6.3f} t={b['t']:+6.2f}")

pickle.dump((res, BAR), open("/home/user/Trade_Cartel/research/v2/reaction_is.pkl", "wb"))
