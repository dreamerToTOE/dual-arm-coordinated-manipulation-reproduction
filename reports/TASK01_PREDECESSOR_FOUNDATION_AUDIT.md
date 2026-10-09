# TASK01 — PREDECESSOR FOUNDATION AUDIT

2026-10-09 · D041 · branch `task01-legacy-scene-foundation` · ENGINEERING / NOT_RUN

## 执行前结论

```text
=== PREDECESSOR FOUNDATION AUDIT ===
Pinned predecessor commit: 631b1f65656d025c1bb2173e874192f3fe4d355a
Task26 files read: pinned Task26 document, complete scene, bridge and 5444-line controller
Existing exact single-Cube mode: no; max_batches=1 executes two
User follow-up: 两件 Cube 也可以，请继续
Chosen tasks: task26_r0_deep, then task26_r0_shallow (original batch 1)
Minimum selector change required: NONE under the latest two-Cube approval
Old runtime components kept behavior-equivalent: ALL; use pinned originals
New runtime components introduced: NONE
Launch sequence: existing GUI / Stop / clean Stage -> original scene -> manual Play
                 -> original bridge -> original MoveIt -> planning_only -> full execution
Stop condition: first substantive lifecycle/preflight/physical failure; no repair-and-rerun
```

审计已在任何新 scene/bridge/MoveIt/控制器运行之前完成。历史 reproduction TASK01 scene、bridge、handoff、parity、readback validator、native D6 probe 全部不参与本次资格验证。旧成功日志只是前代依据，不是本轮 PASS。

## 1. 源码与依赖闭包

主代理直接读取固定提交的四份必读文件全文，不仅依赖摘要；并行只读审计交叉检查 count/index、依赖与隐藏配置。

| 固定提交文件 | SHA256 |
|---|---|
| `docs/tasks/TASK26_TRUCK_BOX_PUSH_IN.md` | `16af05c42a51ac834fdcfa7623968b70086b1d8215b808a772fe93f005e7da4b` |
| `isaac/scripts/task26_truck_box_scene.py` | `43aa7c2eb6a5667da5e94eaaef347229fe6178ec58d6a10d12dddf14ba2aa9e7` |
| `isaac/scripts/task26_truck_box_bridge.py` | `13b5f88d1e7563a37ecafbf571d8ef93015b57059b8912ba9f3399e21e339644` |
| `ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp` | `a844529af73a77b8e52aa7be8eb879a4a86d317148a3ded49ea76e714a72e840` |
| `ros_ws/src/fr3_dual_palletize/config/task26_push_control.yaml` | `7e02ddab2ec5e64d3e939d0c233b6b317a426e84ae2a6013a915dd0765487405` |

进一步直接检查原 `fr3_dual_palletize` CMake 的 Task26 target/dependencies/install、package.xml、配置读取路径，以及以下原启动依赖：

- `fr3_dual_side_suction_description/launch/moveit_dual_side_suction.launch.py`；
- 该包双臂 URDF、L 型工具 xacro、SRDF、kinematics.yaml、CMake/package；
- `fr3_dual_compact_suction_description/scripts/dual_joint_state_bridge.py`、`task06_environment_publisher.py` 及安装规则；
- 外部 `franka_description`、`franka_fr3_moveit_config` 与 ROS Humble/MoveIt 系统依赖的本地可用性。

Task26 三个 runtime 文件自包含，不直接 include/import Task24/27 runtime；Task27 是条件编译/场景分支，不能用它代替原 Task26。不需要另写或整体移植旧 Task24/27。

当前旧仓库工作树 HEAD `d4b290c` 的 controller 已有后续研究修改，不能直接当作固定源码。本轮使用隔离 worktree：

```text
/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation
HEAD = 631b1f65656d025c1bb2173e874192f3fe4d355a
source patch = NONE
```

原 CMake 只构建原 Task26 target，直接调用这次构建的二进制，不复用当前较新的已装 controller。运行依赖使用原 ROS workspace overlay；在运行前比较实际 package-share 的描述、启动/helper 和 push YAML 与固定源码。该配置已读到 `.100` rail advance；如果文件缺失，原 C++ fallback 是 `.200`，因此缺失配置是 STOP，不能依靠默认值继续。

