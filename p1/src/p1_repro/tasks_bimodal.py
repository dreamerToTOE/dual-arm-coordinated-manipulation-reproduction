"""Two-corridor task for the two-stage mode-selection experiments (D1-D3, F1).

A point mass starts at ``(-1, 0)`` and must reach ``(+1, 0)``.  A wall at
``x = 0`` blocks ``|y| <= 0.25``, so there are exactly two feasible modes:
pass above or pass below.  The mode label is analytic (the sign of ``y`` where
the trajectory crosses ``x = 0``), which gives an oracle for clustering.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .cost import CostConfig, stagnation_cost


@dataclass
class BimodalTask:
    horizon: int = 25
    dt: float = 0.1
    start: np.ndarray = field(default_factory=lambda: np.array([-0.8, 0.0]))
    goal: np.ndarray = field(default_factory=lambda: np.array([0.8, 0.0]))
    wall_half_width: float = 0.25
    wall_thickness: float = 0.03
    margin: float = 0.05
    u_max: float = 1.0
    cfg: CostConfig = field(default_factory=CostConfig.paper)
    p_goal: float = 100.0
    p_stay: float = 0.125

    def rollout(self, U: np.ndarray) -> dict:
        """``U`` (M, N, 2) -> positions, collision flags, mode labels."""
        M, N, _ = U.shape
        P = np.empty((M, N + 1, 2))
        P[:, 0, :] = self.start
        Uc = np.clip(U, -self.u_max, self.u_max)
        for k in range(N):
            P[:, k + 1, :] = P[:, k, :] + self.dt * Uc[:, k, :]

        # Collision: sample the segment of every step (3 interior points) and
        # test the inflated wall rectangle.
        frac = np.array([0.25, 0.5, 0.75])
        seg = P[:, :-1, :][:, :, None, :] + frac[None, None, :, None] * (
            P[:, 1:, :] - P[:, :-1, :]
        )[:, :, None, :]
        inside = (
            (np.abs(seg[..., 0]) < 0.5 * self.wall_thickness + self.margin)
            & (np.abs(seg[..., 1]) < self.wall_half_width + self.margin)
        ).any(axis=(1, 2))

        # Mode label: sign of y at the point closest to x = 0.
        idx = np.argmin(np.abs(P[..., 0]), axis=1)
        y_at_wall = P[np.arange(M), idx, 1]
        crossed = np.abs(P[np.arange(M), idx, 0]) < 0.2
        label = np.where(crossed, np.sign(y_at_wall), 0.0).astype(int)

        goal_err = np.linalg.norm(P[:, -1, :] - self.goal, axis=1, keepdims=True)
        goal_cost = self.p_goal * goal_err
        collision = self.cfg.p_ec * inside[:, None].astype(float)
        delta = P[:, -1, :] - self.start
        stay = stagnation_cost(goal_cost, delta, self.cfg)
        cost = goal_cost + collision + stay
        return {
            "pos": P,
            "cost": cost,
            "goal": goal_cost,
            "collision": inside[:, None],
            "label": label,
            "goal_error": goal_err,
            "delta": delta,
            "u": Uc,
        }

    def descriptor(self, diag: dict) -> np.ndarray:
        """Compact kinematic summary: mean lateral offset of the trajectory.

        The paper uses the net joint change ``Theta_0 - Theta_N``.  In this 2-D
        task both detours end at the same point, so the net displacement is
        degenerate; the mean lateral offset plays the same role (positive =
        above the wall, negative = below) and is still a kinematic quantity,
        not the mode label.
        """
        lateral = diag["pos"][:, :, 1].mean(axis=1, keepdims=True)
        # The cost column is deliberately omitted: with a 1500 collision penalty
        # it dominates the descriptor and k-means splits "collided vs not"
        # instead of "above vs below" (measured accuracy drops from 0.88 to
        # 0.65 when it is included at weight 0.2).
        return lateral

    def success(self, diag) -> np.ndarray:
        return ((diag["goal_error"][:, 0] < 0.05) & (~diag["collision"][:, 0])).astype(bool)

    def seed_plan(self, direction: float = 1.0, height: float = 0.5) -> np.ndarray:
        """Feasible nominal plan: a half-sine detour above/below the wall.

        Used as the "previous cycle optimum" from which both controllers start,
        matching the paper's warm-started sampling rather than a cold start.
        """
        t = np.linspace(0.0, 1.0, self.horizon + 1)
        x = self.start[0] + (self.goal[0] - self.start[0]) * t
        y = direction * height * np.sin(np.pi * t)
        P = np.stack([x, y], axis=1)
        U = np.diff(P, axis=0) / self.dt
        return np.clip(U, -self.u_max, self.u_max)

    def nominal_u(self) -> np.ndarray:
        """Zero-mean initial sequence."""
        return np.zeros((self.horizon, 2))

    def jitter(self, U: np.ndarray) -> np.ndarray:
        """Total variation of the control sequence, per sample."""
        return np.sum(np.linalg.norm(np.diff(U, axis=1), axis=-1), axis=1)
