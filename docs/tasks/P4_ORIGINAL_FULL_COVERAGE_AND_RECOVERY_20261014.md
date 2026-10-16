# P4 全文实验义务与失败恢复任务（D079，不缩减）

**论文**：Sintov, Borum & Bretl, *Motion Planning of Fully-actuated Closed Kinematic Chains with Revolute Joints: A Comparative Analysis*, IEEE RA-L 2018，DOI 10.1109/LRA.2018.2846806，作者预印本8页。私有原版资料从用户 Library 已核对；执行环境中必须重读作者稿、附录和作者仓库固定版本909bd72。旧审计见 reports/P4_THREE_METHOD_ORIGINAL_AUDIT.md。

**目的**：不再采用“两个平面环境+60调用”替代全论文。下面每条都是应处理的科研义务；旧结果如实标注、不能重新定义成PASS。原论文可复现性不佳时独立重建并明确与原文差异，但**不以重建结果冒充原论文原条件**。

## 一、原论文完整复现项目表（不可删除）

| ID | 原文出处 | 本次必须复现/验证 | 2026-10-14 旧实验状态 | 分类 |
|---|---|---|---|---|
| P4-T01 | II-A Eq1–3 / Fig1 | 完整闭链构型/有效空间/各类人工奇异及可见性定义 | 仅平面20R部分数学 | MODEL |
| P4-T02 | II-B.1 + original code | APC被动链解析IK/所有可达分支、成功与失败采样 | p0/p16两组3R，不是ABB/Comau IK | ALGORITHM |
| P4-T03 | II-B.2 | NR全链Jacobian/SVD投影及数值收敛/失败 | 平面3×20 NR可规划；空间/多闭环未执行 | ALGORITHM |
| P4-T04 | II-B projections | APC vs NR 500000随机样本：投影成功率、耗时分布及成本；原原环境设定 | 未执行论文原样实验 | EXPERIMENT |
| P4-T05 | II-C | RBS递归中点/IK分支/碰撞局部连接、失败与精度 | 平面离散实现；空间未验证，作者RSS局部捷径没沿用 | ALGORITHM |
| P4-T06 | II-D Eq3 / III Eq4–9 | 可见域、独立/依赖被动链的统计上界及理论适用条件；解析+模拟核对 | 仅局部理论核验，未做空间条件对照 | THEORY |
| P4-T07 | III-A Fig1 | RSS合法人工奇异目标生成与跨IK分支路径 | 固定构造通过；随机目标313请求9996尝试0合法，规划0/20 | FAILED |
| P4-T08 | III-B Eq5–9 | PCS变换多个被动链、选择共有可连接IK分支、搜索树和解路径切换证据 | 两组划分参加搜索，最终解92边只用p0，解上0切换 | PARTIAL |
| P4-T09 | III-C | NR与PCS/RSS在共同规划栈和独立原生栈中的真实代价比较 | 仅单自建BiRRT栈 | PARTIAL |
| P4-T10 | IV Fig2(a) | 原环境I平面20R障碍/关节界/精确起终点、奇异跨分支 | 仅同类E0/E1，无原精确输入 | RECONSTRUCTED |
| P4-T11 | IV Fig2(b) | 原环境II双ABB IRB120搬杆跨杆障碍，刚性闭链 | 未建 | NOT_ATTEMPTED |
| P4-T12 | IV Fig2(c) | 原环境III双ABB IRB120窄通道 | 未建 | NOT_ATTEMPTED |
| P4-T13 | IV Fig2(d) | 原环境IV双Comau NJ-16搬杆/多障碍 | 未建 | NOT_ATTEMPTED |
| P4-T14 | IV Fig2(e) | 原环境V双Comau NJ-16吸盘抓箱输送带至安装位 | 未建 | NOT_ATTEMPTED |
| P4-T15 | IV Fig2(f) | 原环境VI三Comau抓环绕两杆、多闭环和独立约束 | 未建 | NOT_ATTEMPTED |
| P4-T16 | IV-A Fig2 all | 所有六环境起终点需要跨越奇异构型；可行路径/分支见证、碰撞/限位 | 当前E0/E1不证明此关键条件 | NOT_VERIFIED |
| P4-T17 | IV-A | RRT / Bi-RRT / SBL × RSS/PCS/NR 同环境算法比较 | 仅自建BiRRT，另外两类未做 | NOT_ATTEMPTED |
| P4-T18 | IV-A Table I | 环境II–VI × 三规划器 × 三投影方法：原500次/单元、1000秒上限、超时删失 | 旧60次仅E0/E1及5s | NOT_ATTEMPTED |
| P4-T19 | IV-A Fig3 | 环境I被动链数m=1,2,3,7,20与NR：局部连接成功率-距离、运行时间-链数 | 仅p0/p16，无m曲线 | NOT_ATTEMPTED |
| P4-T20 | IV-B Table II | 环境II可见份额、调优步长、采样/失败、采样占时、局部连接成本、树/路径节点 | 旧有非对应指标，不能对照 | NOT_ATTEMPTED |
| P4-T21 | IV-B Table II / Fig4 | 约50000合法点对局部连接概率、按构型距离分箱与方法对比；核对图注I和正文II差异 | 未做 | NOT_ATTEMPTED |
| P4-T22 | IV-B Fig5 | 投影前后邻点配置距离绝对变化随初始距离关系；APC对NR | 未做 | NOT_ATTEMPTED |
| P4-T23 | IV-B | 移除障碍前后 NR/PCS/RSS 在各空间环境表现；验证复杂障碍是否消弱NR可见性优势 | E1障碍不影响旧解路径 | NOT_ATTEMPTED |
| P4-T24 | IV-A/B | 每方法单独调优规划步长/距离和RSS γ=0.2；与统一参数公平诊断分开 | 只固定同0.6rad，没有原调优 | ADAPTED |
| P4-T25 | IV / Table I/II | 独立机器/OS/OMPL/KDL/PQP、作者开源版本与我们的运行/许可差异 | Python GEOS/NumPy，原平台数值不可直接比较 | ADAPTED |
| P4-T26 | IV-B | 局部路径可见性、平滑度、碰撞几何连续性、采样投影成本在复杂空间场景联合解释 | 仅平面离散资格，缺空间证据 | NOT_VERIFIED |
| P4-T27 | III/IV | 空间PCS独立和依赖被动链及多被动链数上限、解析IK可行性；三臂环结构限制 | 未验证 | NOT_ATTEMPTED |
| P4-T28 | V Conclusion | NR易推广、PCS障碍优势和分析限制在与原文一致的困难条件下是否成立 | 旧样本不足以支持结论 | NOT_VERIFIED |
| P4-T29 | 本课题扩展/末章 | 逐方法NR/RBS/PCS/RSS应用双FR3 Benchmark A/B、接口/依赖/风险及未来实证 | 旧报告有简要内容，正式完备分析待复现完成 | DEFERRED |

