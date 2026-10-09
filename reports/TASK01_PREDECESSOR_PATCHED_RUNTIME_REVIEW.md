# TASK01 — 已批准软件修正版的有界 GUI 物理验收

2026-10-09 · ENGINEERING · TASK01 PASS CANDIDATE REVIEW（未 FROZEN）

## 最终结论

```text
TASK01 = PASS CANDIDATE
FOUNDATION_SCENE = PREDECESSOR_TASK26_BATCH1_TWO_CUBES_WITH_AUTHORIZED_SOFTWARE_FIXES
Physical attempts = 2/3 (FAIL, PASS); attempt3 NOT_RUN after full success
Predecessor runtime = 631b1f + explicitly approved two-change commit5ed0c96
Runtime/geometry/physics/gate changes during these attempts = NONE
Benchmark freeze / porting / paper algorithm implementation = NOT_DONE
```

第2次实际完成原 batch1 两件全链及共同 HOME，进程exit0；最低工程资格证据已取得，停止实验，不继续第3次或移植/冻结。第1次失败保留，不宣称三次稳定通过或统计可靠性。本轮两次原 planning-only 都exit0。

## PRE-TASK REPORT

```text
Task: D041 predecessor Task26 batch1 physical qualification with authorized fixes
Scientific objective: verify the mature two-Cube flow can complete as foundation candidate
Minimum sufficient evidence: original preflight PASS, two original physical task PASS,
  wall/cell acceptance and safe retreat/HOME; preserve raw logs and final actual state
Current scope: existing visible GUI, original scene/Play/bridge/MoveIt lifecycle;
  predecessor631b1f + approved two-change commit5ed0c96, original max_batches=1
Explicit non-goals: any additional runtime/source/geometry/physics/ACM/gate change;
  new probe/controller, five Cubes, force/wrench, benchmark redesign or FROZEN
Attempt budget: latest user approves at most3 physical-acceptance attempts;
  each fresh lifecycle, preflight <=600s, physical <=1200s engineering wall caps;
  stop on first full success. Previous runs remain separate historical evidence.
Preferred method: existing GUI executor invokes original assets and direct patched binary
Fallback method: no implementation fallback; unchanged fresh retry for safely rejected planning
Stop / escalation: third unsuccessful attempt; native crash, confirmed unexpected physical
  collision, bridge/state/rail-world/attachment corruption, torque/jam/drift safety fault
  stops immediately rather than repeating a dangerous state. No fix-and-rerun.
Files expected to change: this report, run logs/metadata/snapshots, six persistent records,
  TASK01 status; no production/runtime/benchmark source changes
Validation plan: immutable hashes, fresh original lifecycle, original preflight and physical
  gates, final bridge feedback, original PASS/HOME markers and process cleanup
Known ambiguities/risks: original preflight and carried-Cube FCL coverage limits retained;
  downstream nominal precheck not physical guarantee; USD/ROS-clock feedback not atomic
  post-physics scientific measurement; rail advance is unchanged .100m
Need user confirmation: no; latest user explicitly authorizes runtime up to3 attempts
```

## 授权、现场和固定输入

用户：“继续物理验收，如果三次尝试都失败再反馈给我”。本轮不要求用户再次手动重置；通过现有 GUI 操作原 Stop→scene→Play→bridge 生命周期，保留正常 UI 可见性，不开 standalone/headless。正常重置前先调用旧 bridge 原有 shutdown，避免旧物理订阅/句柄留在被替换 Stage。当前仅有本任务场景，无外部 MoveIt/执行器运行；GUI PID39508/8226 正常响应，双 SG OPEN，rail .750，暂停在旧失败现场。

采用最新软件修正版，不声称 pin 字节完全一致：

- predecessor branch `task01-foundation-side-preflight-fix`, commit `5ed0c967401e5fedb93b938e1c3904f4a4c87600`；
- executable SHA256 `a84cb3ad8734d6a597a81ed33039c732d595029e23a46225c963dfb7069ce992`；
- scene SHA256 `43aa7c2eb6a5667da5e94eaaef347229fe6178ec58d6a10d12dddf14ba2aa9e7`；
- bridge SHA256 `13b5f88d1e7563a37ecafbf571d8ef93015b57059b8912ba9f3399e21e339644`；
- controller SHA256 `8c984cc761b7b4071bfcbc3f01398f30adfa9c43858032f23af551abd752e0f0`。

