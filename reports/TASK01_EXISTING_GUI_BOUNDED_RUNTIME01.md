# TASK01 — authorized existing-GUI runtime01

2026-10-09 (Asia/Shanghai). [ENGINEERING]. Earlier missing-GUI preflight below is preserved as history.

## Current outcome — INSERT_READY captured; sole runtime stopped

```ini
TASK01 = PARTIAL
INSERT_READY = ESTABLISHED_CANDIDATE
existing_GUI_physical_attempt_used = 1/1
TARGET = NOT_RUN
reset_repetitions = 0
FROZEN = false
```

Operator supplied a normally running visible Isaac GUI (Kit PID39508, existing executor127.0.0.1:8226). The approved sequence was executed once: stopped Stage → scene loader → scene ready → **operator manual Play** → bridge loader → saved PRE_PUSH_SHARED → unchanged external ROS driver. No standalone/startup GDB/app.update probe, source repair, recomputation of the recorded PRE_PUSH restore configuration, new IK algorithm, model/physics/ACM/threshold/station change, or second invocation. The unchanged driver retains its existing rear-approach planning/candidate pool. Executable source remains `bbe97849e3e3cd5708861de676e7b952ec00fecb`; invocation HEAD `005cd553ca2fed1a9e8fa37d151930b569a6777a` adds records only. Source diff and critical hashes match the approved executable revision.

This establishes **one engineering INSERT_READY candidate under the original gates**, not TASK01 PASS, FROZEN, repeated reset, stable shared grasp, force control, or successful insertion. The authorized run ends here; no additional experiment is authorized by this outcome.

### Seven observed handoff stages

All scientific state values below use native **post-physics-step simulation timestamps**, not wall time. Integer timestamps are nanoseconds.

| Stage | Saved evidence | Outcome |
| --- | --- | --- |
| PRE_PUSH_SHARED restore | step2829 / stamp47150002459; rails≈.650/.650, actual14q/Cube/TCP saved; bilateral SG CLOSED | Established using recorded configuration |
| Bilateral release | first dual OPEN at8448 /140800007343; refresh1 input8454 | OPEN confirmed; no abnormal Cube drift stop |
| Safe helper/pusher transition | both Cartesian fractions1.0000; synchronized full FCL PASS,227 samples; original settle gate passes | No original unexpected-contact stop |
| Dual rail advance | movement starts8685; both measuredX=.7499998807907104 at8714; SG both OPEN | Fixed .650→.750 move observed |
| Fresh planning world | shift0/generation1 and shift+.100/generation2; complete raw expected/readback; composed validation PASS | Post-step ACK8455 and8715 saved |
| Right rear regrasp | existing rear candidate pool8; synchronized FCL PASS,354 samples; first left OPEN/right CLOSED8959 | Original rear approach/settle/regrasp gates pass |
| INSERT_READY capture | step8967 / stamp149450007794; rails.750/.750, arrived true/true, fresh generation2, left OPEN/right CLOSED | Candidate saved; driver exits0 |

At refresh2 input8714 and ACK8715, the rail `arrived` flags were still false although measured rail/base X met the unchanged gate. At candidate8967 both flags are true. This is reported as observed, not hidden or patched. No old shifted world is accepted as fresh during rail motion.

### Candidate state (complete actual state is in JSON)

- Cube world xyz: `(.791237294674, .000650116708, .260043621063)` m; full quaternion saved.
- Left/right rail X: `.750/.750` m. Left/right measured base xyz: `(.750, -.600000023842, -1.1175871e-8)` and `(.750, +.600000023842, -1.1175871e-8)` m; full base orientations saved.
- `world_shift_x=.09999999999999998`, planning generation2, refreshed true, acknowledged shift `.100`.
- Left SG OPEN; right rear SG CLOSED. Right TCP xyz: `(.728603430541, -.000617979526, .261441324648)` m.
- Cube→rightTCP translation: `(-.062640874107, -.000906094429, +.001364721033)` m; full relative quaternion, both TCP poses, actual14q, helper park label and actual helper q/TCP saved.
- Carriage frame remains `(.910,0,.200; quaternion [0,0,0,1])`; this is the unchanged authored carriage reference, not a new live rigid-body measurement.

Candidate actual7q, radians:

```yaml
left: [0.5367751717567444, -1.3037140369415283, 0.18305011093616486, -2.3715803623199463, 0.2002614587545395, 1.0787299871444702, 0.6808245182037354]
right: [0.17275570333003998, -1.2840396165847778, -1.515870213508606, -1.78056800365448, -1.2768301963806152, 1.5816559791564941, -2.7501113414764404]
```

