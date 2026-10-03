"""Run the Task01 center-only fixture probe in Isaac Sim 4.5 standalone.

Start this with Isaac's python.sh, without sourcing the system ROS setup.
The runner loads only the scene and bridge; ROS/MoveIt test commands are run
separately after it prints READY.
"""

import argparse
import math
import sys
import time
from pathlib import Path


def report_cube05_pose_sources(bridge):
    """Compare PhysX rigid pose with the legacy USD-to-ROS pose, without mutation."""
    rigid_position, rigid_wxyz = bridge.rigids[4].get_world_pose()
    message = bridge._pose(bridge.cube_paths[4])
    from pxr import Usd, UsdGeom
    matrix = UsdGeom.Xformable(bridge.stage.GetPrimAtPath(bridge.cube_paths[4])).ComputeLocalToWorldTransform(
        Usd.TimeCode.Default())
    clean = matrix.RemoveScaleShear().ExtractRotationQuat()
    clean_xyzw = tuple(float(v) for v in clean.GetImaginary()) + (float(clean.GetReal()),)
    usd_position = (message.position.x, message.position.y, message.position.z)
    rigid_position = tuple(float(value) for value in rigid_position)
    usd_xyzw = (message.orientation.x, message.orientation.y,
                message.orientation.z, message.orientation.w)
    rigid_xyzw = tuple(float(rigid_wxyz[index]) for index in (1, 2, 3, 0))
    dot = abs(sum(a * b for a, b in zip(usd_xyzw, rigid_xyzw)))
    dot /= max(1e-12, math.sqrt(sum(a * a for a in usd_xyzw) *
                                sum(b * b for b in rigid_xyzw)))
    angle_deg = math.degrees(2.0 * math.acos(min(1.0, dot)))
    clean_dot = abs(sum(a * b for a, b in zip(clean_xyzw, rigid_xyzw)))
    clean_dot /= max(1e-12, math.sqrt(sum(a * a for a in clean_xyzw) *
                                    sum(b * b for b in rigid_xyzw)))
    clean_angle_deg = math.degrees(2 * math.acos(min(1.0, clean_dot)))
    position_mm = math.dist(usd_position, rigid_position) * 1000.0
    print(
        "[TASK01 pose-source-check] Cube_05 "
        f"PhysX={tuple(round(v, 6) for v in rigid_position)} "
        f"USD={tuple(round(v, 6) for v in usd_position)} "
        f"delta_position={position_mm:.3f} mm "
        f"delta_orientation={angle_deg:.4f} deg "
        f"delta_scale_removed_orientation={clean_angle_deg:.4f} deg",
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-sec", type=float, default=600.0)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--physics-measurements", action="store_true")
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
        physics_publisher = None
        if args.physics_measurements:
            sys.path.insert(0, str(root.parent))
            from isaacsim.core.prims import RigidPrim
            from physics_object_sampler import PhysicsObjectSampler, PhysicsPosePublisher
            view = RigidPrim(list(bridge.cube_paths), reset_xform_properties=False,
                             prepare_contact_sensors=False)
            view.initialize()
            if tuple(view.prim_paths) != tuple(bridge.cube_paths):
                raise RuntimeError("Physics view changed Cube ordering")
            physics_publisher = PhysicsPosePublisher(bridge.node, PhysicsObjectSampler(view))
            print("[TASK01 physics] PUB /task01/physics/cube_poses: PhysX post-step, simulation stamp",
                  flush=True)

        started = time.monotonic()
        last_pose_check = started
        ready = False
        try:
            while app.is_running() and time.monotonic() - started < args.duration_sec:
                app.update()
                now = time.monotonic()
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
                if ready and bridge.cube_state[4] == 2 and now - last_pose_check >= 10.0:
                    report_cube05_pose_sources(bridge)
                    last_pose_check = now
        except KeyboardInterrupt:
            print("[TASK01 fixture] interrupted after experiment", flush=True)
        finally:
            if physics_publisher is not None:
                physics_publisher.close()
                print(f"[TASK01 physics] snapshots={physics_publisher.snapshots}, "
                      f"errors={physics_publisher.errors}", flush=True)
            if ready:
                report_cube05_pose_sources(bridge)
            bridge.shutdown()
            timeline.stop()
        if not ready:
            raise RuntimeError("Fixture did not reach a settled ready state")
        if physics_publisher is not None and physics_publisher.errors:
            raise RuntimeError("Physics measurement callbacks failed")
    except Exception:
        import traceback
        traceback.print_exc()
        app.set_setting("/app/fastShutdown", False)
        raise
    finally:
        app.close()


if __name__ == "__main__":
    main()
