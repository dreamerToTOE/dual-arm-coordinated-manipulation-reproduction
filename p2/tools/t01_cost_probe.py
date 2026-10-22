#!/usr/bin/env python3
"""T01 cost probe: bounded, single-component engineering timings.

No control loop and no estimator/plant closed loop. Each section has a hard cap;
overruns are recorded as BENCH_TIMEOUT rather than extended. For predict/update we
restore a bounded prior before every call, because literal Euler at 4 ms makes the
covariance grow by ~60x per step and would otherwise measure a diverged matrix
instead of the per-call cost (the divergence itself is reported separately).

All numbers are ENGINEERING_SMOKE, never scientific evidence.
"""
import gzip
import io
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "p2" / "reviews" / "T01_COST_PROBE.json"
TOTAL_CAP = 60.0
SECTION_CAP = 10.0
START = time.perf_counter()


def budget_left() -> float:
    return TOTAL_CAP - (time.perf_counter() - START)


def stats(times):
    if not times:
        return {"status": "NO_SAMPLE", "repeats_done": 0, "per_call_ms": None}
    return {"status": "OK", "repeats_done": len(times),
            "per_call_ms": statistics.median(times) * 1e3,
            "min_ms": min(times) * 1e3, "max_ms": max(times) * 1e3}


def timed(fn, repeats: int, cap: float = SECTION_CAP):
    times = []
    t_section = time.perf_counter()
    for _ in range(repeats):
        if time.perf_counter() - t_section > cap:
            out = stats(times)
            out["status"] = "BENCH_TIMEOUT"
            return out
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return stats(times)


