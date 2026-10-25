"""Render key display equations as PNG (matplotlib mathtext) for the report."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["font.family"] = "STIXGeneral"

OUT = Path(__file__).resolve().parents[1] / "reports" / "final" / "eq"
OUT.mkdir(parents=True, exist_ok=True)

EQUATIONS = {
    "eq01_pose_composition": (
        r"x = r + \varepsilon\,\frac{1}{2}\,p\,r ,\quad "
        r"r = a + b\,i + c\,j + d\,k ,\ a^{2}+b^{2}+c^{2}+d^{2}=1 \qquad (3)(4)"
    ),
    "eq02_relative": r"x_r = x_2^{*}\, x_1 \qquad (7)",
    "eq03_absolute": r"x_a = x_2 \otimes \sqrt{x_r} \qquad (8)",
    "eq04_jacobian": (
        r"\dot{x}_r = \dot{x}_2^{*}\,x_1 + x_2^{*}\,\dot{x}_1 "
        r"= C_8\,\dot{x}_2\,x_1 + x_2^{*}\,\dot{x}_1"
        r"\qquad J_r = \left[\,H_+(x_2^{*})\,J_1,\; H_-(x_1)\,C_8\,J_2\,\right] \qquad (11)"
    ),
    "eq05_nullspace": (
        r"u_i^{\mathrm{null}} = N(S_i)\,u_i ,\quad "
        r"N(S_i) = I - J_c^{+}(S_i)\,J_c(S_i) ,\quad "
        r"\Theta_{i+1} = \Theta_i + T_h\,u_i^{\mathrm{null}} \qquad (26)(27)(31)"
    ),
    "eq06_weighting": (
        r"w_i = \exp\!\left(-\frac{C_i}{\lambda}\right) ,\quad "
        r"U^{*} = \frac{\sum_{i} w_i\,U_i}{\sum_{i} w_i} \qquad (23)"
    ),
    "eq07_kmeans": (
        r"\min_{\alpha_k}\;\sum_{k}\sum_{D\in\alpha_k}\|D-\mu_k\|^{2} ,\quad "
        r"D = \left[\,C_{\mathrm{exp}},\; (\Theta_0-\Theta_N)^{\top}\,\right] \qquad (22)(52)"
    ),
    "eq08_singularity": (
        r"w = \sqrt{\prod_{i=1}^{6}\sigma_i} ,\quad "
        r"C_{\mathrm{sing}} = \frac{p_e}{\max(\zeta,\,w)} \qquad (36)(37)"
    ),
    "eq09_auxiliary": (
        r"u_a = J_a^{+}\,K_a\,e_a ,\quad e_a = \mathrm{vec8}(x_{a,d}-x_a) ,\quad "
        r"u_t = N_r\,u_a \qquad (44)(45)"
    ),
    "eq10_switching": (
        r"L_{k+1} = L_k + T_h\left(\frac{C_{k,t}}{C_{k,s}}-\eta\right) ,\quad "
        r"L_{k+1} = \mathrm{clip}\left(L_{k+1},\,L_{\min},\,L_{\max}\right) \qquad (47)(48)"
    ),
}


def render(eq: str, path: Path, dpi: int = 150):
    fig = plt.figure(figsize=(0.1, 0.1))
    fig.text(0, 0, "$" + eq + "$", fontsize=20)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.02, dpi=dpi, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    for name, eq in EQUATIONS.items():
        render(eq, OUT / f"{name}.png")
    print("equations written to", OUT)
