# TASK06 — constrained RRTConnect offline delivery and acceptance gap

2026-10-12; baseline `91a1adc`; branch `task06-p4-constrained-rrtconnect`.
Tested source: `29a9d5cabec8259827c43aaded5be230024b13f6`.
**TASK06 = PARTIAL / STOP FOR USER REVIEW.** TASK02 remains IN_PROGRESS,
TASK02-D PARTIAL / DEFERRED, Benchmark DRAFT / NOT FROZEN. TASK07 not started.

## POST-TASK REPORT

### Objective and minimum sufficient evidence

Compose accepted real-FR3 C/Jc/FK, Newton–SVD projection and RBS/FCL into genuine
bounded bidirectional constrained search. No ordinary MoveIt RRTConnect followed
by endpoint repair. No Isaac, ROS planning service, robot or Task26 invocation.

**Minimum sufficient evidence achieved: NO for the complete predeclared protocol.**
Nontrivial two-tree search, real FCL edge checks, negative tests and fixed-seed
reproducibility are demonstrated. One independent-obstacle acceptance requirement
fails: direct TASK05 connection is rejected by its unchanged projection-locality
guard, **not specifically by collision**. Do not silently recategorize this result
or call complete TASK06 PASS CANDIDATE.

### Completed implementation and reuse

- [Search core](../baselines/p4_closed_chain/constrained_rrtconnect.cpp) and
  [contract](../baselines/p4_closed_chain/constrained_rrtconnect.hpp): two trees,
  explicit 14q endpoints, native joint-bound sampling, actual seeded mt19937_64,
  stable Euclidean nearest neighbor, bounded steering, accepted TASK04 projection,
  accepted TASK05 validation of **every inserted edge**, exact meeting/backtracking,
  bounded nodes/iterations/compute and explicit rejection/budget reasons.
- [Pseudocode and interface](../baselines/p4_closed_chain/CONSTRAINED_RRTCONNECT.md),
  [primary-source/pre-task/prior-asset audit](TASK06_PRE_TASK_PROTOCOL.md) and
  [predeclared protocol](../configs/engineering/task06_constrained_rrtconnect_test_v1.json).
  Protocol committed/pushed as `877decd` before planning experiments; SHA256
  `74a1aa3864da4e3527b6889bfa04b41c7226010a58b8d384e71bf9ce3e6ab32c` unchanged.
- Existing TASK03 model adapter adds only a native position-bounds getter; existing
  TASK05 collision adapter adds only private test-box insertion through its native
  PlanningScene API. Original C/Jc/FK/projection/RBS/FCL semantics are unchanged.
  Full adapter-only diff is saved with the run; no new FK or collision engine.
- [Real-model harness](../platforms/offline_moveit/task06_constrained_rrtconnect/model_test.cpp),
  [complete evidence serializer](../platforms/offline_moveit/task06_constrained_rrtconnect/evidence.hpp),
  [synthetic tests](../tests/task06_constrained_rrtconnect_math.cpp) and
  [offline runner](../scripts/run_task06_offline.py). Link/import existing TASK02
  RunMetadata/RunLogger/BenchmarkResult, existing TASK03–05 and native MoveIt/FCL.
  Logs preserve sampled targets, projections, failed connections/prefixes, tree
  parents, dense paths, source/qualification, counters and deterministic payloads.

Original native model, grasps, meshes, table/walls, SRDF ACM, zero native padding,
unit scale and empty carried-Cube touch-link list retained. Legal tool-mount
contacts remain those already in SRDF; no tool/Cube exemption or new ACM entry.
The held Cube is the existing native AttachedBody representation for **offline
geometry**, not evidence of physical suction/shared-hold stability.

### Method / pseudocode

```text
qualify exact q_start and q_goal via unchanged TASK05 connect(q, q)
create start tree and goal tree, set the actual RNG seed
until bounded node / outer-iteration / compute limits:
    sample one uniform 14q in original native bounds
    alternate the primary tree
    nearest -> repeat bounded raw steer -> TASK04 NR -> TASK05 RBS/FCL -> add edge
    grow the other tree toward the last qualified first-tree node
    use the exact existing target on final connect, do not independently project it
    if exact qualified tree meeting:
        backtrack parents, reverse goal-side dense edges, join once at meeting q
        return the entire qualified discrete path and provenance
return explicit failure; retain trees and only the qualified failed-edge prefix
```

