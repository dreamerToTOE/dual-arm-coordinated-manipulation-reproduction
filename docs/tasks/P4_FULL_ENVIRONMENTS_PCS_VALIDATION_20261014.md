# P4 续研任务：六环境重建、三算法实证、PCS 复杂障碍优势验证

日期：2026-10-14。状态：USER-AUTHORIZED / TASK SPECIFICATION；**不是已经完成的实验**。
当前执行分支：p4-full-reproduction-pcs-study。基线为已归档 P2 文档分支提交 4cb0e96；原 P4 和 P2 已接受历史结果均不得覆盖。
**Codex 从本文开始逐门推进；每个关口提交实际源码、可复查结果与报告。无证据不得宣称完成。**

## 0. 总体目标与论文对象

论文：Sintov, Borum, Bretl (2018), *Motion Planning of Fully-actuated Closed Kinematic Chains with Revolute Joints: A Comparative Analysis*, DOI: 10.1109/LRA.2018.2846806。
权威作者稿：https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf
作者实现参考：https://github.com/avishais/CKCplanning/tree/909bd72fff778aca8682c96f9eb86ae4eb75557b

研究问题不是仅让 RSS/PCS/NR 能运行，而是通过原文各类平台揭示闭链投影方法的适用条件：RSS 奇异采样、PCS active/passive 链划分切换、NR 全链数值投影，加上共同局部连接 RBS 与规划器。特别检验论文提出的 PCS 在复杂障碍环境下可能优于 NR 的条件，不预设一定会观察到优势。

旧结果：20R平面同类重建 E0/E1，RSS 0/20、PCS 20/20、NR 20/20。历史不等于原文六环境、不证明 PCS 真实换链优势；PCS 成功路径的划分切换为 0，E1 障碍没有改变成功路径。旧档案只读，不能把旧 60 次混入新实验统计分母。

## 1. 禁止事项与可用基础

- **保全**：旧 P4 的 reports/P4_THREE_METHOD_POST_TASK.md、全部旧 reports、results、baselines/p4_comparison 和旧 Word/PDF 作为既有版本保留。P2 用户接受冻结版本 f4f9d3b/7787c75、P2 报告和所有其他算法任务均不得覆盖或重写结论。
- 新代码放在独立命名空间（建议 baselines/p4_full/、platforms/p4_full/）；新配置放 configs/p4_full/；新实验结果使用唯一运行 ID 和 results/p4_full/ 子目录；新报告用 reports/P4_FULL_*，不得覆盖旧实验和 Word。
- 这轮用户**明确重新授权** P4 扩展，不受旧 P4 三次工程修正额度所代表的“已停止本轮”的禁止；但旧修正预算与旧结果仍保持原样。新的资源预算、协议、变更及异常停止记录须单独版本化。
- 不实施 P2 内力控制、P3/P5/P1、不改 FR3/Isaac 主工程物理模型、不启动真实机器人、不改 benchmark 物理/ACM/力阈值。统一场景迁移仅在五篇复现完后再审。
- 禁止为追求作者排名而重设难度、成功容差、种子、弃置失败、切换方法定义或使用 GT/另一算法兜底。所有论文结果与独立重建结果分别出表。
- 原作者代码、网格、机器人模型如无明确再分发许可，只参考、引用或在合法授权下安装依赖，勿复制进入本仓库。私有论文 PDF 也不可上传。
- 不得由一幅图片推测毫米级几何并标注为 ORIGINAL；不明尺寸、抓取姿态、工作台与障碍应在证据清单中标明未知和重建假设。

## 2. Gate 0：先审计六个原环境和作者代码

