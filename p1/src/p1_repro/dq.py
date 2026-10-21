"""Dual-quaternion algebra used by the P1 numerical reproduction.

Implements paper Eqs. (1)-(6): quaternions, dual quaternions, unit dual
quaternions ``x = r + eps * (1/2) * p * r``, and the ``vec8`` ordering
``[r_w, r_x, r_y, r_z, d_w, d_x, d_y, d_z]``.

All functions are batched over leading axes; the algebra axis is the last one
(4 for quaternions, 8 for dual quaternions).  Nothing here depends on GPU,
ROS, cuRobo, dqrobotics or the official implementation.
"""

from __future__ import annotations

import numpy as np

EPS = np.finfo(float).eps


# ---------------------------------------------------------------------------
# Quaternions (Hamilton convention, scalar first: w, x, y, z)
# ---------------------------------------------------------------------------
def qmul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Hamilton product ``a * b`` for quaternions with last axis 4.

    Written with direct component indexing (no ``moveaxis``) because this is
    the innermost operation of every rollout.
    """
    a0, a1, a2, a3 = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    b0, b1, b2, b3 = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    return np.stack(
        [
            a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3,
            a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
            a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1,
            a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0,
        ],
        axis=-1,
    )


def qconj(q: np.ndarray) -> np.ndarray:
    out = np.array(q, copy=True)
    out[..., 1:] *= -1.0
    return out


def qnorm(q: np.ndarray) -> np.ndarray:
    return np.linalg.norm(q, axis=-1, keepdims=True)


def qnormalize(q: np.ndarray) -> np.ndarray:
    n = qnorm(q)
    return q / np.where(n < 1e-15, 1.0, n)


def qlog(q: np.ndarray) -> np.ndarray:
    """Quaternion logarithm; returns a pure quaternion ``(0, axis * angle/2)``.

    Handles both the small-angle and the angle-near-pi branches.
    """
    q = qnormalize(q)
    w = np.clip(q[..., :1], -1.0, 1.0)
    v = q[..., 1:]
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    angle = 2.0 * np.arctan2(n, w)
    scale = np.where(n < 1e-12, 0.5, 0.5 * angle / np.where(n < 1e-12, 1.0, n))
    return np.concatenate([np.zeros_like(w), scale * v], axis=-1)


def qexp(p: np.ndarray) -> np.ndarray:
    """Quaternion exponential of a pure quaternion."""
    v = p[..., 1:]
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    small = n < 1e-12
    safe_n = np.where(small, 1.0, n)
    w = np.where(small, 1.0, np.cos(n))
    s = np.where(small, 1.0, np.sin(n) / safe_n)
    return np.concatenate([w, s * v], axis=-1)


def q_from_rotmat(R: np.ndarray) -> np.ndarray:
    """Rotation matrix (..., 3, 3) -> unit quaternion (..., 4), w >= 0."""
    R = np.asarray(R, dtype=float)
    m00, m11, m22 = R[..., 0, 0], R[..., 1, 1], R[..., 2, 2]
    trace = m00 + m11 + m22
    q = np.zeros(R.shape[:-2] + (4,))

    # Four-branch Shepperd method, evaluated with masks (batched-safe).
    case0 = trace > 0.0
    s0 = np.sqrt(np.maximum(trace + 1.0, 1e-30)) * 2.0
    q0 = np.stack(
        [0.25 * s0, (R[..., 2, 1] - R[..., 1, 2]) / s0, (R[..., 0, 2] - R[..., 2, 0]) / s0, (R[..., 1, 0] - R[..., 0, 1]) / s0],
        axis=-1,
    )

    case1 = (~case0) & (m00 > m11) & (m00 > m22)
    s1 = np.sqrt(np.maximum(1.0 + m00 - m11 - m22, 1e-30)) * 2.0
    q1 = np.stack(
        [(R[..., 2, 1] - R[..., 1, 2]) / s1, 0.25 * s1, (R[..., 0, 1] + R[..., 1, 0]) / s1, (R[..., 0, 2] + R[..., 2, 0]) / s1],
        axis=-1,
    )

    case2 = (~case0) & (~case1) & (m11 > m22)
    s2 = np.sqrt(np.maximum(1.0 + m11 - m00 - m22, 1e-30)) * 2.0
    q2 = np.stack(
        [(R[..., 0, 2] - R[..., 2, 0]) / s2, (R[..., 0, 1] + R[..., 1, 0]) / s2, 0.25 * s2, (R[..., 1, 2] + R[..., 2, 1]) / s2],
        axis=-1,
    )

    case3 = (~case0) & (~case1) & (~case2)
    s3 = np.sqrt(np.maximum(1.0 + m22 - m00 - m11, 1e-30)) * 2.0
    q3 = np.stack(
        [(R[..., 1, 0] - R[..., 0, 1]) / s3, (R[..., 0, 2] + R[..., 2, 0]) / s3, (R[..., 1, 2] + R[..., 2, 1]) / s3, 0.25 * s3],
        axis=-1,
    )

    for case, val in ((case0, q0), (case1, q1), (case2, q2), (case3, q3)):
        q = np.where(case[..., None], val, q)
    q = qnormalize(q)
    # Canonical sign: w >= 0 (does not change the rotation).
    return np.where(q[..., :1] < 0.0, -q, q)


def q_to_rotmat(q: np.ndarray) -> np.ndarray:
    q = qnormalize(q)
    w, x, y, z = np.moveaxis(q, -1, 0)
    return np.stack(
        [
            np.stack([1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)], axis=-1),
            np.stack([2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)], axis=-1),
            np.stack([2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)], axis=-1),
        ],
        axis=-2,
    )


# ---------------------------------------------------------------------------
# Dual quaternions (last axis 8)
# ---------------------------------------------------------------------------
def dq_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Dual-quaternion product. ``(r1 + e d1)(r2 + e d2) = r1 r2 + e(r1 d2 + d1 r2)``."""
    ar, ad = a[..., :4], a[..., 4:]
    br, bd = b[..., :4], b[..., 4:]
    return np.concatenate([qmul(ar, br), qmul(ar, bd) + qmul(ad, br)], axis=-1)


