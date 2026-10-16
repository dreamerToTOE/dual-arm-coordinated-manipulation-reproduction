# DECISIONS

## 2026-10-14 — D077：用户接受P2本轮部分完成，冻结交付

用户明确选择“接受本轮部分完成，冻结交付（推荐）”。科研交付7787c75已接受；交付状态ACCEPTED/FROZEN，完整P2仍PARTIAL，不能改判完整论文通过。动力学70/70、组件35/35、时序2/2；ID11真实闭环3.948s估计域失效、未进入7/13s反馈，其他29未执行。修正3/3余0；所有源码/参数/原数据/失败/Word及P4保持原字节，冻结manifest逐一核对接受commit。

本次仅登记接受与冻结，无新科学运行或算法修改。D076待后续路线裁决已由“接受部分完成”收尾，原式18研究没有继续授权；不得因旧路线或“继续”历史消息自动重启P2、P3、Isaac、P4/RSS或FR3改进。新研究须新的明确任务。见[接受与冻结记录](../reports/P2_DELIVERY_ACCEPTANCE_FREEZE.md)。


## 2026-10-14 — D076：真实ID11在3.948s估计域越界停止，累计修正3/3耗尽

v3动力学70/70、E/C35/35、时序2/2通过；source513c36a实际exp3/seed7（原ID11）停止ESTIMATOR_MODEL_PAD_DOMAIN_INVALID，987控制样本至3.944s、最后事件3.948s、829更新/1619预测、GT控制读取0。真实pad仍在域内，估计rho-x−6.425mm/+5.207mm超±5mm，估计角速度260.0205rad/s而真角速度约8.1e−8；不是负协方差或连续3次未收敛退出。未到7/13s反馈，UF/UP都0；完整半步/其他29未运行，窗口RMSnull。P2仍部分完成，不冒称联合反馈有效。

累计小修3/3余0，原失败/JSON修正/零case启动/所有Word保留，无第四轮或条件修改。停止后只读日志/保存矩阵分析、真实绘图、中文17页Word/PDF、保全与GitHub交付；进一步原式18预测解释须另行限定范围，不自改Euler/substep/R/Q/惯量，不以GT绕资格，不P3/Isaac/P4/RSS/FR3算法。见reports/P2_CLOSED_LOOP_POST_TASK.md、P2_CLOSED_LOOP_DELIVERY_INDEX.md。


## 2026-10-14 — D075：小修3修闭环入口路径，累计3/3余0

suite01在run_case之前因relative/absolute路径比较启动失败，实际控制case0、30项NOT_EXECUTED；原source/失败留存。最终小修只入口Path.resolve及当前预算元数据3/0，科学模型/控制/观测/clock/原门限不改。新suite02先原ID11，之后原ID30资格；不做第四轮代码修正或无限调试。若出现真正数值/滤波/控制/模型问题，按既定规则保存停止并报告；原公式变更必须新裁决。


## 2026-10-14 — D074：动力学70/70、E/C35/35、因果时序2/2通过，进入原ID11完整闭环资格

v3来源45a547c，固定N/D70/70、wall11.248585s，三fixture粗/半步五秒积分全部通过。E/C组件source5bfcafd实际35/35；clock来源d90f32f实际2/2。组件通过不等于完整闭环，原观察器式18仍Euler无内部substep。新runtime已冻结，按原case ID11 exp3/seed7 coarse，随后仅原ID30 fine，资格之前其余28不运行。原failedFD/诊断/Word和P4保存；累计小修2/3余1，重大新预测/模型/条件问题仍按规则留证停门。


## 2026-10-14 — D073：明确批准仅native连续Jacobian五点四阶资格

用户已批准五点高精度oracle版本化，保持ε1e−6/绝对门1e−7及全部物理/控制/观测/式18，原FAIL_STOP保留。新v3按同一固定N/D重新资格，全部通过后继续原组件及闭环。累计2/3余1，本次数值资格裁决不重开小修预算。不得再次为同一批准征询；若新的物理/滤波/协议门失败则按规则留证。见reports/P2_IMPLICIT_V3_QUALIFICATION_SPEC.md。


## 2026-10-14 — D072：隐式路线首门固定中央差分失败，暂停下游科学执行

已批D071来源37ccba0；native N/D记录45通过/1失败，零隐式积分/零滤波/零控制。失败为原ε1e−6的连续field Jacobian二阶差分与AD差6.381524e−7>1e−7；独立Python解析与AD最大逐分量差6.522214e−10。固定三点诊断误差加倍/减半比3.999/0.250，支持截断误差解释，不改判原FAIL_STOP。更换native资格oracle为同ε/同门限的五点四阶差分仍需新的明确裁决；未实施或执行，不改observer Eq18。按用户第2/9节停门，隐式五秒/半步/组件与30控制case未执行，P2部分完成。

诊断summary因numpy.int64 JSON错误exit1，三份矩阵已保存；小修2 ee97134仅转Python int和只读恢复已有数据，不重算。P2累计2/3余1，source/原失败/影响全部保留。原v1/批准几何/canonical force与P4/RSS/旧P2保全，不P3/Isaac/FR3优化。见[数值结果](../reports/P2_IMPLICIT_QUALIFICATION_RESULTS.md)、[修正2](../reports/P2_IMPLEMENTATION_CORRECTION02.md)、[任务摘要](../reports/P2_IMPLICIT_POST_TASK.md)。


## 2026-10-14 — D071：批准隐式耦合Lie中点plant，原观察器保持

用户明确批准“隐式耦合Lie中点plant：版本化数值协议，先做等价计算优化与求解/步长资格，再继续闭环”。eb2600a首门失败及385d08d数学风险不覆盖。v1原字节保留；v2仅改变plant积分/授权/来源元数据，接触几何、式9–12/16/19–21/25、观测/控制clock、原判据/预算不变。Eq18滤波Euler预测未获变更批准。先按[P2隐式资格声明](../reports/P2_IMPLICIT_QUALIFICATION_SPEC.md)执行N/D，再组件E/C及原exp3粗/半步；失败留证停门，不自动P3/Isaac/P4/RSS。小修累计1/3余2；此次用户科学数值路线批准单独登记，不重开预算。当前新实现尚未运行科学资格、正式控制0。

新数值路线获明确授权；不把plant隐式批准扩展到observer式18。


## D070 — 2026-10-14：P2第二阶段首门停止，保留数据与数值解释争议

用户第二阶段要求固定资格失败保存并停，重大模型/控制/协议解释需征询。实现9194f9f未改变原几何/force/control，首条5s settle达到120秒限只到3.324s，不能以831样本的接近平衡趋势改判终态门。其后仅作固定数学风险审查385d08d，无补积分/控制/GT。C当前explicit midpoint1/3000的局部快倍率2.730136，改变explicit/implicit或clock需裁决，不自动更换。保全科学失败/全部30未执行账目/中文报告，P2仍部分完成；小修累计1/3余2（本轮无科学修正）。GitHub交付是本次明确授权，不为历史文档的上传审批再问；当前仅数值路线有待批准，不P3/Isaac/P4/RSS。


## D069 — 2026-10-14：接受P2几何资格，授权独立动力学/IESEKF/联合控制第二阶段

用户接受68/68及冻结protocol，明确从834bcc按顺序实施；无需再审模型或重复批准。原力9–12/16及控制19–21/25保持，G用已批准spatial-free Log闭合。原JSON内“execution_authorized_this_round=false”是前阶段历史标记，保留原字节，当前授权单独登记。剩余两轮修正跨阶段累计，主条件不调参；资格或重大模型/控制/协议争议停留证据。包括中文Word、真实图表与GitHub交付；无P4/RSS/Isaac/P3/FR3算法。


## D068 — 2026-10-14：用户批准几何一致接触路线，资格完成后冻结P2协议

用户明确回复允许重新推导几何一致接触模型：保持原位姿/内力控制器、记录差异、有限形变检查后冻结。
采用p2.spatial_free_log_constraint.v1：精确D微分和Ng=Ad(D^-1)N lift，唯一Ac约束解；属于已批[DEVIATION]，不声称作者勘误。
原力9/10/11/12与控制20/21/25/H/W/K/B/KF/KP保留；只替式15抓点演化。原近似阻尼/全稳定性/摩擦释放未验证边界继续明示。
run01原66/66程序PASS保留但交付INCOMPLETE；修正1补signed Eq9日志与2恢复负例，核心模型不变；run02 68/68资格通过。
对模式切换追加新释放方向卸载是零自由Log初态域资格；沿原阈值，不改性能判据，固定时间失守停止、不重锚/等待/加释放控制。
新冻结JSON保留原参数/主seed/时刻/评分和81控制run上限；P2小修总额度已用1/3余2，不重置。后续实际控制最大30+2×7+30=74。
本轮完成审计、几何资格及协议冻结；完整controller/IESEKF/ODE/真实闭环尚未实现，executable=false。后续实施遵冻结协议，同一已批模型无需再确认。
P4科学源/数据/失败/Word及旧P2工作树保存，不新增RSS、不自动P3/Isaac。D067原待裁决停点已解除，其历史文件不覆盖。

## D067 — 2026-10-13：P4阶段性审查接受，授权独立P2审计，重大接触模型争议停止

用户接受P4@79cc871阶段性报告，认可三法真实实验；PCS/NR20/20、RSS无全局路径、PCS换链路径优势未充分证实、完整论文部分完成结论保存。
本轮不得修改P4或追加RSS；独立reproduce-p2-paper-audit基于该提交，不覆盖旧P2未提交资产。
当前只完成P2全文/公式/作者资源与实验前协议；允许有依据的最小原文式模型，不强制FR3/吸盘/Cube/车厢/Isaac，不自动P3。
表I/II与原物块A直接采用；exp2按正文KP=0保留前馈，exp4采用model K失配、trueplant名义K。软接触plant、真实状态、hK观测、IESEKF估计和控制需独立记录。
式15正号与自由方向零形变有关键冲突，式22有限微分有理论疑点。原式/诊断保存；不给负号或几何一致候选默认授权。
用户“重大算法假设或实验模型存在争议时停止请示”现已触发；协议标DRAFT/executable=false，接触variant=null。先完成可审查审计和协议，再请用户裁决。
后续三轮小幅修正预算本轮0/3；固定模型/判据不能为逼近原图1.5N或80%而变更。正式Word实验部分待真实数据。
此决定覆盖D066历史不得P2门禁，不覆盖P4原失败/旧科研结果，也不授权P3或旧场景运行。

## D066 — 2026-10-13：保全P4三方法既有成果，真实部分完成交付后停止

本次明确用户任务授权在原文和条件可确定时继续实现/实验，并上传GitHub后等审查。
发现既有独立分支和协议6d64b26、实现2ab2348、三轮修正41689ef/17202df/3d51ca0；
不重新创建同名分支或重置进度，保全131个未提交文件至219a8a7。
统一20R原环境I同类重建可按已声明协议核验，不擅改为FR3、原空间几何或更容易端点。
原文/原输入/软件差异详见补充审计；这一决定不改变冻结协议、阈值、种子或原历史结论。
当前已有60次真实统计与3重复；科学修正上限3/3用满，不重复预算或继续第四次调整。
数据/报告交付可完成，但RSS无全局解、完整重复未过、原六环境/m比较未覆盖，因此科学状态部分完成。
报告排版修订仅调整图9图例/页脚，另存正式Word/PDF，不计作新的科学算法修正。
全量原始失败、被保护旧NR/FR3来源和原报告继续保留。独立数据核验不新增规划实验。
本次授权已明确要求GitHub完整提交，因此完成核验后直接推送任务分支；上传后停止等审查，不自动P2或Isaac。

## D065 — 2026-10-13：P4需实测RSS/PCS/NR三种方法，报告以本人汇报口吻

用户要求纠正两处：一是导师报告不得使用“编写目的”等编写说明，应以第一人称直接介绍论文模型、算法与真实复现数据，应用现有FR3/Cube车厢的差距仅放最后一章；二是P4原文三策略RSS、PCS和NR都需要实际复现、统一实验并产生真实对比图表，不能只做NR+把原文表格移植到报告。对于作者代码不完整/只有伪代码的论文，允许最多三轮有据可查的小改修复尝试；仍达不到论文指标就如实报告所得到的数据及差距，不事后放宽门限或选择性报告。

新专项见 `docs/tasks/P4_THREE_METHOD_COMPARISON.md`。此前D064仅更新叙事结构，本次进一步授权从论文完整方法出发做三法实验方案，不授权场景/模型擅改、Isaac/ROS/机器人执行；已有NR、FR3历史结论及失败证据仍保留。新三方法实验必须先审核模型可行性、预声明可比条件和预算，用户审查关键科学假设后再进行。


## D064 — 用户要求先忠实复现五篇论文，不强制匹配现有工程场景

日期：2026-10-13。用户明确表述：目前以复现原论文算法为主，五篇都复现后再考虑小改；当前Codex明显过度围绕自己的FR3/Isaac场景展开，需更正。报告前面应围绕原论文算法或控制器，应用当前场景的差距及问题**最后新开一章**。

处理：当前P4→P2→P3→P5→P1，优先作者原算法、系统/实验条件与能生成真实图表的最小实验；无强制FR3/车厢/Isaac匹配验收。旧D055场景应用目标仍保留为五篇结束后的后续阶段，但原“逐篇必须先Isaac才能进下篇”门禁不适用当前阶段。P4原报告02f9346保留；单独按 `docs/tasks/P4_REPORT_REFOCUS.md` 更新报告叙事与新增应用差距末章。

本次仅调整规划和报告标准，不授权新P4科学实验、规划优化、实际机器人/Isaac/ROS运行、不修改原算法/数据/Benchmark、不自动启动P2。旧精度FAIL、TASK06整体部分完成、TASK06-IS-A离线初步通过及B0执行资格不足全部保留。


## D063 — 2026-10-12：P4报告只整理已有证据，交付后停止审查

用户指定最新规划 e32d19d、独立工作分支、六份本地资料核对及全文阅读，输出中文Word。
遵循D062报告优先路线，实际只读存量，所有原数学/规划/物理资格与失败不改判。
报告按DEFORM两部分解释RSS/PCS/NR、FR3适配公式、NR/RBS/双树及真实日志；
把12/14/18/20维模型、PQP/FCL、500次平均与小样本/单次差异明确列出，拒绝性能优势外推。
NR-only报告完成不意味着RSS/PCS、奇异通道、原三法比较或Isaac物理执行已完成。
私有PDF/范例不上云；只上传原创报告、图表、派生数据/来源hash及报告层脚本。
本项仅记录代理交付与用户既有授权，不冒充用户已接受报告；后续P2→P3→P5→P1
每篇仍需先审查上一份报告、全文依据与独立真实实验授权。Benchmark不冻结。
[任务前](../reports/P4_REPORT_PRE_TASK.md) · [交付](../reports/P4_REPORT_POST_TASK.md)。

## D062 — 2026-10-12：论文原文核实与“论文复现报告优先”路线更新

