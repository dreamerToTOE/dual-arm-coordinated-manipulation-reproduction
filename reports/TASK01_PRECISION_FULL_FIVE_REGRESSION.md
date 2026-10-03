# TASK01 — 当前精准推入版正常五件端到端回归

2026-10-03；状态：**FAIL_SAFE_STOP（完成1/5，第2件吸附前对齐门限失败）**；TASK01 基准仍 IN_PROGRESS，未冻结。

## PRE-TASK REPORT

- Task: TASK01 / D014 Cube04 单臂精准推入 + D015 空载退出修复。
- Goal: 从原正常供料开始实际执行全部五件，补足前轮前三/四件预置夹具的证据边界。
- Paper method understood as: 仍在基准准备，不实施 P2/P3 等论文算法；原 D004 前三件双吸盘同步约束协议尚不能由串行工程 demo 证明。
- Scope: 增加已有测试探针的零预置模式、只读稀疏 PhysX 采样、当前已编译执行器完整回归、记录结果。
- Files expected to change: 本仓 `task01_cube04_headless.py`、汇总器/测试、报告、六份记录和结果；不修改旧工程控制器/场景。
- Validation plan: 单测/语法/原始文件 hash → 全新 headless Isaac 正常供料 → MoveIt → first_batch=1/max_batches=5 → 原门限真实验收 → 保存成功或失败。
- Known risks: OMPL 构型不固定，局部 PASS 不保证完整五件；原材质/隐藏质量/时序测量和 MoveIt teardown 缺陷仍存在。磁盘仅约3.6GB，不增加全频接触大日志。
- Need user confirmation: no；仅测试。若要修改模型、材质、接触方法或门限才能继续，则停止等用户明天确认。

## 实施边界

默认预置3件行为保持；新增 `--preplaced-count 0` 时不预置、不开关重力、不取消原 Bridge 自动批1供料。必须等待原 Bridge 检测第一件实际 ARRIVED 才打印 READY，不使用空集 `all([])`。供料 ARRIVED 不算码垛成功；汇总中的全五件完成字段仅由零预置模式和五条实际批 PASS 得到，仍需实际进程退出码/总任务日志交叉检查。

运行旧工程已编译 `task01_cube04_precision_insert`，二进制 SHA256 `77b4f4993c0a5a0cecc82e03c7a671182f384d60576e42e14443d80c78b0866f`；原场景、质量、有效摩擦0.5/0.5、ACM、释放/推入和间隙门限不变。不会将一次完整 demo 冒充统计可靠性、论文协议实现或 TASK01 FROZEN。

## 计划命令（实际执行状态以下文结果/metadata为准）

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_cube04_headless.py \
  --asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5 \
  --preplaced-count 0 --duration-sec 2600 \
  --output-dir results/20261003_TASK01_precision_full_five_01/raw

# 另一个终端
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description \
  moveit_dual_side_suction.launch.py use_rviz:=false

# READY 后在另一终端（同样 source 系统ROS和本项目）
ros2 run fr3_dual_palletize task01_cube04_precision_insert --ros-args \
  -p first_batch:=1 -p max_batches:=5 \
  -p center_pusher_arm:=right -p execution_time_scale:=5.0
