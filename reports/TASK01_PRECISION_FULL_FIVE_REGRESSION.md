# TASK01 — 当前精准推入版正常五件端到端回归

2026-10-03；状态：IN_PROGRESS，仅工程回归；TASK01 基准未冻结。

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

结果待实际执行完成填写；原始记录不覆盖前轮成功/失败。
