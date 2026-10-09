# TASK01 — Bounded read-only startup crash diagnosis

2026-10-08 (Asia/Shanghai), source checkpoint407bd34. **Read-only diagnosis
complete1/1; native module clue identified, exact root cause unresolved.**
TASK01 PARTIAL / INSERT_READY NOT_ESTABLISHED / not FROZEN. No new Isaac/ROS run.

2026-10-09 (Asia/Shanghai): resumed record finalization/publication after the user
said “继续”. The evidence/diagnosis above belongs to2026-10-08; no new diagnostic,
simulator or debugger invocation occurred during finalization. Existing exhausted
allowances were not reopened.

## PRE-TASK REPORT

```text
Task: TASK01 native startup crash, read-only diagnosis
Scientific objective: identify the engineering blocker preventing actual INSERT_READY
Minimum sufficient evidence: existing crash stack/module/call site if available;
  otherwise an explicit evidence gap and narrowly scoped next diagnostic request
Current scope: read existing two crash logs, previous successful startup prefix,
  existing core/apport/Kit crash artifacts and source/SDK call chain
Explicit non-goals: fixes, source/config/binary changes, imports that start Isaac,
  live debugger/inferior, new simulator/ROS run, commands, benchmark/physics/ACM
  changes, controller/force/suction work, new parity/probe or five-Cube flow
Attempt budget: one diagnosis iteration1/1, at most10min; no live runtime allowance
Preferred method: already captured native stack/core and existing SDK logs
Fallback method: source/log boundary analysis only; no crash recreation authorized
Stop/escalation condition: evidence sufficient, no available stack/core, or time cap;
  no speculative repair/relaunch, request separate authority if more evidence needed
Files expected to change: report and six persistent records/TASK01 links only
Validation plan: read-only source/evidence checks; document confirmed versus inferred;
  verify runtime/config hashes unchanged; offline record audit and Git branch push
Known ambiguities/risks: SIGSEGV log has no usable Python stack; shell core-dump
  message alone does not prove a retained accessible core; startup symptom need not
  establish a shared root cause between attempts
Need user confirmation: no for the agreed diagnosis; yes for any new run or fix
```

All previous runtime budgets remain consumed. Wall time here is a diagnostic
resource cap, not a scientific simulation timestamp. Existing records are retained.

## Findings — confirmed versus inferred

### 1. The previous stdout-only execution boundary was incomplete

Full Kit logs contain positive markers beyond `app ready`:

| Marker | retry01 Kit line / app-relative time | retry02 Kit line / app-relative time |
| --- | --- | --- |
| Simulation App Startup Complete | 5420 / 10.589s | 5404 / 81.426s |
| isaacsim.ros2.bridge started | 7204 / 10.765s | 7188 / 83.685s |
| Surface Gripper enable request | 7210 / 10.810s | 7194 / 83.915s |
| World1 USD/session layer load | 8985–8986 / 10.971s | 8969–8970 / 84.176s |

Thus `SimulationApp` initialization completed and SDK ROS2 bridge enabled before
the crashes. **This is not a MoveIt/driver startup:** no MoveIt driver/log/refresh
exists in either run. Prior statements that the crash was after `app ready` remain
true for the captured console, but `app ready` is not the final actual call boundary.
Stdout buffering/truncation explains why the complete Kit log is more informative;
we do not infer execution limits solely from absent stdout prints.

The GUI source [task01_insert_ready_gui.py](../platforms/isaac_ros2/handoff/task01_insert_ready_gui.py)
places `SimulationApp` at88, ROS2 bridge enable at100, Surface Gripper enable at106,
new stage at107, stage/physics/FR3 references at108–122, and asset/UI updates
at123–124. **Inference/investigation window:** early new-stage/asset initialization
around107–124. This is not an exact fault call or a rigorously established upper
execution bound. Missing `_apply_official_joint_limits()` stdout cannot prove125
was not reached, particularly given buffering. The actual physical/control stream
and handoff have no execution evidence.

The earlier successful prefix `kit_20261008_202948.log` passes these markers and
continues to FR3 materials/joint-limit/SG activity. The same source path has worked;
this does not prove current native async/render/stage behavior is deterministic.

### 2. Strongest native clue: same-time OmniGraph worker crash

Existing kernel journal, rendered in Asia/Shanghai, records:

```text
2026-10-08T21:31:44+0800 ... kernel:
tbb.worker[12295]: segfault at 40
ip 00007ae437f418d9 sp 00007ae4b6bfc740 error 4
in libomni.graph.core.plugin.so[7ae437e00000+313000]
```

Apport records retry02 parent11986 receiving SIG11 at the same second. This is
a concrete **native module/fault-address clue**, correlated with retry02, not a
full native stack or retained parent/thread mapping. It supports investigating
OmniGraph's worker/stage lifecycle, **not** declaring an OmniGraph bug, null-pointer
root cause, ROS bridge/SG/CUDA/driver incompatibility, or geometric collision.
Retry01 has no equivalent retained kernel/module record in the audited evidence;
do not assert both runs have a proven common root.

