# TASK01 — 前三件双吸附主从推压，后两件精准单臂插入

日期：2026-10-05；状态：IN_PROGRESS。本报告不能引用旧流程 5/5 作为新流程通过。

## PRE-TASK REPORT

- Task: TASK01，落实用户批准的前三件 rear+side 双吸附与主从互换。
- Goal: 前三件后臂主推、侧臂吸附约束；到深墙后侧臂主压、后臂保持深墙贴合。第四/第五保留精准预定位与单后推。
- Paper method understood as: [ADAPTATION] 用户基准接触协议 / [ENGINEERING] 同步轨迹与安全检查；不是 P2 内部力控制或 P3 力位混合复现。
- Scope: 新独立执行节点复用已验收共同搬运/落桌/重抓/短清障和 RRT 转场；前三件在后吸盘重抓后建立侧吸盘，双 CLOSED 才推进，主从换角色不松开吸盘。新分支不得回退成停放 helper 或单臂 trim。
- Files expected to change: 上游共享 cpp 的新独立宏、独立入口/接触策略 header、CMake；本仓测试、此报告、六份记录、任务说明与结果。
- Validation plan: 固定面中心工具几何检查 → 策略/软件单测 → 编译 → 完整 FR3 无执行 FCL/接触链预检 → 本机 headless 单件/前三件 → 后两件回归 → 新鲜普通完整五件。
- Known ambiguities / risks: 双吸附闭环跟踪误差、第三件工具/关节净空、推墙后位置命令的载荷。本轮仍不具有校准 TCP wrench；关节 effort 不叫接触力。旧 BUG-016/MoveIt teardown 保留。
- Need user confirmation: no，用户明确批准前三件双臂、后两件精准；但工具/场景/质量/摩擦/ACM/门限/论文方法/冻结改变需另行确认。

## 初始只读检查

旧节点 `task01_cube04_precision_insert` / 上游 `df9c2c0` 保留；本仓起始 `bb301b2`。
现有 xacro 盒体在前三件 prepush/deep/pressed 的 rear+朝中央空隙侧面中心姿态，未发现 tool-tool / tool-wall / tool-previous-cube 盒体相交。没有改场景；这不是完整 FR3 FCL、轨迹或 PhysX 证明。第三件 helper 从 -Y 自由面约束 +Y 内件，不从已贴近外件的 +Y 面挤入。

## 实现与当前证据（2026-10-05）

Runtime `ff20ac3d18f16245cabb1a32e8e2c14a83af42ed`，独立目标binary SHA256 `bd1de5b7a69ebd84f42c1f827879551cd62a4a939737c2341239c8f3087214c2`；旧节点不替换。前三helper在朝中央通道的侧面中心，第三不挤到已贴近外件的一面。加载段不用RRT；同一物体位移网格、有限近seed世界FK微解算、两臂相同点时间，随后联合FCL/原相对几何门控。原80Nm只是raw joint effort保护，不叫接触力。X/Y各16段实际反馈，双CLOSED互锁，失败双OPEN并恢复当前Cube World。

新双吸附侧压终点为原贴墙格位，不沿用旧未吸附机械杯面4mm越程；第四/第五不改精准单推。释放后局部30mm法向清障预检（执行必须双OPEN），接原RRT/FCL转场。意图接触期间仅当前移动Cube沿用旧“非静态障碍”策略，全部桌/墙/前件/机器人碰撞检查保留；没有扩大ACM，也不声称这已验证移动Cube全部连续接触动力学。

编译PASS、34 Python与4 C++策略测试PASS；YAML analytic PASS但36nulls/哈希未变。名义无执行探针04前三链3/3 PASS，relative TCP max_axis约0.002mm。探针01/02/03负结果保留；配置缺IK、独立时间缩放漂移/Cartesian跳支、窄同侧seed覆盖不足不是新物理碰撞结论。

初始checkpoint：新鲜原场景首块物理 `results/20261005_TASK01_dual_fixture_cube01` 当时正在运行；未取得新流程物理PASS。最终首试/复测结果见下节。旧5/5只属于rear-only推入/未吸附侧压旧节点。

### 首块新物理试验：X通过，Y互锁停止

上述运行现已结束，controller exit1 / completed=[]，不是首块完整PASS。rear=right、side=left均CLOSED时X的16/16片段完成，到深墙gap0.286mm，alignment2.171mm/tilt0.265deg。刚进入主从互换后即触发active interlock；旧日志未记录具体是哪项状态或raw力矩，不能确定根因，也不能叫物理不可行。

