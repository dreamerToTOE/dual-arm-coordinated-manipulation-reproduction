# WORKLOG

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

保留canonical mechanics/geometry；Eigen前向AD计算核、Boost50差分oracle、24未知Newton隐式步及v2首跑声明已写入。


## 2026-10-14 — P2第二阶段真实首门与数值审查交付

执行动力学资格1次，停止于DYNAMICS_WALL_LIMIT；没有重启、延长、GT/desired pose替代。独立只读核验16项通过，1023保护文件/旧P2八文件/P4工作树及前阶段P2源码数据保持。另固定4数学点FD42/one-step谱审查一次11.4869s，未运行新ODE轨迹/控制。IESEKF设计与草案测试移至reports（未实现/执行，归一化Jac门不得替换原物理门）。阶段性Word30原生公式/4图，15页PDF已目视；旧字体预览/初稿和空页稿保留，终版修分页，不算科学小修。


## 2026-10-14 — P2 stage2前置工作

六份指定资料已读取；先行报告/旧资产核对归档。新mechanics显式分离true dynamics与后续观测/估计/命令，只调用已批准G演化。独立资格将验证Eq9–12物理wrench映射、Eq16及固定settle/步长；未用控制命令生成内力曲线。


## 2026-10-14 — 用户批准后完成P2接触推导、有限形变资格与协议冻结

延续59260fa审计，用户明确选择几何一致路线；两项独立推导确定EE nulltwist lift与Log约束的唯一小矩阵解。
PRE ac9e35d先登记66case/门限再执行，run01原记录PASS；独立复核发现signed Eq9差日志/恢复负例遗漏，外部资格记INCOMPLETE，不覆盖原数据。
小修1计划先记录，保留旧66输入，再修−KΔτ/空约束标签并追加2恢复负例；模型contact_geometry.py源未改变。
临时Python路径失效导致exit127、case0；系统已装相同3.10.12/1.24.4/1.8.0，改用稳定解释器，失败另存。
51696a8同源run02 68/68 PASS；独立核对来源/归档SHA、signed fields、原输入、两种negative与单位统计。
新冻结JSON/说明保留原表参数/观测设计/seed/参考/判据，增已批几何解和模式新自由初态；数学推导原字节版及标准LaTex显示版分别保留。
本轮闭环0/物体ODE0/IESEKF0/P4新规划0/P3/Isaac/ROS0。小修累计1/3，余2；未来不重置。
本轮范围完成在冻结交付处，下一实现阶段遵冻结协议，正式Word实验部分待真实控制数据。

## 2026-10-13 — P2独立原文审计与协议设计

从用户接受的79cc871建立独立reproduce-p2-paper-audit工作树；原P4clean、旧P2八个未跟踪文件保留，未复用为完整控制器。
核对私有P2 PDF SHA0188b6be…；阅读全文八页、图1–9/表I–II，逐图核对公式括号/逆方向与图5物块属性。
调查作者网站/仓库索引/BibTeX/大学记录，未定位完整P2可复跑工程；引用[18]IKFoM固定59cfc095、GPL-2.0只读。
完成PRE-TASK与PRIOR-ASSET；旧码垛631b1f6通用日志/坐标模式已有薄适配，旧力控945e831 Task08命令wrench与双weld仅参考。
固定脚本独立审式15/22：自由滑动正号80μm/4ms，有限形变Eq22微分与右Jacobian疑点保存。两次独立只读复核确认停点，进一步限制“只改负号即可”的说法。
协议草案明确plant/观测/42维估计/控制分离、causal hB、新测量时间戳、异步Q尺度、C冻结、exp2前馈、exp4仅模型K失配、初始化与模式新恢复分量门禁。
本轮只执行1次数学审计；闭环0/P4规划0/Isaac0/ROS0/P3零。重大模型裁决前不改接触演化、不进入三轮修正。
保全清单/协议验证见results/20261013_P2_original_audit/；交付停点见reports/P2_AUDIT_POST_TASK.md。

## 2026-10-13 — P4三方法接手、全量核验与交付

主工作树保留task06-is-a-p4-scene-adapter及5个未跟踪日志。fetch指定两分支，
发现独立reproduce-p4-three-methods已经存在且以d5b5096为祖先，未重置/重建或覆盖它。
依次阅读最新D065与必读文件，重读P4八页、原图/表和外部CKCplanning固定909bd72；
核对旧631b1f6 shared_object_planner只作参考。已有协议6d64b26早于实现与三轮修正。
131个未提交P4成果按SHA256保全并提交219a8a7，既有60统计/3重复未重跑。
复核17项数学/接口检查；只读核对63个规划原件、561旧文件和9科学来源。
新增标准库可移植核验器，用独立线段距离检查3312个成功路径点；不导入规划/IK/模拟器。
完整重复缺口、零RSS合格随机奇异点、PCS最终单划分、E1路径未变都保留，没有补数据或扩大预算。
原18页报告全部页面检查，另存正式文件名，仅移动图9图例和换页脚，正文XML/16公式/10图不变。
新增原文审计、依赖清单、交付说明和六份记录。源码/参数/旧NR/Task26/Benchmark不改。
三次科学修正分别为41689ef、17202df、3d51ca0；预算3/3已用完，交付后停止等审查。

## 2026-10-12 — P4 paper-first中文Word交付（报告层，不重跑）

fetch指定规划branch/commit，独立worktree `dual-arm-coordinated-manipulation-p4-report` 和
branch `report-p4-paper-first`；原A分支及5个未跟踪日志未动。先读当前治理/原文索引/报告格式，
六份本地资料SHA核对一致，再全文读P4八页/范例；协议266de05先提交。
三项独立只读审计核对数学、原文忠实性、实际规划/执行审查证据。
新增存量读取出图与Word生成器，未导入科学执行模块；只读18原gzip、9对确定性、
293历史精度、194+293投影记录、1869q及闭链/余量。中文Noto字体/16原生OMML、10图，
LibreOffice独立profile生成23页PDF并检查实际页面。报告层修正根节点null读取、图形指数字体、
净变化绝对值/坐标映射措辞和空数学基底占位；不改原记录、模型或科研结论。
报告提交待用户审查，原FAIL/PARTIAL/Benchmark草案保留；不Isaac/ROS/新实验/自动P2。
[报告交付](../reports/P4_REPORT_POST_TASK.md) · [派生数据说明](../reports/p4_report_assets/README.md)。

## 2026-10-12 — TASK06-IS-B0 固定路径与旧执行条件审查

从f0a57c2继续原A分支，保留5个旧未跟踪日志；fetch确认远程基线一致。
先读治理/任务/复用/P4/Benchmark、旧执行来源，提交上传c20c381事前诊断协议。
只新增saved-data分析/图表与7合成测试，e1a2e22；并行只读审计旧同步、赋时和来源。
单次正式分析run01完成14关节余量/行程/反转、完整CSV与6张PNG/SVG，无原路径变更。
定位index860左J4逼近上限.236039°，同处11关节反转/双树汇合，L2路径6.4倍端点直线
诊断参照（不把直线当合法路径）。旧到位容差大于余量且非全程上界，判执行准备不满足。
全部25旧artifact/620source/94树边/1869点资格一致；新增数据记录source与artifact hashes。
审计原v/a/持件/起点缺口，未生成时间轨迹/新执行器，不运行Isaac/ROS服务/命令或重规划。
报告、六项记录/入口更新后GitHub交付，停止等待审查；不自动独立改进/B/C/TASK07。

## 2026-10-12 — TASK06-IS-A 新独立名义输入与合格离线路径交付

按用户第二阶段指令重读治理/原接口和源资产，以7bae83a继续原分支，保留5个旧未跟踪日志。
先提交/上传20fe06d PRE-TASK/PRIOR-ASSET及v2固定预算；旧Task26场景/成熟控制链不改。
薄适配原FCL世界输入/只读组合readback，直接现成KDL-LMA造端点，原C/Jc/NR/RBS/双树
不改。预编译KDL imported-target/JSON类型问题仅软件修正；源码c88a80c。
run02因启动PYTHONPATH覆盖丢ROS Python包而停止，未IK/搜索；只读诊断确认一次命令修正。
run03来源/模型/world资格通过，各端点第0候选即合格，唯一seed7搜索成功后停止。
1869点独立约束/限位/连续性/FCL和94保存树边验证通过；原完整19MB搜索JSON无损gz，
失败、完整14q/TCP/Cube、原生world/ACM/资源、protocol/source/artifact hashes齐全。
15接口+72TASK02+4数学目标PASS；598旧文件/8mesh/4oldassets不变，旧报告/负例不改。
记录/任务/入口更新，GitHub交付后停止；没有Isaac/ROS服务/命令/Benchmark定稿/B/C/TASK07。
[交付报告](../reports/TASK06_IS_A_NOMINAL_SCENE02.md)。

## 2026-10-12 — TASK06-IS-A 单轮只读来源审计与薄接口交付

保留原5个未跟踪日志，获取规划分支并从eb858651建立task06-is-a-p4-scene-adapter。
完整阅读当前治理、TASK03–06、固定旧Task26/模型/桥接/同步执行与历史两件证据；
先提交任务前复用审查及锁定协议462e6b1，再提交原接口调用与数据门禁a7223e3。
唯一source run因Task26 Y±.314与历史world±.303不同拒绝，立即停止科学验证；
没有新IK、抓取拟合、改world后重跑或搜索。实际持件端点与完整两件world也未确认。
独立编译与合成回归一次通过；新适配接口当前为未完成场景规划验收的骨架，
不报告原生模型/FCL加载或合格路径。保存失败原始日志、软件输出资格、静态参数读回，
更新六项记录及入口。全部成熟部件/原结果/Benchmark不改，旧未跟踪文件不提交。
TASK06-IS-A部分完成；交付后停止，未启动B/C或TASK07。
[本轮报告](../reports/TASK06_IS_A_SCENE_ADAPTER01.md)。

## 2026-10-12 — D055 总路线修订（文档范围）

用户明确要求五篇论文的算法逐篇进入既有 Isaac Sim 场景，P4 先补场景适配、执行与阶段对比三个关口。新建独立规划分支，仅更新路线、执行规范、任务卡和决策记录；无新算法编译、规划/仿真/机器人实验。TASK06 完整协议仍部分完成，Benchmark 仍草案。详见 [路线](REPRODUCTION_ROADMAP.md)。


## 2026-10-12 — TASK06 scoped review recorded; no implementation or experiment

Base74d4276, same task06branch. Read governance/active task/current evidence;
documentation-only pretask, no replacement infrastructure. Record explicit D054
core softwarePASSCANDIDATE versus overallPARTIAL, add separate unapproved P4
obstacle evaluation backlog. Preserve old report/protocol/rawresults and all prior
negative evidence; no source/parameter/model/scene/ACM/Benchmark modifications.
Only saved-evidence hashes, result inventory, document links and Gitdiff checked;
40artifacthashes match,18calls/9pairs/4NODE_LIMIT/two553node148edge successes retained.
New planning/IK/FCL/physics calls0; no test-suite reexecution or TASK07. Stop after
documents-only GitHub commit, leave5unrelated untracked TASK01 logs untouched.
[Review / POST-TASK REPORT](../reports/TASK06_REVIEW_CLOSEOUT.md).

## 2026-10-12 — TASK06 fixed scientific suite complete; acceptance gap preserved

Source29a9d5c compiled,72Python/CTest4of4 and all realTASK03–05 regressions pass.
Exactly3scenes×3seeds×2repeats:14SUCCESS/4NODE_LIMIT; all9repeat pairs exact.
Genuine553-node obstacle path found twice for20261012; otherseeds fixed600-node
stops, no retries. Direct obstacle connector first fails unchangedTASK05 locality
guard (.0869493>.020rad); recordTASK06PARTIAL rather than retunefixture/criterion.
Full sampled/projection/RBS/FCL/parent/densepath traces losslesslygz preserved with
rawhash/length; negative build01 retained. Read-only saved-evidence audit verifies
40artifact/35source/23rawgzip/18payloadhashes,536protectedfiles/8meshes/4oldassets
unchanged during run. Reports/task/status/records updated for stop-for-review,
no additional scientific experiment/code tuning. OriginalprecisionFAIL retained;
noIsaac/services/Task26/model/ACM/Benchmarkedit/TASK07. Git staging explicitly
excludes5unrelated historical untrackedlogs and generatedbuild/install.
[POST-TASK REPORT](../reports/TASK06_CONSTRAINED_RRTCONNECT01.md).

## 2026-10-12 — TASK06 compile-only failure retained; explicit conversion fix

First suite invocation `constrained_search01` stopped at C++ harness compilation:
JSON→Eigen initializer-list conversion and JSON-key overload ambiguity. No real
planner/FCL trial was run. Evidence/result remains PARTIAL; sourceba20c98 retained.
One evidence-based software fix makes numeric/key conversions explicit, unchanged
planner/protocol/model/guards. Also persist the predeclared deterministic payload,
repeat equality and SHA256 fingerprint rather than only in-memory comparison.
Recompile and execute the still-unrun fixed scientific suite; no seed/scene tuning.

## 2026-10-12 — TASK06 primary audit and precommitted fixed engineering protocol

