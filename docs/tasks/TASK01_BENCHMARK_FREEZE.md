# TASK01 — Freeze Benchmark V1

Status: IN_PROGRESS (candidate study; benchmark_v1 not yet reviewed or frozen)

## 2026-10-05 用户批准新3+2接触协议

Follow-up：新首件ff20ac3双吸X16段PASS/deep0.286mm，但Y起步互锁FAIL，整件未PASS；实测换角色起点e0477ab fresh replay进行中，原数值门限未改。BUG-017 OPEN，35 Python /4 C++ /build PASS；TASK01仍不能冻结。

前三件双吸附rear-primary X推入、side约束，到深墙不松吸盘换side-primary Y压紧/rear保持深墙；后两件精准暂放+单rear插入。独立节点ff20ac3、无执行前三完整FR3链PASS，首块新鲜普通供料物理运行中，不能借旧5/5宣称新流程通过。详见 `reports/TASK01_DUAL_SUCTION_FIXTURE.md` /D019。YAML还是原DRAFT/36nulls，模型/物理/门限未冻结；不启动TASK02/论文算法。

## Latest final engineering result (2026-10-04)

当前独立精准插入版源码 `df9c2c0` 在本机 Isaac headless 的普通供料五件实际完成：零预置、release hold=0、scale=5；controller 0 / 双臂最终 HOME / 双杯 OPEN。五件中心误差 1.983 / 0.807 / 0.723 / 1.319 / 0.481 mm，第四邻缝 0.347 mm，第五两侧缝 1.987 / 1.473 mm。18,498 条稀疏 PhysX 记录无完整性错误，3,212 条释放诊断。完整命令、源码/hash、原日志摘录和未解决问题见 `reports/TASK01_RELEASE_CLEARANCE.md` 及 `results/20261004_TASK01_empty_rrt_full_01/`。

新增有限空载 RRT 备用通过失败姿态四位小数无命令重放 / 1,277 次联合 FCL，但本轮普通 Cartesian 全通过，**备用未物理触发**。历史 Cube02 5.138 mm 释放回带本轮未复现、BUG-016 原因仍 OPEN；已有对象恢复严格比较及 MoveIt teardown -11 保留。该一次实际完整 PASS 取代下方“当前仍失败”的历史运行状态，不抹掉负结果，不是稳定性、GUI 验收或论文复现证明。

原场景、质量、有效摩擦、ACM、门限和 benchmark YAML 未改，D004 前三件协议/力与时间测量/数值审查仍待确认；36 nulls / DRAFT 保持，TASK01 不冻结，TASK02 TODO。

## Latest XYZ engineering result (2026-10-04)

User-approvedD016 combinedXYZ preclose implemented in independentvariant; build/C++/22Python/real RobotModel IK+FCL PASS. Actual normalfeed Cube02residuals X2.012→0.606mm/Z1.589→0.451mm/gapdelta0.879→0.275mm pass originalgate aftertwo total1mm-boundedmoves. Correctionplanning0.078621s/physicalexecution7.569621s(scale5); Cube01alreadyvalidskipscorrection. But full-five remainsFAIL: Cube02laterdeepgap0.488→5.138mm>original3mm aroundsidepress/rearsuctionrelease, controllerexit1/completed[1],noCube03–05commands. 7680physicalposes0errors, allownedprocessesstopped/teardown-11retained. `reports/TASK01_PRECLOSE_XYZ.md` contains PRE/POST/commands/hashes/results and BUG-016 scope boundary. No loadedcontrol/model/material/scene/ACM/gate/YAMLchanges;36nulls andD004/metrologyreviewstillpending, TASK02TODO. Do not reinterpretpreclosePASS as full-task or paper reproductionPASS.

## Latest normal-feed precision-variant regression (2026-10-03)

No preplacement, unchanged runtime/model/gates; actual five-object attempt fails safely at Cube02 before suction, controllerexit1 and onlybatch1PASS. FineYgapdelta reaches0.001mm, but actualX correspondence3.150mm>original2.500mm. Cube03–05notadvanced;7214valid sparse samples; all ownedruntimesstopped. `reports/TASK01_PRECISION_FULL_FIVE_REGRESSION.md` containscommands/negativeevidence/nextscope. Do not reinterpret earlierisolated fifth/fourth→fifthPASS as stable full-flow. XYZtracking/modelmetrology diagnosis/correction scope and existingfriction/hiddenmass/D004/36numericreview stillneeded;TASK02notstarted.

## Latest engineering validation / user-review boundary (2026-10-03)

