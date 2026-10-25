# D084 S4 — bounded PCS difficulty diagnostic package

This package records the completed frozen three-condition diagnostic from `results/20261022_D083_difficult02/`. It is an archival endpoint diagnostic, not an unbiased hard-benchmark study. The first `C1_PCS_seed7` call remains `UNKNOWN_ARTIFACT_SERIALIZATION_FAILED` and was never rerun.

## Frozen batch and results

- 36 registered calls: one preserved UNKNOWN first call plus 35 resume calls.
- PCS: 8/8 complete evaluable successes plus 1 UNKNOWN.
- Compatible fixed-0: 9/9 independent successes.
- NR: 9/9 independent successes.
- RSS: 3/9 independent successes and 6 time limits.
- All 29 complete successes passed the independent saved-path checks. Tree and final-path partition switches are zero.
- New RSS calls made 53 singular requests and 1,696 constructions; all 1,696 were `IK_UNREACHABLE`, with zero valid singular constructions. The three RSS successes use ordinary same-branch partition-16 edges.

The saved audit reports 3,111 saved path points and 12,357 dense points, maximum dense position residual `9.932681348866121e-9 m`, minimum dense clearance `0.0017204385542725804 m`, and zero independent failures. These remain discrete checks; they are not continuous CCD or dynamic safety certificates.

## Budget and preserved raw evidence

The combined external cost, including the failed first call, is `17.00 wall / 19.84 process-CPU seconds` against the frozen `180/240` Stage C cap. Nominal unused budget is `163.00 wall / 220.16 CPU seconds`; it does not authorize new calls. The complete 35-file raw planner archive remains at `results/20261022_D083_difficult02/raw_planner/` (8,269,303 bytes) and is covered by `artifact_sha256.json`. The package includes qualifications, independent paths, ledgers, audits, summaries, and the diagnostic plot.

Key hashes:

| File | SHA-256 |
|---|---|
| `summary.json` | `159f69327a0644a85a7cf1ed8a7efaf3405713c7e63ce29b1ba07a264bdefe32` |
| `planner_trials.csv` | `da7f0c3965575b9e7650232b3d9d6ff0de14bea02f4928a2bcfeffb41cb70086` |
| `method_summary.csv` | `c88d9f5d722af4460a0848cb9f6e461a02d55979581afd9b63067b83c04383fb` |
| `difficult_diagnostic.png` | `9db186ca49f85b253a6c0c560869d77b2bbdfb483815834f76c8c157e6f2b8cb` |
| `manifest.json` | `5104ee0eb9dae574b03b77e54016b53d9611113455c1ace2a02c138b4c90d0ee` |

No universal PCS advantage or genuinely hard-scene claim is supported. The original D083 failure and all negative evidence remain preserved.
