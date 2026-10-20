"""P3 hybrid force-position arm control — paper Eq.(27)-(28).

[ORIGINAL] Eq.(27):
    tau = J^T [[Omega, 0], [0, I]] K_p dx + J^T [[R_h, 0], [0, R_h]] w
          - D qdot + tau_g + tau_f
[ORIGINAL] Eq.(28):
    Omega = R_h Sigma R_h^T,  Sigma = diag([0, 1, 1]) in R^{3x3}

Frames and dimensions (audited, see p3/reviews/P3_T00_SOURCE_AUDIT.md):
    J   : 6 x n, task-space Jacobian of the arm, wrenches to joint torques
    K_p : 6 x 6 (translation N/m, rotation N*m/rad)
    dx  : 6, position error [m, rad]
    w   : 6, perturbation wrench [N, N*m] in the hole frame
    R_h : 3 x 3 rotation of the hole frame w.r.t. the global reference
    D   : n x n damping (N*m*s/rad), qdot: n
There is **no measured external force feedback** in this law; the paper states
explicitly "there is no force feedback term" (p.8571). The function signature
therefore has no force-input argument, and T04 includes a mutation test that
would detect silently added feedback.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

SIGMA = np.diag([0.0, 1.0, 1.0])  # Eq.(28): position selection in the hole frame


class ControlDomainError(ValueError):
    """Raised for invalid dimensions, frames or non-finite inputs."""


def _as(value, shape, name) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if arr.shape != shape:
        raise ControlDomainError(f"{name} must have shape {shape}, got {arr.shape}")
    if not np.isfinite(arr).all():
        raise ControlDomainError(f"{name} must be finite")
    return arr


def _rotation(R, name="R_h") -> np.ndarray:
    R = np.asarray(R, dtype=float)
    if R.shape != (3, 3):
        raise ControlDomainError(f"{name} must be 3x3, got {R.shape}")
    if not np.isfinite(R).all():
        raise ControlDomainError(f"{name} must be finite")
    if not np.allclose(R.T @ R, np.eye(3), atol=1e-9):
        raise ControlDomainError(f"{name} is not orthonormal")
    if np.linalg.det(R) < 0:
        raise ControlDomainError(f"{name} must be a proper rotation (det > 0)")
    return R


def omega(R_h) -> np.ndarray:
    """Eq.(28): Omega = R_h diag([0,1,1]) R_h^T  in R^{3x3}."""
    R = _rotation(R_h)
    return R @ SIGMA @ R.T


def position_selector(R_h) -> np.ndarray:
    """6x6 block [[Omega, 0], [0, I3]] of Eq.(27) (3x3 zero block)."""
    Om = omega(R_h)
    block = np.zeros((6, 6))
    block[:3, :3] = Om
    block[3:, 3:] = np.eye(3)
    return block


def wrench_rotation(R_h) -> np.ndarray:
    """6x6 block [[R_h, 0], [0, R_h]] of Eq.(27) — a pure rotation of a wrench."""
    R = _rotation(R_h)
    block = np.zeros((6, 6))
    block[:3, :3] = R
    block[3:, 3:] = R
    return block


def rotate_wrench(R, w) -> np.ndarray:
    """Rotate a 6-vector wrench by a rotation matrix (no translation part)."""
    return wrench_rotation(R) @ _as(w, (6,), "w")


def torque_terms(J, R_h, Kp, dx, w, D, qdot, tau_g, tau_f,
                 R_task_to_hole: Optional[np.ndarray] = None) -> dict:
    """All terms of Eq.(27) separately, for auditing and plotting.

    `R_task_to_hole` is an explicit [ADAPTATION: frame naming] relabelling used
    only when the perturbation wrench is generated in the task frame (push +z)
    while the hole frame uses +x as the insertion axis. Default None = literal
    application of Eq.(27) (w taken as already expressed in the hole frame).
    """
    J = np.asarray(J, dtype=float)
    if J.ndim != 2 or J.shape[0] != 6:
        raise ControlDomainError(f"J must be 6 x n, got {J.shape}")
    if not np.isfinite(J).all():
        raise ControlDomainError("J must be finite")
    n = J.shape[1]
    Kp = _as(Kp, (6, 6), "Kp")
    dx = _as(dx, (6,), "dx")
    w = _as(w, (6,), "w")
    D = _as(D, (n, n), "D")
    qdot = _as(qdot, (n,), "qdot")
    tau_g = _as(tau_g, (n,), "tau_g")
    tau_f = _as(tau_f, (n,), "tau_f")
    R_h = _rotation(R_h)

    if R_task_to_hole is not None:
        w = rotate_wrench(_rotation(R_task_to_hole, "R_task_to_hole"), w)

    F_pos = position_selector(R_h) @ Kp @ dx     # Eq.(27) first term wrench
    F_pert = wrench_rotation(R_h) @ w            # Eq.(27) second term wrench
    tau_pos = J.T @ F_pos
    tau_pert = J.T @ F_pert
    tau_damp = -D @ qdot
    tau = tau_pos + tau_pert + tau_damp + tau_g + tau_f
    return {
        "F_pos": F_pos,
        "F_pert": F_pert,
        "F_total": F_pos + F_pert,
        "tau_pos": tau_pos,
        "tau_pert": tau_pert,
        "tau_damp": tau_damp,
        "tau_gravity": tau_g.copy(),
        "tau_friction": tau_f.copy(),
        "tau": tau,
    }


def arm_torque(J, R_h, Kp, dx, w, D, qdot, tau_g, tau_f,
               R_task_to_hole: Optional[np.ndarray] = None) -> np.ndarray:
    """Eq.(27) joint torque vector (N*m)."""
    return torque_terms(J, R_h, Kp, dx, w, D, qdot, tau_g, tau_f,
                        R_task_to_hole=R_task_to_hole)["tau"]
