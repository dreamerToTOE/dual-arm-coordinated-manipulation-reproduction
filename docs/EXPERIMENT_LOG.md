# EXPERIMENT_LOG

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

本阶段尚未执行数值/滤波/控制资格或运输，编译不是科学PASS；首跑将在源码提交后单独归档。


## 2026-10-14 — P2 stage2资格FAIL_STOP；控制run0

- science9194f9f：scripts/qualify_p2_dynamics.py → results/20261014_P2_stage2_dynamics01；11已完成检查通过，首条lockedEE5s在120秒限止t3.324s（最后250Hz日志3.32s/831条），整体资格wall120.050961s含前置/终止归档。未完成5s/halfstep；summary FAIL_STOP。
- science385d08d：scripts/audit_p2_stage2_numerics.py → results/20261014_P2_stage2_numerical_audit01；4固定数学点/FD42孤立map，wall11.486919s，无新ODE轨迹、无控制；C coarse倍率2.730136/half.654550，原4ms Euler未测量预测有风险但不证明IESEKF发散。
- 控制ledger：主20、代表5、GT/半步诊断5全部NOT_EXECUTED，未补0指标、未称20次实际失败。小修仍1/3余2，30/74/81、120/7200预算不扩大。


## 2026-10-14 — P2 stage2运行前声明

本轮控制实验尚0；动力学数学资格待冻结源码后运行。20主case、5代表case、5GT/步长诊断沿原协议，初套30/未来至多74；120s/case、7200s整体不扩展。首门失败保留日志并停止后续。


## 2026-10-14 — P2有限接触几何资格（非控制实验）

初版ac9e35d：results/20261013_P2_contact_geometry_qualification01/，66/66程序PASS；符号/覆盖问题使其交付资格INCOMPLETE，raw不改。
修正1：b58e66f/51696a8，核心几何SHA47557da9…两轮相同；−KΔτ日志、恢复负例补齐，原输入/门限不改。

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/qualify_p2_contact_geometry.py --output-dir results/20261014_P2_contact_geometry_qualification02

68case=36有限导数+6坐标+2基+9H代数+9积分+6切换；全部资格通过。线性FD2.81893e−11m/s、角FD7.835997e−10rad/s，sliding自由漂移3.18535e−13m、pivot3.29656e−12rad。
负切换为独立合成的released/restored无效预载，不是实际控制force；dualH转置功率项只代数自洽。所有数学状态/检查值/失败判断保存JSONL。
原临时环境启动命令exit127，Python未启动/case0；失败另存environment/launch_failure.json。有效run版本与原一致。
[原始/独立归档](../results/20261014_P2_contact_geometry_qualification02/independent_artifact_audit.json)。主闭环/GT控制/ODE/IESEKF矩阵均NOT_EXECUTED，小修1/3余2，P4/RSS/Isaac/ROS/P3运行0。

## 2026-10-13 — P2原文数学一致性诊断（非控制实验）

一次实际命令：

    /tmp/p4-three-source.sHcHgg/venv/bin/python scripts/audit_p2_kinematic_identities.py --output results/20261013_P2_original_audit/kinematic_identity_audit.json

Python3.10.12/NumPy1.24.4/SciPy1.8.0；固定解析输入，无随机采样/增益搜索。
式15 D=I、自由x、EE静止、物体.01m/s、dt4ms：印刷正号D平移80μm，负号局部候选0；仅证明符号反例，不认证有限形变完整模型。
式22对固定O/G的单接触弹性式9做独立矩阵Exp/Log中央差分；eps1e−4/1e−5/1e−6全部保存。1e−6时原印刷式平移导数分量误差约−.095183/−.133877/.009254N/s；直接微分残差<4.4e−10逐分量。
结果为待裁决的不一致，不是论文公式全通过或内力控制实验。hK不是时变W/H/阻尼下完整hI导数。
闭环run=0、小修0/3，所有未来主矩阵标NOT_EXECUTED；协议variant=null/executable=false。P4新实验/追加RSS=0。

## 2026-10-13 — P4三方法既有实验归档及独立核验

协议6d64b26；初版2ab2348；修正1/2/3分别41689ef/17202df/3d51ca0。
真实科学运行命令见各run metadata；最终命令为：

    /tmp/p4-three-source.sHcHgg/venv/bin/python scripts/run_p4_three_methods.py --run-id 20261013_P4_three_methods_round3

round0启动路径错误未建logger；修正1保留traceback。round1为16/17测试、未规划；
round2为17测试通过、完整RSS超时1次、PCS写gzip中断及ABORTED；这些不混入最终分母。
round3：E0/E1×outer200/800×RSS/PCS/NR×seed[7,23,41,101,20261013]共60统计；
每算法E0/200/seed7重复一次，共63份原件。共同5s/2000nodes/.6rad/.05rad/1e-8闭链；
Python3.10.12、NumPy1.24.4、Shapely2.1.2/GEOS3.13.1、i7-10700F。
RSS20超时，PCS20成功，NR20成功；全调用均时5.000134/.581200/.035464s。
RSS313请求/9996构造/0合格奇异点；PCS树边520p16+92p0、解边92p0；3重复中RSS载荷不一致。
原始数据在results/20261013_P4_three_methods_round1、round2、round3，全量保留。

本轮只复核已有科学数据，没有重新运行统计套件或新增随机seed。
新命令：python3 scripts/verify_p4_three_delivery.py --output reports/P4_THREE_METHOD_DELIVERY_QA.json；
17项unittest复核、保存证据QA、报告图例排版及LibreOffice导出。
独立几何3312点全部合格，净距与GEOS最大差2.78e-17m；131接手文件/561旧文件/9来源SHA不变。
Word18页/16公式/10图；排版修订科研数值变化0。全部科学结论仍部分完成，没有物理执行。

## 2026-10-12 — P4报告存量出图：不是新增科学实验

科学规划/IK/NR/FCL查询/物理/机器人调用均0；仅读取并校验原始结果。
统计保持TASK03历史219/293位置超原0.05μm，TASK04 194/194邻域与293/293诊断，
TASK05 10正例/3负例，TASK06 14SUCCESS+4NODE_LIMIT/18调用/9对重复；
私有障碍直连仍PROJECTION_JUMP且被拒中点未FCL查询。IS-A原单次seed7
96nodes/94edges/1869q/.213194502s计算；B0左J4 index860 .236039°不能执行。
39来源SHA、18原gzip读回、1869q/残差/余量和原输入不变检查通过；
1212个真实投影初值/更新仅派生CSV，不补零/延长。报告23页/16公式/10中文图；
所有几何曲线无执行时间，min_distance仍UNAVAILABLE，不添加新统计显著性结论。
[机器可读检查](../reports/p4_report_assets/delivery_check.json)。

## 2026-10-12 — B0 固定数据分析一次，非新规划或物理实验

预声明c20c381，源码e1a2e22；run=20261012_TASK06_IS_B0_path_review01。
原1869q SHA073723b32e4bc392af3fb0a182a03e92e45026771dc1d46fa9b7276b21614781不变。
最小margin左J4 index860=.004119662522rad，q−.121019662522，上限−.1169。
左J4累计4.152684973rad vs净变化.430655518rad；全L2长11.940815548rad；
邻接maxL2 .009923957011、Linf .005315105379（原.01门限合格），24逐关节反转。
全部原source620/artifact25、树边94、独立点1869及URDF限位14一致，复核无新FCL。
原闭链max8.62520825e-9m/5.30773506e-9rad；原最小碰撞距离仍未查询。
7/7纯合成软件测试；3组图表和完整CSV/JSON，seed UNSET，simulation/step null。
结果INCOMPLETE仅指执行准备不满足，不更改原P4成功；未构造时间轨迹、v/a不认证。
新规划/IK/NR/FCL/Isaac/ROS服务/命令均0，原输入及旧资产hash前后不变。
[完整结果](../results/20261012_TASK06_IS_B0_path_review01/summary.json) ·
[POST-TASK REPORT](../reports/TASK06_IS_B0_PRE_EXECUTION_REVIEW.md)。

## 2026-10-12 — TASK06-IS-A V2 唯一名义端点/规划进程（离线）

协议20fe06d，测试c88a80c；第一阶段历史失败未改。独立v2保留六个原ID world BOX、
Task26 .628m内宽、slotB Cube2静态障碍；原.120m Cube、.800kg、工具/ACM/门限不变。
run02仅source wrapper启动失败：PYTHONPATH=.覆盖ROS路径，xacro无法import ament包；
ABORTED/原日志保留，无native/IK/搜索。完整环境展开成功、坏环境import失败为只读诊断。
一次命令纠正保留PYTHONPATH，新run03实际科学进程1次，硬上限120s。
START/GOAL各1/64对，seed-only HOME→accepted START，两RNG初始化但draw0；原NR各1更新。
规划seed7：SUCCESS，96nodes(63/33)，94edges，1869点，.213194502s compute，
长度11.940815548rad，最大闭链8.62520825e-9m/5.30773506e-9rad，最小关节余量.004119663rad。
规划FCL1964次free，加端点2次、独立输出1869次，共3835状态检查；没有native距离查询。
14随机draw/1sample；94candidate projection中1失败保留，RBS1774calls/0fail。
原software regression15+72tests/4CTest目标PASS；598原文件/8STL/4旧资产hash不变。
25artifact/620sourcehash、gz原19140034bytes及SHA核验一致。seed41/20261012未运行。
没有物理时间/step/执行命令/正式计分；当前适配初步通过，不回判原TASK06整体。
[完整证据](../results/20261012_TASK06_IS_A_nominal_scene03/summary.json) ·
[失败run02](../results/20261012_TASK06_IS_A_nominal_scene02/summary.json) ·
[报告](../reports/TASK06_IS_A_NOMINAL_SCENE02.md)。交付后停止。

## 2026-10-12 — TASK06-IS-A：来源拒绝证据与独立软件检查（无仿真）

预声明462e6b1，测试源码a7223e3。`20261012_TASK06_IS_A_scene_adapter01` 唯一
runner返回1，原结果ABORTED：SOURCE_MODEL_INPUT_AUDIT，carriage_y [-.314,.314]
!=[-.303,.303]。protocol SHA256=0ea7988f42814027d711fca646d8623e88c192f715cef9dba76b3c35b75d43db。
条件种子7/41/20261012均未启用；科学搜索0、IK0、原生FCL状态查询0、执行0；
simulation_time/physics_step=null。原native加载/xacro核验未到达，不能称FCL通过。
592文件before/after相同，原始summary/result/metadata/failure保留且不补写为成功。

`20261012_TASK06_IS_A_software_checks01` 是分开的单次软件证据：configure60s、
build240s、unittest每项60s、CTest60s硬上限；配置/编译exit0，8+72Python测试及
4个合成数学CTest目标通过。Python只有部分raw stdout+明确标注的最终观测摘要，
不冒充完整原始stdout；没有为补输出重跑。源码静态读回只是审计记录，无新模型运行。
路径残差/长度/节点/规划耗时/关节余量未计算，最近距离不可用；不是物理或科研指标。
[来源失败](../results/20261012_TASK06_IS_A_scene_adapter01/summary.json) ·
[软件范围](../results/20261012_TASK06_IS_A_software_checks01/summary.json) ·
[报告](../reports/TASK06_IS_A_SCENE_ADAPTER01.md)。

## 2026-10-12 — TASK06 review annotation only; NO NEW EXPERIMENT

D054 review of74d4276 accepts coreoffline softwarePASSCANDIDATE only; overall
TASK06PARTIAL/rawsuiteFAILURE remain. Existing40artifactSHA256 checks andinventory
readback pass;18fixedcalls/9repeatpairs/4NODE_LIMIT/both553node148edge paths retained.
Directfailure remainsPROJECTION_JUMP with noFCLquery at rejected midpoint.
No original result/log/metric/threshold rewritten; no planner/FCL/IK/physics/test
suite invoked. This entry is review provenance, not an additional run or trial.
Future standalone P4 obstacle evaluation pending separately, not authorized now.
[Review](../reports/TASK06_REVIEW_CLOSEOUT.md).

## 2026-10-12 — TASK06 constrained_search01 compile-only; search02 sole fixed suite

D052 protocol877decd/SHA74a1aa3864da… committed/pushed before experiments.
01sourceba20c98 failsC++JSON/Eigen/keyconversion atbuild, scientificcalls0;
oneexplicitconversionfix29a9d5c, noalgorithm/protocoltuning.02Releasebuild+72TASK02+
CTest4/4(93/108/300/2757assertions)+435realFD+194/293TASK04+10positive/3negative
TASK05pass. Exactly18plan calls: simple/nontrivial7/41/20261012twice allSUCCESS;
private obstacle7/41twiceNODE_LIMIT600;20261012twiceSUCCESS553nodes/148solution
edges/2261points.9repeatpairs payload/path/counters/status exact.18-callprojection
50602/fail26;nativeFCLstatequeries55118/collisionpositive392; costs.072159–.883389s
planfunctiononly, notexecution/performancebenchmark. SuccessmaxC9.91760409e-9m/
9.98385517e-9rad, minjointmargin.001980096rad. No native distance query;UNAVAILABLE.
Direct obstacle0→100 returnsPROJECTION_JUMP, correction.0869493378rad>.020guard,
FCLnullatmidpoint; onlypredeclaredgap, overallTASK06PARTIAL/nativecheckerexit1.
Nativebounds/collisionroot negatives reject;allraw/typedFAILUREevidence retained.
Onecompletefixedsuite,noextra seeds/budget/scenechanges;23losslessgzoriginals,
40artifact/35sourcehashesmatch,536protected/8meshes/4oldassets unchangedbefore/after.
Simtime/stepnull, commands0, qualificationofflineonly. OriginalTASK03precisionFAIL
unchanged;TASK02IN_PROGRESS/DDEFERRED, BenchmarkDRAFT. NoIsaac/services/robot/
Task26/TASK07. Saved-evidencehashreadback is not a new planning experiment.
[POST-TASK REPORT](../reports/TASK06_CONSTRAINED_RRTCONNECT01.md),
[run02summary](../results/20261012_TASK06_constrained_search02/summary.json).

## 2026-10-09 — TASK05 local_connection01/02, bounded offline suite only

D050 pre-experimentprotocol55e53493… at e308a71; no later numerical changes.
Sources e335e72 (run01) and1387808 (run02 diagnostic-onlyfix). Each10commands0:
configure/build,72TASK02,CTest3/3,93TASK03/108TASK04/300TASK05mathassertions,
435actualFR3FDconfigs,194+293TASK04projections and10realRBSpositive+3negativecases.
Perrun:32pathpointoccurrences,14midpointcalls,35nativeFCLqueries; maxclosure
1.8427461484e-10m/2.1963382036e-9rad; minnativejointmargin.6339639322rad;
maxadjacentL2.00965945294rad/Linf.00619235117rad. Genuine negative FCL returns
COLLISION with12ROBOT_ENV+4CUBE_ENV contacts, no failedendpoint addedtoprefix.
Run01warning/worldlinkqueryERROR retained; no scientific failure. Only diagnostic
lookup and indentation corrected, run02clean, checkedq/status/prefixexactlyequal.
Final tiny-suitecompute.004389573sec (wallcostonly, NOT robotcycletime).
Metadata/artifacthasheschecked;505protected/8STLs/4oldassets unchanged. Full outputs
results/20261009_TASK05_local_connection0{1,2}/; seedUNSET,physicstime/stepnull,
typedSUCCESS scopeofflineonly/UNQUALIFIED. NoIsaac/ROSservices/controllers/IK/
Task26/Benchmark edits. TASK05PASSCANDIDATE onlydiscrete, not continuous safety or
fullP4/physicalclaim. TASK02IN_PROGRESS/DDEFERRED, BenchmarkDRAFT; stopforreview.
[Report](../reports/TASK05_LOCAL_CONNECTION01.md).

