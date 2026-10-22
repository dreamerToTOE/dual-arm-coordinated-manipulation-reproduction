# P2 AGENTS — scoped rules

You are implementing a **simulation-focused** paper reproduction. You are not tasked with reproducing hardware or changing P4. The existing paper-audit source branch is archived evidence, not permission to restart previous jobs or rewrite old evidence.

## Source-of-truth hierarchy
1. Original paper equations, Fig. 1–9, Tables I–II, video after independently obtained.
2. Frozen historical P2 configs & source, explicitly noting approved deviations and known failures.
3. New documented simulation adaptation, only with justification and a parallel original-baseline result.

The user has approved creation of this plan and the old-work integration, **not** blanket permission to make scientific claims or skip experiments. Never run a stage before its predecessor passes review.

## Invariants
- Frame/unit assertions; SE(3), SO(3) and wrench adjoint rigor; no silent right/left convention swapping.
- Independent plant vs controller state: never use privileged ground-truth plant state in a primary feedback controller. Ground truth may be used only for scoring and explicitly marked diagnostics.
- Preserve event timestamps, asynchronous 15 fps visual / 100 Hz tactile / 4 ms IESEKF and disparate robot command rates when reproducing claimed conditions (verify each against PDF/config before freezing).
- Preserve full original failure and reasons: estimator pad-domain invalid at t=3.948s, incomplete run ledger, prior FD qualification failure, paper Eq. (15) model divergence.
- A `PASS` for math/unit/integration/physics is not a `PASS` for paper-level metric agreement.
- Derive random seeds, perturbations and numerical tolerances **before** looking at outcomes. Freeze per-run config & revision.
- Use fixed wall/cpu budgets and a short smoke run before batch workloads. No unbounded jobs. No hidden tolerance relaxation.
- Keep optional MuJoCo validation as an independent physical model, not merely replaying the numerical plant in a 3D viewer.
- No changes to P4 paths, branches, workflow processes or files. No force pushes, no merges to main without user review.
- When something fails 3 reasoned attempts: stop, document hypothesis/falsification and classify paper insufficiency vs implementation vs unsupported parameter.

## Required exit report per task
Scope; paper equations; source commit / file hashes; exact commands; config; seeds; wall time; passes/failures; new plots; objective metrics; limitations; task-to-paper mapping; permission requested for next gate. Status choices: `NOT_EXECUTED`, `BLOCKED`, `FAIL`, `MATH_PASS`, `NUMERICAL_REPRODUCED`, `PHYSICS_REPRODUCED`, `PAPER_TREND_MATCH`, `PAPER_QUANT_MATCH` (use only with independent evidence).
