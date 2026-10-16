# R2 ABB CBiRRT 因子 D：最小分阶段资格 PRE 草案

2026-10-16。**STATIC_PRE_DRAFT / NOT_FROZEN / NO_NEW_BUILD_OR_SCIENTIFIC_EXECUTION**。本文件只独立复核保存的16组角度算术、原调用链、既有合格证据和实际成本；不是可执行协议，也不把候选标为已合格。0编译、0原C++接口、0 FK/J/IK/NR/碰撞/RBS/RNG/solve、0 VI构造。对应紧凑来源记录为 `P4_FULL_R2_ABB_CBIRRT_D_STATIC_PRE_EVIDENCE_20261016.json`。

完整211项义务、原论文全部统计分母保持。既有II的PCS 177节点、NR 393节点离散起终路径保持，不重跑或改判；正式Table I仍0/22500。VI为974/974、余额0。本候选与H随机helper、IV腕资格及RSS独立推进，不把H资格作为D前置，不向D stage混入H的break。

## 已独立核对的缺陷与真实影响位置

原 `CKCplanning@909bd72fff778aca8682c96f9eb86ae4eb75557b` 的 `planners/CBiRRT_PCS.cpp:122` 中，role1先从a把arm2写入qb，随后从b再次覆盖qb，qa保持六个零；实际公式为 `norm(b.arm2)`。`State`确为`vector<double>`，不是未初始化内存。现有16组保存算术全部重新核对一致；四个同点反例依次为3.239119425422773、4.128865608898457、1.665155567082146、2.4702822659418953 rad。**这些仍是源码语义与保存数组算术，尚非运行原C++函数。**

单因子 `CBIRRT_ROLE1_FIRST_STATE_DESTINATION` 仅将role1首次retrieve的第三实参qb改为qa；原文件SHA256为`60f6a483c533f61749bc7e741acc72bfc8cc2e137d719b25392e73831e458d93`，预测候选为`5b87ed08d674251594efc899ad922398f9c29a0a42f74494cafa7fa2424ae5c2`。现有纯字节候选函数可整文件逆变换还原。原native和R2该文件相同，但不因此混淆两套APC数值或整体资产。

真实链为 `solve→growTree→activeDistance`。d参与 `d>maxDistance_`、12维插值比例`maxDistance_/d`及reach判定；grow每次用原`rand()%2`选角色，extend/connect上限原100/500。**NN本身绑定header的`distanceFunction→si_->distance`，是全12维距离。** cpp中“NN over the active distance”注释与代码不符；D不是NN修复。不改该NN、角色随机流、range、插值、APC、branch fallback、RBS、障碍或门限，不由本缺陷推断论文PCS理论错误。

原 `run/plan_PCS.cpp:126` 为validity checking resolution **0.02**（注释“3%”不作为参数）；CBiRRT paper II/native1 range **2.6**、paper III/native2 **1.0**。RBS原`RBS_tol=.05`、最大深度150、withObs=true，均保留。原grow先按共branch尝试role0 RBS，失败后才role1，不是按新距离重新挑分支。

## 直接继承的证据与必须新建的入口

|现有资产或证据|本候选用途|是否重建或重跑|
|---|---|---|
|PCS BUILD01四目标、LOCAL01及其所有原失败|固定branch、非平凡RBS、回溯、plain/trace来源；原PARTIAL保持|不重跑整套LOCAL矩阵|
|原RRT_PCS E2E01、PATH01|II的完整177节点、176叶和三条原回溯边；固定回归输入及独立物理证据|原实验不重跑|
|原RRT_NR E2E01、PATH01|393节点完整路径和persistent外门工程经验|不把NR模型或结果混入PCS|
|v3碰撞manifest下既有native/aligned worker、独立ABB FK/branch oracle|新CBi路径逐节点外门，原闭链/界/branch/碰撞门|复用旧binary，无新编译|
|旧PCS thin binary|只支持limits/project/rbs/reconstruct，不导出D或CBi solve|不能拿它当D或CBi入口|
|旧RRT_PCS E2E binary|只构造原RRT，虽可复用I/O设计|不能拿它当CBi入口|
|新source-control与D-fixed stage各一个binary|同一个受限driver提供distance、local、one-shot solve模式；plain/trace仅观测flag|必须新工程，先冻结后仅构建一次|

建议一个R2数值基底、两source版本足够隔离D。distance不调用模型，不必再建native/R2四目标；原native数值失败继续保存。builder须从原geometry_consistent_plain新复制，禁止修改旧stage。控制版与修复版除D及同构观测/独占输出I/O外全字节一致；二者均不启H补丁。新binary应一次包含后续已审入口，避免每个小门重新编译。工程成功不自动允许science，后续逐阶段独立冻结claim和实际账。

