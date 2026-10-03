"""[ENGINEERING] 不依赖启动 Isaac 的接触缓冲/参考点负向测试。"""

from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from physics_contact_sampler import PhysicsContactSampler


class FakeContactView:
    sensor_count, filter_count = 1, 1
    sensor_paths, filter_paths = ["cube"], [["wall"]]

    def __init__(self):
        self.valid = True
        self.counts = np.array([[1]])
        self.starts = np.array([[0]])
        self.normal = np.array([[2.0]])
        self.point = np.array([[1.0, 2.0, 3.0]])
        self.direction = np.array([[-1.0, 0.0, 0.0]])
        self.friction = np.array([[0.0, 1.0, 0.0], [0.0, 2.0, 0.0]])
        self.anchors = np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]])

    def check(self):
        return self.valid

    def get_contact_force_matrix(self, dt):
        return np.array([[[-2.0, 0.0, 0.0]]])

    def get_contact_data(self, dt):
        self.counts[:] = 1
        return self.normal, self.point, self.direction, np.array([[0.0]]), self.counts, self.starts

    def get_friction_data(self, dt):
        # 刻意模拟 PhysX 两次 API 共用索引缓冲。
        self.counts[:] = 2
        return self.friction, self.anchors, self.counts, self.starts


class ContactSamplerTests(unittest.TestCase):
    def setUp(self):
        self.view = FakeContactView()
        self.sampler = PhysicsContactSampler(self.view, ["cube"], ["wall"])
        self.snapshot = SimpleNamespace(stamp_ns=20, physics_step=4, frame_id="world",
                                        bodies=[SimpleNamespace(prim_path="cube", position_m=(0, 0, 0))])

    def test_shared_buffer_copy_force_moment_and_stamp(self):
        result = self.sampler.capture(self.snapshot, 1 / 60)
        pair = result["pairs"][0]
        np.testing.assert_allclose(pair["collision_force_world_n"], [-2, 3, 0])
        np.testing.assert_allclose(pair["collision_torque_about_sensor_origin_world_nm"], [-9, -6, 7])
        self.assertEqual(pair["normal_contact_count"], 1)
        self.assertEqual(pair["friction_anchor_count"], 2)
        self.assertEqual((result["stamp_ns"], result["physics_step"]), (20, 4))

    def test_changed_reference_point_shifts_moment(self):
        self.snapshot.bodies[0].position_m = (0, 1, 0)
        pair = self.sampler.capture(self.snapshot, 1 / 60)["pairs"][0]
        np.testing.assert_allclose(pair["collision_torque_about_sensor_origin_world_nm"], [-9, -6, 5])

    def test_bad_dt_rejected(self):
        for dt in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                self.sampler.capture(self.snapshot, dt)

    def test_dead_view_rejected(self):
        self.view.valid = False
        with self.assertRaises(RuntimeError):
            self.sampler.capture(self.snapshot, 1 / 60)

    def test_missing_origin_rejected(self):
        self.snapshot.bodies = []
        with self.assertRaises(ValueError):
            self.sampler.capture(self.snapshot, 1 / 60)

    def test_buffer_out_of_range_rejected(self):
        with self.assertRaises(RuntimeError):
            self.sampler._slice(np.array([[2]]), np.array([[0]]), 0, 0, 1)

    def test_nonfinite_force_rejected(self):
        self.view.normal[:] = float("nan")
        with self.assertRaises(ValueError):
            self.sampler.capture(self.snapshot, 1 / 60)

    def test_filter_order_rejected(self):
        with self.assertRaises(ValueError):
            PhysicsContactSampler(self.view, ["cube"], ["wrong_wall"])


if __name__ == "__main__":
    unittest.main()
