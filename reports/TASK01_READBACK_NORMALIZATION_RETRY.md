# TASK01 — Authorized readback normalization repair and one bounded retry

2026-10-08. **PREPARING / runtime NOT_RUN (additional allowance0/1). TASK01 PARTIAL / DRAFT, not FROZEN.**

## PRE-TASK REPORT

```text
Task: TASK01 / D039 readback-validator repair
Scientific objective: establish complete actual INSERT_READY under the fixed handoff
Minimum sufficient evidence: actual INSERT_READY sample; complete expected/readback
  CollisionObjects and composed worldshape checks at initial0 and postrail+.100
Current scope: message-representation equivalence validator and original evidence
Explicit non-goals: TARGET, resets, geometry/tool/carriage/ACM/physics changes,
  station/helper/grasp changes, IK/FCL acceptance changes, suction tuning,
  force control, parity10, five-Cube application
Attempt budget: one separately authorized repair and bounded runtime1/1
Preferred method: compare T_world_object × T_object_shape, keep full raw messages
Fallback method: none authorized; never relax epsilon or create third validator
Stop condition: any user-listed guard; readback recurrence→ENGINEERING ESCALATION
Files expected to change: C++ validator/pure tests/CMake; launch evidence path only;
  this report, run metadata/selected evidence, six records and TASK01 link
Validation plan: pure normalization/rejection tests, build, source/config hashes;
  then one visibleGUI launch with180s wholeprocess bound and reset-repeats0
Known risks: unspecified/empty ROS quaternion representation, serialization precision,
  subsequent safe transition/rail/rear stages have not yet been tested in this run
Need user confirmation: no, explicit additional allowance received
```

## Exact authorization and scientific boundary

Previous `f73490d` run failed at `bilateral CLOSED→OPEN→refresh(0)→table readback guard`, before any safe transition/rail/rear. This is not handoff geometry failure. User now approves **one and only one** representation-aware correction/retry; if the readback root remains unresolved, STOP/ENGINEERING ESCALATION, not a third validator.

[ENGINEERING] Compare id, world frame, primitive count/type, dimensions and composed worldshape SE3. Fixed message-equivalence epsilons:

```text
translation norm ≤1e-8 m
rotation angle ≤1e-8 rad
dimension absolute difference ≤1e-12 m
```

These are serialization/numerical-equivalence checks, **not** benchmark spatial success, collision padding, IK or FCL tolerances. No runtime-adjustable epsilon, no autonomous relaxation. Equivalent quaternion signs and equivalent object/shape pose factorization must pass; actual translation/rotation/type/size/frame/count mismatch must stop. Invalid/nonfinite inputs stop with raw evidence.

For every refresh retain full sent/readback message (lossless ROS CDR plus all-field readable JSON), object/primitive poses, dimensions/type, composed world poses, errors, shift, generation and measured native physicsstep/simstamp. Save before acting on validation verdict, including failure. Initialshift0 and postrail.100 use the same validator; freshworld requirement is unchanged.

## Runtime bound and unchanged inputs

```text
PRE_PUSH_SHARED (.650/.650)
→ bilateral OPEN confirmed
→ original safe helper/pusher transition
→ fixed .750/.750 rails
→ rebuilt +.100 shifted planning world
→ right rear(-X) existing SG regrasp
→ INSERT_READY capture
→ STOP
```

No repeated restore or TARGET continuation. GUI harness, bridge, extracted original primitives and benchmark YAML stay byte-identical to `f73490d`. Existing q/Cube-drift/collision/FCL/rail guards remain. Native post-step timestamp remains the scientific state clock; walltime is only a deadline/log profile.

Immutable hashes at preflight:

```text
benchmark_v1.yaml:25b7162c848b4cfeeff7e07a8cd154f26dff215c6d8f3d1caf8cf6333bcc8783
task26_reused_primitives.hpp:2051c84b9275e5bf1d286dcfd02b441e32a490e7b0b120757068878425d45cb1
reused_bridge.py:e4c1dc8bea2098d315d2404bdbd0b5c986ca46df4ac9a7facca123a4e5dabae1
task01_insert_ready_gui.py:539615dc789460abc2e3b0b2e7c09dff8c7ad00b8dc74327f1e8d114a0a1a77c
```

## Planned command (exactly one authorized invocation)

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
DISPLAY=:1 ROS_LOCALHOST_ONLY=1 ROS_DOMAIN_ID=0 \
TASK01_READBACK_EVIDENCE_DIR=/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/results/20261008_TASK01_readback_retry01/raw/planning_world_readback \
timeout --signal=KILL 180s scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/handoff/task01_insert_ready_gui.py \
  --output-dir results/20261008_TASK01_readback_retry01/raw \
  --wall-limit-sec 180 --reset-repeats 0
```

Environment path only passes the evidence destination into the existing nested launch; no GUI/bridge/runtime-topology code change. Same controller deadline120s and15s cleanup reservation under the180s outer hard bound. Any collision, safe-transitionFCL failure, Cube drift, measuredrail/base/shift mismatch, rear failure or absent attachment stops. If successful capture, submit actual candidate to user, TASK01 remains PARTIAL; no FROZEN or next-stage execution.

## Software preflight (not physical evidence)

The single preparation CMake Release build and pure `--self-test` passed (exit0; tests run before ROS initialization). Tests cover equivalent object/primitive factorization, noncommuting composition, quaternion signs, actual mismatches, exact/next-float epsilon boundaries, invalid/nonfinite inputs, full-field JSON and CDR roundtrip. Launch pure construction passed (7 entities). Independent read-only scope audit and `git diff --check` passed. No ROS/IK/Isaac was run in these tests. CMake needed no changes.

Immutable input hashes above rechecked unchanged. New driver source SHA256 `e8ed058e58e63eb7f0a36bd02daa25151e62d81867d0bc52754192a9375f909a`; validator `6ab64d3fa680a92957d24198a2f2c895ce4c026559414112e92ba386949ec030`; launch `4c707922986112f9d667d3ba212191c0099bcdb94a010050168361438a7f3f47`.

## Outcome

Pending software preflight and single runtime attempt. Neither representation validation nor handoff completion is presumed from this preparation entry. Historic raw/negative evidence remains untouched. BUG001/wrench stays TASK10-IS; shutdown fault deferred; full collision-model equivalence a known limitation; five-Cube Task27 legacy.
