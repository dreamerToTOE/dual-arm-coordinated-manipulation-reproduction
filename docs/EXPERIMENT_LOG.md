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

## 2026-09-30 20260930_TASK01_static_geometry
Task: TASK01
Baseline: none; candidate geometry check only
Platform: system Python 3 + PyYAML; analytic validation (not Isaac)
Commit at probe: ca2b1f75a85c32bcad87b193328cbe7424680183
Seed: not applicable
Command: `python3 scripts/validate_benchmark_candidate.py`
Config: `configs/benchmark/benchmark_v1.yaml` (DRAFT)
Result: PASS for internal analytic geometry; TASK01 itself remains IN_PROGRESS
Key metrics: 0 failed dimension checks; 30 unresolved/null configuration fields
Artifacts: `results/20260930_TASK01_static_geometry/`
Notes: No physical contact, collision, sensing or timing validation was performed.

## 2026-09-30 20260930_TASK01_contact_protocol
Task: TASK01
Baseline: none; candidate protocol and geometry check only
Platform: system Python 3 + PyYAML; analytic validation (not Isaac)
Commit at probe: 93e7e54 (parent of uncommitted draft)
Seed: not applicable
Command: `python3 scripts/validate_benchmark_candidate.py`
Config: `configs/benchmark/benchmark_v1.yaml` (DRAFT)
Result: PASS for internal analytic geometry/protocol; TASK01 itself remains IN_PROGRESS
Key metrics: 0 failed checks; 36 unresolved/null configuration fields; 1° yaw consumes 1.038 mm nominal center clearance
Artifacts: `results/20260930_TASK01_contact_protocol/`
Notes: No physical contact, collision, sensing or timing validation was performed.

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
