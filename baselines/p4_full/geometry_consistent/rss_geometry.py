"""Geometric singular-set construction, with no RNG or solver side effects.

R2 adaptation: the rigid geometry, literal author base/grasp transforms and
joint limits are preserved.  Only the designated elbow angle is derived from
the actual forearm offset.  A mode tag is not a validity/rank certificate.
The three-arm transform recipe is an explicit independent reconstruction;
the public VI RSS code does not determine a complete native implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import math
from typing import Any, Sequence

import numpy as np


AUTHOR_PI = 3.1416
RSS_GAMMA = 0.2
THREE_MODE_PROBABILITIES = (1.0/3.0, 1.0/3.0, 1.0/3.0)
AUTHOR_COMAU_MODE_PROBABILITIES = (0.0, 1.0, 0.0)


class SingularMode(IntEnum):
    ELBOW_AND_WRIST = 0
    WRIST = 1
    ELBOW = 2


@dataclass(frozen=True)
class ElbowGeometry:
    family: str
    upper_arm_mm: float
    forearm_x_mm: float
    forearm_z_mm: float
    shoulder_offset_mm: float
    elbow_lower_rad: float
    elbow_upper_rad: float

    @property
    def alpha_rad(self) -> float:
        return math.atan2(self.forearm_x_mm, self.forearm_z_mm)

    @property
    def effective_forearm_mm(self) -> float:
        return math.hypot(self.forearm_x_mm, self.forearm_z_mm)


ABB_IRB120 = ElbowGeometry("ABB_IRB120", 270.0, 302.0, 70.0, 0.0,
                          -110.0*AUTHOR_PI/180.0, 70.0*AUTHOR_PI/180.0)
COMAU_NJ16 = ElbowGeometry("COMAU_NJ16", 1250.0, 186.5+1250.0, 210.0, 524.5,
                          -90.0*AUTHOR_PI/180.0, 75.0*AUTHOR_PI/180.0)


def geometry_for(family: str | ElbowGeometry) -> ElbowGeometry:
    if isinstance(family, ElbowGeometry):
        return family
    if family.upper() in ("ABB", "ABB_IRB120", "IRB120"):
        return ABB_IRB120
    if family.upper() in ("COMAU", "COMAU_NJ16", "NJ16", "IV", "V", "VI"):
        return COMAU_NJ16
    raise ValueError("unsupported revolute-axis geometry")


def _mode(mode: int | SingularMode) -> SingularMode:
    if isinstance(mode, bool):
        raise ValueError("boolean is not a singular mode")
    return SingularMode(mode)


def _q(value: Sequence[float]) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (6,) or not np.isfinite(result).all():
        raise ValueError("six finite arm angles are required")
    return result


def elbow_singularities(family: str | ElbowGeometry) -> list[dict[str, Any]]:
    """Principal straight/folded representatives, without clamping or wrapping.

    Current author q3 intervals are shorter than 2pi.  All periodic copies
    inside those intervals are enumerated explicitly, including an empty fold
    set.  Source angle limits use literal 3.1416; geometry uses atan2.
    """
    g = geometry_for(family)
    result = []
    for kind, principal in (("straight", -g.alpha_rad), ("folded", math.pi-g.alpha_rad)):
        lo = math.ceil((g.elbow_lower_rad-principal)/(2.0*math.pi))
        hi = math.floor((g.elbow_upper_rad-principal)/(2.0*math.pi))
        copies = [principal+2.0*math.pi*k for k in range(lo, hi+1)]
        result.append({"kind": kind, "principal_q3_rad": principal,
                       "principal_within_author_limits": g.elbow_lower_rad <= principal <= g.elbow_upper_rad,
                       "periodic_copies_within_author_limits_rad": copies,
                       "source_limits_rad": [g.elbow_lower_rad, g.elbow_upper_rad]})
    return result


def apply_mode(raw_q: Sequence[float], family: str | ElbowGeometry,
               mode: int | SingularMode, *, elbow_kind: str = "straight") -> np.ndarray:
    """Constrain an externally drawn vector; draw nothing and solve nothing.

    All other coordinates retain their exact values.  Their full limits and
    collision/closure/rank qualification remain the caller's responsibility.
    The current straight q3=-alpha is allowed by both robot families.  An
    unavailable folded branch raises rather than silently switching branches.
    """
    result, g, mode = _q(raw_q).copy(), geometry_for(family), _mode(mode)
    if mode in (SingularMode.ELBOW_AND_WRIST, SingularMode.ELBOW):
        if elbow_kind not in ("straight", "folded"):
            raise ValueError("elbow_kind must be straight or folded")
        elbow = -g.alpha_rad if elbow_kind == "straight" else math.pi-g.alpha_rad
        if not g.elbow_lower_rad <= elbow <= g.elbow_upper_rad:
            raise ValueError("requested singular elbow is outside the unchanged author limits")
        result[2] = elbow
    if mode in (SingularMode.ELBOW_AND_WRIST, SingularMode.WRIST):
        result[4] = 0.0
    return result


def author_mode_probabilities(family: str | ElbowGeometry) -> tuple[float, float, float]:
    """Do not describe the public Comau fixed-mode source as a uniform mix."""
    return THREE_MODE_PROBABILITIES if geometry_for(family).family == "ABB_IRB120" else AUTHOR_COMAU_MODE_PROBABILITIES


def mode_from_uniform(u: float, probabilities: Sequence[float]) -> SingularMode:
    """Explicit-profile selection only; the RNG and profile are frozen outside.

    Use native rand()%3 outside this helper if reproducing that exact discrete
    RNG.  A uniform three-mode Comau profile is a disclosed R2 diagnostic or
    independent reconstruction, not the public fixed-mode author program.
    """
    p = np.asarray(probabilities, dtype=float)
    if p.shape != (3,) or not np.isfinite(p).all() or np.any(p < 0.0) or abs(float(p.sum())-1.0) > 1e-12:
        raise ValueError("three nonnegative probabilities summing to one are required")
    if not math.isfinite(u) or not 0.0 <= u < 1.0:
        raise ValueError("u must be in [0,1)")
    return SingularMode(int(np.searchsorted(np.cumsum(p), u, side="right")))


def singularity_factors(q: Sequence[float], family: str | ElbowGeometry) -> dict[str, float | str]:
    """Geometric factors, not a numerical acceptance predicate.

    The product is the 6R determinant up to the chosen row/axis sign.  The
    shoulder factor is saved even though the retained three modes do not
    explicitly construct that entire singular subset.
    """
    q, g = _q(q), geometry_for(family)
    shoulder = (g.shoulder_offset_mm+g.upper_arm_mm*math.sin(q[1])
                +g.forearm_z_mm*math.sin(q[1]+q[2])
                +g.forearm_x_mm*math.cos(q[1]+q[2]))
    elbow = g.upper_arm_mm*(g.forearm_z_mm*math.sin(q[2])+g.forearm_x_mm*math.cos(q[2]))
    wrist = math.sin(q[4])
    return {"family": g.family, "alpha_rad": g.alpha_rad,
            "shoulder_radial_factor_mm": shoulder,
            "elbow_planar_factor_mm2": elbow,
            "wrist_factor": wrist, "determinant_factor_product_mm3": shoulder*elbow*wrist}


def _transform(value: Any) -> np.ndarray:
    t = np.asarray(value, dtype=float)
    if t.shape != (4, 4) or not np.isfinite(t).all():
        raise ValueError("finite 4 by 4 transform required")
    if (np.max(np.abs(t[3]-np.array([0., 0., 0., 1.]))) > 1e-10
            or np.max(np.abs(t[:3,:3].T@t[:3,:3]-np.eye(3))) > 1e-10
            or abs(float(np.linalg.det(t[:3,:3]))-1.0) > 1e-10):
        raise ValueError("input is not SE(3); no projection or repair is applied")
    return t


def _inverse(t: np.ndarray) -> np.ndarray:
    result = np.eye(4)
    result[:3,:3] = t[:3,:3].T
    result[:3,3] = -t[:3,:3].T@t[:3,3]
    return result


def _adjoint(t: np.ndarray) -> np.ndarray:
    x,y,z = t[:3,3]
    skew = np.array([[0.,-z,y],[z,0.,-x],[-y,x,0.]])
    result = np.zeros((6,6))
    result[:3,:3] = t[:3,:3]
    result[:3,3:] = skew@t[:3,:3]
    result[3:,3:] = t[:3,:3]
    return result


def vi_target_poses(singular_ee_world: Any, designated_passive_arm: int,
                    q12_transform: Any, q13_transform: Any) -> dict[int, np.ndarray]:
    """VI-A independent recipe, no IK call and no branch selection.

    Caller supplies the original literal Q12/Q13 and world EE pose.  The
    right-facing matrix S is exactly the author's matrix, not Rz(3.1416).
    T1*=Ts S Q1s^-1; To*=T1* Q1o S.  The original singular arm pose is retained
    by identity and is never re-solved into a different wrist configuration.
    """
    if designated_passive_arm not in (2,3):
        raise ValueError("active arm is fixed to 1; designated passive must be 2 or 3")
    ts = _transform(singular_ee_world)
    grasp = {2:_transform(q12_transform),3:_transform(q13_transform)}
    facing = np.diag([-1.,-1.,1.,1.])
    t1 = ts@facing@_inverse(grasp[designated_passive_arm])
    poses = {1:t1,2:t1@grasp[2]@facing,3:t1@grasp[3]@facing}
    poses[designated_passive_arm] = ts.copy()
    return poses


def vi_residual_transforms(t1: Any, t2: Any, t3: Any,
                           q12_transform: Any, q13_transform: Any) -> tuple[np.ndarray, np.ndarray]:
    """Two separate SE(3) closure errors; never substitute one loop for both."""
    t1,t2,t3 = (_transform(t) for t in (t1,t2,t3))
    q12,q13 = _transform(q12_transform),_transform(q13_transform)
    facing = np.diag([-1.,-1.,1.,1.])
    return _inverse(t2)@t1@q12@facing, _inverse(t3)@t1@q13@facing


def vi_constraint_jacobian_at_closure(j1_body: Any, j2_body: Any, j3_body: Any,
                                      q12_transform: Any, q13_transform: Any) -> np.ndarray:
    """12 by 18 derivative at exact closure, with [v_mm,omega] body twists.

    This is not a complete off-manifold Log-residual Newton Jacobian; callers
    must not omit the Log Jacobian when using a nonzero residual in a solver.
    """
    matrices = [np.asarray(j,dtype=float) for j in (j1_body,j2_body,j3_body)]
    if any(j.shape != (6,6) or not np.isfinite(j).all() for j in matrices):
        raise ValueError("three finite 6 by 6 body Jacobians required")
    facing = np.diag([-1.,-1.,1.,1.])
    h12,h13 = _transform(q12_transform)@facing,_transform(q13_transform)@facing
    result = np.zeros((12,18))
    result[:6,:6] = _adjoint(_inverse(h12))@matrices[0]
    result[6:,:6] = _adjoint(_inverse(h13))@matrices[0]
    result[:6,6:12] = -matrices[1]
    result[6:,12:18] = -matrices[2]
    return result


def vi_rank_report(j1_body: Any, j2_body: Any, j3_body: Any,
                    q12_transform: Any, q13_transform: Any, *,
                    relative_threshold: float = 1e-6) -> dict[str, Any]:
    """Record full and passive ranks separately, not a validity certificate."""
    if not math.isfinite(relative_threshold) or not 0.0 < relative_threshold < 1.0:
        raise ValueError("positive relative rank threshold below one required")
    full = vi_constraint_jacobian_at_closure(j1_body,j2_body,j3_body,q12_transform,q13_transform)
    passive = full[:,6:]
    def rank_data(matrix: np.ndarray, linear_rows: Sequence[int]) -> dict[str, Any]:
        scaled = matrix.copy()
        scaled[list(linear_rows),:] /= 1000.0
        sigma = np.linalg.svd(scaled,compute_uv=False)
        cutoff = relative_threshold*float(sigma[0]) if sigma.size else 0.0
        return {"rank":int(np.count_nonzero(sigma>cutoff)),"singular_values":sigma.tolist(),
                "cutoff":cutoff,"position_row_scaling":"mm to m; rank-only scaling"}
    return {"active_arm":1,"passive_arms":[2,3],"relative_threshold":relative_threshold,
            "full_12_by_18":rank_data(full,(0,1,2,6,7,8)),
            "passive_12_by_12":rank_data(passive,(0,1,2,6,7,8)),
            "passive_arm_2":rank_data(np.asarray(j2_body,dtype=float),(0,1,2)),
            "passive_arm_3":rank_data(np.asarray(j3_body,dtype=float),(0,1,2)),
            "branch_identity_contract":"(active_arm=1, branch_set_arm2, branch_set_arm3, singular_arm_mask); two identities are required",
            "scope":"Jacobian ranks at closure only; no closure residual, joint limits, collision, sample generation or planning certificate"}