用户说明导师催促五篇论文算法复现，并指定用户上传的18页DEFORM Word复现汇总为报告格式。**当前优先级调整**为“P4 已有核心结果先整理中文科研报告 → P2 → P3 → P5 → P1”，每篇以论文全文的算法与公式、最小可复现实验、原始曲线、与原文对照和完整中文Word报告为交付，报告审查之后再启动下一篇。完成五篇阶段成果后再提小改并集中应用到 Isaac Sim 双FR3场景。

D055“最终五种方法都要用到已有场景”的长期目标仍有效，**但逐篇立即进入Isaac的执行顺序暂缓**。TASK06-IS-B1路径优化、TASK06-IS-B/C、TASK02-D、正式Benchmark及 P2 大规模控制运行均未因本次文档修改自动授权。原TASK03旧抓取精度未通过、TASK06完整协议部分完成、A离线验收和B0执行不满足均保留不改。

在公开仓库只提交完整原文索引/DOI/作者手稿/原始PDF的个人本地文件校验值、DEFORM报告结构提炼及Codex执行顺序。用户的五份论文 PDF 和DEFORM示例 DOCX 属于需核对公开转载许可的资料，不未经授权上传到公开 GitHub。用户可在本地工作树 `references/private_sources/` 放置私有副本，`.gitignore` 忽略该目录。Codex 必须读全文，没有文件须从合法来源核对或请求用户提供，不可把参考卡当原文。见 `references/ORIGINAL_PAPERS.md`、`docs/PAPER_FIRST_REPRODUCTION_ORDER.md`、`docs/PAPER_REPRODUCTION_REPORT_FORMAT.md`。


## D061 — B0 审查结果：保留原合格离线路径，拒绝自动升级执行

2026-10-12，代理结果，不是用户新物理授权。D060协议c20c381、源码e1a2e22。
左J4最小余量index860=.004119663rad/.236039°；旧接受终点误差.035/.06rad
不能当全程误差认证；缺动态包络、原生加速度/共同赋时、实际持件START对齐。
结论仅“执行准备条件不满足”，不推翻A离线初步验收或修改原P4阈值/成功结果。
25artifact/620source/1869点/94边资格核验一致；7合成测试和图表仅审查证据。
后续独立路径改进可研究原TASK05验证的约束捷径/执行余量筛选，但须另行预声明
并标工程后处理，不回写原路径/算法/Benchmark；本轮未重规划/改进/赋时/物理运行。
提交后停止，B/C/TASK07未授权；原TASK06整体部分完成、Benchmark草案。
[审查与POST-TASK REPORT](../reports/TASK06_IS_B0_PRE_EXECUTION_REVIEW.md)。

## D060 — 用户接受 A 离线适配，只批准 B0 固定路径执行前审查

2026-10-12，基线 f0a57c2、原 A 分支。接受 A 无执行规划适配初步验收，
尚不批准 1869 点路径下发 Isaac：约 .236° 最小余量须独立审查。
新授权仅一次只读离线分析、旧执行能力取证和时间参数化资格研究；不重规划、
不改原路径/模型/场景/ACM/门限/端点/旧结果/Benchmark，不启动 Isaac/ROS/命令。
先登记逐点余量、累计行程、连续性/反向规则，复核原资格来源并输出曲线。
旧跟踪容差不能冒充瞬时误差上界；无时间路径不能凭计算耗时称运动时长。
交付只报告执行准备条件满足/不满足，独立改进建议不自动实施，上传后停止。
[任务前与复用协议](../reports/TASK06_IS_B0_PRE_TASK_PROTOCOL.md)。

## D059 — TASK06-IS-A 第二阶段交付：仅同源名义离线适配初步通过，等待审查

2026-10-12；本项记录代理结果，**不是用户新审查决定或Benchmark冻结**。
D058协议20fe06d、测试c88a80c；原输入/算法/模型/碰撞许可/结果不改。
采用预声明Task26 .628m六对象world及名义持件阶段(.500,0,.540)→(.790,.060,.280)，
各候选0由现成KDL/原NR得到完整14q并通过独立pose/closure/limits/FCL。
唯一seed7真实P4双树成功，96nodes/94edges/1869离散点，独立原FCL复核通过。
run02启动环境错误原ABORTED保留；一次命令级修正后才进入唯一科学进程，非事后改标准。
结论只允许“无执行规划适配初步验收通过”，不替代真实持件测量、动态执行或正式科研基准。
成功即停，剩余候选/seed不再启用，不自动B/C/TASK07；原TASK06整体部分完成，
TASK02-D暂缓、Benchmark草案未定稿。所有旧负面证据和协议状态保持。
[POST-TASK REPORT](../reports/TASK06_IS_A_NOMINAL_SCENE02.md)。

## D058 — 用户接受A第一阶段软件范围，批准独立Task26世界与名义端点路线

2026-10-12，基线7bae83a，整体A仍部分完成。另行批准一次有界离线补证：
采用Task26真实0.628m车厢为新v2输入，不覆盖0.606m历史归档/原失败协议。
START共同抬起(.500,0,.540)，GOAL共同短推释放前(.790,.060,.280)，明确名义而非实测。
无完整历史构型时可用已有运动学有界构造；原C/Jc/NR/RBS/FCL/P4算法门限不变。
预声明保留第二供料Cube02作固定障碍、休眠后批不入world；禁止按结果改障碍。
直接KDL-LMA后端不启动ROS；候选/种子/预算和单次实验在新协议登记。
禁止Isaac/ROS规划服务/命令/旧Task26或Benchmark改动/B/C/TASK07；交付后停止。
[任务前协议与复用审查](../reports/TASK06_IS_A_STAGE2_PRE_TASK_PROTOCOL.md)。

## D057 — TASK06-IS-A 输入不一致即停止，不用编译通过代替场景规划通过

2026-10-12，落实D056的预声明停止条件，不推定新的用户验收或输入授权。
固定source run确认Task26的628mm车厢与P4历史606mm世界不是同一环境；
共同持件实际端点也没有完整证据。保留ABORTED，不改旧world、抓取或数值标准。
单独软件编译/合成回归只证明接口组织可构建、缺失输入能拒绝，不能填补路径证据。
TASK06-IS-A部分完成；P4原核心软件和原整体分项状态不变。
仅在新适配输入引用原Task26世界与明确A端点定义是后续审查建议，本轮未执行。
需要实时持件状态时另行申请最小采集，不启动GUI/ROS或重写成熟执行器。
本轮不冻结基准、无B/C/TASK07，交付后停止。
[交付报告](../reports/TASK06_IS_A_SCENE_ADAPTER01.md)。

## D056 — TASK06-IS-A：先核对现有场景，未确认端点不启动搜索

2026-10-12，用户授权从 eb858651 的规划分支建立独立 A 分支；仅静态/离线。
复用原 TASK03–06、TASK02 和固定旧 Task26@631b1f + 5ed0c96 工程资产。
不得启动 Isaac/ROS/命令、新 IK 或用不匹配历史 q 替代实际 START/PRE_PUSH。
旧两件验收不改写成正式单 Cube 通过；名义预推、短推高位、落桌终点分开。
原起终点实际持件 14q 尚未保存/确认，端点缺失时只提交映射与拒绝证据。
一轮固定来源/模型/接口离线检查；原 NR/RBS/搜索参数与 Benchmark 不改。
条件规划参数仅登记，端点 null 时种子预算不启用。提交后等待用户输入路线审查。
[任务前与复用审查](../reports/TASK06_IS_A_PRE_TASK_AUDIT.md)。

## D055 — 用户决定：五篇论文必须逐篇落到现有 Isaac Sim 科研场景

2026-10-12。用户确认“要将这 5 篇论文中的创新方法用到我们的场景中”，并认可“场景适配/无命令验证→Isaac 运动执行→实验对比”三步，要求据此改路线。此前“完成 P4 离线软件直接进入 P2”的建议被撤回。

决策：P4 TASK03–06 的离线基础之后新增 TASK06-IS-A、B、C，先完成与已有双 FR3+侧吸+Cube+车厢场景的适配与规划，再在单独用户授权下执行和对比。其余 P2/P3/P5/P1 也必须完成相应的 Isaac 应用验证和阶段性对比后再申请下篇启动；允许独立记录部分完成/暂缓，而不把离线通过当论文整体完成。

本轮仅修改规划/治理/任务卡，**不启动仿真、服务或算法实验**；随后交给 Codex 的指令只授权 TASK06-IS-A 的离线场景核查和无运动命令适配，若需实时 GUI 或 ROS 须停下另行请示。B/C、P2 TASK07、P4 独立障碍补测均没有获得执行许可。

既有 D052/D054 的 TASK06 原预声明 FAIL/整体部分完成不变，TASK02-D 继续暂缓，Benchmark 尚未定稿。旧 Task26 工程成熟部件优先薄适配而非重写；五篇方法属于论文/场景适配，不得将工程复用伪称论文原方法。

[完整路线](REPRODUCTION_ROADMAP.md) · [阶段 A 任务卡](tasks/TASK06_IS_A_SCENE_PLANNING_ADAPTER.md)。


## D054 — User accepts TASK06 core software candidate; overall protocol remains PARTIAL

2026-10-12, explicit review of `74d4276` on `task06-p4-constrained-rrtconnect`.
**Core offline planner software implementation = PASS CANDIDATE.**
**Overall TASK06 = PARTIAL.** These are separate acceptance scopes; this is not
retroactive PASS of D052 or relaxation of any numerical/algorithmic condition.

Retain all18fixed-seed calls,9deterministic repeat pairs,4NODE_LIMIT results and
both553-node/148-solution-edge obstacle successes. Direct TASK05 connection stays
PROJECTION_JUMP; collision=null at the rejected midpoint, with no FCL query there.
All original results/statuses/metrics/guards and TASK03–05 negatives remain unchanged.
The missing direct-COLLISION qualification becomes a **separate pending P4 evaluation**;
it neither invalidates the accepted software scope nor completes the original protocol.
No authority to implement/run that evaluation, modify code/scene/ACM/model/Benchmark
or start TASK07. This round is documentation only; stop after GitHub submission.
[Scoped review record](../reports/TASK06_REVIEW_CLOSEOUT.md).

## D053 — Retain fixed TASK06 acceptance failure; deliver PARTIAL and stop

2026-10-12. Solepredeclaredsuite source29a9d5c: genuine two-tree NR/RBS/FCL search,
fixedseedrepeats/native negatives pass; obstacle20261012twicefinds148-edgepath.
However directTASK05obstacleedge first fails projectionlocalityguard, notcollision.
KeepD052protocol/fixture/guards/seeds/budgets immutable and thisFAIL visible.
Noagentadjustmentofacceptancescope/tolerance afterresults;TASK06PARTIAL, notPASS.
Onecompile-onlyfix doesnotauthorize empiricalretuning. Existingcompleteevidence
is sufficient for review; stopscientificwork afterGitHubdelivery. Anynewvalidation
case or scopedacceptance requires explicit userdecision, notautomaticTASK07.
No oldTask26/model/ACM/Benchmark change; oldTASK03precisionFAIL preserved;
TASK02IN_PROGRESS/DDEFERRED, BenchmarkDRAFT. Thisrecord is agentdelivery policy,
not useracceptanceor formalBenchmarkfreeze.
[POST-TASK REPORT](../reports/TASK06_CONSTRAINED_RRTCONNECT01.md).

## D052 — Predeclare TASK06 constrained search and fixed offline suite

2026-10-12, baseline91a1adc. User accepts TASK05 only real-FR3/FCL discrete local
connections. Source audit pins CKCplanning909bd72, preserves repeated101/501 grow,
ambient uniform NN→steer→NR→RBS and exact final tree connection. Reuse accepted
TASK02–05 without alternate FK/projection/FCL/ACM. Full native14D sampling with
real mt19937_64 seeds7/41/20261012, two repeats; simple0→1 and nontrivial0→100;
private fixed midpoint BOX only independent test scene. All choices and limits
committed before planning runs, no outcome tuning. Conservative inherited rank/
RBS guards disclosed; no singularity/performance or full P4 reproduction claim.
No Isaac/ROSservices/Task26/TASK07/Benchmark edits; parentTASK02IN_PROGRESS,
DDEFERRED, BenchmarkDRAFT. [PRE-TASK/protocol](../reports/TASK06_PRE_TASK_PROTOCOL.md).

## D051 — TASK05 discrete evidence sufficient; stop before TASK06

2026-10-09. D050 predeclared RBS guards unchanged. NativeFCL/30shapes/16meshes
and unchanged privateACM coverrobotself/interarm/robotworld/carriedCubeworld; no
old filtering, newtouchlink or depthexception.10fixedrealpositiveconnections pass,
3negatives reject including genuine world/tool/attachedCube penetration; fulltrace
andorderedprefix retained. Nativebound/closure failure doesnot repaircallerendpoint.
300syntheticchecks exerciseprojection/jump/continuity/budgets/failureinterfaces,
not a substitute for actualFCL. Two software passes, one logging-onlyfix, identicalq.
Minimum sufficient evidence reached for **OFFLINE DISCRETE LOCAL CONNECTION ONLY**;
no continuous safety/branch/PhysX/suction/time-trajectory/full P4 claim. TASK05
PASSCANDIDATE for userreview, not accepted/frozen automatically. No TASK06 or runtime
authorization inferred. TASK02-D DEFERRED, parentTASK02IN_PROGRESS, BenchmarkDRAFT.
[Report](../reports/TASK05_LOCAL_CONNECTION01.md).

## D050 — TASK04 reviewed; predeclare TASK05 offline RBS protocol

2026-10-09, explicit user acceptance of TASK04 PASS CANDIDATE (OFFLINE PROJECTION
MATHEMATICS ONLY), base5d41869. One bounded TASK05 offline slice, no Isaac/services/
controller/Task26/TASK06/Benchmark edits. Original TASK03 precision FAIL retained.
[ORIGINAL] P4 II-C RBS: project midpoint, validate, recursively connect subsegments.
[ADAPTATION] unchanged 14q FR3 C/Jc/NR and private native MoveIt/FCL.
[ENGINEERING] pre-experiment separate1e-8m/rad and unchanged TASK04 options;
leaf/adjacentL2 .01rad, adjacentLinf .01rad, midpointcorrectionL2 .02rad,
depth12/projections1023/points1025. Original SRDF ACM, no new touch-link allowance,
no padding/model/threshold changes. Ten fixed positive connections and genuine
FCL box-at-TCP negative fixture declared before tests. Discrete point evidence
only, not continuous safety/full paper or physical grasp. Missing scene => PARTIAL,
no replacement collision engine. TASK02-D DEFERRED, Benchmark DRAFT.
[Full PRE-TASK/prior-asset/protocol](../reports/TASK05_PRE_TASK_PROTOCOL.md).

## D049 — TASK04 bounded projection evidence; separate mathematical/physical claims

2026-10-09. [ORIGINAL] P4 Newton pseudoinverse; [ADAPTATION] unchanged TASK03
dual-FR3 C/Jc/FK; [ENGINEERING] Eigen SVD, full-step guards and precommitted D048
protocol. Independent source/math review finds no blocking defect. Exactly 487
real-model calls: required194/194 converge in0/2/3updates, repeatq identical;
original-grasp293/293 inone. Offline regressions/nativebounds/hashes pass, no tuning.
Original TASK03 0.05-micrometre FAIL stays FAIL; projected q never replace archived q.
Low-rank corrections unqualified, not claimed impossible under P4. Fixed SI units,
no scale-invariance/global/collision/physical/path/RRTConnect/full-paper claim.
Only TASK04 PASS CANDIDATE (OFFLINE MATHEMATICS ONLY). TASK02 IN_PROGRESS;
Benchmark DRAFT/NOT FROZEN. Build/runner negatives retained; stop after GitHub
delivery, no TASK05/06. [Report](../reports/TASK04_NR_PROJECTION01.md).

