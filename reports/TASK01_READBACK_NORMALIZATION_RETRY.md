# TASK01 — Authorized readback normalization repair and one bounded retry

2026-10-08. **ENGINEERING ESCALATION / GUI initialization STOP. Additional allowance1/1 consumed. TASK01 PARTIAL / DRAFT, not FROZEN; INSERT_READY NOT_ESTABLISHED.** Preparation entries below describe the pre-run checkpoint, not the final result.

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

## Actual command (exactly one authorized invocation)

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

## Actual outcome — initialization STOP, not readback or geometry failure

The sole attempt ran source `08c34b847906a0f229a442290467c8e1b63fdc22` using the unchanged GUI. Its log ends:

```text
[7.514s] app ready
Fatal Python error: Segmentation fault
... python.sh: ... 398623 ... core dumped ...
There was an error running python
```

The launcher returned **exit1**, before the 180s cap. The native crash's cause is **undetermined**; the log alone does not establish a validator, plugin, resource or model cause. No repair, second launch, debug probe or threshold change followed. Read-only process checks found no remaining matching Isaac/handoff/MoveIt processes.

Actual files are only [inputs_at_run.json](../results/20261008_TASK01_readback_retry01/inputs_at_run.json), [complete launch.log](../results/20261008_TASK01_readback_retry01/launch.log) and [metadata](../results/20261008_TASK01_readback_retry01/metadata.json). `raw/inputs.json` verifies source/config/GUI/launch/binary hashes, visible GUI, reset cap0 and no TARGET. There is no `scene_audit.json`, post-step state/contact stream, MoveIt driver log, refresh JSON, PRE_PUSH sample or INSERT_READY capture.

Therefore:

- readback/composed-transform **runtime validation NOT_REACHED**; neither PASS nor recurring readback failure;
- initial shift0 and post-rail shift+.100 sent/readback evidence **not produced** because no refresh occurred;
- safe transition, rails, rear regrasp and attachment **NOT_REACHED**;
- no scientific native physics step/simulation timestamp or actual q/Cube/TCP/rail measurement available in this run;
- collision/FCL/Cube-drift/rail consistency guards **NOT_EVALUATED**, not safety PASS/FAIL;
- INSERT_READY **NOT_ESTABLISHED**, repeated resets0, TARGET not commanded;
- TASK01 **PARTIAL**, not PASS CANDIDATE or FROZEN; budget **1/1 used**.

Software compilation and pure tests passed, but are not physical evidence. The previous `f73490d` readback STOP remains separate history; this run cannot demonstrate that the normalization repair fixes it in live MoveIt. Historical negative/raw evidence remains untouched. BUG001/wrench stays TASK10-IS; prior shutdown issue deferred; full collision-model equivalence a known limitation; five-Cube Task27 legacy.

## ENGINEERING ESCALATION

```text
Scientific question: can the approved fixed D039 handoff establish actual INSERT_READY?
What is already established: original reuse/provenance; software validator/tests PASS;
  prior supported PRE_PUSH and bilateral OPEN observations from earlier run only.
What remains unknown: live composed-world readback and complete fixed handoff state.
Why the remaining unknown matters: cannot accept INSERT_READY from software tests.
Attempts made: this separately authorized bounded retry1/1; startup SIGSEGV before
  any MoveIt refresh. No second attempt and no third validator.
Root blocker classification: TASK-BLOCKING GUI native initialization failure;
  exact root cause not diagnosed. Readback correctness remains runtime-unverified.
Is it still task-critical: yes, for actual INSERT_READY evidence.
Lower-cost evidence available: successful pure build/serialization/SE3 tests and
  source/hash audit; insufficient for physical handoff acceptance.
Recommended action: stop runtime; preserve fixed geometry/topology and evidence.
Need user decision: whether to authorize a separate bounded startup diagnosis and
  subsequent attempt, or keep the task paused. No further authority inferred.
```

## POST-TASK REPORT

```text
Task: TASK01 / readback-validator normalization, independent allowance1/1
Status: PARTIAL; runtime STOP; INSERT_READY NOT_ESTABLISHED
Scientific objective: establish actual fixed handoff INSERT_READY
Minimum sufficient evidence achieved: no
Completed: fixed object×shape equivalence validator, full raw refresh persistence,
  lossless CDR/all-field JSON, strict pure tests, launch evidence-directory wiring;
  one bounded visible attempt, negative startup evidence preserved.
Files changed: collision_readback.hpp; task01_rear_handoff.cpp;
  moveit_handoff.launch.py; this report; run metadata/log/input; six records; TASK01.
Commands run: one preparation build/self-test; pure launch construction;
  sole actual GUI command above; read-only hashes/process/artifact audit; git publish.
Tests / experiment results: software PASS; physical initialization STOP (exit1).
Key metrics: additional attempts1/1; recorded post-step samples0; refresh records0;
  actual q/TCP/Cube/rail/step/time unavailable; no READY, reset or TARGET.
TASK-BLOCKING: GUI native initialization crash; readback/handoff runtime unverified.
DEFERRED: BUG001/wrench TASK10-IS and earlier shutdown issue.
KNOWN LIMITATION: full model equivalence not required/established.
LEGACY: old five-Cube Task27, not executed.
Attempt budget used: additional1/1; previous exhausted budgets unchanged.
Escalation required: yes; no automatic retry or new validator/probe.
Paper fidelity: ORIGINAL paper/controller unchanged; ADAPTATION D039 fixed topology
  unchanged; ENGINEERING message equivalence and evidence only; no new DEVIATION
  or EXPERIMENTAL controller/model alteration.
Records updated: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK/TASK01.
Open risks: native crash cause unknown; live readback and downstream stages untested.
Recommended next step: user decision on separate startup diagnosis/attempt budget.
Git: task01-benchmark-draft; code checkpoint08c34b8; evidence commit follows.
Dirty files preserved: three pre-existing untracked historic launch logs.
```

### Software command provenance

These commands were already run once during preparation; **not rerun after the crash**. Outputs reside in tool history, not an independently captured compiler log:

```bash
source /opt/ros/humble/setup.bash
cmake -S platforms/isaac_ros2/handoff -B build/task01_handoff -DCMAKE_BUILD_TYPE=Release
cmake --build build/task01_handoff -j2
build/task01_handoff/task01_rear_handoff --self-test configs/benchmark/benchmark_v1.yaml
```

Tool session44362 exit0: `[100%] Built target task01_rear_handoff`; `PURE SELF TEST PASS: current world/Task26 regressions plus composed readback, strict epsilon boundaries, malformed inputs and raw CDR/all-field JSON; no ROS/IK/Isaac`. Launch AST/import/`generate_launch_description()` test, using system Python and existing ROS/install environment, returned `PURE LAUNCH CONSTRUCTION PASS: 7 entities, evidence-directory env wiring, no ROS launch` (exit0). This is construction only, not node/MoveIt startup.
