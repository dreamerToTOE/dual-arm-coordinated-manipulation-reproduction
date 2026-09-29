# P3 — Dual-Arm Peg-in-Hole / Hybrid Insertion

Paper: *Peg-in-Hole Assembly With Dual-Arm Robot and Dexterous Robot Hands* (IEEE RA-L, 2022).

## Relevant arm-level method
- compliant/contact-aware assembly;
- force-position hybrid control;
- perturbation patterns;
- assembly stages: approaching, searching, aligning, inserting.

## Not primary for our reproduction
Dexterous-hand grasping and in-hand rotation are not the target of our cube/carriage task unless later evidence shows they are required.

## Reproduction target
1. position-only pushing baseline;
2. hybrid force/position controller;
3. jam detection;
4. search/align recovery inspired by perturbation patterns;
5. MuJoCo validation;
6. Isaac Benchmark B migration.

## Scientific caution
Our carriage insertion is not geometrically identical to peg-in-hole. Report the mapping as [ADAPTATION], not as identical task reproduction.