软件两项修正已完成离线检查与编译，不在本轮再修复。固定 original max_batches=1、execution_time_scale=3.0、ROS_LOCALHOST_ONLY=0。不启用 TASK27，不重新求科研 START，不使用 reproduction scene/bridge/handoff。原两件 active、另外两件 dormant；不是 SINGLE_CUBE。

## 执行状态

| 尝试 | 原预检 | 物理结果 | 真实完成范围 |
|---|---|---|---|
| 1 | exit0 / PASS | exit1 / FAIL | deep全链PASS；shallow右臂外侧下降时左臂保持位到位超时，未双吸附，未共同HOME |
| 2 | exit0 / PASS | exit0 / PASS | deep、shallow均完成实际双侧抓持/搬运/释放/后抓/推进/侧压/退出；实际共同HOME完成 |
| 3 | NOT_RUN | NOT_RUN | 第2次完整成功后按最低充分证据规则停止 |

### 第1次负证据

[raw physical](../results/20261009_TASK01_predecessor_patched_runtime01/physical.log) 第610–611行第一件PASS：cell .993mm、deep gap .152mm、side gap .982mm。第901–902行第二件 `RIGHT_OUTER_DESCENT` 执行后，左臂CONTACT保持位25s到位等待失败，max_error3.931858deg（joint6，原门限未改）。上一行 `RIGHT_CONTACT final command` 是原代码预先打印的outer_descent末点，不能误读为真实CONTACT完成。原wait函数短路后未继续right settle检查；未抓起第二件。

[failure snapshot](../results/20261009_TASK01_predecessor_patched_runtime01/failure_snapshot.json)：暂停后双SG OPEN、rail .750、callbackerrors{}。Cube02仍在供料附近，Y扰动约14mm；有非零关节速度。根因未隔离，日志没有确切unexpected robot collision/torque/jam或句柄失效证据；不把数值残差等同于已证实碰撞，也不称此现场动态稳定。原样fresh重跑由用户新增3次预算覆盖，不修drive/几何/门禁。

### 第2次完整物理证据

[raw physical](../results/20261009_TASK01_predecessor_patched_runtime02/physical.log) 第608/1205/1220行分别记录两件格位门禁和实际整批HOME成功；第1218–1219行实际HOME残差左.059deg、右.062deg。外部前台终端管道采用pipefail，确认物理退出码0，不用tee或launcher退出码代替controller结果。

| 原执行器验收项 | deep / Cube01 | shallow / Cube02 |
|---|---:|---:|
| cell_error | 1.181 mm | 0.376 mm |
| +X深墙 / 同行前件间隙 | +0.297 mm | +0.369 mm（原名义前件支撑算法） |
| +Y墙间隙 | +1.143 mm | +0.070 mm |
| 原16段推进峰值监测关节力矩 | 23.48 Nm | 28.98 Nm |
| 实际每件完整链 | PASS | PASS |

原后抓整链筛选、实际侧压背挡8段均通过原5mm贴线门禁；当前path报告各段约.001mm。这是本次路径上的观察，不证明旧300–1000mm偏差全由生命周期缺陷造成，也不保证所有未来IK分支都可行。原80Nm监督未触发；不是校准后的TCP contact wrench。

### 最终现场和清理

[final snapshot](../results/20261009_TASK01_predecessor_patched_runtime02/final_snapshot.json) 在实际HOME结束后暂停GUI保存，**与每件验收不是同一时刻读数**：

- Cube01 `(1.099999428, .253218740, .259999394) m`；Cube02 `(.979630828, .253930330, .260000020) m`，原USD反馈。
- 两轨 measured/target `.750`、arrived=true；native base分别 `(.750,±.600,≈0)`，原站位一致。
- 双SG OPEN，feed `[2,2,0,0]`，bridge callbackerrors `{}`；原另外两件仍休眠z=-5。
- actual关节/Dof names/TCP/base/Cube/速度在snapshot中完整保存；未作为新的FROZEN START/RESET，不运行reset重复。
- GUI原PID39508保留且Pause，不Stop/重建，不再发robot/rail/SG命令；两轮本轮ownedMoveIt分别Ctrl-C终止exit130，相关子进程复核已退出。没有cleanup调试或后续任务。

快照的legacy timeline time和ROS clock明确分列，**不是原子native post-physics科研状态**；不混用成论文时间序列、held稳定性或reset认证。callbackerrors{}只表示原桥接无异常，不是独立PhysX无碰撞证明。

## 实际命令（两轮各一次）

原GUI生命周期加载已记录在各轮scene/Play/bridge日志中。重建前先旧bridge.shutdown→实际Stop；scene ready后在同一现有GUI Play，再原bridge。未启动headless/SimulationApp/app.update启动循环或reproduction harness。

