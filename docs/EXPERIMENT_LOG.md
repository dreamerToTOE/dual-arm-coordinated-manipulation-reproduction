# EXPERIMENT_LOG

Append-only experiment index.

At repository initialization, no experiments had been run.

## 2026-09-30 20260930_TASK00_mujoco_smoke
Task: TASK00
Baseline: none; environment smoke test only
Platform: existing isolated MuJoCo .venv
Commit at probe: 9f71e0a78a9d852d060b4e7e4c3225558d1d9bb1
Seed: not applicable
Command: see results/20260930_TASK00_mujoco_smoke/metadata.yaml
Config: inline one-joint sphere model
Result: PASS
Key metrics: MuJoCo 3.13.0; one mj_step advanced simulation time to 0.002 s
Artifacts: results/20260930_TASK00_mujoco_smoke/
Notes: This is not a dual-arm force-control or paper-reproduction experiment.

Recommended entry:
```text
## <date> <run_id>
Task:
Baseline:
Platform:
Commit:
Seed:
Command:
Config:
Result: PASS/FAIL
Key metrics:
Artifacts:
Notes:
```

## 2026-10-20 20261020_104153_P3-T03_selection (corrected)
Task: P3-T03 (post-delivery review R1)
Baseline: Eq.(27)-(28) selection/frame operators; supersedes `20261020_094115_P3-T03_selection` (preserved)
Platform: pure NumPy, Python 3.10 (`/usr/bin/python3.10`)
Commit at probe: 11542aee (review) + working tree
Seed: 20261019
Command: `/usr/bin/python3.10 p3/tools/run_t03_selection.py`
Config: R_h = Rz(30°)Ry(15°); R_task_to_hole = Ry(+90°) (TEST_FIXTURE rotations)
Result: PASS (23/23)
Key metrics: Omega symmetric 0, idempotent 1.1e-16, frame covariance 1.1e-16, push-axis annihilation 8.5e-17;
  literal-frame negative control ||Omega(I)e_z|| = 1.0
Artifacts: results/20261020_104153_P3-T03_selection/
Notes: T03_12 now uses the physical push axis p_ref = R_h(R_task_to_hole e_z); T03_15 added as negative control.

## 2026-10-20 20261020_104220_P3-T02_stages (corrected metrics)
Task: P3-T02 (post-delivery review R3)
Baseline: Eq.(23)-(26) stage composition; supersedes `20261020_093810_P3-T02_stages` (preserved)
Platform: pure NumPy, Python 3.10
Commit at probe: 11542aee (review) + working tree
Seed: 20261019
Command: `/usr/bin/python3.10 p3/tools/run_t02_stages.py`
Config: TEST_FIXTURE pattern parameters; case boundaries 0/3.2/10.5/16.5/17.5 s (case 1)
Result: PASS (16/16)
Key metrics: case-1 jumps approach->search 1.824 N / 0.000 N*m; search->align 5.000 N / 0.391 N*m;
  align->insert 0.000 N / 0.391 N*m
Artifacts: results/20261020_104220_P3-T02_stages/
Notes: force and moment jumps separated; `jump_mixed_l2_unphysical` retained as diagnostic only.

## 2026-10-20 20261020_104237_P3-T06_integration (corrected metrics)
Task: P3-T06 (post-delivery review R2)
Baseline: Eq.(16)-(28) deterministic stage integration; supersedes `20261020_094514_P3-T06_integration` (preserved)
Platform: pure NumPy, Python 3.10
Commit at probe: 11542aee (review) + working tree
Seed: 20261019 (fixed fixtures), dt = 0.01 s
Command: `/usr/bin/python3.10 p3/tools/run_t06_integration.py`
Config: four documented cases, TEST_FIXTURE state/J/gains
Result: PASS (12/12)
Key metrics: max_{t,k}|tau_k| = 10.152 N*m; max_t||tau||2 = 12.590 N*m; max_{t,i}|F_i| = 10.00 N;
  max_t||F||2 = 11.18 N; max_t||m||2 = 0.391 N*m
Artifacts: results/20261020_104237_P3-T06_integration/ (4 CSV traces)
Notes: component maxima and vector norms reported separately; no object motion or success rate claimed.
