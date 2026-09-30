# TASK01 — benchmark_v1 draft candidate

Date: 2026-09-30
Status: **DRAFT, not FROZEN**

## Scope and provenance

The user confirmed the legacy Task27 dual-FR3, fixed L-side-suction and truck-box scene as the geometric starting point. The candidate in `configs/benchmark/benchmark_v1.yaml` transcribes the observed source values; the legacy source revision and individual SHA-256 file hashes are recorded in that YAML. These values are an **[ADAPTATION]** to a shared experimental benchmark, not an [ORIGINAL] numerical specification from any of P1–P5. This iteration implements no paper algorithm.

## Candidate geometry

- FR3 bases at rest: left `(0.650, -0.600, 0.000)` m, right `(0.650, +0.600, 0.000)` m; independent X rails `[0.450, 1.050]` m.
- Table top `z=0.200` m; Cube `0.120` m edge, `0.800` kg, center `z=0.260` m. Authored static/dynamic friction `0.90/0.75`; effective contact law is not yet verified.
- Tool: fixed 80-mm-down + 130-mm-sideways L tool; TCP lateral offset from link8 155 mm. Nominal opposite-face TCP translations relative to an axis-aligned Cube are `y=±0.061` m, including a 1-mm commanded gap. Candidate quaternions are directly derived from the legacy `sidePose()` function, not from a measured grasp.
- Carriage interior `x=[0.910,1.160]`, `y=[-0.303,+0.303]` m. Entrance is on `-X`; insertion travels `+X`. The candidate entrance frame is **proposed** at `(0.910,0,0.200)` m, identity orientation; the legacy scene did not publish this TF.
- A target / B start Cube center `(0.790,0,0.260)` m; B target `(1.100,0,0.260)` m. The commanded insertion travel is `0.310` m. At target, Cube's +X face touches the deep wall nominally. Adjacent inner cubes at `y=±0.1215` leave `1.5` mm nominal clearance on either side of the center Cube.

## Validation performed

`python3 scripts/validate_benchmark_candidate.py` passed analytic checks for table/cube/wall heights, 606-mm interior width, A/B handoff, entrance gap, deep-wall and side-wall flush positions, quaternion norm and 1.5-mm center side gaps. It found **30 unresolved configuration fields**. The candidate file SHA-256 at this iteration is:

`6fd7e167ea703ec6874b3090e04f4837bddc4c10279200d91ed6748793ff49e0` (initial draft)

See `results/20260930_TASK01_static_geometry/` for command, metadata and output summary. This is **not** an Isaac collision/contact validation. No Isaac process was active at the time of this iteration.

## Before TASK01 can pass or freeze

1. Define Benchmark A's actual dual-grasp initial Cube pose and robot joint state; validate the proposed object-to-TCP transforms with measured TCP poses.
2. Choose Benchmark B's start contact topology and supporting/pushing roles. The old demo's mixed suction/release/push phases cannot be imported silently.
3. Decide rail poses for both benchmark starts, and publish/verify the proposed carriage-entrance TF.
4. Explicitly configure and measure physics dt, controller dt and one ROS timestamp domain; verify PhysX material combination and contact settings.
5. Provide calibrated end-effector/contact-wrench measurements (legacy joint effort is insufficient), collision-distance metric and safety monitor.
6. Review C0–C5 perturbation magnitudes, seeds/trials, tuning budget and all success/failure tolerances. None inherit the demo's permissive 10-mm placement tolerance by default.
7. Run fresh Isaac scene/physics validation and user review. Only then mark PASS/FROZEN and pin a benchmark hash/version.

## Scientific classification

- [ORIGINAL]: No paper method has been implemented.
- [ADAPTATION]: Task27 geometry mapped to a proposed common dual-FR3 benchmark.
- [ENGINEERING]: Source hashes, structured draft configuration and static consistency checker.
- [DEVIATION]: None executed. Near-unbreakable suction and simulator ground truth remain **possible** deviations requiring approval and explicit reporting before comparison.
- [EXPERIMENTAL]: Analytic geometry check only; no physical simulation trial.

## Contact-protocol revision (2026-09-30)

The user clarified that Cube 01–04 and Cube 05 have **different** placement control problems:

| Subcase | Initial staging | Contact and action | Endpoint |
|---|---|---|---|
| B-fixture, Cube 01–04 | Coarse but safe PRE_PUSH; final precision can be corrected during push | Rear-face suction arm pushes +X while a side-face suction arm constrains Y/yaw. At deep-wall contact, the side arm presses laterally while the former pusher holds the Cube against the deep wall. | Outer cubes against side walls; inner cubes against seated outer cubes. |
| B-center, Cube 05 | Precisely aligned PRE_PUSH | One rear-face suction arm pushes +X; the other arm has no Cube contact. | Center gap between inner cubes; nominal 1.5-mm side clearance. |

The final-side-wall wording only applies to outer fixture cubes. The center cube cannot be pressed directly onto the Y walls because the other four cubes intervene. Cube 05 is therefore an **[EXPERIMENTAL] single-arm subcase**, not a reproduced dual-arm insertion controller. Do not aggregate the B-fixture and B-center success rates or claim the latter proves P2/P3 dual-arm coordination.

At 1° yaw, the 120-mm square's projected half-width grows by about 1.038 mm, leaving only 0.462 mm nominal lateral budget from the 1.5-mm side gap. A staging gate must account for yaw, lateral offset, collision geometry and physical margin. No numerical gate is frozen yet.

The revised candidate YAML SHA-256 is `a49d60a4dc6a8a00c3bf55a512113af50760968827a8cefe64dae1c7de55fde8`; its analytic checker passes with 36 unresolved fields. See `results/20260930_TASK01_contact_protocol/`. This remains a draft; no Isaac physical validation was run.
