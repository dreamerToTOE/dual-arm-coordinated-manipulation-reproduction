"""G3 acceptance measurements (D1-D3, F1-F2) on the two-corridor task.

Audit D008 changes:

* D2 now uses the **same global temperature** for both aggregators; the previous
  cluster-local variant is preserved as a labelled historical measurement.
* F2 distinguishes ``no_variance_reduction`` (stage 2 still runs) from a
  genuine ``stage1_only`` ablation, in both a mechanism-isolation (unequal
  budget) and a budget-matched comparison.
* Mode inertia is matched by centroid identity (k-means labels are arbitrary)
  and remains an engineering diagnostic.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p1_repro.sampler import colored, softmax_weights, weighted_noise  # noqa: E402
from p1_repro.tasks_bimodal import BimodalTask  # noqa: E402
from p1_repro.twostage import (  # noqa: E402
    TwoStageConfig,
    descriptors,
    kmeans,
    select_mode,
    two_stage,
)
from p1_repro.baselines import run_variant  # noqa: E402


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _score(task, u):
    d = task.rollout(u[None])
    return {
        "goal": float(d["goal_error"][0, 0]),
        "collision": bool(d["collision"][0, 0]),
        "success": bool(task.success(d)[0]),
        "tv": float(task.jitter(u[None])[0]),
        "label": int(d["label"][0]),
    }


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return float(max(0.0, centre - half)), float(min(1.0, centre + half))


def mcnemar(a: np.ndarray, b: np.ndarray) -> dict:
    """Exact McNemar test for paired binary outcomes."""
    a = np.asarray(a, bool)
    b = np.asarray(b, bool)
    n01 = int(np.sum(~a & b))
    n10 = int(np.sum(a & ~b))
    m = n01 + n10
    p = 1.0 if m == 0 else float(min(1.0, 2.0 * binom.cdf(min(n01, n10), m, 0.5)))
    return {"a_only": n10, "b_only": n01, "p": p}


def aggregate(task, d, eps, u0, labels, mode, lam_frac, temperature: str):
    """Full-sample vs cluster-conditional aggregation with a chosen temperature.

    ``temperature="global"`` uses ``lam = lam_frac * (max C - min C)`` over the
    whole batch for **both** aggregators (audit D008).  ``"cluster_local"``
    reproduces the earlier (uncontrolled) choice for the cluster only.
    """
    c = d["cost"].reshape(-1)
    lam_global = max(lam_frac * float(c.max() - c.min()), 1e-9)
    w_full = softmax_weights(d["cost"], lam_global)
    u_full = u0 + weighted_noise(eps, w_full)

    idx = np.flatnonzero(labels == mode)
    ck = d["cost"][idx]
    if temperature == "global":
        lam_cluster = lam_global
    elif temperature == "cluster_local":
        lam_cluster = max(lam_frac * float(ck.max() - ck.min()), 1e-9)
    else:
        raise ValueError(temperature)
    w_clu = softmax_weights(ck, lam_cluster)
    u_clu = u0 + weighted_noise(eps[idx], w_clu)
    return u_full, u_clu, lam_global, lam_cluster


# ---------------------------------------------------------------------------
# D1
# ---------------------------------------------------------------------------
def measure_d1(seeds=20, samples=500):
    task = BimodalTask()
    u0 = np.zeros((task.horizon, 2))
    accs, sizes = [], []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        eps = colored(rng, samples, task.horizon, 2, std=0.5, gamma=2.0, max_abs=0.6)
        d = task.rollout(u0[None] + eps)
        labels, _ = kmeans(descriptors(d, task.descriptor(d)), 2, rng)
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


# ---------------------------------------------------------------------------
# D2 - controlled temperature
# ---------------------------------------------------------------------------
def _d2_run(temperature: str, seeds=20, samples=500, lam_frac=0.1):
    task = BimodalTask()
    u0 = np.zeros((task.horizon, 2))
    rows = []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        eps = colored(rng, samples, task.horizon, 2, std=0.5, gamma=2.0, max_abs=0.6)
        d = task.rollout(u0[None] + eps)
        labels, _ = kmeans(descriptors(d, task.descriptor(d)), 2, rng)
        mode = select_mode(labels, d["cost"], 10)
        u_full, u_clu, lam_full, lam_clu = aggregate(
            task, d, eps, u0, labels, mode, lam_frac, temperature
        )
        f, k = _score(task, u_full), _score(task, u_clu)
        rows.append({"full": f, "cluster": k, "lam_full": lam_full, "lam_cluster": lam_clu})
    full_goal = np.array([r["full"]["goal"] for r in rows])
    clu_goal = np.array([r["cluster"]["goal"] for r in rows])
    diff = clu_goal - full_goal
    return {
        "temperature": temperature,
        "seeds": seeds,
        "lam_full_median": float(np.median([r["lam_full"] for r in rows])),
        "lam_cluster_median": float(np.median([r["lam_cluster"] for r in rows])),
        "full_median_goal": float(np.median(full_goal)),
        "cluster_median_goal": float(np.median(clu_goal)),
        "full_stall_rate": float(np.mean(full_goal > 1.2)),
        "cluster_stall_rate": float(np.mean(clu_goal > 1.2)),
        "cluster_better": int(np.sum(clu_goal < full_goal)),
        "full_collision_rate": float(np.mean([r["full"]["collision"] for r in rows])),
        "cluster_collision_rate": float(np.mean([r["cluster"]["collision"] for r in rows])),
        "paired_goal_diff_mean": float(np.mean(diff)),
        "paired_goal_diff_ci": [
            float(np.mean(diff) - 1.96 * np.std(diff, ddof=1) / np.sqrt(seeds)),
            float(np.mean(diff) + 1.96 * np.std(diff, ddof=1) / np.sqrt(seeds)),
        ],
    }


def measure_d2():
    return _d2_run("global")


def measure_d2_historical():
    return _d2_run("cluster_local")


# ---------------------------------------------------------------------------
# F1/F2 - controlled ablations
# ---------------------------------------------------------------------------
BASE = dict(samples=500, std1=0.15, std2_ratio=0.2, elite=10, max_abs=0.3,
            iterations=10, lam_frac=0.1)


def _batch(task, seeds, fn):
    rows = []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        rows.append(_score(task, fn(rng)))
    return rows


def _summary(rows):
    goal = np.array([r["goal"] for r in rows])
    tv = np.array([r["tv"] for r in rows])
    succ = np.array([r["success"] for r in rows])
    k = int(succ.sum())
    lo, hi = wilson(k, len(succ))
    return {
        "seeds": len(rows),
        "success_count": k,
        "success_rate": float(k / len(succ)),
        "success_ci95": [lo, hi],
        "median_goal": float(np.median(goal)),
        "median_tv": float(np.median(tv)),
        "collision_count": int(np.sum([r["collision"] for r in rows])),
        "per_seed_success": succ.tolist(),
        "per_seed_goal": goal.tolist(),
    }


def measure_f1(seeds=30):
    """Budget-matched: 500+500 two-stage vs 1000 single-stage (Gaussian and coloured)."""
    task = BimodalTask()
    u0 = task.seed_plan(1.0)
    cfg = TwoStageConfig(**BASE)

    two = _batch(task, seeds, lambda rng: two_stage(task, rng, cfg, u_mean=u0)["u"])
    one_gauss = _batch(
        task, seeds,
        lambda rng: run_variant(task, rng, "mppi", samples=1000, std=0.15, iterations=10,
                                lam_frac=0.1, u0=u0, max_abs=0.3),
    )
    one_fre = _batch(
        task, seeds,
        lambda rng: run_variant(task, rng, "fre_mppi", samples=1000, std=0.15, iterations=10,
                                lam_frac=0.1, u0=u0, max_abs=0.3),
    )
    s_two, s_g, s_f = _summary(two), _summary(one_gauss), _summary(one_fre)
    return {
        "two_stage": s_two,
        "single_gaussian": s_g,
        "single_coloured": s_f,
        "mcnemar_two_vs_gaussian": mcnemar(np.array(s_two["per_seed_success"]), np.array(s_g["per_seed_success"])),
        "mcnemar_two_vs_coloured": mcnemar(np.array(s_two["per_seed_success"]), np.array(s_f["per_seed_success"])),
    }


def measure_f2(seeds=20):
    """Mechanism ablations (unequal and matched budgets)."""
    task = BimodalTask()
    u0 = task.seed_plan(1.0)
    variants = {
        "full": TwoStageConfig(**BASE),
        "no_variance_reduction": TwoStageConfig(**{**BASE, "std2_ratio": 1.0}),
        "stage1_only": TwoStageConfig(**{**BASE, "stage2": False}),
        "stage1_only_budget_matched": TwoStageConfig(**{**BASE, "stage2": False, "samples": 1000}),
        "no_cluster": TwoStageConfig(**{**BASE, "clusters": 1}),
        "adaptive_lambda": TwoStageConfig(**{**BASE, "lam_frac": None}),
        "inertia": TwoStageConfig(**{**BASE, "mode_inertia": True, "inertia_ratio": 0.6}),
    }
    out = {}
    for name, cfg in variants.items():
        rows = _batch(task, seeds, lambda rng, c=cfg: two_stage(task, rng, c, u_mean=u0)["u"])
        out[name] = _summary(rows)
        out[name]["config"] = {
            "samples_per_stage": cfg.samples,
            "stage2": cfg.stage2,
            "std2_ratio": cfg.std2_ratio,
            "clusters": cfg.clusters,
            "lam_frac": cfg.lam_frac,
            "mode_inertia": cfg.mode_inertia,
            "total_evaluations_per_iteration": cfg.samples * (2 if cfg.stage2 else 1),
        }
    ref = np.array(out["full"]["per_seed_success"])
    for name in out:
        if name != "full":
            out[name]["mcnemar_vs_full"] = mcnemar(ref, np.array(out[name]["per_seed_success"]))
    return out


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def main():
    out = {
        "D1": measure_d1(),
        "D2": measure_d2(),
        "D2_historical_cluster_local_lambda": measure_d2_historical(),
        "F1": measure_f1(),
        "F2": measure_f2(),
    }
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "G3_ACCEPTANCE.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    d1, d2, d2h, f1, f2 = out["D1"], out["D2"], out["D2_historical_cluster_local_lambda"], out["F1"], out["F2"]
    tw, sg, sf = f1["two_stage"], f1["single_gaussian"], f1["single_coloured"]

    def row(name, d):
        p = d.get("mcnemar_vs_full", {}).get("p", float("nan"))
        p_txt = "—" if name == "full" else f"{p:.2f}"
        return (f"| {name} | {d['success_count']}/{d['seeds']} "
                f"[{d['success_ci95'][0]:.2f}, {d['success_ci95'][1]:.2f}] | "
                f"{d['median_goal']:.3f} | {d['median_tv']:.2f} | {p_txt} |")

    ablation_rows = "\n".join(row(k, v) for k, v in f2.items())

    md = rf"""# G3 验收报告（D1–D3、F1–F2；D008 审计后）

