#!/usr/bin/env python3
"""T03 convergence errata: Richardson self-convergence with full pose, plus a
strict-JSON copy of the spectrum file.

Re-integrates the SAME deterministic fixtures used by T03 (A P1 and C P1) at h,
h/2 and h/4, this time recording orientation as well. The original npz
trajectories are not modified. No parameter, threshold or fixture is changed.
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "p2" / "tools"))

from baselines.p2_pose_force import contact_geometry as geo          # noqa: E402
from baselines.p2_pose_force import mechanics as mech               # noqa: E402
from baselines.p2_pose_force.observations import FilterState         # noqa: E402
from baselines.p2_pose_force.native_model import NativeModel, build_native  # noqa: E402
from t03_plant_audit import (build_objects, make_point, U0, MODES, DT0)      # noqa: E402

OUT = ROOT / "p2" / "reviews"
RUN = ROOT / "p2" / "runs" / "20261019_T03_CONVERGENCE_ERRATA"
SCALES = np.array([1e-3, 1e-3, 1e-3, 1e-3, 1e-3, 1e-3,
                   1e-3, 1e-3, 1e-3, 1e-3, 1e-3, 1e-3])


def integrate(native, state, ph, dt, duration=0.30, sample_dt=0.004):
    n = int(round(duration / dt))
    every = max(1, int(round(sample_dt / dt)))
    rows = []
    for k in range(n):
        state, _ = native.advance(state, U0, MODES, ph, dt, 1)
        if (k + 1) % every == 0:
            rows.append({"t": (k + 1) * dt,
                         "pos": state.O[:3, 3].copy(),
                         "rot": geo.se3_log(state.O)[3:].copy(),
                         "V": state.V.copy()})
    return rows


def diff(a, b):
    """12-vector difference in declared coordinates (m, rad, m/s, rad/s)."""
    dpos = a["pos"] - b["pos"]
    # rotations are stored as rotvec; differences are <= 1e-6 rad here, so the
    # component difference is a valid local chart difference (documented).
    drot = a["rot"] - b["rot"]
    return np.r_[dpos, drot, a["V"] - b["V"]]


def _R(rotvec):
    from scipy.spatial.transform import Rotation
    return Rotation.from_rotvec(rotvec).as_matrix()


def norms(a, b):
    d = diff(a, b)
    return {"pos": float(np.linalg.norm(d[0:3])),
            "rot": float(np.linalg.norm(d[3:6])),
            "vel_lin": float(np.linalg.norm(d[6:9])),
            "vel_ang": float(np.linalg.norm(d[9:12])),
            "combined_scaled": float(np.linalg.norm(d / SCALES))}


def main() -> int:
    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    objects = build_objects(cfg)
    native = NativeModel(build_native("/home/ubuntu2004/lmy/.p2_native_build_v3"))
    RUN.mkdir(parents=True, exist_ok=True)
    result = {"kind": "T03_CONVERGENCE_ERRATA", "duration_s": 0.30,
              "scales": SCALES.tolist(),
              "scale_note": "combined norm divides pos/rot/vel by 1e-3 only to make "
                            "the blocks commensurate; per-block orders do not depend on it",
              "objects": {}}

    for name in ("A", "C"):
        obj = objects[name]
        ph, st = obj["physics"], obj["state"]
        pt, meta = make_point(st, "P1", ph)
        traj = {lab: integrate(native, pt, ph, dt) for lab, dt in
                (("h", DT0), ("h_over_2", DT0 / 2), ("h_over_4", DT0 / 4))}
        for lab, rows in traj.items():
            np.savez_compressed(RUN / f"{name}_P1_{lab}.npz",
                                t=np.array([r["t"] for r in rows]),
                                pos=np.array([r["pos"] for r in rows]),
                                rot=np.array([r["rot"] for r in rows]),
                                V=np.array([r["V"] for r in rows]))
        n = min(len(traj["h"]), len(traj["h_over_2"]), len(traj["h_over_4"]))
        # adjacent differences (self-convergence) and old h/4-referenced errors
        e_adj = {k: [] for k in ("pos", "rot", "vel_lin", "vel_ang", "combined_scaled")}
        e_ref = {k: [] for k in ("pos", "rot", "vel_lin", "vel_ang", "combined_scaled")}
        for i in range(n):
            a, b, c = traj["h"][i], traj["h_over_2"][i], traj["h_over_4"][i]
            assert abs(a["t"] - b["t"]) < 1e-12 and abs(b["t"] - c["t"]) < 1e-12
            n_ab, n_bc, n_ac = norms(a, b), norms(b, c), norms(a, c)
            for k in e_adj:
                e_adj[k].append([n_ab[k], n_bc[k]])
                e_ref[k].append(n_ac[k])
        summary = {}
        for k in e_adj:
            arr = np.array(e_adj[k])
            e1 = float(np.max(arr[:, 0]))     # ||x_h - x_h/2||
            e2 = float(np.max(arr[:, 1]))     # ||x_h/2 - x_h/4||
            summary[k] = {
                "max_adjacent_h_h2": e1, "max_adjacent_h2_h4": e2,
                "order_richardson": (float(np.log2(e1 / e2)) if e1 > 0 and e2 > 0 else None),
                "order_old_reference_h4": (float(np.log2(float(np.max(e_ref[k])) / e2))
                                           if np.max(e_ref[k]) > 0 and e2 > 0 else None),
            }
        # final-time values, where the trajectory has settled the most
        last = n - 1
        n_ab, n_bc, n_ac = (norms(traj["h"][last], traj["h_over_2"][last]),
                            norms(traj["h_over_2"][last], traj["h_over_4"][last]),
                            norms(traj["h"][last], traj["h_over_4"][last]))
        final = {}
        for k in n_ab:
            final[k] = {"h_vs_h2": n_ab[k], "h2_vs_h4": n_bc[k], "h_vs_h4": n_ac[k],
                        "order_richardson": (float(np.log2(n_ab[k] / n_bc[k]))
                                             if n_ab[k] > 0 and n_bc[k] > 0 else None)}
        result["objects"][name] = {"meta": meta, "samples": n,
                                   "max_over_time": summary, "final_time": final,
                                   "rot_range_rad": [float(np.min(np.abs(np.array([r["rot"] for r in traj["h"]])))),
                                                     float(np.max(np.abs(np.array([r["rot"] for r in traj["h"]]))))]}
        print(name, "orders", {k: round(v["order_richardson"], 3) if v["order_richardson"] else None
                               for k, v in summary.items()})

    (OUT / "T03_CONVERGENCE_ERRATA.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # strict-JSON copy of the spectrum file
    src = json.loads((OUT / "T03_SPECTRUM.json").read_text())
    nonfinite = []

    def clean(node, path=""):
        if isinstance(node, dict):
            return {k: clean(v, f"{path}/{k}") for k, v in node.items()}
        if isinstance(node, list):
            return [clean(v, f"{path}[{i}]") for i, v in enumerate(node)]
        if isinstance(node, float) and not np.isfinite(node):
            nonfinite.append({"path": path, "value": str(node)})
            return None
        return node

    cleaned = clean(src)
    cleaned["_nonfinite_replaced_by_null"] = nonfinite
    cleaned["_source"] = "p2/reviews/T03_SPECTRUM.json (unmodified); only non-finite floats -> null"
    (OUT / "T03_SPECTRUM_STANDARD.json").write_text(
        json.dumps(cleaned, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8")
    print("non-finite replaced:", len(nonfinite), nonfinite[:3])
    print("wrote", OUT / "T03_CONVERGENCE_ERRATA.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
