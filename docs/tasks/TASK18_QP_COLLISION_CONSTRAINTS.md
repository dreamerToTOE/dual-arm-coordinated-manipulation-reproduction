# TASK18 — P5 Collision Constraints

Status: TODO

## Goal
Add online self/inter-arm/environment collision avoidance.

## Codex actions
- Use common collision-distance interface / FCL geometry for core reproduction.
- Convert minimum-distance conditions into velocity-level inequalities/dampers.
- Test arm-arm, self, environment cases.
- Clearly label difference from P5 learned SCA boundary.

## PASS
Controller maintains frozen safety margin in unit scenarios and reports solve time/constraint activity.
