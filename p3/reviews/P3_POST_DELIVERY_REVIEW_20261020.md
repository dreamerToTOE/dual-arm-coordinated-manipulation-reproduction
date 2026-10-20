# P3 Post-Delivery Independent Review — 2026-10-20

**Review status:** CONDITIONAL ACCEPTANCE (minor evidence corrections needed before archival), **not** a request to redo the core reproduction.

**Reviewed:** P3 T00 audit, `baselines/p3_peg_in_hole/{patterns,stages,control,fixtures}.py`, T03/T04/T06 test drivers and their JSON artifacts, final Markdown and evidence commit chain (T01 `54306928`, T02 `6aa406e5`, T03 `bf3fdec7`, T04 `f01e36f2`, T06 `dedd8e90`, report `e1f7d874`). GitHub evidence logs report 91/91 PASS; this reviewer did not independently re-execute them.

## Required minimal corrections

### R1 (scientific correctness): T03_12 uses the wrong basis vector

Current `p3/tools/run_t03_selection.py`:
```python
Sel_task = ctl.position_selector(R_H @ R_TASK_TO_HOLE)
push_dir = (R_H @ R_TASK_TO_HOLE) @ np.array([1.0, 0.0, 0.0])
res_push = np.linalg.norm(Sel_task[:3, :3] @ push_dir)
```
This is tautological: it shows that a projector annihilates its own transformed `e_x`; it does NOT check the paper's `e_z` push direction. The inline comment `# = R_h e_z` is also false for `R_y(+90°) e_x = -e_z`.

With `R_task_to_hole e_z = e_x`, the **correct physical push direction in the reference frame** is:
```python
p_ref = R_H @ (R_TASK_TO_HOLE @ np.array([0., 0., 1.]))
assert np.linalg.norm(ctl.omega(R_H) @ p_ref) < tol
```
Also add a negative control that explicitly demonstrates that the unrelabeled literal interpretation is **not generally equivalent**: for `R_H=I`, `ctl.omega(I) @ e_z = e_z != 0`. Thus *projector algebraic properties* of each variant may be valid while *push-axis alignment* of the literal interpretation fails. The integrated `control.py` path already takes `R_task_to_hole`; T06_06 appears to use `p_ref` correctly. Correct T03_12, update T03 POST, T00 source-audit A1 assertions, final report text, re-run T03 and T06. Do not claim the paper independently proves which frame convention was intended; retain A1 as an explicit [ADAPTATION] and source ambiguity.

### R2 (metric correctness): max component vs Euclidean norm

`p3/tools/run_t06_integration.py` currently uses `np.max(np.abs(all_tau))` and `np.max(np.abs(all_w[:, :3]))`, which are **maximum absolute components**, not `max_t ||tau(t)||_2` nor `max_t ||F(t)||_2`. The report writes `||tau|| <= 10.15 N*m`, which is not established by this calculation. Report max-component values with the correct notation, and if desired additionally calculate vector norms separately (with units). Audit any per-stage `mean_abs_force_N`: if computed as mean absolute component, label it so; do not imply a magnitude of a force vector.

### R3 (dimensional correctness): mixed wrench jump norm

`stages.StageSchedule.discontinuities()` records `jump_l2` over a concatenated 6-vector containing forces (N) and moments (N*m). The numerical value is not a physical quantity with one unit. Promote `jump_force_N` and `jump_moment_Nm` to the report's stage-boundary table. Retain mixed `jump_l2` only as an explicitly labeled nonphysical, unnormalized numerical diagnostic, or remove it from the primary results. Correct the graph labels/captions as needed.

### R4 (project governance): append-only registers are stale

On the P3 branch, `docs/STATUS.md`, `docs/WORKLOG.md`, `docs/EXPERIMENT_LOG.md` and `docs/DECISIONS.md` still have only the September foundation entries and do not index the P3 numerical reproduction. Append the P3-specific completion, acceptance scope, A1 decision, test run IDs, commit SHAs, branch and evidence paths. Preserve the older entries and unrelated P2/P4 history. Do not overwrite general benchmark status or claim P3 MuJoCo/Isaac tasks are complete.

## Completion gate

1. Keep the original 91-check result intact as historical evidence. Re-run the corrected tests, producing new versioned run IDs, not overwriting the original JSONs.
2. Rebuild the Markdown, editable DOCX, PDF, scope and equation matrices where affected; make sure report summary states `ALGORITHM_NUMERICAL_VERIFIED (D082 scope)` **only after** the corrected frame-axis test passes.
3. Validate report figures and unit labels, preserve T05 `NOT_EXECUTED_OPTIONAL`, and avoid any new physics/contact work, dependency installs, or extra experiments.
4. Document exact new test counts if a new negative test is added (do not continue calling the revised suite 91 checks by default).
5. Produce one compact final POST: amended check count, corrected numbers and units, links/paths, SHA, caveats, reproducibility command and a recommendation whether to archive P3 and begin P5 paper study.

**General result:** The existing code and evidence provide strong evidence of an arm-level Eq.16–28 **formula implementation and command-consistency demonstration**. They do **not** reproduce object motion, contact outcome, hardware success statistics, or the dual-arm robot dynamics.