def main() -> int:
    report = {"kind": "T01_COST_PROBE", "wall_cap_s": TOTAL_CAP,
              "python": sys.version.split()[0], "executable": sys.executable,
              "env": {}, "sections": {}}

    t0 = time.perf_counter()
    import numpy as np
    report["env"]["numpy"] = np.__version__
    report["sections"]["import_numpy"] = {"status": "OK",
                                          "per_call_ms": (time.perf_counter() - t0) * 1e3}
    t0 = time.perf_counter()
    import scipy
    from scipy.linalg import expm
    report["env"]["scipy"] = scipy.__version__
    report["sections"]["import_scipy"] = {"status": "OK",
                                          "per_call_ms": (time.perf_counter() - t0) * 1e3}

    t0 = time.perf_counter()
    sys.path.insert(0, str(ROOT))
    from baselines.p2_pose_force import mechanics as mech
    from baselines.p2_pose_force.observations import (FilterState, ObservationGenerator)
    from baselines.p2_pose_force.estimator import RightIESEKF
    from baselines.p2_pose_force.native_model import NativeModel, build_native
    report["sections"]["import_p2_modules"] = {
        "status": "OK", "per_call_ms": (time.perf_counter() - t0) * 1e3}

    t0 = time.perf_counter()
    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    report["sections"]["load_protocol_json"] = {
        "status": "OK", "per_call_ms": (time.perf_counter() - t0) * 1e3}

    t0 = time.perf_counter()
    binary = build_native("/home/ubuntu2004/lmy/.p2_native_build_v3")
    native = NativeModel(binary)
    import hashlib
    report["sections"]["native_cache_check_and_load"] = {
        "status": "OK", "per_call_ms": (time.perf_counter() - t0) * 1e3,
        "binary": str(binary),
        "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest()}

    physics = mech.physics_from_protocol(cfg, "A")
    state = mech.initial_state(cfg, "transport")
    U = (np.zeros(6), np.zeros(6))
    modes = ("pivot", "pivot")
    dt = 1.0 / 3000.0

    report["sections"]["native_contact"] = timed(
        lambda: native.contact(state, U, modes, physics), 200)
    report["sections"]["native_advance_1_step_equilibrium_fixture"] = timed(
        lambda: native.advance(state, U, modes, physics, dt, 1), 200)
    report["sections"]["native_continuous_linearization"] = timed(
        lambda: native.continuous_linearization(state, U, modes, physics), 50)

    # --- realistic plant cost: 0.5 s of true integration from the declared initial
    # state (gravity unbalanced, Newton therefore does real work). No control, no
    # estimator, no logs: this is a component benchmark, not a scientific run.
    def plant_batch():
        native.advance(state, U, modes, physics, dt, 12)

    t0 = time.perf_counter()
    n_batches = 125                      # 125*12 = 1500 steps = 0.5 s simulated
    for _ in range(n_batches):
        plant_batch()
    wall = time.perf_counter() - t0
    report["sections"]["plant_only_0p5s_transient"] = {
        "status": "OK", "steps": n_batches * 12, "sim_s": n_batches * 12 * dt,
        "wall_s": wall, "per_step_ms": wall / (n_batches * 12) * 1e3,
        "realtime_factor": wall / (n_batches * 12 * dt),
        "note": "batches of 12 like the controller-period batching of the runner"}

    # --- filter: per-call cost with a bounded prior
    filt = RightIESEKF.from_protocol(FilterState.from_mechanics(state), cfg,
                                     condition="exp3", object_id="A", modes=modes,
                                     rate_provider=native.continuous_linearization)
    P0 = filt.P.copy()
    prior = filt.state.copy()
    t_prior = filt.time

    def predict_bounded():
        filt.state, filt.P, filt.time = prior.copy(), P0.copy(), t_prior
        filt.predict(0.004, U)

    report["sections"]["filter_predict_4ms_euler_bounded_prior"] = timed(predict_bounded, 100)

    # documented divergence of the literal predictor when NOT reset
    filt2 = RightIESEKF.from_protocol(FilterState.from_mechanics(state), cfg,
                                      condition="exp3", object_id="A", modes=modes,
                                      rate_provider=native.continuous_linearization)
    trace = [float(np.max(np.diag(filt2.P)))]
    failure = None
    for k in range(50):
        try:
            filt2.predict(0.004, U)
            trace.append(float(np.max(np.diag(filt2.P))))
        except Exception as exc:
            failure = {"step": k, "error": repr(exc), "p_max_before": trace[-1]}
            break
    report["sections"]["filter_predict_4ms_euler_unbounded"] = {
        "status": "REJECTED_BY_FROZEN_CHECK" if failure else "OK",
        "steps_completed": len(trace) - 1, "failure": failure,
        "p_max_trace": trace[:8], "p_max_last": trace[-1]}

    # --- update cost with the prior restored each call
    sensor = ObservationGenerator(cfg, 7, variant="transport", contact_provider=native.contact)
    tick = 30
    filt.state, filt.P, filt.time = prior.copy(), P0.copy(), t_prior
    filt.predict_to(tick * dt, U)
    packet = sensor.sample_packet(state, tick, None, modes=modes)
    snapshot = (filt.state.copy(), filt.P.copy(), filt.time, filt.consecutive_nonconverged,
                filt.stopped, set(filt.seen_samples))

    def update_bounded():
        st, Pp, tt, nc, stopped, seen = snapshot
        filt.state, filt.P, filt.time = st.copy(), Pp.copy(), tt
        filt.consecutive_nonconverged, filt.stopped = nc, stopped
        filt.seen_samples = set(seen)
        filt.update(packet)

    t_upd = timed(update_bounded, 50, cap=8.0)
    t_upd["observations_in_packet"] = [o.kind for o in packet]
    report["sections"]["filter_update_3obs_packet_bounded_prior"] = t_upd

    # --- candidate stable propagator primitives
    A42 = np.zeros((42, 42))
    A42[6:12, 6:12] = -np.diag(np.r_[np.full(3, 50.0), np.full(3, 0.5)])
    report["sections"]["expm_42x42"] = timed(lambda: expm(0.004 * A42), 20)
    big = np.zeros((84, 84))
    big[:42, :42] = A42
    big[42:, 42:] = -A42.T
    report["sections"]["expm_84x84_vanloan"] = timed(lambda: expm(0.004 * big), 10, cap=8.0)

    Ptest = P0.copy()

    def cov_update():
        F = np.eye(42) + 0.004 * A42
        return F @ Ptest @ F.T + 1e-11 * np.eye(42)

    report["sections"]["covariance_42_matmul_triplet"] = timed(cov_update, 200)

    # --- logging cost with realistic rows from the preserved run
    def row_cost(path, label):
        with gzip.open(path, "rt") as fh:
            row = json.loads(fh.readline())
        blob = len(json.dumps(row, separators=(",", ":")).encode())
        rows = [row] * 1000

        def serialize():
            return [json.dumps(r, separators=(",", ":")) for r in rows]

        def gz():
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=1) as f:
                for r in rows:
                    f.write((json.dumps(r, separators=(",", ":")) + "\n").encode())
            return buf.tell()

        s = timed(serialize, 5)
        g = timed(gz, 5)
        return {"row_bytes": blob, "serialize_1000_rows": s, "gzip1_1000_rows": g}

    case = ROOT / "results" / "20261014_P2_closed_loop_suite02" / "case_11_exp3_7"
    report["sections"]["logging_plant_rows"] = row_cost(case / "plant.jsonl.gz", "plant")
    report["sections"]["logging_estimator_rows"] = row_cost(case / "estimator.jsonl.gz", "estimator")

    report["budget_used_s"] = time.perf_counter() - START
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["sections"], indent=1)[:3000])
    print("total wall s:", round(report["budget_used_s"], 3))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
