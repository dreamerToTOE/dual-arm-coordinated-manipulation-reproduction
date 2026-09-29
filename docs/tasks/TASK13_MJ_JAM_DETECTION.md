# TASK13-MJ — P3 Jam Detection

Status: TODO

## Goal
Detect when forward command no longer produces insertion progress and contact load indicates jamming.

## Codex actions
- Define jam features from progress, velocity, force/torque and time window.
- Avoid single-sample thresholding.
- Tune only on designated development seeds.
- Validate on held-out cases.

## PASS
Reports false-positive/false-negative behavior and produces deterministic JAM events.
