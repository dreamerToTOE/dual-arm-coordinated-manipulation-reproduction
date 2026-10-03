import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    'cube04_summary', Path(__file__).resolve().parents[3] / 'scripts/summarize_cube04_precision.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Cube04SummaryTest(unittest.TestCase):
    def test_gap_and_do_not_confuse_next_task_suction(self):
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary)
            (run / 'raw').mkdir()
            (run / 'raw/controller.log').write_text('Task27 batch 4 PASS:\n')
            ys = [.243, -.243, .1215, -.1225, 0]
            bodies = [{'prim_path': f'/Cube{i+1}', 'position_m': [1.1, y, .26],
                       'quaternion_xyzw': [0, 0, 0, 1]} for i, y in enumerate(ys)]
            rows = [
                {'physics': {'physics_step': 1, 'stamp_ns': 100, 'bodies': bodies},
                 'feed_state': [2, 2, 2, 2, 0], 'suction_closed': {'left': True, 'right': False}},
                {'physics': {'physics_step': 7, 'stamp_ns': 200, 'bodies': bodies},
                 'feed_state': [2, 2, 2, 2, 2], 'suction_closed': {'left': False, 'right': True}}]
            (run / 'raw/physics_pose_samples.jsonl').write_text(
                ''.join(json.dumps(row)+'\n' for row in rows))
            result = module.summarize(run)
            self.assertEqual(result['completed_batches'], [4])
            self.assertEqual(result['fourth_helper_closed_inside_samples'], 0)
            self.assertEqual(result['fifth_helper_closed_inside_samples'], 0)
            self.assertEqual(result['integrity_errors'], [])
            self.assertAlmostEqual(result['cube04_axis_center_neighbor_gap_mm'], .5)
            self.assertAlmostEqual(result['cube04_oriented_projection_neighbor_gap_mm'], .5)
            # 独立第五件探针预置4件，不能写成“前三件预置”或误计第四件吸附。
            (run / 'raw/model_audit.json').write_text(json.dumps({'preplaced_count': 4}))
            fourth_fixture = module.summarize(run)
            self.assertEqual(fourth_fixture['fixture_preplaced_count'], 4)
            self.assertIn('count=4', fourth_fixture['boundary'])
            self.assertNotIn('cube04_insertion_y_span_mm', fourth_fixture)
            self.assertFalse(fourth_fixture['full_five_batch_completion_reported'])
            # 全部供料 ARRIVED 不能冒充五件完成；必须有正常模式的五条批 PASS。
            (run / 'raw/model_audit.json').write_text(json.dumps({'preplaced_count': 0}))
            incomplete = module.summarize(run)
            self.assertFalse(incomplete['full_five_batch_completion_reported'])
            self.assertFalse(incomplete['cube04_neighbor_geometry_available'])
            self.assertIsNone(incomplete['cube04_axis_center_neighbor_gap_mm'])
            (run / 'raw/controller.log').write_text(
                ''.join(f'Task27 batch {i} PASS:\n' for i in range(1, 6)) +
                'task27_plus_outer final Ground Truth: cell_error=1.0 mm\n')
            full = module.summarize(run)
            self.assertTrue(full['full_five_batch_completion_reported'])
            self.assertEqual(full['all_controller_final_geometry_lines'],
                             [('task27_plus_outer', 'cell_error=1.0 mm')])


if __name__ == '__main__':
    unittest.main()
