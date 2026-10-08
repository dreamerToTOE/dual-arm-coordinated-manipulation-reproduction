# TASK01 — Full Single-Cube Geometry

2026-10-08 governance review: this nominal geometry evidence is complete and sufficient for the geometry gate; stop expanding it.09 actual staticreload failed beforecollisionverdict, not a geometry failure. The pending scientific gates are targetedIsaaccriticalstate safety and repeatedreset, not zero-stepqueryperfectness/exhaustivemodel-equivalence. Staticseriesbudget exhausted; no newexperiment/source afteruseroverride, fallback decisionpending. [Review](TASK01_GOVERNANCE_REVIEW.md).

Latest Oct8 downstream08: original native/static q/FK gates and zero-step passed; moving query proof still failed at START. 09 original-handle rebuild prepared only; original discrete geometry evidence and thresholds unchanged, READY not run.

2026-10-08 latest downstream gate: GUI07 actually achieved zero physics callbacks but could not prove the original link2 native query target at START, accepted0 before any overlap verdict. GUI08 subsystem refresh prepared/not run; this does not change the native discrete geometry PASS or authorize READY/FROZEN.

Date: 2026-10-07. Scope: `single_cube_core_benchmark`.
Result: **PASS_DISCRETE_FULL_CHAIN_ONLY** (native probe exit 0).
TASK01 overall remains IN_PROGRESS; this is not FROZEN or physical PASS.

## Fixed benchmark and method

[ADAPTATION] User-approved START=(0.550,0,0.380) m, quaternion xyzw=[0,0,0,1], already held by both arms/off table/no grasping. This is a new scientific benchmark, **not legacy Task27 feed** (D034). PRE_PUSH=(0.790,0,0.260); TARGET=(1.100,0,0.260). Shared-grasp transforms, original L tools, carriage, robot bases, meshes, SRDF/ACM and independent IK acceptance were not changed.

[ENGINEERING] LMA epsilon=1e-7, orientation weight=0.01; acceptance remains translation<=1e-5 m and rotation<=1e-4 rad. START uses the original finite deterministic64-seed/arm pool (retain12), accepts the first full-FCL-free pair; subsequent states each solve once from the preceding actual joint configuration. No new seed after a failed state. The original SRDF/ACM is checked unchanged.

Checks at every state: dual IK and limits; shared-grasp residual; self/inter-arm/full robot-world FCL; signed distance and closest pair/points; wrist/tool-environment distance including link7/link8/tool against deep/+Y/-Y/table; minimum joint margin. Cube/environment is separately audited by original-size, identity-orientation AABB against table and all three walls, because world/world Cube collisions are not covered by robot FCL. Boundary touch is distinct from positive-volume penetration.

No Isaac, robot/ROS/suction commands, integration steps or scientific timestamps were used. These are discrete geometry indices, **not a time-parameterized trajectory or continuous collision certificate**.

## Actual full-chain results

| Segment | States | Maximum Cube translation step | Min joint margin | Max translation / rotation grasp residual | Collision result |
|---|---:|---:|---:|---:|---|
| START→PRE_PUSH (A) | 136/136 | 1.987616 mm | 0.4618280014 rad | 1.538421e-9 m / 5.063085e-6 rad | self/inter/world FCL free; 544 Cube-env checks, 0 penetration |
| PRE_PUSH→TARGET (B) | 157/157 | 1.987179 mm | 0.4678486267 rad | 8.685638e-9 m / 9.944048e-6 rad | self/inter/world FCL free; 628 Cube-env checks, 0 penetration |

293 records / 292 distinct Cube states: PRE_PUSH is recorded in both segments. A state135 and B state136 use **exactly the same 14q and Cube pose**. B was checked again from A's actual PRE configuration; an old B path with a different IK branch was not spliced in.

Every state's minimum signed FCL distance, exact pair/category, closest points and wrist/tool-env distance are in [the CSV](../results/20261007_TASK01_full_single_cube_geometry01/per_state_minimum_fcl_distance.csv). Every 14q, full link FK, per-pair distances, margins and acceptance diagnostics are in [state_records.json](../results/20261007_TASK01_full_single_cube_geometry01/state_records.json).

### Critical states for Isaac parity

| Evidence | State / segment index | Cube center (m) | Pair | Distance |
|---|---|---|---|---:|
| A minimum all / wrist-env | 135 / A135 (PRE) | (0.790,0,0.260) | Cube↔right tool / table↔left tool | 0.999798 / 25.000030 mm |
| Full-chain minimum all | 196 / B60 | (0.9092307692,0,0.260) | shared_cube↔left_fr3_side_suction | 0.999669 mm |
| Full-chain minimum robot-env excluding Cube / wrist-env | 292 / B156 (TARGET) | (1.100,0,0.260) | left_fr3_link7↔carriage_deep_wall | 2.212219 mm |
| Full-chain minimum inter-arm | 196 / B60 | (0.9092307692,0,0.260) | left tool↔right tool | 123.628133 mm |

The approximately 1 mm minimum is the existing intended suction/Cube offset, not a wall gap. The 2.212219 mm wall clearance is still **MoveIt-model-only**; it cannot certify the original Isaac convexHull/contact geometry safe (BUG019).

