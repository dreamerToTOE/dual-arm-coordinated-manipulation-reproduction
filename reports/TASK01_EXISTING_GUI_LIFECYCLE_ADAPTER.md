# TASK01 — reuse Task26 existing-GUI scene → Play → bridge lifecycle

2026-10-09 (Asia/Shanghai). [ENGINEERING]. Software delivery; TASK01 PARTIAL, not FROZEN.

## PRE-TASK REPORT

```text
Task: TASK01 single-Cube existing-GUI scene/handoff adapter only
Scientific objective: unblock the existing benchmark integration lifecycle;
  no new geometry/controller/safety acceptance claimed this iteration
Minimum sufficient evidence: deterministic source reuse + pure lifecycle gates;
  preserve benchmark and control/SG/rail/FCL/readback implementations and hashes
Current scope: scene.py in stopped already-running GUI → user Play → bridge.py
  registers existing pre/post-physics callbacks, no standalone SimulationApp
Explicit non-goals: benchmark/algorithm/tool/wall/ACM/physics/threshold changes,
  image-core investigation, new probes, physical execution, TARGET/force/reset
Attempt budget: one adapter implementation and pure checks; new Isaac runs0;
  prior consumed runtime/debug budgets are not replenished
Preferred method: old Task26@631b1f lifecycle; retain current thin reuse adapters
Fallback method: none this iteration; stop/report any new substantive blocker
Stop/escalation condition: lifecycle guard/test failure, geometry/control drift,
  need for physical execution beyond this implementation request
Files expected to change: TASK01 GUI adapter + scene/bridge editor entrypoints,
  pure tests, this report and six persistent records/current task
Validation plan: AST/mocked lifecycle tests, syntax and immutable hash checks;
  no simulator/ROS/robot/suction/rail command, no acceptance run this iteration
Known ambiguities/risks: GUI attachment not yet tested physically; normal manual
  Play has unscored startup steps; scientific samples remain native post-step;
  current standalone crash retained as history, not repaired or explained
Need user confirmation: no for this explicit adapter change; yes for new runtime
```

## Reuse provenance

User-requested branch checked remotely with git ls-remote:
`side-suction-palletizing = 631b1f65656d025c1bb2173e874192f3fe4d355a`.
Read its `docs/tasks/TASK26_TRUCK_BOX_PUSH_IN.md`, scene and bridge source using
the matching local Git object (web tree fetch was unavailable). The original
scene uses current Stage and stopped Timeline; bridge initializes live handles
after user Play and registers a retained callback object. No old full scene or
bridge is executed: that would import feed/five-Cube/material/effort settings.

Current constructor allowlist, `reused_bridge.py`, C++ handoff, composed-world
readback validator and benchmark remain the scientific/runtime authority. Only
app ownership and scheduling are adapted. No new Surface Gripper, rear grasp,
push/controller or image-core diagnostic route is introduced.

## Implementation and limits

New adapter files under `platforms/isaac_ros2/handoff/`, plus the separate pure test:

- `task01_existing_gui_scene.py`: Script Editor entry for current stopped Stage.
- `task01_existing_gui_bridge.py`: separate entry after manual Play; no automatic driver launch.
- `task01_existing_gui_session.py`: thin lifecycle adapter around existing constructors, SG and native sampler. Retained in `builtins`, asynchronous rather than a blocking Script Editor loop.
- `tests/test_task01_existing_gui_session.py`: stdlib-only AST/mock lifecycle checks.

The scene loader refuses PAUSE, a live previous adapter, changed benchmark/source/asset hashes, and unrelated physics/Graph prims. It rebuilds only the current benchmark's exact named roots. It does not create a SimulationApp, clear/create another Stage, Play, manually step physics or close the GUI. Manual Play may produce unscored initialization steps before the bridge loads. It is not a scientific READY sample.

The bridge checks the same Stage/token/config and an initialized physics view before restoring the **already recorded PRE_PUSH** state, exactly as the existing handoff harness does. This adapter does not replace Benchmark A START or generate new IK. It uses unchanged `build_bridge()` and the unchanged C++ handoff. Native pre-step order0 and post-step order200 replace manual `simulate/fetch`; GUI update awaits are scheduling only. The original `on_post_step` sampler/record/capture function is AST-identical. Stage/token/Play is also checked in each callback before physical writes. Failure notifies the external driver through its existing `halted/error` fields with the last real native step/time, never a fabricated timestamp.

