"""G1 acceptance tests: dual-quaternion kinematics, poses, Jacobians, null space.

Every test is an independent check: the oracle is either an SE(3) matrix
implementation, a central finite difference, or an SVD null-space basis.
Nothing here imports dqrobotics, the official kernel, or a GPU library.
"""

from __future__ import annotations

import numpy as np
import pytest

from p1_repro.dq import (
    C8,
    dq_conj,
    dq_from_rt,
    dq_mul,
    dq_normalize,
    dq_to_rt,
    haminus8,
    hamiplus8,
    q_from_rotmat,
    q_to_rotmat,
    qmul,
)
from p1_repro.kinematics import SerialChain, absolute_pose, dq_sqrt, relative_jacobian, relative_pose
from p1_repro.nullspace import damped_pinv, null_projector, project_velocity
from p1_repro.se3 import exp_so3, se3_inv, se3_log, se3_mul

# UR3 standard-DH parameters from the official example YAML.
UR3_DH = np.array(
    [
        [0.0, 0.1519, 0.0, 1.5708],
        [0.0, 0.0, -0.24365, 0.0],
        [0.0, 0.0, -0.21325, 0.0],
        [0.0, 0.11235, 0.0, 1.5708],
        [0.0, 0.08535, 0.0, -1.5708],
        [0.0, 0.0819, 0.0, 0.0],
    ]
)
BASE1 = np.array([0.612384, 0.353533, -0.353533, 0.612384, -0.087881, 0.013986, 0.013986, 0.087881])
BASE2 = np.array([-0.612384, 0.353533, -0.353533, -0.612384, 0.087864, 0.013983, 0.013983, -0.087864])


def _dh_matrix(theta, d, a, alpha):
    """Independent homogeneous DH transform (matrix path)."""
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    R = np.array([[ct, -st * ca, st * sa], [st, ct * ca, -ct * sa], [0.0, sa, ca]])
    t = np.array([a * ct, a * st, d])
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


def _matrix_fk(dh, q):
    T = np.eye(4)
    for i, (off, d, a, alpha) in enumerate(dh):
        T = T @ _dh_matrix(q[i] + off, d, a, alpha)
    return T[:3, :3], T[:3, 3]


def _chains():
    c1 = SerialChain(UR3_DH, base=BASE1)
    c2 = SerialChain(UR3_DH, base=BASE2)
    return c1, c2


rng = np.random.default_rng(20261021)


# ---------------------------------------------------------------------------
# A1 - algebra and forward kinematics
# ---------------------------------------------------------------------------
def test_dq_roundtrip_and_unit_constraint():
    n = 200
    q = rng.normal(size=(n, 4))
    q /= np.linalg.norm(q, axis=-1, keepdims=True)
    t = rng.normal(size=(n, 3))
    x = dq_from_rt(q, t)
    r, tt = dq_to_rt(x)
    assert np.allclose(tt, t, atol=1e-14)
    assert np.abs(q_to_rotmat(r) - q_to_rotmat(q)).max() < 1e-14
    # unit residual: r'r = 1 and r'd = 0
    assert np.abs(np.sum(r * r, axis=-1) - 1.0).max() < 1e-14
    assert np.abs(np.sum(r * x[..., 4:], axis=-1)).max() < 1e-14


def test_dq_composition_matches_se3():
    n = 300
    qa = rng.normal(size=(n, 4))
    qa /= np.linalg.norm(qa, axis=-1, keepdims=True)
    qb = rng.normal(size=(n, 4))
    qb /= np.linalg.norm(qb, axis=-1, keepdims=True)
    ta, tb = rng.normal(size=(n, 3)), rng.normal(size=(n, 3))
    xa, xb = dq_from_rt(qa, ta), dq_from_rt(qb, tb)
    xab = dq_mul(xa, xb)
    r, t = dq_to_rt(xab)
    R, t_mat = se3_mul((q_to_rotmat(qa), ta), (q_to_rotmat(qb), tb))
    assert np.abs(q_to_rotmat(r) - R).max() < 1e-14
    assert np.abs(t - t_mat).max() < 1e-14


def test_hamilton_operators():
    n = 100
    a = rng.normal(size=(n, 8))
    b = rng.normal(size=(n, 8))
    assert np.abs(np.einsum("...ij,...j->...i", hamiplus8(a), b) - dq_mul(a, b)).max() < 1e-14
    assert np.abs(np.einsum("...ij,...j->...i", haminus8(b), a) - dq_mul(a, b)).max() < 1e-14
    # d(x*) = C8 xdot
    eps = 1e-7
    x = dq_mul(a, dq_conj(b))
    # The conjugate is linear, so the finite difference is exact up to round-off.
    dconj = (dq_conj(x + eps * b) - dq_conj(x)) / eps
    assert np.abs(dconj - np.einsum("ij,...j->...i", C8, b)).max() < 1e-5


