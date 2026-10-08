# TASK01 — Bounded Critical-State Controlled Replay Fallback

2026-10-08. **PREPARED / NOT RUN** at this source checkpoint.

## PRE-TASK REPORT

- Task: TASK01 remaining Tier2 critical safety / deterministic reset evidence.
- Scientific objective: minimum reproducible one-Cube common benchmark, not simulator model equivalence.
- Minimum sufficient evidence: no obvious unexpected Isaac collision invalidating approved nominal geometry at four recorded critical states; then five measured deterministic resets each at START/PRE_PUSH, all with post-physics simulation time.
- Current scope: **START/state0, PRE_PUSH/state135, state196/B60, TARGET/state292 only**; not all292 states. No replacements needed: TARGET already contains the minimum wrist/tool–environment FCL distance2.212219mm, state196 the minimum all-pair0.999669mm.
- Explicit non-goals: zero-step/query-tree/native-handle repairs, parity10, equivalence proof, continuous collision proof, suction stability, wrench/force controller, P2/P3, five-Cube Task27, target/time/success-tolerance redesign.
- Attempt budget: prior07/08/09 same-root3/3 exhausted and permanently stopped; **one separately user-approved bounded controlled fallback**, no automatic repair/retry. Visible process cap120s (internal elapsed guard100s).
- Preferred method: original static-query route STOPPED; not reactivated.
- Approved fallback: original constructors/assets, exact recorded14q/Cube, one normal PhysX simulate/fetch step per snapshot, original contact reports (points/separations) and focused original shape/environment overlaps. Normal startup, not repeated native-handle reconstruction. No random IK or geometry/physics/ACM change.
- Stop/escalation: first explicit unexpected penetration/overlap, invalid state/contact reading, extra uncontrolled step, timeout or engineering failure stops this attempt. Preserve evidence; no new variant without user decision.
- Files expected: this minimal harness/test, run metadata/evidence, three TASK01 reports and six persistent records. Historical parity scripts remain unchanged.
- Validation: input hashes and four indices; pure contact-classification tests; source checkpoint before one visible run; q/Cube pre-write readback and same-poststep actual q/Cube/TCP/carriage/time; critical gate before reset; record5+5 if gate reached.
- Known ambiguities: reset/success numerical tolerances still PENDING_USER_REVIEW. Do not silently use IK tolerances for dynamic reset acceptance. Free dynamic Cube keeps original gravity; no claim of sustained held/suction state. TARGET Cube/deep-wall boundary is expected pending benchmark-definition review, not automatic collision FAIL.
- Execution drift review: each critical state and each first reset pauses at a stdin barrier after saving actual post-step q/Cube/TCP, drift and Cube/environment plane gaps. The executing agent must inspect these data before accepting the snapshot/advancing; no implicit numeric success tolerance is introduced. TARGET expected-boundary classification is not a waiver of actual deep penetration; actual gaps/contact separations are recorded and reviewed. Rejected/unclear snapshot stops the bounded run, not a new repair.
- Need user confirmation: no; this exact fallback authorized. FROZEN and any benchmark-definition change still require user.

## Paper fidelity

[ADAPTATION] unchanged dual-FR3 scientific benchmark. [ENGINEERING] bounded normal-step evidence gathering. [EXPERIMENTAL] simulator safety/reset observations only, not reproduced paper results. No paper controller, [DEVIATION], or benchmark redesign implemented.

## Intended command

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
timeout --signal=TERM --kill-after=20s 120s env DISPLAY=:1 PYTHONUNBUFFERED=1 \
  scripts/run_isaac_bundled_ros.sh \
  platforms/isaac_ros2/probes/task01_critical_controlled_replay_gui.py \
  --output-dir results/20261008_TASK01_bounded_controlled_replay/raw \
  >results/20261008_TASK01_bounded_controlled_replay/launch.log 2>&1
```

Status is based on structured actual evidence, never wrapper exit0 alone. No second simulator run is automatically authorized.
