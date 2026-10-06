# TASK01 — 可见GUI与正常倍率实测

2026-10-06。本轮只做原Task01协议的GUI工程适配及物理回归，不实现论文控制律。

## === PRE-TASK REPORT ===

- Task: TASK01正常倍率GUI测试。
- Goal: 用户可以看到完整原场景和实际运动；先一件，再按结果测试五件。
- Paper method understood as: 已批准前三rear+side主从双推、后两精准单推，非P2/P3方法。
- Scope of this iteration: 可见GUI入口、回环执行客户端、只读诊断与原控制器实测。
- Files expected to change: GUI适配源/测试、六记录、本报告、实验metadata；若发现控制器缺陷，另写有界修复PRE。
- Validation plan: 原模型hash/production SHA核对，63Python测试、画面截图、原反馈与物理日志、真实完成计数和误差。
- Known ambiguities / risks: 正常播放不是100%关节上限；上轮250ms反馈互锁根因未隔离，旧慢速结果不证明新速度。
- Need user confirmation: no。若需要改模型、物理、ACM或保护门限，则停止讨论。

## 可见入口

`task01_gui_fixture.py`明确调用`main(visible_gui=True)`；缺DISPLAY立即报错，
不会转headless。共享历史记录器保持旧源码复现接口，但以后不得直接启动其
headless入口。GUI新增仅观察灯光/相机与127.0.0.1:8226官方Kit VS Code执行器。
原场景、Bridge、物理、摩擦、质量、碰撞体、ACM和保护门限均保持。

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
env ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_gui_fixture.py \
  --asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5 \
  --preplaced-count 0 --duration-sec 3600 \
  --record-release-diagnostics --record-held-diagnostics \
  --physics-fixture-feedback \
  --output-dir results/20261006_TASK01_gui_normal_cube01_run02/raw
```

本入口自动加载原场景/Play/原物理Bridge/同一步原子反馈，不需用户再执行
Editor加载。与ROS终端使用同一个ROS域和localhost设置。

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description \
  moveit_dual_side_suction.launch.py use_rviz:=false
```

另一终端同样source/ROS设置，确认GUI真的显示场景且第一件落稳后：

```bash
ros2 run fr3_dual_palletize task01_dual_suction_fixture --ros-args \
  -p first_batch:=1 -p max_batches:=1 -p execution_time_scale:=1.0 \
  -p dual_fixture_side_roll_world_y_deg:=-15.0 \
  -p dual_fixture_rear_roll_magnitude_deg:=45.0
```

仅连接已启动的GUI/读取或执行显式Kit代码，不另启动仿真：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
python3 scripts/isaac_gui_exec.py --timeout 20 \
  --code "import omni.timeline; print(omni.timeline.get_timeline_interface().is_playing())"
```

## 负启动记录与当前边界

首个`gui_normal_cube01`是可见GUI，但原场景物理/Prim有效而Viewport空网格。
在机器人命令0时尝试渲染重新连接，随后Kit native exit139。保留全部失败日志，
不归因于正常速度或Cube任务。自有未使用的新原型已撤下；没有删除用户源码。

独立`gui_normal_cube01_run02`使用上面SimulationApp可见入口，成功截图显示
双FR3/原L工具/桌面/三墙/第一Cube，真实first feed READY后启动原production。
runtime6bc24ec，binary08f3060ac4d710b5580fad5023ba16bb718df0bfc5505de175bdbcc7a49bd31e。
此时状态RUNNING，最终完成与误差待结果，不能预记物理PASS。

63Python tests通过；原始scene SHA43aa7c2e…、Bridge0f712365…、benchmark
a49d60a4…/36nulls不变。TASK01仍IN_PROGRESS/DRAFT，TASK02 TODO。

## 首件GUI正常倍率负结果

run02按现实墙钟播放：双侧抓取/搬运/下降/释放成功，但接着侧臂重新下降到
双持接触时停止，controller1、完成0、无X/Y段/后续Cube。CONTACT窗口207个
同一步样本，左臂跟踪最大10.108530deg，Cube↔left link8真实接触峰468.823105N，
同一步左J2 raw86.323242Nm超过原80Nm保护。并非有证据的吸盘闭合超时；
原approach_guard未打印停止原因，故最初观察只能说阶段失败，现已更正。
相位标记异步，不能将它当精确控制事件时钟或把raw effort称TCP wrench。

安全双OPEN后剩余驱动目标仍在，已pause可见Timeline避免继续压自由Cube，再
SIGINT正常GUI0关闭/记录flush。6158held/26516atomic/4419sparse完整性零错误；
GUI采样573.024725s。FCL拒绝的其它候选全部保留，不执行；当选规划自由不证明
物理跟踪安全。不据这一未控制IK随机性的运行断言速度或GUI为唯一根因。

## 执行计时软件修复PRE

- Task: 正常倍率可见GUI的轨迹计时适配。
- Goal: 一个规划秒对应一个PhysX秒，而非GUI低于实时仍按现实墙钟发完轨迹。
- Method/scope: [ENGINEERING] 仅Task01同步/单臂下发以已有原子物理时间戳计进度；不改路径、smoothed phase、物理步长、drive、限速或保护。
- Files: runtime共享源码条件分支/fixture impl/policy；本仓库政策单测和六记录/报告/metadata。
- Validation: 重复stamp保持进度、回退拒绝、原250ms失鲜拒绝无wall fallback；串行production build并核对hash后fresh GUI first1/max1/scale1复测。
- Risk/confirmation: side IK/实际几何和正常规划速度仍可能失败；没有单一因果证明。不需新权限；若模型/物理/门限必须改变则停止问用户。

首编译因final hold局部stamp与ROS stamp同名失败exit2/22.3s，保留build.log；
更名并在新独立build02重编译，不在编译中改源码。63Python/政策C++新增物理
进度测试PASS，物理修复结果仍待fresh实测，不从单测推断成功。