**在编程/批量实验之前先完成** reports/P4_FULL_SOURCE_ENVIRONMENT_AUDIT.md，至少包含：
1. 逐页复核论文 II–IV、Fig.2、Fig.3–5、Table I/II、原文具体成功判定与统计预算；记录论文页码/图表位置、原文数值及获取渠道。
2. 逐项检查 CKCplanning 固定版本（尤其 ABB 两平台、8 IK 分支、RSS 真实奇异目标、PCS CBiRRT 划分、NR 及局部连接）；可用官方资产 / geometry / 初始构型 / 工作空间坐标 / 控制规划器 / 缺失依赖与许可证。
3. 六环境逐个记录 ORIGINAL 可精确复用什么、AUTHOR-CODE 直接支持什么、INDEPENDENT-RECONSTRUCTION 哪些需要补建、UNAVAILABLE 哪些不能填补；为每个环境提供证据链接和文件 SHA。
4. 从 6 环境和多规划器组合解释是否能与作者原表直接对照；作者代码没有的 Comau/平面精确配置，不准默写为精确复刻。
5. 用非实验的资源审计证明本机可获得/可许可的资产和依赖版本，形成缺件清单。若重要机器人几何/抓点条件缺失，先提交可证实的独立重建方案并标明偏差；不要停止全部工作或编造原资产。

环境目标表（确切图号/对象名以 Gate 0 全文核验为准）：

| 环境 | 原论文系统 | 后续任务 |
| --- | --- | --- |
| I | 平面20R闭链 | 找回/核对原参数；与既有 E0/E1 分开，重建原环境或具名替代 |
| II | 双ABB IRB120 | 优先从作者程序核对两臂闭链抓持、基础障碍和规划器；建完整3D运动学/碰撞 |
| III | 双ABB IRB120 | 复核原图的受限/窄通道条件；保持与II同机器人而障碍不同 |
| IV | 双Comau | 核实机器人具体型号与原场景；可用合规模型补建 |
| V | 双Comau | 同系较复杂障碍/装配通道；严格分离源证据和独立重建 |
| VI | 三Comau、多闭链 | 按原式进行两个及以上独立闭合约束；不能用双臂单闭链“代替” |

**Gate 0 输出**：数据可用性表、来源和许可清单、原作者与我们几何差异清单、执行预算估算、各环境真实建模可行性与风险。完成后再进入 Gate 1，缺核心事实时记录并提交用户裁决，而不是猜测原值。

## 3. Gate 1：空间模型和独立有效性资格

优先顺序：原论文 II/III 可用 ABB 环境 → IV/V Comau 环境 → VI 三臂多闭环 → I 原平面补强。
每个平台均实现可追溯 FK/Jacobian、关节限位、刚性物体与抓持变换、正确维度 SE(3) 闭链 C(q)=0、障碍/自碰撞/互碰、碰撞模型、合法起终点和可视化。三臂系统明确多个独立闭合约束及其秩。

验证不能只依赖规划器输出：数值有限差分 Jacobian vs 解析、闭链残差、姿态误差、已知正/负碰撞例、人工奇异分支、被动子链 IK 分支数量、距离参考点与单位、合法起终点相互可连接的独立证据。
如果原精确模型无法获得，需同时提供“作者场景可比程度”评级和重建资产 manifest；按环境分别判断而非把全套叫原样复现。
代码写单测 + 环境 smoke test，负例确实被拒绝；各实例有配置 JSON/YAML、场景截图/图示、坐标系和几何来源表。
Gate 1 不能因为“模型创建成功”就标三算法复现成功。

## 4. Gate 2：RSS、PCS、NR 和规划器/局部连接统一资格