## 2026-10-09 — TASK04 finite projection03, negative build01/02 retained

Offline Eigen/MoveIt core2.5.9/Python; invocation15951f7 plus working-source hashes;
D048 protocol precommitted, no tuning:1e-8m/1e-8rad,40fullupdates,SVDcutoff,
exactnativebounds. ExplicitseedUNSET/noRNG.01configurefails overwrittenPYTHONPATH
then wronglegacyroot;02generationfails childfastcdrtargetscope. Both0projectioncalls,
rawnegative logs/results retained.03all8build/testcommands0,72TASK02/93TASK03/
108TASK04checks,435FD configs,CTest2/2PASS.97x2requiredconverge:maxfinal3.69727377e-9m/
9.13054516e-9rad,max3updates,repeatqdiff0. Requiredcompute6.707253ms(total),.034573ms(mean).
293originalGdiagnosesconverge1update:maxfinal2.52269308e-11m/3.17694454e-11rad;
compute4.717277ms. Costs are projection-only steady wall, not physical time.
OriginalTASK03FAIL219/293,max.435027826256micrometres>.05unchanged.487exactcalls;
IK/FCL/execution0;477protected/4legacyassets unchanged. Simstamp/stepnull,
UNQUALIFIED typedSUCCESS offlineonly. Evidence results/20261009_TASK04_projection0{1,2,3}.
No physics/services/Task26/Benchmark/TASK05/06; TASK04PASSCANDIDATE, stopforreview.
[Report](../reports/TASK04_NR_PROJECTION01.md).

## 2026-10-09 — 20261009_TASK03_closure02 offline regression/model math

Task: TASK03; P4_CLOSURE_MATH; offline Eigen/MoveIt core2.5.9/Python (no services).
Base:36c95ab; evidence invocation commit9b59289 plus source-hashed working files.
Seed:null / UNSET; deterministic equations/data, no random IK/RNG.
Config: unchanged archived20261007 full-single-Cube grasp config, not benchmark_v1.
Commands: cmake configure/build (Release,parallel2); sourced installed dependencies;
`PYTHONPATH=. /usr/bin/python3 scripts/run_task03_offline.py --run-id 20261009_TASK03_closure02`.
Actual command argv/exit codes captured in summary. **All four exits0**:72A/B/C,
93math,CTest and real-model software check.435derivativeconfigs, centralworst3.281e-10,
five-point1.545e-10, FK0m/6.107e-16rad; archivedminjointmargin.461828rad.
Acceptance: originalpositionclosuremax.435μm >.05μm,219/293fail; attitude passes.
**TASK03 PARTIAL; typed result INCOMPLETE**, not robot/benchmark SUCCESS.
Artifacts: results/20261009_TASK03_closure02/{metadata,summary,result,model_metrics}.json
and task02_regression/task03_math/ctest/real_model logs. Full perstate/derivative and
example originalC/Jc retained; prior closure01 mathematical output retained.
No simulation stamp/step/session invented; qualification UNQUALIFIED offline math;
no physics/ROS nodes/MoveIt server/Task26 invocation, IK/FCL/projection0. Source/artifact
hashes and protected before/after hashes saved. Results do not prove held-object
stability, collision freedom, benchmark correctness or formal synchronized sensing.
Report: reports/TASK03_CLOSURE_CONSTRAINT01.md. Stop, no automatic TASK04.

## 2026-10-09 — TASK02-C synthetic cross-input metrics; NO PHYSICAL EXPERIMENT

Final stdlib unittest72/72PASS, exit0, engineering wall2.540s (A14+B19+C39). Both independent test formats decode the same4sample trajectory, valid4/rejected0: A relativeTCP0, midpointmax.030m, positionRMSE.0187082869338697m, attitudeRMS.1870828693rad; B progress0,1/3,2/3,1, finaltargetroundoff≈5.55e−17m, formalinsertiontimenull. Synthetic session/stamps/steps are constructed fixtures, not Isaac/MuJoCo data or scoring evidence. FORMAL duration code path is tested only with explicit fabricated declared-post-step TEST_DOUBLE, never published as native measurement. Tests reject session/clock/frame/qualification mixing and invalid/missing input, retain rejection reasons; actual legacyA snapshot compatibility only. Source hashes and immutable A/B/YAML/old4assets captured. Isaac/ROS/MoveIt/Task26/build/physics/robot/suction/rail calls0; no scientific or physical safety result. [Metadata](../results/20261009_TASK02_metrics_measurements01/metadata.json), [example](../results/20261009_TASK02_metrics_measurements01/example_metrics.json), [report](../reports/TASK02_METRICS_MEASUREMENTS01.md).

## 2026-10-09 — TASK02-B synthetic/file acceptance; NO PHYSICAL EXPERIMENT

Final Python3.10.12 stdlib suite33/33PASS, exit0, recorded2.265s engineering wall duration (19newB +14A regressions). Pure rejection/roundtrip checks cover command side-effect tripwires, target/units, event causal identity/confirmation, clock/step ordering, false scientific upgrade, four results, ABORTED including empty exception, INCOMPLETE, immutable old run dirs, SET/UNSET seed and deterministic identical-output bytes. A saved **deliberate synthetic FAILURE**, not a robot failure, logs1command/3events/1historical state; actual metadata/result/events read back and source/artifact hashes retained. Old state is the TASK02-A stored converted snapshot, not freshly sampled. Synthetic sim_ns50000000000/step10 are fixture values only, not Isaac time. Old accepted assets4/4, old worktreeclean, benchmark_v1SHAfbef560a… unchanged. Isaac/ROS/MoveIt/SG/rail/robot/build calls0; no new scientific sample/safety/force result. [Metadata](../results/20261009_TASK02_exchange_logging01/metadata.json), [raw fixture](../results/20261009_TASK02_exchange_logging01/synthetic_observation.json), [report](../reports/TASK02_EXCHANGE_LOGGING01.md).

## 2026-10-09 — TASK02-A offline contracts only; NO NEW PHYSICAL EXPERIMENT

Python standard-library unit tests14/14 PASS (recorded0.009s, engineering wall duration); read-only converter exit0 using previously saved run02 final snapshot SHA10c412fd… and approved local source/assets4/4 hash match. Output SI/xyzw actual14q/nativebase/legacyUSD TCP+objects with original diagnostic timeline/ROSclock; scientific stamp/stepnull/post_stepfalse. Negative tests cover false post-step claims, invalid frame/quaternion/DOF/numeric/object mapping, asset mismatch/path escape, callback errors retained. Neither this conversion nor synthetic clocks produce native state or new safety/force/physical evidence. Isaac/ROS/MoveIt/build/robot/SG/rail invocations0. [Metadata](../results/20261009_TASK02_foundation_interface01/metadata.json), [report](../reports/TASK02_FOUNDATION_INTERFACE01.md). Original failed/successful physical runs unchanged.

## 2026-10-09 — Patched predecessor GUI physical retry01/02 (FAIL then PASS)

Baseline: original631b1f+authorized5ed0c96 two softwarefixes; existingvisibleGUI39508, originalscene/bridge/MoveIt, batch1deep→shallow, time_scale3/ROS_LOCALHOST_ONLY0; no new seedoverride. Eachattemptfresh originalshutdown→Stop→scene→Play→bridge; originalpreflight600s/physical1200s engineeringcaps, none triggered. Attempt1 preflight0/physical1, deepcell.993mm/deepgap.152mm/sidegap.982mm then shallowRIGHT_OUTER_DESCENT leftcontacthold25s/max3.931858deg fail. Attempt2 preflight0/physical0: deepcell1.181mm/deepgap.297mm/sidegap1.143mm; shallowcell.376mm/originalnominalpriorCube gap.369mm/sidegap.070mm; pushpeakmonitor23.48/28.98Nm; actualHOMEleft.059/right.062deg,batchPASS. FinalbothSGOPEN/railmeasuredtarget.750/baseXconsistent/callbackerrors{}; finalCube01laterpositiondiffersfromitsownacceptancesample, retainedrawsnapshot. GUIpaused/ownedROSlaunchCtrl-C130each. Physicalbudget2/3, thirdNOT_RUNafterfullsuccess. Sameimmutableinputs before/after; noforce/clock/material/controller/modelchanges. LegacyUSD/ROSfeedbacknotatomicscientificpost-step, no reliability/continuouscollision orwrenchclaim. [Run01metadata](../results/20261009_TASK01_predecessor_patched_runtime01/metadata.json), [run02metadata](../results/20261009_TASK01_predecessor_patched_runtime02/metadata.json), [fullreview](../reports/TASK01_PREDECESSOR_PATCHED_RUNTIME_REVIEW.md).


## 2026-10-09 — Side-preflight software correction; NO NEW ISAAC EXPERIMENT

Source baseline631b1f→authorized patch5ed0c96, sourceSHA8c984cc7…; production1file/+7−6. Three pure tests in1.913s exit0: extracted actual distance function with small owned-transform RobotState type double/ASAN, exact/8mm/overshoot/empty arithmetic, shared macro gate and unchanged constexpr/scope. This does not run real FK/IK/FCL/PhysX or re-evaluate old failed trajectories. OriginalTask26 Release build exit0 (~45s engineering); separate Task27 compile compatibility check retained. Controller joint/suction/rail commands0; scene/reset/bridge/MoveIt/planning-only/physical invocations0; no new native physics state/time. Prior physical failure is not replaced by softwarePASS. [Software evidence](../results/20261009_TASK01_predecessor_side_fix01/metadata.json), [limits/report](../reports/TASK01_PREDECESSOR_SIDE_PREFLIGHT_FIX.md).

## 2026-10-09 — Predecessor foundation01: preflight PASS, original physical chain FAIL

- Pin631b1f; original batch1 two Cubes approved; source changes0, normal visible GUI, original scene/bridge/controller/model/config. One target build exit0; planning-only1/1 exit0; physical1/1 exit1 before1200s engineering cap. No extra trial or repair. Raw evidence: `results/20261009_TASK01_predecessor_foundation01/`.
- First Cube bilateral lift/transport/descent/release, helper/pusher transition, rails.650→.750, fresh world shift+.100 and right rear regrasp completed. Regrasp drift1.12mm. Original 16-slice +X push completed; final lag.680mm, deep seat gap+.680mm/Zerror.153mm, peak monitored joint torque48.56Nm under original80Nm guard. These are engineering-prefix metrics, not completed placement/force validation.
- Original side candidates1–5,7–8 fail right backstop segment8 FK line-deviation; candidate6 fails left SIDE_PRESS. Example candidate8 deviations304.093/228.603/280.976/1037.690mm exceed unchanged5mm gate despite fraction1. No actual side-compaction commands, second Cube or HOME; no `FCL collision`/pair reported in physical log. Root cause not isolated.
- Original abort both SG OPEN; final Cube01 USD center(1.099852324,.061820220,.260000050)m, Cube02 still supply; railsboth.750/arrived, callback errors{}. GUI paused without reset; owned MoveIt interrupted exit130, children gone. Snapshot is legacy USD/ROS-clock engineering feedback, not atomic native post-step scientific evidence. ~221.22s log interval is not performance score/simulation timestamp. **TASK01PARTIAL / FOUNDATIONNOT_QUALIFIED / STOPFORUSER**. [Result and evidence limits](../reports/TASK01_PREDECESSOR_FOUNDATION_RUNTIME01.md).

## 2026-10-09 — D041 source audit / no new foundation experiment yet

Pinned source631b1f; native Task26 batch1 two Cubes newly approved, zero runtime patches. No new scene/bridge/MoveIt/planning/physical invocation yet, no fresh foundation PASS. Existing GUI PID39508/8226 read-only inspection only; operator confirms clean new Stage prerequisite. Planned budgets preflight1/physical1, currently0/0 used. Original two-Cube September23 PASS remains historical; do not replace this turn's evidence with it. [Pre-run audit](../reports/TASK01_PREDECESSOR_FOUNDATION_AUDIT.md).

## 2026-10-09 — Existing-GUI handoff01: INSERT_READY candidate, not benchmark PASS

- Executable sourcebbe9784 unchanged, invocationHEAD005cd55; one normal existing GUI session/scene/manualPlay/bridge/externaldriver, physicalallowance1/1used. Native output `results/20261009_102650_295770_TASK01_existing_gui_handoff01/`; experiment ends capture/noTARGET/reset/A/force/P3. No new IK algorithm or recomputation of recorded PRE_PUSH restore q; existing rear planning/pool unchanged. No source/physics/model/ACM/geometry/station/threshold edits or automatic rerun.
- PREshared2829/47150002459ns, first bilateralOPEN8448; originalsafeFCL227samplesPASS; rails.650→.750; rawrefresh1/2 generation1/2 shift0/.100PASS andACK8455/8715; rearFCL354samplesPASS; first rearCLOSED8959; capture8967/149450007794ns, rails.750/.750,leftOPEN/rightCLOSED,freshgeneration2. Full14q/base/Cube/TCP/relative/helper/frame saved. Refresh2 arrivedflag initiallyfalse, finalcapturetrue; no hidden timing patch.
-6152 state/contact rows align each native step2817–8968 andstamp46950002449–149466674462ns.978 contactheaders/3859points, originalguard unexpectedpenetration0; candidate5pairs/20points expectedtable/fourcups. Tablemin−.056289mm, cupspositiveseparation2.264–3.012mm, notflushcontactcertificate. Maxdriftnominal1.479843mm; capture1.398375mmnominal/1.401641mmsavedPRE/1.398464mmrefresh2.
- Rawreadbacks include complete expected/observed5objects+CDR; composedtranslation/dimerror0, maxrotation≈1.02e-20rad, unchanged1e-8m/rad and1e-12mmessageepsilons. These do not alter physicalacceptance. CaptureD6handle0/anchorUNAVAILABLE; linearspeed.017425m/s,angular.087455rad/s, notstableheldreset. LargeJSONLslocaluntrackedhashed; selectedcontact/rawreadbacks/corelogpublished.
- Driver43175exit0, afterward move_group43171cleanupSIGSEGV−11; wrapper0notcleanshutdown. GUI39508alive/paused, originalcleanupSGOPEN; no persistedcurrentheldREADYclaim.104.874sadapterschwall is engineeringonly, notscientificstamp/efficiencyscore. Oldlaunchwarningssavedunfixed. **TASK01PARTIAL/INSERT_READYESTABLISHED_CANDIDATE; STOPFORUSER**, notPASS/FROZEN. [Fullreport](../reports/TASK01_EXISTING_GUI_BOUNDED_RUNTIME01.md).

## 2026-10-09 — Approved existing-GUI runtime01 NOT STARTED

Read-only source/process/socket preflight at executable source bbe97849e3e3cd5708861de676e7b952ec00fecb: GUI process/executor8226 not observed. No new Isaac/ROS invocation, scene/bridge load, physics step/time/state/contact/world readback or attachment capture. Not a failed experiment, native crash or safety result; new physical allowance0/1 unused. [Metadata](../results/20261009_TASK01_existing_gui_runtime01/metadata.json), [scope](../reports/TASK01_EXISTING_GUI_BOUNDED_RUNTIME01.md). TASK01 PARTIAL, no FROZEN.

