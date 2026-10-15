# P4 R2：原PCS搜索入口与首条RRT空间路径独立审查 PRE草案

2026-10-15。**只读源码与保存数组审查，未编译、未调用FK/IK/碰撞、未调用solve、未消耗科学候选预算。** 本文件新增，不覆盖任何历史PRE、源码或实验结果。根代理正在单独准备首条真实空间路径；本审查给出该有限pilot的前置风险、可测计数与独立全路径门，最终冻结协议以根代理审查后的文件为准。

## PRE-TASK 与复用边界

任务：审计原三个PCS搜索器的真实采样/扩展可达路径，优先审查固定envII、seed7、range2.6、10秒的原RRT solve入口及完整输出资格。科学目标是取得或如实否决首条原模型空间路径；不把一次pilot加入Table I统计或解释PCS优势。
最小充分证据：原RRT主体真实运行；真实采样与原分支切换/RBS/回溯日志；原状态与独立完整路径资格分列；准确的输入/source/二进制/seed/预算/退出原因。当前只做此报告与保存数据算术，不实现、不运行、不commit。
复用：原909bd72作者快照为DIRECT_PORT，已审查R2数值patch与原RBS保持；A01保存端点及LOCAL01八支输出为TEST_ORACLE；已有构建、claim、预算、v3 collision及计账工具为THIN_ADAPTER；FR3/Isaac只作REFERENCE_ONLY。本阶段不用已有FR3场景替代原ABB机构。
工程实现必须新版本driver/外部构建根，不能修改或覆盖abb_pcs_qualification_v1四二进制及其绑定源码。固定local driver没有solve/sampler入口，不伪称能直接执行新JSON操作。需要用户确认：本只读审查无；后续冻结与执行由根代理按最新授权/实际余额判定。

## 三搜索器真实路径与未达helper

作者快照固定`909bd72fff778aca8682c96f9eb86ae4eb75557b`。原函数位置如下，均为快照相对路径：

|搜索器|真实入口与路径|审查边界|
|---|---|---|
|RRT|`planners/RRT_PCS.cpp:102` solve内完整循环；155–165原OMPL goalBias=.05/uniform采样及rand()%2；167–175全12 NN/距离/插值；188–214原解析IK与失败换另一主动臂；215 collision；218 identify；229–232两共有branch的RBS；235起入树|没有独立grow API；不得抽出自写grow并称原函数。薄子类可只读protected Motion/nn_导出原树/parent/ik；RRT对SVC为私有继承，不能伪称子类可直接公开其私有基类API。|
|CBiRRT|`planners/CBiRRT_PCS.cpp:142` protected growTree；每调用一次rand选角色，内部保角色；161 activeDistance，165全12插值；解析投影/碰撞/identify/RBS后入树。原solve分别以100/500次扩展/连接调度|可薄子类暴露原protected growTree；count1属于组件切片，不是原正式调度。activeDistance存在已证实源码错误，见后节；它不在RRT调用链。|
|SBL|`planners/SBL_PCS.cpp:87` solve内sampleNear/selectMotion与扩展；先建lazy节点，258起checkSolution，294–405连接与isPathValid中RBS|没有独立grow API。未RBS的树边是lazy待查边，不算路径资格。默认projection/grid配置须记录，不能自行换成新投影。|

三搜索器都没有调用SVC的`sample_q`或三参数随机`IKproject`。这些helper的for成功不break、碰撞/界的&&谓词、IK失败沿用旧q等缺陷保留为源代码风险；它们不属于本次RRT solve实际前置门，不为其另花修复预算。旧PRE将随机helper修复写作后续整合前置的笼统表述，由本次具体可达性审查限于实际调用者，不改旧文件。

原run/plan_PCS.cpp:82–124使用RealVector12和原OMPL采样盒，每臂低界[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]、高界[2.88,1.919,1.22,2.79,2.09,3.1416]；validity callback原样恒true，resolution=.02。原源IK仍检查被动臂原physical界，采样盒和物理界必须分列；输出落在物理界内但采样盒外是否拒绝，须按pilot预定义资格口径明确，不将采样盒误称原完整物理限位，亦不暗改分布。

## identify_state_ik的实际语义和保存端点证据

