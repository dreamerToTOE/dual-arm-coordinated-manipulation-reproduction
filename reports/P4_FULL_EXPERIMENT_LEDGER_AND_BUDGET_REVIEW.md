# P4 D079 完整实验执行账本与预算复核

2026-10-14。本文件只做原文、源码与作者已有文件的静态审查。没有执行新的规划、投影、可见性、算法资格或科学case；没有修改新/旧项目工作树。

机器可读文件：`P4_FULL_EXPERIMENT_EXECUTION_LEDGER_D079.json`；Table I单元CSV：`P4_TABLE_I_45CELL_EXECUTION_LEDGER.csv`；作者已有文件基数审查：`P4_AUTHOR_REFERENCE_DATA_CARDINALITY.json`。所有我们实际结果字段为空，executed=0是确切未执行事实，不是科学失败或0成功率。

## 来源更新：六环境资源已经取得，旧缺失判断不延用

以下为author-source候选的固定版本，不等于已经证明它们是最终发表实验的唯一生产版本。源码、原参数、网格、端点与部分作者data都在本地外部资产目录，优先使用作者输入而不是先造同类简化环境。

| 环境 | 作者源与固定SHA | 当前应判的资源状态 |
|---|---|---|
| I | `planar_ckc` e5edcb58e151b78baca43dd4922bfe27a48388cd | 原20R/19单位杆、(7,4)闭合目标、四圆障碍、端点、m测试与原data均找到；不再称原模型缺失。 |
| II/III | `CKCplanning` 909bd72fff778aca8682c96f9eb86ae4eb75557b；`ABB_dualarm_planning` ca095265818cc6b88402c9e6ed47df598dc6d906 | 8分支ABB解析IK、PQP三角网格、三杆/双锥、两套基距/杆长、端点、三planner、投影/可见性/统计代码与原data。 |
| IV | `ckcComau2` 80089340f0f1f6822e5b2821a63c998b6ae0413f | 1800mm杆、6000mm基距、Comau运动学与场景网格、端点、三方法/三planner/data。 |
| V | `ckcComau` **industrialScene** ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca | 箱/吸盘/输送安装网格、非平移抓持变换、异高不对称基座、端点、三方法/三planner/data；默认master初稿不能代替此分支。 |
| VI | `ckcComau3` 25488a86947cd07377cc62c43850df719a70d9ee | 18D端点、三基座、环/两柱、两组抓取变换、active arm对应两passive分支、三planner/data；RSS存在代码移植不完整线索，应做实现资格而不是标模型缺失。 |

详细来源/许可证与逐文件哈希见作者资产审计（摘要SHA `cd9d9c02dc9fe837e6a4420ca70ed561dc49fe89b992741deb362b2ad06e59c3`，manifest SHA `6d5dd1c4c353da51c9f6331afa60f98b01559b72b2b666e4375e003f8ca63cac`）。作者源码和mesh无统一LICENSE；只保留本地来源/获取/哈希，不据此向公开仓库搬入全部文件。

尚未辨识的是：精确依赖版本、最终生产seed、raw文件→最终图表生成链、不同历史配置/步长及某些统计口径。状态应为 **SOURCE-CANDIDATE / LINEAGE-UNKNOWN**；未经这些复核不能宣称ORIGINAL-EXACT，亦不能提前认定BLOCKED-PAPER-RESOURCE。

## 确定次数、源码次数与未知次数分栏

