# TASK01 Single-Cube Geometry Feasibility Probe

2026-10-06 · scope: `single_cube_core_benchmark` · Status: **BLOCKED / stop for review**.

只运行纯几何探针。按用户要求，在加密插入链首个失败后立即停止；没有启动新 Isaac、旧 Task27 控制器或 READY/reset。原 L 工具、车厢、TCP、碰撞网格、SRDF/ACM 没有修改。

## 输入和方法

使用云端已批准的 schema2 候选 `configs/benchmark/benchmark_v1.yaml`，hash `ff490a56…`。模型来自 runtime `d4b290c` 的原源码 xacro 展开，不依赖正在运行的旧五块世界。机器人基座显式核对为 `(0.650, ±0.600, 0)`，无隐藏导轨平移。使用原 LMA 插件和原 SRDF 邻接豁免，仅在本地 PlanningScene 添加一块 Cube、桌面和三面墙。未调用 MoveGroup action，未编辑远程 Scene/ACM。

候选几何：Cube 120 mm / 0.8 kg；原 L 工具下探80 mm/横杆130 mm；桌面1500×800×200 mm、顶面Z=0.200；车厢内部X=0.910…1.160、Y=±0.303 m，墙厚20 mm/高150 mm。保持候选共享抓取左右物体局部 `(0, ±0.061, 0)` 与原固定姿态。PRE_PUSH=(0.790,0,0.260)，TARGET=(1.100,0,0.260)，无偏航，推入310 mm。

端点每臂最多64个显式seed、最多保留12个合法IK，检查成对RobotState的限位、FK抓取残差和全机器人 FCL（双臂各自自碰撞、臂间、工具、桌面、墙、当前Cube）。共享Cube采用当前世界pose，每点更新，不把它删除或整块豁免。1 mm候选抓取间隙使几何探针无需新增接触ACM；这不证明真实吸附。

端点通过后，从选定PRE_PUSH构型按不超过2 mm的物体位移进行上一q单次seed的分支延续，同步求双IK并做全FCL。不是论文P4投影算法，不是路径全局搜索或连续碰撞证明。

## 规定采样点

| Sample | 双IK | Joint Limit | FCL | wrist/tool-wall净空 | Relative Grasp | 结果 |
|---|---|---|---|---|---|---|
| START | 未测试 | 未测试 | 未测试 | 未测试 | 未测试 | 候选仍为PENDING_CAPTURE |
| PRE_PUSH | PASS | PASS | PASS | 46.093 mm | PASS | 仅端点PASS |
| INSERT_10 | PASS | PASS | PASS | 24.392 mm | PASS | 仅端点PASS |
| INSERT_30 | PASS | PASS | PASS | 9.063 mm | PASS | 仅端点PASS |
| INSERT_50 | PASS | PASS | PASS | 9.049 mm | PASS | 仅端点PASS |
| INSERT_70 | PASS | PASS | PASS | 9.061 mm | PASS | 仅端点PASS |
| INSERT_100 | PASS | PASS | PASS | 2.206 mm | PASS | 仅端点PASS |

最小限位余量3.189440°，在30%处；端点抓取平移残差最大0.000585 mm、旋转最大8.56018e-5 rad。100%最近的所检查腕/工具墙对为 `right_fr3_link7 ↔ carriage_deep_wall`，FCL正净空2.205603 mm，不是碰撞穿透。各点的精确14q、误差、成对距离详见JSON/CSV。

## 加密链的首个失败：立即停止

```text
DENSE index=1
insertion_fraction=0.00641025641025641 (0.641026%)
Cube=(0.7919871794871796, 0.0, 0.26) m
PRE_PUSH 后前进1.987179 mm
NO_ACCEPTED_DUAL_IK_ON_PREVIOUS_SEED
exit code=1
```

没有获得通过当前插件返回、限位和FK残差检查的双臂候选，因此该失败点没有执行FCL，**不能编造碰撞对象或穿透深度**。本版没有记录具体拒绝臂或原始IK错误码，不能区分插件失败、越限与残差拒绝；这是诊断缺口，不是已确认的物理障碍。

只有一个上一q seed被测试；六个端点虽然可达，也不能连成已验证安全路径。反之，这个局部seed失败也不能证明所有冗余构型均不可行。没有进一步重放、扩大seed池、改姿态/接触点或改几何。当前结果不是科学benchmark PASS。

## MoveIt / Isaac 几何边界

