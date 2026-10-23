"""N3 audit: the singularity cost (Eqs. 36-37) and its scale.

The published formula is kept unchanged (``p_e / max(zeta, w)``).  This script
measures what the formula does numerically: the units of ``w``, its magnitude
and spread, its effect on the softmax weights and on the selected control, and
its behaviour near a singular configuration.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p1_repro.cost import CostConfig, singularity_cost, terminal_goal_cost, yoshikawa  # noqa: E402
from p1_repro.dq import dq_to_rt  # noqa: E402
from p1_repro.kinematics import SerialChain, relative_jacobian  # noqa: E402
from p1_repro.sampler import colored, softmax_weights, weighted_noise  # noqa: E402
from p1_repro.tasks_dual import BASE1, BASE2, HOME1, HOME2, UR3_DH, DualArmTask  # noqa: E402


def w_at(dh, base1, base2, q1, q2):
    c1 = SerialChain(dh, base=base1)
    c2 = SerialChain(dh, base=base2)
    J = relative_jacobian(c1, c2, q1[None], q2[None])
    return float(yoshikawa(J)[0, 0]), J[0]


def main():
    task = DualArmTask()
    cfg = CostConfig.paper()
    w0, J0 = w_at(UR3_DH, BASE1, BASE2, HOME1, HOME2)
    sv = np.linalg.svd(J0, compute_uv=False)

    # 1) definition check: product of the six non-zero singular values
    w_check = float(np.prod(sv[:6]))
    # 2) unit scaling: w(s) with all DH lengths multiplied by s
    scales = [0.01, 0.1, 1.0, 10.0, 100.0]
    ws = []
    for s in scales:
        dh = UR3_DH.copy()
        dh[:, 1] *= s
        dh[:, 2] *= s
        ws.append(w_at(dh, BASE1, BASE2, HOME1, HOME2)[0])
    alpha = float(np.polyfit(np.log(scales), np.log(ws), 1)[0])

    # 3) distribution over configurations
    rng = np.random.default_rng(0)
    qs1 = HOME1 + rng.uniform(-0.6, 0.6, size=(300, 6))
    qs2 = HOME2 + rng.uniform(-0.6, 0.6, size=(300, 6))
    c1 = SerialChain(UR3_DH, base=BASE1)
    c2 = SerialChain(UR3_DH, base=BASE2)
    Js = relative_jacobian(c1, c2, qs1, qs2)
    w_dist = yoshikawa(Js)[:, 0]
    c_sing = cfg.p_sing / np.maximum(1e-6, w_dist)

    # 4) across-sample spread at the terminal state of one sampled batch
    # Sample joint-velocity sequences around zero (the dual-arm task is not the
    # corridor task; ``colored`` above is 2-D and is not used here).
    U = rng.normal(0, 0.15, size=(200, task.horizon, 12))
    diag = task.rollout(U)
    J_term = relative_jacobian(task.c1, task.c2, diag["q1"], diag["q2"])
    w_term = yoshikawa(J_term)[:, 0]
    c_sing_term = cfg.p_sing / np.maximum(1e-6, w_term)
    goal_term = terminal_goal_cost(diag["xa"], task.xa_d, dq_to_rt(diag["xa"])[1], task.pos_d, cfg)[:, 0]
    c_all = diag["cost"][:, 0]
    lam = 0.1 * float(c_all.max() - c_all.min())

    def weight_effect(delta):
        return float(np.exp(-delta / lam))

    # 5) effect on the selected control (single update, same batch)
    costs_with = c_all + c_sing_term
    costs_without = c_all
    lam_w = 0.1 * float(costs_with.max() - costs_with.min())
    lam_o = 0.1 * float(costs_without.max() - costs_without.min())
    w_w = softmax_weights(costs_with[:, None], lam_w)
    w_o = softmax_weights(costs_without[:, None], lam_o)
    du = weighted_noise(U, w_w) - weighted_noise(U, w_o)

    # 6) sensitivity near singular configurations: a 2-D grid on the first
    # arm's shoulder/elbow (the second arm is fixed at home).
    g1 = np.linspace(-2.6, 0.4, 16)
    g2 = np.linspace(-2.6, 0.4, 16)
    w_grid = np.zeros((len(g1), len(g2)))
    for i, a in enumerate(g1):
        for j, b in enumerate(g2):
            q1 = HOME1.copy()
            q1[1], q1[2] = a, b
            w_grid[i, j] = w_at(UR3_DH, BASE1, BASE2, q1, HOME2)[0]
    k = np.unravel_index(int(np.argmin(w_grid)), w_grid.shape)

    out = {
        "home": {
            "singular_values": sv.tolist(),
            "w": w0,
            "w_product_check": w_check,
            "C_sing_p_e_10": float(cfg.p_sing / w0),
            "C_sing_p_e_0p5": float(0.5 / w0),
            "C_goal_at_home": float(np.sum(np.abs(task.xa_d - task.xa_0)) * cfg.p_goal),
        },
        "unit_scaling": {
            "scales": scales,
            "w": ws,
            "exponent_alpha": alpha,
            "interpretation": "w has units of length^alpha; C_sing = p_e / w has units length^-alpha",
        },
        "distribution": {
            "w_median": float(np.median(w_dist)),
            "w_min": float(w_dist.min()),
            "w_max": float(w_dist.max()),
            "C_sing_median": float(np.median(c_sing)),
            "C_sing_min": float(c_sing.min()),
            "C_sing_max": float(c_sing.max()),
        },
        "terminal_spread": {
            "w_median": float(np.median(w_term)),
            "C_sing_median": float(np.median(c_sing_term)),
            "C_sing_p5": float(np.percentile(c_sing_term, 5)),
            "C_sing_p95": float(np.percentile(c_sing_term, 95)),
            "C_goal_median": float(np.median(goal_term)),
            "C_goal_p5": float(np.percentile(goal_term, 5)),
            "C_goal_p95": float(np.percentile(goal_term, 95)),
            "delta_C_sing_p95_p5": float(np.percentile(c_sing_term, 95) - np.percentile(c_sing_term, 5)),
            "weight_ratio_for_delta": weight_effect(float(np.percentile(c_sing_term, 95) - np.percentile(c_sing_term, 5))),
            "lambda": lam,
        },
        "control_effect": {
            "delta_u_norm": float(np.linalg.norm(du)),
            "u_norm_with": float(np.linalg.norm(weighted_noise(U, w_w))),
            "u_norm_without": float(np.linalg.norm(weighted_noise(U, w_o))),
            "cosine": float(
                np.sum(weighted_noise(U, w_w) * weighted_noise(U, w_o))
                / max(np.linalg.norm(weighted_noise(U, w_w)) * np.linalg.norm(weighted_noise(U, w_o)), 1e-12)
            ),
        },
        "singular_sweep": {
            "grid_shoulder": [float(g1[0]), float(g1[-1]), int(len(g1))],
            "grid_elbow": [float(g2[0]), float(g2[-1]), int(len(g2))],
            "w_min": float(w_grid.min()),
            "w_max": float(w_grid.max()),
            "q_at_wmin": [float(g1[k[0]]), float(g2[k[1]])],
            "C_sing_at_wmin": float(cfg.p_sing / max(w_grid.min(), 1e-6)),
        },
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "N3_SINGULARITY_AUDIT.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    md = f"""# N3 审计：奇异项 (36)(37) 的量纲与数值行为

