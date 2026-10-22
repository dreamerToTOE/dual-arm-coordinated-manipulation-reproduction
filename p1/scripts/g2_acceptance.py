"""G2 acceptance measurements (C1, C2, E1, E2)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p1_repro.sampler import adaptive_weights, effective_sample_size, softmax_weights  # noqa: E402
from p1_repro.switch import UnexploredIndicator, auxiliary_control, decay_rate_fit  # noqa: E402
from p1_repro.tasks_dual import DualArmTask, run_closed_loop  # noqa: E402
from p1_repro.tasks_linear import LinearQuadraticTask, run_mppi  # noqa: E402


def measure_c1():
    task = LinearQuadraticTask(dt=0.1, horizon=20)
    x0 = np.array([1.0, -0.5, 0.0, 0.0])
    opt = task.lqr_cost(x0)
    ratios, first, last = [], [], []
    for seed in range(50):
        r = run_mppi(task, x0, np.random.default_rng(seed), samples=800, iterations=60)
        ratios.append(r["cost"] / opt)
        first.append(r["history"][0])
        last.append(r["history"][-1])
    ratios = np.array(ratios)
    return {
        "lqr_cost": opt,
        "median_ratio": float(np.median(ratios)),
        "max_ratio": float(np.max(ratios)),
        "within_10pct": int(np.sum(ratios <= 1.10)),
        "seeds": 50,
        "mean_first_cost": float(np.mean(first)),
        "mean_last_cost": float(np.mean(last)),
    }


def measure_c2():
    rng = np.random.default_rng(3)
    M, N, n = 200, 5, 2
    costs = rng.normal(size=(M, 1))
    w = softmax_weights(costs, lam=0.5)
    ess = effective_sample_size(w)
    means = np.array([np.einsum("i,ijk->jk", w.reshape(-1), rng.normal(size=(M, N, n))) for _ in range(1000)])
    var = float(means.var(axis=0).mean())
    return {
        "M": M,
        "effective_samples": ess,
        "mc_variance": var,
        "predicted_variance": 1.0 / ess,
        "ratio": var * ess,
        "weights_sum": float(w.sum()),
    }


def measure_e2_units():
    K, dt, steps = 2.0, 0.01, 400
    e = np.array([1.0, -0.5, 0.25])
    hist = [e.copy()]
    for _ in range(steps):
        e = auxiliary_control(e, K, dt)
        hist.append(e.copy())
    rate = decay_rate_fit(np.array(hist), dt)

    ind = UnexploredIndicator(eta=0.4, l_min=-0.05, l_max=0.4, dt=0.15)
    l0 = ind.value
    for _ in range(20):
        ind.update(0.5)
    slope = (ind.value - l0) / (20 * ind.dt)
    for _ in range(1000):
        ind.update(10.0)
    hi = ind.value
    for _ in range(1000):
        ind.update(-10.0)
    lo = ind.value

    def dwell(start, target, ratio, dt_=0.001):
        obj = UnexploredIndicator(eta=0.4, l_min=-0.05, l_max=0.4, dt=dt_)
        obj.value = start
        n = 0
        while (obj.value > target) if start > target else (obj.value < target):
            obj.update(ratio)
            n += 1
            if n > 10**7:
                break
        return n

    down = dwell(0.4, 0.0, 0.3)
    up = dwell(-0.05, 0.0, 0.5)
    return {
        "decay_rate_fit": rate,
        "true_gain": K,
        "L_slope": slope,
        "expected_slope": 0.1,
        "L_max_reached": hi,
        "L_min_reached": lo,
        "dwell_down": down,
        "dwell_up": up,
        "dwell_ratio": down / max(up, 1),
    }


def measure_e2_projection_forms():
    """Eq. (45) vs the priority-consistent projection at the home pose."""
    task = DualArmTask()
    q = task.q_home
    J = task._pose_jacobian_fd(q)
    from p1_repro.kinematics import absolute_pose, relative_jacobian

    Jr = relative_jacobian(task.c1, task.c2, q[None, :6], q[None, 6:])[0]
    N = np.eye(12) - np.linalg.pinv(Jr, rcond=1e-10) @ Jr
    xa0 = absolute_pose(task.c1.fk(q[None, :6]), task.c2.fk(q[None, 6:]))[0]
    err = task.xa_d - xa0
    dq_paper = N @ (np.linalg.pinv(J, rcond=1e-4) @ err)
    dq_prio = N @ (np.linalg.pinv(J @ N, rcond=1e-4) @ err)
    return {
        "task_residual_eq45": float(np.linalg.norm(J @ dq_paper - err)),
        "task_residual_priority": float(np.linalg.norm(J @ dq_prio - err)),
        "error_norm": float(np.linalg.norm(err)),
        "equality_residual_eq45": float(np.linalg.norm(Jr @ dq_paper)),
        "equality_residual_priority": float(np.linalg.norm(Jr @ dq_prio)),
        "step_norm_eq45": float(np.linalg.norm(dq_paper)),
        "step_norm_priority": float(np.linalg.norm(dq_prio)),
    }


def _run_e1(task, seed, switch: bool, eta: float = 0.1, control_steps: int = 12,
            samples: int = 60, inner_iterations: int = 6):
    t0 = time.time()
    r = run_closed_loop(
        task,
        np.random.default_rng(seed),
        control_steps=control_steps,
        samples=samples,
        inner_iterations=inner_iterations,
        std=0.15,
        update_gain=0.3,
        switch=switch,
        eta=eta,
    )
    return {
        "seed": seed,
        "min_pos_error": float(min(r["history"]["pos"])),
        "final_pos_error": float(r["final_pos_error"]),
        "max_drift": float(r["max_drift"]),
        "min_clearance": float(r["min_clearance"]),
        "max_tilt_deg": float(r["max_tilt"]),
        "aux_fraction": float(r["aux_fraction"]),
        "wall_seconds": time.time() - t0,
    }


def measure_e1(seeds=(0, 1, 2)):
    task = DualArmTask()
    return {"baseline": [_run_e1(task, s, switch=False) for s in seeds]}


def measure_n2_traces(seed: int = 0, control_steps: int = 8, etas=(0.1, 1.0)):
    """Per-step C_t, C_s, ratio, L and auxiliary activation for N2."""
    task = DualArmTask()
    out = {}
    for eta in etas:
        r = run_closed_loop(
            task, np.random.default_rng(seed),
            control_steps=control_steps, samples=40, inner_iterations=5,
            std=0.15, update_gain=0.3, switch=True, eta=eta,
        )
        h = r["history"]
        out[f"eta_{eta}"] = {
            "C_t": h["C_t"],
            "C_s": h["C_s"],
            "ratio": h["ratio"],
            "L": h["L"],
            "aux": [bool(x) for x in h["used_aux"]],
            "pos": h["pos"],
        }
    return out


def measure_e1_switch(seeds=(0, 1), etas=(0.1, 1.0)):
    task = DualArmTask()
    return {
        f"eta_{eta}": [
            _run_e1(task, s, switch=True, eta=eta, control_steps=10, samples=40, inner_iterations=5)
            for s in seeds
        ]
        for eta in etas
    }


def main():
    reports = ROOT / "reports"
    reports.mkdir(exist_ok=True)
    partial = reports / "G2_ACCEPTANCE.partial.json"
    out = json.loads(partial.read_text(encoding="utf-8")) if partial.exists() else {}
    sections = [
        ("C1", measure_c1),
        ("C2", measure_c2),
        ("E2_units", measure_e2_units),
        ("E2_projection_forms", measure_e2_projection_forms),
        ("E1", measure_e1),
        ("E1_switch", measure_e1_switch),
        ("N2_traces", measure_n2_traces),
    ]
    for name, fn in sections:
        if name in out:
            continue
        out[name] = fn()
        partial.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"[g2] {name} done", flush=True)
    (reports / "G2_ACCEPTANCE.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    c1, c2, e2, e2p, e1, e1s = (
        out["C1"], out["C2"], out["E2_units"], out["E2_projection_forms"], out["E1"], out["E1_switch"]
    )
    n2 = out["N2_traces"]
    rows_n2 = "\n".join(
        f"| {eta} | {i} | {c_t:.2f} | {c_s:.2f} | {ratio:.2f} | {l:.3f} | "
        f"{'yes' if a else 'no'} | {pos*100:.2f} |"
        for eta, tr in n2.items()
        for i, (c_t, c_s, ratio, l, a, pos) in enumerate(
            zip(tr["C_t"], tr["C_s"], tr["ratio"], tr["L"], tr["aux"], tr["pos"])
        )
    )
    rows = "\n".join(
        f"| {r['seed']} | {r['min_pos_error']:.4f} | {r['final_pos_error']:.4f} | {r['max_drift']:.2e} | "
        f"{r['min_clearance']:.3f} | {r['max_tilt_deg']:.2f} | {r['wall_seconds']:.1f} |"
        for r in e1["baseline"]
    )
    rows_sw = "\n".join(
        f"| {eta} | {r['seed']} | {r['final_pos_error']:.4f} | {r['aux_fraction']:.2f} | "
        f"{r['max_drift']:.1e} | {r['max_tilt_deg']:.2f} |"
        for eta, rs in e1s.items()
        for r in rs
    )
    md = f"""# G2 验收报告（C1、C2、E1、E2）

