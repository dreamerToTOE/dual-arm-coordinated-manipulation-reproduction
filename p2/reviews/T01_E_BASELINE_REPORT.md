# T01-E 优化前等价性基线（冻结）

- **冻结时间**：2026-10-19
- **代码版本**：`d8efdb8c700a`
- **种子**：20261019
- **夹具**：20（11 数值 + 9 异常）
- **数组**：444（`arrays.npz` bacbc46fab37…）
- **生成命令**：`/usr/bin/python3.10 p2/tools/t01e_baseline.py`
- **耗时**：0.40 s
- **自检**：PASS：444/444 位相同

本基线在任何优化之前冻结，用于 O1/O2 的逐元素等价性判定。它保存完整输入、状态、`f/A/F/Lw/Qd`、`P0/P_pred`、接触与 grasp-rate 数组、六类观测的 `H/z/residual`，以及一次完整更新的创新、迭代次数与后验协方差；不以范数或哈希代替矩阵比较。

## 1. 数值夹具

| ID | 模式 | ‖τ‖ (Fro) | ‖v‖ (m/s) | rank(W) | 更新迭代 | 说明 |
|---|---|---|---|---|---|---|
| C01_nominal_pivot | pivot/pivot | 4.16e-17 | 0.00e+00 | 6 | - | frozen reference point; matches the T02 golden case |
| C02_moving_pivot | pivot/pivot | 5.66e-02 | 3.74e-02 | 6 | - | object 0.037 m/s and 0.19 rad/s equivalent, both EE twists nonzero |
| C03_elastic_tight | tight/tight | 6.82e-02 | 1.34e-02 | 6 | - | pad deformation about 1.5 mm / 20 mrad, inside the 5 mm / 0.15 rad domain |
| C04_elastic_sliding | sliding/sliding | 6.82e-02 | 1.34e-02 | 5 | - | elastic + moving; the small pose offsets tilt the sliding axes, rank 5 |
| C05_rank_collinear_sliding | sliding/sliding | 4.16e-17 | 0.00e+00 | 4 | - | nominal collinear sliding axes; the single rank-4 configuration |
| C06_rank_boundary_sliding | sliding/sliding | 1.00e-03 | 0.00e+00 | 5 | - | 1 mrad tilt of one sliding axis; expect rank 5 instead of 4 |
| C07_small_angle | pivot/pivot | 5.49e-07 | 0.00e+00 | 6 | - | 1e-7 m / 1e-7 rad offsets |
| C08_near_pi | pivot/pivot | 4.44e+00 | 0.00e+00 | 6 | - | D rotation pi-1e-3 / pi-2e-3; outside the pad domain, Jacobian coverage only |
| C09_residual_update | pivot/pivot | 5.66e-02 | 3.74e-02 | 6 | 2 | visual1 observation offset by 10 mm / 37 mrad, one iterated update recorded |
| C10_mixed_pivot_sliding | pivot/sliding | 6.82e-02 | 1.34e-02 | 6 | - | third H combination with motion and elastic contact |
| C11_force_dominated | tight/tight | 8.74e-02 | 5.39e-03 | 6 | - | about 3 mm / 60 mrad pad deformation, close to the domain gate |

## 2. 异常输入夹具

这些夹具保证优化后公共 API 仍然拒绝无效输入；消息必须逐字一致。

| ID | 被拒绝 | 异常类型 | 消息（截断） |
|---|---|---|---|
| E01_non_se3 | True | GeometryDomainError | not SE3; no automatic normalization |
| E02_nan_velocity | True | ObservationDomainError | INVALID_FINITE_VECTOR |
| E02b_nan_velocity_validate_state | True | ValueError | NONFINITE_STATE |
| E03_unknown_mode | True | GeometryDomainError | unknown contact mode |
| E04_nonorthonormal_H | True | GeometryDomainError | H must have independent orthonormal rows |
| E05_bad_covariance | True | ObservationDomainError | INVALID_OBSERVATION_COVARIANCE |
| E06_stale_timestamp | True | EstimatorDomainError | STALE_FUTURE_OR_WRONG_DELIVERY_TIMESTAMP |
| E07_nonpositive_dt | True | EstimatorDomainError | INVALID_PREDICTION_INTERVAL |
| E08_non_se3_log | True | GeometryDomainError | not SE3; no automatic normalization |

## 3. 比较方法与判据

`p2/tools/t01e_compare.py --baseline … --candidate … --output …` 逐数组输出 `max_abs`、`max_rel`、最大差异位置与是否位相同。

严格项（无浮点重排）：位相同。其余：绝对/相对均 ≤1e-12。元数据（迭代次数、收敛、异常类型与消息、`rank(W)`）完全一致。

自检：同一代码生成两次，444/444 数组位相同，失败 0 项，最坏绝对差 0.0e+00。

## 4. 哈希记录

| 对象 | SHA256（前 12 位） |
|---|---|
| baselines/p2_pose_force/contact_geometry.py | 47557da9189d |
| baselines/p2_pose_force/estimator.py | 5c045a79b210 |
| baselines/p2_pose_force/mechanics.py | 34831b2cd371 |
| baselines/p2_pose_force/observations.py | cc902ea09239 |
| configs/p2_closed_loop_protocol_v3.json | 0de8477faaa5 |
| p2/tools/t01e_baseline.py | 92224a52b720 |
| p2/tools/t01e_compare.py | c34f7b9ba164 |
| arrays.npz | bacbc46fab37 |

## 5. 局限

C08（近 π）有意落在 pad 域外，只用于 Jacobian/异常覆盖，不得进入控制实验。

本基线只冻结**单步**算子与单次更新，不含时间积分；长时行为属 T03/T04。

基线不是论文实验结果，不构成任何复现成功的证据。

