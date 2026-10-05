# STATUS

## 2026-10-05 follow-up — 首件X双吸推入通过，Y互锁失败；实测换角复测中

`dual_fixture_cube01`/ff20ac3 controller1/completed=[]；16/16 X片段双CLOSED，deep gap0.286mm，随后Y起步active interlock停止/双OPEN，不是首件完整PASS。4747稀疏PhysX样本/0完整性错误；Cube02–05未推进。旧guard没具体原因，暂不能断言是力矩/吸附/物理不可行。

发现X末tracking残差0.551deg，e0477ab新增从双臂实测/新Cube GT重新规划Y与current-start FCL、详细互锁诊断；新鲜原场景首件复测中，尚无新版PASS。35 Python /4 C++ /build PASS。源码/负证据与后续计划持续上传，报告TASK01_DUAL_SUCTION_FIXTURE。TASK01 IN_PROGRESS /36nulls/TASK02 TODO；原场景/物理/ACM/门限/YAML不变。

## 2026-10-05 — 新3+2接触协议已搭建，首块物理验证运行中

用户批准前三件双吸附主从推压、后两精准单rear插入。独立运行节点 `task01_dual_suction_fixture` / runtime `ff20ac3` 编译通过；34个Python测试、4个C++策略测试通过。新无执行探针前三件名义接触/X推入/Y压紧/局部释放退出通过联合FR3 FCL和相对TCP检查（最大轴向变化约0.002mm）；早期探针负结果保留。

新鲜原场景首件试验 `results/20261005_TASK01_dual_fixture_cube01/` 已启动（first1/max1/scale5/hold0/无预置），目前没有新物理PASS。旧节点df9c2c0的一次5/5仍有效但不证明新协议。原场景/教师认可L工具/物理/ACM/门限及YAML不变；TASK01 IN_PROGRESS / DRAFT /36nulls，TASK02 TODO。报告：`reports/TASK01_DUAL_SUCTION_FIXTURE.md`。下方“final”为保留历史结果。

## 2026-10-04 final — 普通供料五件物理回归 5/5 PASS，基准仍未冻结

本机 Isaac 4.5 **headless**、零预置、普通释放 hold=0 的 `empty_rrt_full_01` 完成 batch 1–5，控制器 exit=0，双臂最终 HOME / 双杯 OPEN。运行源码 `df9c2c0`，二进制 `c760d506…`。五件中心误差分别 1.983 / 0.807 / 0.723 / 1.319 / 0.481 mm；第四邻块缝隙 0.347 mm，第五两侧缝隙 1.987 / 1.473 mm。18,498 条稀疏 PhysX 记录，完整性错误 0；3,212 条释放诊断记录。

这是一轮实际完整执行，不是 GUI 验收、长期稳定性或论文复现证明。普通 Cartesian 空载退出本轮都成功，新增有限 RRT 备用**没有物理触发**；备用仅有失败姿态四位小数重放 / 1,277 次联合 FCL 的无机器人命令验证。BUG-016 历史 Cube02 释放回带本次未复现，原因仍 OPEN；已有对象严格恢复比较问题仍未隔离。所有自有运行进程已停止，MoveIt 关闭时 -11 / joint bridge 1 与控制器 0 分开记录。

最新报告：`reports/TASK01_RELEASE_CLEARANCE.md`。原场景、材质、质量、ACM、验收门限及 YAML 未改变。TASK01 保持 IN_PROGRESS / DRAFT / 36 nulls；TASK02 TODO。下方 running / failure 项均为保留的历史 checkpoint，本段为最新结果。

## 2026-10-04 — Empty RRT no-command replay PASS; clean physics regression running

Runtime df9c2c0 built55.8s; binaryc760d506...; correctedrailshift0.1m failedCube02rounded-seedreplay02exit0/fullFCL1277samples, CLOSED/obstructedstartreject and absent-IDsyncsceneundoPASS. Replay01negativepreserved; existing-objectstrictcomparisonproblemnotclaimedresolved. No Arm/joint/suctioncommandsinprobe. New ordinary0preplacedfirst1/max5/scale5/hold0 localheadlessrunempty_rrt_full_01 started, nofinalphysicsPASSyet. Sourcepushed, TASK01IN_PROGRESS/36nulls/TASK02TODO; BUG016remainsOPEN.

