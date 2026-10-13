"""Fixed math/interface cases for the preregistered P4 planar comparison.

These are not independent planning trials or robot-execution evidence.
Do not discard an unreachable/colliding registered singular fixture.
"""

import unittest

import numpy as np

from baselines.p4_comparison.model import IKResult, PlanarModel
from baselines.p4_comparison.strategies import Strategy, nr_project, rbs_connect


class StrategyTests(unittest.TestCase):
    def setUp(self):
        self.model = PlanarModel()
        self.env = "E0_sparse"

    def test_zero_nr_and_fixed_neighbour(self):
        zero = nr_project(self.model, self.model.start)
        self.assertTrue(zero.success, zero.reason)
        self.assertTrue(np.array_equal(zero.q, self.model.start))
        perturbed = self.model.start.copy()
        perturbed[0] += 0.01
        projected = nr_project(self.model, perturbed)
        self.assertTrue(projected.success, projected.reason)
        self.assertLessEqual(np.linalg.norm(self.model.closure(projected.q)[:2]), 1e-8)
        self.assertLessEqual(abs(self.model.closure(projected.q)[2]), 1e-8)
        self.assertTrue(any(sample.get("update_accepted") for sample in projected.trace))
        self.assertTrue(all(len(sample["singular_values"]) == 3
                            for sample in projected.trace if "singular_values" in sample))

    def test_nr_negative_input_and_bound(self):
        invalid = nr_project(self.model, np.zeros(19))
        self.assertEqual(invalid.reason, "INVALID_INPUT")
        outside = self.model.start.copy()
        outside[0] = np.pi + 1e-3
        self.assertEqual(nr_project(self.model, outside).reason, "INITIAL_JOINT_LIMIT")

    def test_true_projection_rank_failure(self):
        class RankZeroModel:
            n = 20

            @staticmethod
            def closure(q):
                return np.array([0.1, 0.0, 0.0])

            @staticmethod
            def jacobian(q):
                return np.zeros((3, 20))

        result = nr_project(RankZeroModel(), np.zeros(20))
        self.assertFalse(result.success)
        self.assertEqual(result.reason, "RANK_ZERO")
        self.assertEqual(result.trace[0]["numerical_rank"], 0)

    def test_same_state_each_method(self):
        for method in ("RSS", "PCS", "NR"):
            with self.subTest(method=method):
                result = rbs_connect(self.model, self.env, method, self.model.start, self.model.start)
                self.assertTrue(result["success"], result["reason"])
                self.assertEqual(len(result["path"]), 2)
                self.assertEqual(result["projection_calls"], 0)

    def test_rss_rejects_different_regular_branch_without_nr(self):
        strategy = Strategy(self.model, self.env, "RSS")
        self.assertEqual(self.model.branch(self.model.start, 16), -1)
        self.assertEqual(self.model.branch(self.model.goal, 16), 1)
        result = rbs_connect(self.model, self.env, "RSS", self.model.start, self.model.goal,
                             strategy=strategy)
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "NO_COMMON_PASSIVE_BRANCH")
        self.assertEqual(strategy.counters.get("nr_calls", 0), 0)

    def test_pcs_uses_actual_common_partition(self):
        strategy = Strategy(self.model, self.env, "PCS")
        choices = strategy.connection_choices(self.model.start, self.model.goal)
        self.assertIn((0, -1), choices)
        self.assertNotIn((16, -1), choices)
        result = rbs_connect(self.model, self.env, "PCS", self.model.start, self.model.goal,
                             strategy=strategy)
        self.assertTrue(result["success"], result["reason"])
        self.assertEqual(result["partition"], 0)
        self.assertEqual(strategy.counters.get("nr_calls", 0), 0)
        for trial in result["trials"]:
            for point in trial["checked_points"]:
                if point["qualification"]["valid"]:
                    self.assertIn(self.model.branch(point["q"], trial["partition"]), (0, trial["branch"]))

    def test_registered_singular_fixture_preserves_actual_status(self):
        # This test does not change the fixture or falsely label geometry
        # failure a successful singular bridge. Scientific verdict is logged
        # independently by the runner using this same registered fixture.
        fixture = self.model.singular_fixture()
        if not fixture.success:
            self.assertIn(fixture.reason, ("IK_UNREACHABLE", "IK_CLOSURE_RESIDUAL", "JOINT_LIMIT"))
            return
        self.assertEqual(self.model.branch(fixture.q, 16), 0)
        self.assertLessEqual(np.linalg.norm(self.model.closure(fixture.q)[:2]), 1e-8)
        self.assertLessEqual(abs(self.model.closure(fixture.q)[2]), 1e-8)
        strategy = Strategy(self.model, self.env, "RSS")
        candidate, identity = strategy.project(fixture.q, 16, -1, phase="MATH_FIXTURE")
        self.assertTrue(candidate.success, candidate.reason)
        self.assertTrue(np.array_equal(candidate.q, fixture.q))
        self.assertEqual(strategy.projection_log[identity]["reason"], "ALREADY_CLOSED_BRANCH")
        # Endpoint branch0 is eligible on both true incident branches.
        self.assertIn((16, -1), strategy.connection_choices(self.model.start, fixture.q))
        self.assertIn((16, 1), strategy.connection_choices(fixture.q, self.model.goal))

    def test_failed_state_does_not_get_zero_collision_evidence(self):
        perturbed = self.model.start.copy()
        perturbed[0] += 0.1
        strategy = Strategy(self.model, self.env, "NR")
        result = strategy.qualify(perturbed)
        self.assertFalse(result["valid"])
        self.assertEqual(result["reason"], "CLOSURE_RESIDUAL")
        self.assertIsNone(result["collision"])
        self.assertEqual(strategy.counters.get("collision_queries", 0), 0)

    def test_bounded_failure_keeps_verified_prefix(self):
        # Endpoints pass, but the declared one-midpoint budget is intentionally
        # insufficient for a .05rad leaf mesh over this registered connection.
        result = rbs_connect(self.model, self.env, "PCS", self.model.start, self.model.goal,
                             {"rbs_max_projections": 1})
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "RBS_PROJECTION_LIMIT")
        self.assertGreaterEqual(len(result["verified_prefix"]), 1)
        self.assertEqual(result["path"], [])
        self.assertTrue(result["trials"])

    def test_pcs_midpoint_budget_is_total_across_partition_trials(self):
        # Explicit interface mock, not real closure/GEOS/planning evidence.
        # Force the first partition to reject its only projection. The second
        # partition must not receive a fresh budget of one more projection.
        class BudgetContractModel:
            n = 20
            partitions = (0, 16)

            @staticmethod
            def branch(q, partition):
                return 1

            @staticmethod
            def closure(q):
                return np.array([0.1, 0.0, 0.0])

            @staticmethod
            def valid(q, env):
                return {"valid": True, "reason": "SYNTHETIC_INTERFACE_MOCK",
                        "collision": {"collision": False, "geometry_queries": 0,
                                      "source": "UNIT_TEST_MOCK_NOT_GEOS"}}

            @staticmethod
            def ik(q, partition, branch):
                return IKResult(False, None, "SYNTHETIC_IK_FAILURE", branch=branch)

        start = np.zeros(20)
        goal = start.copy()
        goal[0] = 0.2
        strategy = Strategy(BudgetContractModel(), "UNIT_TEST_ONLY", "PCS", {"rbs_max_projections": 1})
        result = rbs_connect(strategy.model, strategy.env, "PCS", start, goal, strategy=strategy)
        self.assertFalse(result["success"])
        self.assertEqual(result["projection_calls"], 1)
        self.assertEqual(len(result["trials"]), 2)
        self.assertEqual(result["trials"][0]["projection_calls"], 1)
        self.assertEqual(result["trials"][1]["projection_calls"], 0)
        self.assertEqual(result["reason"], "RBS_PROJECTION_LIMIT")
        self.assertEqual(strategy.counters["ik_solver_calls"], 1)
        self.assertEqual(strategy.counters.get("nr_calls", 0), 0)

    def test_time_limit_is_not_projection_or_geometry_infeasibility(self):
        result = nr_project(self.model, self.model.start, expired=lambda: True)
        self.assertFalse(result.success)
        self.assertEqual(result.reason, "TIME_LIMIT")
        strategy = Strategy(self.model, self.env, "NR", expired=lambda: True)
        checked = strategy.qualify(self.model.start)
        self.assertEqual(checked, {"valid": False, "reason": "TIME_LIMIT"})


if __name__ == "__main__":
    unittest.main()