Read governance/active task/P4/reuse/benchmark docs and pinned631b1f shared/FCL/
Task16 assets. Author909bd72 NR grow loops101/501 and ambientNN→steer→NR→RBS
audited, no upstream code imported. One fixed suite, seeds7/41/20261012×2×3scenes,
fixed private mid-transport BOX, endpoints stored0/1/100; limits fixed in877decd
before experiments and uploaded. Thin adapters expose existing native bounds/
private-box insertion only. New search/orchestration unit tests compile and pass
2757 synthetic assertions independently; not actual FR3/FCL acceptance. Real suite
pending. No scientific threshold/Benchmark/old source edits or runtime launched.

## 2026-10-12 — Resume interrupted TASK05 report/GitHub handoff only

User sayscontinue; retain original offline scope, no newtask/runtime authorization.
Re-readgovernance/status/task/report; currentbranchtask05-p4-local-connection with
testedHEAD1387808. Existingrun01/run02 artifacts valid, run02allsourcehashesmatch;
run01twopre-fixhashes correctly refer toe335e72. Independent read-only delivery
review compares counts/contacts/logs/links. No newexperiment/code or oldasset edit.
Stage onlyTASK05docs/report/tworesultfolders, preserve unrelated olduntrackedlogs.
Submit taskbranch thenSTOPforreview; TASK06/physics not started.


## 2026-10-09 — TASK04 review accepted; bounded TASK05 offline connection delivered

Base5d41869; newtask05-p4-local-connection branch. Read governance/reuse/card/full
P4/pinnedsharedObjectPlanner+conflictdetector. Main pretask/priorasset audit preceded
edits; D050 protocol committed e308a71 before experiments. PaperRBS selected,
not independent global-alpha projection; unchanged TASK03/04 sources reused.
Thin private native FCL adapter excludes old self/world filters and ACM expansions.
Parallel independent code/paper review and unit/backend implementation; all fixed
acceptance runs orchestrated by root, no controls. Endpoint NaN/cutoff/prefix trace
issues fixed before first run, not numerical protocol changes. e335e72 run01allPASS;
1387808 only uses hasLinkModel for worldbody classification and removesindentwarning;
run02allPASS, exactsameq/status/prefix. Both logs/negatives retained. Native30shapes/
16meshes,10positiveedges/3negativeedges,14NRcalls/35FCLchecks perrun.72/93/108/300
regressionchecks+435realFDconfigs PASS; oldprecisionFAIL retained. FullJSON traces,
model/ACM/environment provenance and505protected/8mesh/4legacyhashes unchanged.
No Isaac/ROS services/Task26/Benchmark edits or TASK06; parentTASK02IN_PROGRESS,
measurementDDEFERRED, BenchmarkDRAFT. DeliverySTOPforreview, noextra instrumentation.
[Report](../reports/TASK05_LOCAL_CONNECTION01.md).

## 2026-10-09 — TASK03 review closure and bounded TASK04 offline projection

User baseline91422f4, same task03 branch. Read governance/cards/original P4 and
pinned predecessor shared-object assets; reuse C/Jc/FK and TASK02 logger. D047
records reviewed math PASS versus original precision FAIL; D048 predeclared and
pushed15951f7 before experiments. Parallel independent math/code review and test
implementation, root unified finite execution. Full-step SVD with explicit failures,
rank/limits/proposal/acceptance/cost trace, no fallback or second kinematics stack.
Build-only01 ABORTED(PYTHONPATH/legacyroot) and02 FAILURE(imported-target scope)
preserved; dependency/launcher corrections only.03all8commands0:72TASK02/93TASK03/
108TASK04checks,435FD configs PASS;194required +293diagnostic converge,max3updates,
repeatqdiff0. OriginalFAIL219/293 remains.477protectedfiles/4oldassets unchanged;
complete outputs/source hashes, physicaltime null. No Isaac/ROS services/Task26/
IK/FCL/Benchmark/TASK05/06. TASK04PASSCANDIDATE, TASK02IN_PROGRESS, BenchmarkDRAFT.
Stop for review. [Report](../reports/TASK04_NR_PROJECTION01.md).

## 2026-10-09 — TASK03 offline rigid-chain mathematics; stop PARTIAL

- Base36c95ab; created task03-p4-closure-constraint. First audit commit9b59289 was
  pushed: close TASK02-D PARTIAL/DEFERRED, no Observer and no freeze; API availability
  distinguished from qualified native time/reset. Not an offline algorithm blocker.
- Read governance/reuse/task/P4 and complete original shared-object planner/model/tool
  sources; consulted author full paper. Prior-asset and pre-task reports preceded edits.
  Reused original model/FK and accepted B RunLogger; no old top-midpoint gates imported.
- Implemented pure Eigen closure/Jc with fixed-transform direction, correct lever arms,
  world geometric reference and rigorous SO3 chart, plus thin offline MoveIt-core adapter.
  No ROS context/node, MoveGroup/service, controller, IK, collision query or projection.
- Independent math/source reviewer confirmed signs/frames/fidelity. Existing293 q/FK
  records (292unique) kept unchanged; exact model snapshots hash-match ignored originals.
- Initial unsourced build failed ament dependency/library resolution; sourced installed
  Humble only, then existing predecessor install for mesh URI resolution. No dependency
  installation or install-file edit. First mesh-warning mathematical run retained;
  final log contains normal model loading, no mesh warnings. Existing incomplete
  predecessor package setup warning preserved as environmental information, not repaired.
- Final saved regression:72 A/B/C tests,93 math checks and435 model derivative configs
  pass. Original fixed-grasp precision does not:219/293positionrecords exceed5e-8m,
  max4.35027826256e-7m. No threshold/IK/G adjustment; algebraic test-only fixture is not
  a substitute. Typed result INCOMPLETE and independent TASK03 status PARTIAL.
- Formula/frame/provenance/report/source/log/result records prepared for scoped GitHub
  delivery. Benchmark/A/B/C/foundation hashes unchanged; unrelated old raw logs preserved
  and excluded. TASK02 IN_PROGRESS / Benchmark DRAFT. Stop for review, no TASK04.

## 2026-10-09 — TASK02-D availability audit recorded; enter offline TASK03

User accepts closing the local4.5 audit asPARTIAL/DEFERRED. Record actual installed enum,
managerregistration, explicitpostbinding, native getters/CoreNodes clocks and missingphase/reset/
USDguarantees; noObserver, simulatorimport/runtime or oldTask26 edit. Root implementation starts
from36c95ab onnewtask03-p4-closure-constraint. Re-read governance/reuse/TASK03/P4; independently
audit pinnedoldsharedplanner+side-toolmodel, retrieve authorP4fulltext. Announce PRE/PRIOR-ASSET
checks beforeediting; preserve unrelatedrawlogs. Newscope isclosed-chainmath/offlineFK only,
not projection or Benchmark. [D audit](../reports/TASK02_POST_STEP_API_AUDIT.md).

## 2026-10-09 — TASK02-C one bounded offline math/measurement implementation

Read current governance/TASK02/reuse map and pinned631b1f Task14 cpp/doc plus Task16 cpp before coding; fetch confirmed basec7b33b1 equal to origin. Main preserves exact Task14 initial drift and sample-RMS definitions; legacy thresholds/runtime are reference-only. New common math/evaluation and measurement dataclasses reuse existing A/B types/codec without edits. Parallel read-only audit/review and two-file synthetic test work; review corrections confined to new C channel-order/vector/end-sample guards. Two independent mock-format decoders, no platform imports; synthetic and real-declared test-double branches explicitly separate. All72A/B/C testsPASS, example JSON exclusively created and decoded, source/config/old4asset hashes verified; unrelated raw logs untouched/excluded. Save tests/metadata/scope/readback and six records/report/API/task/start/README updates. No physical/software runtime stack launch, old source or benchmark change. Publish this slice only; TASK02-C PASS CANDIDATE, parent IN_PROGRESS, Benchmark DRAFT; stop without TASK02-D/TASK03. [Delivery](../reports/TASK02_METRICS_MEASUREMENTS01.md).

## 2026-10-09 — TASK02-B one bounded offline exchange/logging implementation

Re-read latest governance, TASK02 spec and POST_TASK01_REUSE_MAP; fetch of the active origin branch confirmed no divergence. Main fully inspected pinned631b1f task_event.hpp, task_trajectory_candidate.hpp and task16_planning_benchmark.cpp before coding. Classified semantics/output patterns THIN_ADAPTER and TASK02-A saved snapshot TEST_ORACLE; old execution/thresholds REFERENCE_ONLY. Implement stdlib immutable typed command/event/result/run contracts, strict deterministic wire codec, planned-only legacy event adapter and single-writer file logger. Independent read-only review led to minimal causal-command/argv/persisted-metadata/empty-exception/qualification guard corrections within the same offline cycle, not another runtime attempt. Final33tests pass; retained-failure example decoded from actual files, seed UNSET, synthetic observation explicitly labeled and historical state unpromoted. Temporary intermediate example was regenerated after metadata contract completion; no old/user evidence removed. Re-check old accepted4hashes/worktree and benchmark SHA; no execution stack changes/invocations. Update six records, task/start/README/common docs and report; publish only owned files on task02-minimal-foundation-interface. Stop at PASS CANDIDATE, parent IN_PROGRESS; no TASK03. [Delivery](../reports/TASK02_EXCHANGE_LOGGING01.md).

## 2026-10-09 — Accept foundation; minimal TASK02-A in-place state adapter

Recorded explicit user acceptance of foundation PASS CANDIDATE with no formal Benchmark freeze; subsequent “继续” advances minimum migration/interfaces, not another physical qualification. Main re-read governance/task/reuse maps/P4/benchmark and inspected pinned old trajectory/event, Task26 scene and Task16 output patterns before coding. Auxiliary inventory agent was unavailable due service usage limit; main completed the source check directly. New `common/interfaces` draft and `platforms/isaac_ros2/foundation` read-only adapter bind known identities/SI/xyzw/measurement sources; explicit raw/local asset provenance and unavailable clocks prevent fabricated scientific synchronization. Old source/GUI/controller untouched. Offline14tests PASS; strict asset check4/4 and stored final snapshot CLI conversion exit0. Created `task02-minimal-foundation-interface`; six records/README/start/task/report updated. No robot/suction/rail/ROS/Isaac command; parent TASK02 still IN_PROGRESS, formal command/logger/metrics/seed and live post-step binding deferred to next slice. [Delivery](../reports/TASK02_FOUNDATION_INTERFACE01.md).

## 2026-10-09 — Complete bounded GUI physical acceptance; second run PASS

Using only approved5ed0c96 and originalGUIscene→Play→bridge→MoveIt, ran2freshpreflights/2physicalinvocations undernewmax3permission. Firstfullbatchfailed atshallowleftjointsettle despiteactualdeepCubePASS; preservednegative and originalpausefeedback. Second progressesbeyondsameguard, completesbothfulloriginalCubechains/sidecompaction/release/retreat andjointHOME; controllerexit0/originalbatchPASS. Finalactualpositions/q/TCP/base/rail/SG/callbackhealthsavedbeforeownedlaunchCtrl-C130; GUIpreservedPause; originalsource/binary/scene/bridgehashes unchanged/isolatedoldworktreeclean. Stopafter2/3withoutthird orrepair/freeze. Updateall6records/TASK01/README/report/metadatas andpublishrawlogs, retainintermittentfirstfailureandlegacymeasurement/FCLlimits. TASK01PASSCANDIDATEonly. [Review](../reports/TASK01_PREDECESSOR_PATCHED_RUNTIME_REVIEW.md).


## 2026-10-09 — Begin authorized patched-predecessor GUI retries

Read governance/D041/activeTASK01/reuse/source scope, independently review reset/shutdown safety. Published pre-run scopeeade5de before completion; existing GUI39508/8226, no standalone. Original scene/bridge hashes and actualbinary match approved5ed0c96; original overlayYAMLcmp passes. Attempt1 fresh reset/preflight0, physical1: actual deepCube side-chain/backstop gate and full physical per-Cube PASS, shallowactualjointsettle25s/max3.931858deg fail beforeclose, no finalHOME. Preserved negative raw log and pause snapshot, SGbothOPEN/bridgeerrors{}/rail.75; no exactcollision proof. Under latest max3 runtime authority, started unchangedfreshattempt2 with preflight0; no implementation iteration/threshold/drive/geometry changes. Final outcome pending, TASK01PARTIAL. [Run review](../reports/TASK01_PREDECESSOR_PATCHED_RUNTIME_REVIEW.md).


## 2026-10-09 — Fix two audited software issues without rerunning Isaac

Read-only old Task25/26/27/code/log/history audit found prior same backstop segment8 failure and6289f2b downstream candidate filter hidden from Task26 by macro. Main/independent installed-header audit also confirmed dangling Eigen Block return in original FK checker; historical root trigger remains unproven. User approved minimal correction. In isolated pinned-source worktree created `task01-foundation-side-preflight-fix`, changed only controller (+7/−6) and committed/pushed5ed0c96. No original side-suction branch overwrite or current runtime-fixes source edit. Offline regression uses actual extracted distance function and type double/ASAN, with source/macro/constant scope checks;3testsPASS. Build originalTask26 and compatibilityTask27 targets, no simulator/model/control invocation. Record authorized override and software-only evidence; no automatic physical retry/foundationPASS/FROZEN. [Report](../reports/TASK01_PREDECESSOR_SIDE_PREFLIGHT_FIX.md).

