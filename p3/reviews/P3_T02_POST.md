# P3-T02 POST — Assembly-stage composition (Eq.23–26)

**Status**: `PASS` — 16/16 checks (metrics corrected 2026-10-20, review R3).
**Run**: `results/20261020_104220_P3-T02_stages/results.json`
**Superseded run (preserved)**: `results/20261020_093810_P3-T02_stages/results.json` (mixed jump norm)
**Command**: `/usr/bin/python3.10 p3/tools/run_t02_stages.py`
**Code**: `baselines/p3_peg_in_hole/stages.py` **[ORIGINAL composition / ADAPTATION schedule]**
**Figures**: `p3_t02_case1_wrench.png`, `p3_t02_boundary_jumps.png`

## 1. Composition evidence

| Check | Content | Residual |
|---|---|---|
| T02_01 | approach = push (Eq.23) vs oracle | 0 |
| T02_02 | search = push + spiral (Eq.24) | 0 |
| T02_03 | align = push + wiggle + rub (Eq.25) | 0 |
| T02_04 | insert = push (Eq.26) | 0 |
| T02_05 | structural separation: approach/insert carry no oscillation; search adds spiral fx; align adds wiggle mx and rub mz | behaviour |

## 2. Four documented case sequences

| Case | Sequence | Boundaries [s] | Evidence |
|---|---|---|---|
| case1 approach-search-align-insert | 4 stages | 0 / 3.2 / 10.5 / 16.5 / 17.5 | digitized qualitatively from Fig.9 **[ADAPTATION]** |
| case2 approach-search-insert | 3 stages | 0 / 3.5 / 9.0 / 14.0 | illustrative **[ADAPTATION]** |
| case3 approach-align-insert | 3 stages | 0 / 3.0 / 12.0 / 16.5 | illustrative **[ADAPTATION]** |
| case4 approach-insert | 2 stages | 0 / 4.0 / 8.0 | illustrative **[ADAPTATION]** |

T02_06: stage attribution and wrench equality on a 17-point grid per segment —
`seq_ok = True`, `stage_errors = 0`, `maxdiff = 0`. Case boundaries are **externally
prescribed**, mirroring the paper's manual switching (p.8572); no automatic phase
recognition is implemented.

## 3. Boundary discontinuities (reported, not errors)

| Boundary | Force jump ‖Δf‖₂ [N] | Moment jump ‖Δm‖₂ [N·m] |
|---|---:|---:|
| approach→search | 1.824 (equals the spiral force magnitude at t = 3.2 s) | 0.000 |
| search→align | 5.000 | 0.391 |
| align→insert | 0.000 | 0.391 (residual wiggle/rub phase at 16.5 s) |

Force and moment jumps are now reported separately (review R3). The concatenated 6-vector norm is
retained in the JSON only as `jump_mixed_l2_unphysical` — a dimensionless, unnormalized diagnostic
that must not be quoted as a physical quantity (it adds newtons to newton-metres).

The jumps are legitimate command changes; the driver reports them (JSON
`boundary_jumps`) instead of smoothing or rejecting them.

## 4. Negative and mutation evidence

| Check | Content | Result |
|---|---|---|
| T02_N1 | unknown stage `dwell` | rejected |
| T02_N2 | non-contiguous schedule | rejected |
| T02_N3 | zero-length/backwards segment | rejected |
| T02_N4 | wrong boundary count | rejected |
| T02_N5 | unknown case | rejected |
| T02_N6 | time outside schedule | rejected |
| T02_M1 | aligning without rub | **detected** (0.136 N·m) |
| T02_M2 | searching without push | **detected** (10 N) |
| T02_08 | approach ≡ insert by Eq.(23)/(26) | documented equivalence, not a defect |

## 5. Limitation

This validates *command composition*, not assembly behaviour. Approach and insert are
identical commands by construction (Eq.23 vs Eq.26), so stage labels — not wrench values —
distinguish them; the report does not claim stage recognition.
