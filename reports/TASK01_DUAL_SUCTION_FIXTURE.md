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

新鲜原场景首块物理 `results/20261005_TASK01_dual_fixture_cube01` 正在运行；未取得新流程物理PASS。旧5/5只属于rear-only推入/未吸附侧压旧节点。

### 首块新物理试验：X通过，Y互锁停止

上述运行现已结束，controller exit1 / completed=[]，不是首块完整PASS。rear=right、side=left均CLOSED时X的16/16片段完成，到深墙gap0.286mm，alignment2.171mm/tilt0.265deg。刚进入主从互换后即触发active interlock；旧日志未记录具体是哪项状态或raw力矩，不能确定根因，也不能叫物理不可行。

X末左臂tracking残差0.551deg，原Y沿命令终点衔接而非实测状态。新工程版本 `e0477ab`（binary `d1658940…`）在深墙座稳后读取同一份双臂实测状态/新Cube GT、保留双CLOSED、检查当前联合FCL再计划Y和释放包络；guard记录rear/side状态与两臂raw peak torque，不放宽任何门限。新鲜首件复测 `results/20261005_TASK01_dual_fixture_cube01_measured` 已开始，结果待实测，不能宣称修复因果已经证实。

首试4747条稀疏PhysX样本/0完整性错误，失败后双OPEN，Cube02–05仍停车；原日志与analysis/protocol保留。新增协议parser实际把旧五件PASS判为 `full_new_protocol_logged=false`；35 Python测试通过（包含保留失败局部证据），4 C++策略测试和新版编译通过。

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
```

完整Isaac/MoveIt命令在两run的metadata.json。新鲜headless为用户本机，不是远程GUI，零预置且普通release hold=0。软件安全筛选不保证双D6力学稳定；TASK01依旧IN_PROGRESS。