| 账本ID | 原文要求 | 原论文明确的次数 | 已取得源码/文件的次数 | 执行与独立验收要点 |
|---|---|---|---|---|
| E01 / T04 | p2环境II APC/NR投影效率 | 500000 ambient输入；各方法一次/输入 | `test_apc_kdl.cpp` N500000；公开文件恰500000行 | 同输入两投影，成功/失败都记；关闭限位与碰撞符合原文。失败输出不得计算有效projection distance。当前类default限位=true而test未关闭，必须先辨识版本/做原文条件明确适配。 |
| E02 / T19 | Fig3上图I visibility，PCS m1/2/3/7/20 vsNR，bin .3rad | 未给样本数 | PCS程序N200000 **success target**，NR程序N50000 **success target**；public raw只有112684/57965行 | 计数不是200000/50000总尝试；必须全部failed RBS和被投影拒绝的请求另记，合法pair条件与可见率分母分开；m集合嵌套、不事后选择最有利partition。 |
| E03 / T19 | Fig3下图I，Bi-RRT m1…20时间 | 未给每m repeats/cutoff | 源码PCS1000/m＋NR1000，共21000调用；raw为m1/2各751、其余750，NR1000 | 重复数与最终paper来源链UNKNOWN；不可把source1000或raw750写成paper明确事实。当前mode3不是benchmark mode4；cutoff CLI输入，不给默认1s冒充原论文。 |
| E04 / T20–21 | TableII visibility、Fig4 curve，II，.3rad bin | 50000起终配置/pair量级，单方法/总量需核对原记录 | 当前ABB代码PCS100k、NR200k、RSS100k，来源env也不同；raw108435/444392/77488行 | 保留Fig4caption I/bodyII冲突；不能混env1/2、不能直接照抄各异sampler后声称统一pair分布。原文对齐与公共输入诊断分别预注册。 |
| E05 / T20 | TableII十指标，II/Bi-RRT | 没另报repeats | 与TableI同cell时可复用其500正式调用 | 不应重复花费或冒加样本；RSS/PCS/NR d=.6/1/2.6；完整保存sample attempts、accepted/failed、local耗时次数、树/路径节点与shortcut口径。 |
| E06 / T22 | Fig5投影前后邻点距离绝对变化 | 未给N | 当前两个_d程序100k accepted projections/method | 同一valid neighbor：abs(d_before−d_after)，bin .46rad；原代码APC fullambient/NR chopped且env不同；当前MATLAB部分画after distance，需要分原文定义和作者代码诊断，不能换统计量制造论文曲线。 |
| E07 / T19 | p6平面APC projection约快40倍 | 未给N | 源码APC500k **成功输入target且每输入最多20次retry**，NR500k ambient尝试 | 不把APC最后一次成功cost当总重试cost；分all attempts/accepted/success-only统计，独立验证投影；integer-division偏置需最小oracle。 |
| E08 / T23 | p7去障碍后空间NR优于PCS，VI例外 | 未给N，也未说明是否各planner | 有withObs开关/相关source，最终raw对应待查 | 空间II–VI、原端点/限位/模型不变，仅移除外部障碍；自/互碰与物体碰撞语义仍说明。若拓展全部三planner、RSS或I，标额外诊断。 |
| E09 / T08/T27/T28 | fullPCS vsfixed每划分、复杂障碍/窄通道/多环的机理 | 原文没有该完整fixed消融次数 | 这是用户授权的新增可证伪机制实验 | I20固定划分，II–V各2，VI3active roles（每role两个passive分支）；合法难例先独立见证或UNKNOWN。最终解边partition变化独立于树切换。固定版本只移除换划分，其余配置一致。 |
| E10 /新增T30 | p7 APC/NR流形分布近似相同、覆盖主张 | 无样本数、test、统计量 | 有gen_samples类来源，最终对应尚未辨识 | 六环境；ambient requests与accepted feasible分布分开；预声明joint、branch与objectpose descriptor/检验。有限点覆盖诊断不能证明整个连续流形。 |
| E11 / T24 | γ=.2、各法/planner调优d | 原文没给搜索grid/repeats | source各mode counts不同；cleanCKC三个run都step2.6/1 | 训练profiling seed与正式500分开；不得按正式排名挑参数；作者原文参数、原source历史参数、公共参数公平诊断分三种来源。 |
| E12 / T01/T05/T06/T07/T16/T27 | Eq1–9/Fig1/数学/路径/多环资格 | 不给统一N | 原样fixture与独立oracle需预注册 | 原模型/分支/真实passive秩、负碰撞、边连续、全环约束秩；VI默认NR顺序1–2＋3不同于全18D同时投影，分别记录，不偷换原生算法。 |

50000点对组的精确生成分布、是否每method50000不能只靠正文一句确定；任务规定的50000合法pair目标保留，具体统计单位必须在正式protocol中列出。将同一固定pair bank给各方法会生成150000 local checks，这是一个清楚的公共输入诊断；如与作者sampler分布不同应另列AUTHOR-NATIVE，对应原方法较高/较低可见性不能偷用同义标签。

## Table I正式单元与数值（单位s）

每项500调用，上限1000s；横线为原表显示，不填我们失败值。下面45项完整展开在CSV中。

| 环境 | planner | RSS | PCS | NR |
|---|---|---:|---:|---:|
| II | RRT | 90.86 | .33 | .60 |
| II | Bi-RRT | 7.27 | .22 | .13 |
| II | SBL | 397.29 | .60 | .16 |
| III | RRT | 75.94 | 2.91 | 1.53 |
| III | Bi-RRT | 23.10 | 1.06 | .92 |
| III | SBL | 648.9 | 5.48 | 7.56 |
| IV | RRT | — | 99.24 | 75.88 |
| IV | Bi-RRT | 175.5 | 27.18 | 38.84 |
| IV | SBL | — | 147.95 | 234.82 |
| V | RRT | — | — | — |
| V | Bi-RRT | 330.6 | 3.81 | 11.76 |
| V | SBL | 587.29 | 2.61 | 3.55 |
| VI | RRT | — | — | — |
| VI | Bi-RRT | 537.2 | 3.7 | 36.63 |
| VI | SBL | — | 7.16 | 82.24 |

