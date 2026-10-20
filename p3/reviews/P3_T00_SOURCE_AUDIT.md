# P3-T00 — Source equation audit (Eq. 16–28) + PRE-TASK report

**Status**: `SOURCE_AUDIT_COMPLETE`
**Date**: 2026-10-20 | **Branch**: `reproduce-p3-paper-study-20261019` | **Base**: `5e43cf05`
**Paper**: Lee et al., *Peg-in-Hole Assembly With Dual-Arm Robot and Dexterous Robot Hands*, IEEE RA-L 7(4):8566–8573, 2022. DOI `10.1109/LRA.2022.3187497`.
**PDF**: `papers_and_reference_all/references/private_sources/P3_original.pdf`, 8 pp., SHA256 `d16235aa3af25e8e8a52299abb8d1e47c5f9190b3e766f2450cd963687139bd1` (matches `SHA256SUMS.txt`).
**Evidence images**: `p3/evidence/pdf_pages/` (`page-4.png`…`page-7.png`, `eq16_18_zoom.png`, `eq19_21_zoom.png`, `eq21_zoom.png`, `eq19_22_zoom.png`, `eq27_zoom.png`, `fig5_zoom.png`).

## 1. PRE-TASK report (AGENTS.md §1)

```text
=== PRE-TASK REPORT ===
Task:                P3 core algorithm numerical reproduction (T01→T02→T03→T04→T06), D082 scope
Scientific objective: establish that the arm-level algorithms of Eq.(16)-(28) are implemented
                     faithfully and validated by independent mathematics (not by self-consistency)
Minimum evidence:    per-equation transcription audit against PDF page images; analytic spot checks
                     computed independently of production code; deterministic positive + mutation
                     negative tests; virtual-work identity; plotted traces with explicit units
Current scope:       patterns (16-22), stage composition (23-26), selection/frame (27-28), torque law
                     (27) end-to-end, deterministic integration of the four documented stage sequences
Explicit non-goals:  Eq.(1)-(15) dexterous-hand mechanisms; 50-DOF hardware; 87%/13.86 s statistics;
                     MuJoCo/Isaac deployment; contact dynamics; automatic stage recognition;
                     Fig.9/Fig.11 trajectory reproduction; any claim of FULL_PAPER_REPRODUCED
Attempt budget:      3 evidence-based iterations per root blocker (AGENTS.md §5.2)
Preferred method:    source-faithful pure NumPy implementation in baselines/p3_peg_in_hole/ +
                     separate oracles in p3/oracles/ that never import production code
Fallback method:     analytic scalar closed forms at prescribed sample times for any component whose
                     vector form is ambiguous (still independent of production code)
Stop / escalation:   material source ambiguity that changes implementation; scope increase;
                     exhausted budget on one blocker
Files expected:      baselines/p3_peg_in_hole/*, p3/tools/run_t0*.py, p3/oracles/*,
                     p3/reviews/*, results/20261020_P3-T0*/
Validation plan:     per-task PRE/POST + JSON + figures; independent oracle residual printout
Known ambiguities:   A1 push-axis naming (z) vs selection axis (x); A2 K_p matrix/packaging;
                     A3 missing numeric parameters; A4 a constant in Eq.(18) vs a(t) in Eq.(22);
                     A5 wrench rotation without translation; A6 tau_f unspecified
Need user confirmation: NO (all ambiguities resolvable without changing acceptance properties;
                     see §4 for the argument and the recorded [ADAPTATION] labels)
```

## 2. Verbatim transcription (audited from page images, not from pdftotext)

Page 5 (p.8570), Eq.(16)–(24); page 6 (p.8571), Eq.(25)–(28).

