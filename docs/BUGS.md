# BUGS

## BUG-019 — 同一实测姿态的机器人-深墙碰撞模型不一致

2026-10-06；OPEN。精确step19753/21051实测FK与PhysX差<0.001mm，MoveIt墙FCL无碰撞，却有left link7深墙非零接触。原NVIDIA link7 mesh(convexHull)与franka_description link7 STL不同；离线原mesh凸包交集支持几何差异，而非100mm导轨偏移错误。尚未逆向cooked hull/contact offsets，不能由此宣称全部effort都来自墙接触。

不改原场景/碰撞体/ACM/80Nm；检查绕杯面法向腕姿候选，原点与法向不动。nominal02前三链/1330腕部节点无墙重叠仍不等于物理修复；BUG017保持OPEN。

BUG017 latest：diagnostic02再现Y15自动保护 left86.958/right52.123Nm；同一步leftJ2峰86.997Nm且link7-wall140.242N，X16已有309.658N；原保护有效/整件完成0。持件记录已获得，不再写“零接触数据”。

采集工程负结果：nominal01 stdout/rosout穿插，分析器正确拒绝；nominal02用独立不覆盖文件复验通过，旧坏记录不删除/不修饰。BUG018网络恢复、fresh资产溯源成功，不抹startup01失败。

## 2026-10-06 follow-up — 网络恢复，原场景第二次启动

原S3直连/代理HEAD恢复HTTP200，runtime d35cc0c正常push成功；保留startup01失败。相同官方资产/原参数的startup02重新运行，held live handles与首件物理诊断仍待验证，尚未发controller命令。BUG017根因未解决，BUG018外部连接暂时恢复不抹掉负结果；模型/物理/门限/YAML不变。本段更新此前“final”失败checkpoint，不叫新物理PASS。

## 2026-10-06 final — BUG-018 官方FR3资产/GitHub连接失败（外部状态）

2026-10-06，OPEN。原资产URL的stat失败，headless traceback在_asset_url找不到FR3；直连/127.0.0.1:7897代理HTTPS均unexpected EOF，GitHub SSH banner超时。SDK仅查cache仍ERROR_CONNECTION，本地发现fr3缓存不等于来源/物理模型已确认。hold诊断有效句柄与物理样本未得到，不把startup失败归为新控制算法失败。SimulationApp failure.json与exit0矛盾已留证，不能仅靠process0验收。BUG017仍OPEN，原门限不变。

## 2026-10-06 — BUG-017仍OPEN

先补持件窗口的同一步接触/DOF完整记录；旧release-only日志无法观测Y15。原80Nm保护不改，未宣称闭环内力根因或碰撞排除。启动valid句柄/路径/DOF检查不通过时不发机器人命令。

## BUG-017 follow-up — 双CLOSED下Y15 raw effort超限，根因仍OPEN

2026-10-05，e0477ab新鲜原场景复测：X16/Y14段完成，Y15 left86.975/right32.984Nm触发原80Nm保护，两个杯都CLOSED；本次触发项是raw关节effort而非吸盘OPEN。实测换角色修正使本次能进入Y，但不同IK构型的两次运行不能证明单一修正的因果。

释放后静态FCL PASS/较低effort不是失败步无碰撞或闭环内力根因证明。最后稀疏双CLOSED样本Y离原终点还有17.354mm，不能声称终点侧墙越程。持件同物理步contacts/关节状态缺失（原release logger未激活），需要区分机器人/工具接触、轨迹跟踪误差及闭环约束载荷。保留失败，不提高80Nm、不放宽碰撞/几何门限、不改旧场景；OPEN。

## BUG-017 — 新rear+side协议进入Y压紧时互锁停止

Date: 2026-10-05; Task: TASK01; Status: OPEN.
Evidence: ff20ac3 Cube01 X16/16 dualCLOSED/deep0.286mm，主从换角后controller1/未完成Y首段/双OPEN。旧guard不输出触发项，不能将failure直接归因于接触力、吸附失效或物理不可行。
Candidate issue: X末左臂joint tracking残差0.551deg，Y原从命令终点继续可能再次顶墙。e0477ab改同一实测起点/current FCL与Y重算、补具体raw torque/state诊断；fresh replay进行中，还不是RESOLVED。
No geometry/ACM/gate relaxation; no calibrated contact force or force controller.

## 2026-10-05 — 新协议覆盖与仍存风险

BUG-009：用户已将“前四双吸附”更新为“前三双吸附、后两精准单推”。新独立节点已实现前三rear+side CLOSED主从换角，不恢复第四侧接触；名义FR3链PASS，但新物理过程未完成，不能标协议覆盖已验收。