## 2026-10-09 — Existing-GUI adapter: pure software checks, NO ISAAC EXPERIMENT

Source base d961a46. Lifecycle mock/AST tests and syntax/hash/source checks only; tests do not import Isaac/ROS or start an inferior/controller. Runtime attempts0, robot/suction/rail commands0, native simulation state/contact/readback/INSERT_READY records0. Historical run results are unchanged. New active loading route follows pinned Task26@631b1f, but runtime behavior is **NOT_VALIDATED**. No safety/held READY/reset/dynamics/FROZEN claim. [Software checks and immutable inputs](../reports/TASK01_EXISTING_GUI_LIFECYCLE_ADAPTER.md).

## 2026-10-09 — Startup-only diagnostic, NOT benchmark execution

- Source944422dc92e7a8f39f0e8c8066147073ba0745f0; one DISPLAY`:1` GDB invocation under180s cap, ~109.663s log-file interval (engineering only). PID17071/LWP17392/thread67`tbb.worker`, SIGSEGV/address0x40/PC0x73be3cf418d9 in OmniGraph core; image-core×2→exec-core×2→TBB native callers; malloc fastbin integrity warning. Symbols stripped, corrupting writer/root unresolved.
- Originalmain line124 observed before STOP-timeline app.update,125 barrier not reached; noPLAY/physicalcontrol/projectSGbridge/commands/MoveIt/worldrefresh/handoff/regrasp/READY/TARGET. No q/TCP/Cube/contact/nativepoststep data; no safety or stability verdict. SDK app/bridge startup markers are diagnostic profiling, not sim timestamps.
- GDB captured then killedinferior; wrapper0 is NOTIsaacPASS. PIDs17037/17038/17071 and ownedPGIDs gone. Original eight hashes unchanged; launcher software5tests/syntax/reviewsPASS do not provide scientific acceptance.
- New allowance1/1 consumed, norepair/secondcapture/retry. [Full provenance](../reports/TASK01_STARTUP_NATIVE_STACK_CAPTURE.md), [metadata](../results/20261009_TASK01_startup_native_stack01/metadata.json), [native log](../results/20261009_TASK01_startup_native_stack01/launch.log). TASK01PARTIAL/noFROZEN; await bounded next decision.

## 2026-10-08 — Existing-log startup diagnosis: NO NEW ISAAC EXPERIMENT

- Source407bd34; one read-only diagnostic iteration, no new simulator/ROS/control/debugger/test run or fix. Prior retry01/02 physical evidence remains separate and unchanged; all eight runtime hashes match.
- Full Kit positive markers: SDK startup complete10.589/81.426s, ROS bridge started10.765/83.685s, SG enable request10.810/83.915s, last World1 layers10.971/84.176s (app-relative profiling, not scientific simulation time). Console truncation cannot establish the actual last call.
- Existing kernel21:31:44+0800: `tbb.worker[12295]`, address0x40, IP00007ae437f418d9 in `libomni.graph.core.plugin.so`, correlated with retry02 PID11986 SIG11. Native parent/thread stack unavailable; root cause not inferred.
- Apport exactPID398623/11986 ignored non-package bundled Python with core limit0; no matching core. Selected excerptSHAda076852… and source hashes in [metadata](../results/20261008_TASK01_startup_readonly01/metadata.json). New native physics step/time/state/readback/READY absent. Diagnosis1/1 complete, TASK01PARTIAL; separate live stack-capture authority needed. [Report](../reports/TASK01_STARTUP_READONLY_DIAGNOSIS.md).

## 2026-10-08 — Unchanged readback retry02: no scientific-state evidence

- Run `results/20261008_TASK01_readback_retry02`, source d8d0096511c165f3afc616cf76b2331222dce407; all eight runtime/config/binary SHA match retry01. Exact command/input hashes in [metadata](../results/20261008_TASK01_readback_retry02/metadata.json).
- One DISPLAY=:1 GUI, 180s cap/reset0/noTARGET. App-ready62.619s, lastTLAS64.839s, nativeSIGSEGV/PID11986/core-dump message, wrapperexit1 beforecap. App-relative time is not native simulation time; actual physics step/time unknown.
- Only input and launchlog retained (SHAf6a33b28…/738fab8f…). Recorded state/contact rows0/0, refresh0, no driver/sceneaudit/PRE/READY. Runtime readback/rails/rear NOT_REACHED; original guards NOT_EVALUATED. No collision or geometry verdict inferred.
- New user-requested1/1 consumed, no repair/newprobe/rebuild/test/secondinvocation. Matching owned processes absent. TASK01PARTIAL/notFROZEN; actualINSERT_READY remains unavailable. [Report/escalation](../reports/TASK01_UNCHANGED_RETRY02.md).

## 2026-10-08 — Readback retry01: GUI initialization crash, no scientific state

- Run `results/20261008_TASK01_readback_retry01`; source08c34b8, binarySHA86237ffa…, config25b7162c…, unchangedGUI539615dc…; exact command/hashes in [metadata](../results/20261008_TASK01_readback_retry01/metadata.json).
- Exactly one DISPLAY=:1 visibleGUI, external180s cap, reset0/TARGETfalse. After app-relative7.514s `app ready`, `Fatal Python error: Segmentation fault`, nativepid398623/core-dump message; wrapperexit1 beforecap. App log time is not a native simulation timestamp. Root cause undetermined.
- Only complete launchlog and hash-matched inputJSON retained. Recordedpoststepstates0/contacts0, refreshJSON0, q/TCP/Cube/rail/native step/time unavailable. No driver/sceneaudit/PREsample/READY. Cannot establish actualphysicsstep0, collision free, live validator PASS/FAIL or handoffgeometryfailure from missing data.
- Safe transition/rails/rear/attachment/readback bothshifts NOT_REACHED, originalguardverdicts NOT_EVALUATED. No repeats/TARGET; processes absent. Additional1/1 consumed, no retry/code repair/probe. TASK01PARTIAL/notFROZEN; user decision required. [Report/escalation](../reports/TASK01_READBACK_NORMALIZATION_RETRY.md).

## 2026-10-08 — Readback normalization preparation (no physical experiment yet)

User-authorized independent allowance1/1 remains0/1 at this checkpoint. Unique CMake Release build/pure `--self-test` exit0; normalization, fixed epsilon boundary rejection, invalid/nonfinite and lossless raw evidence tests passed. Launch pure construction7 entities and independent scope audit passed. No ROS initialization, IK, Isaac or control command in software checks. YAML/GUI/bridge/original primitives byte-identical to f73490d; driver/source/launch hashes in [bounded plan](../reports/TASK01_READBACK_NORMALIZATION_RETRY.md). Planned sole visibleGUI attempt180s with reset-repeats0; all runtime results still NOT_RUN, TASK01 PARTIAL, no TARGET/FROZEN.

## 2026-10-08 — TASK01 fixed handoff01 (PARTIAL, initial world gate)

- Run `results/20261008_TASK01_fixed_handoff01/`; sourceee51470, configSHA25b7162c…, gui539615dc…, driver231785fa…; exactcommand/artifacthashes inmetadata. One180s-cappedvisibleGUI, consumed1/1, endedbeforecap.
-351recordednativepoststeps5–355, times.083333338→5.916666975s; fourordinarySDKwarmupsteps precedestream. BothSGCLOSED196samples(firststep6/.100000005s); firstconfirmedbothOPENstep202/3.366666842s.
- PREstep17/.283333348s: actualCube(.789996266,.000000154,.259998947)m, error3.882252µm; qmaxleft.000644268rad/right.000361433rad; railsboth.649999976m, unchanged. Full14q/TCP/base/relativetransform/frame/status savedselectedevidence. Actualmass.8000000119kg/material.5,.5,0; originalTGS/GPU/60Hz/CCD/gravity retained.
-441contactheaders onlycupCube/tableCube; minleftcup+.954676mm/right+.999734mm, expectedtableCube−.008691mm. No unexpectedrobotenvironmentreport inthisstationaryprefix—notwholehandoffsafety, airbornehold, nativeD6anchororREADYresetproof.
- Initialshift0worldreadback rejects task01_table before safepath/rails/rear. ACKgeneration0; INSERT_READYnotcaptured, reset0, TARGET/Bnotrun. Combinedguarddoesnotlogexactfield; normalizedobject/shapepose explanation issourcesupported, notactualvalueproof.
- Driverexit1; launchshutdownmove_group−11; Isaacwrapper0isnotPASS. Allownedprocessesabsent, nosecondattempt/runtimeedit. TASK01PARTIAL/DRAFT/STOPFORUSER; BUG001TASK10IS; fiveCubeoutofscope. [Report](../reports/TASK01_FIXED_HANDOFF_INTEGRATION.md).

## 2026-10-08 — D039 fixed handoff software preflight (not physical evidence)

CMake Release build+pure `task01_rear_handoff --self-test` PASS (before rclcpp init:5objects/.100projection/rear/interpolation). Eight `test_reused_bridge.py` mock tests PASS (0.020s), including originalrail math/arrival, same-stamp atomic commands and fail-closed setter. Python compilation/launch construction/diff check PASS. No ROS/IK/Isaac/control command ran. Physical integration allowance remains0/1. [Bounded run plan](../reports/TASK01_FIXED_HANDOFF_INTEGRATION.md).

## 2026-10-08 — TASK01 reuse audit: NO NEW EXPERIMENT

- Scope: predecessor Git/source/log reads only; current input c525fc1, old source pin631b1f. No simulator, ROS, IK, build, controller, suction, reset or physical steps initiated. No new experiment/acceptance result.
- Historical raw evidence: old `artifacts/task27_repeat_20260926/full_run_606_optimized.log`, SHA2562a286c3ad2a339f2525025ef13ed28ef752cf1ba515da9a41912fa5a2e593bec. L2985 BOTH rail .650→.750; L3094 right pusher; L3147 deep-wall .426 mm; L3149 after-exit .480 mm / cell error .509 mm. [Verbatim excerpt](../reports/evidence/TASK01_PRIOR_RIGHT_PUSH_EXCERPT.log); **not a new run and no verifiable historical build SHA**.
- Task24 .184/.115 mm single-Cube results remain documentation-level historical evidence; Task11–13 top-grasp results do not validate current side-tool geometry. Do not label five-Cube success or fixed-.650 current B PASS.
- Current YAML SHAda1b1de4… unchanged; A136 existing evidence retained, old bilateral B157 superseded. INSERT_READY/held reset/new rear B NOT_RUN. New integration attempts0; old budgets not reopened. [Audit/plan](../reports/TASK01_PRIOR_PROJECT_REUSE_AUDIT.md).

## 2026-10-08 — TASK01 command-only additional attempt1/1: safety FAIL

- Run: `results/20261008_TASK01_critical_safety_command_rerun/`; checkpointa10db77, unchanged source47d22ce/SHAab174884…; exact command in metadata/report. VisibleGUI, four recorded14q/Cube states, original1/60step each; no IK/code/geometry/physics/ACM change or controller/suction command.
- Actual steps1–4: .0166666675359/.0333333350718/.0500000026077/.0666666701436s. Post-step dt accumulator/native core match; no scientific wall timestamps. Carriage[.91,0,.2,0,0,0,1] unchanged.
- START/PRE/state196: no unexpected collision;17 focus queries each. PRE/state196 have expected Cube/table hits, not robotenvironment failures. Free-Cube drift2.725005/.000298/1.362503mm; not held stability. Existing7puretests passed, not simulator acceptance.
- TARGET: original `UNEXPECTED_COLLISION_STOP`, leftlink7/deepwall min−3.016427159mm at[1.160529494,-.238035619,.347037017]m. Additional unclassified rightlink7/deepwall−3.016243223mm. Nominal FCL leftlink7/deepwall+2.212219mm. Cube/deepwall−5.59e-8m boundary is not the blocking pair. Postqmax.018546728rad, TCP2.513139/4.758278mm, Cube drift.252231mm; exact14q/poses saved.
- Immediate stop: four snapshots, three continuation tokens,0reset. TARGET overlap/fourthstdin NOT_RUN; original failure.json saved, no summary. Unchanged harness inputs default5resets is inherited metadata, **not current authorization/execution**.
- Lifecycle: app.close starts at logged13.108s, resource wait ends by120s groupKILL/137; owned processes absent. No second attempt/shutdown repair. Scientific verdict derives from contact evidence, not exit137.
- Status: TASK01 PARTIAL; safety FAIL; READY/reset BLOCKED_BY_SHARED_HOLD_SEMANTICS. All input hashes/scene audit match previous run. [Report](../reports/TASK01_CRITICAL_SAFETY_COMMAND_RERUN.md); additional1/1 consumed, stop for user.

## 2026-10-08 — TASK01 bounded controlled replay (one approved attempt, PARTIAL)

- Run: `results/20261008_TASK01_bounded_controlled_replay/`; sourcecommit47d22ce, SHAab174884…; originalruntime d4b290c. Exact nativegeometry snapshot3dbe7fcb…/states607c3048…; no newIK.
- Command:120s bounded DISPLAY=:1 visibleGUI, bundledROS launcher, `task01_critical_controlled_replay_gui.py`; exact command inmetadata/report. No controller/suction/force/fiveCube.
- Software:7newpure classification testsOK/compile/diffOK, not runtimePASS.
- Actual snapshot: STARTstate0 only, one PhysXstep and nativeclock0.01666666753590107s, no wallstate timestamps. Beforeqmax9.70629e-8rad/Cubepos1.28392e-8m; postqmax9.05020e-5rad, TCP0.096015/0.067458mm, freeCubegravitydrop2.725005mm, rotation0. Frame[.91,0,.2,0,0,0,1]. Mass.8000000119kg/friction.5/.5/0. GPUsceneattributesTrue/GPU retained, NumPy notCPUproof.
- Contacts:8cup–Cube headers32points allpositive0.999954–1.000086mm, no penetration.17focusedoriginalshapequeries/37hits,0environmenthits/count/callbackerror. Exactpaths/readback saved untouched incritical_START_sample.json.
- Stop: added stdin review gate unconsumed, processT/Tl consistent backgroundTTYread; launchertimeout124/reaped. No probe summary/failure; post-runauditseparate. Observedcritical1/reviewsaccepted0; PRE/state196/TARGET NOT_RUN, START/PREreset0/0.
- Conclusion: limited START short-step safety observation only; no four-state/READY/PASSCANDIDATE/FROZEN/model-equivalence/force/suction claim. Oneapprovedfallback1/1used; no additionalexperiment. Originalnominalgeometry A136/B157 remainsPASS.

## 2026-10-08 — Correct09 actual result; governance review, no additional run

09 had already executed before governance override, source commit `a5dba59`/SHA `803b1e9e…`, visible bounded GUI. Actual `ENGINEERING_ORIGINAL_RELOAD_STATE_STOP`, accepted0/START index0/callback0; after original handles reloaded, left7q all0, max expectedq error2.43079576661854rad. Immediate stop before right freshq or collision query; no READY/reset/force. Software70OK/.148s and wrapper0 are not simulator PASS. [09 actual metadata](../results/20261008_TASK01_isaac_model_parity09/metadata.json)/[summary](../results/20261008_TASK01_isaac_model_parity09/summary.json); raw rejection preserved. Recent07/08/09 same-root attempts now exhaust default3/3; no experiment after user requested governance reading. Proposed targeted Tier2 fallback remains NOT_RUN pending approval.

## 2026-10-08 — isaac_model_parity08 query proof STOP；09 IN DESIGN

