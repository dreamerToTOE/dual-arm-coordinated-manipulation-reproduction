# DECISIONS

## D010 — Repair quantization without weakening alignment or bypassing protocol review
- Date: 2026-10-03
- Classification: [ENGINEERING] bounded residual/local-FK correction and scaled-transform extraction; [EXPERIMENTAL] normal-feed regression.
- Decision: Remove mandatory 0.650 mm pre-close step, keep maximum 1 mm, original 0.300 mm physical gate and three attempts. Use seeded local FK micro-IK only while ungrasped, with conservative scope/joint bounds and unchanged full synchronized FCL. Task26 default unchanged.
- Measurement: Task27 scale removal fixes its quaternion only, not USD frame lag. Explicit official asset root only avoids directory discovery failure; same FR3 source still required.
- Scientific boundary: A repaired legacy five-Cube demo is not automatically D004 fixture-protocol or TASK01 freeze evidence. No benchmark numeric approval, geometry/mass/material change, ACM expansion or paper implementation is authorized by persistence request.

Append-only architectural and scientific decisions.

## D001 — Two-platform strategy
- Date: 2026-09-29
- Decision: Isaac Sim + ROS2 is the final common benchmark; MuJoCo is an auxiliary force/contact laboratory mainly for P2/P3.
- Reason: preserve fair final comparison while accelerating force/contact debugging.
- Impact: baseline algorithms remain platform-independent and use adapters.

## D002 — Baseline-first rule
- Date: 2026-09-29
- Decision: `ours/` remains algorithmically empty until TASK30.
- Reason: derive our method from reproducible evidence and failure cases rather than premature design.

## D003 — Task27 as TASK01 geometric starting point
- Date: 2026-09-30
- Classification: [ADAPTATION]
- Decision: Use the existing Task27 dual-FR3, fixed L-side-suction, rail and five-wide truck-box scene as the *starting geometry* for the common benchmark draft.
- User input: Explicitly confirmed "对" in response to this proposed starting point.
- Scope: This does not freeze the existing physics, grasp/contact topology, perturbations, timings or success thresholds. TASK01 stays IN_PROGRESS until the candidate and all values are reviewed and validated.
- Impact: The Task27 source constants are traceable in `configs/benchmark/benchmark_v1.yaml`; unresolved choices stay null rather than inheriting unsafe demo defaults.

## D004 — Different contact protocols for the first four and fifth cubes
- Date: 2026-09-30
- Classification: [ADAPTATION] for the common Task27 cell; [EXPERIMENTAL] for the task-specific staged contact sequence.
- Decision: Cubes 01–04 may start from coarse safe PRE_PUSH staging and are pushed toward the deep wall with a rear-face suction primary arm and a side-face suction constraint arm. At deep-wall contact, the side arm presses laterally while the former pusher holds the deep-wall constraint. Cube 05 is precisely aligned at PRE_PUSH, then inserted by one rear-face suction arm; the other arm makes no Cube contact.
- User input: Explicitly distinguished the first four dual-arm adjustable placements from the fifth single-arm precision insertion.
- Scientific boundary: Cube 05 is not a two-arm insertion test and must not be reported as evidence for a reproduced cooperative insertion controller. Cross-method results must distinguish the dual-arm fixture phase from the single-arm center phase.
- Still open: pre-push tolerances, primary arm assignment, contact-force limits, B-case perturbations and physical validation. No values are frozen by this decision.

## D005 — Isolated Cube 05 arm-symmetry probe, not a benchmark shortcut
- Date: 2026-09-30
- Classification: [EXPERIMENTAL] test fixture and [ENGINEERING] test-only arm selector.
- Decision: For the arm-symmetry feasibility probe only, directly place Cubes 01–04 at their final cells, require actual Isaac physics settle, then feed and execute only Cube 05. Run left and right from separate clean scenes. Keep the legacy controller's default `center_pusher_arm=right`; choosing left requires an explicit parameter.
- Reason: Compare whether either arm can physically perform the fifth-Cube single-arm push without spending four prior cycles on each test. This does not validate first-four placement or freeze the benchmark.
- Numerical implementation: 100 nm comparison guard at the 1.5 mm inner-side-gap boundary only, to absorb an observed 38 nm float32 serialization excess; neither the target geometry nor the material threshold changes at meaningful precision.
- Impact: Results are labeled [EXPERIMENTAL], with separate run metadata and raw log pointers. TASK01 remains IN_PROGRESS.