> 自动生成：`python p1/scripts/n3_singularity_audit.py`
> 公式保持不变：$w=\\prod_{{i=1}}^6\\sigma_i$，$C_{{\\text{{sing}}}}=p_e/\\max(\\zeta,w)$。

## 1. 定义与量级（home 位形）

| 量 | 值 |
|---|---|
| 6 个非零奇异值 | {np.round(sv[:6], 3).tolist()} |
| $w$ | {w0:.6f} |
| $w$ 与奇异值连乘的差 | {abs(w0 - w_check):.2e} |
| $C_{{\\text{{sing}}}}$（$p_e=10$） | {out['home']['C_sing_p_e_10']:.1f} |
| $C_{{\\text{{sing}}}}$（$p_e=0.5$，代码口径） | {out['home']['C_sing_p_e_0p5']:.1f} |
| home 处 $C_{{\\text{{goal}}}}$ | {out['home']['C_goal_at_home']:.2f} |

## 2. 单位与标度

| DH 长度缩放 $s$ | $w$ |
|---|---|
""" + "\n".join(f"| {s:g} | {w:.3e} |" for s, w in zip(scales, ws)) + f"""

在 $s\\in[0.01,100]$ 上的 log-log 经验斜率：**{alpha:.3f}**。

**测量**：$w$ 随长度单位单调变化，但 2.712 是该有限区间上的经验斜率，**不是物理量纲**。$J$ 同时含平移行（带长度单位）与旋转行（无量纲），因此不存在唯一的"$w$ 的量纲"；要给 $w$ 一个有物理意义的归一化，必须先指定特征长度或显式缩放约定（例如把平移行除以 $L_c$）。**解释**：在未指定缩放约定时，$p_e/w$ 与 $C_{{\\text{{goal}}}}$ 不可通约；$p_e=10$ 只在某个隐含单位下才与 goal 同量级。论文未给出该约定，故无法从原文确定 $p_e$ 的正确标度。

