# TASK01 — One authorized visible startup native-stack capture

2026-10-09 (Asia/Shanghai). COMPLETE / runtime allowance1/1 consumed; STOP FOR USER.
TASK01 PARTIAL / not FROZEN. This is startup diagnosis, not handoff execution.

## PRE-TASK REPORT

```text
Task: TASK01 startup-only native debugger capture
Scientific objective: obtain causal engineering evidence before proposing a fix
Minimum sufficient evidence: first intercepted fatal native signal's stack/module,
  correlated with precise startup progress; otherwise barrier/timeout result
Current scope: one visible GUI under GDB, ≤180s whole process bound, unchanged
  original harness prefix with independent launcher-level pre-control stop
Explicit non-goals: handoff/regrasp/rail/physics control/robot/suction command,
  changes to benchmark/model/tool/walls/ACM/physics/IK/FCL/thresholds, repairs,
  repeat runs, full core dumps, force, parity10, five-Cube or model-equivalence work
Attempt budget: newly approved one debugger invocation1/1; all prior allowances
  remain consumed; no automatic retry or additional instrumentation variant
Preferred method: native GDB stop+backtrace, original SDK environment for inferior
Fallback method: no new runtime; report reached stop barrier or timeout as evidence
Stop/escalation condition: first fatal signal, pre-control barrier, launch error,
  or 180s hard cap; preserve evidence and stop, no continue/repair/further run
Files expected to change: diagnostic launcher/GDB shell+command file/pure tests,
  this report/run metadata/selected stack and six records; original inputs unchanged
Validation plan: pure AST/line-trace guard tests, shell syntax, independent scope
  and environment review/hashes; exactly one visible capture, then offline audit
Known ambiguities/risks: debugger timing may alter an async startup race; a signal
  intercepted before handlers does not by itself prove original fatal cause;
  original SDK startup updates are not a zero-physics-step certificate
Need user confirmation: no for this explicit one-run capture; yes for any fix,
  complete handoff run, extra capture or benchmark alteration
```

## Safety and fidelity

[ENGINEERING] The original GUI SHA539615dc… remains byte-identical. A thin launcher
checks that hash, identifies its existing main AST and stops before the call
`ns['_apply_official_joint_limits']()` (currently125), before tool/world/cube
construction and far before169 `timeline.play()`, explicit simulate/fetch, prim
restoration, SG commands and MoveIt launch. It records flushed line milestones.
At the barrier it exits directly without native shutdown updates, rather than
allowing original finally/cleanup to dispatch work. This is a diagnostic cut-off,
not a benchmark or reset state. No time/pose/collision claim is derived from it.

Only the inferior receives Isaac library/Python paths and libcarb preload; GDB's
own Python/library environment stays clean. Existing SDK environment setup is
sourced, no system package/driver/cache/core-handler modification. Backtraces omit
function arguments; no full environment, locals, heaps or core dump published.

## Outcome

Preflight: pure launcher tests PASS (5 cases), shell syntax PASS. Independent
read-only guard and SDK/GDB-environment review PASS; no inferior was started by
tests/review. Exact125 normal barrier exits42; early exceptional flow beyond125
exits43 without cleanup. Only the original main Python frame is traced; native
threads remain active and debugger/trace timing can change a race.

The actual single invocation must be wrapped with `timeout --signal=KILL 180s`
(not `--foreground`), followed by owned-process cleanup audit. At preparation,
no Isaac/MoveIt process exists and DISPLAY`:1` has an X socket. All eight original
input/config/driver hashes match their pre-diagnosis values.

**Native startup stack captured; no fix or retry. TASK01 remains PARTIAL.**
Source frozen before run: `944422dc92e7a8f39f0e8c8066147073ba0745f0`.
One DISPLAY`:1` invocation under the stated180s external cap. Log-file creation
09:26:15.103→last write09:28:04.766+08:00 (~109.663s engineering interval), before
cap. These file/wall/profile times are not post-physics timestamps.

The inferior PID17071 stopped on the first intercepted **SIGSEGV** in GDB
thread67 / LWP17392, name`tbb.worker`, fault address`0x40`. Program counter
`0x73be3cf418d9` in `libomni.graph.core.plugin.so` (extension2.181.8,
build ID`d001508a46cd3c10a243f688745224fbd4906724`). The native call chain is:

```text
OmniGraph core [unknown stripped symbol]
← OmniGraph image-core [two frames]
← Kit execution-core [two frames]
← TBB worker/scheduler
← pthread / clone3
```

The log also reports `malloc_consolidate(): unaligned fastbin chunk detected`.
The all-thread snapshot shows thread9 / LWP17116 / `carb.tasking5` already in
`pthread_kill → raise → abort → __libc_message`. Thus SIGSEGV is the **first
signal intercepted by this GDB run**, not proven to be the first native failure
or corruption event; concurrent native signal/fatal paths do not establish order.
This is an additional heap-integrity symptom, **not identification of the
corrupting writer, ownership/lifetime error or defective package**. SDK modules
are stripped; top-frame function names and their arguments are unavailable.
Do not attribute this to Surface Gripper/MoveIt/CUDA, benchmark geometry or a
specific SDK bug solely from the module chain. SDK bridge initialization is not
the same as constructing the project suction bridge or sending commands.

Last flushed original-main milestone is124, immediately before a STOP-timeline
asset/UI `app.update()`;100/106/107/120/122 were positively observed. This narrows
the startup window beyond the earlier buffered console. It does not identify a
particular Python/native causal call. The125 pre-control barrier was not reached
before the first signal. Native SDK workers remain active while timeline isSTOP.

GDB captured the stopped-thread12-frame stack, all-thread short stacks, loaded
modules and fault instructions, then **explicitly killed** the inferior—no signal
delivery/continue, no automatic relaunch. Wrapper exit0 means capture commands
completed, **not Isaac/benchmark PASS**. No full core dump, locals, environment or
arbitrary memory inspection was published. Owned timeout/GDB/inferior PIDs
17037/17038/17071 and PGIDs17037/17071 are absent; matching Isaac/MoveIt processes
absent. No user scene/data deletion occurred.

## Evidence and scientific limits

- [Full capture log](../results/20261009_TASK01_startup_native_stack01/launch.log)
  SHA`0f19358bfed0da51621fb468822e4907104ea369d03c3f41ca6127bd380a2f4b`.
- [Run metadata](../results/20261009_TASK01_startup_native_stack01/metadata.json),
  [last launcher marker](../results/20261009_TASK01_startup_native_stack01/startup_guard.json),
  [original harness inputs](../results/20261009_TASK01_startup_native_stack01/raw/inputs.json).
- SDK Kit log`kit_20261009_092619.log` independently confirms startup complete
  at95.047s, SDK ROS bridge started99.092s, SG enable request99.825s and World1
  layer initialization100.107s. These are app-relative diagnostic times only.
- ELF `.text` address0x41ed0 and GDB loaded-text0x73be3ce41ed0 imply load bias
  0x73be3ce00000; current fault module-relative PC0x1418d9. The prior retry02
  kernel PC minus its recorded module base is also0x1418d9/address0x40. This is
  consistent fault-site evidence across runs, **not proof of the same root cause**.
- All eight original hashes were checked after run and remain unchanged.
  Changes are diagnostic launchers/tests and records/evidence only.

No `timeline.play()`, project bridge construction, robot/joint/suction/rail
command, MoveIt launch, world refresh/readback, handoff, rear regrasp, READY/reset
or TARGET execution took place in the controlled original-main prefix. No new
q/TCP/Cube/contact/collision/simulation-step safety or stability evidence exists.
This is **not** the critical-state safety fallback or a TASK01 acceptance run.

## Disposition / escalation

Native-stack evidence objective met; actual startup defect remains unresolved and
TASK-BLOCKING for physical INSERT_READY. Readback repair remains softwarePASS /
runtimeUNVERIFIED. `TASK01 = PARTIAL`, `INSERT_READY = NOT_ESTABLISHED`, noFROZEN.
New allowance1/1 exhausted; all prior allowances remain consumed. Stop now; no
startup repair, extra capture, new probe, collision/physics change or integration
rerun without a separately bounded user decision. BUG001 stays TASK10-IS; no
force/wrench, P2/P3, five-Cube or benchmark redesign was added.