- 先对同一环境做三方法可执行性：RSS 真实被动奇异条件及合法跨分支桥接；不能靠普通NR兜底。现有RSS 0/20的奇异采样根因应单独检查和解释，不能只重试。
- PCS 必须支持每个机器人模型上至少两组合法且真正不同的 nonredundant 被动划分（如果只有一组或者求解器缺分支，则标不可用并给出结构证据）；记录每次选择、退路尝试、tree edge、final path edge 的划分和 IK 分支、切换位置和切换前后全链一致性。三臂情形显式核验两条被动链共同可连接条件，不能照搬双臂判据。
- NR 是全闭链雅可比伪逆数值投影，不允许以解析 IK 代替；记录迭代、奇异值、失败、代价、参数差异。
- 共享规划器（作者对应 RRT / Bi-RRT / SBL 等，按原文可比清单落实）和 RBS 局部连接、碰撞、距离与计时口径。对同一个 planner/环境比较三方法；不要只给 RSS 一个劣势参数。
- 覆盖主要合法 IK 分支、人工奇异、局部连接、分割限制与完整路径；证明局部路径的离散闭链/碰撞资格，必要时更密重检或 CCD，并注明离散保证边界。
- 若作者各法使用不同最佳步长/距离，设置两份独立协议：“原文参数/合理复原调优”和“统一参数诊断”；两份数据不混，也不把统一参数统计冒充原文复刻。

## 5. Gate 3：PCS优势验证——先冻结假设和公平测试

研究假设（必须允许被证伪）：
H1：低障碍情况下 NR 因局部连接可见性与路径较短，性能可能优于PCS；
H2：高障碍/窄通道下，PCS 的局部连接投影成本和分支覆盖有机会抵消其局部可见性不足；
H3：PCS 全划分相对 fixed-partition PCS 在需要改变人工奇异集合的任务中有优势；
H4：RSS 随机有效奇异目标及远处连接可能拖慢其全局搜索，但要与作者原实现和有限预算机制区分。

至少有：无障碍对照、逐级加密障碍、窄通道、需要不同分支/划分的验证 fixture、多闭链场景。困难条件必须有独立合法可行路径证据或给“可行性未知”标签；防止把无解问题算成某算法更差。不能先试跑种子再挑只对PCS有利的地图。环境密度、种子、抓持和起终点在正式试验前冻结。
设置 **full PCS / fixed-p0 / fixed-p16 / NR / RSS** 的明确消融，不准把固定划分版本误写为论文完整 PCS。若多个合法被动划分，扩充消融；每个原生规划器内部成组对比。

要求记录：每次调用成功/失败原因及右截断预算、到达目标的实际时间（未成功则删失）、全调用耗时、投影/IK单次耗时、RBS局部连接成功率与开销、采样成功率、树节点、碰撞拒绝、净距、路径长度/平滑度、可见性随构型间距的曲线、真实执行过的换划分次数（树上与最终解路径分开）。PCS 全局成功不等于最终路径必有换链；机理验证还需专门 witness / 划分消融。
统计比较应报告配对的随机种子与同环境预算；成功率及不确定性、对删失时间妥当处理、成功条件下时间分布和独立 CPU 平台信息。不能比较“RSS 5s失败时间”和“NR 35ms成功时间”的倍数作为性能胜负。

**规模纪律**：先跑资源 smoke/小样本 pilot（建议每组10个）排除实验框架错误；随后每环境/算法/规划器至少30组固定配对种子建立可靠趋势。原论文空间实验的每法/规划器 500 次以及原 1000s cutoff 是对齐目标；完整规模与硬件运行成本在 Gate 0 报预算，不得私自缩减成30并声称与原500次同强度；超过本机/预算则报告并请求下一步决策。数据不允许只留成功试验。根据原文 Table I/II 与 Fig.3–5 分别重建可比项目；不能因统计巨大提前跳过 VI 或无失败日志。

## 6. Gate 4：报告、解释与场景迁移判断（严格最后开展）