## D047 — TASK03 review accepts offline mathematics, preserves historical precision FAIL

2026-10-09, explicit user review of91422f4. **TASK03 mathematical implementation =
PASS CANDIDATE (OFFLINE MATHEMATICS ONLY)**: real-FR3 finite-difference Jacobian
validation passes. **Historical configuration precision = FAIL**: original293records
max position closure0.435028μm exceeds unchanged0.05μm;219records exceed the limit.
Keep original data, grasps, robot/model, source/tests and result status fields unchanged.
This is an approved classification of acceptance scopes, **not** tolerance relaxation
or retroactive conversion of the failed original diagnostic into PASS.
Full P4 reproduction remains incomplete: no projection/path connection/RRTConnect
conclusion in TASK03 evidence. Later TASK04 evidence is a separate software slice.
The prior D046/PARTIAL delivery remains accurate historical evidence, superseded only
for reviewed mathematical acceptance. No scientific Benchmark freeze.

## D048 — TASK04 predeclared offline full-step SVD projection protocol [ENGINEERING]

2026-10-09, before projection experiments. Implement qnext=q−Jc†C using existing
TASK03 C/Jc/FK. No damping, line search, row weighting, clamp, active-set, alternate
IK or grasp fit. Fixed chart uses SI m/rad; independent convergence does not make
the numerical pseudoinverse invariant to arbitrary unit scaling.

Engineering test standard: position norm≤1e-8m **and** rotation norm≤1e-8rad;
max40 accepted full Newton updates, with final evaluation after the40th. Eigen
JacobiSVD, cutoff=max(1e-12,1e-10σmax), singular values≤cutoff truncated.
When correction is required and rank<6, explicitly reject as unqualified local
projection; this conservative policy is **not required by P4** and does not reproduce
the paper's general singular-configuration behavior. Already-converged states may
return zero-update success. Candidate must be finite and inside original native
URDF bounds, otherwise reject/no clamp; preserve last accepted q and rejected proposal.
Step≤1e-14rad without convergence is numerical stagnation, not success.

Finite deterministic suite: once-fixed algebraic START grasp G*, one zero sample,
84single-joint samples (14×2signs×magnitudes.001/.01/.03rad),12coupled samples
(4 deterministic directions×3 magnitudes) =97, repeat twice. Output-q repeat
maxelement difference≤1e-12rad. Independent diagnostic: all293 archived originalq
with unchanged originalG, once; projected q goes only into new TASK04 result files.
No empirical tuning after results. Wallcompute time only, no simulation timestamp.
Config: `configs/engineering/task04_projection_test_v1.json`. Synthetic failure
tests exercise intentional alternate options, not new empirical acceptance thresholds.
No TASK05/06, simulator, services, old Task26 or Benchmark changes. If evidence fails,
report PARTIAL; do not silently expand method or acceptance.

## D046 — Explicit rigid closure chart; immutable existing FK; no acceptance fitting

2026-10-09. [ORIGINAL] P4 generic rigid-chain C(q)=0 framework, joint/collision
validity separate. [ADAPTATION] dualFR3 predicts Object with explicit TCP→Object G,
position left−right in world and Log(RR^T RL) in right predicted Object axes.
Jacobian accounts for fixed-grasp lever arms and SO3 differential. [ENGINEERING]
reuse MoveIt2.5.9 RobotState FK/Jacobian, rotate first-joint-parent geometric axes to
world, validate by independent FK differences; no new DH chain, planner or projection.
Exact expanded archived URDF/SRDF snapshots make tests portable without geometry
or ACM changes; license/source identity retained. Old Task26 and Benchmark untouched.

**Do not freeze or silently change offline acceptance:** original historic G/q
position closure0.435μm exceeds previously declared0.05μm. Keep this negative result
and TASK03 PARTIAL, even though math/Jacobian software PASS. The engineering precision
is not a formal Benchmark threshold. A one-time algebraic G*=FK(q0)^-1O fixture
is classified mathematical/test-only, fixed for every subsequent perturbation;
never feed it to benchmark/control/SG or use it to claim original grasp acceptance.
No new IK or tolerance iteration. User review required before changing acceptance
policy; no automatic TASK04/physical experiment. [Formula/source/evidence](../reports/TASK03_CLOSURE_CONSTRAINT01.md).

## D045 — Defer native Isaac sampling qualification; unblock offline math [ENGINEERING]

2026-10-09. Explicit userapproval endsTASK02-D availabilityaudit. InstalledIsaac4.5 supports
directPhysXpost-step, nativeq/rigid/link/CoreNodes time/count; not complete same-step/source/reset
attestation. Do notimplementObserver or relabeloldUSD/ROSsamples. TASK02-DPARTIAL/DEFERRED,
parentIN_PROGRESS, BenchmarkDRAFT. LaterformalIsaacmeasurementadapter owns theseissues;
P4offlinekinematics/planning doesnotdependonthem. Noengineeringscopecontinuation or TASK04
authorization inferred. [Evidence](../reports/TASK02_POST_STEP_API_AUDIT.md).

## D044 — TASK02-C reuses initial-drift math; measurement eligibility is not success [ENGINEERING]

2026-10-09. User approves one offline slice on task02-minimal-foundation-interface fromc7b33b1; no runtime, old engineering/physics/YAML/A/B semantic edits or automatic next task. Preserve pinned Task14 relativeTCP and object-midpoint world-vector drift against first valid sample, sign-invariant orientation angle and equally weighted max/RMS. Explicit target-position RMSE and B nominal-axis/target math are basic contract extensions, not paper algorithms. Old3mm/5mm/2deg/30ms thresholds stay historical; timestamp-skew policy must be explicitly supplied and is not a success criterion. Same session/SIMULATION/native-declared post-step qualification is required for formal metrics; synthetic mode yields no real duration. Whole-input frame/session/domain/qualification/reversal failures cannot be hidden by dropping rows; row-level missing/invalid/duplicate/skew failures preserve counts and reasons. Formal insertion duration is only a caller-delimited qualified endpoint window, not target-arrival detection; unavailable endpoint does not borrow another sample. Wrench torque is about explicit application point in sameframe; distance uses declared signed/witness conventions. No data schema provides native attestation. Two mock adapters and all72regressions provide software minimum evidence, not simulator equivalence. TASK02-C PASS CANDIDATE, TASK02 IN_PROGRESS, BENCHMARK DRAFT/NOT FROZEN; stop for user review, no TASK02-D/TASK03. [POST-TASK REPORT](../reports/TASK02_METRICS_MEASUREMENTS01.md).

## D043 — TASK02-B commands are data; confirmation is evidence-backed, not execution [ENGINEERING]

2026-10-09. User explicitly approves exactly one bounded offline command/event/result/logger implementation and prohibits Isaac/ROS/MoveIt, mature runtime changes and TASK03. Preserve predecessor631b1f SUCTION_ON/ATTACH/SUCTION_OFF/DETACH names and trajectory-relative TaskStageMarker semantics through a thin planned-only adapter. Add explicit PLANNED/OBSERVED/CONFIRMED/FAILED statuses; observed/confirmed use explicit post-step sim clock/session, while plans use trajectory clock/ID. Confirmation must reference prior matching observation/object/link/command/attachment, never derive attachment from a suction command or CLOSED alone. Data interfaces and logger do not send commands or replace Task26. Result statuses and measurement qualification are independent, scoped declarations, not frozen scientific scoring. Use deterministic standard-library JSON/JSONL with exclusive run directories and explicit argv/config paths/sources/seed SET or UNSET; no DB/services. Seed records do not seed OMPL/Isaac/RNG. Existing historical state cannot become synchronized scientific evidence; nonempty qualified states are required for the logger's synchronized result label. PASS CANDIDATE applies only to TASK02-B offline contract acceptance; parent TASK02 remains IN_PROGRESS, scientific Benchmark DRAFT. [Evidence and POST-TASK REPORT](../reports/TASK02_EXCHANGE_LOGGING01.md).

## D042 — Accept engineering foundation; minimal in-place unified interface first [ENGINEERING]

2026-10-09. Explicit user accepts TASK01 foundation feasibility PASS CANDIDATE and says formal scientific Benchmark must not be frozen. Close repeated qualification/redevelopment of mature grasp/regrasp/push; retain first physical negative and authorized5ed0c96 source exception. Interpret follow-up “继续” as minimum migration/common contracts, not physics/safety/model edits. Prefer accepted predecessor source in place through a read-only thin adapter before any source copy; preserve original scene/Play/bridge/MoveIt/controller lifecycle. TASK02-A standard-library contracts expose SI/xyzw/frame/source/joint identities, unavailable science fields and diagnostic clocks; local hash guard verifies only its4declared assets. Do not infer simulation step from timeline, world_shift from rail, native attachment from SG CLOSED, or measured collision/force from absent data. Draft interfaceversion is not a Benchmark freeze. Command/result/metrics/logger/livepost-step binding remain later slices; paper algorithms still must be new/paper-derived. No new runtime authorization or historical threshold import. [Plan and evidence](../reports/TASK02_FOUNDATION_INTERFACE01.md).

## D041 follow-up — Stop after full patched-predecessor success, candidate only [ENGINEERING]

2026-10-09. Usermax3runtimepermissionproducedFAILthenfullPASSin2invocations. Minimumfoundationengineeringevidence achieved bysecondactualtwoCube+HOMEexit0, so stop withoutthird; notseek3successes or perfectdiagnostics. LabelFOUNDATIONcandidateWITH_AUTHORIZED_SOFTWARE_FIXES, not byte-identical631b1f; preservefirstphysicaljointsettlefailure andlimitedoriginalmeasurement/FCLsupportsemantics. TASK01PASSCANDIDATEreview, notFROZEN, noautomaticport/TASK02/benchmarkedit. Force/clockresearchrequirements notsilentlypromotedintothislegacyqualification. Usermustreviewfoundationuse/reusepath. [Result](../reports/TASK01_PREDECESSOR_PATCHED_RUNTIME_REVIEW.md).


## D041 follow-up — User renews bounded GUI physical acceptance, maximum3 [ENGINEERING]

2026-10-09. User explicitly authorizes “继续物理验收，如果三次尝试都失败再反馈给我”. Run approved predecessor5ed0c96 software fix using existing visible GUI and original Task26 batch1 two-Cube assets/lifecycle. Up to3 fresh acceptance attempts, stop first success; unchanged safely rejected planning may retry, hard physical/state/native failure stops immediately. No additional fix, geometry/physics/ACM/gate change, standalone or foundation freeze. Original bridge shutdown before Stop/rebuild; GUI executor may perform Play/reset for this new runtime authorization. Preflight600s/physical1200s engineering caps per attempt. [Pre-run scope](../reports/TASK01_PREDECESSOR_PATCHED_RUNTIME_REVIEW.md).


## D041 follow-up — Explicit two-change software exception, not a new physical allowance [ENGINEERING]

2026-10-09. User “可以” approves preceding evidence-based proposal only: materialize FK translation before localRobotState destruction, and enable existingTask27 rear→samePUSHendpoint→side-chain selector forTask26. This is a narrow explicit exception to original no-source-patch qualification rule, recorded as modified predecessor5ed0c96; do not call it byte-identical631b1f or silently replace previous failure. No entireTASK27 macro/layout/tolerances, geometry/physics/ACM/parameters or controller rewrite. One software correction/build-check cycle; original preflight/physical1/1 remain consumed and no new runtime/reset inferred. New qualified foundation label must disclose authorizedsoftwarefixes if later tested; currentPARTIAL/notqualified/notFROZEN. First substantive software failure stops, no fallback implementation. [Plan/evidence](../reports/TASK01_PREDECESSOR_SIDE_PREFLIGHT_FIX.md).

## D041 follow-up — Stop at original side-compaction rejection; no foundation qualification [ENGINEERING]

2026-10-09. Original predecessor batch1 qualification was invoked once after original planning-only PASS; physical failure at first Cube's side-compaction FK gate stops the task. Completed transport/rail/regrasp/push prefix and historical predecessor PASS cannot substitute for the missing final side seat/second Cube/retreat. Record TASK01PARTIAL/FOUNDATIONNOT_QUALIFIED, preserve original source and acceptance, save negative evidence. Pausing the operator GUI and interrupting owned ROS processes does not authorize reset/HOME or retry. No new probe, second candidate station, geometry/ACM change, porting or FROZEN. If continuing, request separately bounded existing-evidence kinematics diagnosis before any implementation or new physical trial; root cause not presumed. [Review](../reports/TASK01_PREDECESSOR_FOUNDATION_RUNTIME01.md).

## D041 follow-up — User accepts original two-Cube batch, no selector patch [ENGINEERING]

2026-10-09. User explicitly says “两件cube也可以，请你继续”. Qualify pinned predecessor Task26's native batch1 (`task26_r0_deep` then `task26_r0_shallow`) with `max_batches=1`, without any selector/count/loop or runtime source edit. Original scene retains four Prim rigid bodies, only the first two active; no second batch request. All D041 original lifecycle/mature-engineering preservation, first substantive failure stop, one preflight/one physical invocation and no FROZEN/port-before-qualification rules remain. Active candidate label is `PREDECESSOR_TASK26_BATCH1_TWO_CUBES`, not a false single-Cube result. [Pre-run full source audit](../reports/TASK01_PREDECESSOR_FOUNDATION_AUDIT.md).

## D041 — Restart TASK01: qualify predecessor Task26 as the foundation scene [ENGINEERING]

2026-10-09, explicit user decision.

The previous TASK01 approach is superseded as the active execution strategy. Rather than rebuilding a parallel single-Cube Isaac stack, TASK01 must first run the predecessor Task26 implementation itself and determine whether it can serve as the foundation scene.

Pinned predecessor: dreamerToTOE/dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a.

Qualification target: exactly one independent Task26 Cube, task26_r0_deep.

Allowed modification before qualification: only a minimal one-Cube selector/count/loop adaptation if the old source has no exact single-Cube mode. No geometry, physics, tool, Surface Gripper, rail, MoveIt, planning, FCL, push, wall-seat or retreat behavior may be redesigned.

A successful full predecessor one-Cube run yields FOUNDATION_SCENE = PREDECESSOR_TASK26_SINGLE_CUBE / PASS CANDIDATE. Benchmark freeze and porting decisions occur only afterward.

## D039 follow-up — Capture is the stopping point, not stable reset certification [ENGINEERING]

