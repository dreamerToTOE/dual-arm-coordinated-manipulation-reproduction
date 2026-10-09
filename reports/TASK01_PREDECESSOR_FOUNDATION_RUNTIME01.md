# TASK01 — 原 Task26 第一批两件资格验证：PARTIAL，已停止

2026-10-09 · branch `task01-legacy-scene-foundation` · ENGINEERING

## 结论

```text
TASK01: PARTIAL / STOP_FOR_USER
FOUNDATION_SCENE: NOT_QUALIFIED
Predecessor commit: 631b1f65656d025c1bb2173e874192f3fe4d355a
One-Cube selector: NONE; latest user approved original batch1 two Cubes
Scene load: PASS (existing visible GUI, original scene)
Bridge: PASS (manual Play, original bridge, initial/final callback error counts empty)
MoveIt: STARTED / original launch and model/helper/config verified
Planning-only: PASS / one invocation / exit0
Physical full-chain: FAIL / one invocation / exit1
Final Cube pose / old Task26 acceptance:
  first Cube reached +X deep support; side compaction and final-cell acceptance NOT_COMPLETED
  second Cube NOT_STARTED
Retreat/HOME: NOT_REACHED
Unexpected failures: original FK straight-line gate rejected all full side-compaction candidates
Changes to predecessor behavior: NONE; pinned scene/bridge/controller/geometry/physics/config unchanged
Recommended foundation decision: do not qualify or freeze; await user-scoped next action
```

这是固定旧实现**本次完整链未复现**，不是“旧场景永远不可行”，也不是新 wrapper/selector 失败。未把历史两件 PASS 当作当前 PASS。按 D041 首个实质失败停止，未修复或第二次调用。

## 执行顺序与授权

1. 切换指定分支，重读治理/D041/TASK01；主代理直接完整审计旧 Task26 必读文件，独立只读复核。
2. 用户接受两件，选择原 `max_batches=1`，零 selector/count/loop 补丁；原 scene 四件刚体、仅批1两件 active。
3. **先提交并 push 审计 `bb18099`**，才运行；审计入口见 [PREDECESSOR FOUNDATION AUDIT](TASK01_PREDECESSOR_FOUNDATION_AUDIT.md)。
4. 隔离旧 worktree HEAD631b1f，原 CMake Task26 target Release build exit0；依赖包实际 launch/URDF/L tool/SRDF/kinematics/helpers/push YAML 均逐文件 `cmp` 与 pin 相同。直接运行新构建原二进制，不误用较新已装 controller。
5. 已正常启动 GUI PID39508，操作者 Stop→File New；原 scene ready→操作者手动 Play→原 bridge→原 MoveIt。未启动 standalone/headless/SimulationApp，未加载 reproduction TASK01 scene/bridge/handoff。
6. 原 planning-only 唯一调用 exit0；原物理两件唯一调用 exit1。工程 timeout 600/1200s 均未触发。物理日志区间约221.22s 是原 ROS/工程运行时间，不作为 post-physics 科研时间或效率 benchmark。

## 预检证据

[planning_only.log](../results/20261009_TASK01_predecessor_foundation01/planning_only.log) 第419/816行分别 deep/shallow PASS，第828行原 batch1/HOME 预检 PASS。没有 joint/suction/feed/rail 命令；但原 PlanningScene 被改写，bridge 自发到料也已发生。

证据局限保留：原 HOME 预检由实际 HOME 起算而非虚拟最终构型；共同抓持 FCL 不包含摘掉的载荷 Cube；预检不模拟 rail 前移；原 shallow 支撑 gap 使用名义 deep X；USD/ROS-clock 反馈不是原子 native post-step 科研测量。没有新增验证系统去填补这些边界。

## 实际完成的前缀

