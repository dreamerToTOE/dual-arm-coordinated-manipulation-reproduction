# TASK06-IS-A 第二阶段 — 同源 Task26 输入与名义端点离线规划

2026-10-12。**无执行规划适配初步验收通过，停止等待用户审查。**
仅限一个共同携带 Cube、固定来源世界、名义端点和离散闭链/FCL 路径。
不代表 Isaac 执行成功、正式 Benchmark、吸附稳定性或完整 P4 复现。

## 1. 版本、范围与保留证据

- 基线 `7bae83a7cf956fe03f6bb1128ff69a63516dee0a`；分支 `task06-is-a-p4-scene-adapter`。
- [任务前报告/复用审查](TASK06_IS_A_STAGE2_PRE_TASK_PROTOCOL.md)与独立
  [V2 世界输入](../configs/engineering/task06_is_a_task26_scene_v2.yaml)、
  [有界协议](../configs/engineering/task06_is_a_scene_adapter_v2.json)先提交并上传为 `20fe06d`。
- 测试源码 `c88a80c`；唯一真正的候选/规划进程：
  [nominal_scene03](../results/20261012_TASK06_IS_A_nominal_scene03/summary.json)。
- 原 0.606 m 归档、第一阶段 carriage_y 拒绝、原协议与全部 TASK03–06 历史结果
  保持不变。本次是用户另行批准的独立 0.628 m 名义输入路线，**不是回判旧失败为通过**。
- 旧工程固定 `631b1f65656d025c1bb2173e874192f3fe4d355a`，仅控制器用获批准
  `5ed0c967401e5fedb93b938e1c3904f4a4c87600`；旧 scene/bridge/tool/SRDF 不改。

## 2. 来源几何与原生 world 对照

世界系均 `world`，m/rad，四元数 xyzw。下表通过原源码常量/控制器/launch 核对，
再与同一原生 MoveIt PlanningScene 的组合 world-shape readback 比较（消息等价
epsilon=1e-12，不是安全容差）。[完整来源](../results/20261012_TASK06_IS_A_nominal_scene03/source_audit.json)；
[实际 readback](../results/20261012_TASK06_IS_A_nominal_scene03/native_world_readback.json)。

| 对象编号 | world 中心 m | BOX 尺寸 m | 来源与政策 |
| --- | --- | --- | --- |
| task26_table | (.550,0,.100) | (1.500,.800,.200) | 原 scene/Table、controller/tableObject |
| task24_table | (.550,0,.100) | (1.200,.800,.200) | 原 MoveIt launch 的嵌套表，原样保留 |
| task26_box_wall_deep | (1.170,0,.275) | (.020,.668,.150) | 原 boxWallObjects/WallDeep |
| task26_box_wall_minus_y | (1.035,-.324,.275) | (.290,.020,.150) | 原 boxWallObjects/WallMinusY |
| task26_box_wall_plus_y | (1.035,+.324,.275) | (.290,.020,.150) | 原 boxWallObjects/WallPlusY |
| task26_cube_2 | (.350,0,.260) | (.120,.120,.120) | 原 batch1 slot B，全程固定非选中障碍 |

全部 world BOX 单位姿态，6 个 ID/形状数/尺寸/组合位姿相符。没有改原 Task26。
新内宽 `.628 m`（Y±.314）与旧归档 `.606 m`（Y±.303）每侧差11 mm；旧归档不覆盖。
三个墙的中心 Y±.324、深墙宽.668按原源码计算，不用归档 alias 替代原 ID。
launch 嵌套表被原大表包含，但仍保留原编号和几何，不因规划结果删掉。

这是**一个携带研究对象 + 一个固定供料障碍**，不是两件执行调度。携带体
`task26_cube_1` 不同时放入静态 world；后批休眠 Cube03/04按原规划政策排除。
Cube size=.120³ m、原质量=.800 kg；质量只核对来源，本轮不做动力学。
其他 Cube 的政策在20fe06d实验前已固定，结果后未改变。

## 3. 模型、坐标和抓取接口

直接复用 TASK03 原 URDF/SRDF/FK、C/Jc，TASK04 NR-SVD，TASK05 RBS/FCL，
TASK06 双树及 TASK02 文件日志。只有平台包装器增加可选世界对象输入/附着 ID
和只读原生 World readback；默认历史四对象与 `task05_shared_cube` 身份回归通过。
没有新的 IK、FK、碰撞检测引擎、scene/bridge 或执行器。

原固定 xacro 展开与 TASK03 模型逐字段/数值/结构相同：

