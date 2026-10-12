# TASK06-IS-B0 — 固定 P4 路径执行前审查

2026-10-12；基线 **f0a57c2**；分支 `task06-is-a-p4-scene-adapter`。
预声明协议 **c20c381**，分析源码 **e1a2e22**，唯一正式分析 run01。

## 结论：执行准备条件不满足

原1869点路径仍有合格的**离线闭链、原生限位和离散 FCL**证据，未推翻 A 的
初步验收。但左臂 J4 在第861点（零基860）距上限仅 **0.004119662522 rad / 0.236039°**。
旧执行器接受的终点误差大于它，且没有全程跟踪误差包络。另缺原生加速度限额、
合格共同时间表和实测持件 START 对齐证据。**不得下发本路径执行。**

审查工作已完成；结果文件 `INCOMPLETE` 表示执行资格不齐，不是原 P4 搜索失败。
没有启动 Isaac/ROS/MoveIt 服务、控制器，没有重规划、IK、投影、新FCL查询或命令。
原路径、旧 Task26、模型、ACM、端点、结果与 Benchmark 未改；Benchmark 仍草案。

## 1. 最危险构型

| 项目 | 保存值 |
|---|---:|
| 路径点 | index=860 / 第861点，共1869点 |
| 机械臂/关节 | left / fr3_joint4 |
| 实际路径目标角 | −0.12101966252210423 rad / −6.933915900614° |
| 原生允许范围 | [−3.077, −0.1169] rad |
| 最近边界 | 上限 −0.1169 rad |
| 余量 | 0.004119662522104231 rad / 0.236039275535° |
| 沿关节空间弧长位置 | 49.0706%，不是运动时间进度 |
| 原树证据 | START node62 / attempt61 / checked_point1；与GOAL node32汇合 |

完整14q保存在[summary critical](../results/20261012_TASK06_IS_B0_path_review01/summary.json)，
与原 `planner_seed7.json.gz` 的 meeting q 完全相等，未重新求解。

全部限位余量按 `min(q−lower,upper−q)` 求取；不角度wrap/clamp。
下表显示各关节最危险点，不是所有关节在同一时刻的状态；L/U 表示最近下/上限。

| 关节 | 零基点 | q(rad) | 边界 | 最小余量(rad) | 最小余量(°) |
|---|---:|---:|:---:|---:|---:|
| 左J1 | 860 | 2.372713465 | U | 0.527986535 | 30.251400 |
| 左J2 | 860 | 1.068055966 | U | 0.768044034 | 44.005682 |
| 左J3 | 860 | −1.550686947 | L | 1.350013053 | 77.350050 |
| 左J4 | 860 | −0.121019663 | U | **0.004119663** | **0.236039** |
| 左J5 | 860 | −1.581801157 | L | 1.294498843 | 74.169320 |
| 左J6 | 304 | 1.134229274 | L | 0.694429274 | 39.787867 |
| 左J7 | 0 | 1.292079499 | U | 1.758720501 | 100.767262 |
| 右J1 | 1125 | 0.634848635 | U | 2.265851365 | 129.823720 |
| 右J2 | 860 | −1.225482326 | L | 0.610617674 | 34.985816 |
| 右J3 | 1868 | −1.065130324 | L | 1.835569676 | 105.170395 |
| 右J4 | 860 | −0.481102029 | U | 0.364202029 | 20.867239 |
| 右J5 | 1868 | −0.895006555 | L | 1.981293445 | 113.519752 |
| 右J6 | 0 | 1.133153777 | L | 0.693353777 | 39.726245 |
| 右J7 | 0 | −1.128100119 | L | 1.922699881 | 110.162588 |

只有左J4进入旧容差大小量级：index823–885 共63点余量≤.035rad；
index789–908 共120点余量≤.06rad。它是中间绕行风险，不是起终点违法。

## 2. 累计行程、绕行与连续性

`travel_j=Σ|Δq_j|`；净变化取 `|goal−start|`。
比值用于定位绕行，**端点直线只是诊断参照，不是已证明可行的闭链替代路径**。
方向反转计数忽略零delta；1e-9rad数值过滤仅诊断。本路径原始/过滤计数相同。

