# Prior Project Reuse Map — side-suction-palletizing

Status: **ACTIVE ENGINEERING REFERENCE for TASK01 and later Isaac integration.**

Source repository:
- `dreamerToTOE/dual-arm-embodied-palletizing`
- branch: `side-suction-palletizing`

The reproduction project must not treat previously validated engineering assets as if they do not exist. Reuse is allowed and preferred when it preserves the scientific benchmark and does not import paper-specific claims.

## What is already physically demonstrated

### A. Bilateral side-suction shared-object transport
Relevant predecessor:
- `docs/tasks/TASK24_SIDE_SUCTION_TIGHT_OFFLINE.md`
- `isaac/scripts/task24_side_suction_tight_scene.py`
- `isaac/scripts/task24_side_suction_tight_bridge.py`
- `ros_ws/src/fr3_dual_palletize/src/task24_side_suction_tight.cpp`

Validated behavior:
```text
bilateral side contact
→ both Surface Grippers CLOSED
→ common lift
→ common X/Y transport
→ common descent to PRE_PUSH/entry region
→ release
```

The same L-shaped side-suction tool family is used: 80 mm vertical drop, 130 mm lateral support, TCP lateral offset 155 mm. Task24 records two independent single-Cube physical passes with final placement errors 0.184 mm and 0.115 mm.

Task24's validated Isaac holding mechanism used the existing Surface Gripper / D6 attachment abstraction. The historical parameters are engineering references, not newly calibrated force semantics:
- fixed grasp / bendAngle 0;
- stiffness `1e4`;
- damping `1e3`;
- force/torque break limits `1e6`;
- capture threshold approximately 3 mm.

TASK01 may reuse this mechanism to represent the benchmark statement “already stably shared-held”. It must not turn this reuse into suction-dynamics research or wrench calibration.

### B. Shared-object attachment itself
Relevant predecessors:
- `docs/tasks/TASK11_SHARED_OBJECT_BASELINE.md`
- `docs/tasks/TASK12_SHARED_BOX_LIFT.md`
- `docs/tasks/TASK13_SHARED_BOX_PLACE.md`

These tasks already demonstrated that two Isaac Surface Grippers can attach to the same rigid body, lift it, transport it, descend, release, and retain small relative-geometry error. Therefore “can Isaac represent a body held by both arms?” is not a new research question.

### C. Staged carriage insertion
Relevant predecessors:
- `docs/tasks/TASK26_TRUCK_BOX_PUSH_IN.md`
- `docs/tasks/TASK27_FIVE_CUBE_CENTER_INSERT.md`
- `isaac/scripts/task26_truck_box_scene.py`
- `isaac/scripts/task26_truck_box_bridge.py`
- `isaac/scripts/task27_five_cube_center_insert_scene.py`
- `isaac/scripts/task27_five_cube_center_insert_bridge.py`
- `ros_ws/src/fr3_dual_palletize/src/task26_truck_box_push_in.cpp`

Validated topology:
```text
bilateral shared transport to PRE_PUSH
→ release both side suctions
→ move helper arm out of the insertion work zone
→ one pusher arm regrasp Cube -X face
→ single-arm +X segmented insertion
→ deep-wall support / gap check
→ retreat
```

For the Task27 center Cube the validated default pusher was the **right arm**; the helper was parked outside the insertion work zone. The source explicitly prechecked the complete chain “regrasp → +X push → exit” before selecting a redundant IK/RRT candidate.

Historical Task27 center-Cube results include:
- target Cube center `x=1.100 m`;
- physical final center near `x=1.099–1.100 m`;
- deep-wall gap approximately 0.3–0.6 mm in successful runs;
- segmented +X insertion completed;
- final retreat/home completed.

These results establish engineering feasibility of the staged topology. They do **not** automatically freeze current scientific success thresholds or prove P3 force-control performance.

## What must NOT be imported blindly

Do not treat the full five-Cube Task27 application as the common scientific benchmark. The following remain legacy/stress-test scope:
- five-Cube scheduling;
- neighbor-Cube placement sequence;
- batch handoff;
- side compaction of the four reference Cubes;
- old execution-speed tuning;
- old per-run success as a new statistical benchmark.

Do not inherit old force/torque readings as calibrated TCP wrench data. TASK10-IS still owns wrench semantics.

## Reproduction benchmark mapping

```text
Benchmark A — TIGHT_TRANSPORT
START (already bilateral-held)
→ PRE_PUSH
scientific focus: closed-chain / object-level dual-arm coordination

Fixed engineering handoff
PRE_PUSH
→ release bilateral side suction
→ right-arm -X rear regrasp
→ left helper park
→ INSERT_READY

Benchmark B — CONSTRAINED_INSERTION
INSERT_READY
→ single right-arm +X insertion
→ TARGET
scientific focus: position-only vs hybrid force-position / jam / recovery
```

The handoff is a **common fixed engineering precondition**, not a scored P3 algorithm. All compared P3 methods must start from the same INSERT_READY state once frozen.

## Why D039 changed the draft topology

The previous reproduction draft incorrectly kept both side tools rigidly attached while driving the Cube all the way to `x=1.100`. That was not the validated Task26/27 workflow. Isaac then correctly exposed wrist/deep-wall interference at TARGET (about -3.016 mm link7 contact separation), while the original staged workflow avoided carrying both wrists into the deep end.

The failed bilateral-to-TARGET evidence remains valid evidence for the superseded topology and must not be deleted.
