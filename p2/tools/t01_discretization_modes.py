#!/usr/bin/env python3
"""T01: closed-form amplification factors for candidate Eq.(18) discretizations.

Pure linear algebra on the CONTINUOUS eigen-spectrum already measured in
results/20261014_P2_stage2_numerical_audit01. No plant, no filter, no trajectory.

For the scalar test equation  xdot = lambda x  the one-step amplification is
    Euler          R = 1 + z
    implicit Euler R = 1 / (1 - z)
    trapezoid/CN   R = (1 + z/2) / (1 - z/2)
    matrix exp     R = exp(z)
    Euler substeps R = (1 + z/n)^n
with z = h*lambda.  |R| > 1 means the discrete propagation is unstable.
"""
import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "reviews" / "T01_DISCRETIZATION_MODES.json"

# Eigenvalues measured (not re-simulated) in the pre-run numerical audit.
SPECTRA = {
    "A_nominal": [
        (-2183.06990210081, 0.0),
        (-352.5751546641485, 0.0),
        (-83.54480449508625, -97.74101281240695),
        (-83.54480449508625, 97.74101281240695),
        (-73.09948830425131, -105.59648126712456),
        (-73.09948830425131, 105.59648126712456),
    ],
    "C_nominal": [
        (-9335.806743430947, 0.0),
        (-452.83004259913815, 0.0),
        (-145.5874945027786, -105.5800346879516),
        (-145.5874945027786, 105.5800346879516),
    ],
}

STEPS = {
    "1/3000": 1.0 / 3000.0,
    "1/1000": 1.0 / 1000.0,
    "3ms_observed_last_prediction": 0.003,
    "4ms_paper_filter": 0.004,
}

SCHEMES = ("euler", "implicit_euler", "trapezoid", "matrix_exp")


def amp(scheme: str, z: complex, substeps: int = 1):
    if scheme == "euler":
        return 1.0 + z
    if scheme == "implicit_euler":
        return 1.0 / (1.0 - z)
    if scheme == "trapezoid":
        return (1.0 + z / 2.0) / (1.0 - z / 2.0)
    if scheme == "matrix_exp":
        return complex(math.e ** z.real * math.cos(z.imag),
                       math.e ** z.real * math.sin(z.imag))
    if scheme == "euler_substeps":
        return (1.0 + z / substeps) ** substeps
    raise ValueError(scheme)


def table() -> dict:
    out = {}
    for fixture, spectrum in SPECTRA.items():
        fastest = min(abs(lam) for lam, _ in spectrum)
        # fastest decaying real mode (largest |lambda|)
        lam_fast = max(spectrum, key=lambda p: abs(complex(*p)))
        out[fixture] = {
            "fastest_mode_per_s": {"real": lam_fast[0], "imag": lam_fast[1]},
            "fastest_mode_modulus_per_s": abs(complex(*lam_fast)),
            "euler_critical_step_s": 2.0 / abs(complex(*lam_fast)),
            "euler_critical_rate_hz": abs(complex(*lam_fast)) / 2.0,
            "spectrum_modulus_range": [fastest, abs(complex(*lam_fast))],
            "by_step": {},
        }
        for step_name, h in STEPS.items():
            rows = {}
            for scheme in SCHEMES:
                factors = [abs(amp(scheme, complex(lam, om) * h)) for lam, om in spectrum]
                rows[scheme] = {
                    "max_abs_amplification": max(factors),
                    "fast_mode_abs_amplification": abs(
                        amp(scheme, complex(lam_fast[0], lam_fast[1]) * h)),
                    "stable_all_modes": max(factors) <= 1.0,
                }
            substeps = {}
            for n in (2, 4, 5, 8, 16):
                f = abs(amp("euler_substeps", complex(lam_fast[0], lam_fast[1]) * h, n))
                substeps[str(n)] = {"fast_mode_abs_amplification": f, "stable": f <= 1.0}
            rows["euler_substeps"] = substeps
            # ratio of the EXACT discrete process noise to the naive h*q for the fast mode
            re = lam_fast[0]
            ratio = (1.0 - math.exp(2.0 * re * h)) / (-2.0 * re * h)
            rows["exact_Qd_over_naive_hQc_fast_mode"] = ratio
            out[fixture]["by_step"][step_name] = {"h_s": h, "schemes": rows}
    return out


def main() -> int:
    data = table()
    data["meta"] = {
        "kind": "T01_ANALYTIC_DISCRETIZATION_TABLE",
        "source_spectrum": "results/20261014_P2_stage2_numerical_audit01/summary.json "
                           "(continuous_eigenvalues_per_s), not re-integrated",
        "units": "lambda in 1/s, h in s, amplification dimensionless",
        "criterion": "|R(h*lambda)| <= 1 for every eigen-mode",
        "not_a_simulation": True,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for fixture in SPECTRA:
        f = data[fixture]
        print(f"== {fixture}: fastest |lambda|={f['fastest_mode_modulus_per_s']:.2f} 1/s "
              f"-> Euler h_crit={f['euler_critical_step_s']*1e3:.3f} ms")
        for step_name, blk in f["by_step"].items():
            h = blk["h_s"]
            parts = []
            for scheme in SCHEMES:
                parts.append(f"{scheme}={blk['schemes'][scheme]['max_abs_amplification']:.4g}")
            sub = blk["schemes"]["euler_substeps"]
            parts.append("euler_n5=" + format(sub["5"]["fast_mode_abs_amplification"], ".4g"))
            parts.append("Qd_ratio=" + format(blk["schemes"]["exact_Qd_over_naive_hQc_fast_mode"], ".4g"))
            print(f"  h={h*1e3:.3f} ms  " + "  ".join(parts))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