新探针暴露的软件问题：只复制URDF/SRDF使本地IK未实例化（探针已改读当前MoveIt运动学参数）；独立时间缩放使相对TCP超原门限、Cartesian候选跳支（安全拒绝，改共同位移网格）；相同窄joint seed未覆盖首件连续构型（非物理不可行结论）。先前负日志保留。

双D6闭环下实际几何/effort/释放残留未验证；BUG-016间歇回带、未校准wrench/动态时间通道、MoveIt关闭-11仍OPEN。零命令FCL/一次旧5/5不能将这些标RESOLVED。

## 2026-10-04 final — 完整一次通过，保留未覆盖缺陷

普通 `empty_rrt_full_01` 五件实际 PASS / controller 0 / HOME；此前正常成功退出并未失效。本轮普通 Cartesian 空载退出均通过，因此 RRT 备用只有无命令失败姿态重放覆盖，没有实际备用执行证明。构型敏感的旧退出失败保留为工程健壮性风险，不能标为完全 RESOLVED。

BUG-016 仍 OPEN / intermittent：本轮 Cube02 最终 deep gap=0.800 mm，原 5.138 mm 回带未复现。第一、二件同一步窗口 2,870 条有效记录；Cube02 侧压末至 clearance 末 X 变化约 -0.0637 mm。退出中工具仍有 X 运动，Cube 未大幅回带；不能宣称“消除了工具 X 运动”或隔离了根因。普通 OPEN phase 至多 1 step，是异步阶段标签，不是独立静止释放观察。

重放 01 的已有对象严格逐字段恢复比较失败仍未隔离；重放 02 只验证原本不存在的 6 个对象同步 REMOVE + 查询不存在。首轮左候选拒绝详细子原因记录不足，不能仅由后来更换 goal constraint 检查断言唯一因果。恢复失败仍阻止任何机器人执行。

BUG-004 MoveIt teardown -11 再现，joint bridge 关闭 1；控制器完成 0 独立有效，不等于所有进程生命周期正常。原材质/质量、动态测量与 D004 接触差异待审查，不由本次几何 PASS 消除。

## 2026-10-04 — New replay guard/restore validation boundaries

Manualaggregate-angleendpointguard differedfromoriginalMoveItposegoalconstraints; replacedbycheckingconstructedactualrequest, nobenchmarktolerancechange. Replay02PASS/norobotcommands. Replay01strictbitwisecomparisonofrestoredexistingobjectsFAILremainsunexplained; absent-IDsyncREMOVEverifiedinfreshreplay02, do notclaimbothcasesresolved. Runtimecallerrestorefailureblockscommand. ActualRRTmotionnotyetverified; originalBUG016releasebackdragstillOPEN.

## 2026-10-04 — Empty-retreat configuration-sensitive recurrence

OPEN; currentCube02 Cartesianfraction1butFK752–967mm, localIKfails118/151. Actualcommanddelta<0.001rad; historicalCube02passesdifferinredundantconfiguration. SamecontrollersCube01retreatPASS, so notallretreatsbroken. RRTbackupisnotyetvalidated; genuinecollision/boundsremainrejects. PriorBUG016releasebackdragstillOPEN/notreached. Evidence measured_side_full_01/raw/controller.log, analysis.json. No gate bypass.

## 2026-10-04 — Side approach command/measurement seed mismatch, patch not yet verified

Diagnostic02 abortsbeforeCube02release: SIDECOMPACTIONincludesactualcurrentCube butpusherholdseedisPUSHcommandend, gives0.783mm collisiont0onall8candidates. ExistingjointsettlegatedoesnotmeanCartesiancommand=physicalpose. Postabortstaticcupgap0.267mm isonlysupporting—notexactfailurestate—observation. Independentactualsideapproach nowusesmeasureddualstatewithoriginaljointdelta/bounds/graspchecksandcurrentCubeFCL; noexemption. Physicalproofpending. BUG016originalreleasereturnremainsOPEN, notsolvedbyfirstcubediagnosticPASS.

## 2026-10-04 — Release diagnostics do not yet establish cause

BUG-016 remainsOPEN. Firstcube not reproducing priorsecondcube failure: holdX0.028mm,clearanceX0mm. NeedCube02 data before attributingdrift torelease/servo/trajectory. Diagnostic01 BRANCH_SIGN source lookup failurefixedonly inprobeconfiguration afterpreservingfailure; no controller ran. SimulationApp.close returned0 despiteexception, therefore failure.json/errorlogs—notexit0alone—mustgovernrunstatus.

## BUG-016 follow-up — Instrument before choosing a remedy