报告结构延续科研汇报：原论文数学/算法 → 原文六环境和算法定义 → 我们各环境真实实现、资格与参数 → 三方法统一对比（含PCS困难场景消融）→ 与原文差异/失败 → **独立的“对双FR3场景可借鉴思想与实施条件”**。
不能只写“可以用于Isaac”，应逐方法、逐模块填写：
- P4 NR / RBS / PCS / RSS：核心原理、我们实证证据、适用 Benchmark A 共同搬运的具体环节、接口输入输出、需要哪些机器人/抓持/碰撞模型、当前未满足的依赖、潜在优势与失效条件；
- 与现有 MoveIt2/OMPL、闭链轨迹生成、FCL、接触控制的差异与不可直接照搬点；
- 候选小改/与P2位姿-内力协调、P5-QP等组合的假设、可检验指标与公平基线；
- 推荐/不推荐/暂时无证据的分级以及证据级别 ORIGINAL / VERIFIED-REPRODUCTION / ADAPTATION / PROPOSED；
- **只写迁移方案，不修改FR3/Isaac工程，不把概念提案当成已验证结果**。
所有论文 P1/P2/P3/P4/P5 的复现报告尾章必须按该标准执行，详见 docs/PAPER_REPRODUCTION_REPORT_FORMAT.md 最新规则。

## 7. 源码、实验记录、报告交付与停止

每个 gate 依次产生：PRE-TASK、POST-TASK、源 SHA/config SHA、命令与软件版本、结果原始记录、错误与原因、6份状态记录（STATUS/WORKLOG/EXPERIMENT_LOG/BUGS/DECISIONS/USER_FEEDBACK）、下一步是否可开始。新数据先冻结协议再运行，失败要留下证据、不能一边测一边改考题。
最终提交中文可编辑 Word + PDF、三方法环境指标图/可视化、独立结果复核脚本、实际可复现命令、逐环境原文与我们两栏对照、授权依赖清单、完整负例、关键 blocker 与用户审核结论。
若外部资产许可、无可验证空间闭链、环境VI多闭环或核心数学等实质问题挡住，则明确部分完成、产出阻塞报告和替代路线，不默默跳过某个环境。不得在没有完整验证数据前填 PCS 更优的结论。
本轮 Codex **不能自动启动 P3/P5/P1 或 Isaac 应用**；五篇统一复现完再作系统扩展。用户要求 P4 深化后才作算法迁移判断，所以 Gate 4 必须后于 Gate 1–3 的真实数据分析。

## 8. Codex 启动工作指令（用于 VS Code / Codex）

读取本文件及 CODEX_START_HERE.md、docs/PAPER_REPRODUCTION_REPORT_FORMAT.md、reports/P4_THREE_METHOD_ORIGINAL_AUDIT.md、reports/P4_THREE_METHOD_POST_TASK.md、baselines/p4_comparison/README.md 和原论文。
先在 p4-full-reproduction-pcs-study 分支复核原 P4/P2 保护清单和只读作者代码，再完成 Gate 0 环境/授权/接口审计，写 PRE/POST 和差异清单。随后**按照已经定义的 Gate 1→2→3→4 实际推进代码、单测、规划实验和报告**，以真实文件/数据为准。对非实质工程实现问题可按预先记录的正确性测试修复；科学模型假设变化、重要资源缺失或正式实验协议变更须用户裁决。每个 gate 单独提交/输出证据，不能用占位图、虚构表、旧 P4 数据或仅代码通过冒充完成。严禁修改既有 P2/P4 历史实验及用户已接受结论。

## 2026-10-15 — R2用户批准974上限及固定64点组合离散资格实测

用户明确批准原剩50加新增14，VI B总上限960→974；单项30wall/60CPU及累计180wall/360CPU保持，无正式规划预算。批准原文逐字保存于configs/p4_full/r2_vi_rss_ingress_composite_user_approval_20261015.json，源码/协议冻结243fa05。固定清单、原解析支、δ=.01、h=.0025、γ=.2未变，不换点或加深；原Q2 UNKNOWN、原center、六fiber及所有失败保留。

单次INGRESS_COMPOSITE01实际64/64节点及四条regular↔fiber接入离散门通过，PASS_RECONSTRUCTED_COMPOSITE_DISCRETE_ONLY。96条regular叶和6条保存fiber叶均严格<h；四半regular最大叶距分别.001726025161094/.001850849712175/.001488951615670/.001491095303782rad。数学FK/J704、adapter内部192（合896）、IK1024、源碰撞64；实际wall14.198019690000/CPU10.876665。此为明确标记的独立重建组合，不是原作者RSS/RBS忠实实现证明、连续无碰撞或全局RSS规划成功。

