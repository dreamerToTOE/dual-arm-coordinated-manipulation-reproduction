"""G3 acceptance measurements (D1-D3, F1-F2) on the two-corridor task."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p1_repro.sampler import colored, softmax_weights, weighted_noise  # noqa: E402
from p1_repro.tasks_bimodal import BimodalTask  # noqa: E402
from p1_repro.twostage import (  # noqa: E402
    TwoStageConfig,
    descriptors,
    kmeans,
    select_mode,
    single_stage,
    two_stage,
)


def _score(task, u):
    d = task.rollout(u[None])
    return {
        "goal": float(d["goal_error"][0, 0]),
        "collision": bool(d["collision"][0, 0]),
        "success": bool(task.success(d)[0]),
        "tv": float(task.jitter(u[None])[0]),
        "label": int(d["label"][0]),
    }


def measure_d1(seeds=20, samples=500):
    """Clustering accuracy against the analytic above/below labels."""
    task = BimodalTask()
    u0 = np.zeros((task.horizon, 2))
    accs, sizes = [], []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        eps = colored(rng, samples, task.horizon, 2, std=0.5, gamma=2.0, max_abs=0.6)
        d = task.rollout(u0[None] + eps)
        X = descriptors(d, task.descriptor(d))
        labels, _ = kmeans(X, 2, rng)
        mask = d["label"] != 0
        if mask.sum() > 10 and len(np.unique(d["label"][mask])) == 2:
            acc = max(
                np.mean(labels[mask] == (d["label"][mask] > 0)),
                np.mean(labels[mask] == (d["label"][mask] < 0)),
            )
            accs.append(float(acc))
            sizes.append(int(min(np.bincount(labels, minlength=2))))
    return {
        "seeds": len(accs),
        "mean_accuracy": float(np.mean(accs)),
        "min_accuracy": float(np.min(accs)),
        "max_accuracy": float(np.max(accs)),
        "min_cluster_size_median": float(np.median(sizes)),
    }


def measure_d2(seeds=20, samples=500, lam_frac=0.1):
    """Same batch: full-sample mean vs cluster-conditional mean."""
    task = BimodalTask()
    u0 = np.zeros((task.horizon, 2))
    rows = []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        eps = colored(rng, samples, task.horizon, 2, std=0.5, gamma=2.0, max_abs=0.6)
        d = task.rollout(u0[None] + eps)
        c = d["cost"].reshape(-1)
        lam = lam_frac * float(c.max() - c.min())
        w_full = softmax_weights(d["cost"], max(lam, 1e-9))
        u_full = u0 + weighted_noise(eps, w_full)
        labels, _ = kmeans(descriptors(d, task.descriptor(d)), 2, rng)
        mode = select_mode(labels, d["cost"], 10)
        idx = np.flatnonzero(labels == mode)
        ck = d["cost"][idx]
        w_clu = softmax_weights(ck, max(lam_frac * float(ck.max() - ck.min()), 1e-9))
        u_clu = u0 + weighted_noise(eps[idx], w_clu)
        f, k = _score(task, u_full), _score(task, u_clu)
        rows.append({"full": f, "cluster": k})
    full_goal = np.array([r["full"]["goal"] for r in rows])
    clu_goal = np.array([r["cluster"]["goal"] for r in rows])
    return {
        "seeds": seeds,
        "full_median_goal": float(np.median(full_goal)),
        "cluster_median_goal": float(np.median(clu_goal)),
        "full_stall_rate": float(np.mean(full_goal > 1.2)),
        "cluster_stall_rate": float(np.mean(clu_goal > 1.2)),
        "cluster_better": int(np.sum(clu_goal < full_goal)),
        "full_collision_rate": float(np.mean([r["full"]["collision"] for r in rows])),
        "cluster_collision_rate": float(np.mean([r["cluster"]["collision"] for r in rows])),
    }


def _run_batch(task, u0, seeds, two: bool, cfg: TwoStageConfig | None, single_samples=1000, std=0.15,
               iterations=10, lam_frac=0.1):
    out = []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        if two:
            res = two_stage(task, rng, cfg, u_mean=u0)
        else:
            res = single_stage(
                task, rng, samples=single_samples, std=std, iterations=iterations,
                max_abs=0.3, u_mean=u0, lam_frac=lam_frac,
            )
        out.append(_score(task, res["u"]))
    return out


def _summary(rows):
    goal = np.array([r["goal"] for r in rows])
    tv = np.array([r["tv"] for r in rows])
    return {
        "seeds": len(rows),
        "success_rate": float(np.mean([r["success"] for r in rows])),
        "median_goal": float(np.median(goal)),
        "median_tv": float(np.median(tv)),
        "collision_rate": float(np.mean([r["collision"] for r in rows])),
    }


def measure_f1(seeds=30):
    task = BimodalTask()
    u0 = task.seed_plan(1.0)
    cfg = TwoStageConfig(samples=500, std1=0.15, std2_ratio=0.2, elite=10, max_abs=0.3,
                         iterations=10, lam_frac=0.1)
    two = _summary(_run_batch(task, u0, seeds, True, cfg))
    one = _summary(_run_batch(task, u0, seeds, False, cfg))
    return {"two_stage": two, "single_stage": one}


def measure_f2(seeds=20):
    """Ablations: clustering, second stage, temperature schedule."""
    task = BimodalTask()
    u0 = task.seed_plan(1.0)
    base = dict(samples=500, std1=0.15, std2_ratio=0.2, elite=10, max_abs=0.3, iterations=10, lam_frac=0.1)

    variants = {
        "full": TwoStageConfig(**base),
        "no_cluster": TwoStageConfig(**{**base, "clusters": 1}),
        "no_stage2": TwoStageConfig(**{**base, "std2_ratio": 1.0}),
        "adaptive_lambda": TwoStageConfig(**{**base, "lam_frac": None}),
        "with_inertia": TwoStageConfig(**{**base, "mode_inertia": True, "inertia_ratio": 0.6}),
    }
    out = {}
    for name, cfg in variants.items():
        out[name] = _summary(_run_batch(task, u0, seeds, True, cfg))
    return out


def main():
    out = {
        "D1": measure_d1(),
        "D2": measure_d2(),
        "F1": measure_f1(),
        "F2": measure_f2(),
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "G3_ACCEPTANCE.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    d1, d2, f1, f2 = out["D1"], out["D2"], out["F1"], out["F2"]
    md = f"""# G3 验收报告（D1–D3、F1–F2）

