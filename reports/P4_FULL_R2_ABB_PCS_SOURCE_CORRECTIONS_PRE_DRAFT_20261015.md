# R2 ABB PCS公开源码：两个独立最小修复候选 PRE草案

日期：2026-10-15。状态：**SAVED_SOURCE_AND_ARRAY_REVIEW / PRE_DRAFT / UNBUILT / UNEXECUTED / UNQUALIFIED**。只读旧源码/manifest、A01保存角和历史成本，新增项目自有补丁函数、候选哈希说明和纯数组反例；0 FK/J、0 IK、0 NR/SVD、0碰撞、0 RNG、0 solver、0编译，未创建新stage、claim或实验目录。不改已冻结NR、旧plain/trace、旧工程build、已合格原RRT路径或任何失败日志。

完整211义务保留。原RRT_PCS已有II seed7的177/177合格源策略离散起终路径，报告仍为重建端点/R2数值/原RRT算法/观测I/O，不是正式Table I或完整几何/CCD。下列随机三参helper不在RRT_PCS、CBiRRT_PCS、SBL_PCS真实grow路径中，**不是这三种planner有限资格的前置**。本草案响应导出接口的真实缺陷；不能用其未修复否认已取得的原RRT路径，也不能把helper修复冒充规划器能力提升。

## 独立候选与来源保全

`baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py` 只提供纯内存 `candidate_bytes(original,factor)`，返回新字节和SHA manifest，不写stage、不编译、不执行。每个因子只准匹配一个函数/一个锚点，反向替换必须整文件逐字节还原。`configs/p4_full/r2_abb_pcs_source_corrections_v1.draft.json` 绑定原native/R2两份plain源码、原build manifest与4个A01端点，保存两因子各自的预测修复SHA；没有combined选项。

原SVC、CBiRRT两个文件在author_native与geometry_consistent stage中分别字节相同；两数值版本的区别位于原APC与既有R2数值修复。后续复制两个基底时仍须绑定整套源/头/库/mesh/binary与commit，不能仅以这两个文件相同就混淆数值版本。原失败源码、LOCAL01全部原失败、原原生IK物理失格、旧source Exact/独立path PASS原记录不改。

## 因子H：三参随机分支IKproject只补成功break

原 `StateValidityChecker::IKproject(State &q1,State &q2,int active_chain)` 用原0..7向量及 `std::random_shuffle`，逐分支执行calc_specific与原双身份identify检查；所有迭代分支只有continue或落到循环尾，**没有break/return true**。只要正常走到函数末，for的i必为8，故返回false。此静态控制流证明不需要新IK/随机采样；异常/中断没有正常返回，另记UNKNOWN。原helper可能在返回false时已改写被动关节，旧输出必须保留。

候选 `HELPER_FIRST_IDENTIFIED_SUCCESS_BREAK` 仅在原“任一identify label为−1就continue”语句之后插入一个 `break;`，使首次双身份通过时退出原loop，继续使用原i==8失败/否则true返回。保留原shuffle调用/初始顺序/随机数实现，原calc_specific、identify、角限位/IK规则、失败候选及原False变更行为，**不**夹带碰撞门、重新挑分支、周期lift或改采样概率。该helper本体原来没有collision查询；候选也不增加。source true不等于闭链/限位/碰撞合格，独立物理与v3 aligned原策略离散门分列。

两边原源码SHA `7b6013282f698e47d1f55c2ed31cf0edf52ca6ccf369035016a18e38e42a527f`；仅加break的预测SHA `c8e302ccbe786590d62e9f2d803e3ee058fc115d2059d8f5cbb97e4aba6d34cb`。此为内存字节运算的候选，尚无该源码的构建或资格结果。

未来H固定资格草案：4个A01中心（II/III各起终）×2角色×seed7/17=16请求；原数值/R2数值×原控制流/break候选×plain/trace=128顶层helper。每个匹配请求进入前调用原srand同一seed，source原shuffle完成后只观测8支顺序；不预生成/替换permutation，不调用额外rand。绑定libstdc++11的现有实现有7次rand调用/8元素shuffle，这是结构上界预测896draw，不是已观测次数。

必须保存每次分支进入、calc_specific返回及候选q、identify输入/返回、最终bool/完整q和观测prefix。原/break在首次双身份成功之前的branch序列、数值候选和身份应逐值一致；break候选必须恰在该首次成功停止；若均无成功，两版必须保留false及同最终q。不能要求两版本最终q普遍相等，因为原版还会继续搜索/覆盖后续被动候选。plain/trace在各自同variant同seed的完整输出应一致，观测不消耗额外随机数/模型调用。

每个最终返回候选（含原false留下的q）独立检查原1e-5mm/1e-5旋转矩阵闭链、12角原界、原identify及几何branch身份、v3 aligned原离散碰撞。原生数值闭合失败仍是原生数值失败；break可修复控制流而未修复原数值，不得混报。合法碰撞拒绝不靠换seed/分支制造128/128。原8支每个中间候选完整保留，但本最小资格不会把未独立复核的中间候选批量标PASS。

H顶层128调用的静态最坏：直接analytic尝试≤1024；每个成功候选的identify最多双臂各8支，≤16384额外analytic尝试，总≤17408；源active FK每direct一次+每identify双臂，≤3072次。外部128最终q复核≤256数学armFK、128 collision worker、≤512 adapter内部armFK/J。以上**全为预算结构上界/预测，不是实际started/completed**；原body正常最多8loop，不以内部guard改写原返回。外部watchdog控制总预算，实际计数只从相应source事件和完成响应读，未返回内部工作标UNOBSERVED。

