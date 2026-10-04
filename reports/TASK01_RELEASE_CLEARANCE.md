# TASK01 — 侧压后的释放与短退出诊断/修复

日期：2026-10-04；本轮状态：PARTIAL。工程版普通供料五件实际 5/5 PASS；TASK01 基准仍 IN_PROGRESS / 未冻结。

## PRE-TASK REPORT

- Task: TASK01，独立精准插入工程版BUG-016。
- Goal: 在原3mm深墙门限内避免Cube02释放附近退离深墙，保留XYZ修正。
- Paper method understood as: 本轮工程基准准备，不实施P2内部力控制/P3力位混合；不能把前三件原D004协议差异改称已复现。
- Scope of this iteration: 用户“继续”明确同意继续修复释放/退出窗口。先阶段标记+同一步PhysX工具/碰撞接触读数，分离释放与退出，再做依据证据的最小退出/释放修复。
- Files expected to change: 上游独立宏分支/只读probe或策略header；本仓headless记录器及测试、此报告、六份记录、task说明、结果。
- Validation plan: 数学/软件测试→编译→真实RobotModel无命令FCL→实际诊断→修复局部回归→正常供料五件。局部预置或诊断hold不计完整五件PASS。
- Known ambiguities / risks: 既有2deg关节落稳门限可能隐藏受压稳态残差；未知是约束解除、杯面接触还是退出起点错误。诊断阶段消息为异步到达标签，工具/物体/碰撞数据在同一步，不能当作吸盘D6或TCP标定力。OMPL随机、不构成可靠性；磁盘仅3.8GB，避免整个流程full-rate巨量力日志。
- Need user confirmation: no，用户已批准该窗口的最小工程修复；几何/材质/质量/吸盘参数/ACM/门限/论文方法/基准冻结仍不在授权范围。如需此类改变则停止。

## 分类与边界

[ORIGINAL] 本轮无论文算法实现；[ADAPTATION] 复用现有FR3/L工具/PhysX/MoveIt；[ENGINEERING] 阶段观测、同一步读数、有限IK/碰撞检查与测量起点；[DEVIATION] 不新增基准/论文接触差异，既有D004差异保留；[EXPERIMENTAL] 可选主线程短hold或局部预置用于诊断，与普通完整执行区分。

上游 https://github.com/dreamerToTOE/dual-arm-embodied-palletizing ，起始commit f0812a4，根未声明统一许可证；上游修改单独记录。本仓起始59a8095。保护目录不访问/不修改。

## 验证与最终记录

以下按时间保留诊断 checkpoint 与负结果；最后的“最终普通五件物理结果”是当前结论。上一轮完整失败保持在 `results/20261004_TASK01_preclose_xyz_full_01`，不得覆盖。

### 诊断 checkpoint

独立变体 build PASS56.5s/package56.8s/total，runtime b259366/binaryc0939f21...。Python28/28PASS，包括摘要峰值、混步拒绝、非有限位置拒绝。诊断01在启动期BRANCH_SIGN读取失败，无控制器命令；failure.json是权威负证据，Isaac.close导致exit0不能算PASS。诊断02用bridge命名空间取得既有sign，未改scene/bridge。

诊断02 max5为保留Cube02短转场分支，但在batch2完成后主动停止，避免1400s仿真deadline中断后续持件运动。hold3s改变时序，仅诊断；普通默认0未改。第一块观察到OPEN静止hold的Xdelta0.028mm、短退出Xdelta0mm，不复现此前第二块问题，尚不能归因/宣称修复。实际第二块数据待完成。命令、版本和artifact见run metadata。

### 诊断最终结果 / 实测起点修复

诊断02实际未到达batch2完成：Cube02推到深墙，gap1.804mm通过原3mm门限；后续SIDE_HIGH_APPROACH所有候选在t=0因left_fr3_side_suction与当前Cube碰撞0.783mm而拒绝，安全打开并exit1。第一块cell0.946/deep0.497/side0.805mm通过；13227稀疏物理样本/0错误、1617释放窗口样本，Cube03–05未先进。此前Cube02释放回带尚未复现，不能用这次失败给它归因。结束headless时所有杯已OPEN，MoveItteardown-11继续存在。

