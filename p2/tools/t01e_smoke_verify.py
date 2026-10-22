#!/usr/bin/env python3
"""Post-run verification of a T01-E smoke directory (read-only)."""
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

RUN = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if RUN is None or not RUN.is_dir():
    print("usage: t01e_smoke_verify.py <run_dir>", file=sys.stderr)
    raise SystemExit(2)

OUT = RUN / "smoke_verification.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_jsonl_gz(name):
    path = RUN / name
    if not path.exists():
        return None
    with gzip.open(path, "rt") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main() -> int:
    summary = json.loads((RUN / "summary.json").read_text())
    termination = json.loads((RUN / "termination.json").read_text()) \
        if (RUN / "termination.json").exists() else None

    plant = read_jsonl_gz("plant.jsonl.gz") or []
    est = read_jsonl_gz("estimator.jsonl.gz") or []
    sensors = read_jsonl_gz("sensors.jsonl.gz") or []
    commands = read_jsonl_gz("commands.jsonl.gz") or []
    settling = read_jsonl_gz("settling.jsonl.gz") or []

    def monotonic(rows):
        ts = [r["time_s"] for r in rows]
        return all(b >= a for a, b in zip(ts, ts[1:])), (ts[0], ts[-1]) if ts else (None, None)

    plant_mono, plant_span = monotonic(plant)
    est_mono, est_span = monotonic(est)

    plant_required = all(all(k in r for k in ("state", "h_N_Nm", "internal_N_Nm"))
                         for r in plant)
    est_required = all(all(k in r for k in ("state", "P_diagonal"))
                       for r in est)
    plant_snap = sum(1 for r in plant if r.get("bulk_snapshot"))
    est_snap = sum(1 for r in est if r.get("bulk_snapshot"))
    plant_bulk_suppressed_clean = all(
        ("W" not in r) for r in plant if not r.get("bulk_snapshot"))

    kinds = Counter(o["observation"]["kind"] for o in sensors)
    events = Counter(e.get("type", "?") for e in
                     [json.loads(l) for l in (RUN / "events.jsonl").read_text().splitlines() if l])

    ctx = {}
    for name in ("failure_context_plant.jsonl", "failure_context_estimator.jsonl"):
        p = RUN / name
        if p.exists():
            d = json.loads(p.read_text())
            ctx[name] = {"events": len(d["events"]), "reason": d["reason"],
                         "first_has_state": "state" in d["events"][0] if d["events"] else False,
                         "counters": d.get("counters")}
        else:
            ctx[name] = None

    # estimator is logged at heartbeats AND at packet times, so every plant tick
    # must appear in the estimator stream, not the other way round.
    plant_ticks = {r["tick"] for r in plant}
    est_ticks = {r["tick"] for r in est}
    est_superset = plant_ticks.issubset(est_ticks)
    est_time_by_tick = {r["tick"]: r["time_s"] for r in est}
    tick_time_agree = all(est_time_by_tick.get(r["tick"]) == r["time_s"] for r in plant)

    result = {
        "run": str(RUN),
        "status": summary.get("status"),
        "reason": summary.get("reason"),
        "wall_s": summary.get("wall_s"),
        "phase": summary.get("phase"),
        "last_event_time_s": summary.get("last_event_time_s"),
        "transport_samples": summary.get("transport_samples"),
        "predictions": summary.get("estimator_predictions"),
        "updates": summary.get("estimator_updates"),
        "gt_control_state_reads": summary.get("GT_control_state_reads"),
        "logs": {
            "plant_rows": len(plant), "estimator_rows": len(est),
            "sensor_rows": len(sensors), "command_rows": len(commands),
            "settling_rows": len(settling),
            "plant_time_span": plant_span, "estimator_time_span": est_span,
            "plant_monotonic": plant_mono, "estimator_monotonic": est_mono,
            "plant_required_keys_all_rows": plant_required,
            "estimator_required_keys_all_rows": est_required,
            "plant_bulk_snapshots": plant_snap,
            "estimator_bulk_snapshots": est_snap,
            "suppressed_rows_have_no_W": plant_bulk_suppressed_clean,
            "observations_by_kind": dict(kinds),
            "events_by_type": dict(events),
            "plant_ticks_subset_of_estimator": est_superset,
            "tick_time_agreement": tick_time_agree,
        },
        "failure_context": ctx,
        "termination_reason": termination.get("reason") if termination else None,
        "termination_has_estimate": termination.get("last_estimate_state") is not None
        if termination else None,
        "termination_has_published_u": termination.get("last_published_U") is not None
        if termination else None,
        "files_sha256": {p.name: sha(p) for p in sorted(RUN.iterdir()) if p.is_file()},
    }

    checks = {
        "summary_present": summary is not None,
        "log_rows_consistent_with_summary": len(plant) == summary.get("transport_samples"),
        "plant_monotonic": plant_mono,
        "estimator_monotonic": est_mono,
        "plant_required_keys": plant_required,
        "estimator_required_keys": est_required,
        "suppressed_rows_clean": plant_bulk_suppressed_clean,
        "plant_ticks_subset_of_estimator": est_superset,
        "tick_time_agreement": tick_time_agree,
        "no_gt_feedback": summary.get("GT_control_state_reads") == 0,
        "failure_context_200": all(v and v["events"] == 200 for v in ctx.values()) if ctx else False,
        "termination_matches_summary": (termination or {}).get("reason") == summary.get("reason"),
    }
    result["checks"] = checks
    result["verdict"] = "PASS" if all(checks.values()) else "FAIL"
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for k, v in checks.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    print(json.dumps({k: result[k] for k in ("status", "reason", "wall_s",
                                             "transport_samples", "predictions", "updates")}))
    print("logs:", result["logs"]["plant_rows"], result["logs"]["estimator_rows"],
          "snapshots:", result["logs"]["plant_bulk_snapshots"],
          result["logs"]["estimator_bulk_snapshots"])
    print("context:", {k: (v or {}).get("events") for k, v in ctx.items()})
    print("verdict:", result["verdict"])
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
