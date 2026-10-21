"""Cost terms of the paper (Eqs. 32-43) and the two parameter sets.

``paper`` follows Table I; ``code`` follows the shipped example YAML.  The
differences are documented in ``P1_EQUATION_AUDIT.md`` section 10 and are kept
explicit rather than averaged away.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def l1(x: np.ndarray) -> np.ndarray:
    """Sum of absolute values over the last axis, shape ``(..., 1)``."""
    return np.sum(np.abs(x), axis=-1, keepdims=True)


@dataclass(frozen=True)
class CostConfig:
    name: str = "paper"
    p_ec: float = 1500.0
    p_sc: float = 1500.0
    p_tilt: float = 1500.0
    p_goal: float = 100.0
    p_sing: float = 10.0
    p_vel: float = 0.0
    p_acc: float = 0.0
    p_stay: float = 0.125
    tilt_max_deg: float = 8.0
    stagnation_mode: str = "paper"  # "paper" or "code"
    position_weight: float = 0.0

    @staticmethod
    def paper() -> "CostConfig":
        return CostConfig()

    @staticmethod
    def code() -> "CostConfig":
        return CostConfig(
            name="code",
            p_sing=0.5,
            p_stay=10.0,
            stagnation_mode="code",
            position_weight=100.0,
        )


def terminal_goal_cost(
    xa: np.ndarray,
    xa_d: np.ndarray,
    pos: np.ndarray,
    pos_d: np.ndarray,
    cfg: CostConfig,
) -> np.ndarray:
    """``p_g ||vec8(x_a,N - x_a,d)||_1`` (Eq. 38), plus the optional code term.

    The code adds ``position_weight * ||p_d - p||_1`` on top of the 8-vector
    difference, so translation is penalised twice.  ``paper`` keeps that term
    at zero.
    """
    cost = cfg.p_goal * l1(xa_d - xa)
    if cfg.position_weight:
        cost = cost + cfg.position_weight * l1(pos_d - pos)
    return cost


def tilt_cost(angle_deg: np.ndarray, cfg: CostConfig) -> np.ndarray:
    """Indicator penalty outside the tilt range (Eq. 32)."""
    over = (angle_deg < -cfg.tilt_max_deg) | (angle_deg > cfg.tilt_max_deg)
    return cfg.p_tilt * over.astype(float)


def collision_cost(min_distance: np.ndarray, threshold: float, weight: float) -> np.ndarray:
    """Indicator penalty when a sphere pair is closer than ``threshold`` (Eq. 33)."""
    return weight * (min_distance < threshold).astype(float)


def velocity_cost(u: np.ndarray, cfg: CostConfig) -> np.ndarray:
    """``p_v * sum_k ||u_k||_1`` (Eq. 39)."""
    return cfg.p_vel * np.sum(np.abs(u), axis=(-2, -1))[..., None]


def accel_cost(u: np.ndarray, dt: float, cfg: CostConfig) -> np.ndarray:
    """``p_a * sum_k ||(u_k - u_{k-1})/dt||_1`` (Eq. 40)."""
    du = np.diff(u, axis=-2) / dt
    return cfg.p_acc * np.sum(np.abs(du), axis=(-2, -1))[..., None]


def stagnation_cost(goal_cost: np.ndarray, delta_q: np.ndarray, cfg: CostConfig) -> np.ndarray:
    """Anti-stagnation term (Eq. 42).

    ``paper``:  ``p_s * C_goal / max(zeta, ||dq||_1)``
    ``code`` :  ``C_goal / (p_s * max(1e-3, ||dq||_2^2))``
    """
    if cfg.stagnation_mode == "paper":
        denom = np.maximum(1e-6, np.sum(np.abs(delta_q), axis=-1, keepdims=True))
        return cfg.p_stay * goal_cost / denom
    denom = np.maximum(1e-3, np.sum(delta_q * delta_q, axis=-1, keepdims=True))
    return goal_cost / (cfg.p_stay * denom)