TASK01/[ENGINEERING]/visible Isaac4.5，commit3e2414b72d2d103b0012b1b8cb9dda06764bf17f/source29cfd626a4f1f78cc943baeee151807e6c3fd48252ed6dfaeae0ad9b2965699a；完整命令/inputs见 [08 metadata](../results/20261008_TASK01_isaac_model_parity08/metadata.json)。实际START accepted0/callbacks0，disabled-physics flush/on_update(time,0,false)已调用但left link2内部点query0hits，`ENGINEERING_STALE_OR_UNVERIFIED_NATIVE_QUERY_STOP`，不是collision/READY。56纯unit主代理0.100s OK。

本轮raw/failure已保存actual14q/TCP/Cube与18FK，q error左9.706287595889762e-8/右1.7115877160023274e-8rad，TCP position3.976069182062307e-7/6.256020684309647e-7m，18FK max position5.988083249179899e-7m/rotation1.082772143160413e-6rad；pre/post27 native与geometry fingerprint保持。step/time=null，仅静态索引、非poststep科学测量。09逐态原native handle重建IN DESIGN/API review、未执行，原USD/hash/14q/model/ACM保持；03–08保留，不称parityPASS，BUG019未判决/BUG001非阻塞。

## 2026-10-08 — isaac_model_parity07 零步query proof STOP；08未运行

TASK01/[ENGINEERING]/visible Isaac4.5，commit0fb2fc4/source8887ad1bd7d674ecae930b65a8c496d3c1776433b34eab826f2172dce72660cf，原输入/确定14q/config不变；命令和产物见 [07 metadata](../results/20261008_TASK01_isaac_model_parity07/metadata.json)。START accepted0、actual callbacks0/dt[]，pre27 native max差0m/6.165552397244359e-7rad，post27 max变化2.9802322387695312e-8m/4.2146848510894035e-8rad，geometry fingerprint前后相同。51纯tests主代理0.099s OK；inputs/candidate/runtime hashes独立一致。

mirror/paused后stale[]，left link0/link1 exact shape+owner hit，但left link2 cooked质心10µm球未hit，`ENGINEERING_STALE_OR_UNVERIFIED_NATIVE_QUERY_STOP`；static_replay空，不是实际collision/BUG019判决。成功actual_q/liveFK全表未存，只由控制流知晓，不补写；READY NOT_RUN。08仅准备原flush_changes/on_update(static_time,0,False)非physics刷新；source29cfd626…/新增测试待验/GUI NOT_RUN，不保证treefreshness，不减弱门禁或改原模型，03–07保留，BUG001非阻塞。

## 2026-10-08 — isaac_model_parity06 render-only仍2callbacks STOP；07未运行

TASK01/[ENGINEERING]/visible Isaac4.5，commit `0a78485` /source `923aca89345fa7850ad9f5b981c38718c742a98c12fb07c9a7e4206a7a244498`，原config/确定14q/inputs SHA一致。完整480s可见命令与证据在 [06 metadata](../results/20261008_TASK01_isaac_model_parity06/metadata.json)。GUI14.25s、START accepted0：实际callback2，各dt0.01666666753590107s，render_guard拒绝。pre-render27 native比较max0m/6.165552397244359e-7rad与mirror后stale0已存；static_replay为空，moving queries/full collision未执行，无collision verdict/READY。50纯unit tests主代理0.079s OK；wrapper0非PASS，不能称无积分。

SDK源码存在_warm_start直接update_simulation与_create_simulation_view第二调用绕过render gate，符合2events但缺唯一causal trace。07只准备原force_load/start_simulation直接初始化、不timeline PLAY/update/simulate/fetch，保留零步/q/native/几何/query所有守卫；不patch/禁用SDK callback、不改物理/model/ACM/benchmark。source8887ad…待freeze、GUI07未运行；旧03–06各自保留，BUG019 NOT_ESTABLISHED、READY NOT_RUN，BUG001非阻塞。

## 2026-10-08 — isaac_model_parity05 意外积分STOP；06未运行

TASK01/[ENGINEERING]/visible Isaac4.5，commit `8188168`，source SHA `66dce1cd96875298f3830a25bb64232d6eb75f97717deaef7134feb43368cdba`，原config/确定14q/模型不变。命令（同480s可见wrapper、output-dir改05）、完整输入和产物见 [05 metadata](../results/20261008_TASK01_isaac_model_parity05/metadata.json)。约13.8s工程wall time，START accepted0，实际 `ENGINEERING_UNINTENDED_PHYSICS_DISPATCH_STOP`：paused app.update触发physics-step callbacks2，Cube USD z从0.38到0.3772749900817871m，velocity=(0,0,-0.16350001)m/s。integration_requested=false但integration_actually_observed=true；不能宣称没有积分/纯静态。无碰撞结果，wrapper0非PASS，owned GUI已退出回收。

已保存pre_notice27 nativeactor比较，max position difference0m、max rotation difference6.165552397244359e-7rad，不能与after-notice状态混淆。raw/output_sync_rejection、前后inventory、failure、源码快照与metadata/summary保留；科研step/time仍null（没有合法静态或READY测量），READY/controller/suction/force NOT_RUN。03/04/05各自负结果不覆盖，BUG019 NOT_ESTABLISHED。

06准备官方render-style playSimulations临时False→app.update→finally原bool恢复，force_load初始化亦隔离；独立step0/callback0与time/q/native再验。只把SDK动态velocity/jointstate从几何参数hash分离，mass/scale/mesh/limits/drive/material/scene/frames保留；dt/gravity/benchmark/ACM/实际几何不改。纯mock回归准备，06未运行/source待冻结；`8188168`已direct push，BUG001非阻塞。

## 2026-10-08 — single_cube_core_benchmark / isaac_model_parity04 API precision停止；05未运行

TASK01，[ENGINEERING]静态原模型输出适配，非论文算法；Isaac4.5 visible GUI/既有全链确定14q，无新IK。Commit `a672224`，probe SHA `3bf86b380723b317b2eb4b32f3020a3736a16126887648bbc8a80c0bc3da8753`；config仍不可变native-run `config_at_run.yaml` /SHA `3dbe7fcb192d09db83be801314582249ac3c0c77c9ffd683801ca7680d54881b`。实际命令与完整证据见 [04 metadata](../results/20261008_TASK01_isaac_model_parity04/metadata.json)：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
timeout --signal=TERM --kill-after=20s 480s env DISPLAY=:1 PYTHONUNBUFFERED=1 \
  scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_single_cube_model_parity_gui.py \
  --output-dir results/20261008_TASK01_isaac_model_parity04/raw \
  --hold-for-inspection-sec 0
```

Actual约14.5s工程wall time，START/index0 accepted0，`ENGINEERING_USD_ATTRIBUTE_PRECISION_STOP`：原SDK `/World/Task01/Cube.xformOp:orient` expected GfQuatf/got GfQuatd。实际Fabric disabled、updateToUsd=true；未进入全链碰撞判定，native成功值未落盘、不反填，wrapper0不等PASS。32软件测试OK只是当轮软件证据。Artifacts=root metadata/summary/source snapshot/software_validation/launch.log；raw inputs/failure/output_sync_contract。physics integration_requested=false，step/time=null、READY/controller/suction/force NOT_RUN，owned GUI已退出回收。03负结果保留；BUG019 NOT_ESTABLISHED，不作几何FAIL/模型修复结论。

05准备状态属性precision修复与扩大不可变几何库存；原SDK物化pose orient与几何尺度分开，helper仍reject新增/reorder/非法ops，原模型/benchmark/ACM不改。增加final/screenshot step0守卫。35纯USD/query tests主代理已实际复跑exit0/0.093s，source `66dce1cd96875298f3830a25bb64232d6eb75f97717deaef7134feb43368cdba` 已冻结；**GUI05尚未运行，无05 GUI/物理实验结果**。Git `a672224` direct push成功，首次proxy timeout保留，不改全局SSH。

## 2026-10-08 — single_cube_core_benchmark / isaac_model_parity03 工程门禁停止

TASK01；baseline=[ENGINEERING]原cooked-shape静态对照，不是论文算法；platform=Isaac Sim4.5 visible GUI/CPU PhysX。Source commit `d9c422c`，probe SHA `27e0a043431a83b0f8fa760fd6307f8749ee2e825de154dcad4c3c67ae6d7aa1`，执行前源码快照一致；seed为既有全链14q（无新IK）；config=`results/20261007_TASK01_full_single_cube_geometry01/config_at_run.yaml`、SHA `3dbe7fcb192d09db83be801314582249ac3c0c77c9ffd683801ca7680d54881b`。完整来源/命令/指标在 [03 metadata](../results/20261008_TASK01_isaac_model_parity03/metadata.json)。实际命令：

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
timeout --signal=TERM --kill-after=20s 480s env DISPLAY=:1 PYTHONUNBUFFERED=1 \
  scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_single_cube_model_parity_gui.py \
  --output-dir results/20261008_TASK01_isaac_model_parity03/raw \
  --hold-for-inspection-sec 0
```

Actual status=`ENGINEERING_STALE_USD_QUERY_SOURCE_STOP`，accepted0/attempted index0；wrapper exit0不是PASS。START已存q reset max left9.706287595889762e-8/right1.7115877160023274e-8rad，TCP位置误差left3.976069182062307e-7/right6.256020684309647e-7m，角误差6.861009855998394e-7/1.0000444493033106e-6rad；Cube=(0.550000011920929,0,0.3799999952316284)、identity。native actor门禁未拒绝只由控制流知晓，实际成功比较值未落盘，不补写。CPU device ordinal=-1，readback_suppressed=false不单独证明查询freshness。

Rejected USD source=`/World/left_fr3/fr3_link1/collisions`：rotation旧identity，与live-body预期矩阵max error0.609714114482171（无量纲），不是collision depth。尚未进入移动shape查询/全链collision验收；geometry_failure_established=false、BUG019 NOT_ESTABLISHED。Artifacts=root metadata/summary/源码快照/软件测试log，以及raw inputs/query_frame_rejection/query_api_contract/original_shape_audit/cooked_shapes/failure；原负结果不覆盖。进程已退出回收。独立软件19 tests OK，仅软件证据；physics integration_requested=false、physics step与simulation timestamp=null（静态索引，不伪造poststep科研时标），controller/suction/force=未运行，READY/reset NOT_RUN。

04目前只准备D035静态输出适配，**尚未运行、无实验结果**。A136/B157几何证据仍有效；TASK01 IN_PROGRESS/PARTIAL，TASK02/P4未开始，BUG001延期TASK10-IS不阻塞。

## 2026-10-07 — single_cube_core_benchmark / full_single_cube_geometry01

Task TASK01；[ENGINEERING]/[EXPERIMENTAL]离散完整几何，不是P4算法。Platform native Humble/MoveIt2 2.5.9/LMA/FCL；source fb643f1、approval cc04cec、model d4b290c；binary7da613a4…；原run config SHA3dbe7fcb…881b（config_at_run.yaml，后录q候选不改变旧证据）。命令/完整SHA见metadata.json与FULL_SINGLE_CUBE_GEOMETRY报告。显式START有限64seed/arm retain12，首fullFCL有效pair；之后每臂一次previous-q延续，不重新选分支。

Actual exit0/PASS_DISCRETE_FULL_CHAIN_ONLY：A136/B157/293records292unique；A step1.987616mm B1.987179mm；PRE pose/14q exactequal。joint margin min A0.4618280014/B0.4678486267rad，max grasptranslation1.538421e-9/8.685638e-9m，rotation5.063085e-6/9.944048e-6rad。self/inter/world collision0，Cube四环境1172checks/positive-volume0。min全FCL state196 Cube↔lefttool0.999669mm；min腕工具环境state292/TARGET leftlink7↔deepwall2.212219mm。每态distance/pair/nearestpoints记录：state_records.json、1758row CSV、full/summary/startcandidate；原stdout与build保留，未抹前轮数值负记录。

Isaac/robot/ROS/suction命令0、physicssteps0；不能称时间轨迹/连续证书/动力学或吸附PASS。START/PRE配置只candidate。纯几何后新visibleGUI staticparity初始化，另run结果待定；reset未运行，BUG001不阻塞本task。TASK01 IN_PROGRESS，TASK02 TODO。

## 2026-10-07 — single_cube_core_benchmark / IK diagnosis + same-seed precision A/B

Task: TASK01；Baseline: [ENGINEERING]/[EXPERIMENTAL]有限数值诊断，不是论文算法。Platform: native Humble/MoveIt2 2.5.9/LMA/FCL，无Isaac。Source: instrumentation12a6d74/binary415f23ef；A/B与dense8a5bbaf/binary01d64241；AABB2856fa5。Config:原schema2候选ff490a56…及runtime d4b290c模型hash不变。Seed:原显式端点策略；A/B精确原probe02 PRE_PUSH14q、每臂一次；dense上一q延续。

Results: diagnostic01为编译结束前旧binary误跑，INVALID_DIAGNOSTIC_OLD_BINARY/exit1，缺诊断字段和实际exe SHA，不当作新代码验证。正确diagnostic02/原精度对照exit1均定位ROTATION_RESIDUAL_REJECTED：两臂SUCCESS、bounds true、角残差2.582469e-4/9.985173e-4rad。仅本地epsilon1e-7（权重/验收不变）同seed角残差1.841597e-6/2.037263e-6rad、IK/FCL PASS，exit3/PASS_RECORDED_STEP_ONLY。

Dense: 六端点PASS；157状态、步长1.987179mm、FCL pairs0、joint margin最小25.755478deg、相邻单关节增量最大0.415676deg、TCP translation最大6.591492e-9m/rotation9.942151e-6rad。无时间化/连续扫掠保证。AABB audit:628对、体积穿透0、table边界touch157/deep目标touch1、4基本测试PASS/exit0。

Artifacts: results/20261007_TASK01_single_cube_{ik_diagnostic01,ik_diagnostic02,precision_default,precision_tight,precision_dense}/各metadata.json、JSON/CSV、probe_evidence.log；完整命令见reports/TASK01_SINGLE_CUBE_IK_DIAGNOSIS.md及逐run metadata。Native dense exit3/PARTIAL_UNDEFINED_START，不是TASK01 PASS。机器人/吸盘命令0、新物理启动0、ACM/工具/车厢/TCP/基座修改0；BUG019模型差异仍OPEN，START和READY/reset待验。

## 2026-10-06 — single_cube_core_benchmark / geometry_probe01,02

- Platform: native ROS2 Humble/MoveIt2 2.5.9/LMA/FCL，零Isaac启动/零关节和吸盘命令。Source b31ff05/c9d71f4，runtime模型d4b290c；候选hash ff490a56…，几何/ACM不改。
- probe01: 六规定插入端点通过，START未定义，exit3/PARTIAL；不是完整链PASS。
- probe02: 六端点通过；上一q seed连续检查第二状态（CubeX0.791987179，0.641026%）无合格双IK，exit1/FAIL_STOP。不记录为物理碰撞/全局无解；具体臂/插件错误需另行批准诊断。
- 端点最小关节余量3.189440°；最近腕/工具墙FCL距离为right_link7↔deep wall2.205603mm；最大抓取位置残差0.000585mm。原Isaac mesh不等价，不能据此认证物理净空。
- Artifact roots: results/20261006_TASK01_single_cube_geometry_probe01、probe02；metadata.yaml/sample_results.json/dense_insertion_results.json/三个CSV/精选原日志；详情和完整命令见reports/TASK01_SINGLE_CUBE_GEOMETRY.md。
- Stop rule: 首败立即停止，未进入Isaac READY/reset、force/P4或其它后续任务。

