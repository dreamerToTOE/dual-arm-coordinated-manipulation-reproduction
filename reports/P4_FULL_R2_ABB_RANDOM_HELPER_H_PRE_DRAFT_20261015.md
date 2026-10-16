# R2 ABB 三参随机helper H：双目标真实接口资格 PRE草案

日期2026-10-15。状态 **DRAFT / UNBUILT / UNEXECUTED / UNQUALIFIED**。本文件、新builder、driver、观测头与字节变换器均只准备可审查源码；尚未编译、建立stage/claim/实验目录，未调用RNG、FK/J、IK、NR/SVD、碰撞或planner。工程与science必须分别经root冻结和独立审查后才能运行；本PRE自身不授权执行。

这份方案采用root最新的局部资格精简：**仅已合格的R2数值基底、2个控制流目标、runtime plain/trace、16请求×2控制流×2mode=64次helper**。旧`P4_FULL_R2_ABB_PCS_SOURCE_CORRECTIONS_PRE_DRAFT_20261015.md`及旧4target/native128配置原样保留为历史，不执行其已被替代的H范围。原生数值helper真实接口仍未验证；旧原生IK失格证据不改、不重复运行。

原RRT_PCS已有II seed7、177/177源策略离散路径资格；H三参helper不在RRT/CBiRRT/SBL的真实grow路径中，不是其规划资格前置。本轮不把helper更正当作规划能力提升。D的CBiRRT真实activeDistance修复仍为随后独立因子；H代码不链接planner，不产生D组合目标。

## 固定来源与唯一控制流差异

只读基底`/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1/geometry_consistent_plain`；作者提交`909bd72fff778aca8682c96f9eb86ae4eb75557b`。builder复用已审查的RRT builder纯stdlib资产读取器，验证旧build manifest、源/头、mesh、原binary、PQP库、OMPL库及旧claim链；另外绑定`g++11`实际文件和libstdc++11的`bits/stl_algo.h`。不导入旧ABB PCS builder，因为该模块会导入模型/科学执行代码。

两个新外部目标为`abb_random_helper_h_v1/source_control`及`success_break`。二者都继承既有R2数学pi修复；第一个保留原控制流，第二个仅在原identify失败continue之后加一条`break;`。原SVC SHA256 `7b6013282f698e47d1f55c2ed31cf0edf52ca6ccf369035016a18e38e42a527f`；只补break、尚未观测包装的SHA256 `c8e302ccbe786590d62e9f2d803e3ee058fc115d2059d8f5cbb97e4aba6d34cb`。不改原0..7向量、shuffle、calc_specific、IK、identify、原角界、源碰撞契约或原正常返回规则。

`abb_pcs_source_corrections_draft.py`保留原单因子补丁及反向整文件字节证明。新增`abb_helper_instrumentation_draft.py`对完整原函数体加进入/返回lambda包装；helper内额外只记录原shuffle之后的8支顺序、每支进入时q、原identify返回后的候选q及身份。逆序移除全部观测时，整个3文件source map必须逐字节回到补丁前/后的对应基底。读取和写入用bytes，原APC CRLF函数体保留。source_control逆转后等于原R2字节；success_break逆转后等于独立H补丁字节；不得把观测后的哈希与无观测原哈希混用。

`abb_helper_observation_draft.hpp`无内部调用帽、无额外RNG或模型调用。它记录helper、calc_R1/R2、原native FK/IK、identify、source_limits与collision函数的进入/完成，并将事件立即flush到stderr，保留未返回调用的最后可见prefix。最终原FK/IK内部未观测细节仍为UNOBSERVED，不能从算法上界反推实际计数。观测可能增加I/O/分配成本，不作论文效率比较。

## 真实接口、随机数与64固定请求

