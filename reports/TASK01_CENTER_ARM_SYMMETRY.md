# TASK01 Cube 05 单臂推进对称性探针（2026-09-30）

状态：**左右单臂各一次 Isaac 物理探针通过；不是 benchmark_v1 冻结或 P2/P3 复现结果**。

## 目的与范围

按用户要求，将 Cube 01–04 直接放在 Task27 的四个最终格位，只运行 Cube 05 的到料、双臂紧协调预推、释放和单臂 +X 插入。分别让右臂和左臂承担最后的推进；另一个机械臂在单臂推进阶段不接触 Cube。这样不必重复执行前四次完整码垛，但仍使用真实 Isaac 物理、Task27 ROS Bridge 与 MoveIt/FCL。

这个预置四块的工装属于 **[EXPERIMENTAL]** 快捷测试，不能声称已经验证 Cube 01–04 的现场放置。两臂的末端/目标几何对称，也不意味着 IK 分支、关节限位、轨迹或接触力学必然相同。

## 可复现运行方式

终端 A（干净终端，不预先 source ROS）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
/home/ubuntu2004/isaacsim-4.5.0/python.sh \
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

将 `right` 改为 `left` 做第二次。只规划检查可额外传 `-p planning_only:=true`，此模式不发布机械臂、吸盘或到料命令。

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

这两次结果支持**固定场景下两臂都能执行第五块**，而非统计意义上的等效；左右结果存在实际差异。

## 科学边界与待办

这是一轮两臂可行性探针；一次成功不能证明稳定性、长期可靠性或左右在统计上等效。还需要相同初始条件下左臂物理结果、重复试验、实际六自由度 Cube 位姿及接触力/力矩记录。当前桥没有末端接触 wrench，不能把关节驱动力矩当作吸盘接触力。TASK01 仍为 `IN_PROGRESS`；36 个未定字段也尚未冻结。

源码：`platforms/isaac_ros2/probes/`；旧工程测试补丁：`ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp`。运行元数据见 `results/20260930_TASK01_center_right_physical/` 与 `results/20260930_TASK01_center_left_physical/`。
