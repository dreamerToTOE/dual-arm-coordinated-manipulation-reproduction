# Reproduction experiment matrix — no experiment omitted

This is a **planning index** for simulation; outcomes remain `NOT_EXECUTED` on the new branch. Numerical/virtual experiments are not hardware experiments.

| ID | Original evidence | Baseline & contrast | Simulation outputs / required metrics | Target gate |
| --- | --- | --- | --- | --- |
| E00 | Eq.(1)–(18), Tables I–II | Lie/contact/plant/estimator qualification | invariant, residual, energy, numerical convergence, covariance positivity | T02–T04 |
| E01 | Fig.6 exp1 | pose control only | position/angular error, internal force vs time | T06 |
| E02 | Fig.6 exp2 | internal wrench controller only | position/angular error, internal force vs time | T06 |
| E03 | Fig.6 exp3 | both controllers | same trajectories, timing, error/force RMS & maxima | T06 |
| E04 | Fig.6 exp4 | both + biased stiffness model | same vs E03; true-vs-assumed K and robustness | T06 |
| E05 | Fig.7 | exp1 vs exp3 on high-moment pose | internal **moment** and force time series; improvement ratio with stated interval | T07 |
| E06 | Supplement video | manifold IESEKF vs standard EKF | pose/calibration error & robustness under matched sensor noise/occlusion | T04 |
| E07 | Fig.8 | sequential assembly of A,B1,B2,C | final pose accuracy per object, contact timeline, full success, 5 repeats | T09 |
| E08 | Fig.9 | pivot vs sliding/contact switch for C | actual relative motion, friction/contact state, force and pose curves | T08 |
| E09 | Supplement video, IV.A | slow lowering and contact detection | external wrench estimate, trigger errors, final placement | T09 |
| E10 | Table I–II and protocol | reported params / hardware timing emulation | parameter provenance, unreported fields flagged UNKNOWN | T00–T01 |

Comparison grading **per experiment**:
1. `MATH_PASS`: equations/invariants only;
2. `NUMERICAL_REPRODUCED`: simulated controlled dynamics completed;
3. `PHYSICS_REPRODUCED`: independent MuJoCo behavior completed;
4. `PAPER_TREND_MATCH`: specified experiment's trend consistent;
5. `PAPER_QUANT_MATCH`: comparable metric and measurement conditions plus declared tolerance;
6. `FAIL/BLOCKED/NOT_EXECUTED` preserved honestly.

Capture at least `time_s, object_pos_error_m, object_orientation_error_rad, internal_force_N, internal_moment_Nm, contact_mode, commanded_twist, pose_ground_truth, pose_estimate, estimator_health, parameters, source_sha`. Do not fill missing data with zero. Compare per experimental phase, not mismatched time windows.