2026-10-04; OPEN. Added independentrelease/clearance tags and optional3s stationarypostreleasehold toseparateconstraint/contact responsefromwithdrawal trajectory. Same-stepPhysXcube/tools/collisionreadoutonlywithinwindow; asyncphasearrivalnotahardtimestampcontract, collision telemetryexcludesD6suction. No rootcause/PASS claim untilactualevidence; no physics/gate bypass.

## BUG-016 — Cube02 loses deep-wall seating around rear suction release

2026-10-04; TASK01; OPEN_PHYSICAL_RELEASE_WINDOW. New normal-feed XYZ variant passes original attachment gates and deep push seating0.488mm. After sidewall reached, first bothOPEN sim689.933s x1.099789; bysim691.133s x1.094862, finaldeep5.138mm>3.000mm, cell5.138mm; yaw0.000120deg. Controllerexit1, completedonlybatch1; Cube03–05notadvanced. NegativeX drift/temporary2mmheight excursion occur in release/clearance window, but sparse cube/gripper records alone do not prove cup-contact/constraint-release/tracking causality. No scene/contact/physics/gate change. Need same-step tool/contact/action-phase diagnosis then user-approved release/withdrawal fix, not relaxedgates. Evidence `preclose_xyz_full_01/analysis.json`, `release_drift.json`, raw retained; report TASK01_PRECLOSE_XYZ.

## BUG-015 follow-up — Bounded XYZ physically passes once, not global reliability

ApprovedD016/independent variant: Cube02X2.012→0.606mm, Z1.589→0.451mm, gapdelta0.879→0.275mm aftertwo1mm-boundedmicrocorrections; originalgatepassesbeforegrasp. StaticmeasuredFK tracksIsaac within0.056mm maxnorm, whilecommandtrackingnorm reaches2.806mm. Supports tracking-residual diagnosis at these holds, not complete model/time calibration. Preclose scoped workaround verified; wholeprocesslaterfails BUG-016, keep earlierfailures and no stablefullfive claim.

## 2026-10-04 — BUG-015 approved XYZ repair, verification pending

User approved pre-suction XYZ residual correction with unchanged gates. Independent variant now corrects all translation components in one total1mm move; diagnostics compare command-FK/measured-FK/Isaac before correction. Initial mathematical checks PASS, but no claim tracking/model origin identified or full flow repaired before physical evidence. Previous failed run retained; material/contact/measurement/teardown issues remain independent.

## BUG-015 — Pre-close Y correction does not resolve actual X correspondence error

- Date2026-10-03; TASK01; OPEN_DIAGNOSED_GATE_FAILURE.
- Normal current-variant five-Cube run completesCube01, then Cube02preclose fails after3checks/controllerexit1 before suction. InitialX3.027mm; finalX3.150mm>original2.500mm, despite Ygapdelta2.230→0.427→0.001mm. Lateststationary published left/rightTCPx difference3.149754mm supports the gate failure; snapshots nonsynchronous, not motion-time metrology.
- Code computes max(Cube-leftX,Cube-rightX,left-rightX). Current fine correction accumulates only Y execution residual, repeatedly nominalX/Z does not establish actualXYZ convergence. Tracking/model/metrology root cause not yet isolated; do not claim geometry impossible or force control necessary.
- No original threshold/model/contact/control changed; Cube02notgrasped, Cube03–05notcommanded, all test processes stopped. Report/metadata: TASK01_PRECISION_FULL_FIVE_REGRESSION, precision_full_five_01. Discuss read-onlyFK-vs-Isaac diagnosis and bounded ungraspedXYZ correction scope before modifying runtime; material/D004/freeze remain pending. BUG-004teardown-11 also repeats independently.

## 2026-10-03 — Normal-feed test readiness guard

Existing sparse probe was intentionally limited to preplaced3/4 and cancels batch1. New zero-preplaced mode must retain automatic initial feed and wait for actual first ARRIVED, not all([]). Added engineering test-mode guard/unit coverage; this is not a robot control defect or a scene repair. Earlier physical/model/force/teardown issues remain open; full normal-feed variant result pending.

## 2026-10-03 — Empty retreat WORKAROUND validated narrowly

Independent approved precision variant now passes one isolated fifth and one actual fourth→fifth continuation, using measured starts with releasedcurrentCube strictFCL. Final ordinary pathsmax0.002mm printed deviation; local-seed fallbacklong replaypasses withoutcommands. This is a verified narrow engineering workaround, not proof all random IKbranches/repeatedtrials work; fallbackphysicallynottriggered. OlderfourthdriftFAIL and fifthIKabortretained. BUG-004 MoveItteardown-11 repeats bothnewphysicalruns; actual0.5/0.5 versusdocument0.90/0.75, hiddenmass and D004contacttopology remainopen. BUG-006 rotation is already fixed for Task27 by prior Gf.Transform patch; historical Task26 branch remains untouched. USD motion-time synchronization/metrology still needs review. Report TASK01_EMPTY_RETREAT_REPAIR.