2026-10-09. Fulfilled sole approved existing-GUI attempt with unchanged bbe9784 source: operatorPlay, savedsharedPRE, originalrelease/safe/FCL/dualrail/freshcomposedworld/rearregrasp, actualcandidate8967. Record **INSERT_READY ESTABLISHED_CANDIDATE / TASK01 PARTIAL**, notPASS/FROZEN. No benchmark/station/algorithm/SG/ACM/physics edits; noTARGET/reset. Preserve generation2 refresh-time pose versus later candidate drift and actualrailarrivedflags rather than redefining gates. NativeD6handle/anchor unavailable and nonzero capturevelocity constrainclaim to observedcandidate, notstablehold/reset. OriginalcleanupopensSG/pausesGUI; MoveItshutdown−11 afterdriver0 isDEFERRED here andreported separately, not concealed ascleanPASS or triggernewdebugging. Minimum sufficient candidateevidence obtained; budget1/1consumed; stopandawaituserreview, no automaticnextacceptance/fix/retry. [Fullreview](../reports/TASK01_EXISTING_GUI_BOUNDED_RUNTIME01.md).

## D040 — TASK02+ prior-engineering reuse is mandatory before new implementation [ENGINEERING]

2026-10-09. User explicitly requested a second cross-repository review so later tasks do not rebuild already completed engineering infrastructure.

Decision:
- `dual-arm-embodied-palletizing@side-suction-palletizing` pinned at `631b1f65656d025c1bb2173e874192f3fe4d355a` is the engineering reuse source for TASK02+;
- every TASK02+ implementation must perform a PRIOR-ASSET CHECK before coding;
- reusable assets are classified as DIRECT_PORT / THIN_ADAPTER / TEST_ORACLE / REFERENCE_ONLY;
- generic trajectory/event contracts, geometry utilities, MoveIt/FCL wrappers, synchronized execution, metrics/logging patterns and planning-sandbox isolation should be adapted instead of independently rewritten;
- paper-specific mathematics/controllers/planners remain new and must retain ORIGINAL/ADAPTATION/DEVIATION traceability;
- historical application schedulers/placement/router logic are not automatically promoted into P1–P5 baselines.

The detailed mapping is `docs/POST_TASK01_REUSE_MAP.md`. TASK01-specific reuse remains separately governed by `docs/PRIOR_PROJECT_REUSE.md`.

## D039 follow-up — One existing-GUI physical attempt; no substitute launch [ENGINEERING]

2026-10-09 explicit user authorization fixes executable source bbe9784 and scene→manualPlay→bridge→external unchanged driver sequence. Stop at first crash/lifecycle/restore/OPEN/drift/FCL/rail/world/contact/regrasp/attachment failure; no repair-and-rerun. End only INSERT_READY candidate, TASK01 PARTIAL; no TARGET/reset/A/force/P3/FROZEN. Keep all geometry/ACM/physics/SG/stations/thresholds unchanged. Missing already-normal GUI is a prerequisite, not authority to start standalone; preflight found none, so physical allowance remains0/1. Same permission may begin after operator provides existing GUI/executor; prior budgets do not reset. [Protocol and preflight](../reports/TASK01_EXISTING_GUI_BOUNDED_RUNTIME01.md).

## D039 follow-up — Existing GUI belongs to operator; reuse Task26 lifecycle [ENGINEERING]

2026-10-09, explicit user request. Current single-Cube scene authors only its named roots in a STOPped existing Stage; operator Play initializes normal physics; a separate bridge editor entry initializes recorded PRE_PUSH state and existing SG/ROS handles, then waits on native pre/post callbacks. Controller remains the unchanged C++ handoff launched in an external ROS terminal. No standalone SimulationApp/new Stage/app.update/manual simulate/automatic Play/app.close. Original harness retained byte-identical as inactive historical route, not silently repaired. No whole legacy scene import or new SG/regrasp/push/controller, no image-core research. D039 benchmark/stations/world refresh/readback/FCL/guards/time semantics are unchanged. Session failure publishes existing halted/error fields with the last real post-step stamp; no timestamp invented. One software adapter iteration, no additional physical attempt or replenished budgets. Ending pause/shutdown opens SG, not stable held READY; TASK01 PARTIAL, no TARGET/reset/FROZEN. [Implementation and limits](../reports/TASK01_EXISTING_GUI_LIFECYCLE_ADAPTER.md).

## D039 follow-up — One pre-control native capture, no implicit repair [ENGINEERING]

2026-10-09. User approved exactly one visibleGUI/GDB180s startup-only invocation, not integration or source repair. Keep original harness/config/binary byte-identical; diagnostic hash+AST125 exit barrier before169PLAY and all controls, independentmaintrace only. Clean GDB environment/native stack without locals/core, SDK paths/preload onlyinferior. FirstSIGSEGV stops; capturedOmniGraph/image/exec/TBB stack and heap-integrity symptom, thenkill/no continue. Native fault evidence is not corrupting root, collision/readbackFAIL, READY or benchmarkPASS. No remainingbudget1/1; furtherfix/capture/integration needsnewboundedauthority. Physics clock absent; do not label diagnostic wall/profile time scientific. Eighthashesunchanged/TASK01PARTIAL/notFROZEN; D039topology/stations/thresholds untouched. [Report](../reports/TASK01_STARTUP_NATIVE_STACK_CAPTURE.md).

## D039 follow-up — Separate native startup evidence from handoff claims [ENGINEERING]

2026-10-08. User approved bounded diagnosis; explicitly performed one existing-evidence-only audit, no live run/fix. Use full Kit positive markers over truncated console for execution boundary: SDK/ROS bridge completed, SG enable requested, then early-stage/asset investigation window. Kernel OmniGraph fault is a concrete correlated module clue, not exact root/stack or benchmark defect; absent buffered prints are not strict execution upper bounds. Apport non-package rejection explains missing core. Publish selected logs/source hashes without unrelated crash/environment data. Stop diagnosis1/1; any native-stack capture, launcher change, repair or handoff retry requires separate authority, no global core/benchmark change. TASK01PARTIAL/notFROZEN. [Report](../reports/TASK01_STARTUP_READONLY_DIAGNOSIS.md).

## D039 follow-up — Interpret “再次尝试” as one unchanged invocation [ENGINEERING]

2026-10-08. Announced interpretation: one new bounded runtime attempt using identical harness/config/binary, output/evidence directories only; no repair or scope expansion. Retain all previous exhausted allowances,180s/reset0/TARGET0 and original stops. Retry02 repeated native startup symptom before runtime state/readback, so no validator/geometry PASS/FAIL claim or fixed-handoff redesign. New1/1 consumed; further blind launch and native-debug implementation are not authorized. Recommend separate bounded startup diagnosis for user decision; benchmark and paper methods unchanged/notFROZEN. [Report](../reports/TASK01_UNCHANGED_RETRY02.md).

## D039 readback follow-up — startup STOP does not redefine handoff [ENGINEERING]

2026-10-08. Source08c34b8 changes only worldshape message-equivalence validation/evidence/puretests/output path, using fixed1e-8m/rad and1e-12dimension limits; benchmark/geometry/tool/ACM/physics/stations/IK/FCL/topology unchanged. Sole additionalruntime1/1 crashes native before anyrefresh or actualstate. Do not interpret as repeatedvalidatorfailure, physicalworldoffset or handoffgeometryfailure. Messagefix is softwarePASS/runtimeUNVERIFIED, noINSERT_READY. Exhaustedallowance means stop/noautomatic native/startup fixes orsecondlaunch. User must decide any separate startup diagnosis budget. No TARGET, helper/station changes, resets, force, parity10 orFROZEN. [Final report](../reports/TASK01_READBACK_NORMALIZATION_RETRY.md).

## D039 readback retry authorization — equivalence, not spatial relaxation [ENGINEERING]

2026-10-08. User grants one additional1/1 only for CollisionObject readback normalization: validate id/worldframe/count/type/dimensions and T_world_object×T_object_shape. Fixedtranslation/rotation1e-8,dimensions1e-12; not benchmark/IK/FCL/collision/success tolerances, no adaptive enlargement. Save full raw sent/readback/object/shape/composedvalues+shift/generation/nativepoststepclock before verdict. Keep fixed.650→.750 helper/rear topology and all geometry/physics/ACM. One visible≤180sretry, reset0/TARGET0; captureactualINSERT_READY thenstopPARTIAL/notFROZEN. Same-root recurrence→ENGINEERING ESCALATION, not thirdvalidator. [Protocol](../reports/TASK01_READBACK_NORMALIZATION_RETRY.md).

## D039 integration follow-up — stop at first world gate, preserve fixed station [ENGINEERING]

2026-10-08. Approvedoneattempt usedat sourceee51470; initialzero-shift tablemessage-readback rejects before safe/rail/rear. .750/.750 remainsapprovedcandidatependingcapture; no .700/.800 orgeometry/ACM/physics/forcechange. Source-level MoveItnormalization explainsguardrisk butwithoutobservedrawobjects cannotclaim confirmedphysicaloffset orfixedworld. Stop/noimplementationrerun; propose futureexplicitallowanceforcomposedobject+shape worldpose verification+rawmessages, nottolerancerelaxation. No TARGET/Bstage/READYrepeat; noFROZEN. Wrapper0doesnotprovePASS; driver1/cleanup−11preserved. [Actualresult](../reports/TASK01_FIXED_HANDOFF_INTEGRATION.md).

## D039 fixed-rail follow-up — user-approved .750 B candidate [ADAPTATION]

2026-10-08. Both A/PRE rails/rest remain .650m; INSERT_READY candidate .750/.750m and world_shift_x=+.100m are fixed common engineering handoff, not P3 tuning variables. Require bilateral OPEN confirmation, old safe helper/pusher state, measured rail/base consistency and complete world rebuild/ACK after move. Capture fullpoststep14q/base/rail/Cube/TCP/leftOPEN/rightrearCLOSED/relativeattachment/helperpark/carriage/time/step, not14q alone. Do not bring old friction, robot speed, drives,80Nm guard or3mmwallgate into benchmark.

One visible bounded integration≤180s to INSERT_READY, two capped captured-state restores within same launch; no TARGET execution. First substantive collision/regrasp/world mismatch stops, no alternative .700/.800 station or automatic second attempt. Software-only finite source reuse adapters do not reopen exhausted parity/static budgets. Relative Cube→TCP pose is not the native D6 anchor. Formal freeze thresholds and Benchmark-B geometry/runtime remain pending; TASK01 PARTIAL/notFROZEN. [Protocol](../reports/TASK01_FIXED_HANDOFF_INTEGRATION.md).

## D039 audit follow-up — Pinned primitives and explicit rail-state review [ENGINEERING]

2026-10-08, user requested rereading latest governance and asset audit before integration. Fixed predecessor source631b1f, current definitions c525fc1. Reuse Task24 SG lifecycle / atomic command and Task26 local rear full-chain precheck / segmented position push / exit, not whole five-Cube Task27 wrapper. New START remains D034 scientific(.55,0,.38), not legacy feed. Correct reuse-map sequence to release→left park→right rear, matching D039/YAML.

Raw historical right-pusher evidence includes **both bases .650→.750**, model world_shift .100. YAML's .650 is rest station, not a frozen B prohibition/selection. Recommend existing rail handoff as a nominal candidate; **user confirmation pending** before adding it to INSERT_READY or implementing. No decision to change base rest, tool, carriage, TARGET, ACM, friction/drive or frequency has been made. Do not call old .750 PASS a current fixed-.650 result.

Future deterministic INSERT_READY needs actual14q plus actual bases/rails/frame shift, Cube/TCP/SG/attachment and post-step time. Old raw7q candidate output is insufficient. Existing live sampler can supply pose/time bindings; no new SG/regrasp/push or logging framework. No experiment/integration this turn; new budget0used, old budgets exhausted. [Audited source/provenance and minimal plan](../reports/TASK01_PRIOR_PROJECT_REUSE_AUDIT.md).

## D039 — Restore staged transport→release→rear-regrasp→single-arm insertion topology [ADAPTATION]

2026-10-08, explicit user approval after reviewing the already completed `dreamerToTOE/dual-arm-embodied-palletizing@side-suction-palletizing` work.

The reproduction draft had unintentionally changed the physical task by keeping both L-shaped side-suction tools attached from PRE_PUSH to TARGET. That was not the validated Task26/27 workflow and produced an Isaac TARGET wrist/deep-wall collision (~−3.016 mm link7 separation).

The common benchmark is corrected before freeze:

```text
Benchmark A:
bilateral shared hold, START → PRE_PUSH_SHARED

Fixed engineering handoff:
release both side suctions
→ left helper park
→ right pusher regrasp Cube -X face
→ INSERT_READY

Benchmark B:
right rear pusher, INSERT_READY → TARGET x=1.100
```

Decisions:
- retain TARGET x=1.100; do not move it to 1.090 merely to make the superseded bilateral topology fit;
- use the predecessor Task27 center-Cube default **right-arm pusher** for benchmark_v1;
- treat PRE_PUSH→INSERT_READY as fixed/common engineering setup, not a scored P3 controller;
- formal P3 metrics begin at INSERT_READY;
- prefer reuse of Task24/Task11–13 Surface Gripper holding and Task26/27 regrasp/push primitives over new infrastructure;
- preserve all bilateral-to-TARGET failure evidence as historical negative evidence;
- full five-Cube scheduling remains LEGACY/stress-test, not the scientific one-Cube baseline;
- wrench semantics remain TASK10-IS; historical joint/contact readings are not calibrated wrench evidence.

This is a benchmark topology correction while benchmark_v1 is still DRAFT, not an ACM relaxation or hidden geometry repair.



## D038 — One launcher-only allowance; critical safety only, no READY/reset [ENGINEERING]

2026-10-08, explicit user approval: additional1/1,120s whole-process hard cap; reuse existing harness and four recorded14q/Cube states. Only command/stdin flow correction; no probe/collision/model/tool/carriage/ACM/physics/IK edit. User supersedes automatic5+5reset because freeCube does not represent already-stably-sharedheldSTART. End statuses TASK01 PARTIAL / safety PASSorFAIL / READY BLOCKED_BY_SHARED_HOLD_SEMANTICS; wait for user holding-representation decision. No force/suctiondynamics sidework.

Implementation has **no source edit**: pipe3 automated continuation tokens then fourth stop after saved fourth snapshot, before RESET. Tokens are launch flow only, not manual scientific/READY acceptance. Original collision guard remains higher-priority. Default GNUtimeout groupKILL120s covers children; no TTY read. Old harness default5reset in inputs is preserved as forensic metadata, not current authorization.

Actual one attempt: TARGET leftlink7/deepwall−3.016427159mm triggers STOP before fourth stdin; raw right contact−3.016243223mm. Foursteps,0reset; resource-close wait capped137, owned gone. TASK01 PARTIAL / safety FAIL. No geometry/controller/tolerance repair or second launch. Collision action and holding representation separately await user; no implicit suction/rigid attachment choice. D034 new scientific START remains distinct from Task27 feed. Prior static3/3, controlled1/1 and additional1/1 consumed; no autonomous budget reset. [Report](../reports/TASK01_CRITICAL_SAFETY_COMMAND_RERUN.md).

## D037 — User-approved one bounded critical-state fallback; no automatic retry [ENGINEERING]

