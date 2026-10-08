"""[ENGINEERING] Pure unit tests; no Isaac, PhysX, GUI, or scene construction.

Run: python3 -m unittest discover -s tests -p test_task01_static_query_guard.py -v
These tests validate software guards, not model parity or physical safety.
"""

import math
from pathlib import Path
import runpy
import types
import unittest

import numpy as np


PROBE = Path(__file__).resolve().parents[1] / "platforms/isaac_ros2/probes/task01_single_cube_model_parity_gui.py"
HELPERS = runpy.run_path(str(PROBE), run_name="task01_static_query_guard_test_helpers")


class Hit:
    def __init__(self, path, owner="original/body"):
        self.collision = path
        self.rigid_body = owner


class BrokenHit:
    @property
    def collision(self):
        raise RuntimeError("simulated native callback property failure")


def native_call(hits, returned_count=None):
    def call(callback):
        for hit in hits:
            if callback(hit) is not True:
                raise AssertionError("Guard must continue native traversal")
        return len(hits) if returned_count is None else returned_count
    return call


class Attribute:
    def __init__(self, value):
        self.value = value

    def Get(self):
        return self.value


class Mesh:
    pass


class Cube:
    def __init__(self, prim):
        self.prim = prim

    def GetSizeAttr(self):
        return Attribute(self.prim.size)


class Cylinder:
    def __init__(self, prim):
        self.prim = prim

    def GetRadiusAttr(self):
        return Attribute(self.prim.radius)

    def GetHeightAttr(self):
        return Attribute(self.prim.height)

    def GetAxisAttr(self):
        return Attribute(self.prim.axis)


SCHEMA = types.SimpleNamespace(Mesh=Mesh, Cube=Cube, Cylinder=Cylinder)
GF = types.SimpleNamespace(Vec3d=lambda *values: tuple(values))


class Prim:
    def __init__(self, kind, **attributes):
        self.kind = kind
        self.__dict__.update(attributes)

    def IsA(self, schema):
        return schema is self.kind

    def GetPath(self):
        return "/original/collider"


class AffineMatrix:
    def __init__(self, scale=(2., 3., 4.), translation=(1., 2., 3.)):
        self.scale = scale
        self.translation = translation

    def Transform(self, point):
        return [self.scale[k] * point[k] + self.translation[k] for k in range(3)]


class NativeCallbackGuardTests(unittest.TestCase):
    def query(self, hits, count=None):
        return HELPERS["native_query_hits"](native_call(hits, count), {"known"}, "test-only")

    def test_exact_hit_and_owner_recorded(self):
        result = self.query([Hit("known")])
        self.assertNotIn("error", result)
        self.assertEqual(result["reported_hit_count"], 1)
        self.assertEqual(result["callback_count"], 1)
        self.assertEqual(result["hits"], [{"collision": "known", "rigid_body": "original/body"}])

    def test_unknown_collider_rejected_after_callback(self):
        result = self.query([Hit("unknown")])
        self.assertIn("error", result)
        self.assertTrue(result["callback_errors"])
        self.assertEqual(result["callback_count"], 1)

    def test_callback_property_exception_does_not_escape_callback(self):
        result = self.query([BrokenHit()], 1)
        self.assertIn("error", result)
        self.assertIn("simulated native callback property failure", result["callback_errors"][0])

    def test_reported_callback_count_mismatch_rejected(self):
        result = self.query([Hit("known")], 2)
        self.assertIn("error", result)
        self.assertEqual(result["reported_hit_count"], 2)
        self.assertEqual(result["callback_count"], 1)

    def test_fractional_and_negative_native_count_rejected(self):
        for count in (-1, 1.5):
            with self.subTest(count=count):
                self.assertIn("error", self.query([Hit("known")], count))

    def test_empty_query_count_consistency_is_not_positive_hit(self):
        result = self.query([])
        self.assertNotIn("error", result)
        self.assertEqual(result["hits"], [])
        # Actual positive guard separately requires exact-target membership.