def test_fk_matches_independent_matrix_chain():
    # Identity base/effector so the matrix chain is directly comparable.
    c1 = SerialChain(UR3_DH)
    n = 200
    q = rng.uniform(-np.pi, np.pi, size=(n, 6))
    x = c1.fk(q)
    r, t = dq_to_rt(x)
    for k in range(n):
        R, tm = _matrix_fk(UR3_DH, q[k])
        assert np.abs(q_to_rotmat(r[k]) - R).max() < 1e-12
        assert np.abs(t[k] - tm).max() < 1e-12


# ---------------------------------------------------------------------------
# A2 - relative and absolute pose
# ---------------------------------------------------------------------------
def test_relative_pose_matches_se3():
    c1, c2 = _chains()
    q1 = rng.uniform(-2, 2, size=(50, 6))
    q2 = rng.uniform(-2, 2, size=(50, 6))
    xr = relative_pose(c1.fk(q1), c2.fk(q2))
    r, t = dq_to_rt(xr)
    for k in range(50):
        Ra, ta = dq_to_rt(c1.fk(q1[k : k + 1]))
        Rb, tb = dq_to_rt(c2.fk(q2[k : k + 1]))
        R, tt = se3_mul(se3_inv((q_to_rotmat(Rb[0]), tb[0])), (q_to_rotmat(Ra[0]), ta[0]))
        assert np.abs(q_to_rotmat(r[k]) - R).max() < 1e-12
        assert np.abs(t[k] - tt).max() < 1e-12


def test_absolute_pose_is_group_midpoint_and_base_invariant():
    c1, c2 = _chains()
    q1 = rng.uniform(-2, 2, size=(20, 6))
    q2 = rng.uniform(-2, 2, size=(20, 6))
    x1, x2 = c1.fk(q1), c2.fk(q2)
    xr = relative_pose(x1, x2)
    s = dq_sqrt(xr)
    xa = absolute_pose(x1, x2, xr)
    assert np.abs(dq_mul(s, s) - xr).max() < 1e-12
    assert np.abs(dq_mul(dq_conj(xa), x1) - s).max() < 1e-12
    assert np.abs(dq_mul(dq_conj(xa), x2) - dq_conj(s)).max() < 1e-12
    xa_swap = dq_mul(x1, dq_conj(s))
    assert np.abs(xa - xa_swap).max() < 1e-12


def test_absolute_pose_counterexample_to_euclidean_average():
    # Fixed case used in P1_PAPER_STUDY.md 3.3(b).
    def Rz(a):
        return np.array([[np.cos(a), -np.sin(a), 0.0], [np.sin(a), np.cos(a), 0.0], [0.0, 0.0, 1.0]])

    t1 = np.array([0.5, 0.2, 0.1])
    t2 = np.array([-0.1, 0.3, 0.2])
    x1 = dq_from_rt(q_from_rotmat(Rz(0.9)), t1)
    x2 = dq_from_rt(q_from_rotmat(Rz(-0.4)), t2)
    _, ta = dq_to_rt(absolute_pose(x1[None], x2[None]))
    assert np.allclose(ta[0], [0.183153, 0.148916, 0.15], atol=2e-6)
    assert abs(np.linalg.norm(ta[0] - 0.5 * (t1 + t2)) - 0.1024787) < 1e-5


# ---------------------------------------------------------------------------
# A3 - relative Jacobian
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("eps_h", [1e-5, 1e-6])
def test_relative_jacobian_matches_central_difference(eps_h):
    c1, c2 = _chains()
    q1 = rng.uniform(-2, 2, size=(5, 6))
    q2 = rng.uniform(-2, 2, size=(5, 6))
    J = relative_jacobian(c1, c2, q1, q2)
    worst = 0.0
    for k in range(5):
        for j in range(12):
            q1p, q1m, q2p, q2m = q1[k : k + 1].copy(), q1[k : k + 1].copy(), q2[k : k + 1].copy(), q2[k : k + 1].copy()
            if j < 6:
                q1p[0, j] += eps_h
                q1m[0, j] -= eps_h
            else:
                q2p[0, j - 6] += eps_h
                q2m[0, j - 6] -= eps_h
            fd = (relative_pose(c1.fk(q1p), c2.fk(q2p)) - relative_pose(c1.fk(q1m), c2.fk(q2m))) / (2 * eps_h)
            worst = max(worst, np.abs(fd[0] - J[k, :, j]).max())
    assert worst < 1e-6, f"max |FD - J| = {worst:.3e}"


def test_negative_control_wrong_conjugation_fails_fd():
    # x_r = x_1^* x_2 instead of x_2^* x_1 must not match the same FD.
    c1, c2 = _chains()
    q1 = rng.uniform(-2, 2, size=(1, 6))
    q2 = rng.uniform(-2, 2, size=(1, 6))
    J_wrong = relative_jacobian(c2, c1, q2, q1)
    h = 1e-6
    q1p, q1m = q1.copy(), q1.copy()
    q1p[0, 0] += h
    q1m[0, 0] -= h
    fd = (relative_pose(c1.fk(q1p), c2.fk(q2)) - relative_pose(c1.fk(q1m), c2.fk(q2))) / (2 * h)
    assert np.abs(fd[0] - J_wrong[0, :, 0]).max() > 1e-3