VI B累计974构造，余额0；累计wall68.712002153999/CPU24.203842，余111.287997846001wall/335.796158CPU。13run自身消耗逐份计入R2总账，合wall109.563377079999/CPU55.934698，余3490.436622920001/7144.065302。不得使用旧快照余50再次构造，不重置claim。新账本results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V3.json，旧9/12run账本不改。

最新211项对照reports/P4_FULL_R2_INGRESS_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv/.md保存全部历史列，另列本次组合资格；13run报告P4_FULL_R2_VI_RSS_INGRESS_POST_TASK_20261015.md及独立POST审查。正式Table I仍0/22500，500000配对投影、约50000合法点对、全部Fig.3–5/Table I–II及消融义务不缩。继续II/III普通PCS固定branch/RBS/回溯与三搜索器链接资格，先冻结版本/原返回对照/预算，0solve；工程成本另列并保守扣R2总帽，不扣已耗尽的VI候选账。P4仍部分完成，不P2/Isaac，不提前结题。


## 2026-10-15 — R2 ABB PCS原固定局部接口：10通过/6拒绝，整体部分完成

工程aa57c24冻结四目标source-native/R2 numerics×plain/trace，全部构建exit0，三PCS搜索器仅链接，实际wall94.592335203997/CPU130.109068；232产物/source/claim/recipe/commit绑定经独立复核。科学95851e0冻结后单次LOCAL01，无超时/异常，actual wall81.132350082000/CPU78.392314。320顶层project，20RBS，20回溯（180plain/trace逻辑对）；442trace固定branch投影、364成功输出独立复验，752数学FK、368碰撞/1472adapter内部FKJ，78252adapter及29618源内部PQP查询，非上限填充。

R2数值10/16固定局部边通过非阈值提前返回的真实RBS/回溯、闭链、原branch/限位及source aligned离散碰撞；6拒绝分5源投影false+1碰撞，保存目标必要代数门独立确认3几何workspace拒绝、2原q3下界拒绝，未新FK/IK，不能称全部几何不可达。II start主动arm2、II goal主动arm1缺本固定h正例，整体FIXED_LOCAL_ABB_PCS_PARTIAL。作者原数值16局部端点全拒绝，原失败留存；未换h/中心/分支重试。44个下游模板依预置gate未执行，不是超时丢尾；三个planner solve/RNG0，不推出全局PCS或优势。

新15execution为14science+1新engineering，逐自身实耗保守计R2合wall285.288062365996/CPU264.436080，余3314.711937634004/6935.563920；工程不当science成功，VI B仍974/974余0。新账V4保V3及旧12/9run原字节，新ABB_PCS完整211表保前68历史列，正式TableI仍0/22500及全部原分母不缩。继续固定失败根因、IV100×8原wrist数学资格及其余环境/方法门，先独立冻结预算、无正式规划/P2/Isaac。实际记录results/p4_full/20261015_R2_ABB_PCS_LOCAL01/execution.json；审查reports/P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_REVIEW_20261015.md。


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


## 2026-10-16 CBiRRT D P完整413节点离散路径独立通过，V18交付

c5e4d2e冻结P唯一运行，环境II/RECONSTRUCTED A01/版本化几何和D距离接口，原S02候选四真M109/145/33/129完整413唯一节点/412叶；P没有再solve/RBS/IK/NR/采样。原五回溯[T,T,F,T,T]及M[109,145,2,33,129]全保留，role0 false29266/M2→role1 true29271/M33不改判。413/413全数学/限位/关联被动branch/离散collision通过，独立保存POST58152/58152、失败0、external/path true，SHA2c548df054867c7d9545fac3726142f3581b3cdfbe54299233a27bb07bace4d0；原execution/charge false及S02候选状态不回写。

