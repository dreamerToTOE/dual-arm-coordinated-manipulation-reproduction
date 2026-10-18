# Historical P2 provenance and reuse / 旧成果可追溯整合

**Immutable source commit (user-accepted partial handoff): [`7787c75a8042af041579e5df0c9ac3e3ec4f6195`](https://github.com/dreamerToTOE/dual-arm-coordinated-manipulation-reproduction/commit/7787c75a8042af041579e5df0c9ac3e3ec4f6195).**
Copied blobs from this commit preserve identical SHA and the original repository-relative paths; the copied materials are **legacy evidence**, not newly successful runs. The archived source branch is `reproduce-p2-paper-audit`; it is mixed with P4 materials and deliberately was **not** used as new branch base.

## Verified, narrowly described historical observations
| Historical evidence | What was actually achieved | What it does NOT prove |
| --- | --- | --- |
| `results/20261014_P2_contact_geometry_qualification02/` | Contact-geometry finite check and corrected sign/negative cases documented in `reports/P2_CONTACT_GEOMETRY_POST_TASK.md`. | Full dynamic/contact or assembly reproduction. |
| `results/20261014_P2_implicit_qualification_v3_01/summary.json` | **70/70 qualification checks PASS**, including five-second independent plant integrations. | Controller+state-estimator joint closed-loop stability. |
| `results/20261014_P2_components_qualification01/summary.json` | **35/35 component checks PASS** for observation, estimator and controller. | Actual paper trajectory followed under feedback. |
| `results/20261014_P2_clock_qualification01/summary.json` | **2/2 causal scheduling checks PASS**. | Independent experimental outcomes. |
| `results/20261014_P2_closed_loop_suite02/case_11_exp3_7/summary.json` | First actual estimated-state primary closed loop stopped at **t=3.948 s**, `ESTIMATOR_MODEL_PAD_DOMAIN_INVALID`; no full exp3 outcome. | Completed Fig.6 exp1–exp4 or full paper. |
| `results/20261014_P2_closed_loop_suite02/summary.json` | `FAIL_STOP`, one attempted and zero completed, other cases NOT_EXECUTED. | 30 completed runs or 30 negative results. |
| `reports/P2_IMPLICIT_QUALIFICATION_RESULTS.md` | Earlier fixed two-point finite-difference Jacobian gate failed and was preserved; later revised-oracle v3 qualified. | That the earlier failed criterion was ever passed unchanged. |

## Scientific deviations / do NOT bury
- The historical `p2.spatial_free_log_constraint.v1` contact geometry was a **user-approved alternative interpretation** to a disputed Eq. (15). See `reports/P2_CONTACT_GEOMETRY_DERIVATION_RENDERED.md` and `reports/P2_ORIGINAL_PAPER_AUDIT.md`. It is **not** author-confirmed erratum or literal Eq. (15) reproduction.
- Former implementation has **ideal Cartesian endpoint commands**; it does not verify complete joint-space Eq. (26) or physical KUKA/SIA5F compliance.
- Soft-contact damping, friction, sensor pad deformation, model error and perception noise require explicit fidelity analyses.
- Original frozen delivery declared `PARTIAL`, accepted with 3/3 repair budget used. New work is a **new authorized research scope** with new ledgers, not a rewrite of that verdict.
- Old report names/plots may look like success; cite actual result JSON and timestamp before claiming paper agreement.

## Integration manifest
Imported unchanged P2 code: `baselines/p2_pose_force/`; numerical scripts: `scripts/*p2*.py`; unit tests: `tests/test_p2_*.py`; config: `configs/p2_*`; mathematical common Python/C++ helpers: `common/`; original P2 task docs: `docs/tasks/P2_*`; accepted reports: `reports/P2_*`; recorded P2 result folders: `results/*_P2_*`.

The source SHA for each imported Git blob must be checked with `git ls-tree` (T00). No historical archive, log, plot or failed test should be removed or replaced. Some bulky report-rendering images and non-P2 shared programs are not copied into the new isolated branch; they remain available at the source commit. See [source immutable tree](https://github.com/dreamerToTOE/dual-arm-coordinated-manipulation-reproduction/tree/7787c75a8042af041579e5df0c9ac3e3ec4f6195) for anything not included.
