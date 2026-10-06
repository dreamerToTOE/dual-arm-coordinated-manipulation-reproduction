# Legacy Task27 Scope

## Status
Preserved historical application/stress-test asset. **Not a gate for TASK01 benchmark_v1.**

## What remains valuable
The five-Cube Task27 work contains useful engineering evidence about:
- full application sequencing;
- MoveIt/FCL integration;
- side-suction tool behavior;
- multi-object clutter;
- release/retreat failures;
- physics/contact instrumentation;
- GUI/headless differences.

None of that history is deleted.

## What it is not
It is not the common paper-reproduction benchmark because it mixes:
- multi-Cube fixture construction;
- different contact topologies across Cubes;
- inter-batch retreat;
- legacy application-specific success criteria;
- sensing/control issues not required by P4.

## Future use
After the one-Cube scientific baselines are mature, Task27 may be used as:
1. application demo;
2. stress test in multi-object clutter;
3. transfer/generalization experiment.

A method must not be tuned on Task27 and then reported as if that tuning were part of benchmark_v1.
