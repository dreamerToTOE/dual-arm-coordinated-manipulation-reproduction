#!/usr/bin/env python3
"""Bounded single-case diagnostic entry (T01-E smoke).

Hard-wired to case id 11 / exp3 / seed 7 / object A, original
PAPER_LITERAL_EULER, original gains, clocks and gates. It deliberately has no
case list and no loop: it can only ever run this one case. Every limit is
fail-closed and validated before any work starts.

Usage
    /usr/bin/python3.10 p2/tools/run_p2_smoke.py \
        --confirm case11-exp3-seed7-A --transport-limit-s 4.5 --wall-cap-s 60

Exit codes: 0 = the run produced a summary (scientific FAIL_STOP included),
1 = infrastructure failure, 2 = refused arguments.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from run_p2_closed_loop import run_case                        # noqa: E402
from baselines.p2_pose_force.native_model import build_native, NativeModel  # noqa: E402

CONFIRM = "case11-exp3-seed7-A"
MAX_TRANSPORT_S = 4.5
MAX_WALL_S = 60.0
CASE = {"id": 11, "condition": "exp3", "seed": 7, "variant": "transport",
        "GT": False, "scale": 1}
SOURCES = [
    "scripts/run_p2_closed_loop.py", "scripts/p2_event_log.py",
    "baselines/p2_pose_force/contact_geometry.py",
    "baselines/p2_pose_force/mechanics.py",
    "baselines/p2_pose_force/estimator.py",
    "baselines/p2_pose_force/observations.py",
    "baselines/p2_pose_force/native_model.py",
    "baselines/p2_pose_force/native_kernel.cpp",
    "configs/p2_closed_loop_protocol_v3.json",
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", required=True)
    ap.add_argument("--transport-limit-s", type=float, default=MAX_TRANSPORT_S)
    ap.add_argument("--wall-cap-s", type=float, default=MAX_WALL_S)
    args = ap.parse_args()

    # ---- fail-closed guards ------------------------------------------------
    if args.confirm != CONFIRM:
        print(f"refused: --confirm must be exactly {CONFIRM!r}", file=sys.stderr)
        return 2
    if not (0 < args.transport_limit_s <= MAX_TRANSPORT_S):
        print(f"refused: transport-limit-s must be in (0, {MAX_TRANSPORT_S}]", file=sys.stderr)
        return 2
    if not (0 < args.wall_cap_s <= MAX_WALL_S):
        print(f"refused: wall-cap-s must be in (0, {MAX_WALL_S}]", file=sys.stderr)
        return 2
    assert CASE == {"id": 11, "condition": "exp3", "seed": 7, "variant": "transport",
                    "GT": False, "scale": 1}

    cfg_path = ROOT / "configs" / "p2_closed_loop_protocol_v3.json"
    cfg = json.loads(cfg_path.read_text())
    run_id = time.strftime("%Y%m%d_%H%M%S") + "_T01E_SMOKE_case11_exp3_seed7"
    out = ROOT / "p2" / "runs" / run_id
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    preflight = {
        "kind": "ENGINEERING_SMOKE",
        "run_id": run_id,
        "case": CASE,
        "transport_limit_s": args.transport_limit_s,
        "wall_cap_s": args.wall_cap_s,
        "command": sys.argv,
        "git_commit": commit,
        "source_sha256": {p: sha(ROOT / p) for p in SOURCES},
        "config_sha256": sha(cfg_path),
        "started_unix": time.time(),
        "predictor": "PAPER_LITERAL_EULER",
        "gt_feedback": False,
    }

    native = NativeModel(build_native("/home/ubuntu2004/lmy/.p2_native_build_v3"))
    started = time.perf_counter()
    try:
        summary = run_case(cfg, CASE, out, native, started, 0.0,
                           transport_limit_s=args.transport_limit_s,
                           wall_limit_s=args.wall_cap_s)
    except Exception as exc:                     # infrastructure failure
        print(f"infrastructure failure: {exc!r}", file=sys.stderr)
        return 1

    wall = time.perf_counter() - started
    manifest = dict(preflight)
    manifest.update({
        "status": summary.get("status"),
        "reason": summary.get("reason"),
        "wall_s": wall,
        "summary": summary,
        "files_sha256": {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()},
    })
    (out / "smoke_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": run_id, "status": summary.get("status"),
                      "reason": summary.get("reason"), "wall_s": round(wall, 3),
                      "out": str(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
