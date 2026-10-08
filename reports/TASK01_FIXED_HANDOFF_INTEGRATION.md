# TASK01 — D039 fixed-rail handoff integration

2026-10-08. **PREPARED / NOT_RUN; TASK01 PARTIAL / DRAFT, not FROZEN.**

## Requirement and bounded scope

User approves one integration ending at a complete, repeatable INSERT_READY candidate:

```text
PRE_PUSH_SHARED, both rails .650
→ bilateral physical OPEN confirmed
→ existing helper/pusher safe transition
→ both rails .750
→ measured base/rail checks, refresh planning world with shift +.100
→ right rear(-X) Surface Gripper regrasp
→ capture INSERT_READY
```

Fixed .750 is D039 common engineering setup, not a P3 controller variable; A/rest stays .650. No alternative stations or .650/.750 optimization comparison. No TARGET command in this run. The next B geometry/safety stage requires successful READY first.

One visible GUI launch, **180 s whole-process hard bound**, internal work deadline reserves 15 s for cleanup; controller deadline 120 s. Two restores of the same captured state within that launch (no new IK/handoff search) are capped and reported separately. First substantive collision, regrasp failure, or rail/world mismatch stops; no second launch. Earlier parity/control budgets remain exhausted.

## Reuse and classifications

- [ADAPTATION] User-approved fixed rail candidate and staged topology.
- [ENGINEERING] Fixed-source Task26 primitives from `631b1f65656d025c1bb2173e874192f3fe4d355a`; see [source audit](TASK01_PRIOR_PROJECT_REUSE_AUDIT.md).
- Original scene constructors/L geometry/official FR3 asset, SG lifecycle, same-stamp joint commands, and rail mover are reused, not redesigned. The AST adapter's only source patch makes the final rail setter exception fail closed.
- C++ extracts the original interpolation, synchronization, finite rear RRT candidate pool and full-RobotState FCL checks. It does not include the old whole application or TARGET push/exit.
- Current arm MoveIt scaling/time_scale=1.0; no old .12/3x robot settings, friction, drives, effort guard or deep-wall gap gate. The approved rail mover alone retains its internal .20 m/s / .001 m / .20 s / 1 s engineering constants; they are not robot trajectory scaling or P3 parameters.
- Normal Isaac SDK PLAY/warm-start, then PAUSE with explicit controlled steps, initializes existing prims. No zero-step, query-tree or native-handle repair.
- Fresh MoveIt world contains exactly current YAML table (1.5 m), three walls and one Cube. After base advance it is rebuilt, read back and acknowledged; each FCL scene is new. The fixed URDF bases remain .650; virtual planning coordinates use `physical_world_x - .100`, with measured actual bases recorded separately. Carriage physical frame does not move.
- No [ORIGINAL] paper controller or scientific algorithm implemented; no [DEVIATION] to tool/carriage/ACM/physics.

## Capture and guards

One live-PhysX post-step stamp/step is shared by measured bases/rails, both7q, Cube, link8-derived TCP poses, SG status, planning-world generation, helper park and carriage frame. Cube→rightTCP SE3 is measured in that same sample, explicitly **not a recovered native D6 joint anchor**. Optional public D6 identity is recorded if available; one SG per arm, not eight cup attachments.

`.01 rad` settle and `.005 m` Cube-drift guards are explicit engineering STOP conditions, not newly frozen scientific success tolerances. Rail/base/shift consistency uses 1e-5 m; no refresh at a merely approaching .7493 m. Cube/table and cup/Cube contact can be expected; L rod/manifold or non-allowed robot/environment penetration stops. All raw contact reports are retained by post-step stamp; contact-report absence is not proof of complete model equivalence/continuous collision freedom.

## Software-only checks completed before physical attempt

```bash
source /opt/ros/humble/setup.bash
cmake -S platforms/isaac_ros2/handoff -B build/task01_handoff -DCMAKE_BUILD_TYPE=Release
cmake --build build/task01_handoff -j2
build/task01_handoff/task01_rear_handoff --self-test configs/benchmark/benchmark_v1.yaml
python3 -m unittest discover -s platforms/isaac_ros2/handoff -p test_reused_bridge.py -v
python3 -m py_compile platforms/isaac_ros2/handoff/*.py
git diff --check
```

C++ build/pure world/rear/interpolation self-test PASS; 8 mock bridge tests PASS; Python syntax/launch construction PASS. These are not ROS/IK/Isaac acceptance. Initial compile BoundedVector assignment and startup wiring issues were fixed before any physical launch, not counted as simulator attempts.

## Authorized run command (one attempt only)

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
DISPLAY=:1 ROS_LOCALHOST_ONLY=1 ROS_DOMAIN_ID=0 \
timeout --signal=KILL 180s scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/handoff/task01_insert_ready_gui.py \
  --output-dir results/20261008_TASK01_fixed_handoff01/raw \
  --wall-limit-sec 180 --reset-repeats 2
```

Launcher starts only owned MoveIt/state publisher/thin driver; no old environment publisher/fake controllers/Task27. GUI self-shutdown and launch cleanup are engineering only. If hard termination leaves an owned ROS process group, reap that validated PID/group; do not relaunch.

## Pending outcome

Actual run metadata/results will be appended here. Neither deterministic START READY nor rear B safety is established by software tests. TASK01 remains PARTIAL; force/wrench BUG001 deferred TASK10-IS; five-Cube flow legacy/out of scope.