| 原阶段 | 本轮证据 |
|---|---|
| 批1到料 | feed `[2,2,0,0]`；Cube_01/02 位于原 `.500/.350,0,.260`；后两件 z=-5 |
| 对应侧面抓持 | 原 PRE_CLOSE/POST_CLOSE geometry 通过；共同搬运各阶段双 CLOSED |
| 紧协调搬运 | 原 LIFT→X→Y→DESCENT→SHORT_PUSH→DROP 完成；阶段同步 FCL、原真实附件几何检查通过 |
| 双侧释放/安全换位 | 原日志双 OPEN、helper park/pusher lift 完成 |
| 导轨/规划世界 | 原 `.650→.750` 两轨、world shift `+.100`，原重建与其后 FCL 完成 |
| rear regrasp | 原右臂选第6/20合格重抓候选，换位漂移 `1.12 mm`；后杯 CLOSED，开始推进 |
| 16段 +X 推进 | 16/16执行；最后实际 x=1.0993、lag=.68mm；最高监测关节力矩48.56Nm，低于原80Nm保护 |
| 深墙支撑 | 原 `+X support seat`：gap=+.680mm，z_error=.153mm，通过此阶段旧门禁 |
| 侧压/背挡 | 全链预检失败；**没有实际发送 SIDE_HIGH_APPROACH/CONTACT/PRESS 执行动作** |
| 浅位第二件/退出/HOME | 未执行；不能称第一件最终码垛 PASS 或0/2成功可变成1/2 |

## 精确停止原因

失败是 `task26_r0_deep EXECUTION SIDE_COMPACTION` 的原贴线门禁，不是已发生实际碰撞：

- 原侧压候选1–5、7–8的右臂背挡 `SIDE_BACKSTOP_Y_*_SEGMENT_8`，Cartesian fraction=1但 FK 直线偏离超过原 `5 mm` 门限。
- 候选6在更早的左臂 `SIDE_PRESS_6` 即被同门禁拒绝。
- 例：最后候选8/backstop段8，原四种 step 的偏离为 `304.093 / 228.603 / 280.976 / 1037.690 mm`。候选拒绝发生在预检，不能描述成机器人实际走出这些距离或撞墙。
- [physical.log](../results/20261009_TASK01_predecessor_foundation01/physical.log) 第721行：`cannot preflight a safe SIDE_COMPACTION chain`；第722行原安全 abort 明确 `both side suctions are OPEN`；进程 exit1。
- 该日志没有 `FCL collision` / `FCL pair` 报告；不能捏造 exact collision pair，也不据此宣称完整 PhysX 无碰撞证书。

候选池/步长重试均为 pin 中的原有界行为，不是本轮新增尝试。原池耗尽即停止，外部物理 invocation 只有1次。现象与冗余 IK 路径不贴线一致，但**根因尚未隔离**，不自动归咎几何、机器人、LMA参数或版本，也不调epsilon/seed/站位/阈值。

## 停止现场与清理

已保存 [failure_snapshot.json](../results/20261009_TASK01_predecessor_foundation01/failure_snapshot.json)：原 USD pose、实际关节、TCP、rail/SG/feed/bridge错误。只是停止后工程快照，不是原子 post-physics/frozen科研状态。

- Cube_01 停止后中心 `(1.099852324, .061820220, .260000050) m`，尚未侧压到 y=.254。
- Cube_02 仍在原供料 `(.349998832,-.000001499,.259999990)`；另外两件休眠。
- rail measured/target 两侧 `.750`、arrived=true；双 SG OPEN；bridge callback errors `{}`。
- 原物理进程已结束；仅以终端 Ctrl-C 结束本轮 MoveIt launch（exit130），之后原 owned 子进程未见。没有去诊断 cleanup segfault；不称 launch clean exit0。
- 正常 GUI 保留且已 Pause，未 Stop/reset/重抓/回 HOME/再次执行，等待用户审查。

## 证据与不可变性

[provenance](../results/20261009_TASK01_predecessor_foundation01/preflight_provenance.json) / [scene load](../results/20261009_TASK01_predecessor_foundation01/scene_load.log) / [full MoveIt log](../results/20261009_TASK01_predecessor_foundation01/moveit.log) / [full physical log](../results/20261009_TASK01_predecessor_foundation01/physical.log)。

```text
binary SHA256: 80f924f46a9cccc1c87a4cfe0ab6f7ed0552409f0747b3505b577da189a29a6f
physical.log: e2205ecef3cf743c5aed4832d8d6dd47b641109708824bf74128a7ff48ade73f
planning_only.log: ba7da3ee24203bbdddfb4bfe2daf6ba8523b247444e698a3dc9d5a9fa7a2b39f
moveit.log: 9c522c977c5bd16a9d17eac692a772cd44c20c761d010cd816ea2438021fd954
```