## 2026-10-09 — Sole original Task26 qualification completed; negative result preserved

Audit published before runtime atbb18099. Isolated pinned631b1f worktree original Task26 target built once; resolved launch/model/helper/YAML files byte-checked against pin. Operator Stop/New→original scene→operator manualPlay→original bridge→original MoveIt, then one planning-only PASS and one physical FAIL. No predecessor source patch or reproduction runtime. Original bilateral transport/release/rail+.100/world rebuild/rear regrasp/16-slice push completed; side-compaction preflight exhausted original FK gate candidates, so no second Cube or HOME. Main and independent read-only review distinguish planned deviation from actual collision/motion. Save complete logs/provenance and original feedback snapshot; original safe abort opens both SG, then pause GUI and interrupt owned ROS launch, no reset or rerun. Update six records/TASK01/README; PARTIAL/NOT_QUALIFIED, await new bounded authority. [Report](../reports/TASK01_PREDECESSOR_FOUNDATION_RUNTIME01.md).

## 2026-10-09 — Pinned Task26 full audit before foundation runtime

Main directly read mandatory pinned document/scene/bridge/5444-line controller, original launch/model/SG/planning/rail/push/HOME/config closure; independent read-only audits cross-checked indexing and dependencies. Source pin631b1f differs from current old worktree controller. User accepts two Cubes, so select original batch1 unchanged; no selector/scene/bridge/controller implementation. Record raw module hashes, original two targets, config fallback risk, original planningScene mutation/table duplication, optional diagnostics and measurement limits. Existing GUI/executor observed, paused historical Stage detected; operator confirms Stop/New prerequisite after request. Only documentation changes and read-only checks so far, runtime0/1. Submit audit before isolated build and original lifecycle. [Report](../reports/TASK01_PREDECESSOR_FOUNDATION_AUDIT.md).

## 2026-10-09 — TASK01 restart design

Per user instruction, created branch task01-legacy-scene-foundation and archived the prior active TASK01 specification. Reframed TASK01 as a direct qualification of the predecessor Task26 scene/runtime with one independent Cube only.

No simulator or ROS run was performed in this design iteration. No old runtime code was copied or rewritten. The active task now requires Codex to read the pinned predecessor source itself, use its original GUI → scene → Play → bridge → MoveIt → executor lifecycle, make at most a selector-only one-Cube reduction if needed, and run one complete mature Task26 Cube flow before any new foundation implementation is considered.

## 2026-10-09 — Complete the one approved existing-GUI handoff, no runtime edits

User reports normal GUI/executor ready; read-only preflight verified PID39508/STOP and approved executable/config/binary hashes. Sole scene load, operator manualPlay, sole bridge load, saved bilateral-held PRE, sole unchanged external ROS handoff driver. Original safe/FCL gates, bothrails.650→.750, full composed expected/readback refresh0/.100 and rightrear regrasp establish candidate8967. No source/build/config/physics/ACM/IK threshold change or new tests. Offline independent review confirms native state/contact step alignment, candidate same-step contact and raw CDR lengths; save complete compact evidence and hash-index local raw22MB/1.26MB streams. Record unavailable native anchor/nonzero speed/derived TCP limits and move_group shutdown−11 after driver0, no diagnosis/rerun. Runtime stopped1/1, no TARGET/reset/A/force/P3/PASS/FROZEN; six records/TASK01/README updated. [Outcome](../reports/TASK01_EXISTING_GUI_BOUNDED_RUNTIME01.md).

## 2026-10-09 — Cross-repository reuse audit for TASK02+

Reviewed the current reproduction task map against the predecessor `side-suction-palletizing` source, excluding already-handled TASK01 work. Identified reusable engineering assets for common interfaces/metrics, P4 planning scaffolding, P2 execution/geometry monitoring, P3 position-only rear insertion, P5 platform/collision scaffolding, P1 isolated MoveIt sandbox/cache validation, and unified benchmark reporting.

Added `docs/POST_TASK01_REUSE_MAP.md`, made the PRIOR-ASSET CHECK mandatory in `AGENTS.md`, and linked it from `CODEX_START_HERE.md`. No simulator, ROS, controller, benchmark or baseline algorithm was executed or changed. No paper-specific algorithm was imported.

## 2026-10-09 — Sole existing-GUI runtime authorization: prerequisite check only

Re-read governance/current task/P4/benchmark and inspected git/critical hashes. No code/build/config change or tests; approved bbe9784 adapter source remains byte-identical. Process/listener preflight plus independent audit found no running Isaac/Kit GUI or existing8226 executor. No scene, Play, SG, rails, ROS driver or physical samples. Saved preflight report/metadata and records, waiting for operator prerequisite; allowance0/1, no startup fallback or repair. [Record](../reports/TASK01_EXISTING_GUI_BOUNDED_RUNTIME01.md).

## 2026-10-09 — Reuse Task26 scene → Play → bridge in an existing GUI

Read mandatory governance/current TASK01/P4/benchmark/reuse records and remote-verified Task26@631b1f sources; wrote pre-task software-only scope before editing. Added a thin current-Stage scene loader, manual-Play bridge entry and asynchronous session adapter, retaining original constructors, SG and C++ fixed handoff. Native callbacks replace standalone manual simulation; Stage/token gates precede physical writes, existing halted/error protocol preserves last native stamp on failure, and external controller ownership is explicit. No new grasp/push/FCL/readback algorithm, benchmark geometry/physics/ACM edit, image-core investigation or runtime. Independent source audit plus pure AST/mock tests; preserve eight immutable hashes and prior logs. Complete README/records/report updated; TASK01 PARTIAL, new physical evidence absent. [Delivery](../reports/TASK01_EXISTING_GUI_LIFECYCLE_ADAPTER.md).

## 2026-10-09 — Authorized startup-only GDB capture completed

User “可以” approved one visible native-stack capture,180s hard cap, stop before physical/control/handoff. Re-read governance/task/P4; wrote pre-task scope; added thin hash/AST/main-only125 exit launcher and clean-GDB/SDK-inferior wrapper, no original harness edit. Five pure launcher tests/shell syntax/two independent read-only reviews PASS. Source944422d frozen before sole invocation. FirstSIGSEGV captured in OmniGraph worker with image-core/exec/TBB callers and heap warning; no exact corrupting cause. Saved full stack/log/input/guard/metadata, GDBkilledinferior, no further run or fix. ~110s engineering log interval; owned PID/PGIDs absent. Eight runtime hashes unchanged. TASK01PARTIAL, no physical safety/READY/FROZEN;1/1 consumed, six records/TASK01/report updated. [Result](../reports/TASK01_STARTUP_NATIVE_STACK_CAPTURE.md).

## 2026-10-09 — Finalize previous read-only diagnosis records

User requested continuation; resumed only the pending final review/commit/push of2026-10-08 existing-evidence diagnosis. No new diagnostic iteration, runtime, debugger, tests or source/config/binary edits. Retained evidence dates/hashes, added publication completion date; no budget reset, READY claim or FROZEN. [Completed findings](../reports/TASK01_STARTUP_READONLY_DIAGNOSIS.md).

## 2026-10-08 — Read-only startup diagnosis, no rerun or implementation

One bounded existing-evidence diagnosis approved; read governance/task/benchmark/paper, then two parallel read-only core/call-chain audits. Main verified selected Kit markers, exact prior PID Apport records and existing Asia/Shanghai kernel line. Corrected console-only boundary: SDK init/ROS bridge had completed. Kernel points to correlated OmniGraph worker fault; no stack/causal fix. Apport refused saved reports for bundled Python, so no usable core. Preserved selective verbatim excerpt/SHA and metadata; no environment/core secrets published. Runtime/config/binary unchanged; no simulator/ROS/debugger/test/fix or global core setting. Diagnosis now stopped1/1; six records/TASK01 updated and published, task remainsPARTIAL/noREADY/FROZEN. [Report](../reports/TASK01_STARTUP_READONLY_DIAGNOSIS.md).

## 2026-10-08 — Additional unchanged retry02, no implementation edits

Reread governance/current TASK01/reuse/benchmark/paper; announced one-invocation interpretation of “再次尝试”. Read-only audit verified identical eight hashes and original bound/scope. No runtime/source/config/binary/launcher edits, rebuild or tests. Sole visible GUI at d8d0096 with new evidence directory/reset0 again nativeSIGSEGV afterapp-ready; exit1 before180s. Captured complete log/input hashes, no scientific post-step or readback data. New1/1 used; no startup diagnosis/repair/extra launch. Offline result/process checks and six records/TASK01/report updated; preserve old logs. TASK01PARTIAL, noREADY/TARGET/FROZEN; escalate for separately budgeted startup diagnosis. [Run record](../reports/TASK01_UNCHANGED_RETRY02.md).

## 2026-10-08 — Readback normalization implementation and sole retry result

Limited change: composed object×primitive SE3 validator, fixed1e-8m/rad/1e-12dims, lossless CDR/full-field evidence before verdict, strict pure tests and launch output-directory parameter. New header/driver/launch only; immutable benchmark/GUI/bridge/primitives hashes unchanged. Preparation compile/self-test and pure7-entity launch construction exit0; independent scope audit PASS. Source committed08c34b8 before runtime. Sole180s-capped visibleGUI command reset0 died nativeSIGSEGV just after app-ready; wrapperexit1, no physics/readback/handoff records, only hashed inputs/log. Budget1/1 consumed, no second launch/startup fix, no TARGET. Read-only evidence/process audit; complete negative result and six records updated. TASK01PARTIAL/notFROZEN, startup root undetermined; STOPFORUSER/ENGINEERINGESCALATION. [Full record](../reports/TASK01_READBACK_NORMALIZATION_RETRY.md).

## 2026-10-08 — Readback normalization repair preparation

Reread AGENTS/governance/STATUS/currentTASK01/D039/reuse/benchmark/P4; pre-task report delivered. New authorization permits only composedworldshape message validation plus full raw evidence, one bounded retry, no geometry/handoff/safety-condition change. ImmutableYAML/GUI/bridge/primitives hashes recorded. Implement validator/puretests/evidence-path launch wiring; no runtime yet, additional0/1. Plan onevisible180s cap to INSERT_READY, no repeatedreset/TARGET. [Protocol](../reports/TASK01_READBACK_NORMALIZATION_RETRY.md).

## 2026-10-08 — D039 integration01 actual STOP, no repair/retry

Onevisible180s-capped run sourceee51470; normalSDKwarm-start→recordedPRE14q→bothSGCLOSED→bothOPENconfirmed. Initial worldapply/readback atshift0 rejects task01_table. Bothbasesremain.65, no safeplanning/rail/rear/READY/reset/TARGET.351nativepoststepstate/contactrows and selectedPREstate/stoplogs saved; originalmass/friction/geometry/physics retained. Read-only installedMoveItheader identifies shape/objectpose normalization as guardfalsefailure risk, not proven actualdifference (rawobjectsnotlogged). Driver1, wrapper0 despitefailure, cleanupmove_group−11; ownedprocessesabsent. Integrationbudget1/1consumed, STOPFORUSER/nofix/relaunch. [Full report](../reports/TASK01_FIXED_HANDOFF_INTEGRATION.md).

## 2026-10-08 — D039 fixed handoff preparation

User approved both rails .750 candidate; base_at_rest .650 unchanged. Added candidate/required capture fields and pinned-source single-Cube SG/rail, C++ safe/rear/FCL driver, minimal MoveIt launch and visible post-step recorder. Source audit precedes code; Task27/five-Cube/main not executed. C++ compile/self-test, Python syntax/launch construction and8 pure mock tests PASS. No physical launch yet, budget0/1; one≤180s attempt scheduled. No tool/wall/ACM/friction/drive/controller-force modification. [Files, provenance and planned command](../reports/TASK01_FIXED_HANDOFF_INTEGRATION.md).

## 2026-10-08 — Read-only old-asset audit and minimum staged integration plan

Safely fast-forwarded task branch to cloud `c525fc1`; re-read mandatory governance/status/D039/reuse/task/benchmark/paper files. Two parallel read-only audits checked shared hold and rear insertion against predecessor Git objects `631b1f…`; source worktree remains runtime-fixes/d4b290c, unmodified. Root independently checked original right-pusher/rail/seat log lines and hashes.

Mapped 19 source/report assets into a hashed manifest. Preserved a byte-verifiable 11-line excerpt from `full_run_606_optimized.log` (original SHA2a286c…); raw run lacks build SHA and is historical only. Identified both .750 rail station, actual14q+base/attachment snapshot requirement, legacy center index4/neighbor dependencies, ignored OPEN return in normal release, old timestamp/friction differences. Audited existing live post-step sampler for thin reuse, not a new measurement framework.