2026-10-08. Explicituserapproval: staticparity07→08→09 counts as one root3attempts, exhausted; stopzero-step/staticquery/nativehandle/querytree extensions permanently. Newallowance **one** boundedcontrollednormalstep visibleGUI fallback, onlySTART/PRE/state196B60/TARGET (at most5ifrisk-basedreplacement, no replacementneeded). Exactrecorded14q, originalCube/tool/carriage/grasp/SRDFACM/physics, noIKresampling. Immediateunexpectedcollisionstop; TARGETCube/deepboundary pendingdefinition, not automaticFAIL/redesign. Onlysafetygatepasses then5START+5PREdeterministicreset withpoststepclock, thenPASSCANDIDATEREVIEW/notFROZEN.

Scientificrequirement is minimalcriticalIsaacsafety, not equivalence/exhaustive292/zeroqueryproof or force/suctionstability. Proberetainsactual drift/depth, noreset/successthresholdinvented. START(.55,0,.38) remainsnewresearchbenchmark/notlegacyTask27feed (D034). Deferreddefinitionitems: TARGETtouch, reset/successtolerances, already-heldstart semantics, frequencypolicy; no changeshere. BUG001staysTASK10IS/P2, P2P3/fiveCubeoutofscope.

Actualoutcome: source47d22ce, bounded120sGUI1/1used. START1sample/noobservedunexpectedcontactpenetration/focusenvhit, butaddedstdinreviewblockedT/Tl, inferredTTY/SIGTTIN, exit124; noacceptedreview or otherstates/reset. Allprocessesreaped; sourceunchangedafterrun. No secondattempt or parity10. STOPFORUSER, TASK01PARTIAL, no candidatefreezeclaim. Prospectivecommand-onlyforeground-terminalcorrection needs explicitnewboundedallowance, notautomaticbudgetreset. [Report](../reports/TASK01_BOUNDED_CONTROLLED_REPLAY.md).

## D036 — 2026-10-08 TASK01 minimum evidence / anti-loop scope decision [ENGINEERING]

User explicitly requires current GitHub AGENTS/EXECUTION_GOVERNANCE review, not inertial parity09 development. Read cloud main `0e3f8f5`. REQUIREMENT is a minimal reproducible oneCube environment with actual critical-state safety/reset; static all-state original-query checking is a PREFERRED METHOD, not the scientific goal. Recent07/08/09 same-root default3/3 exhausted despite different sub-errors; stop/no parity10, no initialization-schema implementation. Preserve A136/B157 geometryPASS and known14q; no change to benchmark/tool/carriage/grasp/ACM/limits/acceptance/physics. Correct09 actual failure instead of planned state.

Recommend STOP FOR USER now; proposed FALLBACK is small critical-state controlled synchronized visible replay plus ≥3START/≥3PRE resets under one ≤120s bounded attempt, original configuration and poststep time, first unexpected collision or unvalidated measurement stops. Proposed route not implemented/authorized; user must approve allowance and any change from earlier strictly static preferred method. Do not silently waive remainingruntime safety/reset or claim exhaustive model-equivalence/continuous collision/stability. BUG001 remains TASK10-IS, legacy5Cube not prerequisite. [Review](../reports/TASK01_GOVERNANCE_REVIEW.md).

## D035 follow-up — 08 query缺口保留，逐态原handle重建先安全审核

2026-10-08，[ENGINEERING]。08零步官方subsystem refresh未证实link2 query（accepted0），不能报parityPASS/collision判决；本轮actual14q/TCP/FK已存，仍只静态index，不叫poststep/force证据。09仅设计逐状态原native handle重建，安全API复核中未执行；保留owned原USD/hashes/已捕获14q与完整零步/query守卫，不改model/几何/ACM/benchmark、不随机IK。无P4/DEVIATION；先parity才READY，BUG001延期非阻塞、03–08原记录保持。

## D035 follow-up — 原SDK非physics更新只作刷新候选，不推定query freshness

2026-10-08，[ENGINEERING]。07 callback0/q-native及镜像门禁通过后，left link2内部点query未命中即拒绝，不作collision判决。08仅准备原IPhysxSimulation.flush_changes和IPhysxStageUpdate.on_update(static_time,0,False)；文档只说明physics更新关闭、其他子系统更新，不保证query tree freshness，必须保留所有原positive/negative query、step0/q/native/geometry hardguards。

source29cfd626… prepared NOT_RUN、测试待主代理。不Play/stepping、不改原model/benchmark/ACM、不实现P4/DEVIATION。先parity才READY（NOT_RUN），BUG019未判决/BUG001非阻塞，03–07原负证据与成功q/liveFK未存限制保留。

## D035 follow-up — 不触发Play的原API初始化，不修改SDK callback或物理

2026-10-08，[ENGINEERING]。06 official render gate仍观察2步并拒绝；SDK_warm_start/update_simulation与_create_simulation_view第二调用绕过render gate可解释事件数，但未捕获唯一因果trace。07仅准备不timeline PLAY，原force_load/start_simulation API只初始化，不update/simulate/fetch，不禁用/patch SDK callback；全部零步/q/native/几何/query freshness门禁保持，不改physics/model/ACM/benchmark。

source8887ad…待freeze，GUI07未运行；03–06负结果保留，先真实parity再READY（NOT_RUN），BUG019无科学碰撞判决，BUG001延期非阻塞。不是P4或论文[DEVIATION]，不预报PASS CANDIDATE/FROZEN，TASK02 TODO。

## D035 follow-up — render dispatch隔离与独立step0，不把动态输出当几何参数

2026-10-08，[ENGINEERING]。05 paused app.update实际积分2步/START accepted0，立即拒绝，不给静态/碰撞PASS；pre_notice27 native证据只支持通知前状态，不混用after-notice。06准备按官方SimulationContext.render方式临时关闭 `/app/player/playSimulations`、app.update后finally恢复原bool，force_load初始化也隔离，实际callback必须0且time/q/native再验。

SDK动态body velocity/jointstate从不可变“几何参数”hash中单列为state-output，并不移除独立step0拒绝；mass/scale/mesh/limits/drive/material/scene/frame仍严格库存。Scene dt/gravity/benchmark/ACM/实际几何不改，纯mock回归和GUI06未完成/source待冻结。无P4/DEVIATION，READY仍NOT_RUN，BUG019未判决、BUG001非阻塞；保留03/04/05，`8188168` direct push已完成。

## D035 follow-up — 原属性precision与state-output/geometry双审计，不消除负结果

2026-10-08，[ENGINEERING]。04因原SDK Cube orient expectedQuatf/gotQuatd在START停止，accepted0/wrapper0非PASS；Fabric disabled/updateToUsd=true，native成功值未保存且未进入碰撞判定，03/04均保留，不能作BUG019几何判决或修复证据。

05仅依既有状态属性precision写值。将body pose state-output库存与不可变几何尺度分开：原SDK可能自己物化Cube orient，这是SDK状态输出，不是helper新增ops；helper依旧只写existing translate/orient、不新增/重排，非法顺序拒绝。geometry fingerprint涵盖全scene physics/材料、所有相关ancestors、工具TCP库存，原scale/local collider/shape/mesh/limits/参数和q/native/setting/step0守卫不削弱；新增final与screenshot step0检查。35纯USD/query测试主代理实际复跑exit0/0.093s，source已冻结，GUI05尚未运行。

不改任何benchmark/实际几何/ACM，不实现P4、force或论文[DEVIATION]。READY仍须先过实际parity；BUG019未判决、BUG001非TASK01阻塞；全部门禁通过也只PASS CANDIDATE。Git采用命令局部direct push成功上传 `a672224`，首次proxy timeout记录保留，不改全局SSH。

## D035 — 静态输出源工程修复保留原模型与全部取证门禁

2026-10-08，[ENGINEERING]。03 START/state0 因USD collider旧旋转被正确拒绝，accepted0；wrapper0不等于PASS，不把尚未发生的移动shape/full-chain查询说成几何失败或BUG019实际碰撞。已通过native actor门禁但成功值未存，只记录控制流事实，不能事后补成实测数值；后续新的执行应完整保存native与USD比较。

04准备优先复用官方scene/Fabric当前已有导出路径。若仍stale，仅可把已经验证的native actor SE3镜像到**原body已有**translate/orient作为静态输出适配；不得新增/重排xform ops，不动原scale、collider local transforms、网格/shape、物理/设置、工具/车厢/抓持/SRDF/ACM/IK验收/基准。处理paused notices后再次完整核对q、native actor、原几何/设置与step0，实际cooked-shape positive/negative移动query freshness门禁不削弱。不能用USD镜像自动推定PhysX actor或broadphase已同步。

04尚未运行；任何证实FCL-free/Isaac真实意外重叠依旧首败即停/exact pair，不修几何。静态replay以index记录、step/time=null，不伪称postphysics reset数据；仅parity实际通过才继续START/PRE多次READY/reset。此决策不是P4实现、论文替代算法或[DEVIATION]，不为TASK01加force门槛；BUG001属于TASK10-IS。只在所有门禁实际通过后才可PASS CANDIDATE，FROZEN仍待用户批准。

## D034 evidence follow-up — 全链实得14q只候选，先核模型再reset

2026-10-07，[EXPERIMENTAL] 新START几何链实际A136/B157通过，实际PRE14q完全相同；所有状态distance而非仅六端点已保存。START与PRE配置记录候选YAML，不自动FROZEN，不再随机求起点。原run配置独立快照/SHA，避免录q后篡改旧hash。

[ENGINEERING] 全链最小腕工具环境gap在TARGET左link7/deepwall2.212219mm；另全pair min约1mm为现有Cube/杯面间距。实际PhysX对照优先START/PRE/TARGET/state196，再其余全部状态；不用FCL模型给PhysX背书。未过parity不做reset，未过reset不标TASK01 PASS CANDIDATE；旧5Cube与force/wrench仍不在范围内。

## D034 — 新科研START明确批准；全链几何→模型一致性→READY/reset按序门禁

2026-10-07，[ADAPTATION] 用户明确确认Benchmark A START Cube=(0.550,0,0.380)m、xyzw=(0,0,0,1)：双FR3已经通过当前shared-grasp transforms稳定共同持件并离桌，不包含抓取过程。**这是新的科研benchmark设计，不是旧Task27 feed pose**。PRE_PUSH=(0.790,0,0.260)、TARGET=(1.100,0,0.260)、L工具/车厢/抓取/TCP/基座/碰撞网格/SRDF/ACM/独立验收保持。

[ENGINEERING] 探针继续已验证LMA epsilon1e-7/weight0.01、平移1e-5m/旋转1e-4rad验收和≤2mm Cube位移；记录所有状态full FCL最小距离/最近pair及腕工具环境距离。A先检查，首败即停；A通过后以其实际PRE14q延续B，不能简单拼接旧B另一IK构型。记录实际START14q为候选及provenance，供后续reset精确恢复，不自动FROZEN。

[EXPERIMENTAL] 几何通过后才可见GUI静态replay单Cube全链作BUG019原模型对照，任何FCL-free/Isaac-overlap exact pair出现即停止，不改几何/ACM。模型门禁通过后重复START/PRE reset，用post-physics-step simulation stamp记录q/Cube/TCP/frame误差。不得开五Cube/完整控制器/force calibration；BUG001/wrench/重力惯性补偿归TASK10-IS，不是TASK01门禁。全通过也仅PASS CANDIDATE，待用户最终冻结审查。

## D033 — 原几何/门限下同seed数值精度对照，不等同物理或论文PASS

2026-10-07，[ENGINEERING]/[EXPERIMENTAL]。用户批准“继续”保留几何诊断；只在独立探针中记录每臂拒绝并允许收紧LMA epsilon（1e-5→1e-7），同一失败14q/目标重放。保持orientation_vs_position0.01、平移1e-5m/旋转1e-4rad验收、原限位/模型/抓取/ACM/runtime文件不变；不新增随机重试、暗改START或工具/车厢。只证明数值停止精度不满足原验收的局部问题得到解决。

随后≤2mm名义插入检查首次真实失败即停；157状态实际通过，也只记离散几何PASS，整体PARTIAL待START和Isaac审查，TASK02不提前开始。robot FCL未覆盖的worldCube/environment，用当前原盒形/零偏航AABB补审计，不豁免接触/改变PhysX。保留原失败与旧binary无效尝试，完成实际构建后核对exe再跑；无新论文[DEVIATION]。

## D032 — 单 Cube 几何先行，首败后停止，不从端点PASS推断路径PASS

2026-10-06，[ENGINEERING]/[EXPERIMENTAL]。遵循用户新要求及云端已批准单Cube范围（同日single-Cube D016，与历史XYZ D016不同）：只做几何，不启动长Isaac试验。端点PASS与同一seed加密链分开记录；连续链首败后不再搜索/修改，不将数值IK失败称工具几何不可行。START仍待定义，不自行选择供料点或平移导轨。以后只有用户确认诊断范围后再继续，工具/车厢/TCP/SRDF/ACM和force/wrench延期边界保持。未新增论文[DEVIATION]，没有借机实现P4。

## D031 — 仅新侧接触下降补实际规划时间化，不降播放倍率掩盖问题

2026-10-06。[ENGINEERING] 本机Humble Cartesian srv无v/a scale；Task01 DUAL_SIDE_CONTACT以现有MotionPlanRequest速度/加速度scale（当前0.12）做IPTP，逐点q和joint_names必须完全不变，完整同步FCL保持，播放1.0/PhysX秒不变。不是改物理或关闭碰撞，不改其它Cartesian或旧节点时序；不将slow成功当normal成功。真实接近仍失败则保留，不从软件补计时称已经修复。

## D030 run follow-up — fresh GUI实测，不拿软件测试称通过

source6fa161e串行58.5s/Binary75f798a1核对后进入fresh可见原场景首件；GUI显示/READY确认和控制器初始化均实际通过。外部20s只读原子消息receipt记录物理/现实时间关系，不能把receipt频率当纯physics FPS或据此单独证明接触根因。保持所有原保护/模型/36nulls，先实际结果再决定五件。

## D030 — 正常规划播放用实际PhysX秒，GUI延迟不变成隐性加速

2026-10-06。[ENGINEERING] 仅Task01 single/sync执行器，从已校验的原子fixture_geometry拿物理stamp；一次循环双臂同phase，重复stamp停进度，回退拒绝，原250ms收件失鲜拒绝且无wall fallback。1.0定义为正常物理规划秒，12%RRT限速/原Cartesian时间/phase平滑/下发周期均不变。不是改physics dt/drive/路径/ACM，也不是论文控制律。真实GUIrun02跟踪/接触负结果保留；因果不唯一，fresh重测前不宣称物理修复。如果标准规划速度仍失效，不自动降速、提高force gate或改模型。

## D029 — 可见SimulationApp复用原fixture记录器，不静默fallback

2026-10-06。[ENGINEERING] 新GUI入口显式headless=False，缺DISPLAY立即拒绝；本机官方Kit VS Code执行器只监听回环。只增加可视灯光/观察相机，不改原场景/工具/碰撞/物理、采样或控制门限。第一次可见GUI渲染失败时先不运动，保留0命令/native139负启动，再独立fresh GUI截图确认后实测。先单件scale1，后按结果五件；不能拿旧慢速PASS支持新速度/全任务PASS。历史headless源码可保留复现，但本轮及未来不得直接启动其无界面入口。

