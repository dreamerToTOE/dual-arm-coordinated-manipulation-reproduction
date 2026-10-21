"""Independent SE(3) reference implementation (rotation matrices + translations).

This module is deliberately written without dual quaternions: it is the
independent oracle for the DQ kinematics in ``dq.py`` / ``kinematics.py``.
Batched over leading axes.
"""

from __future__ import annotations

import numpy as np

from .dq import q_from_rotmat, q_to_rotmat, qexp


def hat(w: np.ndarray) -> np.ndarray:
    w = np.asarray(w, dtype=float)
    x, y, z = np.moveaxis(w, -1, 0)
    zero = np.zeros_like(x)
    return np.stack(
        [
            np.stack([zero, -z, y], axis=-1),
            np.stack([z, zero, -x], axis=-1),
            np.stack([-y, x, zero], axis=-1),
        ],
        axis=-2,
    )


def cross(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a0, a1, a2 = np.moveaxis(a, -1, 0)
    b0, b1, b2 = np.moveaxis(b, -1, 0)
    return np.stack(
        [a1 * b2 - a2 * b1, a2 * b0 - a0 * b2, a0 * b1 - a1 * b0], axis=-1
    )


def exp_so3(w: np.ndarray) -> np.ndarray:
    """Rodrigues formula, batched; robust at zero."""
    w = np.asarray(w, dtype=float)
    theta = np.linalg.norm(w, axis=-1, keepdims=True)
    small = theta < 1e-12
    safe = np.where(small, 1.0, theta)
    # K is the skew matrix of the *unit* axis for the regular branch and of
    # the (small) rotation vector for the near-zero branch, hence s = sin(theta)
    # and c = 1 - cos(theta) rather than the unnormalised-hat coefficients.
    K = hat(w / safe)
    K2 = K @ K
    s = np.where(small, 1.0, np.sin(safe))
    c = np.where(small, 0.5, 1.0 - np.cos(safe))
    eye = np.broadcast_to(np.eye(3), K.shape)
    return eye + s[..., None] * K + c[..., None] * K2


def log_so3(R: np.ndarray) -> np.ndarray:
    """Rotation logarithm via the quaternion branch (stable near pi)."""
    q = q_from_rotmat(R)
    v = q[..., 1:]
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    w = np.clip(q[..., :1], -1.0, 1.0)
    angle = 2.0 * np.arctan2(n, w)
    scale = np.where(n < 1e-12, 2.0, angle / np.where(n < 1e-12, 1.0, n))
    return scale * v


def v_matrix(w: np.ndarray) -> np.ndarray:
    """Left Jacobian ``V(w)`` of SO(3), batched."""
    theta = np.linalg.norm(w, axis=-1, keepdims=True)
    small = theta < 1e-8
    safe = np.where(small, 1.0, theta)
    K = hat(w)
    K2 = K @ K
    a = np.where(small, 0.5, (1.0 - np.cos(safe)) / (safe * safe))
    b = np.where(small, 1.0 / 6.0, (safe - np.sin(safe)) / (safe**3))
    eye = np.broadcast_to(np.eye(3), K.shape)
    return eye + a[..., None] * K + b[..., None] * K2


def v_inverse(w: np.ndarray) -> np.ndarray:
    """Inverse of ``V(w)``, batched."""
    theta = np.linalg.norm(w, axis=-1, keepdims=True)
    small = theta < 1e-6
    safe = np.where(small, 1.0, theta)
    K = hat(w)
    K2 = K @ K
    # 1/theta^2 * (1 - theta / (2 tan(theta/2))) has a finite limit 1/12.
    coeff = np.where(
        small,
        1.0 / 12.0,
        (1.0 - safe / (2.0 * np.tan(safe / 2.0))) / (safe * safe),
    )
    eye = np.broadcast_to(np.eye(3), K.shape)
    return eye - 0.5 * K + coeff[..., None] * K2


def se3_exp(xi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """``xi = [omega, v]`` (..., 6) -> ``(R, t)``."""
    xi = np.asarray(xi, dtype=float)
    w, v = xi[..., :3], xi[..., 3:]
    R = exp_so3(w)
    t = np.einsum("...ij,...j->...i", v_matrix(w), v)
    return R, t


def se3_log(R: np.ndarray, t: np.ndarray) -> np.ndarray:
    """``(R, t)`` -> ``[omega, v]`` (..., 6)."""
    w = log_so3(R)
    v = np.einsum("...ij,...j->...i", v_inverse(w), t)
    return np.concatenate([w, v], axis=-1)


def se3_mul(T1: tuple[np.ndarray, np.ndarray], T2: tuple[np.ndarray, np.ndarray]):
    R1, t1 = T1
    R2, t2 = T2
    return R1 @ R2, np.einsum("...ij,...j->...i", R1, t2) + t1


def se3_inv(T: tuple[np.ndarray, np.ndarray]):
    R, t = T
    Rt = np.swapaxes(R, -1, -2)
    return Rt, -np.einsum("...ij,...j->...i", Rt, t)


def se3_sqrt(T: tuple[np.ndarray, np.ndarray]):
    """SE(3) square root: ``exp(0.5 * log(T))``."""
    R, t = T
    xi = se3_log(R, t)
    return se3_exp(0.5 * xi)


def se3_from_quat(q: np.ndarray, t: np.ndarray):
    return q_to_rotmat(q), t


def quat_from_R(R: np.ndarray) -> np.ndarray:
    return q_from_rotmat(R)