Wrote [audit/plan](../reports/TASK01_PRIOR_PROJECT_REUSE_AUDIT.md), linked TASK01, corrected release→left park→right rear order in reuse map, updated six records. **No code/config/model/physics edits, no ROS/Isaac/IK/build/reset.** Existing +.100 rail handoff is a recommendation requiring user review, not an approved benchmark state. Integration attempt budget used0; no restart of exhausted parity. Final file/source/link/hash checks and publication are records-only.

Validation actually completed: diff whitespace, manifest JSON, YAML DRAFT/one-Cube/staged order/pending state assertions, raw-excerpt cmp, unchanged config/sampler SHA and source tracked-worktree checks all exit0. These are definition/provenance checks, not physical acceptance.

## 2026-10-08 — D039 benchmark topology correction / predecessor reuse audit

Reviewed `dual-arm-embodied-palletizing@side-suction-palletizing` Task24, Task26, Task27 and Task11–13 records plus Task26 source behavior. Confirmed prior physical workflow:
bilateral side-suction transport → release → one-arm -X rear regrasp → segmented +X insertion → exit. Task27 center insertion defaults to the right pusher and parks the helper outside the insertion workspace.

No simulator experiment or algorithm implementation was run in this iteration. Updated benchmark/task/roadmap/P3 specs and added `docs/PRIOR_PROJECT_REUSE.md`. Archived the pre-D039 TASK01 spec so parity/bilateral-TARGET history is not lost.



## 2026-10-08 — One command-only rerun; explicit TARGET safety failure

Re-read local governance/start/status/currenttask/benchmark/P4 documents; issued PRE report and delegated read-only launcher/evidence audit. User granted additional1/1, four states only, no reset. Records checkpoint `a10db77`; existing7pure classification tests passed. **No harness/launcher source, geometry, model, physics, ACM or IK modification**. Pipe supplies3 continuation tokens then fourth stop at the existing barrier; default GNU timeout groupKILL120s covers startup/close. HarnessSHA `ab174884…` unchanged.

START/PRE/state196 passed original safety guards. TARGET immediately stopped on leftlink7/deepwall separation−3.016427159mm; unclassified right raw contact−3.016243223mm in the same step. Fourth stdin stop, TARGET overlap queries and all resets were not reached. Four post-steps/.0666666701436s; native clock agrees. Selected raw JSON copied byte-for-byte with SHAs; six input hashes and scene_audit match the previous attempt. No further replay or diagnosis after the collision.

Original app.close started at logged13.108s but its resource wait lasted until external120s hardKILL, wrapper137; owned processes confirmed absent. No clean shutdown or repair claim. Reports/task/six records updated; prior124 attempt and untracked parity01/02logs preserved. TASK01 PARTIAL / safety FAIL / READY BLOCKED_BY_SHARED_HOLD_SEMANTICS. Stop for user collision action and holding-representation choice; no force/P2/P3/fiveCube work. Publication recorded after verification.

## 2026-10-08 — One approved controlled fallback executed, bounded launcher stop

Git follow-up: initial non-fast-forward push rejected; read remote task-branch governance files fully, fetched `bfd09ac` and merged safely/no conflicts. Pushed `b73e273` successfully, then verified the new actual PARTIAL metadata through the GitHub file tool. This also uploads prior review9f5a03b. Main untouched; no experiment/source change during sync. This publication note is a records-only follow-up.

Re-read current cloud AGENTS/EXECUTION_GOVERNANCE through GitHub plugin (complete files), plus local startup/status/task/P4/benchmark. User approved4states+5eachreset, no staticquery repair. Main prepared minimal reuse-based originalscene normal `simulate/fetch` harness; readonly independent API/source/evidence audit. Sevenpure classification tests/py_compile/diff checksOK. Source checkpoint47d22ce/SHAab174884… before singleGUI launch, unchanged during/after run; no original runtime source/geometry/physics/ACM/YAML edits.

One originaldt synchronized START14q/Cube, saved nativeposttime/step/contacts/overlaps. Actual1step START had no unexpectedpenetration/environmenthit;14qpostmax9.05020e-5rad, TCP0.096015/0.067458mm, CubeZdrop2.725005mm withoutheldconstraint (notREADY). Inputs/material/mass/frame allsaved. Introduced stdin drift-review gate then blocked in background terminal read (processT/Tl, SIGTTINconsistent/nottraced); one accept_snapshot input was sent but never persisted. Outer120s timeout124/reaped, nointernalfailure/summary, noPRE/state196/TARGET orreset. This avoidable launcher barrier was agent-added, not a new physicsmodel fault.

No retry/source change after the one approved attempt. Saved originalSTART42.6kB/rawinput/sceneaudit/source/log and post-runoutcome clearly distinguished from probe output. Corrected CPU label to measured GPUsceneattributes/NumPyfrontend. Updated three requestedreports, task, sixrecords and governance authorizationfollowup. TASK01PARTIAL; userdecision required for any extra bounded command-only run; never parity10/FROZEN/force work.

## 2026-10-08 — User governance override / stop engineering loop

Fully re-read latest cloud AGENTS (243 lines), EXECUTION_GOVERNANCE (103), startup/task/status/benchmark/P4 references. SSH/HTTPS fetch failed; used raw GitHub pinned main `0e3f8f5`, did not merge stale main or overwrite task progress. No new source/Isaac/physics after override. Audit corrects09 actual reloaded leftq all0 vs candidate max2.43079577rad/callback0,70 softwareOK/.148s, no collision verdict; previous planned text is superseded, not erased. Recent07/08/09 count as exhausted same-root3/3. Stop parity series and proposed initialization extension. Scope/ownership/minimum Tier2/escalation in [review](../reports/TASK01_GOVERNANCE_REVIEW.md); fallback awaits user decision.

## 2026-10-08 — 08 query proof仍停止；09逐态原native重建IN DESIGN

08 source3e2414b/29cfd626…，START accepted0/callback0，官方flush与on_update(time,0,false)实际完成，left link2内部点query依旧miss。56纯unit0.100s OK不能替代parity；成功actual_q/TCP/Cube/18linkFK本轮实际落盘，pre/post27 native和不变几何fingerprint保留，但无碰撞结论/READY。

09仅设计原模型逐状态native handle重建，安全API审核中未执行；owned原USD/hashes/known14q保持，不改model/几何/ACM/benchmark、不给parityPASS。旧03–08负结果不覆盖，静态index不冒充poststep测量；BUG001延期非阻塞、TASK02 TODO。

## 2026-10-08 — 07合法零步后query guard停止；08官方零步refresh候选未运行

07 commit0fb2fc4/source8887ad…，START callbacks0/accepted0；pre/post27 native比较与不变geometry fingerprint保存，inputs/runtime/candidate YAML独立hash一致，51纯unit0.099s OK。原left link2 cooked质心查询无hit而立即拒绝；独立坐标核对未见明显变换错误，但不能唯一归因stale tree。没有collision verdict/READY；成功q/liveFK全表未存，只记录控制流通过，不反填。

08 source29cfd626…只准备原flush_changes + stage_update.on_update(static_time,0,False)工程refresh（文档：更新其他子系统、不更新physics），非tree freshness保证。全部零步/q/native/geometry/query hardguards、no Play/stepping及原模型保持，测试待主代理、GUI08 NOT_RUN。保留03–07，BUG019未判决/BUG001非阻塞，TASK02 TODO。

## 2026-10-08 — 06零步guard拒绝；07避免Play warm-start仅准备

06 commit0a78485/source923aca…，GUI14.25s/START accepted0：render gate仍callbacks2×0.01666666753590107s。输出mirror stale0、pre-render27 native比较max0m/6.165552397244359e-7rad已保存，但render_guard随后拒绝，moving queries/碰撞未开始；50纯测试0.079s OK、wrapper0不证明parity。candidate YAML/捕获14q/runtime原模型hash独立复核未变。

SDK源码 `_warm_start`直接update_simulation及`_create_simulation_view`第二调用可绕过render gate，与2events吻合，非唯一已取证因果。07准备不timeline PLAY，仅原force_load/start_simulation初始化，无update/simulate/fetch、无SDK callback禁用/patch或物理/model/ACM/benchmark变动；所有step0/q/native/几何/query guards保留。source8887ad…待freeze，GUI07未运行；03–06负结果保留，READY NOT_RUN、BUG019未判决/BUG001非阻塞、TASK02 TODO。

## 2026-10-08 — 05意外physics dispatch保护停止；06 render gate准备

05 commit `8188168` /source `66dce1cd…`，GUI约13.8s、START accepted0。paused app.update实际callback2，Cube z0.3772749900817871m/vz=-0.16350001m/s，真实积分已发生，立即拒绝，不称静态PASS。通知前27 nativeactor比较已落盘（位置max0m/角max6.165552397244359e-7rad），与通知后数据分开；wrapper0非PASS/READY NOT_RUN，无模型碰撞判决。03/04/05负记录保留，`8188168` direct push成功。

06只准备官方render模式临时关闭playSimulations/app.update/finally恢复原bool，force_load初始化亦dispatch隔离；callback0、time/q/native核验不削弱。Fingerprint区分SDK动态velocity/jointstate输出与mass/scale/mesh/limits/drive/material/scene/frame几何参数；不改Scene dt/gravity、实际几何/benchmark/ACM。纯mock render-gate回归准备，06未运行/source待冻结；D035 ENGINEERING，无P4/DEVIATION，BUG019未判决、BUG001非阻塞。

## 2026-10-08 — 04原SDKQuatf属性报错保留；05状态precision与库存审计准备

04使用已固化 `a672224` /probe SHA `3bf86b380723b317b2eb4b32f3020a3736a16126887648bbc8a80c0bc3da8753`，可见GUI约14.5s后START accepted0，原SDK Cube `xformOp:orient` expected GfQuatf/got GfQuatd，实际 `ENGINEERING_USD_ATTRIBUTE_PRECISION_STOP`。Fabric未启用、updateToUsd=true，未进入模型碰撞验证；native成功值未保存，wrapper0非PASS、进程已退出回收。03 stale源负结果未覆盖；04也不是几何失败、BUG019判决或物理成功。Git首次proxy push超时保留，随后direct push `a672224` 成功，无全局SSH改动。

05仅工程输出precision依原属性修正；body pose state-output允许原SDK自己物化Cube orient并单独审计，helper仍不新增ops/不重排且拒绝非法顺序。不可变geometry fingerprint扩展全scene physics/材料、ancestors、工具TCP库存，原scale/local shape/limits/参数继续核对；增加final step0及screenshot step0守卫。35纯USD/query测试主代理实际复跑exit0/0.093s，source SHA `66dce1cd96875298f3830a25bb64232d6eb75f97717deaef7134feb43368cdba` 已冻结。GUI05尚未运行，不能记录为GUI/model PASS；READY NOT_RUN，无benchmark/实际几何/ACM/force/P4改动，后续结果另追加。

## 2026-10-08 — 03可见静态取证门禁停止；04输出适配仅准备

按用户“继续”保留既定单Cube严格顺序。`d9c422c` /probe SHA `27e0a043431a83b0f8fa760fd6307f8749ee2e825de154dcad4c3c67ae6d7aa1` 在执行前保存byte-identical快照；使用原native-run配置与官方资产，不执行旧五Cube场景入口/ROSgraph/controller。03可见GUI加载原模型及实际cooked shape，CPU tensor ordinal=-1/readback_suppressed=false。START q/Cube/TCP与link FK通过已存门禁；native actor比较控制流未拒绝，但成功值未包含在失败产物，保留这个证据缺口，不反填数据。

实际在 `/World/left_fr3/fr3_link1/collisions` 的USD旧旋转停止，accepted=0，未进入移动shape查询和全链碰撞判定。状态为 `ENGINEERING_STALE_USD_QUERY_SOURCE_STOP`；wrapper0与实际failure分开记录，owned GUI进程已退出/reaped。纯软件query守卫19测试OK不等于模型一致性PASS。03原始负记录保留，没有称BUG019复现/修复、几何FAIL、READY或动力学PASS。

04准备遵循D035：先官方scene/Fabric当前已有输出路径，必要时仅把verified native SE3镜像到原body既有translate/orient；保留原scale、local collider、ops顺序、几何、设置及step0，paused notices后再核对q/native与所有守卫，不跳过freshness验证。04尚未运行，结果必须另记。无P4、force/wrench、物理参数/ACM或基准改动；READY/reset仍NOT_RUN，TASK01未冻结。

## 2026-10-07 — 用户批准新START；有序全链几何实际通过

D034/cc04cec记录START=(.55,0,.38)、identity、双臂已持件，不是Task27feed。fb643f1增加独立完整链probe，抽取原几何helper保持算法，失败记录/nearest-point有限性/distance-collision一致性守卫。两轮build都真实完成，第一仅build未执行；最终build02核对SHA后只运行一次fullchain exit0。未更改原model/ACM/mesh/场景，禁止以改几何解决失败。

A136/B157、≤2mm、previous-q各一次IK、PRE接缝实际14q完全复用，293完整状态均PASS；记录每态六类FCL min/exact pair/closestpoints与所有linkFK/IK诊断。Cube四环境另1172检查无穿透。START/PRE的14q复制候选YAML而非冻结；原run config_at_run不可变保存。独立readonly产物复核counts/seam/steps/min/max/CSV/source/input/binarySHA全部相符。