These are recorded candidate measurements, not a new frozen reset configuration or benchmark edit.

### Readback and contact evidence

Each refresh saves all5 complete expected and5 observed CollisionObjects, full JSON/CDR bytes, object/primitive poses, dimensions/types, composed world poses, input/post-readback snapshots and post-step ACK. Offline CDR byte-length checks pass; no separate ROS re-read or CDR decode was performed during offline review.

| Refresh | Shift / generation | Input step / stamp | ACK step / stamp | Largest composed translation / rotation / dimension error |
| --- | --- | --- | --- | --- |
| 1 | .000 /1 | 8454 /140900007349 | 8455 /140916674016 | 0m /1.017445442e-20rad /0m |
| 2 | .100 /2 | 8714 /145233340908 | 8715 /145250007575 | 0m /1.016453538e-20rad /0m |

Both original validators report PASS/errors=[] at unchanged message-equivalence epsilons `1e-8m`, `1e-8rad`, dimensions `1e-12m`. These are not collision/success tolerances. Table object×primitive normalization is present in actual readback and composes to the same world geometry. Generation2 describes refresh2's Cube snapshot, not an assertion that the later moving Cube equals its cached pose exactly.

6152 state rows and6152 contact rows align one-to-one by step/stamp,2817–8968 /46950002449–149466674462ns, with no missing steps, duplicate or backwards stamps. Raw contact stream contains978 headers /3859 points (9 headers have no points). Offline classification using the **unchanged existing guard** reports0 unexpected penetration events. No `failure.json` or `unexpected_collision.json` was produced. Candidate8967 has one matching contact row:5 pairs /20 points, expected Cube/table plus right four cups. Minimum Cube/table separation is−.056289mm, expected support contact; right cup/Cube separations are positive,2.264–3.012mm, not measured flush contact.

Maximum measured Cube position drift over the saved stream is **1.479843mm from nominal PRE_PUSH `[.790,0,.260]`**. Candidate drift is1.398375mm from nominal,1.401641mm from saved PRE sample, and1.398464mm from refresh2 input. These references are deliberately distinguished; all remain within the unchanged original5mm guard. No continuous collision certificate, full PhysX/MoveIt equivalence, or exhaustive overlap-free proof is claimed.

### Limits and shutdown anomaly — no repair or rerun

- Attachment reports existing Surface Gripper CLOSED and joint name, but **`public_d6_handle=0` / `actual_joint_anchor=UNAVAILABLE`**. Cube→TCP transform is derived from same-step actual poses, not independently measured native D6 anchors. Native attachment identity/anchor certification remains unavailable; do not call it verified.
- Candidate Cube linear speed `.0174252684m/s`, angular speed `.0874547023rad/s`: an instantaneous candidate, **not a static/stable-held READY proof**. TCPs use measured link poses plus unchanged fixed tool transform.
- Existing adapter ends by pausing GUI and opening SG. Final GUI is alive but is **not the captured held state**. No reset repetition/hold-duration test was run.
- Raw summary marks external driver exit `NOT_OBSERVED`; independent terminal log proves driverPID43175 exits0 after capture. During subsequent SIGINT cleanup, **move_group PID43171 exits−11 (segmentation fault)**. PTY/wrapper0 does not make the overall launch clean. GUIPID39508 remains alive; owned ROS processes are gone. This repeats a historical cleanup symptom, is recorded as DEFERRED for this candidate-only scope, and was not diagnosed/fixed/retried.
- Original launch warnings/errors (no3D sensor plugins/controller_names, missing joint acceleration limits using default1rad/s², deprecated APIs/duplicate rosout/world-removal warnings) remain in the complete log. They did not trigger the existing handoff stop; no parameter-chain perfection claim or new repair.
- Adapter reports104.874349s **engineering wall runtime**, including the held prefix/manual terminal delay. External driver log10:28:21–10:28:36 is also engineering only; neither is a P3 efficiency score or scientific simulation clock.

### Artifacts / publication

Actual native evidence: [run inputs](../results/20261009_102650_295770_TASK01_existing_gui_handoff01/inputs.json), [PRE sample](../results/20261009_102650_295770_TASK01_existing_gui_handoff01/pre_push_shared_sample.json), [INSERT_READY](../results/20261009_102650_295770_TASK01_existing_gui_handoff01/insert_ready_candidate.json), [raw summary](../results/20261009_102650_295770_TASK01_existing_gui_handoff01/summary.json), [refresh1](../results/20261009_102650_295770_TASK01_existing_gui_handoff01/planning_world_readback/refresh_0001.json), [refresh2](../results/20261009_102650_295770_TASK01_existing_gui_handoff01/planning_world_readback/refresh_0002.json), [complete external driver log](../results/20261009_102650_295770_TASK01_existing_gui_handoff01/external_moveit_driver.log).

