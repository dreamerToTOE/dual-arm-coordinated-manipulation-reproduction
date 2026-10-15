# R2 ABB普通NR原GD/RBS接缝：局部资格 PRE草案

2026-10-15。**DRAFT / BUILD_PENDING / NOT_FROZEN / ZERO_NEW_SCIENTIFIC_CALLS**。本轮只写runner/PRE及saved-only协议草案，不编译、求FK/J/NR/碰撞、运行binary或提交。Q1固定64移植资格及独立14272项复核已通过，不重放。RSS与普通NR解耦，其他环境和全文211义务完整保留。

## PRE-TASK REPORT

- Task：把已合格的II/III物理C++ NR接到原作者`kdl::GD`真实入口，验证原SVC/RBS/回溯有限行为。
- Scientific objective：确认同一数值内核在原GD→IKproject→碰撞和原RBS递归中有可解释、物理合格的返回，观察真实非平凡连接与完整原回溯。
- Minimum sufficient evidence：固定全部20顶层请求、原返回/false候选/失败path前缀、plain/trace逐值一致、实际递归GD事件和原碰撞、全部成功候选/原path的独立闭合/源界/aligned离散碰撞资格，完整失败与未检查尾部。
- Scope：A01 II/III起终点4个`project_q12`，首个保存PCS环境II路径4个milestone的3条连续边各`rbs`与`reconstruct`，plain/trace两mode，最多20顶层。不新增样本、选边、改seed、修path或换端点。
- Non-goals：不修改原sourceRBS中点/.05/depth150/递归/返回/Confs本体，不做RRT/CBiRRT/SBL solve、RNG、RSS、原生KDL轨迹或速度比较；不加NR固定主动臂/解析分支门。
- Attempt budget：准备0科学；拟单次60wall/120CPU，取R2累计3600/7200余额min。claim一次、不得重置/重复执行；原VI B974构造额度余0。
- Preferred method：复用原PCS trace/driver工程框架、common.RunBudget/Evidence.process和PCS collision-worker/API；数学检查复用既有独立端点oracle，不另造solver、SVD或通用预算/transport。
- Fallback：无自动fallback或新fixture；正常source拒绝保留PARTIAL，runtime/预算/证据问题保存prefix UNKNOWN。
- Stop/escalation：改版返回true却闭合/源界失败为soundness阻断；plaintrace不等价、querycode错误、来源/预算/进程/观测失败立即保全停止依赖阶段。三次同机制有证据修复未解则按D079根因审查。
- Files expected：本PRE、`scripts/qualify_p4_full_r2_abb_nr_local_draft.py`、draft协议；rss agent负责builder/driver/observation和fixed-input inventory，不修改任何原冻结源与历史。
- Validation：仅AST及saved-only describe/validate；工程独立冻结构建后再绑定binary/manifest、root审runner、rss审数学/接缝，提交并冻结才能科学执行。
- Risks：保存PCS边不保证NR局部可连；全路径碰撞枚举可能超过60秒；必须保存全队列和未检查尾部，不能截子集PASS。原source离散策略非完整几何/CCD。
- Need user confirmation：no（仅已授权有限资格恢复准备；正式统计仍需成本pilot及另审）。

## PRIOR-ASSET CHECK

既有631b1f工程复用审计和`docs/POST_TASK01_REUSE_MAP.md`继续适用；FR3/MoveIt/Isaac机构不替代原ABB。Q1 C++物理NR为已合格算法资产DIRECT_PORT；作者GD/SVC/RBS完整body与原sourcePQP为DIRECT_PORT，外部隔离副本仅GD顶层显式转接；PCS trace/JSONL transport、common预算/evidence、collision_worker为THIN_ADAPTER；端点独立oracle与v3 aligned collision为TEST_ORACLE；旧14维工程projection仅REFERENCE_ONLY。不复制算法或重造基础设施，不需要新用户决定。

## 固定输入与明确标签

请求inventory由rss agent逐字复制A01 II_0/II_1/III_0/III_1的`selected_q_rad`以及`20261015_R2_ABB_RRT_PCS_E2E01/runtime/result.json`的全部4个`milestones_q12`。3边严格(0,1)、(1,2)、(2,3)，使用原binary64，不用已稠密PCS节点替代NR回溯，也不拼新路径。inventory、A01/source执行/协议/claim/build及既有PCS完整路径POST、Q1 execution/独立POST/实际binary全部绑定。

标签`RECONSTRUCTED_ENDPOINTS / PHYSICAL_FULL_NR_CPP / ORIGINAL_NR_SVC_RBS_CONTROL_FLOW`；原作者KDL/native失败保持，不将版本化C++候选冒称作者原生。全12坐标可改变；不检查固定主动链或解析branch，不以PCS的分支条件拒绝普通NR。

固定调度为II trace8→II plain8→III trace2→III plain2（每mode中先原2端点project，再按边序rbs/reconstruct各一次）；source RBS false也保留固定reconstruct独立请求，不拿它当连接成功，不补算/换边。共4project×2+3rbs×2+3reconstruct×2=20顶层。batch提前退出时顶层`requested`与实际原响应`completed`分开，未返回项UNKNOWN，不用20帽冒报完成数。

driver单binary参数`ENV MODE RUNTIME`，runtime仅复制binding的simulator网格，不复制作者旧paths。stdout保留原源输出，只有`P4_NR_RESPONSE `前缀行解析为响应。plain/trace的environment/request/id/op/returned/q12/path_q12及原逻辑计数逐值相同，trace的obs/count/成本不作为plain相等字段。`observer_errors`必须空，trace entered/completed/id-kind配对、GD summary与事件逐值核对；plain内部计数仍UNOBSERVED。