然后才实现/启动单Cube visibleGUI静态PhysX query/cookedshape一致性probe，不执行旧scene module bottom、五Cube/ROSgraph/控制器，不改材料/drive/原碰撞。GUI初始化进行中，parity与READY无通过结论；首意外overlap会停，不修geometry/ACM。三报告和六记录持续保存，force/wrench延期TASK10-IS、TASK02未开始。

## 2026-10-07 — 保持几何的单Cube IK拒绝诊断与精度对照

按用户“继续”及PRE报告，仅扩展只读probe日志/局部数值设置，没有启动Isaac。12a6d74为每臂记录solver bool/error/raw q/限位/FK残差与拒绝原因；首次diagnostic01在链接前误启动旧exe，不算instrumentation验证，标INVALID并保留旧log，等待actual build exit0后另起diagnostic02。有效结果确认两臂SUCCESS/界限通过但旋转残差超原1e-4rad，BUG025诊断缺口定位，不编造碰撞pair。

8a5bbaf新增同记录14q重放和只收紧本地epsilon选项（默认不变）、int/bool kinematics解析及tip断言。同二进制原1e-5重现拒绝，1e-7同seed/同目标通过原门限与full FCL；然后有限dense原名义段157/157通过，max旋转9.94215e-6rad、密集margin25.755478deg。2856fa5补worldCube对table/三墙零偏航AABB审计628对，无体积穿透/4基本测试PASS，不改变ACM或PhysX容差。

五个run元数据/结构化结果/原stdout均保存，报告TASK01_SINGLE_CUBE_IK_DIAGNOSIS。原YAML/model/kinematics hash不变；START缺定义和BUG019留待用户审查，整体PARTIAL，TASK02 TODO，无P4/force/旧五块debug。后续须先确认START，不能用插入局部成功宣称科研冻结。

## 2026-10-06 — 单 Cube 几何检查首败停止，不再扩展旧应用

读取用户附件及云端单Cube计划；ff-only不可用（本地旧证据提交与远端新计划分叉），安全merge保留双边历史，仅STATUS顶部冲突手工保留新范围和旧负结果。f616603完成合并，未force/reset。停止自有旧GUI193707，未启动新Isaac、未继续旧五块控制器。

新增独立native probe，读原源码xacro/kinematics和新schema2候选，在本地一Cube/桌/三墙检查，无MoveGroup action/remoteScene修改/机器人或吸盘命令。串行build PASS；b31ff05端点probe01六PASS/START缺失/exit3。c9d71f4加密probe02六端点PASS，但上一q单次seed在前进1.987179mm无合格双IK，exit1，当即停止并汇报。没有错误后重放、试别的姿态、改工具/车厢/ACM/门限；具体拒绝臂/插件原始错误未记录，不编造碰撞pair。

保存两个run的metadata、sample JSON、CSV（84限位/12抓取误差）、dense JSON及精选原日志；报告TASK01_SINGLE_CUBE_GEOMETRY。原场景/Bridge SHA保持；START/连续IK/Isaac碰撞模型差异待审查，TASK01 BLOCKED、TASK02 TODO，force/wrench留TASK10-IS。

## 2026-10-06 — PhysX计时仍FAIL；Cartesian接近计时范围PRE

physclock首件侧接近原80Nm互锁拒绝left86.670/实际Cube接触217.404N，未建立side suction、未执行X/Y。完整数据/负结果保存，GUIpause后正常0停止，不冒称时基修复PASS。读取本机GetCartesianPath.srv确认无v/a缩放字段；仅Task01 DUAL_SIDE_CONTACT显式按现有请求0.12/IPTP计时、逐值q不变/FCL仍必做，非改physics、drive、路径或门限。构建完成前不改源码，fresh GUI实测待结果。

## 2026-10-06 — PhysX时基production通过并fresh可见GUI启动

build02修正重名后58.5s/exit0，source6fa161e/binary75f798a1、源码冻结期间编译；63Python/两组C++通过。fresh可见GUI再次加载同原场景，图片确认第一供料落稳后启动normal1.0首件，没有用旧慢速/旧初始化stage代替。同步shared phase来自同一次stamp，单臂也用原子反馈；保持原轨迹和保护，新增缺失ready/age/stamp错误日志及侧接近互锁详情。真实结果RUNNING，读取原子消息的外部20s只读时钟采样无命令。

## 2026-10-06 — GUI首件负结果与实际物理时间计时PRE

run02实际COMMON搬运完成，但重抓侧臂下降CONTACT跟踪最大10.109deg并与Cube真实接触，left raw86.323Nm，原保护拒绝/安全OPEN，无X/Y。最初日志缺接近互锁细节，不能称闭合超时；补正式负结果/held审计。暂停余下drive再正常停owned GUI0，不无界面重启。仅Task01执行器改用既有原子PhysX stamp，共享双臂进度、不用wall fallback；get时原250ms且回退拒绝，旧Task26/27、路径、physics、ACM等不变。新增进度C++测试，63Python及两政策组PASS；首编译final hold重名失败保留，build02修正后进行中，不边改源边build。

## 2026-10-06 — 可见GUI启动诊断及首件正常倍率回归

按用户“启动gui继续测试”。先官方可见GUI加载原fixture/Bridge/readonly recorder，Prim/物理存在但空网格，机器人命令0；渲染detach/readd排查后native139，完整负记录保留。撤下仅本轮新增且未使用的GUI原型，改复用原记录器的SimulationApp可见入口，显示原完整场景成功。新增缺DISPLAY拒绝的GUI入口、循环执行客户端（仅127.0.0.1:8226）、两GUI设置单测；不改原场景/Bridge/物理/门限。

新fresh可见run02第一供料真实落稳、截图确认后启动08f3060a原production，first1/max1/scale1/roll-15/rear45。63Python PASS，无headless进程启动；实际结果RUNNING，原反馈过期问题待观察，不从配置通过推断物理通过。

## 2026-10-06 — 正常播放倍率与可见GUI工作流

按用户新要求停止延续无界面实验。核对播放计时为wall_elapsed/time_scale，上轮5.0=20%，旧默认3.0约33.3%；新`TASK01_DUAL_SUCTION_FIXTURE`默认1.0，增加明确播放比例与保留12%规划限速的启动日志，有限值/倍率>=1门禁在任何Arm命令前拒绝错误输入。旧Task26/27节点默认3.0不静默改动，历史显式5.0日志不篡改。README/启动指南记录GUI场景→Play→原Bridge→原子反馈全部步骤。没有改接触速度规划、场景、ACM、保护门限或启动新物理实验；编译与软件检查结果另见TASK01_GUI_SPEED报告。

此前full01最终归档FAIL_X16_STALE_OR_INVALID/controller1、headless0/completed[]；17几何匹配、5862held/21398atomic/3566sparse完整性0错，未到空载转场。保留原数据和未知根因，不能用normal速度设置称修复了反馈问题。

## 2026-10-06 — 空载局部管线重放PASS/真实five-Cube开始

第一请求局部action探针3个postprocessed路径被MoveIt拒绝，负结果保留。最终仅新fixture OPENhandoff复用当前进程本机OMPL与参数副本，segment fraction0.0005/原RRTConnect/原目标/完整世界，IPTP不改q路点，顺序第二臂含第一预测终点，执行前再以第一实测关节完整FCL复验。无远程Scene或参数写/额外move_group/背景预规划，旧及加载链不改。probe03同f237cff串行重编译并实际无命令PASS，首编译main-local槽位lambda错误与中间binary一致性边界保留。原61Python/两C++/benchmark36nulls/hash PASS。新fresh原headless普通供料five-Cube回归启动，source/binary检查后运行，暂不预记完成。

## 2026-10-06 — full02终局归档与空载转场PRE

控制器1、第三件实际双吸推压放置成功但handoff未完成，不能把三放置/两batch冒称五件成功。正常停自有headless0并审计完整stream：105精确stamp、36469held、51175atomic、8529sparse/0errors；原raw保存。当前只读读取MoveIt world/ACM证实无Cube条目全豁免，不能以扩大ACM修复。准备仅新节点的有限空载路径候选筛选、同一实测完整起点和第二段预测partner起点，原RRTConnect/目标/每侧3mm冗余/30mm退出不变。不是冻结的Task22后台沙箱预规划。

磁盘不足时仅自有已结束full01空闲日志gzip无损压缩，逐字节解压SHA验证；元数据保留路径/hash/恢复方式。没有删除原始内容或改用户文件。

## 2026-10-06 — full02前两件物理完成，第三关键回归继续

第一rear候选1–4联合gate拒绝、5/24通过后执行，第二1/24通过；两件实际X16/Y16/双CLOSED/无释放角色交换及短RRT转场batchPASS。最终短清障center0.302/0.407、deep0.156/0.091、side0.259/0.397mm。第二rearOPEN norm2.026→1.031→0.036mm。原门限未变；只前两件证据，第三/后两/最终同一步审计待结果。

## 2026-10-06 — final binary full02启动正常

不再边改源边编译，CMake -B目标重建57e72f83、两组root arm字符串与run前SHA验证成功。新fresh原stage/正常供料/零预置，自动READY后启动controller模型正常并已进入首件实际运动；先前full01未运动负记录保留。没有放宽保护、改场景或用采样空转宣称物理通过。完整回归和同一步审计继续中。

## 2026-10-06 — production二进制一致性审计更正

full01控制器启动阶段拒绝/命令0；通过只读RPC核对六参数类型值正确，strings揭示production缺root arm前缀，probe有。编译时修改include造成已读旧源码、链接更新mtime并后续no-op；不再称production与a3fceab一致。保留startup负日志/3600s空闲采样（非运动验收），串行CMake -B重编译/字符串及SHA验证后另fresh full02。未修改源码行为/场景/物理/门限来掩盖失败。

## 2026-10-06 — 联合rear预检实现/诊断验证，物理fresh复测启动

首三候选只读HIGH IK+连续下降+双X/Y+短退出复用现有本地FK/FCL，不再拿旧solo链代表新协议；后两精准solo不变。原blocked姿态拒绝、3替代完整本地链通过。参数读取首轮拒绝（实际是left/right_arm.* LMA）修正后通过，旧失败日志保留；61Python/两C++ PASS，第一次C++临时目录不存在不是源码失败，set-e/mktemp重跑通过。a3fceab控制器SHA174d6ef7，fresh零预置五件headless启动；没改场景/物理/门限，未称物理完成。

## 2026-10-06 — BUG021无命令重放与联合链修复PRE

probe从/move_group有界读取当前KDL参数，用第三件held step46343精确14关节/Cube重放；原rear固定侧HIGH 60/60解都有工具↔right link5碰撞。保持rear TCP，前7有效IK找到3终点组合自由。保存build/side_goal_probe/rear_goal_search日志及binary SHA，未发机器人/吸盘/供料/导轨或远程Scene命令。新增联合候选预检PRE见原子反馈报告：纯软件、首三件、旧后两与原模型/物理/ACM/门限不改；先编译/共用只读链，再真实fresh回归。

## 2026-10-06 — full01真实2/5，第三goal诊断

前三后杯OPEN精调都通过，第一第二新主从双吸X/Y、释放/短RRT转场真实通过；第三rear重抓后side HIGH无合法goal sample×8（各约20s），安全双OPEN/exit1，不执行第四第五。保存70精确stamp几何/37804完整held审计和全部失败日志，headless正常停机0；无持件机器人-墙非零接触。新增纯probe精确14关节/Cube输入、60有限KDL种子与FCL pair计数，不构造Arm/发命令/改远程Scene。不是目标全局不可行证明，也不直接改控制器。

## 2026-10-06 — 首件新协议实际通过，开始完整五件回归

runtime39f1a0c原场景rear45/side-15，后杯OPEN两次XYZ后norm0.205mm，X16/Y16/双吸附主从换角/释放/HOME全部完成/controller0，最终中心0.303/deep0.212/side0.216mm。同一步35几何精确匹配、8470held0完整性错且窗口无非零机器人-墙接触；原80Nm/2.5mm不变。Isaac正常0退出，MoveIt关闭-11另记。保存首件报告/metadata/audits；同binary fresh first1/max5继续，不能复用这一件称全部稳定。

## 2026-10-06 — rear45真实Z残差与后杯OPEN精调

rear_roll_cube01最终X1原alignment失败、双OPEN，精确stamp确认rear Z为PRE_CLOSE -2.363/CLOSED -2.462/X1 -2.578mm；不是USD假报，没到墙。保存metadata/geometry_audit/held_analysis，失败不抹。runtime39f1a0c新增仅前三rear OPEN的有界XYZ，上一命令FK加实测残差，原Cube参与完整联合FCL，helper保持实测姿态，失效拒绝CLOSE。初编译linkPose签名错误exit2，修正后build50.4s PASS/61Python/两组C++/analytic36nulls。原模型/物理/保护门限不改，真实新首件待测。

## 2026-10-06 — 后腕名义检查与实际重抓接入

- rear45镜像/side-15无命令前三链3/3 PASS；1330双腕节点三墙均0交集，不仅查深墙。
- SciPy1.8 HiGHS默认status4两次保留，换同约束内点LP并检查残差，61Python/C++PASS；没有放宽交集判据或跳过坏行。
- 新节点前三件后抓OPEN RRT/预演统一姿态函数，后两件/旧节点原pushPose不变；待编译和新鲜首件原门限物理验证，不能提前PASS。