Default loading does not spawn MoveIt/controller: an operator launches the unchanged driver separately, matching old Task26. The optional existing owned-launch path has only an explicit absolute readback evidence directory added to its command. No C++ protocol/algorithm change.

The adapter has a **cooperative <=180-second engineering deadline** while Kit callbacks continue servicing; it is not an OS hard cap against native GUI hangs. It owns callbacks/its ROS bridge, not the host GUI or an external terminal's processes. Driver disappearance from the ROS graph after it was actually observed is cleanup evidence, not a known zero exit code; external exit code is recorded `NOT_OBSERVED`. Read the terminal's exit/log too. On failure, stop the external launch with Ctrl+C. On normal/cancel/error cleanup, the GUI is paused and the unchanged SG shutdown opens the grippers. The paused final view is therefore **not a stable held READY state** or proof of reset repeatability.

No new simulator/ROS/controller/GDB run was performed this iteration. No new native samples, physics contacts, raw live CollisionObjects, rail movement, rear attachment or INSERT_READY evidence exist. Old native startup failure is preserved as historical standalone-route evidence, not declared repaired. Old diagnostic/probe/runtime budgets remain exhausted; no fallback or further image-core work is introduced.

## Complete loading sequence (for a separately approved runtime)

The commands below are delivery instructions, **not commands executed this iteration**. Use an already normally started visible Isaac GUI and a clean Stage, or a stopped current TASK01 Stage with only its expected named assets. Stop other controllers; do not launch a second `move_group` over an existing controller session.

### 1. Existing Isaac GUI: Stop, then load scene

Click **Stop**, not Pause. In Script Editor:

```python
exec(open("/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/platforms/isaac_ros2/handoff/task01_existing_gui_scene.py").read())
```

Expected console: `TASK01 single-Cube scene ready in existing GUI`. Only the current single Cube, two FR3/current L-tools, carriage and table are loaded; no five-Cube/feed wrapper. A rejected foreign asset must be reviewed, not automatically deleted or ignored.

### 2. Manually Play, then load bridge

Click **Play**, allow normal physics initialization. Then in Script Editor:

```python
exec(open("/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/platforms/isaac_ros2/handoff/task01_existing_gui_bridge.py").read())
```

**This bridge entry is not read-only**: it restores recorded PRE_PUSH q/Cube and establishes the existing supported bilateral hold. It prints a unique absolute output directory and, on successful initialization, `TASK01 PRE_PUSH_SHARED sample saved; run the existing handoff driver in the ROS terminal.` Start the terminal driver only after that message. Rejected/failed initialization is a STOP, not a reason to rerun automatically.

### 3. External ROS terminal: unchanged fixed handoff

Use the same `ROS_DOMAIN_ID`/DDS/network environment as the already-running GUI. Do not add different ROS-localhost/domain settings in only one process. Paste the **actual absolute output directory printed by the bridge** when prompted:

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash

