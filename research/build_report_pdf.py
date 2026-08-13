"""Typeset a markdown research report as a PDF.

Prose-oriented: serif body, sans headings, real tables, and the [YES]/[NO]/[?]
assessment marks rendered as coloured glyphs. Unlike the corpus builders (which
preserve source text verbatim in monospace), this one lays the document out for
reading.

Usage:  python3 research/build_report_pdf.py <input.md> <output.pdf> "<Title>" "<Subtitle>"
"""
import sys, os, re, html
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether, PageBreak, NextPageTemplate)

FDIR = "/usr/share/fonts/truetype/dejavu"
for name, f in [("Body", "DejaVuSerif.ttf"), ("Body-Bold", "DejaVuSerif-Bold.ttf"),
                ("Head", "DejaVuSans-Bold.ttf"), ("UI", "DejaVuSans.ttf")]:
    pdfmetrics.registerFont(TTFont(name, f"{FDIR}/{f}"))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold",
                              italic="Body", boldItalic="Body-Bold")

W, H = A4
INK    = HexColor("#1A1A1A")
MUTED  = HexColor("#6B7280")
RULE   = HexColor("#D4D7DC")
HILITE = HexColor("#FFE9A8")
ACCENT = HexColor("#8A6D1F")
DARK   = HexColor("#15181C")
GOOD   = HexColor("#1F7A4D")
BAD    = HexColor("#B03A2E")
MAYBE  = HexColor("#B7791F")

S = {
 "h1":   ParagraphStyle("h1", fontName="Head", fontSize=21, leading=26, textColor=INK,
                        spaceBefore=0, spaceAfter=6),
 "h2":   ParagraphStyle("h2", fontName="Head", fontSize=14, leading=18, textColor=INK,
                        spaceBefore=16, spaceAfter=7),
 "h3":   ParagraphStyle("h3", fontName="Head", fontSize=10.5, leading=14, textColor=ACCENT,
                        spaceBefore=12, spaceAfter=5),
 "body": ParagraphStyle("body", fontName="Body", fontSize=9.2, leading=13.6, textColor=INK,
                        spaceAfter=6, alignment=TA_LEFT),
 "li":   ParagraphStyle("li", fontName="Body", fontSize=9.2, leading=13.4, textColor=INK,
                        leftIndent=11, bulletIndent=2, spaceAfter=2.5),
 "li2":  ParagraphStyle("li2", fontName="Body", fontSize=8.9, leading=12.8, textColor=INK,
                        leftIndent=24, bulletIndent=15, spaceAfter=2),
 "li3":  ParagraphStyle("li3", fontName="Body", fontSize=8.6, leading=12.4, textColor=MUTED,
                        leftIndent=37, bulletIndent=28, spaceAfter=2),
 "cell": ParagraphStyle("cell", fontName="Body", fontSize=8.4, leading=11.6, textColor=INK),
 "cellh": ParagraphStyle("cellh", fontName="Head", fontSize=8.4, leading=11.6, textColor=INK),
}

MARK = {"[YES]": f'<font name="UI" color="#1F7A4D">✓</font> ',
        "[NO]":  f'<font name="UI" color="#B03A2E">✗</font> ',
        "[?]":   f'<font name="UI" color="#B7791F">?</font> '}


def inline(t):
    t = html.escape(t)
    # bare glyphs first, so the bracket forms we insert below aren't re-processed
    t = t.replace("✓", '<font name="UI" color="#1F7A4D">✓</font>')
    t = t.replace("✗", '<font name="UI" color="#B03A2E">✗</font>')
    for k, v in MARK.items():
        t = t.replace(html.escape(k), v)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`(.+?)`", r'<font name="UI">\1</font>', t)
    return t