class ConservativeOutsideAabbTests(unittest.TestCase):
    def outside(self, point, radius=1e-5):
        return HELPERS["sphere_proven_outside_aabb"](point, [-1.] * 3, [1.] * 3, radius)

    def test_whole_sphere_separated_in_any_axis(self):
        for point in ([2., 0., 0.], [0., -2., 0.], [0., 0., 2.]):
            with self.subTest(point=point):
                self.assertTrue(self.outside(point))

    def test_center_outside_is_not_enough_when_radius_intersects(self):
        self.assertFalse(self.outside([1. + 5e-6, 0., 0.]))

    def test_sphere_touch_is_not_proven_separation(self):
        self.assertFalse(self.outside([1. + 1e-5, 0., 0.]))

    def test_additional_one_micrometer_margin_is_required(self):
        self.assertFalse(self.outside([1. + 1e-5 + .5e-6, 0., 0.]))
        self.assertTrue(self.outside([1. + 1e-5 + 2e-6, 0., 0.]))

    def test_inside_point_is_not_proven_outside(self):
        self.assertFalse(self.outside([0., 0., 0.]))


class ActualCookedAndPrimitiveInteriorTests(unittest.TestCase):
    def geometry(self, prim, cooked=None):
        return HELPERS["transformed_probe_geometry"](prim, cooked, AffineMatrix(), np, GF, SCHEMA)

    def test_cooked_vertices_centroid_and_aabb_not_authored_points(self):
        prim = Prim(Mesh, authored_vertices=[[999., 999., 999.]])
        cooked = {"convexes": [{"vertices": [[0., 0., 0.], [1., 0., 0.],
                                                [0., 1., 0.], [0., 0., 1.]]}]}
        point, lower, upper = self.geometry(prim, cooked)
        np.testing.assert_allclose(point, [1.5, 2.75, 4.])
        np.testing.assert_allclose(lower, [1., 2., 3.])
        np.testing.assert_allclose(upper, [3., 5., 7.])

    def test_mesh_without_actual_single_cooked_convex_rejected(self):
        for cooked in (None, {"convexes": []}, {"convexes": [{}, {}]}):
            with self.subTest(cooked=cooked):
                with self.assertRaises(RuntimeError):
                    self.geometry(Prim(Mesh), cooked)

    def test_nonfinite_and_coplanar_actual_vertices_rejected(self):
        for vertices in ([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [math.nan, 0., 1.]],
                         [[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [1., 1., 0.]]):
            with self.subTest(vertices=vertices):
                with self.assertRaises(RuntimeError):
                    self.geometry(Prim(Mesh), {"convexes": [{"vertices": vertices}]})

    def test_cube_center_and_scale_retained_in_world_aabb(self):
        point, lower, upper = self.geometry(Prim(Cube, size=.12))
        np.testing.assert_allclose(point, [1., 2., 3.])
        np.testing.assert_allclose(lower, [.88, 1.82, 2.76])
        np.testing.assert_allclose(upper, [1.12, 2.18, 3.24])

    def test_y_cylinder_center_and_conservative_aabb(self):
        point, lower, upper = self.geometry(Prim(Cylinder, radius=.01, height=.04, axis="Y"))
        np.testing.assert_allclose(point, [1., 2., 3.])
        np.testing.assert_allclose(lower, [.98, 1.94, 2.96])
        np.testing.assert_allclose(upper, [1.02, 2.06, 3.04])

    def test_invalid_primitive_dimension_and_axis_rejected(self):
        for prim in (Prim(Cube, size=0.), Prim(Cube, size=math.nan),
                     Prim(Cylinder, radius=.01, height=.04, axis="Q")):
            with self.subTest(attributes=vars(prim)):
                with self.assertRaises(RuntimeError):
                    self.geometry(prim)


class QuaternionFiniteTests(unittest.TestCase):
    def test_sign_and_finite_scale_equivalence(self):
        angle = HELPERS["quat_angle"]([0., 0., 0., 2.], [0., 0., 0., -3.])
        self.assertAlmostEqual(angle, 0.)

    def test_nonfinite_malformed_and_zero_quaternion_rejected(self):
        for quaternion in ([0., 0., 0., 0.], [0., 0., math.nan, 1.],
                           [0., 0., math.inf, 1.], [0., 0., 1.]):
            with self.subTest(quaternion=quaternion):
                with self.assertRaises(RuntimeError):
                    HELPERS["quat_angle"](quaternion, [0., 0., 0., 1.])


if __name__ == "__main__":
    unittest.main()
