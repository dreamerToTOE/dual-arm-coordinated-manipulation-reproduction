# TASK01 — Isaac / MoveIt Model Parity

2026-10-07. Current status: GUI_INITIALIZATION_IN_PROGRESS, **not PASS**.

Prerequisite full discrete geometry passed (A136/B157, exact PRE14q seam): [report](TASK01_FULL_SINGLE_CUBE_GEOMETRY.md). The original PhysX convexHull model is not assumed equivalent to the MoveIt STL. Full-chain wall-risk state is TARGET/state292, left_link7↔deep_wall FCL clearance2.212219mm; intended Cube/tool minimum is state196/0.999669mm.

Independent visible GUI only: dual FR3/current L tools/one Cube/table/carriage. No old five-Cube fixture, ROS/controller, motion execution, force/wrench calibration, ACM expansion or geometry changes. Original asset and construction-source hashes must be captured. Static teleports have geometry index, not fabricated simulation timestamps or READY claims. Query/convex-cooked evidence must distinguish actual shape overlap from original SRDF Adjacent allowed pairs and expected Cube support touch.

Replay all states where possible, with early priority START→A minimum/PRE→TARGET (full-chain wall minimum)→state196 (full all-pair minimum). Required insertion samples and all-state replay remain to verify. First unexpected FCL-free/Isaac collision stops, records exact pair/state/actual FK/cooked shape evidence, no geometry repair.

Artifact directory: `results/20261007_TASK01_isaac_model_parity01/`. Actual outcome and commands will replace this pending checkpoint. READY/reset has not been authorized or run.
