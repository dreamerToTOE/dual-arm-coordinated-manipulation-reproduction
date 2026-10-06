import itertools
import io
import json
import unittest
from audit_held_hull import common_ball_radius, summarize_probe
from task01_held_moveit_replay import select_steps


class HeldReplayHullTest(unittest.TestCase):
    def setUp(self):
        self.vertices = list(itertools.product([-.5, .5], repeat=3))
        self.wall = [[-.5, .5]] * 3

    def test_overlap(self):
        value = common_ball_radius(self.vertices, [0, 0, 0], [0, 0, 0, 1], self.wall)
        self.assertAlmostEqual(value['common_ball_radius_m'], .5)

    def test_separation(self):
        value = common_ball_radius(self.vertices, [-2, 0, 0], [0, 0, 0, 1], self.wall)
        self.assertLess(value['common_ball_radius_m'], 0)
        self.assertAlmostEqual(value['deep_wall_x_plane_clearance_m'], 1)

    def test_translation_invariant_radius_and_world_witness(self):
        offset = [1.25, -2.5, .3]
        wall = [[v-.5, v+.5] for v in offset]
        value = common_ball_radius(self.vertices, offset, [0, 0, 0, 1], wall)
        self.assertAlmostEqual(value['common_ball_radius_m'], .5)
        for actual, expected in zip(value['witness_center_m'], offset):
            self.assertAlmostEqual(actual, expected)

    def test_invalid_pose(self):
        for q in ([0, 0, 0, 0], [0, 0, 0, float('nan')]):
            with self.assertRaises(ValueError):
                common_ball_radius(self.vertices, [0, 0, 0], q, self.wall)

    def test_no_records(self):
        with self.assertRaises(ValueError):
            summarize_probe([], self.vertices, self.wall)

    def test_duplicate_records(self):
        line = 'HELD_HULL_AUDIT cube X 0 left -2 0 0 0 0 0 1'
        with self.assertRaises(ValueError):
            summarize_probe([line, line], self.vertices, self.wall)

    def test_interleaved_log_rejected(self):
        with self.assertRaises(ValueError):
            summarize_probe(['HELD_HULL_AUDIT cube X 0 left [INFO] logger 0 0'], self.vertices, self.wall)

    def test_single_record(self):
        value = summarize_probe(['HELD_HULL_AUDIT cube X 0 left -2 0 0 0 0 0 1'], self.vertices, self.wall)
        self.assertEqual(value['samples'], 1)
        self.assertEqual(value['phases']['cube:X:left']['overlapping_samples'], 0)

    def test_exact_steps_and_missing(self):
        lines = [json.dumps({'physics': {'physics_step': step}}) for step in [1, 2, 3]]
        self.assertEqual([r['physics']['physics_step'] for r in select_steps(lines, [3, 1])], [3, 1])
        with self.assertRaises(ValueError):
            select_steps(lines, [4])

    def test_duplicate_step(self):
        line = json.dumps({'physics': {'physics_step': 1}})
        with self.assertRaises(ValueError):
            select_steps([line, line], [1])


if __name__ == '__main__':
    unittest.main()
