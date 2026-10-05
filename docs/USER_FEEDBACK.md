# USER_FEEDBACK

## 2026-10-05 — 更新推入接触分工（覆盖旧“前四双吸附”的该部分）

实施记录边界：用户授权新流程的软件起点/同步/FCL修正与测试；发现闭环力学问题仍须保留负结果，不以放宽门限或修改现有场景替代诊断。

- 用户明确批准：“那就按照新的流程来，前三个cube双臂推入，后面两个cube强调推入前位置的精准”。前三件 rear+side 同时吸附，rear 主推到深墙、side 约束；到墙后互换主从做侧压。第四、第五复用精准暂放/单 rear 吸附插入，不恢复第四件侧吸压紧。
- 这授权新工程执行分支，不授权改变原场景、教师确认 L 型工具、质量/摩擦、ACM、验收门限或冻结36个未决值；也不等于批准力控/论文算法实现。旧5/5证据必须与新协议分开记录。

## 2026-10-04 final — 按“以前退出没问题”核对并交付本轮结果

用户最新要求“那你继续，我记得之前退出都是没问题的啊”。保留此前退出 PASS，实际比较冗余构型而非宣布全面回归；复用已允许的空载 RRT 备用并先验证后执行。向用户明确本轮 Isaac 在其本机后台 headless 跑，不是远程或 GUI。

本轮普通五件物理运行最终全部 PASS / 控制器 0 / 双臂 HOME；RRT 备用未触发、历史释放漂移未归因、一次成功不等于稳定版或基准冻结，已在交付前说明。自有运行进程停止并上传过程/负证据。没有从“继续”推断场景/材质/ACM/门限/论文方法改变的权限，也未开展 TASK02。

## 2026-10-04 — Continue locally with explicit headless disclosure

User“那你继续”authorizescontinuingengineeringtests. ExplainedoldexitPASSandconfiguration-sensitivecurrentfailure, corrected100mmrailframeinreplay, announcednewnormalfeedtestexplicitlylocalheadless. NoGUIacceptanceor5/5claimfromreplay. Preservepartialfailures, pauseonlyifscientific/model/gateauthorityneeded; source/runtimebranchpushed.

## 2026-10-04 — Explain headless execution and verify previously working exits

UseraskswhereIsaacrunsbecauseGUIwasnotopened; confirmedlocal/home/ubuntu2004/isaacsim-4.5.0backgroundSimulationApp(headless=True), notremote/notsandbox/nothumanGUIacceptance. Userthenrequestscontinuationandrecallspreviousexitsworked. PreserveoldPASSwithscope, compareactualseedsandframeoffsets; don'tinventmodelregressionorcallpartialfivePASS. Continuein-scopedunloadedRRTreuse, reportmajorissuesandrecordGitHub. No inferredgeometry/contact/gateapproval.

## 2026-10-04 — No collision bypass for new diagnostic blockage

Continuation staysengineering-scoped: secondcube'snewcommand-seedcollisionisrecorded, notignored. ReuseactualseedandstrictFCL beforefurtherreleasevalidation; nouserapprovalinferredforACM/material/grasp/benchmarkchanges. Ordinaryrunhold0required; diagnosticfirstcubestabilitycannotbehandedoffasstablefivecube.

## 2026-10-04 — Continue scoped release-window diagnosis

Continuinguserapprovedrepair independently withfirsttwoobjectphysicaldiagnostics. Preserve originalscene/material/gripper/acceptance, do notinferpermissionforpaperforcecontrol/benchmarkfreeze. Publishin-progressandnegativeevidence; reportordinaryvalidation separatelyfromoptionaldiagnostichold. No user-action requested while safe diagnostic progress remains.

## 2026-10-04 — Continue after XYZ pass / release-gap failure