`validity_checkers/StateValidityCheckerPCS.cpp:275–318`：只对输入ik=-1的一侧重新算；以该侧主动臂FK构造目标，然后calc_all_IK_solutions枚举原0..7并过滤源IK返回false项；按branch升序检查，**六关节原值L2差严格<0.1rad，第一个命中即break**。`normDistance:321–326`不作2π环绕，也不比较独立几何branch或闭链残差。`proj_classes/apc_class.cpp:249–279`证实枚举次序。
RRT根入口115–125仅identify并入树；不像另两个搜索器，它没有显式“两branch均非-1且原collision clear”门。goal同样先identify。已合格保存端点可外部预验并保留原入口行为，但不能把SI恒true误称闭链/碰撞资格。已知的ik项被原identify直接信任，需在记录中区分原保留值与本次真正枚举值。

以下只读取A01 selected_q_rad和LOCAL01保存八支固定project输出，执行差值/范数算术；没有重新计算FK/IK。calc_specific与identify的目标矩阵构造相同，因此该表支持预期原identify标签，但尚不能冒称真实新solve已执行入口：

|保存中心|原role|唯一原L2<.1的branch|命中距离rad|最近其他原返回true根距离rad|true2π最近其他根距离rad|
|---|---:|---:|---:|---:|---:|
|II_0|0|3|4.965068306494546e-16|5.730957010745739|5.179920260571582|
|II_0|1|0|5.087681048629236e-16|1.200260579308926|1.200260579308926|
|II_1|0|0|2.155663185615397e-15|0.9072842358196641|0.9072842358196642|
|II_1|1|3|4.871083751584927e-16|5.44140233415787|5.441393851254049|
|III_0|0|1|1.570092458683775e-16|4.878386076963496|4.878386076963495|
|III_0|1|1|1.070660311630528e-15|5.44140233415787|5.441393851254049|
|III_1|0|3|1.332267629550188e-15|4.678361876209778|4.678361876209777|
|III_1|1|1|5.700831962127702e-16|5.846298726731189|5.0897365424913|

四中心两角色共8项均只有一个命中；II start预期[3,0]、goal[0,3]；III start[1,1]、goal[3,1]。这些实际保存数组中没有容差多命中或2π漏识，不据潜在风险阻止RRT pilot，也不修改0.1或选择规则。
实际路径仍有两类待观察风险：(1)靠近奇异处多个真实branch可能同时落在0.1球内，源首命中可能与独立几何branch不同；(2)q6在原物理±400°范围有周期等价但源IK给主值，原OMPL盒±3.1416甚至略跨真实π，源原差可产生约2π而返回-1。保存端点未体现这些风险，不等于全路径已排除。不能擅做wrap/选最近根/放宽门。
新的观察包装应保留原body，仅记录每次原identify实际调用的q与传入/返回两ik；若候选/距离可直接只读取得则保存，不为审计额外枚举8支或新增IK。独立全路径对每节点的两臂几何branch/奇异集合和树边实际使用branch核对。若有多命中、-1或差异，原source状态保留；相应路径不得凭标签相等通过。非路径树节点不需先验全部数学合格才能运行有限pilot，但不能据它们宣称soundness。

## CBiRRT activeDistance独立代数反例（不阻原RRT）

源码`planners/CBiRRT_PCS.cpp:122–139`中active_chain=1时，读取a的arm2误写qb，再读取b继续写qb；qa为vector(6)的零值。因此结果是||b.arm2||而非||a.arm2−b.arm2||。growTree:161真实调用。令a=b为保存II_0，arm2=
`[1.0042713284452618, 0.2729059574498862, 0.9485892867539307, -1.1501189067527977, 1.8100179182011582, -1.977396290726386]`，则原返回`3.239119425422773rad`，正确同点距离为`0`。这是保存角值纯代数反例，0FK/IK，不是论文理论反例。
最小候选修复仅把active1分支首个`retrieveStateVector(a->state, qa_dummy, qb)`的末参改为`qa`，须新版本独立审查与资格；本报告没有实施。原数值+原控制流、R2数值+原控制流、R2数值+该单处修复应三列报告，不能覆盖历史。该函数不在RRT路径，不能为此停止原RRT有限pilot。

## envII/seed7/range2.6/10s首条真实RRT pilot建议冻结条件

