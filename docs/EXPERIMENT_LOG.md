# EXPERIMENT_LOG

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
