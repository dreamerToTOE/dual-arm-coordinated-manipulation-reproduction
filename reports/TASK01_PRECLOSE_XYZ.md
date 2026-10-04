# TASK01 — 吸附前合并 XYZ 有界纠偏

日期：2026-10-04；状态：XYZ吸附前工程验证PASS；五件全流程FAIL（完成1/5，Cube02释放后深墙间隙5.138mm）。TASK01仍未冻结。

## PRE-TASK REPORT

- Task: TASK01，当前独立精准推入工程版吸附前对中。
- Goal: 原门限内修复上一轮 Cube02 X对应偏差3.15mm导致的安全停机，并记录新增耗时。
- Paper method understood as: 基准工程准备，尚未实施P2/P3论文力控；既有前三件D004接触协议差异仍保留，不以demo冒充科学复现。
- Scope: 用户明确同意未吸附XYZ残差合并微调；静止态命令FK/实测FK/IsaacTCP诊断、数学/真实模型只读测试、正常五件实际回归。
- Files expected to change: 上游运行工程preclose_alignment.hpp、独立宏分支、只读probe；本仓测试/分析/报告/六份记录/结果。
- Validation plan: header数学测试→colcon完成→真RobotModel细IK/FCL无命令测试→正常供料五件→旧几何门限/安全停止/耗时统计。
- Known ambiguities/risks: 误差来源尚未完全隔离；三次检查最多两次微调，1mm向量限幅不保证大误差可修；原传感器静止快照非同一步同步；OMPL未固定seed；旧MoveIt teardown问题仍可能出现。
- Need user confirmation: no，用户已明确批准本次XYZ扩展；模型/物理/接触/门限/基准冻结仍不在授权范围。

## 实现

只在 `TASK01_CUBE04_PRECISION_INSERT` 独立分支启用；旧Task26/Task27节点保留原Y残差逻辑。对每个杯面，计算 `delta = desired_GT - actual_GT`，按整个位移向量长度限幅到1mm，然后将其累加到上一条命令FK位置。XYZ一次规划/执行，不逐轴重新RRT。复用原细IK、联合FCL与原姿态；滑轨偏移统一到模型坐标，不重复扣除。

合格即吸附，零额外修正动作；最多三次检查/两次微调，失败保持OPEN并停止后续任务。只有两杯均OPEN才准许纠偏，规划后执行前再次检查。保持原2.5mm XYZ对应门限、0.3mm预吸附间隙差门限及全部已放置Cube验收门限，不改变场景/工具/摩擦/质量/ACM/载物动作。

每轮静止检查记录命令FK、实测关节FK、IsaacTCP及差值。实测FK接近Isaac但不同于命令时支持关节跟踪残差解释；若FK与Isaac不同，则需继续查模型/坐标/时间合同，不能宣称已隔离原因。单一读取每侧GT仍不是硬同步，不作动态测量合同证明。

计时拆分 `plan_wall_s`、`execute_wall_s`、`total_wall_s`，总项含复测等待/诊断。真实模型probe直接调用同一细IK实现，不发送joint/suction命令。

Fidelity：[ORIGINAL] 尚无论文方法；[ADAPTATION] 当前FR3/TCP/滑轨坐标映射；[ENGINEERING] 未吸附XYZ残差修正/测试/计时；[DEVIATION] 不新增接触或门限差异，既有D004差异保留；[EXPERIMENTAL] 固定场景运行，不构成可靠性或基准冻结证明。

上游：https://github.com/dreamerToTOE/dual-arm-embodied-palletizing ，原commit3ee42d2；根未声明统一许可证。本仓只存适配测试/证据，上游补丁均单独提交。

## 验证结果

colcon完成（包69s，总73s）；C++原Y策略及新XYZ向量限幅测试PASS；Python最终22/22 PASS。最初Python新增解析测试暴露日志末尾句点被读成数字的错误，已修复正则并保留失败记录，不涉及机器人逻辑。

真实MoveIt RobotModel只读probe exit=0：左右合并XYZ细IK各0.707mm/9点，联合FCL25样本PASS；加入已释放Cube障碍后正确拒绝。原空载退出及真实种子回放也PASS。probe未构造机器人/吸盘命令发布器。物理回归待完成；上一轮失败原始证据保持在 `20261003_TASK01_precision_full_five_01`。

### 正常供料物理运行中间检查点（非最终PASS）

运行 `20261004_TASK01_preclose_xyz_full_01`，runtime f0812a4，原速度scale=5。Cube01已完成batch1，吸附前直接合格，没有纠偏，总检查0.278s。Cube02真正触发两次合并XYZ纠偏：X对应2.012→1.361→0.606mm，Z1.589→1.009→0.451mm，左右间隙差0.879→0.607→0.275mm，原0.300mm门限内通过后才吸附。左杯两次向量均1.000mm，右杯0.702/0.002mm；不扩大限幅或重试次数。两次纠偏规划总0.078621s，执行7.569621s，检查窗口8.414887s（原scale=5慢速执行，非计算延迟）。Cube02后续搬运/最终摆放仍在运行，不把此检查点当作五件成功。

