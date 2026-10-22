# P2 chronological Codex task board

Tasks are strictly sequential; do **not** initiate a later stage until the user accepts its predecessor's evidence. Each has detailed prerequisites, action, checks, output and stop reasons. The current approved scope is **numerical simulation first**, optional credible physics simulation for contact and assembly, with **zero real hardware required**.

| Stage | Task | Suggested work days (non-additive) | Exit condition |
|---|---|---|---|
| G0 | [T00 Historical audit & freeze](P2_T00_PROVENANCE.md) | 0.5–1 | provenance and fail ledger verified |
| G0 | [T01 Environment & paper protocol](P2_T01_ENV_PROTOCOL.md) | 0.5–1 | reproducible smoke & paper inputs |
| G1 | [T02 SE(3), contact & grasp](P2_T02_MATH_CONTACT.md) | 1–2 | math identities and model deviations explicit |
| G1 | [T03 Independent dynamics](P2_T03_PLANT.md) | 1–2 | real integrated state, energy/wrench and convergence |
| G2 | [T04 Visual-tactile IESEKF](P2_T04_ESTIMATOR.md) | 2–4 | estimator gate and honest baseline-vs-EKF |
| G3 | [T05 Pose/force & joint kinematics](P2_T05_CONTROL_IK.md) | 2–3 | estimated-state closed-loop through feedback stages |
| G4 | [T06 Fig.6 exp1–exp4](P2_T06_FIG6.md) | 2–3 | four matched experiments and overlay |
| G4 | [T07 Fig.7 high moments](P2_T07_FIG7.md) | 1–2 | controlled torque contrast |
| G5 | [T08 Fig.9 pivot/sliding](P2_T08_SLIDING.md) | 2–3 | physical contact mode switch with relative motion |
| G5 | [T09 Fig.8 virtual assembly](P2_T09_ASSEMBLY.md) | 2–4 | A/B1/B2/C scene, statistics, contact placement |
| G6 | [T10 Critical paper comparison](P2_T10_REVIEW.md) | 1–2 | completeness ledger & paper-vs-simulation table |

**Timeline:** about 2–3 weeks is an aspirational target with reuse. G5 may take longer without validated gripper/soft-contact parameters; incomplete G5 is documented as BLOCKED, never erased or automatically declared out of scope.

**Output contract:** `p2/reviews/Txx_PRE.md`, `p2/reviews/Txx_POST.md`, `p2/runs/<run_id>/metadata.json`, result tables, plots, raw trajectory, final integrity/hashes. Include exact source/ref, command, seed, environment, wall time, run status, unexpected failures, and delta vs paper.

**Budgets by stage:** first smoke ≤60 s wall each, qualification ≤180 s wall each, any extended suite budget explicitly proposed to user before execution, at most 3 targeted repair cycles per blocker; no runaway sweeps, no 18,000 cases, no auto-execution of the complete roadmap.