def test_jacobian_rank_is_six():
    c1, c2 = _chains()
    q1 = rng.uniform(-2, 2, size=(20, 6))
    q2 = rng.uniform(-2, 2, size=(20, 6))
    J = relative_jacobian(c1, c2, q1, q2)
    for k in range(20):
        s = np.linalg.svd(J[k], compute_uv=False)
        assert s[6] / s[0] < 1e-12
        assert s[5] / s[0] > 1e-3


# ---------------------------------------------------------------------------
# B1 - null-space projector
# ---------------------------------------------------------------------------
def test_null_projector_properties():
    c1, c2 = _chains()
    q1 = rng.uniform(-2, 2, size=(10, 6))
    q2 = rng.uniform(-2, 2, size=(10, 6))
    J = relative_jacobian(c1, c2, q1, q2)
    N = null_projector(J)
    assert np.abs(N @ N - N).max() < 1e-12
    assert np.abs(N - np.swapaxes(N, -1, -2)).max() < 1e-12
    assert np.abs(J @ N).max() < 1e-10
    for k in range(10):
        assert np.linalg.matrix_rank(N[k], tol=1e-8) == 6


def test_projection_kills_relative_velocity():
    c1, c2 = _chains()
    q1 = rng.uniform(-2, 2, size=(10, 6))
    q2 = rng.uniform(-2, 2, size=(10, 6))
    J = relative_jacobian(c1, c2, q1, q2)
    u = rng.normal(size=(10, 12))
    up = project_velocity(J, u)
    before = np.linalg.norm(np.einsum("kij,kj->ki", J, u), axis=-1)
    after = np.linalg.norm(np.einsum("kij,kj->ki", J, up), axis=-1)
    assert np.all(after < 1e-12 * np.maximum(before, 1e-12) + 1e-14)


def test_rank_degenerate_projector_vanishes():
    # A 6-DOF arm asked to hold a full 6-DoF task has no self-motion left.
    chain = SerialChain(UR3_DH, base=BASE1)
    q = rng.uniform(-2, 2, size=(5, 6))
    J = chain.jacobian(q)
    N = null_projector(J)
    assert np.abs(N).max() < 1e-8
    # A synthetic full-rank 12-row constraint also collapses the projector.
    J_full = np.eye(12)[None]
    assert np.abs(null_projector(J_full)).max() < 1e-10


def test_official_style_damping_is_ill_conditioned():
    """Characterises the 1e-16 damping used by the released kernel.

    With an 8-row rank-6 Jacobian, ``J J^T + 1e-16 I`` has condition ~1e16 and
    the float64 inverse destroys the projector; this is recorded, not hidden.
    """
    c1, c2 = _chains()
    q1 = rng.uniform(-2, 2, size=(1, 6))
    q2 = rng.uniform(-2, 2, size=(1, 6))
    J = relative_jacobian(c1, c2, q1, q2)[0]
    N_bad = np.eye(12) - damped_pinv(J, 1e-16) @ J
    assert np.abs(N_bad @ N_bad - N_bad).max() > 1e-2
    N_good = null_projector(J[None])[0]
    assert np.abs(N_good @ N_good - N_good).max() < 1e-12


# ---------------------------------------------------------------------------
# B2 - finite-step residual order
# ---------------------------------------------------------------------------
def _drift(Th, steps=15, projected=True):
    c1, c2 = _chains()
    q1 = np.array([[0.0, -1.0, 0.5, -1.5, 0.3, 0.2]])
    q2 = np.array([[0.2, -0.9, 0.4, -1.4, 0.25, 0.15]])
    # Fixed direction: varying it per Th would contaminate the scaling fit.
    u = np.array([0.11, -0.23, 0.17, 0.05, -0.09, 0.13, -0.07, 0.19, -0.15, 0.03, 0.21, -0.12])
    u = u / np.linalg.norm(u) * 0.3
    x0 = relative_pose(c1.fk(q1), c2.fk(q2))
    for _ in range(steps):
        J = relative_jacobian(c1, c2, q1, q2)
        uu = project_velocity(J, u[None])[0] if projected else u
        q1 = q1 + Th * uu[None, :6]
        q2 = q2 + Th * uu[None, 6:]
    return float(np.linalg.norm(relative_pose(c1.fk(q1), c2.fk(q2)) - x0))


def test_projected_residual_is_second_order():
    ths = np.array([0.00125, 0.0025, 0.005, 0.01])
    d = np.array([_drift(t) for t in ths])
    slope = np.polyfit(np.log(ths), np.log(d), 1)[0]
    assert abs(slope - 2.0) < 0.1, f"slope={slope:.3f}"


def test_unprojected_drift_is_first_order():
    ths = np.array([0.00125, 0.0025, 0.005, 0.01])
    d = np.array([_drift(t, projected=False) for t in ths])
    slope = np.polyfit(np.log(ths), np.log(d), 1)[0]
    assert abs(slope - 1.0) < 0.1, f"slope={slope:.3f}"


def test_projection_reduces_drift_by_three_orders():
    dp = _drift(0.005)
    du = _drift(0.005, projected=False)
    assert du / dp > 1e3, f"ratio={du / dp:.1f}"
