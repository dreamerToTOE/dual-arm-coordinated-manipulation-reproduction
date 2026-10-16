# R2 ABB 原 RRT_NR 真实入口：保存源码工程草案

2026-10-15。**STATIC_DRAFT_ONLY / NOT_FROZEN / ZERO_COMPILE_ZERO_QUERY_ZERO_SOLVE**。

这是普通NR局部资格后的下一入口准备，不替代当前局部资格，不自动启动新工程或规划。当前interface工程已经成功，原RRT_NR已link但local driver无solve入口；本文准备另一个薄driver及完整回溯I/O观察，使用新stage/claim，历史stage只读。已有builder和科学runner/配置草案，尚未冻结或执行，也没有新预算被消耗。

## PRE-TASK REPORT 与复用门

- Task：构建环境II原RRT_NR单target，并在局部资格及独立POST通过后准备固定seed7、10秒的真实入口资格。
- Scientific objective：确认原完整planner调用链产出真实起终点路径；source Exact与独立完整路径资格必须分开，不把有限pilot计入TableI。
- Minimum sufficient evidence：唯一工程命令/源码/binary/mesh、原GD保全、state-level完整Confs和bool、原搜索器返回/PlannerData/里程点、全部完整路径队列及独立检查。
- Scope：一target、一次seed7；数值沿Q1/局部physical NR，SVC/RBS/搜索原body保留，只有GD接缝和回溯I/O观察。
- Non-goals：不重新Q1/局部资格，不运行CBiRRT/SBL/RSS，不调seed/range/迭代或接受门，不修path，不作性能/PCS优势或完整物理碰撞声明。
- Attempt budgets：工程45wall/90CPU；真实solve运行30wall/60CPU内只一次solve10秒；完整路径独立检查另120wall/240CPU、最多2048唯一节点。均取R2总3600/7200余额min，工程/solve/path三个独立claim，不自动连跑。
- Preferred method：薄复用成功NR interface builder中的GD seam/kernel TU与既有RRT_PCS builder/runner的fresh stage、manifest、exclusive、process-group watchdog、完整原路径观察；不另造预算/solver/通用日志。
- Fallback：无自动重试/别seed/新fixture；失败和超时保存prefix，路径过2048保留全队列及未查尾部UNKNOWN，不截prefix PASS。
- Stop/escalation：局部II端点/非平凡边/soundness门或独立saved POST未通过即不可freeze；source/build/input/hash变化阻断。三次同机制失败按D079进入根因审查。
- Files expected：本PRE、`build_p4_full_r2_abb_rrt_nr_e2e_draft.py`、`qualify_p4_full_r2_abb_rrt_nr_e2e_draft.py`、薄driver/header、工程及科学draft；独立路径runner由后续阶段另审。
- Validation：本阶段仅AST/保存源码instrument/describe/validate和hash。工程独立审核、精确源码提交及rootfreeze后才compile；成功build后重绑binary并另审科学runner后才solve。
- Need user confirmation：no（只做已授权有限资格恢复的静态准备；完整正式统计仍需合格成本pilot和向用户报告预算）。

DIRECT_PORT为已合格physical NR core及作者SVC/RBS/RRT算法；THIN_ADAPTER为既有JSONL/工程/预算/完整回溯observer；TEST_ORACLE为后续端点FK/J、源限位及v3 aligned离散碰撞。旧14维工程/FR3/MoveIt/Isaac不替代论文机构。原方法与作者KDL轨迹仍分开：此版标签`RECONSTRUCTED_A01_ENDPOINTS / Q1_PHYSICAL_FULL_NR_CPP / ORIGINAL_RRT_NR / OBSERVED_IO`。

## 复用与唯一差异

`abb_rrt_nr_e2e_driver_draft.cpp`直接薄改已合格的`abb_rrt_pcs_e2e_driver.cpp`：include原RRT_NR，使用同一个已Q1/局部验证的physical GD seam，删除PCS identify/active/branch字段，不改树搜索/投影/RBS算法。原12维sampler box、恒true state callback、完整PlannerData/原milestone数组、单seed、无路径平滑/截尾沿用。原作者`run/plan_NR.cpp`确认paper II/nativeenv1的RRT range2.6、paper III/nativeenv2 range0.8、resolution0.1、default goalBias0.05。此草案只II、seed7、range2.6、goalBias0.05、solve10秒，资源外帽及完整独立路径资格须后续PRE另冻。这里的seed7/10秒是有限资格pilot选择，不冒称原论文统计条件。

`abb_rrt_nr_e2e_observation_draft.hpp`复用现有`abb_rrt_pcs_e2e_observation.hpp`中的exclusive open/append/fsync/new-json/q12及reconstruction容器。只增加无active/branch的NR完整Confs observer。nlohmann默认round-trip binary64（最高17位有效数字）保留原qa/qb/Confs/bool，包括normal false前缀。

