# Paper-to-code coverage map — provisional, must be verified at T00

| Paper portion | Historical code | Required new qualification |
|---|---|---|
| (1)–(6) SE(3) Lie representation | `baselines/p2_pose_force/contact_geometry.py`, `common/geometry/se3.hpp` | Independent SO(3)/SE(3) Exp/Log/Adjoint conventions & finite-difference identities |
| (7)–(8), (15) contact geometry and varying modes | `contact_geometry.py`, `reports/P2_CONTACT_GEOMETRY_DERIVATION_RENDERED.md` | Original-vs-approved-alternative Eq.15 discrepancy table, valid domain |
| (9)–(12) compliance, wrenches, grasp matrix | `mechanics.py`, `native_kernel.cpp` | Independent wrench balance, frame transform, object inertial effects |
| (13)–(16) state/plant | `mechanics.py`, `native_model.py` | 42-state contract, stable integration, non-privileged controller access |
| (17)–(18) visual-tactile IESEKF | `observations.py`, `estimator.py`, `clocking.py` | Closed-loop failure root cause; standard EKF contrast; vision dropout; causal timing |
| (19)–(24) wrench controller & local stability | `control.py`, `tests/test_p2_control_qualification.py` | Projector rank/physical units, linear vs nonlinear response, robustness |
| (25) object SE(3) pose control | `control.py` | Trajectory tracking with independent estimated pose |
| (26) robot joint kinematic inversion + contact selector | Historically **not shown fully qualified** at joint level | Add 7-DOF joint model, Jacobian pseudoinverse, null-space, singularity limits (no invented original URDF claims) |
| Fig.6 exp1–exp4 | `scripts/run_p2_closed_loop.py`, original `configs/p2_closed_loop_protocol_v3.json` | Re-run only after estimator+controller gates; paper parameters and four conditions |
| Fig.7 high internal moment | historical `qualify_p2_implicit_v3.py` plant traces | Controlled run with genuine measurement/estimation & internal torque comparison |
| Fig.8 assembly A/B1/B2/C | no verified full scene | Virtual physics assembly; per-object pose stats; initial conditions and 5 repeats |
| Fig.9 sliding/pivot | `contact_geometry.py` and historical sliding **plant** trace | Independent physical sliding with actual relative motion/friction & mode change |
| Supplemental video EKF/contact placement | external resource not fully audited | Acquire official video or label unavailable; never invent comparison values |

**NOTE:** A historical module's presence here is a reuse lead, not proof it implements the exact paper equation. T00–T05 must check terms, frames, parameters and numerical evidence against the paper.
