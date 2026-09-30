# TASK01 static geometry check

Command: `python3 scripts/validate_benchmark_candidate.py`

Result: `PASS: TASK01 draft geometry is internally consistent (analytic only).`
Unresolved: `PENDING: 30 unresolved fields; benchmark remains DRAFT.`

The script enumerates each null field in the live candidate. It does not verify PhysX contacts, MoveIt collisions, actual rail motion, grasp stability or benchmark metrics.
