# USER_FEEDBACK

Persistent user decisions/feedback that must influence future work.

## 2026-09-29
- Keep detailed records and feedback during Codex work.
- Use a separate reproduction repository instead of mixing baselines into the palletizing repository.
- Use MuJoCo as an auxiliary force/contact platform where useful, but keep Isaac Sim as the final unified benchmark.

## 2026-09-30
- Advance tasks in repository order and persist process records to GitHub as work proceeds.
- MuJoCo is already installed in a .venv belonging to the existing force-control project; locate and reuse that environment for audits instead of assuming the system Python import result means MuJoCo is absent.

## 2026-10-21 — Reproduction report writing preference (mandatory for future reports)
- The user personally removed the section titled **“3.2 为什么只做算法数值复现”** from the P5 Word report. Do **not** restore it or add a replacement explaining why the project reproduces algorithms numerically rather than running full simulation/hardware experiments.
- In future P1–P5 and other paper reproduction reports, **do not narrate instructions from the supervisor/advisor**, e.g., “导师要求……”, “导师说……”, or justify project choices by citing their requests. This is a report-writing rule, not a change to the underlying research scope or repository technical evidence.
- Write for a scientific reader: foreground the paper's research question, methods, equations/derivations, original experiments as relevant, our implementation, actual numerical results, comparisons, and technical limitations. State scope/limitations briefly and objectively **only where scientifically necessary**, without discussing who assigned the work.
- The “3.2” prohibition refers to the *content of that particular explanatory section*, **not** to the numerical heading “3.2” in every future document. Re-number naturally; do not add a placeholder heading.
- **Do not edit the P5 Word report as part of recording this preference**; the user has already deleted the section locally.