X末左臂tracking残差0.551deg，原Y沿命令终点衔接而非实测状态。新工程版本 `e0477ab`（binary `d1658940…`）在深墙座稳后读取同一份双臂实测状态/新Cube GT、保留双CLOSED、检查当前联合FCL再计划Y和释放包络；guard记录rear/side状态与两臂raw peak torque，不放宽任何门限。新鲜首件复测 `results/20261005_TASK01_dual_fixture_cube01_measured` 已开始，结果待实测，不能宣称修复因果已经证实。

首试4747条稀疏PhysX样本/0完整性错误，失败后双OPEN，Cube02–05仍停车；原日志与analysis/protocol保留。新增协议parser实际把旧五件PASS判为 `full_new_protocol_logged=false`；35 Python测试通过（包含保留失败局部证据），4 C++策略测试和新版编译通过。

### 实测换角色复测：Y完成14段，第15段raw关节effort保护停止

运行源码 `e0477ab3a8ba2b23bf99297e8af99227d727ede0`，binary SHA256 `d1658940c72be17d4cb903bd0fdd3357ce5f82b7514d22d5e55207baaff82cff`。新鲜本机headless原场景，first1/max1/scale5/hold0/零预置；控制器运行期间没有源码修改。MoveIt保留旧进程而物理Stage重新启动，未宣称固定OMPL随机种子。

实测起点FCL/Y重算通过。X16/16、Y14/16片段双CLOSED完成，但Y第15段触发原80Nm保护，controller exit1/completed=[]，之后双OPEN，后四件未推进。关键原日志（完整精选在run的controller_evidence.log）：

```text
DUAL_ROLE_SWAP_MEASURED_START synchronized FCL PASS, samples=11.
DUAL_SIDE_PRIMARY_Y_MEASURED relative TCP PASS: max_axis=0.004 mm angle=0.000 deg.
DUAL_ROLE_SWAP: side PRIMARY, rear deep-wall HOLD; no suction release.
DUAL_SIDE_PRIMARY_Y slice 14 rear=CLOSED side=CLOSED rear_gap=1.129 mm side_gap=0.137 mm alignment=1.448 mm tilt=0.220 deg.
+X support seat (+X deep wall): gap=+0.191 mm (target 0), z_error=0.209 mm.
DUAL_SIDE_PRIMARY_Y slice=15 active interlock: rear=CLOSED side=CLOSED left_peak=86.975 Nm right_peak=32.984 Nm (limit=80.000); no later command.
Task26 safe abort during dual fixture contact/push: both side suctions are OPEN.
[ros2run]: Process exited with failure 1
```

本次触发项是raw关节effort而不是吸盘OPEN。它不是已校准TCP wrench，不能将86.975Nm报成接触力，或断言必须力控。X完成深墙gap0.445mm；Y14后深墙gap0.191mm/attachment alignment1.448mm/tilt0.220deg。最后稀疏双CLOSED样本Cube中心 `(1.099520,0.225646,0.260454)m`，距名义侧压终点Y=0.243m仍17.354mm；这不是互锁同一步，不应直接解释为已到侧墙后的越程。

新增只读释放后静态实际姿态探针 `c1df356ea77e028e0f38fb9f65d677e3782a0b67`，build66s PASS；不构造Arm、不发joint/suction/feed/rail、不改远程PlanningScene/ACM。在本地保留桌/墙/其他对象，仅忽略当前合法接触Cube01，联合FCL11样本PASS。**释放后静态PASS不能排除互锁瞬间碰撞，也不能区分闭环约束载荷/跟踪误差/其他接触。** 原release-only logger未激活，本轮0接触记录不等于0接触力。

本轮9432稀疏PhysX样本/0完整性错误，35 Python PASS；新3+2 C++策略重新编译/执行PASS。全部自有试验进程停止，headless exit0；MoveIt关闭-11/joint bridge1另记，不把正常launch退出0叫无teardown bug。TASK01仍IN_PROGRESS/36nulls，不能借旧5/5或无命令名义3链PASS冻结。后两精准单推源逻辑保留，本轮未进行新节点后两件物理回归。

### 下一步（未执行，保持当前边界）

