import unittest
from audit_fixture_geometry_feedback import audit, gaps


def pose(x, y, z):
    return {'position_m': [x, y, z], 'quaternion_xyzw': [0, 0, 0, 1]}


class FeedbackAuditTests(unittest.TestCase):
    def setUp(self):
        self.log = ('task27_plus_outer X_3 rear=CLOSED side=CLOSED rear_gap=1.000 mm '
            'side_gap=1.000 mm alignment=0.000 mm tilt=0.000 deg. physics_stamp_ns=100')
        self.row = {'physics': {'stamp_ns': 100, 'physics_step': 3,
            'bodies': [pose(1, 0, .26)]}, 'tools_physics': {'stamp_ns': 100},
            'tcp_poses_world_from_physics_link8': {'left': pose(1, -.061, .26),
                                                 'right': pose(.939, 0, .26)}}

    def test_exact_stamp_matches(self):
        self.assertEqual(audit(self.log, [self.row])['status'], 'PASS_EXACT_STAMP_GEOMETRY_ONLY')

    def test_no_nearest_join_or_empty_pass(self):
        with self.assertRaises(ValueError):
            audit('', [self.row])
        with self.assertRaises(ValueError):
            audit(self.log, [])
        self.row['physics']['stamp_ns'] = 101
        with self.assertRaises(ValueError):
            audit(self.log, [self.row])

    def test_reject_mixed_duplicate_and_incorrect_logged_values(self):
        with self.assertRaises(ValueError):
            audit(self.log, [self.row, self.row])
        with self.assertRaises(ValueError):
            audit(self.log.replace('1.000', '9.000'), [self.row])
        self.row['tools_physics']['stamp_ns'] += 1
        with self.assertRaises(ValueError):
            audit(self.log, [self.row])

    def test_minus_side_direction(self):
        values = gaps(pose(1, 0, .26), pose(.939, 0, .26), pose(1, .061, .26), -1)
        self.assertAlmostEqual(values[0], 1.)
        self.assertAlmostEqual(values[1], 1.)
