# R2 普通 NR 真实入口审计与物理全链 C++ 移植 PRE 草案

日期：2026-10-15。状态：**READ_ONLY_SOURCE_AUDIT_COMPLETE / PRE_DRAFT_NOT_FROZEN / MUST_BUILD_BEFORE_FREEZE**。

本报告是原 R2 的接口恢复准备，不是新一轮运动学研究，也不是已执行资格或正式统计。撰写时只读取原源码、已有结果与库文件；不编译、不调用 FK/J、NR、IK、碰撞、RNG 或 planner solve，不修改已冻结源码、配置、PRE、历史结果和预算账本。允许的新源码草稿仅为 II/III 的既有物理 NR 内核移植，未经构建/数学对照前不可用于资格或速度比较。RSS 与此路线解耦；不追加 IV/VI RSS 构造。

## 结论和最早下一切片

建议优先采用项目自有 **Eigen C++ physical_nr 内核移植**，从 II/III 的 6×12 全坐标约束开始。仅逐式移植已经合格的 `physical_nr.py`、ABB 独立刚体变换与 Jacobian、SVD 更新及收敛后周期图，不新造 solver、不改变原 NR 方法。通过数学/行为对照后，在隔离的作者源码副本中给 `kdl::GD` 顶层入口加显式回调，保留原 `IKproject`、`isValidRBS`、RBS 和回溯本体。native 原版、我方重建数值版各有 plain/trace；两个版本不能混报为作者原生。

持久 Python worker/嵌入 CPython 可以更快复用现有参考内核、验证传输和 RBS 接缝，但解释器与数据交换会继续阻断公平速度比较。若最终需 C++，先做此临时桥会引入第二套接口资格。因此把它列为兼容备选，不作为首选，也不为未使用的辅助接口投入工程。

下一切片只恢复普通 NR；无 RSS 成功先决条件。I 的 3×20、IV/V 的 6×12、VI 的 12×18、全部论文表图/算法/统计义务保留，不能因本切片先 II/III 而改为已完成或缩小总范围。

## 原始失败的证据边界

| 环境/源码 | 已保存证据支持的具体问题 | 不能推导的结论 |
|---|---|---|
| I / `planar_ckc` | GD 入参量化到 1e-5、KDL 最后一角为 `3.1416-q19`、输出 abs(q)<1e-4 截零、按 2×3.1416 wrap；默认 `include_constraints=false` | GD 返回 true 不等于原障碍/限位资格，不可只替换 π 后宣称全部修复 |
| II/III / `CKCplanning` | R1 保存的 20 个物理误差矩阵由近似基座 yaw 与反链内部残差解释到约 3e-13 mm；II 索引 6/7 另有输出截零造成的约 .020649227/.010282231 mm 闭合损伤 | 不可把全部失败归为 π；没有 pre-zero 原始 q，不能改写旧 FAIL；l5/lee 66/66 与 65.5/66.5 之和相同只支持端点解释，不能外推到碰撞链 |
| IV / `ckcComau2`；V / `ckcComau_industrialScene` | 17 个原返回 q 的物理误差由基座 yaw 与内部剩余角误差×杠杆臂共同解释；V 样本0 仍有超出单纯 π 误差的 .001951684 mm 项 | 这些样本没有恰为零的角，不能据此批次断定截零是原因；IV 3 个 false 缺少 KDL ret/pre-zero/限位阶段日志，旧原因仍 UNKNOWN |
| VI / `ckcComau3` | 原 GD 是 GD12 后 FK13（有 abs<1e-4 截零）再数值 IK3；不是同时 12×18 Newton | 不可冒充原作者同时全链 NR；不同零集合表达或同零集合都不保证离流形更新相同 |

证据来源：`P4_FULL_ABB_NATIVE_FAILURE_ROOT_CAUSE_REVIEW_R1.md`、`P4_FULL_COMAU_SAVED_DATA_ROOT_CAUSE_R1.md`、`P4_FULL_R2_SPATIAL_INDEPENDENT_REVIEW.md`、R1 POST-TASK 和原 R2 保存记录。R2 物理 NR 已保存 160 次空间调用中 154 次合法收敛、6 次闭合但限位拒绝（均 IV q3 低于 -1.5708）；后续 IV 局部 24/24 只支持所冻结有限邻域，不改变旧失败。此处不重跑这些结论。

原 `ChainIkSolverPos_NR` 为 10000 次、1e-5；本地 KDL pinv 默认绝对奇异值 cutoff=1e-5、SVD 最大150次。现参考内核采用相对 cutoff=1e-12，且残差图、单位、周期与停止门不同。**重建版是论文 full-Jacobian Moore–Penrose NR 原理的独立实现，不是原 KDL 迭代轨迹或投影映射的逐位修复。**若要求原 KDL 路线，可另推导保留原基座的正确反链目标；不能用仅相同零集合来证明等价。

