# TASK17 — P5 Joint Constraints

Status: TODO

## Goal
Add position/velocity safety constraints without destabilizing TASK16.

## Codex actions
- Encode joint velocity bounds.
- Add position-limit look-ahead/damper constraints.
- Record infeasibility reason/status.
- Test near lower/upper joint limits.

## PASS
No limit violations in the frozen unit suite and QP infeasibility is handled explicitly.
