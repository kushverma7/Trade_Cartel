"""Compile EVERY original source file under trader_playbooks/sources into one PDF.

Original PDFs are reproduced page-for-page, verbatim, behind a highlighted title page.
Text originals (.txt/.md/.csv), plus .docx and .html, are typeset with the same
highlighted title band. Nothing in the directory is skipped.
"""
import os, re, glob, io, zipfile, unicodedata
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter

ROOT = "/home/user/Trade_Cartel/trader_playbooks/sources"
OUT = "/tmp/claude-0/-home-user-Trade-Cartel/af36979e-ba34-557a-a8b0-0a27e52e3758/scratchpad/corpus"
os.makedirs(OUT, exist_ok=True)
W, H = A4
ML, MR, MT, MB = 20*mm, 18*mm, 20*mm, 18*mm
TW = W - ML - MR
BODY, LEAD = 8.6, 11.4

INK    = HexColor("#1A1D21")
MUTED  = HexColor("#6B7280")
RULE   = HexColor("#D8DBE0")
HILITE = HexColor("#FFE9A8")
ACCENT = HexColor("#8A6D1F")
SECTBG = HexColor("#1A1D21")


def clean(s):
    s = (s.replace("‘", "'").replace("’", "'")
          .replace("“", '"').replace("”", '"')
          .replace("–", "-").replace("—", "--")
          .replace("…", "...").replace(" ", " ").replace("\t", "    "))
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if ord(c) < 256)


def title_of(path):
    base = os.path.basename(path)
    stem = re.sub(r"\.[A-Za-z0-9]+$", "", base)
    if path.lower().endswith((".txt", ".md")):
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


