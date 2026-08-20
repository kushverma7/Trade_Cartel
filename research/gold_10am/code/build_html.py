"""Render the Gold 10AM report as a self-contained HTML page.

Deliberately a small hand-rolled converter rather than a library: the report uses
only headings, tables, blockquotes, lists, fences and inline emphasis, and this
way the markup carries the report's own semantics — verdict banners, pass/fail
colouring on statistical verdicts, tabular figures — instead of generic output.
"""
import os, re, html, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "report", "GOLD_10AM_2024_2026_FULL_REPORT.md")
DST = os.path.join(HERE, "..", "report", "gold_10am_report.html")


def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*]+)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def convert(md):
    lines = md.split("\n")
    out, toc = [], []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]

        # fenced code
        if ln.startswith("```"):
            j = i + 1
            buf = []
            while j < n and not lines[j].startswith("```"):
                buf.append(html.escape(lines[j])); j += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            i = j + 1
            continue

        # table
        if ln.startswith("|") and i + 1 < n and re.match(r"^\|[\s:*-]+\|", lines[i + 1]):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            aligns = [c.strip() for c in lines[i + 1].strip().strip("|").split("|")]
            j = i + 2
            body = []
            while j < n and lines[j].startswith("|"):
                body.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            def cls(k):
                a = aligns[k] if k < len(aligns) else "---"
                return ' class="r"' if a.endswith(":") else ""
            t = ['<div class="tw"><table>']
            if any(h for h in head):
                t.append("<thead><tr>" + "".join(
                    f"<th{cls(k)}>{inline(h)}</th>" for k, h in enumerate(head)) + "</tr></thead>")
            t.append("<tbody>")
            for row in body:
                cells = []
                for k, c in enumerate(row):
                    v = inline(c)
                    extra = ""
                    # semantic colouring on verdict-bearing cells
                    if re.fullmatch(r"\*?\*?(No|None|REJECTED|BLOCKED)\*?\*?\.?", c):
                        extra = ' data-v="neg"'
                    elif re.fullmatch(r"\*?\*?(Yes|ACCEPTED)\*?\*?\.?", c):
                        extra = ' data-v="pos"'
                    cells.append(f"<td{cls(k)}{extra}>{v}</td>")
                t.append("<tr>" + "".join(cells) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("\n".join(t))
            i = j
            continue

        # headings
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            sid = slug(txt)
            if lvl == 1:
                out.append(f'<h1 id="{sid}">{inline(txt)}</h1>')
            elif lvl == 2:
                toc.append((sid, txt))
                out.append(f'<h2 id="{sid}">{inline(txt)}</h2>')
            else:
                out.append(f'<h{lvl} id="{sid}">{inline(txt)}</h{lvl}>')
            i += 1
            continue

        if ln.startswith("---") and set(ln.strip()) == {"-"}:
            out.append("<hr>"); i += 1; continue

        # blockquote
        if ln.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip()); i += 1
            out.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>")
            continue

        # lists (ordered / unordered, with continuation lines)
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", ln)
        if m:
            ordered = bool(re.match(r"\d+\.", m.group(2)))
            items = []
            while i < n:
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if not mm:
                    if items and lines[i].startswith("   ") and lines[i].strip():
                        items[-1] += " " + lines[i].strip(); i += 1; continue
                    break
                items.append(mm.group(3)); i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue

        if not ln.strip():
            i += 1; continue

        # paragraph
        buf = []
        while i < n and lines[i].strip() and not lines[i].startswith(("#", "|", ">", "```")) \
                and not re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[i]) \
                and not (lines[i].startswith("---") and set(lines[i].strip()) == {"-"}):
            buf.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")

    return "\n".join(out), toc


CSS = """
:root{
  --paper:#F6F4EF; --surface:#FFFFFF; --ink:#191B1F; --muted:#5C6views;
}
"""

TEMPLATE = """<title>Gold 10AM Verdict</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#F5F3EE; --surface:#FFFFFF; --ink:#1A1C20; --muted:#5D6views;
}
</style>
"""