Later than the historical failure checkpoints below: measured empty-retreat start / releasedCube strictFCL / bounded local-seed fallback implemented in independent approved precision variant. Basic and long no-command FK/FCL PASS; isolated actual Cube05 and fresh actual Cube04→05 pair both exit0/PASS. Fourth neighbor0.375mm/deep0.244mm; fifth error0.530mm/deep0.476mm. First3/4preplaced are not executed/full-five proof, fallback not physically triggered, no repeatability claim. Exact sources/commands/negative evidence: `reports/TASK01_EMPTY_RETREAT_REPAIR.md`. Task27 rotation fix from prior iteration preserved; USD dynamic timing still uncalibrated. Actualfriction0.5/0.5, hiddenmass, first-three D004 and36numericfields require review before benchmarkfreeze/paperalgorithms. All owned runtimes stopped; teardown-11 persists. No YAML/hash/scene/model/ACM/gate change.

## Authorized Cube04 protocol experiment (2026-10-03)

User explicitly asks Cube04 to use Cube05 precision single-rear insertion. Independent engineering controller target, no scene/model/gate changes; new PRE_PUSH Y control target is the old pressed 0.5-mm gap. Physical Cube04/05 probe uses only first three pre-placed/settled. See `reports/TASK01_CUBE04_PRECISION_INSERT.md` and D014; old D004 no longer applies to Cube04 in this variant, not blanket first-three approval. No numeric YAML freeze or TASK02 advance.

Final experimental handoff: one slow Cube04 PASS (neighbor 0.227 mm, deep 0.413 mm), earlier faster Cube04 drift failure. Cube05 follow-on empty retreat refused unsafe off-line IK branch; whole run exit 1. No stable/full-five PASS and no TASK01 freeze. Next engineering diagnostic is empty-retreat branch selection while original guards remain enforced.

## Current progress (2026-10-02)
- User confirmed the existing Task27 dual-FR3, L-side-suction and truck-box scene as the **geometric starting point**, not as a wholesale approval of its numerical parameters or thresholds.
- Draft candidate: `configs/benchmark/benchmark_v1.yaml`; analytic checker: `scripts/validate_benchmark_candidate.py`.
- Initial static geometry passed with 30 unresolved fields. After recording the user-confirmed B-fixture/B-center contact split, the latest static check still passes and has 36 unresolved fields (new alignment/force gates were made explicit).
- Fresh [EXPERIMENTAL] Isaac 4.5 probe: four Cubes directly pre-placed, then only Cube 05 executed with the right or left pusher in separate clean scenes. Right and left each passed 3/3 physical runs; final center error was at most 0.603/0.669 mm respectively. Detailed Ground Truth and boundaries are in `reports/TASK01_CENTER_ARM_SYMMETRY.md`. This small, non-seeded sample does not validate full four-Cube fixture construction, long-term reliability, calibrated contact forces, or the frozen benchmark.
- New instrumentation records final Bridge pose and compares motion-time PhysX and USD pose sources read-only. The sources differed transiently by up to about 2.8 mm in observed push samples, then converged after settle; this must be resolved as a measurement/timing issue before dynamic contact metrics are frozen (BUG-005). MoveIt shutdown also repeatedly segfaulted after successful controller completion (BUG-004).
- The benchmark remains **DRAFT / IN_PROGRESS**. No paper baseline may use it as a frozen common test yet.

## Goal
Freeze one common dual-FR3 Cube/carriage benchmark before tuning any paper method.

## Measurement follow-up (2026-10-03)
- Diagnosed the motion-time position mismatch as USD application-frame lag relative to PhysX physics steps. Separately confirmed that extracting a quaternion from the scaled Cube world matrix corrupts the old Bridge rotation. Historical Bridge yaw values are retained but must not be treated as accurate 6D measurements.
- Added an opt-in read-only physics pose/velocity channel with a single simulation timestamp and physics-step number per snapshot. External ROS known-motion calibration passed at 30 Hz and 20 Hz frame updates with 60 Hz physics: maximum position error about 0.000313 mm and angular error about 0.000865 deg. This is sensor-plumbing evidence, not contact/benchmark performance.
- Details, failures, source references and complete commands: `reports/TASK01_PHYSICS_POSE_MEASUREMENT.md`. Old Task27 control/scene sources and all 36 unresolved benchmark fields remain unchanged. TASK02 stays TODO pending review/freeze.
- A further real right-arm Cube 05 task passed (0.520 mm final center error, both arms HOME), while the separate recorder obtained 14,295 contiguous five-Cube snapshots with no record errors. This validates measurement integration with the existing physical task, not a new controller or full five-Cube benchmark.

## Force feasibility follow-up (2026-10-03)

