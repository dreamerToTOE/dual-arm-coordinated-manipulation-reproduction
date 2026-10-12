# TASK06-IS-A — 现有场景只读适配与离线审计交付

日期：2026-10-12。**TASK06-IS-A：部分完成；停止，等待用户审查。**
没有合格场景路径，不能报告“无执行规划适配初步验收通过”。

## 1. 来源与验收边界

- 规划基线：`eb8586511419940f1dce8a7e667fffa52a21cf82`。
- 工作分支：`task06-is-a-p4-scene-adapter`。
- 任务前报告、资产复用与协议先提交为 `462e6b1`，实现提交为 `a7223e3`。
- 固定旧工程：[Task26@631b1f6](https://github.com/dreamerToTOE/dual-arm-embodied-palletizing/tree/631b1f65656d025c1bb2173e874192f3fe4d355a)。
  两项获批准的软件修正版本：`5ed0c967401e5fedb93b938e1c3904f4a4c87600`。
  本地只读工作树：`/home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation`。
- 已接受的基础证据：[旧批次两件运行审查](TASK01_PREDECESSOR_PATCHED_RUNTIME_REVIEW.md)、
  [原始初始快照](../results/20261009_TASK01_predecessor_patched_runtime02/initial_snapshot.json)、
  [原始最终快照](../results/20261009_TASK01_predecessor_patched_runtime02/final_snapshot.json)、
  [原始物理日志](../results/20261009_TASK01_predecessor_patched_runtime02/physical.log)。
- P4 模型来源：[不可变模型说明](../tests/fixtures/task03/README.md)；环境输入仍是
  [早期单 Cube 几何归档](../results/20261007_TASK01_full_single_cube_geometry01/config_at_run.yaml)。
  该环境归档不等于后经 D041 接受的 Task26 基础场景。
- 旧基础验收是 batch 1 的 deep/shallow **两件**工程执行，不是单 Cube 正式科研基准验收。
  本轮既不重验旧执行，也不把它改写为 P4 物理实验。

[任务前报告](TASK06_IS_A_PRE_TASK_AUDIT.md) ·
[预声明协议](../configs/engineering/task06_is_a_scene_adapter_v1.json) ·
[静态来源与原模型字段读回](TASK06_IS_A_SOURCE_READBACK.json)。

## 2. 既有资产复用

| 分类 | 使用方式与资格 |
| --- | --- |
| 直接复用 | 原 TASK03 `C/Jc`、FR3 FK；TASK04 Newton–SVD；TASK05 RBS；TASK06 双向约束搜索；TASK02 元数据/文件日志，不复制或改算法 |
| 薄适配 | 新只读常量/来源审计、端点门禁，C++ 通过原 `DualFr3Model` / `CollisionAdapter` / `p4::plan` 接口连接；不新建碰撞引擎 |
| 对照证据 | 原 URDF/SRDF、旧 Task01 日志/快照、原 TASK03–06 报告与所有负面结果，只读保存 |
| 仅供参考 | 旧 scene、bridge、Surface Gripper、导轨、双臂同步执行、shared_object_planner 和冲突检测器；不加载/移植或发送命令 |

旧通用 shared_object_planner 的顶部吸盘 TCP 和额外 tool–Cube 接触许可不移植到侧吸 P4。
成熟 Task26 控制链不重新实现。新适配器目前是**编译与数据门禁已验证的接口骨架**，
不是已经完成端到端现有场景规划的可运行成功版本。

## 3. 场景／模型逐项对照

以下 m/rad 为单位；四元数顺序均为 xyzw。来源简称：

- **S**：旧 `isaac/scripts/task26_truck_box_scene.py`，631b1f6 与 5ed0c96 相同。
- **B**：旧 `isaac/scripts/task26_truck_box_bridge.py`，两版本相同。
- **U/T/R**：旧描述包 `dual_fr3_side_suction.urdf.xacro` / `dual_side_suction.xacro` / SRDF。
- **C**：旧 `task26_truck_box_push_in.cpp`，使用获批准的 5ed0c96。
- **H**：上述已接受的 Task01 两件历史证据，仅旧异步工程快照。
- **P**：TASK03 的不可变展开 URDF/SRDF、TASK05 的原 FCL 适配器、早期环境归档。

### 3.1 关节、世界系、基座与导轨

有序 14q 明确定义为：

```text
left_fr3_joint1, left_fr3_joint2, left_fr3_joint3, left_fr3_joint4,
left_fr3_joint5, left_fr3_joint6, left_fr3_joint7,
right_fr3_joint1, right_fr3_joint2, right_fr3_joint3, right_fr3_joint4,
right_fr3_joint5, right_fr3_joint6, right_fr3_joint7
```

来源：U、P 和新 `JOINT_NAMES`。左右原 USD articulation 各只有本臂关节名；
旧 bridge/ROS joint-state 前缀负责区分两臂，不能按单臂同名数组混排。
导轨位移不属于这 14 个优化变量，必须另带基座/世界状态。

| 项 | 已确认的源码／历史值 | 与 P4 的关系／缺口 |
| --- | --- | --- |
| 世界系 | `world`；位置 m、关节 rad，Cube/TCP ROS pose 的 header.frame_id=world，S/B/C | P 是同名固定世界系；没有新实时世界测量 |
| 左基座初始 | `(0.650,-0.600,0)`、无旋转，S/U；H 初始 rail=.650 | P 归档同值；实际搬运端点状态未保存 |
| 右基座初始 | `(0.650,+0.600,0)`、无旋转，S/U；H 初始 rail=.650 | P 归档同值；本轮不认证 PhysX 与 URDF 全模型等价 |
| 导轨范围 | 左右 X 均 `[.450,1.050]`，Y 固定 ±.600，S/B | 科研 A 固定站位是源码 .650；不扫站位 |
| B 阶段移轨 | 旧流程基座 X=.750，`g_world_shift_x=+.100`，C；H 最终 rail=.750 | 仅记录旧工程坐标变换，不执行 handoff、不作为 A 起终点 |
| 移轨后的模型系 | C 的 world pose 输入 X 减 `g_world_shift_x`；基座 URDF 仍以 .650 固定 | A shift=0；不能把最终 .750 HOME q 偷换为 .650 持件构型 |
| link7→link8 | 固定平移 `(0,0,.107)`，无旋转，P/原 FR3 宏 | 不是工具 TCP 偏移；link8 是工具安装参考 |

原生位置限位来源：原 Franka FR3 描述及 S 的
`FR3_OFFICIAL_JOINT_LIMITS_RAD` 对 NVIDIA USD 的明确覆盖；P XML 同字段。

| joint i（左右相同） | lower rad | upper rad |
| --- | ---: | ---: |
| 1 | -2.9007 | 2.9007 |
| 2 | -1.8361 | 1.8361 |
| 3 | -2.9007 | 2.9007 |
| 4 | -3.0770 | -0.1169 |
| 5 | -2.8763 | 2.8763 |
| 6 | 0.4398 | 4.6216 |
| 7 | -3.0508 | 3.0508 |

该表是静态读回，不是本轮成功运行原生模型限位审计。来源门禁提前停止，
完整 xacro 展开逐字段等价检查和 native loader 都**未执行**。

### 3.2 侧吸工具、TCP 和固定抓取方向

| 项 | 原定义与来源 |
| --- | --- |
| 工具安装 | `side_suction` 固定挂在本臂 link8，安装变换为单位阵，U/T/S |
| 竖杆 | 尺寸 `.028×.028×.080`，中心 `(0,0,.040)`，T/S |
| 横杆 | `.018×.130×.018`，中心 `(0,±.065,.080)`，T/S |
| manifold | `.070×.014×.070`，中心 `(0,±.138,.080)`，T/S |
| 四杯 | 半径 .010、长度 .010；中心 X=±.024，Y=±.150，Z=.056/.104，T/S |
| 左 link8→TCP | 平移 `(0,-.155,.080)`，yaw=`-π/2`，T/P |
| 右 link8→TCP | 平移 `(0,+.155,.080)`，yaw=`+π/2`，T/P |
| 吸附命令几何 | Cube 面中心 Z 对齐；左右名义 1 mm gap；C `sidePose` 指定 TCP 的局部 +X 分别朝世界 +Y/-Y |

固定变换方向统一写成 `^A T_B`，把 B 系坐标变到 A 系。
`^W T_TCP(q)=^W T_base · FK_base→link8(q) · ^link8 T_TCP`。
名义 Cube 姿态为单位旋转时，从 C 的 sidePose 和间隙推导的候选抓取为：

```text
^O T_TCP_L: p=[0,-.061,0], quat=[sqrt(.5), sqrt(.5),0,0]
^O T_TCP_R: p=[0,+.061,0], quat=[sqrt(.5),-sqrt(.5),0,0]
G_L/R = ^TCP_L/R T_O = inverse(^O T_TCP_L/R)
^W T_O,L/R(q) = ^W T_TCP_L/R(q) · G_L/R
```

TASK03 的 C/Jc 使用 `G=TCP→Cube`，不是把 object→TCP 直接右乘 FK。
这些**名义命令抓取**与 P 的历史候选定义相同；不等于已测量的真实 Surface
Gripper 附件相对变换。H 保存的是 x/z/gap/tilt 标量诊断而非完整双方固定变换；
实际搬运 START/PRE_PUSH 的 attachment transform **尚未确认**，本轮不拟合/校准。
原 TASK03 历史闭合精度失败及 TASK04 原抓取诊断结果全部保留，不借适配改门限。

### 3.3 Cube、车厢、桌面及其他障碍

| 项 | 旧 Task26（S/C/H） | P4 历史 FCL 输入（P）／结论 |
| --- | --- | --- |
| Cube | `.120×.120×.120`、.800 kg；Dynamic；slot A=(.500,0,.260)，slot B=(.350,0,.260) | 尺寸/质量相同；不证明同一持件关节状态 |
| 桌面 | 中心 `(.550,0,.100)`、尺寸 `(1.500,.800,.200)`、顶 Z=.200 | 相同；本轮只做来源比较 |
| 车厢 | -X 开口、+X 深墙、±Y 墙、无顶；底面为桌面 | 拓扑相同，不代表几何完全相同 |
| 内部 X | `[.910,1.160]` | 相同至序列化精度 |
| **内部 Y** | **[-.314,+.314]，宽 .628** | **[-.303,+.303]，宽 .606；不匹配，立即停止** |
| 墙厚/高度 | .020 / .150，Z 顶=.350 | 归档同值；Y 不匹配先触发停止，后续自动门禁未运行 |
| 深墙 | 中心 `(1.170,0,.275)`、尺寸 `(.020,.668,.150)` | 归档重建深墙 Y 尺寸 .646，不相同 |
| ±Y 墙 | 中心 `(1.035,±.324,.275)`、尺寸 `(.290,.020,.150)` | 归档墙中心 Y=±.313，各相差 11 mm |
| 原 MoveIt launch 桌对象 | `task24_table`：中心同上，尺寸 `(1.200,.800,.200)`，旧 launch | C 再加 `task26_table` 更大且未移除该 ID；属于原运行中的重叠静态表示，P 模板没有复原全部 world IDs |
| 其他 Cube | Task26 共 4 件，batch 1 来料两件；搬 Cube_01 时 Cube_02 仍可能在 slot B；后批休眠件 Z=-5、gravity disabled | 原 TASK05 模板只载一个附着 Cube、table、三墙；**不是完整两件基础场景**，不能忽略待料件后声称同场景通过 |
| 导轨、标记 | 导轨可视轨道/台车、stage markers 按 S 无 collider | 仅记录，不新增障碍或 collision exemption |

以上墙中心/尺寸是按原 S/C 的公式静态计算，不是运行 FCL/PhysX 得到的测量。
静态值与 SHA256 在 [读回 JSON](TASK06_IS_A_SOURCE_READBACK.json)；完整 48 条
原 SRDF disabled pairs 同文件可查。原有同臂 Adjacent/Never/Default 许可保留；
没有扩大 inter-arm、robot–world 或 tool–Cube ACM。原 TASK05 的 carried Cube
按左 TCP 固定附着并保留原碰撞许可，不导入旧控制器的额外接触过滤。
合法理想杯面接触与真实穿透由原后端/许可关系处理，不能以吸盘 CLOSED 自动豁免。

### 3.4 搬运 A 起终点：命令定义不等于持件测量

| 状态 | 名义 Cube center（world m） | 来源／资格 |
| --- | --- | --- |
| 供料 | `(.500,0,.260)` | S slot A；这是桌面来料，不是已离桌 START |
| 共同抬起后 | `(.500,0,.540)` | C 源码 Z+.280；H GT 三位小数约 .539；实际 14q/TCP/附件未保存 |
| 下降前 entry | `(.770,+.060,.540)` | C `entry_x=pre_push.x-.020`，对 deep 第一件 |
| 共同下降 | `(.770,+.060,.280)` | C `.020` release gap；不是桌面 PRE_PUSH |
| 带件短推终点 | `(.790,+.060,.280)` | C `COMMON_SIDE_SHORT_PUSH`；H 仍双 CLOSED；缺完整 14q |
| 源码任务 pre_push | `(.790,+.060,.260)` | task26_r0_deep 名义字段；不能混成上一行 |
| 实際落桌步骤终点 | `(.770,+.060,.260)` | C `COMMON_DROP_TO_TABLE` 使用 entry_x，H GT 对应；本轮不修旧流程 |
| 早期科研 START/PRE_PUSH | `(.550,0,.380)` / `(.790,0,.260)` | D041 前历史设计，仅数学对照；不是旧 Task26 实际搬运端点，不重新启用 |

H 初始完整关节快照：HOME，rail=.650/.650，SG 均 OPEN。
H 最终完整关节快照：HOME，rail=.750/.750，SG 均 OPEN。
四条 `RIGHT_CONTACT final command q=` 只有右臂、四位小数且是命令，不是
共同持件实际 14q。日志中阶段 GT/ATTACHMENT 标量不能反推合格的闭链端点。
因此本轮 `endpoints.start/goal=null`；明确拒绝 HOME、四位命令、历史293q、新 IK
或 refit 抓取替代，实际持件起终点及其阶段定义 **尚未确认**。

## 4. 实现、预声明协议与实际运行

新源码均在薄接口目录，不编辑 TASK03–06 算法：

- [source_audit.py](../platforms/offline_moveit/task06_is_a_scene_adapter/source_audit.py)：
  白名单 AST 读取，不执行 Isaac 脚本；固定 Git/哈希、场景/归档门禁、端点拒绝。
- [native_audit.cpp](../platforms/offline_moveit/task06_is_a_scene_adapter/native_audit.cpp)：
  复用旧模型/FCL/约束搜索入口。`planQualifiedEndpoints` 仅编译连接；没有已批准
  端点时不调用，当前 runner 不接受自行填入端点。本轮未启动该原生程序。
- [runner](../scripts/run_task06_is_a_offline.py)、[8项合成数据测试](../tests/test_task06_is_a_scene_adapter.py)。

协议锁定 462e6b1。条件种子 7/41/20261012 每个最多一次、首条合格即停；原
NR/RBS、600节点/800迭代/20s预算不改。**这些科学搜索均未启用**。

唯一来源验证，测试源码 a7223e3，返回 exit 1：

```text
SOURCE_MODEL_INPUT_AUDIT
Static scene/archive mismatch: carriage_y: [-0.314, 0.314] != [-0.303, 0.303]
```

[failure.json](../results/20261012_TASK06_IS_A_scene_adapter01/failure.json) ·
[summary.json](../results/20261012_TASK06_IS_A_scene_adapter01/summary.json) ·
[metadata.json](../results/20261012_TASK06_IS_A_scene_adapter01/metadata.json) ·
[result.json](../results/20261012_TASK06_IS_A_scene_adapter01/result.json)。
原始结果保留 `ABORTED`；不是 RRT 概率失败，也不是现有场景被证明不可行。
完整 source_audit/native_audit 文件未产生，xacro 等价、原生模型/碰撞清单、
完整端点运行门禁尚未到达，不能将预先声明的 claim_scope 当已完成证据。

独立、一次的**软件检查**（不重跑来源门禁，不加载场景）全部通过：

| 检查 | 结果 | 资格 |
| --- | --- | --- |
| CMake 配置/编译 | exit 0 / 0 | 原依赖和新接口能构建，不证明模型或场景加载成功 |
| 新适配数据测试 | 8/8 | 常量解释、顺序、缺失/伪造端点拒绝等合成接口 |
| TASK02 A/B/C | 72/72 | 既有纯离线数据/指标/日志回归 |
| TASK03–06 CTest | 4/4 目标 | 合成数学测试；不是新增真实 FR3/FCL 验收 |

[软件检查目录](../results/20261012_TASK06_IS_A_software_checks01/summary.json)
保存配置、编译、CTest 完整 stdout；Python 保存初始 raw stdout 与明确标记的
最终观测摘要，**不是完整 Python stdout**，未为补日志重跑。原工作区 overlay
有既存 fr3_dual_palletize/local_setup.bash 缺失警告，编译/测试仍返回 0；未修环境。

## 5. 路径指标与完整性

| 必需指标 | 本轮值 |
| --- | --- |
| 科学搜索 / IK / 原生 FCL 状态查询 / 执行命令 | 0 / 0 / 0 / 0 |
| 合格现有场景路径数 | 0 |
| 起终点闭链、限位；最大位置/旋转残差 | 未计算：没有确认的持件端点 |
| 路径长度、节点数量、规划耗时、最小关节余量 | 未计算；不得填 0 冒充规划结果 |
| 随机种子、实际 RNG | 未设置／未启用；三个条件种子预算未使用 |
| 最小碰撞距离 | 不可用，没有原生查询；不从零接触推断正距离 |
| 模型来源 | 固定旧源码与历史 URDF/SRDF 已列明；完整 xacro/native 核验未执行 |
| simulation time / physics step | null；软件 wall compute 不是科研仿真时间 |

唯一失败运行前后 592 个受保护文件 SHA256 完全相同，包含原算法、原模型/
ACM、benchmark_v1、旧 Task26 适配与历史实验；最终读回仍相同。
[交付完整性与 artifact SHA256](../results/20261012_TASK06_IS_A_software_checks01/delivery_integrity.json)
确认固定旧工作树仍在5ed0c96且无本地改动，新读回的5个旧来源文件哈希均匹配。
原 TASK03 精度 FAIL、原 TASK06 障碍直接连接 PROJECTION_JUMP/整体部分完成
以及所有旧结果不变。最初 5 个未跟踪旧日志留在原位，不纳入提交。

## 6. POST-TASK REPORT

- Task/Status：TASK06-IS-A，部分完成。
- Scientific objective：现有场景可追溯闭链无命令路径。Minimum sufficient evidence：**未达到**。
- Completed：旧资产复用和来源映射；薄接口/日志/拒绝门禁；编译与纯离线回归；
  输入不一致及端点缺失负证据保存。无规划通过或物理成功声明。
- Files changed：新 adapter、runner、tests、工程协议、报告/新结果目录；
  六项持续记录和入口/任务卡，仅增加当前状态、不删历史。
- Commands run：Git status/fetch/新分支/来源读取；单次离线 runner；
  一次 CMake configure/build、8+72 unittest、4 CTest；命令清单见软件元数据。
- Tests/results/key metrics：见第4–5节；输入拒绝不等于算法失败。
- TASK-BLOCKING：Task26 Y/完整障碍信息与 P4 历史 world 不匹配；实际持件
  START/PRE_PUSH 14q、两 TCP、Cube/附件变换及准确阶段定义缺失。
- DEFERRED：TASK02-D 原生时钟/步/reset 认证、Isaac执行/测量、B/C、力控，
  不以此继续扩展当前审计；Benchmark 草案未定稿。
- KNOWN LIMITATION：合成回归/编译不证明真实 FCL、PhysX、附件稳定或连续安全。
- LEGACY：原两件后杯/侧压/导轨控制及原模型对照结果，不重新开发成熟执行流程。
- Attempt budget used：来源核对 1/1；没有修场景/配置后重试，无新种子或 IK。
  软件检查单独一次。Escalation：需要输入路线审查，不因“工程问题”循环修复。
- [ORIGINAL]：P4 已有 NR/RBS/双树算法不变。
- [ADAPTATION]：固定真实 FR3/侧吸与旧世界来源映射，当前资格未完成。
- [ENGINEERING]：只读 AST/Git/hash、拒绝门禁、编译和 TASK02 证据记录。
- [DEVIATION]：未选择普通 MoveIt RRT 替代，没有论文/门限改变。
- [EXPERIMENTAL]：本轮没有新的物理或科研规划实验，只有源门禁和合成软件检查。
- Records updated：STATUS、WORKLOG、EXPERIMENT_LOG、BUGS、DECISIONS、USER_FEEDBACK。
- Open risks：名义 vs 实际 grasp、单件 vs 两件障碍、不同搬运阶段、原生模型
  等价尚未验证；不把较窄历史 world 直接宣称为当前完整环境。
- Recommended next step：请审查是否授权仅在**新适配输入**中引用原 Task26 的
  .628 m 世界（不改旧 scene/历史归档/Benchmark），并指定有证据的 A 端点路线。
  若需实时取得持件 14q/附件，先批准单独最小只读采集；本轮不启动。
- Git：工作分支 task06-is-a-p4-scene-adapter；任务前462e6b1、实现a7223e3；
  本报告与证据提交在其后。旧 5 个未跟踪文件保留。提交后停止；不进入 B/C/TASK07。

**本报告不是用户验收、正式基准定稿或 TASK06 整体改判。**
