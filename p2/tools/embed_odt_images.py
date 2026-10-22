#!/usr/bin/env python3
"""Embed linked images into an ODT (Pictures/ + manifest), in place."""
import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import quoteattr

odt = Path(sys.argv[1]).resolve()
base = odt.parent
tmp = base / (odt.stem + "_embed_tmp")
if tmp.exists():
    shutil.rmtree(tmp)
tmp.mkdir()

with zipfile.ZipFile(odt) as z:
    names = z.namelist()
    z.extractall(tmp)

content = (tmp / "content.xml").read_text(encoding="utf-8")
manifest = (tmp / "META-INF" / "manifest.xml").read_text(encoding="utf-8")

hrefs = set(re.findall(r'xlink:href="([^"]+)"', content))
added = []
for href in sorted(hrefs):
    if href.startswith("#") or href.startswith("Pictures/"):
        continue
    cand = [(base / href).resolve()]
    name = Path(href).name
    cand += list(base.glob(f"**/{name}"))
    src = next((c for c in cand if c.exists() and c.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif")), None)
    if src is None:
        continue
    dest_name = "Pictures/" + src.name
    (tmp / "Pictures").mkdir(exist_ok=True)
    shutil.copy2(src, tmp / dest_name)
    content = content.replace(f'xlink:href={quoteattr(href)}', f'xlink:href={quoteattr(dest_name)}')
    added.append(dest_name)
    ext = src.suffix.lstrip(".").lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}[ext]
    entry = f'<manifest:file-entry manifest:full-path={quoteattr(dest_name)} manifest:media-type="{mime}"/>'
    manifest = manifest.replace("</manifest:manifest>", entry + "</manifest:manifest>")

(tmp / "content.xml").write_text(content, encoding="utf-8")
(tmp / "META-INF" / "manifest.xml").write_text(manifest, encoding="utf-8")

out = odt.with_suffix(".odt")
with zipfile.ZipFile(out, "w") as z:
    z.write(tmp / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
    for p in sorted(tmp.rglob("*")):
        if p.name == "mimetype" or not p.is_file():
            continue
        z.write(p, str(p.relative_to(tmp)), compress_type=zipfile.ZIP_DEFLATED)
shutil.rmtree(tmp)
print(f"embedded {len(added)} images into {out}")
