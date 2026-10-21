"""Serial-chain dual-quaternion kinematics (paper Eqs. 10-11).

Two conventions are supported:

* ``standard`` (distal) DH: ``A_i = Rz(theta) Tz(d) Tx(a) Rx(alpha)``,
  joint axis ``z`` in the parent frame;
* ``modified`` (proximal) DH: ``A_i = Tx(a) Rx(alpha) Rz(theta) Tz(d)``,
  joint axis ``Rx(alpha) z`` in the parent frame.

The analytic dual-quaternion Jacobian is built from
``j_k = 1/2 * Ad(x_pre, zeta_k) * x_full``, which is the derivation used in
``P1_PAPER_STUDY.md`` Eq. (11').  It is validated against central differences
in the test-suite, independently of any upstream implementation.
"""

from __future__ import annotations

import numpy as np

from .dq import dq_conj, dq_from_rt, dq_mul, dq_normalize, qmul


IDENTITY_DQ = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])


def _quat_axis(angle: np.ndarray, axis: int) -> np.ndarray:
    """Quaternion for a rotation of ``angle`` about a coordinate axis."""
    c = np.cos(0.5 * angle)
    s = np.sin(0.5 * angle)
    zero = np.zeros_like(c)
    if axis == 0:
        return np.stack([c, s, zero, zero], axis=-1)
    if axis == 1:
        return np.stack([c, zero, s, zero], axis=-1)
    return np.stack([c, zero, zero, s], axis=-1)


def dh_transform(theta, d: float, a: float, alpha: float, convention: str = "standard") -> np.ndarray:
    """One joint transform as a unit dual quaternion, batched over ``theta``."""
    theta = np.asarray(theta, dtype=float)
    if convention == "standard":
        q = qmul(_quat_axis(theta, 2), _quat_axis(np.full_like(theta, alpha), 0))
        t = np.stack([a * np.cos(theta), a * np.sin(theta), np.full_like(theta, d)], axis=-1)
    elif convention == "modified":
        q = qmul(_quat_axis(np.full_like(theta, alpha), 0), _quat_axis(theta, 2))
        t = np.stack(
            [
                np.full_like(theta, a),
                np.full_like(theta, -d * np.sin(alpha)),
                np.full_like(theta, d * np.cos(alpha)),
            ],
            axis=-1,
        )
    else:
        raise ValueError(f"unknown DH convention {convention!r}")
    return dq_from_rt(q, t)


def joint_axis(alpha: float, convention: str = "standard") -> np.ndarray:
    """Joint screw axis as a dual-quaternion kinematic unit (8,)."""
    if convention == "standard":
        axis = np.array([0.0, 0.0, 1.0])
    else:
        axis = np.array([0.0, -np.sin(alpha), np.cos(alpha)])
    return np.concatenate([[0.0], axis, [0.0, 0.0, 0.0, 0.0]])