真实数学臂FK826/branch826/collision413/adapter内部FKJ1652/PQP95816；双worker88329/88330 exit0/reaped、起闭组及EOF/pending/tail真门通过。保存闭链max4.547473508864641e-13mm/6.730727086790012e-16，限位最小余.016467847389747492rad、叶max.049872908712302065<.05。四段主动[0,0,1,1]/branch均3只是切换机制见证，无优势统计。独立variant附录1659/1659、SHA287a9dd1877b17e3cf439aca891c5832869f5b40973e9757f6314c8822be705a：native413全部TCP pose mismatch，最大.003531998994674268mm/6.824437533303751e-6，native物理pose未合格；aligned413全部pose通过，最大3.410605131648481e-13mm/4.440892098500626e-16。两raw collision均0、各47908PQP，接纳仅原已冻aligned策略，不称native几何全过。

外层104.88wall/11.8CPU（原GNUtime104.87/10.53/1.25/0）在120/240内，仅替换内部样本一次，包含完整物理/保存链核验与清理/持久化，不作论文性能样本。V18实际36execution=29科学账+7工程，charged685.555705375994wall/542.4289229999999CPU，余额仅上界2914.444294624006/6657.5710770000005；历史未测尾部UNKNOWN保持。最新CBIRRT_D_PATH完整表211×158保前154；V18保全实际PASS、七组mismatch空，1028旧科学文件、57崩溃文件8482891B/tar、5其他工作树13未提交、旧V17与历史列保留。主POST见reports/P4_FULL_R2_ABB_CBIRRT_D_PATH_POST_TASK_20261016.md，personnel_independent=false。

此证书只覆盖本版本完整离散source-policy起终路径，不证明CCD/实体杆/省略pair/原native几何/RSS分布/复杂障碍PCS优势/成功率或论文完整。原S01/D64/H STOP与UNKNOWN、split证书边界、旧PCS177/NR393保持；VI974/974余0、正式0/22500、全部211义务及原统计规模不缩。下一继续其余原生搜索器和环境资格，RSS解耦诊断；端到端后成本pilot再申请正式预算，不自动正式大规模/P2/Isaac/结题Word。


## 2026-10-16 CBiRRT_NR BUILD01依赖留证停止与V19实际账

203c6ff唯一工程compiler exit0/reaped、前后空组，但-MD配-o实际只生成最后TU同名.d，未满足六TU独立依赖留证；STOP_PREFIX_RETAINED保留。二进制848464B/7c6ac348...实际存在但无成功manifest，binary/query/solve/VI/formal均0。独立保存13720/13720仅证明失败/费用一致，engineering_build_qualified=false；根因为我们工程设计与V4静态审查错误，不归因作者算法或论文。原源码/协议/claim/stage/二进制/完整日志/唯一.d/旧报告全部保留，禁止补造缺失依赖或复用该claim。见CBIRRT_NR_BUILD_POST_TASK、BUILD_ROOT_INDEPENDENT_POST及BUILD01_FAILURE_ROOT_CAUSE。

GNUtime33.95 44.43 11.03 1，上界33.96wall/55.48CPU已独立确认并替换内部样本一次。V19实际37=29科学账+8工程，累计719.515705375994wall/597.908923CPU，余额上界2880.484294624006/6602.091077；历史未测尾UNKNOWN不改。完整211×162表保前158列；V19保全PASS，旧1028科学/57崩溃文件及tar/另5工作树13未提交/V18全部保持。

下一项仅新版本BUILD02，依据GCC官方-MF -让六TU规则完整写独占stdout，再逐raw规则/TU/保护依赖留证；原算法body与数值源码不改。新45wall/90CPU扣R2总3600/7200，先独立静态/协议/commit冻结后唯一构建，不是同claim重试或预算重置；科学solve仍另冻。VI974/974余0，Table I0/22500，211义务及全部原规模不缩；不P2/Isaac/提前结题。


