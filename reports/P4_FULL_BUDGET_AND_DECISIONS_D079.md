# P4 D079 计算预算与待裁决清单

## 已冻结的当前执行额度

本轮首批 R1 数学/构建资格总墙时1800s，每原生模型构建和单诊断120s；最多6个模型构建目标，固定seed20261014，无正式规划调用。源码/协议提交后执行；超限保存前缀，不补跑未声明样本。另限20分钟进行依赖获取与编译，工程运行与科学试次分账。旧RSS/PCS保存数据回放属于只读历史证据，不计新规划统计。完整定义见 configs/p4_full/r1_qualification_v1.json。

## 完整论文实验额度：不缩减

Table I：环境II–VI × RRT/Bi-RRT/SBL × RSS/PCS/NR，共45单元，每单元500次，22500调用，每调用1000秒。最坏6250核小时（单核串行260.4天；8物理核理想上限约32.55天墙时，尚未包括其他实验和并发计时失真）。本机 i7-10700F/8核16线程、46GiB，论文i7-6700HQ/8GB；实际墙时必须用资格后pilot实测，不能据原秒数承诺同机器性能。

另有：同500000 ambient输入的APC/NR投影各500000、空间50k合法点对RSS/PCS/NR；平面Fig3上图五m+NR，下图全部m1…20+NR；Fig5配对投影距离变化；空间去障碍、PCS各fixed划分、窄通道/复杂障碍/三臂机制；新增T30分布诊断。作者平面mode4每条件1000次/CLI时间可变；论文未明确生产重复数。作者visibility驱动以“成功数”达到目标且无上限，不能照搬为有限成本/全部点对成功率。

上述正式22500调用规模完整保留，尚未申请执行6250核小时。不能用10条资格或pilot替换500正式重复，也不删除超时/原dash单元。先量化原生单次成本、构建和模型可执行性，再提交可执行批次、硬上限与停止条件供用户裁决。

## 科学与来源待裁决

1. 原最终发表PDF未获取；现有8页作者accepted稿作为明确版次，不断言相同最终排版。额外视频未获取，不断言不存在。
2. 现有七个作者快照覆盖全部I–VI，但生产软件版本、seed、数据到论文图表链未确定。绝不再把Comau/三臂笼统判missing。
3. Fig4图注I与正文II冲突；保留冲突，II作者模型可做明确II对应检验，不能将其称图注消歧。
4. 作者ABB测试默认关节界与原500k“无界”文字不同；以原实验文字为本次无界投影条件，保留源测试差异。原clean步长也与TableII不同。
5. 式7标签、RSS elbow-only固定值、VI RSS移植/NR顺序核：先独立有限资格，未验证前UNKNOWN；需要改变方法/模型时暂停，不默改常数或将另一方法冒名。
6. 所有源快照无统一LICENSE，作者源和网格只外部引用，不在公开库搬运。OMPL/BSD头、KDL/LGPL、PQP上游许可逐项核查。本次提交独立驱动、配置、哈希与可复查日志。
7. 完整性能采样/profiling未知项需另冻科学协议：候选步长网格、原计数与配对统计、所有full/fixed划分、失败删失及高密路径oracle。不会在见到结果后改口径。

## 当前状态

R0清单与来源已建立；R1真实运行尚未开始；R2正式规划0；R4未结题。当前不是论文FULL。用户审批是明确资源/科学路线的停点，不以已上传规范视作已运行。


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


## 2026-10-15 — P4 R2接续12run：fiber组件通过、旧48真实碰撞已补齐

当前12run自身成本合计95.365357389998wall秒/45.058033CPU秒，R2余3504.634642610002/7154.941967。VI B累计910构造、54.513982463999wall/13.327177CPU，余50构造/125.486017536001wall/346.672823CPU。旧48仅扣R2、不扣B。不得重置claim、重跑原预算或重复加cumulative。 最新211项对照为reports/P4_FULL_R2_CONTINUATION_ORIGINAL_VS_REPRODUCED_COVERAGE_20261015.csv/.md，前47历史列逐值保留；12run新账为results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER_V2.json，原9run快照不改。正式TableI仍0/22500，500000配对投影/约50000合法点对/Fig3–5/TableI–II及全部消融义务完整保留。P4全文仍部分完成，不P2/Isaac。 新三项依次wall/CPU=.208154164/.208192、1.185148035998/1.167442、13.069952120997/12.882597。工程与保存分析另账，不拿上限作实耗。


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


## 2026-10-16 — D64仅补未派发两项完成，分次保存资格独立通过

095c56c冻结TAIL02后唯一执行，仅原62/63、D-fixed/III/trace/seed7，1新进程/2请求均正常返回、exit0/reaped、新UNKNOWN空。旧0..61只精确复用raw；1374/1374人员独立保存检查通过，全部64响应/32plain-trace对/9真实进程、原六维L2/state/对称/role0/四原同点反例完整核对。标签SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO，仅距离接口分次证书；原D64 STOP、61complete、UNKNOWN[61,62,63]、末-9和false门永久保持，不能宣称原8进程单run通过。trace累计5mesh+32distance，plain内部/库seed draw仍UNOBSERVED；close_group仅冻结源码成功门推断，不冒称保存现场快照。

本项内部样本.9946544039994478wall/.9409050000000001CPU；独占外层GNUtime覆盖最终execution/receipt/退出，上界1.21wall/.99CPU，满足新5/10且只替换计费一次。V14共32execution=25科学运行账+7工程，累计chargedwall567.215705375994/CPU518.608923；历史D64末端未测尾部仍UNKNOWN，余额仅上界。新V14保全PASS，旧1028科学文件、57崩溃文件8482891B/tar、另5worktree13未提交、V13/211前138列逐值保持，新142列完整表。VI974余0、正式0/22500、全部原文义务及统计规模不缩。

见reports/P4_FULL_R2_ABB_CBIRRT_D_TAIL02_POST_TASK_20261016.md、TAIL02_SAVED_INDEPENDENT_POST、CBIRRT_D_TAIL_SPLIT完整对照表。下一L12须新版完整前置契约消费真实TAIL02/独立aggregate/外层上界/V14，不能OR状态绕原L门；原L源码/PRE保留。拟原3边12调用、30/60、无新独立物理oracle；通过后S单solve与P完整路径分阶段冻结。正式成本pilot/大预算仍后续，不P2/Isaac，不提前结题Word/PDF。