| 关节 | 累计行程(rad) | 净变化绝对值(rad) | 行程/净变化 | 反转次数 | 最大邻接变化(rad) |
|---|---:|---:|---:|---:|---:|
| 左J1 | 4.241173 | .521058 | 8.140 | 1 | .003983943 |
| 左J2 | 3.531749 | .473331 | 7.461 | 1 | .004293346 |
| 左J3 | 5.172695 | .402422 | 12.854 | 1 | .005151300 |
| 左J4 | 4.152685 | .430656 | 9.643 | 1 | .004006913 |
| 左J5 | 4.365728 | .127042 | 34.364 | 1 | .004706835 |
| 左J6 | 1.272156 | .868050 | 1.466 | 3 | .002981651 |
| 左J7 | .901676 | .427255 | 2.110 | 2 | .002002874 |
| 右J1 | 1.867521 | .216519 | 8.625 | 3 | .002438712 |
| 右J2 | .774608 | .130825 | 5.921 | 3 | .002440879 |
| 右J3 | 2.296129 | .242425 | 9.472 | 1 | .003263664 |
| 右J4 | 3.690715 | .751010 | 4.914 | 1 | .005315105 |
| 右J5 | 1.448805 | .064901 | 22.323 | 3 | .001815113 |
| 右J6 | 1.635057 | .742759 | 2.201 | 2 | .003456263 |
| 右J7 | 1.892736 | .665792 | 2.843 | 1 | .002666942 |

最大累计行程是左J3（296.374°），左J4累计237.931°却净变化24.675°。
左J5的高比值部分来自很小的端点差，不能仅凭比值判断绝对最大绕行。
全路径14维 L2长度11.940815548rad；端点直线距离1.865774288rad，比值6.399925。
11个关节在树汇合点860反转；全链24次逐关节反转，并非高频抖动/分支跳变证据。
这是首个可行解，原算法没有以最短路径/执行余量作为本轮接受条件。

邻接最大L2=.009923957011rad，出现在832→833；最大Linf=.005315105379rad，
出现在860→861的右J4。均满足原 .01/.01rad门限，没有发现原门限意义下的断裂。
完整10条最大邻接、24个反转位置和1869点14关节余量均保留于JSON/CSV。
小邻接只证明离散数值连续性；没有时间，不能声称速度/加速度合格。

## 3. 曲线和机器可读证据

横轴全部是**原路径点序号，不是时间**；未构造新空间路径或时间轨迹。

- [14关节角度/原限位曲线](../results/20261012_TASK06_IS_B0_path_review01/joint_positions.png)
  （[SVG](../results/20261012_TASK06_IS_B0_path_review01/joint_positions.svg)）。
- [14关节余量曲线](../results/20261012_TASK06_IS_B0_path_review01/joint_margins.png)
  （[SVG](../results/20261012_TASK06_IS_B0_path_review01/joint_margins.svg)）。
  .035/.06线仅是旧终点容差参照，不是已认证动态包络/新Benchmark标准。
- [14关节累计行程](../results/20261012_TASK06_IS_B0_path_review01/joint_travel.png)
  （[SVG](../results/20261012_TASK06_IS_B0_path_review01/joint_travel.svg)）。
- [全部数值表](../results/20261012_TASK06_IS_B0_path_review01/joint_review.csv)、
  [逐点余量/邻接](../results/20261012_TASK06_IS_B0_path_review01/path_points.csv)、
  [方向反转](../results/20261012_TASK06_IS_B0_path_review01/direction_reversals.json)。

## 4. 原闭链与 FCL 资格来源复核

固定path SHA256：`073723b32e4bc392af3fb0a182a03e92e45026771dc1d46fa9b7276b21614781`。
原搜索JSON解压19140034bytes，SHA256
`e6d751833e3d5ba19bd2e23c97a1b0c4ec230ca594c954addc3971d826a0716d`。

25/25原artifact hashes、620/620原source hashes一致（612项对应实际测试提交
c88a80c60b13b39a619b17c1de36bb2a72932364，8项外部原STL）。交付README文档变更
不回写测试metadata。14原生限位与URDF精确一致，四份1869点记录精确对应，
94/94树边的parent/child/attempt/CONNECTED/check点/FCL/leaf资格完整对应。

