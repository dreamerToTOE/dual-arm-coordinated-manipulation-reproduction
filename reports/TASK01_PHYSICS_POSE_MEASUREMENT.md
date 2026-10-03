# TASK01 位姿/时间测量诊断与校准（2026-10-03）

状态：**独立匀速刚体校准通过；TASK01 仍为 IN_PROGRESS，不是 benchmark 冻结或论文控制器复现结果。**

## 范围与分类

- **[EXPERIMENTAL]** 单个无重力匀速刚体，用解析位置/角度检查传感通路，不验证接触力学。
- **[ENGINEERING]** 只读 PhysX post-step 采样器、ROS 发布/记录器与干净环境启动脚本。
- **[ADAPTATION]** Isaac Ground Truth 映射为 ROS `world` 位姿与仿真时间。
- 未改 Task27 场景、质量/摩擦、关节控制、接触流程、成功阈值或规划器；未实现任何论文方法。

## 两个不同根因

### 1. USD 位置更新慢于物理步

最小场景采用 `physics_dt=1/60 s`，刚体线速度 `0.2 m/s`。在同一物理步回调中，PhysX 已前进而 USD 仍可能是上一应用帧的位置；`app.update()` 返回后两者位置一致。在应用帧间隔为 `1/30 s` 时，回调内最大差为 `6.667 mm`；改成 `1/20 s` 时最大差为 `10.000 mm`，与 `v × frame_dt` 一致。

这解释了此前推入过程中的瞬时位置差，但并不等于修好了旧 `/task27/cube_poses`：旧桥仍在物理回调中读取 USD。

### 2. 带缩放矩阵不能直接提取旋转

旧桥 `task26_truck_box_bridge.py::_pose()` 用 `ComputeLocalToWorldTransform()` 后直接 `ExtractRotationQuat()`。Cube 的该矩阵包含 `scale=(0.12, 0.12, 0.12)`，因此得到的旋转错误；再归一化四元数也无法恢复正确角度。

在应用帧更新完成、位置完全一致的时刻，旧提取方式与 PhysX 的旋转差仍达 `27.464°`。仅将 USD 矩阵先 `RemoveScaleShear()`，角度差降至 `0.000154°` 以内。这是独立于位置时序的确定性变换错误。