## 2. 两件模式与原几何

最新用户明确接受两件。因此保留 scene/C++ 的原 `BATCH_SIZE=2`、`BATCH_COUNT=2` 和四项任务表，调用 `max_batches:=1`。scene 原生创建四件刚体：第一批两件唤醒，另两件保持 `z=-5 m`/关闭重力，不请求第二批。不是“四件全部执行”，也不是“场景只有两件 Prim”。bridge 原动态 metadata/PoseArray/feed-mask 匹配保持不变。

| 原任务 | 供料中心 m | PRE_PUSH m | 最终 CELL m | 后向支撑 |
|---|---|---|---|---|
| `task26_r0_deep` / Cube_01 | `(.500, 0, .260)` | `(.790, +.060, .260)` | `(1.100, +.254, .260)` | +X 深墙 |
| `task26_r0_shallow` / Cube_02 | `(.350, 0, .260)` | `(.790, +.060, .260)` | `(.980, +.254, .260)` | 第一件的 -X 面 |

Cube 边长 `.120 m`、质量 `.800 kg`；桌面 `1.50 × .80 × .20 m`，顶面 `.200 m`；车厢内腔 X `[.910,1.160]`，Y `[-.314,+.314]`，墙厚 `.020`、高 `.150`。L 杆下探 `.080`、横段 `.130`、原阵列与 TCP 不变。两基座原 rest `.650`/Y±`.600`，推入前旧 YAML 导轨 `.650→.750`、world shift `+.100`。

保留原 HOME、LMA 参数、SRDF/ACM、官方关节/drive override、摩擦/physics/SG 和验收门限。不导入 reproduction 的 START `[.55,0,.38]`、中心 TARGET y=0、冻结 14q、LMA epsilon override 或新 readback guard。

## 3. 原成熟流程（不重新实现）

```text
原批次到料 / Ground Truth
→ 空载 RRT 候选 + 全链同步 FCL
→ 两侧中心接触 / 原吸附前与后几何门禁 / 双 SG CLOSED
→ COMMON_LIFT → Cartesian X/Y/Z 搬运 → short push → drop to table
→ 双侧 OPEN → helper park / pusher lift
→ 两轨 +.100 → rebuild static world / reproject existing Cubes
→ 原右臂 -X rear regrasp (完整 regrasp/push/exit 候选筛选)
→ 原 16 段 +X 推进与进度/力矩保护
→ 原另一臂侧压 + 原推臂保持背挡、同步 Y 跟随
→ release / 原退出 / 真实格位与支撑间隙验收
→ 第二件同样原流程 → 原共同 HOME
```

只保留原位置推进与原保护，默认 `wrench_probe` 为空，不执行 force/wrench calibration 或新导纳实验。旧程序内部有界 RRT 候选/Cartesian retries 是原算法行为，不新增外部失败重跑。

## 4. 原启动方式与本轮准备

本轮 GUI 已正常运行（PID39508 / 本地8226 executor）。只读检查发现它仍暂停在历史 reproduction Stage；已请求操作者 Stop + File→New，操作者随后确认“新场景已准备”。在确认清洁 Stage 后才加载原 scene；不得在原 Task01 对象仍存在时混装旧场景。仍由操作者手动 Play。

Script Editor / 已有 GUI 执行器使用相同两条原文件加载命令；明确选择原 Task26，避免残留全局 Task27 模式：

```python
_SIDE_SUCTION_SCENARIO = "task26"
exec(open("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/isaac/scripts/task26_truck_box_scene.py").read())
```

scene ready 后手动 Play，再：

```python
_SIDE_SUCTION_SCENARIO = "task26"
exec(open("/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/isaac/scripts/task26_truck_box_bridge.py").read())
```

外部 ROS 环境与原 MoveIt：

```bash
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description moveit_dual_side_suction.launch.py use_rviz:=false
```

Planning-only command（独立编译原 target；没有新 controller/wrapper）：