## 真实 solve → 投影 → RBS 路径

本节以直接调用为准，不以函数名或注释推断额外前置条件。

- II/III `CBiRRT_NR.cpp`：`solve` 采样 `sampler_->sampleUniform` → `growTree` 插值 → 在 `mode==1 || !reach` 时 `IKproject(dstate)` → `GD(q)` → 取 `q_solution` → source 碰撞 → `checkMotionRBS` → 算术中点 → `isValidRBS` → `GD` → source 碰撞 → 原递归。mode2 且已 reach 跳过顶层投影，端点资格必须外部先满足。
- II/III `RRT_NR.cpp`：goal bias 或 sampleUniform → 原距离截步 → 除 goal 且 reach 外 `IKproject` → `checkMotionRBS`。不能把所有采样都描述为先调用 `sample_q`。
- II/III `SBL_NR.cpp`：`sampleNear` → 实际调用 `IKproject(xstate,true)` → 加树 → `checkSolution/isPathValid` 懒验证路径边时才 `checkMotionRBS`。其实际参数 true 使投影包含 source 碰撞；“lazy”注释不能覆盖真实布尔值。
- IV/V/VI 相应 `*_GD.cpp` 搜索器采用同类 `IKproject`/RBS 接口；IV `ckcComau2` 还在 `withObs` 路径保留 `checkEE`，即两臂 FK6 的 z 均至少10 mm。不可在统一适配中丢掉此门。
- I 使用 `gd::StateValidityChecker` 与 `*_gd.cpp`；原 RBS tolerance .05、深度100，non_decrease_count>100 有效。空间环境 .05、深度150，源码 nondecrease 检查被注释。I 检查递归与回溯的 nondecrease 距离表达并不完全相同，均保留。六环境不得硬统一深度/距离/遍历顺序。

`sample_q` 在 II/III 有 `collision && !check_angle_limits` 可疑布尔，但不是上述三搜索器直接路径。它应在全清单的实际到达路径另审，不得把未到达 helper 完全恢复设置为当前原 planner 接口资格的虚假前置。SVC 中线段 `checkMotion/isValid` 也是不同于实际 `checkMotionRBS/isValidRBS` 的接口。

普通 NR 全坐标投影可改变所有主动/被动关节。PCS 的固定主动链保持、固定解析 branch 或 8 分支枚举不能挪作 NR 拒绝门。分支身份可诊断记录，不能为得到“同支”挑换 NR 输出。

## 资产复用与两条路线

| 资产/路线 | 分类与复用方式 | 限制 |
|---|---|---|
| `physical_nr.py` + `abb_independent_oracle.py` | TEST_ORACLE；逐式移植物理 g/J、数值图与 Moore–Penrose 更新 | 资格参考，不是速度基线；原文件保持不变 |
| Eigen 3.4.0 `JacobiSVD`，动态6×12矩阵 | DIRECT_PORT 数值库调用；显式 thin U/V + `s > s0*1e-12`，由库做 SVD | 不重写 SVD；浮点算法与 NumPy 不同，须比较谱/投影算子或 delta，不能要求 U/V 向量逐位相同 |
| 原 KDL 链、原三搜索器、SVC/RBS/回溯、source PQP | DIRECT_PORT 作者原生对照与原接口本体，外部只读固定快照 | 原几何目标不自动成为物理全链内核；不可把源码拷进仓库冒充项目自有 |
| PCS JSONL transport、plain/trace、claim/预算/源哈希机制 | THIN_ADAPTER；仅复用输入输出与记录框架 | 删除 PCS branch/active 限制，不制造第二套通用日志或预算框架 |
| 持久 CPython/worker | THIN_ADAPTER 备选，原 Python 内核不改 | 额外启动/IPC/解释器成本，接口资格可用，公平速度不可用；避免“一次桥接再一次移植” |
| `baselines/p4_closed_chain/projection.*` | REFERENCE_ONLY / TEST_ORACLE | 14维/6行工程机构、m单位、每步限位拒绝、满秩拒绝和停滞策略不同，不是 drop-in |
| VI tree alternate | REFERENCE_ONLY | cpp include 默认 header 与 tree 声明错配；主臂仅1个活动关节、其余5个注释；不是18维，WDLS/JL/1e-3/1000次等也不同。未尝试编译 |
| `docs/POST_TASK01_REUSE_MAP.md` 中631b1f 工程资源 | 现有 THIN_ADAPTER/TEST_ORACLE 分类继续 | FR3/MoveIt/Isaac 不是论文 ABB/Comau 数学内核，本切片不迁移其模型或研究方向 |

