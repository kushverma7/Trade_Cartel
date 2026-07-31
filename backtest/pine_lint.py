#!/usr/bin/env python3
"""
Static checks for Pine v6 files, tuned to the failure modes in this repo.

Pine's continuation rule: a line continuing the previous statement must be
indented by something that is NOT a multiple of four, because multiples of
four mean a nested block. Earlier ad-hoc versions of this check only
recognised continuations that OPEN a bracket or START with an operator, so
they raised false alarms on the common form where the previous line ENDS
with `and` / `or` / `+`. Both forms are handled here.

  python3 -m backtest.pine_lint strategies/foo.pine
"""
import re, sys, collections

# A line CONTINUES onto the next when it ends with a dangling operator or an
# open bracket. Two traps this must avoid:
#   - `=>` ends a FUNCTION HEADER, which opens a block, not a continuation
#   - the check must run on the line WITH its strings intact, or
#     `if x == "foo"` reduces to `if x ==` and looks like a continuation
CONT_END = re.compile(r'(\b(and|or|not)|[+\-*/,?:<>]|(?<![=<>!])=|\()\s*$')
BLOCK_END = re.compile(r'=>\s*$')


def continues(line_no_comment):
    t = line_no_comment.rstrip()
    if not t or BLOCK_END.search(t):
        return False
    return bool(CONT_END.search(t))


def lint(path):
    src = open(path).read().split('\n')
    problems = []

    decls = collections.defaultdict(list)
    pat = re.compile(r'^(?:var\s+)?(?:(?:bool|int|float|string|color|line|label|table)\s+)?([A-Za-z_]\w*)\s*=(?!=)')
    depth = 0
    prev_code = ""
    prev_raw = ""
    for i, l in enumerate(src, 1):
        st = l.strip()
        if not st or st.startswith('//'):
            continue
        ind = len(l) - len(l.lstrip(' '))
        code = re.sub(r'"(?:[^"\\]|\\.)*"', '', l).split('//')[0]

        is_cont = depth > 0 or continues(prev_raw) or st[0] in '+-?:,)'
        if is_cont:
            if ind and ind % 4 == 0:
                problems.append((i, "continuation at a multiple-of-4 indent "
                                    "(Pine reads it as a new block)", st[:60]))
        elif ind % 4:
            problems.append((i, "block indent is not a multiple of 4", st[:60]))

        if ind == 0 and not is_cont:
            m = pat.match(st)
            if m:
                decls[m.group(1)].append(i)
            t = re.match(r'^\[([^\]]+)\]\s*=', st)
            if t:
                for n in t.group(1).split(','):
                    decls[n.strip()].append(i)

        if re.match(r'^(if |for |else$|else\s|while )', st) or st.rstrip().endswith('=>'):
            j = i
            while j < len(src) and (not src[j].strip() or src[j].strip().startswith('//')):
                j += 1
            if j >= len(src) or (len(src[j]) - len(src[j].lstrip())) <= ind:
                problems.append((i, "block header with no body", st[:60]))

        depth += code.count('(') + code.count('[') - code.count(')') - code.count(']')
        depth = max(depth, 0)
        prev_code = code
        prev_raw = l.split('//')[0]

    for k, v in decls.items():
        if len(v) > 1:
            problems.append((v[1], f"duplicate top-level declaration of {k!r} "
                                   f"(also at line {v[0]})", ""))

    for i, l in enumerate(src, 1):
        if 'strategy.exit(' in l and 'limit=' in l and 'stop=' not in l \
                and not l.strip().startswith('//'):
            problems.append((i, "strategy.exit with a limit but NO stop (BUG-014)", l.strip()[:60]))

    if depth != 0:
        problems.append((len(src), f"file ends with unbalanced delimiters ({depth})", ""))
    return problems


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        probs = lint(p)
        print(f"{p}: {'CLEAN' if not probs else str(len(probs)) + ' problem(s)'}")
        for ln, msg, txt in probs:
            print(f"   line {ln}: {msg}")
            if txt:
                print(f"      {txt}")
        bad += len(probs)
    sys.exit(1 if bad else 0)
