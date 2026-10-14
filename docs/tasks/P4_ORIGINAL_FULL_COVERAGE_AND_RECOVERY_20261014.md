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
