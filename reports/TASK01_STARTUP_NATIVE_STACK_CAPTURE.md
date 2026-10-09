# TASK01 — One authorized visible startup native-stack capture

2026-10-09 (Asia/Shanghai). PREPARING / runtime allowance0/1.
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

Pending the single authorized invocation. No startup fix, scientific acceptance,
collision result or INSERT_READY is presumed.