Engineering lifecycle and offline review: [metadata](../results/20261009_TASK01_existing_gui_runtime01/metadata.json), [selected stages and candidate contact](../results/20261009_TASK01_existing_gui_runtime01/evidence_summary.json), [offline audit](../results/20261009_TASK01_existing_gui_runtime01/offline_review.json), [artifact/source hashes](../results/20261009_TASK01_existing_gui_runtime01/artifact_manifest.json), exact requests/responses and single-driver command in the same directory. Large raw state/contact JSONL remains **local, untracked, SHA256-indexed**, not deleted or represented as published full data. Complete raw readback, candidate and selected same-step contact evidence are published.

### POST-TASK REPORT — actual runtime

```text
Task/status: TASK01 PARTIAL; INSERT_READY ESTABLISHED_CANDIDATE; STOP FOR USER
Minimum sufficient evidence: one complete actual candidate and seven gate outcomes
Completed: approved existing normal GUI lifecycle and unchanged fixed handoff
Files changed: evidence/report/metadata/persistent records/README only
Commands: one scene load; operator manual Play; one bridge load; one external
  ROS launch; read-only completion/process/hash checks; offline evidence audit
Result: candidate8967/149450007794ns; rails.750/.750; leftOPEN/rightCLOSED;
  generation2/shift+.100; original FCL/contact/drift/readback gates pass
No runs: TARGET, reset, Benchmark A transport, force/wrench/P3, five Cube
TASK-BLOCKING next acceptance unknowns: rear B validation and repeatable held
  READY/reset remain unperformed; user must approve next scoped work
KNOWN LIMITATION: native anchor/handle unavailable, nonzero capture speed,
  sampled contacts/derived TCPs are not stability or full model parity proof
DEFERRED: move_group cleanup−11; force/wrench belongs TASK10-IS
LEGACY: standalone image-core/parity/debug/five-Cube routes not resumed
Attempt budget: sole authorized physical/lifecycle attempt1/1 consumed
Escalation: no new repair or retry; preserve shutdown anomaly and limits
Paper fidelity: ENGINEERING integration/evidence only; no algorithm change
Records: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK/TASK01
Next: user reviews candidate/limits; no automatic TARGET/reset/PASS/FROZEN
Git: task01-benchmark-draft; executable source bbe9784 byte-identical
```

## Historical preparation and missing-GUI preflight (superseded by outcome above)

## Runtime resume — PRE-TASK REPORT (before sole scene load)

User reports GUI ready. PID39508 is the normally started Kit GUI with the existing8226 listener; one read-only executor request succeeds, current Stage exists and Timeline is STOPped (not PAUSE). No standalone/startup/debug launch. Current HEAD005cd55 contains records only after executable sourcebbe9784; all active source/config hashes match, runtime source diff is empty.

```text
Task: same authorized existing-GUI PRE_PUSH_SHARED→INSERT_READY attempt1/1
Scientific objective/minimum evidence: establish complete actual INSERT_READY;
  seven stages with unchanged FCL/contact/drift/world/attachment gates
Scope: stopped current Stage→unchanged scene→operator Play→unchanged bridge
  →PRE_PUSH_SHARED saved→external unchanged handoff driver
Non-goals: TARGET/reset/A transport/force/P3; no source/model/physics/ACM repair
Attempt budget: one physical/lifecycle invocation; scene load begins1/1;
  prior budgets unchanged, no same-round fix/reload/rerun
Preferred method: existing normal GUI / reviewed Task26 lifecycle
Fallback: NONE
Stop: first explicit native/lifecycle/restore/release/drift/FCL/rail/world/contact/
  regrasp/attachment failure, or adapter deadline; no automatic retry
Files expected to change: evidence/report/metadata/six persistent records only
Validation: observe native post-step actual state and original driver gates;
  preserve complete raw expected/readback objects at shift0/.100
Risks: cooperative deadline not native-hang OS cap; external driver ownership;
  final shutdown opens SG, candidate capture not held-reset proof
User confirmation: runtime already authorized; manual Play required after scene
```

## PRE-TASK REPORT