## 2026-10-06 — legacy_task27_five_cube / 仅结束上一请求遗留GUI

旧gui_contact_timing_cube01在本轮请求前已controller1，DUAL_SIDE_APPROACH rearCLOSED/sideOPEN、left86.949/right27.352Nm触发80Nm保护，无后续X/Y执行。本轮仅pause并正常关闭自有GUI0，补旧metadata，不开展新旧应用测试。raw summary2650 snapshots/errors[]保留；不算新单Cube科研试验。

## 2026-10-06 — gui_physclock_cube01 final FAIL；CONTACT IPTP准备

6fa161e/75f798a1、fresh可见/zero-preplaced/first1,max1/scale1。CONTACT310样本、左tracking5.429181deg、leftJ2 raw86.670166Nm、Cube左工具接触217.403930N；原80Nm互锁/双OPEN/controller1/完成0，无X/Y。GUIpause/SIGINT0，1904held/11098atomic/1849sparse完整性0错，279.117870s。早20s外部只读原子1199样本/PhysX-wall1.000084/receipt max41.339ms，不覆盖contact窗口或作单因证明。下一仅Task01侧下降同q/IPTP按现有缩放构建中，物理PASS待结果。

## 2026-10-06 — gui_physclock_cube01 RUNNING

runtime6fa161e/binary75f798a1、GUIadapter433e836，production build02 58.5s/exit0、63Python/两政策C++ PASS。0preplaced/first1/max1/scale1/rear45/side-15/PhysX秒回放，fresh可见GUI截图确认/first feed真实READY后开始actual运动。沿用自有新MoveIt，无新后台沙箱/全局参数或world豁免。命令完整写metadata；只读20s原子receipt对物理stamp采样，尚未从软件/启动预记物理PASS。

## 2026-10-06 — gui_normal_cube01_run02 FAIL_CONTACT / PhysX秒修复准备

生产6bc24ec/08f3060a，headlessFalse/zero-preplaced/first1/max1/scale1现实墙钟。CONTACT207样本、左跟踪10.108530deg、Cube-left link8峰468.823105N、leftJ2 raw86.323242Nm；原80Nm拒绝、双OPEN/controller1/完成0，无X/Y及后续Cube。GUIpause再SIGINT0，6158held/26516atomic/4419sparse0完整性错、573.024725s。构型随机性/GUI物理实时比未控制，不能断言单因。原动态Cube被工具接触后移动，最终不是成功落位。

仅Task01计时以已有原子物理stamp推进的新软件测试通过；首build22.3s/error2变量重名，日志原样保留，修正后build02待结果。修改路径几何/drive/物理/门限0次，未重启headless，fresh正常GUI复测待启动。

## 2026-10-06 — 可见GUI负启动与正常倍率首件RUNNING

gui_normal_cube01：官方Isaac GUI可见但Viewport空网格，原物理/Prim/first feed有效；控制器命令0，渲染连接排查后Kit139，不是速度/协议物理结果。gui_normal_cube01_run02：可见SimulationApp入口截图显示完整原fixture，runtime6bc24ec/binary08f3060a，first1/max1/scale1/zero-preplaced/roll-15/rear45，原atomic反馈和full-rate只读held/release启用、ROS_LOCALHOST_ONLY0。正常GUI实测已启动，结果未出，不预填成功。新GUI设置两测试加原61=63PASS，benchmark36nulls/原hash不变，完整命令和负结果在metadata/报告。

## 2026-10-06 — empty_handoff_full01 final FAIL；新倍率没有物理结果

runtimef237cff/binary812c71ee、原零预置first1/max5/scale5/hold0配置；第一X1–15双CLOSED完成，X16互锁反馈STALE_OR_INVALID（left20.627/right30.965Nm<80），安全双OPEN、controller1/completed[]，后续Cube未命令。Isaac受控SIGINT后exit0。17stamp匹配舍入差<=0.000491945mm/deg，5862held/21398atomic/3566sparse无记录完整性错；release0、wall474.505s。记录完整性通过不等于ROS及时交付通过。空载helper未物理触发，根因待诊断。

随后用户要求normal倍率/GUI-only；独立Task01默认1.0、MoveIt规划限速仍12%。只编译和61离线测试，不启动headless或新GUI物理动作；尚无1.0倍率的运行误差/速度/成功率。旧scale5证据不可用于该新配置验收，benchmark36nulls/hash不变。

## 2026-10-06 — exact empty handoff replay PASS，物理回归RUNNING

results/20261006_TASK01_empty_handoff_replay：旧action/probe1；局部OMPL/IPTP probe02与最终f237cff probe03均0。最终a33c7565、full02最后step51290/stamp854833377916精确14q/三pose，same-start11+left491+right469完整FCL，CLOSED/obstruction安全拒绝、world前后完全一致；6条同raw路径三种计时全部安全，不证明单一TOTG因果。原参数/scene/ACM不改；软件61Python/2C++、analytic36nulls PASS。fresh results/20261006_TASK01_empty_handoff_full01本机headless0preplaced/first1/max5/scale5/hold0/side-15/rear45，production812c71ee、READY与hash守卫后开始实际回归；物理结果尚未产生。

## 2026-10-06 — coupled_rear_full02 final FAIL

runtimea3fceab/binary57e72f83，参数/命令见run metadata。前三真实CONTACT/X16/Y16/ROLE_SWAP/OPEN完成，GT center0.302/0.407/1.343mm、deep0.156/0.091/0.087mm、侧/邻缝0.259/0.397/0.160mm。第三清障6.3mm RRT无合法样本；26.9mm得到左右各3候选却只取最短，后验FCL拒绝left suction↔Cube03（t0.610/depth0.329mm），未执行该路径。completed[1,2]、controller1、headless0、后两无命令。105stamp舍入差≤0.000499181mm/deg；36469held/51175atomic/8529sparse完整性0错，release501。CONTACT/X/Y peak raw46.019/48.571/37.297Nm、该窗口机器人-墙非零pair0；COMPLETE跨转场，不能称全程零接触。BUG021旧HIGH本轮跨过，不宣称所有构型修复。原参数/36nulls不变。

## 2026-10-06 — coupled_rear_full02物理2/5运行checkpoint

controller仍运行/batch[1,2]PASS，前三新协议前两X/Y各16段均CLOSED且swap在release前。第一后抓candidate5/24通过新gate、第二candidate1；第二rearXYZ norm2.026/1.031/0.036mm。最新release+短清障GT中心误差0.302/0.407mm、deep0.156/0.091、side0.259/0.397，无批间HOME、原路长退出。第三初始抓取已开始，但尚未到关键side HIGH；不写五件PASS或稳定性。最终采样审计待flush，原seed/model/physics/gates不变。

## 2026-10-06 — coupled_rear_full02 RUNNING

runtime a3fceab/source final、serial force binary57e72f83，fresh Isaac4.5本机headless/0preplaced/first1/max5/scale5/hold0/side-15/rear45；沿用自有原参数MoveIt launch，仅fresh物理stage。启动等待READY≤90s并exactSHA守卫，controller实际模型/IK/首件RRT+FCL完成进入运动。尚无全件完成结果；commands/metadata独立full02，full01startup失败不覆盖。seed null/原模型物理门限保持。

## 2026-10-06 — coupled_rear_full01 FAIL_STARTUP_NO_COMMANDS

controller SHA174d6ef7 exit1因旧filter拒绝当前LMA root-arm参数；命令0/完成0，非物理推压失败。Isaac ready但在3600s空闲采样时限正常退出0，35998sparse/215989atomic0errors，仅自动第一件供料，未执行机器人。六参数RPC类型值有效；生产strings无root arm前缀，成功probe有，因此之前source/binary等价声明作废。串行强制 -B重建后再fresh full02，原日志保留、不覆盖。

## 2026-10-06 — coupled_rear只读链PASS，fresh full01启动

coupled_rear_goal_search首次exit1无命令/参数名布局错误，修正后02 exit0：记录rear60IK/0free拒绝，替代attempt4/5/6完成200mm连续下降/约330mm X/1mm Y/30mm退出完整FCL与相对TCP。某些endpoint-free候选连续链仍失败，负日志原样保存；HIGH的RRT连接不属于这个纯本地PASS。61Python与两C++成功重跑，C++首harness路径错误保留；controller52.2s构建、probe53.0s+修正build。当前实际插件LMA（KDL底层），不是更改IK算法。a3fceab /174d6ef7生产binary，fresh coupled_rear_full01零预置五件headless启动；metadata记录原参数/seed null，实际完成数待定。

## 2026-10-06 — full01第三件goal与rear替代构型诊断

side_goal_probe exit1：原fixed-rear下60IK/0free，主pair left_fr3_side_suction↔right_fr3_link5。rear_goal_search exit0：同rear TCP，rear_solved7，3对HIGH/CONTACT/park终点全FCL自由（attempt2/5/6）。两个无命令实验共用准确held快照46343/stamp772383373616、原远程world，仅本地替换当前Cube；未控制KDL内部RNG，不是全球不可行/受控A/B/路径/物理PASS。探针 ebddf6d、SHAa4462325、build52.7s；完整精确命令/输入见full01 metadata、raw日志。联合链版编译进行中，不预填通过。

## 2026-10-06 — rear_open_xyz_full01 FAIL_CUBE03_SIDE_HIGH

runtime39f1a0c/repro566ff09/binaryefb1d133，zero-preplaced first1/max5/scale5/hold0。实际completed[1,2]、各X16/Y16，最终center0.269/0.470mm，deep0.099/0.019mm，side0.250/0.470mm；短清障RRT转场/无批间HOME。rear XYZ最终0.047/0.006/0.002mm。第三侧臂高位8×约20s目标采样失败/Invalid goal state，controller1/安全双OPEN，第四第五未命令；非几何/80Nm触发。70原子stamp精确匹配/roundingmax0.000496，37804held/8899sparse/53398atomic0错误，release163（不称全部释放窗口覆盖）；headless0/wall1481.936s。持件窗口robot-wall非零pair0，不是模型一致性或五件稳定性证明。只读goal诊断新探针初build52.7s有声明/format warnings，修正后重新build中。

## 2026-10-06 — rear_open_xyz_cube01 PASS_FIRST_CUBE_ONLY

runtime39f1a0c/repro7b61780/binaryefb1d133…，普通zero-preplaced first1/max1/scale5/hold0。rear residual2.196→1.201→0.205mm，两次命令增量≤1mm、实际FK微轨迹span3.178/3.200mm（仍原4mm scope）；X16/Y16/controller0/batch[1]/双OPEN/HOME，最终center0.303/deep0.212/side0.216mm。35精确stamp geometry/rounding≤0.0004966，8470held/26166atomic/4361sparse0错误，4524release；持件窗口robot-wall非零pair0，raw revolute CONTACT最大46.669Nm。560.393s采样、headless0、MoveIt清理-11/joint bridge1。首件单次PASS不是多件稳定/GUI/benchmark冻结，full-five同binary准备。

## 2026-10-06 — rear_roll_cube01 FAIL_X1 / OPEN rear XYZ software PASS

runtime4ebe279/reproe4004ab/binarye50b23fe…，fresh零预置first1/max1/scale5/hold0、rear45/side-15。X1 alignment2.577694mm>原2.5mm；3条原子stamp准确匹配、日志舍入差max0.000488mm/deg。controller1/completed[]/双OPEN/headless0，35922atomic/4552held/5987sparse均0完整性错；没到墙/Y，非碰墙修复PASS。

新runtime39f1a0c/binaryefb1d133…后杯OPEN XYZ最多3次/向量1mm/目标0.3mm，不变原加载验收。colcon目标首次linkPose参数类型错误exit2/20.8s，修正后50.4s PASS；61Python、实际header的preclose与dual_fixture两组C++ PASS，analytic36nulls/DRAFT。fresh首件物理试验准备；不是论文算法或可靠性证明。

## 2026-10-06 — rear_roll_nominal01 PASS_NO_COMMAND

runtime39d72c6/probe902c1fb1…/build51.2s，side-15、rear镜像45，probe0/3链通过。第一次原世界坐标LP status4，等价重心坐标default仍status4；两份失败JSON保留。同约束HiGHS-IPM审计1330节点×三墙0交集，61PythonPASS。无机器人/吸盘/供料/轨道/remoteScene命令，未物理执行，非全机器人PhysX或连续tracking保证。

## 2026-10-06 — atomic_feedback_cube01 FAIL_Y15_FRESH

完整命令/源码hash在run metadata。controller1/完成0，X16/Y14完成，Y15原80Nm left86.999/right70.170、feedback FRESH；实际right link7↔+Y墙745.807766N/step19613。双OPEN/headless0。25171feedback/0错、9491held/4195sparse/0完整性错误；33打印几何与精确物理stamp匹配到舍入误差。

同callbackUSD源X9–11可产生-1.622/-1.631/-1.755mm假负rear gap，最大rear差3.055mm；未重建旧ROS异步接收。旧nominal02三墙凸包：1330节点deep0/minusY0/plusY7交集，LP值非深度；只读后腕45deg候选待检查。60Python/C++PASS，场景/物理/门限/YAML不变。

## 2026-10-06 — cup_roll_cube01 FAIL_X3 / atomic feedback准备

run metadata保存runtime dd63c74、repro eb3b7f9、binary f74cc897…、first1/max1/scale5/hold0/zero-preplaced/roll-15、seed null和完整命令。controller1/完成0，X3旧rear=-1.784mm/末同一步+1.065277mm；双OPEN，headless0，held4738/sparse4085/0错误。未到深墙/Y，不能用名义1330节点检查当物理PASS。

新原子测量软件56Python/C++PASS；原模型/桥/scene/hash/YAML不变。新的受控源对照首件待实际结果，不预填通过。

## 2026-10-06 latest — held diagnostic02 FAIL / nominal wrist02 PASS_NO_COMMAND

- 本机Isaac4.5 headless / 原source d35cc0c+b749abc / first1,max1,scale5,hold0,zero-preplaced / RNG未受控；diagnostic02 controller1、X16/Y14、Y15原80Nm止动 left86.958/right52.123；bothOPEN/后四件未发指令，headless SIGINT后0。held10538/稀疏4598均0完整性错误。源commit、binaryhash、完整命令见run metadata。
- 真正机器人-墙pair `/World/left_fr3/fr3_link7`↔`WallDeep`，X16峰309.657685N；Y15 step21051 same-row raw leftJ2=86.997253Nm/contact140.242401N。20Hz ROS guard与poststep峰值不同，不强行对齐。四肢/DOF同一步，不是D6 wrench。
- 19627/19753/21051精确14关节只读服务重放，模型FK+已知rail0.1m与物理最大差0.000872mm；实测X16/Y15 `/check_state_validity` valid且无wall pair。object.pose与primitive local pose单列，防规范化局部0位置误读。
- Fresh official USD SHA3feceb47…与cache一致；NVIDIA mesh convexHull、URDF STL差异存在；原USD凸包在记录实测姿态与深墙LP交集有正共同球半径，STL凸包比较则不相交。LP值不是碰撞深度/最小距离，未逆向PhysX cooked hull/contact offset。
- nominal01/0cfdbaf probe0/3链名义通过，但stdout/rosout穿插，hull分析1拒绝，保存负结果。nominal02/c13ea40独立数据，probe0/3链通过、1330腕部节点、0深墙凸包重叠/minXplane6.766308mm。只读无joint/suction/feed/rail与Scene/ACM写；不是物理/全五件PASS。
- 53Python/build目标PASS，analytic PASS only/36nulls。新转角仅探针，未改执行器。原source/scene/bridge/YAML hash保持。

