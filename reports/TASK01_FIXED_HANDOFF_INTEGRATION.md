# TASK01 — D039 fixed-rail handoff integration

2026-10-08. **ONE ATTEMPT USED / STOP FOR USER; TASK01 PARTIAL / DRAFT, not FROZEN.** Preparation protocol below is retained; actual outcome takes precedence.

## Actual outcome — first planning-world readback gate STOP

Source commit `ee514703da4835e5b1f1f06f7fbb6777f6bc68c1`; [metadata and hashes](../results/20261008_TASK01_fixed_handoff01/metadata.json). The single authorized visible GUI run ended well inside its180s bound (Kit begins shutdown at20.914s). No second launch or runtime source repair.

Observed steps:

```text
normal SDK initialization
→ restore recorded PRE_PUSH14q/Cube, both bases .650
→ bilateral SG CLOSED observed
→ bilateral OPEN observed/confirmed by driver
→ initial planning world apply/readback at world_shift=0
→ STOP: Planning object differs after shift: task01_table
```

**No safe-transition path, rail move, rear regrasp, INSERT_READY capture, repeated restore, TARGET command or B geometry/FCL test ran.** The `.750/.750` YAML entries remain approved candidates pending actual measured capture. The name “after shift” is a generic guard message: this failure occurred at the **initial zero-shift refresh**, not after moving rails.

Selected actual evidence: [PRE_PUSH post-step sample](evidence/TASK01_FIXED_HANDOFF_PRE_PUSH_SAMPLE.json), [verbatim stop logs](evidence/TASK01_FIXED_HANDOFF_STOP.log). Raw351 state rows and351 contact rows remain local under the ignored run `raw/`, with hashes in metadata. The first recorded step is5 (four ordinary SDK warm-up steps precede the scientific sample stream); last355, sim stamps83,333,338→5,916,666,975ns. Both SG CLOSED observed196 samples, firststep6/time100,000,005ns; first confirmed OPEN step202/time3,366,666,842ns. These are native post-step times, not ROS log/wall times.

PRE_PUSH sample step17/time283,333,348ns:

- Both measured rail/base X=.6499999761581421m throughout; no rail command reached execution.
- Joint error relative to recorded PRE q: left0.000644268rad, right0.000361433rad. Cube translation error3.882252µm; actual Cube[.789996266,.000000154,.259998947]m. Full actual14q/TCP/relative transform/base/frame/status saved, not only nominal targets.
- Observed Cube mass.8000000119kg, effective material[.5,.5,0], TGS/GPU/60Hz/CCD/gravity retained. No drive/friction/tool/wall/ACM edit.
- Contact telemetry reports only cup–Cube and Cube–table pairs: minimum cup separations left+.954676mm/right+.999734mm; expected support Cube–table−.008691mm. No unexpected robot/tool–environment contact was reported **during this incomplete stationary prefix**. This is not whole-handoff safety, airborne shared-hold validation or deterministic READY/reset evidence.
- Right API reports CLOSED, but optional dynamic-control lookup returns handle0. Native D6 anchor/object identity was not established. Measured relative Cube→TCP is correctly marked as a physics-pose transform, not a joint-anchor proof.

### Read-only diagnosis, not a new attempt

Driver compares shape count, shape-pose count, dimensions and exact `primitive_poses[0]` using one combined error. It does **not** compare composed object+shape transforms. Installed MoveIt2.5.9 header `/opt/ros/humble/include/moveit/planning_scene/planning_scene.h:704–711` documents promoting a populated shape pose into the object pose when the object pose is empty, leaving the shape pose identity. `/opt/ros/humble/include/moveit/collision_detection/world.h:89–106` distinguishes object pose, relative shape pose and world shape pose.

Thus normal message normalization can trigger this guard while physical world geometry remains identical. This is the strongest source-supported explanation; **sent/received raw objects were not saved, so the exact failing field/value and real world offset are unconfirmed**. Do not classify it as an observed rail/geometry/collision failure, or as a fixed issue. No code correction/ROS diagnostic request/new run follows.