def build():
    md = open(SRC).read()
    body, toc = convert(md)
    toc_html = "".join(
        f'<a href="#{sid}">{html.escape(txt)}</a>' for sid, txt in toc)
    page = HEAD + f"""
<div class="shell">
  <nav class="toc" aria-label="Sections">
    <p class="toclabel">Sections</p>
    {toc_html}
  </nav>
  <main class="doc">
    <header class="hero">
      <p class="eyebrow">Quantitative research &middot; XAU/USD &middot; 2024-08-20 → 2026-08-19</p>
      <h1>The 10AM Body Break does not transfer to gold</h1>
      <p class="verdict">NO EVIDENCE OF GOLD EDGE</p>
      <div class="facts">
        <div><span class="k">Setup days</span><span class="v">339</span><span class="s">of 523 weekdays</span></div>
        <div><span class="k">Trades</span><span class="v">607</span><span class="s">four logic branches</span></div>
        <div><span class="k">First-passage tests</span><span class="v">0 / 64</span><span class="s">significant</span></div>
        <div><span class="k">Holdout PF</span><span class="v neg">0.841</span><span class="s">sole candidate</span></div>
        <div><span class="k">09:50 candle absent</span><span class="v neg">180 / 180</span><span class="s">AEDT + NY&nbsp;EST weekdays</span></div>
        <div><span class="k">Measured spread</span><span class="v">$0.630</span><span class="s">median, per ounce</span></div>
      </div>
    </header>
    {body}
  </main>
</div>
"""
    with open(DST, "w") as f:
        f.write(page)
    print(f"wrote {DST}  ({len(page):,} bytes, {len(toc)} sections)")


