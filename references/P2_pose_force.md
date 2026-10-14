# P2 — Cooperative Pose/Force Control

## 2026-10-14 D068：接触模型获准、有限资格与协议冻结

[模型推导](../reports/P2_CONTACT_GEOMETRY_DERIVATION_RENDERED.md) · [冻结协议](../reports/P2_CLOSED_LOOP_FROZEN_PROTOCOL.md) · [资格交付](../reports/P2_CONTACT_GEOMETRY_POST_TASK.md)。
式15替为用户批准的spatial-free Log闭合；原力9/10/11/12与控制20/21/25保留。
68/68仅接触几何资格，原run01不足/修正1保留，小修1/3余2；完整IESEKF/物体动力学/控制尚未实现，闭环0。
下方D067待裁决为历史，当前模型批准已明确。

## 2026-10-13 原文审计进展（D067）

[P2全文/公式审计](../reports/P2_ORIGINAL_PAPER_AUDIT.md) · [闭环协议草案](../reports/P2_CLOSED_LOOP_EXPERIMENT_PROTOCOL.md) · [任务卡](../docs/tasks/P2_PAPER_AUDIT_AND_PROTOCOL.md)。
原文八页、式1–26/图1–9/表I–II已核对。原物块A和软接触模型优先，不强制FR3/场景。
式15自由抓取坐标更新存在几何一致性争议；式22有限弹性导数有左右Jacobian疑点；协议不可执行，待用户裁决。
exp2仅KP=0、前馈保留；exp4仅模型K失配；主实验不能用GT或纯hdot替代42维估计/物体动力学。旧数学模块不是闭环复现。

Paper: *Cooperative Object Transport and Assembly: Pose/Force Control by Visual-Tactile Feedback* (IEEE RA-L, 2026).

## Problem
Track the pose of a common workpiece while minimizing/regulating internal stress/wrench during cooperative dual-arm manipulation.

## Core ideas
- object pose represented on SE(3);
- robot-object interaction/contact model;
- grasp matrix;
- external vs internal wrench;
- object-pose controller;
- internal-force controller;
- visual-tactile state estimation / calibration in the full paper.

## Reproduction scope
### Core
- grasp matrix and wrench decomposition;
- object-pose control;
- internal-wrench regulation;
- combined pose + internal-force experiment.

### Adaptation
First MuJoCo/Isaac version may use simulator ground-truth object pose and contact wrench instead of full visual-tactile IESEKF.

This omission must be reported; it is not a full perception-stack reproduction.