Cleanup: driverexit1; launch begins own-node shutdown; move_group exits−11 during destruction (preexisting lifecycle family, deferred, not the primary planning gate). Isaac wrapperexit0 despite savedfailure and no capture—wrapper0 is not acceptance. Owned Isaac/MoveIt/controller processes verified absent; no hard timeout needed.

### Governance verdict

```text
TASK01 = PARTIAL / DRAFT
Fixed handoff = INCOMPLETE, STOP at initial planning-world readback
INSERT_READY = NOT_ESTABLISHED
Rear B geometry/safety = NOT_RUN
Attempt allowance = 1/1 used; no autonomous retry
FROZEN = false
```

Minimum sufficient evidence for the requested handoff was **not achieved**. TASK-BLOCKING: world readback acceptance, then actual fixed-handoff/READY and rear B evidence. KNOWN LIMITATION: this guard lacks raw object values, native D6 anchor unavailable, and incomplete contact sampling is not model equivalence. DEFERRED: cleanup fault; BUG001/wrench TASK10-IS. LEGACY: five-Cube Task27.

Recommended next step **requires fresh user approval**: correct only the message-representation validation, save full sent/readback objects and verify composed world shape transforms; then one explicitly bounded same-station attempt. Do not loosen spatial acceptance, change geometry/ACM/physics or infer a new runtime allowance from this diagnosis.

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

## Earlier preparation checkpoint

At preparation time runtime was NOT_RUN. Actual result above supersedes that checkpoint. Neither deterministic START READY nor rear B safety is established by software tests. TASK01 remains PARTIAL; force/wrench BUG001 deferred TASK10-IS; five-Cube flow legacy/out of scope.

## POST-TASK REPORT

```text
Task: TASK01 / D039 fixed .650→.750 handoff
Status: PARTIAL / STOP FOR USER; not FROZEN
Scientific objective: reusable complete INSERT_READY before rear Benchmark B
Minimum sufficient evidence achieved: no
Completed: approved candidate/config; pinned-source adapters; software tests;
           one visible run, PRE_PUSH SG lifecycle observation, failure evidence
Files changed: benchmark_v1.yaml; platforms/isaac_ros2/handoff/ (7 source/test files);
               this report; selected PRE_PUSH JSON/stop log; run metadata;
               STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK;
               TASK01_BENCHMARK_FREEZE.md
Commands run: CMake build/pure self-test, 8 mock tests, Python syntax/launch construct;
              one 180s-bound GUI command above; read-only raw/hash/source inspection
Tests / experiment results: software PASS; integration incomplete at firstworld gate
Key metrics:351 nativepoststep samples; rails unchanged .649999976/.649999976;
            PRE17 Cube3.882µm/qleft.000644268rad/qright.000361433rad;
            capture0/reset0/railmove0/TARGET0
Blockers:
 TASK-BLOCKING: unaccepted world-readback, then actual handoff/READY/rear B evidence
 DEFERRED: BUG001 force/wrench TASK10-IS; shutdown lifecycle fault
 KNOWN LIMITATION: no raw sent/readback objects; public D6 lookup0/no native anchor;
                  reported contact absence is not full safety/equivalence
 LEGACY: five-Cube Task27 application
Attempt budget used:1/1; no second integration; prior exhausted budgets unchanged
Escalation required:yes, fresh bounded approval before repair/runtime
Paper fidelity:
 [ORIGINAL]:no paper control method implemented
 [ADAPTATION]:user-approved fixed B station, current staged single-Cube topology
 [ENGINEERING]:pinned SG/rail/rear/FCL reuse, thin interface/poststep recorder
 [DEVIATION]:none to benchmark tool/carriage/ACM/physics/thresholds
 [EXPERIMENTAL]:one incomplete runtime candidate integration, not scientificPASS
Records updated:STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK all yes
Open risks:world guard normalization, untested remainder, held START reset pending
Recommended next step:explicitly approved composed-object+shape validation and
                      raw object capture, then one bounded same-station retry
Git branch:task01-benchmark-draft
Runtime source commit:ee514703da4835e5b1f1f06f7fbb6777f6bc68c1
Dirty files intentionally preserved:two prior parity launch logs; current full launchlog
```
