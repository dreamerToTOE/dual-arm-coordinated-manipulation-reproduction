# P4 NR constrained bidirectional search — TASK06

Pure offline search orchestration. It calls existing `project()` and `connect()`;
it has no MoveGroup planner, robot command, simulator, trajectory timing or sensor.
See [pre-experiment source audit / protocol](../../reports/TASK06_PRE_TASK_PROTOCOL.md).

## Pseudocode (source-audited NR branch)

```text
qualify exact q_start and q_goal via existing TASK05 connect(q,q)
initialize start and goal trees with qualified roots
initialize mt19937_64 with caller's actual seed
for iteration in [0, max_iterations):
    check total node and compute budgets
    alternate primary and secondary trees
    sample q_rand uniformly in complete native 14D position bounds
    primary_node = nearest(primary, q_rand) in Euclidean ambient joint space
    first = GROW(primary, primary_node, q_rand, EXTEND, <=101 attempts)
    if budget termination: return failure evidence
    second_node = nearest(secondary, first.last_node.q)
    second = GROW(secondary, second_node, first.last_node.q, CONNECT, <=501 attempts)
    if budget termination: return failure evidence
    if second reached its exact existing target:
        backtrack qualified parent edges in both trees
        reverse goal-tree ordered TASK05 path prefixes
        join at identical meeting q, remove only duplicated meeting point
        return dense TASK05-verified path + provenance
return ITERATION_LIMIT, no solution, all failure evidence retained

GROW(tree, parent, target, mode, cap):
    repeat at most cap:
        check global compute/node budgets
        steer raw candidate toward target by <=0.20 rad joint L2
        if EXTEND or target outside raw range:
            call original TASK04 NR-SVD projection
            reject failed projection or correction >0.25 rad
        else:
            use exact existing target, no projection/snap
        reject nonfinite, extension >0.45 rad or progress <=1e-12 rad
        edge = original TASK05 connect(parent.q, candidate)
        check compute budget after the bounded existing callback
        if any edge check fails: return last accepted node + failed local prefix
        insert candidate with parent and full accepted edge evidence
        if raw target within range: return reached
    return last accepted node, not reached
```

Both growth modes repeat in audited author NR code; this is not a single-step
ordinary RRTConnect with repair at the end. A trapped first growth still permits
the secondary tree connection, as in author code. No direct-return shortcut,
goal bias, path smoothing, shortcutting, weighted metric or learned sampler.
Identical caller endpoints are validated; the generic loop remains in effect.

## Interfaces and evidence

`p4::plan(start,goal,native_lower,native_upper,C_Jc,native_margin,FCL,PlannerOptions)`
returns `PlannerResult`. Caller supplies exact14q, in original left7/right7 order,
rad. G, transforms and C/Jc are the accepted TASK03 definitions; no new Euler
residual/FK. Native bounds are read-only from the same RobotModel.

Each root has original TASK05 state qualification. Every inserted node carries a
parent and index into `attempts`, whose projection and full `ConnectionResult`
include q/residual/margin/native contacts and ordered accepted leaf edges. Failed
edge prefixes are diagnostics, never successful global solutions. Returned dense
points reference exact checked points and retain reversed goal-side provenance.
JSON serializers reuse TASK05 projection/connector serialization.

Counters explicitly separate candidate NR and RBS-midpoint projections/failures,
accepted start/goal edges, rejected connections, native collision adapter queries,
positive/unavailable results, NN comparisons and RNG draws. One native collision
adapter query performs self and world checks; count is **state queries**, not internal
FCL BVH traversals. Metrics are dense-path joint L2 length, milestone length,
max/RMS position and rotation C norms, minimum native margin and adjacent L2/Linf.

Actual uniform sampler uses `(mt19937_64() >> 11) * 2^-53`, in joint order.
Linear NN selects earliest inserted node on exact ties. No implementation-dependent
distribution, reseeding during search or hashing seed without using it.
Same seed/input determinism is verified on status, states/parents/path, samples and
search counters; compute timings and native contact list ordering are excluded.
Wall cutoff can cause different progress; such a repeat is a failed gate, not hidden.
Budget checks cannot preempt an existing projection/FCL callback midway: its own
iteration/point caps remain fixed, then search checks elapsed time immediately.

Minimum collision distance is `UNAVAILABLE_NATIVE_DISTANCE_NOT_QUERIED`.
No distance/positive clearance inferred from free states. Returned geometric path
is **not** an execution trajectory or rigorous continuous swept-volume guarantee.

## Fidelity boundary

ORIGINAL: NR/RBS bidirectional planning with source-derived growth order.
ADAPTATION: actual14DoF FR3, existing strict SE(3) residual and native MoveIt/FCL
instead of author's12DoF industrial arms/KDL/PQP.
ENGINEERING: finite inner/global budgets, exact endpoint checks, native limits,
progress/correction/accepted-step bounds, stable NN and log organization.
Inherited explicitly disclosed difference: accepted TASK04 rank<6 rejection and
TASK05 locality guards are conservative; **no paper singularity-passage or original
benchmark performance conclusion** follows from this offline slice.

## Reproduce offline only

```bash
cd /home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-reproduction
source /opt/ros/humble/setup.bash
source /home/ubuntu2004/lmy/dual-arm-embodied-palletizing-task01-foundation/ros_ws/install/setup.bash
PYTHONPATH="${PWD}:${PYTHONPATH}" /usr/bin/python3 scripts/run_task06_offline.py \
  --run-id YOUR_NEW_TASK06_RUN_ID
```

Sourcing library/mesh paths starts no ROS service. Runner protects immutable
protocols/fixtures/old results/core algorithms/meshes/legacy assets, uses exclusive
TASK02 run logger and typed results, and losslessly gzips full trial evidence.
Run ID must be new; never overwrite historical evidence. No Isaac required.
