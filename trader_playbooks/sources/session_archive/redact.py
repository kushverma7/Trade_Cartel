"""Credential redaction for session archives.

EXISTS BECAUSE: kushverma7/Trade_Cartel is a PUBLIC repository and session
transcripts are archived into it. On 2026-08-17 a live API key was pasted into
the conversation; without this filter the next archive would have published it.

Run EVERY transcript through redact_text() before it is written to disk.
Fail closed: if a pattern is uncertain, redact it.
"""
import re

PATTERNS = [
    (re.compile(r"\b[a-z]{2,6}_live_[A-Za-z0-9]{16,}\b"),        "[REDACTED_LIVE_KEY]"),
    (re.compile(r"\b[a-z]{2,6}_(test|sk|pk)_[A-Za-z0-9]{16,}\b"), "[REDACTED_KEY]"),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"),                   "[REDACTED_SK]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),               "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                         "[REDACTED_AWS_KEY]"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}\b"),            "[REDACTED_SLACK_TOKEN]"),
    (re.compile(r"\bey[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"),
                                                                  "[REDACTED_JWT]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
                re.S),                                            "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"\b(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{16,})['\"]?",
                re.I),                                            r"\1=[REDACTED]"),
]


def redact_text(s: str) -> str:
    for pat, rep in PATTERNS:
        s = pat.sub(rep, s)
    return s


def scan(s: str) -> list[str]:
    """Return the names of patterns that MATCH — for auditing, not redacting."""
    hits = []
    for pat, rep in PATTERNS:
        if pat.search(s):
            hits.append(rep)
    return hits


if __name__ == "__main__":
    import sys, glob, gzip, lzma, os
    bad = 0
    for f in sys.argv[1:] or glob.glob(os.path.join(os.path.dirname(__file__), "**", "*"), recursive=True):
        if not os.path.isfile(f):
            continue
        try:
            if f.endswith(".gz"):
                t = gzip.open(f, "rt", errors="replace").read()
            elif f.endswith(".xz"):
                t = lzma.open(f, "rt", errors="replace").read()
            else:
                t = open(f, errors="replace").read()
        except Exception:
            continue
        h = scan(t)
        if h:
            bad += 1
            print(f"LEAK  {f}: {', '.join(sorted(set(h)))}")
    print("clean" if not bad else f"{bad} file(s) contain credential patterns")
