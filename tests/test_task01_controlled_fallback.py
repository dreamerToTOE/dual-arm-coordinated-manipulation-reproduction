"""纯分类/范围测试，不是Isaac验收证据。"""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "platforms/isaac_ros2/probes"))
from task01_critical_controlled_replay_gui import CRITICAL, pair_classification


class ControlledFallbackContract(unittest.TestCase):
    def setUp(self):
        self.row = {"cube_environment_geometry": {"checks": [
            {"body2": "table", "volumetric_penetration": False, "signed_axis_aligned_distance_m": 0.},
            {"body2": "carriage_deep_wall", "volumetric_penetration": False, "signed_axis_aligned_distance_m": 0.},
            {"body2": "carriage_plus_y_wall", "volumetric_penetration": False, "signed_axis_aligned_distance_m": .2},
        ]}}

    def test_only_four_recorded_states(self):
        self.assertEqual([s[1] for s in CRITICAL], [0, 135, 196, 292])

    def test_target_boundary_expected_not_redefined(self):
        category, reason = pair_classification(["shared_cube", "carriage_deep_wall"], self.row, {})
        self.assertEqual(category, "EXPECTED_CONTACT")
        self.assertIn("pending_user_definition", reason)

    def test_support_expected(self):
        self.assertEqual(pair_classification(["table", "shared_cube"], self.row, {})[0], "EXPECTED_CONTACT")

    def test_robot_environment_not_allowed(self):
        for robot in ("left_fr3_link7", "right_fr3_link8", "left_fr3_side_suction"):
            for env in ("table", "carriage_deep_wall", "carriage_plus_y_wall", "carriage_minus_y_wall"):
                self.assertEqual(pair_classification([robot, env], self.row, {})[0], "UNEXPECTED_PAIR")

    def test_existing_acm_only(self):
        acm = {("left_fr3_link7", "left_fr3_link8"): "Adjacent"}
        self.assertEqual(pair_classification(["left_fr3_link8", "left_fr3_link7"], self.row, acm),
                         ("EXPECTED_CONTACT", "original_SRDF:Adjacent"))
        self.assertEqual(len(acm), 1)

    def test_cube_sidewall_not_nominal_expected(self):
        self.assertEqual(pair_classification(["shared_cube", "carriage_plus_y_wall"], self.row, {})[0], "UNEXPECTED_PAIR")

    def test_cube_volumetric_penetration_not_boundary(self):
        self.row["cube_environment_geometry"]["checks"][1]["volumetric_penetration"] = True
        self.assertEqual(pair_classification(["shared_cube", "carriage_deep_wall"], self.row, {})[0], "UNEXPECTED_PAIR")


if __name__ == "__main__":
    unittest.main()
