# TASK01 — 单 Cube 连续 IK 数值诊断（2026-10-07）

Status: **PARTIAL**。原失败点已定位并在同种子对照中通过；PRE_PUSH → TARGET 的名义插入段通过157个离散状态检查。**TASK01没有PASS/FROZEN**：START未定义，START→PRE_PUSH未验证，Isaac READY/reset与碰撞模型差异尚未处理。用户“继续”仅用于保持全部几何的数值诊断；本轮没有启动Isaac。

## 原失败原因与同种子对照

保留2026-10-06 probe02的FAIL_STOP，不把旧结果覆盖成成功。它在前进1.987179mm时把候选拒绝，但原版本没有记录拒绝原因。

新instrumentation（12a6d74）有限复测确认：左右LMA都返回true/MoveIt SUCCESS=1、各7个有限关节值、限位通过；真正拒绝原因是两臂旋转残差超过1e-4rad，**不是已证明无IK解、不是碰撞**。当时未运行FCL。

默认LMA的停止条件使用带权的笛卡尔误差；Humble默认epsilon=1e-5、旋转权重orientation_vs_position=0.01，因此求解器SUCCESS不保证原始旋转残差小于本探针独立验收的1e-4rad。依据为[官方Humble LMA插件源码](https://raw.githubusercontent.com/moveit/moveit2/humble/moveit_kinematics/lma_kinematics_plugin/src/lma_kinematics_plugin.cpp)中的参数初始化与加权求解调用。收紧epsilon是本地数值求解工程设置，不是放宽验收或替换论文算法。

同一二进制8a5bbaf、同一个原记录14q seed、同一目标Cube=(0.7919871794871796,0,0.26)、同一抓取和几何，只改变进程内epsilon：

| 原始旋转残差(rad) | epsilon=1e-5 | epsilon=1e-7 |
|---|---:|---:|
| 左臂 | 2.582469016866072e-4 | 1.8415970339821752e-6 |
| 右臂 | 9.98517296020584e-4 | 2.037262916647003e-6 |
| 独立验收 | REJECT，两臂超1e-4 | ACCEPT，两臂低于1e-4 |
| 原始SRDF/ACM全机器人FCL | 未运行，无合格双IK | PASS，无碰撞对 |

平移验收仍1e-5m，旋转验收仍1e-4rad；权重仍0.01、max iterations仍500，关节界限、工具/车厢/TCP/基座、原SRDF/ACM、seed均未改。没有编辑runtime kinematics.yaml或install生成文件；`--ik-epsilon`只允许收紧到≤1e-5的正有限值。

## 插入段离散几何结果

同一显式端点seed策略，在epsilon=1e-7下重新获得PRE_PUSH，再用上一q单次求解延续，不在中途更换seed/抓取/姿态。六个规定插入端点通过；密集插入段0→100%共157状态、156段，每段1.987179mm。每状态同时检查双IK、FK共享抓取残差、关节界限、完整机器人self/inter-arm/world FCL。沒有新增碰撞豁免。

- 157/157状态通过，无FCL碰撞对。
- 密集链最小关节限位余量25.755478°；最大单关节相邻状态增量0.415676°。这不是时间轨迹或速度/加速度证明。
- 密集链最大TCP平移残差6.5914918e-9m；最大旋转残差9.9421506e-6rad。
- 六个规定端点的腕/工具对墙最小FCL距离2.212015mm（left_link7/deep wall）。密集链没有逐状态记录距离，不能把这个端点最小值称为整个路径的最小净空。
- START仍`NOT_RUN_UNDEFINED_START`；native结果`PARTIAL_UNDEFINED_START`，exit3刻意不返回整体PASS。

MoveIt的robot/world检查不会额外检查两个world物体相撞。对此独立新增名义Cube/环境AABB审计：当前Cube和全部环境是零偏航轴对齐方盒，共628对检查，体积重叠0；Cube/桌面157个边界接触，Cube/深墙1个终点边界接触，符合名义支撑/贴墙关系。4个分离/接触/穿透基本测试通过。1e-12m仅用于双精度边界舍入，不增加物理穿透容限。这个补充检查**不是PhysX接触偏置、转动物体或实际加载跟踪的证明**。

## 构建与实验溯源

串行构建完成后核对最终二进制，再做有效diagnostic02和A/B。有效诊断二进制SHA=415f23ef…；A/B与密集检查二进制SHA=01d64241…；逐run metadata存完整SHA、源码commit、候选/model/kinematics输入hash及命令。

首次diagnostic01误在新instrumentation链接完成前启动，实际运行旧二进制、没有左右诊断字段。原log最后写入mtime为20:08:26.211，新链接mtime为20:08:28.330。保留该run并标记`INVALID_DIAGNOSTIC_OLD_BINARY`，不算新代码验证；未测到实际旧exe SHA，所以记录null而非猜测。其exit1不是新instrumentation实验结果。随后等待构建实际exit0，另起diagnostic02验证。

完整结果目录：

1. `results/20261007_TASK01_single_cube_ik_diagnostic01/`：旧binary/无效诊断溯源，保留FAIL原数据。
2. `results/20261007_TASK01_single_cube_ik_diagnostic02/`：正确instrumentation，确认两臂旋转残差拒绝，exit1。
3. `results/20261007_TASK01_single_cube_precision_default/`：同种子原精度对照FAIL_STOP，exit1。
4. `results/20261007_TASK01_single_cube_precision_tight/`：同种子收紧精度PASS_RECORDED_STEP_ONLY，exit3。
5. `results/20261007_TASK01_single_cube_precision_dense/`：157状态+Cube/environment审计通过，但PARTIAL_UNDEFINED_START，native exit3/audit exit0。

每个目录含metadata.json、结构化结果、精选原stdout证据；大型raw/build本地忽略，不提交build/install。

## 实际验证命令

以下为本轮运行记录；旧结果拒绝覆盖。再次复现必须使用新输出目录，不能向原证据目录重写。

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/install/setup.bash
cmake --build build/single_cube_geometry --parallel 1

# 相同输入，默认精度；返回1表示被原验收拒绝。
build/single_cube_geometry/task01_single_cube_geometry \
  configs/benchmark/benchmark_v1.yaml \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.urdf \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf \
  /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/config/kinematics.yaml \
  results/20261007_TASK01_single_cube_precision_default \
  --replay-step results/20261006_TASK01_single_cube_geometry_probe02/dense_insertion_results.json

# 同一seed/目标，只收紧求解精度；返回3表示仅该记录步骤通过。
build/single_cube_geometry/task01_single_cube_geometry \
  configs/benchmark/benchmark_v1.yaml \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.urdf \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf \
  /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/config/kinematics.yaml \
  results/20261007_TASK01_single_cube_precision_tight \
  --replay-step results/20261006_TASK01_single_cube_geometry_probe02/dense_insertion_results.json \
  --ik-epsilon 1e-7

# PRE_PUSH到TARGET的<=2mm离散链；返回3因为START尚缺。
build/single_cube_geometry/task01_single_cube_geometry \
  configs/benchmark/benchmark_v1.yaml \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.urdf \
  results/20261006_TASK01_single_cube_geometry_probe01/raw/robot.srdf \
  /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws/src/fr3_dual_side_suction_description/config/kinematics.yaml \
  results/20261007_TASK01_single_cube_precision_dense --ik-epsilon 1e-7

python3 platforms/isaac_ros2/probes/single_cube_geometry/audit_cube_environment.py \
  configs/benchmark/benchmark_v1.yaml \
  results/20261007_TASK01_single_cube_precision_dense/dense_insertion_results.json \
  results/20261007_TASK01_single_cube_precision_dense/cube_environment_audit.json

# 证据/源码/二进制一致性及不放宽/不覆盖门禁检查，exit0。
python3 results/20261007_TASK01_single_cube_precision_dense/verify_evidence.py
```

证据审计五组PASS：同seed/同目标/同验收对照、157状态间距/限位/残差/FCL、628个名义Cube/environment检查、五run元数据/源码commit/当前有效binary hash及artifact、非法epsilon（0/-1/nan/1e-4）与覆盖旧结果均返回2且不创建结果。摘要保存在`verification.json`，脚本保留可重复核对。

## 剩余边界与下一步

本轮只证明当前模型下名义插入的离散几何可行性，不是连续碰撞证书、实际吸附/动力学稳定性、START搬运链或P4论文算法。BUG019原Isaac link7 convexHull与MoveIt STL不等价仍OPEN；很小的FCL净空不能换算成PhysX安全保证。没有启动Isaac/READY/reset或发送机器人/吸盘命令，没有推进TASK02或力控。

需要用户确认Benchmark-A START Cube位置及其共享初始状态定义，随后只补对应几何检查，再安排可见GUI的单Cube READY/reset。不能从旧五Cube供料点暗中选START，不能以本轮数值修复宣布冻结。

=== POST-TASK REPORT ===

Task: TASK01 Single-Cube Geometry Feasibility / numeric diagnosis
Status: PARTIAL
Completed: 拒绝原因定位；同seed epsilon A/B；名义插入157状态和Cube/environment628对检查。
Files changed: probe.cpp、audit_cube_environment.py、五个run结果/metadata、本报告及旧报告follow-up、TASK01及六记录；runtime/model/候选未改。
Commands run: 上列serial CMake/native replay/dense/Python审计。
Tests / experiment results: build PASS；有效原精度FAIL、收紧单步PASS、157状态PASS；无效旧binary尝试单独保留。
Key metrics: dense margin25.755478deg、max rotation9.9421506e-6rad、FCL pair0、名义体积穿透0、物理/机器人/吸盘命令0。
Paper fidelity: [ORIGINAL]未实现论文方法；[ADAPTATION]复用已批准单Cube范围；[ENGINEERING]数值精度/诊断与AABB审计；[DEVIATION]无新增；[EXPERIMENTAL]有限同seed对照与离散可行性检查。
Records updated: STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK均更新。
Open risks: START定义、Isaac/MoveIt碰撞模型差异、READY/reset待验，不可称TASK01 PASS/FROZEN。
Recommended next step: 用户确认START后补几何；不直接启动长Isaac。
Git: task01-benchmark-draft；有效instrumentation12a6d74、precision8a5bbaf、环境审计2856fa5，记录提交/push见最终回复。
