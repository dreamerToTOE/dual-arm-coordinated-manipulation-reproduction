# P4 D084 / S1 — ABB Environment II spatial visualization

**Single-window rule:** Complete ONLY this task; commit, push, give a short post-task report, then STOP. No automatic next stage. The overall task router is `docs/tasks/P4_D084_WINDOW_INDEX_20261023.md`. D084 changes orchestration only, not D083 scientific scope or author-paper facts. Scientific baseline pre-D084 `0b41236e`; always inspect current HEAD instead of assuming it.

**Purpose:** Convert previously saved **Environment II** dual ABB trajectories into verifiable 3D figures. **No new planning or scientific metric change.**

Read `reports/P4_D082_SPATIAL_RECOVERY_20261022.md` and the latest `reports/P4_D084_S0_RECOVERY_CHECKPOINT.md` if present. Inspect `scripts/p4_d083/render_spatial.py` and existing visualization assets first. Use authentic saved q paths/certificates: RRT PCS 177 states, RRT NR 393, CBiRRT PCS 413, CBiRRT NR 689; SBL separately documented if used. Reuse actual ABB base transforms, bar/object and obstacles; source-model link geometry only, with transparent proxy shapes if necessary.

Produce source-linked 3D scene with start/goal and trajectory snapshots; separate PCS/NR trajectory comparison and closure/joint/collision metrics from previously qualified evidence. An optional compact animation is allowed if cheap; no interpolated frames may be labeled CCD-qualified or dynamically executable. If meshes/provenance unavailable, use carefully labeled centerline/capsule representation rather than inventing industrial geometry.

**Deliverable:** versioned `reports/p4_d084_abb_ii/` with figure(s), script, small data or manifest, README listing exact path SHA and certificate, and `reports/P4_D084_S1_POST.md`. Keep native/aligned and finite-discrete limitations explicit. Commit/push. **STOP**. Do not work on III, Fig3, difficulty tests or PDF.

## Session exit checklist
- Record source commit(s), input/result hashes, completed/UNKNOWN/failed evidence, resource consumption and remaining block.
- Any files still only local must be explicitly enumerated. No irreversible cleanup.
- Push the stage report and artifacts if possible, verify remote HEAD/clean tracked state, then terminate work.
