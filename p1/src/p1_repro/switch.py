"""Auxiliary controller and unexplored-degree indicator (paper Eqs. 44-49)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def auxiliary_control(error: np.ndarray, gain: float, dt: float) -> np.ndarray:
    """Explicit-Euler proportional correction ``e <- e - dt * K * e``.

    The paper writes ``u_a = J_a^+ K_a e_a`` and integrates with ``T_h``; for a
    single task direction this reduces to the first-order update used here.
    """
    return error - dt * gain * error


def decay_rate_fit(history: np.ndarray, dt: float) -> float:
    """Fit ``-d/dt log||e||`` from a trajectory of error vectors."""
    norms = np.linalg.norm(history, axis=-1)
    norms = np.maximum(norms, 1e-15)
    t = dt * np.arange(len(norms))
    slope = np.polyfit(t, np.log(norms), 1)[0]
    return float(-slope)


@dataclass
class UnexploredIndicator:
    """``L_{k+1} = clip(L_k + dt (C_t/C_s - eta), L_min, L_max)`` (Eqs. 47-48)."""

    eta: float = 0.1
    l_min: float = -0.05
    l_max: float = 0.4
    dt: float = 0.15
    value: float = 0.0

    def update(self, ratio: float) -> float:
        self.value = float(np.clip(self.value + self.dt * (ratio - self.eta), self.l_min, self.l_max))
        return self.value

    @property
    def use_sampling(self) -> bool:
        """Eq. (49): sampling control while ``L >= 0``."""
        return self.value >= 0.0

    def dwell_time_to(self, target: float, ratio: float, max_steps: int = 10**6) -> int:
        """Number of control steps needed to cross ``target`` at a constant ratio."""
        n = 0
        while (self.value > target) if self.value > target else (self.value < target):
            self.update(ratio)
            n += 1
            if n >= max_steps:
                break
        return n