**表的总量不是性能评分**：以上29项是任务账本，不是29项所有PASS才证明论文理论绝对正确；任何实验如果不能核验需要提供有证据的BLOCKED，不能删行或谎报完整复现。正式执行前将每项细化到参数、源码、run_id、图、期望数值、观察数值、效应判断与署名来源，并以表的行ID命名报告索引。

## 二、平台和方法实施

按原 Fig.2 创建六个独立平台（注意 E0/E1 是原 I 类型重建，并不算两个原论文环境）；环境II/III的ABB作者代码优先复核、IV/V Comau NJ-16 及 VI 三臂抓环须检查真实URDF/网格/抓持变换/许可，不能以“双臂近似”代替 VI。所有平台都需关节上下界、真实刚抓约束、物体碰撞几何、SE(2)/SE(3)闭链、负例、奇异起终点和可复现配置；仿真引擎不必强制 Isaac，研究本质是路径规划。
每种环境逐项复现原作者中对应的 RSS/PCS/NR 实现机制；RSS真正生成被动奇异目标，PCS真实选择不同被动链的共有IK分支，NR用全链伪逆，不准算法兜底冒名；支持作者RRT/Bi-RRT/SBL方法及RBS局部检验，不把所有结果塞进一个BiRRT后称完整原实验。
对原方法调优后的运行与同参数诊断另开协议和结果目录，第一批只作环境、算法和起终点资格。先完成 Fig3/4/5 与 Table II 的试验设计、抽样定义和统计独立性核对，逐项处理原文图注/正文环境标签冲突，不私改原文。

