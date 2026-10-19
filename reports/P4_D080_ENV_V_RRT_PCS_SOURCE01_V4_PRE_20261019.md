# D080 环境 V：RRT+PCS SOURCE01 V4 冻结前审查

本文件冻结一次且仅一次环境 V RRT+PCS source solve。V4 BUILD02 已通过独立工程后审（2 TU 编译、1 次链接），其状态仍为 `BUILT_NOT_QUERIED`；本次 source 运行使用同一 V4 ELF，不重新编译。

- 环境/方法/规划器：V / PCS / RRT
- 实现来源：`CORRECTED_COMAU_APC_ALIGNED_V3_RECONSTRUCTED_A02_ORIGINAL_RRT_CONTROL`
- 端点：已保存的 V A02 重建端点；主动关节保持不变，aligned 离散碰撞策略独立合格。原生 TCP 不一致、连续碰撞未证均单列。
- 随机条件：seed=7，RRT range=0.2 rad，goal bias=0.05，单次 10 s solve。
- 资源上限：30 s wall、60 s CPU；工作保留阈值 25 s / 50 s；单 source process、单 source solve。
- 通过边界：source exact/approximate、完整原始输出、trace、回溯和成本必须保存；source exact 只产生候选，不等同端到端路径成功。候选随后必须独立核验闭链、IK 分支、关节限位、原始/对齐碰撞和路径回溯。
- 禁止事项：不放宽几何、碰撞、安全带、闭链或资源判据；不执行正式统计、不追加 VI、不启动 P2/Isaac/FR3。

V4 prior 使用 `results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V42.json`，charged wall=1171.2983912569775 s，CPU=1004.4874179999999 s。正式 Table I 仍为 0/18000；本次是资格性单次 source solve，不计入正式统计。
