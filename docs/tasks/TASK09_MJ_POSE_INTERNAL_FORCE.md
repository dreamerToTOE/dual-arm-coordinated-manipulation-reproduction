# TASK09-MJ — P2 Pose + Internal Force

Status: TODO

## Goal
Combine object pose tracking with internal-wrench regulation.

## Experiments
Run at least:
- pose-only;
- internal-force-only;
- pose + internal-force.

## Codex actions
- Add internal-wrench objective/controller.
- Preserve object pose objective.
- Record left/right wrench, external wrench, internal wrench and object pose.
- Document simulator-ground-truth substitution for paper perception stack.

## PASS
Combined controller improves internal-wrench metric without unacceptable pose degradation relative to frozen thresholds.