静止日志实测FK与IsaacTCP差约几十微米，命令FK→实测FK仍有毫米级残差；这支持当前误差主要在执行/跟踪侧，但读数不是硬同步，不宣称时间合同/动态模型已全面验证。源码与初期记录均已push；SSH直连被当前网络关闭，命令局部使用已有HTTP CONNECT代理后push成功，未改SSH或系统配置。

### 最终结果 / 原始失败保留

- Runtime f0812a4；reproduction测试源b0dbd86、启动记录8adf617；二进制 `fc5e7f8a340287cc6770c78a7a338d439395a2e1caaec8ee950c8317de615539`。scene/bridge SHA与上一轮完全相同，详见metadata。
- 正常供料，无预置。controller exit1，已完成batch1；Cube02通过吸附前XYZ/吸附/搬运/深墙推入，但在后续最终检查失败。Cube03–05仍在停车位，未规划或执行。不能交付为全流程稳定版。
- Cube01最终cell误差1.576mm，深墙0.871mm/侧墙1.313mm；Cube02推到底墙时0.488mm，最终深墙5.138mm > 原3.000mm门限。侧墙接近零，最终PhysX yaw0.000120deg，不能用斜摆解释或扩大间隙验收。
- 7680稀疏同一步PhysX采样，0采样/完整性错误。controller日志窗口714.408s，sampler815.721s；原推入raw关节力矩峰35.36Nm（不是TCP力）。终止自有headless exit0；MoveIt在主动关停时再次exit-11/关节bridge exit1，与之前相同，不是本次控制器几何失败的起因。所有自有进程已停止。

### 释放阶段只读定位

`release_drift.json`保留从原始同一步PhysX样本提取的状态：sim685.933s侧墙附近时x1.099861（后吸盘CLOSED）；首次双杯OPEN为sim689.933s，x1.099789；sim691.033s首次深墙间隙超过3mm；sim691.133s落到x1.094862并维持至最终。也就是解除后吸盘附近约1.2s，负X移动约4.93mm，且有约2mm临时抬高。

这将问题缩小到侧压完成后的物理释放/接触/退出窗口，尚未隔离是杯面接触回带、压力释放响应、姿态跟踪还是撤离轨迹。不能凭这些稀疏Cube样本宣布具体力学根因。源码仍按既有方式侧压完成500ms后打开后杯，再短清障；未修改这一载物/接触协议。后续需要明确授权诊断和修复该窗口，先增加同一步工具/接触/动作阶段观测，不改变场景、摩擦或门限来规避失败。

### 已使用的完整验证命令

外部ROS终端：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
colcon build --packages-select fr3_dual_palletize --symlink-install \
  --executor sequential --cmake-args -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
ros2 launch fr3_dual_side_suction_description moveit_dual_side_suction.launch.py use_rviz:=false
```

第二个同环境终端，真实模型只读检查：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 run fr3_dual_palletize task01_empty_retreat_probe
```

干净Isaac终端（内建ROS，不source系统Python）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_cube04_headless.py \
  --asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5 \
  --preplaced-count 0 --duration-sec 2600 \
  --output-dir results/20261004_TASK01_preclose_xyz_full_01/raw
```

等正常首件真正ARRIVED/READY后，第三个ROS终端：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 run fr3_dual_palletize task01_cube04_precision_insert --ros-args \
  -p first_batch:=1 -p max_batches:=5 \
  -p center_pusher_arm:=right -p execution_time_scale:=5.0
```

统计命令（本次raw已保留，不要覆盖，下一次用新的run目录）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
python3 -m unittest discover -s platforms/isaac_ros2/probes -p 'test_*.py' -v
python3 scripts/summarize_cube04_precision.py results/20261004_TASK01_preclose_xyz_full_01
python3 scripts/validate_benchmark_candidate.py configs/benchmark/benchmark_v1.yaml
```

## POST-TASK REPORT

- Completed: 合并XYZ有限纠偏、两处OPEN检查、静止FK分解、耗时日志及负例测试；真实模型和一次实际纠偏通过。
- Files changed: 上游3源码文件；本仓header测试、汇总测试/脚本、此报告/六份记录/TASK01任务说明、unit/full run结果。
- Validation: colcon PASS；C++ PASS；22Python PASS；真实模型XYZ/FCL及障碍拒绝PASS；正常五件全流程FAIL/exit1，仅batch1PASS，Cube02后吸盘释放附近退离深墙。
- Paper fidelity: 本轮ENGINEERING/EXPERIMENTAL，不是论文力控；D004前三件差异、实际摩擦0.5/0.5和隐藏质量/时间与力测量合同仍待review。
- Remaining / next: 在原门限下定位释放/接触回带，后续协议或载物控制修改须用户决定；不得把本次XYZ修正推广为全流程稳定。
- Safety: 无场景/工具/摩擦/质量/ACM/门限/载物控制/YAML改动；保护目录未访问或修改；停止全部自有测试进程，历史失败保留。
- Delivery: 运行源码task01-runtime-fixes、本仓记录task01-benchmark-draft；raw本地忽略，analysis/metadata和释放窗口数值随GitHub提交。TASK01 IN_PROGRESS/36nulls，TASK02 TODO。
