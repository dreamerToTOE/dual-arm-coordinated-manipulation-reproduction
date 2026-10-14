# P4 D079 原文逐页复核（只读审查草稿）

2026-10-14。本审查未修改任何旧P4/P2文件，未运行规划器、投影实验或科学case。
全文提取和逐页渲染仅存于私有阅读目录，不应提交全文或原PDF。

## 来源身份与阅读范围

- 作者稿：*Motion Planning of Fully-actuated Closed Kinematic Chains with Revolute Joints: A Comparative Analysis*，Avishai Sintov、Andy Borum、Timothy Bretl，8页，页眉为PREPRINT VERSION / ACCEPTED JUNE, 2018；PDF元数据2018-07-06。
- 私有输入SHA256：`193710e5a9d4284cf62b30ff189a1df038a9d5c5ce3f1545525dc2f78bea08c6`。实际文件位于用户已有私人论文目录。DOI `10.1109/LRA.2018.2846806`；正式期刊页2886–2893与当前作者稿页1–8不同。
- 已读全部8页文字、式1–9、Fig.1–5、Table I–II及全部参考文献；Fig.1–5、两表和数学概率式另外逐页渲染复核。原稿无编号算法伪代码，无独立附录，不据此断言外部补充材料不存在。
- [作者稿](https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf)、[作者代码固定版](https://github.com/avishais/CKCplanning/tree/909bd72fff778aca8682c96f9eb86ae4eb75557b)、[作者出版列表](https://avishaisintov.wordpress.com/publications/)、[期刊记录](https://doi.org/10.1109/LRA.2018.2846806)。2026-10-14网络查询仍可获得作者仓库，出版列表的本论文条目只有online链接；本次有限搜索未找到专属视频/附录入口，不能将其写成确定不存在。
- 本地作者仓库HEAD `909bd72fff778aca8682c96f9eb86ae4eb75557b`，状态干净；未拷贝/编译/修改该仓库。README、makefile、APC/KDL类、PCS/RSS有效性检查、相关run入口和CBiRRT机制用于文字审计。其余planner完整工程审核需独立完成，不把部分阅读声称成全仓库资格通过。
- D079任务固定ref `6276f78ce184d54185f299f0bd9a1a7a3267f73a`，GitHub工具完整读取总规程与29项P4任务书。

## 29项任务与原文直接事实

| ID | 原文定位 | 直接事实、预期现象、必须保留的限制 |
|---|---|---|
| P4-T01 | p2 II-A 式1–2；p3 II-D 式3/Fig1 | 构型闭合C=0、合法集为闭合且碰撞/限位合法；单平面环3约束、单空间环6约束；物体与抓手被当成刚性杆。可见性由具体valid_edge决定，不是纯几何连通性。 |
| P4-T02 | p2 II-B.1 | APC随机active、解析IK闭合passive；passive非冗余、平面3R/空间通常6R且末端充分驱动。必须保持全部可行IK分支与分支身份；作者ABB类NUM_IK_SOLUTIONS=8，不是任意6R最多16全部都适用于ABB。 |
| P4-T03 | p2 II-B.2；p5 III-C；p6 IV-A | NR全部约束Jacobian伪逆更新，残差或迭代上限停止；KDL Newton/SVD；论文提到可选backtracking，并未强制使用。作者GD上限10000，精度1e-5，毫米机构，成功后小角<1e-4置零。 |
| P4-T04 | p2 II-B末段 | 环境Fig2b两空间6R臂、500000随机ambient点、无关节界/无碰撞；APC成功7.92%、NR100%；APC单次耗时快3–6倍且基本不随投影距离变化，NR迭代随距离增长。采样范围、seed及完整数据未在论文给出。 |
| P4-T05 | p3 II-C | RBS：直线中点投影到Co，递归两个子段至分辨率或失败；避免不连续投影。作者RBS_tol=.05rad、最大深度150；RSS有距奇异端点15*tol=.75rad提前结束的额外机制，与普通RBS须分开说明并独立验路径。 |
| P4-T06 | p3 II-D/III-A；p4 III-A/B；p5 式4–9 | Hausdorff测度、等分支测度假设；单链上界1/ξ，多独立链Pm=∏(1−1/ξk)，可见份额≤1−Pm。依赖链是重叠部分有多个IK；平面共有≤2关节时原文断言不会依赖。所有界很松，碰撞/限位可大幅降低。式7条件概率标签另需独立枚举核对，见下文。 |
| P4-T07 | p3–4 III-A/Fig1c | 人工actuator singularity为passive方阵Jac失秩；RSS以概率γ抽人工奇异target，作为IK连通分支桥；完全驱动系统可跨该人工奇异，不需断开刚抓。实际γ=.2经profiling。只有普通随机APC投影不算RSS。 |
| P4-T08 | p4 III-B/Fig1d | 更换passive改变人工奇异集合；两个端点有某partition共同IK分支时用该分支投影插值连边。最终路径实际partition变化与树中使用不同partition分别记录；论文没有提供逐边切换日志或证明每条路径必切换。 |
| P4-T09 | p5–6 IV | 原三个method置于RRT、Bi-RRT、SBL；原C++OMPL/PQP/KDL。共同独立栈用于公平诊断，作者原生栈用于实现核对；不能将某新栈结果伪称作者机器秒数。 |
| P4-T10 | p5 IV；p6 Fig2a/Fig3 | I为20维平面CKC，障碍与每关节±180°界。图示两端姿态，但本论文未给精确杆长、障碍尺寸/端点数字；旧E0/E1只能同类重建。 |
| P4-T11 | p5 IV；p6 Fig2b | II为两台6-DOF ABB IRB-120共抓杆、三杆障碍。作者repo env=1即本论文II，help称envI是代码局部编号，不得错映射为论文平面I。 |
| P4-T12 | p5 IV；p6 Fig2c | III仍双ABB IRB-120，杆穿窄通道（图中双锥形障碍）。作者repo env=2为论文III。精确几何优先作者mesh与transform。 |
| P4-T13 | p5 IV；p6 Fig2d | IV为双6-DOF Comau nj-16，共抓杆穿多个障碍。论文没有明确NJ16具体臂长variant、DH/URDF/抓持变换；公开ABB代码不能声称覆盖Comau。 |
| P4-T14 | p5 IV；p6 Fig2e | V为双Comau nj-16，吸盘抓箱由输送带到安装位置；假设吸盘/物体刚接，无力、柔性、泄漏、抓取控制实验。不得加入FR3条件后称原环境。 |
| P4-T15 | p5 IV；p6 Fig2f；p7 IV-B | VI三Comau共同抓环、两杆障碍、多环；每个active arm对应两个passive arms。一般建模18关节/两组6约束，但这是由机构推导的账本数字，论文没逐项报告Jac秩；需实测独立约束秩。 |
| P4-T16 | p5 IV | 全六环境作者声明起终点间需要跨奇异构型；不能仅检查端点闭合或跑一条成功路径。应记录针对所选passive的起终branch、实际人工奇异/变划分见证，区分全链真实奇异。 |
| P4-T17 | p5 IV；p6 TableI | RRT、Bi-RRT、SBL；投影Bi-RRT相当CBi-RRT。SBL含lazy collision checking，不能以普通双树替代。作者仓库还有PRM/RLX，但不是论文规定三主method/三planner对照。 |
| P4-T18 | p6 IV-A/TableI | II–VI，5×3planner×3method，每cell500试验，上限1000s；横线表示1000s内找不到解。未完整给失败样本比例、删失均值定义、seed和confidence interval；均值解释必须注明该缺口。 |
| P4-T19 | p6 Fig3 | I的local connection率按全关节欧氏距离，bin .3rad，m=1,2,3,7,20及NR；下图Bi-RRT平均规划时对m=1…20，NR水平参考。作者描述平面APC投影约比NR快40倍；不要只做5个m的时间点冒充完整下图。 |
| P4-T20 | p7 TableII | II/Bi-RRT的10指标：Pv、调优距离、样本数、失败比例、sampling占时、平均local cost、local checks/sec、local占时、tree节点、path节点。每字段需核对代码统计口径，尤其检查调用/接受样本/shortcut前后。 |
| P4-T21 | p6 IV-B；p7 Fig4/TableII | 正文说II，在Co抽50000起终pair并检查local connection；Fig4正文亦II，但caption写I。bin .3rad。应登记冲突，不能私改caption或者混I、II日志；采样点生成分布及失败重试口径未公开。 |
| P4-T22 | p7 IV-B；p8 Fig5 | II投影随机邻点前后与同一valid neighbor的构型距离绝对变化，APC/NR平均对原距离，bin .46rad；NR较保距。必须两种投影使用相同邻点定义，不能把到manifold的投影位移替代该量。 |
| P4-T23 | p7 IV-B | 原文明示去除障碍后，全部空间环境除VI外NR优于PCS；复杂IV–VI使NR可见性优势降低、昂贵小步投影增加。无障碍对照是真正待复现实验，不能因未画单独图而删行。 |
| P4-T24 | p5–6 IV-A；p7 TableII | γ=.2；最大扩展距离d按各method/planner分别profile最小runtime；TableII II/Bi-RRT RSS/PCS/NR d=.6/1/2.6。统一参数诊断必须另列，不能改变原调优结果含义。 |
| P4-T25 | p5 IV；p6 IV-A | Intel i7-6700HQ、Ubuntu、8GB；C++ OMPL、PQP，NR OROCOS KDL/SVD；具体版本未给。所有硬件/编译器/依赖/许可证差异留账，不跨机声称相同秒数或复现原比值。 |
| P4-T26 | p7 IV-B/TableII | NR可见性高、步较大、path节点少；这是平滑度的代理，不是论文实测曲率。碰撞几何连续性/分辨率和path质量要独立验证；新增total variation/曲率指标标PROPOSED。 |
| P4-T27 | p4–5 III-B；p7–8 IV-B | 额外空间passive可能无闭式IK或冗余；II–IV含杆及其两侧相邻关节的passive有无限解。PCS/RSS原文声称仅ear-decomposable结构可实现；VI两passive同时共享branch要求，III-B单环概率分析“不完全适用”。 |
| P4-T28 | p8 V；p7分析；TableI | 总结PCS在clutter中有利、NR更易推广；TableI并非PCS每cell绝对快于NR（如II/BiRRT .22 vs .13）。客观检验条件性效应，不能强行证明PCS普遍支配。力、grasp statics、control、manipulability仅future work，不应冒充本论文已完成控制。 |
| P4-T29 | 用户任务，非原论文实测 | FR3 Benchmark A/B接口、前提和风险属于PROPOSED；须等实际原算法研究后详细分析，明确7R冗余、刚接 vs 吸盘接触、A闭链/B单臂等差异；不启动Isaac/ROS。 |

## 必须追加、不能被29行吞掉的义务

**P4-T30 原文投影后采样分布/覆盖主张**：p7 IV-B，作者称在全部环境APC与NR在流形上分布几乎相同，并随样本增多覆盖整个流形。无原统计量、样本数、test、error bar或raw data。必须单独登记为原文经验主张，合法输入下记录投影后构型/branch/物体pose的分布差异及覆盖诊断；不把ambient均匀采样当成manifold均匀，也不能凭有限统计证明整个连续流形完全覆盖。数据缺口明确保存。

29行不应删除。建议细化T06（式4、5、6、7、8、9，各适用条件）、T19（visibility五m；time全20m；40倍投影）、T20（10指标）、T27（ear decomposition/冗余非可实现/VI共分支）与T28（无障碍排序、复杂环境机制、软件泛化）为稳定子ID。以上是细化，不重算科研成功率。

## 原文概率式7–8的待验证语义

p4的elbow–wrist–elbow例：每passive ξ=8，共同wrist消去4分支。p5式7给p̃=(1−1/8)/(8−4)=7/32，文字称在首passive分支不同条件下另passive可见的条件概率，并说较小；7/32却大于1/8。

在一个独立均匀分支枚举模型中，共同wrist2分支，两侧elbow各4分支，共32tuple；给定参考tuple，A相同4个、B相同4个、同时相同1个，故两链union visibility为7/32，而P(Bsame|Anotsame)=3/28。这说明该例式7值与pair union visibility一致，条件概率文字标签待澄清。此处是独立数学核对建议，未运行oracle、未与作者更广义几何分布比较，不判定原方法错误，也不作为擅自改PCS公式的理由。

## 原作者实现的资格线索（尚未通过实验）

1. `apc_class.h:2,11`明确双ABB/8IK；run为12维。代码env1/2分别映射论文II/III；无证据把ABB模型认作所有六环境。
2. `run/plan_PCS.cpp:96–111`第6轴±π并注释厂家应±6.98但现IK不支持。`apc_class.cpp:19–25`厂家轴6±400°。厂家限位文字/代码采样界/解析IK输出范围须分别留账。
3. `StateValidityCheckerPCS.cpp:218,252`与RSS `:216,245`采样拒绝条件为withObs AND collision AND NOT limits，而不是独立碰撞/限位拒绝。直接运行上游sample_q不能当合法性oracle；应保留上游版本并独立检查，不把源代码问题直接升级为论文结论错误。
4. `StateValidityCheckerRSS.cpp:255–305`奇异三模式先q2固定q3=−π/2和/或q5=0，再IK q1、branch识别、碰撞拒绝；do-while无限拒绝采样。`CBiRRT_RSS.cpp:351–356`γ=.2。真实秩、闭合、限位、碰撞和分支阈值应拆开诊断。
5. `StateValidityCheckerRSS.cpp:486`距奇异目标<15*.05就返回true，最后区间尚需独立稠密路径检查。`identify_state_ik`匹配容差.1rad；是否导致误识别须诊断，不能预断言。
6. `kdl_class.cpp:94`NR10000/1e-5；`:111`成功后1e-4小角置零；`GD`毫米参数且角归一化。不擅自将这些改成新数值精度再称作者精确条件。
7. 顶层未见统一LICENSE；部分OMPL-derived planner/run有BSD头，APC和mesh无统一授权。代码可本地只读运行核对，公开提交应保持来源/patch/external-fetch清单，避免未取得明确许可证的全文源码/mesh搬入新仓库。

## 原数据、规模和关键不可辨识项

- TableI正式22500调用；每次1000s给最坏22.5e6s=6250核小时（单核串行260.4天），不含模型、profiling、500000投影、50000pairs、Fig3全m、去障与固定partition消融。只是量化上限，不是实际已消费预算。需要执行预算审批，不得偷偷缩500次。
- 原论文不给完整各方法采样seed、版本、末端/障碍全部尺寸、所有准确起终值、Comau variant/模型、全部规划step、超时统计和Fig3/4/5原始数据。合理重建要认证参数来源、标INDEPENDENT-RECONSTRUCTION；已有ABB输入也需独立闭链/碰撞/分支资格。
- TableII直接参照值（RSS/PCS/NR）：Pv% .85/1.31/23.74；d .6/1/2.6；avg samples5544/532/151；failed%83.64/20.48/16.17；sampling%3.03/19.05/27.80；local ms4.97/.32/1.40；checks/s102/1639/508；local%50.73/53.82/71.58；tree nodes476/408/13；path nodes26/29/7。
- TableI的36个数值与9个dash已逐页视觉核验；原表仅是参照值，不能新运行缺失时挪作我们结果。原“均时500次”与失败删失细节UNKNOWN，需双口径保存actual success runtime及censored budget。

## 交叉审查结论

现有29项是必要初始账本，新增T30后至少30项；未开展新科学case，不给任何Gate PASS。旧P4平面源码、60调用、RSS失败与PCS零解路径切换事实继续有效，但只能对应旧INDEPENDENT-RECONSTRUCTION/PARTIAL记录。D079可执行的作者算法资格、全环境来源审查和预算必须接续，不能以旧3/3记录自动放弃，也不能未经审批显著扩算力或假定未公布Comau模型。