实际侧压规划混用了PUSH命令终点与Cube实测位姿。失败后的静态ROS杯面后侧间隙约0.267mm（不同时间，不是失败瞬间证明）；因此先复用已有实测seed工程机制。在独立宏分支的实际侧压入口，用同一RobotState取双臂，验证CLOSED背挡/OPEN侧压臂、关节形状/有限/限位、命令差仍在原0.035rad内，然后生成hold seed，当前Cube仍在完整FCL里。预测预检、侧压/释放轨迹目标、旧Task26/27行为均不改。实测碰撞仍拒绝，不扩大ACM/不豁免Cube。runtime2fbfa0b；最终binary6a64fb90...。C++政策单测PASS，Python28/28PASS，完整build62s+最终增量0.44s；实际效果未先行宣称。

下一次正常供料5件，hold默认0，不使用预置；`results/20261004_TASK01_measured_side_full_01/metadata.json`保存精确命令/版本/hash。普通释放窗口继续只读记录，既有BUG-016仍OPEN。

普通测试checkpoint：同一最终binary的真实RobotModel无命令XYZ/空载退路/FCL probe exit0。Cube01实测side-start联合FCL通过，普通releasehold0，最终cell0.678/deep0.670/side0.108mm通过；batch1PASS并到第二件预吸位。第二件仍在运行，不能提前宣称修复Cube02或完整五件。基准analytic checkerPASS/36nulls/hash不变。一次误传checker的`--help`被当作文件名报错，随后按真实文件参数重跑PASS，不是仿真或模型负结果。

### 2026-10-04 后续 PRE-TASK REPORT：空载退出备用路径

- Task: TASK01，Cube02落桌后空载退出。
- Goal: 对比此前成功记录，复用已允许的空载RRTConnect，保留安全拒绝和释放诊断。
- Paper method understood as: 仍为工程基准准备，不实施P2/P3论文控制方法。
- Scope: 独立变体双杯OPEN后，实测起点+原目标，Cartesian和连续seed失败才尝试有限RRT；已释放Cube保留完整FCL，不更改持件路径/侧压/模型/场景/ACM/门限。
- Files expected to change: 上游共享cpp独立宏、无命令probe；此报告、六份记录、结果metadata/摘要。
- Validation plan: 失败日志差异审查→编译/政策测试→四位小数失败seed无命令重放（临时同步PlanningScene须同步恢复）→全新普通供料物理回归。
- Known ambiguities / risks: 此前局部Cube04→05成功时未触发备用IK，不覆盖本次Cube02肘部分支。OMPL不固定随机seed；同步FCL为离散采样，不是连续碰撞保证。复现仍可能发现实测起点碰撞，必须拒绝。
- Need user confirmation: no，用户明确要求继续，空载RRT属既有工程路径复用；科学/几何/物理/门限变化仍需另行确认。

普通measured_side_full_01实际最终FAIL：Cube01完成；Cube02共同落桌并双杯OPEN后，左臂实测seed与命令差0.000681rad/右0.000995rad。4种Cartesian步长fraction均1，但FK直线偏差752–967mm，严格拒绝；连续IK失败118/151段，controllerexit1，后续对象未执行。未到达Cube02侧压/释放，BUG-016尚无修复证明。Isaac在本机后台headless运行，不是GUI验收；用户询问后已明确说明。

空载RRT最终源码runtime df9c2c0，binaryc760d506...；编译55.8s/package56.1s/total通过。每臂最多3个3s候选；数字/限位/实测首点/原MoveIt目标约束检查，复用关节总路程排序，起点及双臂同步FCL保留当前Cube；场景恢复失败不执行。旧Task26/27宏分支不启用此机制。

无命令重放01 exit1：新手写总角度门限拒绝左候选，场景已有对象的严格逐字段恢复比较失败，均保留。重放02按本次实际MoveIt请求的原目标约束判断（不是放宽用户门限），使用正确上一批railshift0.100m，起点Cube模型x0.667925、目标leftx0.690/rightx0.590。exit0：严格FCL1277采样，CLOSED/起点障碍负测试通过，临时同步的6个原本不存在ID同步删除/查询确认。第一次已有对象逐字段恢复问题没有由第二次absent-ID测试证明解决，后续需独立核查；当前实际caller的当前Cube正常被摘除，走已验证REMOVE分支。该重放不发布机器人命令，不构造Arm，但会临时改PlanningScene，不应叫场景只读。旧Cube04/05连续seed重放及XYZ测试仍通过，Python28/C++策略/analytic36nulls通过。