- URDF fixture SHA256 `a9d6a364c89b9e72e51da962d16ee44de45595429339b51004a59211b312939b`。
- SRDF fixture SHA256 `11b89277bfa5fb7bcedfa35f8285507e88d2c793df6ba8e04daf12c8eb8d023a`。
- 左右 base=(.650,-.600,0)/(.650,+.600,0)，单位旋转，rails=.650/.650，world_shift=0。
- 固定 L 工具、link7→link8 .107 m、TCP 偏移和原生限位与
  [第一阶段详细对照表](TASK06_IS_A_SCENE_ADAPTER01.md)一致，本次实际完成 XML/native 核验。
- 原 native FCL 加载30个机器人 collision shapes、16个 mesh 实例，8份原 STL。
  原 SRDF 48个 disabled pairs、zero padding、scale=1 不变，ACM 未增条目。
- `T^A_B` 把 B 坐标映到 A；输入为 `T^Object_TCP`，C/Jc/FCL用其逆 `T^TCP_Object`。
  左 object→TCP p=(0,-.061,0)，q=(√.5,√.5,0,0)；右 p=(0,+.061,0)，
  q=(√.5,-√.5,0,0)。使用原 sidePose 的1 mm名义间隙，不重拟合附件。
- 原生 FCL 将 Cube挂在左TCP、touch_links=[]，右TCP经闭链预测同一Cube。
  **不豁免 tool–Cube，任何未被原SRDF许可的原生碰撞都拒绝**；合法工具安装接触
  只沿用原SRDF。上述表示不是 PhysX 双吸盘实测 attachment。

[native manifest/ACM/资源和形状明细](../results/20261012_TASK06_IS_A_nominal_scene03/native_manifest.json)。

## 4. 名义端点的阶段和完整14q

旧成功日志 `physical.log` **273行 COMMON_LIFT** 与 **301行 COMMON_SIDE_SHORT_PUSH**
均明确双 CLOSED，随后才释放；另核对原 controller 的 trace_held 调用和目标公式。
START来源 slot A .500/0/.260 + lift .280 → (.500,0,.540)。GOAL来源原预推
.790/.060/.260 + release gap .020 → (.790,.060,.280)，位于短推完成、释放之前。
两者名义物体姿态均 [0,0,0,1]，不是落桌、HOME、旧科研端点或实际物理测量。