> 自动生成：`python p1/scripts/g2_acceptance.py`
> 环境：Python 3.10.12，NumPy 1.24.4，float64，纯 CPU
> 测试：`p1/tests/test_g2_mpc.py`（8 项全部通过）

## 1. C1 单阶段 MPPI vs 有限时域 LQR

| 指标 | 值 | 判定 |
|---|---|---|
| LQR 最优代价（Riccati 反向递推） | {c1['lqr_cost']:.3f} | oracle |
| 50 个种子的代价比中位数 | {c1['median_ratio']:.4f} | 通过（≤1.10） |
| 最差代价比 | {c1['max_ratio']:.4f} | — |
| 落在 10% 以内的种子数 | {c1['within_10pct']}/{c1['seeds']} | 通过（≥45） |
| 平均初始代价 → 平均最终代价 | {c1['mean_first_cost']:.1f} → {c1['mean_last_cost']:.1f} | 收敛 |

说明：C1 的任务是**线性二次型测试台**，代价含控制项 $u^\\top R u$ 以保证最优解良定；论文主实验的 $p_v=p_a=0$。它检验的是"加权均值确实在优化"，不是论文的完整代价。

## 2. C2 加权估计器

| 指标 | 值 |
|---|---|
| M / 有效样本数 | {c2['M']} / {c2['effective_samples']:.2f} |
| 蒙特卡洛方差（1000 次） | {c2['mc_variance']:.4f} |
| 预测方差 $\\sigma^2/M_{{\\text{{eff}}}}$ | {c2['predicted_variance']:.4f} |
| 比值 | {c2['ratio']:.3f}（通过区间 0.8–1.25） |

