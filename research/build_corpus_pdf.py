"""Compile every source transcript, conversation and book text in trader_playbooks/sources
into one PDF: each document opens with a highlighted title band, plus a contents list
and PDF bookmarks."""
import os, re, glob, unicodedata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter

ROOT = "/home/user/Trade_Cartel/trader_playbooks/sources"
OUT = "/tmp/claude-0/-home-user-Trade-Cartel/af36979e-ba34-557a-a8b0-0a27e52e3758/scratchpad"
W, H = A4
ML, MR, MT, MB = 20*mm, 18*mm, 20*mm, 18*mm
TW = W - ML - MR
BODY, LEAD = 8.6, 11.4

INK    = HexColor("#1A1D21")
MUTED  = HexColor("#6B7280")
RULE   = HexColor("#D8DBE0")
HILITE = HexColor("#FFE9A8")      # the title highlight
ACCENT = HexColor("#8A6D1F")
SECTBG = HexColor("#1A1D21")

SECTIONS = [
    ("Books, Courses and Reports", sorted(glob.glob(f"{ROOT}/*.txt") + glob.glob(f"{ROOT}/*.md"))),
    ("Raw Transcripts",            sorted(glob.glob(f"{ROOT}/raw_transcripts/*"))),
    ("Session Archive",            sorted(glob.glob(f"{ROOT}/session_archive/*"))),
    ("AMDM Synthesis",             sorted(glob.glob(f"{ROOT}/amdm_synthesis/*"))),
]


def clean(s):
    s = (s.replace("‘", "'").replace("’", "'")
          .replace("“", '"').replace("”", '"')
          .replace("–", "-").replace("—", "--")
          .replace("…", "...").replace(" ", " ").replace("\t", "    "))
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if ord(c) < 256)


def title_of(path):
    base = os.path.basename(path)
    stem = re.sub(r"\.(txt|md)$", "", base)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for _ in range(40):
                ln = f.readline()
                if not ln:
                    break
                ln = ln.strip()
                cand = None
                m = re.match(r"^#\s+(.{4,90})$", ln)
                if m:
                    cand = m.group(1)
                else:
                    m = re.match(r"^[Tt]itle\s*[:=]\s*(.{4,90})$", ln)
                    if m:
                        cand = m.group(1)
                if cand:
                    c = clean(cand).strip()
                    # reject rules / banners like "======" or "######"
                    letters = sum(ch.isalnum() for ch in c)
                    if letters >= 4 and letters >= 0.5 * len(c):
                        return c, base
    except Exception:
        pass
    t = stem.replace("_", " ").replace("-", " ").strip()
    return (t[:1].upper() + t[1:]) or base, base


def wrap(text, font, size, width):
    out = []
    for para in text.split("\n"):
        para = para.rstrip()
        if not para:
            out.append("")
            continue
        line = ""
        for w in para.split(" "):
            while stringWidth(w, font, size) > width:
                cut = len(w)
                while cut > 1 and stringWidth(w[:cut], font, size) > width:
                    cut -= 1
                if line:
                    out.append(line)
                    line = ""
                out.append(w[:cut])
                w = w[cut:]
            t = w if not line else line + " " + w
            if stringWidth(t, font, size) <= width:
                line = t
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


class Book:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.page = 1
        self.y = H - MT

    def foot(self):
        self.c.setStrokeColor(RULE)
        self.c.setLineWidth(.4)
        self.c.line(ML, MB + 7*mm, W - MR, MB + 7*mm)
        self.c.setFont("Helvetica", 7)
        self.c.setFillColor(MUTED)
        self.c.drawString(ML, MB + 2.5*mm, "Trade Cartel - Source Corpus")
        self.c.drawRightString(W - MR, MB + 2.5*mm, str(self.page))

    def newpage(self):
        self.foot()
        self.c.showPage()
        self.page += 1
        self.y = H - MT

    def section(self, name):
        if self.y < H - MT:
            self.newpage()
        self.c.setFillColor(SECTBG)
        self.c.rect(0, H/2 - 30*mm, W, 60*mm, fill=1, stroke=0)
        self.c.setFillColor(HILITE)
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawCentredString(W/2, H/2, clean(name))
        self.c.setFillColor(HexColor("#9CA3AF"))
        self.c.setFont("Helvetica", 9)
        self.c.drawCentredString(W/2, H/2 - 12*mm, "SECTION")
        start = self.page
        self.newpage()
        return start

    def doc(self, title, fname, text):
        if self.y < H - MT:
            self.newpage()
        start = self.page
        lines = wrap(clean(title), "Helvetica-Bold", 15, TW - 10*mm)
        bh = len(lines) * 19 + 16
        self.c.setFillColor(HILITE)
        self.c.rect(ML, self.y - bh + 6, TW, bh, fill=1, stroke=0)
        self.c.setFillColor(ACCENT)
        self.c.rect(ML, self.y - bh + 6, 2.5*mm, bh, fill=1, stroke=0)
        self.c.setFillColor(INK)
        self.c.setFont("Helvetica-Bold", 15)
        ty = self.y - 14
        for ln in lines:
            self.c.drawString(ML + 6*mm, ty, ln)
            ty -= 19
        self.y -= bh + 4
        self.c.setFont("Helvetica-Oblique", 7.5)
        self.c.setFillColor(MUTED)
        self.c.drawString(ML, self.y, clean(fname))
        self.y -= 14
        self.c.setFillColor(INK)
        for ln in wrap(clean(text), "Helvetica", BODY, TW):
            if self.y < MB + 14*mm:
                self.newpage()
            self.c.setFont("Helvetica", BODY)
            self.c.setFillColor(INK)
            self.c.drawString(ML, self.y, ln)
            self.y -= LEAD
        return start

    def done(self):
        self.foot()
        self.c.save()


