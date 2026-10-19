#!/usr/bin/env python3
"""T04-B: mode B coupled closed-loop simulation, 5s settle + 7.5s transport.
Uses the stable propagation (ADAPTED_STABLE_PROPAGATION_V1) for the estimator
and the original native plant + PoseForceController. Original Q/R, gains,
sensors, gates and clocks. GT only for scoring."""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from run_p2_closed_loop import run_case
from baselines.p2_pose_force.native_model import NativeModel, build_native

CONFIRM = "case11-exp3-seed7-A-modeB"
MAX_TRANSPORT = 7.5
MAX_WALL = 120.0
CASE = {"id": 11, "condition": "exp3", "seed": 7, "variant": "transport",
        "GT": False, "scale": 1}
SOURCES = ["scripts/run_p2_closed_loop.py", "scripts/p2_event_log.py",
           "baselines/p2_pose_force/stable_propagation.py",
           "baselines/p2_pose_force/estimator.py",
           "baselines/p2_pose_force/mechanics.py",
           "baselines/p2_pose_force/contact_geometry.py",
           "baselines/p2_pose_force/native_kernel.cpp",
           "configs/p2_closed_loop_protocol_v3.json"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", required=True)
    ap.add_argument("--transport-limit-s", type=float, default=MAX_TRANSPORT)
    ap.add_argument("--wall-cap-s", type=float, default=MAX_WALL)
    a = ap.parse_args()
    if a.confirm != CONFIRM:
        print(f"refused: --confirm must be {CONFIRM!r}", file=sys.stderr); return 2
    if not (0 < a.transport_limit_s <= MAX_TRANSPORT):
        print(f"refused: transport limit must be in (0, {MAX_TRANSPORT}]", file=sys.stderr); return 2
    if not (0 < a.wall_cap_s <= MAX_WALL):
        print(f"refused: wall cap must be in (0, {MAX_WALL}]", file=sys.stderr); return 2

    cfg_path = ROOT / "configs" / "p2_closed_loop_protocol_v3.json"
    cfg = json.loads(cfg_path.read_text())
    run_id = time.strftime("%Y%m%d_%H%M%S") + "_T04_B_COUPLED_7P5_case11"
    out = ROOT / "p2" / "runs" / run_id
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    native = NativeModel(build_native("/home/ubuntu2004/lmy/.p2_native_build_v3"))
    started = time.perf_counter()
    try:
        summary = run_case(cfg, CASE, out, native, started, 0.0,
                           transport_limit_s=a.transport_limit_s,
                           wall_limit_s=a.wall_cap_s,
                           propagation_mode="B")
    except Exception as exc:
        print(f"infrastructure failure: {exc!r}", file=sys.stderr); return 1
    wall = time.perf_counter() - started
    manifest = {"kind": "T04_B_COUPLED_SIMULATION", "run_id": run_id,
                "case": CASE, "transport_limit_s": a.transport_limit_s,
                "wall_cap_s": a.wall_cap_s, "propagation_mode": "B",
                "git_commit": commit, "command": sys.argv,
                "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                                  for p in SOURCES},
                "wall_s": wall, "summary": summary,
                "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(out.iterdir()) if p.is_file()}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"run_id": run_id, "status": summary.get("status"),
                      "reason": summary.get("reason"), "wall_s": round(wall, 2),
                      "last_transport_t": summary.get("last_transport_log_time_s")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
