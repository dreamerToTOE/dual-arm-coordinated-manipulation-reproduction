#!/usr/bin/env python3
"""T04 stage A: stable predictor implementation qualification (prediction only).

Compares, on identical fixtures and parameters:
  mode A  PAPER_LITERAL_EULER            (estimator.prediction_linearization)
  mode B  ADAPTED_STABLE_PROPAGATION_V1  (stable_propagation.propagate)
  native  implicit plant one-step map    (reference only, not the estimator)

For every fixture and step it computes the right-error FD Jacobian of each map
separately and reports it next to the analytic Phi; it never assumes they are
equal. Covariance propagation and the Van Loan Qd are checked independently.

No estimator default path is modified, no closed loop, no observation update.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "p2" / "tools"))

from baselines.p2_pose_force import mechanics as mech               # noqa: E402
from baselines.p2_pose_force import estimator as est                 # noqa: E402
from baselines.p2_pose_force import stable_propagation as sp         # noqa: E402
from baselines.p2_pose_force.observations import FilterState          # noqa: E402
from baselines.p2_pose_force.native_model import NativeModel, build_native  # noqa: E402
from t03_plant_audit import build_objects, equilibrium_state, U0, DT0  # noqa: E402

REV = ROOT / "p2" / "reviews"
RUN = ROOT / "p2" / "runs" / "20261019_T04_STAGE_A"
EPS = 1e-6
CAP = 180.0


def fd_jacobian(map_fn, state, eps=EPS):
    base = map_fn(state)
    J = np.zeros((42, 42))
    for j in range(42):
        e = np.zeros(42); e[j] = eps
        J[:, j] = map_fn(state.retract(e)).local(map_fn(state.retract(-e))) / (2 * eps)
    return J, base


def classify(ev):
    rho = float(np.max(np.abs(ev)))
    neutral = int(np.sum(np.abs(np.abs(ev) - 1.0) <= 1e-9))
    unstable = int(np.sum(np.abs(ev) > 1.0 + 1e-9))
    return {"rho": rho, "neutral_count": neutral, "unstable_count": unstable,
            "max_real": float(np.max(ev.real))}


def pad_ok(contact):
    return bool(np.all(np.abs(contact.tau[:, :3]) <= 0.005)
                and np.all(np.abs(contact.tau[:, 3:]) <= 0.15))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall-cap", type=float, default=CAP)
    args = ap.parse_args()
    t_start = time.perf_counter()

    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    objects = build_objects(cfg)
    native = NativeModel(build_native("/home/ubuntu2004/lmy/.p2_native_build_v3"))
    probe = est.RightIESEKF.from_protocol(FilterState.from_mechanics(objects["A"]["state"]),
                                          cfg, condition="exp3", object_id="A",
                                          modes=("pivot", "pivot"))
    QC = probe.Qc_diag.copy()
    P0 = probe.P.copy()
    RUN.mkdir(parents=True, exist_ok=True)

    eqA, _ = equilibrium_state(native, objects["A"]["state"], objects["A"]["physics"])

    def states_for(name):
        obj = objects[name]
        base = eqA if (name == "A" and eqA is not None) else obj["state"]
        out = {"S1_static": (base, ("pivot", "pivot"), "static reference")}
        d = np.zeros(42)
        d[0:6] = [0.001, -0.0008, 0.0005, 0.008, -0.006, 0.004]
        d[6:12] = [0.02, -0.01, 0.005, 0.10, -0.05, 0.02]
        out["S2_moving_deformed"] = (base.retract(d), ("pivot", "pivot"), "1 mm/10 mrad + velocity")
        d = np.zeros(42); d[:6] = 1e-7; d[6:12] = 1e-8
        out["S3_small_angle"] = (base.retract(d), ("pivot", "pivot"), "1e-7 m/rad")
        d2 = np.zeros(42); d2[6:12] = [0.02, -0.01, 0.005, 0.10, -0.05, 0.02]
        out["S2b_near_eq_moving"] = (base.retract(d2), ("pivot", "pivot"),
                                     "velocity only, no pose offset (near equilibrium)")
        # Large attitude of the whole grasped assembly: rotate object and both
        # arms together (so the pad deformation stays legal), then add a small
        # differential deformation on arm 1.
        from scipy.spatial.transform import Rotation as _Rot
        R = _Rot.from_rotvec([0.5, -0.2, 0.1]).as_matrix()
        T = np.eye(4); T[:3, :3] = R
        from baselines.p2_pose_force.contact_geometry import inverse as _inv
        O4 = T @ base.O
        E14 = T @ base.E1
        E24 = base.C @ T @ _inv(base.C) @ base.E2
        diff = np.array([0.001, 0.0, 0.0, 0.02, 0.0, 0.0])
        E14 = E14 @ __import__("baselines.p2_pose_force.contact_geometry",
                                fromlist=["se3_exp"]).se3_exp(diff)
        s4 = FilterState(O4, base.V.copy(), E14, E24, base.C.copy(),
                         base.G1.copy(), base.G2.copy())
        out["S4_large_attitude"] = (s4, ("pivot", "pivot"),
                                   "0.56 rad world attitude with arms following; 1 mm/20 mrad differential")
        if name == "A":
            out["S5_mode_boundary"] = (base, ("pivot", "pivot"), "pivot, tau_z moment near zero")
        else:
            tilt = FilterState(obj["state"].O, obj["state"].V * 0.0,
                               obj["state"].E1 @ np.array([[1, 0, 0, 0],
                                                           [0, np.cos(1e-3), -np.sin(1e-3), 0],
                                                           [0, np.sin(1e-3), np.cos(1e-3), 0],
                                                           [0, 0, 0, 1]]),
                               obj["state"].E2, obj["state"].C, obj["state"].G1, obj["state"].G2)
            out["S5_mode_boundary"] = (tilt, ("sliding", "sliding"), "sliding axes tilted 1 mrad (rank 5)")
        return out

    steps = (("h_1_3000", 1 / 3000), ("h_1ms", 1e-3), ("h_3ms", 3e-3), ("h_4ms", 4e-3))
    result = {"kind": "T04_STAGE_A",
              "mode_a": sp.MODE_A, "mode_b": sp.MODE_B,
              "eps": EPS, "thresholds": {"abs": 1e-12, "rel": 1e-12},
              "cases": []}

    def timeit(fn, n=5):
        ts = []
        for _ in range(n):
            t0 = time.perf_counter(); fn(); ts.append(time.perf_counter() - t0)
        return float(np.median(ts))

    for name in ("A", "C"):
        ph = objects[name]["physics"]
        for skey, (state, modes, note) in states_for(name).items():
            fs = FilterState.from_mechanics(state)
            for dkey, h in steps:
                if time.perf_counter() - t_start > args.wall_cap:
                    result["budget_stop"] = True
                    break
                try:
                    f, A = native.continuous_linearization(state, U0, modes, ph)
                    contact = native.contact(state, U0, modes, ph)

                    # mode A (literal baseline, unchanged code)
                    pred_a, F_a, Lw_a = est.prediction_linearization(
                        fs, U0, modes, ph, h, rate_provider=native.continuous_linearization)
                    Qd_a = h * (Lw_a * QC[None, :]) @ Lw_a.T

                    # mode B (our stable adaptation)
                    t_vl0 = time.perf_counter()
                    pred_b, Phi_b, Qd_b, delta_b = sp.propagate(fs, f, A, h, QC)
                    vl_ms = (time.perf_counter() - t_vl0) * 1e3

                    # theoretical references
                    I = np.eye(42)
                    Phi_trap = np.linalg.solve(I - h * A / 2, I + h * A / 2)
                    Phi_exp = expm(h * A)

                    # right-error FD Jacobians of the three actual maps
                    def map_a(s, h=h):
                        ff, _ = est.continuous_linearization(s, U0, modes, ph)
                        return s.retract(h * ff)

                    def map_b(s, h=h):
                        ff, AA = native.continuous_linearization(s, U0, modes, ph)
                        _, d = sp.phi1_action(AA, ff, h)
                        return s.retract(d)

                    def map_n(s, h=h):
                        out, _ = native.advance(s, U0, modes, ph, h, 1)
                        return out

                    J_a, _ = fd_jacobian(map_a, fs)
                    J_b, _ = fd_jacobian(map_b, fs)
                    J_n, _ = fd_jacobian(map_n, fs)

                    # Qd qualification (mode B)
                    G = np.diag(QC)
                    sym = float(np.max(np.abs(Qd_b - Qd_b.T)) / max(np.max(np.abs(Qd_b)), 1e-300))
                    ev_q = np.linalg.eigvalsh((Qd_b + Qd_b.T) / 2)
                    psd = float(ev_q[0] / max(ev_q[-1], 1e-300))
                    lyap = A @ Qd_b + Qd_b @ A.T - (Phi_b @ G @ Phi_b.T - G)
                    lyap_rel = float(np.max(np.abs(lyap)) / max(np.max(np.abs(G)), 1e-300))
                    if h <= 1e-3:      # quadrature reference only for the affordable steps
                        Qref = sp.qd_integral_reference(A, G, h, intervals=80)
                        qref_rel = float(np.max(np.abs(Qd_b - Qref)) / max(np.max(np.abs(Qref)), 1e-300))
                    else:
                        Qref, qref_rel = None, None

                    # covariance propagation
                    P_a = F_a @ P0 @ F_a.T + Qd_a
                    P_b = Phi_b @ P0 @ Phi_b.T + Qd_b
                    def spd(M):
                        ev = np.linalg.eigvalsh((M + M.T) / 2)
                        return {"symmetry": float(np.max(np.abs(M - M.T))),
                                "min_eig": float(ev[0]), "max_eig": float(ev[-1])}

                    # short-time non-normal amplification
                    amp = [float(np.linalg.norm(expm(t * A), 2)) for t in (h / 4, h / 2, h)]
                    ev_a, ev_b, ev_n = (np.linalg.eigvals(F_a), np.linalg.eigvals(Phi_b),
                                        np.linalg.eigvals(J_n))

                    rec = {
                        "object": name, "state": skey, "note": note, "modes": list(modes),
                        "dt": h, "f_norm": float(np.linalg.norm(f)),
                        "pad_domain_ok": pad_ok(contact),
                            "phi": {
                            "rho_a": float(np.max(np.abs(ev_a))),
                            "rho_b": float(np.max(np.abs(ev_b))),
                            "rho_trap": float(np.max(np.abs(np.linalg.eigvals(Phi_trap)))),
                            "rho_native_fd": float(np.max(np.abs(ev_n))),
                            "class_a": classify(ev_a), "class_b": classify(ev_b),
                            "class_native": classify(ev_n),
                        },
                        "phi_vs_fd": {
                            "F_a_vs_J_a": float(np.max(np.abs(F_a - J_a))),
                            "Phi_b_vs_J_b": float(np.max(np.abs(Phi_b - J_b))),
                            "Phi_trap_vs_J_native": float(np.max(np.abs(Phi_trap - J_n))),
                            "Phi_b_vs_J_native": float(np.max(np.abs(Phi_b - J_n))),
                            "F_a_vs_J_native": float(np.max(np.abs(F_a - J_n))),
                            "scale": float(max(np.max(np.abs(J_n)), 1.0)),
                        },
                        "qd": {"symmetry_rel": sym, "min_over_max_eig": psd,
                           "vanloan_ms": float(vl_ms),
                               "lyapunov_rel": lyap_rel,
                               "simpson_rel": qref_rel,
                               "trace": float(np.trace(Qd_b))},
                        "cov": {"P_a": spd(P_a), "P_b": spd(P_b),
                                "trace_ratio_b_over_a": float(np.trace(P_b) / np.trace(P_a))},
                        "nonnormal_amplification": amp,
                        "cost_ms": {"predict_a": timeit(lambda: est.prediction_linearization(
                                        fs, U0, modes, ph, h,
                                        rate_provider=native.continuous_linearization)),
                                    "predict_b": timeit(lambda: sp.propagate(fs, f, A, h, QC))},
                    }
                except Exception as exc:            # keep going, record honestly
                    import traceback as _tb
                    result["cases"].append({"object": name, "state": skey, "dt": h,
                                            "note": note, "modes": list(modes),
                                            "status": "FAIL", "error": repr(exc),
                                            "traceback": _tb.format_exc()})
                else:
                    result["cases"].append(rec)
    # h-refinement of the analytical-vs-FD mismatch for the deformed moving state
    consistency = {}
    for name in ("A", "C"):
        ph = objects[name]["physics"]
        st = states_for(name)["S2_moving_deformed"][0]
        fs = FilterState.from_mechanics(st)
        seq = []
        for h in (4e-3, 2e-3, 1e-3, 5e-4, 2.5e-4):
            f, A = native.continuous_linearization(st, U0, ("pivot", "pivot"), ph)
            Phi, _ = sp.phi1_action(A, f, h)
            def map_b(s, h=h):
                ff, AA = native.continuous_linearization(s, U0, ("pivot", "pivot"), ph)
                _, d = sp.phi1_action(AA, ff, h)
                return s.retract(d)
            J, _ = fd_jacobian(map_b, fs)
            seq.append({"h": h, "abs": float(np.max(np.abs(Phi - J))),
                        "scale": float(np.max(np.abs(J)))})
        for i in range(1, len(seq)):
            seq[i]["ratio_to_prev"] = (seq[i - 1]["abs"] / seq[i]["abs"]
                                       if seq[i]["abs"] > 0 else None)
        consistency[name] = seq
    result["phi_consistency_refinement"] = consistency
    result["wall_s"] = time.perf_counter() - t_start
    result["cap_s"] = args.wall_cap
    result["count"] = len(result["cases"])
    (REV / "T04_STAGE_A.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"cases": result["count"], "wall_s": round(result["wall_s"], 2)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