## 2026-10-04 — Ordinary second-Cube retreat rejected; bounded empty RRT preparing

Ordinary measured_side_full_01 controllerexit1/completed[1], Cube01cell0.678/deep0.670/side0.108mm. Cube02dropped/bothOPEN, measured-commanddelta0.000681/0.000995rad, CartesianFK752–967mm rejected; continuousIKfails118/151. EarlierCube02retreatPASSuseddifferentredundantconfiguration; notblanketlogicregression/rootcauseproof. Headlesslocalteststoppedaftercontrollerabort,17319sparseposes0errors. AddedunbuiltOPEN-onlyRRTbackupwithsameactualstart/originalgoal/fullreleasedCubeFCL, ≤3plans/arm; numeric/bounds/adapterstart/goalchecksandverifiedscenecleanup. Pendingreal-model/physicsvalidation, BUG016stillOPEN. No model/physics/ACM/gate/YAMLchange,TASK01IN_PROGRESS/36nulls,TASK02TODO.

## 2026-10-04 — Diagnostic stopped safely; measured side start built

Diagnostic02 exit1/completed[1]; Cube02 before release side-approach t0 commanded-seed/currentCube collision0.783mm, deepseat1.804mm. Firstcubeholdstable notsecondcubeproof. Preserved13227poses/0errors/1617contacts, stoppedallownedprocesses/teardown-11. Independent actual side start nowusesone measuredRobotState, CLOSEDpusher/OPENhelper, existingjointdelta/bounds, strictcurrentCubeFCL. Runtime2fbfa0b/build+policyPASS/Python28PASS. Norelease-control/rootcause claim yet; cleanordinaryhold0/fullfive preparing. ReportTASK01_RELEASE_CLEARANCE, TASK01IN_PROGRESS/36nulls/TASK02TODO.

## 2026-10-04 — Diagnostic physical checkpoint, not a control fix

Runtime b259366 buildPASS56.5s, diagnostic02 physically running with3s hold after OPEN. Cube01 release-hold deltaX0.028mm and clearance deltaX0.000mm, hence first object does not reproduce previous Cube02 failure. Cube02 underway. Initial diagnostic01 startupBRANCH_SIGN ordering failure archived (processclose returned0 despite failure.json); no controller was started then. Logger uses bridge namespace for signs, not scene edit. Python28/28PASS including peak/mixed-step guards. Stop diagnostic after second completed batch before later object control; no normal-flow or reliability claim. Prior full-flowFAIL retained, no active release-motion repair yet.

## 2026-10-04 — Release-window diagnostic underway

User approved continuing BUG-016 repair. Added independent-variant release/clearance stage topic and optional3s post-release main-thread diagnostic hold (ordinarydefault0), plus read-only same-physics-step tools/collision logger active only inside release window. Software25testsPASS, build/physics pending. No scene/model/material/gripper/ACM/gate or active release-control fix yet. Report TASK01_RELEASE_CLEARANCE. TASK01 IN_PROGRESS/36nulls,TASK02TODO; priorXYZPASS/full-flowFAIL preserved.

## 2026-10-04 final — XYZ pre-close verified, full flow still FAIL

User-approved independent XYZ extension compiled, C++/22 Python/real RobotModel XYZ+FCL PASS. Normal-feed run: Cube01 batchPASS; Cube02 physically corrects X2.012→0.606mm/Z1.589→0.451mm/gapdelta0.879→0.275mm within original gates, then grasps/transports/pushes. But after side pressing and rear release, deep gap grows0.488→5.138mm > original3mm, exit1/completed1of5; Cube03–05notadvanced. Two XYZ moves total1mm cap, planning0.078621s/execution7.569621s atscale5. 7680valid sparse PhysX poses/0errors; static FK–Isaac difference norm max0.056mm, no hard dynamic timing proof. All owned processes stopped, teardown-11 repeats. Runtime f0812a4; full report `reports/TASK01_PRECLOSE_XYZ.md`, BUG-016 release-window diagnosis needs next-scope review. No scene/model/physics/ACM/gate/loaded-control/YAML changes; TASK01 IN_PROGRESS,36nulls,TASK02TODO. GitHub transport recovered with command-local existing HTTP CONNECT proxy, no system config edits.

