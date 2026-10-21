# P1 — Two-Stage Sampling MPC

Paper: *Real-Time Dual-Arm Cooperative Manipulation Under Multiple Constraints: A Two-Stage Sampling MPC Approach* (IEEE T-RO, 2026).

## Problem
Real-time reactive dual-arm coordination under high-dimensional nonconvex constraints.

## Core method
- cooperative dual task-space with relative/absolute pose variables;
- sampling-based MPC;
- first-stage high-variance exploration;
- k-means mode clustering/selection;
- second-stage lower-variance refinement;
- equality constraints enforced through null-space projection;
- inequality constraints handled by sampling rejection/clamping/cost shaping;
- auxiliary controller near steady state;
- GPU acceleration.

## Reproduction target
1. Reproduce upstream example at pinned commit.
2. Port/adapt to dual FR3.
3. Enforce shared-object relative-pose constraint.
4. Reproduce two-stage exploration/refinement.
5. Evaluate collision handling and real-time compute.
6. Integrate with Isaac Benchmark A.

## Fidelity warning
Do not call a generic MPPI controller “P1 reproduction” unless two-stage mode handling and equality-constraint treatment are implemented and documented.

## 2026-10-21 补注（不改写上方历史表述）
G0 研究已完成，入口为 `p1/P1_PAPER_STUDY.md`。三处需要修正的立项期判断：
1. "Reproduction target" 把算法复现与双 FR3/Isaac 集成排成一条线；G0 的结论是两者是不同类证据，数值复现应独立完成（见 `p1/P1_IMPLEMENTATION_PLAN.md` §1）。
2. 论文式 (8) 印为 $x_2^*x_{r/2}$，几何自洽读法与官方内核均为 $x_2\sqrt{x_r}$（SE(3) 螺旋中点），见 `p1/P1_EQUATION_AUDIT.md` §2.1。
3. 上游 `main` 已删除表 II 的 12 个基线；基线只存在于 `pre-paper-accept` 快照，见 `p1/P1_OFFICIAL_CODE_AUDIT.md` §1.3、§6。
