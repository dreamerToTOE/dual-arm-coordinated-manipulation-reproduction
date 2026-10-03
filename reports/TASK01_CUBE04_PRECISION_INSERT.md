# TASK01 — 第四件复用第五件精准单臂直推

2026-10-03；状态：实现/编译通过，首轮物理验收失败，最终二进制低速复测进行中；不是 TASK01 冻结。

## 用户批准范围与方法

用户明确要求“那第4块采取第5块的推入方式”，并要求不改已完成场景。
新增独立节点 `task01_cube04_precision_insert`，复用 Task26/27 控制器，不复制控制算法。
第四件：双臂搬运、精准暂放 → 双吸盘 OPEN / 双臂退出 → 左臂从 -X 后面重抓 → 单臂 +X 分段推进 → 松吸盘 / 安全退出。
辅助臂在后吸直推期间停放、OPEN；无低位侧吸、无到深墙后的 INNER_SIDE_TRIM。
第五件仍由 `center_pusher_arm`（默认 right）完成原中心通道单臂插入。
第一至三件保持原工程执行器行为；并不声称它们已实现 D004 论文实验接触协议。

第四件 `cell` 及最终门限不改。新模式仅将 PRE_PUSH 的 Y 控制目标设为实测 Cube02 中心 + 120 mm + **原侧压终点已有的 0.5 mm**，代替旧模式先留 1.5 mm、入墙后侧压 1 mm。
这使暂放控制目标沿 Y 向邻件移动 1 mm，是明确的控制协议适配，**不是场景源码不变就等于所有控制目标不变**。基准 YAML 未改、36 null 未批准。
后吸前新增更严格工程门控：实际 Y 对齐误差 ≤0.5 mm；按两件真实旋转计算 Y 投影包围范围，邻件余隙 ≥0；辅助臂必须 OPEN。不满足即停，不放宽最终验收。
完整同步 FCL、分段跟随/87 Nm 力矩停机、原最终邻件间隙 [-0.5,1.5] mm（100 nm 数值保护）全部保留。
原节点不定义新宏，因此仍执行旧内侧短压。未修改 Isaac 场景、夹具、质量、实际摩擦 0.5/0.5、ACM。

## 文件 / 来源

上游为用户工程 https://github.com/dreamerToTOE/dual-arm-embodied-palletizing ，修改前 SHA `76408c855e3e7b4966db8bfcc26683587d31f3fb`，分支 `task01-runtime-fixes`；工程根未声明统一许可证，不冒充论文开源实现。
新增 wrapper `ros_ws/src/fr3_dual_palletize/src/task01_cube04_precision_insert.cpp`、策略头 `include/fr3_dual_palletize/cube04_precision_policy.hpp`；共享控制器用编译宏隔离更改，CMake 新增安装目标。
本复现仓库新增 `platforms/isaac_ros2/probes/task01_cube04_headless.py`、策略单测和本记录。
物理探针原样加载旧 Task27 场景/Bridge，**只在测试实例中预置前三件并等待原落稳检测**，第四/第五件仍请求正常供料并执行实际搬运。
采样 PhysX post-step，每六物理步记录一次；不将此稀疏位姿通道称为力传感器/全频碰撞校验。

## 可复现命令

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --packages-select fr3_dual_palletize --symlink-install \
  --executor sequential --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
ros2 pkg executables fr3_dual_palletize | rg task01_cube04
```

隔离物理探针（终端一；不用 source 系统 ROS；无用户 GUI 同时占用）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_cube04_headless.py \
  --asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5 \
  --duration-sec 1050 --output-dir results/20261003_TASK01_cube04_precision_02/raw
```

终端二：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description moveit_dual_side_suction.launch.py use_rviz:=false
```

看到探针 READY 后，终端三：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 run fr3_dual_palletize task01_cube04_precision_insert --ros-args \
  -p first_batch:=4 -p max_batches:=2 \
  -p center_pusher_arm:=right -p execution_time_scale:=3.0
```

已有正常 GUI 场景不能直接用 first_batch=4 跳过前三件；必须前三件已在格位通过原验收，或从第一批运行该新节点。测试探针不是新 GUI 基准场景。

## 测试 / 科学边界

- C++ 策略单测通过；Python 语法检查通过；colcon 编译通过。
- 初次新探针使用旧 callback 的错误 API 参数，启动即退出；已换成现有验证探针相同的 PhysX post-step API，并补异常记录。不算物理任务失败/通过。
- `_02` 第四件实际执行至推入/短退，但最终邻件间隙 1.827 mm 超过原 1.5 mm，controller exit 1；第5件未执行。暂放 Y 误差 0.046 mm / 初始旋转投影余隙 0.454 mm；推进期间稀疏物理 Y 范围 1.089 mm，yaw 最大 0.210 deg，原门限没有放宽。6036 个有效稀疏采样；实际辅助吸盘 CLOSED=0、INNER_SIDE_TRIM 命令=0。
- `_02` controller 启动早于最后一次重编译完成；其二进制 SHA 已记录（缺最后的非有限输入门控保护/日志宏可移植性改动，物理流程相同），不能作为最终交付二进制验证。`_03` 单独清场复测最终 SHA，time_scale=5，未增加力控/横向反馈。
- 所有物理负证据保留；无稳定性、多次重复或完整五件通过声明。
- [ORIGINAL] 本次未实现论文算法；[ADAPTATION] 第四件用户批准的后吸直推协议；[ENGINEERING] 宏隔离/策略测试/门控；[DEVIATION] 第四件不再遵循旧 D004 双吸盘插入；[EXPERIMENTAL] 前三件预置缩短测试准备。
- 未开始 TASK02；未解决原始力/时间标定、前三件 D004、MoveIt teardown 问题。
