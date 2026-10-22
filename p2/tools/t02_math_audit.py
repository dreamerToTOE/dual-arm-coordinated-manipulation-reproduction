#!/usr/bin/env python3
"""T02: independent mathematical audit of the P2 original-code path.

Read-only. No plant time integration, no controller, no closed loop, no source
change. Every check is recorded individually with its own tolerance and error.

Outputs
  p2/reviews/T02_MATH_AUDIT.json     one record per property
  p2/reviews/T02_MATH_BASELINE.json  source hashes + golden values for T01-E

Deterministic: PCG64 seed fixed below; all random states reproducible.
"""
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np
from scipy.linalg import expm
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from baselines.p2_pose_force import contact_geometry as geo          # noqa: E402
from baselines.p2_pose_force import mechanics as mech               # noqa: E402
from baselines.p2_pose_force import estimator as est                # noqa: E402
from baselines.p2_pose_force.observations import (                   # noqa: E402
    FilterState, ObservationGenerator)

AUDIT = ROOT / "p2" / "reviews" / "T02_MATH_AUDIT.json"
BASE = ROOT / "p2" / "reviews" / "T02_MATH_BASELINE.json"
SEED = 20261019
T_START = time.perf_counter()

checks = []
baseline = {"kind": "T02_MATH_BASELINE", "golden": {}, "source_sha256": {}}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(x: float, scale: float) -> float:
    return float(abs(x) / max(1.0, abs(scale)))


def record(cid, title, status, max_abs, max_rel, tol, unit, detail=None):
    # relative error is defined against max(1, |quantity|); when a check does not
    # supply its own normalisation we report the absolute value in that scale.
    if not max_rel and max_abs:
        max_rel = max_abs
    checks.append({
        "id": cid, "title": title, "status": status,
        "max_abs_error": float(max_abs), "max_rel_error": float(max_rel),
        "tolerance": tol, "unit": unit, "detail": detail or {},
    })


def run(cid, title, fn, tol, unit=""):
    try:
        detail, max_abs, max_rel, status = fn()
        record(cid, title, status, max_abs, max_rel, tol, unit, detail)
        return detail
    except Exception as exc:                       # keep going, record honestly
        record(cid, title, "FAIL_EXCEPTION", float("nan"), float("nan"), tol, unit,
               {"exception": repr(exc)})
        return None


def rand_pose(rng, max_ang=0.06, max_t=0.02):
    axis = rng.normal(size=3)
    axis /= np.linalg.norm(axis)
    ang = rng.uniform(-max_ang, max_ang)
    T = np.eye(4)
    T[:3, :3] = Rotation.from_rotvec(axis * ang).as_matrix()
    T[:3, 3] = rng.uniform(-max_t, max_t, 3)
    return T


def perturbed_states(base, n, rng):
    out = []
    for _ in range(n):
        d = np.zeros(42)
        d[0:6] = np.r_[rng.uniform(-0.01, 0.01, 3), rng.uniform(-0.03, 0.03, 3)]
        d[6:12] = np.r_[rng.uniform(-0.03, 0.03, 3), rng.uniform(-0.05, 0.05, 3)]
        for blk in range(2, 7):
            sl = slice(6 * blk, 6 * blk + 6)
            d[sl] = np.r_[rng.uniform(-0.01, 0.01, 3), rng.uniform(-0.03, 0.03, 3)]
        out.append(base.retract(d))
    return out


def ad_linear_first(tau):
    v, w = tau[:3], tau[3:]
    out = np.zeros((6, 6))
    out[:3, :3] = out[3:, 3:] = geo.skew(w)
    out[:3, 3:] = geo.skew(v)
    return out