## 2026-10-03 — Cube05 empty retreat IK branch defect follow-up

Status: OPEN / engineering patch built, not physically verified. Prior Cube04/05 slow run safely rejects Cube05 retreat at 289–450 mm FK deviation despite fraction=1. New independent precision variant uses actual measured start state, then bounded seeded local IK if ordinary candidates fail; released current Cube included in strict FCL. No collision exemptions; real starting collision will stop, not be hidden. Report: TASK01_EMPTY_RETREAT_REPAIR.md. Cube04 drift/model/force/teardown issues remain separate and open.

Follow-up: isolated fifth actual full physical PASS with measured-start ordinary retreat (0.002/0.001mm FK deviations) and currentCube FCL. Long seeded fallback passes separate read-only replay. No failing-state exact A/B replay or repeated physical proof yet; Cube04→05 continuation pending. BUG-004 teardown -11 repeats; no claim of clean MoveIt lifecycle.

## BUG-014 — Fifth empty retreat can switch to a large off-line IK branch
- Date: 2026-10-03; TASK01; OPEN_ENGINEERING_ROBUSTNESS.
- In final Cube04→05 test, fourth passes and fifth carries/drops, but actual PREPLANNED_COMMON_RETREAT left trajectories show 289.3–450.1 mm FK deviation from the requested line. Original 5-mm guard correctly refuses execution; controller opens both cups and exits 1. No collision/line threshold widened. Candidate preflight alone does not ensure actual later replanning remains on the same branch.
- Evidence: `_03/raw/controller.log`, analysis/metadata. This is after Cube05 release, not Cube04 side-rod collision. Need inspect measured start state/IK branch and safe empty-arm exit candidates before claiming continuous reliable execution; do not enable arbitrary unsafe Cartesian fraction-only acceptance.

## BUG-013 follow-up — one low-speed pass, not resolved reliability
- `_03` fourth passes 0.227-mm neighbor gate; `_02` remains failure at 1.827 mm. Different random IK/RRT branches and speed prevent causal attribution to slowdown alone. Keep repeatability risk OPEN; no new force/lateral-feedback controller authorized or silently added.

## BUG-013 — Cube04 pure single-arm insertion drifts despite precise initial placement
- Date: 2026-10-03; TASK01; OPEN_PHYSICAL_VALIDATION.
- First variant test starts with Y error 0.046 mm yet ends at 1.827-mm neighbor gap (> unchanged 1.5 mm), safe stop and no Cube05. Sparse physical insertion Y span about 1.089 mm, yaw up to 0.210 deg. This shows initial precision alone does not guarantee tracking, not proof of physical impossibility.
- Original initial/pre-close/final gates and model preserved. Low-speed final-binary repeat pending. Any online Y feedback, rear+side restoration or force controller beyond the approved Cube05-like method needs explicit direction, not hidden compensation.

## 2026-10-03 — Cube04 variant validation checkpoint
- New test-runner callback argument mismatch fixed before any robot control. Preserve negative startup log; not an inherited scene failure. New Cube04 protocol physical validation pending, cannot mark BUG-009 globally resolved: first three cooperative rear+side protocol still unmet.
- Cube04 original final <=1.5-mm neighbor gap retained; precision target can still fail through physical tracking/yaw drift. Stop on real failure instead of enabling side trim or widening acceptance. Force/time/model/MoveIt teardown issues remain open.

## 2026-10-03 — BUG-009 fixed-center roll alternative checked
Status: OPEN
Evidence: Follow-up fixed-center/normal roll sweep has 24/24 rod-neighbor intersections. This eliminates the tested discrete rotation-only alternatives, not every continuous/contact-order strategy. No offset/edge grasp, model change or collision bypass adopted.

## 2026-10-03 — BUG-009 physical contact-accessibility follow-up
Status: OPEN / CURRENT_SIDE_POSE_GEOMETRY_BLOCKER
Evidence: Exact existing tool OBBs at Cube04 +Y face center intersect the measured seated Cube03. Lateral support minimum SAT axis overlap=33.524 mm; vertical support also intersects. This is not PhysX depth and not an exhaustive arbitrary-roll search. Old full-five demo still does not use rear+side simultaneous suction constraint. Tool/contact sequence changes need explicit review; no ACM expansion, Cube ignore, geometry change or edge-cup shortcut implemented.
Run: results/20261003_TASK01_fixture_protocol_clearance/.

