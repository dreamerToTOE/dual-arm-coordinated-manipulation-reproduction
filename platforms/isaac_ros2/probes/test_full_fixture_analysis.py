"""Unit checks for signs, reference shifts and quaternion handling only."""

import unittest

import numpy as np

from analyze_full_fixture import rotation_xyzw, static_excess_wrench, suction_face, support_statistics


class ReactionTests(unittest.TestCase):
    def setUp(self):
        paths = [f"/World/left_fr3/{name}" for name in
                 ("fr3_link8", "fr3_hand", "fr3_leftfinger", "fr3_rightfinger", "fr3_hand_tcp")]
        self.topology = {"left": {"link_paths": [paths], "masses_kg": [[1., 0, 0, 0, 0]],
            "com_poses": [[[.1, 0, 0, 0, 0, 0, 1]] + [[0, 0, 0, 0, 0, 0, 1]]*4]},
            "incoming_joint_frames_authored": {paths[0]: {"joint_type": "PhysicsFixedJoint",
                "child_local_anchor_m_authored": [0, 0, 0],
                "child_local_joint_quaternion_xyzw": [0, 0, 0, 1]}}}
        self.row = {"articulations": {"left": {
            "link_poses_world_xyzw": [[[0, 0, 0, 0, 0, 0, 1]]*5],
            "incoming_joint_wrench_raw": [[[0, 0, 9.81, 0, -.981, 0]] + [[0]*6]*4]}},
            "tcp_poses_world_from_physics_link8": {"left": {"position_m": [.2, 0, 0]}}}

    def test_empty_gravity_and_com_moment(self):
        np.testing.assert_allclose(static_excess_wrench(self.row, self.topology, "left"), 0, atol=1e-12)

    def test_payload_shift_about_tcp(self):
        # Extra +Z load applied at the TCP has -Y moment at the anchor.
        self.row["articulations"]["left"]["incoming_joint_wrench_raw"][0][0][2] += 5
        self.row["articulations"]["left"]["incoming_joint_wrench_raw"][0][0][4] -= 1
        np.testing.assert_allclose(static_excess_wrench(self.row, self.topology, "left"),
                                   [0, 0, 5, 0, 0, 0], atol=1e-12)

    def test_reference_change_rejected(self):
        frame = self.topology["incoming_joint_frames_authored"]["/World/left_fr3/fr3_link8"]
        frame["child_local_anchor_m_authored"] = [0, 0, .01]
        with self.assertRaises(ValueError):
            static_excess_wrench(self.row, self.topology, "left")

    def test_rotation_scale_is_not_orientation(self):
        np.testing.assert_allclose(rotation_xyzw([0, 0, 2**-.5, 2**-.5]),
                                   [[0, -1, 0], [1, 0, 0], [0, 0, 1]], atol=1e-12)
        with self.assertRaises(ValueError):
            rotation_xyzw([0, 0, 0, 0])

    def test_face_association_requires_inward_cup_normal(self):
        body = {"position_m": [0, 0, 0], "quaternion_xyzw": [0, 0, 0, 1]}
        rear = {"position_m": [-.061, 0, 0], "quaternion_xyzw": [0, 0, 0, 1]}
        self.assertEqual(suction_face(rear, body), "-X")
        rear["quaternion_xyzw"] = [0, 0, 1, 0]
        self.assertIsNone(suction_face(rear, body))
        side = {"position_m": [0, -.061, 0], "quaternion_xyzw": [0, 0, 2**-.5, 2**-.5]}
        self.assertEqual(suction_face(side, body), "-Y")

    def test_alternating_reaction_is_not_a_dc_bias(self):
        result = support_statistics([[.5, 0, 7.848, 0, 0, 0],
                                     [-.5, 0, 7.848, 0, 0, 0]], [0, 0, 7.848])
        self.assertEqual(result["count"], 2)
        self.assertAlmostEqual(result["mean_force_error_n"], 0)
        self.assertAlmostEqual(result["instantaneous_force_error_n"]["rms"], .5)
        self.assertEqual(result["status"], "DIAGNOSTIC_ONLY_NOT_CALIBRATED")


if __name__ == "__main__":
    unittest.main()
