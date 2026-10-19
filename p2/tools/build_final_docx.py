#!/usr/bin/env python3
"""Build P2 final report deliverables: styled HTML -> docx -> pdf via LibreOffice.

Controlled Markdown subset: #/##/### headings, paragraphs, pipe tables,
fenced code blocks, images ![alt](rel), unordered lists, **bold**, `code`.
"""
import html
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "p2" / "reports" / "final"
MD = FINAL / "P2_FINAL_REPORT.md"
HTML = FINAL / "P2_FINAL_REPORT.html"
PROFILE = "file:///home/ubuntu2004/WorkBuddy/2026-10-19-21-10-45/.workbuddy/tmp/lo_profile"

text = MD.read_text(encoding="utf-8")

def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s

out = []
lines = text.splitlines()
i = 0
in_code = False
code_buf = []
para_buf = []

def flush_para():
    if para_buf:
        out.append("<p>" + inline(" ".join(para_buf)) + "</p>")
        para_buf.clear()

while i < len(lines):
    ln = lines[i]
    if ln.strip().startswith("```"):
        flush_para()
        if not in_code:
            in_code = True
            code_buf = []
        else:
            in_code = False
            out.append("<pre class=\"code\">" + html.escape("\n".join(code_buf)) + "</pre>")
        i += 1
        continue
    if in_code:
        code_buf.append(ln)
        i += 1
        continue
    m_img = re.match(r"!\[(.*?)\]\((.*?)\)\s*$", ln.strip())
    if m_img:
        flush_para()
        src = m_img.group(2)  # relative to the HTML file; LibreOffice resolves and embeds
        out.append(f'<p class="img"><img src="{src}" style="width:560px"/></p>')
        i += 1
        continue
    if ln.startswith("### "):
        flush_para(); out.append("<h3>" + inline(ln[4:]) + "</h3>"); i += 1; continue
    if ln.startswith("## "):
        flush_para(); out.append("<h2>" + inline(ln[3:]) + "</h2>"); i += 1; continue
    if ln.startswith("# "):
        flush_para(); out.append("<h1>" + inline(ln[2:]) + "</h1>"); i += 1; continue
    if ln.strip() == "---":
        flush_para(); out.append("<hr/>"); i += 1; continue
    if ln.strip().startswith("|"):
        flush_para()
        tbl = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-{3,}:?", c) for c in row):
                tbl.append(row)
            i += 1
        if tbl:
            ncols = max(len(r) for r in tbl)
            t = ["<table>"]
            for ridx, row in enumerate(tbl):
                row = row + [""] * (ncols - len(row))
                tag = "th" if ridx == 0 else "td"
                t.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in row) + "</tr>")
            t.append("</table>")
            out.append("".join(t))
        continue
    if ln.strip().startswith("- "):
        flush_para()
        items = []
        while i < len(lines) and lines[i].strip().startswith("- "):
            items.append(lines[i].strip()[2:]); i += 1
        out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
        continue
    if ln.strip():
        para_buf.append(ln.strip())
    else:
        flush_para()
    i += 1
flush_para()

css = """
body { font-family: 'Noto Sans CJK SC','WenQuanYi Zen Hei',sans-serif; font-size: 10.5pt; line-height: 1.55; }
h1 { font-size: 17pt; border-bottom: 2px solid #333; padding-bottom: 6px; }
h2 { font-size: 13.5pt; margin-top: 18px; border-bottom: 1px solid #999; padding-bottom: 3px; }
h3 { font-size: 11.5pt; margin-top: 14px; }
table { border-collapse: collapse; width: 100%; font-size: 8.5pt; margin: 8px 0; }
th, td { border: 1px solid #888; padding: 3px 5px; vertical-align: top; }
th { background: #e8e8e8; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 9pt; background: #f2f2f2; }
pre.code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.5pt; background: #f5f5f5;
           border: 1px solid #ccc; padding: 8px; white-space: pre-wrap; }
p.img { text-align: center; margin: 10px 0; }
hr { border: none; border-top: 1px solid #aaa; }
"""
doc = ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
       "<title>P2 Final Report</title><style>" + css + "</style></head><body>"
       + "\n".join(out) + "</body></html>")
HTML.write_text(doc, encoding="utf-8")
print(f"wrote {HTML}")

for target, fmt in (("docx", "docx:\"MS Word 2007 XML\""), ("pdf", "pdf")):
    r = subprocess.run(
        ["soffice", "--headless", f"-env:UserInstallation={PROFILE}",
         "--convert-to", fmt, "--outdir", str(FINAL), str(HTML)],
        capture_output=True, text=True, timeout=300)
    print(target, r.returncode, r.stdout.strip()[-200:], r.stderr.strip()[-200:])
