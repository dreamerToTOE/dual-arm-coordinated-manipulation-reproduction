"""Null-space equality handling (paper Eqs. 26-31).

The projector is the damped version used by the official kernel:

    N = I - J^T (J J^T + eps I)^{-1} J

with ``eps = 1e-16`` in float64.  The same file also implements the
deterministic map ``g`` (velocity clamp -> Euler step -> position clamp ->
allowed velocity), matching the order in ``mppi_project_step``.
"""

from __future__ import annotations

import numpy as np


def damped_pinv(J: np.ndarray, eps: float = 1e-16) -> np.ndarray:
    """``J^+ = J^T (J J^T + eps I)^{-1}`` (the official kernel's formula).

    Kept for fidelity comparisons.  For an 8-row dual-quaternion Jacobian the
    last two singular values are structurally zero, so ``eps = 1e-16`` makes
    ``J J^T + eps I`` have condition number ~1e16 and the float64 inverse is
    unusable; see ``pinv`` for the numerically defined Moore-Penrose inverse.
    """
    J = np.asarray(J, dtype=float)
    rows = J.shape[-2]
    JJt = J @ np.swapaxes(J, -1, -2)
    reg = eps * np.eye(rows)
    inv = np.linalg.inv(JJt + reg)
    return np.swapaxes(J, -1, -2) @ inv


def pinv(J: np.ndarray, rcond: float = 1e-10) -> np.ndarray:
    """Moore-Penrose pseudoinverse via SVD with a relative rank cut-off.

    For the 8 x n dual-quaternion Jacobian the rank is 6; truncating the two
    structural zero singular values gives the orthogonal projector that the
    paper's ``I - J^+ J`` denotes.
    """
    J = np.asarray(J, dtype=float)
    U, s, Vt = np.linalg.svd(J, full_matrices=False)
    cut = rcond * np.max(s, axis=-1, keepdims=True)
    s_inv = np.where(s > cut, 1.0 / np.where(s > cut, s, 1.0), 0.0)
    return (np.swapaxes(Vt, -1, -2) * s_inv[..., None, :]) @ np.swapaxes(U, -1, -2)


def null_projector(J: np.ndarray, rcond: float = 1e-10) -> np.ndarray:
    """``N = I - J^+ J``, shape (..., n, n), with the SVD pseudoinverse."""
    n = J.shape[-1]
    eye = np.broadcast_to(np.eye(n), J.shape[:-2] + (n, n))
    return eye - pinv(J, rcond) @ J


def project_velocity(J: np.ndarray, u: np.ndarray, rcond: float = 1e-10) -> np.ndarray:
    """``u_null = N u`` (paper Eq. 26)."""
    return np.einsum("...ij,...j->...i", null_projector(J, rcond), u)


def g_map(
    q1: np.ndarray,
    q2: np.ndarray,
    u1: np.ndarray,
    u2: np.ndarray,
    dq_min1,
    dq_max1,
    dq_min2,
    dq_max2,
    q_min1,
    q_max1,
    q_min2,
    q_max2,
    dt: float,
):
    """Deterministic limit map ``g`` + Euler step (paper Eq. 28, 31).

    Order: velocity clamp, integrate, position clamp, allowed-velocity
    recomputation.  Returns the next positions and the velocity that was
    actually realised.
    """
    u1 = np.clip(u1, dq_min1, dq_max1)
    u2 = np.clip(u2, dq_min2, dq_max2)
    q1_next = np.clip(q1 + dt * u1, q_min1, q_max1)
    q2_next = np.clip(q2 + dt * u2, q_min2, q_max2)
    u1_allowed = (q1_next - q1) / dt
    u2_allowed = (q2_next - q2) / dt
    return q1_next, q2_next, u1_allowed, u2_allowed


def project_step(
    J: np.ndarray,
    u1: np.ndarray,
    u2: np.ndarray,
    q1: np.ndarray,
    q2: np.ndarray,
    dq_min1,
    dq_max1,
    dq_min2,
    dq_max2,
    q_min1,
    q_max1,
    q_min2,
    q_max2,
    dt: float,
):
    """Full rollout step: null-space projection then ``g``."""
    u = np.concatenate([u1, u2], axis=-1)
    u_proj = project_velocity(J, u)
    u1p, u2p = u_proj[..., : u1.shape[-1]], u_proj[..., u1.shape[-1] :]
    return g_map(q1, q2, u1p, u2p, dq_min1, dq_max1, dq_min2, dq_max2, q_min1, q_max1, q_min2, q_max2, dt)


def relative_pose_error(xr: np.ndarray, xr_d: np.ndarray) -> np.ndarray:
    """``vec8(x_r,d - x_r)`` as used by the paper's inner loops."""
    return xr_d - xr