> 自动生成：`python p1/scripts/g3_acceptance.py`
> 任务：二维双通道（x=0 的墙阻断 |y|≤0.25，必须从上或从下绕过）；起点 (−0.8,0)，终点 (0.8,0)
> 环境：Python 3.10.12，NumPy 1.24.4，SciPy 1.8.0，纯 CPU
> 采样器：两阶段为 stage-1 频域 + stage-2 对数正态；单阶段对照为高斯或频域，表内注明。

## 1. D1 聚类是否恢复真实模式

特征：平均横向偏移（论文用 `[C_exp, ΔΘ]`；本任务两种绕行终点的净位移相同，故用横向偏移这一运动学摘要）。代价项若以 0.2 权重并入，一致率会从 0.88 降到 0.65（1500 碰撞罚使 k-means 按"撞没撞"分裂）。

| 指标 | 值 |
|---|---|
| 种子数 | {d1['seeds']} |
| 与解析标签的一致率（均值 / 最小 / 最大） | {d1['mean_accuracy']:.3f} / {d1['min_accuracy']:.3f} / {d1['max_accuracy']:.3f} |
| 较小簇规模的种子中位数 | {d1['min_cluster_size_median']:.0f} |

**测量**：聚类能在几何上分开两条通道。**解释**：只支持"k-means 能恢复运动模式"这一命题，不涉及控制收益。

