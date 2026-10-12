# P4 — Closed-Chain Motion Planning

## 2026-10-12 论文式中文汇总（已有数据，不新增实验）

主代理阅读全文P4八页及私有DEFORM范例，六份资料SHA匹配。
[中文可编辑Word](../reports/P4_论文复现汇总.docx) / [PDF](../reports/P4_论文复现汇总.pdf) /
[真实图表数据](../reports/p4_report_assets/README.md)。仅NR路线，RSS/PCS及三法对比尚未完成；
原历史精度FAIL、TASK06整体PARTIAL与B0不能执行均保留，不能宣称完整P4/物理验收。
报告待用户审查，不自动进入P2；私有原文/范例不上传。

Paper: Avishai Sintov, Andy Borum, Timothy Bretl,
*Motion Planning of Fully Actuated Closed Kinematic Chains With Revolute Joints:
A Comparative Analysis*, IEEE RA-L 3(4), 2886–2893, 2018.
DOI: [10.1109/LRA.2018.2846806](https://doi.org/10.1109/LRA.2018.2846806).
[Author's full 8-page manuscript](https://avishaisintov.wordpress.com/wp-content/uploads/2018/06/sintov-pcs.pdf)
and [university publication record](https://experts.illinois.edu/en/publications/motion-planning-of-fully-actuated-closed-kinematic-chains-with-re/).

## TASK06 primary-source search audit and delivery (2026-10-12)

Full manuscript NR/RBS/bidirectional sampling combination and author
[CKCplanning pinned909bd72](https://github.com/avishais/CKCplanning/tree/909bd72fff778aca8682c96f9eb86ae4eb75557b)
`CBiRRT_NR.cpp` grow/connection/backtrack audited before experiments. Ambient
uniform sample -> Euclidean NN -> bounded steer -> NR -> RBS; alternate trees,
repeated101/501growth and exact final target retained. No ordinary MoveIt planner
substitution, upstream code import, optimization/performance or singularity claim.
14D FR3/MoveIt-FCL is ADAPTATION; inherited conservative rank/locality guards are
disclosed differences, not reproduction of general paper singular passage.
Author runtime dependency/defaultNN not fully pinned; repository-wide license absent,
someplanner BSDheaders only, all source REFERENCE_ONLY.
[Complete audit and predeclared protocol](../reports/TASK06_PRE_TASK_PROTOCOL.md).

Offline source29a9d5c finds real multi-node FCL paths and9deterministic repeats.
**TASK06 PARTIAL**: private-obstacle direct connector rejected by projection guard,
not collision as the fixedprotocolrequires. No post-result tuning/fullP4PASS.
[Implementation and results](../reports/TASK06_CONSTRAINED_RRTCONNECT01.md).

## TASK03 primary-source audit (2026-10-09)

Full manuscript inspected. Printed page 2, II-A Eq. (1) defines generic rigid
closure C(q)=0; Eq. (2) separately requires bounds/collision validity. Spatial
closure has six constraints. II-B.2 discusses constraint Jacobian and NR;
printed page 6 IV-A names Orocos KDL/SVD. NR and planning remain later tasks.
Author code [CKCplanning](https://github.com/avishais/CKCplanning) is linked on
printed page 5; it was not imported or patched in TASK03.

[ORIGINAL]: rigid closure requirement and generic constraint framework.
[ADAPTATION]: dual-FR3 explicit fixed TCP→Object transforms, position difference,
local SO(3) log residual and its analytic 6×14 derivative. These exact FR3
formulas do not appear in the original manuscript. [ENGINEERING]: pure Eigen
validation, existing MoveIt FK adapter and finite-difference tests. Do not call
this slice a completed P4 planner reproduction.
[Formula/frames](../baselines/p4_closed_chain/README.md),
[TASK03 evidence and partial acceptance](../reports/TASK03_CLOSURE_CONSTRAINT01.md).

## Problem
Sampling-based planning when valid configurations lie on a closed-chain constraint manifold.

## Reproduction target
- define dual-FR3 shared-object closure residual C(q);
- compute/approximate constraint Jacobian;
- Newton-Raphson/pseudoinverse projection to the constraint manifold;
- constrained local connection with projection at intermediate states;
- integrate with RRT/RRTConnect and collision checks.

## Key measurements
- projection success rate;
- projection iterations/time;
- final closure residual;
- planning success rate/time;
- path length/smoothness;
- collision safety.

## Scope
Reproduce the general projection-based planner path first. Other planning variants from the comparative paper may be added only if needed for a fairer baseline.
