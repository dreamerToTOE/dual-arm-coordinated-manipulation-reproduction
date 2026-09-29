# TASK08-MJ — P2 Object Pose Controller

Status: TODO

## Goal
Control the shared cube pose in MuJoCo without yet regulating internal wrench.

## Codex actions
- Use common SE(3) pose error.
- Implement object-level pose controller from P2 reproduction card/paper.
- Map desired object motion to arm commands through common interfaces.
- Test translation, orientation and combined trajectories.

## Metrics
object pose RMSE, settling time, overshoot, contact stability.

## PASS
Stable object trajectory tracking across frozen test set.