## 2026-10-16 CBiRRT_NR BUILD02六规则完成、五PQP头未冻停止与V20

909d6aa唯一BUILD02 compiler exit0/reaped/空组，-MD -MF -完整196455B六TU原raw规则/TU once/派生切片均已形成；末门发现BV.h/PQP.h/PQP_Compile.h/PQP_Internal.h/Tri.h五PQP头未冻，STOP_PREFIX_RETAINED。五真实SHA在bound无同值别名，其他743实际依赖中受管无额外缺项；这是我们工程资产冻结遗漏，不归因算法或论文。原BUILD01与本次所有源码/参数/协议/claim/ELF/raw/失败保留，不运行后补清单改判，不复用claim。

独立保存13762/13762只证明失败/费用/六规则事实一致，engineering_build_qualified=false，外层监督true。GNUtime33.56 43.99 10.98 1，上界33.57wall/54.99CPU只替换内部样本一次。V20实际38=29科学账+9工程，累计753.085705375994wall/652.898923CPU，余额上界2846.914294624006/6547.101077，历史未测尾UNKNOWN。211×166保前162列，V20七组保全PASS，旧1028科学/57crash及tar/另5树13未提交/V19保持。见BUILD02_POST_TASK、BUILD02_ROOT_INDEPENDENT_POST与BUILD02_FAILURE_ROOT_CAUSE。

下一新BUILD03仅补五PQP头冻结，并依据已保存全部实际依赖做静态完整核对；原科学源不改，新45wall/90CPU仍扣R2总3600/7200。先静态/PRE/协议/commit冻结后唯一工程；binary/query/solve/VI/formal目前0。VI974余0、TableI0/22500、211义务与全部原规模保持，不P2/Isaac或提前结题。


## 2026-10-16 CBiRRT_NR BUILD03仅工程独立通过，V21实际交付

c5a75ab唯一BUILD03 BUILT_NOT_QUERIED、compiler exit0/reaped/空组/diag0，六TU完整raw规则/743实际依赖/全部受管预冻SHA/派生切片均合格。独立POST13927/13927，engineering_build_qualified与external监督true，binary/query/solve/VI/formal仍0。前两STOP/原源码/ELF/raw/claim和全部费用保留；只补五PQP头预先绑定，科学三稿/full12 NN/双树/RBS/回溯/physicalGD接缝不改，继续RECONSTRUCTED。见BUILD03_POST_TASK及BUILD03_ROOT_INDEPENDENT_POST。

GNUtime33.73 44.96 9.87 0，上界33.74wall/54.85CPU只替换内部样本一次。V21实际39=29科学账+10工程，累计786.8257053759941wall/707.748923CPU，余额上界2813.174294624006/6492.251077，历史未测尾UNKNOWN。211×170保前166列，V21七组保全PASS，旧1028科学/57crash及tar/另5树13未提交/V20保持。

下一仅另冻II/A01/seed7/range2.6/原10秒单solve外30/60；EXACT候选需完整原M独立路径另120/240/max2048资格。RSS静态下一门报告已另交，SBL源码.05与γ=.2差异保留待裁决；不新增VI。VI974余0、正式0/22500、211全部义务与原规模不缩，端到端后成本pilot/正式预算另审，不P2/Isaac/提前结题。


## 2026-10-17 CBiRRT_NR SOLVE01完整候选与V22接续交付

119a1b3冻结唯一II/A01/seed7/range2.6/原10秒solve，source EXACT非approximate、16Motion、12里程点、11真实回溯全true。原M长度65/65/17/65/129/129/65/33/33/33/65，699引用完整连接689唯一节点/688叶，bridge16→14两端q不同保留。原stdout/stderr/原生paths、GD29/project45/midpoint44/vectorRBS365/stateRBS46 false全保存；单write/EOF、严格唯一JSON、双actualEOF、exit0/reaped/空组、diag0。独立保存POST16711/16711，SHA549d585f1fb2be390b28a0d64dfb90815e58092a9efd7e3c4d478abebe381ef1，只证入口/完整素材/费用，source状态与independent_path_qualified=false不回写。主POST见reports/P4_FULL_R2_ABB_CBIRRT_NR_SOLVE01_POST_TASK_20261016.md。

