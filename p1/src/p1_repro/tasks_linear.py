"""Linear-quadratic test task with an exact finite-horizon Riccati oracle (C1)."""

from __future__ import annotations

import numpy as np


class LinearQuadraticTask:
    """2-D double integrator: state ``[p_x, p_y, v_x, v_y]``, control ``[a_x, a_y]``."""

    def __init__(self, dt: float = 0.1, horizon: int = 20, q: float = 10.0, r: float = 0.1, qf: float = 1000.0):
        self.dt = dt
        self.N = horizon
        I = np.eye(2)
        self.A = np.block([[I, dt * I], [np.zeros((2, 2)), I]])
        self.B = np.vstack([0.5 * dt * dt * I, dt * I])
        self.Q = q * np.eye(4)
        self.R = r * np.eye(2)
        self.Qf = qf * np.eye(4)
        self.n = 4
        self.m = 2

    def rollout(self, U: np.ndarray, x0: np.ndarray) -> np.ndarray:
        """``U`` (M, N, 2) -> states (M, N+1, 4)."""
        M = U.shape[0]
        X = np.empty((M, self.N + 1, self.n))
        X[:, 0, :] = x0
        for k in range(self.N):
            X[:, k + 1, :] = X[:, k, :] @ self.A.T + U[:, k, :] @ self.B.T
        return X

    def cost(self, U: np.ndarray, x0: np.ndarray) -> np.ndarray:
        X = self.rollout(U, x0)
        stage = np.einsum("mki,ij,mkj->m", X[:, :-1], self.Q, X[:, :-1])
        ctrl = np.einsum("mki,ij,mkj->m", U, self.R, U)
        terminal = np.einsum("mi,ij,mj->m", X[:, -1], self.Qf, X[:, -1])
        return (stage + ctrl + terminal)[:, None]

    def lqr_cost(self, x0: np.ndarray) -> float:
        """Exact finite-horizon cost by backward Riccati recursion."""
        P = self.Qf
        for _ in range(self.N):
            S = self.R + self.B.T @ P @ self.B
            K = np.linalg.solve(S, self.B.T @ P @ self.A)
            P = self.Q + self.A.T @ P @ (self.A - self.B @ K)
        return float(x0 @ P @ x0)


def run_mppi(
    task: LinearQuadraticTask,
    x0: np.ndarray,
    rng: np.random.Generator,
    samples: int = 2000,
    iterations: int = 60,
    std: float = 0.5,
    lam: float = 0.5,
    target: tuple[float, float] = (22.0, 30.0),
) -> dict:
    from .sampler import adaptive_weights, effective_sample_size, gaussian, weighted_noise

    u_mean = np.zeros((task.N, task.m))
    history = []
    m_eff = []
    for _ in range(iterations):
        eps = gaussian(rng, (samples, task.N, task.m), std)
        U = u_mean[None, :, :] + eps
        costs = task.cost(U, x0)
        w, lam = adaptive_weights(costs, lam, target)
        u_mean = u_mean + weighted_noise(eps, w)
        history.append(float(task.cost(u_mean[None], x0)[0, 0]))
        m_eff.append(effective_sample_size(w))
    final_cost = float(task.cost(u_mean[None], x0)[0, 0])
    return {
        "cost": final_cost,
        "best_sample_cost": float(history[-1]),
        "history": history,
        "mean_effective_samples": float(np.mean(m_eff)),
        "u_mean": u_mean,
    }