最大闭链位置8.6252082465342e-9m、旋转5.3077350613721256e-9rad，均满足原1e-8。
全部独立记录FCL complete、self/world clear、contacts=[]；仍是原full-robot
PlanningScene/FCL（含臂间/环境），原SRDF/ACM不改，没有增加吸盘接触许可。
来源：[原独立验证入口](../platforms/offline_moveit/task06_is_a_scene_adapter/nominal_planning.cpp#L303)、
[dense点/树边来源](../baselines/p4_closed_chain/constrained_rrtconnect.cpp#L300)、
[原碰撞调用](../platforms/offline_moveit/task05_local_connection/collision_adapter.cpp#L428)。

最小碰撞距离仍为 **UNAVAILABLE_NATIVE_DISTANCE_NOT_QUERIED**，无连续扫掠或PhysX等价证书。
闭链保证左右预测物体一致，不等于全链物体固定世界姿态。名义离线端点仍不是物理测量。

## 5. 旧 Task26 执行能力审查与复用边界

旧固定631b1f6，批准软件修正5ed0c967401e5fedb93b938e1c3904f4a4c87600。
两者差异仅原控制器13行FK生命周期/既有整链预检修正，以下模块不改。

源码链接：[Task26 controller](https://github.com/dreamerToTOE/dual-arm-embodied-palletizing/blob/5ed0c967401e5fedb93b938e1c3904f4a4c87600/ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp)、
[bridge](https://github.com/dreamerToTOE/dual-arm-embodied-palletizing/blob/631b1f65656d025c1bb2173e874192f3fe4d355a/isaac/scripts/task26_truck_box_bridge.py)、
[launch](https://github.com/dreamerToTOE/dual-arm-embodied-palletizing/blob/631b1f65656d025c1bb2173e874192f3fe4d355a/ros_ws/src/fr3_dual_side_suction_description/launch/moveit_dual_side_suction.launch.py)。

| 能力 | 来源与实际语义 | B0资格 |
|---|---|---|
| 关节命令 | controller836–870/1139–1153；/left,right/joint_command，JointState，仅position；strip前缀为fr3_joint1…7 | 可复用；P4左1…7右1…7按名称拆分 |
| 同步下发 | executeSync1324–1378，一个调度线程、steady_clock/墙钟10ms、同stamp；bridge627–680/699按stamp成对写ArticulationAction | 现有工程通路可复用，不新建执行器；非认证physics时钟 |
| 共同相位 | s=3u²−2u³，左右各用s×自身时长；interpolate479–513线性关节插值 | 本路径必须共享每点时间/对应索引，不能独立retime两臂 |
| 到位 | controller160–179/1170–1227；普通.035rad；稳态残差.06rad、max-error变化≤.002rad×5；timeout25s | 终点检查，不是全程误差包络；稳定max-error不等于认证各关节速度为零 |
| 末端保持 | 200×墙钟10ms，共约2s；随后到位判断 | 工程保持，不是物理仿真时间/动力学证书 |
| 原规划缩放 | controller1298–1299速度/加速度请求各.12；默认time_scale3，禁止<1 | 不自动适用于P4任意输入点列；本轮不设执行速度 |
| 持件 | controller4381–4443预检LIFT→双ON→实际CLOSED(3s)→对应几何复核→更新实测Cube；每stage复核CLOSED/几何 | 不把ON命令当ATTACH；原SG/D6只复用，不改参数 |
| 释放 | 落桌后双OPEN确认；2653–2668等待OPEN6s | GOAL短推释放前仍须双CLOSED，不提前释放 |
| 起点 | scene414–426只HOME；原snapshot两SG OPEN、rails.65/.65、Cube桌面(.5,0,.26) | 不等于新START完整14q/持件状态，禁止HOME直接跳首点 |
| 读取资格 | bridge805–812工程USD/CLOSED反馈 | 原TASK02-D同步post-step认证仍暂缓，不冒充正式测量 |

旧共同LIFT/SHORT_PUSH日志证明确实双CLOSED，**不证明 q 等于离线START**。
旧执行器main也没有本P4 JSON输入口；未来只能薄适配其现成executeSync，不在本轮开发。

## 6. 来源驱动的余量与跟踪要求

执行必要误差预算（每关节、朝最近限位的最坏方向）应满足：

\[
m_j>E_{tracking,j}+E_{alignment,j}+E_{model,j}.
\]

误差项必须可追溯，不能用RMS、均值或终点观察代替全过程上界。
旧普通终点容差.035rad=2.005352°，稳定残差.06rad=3.437747°，分别为当前
最小余量的8.495842/14.564300倍。若复用原“可接受终点误差包络”作保守参考，
余量需要严格超过 **.06rad加其余误差预算**；这只是源驱动参考必要条件，
不是已认证的运动包络，也**不冻结为Benchmark门限**。

原实际日志LIFT终点left.161°/right.192°；SHORT_PUSH .108°/.148°，另一侧压阶段
left.708°已大于.236°。来源[physical.log](../results/20261009_TASK01_predecessor_patched_runtime02/physical.log)
271–274/299–302/1188。这些是旧路径各臂最大误差，未说明是哪一关节、误差方向、
瞬态最大值；**不能据此宣称本路径已经越界，也不能宣称本路径安全**。

保留本路径须先证明全程总误差小于.004119663rad；当前无此证据。
不将旧到位容差临时调低来替代证明，不更改原限位/P4数值精度。

## 7. 时间参数化资格：本轮不构造时间轨迹

1869点没有执行时间。**.213194502s是原规划计算耗时，不是运动时长**。
可复用旧时间缩放/线性插值/同步发布结构，但当前没有合格赋时输出：

1. ensureTiming411–436无时间时按.03×index兜底，不校验关节v/a。
   synchronize1381–1408仅缩放时间；共同14q若采用完全相同的时间点拆分，
   位置配对可保留。共同三次相位仅保证整体首尾零速度，内部折点仍可能速度跳变。
2. shared_object_planner.cpp95–209按两臂各自TCP长度重新采样；会改变本已认证
   14q点列/对应关系，不能直接套用以声称“只加时间”。
3. 原URDF/本机FR3 joint_limits.yaml给每臂速度上限
   `[2.62,2.62,2.62,2.62,5.26,4.18,5.26] rad/s`，有来源。
   position_based_velocity_limits.deceleration_limit不是认证的通用加速度上限。
   原launch未载入完整加速度覆盖；[旧moveit.log](../results/20261009_TASK01_predecessor_patched_runtime02/moveit.log)
   第141行明确实际使用默认1rad/s²，不是已审查FR3物理加速度限额。
4. 旧launch使用AddTimeOptimalParameterization，但P4不走原MoveIt流水线。
   本机TOTG头167–175默认path_tolerance=.1、resample_dt=.1、min_angle_change=.001；
   不可将这种可重采样方法直接认定为严格不变空间路径。未调用TOTG/IPTP。

本机配置/旧source/日志的完整hash保存在本run metadata。外部FR3包HEAD
02afaae282d4a8e10d7d2f781b23b3515c303ce5是本机依赖，不伪称固定旧repo自有文件。
时间参数化即使以后通过，也不会增加关节余量，不自动证明连续无碰撞/吸附稳定。

## 8. 待用户决定的独立路径改进建议（本轮未执行）

优先先解决空间绕行与余量，不直接依靠放慢速度：另行预声明一个独立 P4 路径
质量/执行裕量实验，保留当前路径为原始证据，模型/场景/ACM/端点/闭链数值精度
不变。可审查路径筛选或经原TASK05验证的约束捷径是否减少860附近绕行，
执行裕量条件从上述误差预算明确后再登记；如新增捷径需作为工程后处理单独
标明，不回写原P4结果或声称原论文必有该优化。本轮没有新seed/重规划/捷径。

随后仍需分别补有来源的v/a配置与不改空间路径的共同时间表，以及通过原抓持
流程实测START14q/两TCP/Cube/附件/rails.65/.65/world_shift0并核对世界。
没有授权实施这些步骤；不能从旧HOME/open快照推断它们已完成。

## POST-TASK REPORT

- 完成：固定1869点/14关节审查、表格与3组PNG+SVG、25artifact/620source/94边
  来源核验、旧执行/持件/赋时能力与局限审计；7/7合成软件测试通过。
- 预算：一次正式saved-data分析，耗时只记诊断；seed未设置，无RNG。
  新规划/IK/NR/FCL/Isaac/ROS服务/执行命令全部0，未生成时间轨迹。
- 保护：原输入/模型/旧资产hash前后不变，原A失败及成功和全部历史负证据不改。
  5个不相关未跟踪旧日志保留且不提交。
- 阻塞：执行余量/运动误差包络、原生加速度与共同时间表、实际持件START建立。
  TASK02-D正式采样暂缓，距离/连续安全未证是已知局限，不本轮重建后端。
- 资格：**执行准备条件不满足**；A已获用户接受的离线初步验收保持。
  TASK06原整体部分完成；Benchmark草案未定稿。提交GitHub后停止等待审查。
- [分析源码](../scripts/review_task06_is_b0_path.py)、[合成测试](../tests/test_task06_is_b0_review.py)、
  [测试实际输出](TASK06_IS_B0_SOFTWARE_TEST_OUTPUT.txt)、
  [协议](TASK06_IS_B0_PRE_TASK_PROTOCOL.md)、
  [结果与source/artifact hashes](../results/20261012_TASK06_IS_B0_path_review01/metadata.json)。
