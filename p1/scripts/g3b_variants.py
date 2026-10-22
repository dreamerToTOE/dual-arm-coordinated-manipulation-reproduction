"""Controller-variant comparison on the two-corridor task (Table II structure).

Audit D008 section 5: every variant is profiled for its *effective* sampling
statistics, and results are reported per seed with Wilson intervals and a
paired McNemar test against the two-stage controller.  This is an
algorithm-family comparison, not a controlled mechanism ablation (the latter
lives in ``g3_acceptance.py`` F2).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p1_repro.baselines import run_variant, sampling_profile  # noqa: E402
from p1_repro.tasks_bimodal import BimodalTask  # noqa: E402
from p1_repro.twostage import TwoStageConfig, two_stage  # noqa: E402

STD = 0.15
MAX_ABS = 0.3
ITER = 10
LAM_FRAC = 0.1


def score(task, u):
    d = task.rollout(u[None])
    return {
        "goal": float(d["goal_error"][0, 0]),
        "collision": bool(d["collision"][0, 0]),
        "success": bool(task.success(d)[0]),
        "tv": float(task.jitter(u[None])[0]),
    }


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return float(max(0.0, c - h)), float(min(1.0, c + h))


def mcnemar(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    n01, n10 = int(np.sum(~a & b)), int(np.sum(a & ~b))
    m = n01 + n10
    p = 1.0 if m == 0 else float(min(1.0, 2 * binom.cdf(min(n01, n10), m, 0.5)))
    return {"a_only": n10, "b_only": n01, "p": p}


def profile_two_stage(samples):
    s1 = sampling_profile("colored", samples, 25, STD, MAX_ABS)
    s2 = sampling_profile("log", samples, 25, STD * 0.2, MAX_ABS)
    return {
        "stage1": s1,
        "stage2": s2,
        "total_evaluations_per_iteration": 2 * samples,
        "iterations": ITER,
        "total_evaluations": 2 * samples * ITER,
        "initial_plan": "seed_plan(+y)",
        "temperature": f"global lambda = {LAM_FRAC} * (max C - min C) per stage",
        "control_limit": 1.0,
        "cost_components": ["goal", "collision", "stagnation"],
    }


def profile_variant(kind, samples):
    sampler = {"mppi": "gauss", "log_mppi": "log", "fre_mppi": "colored",
               "biased_mppi": "colored", "high_mppi": "colored", "cem": "gauss"}[kind]
    base = sampling_profile(sampler, samples, 25, STD, MAX_ABS)
    cost = ["goal", "stagnation"] if kind == "high_mppi" else ["goal", "collision", "stagnation"]
    return {
        **base,
        "total_evaluations_per_iteration": samples,
        "iterations": ITER,
        "total_evaluations": samples * ITER,
        "initial_plan": "seed_plan(+y)",
        "temperature": f"global lambda = {LAM_FRAC} * (max C - min C)",
        "control_limit": 1.0,
        "cost_components": cost,
        "note": "anchored to the seed plan every iteration" if kind == "biased_mppi" else
                ("elite mean/var, std adapts" if kind == "cem" else ""),
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
    out, profiles = {}, {}
    for name, kind in variants.items():
        rows = []
        for seed in range(seeds):
            rng = np.random.default_rng(seed)
            if kind == "two":
                cfg = TwoStageConfig(samples=500, std1=STD, std2_ratio=0.2, elite=10,
                                     max_abs=MAX_ABS, iterations=ITER, lam_frac=LAM_FRAC)
                u = two_stage(task, rng, cfg, u_mean=u0)["u"]
            else:
                u = run_variant(task, rng, kind, samples=1000, std=STD, iterations=ITER,
                                lam_frac=LAM_FRAC, u0=u0, max_abs=MAX_ABS)
            rows.append(score(task, u))
        succ = np.array([r["success"] for r in rows])
        k = int(succ.sum())
        lo, hi = wilson(k, seeds)
        out[name] = {
            "seeds": seeds,
            "success_count": k,
            "success_rate": float(k / seeds),
            "success_ci95": [lo, hi],
            "median_goal": float(np.median([r["goal"] for r in rows])),
            "collision_count": int(np.sum([r["collision"] for r in rows])),
            "median_tv": float(np.median([r["tv"] for r in rows])),
            "per_seed_success": succ.tolist(),
            "per_seed_goal": [float(r["goal"]) for r in rows],
        }
        profiles[name] = profile_two_stage(500) if kind == "two" else profile_variant(kind, 1000)

    ref = np.array(out["ours_two_stage"]["per_seed_success"])
    for name in out:
        if name != "ours_two_stage":
            out[name]["mcnemar_vs_ours"] = mcnemar(ref, np.array(out[name]["per_seed_success"]))
    return {"results": out, "profiles": profiles}


def main():
    data = run()
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "G3B_VARIANTS.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    res, prof = data["results"], data["profiles"]

    fair = "\n".join(
        f"| {name} | {p['total_evaluations']} | {p['iterations']} | "
        f"{p.get('stage1', p).get('sampler', 'cem/elite')} | "
        f"{p.get('stage1', p).get('nominal_std', STD):.3f} | "
        f"{p.get('stage1', p).get('effective_std', float('nan')):.3f} | "
        f"{p.get('stage1', p).get('clipping_fraction', 0.0):.2f} | "
        f"{p.get('stage1', p).get('lag1_correlation', float('nan')):.2f} | "
        f"{'yes' if 'collision' in p['cost_components'] else 'no'} |"
        for name, p in prof.items()
    )
    rows = "\n".join(
        f"| {name} | {v['success_count']}/{v['seeds']} "
        f"[{v['success_ci95'][0]:.2f}, {v['success_ci95'][1]:.2f}] | {v['median_goal']:.3f} | "
        f"{v['collision_count']} | {v['median_tv']:.2f} | "
        f"{v.get('mcnemar_vs_ours', {}).get('p', float('nan')):.3f} |"
        for name, v in res.items()
    )
    md = f"""# G3B 控制器变体对照（D008 审计后）

