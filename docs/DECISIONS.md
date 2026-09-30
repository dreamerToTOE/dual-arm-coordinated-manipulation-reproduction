# DECISIONS

Append-only architectural and scientific decisions.

## D001 — Two-platform strategy
- Date: 2026-09-29
- Decision: Isaac Sim + ROS2 is the final common benchmark; MuJoCo is an auxiliary force/contact laboratory mainly for P2/P3.
- Reason: preserve fair final comparison while accelerating force/contact debugging.
- Impact: baseline algorithms remain platform-independent and use adapters.

## D002 — Baseline-first rule
- Date: 2026-09-29
- Decision: `ours/` remains algorithmically empty until TASK30.
- Reason: derive our method from reproducible evidence and failure cases rather than premature design.

## D003 — Task27 as TASK01 geometric starting point
- Date: 2026-09-30
- Classification: [ADAPTATION]
- Decision: Use the existing Task27 dual-FR3, fixed L-side-suction, rail and five-wide truck-box scene as the *starting geometry* for the common benchmark draft.
- User input: Explicitly confirmed "对" in response to this proposed starting point.
- Scope: This does not freeze the existing physics, grasp/contact topology, perturbations, timings or success thresholds. TASK01 stays IN_PROGRESS until the candidate and all values are reviewed and validated.
- Impact: The Task27 source constants are traceable in `configs/benchmark/benchmark_v1.yaml`; unresolved choices stay null rather than inheriting unsafe demo defaults.

## D004 — Different contact protocols for the first four and fifth cubes
- Date: 2026-09-30
- Classification: [ADAPTATION] for the common Task27 cell; [EXPERIMENTAL] for the task-specific staged contact sequence.
- Decision: Cubes 01–04 may start from coarse safe PRE_PUSH staging and are pushed toward the deep wall with a rear-face suction primary arm and a side-face suction constraint arm. At deep-wall contact, the side arm presses laterally while the former pusher holds the deep-wall constraint. Cube 05 is precisely aligned at PRE_PUSH, then inserted by one rear-face suction arm; the other arm makes no Cube contact.
- User input: Explicitly distinguished the first four dual-arm adjustable placements from the fifth single-arm precision insertion.
- Scientific boundary: Cube 05 is not a two-arm insertion test and must not be reported as evidence for a reproduced cooperative insertion controller. Cross-method results must distinguish the dual-arm fixture phase from the single-arm center phase.
- Still open: pre-push tolerances, primary arm assignment, contact-force limits, B-case perturbations and physical validation. No values are frozen by this decision.
