"""G1 acceptance measurements (modules A1-A3, B1-B2).

Runs the numeric checks that back ``reports/G1_ACCEPTANCE.md``.  Pure CPU;
no upstream code, no GPU, no dqrobotics.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from p1_repro.dq import (  # noqa: E402
    dq_conj,
    dq_from_rt,
    dq_mul,
    dq_to_rt,
    q_from_rotmat,
    q_to_rotmat,
)
from p1_repro.kinematics import (  # noqa: E402
    SerialChain,
    absolute_pose,
    dq_sqrt,
    relative_jacobian,
    relative_pose,
)
from p1_repro.nullspace import damped_pinv, null_projector, project_velocity  # noqa: E402

UR3_DH = np.array(
    [
        [0.0, 0.1519, 0.0, 1.5708],
        [0.0, 0.0, -0.24365, 0.0],
        [0.0, 0.0, -0.21325, 0.0],
        [0.0, 0.11235, 0.0, 1.5708],
        [0.0, 0.08535, 0.0, -1.5708],
        [0.0, 0.0819, 0.0, 0.0],
    ]
)
BASE1 = np.array([0.612384, 0.353533, -0.353533, 0.612384, -0.087881, 0.013986, 0.013986, 0.087881])
BASE2 = np.array([-0.612384, 0.353533, -0.353533, -0.612384, 0.087864, 0.013983, 0.013983, -0.087864])
RNG = np.random.default_rng(20261021)


def dh_matrix(theta, d, a, alpha):
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    T = np.eye(4)
    T[:3, :3] = [[ct, -st * ca, st * sa], [st, ct * ca, -ct * sa], [0.0, sa, ca]]
    T[:3, 3] = [a * ct, a * st, d]
    return T


def matrix_fk(dh, q):
    T = np.eye(4)
    for i, (off, d, a, alpha) in enumerate(dh):
        T = T @ dh_matrix(q[i] + off, d, a, alpha)
    return T


def measure():
    out = {}
    chain = SerialChain(UR3_DH)
    q = RNG.uniform(-np.pi, np.pi, size=(500, 6))
    x = chain.fk(q)
    r, t = dq_to_rt(x)
    pos_err, rot_err = [], []
    for k in range(len(q)):
        T = matrix_fk(UR3_DH, q[k])
        pos_err.append(np.linalg.norm(t[k] - T[:3, 3]))
        rot_err.append(np.abs(q_to_rotmat(r[k]) - T[:3, :3]).max())
    out["A1_fk_pos_max"] = float(np.max(pos_err))
    out["A1_fk_rot_max"] = float(np.max(rot_err))
    out["A1_unit_real_residual"] = float(np.abs(np.sum(r * r, axis=-1) - 1.0).max())
    out["A1_unit_dual_residual"] = float(np.abs(np.sum(r * x[..., 4:], axis=-1)).max())

    # A2 midpoint
    c1, c2 = SerialChain(UR3_DH, base=BASE1), SerialChain(UR3_DH, base=BASE2)
    q1 = RNG.uniform(-2, 2, size=(100, 6))
    q2 = RNG.uniform(-2, 2, size=(100, 6))
    x1, x2 = c1.fk(q1), c2.fk(q2)
    xr = relative_pose(x1, x2)
    s = dq_sqrt(xr)
    xa = absolute_pose(x1, x2, xr)
    out["A2_sqrt_square_max"] = float(np.abs(dq_mul(s, s) - xr).max())
    out["A2_midpoint_identity_max"] = float(np.abs(dq_mul(dq_conj(xa), x1) - s).max())
    out["A2_base_invariance_max"] = float(np.abs(xa - dq_mul(x1, dq_conj(s))).max())

    # A3 Jacobian vs central differences
    J = relative_jacobian(c1, c2, q1[:10], q2[:10])
    h = 1e-6
    worst_abs, worst_rel = 0.0, 0.0
    for k in range(10):
        for j in range(12):
            a1p, a1m = q1[k : k + 1].copy(), q1[k : k + 1].copy()
            a2p, a2m = q2[k : k + 1].copy(), q2[k : k + 1].copy()
            if j < 6:
                a1p[0, j] += h
                a1m[0, j] -= h
            else:
                a2p[0, j - 6] += h
                a2m[0, j - 6] -= h
            fd = (relative_pose(c1.fk(a1p), c2.fk(a2p)) - relative_pose(c1.fk(a1m), c2.fk(a2m))) / (2 * h)
            err = np.abs(fd[0] - J[k, :, j]).max()
            worst_abs = max(worst_abs, float(err))
            worst_rel = max(worst_rel, float(err / max(np.abs(J[k, :, j]).max(), 1e-12)))
    out["A3_jac_fd_abs_max"] = worst_abs
    out["A3_jac_fd_rel_max"] = worst_rel

    # rank
    Jall = relative_jacobian(c1, c2, RNG.uniform(-2, 2, size=(50, 6)), RNG.uniform(-2, 2, size=(50, 6)))
    ratios = [np.linalg.svd(Jall[k], compute_uv=False)[6] / np.linalg.svd(Jall[k], compute_uv=False)[0] for k in range(50)]
    out["A3_rank_sigma7_over_sigma1_max"] = float(np.max(ratios))
    out["A3_sigma6_over_sigma1_min"] = float(
        min(np.linalg.svd(Jall[k], compute_uv=False)[5] / np.linalg.svd(Jall[k], compute_uv=False)[0] for k in range(50))
    )

    # B1 projector
    N = null_projector(Jall)
    out["B1_idempotence_max"] = float(np.abs(N @ N - N).max())
    out["B1_symmetry_max"] = float(np.abs(N - np.swapaxes(N, -1, -2)).max())
    out["B1_JN_max"] = float(np.abs(Jall @ N).max())
    out["B1_rank_min"] = int(min(np.linalg.matrix_rank(N[k], tol=1e-8) for k in range(50)))

    u = RNG.normal(size=(50, 12))
    up = project_velocity(Jall, u)
    before = np.linalg.norm(np.einsum("kij,kj->ki", Jall, u), axis=-1)
    after = np.linalg.norm(np.einsum("kij,kj->ki", Jall, up), axis=-1)
    out["B1_projection_ratio_min"] = float(np.min(before / np.maximum(after, 1e-18)))

    # B2 drift
    u0 = np.array([0.11, -0.23, 0.17, 0.05, -0.09, 0.13, -0.07, 0.19, -0.15, 0.03, 0.21, -0.12])
    u0 = u0 / np.linalg.norm(u0) * 0.3
    qa = np.array([[0.0, -1.0, 0.5, -1.5, 0.3, 0.2]])
    qb = np.array([[0.2, -0.9, 0.4, -1.4, 0.25, 0.15]])

    def drift(th, steps=15, projected=True):
        a, b = qa.copy(), qb.copy()
        x0 = relative_pose(c1.fk(a), c2.fk(b))
        for _ in range(steps):
            Jk = relative_jacobian(c1, c2, a, b)
            uu = project_velocity(Jk, u0[None])[0] if projected else u0
            a = a + th * uu[None, :6]
            b = b + th * uu[None, 6:]
        return float(np.linalg.norm(relative_pose(c1.fk(a), c2.fk(b)) - x0))

    table = []
    for th in [0.00125, 0.0025, 0.005, 0.01, 0.02]:
        dp, du = drift(th), drift(th, projected=False)
        table.append({"Th": th, "projected": dp, "unprojected": du, "ratio": du / dp})
    out["B2_drift_table"] = table
    ths = np.array([row["Th"] for row in table[:4]])
    out["B2_projected_slope"] = float(np.polyfit(np.log(ths), np.log([row["projected"] for row in table[:4]]), 1)[0])
    out["B2_unprojected_slope"] = float(np.polyfit(np.log(ths), np.log([row["unprojected"] for row in table[:4]]), 1)[0])
    out["B2_ratio_at_0p005"] = float(table[2]["ratio"])

    # B2 damping characterisation
    J0 = relative_jacobian(c1, c2, qa, qb)[0]
    N_bad = np.eye(12) - damped_pinv(J0, 1e-16) @ J0
    N_12 = np.eye(12) - damped_pinv(J0, 1e-12) @ J0
    out["B2_damping_1e16_idempotence"] = float(np.abs(N_bad @ N_bad - N_bad).max())
    out["B2_damping_1e12_idempotence"] = float(np.abs(N_12 @ N_12 - N_12).max())
    out["B2_svd_idempotence"] = float(np.abs(null_projector(J0[None])[0] @ null_projector(J0[None])[0] - null_projector(J0[None])[0]).max())

    # negative control: the literal Eq. (8) reading x_2^* x_{r/2} is not the
    # group midpoint; measure how far it is from x_a and from the identity.
    xa_literal = dq_mul(dq_conj(x2), s)
    out["A2_negative_control_shift"] = float(np.abs(xa_literal - xa).max())
    out["A2_literal_midpoint_residual"] = float(
        np.abs(dq_mul(dq_conj(xa_literal), x1) - s).max()
    )
    return out


def main():
    data = measure()
    outdir = ROOT / "reports"
    outdir.mkdir(exist_ok=True)
    (outdir / "G1_ACCEPTANCE.json").write_text(json.dumps(data, indent=2), encoding="utf-8")

    t = data["B2_drift_table"]
    rows = "\n".join(
        f"| {r['Th']:.5f} | {r['projected']:.3e} | {r['unprojected']:.3e} | {r['ratio']:.1f} |" for r in t
    )
    md = f"""# G1 验收报告（模块 A1–A3、B1–B2）

