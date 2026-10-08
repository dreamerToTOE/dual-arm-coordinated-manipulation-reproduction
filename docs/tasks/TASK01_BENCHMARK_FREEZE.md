# TASK01 — Core Single-Cube Benchmark Freeze

Status: **IN_PROGRESS / PARTIAL — topology corrected by D039 (2026-10-08)**

Latest: user approved D039 fixed rail move .650→.750both and world_shift_x=+.100; A/rest .650 unchanged. Candidate is recorded, not FROZEN. One bounded single-Cube integration prepared, ending complete INSERT_READY; software tests PASS, actual integration NOT_RUN. No second station/search/target command. [Protocol](../../reports/TASK01_FIXED_HANDOFF_INTEGRATION.md). The prior audit paragraph below describes the earlier pre-approval checkpoint.

2026-10-08 update: [pinned-source reuse audit and minimal integration plan](../../reports/TASK01_PRIOR_PROJECT_REUSE_AUDIT.md) completed without simulator/IK/build. Existing Task24 hold and Task26 rear primitives are present. The raw historical right-pusher PASS uses both base rails X=.750; current YAML only declares rest X=.650 plus rail limits. Confirm the nominal INSERT_READY base/rail state before integration; actual14q/holding/reset remain pending. Current benchmark YAML and all geometry/physics are unchanged.

## Scientific objective
Freeze the minimum reproducible single-Cube benchmark that matches the actual research workflow already demonstrated in the predecessor project:

```text
dual-FR3 bilateral side-suction tight transport
START → PRE_PUSH
        ↓
fixed handoff: release → right-arm rear regrasp
        ↓
single-arm constrained +X insertion
INSERT_READY → TARGET
```

TASK01 is a benchmark-definition and reproducibility task. It is not a force-controller task.

## D039 correction — active topology

The previous draft incorrectly required both side-suction tools to remain attached from PRE_PUSH all the way to TARGET. That topology is now **superseded**.

Why:
- the validated predecessor Task26/Task27 workflow releases bilateral side suction at PRE_PUSH;
- one arm then regrips the Cube on its -X face and performs segmented +X insertion;
- keeping both side wrists attached at TARGET produced an actual Isaac link7/deep-wall penetration of about -3.016 mm;
- that negative result is retained, but it does not define the corrected Benchmark B.

Do **not** fix the superseded topology by changing ACM, wall geometry, tool geometry, collision meshes, or moving TARGET from x=1.100 merely to make both wrists fit.

## Prior engineering assets to reuse
Read `docs/PRIOR_PROJECT_REUSE.md` before any TASK01 implementation.

Primary source:
`dreamerToTOE/dual-arm-embodied-palletizing@side-suction-palletizing`

Reuse, do not reinvent:
- Task24 bilateral L-tool Surface Gripper attachment and transport;
- Task11–13 evidence that two Surface Grippers can hold one rigid object;
- Task26/27 release → rear regrasp → segmented +X insertion → exit topology;
- Task26/27 full-chain candidate precheck idea;
- Task27 center-Cube default **right-arm pusher** and helper-arm park strategy.

The full five-Cube application remains legacy/stress-test scope; only reusable primitives and evidence are imported.

## Benchmark A — TIGHT_TRANSPORT

### Start
Cube center:
`[0.550, 0.000, 0.380] m`, identity orientation.

Both side Surface Grippers are already CLOSED and the Cube is stably shared-held. Grasp acquisition is not scored.

### Goal
PRE_PUSH_SHARED:
`[0.790, 0.000, 0.260] m`, identity orientation.

### Existing evidence
Dense START→PRE_PUSH geometry already passed with 136/136 states using the recorded deterministic 14q chain. Preserve that result; do not rerun it unless a frozen input changes.

### Remaining TASK01 evidence
1. Reuse the existing Surface Gripper hold representation rather than a free Cube.
2. Verify START and PRE_PUSH can be restored repeatably with bilateral hold active.
3. Record q/Cube/TCP/grasp residual and post-physics simulation time.

Do not calibrate wrench or tune suction dynamics here.

## Fixed handoff — PRE_PUSH_SHARED → INSERT_READY