## 2026-10-06 follow-up — 网络恢复，原场景第二次启动

原S3直连/代理HEAD恢复HTTP200，runtime d35cc0c正常push成功；保留startup01失败。相同官方资产/原参数的startup02重新运行，held live handles与首件物理诊断仍待验证，尚未发controller命令。BUG017根因未解决，BUG018外部连接暂时恢复不抹掉负结果；模型/物理/门限/YAML不变。本段更新此前“final”失败checkpoint，不叫新物理PASS。

## 2026-10-06 final — held_fixture_diagnostic01 FAIL_STARTUP

Task TASK01；local Isaac4.5 headless/ROS2 Humble/MoveIt；runtime d35cc0c769fe51832dd0717ba0fcf71b873e2cef/binary d6b53269…，seed null。原first1/max1/scale5/hold0/0preplaced配置，controller未启动。44Python/build103s PASS、analytic36nulls；headless原FR3_asset_url失败，failure.json存在但app exit0，严格判FAIL_STARTUP，held_samples0/live handle未验证。MoveIt启动planning ready，关闭-11/bridge1，非运动失败。结果metadata与startup_evidence.log保存，完整raw本地ignored。网络curl35（SSL EOF）/SSH255（banner timeout）/SDK ERROR_CONNECTION；未使用未经溯源缓存。

## 2026-10-06 — held_fixture_diagnostic01准备

Task TASK01；[EXPERIMENTAL]首件新协议诊断；local Isaac4.5 headless/ROS2 Humble/MoveIt。first1/max1/scale5/hold0/zero preplaced；新代码待commit SHA记录；39Python/build PASS。原场景和门限不变，原Y15FAIL保留；startup检查中，未发控制命令。结果路径results/20261006_TASK01_held_fixture_diagnostic01/，metadata待真实过程补齐。

## 2026-10-05 final — dual_fixture_cube01_measured FAIL / released diagnostic PASS

- Task: TASK01; baseline: [EXPERIMENTAL] user-approved3+2 protocol; platform: local user-machine Isaac4.5 headless/PhysX/ROS2 Humble/MoveIt.
- Executed commit e0477ab3a8ba2b23bf99297e8af99227d727ede0, binary d1658940c72be17d4cb903bd0fdd3357ce5f82b7514d22d5e55207baaff82cff; seed null/uncontrolled. Config benchmark_v1.yaml/hash a49d60a4… unchanged; first1/max1/scale5/hold0/zero preplaced. Commands: measured run metadata.json.
- FAIL/controller1/completed=[]: X16/16 and Y14/16 dualCLOSED; measured-start FCL/replanning succeeds; Y15 guard left86.975/right32.984Nm>80Nm. Later cubes not commanded; bothOPEN on abort. X deep seat0.445mm; Y last completed deep seat0.191mm/alignment1.448mm/tilt0.220deg.
- Released static-state diagnostic exit0/FCL PASS (all remaining walls/table/other objects retained). Later released state is not event-time collision proof. Last sparse dualCLOSED pose (1.099520,0.225646,0.260454)m, 17.354mm short of nominal Y endpoint. No calibrated contact-wrench/root-cause claim.
- Artifacts: results/20261005_TASK01_dual_fixture_cube01_measured/{metadata.json,analysis.json,protocol.json,controller_evidence.log,released_state_evidence.log}; ignored raw logs/poses/audit/summary. 9432 snapshots/0 integrity errors; release_contact_samples.jsonl empty because release phases not reached.
- Build66s/Python35 PASS; analytic geometry PASS only/36nulls. All owned processes stopped, headless exit0; MoveIt teardown-11/bridge1 independently of controller1. No source edits during physical run. Old5/5/new nominal3-chain PASS do not establish new physical5/5.

## 2026-10-05 follow-up — dual_fixture_cube01 FAIL / measured replay running

- Actual runtimeff20ac3/bd1de5b7…, first1/max1/scale5/hold0/0preplaced: controller1, completed=[], bothOPEN on abort. X16/16 dualCLOSED, deep0.286mm/alignment2.171mm/tilt0.265deg; Y0 completed slices. Raw guard lacked torque/state reason; no exact cause claim. 4747 sparse PhysX samples, integrity0; later4 cubes parked. Metadata/analysis/protocol/controller_evidence all under run directory.
- e0477ab/d1658940…: measured role-swap seed/current FCL/explicit interlock diagnostics only; 54.3s buildPASS, Python35PASS, prior4 C++ policiesPASS. Fresh original scene measured Cube01 replay started, same config; result pending, no source edits mid-run. MoveIt retained, original physical stage restarted. Detailed commands/artifact paths in measured run metadata.

## 2026-10-05 TASK01 dual_fixture_preflight / cube01

- Platform: local user machine Isaac 4.5 headless + ROS2 Humble MoveIt; not GUI acceptance.
- Runtime final source: ff20ac3 / probe binarybe34b81c… / executablebd1de5b7…; reproduction basebb301b2 + new records/tests. Seed:null, explicit nominal joint seeds in source, internal IK/OMPL randomness uncontrolled.
- Commands/config/status/artifacts: `results/20261005_TASK01_dual_fixture_preflight/metadata.json` and `results/20261005_TASK01_dual_fixture_cube01/metadata.json`. 原场景/工具/参数/ACM/门限未改；YAML SHA256 a49d60a4…，36nulls。
- Offline: 34 Python /4 C++ policy / build PASS. Analytic candidate PASS only.
- No-command nominal full-robot probe04 exit0: 3/3 contact/X/Y/30mm released exit FCL chains PASS, relative TCP max axis about0.002mm; no Arm publishers, remote scene/ACM mutation or physical commands. Probe01–03 failures preserved (IK config; independent time-scale relative drift / rejected Cartesian branch; narrow joint seed coverage).
- Fresh normal-feed first1/max1/scale5/hold0 physical controller started; actual result pending. It is not full-five, force-control or paper-method evidence.

## 2026-10-04 final — empty_rrt_full_01 普通实际执行 5/5 PASS

- 平台：用户本机 Isaac 4.5 headless + PhysX + ROS2 Humble + MoveIt2；不是 GUI 验收。源码 `df9c2c0` / binary `c760d506…`，无中途重编译或场景/门限调整。
- 配置：preplaced_count=0，first_batch=1，max_batches=5，center_pusher_arm=right，execution_time_scale=5.0，release_diagnostic_hold_sec=0（默认）。已知离线位姿；OMPL 随机数未受控。
- 结果：实际 completed=[1,2,3,4,5]，controller=0，最终双臂 HOME、双吸盘 OPEN。中心误差 [1.983,0.807,0.723,1.319,0.481] mm，深墙 gap [1.521,0.800,0.235,0.641,0.406] mm。第四 neighbor gap=0.347 mm；第五两侧 gap=1.987/1.473 mm。
- Cube02 preclose gap asymmetry 1.283→0.850→0.219 mm，3 checks / 2 corrections；规划总计 0.069299 s，执行 7.418296 s。其他四件不做多余纠偏。原门限不变。
- 记录：18,498 个稀疏 PhysX snapshots / 0 integrity errors，3,212 个 release snapshots；controller 首日志至最终 batch PASS=1,726.184527 s，sampler wall=1,940.471278 s（含准备/空闲）。慢速 scale=5，非效率基准。
- 退出：headless=0；MoveIt 子进程关闭 -11 / joint bridge 1 单列，不能由 launcher 0 宣称全部干净关闭。自有进程已停。
- 证据：`results/20261004_TASK01_empty_rrt_full_01/{metadata.json,analysis.json,release_windows.json,controller_excerpt.txt}`；raw 在该目录本地保存并忽略。完整命令见 metadata 和报告。
- 边界：RRT 备用未物理触发；一轮成功不解决历史释放漂移/可靠性/已有对象恢复比较，也不证明论文接触/力控或冻结基准。TASK01 IN_PROGRESS / 36 nulls。

## 2026-10-04 — empty_rrt_replay_01 FAIL / replay_02 PASS; full_01 running

Replay01exit1/newguardrejections/exactrestorefalse; norobotcommand. Replay02freshMoveItactualrequestconstraints/railshift.1: exit0, fullFCL1277samples, CLOSEDandobstructionnegativePASS, originalnamedIDs0→temporary6→restored0; notexisting-IDrestorationproof. Builds56.2s/55.8s separatelyrecorded. Runtimefinaldf9c2c0/binaryc760d506.../Python28/C++PASS. Full_01 localIsaacheadlessnormalfirst1/max5/scale5/hold0/3000sdeadline starts; samplerREADY/controllerplanning, actualcompletionpending. Preserveallraw/metadata/commandsandnegativeprecedingrun.

## 2026-10-04 — measured_side_full_01 final physical FAIL

Runtime2fbfa0b/binary6a64fb90..., hold0/preplaced0/first1/max5/scale5. Cube01batchPASS; Cube02COMMON_DROPGT(.768,-.060,.262), bothOPEN; fourCartesianstepsfraction1butFK752–967mm, boundedIK118/151failure, exit1/safeabort. NoCube02side/release-windowtestandnolaterCubecommand. 17319sparsePhysXposes0integrityerrors; headlessSIGTERMaftercontrollerabortwritesummary, noGUIused. Finalmetadata/analysis/release_windows inresults/20261004_TASK01_measured_side_full_01. CurrentnewRRTunbuilt/notusedinthisrun. 28offlinePythontestsPASSnextiteration.

## 2026-10-04 — Diagnostic02 final FAIL and new ordinary regression preparing

Diagnostic02 raw/analysis/release_windows retained: exit1/completed[1], firstcell0.946/deep0.497/side0.805mm; seconddeep1.804mm, laterpre-releaseSIDEPREFLIGHTcommandseedFCL0.783mm abort. No secondrelease trace, no causalclaim on originalBUG016. 13227poses0integrityerrors,1617windowcontacts; headlessexit0,teardownmovegroup-11/jointbridge1. Addedmeasuredsideactualstart runtime2fbfa0b/binary6a64fb90...,policyCPP/Python28/buildPASS. Normalfirst1/max5/scale5/hold0/preplaced0 runmeasured_side_full_01next; not a PASS untilactualcompletion.

## 2026-10-04 — Diagnostic02 in-progress checkpoint

TASK01 EXPERIMENTAL normalfeedfirst1/max5/scale5/releasehold3s, runtimeb259366/binaryc0939f21..., sourcecapture6f8dd67. Original scene/physics/gates preserved. FirstcubeSIDE_PRESS/release/shortclearance observed: stationaryOPEN holdXdelta0.028mm, shortclearanceXdelta0.000mm. This is not evidence for secondcube norordinary timing. Stopafterbatch2 planned beforeCube03 commands. Startup01negativeBRANCH_SIGN failure archive, no controller then; build56.5s andPython28testsPASS. No active motion repair yet; tools/contacts samephysstep, phasearrivalasync, collisionforceexcludesD6wrench.

## 2026-10-04 — Release diagnostic software checks

TASK01 ENGINEERING, 25PythonunittestsPASS including activephasewindow selection/identity+rotatedtoolTCP transform/invalidquaternion rejection. Diagnostic runtime addsnoordinarymotionchanges, optionalholdEXPERIMENTALdefault0. Preparingnormalfeedfirst1/max5/scale5/hold3, releasewindowfull-rate same-step contact/tools only; actualresultpending, notphysicalPASS.

## 2026-10-04 final — Actual bounded XYZ PASS, full five FAIL at later release

TASK01 ENGINEERING/EXPERIMENTAL, Isaac4.5/Humble/MoveIt2, runtimef0812a4/binaryfc5e7f8a...; reproductionb0dbd86(test)/8adf617(launch record), OMPL RNG uncontrolled. Metadata commands/config/hashes in `results/20261004_TASK01_preclose_xyz_full_01`. Normalfeed0preplaced; exit1/completed[1],714.408s controller/815.721s sampler. Cube01cell1.576/deep0.871/side1.313mm. Cube02 actualXYZ correction X2.012→1.361→0.606,Z1.589→1.009→0.451,gapdelta0.879→0.607→0.275mm; original gatesPASS, maxvector1mm, two correctionsplan0.078621s/execute7.569621s. Pre-side-pressdeep0.488mm but final5.138mm>3mm; sim689.933firstbothOPEN x1.099789, sim691.133x1.094862, finalyaw0.000120deg. 7680samples0errors; Cube03–05unexecuted; allownedprocessesstopped, teardown-11retained. StaticFK/Isaac maxnorm0.056mm is not dynamic synchronized calibration. C++/22Python/build/realXYZ+FCLno-commandPASS in unitrun; firstPython parserfailure retained. No scene/model/physics/ACM/threshold/loaded-control/freezechange; not stable/full-five benchmark proof.

## 2026-10-04 — XYZ header mathematical checks

Task TASK01, baseline ENGINEERING pre-close XYZ, standalone C++17. Command: `c++ -std=c++17 -Wall -Wextra -Werror -I <legacy>/ros_ws/src/fr3_dual_palletize/include platforms/isaac_ros2/probes/test_preclose_alignment.cpp -o /tmp/task01_preclose_xyz_test`; execution PASS. Checks: old Y semantics, combined vector direction/1mm norm bound, tiny and zero residual, NaN/Inf rejection, mathematical previous-static-failure replay. No robot commands or physical-tracking proof. Build/real-model/full-flow trials pending; report TASK01_PRECLOSE_XYZ.

## 2026-10-03 — Current variant full-five actual FAIL_SAFE_STOP

TaskTASK01, baselineEXPERIMENTAL normal-feed D014/D015 variant, Isaac4.5/ROS2/MoveIt2; repro511349c atlaunch/legacy3ee42d2/binary77b4f499..., OMPLuncontrolled. Commands/config/artifacts: `results/20261003_TASK01_precision_full_five_01/metadata.json`, reportTASK01_PRECISION_FULL_FIVE_REGRESSION. Actualexit1/completed[1], no preplacement. Cube01center1.605/deep1.006/side1.251mm; Cube02precloseX3.027→3.145→3.150mm against2.500mm gate, gapdelta2.230→0.427→0.001mm against0.300mm gate. No suction/laterCube execution. 7214sparse samples0errors, sampler761.389s/controller472.036s, rawpushtorque35.53Nm(notTCP). Allownedruntimesstopped; MoveItteardown-11/jointbridgeExternalShutdown exit1 independent. Offline21/21PASS; no YAML/hash/runtime/model/physics/gate change. Prior partialsuccess does not erase newfailure; no frozenbenchmark/paper/reliability claim.

## 2026-10-03 — Current variant normal full-five run preparing

Task TASK01, baseline EXPERIMENTAL normal-feed approved precision variant, Isaac4.5/ROS2/MoveIt2; uncontrolled OMPL, no preplacement. Planned run `results/20261003_TASK01_precision_full_five_01/`, first_batch1/max_batches5/time_scale5, same binary77b4f499... and original physics/gates. No physical result yet; exact commands/pins/artifacts in metadata and report TASK01_PRECISION_FULL_FIVE_REGRESSION. Test-only code changes; no statistical reliability or frozen benchmark claim.

## 2026-10-03 — Final actual fourth/fifth continuous run