```text
Task: one existing-GUI PRE_PUSH_SHARED → INSERT_READY runtime
Scientific objective: establish and save actual INSERT_READY candidate only
Minimum sufficient evidence: all seven handoff stages with original guards;
  actual post-step rail/base/14q/Cube/TCP/SG/attachment/park/frame/world generation
  plus contact evidence and complete raw expected/readback objects
Current scope: exactly bbe9784 scene → operator Play → bridge → external driver
Explicit non-goals: TARGET, reset repeats, full A, force/wrench/P3, source fixes;
  standalone SimulationApp/GDB/app.update probes/parity/image-core research
Attempt budget: existing-GUI physical allowance1/1 authorized; used0/1
Preferred method: already-running visible GUI with existing local executor
Fallback method: NONE; do not create a GUI or use the historical launcher
Stop/escalation: first listed guard/GUI/lifecycle failure; no repair-and-rerun
Files expected to change: run evidence/report and persistent records only
Validation plan: preflight source hashes/GUI connection; then unchanged native
  handoff gates only if GUI prerequisite exists
Known risks: existing route unvalidated; cooperative cap not native hang killer;
  external driver ownership/exit code and held-state cleanup limits unchanged
Need user confirmation: runtime is already approved; operator must provide the
  normally started GUI/local executor before this same allowance can begin
```

## Read-only preflight outcome

- Current commit `bbe97849e3e3cd5708861de676e7b952ec00fecb`, task branch `task01-benchmark-draft`.
- Scene/bridge/session hashes match the software-delivery metadata. Benchmark, SG, C++ handoff, readback, launch and driver binary hashes are unchanged. No source/build/config/physics/control modification or new test run.
- Process inspection found no running Isaac/Kit GUI (excluding the inspection command itself).
- Listening-socket inspection found no existing local executor at `127.0.0.1:8226`, the endpoint documented in the predecessor's `docs/operations/ISAACSIM_LOCAL_CONTROL.md`.
- This is a **missing prerequisite**, not an observed native crash, scene/bridge failure, collision, readback failure or failed physical attempt. No GUI connection or loading was attempted.

```ini
TASK01 = PARTIAL
INSERT_READY = NOT_ESTABLISHED
runtime = NOT_STARTED_GUI_PREREQUISITE_MISSING
existing_GUI_physical_attempt_used = 0/1
scientific_simulation_step_and_stamp = UNAVAILABLE_NOT_RUN
```

Do not replace the missing GUI with a standalone harness or consume the one physical attempt by blind launch. Wait for the operator to open a normal GUI and enable the existing executor. This does not authorize a second allowance or any source repair.

## Operator prerequisite (not executed by agent)

Open Isaac Sim normally. Once its GUI has fully started, in Script Editor enable the **existing** local execution extension as documented in the predecessor project:

```python
import carb
import omni.kit.app

settings = carb.settings.get_settings()
settings.set("/exts/isaacsim.code_editor.vscode/host", "127.0.0.1")
settings.set("/exts/isaacsim.code_editor.vscode/port", 8226)
omni.kit.app.get_app().get_extension_manager().set_extension_enabled_immediate(
    "isaacsim.code_editor.vscode", True
)
print("[Project] Isaac local executor ready at 127.0.0.1:8226")
```

This extension setup is not a new simulator/controller/probe. The agent has not executed it. Then report GUI ready; the already-approved sole attempt can follow `Stop → current scene → scene ready → operator Play → current bridge → PRE_PUSH_SHARED saved → unchanged external driver`. Full reviewed loading commands remain in [bbe9784 delivery](TASK01_EXISTING_GUI_LIFECYCLE_ADAPTER.md). Do not start the driver early or manually run another experiment while awaiting this attempt.

## POST-TASK REPORT — preflight paused, not physical outcome

```text
Task/status: TASK01 PARTIAL; authorized runtime not started
Minimum sufficient INSERT_READY evidence achieved: no
Completed: source/critical hash and local GUI/executor prerequisite checks
Files changed: documentation and preflight metadata only
Commands run: git/sha256sum/ps/pgrep/ss and instruction/source reads only
Experiment result/key metrics: no native step/time/q/Cube/contact/attachment;
  no scene load, Play, bridge, ROS driver, robot/suction/rail commands
TASK-BLOCKING prerequisite: normally running GUI/executor unavailable locally
DEFERRED: force/wrench TASK10-IS
KNOWN LIMITATION: new GUI route physical behavior remains unverified
LEGACY: standalone startup crash/debug/probe route; not resumed
Attempt budget used: 0/1 new allowance; prior exhausted budgets unchanged
Escalation: prerequisite notification, not new engineering diagnosis/repair
Paper fidelity: ENGINEERING only; no algorithm/benchmark deviation
Records: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK/TASK01
Recommended next step: operator enables existing GUI/executor, then use the
  same authorized attempt; first failure stops, success only candidate capture
Git/source: task01-benchmark-draft; executable source remains bbe9784 unchanged
```
