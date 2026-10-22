# WORKLOG

Append-only project work log.

## 2026-09-29 — Repository initialization
- Created V2 architecture for five-paper reproduction.
- Defined dual-platform strategy: MuJoCo for contact/force unit validation; Isaac/ROS2 for final benchmark.
- Defined mandatory traceability rules for Codex.
- Next task: TASK00 Environment Audit.

## 2026-09-30 — TASK00 environment audit started
- Cloned the repository and opened `task00-environment-audit` from `main`.
- Began read-only host, ROS 2, MoveIt, Isaac Sim, model and runtime-interface checks.
- No paper algorithm or benchmark geometry has been changed.

## 2026-09-30 — TASK00 environment audit completed
- Recorded host/GPU/ROS/MoveIt/OMPL/FCL/Isaac/MuJoCo versions and exact probe commands in reports/TASK00_ENVIRONMENT.md.
- Corrected the initial system-Python-only MuJoCo finding: MuJoCo 3.13.0 works in the existing isolated .venv; its minimal step was logged under results/.
- Expanded the legacy dual-FR3 URDF/SRDF, sampled live ROS interfaces while available, and marked unavailable or untested scientific interfaces explicitly.
- TASK00 PASS is an audit result, not a claim of benchmark readiness. TASK01 is READY but cannot be FROZEN before user review.

## 2026-10-21 — P1 G0 paper study and reproduction planning
- Created `reproduce-p1-numerical-20261021` from `main@a596c973`; no accepted P2/P3/P4/P5 branch content was modified.
- Read the full 19-page T-RO paper (PDF SHA256 `8b4589ce…de3c`), rebuilt every equation's assumptions/inputs/outputs/dimensions, and resolved the absolute-pose equation by three independent arguments (group midpoint, base-frame invariance, official kernel).
- Audited both official repositories at two fixed snapshots each (`dual_arm_gpu_mpc@fe5b49f7` / `@1820a9e8`; `cuda_dq_kernel@231f130e` / `@c762b7d6`), recording tarball and key-file SHA256, dependency stacks, structure, examples, model assets, and missing components.
- Built the paper-equation-to-source map (35 items: 17 ORIGINAL, 7 CODE_MODIFIED, 4 MISSING, 1 AMBIGUOUS, 6 EXTERNAL_DEPENDENCY) and the 16-row original-experiment matrix with per-task reported values.
- Wrote the 16-module proposed reproduction matrix (A–G) with independent oracles, positive/negative controls, quantitative acceptance criteria, dependencies, compute cost, and expected fidelity.
- Wrote the implementation plan as DRAFT only. No dependency was installed, no CUDA extension compiled, no GPU context initialized, and no paper algorithm was executed.
- Open scientific decisions Q1–Q10 are recorded in `p1/P1_IMPLEMENTATION_PLAN.md` §5; G1 must not start before they are resolved.

## 2026-10-21 — P1 G1–G3 numerical reproduction
- Implemented a pure-NumPy package `p1/src/p1_repro/`: DQ algebra, independent SE(3) oracle, DH/MDH chains, relative/absolute pose, analytic relative Jacobian, null-space projection, cost terms, three samplers, single-stage MPPI, k-means + mode selection + two-stage refinement, dual-arm and two-corridor tasks, auxiliary/L switching.
- G1: FK 4e-16 m, Jacobian vs central differences 2e-10, rank 6, projector idempotent 3e-15, projected drift slope 2.000 vs unprojected 1.001, drift ratio 1.0e4 at Th=0.005.
- G2: single-stage MPPI within 3% of the finite-horizon LQR cost (50/50 seeds), estimator variance ratio 0.994, L-indicator slope/saturation/dwell ratio exact (8.00), dual-arm task reaches 2.0–2.3 cm with equality drift ~1e-6, no collisions, tilt <1.1 deg.
- G3: clustering recovers the two corridor modes at 0.872; two-stage 0.43 success vs single-stage 0.00 at equal budget (0.057 vs 0.152 m); ablation shows the second re-weighting pass, not clustering, drives the gain in this task (no-cluster 0.90). Negative result kept and explained.
- New findings: official 1e-16 damping gives |N^2-N|=0.247 in float64; Eq. (45) leaves an absolute-task residual of 0.0115 vs 3.8e-5 for the priority-consistent form.
- 31 tests pass (`cd p1 && python -m pytest tests -q`). No CUDA install, no GPU context, no ROS/cuRobo.

