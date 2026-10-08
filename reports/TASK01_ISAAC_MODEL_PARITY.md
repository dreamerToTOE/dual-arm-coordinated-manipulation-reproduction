# TASK01 — Isaac / MoveIt Model Parity

2026-10-08. Current status: ENGINEERING_UNVERIFIED_MOVING_NATIVE_QUERY_STOP (07); disabled-physics subsystem refresh prepared (08 not run), **not PASS**.

Prerequisite full discrete geometry passed (A136/B157, exact PRE14q seam): [report](TASK01_FULL_SINGLE_CUBE_GEOMETRY.md). The original PhysX convexHull model is not assumed equivalent to the MoveIt STL. Full-chain wall-risk state is TARGET/state292, left_link7↔deep_wall FCL clearance2.212219mm; intended Cube/tool minimum is state196/0.999669mm.

Independent visible GUI only: dual FR3/current L tools/one Cube/table/carriage. No old five-Cube fixture, ROS/controller, motion execution, force/wrench calibration, ACM expansion or geometry changes. Original asset and construction-source hashes must be captured. Static teleports have geometry index, not fabricated simulation timestamps or READY claims. Query/convex-cooked evidence must distinguish actual shape overlap from original SRDF Adjacent allowed pairs and expected Cube support touch.

Replay all states where possible, with early priority START→A minimum/PRE→TARGET (full-chain wall minimum)→state196 (full all-pair minimum). Required insertion samples and all-state replay remain to verify. First unexpected FCL-free/Isaac collision stops, records exact pair/state/actual FK/cooked shape evidence, no geometry repair.

Latest artifact directory: `results/20261008_TASK01_isaac_model_parity07/`. READY/reset gate not reached or run.

## 07 actual zero-step query guard stop / 08 subsystem refresh prepared

07 source commit `0fb2fc4`, SHA `8887ad1bd7d674ecae930b65a8c496d3c1776433b34eab826f2172dce72660cf`. No PLAY native initialization eliminated actual physics callbacks (**0**, dt list empty), but START still accepted0: link0/link1 actual cooked interior-point queries hit the correct original collider/owner; link2 exact original target returned zero hits and stopped before collision verdict. 27 native actors matched tensors before output (max0m/6.165552397244359e-7rad); after output max position change2.9802322387695312e-8m/rotation4.2146848510894035e-8rad. USD source frames and original immutable fingerprint matched. Q/FK/TCP guards traversed successfully but their successful numerical values were not saved in 07 failure artifact; do not backfill measurements. [07 metadata](../results/20261008_TASK01_isaac_model_parity07/metadata.json), [summary](../results/20261008_TASK01_isaac_model_parity07/summary.json). 51 software tests OK/0.099s; wrapper0 not PASS, GUI closed/reaped.

Independent cooked-plane/transform audit found the link2 centroid strictly inside all60 hull planes (minimum approximately50.808mm); collider local-to-owner is unit/identity and independent world transform agrees within16.7nm. A stale query target is consistent with the miss, not a uniquely captured cause. No verified unexpected collision/BUG019 result, no READY/reset. 08 only tries installed official `IPhysxSimulation.flush_changes()` then `IPhysxStageUpdate.on_update(static_time, 0.0, False)` (physics update disabled, other subsystems updated). It does not promise query-tree freshness: actual zero-step, native pose/q/immutable model, original cooked positive/negative queries remain mandatory. No Play/integration/model/ACM changes. 08 prepared, not run.

## 06 actual render-only guard stop / 07 no-PLAY initialization prepared

06 commit `0a78485`, SHA `923aca89345fa7850ad9f5b981c38718c742a98c12fb07c9a7e4206a7a244498`, GUI14.25s. Mirror output reached zero stale shapes and preserved pre-render27 actor comparisons (maxpos0m/maxrot6.165552397244359e-7rad), but the first render still produced **2 callbacks each0.01666666753590107s**. START accepted0; moving-query/full-overlap tests not reached. [06 metadata](../results/20261008_TASK01_isaac_model_parity06/metadata.json), [summary](../results/20261008_TASK01_isaac_model_parity06/summary.json). Integration was actually observed despite the render dispatch guard and contrary to the static intent. 50 pure tests OK/0.079s are not GUI PASS. Owned process closed/reaped, wrapper0 not PASS.

