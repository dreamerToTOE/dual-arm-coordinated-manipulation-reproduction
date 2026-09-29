# P2 — Cooperative Pose/Force Control

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