1. 仅envII（source env1）、原RRT_PCS、R2已审查数学数值版本、固定A01 II_0→II_1，不更换起终点或用局部成功点替换。原900/300mm、原base/grasp、原碰撞和branch/限位不变。seed7同时在任何OMPL RNG对象构造前`ompl::RNG::setSeed(7)`及`srand(7)`，保存OMPL/glibc版本、局部种子和实际采样。只给C rand或只给OMPL seed不是完整固定随机流。
2. 原goalBias=.05，原uniform sampler，原全12 NN/steer/插值与原失败fallback不变。range固定为原run脚本envII RRT的2.6；此前root默认2不是用户要求，已纠正，不把header默认2当原run条件。本次一次pilot仍不是原Table I统计。10s为固定有限solve ptc，不因找不到路径增加seed/时长/改range。
3. 一次source solve，保留原状态INVALID/TIMEOUT/APPROXIMATE/EXACT。原`specs_.approximateSolutions=true`且超时可交approxsol，不能把bool(status)当exact。只有exact满足完整独立门才能记“本pilot合格路径”；approx可保存可视化但另标。
4. 原solve内`save2file`返回void；回溯失败只return并不会撤销后续原EXACT状态。其ofstream默认约6位有效数字。须留存原path_milestones/path.txt/log原字节，同时从内存/trace用17位有效数字的JSON保存精确milestones、parent、两ik、每条实际RBS/回溯结果及完整重建节点。不得从舍入txt读回后放宽1e−5mm门；不得将只有milestones的折线称闭链路径。
5. solve外层while检查ptc，单次RBS和solve内save2file可越过10s检查；必须再设外部hard wall/CPU。guard/timeout是项目预算截断UNKNOWN，不能伪造成原返回false或规划普通失败。所有入口/完成计数分列，未返回调用和数据前缀保留，claim及run目录存在即拒绝重复执行。

## 可观测计数与有限失效界限

静态调用边界：start+goal共至多4原FK/32原IK；每随机扩展至多2个calc_specific（每个1FK+1IK），成功后至多一侧未知identify（1FK+8IK）；至多两个顶层RBS；每真实非叶递归至多一个固定branch project（1FK+1IK）及一次原collision。goal bias直接到可达goal时会绕投影，但仍须原RBS。原maxdepth150不能替代CPU/调用帽；其潜在递归树远大于有限budget。

建议冻结以下工程保护帽；它们是截断界，不是算法通过标准、预报调用数或完成数。根代理若采用不同更紧帽，须在运行前写入最终协议。

|类目|建议本次上限|到达后判定|
|---|---:|---|
|source solve|1|禁止重复同一claim|
|source solve名义ptc|10s wall|原返回状态与实际wall分别保存|
|source硬进程帽（含其回溯/保存）|20s wall /40s CPU|截断UNKNOWN；保留运行中的调用与全部输出|
|source随机扩展/identify调用|4096 /4100|CAP_UNKNOWN，禁止增帽后同seed重跑|
|source native IK / native FK|65536 /32768|CAP_UNKNOWN，started/completed分列；collision内FK另列|
|source RBS递归/回溯递归|65536 /16384|CAP_UNKNOWN，不能伪报source false|
|source collision / actual PQP pair query|65536 /7602176|按真实进入/完成计，不用collision×116填实测|
|精确重建path节点N（含端点）|2048|超过则完整path资格未完成，不能抽稀后PASS|
|独立数学arm FK|4096=2N|按实际请求/完成计，完全相同q缓存须绑定原已合格record|
|v3逻辑collision / adapter内部armFK/J|2048 /8192|native/aligned两variant分列；内部started无hook则UNOBSERVED|
|v3 PQP pair query|475136=2048×2×116|按query_codes实际计；未知/engine错误停止|

建议新薄工程（最多2目标，不重建旧四目标）90wall/180CPU；科学整段（source20wall/40CPU+独立完整path门和输出）180wall/360CPU。总耗保守纳R2原3600wall/7200CPU，工程与science分别写execution；冻结前重新读全部最新execution与source/hash，按实际余额取min，不给VI B任何新增候选。完整输出资格若时间不足，保存已检前缀和未检节点清单，整体UNKNOWN，不增加预算、不删节点或改变阈值。
本报告建议的source调用帽要求新观测guard覆盖实际直接calc_specific、identify、原采样入口、递归和PQP。已有pcs_source_trace的每请求64project/64IK等帽仅用于旧固定local接口，不能未经审查沿用到solve；若无法可靠观察某计数，写UNOBSERVED并依硬时间帽，不能伪称完成/帽内。原算法body/static等价核对与低层资格可复用；两次10s plain/trace不应仅因时间截断不同长度就判算法不等价，也不能拿trace耗时作原性能。

## 独立完整path验收（保持既有门限）