## 2026-10-06 — 原子反馈实测与后腕侧墙定位

- runtime88ef454/build54.2s/binary31d862a6…；原子反馈首件真实X16/Y14，Y15原保护停止，bothOPEN/完成0。33精确stamp几何校验匹配，60Python/C++PASS；源对照显示USD可在有效物理正gap时输出<-1mm。
- 同步问题工程修复不能解决几何碰撞：实际rear right link7↔+Y墙745.808N。旧nominal02补三墙凸包，有7右腕Y节点重叠；原deep-only证据限缩。
- 第二阶段PRE：只读后杯面法向worldX镜像转腕45deg，中心/法向不变，使腕部向中央。需前三IK/FCL/TCP+原USD双腕三墙检查，暂不改执行器/物理/门限；失败保留。

## 2026-10-06 — 腕姿实测负结果与持件原子反馈

- dd63c74编译/非法31deg提前拒绝通过，首件X3旧rear gap负值停止；保存4738 held/4085 sparse/0错误，未到深墙，不声称姿态物理修复。
- 本轮PRE：定位旧USD显示滞后及独立latest观测，新增可选live PhysX五Cube+两link8单view快照/TCP固定变换/单PoseArray；独立3+2控制节点必需该源、格式/时间/250ms门控、不回退旧反馈。旧场景/bridge源码/后两单推不变。
- 56Python/C++边界检查PASS，编译和新鲜首件headless验证进行中。P2/P3未实施，36nulls不填，benchmark未冻结。

## 2026-10-06 latest — 真实接触诊断与只读腕姿候选

诊断02原source d35cc0c/b749abc实际首件复现Y15保护，原物理/模型/80Nm/ACM不改。先自动safe abort，再手动结束仅仿真记录进程；保存10538连续held与4598稀疏行、精确峰值接触/DOF、服务FK/FCL重放和原mesh/hull审计。发现left link7深墙实体接触，而同关节MoveIt墙检查自由；测量FK一致，不能继续把根因只归为闭链内部力。

新增只读重放脚本、凸包审计和9单测，53Python通过。探针0cfdbaf名义3链通过，但多线程日志穿插污染数据，分析器拒绝；c13ea40改独立不覆盖数据文件，重新nominal02通过3链与1330原mesh离线节点/0墙重叠。杯面中心/法向不变，仅面内转角候选，仍未改执行器/运行新物理任务。原资产fresh GET SHA与cache一致，未使用不明替代模型。

## 2026-10-06 follow-up — 网络恢复，原场景第二次启动

原S3直连/代理HEAD恢复HTTP200，runtime d35cc0c正常push成功；保留startup01失败。相同官方资产/原参数的startup02重新运行，held live handles与首件物理诊断仍待验证，尚未发controller命令。BUG017根因未解决，BUG018外部连接暂时恢复不抹掉负结果；模型/物理/门限/YAML不变。本段更新此前“final”失败checkpoint，不叫新物理PASS。

## 2026-10-06 final — 本轮启动负结果，未开展物理推压

实现持件phase只读记录、全机器人contact路径/DOF targets/positions/velocity/projected effort、同一步/丢步/空流/非有限分析门控，44单测与编译PASS。真实启动在FR3远程stat连接失败，未导入诊断到有效机器人；本轮不是Y15再次失败或修复证据。尝试直连/代理/另一S3域名/SSH及SDK缓存lookup，均失败；离线缓存含FR3但来源映射未证实，不擅自替代。原场景/工具/质量/摩擦/门限/ACM/YAML哈希未变，自有进程结束。

## 2026-10-06 — 持件诊断搭建

复用原pose/contact sampler和release logger接口，专用held phases；记录机器人全部link/桌墙Cube接触对、DOF positions/targets/velocities/projected effort，零接触对仅压缩不设力阈值。保持旧logger默认行为；39 Python/build PASS，启动验证中。

## 2026-10-05 final — 实测换角色复测结束，保存未通过结果

`dual_fixture_cube01_measured`/e0477ab/binary d1658940…：X16与Y14段实际完成且双CLOSED，Y15 raw effort86.975/32.984Nm触发80Nm保护。controller1/completed0，后续四件保持停车，不叫首件或五件PASS。保存metadata、analysis、protocol与精选控制器原日志。

新增只读 `diagnose_released_state:=true` 探针并编译66s，释放后实际14关节姿态对桌/墙/其他物体联合FCL通过；仅本地忽略当前合法接触Cube01，不修改远程Scene/ACM、不发布机器人命令。不能回推互锁步无碰撞。末双CLOSED样本距名义侧压终点还有17.354mm；原release logger只采释放窗口，本轮没进入它，零接触样本不等于零接触力。

35 Python PASS；稀疏姿态9432/完整性错误0；自有Isaac0退出与MoveIt关闭-11分别记录。模型/物理/门限/benchmark哈希不变。持件同一步接触/关节观测待下一步，不从两次失败推断必须改基准或加论文力控。

## 2026-10-05 follow-up — 保存首块负结果与实测换角版本

首件新协议实际X完成16/16双CLOSED、贴深墙0.286mm，但Y开始触发未细分互锁，控制器1、双OPEN、completed0。保存4747无完整性错误PhysX样本与精选原日志/protocol，不把搬到深墙叫整件PASS。

仅新分支增加换角时实测双臂起点/新Cube GT、当前状态FCL与重算Y/退路，记录互锁rear/side及raw力矩。e0477ab编译54.3s，35 Python/4 C++ PASS，新鲜首件复测已启动。没有改场景/模型/物理/ACM/门限或开始论文力控；根因未确定。

## 2026-10-05 — 新3+2协议实现与首块验证

完成PRE报告后新增独立节点/策略header/共享实现include/无执行探针，保留旧节点。前三件建立rear+朝中央空隙side两个面中心吸附，双CLOSED下共同X推入与不松吸盘的主从互换Y压紧；第四第五继承精准单推。保留80Nm原始effort监督、原接触几何门控、失败双OPEN并回写当前Cube。工具盒体初检不等于FR3证据。

完整探针先失败于本地IK缺参，再暴露独立轨迹时间缩放不保相对几何/Cartesian跳支。复制当前MoveIt运动学参数、复用连续世界FK微解算成同一位移网格、扩大对置名义seed覆盖后，最终前三链全部通过，relativeTCP最大约0.002mm；无机器人命令。34 Python+4 C++策略测试、colcon build PASS。新鲜headless原场景首块运行中，源码ff20ac3/binarybd1de5b7…；不借用旧5/5或启动纸面力控。

## 2026-10-04 final — 完成普通五件回归并收尾上传

保持已编译源码 `df9c2c0` 和原场景/模型/物理/门限，实际跑完零预置 first_batch=1 / max_batches=5 / time_scale=5 / release hold=0。五个 batch 均 PASS，controller 0，双臂 HOME；普通空载 Cartesian 成功，新 RRT 备用未触发。保存 metadata、analysis、release_windows 和精选 controller 原日志；raw 留本地、不提交大数据。18,498 条稀疏姿态 / 0 完整性错误，3,212 条释放诊断。复核 Cube02 XYZ 两次有限修正的规划 0.069299 s / 慢速执行 7.418296 s，不把约 28.77 min 的 demo 当效率结果。

停止自有 Isaac、MoveIt 与控制器进程；保留 MoveIt teardown -11 / bridge 1。六份记录和 TASK01 报告更新，历史普通失败、重放 01 失败不抹掉。此前退出成功与本次成功都保留，但不能据此证明所有冗余构型可靠或 BUG-016 已修复。TASK01 仍待用户基准/接触/测量审查，TASK02 未开始。

## 2026-10-04 — Bounded fallback built and replayed before commands

FinalRRT source/runtime df9c2c0 pushed; fullbuild55.8s PASS. OriginalMoveItrequestgoalconstraintsreplaceincorrecthandwrittenaggregate-angleguard, notsuccessthresholdchange. Negativefirstreplayretained; finalno-commandreplay02PASS1277jointFCLsamplesincludingreleasedCube; syncREMOVE/absenceconfirmed. Ordinaryheadless0preplacedfive-runlaunched, binarypinned, resultpending. Prioroldexitsnotdiscarded; sameCube02differentredundantqrecorded. Existing-objectbitwise restoration comparison needslaterunitreview; noclaimresolved.

## 2026-10-04 — Reconcile prior retreat successes with normal-feed failure

UsercorrectlyrecallspreviousexitPASS; comparedactualCube02jointseedsratherthanassumingglobalregression. Currentleftj3=-2.7546/j4=-2.8750rad, tinytrackingdelta; originalFKguardrejectsbadCartesian. ArchivedFAILsummary17319poses/0errors, stopownedheadlessafterbothOPEN. PreparingRRTreplayusingretainedrailshift0.1m, sameworld/target; threecandidatebudgetandshortestjointtravelranking, verifiedsceneundo, no robotcommandsinprobe. Existing28PythonPASS; build/physicalpending. PREinTASK01_RELEASE_CLEARANCE, no scientificchange.

## 2026-10-04 — Diagnostic failure retained; actual side seed engineering repair

Diagnostic02 Cube02SIDE_HIGH_APPROACH t0 activeCube collision0.783mm aborts before sidepress/release; onlybatch1PASS. Collected13227poses/1617releasecontacts0errors; stoppedheadlesswithbothOPEN, MoveItteardown-11. PostabortstaticrearCupgap0.267mm notexactfailuretimestamp. Mixedcommandseed+actualGT identifiedinsource; adapted independentactualsideplan tosinglemeasuredRobotState andexistingdeltabounds/graspstate, currentCubeFCL stillstrict. Sharedfinite-seed helper/unitextended; runtime2fbfa0bpushed, build62s/finalincremental0.44s/Python28testsPASS. Normalhold0/fullfive preparing, originalreleasedrift remainsOPEN/noeffectclaim yet.

## 2026-10-04 — Release diagnostic startup/build/first-object checkpoint

Compiledindependentvariant56.5s/package56.8s/total, committedruntimeb259366. Startup01failsBRANCH_SIGN lookup beforecontroller, failure.json retained despiteIsaaccloseexit0; corrected logger config namespace only. Diagnostic02 startsnativecube/tool/contactviews beforecommands; optionalhold3s distinguishesrelease fromclearance. First-objectholdX0.028mm,clearanceX0mm; secondobjectstillrunning. Addedsummary peak/mixed-step/nonfinite regression, Python28/28PASS. Exactbinary/pins/commands inmetadata. Diagnosticstopatbatch2 prevents later loaded motion atsimdeadline; not ordinaryfullfive proof.

## 2026-10-04 — Release-window diagnostic preparation

Reread mandatory instructions/currentTask01/spec/P2/P3 cards and statuses, sent PRE-TASK. Scoped userapprovalto release/clearance engineering, not forcecontrol/model/gates. Addedphasepublisher plusoptionaldiagnostichold default0 onlyindependentnode; opt-in headless usesexisting validatedPhysicsContactSampler and nativeRigidPrim tools, noUSDdisplaypose. Full-rate onlyduringreleasephases, sparseordinaryposesunchanged. Phasearrivalsasyncexplicitlylabelled; collisionforcesnotD6wrench. 25softwaretestsPASS; build/actualdiagnosticpending.

## 2026-10-04 final — XYZ validation completed, release-window failure retained

Built runtime f0812a4; C++/22Python/real RobotModel PASS including XYZ obstruction rejection. Started actual normal-feed headless with unchanged scene/bridge hashes, no preplaced objects. Cube01PASS; Cube02 needs two XYZ corrections and passes original preclose gates (X0.606/Z0.451/gapdelta0.275mm). Planning0.078621s/execution7.569621s, bounded1mm and3checks. Actual Cube02 later fails final deep gap5.138mm against3mm despite pre-side-press0.488mm; physical data shows negativeX retreat around rear suction release after sidewall reached. No loaded/contact/physics/gate repair silently added. Preserved full fail/exit1,7680samples0errors and release_drift.json; no later cube advanced. Stopped exact owned processes, headlessexit0/MoveItteardown-11. Updated all six records/task/report/metadata; branches uploaded through command-local existing proxy after directSSH failure. TASK01 IN_PROGRESS/36nulls, TASK02TODO; next release/contact diagnosis needs scope decision.

## 2026-10-04 — Pre-close XYZ engineering implementation

Read required task/benchmark/paper records and git status; announced PRE-TASK. User approved merged XYZ correction rather than three serial axis moves. Added pure finite-input helper with total 1mm vector cap, accumulated commanded-FK targets in the independent variant, OPEN guards, static FK/Isaac diagnostics and timing. Preserved legacy Y logic under other nodes and all existing gates/model/physics/loaded control. Extended mathematical and no-command RobotModel probes; build/physical evidence pending.

## 2026-10-03 — Normal full-five negative result preserved

