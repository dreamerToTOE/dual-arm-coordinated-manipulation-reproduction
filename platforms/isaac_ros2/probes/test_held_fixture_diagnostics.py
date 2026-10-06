"""[ENGINEERING] 持件诊断phase/DOF映射与压缩的离线负向验证。"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from held_fixture_diagnostics import held_cube_index, finite_vector


class HeldDiagnosticsTests(unittest.TestCase):
    def test_known_phase_and_bounds(self):
        self.assertEqual(held_cube_index('task27_plus_outer:X_16'), 0)
        self.assertEqual(held_cube_index('task27_plus_inner:Y_1'), 2)
        self.assertEqual(held_cube_index('task27_minus_outer:ABORT'), 1)
        for phase in ('task27_plus_outer:X_0', 'task27_plus_outer:Y_17',
                      'task27_minus_inner:X_1', 'task27_plus_outer:HOME', '', 'unknown:CONTACT'):
            self.assertIsNone(held_cube_index(phase))

    def test_reject_bad_dof_readout(self):
        self.assertEqual(finite_vector([[1, 2]], 2), [1, 2])
        for value in ([[1]], [[1, float('nan')]], [[1, float('inf')]]):
            with self.assertRaises(ValueError):
                finite_vector(value, 2)