## BUG-011 — Real-FR3 hold reactions alternate and velocity readout differs from pose derivative
Date: 2026-10-03
Task: TASK01
Status: OPEN_METROLOGY / ANALYZER_ALIASING_FIXED
Evidence: 238 full-rate observed hold samples: net support mean error 0.000370 N but instantaneous RMS 0.494278 N; mean Cube-center moment residual 0.014902 Nm. Tensor speed RMS 0.012773 m/s while position-FD RMS 0.000505 m/s, discrepancy max 0.013163 m/s. Root cause of physical/API velocity behavior unconfirmed; cannot call force calibration PASS from mean only.
Diagnostic correction: Decimation by six captured one parity of alternating reactions and created a false mean lateral bias. Explicit hold now uses every physics step, reports mean and instantaneous errors separately; alternating-sequence regression PASS. No physics/solver/filter/gate changed.
Run: results/20261003_TASK01_fr3_static_payload_v2/analysis.json.

## BUG-012 — Declared high-friction material deleted before task objects build
Date: 2026-10-03
Task: TASK01
Status: OPEN_MODEL_REVIEW
Evidence: _make_material creates material below /World/Task27; _build_objects subsequently removes that root without rebuilding material. Startup USD physics/all-purpose bindings unresolved; actual Cube shape backend properties are static/dynamic friction 0.5/0.5 and restitution 0, despite declared 0.90/0.75/0. Cube actual masses are 0.800000012 kg.
Impact: Prior demos must not be interpreted as tests with the declared high-friction material. Repairing lifecycle changes actual physics; approve effective material version and rerun before freeze. Pairwise effective combination rule also remains open.
Run: results/20261003_TASK01_mass_material_audit_v3/summary.json; earlier partial path/purpose-only audits preserved.

## 2026-10-03 — BUG-010 controlled replacement verified
Status: RESOLVED_TEST_MECHANISM_ONLY
Evidence: Optional task-thread hold leaves executor running, resumes without stale state, and completes Cube01/HOME with controller exit 0. It does not resolve the new force/velocity issue BUG-011 or approve benchmark/model values.

## 2026-10-03 — BUG-004 teardown recurrence
Status: OPEN
Evidence: Full-five/controlled-hold shared MoveIt launch later interrupted: move_group exit -11, dual_joint_state_bridge exit 1. Controller manipulation and Isaac complete/stop separately; do not call launch teardown clean.

## 2026-10-03 — BUG-008 repaired inherited full-flow verification
Status: RESOLVED_FOR_LEGACY_DEMO / NOT_PROTOCOL_OR_FREEZE_PROOF
Evidence: d80b6b6 unit/build PASS and fresh normal-feed physical batches 1–5 PASS, exit 0 and both arms HOME. Original 0.300 mm measured pre-close gate, three attempts and full FCL retained. This is one unseeded full run, not broad reliability evidence; D004 protocol remains BUG-009.

## BUG-010 — Whole-process pause invalidates ROS current-state request
Date: 2026-10-03
Task: TASK01
Status: RESOLVED_TEST_MECHANISM / NEGATIVE_EVIDENCE_RETAINED
Symptom: Experimental 7-s SIGSTOP after lift also suspends the ROS executor. An in-flight 2-s state request returns stale data after SIGCONT; controller safely opens both and exits 1.
Resolution: Do not use process pause as supported metrology method. Use explicit default-zero task-thread hold leaving executor active (legacy 76408c8); controlled replacement validation pending. Ordinary five-Cube run succeeded without this pause.
Evidence: results/20261003_TASK01_fr3_static_payload/{metadata,analysis}.json and raw controller/hold_driver logs.

## 2026-10-03 — BUG-006 Task27-only fix
Status: FIXED_TASK27_QUATERNION / TIMING_MIGRATION_PENDING
Evidence: d80b6b6 removes Cube scale before extracting quaternion in Task27 only; same-step PhysX final yaw is now preserved rather than compressed by scale. Prior calibration distinguishes orientation extraction from USD lag. Task26 default untouched; legacy wall timestamp / frame lag BUG-002/005 remain open.

## 2026-10-03 — BUG-008 bounded-correction checkpoint
Status: FIX_IMPLEMENTED / FULL_FLOW_VALIDATION_PENDING
Evidence: d80b6b6 in legacy task01-runtime-fixes replaces 0.650 mm minimum correction with measured residual and precise seeded FK solving. Unit/build PASS. Fresh Cube01 0.447 -> 0.001 mm; Cube02 0.287 mm passes original 0.300 mm gate. Do not claim full five-Cube fix until physical completion.