def parse(md):
    story, i = [], 0
    lines = md.split("\n")
    first_h2 = True
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if not s or s == "---":
            i += 1
            continue

        if s.startswith("# "):
            story.append(Paragraph(inline(s[2:]), S["h1"])); i += 1; continue

        if s.startswith("## "):
            if not first_h2:
                story.append(PageBreak())
            first_h2 = False
            story.append(Paragraph(inline(s[3:]), S["h2"]))
            story.append(HRule()); i += 1; continue

        if s.startswith("### "):
            story.append(Paragraph(inline(s[4:]), S["h3"])); i += 1; continue

        if s.startswith("|") and i + 1 < len(lines) and set(lines[i+1].strip()) <= set("|-: "):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not set("".join(cells)) <= set("-: "):
                    rows.append(cells)
                i += 1
            if rows:
                data = [[Paragraph(inline(c), S["cellh"] if r == 0 else S["cell"])
                         for c in row] for r, row in enumerate(rows)]
                ncol = max(len(r) for r in data)
                avail = W - 40*mm
                t = Table(data, colWidths=[avail*0.34] + [avail*0.66/(ncol-1)]*(ncol-1)
                          if ncol > 1 else [avail], repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), HILITE),
                    ("LINEBELOW", (0, 0), (-1, 0), .8, ACCENT),
                    ("LINEBELOW", (0, 1), (-1, -2), .3, RULE),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ]))
                story.append(Spacer(1, 4)); story.append(t); story.append(Spacer(1, 7))
            continue

        m = re.match(r"^(\s*)([-*])\s+(.*)$", ln)
        if m:
            ind = len(m.group(1))
            st = S["li"] if ind < 2 else (S["li2"] if ind < 4 else S["li3"])
            bullet = "•" if ind < 2 else ("–" if ind < 4 else "·")
            story.append(Paragraph(inline(m.group(3)), st, bulletText=bullet)); i += 1; continue

        m = re.match(r"^(\s*)(\d+)\.\s+(.*)$", ln)
        if m:
            ind = len(m.group(1))
            st = S["li"] if ind < 2 else (S["li2"] if ind < 4 else S["li3"])
            story.append(Paragraph(inline(m.group(3)), st,
                                   bulletText=f"{m.group(2)}.")); i += 1; continue

        story.append(Paragraph(inline(s), S["body"])); i += 1
    return story


class HRule(Spacer):
    def __init__(self):
        Spacer.__init__(self, 1, 6)

    def draw(self):
        self.canv.setStrokeColor(RULE)
        self.canv.setLineWidth(.7)
        self.canv.line(0, 3, W - 40*mm, 3)


TITLE = SUBTITLE = ""


def cover(c, doc):
    c.saveState()
    c.setFillColor(DARK); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HILITE); c.rect(20*mm, H - 96*mm, 52*mm, 3*mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF")); c.setFont("Head", 25)
    for k, line in enumerate(TITLE.split("|")):
        c.drawString(20*mm, H - 88*mm + k*0, line.strip())
    c.setFillColor(HILITE); c.setFont("Head", 15)
    c.drawString(20*mm, H - 110*mm, SUBTITLE)
    c.setFillColor(HexColor("#9CA3AF")); c.setFont("UI", 9)
    c.drawString(20*mm, H - 128*mm, "Claims presented alongside sources for independent verification.")
    c.drawString(20*mm, H - 135*mm, "Documented fact, contested interpretation and speculation are marked separately.")
    c.setFont("UI", 8.5)
    c.setFillColor(GOOD); c.drawString(20*mm, H - 152*mm, "✓")
    c.setFillColor(HexColor("#9CA3AF")); c.drawString(26*mm, H - 152*mm, "documented")
    c.setFillColor(BAD); c.drawString(60*mm, H - 152*mm, "✗")
    c.setFillColor(HexColor("#9CA3AF")); c.drawString(66*mm, H - 152*mm, "not supported")
    c.setFillColor(MAYBE); c.drawString(105*mm, H - 152*mm, "?")
    c.setFillColor(HexColor("#9CA3AF")); c.drawString(111*mm, H - 152*mm, "interpretation")
    c.restoreState()


def page(c, doc):
    c.saveState()
    c.setStrokeColor(RULE); c.setLineWidth(.4)
    c.line(20*mm, 15*mm, W - 20*mm, 15*mm)
    c.setFont("UI", 7); c.setFillColor(MUTED)
    c.drawString(20*mm, 10*mm, SUBTITLE)
    c.drawRightString(W - 20*mm, 10*mm, str(doc.page - 1))
    c.restoreState()


def build(src, dest, title, subtitle):
    global TITLE, SUBTITLE
    TITLE, SUBTITLE = title, subtitle
    doc = BaseDocTemplate(dest, pagesize=A4, title=title, author="Trade Cartel",
                          leftMargin=20*mm, rightMargin=20*mm,
                          topMargin=20*mm, bottomMargin=20*mm)
    frame = Frame(20*mm, 20*mm, W - 40*mm, H - 40*mm, id="f", showBoundary=0)
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame], onPage=cover),
        PageTemplate(id="body", frames=[frame], onPage=page)])
    md = open(src, encoding="utf-8").read()
    story = [NextPageTemplate("body"), PageBreak()] + parse(md)
    doc.build(story)
    print(f"WROTE {dest}  {os.path.getsize(dest)/1024:.0f} KB")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2],
          sys.argv[3] if len(sys.argv) > 3 else "Report",
          sys.argv[4] if len(sys.argv) > 4 else "")