Actually ran normal feed first1/max5/time_scale5, no preplaced cubes and unchanged binary77b4f499... . Cube01PASS (center1.605mm, deep1.006/side1.251mm), short/RRT handoff to Cube02. Two fine Y corrections converge gap asymmetry to0.001mm but X mismatch remains3.150mm>2.500mm, so pre-close safely exits1 without suction or later tasks. Stationary TCP read-only snapshots support3.149754mm difference, not synchronous dynamic calibration. 7214 valid sparse poses; no code/model/gate changes. Added null guard for parked/unexecuted Cube04 neighbor geometry in summarizer, not physical scene. Saved raw/metadata/analysis/report, stopped all owned processes; MoveItteardown-11 persists. User-review boundary: do not silently add XYZ feedback/model/material changes to obtainPASS.

## 2026-10-03 — Normal five-Cube regression preparation

Read current handoff and scoped validation records. No hard choice needed to test the current variant from normal feed. Added zero-preplaced mode to the existing sparse headless probe, preserving Bridge automatic batch1 and requiring actual first arrival (no empty-set READY). Expanded read-only summaries to retain all five final geometry lines and distinguish placement PASS from feed ARRIVED. Original runtime/controller/scene/physics/ACM/gates unchanged. Full report PRE-TASK saved; full-run result pending. Keep prior negative results and all numeric/model decisions pending.

## 2026-10-03 — Final empty retreat validation / review stop

Clean Cube04→05 trial exits0, batches4/5 actual PASS: fourth neighbor0.375mm/deepgap0.244mm, fifth position0.530mm/deepgap0.476mm. Macro-scoped live-start ordinary Cartesian succeeds with currentCube strictFCL (540/287 samples), fallback not physically triggered; separate long no-command replay proves seeded solver feasibility. Fourth no trim, helperOPEN; short clear/RRT next-object transition preserved. 7778 sparse samples0errors; independent fifth4691 samples0errors andexit0. All owned runtimes stopped, MoveIt teardown-11 repeats. Exact metadata/raw/summary in three empty_retreat run dirs; final report complete. No reliability/full-five-new-variant/force/paper/freeze claim. Six records updated, protected folder/old scene/material/ACM untouched; stop before model/contact/numeric decisions needing user review.

## 2026-10-03 — Empty retreat repair checkpoint

Added macro-isolated measured-state empty retreat / fresh released-Cube FCL world / bounded seed-continuation fallback, reusing existing fine IK rather than changing loaded/contact control. Added read-only real RobotModel FK/FCL probe and pure C++ guards; added optional four-preplaced fixture mode. colcon final completion 57.2 s, policy PASS, Python19/19, unchanged YAML/36 nulls. Physical results pending; negative prior fourth/fifth results retained.

Follow-up: final real RobotModel basic probe PASS after correcting only invalid-quaternion test input (ROS default w=1). Long rounded-seed no-command replay left404.716/right301.601mm PASS +610 FCL samples including released Cube. Actual isolated fifth full cycle/controller exit0:0.540mm center/0.514mm deepgap, 4691 sparse samples, no integrity errors. Four fixture cubes preplaced; fallback not physically triggered, so no causal/reliability claim. All owned first-run runtimes stopped; MoveIt teardown -11. New clean actual fourth/fifth trial starting.

## 2026-10-03 — Cube04 variant physical handoff / tests stopped
- Final `7be3659` binary time_scale=5 passes fourth: precise staging 0.040 mm, final neighbor 0.227 mm, deep gap 0.413 mm, cell error 1.339 mm. No helper-side suction or inner trim; short-clearance/RRT transition to fifth completes.
- Fifth actually dual-carried/dropped, but actual empty Cartesian retreat fails original 5-mm line-deviation guard (up to 450.1 mm), safely opens both cups and exits 1. Only fourth physically completed. No ignored constraint/fallback/extra feedback implemented; original fifth controller behavior remains preserved.
- 8,985 sparse samples, zero integrity/sampler errors; fourth insertion Y span 0.205 mm/yaw max 0.053 deg. Later actual material/mass unchanged. Python 19/19 plus standalone C++ policy PASS. MoveIt stop again -11, both owned runtimes stopped. Report/metadata/negative evidence uploaded; no benchmark freeze.

## 2026-10-03 — Cube04 first physical failure retained
- Actual first three settled, fourth normal-fed/dual-carried/staged/rear-regrasped/pushed. PRE_PUSH precision error 0.046 mm passes, but lateral drift produces final gap 1.827 mm, exceeding unchanged 1.5-mm gate; controller exit 1, no fifth command.
- 6,036 sparse PhysX samples, no integrity/readout errors; fourth helper CLOSED count inside carriage=0, no inner trim; peak raw joint torque 23.0 Nm. No force calibration claim.
- Exploratory controller was launched before final logging/nonfinite-guard rebuild completed; exact binary hash retained. Separate final-build clean-scene time_scale=5 repetition running. Avoid calling the exploratory binary the final delivery. No changes to scene/material/ACM, no silent online correction.

## 2026-10-03 — Cube04 precision insert implementation checkpoint
- Read all mandated task/source/benchmark records; issued pre-task report. User explicitly approves Cube04 contact-protocol adaptation.
- Added independent legacy ROS executable + compile-time policy, reused shared controller; fourth no longer plans/executes INNER_SIDE_TRIM, remains inner-neighbor accepted. PRE_PUSH uses previous pressed target 0.5 mm. Old nodes/scenes unchanged in behavior/geometry.
- New physical fixture initializes/settles first three only, logs sparse same-step PhysX positions and actual material/mass. First probe callback argument mistake retained, fixed via already validated post-step API. Compile/unit/syntax PASS; physical run preparing. Six records updated; no freeze/paper algorithms.

## 2026-10-03 — Further persistence / non-mutating contact alternative check
- User repeated “继续，直到task01调通，再汇报” and “继续”; no model/numeric approval was supplied. Tested a safe alternative before requesting a tool change: 24 discrete TCP rolls at the same Cube04 face-center/inward normal. All retain lateral-support/neighbor intersection; no command/IK/model change, no continuous-search impossibility claim.
- Added corresponding rod/roll regression (18 offline Python tests total). Preserved exact upstream patch context spaces using scoped .gitattributes instead of editing patch syntax.

## 2026-10-03 — TASK01 final evidence and mandatory review boundary
- Controlled default-zero task-thread hold completes normally: Cube01 / both HOME / exit 0. 34,510 recorded snapshots, zero integrity errors; 238 full-rate hold samples after first second. Mean force error 0.000370 N, instantaneous RMS 0.494278 N; mean moment residual 0.014902 Nm, tensor-vs-position-FD velocity max error 0.013163 m/s. Not force/internal-wrench calibration PASS. Repaired analyzer decimation aliasing, kept raw peaks and added regression; all 17 Python offline tests PASS.
- Existing xacro OBB audit: Cube04 face-center sidePose right has lateral/vertical support intersections with actual seated Cube03. Lateral minimum SAT axis overlap=33.524 mm, not PhysX penetration depth; no exhaustive arbitrary-roll claim or robot command. This is a protocol/geometry review blocker (BUG-009), not license to move cup to edge or ignore neighbor.
- Three startup mass/material audits retained, final reads actual backend Cube mass 0.800000012 kg and shape coefficients 0.5/0.5/0. Source material gets deleted in _build_objects after it was created. No silent restoration to 0.90/0.75; that would change physical comparison (BUG-012). First audit's incorrect tool path and intermediate partial binding checks explicitly retained.
- MoveIt teardown again -11; normal manipulation results not called clean-launch lifecycle PASS. All owned test processes stopped. Ordinary full-five and failed pause outcomes remain alongside new summaries and six records.
- GitHub records prepared on task01-benchmark-draft; legacy 76408c8 on task01-runtime-fixes already pushed. Scientific stop boundary: tool/contact/material review needed; 36 nulls unchanged and TASK02 still TODO.

## 2026-10-03 — TASK01 repaired full-flow outcome and load-check follow-up
- Normal fixed-feed inherited demo completes 5/5 physical batches with controller exit 0 and both arms HOME. No pre-placed fixture, physics/ACM/gate relaxation. Real final center errors 1.669/2.276/0.574/0.615/0.563 mm; final sample yaw maximum 0.741 deg. Controller fifth-Cube settle value 0.493 mm is a different sampling time.
- Full-stream integrity audit PASS: 70,434 snapshots, zero missed/nonmonotonic/nonfinite/mixed-step samples, dt=0.0166666675359 s. 5 analysis unit checks PASS.
- Read-only sampled contact-topology audit corroborates BUG-009: transport has opposed-side suction, but first-four rear+side simultaneous CLOSED is absent. No full D004 or paper success claim.
- Archived failed whole-process-pause metrology: suspending ROS executor expires current-state request; after resume controller opens both and returns 1. Does not invalidate ordinary five-Cube PASS. Replaced with opt-in task01_calibration_hold_sec in legacy 76408c8, default 0, main task thread only; normal ROS executor remains active. Build PASS (47.9 s). Supported SIGSTOP driver removed, exact initial variant retained in failed raw.
- Fresh controlled hold/load test is underway, with received phase observed alongside simulation step in opt-in measurement stream. No dynamic contact/internal-force calibration claim yet.
- Requested user model review for 1e6 suction break limits / retained 1.946277 kg branch; candidate YAML/hash/nulls unchanged. Six records and README/task report updated; TASK01 IN_PROGRESS / TASK02 TODO.

## 2026-10-03 — TASK01 runtime-repair checkpoint (execution ongoing)
- User requested continuing until TASK01 works, not another routine interim handoff. No numeric freeze or theory change was inferred.
- Fixed Task27 pre-close minimum-step overshoot with full measured residual correction capped at 1 mm and no minimum step. A seeded local FK/Jacobian micro-solver requires 5 um / 50 urad endpoint accuracy; joint bounds, seed neighborhood, full synchronized FCL, original 0.300 mm measured gate and three-attempt stop remain mandatory. This is [ENGINEERING], not a new paper planner. Task26 default path unchanged.
- Corrected scaled-USD quaternion extraction only in Task27; position/time lag remains separately open. Legacy fixes committed on task01-runtime-fixes at d80b6b6. Pure C++ regression PASS and ROS package build PASS (55.7 s); initial missing include-path build FAIL retained.
- Explicit official asset-root option bypasses failed S3 directory discovery, without substituting the FR3 asset. Real link8 incoming fixed-joint anchor/axes audit now succeeds on both arms.
- Fresh normal-feed five-Cube physical run ongoing: Cube01 legacy batch PASS; preclose asymmetry 0.447 -> 0.001 mm. Cube02 passes preclose at 0.287 mm, below unchanged 0.300 mm gate. Do not infer final 5/5 yet.
- Audit found an additional protocol gap: legacy helper parks during deep push, and inner cubes receive solo rear-suction lateral trim. A legacy full-flow PASS alone cannot validate the explicitly requested D004 rear-primary/side-constraint and role-swap fixture protocol. Geometry/gates remain unchanged; benchmark draft still has 36 nulls.

Append-only project work log.

## 2026-09-29 — Repository initialization
- Created V2 architecture for five-paper reproduction.
- Defined dual-platform strategy: MuJoCo for contact/force unit validation; Isaac/ROS2 for final benchmark.
- Defined mandatory traceability rules for Codex.
- Next task: TASK00 Environment Audit.

## 2026-09-30 — TASK00 environment audit started
- Cloned the repository and opened `task00-environment-audit` from `main`.
- Began read-only host, ROS 2, MoveIt, Isaac Sim, model and runtime-interface checks.
- No paper algorithm or benchmark geometry has been changed.

## 2026-09-30 — TASK00 environment audit completed
- Recorded host/GPU/ROS/MoveIt/OMPL/FCL/Isaac/MuJoCo versions and exact probe commands in reports/TASK00_ENVIRONMENT.md.
- Corrected the initial system-Python-only MuJoCo finding: MuJoCo 3.13.0 works in the existing isolated .venv; its minimal step was logged under results/.
- Expanded the legacy dual-FR3 URDF/SRDF, sampled live ROS interfaces while available, and marked unavailable or untested scientific interfaces explicitly.
- TASK00 PASS is an audit result, not a claim of benchmark readiness. TASK01 is READY but cannot be FROZEN before user review.

## 2026-09-30 — TASK01 benchmark candidate study started
- Compared the repository benchmark requirements with the existing Task27 Cube/side-suction/carriage geometry and control constants.
- Asked whether the frozen benchmark should use that validated scene as its geometric starting point or a separately designed scene.
- No benchmark values have been frozen; paper algorithms remain untouched.
- Added reports/TASK01_SOURCE_PARAMETER_MATRIX.md: source-grounded Task27 geometry/material/robot values, dimensional checks and explicit decisions still needed before any benchmark_v1 freeze.
- Isaac/MoveIt runtime had exited before TASK01 validation; no fresh physical benchmark was run.

## 2026-09-30 — TASK01 Task27-derived draft assembled
- Recorded user confirmation of Task27 as the geometric starting point in D003.
- Added `configs/benchmark/benchmark_v1.yaml` with source hashes, frames, dual-FR3/rail/L-tool geometry, cube/carriage coordinates, nominal side TCP transforms and explicit nulls for unapproved values.
- Added an analytic checker for internal dimension, handoff, wall-flush and nominal grasp consistency. It passed and enumerated 30 unresolved fields.
- No fresh Isaac simulation was run: no Isaac process was active during this iteration. TASK01 remains IN_PROGRESS; do not interpret the static pass as physics or paper-method validation.

