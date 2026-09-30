"""Task01 probe wrapper for legacy Task27 ROS bridge.

The pre-placed cubes use the existing arrival/settle detector. No fake ARRIVED
flag is published before they physically settle at their cell locations.
"""

import builtins
import json
import os
from pathlib import Path


LEGACY_ROOT = Path(os.environ.get(
    "TASK01_LEGACY_ROOT", "/home/ubuntu2004/lmy/dual-arm-embodied-palletizing"
))
BRIDGE_SOURCE = LEGACY_ROOT / "isaac/scripts/task26_truck_box_bridge.py"


def start_bridge():
    if not BRIDGE_SOURCE.is_file():
        raise FileNotFoundError(f"Legacy Task27 bridge source missing: {BRIDGE_SOURCE}")
    legacy = {"_SIDE_SUCTION_SCENARIO": "task27"}
    exec(compile(BRIDGE_SOURCE.read_text(encoding="utf-8"), str(BRIDGE_SOURCE), "exec"),
         legacy, legacy)
    bridge = builtins._task26_batched_feed_bridge
    if bridge.stage.GetPrimAtPath("/World/Task27").GetCustomDataByKey("task01_probe") != \
            "four_cubes_preplaced_center_pending":
        bridge.shutdown()
        raise RuntimeError("Task01 fixture scene marker missing; refusing to fake feed state")

    fixture_cells = []
    for index in range(4):
        prim = bridge.stage.GetPrimAtPath(bridge.cube_paths[index])
        meta = prim.GetCustomDataByKey("task26_metadata")
        if meta is None:
            bridge.shutdown()
            raise RuntimeError(f"Missing fixture metadata: {bridge.cube_paths[index]}")
        fixture_cells.append(tuple(float(value) for value in json.loads(meta)["cell_pose"]))

    with bridge._lock:
        # The unmodified bridge auto-feeds batch 1. Disable it for this probe.
        bridge._pending_batch = None
        for index, cell in enumerate(fixture_cells):
            bridge.slot_pose[index] = cell
            bridge.cube_state[index] = legacy["STATE_ARRIVING"]
            bridge.stable_accum[index] = 0.0
            bridge.released_batches.add(index + 1)
    print("[TASK01 fixture] Bridge waiting for Cubes 01–04 to settle at their actual cells.")
    print("[TASK01 fixture] Only feed batch 5 may move Cube_05 into the supply slot.")
    return bridge


if __name__ == "__main__":
    start_bridge()
