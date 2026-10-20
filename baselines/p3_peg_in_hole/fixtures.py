"""P3 illustrative fixtures — NOT paper values.

The paper (Lee et al., RA-L 2022) reports no numeric values for the
perturbation amplitudes, frequencies, spiral modulation, damping, gains
(except the hole-arm scalar range 500 <= k_p <= 1000), Jacobian, error
trajectory, gravity or friction compensation. Every number here is an
explicit TEST_FIXTURE used to exercise the algorithms; none of them is
claimed to reproduce the paper's experiments.
"""
from __future__ import annotations

import numpy as np

TEST_FIXTURE = {
    # Eq.(19)-(22) pattern parameters (illustrative only)
    "f_push_N": 10.0,
    "f_rub_Nm": 0.30,
    "v_rub_rad_s": 2.0 * np.pi * 1.5,
    "f_wiggle_Nm": 0.25,
    "v_wiggle_rad_s": 2.0 * np.pi * 1.0,
    "alpha_N": 2.0,
    "beta_N": 3.0,
    "v_spiral_rad_s": 2.0 * np.pi * 0.5,
    # Eq.(27) gains: hole arm anchor 500 <= k_p <= 1000 is the only paper value;
    # the peg arm is described only as "low" gain.
    "k_p_hole_translation_N_m": 600.0,     # inside the paper's stated range
    "k_p_hole_rotation_Nm_rad": 30.0,      # TEST_FIXTURE
    "k_p_peg_translation_N_m": 120.0,      # TEST_FIXTURE ("low")
    "k_p_peg_rotation_Nm_rad": 8.0,        # TEST_FIXTURE ("low")
    "damping_Nm_s_rad": 2.0,               # TEST_FIXTURE
    "tau_gravity_Nm": (0.0, -8.0, 5.0, 2.0, 0.0, -1.0, 0.0),   # TEST_FIXTURE posture
    "tau_friction_Nm": (0.2, -0.2, 0.1, 0.0, 0.1, -0.1, 0.0),  # TEST_FIXTURE constant
    # Kinematics surrogate: J = [I6 | b] (6x7, full rank). TEST_FIXTURE, not a robot.
    "jacobian_redundancy_column": (0.3, -0.2, 0.1, 0.05, -0.1, 0.02),
}

# Stage boundaries digitized qualitatively from Fig.9 (case 1):
# approaching ends ~3.2 s, searching ~3.2-10.5 s, aligning ~10.5-16.5 s,
# insertion ~16.5-17.5 s. [ADAPTATION: approximate digitization]
STAGE_BOUNDARIES_CASE1_S = (0.0, 3.2, 10.5, 16.5, 17.5)
# Cases 2-4 are not shown on a time axis in the paper: illustrative only.
STAGE_BOUNDARIES_CASE2_S = (0.0, 3.5, 9.0, 14.0)
STAGE_BOUNDARIES_CASE3_S = (0.0, 3.0, 12.0, 16.5)
STAGE_BOUNDARIES_CASE4_S = (0.0, 4.0, 8.0)


def pattern_set():
    """Build the four paper patterns with TEST_FIXTURE parameters."""
    from .patterns import Push, Rub, Spiral, Wiggle

    return {
        "push": Push(TEST_FIXTURE["f_push_N"]),
        "rub": Rub(TEST_FIXTURE["f_rub_Nm"], TEST_FIXTURE["v_rub_rad_s"]),
        "wiggle": Wiggle(TEST_FIXTURE["f_wiggle_Nm"], TEST_FIXTURE["v_wiggle_rad_s"]),
        "spiral": Spiral(TEST_FIXTURE["alpha_N"], TEST_FIXTURE["beta_N"],
                         TEST_FIXTURE["v_spiral_rad_s"]),
    }


def gains(arm: str = "peg") -> np.ndarray:
    tr = TEST_FIXTURE[f"k_p_{arm}_translation_N_m"]
    ro = TEST_FIXTURE[f"k_p_{arm}_rotation_Nm_rad"]
    return np.diag([tr, tr, tr, ro, ro, ro])


def damping(n: int = 7) -> np.ndarray:
    return TEST_FIXTURE["damping_Nm_s_rad"] * np.eye(n)


def gravity(n: int = 7) -> np.ndarray:
    return np.asarray(TEST_FIXTURE["tau_gravity_Nm"], dtype=float)[:n]


def friction(n: int = 7) -> np.ndarray:
    return np.asarray(TEST_FIXTURE["tau_friction_Nm"], dtype=float)[:n]


def jacobian(n: int = 7) -> np.ndarray:
    """J = [I6 | b]: a full-rank 6x7 surrogate, TEST_FIXTURE (no robot model)."""
    b = np.asarray(TEST_FIXTURE["jacobian_redundancy_column"], dtype=float)
    return np.hstack([np.eye(6), b.reshape(6, 1)])


def singular_jacobian() -> np.ndarray:
    """Rank-deficient 6x7 Jacobian: the last row is identically zero."""
    J = jacobian().copy()
    J[5, :] = 0.0
    return J