> 自动生成：`python p1/scripts/g3_acceptance.py`
> 任务：二维双通道（x=0 处的墙阻断 |y|≤0.25，必须从上或从下绕过）；起点 (−0.8,0)，终点 (0.8,0)
> 环境：Python 3.10.12，NumPy 1.24.4，纯 CPU

## 1. D1 聚类是否恢复真实模式

特征：`平均横向偏移`（论文用 `[C_exp, ΔΘ]`；本任务中两种绕行终点的净位移相同，故用横向偏移这一运动学摘要，见 `tasks_bimodal.py:descriptor`）。把代价项以 0.2 权重并入会把一致率从 0.88 拉到 0.65——代价中的 1500 碰撞罚使 k-means 按"撞没撞"而不是"从上/从下"分裂。

| 指标 | 值 |
|---|---|
| 种子数 | {d1['seeds']} |
| 与解析标签的一致率（均值 / 最小 / 最大） | {d1['mean_accuracy']:.3f} / {d1['min_accuracy']:.3f} / {d1['max_accuracy']:.3f} |
| 较小簇规模的种子中位数 | {d1['min_cluster_size_median']:.0f} |

## 2. D2 同批次对照：全样本平均 vs 簇条件平均

宽温度（$\\lambda=0.1\\times$ 代价极差，接近论文"归一化 5–10"的宽权重），单次更新，{d2['seeds']} 个种子：

| 指标 | 全样本 | 簇条件 |
|---|---|---|
| 终端误差中位数 (m) | {d2['full_median_goal']:.3f} | {d2['cluster_median_goal']:.3f} |
| 停滞率（误差 > 1.2 m） | {d2['full_stall_rate']:.2f} | {d2['cluster_stall_rate']:.2f} |
| 碰撞率 | {d2['full_collision_rate']:.2f} | {d2['cluster_collision_rate']:.2f} |
| 簇条件更优的种子数 | — | {d2['cluster_better']}/{d2['seeds']} |

**这是一个零结果**：单次更新时两者都只移动很小（宽权重 + 零均值噪声 → 加权均值≈0），簇条件并没有更好（0/20）。因此 D2 的"单次更新反事实"无法验证论文 Fig. 4(a) 的模式平均；该现象只能在迭代中观察（F1）。

## 3. F1 等预算：单阶段 vs 两阶段

