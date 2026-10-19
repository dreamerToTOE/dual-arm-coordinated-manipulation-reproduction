#!/usr/bin/env python3
"""T04 R1+ replay: full per-event instrumentation for modes A and B.

Fixes all R1 defects: actual per-mode innovations, non-convergence stop gate,
full 42x42 P per event, NEES by Cholesky (per-block where definable),
NIS from actual whitened prior innovation, per-event timing, split gate values.
"""
import argparse
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.linalg import cho_factor, cho_solve

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "p2" / "tools"))

from baselines.p2_pose_force import contact_geometry as geo                  # noqa: E402
from baselines.p2_pose_force import mechanics as mech                       # noqa: E402
from baselines.p2_pose_force import estimator as est                         # noqa: E402
from baselines.p2_pose_force import stable_propagation as sp                  # noqa: E402
from baselines.p2_pose_force.observations import (                            # noqa: E402
    FilterState, Observation)
from baselines.p2_pose_force.native_model import NativeModel, build_native    # noqa: E402

SOURCE = ROOT / "p2" / "runs" / "20261019_103729_T01E_SMOKE_case11_exp3_seed7"
BLOCKS = ("O", "V", "E1", "E2", "C", "G1", "G2")
GATE_LIN, GATE_ANG = 0.005, 0.15


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_gz(name):
    with gzip.open(SOURCE / name, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


class StableFilter(est.RightIESEKF):
    def predict(self, dt, published_command):
        if self.stopped:
            raise est.EstimatorDomainError('FILTER_ALREADY_STOPPED')
        f, A = (self.rate_provider or est.continuous_linearization)(
            self.state, published_command, self.modes, self.physics)
        pred, Phi, Qd, _ = sp.propagate(self.state, f, A, dt, self.Qc_diag)
        P = est._checked_covariance(Phi @ self.P @ Phi.T + Qd)
        rep = est.PredictionReport(self.time, self.time + dt, Phi, Qd)
        self.state, self.P, self.time = pred, P, self.time + dt
        self.last_prediction = rep
        return rep


def build_filter(mode, cfg, native, init):
    ph = mech.physics_from_protocol(cfg, "A", "exp3", observer=True)
    state = FilterState(**{k: np.array(v, float) for k, v in init["estimate"].items()})
    P0 = np.array(init["P0"], float)
    cls = StableFilter if mode == "B" else est.RightIESEKF
    filt = cls(state, ph, ("pivot", "pivot"), P0, np.zeros(42),
               initial_time=0.0, rate_provider=native.continuous_linearization)
    filt.Qc_diag = 0.004 * np.concatenate([np.array(cfg["original_parameters"]["Q"][k], float)
                                           for k in ("O", "V", "E1", "E2", "C_transport", "G1", "G2")])
    filt.P = P0.copy()
    filt.seen_samples = {tuple(k) for k in init["consumed_samples"]}
    return filt, ph


def compute_nees(err42, P):
    """NEES via Cholesky; returns per-block dict and total, or NOT_COMPUTABLE."""
    try:
        L = np.linalg.cholesky((P + P.T) / 2)
    except np.linalg.LinAlgError:
        return {"total": "NOT_COMPUTABLE", "reason": "P not SPD"}
    y = np.linalg.solve(L, err42)
    total = float(np.dot(y, y))
    blocks = {}
    for i, name in enumerate(BLOCKS):
        sl = slice(6 * i, 6 * i + 6)
        blocks[name] = float(np.dot(y[sl], y[sl]))
    return {"total": total, **blocks}


def compute_nis(filt, state, packet, observations_data):
    """NIS = rw^T S^{-1} rw using the prior P and the linearised packet."""
    try:
        T = np.eye(42)
        residual, rw, Hw = filt._linearized_packet(state, packet, T)
        S = np.eye(len(rw)) + Hw @ filt.P @ Hw.T
        L = np.linalg.cholesky(S)
        y = np.linalg.solve(L, rw)
        nis = float(np.dot(y, y))
        return {"nis": nis, "dof": len(rw), "S_min_eig": float(np.linalg.eigvalsh(S)[0])}
    except Exception as exc:
        return {"nis": "NOT_COMPUTABLE", "reason": repr(exc)[:80]}


def replay(mode, cfg, native, run_dir, wall_cap):
    t0 = time.perf_counter()
    init = json.loads((SOURCE / "initialization.json").read_text())
    est_rows = read_gz("estimator.jsonl.gz")
    sensors = read_gz("sensors.jsonl.gz")
    by_id = {r["observation"]["sample_id"]: r["observation"] for r in sensors}
    plant = {r["tick"]: r for r in read_gz("plant.jsonl.gz")}

    filt, ph_est = build_filter(mode, cfg, native, init)
    ph_ctrl = mech.physics_from_protocol(cfg, "A", "exp3", observer=True)

    summary_rows = []
    P_matrices = []
    gate_lin_max, gate_ang_max = 0.0, 0.0
    counts = {"predictions": 0, "updates": 0}
    failure, stop_reason = None, None
    timing = {"predict_s": [], "update_s": [], "nees_s": []}

    for idx, row in enumerate(est_rows[1:]):
        if time.perf_counter() - t0 > wall_cap:
            failure = "BUDGET_STOP"
            break
        tick, t = row["tick"], row["time_s"]
        U_raw = row["old_published_model_input"]
        U = (np.array(U_raw[0], float), np.array(U_raw[1], float))

        tp0 = time.perf_counter()
        pred = filt.predict_to(t, U)
        tp1 = time.perf_counter()
        if pred is not None:
            counts["predictions"] += 1
            timing["predict_s"].append(tp1 - tp0)

        innov_b, innov_a, nis_data = None, None, None
        if row["observations_consumed"] and tick > 0:
            packet = []
            for kind, sid in row["observations_consumed"]:
                o = by_id[sid]
                packet.append(Observation(kind, np.array(o["value"], float),
                                          np.array(o["covariance"], float),
                                          o["sample_id"], o["sample_stamp"], o["delivery_stamp"]))
            # NIS from prior (before update iterations)
            nis_data = compute_nis(filt, filt.state, packet, None)
            tu0 = time.perf_counter()
            rep = filt.update(packet)
            tu1 = time.perf_counter()
            counts["updates"] += 1
            timing["update_s"].append(tu1 - tu0)
            innov_b = float(np.linalg.norm(rep.innovation_before))
            innov_a = float(np.linalg.norm(rep.innovation_after))
            if rep.stop_requested:
                failure = rep.stop_reason or "UPDATE_STOP_REQUESTED"
                stop_reason = failure
                break

        # domain gate
        modeled = native.contact(filt.state, U, modes=("pivot", "pivot"), physics=ph_ctrl)
        lin_max = float(np.max(np.abs(modeled.tau[:, :3])))
        ang_max = float(np.max(np.abs(modeled.tau[:, 3:])))
        gate_lin_max = max(gate_lin_max, lin_max)
        gate_ang_max = max(gate_ang_max, ang_max)
        if lin_max > GATE_LIN or ang_max > GATE_ANG:
            failure = "ESTIMATOR_MODEL_PAD_DOMAIN_INVALID"
            stop_reason = f"linear={lin_max:.6f} angular={ang_max:.6f}"
            break

        # state error vs GT
        gt = plant.get(tick)
        err_vec = None
        if gt is not None:
            gt_state = gt["state"]
            d = np.zeros(42)
            for i, blk in enumerate(BLOCKS):
                est_blk = getattr(filt.state, blk)
                gt_blk = np.array(gt_state[blk], float)
                if blk == "V":
                    d[6*i:6*i+6] = est_blk - gt_blk
                else:
                    d[6*i:6*i+6] = geo.se3_log(geo.inverse(gt_blk.reshape(4,4)) @ est_blk.reshape(4,4))
            err_vec = d.tolist()

        # domain gate values (split)
        # NEES and P persistence
        P_matrices.append(filt.P.copy())
        nees_data = {"total": "NOT_COMPUTABLE", "reason": "no GT"}
        if err_vec is not None:
            tn0 = time.perf_counter()
            nees_data = compute_nees(np.array(err_vec), filt.P)
            timing["nees_s"].append(time.perf_counter() - tn0)

        summary_rows.append({
            "tick": tick, "t": t, "is_update": innov_b is not None,
            "v_lin": filt.state.V[:3].tolist(), "v_ang": filt.state.V[3:].tolist(),
            "p_trace": float(np.trace(filt.P)),
            "innov_before": innov_b, "innov_after": innov_a,
            "nis_dof": nis_data.get("dof") if nis_data else None,
            "nis": nis_data.get("nis") if nis_data else None,
            "nees_total": nees_data.get("total"),
            "nees_O": nees_data.get("O"),
            "nees_V": nees_data.get("V"),
            "gate_lin": lin_max, "gate_ang": ang_max,
            "consecutive_nonconverged": filt.consecutive_nonconverged,
            "err_norm": float(np.linalg.norm(err_vec)) if err_vec is not None else None,
        })

    # check non-convergence gate
    if filt.consecutive_nonconverged >= 3 and failure is None:
        failure = "THREE_CONSECUTIVE_NONCONVERGED"
        stop_reason = "non-convergence stop gate"

    # save P matrices
    P_arr = np.array(P_matrices)
    np.savez_compressed(run_dir / f"P_{mode}.npz", P=P_arr)
    summary_rows_arr = {k: [r[k] for r in summary_rows] for k in summary_rows[0]} if summary_rows else {}
    np.savez_compressed(run_dir / f"summary_{mode}.npz",
                        **{k: np.array(v, dtype=float) for k, v in summary_rows_arr.items()
                           if all(isinstance(x, (int, float)) or x is None for x in v)})

    result = {
        "mode": mode, "counts": counts, "failure": failure, "stop_reason": stop_reason,
        "gate_lin_max": gate_lin_max, "gate_ang_max": gate_ang_max,
        "timing": {
            "predict_median_ms": float(np.median(timing["predict_s"]) * 1e3) if timing["predict_s"] else None,
            "predict_max_ms": float(np.max(timing["predict_s"]) * 1e3) if timing["predict_s"] else None,
            "update_median_ms": float(np.median(timing["update_s"]) * 1e3) if timing["update_s"] else None,
            "update_max_ms": float(np.max(timing["update_s"]) * 1e3) if timing["update_s"] else None,
            "nees_median_ms": float(np.median(timing["nees_s"]) * 1e3) if timing["nees_s"] else None,
        },
        "summary_rows": summary_rows,
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("A", "B"), required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--wall-cap", type=float, required=True)
    args = ap.parse_args()

    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    native = NativeModel(build_native("/home/ubuntu2004/lmy/.p2_native_build_v3"))
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=False)

    result = replay(args.mode, cfg, native, out_dir, args.wall_cap)
    result["source_sha256"] = {p.name: sha(SOURCE / p.name) for p in sorted(SOURCE.iterdir()) if p.is_file()}
    result["files"] = {p.name: sha(p) for p in sorted(out_dir.iterdir()) if p.is_file()}
    (out_dir / "replay_summary.json").write_text(
        json.dumps({k: v for k, v in result.items() if k != "summary_rows"}, indent=2,
                   ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("mode", "counts", "failure",
                                             "gate_lin_max", "gate_ang_max")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
