# TASK01 Cube 05 单臂推进对称性探针（2026-09-30）

状态：**左右单臂各三次 Isaac 物理探针通过；不是 benchmark_v1 冻结或 P2/P3 复现结果**。

## 目的与范围

按用户要求，将 Cube 01–04 直接放在 Task27 的四个最终格位，只运行 Cube 05 的到料、双臂紧协调预推、释放和单臂 +X 插入。分别让右臂和左臂承担最后的推进；另一个机械臂在单臂推进阶段不接触 Cube。这样不必重复执行前四次完整码垛，但仍使用真实 Isaac 物理、Task27 ROS Bridge 与 MoveIt/FCL。

这个预置四块的工装属于 **[EXPERIMENTAL]** 快捷测试，不能声称已经验证 Cube 01–04 的现场放置。两臂的末端/目标几何对称，也不意味着 IK 分支、关节限位、轨迹或接触力学必然相同。

## 可复现运行方式

终端 A（干净终端，不预先 source ROS）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_center_headless.py --duration-sec 900
```

待终端 A 出现 `READY: four physical cubes settled`。终端 B：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description \
  moveit_dual_side_suction.launch.py use_rviz:=false
```

终端 C（同样 source Humble 和旧仓库 workspace；两次物理实验之间必须重启终端 A 的场景/桥，不能在已码垛的场景上直接换臂）：

```bash
ros2 run fr3_dual_palletize task27_five_cube_center_insert --ros-args \
  -p first_batch:=5 -p max_batches:=1 \
  -p center_pusher_arm:=right -p execution_time_scale:=3.0
```

将 `right` 改为 `left` 可做另一臂的独立试验。只规划检查可额外传 `-p planning_only:=true`，此模式不发布机械臂、吸盘或到料命令。

每次重复试验都重启终端 A、B，等待新的 READY，然后运行终端 C。当前 Isaac 4.5 独立 `python.sh` 在干净终端下没有自动设置 ROS Bridge 的 RMW/库搜索路径；上面的两个环境变量指定 Isaac 自带的 Humble 库，没有依赖系统 `rclpy`。省略它们时，本轮首次空场景尝试在 Bridge 启动阶段失败，未发送机器人命令。

## 运行条件与结果

- 旧工程基线提交：`d93f2858ec5345d2234fb3a8b1ec018b9ca5a0de`，外加本次最小测试补丁 `631b1f6`（`center_pusher_arm` 参数、内侧间隙的 100 nm 浮点比较保护）。默认 `right` 不变。运行时该补丁尚未提交，但运行后原样提交；草案 YAML 的旧源码哈希仍指向原基线，不能误当成补丁后的源码哈希。
- 本仓库测试前提交：`76d24dc9226141e761ad779c0d25b4e22f2ed10b`；测试探针和本文是该提交之后的改动。
- `colcon build --packages-select fr3_dual_palletize --symlink-install --executor sequential --parallel-workers 1`：通过。
- Isaac 第一次场景：Cube 01–04 的刚体落稳且各自中心误差均为 `0.000 mm`（按桥发布的三位小数日志）；Cube 05 仍在供料区。
- MoveIt/FCL 只规划：右臂与左臂各自的完整第五块轨迹均通过，且未发机器人或吸盘命令。
- **右臂物理执行：PASS**。双吸盘闭合、抬升、共同运输、下放，随后右臂从 Cube 的 `-X` 面单臂推进 16 片，最终双臂 HOME。最大推入驱动峰值扭矩 `35.96 Nm`；Cube 05 最终中心误差 `0.603 mm`，后墙间隙 `0.586 mm`，与 +Y/-Y 内侧块的实际间隙分别 `1.361 / 1.639 mm`（合计 `3.000 mm`）。双臂搬运期间记录到吸附两侧间隙差 `0.142 mm`、倾斜 `0.086°`。原始 ROS 日志：`/home/ubuntu2004/.ros/log/task27_five_cube_center_insert_170389_1790768859580.log`。
- **左臂物理执行：PASS**。从全新同几何 Isaac 场景重新开始；双吸盘搬运、落台、左臂重抓与 16 片 +X 推进均完成，双臂最终 HOME。推进前曾触发一次 `PRE_CLOSE_REACQUIRE`，不能视作与右臂行为完全一样。峰值关节驱动力矩 `35.87 Nm`；最终中心误差 `0.669 mm`，后墙间隙 `0.633 mm`，与 +Y/-Y 内侧块的实际间隙分别 `1.719 / 1.281 mm`（合计 `3.000 mm`）。双臂共同 X 运输时两侧吸附间隙差 `0.135 mm`、倾斜 `0.046°`。原始 ROS 日志：`/home/ubuntu2004/.ros/log/task27_five_cube_center_insert_175723_1790769635313.log`。

| 指标 | 右臂推进 | 左臂推进 |
|---|---:|---:|
| 完整第五块物理运行 | PASS | PASS |
| 最终中心误差 | 0.603 mm | 0.669 mm |
| +X 后墙间隙 | 0.586 mm | 0.633 mm |
| +Y / -Y 相邻间隙 | 1.361 / 1.639 mm | 1.719 / 1.281 mm |
| 两侧间隙不对称量 | 0.278 mm | 0.438 mm |
| 推入最大关节驱动力矩 | 35.96 Nm | 35.87 Nm |