GNUtime9.05 7.51 1.18 0，上界9.06wall/8.71CPU替换内部样本一次。V22真实40execution=30科学账+10工程，charged795.885705375994/716.458923，余额仅上界2804.114294624006/6483.541077，历史未测尾UNKNOWN保持。完整211×174保前170。旧账遗留solve累计字段未覆盖所有新入口，原字节保留；V22_ADDENDUM按真实dispatch逐run修正为此前4+本次1=5（含PCS CBi S01失败），正式仍0/22500，不将5调用当5合格路径。

下一完整689节点P先独立静审/真实证书及V22账绑定、源码协议commit冻结，再唯一120wall/240CPU/max2048；不重solve/RBS、补点或截尾。旧413逐文件fsync耗104.88wall已识别工程成本风险，P拟沿NR393原即时close写法与科学AST，最终逐字单tar/fsync耐久证据及全预算核验；实际资格尚未执行。RSS新静态契约保留SBL .05/冻结γ=.2差异、RRT禁exact、CBi serial导出与SBL -2风险，仅源码证据，0新RSS/VI。VI974/974余0、全部211义务及原45×500/1000s/投影/可见性/图表/消融不缩；端到端后先可重复成本pilot再申请正式预算，不P2/Isaac/提前结题。


## 2026-10-17 CBiRRT_NR完整689节点离散起终路径独立通过，V23

742fff2冻结唯一P，II/A01/RECONSTRUCTED physical NR的11原M、699引用、689唯一节点/688叶完整资格通过。实际source-policy math/原限位/aligned collision689/689全true，独立POST41787/41787、失败0、path/external true，SHAb3a2443cb790df547597fe5a72b4eeb78341d2f93a4b4beca8252eba692c40c8；原execution false、S原候选及全部旧GD/project/RBS false/STOP/UNKNOWN不回写。闭链max9.8002665254171e-6mm/4.6722628137957356e-8、原限位余.08726666666666683rad、叶max.04951897373867186<.05。mathFK1378/collision689/adapterFKJ2756/PQP159848（两variant各79924）；native collision0但TCP0/689、aligned collision0且TCP689/689，不能称native几何资格全过。主POST见reports/P4_FULL_R2_ABB_CBIRRT_NR_PATH01_POST_TASK_20261017.md。

NR393 counted/科学loop/即时close writer逐AST不变，完整散文件与3447成员tar逐字核验/fsync，真双worker EOF/exit0/reaped/空组/diag0。GNUtime19.58 15.94 1.87 0，费用上界19.59wall/17.83CPU替换内部样本一次；P无新solve/RBS/IK/投影/采样。V23真实41execution=31科学账+10工程，charged815.475705375994/734.288923，余额仅上界2784.524294624006/6465.711077，历史未测尾UNKNOWN保持。v3账保留旧费用/历史并逐execution明确source累计5、本P新增0；211×178保前174，V23七组保全实际PASS空mismatch，1028旧科学、57崩溃文件8482891B/tar、五其他工作树13未提交及V22完整保持。

离散证书不证明CCD、实体rod/省略pair安全、nativeKDL等价、全局成功率、RSS或PCS复杂障碍优势；全部211义务、原45×500/1000s与投影/点对/Fig3–5/TableI–II/消融不缩。VI974/974余0、正式0/22500。下一SBL专属默认projection公有线性作用观察、lazy删树代际/未初始化a_chain不读、原bridge/M契约，先工程版本化静审与冻结；RSS独立继续原RBS/分布/入口诊断，不增VI。端到端后可重复cost pilot和正式预算另审，不P2/Isaac/提前结题Word/PDF。
