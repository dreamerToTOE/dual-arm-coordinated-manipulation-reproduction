#!/usr/bin/env python3
"""T03: independent plant (Eq.13-16) numerical audit.

Two stages, each with its own hard wall cap:
  S  continuous/discrete spectra + native one-step map FD + C legacy rho probe
  P  genuine nonequilibrium transients, step-size refinement and convergence

No estimator, no control, no closed loop. Native plant is used as-is; nothing is
tuned. Deterministic fixtures are declared in reviews/T03_PRE.md.

Outputs
  p2/reviews/T03_SPECTRUM.json
  p2/reviews/T03_PERTURBATION.json
  p2/runs/<run_id>/trajectories/*.npz + manifest.json
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from baselines.p2_pose_force import contact_geometry as geo          # noqa: E402
from baselines.p2_pose_force import mechanics as mech               # noqa: E402
from baselines.p2_pose_force import estimator as est                # noqa: E402
from baselines.p2_pose_force.observations import FilterState         # noqa: E402
from baselines.p2_pose_force.native_model import NativeModel, build_native  # noqa: E402

BLOCKS = ("O", "V", "E1", "E2", "C", "G1", "G2")
CAPS = {"spectrum": 120.0, "perturb": 240.0}
DT0 = 1.0 / 3000.0
U0 = (np.zeros(6), np.zeros(6))
MODES = ("pivot", "pivot")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_objects(cfg):
    """Nominal states and physics for A, B1, B2, C. B1/B2 inertia and grasps are
    ADAPTATION (paper gives mass and cuboid size only)."""
    g = np.array(cfg["model"]["gravity_m_s2"], float)
    par = cfg["original_parameters"]
    K = np.array(par["K_nominal"], float)
    B = np.array(par["B_nominal"], float)
    Ba = np.array(par["B_air"], float)
    C = mech.transform(cfg["model"]["true_C_b1_to_b2"]["translation_m"],
                       np.array([[np.cos(np.pi), -np.sin(np.pi), 0],
                                 [np.sin(np.pi), np.cos(np.pi), 0], [0, 0, 1]]))

    objects = {}

    # A: protocol fixture
    phA = mech.physics_from_protocol(cfg, "A")
    stA = mech.initial_state(cfg, "transport")
    objects["A"] = {"physics": phA, "state": stA, "source": "PAPER mass/dims; protocol grasps (ADAPTATION)"}

    # C: legacy vertical fixture used by the 2026-10-14 C audit
    phC = mech.physics_from_protocol(cfg, "C")
    stC = mech.initial_state(cfg, "sliding")
    objects["C"] = {"physics": phC, "state": stC,
                    "source": "PAPER mass/dims; conditional_sliding grasps (ADAPTATION)"}

    # B1/B2: paper mass and cuboid size, everything else ADAPTATION
    m, (dx, dy, dz) = 0.280, (0.075, 0.140, 0.040)
    inertia = m / 12 * np.array([dy * dy + dz * dz, dx * dx + dz * dz, dx * dx + dy * dy])
    phB = mech.Physics(m, inertia, (K.copy(), K.copy()), B.copy(), Ba.copy(), g)

    def grasp_b(sign):
        ex = np.array([0.0, 0.0, 1.0])
        ey = np.array([0.0, -sign, 0.0])
        ez = np.array([sign, 0.0, 0.0])
        T = np.eye(4)
        T[:3, :3] = np.column_stack([ex, ey, ez])
        T[:3, 3] = [sign * dx / 2, 0.0, 0.0]
        return T

    G1, G2 = grasp_b(+1), grasp_b(-1)
    O = mech.transform(cfg["model"]["initial_nominal_O_A"]["translation_m"])
    stB = mech.State(O, np.zeros(6), O @ G1, C @ O @ G2, C, G1, G2)
    for name in ("B1", "B2"):
        objects[name] = {"physics": phB, "state": stB,
                         "source": "PAPER mass/dims; inertia + grasp geometry ADAPTATION"}
    return objects


def make_point(state, kind, physics=None):
    """Declared operating points (see T03_PRE table)."""
    d = np.zeros(42)
    if kind == "nominal":
        return state, {"kind": "nominal", "pose_offset_m": 0.0, "pose_offset_rad": 0.0,
                       "velocity": np.zeros(6).tolist()}
    if kind == "EQ":
        raise ValueError("EQ requires the numerical solver; see equilibrium_state")
    if kind == "P1":
        d[0:6] = [0.003, -0.002, 0.001, 0.010, -0.008, 0.005]      # ~3 mm, ~0.014 rad
        d[6:12] = [0.02, -0.01, 0.005, 0.10, -0.05, 0.02]
    elif kind == "P2":
        d[0:6] = [0.0015, -0.0010, 0.0008, 0.008, -0.006, 0.004]   # preload ~1.5 mm, 10 mrad
        d[6:12] = [0.05, 0.02, -0.01, 0.25, 0.10, -0.05]
    else:
        raise ValueError(kind)
    return state.retract(d), {"kind": kind, "pose_offset_m": float(np.linalg.norm(d[:3])),
                              "pose_offset_rad": float(np.linalg.norm(d[3:6])),
                              "velocity": d[6:12].tolist()}


def equilibrium_state(native, state, physics, lo=-0.02, hi=0.02, tol=1e-12, maxit=60):
    """1-D bisection on the COM height so that the vertical acceleration vanishes."""
    def fz(dz):
        d = np.zeros(42); d[2] = dz
        f, _ = native.continuous_linearization(state.retract(d), U0, MODES, physics)
        return float(f[8]), state.retract(d)

    flo, _ = fz(lo)
    fhi, _ = fz(hi)
    if flo * fhi > 0:
        return None, {"found": False, "f_lo": flo, "f_hi": fhi}
    for _ in range(maxit):
        mid = 0.5 * (lo + hi)
        fm, candidate = fz(mid)
        if abs(fm) <= tol or (hi - lo) < 1e-12:
            f_full, _ = native.continuous_linearization(candidate, U0, MODES, physics)
            norm = float(np.linalg.norm(f_full))
            if norm > 1e-6:      # vertical balance alone is not a full equilibrium
                return None, {"found": False, "reason": "full_residual_not_zero",
                              "drop_m": mid, "fz": fm, "f_norm": norm}
            return candidate, {"found": True, "drop_m": mid, "fz": fm, "f_norm": norm}
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return None, {"found": False, "reason": "bisection_limit"}


def discrete_spectra(A, h):
    out = {}
    I = np.eye(A.shape[0])
    schemes = {
        "euler": I + h * A,
        "implicit_euler": np.linalg.solve(I - h * A, I),
        "trapezoid": np.linalg.solve(I - h * A / 2, I + h * A / 2),
        "matrix_exp": expm(h * A),
    }
    for n in (4, 8, 16):
        schemes[f"euler_substeps_{n}"] = np.linalg.matrix_power(I + h * A / n, n)
    for name, M in schemes.items():
        ev = np.linalg.eigvals(M)
        idx = int(np.argmax(np.abs(ev)))
        out[name] = {"rho": float(np.max(np.abs(ev))),
                     "argmax_real": float(ev[idx].real),
                     "argmax_imag": float(ev[idx].imag),
                     "stable": bool(np.max(np.abs(ev)) <= 1.0)}
    return out


def eigen_summary(A, top=8):
    w, V = np.linalg.eig(A)
    order = np.argsort(-np.abs(w))
    modes = []
    for i in order[:top]:
        col = np.abs(V[:, i])
        parts = {b: float(np.sum(col[6 * k:6 * k + 6])) for k, b in enumerate(BLOCKS)}
        dom = sorted(parts.items(), key=lambda kv: -kv[1])[:3]
        modes.append({"real": float(w[i].real), "imag": float(w[i].imag),
                      "modulus": float(abs(w[i])),
                      "dominant_blocks": [[b, round(v, 4)] for b, v in dom]})
    allmods = [{"real": float(x.real), "imag": float(x.imag), "modulus": float(abs(x))} for x in w]
    condV = float(np.linalg.cond(V))
    henrici = float(np.linalg.norm(A @ A.T - A.T @ A) / max(np.linalg.norm(A) ** 2, 1e-300))
    return {"all_eigenvalues": allmods, "top_modes": modes,
            "min_real_part": float(np.min(w.real)), "max_real_part": float(np.max(w.real)),
            "max_modulus": float(np.max(np.abs(w))),
            "eigenvector_condition": condV, "henrici_departure": henrici,
            "n_positive_real_gt_1e-6": int(np.sum(w.real > 1e-6)),
            "n_neutral_abs_real_lt_1e-6": int(np.sum(np.abs(w.real) <= 1e-6))}


def native_jacobian(native, state, physics, dt, eps=1e-6):
    base, _ = native.advance(state, U0, MODES, physics, dt, 1)
    J = np.zeros((42, 42))
    failures = 0
    for j in range(42):
        e = np.zeros(42); e[j] = eps
        try:
            yp, _ = native.advance(state.retract(e), U0, MODES, physics, dt, 1)
            ym, _ = native.advance(state.retract(-e), U0, MODES, physics, dt, 1)
            J[:, j] = yp.local(ym) / (2 * eps)
        except Exception:
            failures += 1
            J[:, j] = np.nan
    return J, base, failures


def stage_spectrum(native, objects, out_dir, deadline):
    result = {"kind": "T03_SPECTRUM", "h": DT0, "objects": {}}
    for name, obj in objects.items():
        if time.perf_counter() > deadline:
            result.setdefault("budget_stop", []).append(name)
            break
        ph, st = obj["physics"], obj["state"]
        rec = {"source": obj["source"], "points": {}}
        eq_state, eq_meta = equilibrium_state(native, st, ph)
        rec["equilibrium"] = eq_meta
        points = [("nominal", st, {"kind": "nominal"}),
                  ("P1", *make_point(st, "P1", ph)),
                  ("P2", *make_point(st, "P2", ph))]
        if eq_state is not None:
            points.insert(1, ("EQ", eq_state, {"kind": "EQ", **eq_meta}))
        for kind, pt, meta in points:
            f_nat, A_nat = native.continuous_linearization(pt, U0, MODES, ph)
            _, A_py = est.continuous_linearization(FilterState.from_mechanics(pt), U0, MODES, ph)
            entry = {"meta": meta,
                     "f_norm": float(np.linalg.norm(f_nat)),
                     "A_native_vs_python_maxdiff": float(np.max(np.abs(A_nat - A_py))),
                     "continuous": eigen_summary(A_nat),
                     "discrete_theory": {},
                     "native_map": {}}
            for label, h in (("h", DT0), ("h_over_2", DT0 / 2), ("h_over_4", DT0 / 4),
                             ("1ms", 1e-3), ("4ms", 4e-3)):
                entry["discrete_theory"][label] = {"h_s": h, **discrete_spectra(A_nat, h)}
            for label, h in (("h", DT0), ("h_over_2", DT0 / 2), ("h_over_4", DT0 / 4)):
                J, base, fails = native_jacobian(native, pt, ph, h)
                ev = np.linalg.eigvals(J)
                entry["native_map"][label] = {
                    "h_s": h, "fd_eps": 1e-6, "failed_columns": fails,
                    "rho": float(np.max(np.abs(ev))),
                    "argmax_real": float(ev[int(np.argmax(np.abs(ev)))].real),
                    "argmax_imag": float(ev[int(np.argmax(np.abs(ev)))].imag),
                    "min_real_part": float(np.min(ev.real)),
                    "max_real_part": float(np.max(ev.real)),
                }
                np.savez_compressed(out_dir / f"J_{name}_{kind}_{label}.npz", J=J)
            entry.pop("_rows", None)
            rec["points"][kind] = entry
        result["objects"][name] = rec
    return result


def stage_c_legacy(native, objects, run_dir, deadline):
    """Resolve the historical 'C rho=2.73' by comparing THREE maps:
    native implicit midpoint (production), mechanics.midpoint_step (explicit
    predictor-corrector used by the old audit), and the theoretical matrices."""
    from baselines.p2_pose_force.mechanics import midpoint_step
    obj = objects["C"]
    ph, st = obj["physics"], obj["state"]
    out = {"fixture": "conditional_sliding vertical C, pivot/pivot, h=1/3000",
           "eps_sweep": {"native": {}, "python_midpoint_step": {}},
           "checks": {}}
    f, A = native.continuous_linearization(st, U0, MODES, ph)
    lam = np.linalg.eigvals(A)
    fastest = lam[int(np.argmin(lam.real))]
    z = DT0 * fastest
    out["checks"]["f_norm_at_point"] = float(np.linalg.norm(f))
    out["checks"]["continuous_min_real_part"] = float(np.min(lam.real))
    out["checks"]["continuous_max_real_part"] = float(np.max(lam.real))
    out["checks"]["fastest_mode"] = {"real": float(fastest.real), "imag": float(fastest.imag)}
    out["checks"]["z_h_lambda"] = {"real": float(z.real), "imag": float(z.imag)}
    out["checks"]["scalar_factors_at_z"] = {
        "euler_abs": float(abs(1 + z)),
        "explicit_midpoint_abs": float(abs(1 + z + z * z / 2)),
        "implicit_midpoint_abs": float(abs((1 + z / 2) / (1 - z / 2))),
        "exponential_abs": float(abs(np.exp(z))),
    }

    I = np.eye(42)
    for label, M in (("implicit_midpoint_theory",
                      np.linalg.solve(I - DT0 * A / 2, I + DT0 * A / 2)),
                     ("euler_theory", I + DT0 * A),
                     ("exponential_theory", expm(DT0 * A))):
        ev = np.linalg.eigvals(M)
        out["checks"][f"{label}_rho"] = float(np.max(np.abs(ev)))

    # python midpoint_step (explicit predictor-corrector) FD, with eps sweep
    base = midpoint_step(st, U0, MODES, ph, DT0)
    for eps in (1e-4, 1e-5, 1e-6, 1e-7):
        if time.perf_counter() > deadline:
            out["budget_stop"] = True
            break
        J = np.zeros((42, 42))
        for i in range(42):
            d = np.zeros(42); d[i] = eps
            p = midpoint_step(st.retract(d), U0, MODES, ph, DT0)
            m = midpoint_step(st.retract(-d), U0, MODES, ph, DT0)
            J[:, i] = (p.local(base) - m.local(base)) / (2 * eps)
        ev = np.linalg.eigvals(J)
        out["eps_sweep"]["python_midpoint_step"][str(eps)] = {
            "rho": float(np.max(np.abs(ev))),
            "argmax_real": float(ev[int(np.argmax(np.abs(ev)))].real)}
        if eps == 1e-6:
            np.savez_compressed(run_dir / "J_C_legacy_python_midpoint_step.npz", J=J)

    # native implicit map FD, with eps sweep
    for eps in (1e-4, 1e-5, 1e-6, 1e-7):
        if time.perf_counter() > deadline:
            out["budget_stop"] = True
            break
        J, _, fails = native_jacobian(native, st, ph, DT0, eps=eps)
        ev = np.linalg.eigvals(J)
        out["eps_sweep"]["native"][str(eps)] = {
            "rho": float(np.max(np.abs(ev))), "failed_columns": fails,
            "argmax_real": float(ev[int(np.argmax(np.abs(ev)))].real)}
        if eps == 1e-6:
            np.savez_compressed(run_dir / "J_C_legacy_native.npz", J=J, A=A)

    # is the point an equilibrium?
    residual = mech.equilibrium_residual(st, mech.mechanics(st, U0, MODES, ph), ph)
    out["checks"]["gravity_contact_residual_N_Nm"] = residual.tolist()
    out["checks"]["f_norm_nominal"] = float(np.linalg.norm(f))
    eq_state, eq_meta = equilibrium_state(native, st, ph)
    out["checks"]["numerical_equilibrium"] = eq_meta
    if eq_state is not None:
        f_eq, A_eq = native.continuous_linearization(eq_state, U0, MODES, ph)
        out["checks"]["f_norm_equilibrium"] = float(np.linalg.norm(f_eq))
        out["checks"]["equilibrium_min_real_part"] = float(np.min(np.linalg.eigvals(A_eq).real))

    _, diag = native.advance(st, U0, MODES, ph, DT0, 1)
    out["checks"]["native_newton"] = {k: diag.get(k) for k in
                                      ("completed_steps", "max_newton_iterations",
                                       "max_accepted_residual_component")}
    pt, _ = make_point(st, "P1", ph)
    traj = integrate(native, pt, ph, DT0, 0.2)
    out["checks"]["perturbed_growth"] = growth_summary(traj)
    return out


def energy(state, contact, ph):
    v, w = state.V[:3], state.V[3:]
    M = ph.M_diag
    ke = 0.5 * float(np.sum(M * state.V * state.V))
    pe = float(ph.mass * 9.81 * state.O[2, 3])
    tau = contact.tau.ravel()
    K = np.tile(np.asarray(ph.K[0]), 2) if len(ph.K) == 2 else np.asarray(ph.K[0])
    elastic = 0.5 * float(np.sum(K * tau * tau))
    return {"kinetic": ke, "gravity_potential": pe, "elastic": elastic,
            "total": ke + pe + elastic}


def integrate(native, state, ph, dt, duration, sample_dt=0.004):
    """Integrate with the native plant; sample at fixed physical times."""
    n = int(round(duration / dt))
    every = max(1, int(round(sample_dt / dt)))
    rows = []
    for k in range(n):
        state, diag = native.advance(state, U0, MODES, ph, dt, 1)
        if (k + 1) % every == 0:
            c = native.contact(state, U0, MODES, ph)
            e = energy(state, c, ph)
            rows.append({
                "t": (k + 1) * dt,
                "pos": state.O[:3, 3].tolist(),
                "quat": None,
                "V": state.V.tolist(),
                "tau_norm": float(np.linalg.norm(c.tau)),
                "hK_norm": float(np.linalg.norm(c.hK)),
                "internal_force_norm": float(np.linalg.norm(c.internal[:, :3])),
                "internal_moment_norm": float(np.linalg.norm(c.internal[:, 3:])),
                "energy": e,
                "newton_iterations": int(diag.get("max_newton_iterations", -1)),
                "residual": float(diag.get("max_accepted_residual_component", np.nan)),
            })
    return rows


def growth_summary(rows):
    if len(rows) < 2:
        return None
    def mag(r):
        return float(np.linalg.norm(r["V"]))
    v0, v1 = mag(rows[0]), mag(rows[-1])
    return {"v_norm_start": v0, "v_norm_end": v1,
            "ratio": (v1 / v0) if v0 > 0 else None,
            "tau_start": rows[0]["tau_norm"], "tau_end": rows[-1]["tau_norm"],
            "energy_start": rows[0]["energy"]["total"], "energy_end": rows[-1]["energy"]["total"]}


def stage_perturb(native, objects, run_dir, deadline):
    traj_dir = run_dir / "trajectories"
    traj_dir.mkdir(parents=True, exist_ok=True)
    result = {"kind": "T03_PERTURBATION", "duration_s": 0.30, "objects": {}}
    for name, obj in objects.items():
        if time.perf_counter() > deadline:
            result.setdefault("budget_stop", []).append(name)
            break
        ph, st = obj["physics"], obj["state"]
        rec = {"source": obj["source"], "points": {}}
        for kind in ("P1", "P2"):
            pt, meta = make_point(st, kind)
            entry = {"meta": meta, "runs": {}}
            ref = None
            for label, dt in (("h", DT0), ("h_over_2", DT0 / 2), ("h_over_4", DT0 / 4)):
                if time.perf_counter() > deadline:
                    entry.setdefault("budget_stop", []).append(label)
                    break
                t0 = time.perf_counter()
                rows = integrate(native, pt, ph, dt, 0.30)
                entry.setdefault("_rows", {})[label] = rows
                np.savez_compressed(traj_dir / f"{name}_{kind}_{label}.npz",
                                    t=np.array([r["t"] for r in rows]),
                                    pos=np.array([r["pos"] for r in rows]),
                                    V=np.array([r["V"] for r in rows]),
                                    tau=np.array([r["tau_norm"] for r in rows]),
                                    hK=np.array([r["hK_norm"] for r in rows]),
                                    internal_f=np.array([r["internal_force_norm"] for r in rows]),
                                    internal_m=np.array([r["internal_moment_norm"] for r in rows]),
                                    energy=np.array([[r["energy"][k] for k in
                                                      ("kinetic", "gravity_potential", "elastic", "total")]
                                                     for r in rows]),
                                    newton=np.array([r["newton_iterations"] for r in rows]),
                                    residual=np.array([r["residual"] for r in rows]))
                entry["runs"][label] = {
                    "dt_s": dt, "samples": len(rows), "wall_s": time.perf_counter() - t0,
                    "start": {"v_norm": float(np.linalg.norm(rows[0]["V"])),
                              "tau_norm": rows[0]["tau_norm"],
                              "energy_total": rows[0]["energy"]["total"]},
                    "end": {"v_norm": float(np.linalg.norm(rows[-1]["V"])),
                            "tau_norm": rows[-1]["tau_norm"],
                            "energy_total": rows[-1]["energy"]["total"]},
                    "max_newton": max(r["newton_iterations"] for r in rows),
                    "max_tau": max(r["tau_norm"] for r in rows),
                    "max_internal_force": max(r["internal_force_norm"] for r in rows),
                    "max_internal_moment": max(r["internal_moment_norm"] for r in rows),
                    "energy_drift": rows[-1]["energy"]["total"] - rows[0]["energy"]["total"],
                }
                if label == "h_over_4":
                    ref = rows
            # convergence vs h/4 at aligned sample indices
            if ref is not None:
                conv = {}
                for label in ("h", "h_over_2"):
                    rows = entry["_rows"][label]
                    n = min(len(rows), len(ref))
                    errs = {"pos_m": 0.0, "angle_rad": 0.0, "vel": 0.0}
                    for i in range(0, n, max(1, n // 10)):
                        dp = np.linalg.norm(np.array(rows[i]["pos"]) - np.array(ref[i]["pos"]))
                        dv = np.linalg.norm(np.array(rows[i]["V"]) - np.array(ref[i]["V"]))
                        errs["pos_m"] = max(errs["pos_m"], float(dp))
                        errs["vel"] = max(errs["vel"], float(dv))
                    conv[label] = errs
                if "h" in conv and "h_over_2" in conv:
                    ratio = (conv["h"]["pos_m"] / conv["h_over_2"]["pos_m"]
                             if conv["h_over_2"]["pos_m"] > 0 else None)
                    conv["order_pos"] = (float(np.log2(ratio)) if ratio and ratio > 0 else None)
                entry["convergence"] = conv
            entry.pop("_rows", None)
            rec["points"][kind] = entry
        result["objects"][name] = rec
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("spectrum", "perturb", "all"), default="all")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()

    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    objects = build_objects(cfg)
    native = NativeModel(build_native("/home/ubuntu2004/lmy/.p2_native_build_v3"))
    run_id = args.run_id or time.strftime("%Y%m%d_%H%M%S") + "_T03_PLANT"
    run_dir = ROOT / "p2" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {"kind": "T03_PLANT_RUN", "run_id": run_id, "command": sys.argv,
                "caps_s": CAPS,
                "source_sha256": {p: sha(ROOT / p) for p in (
                    "baselines/p2_pose_force/mechanics.py",
                    "baselines/p2_pose_force/contact_geometry.py",
                    "baselines/p2_pose_force/estimator.py",
                    "baselines/p2_pose_force/native_kernel.cpp",
                    "configs/p2_closed_loop_protocol_v3.json")}}

    if args.stage in ("spectrum", "all"):
        t0 = time.perf_counter()
        spec = stage_spectrum(native, objects, run_dir, t0 + CAPS["spectrum"])
        spec["c_legacy"] = stage_c_legacy(native, objects, run_dir, t0 + CAPS["spectrum"])
        spec["wall_s"] = time.perf_counter() - t0
        spec["cap_s"] = CAPS["spectrum"]
        (ROOT / "p2" / "reviews" / "T03_SPECTRUM.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"spectrum stage {spec['wall_s']:.2f}s")

    if args.stage in ("perturb", "all"):
        t0 = time.perf_counter()
        pert = stage_perturb(native, objects, run_dir, t0 + CAPS["perturb"])
        pert["wall_s"] = time.perf_counter() - t0
        pert["cap_s"] = CAPS["perturb"]
        (ROOT / "p2" / "reviews" / "T03_PERTURBATION.json").write_text(
            json.dumps(pert, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"perturb stage {pert['wall_s']:.2f}s")

    manifest["files_sha256"] = {p.name: sha(p) for p in sorted(run_dir.rglob("*")) if p.is_file()}
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("run dir", run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
