#!/usr/bin/env python3
"""Build the T02 Chinese Markdown report from the audit JSON.

P2-native path: no P4 imports, no python-docx, Markdown + PNG only.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "p2" / "tools"))

from p2_md_report import bar_chart, render                       # noqa: E402

REVIEWS = ROOT / "p2" / "reviews"
FIGS = REVIEWS / "figures"


def short(s, n=12):
    return s[:n]


# The audit JSON keeps the labels produced by the reviewed run. Two Eq.(15)
# checks used "1/s" where the free coordinate is a translation; the correction
# is documented in reviews/T02_UNIT_ERRATA.json and applied only to display.
UNIT_OVERRIDE = {
    "eq15_adapted_free_log_invariant": "m/s or rad/s (mixed)",
    "eq15_printed_vs_adapted_counterexample": "m/s",
}


def main() -> int:
    audit = json.loads((REVIEWS / "T02_MATH_AUDIT.json").read_text())
    base = json.loads((REVIEWS / "T02_MATH_BASELINE.json").read_text())
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()

    status_counts = {}
    for c in audit["checks"]:
        status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1

    by_id = {c["id"]: c for c in audit["checks"]}
    eq15 = by_id["eq15_printed_vs_adapted_counterexample"]["detail"]
    rbar = by_id["damping_Rbar_lever_arm"]["detail"]
    rank = by_id["grasp_rank_by_mode"]["detail"]

    colors = ["#c44e52" if c["status"].startswith("DEVIATION") else "#55a868"
              for c in audit["checks"]]
    fig1 = bar_chart(
        [c["id"] for c in audit["checks"]],
        [max(c["max_abs_error"], 1e-18) for c in audit["checks"]],
        FIGS / "t02_max_absolute_error.png",
        "T02 max absolute error per check (units differ; green=PASS, red=recorded deviation)",
        "max abs error (log)", log=True, colors=colors)

    rows = []
    for c in audit["checks"]:
        rows.append([c["id"], c["status"], f"{c['max_abs_error']:.2e}",
                     f"{c['max_rel_error']:.2e}",
                     f"{c['tolerance']:.0e}" if c["tolerance"] else "-",
                     UNIT_OVERRIDE.get(c["id"], c["unit"])])

    spec = {
        "title": "P2-T02 数学复核报告（原版回归基线）",
        "filename": "T02_REPORT.md",
        "meta": {
            "日期": "2026-10-19",
            "分支": "reproduce-p2-numerical-simulation-20261018",
            "提交": commit,
            "命令": "`/usr/bin/python3.10 p2/tools/t02_math_audit.py`",
            "随机种子": audit["seed"],
            "总墙钟": f"{audit['wall_s']:.2f} s",
            "性质": "只读数学复核；无积分、无控制、无闭环",
        },
        "summary": (
            "共 23 项检查："
            + "、".join(f"{k} {v}" for k, v in sorted(status_counts.items()))
            + "。全部代数恒等式在 1e-12 量级内成立；两项为**已记录的偏离**（论文自身的近似或已批准替代），"
              "不是代码缺陷。**本报告只证明数学实现与论文公式一致，不证明任何控制实验。**"
        ),
        "sections": [
            {
                "heading": "1. 结论",
                "paragraphs": [
                    "SE(3) Exp/Log 往返、Adjoint 同态与逆、`Ad(Exp(τ)) = expm(ad(τ))`、wrench 功率不变性"
                    "均在 1e-12 内通过；接触本构（式 9/10/11）、W 结构（式 12）、虚功一致、"
                    "内部 wrench 投影（式 20）均通过。",
                    "现有右 Euler 预测的 `F` 与真实一步 map 的右误差有限差分一致（相对误差 2.6e-11），"
                    "6 类观测的解析 Jacobian 与其独立差分一致（5.9e-11）。因此 3.948 s 的失败"
                    "**不是 Jacobian 实现错误**，而是离散化稳定性问题（见 T01 裁决）。",
                    "两项偏离：式 (10) 用 `R̄` 替代 `Ad(D)`，丢掉杠杆臂块；式 (15) 印刷式在反例中"
                    "把自由方向形变速率翻倍。",
                ],
            },
            {
                "heading": "2. 逐项结果",
                "paragraphs": [
                    "单位说明：式(15) 反例的自由 Lie 坐标是沿 x 的平移，速率单位为 **m/s**；"
                    "`0.02 m/s × 4 ms = 80 µm`。审计 JSON 中该检查的 `unit` 仍保留原始标注 `1/s`，"
                    "更正见 `T02_UNIT_ERRATA.json`，数值未改动。",
                ],
                "table": {
                    "columns": ["检查", "状态", "最大绝对误差", "最大相对误差", "容差", "单位"],
                    "rows": rows,
                },
                "figure": {"path": "figures/t02_max_absolute_error.png",
                           "caption": "图 1：各检查的最大绝对误差（对数轴，单位随检查不同）。绿色为通过，红色为已确认偏离。"},
            },
            {
                "heading": "3. 两处已确认的偏离",
                "paragraphs": [
                    f"**式 (15) 印刷式 vs 已批准几何**：在同一反例（D=I，sliding，物体沿 x 以 0.01 m/s 运动，EE 静止）下，"
                    f"已批准几何的自由方向形变速率为 {eq15['adapted_free_component_1_s']:.1e} 1/s，"
                    f"印刷式为 {eq15['printed_free_component_1_s']:.2f} 1/s；4 ms 对应形变 "
                    f"{eq15['printed_deformation_over_4ms_m']*1e6:.0f} µm（应为 0）。"
                    f"印刷式恰好等于 2 倍自由速率（`printed_equals_two_times_a=True`），"
                    "与旧审计的 80 µm 结论独立一致。",
                    f"**式 (10) 的 `R̄` 近似**：`R̄ = diag(R,R)` 丢掉了 `Ad(D)` 的 `[p]×R` 块（杠杆臂耦合）。"
                    f"在随机小扰动状态上，相对 twist 最大相对差 {rbar['relative_twist_difference_max']:.2e}。"
                    "这是论文自己的线性化近似，不是实现错误；T04 需在运动状态下评估其影响。",
                    f"**秩的夹具依赖性**：`rank(W)` 在标称夹具为 tight 6 / pivot 6 / sliding 4；"
                    f"在一般扰动状态 sliding 变为 {rank['perturbed_generic']['sliding']['rank']}，"
                    "因为两条滑移轴的共同自由方向退化为一个叉积方向。后续秩门必须绑定具体夹具。",
                ],
            },
            {
                "heading": "4. 未优化回归基线（供 T01-E 使用）",
                "paragraphs": [
                    "`p2/reviews/T02_MATH_BASELINE.json` 记录了 4 个源文件的 SHA256 与一组黄金数值："
                    "标称状态的 D/τ/hK/hB/h/W/奇异值/内部 wrench、两臂 grasp rate、6 类观测 Jacobian 的范数与校验和、"
                    "一次 4 ms 预测的 F 范数与校验和、一次 3 观测更新的后验 V 与 P 对角。",
                    "T01-E 的等价性判据：同一输入下逐项相对误差 ≤1e-12（或位相同），"
                    "并附绝对/相对误差与最大差异；**“运行不报错”不算等价**。",
                ],
                "table": {
                    "columns": ["源文件", "SHA256（前 12 位）"],
                    "rows": [[k, short(v)] for k, v in base["source_sha256"].items()],
                },
            },
            {
                "heading": "5. 局限",
                "paragraphs": [
                    "本报告只覆盖**单点/小扰动**的数学性质，不覆盖长时积分、模式切换瞬态、"
                    "非正规矩阵谱、闭环统计；这些属于 T03/T04。",
                    "观测 Jacobian 的对照在零残差处进行；非零残差时的左 Jacobian 约定"
                    "（`H = J_l^{-1}(r) ∂h/∂δ`）与 IEKF 更新式一致，但需在 T04 的闭环中复核。",
                    "不得据此报告声称论文控制实验成功或部分成功。",
                ],
            },
        ],
    }
    path = render(spec, REVIEWS)
    print("wrote", path, "and", fig1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
