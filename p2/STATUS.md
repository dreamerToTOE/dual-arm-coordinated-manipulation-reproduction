# P2 simulation program status — 2026-10-18 (updated by T00)

**T00 AUDIT COMPLETE — NO NEW SCIENTIFIC RUN.** No experiment, integration or test has been executed on this branch. All imported records remain frozen historic results from commit `7787c75a8042af041579e5df0c9ac3e3ec4f6195`. Overall paper status: **PARTIAL**.

| Gate | Status | Comment |
|---|---|---|
| T00 frozen evidence/provenance | `COMPLETE` (static audit) | 198/198 in-scope blobs identical; 181/181 located files SHA256-identical, 0 mismatch. Verdict `PROVENANCE_PASS_WITH_RECORDED_DEVIATIONS`. See `reviews/T00_POST.md`. |
| T01 reproducible environment | `PREPARATION_COMPLETE` / `PENDING_REVIEW` | Env + parameter freeze + Eq.(18) design + budget done; no control case run. See `reviews/T01_POST.md`. |
| T01-E engineering optimisation (O1+O2) | `COMPLETE` (engineering equivalence only) | O1-a/b/c pass with 444/444 bitwise; O1-d abandoned (1.2e-10 random, 2.8e-6 near pi); O2 event-preserving logs. predict 3.37→1.16 ms, update 32.1→13.7 ms. No end-to-end run. See `reviews/T01_E_POST.md`. |
| T02 SE(3), grasp/contact math | `MATH_PASS` | 21/23 properties pass, 2 recorded deviations (Eq.10 R̄ lever arm 1.4e-3; Eq.15 printed form 80 µm vs 0). Euler `F` verified against right-error FD (2.6e-11) → the 3.948 s stop is not a Jacobian bug. See `reviews/T02_POST.md`. |
| T03 independent dynamic plant | NOT_EXECUTED | Historical 70/70 PASS is *legacy* only; note its 5 s integrations end at rest |
| T04 IESEKF & estimated-state closure | NOT_EXECUTED | 3.948 s stop now traced to Eq.(18) 4 ms Euler instability of the −2183 s⁻¹ mode (pre-computed Euler factor −7.732; saved F −5.547) |
| T05 controller / joint inversion | NOT_EXECUTED | Eq.(26) still needs joint-level evidence |
| T06 exp1–exp4 | NOT_EXECUTED | New outputs absent |
| T07 high-moment Fig.7 | NOT_EXECUTED | New controlled comparison absent |
| T08 pivot/sliding Fig.9 | NOT_EXECUTED | Physical sliding absent; grasp-force/friction model and paper time base both missing |
| T09 four-object assembly Fig.8 | NOT_EXECUTED | Virtual scene absent; B1/B2 properties and assembly layout not yet in protocol |
| T10 audit, reporting & decision | NOT_EXECUTED | Cannot claim full reproduction |

## Open items recorded at T00 (do not silently fix)

1. **Blocking** — Eq.(18) literal 4 ms right-Euler predictor is numerically unstable for the code's stiffness/damping model. A versioned propagation variant plus a parallel `PAPER_LITERAL_EULER` baseline must be declared before T04/T05. T01 produced the design (`reviews/T01_DISCRETIZATION.md`) but no implementation.
2. **Blocking** — phase-resolved budget: a 95 s transport case is 560–830 s wall (measured 5.83× transport realtime; 600 s planning value), so 30 cases are 17.7–24 ks against a frozen 7200 s cap. Engineering optimisation is a prerequisite; see `reviews/T01_BUDGET.md`.
3. `reports/P2_DELIVERY_ACCEPTANCE_FREEZE.md` and `reports/P2_ACCEPTED_DELIVERY_FREEZE_MANIFEST.json` live in `f4f9d3b9`, not in the frozen tree; referenced read-only, not imported.
4. `common/README.md` differs from the frozen commit (main version) and `common/metrics/README.md` was not imported — documentation only, no algorithm change. All 111 unimplemented report-rendering assets are listed in `LEGACY_BLOB_CHECK.json::…::missing_paths`; do not claim "zero omissions of all assets".
5. Protocol object set lacks B1/B2; Fig.9 time base (paper 0–250 s vs legacy 30 s surrogate) and Fig.5(b) assembly layout are unresolved.
6. Report path: the three `build_p2_*_review.py` scripts are registered `LEGACY_REPORT_PATH_UNUSABLE` (bytes preserved) in `reviews/LEGACY_REPORT_PATH.md`; the P2-native Markdown/PNG path is `tools/p2_md_report.py` + `tools/t02_report.py`. `python-docx` is still absent and PDF/Word export stays a T10 decision.
7. T01-E **completed as an engineering change only**: equivalence 444/444 bitwise, but no closed loop, no 95 s case and no end-to-end timing were measured. The 350–420 s extrapolation per case is a component-based estimate, not evidence that the 400 s budget holds. Seed count stays 5. O2 runner integration is import-checked only; a short closed-loop smoke needs separate approval.

No stage is automatically unlocked by legacy tests. After each accepted task update this table without rewriting historical acceptance or manipulating failed results.