### 3. Why there is no saved core to inspect

The kernel core handler points to Apport, not an ordinary `core` file. Exact prior
PIDs appear in `/var/log/apport.log`:

```text
PID398623: signal11, core limit0; bundled python executable does not belong to a package, ignoring
PID11986:  signal11, core limit0; bundled python executable does not belong to a package, ignoring
```

No corresponding report in `/var/crash`, no systemd core in
`/var/lib/systemd/coredump`, and no matching new Kit dump were found; `coredumpctl`
is not installed. The shell's “core dumped” message is **not evidence that a
usable core was persisted**. GDB is installed but was not executed, as there
was no existing matching core. No core extraction, package install, global handler
or limit change, live debugger, new process crash, simulator or command ran.

### 4. Evidence retained and diagnostic stop

[Selected verbatim existing evidence](evidence/TASK01_STARTUP_EXISTING_LOG_EXCERPT.log)
contains only the two Kit marker sets, the exact two Apport records and the kernel
line. Unrelated applications/environment/core contents are not published.
[Diagnostic metadata](../results/20261008_TASK01_startup_readonly01/metadata.json)
records provenance and hashes. Full Kit logs remain local; original console/input
logs from retry01/02 remain separately tracked. No negative history is overwritten.

The one read-only diagnosis is now stopped. **No source/config/binary changed; no
new physical evidence or successful fix.** Do not reopen any prior runtime budget.
TASK01 remains PARTIAL; exact startup root and live readback/INSERT_READY remain
unverified. BUG001/force stays TASK10-IS; model equivalence remains a known
limitation, not an exhaustive diagnostic requirement; five-Cube Task27 is legacy.

## ENGINEERING ESCALATION

```text
Scientific question: remove the startup blocker to obtain actual INSERT_READY evidence.
What is already established: complete SDK initialization/ROS bridge positive
  markers; same-time retry02 kernel fault in OmniGraph core; Apport ignored cores.
What remains unknown: complete native/Python stack, exact faulting call and cause;
  live readback/handoff acceptance.
Why the remaining unknown matters: cannot justify a narrowly correct fix from
  last-log ordering or a native library name alone.
Attempts made: one newly approved read-only diagnosis1/1; zero new runtime/debug
  runs and zero fixes. Prior physical allowances remain consumed.
Root blocker classification: TASK-BLOCKING native startup/early-stage failure;
  module clue known, causal defect unresolved.
Is it still task-critical: yes for actual Isaac acceptance.
Lower-cost evidence available: existing logs/kernel/Apport/source; no matching core.
Recommended action: request a separately bounded visible startup-only native-stack
  capture, stopping before physics/handoff/robot/suction commands; no benchmark edit.
Need user decision: approve that diagnostic runtime and its explicit budget/cap;
  no authorization to repair or retry the complete handoff is inferred now.
```

## POST-TASK REPORT

```text
Task: TASK01 / read-only native startup diagnosis
Status: PARTIAL; diagnosis completed, exact root unresolved, TASK01 not FROZEN
Scientific objective: identify startup blocker preventing actual INSERT_READY.
Minimum sufficient evidence achieved: module/evidence-gap diagnostic target yes;
  causal fix or scientific benchmark acceptance no.
Completed: existing console/Kit/kernel/Apport/core inventory/source audit;
  precise markers, module clue and unsaved-core explanation; records/provenance.
Files changed: report/selected log/diagnostic metadata, six records and TASK01 link.
Commands run: read-only rg/sed/nl/sha/journal/core inventory/Git checks; offline
  record consistency and branch publication. No simulator/debugger/ROS/test run.
Tests / experiment results: no new experiment; prior input hashes unchanged.
Key metrics: diagnosis1/1; new runtime0; fixes0; available matching cores0;
  new scientific step/time/q/Cube/TCP/rail/contact/readback/READY evidence absent.
TASK-BLOCKING: exact startup native root and live INSERT_READY acceptance unknown.
DEFERRED: BUG001/wrench TASK10-IS, prior shutdown fault.
KNOWN LIMITATION: full model equivalence not required/established.
LEGACY: five-Cube Task27, no execution.
Attempt budget used: one read-only diagnosis1/1; all prior budgets unchanged.
Escalation required: yes, before any new live diagnostic capture/fix/handoff run.
Paper fidelity: ORIGINAL/ADAPTATION unchanged; ENGINEERING records/diagnosis only;
  no DEVIATION or EXPERIMENTAL benchmark/controller alteration.
Records updated: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK/TASK01.
Open risks: module clue is not root cause; asynchronous call site unspecified.
Recommended next step: user decision on bounded startup-only native-stack capture.
Git: task01-benchmark-draft, diagnostic source407bd34; record commit follows;
  three pre-existing untracked historical launch logs preserved.
```
