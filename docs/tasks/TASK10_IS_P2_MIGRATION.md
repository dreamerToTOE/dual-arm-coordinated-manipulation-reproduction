# TASK10-IS — Isaac Force/Wrench Calibration + P2 Migration

Status: TODO

## Why this task owns force calibration
TASK01 freezes the environment. P2 is the first reproduced baseline whose scientific claim depends on external/internal wrench. Therefore accurate Isaac force/wrench semantics are calibrated here rather than blocking P4 or the core benchmark freeze.

## Part A — force/wrench interface calibration
Define one common `ContactWrench` source for Isaac.

Required properties:
- force and torque in SI units;
- explicit reference frame;
- explicit application/reference point;
- post-physics-step simulation timestamp;
- documented sign convention;
- joint effort is never relabeled as TCP/contact wrench.

Validate with controlled cases such as:
1. known static payload;
2. symmetric dual-arm squeeze;
3. same-direction object load;
4. zero-contact/free-space sanity check.

If raw joint/mount reaction is used, validate any required gravity/inertia compensation and moment shift before calling it TCP wrench.

## Part B — P2 migration
- Implement Isaac adapter for state/contact/command interfaces.
- Reuse the TASK07–09 P2 algorithm unchanged where possible.
- Verify frame transforms.
- Run the one-Cube Benchmark A.

## PASS
- [ ] calibrated/sanity-checked wrench contract exists;
- [ ] same-step simulation timestamps;
- [ ] frame/application point documented;
- [ ] P2 controller runs in Isaac through adapter;
- [ ] MuJoCo→Isaac parameter differences are documented;
- [ ] no historical five-Cube flow is required for PASS.