```bash
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash
export ROS_LOCALHOST_ONLY=0
/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/build/fr3_dual_palletize/task26_truck_box_push_in --ros-args -p planning_only:=true -p max_batches:=1
```

Physical command：

```bash
/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/build/fr3_dual_palletize/task26_truck_box_push_in --ros-args -p max_batches:=1 -p execution_time_scale:=3.0
```

保留前代已验收 `execution_time_scale=3.0` 与原速度设定，不称为新 benchmark 的效率结果。`ROS_LOCALHOST_ONLY=0` 是旧文档的 GUI DDS 互通要求。

## 5. 风险、证据范围与停止

- 原 `planning_only` 不发 joint/suction/feed/rail 命令，但会重建/修改共享 MoveIt PlanningScene，完成件被虚拟回写格位；bridge 原自动到料不属于 controller planning-only 命令。它也不实际移动或模拟 rail handoff；物理流程仍在实际 rail move 后刷新与重新 FCL。不宣称整个 GUI/场景只读或完整物理安全证书。
- 原 launch 另加 `task24_table`（长1.20m），controller 加 `task26_table`（长1.50m），原刷新不移除前者。这是原组合的模型风险，记录但不自行修复、扩大 ACM 或偷偷删除对象。
- 原 scene 的硬编码 `task26_diag.json` 当前不存在；原 optional `t26_clearance_probe.flag` 当前存在，会启用已有 AABB 日志，不改控制。保留原行为；AABB 不是精确 PhysX/FCL 等价证明。
- 原 bridge 读取 USD pose，并用原 ROS clock；不宣称 native 原子 post-physics 科研时间、D6 anchor 或连续碰撞证明。此次只按原 Task26 验收 foundation 的完整工程可复现性。
- 外部 FR3 资产、系统 MoveIt 和 GUI 版本属于实际环境依赖，固定项目 commit 不冻结它们。记录实际版本/路径与异常，不现场“修好”一个新的 foundation。
- 只允许一次 planning-only（工程超时上限600s）、通过后一次两件物理调用（上限1200s）。首个实质失败立即停止，分类环境/依赖/启动/旧流程不可复现；不改源码、drive/SG/墙/tool/阈值，不自动第二次 invocation，不调查 image-core/cleanup segfault。
- 成功需两件原 PASS、实际格位/后向支撑/侧墙门禁（原位置10mm、间隙3mm）与共同 HOME。只可给出 `TASK01=PASS CANDIDATE`、`FOUNDATION_SCENE=PREDECESSOR_TASK26_BATCH1_TWO_CUBES`；两件名称是最新授权，不能冒称 SINGLE_CUBE 或 FROZEN。失败保留本轮实际日志，历史 PASS 不覆盖失败。

下一步只做固定 worktree 构建与上述原链路资格验证。暂不移植、优化、冻结 benchmark 或开展论文控制算法。

## 6. 独立预检复核补充（预检后记录，不改原实现）

原 planning-only 本轮 exit0：deep/shallow 分别输出 PASS，随后原 batch1/HOME 预检 PASS。候选池中存在被拒绝的 RRT 解，保留全日志，不称所有候选成功。

- 原 `planHome()` 使用 `setStartStateToCurrentState()`；零执行时实际仍在 HOME，本轮 HOME 预检为各2点/联合8样本，不能解释成虚拟最终退出构型→HOME 的证书。真实物理末尾另从实际状态规划和执行 HOME。
- 原 `validateSync()` 验证给定 world 和双臂关节；共同抓持阶段当前 Cube 已摘出 world，未建立 AttachedCollisionObject。因此不声称 carried-Cube 全链碰撞覆盖；只是保留原工程规划门禁，最终须真实物理资格验证。
- 原 shallow `xSupportGap()` 用名义 deep X，不是另一个 Cube 的当前实际 X。保留原门禁；最终若补算两件 Ground Truth 真实净距，应明确标为独立离线计算。

这些是前代实现的证据限制，不授权替换控制器或新建验证系统。实际物理结果尚未在本节作结论。
