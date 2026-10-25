# D083 Stage A — pre-task / prior-asset check

Task: visualize qualified saved dual ABB paths, with source geometry and four III role transitions.
Scientific objective: make actual saved spatial trajectories and their evidence limits inspectable.
Minimum sufficient evidence: II PCS177 / NR393 3D path frames and TCP/object paths; III649 frames before/at/after all four switches and role timeline; hash-bound raw q/evidence manifest.
Current scope: rendering and saved-record arithmetic only. No planning, IK, NR, RBS or collision calls; render FK is not requalification.
Attempt budget: at most three engineering fixes per concrete rendering blocker. No new scientific experiment budget.
Preferred method: render original private .tris robot/obstacles at exact aligned source mesh transforms, bind TCP against saved independent poses.
Fallback: labeled link centerlines with exact joint frames, retaining original obstacle mesh surfaces.
Stop / escalation: inconsistent saved q/certificate/hash or mesh identity; no geometric/threshold adjustment to obtain a picture.
Files expected to change: scripts/p4_d083/render_spatial.py; this asset folder; results/20261022_D083_spatial_visualization01/.
Validation: certificate/execution SHA; q-to-node/math binding; rendering FK TCP versus saved poses; exact edge-role identity; inspect PNGs. All acceptance evidence is inherited and labeled.
Known risks: original mesh frame policy, omitted collision pairs, collinear rod triangles, native TCP mismatch; no continuous CCD or physical timing.
Need user confirmation: no — D083 explicitly authorizes Stage A and rendering saved paths.

## PRIOR-ASSET CHECK

Read: CODEX_START_HERE, AGENTS, governance, status, D083, D082 decision/delivery/findings/spatial recovery, P4 card and full eight-page original text at work/d081_p4_text/P4_original.txt; reuse map. Historical Benchmark is not changed by rendering.
Pinned source inspected: dreamerToTOE/dual-arm-embodied-palletizing@631b1f65656d025c1bb2173e874192f3fe4d355a (existing foundation checkout).
Old areas searched: shared_object_planner.cpp and task14_shared_box_geometry_monitor.cpp. REFERENCE_ONLY: generic provenance/paired TCP metric patterns; FR3/MoveIt/synchronization geometry not applicable to ABB source rendering.
DIRECT_PORT: none from old FR3 application.
THIN_ADAPTER: existing saved qualified ABB source mesh frames / elementary transform oracle; CSV/hash patterns from current D082 audit.
TEST_ORACLE: saved node_math poses and existing independent saved certificates.
Scientific algorithm remaining new/paper-derived: none in this visualization task; scientific algorithms and original qualified trajectories are reused unchanged.
New implementation: bounded matplotlib mesh/centerline renderer and record-binding exports only [ENGINEERING].
Rejected assets: generic FR3 geometry, execution timelines, new planners; they would change the scientific scene.
Risk of contamination: prevented by matching original meshes and saved TCP values. No historical threshold imported as a new test.
Need user decision: no.
