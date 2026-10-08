# TASK01 — READY / Reset

2026-10-08. Status: **NOT_RUN_PENDING_MODEL_PARITY**.

Latest actual GUI attempt03 stopped at START/index0 on stale USD collider output before any accepted parity sample. This is an engineering source-frame rejection, not a geometric collision verdict. Output-adapter04 is prepared but not yet run. See [parity report](TASK01_ISAAC_MODEL_PARITY.md). No repeated post-step reset has occurred and no READY state is claimed.

Later Oct8 checkpoint: 04 actually stopped on a Cube state-output `Quatf/Quatd` type mismatch, again accepted0, not a geometry failure; typed-output correction05 is prepared/not run. READY/reset remains NOT_RUN, and the earlier 03/04-plan text above is preserved as history.

Actual START/PRE_PUSH candidate 14q was recorded by the native full-chain geometry probe in [candidate YAML](../configs/benchmark/benchmark_v1.yaml) and [full-chain report](TASK01_FULL_SINGLE_CUBE_GEOMETRY.md). These are not FROZEN; future benchmark reset must restore them rather than randomly solve IK again.

Do not initialize dynamic held-Cube READY before original Isaac/MoveIt collision-model parity passes. Planned scope: repeated Benchmark A START and Benchmark B PRE_PUSH reset; record q error, Cube pose error, both TCP errors, carriage frame, true post-physics-step simulation timestamp/step and unintended contacts. A paused nominal static replay is not this test.

No force/wrench calibration or full controller; BUG001 belongs to TASK10-IS and does not block this gate. TASK01 can only become PASS CANDIDATE after actual parity and reset evidence, followed by user freeze approval.