## BUG-009 — Legacy first-four push contact protocol differs from D004
Date: 2026-10-03
Task: TASK01
Status: OPEN
Symptom: Legacy deep push holds helper at a parked pose, rather than side-face suction constraint. Inner cubes later get rear-arm-only lateral trim, not the approved side-primary/rear-hold role swap.
Evidence: task26_truck_box_push_in.cpp executePushWithSupervision call and isInnerReferenceTask block under TASK27_FIVE_CUBE.
Impact: Legacy full five-Cube demo PASS cannot establish requested cooperative fixture behavior or be relabeled as paper dual-arm insertion evidence.
Resolution needed: Verify contact accessibility and implement/test the distinct fixture protocol without geometry/gate relaxation; stop for user direction if physical constraints require benchmark change.

Append-only unresolved/resolved bug register.

At repository initialization, no bugs were recorded.

## BUG-001 — Contact-wrench telemetry gap
Date: 2026-09-30
Task: TASK00
Status: OPEN
Symptom: The observed legacy Task27 ROS graph has joint effort but no contact-wrench message for either suction/contact interface.
Reproduction: With the legacy bridge active, run ros2 topic list -t and inspect /task27/{left,right}/measured_joint_forces.
Suspected cause: Current legacy bridge publishes articulation joint forces, not a contact sensor wrench.
Evidence: reports/TASK00_ENVIRONMENT.md and legacy task26_truck_box_bridge.py.
Workaround: None. Do not treat joint effort as end-effector contact wrench.
Resolution: Define a sensor/estimator and calibrated frame contract in TASK01/TASK02 before P2/P3 force benchmarks.
Related commit/run: TASK00 environment audit.

## BUG-002 — Benchmark time-base ambiguity
Date: 2026-09-30
Task: TASK00
Status: OPEN
Symptom: One live snapshot had /clock at approximately 1787 s while TCP/Cube pose headers were near 1790752970 s.
Reproduction: During a fresh legacy launch, sample /clock and both stamped pose topics together, and query use_sim_time on all consumers.
Suspected cause: Mixed simulation-time and wall-time stamping; not yet proven.
Evidence: reports/TASK00_ENVIRONMENT.md.
Workaround: None accepted for scientific metrics.
Resolution: Freeze and validate one timestamp policy before synchronized benchmark logging.
Related commit/run: TASK00 environment audit.

## BUG-003 — Carriage reference-frame contract absent
Date: 2026-09-30
Task: TASK00
Status: OPEN
Symptom: Legacy USD TruckBox prim and rail-state messages exist, but no explicit carriage/entrance TF was observed.
Reproduction: Inspect the legacy Task27 scene/bridge and its ROS graph.
Suspected cause: The existing controller uses known scene geometry rather than a public frame contract.
Evidence: reports/TASK00_ENVIRONMENT.md.
Workaround: None for a transferable common benchmark.
Resolution: Define carriage and entrance frames in TASK01 and expose them through the TASK02 adapter.
Related commit/run: TASK00 environment audit.

## BUG-004 — MoveIt shutdown segmentation fault after completed Task01 probes
Date: 2026-09-30
Task: TASK01
Status: OPEN
Symptom: After both Cube 05 physical runs had exited normally and the MoveIt launch was interrupted with Ctrl-C, `move_group` exited with code -11 during `rclcpp::CallbackGroup` destruction.
Reproduction: Launch `moveit_dual_side_suction.launch.py use_rviz:=false`, run the Task01 probe, then send Ctrl-C to launch. Reproduced after every one of the four additional completed runs on 2026-10-02; `move_group` exit code -11 and stack ends in `rclcpp::CallbackGroup::~CallbackGroup()`.
Suspected cause: Shutdown lifetime/race in the installed MoveIt/ROS stack; unconfirmed.
Evidence: Launch output from 2026-09-30 and 2026-10-02; all six Task27 node logs contain `batch 5 PASS` before shutdown. The controller process exited 0 in each new trial.
Workaround: None required for completed trajectory execution, but do not classify launch teardown as clean.
Resolution: Isolate the MoveIt/ROS shutdown lifetime issue under a standalone shutdown check before declaring the runtime harness reliable; do not change the manipulation planner to mask this teardown defect.
Related commit/run: TASK01 center right/left physical probes.