HEAD = """<title>Gold 10AM Verdict</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#F4F2ED; --surface:#FBFAF7; --ink:#1A1C20; --muted:#5E6views;
  --muted:#5E6167; --rule:#DCD9D1; --rule2:#EAE7E0;
  --brass:#8A6A2F; --brass-soft:#F0E7D4;
  --neg:#9B3B32; --pos:#3C6E4A;
  --serif:"Source Serif 4",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,"SF Mono",Menlo,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#131519; --surface:#191C21; --ink:#E7E5E0; --muted:#9DA0A7;
    --rule:#2B2F36; --rule2:#22262C;
    --brass:#CBA94A; --brass-soft:#2A2517;
    --neg:#DC7C72; --pos:#77AE86;
  }
}
:root[data-theme="dark"]{
  --paper:#131519; --surface:#191C21; --ink:#E7E5E0; --muted:#9DA0A7;
  --rule:#2B2F36; --rule2:#22262C;
  --brass:#CBA94A; --brass-soft:#2A2517;
  --neg:#DC7C72; --pos:#77AE86;
}
:root[data-theme="light"]{
  --paper:#F4F2ED; --surface:#FBFAF7; --ink:#1A1C20; --muted:#5E6167;
  --rule:#DCD9D1; --rule2:#EAE7E0;
  --brass:#8A6A2F; --brass-soft:#F0E7D4;
  --neg:#9B3B32; --pos:#3C6E4A;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--serif); font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased;
}
.shell{display:grid; grid-template-columns:1fr; gap:0; max-width:1180px; margin:0 auto; padding:0 20px}
@media (min-width:1000px){
  .shell{grid-template-columns:232px minmax(0,1fr); gap:48px; padding:0 32px}
}
/* ---- table of contents ---- */
.toc{display:none}
@media (min-width:1000px){
  .toc{
    display:block; position:sticky; top:0; align-self:start;
    max-height:100vh; overflow-y:auto; padding:40px 0 60px;
    font-family:var(--sans); font-size:12.5px; line-height:1.45;
    border-right:1px solid var(--rule2);
  }
  .toc a{
    display:block; padding:4px 14px 4px 0; color:var(--muted);
    text-decoration:none; border-left:2px solid transparent; padding-left:10px;
  }
  .toc a:hover{color:var(--brass); border-left-color:var(--brass)}
  .toc a:focus-visible{outline:2px solid var(--brass); outline-offset:2px}
}
.toclabel{
  font-family:var(--sans); font-size:10.5px; letter-spacing:.13em;
  text-transform:uppercase; color:var(--muted); margin:0 0 12px 10px;
}
.doc{padding:40px 0 120px; min-width:0}
/* ---- hero ---- */
.hero{
  border-top:3px solid var(--brass); background:var(--surface);
  border:1px solid var(--rule); border-top:3px solid var(--brass);
  padding:34px 34px 28px; margin-bottom:46px;
}
.eyebrow{
  font-family:var(--sans); font-size:11px; letter-spacing:.12em;
  text-transform:uppercase; color:var(--muted); margin:0 0 14px;
}
.hero h1{
  font-family:var(--serif); font-weight:600; font-size:clamp(28px,4.2vw,42px);
  line-height:1.12; letter-spacing:-.015em; margin:0 0 18px; text-wrap:balance;
}
.verdict{
  display:inline-block; font-family:var(--sans); font-weight:600;
  font-size:13px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--neg); border:1px solid currentColor; padding:7px 14px; margin:0 0 26px;
}
.facts{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:1px; background:var(--rule2); border:1px solid var(--rule2);
}
.facts>div{background:var(--surface); padding:14px 16px; display:flex; flex-direction:column; gap:2px}
.facts .k{font-family:var(--sans); font-size:10.5px; letter-spacing:.09em; text-transform:uppercase; color:var(--muted)}
.facts .v{font-family:var(--sans); font-weight:600; font-size:24px; font-variant-numeric:tabular-nums; letter-spacing:-.01em}
.facts .v.neg{color:var(--neg)}
.facts .s{font-family:var(--sans); font-size:11.5px; color:var(--muted)}
/* ---- prose ---- */
.doc h1{
  font-weight:600; font-size:clamp(24px,3vw,32px); line-height:1.2;
  margin:56px 0 8px; text-wrap:balance; letter-spacing:-.012em;
}
.doc h2{
  font-family:var(--sans); font-weight:600; font-size:19px; line-height:1.3;
  margin:52px 0 14px; padding-top:18px; border-top:1px solid var(--rule);
  text-wrap:balance; letter-spacing:-.005em; scroll-margin-top:16px;
}
.doc h3{font-family:var(--sans); font-weight:600; font-size:15px; margin:30px 0 8px; letter-spacing:.005em}
.doc h4{font-family:var(--sans); font-weight:600; font-size:13.5px; margin:24px 0 6px; color:var(--muted)}
p{margin:0 0 16px; max-width:70ch}
ul,ol{margin:0 0 18px; padding-left:22px; max-width:70ch}
li{margin:0 0 7px}
li::marker{color:var(--brass)}
strong{font-weight:600}
hr{border:0; border-top:1px solid var(--rule); margin:40px 0}
blockquote{
  margin:24px 0; padding:16px 20px; background:var(--brass-soft);
  border-left:3px solid var(--brass); max-width:70ch;
  font-size:16.5px;
}
blockquote p{margin:0}
code{
  font-family:var(--mono); font-size:.85em; background:var(--rule2);
  padding:1px 5px; border-radius:2px; word-break:break-word;
}
pre{
  background:var(--surface); border:1px solid var(--rule); padding:16px 18px;
  overflow-x:auto; margin:0 0 22px; font-size:13px; line-height:1.6;
}
pre code{background:none; padding:0; font-size:13px}
/* ---- tables ---- */
.tw{overflow-x:auto; margin:0 0 26px; border:1px solid var(--rule); background:var(--surface)}
table{border-collapse:collapse; width:100%; font-family:var(--sans); font-size:13px}
th,td{
  padding:8px 12px; text-align:left; border-bottom:1px solid var(--rule2);
  white-space:nowrap; font-variant-numeric:tabular-nums;
}
th{
  font-weight:600; font-size:10.5px; letter-spacing:.07em; text-transform:uppercase;
  color:var(--muted); border-bottom:1px solid var(--rule); vertical-align:bottom;
  position:sticky; top:0; background:var(--surface);
}
td.r,th.r{text-align:right}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover td{background:var(--rule2)}
td[data-v="neg"]{color:var(--neg); font-weight:600}
td[data-v="pos"]{color:var(--pos); font-weight:600}
td strong{color:var(--ink)}
@media (max-width:620px){
  body{font-size:16px}
  .hero{padding:24px 20px 20px}
  th,td{padding:7px 9px; font-size:12px}
}
</style>
"""

if __name__ == "__main__":
    build()
