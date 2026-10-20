#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P5 study-phase schematic figures.

Purpose
-------
Redraw, with Chinese labels, the explanatory figures needed by
``p5/P5_PAPER_STUDY.md``.  These are *schematic* redrawings of concepts taken
from the paper text; they are NOT reproductions of the paper's own figures and
they contain no numerical output of any algorithm.

Hard rules encoded here
-----------------------
* No paper artifact (PDF page image, learned model, dataset) is read.
* No algorithm is executed.  Every plotted curve is an analytic toy function
  chosen only to visualise a definition (e.g. ``Gamma > 1`` means free space).
* Every figure carries a "redrawn schematic" watermark.

Run
---
    /usr/bin/python3.10 p5/tools/p5_figures.py
"""

import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "evidence", "figures"))

CJK_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
]


def _setup_font():
    for path in CJK_CANDIDATES:
        if os.path.exists(path):
            font_manager.fontManager.addfont(path)
            name = font_manager.FontProperties(fname=path).get_name()
            plt.rcParams["font.family"] = [name]
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 110
    plt.rcParams["savefig.dpi"] = 200


def _watermark(fig, text="示意图（本仓库重绘，非论文原始图）"):
    fig.text(
        0.5,
        0.012,
        text,
        ha="center",
        va="bottom",
        fontsize=8,
        color="#8a8f98",
    )


def _box(ax, xy, w, h, label, fc="#eef2f7", ec="#5b6b7c", fs=9, lw=1.0):
    ax.add_patch(
        FancyBboxPatch(
            xy,
            w,
            h,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            linewidth=lw,
            facecolor=fc,
            edgecolor=ec,
        )
    )
    ax.text(xy[0] + w / 2, xy[1] + h / 2, label, ha="center", va="center", fontsize=fs)


def _arrow(ax, p, q, style="-|>", color="#33414f", lw=1.1, ls="-"):
    ax.add_patch(
        FancyArrowPatch(
            p, q, arrowstyle=style, mutation_scale=12, color=color, linewidth=lw, linestyle=ls
        )
    )


def fig_framework():
    fig, ax = plt.subplots(figsize=(9.8, 4.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    yA, hA = 0.66, 0.19
    _box(ax, (0.015, yA), 0.17, hA, "真实物体运动\n$\\xi^O,\\dot{\\xi}^O$\n(视觉/动捕)", fc="#fdf1e3")
    _box(ax, (0.225, yA), 0.21, hA, "轨迹预测 + 可达性判别\n式(1) GMM 似然\n$\\to$ 拦截点 $T^*,\\xi^O(T^*)$")
    _box(ax, (0.475, yA), 0.21, hA, "多臂 LPV 动力学系统\n式(2)(8)(9)(11)\n$\\tau_{c_i}$ 同步分配, $\\gamma$ 协调")
    _box(ax, (0.725, yA), 0.255, hA, "集中式 QP 逆运动学\n式(17)(18)(19)-(23)\n约束: 任务/限位/SCA")

    yB, hB = 0.38, 0.17
    _box(ax, (0.475, yB), 0.21, hB, "SCA 边界 $\\Gamma(f(q))$, $\\nabla\\Gamma$\n式(24)-(28)\n离线学习 / 在线评估", fc="#f2eef8")
    _box(ax, (0.725, yB), 0.255, 0.13, "关节速度指令 $\\dot{q}\\in\\mathbb{R}^{d_Q}$", fc="#e9f4ea")

    yC = 0.09
    _box(ax, (0.475, yC), 0.21, 0.14, "机器人本体（关节空间）", fc="#e9f4ea")
    _box(ax, (0.725, yC), 0.255, 0.14, "低层跟踪控制器\n(论文假设: 完美跟踪)", fc="#f3f3f3")

    _arrow(ax, (0.185, yA + hA / 2), (0.225, yA + hA / 2))
    _arrow(ax, (0.435, yA + hA / 2), (0.475, yA + hA / 2))
    _arrow(ax, (0.685, yA + hA / 2), (0.725, yA + hA / 2))

    _arrow(ax, (0.8525, yA), (0.8525, yB + 0.13))
    _arrow(ax, (0.640, yB + hB), (0.760, yA), color="#7a8794", ls="--")
    ax.text(0.665, 0.585, "$\\Gamma,\\nabla\\Gamma\\to(17d)$", fontsize=7.4, color="#7a8794", ha="center")

    _arrow(ax, (0.8525, yB), (0.8525, yC + 0.14))
    _arrow(ax, (0.725, yC + 0.07), (0.685, yC + 0.07))

    # feedback from robot back to object state (conceptual)
    ax.plot([0.475, 0.10, 0.10], [yC + 0.07, yC + 0.07, yA], color="#7a8794",
            lw=1.0, ls="--")
    _arrow(ax, (0.10, yC + 0.07), (0.10, yA), color="#7a8794", ls="--")
    ax.text(0.52, 0.045, "闭环：机器人状态 / 物体观测反馈", fontsize=7.4, color="#7a8794", ha="center")

    ax.text(0.5, 0.95, "P5 框架数据流（对应论文 Fig.3 的方块图）", ha="center", fontsize=11)
    _watermark(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path = os.path.join(OUT, "p5_fig01_framework.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def fig_variables():
    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    ax.set_xlim(-0.2, 1.25)
    ax.set_ylim(-0.35, 1.05)
    ax.set_aspect("equal")
    ax.axis("off")

    # robots
    for bx, lab in ((0.02, "机器人 $i$"), (0.98, "机器人 $j$")):
        ax.add_patch(Rectangle((bx, 0.05), 0.10, 0.16, facecolor="#dfe6ee", edgecolor="#5b6b7c"))
        ax.text(bx + 0.05, -0.02, lab, ha="center", fontsize=9)
        ax.plot([bx + 0.05, bx + 0.05], [0.21, 0.40], color="#33414f", lw=3, solid_capstyle="round")
        ax.plot([bx + 0.05], [0.40], marker="o", ms=7, color="#c0392b")

    # object & reaching points
    ax.add_patch(Rectangle((0.40, 0.60), 0.22, 0.18, facecolor="#fde7c9", edgecolor="#b7791f"))
    ax.text(0.51, 0.82, "真实物体 $\\xi^O$", ha="center", fontsize=9)
    ax.plot([0.42], [0.62], marker="s", ms=7, color="#1f6f8b")
    ax.plot([0.60], [0.76], marker="s", ms=7, color="#1f6f8b")
    ax.text(0.42, 0.55, "到达点 $^i\\xi^O$", fontsize=8, ha="center", color="#1f6f8b")
    ax.text(0.63, 0.71, "$^j\\xi^O$", fontsize=8, color="#1f6f8b")

    # virtual object
    ax.plot([0.51], [0.36], marker="D", ms=10, color="#2e7d32")
    ax.text(0.51, 0.28, "虚拟物体 $\\xi^V$", ha="center", fontsize=9, color="#2e7d32")

    # targets
    ax.plot([0.16], [0.78], marker="*", ms=14, color="#6a1b9a")
    ax.text(0.16, 0.86, "$x_i^d$ (异步目标)", ha="center", fontsize=8, color="#6a1b9a")
    ax.plot([0.86], [0.78], marker="*", ms=14, color="#6a1b9a")
    ax.text(0.88, 0.86, "$x_j^d$", ha="center", fontsize=8, color="#6a1b9a")

    # vectors
    _arrow(ax, (0.05, 0.40), (0.51, 0.36), color="#c0392b")
    ax.text(0.20, 0.30, "$\\tau_{c_i}(x_i^V-x_i^d)$", fontsize=8, color="#c0392b")
    _arrow(ax, (0.51, 0.36), (0.51, 0.60), color="#2e7d32", ls="--")
    ax.text(0.53, 0.47, "$\\gamma\\,\\xi^O$ 方向", fontsize=8, color="#2e7d32")
    _arrow(ax, (1.03, 0.40), (0.60, 0.76), color="#c0392b")
    _arrow(ax, (0.16, 0.76), (0.02 + 0.05, 0.42), color="#6a1b9a", ls=":")

    ax.text(0.55, 0.99, "式(2) 的变量几何（二维示意，对应论文 Fig.2/Fig.4）", ha="center", fontsize=10.5)
    _watermark(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path = os.path.join(OUT, "p5_fig02_variables.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def fig_qp_structure():
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # matrix sketch
    x0, y0, cell = 0.20, 0.20, 0.052
    n = 9
    for i in range(n):
        for j in range(n):
            ax.add_patch(
                Rectangle((x0 + j * cell, y0 + (n - 1 - i) * cell), cell, cell,
                          facecolor="#f7f9fb", edgecolor="#d6dde5", lw=0.5)
            )

    def blk(i0, i1, j0, j1, color, label, fs=6.5, textcolor="#243342"):
        for i in range(i0, i1):
            for j in range(j0, j1):
                ax.add_patch(
                    Rectangle((x0 + j * cell, y0 + (n - 1 - i) * cell), cell, cell,
                              facecolor=color, edgecolor="#b9c4cf", lw=0.5)
                )
        ax.text(x0 + (j0 + (j1 - j0) / 2) * cell, y0 + (n - (i0 + (i1 - i0) / 2)) * cell,
                label, ha="center", va="center", fontsize=fs, color=textcolor)

    blk(0, 3, 0, 3, "#dbe7f3", "$W$")
    blk(0, 3, 3, 6, "#f6dcd6", "$-J^\\top$")
    blk(0, 3, 6, 9, "#dff0d8", "$-\\nabla\\Gamma$")
    blk(3, 6, 0, 3, "#f6dcd6", "$J$")
    blk(6, 9, 0, 3, "#dff0d8", "$\\nabla\\Gamma^\\top$")
    blk(3, 6, 3, 6, "#ffffff", "$0$")
    blk(6, 9, 6, 9, "#ffffff", "$0$")
    blk(3, 6, 6, 9, "#ffffff", "$0$")
    blk(6, 9, 3, 6, "#ffffff", "$0$")

    ax.annotate("$d_Q$", xy=(x0, y0 - 0.035), xytext=(x0 + 1.5 * cell, y0 - 0.035),
                ha="center", fontsize=8)
    ax.annotate("$d_N$", xy=(x0 + 3 * cell, y0 - 0.035), xytext=(x0 + 4.5 * cell, y0 - 0.035),
                ha="center", fontsize=8)
    ax.annotate("1", xy=(x0 + 6 * cell, y0 - 0.035), xytext=(x0 + 7.5 * cell, y0 - 0.035),
                ha="center", fontsize=8)

    ax.text(0.63, 0.72, "$M\\,u = b$ 的最优性条件 (21a)(21b)\n$u=[\\dot{q};\\ \\eta;\\ \\nu]$",
            fontsize=9.5, va="top")
    ax.text(0.63, 0.52, "不等式 $-$ 只出现在 $\\Omega$ 的投影里：\n"
                        "$\\dot{\\theta}^- \\leq \\dot{q} \\leq \\dot{\\theta}^+$ (17c)(18)\n"
                        "$-\\nabla\\Gamma^\\top\\dot{q} \\leq \\log(\\Gamma-1)$ (17d)\n"
                        "对偶变量 $\\nu \\geq 0$ (23)",
            fontsize=8.6, va="top")
    ax.text(0.63, 0.20, "投影动力学 (20):\n"
                        "$\\dot{u}=(I+M^\\top)(P_\\Omega(u-(Mu+b))-u)$",
            fontsize=8.6, va="top")

    ax.text(0.5, 0.96, "QP (17a-d) → LVI (19) → 块矩阵结构（对应式 (21a)）", ha="center", fontsize=10.5)
    _watermark(fig)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path = os.path.join(OUT, "p5_fig03_qp_structure.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def fig_sca_boundary():
    fig, ax = plt.subplots(figsize=(6.8, 5.2))

    def G(x, y):
        return 1.0 + 1.10 * np.sin(2.4 * np.pi * x) * np.cos(1.9 * np.pi * y) + 0.55 * (x - y) - 0.10

    g = np.linspace(0, 1, 500)
    X, Y = np.meshgrid(g, g)
    Z = G(X, Y)
    lv = ax.contourf(X, Y, Z, levels=np.linspace(Z.min(), Z.max(), 15), cmap="RdBu", alpha=0.78)
    ax.contour(X, Y, Z, levels=[1.0], colors="#111111", linewidths=1.8)
    ax.contour(X, Y, Z, levels=[0.0], colors="#777777", linewidths=0.7, linestyles=":")
    fig.colorbar(lv, ax=ax, shrink=0.86, label=r"$\Gamma(q^{ij})$（示意值）")

    # pick a point that sits on the Gamma = 1 contour
    idx = np.unravel_index(np.argmin(np.abs(Z - 1.0) + 0.02 * (X > 0.55) + 0.02 * (Y < 0.45)), Z.shape)
    q = np.array([X[idx], Y[idx]])

    def grad(p):
        h = 1e-4
        return np.array([(G(p[0] + h, p[1]) - G(p[0] - h, p[1])) / (2 * h),
                         (G(p[0], p[1] + h) - G(p[0], p[1] - h)) / (2 * h)])

    gr = grad(q)
    gr = gr / (np.linalg.norm(gr) + 1e-12)
    ax.annotate("", xy=q + 0.11 * gr, xytext=q,
                arrowprops=dict(arrowstyle="-|>", color="#111111", lw=2))
    ax.text(*(q + 0.125 * gr), r"$\nabla\Gamma$", fontsize=12)
    ax.plot([q[0]], [q[1]], "o", ms=8, color="#111111")

    t = np.array([-gr[1], gr[0]])
    L = 0.10
    ax.plot([q[0] - L * t[0], q[0] + L * t[0]],
            [q[1] - L * t[1], q[1] + L * t[1]], color="#0b5394", lw=2.0)
    ang = np.degrees(np.arctan2(t[1], t[0]))
    if ang > 90:
        ang -= 180
    if ang < -90:
        ang += 180
    ax.text(q[0] + 0.03, q[1] - 0.13,
            "蓝线 = (17d) 的切平面\n可行侧：$\\nabla\\Gamma^\\top\\dot{q}^{ij}\\geq -\\log(\\Gamma-1)$",
            fontsize=8.0, color="#0b5394", ha="left", va="top")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("$q^{ij}$ 分量 1（示意）")
    ax.set_ylabel("$q^{ij}$ 分量 2（示意）")
    ax.set_title(r"实线 $\Gamma=1$ 为安全边界，$\Gamma>1$ 自由、$\Gamma<1$ 碰撞 (16)", fontsize=10)
    _watermark(fig, "示意图：等值线为解析玩具函数，非官方学习模型输出")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path = os.path.join(OUT, "p5_fig04_sca_boundary.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def fig_sync_alloc():
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    t = np.linspace(0, 6, 600)
    # illustrative first-order relaxation (not simulation of eq.(8))
    tau = 0.01 + 0.98 / (1 + np.exp(-1.5 * (t - 2.4)))
    gamma = 1 - np.exp(-0.55 * t)

    ax2 = ax.twinx()
    ax.plot(t, tau, color="#c0392b", lw=2, label=r"$\tau_{c_i}$：同步分配 (0→异步, 1→同步)")
    ax2.plot(t, gamma, color="#2e7d32", lw=2, ls="--", label=r"$\gamma$：协调参数（虚拟物体→真实物体）")
    ax.axvline(2.4, color="#999999", lw=0.8, ls=":")
    ax.text(2.45, 0.12, "物体开始朝机器人运动", fontsize=8, color="#666666")

    ax.set_xlabel("时间 (示意)")
    ax.set_ylabel(r"$\tau_{c_i}$", color="#c0392b")
    ax2.set_ylabel(r"$\gamma$", color="#2e7d32")
    ax.set_ylim(-0.02, 1.05)
    ax2.set_ylim(-0.02, 1.05)
    lines = ax.get_lines()[:1] + ax2.get_lines()[:1]
    ax.legend(lines, [l.get_label() for l in lines], loc="center right", fontsize=8.5, frameon=False)
    ax.set_title("同步/异步行为与同步分配 $\\tau_{c_i}$、协调参数 $\\gamma$ 的定性关系（对应式 (8)(15)）", fontsize=10)
    _watermark(fig, "示意图：曲线为定性形状，非论文数据或仿真结果")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    path = os.path.join(OUT, "p5_fig05_sync_allocation.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def main():
    _setup_font()
    os.makedirs(OUT, exist_ok=True)
    for fn in (fig_framework, fig_variables, fig_qp_structure, fig_sca_boundary, fig_sync_alloc):
        print(fn())


if __name__ == "__main__":
    main()
