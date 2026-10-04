"""[EXPERIMENTAL] 保留旧场景：正常五件供料，或前3/4件预置的局部回归。

只缩短测试准备过程；不能将预置前三件算作完整五件实测成功。
不改旧场景源码、夹具、材质或物理参数；采样由 PhysX post-step 驱动。
"""

import argparse
import builtins
from dataclasses import asdict
import json
import os
from pathlib import Path
import signal
import sys
import time


def fixture_ready(cube_states, preplaced_count, arrived_state):
    """正常供料必须等第一件真正到位，不能利用 all([]) 提前宣称 READY。"""
    if preplaced_count not in (0, 3, 4):
        raise ValueError("Unsupported preplaced count")
    required = max(1, preplaced_count)
    return len(cube_states) >= required and all(
        state == arrived_state for state in cube_states[:required])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--duration-sec", type=float, default=1000.0)
    parser.add_argument("--asset-root", required=True)
    parser.add_argument("--record-release-diagnostics", action="store_true",
                        help="Read-only full-rate contacts/tools ONLY inside release phases")
    parser.add_argument("--preplaced-count", type=int, choices=(0, 3, 4), default=3,
                        help="0 uses normal feed; 4 isolates Cube05; preplaced cubes are not executed")
    args = parser.parse_args()
    if args.duration_sec <= 0:
        parser.error("duration must be positive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    legacy_root = Path(os.environ.get(
        "TASK01_LEGACY_ROOT", "/home/ubuntu2004/lmy/dual-arm-embodied-palletizing"))
    from isaacsim import SimulationApp
    app = SimulationApp({"headless": True, "multi_gpu": False, "sync_loads": False,
                         "fast_shutdown": True})
    bridge = subscription = None
    stopping = False

    def request_stop(signum, frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    count, errors, latest = 0, [], None
    try:
        import numpy as np
        import omni.physx
        import omni.timeline
        import omni.usd
        from pxr import Gf, PhysxSchema
        import isaacsim.storage.native as storage
        from isaacsim.core.prims import RigidPrim
        import omni.physics.tensors as tensors
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from physics_object_sampler import PhysicsObjectSampler
        omni.usd.get_context().new_stage()
        namespace = {"_SIDE_SUCTION_SCENARIO": "task27"}
        source = legacy_root / "isaac/scripts/task26_truck_box_scene.py"
        original_discovery = storage.get_assets_root_path
        storage.get_assets_root_path = lambda: args.asset_root
        try:
            exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"),
                 namespace, namespace)
        finally:
            storage.get_assets_root_path = original_discovery
        stage = omni.usd.get_context().get_stage()
        if args.record_release_diagnostics:
            for index in range(1, 6):
                prim = stage.GetPrimAtPath(f"/World/Task27/Supply/Cube_{index:02d}")
                PhysxSchema.PhysxContactReportAPI.Apply(prim).CreateThresholdAttr(0.0)
        tool_values = {'tcp_y': namespace['TCP_Y'],
                       'vertical_drop_z': namespace['VERTICAL_DROP_Z']}
        cells = tuple(tuple(task["cell"]) for task in namespace["TASKS"][:args.preplaced_count])
        for index, center in enumerate(cells, start=1):
            prim = stage.GetPrimAtPath(f"/World/Task27/Supply/Cube_{index:02d}")
            if not prim.IsValid():
                raise RuntimeError("Original fixture cube missing")
            prim.GetAttribute("xformOp:translate:task26_pose").Set(Gf.Vec3d(*center))
            PhysxSchema.PhysxRigidBodyAPI.Apply(prim).CreateDisableGravityAttr().Set(False)
        timeline = omni.timeline.get_timeline_interface()
        timeline.play()
        for _ in range(120):
            app.update()
        source = legacy_root / "isaac/scripts/task26_truck_box_bridge.py"
        namespace = {"_SIDE_SUCTION_SCENARIO": "task27"}
        exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"),
             namespace, namespace)
        # BRANCH_SIGN 由原Bridge定义；长度由原scene定义，不能混用命名空间。
        tool_values['branch_sign'] = namespace['BRANCH_SIGN']
        bridge = builtins._task26_batched_feed_bridge
        # 不伪造 ARRIVED；复用原 bridge 的速度/位置落稳检测。
        with bridge._lock:
            # 正常五件回归保留 Bridge 的自动批1供料；只有预置夹具才取消它。
            if args.preplaced_count:
                bridge._pending_batch = None
            for index, cell in enumerate(cells):
                bridge.slot_pose[index] = cell
                bridge.cube_state[index] = namespace["STATE_ARRIVING"]
                bridge.stable_accum[index] = 0.0
                bridge.released_batches.add(index + 1)
        view = RigidPrim(list(bridge.cube_paths), reset_xform_properties=False,
                         prepare_contact_sensors=False)
        view.initialize()
        sampler = PhysicsObjectSampler(view)
        sim_view = tensors.create_simulation_view("numpy")
        sim_view.set_subspace_roots("/")
        materials = sim_view.create_rigid_body_view(list(bridge.cube_paths))
        (args.output_dir / "model_audit.json").write_text(json.dumps({
            "preplaced_count": args.preplaced_count, "preplaced_cells_m": cells,
            "cube_masses_kg": np.asarray(view.get_masses()).tolist(),
            "actual_material_columns": ["static_friction", "dynamic_friction", "restitution"],
            "actual_cube_materials": np.asarray(materials.get_material_properties()).tolist(),
            "scene_source": str(legacy_root / "isaac/scripts/task26_truck_box_scene.py"),
            "boundary": ("Normal feed; no cubes preplaced; placement completion requires controller PASS evidence"
                         if args.preplaced_count == 0 else
                         "Only non-preplaced cubes physically executed; no full-five proof")}, indent=2) + "\n")
        started = time.monotonic()
        ready = False
        diagnostics = None
        with (args.output_dir / "physics_pose_samples.jsonl").open("w") as stream, \
             (args.output_dir / "release_contact_samples.jsonl").open("w") as release_stream:
            if args.record_release_diagnostics:
                from release_diagnostics import ReleaseDiagnostics, active_cube_index
                diagnostics = ReleaseDiagnostics(bridge.node, sim_view, list(bridge.cube_paths),
                                                 tool_values, release_stream)
            steps = 0

            def post_step(dt):
                nonlocal count, latest, steps
                steps += 1
                record_release = diagnostics is not None and active_cube_index(diagnostics.phase) is not None
                if steps % 6 and not record_release:
                    return
                try:
                    snapshot = sampler.capture()
                    if diagnostics is not None:
                        diagnostics.capture(snapshot, float(dt), bridge.grippers)
                    if steps % 6:
                        return
                    latest = {"physics": asdict(snapshot),
                              "feed_state": list(bridge.cube_state),
                              "suction_closed": {side: bool(g.is_closed())
                                                 for side, g in bridge.grippers.items()}}
                    stream.write(json.dumps(latest, sort_keys=True) + "\n")
                    count += 1
                except Exception as error:
                    if not errors:
                        print("[TASK01 Cube04] sampler error:", repr(error), flush=True)
                    errors.append(repr(error))

            subscription = omni.physx.get_physx_interface().subscribe_physics_on_step_events(
                post_step, False, 200)
            while app.is_running() and not stopping and time.monotonic() - started < args.duration_sec:
                app.update()
                if errors:
                    raise RuntimeError("Stopping diagnostic after a physical readout error")
                if not ready and fixture_ready(bridge.cube_state, args.preplaced_count,
                                               namespace["STATE_ARRIVED"]):
                    ready = True
                    if args.preplaced_count == 0:
                        print("[TASK01 Cube04] READY: normal first feed physically arrived; "
                              "no cubes preplaced; run first_batch:=1 max_batches:=5", flush=True)
                    else:
                        print(f"[TASK01 Cube04] READY: first {args.preplaced_count} physically settled; "
                              f"run first_batch:={args.preplaced_count + 1} "
                              f"max_batches:=1 or {5 - args.preplaced_count}", flush=True)
        subscription.unsubscribe()
        subscription = None
        (args.output_dir / "summary.json").write_text(json.dumps({
            "ready": ready, "snapshots": count, "errors": errors,
            "wall_s": time.monotonic() - started, "final_snapshot": latest,
            "release_diagnostic_snapshots": diagnostics.count if diagnostics else 0}, indent=2) + "\n")
        if not ready or errors:
            raise RuntimeError("Fixture readiness / physical sampler validation failed")
    except Exception as error:
        import traceback
        traceback.print_exc()
        (args.output_dir / "failure.json").write_text(json.dumps({
            "error": repr(error), "traceback": traceback.format_exc()}, indent=2) + "\n")
        raise
    finally:
        if subscription is not None:
            subscription.unsubscribe()
        if bridge is not None:
            bridge.shutdown()
        app.close()


if __name__ == "__main__":
    main()
