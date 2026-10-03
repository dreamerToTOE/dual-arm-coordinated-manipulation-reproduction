# TASK01 正常供料五 Cube 物理探针（2026-10-03）

最新状态：**修正版旧工程正常五件物理流程 5/5 通过；TASK01 仍 IN_PROGRESS，不是已冻结 benchmark。**

后续受控 hold 已通过机器人流程，但真实瞬时 wrench/速度仍未标定；内件规定的侧吸姿态存在邻 Cube 干涉；实际摩擦 0.5/0.5 与声明 0.90/0.75 不一致。最新证据/方向请求：[评审报告](TASK01_RUNTIME_REVIEW_20261003.md)。没有改工具/材料或将旧流程当 D004 通过。

## 修正后完整五件实测（后续实验，历史失败保留）

- Run: `results/20261003_TASK01_full_five_corrected_01/metadata.json`；legacy fix `d80b6b6`，patch/provenance 在 `platforms/isaac_ros2/legacy_patches/`。
- 初次 build 因新 header include path 缺失失败；补正 CMake 后 build PASS（55.7 s）。9 项 C++ residual assertions PASS；新增分析器 5 项 unit checks PASS。
- 去掉 0.650 mm 最小步长，按实测 residual 修正、最多 1 mm；未吸附微 IK 验证 5 um / 50 urad endpoint、关节范围和 seed 邻域，并继续完整同步 FCL。原 0.300 mm gate/三次停机、几何/质量/摩擦/ACM 保持。
- 仅 Task27 去除 scaled-USD quaternion 提取错误；USD application-frame lag 仍独立存在。官方 asset root 显式指定绕过目录发现故障，引用的机器人资产不变。
- 第一件预吸附左右 gap 差 0.447 -> **0.001 mm**；第二件 **0.287 mm**；第四件 0.973 -> **0.296 mm**。修正未再使该流程在预吸附过冲处中止。
- 真实正常供料、没有预放夹具：`batch 1/2/3/4/5 PASS`，controller exit **0**，双臂最终 HOME。ROS controller wall **1284.391 s**（包含规划/等待），不是按此混合时钟计算的冻结执行时间。
- **70,434** 连续同一步物理记录、0 缺失/倒退/非有限数/跨通道 stamp-step 不一致；dt 实测 0.0166666675359 s。每步 contact normal matrix 重建最大误差 3.05176e-5 N。

| Cube | 结束后 PhysX center error (mm) | 实际 yaw (deg) | 最近深墙平面 gap (mm) |
|---|---:|---:|---:|
| 01 | 1.669 | -0.74091 | 0.447 |
| 02 | 2.276 | 0.00290 | 2.273 |
| 03 | 0.574 | -0.00009 | 0.234 |
| 04 | 0.615 | 0.09111 | 0.384 |
| 05 | 0.563 | 0.08054 | 0.386 |

第五件 controller 当时的 center error 为 **0.493 mm**；后续 PhysX 最后样本为 **0.563 mm**，时间不同，不删掉或混写其中一个。最近角/面到墙距离不是整个面贴合证明。峰值 Cube02-side-wall collision 156.905 N、Cube01-deep-wall 148.364 N，包括瞬态；不是吸盘内力或批准的安全门限。

### 尚未满足用户指定的双臂推压协议（BUG-009）

逐 6 步抽样，前四件都有双侧吸盘 CLOSED 的搬运样本，但 rear + side 同时 CLOSED 的推压样本为 **0**。源码也确认：向深墙推入时 helper 停放；外件再用未吸附杯面侧压、rear suction 保持；内件是 rear 单臂侧向微调。

因此上面的 5/5 是**继承流程工程回归 PASS**，不能误报成 D004 rear 主推/side 吸附约束及角色交换的四件夹具 PASS；TASK01 的数值/接触协议评审与修正仍不能省略。分析器只读，不扩大 ACM、不改机器人或 Cube。

复现使用下文三终端命令；场景命令需加：

```bash
--asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5
```

离线审核完整停止后的记录：

```bash
python3 platforms/isaac_ros2/probes/analyze_full_fixture.py \
  results/20261003_TASK01_full_five_corrected_01/raw \
  --output results/20261003_TASK01_full_five_corrected_01/analysis.json
python3 -m unittest discover -s platforms/isaac_ros2/probes \
  -p test_full_fixture_analysis.py -v
```