## 2026-10-03 latest — Normal-feed current variant FAIL, stopped for review

Full five-object attempt (no preplacement), same tested binary/model/gates: controller exit1, only Cube01 actual PASS. Cube02 pre-close Y gap asymmetry corrects2.230→0.427→0.001mm, but X TCP mismatch3.150mm exceeds original2.500mm alignment gate; suction never enabled, Cube03–05 not advanced. 7214 sparse PhysX samples/0errors. No controller/model/physics/gate change; all owned test processes stopped, MoveItteardown-11 repeats. Report `reports/TASK01_PRECISION_FULL_FIVE_REGRESSION.md`. Prior partial/legacy PASS evidence retained; current variant is not full-flow stable. Next discuss XYZ execution residual diagnosis/correction scope plus pending model/contact/36numeric review; TASK01 IN_PROGRESS, TASK02 TODO.

## 2026-10-03 — Current variant full normal-feed regression preparing

Adding only zero-preplaced test mode and read-only summaries, then actual first_batch=1/max_batches=5 using unchanged current binary/model/physics/gates. Previous isolated fifth and fourth→fifth PASS remain scoped results. Full-flow result pending; no paper method or benchmark freeze. Report: `reports/TASK01_PRECISION_FULL_FIVE_REGRESSION.md`. Stop for user decision if model/contact/physics/gate changes become necessary; TASK02 TODO.

## 2026-10-03 final — empty-retreat engineering PASS, benchmark review pending

Final report: `reports/TASK01_EMPTY_RETREAT_REPAIR.md`. Real-model FK/FCL basic and long replay PASS; isolated Cube05 physical exit0; clean actual Cube04→Cube05 continuous physical exit0. Fourth neighbor gap0.375mm/deepgap0.244mm; fifth center error0.530mm/deepgap0.476mm. Released Cube included in actual retreat FCL; fallback not physically triggered. 7778+4691 sparse valid samples; no full-five-new-variant/reliability claim. All owned runtimes stopped; MoveIt teardown-11 remains. Code/results pushed. TASK01 IN_PROGRESS with36nulls; model/material/D004/freeze decisions remain for user review; TASK02 TODO.

## 2026-10-03 latest — empty retreat engineering repair, tests pending

New precision-variant empty retreat uses measured joint seed and bounded continuous-seed fallback, with released Cube included in strict FCL. Build + policy +19 Python tests PASS; real RobotModel / physical verification next. No scene/model/material/ACM/gate change. Report: `reports/TASK01_EMPTY_RETREAT_REPAIR.md`. TASK01 IN_PROGRESS, TASK02 TODO; 36 nulls unchanged.

Latest follow-up: real RobotModel basic/long replay PASS; isolated actual Cube05 exit0/batch5 PASS, placement0.540mm/deepgap0.514mm; ordinary measured-start retreat/FCL passes, fallback not triggered physically. New clean Cube04→05 run starting. No stable/full-five claim; MoveIt teardown -11 remains.

Last update: 2026-10-05

## Latest Cube04 variant handoff — PARTIAL, physical tests stopped

Independent `task01_cube04_precision_insert` implemented/pushed (legacy `7be3659`). Final-binary slow trial passes actual Cube04, final neighbor gap 0.227 mm / deep gap 0.413 mm, no side trim/helper side suction. Subsequent Cube05 transport/drop succeeds but empty Cartesian retreat rejected at up to 450.1-mm FK deviation; controller safely exits 1, only batch4 PASS. First faster trial failed Cube04 neighbor gate. No stable/full-five claim. 19 Python + standalone C++ policy tests PASS. All owned test processes stopped; MoveIt teardown -11 persists. Six records/results/report updated. TASK01 IN_PROGRESS; TASK02 TODO.

## Cube04 final-binary slow trial — fourth passed, fifth running

Clean time_scale=5 trial passes Cube04 original final gates: neighbor 0.227 mm, deep-wall 0.413 mm, precise staging Y error 0.040 mm. No inner trim/helper side suction; short-clearance/RRT handoff to Cube05 completes (batch4 PASS). Cube05 actual transport/insert now running. Previous time_scale=3 trial failed; do not infer stable repeatability or causal speed-only fix.

## Cube04 physical negative checkpoint

