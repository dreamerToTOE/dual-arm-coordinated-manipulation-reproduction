# P4 R2 IV原wrist-only：100固定目标×8解析支 PRE-TASK草案

2026-10-15。**工程准备草案，未冻结、未执行或编译。薄runner与frozen=false配置正在本轮准备。** 仅准备既有R2资格范围内尚未运行的IV wrist-only数学构造；不重复II/III/V已有700目标/5600 IK，不占VI B额度，VI新增14额度已由用户明确批准，B累计上限974；VI64组合已实际64/64通过独立离散资格，B累计974/974、余0。本项禁止任何新VI候选，不以本草案重置其claim或额度。

## PRE-TASK REPORT

- **目标与最小证据**：逐个检验原IV源腕部模式能否从固定R1被动臂输入得到真实降秩、原界内、闭链且分支身份可信的active解析根。完整保留100目标×8支=800次编号IK请求、所有失败/不可达根、秩谱、输入/输出/残差/限位；至少一个目标存在合格根才通过本组“存在数学正例”门。0/100也必须如实交付，不能换seed/样本或转新模式。
- **固定输入及种子**：只读 `results/p4_full/20261014T1545_R1_COMAU02/IV_native.jsonl`，SHA `3ae03596a6e5e52ba9e4c5b99fa10e61c713dcb9741860c7064563e4ca87b2f6`。取其中100条 `type=fk_sample`，原文件顺序及 `sample=0…99`；每条取 `q_rad[6:12]` 为arm2。原元数据base seed=20261014、effective seed=20265014、std::mt19937_64、原关节界uniform且无成功筛选；本次0 RNG，不重新生成这些角。
- **唯一模式与坐标**：原 `ckcComau2/validity_checkers/StateValidityCheckerRSS.cpp:260–307` 实际 `sMode=1`，设置被动 `q5=0`，其余五角逐值保留。既有脚本的Comau `apply_mode(...,1)`采用同一规则。无肘部/肩部新模式，无成功后换根或周期lift搜索，源解析返回的canonical代表原样保留；保留R1原q与新forced passive q分栏。此为确定性固定输入资格，不是源rand()/随机选根/拒绝重试分布的运行复现。
- **几何与闭链**：保留Comau原几何mm参数 `[344,524.5,199,1250,186.5,210,1250,116.5,22]`；arm1基座 `[-3000,0,0,0]`，arm2 `[3000,0,0,-3.1416]`；抓持 `Q=Tx(1800mm)`，`S=diag(-1,-1,1,1)`。以原独立FK/J一次得到每个forced passive `T2,J2`，固定active目标 `T1*=T2·S·Q^-1`；不得用数学π替换这些物理基座字面量或改抓持。解析IK数值修正继续标RECONSTRUCTED。
- **解析根与请求顺序**：按sample升序、branch=0…7升序完整枚举，目标总数100、IK请求800。仅复用现有 `build/p4_full/20261015_R2_SPATIAL01/comau_iv_batch`，SHA `acb44b837629fb8d822c4a238ab5014f78fd594dd1eb2e075015645e7370882a`；冻结其来源源码/patch/geometry/oracle SHA，当前不重编译。保留native返回成功/失败、原source分支编号与canonical代表；不因其他分支失败而跳过剩余编号，不用NR fallback。
- **原界与数值门**：两臂原角界为degrees `[−180,180], [−60,125], [−90,75], [−2700,2700], [−120,120], [−400,400]` 乘原3.1416/180；q4多圈代表不wrap。闭链位置maxabs≤1e−5 mm、旋转矩阵maxabs≤1e−5；rank平移mm→m，SVD相对阈值1e−6。所有source-accepted active根必须独立回代闭合，否则为实现soundness矛盾并立即停止下游。
- **分层资格与分母**：G0保留与旧700组可比较的“passive rank<6、真实闭链、两臂原界”判定，100目标与800分支分别报告；不能覆盖旧失败。G1另外报告被动rank是否恰为5、active请求编号是否包含于独立几何branch_set、独立物理6×12闭链Jacobian rank是否为6，保留各谱/branch meeting set，严禁把奇异腕强行分配唯一支。G0/G1与未来碰撞门分别列；G1未通过不能进入桥或规划。新增这些独立诊断不得伪称旧脚本早已检验。
- **本阶段调用与预算草案**：最多100个forced passive目标、800次IK分支请求、30秒墙钟/60秒CPU；计R2原3600/7200总账一次，0新增VI B构造，0碰撞/RBS/NR/规划。本项100次passive FK/J供目标、rank及其8支闭链复用；每个source-accepted根仅一次active FK/J，pose/J同时供回代、闭链残差、active rank和物理6×12 Jacobian复用。数学FK/J为100+A≤900（A为实际source-accepted根数），不调用会额外FK的residual_metrics/closure_vector_jacobian。已有batch的每个accepted K内部还自动调用一次native FK，单独计A≤800；显式native F操作0。完整800请求不等于800接受，不填上界冒充实测；事件逐次记录数学started/completed、external_K_dispatched/JSON_completed、native_accepted_FK_observed。已有binary没有K/FK内部start hook，其内部真实started明确UNOBSERVED，不能由请求数推断；中断未输出尾项UNKNOWN。旧700数学构造实测1.502717416墙钟/1.015161 CPU，只能作成本参考，不能保证新100成本。
- **碰撞与EE的后续门**：本数学阶段不查询碰撞。完成后将所有G1数学合格根按原sample/branch排序冻结为另一完整列表，再准备一次性原source-policy碰撞资格及成本测量，不反复查询同一候选、不只挑首个成功样本。v3 manifest已有IV native/aligned，不能将native TCP误差忽略；选定策略沿用已资格aligned，保存native差异。原IV `sampleSingular` 的collision/checkEE条件被注释，故独立安全资格与原源函数返回必须分开；以后可只读保存TCP作≥10mm诊断，未调用原checkEE不得写已执行。
- **碰撞成本预估与审批边界**：若数学合格根很多，理论最多800逻辑碰撞/1600变体/3200内部arm FK/J。旧48的13.069952121墙钟/12.882597 CPU线性估计800约217.83/214.71秒，仅为后续成本预报，当前不启动。须先冻结合格列表及有限前缀测成本，前缀结果在续验中复用，不能重复；再据实际查询数与R2余量报告具体完整预算。不因预算紧张删除其余候选、改通过门或伪称100目标都已碰撞资格通过。
- **停止/升级**：来源、原100行、数组顺序、分支/geometry/界/gate hash矛盾，非有限或accepted根回代不闭合，进程错误或时间帽均停止、保留前缀。常规不可达/限位/诊断拒绝完整计入；不换输入、不改q5之外的角、不加采样重试。若同机制已有三修证据，先根因审查；不能把0目标直接称RSS方法或论文理论错误。
- **冻结前必要工作**：新增薄runner `scripts/qualify_p4_full_r2_iv_rss_wrist_fixed100.py` 和 `configs/p4_full/r2_iv_rss_wrist_fixed100_qualification_v1.draft.json`（`frozen=false`）；展开100个原source行哈希、原q6与forced q6、800请求编号，目标矩阵由真实FK阶段生成留证；绑定本PRE、现有源码/二进制、source作者RSS文件、R1原文件、IV原NR失败/新有限局部资格记录、当前全部R2 execution/prior累计，BUILD工程成本保守计入R2总帽但另列为非科学。准备开始时ABB LOCAL01仍执行中，必须等待其execution及主流程总账审查；本轮已只读观察其execution落盘，现根代理V4总账已落盘，15execution=14science+1engineering，总帽保守已用wall285.28806236599576s/CPU264.43608s；配置绑定该V4及全部execution原SHA，状态更新为WAIT_INDEPENDENT_STATIC_REVIEW_AND_ROOT_FREEZE，不因此自动执行。先独立静态审查，再由父任务确认prior账目、冻结且commit后才运行。当前PRE本身不是运行授权或已完成实验。
- **输出与报告**：新独立run/claim，保输入/输出/日志、所有矩阵/谱/原支/原界、G0/G1分支及目标数、未执行尾项与实际wall/CPU。更新覆盖表时只能写IV固定wrist数学组件资格；完整RSS分布、所有理论奇异子集、碰撞、RBS、global planning及Fig/Table统计继续待验。