## 历史原版结果（未修改原失败证据）

原版状态：**PARTIAL。五批只规划检查通过；真实执行完成 Cube 01，Cube 02 吸附前失败，完整流程未通过。**

## 范围与复现边界

- [EXPERIMENTAL] 旧 Task27 正常五件供料，不预放前四件，不以已成功的 Cube 05 单独夹具代替完整流程。
- [ENGINEERING] 新仓库独立 headless runner 同一 PhysX post-step 记录五个 Cube 位姿/速度、碰撞力/力矩、双臂 link 位姿、raw incoming joint reaction、TCP、吸盘和供料状态。
- [ADAPTATION] N/Nm、world、仿真 stamp/step 显式记录；TCP 使用真实 link8 与旧场景固定工具变换。入口候选 `(0.910, 0, 0.200)` 未发布/冻结公共 TF。
- 执行时新仓库 HEAD `32ccb2b902ab23cd5f60c191d579ff7e2ccc7fe6`，探针为本次未提交变体，详见各 metadata；旧仓库 `631b1f65656d025c1bb2173e874192f3fe4d355a`，tracked scene/bridge/controller/model 本轮不改。
- benchmark YAML SHA256 `a49d60a4dc6a8a00c3bf55a512113af50760968827a8cefe64dae1c7de55fde8`，36 个 null 不变。未加力控、放宽门限或扩大 ACM。
- 不是论文方法、冻结 benchmark 的有效性/可靠性证明；正常五件“demo”与用户指定的接触协议仍需单独核对。

## 完整运行命令

本次无用户 GUI，使用独立 headless。不要同时在同一 ROS graph 启动另一 GUI/控制器。

终端 1：完整正常供料场景，自动加载原 bridge，附加只读测量，无需 Script Editor：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_full_fixture_headless.py \
  --asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5 \
  --duration-sec 1800 --output-dir results/manual_TASK01_full_five/raw
```

等待 `READY: batch 1 feed settled`，确认无 `raw/failure.json`。仅查启动可加 `--verify-only --duration-sec 45`，不执行机器人。

终端 2：保持原 MoveIt 运行：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description \
  moveit_dual_side_suction.launch.py use_rviz:=false
```

终端 3：先五批 planning-only，再在同一正常初始场景真实执行：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 run fr3_dual_palletize task27_five_cube_center_insert --ros-args \
  -p planning_only:=true -p first_batch:=1 -p max_batches:=5
ros2 run fr3_dual_palletize task27_five_cube_center_insert --ros-args \
  -p first_batch:=1 -p max_batches:=5 \
  -p center_pusher_arm:=right -p execution_time_scale:=3.0
