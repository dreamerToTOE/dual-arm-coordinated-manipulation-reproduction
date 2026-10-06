import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from physics_object_sampler import BodySample, PhysicsSnapshot
from fixture_geometry_stream import geometry_poses


class GeometryStreamTests(unittest.TestCase):
    def setUp(self):
        self.paths = ('/World/Cube01', '/World/Cube02')
        self.values = {'branch_sign': {'left': 1, 'right': -1},
                       'tcp_y': .155, 'vertical_drop_z': .080}
        paths = self.paths + ('/World/left_fr3/fr3_link8', '/World/right_fr3/fr3_link8')
        self.sample = PhysicsSnapshot(100, 1, 'world', tuple(
            BodySample(p, (1., 0., .3), (0., 0., 0., 1.), (0.,)*3, (0.,)*3) for p in paths))

    def test_order_offset_and_quaternion(self):
        poses = geometry_poses(self.sample, self.paths, self.values)
        self.assertEqual(len(poses), 4)
        self.assertEqual(poses[0]['position_m'], (1., 0., .3))
        for i, sign in ((2, 1), (3, -1)):
            self.assertEqual(poses[i]['position_m'], [1., sign * .155, .38])
            self.assertAlmostEqual(sum(q*q for q in poses[i]['quaternion_xyzw']), 1.)

    def test_reject_order_and_frame(self):
        with self.assertRaises(ValueError):
            geometry_poses(self.sample, self.paths[::-1], self.values)
        bad = PhysicsSnapshot(100, 1, 'base', self.sample.bodies)
        with self.assertRaises(ValueError):
            geometry_poses(bad, self.paths, self.values)

    def test_rotated_offset(self):
        body = self.sample.bodies[-1]
        changed = BodySample(body.prim_path, body.position_m,
            (0., 0., 2**-.5, 2**-.5), body.linear_velocity_m_s, body.angular_velocity_rad_s)
        sample = PhysicsSnapshot(100, 1, 'world', self.sample.bodies[:-1] + (changed,))
        self.assertAlmostEqual(geometry_poses(sample, self.paths, self.values)[-1]['position_m'][0], 1.155)