Task TASK01 / EXPERIMENTAL Cube04 precision + engineering empty retreat. Legacy3ee42d2/controller binary77b4f499..., reproduction5c72a1a atlaunch; uncontrolledOMPL, originalslots/cells/time_scale5. Exact commands/config/pins in `results/20261003_TASK01_empty_retreat_pair_01/metadata.json`. Controllerexit0, actual batches[4,5]PASS (first3preplaced). Fourthgap0.375/deep0.244mm, fifthcenter0.530/deep0.476mm; 7778 valid sparse poses/0errors; rawpeakjoint torque34.21Nm. ReleasedcurrentCube FCL540/287samples passes, no fallbacktrigger. Simulatorstopped successfully; MoveItteardown-11 separately. Basic/long no-command FK/FCL and isolated fifthalsoPASS; final report TASK01_EMPTY_RETREAT_REPAIR. No YAML freeze/full-five/reliability proof; all prior failures preserved.

## 2026-10-03 — TASK01 empty retreat software regression

Result: PASS software only. Commands: `colcon build --packages-select fr3_dual_palletize --symlink-install --executor sequential --cmake-args -DCMAKE_BUILD_TYPE=Release`, C++ policy -Wall/-Wextra/-Werror, Python unittest19/19, benchmark draft analytic checker PASS/36nulls. No robot commands yet in this iteration. Report: TASK01_EMPTY_RETREAT_REPAIR.md. Real RobotModel and physical trials next.

Follow-up runs: `20261003_TASK01_empty_retreat_unit` basic + long deterministic rounded-seed FK/FCL replay PASS (initial probe-only input mistake retained); `20261003_TASK01_empty_retreat_center_01` actual fifth full physical exit0/PASS, 0.540mm error, 0.514mm deepgap, 4691 samples/0errors. CurrentCube FCL included, no fallback trigger, no threshold/model/physics change. Four preplaced not executed; exact commands/source hashes in run metadata. MoveIt teardown -11. `...empty_retreat_pair_01` starts next clean fourth/fifth experiment.

## 2026-10-03 — Final Cube04 variant physical result: PARTIAL
- `_03`: PARTIAL_CUBE04_PASS_CUBE05_EMPTY_RETREAT_PLANNING_ABORT. Exact final source `7be3659`, binary `daec912…`, time_scale=5. Actual batch4 PASS (neighbor 0.227 mm, deep 0.413 mm); batch5 transport/drop done, empty retreat invalid FK path rejected, no fifth rear push. Controller exit 1, move_group teardown -11.
- 8,985 sparse post-step snapshots, 0 sampler/integrity errors; fourth helper closed inside=0, inner trim commands=0; fourth lateral span 0.205 mm/yaw max 0.053 deg, max raw push joint torque 24.29 Nm. Not calibrated contact wrench. First three pre-placed: not full-five proof or stable-success estimate. Both test processes stopped.
- Python regression 19/19 PASS; C++ policy/syntax/diff checks PASS; unchanged benchmark analytic checker PASS with 36 nulls/hash `a49d60…`. No paper/TASK02 implementation.

## 2026-10-03 — Cube04 precise staging is not sufficient in first physical trial
- `_02`: FAIL_CUBE04_FINAL_NEIGHBOR_GAP_SAFE_STOP, controller exit 1, zero completed new batches. Initial Y error 0.046 mm / oriented clearance 0.454 mm; final original axis-gap acceptance 1.827 mm, oriented projected gap 1.607 mm. Cube05 not executed. Raw push torque max 23.0 Nm. 6,036 sparse samples, zero integrity errors, no helper-side suction/inner trim. MoveIt teardown -11 retained separately.
- `_03`: FINAL_BUILD_REPETITION_RUNNING, time_scale=5 instead of 3, clean original physics, same original gates; not a new force/feedback algorithm. Exact source/binary identity will be recorded.

## 2026-10-03 — Cube04 precision variant startup
- C++ policy regression and Python syntax PASS. Package build PASS; non-portable directive-inside-logging-macro warning removed before final test build.
- `20261003_TASK01_cube04_precision_01`: FAIL_NEW_PROBE_STARTUP_API, no controller execution; initially passed extra argument to legacy callback subscription; raw startup preserved. Final probe uses existing verified post-step API and exception artifact writer.
- `20261003_TASK01_cube04_precision_02`: RUNNING_CHECKPOINT; first three pre-placed/physically settled, Cube04/05 physical execution pending. Not full-five proof; scene/material/final gates unchanged.

## 2026-10-03 — TASK01 fixed-contact TCP roll diagnostic
- Same `20261003_TASK01_fixture_protocol_clearance` run family, additional `roll_sweep_summary.json`: fixed face center/normal, TCP roll 0..345 deg in 15 deg steps, 24/24 poses have lateral rod/Cube03 OBB intersection, zero clear box-only poses. No robot commands; no arbitrary-contact/IK completeness claim. New regression passes; 18 Python offline tests total.

## 2026-10-03 — TASK01 controlled hold, protocol geometry and actual material
- `20261003_TASK01_fr3_static_payload_v2`: PASS_CONTROLLED_HOLD_AND_CUBE01 / PARTIAL_METROLOGY. Default-zero optional 7-s task-thread hold, legacy 76408c8; controller exit 0, placement/HOME complete. 34,510 snapshots, 238 full-rate load samples. Mean net-support error 0.000370 N but instantaneous RMS 0.494278 N / moment mean 0.014902 Nm and velocity discrepancy persist. Raw six-step diagnostic was aliased; full-rate reanalysis does not convert this into a sensor PASS.
- `20261003_TASK01_fixture_protocol_clearance`: REQUIRED_SIDE_POSE_INTERFERES. Read exact existing xacro and prior full-flow Cube03 PhysX pose; Cube04 centered right helper support boxes intersect neighbor, minimum lateral SAT axis overlap 33.524 mm. Analytic only, no commands/model changes. Metadata + summary tracked.
- `20261003_TASK01_mass_material_audit`, `_v2`, `_v3`: Initial two PARTIAL audits retained; final PASS_MASS_AND_SHAPE_READOUT / MODEL_REVIEW_PENDING. Cube actual mass 0.800000012 kg, static/dynamic friction 0.5/0.5, restitution 0.0. Declared 0.90/0.75 material deleted by cleanup; no effective combine-rule freeze. Initial wrong tool path corrected in reader only; no scene changed.
- `python3 -m unittest discover -s platforms/isaac_ros2/probes -p 'test_*.py' -v`: 17/17 PASS. YAML checker still analytic PASS / 36 unresolved, not TASK01 PASS. Report `TASK01_RUNTIME_REVIEW_20261003.md` contains commands, results and boundaries.
- MoveIt SIGINT teardown again exit -11; retained full-five raw launch log. Test processes fully stopped; no ordinary controller failure inferred from teardown.

## 2026-10-03 — TASK01 completed normal feed and retained failed metrology
- results/20261003_TASK01_full_five_corrected_01/: PASS_LEGACY_FIVE_CUBE_DEMO_ONLY, controller exit 0, physical batches 1–5 complete, both arms HOME, wall 1284.391 s. Detailed physical geometry and 70,434-snapshot integrity analysis uploaded; raw heavy remains ignored. BUG-009 contact protocol not passed.
- results/20261003_TASK01_fr3_static_payload/: FAIL_EXPERIMENTAL_PAUSE_THEN_SAFE_ABORT, 7-s SIGSTOP of controller group also pauses state monitor; resume triggers stale-state failure and releases both cups. Raw script/negative logs preserved; no normal-flow regression claimed.
- Fresh results/20261003_TASK01_fr3_static_payload_v2/ is controlled opt-in task-thread hold instead of process suspension; phase recorded with physical snapshots. Build PASS 47.9 s; physical force statistics pending at this checkpoint.

## 2026-10-03 — TASK01 corrected runtime checkpoint
- Run: results/20261003_TASK01_preclose_unit/metadata.json — PASS_UNIT_AND_BUILD_ONLY. Residual regression and corrected colcon build PASS; initial target include-path failure retained.
- Run: results/20261003_TASK01_full_five_corrected_01/metadata.json — RUNNING_CHECKPOINT. Fresh headless normal feed, max_batches=5, right center pusher, time_scale=3, no pre-placed fixture. Cube01 complete; Cube02 pre-close correction passes original gate. Final completion/force/pose audit pending.
- Link8 authored incoming fixed-joint anchor/axes audit succeeds; empty-branch static force/torque consistency is preliminary only, not dynamic contact/internal-force calibration.

Append-only experiment index.

At repository initialization, no experiments had been run.

## 2026-09-30 20260930_TASK00_mujoco_smoke
Task: TASK00
Baseline: none; environment smoke test only
Platform: existing isolated MuJoCo .venv
Commit at probe: 9f71e0a78a9d852d060b4e7e4c3225558d1d9bb1
Seed: not applicable
Command: see results/20260930_TASK00_mujoco_smoke/metadata.yaml
Config: inline one-joint sphere model
Result: PASS
Key metrics: MuJoCo 3.13.0; one mj_step advanced simulation time to 0.002 s
Artifacts: results/20260930_TASK00_mujoco_smoke/
Notes: This is not a dual-arm force-control or paper-reproduction experiment.

## 2026-09-30 20260930_TASK01_static_geometry
Task: TASK01
Baseline: none; candidate geometry check only
Platform: system Python 3 + PyYAML; analytic validation (not Isaac)
Commit at probe: ca2b1f75a85c32bcad87b193328cbe7424680183
Seed: not applicable
Command: `python3 scripts/validate_benchmark_candidate.py`
Config: `configs/benchmark/benchmark_v1.yaml` (DRAFT)
Result: PASS for internal analytic geometry; TASK01 itself remains IN_PROGRESS
Key metrics: 0 failed dimension checks; 30 unresolved/null configuration fields
Artifacts: `results/20260930_TASK01_static_geometry/`
Notes: No physical contact, collision, sensing or timing validation was performed.

## 2026-09-30 20260930_TASK01_contact_protocol
Task: TASK01
Baseline: none; candidate protocol and geometry check only
Platform: system Python 3 + PyYAML; analytic validation (not Isaac)
Commit at probe: 93e7e54 (parent of uncommitted draft)
Seed: not applicable
Command: `python3 scripts/validate_benchmark_candidate.py`
Config: `configs/benchmark/benchmark_v1.yaml` (DRAFT)
Result: PASS for internal analytic geometry/protocol; TASK01 itself remains IN_PROGRESS
Key metrics: 0 failed checks; 36 unresolved/null configuration fields; 1° yaw consumes 1.038 mm nominal center clearance
Artifacts: `results/20260930_TASK01_contact_protocol/`
Notes: No physical contact, collision, sensing or timing validation was performed.

## 2026-09-30 20260930_TASK01_center_right_physical
Task: TASK01
Baseline: none; experimental Task27 fifth-Cube probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit at probe: 76d24dc (new repo), d93f285 (legacy repo), with working-tree test patch later committed unchanged as 631b1f6
Seed: not fixed in legacy OMPL
Command/config: `results/20260930_TASK01_center_right_physical/metadata.yaml`
Result: PASS, one physical run; four fixtures pre-placed
Key metrics: Cube 05 final center 0.603 mm; +X wall gap 0.586 mm; +Y/-Y side gaps 1.361/1.639 mm; peak joint torque 35.96 Nm
Artifacts: metadata, `reports/TASK01_CENTER_ARM_SYMMETRY.md`, external raw ROS log listed therein

## 2026-09-30 20260930_TASK01_center_left_physical
Task: TASK01
Baseline: none; experimental Task27 fifth-Cube probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit at probe: 76d24dc (new repo), d93f285 (legacy repo), with working-tree test patch later committed unchanged as 631b1f6
Seed: not fixed in legacy OMPL
Command/config: `results/20260930_TASK01_center_left_physical/metadata.yaml`
Result: PASS, one independent physical run; four fixtures pre-placed
Key metrics: Cube 05 final center 0.669 mm; +X wall gap 0.633 mm; +Y/-Y side gaps 1.719/1.281 mm; peak joint torque 35.87 Nm; one pre-close reacquire
Artifacts: metadata, `reports/TASK01_CENTER_ARM_SYMMETRY.md`, external raw ROS log listed therein
Notes: Both arms HOME. Left and right results differ; no statistical equivalence is claimed.

## 2026-10-02 20261002_TASK01_center_repeatability
Task: TASK01
Baseline: none; [EXPERIMENTAL] legacy Task27 Cube 05 arm-symmetry probe
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Seed: uncontrolled legacy OMPL (no fixed-seed claim)
Command/config: Four per-run `results/20261002_TASK01_center_{right,left}_{02,03}/metadata.yaml` files; benchmark draft `configs/benchmark/benchmark_v1.yaml`
Result: Four new physical runs PASS with both arms HOME; including 2026-09-30, right 3/3 and left 3/3 PASS. TASK01 remains IN_PROGRESS.
Key metrics: right center error [0.603, 0.429, 0.374] mm, mean 0.469 mm; left [0.669, 0.408, 0.561] mm, mean 0.546 mm; maximum side-gap imbalance 0.582/0.802 mm (right/left).
Artifacts: `reports/TASK01_CENTER_ARM_SYMMETRY.md`, four per-run metadata files, external raw ROS logs named there; scripts `task01_capture_final_pose.py` and `summarize_task01_center_trials.py`.
Limitations: Four fixture cubes were pre-placed; no contact wrench; motion-time PhysX/USD pose disagreement remains open (BUG-005). `move_group` repeatedly segfaulted during Ctrl-C teardown after completed task runs (BUG-004).
Notes: Both arms HOME. Not a reproducibility or statistical symmetry result.

## 2026-10-03 TASK01 known-motion sensor diagnosis/calibration
Task: TASK01
Baseline: none; [EXPERIMENTAL] measurement calibration, not contact control
Platform: Isaac Sim 4.5; external ROS2 Humble observer
Commit: b442ecb22c635e9eb90453fff61bcffa45103ce1 plus uncommitted measurement changes committed with this report
Seed: no random sampling
Command/config: Per-run metadata in results/20261003_TASK01_pose_timing/, physics_ros_30hz/, physics_ros_debug/, physics_ros_clean_30hz/, physics_ros_zero_damping_30hz/ and physics_ros_zero_damping_20hz/
Result: Initial no-ROS pose diagnosis passed. Mixed-library startups failed; clean-ROS angular calibration initially failed because the known-motion model omitted angular damping. Explicit zero damping on the free calibration body then produced two PASS_SENSOR_CALIBRATION results; gates unchanged.
Key metrics: 120 motion samples/run; p_max=0.000312946/0.000312902 mm, angle_max=0.000864737/0.000864742 deg (30/20 Hz frames, 60 Hz physics); callback errors=0; legacy USD callback lag=6.667/10.000 mm; scaled-quaternion error up to 27.464 deg.
Artifacts: Per-run metadata and ignored raw JSONL/JSON; reports/TASK01_PHYSICS_POSE_MEASUREMENT.md
Boundary: Deterministic no-contact free body; not manipulation accuracy or a benchmark gate. Explicit zero damping is not a change to Task27 physics.

