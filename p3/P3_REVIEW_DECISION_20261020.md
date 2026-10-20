# P3 Review Decision — 2026-10-20

**Status:** APPROVED_WITH_CORRECTIONS for **algorithm-level numerical reproduction** on `reproduce-p3-paper-study-20261019`. This review supersedes the proposed acceptance logic in `p3/P3_PAPER_STUDY_AND_PLAN.md` where they conflict; preserve that study as the historical proposal.

**Paper:** Lee et al., *Peg-in-Hole Assembly With Dual-Arm Robot and Dexterous Robot Hands*, IEEE RA-L 7(4), 2022, DOI 10.1109/LRA.2022.3187497.

## Scope gate

- **Required:** reproduce and independently validate arm-level perturbation patterns, the four stage-command compositions, position/force selection and frame transformations, and paper-faithful task-space command to joint-torque mapping (paper Eq. 16–28, subject to source-image audit).
- **Required integration evidence:** deterministic stage scripts that route commands through the same independently tested numerical pipeline. They demonstrate **command consistency**, not physics or insertion success.
- **Out of scope under D082:** Eq. 1–15 dexterous-hand mechanisms, original 50-DOF hardware, hardware results including 87% / 13.86s, Isaac/MuJoCo deployment, complete contact dynamics, and automatic phase recognition. Record each explicitly as NOT_REPRODUCED / OUT_OF_SCOPE_D082.
- Original paper phase switches were manual. Scripts declaring stage boundaries are **[ADAPTATION]**, not paper-original automatic state estimation. Avoid building a contact-driven state machine unless approved as a separate extension.
- A standalone quasi-static contact/jam surrogate is **optional [EXPERIMENTAL/OUR_EXTENSION]** and is not an acceptance dependency. Never score a surrogate's self-generated insertion success as a reproduced experimental result.
- P3 work remains isolated from P2/P4; do not modify their history, artifacts or branches. Do not generalize the old main-branch benchmark status to block this explicitly approved P3 numerical study.

## Corrected acceptance matrix

| Task | Acceptance | Negative/mutation evidence | Label |
|---|---|---|---|
| T01 Eq.16–22 modes | Source-PDF transcription audit: all symbols, units, force/torque axes, phases, and values. Exact analytical spot checks independent of production code, sample/time invariants, bounds **only if justified by source assumptions**. | Reject nonfinite/dimensionally invalid inputs; swapped sine phase/frequency/amplitude produces test failure. Constant-mode `b=0` is **not** automatically an error; do not reject `beta<0` without a paper-specified domain restriction. | ORIGINAL for actual paper equations; ENGINEERING for tests |
| T02 Eq.23–26 stage combinations | Explicit stage-command composition oracles and externally prescribed stage schedule; reproduce all four documented case *stage sequences* where confirmed by source. | Incorrect combinations, unknown stage, wrong ordering are detected; report any stage-boundary discontinuities rather than assuming they are illegal. | ORIGINAL stage composition; ADAPTATION manual phase script |
| T03 Eq.27–28 projector/frame | Verify precise position-selection operator **from source page**, including translational/rotational block dimensions. For a legitimate orthonormal `R_h` verify `Omega^T=Omega`, `Omega^2=Omega`, selected axis annihilation, rotated-frame covariance, and correctly paired twist/wrench power invariance. | Wrong-frame, transpose/sign, and nonorthogonal rotation mutations detected. **Do not reject singular Jacobians just because rank deficient**. No claim that `||J^T w|| = ||w||`. | ORIGINAL + ENGINEERING tests |
| T04 original full torque law | Reproduce every **source-confirmed** term, preserve ordering and frames of `J`, `R_h`, position command, damping, gravity/friction compensation; confirm exact expression on paper PDF screenshot rather than copying the study's compressed shorthand. Independent numerical oracle, virtual work `(J^Tw)^T qdot = w^T(J qdot)`; affine response to feedforward wrench for fixed state. | Inject sign/frame/control-term mutations; verify no *measured external force feedback* added silently. **Singular `J` need not make `J^Tw` diverge**. | ORIGINAL (+ clearly identified modelling choices) |
| T05 contact surrogate | OPTIONAL, fenced-off independent diagnostic only; document geometry, friction assumptions, failure modes, lack of ground truth, and limitations. | Do not assert "two-point normal force always points toward center"; this depends on geometry/contact normals, friction and state. Never count its pass toward paper reproduction. | EXPERIMENTAL / OUR_EXTENSION |
| T06 deterministic integration | Trace Eq.16–28 through all applicable stage sequences and generate finite command/torque timelines, per-stage comparisons, and plots; use physically meaningful units and frames. | Detect missing stage commands, clock/frame inconsistencies, dead or unexercised branches. Do **not** claim reproduced Fig.9/11 object motion or original success statistics without calibrated dynamics and digitized original measurements. | ENGINEERING / ADAPTATION |

## Non-negotiable reproducibility and governance

1. Read `AGENTS.md`, `CODEX_START_HERE.md`, `docs/EXECUTION_GOVERNANCE.md`, paper card, and `p3/P3_PAPER_STUDY_AND_PLAN.md`; run `git status`. Capture PRE-TASK report. The repo-wide `docs/STATUS.md` on this branch predates this P3 study; use this specific approval for P3 only without editing historical unrelated status/benchmarks.
2. Audit the local `papers_and_reference_all/references/private_sources/P3_original.pdf` against SHA256 ledger. Inspect PDF page image rather than relying on extracted notation for Eq.16–28, especially Eq.27/28 block matrices. If a source discrepancy would change implementation, record the discrepancy and stop for a decision rather than guessing.
3. Use independent mathematical checks, mutation negatives, deterministic seeds, versioned parameters, PRE/POST artifacts, commands, run metadata and plotted evidence. No circular test oracle calling the same implementation. State explicit tolerances and their rationale.
4. Execute T01 → T02 → T03 → T04 → T06, each independently committed and logged. T05 only if it is near-zero-cost and explicitly isolated; it may be skipped without blocking algorithm verification.
5. Keep paper facts separate from assumptions. Missing gains/parameters must be tagged as illustrative TEST_FIXTURE or ADAPTATION; no false numeric agreement claims. Ensure units N, N·m, m, rad, s and frames are explicit.
6. Default max 3 evidence-based implementation iterations per root blocker. If unresolvable, classify SOURCE_AMBIGUITY vs IMPLEMENTATION_ERROR vs OUT_OF_SCOPE; record an honest PARTIAL/UNKNOWN and report.
7. Never require new pip/network installs solely to make P3 work; prefer available NumPy/standard-library or lightweight pure-Python fixtures. Keep production code distinct from test oracle.
8. End with a concise table: Eq mapping, implemented/validated, independent evidence, limitations, status, figures, exact commit hashes, reproducible commands. Use `ALGORITHM_NUMERICAL_VERIFIED` only after **all required core claims** pass. Never claim FULL_PAPER_REPRODUCED.

## Execution authorization

The user requested P3 reproduction after the paper-study review gate. Proceed on this P3 branch with the corrected core numerical scope, without waiting for a new approval after each ordinary passing test. Pause only at a material paper ambiguity, scientifically significant deviation, scope increase, or exhausted blocker budget. Preserve P2/P4 independence.