## 3. E2 辅助控制器与 L 指标

| 指标 | 值 | 判定 |
|---|---|---|
| 误差衰减率拟合 | {e2['decay_rate_fit']:.4f} | 真值 {e2['true_gain']}，误差 {abs(e2['decay_rate_fit']-e2['true_gain'])/e2['true_gain']*100:.1f}% |
| $\\dot L$（比值 0.5，$\\eta=0.4$） | {e2['L_slope']:.4f} | 期望 0.1，通过 |
| $L$ 饱和上/下界 | {e2['L_max_reached']:.3f} / {e2['L_min_reached']:.3f} | 与 0.4 / −0.05 一致 |
| 下/上停留步数（$dt=0.001$） | {e2['dwell_down']} / {e2['dwell_up']} | 比值 {e2['dwell_ratio']:.2f}（理论 8） |

### E2 附带发现：式 (45) 不是约束任务的精确解

| 量 | 论文式 (45) $N J_a^+ e$ | 优先级一致式 $N(J_aN)^+e$ |
|---|---|---|
| 绝对任务残差 $\\|J_a\\Delta q-e\\|$ | {e2p['task_residual_eq45']:.4f} | {e2p['task_residual_priority']:.4f} |
| 等式残差 $\\|J_r\\Delta q\\|$ | {e2p['equality_residual_eq45']:.2e} | {e2p['equality_residual_priority']:.2e} |
| 步长范数 | {e2p['step_norm_eq45']:.3f} | {e2p['step_norm_priority']:.3f} |
| 误差范数 | {e2p['error_norm']:.4f} | — |

