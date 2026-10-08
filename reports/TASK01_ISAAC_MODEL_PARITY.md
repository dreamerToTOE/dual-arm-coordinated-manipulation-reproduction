# TASK01 — Isaac / MoveIt Model Parity

2026-10-08. Current status: GUARDED_STATIC_REPLAY_PENDING, **not PASS**.

Prerequisite full discrete geometry passed (A136/B157, exact PRE14q seam): [report](TASK01_FULL_SINGLE_CUBE_GEOMETRY.md). The original PhysX convexHull model is not assumed equivalent to the MoveIt STL. Full-chain wall-risk state is TARGET/state292, left_link7↔deep_wall FCL clearance2.212219mm; intended Cube/tool minimum is state196/0.999669mm.

Independent visible GUI only: dual FR3/current L tools/one Cube/table/carriage. No old five-Cube fixture, ROS/controller, motion execution, force/wrench calibration, ACM expansion or geometry changes. Original asset and construction-source hashes must be captured. Static teleports have geometry index, not fabricated simulation timestamps or READY claims. Query/convex-cooked evidence must distinguish actual shape overlap from original SRDF Adjacent allowed pairs and expected Cube support touch.

Replay all states where possible, with early priority START→A minimum/PRE→TARGET (full-chain wall minimum)→state196 (full all-pair minimum). Required insertion samples and all-state replay remain to verify. First unexpected FCL-free/Isaac collision stops, records exact pair/state/actual FK/cooked shape evidence, no geometry repair.

Artifact directory: `results/20261007_TASK01_isaac_model_parity01/`. Actual outcome and commands will replace this pending checkpoint. READY/reset has not been authorized or run.

## Preserved engineering attempts (2026-10-07)

1. `isaac_model_parity01`: cold GUI startup exceeded its bounded wait; owned process stopped/reaped, no scene created or physics loaded. This is not an IK/model collision failure. [Metadata](../results/20261007_TASK01_isaac_model_parity01/metadata.json).
2. `isaac_model_parity02`: visible minimal scene and original cooking/PhysX handles loaded. Initial live tensor FK passed, but the first query stopped on five existing environment/environment connections (table↔three walls; deep wall↔±Y walls). The adapter had not classified original fixture connections. Also the image still showed default standing robot poses, so tensor FK alone does **not** establish that actual query actors/shapes were at the commanded q. This run has **no scientific parity conclusion**, even though wrapper exit0 (app shutdown can mask return status). [Metadata](../results/20261007_TASK01_isaac_model_parity02/metadata.json), [actual scene image](../results/20261007_TASK01_isaac_model_parity02/gui_scene.png), [stale-pose observation](../results/20261007_TASK01_isaac_model_parity02/stale_pose_observation.png).

The old raw failure summary is unchanged. Probe source hashes were not captured at execution for 01/02; an exact inverse-adapter-patch source reconstruction is retained and labeled reconstructed, not an in-run snapshot. Do not retroactively associate the updated script hash with those runs.

## 2026-10-08 guarded replay scope

[ENGINEERING] Construct from the immutable native-run YAML snapshot. Check finite q/Cube and both TCPs, tensor FK against native PhysX actor pose, original collider world matrices against those bodies, effective readback status and actual cooked-convex source semantics. Positive native query at the original wall corner proves interface availability but not moving-target freshness; additional small-volume queries inside actual cooked original robot/tool/Cube shapes must hit their exact collider, and sufficiently distant old locations must no longer hit after a legitimate benchmark-state change. These queries do not move geometry or change any mask. Unknown-hit/callback errors are saved and raised after C++ callbacks return, not silently lost.

Preserve all original fixture hits, with original dimensions/AABB construction proof; this is not robot/Cube ACM expansion. Native query/readback freshness or actor-frame inconsistency is an ENGINEERING_STOP, not a BUG019 geometric verdict. Verified non-design robot/tool/Cube overlap is first-failure-stop with exact pair. No original geometry, physics parameters, SRDF/ACM, thresholds, force calibration or controller changes.

Static nominal replay records retain state indices, physics_step=null and simulation_timestamp=null; they are not fabricated post-step scientific measurements. Native shape-overlap evidence does not by itself certify contact-offset safety or dynamics. READY/reset and any post-step contact validation remain NOT_RUN until the parity gate permits them.
