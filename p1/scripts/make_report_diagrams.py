"""Algorithm diagrams for the P1 Chinese report (matplotlib, no external deps)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).resolve().parents[1] / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def box(ax, x, y, w, h, text, fc="#eef3fb", ec="#2f4b7c", fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color="#1b1b1b")


def arrow(ax, p1, p2, style="-|>", color="#333333", lw=1.2, rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=12,
                                 color=color, lw=lw, connectionstyle=f"arc3,rad={rad}"))


def architecture():
    fig, ax = plt.subplots(figsize=(10.6, 5.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.0); ax.axis("off")

    # row 1
    box(ax, 0.10, 3.30, 1.25, 0.90, "状态 $\\Theta_k$\n关节位置", fs=10.0)
    box(ax, 1.65, 3.30, 2.05, 0.90, "第一阶段采样\n$M$ 条，$\\Sigma_1$\n逐步零空间投影", fs=10.0)
    box(ax, 4.00, 3.30, 1.55, 0.90, "代价 $C_{exp}$\n含停滞项", fs=10.0)
    box(ax, 5.85, 3.30, 1.75, 0.90, "k-means\n$K$ 簇，特征\n$[C_{exp},\\Delta\\Theta]$", fs=9.6)
    box(ax, 7.90, 3.30, 1.90, 0.90, "精英众数选模\n$\\alpha^{*}$", fs=10.0)

    # row 2 (right to left)
    box(ax, 7.90, 1.55, 1.90, 0.90, "簇内加权聚合\n$\\sum w_iU_i/\\sum w_i$", fs=9.6)
    box(ax, 5.70, 1.55, 1.85, 0.90, "第二阶段\n$M$ 条，$\\Sigma_2<\\Sigma_1$", fs=9.6)
    box(ax, 3.55, 1.55, 1.80, 0.90, "全样本聚合\n（$C_{std}$）", fs=10.0)
    box(ax, 1.75, 1.55, 1.45, 0.90, "切换\n$L\\geq0$ ?", fs=10.0)
    box(ax, 0.10, 1.55, 1.35, 0.90, "低层\n$u_l=u_r+N_ru_h$", fs=9.2)

    # auxiliary branch
    box(ax, 1.75, 0.30, 1.45, 0.80, "辅助控制器\n$N_rJ_a^{+}e_a$", fs=9.2, fc="#fdf1e3", ec="#8a5a1f")

    # horizontal arrows row 1
    arrow(ax, (1.35, 3.75), (1.65, 3.75))
    arrow(ax, (3.70, 3.75), (4.00, 3.75))
    arrow(ax, (5.55, 3.75), (5.85, 3.75))
    arrow(ax, (7.60, 3.75), (7.90, 3.75))
    # down to row 2
    arrow(ax, (8.85, 3.30), (8.85, 2.45))
    # row 2 right to left
    arrow(ax, (7.90, 2.00), (7.55, 2.00))
    arrow(ax, (5.70, 2.00), (5.35, 2.00))
    arrow(ax, (3.55, 2.00), (3.20, 2.00))
    # auxiliary up into switch
    arrow(ax, (2.48, 1.10), (2.48, 1.55))
    # switch to low level
    arrow(ax, (1.75, 2.00), (1.45, 2.00))
    # low level down to robot
    arrow(ax, (0.78, 1.55), (0.78, 1.05))
    ax.text(0.78, 0.80, "机器人 / 下一周期", ha="center", fontsize=8)
    ax.text(2.48, 0.10, "（$L<0$ 时接管）", ha="center", fontsize=7.5, color="#8a5a1f")
    fig.tight_layout()
    fig.savefig(OUT / "fig1_architecture.png", dpi=220)
    plt.close(fig)


def two_stage():
    fig, ax = plt.subplots(figsize=(9.4, 3.9))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
    box(ax, 0.2, 2.3, 2.2, 1.0, "第一阶段：探索\n$M$ 条，$\\Sigma_1$ 大\n（$T_h$ 步投影）", fc="#e8f1e8", ec="#3d6b3d", fs=8.5)
    box(ax, 2.9, 2.3, 2.0, 1.0, "聚类（K 簇）\n精英 $m$ 条\n众数选模", fc="#e8f1e8", ec="#3d6b3d", fs=8.5)
    box(ax, 5.4, 2.3, 2.1, 1.0, "簇内聚合\n$\\sum w_iU_i/\\sum w_i$\n$w_i=e^{-C_i/\\lambda}$", fc="#e8f1e8", ec="#3d6b3d", fs=8.5)
    box(ax, 8.0, 2.3, 1.8, 1.0, "第二阶段\n$\\Sigma_2<\\Sigma_1$\n全样本聚合", fc="#fdf1e3", ec="#8a5a1f", fs=8.5)

    box(ax, 0.2, 0.5, 2.2, 0.85, "代价 $C_{exp}$\n含 $C_{stay}$", fs=8)
    box(ax, 2.9, 0.5, 2.0, 0.85, "描述子 $D$\n$[C_{exp},\\Delta\\Theta]$", fs=8)
    box(ax, 5.4, 0.5, 2.1, 0.85, "均值 $\\mu_{\\alpha^*}$\n（单一模式）", fs=8)
    box(ax, 8.0, 0.5, 1.8, 0.85, "输出序列\n热启动下一周期", fs=8)

    arrow(ax, (1.3, 2.3), (1.3, 1.35))
    arrow(ax, (2.4, 0.9), (2.9, 0.9))
    arrow(ax, (2.4, 2.8), (2.9, 2.8))
    arrow(ax, (3.9, 2.3), (3.9, 1.35))
    arrow(ax, (4.9, 0.9), (5.4, 0.9))
    arrow(ax, (4.9, 2.8), (5.4, 2.8))
    arrow(ax, (6.5, 2.3), (6.5, 1.35))
    arrow(ax, (7.5, 2.8), (8.0, 2.8))
    arrow(ax, (8.9, 2.3), (8.9, 1.35))
    ax.text(5.0, 3.55, "第一阶段：发现模式", fontsize=9, color="#3d6b3d", weight="bold")
    ax.text(8.0, 3.55, "第二阶段：局部精化", fontsize=9, color="#8a5a1f", weight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "fig2_two_stage.png", dpi=220)
    plt.close(fig)


def pose():
    fig, ax = plt.subplots(figsize=(8.2, 4.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.2); ax.axis("off")

    # bases
    ax.add_patch(plt.Rectangle((0.4, 0.5), 1.1, 0.35, fc="#cccccc", ec="#666"))
    ax.add_patch(plt.Rectangle((8.3, 0.5), 1.1, 0.35, fc="#cccccc", ec="#666"))
    ax.text(0.95, 0.25, "基座 1", ha="center", fontsize=8)
    ax.text(8.85, 0.25, "基座 2", ha="center", fontsize=8)

    # links (schematic)
    ax.plot([0.95, 2.0, 2.9, 3.9], [0.85, 1.7, 1.4, 2.5], "-o", color="#2f4b7c", lw=2, ms=4)
    ax.plot([8.85, 7.8, 6.9, 5.9], [0.85, 1.7, 1.4, 2.5], "-o", color="#2f4b7c", lw=2, ms=4)
    ax.add_patch(plt.Rectangle((4.05, 2.60), 1.9, 0.85, fc="#fdf1e3", ec="#8a5a1f", lw=1.5))
    ax.text(5.0, 3.02, "共持物体", ha="center", fontsize=9)

    # frames
    def frame(x, y, label, color):
        ax.annotate("", xy=(x + 0.5, y), xytext=(x, y),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4))
        ax.annotate("", xy=(x, y + 0.5), xytext=(x, y),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.4))
        ax.text(x + 0.05, y - 0.28, label, fontsize=9, color=color)

    frame(3.85, 2.35, "$\\mathcal{F}_1$", "#b03a2e")
    frame(6.05, 2.35, "$\\mathcal{F}_2$", "#1f618d")
    frame(0.95, 0.9, "$\\mathcal{F}_b$", "#555555")

    ax.text(0.3, 4.75, "相对位姿：$x_r=x_2^{*}x_1$（末端 1 在末端 2 系中）", fontsize=10)
    ax.text(0.3, 4.35, "绝对位姿：$x_a=x_2\\sqrt{x_r}$（SE(3) 群中点）", fontsize=10)
    ax.text(0.3, 3.95, "绝对直线：$l_a=n_a+\\epsilon\\,s_a\\times n_a$（倾角约束只用方向）", fontsize=10)
    ax.text(0.3, 3.55, "$\\sqrt{x_r}$ 为 SE(3) 平方根；$x_a^{-1}x_1=\\sqrt{x_r}$，$x_a^{-1}x_2=\\sqrt{x_r}^{-1}$", fontsize=9, color="#444")
    fig.tight_layout()
    fig.savefig(OUT / "fig3_pose_frames.png", dpi=220)
    plt.close(fig)


if __name__ == "__main__":
    architecture()
    two_stage()
    pose()
    print("diagrams written to", OUT)