def dq_conj(a: np.ndarray) -> np.ndarray:
    """Classical dual-quaternion conjugate; equals the inverse for unit inputs."""
    return np.concatenate([qconj(a[..., :4]), qconj(a[..., 4:])], axis=-1)


def dq_norm(a: np.ndarray) -> np.ndarray:
    """Dual norm ``sqrt(x x*)`` as an 8-vector (scalar part carries the norm)."""
    return dq_mul(a, dq_conj(a))


def dq_normalize(a: np.ndarray) -> np.ndarray:
    n2 = dq_mul(a, dq_conj(a))
    n = np.sqrt(np.maximum(n2[..., :1], 1e-30))
    out = a / n
    # Re-orthogonalise the dual part against the real part (r . d = 0).
    r = out[..., :4]
    d = out[..., 4:]
    d = d - r * np.sum(r * d, axis=-1, keepdims=True)
    return np.concatenate([qnormalize(r), d], axis=-1)


def dq_inv(a: np.ndarray) -> np.ndarray:
    """Inverse for unit dual quaternions (paper: conjugate == inverse)."""
    return dq_conj(dq_normalize(a))


def dq_from_rt(r: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Build ``x = r + eps (1/2) p r`` from a unit quaternion and a translation."""
    r = qnormalize(r)
    p = np.concatenate([np.zeros(t.shape[:-1] + (1,)), t], axis=-1)
    return np.concatenate([r, 0.5 * qmul(p, r)], axis=-1)


def dq_to_rt(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Decode a unit dual quaternion into ``(quaternion, translation)``."""
    x = dq_normalize(x)
    r = x[..., :4]
    d = x[..., 4:]
    p = 2.0 * qmul(d, qconj(r))
    return r, p[..., 1:]


def vec8(x: np.ndarray) -> np.ndarray:
    """Documented ``vec8`` ordering: ``[r(4), d(4)]``."""
    return x


def hamiplus8(x: np.ndarray) -> np.ndarray:
    """Left-multiplication matrix ``H+(x)`` with ``x * y = H+(x) y``."""
    x = np.asarray(x, dtype=float)
    Hr = _hamiplus4(x[..., :4])
    Hd = _hamiplus4(x[..., 4:])
    zero = np.zeros_like(Hr)
    return np.concatenate(
        [np.concatenate([Hr, zero], axis=-1), np.concatenate([Hd, Hr], axis=-1)], axis=-2
    )


def haminus8(x: np.ndarray) -> np.ndarray:
    """Right-multiplication matrix ``H-(x)`` with ``y * x = H-(x) y``."""
    x = np.asarray(x, dtype=float)
    Hr = _haminus4(x[..., :4])
    Hd = _haminus4(x[..., 4:])
    zero = np.zeros_like(Hr)
    return np.concatenate(
        [np.concatenate([Hr, zero], axis=-1), np.concatenate([Hd, Hr], axis=-1)], axis=-2
    )


def _hamiplus4(q: np.ndarray) -> np.ndarray:
    w, x, y, z = np.moveaxis(q, -1, 0)
    rows = [
        np.stack([w, -x, -y, -z], axis=-1),
        np.stack([x, w, -z, y], axis=-1),
        np.stack([y, z, w, -x], axis=-1),
        np.stack([z, -y, x, w], axis=-1),
    ]
    return np.stack(rows, axis=-2)


def _haminus4(q: np.ndarray) -> np.ndarray:
    w, x, y, z = np.moveaxis(q, -1, 0)
    rows = [
        np.stack([w, -x, -y, -z], axis=-1),
        np.stack([x, w, z, -y], axis=-1),
        np.stack([y, -z, w, x], axis=-1),
        np.stack([z, y, -x, w], axis=-1),
    ]
    return np.stack(rows, axis=-2)


C8 = np.diag([1.0, -1.0, -1.0, -1.0, 1.0, -1.0, -1.0, -1.0])


def dq_kinematic_units(x: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Dual-quaternion kinematic unit for a twist ``u`` (6,) -> (8,).

    Used for tests of the Jacobian; not required by the controller.
    """
    w, v = u[:3], u[3:]
    return np.concatenate([[0.0], w, [0.0], v])