User“继续”authorizespreviouslyproposedrelease/withdrawalrepairwithunchangedscene/friction/gripper/gates. CarryforwardXYZcodeandhonestpartialoutcome, diagnosebeforeadjustment, re-testactualphysics andrecordGitHub. Noimplicitapprovalforbenchmarkfreeze/materialchange/paperforcecontrol.

## 2026-10-04 final — Approved XYZ change delivered with honest failure boundary

User's “好的，那就这么做” applied to one merged boundedXYZ correction only. Implemented/tested without changing model/physics/acceptance or loaded task. Physical Cube02preclose passes aftertwo corrections; ~0.079s totalplanning vs7.57s slowphysicalmoves, no extra correction forCube01. Full flow still failsCube02post-release deepgap5.138mm, so no stable/fullfive handoff. Stop before distinct release/contact-control redesign, save evidence for nextuserdirection; don't silently implement forcecontrol or widen gates. Allownedtestprocessesstopped, GitHubrecordspublished, TASK01notfrozen.

## 2026-10-04 — Explicit approval for pre-suction XYZ and efficiency policy

User asks what XYZ means, why prior runs passed, and overhead; then confirms “好的，那就这么做”. Explained that prior X/Z residuals existed below gates; latest onlyXfailed and random/configuration cause not proved. Approved one combined bounded XYZ micro trajectory only if needed, not three axis moves/full RRT, same3checkstop. Current implementation adds static FK/Isaac diagnostic and measured timing; no approval to change validated scene/material/gates or loaded/contact controller.

## 2026-10-03 — Test-only continuation ended at actual alignment failure

Completed remaining autonomous full-five regression rather than relying on preplacedfixturePASS. Currentvariant failsCube02pre-closeXgate, onlyCube01PASS; stoppedwithout suction/latercubes, no control/model/material/gate edits. User's hard-decision boundary respected: savefailure and proposedXYZdiagnosis/correction discussion plus unresolvedmodel/contact/numericalreview for tomorrow, not hidden compensation or benchmarkPASS. Raw and summarizedresults retained; ownedtestprocessesstopped.

## 2026-10-03 — Repeated autonomous-continuation request

User: “如果你可以自己继续就继续，如果需要我来做硬性决断，就停下来等我明天来”. One remaining safe engineering validation is full five-Cube regression of the current variant from normal feed, not another protocol/model redesign. Announced PRE-TASK scope before edits; do not silently change physics/contact/numeric gates or start paper methods to obtain a PASS. Record any remaining hard decision for tomorrow.

## 2026-10-03 — End-of-turn boundary respected

Autonomous engineering continuation completed real FK/FCL and isolated/continuous Cube04/05physicaltests, all finalcontrollers exit0. No new approval for numericfreeze, model/material/contactmethod changes was inferred. Test processes stopped and findings saved/pushed so user can review tomorrow; originalscene/protectedfolder/thresholds preserved. This does not erase earlier failures or claim TASK01finished.

## 2026-10-03 — Autonomy boundary for next repair

User: “如果你可以自己继续就继续，如果需要我来做硬性决断，就停下来等我明天来”. Continue safe engineering diagnosis, tests and records; do not infer permission to change physics/model/contact methods or freeze numeric benchmark values. Empty-retreat IK/start-state reliability is in scope. Material decisions will be recorded for tomorrow without requiring immediate response.

## 2026-10-03 — Final boundary for the approved fourth change
- Implemented exactly the approved contact split: fourth now precision-staged/single rear push, not helper side suction or post-seat trim; first three and old nodes retained. One fourth physical PASS and a fifth follow-on failure are recorded separately. No approval for additional online compensation, force control, scene editing or benchmark freeze inferred from this request.

## 2026-10-03 — Scope remains single-rear insertion, no hidden fallback
- No new user instruction authorizes restoring Cube04 side pressing or adding online lateral/force correction after a failed pure single-arm test. Preserve initial request and report negative outcomes explicitly; low-speed repetition is not permission to freeze the benchmark.