def ad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Adjoint action ``x y x*`` for unit dual quaternions."""
    return dq_mul(dq_mul(x, y), dq_conj(x))


class SerialChain:
    """A serial chain with a fixed base and effector transform.

    Parameters
    ----------
    dh : sequence of (theta_offset, d, a, alpha)
    convention : ``"standard"`` or ``"modified"``
    base, effector : length-8 unit dual quaternions
    """

    def __init__(self, dh, convention: str = "standard", base=None, effector=None):
        self.dh = np.asarray(dh, dtype=float)
        if self.dh.ndim != 2 or self.dh.shape[1] != 4:
            raise ValueError("dh must be (n, 4): theta_offset, d, a, alpha")
        self.convention = convention
        self.n = self.dh.shape[0]
        # The published base quaternion is rounded to six decimals (norm
        # 1 - 5e-7), so normalise it exactly as the official code does.
        self.base = IDENTITY_DQ.copy() if base is None else dq_normalize(np.asarray(base, dtype=float))
        self.effector = IDENTITY_DQ.copy() if effector is None else dq_normalize(np.asarray(effector, dtype=float))
        self.axes = [joint_axis(row[3], convention) for row in self.dh]

    def transforms(self, q: np.ndarray) -> list[np.ndarray]:
        q = np.asarray(q, dtype=float)
        if q.shape[-1] != self.n:
            raise ValueError(f"q last axis must be {self.n}, got {q.shape}")
        out = []
        for i, (offset, d, a, alpha) in enumerate(self.dh):
            out.append(dh_transform(q[..., i] + offset, d, a, alpha, self.convention))
        return out

    def fk(self, q: np.ndarray) -> np.ndarray:
        """Forward kinematics as a unit dual quaternion, batched over ``q``."""
        x = self.base
        for A in self.transforms(q):
            x = dq_mul(x, A)
        return dq_mul(x, self.effector)

    def fk_frames(self, q: np.ndarray) -> list[np.ndarray]:
        """Frames after each joint (including base, excluding effector)."""
        frames = []
        x = self.base
        for A in self.transforms(q):
            x = dq_mul(x, A)
            frames.append(x)
        return frames

    def fk_with_frames(self, q: np.ndarray):
        """Forward kinematics plus the joint frames (single pass per chain)."""
        x = self.base
        frames = []
        for A in self.transforms(q):
            x = dq_mul(x, A)
            frames.append(x)
        return dq_mul(x, self.effector), frames

    def jacobian(self, q: np.ndarray) -> np.ndarray:
        """Analytic dual-quaternion Jacobian, shape ``q.shape[:-1] + (8, n)``."""
        q = np.asarray(q, dtype=float)
        As = self.transforms(q)
        x_full = self.fk(q)

        pre = self.base
        cols = []
        for i in range(self.n):
            z = ad(pre, self.axes[i])
            cols.append(0.5 * dq_mul(z, x_full))
            pre = dq_mul(pre, As[i])
        return np.stack(cols, axis=-1)


def relative_pose(x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
    """Paper Eq. (7): ``x_r = x_2^* x_1``."""
    return dq_mul(dq_conj(x2), x1)


def absolute_pose(x1: np.ndarray, x2: np.ndarray, xr: np.ndarray | None = None) -> np.ndarray:
    """Paper Eq. (8), corrected reading: ``x_a = x_2 * sqrt(x_r)``.

    ``sqrt`` is the SE(3) square root (``exp(0.5 log(.))``), so ``x_a`` is the
    group midpoint: ``x_a^{-1} x_1 = sqrt(x_r)`` and ``x_a^{-1} x_2 = sqrt(x_r)^{-1}``.
    """
    if xr is None:
        xr = relative_pose(x1, x2)
    return dq_mul(x2, dq_sqrt(xr))


def dq_sqrt(x: np.ndarray) -> np.ndarray:
    """SE(3) square root expressed as a dual quaternion.

    The rotation is halved in the *quaternion* branch, not in the principal
    rotation-matrix branch: if the input rotation angle is in (pi, 2*pi), the
    square root must have angle in (pi/2, pi) so that ``s * s == x`` exactly.
    Canonicalising the quaternion to ``w >= 0`` would instead give ``s*s = -x``;
    both are the same rigid transform, but the paper's ``vec8`` cost is sign
    sensitive.
    """
    from .dq import dq_from_rt, dq_to_rt, qexp, qlog
    from .se3 import exp_so3, se3_exp, v_inverse

    r, t = dq_to_rt(x)
    w = 2.0 * qlog(r)[..., 1:]
    v = np.einsum("...ij,...j->...i", v_inverse(w), t)
    _, ts = se3_exp(0.5 * np.concatenate([w, v], axis=-1))
    qs = qexp(0.5 * qlog(r))
    # Keep the matrix and quaternion branches consistent (same rotation).
    del exp_so3
    return dq_from_rt(qs, ts)


def _quat_to_R(q: np.ndarray) -> np.ndarray:
    from .dq import q_to_rotmat

    return q_to_rotmat(q)


def relative_jacobian(chain1: SerialChain, chain2: SerialChain, q1, q2) -> np.ndarray:
    """Analytic relative Jacobian ``J_r = [H+(x_2*) J_1, H-(x_1) C8 J_2]``."""
    from .dq import C8, haminus8, hamiplus8

    x1 = chain1.fk(q1)
    x2 = chain2.fk(q2)
    J1 = chain1.jacobian(q1)
    J2 = chain2.jacobian(q2)
    left = hamiplus8(dq_conj(x2)) @ J1
    right = haminus8(x1) @ (C8 @ J2)
    return np.concatenate([left, right], axis=-1)