本地只读确认已有 Eigen SVD、Orocos KDL 1.5.1、nlohmann JSON；Python3.10 development header/lib 也存在。没有为本报告安装依赖或编译。

草稿资产：`baselines/p4_full/geometry_consistent/physical_nr_abb_cpp_draft.hpp`，单一项目自有头文件，无main/driver/build脚本，不链接或调用作者程序；`reports/P4_FULL_R2_NR_CPP_DRAFT_STATIC_REVIEW_20261015.json` 只记录文本/括号检查，**不是构建检查或科学PASS**；`reports/P4_FULL_R2_NR_SOURCE_AUDIT_SAVED_INPUTS_20261015.json` 只读复制旧输入/历史输出/哈希。所有这些均标记未冻结、未编译、未执行，不修改现有 bound。

## 拟移植内核：与 Python 的一一对应

首份 C++ 草稿只含 II/III。物理几何保持 ABB b=166、l1=124、l2=270、l3a=70、l3b=149.6、l4=152.4、l5=65.5、lee=66.5 mm；II D/L=900/300，III=1200/500；base2 yaw=3.1416，grasp 沿 x 的原 rod，S=diag(-1,-1,1,1)。坐标顺序为 arm1 六角后 arm2 六角，轴 z,y,y,x,y,x，不替换现代 URDF。

1. g 为 `p2-p_target`（mm）与主值 `log(R2 R_target^T)`（rad）；J 为 Python 原物理全链表达，包含离流形逆左 Jacobian。SO3 距 π<1e-7 必须报告图歧义，不能随意选择轴。
2. 使用未缩放 mm/rad 行，`q_next=q−V diag(inv_s) U^T g`，仅 `s>s0*1e-12` 取倒数，不增加 damping、line search、步长夹紧、迭代内限位夹紧或低秩全拒绝。
3. 默认最多10000次更新；循环含 iteration0和10000的收敛判断。分别 `position_max_abs<=1e-5 mm`、`rotation_matrix_max_abs<=1e-5`。SO3角指标仅诊断，不替代矩阵门。
4. 收敛后 true 2π 的 atan2(sin,cos) 周期图，重评物理闭合，再按原 `3.1416` 角度限位检查。维持 CONVERGED / POST_CHART_RESIDUAL_REJECTED / CLOSED_BUT_JOINT_LIMIT_REJECTED / 图歧义 / ITERATION_LIMIT / WALL_LIMIT / NONFINITE 等语义。候选含失败 q 保留。
5. C++ trace 增加每步 q/g/J/spectrum/cutoff/rank/delta 与前后指标，只是观测，不控制更新。plain 与 trace 的相同 C++ 内核必须解析数值精确相同。跨语言按冻结误差门比较数值，不能把运行时或 SVD 列符号误当科学差异。

Python 原 trace 只保存每步残差指标，**没有**完整 q/g/J/spectrum/delta。64个旧输入/最终输出/指标轨迹可直接绑定；完整逐步等价需要在新科学资格中原封调用旧函数/观测副本作有预算重放，不能在 saved-only 报告中伪称已有完整 trace。此重放只验证新 C++ 移植，不重开原 R1/R2 科学结论。

## 输入冻结草案与最小门

新 companion JSON 保存只读哈希、64个 II/III 已保存 `nr_reference` 输入/最终候选/状态/指标轨迹，以及原 PCS 冻结的4中心+16个±.08rad输入。数据从原 JSON 原样复制，无 RNG、筛选成功样本、数值评估或新候选构造。

