# D082 independent saved planar trajectory qualification

All 26 saved successful D081 stability-pilot trajectories independently pass: 2,142 original saved path configurations, all 2,116 saved RBS leaves, and 6,348 additional reconstructed midpoints (8,490 total configurations). The original 24 TIME_LIMIT trials remain failures with their original denominators; no planner was run.

The independent oracle uses explicit 20R forward kinematics, finite joint limits, 170 nonadjacent segment-pair distances with capsule radii, and segment-to-circle obstacle distances. It does not import production model/strategy/planner code, Shapely, or GEOS. Eleven positive/negative fixtures include crossing/parallel/overlapping/degenerate segment cases, obstacle tangency, closure and limit perturbations, and an actual saved closed but colliding configuration.

Every successful solution is bound to its exact roots, tree ancestry, accepted edge, passive partition/branch, checked-point indices, ordered RBS leaves and original source/input SHA256 values. The additional two subdivision levels follow the recorded PCS analytic chart or independent full-Jacobian NR of recursive midpoint seeds. Unprojected straight chords are not treated as manifold paths. Arrays and pointwise residuals/clearances are in dense_paths/*.npz; each segment carries attempt, partition and branch metadata. NR partition -1/branch 0 denote no passive analytic chart.

The largest residual among dense path configurations is 9.039665918063288e-9 m and 2.220446049250313e-15 rad, under the frozen 1e-8 m/rad limits. Minimum capsule/circle clearance is 0.053965014267069594 m and minimum joint margin is 0.3460122412440585 rad. Maximum refined adjacent joint distance is 0.013110508084183946 rad. Independent saved-state clearances differ from the archived GEOS results by at most 5.551115123125783e-17 m.

All successful PCS solution edges use partition 0 and have zero genuine final-path partition switches. Thus these outcomes provide no evidence that swapping in full PCS improves these task solutions over fixed partition 0. RSS and fixed partition 16 have zero successful paths in the saved five-seed-per-scene pilot; their failures are retained.

This is a reconstructed planar virtual planning task with finite discrete qualification. It provides no strict continuous collision detection, physical execution, original spatial-environment equivalence, or original 500-trial Table I claim. Two added midpoint levels are a new independent qualification of saved edges, not new planning or a claim that the original planner sampled those points.

Run: `python3 scripts/p4_d082/independent_planar_validation.py --output <a-new-output-directory>` from the repository root. Existing output directories are refused. The full actual timed command and raw exit/timing logs are in execution_receipt.json and execution/. Actual GNUtime usage: 3.62 wall seconds and 4.93 CPU seconds, within the 180-second external bound.