## BUG-005 — Motion-time PhysX and USD Cube pose sources are not synchronized
Date: 2026-10-02
Task: TASK01
Status: OPEN
Symptom: During Cube 05 pushing, a read-only same-loop comparison of the Isaac `RigidPrim.get_world_pose()` result and the USD transform used by the legacy Bridge's `/task27/cube_poses` sometimes differed by 0.4–2.8 mm in position. After Cube settle, the positional difference printed as 0.000 mm. Orientation-source difference in observed samples was around 0.02–0.15 deg.
Reproduction: Run `platforms/isaac_ros2/probes/task01_center_headless.py` with the bundled Humble ROS environment, execute the Cube 05 probe, and inspect `[TASK01 pose-source-check]` lines during motion and after settle.
Suspected cause: A physics/USD update or read timing mismatch is possible but not established. This instrumentation alone cannot distinguish timing from transform or caching issues.
Evidence: Headless stdout from left/right repeat runs on 2026-10-02; e.g. left 3 had a 2.840 mm transient sample during push, then 0.000 mm after settle. Final Bridge pose samples and Task27 ROS logs are recorded in `reports/TASK01_CENTER_ARM_SYMMETRY.md`.
Workaround: Use only settled final Bridge pose for current exploratory static placement metrics; do not treat instantaneous Bridge pose as a synchronized contact/velocity measurement.
Resolution: Define one timestamped physics pose pipeline, compare against USD and ROS with a common simulation time, then freeze the TASK01/TASK02 measurement contract.
Related commit/run: TASK01 center repeatability probes.

## 2026-10-03 — BUG-002 follow-up: new channel workaround only
Status: WORKAROUND for TASK01 probe; legacy interface remains OPEN
Evidence: Legacy `_publish()` stamps poses with `node.get_clock().now()` in wall-time while the scene publishes simulation `/clock`. New `PhysicsObjectSampler` reads Isaac core simulation time in a completed physics step. External ROS calibration verifies that new poses, snapshots and `/clock` share the simulation time domain.
Boundary: `/task01/physics/cube_poses` is separate from `/task27/cube_poses`. TCP, effort and legacy consumers have not been migrated; this is not a global resolution or a frozen synchronization contract.
Related report: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md

## 2026-10-03 — BUG-004 follow-up: not reproduced on today's interrupt paths
Status: OPEN
Observation: One idle MoveIt startup interrupted before robot execution and one launch interrupted after a successful 215-s Cube 05 task both exited move_group with SIGINT code -2, not -11. The joint-state bridge also showed KeyboardInterrupt. This differs from the prior repeatable callback-group teardown stack, but no shutdown fix was implemented and these interrupt paths are not proof of resolution.
Related run: results/20261003_TASK01_fixture_physics_channel/

## 2026-10-03 — BUG-005 follow-up: frame-update lag reproduced
Status: WORKAROUND for new PhysX channel; legacy USD motion measurement remains OPEN
Confirmed cause: At 0.2 m/s and 60 Hz physics, legacy/post-step callbacks see stale USD position up to 6.667 mm with 30 Hz application frames or 10.000 mm with 20 Hz frames. After application update, positional difference is zero. The independent known-motion ROS probe directly sampling PhysX passed at both frame rates.
Workaround: New read-only live-physics snapshot, one simulation stamp/step per sample, rejecting USD fallback. Do not compute dynamic contact/velocity metrics from legacy USD callback data.
Related report/runs: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md; results/20261003_TASK01_physics_ros_zero_damping_{30hz,20hz}/

## BUG-006 — Scaled USD matrix corrupts legacy Cube orientation
Date: 2026-10-03
Task: TASK01
Status: WORKAROUND for new physics measurement; legacy Bridge remains OPEN
Symptom: Legacy `_pose()` extracts a quaternion directly from the Cube world transform containing scale=(0.12,0.12,0.12), then normalizes it. This underestimates the actual angle; normalization does not remove scale from the rotation matrix.
Reproduction: Run task01_pose_timing_probe.py; inspect raw_usd_rotation_error_deg versus scale_removed_usd_rotation_error_deg after app.update().
Confirmed cause: ExtractRotationQuat requires a rotation matrix; applying it before removing scaling violates the OpenUSD API contract. In the corrected zero-damping calibration, raw extraction error reaches 27.464 deg while scale-removed extraction differs from PhysX by at most 0.000154 deg after app update.
Workaround: Use live PhysX quaternion in the new measurement channel. Do not reinterpret old Bridge yaw as physical 6D Ground Truth. Correct only the historical report's validity statement; retain original numbers.
Resolution needed: Migrate the final common adapter's pose consumers with an explicit tested frame/time contract. This iteration does not modify legacy control code.
Related report: reports/TASK01_PHYSICS_POSE_MEASUREMENT.md