## D028 — 正常规划轨迹倍率与GUI-only仿真

- Date: 2026-10-06; Classification: [ENGINEERING]运行默认值/工作流；[EXPERIMENTAL]后续新速度验收。
- User input: 用户询问是否50%运行并要求100%；以后不要headless，需要看场景。
- Decision: 当前`task01_dual_suction_fixture`默认`execution_time_scale=1.0`，含义是按规划时间100%播放，之前实测5.0是20%、2.0才是50%。该设置不等于MoveIt/机器人关节上限100%；RRT速度/加速度12%保持并明确告知用户，不推断批准把接触运动直接提高至硬件上限。
- Workflow: 以后助手只启动可见Isaac GUI，不再headless；保留历史脚本、命令与原始负证据，完整列出scene/Play/Bridge/原子反馈加载步骤。当前仅改新节点默认值，旧Task26/27参数不受影响，显式历史5.0参数仍优先于新默认值。
- Validation boundary: 1.0实际轨迹需要重新GUI物理验收；此前慢速单次PASS不可用于normal倍率成功率。250ms反馈/80Nm/2.5mm/ACM/物理/模型/36项null均不改变；不启动P2/P3控制律或TASK02。

## D027 follow-up — 加密空载几何检查、保持路点的计时，先同路径对照

首个请求局部scene探针3次被MoveIt自己判后处理路径无效，全部负结果保留。下一工程范围仅OPEN空载handoff：在当前控制器内加载原OMPL插件和配置副本，本地检查分段比例0.0005、IPTP计时并逐值验证q路点未变，最后仍原0.01s完整FCL/起点/目标/限位守卫。不是启动后台沙箱/第二move_group，也不改全局参数、加载轨迹、ACM、世界或接触门限。probe同一raw RRT分别检查原几何/defaultTOTG/IPTP，不能先验声称TOTG唯一根因。当前改动未作物理成功承诺，不是P2/P3复现或benchmark冻结。

## D027 — 只读重放与实际路径规划使用同一完整场景和顺序起点

Date: 2026-10-06. [ENGINEERING] 新fixture空载转场有限RRT候选池，原场景、目标、碰撞冗余、ACM、阈值不变。先从一次完整实测RobotState规划/验第一臂，再以第一臂预测终点+第二臂原起点规划/验第二臂；两段均通过才执行。MoveGroup plan_only的planning_scene_diff只作用于该请求场景副本，不是后台沙箱预规划，不写远程Scene，也不豁免当前Cube。实现/真实验证待完成，不能预记PASS；若需改变模型/物理/门限则另问用户。官方MoveIt2 Humble move_action_capability.cpp 的executeMoveCallbackPlanOnly使用copyPlanningScene进行请求局部规划。

## D026 physical checkpoint — 以实际完成计数，不以候选成功计数

full02已实际batch1/2通过，第三抓取继续。联合gate PASS只授权同候选后续实测流程，不将preflight当batch完成；原RRT/FCL重试/OPEN XYZ/原子geometry/80Nm仍全部保留。短清障后的GT而非释放前命令终点作为最新落点记录，不从2/5提升稳定性或冻结状态。

## D026 run follow-up — READY与hash双守卫后才运动

production57e72f83强制重编译核对成功后，fresh full02只有在新场景日志出现真实first feed READY且exe SHA完全相符时才启动。启动正确不等于物理成功；运行期间不改当前源码/门限/场景，避免再次二进制与记录时序错位。

## D026 build follow-up — 实验前串行核对最终执行二进制

不边修改include边编译production目标；增量no-op/mtime不足以保证源码一致。full01 174d6ef7等价声明作废并保留启动负结果；当前强制目标重建，不编辑生成install文件。核对新binary SHA及真实执行初始化后才能算source对应运行。probe已通过的本地联合链结果独立保留，不拿未动作的production启动当物理测试。

## D026 follow-up — 旧solo预检不能代表新双吸链

首三选候选改用新双链，不再要求/宣称旧helper-park solo PUSH/RETREAT代表rear+side可行；后两/旧节点保持原逻辑。实际HIGH RRT/下降/加载联合FCL及80Nm/原子几何guard依然必做，不持件换构型。参数从实际运行MoveIt读取，支持现有root arm布局，不把插件变化当成算法修复。只读链通过后才进入fresh原场景物理回归，不以endpoint或软件PASS冻结benchmark。

## D026 — rear在OPEN候选选择时预检新双臂链

2026-10-06，[ENGINEERING]。同rear吸点已有替代端点构型可让side HIGH/CONTACT全FCL自由；选择时只看旧solo推入不够。仅新首三候选改为HIGH IK、连续下降（自由当前Cube参与FCL）、同进度双X/Y和短退出；原合法运动当前Cube仅在本地push世界不作静态障碍，所有其它对象/ACM不动。旧后两精准solo预检不改；现场实际HIGH RRT连接与负载检查仍必做，不能用候选预检绕过真实保护。保持原场景/工具/吸点/姿态/物理/80Nm/几何门限，局部插件参数来自当前MoveIt有界读取。不是论文算法、CLOSED构型调整或全局可行证明；真实回归后才汇报结果。

## D025 — 第三goal失败先做固定rear的有限IK/FCL重放

2026-10-06，[ENGINEERING]/[EXPERIMENTAL]。front2物理通过、third side HIGH无合法目标，先用原MoveIt模型/kinematics/world和精确实测14关节/Cube输入，在纯probe固定后臂、60个有限侧臂IK种子统计goal collision pairs。无Arm/机器人/吸盘/导轨/供料消息、无远程Scene/ACM写入。0合法候选不等于全局不可行；不从怀疑直接改rear/side的物理姿态、场景或保护。若要调整选构型预检，需先得到重放证据，保留full01失败。

## D024 follow-up — 精调首件通过后才进入五件；命令限步与轨迹span分开

首件两次OPEN精调norm2.196→1.201→0.205mm，实际流程controller0。1mm限制上一命令目标的修正向量，不是从实测起点的全部TCP运动；本次span3.178/3.200mm含旧执行残差，仍满足既有4mm/0.02rad微解算/FCL范围。明确记录这一区别，不隐瞒位移或放宽加载门限。

下一步同binary/原物理fresh zero-preplaced first1/max5，前三双吸附后两精准单rear。只一次首件不证明后续Cube、不自动冻结benchmark/推进TASK02；任何失败保留并停止后续对象，原模型/物理/门限权限边界保留。

## D024 — 复用吸附前XYZ消除rear重抓残差，不放宽加载门限

2026-10-06，[ENGINEERING]。rear45实测X1原子alignment2.578mm、主要rear Z残差，复用用户已允许的OPEN XYZ精调：仅前三后杯重抓，上一发送命令FK加同一步Cube/TCP残差；每次整向量≤1mm、最多3次/4检查。0.3mm仅新的吸附前目标精度，不替代原2.5mm/80Nm/碰撞门控。helper OPEN实测保持、原自由Cube/所有其它静态对象参与联合FCL；观测过期/失败则双OPEN停止，不CLOSE或推进下一件。

后两单rear/旧节点/L工具/世界几何/材料/物理/ACM及CLOSED路径不变。属于既有精调软件复用，不是论文控制律或新的力控；实际fresh首件须另验，若需模型/物理/门限改变仍停止询问。

## D023 follow-up — OPEN时建立后腕姿态，CLOSED时只共同平移

无命令rear45三链与三墙检查通过后，仅新3+2节点前三后抓RRT/预演调用同一函数，后两件原pushPose；不在已经吸附时修改相对grasp。参数非法在Arm前拒绝。原几何/物理/门限/ACM不变，fresh首件实际验证是必需，名义结果不叫物理PASS。

LP求解变更为[ENGINEERING]：等价坐标重心化、同全部约束的HiGHS-IPM与解残差检查；两次default solver失败保留，没跳数据/没更改碰撞成功阈值。

## D023 — 保持后杯面法向，先向中央让腕的无命令验证

2026-10-06，[EXPERIMENTAL]/[ENGINEERING]。原子反馈首件暴露rear右腕侧墙接触，不把原80Nm错误叫传感假报。只读probe增加rear worldX法向镜像roll幅值（诊断范围0..60deg，不是验收容差），尝试45deg/+Y正转、-Y负转，把腕向自由中央偏移；side保持-15deg。执行器未采用，没有CLOSED下转腕。

扩大**检查覆盖**到原三面墙，未扩大墙几何/ACM。既有deep-only结果保留且明确受限，新的名义PASS仍需完整空载接近/实际物理验证。模型/质量/材料/门限/36数值冻结若需改变则另问。

## D022 — 修复测量同步，不放宽接触门限

2026-10-06，[ENGINEERING]/[ADAPTATION]。用户继续授权下，在独立3+2节点前三双吸附的几何检查中引入单消息live PhysX快照，Cube与两个TCP共享一次读出；旧场景/bridge/topic和后两单rear不改。250ms仅观测新鲜度超时，不是新几何成功阈值。启动缺消息/运行过期拒绝，不能退回USD或无限重试。

保留dd63c74 X3失败，先进行相同原参数的新鲜first1/max1 headless复测及同回调USD源对照。模型/物理/ACM/80Nm不更改；新姿态深墙风险、碰撞模型差异和36数值评审仍待解决，不提前推进论文控制器/冻结。

## D021 — 先做原点/杯面法向不变的腕姿检查，不靠换场景或加力控

2026-10-06；[ENGINEERING]/[EXPERIMENTAL]。用户“继续”下，先保持原controller/模型/物理/80Nm实际复测并记录；实测机器人-深墙接触且FK一致，不再仅假定闭链内力。只读探针允许绕杯面法向worldY转角（有限±30deg诊断范围，不是benchmark门限）候选，杯面中心、法向、3+2角色、cube/墙/L几何不变；不选新基座/墙/碰撞豁免。

nominal02 -15deg通过原FR3链与原USD凸包离线检查；执行器尚未应用，不用无命令证据替代物理验收。nominal01采样行坏就FAIL分析，独立文件重跑而非吞掉坏行。若需要改模型/物理/benchmark/论文算法则另问；36nulls/TASK02保持。

## 2026-10-06 follow-up — 网络恢复，原场景第二次启动

原S3直连/代理HEAD恢复HTTP200，runtime d35cc0c正常push成功；保留startup01失败。相同官方资产/原参数的startup02重新运行，held live handles与首件物理诊断仍待验证，尚未发controller命令。BUG017根因未解决，BUG018外部连接暂时恢复不抹掉负结果；模型/物理/门限/YAML不变。本段更新此前“final”失败checkpoint，不叫新物理PASS。

## 2026-10-06 final — D020 final：外部依赖失败不篡改模型取得结果

只读代码/44软件测试/编译通过，外部资产失败使真实采样尚未验证；保留原模型/门限，不把未验证来源的cached FR3当作原模型替换。保留失败.json，即使Kit cleanup退出0也判startupFAIL；不宣称新3+2或Y15通过。网络/代理恢复后从同样普通供料首件重启并先确认live sampler，随后再做证据驱动工程修正。没有修改系统网络设置/SSH凭据或开始论文算法。

## 2026-10-06 — D020 诊断优先、控制律不改

[ENGINEERING]新增专用异步phase topic并复用同一步sampler；真实contact-report telemetry为可选运行期API，不改原源码场景/几何/材质/质量/驱动/solver。采DOF投影effort而非混合6Dfallback；保持revolute Nm/prismatic N区别，不叫TCP wrench。先记录后决定是否有原范围内修正，不默许力控/物理/门限改变。

## D019 final checkpoint — 新流程软件实现不等于物理验收

2026-10-05；实测换角色试验X16/Y14后在Y15触发86.975Nm保护。保持前三双吸附/后两精准单推，不以helper退场、单臂替代、提高80Nm或改场景获得PASS。首件未完整完成，不继续后四件并称新5/5。

仅添加释放后静态只读FCL诊断，不解释为触发步无碰撞；下一步为持件同物理步接触/关节观测及证据驱动工程修正。若确需改物理、工具、基准或新增论文/力控方法，遵循原停工确认边界，而不是由失败自行授权。旧5/5与新3+2负证据分开，benchmark仍DRAFT/36nulls。

## D019 follow-up — 换主从角色必须使用墙接触后的实测起点

2026-10-05；[ENGINEERING] e0477ab仅新节点：X到深墙后重新取双臂共享实测状态和新Cube GT，保持双CLOSED，通过当前联合FCL后从该真实起点按原目标重算Y/释放包络。不得把命令终点当作真实刚性闭环状态，不增加顶墙越程、改材料或放宽80Nm/几何门限。旧日志未确定互锁原因，补详细诊断与新鲜场景复测，不把这个合理修正称为已证明根因。

## D019 — 前三 rear+side 双吸附，后两精准单 rear 插入

- Date: 2026-10-05；用户明确批准新的3+2分工，覆盖D004中“前四件双吸附”的该部分。
- [ADAPTATION] 新独立节点 `task01_dual_suction_fixture`：旧共同 lift/XYZ 搬运/落桌后，rear 重抓 -X 面；helper 抓朝中央自由通道的侧面中心。双 CLOSED 才允许共同 +X 推入，到深墙后不松吸盘互换 rear-hold / side-primary。第三件是双吸附侧压，不隐性回退成 helper park / solo trim。第四/第五继承精准暂放、单 rear 推入。
- [ENGINEERING] 两臂使用同一物体位移进度，每2mm共同 waypoint 复用有限世界FK Jacobian微解算；每段保持实际 grasp 相对变换，整条联合10ms FCL及原2.5mm/3deg相对几何门控。不是把独立时间参数化轨迹仅拉成一样时长。旧节点负载路径不变。
- [ADAPTATION] 双吸附闭环不能照搬旧未吸附侧压的4mm压紧越程；新节点终点为既有贴墙格位。没有改变墙/格位/验收值。第三件保留原1mm短压目标，第四没有侧压。新释放局部法向清障包络30mm，只有双OPEN才执行，再接原RRT/FCL转场；不要求helper跨过整个中央槽120mm退出。
- [ENGINEERING] 新执行器带CLOSED/OPEN及原80Nm原始关节effort互锁、有限候选、失败双OPEN并回写当前Cube，保留旧可执行节点。无执行探针不构造Arm或发布joint/suction/feed/rail，也不修改远程PlanningScene/ACM。
- [EXPERIMENTAL] 名义IK种子/盒体检查及本机headless验证只建立工程可行性证据；没有校准接触wrench或P2内部力/P3力位混合控制。推墙阶段只有当前移动Cube按旧接触策略不作静态障碍，其余桌/墙/已放块与全部机器人碰撞检查保留；不声称这就是移动物体的完整连续接触动力学证明。
- TASK01仍IN_PROGRESS / DRAFT /36nulls；模型/物理参数和YAML/hash保持不变。新版5/5未验证前，不借用旧df9c2c0的5/5作为新版PASS。

## D018 final validation — 不把一次成功扩大为方法或可靠性证明

2026-10-04；[ENGINEERING]。保持源码和原门限不变完成一次零预置/hold=0 的实际五件回归。旧 Cartesian/continuous-seed 优先，有限 RRT 仅双吸盘 OPEN 且前者拒绝后使用；本轮未触发，不能用 5/5 为其实际执行背书。失败重放 01、历史 Cube02 回带和 MoveIt teardown 继续保存。