## 数学、候选与原完整路径门

原physical NR参数/Q1默认保持：10000更新、内部120秒、1e-5mm/1e-5旋转矩阵、relativeSVD1e-12、原3.1416源限位、收敛后真2π周期图；无阻尼/夹紧/线搜索。原RBS/.05/depth150/遍历及回溯插入顺序保持。

每个trace GD已完成记录的input/candidate/status/returned/accepted_updates/metrics全部保留；每个有限候选做独立物理闭合与原源界检查。GD returned=true必须闭合/限位合格，候选没有固定链/branch限制。返回false仍保存和分析候选，正常不收敛/限位拒绝不改判。成功GD候选、顶层project最终q以及所有原回溯节点必须通过v3 native/aligned实际查询，最终资格采用aligned；querycodes全部0、TCP一致、原离散策略无碰撞才合格。源上层false而GD候选物理合格/碰撞拒绝属于可解释拒绝，不强制成功。

独立节点记录按`environment+packed binary64 q12 bytes`复用，保留每个GD/project/path来源ref；signed zero不合并，不按容差merge，也不筛碰撞后换输出。有限GD=false候选先保存数学资格；不因它未被方法接受而自动给它制造后续碰撞通过义务。源accepted候选与路径节点全部碰撞，无抽稀。每个节点数学保存2个独立FK，collision-worker保存4个adapter内部FK/J与native/aligned完整响应及PQP queries，started/completed分别真实计数。

为与既有记录一致，数学事件字段仍叫`math_arm_FK_*`；实际`oracle.arm_fk`底层调用同时构造FK/J，因此每节点实际2次独立FK/J函数调用，不能称J为0。source `collisionCheck_counter`只是原上层碰撞入口次数，trace `pqp`和adapter每variant `query_codes`才是实际细粒度PQP查询数，三层计数分列，不互相冒充。

成功回溯必须原path完整首尾精确等于请求qa/qb，所有12角有限，所有相邻完整12角L2距离**严格<.05rad**，全部原节点独立通过；不补点、投影、平滑、截尾或修端点。失败回溯前缀照存并检查，但不把prefix当成功路径。成功RBS的全部已接受GD中点同样要独立通过；非平凡正例需原qa→qb距离≥.05且原rbs/reconstruct trace都真实发生GD递归投影，并具有完整合格原回溯。

正常source拒绝不等于实现错误：每边记录PASS/REJECT/UNKNOWN；3条不强迫全NR可连。所有20请求/资格尾部完成且全部物理soundness/plaintrace门通过时，若3边均成功可标有限LOCAL_QUALIFIED；有拒绝则整体PARTIAL。至少1条非平凡成功+完整合格原回溯仅支持下一单独planner资格门。全无正例也原样交root判断，不自动追加fixture。

下一planner目标明确为**环境II原RRT_NR**：其有限入口门额外要求环境II两个固定A01端点的`project_q12`均returned=true且完整节点资格通过、至少1条非平凡合格边、全部soundness/plaintrace/完整尾部门通过，而且任何true RBS/false reconstruct均阻断该门。分别记录II/III endpoint_gate；III端点正常false会使整体PARTIAL，但不否决已合格II入口。整体LOCAL_QUALIFIED仍要求全部4端点和全部3边通过；不将局部入口门冒充规划已完成。

## 资源、保全与下一步

60wall/120CPU含runtime复制、所有导入、source进程、原递归GD/碰撞、独立数学/碰撞、完整日志、后哈希和清理；工程构建另行单次预算。原RBS递归数量无法由固定20顶层推测，真实trace计数，plain内部UNKNOWN；不按可见trace推造未观测started。碰撞节点全队列在解释原响应后冻结，按确定来源顺序处理；资源耗尽保存prefix/未检查队列，任何尾部不允许PASS。禁止为省时复用旧PCS物理check替代本次新NR输出；只有同次精确同q记录可复用。

driver每条trace外部观测帽固定`nr_gd=1024,nr_project=1,nr_valid_midpoint=1024,nr_rbs=2049,nr_reconstruct=2049,collision=1024,pqp=131072`，触发抛出runtime UNKNOWN而非source正常false；plain无内部观测帽，仍受同次外部墙钟/CPU帽。它们不修改原递归depth150或算法返回；触帽只留prefix，不重跑、不改成拒绝成功。

common.Evidence原API只查parent+reaped child CPU，故runner采用其子类薄适配同一process API，沿Q1现有`live_group_cpu`在20ms等待处额外检查parent+reaped+当前live进程组CPU，覆盖持久node worker及其PQP子进程；墙帽由原RunBudget守护。路径/候选的plaintrace比较除非计时source counters外，q/request/path采用packed binary64比对（含signed zero）；节点去重也用相同字节语义。

冻结前重读全部当前20及新工程execution自有wall/CPU，逐份一次计入，旧V5/V6快照只历史。工程未ready时协议明确MUST_BUILD_BEFORE_FREEZE；实际manifest/binary/claim/build source、Q1已审证据、v3collision全部源/网格/库必须绑定。源/协议/claim运行前后哈希一致，exclusive claim/output、异常前缀/cleanup错误保留，不能覆盖旧失败。

Q1只固定64移植通过，当前接缝仍未运行。普通NR有限局部后仍需原planner真实起终点路径资格和成本pilot，再报告正式规模预算；TableI0/22500和全部211项原文义务不缩。最终中文Word/PDF及双FR3吸盘/装配方法适用分析、用户审查最新范围表要求保持，不自动P2/Isaac。