## Recorded reset configuration, not frozen

```yaml
benchmark_a_start_joint_state_rad:
  left: [0.6556998327304024, -0.9158460955296517, 0.9361619490344238, -2.43079576661854, 0.7029262366728565, 1.726259984792982, 1.2164416425071283]
  right: [-0.47514226618537353, -1.1301697571742122, -0.9979978814517659, -2.404800398376118, -0.8636013246419576, 1.5572941255153623, -1.0752371378447552]
benchmark_b_start_joint_state_rad:
  left: [0.21744143569271313, -0.5164914914460937, 1.0171641693028668, -2.6091513733003326, 0.5632971965150655, 2.2361990887058414, 0.7985013134114293]
  right: [0.03097153340224297, -0.8182678884154884, -1.2267956826752937, -2.5710825559909845, -0.8729224205691766, 2.028938813811622, -0.5717471798134617]
```

These actual values are copied into the candidate YAML. Repeated reset must use them, not randomly re-solve IK. Physical parity and repeatability are separate subsequent gates. User final freeze is pending.

## Reproduction and provenance

Source commit `fb643f1`; model commit `d4b290c1f929428e7d3bd6776b6d55709ca34b0f`.
The actual execution used [config_at_run.yaml](../results/20261007_TASK01_full_single_cube_geometry01/config_at_run.yaml) before recording the returned q. Its SHA256 is `3dbe7fcb192d09db83be801314582249ac3c0c77c9ffd683801ca7680d54881b`. Do not compare that old run hash to the subsequently updated candidate YAML.

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash
cmake -S platforms/isaac_ros2/probes/single_cube_geometry -B build/single_cube_geometry
cmake --build build/single_cube_geometry --target task01_full_single_cube_geometry -j2
build/single_cube_geometry/task01_full_single_cube_geometry \
  configs/benchmark/benchmark_v1.yaml \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.urdf \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf \
  /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/config/kinematics.yaml \
  results/20261007_TASK01_full_single_cube_geometry01
```

This is the actual-run command; choose a new output directory for a new run, do not overwrite the recorded evidence. The expanded input XML/raw build/stdout logs are preserved locally under ignored raw/. Structured results, immutable config snapshot, metadata/hashes and [selected original stdout](../results/20261007_TASK01_full_single_cube_geometry01/probe_evidence.log) are tracked.

The first build-only log is retained; only the final actually completed build02 binary was invoked. Final binary SHA256 `7da613a4cac990a7c07adb2cee10bfce9fe9f01f3bc709b26562305eb0840605`. Full input/source/command/metric provenance: [metadata.json](../results/20261007_TASK01_full_single_cube_geometry01/metadata.json), [summary.json](../results/20261007_TASK01_full_single_cube_geometry01/summary.json).

## Next gates / limits

Latest Oct8 checkpoint: GUI06 mirror output was no longer stale, but zero-step guard still rejected SDK implicit integration before native moving queries. 07 no-PLAY initialization is prepared/not run. Original full discrete geometry PASS and recorded exact START/PRE14q remain unchanged; READY/reset NOT_RUN.

Current Oct8 checkpoint: GUI05 correctly rejected unintended physics dispatch during its pause-labelled refresh (accepted0). This is not a valid static parity run or a new geometric verdict. Official render-only dispatch06 is prepared/not run; native all-state geometry evidence remains unchanged. No model/threshold edits, no READY/reset. See [parity report](TASK01_ISAAC_MODEL_PARITY.md).

Later Oct8 checkpoint: GUI04 stopped on an SDK Cube pose-field precision error before any accepted parity sample; correction05 prepared, not run. This changes neither the native geometry PASS nor any model/benchmark threshold. READY/reset remains gated; [actual parity attempts](TASK01_ISAAC_MODEL_PARITY.md).

2026-10-08 update: actual guarded visible GUI03 rejected a stale USD source frame at START before accepting any parity sample; native discrete geometry evidence above is unchanged. This is an engineering adapter stop, not IK/FCL failure or confirmed BUG019 overlap. Corrected output adapter04 is prepared, not yet run; READY/reset remains NOT_RUN. See [parity report](TASK01_ISAAC_MODEL_PARITY.md).

Independent stored-evidence verifier actually passed twice (exit0, 210,164 assertions): counts, exact seam, <=2mm steps, finite positive distances/nearest points, every collision/AABB result, CSV/summary/metadata consistency, immutable config and source/model/binary hashes. It does not read the changed working YAML and is not another probe or physics run. [Validation result](../results/20261007_TASK01_full_single_cube_geometry01/evidence_validation.json).

```bash
python3 platforms/isaac_ros2/probes/single_cube_geometry/verify_full_chain_evidence.py \
  results/20261007_TASK01_full_single_cube_geometry01
```

Visible GUI static parity must compare actual original PhysX cooked shapes/query hits at these same q/Cube states. First unexpected FCL-free/Isaac-overlap pair stops without altering geometry or ACM. Only parity success permits repeated post-physics-stamped START/PRE READY/reset. No dynamics, suction stability, controller execution or force-control claim is made here. BUG001/wrench remains TASK10-IS, non-blocking for TASK01. TASK02/P4 have not started.