First time_scale=3 exploratory trial: precise pre-staging 0.046 mm, but final neighbor gap 1.827 mm > original 1.5 mm, safe stop; Cube05 not executed. No inner trim or helper-side suction. Final built binary now repeating from clean physics at time_scale=5; no feedback/force controller added. New failure preserved, TASK01 not passed.

## 2026-10-03 Cube04 protocol adaptation — running

User explicitly approved Cube04 adopting Cube05 precise-stage/single-rear-suction insertion. New independent executable/build/unit checks pass; Cube04/05 physical probe now running with first three pre-placed/settled. Original scenes/materials/ACM/final gates preserved. Control PRE_PUSH Y changes to the existing 0.5-mm pressed target; benchmark YAML unchanged. Report: `reports/TASK01_CUBE04_PRECISION_INSERT.md`. TASK01 remains IN_PROGRESS, TASK02 TODO.

## Project state
Repository initialized. No baseline implementation has started.

| Task | Status | Notes |
|---|---|---|
| TASK00 Environment Audit | PASS | Report: reports/TASK00_ENVIRONMENT.md; external integration gaps identified |
| TASK01 Benchmark Freeze | IN_PROGRESS | Current engineering variant normal-feed physical 5/5 once, runtime df9c2c0 / controller 0 / final HOME. Not reliability or freeze; empty RRT physically untriggered, historical BUG-016 open. First-three D004/model/force/time/36 nulls/teardown pending. Latest report TASK01_RELEASE_CLEARANCE |
| TASK02 Common Interfaces / Logger / Metrics | TODO | Depends on TASK01 |
| TASK03–06 P4 | TODO | |
| TASK07–10 P2 | TODO | |
| TASK11–15 P3 | TODO | |
| TASK16–19 P5 | TODO | |
| TASK20–26 P1 | TODO | |
| TASK27–30 Evaluation/Freeze | TODO | |
| TASK31 Ours v0 | TODO | Must wait for TASK30 |

## Current gate
**Do not implement paper algorithms yet. Draft and review TASK01 benchmark_v1 first.**

## 2026-10-03 final evidence / review stop

Latest report: `reports/TASK01_RUNTIME_REVIEW_20261003.md`. Actual five-Cube ordinary manipulation works; the additional opt-in hold also resumes and places Cube01 with exit 0. Full-rate static diagnostics expose alternating reaction and tensor/pose finite-difference velocity disagreement; no instantaneous force/internal-wrench PASS. OBB audit proves current Cube04 centered helper tool intersects Cube03. Actual material audit exposes 0.5/0.5 coefficients rather than 0.90/0.75. These need explicit model/contact direction, not silent changes under a persistence request. No YAML/null/hash change, paper implementation or frozen benchmark claim. Six records updated, all owned simulators/controllers stopped; MoveIt teardown still -11.

Further continuation: 24 fixed-center/inward-normal TCP rolls all retain lateral-support/Cube03 intersection. No box-clear rotation-only candidate found, no commands. Final offline Python regression 18/18 PASS; protocol/model review still required.

## 2026-10-03 runtime-repair checkpoint

Bounded fine pre-close correction and Task27 quaternion fix are implemented in legacy branch `task01-runtime-fixes` (`d80b6b6`); unit/build PASS. Fresh normal five-Cube physical regression is running: Cube01 complete and Cube02 pre-close passes unchanged 0.300 mm gate. No final full-flow result yet. Real link8 fixed-joint frame/anchor audit now succeeds; dynamic contact compensation still unvalidated. Legacy first-four push/inner-trim topology also differs from D004 (BUG-009), so even legacy demo completion alone cannot freeze TASK01. YAML remains DRAFT with 36 nulls; TASK02 TODO.

## 2026-10-03 completed legacy-demo checkpoint

Subsequent full run completes all five physical batches, controller exit 0 and both arms HOME. Detailed results/negative prior run remain in TASK01_FULL_FIXTURE_CONTACT_PROBE. Final center errors range 0.574–2.276 mm for the four fixtures; Cube05 controller 0.493 mm / later physical sample 0.563 mm. Rear+side simultaneously CLOSED sample count for first four is zero, so D004 is still unmet. Whole-process pause calibration safely fails on stale ROS state; replacement leaves ROS executor active and uses an explicit optional hold parameter. No benchmark freeze, physics/gate change or paper implementation.
