"""Companion volume: every spoken-word source (live streams, webinars, YouTube videos,
mentor calls, podcast interviews), the conversation archive, and the distilled playbooks
and working documents that the source-corpus volume did not cover.

Same exactness guarantees as build_corpus_pdf_exact.py: full-Unicode monospace, hard wrap
at the column width, and a render-time assertion that unwrapping reproduces the source
character-for-character.
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
OUT = "/tmp/claude-0/-home-user-Trade-Cartel/af36979e-ba34-557a-a8b0-0a27e52e3758/scratchpad/tr"
os.makedirs(OUT, exist_ok=True)
DEST = f"{REPO}/Trade_Cartel_Transcripts_And_Lessons.pdf"

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

# ---- attribution, from trader_playbooks/sources/session_archive/03_source_audit_reports.md ----
TRANSCRIPTS = {
 "line0878_2026-07-19.txt": ("PBD Method — Shortcut Logic (narrated, AI-translated from German)", "pbd_logic.md"),
 "line0896_2026-07-19.txt": ("Fabio Valentini — Podcast Interview (Robbins World Cup rankings)", "valentini_scalping.md"),
 "line0916_2026-07-19.txt": ("Fabio Valentini — Chart Fanatics episode (full scalping showcase)", "valentini_scalping.md / orderflow_effort_result.md"),
 "line1000_2026-07-19.txt": ("Valentini / DeepCharts — Order Flow Foundations (teaching video)", "orderflow_effort_result.md"),
 "line1019_2026-07-19.txt": ("Fabio Valentini — Words of Wisdom podcast, live NY-session order-flow scalping", "valentini_scalping.md (v3)"),
 "line1032_2026-07-19.txt": ("DeepCharts / Valentini — short promo cut", "orderflow_effort_result.md"),
 "line1048_2026-07-19.txt": ("Kurisko — Bull Flag with Stochastics (quad rotation)", "kurisko_quad_rotation.md"),
 "line1142_2026-07-19.txt": ("Jim Roppel — hedge fund manager, quickfire gauntlet interview", "roppel_trend_following.md"),
 "line1154_2026-07-19.txt": ("\"Are You Actually a Price Action Trader?\" — price action vs. concepts", "pure_pa_smc.md"),
 "line1170_2026-07-19.txt": ("Dave — Market Structure, part 1 ($700 to $89,000, publicly verified)", "dave_market_structure.md"),
 "line1187_2026-07-19.txt": ("Dave — Market Structure, part 2 (chart walkthrough)", "dave_market_structure.md"),
 "line1200_2026-07-19.txt": ("Dave — Market Structure, part 3 (internal swings, psychology)", "dave_market_structure.md"),
 "line1248_2026-07-20.txt": ("Daye — Introduction to Quarterly Theory (live stream)", "quarterly_theory.md"),
 "line1291_2026-07-20.txt": ("Steve / MMM4x — Day 1 Live Seminar (market maker cycle)", "steve_mm_cycle.md"),
 "line1427_2026-07-20.txt": ("Renko / Heikin-Ashi ABC Scalper — mentor call with student John", "renko_ha_abc_scalper.md"),
 "line1527_2026-07-20.txt": ("Brandon Wendell (Online Trading Academy) — Supply and Demand", "wendell_supply_demand.md"),
 "line1582_2026-07-20.txt": ("Introduction to the Forex Master Pattern", "fx_master_pattern.md"),
 "line1625_2026-07-20.txt": ("Steve / MMM4x — Nick & GP mentoring call (MM cycle v2)", "steve_mm_cycle.md"),
 "line1675_2026-07-20.txt": ("\"Forex James\" — How Market Makers Manipulate Retail", "steve_mm_cycle.md (rejected)"),
 "line1694_2026-07-20.txt": ("\"Forex James\" — Beating Market Makers / broker selection", "steve_mm_cycle.md (rejected)"),
 "line3375_2026-07-20.txt": ("Ilan Yotov — The Quarters Theory (author webinar)", "yotov_quarters_theory.md"),
}


def prep(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x0c", "\n")
    out = []
    for ch in text:
        if ch == "\n":
            out.append(ch); continue
        if ch == "\t":
            out.append("    "); continue
        if ch in INVISIBLE:
            SUBS[(ch, "(removed: invisible control character)")] += 1; continue
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
    for src in text.split("\n"):
        if not src:
            lines.append(""); spans.append(1); continue
        n = 0
        for i in range(0, len(src), cols):
            lines.append(src[i:i+cols]); n += 1
        spans.append(n)
    return lines, spans


def verify(text, lines, spans):
    rebuilt, i = [], 0
    for n in spans:
        rebuilt.append("".join(lines[i:i+n])); i += n
    return "\n".join(rebuilt) == text


def footer(c, page):
    c.setStrokeColor(RULE); c.setLineWidth(.4)
    c.line(ML, MB + 6*mm, W - MR, MB + 6*mm)
    c.setFont("Sans", 6.5); c.setFillColor(MUTED)
    c.drawString(ML, MB + 2*mm, "Trade Cartel — Transcripts, Lessons and Working Documents")
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


def render_item(dest, title, fname, raw, note=None):
    text = prep(raw)
    lines, spans = hardwrap(text, COLS)
    assert verify(text, lines, spans), f"content check FAILED for {fname}"
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


def section_page(dest, name, sub=""):
    c = canvas.Canvas(dest, pagesize=A4)
    c.setFillColor(SECTBG); c.rect(0, H/2 - 32*mm, W, 64*mm, fill=1, stroke=0)
    c.setFillColor(HILITE); c.setFont("Sans-Bold", 22)
    c.drawCentredString(W/2, H/2 + 2*mm, name)
    c.setFillColor(HexColor("#9CA3AF")); c.setFont("Sans", 8.5)
    if sub:
        c.drawCentredString(W/2, H/2 - 9*mm, sub)
    c.save()
    return dest


def pretty(path):
    stem = re.sub(r"\.[A-Za-z0-9]+$", "", os.path.basename(path))
    t = stem.replace("_", " ").replace("-", " ").strip()
    return t[:1].upper() + t[1:]


# ---------------- build ----------------
tr_files = sorted(glob.glob(f"{SRC}/raw_transcripts/*"))
conv = sorted(glob.glob(f"{SRC}/session_archive/*.md"))
books = sorted(glob.glob(f"{REPO}/trader_playbooks/*.md"))
work = sorted(glob.glob(f"{REPO}/*.md"))

items, n, chars = [], 0, 0


def add_section(name, sub):
    global n
    items.append(("SEC", name, None, section_page(f"{OUT}/s{n}.pdf", name, sub), 1)); n += 1


def add_doc(title, fname, raw, note=None):
    global n, chars
    d, c = render_item(f"{OUT}/i{n}.pdf", title, fname, raw, note); n += 1
    chars += c
    items.append(("DOC", title, fname, d, len(PdfReader(d).pages)))


add_section("Live Streams, Webinars and Video Transcripts",
            f"{len(tr_files)} spoken-word sources, verbatim")
for f in tr_files:
    base = os.path.basename(f)
    title, playbook = TRANSCRIPTS.get(base, (pretty(f), None))
    note = f"distilled into {playbook}" if playbook else None
    add_doc(title, base, open(f, encoding="utf-8", errors="replace").read(), note)

add_section("Conversation Archive", f"{len(conv)} session records, including verbatim user turns")
for f in conv:
    add_doc(pretty(f), os.path.basename(f), open(f, encoding="utf-8", errors="replace").read())

add_section("Distilled Playbooks", f"{len(books)} playbooks built from the sources above")
for f in books:
    add_doc(pretty(f), os.path.basename(f), open(f, encoding="utf-8", errors="replace").read())

add_section("Working Documents", f"{len(work)} operating records, ledgers and protocols")
for f in work:
    add_doc(pretty(f), os.path.basename(f), open(f, encoding="utf-8", errors="replace").read())

if SUBS:
    app = ["SUBSTITUTION LOG", "=" * COLS, "",
           "Every character was rendered as-is except those below, which the font has no",
           "glyph for. Each was replaced with a same-width stand-in so alignment survives.",
           "", f"{'CODEPOINT':<12}{'NAME':<44}{'REPLACED WITH':<32}{'COUNT':>8}", "-" * COLS]
    for (ch, rep), cnt in sorted(SUBS.items(), key=lambda kv: -kv[1]):
        try: nm = unicodedata.name(ch)
        except ValueError: nm = "(unnamed control / private use)"
        app.append(f"U+{ord(ch):04X}{'':<6}{nm[:43]:<44}{rep[:31]:<32}{cnt:>8}")
    app += ["-" * COLS, "", f"distinct characters substituted : {len(SUBS)}",
            f"total substitutions             : {sum(SUBS.values())}",
            f"total characters typeset        : {chars}"]
    add_section("Appendix", "substitution log")
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
fc.drawString(ML, H - 92*mm, "Trade Cartel")
fc.setFillColor(HILITE); fc.setFont("Sans-Bold", 24)
fc.drawString(ML, H - 114*mm, "Transcripts & Lessons")
fc.setFillColor(HexColor("#9CA3AF")); fc.setFont("Sans", 9.5)
for i, s in enumerate([
        "Every live stream, webinar, YouTube lesson, mentor call and podcast",
        "interview in the repository — each attributed to its speaker and to the",
        "playbook it was distilled into.",
        "",
        "Plus the conversation archive, all 35 distilled playbooks, and the",
        "working documents: ledgers, registers and protocols."]):
    fc.drawString(ML, H - 136*mm - i*7*mm, s)
fc.setFillColor(HILITE); fc.setFont("Sans-Bold", 11)
fc.drawString(ML, H - 190*mm, f"{ndocs} documents     {bodypages + front} pages")
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
    for p in PdfReader(it[3]).pages:
        w.add_page(p)
parent = None
for idx, (kind, t, base, _, _) in enumerate(items):
    if kind == "SEC":
        parent = w.add_outline_item(t, start[idx] - 1)
    else:
        w.add_outline_item(t, start[idx] - 1, parent=parent)
w.add_metadata({"/Title": "Trade Cartel - Transcripts and Lessons", "/Author": "Trade Cartel"})
with open(DEST, "wb") as f:
    w.write(f)
print(f"documents {ndocs}   pages {len(PdfReader(DEST).pages)}   "
      f"{os.path.getsize(DEST)/1048576:.1f} MB")
print(f"characters typeset {chars}   substitutions {sum(SUBS.values())}")