body = Book(f"{OUT}/_body.pdf")
toc = []
for sec, files in SECTIONS:
    files = [f for f in files if os.path.isfile(f) and f.lower().endswith((".txt", ".md"))]
    if not files:
        continue
    toc.append(("SEC", sec, None, body.section(sec)))
    for f in files:
        t, base = title_of(f)
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except Exception as e:
            txt = f"[unreadable: {e}]"
        if not txt.strip():
            txt = "[empty file]"
        toc.append(("DOC", t, base, body.doc(t, base, txt)))
body.done()
nbody = len(PdfReader(f"{OUT}/_body.pdf").pages)
ndocs = sum(1 for k, *_ in toc if k == "DOC")
print(f"body pages: {nbody}   documents: {ndocs}")

# ---------- front matter ----------
per = 40
ntoc = max(1, -(-len(toc) // per))
front = 1 + ntoc
fc = canvas.Canvas(f"{OUT}/_front.pdf", pagesize=A4)
fc.setFillColor(SECTBG)
fc.rect(0, 0, W, H, fill=1, stroke=0)
fc.setFillColor(HILITE)
fc.rect(ML, H - 100*mm, 52*mm, 3*mm, fill=1, stroke=0)
fc.setFillColor(HexColor("#FFFFFF"))
fc.setFont("Helvetica-Bold", 30)
fc.drawString(ML, H - 92*mm, "Trade Cartel")
fc.setFillColor(HILITE)
fc.drawString(ML, H - 115*mm, "Source Corpus")
fc.setFillColor(HexColor("#9CA3AF"))
fc.setFont("Helvetica", 10)
fc.drawString(ML, H - 140*mm, "Every transcript, conversation and book text held in the repository")
fc.drawString(ML, H - 148*mm, f"{ndocs} documents  -  {nbody + front} pages")
fc.showPage()

i = 0
for pg in range(ntoc):
    fc.setFillColor(INK)
    fc.setFont("Helvetica-Bold", 16)
    fc.drawString(ML, H - MT, "Contents")
    fc.setStrokeColor(RULE)
    fc.setLineWidth(.6)
    fc.line(ML, H - MT - 5*mm, W - MR, H - MT - 5*mm)
    y = H - MT - 14*mm
    while i < len(toc) and y > MB + 10*mm:
        kind, t, base, p = toc[i]
        i += 1
        if kind == "SEC":
            y -= 3*mm
            fc.setFillColor(HILITE)
            fc.rect(ML, y - 1.5*mm, TW, 6*mm, fill=1, stroke=0)
            fc.setFillColor(INK)
            fc.setFont("Helvetica-Bold", 9.5)
            fc.drawString(ML + 2*mm, y + 0.6*mm, clean(t).upper())
            fc.drawRightString(W - MR - 2*mm, y + 0.6*mm, str(p + front))
            y -= 9*mm
        else:
            fc.setFillColor(INK)
            fc.setFont("Helvetica", 8.6)
            s = clean(t)
            while stringWidth(s, "Helvetica", 8.6) > TW - 18*mm and len(s) > 8:
                s = s[:-2]
            fc.drawString(ML + 3*mm, y, s)
            fc.setFillColor(MUTED)
            fc.drawRightString(W - MR, y, str(p + front))
            y -= 5.6*mm
    fc.setFont("Helvetica", 7)
    fc.setFillColor(MUTED)
    fc.drawRightString(W - MR, MB + 2.5*mm, str(pg + 2))
    fc.showPage()
fc.save()

w = PdfWriter()
for pdf in (f"{OUT}/_front.pdf", f"{OUT}/_body.pdf"):
    for p in PdfReader(pdf).pages:
        w.add_page(p)
parent = None
for kind, t, base, p in toc:
    if kind == "SEC":
        parent = w.add_outline_item(clean(t), p + front - 1)
    else:
        w.add_outline_item(clean(t), p + front - 1, parent=parent)
w.add_metadata({"/Title": "Trade Cartel - Source Corpus", "/Author": "Trade Cartel"})
dest = f"{OUT}/Trade_Cartel_Source_Corpus.pdf"
with open(dest, "wb") as f:
    w.write(f)
print("WROTE", dest, os.path.getsize(dest) // 1024, "KB", len(PdfReader(dest).pages), "pages")