## 阶段 E：有限工程，只编译不query

拟两目标，每目标45秒墙钟/90秒CPU，两目标合计60/120；超总帽时保存已完成目标和失败前缀，不补编译或覆盖stage。链接原APC、SVC、collision和CBiRRT，不为未用搜索器再链接RRT/SBL。source-control保原错误；D-fixed只施加单token修复。

新driver可通过派生probe公开受保护Motion/activeDistance，不改原header保护级别。distance/local模式不得调用setup/solve或抽样；构造器读mesh单列，不能报成碰撞查询。原CBiRRT还含`ompl::RNG rng_`成员，构造原对象会发生RNG种子初始化；不能把“距离不抽样”写成“整个进程没有RNG初始化”。需静态与实际计数区分：未插桩内部调用不得用返回数反推true_started。所有工程源码、原源与观测变换、库/编译器/mesh/hash、命令、stdout/stderr、父进程与活动进程组CPU、旧stage保全均先审查。

## 阶段 D：先运行真实原距离接口

拟15墙钟/30 CPU；固定保存16case，source-control/D-fixed × plain/trace，共64次真实原activeDistance。每case使用对应环境保存start/goal的有序点对与role；不跨环境配点。建议每source×mode×environment独立新进程，共8个进程，每进程8个距离请求，OMPL对象前固定`setSeed(7)`；原planner的8次构造及直接rng成员初始化单列，库内部未hook的种子生成draw数标UNOBSERVED，不假写0。把完整原12角写入OMPL state，再直接调用原函数；不运行grow、IK、RBS、collision、rand/shuffle/sampleUniform或solve，距离体与观测均0抽样。

原错误版必须复现保存公式和四个同点非零反例，不能要求它满足距离公理而改判整个对照失败。D-fixed两role均对六维L2独立参考绝对误差≤1e-12；同点严格0、交换对称；role0两source版逐值相同。每版plain/trace的输入、返回和不可变state一致，观测零额外模型/随机调用。保存完整64请求/响应、source/body/二进制链、前后资产与预算。仅此门通过只允许报`PASS_FIXED16_ACTIVE_DISTANCE_INTERFACE`，不能报规划器合格。

## 阶段 L：仅验证新stage接缝的原非平凡RBS与回溯

不另造成功fixture，固定取旧RRT_PCS E2E01的**全部三条**原里程点边，原序号0/1/2与角色/branch分别为(0,3)、(1,3)、(0,0)，保存回溯节点数80/65/34。输入和参考直接绑定 `runtime/reconstruction_attempts.jsonl` SHA256 `2aea2a4b79c280d09543a3d2f7f675422c3479c6440d4802e33ca5c66f7c2b26`；不从低精度txt反建角度。

建议仅在新D-fixed binary做3边×原state-level checkMotionRBS/reconstructRBS×plain/trace，**12个顶层调用**，拟30墙钟/60 CPU。local模式只构造原SVC，不构造CBiRRT/RNG成员；D本不参与这些函数，控制版SVC字节相同不必再做相同12调用。state-level重构入口保原先push首末，再调用原向量递归，不用自写递归替代。原完整body按已审返回lambda观测；trace不额外FK/IK、random或碰撞。

要求12返回均true、三边都有真实非平凡中点，plain/trace投影输入与返回逐值一致；新重构完整q序列须与旧80/65/34保存序列binary64逐值一致。这样可继承旧177个唯一节点的独立闭链/branch/界/碰撞外门，**无需再次查询同节点物理检查**。若新stage输出不同，不以ε放宽等价、不截掉节点、不另选边；保存差异停止接缝门，先检查工程/编译/观测解释再冻结新路线。原旧资格结论不随新stage失败改判。

## 阶段 S：单次真正空间CBiRRT规划入口

仅当D/L通过，再冻II、seed7、原range2.6、原12维采样盒（含q6±3.1416）、恒true callback、resolution .02、10秒solve。原CBi没有RRT的goalBias参数，**不得拷入`.05`或调用setGoalBias**。`ompl::RNG::setSeed(7)`和`srand(7)`在OMPL对象构造前各一次，原`rand()%2`/sampleUniform/nearest及100/500迭代保留。起终点用已合格A01 II_0/II_1，分别保原branch3/0，分类明确为`RECONSTRUCTED_ENDPOINTS_AND_R2_NUMERICS / D_SINGLE_TOKEN_CORRECTION / AUTHOR_CBIRRT_SEARCH / OBSERVED_IO`。

拟一个新D-fixed入口、**恰1次solve**，整次30墙钟/60 CPU；不另跑source-control solve、第二plain/trace solve或换seed。本阶段目的为固定候选的有限资格，不推断修复的成功率/速度效果。原错误动态证据已在D门64真实调用保存；未来性能对照仍需完整新冻结，不由单次成功免除原文对照。

