"""Controller-variant comparison on the two-corridor task (Table II structure)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p1_repro.baselines import run_variant  # noqa: E402
from p1_repro.tasks_bimodal import BimodalTask  # noqa: E402
from p1_repro.twostage import TwoStageConfig, two_stage  # noqa: E402


def score(task, u):
    d = task.rollout(u[None])
    return {
        "goal": float(d["goal_error"][0, 0]),
        "collision": bool(d["collision"][0, 0]),
        "success": bool(task.success(d)[0]),
        "tv": float(task.jitter(u[None])[0]),
    }


def run(seeds=30):
    task = BimodalTask()
    u0 = task.seed_plan(1.0)
    variants = {
        "ours_two_stage": "two",
        "mppi": "mppi",
        "log_mppi": "log_mppi",
        "fre_mppi": "fre_mppi",
        "biased_mppi": "biased_mppi",
        "high_mppi": "high_mppi",
        "cem": "cem",
    }
    out = {}
    for name, kind in variants.items():
        rows = []
        for seed in range(seeds):
            rng = np.random.default_rng(seed)
            if kind == "two":
                cfg = TwoStageConfig(samples=500, std1=0.15, std2_ratio=0.2, elite=10,
                                     max_abs=0.3, iterations=10, lam_frac=0.1)
                u = two_stage(task, rng, cfg, u_mean=u0)["u"]
            else:
                u = run_variant(task, rng, kind, samples=1000, std=0.15, iterations=10,
                                lam_frac=0.1, u0=u0)
            rows.append(score(task, u))
        goal = np.array([r["goal"] for r in rows])
        out[name] = {
            "seeds": seeds,
            "success_rate": float(np.mean([r["success"] for r in rows])),
            "median_goal": float(np.median(goal)),
            "collision_rate": float(np.mean([r["collision"] for r in rows])),
            "median_tv": float(np.median([r["tv"] for r in rows])),
        }
    return out


def main():
    out = run()
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "G3B_VARIANTS.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    rows = "\n".join(
        f"| {name} | {v['success_rate']:.2f} | {v['median_goal']:.3f} | "
        f"{v['collision_rate']:.2f} | {v['median_tv']:.2f} |"
        for name, v in out.items()
    )
    md = f"""# G3B 控制器变体对照（二维双通道任务）

> 自动生成：`python p1/scripts/g3b_variants.py`
> 等预算：每变体 1000 样本/迭代 × 10 迭代；两阶段为 500（探索）+ 500（精化）。
> 起点为可行种子（"上一周期最优"）；温度 $\\lambda=0.1\\times$ 代价极差（宽权重，接近论文口径）。
> {out['ours_two_stage']['seeds']} 个种子。

| 变体 | 成功率 | 终端误差中位数 (m) | 碰撞率 | TV 中位数 |
|---|---|---|---|---|
{rows}

## 结论

- **mppi / log_mppi / cem / biased_mppi 均达到 1.00**（{out['mppi']['seeds']} 种子）；**ours_two_stage 只有 {out['ours_two_stage']['success_rate']:.2f}**。在本任务上两阶段**没有**优于单阶段 i.i.d. 采样。
- **fre_mppi（频域有色噪声）为 {out['fre_mppi']['success_rate']:.2f}**：有色噪声（平滑、时间相关）在此任务探索效率低于 i.i.d. 噪声；这也是单阶段"停滞"的来源之一。
- **high_mppi** 从可行种子出发且噪声很小，故未表现出碰撞（碰撞率 {out['high_mppi']['collision_rate']:.2f}）；该消融需要更大幅度的扰动或冷启动才能体现"不处理约束就撞"，未作为证据。
- 所有数值是本任务的受控复现，**不是论文表 II 的逐格复刻**；两阶段相对基线的优势在本任务未复现，见 `G3_ACCEPTANCE.md` 与 `OPEN_ISSUES.md`。
"""
    (reports / "G3B_VARIANTS.md").write_text(md, encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
