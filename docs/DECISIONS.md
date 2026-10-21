# DECISIONS

Append-only architectural and scientific decisions.

## D001 — Two-platform strategy
- Date: 2026-09-29
- Decision: Isaac Sim + ROS2 is the final common benchmark; MuJoCo is an auxiliary force/contact laboratory mainly for P2/P3.
- Reason: preserve fair final comparison while accelerating force/contact debugging.
- Impact: baseline algorithms remain platform-independent and use adapters.

## D002 — Baseline-first rule
- Date: 2026-09-29
- Decision: `ours/` remains algorithmically empty until TASK30.
- Reason: derive our method from reproducible evidence and failure cases rather than premature design.

## D003 — P1 数值复现的范围与基线
- Date: 2026-10-21
- Decision: P1 当前阶段只做**算法数值复现**，分支从 `main@a596c973` 建立；不继承 P2/P3/P4/P5 的未合并分支，不做 Isaac Sim / MuJoCo / ROS 2 / 双 FR3 集成。
- Reason: P1 的算法主张（两阶段模式选择、零空间传播、辅助切换）可在纯 CPU 上独立验证；平台集成属于另一类证据，混入会掩盖算法是否被复现。
- Impact: 复现代码放在 `p1/src/`，不触碰 `baselines/`、`platforms/`、`common/`；若将来提升为统一基准基线，再按 AGENTS §9 迁移并单独审查。

## D004 — P1 官方代码按两个快照审计，且不作为算法 oracle
- Date: 2026-10-21
- Decision: 同时审计 `main`（`fe5b49f7`）与 `pre-paper-accept`（`1820a9e8`）及其内核快照；上游实现只用于"实现存在性"与差异定位，不作为正确性 oracle。
- Reason: 主分支删除了 12 个基线与 Task 3–6 场景，但保留了论文的控制器结构；接收前快照含基线但无文档。两者都不完全等于论文式子，且仓库无许可证。
- Impact: 独立 oracle 必须是 SE(3) 复合/有限差分/SVD 零空间；不复制上游源码入库；GPU 路径（模块 G）单列并需单独授权。
