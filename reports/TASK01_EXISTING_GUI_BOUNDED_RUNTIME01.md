# TASK01 — authorized existing-GUI runtime01: waiting for GUI prerequisite

2026-10-09 (Asia/Shanghai). [ENGINEERING] preflight only.

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
