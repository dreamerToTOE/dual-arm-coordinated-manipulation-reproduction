"""[ENGINEERING] 丢步/混步/非数值诊断不得被汇总成PASS。"""
import unittest
from analyze_held_fixture import summarize


def row(step):
    stamp = step * 100
    base = {'physics_step': step, 'stamp_ns': stamp}
    sample = {'physics': dict(base, bodies=[{'position_m': [1,.2,.26]}]),
        'phase_received_async': 'task27_plus_outer:Y_15',
        'suction_closed': {'left': True, 'right': True}, 'articulations': {}}
    for key in ('tools_physics', 'robots_physics', 'collision_contacts', 'robot_collision_contacts'):
        sample[key] = dict(base, pairs=[])
    for side in ('left', 'right'):
        sample['articulations'][side] = {'dof_names': ['fr3_joint1', 'fr3_finger_joint1'],
            'positions_rad': [0,.02], 'position_targets_rad': [.01,.02],
            'projected_joint_effort_raw': [87,.1], 'velocities_rad_s': [0,0]}
    return sample


class HeldAnalysisTests(unittest.TestCase):
    def test_rejects_empty_stream(self):
        with self.assertRaises(ValueError):
            summarize([])

    def test_preserves_peak_joint_and_both_closed(self):
        result = summarize([row(3), row(4)])
        phase = result['phases']['task27_plus_outer:Y_15']
        self.assertEqual(phase['max_raw_effort']['left']['joint'], 'fr3_joint1')
        self.assertEqual(phase['both_closed_samples'], 2)

    def test_rejects_step_gap_and_mixed_contacts(self):
        with self.assertRaises(ValueError):
            summarize([row(3), row(5)])
        bad = row(3); bad['robot_collision_contacts']['stamp_ns'] += 1
        with self.assertRaises(ValueError):
            summarize([bad])

    def test_rejects_nonfinite_and_wrong_dof_count(self):
        bad = row(3); bad['articulations']['left']['positions_rad'][0] = float('nan')
        with self.assertRaises(ValueError):
            summarize([bad])
        bad = row(3); bad['articulations']['left']['positions_rad'].pop()
        with self.assertRaises(ValueError):
            summarize([bad])
