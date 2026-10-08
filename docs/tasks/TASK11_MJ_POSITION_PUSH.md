# TASK11-MJ — P3 Position-Only Rear-Push Baseline

Status: TODO

## Goal
Establish a deliberately simple insertion baseline for Benchmark B before hybrid control.

## Start contract
Begin from the frozen `INSERT_READY` state, not from bilateral PRE_PUSH:
- right rear (-X face) grasp active;
- left helper parked;
- Cube at the frozen insertion start pose.

The PRE_PUSH→INSERT_READY handoff is common engineering setup and is not scored as part of this controller.

## Codex actions
- Move the Cube from INSERT_READY along +X using position/pose control.
- Keep lateral/vertical/orientation targets fixed.
- Log contact force and jam-relevant signals using the common interface.
- Run C0–C5 reduced MuJoCo cases.
- Do not reimplement the bilateral handoff inside the controller.

## PASS
Baseline is reproducible and exposes where pure position control succeeds/fails under the same rear-push contact topology used by later P3 variants.
