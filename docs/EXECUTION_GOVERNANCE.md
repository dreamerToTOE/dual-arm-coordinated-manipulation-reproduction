# Execution Governance — Scientific Progress Over Engineering Loops

This document defines how coding agents decide **what is worth fixing now**.

## 1. The central rule
Every task must answer one scientific/benchmark question.

Do not optimize a diagnostic subsystem beyond what is required to answer that question.

The task specification must therefore separate:
- **Scientific objective**
- **Minimum sufficient evidence**
- **Non-goals**
- **Preferred method**
- **Fallback method**
- **Attempt budget**
- **Stop/escalation condition**
- **Deferred issues**

## 2. Blocker taxonomy

### TASK-BLOCKING
Without resolving it, the task's required scientific conclusion is invalid or unavailable.

### DEFERRED
Real issue, but explicitly owned by a later task.

### KNOWN LIMITATION
Uncertainty remains, but the current claim can be stated honestly with that limitation.

### LEGACY
Belongs to historical application/demo code and is not part of the current benchmark.

Only TASK-BLOCKING issues justify extending the current task by default.

## 3. Default engineering attempt budget
For one root blocker:
- Attempt 1: diagnose.
- Attempt 2: implement the most evidence-supported fix.
- Attempt 3: use a bounded fallback or alternative measurement route.

If still unresolved: stop and escalate.

Do not automatically create serial variants such as probe04/probe05/probe06 without a new user-approved reason.

## 4. Escalation decision
After the attempt budget is exhausted, answer:

1. What scientific statement were we trying to establish?
2. What has already been established?
3. What remains uncertain?
4. Does that uncertainty invalidate the task?
5. Is there a lower-cost evidence route?
6. Should the issue be deferred or accepted as a limitation?

The coding agent must recommend one of:
- **CONTINUE** — truly task-blocking and worth another approved attempt.
- **FALLBACK** — use another acceptable evidence method.
- **DEFER** — assign to a later task/bug owner.
- **ACCEPT LIMITATION** — record and proceed.
- **STOP FOR USER** — benchmark/theory decision required.

## 5. Evidence tiers
Use the lowest tier that is sufficient.

### Tier 1 — Sanity evidence
Enough to reject obvious model/interface errors.

### Tier 2 — Task acceptance evidence
Reproducible evidence sufficient for the task's PASS criteria.

### Tier 3 — Research-grade comparison evidence
Repeated, logged, fair evidence needed for a paper table/claim.

### Tier 4 — Subsystem equivalence / exhaustive proof
Only pursue if the research question explicitly requires it.

A TASK01 benchmark setup usually needs Tier 2, not Tier 4.

## 6. Examples for this repository

### TASK01 collision-model difference
Scientific requirement:
critical benchmark states must not show unexpected collision in the final Isaac environment.

Acceptable evidence:
targeted critical-state sanity/replay plus recorded model discrepancy.

Not automatically required:
proving exact equivalence of FCL STL and PhysX cooked convex hulls or perfect zero-step query-cache semantics.

### TASK10-IS force/wrench
Scientific requirement:
validated wrench semantics for P2's internal-force claims.

This **is** task-blocking for P2 Isaac evaluation, but it is DEFERRED for TASK01/P4.

### Legacy five-Cube Task27
Useful application/stress-test evidence, but LEGACY with respect to the one-Cube scientific benchmark.

## 7. Task writing rule
When creating or revising a task, use `docs/tasks/TASK_TEMPLATE.md`.
Technical details belong under Preferred Method; do not accidentally promote them into Requirements.

## 8. Progress review trigger
A task requires a governance review when any of the following occurs:
- same root blocker reaches three implementation iterations;
- task duration/commit count grows without new scientific evidence;
- new subsystem is added;
- acceptance criteria keep expanding;
- agent proposes a fourth probe/version for the same root issue;
- a later-task issue begins blocking the current task.

At that point, update STATUS with a short scope review before further coding.


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