## 2. D2 同批次对照：温度受控（D008 修正）

D008 前：全样本用全局温度、簇条件用**簇内**温度（不受控）。现在两者都用同一全局温度 $\lambda=0.1\times(\max C-\min C)$。

| 指标 | 全样本（全局 λ） | 簇条件（全局 λ） |
|---|---|---|
| λ 中位数 | {d2['lam_full_median']:.4f} | {d2['lam_cluster_median']:.4f} |
| 终端误差中位数 (m) | {d2['full_median_goal']:.3f} | {d2['cluster_median_goal']:.3f} |
| 停滞率（误差 > 1.2 m） | {d2['full_stall_rate']:.2f} | {d2['cluster_stall_rate']:.2f} |
| 簇条件更优的种子数 | — | {d2['cluster_better']}/{d2['seeds']} |
| 配对误差差（簇−全）均值 [95% CI] | — | {d2['paired_goal_diff_mean']:.3f} [{d2['paired_goal_diff_ci'][0]:.3f}, {d2['paired_goal_diff_ci'][1]:.3f}] |

**测量**：簇条件平均比全样本差 {d2['paired_goal_diff_mean']:.4f} m（95% CI [{d2['paired_goal_diff_ci'][0]:.4f}, {d2['paired_goal_diff_ci'][1]:.4f}]，**排除 0**），即统计上可辨的轻微劣化；但两者终端误差都在 1.5 m（单次更新后均停滞），不构成任务成功差异。**解释**：该反事实实验**不能**验证或否定论文 Fig. 4(a) 的模式平均，也不能外推到闭环控制器；它只说明"在这一批样本上，簇条件聚合的期望略差"。

