# P3-T03 POST — Force/position selection and frames (Eq.27–28)

**Status**: `PASS` — 23/23 checks (corrected 2026-10-20, review R1).
**Run**: `results/20261020_104153_P3-T03_selection/results.json`
**Superseded run (preserved)**: `results/20261020_094115_P3-T03_selection/results.json` (22 checks, T03_12 tautological)
**Command**: `/usr/bin/python3.10 p3/tools/run_t03_selection.py`
**Code**: `baselines/p3_peg_in_hole/control.py` **[ORIGINAL Eq.(27)-(28)]** · Oracle: `p3/oracles/oracle_control.py` (`Ω = I − n nᵀ`, a different derivation)
**Figures**: `p3_t03_selection.png`, `p3_t03_mutations.png`

## 1. Selector algebra

| Check | Content | Residual |
|---|---|---|
| T03_01 | `Ω = R_h diag([0,1,1]) R_hᵀ` vs complementary-projector oracle | 1.1e-16 |
| T03_02 | symmetry `Ωᵀ = Ω` | 0 |
| T03_03 | idempotence `Ω² = Ω` | 1.1e-16 |
| T03_04 | rank 2 — singular values {1, 1, 0} | spectrum |
| T03_05 | `Ω(R_h e_x)=0`, `Ω(R_h e_y)=R_h e_y`, `Ω(R_h e_z)=R_h e_z` | ≤1.1e-16 |
| T03_06 | frame covariance `Ω(R₂R₁)=R₂Ω(R₁)R₂ᵀ` | 1.1e-16 |
| T03_07 | 6×6 block `[[Ω,0],[0,I₃]]` exact structure | 0 |
| T03_08 | selector symmetric + idempotent, rank 5 | 1.1e-16 |

## 2. Units, frames, power

| Check | Content | Residual |
|---|---|---|
| T03_09 | `blkdiag(R_h,R_h)` vs oracle, orthonormal | 0 |
| T03_10 | paired wrench/twist power `(W_R w)ᵀ(W_R V) = wᵀV` | 2.2e-16 |
| T03_11 | dimensions: `F ∈ R⁶`, `τ ∈ R⁷` | shapes |
| T03_12 | **A1 (corrected)**: `Ω(R_h)` annihilates the *physical* push direction `p_ref = R_h(R_task→hole e_z)` | 8.5e-17 |
| T03_15 | **negative control**: literal frame (`R_h=I`, no relabelling) leaves `e_z` un-annihilated (`‖Ω(I)e_z‖=1`) | 1.0 (dimensionless) |
| T03_13 | rank-deficient `J` (rank 5) accepted; `JᵀF` finite | \|τ\| = 11.03 N·m |
| T03_14 | no norm-preservation claim: `‖JᵀF‖/‖F‖ ≠ 1` reported | 1.001 |

**A1 resolution (recorded, corrected)**: the paper builds `w` with push along z (Eq.19/Fig.5) but fixes
`Σ = diag([0 1 1])` in a frame whose insertion axis is x. This is a **real source ambiguity**, not a
tautology: the two readings are both valid projectors but exclude *different physical directions*.
The relabelled (CONSISTENT) variant excludes the task push axis — `Ω(R_h)·p_ref = 0` at 8.5e-17 with
`p_ref = R_h(R_task→hole e_z)` (T03_12). The literal reading excludes `R_h e_x`; with `R_h = I` the
push direction stays fully inside the position-controlled subspace (`‖Ω(I)e_z‖ = 1`, T03_15). We adopt
the relabelled convention as **[ADAPTATION: frame naming]** and retain the literal variant for audit
only. The paper does not state which convention was intended, so this is **not** claimed as
paper-established.

## 3. Negative and mutation evidence

| Check | Content | Result |
|---|---|---|
| T03_N1 | non-orthonormal `R_h` (×1.02) | rejected |
| T03_N2 | improper rotation (`det = −1`) | rejected |
| T03_N3 | NaN `R_h` | rejected |
| T03_N4 | wrong shape (2×2) | rejected |
| T03_M1 | transpose mutation `R_hᵀ` | detected (0.822) |
| T03_M2 | force rotated, moment not | detected (0.266 N/N·m) vs frame-consistent oracle |
| T03_M3 | `Σ = diag([1,0,1])` (wrong selected axis) | detected (0.837) |
| T03_M4 | non-orthonormal force block breaks power invariance | detected (0.133 W²) |

**Methodological finding**: the scalar power `wᵀV` is invariant under *any* block-orthonormal
transform, including one whose force and moment blocks disagree. Power invariance therefore
**cannot** detect a force-only frame error; the mutation must be compared against the
frame-consistent oracle (T03_M2). This is recorded to prevent an over-strong claim later.

## 4. Scope statement

- Singular Jacobians are not treated as a failure of the `Jᵀ` mapping (T03_13); no pseudo-inverse
  is required by Eq.(27).
- No claim `‖Jᵀw‖ = ‖w‖` is made (T03_14 reports the ratio explicitly).
- The 3×3/6×6 block structure is taken from the page image (`P3_T00_SOURCE_AUDIT.md`, `eq27_zoom.png`),
  not from the compressed `pdftotext` stream.