先在同一物理步采集持件推压窗口的14关节状态、工具/Cube姿态、接触对及raw effort，定位Y15保护。然后再考虑原门限内的小步实测起点/跟踪工程修正；若证据要求改工具/物理/基准或新增力控/论文算法，先向用户申请新的范围。不得恢复helper停放、降低接触协议要求、提高80Nm或扩大ACM换取PASS。

### 验证命令

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
colcon build --packages-select fr3_dual_palletize --symlink-install --parallel-workers 1
source install/setup.bash
# 原场景bridge已就绪且没有执行器运行时，仅做名义规划/FCL，不发机器人命令
ros2 run fr3_dual_palletize task01_dual_fixture_probe
# 首块物理试验，不是五块验收
ros2 run fr3_dual_palletize task01_dual_suction_fixture --ros-args \
  -p first_batch:=1 -p max_batches:=1 -p execution_time_scale:=5.0
# 控制器已经停止且物理Stage仍运行时，静态只读检查；不是触发瞬间诊断
ros2 run fr3_dual_palletize task01_dual_fixture_probe --ros-args \
  -p diagnose_released_state:=true
```

完整Isaac/MoveIt命令在两run的metadata.json。新鲜headless为用户本机，不是远程GUI，零预置且普通release hold=0。软件安全筛选不保证双D6力学稳定；TASK01依旧IN_PROGRESS。

## === POST-TASK REPORT ===

- Task: TASK01，新3+2执行协议；Status: **PARTIAL**（软件实现/名义FCL通过，首件实际未完整通过）。
- Completed: 独立前三双吸附主从节点；后两精准单推复用；共同进度/联合FCL/原门限互锁；两次首件实际试验和释放后只读诊断；旧节点/场景不替换。
- Files changed: runtime `src/task01_dual_suction_fixture.cpp`, `src/task01_dual_fixture_impl.inc`, `src/task01_dual_fixture_probe.cpp`, `src/task26_truck_box_push_in.cpp`（独立宏/可选guard）, `include/fr3_dual_palletize/dual_fixture_policy.hpp`, CMakeLists；本仓策略/parser测试、summarize_dual_fixture.py、本报告、六记录、TASK01任务卡及三个结果目录的小型证据。各commit diff为准确列表，raw/build/install未提交。
- Commands run: 上述build/MoveIt/controller/probe命令；两个physical run的metadata记录完整Isaac参数；Python unittest discover、benchmark analytic checker；g++ -std=c++17 -Wall -Wextra -Werror编译dual fixture policy后执行；git diff --check。
- Tests / results: build/Python35/4项累计C++策略/名义前三3链联合FCL PASS；本轮dual policy重跑PASS；两次首件实际FAIL。首试Y起步互锁原因未记录，复测Y15明确raw effort保护；释放后静态FCL PASS仅后状态。
- Key metrics: 复测X16/Y14 completed slices/bothCLOSED，left86.975/right32.984Nm与80Nm保护；完成整件0；9432稀疏pose/0完整性错误；其余四件未推进。完整metadata/analysis/protocol/原日志摘录见 `results/20261005_TASK01_dual_fixture_cube01_measured/`。
- Paper fidelity: [ORIGINAL] 未实现任何新论文控制算法；[ADAPTATION] 用户批准前三rear+side主从互换、后两精准单推；[ENGINEERING] 实测起点/共同进度/FCL/互锁/只读诊断；[DEVIATION] 没有放宽门限/改场景来伪造通过，不声称忠实论文复现；[EXPERIMENTAL] 首件负结果与名义探针均有范围限制。
- Records updated: STATUS、WORKLOG、EXPERIMENT_LOG、BUGS（017 OPEN）、DECISIONS（D019）、USER_FEEDBACK全部更新；TASK01任务卡/本报告/results更新。
- Open risks: Y15载荷/碰撞根因未隔离；没有持件同一步contact/14joint证据；双D6动态载荷、模型质量/摩擦/36nulls审查及历史BUG016、MoveIt teardown仍OPEN。新物理5/5和后两新节点回归未执行。
- Recommended next step: 同物理步只读持件诊断 → 原门限内工程修正 → 新鲜首件/前三件/后两件/完整五件依次验收；需要物理或算法范围扩大时先征询。
- Git branch / commit / dirty files: runtime `task01-runtime-fixes`，实施ff20ac3、实测换角色e0477ab、静态诊断c1df356；本仓 `task01-benchmark-draft`，最后记录commit见Git历史。本报告与证据一并提交，不声称raw全部上传。用户原有runtime未跟踪目录保留；保护目录未访问/修改。
