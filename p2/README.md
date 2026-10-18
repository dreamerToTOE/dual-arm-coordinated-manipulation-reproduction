# P2 Numerical + Virtual Simulation Reproduction

**Paper**: Marco De Simone et al., *Cooperative Object Transport and Assembly: Pose/Force Control by Visual-Tactile Feedback*, IEEE RA-L (2026), DOI [10.1109/LRA.2026.3665445](https://doi.org/10.1109/LRA.2026.3665445).

## Objective / 授权范围
Reconstruct the paper's mathematical models and algorithms primarily in Python, with independent MuJoCo virtual-physics checks wherever credible. Recreate paper Fig. 6–9 / Table I–II and supplemental-video behaviors as **virtual experiments**, without requiring physical KUKA/Yaskawa robots, physical tactile sensors, or an Isaac Sim port in this stage. Numerical agreement is a research question, not an assumed result. Do not promise exact hardware precision or fabricate missing paper parameters.

**Current status: SETUP / NOT EXECUTED.** This branch adds a new roadmap and copies already-existing P2 files from a frozen historical commit without running new tests, fixing failures, or claiming reproduction success.

## Getting started
1. Read [Codex entry](CODEX_START_HERE.md), [governance](AGENTS.md), [legacy audit](LEGACY_EVIDENCE.md), [paper-to-code index](PAPER_TO_CODE.md), [experiment matrix](EXPERIMENT_MATRIX.md), and [tasks index](tasks/INDEX.md).
2. Start from `p2/tasks/P2_T00_PROVENANCE.md`. At each stage produce the required auditable outputs and wait for approval before starting the next stage.
3. Historical Python implementation resides in `baselines/p2_pose_force/`, old P2 tests in `tests/test_p2_*.py`, runnable scripts in `scripts/*p2*.py`, configs under `configs/p2_*`, and **original** evidence under `reports/P2_*` / `results/*_P2_*`. These paths were imported byte-for-byte at the same Git blob SHA from [accepted legacy handoff](https://github.com/dreamerToTOE/dual-arm-coordinated-manipulation-reproduction/blob/7787c75a8042af041579e5df0c9ac3e3ec4f6195/reports/P2_DELIVERY_ACCEPTANCE_FREEZE.md).
4. New experiments should use namespaced `p2/runs/<run_id>/` with metadata, fixed config snapshot, source SHA, random seed, command, stdout/stderr, termination cause, arrays/curves, metrics and integrity manifest. Do not overwrite any historical file.

## Explicit separation
- P4 planning and other paper branches are outside this effort; no editing P4 branches, paths, reports, processes or ongoing jobs.
- The base is `main`, **not** the divergent P2 audit branch carrying mixed P4 history.
- Original old P2 acceptance was **partial**. Unit/component tests are not evidence that the closed loop completed. [Legacy details](LEGACY_EVIDENCE.md).
- **Do not** change source equations, metrics, thresholds or experimental scope silently; record any adaptation relative to the original paper.
- Original figures are target evidence, not synthetic data to digitize and misrepresent as measurements.

## Research decision gates
G0 provenance & paper contract → G1 physics/model qualification → G2 estimator closure → G3 control closure → G4 exp1–exp4 / high-moment → G5 sliding + assembly virtual tests → G6 independent audit & comparison. Each gate can be PASS, FAIL, BLOCKED or NOT_EXECUTED; no automatic green status.