不能从某dash推出500/500均失败，论文没有提供每cell逐试验分母；我们必须记录每次成功/timeout/错误和删失，不复制该缺口。全部失败仍在500正式分母内；根本未执行的cell没有成功率，不填0/500。

## 定量预算与必须先取得的审批

### 正式TableI规模不缩减

45cell ×500×1000s = **22500调用，22500000s，6250单线程核小时**。单执行槽最坏260.4天；4槽均独立原生单线程最多1562.5小时墙钟，16槽390.6小时（机器是否有这些可隔离CPU与RAM未知，这些是算术，不是可用资源承诺）。此预算不包括source编译、path独立验收、profiling或其他实验族。作者阻塞式无限拒绝sampler可能不响应OMPL solve deadline；若无外层守护，6250h甚至不是严格上界。应在执行器层保存日志并区分OMPL cutoff与外层资源终止，不能混成算法无解。

36有限均值合计3670.82s。若**仅作量级说明**，将500×36均值与9dash各500×1000相加为1759.84核小时；这既不是本机预测，也不是正式预算上界，原表删失/条件均值口径不足，不能据此承诺完成日期。

### 其他族的诚实预算公式

原论文对很多组不报告repeat/cutoff，源码又含accepted-target及无限拒绝。先保留目标与缺口，用资格运行取得真实每投影/采样/RBS的时间与拒绝比例，再冻结总CPU/墙钟/原始请求上限；达到上限而没达到目标时，保留partial/incomplete事实，不改N。

- Fig3 runtime按当前source1000/m对齐方案：`21000*T_I/3600`核小时。`T_I`未给；若提议10s则58.33h，若1000s则5833.33h。两个只是可审预算方案，都不可写成已批准/原文已给。源码raw750与N1000需先追踪，不能偷偷取较小者。
- 500000paired投影：`500000*(t_APC+t_NR)+采样/独立验收`秒；这里t必须来自新资格数据或明确单调用上界，不跨机使用论文旧mean。正式目标还是500000输入，不因预算小改成5000。
- 50000shared合法pairs三方法：`50000*(t_RSS_RBS+t_PCS_RBS+t_NR_RBS)+合法pair生成`秒；额外保留raw request/拒绝计数与失败。作者native不同分布需要另账。
- fixed-partition机制每障碍condition共有I(20+fullPCS+NR+RSS)=23、II–V各5、VI6，共49环境/method单元，全部三planner为147cell；L个冻结condition、N组配对seed、C秒cap给`147*L*N*C/3600`核小时。**例如**L3/N30/C120为441h；这是新增预算示例，不替代原500/1000，不表述已批准。
- 无障碍原主张的NR/PCS在II–VI、全部三planner扩展为30cell；RSS追加15cell。原planner范围/repeats未知，需在新增protocol中明确选项；若reuse同case必须config/source/input/seed完全相同，不能仅按environment标签复用。
- T30采样分布各六环境两个projection：`6*N_distribution*(t_APC+t_NR)+合法性验收`；拒绝数独立。N、descriptor与统计test应冻结，作者未给则标我们预声明，不冒作原次数。
- profiling：逐env/method/planner/candidate×Ntrain×Ctrain单独计，正式seed未使用。不能只为RSS加时、降低成功门限或在主矩阵上试到期望排名。

因此目前只有TableI完整正式上界可定量锁定；把所有未知族合成一个精确总小时数会虚构输入。可以向用户同时提交确定部分和未决预算参数，而不是宣称全部暂不可做。

### 可先执行的低预算资格建议（不计入正式统计）

建议独立登记 **Q01，CPU/墙钟总上限2h**，源码与fixture冻结后执行，不扩正式预算：

1. 只读获取/版本/依赖/构建资格；每构建目标最多10min，保存成功与真实编译错误。不运行作者自带预编译binary代替可追溯build。
2. 每环境固定作者端点和事前定义的解析/有限差分/IK分支/正负碰撞fixture；不存在的精确分支或合法奇异positive不能写单位矩阵占位。源模型/毫米/弧度/末轴chart保留，资格实际残差独立记录。
3. 每可运行RSS奇异mode先100个**raw请求**的预注册生成诊断，全部拒绝原因与实际秩保存；这是资格诊断，不是论文正式规划成功率，不能取得0合法就放弃或无限重复。
4. 最多51个原生planner资格调用：空间45cell各1＋I中PCS/NR×3planner各1，单次30s；最多1530s。I/RSS如独立新增则另3calls/90s，标新增而非Fig3原实验。
5. deterministic RBS正负/跨branch fixture和输出路径稠密重检。源代码不能编译或负例未拒绝时保存failure_id并暂停该链路盲跑，独立部件仍可继续工程资格。

