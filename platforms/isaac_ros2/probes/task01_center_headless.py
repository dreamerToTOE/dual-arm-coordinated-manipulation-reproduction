"""Run the Task01 center-only fixture probe in Isaac Sim 4.5 standalone.

Start this with Isaac's python.sh, without sourcing the system ROS setup.
The runner loads only the scene and bridge; ROS/MoveIt test commands are run
separately after it prints READY.
"""

import argparse
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-sec", type=float, default=600.0)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    from isaacsim import SimulationApp
    app = SimulationApp({
        "headless": True,
        "renderer": "RaytracedLighting",
        "anti_aliasing": 0,
        "multi_gpu": False,
        "sync_loads": False,
        "fast_shutdown": True,
    })
    try:
        import omni.timeline
        import omni.usd

        root = Path(__file__).resolve().parent
        omni.usd.get_context().new_stage()
        scene = {"__name__": "task01_probe_scene"}
        source = root / "task01_center_fixture_scene.py"
        exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"),
             scene, scene)
        cells = scene["build_scene"]()

        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        for _ in range(120):
            app.update()

        bridge_code = root / "task01_center_fixture_bridge.py"
        bridge_module = {"__name__": "task01_probe_bridge"}
        exec(compile(bridge_code.read_text(encoding="utf-8"),
                     str(bridge_code), "exec"), bridge_module, bridge_module)
        bridge = bridge_module["start_bridge"]()

        started = time.monotonic()
        ready = False
        while app.is_running() and time.monotonic() - started < args.duration_sec:
            app.update()
            if not ready and all(state == 2 for state in bridge.cube_state[:4]):
                for index, target in enumerate(cells):
                    actual, _ = bridge.rigids[index].get_world_pose()
                    error = sum((float(actual[axis]) - target[axis]) ** 2
                                for axis in range(3)) ** 0.5
                    print(f"[TASK01 fixture] Cube_{index + 1:02d} settled pose error "
                          f"= {error * 1000:.3f} mm", flush=True)
                print("[TASK01 fixture] READY: four physical cubes settled; "
                      "run Task27 first_batch:=5 max_batches:=1.", flush=True)
                ready = True
                if args.verify_only:
                    break
        if not ready:
            raise RuntimeError("Fixture did not reach a settled ready state")
        bridge.shutdown()
        timeline.stop()
    finally:
        app.close()


if __name__ == "__main__":
    main()