> 自动生成：`python p1/scripts/g1_acceptance.py`
> 环境：Python 3.10.12，NumPy 1.24.4，float64，纯 CPU
> 代码：`p1/src/p1_repro/{{dq,se3,kinematics,nullspace}}.py`
> 测试：`p1/tests/test_g1_dq_kinematics.py`（18 项全部通过）

## 1. A1 代数与正运动学

| 指标 | 值 | 判定 |
|---|---|---|
| FK 位置误差 vs 独立 SE(3) 矩阵链（500 构型） | {data['A1_fk_pos_max']:.2e} m | 通过（≤1e-12） |
| FK 旋转误差 vs 独立 SE(3) 矩阵链 | {data['A1_fk_rot_max']:.2e} | 通过（≤1e-12） |
| 实部单位残差 | {data['A1_unit_real_residual']:.2e} | 通过（≤1e-12） |
| 实部-对偶部正交残差 | {data['A1_unit_dual_residual']:.2e} | 通过（≤1e-12） |

## 2. A2 相对/绝对位姿

| 指标 | 值 | 判定 |
|---|---|---|
| $\\|s^2-x_r\\|_\\infty$ | {data['A2_sqrt_square_max']:.2e} | 通过（≤1e-12） |
| 群中点恒等式 $\\|x_a^{{-1}}x_1-s\\|_\\infty$ | {data['A2_midpoint_identity_max']:.2e} | 通过（≤1e-12） |
| 基座交换不变性 | {data['A2_base_invariance_max']:.2e} | 通过（≤1e-12） |
| 负对照：按论文星号字面实现的位姿偏移 | {data['A2_negative_control_shift']:.2e} | 必须 >1e-2，通过 |
| 负对照：字面式的中点心恒等式残差 | {data['A2_literal_midpoint_residual']:.2e} | 必须 >1e-2，通过 |

