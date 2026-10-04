"""[ENGINEERING] 释放诊断摘要不能丢失峰值或混用物理步。"""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_release_window import summarize


def sample(step, x, force):
    return {
        'phase_received_async': 'task27_minus_outer:RELEASE_OPEN',
        'physics': {'stamp_ns': step * 10000000, 'physics_step': step,
                    'bodies': [None, {'position_m': [x, 0, .26], 'linear_velocity_m_s': [0, 0, 0]}]},
        'tools_physics': {'stamp_ns': step * 10000000, 'physics_step': step},
        'tcp_poses_world_from_physics_link8': {
            side: {'position_m': [1, 0, .26]} for side in ('left', 'right')},
        'suction_closed': {'left': False, 'right': False},
        'collision_contacts': {'pairs': [{'other_path': '/World/Table',
            'collision_force_world_n': [force, 0, 0], 'normal_contact_count': 1}]},
    }


class ReleaseSummaryTests(unittest.TestCase):
    def setUp(self):
        self.rows = [sample(1, 1.1, 3), sample(2, 1.095, -3), sample(3, 1.1, 3)]
        for row in self.rows:
            row['physics']['bodies'][0] = copy.deepcopy(row['physics']['bodies'][1])

    def test_peak_not_hidden_by_final_or_mean(self):
        phase = summarize(self.rows)['phases'][0]
        self.assertAlmostEqual(phase['range_mm'][0], 5)
        self.assertEqual(phase['delta_mm'][0], 0)
        self.assertEqual(phase['collision_pairs']['/World/Table']['max_force_norm_n'], 3)
        self.assertEqual(phase['collision_pairs']['/World/Table']['mean_force_world_n'][0], 1)

    def test_mixed_step_rejected(self):
        self.rows[0]['tools_physics']['physics_step'] = 50
        with self.assertRaises(ValueError):
            summarize(self.rows)

    def test_nonfinite_position_rejected(self):
        self.rows[0]['physics']['bodies'][1]['position_m'][0] = float('nan')
        with self.assertRaises(ValueError):
            summarize(self.rows)


if __name__ == '__main__':
    unittest.main()
