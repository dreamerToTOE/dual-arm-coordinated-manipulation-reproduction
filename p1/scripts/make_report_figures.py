"""Generate the numerical figures used by the Chinese reproduction report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "reports"
FIG = REP / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def load(name):
    return json.loads((REP / name).read_text(encoding="utf-8"))


def fig_g1():
    d = load("G1_ACCEPTANCE.json")
    t = d["B2_drift_table"]
    th = np.array([r["Th"] for r in t])
    p = np.array([r["projected"] for r in t])
    u = np.array([r["unprojected"] for r in t])
    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    ax.loglog(th, p, "o-", label=f"projected (slope {d['B2_projected_slope']:.3f})")
    ax.loglog(th, u, "s-", label=f"unprojected (slope {d['B2_unprojected_slope']:.3f})")
    ax.set_xlabel("$T_h$ (s)")
    ax.set_ylabel(r"$\|x_r(T)-x_r(0)\|$")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    ax.set_title("Null-space projection: finite-step drift")
    fig.tight_layout()
    fig.savefig(FIG / "g1_drift_scaling.png", dpi=200)
    plt.close(fig)


def fig_g2():
    d = load("G2_ACCEPTANCE.json")["N2_traces"]
    fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.2), sharey=True)
    for ax, (eta, tr) in zip(axes, d.items()):
        x = np.arange(len(tr["L"]))
        ax.plot(x, tr["L"], "o-", color="tab:blue", label="$L$")
        ax.set_ylim(-0.08, 0.45)
        ax.set_xlabel("control cycle")
        ax.set_title(f"$\\eta$ = {eta.split('_')[1]}")
        ax.grid(alpha=0.3)
        ax2 = ax.twinx()
        ax2.plot(x, tr["ratio"], "s--", color="tab:orange", label="$C_t/C_s$")
        ax2.axhline(float(eta.split("_")[1]), color="tab:red", lw=1, ls=":", label="threshold")
        ax2.set_ylim(0, 1.8)
        ax2.set_ylabel("$C_t/C_s$")
        for i, a in enumerate(tr["aux"]):
            if a:
                ax.axvspan(i - 0.4, i + 0.4, color="tab:green", alpha=0.15)
    axes[0].set_ylabel("$L$")
    axes[0].legend(loc="upper left", fontsize=7)
    axes[1].legend(loc="upper left", fontsize=7)
    fig.suptitle("Auxiliary switching: L and cost ratio (green = auxiliary active)", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "g2_switch_traces.png", dpi=200)
    plt.close(fig)


def fig_g3_ablation():
    d = load("G3_ACCEPTANCE.json")
    f2 = d["F2"]
    names = ["full", "no_variance_reduction", "stage1_only", "stage1_only_budget_matched",
             "no_cluster", "adaptive_lambda", "inertia"]
    labels = ["full", "no $\\Sigma$ red.", "stage1 only\n(500/iter)", "stage1 only\n(1000/iter)",
              "no cluster", "adaptive $\\lambda$", "inertia"]
    vals = [f2[n]["success_count"] for n in names]
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    bars = ax.bar(range(len(vals)), vals, color=["tab:blue"] + ["tab:gray"] * 6)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylabel("success / 20 seeds")
    ax.set_ylim(0, 21)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, str(v), ha="center", fontsize=8)
    ax.set_title("Mechanism ablation (two-corridor task)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "g3_ablation.png", dpi=200)
    plt.close(fig)


def fig_g3b():
    d = load("G3B_VARIANTS.json")["results"]
    names = ["ours_two_stage", "mppi", "log_mppi", "fre_mppi", "biased_mppi", "high_mppi", "cem"]
    labels = ["two-stage", "MPPI\n(Gauss)", "Log-MPPI", "Fre-MPPI", "Biased", "High", "CEM"]
    rate = np.array([d[n]["success_rate"] for n in names])
    lo = np.array([d[n]["success_ci95"][0] for n in names])
    hi = np.array([d[n]["success_ci95"][1] for n in names])
    err = np.vstack([rate - lo, hi - rate])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar(range(len(rate)), rate, yerr=err, capsize=3,
           color=["tab:blue"] + ["tab:gray"] * 6)
    ax.set_xticks(range(len(rate)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("success rate (30 seeds, 95% Wilson CI)")
    ax.set_title("Controller variants on the two-corridor task (equal budget)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG / "g3b_variants.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig_g1()
    fig_g2()
    fig_g3_ablation()
    fig_g3b()
    print("figures written to", FIG)