## 2026-10-03 — BUG-001 follow-up: collision channel calibrated, suction gap remains
Status: PARTIAL WORKAROUND; FR3 TCP contact-wrench contract still OPEN
Evidence: Independent known-load normal/friction/torque calibration passes at 60/120 Hz. A dual-suction-held 0.8 kg object produces 0 N collision telemetry: D6 reaction is excluded. Independent articulated-mount reaction captures the known suction load and identifies the raw link-axis/link-origin convention, but is not a FR3 compensation calibration.
Next: Validate the actual link8 branch gravity/inertia compensation, action/reaction sign and moment shift to TCP before publishing a contact estimator. Do not treat old JointState.effort, new collision wrench, or uncorrected incoming joint wrench as interchangeable.
Related report: reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md

## BUG-007 — Hidden tool-body mass / contact-force compensation ambiguity
Date: 2026-10-03
Task: TASK01
Status: OPEN (model audit finding; no model change authorized)
Symptom: Disabling old hand/finger visual and collision does not remove their rigid-body masses. Actual articulation topology has 13 links, with about 1.946277 kg in the link8+hand+fingers+hand_tcp branch; static support is about 19.093 N before grasping any Cube.
Evidence: Full-scene readout topology.json; independent mount calibration proves that incoming reactions include downstream gravitational load. Actual link8 raw reactions also show roughly this support after world-frame rotation.
Risk: Calling raw incoming force a suction contact wrench gives biased force/internal-stress metrics. Invisible bodies also influence the physical dynamics and must be included in the benchmark model description.
Resolution needed: Audit/record model masses and inertias; calibrate compensation. Any removal/replacement of masses changes the benchmark physics and requires explicit user review; not done here.
Related report: reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md

Template:
```text
## BUG-XXX
Date:
Task:
Status: OPEN/WORKAROUND/RESOLVED
Symptom:
Reproduction:
Suspected cause:
Evidence:
Workaround:
Resolution:
Related commit/run:
```

## 2026-10-03 — BUG-001/007 reference-convention correction
Status: OPEN / independently calibrated channel only
Correction: Earlier follow-up's link-axis/link-origin identification is INVALIDATED due to scaled authored COM/anchors. Final unscaled nine-hypothesis test identifies incoming joint axes/about joint anchor (3.436e-6 N / 4.430e-7 Nm errors), with physics COM checked. Raw prior PASS retained; metadata explicitly invalidated for reference inference. Do not transform FR3 raw incoming by link pose alone or ignore the moment reference.
BUG-007 qualification: 1.946277 kg and 19.092980 N are topology/analytic facts. The temporary about-19.10 N link-pose rotation is only an uncalibrated magnitude observation, not FR3 joint mapping proof. Added authored-frame audit failed on asset-root lookup; mapping/compensation stay unverified.
Evidence: results/20261003_TASK01_mount_joint_reference_final/ and reports/TASK01_FORCE_MEASUREMENT_FEASIBILITY.md.

## BUG-008 — Pre-close minimum correction overshoots symmetry gate
Date: 2026-10-03
Task: TASK01
Status: OPEN
Symptom: Normal-feed run places Cube 01 then fails Cube 02 before suction. Gap difference 0.968 -> 0.315 -> 0.339 mm never meets original 0.300 mm gate; controller exits 1, no later cube commanded.
Evidence-supported cause: Legacy effective_step clamps nonzero correction to at least 0.650 mm. Near the gate it overshoots the acceptable interval. Last x/z mismatches are within original 2.5 mm gate and not the failure. Final independent physics TCP/body pose confirms 0.338941 mm difference.
Evidence: results/20261003_TASK01_full_five_physical_v2/raw/controller.log; reports/TASK01_FULL_FIXTURE_CONTACT_PROBE.md.
Resolution needed: Fix quantization/deadband with endpoint FK/tracking feedback, retain the 0.300 mm geometry gate and three-attempt stop. Rerun five normal-feed cubes; no ACM/physics change. Not fixed in this metrology scope.

## 2026-10-03 — BUG-004/006 full-flow reproduction
BUG-004: move_group again exits -11 at rclcpp::CallbackGroup destruction after stopping the incomplete run. Execution and shutdown failures are separate; no clean-lifecycle claim.
BUG-006: Cube 01 final physical yaw -1.095465 deg versus legacy scaled-USD near-zero yaw. Oriented nearest-wall gap differs from center/axis-aligned gap; no physical orientation PASS from old telemetry.
Evidence: results/20261003_TASK01_full_five_physical_v2/raw/{controller,moveit}.log and physics_contact_samples.jsonl; report above.