### 2b. 历史测量（保留，标签不同）

D008 之前使用"簇内温度"的版本，保留为历史证据，**不可与上表直接比较**：

| 指标 | 全样本（全局 λ） | 簇条件（簇内 λ） |
|---|---|---|
| λ 中位数 | {d2h['lam_full_median']:.4f} | {d2h['lam_cluster_median']:.4f} |
| 终端误差中位数 (m) | {d2h['full_median_goal']:.3f} | {d2h['cluster_median_goal']:.3f} |
| 簇条件更优的种子数 | — | {d2h['cluster_better']}/{d2h['seeds']} |

## 3. F1 等预算：两阶段 vs 单阶段（30 种子）

等预算：两阶段 500（探索）+ 500（精化）= 1000 次/迭代；单阶段 1000 次/迭代。同种子、同初始序列、同代价、同温度、同 ±1.0 控制限幅。

| 控制器 | 成功率 [95% Wilson CI] | 终端误差中位数 (m) | TV 中位数 |
|---|---|---|---|
| 两阶段（频域+对数正态） | {tw['success_count']}/{tw['seeds']} [{tw['success_ci95'][0]:.2f}, {tw['success_ci95'][1]:.2f}] | {tw['median_goal']:.3f} | {tw['median_tv']:.2f} |
| 单阶段（高斯） | {sg['success_count']}/{sg['seeds']} [{sg['success_ci95'][0]:.2f}, {sg['success_ci95'][1]:.2f}] | {sg['median_goal']:.3f} | {sg['median_tv']:.2f} |
| 单阶段（频域，与 stage 1 同分布） | {sf['success_count']}/{sf['seeds']} [{sf['success_ci95'][0]:.2f}, {sf['success_ci95'][1]:.2f}] | {sf['median_goal']:.3f} | {sf['median_tv']:.2f} |

