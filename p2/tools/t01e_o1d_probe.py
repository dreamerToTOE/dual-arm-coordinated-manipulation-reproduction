#!/usr/bin/env python3
"""O1-d probe: compare a custom SO(3) Log against scipy, before touching code.

Only se3_log is in scope. The probe reports max absolute and relative differences
for random poses, small angles, near-pi and exact-pi cases. O1-d is adopted only
if every case stays within 1e-12 (absolute and meaningful relative).
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from baselines.p2_pose_force import contact_geometry as geo     # noqa: E402

OUT = ROOT / "p2" / "reviews" / "t01e_o1d_probe.json"


def rotvec_custom(R):
    tr = float(R[0, 0] + R[1, 1] + R[2, 2])
    c = max(-1.0, min(1.0, (tr - 1.0) / 2.0))
    theta = math.acos(c)
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    if theta < 1e-7:
        return 0.5 * v
    if math.pi - theta < 1e-6:
        A = (R + np.eye(3)) / 2.0
        i = int(np.argmax(np.diag(A)))
        w = A[:, i] / math.sqrt(max(A[i, i], 1e-300))
        w = w / np.linalg.norm(w)
        return w * theta
    return (theta / (2.0 * math.sin(theta))) * v


def compare(title, rotations):
    worst_abs = 0.0
    worst_rel = 0.0
    worst_matrix = 0.0
    for R in rotations:
        ref = Rotation.from_matrix(R).as_rotvec()
        got = rotvec_custom(R)
        d = np.abs(ref - got)
        scale = np.maximum(np.abs(ref), np.abs(got))
        rel = np.where(scale >= 1e-12, d / np.maximum(scale, 1e-300), 0.0)
        worst_abs = max(worst_abs, float(np.max(d)))
        worst_rel = max(worst_rel, float(np.max(rel)))
        worst_matrix = max(worst_matrix,
                           float(np.max(np.abs(Rotation.from_rotvec(got).as_matrix() - R))))
    return {"case": title, "n": len(rotations), "max_abs": worst_abs,
            "max_rel_meaningful": worst_rel, "max_matrix_error": worst_matrix,
            "pass": worst_abs <= 1e-12 and worst_rel <= 1e-12}


def main() -> int:
    rng = np.random.default_rng(20261019)
    cases = []
    # random axes, angles uniform in [0, pi-1e-3]
    rot = []
    for _ in range(3000):
        axis = rng.normal(size=3); axis /= np.linalg.norm(axis)
        rot.append(Rotation.from_rotvec(axis * rng.uniform(0.0, math.pi - 1e-3)).as_matrix())
    cases.append(compare("random_3000", rot))

    # small angles
    small = []
    for mag in (1e-12, 1e-10, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4):
        axis = np.array([0.3, -0.5, 0.81]); axis /= np.linalg.norm(axis)
        small.append(Rotation.from_rotvec(axis * mag).as_matrix())
    cases.append(compare("small_angle", small))

    # near pi
    near = []
    for gap in (1e-3, 1e-5, 1e-7, 1e-8):
        axis = np.array([0.2, -0.6, 0.77]); axis /= np.linalg.norm(axis)
        near.append(Rotation.from_rotvec(axis * (math.pi - gap)).as_matrix())
    cases.append(compare("near_pi", near))

    # exact pi around the three coordinate axes (sign ambiguity, matrix checked)
    exact = [Rotation.from_rotvec(np.array([math.pi, 0, 0])).as_matrix(),
             Rotation.from_rotvec(np.array([0, math.pi, 0])).as_matrix(),
             Rotation.from_rotvec(np.array([0, 0, math.pi])).as_matrix()]
    cases.append(compare("exact_pi_axes", exact))

    # identity
    cases.append(compare("identity", [np.eye(3)]))

    # full se3_log path on a pose with translation
    tau = np.r_[0.01, -0.02, 0.03, 0.2, -0.3, 0.1]
    T = geo.se3_exp(tau)
    ref = geo.se3_log(T)
    got = np.r_[np.linalg.solve(geo._V(rotvec_custom(T[:3, :3])), T[:3, 3]), rotvec_custom(T[:3, :3])]
    d = np.abs(ref - got)
    scale = np.maximum(np.abs(ref), np.abs(got))
    rel = np.where(scale >= 1e-12, d / np.maximum(scale, 1e-300), 0.0)
    cases.append({"case": "se3_log_full_pose", "n": 1, "max_abs": float(np.max(d)),
                  "max_rel_meaningful": float(np.max(rel)),
                  "max_matrix_error": 0.0,
                  "pass": float(np.max(d)) <= 1e-12 and float(np.max(rel)) <= 1e-12})

    all_pass = all(c["pass"] for c in cases)
    payload = {"kind": "T01E_O1D_PROBE", "cases": cases, "adopt": all_pass,
               "criterion": "abs <= 1e-12 and meaningful rel <= 1e-12"}
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for c in cases:
        print(f"{'PASS' if c['pass'] else 'FAIL'} {c['case']:<18} n={c['n']:<5} "
              f"abs={c['max_abs']:.3e} rel={c['max_rel_meaningful']:.3e} "
              f"matrix={c['max_matrix_error']:.3e}")
    print("adopt:", all_pass)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