下一轮`results/20261004_TASK01_empty_rrt_full_01`：本机headless全新普通供料0预置，first1/max5/scale5/hold0，实际结果待完成。源码已推上游task01-runtime-fixes。不得用无命令重放替代实际退出或完整五件证明。

正常物理checkpoint（同一df9c2c0二进制，仍运行）：batch1和2已实际PASS；第一块cell1.983/deep1.521/side1.272mm，第二块cell0.807/deep0.800/side0.104mm。两件空载退路均普通Cartesian通过，未触发RRT。前两释放窗口2870条same-step诊断完整性通过，Cube02press末x1.0992638→clearancelast1.0992001，回带约0.0637mm；CLEARANCE_ENTER内CubeXdelta-0.012mm，后臂TCPX-5.734/侧压臂-14.073mm。工具仍有X运动但本次Cube未大幅回带，不能归因“已消除该运动”。phase标签异步、普通OPEN标签最多1step，不构成单独静止释放观察；历史5.138mm失败仍保留/BUG016仍OPEN。第三块正在原流程执行，不能算完整五件。

## 最终普通五件物理结果（2026-10-04）

`results/20261004_TASK01_empty_rrt_full_01` 最终实际完成五个 batch，控制器退出 **0**，双臂回到共同 HOME，最终关节最大误差左 0.059° / 右 0.061°，双吸盘 OPEN。运行在**用户本机的无界面 Isaac 4.5**，不是 GUI、人为观测验收或远程仿真。

| Cube / 顺序 | 中心误差 mm | 深墙 gap mm | 侧墙或邻块 gap mm |
|---|---:|---:|---:|
| 1 / +Y 外侧 | 1.983 | 1.521 | 1.272 |
| 2 / -Y 外侧 | 0.807 | 0.800 | 0.104 |
| 3 / +Y 内侧 | 0.723 | 0.235 | 0.817 |
| 4 / -Y 内侧 | 1.319 | 0.641 | 0.347 |
| 5 / 中央插入 | 0.481 | 0.406 | 1.987 / 1.473 |

第四件精准 staging 的 Y error=0.082 mm（原 0.500 mm 门限），oriented neighbor clearance=0.480 mm，helper OPEN；无第四件 inner trim。最终第四邻缝的轴向中心计算为 0.347470 mm，考虑姿态的投影间隙为 0.236150 mm；后者**不是 PhysX penetration depth**。第五位于实际 `(1.0995935202,-0.0010754584,0.2600000203)` m，yaw=0.068500°。全部最终 pose / quaternion 在 analysis.json。

五次普通空载 Cartesian 退出均经 `RELEASED_CUBE_INCLUDED` 联合 FCL 通过。**本轮没有触发新增空载 RRT 备用**；重放 02 的 1,277 次联合 FCL、CLOSED / 障碍负例和场景清理只证明其无机器人命令路径，不证明真实备用执行、连续碰撞安全或所有冗余构型可靠。原先成功退出与本次成功一致；旧失败构型及 752–967 mm 的不安全 Cartesian 候选仍保留，不能只凭 fraction=1 执行。

Cube02 XYZ 原 gap delta 1.283→0.850→0.219 mm，X mismatch 1.307→0.693→0.186 mm，Z mismatch 1.352→0.775→0.198 mm。三次检查 / 两次合并修正，单臂每次总位移上限仍 1 mm，原门限不变。修正规划 0.069299 s、慢速物理执行 7.418296 s、总 8.303532 s；其他四件不做无必要纠偏。

18,498 个稀疏 PhysX snapshots / 0 integrity errors，3,212 个释放诊断 snapshots。controller 首日志至 batch5 PASS=1,726.184527 s（约 28.77 min），sampler wall=1,940.471278 s（含准备/空闲）；人为慢速 execution_time_scale=5，**不是效率基准**。raw 推入关节 torque peak=32.7 Nm，不是校准 TCP 力，也不包含可识别的吸盘内部力。

