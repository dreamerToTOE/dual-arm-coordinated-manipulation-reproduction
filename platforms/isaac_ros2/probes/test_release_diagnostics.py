"""[ENGINEERING] 无Isaac依赖的阶段选择与固定工具变换测试。"""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_diagnostics import active_cube_index, tcp_from_link8


class ReleaseDiagnosticsTests(unittest.TestCase):
    def test_record_only_known_release_window(self):
        self.assertEqual(active_cube_index('task27_minus_outer:RELEASE_OPEN'), 1)
        self.assertEqual(active_cube_index('task27_plus_outer:CLEARANCE_ENTER'), 0)
        for value in ('', 'garbage', 'task27_minus_outer:HOME',
                      'task27_minus_outer:CLEARANCE_SETTLED', 'unknown:RELEASE_OPEN'):
            self.assertIsNone(active_cube_index(value))

    def test_identity_and_quarter_turn(self):
        p = tcp_from_link8((1, 2, 3), (0, 0, 0, 1), (0, .13, .08), (0, 0, 0, 1))
        self.assertEqual(p['position_m'], [1, 2.13, 3.08])
        p = tcp_from_link8((1, 2, 3), (0, 0, 2**-.5, 2**-.5),
                           (0, .13, .08), (0, 0, 0, 1))
        for a, b in zip(p['position_m'], (.87, 2, 3.08)):
            self.assertAlmostEqual(a, b)
        self.assertAlmostEqual(math.hypot(*p['quaternion_xyzw']), 1)

    def test_invalid_quaternion_rejected(self):
        for q in ((0, 0, 0, 0), (0, 0, math.nan, 1)):
            with self.assertRaises(ValueError):
                tcp_from_link8((0, 0, 0), q, (0, .13, .08), (0, 0, 0, 1))


if __name__ == '__main__':
    unittest.main()