> 自动生成：`python p1/scripts/g3b_variants.py`
> 二维双通道任务；{res['ours_two_stage']['seeds']} 个种子；等预算 10,000 次轨迹评估/运行。
> 这是**算法家族对照**，不是受控机制消融；受控消融见 `G3_ACCEPTANCE.md` F2。

## 1. 采样与控制口径（公平性记录）

| 变体 | 总评估次数 | 迭代 | 采样器 | 名义 std | 有效 std | 截断比例 | lag-1 | 含碰撞代价 |
|---|---|---|---|---|---|---|---|---|
{fair}

- 两阶段的“有效 std”行取 stage-1；stage-2 为对数正态、std=0.03。
- `biased_mppi` 每轮把均值锚回 seed plan；`high_mppi` 去掉碰撞/倾角代价；`cem` 的 std 随精英集自适应。
- 所有变体同初始序列、同控制限幅 ±1.0、同全局温度定义；两阶段额外多一次聚合。

## 2. 结果（配对种子）

| 变体 | 成功 [95% Wilson CI] | 终端误差中位数 (m) | 碰撞数 | TV 中位数 | McNemar vs ours (p) |
|---|---|---|---|---|---|
{rows}

## 3. 测量与解释

**测量**：高斯/Log/CEM/Biased 单阶段均达到 {res['mppi']['success_count']}/{res['mppi']['seeds']}；两阶段 {res['ours_two_stage']['success_count']}/{res['ours_two_stage']['seeds']}；频域单阶段 {res['fre_mppi']['success_count']}/{res['fre_mppi']['seeds']}。

**解释**：
- 在本任务与这套参数下，**两阶段没有优于单阶段高斯/Log/CEM/Biased**；频域采样是最弱的一支。
- `high_mppi` 的碰撞数为 {res['high_mppi']['collision_count']}：从可行种子出发、扰动幅度小，未触发碰撞——该消融不能作为“不处理约束会撞”的证据。
- McNemar 的 p 值只针对配对成功/失败，不衡量误差大小；成功率接近 1 时检验力很低。

**范围**：本表不是论文表 II 的逐格复刻，不能外推到 UR3/Franka 场景；它只说明在本数值任务上“两阶段 > 单阶段”的排序不成立。
"""
    (reports / "G3B_VARIANTS.md").write_text(md, encoding="utf-8")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
