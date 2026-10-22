# P2-T03: Independent integrated object/contact plant

**Initial status:** NOT_EXECUTED. **Predecessor:** P2-T02 review accepted. **Reference:** see `p2/PAPER_TO_CODE.md` and `p2/EXPERIMENT_MATRIX.md`.

## Actions / 执行细则
- Audit old 42-dimensional state dynamics and native implicit Lie midpoint solver (paper Eq.(13)–(16)); confirm old 70/70 checks and preserved prior FD oracle failure provenance.
- Reproduce independent COM Newton/Euler dynamics and soft contact under gravity; no desired-pose or force-controller target injected directly into the plant.
- Fixed nominal, high-moment, sliding/free-motion initial conditions: run bounded 5s integration with full/well-stated half-step comparison; check energy/drift/contact wrench plus solver convergence.
- Validate alternative backend/ODE reference at at least two time steps; do not adjust integration tolerances retroactively.

## Acceptance / 验收门槛
Exit: actual integrated state/force/time histories and error convergence, model discrepancies documented, no oracle resets.

## Guard / 禁止事项
Qualified plant does not establish IESEKF/control.

## Minimum handoff
Provide `p2/reviews/T03_PRE.md` before any runs (scope, paper mapping, hardware assumption, pinned params, exact command, seed, wall budget) and `p2/reviews/T03_POST.md` after (changed files and commit, case ledger with PASS/FAIL/BLOCKED/NOT_EXECUTED, generated data paths, figures, independent verification, known deviations and decision request). Preserve historical evidence unmodified.

## T01 审查后的计划补充（2026-10-19，仅计划，本轮未执行）

来源：Issue #35 审查意见 + `p2/reviews/T01_DISCRETIZATION.md`。本节**新增**要求，不删除、不放宽上文任何验收条件。

- **快/慢模态谱**：对 A、B1、B2、C 四个对象，在 nominal 与至少两个非平衡工作点上输出 42 维右误差 Jacobian 的**全部**特征值（实部、虚部、模），标注最快实模态、复模态对与对应物理方向；与 `results/20261014_P2_stage2_numerical_audit01` 的 −2183.07 s⁻¹（A）、−9335.81 s⁻¹（C）逐项对照，偏差必须解释。
- **离散谱**：对候选传播格式（显式 Euler / 隐式 Euler / 梯形 / 矩阵指数 / 子步 Euler）在 `1/3000`、`1 ms`、`4 ms` 下给出 `ρ(Φ)` 表；**必须核查 C 的 `ρ=2.73`**（旧隐式中点审计，1/3000）：判断它是线性化伪影、fixture 非平衡项，还是真实不稳定。禁止用静止平衡的五秒积分替代运动保真结论。
- **受扰运动验证**：在非平衡初值下施加已知小扰动（位置 / 姿态 / 速度），检验能量耗散、接触力恢复、步长收敛（粗 / 半 / 四分之一），给出观测收敛阶；不得只报终端平衡状态。
- **新增产物**：`T03_SPECTRUM.json`（逐模态）、`T03_PERTURBATION.json`（衰减与收敛）、`T03_POST.md` 中显式写明"静止积分 ≠ 运动保真"。
- **预算**：谱分析属静态数学，墙钟 ≤120 s；受扰积分按优化后单案 ≤400 s 口径（见 `T01_BUDGET.md`），超出即停。
- **禁止**：不得据谱结果修改 plant 参数或刚度/阻尼；C 的 `ρ=2.73` 若复现，先归因，再决定是否版本化新积分器，不静默替换。