## D006 — Keep Cube 05 repeatability evidence exploratory
- Date: 2026-10-02
- Classification: [EXPERIMENTAL] repeated fixed-fixture trials; [ENGINEERING] read-only logging and pose-source probes.
- Decision: Record right/left 3/3 physical passes as a small-sample feasibility result only. Do not freeze a reliability number, arm-equivalence claim, or contact-dynamics metric from these trials: OMPL seed is uncontrolled, four fixture Cubes were pre-placed, and contact wrench is absent.
- Measurement rule: Final settled `/task27/cube_poses` is usable as Isaac Bridge Ground Truth for this exploratory position report, but motion-time USD and PhysX poses are not yet a synchronized measurement contract. Keep their discrepancy open as BUG-005.
- Impact: TASK01 remains IN_PROGRESS with 36 unresolved configuration fields; no benchmark thresholds, geometry or Task27 control logic changed.

## D007 — Diagnose and isolate measurement errors before benchmark freeze
- Date: 2026-10-03
- Classification: [ENGINEERING] read-only sampler/environment launcher; [EXPERIMENTAL] deterministic free-body calibration; [ADAPTATION] Isaac Ground Truth to ROS.
- Decision: Add a separate optional PhysX post-step pose/velocity channel with one simulation stamp and step number per snapshot. Reject invalid physics handles rather than falling back to USD. Keep Task27 control and legacy topics unchanged while documenting their defects.
- Reason: USD callback positions lag the physical state; quaternion extraction from the scaled Cube transform is independently wrong. Dynamic contact metrics cannot be validated from these old measurements.
- Validation: External ROS known-motion calibration at 60 Hz physics with 30/20 Hz frame updates, without contact. Explicit zero damping applies only to that calibration body, never to the Task27 scene.
- Impact: Old exploratory settled position metrics remain traceable; old yaw metrics are marked invalid for physical 6D claims. TASK01 remains IN_PROGRESS, TASK02 interfaces remain unfrozen, and no contact-force or paper fidelity claim is introduced.

## D008 — Separate collision wrench, mount reaction and contact estimation
- Date: 2026-10-03
- Classification: [ENGINEERING] same-step telemetry/buffer handling; [ADAPTATION] Isaac impulses to world N/Nm; [EXPERIMENTAL] known-load calibration fixtures and nominal full five-Cube probe.
- Decision: Calibrate collision normal/friction forces and moments separately from suction D6 loads. Use an isolated articulated mount to test reaction availability and frame/reference-point conventions, not to silently insert a new FR3 load-cell joint. Keep real FR3 raw reactions explicitly raw until gravity/inertia compensation, sign and TCP moment shift are validated.
- Reason: Suction can support 7.848 N while collision signals are zero. Actual FR3 has retained hidden-body mass; raw reactions are therefore not end-effector contact estimates.
- Numerical boundary: Calibration gates/known loads belong to the independent metrology fixture, not benchmark acceptance thresholds. No TASK01 numeric field is frozen from these experiments, and no legacy model mass or control parameter changes.
- Full-flow boundary: Normal-feed Task27 five-Cube probe uses the existing controller without pre-placing the fixture. Controller log alone establishes its actual physical completion; five feed ARRIVED flags do not prove five placements. Paper fidelity/contact topology still needs separate review.

## D009 — Validate physical reference; retain negative full-flow results
- Date: 2026-10-03
- Classification: [ENGINEERING] raw naming/model checks/metadata; [EXPERIMENTAL] axes/anchor fixture; [ADAPTATION] eventual TCP wrench mapping.
- Decision: Verify actual physics COM, no rigid-body scale in reference fixture. Test link/principal/joint axes crossed with link origin/COM/joint anchor. Final result is joint axes/about joint anchor. Explicitly invalidate earlier scaled-body inferences, preserve raw software PASS.
- Impact: Real FR3 reactions stay raw until actual joint frame/anchor, gravity/inertia and TCP shift checks. Failed asset-root startup is not a successful frame audit.
- Full flow: Record 5/5 planning-only but 1/5 physical completion, Cube 02 pre-close overshoot separately. Never widen the 0.300 mm gate to accommodate minimum 0.650 mm correction. No legacy controller fix in this read-only scope.
- Freeze: 36-field checklist is a review queue, not approved values. Keep YAML/hash unchanged, TASK01 IN_PROGRESS, TASK02 TODO; no early paper algorithm/model mass changes.