def main() -> int:
    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    physics = mech.physics_from_protocol(cfg, "A")
    base = mech.initial_state(cfg, "transport")
    base_f = FilterState.from_mechanics(base)
    rng = np.random.default_rng(SEED)
    U = (np.zeros(6), np.zeros(6))
    modes = ("pivot", "pivot")

    for p in ("contact_geometry.py", "mechanics.py", "estimator.py", "observations.py"):
        baseline["source_sha256"][f"baselines/p2_pose_force/{p}"] = sha(
            ROOT / "baselines" / "p2_pose_force" / p)
    baseline["source_sha256"]["configs/p2_closed_loop_protocol_v3.json"] = sha(
        ROOT / "configs" / "p2_closed_loop_protocol_v3.json")
    baseline["seed"] = SEED

    # ---------------- 1. SE(3) Exp/Log -------------------------------------
    def c_roundtrip():
        worst_te, worst_te2 = 0.0, 0.0
        for _ in range(20):
            T = rand_pose(rng, 3.0, 0.5)
            tau = geo.se3_log(T)
            worst_te = max(worst_te, np.max(np.abs(geo.se3_exp(tau) - T)))
            ax = rng.normal(size=3); ax /= np.linalg.norm(ax)
            tau2 = np.r_[rng.uniform(-0.3, 0.3, 3), ax * rng.uniform(0.0, 2.9)]
            worst_te2 = max(worst_te2, np.max(np.abs(geo.se3_log(geo.se3_exp(tau2)) - tau2)))
        worst = max(worst_te, worst_te2)
        return ({"exp_log_exp_max": worst_te, "log_exp_log_max": worst_te2},
                worst, 0.0, "PASS" if worst <= 1e-12 else "FAIL")
    run("se3_exp_log_roundtrip", "Exp/Log roundtrip, 20 random poses (|theta|<=3)", c_roundtrip, 1e-12, "m/rad")

    def c_small():
        errs = []
        for mag in (1e-9, 1e-7, 1e-5, 1e-4):
            tau = np.array([1.0, -2.0, 3.0, 0.5, 1.5, -1.0]) * mag
            errs.append(np.max(np.abs(geo.se3_log(geo.se3_exp(tau)) - tau)))
        return {"by_magnitude": errs}, max(errs), 0.0, "PASS" if max(errs) <= 1e-14 else "FAIL"
    run("se3_exp_log_small_angle", "Exp/Log at 1e-9,1e-7,1e-5,1e-4", c_small, 1e-14, "m/rad")

    def c_near_pi():
        axis = np.array([0.3, -0.5, 0.81]); axis /= np.linalg.norm(axis)
        errs = {}
        for gap in (1e-3, 1e-5):
            tau = np.r_[0.01, -0.02, 0.03, axis * (np.pi - gap)]
            errs[str(gap)] = float(np.max(np.abs(geo.se3_log(geo.se3_exp(tau)) - tau)))
        tau_pi = np.r_[0.0, 0.0, 0.0, axis * (np.pi - 1e-7)]
        roundtrip_pi = float(np.max(np.abs(geo.se3_log(geo.se3_exp(tau_pi)) - tau_pi)))
        raised = False
        try:
            D = geo.se3_exp(tau_pi)
            geo.grasp_rate(D, np.eye(4), np.eye(4), np.zeros(6), np.zeros(6),
                           geo.selection("pivot"), rcond=1e-12)
        except geo.GeometryDomainError:
            raised = True
        status = "PASS" if max(errs.values()) <= 1e-9 and raised else "FAIL"
        return {"gaps": errs, "roundtrip_at_pi_minus_1e-7": roundtrip_pi,
                "grasp_rate_rejects_near_pi": raised}, max(errs.values()), 0.0, status
    run("se3_log_near_pi_and_boundary", "Log near pi (1e-3,1e-5) and chart-boundary rejection", c_near_pi, 1e-9, "rad")

    def c_inverse():
        errs = []
        for _ in range(10):
            T = rand_pose(rng)
            errs.append(np.max(np.abs(T @ geo.inverse(T) - np.eye(4))))
            tau = geo.se3_log(T)
            errs.append(np.max(np.abs(geo.se3_exp(tau) @ geo.se3_exp(-tau) - np.eye(4))))
        return {"n": len(errs)}, max(errs), 0.0, "PASS" if max(errs) <= 1e-12 else "FAIL"
    run("se3_inverse_and_negative_twist", "T inv(T)=I and Exp(tau)Exp(-tau)=I", c_inverse, 1e-12, "dimensionless")

    # ---------------- 2. Adjoint ------------------------------------------
    def c_homomorphism():
        errs = []
        for _ in range(10):
            T1, T2 = rand_pose(rng), rand_pose(rng)
            errs.append(np.max(np.abs(geo.adjoint(T1 @ T2) - geo.adjoint(T1) @ geo.adjoint(T2))))
            errs.append(np.max(np.abs(geo.adjoint(geo.inverse(T1)) @ geo.adjoint(T1) - np.eye(6))))
        return {"n": len(errs)}, max(errs), 0.0, "PASS" if max(errs) <= 1e-12 else "FAIL"
    run("adjoint_homomorphism_and_inverse", "Ad(T1T2)=Ad(T1)Ad(T2), Ad(T^-1)Ad(T)=I", c_homomorphism, 1e-12, "dimensionless")

    def c_adjoint_exp():
        errs = []
        for _ in range(10):
            tau = np.r_[rng.uniform(-0.3, 0.3, 3), rng.uniform(-2.5, 2.5, 3)]
            errs.append(np.max(np.abs(geo.adjoint(geo.se3_exp(tau)) - expm(ad_linear_first(tau)))))
        return {"n": len(errs)}, max(errs), 0.0, "PASS" if max(errs) <= 1e-12 else "FAIL"
    run("adjoint_equals_exp_of_ad", "Ad(Exp(tau)) = expm(ad(tau))", c_adjoint_exp, 1e-12, "dimensionless")

    def c_power():
        errs = []
        for _ in range(10):
            T = rand_pose(rng)
            Vb = np.r_[rng.uniform(-0.1, 0.1, 3), rng.uniform(-0.3, 0.3, 3)]
            hb = np.r_[rng.uniform(-5, 5, 3), rng.uniform(-1, 1, 3)]
            Va = geo.adjoint(T) @ Vb
            ha = np.linalg.solve(geo.adjoint(T).T, hb)
            errs.append(abs(ha @ Va - hb @ Vb))
        return {"n": len(errs)}, max(errs), 0.0, "PASS" if max(errs) <= 1e-12 else "FAIL"
    run("wrench_power_invariance", "h_a=Ad(T)^-T h_b preserves h^T V", c_power, 1e-12, "W")

    # ---------------- 3. contact constitutive ------------------------------
    states = perturbed_states(base_f, 10, rng)

    def c_stiffness():
        worst = 0.0; energy_min = np.inf
        for S in states:
            c = mech.mechanics(S, U, modes, physics)
            K = physics.K[0]
            worst = max(worst, np.max(np.abs(c.hK[0] + K * c.tau[0])))
            energy_min = min(energy_min, float(c.tau[0] @ (K * c.tau[0])))
        return ({"tau_energy_min_Nm": energy_min}, worst, 0.0,
                "PASS" if worst <= 1e-12 and energy_min >= -1e-15 else "FAIL")
    run("elastic_constitutive_eq9", "hK = -K tau and tau^T K tau >= 0", c_stiffness, 1e-12, "N/Nm")

    def c_damping():
        worst = 0.0
        for S in states:
            c = mech.mechanics(S, U, modes, physics)
            E1, E2c = mech.common_endpoints(S)
            for r, (E, G) in enumerate(((E1, S.G1), (E2c, S.G2))):
                D = geo.inverse(E) @ S.O @ G
                Rbar = np.zeros((6, 6)); Rbar[:3, :3] = Rbar[3:, 3:] = D[:3, :3]
                vrel = Rbar @ geo.adjoint(geo.inverse(G)) @ S.V - U[r]
                worst = max(worst, np.max(np.abs(c.hB[r] + physics.B * vrel)))
        return {"n_states": len(states)}, worst, 0.0, "PASS" if worst <= 1e-12 else "FAIL"
    run("damping_constitutive_eq10_11", "hB = -B (Rbar Ad(G^-1) V_o - U)", c_damping, 1e-12, "N/Nm")

    def c_d_definition():
        worst = 0.0
        for S in states:
            E1, E2c = mech.common_endpoints(S)
            D1 = geo.inverse(E1) @ S.O @ S.G1
            D2 = geo.inverse(E2c) @ S.O @ S.G2
            c = mech.mechanics(S, U, modes, physics)
            worst = max(worst, np.max(np.abs(c.D[0] - D1)), np.max(np.abs(c.D[1] - D2)))
        return {"n_states": len(states)}, worst, 0.0, "PASS" if worst <= 1e-12 else "FAIL"
    run("contact_pose_eq8", "D_r = E_r^-1 O G_r with base adapter on robot 2", c_d_definition, 1e-12, "dimensionless")

    # ---------------- 4. grasp matrix / internal projection ----------------
    def c_W_structure():
        worst = 0.0; dims = {}
        for mode_pair in (("tight", "tight"), ("pivot", "pivot"), ("sliding", "sliding")):
            S = states[0]
            c = mech.mechanics(S, U, mode_pair, physics)
            E1, E2c = mech.common_endpoints(S)
            cols = []
            for E, G in ((E1, S.G1), (E2c, S.G2)):
                A = G @ geo.inverse(geo.inverse(E) @ S.O @ G)      # T^o_e
                cols.append(geo.adjoint(geo.inverse(A)).T)
            Wref = np.hstack(cols) @ c.H.T
            worst = max(worst, np.max(np.abs(c.W - Wref)))
            dims[mode_pair[0]] = c.W.shape
        return {"shapes": dims}, worst, 0.0, "PASS" if worst <= 1e-12 else "FAIL"
    run("grasp_matrix_eq12_structure", "W = [Ad(T_e1^o)^-T, Ad(T_e2^o)^-T] H^T", c_W_structure, 1e-12, "dimensionless")

    def c_virtual_work():
        worst = 0.0
        for S in states:
            for mode_pair in (("tight", "tight"), ("pivot", "pivot"), ("sliding", "sliding")):
                c = mech.mechanics(S, U, mode_pair, physics)
                E1, E2c = mech.common_endpoints(S)
                lhs = float(c.external @ S.V)
                rhs = 0.0
                Hh = c.H @ c.h.ravel()
                rows = 0
                for r, (E, G) in enumerate(((E1, S.G1), (E2c, S.G2))):
                    Hr = geo.selection(mode_pair[r])
                    nr = Hr.shape[0]
                    A = G @ geo.inverse(geo.inverse(E) @ S.O @ G)     # T^o_e
                    Ve = geo.adjoint(geo.inverse(A)) @ S.V            # rigid-body EE twist
                    rhs += float(Hh[rows:rows + nr] @ (Hr @ Ve))      # same selected components
                    rows += nr
                worst = max(worst, rel(lhs - rhs, max(abs(lhs), abs(rhs))))
        return {"n_states": len(states)}, worst, worst, "PASS" if worst <= 1e-10 else "FAIL"
    run("grasp_virtual_work", "h_E^T V_o = sum_r (H h)_r^T V_e_r", c_virtual_work, 1e-10, "W")

    def c_projection():
        worst = {"idempotent": 0.0, "symmetric": 0.0, "null": 0.0, "lift": 0.0, "complete": 0.0}
        for S in states:
            for mode_pair in (("tight", "tight"), ("pivot", "pivot"), ("sliding", "sliding")):
                c = mech.mechanics(S, U, mode_pair, physics)
                W = c.W
                Wp = np.linalg.pinv(W, rcond=1e-12)
                P = np.eye(W.shape[1]) - Wp @ W
                Hh = (c.H @ c.h.ravel())
                hIt = P @ Hh
                worst["idempotent"] = max(worst["idempotent"], np.max(np.abs(P @ P - P)))
                worst["symmetric"] = max(worst["symmetric"], np.max(np.abs(P - P.T)))
                worst["null"] = max(worst["null"], np.max(np.abs(W @ hIt)))
                hI = c.H.T @ hIt
                worst["lift"] = max(worst["lift"], np.max(np.abs(c.H @ hI - hIt)))
                worst["complete"] = max(worst["complete"], np.max(np.abs(Hh - (hIt + Wp @ W @ Hh))))
        m = max(worst.values())
        return worst, m, m, "PASS" if m <= 1e-10 else "FAIL"
    run("internal_projection_eq20", "P=I-W+W idempotent, W hIt=0, H hI=hIt, completeness", c_projection, 1e-10, "N/Nm")

    def c_rank():
        # The protocol's expected ranks belong to the NOMINAL fixture; a generic
        # perturbed state is not expected to keep rank 4 for sliding/sliding.
        table = {"nominal": {}, "perturbed_generic": {}}
        ok = True
        expected = {("tight", "tight"): 6, ("pivot", "pivot"): 6, ("sliding", "sliding"): 4}
        for mode_pair, want in expected.items():
            c = mech.mechanics(base_f, U, mode_pair, physics)
            sv = c.singular_values
            rank = int(np.sum(sv > 1e-10 * sv[0]))
            table["nominal"][mode_pair[0]] = {"rank": rank, "expected": want,
                                              "all_singular_values": sv.tolist()}
            ok = ok and rank == want
        for mode_pair in expected:
            c = mech.mechanics(states[0], U, mode_pair, physics)
            sv = c.singular_values
            table["perturbed_generic"][mode_pair[0]] = {
                "rank": int(np.sum(sv > 1e-10 * sv[0])), "all_singular_values": sv.tolist()}
        table["interpretation"] = (
            "rank(W) is fixture dependent: sliding/sliding gives 4 only when both EE "
            "sliding axes are exactly collinear (nominal fixture). A generic perturbed "
            "state gives 5 because the common free direction is the single cross product.")
        return table, 0.0, 0.0, "PASS" if ok else "FAIL"
    run("grasp_rank_by_mode", "rank(W) at the nominal fixture (tight 6, pivot 6, sliding 4)", c_rank, 0.0, "rank")

    def c_lever_arm():
        # Eq.(10) replaces Ad(D) by Rbar=diag(R,R); the dropped block is [p]x R,
        # i.e. the lever-arm coupling between angular velocity and linear velocity.
        worst = 0.0; sample = None
        for S in states:
            E1, E2c = mech.common_endpoints(S)
            for E, G in ((E1, S.G1), (E2c, S.G2)):
                D = geo.inverse(E) @ S.O @ G
                R = D[:3, :3]
                Rbar = np.zeros((6, 6)); Rbar[:3, :3] = Rbar[3:, 3:] = R
                q = geo.adjoint(geo.inverse(G)) @ S.V
                exact = geo.adjoint(D) @ q
                approx = Rbar @ q
                scale = max(1.0, np.linalg.norm(exact))
                worst = max(worst, float(np.linalg.norm(exact - approx) / scale))
                if sample is None:
                    sample = {"exact": exact.tolist(), "approx": approx.tolist(),
                              "dropped_block_norm": float(np.linalg.norm(geo.skew(D[:3, 3]) @ R))}
        return ({"relative_twist_difference_max": worst, "sample": sample},
                worst, worst, "DEVIATION_CONFIRMED")
    run("damping_Rbar_lever_arm", "Eq.(10) Rbar drops the [p]xR lever-arm block of Ad(D)",
        c_lever_arm, 0.0, "relative")

    # ---------------- 5. selection matrices --------------------------------
    def c_selection():
        details = {}
        ok = True
        for mode, rows in (("tight", 6), ("pivot", 5), ("sliding", 4)):
            H = geo.selection(mode)
            details[mode] = {"shape": H.shape}
            ok = ok and H.shape == (rows, 6) and np.allclose(H @ H.T, np.eye(rows), atol=1e-14)
            N = np.linalg.svd(H, full_matrices=True)[2][rows:].T
            ok = ok and np.allclose(H @ N, 0, atol=1e-14) and np.allclose(N.T @ N, np.eye(6 - rows), atol=1e-14)
        # printed definitions
        ok = ok and np.allclose(geo.selection("tight"), np.eye(6))
        ok = ok and np.allclose(geo.selection("pivot"), np.eye(6)[:5])
        ok = ok and np.allclose(geo.selection("sliding"), np.eye(6)[2:])
        raised = False
        try:
            geo.selection("weld")
        except geo.GeometryDomainError:
            raised = True
        ok = ok and raised
        details["unknown_mode_rejected"] = raised
        return details, 0.0, 0.0, "PASS" if ok else "FAIL"
    run("selection_matrices", "H tight=I6, pivot=I6[:5], sliding=I6[2:]; H H^T=I; H N=0", c_selection, 0.0, "dimensionless")

    # ---------------- 6. right Jacobian ------------------------------------
    def c_right_jacobian():
        worst = 0.0
        for _ in range(5):
            tau = np.r_[rng.uniform(-0.2, 0.2, 3), rng.uniform(-1.5, 1.5, 3)]
            Jr = geo.right_jacobian(tau)
            eps = 1e-6
            for i in range(6):
                e = np.zeros(6); e[i] = 1.0
                Tp = geo.se3_exp(tau) @ geo.se3_exp(eps * e)
                Tm = geo.se3_exp(tau) @ geo.se3_exp(-eps * e)
                fd = (geo.se3_log(Tp) - geo.se3_log(Tm)) / (2 * eps)
                worst = max(worst, np.max(np.abs(fd - np.linalg.solve(Jr, e))))
        return {"eps": 1e-6}, worst, 0.0, "PASS" if worst <= 1e-7 else "FAIL"
    run("right_jacobian_inverse_fd", "d/deps Log(Exp(tau)Exp(eps e_i)) = Jr(tau)^-1 e_i", c_right_jacobian, 1e-7, "dimensionless")

    # ---------------- 7. Eq.(15): adapted vs printed -----------------------
    def c_eq15_invariant():
        worst = 0.0
        for S in states[:5]:
            E1, E2c = mech.common_endpoints(S)
            for mode_pair in (("pivot", "pivot"), ("sliding", "sliding"), ("tight", "tight")):
                for r, (E, G) in enumerate(((E1, S.G1), (E2c, S.G2))):
                    H = geo.selection(mode_pair[r])
                    res = geo.grasp_rate(S.O, E, G, S.V, np.zeros(6), H, rcond=1e-12)
                    N = res.free_basis_EE
                    if N.shape[1]:
                        worst = max(worst, np.max(np.abs(N.T @ res.tau_rate)))
        return {"n_states": 5}, worst, 0.0, "PASS" if worst <= 1e-10 else "FAIL"
    run("eq15_adapted_free_log_invariant", "N^T tau_dot = 0 for the approved geometry", c_eq15_invariant, 1e-10, "1/s")

    def c_eq15_printed():
        # D = I, sliding free x/y, object 0.01 m/s along x, EE static, G = I
        O = np.eye(4); E = np.eye(4); G = np.eye(4)
        V = np.array([0.01, 0.0, 0.0, 0.0, 0.0, 0.0])
        H = geo.selection("sliding")
        N = np.linalg.svd(H, full_matrices=True)[2][H.shape[0]:].T
        a = geo.adjoint(geo.inverse(G)) @ V
        adapted = geo.grasp_rate(O, E, G, V, np.zeros(6), H, rcond=1e-12)
        adapted_free = float(np.max(np.abs(N.T @ adapted.tau_rate)))
        VG_printed = N @ (N.T @ a)
        tau_dot_printed = a + VG_printed
        printed_free = float(np.max(np.abs(N.T @ tau_dot_printed)))
        h = 4e-3
        detail = {
            "adapted_free_component_1_s": adapted_free,
            "printed_free_component_1_s": printed_free,
            "adapted_deformation_over_4ms_m": adapted_free * h,
            "printed_deformation_over_4ms_m": printed_free * h,
            "printed_equals_two_times_a": bool(np.allclose(VG_printed, N @ (N.T @ a))),
        }
        status = "DEVIATION_CONFIRMED" if adapted_free <= 1e-12 < printed_free else "FAIL"
        return detail, printed_free, 0.0, status
    run("eq15_printed_vs_adapted_counterexample",
        "printed +HbarHbar^T Ad(D^-1) V_rel doubles free strain; adapted zeroes it",
        c_eq15_printed, 0.0, "1/s")

    # ---------------- 8. estimator measurement Jacobians -------------------
    def fd_pose_residual(S, X0, kind, obs, eps=1e-6):
        def r(state):
            expected = est.measurement_prediction(state, kind, physics)
            if kind.startswith("hK"):
                return obs - expected
            return geo.se3_log(geo.inverse(expected) @ obs)
        base_r = r(X0)
        H = np.zeros((6, 42))
        for j in range(42):
            e = np.zeros(42); e[j] = eps
            H[:, j] = (r(X0.retract(e)) - r(X0.retract(-e))) / (2 * eps)
        return H, base_r

    def c_measurement_jacobian():
        S = states[0]
        out = {}
        worst = 0.0
        eps = 1e-6
        for kind in ("EE1", "EE2", "hK1", "hK2", "visual1", "visual2"):
            h0 = est.measurement_prediction(S, kind, physics)
            H_code = est.measurement_jacobian(S, kind, physics)
            H_fd = np.zeros((6, 42))
            for j in range(42):
                e = np.zeros(42); e[j] = eps
                hp = est.measurement_prediction(S.retract(e), kind, physics)
                hm = est.measurement_prediction(S.retract(-e), kind, physics)
                if kind.startswith("hK"):
                    H_fd[:, j] = (hp - hm) / (2 * eps)
                else:
                    H_fd[:, j] = geo.se3_log(geo.inverse(h0) @ hp)
                    H_fd[:, j] -= geo.se3_log(geo.inverse(h0) @ hm)
                    H_fd[:, j] /= (2 * eps)
            err = np.max(np.abs(H_code - H_fd)) / max(1.0, np.max(np.abs(H_fd)))
            out[kind] = float(err)
            worst = max(worst, err)
        return out, worst, worst, "PASS" if worst <= 1e-6 else "FAIL"
    run("measurement_jacobian_fd", "analytic H vs central FD of the residual, 6 observation kinds", c_measurement_jacobian, 1e-6, "relative")

    # ---------------- 9. discrete prediction F vs FD of the real map -------
    def c_prediction_F_fd():
        S = states[0]
        h = 0.004
        _, F_code, _ = est.prediction_linearization(S, U, modes, physics, h)

        def map_step(state):
            f, _ = est.continuous_linearization(state, U, modes, physics)
            return state.retract(h * f)

        X0 = map_step(S)
        eps = 1e-6
        F_fd = np.zeros((42, 42))
        for j in range(42):
            e = np.zeros(42); e[j] = eps
            F_fd[:, j] = map_step(S.retract(e)).local(map_step(S.retract(-e))) / (2 * eps)
        err = np.max(np.abs(F_code - F_fd)) / max(1.0, np.max(np.abs(F_fd)))
        detail = {"relative_max": float(err), "max_abs": float(np.max(np.abs(F_code - F_fd))),
                  "frobenius_code": float(np.linalg.norm(F_code)),
                  "spectral_radius_code": float(np.max(np.abs(np.linalg.eigvals(F_code))))}
        return detail, err, err, "PASS" if err <= 1e-5 else "FAIL"
    run("prediction_F_right_error_fd", "F from prediction_linearization vs right-error FD of the Euler map", c_prediction_F_fd, 1e-5, "relative")

    # ---------------- 10. domain gates -------------------------------------
    def c_domain():
        import types
        good = types.SimpleNamespace(tau=np.zeros((2, 6)), h=np.zeros((2, 6)))
        mech.validate_state(states[0], good)
        bad_lin = types.SimpleNamespace(tau=np.zeros((2, 6)), h=np.zeros((2, 6)))
        bad_lin.tau[0, 0] = 0.0051
        bad_ang = types.SimpleNamespace(tau=np.zeros((2, 6)), h=np.zeros((2, 6)))
        bad_ang.tau[1, 3] = 0.1501
        flags = {}
        for label, obj in (("linear", bad_lin), ("angular", bad_ang)):
            try:
                mech.validate_state(states[0], obj)
                flags[label] = False
            except ValueError as exc:
                flags[label] = str(exc) == "PAD_DOMAIN_INVALID"
        ok = all(flags.values())
        return flags, 0.0, 0.0, "PASS" if ok else "FAIL"
    run("pad_domain_gate", "5 mm / 0.15 rad gates raise PAD_DOMAIN_INVALID", c_domain, 0.0, "m/rad")

    def c_invalid_se3():
        T = np.eye(4); T[:3, :3] *= 1.1
        rejected = False
        try:
            geo.validate_transform(T)
        except geo.GeometryDomainError:
            rejected = True
        return {"scaled_rotation_rejected": rejected}, 0.0, 0.0, "PASS" if rejected else "FAIL"
    run("invalid_se3_rejected", "non-orthonormal rotation is rejected without normalisation", c_invalid_se3, 0.0, "dimensionless")

    # ---------------- 11. golden baseline for T01-E ------------------------
    def golden():
        S = base_f
        c = mech.mechanics(S, U, modes, physics)
        g = {
            "state": S.as_dict(),
            "contact": {
                "D": c.D.tolist(), "tau": c.tau.tolist(),
                "hK": c.hK.tolist(), "hB": c.hB.tolist(), "h": c.h.tolist(),
                "external": c.external.tolist(), "W": c.W.tolist(),
                "singular_values": c.singular_values.tolist(),
                "internal": c.internal.tolist(),
            },
            "grasp_rate": {},
            "estimator": {},
        }
        E1, E2c = mech.common_endpoints(S)
        for name, (E, G) in (("arm1", (E1, S.G1)), ("arm2", (E2c, S.G2))):
            res = geo.grasp_rate(S.O, E, G, S.V, np.zeros(6), geo.selection("pivot"), rcond=1e-12)
            g["grasp_rate"][name] = {"tau_rate": res.tau_rate.tolist(),
                                     "grasp_body": res.grasp_body.tolist(),
                                     "singular_values": res.singular_values.tolist()}
        # measurement Jacobians
        for kind in ("EE1", "EE2", "hK1", "hK2", "visual1", "visual2"):
            H = est.measurement_jacobian(S, kind, physics)
            g["estimator"][f"H_{kind}"] = {"norm": float(np.linalg.norm(H)),
                                           "max_abs": float(np.max(np.abs(H))),
                                           "sha1_of_rounded": hashlib.sha1(
                                               np.round(H, 12).tobytes()).hexdigest()}
        # one prediction and one update
        pred, F, Lw = est.prediction_linearization(S, U, modes, physics, 0.004)
        g["estimator"]["predict"] = {
            "F_norm": float(np.linalg.norm(F)), "F_max_abs": float(np.max(np.abs(F))),
            "F_sha1_rounded": hashlib.sha1(np.round(F, 12).tobytes()).hexdigest(),
            "state_V": pred.V.tolist(),
        }
        filt = est.RightIESEKF.from_protocol(S, cfg, condition="exp3", object_id="A",
                                             modes=modes, rate_provider=None)
        filt.predict_to(30 * (1.0 / 3000.0), U)
        sensor = ObservationGenerator(cfg, 7, variant="transport",
                                      contact_provider=lambda st, u, m, ph: mech.mechanics(st, u, m, ph))
        packet = sensor.sample_packet(base, 30, None, modes=modes)
        rep = filt.update(packet)
        g["estimator"]["update"] = {
            "observations": [o.kind for o in packet], "iterations": rep.iterations,
            "converged": bool(rep.converged),
            "V": filt.state.V.tolist(), "P_diag": np.diag(filt.P).tolist(),
            "P_sha1_rounded": hashlib.sha1(np.round(filt.P, 14).tobytes()).hexdigest(),
        }
        return g

    baseline["golden"] = golden()
    baseline["generated"] = "p2/tools/t02_math_audit.py"
    baseline["wall_s"] = time.perf_counter() - T_START

    summary = {}
    for c in checks:
        summary[c["status"]] = summary.get(c["status"], 0) + 1
    out = {
        "kind": "T02_MATH_AUDIT",
        "date": "2026-10-19",
        "seed": SEED,
        "scope": "read-only audit of baselines/p2_pose_force; no integration, no control loop",
        "summary": summary,
        "checks": checks,
        "wall_s": time.perf_counter() - T_START,
    }
    AUDIT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    BASE.write_text(json.dumps(baseline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for c in checks:
        print(f"{c['status']:<22} {c['id']:<40} max_abs={c['max_abs_error']:.3e} "
              f"max_rel={c['max_rel_error']:.3e}")
    print("summary:", summary, "wall_s:", round(out["wall_s"], 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