## 3. 配置分布与样本变化

| 量 | 中位数 | 5% | 95% |
|---|---|---|---|
| $w$（300 构型） | {out['distribution']['w_median']:.4f} | {out['distribution']['w_min']:.4f} | {out['distribution']['w_max']:.4f} |
| $C_{{\\text{{sing}}}}$（200 终端样本） | {out['terminal_spread']['C_sing_median']:.1f} | {out['terminal_spread']['C_sing_p5']:.1f} | {out['terminal_spread']['C_sing_p95']:.1f} |
| $C_{{\\text{{goal}}}}$（同批） | {out['terminal_spread']['C_goal_median']:.2f} | {out['terminal_spread']['C_goal_p5']:.2f} | {out['terminal_spread']['C_goal_p95']:.2f} |

$C_{{\\text{{sing}}}}$ 的 5–95% 跨度 {out['terminal_spread']['delta_C_sing_p95_p5']:.0f}，对应权重比 $e^{{-\\Delta C/\\lambda}}$ = {out['terminal_spread']['weight_ratio_for_delta']:.2e}（$\\lambda$={out['terminal_spread']['lambda']:.3f}）。**测量**：在样本间近似常数，软最大中大部分被抵消；但剩余变化仍可主导权重。

## 4. 对所选控制的影响

| 量 | 值 |
|---|---|
| 加/不加 $C_{{\\text{{sing}}}}$ 的 $\\Delta u$ 范数 | {out['control_effect']['delta_u_norm']:.4f} |
| 加权噪声范数（有/无） | {out['control_effect']['u_norm_with']:.4f} / {out['control_effect']['u_norm_without']:.4f} |
| 余弦相似度 | {out['control_effect']['cosine']:.3f} |

## 5. 近奇异敏感性

第一臂肩/肘二维网格（{out['singular_sweep']['grid_shoulder'][2]}×{out['singular_sweep']['grid_elbow'][2]}，范围 {out['singular_sweep']['grid_shoulder'][0]:.2f}–{out['singular_sweep']['grid_shoulder'][1]:.2f} rad）：

| 量 | 值 |
|---|---|
| $w$ 范围 | {out['singular_sweep']['w_min']:.3e} – {out['singular_sweep']['w_max']:.3e} |
| $w$ 最小处 (肩, 肘) | {out['singular_sweep']['q_at_wmin']} |
| 该处 $C_{{\\text{{sing}}}}$ | {out['singular_sweep']['C_sing_at_wmin']:.1f} |

## 6. 结论（不改公式）

1. $w$ **依赖长度单位**：在 $s\\in[0.01,100]$ 上的经验斜率为 {alpha:.3f}，但这不是物理量纲；混合平移/旋转行的 Jacobian 需要显式缩放约定或特征长度才能定义有物理意义的可操作度。
2. 因此 $p_e=10$ 与 $p_g=100$ 的比值依赖长度单位与缩放约定；论文没有给归一化，**标度无法从原文确定**。
3. 不将 $p_e/w$ 替换为 $p_e\\cdot w$：后者的优化方向相反且同样无量纲化不充分；如要改动需论文层面的数学论证。
4. 记录为 `OPEN_ISSUES.md` N3（`[需论文澄清]`）。
"""
    (reports / "N3_SINGULARITY_AUDIT.md").write_text(md, encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
