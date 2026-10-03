# STATUS

## 2026-10-03 latest — empty retreat engineering repair, tests pending

New precision-variant empty retreat uses measured joint seed and bounded continuous-seed fallback, with released Cube included in strict FCL. Build + policy +19 Python tests PASS; real RobotModel / physical verification next. No scene/model/material/ACM/gate change. Report: `reports/TASK01_EMPTY_RETREAT_REPAIR.md`. TASK01 IN_PROGRESS, TASK02 TODO; 36 nulls unchanged.

Latest follow-up: real RobotModel basic/long replay PASS; isolated actual Cube05 exit0/batch5 PASS, placement0.540mm/deepgap0.514mm; ordinary measured-start retreat/FCL passes, fallback not triggered physically. New clean Cube04→05 run starting. No stable/full-five claim; MoveIt teardown -11 remains.

Last update: 2026-10-03

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
| TASK01 Benchmark Freeze | IN_PROGRESS | Inherited demo 5/5 distinct from protocol/freeze. D014 Cube04 single-rear variant: one slow physical PASS, earlier drift FAIL; Cube05 continuous trial empty-retreat FAIL. First-three D004/model/force/time/36 nulls/teardown pending. Reports TASK01_CUBE04_PRECISION_INSERT and TASK01_RUNTIME_REVIEW_20261003 |
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
