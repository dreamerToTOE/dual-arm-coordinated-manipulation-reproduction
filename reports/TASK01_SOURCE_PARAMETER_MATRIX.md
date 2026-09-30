# TASK01 — Candidate source-parameter matrix

Date: 2026-09-30
Status: SOURCE STUDY ONLY — NOT benchmark_v1, NOT frozen, NOT validated in this repository.

## Provenance

The values below are extracted from the separate, previously exercised palletizing project:

- isaac/scripts/task26_truck_box_scene.py, in Task27 mode through task27_five_cube_center_insert_scene.py
- isaac/scripts/task26_truck_box_bridge.py, in Task27 mode
- ros_ws/src/fr3_dual_side_suction_description/urdf and srdf
- ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp
- ros_ws/src/fr3_dual_palletize/config/task26_push_control.yaml

This matrix is not an assertion that those values are scientifically suitable for every paper baseline. Importing them into the new repository would be an [ADAPTATION] and requires benchmark review.

## Source values relevant to a common scene

| Field | Existing Task27 value | TASK01 interpretation / unresolved decision |
|---|---:|---|
| Left FR3 base at rail rest | (0.650, -0.600, 0.000) m | Candidate Benchmark A base |
| Right FR3 base at rail rest | (0.650, +0.600, 0.000) m | Candidate Benchmark A base |
| Rail X travel per arm | [0.450, 1.050] m | Whether rails are enabled in the benchmark must be frozen |
| Push rail advance | +0.100 m from rest | Existing push phase uses x=0.750 m; Benchmark B start base may differ from A |
| Table top | z=0.200 m | Candidate world frame / support plane |
| Cube edge / half-edge | 0.120 / 0.060 m | Existing Cube is four times the original 30-mm linear edge |
| Cube mass | 0.800 kg | From USD MassAPI |
| Physics material | static friction 0.90, dynamic friction 0.75, restitution 0 | Material is bound to table, Cube and walls; confirm effective PhysX combination rule |
| L-tool geometry | 80-mm vertical, 130-mm lateral, TCP lateral offset 155 mm, 2×2 cups | Existing tool-specific candidate; paper methods should not hardcode tool geometry |
| Nominal side-contact TCP points in Cube frame | y≈±(0.060+0.001) m, x=z=0 relative to Cube center | 1-mm command gap, mirror-symmetric; full SE(3) grasp transforms still need derivation/approval |
| Side-suction capture threshold | 0.003 m | Existing physics setting, not yet a benchmark success threshold |
| Grip break limits | force/torque 1.0e6 | Existing near-unbreakable constraint; may bias pose/force studies and needs explicit review |
| Truck interior X | [0.910, 1.160] m | Entrance at x=0.910 m; +X push |
| Truck interior Y | [-0.303, +0.303] m | 0.606-m clear width for five 0.120-m Cubes |
| Wall thickness / height | 0.020 / 0.150 m | Wall top z=0.350 m; first-layer Cube top z=0.320 m |
| Single center-Cube PRE_PUSH | (0.790, 0, 0.260) m | Existing Task27 fifth-Cube target before pushing |
| Single center-Cube final center | (1.100, 0, 0.260) m | Deep wall face x=1.160 m is exactly touched at target |
| Center-Cube translation | +0.310 m in X | Includes 0.060 m of approach before the entrance face |
| Adjacent inner Cube centers | (1.100, ±0.1215, 0.260) m | Leaves 1.5-mm nominal gap on each side of centered Cube |
| Outer Cube centers | (1.100, ±0.243, 0.260) m | Existing pressed target touches corresponding Y wall nominally |
| Controller command period | 0.010 s | Existing dual command period, not proven to be the Physics step |
| Isaac physics step | Not explicitly authored in Task27 scene | Must be explicitly set and measured before freeze |
| Existing FCL sample period | 0.010 s | Legacy verification detail, not necessarily final benchmark policy |
| Existing final placement tolerance | 0.010 m | Too permissive to adopt silently as a scientific success threshold |

Simple geometry calculation from these source values: 5 × 0.120 + 4 × 0.001 + 2 × 0.001 = 0.606 m; center-to-inner-fixture clearance is 0.1215 - 0.060 - 0.060 = 0.0015 m on each side. This is only an analytic check, not a PhysX contact validation.

## Choices that must precede benchmark_v1 freeze

1. Choose whether Task27's existing L-tool, rails and truck are the starting geometry or whether this scientific benchmark gets a new independent scene. User review requested.
2. Define Benchmark A's exact initial shared-grasp pose and start robot state. The source scene begins before grasp; the repository spec begins after stable shared contact.
3. Define Benchmark B's start mode: released Cube with a pushing arm and side-support arm, or another dual-arm contact topology. The old demo's mode transitions cannot be silently substituted for a paper benchmark.
4. Freeze full left/right object-to-TCP SE(3) transforms and a common world, carriage and entrance frame convention.
5. Set and measure physics dt, control dt, solver/contact settings, and one timestamp domain. The existing scene does not explicitly set physics dt.
6. Specify contact-wrench sensors/calibration. Legacy joint effort alone is insufficient for P2/P3 force metrics.
7. Fix seeds, trial count, perturbation magnitudes/signs for C0–C5, tuning budget and success/failure thresholds before comparing methods. Do not use the old demo's tolerances uncritically.
8. Run the candidate in Isaac and, if useful, a reduced MuJoCo contact test; then produce a content hash and user-reviewed benchmark_v1.yaml. No candidate has been frozen yet.

## Scientific classification

- [ORIGINAL]: no paper-specific algorithm is implemented here.
- [ADAPTATION]: mapping the common benchmark to a dual-FR3 Cube/carriage scene.
- [ENGINEERING]: collecting source constants and checking dimensional arithmetic.
- [DEVIATION]: none implemented; possible departures (near-unbreakable suction, rigid fixtures, ground truth instead of sensing) remain explicit review items.
- [EXPERIMENTAL]: no new physical benchmark run in TASK01 yet.
