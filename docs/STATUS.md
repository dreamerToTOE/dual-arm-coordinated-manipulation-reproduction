# STATUS

Last update: 2026-10-21

## Project state
Repository initialized. No baseline implementation has started.

| Task | Status | Notes |
|---|---|---|
| TASK00 Environment Audit | PASS | Report: reports/TASK00_ENVIRONMENT.md; external integration gaps identified |
| TASK01 Benchmark Freeze | READY | Needs user review before FROZEN; spec remains DRAFT |
| TASK02 Common Interfaces / Logger / Metrics | TODO | Depends on TASK01 |
| TASK03–06 P4 | TODO | |
| TASK07–10 P2 | TODO | |
| TASK11–15 P3 | TODO | |
| TASK16–19 P5 | TODO | |
| TASK20–26 P1 | TODO | |
| TASK27–30 Evaluation/Freeze | TODO | |
| TASK31 Ours v0 | TODO | Must wait for TASK30 |

## Current gate
**Do not implement paper algorithms yet. Draft and review TASK01 benchmark_v1 first.**

## 2026-10-21 — P1 G0 论文研读与复现规划

- 分支：`reproduce-p1-numerical-20261021`（基线 `a596c973`，`main`）。
- 状态：**G0 完成；G1–G3 数值复现完成；G4（GPU）未启动**。交付物见 `p1/` 与 `p1/reports/`。
- 已建立：论文公式账本（52 式）、两仓库两快照的固定 SHA 审计（`fe5b49f7` / `1820a9e8` / `231f130e` / `c762b7d6`）、16 项原始实验矩阵、16 项候选复现模块（A–G）、实施计划草案。
- 关键判定：
  - 论文式 (8) 印为 $x_2^*x_{r/2}$，几何自洽读法与官方内核均为 $x_2\sqrt{x_r}$（SE(3) 螺旋中点）；已记录为 `AMBIGUOUS` 并给出三重证据。
  - 表 I 与示例 YAML 有 8 项参数不一致；代码另在采样分布、停滞项、奇异项、$C_s$ 选取、每周期重置种子上偏离论文式子（共 7 项 `CODE_MODIFIED`）。
  - 官方仓库**无许可证**；主分支缺 12 个基线、Task 3–6 场景、动态障碍膨胀与高层节流。
- 可复现边界：算法机理（A/B/D/F）可高保真数值复现；表 II 的逐格数值与 Fig. 8 的绝对时延不可直接复现。
- G1–G3（2026-10-21）：纯 NumPy 实现 DQ 运动学、零空间、单/两阶段采样与两组任务；31 项测试通过；G1 全部指标达机器精度，G2 的 MPPI 与 LQR 差 3%，G3 两阶段 0.43 vs 单阶段 0.00（等预算），修正官方有色噪声幅度后，两阶段（0.67）不再优于单阶段（0.67），去掉聚类反而 1.00——两阶段/k-means 的收益未复现（负结果 N1）；辅助终结器在 η=1.0 时把 E1 收敛到 0.79–1.16 cm，表 I 的 η=0.1 则永不切换（N2）。
- D008 审计（2026-10-22）：修正 D2 温度、阶段二消融、惯性簇身份与 G3B 公平性；新增 N2 轨迹与 N3 量纲审计；验收结论 **PARTIALLY_VERIFIED**（阻塞 B1–B3 属论文澄清类）。详见 `p1/D008_AUDIT.md`。
- 下一步：按 `p1/CHINESE_REPORT_OUTLINE.md` 撰写中文复现报告（本轮不生成 Word）；待作者澄清后再评估解除 B1–B3。
