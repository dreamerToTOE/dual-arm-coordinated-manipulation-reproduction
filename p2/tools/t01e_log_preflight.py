#!/usr/bin/env python3
"""O2 preflight: serialise REAL runner-shaped rows through EventLog and read back.

Non-scientific: no plant integration, no filter execution. It builds the exact
row shapes produced by the runner (numpy arrays for D/W/hK/h/internal/P_diagonal/
innovation_*), writes them through EventLog, reads the gzip back and checks:
  - every line parses as JSON
  - state / h_N_Nm / internal_N_Nm are present in every line (half-step gate)
  - bulk keys appear only on snapshot lines
  - finite values round-trip exactly (bitwise for float64 after list->array)
  - the ring holds 200 complete rows including bulk, and dumps readable context
  - non-finite values are written as the strings nan/inf, never dropped
"""
import gzip
import io
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from baselines.p2_pose_force import mechanics as mech          # noqa: E402
from baselines.p2_pose_force import estimator as est            # noqa: E402
from baselines.p2_pose_force.observations import (               # noqa: E402
    FilterState, ObservationGenerator, calibrate_paired_visuals)
from p2_event_log import BULK_KEYS, ALWAYS_PRESENT, EventLog    # noqa: E402

OUT = ROOT / "p2" / "reviews" / "t01e_log_preflight.json"


def build_rows(n=300):
    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    physics = mech.physics_from_protocol(cfg, "A")
    state = mech.initial_state(cfg, "transport")
    fs = FilterState.from_mechanics(state)
    U = (np.zeros(6), np.zeros(6))
    modes = ("pivot", "pivot")
    contact = mech.mechanics(state, U, modes, physics)
    filt = est.RightIESEKF.from_protocol(fs, cfg, condition="exp3", object_id="A", modes=modes)

    plant, estimator = [], []
    for i in range(n):
        t = i * 0.004
        plant.append({
            "phase": "transport", "time_s": t, "global_case_time_s": 10 + t,
            "tick": i * 12, "state": state.as_dict(),
            "D": contact.D, "tau": contact.tau,
            "hK_N_Nm": contact.hK, "hB_N_Nm": contact.hB, "h_N_Nm": contact.h,
            "internal_N_Nm": contact.internal, "external_N_Nm": contact.external,
            "W": contact.W, "W_singular_values": contact.singular_values,
            "solver": {"completed_steps": 12, "max_newton_iterations": 2},
            "GT_goal_distance_m": 0.01, "GT_goal_angle_rad": 0.02,
        })
        estimator.append({
            "tick": i * 12, "time_s": t, "global_case_time_s": 10 + t,
            "state": fs.as_dict(), "P_diagonal": np.diag(filt.P),
            "P_full_at_1Hz": filt.P if i % 250 == 0 else None,
            "old_published_model_input": [np.zeros(6), np.zeros(6)],
            "prediction_interval_s": 0.004,
            "observations_consumed": [["EE1", f"transport:EE1:{i}"]],
            "iterations": 3, "converged": True, "consecutive_nonconverged": 0,
            "innovation_before": np.linspace(1e-6, 2e-6, 6),
            "innovation_after": np.linspace(1e-7, 2e-7, 6),
            "stop_requested": False,
        })
    return plant, estimator


