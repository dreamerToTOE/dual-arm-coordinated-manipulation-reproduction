# TASK01 — Isaac / MoveIt Model Parity

2026-10-08. Current status: ENGINEERING_STALE_USD_QUERY_SOURCE_STOP (03); output-adapter correction prepared (04 not run), **not PASS**.

Prerequisite full discrete geometry passed (A136/B157, exact PRE14q seam): [report](TASK01_FULL_SINGLE_CUBE_GEOMETRY.md). The original PhysX convexHull model is not assumed equivalent to the MoveIt STL. Full-chain wall-risk state is TARGET/state292, left_link7↔deep_wall FCL clearance2.212219mm; intended Cube/tool minimum is state196/0.999669mm.

Independent visible GUI only: dual FR3/current L tools/one Cube/table/carriage. No old five-Cube fixture, ROS/controller, motion execution, force/wrench calibration, ACM expansion or geometry changes. Original asset and construction-source hashes must be captured. Static teleports have geometry index, not fabricated simulation timestamps or READY claims. Query/convex-cooked evidence must distinguish actual shape overlap from original SRDF Adjacent allowed pairs and expected Cube support touch.

Replay all states where possible, with early priority START→A minimum/PRE→TARGET (full-chain wall minimum)→state196 (full all-pair minimum). Required insertion samples and all-state replay remain to verify. First unexpected FCL-free/Isaac collision stops, records exact pair/state/actual FK/cooked shape evidence, no geometry repair.

Latest artifact directory: `results/20261008_TASK01_isaac_model_parity03/`. READY/reset has not been authorized or run.

## 03 actual guarded GUI result — source-frame rejection, no geometry verdict

Commit d9c422c; actual source snapshot SHA256 `27e0a043431a83b0f8fa760fd6307f8749ee2e825de154dcad4c3c67ae6d7aa1`. Visible CPU PhysX (tensor device ordinal=-1) loaded the original one-Cube scene/cooked hulls. At START/index0, q/TCP/nominal FK guards passed but the USD query-source frame did not. Accepted parity states: **0**. Moving-target queries/full-chain overlap checks were not reached.

Rejected collider `/World/left_fr3/fr3_link1/collisions`: USD rotation remained identity although the tensor/native actor gate expected the q1-rotated link. Maximum matrix-element difference `0.609714114482171` is **dimensionless rotation error**, not clearance or penetration depth. Left/right maximum q reset errors were `9.706287595889762e-8 / 1.7115877160023274e-8 rad`; TCP position errors `3.976069182062307e-7 / 6.256020684309647e-7 m`; TCP rotation errors `6.861009855998394e-7 / 1.0000444493033106e-6 rad`. Cube tensor pose `(0.550000011920929,0,0.3799999952316284)` with identity orientation.

The native actor gate was traversed successfully, but its successful numerical comparison values were **not persisted** in 03; they must not be reconstructed as observations. Exact rejection/FK/q/Cube are in the preserved raw evidence; structured [metadata](../results/20261008_TASK01_isaac_model_parity03/metadata.json) and [summary](../results/20261008_TASK01_isaac_model_parity03/summary.json) record the limitation. Wrapper exit0 reflects app shutdown, **not PASS**. Owned GUI process exited/reaped; no background Isaac/MoveIt run survives. BUG019 remains OPEN/NOT_ESTABLISHED for this new chain. No geometry, ACM, physical parameters or acceptance changes; no integration, READY/reset or wrench test. Software guard tests: 19 OK, not physics evidence.

Actual command (repo cwd):

```bash
timeout --signal=TERM --kill-after=20s 480s env DISPLAY=:1 PYTHONUNBUFFERED=1 \
  scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_single_cube_model_parity_gui.py \
  --output-dir results/20261008_TASK01_isaac_model_parity03/raw \
  --hold-for-inspection-sec 0
```

## 04 engineering output correction — prepared, not yet run

Preserve paused state and actual output settings; try official `update_transformations_scene` and **already enabled** Fabric `force_update/save_to_usd`, without enabling Fabric or changing physics settings. If tensor teleports still do not export, mirror the already validated body SE3 to **existing** body translate/orient ops only. Original actor hierarchy, op order/scale, all child/tool collider local geometry and physics properties remain unchanged. Process paused USD notices, then recheck native actors, 14q, Cube, immutable geometry/settings fingerprint and zero physics-step callbacks. Reject unsupported/time-sampled/reordered ops; never add/reset/reorder ops. All original cooked-shape and moving-query guards remain mandatory. This is a static state-output adapter, not a geometric repair or paper method. 04 has no result yet.

## Preserved engineering attempts (2026-10-07)

1. `isaac_model_parity01`: cold GUI startup exceeded its bounded wait; owned process stopped/reaped, no scene created or physics loaded. This is not an IK/model collision failure. [Metadata](../results/20261007_TASK01_isaac_model_parity01/metadata.json).
2. `isaac_model_parity02`: visible minimal scene and original cooking/PhysX handles loaded. Initial live tensor FK passed, but the first query stopped on five existing environment/environment connections (table↔three walls; deep wall↔±Y walls). The adapter had not classified original fixture connections. Also the image still showed default standing robot poses, so tensor FK alone does **not** establish that actual query actors/shapes were at the commanded q. This run has **no scientific parity conclusion**, even though wrapper exit0 (app shutdown can mask return status). [Metadata](../results/20261007_TASK01_isaac_model_parity02/metadata.json), [actual scene image](../results/20261007_TASK01_isaac_model_parity02/gui_scene.png), [stale-pose observation](../results/20261007_TASK01_isaac_model_parity02/stale_pose_observation.png).

The old raw failure summary is unchanged. Probe source hashes were not captured at execution for 01/02; an exact inverse-adapter-patch source reconstruction is retained and labeled reconstructed, not an in-run snapshot. Do not retroactively associate the updated script hash with those runs.

## 2026-10-08 guarded replay scope

[ENGINEERING] Construct from the immutable native-run YAML snapshot. Check finite q/Cube and both TCPs, tensor FK against native PhysX actor pose, original collider world matrices against those bodies, effective readback status and actual cooked-convex source semantics. Positive native query at the original wall corner proves interface availability but not moving-target freshness; additional small-volume queries inside actual cooked original robot/tool/Cube shapes must hit their exact collider, and sufficiently distant old locations must no longer hit after a legitimate benchmark-state change. These queries do not move geometry or change any mask. Unknown-hit/callback errors are saved and raised after C++ callbacks return, not silently lost.

Preserve all original fixture hits, with original dimensions/AABB construction proof; this is not robot/Cube ACM expansion. Native query/readback freshness or actor-frame inconsistency is an ENGINEERING_STOP, not a BUG019 geometric verdict. Verified non-design robot/tool/Cube overlap is first-failure-stop with exact pair. No original geometry, physics parameters, SRDF/ACM, thresholds, force calibration or controller changes.

Static nominal replay records retain state indices, physics_step=null and simulation_timestamp=null; they are not fabricated post-step scientific measurements. Native shape-overlap evidence does not by itself certify contact-offset safety or dynamics. READY/reset and any post-step contact validation remain NOT_RUN until the parity gate permits them.
