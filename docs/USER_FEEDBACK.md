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
- Expected the fifth Cube's left/right single-arm insertion to be geometrically symmetric, and requested direct Isaac comparison without repeating the full process: place the first four Cubes at their intended final cells and test only Cube 05. Keep the two runs separate so feasibility is not mistaken for proof of equivalence.

## 2026-10-02
- User requested continuation of the same Cube 05 left/right experimental validation. This did not authorize freezing TASK01 or changing the benchmark geometry; repeated fresh-scene trials and evidence recording were kept within the existing probe scope.

## 2026-10-03
- User requested continuation. Advanced TASK01 measurement diagnosis within the existing Task27-derived draft rather than starting paper baselines before the freeze gate. No new numeric benchmark approval or permission to modify the protected reinforcement_stair-test directory was inferred.
- User approved continuing the proposed order: force-measurement feasibility/calibration, synchronized frames/time, then a full five-Cube nominal probe and benchmark parameter review. This is not permission to alter hidden-body masses, freeze success gates, skip TASK01, or start paper force controllers; the protected directory remains untouched.