[EXPERIMENTAL] 慢速 scale=5 / OMPL RNG 不受控的一轮本机 headless 成功只证明该次流程到位。停止本轮自有测试进程，不继续循环来声称稳定。TASK01 的论文接触协议、材质/质量、力/时间测量与 36 数值冻结需要用户审查；不因 demo PASS 自动推进 TASK02。没有新增 [DEVIATION]，既有 D014 第四件适配与前三件 D004 差异仍单列。

## D018 validation — Check original goal semantics, keep negative evidence

ENGINEERING: evaluateendpointusingactualMoveItconstructedgoalconstraints insteadofinventingaggregate-anglegate; numeric/seed/bounds remain. Frozenacceptancevaluesunchanged. Beforephysicalcommandsverifyroundedfailedstate/railshift andtemporaryabsent-IDsynccleanup withnorobotpublishers. Preservefailedfirstreplayanddo notinferexisting-objectrestoreverifiedfromabsence-onlycase. Actualrunusespinnedbinary/source; nogoal/scene/material/ACMchangesmidrun.

## D018 — Reuse bounded free-space RRT only after physical release

2026-10-04; ENGINEERING. User“那你继续，我记得之前退出都是没问题的啊”requestscomparisonandrepair. KeepCartesian/localcontinuousseedfirst; ifrejectedandbothcupsOPEN, ≤3RRTConnectrequests/arm,3s/request, samefullmeasuredstartandoriginaltargets. PreservecurrentreleasedCubeinworld/MoveItplanningandjointFCL, checknumeric/bounds/firstpointnotadapter-shifted/endpoint, ranksbyexistingjointtravelscore. Temporarilyaddedworldobjectmustsynchronouslyrestore,elseabort. No loadedXYZ/contact/scene/material/ACM/gate/paperchange. Roundedreplaymustusepreviousbatchrailshift0.1m; noexactA/Borfullphysicsclaimfromreplay.

## D017 — Repair measured start before entering the blocked diagnostic window

ENGINEERING: newdiagnostic revealspre-releaseactualsideplanningmixescommandjointseedwithmeasuredCubeGT. Reuseexistingone-RobotState seedmechanismforindependentactualsideentry; validateCLOSEDpusher/OPENhelper, jointfinite/count/bounds andoriginal0.035radcommanddeltagate. KeepcurrentCubeinFCL, allphysics/contacttargets/protocols/ACM unchanged. Ifmeasuredstartstillcollides, stop; do notallowpairtoobtainPASS. Thisprerequisiterepairdoesnotestablishrelease-driftcause. Nextordinaryfullfivehasdiagnostichold0, nosilent3sdelayfix.

## D017 checkpoint — Diagnostic timing is not normal-flow evidence

Keep3s hold strictlyopt-in/default0. Enddiagnosticaftersecondcompletedbatch andbeforelaterobjectmotion toavoidfixedsimduration interruptingloadedtask. Do notcallfirstcubestabilitysecondcube repair ordiagnosticPASSordinaryfivePASS. Maintainasynctag caveat andcollision-versusD6 distinction; addpeak/mixedstep regression beforeusingcontactsummary. Noactivecontrol/physics/contact/gate changefromthischeckpoint.

## D017 — User-approved release/withdrawal repair, evidence-first scope

2026-10-04; user“继续”followingexplicitproposal permitsminimalrelease/clearanceengineeringrepair. Firstaddread-onlyphase/tool/contactobservations andoptionalpostreleasehold; ifcubeisstablebeforefirstwithdrawal, inspectactualseed/pressure unloading/trajectory ratherthanchangefrictionorforcegates. Adiagnosticholdrunisnotordinaryfull-flowproof. Preservemodel/material/ACM/gripperparameters/successgates/YAML; stopifcontactredesign/forcecontrol/benchmarkchoicebecomesnecessary. PriorD004gapstillpending.

## D016 validation — Scope completed without expanding into loaded/release control

2026-10-04; XYZactualtwo-correctionPASS, but new laterCube02deep-wallfailure5.138mm retained, rather than claiming full-flowPASS or adjusting3mm gate. Stop after safe diagnostics/records; fixing release/withdrawal/contact or adding force/physics changes is a distinct next scope. Originalmodel/material/ACM/contact/loadedflow and36nulls preserved. Report TASK01_PRECLOSE_XYZ; BUG-016. One negative normal-feed run is enough to reject stability, not prove physical impossibility or a specific contact-force root cause.

## D016 — User-approved merged XYZ pre-suction correction

2026-10-04; [ENGINEERING]. User “好的，那就这么做” approves described XYZ extension/speed policy. Apply only when original attachment gate fails and both cups OPEN; accumulated command-FK plus actual residual, total1mm vector bound, same fineIK/FCL/orientation, maximum3checks. No separate X/Y/Z RRT, no correction when already valid, timing recorded. No authority inferred to change mass/material/contact topology/gates/freeze36fields or implement paper force control. Old Task26/27 nodes retain Y-only semantics; current precision variant receives the change.

## 2026-10-03 — Full-run failure retained, no autonomous compensation expansion

Actual no-preplacement run failsCube02Xcorrespondence3.150mm>2.500mm afterYconverges0.001mm; onlyCube01placed. Keep same scene/model/control/gates and stop this test-only iteration rather than silently addXYZtracking compensation or relaxacceptance. Next scope should first isolate FK/tracking/metrology, then discuss bounded ungraspedXYZrepair; noforcecontroller/contactredesign/numericfreeze inferred. Earlierisolated/continuous4→5PASS remains true but cannot establish current full-five stability. TASK01IN_PROGRESS/TASK02TODO,36nulls unchanged.

## 2026-10-03 — Full-flow regression without expanding scope

[ENGINEERING]/[EXPERIMENTAL]: repeated user continuation permits testing current approved variant from normal feed, not redesigning physics or contact. No preplacement and no runtime code/model/gate change. Actual five batch PASS and exit code are required for full-demo evidence; ARRIVED alone is insufficient. A failure requiring material/research decisions stops for tomorrow. Existing36nulls/TASK01 review/D004 first-three discrepancy remain unresolved even if this demo passes.

## D015 validation / hard-decision boundary

2026-10-03; [ENGINEERING] scoped repair physically verified by isolated fifth and fourth/fifth pair, no currentCube exemption. [EXPERIMENTAL] first3/4preplaced; no full-five or stable benchmark assertion. Stop before choosing effective-friction baseline, modifying retained hidden mass, changing first-three D004 protocol, or approving36numericfields. These are material user decisions, not inferred from the instruction to continue independently. Preserve0.5/0.5 actualphysics and originalscene/gates tonight. TASK01 IN_PROGRESS, TASK02 TODO.

## D015 — Engineering continuation limited to already-released empty arms

- Date: 2026-10-03.
- Classification: [ENGINEERING], no paper-method or contact-protocol change.
- Decision: In the approved Cube04 independent variant only, use measured dual-arm seed after confirmed OPEN. Ordinary Cartesian first; bounded piecewise fine-IK seed continuation as fallback, same targets. Include the released Cube in synchronized full FCL and retain all original gates. No feedback/contact/model/physics adjustment to cure drift.
- User boundary: Continue independently only while no hard research decision is needed; stop and record choices if model/material/contact strategy needs to change. Freeze gates remain pending/36 nulls, TASK02 untouched.

## 2026-10-03 — D014/D015 validation boundary
- Final slow trial validates actual fourth single-rear protocol once with original gates; preceding faster trial failed. Report limited feasibility, not stable/five-Cube reproduction. Fifth empty Cartesian exit is independently refused by existing geometric guard. Do not change fifth protocol or hide this negative by calling fourth batch PASS whole-process PASS.
- Recommended next engineering step: safe empty-retreat start-state/IK candidate diagnosis, then repeated fourth→fifth tests. No scene/tool/material/gate change, force controller, research-baseline shortcut or numeric freeze.

## D015 — Retain failed pure single-arm test before considering feedback
- Date: 2026-10-03; [ENGINEERING]/[EXPERIMENTAL]. Cube04 precise-stage variant fails final 1.5-mm neighbor gate at 1.827 mm; do not restore inner trim, widen gates or declare physical impossibility after one sample. Repeat clean physics using final built binary and slower unchanged motion protocol.
- An online lateral-tracking controller would be additional method work, not simply reusing Cube05. Ask before changing that research protocol; all frozen/numeric questions stay pending.

## D014 — Authorized Cube04 single-rear insertion variant
- Date: 2026-10-03; [ADAPTATION]/[DEVIATION], explicit user approval: “那第4块采取第5块的推入方式”. Cube04 is an exception to D004; no blanket approval to change first three or freeze numbers.
- Add an independent executable reusing existing Task26/27 code, guarded compile-time policy; old targets preserve behavior. Do not change original Isaac scene/tool/mass/material/ACM or final placement gates.
- New Cube04 PRE_PUSH Y control target uses Cube02 GT plus 120 mm and original 0.5-mm pressed target; replace post-seat lateral trim, not geometry. Added <=0.5-mm Y engineering staging gate and nonnegative oriented-neighbor projection clearance; no force-control/paper fidelity claim.
- Experimental validation may pre-place/physically settle only the first three; fourth/fifth use normal feed and actual transport. Keep this distinct from all-five proof; YAML remains unchanged/DRAFT.

## D013 — Exhaust non-mutating fixed-contact alternatives before changing tool
- Date: 2026-10-03
- Classification: [ENGINEERING] exact OBB roll diagnostic, not motion planner or paper method.
- Decision: Preserve the user-required face-center contact and inward normal; test discrete TCP rolls on existing tool geometry before asking for alteration. At 15-deg spacing all 24 checked Cube04 poses retain support/neighbor interference. Record this scope; do not infer continuous-search completeness or accept no-box-interference as full IK/path safety.
- Impact: No physics/ACM/contact-position change. Request direction on model/protocol rather than silently adopting half-cup/edge contact.

## D012 — Successful old demo is not authorization to change benchmark physics/contact
- Date: 2026-10-03
- Classification: [ENGINEERING] exact geometry/actual-material readout and full-rate metrology; [EXPERIMENTAL] controlled hold; [DEVIATION] legacy protocol mismatch explicitly identified, not accepted as replacement.
- Decision: Keep ordinary 5/5 PASS separate from D004 fixture and TASK01 freeze. When current face-centered helper pose intersects neighbor, require direction before altering tool/contact/order; do not use ACM/edge-cup shortcuts. When actual Cube friction 0.5/0.5 differs from deleted authored material 0.90/0.75, ask whether to retain actual values or restore/revalidate; don't silently change physics under a bug-fix label.
- Measurement: Use every explicit-hold physics step, report mean bias and raw RMS/peak separately. Do not suppress alternating loads or claim per-cup/internal wrench calibration from correct average support; velocity-vs-pose consistency remains open.
- Impact: TASK01 IN_PROGRESS with unchanged YAML/hash/36 nulls, TASK02 TODO. Scientific review stop follows AGENTS stop conditions; no paper method or numeric/model approval inferred from “until task01 works”.

## D011 — Controlled static-load hold keeps telemetry running
- Date: 2026-10-03
- Classification: [EXPERIMENTAL] static metrology pause; [ENGINEERING] test-only control parameter and phase marker.
- Decision: Do not SIGSTOP a ROS manipulation process for a measurement window: it also stops callback processing and invalidates in-flight state requests. Archive the failed experiment; use task01_calibration_hold_sec only when explicitly requested, default 0, pause task progression while executor stays active and suction/geometry gates continue.
- Impact: 7-s hold changes this experiment's timing and cannot count as an ordinary timing/reliability trial. Physics, grasp stiffness, model masses and benchmark gates remain unchanged. Received hold phase is stamped at physical observation, not claimed to be exact actuator-event timestamp.
- Review: Near-unbreakable suction and hidden branch mass remain proposed inherited model features, not approved numeric freeze; ask user before changing them.

## D010 — Repair quantization without weakening alignment or bypassing protocol review
- Date: 2026-10-03
- Classification: [ENGINEERING] bounded residual/local-FK correction and scaled-transform extraction; [EXPERIMENTAL] normal-feed regression.
- Decision: Remove mandatory 0.650 mm pre-close step, keep maximum 1 mm, original 0.300 mm physical gate and three attempts. Use seeded local FK micro-IK only while ungrasped, with conservative scope/joint bounds and unchanged full synchronized FCL. Task26 default unchanged.
- Measurement: Task27 scale removal fixes its quaternion only, not USD frame lag. Explicit official asset root only avoids directory discovery failure; same FR3 source still required.
- Scientific boundary: A repaired legacy five-Cube demo is not automatically D004 fixture-protocol or TASK01 freeze evidence. No benchmark numeric approval, geometry/mass/material change, ACM expansion or paper implementation is authorized by persistence request.

Append-only architectural and scientific decisions.

## D001 — Two-platform strategy
- Date: 2026-09-29
- Decision: Isaac Sim + ROS2 is the final common benchmark; MuJoCo is an auxiliary force/contact laboratory mainly for P2/P3.
- Reason: preserve fair final comparison while accelerating force/contact debugging.
- Impact: baseline algorithms remain platform-independent and use adapters.

## D002 — Baseline-first rule
- Date: 2026-09-29
- Decision: `ours/` remains algorithmically empty until TASK30.
- Reason: derive our method from reproducible evidence and failure cases rather than premature design.

## D003 — Task27 as TASK01 geometric starting point
- Date: 2026-09-30
- Classification: [ADAPTATION]
- Decision: Use the existing Task27 dual-FR3, fixed L-side-suction, rail and five-wide truck-box scene as the *starting geometry* for the common benchmark draft.
- User input: Explicitly confirmed "对" in response to this proposed starting point.
- Scope: This does not freeze the existing physics, grasp/contact topology, perturbations, timings or success thresholds. TASK01 stays IN_PROGRESS until the candidate and all values are reviewed and validated.
- Impact: The Task27 source constants are traceable in `configs/benchmark/benchmark_v1.yaml`; unresolved choices stay null rather than inheriting unsafe demo defaults.

## D004 — Different contact protocols for the first four and fifth cubes
- Date: 2026-09-30
- Classification: [ADAPTATION] for the common Task27 cell; [EXPERIMENTAL] for the task-specific staged contact sequence.
- Decision: Cubes 01–04 may start from coarse safe PRE_PUSH staging and are pushed toward the deep wall with a rear-face suction primary arm and a side-face suction constraint arm. At deep-wall contact, the side arm presses laterally while the former pusher holds the deep-wall constraint. Cube 05 is precisely aligned at PRE_PUSH, then inserted by one rear-face suction arm; the other arm makes no Cube contact.
- User input: Explicitly distinguished the first four dual-arm adjustable placements from the fifth single-arm precision insertion.
- Scientific boundary: Cube 05 is not a two-arm insertion test and must not be reported as evidence for a reproduced cooperative insertion controller. Cross-method results must distinguish the dual-arm fixture phase from the single-arm center phase.
- Still open: pre-push tolerances, primary arm assignment, contact-force limits, B-case perturbations and physical validation. No values are frozen by this decision.

