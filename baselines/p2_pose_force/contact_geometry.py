"""Explicit P2 Eq15 replacement approved by the user: spatial-free Log constraint.

T_a_b maps b into a. Twists are [linear, angular], right/body coordinates.
This pure geometry module has no controller, sensor, simulator or stored state.
It preserves free Log components, including nonzero initial values; it never
resets deformation. Eq9/10/11/12 and controllers 20/21/25 are not changed here.
"""
from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm
from scipy.spatial.transform import Rotation


MODEL_ID = "p2.spatial_free_log_constraint.v1"


class GeometryDomainError(ValueError):
    pass


def vector(value, shape):
    a = np.asarray(value, dtype=float)
    if a.shape != shape or not np.all(np.isfinite(a)):
        raise GeometryDomainError("invalid finite array shape")
    return a


def skew(x):
    a, b, c = vector(x, (3,))
    return np.array([[0, -c, b], [c, 0, -a], [-b, a, 0.]])


def validate_transform(T):
    T = vector(T, (4, 4))
    R = T[:3, :3]
    if (not np.allclose(T[3], [0, 0, 0, 1], atol=1e-10, rtol=0)
            or not np.allclose(R.T @ R, np.eye(3), atol=1e-10, rtol=0)
            or abs(np.linalg.det(R) - 1) > 1e-10):
        raise GeometryDomainError("not SE3; no automatic normalization")
    return T


def _inv4(T):
    """Inverse of an already validated SE(3) matrix (no re-validation)."""
    out = np.eye(4)
    out[:3, :3] = T[:3, :3].T
    out[:3, 3] = -out[:3, :3] @ T[:3, 3]
    return out


def _adj4(T):
    """Adjoint of an already validated SE(3) matrix (no re-validation)."""
    R = T[:3, :3]
    return np.block([[R, skew(T[:3, 3]) @ R], [np.zeros((3, 3)), R]])


def inverse(T):
    return _inv4(validate_transform(T))


def adjoint(T):
    return _adj4(validate_transform(T))


def _V(theta):
    length = np.linalg.norm(theta)
    s = skew(theta)
    if length < 1e-4:
        a = .5 - length**2 / 24 + length**4 / 720
        b = 1/6 - length**2 / 120 + length**4 / 5040
    else:
        a = (1 - np.cos(length)) / length**2
        b = (length - np.sin(length)) / length**3
    return np.eye(3) + a*s + b*s@s


def _exp6(x):
    """Exp of a finite 6-vector; the caller guarantees the input domain.

    The public se3_exp still validates both input and output; this variant is for
    internal call chains whose result is validated at the enclosing entry point.
    """
    out = np.eye(4)
    out[:3, :3] = Rotation.from_rotvec(x[3:]).as_matrix()
    out[:3, 3] = _V(x[3:]) @ x[:3]
    return out


def _log4(T):
    """Log of an already validated SE(3) matrix (no re-validation)."""
    theta = Rotation.from_matrix(T[:3, :3]).as_rotvec()
    return np.r_[np.linalg.solve(_V(theta), T[:3, 3]), theta]


def se3_exp(x):
    return validate_transform(_exp6(vector(x, (6,))))


def se3_log(T):
    return _log4(validate_transform(T))


def right_jacobian(x):
    x = vector(x, (6,))
    ad = np.block([[skew(x[3:]), skew(x[:3])],
                   [np.zeros((3, 3)), skew(x[3:])]])
    a = np.zeros((12, 12))
    a[:6, :6] = -ad
    a[:6, 6:] = np.eye(6)
    return expm(a)[:6, 6:]


def selection(mode):
    if mode == "tight":
        return np.eye(6)
    if mode == "pivot":
        return np.eye(6)[:5]
    if mode == "sliding":
        return np.eye(6)[2:]
    raise GeometryDomainError("unknown contact mode")