```

第一条不发 joint/suction/feed 命令；第二条本次返回 1，不能作为通过版交付。结束先停控制器，再 Ctrl-C 停测量和 MoveIt。`move_group` 的退出异常必须记录。

## 实际结果

| 项目 | 结果 |
|---|---|
| 五批 IK/同步 FCL planning-only | 5/5 PASS，不是五批物理 PASS |
| Cube 01 | 搬运、推入、侧压、短清障、转下一件完成；原控制器 `batch 1 PASS` |
| Cube 02 | PRE_CLOSE_GEOMETRY 三次失败，未打开吸盘，未继续搬运 |
| Cube 03–05 | 未实际执行 |
| 测量 | 37,236 快照，errors=[]；记录完成不等于任务完成 |
| 最后供料状态 | `[2, 2, 0, 0, 0]`；2 是 ARRIVED，不代表放置完成 |
| MoveIt 关闭 | `move_group` -11，栈到 `rclcpp::CallbackGroup::~CallbackGroup()`，BUG-004 仍 OPEN |

对整份 JSONL 的离线完整性复核通过：37,236 行、漏步/步号时间倒退/接触与位姿 stamp-step 不一致/非有限力及 articulation 数组均为 0；最大 normal matrix 重建误差 `1.525879e-5 N`，physics dt 实测 `0.0166666675359 s`，Cube quaternion norm² 最大误差 `4.44e-16`。自包含复核命令和结果在 `results/20261003_TASK01_full_record_integrity/metadata.json`。这不验证 ROS 控制事件的时钟映射或五件物理成功。

### Cube 02 微调过冲（BUG-008）

实际日志：

```text
PRE_CLOSE_GEOMETRY: left_gap=1.153 mm right_gap=2.122 mm gap_delta=0.968 mm
闭环纠偏: left_delta=+0.000 mm right_delta=-0.650 mm
PRE_CLOSE_GEOMETRY: left_gap=1.153 mm right_gap=1.468 mm gap_delta=0.315 mm
闭环纠偏: left_delta=+0.000 mm right_delta=-0.650 mm
PRE_CLOSE_GEOMETRY: left_gap=1.153 mm right_gap=0.815 mm gap_delta=0.339 mm
cannot establish corresponding dual side contact; do not enable suction.
[ros2run]: Process exited with failure 1
```

旧控制器 Task27 左右 gap 差 gate **0.300 mm**。`effective_step` 强制非零纠偏至少 **0.650 mm**，第二次差值只比门限大 0.015 mm，却又走 0.650 mm，越过可接受区间。最后 x/z 对应误差 1.469/1.377 mm 均在原 2.5 mm gate 内，失败项是左右 gap 差，不是 x/z 或 Cartesian fraction。

最后 PhysX 快照独立复核 left/right gap **1.153472816/0.814531370 mm**，差 **0.338941446 mm**，与旧位置日志一致。应修微调最小步长/死区与实际到位反馈，不应放宽 0.300 mm 门限。

源码：旧仓库 `ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp` 的 `validateDualSideAttachment()` 和 PRE_CLOSE_GEOMETRY 中 `effective_step`。本轮只诊断，不改该控制器。

### Cube 01 正确位姿与接触边界

旧控制器：目标 `(1.100, 0.243, 0.260)`，center error **1.792 mm**；以轴对齐中心计算的深墙/+Y gap **1.200/1.332 mm**。

真实 PhysX 最终中心 `(1.098800302, 0.241668463, 0.260000020)`，quaternion xyzw `(0.000000775, -0.000000125, -0.009559591, 0.999954306)`，yaw **−1.095465°**。旧 scaled-USD quaternion 的接近 0° 结果属 BUG-006，不能作真实方向验收。

按有向 Cube 的 world AABB 半宽计算，最近深墙/+Y 平面 gap 约 **0.06355/0.19531 mm**。这是最近角/面到平面的几何距离，不说明整个面贴紧，不能与中心减固定半宽的 gap 混用。

整段 Cube 01—深墙碰撞合力范数 max **139.098 N**，Cube 01—桌面 max **213.447 N**。包含法向、摩擦和落地/推压瞬态，不是左右吸盘内力，没有已冻结安全 gate，也未与控制事件完成同一仿真时钟对齐。不能据此单独判哪一阶段安全/超限。

## 文件、失败与证据

- 新增 `platforms/isaac_ros2/probes/task01_full_fixture_headless.py`。
- `results/20261003_TASK01_full_five_preflight/`：planning-only metadata/summary 与 raw log。
- `results/20261003_TASK01_full_five_physical_v2/`：执行 FAIL metadata/selected summary；raw 的 controller.log、moveit.log、kit.log、topology.json、physics_contact_samples.jsonl 和测量 summary。
- 启动错误 `STATE_READY`（应为 STATE_ARRIVED）、bridge 覆写 namespace 后的 `BOX_INTERIOR_X` 已修正；失败记录保留，均发生在控制命令之前。
- 最后增加 authored incoming joint frame 审计的 `full_fixture_frame_audit` 因 `Could not find assets root folder` 启动失败，无控制命令。此前完整物理记录不能证明新增帧审计通过；FR3 joint-local/TCP 补偿仍待验证。
- 大 raw 约 1 GB 留本机 ignored 目录，不上传；只上传 metadata、selected summaries 和报告。保留负面结果，不清理用户文件。

## 下一步

1. 修预吸附微调过冲，保留原 0.300 mm gate、几何、质量、ACM 和吸盘参数，显式记录控制变体。
2. 正常供料重跑五件；新测量迁移与旧 quaternion 缺陷分别记录，不以预放四件替代。
3. 验证真实 FR3 入关节坐标、重力/惯性补偿、TCP moment 平移及作用方向。
4. 用户评审 36 个待定字段、近不可断吸盘及隐形质量模型，见 `TASK01_FREEZE_REVIEW_CHECKLIST.md`。
5. TASK01 仍 IN_PROGRESS；通过并评审后才推进 TASK02 → P4 → P2/P3，不提前实现力控或论文算法。