Installed SDK `SimulationManager._warm_start` directly calls force-load/start/update_simulation(dt,0)/fetch on the timeline PLAY event; its `_create_simulation_view` calls update_simulation again. These bypass renderer dispatch and match the observed count, but a unique causal runtime trace was not captured. 07 therefore avoids **timeline PLAY entirely**: original native `force_load_physics_from_usd()` and `start_simulation()` initialize/store the static context, without update_simulation/simulate/fetch. No SDK subscription patch, no physical parameter, geometry/ACM or benchmark change. Retain every actual zero-step/native/q/USD/cooked/moving-query guard. Initialization availability and parity remain empirical gates; 07 not run. Original source/config/asset/q hashes independently match, no new IK. READY/reset still NOT_RUN.

## 05 actual zero-step guard stop / historical 06 plan

05 commit `8188168`, SHA `66dce1cd96875298f3830a25bb64232d6eb75f97717deaef7134feb43368cdba`, source snapshot before execution. After typed pose-output correction, the paused `app.update()` actually triggered **2 physics-step callbacks**; Cube USD z changed to `0.3772749900817871` and velocity z to `-0.16350001 m/s`. Thus integration occurred **despite not being requested**, and this is not a valid static parity run. The zero-step/immutability guard stopped at START, accepted0 before overlap verdict. [05 metadata](../results/20261008_TASK01_isaac_model_parity05/metadata.json), [summary](../results/20261008_TASK01_isaac_model_parity05/summary.json). GUI was closed/reaped, wrapper0 not PASS. The successful **pre-notice** 27 native actor comparisons were actually persisted (max tensor/native position difference0m, rotation6.165552397244359e-7rad); do not confuse them with post-update states. 35 pure tests passed, not static physics evidence.

06 uses the installed official `SimulationContext.render()` dispatch pattern: temporarily `/app/player/playSimulations=False` during render updates, restore the exact original bool in `finally`; same gate during handle loading. Keep actual physics-step callbacks/timeline change/native/q/shape/query checks as independent hard stops. No scene gravity/dt/solver/mass/model change. SDK dynamic velocity/joint-state output is not classified as immutable geometry; original limits/drives/mass/friction/mesh/scale/scene/frame remain hashed, and **actual integration still fails** the separate zero-step guard. Render-only regression is being prepared; 06 has not run. READY/reset remains NOT_RUN. All 03–05 negative evidence is preserved; no BUG019 geometric verdict/PASS/FROZEN claim.

## 04 actual API precision stop / historical 05 plan

04 source commit `a672224`, SHA `3bf86b380723b317b2eb4b32f3020a3736a16126887648bbc8a80c0bc3da8753`; preserved execution-before source snapshot. Visible GUI startup/load about14.5s; accepted parity states0/START attempted. Existing Fabric extension was disabled and `/physics/updateToUsd=true`; hence Fabric separation is **not** the demonstrated cause of 03. Official output materialized a Cube `xformOp:orient` state field of type `GfQuatf`, while the fallback wrote `GfQuatd`, causing a USD type error. No parity overlap verdict, no READY/reset; wrapper0 again is not PASS. [04 metadata](../results/20261008_TASK01_isaac_model_parity04/metadata.json), [summary](../results/20261008_TASK01_isaac_model_parity04/summary.json). 32 pure tests passed but did not cover this SDK float output variant.

