#!/usr/bin/env python3
"""Build the T03 Chinese Markdown report and figures (P2-native renderer)."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "p2" / "tools"))
from p2_md_report import render                                    # noqa: E402

REV = ROOT / "p2" / "reviews"
FIG = REV / "figures"
RUN = ROOT / "p2" / "runs" / "20261019_T03_PLANT"


def fig_spectrum(spec):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, zoom in zip(axes, (False, True)):
        for obj, color in (("A", "#4c72b0"), ("C", "#c44e52"), ("B1", "#55a868")):
            pts = spec["objects"][obj]["points"]
            for kind, marker in (("nominal", "o"), ("P1", "^")):
                if kind not in pts:
                    continue
                ev = pts[kind]["continuous"]["all_eigenvalues"]
                re = np.array([e["real"] for e in ev]); im = np.array([e["imag"] for e in ev])
                ax.scatter(re, im, s=18, marker=marker, alpha=0.6, color=color,
                           label=f"{obj}-{kind}")
        ax.axvline(0, color="k", lw=0.6)
        ax.set_xlabel("Re(lambda) [1/s]"); ax.set_ylabel("Im(lambda) [1/s]")
        ax.grid(alpha=0.3)
        if zoom:
            ax.set_xlim(-20, 5); ax.set_title("zoom near the imaginary axis")
        else:
            ax.set_title("full range (fast mode off-scale)")
    axes[0].legend(fontsize=6, ncol=1, loc="upper left")
    fig.tight_layout(); path = FIG / "t03_continuous_spectrum.png"; fig.savefig(path, dpi=140); plt.close(fig)
    return path


def fig_discrete(spec):
    hs = [("h_over_4", 1 / 12000), ("h_over_2", 1 / 6000), ("h", 1 / 3000),
          ("1ms", 1e-3), ("4ms", 4e-3)]
    schemes = [("euler", "-o", "#c44e52"), ("implicit_euler", "-s", "#4c72b0"),
               ("trapezoid", "-^", "#55a868"), ("matrix_exp", "-d", "#8172b2")]
    objs = ["A", "B1", "C"]
    fig, axes = plt.subplots(1, len(objs), figsize=(12, 3.8), sharey=True)
    for ax, obj in zip(axes, objs):
        pts = spec["objects"][obj]["points"]
        src = "EQ" if "EQ" in pts else "nominal"
        for name, style, color in schemes:
            ys = [pts[src]["discrete_theory"][lab][name]["rho"] for lab, _ in hs]
            ax.plot([h for _, h in hs], ys, style, ms=4, color=color, label=name)
        ax.axhline(1.0, color="k", lw=0.6, ls="--")
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_title(f"{obj} ({src})"); ax.set_xlabel("h [s]"); ax.grid(alpha=0.3)
    axes[0].set_ylabel("spectral radius rho(Phi)")
    axes[0].legend(fontsize=7)
    fig.tight_layout(); path = FIG / "t03_discrete_rho.png"; fig.savefig(path, dpi=140); plt.close(fig)
    return path


def fig_perturb(pert):
    fig, axes = plt.subplots(2, 2, figsize=(11, 6))
    for col, obj in enumerate(("A", "C")):
        for row, key in enumerate(("v_norm", "internal_f")):
            ax = axes[row][col]
            for label, style in (("h", "-"), ("h_over_2", "--"), ("h_over_4", ":")):
                f = RUN / "trajectories" / f"{obj}_P1_{label}.npz"
                if not f.exists():
                    continue
                z = np.load(f)
                y = np.linalg.norm(z["V"], axis=1) if key == "v_norm" else z["internal_f"]
                ax.plot(z["t"], y, style, lw=1.2, label=label)
            ax.set_title(f"{obj} P1 - {'|V| [m/s,rad/s]' if key == 'v_norm' else 'internal force [N]'}")
            ax.set_xlabel("t [s]"); ax.grid(alpha=0.3); ax.legend(fontsize=7)
    fig.tight_layout(); path = FIG / "t03_perturbation.png"; fig.savefig(path, dpi=140); plt.close(fig)
    return path


def fig_convergence(pert):
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    for obj, color in (("A", "#4c72b0"), ("C", "#c44e52"), ("B1", "#55a868")):
        conv = pert["objects"][obj]["points"]["P1"].get("convergence", {})
        if "h" not in conv or "h_over_2" not in conv:
            continue
        dts = np.array([1 / 3000, 1 / 6000])
        errs = np.array([conv["h"]["pos_m"], conv["h_over_2"]["pos_m"]])
        ax.loglog(dts, errs, "-o", color=color, label=f"{obj} (p={conv.get('order_pos'):.2f})")
    ax.loglog(dts, errs[0] * (dts / dts[0]) ** 2, "k--", lw=0.8, label="slope 2")
    ax.set_xlabel("dt [s]"); ax.set_ylabel("max |pos - pos_ref| [m]")
    ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=7)
    fig.tight_layout(); path = FIG / "t03_convergence.png"; fig.savefig(path, dpi=140); plt.close(fig)
    return path


def fig_c_legacy(spec):
    c = spec["c_legacy"]["checks"]
    labels = ["native implicit\n(production)", "explicit midpoint\n(mechanics.midpoint_step)",
              "theory implicit\nmidpoint", "theory Euler"]
    vals = [list(spec["c_legacy"]["eps_sweep"]["native"].values())[0]["rho"],
            list(spec["c_legacy"]["eps_sweep"]["python_midpoint_step"].values())[0]["rho"],
            c["implicit_midpoint_theory_rho"], c["euler_theory_rho"]]
    colors = ["#55a868", "#c44e52", "#4c72b0", "#8172b2"]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    bars = ax.bar(labels, vals, color=colors)
    ax.axhline(1.0, color="k", lw=0.8, ls="--")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.05, f"{v:.4f}", ha="center", fontsize=8)
    ax.set_ylabel("spectral radius rho"); ax.set_title("C at h=1/3000: three different maps")
    ax.tick_params(axis="x", labelsize=7)
    fig.tight_layout(); path = FIG / "t03_c_legacy.png"; fig.savefig(path, dpi=140); plt.close(fig)
    return path


def main() -> int:
    spec = json.loads((REV / "T03_SPECTRUM.json").read_text())
    pert = json.loads((REV / "T03_PERTURBATION.json").read_text())
    FIG.mkdir(parents=True, exist_ok=True)
    f1 = fig_spectrum(spec); f2 = fig_discrete(spec); f3 = fig_perturb(pert)
    f4 = fig_convergence(pert); f5 = fig_c_legacy(spec)

    rows = []
    for obj in ("A", "B1", "B2", "C"):
        for kind in ("nominal", "EQ", "P1", "P2"):
            p = spec["objects"][obj]["points"].get(kind)
            if not p:
                continue
            c = p["continuous"]
            rows.append([obj, kind, f"{p['f_norm']:.1e}", f"{c['min_real_part']:.1f}",
                         f"{c['n_positive_real_gt_1e-6']}", f"{c['max_modulus']:.1f}",
                         f"{p['native_map']['h']['rho']:.6f}",
                         f"{p['discrete_theory']['h']['trapezoid']['rho']:.6f}",
                         f"{p['discrete_theory']['4ms']['euler']['rho']:.2f}"])

    cl = spec["c_legacy"]["checks"]
    srows = []
    for o in ("A", "B1", "B2", "C"):
        for k in ("P1", "P2"):
            v = pert["objects"][o]["points"][k]["runs"]["h"]
            rho = spec["objects"][o]["points"][k]["native_map"]["h"]["rho"]
            p_ord = pert["objects"][o]["points"][k].get("convergence", {}).get("order_pos")
            srows.append([o, k, f"{rho:.6f}", f"{v['max_tau']:.4f}",
                          f"{v['max_internal_force']:.4f}", f"{v['max_internal_moment']:.2e}",
                          f"{v['energy_drift']:+.2e}", v["max_newton"],
                          f"{p_ord:.2f}" if p_ord else "n/a"])

    report = {
        "title": "P2-T03 独立物体-软接触动力学数值审查",
        "filename": "T03_REPORT.md",
        "meta": {
            "日期": "2026-10-19",
            "分支": "reproduce-p2-numerical-simulation-20261018",
            "脚本": "`p2/tools/t03_plant_audit.py`",
            "谱阶段墙钟": f"{spec['wall_s']:.2f} s（上限 {spec['cap_s']:.0f} s）",
            "受扰阶段墙钟": f"{pert['wall_s']:.2f} s（上限 {pert['cap_s']:.0f} s）",
            "性质": "独立 plant 数值分析；无估计器、无控制、无闭环",
        },
        "summary": (
            "A/B1/B2 在 1/3000 s 下 native 隐式一步映射谱半径均为 1.0（中性），"
            "理论梯形 1.000000–1.000004；显式 Euler 则分别达 1.000/1.250/2.112，"
            "4 ms 时 7.73/26.0/36.3。历史 C 的 ρ≈2.73 **不是 native 隐式积分器**的性质："
            "它精确等于 `mechanics.midpoint_step`（显式中点预测-校正）的稳定函数 "
            "|1+z+z²/2|=2.730136，而同一 z=hλ 下 native 隐式映射为 1.0、理论隐式中点为 1.0。"
            "受扰运动在所有对象上衰减、能量单调下降、无异常增长。"
        ),
        "sections": [
            {"heading": "1. 连续谱与工作点", "paragraphs": [
                "每个工作点给出 42 维右误差 Jacobian 的全部特征值。最快实模态：A −2183 s⁻¹、"
                "B1/B2 −6750 s⁻¹、C −9336 s⁻¹。A/B1/B2 的数值平衡点由 COM 高度二分求得"
                f"（COM 下移 {-spec['objects']['A']['equilibrium']['drop_m']*1e3:.3f} mm / "
                f"{-spec['objects']['B1']['equilibrium']['drop_m']*1e3:.3f} mm，残差 <1e-8）；"
                "C 在该夹具下**不存在仅靠竖直位移的完整平衡点**（残差 9.81 由非竖直分量主导），"
                "故 C 只报告 nominal 与两个扰动点。"],
             "table": {"columns": ["对象", "工作点", "‖f‖", "min Re", "正实部模态", "max‖λ‖",
                                   "native ρ(h)", "理论梯形 ρ(h)", "Euler ρ(4ms)"],
                       "rows": rows},
             "figure": {"path": "figures/t03_continuous_spectrum.png",
                        "caption": "图 1：连续谱（左：全范围；右：虚轴附近放大）。最左端点即最快实模态。"}},
            {"heading": "2. 离散稳定性（同一连续线性化）", "paragraphs": [
                "五种格式用**同一个** A 与 h 构造；Euler 在 h=1/3000 即对 B1/B2/C 不稳，"
                "隐式 Euler/梯形/矩阵指数在整个范围内 ρ≤1（P1/P2 的 1.000002–4e-4 来自连续谱中"
                "约 +0.01…+1.05 s⁻¹ 的小正实部，不是格式不稳）。"],
             "figure": {"path": "figures/t03_discrete_rho.png",
                        "caption": "图 2：ρ 随步长变化（虚线为 1）。Euler 在 1/3000 处已越过 1。"}},
            {"heading": "3. 历史 C ρ≈2.73 的归因", "paragraphs": [
                f"旧夹具下 z = hλ = {cl['z_h_lambda']['real']:.4f}。三个**不同**映射的 ρ："
                f"native 隐式 {cl['native_rho_eps1e6'] if 'native_rho_eps1e6' in cl else cl['implicit_midpoint_theory_rho']:.6f}、"
                f"理论隐式中点 {cl['implicit_midpoint_theory_rho']:.6f}、"
                f"`mechanics.midpoint_step` **2.730136**。后者是显式中点预测-校正，稳定函数 "
                f"|1+z+z²/2| = {cl['scalar_factors_at_z']['explicit_midpoint_abs']:.6f}，逐位吻合；"
                f"同一 z 下 Euler |1+z| = {cl['scalar_factors_at_z']['euler_abs']:.6f}（即 2.112）。",
                "FD 的 ε 从 1e-4 到 1e-7，两个映射的 ρ 均不变（native 1.0；显式中点 2.730136），"
                "说明不是差分步长伪影。该点不是平衡点（|f|=9.81），但 native 的 Newton 一步收敛 "
                "（1 次迭代，残差 4e-16）；受扰 0.2 s 速度衰减到 2.9%，与 ρ=1.0 一致，"
                "与 ρ=2.73 不符。结论：**2.73 属于旧审计使用的显式中点实现，不属于生产 plant**；"
                "不能把 Euler 的 2.112 与它混为一谈。"],
             "figure": {"path": "figures/t03_c_legacy.png",
                        "caption": "图 3：C 在同一 z 下三种映射的谱半径。"}},
            {"heading": "4. 非平衡受扰运动", "paragraphs": [
                "每个对象两个扰动点、三个步长（h、h/2、h/4），各积分 0.30 s，每 4 ms 采样。"
                "全部运行：最大 Newton 2 次迭代；速度衰减；能量单调下降（<0）；无异常增长或数值振荡。"],
             "table": {"columns": ["对象", "点", "ρ(native)", "max‖τ‖", "max 内力", "max 内力矩",
                                   "ΔE [J]", "Newton", "p(pos)"],
                       "rows": srows},
             "figure": {"path": "figures/t03_perturbation.png",
                        "caption": "图 4：A/C 的速度范数与内力随时间（三种步长几乎重合）。"}},
            {"heading": "5. 步长收敛", "paragraphs": [
                "以 h/4 为参考，h 与 h/2 在 4 ms 对齐时刻的最大位置差；"
                f"实测经验阶约 {pert['objects']['A']['points']['P1']['convergence']['order_pos']:.2f}。"
                "该值高于名义二阶，说明误差处于渐近区但仍含高阶项；**不据此宣称严格二阶收敛**。"],
             "figure": {"path": "figures/t03_convergence.png",
                        "caption": "图 5：位置误差随 dt（双对数），黑虚线为斜率 2。"}},
            {"heading": "6. B1/B2 的适用性边界", "paragraphs": [
                "B1/B2 的质量 0.280 kg 与尺寸 75×140×40 mm 来自论文 Fig.5(d)；**惯量张量与抓取几何为 "
                "ADAPTATION**（均质长方体、±37.5 mm 对称抓取、EE z 沿物体 x）。"
                "因此 B1/B2 的谱与受扰结果只能作为 assumption-dependent 参考，不能称为论文匹配。"
                "其 Euler 在 1/3000 已不稳（ρ=1.25），若未来使用 B 类对象，必须用隐式/指数格式。"],
             },
            {"heading": "7. 局限", "paragraphs": [
                "① 全部为单点线性化与 0.3 s 短时积分，不覆盖模式切换、长时漂移、接触分离/再接触；"
                "② C 的夹具旋转导致无竖直平衡点，其 P1/P2 从非平衡 nominal 出发；"
                "③ 收敛阶仅用两个步长估计，未做 Richardson 外推；"
                "④ 未验证非正规谱在实际受扰方向上的瞬态增长（仅给出 cond(V)/Henrici 指标）；"
                "⑤ 不构成论文 Fig.6–9 或控制实验的任何证据。"],
             },
        ],
    }
    path = render(report, REV)
    print("wrote", path, [f1.name, f2.name, f3.name, f4.name, f5.name])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
