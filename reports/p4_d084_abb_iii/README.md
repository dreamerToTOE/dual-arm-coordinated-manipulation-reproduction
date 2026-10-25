# D084 S2 — ABB Environment III role-switch evidence

This package binds the four role changes to the existing 649-state, 14-edge saved solution. It copies the previously generated narrow-passage scene, four before/after switch frames, role/evidence scene, saved trajectory view, and saved-state animation, then adds a read-only edge-role timeline from the saved CSV and provenance JSON. No planner, IK, collision, source solve, or qualification call is made.

## Figures and hashes

| File | SHA-256 |
|---|---|
| `fig_S2_abb_iii_role_timeline.png` | `71f533f263ce0412b43cbb982a7eeef229a5816e672eebb75cdb5130234ef655` |
| `fig_S2_abb_iii_role_timeline.pdf` | `4e929dcc6b0be478e0edfa9ea27e7b775bc0f52eede377f17df21eaec9ec4ccc` |
| `role_timeline.csv` | `b38cc2abd63369e6690d47a5eddab163fb025609caa3345493e411ffbc987268` |
| `manifest.json` | `84bcfb17754695de04a926c8d87093c538037fa64f986f09914a1689790002a3` |
| `render_abb_iii.py` | `343d6a3d26b90376313b67f517f35a340cd2787548800b1f31aa5b61fadac0f2` |

The copied source-linked figures retain their D083 hashes in `manifest.json`, including A2v2 (narrow passage), A3 (four switch frames), A4 (roles/evidence), A5 (saved trajectories), and the 36-frame saved-state GIF.

## Frozen role evidence

The saved path has 649 nodes, 648 leaves, 15 milestones, and 14 accepted edges. The active-role array is:

`[0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0]`

The four successive transitions are:

| Boundary | Source node / traversal index | Transition |
|---:|---:|---|
| edge 3 → 4 | 179 / 179 | A1 → A2 |
| edge 4 → 5 | 248 / 248 | A2 → A1 |
| edge 7 → 8 | 392 / 392 | A1 → A2 |
| edge 9 → 10 | 492 / 492 | A2 → A1 |

Inherited saved evidence reports aligned TCP pass 649/649 and native TCP pass 0/649, with maximum native TCP translation mismatch 0.003570536971253091 mm and rotation mismatch 7.347665530579861e-06. The named independent certificate and its SHA are recorded in `manifest.json`.

## Evidence boundary and reproduction

The scientific label is `RECONSTRUCTED_ALIGNED_DISCRETE_SOURCE_COLLISION_POLICY_ONLY`. The source `exact` flag is not an independent certificate. Role changes describe active/passive ownership of accepted discrete edges, not a continuous physical handoff. Native equivalence, continuous CCD, minimum clearance, omitted collision pairs, solid-rod safety, dynamic execution, and PCS superiority are not established.

To regenerate the package in a new directory from the saved CSV/provenance and existing D083 figures:

```bash
python3 scripts/p4_d084/render_abb_iii.py \
  --output reports/p4_d084_abb_iii_replay01
```

The script performs saved-data validation, figure copying, and timeline plotting only.