每个精确重建节点包括start/goal：12维有限；独立闭链位置maxabs≤1e−5mm、旋转元素差≤1e−5；原physical全12界合法；两臂独立几何branch/奇异集合与实际边branch一致；原native与独立FK（若新增观察）位置≤1e−7mm、旋转≤1e−10。源native collision与v3 aligned结果分列，aligned必须CHECKED且clear，TCP对齐通过；任一碰撞/越界为路径资格失败，无替换样本。
全部相邻节点full12原L2严格<.05，保存每条源RBS通过及完整reconstruct通过、叶覆盖/节点顺序/端点一致；每条边的角色/branch与当时parent、child标签及独立几何身份一致，不能只检首尾或抽稀。source的RBS提前true假设端点已合法；独立门承担端点与精度复验，不将无效端点称论文理论反例。路径中至少有真实中点投影和回溯事件，禁止仅阈值提前返回充当完整实证。
首节点与A01 start逐值一致；末节点与冻结goal一致或满足预定义原GoalRegion阈值且明确记录真实误差。不得自行增加goal tolerance；原ProblemDefinition默认threshold的实际OMPL版本值在冻结时读取或显式记录保持，不运行后选择。需可视化时据精确合格节点生成空间图，图为离散原策略路径展示，不是完整实体/遗漏碰撞pair/CCD证书。
若source称EXACT但完整回溯缺失、闭链/branch不符或精确节点碰撞，则标SOURCE_EXACT_INDEPENDENT_PATH_FAIL并留原状态与最早反例；若只是近周期identity漏识阻搜索，标原source识别限制/UNKNOWN，不未经反例归咎论文。若普通10s没有exact，记录有限pilot未成功，不把任务改成无限换seed。科学三次同机制有据修复后按D079根因审查，仍保留后续完整复现义务。

## 当前保存来源与范围

本报告读取时HEAD为67f007126fddd7ad18229eb360efda2b5684e903；期间其他代理可能新增工作，以最终冻结manifest为准。V4账目14 science+1 engineering：science190.69572716199855wall/134.327012CPU；engineering94.59233520399721wall/130.109068CPU；保守R2合计285.28806236599576wall/264.43608CPU，余3314.7119376340042wall/6935.56392CPU。VI B974/974余0、正式Table I仍0/22500。下列为本审查实际读取时SHA，不作未来执行授权：

|来源|SHA256|
|---|---|
|作者`planners/RRT_PCS.cpp`|`db236f3d24b566e8c2737040936d2dfc3ea71f1aec345285b52dc598125a5509`|
|作者`planners/CBiRRT_PCS.cpp`|`60f6a483c533f61749bc7e741acc72bfc8cc2e137d719b25392e73831e458d93`|
|作者`planners/SBL_PCS.cpp`|`a8ebe8a01ad57347096b03621099f5fdf61f78ebcfb6b1635745cfbf4a8cb407`|
|作者`validity_checkers/StateValidityCheckerPCS.cpp`|`7b6013282f698e47d1f55c2ed31cf0edf52ca6ccf369035016a18e38e42a527f`|
|作者`proj_classes/apc_class.cpp`|`c74ea9ade8bb7d80b0b980139c58b659e6911ab3d3cb61b853be980654ede22c`|
|作者`run/plan_PCS.cpp`|`af868b6ed9bb1253fc2283f6d4d2fe8f3437a91ab349414bc44521892c4b3f69`|
|`results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_0.json`|`b39d945cd5d49e4649aba22e57aae9f302694e4d8e0880389542f1ad828b112f`|
|`results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_1.json`|`991c2efe8e68add65c17375d89c89bbb637711d7125b15a34c84a19a2dc15430`|
|`results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/III_0.json`|`85550cbc3ffbf80c80519b5e592e85401dcf1e96ce747f0df5f3d97c97065c6a`|
|`results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/III_1.json`|`50db8b75e8c29c9dfc42646e5165c22f31dd8e2853858686572405c3cd91cc12`|
|`results/p4_full/20261015_R2_ABB_PCS_LOCAL01/execution.json`|`e0793f6ca95cec240b32a6be36d20b0e3df31cd307054fbe4d7cf97789990c6b`|
|`configs/p4_full/r2_abb_pcs_local_v1.json`|`1b545278f37d60dc4a1b9279ad631b982311fed6723956f17a600a34927f2240`|
|`results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V4.json`|`83bb31df9af137c047122216aca48b823b6c9add2471526cced4d03ef58ee6f7`|

LOCAL01固定根8支完整结果仅作保存数据复用，不重做。原作者数值与R2数值严格分列，RECONSTRUCTED端点不冒充原端点直接通过。RRT一个空间path不完成II全部随机统计，也不完成另外两searcher或其他五环境，更不能证明PCS复杂场景优势。22500正式规划、500000投影、约50000点对、Fig.3–5/Table I–II、全部211义务行仍保留；完整P4仍PARTIAL，结题范围表先交用户审查，不自动P2/Isaac。