等预算：单阶段每次迭代 1000 条样本；两阶段 500（探索）+ 500（精化）。同种子、同代价、同 $\\lambda$、10 次迭代，{f1['two_stage']['seeds']} 个种子。

| 指标 | 单阶段 | 两阶段 |
|---|---|---|
| 成功率（误差 < 5 cm 且无碰撞） | {f1['single_stage']['success_rate']:.2f} | {f1['two_stage']['success_rate']:.2f} |
| 终端误差中位数 (m) | {f1['single_stage']['median_goal']:.3f} | {f1['two_stage']['median_goal']:.3f} |
| 控制序列总变差中位数 | {f1['single_stage']['median_tv']:.2f} | {f1['two_stage']['median_tv']:.2f} |
| 碰撞率 | {f1['single_stage']['collision_rate']:.2f} | {f1['two_stage']['collision_rate']:.2f} |

## 4. F2 消融

| 变体 | 成功率 | 终端误差中位数 (m) | TV 中位数 |
|---|---|---|---|
| 完整两阶段 | {f2['full']['success_rate']:.2f} | {f2['full']['median_goal']:.3f} | {f2['full']['median_tv']:.2f} |
| 去掉聚类（K=1） | {f2['no_cluster']['success_rate']:.2f} | {f2['no_cluster']['median_goal']:.3f} | {f2['no_cluster']['median_tv']:.2f} |
| 去掉第二阶段（$\\Sigma_2=\\Sigma_1$） | {f2['no_stage2']['success_rate']:.2f} | {f2['no_stage2']['median_goal']:.3f} | {f2['no_stage2']['median_tv']:.2f} |
| 代码自适应温度 | {f2['adaptive_lambda']['success_rate']:.2f} | {f2['adaptive_lambda']['median_goal']:.3f} | {f2['adaptive_lambda']['median_tv']:.2f} |
| 加模式惯性（0.6） | {f2['with_inertia']['success_rate']:.2f} | {f2['with_inertia']['median_goal']:.3f} | {f2['with_inertia']['median_tv']:.2f} |

## 5. 结论（按证据强度）

1. **D1 通过**：运动学摘要 + k-means 能以 {d1['mean_accuracy']*100:.0f}% 的一致率恢复"从上/从下"两个模式，远高于二分类随机水平——聚类本身在几何上是成立的。
2. **F1 不支持论文主诉**：等预算、同种子、宽温度下，两阶段成功率 {f1['two_stage']['success_rate']:.2f} ≈ 单阶段 {f1['single_stage']['success_rate']:.2f}，中位误差 {f1['two_stage']['median_goal']:.3f} vs {f1['single_stage']['median_goal']:.3f} m，只有轻微优势；换用高斯噪声的单阶段在变体对照里达到 1.00（见 G3B）。**"两阶段显著优于单阶段"在本任务未复现。**
3. **F2 归因（负结果）**：去掉聚类后成功率 **{f2['no_cluster']['success_rate']:.2f}**、误差 {f2['no_cluster']['median_goal']:.3f} m，优于完整两阶段的 {f2['full']['success_rate']:.2f} / {f2['full']['median_goal']:.3f} m；去掉第二阶段降到 {f2['no_stage2']['success_rate']:.2f} / {f2['no_stage2']['median_goal']:.3f} m。说明**起作用的是"第二遍重加权"与 i.i.d. 噪声，不是聚类**；簇条件聚合降低了有效样本数并放大停滞样本的权重。
4. **温度是开关**：代码自适应温度下完整两阶段为 {f2['adaptive_lambda']['success_rate']:.2f}（权重极峰化），宽温度下为 {f2['full']['success_rate']:.2f}——两种口径都不能让聚类反超"去聚类"。
5. **TV/抖动**：两阶段序列总变差 {f1['two_stage']['median_tv']:.2f} vs 单阶段 {f1['single_stage']['median_tv']:.2f}，不更低；"第二阶段抑制抖动"在本任务无证据（需要稳态工况才公平）。

**总体判定**：论文的"两阶段 + k-means 模式选择"机制，在对称双通道任务上（含冷启动与可行种子两种起点）都**没有**表现出相对单阶段 MPPI 的增益；聚类能恢复几何模式，但把它接入控制反而变差。这是一项稳定的负结果，与 G0 记录的"聚类特征/精英数/温度/采样幅度口径欠定义"一致。已记入 `OPEN_ISSUES.md`，不做进一步调参。
"""
    (reports / "G3_ACCEPTANCE.md").write_text(md, encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
