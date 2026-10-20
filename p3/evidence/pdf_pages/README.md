# P3 source-page evidence

Crops from `private_sources/P3_original.pdf` (SHA256 `d16235aa…139bd1`), used to
transcribe Eq.(16)–(28) from page images rather than `pdftotext`:

| File | Content |
|---|---|
| `eq16_18_zoom.png` | Eq.(16)–(18) and the push parameter set (p.8570, left column) |
| `eq19_21_zoom.png` | Eq.(19)–(20) and the wiggle parameter set |
| `eq21_zoom.png` | Eq.(21) `c = [0 0 0 0 π/2 0]^T` (phase on the 5th component) |
| `eq19_22_zoom.png` | Eq.(22) spiral parameter set and `f_spiral(t)` |
| `eq27_zoom.png` | Eq.(27) block matrices (p.8571) |
| `fig5_zoom.png` | Fig.5 pattern directions and axis triad |
| `fig6_zoom.png` | Fig.6 stage sketches |

Regenerate at 420 dpi with:
`pdftoppm -png -r 420 -f 5 -l 6 <pdf> hi` then crop the columns.