Q01需保证2h是整体上限，不能把每子项上限分别追加造成隐性放大；实际达到2h时保存完成/未完成清单，向用户报告新增修复/预算。Q01只有qualification status，不给论文性能结论；成功的单次资格不能计入TableI的500或P4 FULL。

## 子义务再检查：容易漏项的位置

29项＋新增T30外，建议在稳定ID下细化以下条目，不删除原行：

- **T06-Eq7-8**：独立均匀branch枚举检查conditional语义与dependent-pair union；独立/依赖/等测度/碰撞不同分母，VI理论非直接适用。有限oracle不能证明一般所有机构上界。
- **T07-RSS-NN**：p7论证大树使nearest-neighbor检索占时变大。这是解释性原主张，原文无独立NN曲线；主run记录NN调用/耗时/树size，检验该解释或标PAPER-CLAIM-NOT-DIRECTLY-TESTED，不能只解释singularity request rate。
- **T19-PROJECTION40X**：平面约40倍投影成本是独立数据要求，不由runtime-m曲线自动推得；保存retry总成本和一次投影成本，不用最后成功调用掩盖前面失败。
- **T20-NUMERATORS**：十TableII字段分别定义；成功均值与全体删失成本分列；shortcut前/后path节点、added tree nodes/retained tree nodes、accepted sample/raw request不得混用。
- **T24-GAMMA/STEP**：RSS .2来自profiling，但论文search grid/seed缺；保留source grid与原最佳值差异。TableII d优先论文，不以clean run全部2.6/1冒充已复现参数。
- **T25-FINAL-DATA-LINEAGE**：public source/raw与final图不一致不是仅记录repoSHA就已FULL；尤其Fig3 m9/10/11 plotting手工缩放、可见性首点人工100以及source与raw counts差异。新曲线仅读未经美化的新raw，作者公开raw和原刊图分开显示，未证明原因不归咎论文方法。
- **T26-PATHQUALITY**：原仅以path nodes作平滑代理。新增曲率/totalvariation等为PROPOSED，不能硬套原结果；离散RBS不提供连续碰撞证明，单步边界和稠密重检明确。
- **T27-VI-NR**：作者默认顺序NR先1–2再3，tree求解器未进入默认build；忠实native与全18D多约束NR诊断不能混称同一实现。全链Jac数学资格仍必须完成，以独立closure和秩检查监督顺序返回值。
- **T28-CLAIMLEVEL**：论文总结PCS障碍有利并不是每TableI cell胜NR；smart-biased RSS“unlikely match”是推测，力/控制/抓取statics/manipulability是future work。列PAPER-CLAIM-NOT-DIRECTLY-TESTED/PROPOSED，不擅自增加全新改进算法去替代原三法。

结论：可继续原作者平台的工程/数学资格；原模型缺失不再是当前解释。正式完整矩阵预算与抽样/版本链需审查，不能运行后改分母、改成功阈值、缩500或抹掉失败。当前本agent未做任何新科学运行。


## 2026-10-15 恢复后实际账目快照（替代上文未运行预测状态，不改历史）

|run|wall s|CPU s|
|---|---:|---:|
|20261015_R2_COLLISION_CONTROLS01|0.021082576000|0.022198000|
|20261015_R2_ENDPOINT_COLLISION_REPLAY01|1.321430518001|1.324637000|
|20261015_R2_ENDPOINT_RECONSTRUCTED01|7.450141228001|6.025647000|
|20261015_R2_IV_NR_LOCAL01|2.651571520000|0.882651000|
|20261015_R2_PLANAR01|0.111326417000|0.112283000|
|20261015_R2_RSS_CONSTRUCTION01|1.502717416000|1.015161000|
|20261015_R2_SPATIAL01|14.723153130000|9.465682000|
|20261015_R2_VI_RSS_BRIDGE01|7.987086492001|6.310368000|
|20261015_R2_VI_RSS_RECONSTRUCTED01|45.133593772000|5.641175000|

9run自身字段合计wall80.9021030690028s/CPU30.799802s；R2原3600/7200帽，余3519.097896931/7169.200198s。不得再次相加execution内cumulative字段。工程v2 compile合计wall7.612339770s（旧manifest无CPU字段，不能补0作测量）；controls准备wall1.053867114/CPU.863996；v3全build wall3.419461395/CPU3.420515，均另账。

B Q1+Q2共904/960构造，wall53.12068026400084/180s、CPU11.951543/360s，余56/126.879319736/348.048457。原claim与Q2续claim保留，不可换run名重开。A累计wall8.771571746/CPU7.350284，IV local单独2.651571520/.882651。尚无正式规划，22500完整义务和其他原实验分母不缩；正式成本需全部相关资格后pilot实测，不将组件时长当planner耗时。新fixed-center数学诊断若执行，另run记录并从B/R2 wallCPU扣除，不能沿用本快照余额当最新值。