## 2026-10-02 重复物理试验

在四块预置相同几何、每次全新场景/MoveIt 进程的条件下，追加右、左各两次，合计每臂三次。每次控制节点均记录 `Task27 batch 5 PASS`，并完成 16 片单臂推进、双臂 HOME。下表来自只读解析器 `scripts/summarize_task01_center_trials.py`；位姿来自 Isaac Bridge 的 `/task27/cube_poses`，不是外部测量。

| 推进臂/次序 | 中心误差 mm | 后墙间隙 mm | +Y / -Y 间隙 mm | 峰值关节扭矩 Nm | 原始 ROS 日志文件名 |
|---|---:|---:|---:|---:|---|
| 右 1 | 0.603 | 0.586 | 1.361 / 1.639 | 35.96 | `task27_five_cube_center_insert_170389_1790768859580.log` |
| 右 2 | 0.429 | 0.315 | 1.209 / 1.791 | 37.02 | `task27_five_cube_center_insert_84692_1790936257591.log` |
| 右 3 | 0.374 | 0.360 | 1.402 / 1.598 | 35.47 | `task27_five_cube_center_insert_91674_1790937182531.log` |
| 左 1 | 0.669 | 0.633 | 1.719 / 1.281 | 35.87 | `task27_five_cube_center_insert_175723_1790769635313.log` |
| 左 2 | 0.408 | 0.407 | 1.486 / 1.514 | 35.70 | `task27_five_cube_center_insert_88719_1790936801303.log` |
| 左 3 | 0.561 | 0.392 | 1.099 / 1.901 | 34.63 | `task27_five_cube_center_insert_94437_1790937539749.log` |

原始日志均位于 `/home/ubuntu2004/.ros/log/`。右臂中心误差均值 `0.469 mm`、最大 `0.603 mm`；左臂均值 `0.546 mm`、最大 `0.669 mm`。左右各 `3/3` 通过只能说明这个固定场景的小样本可重复执行，不能推出故障率或统计等效。两侧间隙的最大不对称量右臂 `0.582 mm`、左臂 `0.802 mm`；左 3 的两侧间隙为 `1.099 / 1.901 mm`，因此最终居中程度并非每次相同。左 1 发生过一次 `PRE_CLOSE_REACQUIRE`，其余五次未发生。

新增只读最终位姿采样得到本轮四次的 Cube 05 最终中心分别约为右 2 `(1.099685, 0.000291, 0.260000)`、左 2 `(1.099593, 0.000014, 0.260000)`、右 3 `(1.099640, 0.000098, 0.260000)`、左 3 `(1.099608, 0.000401, 0.260000)` m；右 3/左 3 的最终 yaw 约 `0.020° / 0.014°`。这些是 Bridge 发布的 USD 位姿；没有独立六自由度标定。运行时只读对照发现运动中的 PhysX 刚体位姿与同一步所读 USD 位姿偶有约 `2.8 mm` 的瞬时差值，落稳后位置差为 `0.000 mm`（打印精度）。其原因尚未确定，不能将运动中瞬时 Bridge 位姿直接视为同步接触测量，见 BUG-005。

六次控制任务均成功，但本轮每次在完成后用 Ctrl-C 停止 MoveIt launch，`move_group` 的 `rclcpp::CallbackGroup` 析构过程均再次报 -11；这属于可重复的退出缺陷，不是码垛动作失败，见 BUG-004。OMPL 随机种子未固定；多次成功不是严格同随机种子重复性实验。

这些结果支持**固定场景下两臂都能执行第五块**，而非统计意义上的等效；左右结果存在实际差异。

## 科学边界与待办

### 2026-10-03 测量诊断更正

上述历史 Bridge yaw 数值保留用于原始记录追溯，**不能视为准确的物理转角或六自由度测量**。本轮最小校准确认旧桥直接从带 Cube 缩放的 USD 矩阵提取旋转，所得四元数有确定性尺度污染；同时，运动中的 USD 位置在应用帧更新前滞后于 PhysX。落稳后的位置数值不因旋转提取错误而失效，但运动时刻的姿态/时间指标必须改用经校准的物理通路。详见 `TASK01_PHYSICS_POSE_MEASUREMENT.md`。

上面的启动命令已替换为新干净环境脚本，避免父终端继承的系统 ROS Python 路径污染 Isaac 内部 Humble。可选 `--physics-measurements` 发布新的只读 `/task01/physics/cube_poses`；不改变控制流程。该通路是 TASK01 的测量辅助，不是已冻结的 TASK02 完整公共接口。

这是小样本可行性探针，不能证明长期可靠性或左右在统计上等效。仍需固定种子策略、完成前四块真实放置、带时间基准的六自由度 Ground Truth 与末端接触力/力矩记录。当前桥没有末端接触 wrench，不能把关节驱动力矩当作吸盘接触力。TASK01 仍为 `IN_PROGRESS`；36 个未定字段也尚未冻结。

源码：`platforms/isaac_ros2/probes/`；旧工程测试补丁：`ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp`。运行元数据见 `results/20260930_TASK01_center_right_physical/`、`results/20260930_TASK01_center_left_physical/` 与 `results/20261002_TASK01_center_repeatability/`。
