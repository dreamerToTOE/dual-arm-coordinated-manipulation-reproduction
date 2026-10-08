# TASK13-MJ — P3 Jam Detection

Status: TODO

## Goal
Detect when the single rear-pusher commands forward insertion but progress stalls under abnormal contact load.

## Start/topology
Use the same frozen INSERT_READY state and right-rear pusher as TASK11/12. Do not include handoff failures in jam statistics.

## Codex actions
- Define jam features from insertion progress, velocity, force/torque and time window.
- Avoid single-sample thresholding.
- Tune only on designated development seeds.
- Validate on held-out C1–C5 cases.

## PASS
Reports false-positive/false-negative behavior and produces deterministic JAM events.