## 2026-10-03 TASK01 fixture physics-channel integration
Task: TASK01
Baseline: none; [EXPERIMENTAL] pre-placed four-Cube fixture + legacy right-arm fifth-Cube task
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit: b442ecb22c635e9eb90453fff61bcffa45103ce1 plus uncommitted measurement adapter; legacy unchanged at 631b1f65656d025c1bb2173e874192f3fe4d355a
Seed: uncontrolled legacy OMPL
Command/config: results/20261003_TASK01_fixture_sampler_startup/metadata.yaml (failed startup) and results/20261003_TASK01_fixture_physics_channel/metadata.yaml (physical run)
Result: Unsupported tuple constructor argument caused first startup FAIL without robot commands. Corrected list initialization; fresh-scene right-arm full Cube 05 task PASS and independent physics recorder PASS.
Key metrics: center error 0.520 mm; deep gap 0.505 mm; side gaps 1.374/1.626 mm; peak joint torque 35.41 Nm; both arms HOME; logged task duration 215.142 s. Recorder: 14,295 samples, no missing physics steps, no errors, timestamps increasing. Final physical yaw 0.026334 deg versus legacy Bridge 0 deg.
Artifacts: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md; selected result summary + metadata; ROS log /home/ubuntu2004/.ros/log/task27_five_cube_center_insert_32050_1791006079693.log; ignored 32-MB physics snapshot JSONL.
Boundary: New topic is read-only, controller still consumes legacy Bridge; no claim of a synchronized wrench/TCP contract or complete five-Cube fixture construction. MoveIt SIGINT -2 today does not resolve prior BUG-004.

## 2026-10-03 TASK01 final measurement regression / empty-input guard
Task: TASK01
Baseline: none; [ENGINEERING] final measurement checks, [EXPERIMENTAL] known-motion fixture
Platform: Isaac Sim 4.5 + external ROS2 Humble; guard test without an Isaac publisher
Commit: b442ecb22c635e9eb90453fff61bcffa45103ce1 plus final working-tree measurement changes
Seed: no random sampling / not applicable
Command/config: results/20261003_TASK01_final_calibration_30hz/metadata.yaml and results/20261003_TASK01_recorder_empty_guard/metadata.yaml
Result: Final 30 Hz external calibration PASS including exact position/quaternion equality of PoseArray and JSON snapshot. Empty stream yielded saved FAIL summary and exit 1 (negative test PASS, not sensor success).
Key metrics: 120 motion / 150 total pose samples; p_max=0.000312945784 mm, angle_max=0.000864737421 deg; zero callback errors. Empty guard: zero samples, 2-s startup timeout.
Artifacts: Per-run metadata, ignored raw summaries, reports/TASK01_PHYSICS_POSE_MEASUREMENT.md
Boundary: No paper controller, no altered benchmark gate; failure is kept distinguishable from physical task success.

## 2026-10-03 TASK01 collision force/torque calibration
Task: TASK01
Baseline: none; [EXPERIMENTAL] independent known-load fixture, [ENGINEERING] measurement sampler
Platform: Isaac Sim 4.5 PhysX CPU/numpy
Commit: 32ccb2b902ab23cd5f60c191d579ff7e2ccc7fe6 plus per-run uncommitted probe variants saved in this iteration; benchmark SHA unchanged
Seed: no random sampling
Command/config: results/20261003_TASK01_contact_force_{60hz,60hz_v2,60hz_v3,60hz_torque,120hz_yaw30}/metadata.json; probe paths/arguments/variant recorded separately
Results: First startup FAIL (nonexistent PhysicsContext getter); second startup FAIL (unsupported SingleRigidPrim keyword). Corrected 60 Hz v3 PASS has no nonzero torque stage and is not torque evidence. Final 60 Hz torque and 120 Hz/yaw30 runs each PASS all 13 checks. Saved check results are authoritative; early exceptions can still exit 0 with fast shutdown.
Key metrics: support 7.84800024/7.84799969 N; friction Fx -1.99999991/-2.00000003 N; resisting Tz -0.03996668/-0.03998334 Nm; wall yaw0/yaw30 (Fx,Fy)=(-4,0)/(-3.464101,-2) N. Each main window 60/120 samples. Dual suction CLOSED supports payload at 0.500 m while collision signal is zero, proving this interface excludes suction D6 forces.
Artifacts: per-run metadata/selected summary, ignored raw contact_samples.jsonl and Kit logs; reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md.
Boundary: Fixed calibration gates (0.05 N, 0.001 Nm) belong only to independent fixture. No benchmark material/physics/threshold change or paper/internal-force control.

## 2026-10-03 TASK01 incoming mount reaction / reference identification
Task: TASK01
Baseline: none; [EXPERIMENTAL] static articulated mount and suction payload
Platform: Isaac Sim 4.5 PhysX, Surface Gripper
Commit: 32ccb2b plus explicitly different uncommitted probe variants; seed not applicable
Command/config: per-run metadata in mount_reaction_identity, mount_reaction_roll90, mount_reference_identity, mount_joint_reference, mount_joint_reference_unscaled and mount_joint_reference_final under results/20261003_TASK01_*/
Results: Identity/roll90 trials establish known-load availability/direction, not reference-point identity because frames/points coincide. Early scaled-body COM trials have saved software PASS, but their unscaled COM/anchor interpretation is INVALIDATED; metadata reviewed status PARTIAL_REFERENCE_MODEL_INVALIDATED, raw kept. Final two unscaled trials PASS unique joint_axes_about_joint_anchor among nine hypotheses, verify physics COM=5 mm, principal roll45, joint anchor3 mm/joint roll30, payload hold and CLOSED/timestamps. Final field-name regression repeats exact numeric result.
Key metrics: known payload 0.8 kg, world Fz=7.848 N and Ty=-1.255680 Nm; final raw delta (Fx,Fy,Fz) about (0,6.796570575,-3.923998765) N, (Tx,Ty,Tz) about (0,0.616067643,1.067061339) Nm. Correct joint-axis/anchor error 3.435906e-6 N/4.429936e-7 Nm; wrong link origin 0.023544 Nm, wrong COM 0.015696 Nm, wrong link axes 4.0624 N.
Artifacts: metadata/selected summary, raw mount_samples.jsonl and Kit logs; force report.
Boundary: Not real FR3 compensation or universal rotating-joint convention validation. Hidden tool branch mass was not removed; false early origin inference explicitly corrected rather than silently erased.

## 2026-10-03 TASK01 full normal-feed five-Cube readout/preflight/execution
Task: TASK01
Baseline: none; [EXPERIMENTAL] unchanged legacy Task27 normal five-Cube flow, no pre-placed fixture
Platform: Isaac Sim 4.5 + ROS2 Humble + MoveIt2/FCL
Commit: 32ccb2b plus measurement runner variants; legacy unchanged at 631b1f65656d025c1bb2173e874192f3fe4d355a
Seed: legacy OMPL uncontrolled; no fixed-seed/repeatability claim
Command/config: results/20261003_TASK01_full_fixture_readout/, full_fixture_readout_v2/, full_five_physical/, full_five_preflight/, full_five_physical_v2/ and full_fixture_frame_audit/ metadata.json; full report contains all scene/bridge/MoveIt/controller commands
Results: Initial readout FAIL nonexistent STATE_READY; corrected v2 PASS_READOUT_STARTUP. Full-run startup FAIL bridge-overwritten namespace/BOX_INTERIOR_X; corrected run ready. Five planning-only batches PASS. Actual run FAIL: completed1/5, Cube02 stopped at PRE_CLOSE before suction, no later physical object commanded. Last added authored-frame startup audit FAIL on remote asset-root lookup (no robot commands), so that audit unverified.
Key metrics: 37,236 physics/contact/raw joint snapshots, zero callback errors; feed state [2,2,0,0,0] is ARRIVED, not placement. Cube02 gap delta 0.968 -> 0.315 -> 0.339 mm vs original 0.300 mm gate, minimum correction0.650 mm; independent physical final delta0.338941 mm. Cube01 center error1.792 mm, physical yaw -1.095465 deg; nearest oriented deep/+Y gaps0.06355/0.19531 mm, not whole-face flush. Peak Cube01-deepwall collision resultant139.098 N, not suction/internal wrench or a frozen force gate. MoveIt teardown -11 recurs.
Artifacts: selected metadata/summaries, full report; local ignored raw controller/MoveIt/Kit logs, topology and approximately1 GB physics_contact_samples.jsonl.
Boundary: Measurement completion and planning PASS are not physical full-flow PASS. Control event wall time is not yet aligned to recorded simulation time. New quaternion/force sampler is read-only; original controller still consumes old pose channel. TASK01 IN_PROGRESS, 36 fields unresolved, TASK02 TODO.

## 2026-10-03 TASK01 final offline/static validation
Task: TASK01
Baseline: none; [ENGINEERING] sampler algebra/guard tests and artifact checks
Platform: Python3/numpy offline
Commit: 32ccb2b plus final measurement changes
Seed: not applicable
Commands: python3 platforms/isaac_ros2/probes/test_physics_contact_sampler.py; python3 -m py_compile (five new Python files); python3 scripts/validate_benchmark_candidate.py; git diff --check; sha256sum configs/benchmark/benchmark_v1.yaml
Results: 8/8 unit tests PASS; Python compile and static checks PASS, analytic draft reports36 unresolved nulls. Draft hash a49d60a4dc6a8a00c3bf55a512113af50760968827a8cefe64dae1c7de55fde8 unchanged.
Artifacts: results/20261003_TASK01_contact_sampler_unit/{metadata,summary}.json; reports/TASK01_FREEZE_REVIEW_CHECKLIST.md lists all36 fields and explicitly pending approvals.
Boundary: These tests do not establish a frozen benchmark or five-Cube physical success.

## 2026-10-03 TASK01 full recorded-stream integrity
Task: TASK01; baseline none, [ENGINEERING] read-only artifact audit
Platform: Python3 JSONL, offline; seed not applicable; commit32ccb2b plus recorded measurement variants
Command/config: Self-contained Python stdin scan in results/20261003_TASK01_full_record_integrity/metadata.json, reading full_five_physical_v2/raw/physics_contact_samples.jsonl
Result: PASS_RECORD_INTEGRITY across37,236 rows. Missing steps, nonmonotonic steps/stamps, contact/pose stamp-step mismatches and nonfinite contact/articulation arrays all0. Maximum force-matrix vs normal reconstruction error1.525879e-5 N; dt0.0166666675359 s; Cube quaternion norm-squared error4.44e-16.
Artifacts: metadata.json/summary.json and original ignored JSONL. Does not turn the incomplete physical task into PASS or establish ROS-event clock alignment/FR3 wrench compensation.

Recommended entry:
```text
## <date> <run_id>
Task:
Baseline:
Platform:
Commit:
Seed:
Command:
Config:
Result: PASS/FAIL
Key metrics:
Artifacts:
Notes:
```

## 2026-10-14 — D079：全文接续R0来源和协议冻结

同名已有分支同步6276f78，隔离worktree并保全五原工作树13未跟踪文件。全文8页/式1–9/Fig1–5/TableI–II已重读；找到全部六环境七作者快照，30父义务/169完整入口。旧RSS9996目标独立SE2回放全部不可达；旧PCS92解边全p0，不改旧失败/结论。
R1有限资格协议 configs/p4_full/r1_qualification_v1.json：总1800s，单构建/诊断120s，正式规划0。完整TableI22500调用/最坏6250核小时待具体预算裁决。旧P4/P2文件1282条SHA保护；只追加治理记录。源码与资产外部固定引用，不重发布未授权原文/网格。当前P4整体仍部分完成，P2/Isaac不开展。
证据：reports/p4_full_audit/ORIGINAL_FULL_COVERAGE_MATRIX.md，reports/P4_FULL_PRE_TASK_D079.md，reports/P4_FULL_SOURCE_ENVIRONMENT_AUDIT.md，reports/P4_FULL_FAILURE_ROOT_CAUSE_REVIEW_D079.md，reports/P4_FULL_BUDGET_AND_DECISIONS_D079.md。


## 2026-10-15 — P4 D079 原生六环境R1真实资格与报告归档

实测1826项=1580通过+246失败，六环境组件资格均未通过；正式规划0。保存400空间IK/40平面APC/60NR的独立分母，近似π、Comau带符号几何、RSS非真奇异和VI源码缺项分别有证据，不改判旧失败。211项全文对照和9页中文Word/PDF已生成；交付完整性20/20，不等于科学通过。1282原科学文件、1194作者文件、五原工作树及13未跟踪文件均保全。
见 reports/P4_FULL_R1_POST_TASK_20261015.md。用户在具体有限修复提案后回复“继续”，下一阶段仅在独立R2命名空间按2核小时/1小时墙时进行数值一致修复资格；原模型尺寸/基座/抓持/端点/判据不变，正式22500调用预算另审。P4仍部分完成，不启动P2/Isaac/FR3适配。

## 2026-10-15 — P4恢复读账（不是新实验）

只读核对旧R2三run execution.json：20261015_R2_SPATIAL01、20261015_R2_PLANAR01、20261015_R2_RSS_CONSTRUCTION01，合计wall16.337196963s/CPU10.593126s。保存原样，无新IK/NR/采样/规划。端点恢复与VI RSS待新协议/源码提交后执行，VI批准预算尚未消耗。


## 2026-10-15 — P4 R2恢复：A端点完成、IV NR局部完成、VI严格桥仍UNKNOWN

实际命令与配置、seed、source commit、hash、终止原因详各results/p4_full/20261015_R2_*/execution.json。A01 wall7.450141228/CPU6.025647，A02 1.321430518/1.324637；VI Q1 45.133593772/5.641175，seed[7,23,41,101,20261013]；VI Q2固定219/643、无RNG、36/576IK、7.987086492/6.310368、四桥UNKNOWN_DEPTH_CAP；IV local固定24、2.651571520/.882651、24/24。9run总80.902103069/30.799802，sum自身时长不重复累计；正式规划0。具体账本results/p4_full/20261015_RECOVERY_ACTUAL_LEDGER.json。


## 2026-10-15 — P4 R2接续12run：fiber组件通过、旧48真实碰撞已补齐

继续原p4-full-reproduction-pcs-study工作树，R0/R1及崩溃前57文件保全。CENTER_IMAGE01仅2固定active FK/J；FIBER_COMPONENT01固定6节点6/6，54FK/J、6源碰撞/798PQP，原Q2严格桥UNKNOWN及regular↔fiber未验证保持。旧48数学合格RSS分支一次补验：II10clear/8碰撞、III16clear/6碰撞、V0clear/8碰撞，96native/aligned、192内部FK/J、9996PQP API返回无错误；未重做700目标/5600IK，未执行原checkEE。V具体碰撞pair根因UNKNOWN，未据该批判整个模式无解。 当前12run自身成本合计95.365357389998wall秒/45.058033CPU秒，R2余3504.634642610002/7154.941967。VI B累计910构造、54.513982463999wall/13.327177CPU，余50构造/125.486017536001wall/346.672823CPU。旧48仅扣R2、不扣B。不得重置claim、重跑原预算或重复加cumulative。 实际命令及完整依赖SHA见reports/P4_FULL_R2_CONTINUATION_POST_TASK_20261015.md与各run execution；本三项均固定保存输入，无新随机种子/规划事件。


## 2026-10-15 P4 R2 原RRT_PCS单目标工程实际执行

冻结来源85acfd55e32882dfc4cf6b08a3a3c7a43c32a97c；命令 `python3 scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py --protocol configs/p4_full/r2_abb_rrt_pcs_e2e_engineering_v1.json`。唯一E2E_BUILD01 exit0、BUILT_NOT_QUERIED，wall17.12737691100483s、CPU23.727903s；query/solve/VI构造均0。66旧资产前后hash一致，34编译源码/头和20网格绑定，binary SHA6218557517f9f169fedcfdd25d8284407148de695755721f14651bc842a54ae1。工程成本保守扣R2，16execution累计302.4154392770006wall/288.16398300000003CPU；原科学失败不变。详见results/p4_full/20261015_R2_ABB_RRT_PCS_E2E_BUILD01/execution.json。


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
