# TASK15-IS — P3 Isaac Migration

Status: TODO

## Goal
Migrate the MuJoCo position-only, hybrid and recovery variants to Isaac Benchmark B using the corrected staged topology.

## Fixed engineering precondition
Reuse the frozen PRE_PUSH→INSERT_READY handoff:
- bilateral side suction released;
- left helper parked;
- right arm regrips Cube -X face;
- right rear Surface Gripper active.

Formal P3 metrics start at INSERT_READY.

## Codex actions
- Reuse the same baseline controllers through the Isaac adapter.
- Reuse the already validated Task26/27 engineering primitives where compatible; do not rebuild them from scratch.
- Verify contact/wrench frame conventions from TASK10-IS.
- Run C0–C5 with fixed seeds.
- Keep handoff logs separate from controller metrics.
- Store videos only for representative/failure runs.

## PASS
Formal Benchmark-B result table generated for P3 variants from the same frozen INSERT_READY state.
