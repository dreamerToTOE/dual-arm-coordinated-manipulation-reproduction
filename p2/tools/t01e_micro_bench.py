#!/usr/bin/env python3
"""Bounded micro-benchmarks for T01-E (<=15 s total).

Each section uses a fixed fixture and a hard per-section cap. Numbers are
ENGINEERING_SMOKE, not scientific results; the pre-optimisation reference is
p2/reviews/T01_COST_PROBE.json measured with the same method.
"""
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from baselines.p2_pose_force import contact_geometry as geo      # noqa: E402
from baselines.p2_pose_force import mechanics as mech          # noqa: E402
from baselines.p2_pose_force import estimator as est            # noqa: E402
from baselines.p2_pose_force.observations import (               # noqa: E402
    FilterState, ObservationGenerator)
from baselines.p2_pose_force.native_model import (               # noqa: E402
    NativeModel, build_native)

OUT = ROOT / "p2" / "reviews" / "t01e_micro_bench.json"
CAP = 15.0
T0 = time.perf_counter()


def timed(fn, n, cap):
    times = []
    t_start = time.perf_counter()
    for _ in range(n):
        if time.perf_counter() - t_start > cap:
            break
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    if not times:
        return {"n": 0, "median_ms": None}
    return {"n": len(times), "median_ms": statistics.median(times) * 1e3,
            "min_ms": min(times) * 1e3, "max_ms": max(times) * 1e3}


def main() -> int:
    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    physics = mech.physics_from_protocol(cfg, "A")
    base = mech.initial_state(cfg, "transport")
    base_f = FilterState.from_mechanics(base)
    U = (np.zeros(6), np.zeros(6))
    modes = ("pivot", "pivot")
    dt = 1.0 / 3000.0

    native = NativeModel(build_native("/home/ubuntu2004/lmy/.p2_native_build_v3"))
    filt = est.RightIESEKF.from_protocol(base_f, cfg, condition="exp3", object_id="A",
                                         modes=modes,
                                         rate_provider=native.continuous_linearization)
    P0, prior, t_prior = filt.P.copy(), filt.state.copy(), filt.time

    def predict_bounded():
        filt.state, filt.P, filt.time = prior.copy(), P0.copy(), t_prior
        filt.predict(0.004, U)

    sensor = ObservationGenerator(cfg, 7, variant="transport",
                                  contact_provider=lambda s, u, m, p: mech.mechanics(s, u, m, p))
    filt.state, filt.P, filt.time = prior.copy(), P0.copy(), t_prior
    filt.predict_to(30 * dt, U)
    packet = sensor.sample_packet(base, 30, None, modes=modes)
    snap = (filt.state.copy(), filt.P.copy(), filt.time, filt.consecutive_nonconverged,
            filt.stopped, set(filt.seen_samples))

    def update_bounded():
        st, Pp, tt, nc, stopped, seen = snap
        filt.state, filt.P, filt.time = st.copy(), Pp.copy(), tt
        filt.consecutive_nonconverged, filt.stopped = nc, stopped
        filt.seen_samples = set(seen)
        filt.update(packet)

    T = geo.se3_exp(np.r_[0.01, -0.02, 0.03, 0.2, -0.3, 0.1])

    sections = {
        "predict_4ms": timed(predict_bounded, 100, 4.0),
        "update_3obs": timed(update_bounded, 30, 4.0),
        "se3_log_public": timed(lambda: geo.se3_log(T), 4000, 3.0),
        "se3_log_internal": timed(lambda: geo._log4(T), 4000, 3.0),
        "adjoint_inverse": timed(lambda: geo.adjoint(geo.inverse(T)), 4000, 3.0),
        "contact": timed(lambda: mech.mechanics(base_f, U, modes, physics), 300, 2.0),
    }
    sections["total_wall_s"] = time.perf_counter() - T0
    sections["cap_s"] = CAP
    OUT.write_text(json.dumps({"kind": "T01E_MICRO_BENCH", "date": "2026-10-19",
                               "sections": sections}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    for k, v in sections.items():
        if isinstance(v, dict):
            print(f"{k:<20} n={v['n']:<5} median={v['median_ms']:.3f} ms")
    print("wall", round(sections["total_wall_s"], 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
