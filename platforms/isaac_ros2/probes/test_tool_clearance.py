import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import numpy as np

from audit_fixture_tool_clearance import audit, obb_intersection, signed_xyz


class GeometryTests(unittest.TestCase):
    def test_separated_and_intersecting_boxes(self):
        rotation, half = np.eye(3), np.array([.06]*3)
        self.assertFalse(obb_intersection(np.zeros(3), rotation, half,
                                         np.array([.121, 0, 0]), rotation, half)[0])
        hit, overlap = obb_intersection(np.zeros(3), rotation, half,
                                       np.array([.110, 0, 0]), rotation, half)
        self.assertTrue(hit)
        self.assertAlmostEqual(overlap, .01)

    def test_rotated_boxes(self):
        q = np.pi/4
        rotation = np.array([[np.cos(q), -np.sin(q), 0], [np.sin(q), np.cos(q), 0], [0, 0, 1]])
        self.assertTrue(obb_intersection(np.zeros(3), np.eye(3), np.ones(3)*.06,
                                        np.array([.12, 0, 0]), rotation, np.ones(3)*.06)[0])

    def test_only_known_signed_expression(self):
        np.testing.assert_allclose(signed_xyz("0 ${side_sign * 0.155} 0.08", -1), [0, -.155, .08])
        with self.assertRaises(ValueError):
            signed_xyz("0 ${unknown * 0.155} 0.08", 1)

    def test_fixed_center_roll_cannot_move_normal_support_stem(self):
        xml = b'''<robot><joint name="side_suction_tcp_joint"><origin
            xyz="0 0.155 0.08" rpy="0 0 1.5707963267948966"/></joint>
            <collision name="lateral_support_collision"><origin xyz="0 0.065 0.08" rpy="0 0 0"/>
            <geometry><box size="0.018 0.130 0.018"/></geometry></collision></robot>'''
        class UnitXacro:
            def read_bytes(self):
                return xml
            def __str__(self):
                return "unit_geometry_only"
        analysis = {"final_geometry": [{"prim_path": "neighbor", "position_m": [1.1, .1215, .26],
                                       "quaternion_xyzw": [0, 0, 0, 1]}]}
        with patch("audit_fixture_tool_clearance.ET.parse", return_value=ET.ElementTree(ET.fromstring(xml))):
            result = audit(UnitXacro(), analysis, 15)
        self.assertEqual(len(result["roll_sweep_fixed_face_center_and_normal"]), 24)
        self.assertEqual(result["roll_sweep_clear_box_pose_count"], 0)
        for entry in result["roll_sweep_fixed_face_center_and_normal"]:
            self.assertEqual(entry["collisions"][0]["tool_primitive"], "lateral_support_collision")


if __name__ == "__main__":
    unittest.main()
