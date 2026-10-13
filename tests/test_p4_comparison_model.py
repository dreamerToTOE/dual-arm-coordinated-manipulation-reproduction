"""Fixed offline mathematical checks; no search/simulation/robot execution."""
import unittest
from math import pi

import numpy as np
import shapely

from baselines.p4_comparison.model import PlanarModel


class PlanarModelTests(unittest.TestCase):
    def setUp(self):
        self.model = PlanarModel()

    def test_preregistered_dimensions_and_endpoints(self):
        model = self.model
        self.assertEqual(model.n, 20)
        self.assertEqual(np.count_nonzero(model.lengths), 19)
        self.assertEqual(model.partitions, (0, 16))
        for q in (model.start, model.goal):
            self.assertLessEqual(np.linalg.norm(model.closure(q)[:2]), 1e-8)
            self.assertLessEqual(abs(model.closure(q)[2]), 1e-8)
            for environment in model.environments:
                self.assertTrue(model.valid(q, environment)["valid"])
        self.assertEqual(model.branch(model.start, 16), -1)
        self.assertEqual(model.branch(model.goal, 16), 1)
        self.assertEqual(model.branch(model.start, 0), model.branch(model.goal, 0))

    def test_true_geos_version_and_collision_evidence(self):
        self.assertEqual(shapely.__version__, "2.1.2")
        geometry = self.model.collision(self.model.start, "E0_sparse")
        self.assertFalse(geometry["collision"])
        self.assertGreater(geometry["minimum_clearance"], 0.0)
        self.assertGreater(geometry["geometry_queries"], 0)
        # A complete physical folding onto ground gives non-adjacent overlap.
        q = np.zeros(20)
        q[1] = pi
        result = self.model.collision(q, "E0_sparse")
        self.assertTrue(result["collision"])
        self.assertLessEqual(result["minimum_clearance"], 0.0)
        self.assertEqual(len(result["pair"]), 2)

    def test_jacobian_central_difference(self):
        model = self.model
        h = 1e-6
        vectors = (model.start, model.goal, (model.start + model.goal)/2.0,
                   model.start + np.linspace(-0.03, 0.03, 20))
        for q in vectors:
            numerical = np.column_stack([
                (model.closure(q + np.eye(20)[j]*h) -
                 model.closure(q - np.eye(20)[j]*h))/(2*h)
                for j in range(20)])
            error = float(np.max(np.abs(model.jacobian(q) - numerical)))
            self.assertLessEqual(error, 1e-7)

    def test_both_analytic_branches_and_partition_invariance(self):
        model = self.model
        for base in (model.start, model.goal):
            for partition in model.partitions:
                for branch in (-1, 1):
                    result = model.ik(base, partition, branch)
                    self.assertTrue(result.success, result.reason)
                    active = np.ones(20, dtype=bool)
                    active[partition:partition + 3] = False
                    np.testing.assert_array_equal(result.q[active], base[active])
                    residual = model.closure(result.q)
                    self.assertLessEqual(np.linalg.norm(residual[:2]), 1e-8)
                    self.assertLessEqual(abs(residual[2]), 1e-8)
                    self.assertEqual(model.branch(result.q, partition), branch)

    def test_singular_fixture_has_true_passive_rank_loss(self):
        model = self.model
        fixture = model.singular_fixture()
        self.assertTrue(fixture.success, fixture.reason)
        q = fixture.q
        self.assertLessEqual(np.linalg.norm(model.closure(q)[:2]), 1e-8)
        self.assertLessEqual(abs(model.closure(q)[2]), 1e-8)
        self.assertEqual(model.branch(q, 16), 0)
        jacobian = model.jacobian(q)[:, 16:19]
        self.assertLessEqual(abs(float(np.linalg.det(jacobian))), 1e-10)
        self.assertEqual(np.linalg.matrix_rank(jacobian, tol=1e-10), 2)
        # Exact singular branch is shared by the two analytic IK labels.
        positive = model.ik(q, 16, 1)
        negative = model.ik(q, 16, -1)
        self.assertTrue(positive.success, positive.reason)
        self.assertTrue(negative.success, negative.reason)
        self.assertLessEqual(np.linalg.norm(positive.q - negative.q), 1e-7)

    def test_bad_inputs_bounds_and_unreachable_ik_rejected(self):
        model = self.model
        self.assertFalse(model.valid([float("nan")]*20, "E0_sparse")["valid"])
        q = model.start.copy()
        q[0] = pi + 0.01
        self.assertEqual(model.valid(q, "E0_sparse")["reason"], "JOINT_LIMIT")
        result = model.ik(np.zeros(20), 0, 1)
        self.assertFalse(result.success)
        self.assertEqual(result.reason, "IK_UNREACHABLE")
        self.assertEqual(model.ik(model.start, 16, 0).reason, "NON_SINGULAR_BRANCH_ZERO")
        with self.assertRaises(ValueError):
            model.ik(model.start, 17, 1)


if __name__ == "__main__":
    unittest.main()