H拟工程4目标（两数值×两控制流，plain/trace用runtime观测flag），每目标45wall/90CPU、合计120wall/180CPU；只链接helper所需APC/SVC/collision，不为未调用planner重复链接三搜索器。历史geometry plain/原生plain的三搜索器target为21.934770444000605/23.702375222001137wall和30.527862/31.334107CPU；新单RRT target为17.12737691100483wall/23.727903CPU。按后者线性4倍是68.50950764401932/94.911612，仅作预算参照，**不是新helper target实测成本或保证**。合计120/180和单目标45/90均需另行冻结；超帽保存失败，不自动再编译。

H拟science90wall/180CPU一次128调用+全部输出外门。历史48个保存候选collision replay为13.069952120997186wall/12.882596999999999CPU，线性128约34.85/34.35s；新helper分支工作/观测/进程开销未知，90/180是有界小资格帽，不是正式规划成本。不能借预算上界宣称随机流形覆盖或改动原文统计分母。

## 因子D：CBiRRT activeDistance角色1只改首个写入目标

原role0正确把a/b的arm1分别写qa/qb。原role1先 `retrieveStateVector(a->state,qa_dummy,qb)`，再从b把arm2写入同一qb；`State qa(6)` 仍是vector<double>值初始化的六个零，最终返回 `sqrt(sum((0−b.arm2_i)^2))`，与a无关。该函数真实被CBiRRT grow调用，影响d与reach/interpolate控制；具体运行/成功率影响尚未实测，不能与未达helper归为同一个机制。

候选 `CBIRRT_ROLE1_FIRST_STATE_DESTINATION` 仅把role1首次retrieve的第三实参 `qb` 改为 `qa`。第二次retrieve、两dummy、角色随机选择、原6维欧氏sum/pow/sqrt、Range、插值、IK、RBS、碰撞和其余planner都不改。原文件SHA `60f6a483c533f61749bc7e741acc72bfc8cc2e137d719b25392e73831e458d93`，单token修复预测SHA `5b87ed08d674251594efc899ad922398f9c29a0a42f74494cafa7fa2424ae5c2`。不与H补丁同stage；本阶段没有修复或重跑CBiRRT。

纯保存角反例JSON：`reports/P4_FULL_R2_ABB_CBIRRT_ACTIVEDISTANCE_SAVED_COUNTEREXAMPLE_20261015.json`。对同一A01构型a=a、role1，原源码公式推得：

| 保存构型 | 原role1公式d(a,a) rad | 修复公式d(a,a) |
|---|---:|---:|
| II起点 | 3.239119425422773 | 0 |
| II终点 | 4.128865608898457 | 0 |
| III起点 | 1.665155567082146 | 0 |
| III终点 | 2.4702822659418953 | 0 |

这里是**保存数组+源码语义的算术反例，不是执行原C++函数所得**。相同环境start/goal的两个顺序方向也保存，原role1结果因b的norm不同而不对称。两环境各2×2点对×2角色共16数组case，无跨环境伪物理点对，无新FK/IK。它独立反驳该公开函数作为角色距离的实现正确性，不能外推为原论文PCS理论错误。

未来D最小原接口资格草案：一个数值基底即可（distance没有FK/IK且两基底该源码相同），source control/fixed两个fresh stage/binary、runtime plain/trace，固定16case共64次真实activeDistance调用。只通过项目自有derived probe暴露受保护Motion/activeDistance，OMPL state中写入原保存12角，调用原函数；不调用solve/grow、无RNG、无FK/IK/NR/碰撞。role0两source版本输出完全相同；fixed两role均与原6维L2 reference abs≤1e-12，一致点对返回严格0，交换对称；原role1反例独立保留。完整request/return/args/计数与源hash保留。候选代码的真实入口尚未构建，不能以本纯数组反例充当原接口已PASS。

D工程拟两个目标各45wall/90CPU、合60wall/120CPU；按旧单RRT target线性2倍34.25475382200966wall/47.455806CPU，仅为参照，实际driver/CBiRRT链接开销待测。D science15wall/30CPU、64顶层distance；原相应模型调用数必须实测为0，构造期mesh读取与静态资源加载单列，不误写为collision查询。D通过后CBiRRT完整solve和完整路径资格必须另冻预算，不能自动由64distance函数测试升级。

## 冻结、账本与范围

本草案所有预算**未授权/未冻结/未消耗**；不能用本文件直接运行。未来每因子需完整builder、source观测driver和外门runner、独立审查、root冻结、固定claim/新stage/source commit/全资产和原输入hash，工程成功后再冻science；每个执行own wall/CPU一次纳最新R2总帽。先重读实际全部execution（NR工程/资格仍由root推进），不能复用任何报告里的过期余额；VI B974/974、余0，不追加候选。

原生、既有R2数值、source控制流候选、原论文方法四层报告。三次同机制有证据修复仍未解决即进入D079根因审查，保留失败/输入/前缀，不盲重试、换分布/缩统计或放宽门。Table I正式仍0/22500，Fig3–5/TableII、500000投影、50000点对、三规划器、被动链数/局部可见性/复杂障碍/窄通道/固定链消融等全部原义务不变。P4中文Word/PDF、双FR3适用分析与最终全范围对照表用户审查义务保留，不开展P2/Isaac。
