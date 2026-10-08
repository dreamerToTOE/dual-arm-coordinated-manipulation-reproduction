# TASK14-MJ — P3 Search / Align Recovery

Status: TODO

## Goal
Recover from jam/misalignment during Benchmark-B rear-push insertion using bounded paper-inspired perturbation/search behavior.

## State machine
INSERT_READY → PUSH → SEARCH/ALIGN → INSERT → DONE, with JAM_ABORT after bounded recovery attempts.

## Codex actions
- Keep the same right-rear pusher contact topology.
- Implement bounded lateral/orientation perturbations inspired by P3 search/align stages.
- Bound force, amplitude, time and recovery count.
- Compare with the no-recovery hybrid controller from the identical INSERT_READY state.
- Do not change the common handoff or benchmark geometry to improve recovery.

## PASS
Recovery improves success on at least one frozen misalignment class without violating safety limits.