未来builder应从当前成功NR interface stage字节精确复用，只允许再做两个明确工程变化：

1. 原state-level `reconstructRBS(const ob::State*,const ob::State*,Matrix&)`完整body包returning lambda，返回后调用`observe_nr_reconstruction`；不改vector递归/插入算法。必须保存原body SHA及逐字保留一次的证明。
2. `RRT_NR.cpp`唯一`std::remove("./paths/temp.txt");`改为保留temp，是明确I/O偏差。复原该唯一替换后RRT_NR.cpp必须逐字节等于原作者snapshot；不得笼统称修改后整文件byte-identical。搜索、树、goal、路径构造和回溯本体不变。

当前只在新的work副本对这两项做纯文本instrument验证，实际新stage尚不存在，不编译、不运行。完整观察只在原state-level调用返回后发生；异常/kill未返回Confs为UNOBSERVED，保存已发JSONL/源prefix，不能重构伪造完整path。原solve可报告Exact而save2file的reconstruct失败，driver必须原样保留、独立路径门拒绝资格。

## 冻结前义务与预算占位

先完成当前普通NR局部20请求及独立POST；任何soundness/观测/预算问题阻断本入口。下一环境II门要求II两端点project true且完整节点合格、至少一条非平凡合格边、全部soundness/完整尾部及无trueRBS/false回溯。III正常拒绝可保留PARTIAL，不否决合格II。冻结前绑定本driver/header、成功局部/工程binary/source/mesh/Q1/compiler/Eigen/nlohmann/OMPL/KDL/PQP全部确切资产，单独独立静态审查及新工程预算（45wall/90CPU一次，**尚未冻结**）。不重复重编当前成功target，不改变旧stage；当前builder从原corrected plain template新建stage，保留唯一GD seam及新完整回溯观察，清除local trace正文包装。当前compile命令未保留可单独复用的object，不臆测可免编译。

初版`local_gate()`强制ready=false占位，初版v1配置和保存源码静态记录保留。2026-10-16只读恢复后，真实局部execution为`FIXED_LOCAL_ABB_NR_QUALIFIED`，三个非平凡边及147唯一节点资格完成。第一层`P4_FULL_R2_ABB_NR_LOCAL_INDEPENDENT_POST_20261015.json`实际schema为`P4_R2_ABB_NR_LOCAL_SAVED_POST_V1`、status为`PASS_SAVED_EVIDENCE_POST`，117258/117258检查通过，明确`personnel_independent=false`；第二层`P4_FULL_R2_ABB_NR_LOCAL_ROOT_INDEPENDENT_POST_20261015.json`由非runner作者复核，实际schema为`P4_NR_LOCAL_PERSONNEL_INDEPENDENT_STDLIB_SAVED_POST_V1`、status为`PASS_SAVED_EVIDENCE_AUDIT`，218766/218766检查通过。二者均0新科学调用。新gate同时检查真实execution/原协议SHA、两层精确schema/status/检查分母及全部passed记录、第一层II后续gate与两层零科学声明；第二层完整文件SHA连同第一层文件SHA写入工程资产。不能因文件存在或execution布尔为true自动跳过saved POST。builder资产映射同时绑定局部execution/protocol/claim及全部历史bound前后SHA；工程重生为v2 draft并保留v1原字节，仍须root独立freeze与提交后才可build。科学draft在实际成功新build前`MUST_BUILD_BEFORE_FREEZE`，无binary假值。

第二层人员独立审查的原始JSONL链接补充`P4_FULL_R2_ABB_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_20261015.json`另有666/666检查通过，schema=`P4_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_V1`、status=`PASS_RAW_LINK_ADDENDUM`。gate绑定其完整SHA、与主人员独立报告的`main_report_sha256`关系、精确检查分母及零科学声明；没有重跑任何NR/FK/PQP。第一层JSON超过GitHub单文件上限，两个完整大JSON均以确定性无损`.json.gz`及SHA manifest交付，原JSON本地原字节保留。新checkout在运行本入口的只读资产校验前，先按manifest解压恢复同路径JSON并校对原字节SHA；这是证据恢复，不能重跑原科学资格来替代。压缩文件与manifest由root另行保全，gate继续绑定解压后的完整原JSON SHA。

正式调用另单claim固定一次seed7、10秒solve（候选外帽30wall/60CPU，**尚未冻结**），与完整路径独立数学/源界/v3 aligned离散碰撞资格分开记账。原全12每条leaf距离须严格<.05，所有原节点/所有里程边完整检查，source Exact和完整回溯以及独立门共同通过；不施PCS固定active/branch门，不按成功选seed，不修path。完整路径队列/未查尾部必须保留，不能截prefix PASS。若较大需先估正式成本报告用户，不缩211项/22500正式统计等原文义务。

全部正式实验仍0/22500；本草案0compile/query/solve/RNG/VI候选。不得据此启动P2/Isaac或改写全文覆盖状态。
