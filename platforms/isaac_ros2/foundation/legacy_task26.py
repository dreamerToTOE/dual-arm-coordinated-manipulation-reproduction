"""原地复用 Task26；只读文件，绝不启动 GUI/ROS 或发送命令。

Task26@631b1f + 已批准 5ed0c96 是工程来源，不是论文算法。
旧快照中的 USD / native base / ROS clock 分别保留来源，不伪造 post-step 同步。
"""

import argparse
import hashlib
import json
from pathlib import Path

from common.interfaces import ArmState, DualArmState, ObjectState, ObservationClock, Pose, StateRecord
from common.interfaces.state import finite_vector


MANIFEST_PATH = Path(__file__).with_name("legacy_task26_manifest.json")
ARM_JOINT_NAMES = tuple(f"fr3_joint{i}" for i in range(1, 8))


def load_manifest(path=MANIFEST_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify_legacy_assets(root, manifest):
    """严格比对已验收字节；不自动修补、复制、编译或切换旧 worktree。"""
    root = Path(root).resolve(strict=True)
    verified = {}
    for relative_path, expected in manifest["assets"].items():
        path = (root / relative_path).resolve(strict=True)
        if not path.is_relative_to(root):
            raise ValueError(f"asset escapes declared root: {relative_path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"source mismatch: {relative_path}: expected={expected}, actual={actual}")
        verified[relative_path] = actual
    if not verified:
        raise ValueError("empty source asset set")
    return verified


def _pose(data, frame_id, source, native_wxyz=False):
    key = "quaternion_wxyz" if native_wxyz else "quaternion_xyzw"
    quat = tuple(data[key])
    finite_vector(quat, 4)
    if native_wxyz:
        quat = (quat[1], quat[2], quat[3], quat[0])
    return Pose(frame_id, tuple(data["position"]), quat, source)


def convert_snapshot(envelope, cube_ids):
    """只转换明确的旧快照格式；cube_ids 显式绑定，不猜对象身份。"""
    if envelope.get("status") != "ok" or not isinstance(envelope.get("output"), str):
        raise ValueError("expected successful GUI executor snapshot envelope")
    data = json.loads(envelope["output"])
    if data["frame_id"] != "world":
        raise ValueError("Task26 snapshot must explicitly use world frame")
    if len(cube_ids) != len(data["cube_poses"]):
        raise ValueError("object identity mapping does not match pose count")
    clock = ObservationClock(
        legacy_timeline_time_sec=data["timeline_time_sec"],
        diagnostic_ros_clock_ns=data["ros_clock_nanoseconds"],
    )
    arms = {}
    for side in ("left", "right"):
        names = data["dof_names"][side]
        if len(set(names)) != len(names):
            raise ValueError("duplicate legacy DOF name")
        q, dq = data["q"][side], data["q_velocity"][side]
        finite_vector(q, len(names))
        finite_vector(dq, len(names))
        if any(name not in names for name in ARM_JOINT_NAMES):
            raise ValueError("missing explicit FR3 arm joint identity")
        indices = [names.index(name) for name in ARM_JOINT_NAMES]
        arms[side] = ArmState(
            arm_id=side, joint_names=ARM_JOINT_NAMES,
            positions_rad=tuple(q[i] for i in indices),
            velocities_rad_s=tuple(dq[i] for i in indices),
            base_pose=_pose(data["base_world_pose_native"][side], "world", "native_articulation", True),
            tcp_pose=_pose(data["tcp_poses"][side], "world", "legacy_USD_feedback"),
        )
        # 无 scientific world_shift 字段，不由轨道坐标反推它。
        finite_vector((data["rails"][side], data["rail_targets"][side]))
        if not isinstance(data["SG"][side], bool) or not isinstance(data["rail_arrived"][side], bool):
            raise ValueError("legacy SG/rail state must be boolean")
    state = StateRecord(clock, DualArmState(arms["left"], arms["right"]), tuple(
        ObjectState(object_id, _pose(pose, "world", "legacy_USD_feedback"))
        for object_id, pose in zip(cube_ids, data["cube_poses"])
    ))
    output = state.to_dict()
    output["evidence_class"] = "LEGACY_ASYNCHRONOUS_ENGINEERING_SNAPSHOT"
    output["diagnostics"] = {key: data[key] for key in (
        "label", "timestamp_limit", "rails", "rail_targets", "rail_arrived", "SG", "feed", "physics_errors"
    )}
    output["unavailable"] = ["atomic_post_physics_state", "world_shift_x", "collision_distance",
                             "contact_wrench", "attachment_identity", "carriage_frame"]
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--legacy-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest()
        assets = verify_legacy_assets(args.legacy_root, manifest)
        raw = args.snapshot.read_bytes()
        output = convert_snapshot(json.loads(raw), manifest["cube_ids"])
        output["provenance"] = {
            "manifest": manifest, "verified_local_assets": assets,
            "raw_snapshot_sha256": hashlib.sha256(raw).hexdigest(),
            "scope": "local asset bytes only; historical snapshot origin is not cryptographically attested",
        }
        print(json.dumps(output, ensure_ascii=False, allow_nan=False, indent=2))
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(1, f"TASK02-A read-only adapter STOP: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