## PRIOR-ASSET CHECK

沿用已完成的D079 prior-project检索记录与 `P4_FULL_R2_SAVED_RSS_COLLISION_PRE_TASK_20261015.md` 分类：`qualify_rss_construction.py` 的固定输入/8支/旧G0口径是THIN_ADAPTER参考，现有IV corrected analytic binary/physical_nr/oracle/rss_geometry是直接只读复用，RunBudget/Evidence是运行保全薄适配，R1原输入和旧失败是TEST_ORACLE。FR3/MoveIt/FCL/Isaac/吸盘模型仅REFERENCE_ONLY，不能引入论文资格。未启动或修改旧项目。

原R2已执行IV有限局部NR24/24只支持其固定小扰动，未消除旧±.01组失败，也不代替RSS资格。本PRE保持这个边界。旧PRE原字节已归档聊天work，SHA `b681b9f8204bf0bae7b5127748c3d99a0638c625a5fe26bbf2d4e8a8f0b9f63f`。未来实际运行仍须独立静态审查及父任务确认范围、prior总账、冻结和有限账目；本草案没有编译、模型调用或科研预算消耗。


## 本轮工程准备与冻结边界

薄runner已实现，配置保持frozen=false，三项review标志全部false；本代理不调用--protocol、不编译、不commit、不创建科学run或claim。仅允许AST语法解析和--describe-protocol/--validate-draft（读取保存字节、hash、metadata和标量账目；0新FK/J/IK/碰撞）。独立审查通过后，父任务再确认15execution/V4账目、committed源码及配置，最后冻结运行。后续如新增科学/工程execution，当前配置必须停止匹配，不能默默继续用旧余额。

每target依固定顺序派发原8支，source-accepted根无任何周期lift/换根。已编译batch的K内部接受根还自动做一次native FK，此部分按保存JSON观察另计；没有内部start hook，不声称精确内部started。因soundness停止时已派发本target的其余原生输出仍全保留，未完成独立诊断与未派发后续target分别列出。数学完整通过才冻结全部G1根作为后续独立碰撞清单，不擅自启动该阶段。
