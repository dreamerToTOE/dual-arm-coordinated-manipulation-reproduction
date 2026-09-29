# Architecture V2

## Design objective
Separate **paper algorithms**, **platform adapters**, **shared scientific infrastructure**, and **experiments** so one method can run on multiple platforms without duplicate implementations.

## Layers

### 1. references/
Structured paper cards: problem, equations, assumptions, experiments, code status, reproduction scope and known deviations.

### 2. common/
Platform-independent code:
- `interfaces/`: state/command/result contracts.
- `kinematics/`: FK/Jacobian/relative pose/closure residual.
- `dynamics/`: dynamics utilities needed by force control.
- `geometry/`: frame transforms and object/carriage geometry.
- `grasp/`: grasp matrix, external/internal wrench decomposition.
- `collision/`: unified collision-distance API.
- `metrics/`: benchmark metrics.
- `logging/`: run metadata and artifact writer.

### 3. baselines/
Paper methods only:
- `p4_closed_chain/`
- `p2_pose_force/`
- `p3_hybrid_insertion/`
- `p5_qp_coordination/`
- `p1_sampling_mpc/`

### 4. platforms/
#### MuJoCo
Fast contact/force experiments for P2/P3. It must expose the common interfaces and must not own the paper algorithms.

#### Isaac + ROS2
Final dual-FR3 full-system benchmark, MoveIt/FCL integration, contact sensing and execution.

### 5. benchmarks/
- `transport/`: Benchmark A.
- `insertion/`: Benchmark B.
- `unified/`: batch experiment definitions and cross-method comparison.

### 6. results/
Each run:
```
results/<timestamp>_<TASK>_<run-id>/
  metadata.yaml
  config.yaml
  metrics.json
  trajectory.csv
  wrench.csv
  collision.csv
  stdout.log
  plots/
  videos/
```

### 7. third_party/
Pinned upstream paper code, license and patch notes. Prefer adapters, avoid source mutation.

### 8. ours/
Reserved until TASK30 baseline freeze.

## Data flow
```text
benchmark config
   ↓
platform adapter ──→ state/interfaces
   ↓                    ↓
paper baseline ← common math/collision/metrics
   ↓
command
   ↓
platform execution
   ↓
common logger/metrics
   ↓
results + comparison
```

## Design constraint
A metric must not be implemented inside one baseline. A benchmark threshold must not live inside a paper algorithm. A simulator-specific API must not leak into platform-independent baseline logic unless documented as unavoidable.