read -r -p '粘贴 GUI 打印的完整 output 目录: ' TASK01_RUN_DIR
if [[ "$TASK01_RUN_DIR" = /* && -f "$TASK01_RUN_DIR/pre_push_shared_sample.json" ]]; then
  ros2 launch /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/platforms/isaac_ros2/handoff/moveit_handoff.launch.py \
    benchmark_config:=/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/configs/benchmark/benchmark_v1.yaml \
    driver:=/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction/build/task01_handoff/task01_rear_handoff \
    readback_evidence_dir:="$TASK01_RUN_DIR/planning_world_readback"
else
  printf '%s\n' 'STOP: 必须使用本次 GUI 已保存 PRE_PUSH_SHARED 的绝对 output 目录。'
fi
```

The mandatory absolute `readback_evidence_dir` is provided explicitly: no unlogged readback or stale prior run directory. This unchanged driver performs only bilateral OPEN → original safe transition → rails .650/.650 to .750/.750 → fresh planning world +.100 → rear regrasp → INSERT_READY capture. **No TARGET push, no reset repeats, no five Cube or force work.** Its existing guard failures stop the task; do not relaunch or change geometry/parameters to bypass them.

### 4. Stop / inspection

On failure or operator stop: Ctrl+C the external terminal launch, then in Script Editor:

```python
from task01_existing_gui_session import stop_bridge
stop_bridge()
```

This cancels the adapter and pauses the existing GUI; it does not kill an externally owned controller, close/restart Isaac or automatically rebuild the scene. Await its cleanup message/task completion before another deliberate operator action. Do not use the historical standalone launcher/debugger for this lifecycle.

Inspect this run's `inputs.json`, `scene_audit.json`, `pre_push_shared_sample.json`, `post_step_states.jsonl`, `post_step_contacts.jsonl`, raw `planning_world_readback/`, and either `failure.json` or `insert_ready_candidate.json` plus `summary.json`. They are future runtime outputs, not supplied physical evidence in this software delivery. Native post-physics `physics_step` / `simulation_stamp_ns` remain the scientific clock. A saved candidate still requires user review; no auto-FROZEN.

## Pure verification (completed)

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
python3 -m unittest discover -s tests -p test_task01_existing_gui_session.py -v
python3 -m unittest discover -s tests -p test_task01_startup_debug_launcher.py -v
python3 -m py_compile \
  platforms/isaac_ros2/handoff/task01_existing_gui_session.py \
  platforms/isaac_ros2/handoff/task01_existing_gui_scene.py \
  platforms/isaac_ros2/handoff/task01_existing_gui_bridge.py \
  tests/test_task01_existing_gui_session.py
git diff --check
```

Results: **33 new lifecycle tests PASS**, **5 historical guard regression tests PASS**, syntax PASS, diff whitespace PASS. The historical guard tests are pure source checks, not another debugger run. Two independent review passes confirmed Task26 lifecycle reuse and immutable inputs. Test scope is mock/AST, not SDK execution or physical safety. Development-only initial indentation error was corrected before final syntax/tests; no physical retry occurred. [Machine-readable software record/source hashes](../results/20261009_TASK01_existing_gui_adapter01/metadata.json).

### Unchanged SHA256 inputs

| Input | SHA256 |
| --- | --- |
| `configs/benchmark/benchmark_v1.yaml` | `25b7162c848b4cfeeff7e07a8cd154f26dff215c6d8f3d1caf8cf6333bcc8783` |
| original `task01_insert_ready_gui.py` | `539615dc789460abc2e3b0b2e7c09dff8c7ad00b8dc74327f1e8d114a0a1a77c` |
| `reused_bridge.py` | `e4c1dc8bea2098d315d2404bdbd0b5c986ca46df4ac9a7facca123a4e5dabae1` |
| `task26_reused_primitives.hpp` | `2051c84b9275e5bf1d286dcfd02b441e32a490e7b0b120757068878425d45cb1` |
| `task01_rear_handoff.cpp` | `e8ed058e58e63eb7f0a36bd02daa25151e62d81867d0bc52754192a9375f909a` |
| `collision_readback.hpp` | `6ab64d3fa680a92957d24198a2f2c895ce4c026559414112e92ba386949ec030` |
| `moveit_handoff.launch.py` | `4c707922986112f9d667d3ba212191c0099bcdb94a010050168361438a7f3f47` |
| existing driver binary | `86237ffa76d3e2585bd475a06796f98bf49bf3ca34c6bae24e82c835a0bd5325` |

## POST-TASK REPORT

```text
Task: current TASK01 existing-GUI lifecycle adapter [ENGINEERING]
Completed: thin current-Stage scene/manual-Play/native-callback bridge entries;
  unchanged external driver; guards/ownership/stop/evidence instructions
Scientific evidence added: NONE; physical runtime NOT_RUN
Verification: 33 adapter + 5 historical pure tests PASS; syntax/hash/review PASS
Attempts: one software implementation iteration; new simulator/control runs0;
  all prior physical/probe/debug budgets still consumed
Changed: new adapter/entries/pure tests + report/README/persistent records
Unchanged: eight approved inputs; benchmark/tool/carriage/ACM/physics/IK/FCL;
  SG/rails/readback/C++ control; no image-core research, no new probe
Remaining: actual new-route readback/handoff/rear attachment/INSERT_READY,
  benchmark safety/reset acceptance; no runtime conclusion claimed
Risks: native GUI hang not covered by cooperative cap; external process owned
  by terminal; candidate capture != exitcode0; cleanup opens SG != held READY
Status: TASK01 PARTIAL / DRAFT; INSERT_READY NOT_ESTABLISHED; not FROZEN
Next: STOP implementation here; user-reviewed separately bounded GUI runtime
```
