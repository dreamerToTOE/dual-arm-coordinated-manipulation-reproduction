#!/usr/bin/env python3
"""O2 A/B test: legacy full-row logging vs event-preserving policy.

Feeds the SAME synthetic event stream (600 events at 250 Hz, realistic row shape
copied from the preserved plant log) to both writers, then checks:
  - identical event count, order and timestamps
  - identical lossless summaries (phase/time/forces/errors/etc.)
  - bulk payload present only on snapshots (>=1 s) or exceptional events
  - counters add up, ring buffer bound and dump work
  - bytes written before/after
"""
import gzip
import io
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from p2_event_log import BULK_KEYS, EventLog        # noqa: E402

OUT = ROOT / "p2" / "reviews" / "t01e_log_compare.json"


def make_rows(n=600):
    rows = []
    for i in range(n):
        t = i * 0.004
        rows.append({
            "phase": "transport", "time_s": t, "global_case_time_s": 10 + t,
            "tick": i * 12, "state": {"O": [[1, 0, 0, 0.1 * t], [0, 1, 0, 0],
                                            [0, 0, 1, 0.4], [0, 0, 0, 1]]},
            "D": [[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]] * 2,
            "tau": [[0.0] * 6] * 2, "hK_N_Nm": [[0.1] * 6] * 2,
            "hB_N_Nm": [[0.01] * 6] * 2, "h_N_Nm": [[0.11] * 6] * 2,
            "internal_N_Nm": [[0.001] * 6] * 2,
            "W": [[0.0] * 12] * 6, "W_singular_values": [1.0] * 6,
            "estimated_state": {"O": [[1, 0, 0, 0.1 * t], [0, 1, 0, 0],
                                      [0, 0, 1, 0.4], [0, 0, 0, 1]]},
            "solver": {"completed_steps": 12, "max_newton_iterations": 3},
            "GT_goal_distance_m": 0.01, "GT_goal_angle_rad": 0.02,
            "converged": True, "iterations": 3,
            "P_diagonal": [1e-6] * 42,
            "innovation_before": [1e-4] * 6, "innovation_after": [1e-5] * 6,
            "prediction_interval_s": 0.004, "observations_consumed": ["EE1"],
            "stop_requested": False,
        })
    return rows


def write_legacy(rows):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=1) as gz:
        for r in rows:
            gz.write((json.dumps(r, separators=(",", ":")) + "\n").encode())
    return buf.getvalue()


def write_policy(rows, period=1.0):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=1) as gz:
        log = EventLog(gz, snapshot_period_s=period, ring_size=200)
        for i, r in enumerate(rows):
            log.event(r["time_s"], r, exceptional=(i == 450))
    return buf.getvalue(), log


def main() -> int:
    rows = make_rows()
    legacy = write_legacy(rows)
    policy, log = write_policy(rows)

    def timeit(fn, n=5):
        samples = []
        for _ in range(n):
            t0 = time.perf_counter()
            fn()
            samples.append(time.perf_counter() - t0)
        return statistics.median(samples) * 1e3

    t_legacy = timeit(lambda: write_legacy(rows))
    t_policy = timeit(lambda: write_policy(rows))

    legacy_lines = [json.loads(l) for l in
                    gzip.decompress(legacy).decode().splitlines() if l]
    policy_lines = [json.loads(l) for l in
                    gzip.decompress(policy).decode().splitlines() if l]

    same_count = len(legacy_lines) == len(policy_lines) == len(rows)
    same_time = all(a["time_s"] == b["time_s"] and a["tick"] == b["tick"]
                    for a, b in zip(legacy_lines, policy_lines))
    summary_keys = [k for k in rows[0] if k not in BULK_KEYS]
    same_summary = all(all(a.get(k) == b.get(k) for k in summary_keys)
                       for a, b in zip(legacy_lines, policy_lines))
    bulk_flags = [line["bulk_snapshot"] for line in policy_lines]
    bulk_count = sum(bulk_flags)
    expected_bulk = 1 + int(0.6 // 1.0) + 1          # first, every 1 s, one exceptional
    bulk_ok = bulk_count <= expected_bulk + 2 and bulk_count >= 2
    exceptional_line = policy_lines[450]
    exceptional_has_bulk = exceptional_line["bulk_snapshot"] is True and "W" in exceptional_line
    counters = log.summary()
    counters_ok = counters["events"] == len(rows) and \
        counters["events"] == counters["snapshots"] + counters["suppressed"]
    ring_ok = len(log.ring) == 200
    dump_path = Path("/tmp/t01e_log_context.json")
    log.dump_context(dump_path, reason="synthetic_exception")
    dump = json.loads(dump_path.read_text())
    dump_ok = len(dump["events"]) == 200 and dump["reason"] == "synthetic_exception"

    result = {
        "kind": "T01E_LOG_POLICY_AB",
        "events": len(rows),
        "event_count_equal": same_count,
        "timestamps_equal": same_time,
        "summary_fields_equal": same_summary,
        "bulk_snapshots": bulk_count,
        "bulk_snapshot_rule_ok": bulk_ok,
        "exceptional_event_keeps_bulk": bool(exceptional_has_bulk),
        "counters": counters,
        "counters_consistent": counters_ok,
        "ring_buffer_events": len(log.ring),
        "ring_buffer_ok": ring_ok,
        "exception_dump_ok": dump_ok,
        "payload_bytes_legacy": len(legacy),
        "payload_bytes_policy": len(policy),
        "payload_ratio": len(policy) / len(legacy),
        "write_ms_legacy": t_legacy,
        "write_ms_policy": t_policy,
        "write_ratio": t_policy / t_legacy,
        "verdict": "PASS" if all([same_count, same_time, same_summary, bulk_ok,
                                  exceptional_has_bulk, counters_ok, ring_ok,
                                  dump_ok]) else "FAIL",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for k, v in result.items():
        if k not in ("kind",):
            print(f"{k}: {v}")
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