| Eq. | Verbatim content | Components / units |
|---|---|---|
| (16) | `w = [w1 w2 w3 w4 w5 w6]^T` | `[w1,w2,w3]` translation force components in x,y,z; `[w4,w5,w6]` rotation force (moment) components in x,y,z |
| (17) | `w_i = a_i sin(b_i t + c_i) + d_i, i ∈ {1..6}` | `a_i` amplitude (N or N·m), `b_i` angular frequency (rad/s), `c_i` phase (rad), `d_i` bias (N or N·m), `t` (s) |
| (18) | `w = diag(a) vsin(t b + c) + d`, `a,b,c,d ∈ R^{6×1}` | element-wise sine; `tb+c` means `t·b + c` (so `b` is rad/s) |
| (19) | push: `a = b = c = 0^T`, `d = [0 0 f_push 0 0 0]^T` | push along **z**, force magnitude `f_push` (N) |
| (20) | rub: `a = [0 0 0 0 0 f_rub]^T`, `b = [0 0 0 0 0 v_rub]^T`, `c = d = 0^T` | rotation about **z**; `f_rub` is a **moment** amplitude (N·m), `v_rub` (rad/s) |
| (21) | wiggle: `a = [0 0 0 f_wiggle f_wiggle 0]^T`, `b = [0 0 0 v_wiggle v_wiggle 0]^T`, `c = [0 0 0 0 π/2 0]^T`, `d = 0^T` | rotation about **x and y**; phase π/2 sits on the **5th** component (my) → my is a cosine relative to mx |
| (22) | spiral: `a = [f_spiral(t) f_spiral(t) 0 0 0 0]^T`, `b = [v_spiral v_spiral 0 0 0 0]^T`, `c = [0 π/2 0 0 0 0]^T`, `d = 0^T`, `f_spiral(t) = α sin(v_spiral t) + β` | translation spiral in **x–y**; `α` amplitude of the amplitude modulation (N), `β` mean magnitude (N), `v_spiral` (rad/s) |
| (23) | `w_approach = w_push` | — |
| (24) | `w_search = w_push + w_spiral` | — |
| (25) | `w_align = w_push + w_wiggle + w_rub` | — |
| (26) | `w_insert = w_push` | — |
| (27) | `τ = J^T [[Ω,0],[0,I]] K_p Δx + J^T [[R_h,0],[0,R_h]] w − D q̇ + τ_g + τ_f` | `J ∈ R^{6×n}` (arm Jacobian); `K_p ∈ R^{6×6}`; `Δx ∈ R^6`; `w ∈ R^6`; `D` damping; `τ_g`,`τ_f` (N·m) |
| (28) | `Ω = R_h Σ R_h^T`, `Σ = diag([0 1 1])` | `Ω ∈ R^{3×3}`; `R_h` = rotation of hole w.r.t. global reference |

Text checks that constrain the implementation (page 6):
- "The first term generates the joint torque for regulating the desired task-space position **excluding the axis in which the pushing force is applied**."
- "This is done via a **generalized task specification matrix** Ω ∈ R^{3×3}" — hence Ω is 3×3 and the selector in (27) is the 6×6 block `[[Ω,0],[0,I₃]]`.
- "**there is no force feedback term**" — the perturbation is user-commanded feedforward. No measured external force may enter the law.
- Hole arm uses Eq.(15) with "medium position gain, 500 ≤ k_p ≤ 1000" (Eq.(15) is hand/arm-level position control; hand-level Eq.(1)-(15) remain out of scope except this gain statement).

## 3. Numeric parameter availability

The paper gives **no numeric values** for `f_push`, `f_rub`, `v_rub`, `f_wiggle`, `v_wiggle`, `α`, `β`, `v_spiral`, `D`, `τ_f`, `K_p` (except the hole-arm scalar range 500–1000), nor the arm Jacobian or error trajectory.
→ All such values used in validation are tagged **`TEST_FIXTURE`** and are *illustrative only*; no numeric agreement with the paper is claimed or possible.

## 4. Ambiguity register and resolutions