## 2026-09-30 — TASK01 contact-protocol clarification
- Recorded the user's distinct Cube 01–04 dual-arm corrective push/press protocol and Cube 05 precision-staged single-arm insertion protocol in D004 and the draft YAML.
- Extended the static checker to verify four fixture targets and the required single-arm Cube 05 contact topology; it passed with 36 explicit unresolved fields.
- Calculated the nominal center-Cube geometric sensitivity: 1° yaw consumes about 1.038 mm of the 1.5-mm per-side clearance, leaving about 0.462 mm for lateral offset before any physical margin.
- No robot, Isaac or paper baseline was run. The draft remains IN_PROGRESS, not FROZEN.

## 2026-09-30 — TASK01 center-Cube left/right physical probe
- Added a separate Isaac probe wrapper that loads Task27, directly pre-places Cubes 01–04 into their intended cells and waits for real physics settle before permitting only batch 5 feed.
- Added a Task27 test parameter to choose left or right as the fifth Cube's -X-face pusher; its default remains the original right arm. Added a 100 nm float32 comparison epsilon to the inner fixture side-gap boundary (measured 38 nm rounding overshoot), without changing target cells or the millimeter-scale threshold.
- Built `fr3_dual_palletize`, then passed left and right MoveIt/FCL planning-only checks.
- Ran two clean headless Isaac 4.5 scenes, one per physical arm test. Both completed the fifth Cube and returned HOME. Right/left center errors were 0.603/0.669 mm; see `reports/TASK01_CENTER_ARM_SYMMETRY.md` for gap and torque details.
- This is [EXPERIMENTAL] evidence for single-Cube physical feasibility, not a full five-Cube benchmark run or paper-method result. TASK01 remains IN_PROGRESS.

## 2026-10-02 — TASK01 center-Cube exploratory repeatability
- Restarted the Isaac fixture scene and MoveIt independently for four more physical Cube 05 runs (right/left/right/left). With the two earlier runs, each pusher arm now has three completed runs, all with `Task27 batch 5 PASS` and both arms HOME.
- Right arm final center errors: 0.603, 0.429, 0.374 mm; left arm: 0.669, 0.408, 0.561 mm. This is only fixed-scene exploratory repeatability, not proof of statistical equivalence or a frozen benchmark. OMPL seed is not controlled.
- Added read-only final six-DoF Bridge pose sampling, a read-only PhysX/USD pose-source comparison in the headless runner, and a ROS-log parser that only calls a run PASS when the final Task27 PASS line exists.
- In the local Isaac 4.5 `python.sh` clean terminal, ROS Bridge needed explicit bundled Humble `LD_LIBRARY_PATH` and `RMW_IMPLEMENTATION`; the first failed Bridge startup sent no robot commands. Corrected reproduction command in the report.
- Observed motion-time PhysX/USD pose-source disagreement up to about 2.8 mm but zero positional difference after settle (printed precision). Reproduced post-task MoveIt Ctrl-C teardown segfault on each completed run. Recorded BUG-004/BUG-005; neither changed the task geometry or controller.

## 2026-10-03 — TASK01 physical pose/time channel diagnosis and calibration
- Isolated USD position frame-update lag from a separate scaled-transform quaternion extraction defect. At 0.2 m/s, callback position lag grew from 6.667 to 10.000 mm when application frames changed from 30 to 20 Hz; after app update positions match. Raw scaled USD rotation extraction had up to 27.464 deg error, versus 0.000154 deg after removing scale. Marked old Bridge yaw invalid for physical 6D claims without erasing the historical data.
- Added a separate opt-in read-only live-PhysX pose/velocity snapshot with simulation timestamp and step number, external ROS calibration/stream recorders, and a launcher that removes inherited system ROS Python/library paths. No Task27 scene/control source, benchmark value or paper algorithm changed.
- Kept failed attempts visible: mixed ROS type-support startup, a free-body angular expectation that omitted default damping, and an unsupported tuple argument to the five-body view. Corrected those causes without relaxing gates. Zero damping is authored only on the calibration fixture.
- External ROS known-motion calibration passed at 60 Hz physics with both 30/20 Hz app frames (120 motion samples each; maximum position error about 0.000313 mm, angle error about 0.000865 deg).
- One additional right-arm full Cube 05 physical probe passed, center error 0.520 mm, both arms HOME. Separate 250-s recorder received 14,295 contiguous snapshots without record errors. PhysX final yaw was 0.026334 deg while the old Bridge returned 0 deg. Report and complete commands: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md.
- Stopped the processes started by this iteration. MoveIt shutdown yielded SIGINT -2 rather than prior -11; BUG-004 remains open. TASK01 remains IN_PROGRESS with 36 unresolved fields; TASK02 and paper implementations remain untouched.
- Final code regression re-ran 30 Hz calibration with explicit position AND quaternion snapshot equality: all checks PASS. Empty-input recorder test saved FAIL and exited 1 as expected. Python compilation, shell syntax, draft analytic check (36 unresolved fields, unchanged SHA256) and diff checks passed; legacy tracked source remains unchanged.

## 2026-10-03 — TASK01 contact/mount force feasibility checkpoint
- Added a same-step collision sampler combining normal and friction impulses, contact locations and moments about an explicit body origin. Path ordering and shared contact/friction buffers are checked; 8 offline tests PASS.
- Known-load calibration at 60/120 Hz PASS: 0.8 kg support 7.848 N, horizontal friction -2 N, resisting moment about -0.04 Nm, rotated-wall 4 N direction. Dual suction holds the body while collision signal stays zero, confirming this channel does not measure D6 constraint loads.
- Independent mount reaction probes at 0/90 deg roll and nonzero COM/principal axes PASS; identified link-axis components/about-link-origin convention in this API. Actual FR3 gravity/inertia compensation has not been validated.
- Actual FR3 topology retains about 1.946277 kg in the link8/hidden hand/finger/hand_tcp branch. Do not silently delete mass or treat its roughly 19.093 N empty support as contact force.
- Retained startup failures: incorrect 4.5 PhysicsContext getter, SingleRigidPrim constructor keyword, nonexistent feed-state constant, and overwritten scene namespace. No failed startup sent robot commands. Fast-shutdown exit 0 is not a PASS criterion.
- Added full normal-feed five-Cube measurement runner without pre-placement. All five planning-only batches passed; physical execution is underway at this checkpoint. Benchmark YAML remains unchanged with 36 unresolved fields, TASK02 stays TODO.

## 2026-10-03 — TASK01 reference correction and final full-flow result
- Supersedes the checkpoint's reference-point conclusion: early COM fixtures had rigid-body scale, which also scaled authored COM/anchors. Preserve their software PASS but invalidate origin inference. Final unscaled fixture verifies actual COM=5 mm and tests nine axes/point hypotheses; only incoming joint axes/about joint anchor matches (3.436e-6 N / 4.430e-7 Nm error). Final code regression repeats this result.
- Collision calibration remains PASS (13 checks each at 60/120 Hz); 8 offline tests, final Python compilation, analytic draft and diff checks PASS. Benchmark hash unchanged with 36 nulls.
- Normal five-batch preflight PASS, but actual run placed only Cube 01 then safely failed Cube 02 before suction: asymmetry 0.968 -> 0.315 -> 0.339 mm against 0.300 mm gate, with mandatory 0.650 mm minimum correction (BUG-008). PhysX final asymmetry 0.338941 mm independently confirms. No later physical task was advanced.
- 37,236 same-step snapshots, zero measurement errors; not full task PASS. Cube 01 PhysX yaw -1.095465 deg contradicts legacy scaled-USD near-zero yaw (BUG-006). Deep-wall collision peak 139.098 N is not suction/internal force or an approved gate.
- Own full-run processes stopped. MoveIt teardown -11 recurred (BUG-004). Final added authored FR3 joint-frame audit failed on remote asset-root lookup before control commands; new audit remains unverified.
- Reports distinguish force calibration, failed full flow and 36-field freeze review. Metadata retains negative starts and invalidated fixtures; heavy raw remains local/ignored. No legacy tracked model/control or protected-directory change.
- TASK01 IN_PROGRESS, TASK02 TODO. Next scoped correction fix must retain gates, followed by normal five-Cube re-run and remaining model/frame/numeric review; no paper force controller yet.


## 2026-10-06 — TASK01 research reset approved
- Reviewed current GitHub progress after extensive five-Cube Task27 debugging.
- Identified task-scope overload: multi-Cube sequencing, empty retreat, tool-neighbor interference, material mismatch, wrench calibration and timing work had all accumulated inside benchmark freeze.
- Re-scoped benchmark_v1 to one shared Cube + dual FR3 + one carriage.
- Preserved all legacy five-Cube evidence without making it a freeze gate.
- Deferred Isaac force/wrench calibration to TASK10-IS before P2 Isaac migration.
- Next action: single-Cube geometric feasibility probe, then deterministic Isaac READY/reset, then user freeze review.

## 2026-10-14 — D079：全文接续R0来源和协议冻结

同名已有分支同步6276f78，隔离worktree并保全五原工作树13未跟踪文件。全文8页/式1–9/Fig1–5/TableI–II已重读；找到全部六环境七作者快照，30父义务/169完整入口。旧RSS9996目标独立SE2回放全部不可达；旧PCS92解边全p0，不改旧失败/结论。
R1有限资格协议 configs/p4_full/r1_qualification_v1.json：总1800s，单构建/诊断120s，正式规划0。完整TableI22500调用/最坏6250核小时待具体预算裁决。旧P4/P2文件1282条SHA保护；只追加治理记录。源码与资产外部固定引用，不重发布未授权原文/网格。当前P4整体仍部分完成，P2/Isaac不开展。
证据：reports/p4_full_audit/ORIGINAL_FULL_COVERAGE_MATRIX.md，reports/P4_FULL_PRE_TASK_D079.md，reports/P4_FULL_SOURCE_ENVIRONMENT_AUDIT.md，reports/P4_FULL_FAILURE_ROOT_CAUSE_REVIEW_D079.md，reports/P4_FULL_BUDGET_AND_DECISIONS_D079.md。

## 2026-10-15 — P4崩溃断点恢复

真实原工作树为/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full，接管HEAD a39e963，本地已有R2五提交及57未提交文件。已先备份哈希再fetch，未reset/clean/pull/checkout；原6工作树和13其他未跟踪文件保留。已完成独立只读分工核对端点、RSS预算与全文覆盖；无残留P4科学进程。A/B尚未运行；B额度原未用；旧R2wall16.337196963/CPU10.593126。见恢复PRE-TASK和保全manifest。


## 2026-10-15 — P4 R2恢复：A端点完成、IV NR局部完成、VI严格桥仍UNKNOWN

接管a39e963(本地领先5)/远程356a3b1，先归档57文件再fetch，无分叉和残留实验进程。新增source/protocol先提交，再A恢复、v3观测续验、VI Q1/Q2及IV NR local；各run原参数/全候选/事件/失败/source hash均保存。独立只读A/B/Q2/IV审查完成。原工作树与分支接续；57崩溃前文件已保全0792acf，无重做R0/R1。原12端点FAIL保持；最新RECONSTRUCTED12/12通过闭链、原支、原界和source离散碰撞策略。A01四UNKNOWN保留，v3只修我方TCP观测（IV未赋值T7、V少2mm），A02仅4已存候选回放4/4。B Q1 868构造/13888IK、7/30请求合格；Q2再36构造全部节点合格，但四半严格h=.0025在depth3仍UNKNOWN，不能算RSS/RBS规划PASS。IV新增24固定±h全关节原NR局部24/24合格，不替旧6拒绝/3FAIL；全24主动角被NR改变。已推b686e7b，后续实际NR和报告继续提交。


## 2026-10-15 — P4 R2接续12run：fiber组件通过、旧48真实碰撞已补齐

source57ca473固定中心诊断；sourceb6e40a4执行6fiber；sourceca2c553补旧48碰撞。每项先冻结源码/协议、单次执行，输入/stdout/stderr/独占claim齐存。继续原p4-full-reproduction-pcs-study工作树，R0/R1及崩溃前57文件保全。CENTER_IMAGE01仅2固定active FK/J；FIBER_COMPONENT01固定6节点6/6，54FK/J、6源碰撞/798PQP，原Q2严格桥UNKNOWN及regular↔fiber未验证保持。旧48数学合格RSS分支一次补验：II10clear/8碰撞、III16clear/6碰撞、V0clear/8碰撞，96native/aligned、192内部FK/J、9996PQP API返回无错误；未重做700目标/5600IK，未执行原checkEE。V具体碰撞pair根因UNKNOWN，未据该批判整个模式无解。 最新211项对照为reports/P4_FULL_R2_CONTINUATION_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv/.md，前47历史列逐值保留；12run新账为results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V2.json，原9run快照不改。正式TableI仍0/22500，500000配对投影/约50000合法点对/Fig3–5/TableI–II及全部消融义务完整保留。P4全文仍部分完成，不P2/Isaac。


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