固定 worktree 最终 `git status --short` 为空；no predecessor source patch。没有修改 reproduction benchmark、ACM、工具/车厢、mesh、SG/drive/material/physics、IK/FCL门限或计分，也未开 force/wrench、P1–P5、reset repetition 或五 Cube。

记录校验：两个 JSON 解析通过，原代码/二进制与审计 SHA256 一致。原 MoveIt 日志保留5处原生行尾空格以维持原始证据和哈希；除此原始日志外，提交 diff whitespace check 通过。未为格式检查重写运行日志。

## 下一步需用户决定

本轮资格验证预算已用完（planning-only1/1、physical1/1），不再自动重跑。建议若继续，只单独授权对**现有失败构型/日志**做有限的侧压/背挡运动学诊断，先定位原贴线门禁失败，不改变场景或发物理命令；如需修复或重试，再另定范围/预算。当前不选择第二套工具、站位或新控制器，不移植未通过的 foundation，不自行 PASS CANDIDATE/FROZEN。

## POST-TASK REPORT

```text
Task: D041 predecessor Task26 batch1 foundation qualification
Status: PARTIAL / STOP_FOR_USER
Scientific objective: qualify original full predecessor flow as FOUNDATION_SCENE
Minimum sufficient evidence achieved: no (physical full chain failed)
Completed: direct source audit, provenance/build, original GUI lifecycle,
  one preflight, one physical prefix, negative evidence and safe stop
Files changed: reports/TASK01_PREDECESSOR_FOUNDATION_RUNTIME01.md;
  docs/{STATUS,WORKLOG,EXPERIMENT_LOG,BUGS,DECISIONS,USER_FEEDBACK}.md;
  docs/tasks/TASK01_BENCHMARK_FREEZE.md; README.md;
  results/20261009_TASK01_predecessor_foundation01/{preflight_provenance.json,
    failure_snapshot.json,physical.log,moveit.log}
  Predecessor/runtime/benchmark source changes: NONE
Commands run: original scene/bridge via existing GUI executor/manual Play;
  original target-only colcon build; original MoveIt launch;
  pinned original binary planning_only/max_batches=1 then physical/max_batches=1;
  read-only log/hash/source/process checks; normal GUI Pause/ROS Ctrl-C;
  documentation/evidence commit and branch push
Tests / experiment results: build0; preflight0; physical1; launch interruption130
Key metrics: first deep-seat gap+.680mm; 16 push slices; peak monitored48.56Nm;
  rejected candidate8 FK deviations304.093/228.603/280.976/1037.690mm
Blockers:
  TASK-BLOCKING: original side-compaction FK gate; full qualification incomplete
  DEFERRED: force/wrench/TASK10-IS
  KNOWN LIMITATION: carried-Cube FCL omission; nominal shallow support;
    legacy USD/clock feedback; no continuous collision/native attachment proof
  LEGACY: superseded reproduction parity/startup/readback/five-Cube routes
Attempt budget used: planning-only1/1; physical1/1; no external rerun
Escalation required: yes (new diagnostic/repair/runtime scope requires user decision)
Paper fidelity:
  ORIGINAL: no paper algorithm implemented or validated this turn
  ADAPTATION: none to predecessor runtime; original batch-count parameter only
  ENGINEERING: pinned predecessor foundation qualification and evidence capture
  DEVIATION: none to its behavior/acceptance; two-Cube count explicitly approved
  EXPERIMENTAL: one failed qualification, not formal P1–P5 comparison
Records updated:
  STATUS: updated; WORKLOG: updated; EXPERIMENT_LOG: updated;
  BUGS: updated; DECISIONS: updated; USER_FEEDBACK: updated
Open risks: unresolved FK failure cause and incomplete physical qualification
Recommended next step: wait for bounded existing-evidence diagnosis approval;
  no automatic fix/retry/port/freeze
Git branch / commit / dirty files:
  task01-legacy-scene-foundation; runtime source pin631b1f;
  audit publishedbb18099, preflight evidence54d71ac/321b3dd;
  final records commit identifiable by this report's git history;
  pre-existing unrelated untracked evidence preserved, not staged
```

实际完整启动命令、环境和使用的原文件入口见[运行前审计](TASK01_PREDECESSOR_FOUNDATION_AUDIT.md)及本轮 provenance；未为了结案再运行这些命令。
