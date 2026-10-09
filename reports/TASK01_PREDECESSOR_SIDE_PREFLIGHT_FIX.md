# TASK01 — 复用旧侧压整链筛选与 FK 数值生命周期修正

2026-10-09 · ENGINEERING · SOFTWARE PASS / no new simulator experiment

## PRE-TASK REPORT

```text
Task: authorized minimal predecessor Task26 side-preflight fix
Scientific objective: remove identified software defects while preserving foundation geometry
Minimum sufficient evidence: owned FK values/unchanged line-distance arithmetic;
  original Task27 downstream gate compiled for Task26; both targets compile;
  scope/hash checks. These are software evidence, not physical qualification.
Current scope: two approved changes in original task26_truck_box_push_in.cpp
Explicit non-goals: physical rerun, scene/reset/bridge/MoveIt launch, five Cubes;
  geometry/physics/SG/drive/friction/rail/ACM/threshold/IK changes;
  new planner/controller/probe, force/wrench, benchmark freeze
Attempt budget for the current blocker: one evidence-based software correction;
  one bounded build/check cycle, no automatic alternative fix/fallback;
  new physical allowance0, old qualification allowances remain consumed
Preferred method: explicit Eigen::Vector3d return; reuse existing Task27 callback/gate
Fallback method: NONE this turn; stop/report on substantive failure
Stop / escalation condition: compile/scope failure, unintended lifecycle/semantic change;
  no repair-and-rerun or expansion without separately bounded user direction
Files expected to change: isolated predecessor controller; one offline regression test;
  this report, six records, TASK01/README and small software evidence/patch
Validation plan: offline regression on extracted original FK-distance function;
  CMake Task26/Task27 target builds; source diff, pure test and immutable-file hashes
Known ambiguities / risks: old huge deviations cannot be reclassified retrospectively;
  failed raw trajectories unavailable; downstream planning adds existing planning cost;
  nominal precheck does not guarantee later measured-state physical side execution
Need user confirmation: no for these two fixes (user approved previous proposal);
  yes before any new physical/reset experiment
```

## 授权与旧资产证据

用户在只读审计之后回复“可以”，针对已提出的两项最小修正，不解释为重新运行旧资格验证或冻结 foundation 的授权。固定前代基线是 `631b1f65656d025c1bb2173e874192f3fe4d355a`；修正保存在旧仓库隔离分支 `task01-foundation-side-preflight-fix`，不覆盖 `side-suction-palletizing`，不动较新 `task01-runtime-fixes`。

- Task25 文档194–214已有 fraction1/FK离线、5mm门禁及四步长方案；本轮保留。
- Task26 原侧压背挡已拆8段；本轮保留。
- `6289f2b` / Task27 文档250–256已有相同故障与修复：选择 rear 候选时，从该候选 PUSH 末端检查侧压完整链。原 Task26 因宏未启用此筛选；只移动这段已有逻辑的编译边界，不启用整个 TASK27 模式或其布局/容差。
- 原 FK `poseAt` 的 auto 返回 Eigen Block 视图，而局部 RobotState 已销毁；本机 MoveIt/Eigen 头文件证实返回类型。显式返回独立 Vector3d，仅修复数据所有权，不改误差计算。旧 `linkPosition` 也使用独立 Vector3d 返回；不是新的 FK 算法。
- 旧本地日志 `artifacts/task27_repeat_20260926/short_handoff_v2_retry_20260930.log:545–570` 有同名背挡段8被5mm门禁拒绝的记录；该次后续仍失败，不把它当完整PASS。旧文档另有完整物理PASS，但不替代当前资格证据。

## 修改边界与独立复核

1. `poseAt` 增加返回类型 `-> Eigen::Vector3d`，在 RobotState 销毁前完成复制。
2. Task27 inner-specific 筛选仍在 `TASK27_FIVE_CUBE` 内；已有 `side_preflight` 调用及绑定移到共享区，保留 `!isStraightInsertTask(task)`。
3. 原 Task26 lift-only 早退不变；最终后抓位于 rail refresh 后，callback引用最新world；失败恢复原 regrasp Cube；不改实际侧压规划/执行或重复预检。

独立只读代码复核确认 callback赋值早于调用，无新生命周期；Task27内侧/中央件排除与原行为一致。复用的门禁会增加已有 rear 候选规划成本，不能假称速度优化或保证实际运行100%通过。

## 当前结果

软件修正完成；**无新的 Isaac/ROS 控制、planning-only 或物理调用**。TASK01仍PARTIAL，FOUNDATION_SCENE仍NOT_QUALIFIED，未FROZEN。

