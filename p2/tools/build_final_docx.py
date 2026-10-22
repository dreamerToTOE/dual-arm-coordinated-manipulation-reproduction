#!/usr/bin/env python3
"""Build P3 final report deliverables: styled HTML -> ODT (embedded images) -> docx + pdf."""
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / "p2" / "reports" / "final"
MD = FINAL / "P2_FINAL_REPORT.md"
HTML = FINAL / "P2_FINAL_REPORT.html"
PROFILE = "file:///home/ubuntu2004/WorkBuddy/2026-10-19-21-10-45/.workbuddy/tmp/lo_profile"

text = MD.read_text(encoding="utf-8")



def png_size(path):
    """Read PNG width/height from the IHDR chunk (stdlib only)."""
    import struct
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return 800, 500
    w, h = struct.unpack(">II", head[16:24])
    return int(w), int(h)



def png_size(path):
    """Read PNG width/height from the IHDR chunk (stdlib only)."""
    import struct
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
    s = s.replace("\\|", "|")
    return s


out, para_buf = [], []
lines = text.splitlines()
i, in_code, code_buf = 0, False, []


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
        code_buf.append(ln); i += 1; continue
    m_img = re.match(r"!\[(.*?)\]\((.*?)\)\s*$", ln.strip())
    if m_img:
        flush()
        _p = (FINAL / m_img.group(2))
        _w, _h = png_size(_p)
        _hpx = max(40, int(round(540.0 * _h / max(_w, 1))))
        out.append(f'<p class="img"><img src="{m_img.group(2)}" width="540" height="{_hpx}"></p>')
        i += 1; continue
    if ln.startswith("### "):
        flush(); out.append("<h3>" + inline(ln[4:]) + "</h3>"); i += 1; continue
    if ln.startswith("## "):
        flush(); out.append("<h2>" + inline(ln[3:]) + "</h2>"); i += 1; continue
    if ln.startswith("# "):
        flush(); out.append("<h1>" + inline(ln[2:]) + "</h1>"); i += 1; continue
    if ln.strip() == "---":
        flush(); out.append("<hr/>"); i += 1; continue
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
            t = ['<table border="1" cellpadding="4" cellspacing="0" '
                 'style="border-collapse:collapse;width:100%">']
            for ridx, row in enumerate(tbl):
                row = row + [""] * (ncols - len(row))
                tag = "th" if ridx == 0 else "td"
                t.append("<tr>" + "".join(
                    f'<{tag} style="border:1px solid #444;padding:3px 5px">{inline(c)}</{tag}>'
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
    if re.match(r"^\s*\d+\.\s", ln):
        flush()
        items = []
        while i < len(lines) and re.match(r"^\s*\d+\.\s", lines[i]):
            items.append(re.sub(r"^\s*\d+\.\s", "", lines[i])); i += 1
        out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
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
        para_buf.append(ln.strip())
    else:
        flush()
    i += 1
flush()

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
(FINAL / "P2_FINAL_REPORT.html").write_text(
    "<!DOCTYPE html><html><head><meta charset='utf-8'><title>P2 Final Report</title>"
    "<style>" + css + "</style></head><body>" + "\n".join(out) + "</body></html>",
    encoding="utf-8")

def soffice(*args):
    cmd = ["soffice", "--headless", f"-env:UserInstallation={PROFILE}", *args]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    print(" ".join(args[:2]), r.returncode)
    return r

soffice("--convert-to", "odt", "--outdir", str(FINAL), str(HTML))
subprocess.run([sys.executable, str(ROOT / "p2" / "tools" / "embed_odt_images.py"),
                str(FINAL / "P2_FINAL_REPORT.odt")], check=True)
soffice("--convert-to", "docx:MS Word 2007 XML", "--outdir", str(FINAL),
        str(FINAL / "P2_FINAL_REPORT.odt"))
soffice("--convert-to", "pdf", "--outdir", str(FINAL), str(FINAL / "P2_FINAL_REPORT.odt"))
