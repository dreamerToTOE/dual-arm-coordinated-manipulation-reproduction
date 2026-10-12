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

## 逐篇论文的真实场景应用关口（D055）

每个 `baselines/pN_*` 核心算法必须经本身的数学/离线证明后，通过 `platforms/isaac_ros2/` 的**薄适配**连接现有 FR3/Cube/车厢任务；场景无命令验证、授权执行及同场景实验分开交付。P2/P3 的 MuJoCo 适配不能冒充 Isaac 实测。统一参考 [路线](REPRODUCTION_ROADMAP.md)。

当前 P4 新增 TASK06-IS-A/B/C；A 仅核对场景数据和离线规划，不能启动真实运动。复用 Task26 场景/Bridge/双臂执行器时保留旧成熟实现的边界，正式接入和新物理运行要单独授权。

实验数据分为：离线数学/规划、只读场景对齐、实际物理执行、获得原生同一步认证的科研测量。四类不可相互替代；TASK02-D 的物理步采样资格未证实时，时间相关科研指标不可用，不能编造。

## Design constraint
A metric must not be implemented inside one baseline. A benchmark threshold must not live inside a paper algorithm. A simulator-specific API must not leak into platform-independent baseline logic unless documented as unavoidable.