- Independent known-load collision calibration passed at 60/120 Hz, including static friction, nonzero torque, rotated-wall force direction and same-step pose/contact stamping. Collision telemetry demonstrably omits suction D6 constraint loads.
- Independent mount-joint load probes passed at 0/90 deg roll, but their coincident frames do not identify the force reference. The final unscaled COM/principal/joint-anchor/joint-axis test identifies incoming joint axes / about joint anchor. Earlier scaled-body origin identification is invalidated and retained in records. This is not a calibrated FR3 TCP contact estimator or paper controller.
- Actual FR3 topology exposes link8 raw reactions, but its downstream hidden hand/finger/hand_tcp bodies retain mass. Gravity/inertia compensation and TCP moment shifting remain necessary; no body mass was removed.
- Added a separate full five-Cube headless measurement runner: normal feed, no pre-placed four-Cube fixture, unchanged legacy controller. Five-batch planning preflight passed, but physical run placed only Cube 01 then stopped at Cube 02 pre-close: symmetry residual 0.968 -> 0.315 -> 0.339 mm versus 0.300 mm gate, with mandatory 0.65 mm minimum correction. No threshold was relaxed. Reports: `TASK01_FORCE_MEASUREMENT_FEASIBILITY.md`, `TASK01_FULL_FIXTURE_CONTACT_PROBE.md`.
- Benchmark YAML is unchanged; its 36 null fields still require resolution/review, not automatic filling from a successful calibration.
- Review queue: `reports/TASK01_FREEZE_REVIEW_CHECKLIST.md` lists all 36 null fields and already-numeric but unapproved model choices. The last added real-FR3 authored-joint-frame startup audit failed on asset-root availability; that check and TCP compensation remain unvalidated.

## Codex actions

### Final tested outcome / review boundary (2026-10-03)

- Full inherited physical flow 5/5 and controlled Cube01 7-s hold both complete with exit 0/HOME; 17 offline Python tests PASS, latest report `reports/TASK01_RUNTIME_REVIEW_20261003.md`.
- D004 remains unmet: current centered Cube04 side helper tool intersects seated Cube03 (exact OBB evidence; no model/ACM change). Tool/contact-order review needed, not hidden protocol replacement.
- Actual physics Cube friction reads 0.5/0.5 rather than authored 0.90/0.75 because cleanup deletes material. Material version decision/retest needed before freezing.
- FR3 static mean support error 0.000370 N but raw force RMS 0.494278 N / mean moment error 0.014902 Nm and tensor-vs-pose velocity mismatch persist. Full-rate diagnostic fixes aliasing only; no calibrated TCP/internal-wrench claim.
- 36 nulls and numeric/model review pending, YAML/hash unchanged, TASK02 TODO. Following mandatory stop conditions, seek direction on material and centered-helper accessibility before scientific/model changes.

### Runtime-repair checkpoint (2026-10-03, later run)

- Pre-close overshoot fixed without gate relaxation: local seeded fine FK/Jacobian micro correction, maximum 1 mm, no minimum quantization, original 0.300 mm gate and three-attempt stop.
- Task27 quaternion extraction corrected; independent same-step physical records retained. Exact official asset root allows real FR3 joint-frame audit to run; both link8 incoming fixed joints have zero child anchor/identity child axes.
- Fresh normal-feed inherited physical demo **5/5 PASS**, exit 0, both arms HOME. 70,434 snapshots / zero integrity errors. Fifth center error 0.493 mm at controller settle / 0.563 mm at later physical final sample. Full report and upstream patches provide commands/hashes/negative evidence.
- Crucial remaining protocol gap: legacy first-four helper parks during rear push; outer side pressing does not suction the side cup, inner trim is solo. This does not satisfy D004 even though placements complete (BUG-009).
- A whole-process 7-s pause metrology attempt safely aborts after stale-state timeout. Replaced by an opt-in main-thread hold, keeping ROS executor active; controlled load calibration pending at this checkpoint. Ordinary hold default=0.
- All 36 nulls and numeric/model approval remain pending; user asked whether to keep 1e6 suction/1.946 kg hidden branch as candidate. TASK01 stays IN_PROGRESS, TASK02 TODO.
- Define FR3 base poses.
- Define cube size, mass and friction/contact parameters.
- Define left/right grasp transforms.
- Define carriage geometry and entrance frame.
- Define PRE_PUSH and insertion target/depth.
- Define physics dt, control dt and seed policy.
- Define all success/failure tolerances for Benchmark A/B.
- Define C0–C5 insertion perturbations.
- Validate geometry in Isaac; validate P2/P3 reduced version in MuJoCo if needed.

## Outputs
- `configs/benchmark/benchmark_v1.yaml`
- benchmark scene notes.
- benchmark hash/version.

## PASS/FROZEN
All values reviewed by user. Then mark FROZEN. Any later change requires DECISIONS entry and benchmark version bump.
