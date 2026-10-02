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

## 2026-09-30 20260930_TASK01_center_right_physical
Task: TASK01
Baseline: none; experimental Task27 fifth-Cube probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit at probe: 76d24dc (new repo), d93f285 (legacy repo), with working-tree test patch later committed unchanged as 631b1f6
Seed: not fixed in legacy OMPL
Command/config: `results/20260930_TASK01_center_right_physical/metadata.yaml`
Result: PASS, one physical run; four fixtures pre-placed
Key metrics: Cube 05 final center 0.603 mm; +X wall gap 0.586 mm; +Y/-Y side gaps 1.361/1.639 mm; peak joint torque 35.96 Nm
Artifacts: metadata, `reports/TASK01_CENTER_ARM_SYMMETRY.md`, external raw ROS log listed therein

## 2026-09-30 20260930_TASK01_center_left_physical
Task: TASK01
Baseline: none; experimental Task27 fifth-Cube probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit at probe: 76d24dc (new repo), d93f285 (legacy repo), with working-tree test patch later committed unchanged as 631b1f6
Seed: not fixed in legacy OMPL
Command/config: `results/20260930_TASK01_center_left_physical/metadata.yaml`
Result: PASS, one independent physical run; four fixtures pre-placed
Key metrics: Cube 05 final center 0.669 mm; +X wall gap 0.633 mm; +Y/-Y side gaps 1.719/1.281 mm; peak joint torque 35.87 Nm; one pre-close reacquire
Artifacts: metadata, `reports/TASK01_CENTER_ARM_SYMMETRY.md`, external raw ROS log listed therein
Notes: Both arms HOME. Left and right results differ; no statistical equivalence is claimed.

## 2026-10-02 20261002_TASK01_center_repeatability
Task: TASK01
Baseline: none; [EXPERIMENTAL] legacy Task27 Cube 05 arm-symmetry probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Seed: uncontrolled legacy OMPL (no fixed-seed claim)
Command/config: Four per-run `results/20261002_TASK01_center_{right,left}_{02,03}/metadata.yaml` files; benchmark draft `configs/benchmark/benchmark_v1.yaml`
Result: Four new physical runs PASS with both arms HOME; including 2026-09-30, right 3/3 and left 3/3 PASS. TASK01 remains IN_PROGRESS.
Key metrics: right center error [0.603, 0.429, 0.374] mm, mean 0.469 mm; left [0.669, 0.408, 0.561] mm, mean 0.546 mm; maximum side-gap imbalance 0.582/0.802 mm (right/left).
Artifacts: `reports/TASK01_CENTER_ARM_SYMMETRY.md`, four per-run metadata files, external raw ROS logs named there; scripts `task01_capture_final_pose.py` and `summarize_task01_center_trials.py`.
Limitations: Four fixture cubes were pre-placed; no contact wrench; motion-time PhysX/USD pose disagreement remains open (BUG-005). `move_group` repeatedly segfaulted during Ctrl-C teardown after completed task runs (BUG-004).
Notes: Both arms HOME. Not a reproducibility or statistical symmetry result.

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
