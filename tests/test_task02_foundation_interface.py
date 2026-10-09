"""离线接口验收：历史成功快照仅为转换 oracle，不重跑物理。"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from common.interfaces import ObservationClock, Pose
from platforms.isaac_ros2.foundation.legacy_task26 import (
    convert_snapshot, load_manifest, verify_legacy_assets,
)


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "results/20261009_TASK01_predecessor_patched_runtime02/final_snapshot.json"


class FoundationInterfaceTest(unittest.TestCase):
    def setUp(self):
        self.envelope = json.loads(SNAPSHOT.read_text())
        self.data = json.loads(self.envelope["output"])
        self.ids = load_manifest()["cube_ids"]

    def converted(self, data=None, ids=None):
        return convert_snapshot(
            {"status": "ok", "output": json.dumps(self.data if data is None else data)},
            self.ids if ids is None else ids,
        )

    def test_real_success_snapshot_preserves_values_and_sources(self):
        result = self.converted()
        state = result["state"]
        self.assertEqual(result["schema_version"], "task02.state.v0.1")
        for side in ("left", "right"):
            arm = state["arms"][side]
            self.assertEqual(tuple(self.data["q"][side][:7]), arm["positions_rad"])
            self.assertEqual(tuple(self.data["q_velocity"][side][:7]), arm["velocities_rad_s"])
            self.assertEqual(arm["base_pose"]["measurement_source"], "native_articulation")
            self.assertEqual(arm["tcp_pose"]["measurement_source"], "legacy_USD_feedback")
        self.assertEqual(len(state["objects"]), 4)  # 休眠件也保留，不偷改旧场景。
        self.assertEqual(state["objects"][0]["object_id"], self.ids[0])
        self.assertEqual(state["objects"][0]["pose"]["position_m"], tuple(self.data["cube_poses"][0]["position"]))
        self.assertEqual(result["diagnostics"]["SG"], {"left": False, "right": False})
        self.assertIn("collision_distance", result["unavailable"])
        self.assertIn("attachment_identity", result["unavailable"])

    def test_legacy_clock_is_not_upgraded(self):
        clock = self.converted()["state"]["clock"]
        self.assertFalse(clock["post_physics_step"])
        self.assertIsNone(clock["physics_step"])
        self.assertIsNone(clock["simulation_stamp_ns"])
        self.assertEqual(clock["diagnostic_ros_clock_ns"], self.data["ros_clock_nanoseconds"])
        with self.assertRaises(ValueError):
            ObservationClock(**clock).require_scientific_timestamp()

    def test_real_post_step_contract_requires_both_native_fields(self):
        with self.assertRaises(ValueError):
            ObservationClock(post_physics_step=True, simulation_stamp_ns=10)
        with self.assertRaises(ValueError):
            ObservationClock(simulation_stamp_ns=10, physics_step=1)
        with self.assertRaises(ValueError):
            ObservationClock(post_physics_step=True, simulation_stamp_ns=True, physics_step=1)
        self.assertEqual(ObservationClock(10, 1, True).require_scientific_timestamp(), 10)

    def test_native_wxyz_is_explicitly_converted(self):
        data = deepcopy(self.data)
        data["base_world_pose_native"]["left"]["quaternion_wxyz"] = [0.5, 0.5, 0.5, -0.5]
        pose = self.converted(data)["state"]["arms"]["left"]["base_pose"]
        self.assertEqual(pose["quaternion_xyzw"], (0.5, 0.5, -0.5, 0.5))

    def test_joint_identity_not_array_position_controls_mapping(self):
        data = deepcopy(self.data)
        for key in ("dof_names", "q", "q_velocity"):
            data[key]["left"] = list(reversed(data[key]["left"]))
        self.assertEqual(self.converted(data)["state"]["arms"]["left"],
                         self.converted()["state"]["arms"]["left"])

    def test_missing_or_duplicate_joint_identity_rejected(self):
        for name in ("unknown", "fr3_joint2"):
            data = deepcopy(self.data)
            data["dof_names"]["left"][0] = name
            with self.assertRaises(ValueError):
                self.converted(data)

    def test_q_length_nan_inf_and_boolean_rejected(self):
        data = deepcopy(self.data)
        data["q"]["left"].pop()
        with self.assertRaises(ValueError):
            self.converted(data)
        for value in (float("nan"), float("inf"), True):
            data = deepcopy(self.data)
            data["q"]["left"][0] = value
            with self.assertRaises(ValueError):
                self.converted(data)

    def test_no_object_identity_guessing(self):
        with self.assertRaises(ValueError):
            self.converted(ids=self.ids[:2])
        with self.assertRaises(ValueError):
            self.converted(ids=[self.ids[0]] * 4)

    def test_wrong_frame_or_invalid_pose_rejected(self):
        data = deepcopy(self.data)
        data["frame_id"] = "base"
        with self.assertRaises(ValueError):
            self.converted(data)
        data = deepcopy(self.data)
        data["cube_poses"][0]["quaternion_xyzw"] = [0, 0, 0, 0]
        with self.assertRaises(ValueError):
            self.converted(data)
        with self.assertRaises(ValueError):
            Pose("", (0, 0, 0), (0, 0, 0, 1), "USD")

    def test_failed_envelope_is_not_a_snapshot(self):
        with self.assertRaises(ValueError):
            convert_snapshot({"status": "error", "output": self.envelope["output"]}, self.ids)

    def test_callbacks_errors_are_preserved_not_claimed_as_safety(self):
        data = deepcopy(self.data)
        data["physics_errors"] = {"left": "callback failed"}
        output = self.converted(data)
        self.assertEqual(output["diagnostics"]["physics_errors"], data["physics_errors"])
        self.assertNotIn("collision_free", output)

    def test_asset_hash_guard_pass_and_mismatch(self):
        with tempfile.TemporaryDirectory(prefix="task02-source-test-") as directory:
            path = Path(directory) / "asset"
            path.write_bytes(b"approved")  # 临时测试 fixture，绝不写旧工程。
            manifest = {"assets": {"asset": hashlib.sha256(b"approved").hexdigest()}}
            self.assertEqual(verify_legacy_assets(directory, manifest), manifest["assets"])
            path.write_bytes(b"changed")
            with self.assertRaises(ValueError):
                verify_legacy_assets(directory, manifest)

    def test_asset_path_escape_and_empty_set_rejected(self):
        with tempfile.TemporaryDirectory(prefix="task02-source-test-") as directory:
            outside = Path(directory) / "outside"
            outside.write_bytes(b"data")
            root = Path(directory) / "root"
            root.mkdir()
            manifest = {"assets": {"../outside": hashlib.sha256(b"data").hexdigest()}}
            with self.assertRaises(ValueError):
                verify_legacy_assets(root, manifest)
            with self.assertRaises(ValueError):
                verify_legacy_assets(root, {"assets": {}})

    def test_manifest_keeps_engineering_qualification_separate(self):
        manifest = load_manifest()
        self.assertEqual(manifest["scientific_benchmark_status"], "DRAFT_NOT_FROZEN")
        self.assertNotEqual(manifest["base_commit"], manifest["approved_runtime_commit"])
        self.assertEqual(len(manifest["assets"]), 4)


if __name__ == "__main__":
    unittest.main()
