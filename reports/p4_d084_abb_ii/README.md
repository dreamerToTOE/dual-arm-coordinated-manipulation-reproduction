# D084 S1 — ABB Environment II saved-path visualization

This package is a read-only visualization of four already saved and independently qualified Environment II paths. It adds no planner, IK, collision, or path-qualification call. The figure uses each path’s saved node poses for the full TCP trace and renders start, saved midpoint, and goal snapshots with the frozen aligned source CAD-frame convention.

## Contents and hashes

| File | SHA-256 |
|---|---|
| `fig_S1_abb_ii_four_saved_paths.png` | `e6a02829b072c7f166fe060849801df3fa7f40fcc99f6fcb0e2916c5cd45cc0e` |
| `fig_S1_abb_ii_four_saved_paths.pdf` | `9190e6ae0e113146bfb60fa9b8096137280f443c88425fba3be88d73a7dd1ce7` |
| `abb_ii_metrics.json` | `c08a634eb7d586860ed773453f218e59209c0b73014fb855661c800d5e90a08a` |
| `manifest.json` | `a7a507c1b04732afc162d5c578c6c1af2c29082da1affdee34132884ecd9cdd3` |
| `render_abb_ii.py` | `0138c7d87d0a4398287843285fed21611a7c828b97b53a78ba0b28ceafb1f134` |

The canonical D083 renderer used for the source-bound convention is `scripts/p4_d083/render_spatial.py` (SHA-256 `6ca4aba948760cabcc7d425ff9c230fb6d21cb18e10987b0ee6216deb88811ba`). The full input and output hash map is in `manifest.json`.

## Saved path inputs

| Path | Saved nodes / leaves | Source certificate | Certificate SHA-256 |
|---|---:|---|---|
| RRT / PCS | 177 / 176 | `reports/P4_FULL_R2_ABB_RRT_PATH_INDEPENDENT_SAVED_POST_REVIEW_20261015.json` | `637d294b65a7baed72e08f326b232e9e7d98b284d81bd6f6790f382941ac2073` |
| CBiRRT / PCS | 413 / 412 | `reports/P4_FULL_R2_ABB_CBIRRT_D_PATH01_SAVED_INDEPENDENT_POST_20261016.json` | `2c548df054867c7d9545fac3726142f3581b3cdfbe54299233a27bb07bace4d0` |
| RRT / NR | 393 / 392 | `reports/P4_FULL_R2_ABB_RRT_NR_PATH_ROOT_INDEPENDENT_POST_20261016.json` | `0558fb854839edadfead071ba0bcfa0c43ea26079281c59cbcafb036720b21b0` |
| CBiRRT / NR | 689 / 688 | `reports/P4_FULL_R2_ABB_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST_20261017.json` | `b3a2443cb790df547597fe5a72b4eeb78341d2f93a4b4beca8252eba692c40c8` |

The corresponding frozen configs are recorded in `manifest.json`. The private author mesh directory is never copied into this package; its ten input SHA-256 values are recorded there and are checked by the script.

## Evidence boundary

The saved certificates report maximum full-12 joint leaf distances of 0.0494905 (RRT/PCS), 0.0498729 (CBiRRT/PCS), 0.0478001 (RRT/NR), and 0.0495190 rad (CBiRRT/NR). Their saved closure residuals, source mechanical margins, and collision-query scope remain certificate values in `abb_ii_metrics.json`; they are not recomputed or upgraded here. The dark object bar is a display glyph. The package does not certify native TCP equivalence, continuous CCD, minimum clearance, omitted collision pairs, solid-rod safety, dynamic execution, or PCS superiority.

## Reproduction entry point

Use a new output directory so frozen outputs are not overwritten:

```bash
python3 scripts/p4_d084/render_abb_ii.py \
  --mesh-root /path/to/author/CKCplanning/simulator \
  --output reports/p4_d084_abb_ii_replay01
```

The command reads saved records and performs render-only frame construction. It does not invoke the planner or qualification checker.
