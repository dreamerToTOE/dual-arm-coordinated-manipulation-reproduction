"""[ENGINEERING] 正常供料不能空集 READY，局部夹具等待条件保持原样。"""
import unittest

from task01_cube04_headless import fixture_ready


class FixtureReadinessTest(unittest.TestCase):
    def test_normal_feed_waits_for_first_actual_arrival(self):
        self.assertFalse(fixture_ready([], 0, 2))
        self.assertFalse(fixture_ready([0] * 5, 0, 2))
        self.assertFalse(fixture_ready([1, 0, 0, 0, 0], 0, 2))
        self.assertTrue(fixture_ready([2, 0, 0, 0, 0], 0, 2))

    def test_preplaced_modes_still_wait_for_all_fixture_cubes(self):
        self.assertFalse(fixture_ready([2, 2, 1, 0, 0], 3, 2))
        self.assertTrue(fixture_ready([2, 2, 2, 0, 0], 3, 2))
        self.assertFalse(fixture_ready([2, 2, 2, 1, 0], 4, 2))
        self.assertTrue(fixture_ready([2, 2, 2, 2, 0], 4, 2))
        with self.assertRaises(ValueError):
            fixture_ready([2] * 5, 2, 2)


if __name__ == '__main__':
    unittest.main()
