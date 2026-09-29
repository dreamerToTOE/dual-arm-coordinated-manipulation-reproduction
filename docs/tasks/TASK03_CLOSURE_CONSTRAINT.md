# TASK03 — P4 Closure Constraint

Status: TODO

## Goal
Define the shared-object closed-chain constraint for dual FR3.

## Method
For q=[qL,qR], both end-effector/grasp chains must predict the same object pose. Define residual C(q) and constraint Jacobian Jc.

## Codex actions
- Implement FK-based object pose from each arm.
- Define translational + rotational closure residual.
- Implement/verify Jc.
- Add finite-difference Jacobian checks.
- Test valid shared-object states and perturbed states.

## PASS
Residual is near zero on valid grasps; Jacobian check passes within frozen tolerance.
