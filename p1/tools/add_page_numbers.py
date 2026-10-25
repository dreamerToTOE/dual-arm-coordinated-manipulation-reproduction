#!/usr/bin/env python3
"""Add a centred, continuous page-number footer to an ODT (in place).

LibreOffice's HTML import produces master pages without a footer, and CSS
``@page`` counters are not mapped to ODF fields, so this injects a
``text:page-number`` field into every master page after the HTML->ODT step.
"""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

FOOTER_STYLE_NAME = "P1Footer"


def main(odt_path: str):
    odt = Path(odt_path).resolve()
    tmp = odt.parent / (odt.stem + "_pgnum_tmp")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()

    with zipfile.ZipFile(odt) as z:
        z.extractall(tmp)

    styles = tmp / "styles.xml"
    s = styles.read_text(encoding="utf-8")

    # 1) define a centred footer paragraph style once
    if f'style:name="{FOOTER_STYLE_NAME}"' not in s:
        para = (
            f'<style:style style:name="{FOOTER_STYLE_NAME}" style:family="paragraph">'
            '<style:paragraph-properties fo:text-align="center" fo:font-size="9pt" '
            'style:justify-single-word="false"/></style:style>'
        )
        # insert into office:styles
        if "<office:styles>" in s:
            s = s.replace("<office:styles>", "<office:styles>" + para, 1)
        else:
            s = s.replace("<office:automatic-styles>", para + "<office:automatic-styles>", 1)

    # 2) add a footer to every master page
    footer = (
        f'<style:footer style:display="true">'
        f'<text:p text:style-name="{FOOTER_STYLE_NAME}">'
        '<text:page-number text:select-page="current">1</text:page-number>'
        "</text:p></style:footer>"
    )
    # self-closing master-page tags -> expand
    import re

    s = re.sub(
        r'<style:master-page ([^>]*?)/>',
        lambda m: f'<style:master-page {m.group(1)}>{footer}</style:master-page>',
        s,
    )
    styles.write_text(s, encoding="utf-8")

    # rezip with mimetype first and stored
    out = odt
    with zipfile.ZipFile(out, "w") as z:
        z.write(tmp / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
        for p in sorted(tmp.rglob("*")):
            if p.name == "mimetype" or not p.is_file():
                continue
            z.write(p, str(p.relative_to(tmp)), compress_type=zipfile.ZIP_DEFLATED)
    shutil.rmtree(tmp)
    print(f"page-number footer added to {out}")


if __name__ == "__main__":
    main(sys.argv[1])
