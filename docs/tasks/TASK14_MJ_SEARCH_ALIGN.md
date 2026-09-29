# TASK14-MJ — P3 Search / Align Recovery

Status: TODO

## Goal
Recover from jam/misalignment using paper-inspired perturbation/search behavior.

## State machine
PRE_CONTACT → PUSH → SEARCH/ALIGN → INSERT → DONE, with JAM_ABORT after bounded recovery attempts.

## Codex actions
- Implement small lateral/orientation perturbations inspired by P3 search/align stages.
- Bound force, amplitude, time and recovery count.
- Compare with no-recovery hybrid controller.

## PASS
Recovery improves success on at least one frozen misalignment class without violating safety limits.