本次 Cube02 未发生历史 5.138 mm 回带，最终深墙 gap=0.800 mm。第一、二件同一步释放记录 2,870 条；Cube02 press 末到 clearance 末 X 变化约 -0.0637 mm。工具退出仍有 X 运动，但 Cube 本次没被大幅拖离，**未隔离 BUG-016 的原因**。阶段标签异步、普通 OPEN phase 至多一 step，不能替代独立静止释放观察。BUG-016 仍 OPEN / intermittent。

重放 01 左候选拒绝的具体子原因日志不够，前文“总角度门限拒绝”是当时的推断，不作为已隔离的唯一因果结论。重放 01 已有对象严格逐字段恢复比较失败仍未解决；重放 02 仅覆盖原本不存在的对象同步删除/查询。运行代码在恢复失败时停止，不绕过该保护。

自有控制器/Isaac/MoveIt 全部停止。headless 退出 0，MoveIt 关闭子进程 -11 / joint bridge 1 再现，与完成任务的控制器 0 **分别记录**。控制器/headless shell 退出码来自已完成命令会话，原 controller 日志只直接证明批次与 HOME；不能由 launcher 退出 0 宣称全部子进程正常退出。

### 精确版本与工件

- 运行源码仓库：`dual-arm-embodied-palletizing` / `task01-runtime-fixes` / `df9c2c06ad0667c5fe1f34b573e8ee89657bf8af`，已 push。
- 主控制器 binary SHA256：`c760d506fdc678f8733e2b640aca9de428dd65f6467027ea0df299c521715ad6`。
- 共享 cpp / probe cpp / 原 scene / 原 bridge / benchmark YAML 完整 SHA256 在 run metadata；没有在运行期间改源码或重新编译。
- 本仓最终记录提交在 `task01-benchmark-draft` 分支历史；此前 checkpoint `1e7af81` 已推。metadata 保留启动时源码记录，不用收尾文档 commit 伪装实验起始版本。
- Git 跟踪 metadata.json、analysis.json、release_windows.json、controller_excerpt.txt。大型 raw 日志/JSONL 仅本地保留，不提交。

### 本轮实际启动命令

以下是**本轮已执行命令**。若再次测试，改用新的 run-id / output-dir，不能覆盖现存原始证据。

本机 headless（本轮 stdout/stderr 写入同一 raw/kit.log）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
ROS_LOCALHOST_ONLY=0 scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_cube04_headless.py \
  --asset-root https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/4.5 \
  --preplaced-count 0 --duration-sec 3000 --record-release-diagnostics \
  --output-dir results/20261004_TASK01_empty_rrt_full_01/raw
```

另一个终端启动 MoveIt（本轮日志为 raw/moveit.log）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 launch fr3_dual_side_suction_description \
  moveit_dual_side_suction.launch.py use_rviz:=false
```

Isaac 场景/bridge 已就绪后，第三个终端（本轮日志为 raw/controller.log）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 run fr3_dual_palletize task01_cube04_precision_insert --ros-args \
  -p first_batch:=1 -p max_batches:=5 \
  -p center_pusher_arm:=right -p execution_time_scale:=5.0
```

### 编译、无命令重放和离线检查

运行仓库在测试前已完成相关 package 编译（最终 package 55.8 s / total 56.1 s）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-embodied-palletizing/ros_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
colcon build --packages-select fr3_dual_palletize --symlink-install
source install/setup.bash
export ROS_LOCALHOST_ONLY=0
ros2 run fr3_dual_palletize task01_empty_retreat_probe --ros-args \
  -p run_failed_cube02_rrt_replay:=true
```

上述 probe 需要 MoveIt 已启动，临时修改带命名 ID 的 Planning Scene 并同步恢复；没有机器人/吸盘命令发布器，**不是 Planning Scene 只读**。禁止在真实持件执行期间启动该诊断。记录见 `results/20261004_TASK01_empty_rrt_replay_01`（失败保留）和 `_02`（exit 0）。