def roundtrip(rows, label, ref_key="W", ring_keys=("state", "W", "h_N_Nm"),
              required=tuple(ALWAYS_PRESENT)):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=1) as gz:
        log = EventLog(gz, snapshot_period_s=1.0, ring_size=200)
        for r in rows:
            log.event(r["time_s"], r)
    raw = gzip.decompress(buf.getvalue()).decode().splitlines()
    lines = [json.loads(x) for x in raw if x]

    bulk_expected = BULK_KEYS & set(rows[0].keys())
    present_ok = all(all(k in ln for k in required) for ln in lines)
    bulk_flags = [ln["bulk_snapshot"] for ln in lines]
    bulk_only_snapshot = all(
        (all(k in ln for k in bulk_expected) if ln["bulk_snapshot"]
         else all(k not in ln for k in bulk_expected))
        for ln in lines)

    # exact round-trip of a finite numpy array (bitwise after list -> array)
    ref = np.asarray(rows[0][ref_key])
    got = np.array(lines[0][ref_key])
    exact = (got.dtype == ref.dtype) and bool(np.array_equal(got, ref))
    if "h_N_Nm" in rows[0]:
        ref_h = np.asarray(rows[0]["h_N_Nm"])
        exact_h = bool(np.array_equal(np.array(lines[0]["h_N_Nm"]), ref_h))
    else:
        exact_h = True

    ring_full = len(log.ring) == min(200, len(rows))
    ring_has_bulk = all(all(k in rec for k in ring_keys) for rec in log.ring) \
        if ring_full else False

    dump_path = Path(f"/tmp/t01e_preflight_{label}.json")
    log.dump_context(dump_path, reason="preflight")
    dump = json.loads(dump_path.read_text())
    dump_ok = (len(dump["events"]) == min(200, len(rows))
               and dump["reason"] == "preflight"
               and "state" in dump["events"][0])

    return {
        "label": label, "events": len(lines), "expected_events": len(rows),
        "all_lines_parse": len(lines) == len(rows),
        "always_present_ok": present_ok,
        "bulk_only_on_snapshots": bulk_only_snapshot,
        "snapshots": int(sum(bulk_flags)),
        "exact_roundtrip_ref": exact,
        "ref_key": ref_key,
        "exact_roundtrip_h": exact_h,
        "ring_len": len(log.ring),
        "ring_full_rows": ring_full,
        "ring_has_bulk_and_state": ring_has_bulk,
        "dump_events": len(dump["events"]),
        "dump_ok": dump_ok,
        "payload_bytes": len(buf.getvalue()),
        "counters": log.summary(),
        "pass": all([len(lines) == len(rows), present_ok, bulk_only_snapshot, exact,
                     exact_h, ring_full, ring_has_bulk, dump_ok]),
    }


def calibration_check():
    """The calibration path is exercised before any prediction; cover it here."""
    cfg = json.loads((ROOT / "configs" / "p2_closed_loop_protocol_v3.json").read_text())
    state = mech.initial_state(cfg, "transport")
    sensor = ObservationGenerator(cfg, 7, variant="transport",
                                  contact_provider=mech.mechanics)
    pairs = sensor.precalibration_pairs(state)
    cal = calibrate_paired_visuals(pairs, cfg)
    return {"pairs": len(pairs), "iterations": cal.iterations,
            "max_mean_component": cal.maximum_mean_component,
            "pass": len(pairs) == 75 and cal.maximum_mean_component < 1e-9}


def nonfinite_check():
    """A NaN must be visible as the string 'nan', never dropped or clipped."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        log = EventLog(gz, snapshot_period_s=1.0, ring_size=4)
        row = {"phase": "transport", "time_s": 0.0, "tick": 0,
               "state": {"O": np.eye(4)}, "h_N_Nm": np.zeros((2, 6)),
               "internal_N_Nm": np.full((2, 6), np.nan)}
        log.event(0.0, row)
    line = json.loads(gzip.decompress(buf.getvalue()).decode().splitlines()[0])
    cell = line["internal_N_Nm"][0][0]
    return {"serialized_as": cell, "is_string": isinstance(cell, str),
            "detectable": isinstance(cell, str) and cell == "nan",
            "pass": isinstance(cell, str) and cell == "nan"}


def main() -> int:
    plant, estimator = build_rows()
    r_plant = roundtrip(plant, "plant")
    r_est = roundtrip(estimator, "estimator", ref_key="P_diagonal",
                      ring_keys=("state", "P_diagonal", "innovation_before"),
                      required=("tick", "time_s", "state", "P_diagonal",
                                "innovation_before", "iterations", "converged"))
    nf = nonfinite_check()
    cal = calibration_check()
    ok = r_plant["pass"] and r_est["pass"] and nf["pass"] and cal["pass"]
    payload = {"kind": "T01E_O2_PREFLIGHT", "plant": r_plant, "estimator": r_est,
               "nonfinite": nf, "calibration_path": cal,
               "bulk_keys": sorted(BULK_KEYS),
               "always_present": sorted(ALWAYS_PRESENT),
               "verdict": "PASS" if ok else "FAIL"}
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name in ("plant", "estimator"):
        r = payload[name]
        print(f"{name}: events={r['events']} snapshots={r['snapshots']} "
              f"present={r['always_present_ok']} bulk_rule={r['bulk_only_on_snapshots']} "
              f"exact={r['exact_roundtrip_ref']} ring={r['ring_len']}/{r['ring_full_rows']} "
              f"dump={r['dump_ok']} bytes={r['payload_bytes']} pass={r['pass']}")
    print("nonfinite:", nf)
    print("calibration:", cal)
    print("verdict:", payload["verdict"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