```bash
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description moveit_dual_side_suction.launch.py use_rviz:=false

timeout --signal=INT --kill-after=15s 600s \
 /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/build/fr3_dual_palletize/task26_truck_box_push_in \
 --ros-args -p planning_only:=true -p max_batches:=1

timeout --signal=INT --kill-after=15s 1200s \
 /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/build/fr3_dual_palletize/task26_truck_box_push_in \
 --ros-args -p max_batches:=1 -p execution_time_scale:=3.0
```

实际以上ROS命令均前台PTY + pipefail/tee保存全日志，工程timeout均未触发。源码/binary/scene/bridge最终SHA256与执行前相同、旧隔离worktree干净；push YAML实际overlay与pin通过cmp。没有再编译或production修正。

## 保留的边界 / 用户下一步审查

1. 第1次第二件实际到位失败仍是未隔离的可复现性风险；第2次成功不抹除负证据。本轮2次包含1次失败，**不是稳定可靠性证明**。
2. 原planning-only不模拟rail前移/物理接触；共同载荷Cube未作为AttachedCollisionObject加入原FCL；原浅位支撑gap用名义前件X；原HOME零命令预检起于实际HOME。保留这些旧工程限制，不新建验收系统或宣称连续碰撞证书。
3. 原USD/ROS-clock反馈和waitAtTarget门禁不等于原子post-step科研logger/严格零速度稳定证明；正式科学接口由后续任务处理。
4. 力/wrench校准DEFERRED至TASK10-IS；旧parity/image-core/query-tree/五Cube路径LEGACY且未重开。
5. 用户审查本候选是否可成为后续foundation、选in-place thin adapter或最小copy路径；benchmark_v1仍DRAFT。**本轮不自行FROZEN/port/TASK02/P1–P5。**

## POST-TASK REPORT

```text
Task: D041 patched-predecessor Task26 two-Cube GUI physical qualification
Status: PASS CANDIDATE (not FROZEN; prior failure retained)
Scientific objective: qualify complete mature foundation engineering flow
Minimum sufficient evidence achieved: yes, one full original two-Cube/HOME run
Completed: fresh originalGUIlifecycle twice; originalpreflight twice;
  actualphysics twoinvocations, FAIL thenPASS; finalsnapshot/processcleanup
Files changed: thisreport, README, CODEX_START_HERE, TASK01 andsixpersistentrecords;
  results/20261009_TASK01_predecessor_patched_runtime01 and02
Production/runtime/benchmark source changed during this round: NONE
Commands run: existingGUIexecutor originalshutdown/Stop/scene/Play/bridge/Pause;
  originalMoveItlaunch2; originalplanning_only2; approvedbinaryphysical2;
  read-onlyscope/hash/log checks, ownedlaunchCtrl-C, gitrecordscommit/push
Tests / experiment results: preflight0/0; physical1/0; ownedlaunchinterrupt130/130
Key metrics: successfulperCube1.181/.376mm; HOME.059/.062deg;
  peakmonitoredjointtorque23.48/28.98Nm; callbackerrors{} at finalpause
Blockers:
  TASK-BLOCKING: none for this limited foundation-candidate evidence
  DEFERRED: TASK10-IS calibrated wrench; later formal logger/interface contracts
  KNOWN LIMITATION: intermittent actualjointsettle failure, originalFCL/clock/support
    semantics; no statisticalrepeatability/continuouscollision/heldreset proof
  LEGACY: frozen customTASK01/parity/startup/fiveCube routes
Attempt budget used: physical2/3; no3rd invocation afterfullsuccess;
  priorqualification1/1 andsoftwarefix allowance retained separately
Escalation required: no further implementation this round; user candidate review pending
Paper fidelity:
  ORIGINAL: no paper algorithm implemented or reproduced thisround
  ADAPTATION: userapprovedtwoCubequalification insteadexactone
  ENGINEERING: approved5ed0c96 twofix runtime reused; no further modifications
  DEVIATION: none to originalgeometry/physics/ACM/acceptance; sourcepatch disclosed
  EXPERIMENTAL: boundedGUI qualification, not formal cross-method benchmark
Records updated: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK: yes
Open risks: firstnegativephysicalrun unresolved; no new benchmarkfreeze
Recommended next step: userreviewsFOUNDATIONcandidate andsubsequentreusepath
Git branch: task01-legacy-scene-foundation; pre-runscopeeade5de;
  predecessor5ed0c96 unchanged/clean; oldunrelateduntracked artifacts preserved
```