## 三、PCS的决定性实验

提前构造并**冻结**可否证的条件：无障碍、窄通道、复杂障碍、不同被动链划分数、不同IK分支连通情况、三臂多闭环；所有难例必须事先有独立可行路径证据或标明“未证明可行”。包括 full PCS、fixed partition PCS（每一种），NR、RSS；如某特定机器人无法获得解析被动链，先记录机构上的数学不可实现性和所缺代码/关节几何，不能造一套普通数值投影命名为PCS。
PCS 的主要机理证据必须包含：成功路径的真实partition变化（不把树节点变化误当解上变化），分支身份、切换前后轨迹与碰撞/闭链合法性、分划消融成功率和每次投影/RBS成本；即使不发生路径切换，也必须报告其原因以及 full PCS 对 fixed PCS 的效应大小。另跑无障碍消融检验论文指出的 NR/PCS效率权衡。

## 四、旧失败诊断和恢复

旧 RSS：313请求/9996次生成/0合法奇异目标，20/20超时。优先按公式/源码追根：被动Jacobian真实秩、解析分支端点存在性、未公开模型、碰撞拒绝、采样度量、5s及32次尝试截断、Python/C++速差；将每类失败拆成可重复fixture+独立oracle，重新验证完整合法RSS规划。
旧 PCS：20/20成功但解上0换划分；并非算法失败，主要是缺乏见证机制的环境。专门验证复杂场景而不人为挑成功seed；与fixed分划消融后才允许评价PCS优势。
所有失败均遵守 docs/REPRODUCTION_FULL_PAPER_COVERAGE_AND_ROOT_CAUSE_PROTOCOL.md：相同假设3次修复后先交根因报告；属于我方实现应继续有证据修正+重跑全套，属于原文资源缺失则列出最小不可辨识输入/取得尝试；原论文理论错误只能作为严格独立证据的疑似问题报告。

## 五、验收 / 完成后交给用户

每个表行必须有 real run/validation log 或有证据BLOCKED/FAILED；正式 Table I 的原500次与1000s按作者口径申报预算，不能没经用户审核默默缩到几次。统计输出按原Fig3–5与TableI–II组织；成功与超时分母、实验时间和机器口径分开。结题生成 `reports/P4_ORIGINAL_VS_REPRODUCED_COVERAGE.md` + 可机读CSV，格式见 reports/PAPER_ORIGINAL_VS_REPRODUCED_MATRIX_TEMPLATE.md；同时更新中文Word/PDF并给用户展示表格。
最后按 NR、RBS、PCS、RSS 分别详细说明对当前双FR3双吸盘 Benchmark A 的应用接口、优势、前置条件及局限，以及为什么 Benchmark B 的单臂插入不适合直接照搬部分闭链算法。场景扩展只分析不施工。
**执行顺序**：复用已启动的 D078 P4 六环境分支和真实完成内容；本文件是更完整的 D079 测试清单，覆盖其先前可缩减措辞。不要重新做已证据确凿的成功部分，但必须逐条补覆盖。下一篇论文不得自动启动；用户审查表格后再决定。


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