def read_text(path):
    low = path.lower()
    if low.endswith(".docx"):
        try:
            with zipfile.ZipFile(path) as z:
                xml = z.read("word/document.xml").decode("utf-8", "replace")
            xml = re.sub(r"</w:p>", "\n", xml)
            xml = re.sub(r"<w:tab[^>]*/>", "    ", xml)
            return re.sub(r"<[^>]+>", "", xml)
        except Exception as e:
            return f"[could not read docx: {e}]"
    if low.endswith((".html", ".htm")):
        try:
            h = open(path, encoding="utf-8", errors="replace").read()
            h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
            h = re.sub(r"(?i)<br[^>]*>|</p>|</div>|</tr>|</h[1-6]>", "\n", h)
            h = re.sub(r"<[^>]+>", "", h)
            h = (h.replace("&nbsp;", " ").replace("&amp;", "&")
                  .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
            return re.sub(r"\n{3,}", "\n\n", h)
        except Exception as e:
            return f"[could not read html: {e}]"
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except Exception as e:
        return f"[unreadable: {e}]"


def footer(c, page):
    c.setStrokeColor(RULE)
    c.setLineWidth(.4)
    c.line(ML, MB + 7*mm, W - MR, MB + 7*mm)
    c.setFont("Helvetica", 7)
    c.setFillColor(MUTED)
    c.drawString(ML, MB + 2.5*mm, "Trade Cartel - Source Corpus (complete originals)")
    c.drawRightString(W - MR, MB + 2.5*mm, str(page))


def title_band(c, y, title, fname, note=None):
    lines = wrap(clean(title), "Helvetica-Bold", 15, TW - 10*mm)
    bh = len(lines) * 19 + 16
    c.setFillColor(HILITE)
    c.rect(ML, y - bh + 6, TW, bh, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(ML, y - bh + 6, 2.5*mm, bh, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    ty = y - 14
    for ln in lines:
        c.drawString(ML + 6*mm, ty, ln)
        ty -= 19
    y -= bh + 4
    c.setFont("Helvetica-Oblique", 7.5)
    c.setFillColor(MUTED)
    c.drawString(ML, y, clean(fname))
    y -= 11
    if note:
        c.setFont("Helvetica", 7.5)
        c.setFillColor(ACCENT)
        c.drawString(ML, y, clean(note))
        y -= 12
    return y - 4


def render_text_item(dest, title, fname, text):
    c = canvas.Canvas(dest, pagesize=A4)
    page = 1
    y = title_band(c, H - MT, title, fname)
    c.setFillColor(INK)
    for ln in wrap(clean(text), "Helvetica", BODY, TW):
        if y < MB + 14*mm:
            footer(c, page)
            c.showPage()
            page += 1
            y = H - MT
        c.setFont("Helvetica", BODY)
        c.setFillColor(INK)
        c.drawString(ML, y, ln)
        y -= LEAD
    footer(c, page)
    c.save()
    return dest


def render_cover_for_pdf(dest, title, fname, npages):
    c = canvas.Canvas(dest, pagesize=A4)
    y = title_band(c, H - MT, title, fname,
                   f"Original PDF reproduced verbatim - {npages} page{'s' if npages != 1 else ''} follow")
    footer(c, 1)
    c.save()
    return dest


def section_page(dest, name):
    c = canvas.Canvas(dest, pagesize=A4)
    c.setFillColor(SECTBG)
    c.rect(0, H/2 - 30*mm, W, 60*mm, fill=1, stroke=0)
    c.setFillColor(HILITE)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(W/2, H/2, clean(name))
    c.setFillColor(HexColor("#9CA3AF"))
    c.setFont("Helvetica", 9)
    c.drawCentredString(W/2, H/2 - 12*mm, "SECTION")
    c.save()
    return dest


# ---------------- gather EVERY file ----------------
allfiles = sorted(p for p in glob.glob(f"{ROOT}/**/*", recursive=True) if os.path.isfile(p))
pdfs = [p for p in allfiles if p.lower().endswith(".pdf")]
root_txt = sorted(p for p in allfiles
                  if os.path.dirname(p) == ROOT and p.lower().endswith((".txt", ".md")))
sub = lambda d: sorted(p for p in allfiles
                       if os.path.dirname(p) == f"{ROOT}/{d}" and p.lower().endswith((".txt", ".md")))
other = [p for p in allfiles if p.lower().endswith((".csv", ".docx", ".html", ".htm"))]
covered = set(pdfs) | set(root_txt) | set(sub("raw_transcripts")) | set(sub("session_archive")) \
    | set(sub("amdm_synthesis")) | set(other)
missed = [p for p in allfiles if p not in covered]

SECTIONS = [
    ("Original PDF Documents", pdfs, "pdf"),
    ("Books, Courses and Reports", root_txt, "text"),
    ("Raw Transcripts", sub("raw_transcripts"), "text"),
    ("Session Archive", sub("session_archive"), "text"),
    ("AMDM Synthesis", sub("amdm_synthesis"), "text"),
    ("Other Originals", other, "text"),
]
if missed:
    SECTIONS.append(("Remaining Files", missed, "text"))

print(f"{len(allfiles)} files found; {len(missed)} fell through to 'Remaining Files'")

# ---------------- build each item, record page counts ----------------
items = []   # (kind, title, fname, [pdf paths in order], npages)
n = 0
for sec, files, mode in SECTIONS:
    if not files:
        continue
    sp = section_page(f"{OUT}/sec{n}.pdf", sec)
    n += 1
    items.append(("SEC", sec, None, [sp], 1))
    for f in files:
        t, base = title_of(f)
        if mode == "pdf":
            try:
                src = PdfReader(f)
                if src.is_encrypted:
                    try:
                        src.decrypt("")
                    except Exception:
                        pass
                np_ = len(src.pages)
                cov = render_cover_for_pdf(f"{OUT}/c{n}.pdf", t, base, np_)
                n += 1
                items.append(("DOC", t, base, [cov, f], 1 + np_))
                continue
            except Exception as e:
                print(f"  ! {base}: {e} -- falling back to a note page")
                d = render_text_item(f"{OUT}/i{n}.pdf", t, base,
                                     f"[This original PDF could not be merged: {e}]")
                n += 1
                items.append(("DOC", t, base, [d], len(PdfReader(d).pages)))
                continue
        txt = read_text(f)
        if not txt.strip():
            txt = "[empty file]"
        d = render_text_item(f"{OUT}/i{n}.pdf", t, base, txt)
        n += 1
        items.append(("DOC", t, base, [d], len(PdfReader(d).pages)))

ndocs = sum(1 for k, *_ in items if k == "DOC")
bodypages = sum(it[4] for it in items)
print(f"documents: {ndocs}   body pages: {bodypages}")

# ---------------- front matter ----------------
per = 40
ntoc = max(1, -(-len(items) // per))
front = 1 + ntoc
start, acc = {}, front + 1
for idx, it in enumerate(items):
    start[idx] = acc
    acc += it[4]

fc = canvas.Canvas(f"{OUT}/_front.pdf", pagesize=A4)
fc.setFillColor(SECTBG)
fc.rect(0, 0, W, H, fill=1, stroke=0)
fc.setFillColor(HILITE)
fc.rect(ML, H - 100*mm, 52*mm, 3*mm, fill=1, stroke=0)
fc.setFillColor(HexColor("#FFFFFF"))
fc.setFont("Helvetica-Bold", 30)
fc.drawString(ML, H - 92*mm, "Trade Cartel")
fc.setFillColor(HILITE)
fc.drawString(ML, H - 115*mm, "Complete Source Corpus")
fc.setFillColor(HexColor("#9CA3AF"))
fc.setFont("Helvetica", 10)
fc.drawString(ML, H - 140*mm, "Every original document held in the repository, nothing omitted.")
fc.drawString(ML, H - 148*mm, "Original PDFs are reproduced page-for-page, verbatim.")
fc.drawString(ML, H - 160*mm, f"{ndocs} documents  -  {bodypages + front} pages")
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
    while i < len(items) and y > MB + 10*mm:
        kind, t, base, _, _ = items[i]
        p = start[i]
        i += 1
        if kind == "SEC":
            y -= 3*mm
            fc.setFillColor(HILITE)
            fc.rect(ML, y - 1.5*mm, TW, 6*mm, fill=1, stroke=0)
            fc.setFillColor(INK)
            fc.setFont("Helvetica-Bold", 9.5)
            fc.drawString(ML + 2*mm, y + .6*mm, clean(t).upper())
            fc.drawRightString(W - MR - 2*mm, y + .6*mm, str(p))
            y -= 9*mm
        else:
            fc.setFillColor(INK)
            fc.setFont("Helvetica", 8.6)
            s = clean(t)
            while stringWidth(s, "Helvetica", 8.6) > TW - 18*mm and len(s) > 8:
                s = s[:-2]
            fc.drawString(ML + 3*mm, y, s)
            fc.setFillColor(MUTED)
            fc.drawRightString(W - MR, y, str(p))
            y -= 5.6*mm
    fc.setFont("Helvetica", 7)
    fc.setFillColor(MUTED)
    fc.drawRightString(W - MR, MB + 2.5*mm, str(pg + 2))
    fc.showPage()
fc.save()

# ---------------- assemble ----------------
w = PdfWriter()
for p in PdfReader(f"{OUT}/_front.pdf").pages:
    w.add_page(p)
for it in items:
    for src in it[3]:
        r = PdfReader(src)
        if r.is_encrypted:
            try:
                r.decrypt("")
            except Exception:
                pass
        for p in r.pages:
            w.add_page(p)
parent = None
for idx, (kind, t, base, _, _) in enumerate(items):
    if kind == "SEC":
        parent = w.add_outline_item(clean(t), start[idx] - 1)
    else:
        w.add_outline_item(clean(t), start[idx] - 1, parent=parent)
w.add_metadata({"/Title": "Trade Cartel - Complete Source Corpus", "/Author": "Trade Cartel"})
dest = "/home/user/Trade_Cartel/Trade_Cartel_Source_Corpus_FULL.pdf"
with open(dest, "wb") as f:
    w.write(f)
print("WROTE", dest, os.path.getsize(dest) // 1024 // 1024, "MB",
      len(PdfReader(dest).pages), "pages")