def _selection_and_null(H, N):
    H = np.asarray(H, dtype=float)
    if (H.ndim != 2 or H.shape[1] != 6 or not 1 <= H.shape[0] <= 6
            or not np.all(np.isfinite(H))
            or not np.allclose(H @ H.T, np.eye(H.shape[0]), atol=1e-10, rtol=0)):
        raise GeometryDomainError("H must have independent orthonormal rows")
    n = 6 - H.shape[0]
    if N is None:
        N = np.linalg.svd(H, full_matrices=True)[2][H.shape[0]:].T
    N = vector(N, (6, n))
    if (not np.allclose(H @ N, np.zeros((H.shape[0], n)), atol=1e-10, rtol=0)
            or not np.allclose(N.T @ N, np.eye(n), atol=1e-10, rtol=0)):
        raise GeometryDomainError("N must be an orthonormal null basis of H")
    return H, N


@dataclass(frozen=True)
class GeometryRate:
    D: np.ndarray
    tau: np.ndarray
    relative_body: np.ndarray
    grasp_body: np.ndarray
    tau_rate: np.ndarray
    free_basis_EE: np.ndarray
    constraint_matrix: np.ndarray
    singular_values: np.ndarray


def grasp_rate(O, E, G, V_o, U_EE, H, *, null_basis=None, rcond=1e-12):
    """Solve N^T tau_dot=0 with Ad(D) V_G in null(H) at the EE origin.

    a=Ad(G^-1)Vo-Ad(D^-1)U, Ng=Ad(D^-1)N,
    A=N^T Jr(tau)^-1 Ng, VG=-Ng solve(A,N^T Jr^-1 a).
    Only paper tight/pivot/sliding have the stated global-in-chart invertibility
    argument. Other orthonormal H values must pass their own domain checks.
    """
    O, E, G = map(validate_transform, (O, E, G))
    V_o, U_EE = vector(V_o, (6,)), vector(U_EE, (6,))
    if not np.isfinite(rcond) or not 0 < rcond < 1:
        raise GeometryDomainError("invalid rcond")
    H, N = _selection_and_null(H, null_basis)
    D = _inv4(E) @ O @ G
    tau = _log4(D)
    if np.linalg.norm(tau[3:]) >= np.pi - 1e-6:
        raise GeometryDomainError("principal Log chart boundary")
    a = _adj4(_inv4(G)) @ V_o - _adj4(_inv4(D)) @ U_EE
    J = right_jacobian(tau)
    if not N.shape[1]:
        VG, A, sigma = np.zeros(6), np.empty((0, 0)), np.empty(0)
    else:
        Ng = _adj4(_inv4(D)) @ N
        A = N.T @ np.linalg.solve(J, Ng)
        sigma = np.linalg.svd(A, compute_uv=False)
        if sigma[-1] <= rcond * sigma[0]:
            raise GeometryDomainError("free constraint matrix singular; no pseudoinverse fallback")
        alpha = -np.linalg.solve(A, N.T @ np.linalg.solve(J, a))
        VG = Ng @ alpha
    rate = np.linalg.solve(J, a + VG)
    return GeometryRate(D, tau, a, VG, rate, N, A, sigma)


def mode_switch_guard(D, old_mode, new_mode, raw_true_wrench,
                      tau_limit=1e-6, force_limit=.006, moment_limit=2e-6):
    """No reset: both new free directions and newly restored loads must be unloaded.

    raw_true_wrench is pre-switch, unselected Eq9+11 h, not commanded force.
    A failure returns evidence and leaves D/G/EE/object entirely unchanged.
    """
    tau = se3_log(D)
    h = vector(raw_true_wrench, (6,))
    old = set(np.flatnonzero(np.diag(selection(old_mode).T @ selection(old_mode))))
    new = set(np.flatnonzero(np.diag(selection(new_mode).T @ selection(new_mode))))
    restored, released = sorted(new-old), sorted(old-new)
    new_free = sorted(set(range(6))-new)
    strain_check = sorted(set(restored + released + new_free))
    strain_bad = [i for i in strain_check if abs(tau[i]) > tau_limit]
    load_bad = [i for i in sorted(set(restored+released))
                if abs(h[i]) > (force_limit if i < 3 else moment_limit)]
    return {"eligible": not strain_bad and not load_bad,
            "restored_indices": restored, "released_indices": released,
            "new_free_indices": new_free, "tau_before": tau.tolist(),
            "raw_true_wrench_before": h.tolist(),
            "strain_failures": strain_bad, "wrench_failures": load_bad,
            "failure_status": None if not strain_bad and not load_bad else "MODE_SWITCH_PRELOAD_INVALID"}