```

Fidelity: [ORIGINAL] 论文方法尚未实施；[ADAPTATION] 沿用批准的第四件协议；[ENGINEERING] 正常供料测试与读数校验；[DEVIATION] 已有前三件 D004 差异不隐藏、不新增；[EXPERIMENTAL] 一次固定场景五件试验，非可靠性/冻结证明。

## 实际结果

`results/20261003_TASK01_precision_full_five_01/`，零预置、原正常供料、当前同一二进制。controller exit1，仅 batch1 PASS。Cube02三次吸附前检查失败后停止，未开启吸盘；Cube03–05仍在桌下停车位，没有供料或后续执行。原场景、控制器、材质、模型、ACM和门限未改。

Cube01实际落稳中心误差1.605mm、深墙轴向间隙1.006mm、侧墙轴向间隙1.251mm，原验收通过。之后直接短清障→下一件预吸，无批间HOME。最终PhysX yaw -0.968790°；轴向间隙不是整个面完全贴合的证明。

Cube02三轮原GT检查：

| 检查 | X对应误差 | Z对应误差 | 左/右杯间隙 | 间隙差 |
|---|---:|---:|---:|---:|
| 初始 | 3.027mm | 1.533mm | 2.329 / 0.100mm | 2.230mm |
| 第一次微调后 | 3.145mm | 1.521mm | 1.318 / 0.891mm | 0.427mm |
| 第二次微调后 | 3.150mm | 1.521mm | 0.997 / 0.998mm | 0.001mm |

最终Y间隙差已满足0.300mm原门限，但X对应误差仍超过 **2.500mm** 原门限。`validateDualSideAttachment()` 的X误差取 Cube–左TCP、Cube–右TCP、左右TCP三者的最大值，不只是某个杯面到Cube的单独偏差。

停稳后只读ROS快照左TCP x=0.348959131m、右TCP x=0.352108885m，左右差3.149754mm；Cube02物理x=0.349998832m，仍在供料槽。左右快照不是同一时间采样，只用于静止态交叉核对，不作动态同步精度证明。原 `PRE_CLOSE_REACQUIRE` 分支仅对Y计算累计执行残差；名义X/Z目标再次规划不能证明实际执行X/Z已经纠正。确切误差来源（关节跟踪、模型或测量）尚未隔离，**不能因本轮就认定吸盘几何不可能、场景必须改或力控必须上**。

实际日志：

```text
task27_plus_outer final Ground Truth: ... cell_error=1.605 mm, +X deep wall_gap=+1.006 mm, +Y wall_gap=+1.251 mm.
Task27 batch 1 PASS: Cube 已落稳；双臂从短清障位经 RRTConnect 到下一件上方待命位，未执行长距离原路退出或批间 HOME。
task27_minus_outer PRE_CLOSE_GEOMETRY ATTACHMENT: x=3.150 mm z=1.521 mm left_gap=0.997 mm right_gap=0.998 mm gap_delta=0.001 mm tilt=0.000 deg.
task27_minus_outer cannot establish corresponding dual side contact; do not enable suction.
[ros2run]: Process exited with failure 1
```

7,214稀疏同一步PhysX姿态样本，采样异常/完整性异常0，探针墙钟761.389s；控制器实际日志窗口472.036s。原始最大推入关节力矩35.53Nm，不当作TCP力。实际Cube质量0.800000012kg、有效摩擦0.5/0.5保留。失败后第四件尚未放置，汇总将其邻件间隙设null，不能把桌下停车位坐标差误作负间隙。

本轮拥有的Isaac/MoveIt/控制器进程已全部停止。Isaac探针exit0只表示采样正常结束，不表示任务成功。MoveIt退出再现-11，joint-state bridge因关闭时ExternalShutdownException退出1，均记录在teardown日志，不误归因于Cube02吸附前失败。

一次 `ros2 topic echo` 未写消息类型的右TCP诊断失败于发现类型；显式 `geometry_msgs/msg/PoseStamped` 后只读采样成功。不是控制器或吸盘故障，也没重启/修改控制节点。

## 下一步 / 明天决策边界

保持失败，不进行“重试直到PASS”筛选，也不自行放宽2.5mm对齐门限或换场景。建议下一轮先只读比较实际关节FK与Isaac TCP，并讨论将现有未吸附残差修正覆盖XYZ；这是对当前控制修正范围的扩展，本轮没有实施。若误差来自模型/物理/测量，先确定来源和修正范围，不能直接用补偿掩盖。

同时仍需要用户 review：实际有效摩擦0.5/0.5还是旧文档0.90/0.75作为候选、保留隐藏手爪质量的模型合同、前三件D004双吸盘接触协议，以及36个待批准数值。不会因为局部第五件/第四→第五通过就跳到TASK02或冻结基准。

## POST-TASK REPORT

- Task: TASK01 / 当前已批准精准推入版正常五件回归。
- Status: FAIL_SAFE_STOP；完成1/5，未全流程稳定；TASK01仍IN_PROGRESS。
- Files changed: 本仓测试探针/汇总器/两项测试、报告、六份过程记录、metadata/analysis；旧工程源码未改。
- Commands: 上述三进程命令实际执行；Python unittest21/21、语法、原YAML analytic36nulls、diff/hash检查；只读ROS快照、离线结果汇总。
- Results/metrics: 前述完整实测表/metadata/analysis，保留原始失败日志。源码/二进制hash与前轮一致，OMPL未控制种子。
- Fidelity: [ORIGINAL] 无论文实现；[ADAPTATION] 既有第四件用户批准例外；[ENGINEERING] 测试模式/只读指标与安全停机；[DEVIATION] 既有D004前三件差异仍未解决；[EXPERIMENTAL] 本轮固定场景完整尝试但未完成，非稳定性证明。
- Six records: STATUS / WORKLOG / EXPERIMENT_LOG / BUGS / DECISIONS / USER_FEEDBACK 全更新。
- Risks: XYZ执行偏差尚未隔离、材质/隐藏质量/测量同步/接触协议待审、MoveIt teardown崩溃仍存在。
- Next: 停止测试，明天明确上述纠偏/模型与基准范围后再开始新一轮。
- Git: 本仓 `task01-benchmark-draft` 记录测试/结果；旧工程 `task01-runtime-fixes` 保持3ee42d2及已有不相关未跟踪文件，未改保护目录。
