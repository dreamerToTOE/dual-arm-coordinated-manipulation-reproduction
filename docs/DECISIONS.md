# DECISIONS

Append-only architectural and scientific decisions.

## D001 — Two-platform strategy
- Date: 2026-09-29
- Decision: Isaac Sim + ROS2 is the final common benchmark; MuJoCo is an auxiliary force/contact laboratory mainly for P2/P3.
- Reason: preserve fair final comparison while accelerating force/contact debugging.
- Impact: baseline algorithms remain platform-independent and use adapters.

## D002 — Baseline-first rule
- Date: 2026-09-29
- Decision: `ours/` remains algorithmically empty until TASK30.
- Reason: derive our method from reproducible evidence and failure cases rather than premature design.

## D003 — P3 task→hole frame relabelling is an explicit, unproven convention
- Date: 2026-10-20
- Context: Eq.(19)/Fig.5 push along task **z**; §IV-D excludes **x** with `Σ=diag([0 1 1])`. The paper
  never states the task-frame→hole-frame rotation.
- Decision: implement `R_h` literally (hole→reference) and apply an explicit
  `R_task_to_hole` (`e_z→e_x`) to the perturbation wrench; label it **[ADAPTATION: frame naming]**.
- Evidence: with the relabelling, `Ω(R_h)·R_h(R_task→hole e_z) = 0` (8.5e-17, T03_12). Under the
  literal reading the push axis is *not* excluded (`‖Ω(I)e_z‖ = 1`, T03_15). Both variants are valid
  projectors, so this changes physical meaning, not algebra.
- Status: **open source ambiguity** — do not present the chosen convention as paper-established.

## D004 — P3 stage switching is a prescribed script, not state estimation
- Date: 2026-10-20
- Context: the paper switches stages manually (p.8572) and gives no criterion.
- Decision: `stages.StageSchedule` takes externally supplied boundaries; no contact-driven state
  machine is implemented. Label **[ADAPTATION]**.
- Impact: stage *sequences* are validated; insertion success and automatic recognition are explicitly
  not claimed.

## D005 — Reporting convention for mixed-unit quantities
- Date: 2026-10-20 (post-delivery review R2/R3)
- Decision: never quote a norm over a vector that mixes newtons and newton-metres. Force and moment
  jumps are reported separately (`jump_force_N`, `jump_moment_Nm`); the concatenated norm survives
  only as `jump_mixed_l2_unphysical`. Maxima are labelled either `max_{t,k}|x_k|` (component) or
  `max_t‖x‖₂` (vector norm), never conflated.