收尾再次执行，Python **28/28 PASS**，三项纯 C++ policy **PASS**，JSON parse **PASS**，analytic **PASS / 36 nulls**，git diff --check **PASS**：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
python3 -m unittest discover -s platforms/isaac_ros2/probes -p 'test_*.py' -v
python3 scripts/validate_benchmark_candidate.py configs/benchmark/benchmark_v1.yaml
git diff --check
```

C++ policy 使用 `g++ -std=c++17 -Wall -Wextra -pedantic`，include 指向运行仓库真实 `ros_ws/src/fr3_dual_palletize/include`，分别编译执行 `test_empty_retreat_policy.cpp`、`test_preclose_alignment.cpp`、`test_cube04_precision_policy.cpp`，产物在本地 untracked artifacts 的临时目录，不改源码/不提交。

## POST-TASK REPORT

- Task: TASK01，释放/空载退出工程修复与普通五件回归。
- Status: **PARTIAL** overall；当前工程版一次普通实际完整 5/5 PASS。TASK01 基准仍 IN_PROGRESS。
- Completed: 释放阶段只读同一步诊断；实测侧压入口 seed；有限 OPEN-only 空载 RRT 备用及有限值/限位/首点/原 goal constraints/当前 Cube FCL/同步恢复保护；真实模型无命令失败姿态重放；新鲜零预置五件实际回归；工件、负结果和过程上传。
- Files changed: 本轮上游 `task26_truck_box_push_in.cpp` 独立宏分支、`task01_empty_retreat_probe.cpp`；本仓 release 诊断 headless/分析/测试记录、此报告、六份文档、TASK01 任务说明及结果 metadata/摘要/日志摘录。此前本迭代编译/诊断 checkpoint 的详细变更保留在历史和 git diff。原 Task26/27 模型/场景/控制分支未改。
- Commands run: 上列 colcon、MoveIt、no-command replay、headless、controller、28 Python tests、三项 C++ policy、JSON/analytic/diff；完整 run 配置见 metadata。
- Tests / experiment results: build PASS；replay 01 FAIL 保留 / 02 PASS；CLOSED/障碍负例 PASS；普通 physical completed 1–5 / controller exit 0 / HOME；raw 采样完整性 PASS。备用 RRT 实际触发尚未覆盖。
- Key metrics: 第四 neighbor gap 0.347 mm / deep gap 0.641 mm；第五中心误差 0.481 mm / deep gap 0.406 mm / 两侧 1.987、1.473 mm；18,498 snapshots / 0 errors。其他值、慢速时间及负结果详见上文。
- Paper fidelity [ORIGINAL]: 本轮没有开始论文算法。
- Paper fidelity [ADAPTATION]: 复用现有双 FR3、L 工具、原 PhysX/MoveIt 及用户已批准的第四件精准单后推。
- Paper fidelity [ENGINEERING]: 实测 seed、有限空载规划、安全检查、观测/测试/记录。
- Paper fidelity [DEVIATION]: 未新增模型/物理/门限/接触差异；既有 D014 第四件改动、前三件 D004 差异不因此消失。
- Paper fidelity [EXPERIMENTAL]: OMPL RNG 未受控、四位小数失败姿态重放、一次慢速本机 headless 回归；不可替代稳定性/GUI/力控或论文复现证明。
- Records updated: STATUS、WORKLOG、EXPERIMENT_LOG、BUGS、DECISIONS、USER_FEEDBACK 全部更新；TASK01 说明、run 摘要及 report 一并提交。
- Open risks: BUG-016 历史释放回带未隔离，RRT 备用未物理触发，已有对象恢复严格比较未隔离；MoveIt teardown -11；材质/隐藏质量/接触与时间/力测量及 36 nulls 待用户审查。
- Recommended next step: 用户可审阅这版普通实际演示；冻结基准/进入 TASK02 前先审查现存协议与模型/数值清单。若再做工程回归，使用新 run-id、保留门限，不隐式改场景/力控来保证成功。
- Git branch / commit / dirty files: 上游 `task01-runtime-fixes` / `df9c2c0` 已 push；本仓 `task01-benchmark-draft` 的收尾 commit 见分支历史。raw / build / install / 既有 untracked 用户文件不提交、不删除。所有自有测试进程已停止。