## 2026-10-21 — P1 numerical scope fixed; auxiliary finisher and mode inertia
- User decision D007: P1 is numerical-algorithm-only; GPU/simulation/hardware are out of scope. G4 closed in the plan and status.
- Auxiliary finisher: capped per-step Newton motion (0.05 rad) on the priority-consistent projection. With eta=1.0 the L switch engages, error decreases monotonically 1.98 -> 0.92 cm, drift 7.1e-7, aux fraction 1.0; with Table I's eta=0.1 it never engages (Ct/Cs ~ 1).
- Mode inertia (keep the previous cluster unless beaten by 0.6x): two-stage success 0.35 -> 0.55, still below the no-cluster variant 0.90. The published elite-majority rule is unstable for symmetric modes.
- Reports regenerated; one f-string escape bug (\\approx) fixed in the G2 renderer.

## 2026-10-22 — paper-faithful defaults; coloured-noise fix; variant comparison; open issues
- Kept the paper's eta=0.1 and the elite-majority mode rule as the main configuration; eta=1.0 and mode inertia remain diagnostics/ablations only.
- Found and fixed the coloured-noise scaling: the transcribed official formula inflates the time-domain std ~630x (0.15 -> 94); renormalised to the requested std while preserving the 1/f^gamma shape (lag-1 ~0.76). [ENGINEERING], recorded in OPEN_ISSUES P4.
- Implemented the singularity cost (Eq. 36-37): w~0.024 -> C_sing=422 vs C_goal~2.7 (150x); near-constant across samples so the task still reaches ~2.4 cm, but the weighting is not scale-invariant (OPEN_ISSUES N3).
- Added a controller-variant comparison (G3B): Gaussian/Log/CEM/Biased MPPI reach 1.0; two-stage 0.67; coloured 0.43. With the corrected noise the earlier "mode averaging" results change: two-stage no longer beats single-stage (G3 F1: 0.67 vs 0.67, no-cluster 1.00 vs full 0.60). Stable negative result N1 recorded in OPEN_ISSUES.md.
- Regenerated G2/G3/G3B reports; added OPEN_ISSUES.md.

## 2026-10-22 — D008 scientific audit
- Corrected D2: both aggregators now use the same global temperature; the historical cluster-local measurement is preserved and labelled. Result unchanged (3/20, paired CI includes 0).
- Corrected the stage-2 ablation: renamed the old variant to `no_variance_reduction`, added a genuine `stage2=False` bypass with a monkeypatch regression test, and separated mechanism-isolation (500/iter) from budget-matched (1000/iter) comparisons.
- Fixed the D2 report discrepancy (3/20 vs 0/20) by generating all report numbers from JSON and adding a regression test.
- Mode inertia now associates clusters by centroid distance (permutation-equivariant test); it remains a diagnostic and the paper's elite-majority rule stays primary.
- G3B fairness recorded (effective std, clipping fraction, lag-1, budgets, paired seeds, Wilson CI, McNemar). Two-stage 20/30 vs Gaussian 30/30 (p=0.002).
- N2 traces added (C_t, C_s, ratio, L, aux, error per cycle); N3 audit added (w ~ L^2.71, p_e/w dimension L^-2.71, ~5% control effect).
- Regenerated G1/G2/G3/G3B/N3 reports; added D008_AUDIT.md, CHINESE_REPORT_OUTLINE.md and four report figures.
- Acceptance recommendation: PARTIALLY_VERIFIED (blockers B1-B3 are paper-clarification issues).