BUG019已经记录：原Isaac link7 authored `convexHull` 与 `franka_description` STL不同，模型位置一致也不能认为碰撞完全等价。历史对比：Isaac资产hash `3feceb47…`，MoveIt STL `c48646a7…`，见 `results/20261006_TASK01_held_fixture_diagnostic02/mesh_hull_audit.json`。

本轮FCL净空仅适用于所加载URDF；没有启动PhysX或检验原Isaac cooked hull/contact offset。2.206 mm不能据此认证物理净空。原L工具碰撞体参与了FCL，没有忽略工具。失败即停，本轮未做额外Isaac网格审计。

## 命令与证据

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash
cmake -S platforms/isaac_ros2/probes/single_cube_geometry \
  -B build/single_cube_geometry -DCMAKE_BUILD_TYPE=Release
cmake --build build/single_cube_geometry --parallel 1

# 仅生成探针输入文件；不修改原模型/安装目录。
xacro /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/urdf/dual_fr3_side_suction.urdf.xacro \
  > results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.urdf
xacro /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/srdf/dual_fr3_side_suction.srdf.xacro \
  > results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf
build/single_cube_geometry/task01_single_cube_geometry \
  configs/benchmark/benchmark_v1.yaml \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.urdf \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf \
  /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/config/kinematics.yaml \
  results/20261006_TASK01_single_cube_geometry_probe02
```

命令为实际运行记录，**暂不要再次运行**；探针拒绝覆盖已有结果。probe01端点结果exit3/PARTIAL保留；probe02加密首败exit1。source=`c9d71f4`，binary SHA=`1569a5cb…`。构建通过，0关节命令/0吸盘命令/0新Isaac启动。结构化文件在两个 `results/20261006_TASK01_single_cube_geometry_probe0{1,2}/`；probe02包含metadata.yaml、sample_results.json、dense_insertion_results.json、collision_pairs.csv、joint_margin.csv、relative_grasp_error.csv和精选原始probe_evidence.log。

## 下一步候选（等待确认，不实施）

优先保留所有几何，补具体左右臂拒绝原因并有限诊断IK分支连续性/数值收敛；同时需确认Benchmark-A START的Cube pose和共享14q，不能从旧五块供料暗中继承。只有证据显示几何真的受限，才讨论抓取姿态/冗余构型或模型变化；当前没有证据支持缩短工具、扩大车厢、放宽ACM或新增力控。需要用户确认后才继续。

=== POST-TASK REPORT ===

Task: TASK01 Core Single-Cube Benchmark Freeze
Status: BLOCKED（端点部分通过，加密链未通过，按要求停止）
Completed: 云端范围合并；只读探针构建和规定端点检查；加密链首败保存。
Single-Cube Geometry: START未定义；PRE_PUSH/10/30/50/70/100仅端点PASS；0.641026%加密节点FAIL_STOP。
Isaac READY/reset: NOT RUN。
Benchmark candidate: 原双FR3/L工具/120mm Cube/车厢保持；PRE_PUSH和TARGET如上；physics dt候选0.016666667s；physics post-step simulation time；材质候选0.5/0.5，不等于已冻结。
Files changed: 新探针CMake/CPP、结果与本报告、六条项目记录；模型/工具/车厢未改。
Commands run: 上述cmake/xacro/native probe；仅暂停并关闭上一请求遗留自有GUI；无新物理实验。
Tests: build PASS；84限位CSV行、12相对误差行；六端点全FCL PASS；加密2状态检查、第二状态拒绝；JSON/YAML/CSV元数据一致性校验与git diff --check通过（未重跑探针）。
New results: probe01 PARTIAL、probe02 FAIL_STOP；均single_cube_core_benchmark。
Paper fidelity: [ORIGINAL]未实现论文方法；[ADAPTATION]已批准单Cube科研范围；[ENGINEERING]只读IK/FCL检查和记录；[DEVIATION]无新的；[EXPERIMENTAL]有限几何可行性试验，不是物理/全局可行证明。
Legacy Task27: No new five-Cube debugging performed: yes（仅结束旧run并记录既有负结果）。
Force/wrench: Calibration deferred to TASK10-IS: yes。
Records updated: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK: yes。
Open blocker: START缺定义；局部seed连续IK失败且未记录具体拒绝臂；Isaac/FCL差异仍未消除。
Need user decision: 是否允许保持全部几何继续诊断连续IK，并确认START定义。
Recommended next step: 先诊断/确认，不启动Isaac、不改几何、不推进TASK02或力控。
Git: task01-benchmark-draft；源代码c9d71f4；记录提交与push结果见最终回复。