| ID | Ambiguity | Resolution (label) | Does it change acceptance properties? |
|---|---|---|---|
| A1 | Push is along **z** (Eq.19, Fig.5a) but §IV-D fixes the position-excluded axis as **x** (`Σ=diag([0 1 1])`). | The task/peg frame (Fig.5) and the hole frame (Eq.28) differ by an axis relabelling. Implement `R_h` literally (hole→reference) and carry an **explicit** `R_task_to_hole` mapping `e_z → e_x` (rotation about y by +π/2) for the composite command. Both LITERAL (identity map) and CONSISTENT variants are exercised in T03. **[ADAPTATION: frame naming]** | **No.** Ω depends on `R_h` only through the axis `R_h e_x`; any rotation mapping the push axis onto `e_x` yields the same projector, so all projector/annihilation properties are invariant. Verified numerically in T03 (both variants). |
| A2 | `K_p` printed upper-case in (27) vs lower-case `k_p` in (12)-(15); no matrix packaging given. | `K_p = blkdiag(k_p·I₃, k_p_rot·I₃)` as a 6×6 diagonal; translation gain N/m, rotational gain N·m/rad. Hole-arm scalar in [500,1000] is the only paper anchor. **[TEST_FIXTURE for numbers]** | No — packaging is forced by `K_p Δx` with `Δx ∈ R⁶`. |
| A3 | `a` declared constant in Eq.(18) but set to `f_spiral(t)` in Eq.(22). | Implement `w = a(t) ⊙ sin(t b + c) + d` with `a(t)` allowed to be time-varying for spiral. **[ORIGINAL: Eq.(22) is explicit; Eq.(18) notation is loose]** | No — Eq.(22) is unambiguous. |
| A4 | Wrench rotation uses `blkdiag(R_h,R_h)` with **no translation term**, while a general frame change requires `Ad^T`. | Treat `w` as a *direction* wrench in the hole frame with coincident origins (paper's assumption). **[ORIGINAL + documented assumption]** | No for rotation-only frames; recorded as limitation (nonzero origin offset unmodelled). |
| A5 | `τ_f` friction compensation form unspecified. | External input, not modelled; fixture supplies a constant vector. **[TEST_FIXTURE]** | No — term is additive and independently injected. |
| A6 | Stage switching manual in the paper (p.8572: "transitions between the stages were manually controlled"); no criterion given. | Externally prescribed piecewise schedule, validated as contiguous/ordered. **[ADAPTATION: manual phase script]** | No — schedule is an input, not an inferred state. |
| A7 | Fig.5 push axis drawn as z while the peg approaches a horizontal hole; Fig.6 uses its own triad. | Accept the paper's own z-push convention (Eq.19 is explicit). | No. |

No ambiguity forces a guessed equation. **No escalation required.**

## 5. Acceptance mapping to the review decision

| Task | Review acceptance | Implementation | Independent evidence |
|---|---|---|---|
| T01 | Eq.16–22 transcription + analytic spot checks + invariants; reject non-finite/dimension errors; mutations detected; `b=0` constant allowed; `β<0` not rejected | `baselines/p3_peg_in_hole/patterns.py` | `p3/oracles/oracle_patterns.py` (scalar closed forms) |
| T02 | Eq.23–26 compositions + prescribed schedule + all four documented sequences; detect wrong combination/unknown stage/order; report boundary discontinuities | `stages.py` | `p3/oracles/oracle_stages.py` |
| T03 | Ω properties from source page; frame covariance; mutant frames detected; singular J not rejected; no `‖Jᵀw‖=‖w‖` claim | `control.py` | `p3/oracles/oracle_selection.py` |
| T04 | every source-confirmed term, ordering, frames; virtual work; affine response; mutation of sign/frame/term; no measured force feedback | `control.py::arm_torque` | `p3/oracles/oracle_torque.py` |
| T06 | finite command/torque timelines for all stage sequences; missing stage/dead branch/clock checks; **no** Fig.9/11 or success-rate claim | `p3/tools/run_t06_integration.py` | T02/T04 oracles + identity checks |
| T05 | optional, isolated | **SKIPPED** (recorded in POST as not executed; no acceptance dependency) | — |

## 6. Labels used in this program

`ORIGINAL` — follows the paper equation; `ADAPTATION` — mapping/relabelling required by the environment; `ENGINEERING` — software detail; `TEST_FIXTURE` — illustrative numeric value (not from the paper); `EXPERIMENTAL` — our own extension; `OUT_OF_SCOPE_D082` — not reproduced.