Author-source repeated-grow caps 101/501 are retained. Engineering controls:
raw step .20 rad, projected-candidate correction <= .25 rad, accepted extension
<= .45 rad, progress > 1e-12 rad, <=600 nodes, <=800 outer iterations and <=20
compute wall-seconds. Budget checks are cooperative between bounded existing
calls, not hard preemption of arbitrary user callbacks. No bias, smoothing,
shortcuts, prescreen selector or direct-return path was added. Existing TASK05
midpoint correction <= .020 rad and adjacent L2/Linf <= .010 rad are unchanged.
Position/rotation engineering convergence is independently <=1e-8 m / 1e-8 rad;
these are not frozen scientific Benchmark success thresholds.

### Commands actually run

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/install/setup.bash
PYTHONPATH="${PWD}:${PYTHONPATH}" /usr/bin/python3 scripts/run_task06_offline.py \
  --run-id 20261012_TASK06_constrained_search02
```

Sourcing dependencies does not launch ROS. No ROS node/context/planning service,
Isaac or controller was started. Full command argv, finite timeout and exit status
are in [summary](../results/20261012_TASK06_constrained_search02/summary.json).
The already-used run-id is immutable; the command above documents the actual run,
not authorization for additional experiments.

First invocation `constrained_search01` at `ba20c98` failed **compilation only**
(implicit JSON/Eigen conversion and ambiguous JSON-key overload); no real planning
trial occurred. One explicit-conversion fix in `29a9d5c` leaves algorithm/protocol
unchanged and persists the predeclared repeat payload/fingerprint. The complete
fixed scientific suite was then run exactly once; no outcome-driven retry/tuning.
Both [compile-negative run](../results/20261012_TASK06_constrained_search01/summary.json)
and [final run](../results/20261012_TASK06_constrained_search02/metadata.json) remain.

### Regression and negative results

- TASK02 A/B/C: 72 Python tests PASS.
- CTest: 4/4 PASS; TASK03/04/05/06 synthetic assertions: 93 / 108 / 300 / 2757.
- Real FR3 TASK03 Jacobian: 435 configurations PASS for derivative verification.
  **Original historical precision FAIL remains FAIL:** max .435028 micrometres,
  219/293 above unchanged .05-micrometre gate. Do not substitute new projected q.
- Real TASK04: required 194/194 neighboring and independent 293/293 original-grasp
  projection diagnostics PASS; real TASK05: 10 positive connections and three
  bound/closure/native-FCL negatives PASS. Prior accepted semantics retained.
- New native out-of-bounds root is START_REJECTED. New actual box-at-TCP root is
  START_REJECTED with genuine FCL COLLISION/tool and attached-Cube evidence.
- Synthetic tests cover projection failure, unqualified/failed local connection,
  unavailable collision evidence, joint bounds, node/iteration/time exhaustion,
  grow caps, exact meeting/reversed goal-side edges, parent/path provenance and RNG.
  Synthetic backend results are not real collision acceptance.

Configure/build/regressions all exit 0. The final real-suite checker exits **1**
for the one predeclared acceptance gap below, not a compiler failure/crash.
`summary.software_ok=false` is the runner's all-commands-zero aggregate; it does
not mean the software regression tests failed. Typed result is FAILURE at
OFFLINE_SEARCH_ACCEPTANCE with UNQUALIFIED measurement; task-level delivery is PARTIAL.

### Fixed real-FR3 search results

Exactly 18 plan calls: three scenes x seeds 7/41/20261012 x two repeats.
Rows give common status/counts/path length of both repeats; times are first/repeat
**plan-function wall costs only**, excluding load/reference checks, dense independent
revalidation, serialization/compression. Not physical duration or a paper benchmark.

| Scene / stored endpoints | Seed | Both repeats | Nodes | Solution tree edges | Dense points | Dense q length (rad) | Wall seconds (0 / 1) |
|---|---:|---|---:|---:|---:|---:|---|
| Simple 0 -> 1 | 7 | SUCCESS | 107 | 105 | 2037 | 12.797191 | .250113459 / .243725454 |
| Simple 0 -> 1 | 41 | SUCCESS | 22 | 20 | 593 | 3.585136 | .075039405 / .073166141 |
| Simple 0 -> 1 | 20261012 | SUCCESS | 29 | 27 | 629 | 4.402728 | .077852604 / .078191579 |
| Nontrivial 0 -> 100 | 7 | SUCCESS | 106 | 104 | 2005 | 12.718907 | .240979937 / .243172804 |
| Nontrivial 0 -> 100 | 41 | SUCCESS | 22 | 20 | 593 | 3.586426 | .074799013 / .072158639 |
| Nontrivial 0 -> 100 | 20261012 | SUCCESS | 29 | 27 | 629 | 4.422852 | .077603617 / .088054484 |
| Private obstacle 0 -> 100 | 7 | NODE_LIMIT | 600 | 0 | 0 | unavailable | .771383094 / .761820461 |
| Private obstacle 0 -> 100 | 41 | NODE_LIMIT | 600 | 0 | 0 | unavailable | .811210472 / .815149439 |
| Private obstacle 0 -> 100 | 20261012 | SUCCESS | 553 | 148 | 2261 | 15.769458 | .883388844 / .870731099 |

Nontrivial endpoint ambient L2 distance is .921690475 rad; its unchanged direct
TASK05 connector does not qualify. Private obstacle success uses 49 sampled
targets/outer iterations, 93 start-tree +458 goal-tree accepted edges (551 total),
647 growth attempts, 646 candidate NR and 6070 RBS midpoint projections; 90 of
7354 native state queries reject actual collisions. Both trees genuinely grow,
every inserted edge is validated, and final dense points are independently checked.
No failed path is returned as a valid solution.

Across 18 calls: 50,602 projection calls /26 projection failures; 55,118 native
FCL **state queries** /392 positive-collision queries. These counts exclude direct
reference connectors and independent post-search dense revalidation. One state
query invokes existing native self/world checks, not a measured count of FCL
internal primitive/BVH queries. Full per-trial counters/residual max/RMS/margins/
q length and edge source are in [planning metrics](../results/20261012_TASK06_constrained_search02/planning_metrics.json).

Across successful paths: maximum position residual 9.917604088e-9 m, rotation
9.983855172e-9 rad; smallest native joint margin .001980096 rad. Small positive
margin is **not** a robustness reserve or physical safe-tracking claim. Dense
adjacent L2/Linf remain within unchanged TASK05 .010-rad engineering limits.
Sampling may produce long paths even for close endpoints (no smoothing/optimality
in this slice); no efficiency or optimal-path claim is made.

Rejected candidates in obstacle search include genuine collisions of the private
box with left tool, right tool and carried Cube; also table/wall collisions.
Those are recorded failed attempts, **not** collisions on the accepted solution.
Private geometry is only in an independent offline PlanningScene, not Benchmark.

### Exact unmet acceptance item — do not reinterpret

Fixed private box: center (.638888888888889,0,.3355555555555556) m,
size (.020,.180,.120) m, identity orientation. It was fixed in `877decd`, never
moved/resized after results. Native roots qualify; seed 20261012 finds a path.

However, both nontrivial and obstacle direct 0 -> 100 connectors return:

```text
status                  = PROJECTION_JUMP
failed_point_index      = 2
role / depth            = PROJECTED_MIDPOINT / 1
NR status               = CONVERGED (3 accepted updates)
midpoint correction L2  = 0.08694933778810582 rad
unchanged allowed L2    = 0.020 rad
collision evidence      = null (not queried at this rejected midpoint)
```

This is the existing TASK05 locality guard, **not** failure of NR convergence and
**not** a measured direct-path collision. Remaining unchecked portions cannot be
assigned a collision verdict. The obstacle fixture did not produce the specific
predeclared direct-collision test, although real collision rejections and a genuine
multi-node solution exist. Full raw direct evidence:
[direct_obstacle.json.gz](../results/20261012_TASK06_constrained_search02/direct_obstacle.json.gz).
Two seeds exhausting the fixed 600-node budget do not prove geometric impossibility.

### Determinism, provenance and original evidence

All nine same-input/seed repeat pairs have **exactly matching deterministic JSON
payload SHA256**, path, termination status and search counters. Actual RNG is
`std::mt19937_64(seed)` with explicitly defined binary53 uniform mapping; suite seed
is UNSET because it contains multiple independently SET trial seeds. No fake seed.
Wall time and native raw-contact arrays are excluded from repeat equality, but
remain in full raw artifacts; this does not drop their collision verdict/qualification.
See [fingerprints](../results/20261012_TASK06_constrained_search02/deterministic_fingerprints.json)
and [trial metadata](../results/20261012_TASK06_constrained_search02/trial_metadata.json).

Read-only saved-evidence audit: 40 artifact hashes, 35 source/mesh hashes, 23
lossless decompressed raw hashes/byte lengths and 18 deterministic fingerprints
match; nine pairs agree. 536 protected tracked files, eight original meshes and
four predecessor assets unchanged before/after. Audit summary is a separate new
[report JSON](TASK06_EVIDENCE_READBACK.json), not modification of finalized raw logs.
Large original trace JSON is preserved byte-for-byte as `.json.gz`, with original
SHA256/length in summary; no failed evidence discarded or historic run rewritten.
No simulation timestamp, physics step or synchronized measurement invented.
Minimum distance = **UNAVAILABLE_NATIVE_DISTANCE_NOT_QUERIED**, never inferred
positive from no contact. Discrete safety is not continuous swept-volume proof.

### Blockers, budget and escalation

- **TASK-BLOCKING for full predeclared TASK06 acceptance:** independent obstacle
  direct-connector collision qualification missing. Not proven algorithm/model bug.
- **KNOWN LIMITATION:** two obstacle seeds exhaust bounded search; nonoptimal paths;
  inherited rank/locality guards, no continuous collision or minimum distance.
- **DEFERRED:** native post-step clock/reset identity, TASK02-D and later Isaac
  measurement; physical execution/force/suction/full paper performance.
- **LEGACY:** five-Cube Task26/27 application flows are untouched and not evidence here.
- **Attempt budget used:** one compile-only failed invocation, one compile-only
  evidence-based fix; one complete predeclared scientific suite (18 search calls).
  No extra seeds, scene adjustments, acceptance changes or empirical retries.
- **Escalation required: YES for any further acceptance work.** Existing complete
  traces are lower-cost evidence; no new instrumentation/planner run is warranted
  without review. Stop for user decision on scoped acceptance versus a separately
  authorized, predeclared future validation case. Do not change this failed protocol.

### ENGINEERING ESCALATION

- Scientific question: does this fixed suite establish the complete predeclared
  nontrivial constrained-search and obstacle-detour qualification?
- Already established: genuine real-FR3 two-tree paths with native FCL edge checks,
  fixed-seed reproducibility and collision/bound/budget negatives.
- Unknown: a collision-specific direct-connection verdict for the fixed obstacle;
  the unchanged locality guard stops evaluation first.
- Why it matters: that exact verdict was explicitly required before experiments,
  and cannot be inferred from separate rejected search candidates.
- Attempts: one build-only failure/fix and one fixed scientific suite; no retuning.
- Root blocker classification: TASK-BLOCKING for full protocol acceptance; yes,
  still critical to complete TASK06, not to the narrower demonstrated search claim.
- Lower-cost evidence: retained raw direct connector and all tree/FCL traces.
- Recommended action / need user decision: STOP FOR USER review; only the user
  may authorize a new validation scope or accept a narrower stated conclusion.

### Paper fidelity

- **[ORIGINAL]:** paper NR/RBS combination and author-source bidirectional grow,
  project, validate, alternate, connect and backtrack order.
- **[ADAPTATION]:** 14D dual FR3 rigid closure/FK and existing MoveIt/FCL replacing
  the authors' KDL/PQP engineering environment.
- **[ENGINEERING]:** deterministic RNG/NN, explicit finite budgets/progress guards,
  native roots/limits, unchanged accepted numerics, complete file logs/provenance.
- **[DEVIATION, inherited/disclosed]:** accepted TASK04 rank<6 rejection and TASK05
  locality guards are conservative and do not reproduce general singular passage;
  no new method substitution or full P4 performance/fidelity claim.
- **[EXPERIMENTAL]:** private fixed offline obstacle fixture, not Benchmark geometry.

Primary manuscript and pinned author source/versions/license limitations are in
the pre-task audit. Author files are reference-only, not copied/imported code.

### Records and handoff

STATUS, WORKLOG, EXPERIMENT_LOG, BUGS, DECISIONS (D053), USER_FEEDBACK, active task,
README/start-here and P4 progress cards updated; historical entries retained.
Implementation commits `ba20c98`, `29a9d5c`; delivery commit is the subsequent
report/evidence commit on this branch. Existing five unrelated untracked TASK01
logs are preserved and excluded from staging. No generated build/install committed.
Source/document whitespace checks pass. Full staged evidence checks flag original
CMake stdout / captured diff trailing spaces; these raw bytes are deliberately
not normalized or rewritten, preserving their recorded artifact hashes.

**Recommended next step:** review this bounded PARTIAL and exact direct-connection
failure evidence before authorizing anything else. No automatic TASK07, runtime,
additional fixture search, threshold relaxation or Benchmark freeze.