driver严格调用原`checker->IKproject(q1,q2,active_chain)`三参overload；不调用四参fixed helper、不复制helper循环、不在driver闭链或重挑分支。II/III分别采用原env1/2构造器；每个进程启动时读mesh属于资源加载，不是collision查询。`initiate_log_parameters`只初始化原计数。每个request从保存的完整12角开始，helper返回后只保存原bool及完整q，无任何FK/IK/limits/collision查询。

4个旧A01中心为II/III起终点的`selected_q_rad`；每中心active0/1、seed7/17，共16 context。所有原角和端点来源hash冻结。每个相同context在2控制流×2mode中运行各一次，共64。source_control/trace和break/trace使用同一个driver/观测代码；plain/trace由同binary运行时flag切换，不重复编译两个mode。每次真实helper前执行一次原`std::srand(seed)`，原`std::random_shuffle`自行消费随机数；观测只读取原shuffle结果，不预生成permutation、不额外调用rand。

绑定libstdc++11的8元素实现有7次rand的结构预测，64helper为448draw；**这不是实际rand开始/完成计数**。driver明确输出`UNOBSERVED_SOURCE_STDLIB_NOT_INFERRED`，实际srand完成、shuffle完成和helper dispatch/return分别记录。未返回请求保留输入、日志与未执行context，不能换seed或重放。

## 接口与独立终态门

各控制流内部plain/trace的非观测输出应逐值精确相等。相同context两个trace在首次双身份成功之前的shuffle顺序、每支尝试、源候选、原identify结果必须精确同prefix；break必须恰在首次双身份通过后停止。source_control任何正常完成始终false，仍保留其最终变更q。若没有双身份通过，两控制流应false且最终q相同；有成功时原控制流继续执行，不能要求两个最终q普遍相等。active关节原输入应逐值不变。

保留8支各次中间候选，**不**为未独立检查的所有中间点批量授予物理资格。单独冻结的root runner须对全部64最终q（包括原false留下的q）检查：数学链闭合最大位置误差≤1e-5mm、旋转矩阵最大误差≤1e-5、12角原完整机械界、独立几何branch identity，以及v3 aligned原策略离散碰撞。独立branch identity采用已有角度几何判别，零符号相对门64×binary64 epsilon；不调用额外解析IK。source identify标签与独立几何标签分别记录；最终q若没有对应source identify观测必须显式NOT_OBSERVED，不能补调用或猜标签。

原helper本来没有collision查询；候选保持该函数契约。source bool、数值闭链/限位、branch身份、aligned collision资格分列。source true不等于物理通过；正常碰撞/限位拒绝保留，不要求64/64都碰撞free，也不能用换分支/换seed达成全过。若更正helper返回true却违反独立闭链/active/branch正确性，立即soundness STOP并保留prefix，不以放宽门补救。独立碰撞仅源策略离散门，不是完整几何/CCD。

静态最坏64 helper：直接analytic IK≤512、identify analytic IK≤8192、合计≤8704，源armFK≤1536。外门64终态数学armFK/J≤128、独立几何branch判别≤128、collision adapter≤64；每次adapter保留native/aligned两worker，故真实native worker query≤128，adapter内部armFK/J≤256。此前“64collision worker”措辞指64个外门adapter，不能冒充只有64个底层worker query；本处澄清，不扩64终态队列或预算。这些均为结构预算上界，**不是实际started/completed**；source_limits等调用从trace实测，不由理论推算。

新增`scripts/qualify_p4_full_r2_abb_random_helper_h_draft.py`已静态编写，尚未独立复核/冻结/执行。顶层仅stdlib及纯保存源builder；describe/validate不导入模型、不启动进程。实际execute必须要求两个成功build的完整source/protocol/claim/engineering-execution链、当前所有资产hash、提交blob与clean检查、fresh claim/output及root与独立review布尔门。