05 fixes **existing state-field precision**, not geometry. SDK-created body pose-output fields/order are separately audited; body pose output is distinguished from geometry dimensions/scale in the immutable fingerprint. The helper still cannot add/reorder ops and rejects unsupported stacks. Fingerprint additionally covers physics scene/material/joints, disabled colliders, ancestors/base/tool frames and TCP. Preserve original scale, actual collider owner-local geometry, model/source hashes, accepted q/native poses, output settings and step0. A paused notice update is followed by complete guards; final GUI update and screenshots also require step0. All 35 pure USD/query regression tests passed (agent run); main replay/test log will provide execution evidence. 05 is still not run at this checkpoint, no BUG019/PASS/FROZEN claim.

GitHub checkpoint `a672224` was actually pushed over ordinary SSH after a proxy banner timeout; no global SSH config was changed.

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

## 04 historical engineering output plan (before execution)

Preserve paused state and actual output settings; try official `update_transformations_scene` and **already enabled** Fabric `force_update/save_to_usd`, without enabling Fabric or changing physics settings. If tensor teleports still do not export, mirror the already validated body SE3 to **existing** body translate/orient ops only. Original actor hierarchy, op order/scale, all child/tool collider local geometry and physics properties remain unchanged. Process paused USD notices, then recheck native actors, 14q, Cube, immutable geometry/settings fingerprint and zero physics-step callbacks. Reject unsupported/time-sampled/reordered ops; never add/reset/reorder ops. All original cooked-shape and moving-query guards remain mandatory. This is a static state-output adapter, not a geometric repair or paper method. 04 has no result yet.

## Preserved engineering attempts (2026-10-07)

1. `isaac_model_parity01`: cold GUI startup exceeded its bounded wait; owned process stopped/reaped, no scene created or physics loaded. This is not an IK/model collision failure. [Metadata](../results/20261007_TASK01_isaac_model_parity01/metadata.json).
2. `isaac_model_parity02`: visible minimal scene and original cooking/PhysX handles loaded. Initial live tensor FK passed, but the first query stopped on five existing environment/environment connections (table↔three walls; deep wall↔±Y walls). The adapter had not classified original fixture connections. Also the image still showed default standing robot poses, so tensor FK alone does **not** establish that actual query actors/shapes were at the commanded q. This run has **no scientific parity conclusion**, even though wrapper exit0 (app shutdown can mask return status). [Metadata](../results/20261007_TASK01_isaac_model_parity02/metadata.json), [actual scene image](../results/20261007_TASK01_isaac_model_parity02/gui_scene.png), [stale-pose observation](../results/20261007_TASK01_isaac_model_parity02/stale_pose_observation.png).

The old raw failure summary is unchanged. Probe source hashes were not captured at execution for 01/02; an exact inverse-adapter-patch source reconstruction is retained and labeled reconstructed, not an in-run snapshot. Do not retroactively associate the updated script hash with those runs.

## 2026-10-08 guarded replay scope

[ENGINEERING] Construct from the immutable native-run YAML snapshot. Check finite q/Cube and both TCPs, tensor FK against native PhysX actor pose, original collider world matrices against those bodies, effective readback status and actual cooked-convex source semantics. Positive native query at the original wall corner proves interface availability but not moving-target freshness; additional small-volume queries inside actual cooked original robot/tool/Cube shapes must hit their exact collider, and sufficiently distant old locations must no longer hit after a legitimate benchmark-state change. These queries do not move geometry or change any mask. Unknown-hit/callback errors are saved and raised after C++ callbacks return, not silently lost.

Preserve all original fixture hits, with original dimensions/AABB construction proof; this is not robot/Cube ACM expansion. Native query/readback freshness or actor-frame inconsistency is an ENGINEERING_STOP, not a BUG019 geometric verdict. Verified non-design robot/tool/Cube overlap is first-failure-stop with exact pair. No original geometry, physics parameters, SRDF/ACM, thresholds, force calibration or controller changes.

Static nominal replay records retain state indices, physics_step=null and simulation_timestamp=null; they are not fabricated post-step scientific measurements. Native shape-overlap evidence does not by itself certify contact-offset safety or dynamics. READY/reset and any post-step contact validation remain NOT_RUN until the parity gate permits them.