[OpenUSD GfMatrix4d 官方说明](https://openusd.org/24.08/api/class_gf_matrix4d.html) 要求 `ExtractRotationQuat()` 使用旋转矩阵；`RemoveScaleShear()` 用于移除尺度/剪切。另核查了本机 Isaac 4.5 的 `RigidPrim.get_world_poses()` 实现：有有效物理句柄时直接读取 physics view；无句柄则回退 USD。新采样器明确拒绝这种回退。

**历史更正：此前对称性报告中的 Bridge yaw 不是有效六自由度测量。** 保留原始数值以便追溯，但不再用其评价真实转角。落稳后位置结果不受这一旋转提取错误影响。

## 新的实验测量通路

```text
PhysX 每个已完成的物理步
  ├─ initialized RigidPrim view: position / quaternion / linear & angular velocity
  └─ Isaac core nodes: get_sim_time() / get_physics_num_steps()
                │  一个不可变 snapshot
                ├─ /task01/physics/cube_poses            PoseArray
                └─ /task01/physics/cube_poses/snapshot   String (JSON)
                                      ↓
                         外部 ROS2 只读校验/记录器
                                      ↑
                        /clock (仿真时间，同域、不同发布频率)
```

- 订阅 `subscribe_physics_on_step_events(..., pre_step=False, order=200)`，在物理步完成后读数据。
- 采样器读取 live physics view，统一归一化为 ROS `xyzw` 四元数；所有对象共享同一仿真时间戳与物理步号。
- PoseArray 与 JSON 从同一个 snapshot 构造；JSON 额外保留 prim path 和速度。
- 仿真重置/时间不递增/句柄失效时显式报错；重置后必须新建采样器。
- 初始化 view 使用 `reset_xform_properties=False`，不重设场景变换、不添加接触传感器。
- 旧话题不改，控制节点仍用旧 Bridge。新话题目前是 **TASK01 测量辅助接口**，不是已冻结的 TASK02 公共接口，也不提供 TCP/力矩/车厢 TF 的完整同步契约。

## 独立校准结果

刚体边长 `0.12 m`、质量 `0.8 kg`、初始 yaw `7°`，无重力、线速度 `(0.2,0,0) m/s`、角速度 `(0,0,0.3) rad/s`，运动 120 个物理步。为保证解析匀角速模型成立，**仅校准刚体**显式设线/角阻尼为 0，Task27 参数不变。

| 校准项目 | 应用帧 30 Hz | 应用帧 20 Hz |
|---|---:|---:|
| 物理步长 | 1/60 s | 1/60 s |
| 外部 ROS 收到的运动样本 | 120 | 120 |
| 新通路位置解析误差最大值 | 0.000312946 mm | 0.000312902 mm |
| 新通路角度解析误差最大值 | 0.000864737° | 0.000864742° |
| 发布 snapshot 数（含静止） | 150 | 165 |
| 回调异常 | 0 | 0 |
| 最近 `/clock` 与位姿时间戳最大差 | 0.016666668 s | 0.016666669 s |
| 旧 USD 位置回调内滞后最大值 | 6.666675 mm | 10.000005 mm |
| 更新后 USD 原始旋转提取最大误差 | 27.463784° | 27.463784° |
| 更新后移除尺度的 USD 最大角差 | 0.000153299° | 0.000153299° |
| 外部只读校验 | PASS | PASS |

校准 gate 为位置解析误差 `≤10 µm`、旋转解析误差 `≤0.001°`，以及时间/步号递增、单位四元数、相同 snapshot 与 world frame；**这些仅用于测试测量通路，不是码垛验收阈值**。最近 `/clock` 的差来自发布频率/采样相位，不代表多话题时间戳精确相同；不要跨频率按到达时间拼接观测。

运行元数据：`results/20261003_TASK01_physics_ros_zero_damping_{30hz,20hz}/metadata.yaml`。完整 JSONL/JSON 原始数据保存在各运行 `raw/`，按仓库规则不上传大体积原始流。

最终代码又以 30 Hz 应用帧完整回归一次：120 个运动样本、150 个总位姿样本、位置/角度解析误差与上表 30 Hz 相同，PoseArray 与 JSON 的**位置及四元数**逐样本一致，所有检查 PASS。元数据：`results/20261003_TASK01_final_calibration_30hz/metadata.yaml`。未启动 Isaac 时，记录器在 2 s 启动超时后保存 FAIL 摘要并退出 1（符合负向测试预期），没有把空数据误报 PASS。

## 本轮失败记录（没有隐藏或放宽 gate）

1. 首次 ROS 校准继承系统 `/opt/ros/humble` 的 Python 路径，加载了系统 `geometry_msgs` 与 Isaac 内部 ROS 库的混合组合，出现 type-support 未定义符号。Isaac 的 fast shutdown 还可能让异常只表现为缺失摘要而退出 0，因此**退出码 0 不能独立证明成功**。增加失败 traceback/摘要，并用 `scripts/run_isaac_bundled_ros.sh` 清除系统 ROS 路径。新启动日志确认 `rclpy` 和 `geometry_msgs` 均来自 Isaac 自带 Humble。
2. 干净 ROS 环境下首个外部角度校准失败 `1.649°`：期望模型遗漏了默认角阻尼。显式设校准体阻尼为 0 后通过；不是放宽角度阈值，也不是更改码垛物理。
3. 五 Cube view 首次初始化传入 tuple，但 Isaac 4.5 构造器只支持字符串或 list，启动失败且未执行机器人。改为 list 后再运行。失败 Kit 日志：`kit_20261003_133528.log`。

前两类失败及最初无 ROS 诊断各有独立 `results/20261003_TASK01_*/metadata.yaml`；它们不计入成功次数。

## 复现命令

独立校准终端 A，先启动外部 ROS 只读校验器：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=0
python3 platforms/isaac_ros2/probes/task01_validate_physics_stream.py \
  --timeout-sec 120 --output-dir results/manual_TASK01_calibration/raw
```

独立校准终端 B（不依赖父终端是否 source 过 ROS；脚本清理 Python/库路径）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_pose_timing_probe.py \
  --enable-ros --output-dir results/manual_TASK01_calibration/raw
```

20 Hz 校准增加 `--rendering-dt 0.05`，并为新运行换一个输出目录，避免覆盖上一轮数据。

真实第五块探针终端 A：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_center_headless.py \
  --physics-measurements --duration-sec 600
```

等待 `READY: four physical cubes settled`；终端 B 启动 MoveIt（这里不由 MoveIt execute 管理控制器，Task27 经 Bridge 发布命令）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description \
  moveit_dual_side_suction.launch.py use_rviz:=false
```

终端 C 启动五块的只读物理流记录：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=0
python3 platforms/isaac_ros2/probes/task01_record_physics_stream.py \
  --duration-sec 250 --output-dir results/manual_TASK01_fixture/raw
```

终端 D 运行原有第五块控制任务：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 run fr3_dual_palletize task27_five_cube_center_insert --ros-args \
  -p first_batch:=5 -p max_batches:=1 \
  -p center_pusher_arm:=right -p execution_time_scale:=3.0
```

任务完成、Bridge 仍运行时，读取新通道最终位姿：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=0
python3 platforms/isaac_ros2/probes/task01_capture_final_pose.py \
  --topic /task01/physics/cube_poses
```

## 真实 Task27 第五块运行

同一新通道接入全新五块工装场景后，运行右臂第五块全过程。记录器与控制器独立判断结果：

- **控制任务 PASS**：`Task27 batch 5 PASS`，16 片 +X 推入、最终双臂 HOME，控制节点退出 0；日志时长 `215.142 s`。最终中心误差 `0.520 mm`，后墙间隙 `0.505 mm`，+Y/-Y 相邻间隙 `1.374 / 1.626 mm`，峰值关节驱动力矩 `35.41 Nm`（不是吸盘接触 wrench）。
- **测量记录 PASS**：250 s 墙钟记录窗口内，收到 `14,295` 个五对象物理 snapshot。物理步号 `15766..30060` 连续，无丢失物理步，仿真时间 `262.766680371..501.000026129 s`，时间戳严格递增，四元数单位范数最大偏差 `2.22e-16`，无记录错误。
- `/clock` 收到 `11,554` 条，最近时间戳最大差 `0.066666670 s`。这说明两通道不是每步严格一一对应，不可用到达时间对齐；新 snapshot 内各对象自身是一次同步读取。
- PhysX 最终 Cube 05 中心 `(1.099495411, 0.000126179, 0.260000020) m`，yaw `0.026334°`；旧 Bridge 在相同静止时段给出完全相同的位置，却给出四元数 `(0,0,0,1)`、yaw `0°`。历史转角有效性的更正有实际场景证据，不只来自最小校准。
- 运动中再次捕获 PhysX/USD 位置差 `2.836 mm`；保持旧控制逻辑也能完成任务，但这不使旧动态测量自动有效。
- 测试后主动停止本轮 Isaac/MoveIt。Isaac 退出 0，但 SIGINT 下未获得发布器最终清理计数，不能单靠该退出码宣称生命周期完全干净；MoveIt 本轮是 SIGINT `-2`，未复现此前 `-11`。BUG-004 保持 OPEN，不能从一次不同退出路径推断已修复。

原始控制日志：`/home/ubuntu2004/.ros/log/task27_five_cube_center_insert_32050_1791006079693.log`；Kit 日志：`kit_20261003_133640.log`。运行元数据与选定摘要：`results/20261003_TASK01_fixture_physics_channel/`。记录器随后补充零样本/非法输入时的明确失败摘要与步号间隙统计，不改变测量源或本次实测数据。

独立校准中移除尺度的 USD 姿态近似匹配 PhysX，不表示 USD 能替代物理传感：它仍有帧更新滞后，真实 Cube 的极小转角读数也不能据此保证。新通道始终读取 live PhysX 四元数，不依赖 USD 修补后的姿态。

这个控制 PASS 不是前四块现场码垛证据，也不是新通道参与闭环控制的证据；控制器仍使用旧 Bridge。

## 尚未完成

- 新通道尚未替换旧消费者，也没有 synchronized TCP/wrench/车厢 frame 的完整契约。
- 接触 wrench 的标定与接触拓扑验证仍缺失；关节 effort 不是吸盘 wrench。
- MoveIt 控制任务后的 Ctrl-C 析构异常仍为 BUG-004，不能宣称整个生命周期稳定。
- 前四块直接预置、OMPL 种子未固定，不能当作全五块 benchmark/可靠性证据。
- `benchmark_v1.yaml` 的 36 个未定字段保持原样；需完成数值评审与确认再推进 TASK02/论文基线。
