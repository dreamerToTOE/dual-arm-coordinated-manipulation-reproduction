# TASK07-MJ — P2 Grasp Matrix + Internal Wrench

Status: TODO

## Goal
Validate wrench decomposition for two FR3 end-effectors acting on one rigid cube.

## Codex actions
- Build object/grasp frames.
- Implement grasp matrix W.
- Stack left/right contact wrenches.
- Compute object external wrench and internal-wrench component/null-space term.
- Create MuJoCo tests with symmetric squeeze, common-direction push, asymmetric loading.

## PASS
Tests clearly distinguish external motion-producing wrench from internal stress-producing wrench and match analytical expectations.