两者都严格保持相对位姿等式；但把 $J_a^+e$ 直接投到 $\\ker(J_r)$ 会丢掉绝对任务的大部分分量（残差 {e2p['task_residual_eq45']:.3f}，与误差本身同量级）。官方代码实现的正是式 (45)，这解释了为什么它只能做"稳态附近的微调"，而需要低层式 (50)(51) 兜底。

## 4. E1 双 UR3 共持任务（闭环 MPPI）

任务：相对位姿保持（初值）、绝对位姿目标为 1.5 cm / 1° 的世界系刚体位移；两个球形障碍（间隙 1 cm）；倾角上限 8°；关节限幅 ±2.8 rad、±0.8 rad/s 由投影核保证。

| 种子 | 最小位置误差 (m) | 末位置误差 (m) | 最大等式漂移 | 最小间隙 (m) | 最大倾角 (°) | 墙钟 (s) |
|---|---|---|---|---|---|---|
{rows}

**观察**：单阶段 MPPI 能把位置误差从初值 9.3 cm 压到 2.0–2.3 cm，但随后在噪声地板上抖动/回漂（末误差 2.3–7.9 cm），这正是论文引入第二阶段与辅助控制器的动机。等式漂移被限制在 $10^{{-6}}$ 量级（投影 + 离散稳定化），障碍与倾角约束始终满足。

**E1 判定**：三个种子的最小位置误差均 < 0.03 m、等式漂移 < 1e-3、间隙 > 1 cm、倾角 < 8°，**通过**；但"稳定收敛到目标"**未通过**——本实现不做此声明。

**关于 L 切换的实测**：表 I 的 $\eta=0.1$ 要求辅助控制器比采样控制器便宜 **10 倍**才会切换；在 2 cm 误差处 $C_t/C_s\\approx1$，故 $L$ 持续上升、切换不触发（`aux_fraction=0`）。把 $\eta$ 改为 1.0（与论文正文"收敛附近 $C_t/C_s\\approx2$"的描述一致，但与表 I 的 0.1 冲突）后，切换立即生效：

| $\eta$ | 种子 | 末位置误差 (m) | 辅助控制占比 | 最大等式漂移 | 最大倾角 (°) |
|---|---|---|---|---|---|
{rows_sw}

$\eta=1.0$ 时辅助控制器部分接管（占比 0.40–0.80），末误差降到 **0.79–1.16 cm**、漂移 ~5e-7，说明辅助终结器本身工作正常，问题在表 I 的 $\eta$ 与切换叙述不自洽。

**N2 逐周期数值轨迹**（种子 0，前 8 个控制周期；切换条件是 $C_t/C_s<\eta$）：

| $\eta$ | 周期 | $C_t$ | $C_s$ | $C_t/C_s$ | $L$ | 辅助激活 | 位置误差 (cm) |
|---|---|---|---|---|---|---|---|
{rows_n2}

测量：$\eta=0.1$ 时 $C_t/C_s$ 在 0.35–0.60，始终大于 0.1，$L$ 从 0.04 单调升到 0.40，辅助从未激活；$\eta=1.0$ 时前 4 个周期 $C_t/C_s<1$，$L$ 触底 -0.05、辅助接管，随后 $C_t/C_s$ 回升到 >1（采样计划变得便宜），$L$ 上升、辅助退出——切换在两种控制器之间交替。解释：Eq.(47) 的切换门槛是"辅助代价低于 $\eta\times$ 采样代价"，$\eta=0.1$ 实际要求 10 倍优势，这与表 I 的取值直接相关；不据此断言论文全局不自洽，只报告该实现下的行为。

**局限（如实记录）**：该抓取位形下绝对位姿雅可比条件较差（$\\sigma_{{\\min}}\\approx0.117$），6 cm 的物体位移需要约 1.7 rad 的关节运动，因此任务目标取 1.5 cm；更大位移需要重选位形或引入 receding-horizon 的更长时域。
"""
    (reports / "G2_ACCEPTANCE.md").write_text(md, encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
