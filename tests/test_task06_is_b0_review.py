"""Pure synthetic diagnostic tests, not actual FR3/FCL/physics tests."""
import unittest

import numpy as np

from scripts.review_task06_is_b0_path import analyze


class FixedPathReviewTests(unittest.TestCase):
    def test_margin_and_original_angle_no_periodic_wrap(self):
        result, arrays, _ = analyze([[0., 2.8], [.1, 2.99]], [-1, -3], [1, 3], ["L", "R"])
        self.assertEqual(result["critical"]["point_index"], 1)
        self.assertEqual(result["critical"]["joint_name"], "R")
        self.assertEqual(result["critical"]["nearest_bound"], "UPPER")
        self.assertAlmostEqual(result["critical"]["min_margin_rad"], .01)
        self.assertEqual(arrays["q"][1, 1], 2.99)

    def test_travel_detour_reversals_and_zero_delta(self):
        result, arrays, reversal = analyze([[0.], [1.], [1.], [-1.], [0.]], [-2], [2], ["q"])
        row = result["joints"][0]
        self.assertEqual(row["cumulative_travel_rad"], 4.)
        self.assertEqual(row["net_displacement_rad"], 0.)
        self.assertIsNone(row["travel_to_net_ratio"])
        self.assertEqual(row["raw_direction_reversals"], 2)
        self.assertEqual(row["filtered_direction_reversals"], 2)
        self.assertEqual(reversal[0]["filtered"][0]["turn_point_index"], 1)
        self.assertEqual(reversal[0]["filtered"][0]["plateau_end_point_index"], 2)
        self.assertEqual(arrays["cumulative"][-1, 0], 4.)

    def test_raw_and_diagnostic_noise_are_separate(self):
        result, _, _ = analyze([[0.], [1e-10], [0.], [.1]], [-1], [1], ["q"])
        self.assertEqual(result["joints"][0]["raw_direction_reversals"], 2)
        self.assertEqual(result["joints"][0]["filtered_direction_reversals"], 0)

    def test_single_point_and_stable_tie_choice(self):
        result, _, _ = analyze([[0., 0.]], [-1, -1], [1, 1], ["a", "b"])
        self.assertEqual(result["critical"]["joint_name"], "a")
        self.assertEqual(result["path_joint_l2_length_rad"], 0.)
        self.assertEqual(result["max_adjacent_l2_rad"], 0.)
        self.assertEqual(result["top_adjacent_edges"], [])

    def test_adjacent_vector_and_top_order(self):
        result, _, _ = analyze([[0., 0.], [.3, .4], [0., 0.]], [-1, -1], [1, 1], ["a", "b"])
        self.assertAlmostEqual(result["max_adjacent_l2_rad"], .5)
        self.assertAlmostEqual(result["max_adjacent_linf_rad"], .4)
        self.assertEqual([row["edge_index"] for row in result["top_adjacent_edges"]], [0, 1])

    def test_invalid_inputs_rejected(self):
        for q, low, high, names in (([], [-1], [1], ["a"]),
                                    ([[float("nan")]], [-1], [1], ["a"]),
                                    ([[float("inf")]], [-1], [1], ["a"]),
                                    ([[2.]], [-1], [1], ["a"]),
                                    ([[0., 0.]], [-1, -1], [1, 1], ["a", "a"]),
                                    ([[0.]], [1], [-1], ["a"])):
            with self.subTest(q=q), self.assertRaises(ValueError):
                analyze(q, low, high, names)

    def test_same_input_same_numeric_output_and_no_input_mutation(self):
        q = np.array([[0.], [.2], [.1]])
        before = q.copy()
        a, _, reversal_a = analyze(q, [-1], [1], ["a"])
        b, _, reversal_b = analyze(q, [-1], [1], ["a"])
        self.assertEqual(a, b)
        self.assertEqual(reversal_a, reversal_b)
        np.testing.assert_array_equal(q, before)


if __name__ == "__main__":
    unittest.main()
