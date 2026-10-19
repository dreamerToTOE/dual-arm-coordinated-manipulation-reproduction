#!/usr/bin/env python3
"""T01-E pre-optimisation equivalence oracle.

Freezes, BEFORE any optimisation, a set of deterministic fixtures that stress the
paths O1/O2 will touch: nonzero velocity, nonzero elastic contact, all three H
modes, nonzero observation residual, small angle, near-pi, rank-boundary and
invalid inputs. For every numeric fixture it stores the COMPLETE inputs, states,
f/A/F/Lw/Qd, P before and after prediction, contact and grasp-rate arrays, all
six measurement Jacobians, and (for the update fixture) innovation, iteration
count and posterior covariance.

Outputs (in p2/reviews/t01e_baseline/):
  index.json    provenance, source hashes, environment, case table, array manifest
  cases.jsonl   one record per fixture (scalars, exceptions, iteration counts)
  arrays.npz    every matrix/vector keyed "<case>__<name>"

The suite is read-only and bounded: no plant time integration, no control loop.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from baselines.p2_pose_force import contact_geometry as geo          # noqa: E402
from baselines.p2_pose_force import mechanics as mech              # noqa: E402
from baselines.p2_pose_force import estimator as est                # noqa: E402
from baselines.p2_pose_force import observations as obs_mod          # noqa: E402
from baselines.p2_pose_force.observations import (                   # noqa: E402
    FilterState, Observation, ObservationGenerator)

OUT = ROOT / "p2" / "reviews" / "t01e_baseline"
SEED = 20261019
H = 0.004
T0 = time.perf_counter()


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def flatten_state(S: FilterState) -> np.ndarray:
    return np.concatenate([np.ravel(getattr(S, n)) for n in
                           ("O", "V", "E1", "E2", "C", "G1", "G2")])


def pose_delta(scale_t, scale_r, rng):
    d = np.zeros(42)
    d[0:6] = np.r_[rng.uniform(-scale_t, scale_t, 3), rng.uniform(-scale_r, scale_r, 3)]
    for blk in range(2, 7):
        sl = slice(6 * blk, 6 * blk + 6)
        d[sl] = np.r_[rng.uniform(-scale_t, scale_t, 3), rng.uniform(-scale_r, scale_r, 3)]
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default=str(OUT))
    args = ap.parse_args()
    out_dir = Path(args.output_dir)
    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    physics = mech.physics_from_protocol(cfg, "A")
    base = mech.initial_state(cfg, "transport")
    base_f = FilterState.from_mechanics(base)
    rng = np.random.default_rng(SEED)
    sensor = ObservationGenerator(cfg, SEED, variant="transport",
                                 contact_provider=lambda s, u, m, p: mech.mechanics(s, u, m, p))

    probe_filter = est.RightIESEKF.from_protocol(base_f, cfg, condition="exp3",
                                                 object_id="A", modes=("pivot", "pivot"))
    QC = probe_filter.Qc_diag.copy()
    P0 = probe_filter.P.copy()

    arrays = {}
    cases = []

    def add(case_id, kind, X, U, modes, *, note, obs_value=None, do_update=False,
            outside_pad_domain=False):
        f, A = est.continuous_linearization(X, U, modes, physics)
        pred, F, Lw = est.prediction_linearization(X, U, modes, physics, H)
        Qd = H * (Lw * QC[None, :]) @ Lw.T
        P_pred = F @ P0 @ F.T + Qd
        c = mech.mechanics(X, U, modes, physics)
        E1, E2c = mech.common_endpoints(X)
        rates = {}
        for r, (E, G) in enumerate(((E1, X.G1), (E2c, X.G2))):
            res = geo.grasp_rate(X.O, E, G, X.V, U[r], geo.selection(modes[r]), rcond=1e-12)
            rates[f"tau_rate_{r}"] = res.tau_rate
            rates[f"grasp_body_{r}"] = res.grasp_body

        arrays[f"{case_id}__X"] = flatten_state(X)
        arrays[f"{case_id}__U"] = np.asarray(U, float).ravel()
        arrays[f"{case_id}__f"] = f
        arrays[f"{case_id}__A"] = A
        arrays[f"{case_id}__F"] = F
        arrays[f"{case_id}__Lw"] = Lw
        arrays[f"{case_id}__Qd"] = Qd
        arrays[f"{case_id}__P0"] = P0
        arrays[f"{case_id}__P_pred"] = P_pred
        arrays[f"{case_id}__X_pred"] = flatten_state(pred)
        arrays[f"{case_id}__D"] = c.D
        arrays[f"{case_id}__tau"] = c.tau
        arrays[f"{case_id}__hK"] = c.hK
        arrays[f"{case_id}__hB"] = c.hB
        arrays[f"{case_id}__h"] = c.h
        arrays[f"{case_id}__W"] = c.W
        arrays[f"{case_id}__internal"] = c.internal
        arrays[f"{case_id}__singular_values"] = c.singular_values
        for k, v in rates.items():
            arrays[f"{case_id}__{k}"] = v

        obs_rows = []
        for kind_name in ("EE1", "EE2", "hK1", "hK2", "visual1", "visual2"):
            expected = est.measurement_prediction(X, kind_name, physics)
            Hm = est.measurement_jacobian(X, kind_name, physics)
            arrays[f"{case_id}__H_{kind_name}"] = Hm
            if kind_name.startswith("hK"):
                o = expected if obs_value is None else expected + obs_value
                resid = o - expected
                arrays[f"{case_id}__z_{kind_name}"] = np.ravel(o)
            else:
                o = expected if obs_value is None else expected @ geo.se3_exp(obs_value)
                resid = geo.se3_log(geo.inverse(expected) @ o)
                arrays[f"{case_id}__z_{kind_name}"] = np.ravel(o)
            arrays[f"{case_id}__residual_{kind_name}"] = resid
            obs_rows.append({"kind": kind_name, "residual_norm": float(np.linalg.norm(resid))})

        rec = {
            "id": case_id, "kind": kind, "modes": list(modes), "h_s": H,
            "note": note, "outside_pad_domain": outside_pad_domain,
            "state_norm": float(np.linalg.norm(flatten_state(X))),
            "velocity": np.ravel(X.V).tolist(),
            "tau_frobenius": float(np.linalg.norm(c.tau)),
            "W_rank": int(np.sum(c.singular_values > 1e-10 * c.singular_values[0])),
            "singular_values": c.singular_values.tolist(),
            "observations": obs_rows,
        }

        if do_update:
            filt = est.RightIESEKF.from_protocol(X, cfg, condition="exp3", object_id="A",
                                                 modes=modes)
            filt.predict_to(H, U)
            o = obs_value if obs_value is not None else np.zeros(6)
            z = est.measurement_prediction(filt.state, "visual1", physics) @ geo.se3_exp(o)
            observation = Observation("visual1", z, sensor.covariance("visual1"),
                                      f"{case_id}:visual1:0", H, H)
            rep = filt.update((observation,))
            arrays[f"{case_id}__P_post"] = filt.P
            arrays[f"{case_id}__V_post"] = filt.state.V
            arrays[f"{case_id}__innovation_before"] = rep.innovation_before
            arrays[f"{case_id}__innovation_after"] = rep.innovation_after
            rec.update({"update_iterations": rep.iterations,
                        "update_converged": bool(rep.converged),
                        "update_stop_requested": bool(rep.stop_requested),
                        "innovation_norm_before": float(np.linalg.norm(rep.innovation_before)),
                        "innovation_norm_after": float(np.linalg.norm(rep.innovation_after))})
        cases.append(rec)

    # C01 nominal, zero velocity, pivot/pivot
    add("C01_nominal_pivot", "nominal_zero_velocity", base_f, (np.zeros(6), np.zeros(6)),
        ("pivot", "pivot"), note="frozen reference point; matches the T02 golden case")

    # C02 nonzero velocity and nonzero EE commands, pivot/pivot
    d = pose_delta(0.004, 0.02, rng)
    d[6:12] = np.r_[0.03, -0.02, 0.01, 0.15, -0.1, 0.05]
    X2 = base_f.retract(d)
    U2 = (np.array([0.01, -0.005, 0.002, 0.02, -0.01, 0.01]),
          np.array([-0.004, 0.003, 0.001, -0.015, 0.008, -0.005]))
    add("C02_moving_pivot", "nonzero_velocity", X2, U2, ("pivot", "pivot"),
        note="object 0.037 m/s and 0.19 rad/s equivalent, both EE twists nonzero")

    # C03 elastic contact + nonzero velocity, tight/tight
    d = pose_delta(0.0015, 0.02, rng)
    d[6:12] = np.r_[0.01, -0.008, 0.004, 0.05, -0.03, 0.01]
    X3 = base_f.retract(d)
    U3 = (np.array([0.002, -0.001, 0.0005, 0.005, -0.002, 0.001]),
          np.array([-0.001, 0.0008, 0.0003, -0.004, 0.002, -0.001]))
    add("C03_elastic_tight", "nonzero_elastic_contact", X3, U3, ("tight", "tight"),
        note="pad deformation about 1.5 mm / 20 mrad, inside the 5 mm / 0.15 rad domain")

    # C04 elastic contact + motion in sliding mode (generic geometry -> rank 5)
    add("C04_elastic_sliding", "nonzero_elastic_contact", X3, U3, ("sliding", "sliding"),
        note="elastic + moving; the small pose offsets tilt the sliding axes, rank 5")

    # C05 exact collinear sliding fixture (the only rank-4 configuration)
    add("C05_rank_collinear_sliding", "rank_boundary", base_f, U3, ("sliding", "sliding"),
        note="nominal collinear sliding axes; the single rank-4 configuration")

    # C06 rank boundary: tilt one EE z axis by 1 mrad so the axes are not collinear
    X6r = FilterState(base.O, base.V * 0.0, base.E1 @ geo.se3_exp(np.r_[0, 0, 0, 1e-3, 0, 0]),
                      base.E2, base.C, base.G1, base.G2, origin="provided_estimate")
    add("C06_rank_boundary_sliding", "rank_boundary", X6r, U3, ("sliding", "sliding"),
        note="1 mrad tilt of one sliding axis; expect rank 5 instead of 4")

    # C06 small angle
    d = 1e-7 * np.ones(42)
    d[6:12] = 0.0
    X6 = base_f.retract(d)
    add("C07_small_angle", "small_angle", X6, (np.zeros(6), np.zeros(6)), ("pivot", "pivot"),
        note="1e-7 m / 1e-7 rad offsets")

    # C07 near-pi contact rotation (outside the pad domain on purpose)
    axis = np.array([0.2, -0.6, 0.77]); axis /= np.linalg.norm(axis)
    tau_pi = np.r_[0.0005, -0.0003, 0.0002, axis * (np.pi - 1e-3)]
    E1_pi = base.O @ base.G1 @ geo.se3_exp(tau_pi)
    tau_pi2 = np.r_[-0.0004, 0.0002, -0.0001, axis * (np.pi - 2e-3)]
    E2c_pi = base.O @ base.G2 @ geo.se3_exp(tau_pi2)
    X7 = FilterState(base.O, base.V * 0.0, E1_pi, base.C @ E2c_pi, base.C, base.G1, base.G2,
                     origin="provided_estimate")
    add("C08_near_pi", "near_pi", X7, (np.zeros(6), np.zeros(6)), ("pivot", "pivot"),
        note="D rotation pi-1e-3 / pi-2e-3; outside the pad domain, Jacobian coverage only",
        outside_pad_domain=True)

    # C08 nonzero observation residual + one full update
    resid = np.r_[0.01, -0.005, 0.002, 0.03, -0.02, 0.01]
    add("C09_residual_update", "nonzero_observation_residual", X2, U2, ("pivot", "pivot"),
        note="visual1 observation offset by 10 mm / 37 mrad, one iterated update recorded",
        obs_value=resid, do_update=True)

    # C09 mixed modes
    add("C10_mixed_pivot_sliding", "mixed_modes", X3, U3, ("pivot", "sliding"),
        note="third H combination with motion and elastic contact")

    # C10 force dominated, still inside the pad domain
    d = pose_delta(0.003, 0.06, rng)
    d[6:12] = np.r_[0.004, -0.003, 0.002, 0.02, -0.01, 0.005]
    X10 = base_f.retract(d)
    add("C11_force_dominated", "large_elastic_contact", X10,
        (np.zeros(6), np.zeros(6)), ("tight", "tight"),
        note="about 3 mm / 60 mrad pad deformation, close to the domain gate")

    # ---------------- invalid-input fixtures ------------------------------
    def expect_reject(case_id, fn, expected_type, note):
        try:
            fn()
        except Exception as exc:                     # noqa: BLE001 - recorded on purpose
            cases.append({"id": case_id, "kind": "invalid_input", "note": note,
                          "rejected": True, "exception_type": type(exc).__name__,
                          "message": str(exc)})
            return
        cases.append({"id": case_id, "kind": "invalid_input", "note": note,
                      "rejected": False, "exception_type": None, "message": None})

    T_bad = np.eye(4); T_bad[:3, :3] *= 1.1
    expect_reject("E01_non_se3", lambda: geo.validate_transform(T_bad), "GeometryDomainError",
                  "scaled rotation must be rejected, no normalisation")
    expect_reject("E02_nan_velocity",
                  lambda: FilterState(base.O, np.full(6, np.nan), base.E1, base.E2, base.C,
                                      base.G1, base.G2),
                  "ObservationDomainError", "NaN velocity rejected at state construction")
    import types as _types
    bad_state = _types.SimpleNamespace(O=base.O, V=np.full(6, np.nan), E1=base.E1, E2=base.E2,
                                       C=base.C, G1=base.G1, G2=base.G2)
    expect_reject("E02b_nan_velocity_validate_state",
                  lambda: mech.validate_state(
                      bad_state, mech.mechanics(base_f, (np.zeros(6), np.zeros(6)),
                                                ("pivot", "pivot"), physics)),
                  "ValueError", "validate_state must raise NONFINITE_STATE")
    expect_reject("E03_unknown_mode", lambda: geo.selection("weld"), "GeometryDomainError",
                  "unknown contact mode")
    expect_reject("E04_nonorthonormal_H",
                  lambda: geo.grasp_rate(base.O, base.E1, base.G1, base.V, np.zeros(6),
                                         np.array([[1.0, 0, 0, 0, 0, 0],
                                                   [1.0, 1.0, 0, 0, 0, 0]]), rcond=1e-12),
                  "GeometryDomainError", "H rows not orthonormal")
    expect_reject("E05_bad_covariance",
                  lambda: Observation("EE1", base.E1, -np.eye(6), "x", 0.0, 0.0),
                  "ObservationDomainError", "negative covariance")
    stale = Observation("EE1", base.E1, sensor.covariance("EE1"), "stale", 0.0, 0.0)
    filt_stale = est.RightIESEKF.from_protocol(base_f, cfg, condition="exp3", object_id="A",
                                               modes=("pivot", "pivot"))
    filt_stale.predict_to(0.01, (np.zeros(6), np.zeros(6)))
    expect_reject("E06_stale_timestamp", lambda: filt_stale.update((stale,)),
                  "EstimatorDomainError", "observation older than the filter time")
    expect_reject("E07_nonpositive_dt",
                  lambda: est.RightIESEKF.from_protocol(base_f, cfg, condition="exp3",
                                                        object_id="A", modes=("pivot", "pivot")
                                                        ).predict(0.0, (np.zeros(6), np.zeros(6))),
                  "EstimatorDomainError", "prediction interval must be positive")
    expect_reject("E08_non_se3_log", lambda: geo.se3_log(T_bad), "GeometryDomainError",
                  "Log on a non-SE(3) matrix")

    # ---------------- write -------------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)
    npz = out_dir / "arrays.npz"
    np.savez_compressed(npz, **arrays)
    with (out_dir / "cases.jsonl").open("w", encoding="utf-8") as fh:
        for rec in cases:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    src = {}
    for p in ("contact_geometry.py", "mechanics.py", "estimator.py", "observations.py"):
        src[f"baselines/p2_pose_force/{p}"] = sha(ROOT / "baselines" / "p2_pose_force" / p)
    src["configs/p2_closed_loop_protocol_v3.json"] = sha(ROOT / "configs" / "p2_closed_loop_protocol_v3.json")

    import subprocess
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    tools = {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__)),
             "p2/tools/t01e_compare.py": sha(ROOT / "p2" / "tools" / "t01e_compare.py")}
    index = {
        "kind": "T01E_PRE_OPTIMISATION_EQUIVALENCE_ORACLE",
        "date": "2026-10-19",
        "frozen_before_optimisation": True,
        "source_sha256": src,
        "git_commit": commit,
        "tool_sha256": tools,
        "seed": SEED,
        "h_s": H,
        "command": "/usr/bin/python3.10 p2/tools/t01e_baseline.py",
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__},
        "arrays_npz": "arrays.npz",
        "arrays_npz_sha256": sha(npz),
        "case_count": len(cases),
        "numeric_cases": [c["id"] for c in cases if c["kind"] not in ("invalid_input",)],
        "invalid_input_cases": [c["id"] for c in cases if c["kind"] == "invalid_input"],
        "array_keys": sorted(arrays),
        "array_shapes": {k: list(v.shape) for k, v in sorted(arrays.items())},
        "tolerances_proposed": {
            "strict_no_reorder": "bitwise identical",
            "reordered_float_paths": {"abs": 1e-12, "rel": 1e-12,
                                      "note": "per element, report argmax location"},
            "invalid_inputs": "same exception type and message",
        },
        "wall_s": time.perf_counter() - T0,
    }
    (out_dir / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n",
                                    encoding="utf-8")

    print(f"cases={len(cases)} arrays={len(arrays)} npz={npz.stat().st_size/1e6:.2f} MB "
          f"wall={index['wall_s']:.2f}s")
    for rec in cases:
        if rec["kind"] == "invalid_input":
            print(f"  {rec['id']:<28} rejected={rec['rejected']} {rec['exception_type']}")
        else:
            print(f"  {rec['id']:<28} rank={rec['W_rank']} |tau|={rec['tau_frobenius']:.3e} "
                  f"|v|={np.linalg.norm(rec['velocity'][:3]):.3e}")
    print("wrote", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