保持完整原solve/grow/save2file数学体，只追加返回后观测。至少保存真实activeDistance角色/输入/返回及计数、原identify、state-level RBS/回溯所有真假返回与完整q、两个树的成员/parent/root/branch、connectionPoint、最终原高精度milestones及原文本输出。记录同q不同Motion身份或稳定运行内ID，不能仅按相同角度误合并树节点。trace覆盖若不足，单列UNCOVERED，不改seed补覆盖。

`save2file`的`../paths/`和`./paths/`在本次全新独占run内部同时提供相应目录，不向历史路径写入；原temp删除改为保留仅为已审I/O偏差，不能夹带修路径。原smoothing注释保持。若source没有exact连接，避免为“补数据”调用依赖空connectionPoint的原getPlannerData；保留TIMEOUT/INVALID和当时输出，树前缀可由只读probe导出，不能制造连接边。

**Exact不是完整路径资格。** 原save2file在任一边双role重构均false时会提前return，但solve随后仍`addSolutionPath(...false...)`并返回EXACT；必须保留该原行为和所有失败prefix，不偷偷使其变true。首次source Exact只是`SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT`。

## 阶段 P：另冻整条保存路径的独立外门

只有真实S返回exact及完整原回溯候选后，先由保存记录冻结新路径的完整节点队列和全部边，再运行外门；不预猜路径内容。原start树边为parent→child，goal树导出边为child→parent，加原connectionPoint有向桥；必须核对真实start→goal序列及双树链，不能直接复用单RRT“只有一棵树”的图检查。原回溯每边先role0共branch、失败后清M再role1，要求每条最终边有完整true重构，原false候选全部留存。起终点binary64逐值匹配A01，各边首末与里程点/树/分支身份一致。

拟上限120墙钟/240 CPU、最多2048个唯一原节点，完整队列超过帽则本项不执行、不只验前2048个。复用原独立ABB math/branch和v3 native/aligned collision worker；可沿已合格NR PATH01的persistent worker传输，但必须新版本PCS路径runner并逐项静态审查，不能修改任何冻结NR/PCS runner或execution。每唯一节点2次数学arm FK/J/branch，1个碰撞adapter请求（内部4臂FK/J），至多4096数学arm、2048 collision、8192 adapter内部arm。0新IK/NR/投影/RBS/RNG/solve/VI。

原外门保持：位置maxabs≤1e-5 mm、旋转矩阵maxabs≤1e-5；12角原完整机械界；相应被动解析branch独立身份；所有叶全12维L2严格<.05；每节点aligned原离散碰撞clear，native输出/TCP/查询码同时留存，角色切换点两侧分别检查。只能标离散source-policy起终路径资格，不等于CCD、完整实体杆/省略pair安全、RSS/PCS全局优势或论文FULL。

## 成本参考、冻结依赖与停门

|已完成历史执行|实际wall/CPU秒|用途与限制|
|---|---|---|
|PCS四target BUILD01|94.59233520399721 /130.109068|含未用三搜索器链接，不能直接当新两目标耗时|
|原RRT_PCS单target build|17.12737691100483 /23.727903|两倍34.25475382200966 /47.455806仅线性参照|
|原RRT_PCS E2E01整次|.2776374349996331 /.19540999999999997|solve段.016837364；不是CBi速度预测|
|PCS177节点PATH01|40.94035644100222 /1.1020530000000002|旧逐进程/I/O开销，不是几何计算纯成本|
|NR393节点persistent PATH01|3.7730926529998214 /3.9572699999999985|仅证明传输方式已有实现经验，不跨方法比速度|

上述拟帽合计为**255墙钟/510 CPU**（E60/120+D15/30+L30/60+S30/60+P120/240），不是已消耗，也不是一次自动连跑的授权。E/L等可据实现审查进一步收紧；不能省略门或扩大帽。每阶段运行前独立PRE/源码与输入完整冻结、独立审查、父代理冻结、源码已commit、独占claim和全资产hash；按当时实际全部execution重算R2总3600/7200余额，H及其他并行新成本必须纳账，**不绑定过期25或26 execution快照，不冒称本草案已知当前余额**。阶段P队列和预算须在S保存结果后才能最终冻结。

任何工程/证据错误优先从保存数据恢复，不重跑science；数值/branch/路径/碰撞失败保留全部前缀，不改节点、seed、深度、range或门限。相同机制三次有证据修复未解，进入D079五分类根因审查；OUR-IMPLEMENTATION给可证伪修复与新预算，UNKNOWN保留竞争解释，不直接放弃或归罪论文。新科学设计或正式预算扩张仍按用户规则审查。本文件不启动正式实验、P2或Isaac。