- 前代修正源码：[5ed0c96](https://github.com/dreamerToTOE/dual-arm-embodied-palletizing/commit/5ed0c967401e5fedb93b938e1c3904f4a4c87600)，已 push 新分支，仅1文件/+7−6；固定原分支未覆盖。现源码不再声称与631b1f字节一致。
- [离线测试](../tests/test_task01_predecessor_reuse_fix.py)：3tests/exit0，使用**从实际修正源码提取的距离函数**和小型RobotState类型替身，以ASAN检查独立数据生命周期、距离算术；静态检查宏边界/回调顺序/constexpr不变。不是实际机器人FK/IK/FCL或物理证明。
- 原Task26 target-only Release build exit0；原Task27目标也编译链接exit0。仅编译，不运行这两个ROS执行器。
- Git相对631b1f diff只含批准的controller1文件；原scene/bridge/YAML哈希不变，描述/模型/ACM/物理等其他受跟踪文件无diff。记录JSON解析及diff whitespace通过，独立只读代码复核无阻塞项。
- 历史巨大偏差可能涉及检查器缺陷、不同rear构型/站位或真正轨迹异常，但原失败轨迹未保存；本轮没有证据判定其唯一根因，不能回写旧失败为PASS或断言物理已修复。

## 验证命令和出处

```bash
# reproduction repo：离线测试，不启动Isaac/ROS
python3 tests/test_task01_predecessor_reuse_fix.py

# isolated predecessor ros_ws：同一原依赖overlay
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash
export CMAKE_BUILD_PARALLEL_LEVEL=1
export MAKEFLAGS=-j1
colcon build --packages-select fr3_dual_palletize \
  --cmake-target task26_truck_box_push_in --executor sequential \
  --cmake-args -DCMAKE_BUILD_TYPE=Release
cmake --build build/fr3_dual_palletize \
  --target task27_five_cube_center_insert -- -j1
```

两次构建分别使用300s工程上限，未触发；不是新的物理实验预算或科研时间。Task26原依赖overlay提示保留，未修改依赖来消除提示。完整[软件metadata/哈希](../results/20261009_TASK01_predecessor_side_fix01/metadata.json)、[Task26 build](../results/20261009_TASK01_predecessor_side_fix01/build_task26.log)、[Task27 build](../results/20261009_TASK01_predecessor_side_fix01/build_task27.log)、[测试记录](../results/20261009_TASK01_predecessor_side_fix01/unit_tests.txt)。

## POST-TASK REPORT

```text
Task: authorized Task26 minimal FK/side-selection fix
Status: PARTIAL (software PASS; foundation physical acceptance not achieved)
Scientific objective: preserve foundation while fixing audited software boundaries
Minimum sufficient evidence achieved: yes for software correction; no for foundation
Completed: direct old-asset audit, two-change patch, offline3tests/ASAN,
  originalTask26/Task27 compilation and independent source/scope review
Files changed: isolated predecessor task26_truck_box_push_in.cpp only;
  reproduction regression test/report/six records/TASK01/README/software evidence
Commands run: original-source inspections; source git branch/commit/push;
  python offline unit tests; target-only colcon/CMake builds; hash/diff/JSON checks
Tests / experiment results: tests0 (3PASS); Task26 build0; Task27 build0;
  new Isaac/MoveIt/planning_only/physical experiments NOT_RUN
Key metrics: production1file/+7−6; all constexpr preserved; physicalcommands0
Blockers:
  TASK-BLOCKING: foundation full physical acceptance still unvalidated
  DEFERRED: force/wrench/TASK10-IS
  KNOWN LIMITATION: old failed trajectories unavailable, root trigger unresolved;
    extra existing planning cost; nominal precheck vs actual later state
  LEGACY: custom parity/startup/readback/five-Cube paths not resumed
Attempt budget used: authorized softwarecorrection1; one build/check cycle;
  prior qualificationpreflight1/1/physical1/1 retained; new physicalallowance0
Escalation required: yes before any additional fix or physical trial
Paper fidelity:
  ORIGINAL: no paper algorithm implementation this turn
  ADAPTATION: NONE to paper methods
  ENGINEERING: ownership repair and existing6289f2b candidate-gate reuse
  DEVIATION: no benchmark change; documented authorized predecessor source patch
  EXPERIMENTAL: offline software tests, not physical/algorithm comparison
Records updated: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK: yes
Open risks: patched physical outcome unknown; prior diagnostic numbers not revalidated
Recommended next step: user-scoped fresh GUI lifecycle/preflight/physical qualification;
  stop now, do not reset or issue commands automatically
Git branch / commit / dirty files: predecessor task01-foundation-side-preflight-fix
  /5ed0c967401e5fedb93b938e1c3904f4a4c87600 (published, clean);
  reproduction task01-legacy-scene-foundation records commit in this report history;
  unrelated old untracked artifacts preserved, not staged
```