This is a common engineering transition, **not a scored P3 controller**.

Required sequence:
```text
PRE_PUSH_SHARED
→ release both side suctions
→ move left helper arm to safe park outside insertion workspace
→ move right pusher to Cube -X face
→ close existing right Surface Gripper
→ verify attachment + collision gates
→ INSERT_READY
```

Reuse the predecessor Task26/27 behavior and bounded candidate selection. Do not invent a new grasp controller.

Capture and freeze the resulting deterministic INSERT_READY robot state after validation.

## Benchmark B — CONSTRAINED_INSERTION

### Start
INSERT_READY:
- Cube center remains `[0.790, 0.000, 0.260] m`;
- right arm holds Cube on -X face;
- left helper is parked outside the insertion work zone.

### Goal
Cube center:
`[1.100, 0.000, 0.260] m`, identity orientation.

TARGET x=1.100 is retained because this exact staged topology has prior successful physical evidence. Do not change TARGET solely because the superseded bilateral-to-TARGET topology collided.

### Nominal execution topology
```text
right rear Surface Gripper CLOSED
→ +X segmented insertion
→ deep-wall support / gap check
→ safe retreat
```

For future P3 comparisons, metrics begin at INSERT_READY. Handoff time/planning is logged separately and is not part of the force-control score.

## Minimum sufficient evidence for TASK01

- [x] One-Cube geometry, tool, carriage, frames and material candidate explicit.
- [x] Benchmark A START and PRE_PUSH poses explicit.
- [x] Dense A START→PRE_PUSH nominal geometry passed.
- [x] Superseded bilateral-to-TARGET topology failure preserved.
- [ ] Existing bilateral Surface Gripper representation works for A READY/reset.
- [ ] PRE_PUSH → fixed handoff → INSERT_READY is reproduced by reusing predecessor engineering.
- [ ] INSERT_READY deterministic q/TCP/Cube state is captured.
- [ ] Rear-push INSERT_READY→TARGET passes bounded geometry/FCL checks.
- [ ] Critical Isaac sanity confirms no unexpected robot/tool–environment collision for the corrected staged B topology.
- [ ] Repeated START / PRE_PUSH (and if useful INSERT_READY) reset evidence is reproducible.
- [ ] Pending benchmark-definition items receive user review.
- [ ] User marks benchmark_v1 FROZEN.

## Explicit non-goals
Do not spend TASK01 time on:
- five-Cube sequencing/reliability;
- proving MoveIt STL == PhysX cooked hull;
- zero-step query-tree perfection;
- force/TCP-wrench calibration;
- desired push force, impedance/admittance gains, jam thresholds;
- P2/P3/P5/P1 algorithms;
- redesigning the L tool, carriage or ACM;
- tuning historical Surface Gripper parameters unless reuse fails once and the user explicitly approves investigation.

## Attempt budget / stop rule
Follow `AGENTS.md` and `docs/EXECUTION_GOVERNANCE.md`.

For each new blocker:
1. reuse/read predecessor implementation first;
2. one bounded integration attempt;
3. if it fails for a new substantive reason, STOP and classify before designing another variant.

Do not restart parity10 or the superseded bilateral-to-TARGET line.

## Pending final review items
These remain user decisions before FROZEN:
- formal success tolerances for A and B;
- nominal friction 0.5/0.5 final acceptance;
- physics/control frequency relationship;
- exact reset repetition count;
- whether later P3 robustness cases need additional controlled guide/constraint fixtures.

## Historical evidence
The previous active TASK01 file, including the parity03–09 and bilateral-TARGET history, is preserved at:
`docs/tasks/TASK01_BENCHMARK_FREEZE_HISTORY_PRE_D039.md`

Key reports remain authoritative historical evidence:
- `reports/TASK01_FULL_SINGLE_CUBE_GEOMETRY.md`
- `reports/TASK01_GOVERNANCE_REVIEW.md`
- `reports/TASK01_BOUNDED_CONTROLLED_REPLAY.md`
- `reports/TASK01_CRITICAL_SAFETY_COMMAND_RERUN.md`
