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
