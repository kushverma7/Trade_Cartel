"""Everything in the repository about Quarters Theory / Quarterly Theory, in one PDF.

Primary sources, distilled playbooks, code engines and research scripts are reproduced
IN FULL. Every remaining file that mentions the theory contributes context extracts
(±15 lines around each hit, overlapping windows merged) so no reference is missed.

Same exactness guarantees as the other builders: full-Unicode monospace, hard wrap at
the column width, render-time assertion that unwrapping reproduces the source exactly.
"""
import os, re, glob, collections, unicodedata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter
from fontTools.ttLib import TTFont as FTFont

REPO = "/home/user/Trade_Cartel"
SRC = f"{REPO}/trader_playbooks/sources"
OUT = "/tmp/claude-0/-home-user-Trade-Cartel/af36979e-ba34-557a-a8b0-0a27e52e3758/scratchpad/qt"
os.makedirs(OUT, exist_ok=True)
DEST = f"{REPO}/Trade_Cartel_Quarters_Theory_Complete.pdf"

FDIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("Mono", f"{FDIR}/DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("Sans", f"{FDIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", f"{FDIR}/DejaVuSans-Bold.ttf"))
CMAP = set()
for t in FTFont(f"{FDIR}/DejaVuSansMono.ttf")["cmap"].tables:
    CMAP |= set(t.cmap.keys())

W, H = A4
ML, MR, MT, MB = 15*mm, 13*mm, 18*mm, 16*mm
TW = W - ML - MR
BODY, LEAD = 6.9, 8.6
COLS = int(TW / stringWidth("M", "Mono", BODY))
INK, MUTED, RULE = HexColor("#15181C"), HexColor("#6B7280"), HexColor("#D8DBE0")
HILITE, ACCENT, SECTBG = HexColor("#FFE9A8"), HexColor("#8A6D1F"), HexColor("#15181C")

FALLBACK = {"❌": "x", "✅": "✓", "\U0001f534": "o", "\U0001f7e2": "o", "\U0001f7e1": "o",
            "⎯": "—", "⁄": "/", "⭐": "*", "\U0001f4c8": "^", "\U0001f4c9": "v",
            "\U0001f4a1": "!", "\U0001f525": "!"}
INVISIBLE = {"​", "‎", "‏", "️", "﻿", "­", "\x7f", "\x00"}
SUBS = collections.Counter()

QT = re.compile(r"quarters?\s+theory|quarterly\s+theory|yotov|by\s+daye|true\s+open|"
                r"90.?minute\s+quarter|quarter(ly)?\s+(cycle|wood)|\bQ1\b.*\bQ2\b", re.I)

PRIMARY = [
    (f"{SRC}/raw_transcripts/line1248_2026-07-20.txt",
     "Daye — Introduction to Quarterly Theory (live stream, verbatim)"),
    (f"{SRC}/raw_transcripts/line3375_2026-07-20.txt",
     "Ilan Yotov — The Quarters Theory (author webinar, verbatim)"),
    (f"{SRC}/quarterly_theory_daye_compiled_ransh2806.txt",
     "Quarterly Theory by Daye — compiled notes (ransh2806), extracted text"),
    (f"{SRC}/yotov_quarters_theory_2012_glossary.txt",
     "Ilan Yotov — The Quarters Theory (2012), glossary and terms"),
    (f"{SRC}/gold_scalping_strategy_blueprint.txt",
     "Gold Scalping Strategy Blueprint (built on Quarterly Theory)"),
]
PRIMARY_PDF = [
    (f"{SRC}/quarterly_theory_daye_compiled.pdf", "Quarterly Theory by Daye — compiled (original PDF)"),
    (f"{SRC}/quarterly_theory_daye_compiled_ransh2806.pdf", "Quarterly Theory by Daye — ransh2806 compilation (original PDF)"),
]
PLAYBOOKS = [
    (f"{REPO}/trader_playbooks/quarterly_theory.md", "Quarterly Theory — distilled playbook"),
    (f"{REPO}/trader_playbooks/yotov_quarters_theory.md", "Yotov Quarters Theory — distilled playbook"),
]
ENGINES = [(p, f"{os.path.basename(p)} — Pine engine") for p in [
    f"{REPO}/indicators/quarterly_theory_engine.pine",
    f"{REPO}/indicators/quarters_theory_price_engine.pine",
    f"{REPO}/indicators/spaceman_daye_quarters_engine.pine",
    f"{REPO}/indicators/spaceman_yotov_quarters_engine.pine"] if os.path.isfile(p)]
RESEARCH = [(p, f"{os.path.basename(p)} — research script") for p in sorted(
    glob.glob(f"{REPO}/research/qt_*.py") + glob.glob(f"{REPO}/research/levels_qt.py"))]

FULL = {p for p, _ in PRIMARY + PLAYBOOKS + ENGINES + RESEARCH} | {p for p, _ in PRIMARY_PDF}


def prep(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x0c", "\n")
    out = []
    for ch in text:
        if ch == "\n":
            out.append(ch); continue
        if ch == "\t":
            out.append("    "); continue
        if ch in INVISIBLE:
            SUBS[(ch, "(removed: invisible control)")] += 1; continue
        if ord(ch) in CMAP:
            out.append(ch); continue
        if ch in FALLBACK:
            SUBS[(ch, FALLBACK[ch])] += 1; out.append(FALLBACK[ch]); continue
        if 0xE000 <= ord(ch) <= 0xF8FF:
            SUBS[(ch, "·")] += 1; out.append("·"); continue
        d = "".join(c for c in unicodedata.normalize("NFKD", ch) if ord(c) in CMAP)
        rep = d if d else "?"
        SUBS[(ch, rep)] += 1; out.append(rep)
    return "".join(out)


def hardwrap(text, cols):
    lines, spans = [], []
    for s in text.split("\n"):
        if not s:
            lines.append(""); spans.append(1); continue
        n = 0
        for i in range(0, len(s), cols):
            lines.append(s[i:i+cols]); n += 1
        spans.append(n)
    return lines, spans


def verify(text, lines, spans):
    out, i = [], 0
    for n in spans:
        out.append("".join(lines[i:i+n])); i += n
    return "\n".join(out) == text


def footer(c, page):
    c.setStrokeColor(RULE); c.setLineWidth(.4)
    c.line(ML, MB + 6*mm, W - MR, MB + 6*mm)
    c.setFont("Sans", 6.5); c.setFillColor(MUTED)
    c.drawString(ML, MB + 2*mm, "Trade Cartel — Quarters Theory, Complete")
    c.drawRightString(W - MR, MB + 2*mm, str(page))


def title_band(c, y, title, fname, note=None):
    lines, cur = [], ""
    for w in title.split(" "):
        t = w if not cur else cur + " " + w
        if stringWidth(t, "Sans-Bold", 13.5) <= TW - 10*mm:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    bh = len(lines) * 18 + 14
    c.setFillColor(HILITE); c.rect(ML, y - bh + 6, TW, bh, fill=1, stroke=0)
    c.setFillColor(ACCENT); c.rect(ML, y - bh + 6, 2.5*mm, bh, fill=1, stroke=0)
    c.setFillColor(INK); c.setFont("Sans-Bold", 13.5)
    ty = y - 13
    for ln in lines:
        c.drawString(ML + 6*mm, ty, ln); ty -= 18
    y -= bh + 4
    c.setFont("Sans", 7); c.setFillColor(MUTED)
    c.drawString(ML, y, fname); y -= 10
    if note:
        c.setFont("Sans", 7); c.setFillColor(ACCENT)
        c.drawString(ML, y, note); y -= 11
    return y - 4


def render(dest, title, fname, raw, note=None):
    text = prep(raw)
    lines, spans = hardwrap(text, COLS)
    assert verify(text, lines, spans), f"content check FAILED: {fname}"
    c = canvas.Canvas(dest, pagesize=A4)
    page = 1
    y = title_band(c, H - MT, title, fname, note)
    for ln in lines:
        if y < MB + 12*mm:
            footer(c, page); c.showPage(); page += 1; y = H - MT
        c.setFont("Mono", BODY); c.setFillColor(INK)
        c.drawString(ML, y, ln); y -= LEAD
    footer(c, page); c.save()
    return dest, len(text)


def cover_for_pdf(dest, title, fname, n):
    c = canvas.Canvas(dest, pagesize=A4)
    title_band(c, H - MT, title, fname, f"Original PDF reproduced verbatim — {n} pages follow")
    footer(c, 1); c.save()
    return dest


def section_page(dest, name, sub=""):
    c = canvas.Canvas(dest, pagesize=A4)
    c.setFillColor(SECTBG); c.rect(0, H/2 - 32*mm, W, 64*mm, fill=1, stroke=0)
    c.setFillColor(HILITE); c.setFont("Sans-Bold", 21)
    c.drawCentredString(W/2, H/2 + 2*mm, name)
    c.setFillColor(HexColor("#9CA3AF")); c.setFont("Sans", 8.5)
    if sub:
        c.drawCentredString(W/2, H/2 - 9*mm, sub)
    c.save()
    return dest


items, n, chars = [], 0, 0


def add_section(name, sub=""):
    global n
    items.append(("SEC", name, None, [section_page(f"{OUT}/s{n}.pdf", name, sub)], 1)); n += 1


def add_doc(title, fname, raw, note=None):
    global n, chars
    d, c = render(f"{OUT}/i{n}.pdf", title, fname, raw, note); n += 1
    chars += c
    items.append(("DOC", title, fname, [d], len(PdfReader(d).pages)))


def rd(p):
    return open(p, encoding="utf-8", errors="replace").read()


add_section("Primary Sources", "the material you supplied, verbatim and complete")
for p, t in PRIMARY:
    if os.path.isfile(p):
        add_doc(t, os.path.basename(p), rd(p))
for p, t in PRIMARY_PDF:
    if not os.path.isfile(p):
        continue
    r = PdfReader(p)
    if r.is_encrypted:
        try: r.decrypt("")
        except Exception: pass
    cov = cover_for_pdf(f"{OUT}/c{n}.pdf", t, os.path.basename(p), len(r.pages)); n += 1
    items.append(("DOC", t, os.path.basename(p), [cov, p], 1 + len(r.pages)))

add_section("Distilled Playbooks", "what was extracted from the sources above")
for p, t in PLAYBOOKS:
    if os.path.isfile(p):
        add_doc(t, os.path.basename(p), rd(p))

if ENGINES:
    add_section("Pine Engines", "the theory implemented as chart code")
    for p, t in ENGINES:
        add_doc(t, os.path.basename(p), rd(p))

if RESEARCH:
    add_section("Research Scripts", "how the theory was tested")
    for p, t in RESEARCH:
        add_doc(t, os.path.basename(p), rd(p))

# ---------- every remaining reference, in context ----------
cands = []
for p in glob.glob(f"{REPO}/**/*", recursive=True):
    if not os.path.isfile(p) or p in FULL:
        continue
    if "/node_modules/" in p or "/.git/" in p or "/.claude/" in p:
        continue
    if not p.lower().endswith((".md", ".txt", ".pine", ".py", ".csv")):
        continue
    cands.append(p)

extract_docs, CTX = [], 15
for p in sorted(cands):
    try: lines = rd(p).split("\n")
    except Exception: continue
    hits = [i for i, ln in enumerate(lines) if QT.search(ln)]
    if not hits:
        continue
    wins = []
    for i in hits:
        a, b = max(0, i - CTX), min(len(lines), i + CTX + 1)
        if wins and a <= wins[-1][1]:
            wins[-1] = (wins[-1][0], max(wins[-1][1], b))
        else:
            wins.append((a, b))
    out = [f"{os.path.relpath(p, REPO)}", "=" * COLS,
           f"{len(hits)} reference(s), shown with {CTX} lines of context either side.", ""]
    for a, b in wins:
        out.append(f"--- lines {a+1}-{b} " + "-" * max(0, COLS - 20))
        for j in range(a, b):
            mark = ">>" if j in hits else "  "
            out.append(f"{mark}{j+1:6d} | {lines[j]}")
        out.append("")
    extract_docs.append((os.path.relpath(p, REPO), len(hits), "\n".join(out)))

add_section("Every Other Reference", f"{len(extract_docs)} further files, each hit shown in context")
for rel, nh, body in extract_docs:
    add_doc(rel, f"{nh} reference(s)", body)

if SUBS:
    app = ["SUBSTITUTION LOG", "=" * COLS, "",
           f"{'CODEPOINT':<12}{'NAME':<44}{'REPLACED WITH':<32}{'COUNT':>8}", "-" * COLS]
    for (ch, rep), cnt in sorted(SUBS.items(), key=lambda kv: -kv[1]):
        try: nm = unicodedata.name(ch)
        except ValueError: nm = "(unnamed control / private use)"
        app.append(f"U+{ord(ch):04X}{'':<6}{nm[:43]:<44}{rep[:31]:<32}{cnt:>8}")
    app += ["-" * COLS, "", f"total substitutions: {sum(SUBS.values())}"]
    add_section("Appendix")
    add_doc("Substitution Log", "(generated)", "\n".join(app))

ndocs = sum(1 for k, *_ in items if k == "DOC")
bodypages = sum(it[4] for it in items)
per = 42
ntoc = max(1, -(-len(items) // per))
front = 1 + ntoc
start, acc = {}, front + 1
for i, it in enumerate(items):
    start[i] = acc; acc += it[4]

fc = canvas.Canvas(f"{OUT}/_front.pdf", pagesize=A4)
fc.setFillColor(SECTBG); fc.rect(0, 0, W, H, fill=1, stroke=0)
fc.setFillColor(HILITE); fc.rect(ML, H - 100*mm, 52*mm, 3*mm, fill=1, stroke=0)
fc.setFillColor(HexColor("#FFFFFF")); fc.setFont("Sans-Bold", 27)
fc.drawString(ML, H - 92*mm, "Quarters Theory")
fc.setFillColor(HILITE); fc.setFont("Sans-Bold", 22)
fc.drawString(ML, H - 113*mm, "Everything, Complete")
fc.setFillColor(HexColor("#9CA3AF")); fc.setFont("Sans", 9.5)
for i, s in enumerate([
        "Both source lineages — Daye's Quarterly Theory and Ilan Yotov's",
        "Quarters Theory — with every transcript, compiled PDF, glossary,",
        "playbook, Pine engine and research script reproduced in full.",
        "",
        "Every remaining file in the repository that mentions the theory",
        "contributes its references with fifteen lines of context either side,",
        "so nothing is left out."]):
    fc.drawString(ML, H - 134*mm - i*7*mm, s)
fc.setFillColor(HILITE); fc.setFont("Sans-Bold", 11)
fc.drawString(ML, H - 192*mm, f"{ndocs} documents     {bodypages + front} pages")
fc.showPage()

i = 0
for pg in range(ntoc):
    fc.setFillColor(INK); fc.setFont("Sans-Bold", 15)
    fc.drawString(ML, H - MT, "Contents")
    fc.setStrokeColor(RULE); fc.setLineWidth(.6)
    fc.line(ML, H - MT - 5*mm, W - MR, H - MT - 5*mm)
    y = H - MT - 13*mm
    while i < len(items) and y > MB + 9*mm:
        kind, t, base, _, _ = items[i]; p = start[i]; i += 1
        if kind == "SEC":
            y -= 3*mm
            fc.setFillColor(HILITE); fc.rect(ML, y - 1.5*mm, TW, 6*mm, fill=1, stroke=0)
            fc.setFillColor(INK); fc.setFont("Sans-Bold", 9)
            fc.drawString(ML + 2*mm, y + .6*mm, t.upper())
            fc.drawRightString(W - MR - 2*mm, y + .6*mm, str(p)); y -= 9*mm
        else:
            fc.setFillColor(INK); fc.setFont("Sans", 8.2)
            s = t
            while stringWidth(s, "Sans", 8.2) > TW - 18*mm and len(s) > 8:
                s = s[:-2]
            fc.drawString(ML + 3*mm, y, s)
            fc.setFillColor(MUTED); fc.drawRightString(W - MR, y, str(p)); y -= 5.4*mm
    fc.setFont("Sans", 6.5); fc.setFillColor(MUTED)
    fc.drawRightString(W - MR, MB + 2*mm, str(pg + 2))
    fc.showPage()
fc.save()

w = PdfWriter()
for p in PdfReader(f"{OUT}/_front.pdf").pages:
    w.add_page(p)
for it in items:
    for s in it[3]:
        r = PdfReader(s)
        if r.is_encrypted:
            try: r.decrypt("")
            except Exception: pass
        for p in r.pages:
            w.add_page(p)
parent = None
for idx, (kind, t, base, _, _) in enumerate(items):
    if kind == "SEC":
        parent = w.add_outline_item(t, start[idx] - 1)
    else:
        w.add_outline_item(t, start[idx] - 1, parent=parent)
w.add_metadata({"/Title": "Trade Cartel - Quarters Theory, Complete", "/Author": "Trade Cartel"})
with open(DEST, "wb") as f:
    w.write(f)
print(f"documents {ndocs}   pages {len(PdfReader(DEST).pages)}   {os.path.getsize(DEST)/1048576:.1f} MB")
print(f"full-text sources {len(FULL)}   context-extract files {len(extract_docs)}   "
      f"characters typeset {chars}   substitutions {sum(SUBS.values())}")