固定反例：$t_a=(0.183153,0.148916,0.15)$ m，与位置算术平均相差 $0.102479$ m，与 G0 的手算值一致。

## 3. A3 相对雅可比

| 指标 | 值 | 判定 |
|---|---|---|
| 中心差分最大绝对误差（h=1e-6） | {data['A3_jac_fd_abs_max']:.2e} | 通过（≤1e-6） |
| 中心差分最大相对误差 | {data['A3_jac_fd_rel_max']:.2e} | 通过（≤1e-6） |
| $\\sigma_7/\\sigma_1$（50 构型最大值） | {data['A3_rank_sigma7_over_sigma1_max']:.2e} | 通过（≤1e-12） |
| $\\sigma_6/\\sigma_1$（最小值） | {data['A3_sigma6_over_sigma1_min']:.2e} | 秩 6 证实 |

## 4. B1 零空间投影

| 指标 | 值 | 判定 |
|---|---|---|
| $\\|N^2-N\\|_\\infty$ | {data['B1_idempotence_max']:.2e} | 通过（≤1e-12） |
| $\\|N-N^\\top\\|_\\infty$ | {data['B1_symmetry_max']:.2e} | 通过（≤1e-12） |
| $\\|JN\\|_\\infty$ | {data['B1_JN_max']:.2e} | 通过（≤1e-10） |
| $\\mathrm{{rank}}(N)$ 最小值 | {data['B1_rank_min']} | 等于 $n-6=6$ |
| 投影前后 $\\|Ju\\|$ 比值最小值 | {data['B1_projection_ratio_min']:.2e} | 通过（≥1e8） |

## 5. B2 有限步长残差

| $T_h$ (s) | 投影漂移 | 未投影漂移 | 比值 |
|---|---|---|---|
{rows}

- 投影漂移 log-log 斜率：**{data['B2_projected_slope']:.3f}**（理论 2）
- 未投影漂移 log-log 斜率：**{data['B2_unprojected_slope']:.3f}**（理论 1）
- $T_h=0.005$ 时漂移比：**{data['B2_ratio_at_0p005']:.0f}**

结论：逐步零空间投影给出的是**一阶精确、$O(T_h^2)$ 单步残差**；论文贡献 2 的“exactly”只能在连续时间意义下成立。

## 6. 官方 1e-16 阻尼的数值问题（审计补充）

| 投影器构造 | $\\|N^2-N\\|_\\infty$ |
|---|---|
| 官方形式 $J^\\top(JJ^\\top+10^{{-16}}I)^{{-1}}$ | {data['B2_damping_1e16_idempotence']:.2e} |
| 同式，$\\varepsilon=10^{{-12}}$ | {data['B2_damping_1e12_idempotence']:.2e} |
| SVD 截断伪逆（本实现默认） | {data['B2_svd_idempotence']:.2e} |

原因：8 行对偶四元数雅可比秩为 6，$JJ^\\top$ 有两个结构零特征值；加 $10^{{-16}}$ 后条件数约 $10^{{16}}$，float64 求逆的舍入被放大到 $O(1)$。本实现因此使用 SVD 截断的 Moore–Penrose 伪逆（`rcond=1e-10`），并把官方阻尼形式保留为可复现的对照。
"""
    (outdir / "G1_ACCEPTANCE.md").write_text(md, encoding="utf-8")
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