- Q1 内核移植：II 32 + III 32 条既有 R2 NR 输入，顺序不变。拟 C++ plain/trace 各64次、Python原参考详细观测重放64次，共最多192次顶层NR；已有保存终态/轨迹为不额外计算的历史对照。任何失败逐条保留，不能只选择收敛样本。
- Q1 显式比较：状态、iteration数、最终q（逐坐标周期图一致）、逐步g/J、sigma、cutoff附近数值秩、delta和收敛门。建议初稿绝对/相对门：q/delta 1e-10+1e-10×maxabs；g的位置1e-8 mm、旋转1e-10；J逐项1e-8+1e-10×maxabs；sigma同样。最终仍必须通过原独立闭合/限位门，不能用跨语言宽容门替代。cutoff或接受边界附近不符标 UNKNOWN 并审查，不靠放宽门宣称同一迭代。
- Q1 不重新做 R1/R2 Jacobian 有限差分或几何资格；现有 oracle 已有独立证据，只对新移植逐式/数值比较。64条全部条件冻结后一次运行；源 SHA/输入/build变动立即阻断。
- Q2 单独冻结原接口：4中心+16冻结raw输入，native/R2 × plain/trace=最多80次顶层 `IKproject`/GD 对照；不复用64个PCS分支请求为NR义务。下一层16条中心到其 NR 恢复局部节点边，四变体最多64 RBS +64回溯。NR 输出决定边终点，选择规则必须运行前固定，不进行分支挑选或 h 修改。先记录 d<.05 的 vacuous true，不能把它当真实中点调用正控。
- Q2 不要求 native 物理成功才能接受 R2 的有限修复证据；各自原始返回与外部合格性分别报告。R2 返回true却独立物理闭合失败为 soundness 阻断。碰撞/限位拒绝为正常失败，不直接成为论文理论问题。
- Q1/Q2 均0 solve、0 RNG、0正式表I次数。接 planner solve 另冻结真实入口/单seed/原参数/短时帽、完整路径/独立门；不能把接口通过等同全局规划能力。

## 顶层 GD 接缝与原本体保全

原 GD 非 virtual，子类同名方法不保证原调用重定向。建议仅在新的隔离数值版本 `kdl::GD(State q)` 入口加显式项目回调；原native变体没有回调。回调失败不覆盖 `q_solution`，成功才更新，`get_GD_result` 由原SVC继续使用。只hook顶层，不把VI原GD12/IK3转发为新的同时内核后仍冒充原源码。

原 `IKproject` 中的 source 碰撞、IV `checkEE`、原RBS normDistance/算术中点/.05/深度/遍历/返回/回溯插入顺序保留。新增外部 aligned physical collision/oracle单独记录，不能静默替换source PQP。native KDL内部调用计数只有显式观测到才可记；顶层GD调用不等于已观测10000内部迭代。trace记录返回true/false、pre/postq、候选、可观测KDLret、原/独立闭合、源/对齐碰撞、限位、运行时故障、完整prefix/未执行列表。

## 预算和停止条件草案

**本报告不冻结新预算。**建议 E工程移植/构建单次180 wall/360 CPU（仅编译与静态，不科学）；Q1单次60 wall/120 CPU；Q2在Q1通过且实测成本后另冻结、初稿不超过120 wall/240 CPU。所有工程和科学从既有R2总帽扣，取实时剩余额度的min；不得追加VI B构造或将这些上限当已批准新额度。Q1单次运行的外部帽只是资源UNKNOWN，不改变NR10000次方法参数。不得同时启动两个资格；已有claim/output时拒绝重复。

写作时参考账本V4包含15次执行（14科学+1工程），保守R2自有wall=285.28806236599576、CPU=264.43608；剩余3314.7119376340042/6935.56392。此快照会过期，freeze前必须重读执行自有wall/CPU和最新账本SHA，以math.fsum一次计各自成本，不复用旧快照开额度。B累计974、余0，旧时间帽不改变。

任一 source/build/input不匹配、plain/trace逻辑不等价、物理soundness错误、预算/运行时错误须保存prefix并停止依赖阶段；普通限位/碰撞拒绝如实PARTIAL。三次同机制有证据修复仍失败进入D079根因审查，不能盲重试或用放宽门解决。方法/分布变化（阻尼、步长控制、别的残差权重、新采样、分支筛选、I/VI另一机构等）不能夹带在“薄移植”内，须独立方案与预算；此次不需要把原已授权R2有限资格重新解释为大规模规划授权。

## 原作者 / 我方修复 / 论文方法的报告标签

- `AUTHOR_NATIVE_KDL_NR`：原目标、近似π、量化/截零/原周期及原KDL返回均保留，作为真实源码证据。
- `RECONSTRUCTED_PHYSICAL_FULL_NR_CPP_DRAFT`：既有已合格NumPy物理全链NR的项目自有C++移植候选；构建/逐步对照通过后改为有限资格状态，仍不得称原作者原生。
- `PAPER_METHOD_FULL_JACOBIAN_PSEUDOINVERSE_NR`：报告其方法层等价范围与实现差异，不凭源码失败宣布论文理论失败，不凭有限局部通过宣称全局/公平速度/PCS优势。

全部211项完整清单、Table I 的45cell×500=22500（formal仍0）、Fig3–5、TableII、投影500000、点对50000、三规划器、被动链数量/局部可见性/复杂障碍/窄通道/固定链消融义务保留。完成P4后中文Word/PDF及面向双FR3吸盘与装配适用分析保留；最新原文—复现对照表必须交用户审查，不进入P2或Isaac。