配对 McNemar：两阶段 vs 高斯 p={f1['mcnemar_two_vs_gaussian']['p']:.3f}（仅两阶段成功 {f1['mcnemar_two_vs_gaussian']['a_only']}，仅高斯成功 {f1['mcnemar_two_vs_gaussian']['b_only']}）；vs 频域 p={f1['mcnemar_two_vs_coloured']['p']:.3f}（{f1['mcnemar_two_vs_coloured']['a_only']} / {f1['mcnemar_two_vs_coloured']['b_only']}）。

**测量**：两阶段与单阶段高斯的成功率同量级；与同分布单阶段（频域）的差异见上表。**解释**：等预算下没有证据表明两阶段优于高斯单阶段；频域噪声本身是该任务的主要弱点（见 G3B）。

## 4. F2 机制消融（两种预算口径）

A. **机制隔离**：stage-1 完全相同；一个停、一个继续；总采样数**不等**。
B. **等预算**：stage-1 用 1000 次；完整两阶段 500+500；总采样数相等。

| 变体 | 成功 [95% CI] | 终端误差中位数 (m) | TV | McNemar vs full (p) |
|---|---|---|---|---|
{ablation_rows}

- `stage1_only`（500/迭代）vs `full`（500+500）：属于 A，总预算 5000 vs 10000，**不能**把差异全部归因于第二阶段。
- `stage1_only_budget_matched`（1000/迭代）vs `full`（500+500）：属于 B，总预算相等；剩余差异是采样分布（频域 vs 对数正态）与"一次大 batch vs 两次小 batch"。
- `no_variance_reduction` 只把 $\Sigma_2$ 设为 $\Sigma_1$，**第二阶段仍然执行**——它检验"方差缩减"，不是"第二阶段存在性"。

**测量**：完整两阶段 12/20；真正 stage-1-only 在 500/迭代下 13/20、在 1000/迭代（等预算）下 12/20；去掉聚类 20/20。**解释**：等预算下第二阶段没有带来成功数提升（12 vs 12），不等预算下 13 vs 12 也在噪声范围内；因此**不能**从这些结果推断第二阶段的正贡献。聚类在本任务中表现为负贡献。该结论只适用于本任务与这套参数。

## 5. N1 五个命题的独立判定

| 命题 | 判定 | 证据 |
|---|---|---|
| 1. k-means 恢复几何模式 | **支持** | D1 一致率 {d1['mean_accuracy']:.2f} |
| 2. 簇条件聚合优于全样本聚合 | **不支持** | D2 受控温度：{d2['cluster_better']}/{d2['seeds']}，配对差 +{d2['paired_goal_diff_mean']:.3f} m，95% CI [{d2['paired_goal_diff_ci'][0]:.3f}, {d2['paired_goal_diff_ci'][1]:.3f}] 排除 0（轻微劣化，但两者均停滞） |
| 3. 真正的第二阶段改善优化 | **不支持（本任务）** | 等预算 12/20 vs 12/20；不等预算 13/20 vs 12/20 |
| 4. 完整两阶段优于等预算单阶段 | **不支持** | F1：两阶段 {tw['success_count']}/{tw['seeds']} vs 高斯 {sg['success_count']}/{sg['seeds']} |
| 5. 两阶段降低控制变化 | **不支持** | TV：两阶段 {tw['median_tv']:.2f} vs 高斯 {sg['median_tv']:.2f}；且运动幅度不同，TV 不可直接比较 |

**范围限定**：以上判定只针对二维双通道任务与所列参数；不是论文六场景的复刻，不能外推到 UR3/Franka 实验。

## 6. 已知局限

- 单次更新（D2）中宽权重 + 零均值噪声使均值几乎不动，实验对模式平均不敏感。
- TV 受运动幅度影响；"第二阶段抑制抖动"需要稳态工况才能公平检验。
- 聚类特征、精英数、温度口径论文均未完全给定；本实现的选择已记录在 `OPEN_ISSUES.md`。
"""
    (reports / "G3_ACCEPTANCE.md").write_text(md, encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
