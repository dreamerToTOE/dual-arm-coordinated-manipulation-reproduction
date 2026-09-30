# USER_FEEDBACK

Persistent user decisions/feedback that must influence future work.

## 2026-09-29
- Keep detailed records and feedback during Codex work.
- Use a separate reproduction repository instead of mixing baselines into the palletizing repository.
- Use MuJoCo as an auxiliary force/contact platform where useful, but keep Isaac Sim as the final unified benchmark.

## 2026-09-30
- Advance tasks in repository order and persist process records to GitHub as work proceeds.
- MuJoCo is already installed in a .venv belonging to the existing force-control project; locate and reuse that environment for audits instead of assuming the system Python import result means MuJoCo is absent.
- Confirmed Task27 as the geometric starting point for TASK01 benchmark_v1; no approval was given to freeze every old numerical setting or acceptance threshold.
- Clarified Benchmark B: first four cubes use dual-arm suction with one arm pushing toward the deep wall and the other constraining lateral/yaw error, then swap push/hold roles for lateral pressing; Cube 05 must be aligned accurately at PRE_PUSH and pushed inward by one suction arm without second-arm Cube contact.
