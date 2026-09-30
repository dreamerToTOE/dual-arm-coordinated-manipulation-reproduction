"""Task01 probe: load legacy Task27 and pre-place only its first four cubes.

Run while the Isaac timeline is stopped. The fifth cube remains parked for the
normal Task27 feed command. This is an EXPERIMENTAL shortcut, not benchmark A.
"""

import os
from pathlib import Path

from pxr import Gf, PhysxSchema
import omni.usd


LEGACY_ROOT = Path(os.environ.get(
    "TASK01_LEGACY_ROOT", "/home/ubuntu2004/lmy/dual-arm-embodied-palletizing"
))
SCENE_SOURCE = LEGACY_ROOT / "isaac/scripts/task26_truck_box_scene.py"


def build_scene():
    if not SCENE_SOURCE.is_file():
        raise FileNotFoundError(f"Legacy Task27 scene source missing: {SCENE_SOURCE}")
    legacy = {"_SIDE_SUCTION_SCENARIO": "task27"}
    exec(compile(SCENE_SOURCE.read_text(encoding="utf-8"), str(SCENE_SOURCE), "exec"),
         legacy, legacy)

    stage = omni.usd.get_context().get_stage()
    if stage is None:
        raise RuntimeError("Isaac has no USD stage")
    cells = tuple(tuple(task["cell"]) for task in legacy["TASKS"][:4])
    for index, center in enumerate(cells, start=1):
        path = f"/World/Task27/Supply/Cube_{index:02d}"
        prim = stage.GetPrimAtPath(path)
        if not prim.IsValid():
            raise RuntimeError(f"Missing fixture cube: {path}")
        pose = prim.GetAttribute("xformOp:translate:task26_pose")
        if not pose.IsValid():
            raise RuntimeError(f"Missing pose attribute: {path}")
        pose.Set(Gf.Vec3d(*center))
        PhysxSchema.PhysxRigidBodyAPI.Apply(prim).CreateDisableGravityAttr().Set(False)
        print(f"[TASK01 fixture] Cube_{index:02d} -> {center}")

    parked = stage.GetPrimAtPath("/World/Task27/Supply/Cube_05")
    if not parked.IsValid():
        raise RuntimeError("Cube_05 missing from Task27 source scene")
    task_root = stage.GetPrimAtPath("/World/Task27")
    task_root.SetCustomDataByKey("task01_probe", "four_cubes_preplaced_center_pending")
    print("[TASK01 fixture] Four cubes pre-placed; Cube_05 stays parked for feed batch 5.")
    return cells


if __name__ == "__main__":
    build_scene()
