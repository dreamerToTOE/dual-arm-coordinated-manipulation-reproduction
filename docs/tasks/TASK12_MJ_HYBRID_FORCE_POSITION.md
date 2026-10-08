# TASK12-MJ — P3 Hybrid Force/Position Rear-Push Control

Status: TODO

## Goal
From the frozen Benchmark-B INSERT_READY state, regulate insertion-axis force while maintaining lateral/vertical pose and orientation.

## Contact topology
Single right rear (-X face) pusher; left helper remains parked. The fixed PRE_PUSH→INSERT_READY handoff is not part of the controller.

## Codex actions
- Define the task frame at carriage entrance.
- Configure force vs motion subspaces.
- Regulate desired +X insertion force.
- Maintain lateral/vertical position and orientation.
- Compare against TASK11 with identical INSERT_READY and C0–C5 cases.

## PASS
Controller is stable and demonstrates measurable contact-force/robustness behavior relative to the position-only rear-push baseline.
