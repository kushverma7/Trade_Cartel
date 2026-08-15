import itertools, math, pickle, sys
sys.path.insert(0,'research')
import body_break_sweep as S

def sweep(mode):
    S.DO_MODE = mode
    combos = list(itertools.product(["A","B"],[False,True],[False],[11,12,13,14,16],S.STOPS,S.TPS))
    res=[]
    for (lg,fl,os_,eh,sk,tk) in combos:
        m=S.metrics(S.run(lg,fl,os_,eh,sk,tk))
        if m: res.append((dict(logic=lg,flip=fl,endHour=eh,stop=sk,tp=tk),m))
    res.sort(key=lambda r:-r[1]['t'])
    return res

for mode,desc in [("strict","STRICT — 09:50 bar required (as the script specifies)"),
                  ("proxy","PROXY — daily open taken from the session's first bar [DEVIATION]")]:
    res=sweep(mode)
    K=len(res); bar=math.sqrt(2*math.log(K)) if K>1 else 0
    print(f"\n{'='*100}\n{desc}\n{K} cells with >=30 trades   multiple-testing bar t >= {bar:.2f}")
    print(f"{'logic':5} {'flip':5} {'end':>3} {'stop':10} {'tp':11} {'n':>5} {'PF':>6} {'win%':>5} {'net':>8} {'avgR':>7} {'maxDD':>7} {'MAR':>6} {'t':>6} {'yrs+':>5}")
    for c,m in res[:10]:
        print(f"{c['logic']:5} {str(c['flip']):5} {c['endHour']:>3} {c['stop']:10} {c['tp']:11} {m['n']:>5} "
              f"{m['pf']:>6.3f} {m['win']:>5.1f} {m['net']:>8.1f} {m['avgR']:>7.3f} {m['dd']:>7.1f} {m['mar']:>6.2f} {m['t']:>6.2f} {m['yp']}/{m['ny']}")
    print(f"  clearing the bar: {sum(1 for _,m in res if m['t']>=bar)} of {K}")
    print(f"  PF > 1.0        : {sum(1 for _,m in res if m['pf']>1.0)} of {K} ({100*sum(1 for _,m in res if m['pf']>1.0)/K:.1f}%)")
    pickle.dump(res,open(f"/tmp/claude-0/-home-user-Trade-Cartel/af36979e-ba34-557a-a8b0-0a27e52e3758/scratchpad/bb_{mode}.pkl","wb"))