runner首先按固定顺序完成64 helper，在8个factor/mode/environment持久进程中逐请求保留输入、原stdout/stderr完整字节、单条原响应BIN/JSON及trace；每请求仍独立srand同seed。随后对32 plain/trace配对做含signed-zero的binary64精确对照，对16 context做原控制流/首次双身份成功break的完整源event prefix对照。最后对全部64原false/true的最终q做独立终态门；原32 false不筛掉、不换候选，未观测source label不补调用。物理闭链/限位/碰撞与source branch关系分别计数；`final_candidate_all_gates_qualified`还需已观测direct/dual标签与独立几何分支相符，`source_success_fully_qualified`再需source bool true。接口控制流PASS不要求所有候选碰撞free，也不冒充原source全部返回true。

每20ms外部timer检查wall和self+已reap子进程+所有live descendants CPU，初始setup成本计入；source body内部没有guard。64helper、64metric、128数学armFK/J、128独立branch、64adapter、128真实worker query及256adapter FK/J都有进入/完成计数与帽；原始worker返回在adapter追加元数据之前独立保存。清理会kill/reap尚存transport及collision worker，保留原stderr未完成trace、当前partial、完整未完成helper与终态UNKNOWN尾部。清理/证据保存成本纳最终实账，超帽或hash/日志/cleanup错误一律取消PASS。无retry/reset/resume，无尾部截断成功。工程prior/现有draft配置在NR interface/local结束前不刷新；之后必须从此runner重新生成science协议，不能执行旧builder生成的无runner草稿。

transport回收后两路pipe须读取至EOF；原完成响应的完整trace按每session固定调度顺序拼接，与实际stderr逐事件、含signed-zero的binary64精确绑定。未排尽pipe、不可解析trace尾部、额外stdout尾部或raw/response事件不一致均取消完整资格PASS。中断调用允许保存比已完成响应更长的raw前缀，但该部分保持UNKNOWN，不能作为完整响应或通过记录。

## 有界工程与后续science预算草案

工程只编译2个目标，合计60wall/120CPU，每目标45wall/90CPU；每个execution own-cost只记一次入R2总帽3600wall/7200CPU。外部watchdog同时检查单目标与总帽，编译失败、超帽或中断保留源码、日志、claim、stage和前缀，禁止自动重试/清空/复用原claim。工程不执行任何binary查询。仅链接原APC/SVC/collision三CPP，不能用未调用三planner重复链接来消费预算。

最终旧资产重哈希的收尾成本计入工程实账；收尾达到合计时间帽时保留已经链接的binary与全部日志，并将原本成功的状态改记`STOP_FINAL_BUDGET_EXCEEDED`，不得据此启动科学资格或重编。若已有更早失败，保留其原状态与根因并附最终预算越界记录。

预算参考旧单RRT target17.12737691100483wall/23.727903CPU，两倍34.25475382200966/47.455806；这是历史不同target的线性参照，**不是新H编译成本**。未进行新编译测速。science拟60wall/120CPU，含64真实helper及64独立终态数学/branch/碰撞；旧48点collision replay13.069952120997186wall/12.882596999999999CPU的线性64参照17.42660282799625/17.176796，只是参照，helper搜索/trace/进程开销未知。工程成功后先读新实际账，再冻结science完整runner和参数；超帽不能自动扩大。

运行前必须重读全部`20261015_R2_*/execution.json`并冻结哈希、当前own-cost总额和余额。不要复制PRE里的历史余额。V6仅是已交付历史快照；root当前独立NR工程/local若新增执行，应自动进入新protocol的prior ledger，任何旧prior失配都拒绝启动。

## 完整义务和交付边界

所有211原论文义务、原统计分母、Fig3–5/TableI–II、500000投影/50000点对、全部三方法三搜索器、被动链数量/局部可见性/复杂障碍/窄通道/固定链消融继续保留。正式TableI仍0/22500；H是局部导出接口资格，不是正式planner trial。VI974/974、构造余额0，本方案没有VI构造。原源码、旧失败、所有R0/R1/R2结果和原RRT路径保留。P4完整后中文Word/PDF、双FR3方法适用分析及最终全范围对照表给用户审查仍是交付义务；不进入P2、不提前开展Isaac。