旧 run02 文件清单、初始/最终完整q都在 HOME/OPEN；未发现上述持件阶段完整14q。
截断的单臂四位小数命令和早期293q不采用。因此按本轮明确授权直接调用
[MoveIt LMA 所用现成 KDL 后端](https://github.com/moveit/moveit2/blob/2.5.9/moveit_kinematics/lma_kinematics_plugin/src/lma_kinematics_plugin.cpp)，
从相同URDF提取 world→TCP链；不用ROS Node、隐式随机重试或角度harmonize。

预声明每端点64对/15s，LMA epsilon=1e-7、姿态权重.01、maxiter500；NR原门限
1e-8 m/1e-8 rad不变，修正L2/Linf≤.02 rad。越界原始角拒绝，无 clamp/2π转换。
**实际 START、GOAL 均候选0合格**：START用原SRDF HOME仅作seed，GOAL用
合格START仅作seed；两端点 RNG分别初始化2026101202/2026101203，实际draw均0，
不称为随机端点搜索成功率。未使用剩余63候选，也没有规划后重选端点。

完整14q按 left1..7 然后 right1..7；下列17位数据也保存在独立端点JSON，资格是
**离线构造，非历史实测**：

```yaml
nominal_offline_start_joint_state_rad:
  left: [0.5126560598311835, -0.9344838707089989, 0.8344494662155854, -1.982034389850741, 0.6645839077063976, 1.3102840725261935, 1.29207949877598]
  right: [-0.2777936024841532, -1.1480088565387032, -0.8227054135279411, -1.9509543285046695, -0.8301056940520547, 1.1331537774953553, -1.128100118923412]
nominal_offline_goal_joint_state_rad:
  left: [-0.00840197414864269, -0.46115330129009985, 1.2368716062518497, -2.412689908187811, 0.5375415068365744, 2.1783345510923797, 0.8648241551197022]
  right: [-0.061274465335722235, -1.0171839798496394, -1.065130324454565, -2.7019643817926404, -0.8950065547588109, 1.8759130331807956, -0.4623080737896269]
```

| 端点资格 | START | GOAL |
| --- | ---: | ---: |
| 位置闭合残差 m | 7.20456529e-14 | 2.33675884e-12 |
| 旋转闭合残差 rad | 2.50216549e-14 | 2.26220168e-12 |
| 最小原生关节余量 rad | .688091143 | .375035618 |
| 最大Cube名义位置偏差 m | 1.73802215e-7 | 8.60663390e-7 |
| 最大TCP名义位置偏差 m | 1.77299315e-7 | 9.14220057e-7 |
| 最大Cube/TCP名义旋转偏差 rad | 1.26529295e-7 | 9.45752708e-7 |
| NR更新次数 / 修正L2 rad | 1 / 3.95821514e-7 | 1 / 4.04447747e-6 |
| 原生FCL | 完整、self/world均free | 完整、self/world均free |
| 构造计算耗时 s | .001002014 | .000608091 |

两端点KDL FK、原TASK03 MoveIt FK及FCL RobotState TCP矩阵差通过预声明1e-12门禁。
绝对pose独立门限1e-5m/1e-4rad，闭链1e-8m/1e-8rad分别判断；均非正式Benchmark阈值。
[START完整结果](../results/20261012_TASK06_IS_A_nominal_scene03/start_endpoint.json) ·
[GOAL完整结果](../results/20261012_TASK06_IS_A_nominal_scene03/goal_endpoint.json)。

## 5. 原P4规划与独立路径复核

保留原TASK05/06参数：RBS离散邻接L2/Linf≤.01rad、投影精度1e-8m/rad，
原600nodes/800iterations/20s。不是普通MoveIt RRTConnect或末端后处理。
首个实际规划seed=**7**；协议另两seed41/20261012未启用，首条合格后停止。

| 规划量 | 实际结果 |
| --- | ---: |
| 搜索终止 | SUCCESS |
| 节点总数 / START树 / GOAL树 | 96 / 63 / 33 |
| 原TASK05合格解路径边 | 94（左树62、右树32） |
| dense路径点 | 1869 |
| 搜索计算wall耗时 | .213194502 s |
| 全关节路径L2长度 | 11.940815548 rad |
| 最大位置闭合残差 | 8.62520825e-9 m |
| 最大旋转闭合残差 | 5.30773506e-9 rad |
| 最小原生关节余量 | .00411966252 rad（约.236°） |
| 最大相邻L2 / Linf | .00992395701 / .00531510538 rad |
| P4内部FCL查询/碰撞拒绝/不可用 | 1964 / 0 / 0 |
| 候选NR失败 | 1，拒绝并留证据；未变更算法 |
| RBS中点投影数 / 失败 | 1774 / 0 |
| 实际搜索RNG draws / sample | 14 / 1 |
| 最近碰撞距离 | 不可用；没有原生distance查询 |

独立重读返回路径全部1869点：闭链、原关节限位、相邻连续性及原生FCL均合格，
精确保留两端点q。每条解边来源为已有TASK05的CONNECTED证据。交付时另对保存的
全部94条插入树边核对parent/q/attempt、原局部checked_points与leaf_edges，均合格。
端点2次、P4内部1964次、独立输出1869次合计3835次原生FCL状态检查。
**这是离散点与数值连续性证据，不是连续扫掠数学证明；没有关节速度/执行时间。**

- [完整关节路径](../results/20261012_TASK06_IS_A_nominal_scene03/qualified_joint_path.json)。
- [1869点独立复核](../results/20261012_TASK06_IS_A_nominal_scene03/independent_path_validation.json)。
- [原P4全部搜索/投影/RBS/FCL/失败记录，无损gzip](../results/20261012_TASK06_IS_A_nominal_scene03/planner_seed7.json.gz)。
  解压原JSON19,140,034 bytes，SHA256
  `e6d751833e3d5ba19bd2e23c97a1b0c4ec230ca594c954addc3971d826a0716d`。
- [计算统计](../results/20261012_TASK06_IS_A_nominal_scene03/planning_summary.json)。

仅一次小场景结果，不给成功率/优越性能结论。路径长、关节最小余量小，尚未优化；
仅闭链不约束全路径Cube始终固定姿态。以上均不能直接转成机器人下发轨迹。

## 6. 失败、软件回归和不可变性

实现预编译阶段两项工程错误：KDL parser的旧CMake变量没有导出所需include，
改链接已有 `kdl_parser::kdl_parser`；JSON→set<string>需显式get<string>。
原算法、门限均不改，未运行候选/科学搜索。[编译诊断记录](../results/20261012_TASK06_IS_A_nominal_scene03/build_preflight_note.json)。

第一次V2 wrapper run02由于**我使用 `PYTHONPATH=.` 覆盖ROS环境**，xacro子进程
无法导入ament_index_python，返回1；没有native/IK/规划。[原ABORTED结果](../results/20261012_TASK06_IS_A_nominal_scene02/result.json)
及所有原文件保留。独立只读诊断：完整sourced环境xacro成功，覆盖PYTHONPATH时
`import ament_index_python`报ModuleNotFoundError；正确环境定位到
`/opt/ros/humble/lib/python3.10/site-packages/ament_index_python`。
原第一次xacro stderr没有被既有source_audit异常路径保存，不能伪称完整原stderr；
保留原命令/返回失败及后续只读诊断，不重写失败文件。
按治理只做**一次启动命令级纠正**，新run03保留环境，不调整模型/数值/输入。
这不是重新搜索端点或事后修改场景。run02 summary的actual_rng_seeds字段只是
预配置值，没有RNG创建/抽样证据；该轮实际IK/规划/随机draw均0，不修改原JSON。

run03完成并保存 configure/build、**15项接口测试（原8+新7）、72项TASK02**、
**4/4原数学CTest目标**、原FCL默认世界回归。没有重跑原18次TASK06研究套件或
把旧435条真实FD测试说成本轮新增实验。[测试日志](../results/20261012_TASK06_IS_A_nominal_scene03/ctest.log)。

598个既有protected文件、8份原STL、4项固定旧工程资产在完整run03前后哈希不变。
交付只读核验25个artifact、620个source hash与**测试提交c88a80c及未改外部STL**均相符，
原gzip长度/hash相符。测试后适配器README按交付结果更新；其测试时hash仍保存在metadata，
没有把交付文档新hash回写到原实验来源记录。
[交付检查记录](TASK06_IS_A_STAGE2_DELIVERY_CHECK.json)保存数量、边资格与启动诊断。
此前5个无关未跟踪Task01日志保持原样，不提交、不删除。

## 7. POST-TASK REPORT

- Task：TASK06-IS-A 第二阶段，基线7bae83a。
- Status：**无执行规划适配初步验收通过／PASS CANDIDATE (OFFLINE ADAPTATION ONLY)**。
- Scientific objective：在旧Task26同源静态世界中构造名义持件端点并生成合格P4路径。
- Minimum sufficient evidence achieved：是，仅本轮限定离线范围。
- Completed：独立v2输入、来源/模型/readback、现成LMA完整14q、原NR/RBS/P4调用、
  1869点及完整树边资格、失败/元数据/哈希、原软件回归。
- Files changed：新增名义source/native wrapper/runner/tests/v2文件；TASK05平台包装器
  仅可选输入/身份/readback；记录与报告。原核心、模型、旧scene/bridge/结果不改。
- Commands run：CMake构建/离线unittest/CTest；只读xacro/ROS包import诊断；下列
  一个科学进程及保存结果读取。**没有ROS Node、ROS规划服务、Isaac或控制器。**
- Tests/metrics：见第4–6节与完整日志，不声称正式统计/力控/物理成功。
- TASK-BLOCKING：本轮最低离线证据无剩余阻塞；真实持件端点仍不具物理测量资格。
- DEFERRED：TASK02-D原生步/时钟、B/C实际执行、时间参数化及正式对比，未授权。
- KNOWN LIMITATION：离散碰撞、距离不可用、非实测名义附件、单seed、关节余量小。
- LEGACY：原两件Task26 demo；其摩擦/速度/推进/80Nm参数不导入研究算法。
- Attempt budget used：一次启动错误保留+一次命令纠正；实际科学进程1次，
  端点各1/64对、planner1/3seed。没有加预算、重选或结果调参；成功即停。
- Escalation required：离线交付无需；执行必须用户另行审查授权。
- [ORIGINAL]：不改已审查P4的NR/RBS/双树规则。
- [ADAPTATION]：源一致world/TCP/名义目标、原KDL-LMA后端构造端点。
- [ENGINEERING]：输入/readback、native getter、预算/证据文件/原TASK02日志。
- [DEVIATION]：没有新的P4数学更改；既有TASK03–06适配/数值限制继续如原报告。
- [EXPERIMENTAL]：独立工程v2名义测试，不冻结Benchmark、不回写旧实验协议。
- Records：STATUS、WORKLOG、EXPERIMENT_LOG、BUGS、DECISIONS、USER_FEEDBACK、
  当前任务卡、README和开始入口均更新；原报告/负面结果保持。
- Open risks：真机/PhysX跟踪、吸附、速度、全链间隙、正式时钟均尚无本轮证据。
- Recommended next step：用户先审查本交付；不要自动进入B/C/TASK07或直接下发path。
- Git：分支task06-is-a-p4-scene-adapter，协议20fe06d、测试源码c88a80c；
  最终交付提交见Git历史。仅保留原5个无关未跟踪文件。

本轮实际启动命令（**用于追溯，不授权再次科研运行或物理执行**）：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/install/setup.bash
PYTHONPATH="${PWD}:${PYTHONPATH}" python3 scripts/run_task06_is_a_nominal_offline.py \
  --run-id 20261012_TASK06_IS_A_nominal_scene03
```

**交付后停止。TASK06原整体仍部分完成；TASK02-D暂缓；Benchmark草案未定稿。**
