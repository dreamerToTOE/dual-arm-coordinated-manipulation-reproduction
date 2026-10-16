# P4 完整复现：旧 RSS 与 PCS 问题的根因审查

2026-10-14。新增研究分支为 `p4-full-reproduction-pcs-study`，接续基线 `6276f78ce184d54185f299f0bd9a1a7a3267f73a`。旧 P4 `79cc87173e5fad778927d0b4f8b3b0db6e41de7b`、P2 已接受交付和旧修正3/3保持冻结。

我重新核查了旧三方法源码、三次修正、17项数学测试、60个主实验和3个重复试验的记录。旧统计仍为 RSS 0/20、PCS 20/20、NR 20/20；以下新增分析解释这些结果的证据范围，不改判旧失败，也不替代六环境正式实验。

## 1. 审查来源与执行边界

| 资料 | 固定版本/证据 | 读取或实际处理 |
|---|---|---|
| D079规程与29行P4任务 | 新分支基线6276f78 | 完整阅读；按 failure_id 和义务ID对应 |
| 原论文八页作者稿 | SHA256 `193710e5a9d4284cf62b30ff189a1df038a9d5c5ce3f1545525dc2f78bea08c6` | 重新阅读全文，重点II–IV、Fig1–5、TableI–II |
| 旧三法源码与冻结配置 | 79cc871；实验源码3d51ca0 | 只读逐函数追踪；源码/参数哈希留存 |
| 旧原始记录 | `results/20261013_P4_three_methods_round1/round2/round3` | 原记录保留，round3全部主试验按字节读取 |
| 作者ABB代码 | [CKCplanning@909bd72](https://github.com/avishais/CKCplanning/tree/909bd72fff778aca8682c96f9eb86ae4eb75557b) | 只读源码审查，没有调用其IK、采样或规划 |
| 新作者资产审计 | `P4_D079_AUTHOR_ASSET_AUDIT.md`及`author_source_manifest.json` | 新发现全部I–VI相关仓库/分支；旧缺件判断不作为本轮缺件证明 |

我执行了保存输入的独立复数SE(2)几何回放，未导入原模型/IK、未生成随机样本、未调用规划器。约9秒的分析脚本保存9996条原输入的来源哈希和汇总；运行前后旧工作树清洁，源码和配置字节一致。对应文件为 `audit_saved_data.py`、`saved_data_audit.json`；其原始路径和哈希必须随本审查归档，复制时不得改写其运行来源记录。

## 2. P4-RSS-OLD-GENERATOR：最早失败发生在主动端闭合

对应义务：P4-T02、T07、T10、T16、T24。

旧调用路径为 `planner.plan → Strategy.target_sample → 固定q17为0或π → model.ik(raw,0,±1)`。位置见 `baselines/p4_comparison/strategies.py:287` 和 `model.py:127`。我对20个主RSS文件逐项计数，得到313次奇异请求、9996次构造，**全部返回IK_UNREACHABLE**。直伸q17=0有4910次，折叠q17=π有5086次；没有一个生成输入进入碰撞资格。因此碰撞拒绝、奇异识别舍入和RBS接入不是这9996次失败的直接接口。

9996条保存输入实际只有2720个唯一 `(raw_q,generator_branch)`。同随机种子跨环境和预算存在重复，不能把这些记录当成9996个独立抽样来估计未知概率。

### 独立余弦判据

旧正长度杆为 `l=sin(π/38)=0.08257934547233232m`。令后缀局部角累积为 `a_k`，末角 `α=Σq[3:]`，后缀位移 `z=Σl_k exp(i a_k)`。由闭链目标和后缀逆变换，第一端3R去掉第三杆后的腕点为

`w=1−exp(−iα)z−l exp(−iα)`。

两个等长杆必须满足 `|w|≤2l=0.16515869094466465m`，等价余弦为

`D=(|w|²−2l²)/(2l²)≤1`。

保存的9996个输入全部超界。最小腕点半径为 **0.1827381923589296m**，最小D为 **1.4484192245521958**。最小例为 `E0_sparse_budget200_RSS_seed41.json.gz` 的 `singular_log[407]`。腕点中位数约1.02626m，误差量级远高于浮点边界舍入；不能通过acos截断或放宽1e−12边界来修复。

当前可确认的根因是我方重建模型尺度和长后缀均匀分布，使短3R的闭合域在有限预算中完全未命中。**分类：OUR-IMPLEMENTATION，子类模型/抽样与实验设计；局部几何证据高置信。** 原作者空间模型的生成覆盖率尚未知。该结论不证明旧模型无解，不证明RSS理论有误，也不能用于预测新ABB/Comau环境必然失败。

### 固定fixture为何不能替代随机生成

`model.py:238` 的固定fixture由起终点均值、指定q17=0以及p0解析闭合构造。旧原始数学记录确实显示被动Jacobian秩2、两支汇合和两侧RBS桥合格。它没有被插入RSS搜索树、没有进入主实验成功率，是合法的数学正例。它与 `target_sample` 的全角度均匀分布不同，不能作为合法随机生成已经验证的证据。

折叠型还有一个解析潜在限制：等长相邻杆且q17=π时，`vertex18=vertex16`，非相邻 moving_link_17 与 moving_link_19共享端点，中心线距离0，胶囊净距不大于−0.004m。即使某折叠输入通过闭合，也不能通过旧自碰撞政策。此限制尚未成为旧日志的直接失败，因为所有折叠输入先在IK失败；后续不应把它和已经观察的失败阶段混同。

## 3. P4-PCS-OLD-WITNESS：解路径未要求切换

对应义务：P4-T08、T19、T23、T26、T28。

旧PCS真实随机选择p0/p16，APC失败时可尝试另一划分；RBS按照两端共有IK分支检查。候选投影划分与局部连接实际划分不同，必须分别保存。主实验接受节点的候选投影有p16=528、p0=64、精确已有节点=20；实际接受树边有p16=520、p0=92。

20条成功解共有92条边，**全部采用p0**。可比较的连续父子边为p0→p0=52、p16→p16=4，真实跨划分次数为0；树根没有进入划分，不能用紧邻根的两条不同边增加“切换”计数。起终点在p0本来同支，旧数学记录也证明直接p0 RBS可连接。E1增加障碍仍未改变PCS或NR同种子的成功路径。

这不是PCS算法规划失败，而是实验未提供决定性的切换见证和固定划分消融。**分类：OUR-IMPLEMENTATION，子类实验设计不足；高置信。** 后续必须对full PCS和每一种fixed partition分别比较，并保存解上切换点、两侧分支、全链闭合、碰撞、限位及成本。单独选择固定p16作为基线会因旧端点跨p16分支而人为形成很弱基线；固定p0同样必须纳入。

## 4. 工程修正与随机重复的证据边界

三次旧修正依次为Git中文路径解析、精确已闭合奇异解的acos身份保持、NumPy标量JSON转换。旧3/3记录保留；它们不是对合法随机奇异目标零命中进行的三次算法修复。D079的新根因恢复按同一失败机制独立登记，不能倒填旧修正类别或改变原交付判定。

PCS/NR完整非计时重复载荷相同，RSS两次均TIME_LIMIT，但5秒内完成工作量不同，旧完整重复判据失败。新研究应另保存随机索引、实际共同工作前缀和超时位置以区分随机源差异与墙时截断差异。**当前分类：OUR-IMPLEMENTATION中的计时截断/实验规则因素，中高置信；共同前缀尚未逐字段独立复核。** 不重新把旧重复失败改判为通过。

## 5. P4-ABB-RSS-MODE2-STATIC：作者奇异类型需要真实秩检查

这是新增源码风险，尚无新采样/规划实验，不能称为已经观察的作者运行失败。

作者 `sampleSingular` 在一次请求开始时选三种类型之一，后续拒绝循环保持该类型：

| mode | 第二臂固定坐标（零起点） | 静态审查 |
|---|---|---|
| 0 | q[2]=−π/2，q[4]=0 | q[4]=0给出真实腕部奇异；不能由q[2]常数推断又有肘奇异 |
| 1 | q[4]=0 | 真实腕部奇异候选，仍需闭合、限位和碰撞资格 |
| 2 | q[2]=−π/2，q[4]仍随机 | 仅凭该肘角常数不能证明被动6R Jacobian失秩 |

源码见 [StateValidityCheckerRSS.cpp](https://github.com/avishais/CKCplanning/blob/909bd72fff778aca8682c96f9eb86ae4eb75557b/validity_checkers/StateValidityCheckerRSS.cpp#L254)。ABB几何明确 `l2=270mm`、`l3a=70mm`、`l3b+l4=302mm`。等效肘部角为 `α=atan2(302,70)=1.3430303610541368rad=76.94997144633317°`；腕心的两关节Jacobian行列式绝对值为

`|l2[l3a sin(q3)+(l3b+l4)cos(q3)]|=|l2 l34 sin(q3+α)|`。

在q3=−π/2时，该值为 **18900mm²**，并非0。真正肘部退化应满足 `q3+α∈πZ`。腕部q5=0仍可使mode0/1失秩；mode2不能用相同理由直接标为奇异。

这一推导可由作者KDL单臂链的RotZ、RotY、RotY、RotX、RotY、RotX几何交叉核验。固定单臂数学反例 `q=[0,0,−π/2,0,π/2,0]` 满足各关节角界；腕心径向坐标−70mm、肘部因子−18900mm²、腕部sin(q5)=1，解析完整6R行列式绝对值为 **1323000mm³**。这是单臂数学反例，**没有运行新Jacobian程序，没有构造双臂合法闭合样本或核验碰撞**；不能借此断言作者采样实际一定返回了这种构型。

**分类暂为UNKNOWN，子标记AUTHOR-CODE-SUSPECT。** 非奇异肘角推导为高置信；作者运行是否返回误标样本、其他关节是否恰好失秩、实际IK识别/碰撞拒绝是否屏蔽该类型，都需要固定资格数据。没有原论文方法错误的证据。不得静默把q3改成−α或删除mode2后宣称忠实复现；如资格证据确认，进入科学审查并提出独立有界修复。

作者奇异采样也未显式检查整组q2角界；第一臂IK的角界检查不能替代第二臂角界。腕奇异时q4/q6存在连续等价族，作者有限IK规范解未必与实际q2的欧氏距离小于0.1rad，因此不能把 `identify_state_ik()[0]==−1` 一律当作非法。资格应同时保存原生标签、实际被动秩、所有可达分支及奇异哨兵来源，不以标签覆盖几何事实。

## 6. 来源变化与完整恢复路线

新资产审计已找到 `planar_ckc`、ABB完整仓库、`ckcComau2`、`ckcComau/industrialScene`和`ckcComau3`，能追溯I–VI多数几何、抓持、端点和算法。旧“未找到完整输入”的审查属于当时已查来源范围，不改写旧审计；本轮不能沿用该理由跳过环境。当前尚待核实的是依赖准确版本、生产试验种子、公开数据与最终论文表的一一链路、许可证和VI不完整代码，分别登记，不笼统称原模型不存在。

我建议先按作者ABB模型和原生成分布做有界资格，按生成类型记录另一臂IK、闭合、两臂角界、真实碰撞、被动/整体Jacobian秩、分支身份、最近邻距离及RBS接入。该资格只验证接口和机制，不能替代原500次正式规划、500000投影样本或约50000合法点对。

后续各失败按独立 failure_id 保存唯一变更、源码/输入哈希、真实正负例、竞争解释和预算。确认我方实现问题后按D079有界修复；作者资源或方法冲突则分别提供证据并交审查。原判据、种子和失败记录保持不变。P2、Isaac和双FR3适配不进入本轮执行范围。


## 2026-10-15 — 原RRT_PCS取得第一条独立合格空间路径

工程85acfd5来源E2E_BUILD01成功，wall17.12737691100483/CPU23.727903；1a5b811冻结E2E01，原RRT_PCS环境II、seed7、原采样盒与恒true callback、range2.6/goalBias.05、10s单次solve实测exact非approx，solve段.016837364s，整次wall.2776374349996331/CPU.19540999999999997。4里程点、6树节点/5树边、3段原成功回溯，连接角色/branch依次(0,3)→(1,3)→(0,0)，有2次真实角色切换。使用A01 RECONSTRUCTED端点和R2几何一致数值，原始端点及native失败保留，不能冒充原作者原输入直接通过。

b4cbbff冻结完整路径后审PATH01：177/177原密集节点、176叶全部通过独立闭链、原机械限位、每边被动branch及v3对齐原离散碰撞策略，最大闭链位置3.410605131648481e-13mm、旋转4.440892098500626e-16；叶距max.04949053472601928<.05。实际354数学FK、354分支、177collision、708adapter内部FK/J、41064PQP；wall40.94035644100222/CPU1.1020530000000002。原source执行仍保留PENDING历史，独立后审新文件单独给PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH，不改写旧execution。

18execution=16science+2engineering，R2总wall343.63343315300244/CPU289.461446，余3256.3665668469976/6910.538554；VI B974/974余0，正式Table I0/22500不变。最新211项新表保前73历史列，另8列本路径实证。新V5保全审查PASS：1028旧科学文件、57崩溃文件8482891bytes、tar57成员、另5工作树及13未提交文件、旧V4均保持。

原导出随机IKproject/sample_q缺陷不在真实RRT调用链；CBiRRT activeDistance同点非零缺陷尚待版本化修复；原PQP638个BeginModel警告及原统计时间域差异保留。路径资格仅原离散策略，不保证CCD、完整实体杆件/省略碰撞对，也不证明PCS性能优势或完整论文。随后普通NR C++逐式移植/trace等价资格，与RSS解耦；大规模正式实验仍须端到端资格后成本pilot另审。全部原文211项义务保持，不P2/Isaac。详见reports/P4_FULL_R2_ABB_RRT_PCS_PATH_POST_TASK_20261015.md、最新ABB_RRT_PCS覆盖表及V5账本。


## 2026-10-15 — ABB NR固定64移植资格实际通过

c68fa76冻结后的唯一Q1执行完成：II32+III32、C++plain64/trace64/原Python64共192派发与192完成，64跨语言、64历史重放、64独立终态全部通过。q最大差4.440892098500626e-16rad；终态最大位置8.342067303601652e-7mm、旋转矩阵1.50461743064767e-9，原1e-5门不变。Python原NR内部864/864 armFKJ，独立终态128/128；C++内部started/completed仍UNOBSERVED。actual7.05127794699365wall/7.9173490000000015CPU。详细源码、命令、版本和差异见reports/P4_FULL_R2_NR_ABB_Q1_POST_TASK_20261015.md；独立保存证据审查另存，不借0exit或同失败证明能力。

20execution=17科学+3工程保守总359.4902552519934wall/309.65925300000004CPU，旧V5保持，新V6逐own实耗一次。资格标签仅PASS_FIXED64_NUMERICAL_TRANSFER / RECONSTRUCTED_PHYSICAL_FULL_NR_CPP，不是作者KDL轨迹/公平速度或全随机空间投影能力。下一步原GD薄接缝、原NR非平凡RBS/回溯和原RRT入口，先独立PRE/版本/预算冻结；源sample_q未达调用链问题不捆修。VI974余0、正式0/22500、全部211义务不缩。原失败保持，不P2/Isaac。


## 2026-10-16 — 普通NR原GD/SVC/RBS固定局部资格通过，真实规划仍待

7ee551a冻结后LOCAL01唯一执行20/20顶层（4端点+3边RBS/回溯各plain/trace）、10逻辑对binary64和非计时计数一致；3/3非平凡原RBS与完整原回溯通过。147/147全唯一节点/全部来源ref经独立闭链、原3.1416机械界、v3 aligned离散源碰撞合格；max位置9.887878832159913e-6mm/旋转2.5558390071012127e-8，在原1e-5门内，三路径65/65/17节点、最大叶距.04769340858982442<.05。traceGD286/原PQP33150；数学逐臂FK/J294、adapterFK/J588、collision147、native/aligned共34052PQP均实际观测；plain内部UNOBSERVED。原nativeTCP不一致147节点保留，非换门改判。标签RECONSTRUCTED physical full NR +原SVC/RBS控制流，非原KDL轨迹或论文速度。

actual3.6995257820017287wall/4.245554CPU；新工程22.57619615099975wall/31.233423CPU为独立build-only。22execution=18科学+4工程，保守R2累计385.7659771849949wall/345.13823CPU，原3600/7200帽保持。VI974/974余0、正式TableI0/22500和211项全部义务保持。新V7账及完整对照表继承前90列211行逐值不变，新增8列；原V6不改。

runner作者另写保存审计117258/117258（personnel_independent=false），第二代理独立事件树/矩阵算术/资产审计218766/218766及raw-link补审666/666通过，0新科学。大JSON原字节本地保留，确定性无损gzip与SHA manifest入Git；不删除或重跑原失败。详见reports/P4_FULL_R2_ABB_NR_LOCAL_POST_TASK_20261015.md、两份POST与RAW_LINK_ADDENDUM、reports/P4_FULL_R2_ABB_NR_LOCAL_SAVED_POST_ARCHIVE_20261016.json。

环境II下一有限planner门已通过，但尚无NR起终点路径：下一项另冻原RRT_NR单target工程45/90、II seed7单次10s solve外帽30/60、完整独立路径另120/240/max2048，不自动连跑、不调seed/门限/端点。PCS随机三参helper H与CBiRRT距离D仍独立草案未运行；RSS原RBS/分布/入口解耦诊断且不追加VI构造。正式大规模成本pilot需相关端到端资格后安排并向用户报预算，不缩完整原文统计、不P2/Isaac。


## 2026-10-16 — 原 RRT_NR 首条完整空间起终点路径已独立合格

II seed7 的唯一原 RRT_NR solve 得到 exact 非 approximate、7 milestone、55树节点/54树边，6次原完整回溯均true。原source execution的PENDING历史保持；单独完整PATH01检查393/393唯一节点和392叶，通过数学闭链、原机械界和v3 aligned原离散碰撞。最大位置9.793997321594361e-6mm、旋转矩阵3.0701365727470176e-8，最大叶距.0478001489336342<.05rad；最小原界余量.046633132713711944rad。实际数学臂FK/J786、adapter内部1572、collision393、PQP91176（双worker各45588）；原native TCP不一致393记录完整保留。

工程28.08202379599993wall/34.574132999999996CPU；solve执行1.7845762399997511wall/1.7793930000000007CPU；完整path3.7730926529998214wall/3.9572699999999985CPU。V8按25 execution=20科学+5工程逐自身成本一次，累计419.4056698739944wall/385.449026CPU；原3600/7200帽保持。保存算术后审36348/36348（作者兼runner，人员独立=false），另代理人员独立24448/24448全部通过，0新科学/编译。V8保全通过：1028旧科学文件、57崩溃文件及tar、另5worktree/13未提交文件、旧V7和211行前98列均保持；新表另8列证据，不删原义务。

本路径使用A01 RECONSTRUCTED端点与重建physical full NR接缝，不能冒充作者原输入/KDL轨迹或公平速度。仅原离散source policy，非CCD、完整实体/省略pair安全、成功率/方法胜负或完整论文。详见reports/P4_FULL_R2_ABB_RRT_NR_PATH_POST_TASK_20261016.md、两份保存POST、V8账和NR_RRT_PATH完整对照表。VI974/974余额0，正式TableI0/22500与全部原文统计规模保持。

下一项随机三参helper H的缺break返回修复单独冻结有限资格；H不在已合格RRT实际grow调用链。CBiRRT距离D、其他搜索器/环境、RSS原RBS/分布/入口依次诊断；新科学设计/新增VI/正式大预算另审。相关端到端资格后做可重复成本pilot，不提前正式大规模，不P2/Isaac/结题Word/PDF。


## 2026-10-16 — H真实随机三参返回修补：控制流完成、完整终态门墙钟停止

d53a68c固定16context×2控制流×plain/trace共64真实helper全部正常返回；32binary64模式对、16首次成功prefix全部通过，原32false、成功break32true，主动角不变。H不在原三planner真实grow调用链，不据此宣称规划提升。工程2target各exit0，actual24.520090279000215wall/33.067454999999995CPU；工程283/283保存审查通过。原builder/PRE保持；science preflight漏计新工程被26prior断言拦截，未建科学claim前最小修science_prior，修前字节和诊断保留。

独立终态仅34/64完整通过（原false32+修true2）。第35数学门已完，native/aligned两raw worker已返；adapter在总60wall帽处捕获Timeout，aligned内部第140FK/J未完成，实际139/139，仅native变体入adapter结果；不能将raw拼成完整资格。两个partial JSON可解析，原stopped_partial保存二次timer诊断保留。原STOP_CLEANUP_OR_EVIDENCE_ERROR及IDs34..63的30条UNKNOWN不改，不重跑helper/原claim、不自动放宽帽。实耗60.50938905899966wall/39.185680000000005CPU含收尾全扣R2。

人员独立saved后审12622/12622通过仅支持STOP前缀证据一致；原V1报告MD纯展示TypeError另存后V2重审，0科学。64输出19个env+q12字节键，完整34覆盖12键，另7键先查历史精确证据；不以近似角/source true替代物理门。原native TCP mismatch34单列。真实35数学门/70数学臂FK/70geometry、35adapter（1error）/70worker/139adapterFKJ，完整门PQP各3736而全部raw各4060，统计层级不混；plain内部与rand真实计数UNOBSERVED。

V9共27execution=21科学+6工程，自身成本一次累计504.43514921199426wall/457.702161CPU，原3600/7200帽余3095.5648507880057/6742.297839。V9保全PASS，旧1028科学文件、57崩溃文件及tar、另5worktree/13未提交、V8和211行前106列均保持；新表另8列H证据。VI974/974余0，正式0/22500和全部原文统计规模保持。详见reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_POST_TASK_20261016.md、ROOT_INDEPENDENT_POST及V2、V9和HELPER_H完整对照表。

继续原IV wrist-only固定100/800数学组件与其他原RBS/分布/入口资格；CBiRRT距离D独立因子先静态冻结。H必要的后续外门先据现有成本和精确去重另冻，原64资格STOP不改。正式大规模仍待相关端到端资格及成本pilot预算申请，不P2/Isaac，不提前结题Word/PDF。

2026-10-16 H计数勘误：上段全部70worker raw的PQP各4060为报告笔误，逐文件实际query_codes重计及作者8200/8200保存审查确认应为native/aligned各3852；完整34门各3736不变。只更正报告，不改科学execution、raw、STOP或预算。


## 2026-10-16 — IV零查询停止已保全，H64输出既有证据链接通过

IV固定100/800 run01在首模型前因我方metadata guard退出，0target/FK/IK、800未执行。R1 q1 literal±3.1416与runtime degree×3.1416/180相差1ULP；不改实际限位或科学门，v3须分来源精确冻结，原STOP和v2保留。原30/60共享预算扣01后仅余29.96328463000009wall/59.963233CPU，不重置。H64真实helper仍STOP/34完整门/30原UNKNOWN；另398/398人员独立精确保存证据链接覆盖64输出19键，0新科学，SAVED_REUSED_EVIDENCE_ONLY。全部70worker原raw PQP仍各3852，完整34门各3736。

V10按28execution=22科学运行账（含零查询失败）+6工程逐自身成本一次：累计504.47186458199417wall/457.738928CPU，R2余3095.528135418006/6742.261072。V10保全PASS，旧1028科学文件、57崩溃文件8482891bytes及tar、另5worktree/13未提交、V9和211行前114列保持；新表122列另列IV与H保存链接。VI974/974余0、正式0/22500，全部原文义务和统计规模不缩。见IV_RSS_WRIST_ZERO_QUERY_POST_TASK、H_ALL64_SAVED_CERTIFICATE_LINKAGE及IV_PREFLIGHT_H_SAVED完整对照表。先完成IV版本化入口修复资格，CBiRRT D另阶段冻结，正式成本pilot/预算后续，不P2/Isaac。


## 2026-10-16 — IV固定100/800数学组件全部完成，保留794原解析拒绝

697b519冻结v3后唯一run02完成100/100目标、800/800原分支请求与诊断，106数学armFK/J，6accepted全部独立回代/闭链sound，G0/G1均6分支/3targets（s040/s056/s092各b1,b3），794仅ACTIVE_IK_REJECTED，UNKNOWN0。100被动rank5，6accepted主动/完整闭链rank6；最大闭链位置7.105427357601002e-13mm/旋转矩阵2.498001805406602e-16。实际5.185225903000173wall/2.800878CPU；原01零query失败保持，01+02共享耗5.221941273000084wall/2.837645CPU，100/800清单已完整执行，剩余时间不授权新样本/重跑。标签PASS_RECONSTRUCTED_MATH_ONLY，0collision/RBS/NR/RNG/solve/新VI，不是原RSS分布/规划资格或论文FULL。

v3只改pre-loop精确表示guard，真实限位/科学循环/阈值不变；独立静态35/35及root核通过，工程实施者saved后审6386/6386并披露身份。V11共29execution=23科学账+6工程，own成本累计509.65709048499434wall/460.539806CPU，R2余3090.342909515006/6739.460194。V11保全PASS，旧1028科学、57崩溃文件/tar、另5worktree/13未提交、V10/211前122列保持，新130列表。VI974余0、正式0/22500与全部211义务原分母保持。见IV_RSS_WRIST_FIXED100_POST_TASK、02_SAVED_ENGINEERING_POST和最新IV_WRIST_MATH覆盖表；人员完全独立保存审查另5667/5667通过，0新科学，矩阵/J及独立谱秩算术均吻合，报告RUN02_INDEPENDENT_SAVED_REVIEW另档。下一项CBiRRT D两target工程先冻结，后distance/local/单solve分阶段；RSS解耦推进，正式大预算另审，不P2/Isaac。


## 2026-10-16 — CBiRRT D两目标仅工程通过，距离/局部/solve尚未执行

fc3495b冻结BUILD01唯一执行，两target exit0、BUILT_NOT_QUERIED，40.88476686000104wall/56.09734399999999CPU；完整可逆13body观测、单token qb→qa、无H，旧资产与原失败保持。人员独立保存审查301/301通过，0新科学。新binary虽有distance/local/solve三入口，本次binary_execution/query/solve均0，不报算法资格。

V12共30execution=23科学账+7工程，累计550.5418573449954wall/516.63715CPU，余3049.4581426550046/6683.36285，VI974余0、正式0/22500。保全PASS：旧1028科学/57崩溃文件及tar/另5worktree13未提交/V11与211前130列保持，新134列完整表。见CBIRRT_D_BUILD_POST_TASK与BUILD01_SAVED_INDEPENDENT_POST。下一D64真实距离另冻15/30，原错误对照与修复版plain/trace、state不变、原body计数及EOF全部独立检查；L/S/P各阶段另冻，全部原文义务不缩，不P2/Isaac。


## 2026-10-16 — D64原15秒门61/64完成，62raw保存，原STOP保持

唯一source a20318c DISTANCE01实测STOP_FINAL_WALL_OR_CPU_BUDGET，wall15.463848030998633/CPU.9817729999999999，原61complete/UNKNOWN61,62,63不改。实际62dispatched/完整raw，第61index经另saved510/510核对通过，但原UNKNOWN保留；62/63未派发，不用公式补执行。原saved1062/1062通过；8PID全reaped、raw至EOF，4mesh+30distance真实body，plain内部UNOBSERVED。约10.5401秒在响应后的保存/检查窗口，支持工程I/O或调度开销，无syscall计时不妄归具体原因。

V13共31execution=24科学账+7工程，已保存own-cost测量之和wall566.00570537599401/CPU517.618923。最终execution持久化额外费用未独立测，标UNKNOWN；余额仅帽减已测成本的上界，不宣称精确全进程账。原15/30已耗不重置。可按既有R2授权准备只原未派发62/63的版本化TAIL02，拟5/10独立资格帽计总R2，不涉及VI/正式扩张；先全部条件/PRE/源码独立审查冻结再执行。旧0..61仅saved复用，新合并只能SPLIT标签，不改原D64STOP或绕L12门。

V13保全PASS，旧1028科学/57崩溃文件tar/另5worktree13未提交/V12与211前134列保持，新138列表。VI974余0、正式0/22500、全部原文义务不缩，不P2/Isaac。见CBIRRT_D_DISTANCE_STOP_POST_TASK、两份保存独立后审和SAVED_WALL_DIAGNOSIS。


## 2026-10-16 — D64仅补未派发两项完成，分次保存资格独立通过

095c56c冻结TAIL02后唯一执行，仅原62/63、D-fixed/III/trace/seed7，1新进程/2请求均正常返回、exit0/reaped、新UNKNOWN空。旧0..61只精确复用raw；1374/1374人员独立保存检查通过，全部64响应/32plain-trace对/9真实进程、原六维L2/state/对称/role0/四原同点反例完整核对。标签SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO，仅距离接口分次证书；原D64 STOP、61complete、UNKNOWN[61,62,63]、末-9和false门永久保持，不能宣称原8进程单run通过。trace累计5mesh+32distance，plain内部/库seed draw仍UNOBSERVED；close_group仅冻结源码成功门推断，不冒称保存现场快照。

本项内部样本.9946544039994478wall/.9409050000000001CPU；独占外层GNUtime覆盖最终execution/receipt/退出，上界1.21wall/.99CPU，满足新5/10且只替换计费一次。V14共32execution=25科学运行账+7工程，累计chargedwall567.215705375994/CPU518.608923；历史D64末端未测尾部仍UNKNOWN，余额仅上界。新V14保全PASS，旧1028科学文件、57崩溃文件8482891B/tar、另5worktree13未提交、V13/211前138列逐值保持，新142列完整表。VI974余0、正式0/22500、全部原文义务及统计规模不缩。

见reports/P4_FULL_R2_ABB_CBIRRT_D_TAIL02_POST_TASK_20261016.md、TAIL02_SAVED_INDEPENDENT_POST、CBIRRT_D_TAIL_SPLIT完整对照表。下一L12须新版完整前置契约消费真实TAIL02/独立aggregate/外层上界/V14，不能OR状态绕原L门；原L源码/PRE保留。拟原3边12调用、30/60、无新独立物理oracle；通过后S单solve与P完整路径分阶段冻结。正式成本pilot/大预算仍后续，不P2/Isaac，不提前结题Word/PDF。


## 2026-10-16 — CBiRRT D三条原局部接缝完整通过，保持原STOP与分次来源

4ffdda4冻结LOCAL02唯一运行，原3边角色/branch(0,3)/(1,3)/(0,0)×RBS/回溯×plain/trace共12/12真返回，6模式对binary64一致，UNKNOWN/diagnostics空。完整M80/65/34逐binary64等于旧原路径，才复用177唯一节点/176叶的旧独立闭链、branch、原机械限位及aligned离散碰撞证书，0新独立物理查询。两个SVC进程72046/72048均exit0/reaped、raw至EOF，起闭进程组现场快照均已保存。trace真实各entered/completed：stateRBS3/vectorRBS349、state回溯3/vector回溯349、固定branch投影/nativeFK/nativeIK/collision各346、mesh1；plain内部未观测。无CBi/RNG成员构造、solve、compile或新VI。

人员独立保存后审19150/19150、0失败、八AND门全true，外层监督通过；独立POST SHA9c2445a2d8ff25aac353dc06e677dfd0f12573bbce0cfd620fdefb294431adcf。内部样本2.31582639899716wall/2.071816CPU保留；外层原行2.46/1.86/.25/0，上界2.47wall/2.13CPU覆盖worker导入/preflight/清理与最终execution/receipt/退出，满足30/60，并只替换本项计费一次。supervisor自身持久化费用范围外；历史D64记录尾部UNKNOWN不补0。

V15实际33execution=26科学运行账+7工程，累计charged569.685705375994wall/520.738923CPU，R2余额仅上界3030.314294624006/6679.261077。新211行146列完整对照表前142列逐值保持；保全实际PASS：1028旧科学文件、57崩溃文件8482891B/tar、另5工作树13未提交、旧V14保持，无mismatch。见LOCAL02_POST_TASK、LOCAL02_SAVED_INDEPENDENT_POST、CBIRRT_D_LOCAL完整覆盖表及V15账/保全。

本证书仅PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED，D来源仍SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO；原D64 STOP/61complete/UNKNOWN[61,62,63]/末-9/false门与H STOP/30UNKNOWN永久保持。不证明新的CBi全局路径、连续碰撞安全、RSS或PCS优势。旧PCS177/NR393路径不覆盖；VI974/974余额0、正式TableI0/22500、全部211原文义务与统计规模不缩。下一S固定II/seed7单10s solve及30/60需另冻结，原EXACT仅候选待P独立路径门；正式成本pilot/大预算后续，不P2/Isaac或提前结题Word/PDF。


## 2026-10-16 S01 transport 中止、独立失败费用与V16实际交付

S01 source6ac452b已实际进入原CBiRRT solve，唯一dispatch；我方接收器将55B setup debug误作JSON而STOP_PREFIX_RETAINED/JSONDecodeError，源78833末−9/reaped。完整JSON0、raw gate=false；solve完成/EXACT/树/M/路径UNKNOWN，不能报零solve或算法失败。trace mesh/identify/FK/IK完成1/1/2/16，collision id20 entered未返。原失败、源码、claim和全部raw保留。setup临时range3.415829；solve原setRange(Range)使实际grow仍2.6。

独立S01保存POST实际2688/2688、失败0，仅失败前缀保全及费用身份通过；successful_transport_qualified=false，非路径/科学PASS。外层exit1上界1.44wall/1.14CPU只替换内部样本一次。主POST personnel_independent=false，见 reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE01_POST_TASK_20261016.md；独立JSON SHA2263c58e15b65930fd07d616f0b94c040b3d89e48bab3a46bab6780777de41fb。

V16已实际34execution=27科学账+7工程，charged571.125705375994wall/521.878923CPU；R2余额上界3028.874294624006/6678.121077。完整表211行150列保前146，stem CBIRRT_D_SOLVE_STOP；V16保全passed=true，1028旧科学文件、57崩溃文件8482891B及tar、5其他工作树13未提交、旧V15/历史列无mismatch；历史未测尾部仍UNKNOWN。S02另冻精确一次55B前缀+唯一JSON接收器，原30/60共享余28.56wall/58.86CPU，不重开预算、不改源或科学条件；本补记零科学执行。原D/H STOP及UNKNOWN、旧PCS177/NR393保持，VI974/974余0、正式0/22500和211论文义务不缩减；原EXACT仍须独立P路径门，不提前正式大规模/P2/Isaac。


## 2026-10-16 S02 原生EXACT候选、独立入口审查与V17实际交付

S02 source4065ac6，固定II/seed7/原range2.6/10秒solve，只改我方接收器精确一次原55B setup日志+唯一JSON；唯一源85119 exit0/reaped、diag空、完整raw gate=true。原SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT、6Motion/5milestones；五次reconstruct[T,T,F,T,T]，M[109,145,2,33,129]。原role0 false29266/M2及role1 fallback true29271/M33全部保留，四真M完整物化413唯一/412叶，未作物理P，不把false两点当成功边。

人员独立S02保存POST实际5284/5284、失败0，schema P4_SOLVE02_SAVED_INDEPENDENT_POST_V1/status PASS_SOLVE02_TRANSPORT_EVIDENCE_INDEPENDENT_POST，SHA730dbb69ff3749975639dd9cad2fe1f31ca45cb2bf370c0470cfddd329d64412。入口/费用true，independent_path_qualified仍false。外层9.55wall/8.75CPU替换内部sample一次；S01+S02共享累计10.99/9.89<原30/60，不重开帽、不回写旧false字段或S01失败。

V17已实际35execution=28科学账+7工程，charged580.675705375994wall/530.628923CPU、R2余额上界3019.324294624006/6669.371077；历史未测尾部仍UNKNOWN。范围表211行154列保前150，stem CBIRRT_D_SOLVE02；V17保全passed=true无mismatch，旧科学/崩溃文件、其他工作树和历史列保留。主POST见 reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE02_POST_TASK_20261016.md，personnel_independent=false。下一P全413/412独立物理门待冻结，120/240/2048帽、不截尾、不重新solve。本补记零科学调用。原D/H STOP与UNKNOWN、旧PCS177/NR393保持；VI974/974余0、正式0/22500及211论文义务不缩减，不提前正式大规模/P2/Isaac。