## 2026-10-03 — Cube04 should use Cube05 insertion
- User: “那第4块采取第5块的推入方式”. Explicitly authorizes this contact-protocol exception; no implied authorization for all Cubes or benchmark freeze.
- User previously insisted the validated scene must not change; may add things. Retain existing scene, tool, mass/material/geometry. Cube04 final neighbor acceptance remains distinct from Cube05 center acceptance.

## 2026-10-03 — Further continuation while recording
- User again asked to continue until TASK01 works and then said “继续”. Continued safe fixed-contact geometry alternatives and record upload. This remains persistence authority, not approval to change physical material, teacher-approved tool, contact protocol or benchmark gates.

## 2026-10-03 — Requested persistence completed to scientific review boundary
- Normal five-object inherited physical manipulation has actually passed, not just offline plans; controlled hold also completes. User-confirmed D004 is preserved as distinct requirement, not replaced by helper parking/solo trim. Face-center grasp requirement is not traded for edge/half-cup contact.
- New concrete geometry interference and actual-vs-declared material mismatch require user direction under repository rules. Ask before changing teacher-approved L tool/contact sequence or friction. No answer to model-review/numeric questions has arrived; keep them pending, never invent consent.
- All protected user files preserved; no automatic shutdown task or paper baseline has been started.

## 2026-10-03 — Model-review question pending
- Asked whether to retain near-unbreakable suction force/torque limits 1e6 and hidden hand/finger branch mass about 1.946 kg as a candidate, or revise then revalidate. No answer/numeric freeze is inferred at this checkpoint. Continue read-only/controlled metrology with unchanged physics while preserving D004 protocol distinction.

## 2026-10-03 — Persistence request
- User explicitly requested: “继续，直到task01调通，再汇报”. Continue safe in-scope repair and physical verification instead of routine partial handoff. Preserve scientific review/stop conditions; this does not authorize arbitrary numeric freeze or deviations from the approved contact protocol.

Persistent user decisions/feedback that must influence future work.

## 2026-09-29
- Keep detailed records and feedback during Codex work.
- Use a separate reproduction repository instead of mixing baselines into the palletizing repository.
- Use MuJoCo as an auxiliary force/contact platform where useful, but keep Isaac Sim as the final unified benchmark.

## 2026-09-30
- Advance tasks in repository order and persist process records to GitHub as work proceeds.
- MuJoCo is already installed in a .venv belonging to the existing force-control project; locate and reuse that environment for audits instead of assuming the system Python import result means MuJoCo is absent.
- Confirmed Task27 as the geometric starting point for TASK01 benchmark_v1; no approval was given to freeze every old numerical setting or acceptance threshold.
- Clarified Benchmark B: first four cubes use dual-arm suction with one arm pushing toward the deep wall and the other constraining lateral/yaw error, then swap push/hold roles for lateral pressing; Cube 05 must be aligned accurately at PRE_PUSH and pushed inward by one suction arm without second-arm Cube contact.
- Expected the fifth Cube's left/right single-arm insertion to be geometrically symmetric, and requested direct Isaac comparison without repeating the full process: place the first four Cubes at their intended final cells and test only Cube 05. Keep the two runs separate so feasibility is not mistaken for proof of equivalence.

## 2026-10-02
- User requested continuation of the same Cube 05 left/right experimental validation. This did not authorize freezing TASK01 or changing the benchmark geometry; repeated fresh-scene trials and evidence recording were kept within the existing probe scope.

## 2026-10-03
- User requested continuation. Advanced TASK01 measurement diagnosis within the existing Task27-derived draft rather than starting paper baselines before the freeze gate. No new numeric benchmark approval or permission to modify the protected reinforcement_stair-test directory was inferred.
- User approved continuing the proposed order: force-measurement feasibility/calibration, synchronized frames/time, then a full five-Cube nominal probe and benchmark parameter review. This is not permission to alter hidden-body masses, freeze success gates, skip TASK01, or start paper force controllers; the protected directory remains untouched.
