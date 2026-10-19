#!/usr/bin/env python3
"""T04 R1: offline observation-driven replay of the frozen case11 stream.

Mode A uses the untouched RightIESEKF.predict (PAPER_LITERAL_EULER).
Mode B subclasses it with the stable propagation (ADAPTED_STABLE_PROPAGATION_V1);
the estimator default path is not modified. No plant, no controller, no GT in
the loop; the frozen plant log is read only for post-hoc scoring.

Usage:
  t04_r1_replay.py --mode A --output p2/runs/<id>_R1_A
  t04_r1_replay.py --mode B --output p2/runs/<id>_R1_B
"""
import argparse
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "p2" / "tools"))

from baselines.p2_pose_force import contact_geometry as geo                # noqa: E402
from baselines.p2_pose_force import mechanics as mech                     # noqa: E402
from baselines.p2_pose_force import estimator as est                       # noqa: E402
from baselines.p2_pose_force import stable_propagation as sp                # noqa: E402
from baselines.p2_pose_force.observations import (                          # noqa: E402
    FilterState, Observation)
from baselines.p2_pose_force.native_model import NativeModel, build_native  # noqa: E402

SOURCE = ROOT / "p2" / "runs" / "20261019_103729_T01E_SMOKE_case11_exp3_seed7"
BLOCKS = ("O", "V", "E1", "E2", "C", "G1", "G2")
GATE_LIN, GATE_ANG = 0.005, 0.15


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_jsonl_gz(name):
    with gzip.open(SOURCE / name, "rt") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def build_filter(mode, cfg, native, init):
    ph_est = mech.physics_from_protocol(cfg, "A", "exp3", observer=True)
    state = FilterState(**{k: np.array(v, float) for k, v in init["estimate"].items()})
    P0 = np.array(init["P0"], float)
    cls = est.RightIESEKF
    if mode == "B":
        class StableRightIESEKF(est.RightIESEKF):
            def predict(self, dt, published_command):
                if self.stopped:
                    raise est.EstimatorDomainError('FILTER_ALREADY_STOPPED')
                f, A = (self.rate_provider or est.continuous_linearization)(
                    self.state, published_command, self.modes, self.physics)
                pred, Phi, Qd, _ = sp.propagate(self.state, f, A, dt, self.Qc_diag)
                posterior_P = est._checked_covariance(Phi @ self.P @ Phi.T + Qd)
                report = est.PredictionReport(self.time, self.time + dt, Phi, Qd)
                self.state, self.P, self.time = pred, posterior_P, self.time + dt
                self.last_prediction = report
                return report
        cls = StableRightIESEKF
    filt = cls(state, ph_est, ("pivot", "pivot"), P0,
               np.array(json.loads(json.dumps([0.0] * 42)), float),
               initial_time=0.0, rate_provider=native.continuous_linearization)
    # the frozen run's Qc is 0.004*Q_table; rebuild it exactly as the estimator does
    Qdiag = 0.004 * np.concatenate([np.array(cfg["original_parameters"]["Q"][k], float)
                                    for k in ("O", "V", "E1", "E2", "C_transport", "G1", "G2")])
    filt.Qc_diag = Qdiag
    filt.P = P0.copy()
    filt.seen_samples = {tuple(k) for k in init["consumed_samples"]}
    return filt, ph_est


def replay(mode, cfg, native, out_dir, wall_cap):
    t0 = time.perf_counter()
    init = json.loads((SOURCE / "initialization.json").read_text())
    est_rows = read_jsonl_gz("estimator.jsonl.gz")
    sensors = read_jsonl_gz("sensors.jsonl.gz")
    by_id = {}
    for r in sensors:
        o = r["observation"]
        by_id[o["sample_id"]] = o
    plant = read_jsonl_gz("plant.jsonl.gz") or []
    gt_by_tick = {r["tick"]: r for r in plant}

    filt, ph_est = build_filter(mode, cfg, native, init)
    out_rows = []
    counts = {"predictions": 0, "updates": 0}
    failure = None
    max_state_diff = 0.0
    max_innov_diff = 0.0
    nees = []

    for row in est_rows[1:]:
        if time.perf_counter() - t0 > wall_cap:
            failure = "BUDGET_STOP"
            break
        tick, t = row["tick"], row["time_s"]
        U = np.array(row["old_published_model_input"], float)
        pred = filt.predict_to(t, (U[0], U[1]))
        if pred is not None:
            counts["predictions"] += 1
        innov_before = None
        if row["observations_consumed"]:
            packet = []
            for kind, sid in row["observations_consumed"]:
                o = by_id[sid]
                packet.append(Observation(kind, np.array(o["value"], float),
                                          np.array(o["covariance"], float),
                                          o["sample_id"], o["sample_stamp"],
                                          o["delivery_stamp"]))
            rep = filt.update(packet)
            counts["updates"] += 1
            innov_before = float(np.linalg.norm(rep.innovation_before))
        # domain gate (same as the runner)
        modeled = native.contact(filt.state, (U[0], U[1]), modes=("pivot", "pivot"), physics=ph_est)
        gate_ok = (np.all(np.abs(modeled.tau[:, :3]) <= GATE_LIN)
                   and np.all(np.abs(modeled.tau[:, 3:]) <= GATE_ANG))
        if not gate_ok:
            failure = "ESTIMATOR_MODEL_PAD_DOMAIN_INVALID"
            break

        # compare against the frozen log
        fs_row = row["state"]
        max_d = 0.0
        for blk in BLOCKS:
            a = getattr(filt.state, blk)
            b = np.array(fs_row[blk], float)
            max_d = max(max_d, float(np.max(np.abs(a - b))))
        max_state_diff = max(max_state_diff, max_d)
        if innov_before is not None and row.get("innovation_before") is not None:
            max_innov_diff = max(max_innov_diff, abs(
                innov_before - float(np.linalg.norm(row["innovation_before"]))))

        gt = gt_by_tick.get(tick)
        nees_v = None
        if gt is not None:
            d = np.concatenate([
                geo.se3_log(geo.inverse(np.array(gt["state"]["O"])) @ filt.state.O),
                filt.state.V - np.array(gt["state"]["V"], float),
                geo.se3_log(geo.inverse(filt.state.C) @ np.array(gt["state"]["C"])) * 0])
            try:
                nees_v = float(d @ np.linalg.solve(filt.P, d))
            except Exception:
                nees_v = None
        out_rows.append({"tick": tick, "t": t, "V": filt.state.V.tolist(),
                         "pos": filt.state.O[:3, 3].tolist(),
                         "p_trace": float(np.trace(filt.P)),
                         "p_sym": float(np.max(np.abs(filt.P - filt.P.T))),
                         "p_min_eig": float(np.linalg.eigvalsh((filt.P + filt.P.T) / 2)[0]),
                         "innov_before": (None if row.get("innovation_before") is None
                                          else float(np.linalg.norm(row["innovation_before"]))),
                         "nees": nees_v,
                         "gate_tau_max": float(np.max(np.abs(modeled.tau))),
                         })

    return {"mode": mode, "counts": counts, "failure": failure,
            "max_state_diff_vs_frozen": max_state_diff,
            "rows": out_rows, "nees": nees, "frozen_est_rows": len(est_rows)}


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
    result["source_sha256"] = {p.name: sha(p) for p in sorted(SOURCE.iterdir()) if p.is_file()}
    result["files"] = {p.name: sha(p) for p in sorted(out_dir.iterdir()) if p.is_file()}
    (out_dir / "replay_summary.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("mode", "counts", "failure",
                                             "max_state_diff_vs_frozen")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
