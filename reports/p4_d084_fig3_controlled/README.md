# D084 S3 — controlled Fig. 3 saved-result package

This is a read-only package of the completed D083 controlled shared-population experiment. No numerical call was rerun. The original failed `prepare01` path remains at `results/20261022_D083_fig3_controlled01/prepare_failure.json`; the successful frozen output is `results/20261022_D083_fig3_controlled02/`.

## Frozen design and result

- 96 independently qualified saved endpoint configurations from 13 prior successful 20R trajectories.
- 180 shared unordered non-self pairs, with one fixed orientation, distance, and 0.3-rad bin assignment reused at every `m`.
- Nested prefix sizes `m = 1, 2, 3, 7, 16`; 2,880 candidate partition checks and 900 fresh bounded shared-budget checks.
- Candidate results: 2,358 successes, 158 endpoint-branch incompatibilities, and 364 finite RBS midpoint IK-unreachable results.
- Bounded results: 896 successes and 4 failures at `m=1`; `m>=2` has 180/180 successes. No timeout, UNKNOWN, or compute-cap stop occurred.
- Independently qualified accepted local-call records: 3,254, covering 97,577 discrete point references. Maximum position residual is `3.907782776209828e-9 m`; minimum accepted clearance is `0.05470552470531202 m`.

The candidate union and bounded strategy are separate estimators. Candidate-union success is existential under the frozen finite RBS rule; bounded costs are fresh calls and are not cached candidate runtime. These exact rates describe this reconstructed proxy population and do not reproduce the original author’s Fig. 3 population or Bi-RRT planning-time curve.

## Budget and hashes

The successful execution plus failed prepare cost `86.29 wall / 90.71 process-CPU seconds` against the frozen `300/300` Stage B cap. The nominal unused envelope is `213.71 wall / 209.29 CPU seconds`; it is not new execution authorization. `manifest.json` records all copied-file hashes, the full artifact hash manifest, and the 180 raw-pair archive’s local-only path.

Key hashes:

| File | SHA-256 |
|---|---|
| `summary.json` | `bfe1f03236e0aea96f9da894e2b3970be5f8b68e382dd70d45472f6dd8ea5207` |
| `frozen_pairs.csv` | `ad3b6a12b772eaeefe278abc6f45ddd59c170beb54eaed08c36e72b1fd541178` |
| `pair_by_m_outcomes.csv` | `5d1ca17dca2484ae9a70e003eb4ff2a397d7221ab57c08e8ec444799745d6368` |
| `plots_v2/fig3_controlled_visibility_and_local_cost_by_m.png` | `468fd8f82481402bc344c8d44a016d47836fa82c631f7e99e464ccf6dd582cb1` |
| `plots_v2/fig3_controlled_visibility_by_distance.png` | `1446a45c3f2fb19c31884996b3e9d1dc395f591af95ff466595baa09ea3adeb9` |
| `manifest.json` | `7f88cd323e515ab3928c35f767205c54590e3d18a574562ba9d50d4406fe8d8f` |

The 180 raw gzip pair files total 45,389,043 bytes and remain at `results/20261022_D083_fig3_controlled02/raw_pairs/`; they are preserved locally rather than duplicated in this smaller S3 package. Their complete `artifact_sha256.json` is included.

## Evidence boundary

This is a reconstructed planar 20R proxy with correlated endpoints and shared pairs. It does not establish PCS superiority, global visibility, continuous collision safety, original `m=20`, or original author runtime performance. The exact next-stage package must retain the four `m=1` failures and all finite-rule limitations.
