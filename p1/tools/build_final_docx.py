#!/usr/bin/env python3
"""Build P1 final report: styled HTML -> ODT (embedded images) -> docx + pdf."""

from __future__ import annotations

import html
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "reports" / "final"
MD = FINAL / "P1_FINAL_REPORT.md"
HTML = FINAL / "P1_FINAL_REPORT.html"
PROFILE = "file:///home/ubuntu2004/WorkBuddy/2026-10-21-15-54-19/.workbuddy/tmp/lo_profile"

text = MD.read_text(encoding="utf-8")


def png_size(path: Path) -> tuple[int, int]:
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return 800, 500
    w, h = struct.unpack(">II", head[16:24])
    return int(w), int(h)


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s.replace("\\|", "|")


out, para_buf = [], []
lines = text.splitlines()
i, in_code, code_buf = 0, False, []
pending_break = False


def flush():
    if para_buf:
        out.append("<p>" + inline(" ".join(para_buf)) + "</p>")
        para_buf.clear()


while i < len(lines):
    ln = lines[i]
    if ln.strip().startswith("```"):
        flush()
        if not in_code:
            in_code, code_buf = True, []
        else:
            in_code = False
            out.append('<pre class="code">' + html.escape("\n".join(code_buf)) + "</pre>")
        i += 1
        continue
    if in_code:
        code_buf.append(ln)
        i += 1
        continue
    m_img = re.match(r"!\[(.*?)\]\((.*?)\)\s*$", ln.strip())
    if m_img:
        flush()
        p = FINAL / m_img.group(2)
        w, h = png_size(p)
        alt = m_img.group(1)
        if alt == "eq":
            wdisp = min(620, int(round(w * 96.0 / 150.0)))
            hdisp = int(round(h * wdisp / w))
            out.append(f'<p class="eqimg"><img src="{m_img.group(2)}" width="{wdisp}" height="{hdisp}"></p>')
        else:
            hpx = max(40, int(round(620.0 * h / max(w, 1))))
            cap = inline(alt)
            out.append(
                f'<p class="img"><img src="{m_img.group(2)}" width="620" height="{hpx}"></p>'
                f'<p class="cap">{cap}</p>'
            )
        i += 1
        continue
    if ln.startswith("### "):
        flush()
        style = ' style="page-break-before: always"' if pending_break else ""
        out.append("<h3" + style + ">" + inline(ln[4:]) + "</h3>")
        pending_break = False
        i += 1; continue
    if ln.startswith("## "):
        flush()
        style = ' style="page-break-before: always"' if pending_break else ""
        out.append("<h2" + style + ">" + inline(ln[3:]) + "</h2>")
        pending_break = False
        i += 1; continue
    if ln.startswith("# "):
        flush()
        style = ' style="page-break-before: always"' if pending_break else ""
        out.append("<h1" + style + ">" + inline(ln[2:]) + "</h1>")
        pending_break = False
        i += 1; continue
    if ln.strip() == "<!--pagebreak-->":
        flush(); pending_break = True; i += 1; continue
    if ln.strip() == "---":
        flush(); out.append('<p class="gap">&#160;</p>'); i += 1; continue
    if ln.strip().startswith("|"):
        flush()
        tbl = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            raw = lines[i].strip().strip("|")
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", raw)]
            if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                tbl.append(cells)
            i += 1
        if tbl:
            ncols = max(len(r) for r in tbl)
            tbl_style = "border-collapse:collapse;width:100%;font-size:8.2pt;table-layout:fixed"
            if pending_break:
                tbl_style += ";page-break-before:always"
                pending_break = False
            t = [f'<table border="1" cellpadding="4" cellspacing="0" style="{tbl_style}">']
            preset = {2: [30, 70], 3: [24, 44, 32], 4: [18, 28, 27, 27],
                      5: [16, 24, 20, 20, 20]}.get(ncols)
            widths = preset if preset else [100 // ncols] * ncols
            t.append("<colgroup>" + "".join(f'<col style="width:{w}%">' for w in widths) + "</colgroup>")
            for ridx, row in enumerate(tbl):
                row = row + [""] * (ncols - len(row))
                tag = "th" if ridx == 0 else "td"
                t.append("<tr>" + "".join(
                    f'<{tag} style="border:1px solid #444;padding:2px 4px;background-color:{"#e8e8e8" if tag=="th" else "#ffffff"}">{inline(c)}</{tag}>'
                    for c in row) + "</tr>")
            t.append("</table>")
            out.append("".join(t))
        continue
    if re.match(r"^\s*\d+\.\s", ln):
        flush()
        items = []
        while i < len(lines) and re.match(r"^\s*\d+\.\s", lines[i]):
            items.append(re.sub(r"^\s*\d+\.\s", "", lines[i])); i += 1
        out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
        continue
    if ln.strip().startswith("- "):
        flush()
        items = []
        while i < len(lines) and lines[i].strip().startswith("- "):
            items.append(lines[i].strip()[2:]); i += 1
        out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
        continue
    if ln.strip():
        if pending_break and not para_buf:
            flush()
            out.append('<p style="page-break-before: always">' + inline(ln.strip()) + "</p>")
            pending_break = False
            i += 1
            continue
        para_buf.append(ln.strip())
    else:
        flush()
    i += 1
flush()

css = """
@page { size: A4; margin: 2.0cm 1.9cm 2.0cm 1.9cm; }
body { font-family: 'Noto Serif CJK SC','Noto Sans CJK SC',sans-serif; font-size: 10.5pt;
       line-height: 1.62; color: #111; }
h1 { font-family: 'Noto Sans CJK SC',sans-serif; font-size: 17pt; text-align: center;
     margin: 6px 0 14px 0; }
h2 { font-family: 'Noto Sans CJK SC',sans-serif; font-size: 13.5pt; margin-top: 18px;
     border-bottom: 1px solid #999; padding-bottom: 3px; page-break-after: avoid; }
h3 { font-family: 'Noto Sans CJK SC',sans-serif; font-size: 11.5pt; margin-top: 14px; page-break-after: avoid; }
p { text-align: justify; margin: 4px 0; }
li { text-align: left; }
li { text-align: left; }
table { border-collapse: collapse; width: 100%; font-size: 8.2pt; margin: 8px 0; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #888; padding: 2px 4px; vertical-align: top; text-align: left; }
th { background: #e8e8e8; }
td code, th code { white-space: nowrap; }
td code, th code { white-space: nowrap; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 9pt; background: #f2f2f2; }
pre.code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.6pt; background: #f6f6f6;
           border: 1px solid #ccc; padding: 7px 8px; white-space: pre-wrap; margin: 6px 0; }
p.img { text-align: center; margin: 10px 0 2px 0; }
p.cap { text-align: center; font-size: 9pt; color: #333; margin: 0 0 10px 0; }
p.eqimg { text-align: center; margin: 6px 0; }
p.gap { margin: 2px 0; font-size: 1pt; line-height: 0.1; }
"""
(FINAL / "P1_FINAL_REPORT.html").write_text(
    "<!DOCTYPE html><html><head><meta charset='utf-8'><title>P1 数值复现报告</title>"
    "<style>" + css + "</style></head><body>" + "\n".join(out) + "</body></html>",
    encoding="utf-8",
)


def soffice(*args):
    cmd = ["soffice", "--headless", f"-env:UserInstallation={PROFILE}", *args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    print(" ".join(args[:2]), r.returncode)
    if r.returncode != 0:
        print(r.stderr[-800:])
    return r


soffice("--convert-to", "odt", "--outdir", str(FINAL), str(HTML))
subprocess.run([sys.executable, str(ROOT / "tools" / "embed_odt_images.py"),
                str(FINAL / "P1_FINAL_REPORT.odt")], check=True)
subprocess.run([sys.executable, str(ROOT / "tools" / "add_page_numbers.py"),
                str(FINAL / "P1_FINAL_REPORT.odt")], check=True)
soffice("--convert-to", "docx:MS Word 2007 XML", "--outdir", str(FINAL),
        str(FINAL / "P1_FINAL_REPORT.odt"))
soffice("--convert-to", "pdf", "--outdir", str(FINAL), str(FINAL / "P1_FINAL_REPORT.odt"))