## D005 — Isolated Cube 05 arm-symmetry probe, not a benchmark shortcut
- Date: 2026-09-30
- Classification: [EXPERIMENTAL] test fixture and [ENGINEERING] test-only arm selector.
- Decision: For the arm-symmetry feasibility probe only, directly place Cubes 01–04 at their final cells, require actual Isaac physics settle, then feed and execute only Cube 05. Run left and right from separate clean scenes. Keep the legacy controller's default `center_pusher_arm=right`; choosing left requires an explicit parameter.
- Reason: Compare whether either arm can physically perform the fifth-Cube single-arm push without spending four prior cycles on each test. This does not validate first-four placement or freeze the benchmark.
- Numerical implementation: 100 nm comparison guard at the 1.5 mm inner-side-gap boundary only, to absorb an observed 38 nm float32 serialization excess; neither the target geometry nor the material threshold changes at meaningful precision.
- Impact: Results are labeled [EXPERIMENTAL], with separate run metadata and raw log pointers. TASK01 remains IN_PROGRESS.

## D006 — Keep Cube 05 repeatability evidence exploratory
- Date: 2026-10-02
- Classification: [EXPERIMENTAL] repeated fixed-fixture trials; [ENGINEERING] read-only logging and pose-source probes.
- Decision: Record right/left 3/3 physical passes as a small-sample feasibility result only. Do not freeze a reliability number, arm-equivalence claim, or contact-dynamics metric from these trials: OMPL seed is uncontrolled, four fixture Cubes were pre-placed, and contact wrench is absent.
- Measurement rule: Final settled `/task27/cube_poses` is usable as Isaac Bridge Ground Truth for this exploratory position report, but motion-time USD and PhysX poses are not yet a synchronized measurement contract. Keep their discrepancy open as BUG-005.
- Impact: TASK01 remains IN_PROGRESS with 36 unresolved configuration fields; no benchmark thresholds, geometry or Task27 control logic changed.

## D007 — Diagnose and isolate measurement errors before benchmark freeze
- Date: 2026-10-03
- Classification: [ENGINEERING] read-only sampler/environment launcher; [EXPERIMENTAL] deterministic free-body calibration; [ADAPTATION] Isaac Ground Truth to ROS.
- Decision: Add a separate optional PhysX post-step pose/velocity channel with one simulation stamp and step number per snapshot. Reject invalid physics handles rather than falling back to USD. Keep Task27 control and legacy topics unchanged while documenting their defects.
- Reason: USD callback positions lag the physical state; quaternion extraction from the scaled Cube transform is independently wrong. Dynamic contact metrics cannot be validated from these old measurements.
- Validation: External ROS known-motion calibration at 60 Hz physics with 30/20 Hz frame updates, without contact. Explicit zero damping applies only to that calibration body, never to the Task27 scene.
- Impact: Old exploratory settled position metrics remain traceable; old yaw metrics are marked invalid for physical 6D claims. TASK01 remains IN_PROGRESS, TASK02 interfaces remain unfrozen, and no contact-force or paper fidelity claim is introduced.

## D008 — Separate collision wrench, mount reaction and contact estimation
- Date: 2026-10-03
- Classification: [ENGINEERING] same-step telemetry/buffer handling; [ADAPTATION] Isaac impulses to world N/Nm; [EXPERIMENTAL] known-load calibration fixtures and nominal full five-Cube probe.
- Decision: Calibrate collision normal/friction forces and moments separately from suction D6 loads. Use an isolated articulated mount to test reaction availability and frame/reference-point conventions, not to silently insert a new FR3 load-cell joint. Keep real FR3 raw reactions explicitly raw until gravity/inertia compensation, sign and TCP moment shift are validated.
- Reason: Suction can support 7.848 N while collision signals are zero. Actual FR3 has retained hidden-body mass; raw reactions are therefore not end-effector contact estimates.
- Numerical boundary: Calibration gates/known loads belong to the independent metrology fixture, not benchmark acceptance thresholds. No TASK01 numeric field is frozen from these experiments, and no legacy model mass or control parameter changes.
- Full-flow boundary: Normal-feed Task27 five-Cube probe uses the existing controller without pre-placing the fixture. Controller log alone establishes its actual physical completion; five feed ARRIVED flags do not prove five placements. Paper fidelity/contact topology still needs separate review.

## D009 — Validate physical reference; retain negative full-flow results
- Date: 2026-10-03
- Classification: [ENGINEERING] raw naming/model checks/metadata; [EXPERIMENTAL] axes/anchor fixture; [ADAPTATION] eventual TCP wrench mapping.
- Decision: Verify actual physics COM, no rigid-body scale in reference fixture. Test link/principal/joint axes crossed with link origin/COM/joint anchor. Final result is joint axes/about joint anchor. Explicitly invalidate earlier scaled-body inferences, preserve raw software PASS.
- Impact: Real FR3 reactions stay raw until actual joint frame/anchor, gravity/inertia and TCP shift checks. Failed asset-root startup is not a successful frame audit.
- Full flow: Record 5/5 planning-only but 1/5 physical completion, Cube 02 pre-close overshoot separately. Never widen the 0.300 mm gate to accommodate minimum 0.650 mm correction. No legacy controller fix in this read-only scope.
- Freeze: 36-field checklist is a review queue, not approved values. Keep YAML/hash unchanged, TASK01 IN_PROGRESS, TASK02 TODO; no early paper algorithm/model mass changes.


## D016 — Single-Cube scientific benchmark; legacy five-Cube flow is non-blocking
- Date: 2026-10-06
- Classification: [ADAPTATION] benchmark architecture.
- User approval: explicit.
- Decision: benchmark_v1 uses one shared Cube, dual FR3 and one carriage. The legacy five-Cube Task27 application is preserved as a later application/stress test and no longer blocks TASK01.
- Reason: the research question is tight cooperative transport plus constrained cooperative insertion, while the inherited five-Cube sequence introduced unrelated multi-object sequencing, retreat and fixture constraints that prevented progress toward paper baselines.
- Force boundary: TASK01 freezes geometry/frames/material/time/start-goal only. Isaac TCP/contact-wrench calibration moves to TASK10-IS, before P2 Isaac migration. P4 is not blocked by force sensing.
- Nominal material candidate: retain the measured effective 0.5/0.5 static/dynamic friction for benchmark_v1 candidate; P3 may later vary friction as robustness perturbation. Final freeze still requires user review.
- Historical evidence: no old result is deleted or re-labeled; old five-Cube reports remain historical evidence only.

## 2026-10-14 — D079：全文接续R0来源和协议冻结

同名已有分支同步6276f78，隔离worktree并保全五原工作树13未跟踪文件。全文8页/式1–9/Fig1–5/TableI–II已重读；找到全部六环境七作者快照，30父义务/169完整入口。旧RSS9996目标独立SE2回放全部不可达；旧PCS92解边全p0，不改旧失败/结论。
R1有限资格协议 configs/p4_full/r1_qualification_v1.json：总1800s，单构建/诊断120s，正式规划0。完整TableI22500调用/最坏6250核小时待具体预算裁决。旧P4/P2文件1282条SHA保护；只追加治理记录。源码与资产外部固定引用，不重发布未授权原文/网格。当前P4整体仍部分完成，P2/Isaac不开展。
证据：reports/p4_full_audit/ORIGINAL_FULL_COVERAGE_MATRIX.md，reports/P4_FULL_PRE_TASK_D079.md，reports/P4_FULL_SOURCE_ENVIRONMENT_AUDIT.md，reports/P4_FULL_FAILURE_ROOT_CAUSE_REVIEW_D079.md，reports/P4_FULL_BUDGET_AND_DECISIONS_D079.md。


## 2026-10-15 — P4 D079 原生六环境R1真实资格与报告归档

实测1826项=1580通过+246失败，六环境组件资格均未通过；正式规划0。保存400空间IK/40平面APC/60NR的独立分母，近似π、Comau带符号几何、RSS非真奇异和VI源码缺项分别有证据，不改判旧失败。211项全文对照和9页中文Word/PDF已生成；交付完整性20/20，不等于科学通过。1282原科学文件、1194作者文件、五原工作树及13未跟踪文件均保全。
见 reports/P4_FULL_R1_POST_TASK_20261015.md。用户在具体有限修复提案后回复“继续”，下一阶段仅在独立R2命名空间按2核小时/1小时墙时进行数值一致修复资格；原模型尺寸/基座/抓持/端点/判据不变，正式22500调用预算另审。P4仍部分完成，不启动P2/Isaac/FR3适配。

## 2026-10-15 — P4 R2崩溃接续（用户本次明确授权，非重置旧预算）

保全57未提交文件后以0792acf归档；fetch确认远程356a3b1、本地原有5未推送提交无分叉。A固定I label0/空间active arm1，同原唯一解析支、原界内全部真2pi代表，按被动L2最近且先过独立闭合/分支/界/碰撞选择；所有恢复标RECONSTRUCTED。B沿独立候选A，s2/3各1/2、原wrist-only模式1、gamma=.2，5固定seed各6请求至多32构造，冻结分支规则后执行。不得更改原模型/门/失败。预算见新配置，未启动正式规划。


## 2026-10-15 — P4 R2恢复：A端点完成、IV NR局部完成、VI严格桥仍UNKNOWN

本次用户已明确批准A同原active/原支最近周期恢复与B独立三臂资格，不能重复请求原授权、重置960/180wall/360CPU。原作者实现/我方重建/论文数学分别归因；v3仅修我方观测。VI Q2固定首成功219/643、原奇异q4/q6族、γ=.2，source .05/.35文本旁审不参与严格gate。IV新组只验证原NR固定24输入，不回填旧失败；允许原full12改变active，分支只诊断。三次同机制失败进入有证据根因审查，不盲试或缩义务。正式预算另审；211全文义务保持。


## 2026-10-15 — P4 R2接续12run：fiber组件通过、旧48真实碰撞已补齐

沿用户已批B在原剩余内做6固定fiber组件，未重复申请同一批准。新通用fiber-composite接入设计与64新节点预计较现50余额多14，须完整固定协议/源码可审查后对新增范围另行裁决；当前未运行或扩960。其他环境原PCS/NR薄整合可并行准备0solve。source SBL .05与RRT/Bi-RRT .2概率分开，VI独立重建.gamma=.2保持，不按胜负调参。当前12run自身成本合计95.365357389998wall秒/45.058033CPU秒，R2余3504.634642610002/7154.941967。VI B累计910构造、54.513982463999wall/13.327177CPU，余50构造/125.486017536001wall/346.672823CPU。旧48仅扣R2、不扣B。不得重置claim、重跑原预算或重复加cumulative。


## 2026-10-15 — 用户接续优先级：先PCS/NR真实入口，RSS解耦

用户明确要求先完成ABB PCS冻结局部资格，再验证PCS/NR原生规划入口并取得独立检查合格的空间起终点路径；随后RSS诊断解耦推进。LOCAL01已经单次完成，10/16局部边通过、6拒绝和plain/trace一致性保持，不重跑。VI 974/974耗尽，不以剩余时间追加构造。正式大规模实验须端到端资格后成本pilot再申请，22500调用及其他211项原论文义务不缩减。

首个入口选择原RRT_PCS、环境II、A01 RECONSTRUCTED端点、seed7、原main采样盒与恒true callback、原环境II range2.6/goalBias.05；solve10s，外部执行帽30wall/60CPU。单目标工程构建45wall/90CPU；完整保存路径独立离散审查120wall/240CPU、最多2048唯一原节点，所有成本保守扣原R2总帽。每阶段先独立审查、冻结提交，单次claim，无换种子/重采/修路径；当前未运行此build/solve。原helper随机IKproject返回缺陷未被三个PCS planner实际调用，不再误设为前置门，已提交POST保持，补充说明另存。首路径资格不等于连续无碰撞、正式统计、PCS优势或全文完成。P2/Isaac暂缓。


## 2026-10-15 — 原RRT_PCS取得第一条独立合格空间路径

工程85acfd5来源E2E_BUILD01成功，wall17.12737691100483/CPU23.727903；1a5b811冻结E2E01，原RRT_PCS环境II、seed7、原采样盒与恒true callback、range2.6/goalBias.05、10s单次solve实测exact非approx，solve段.016837364s，整次wall.2776374349996331/CPU.19540999999999997。4里程点、6树节点/5树边、3段原成功回溯，连接角色/branch依次(0,3)→(1,3)→(0,0)，有2次真实角色切换。使用A01 RECONSTRUCTED端点和R2几何一致数值，原始端点及native失败保留，不能冒充原作者原输入直接通过。

b4cbbff冻结完整路径后审PATH01：177/177原密集节点、176叶全部通过独立闭链、原机械限位、每边被动branch及v3对齐原离散碰撞策略，最大闭链位置3.410605131648481e-13mm、旋转4.440892098500626e-16；叶距max.04949053472601928<.05。实际354数学FK、354分支、177collision、708adapter内部FK/J、41064PQP；wall40.94035644100222/CPU1.1020530000000002。原source执行仍保留PENDING历史，独立后审新文件单独给PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH，不改写旧execution。

18execution=16science+2engineering，R2总wall343.63343315300244/CPU289.461446，余3256.3665668469976/6910.538554；VI B974/974余0，正式Table I0/22500不变。最新211项新表保前73历史列，另8列本路径实证。新V5保全审查PASS：1028旧科学文件、57崩溃文件8482891bytes、tar57成员、另5工作树及13未提交文件、旧V4均保持。

原导出随机IKproject/sample_q缺陷不在真实RRT调用链；CBiRRT activeDistance同点非零缺陷尚待版本化修复；原PQP638个BeginModel警告及原统计时间域差异保留。路径资格仅原离散策略，不保证CCD、完整实体杆件/省略碰撞对，也不证明PCS性能优势或完整论文。随后普通NR C++逐式移植/trace等价资格，与RSS解耦；大规模正式实验仍须端到端资格后成本pilot另审。全部原文211项义务保持，不P2/Isaac。详见reports/P4_FULL_R2_ABB_RRT_PCS_PATH_POST_TASK_20261015.md、最新ABB_RRT_PCS覆盖表及V5账本。


## 2026-10-15 — ABB NR单目标工程构建已完成，科学Q1尚待冻结

35246c3来源的唯一NR Q1 build exit0，BUILT_NOT_QUERIED；实际8.80554415199731wall/12.280458CPU，原45/90帽保持，没有运行binary或科学模型。7自有源和379编译器/库头前后哈希匹配，18prior execution保持。原编译缩进warning保留，未重编；详见reports/P4_FULL_R2_NR_ABB_Q1_BUILD_POST_TASK_20261015.md。

当前19execution=16science+3engineering，自身实耗合352.43897730499975wall/301.74190400000003CPU，保守扣R2；旧V5保持。随后固定II/III全64输入、同binary plain64/trace64及原Python完整观测64，另64终态物理检查，拟整项60wall/120CPU；须runner与外部watchdog独立审查、绑定实际binary/19prior、提交冻结后单次执行。RECONSTRUCTED物理NR移植不冒称作者KDL轨迹/速度，普通RBS/规划仍未通过。VI974余0，正式0/22500，211义务不缩，不P2/Isaac。


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
