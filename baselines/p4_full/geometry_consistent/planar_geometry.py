"""Project-owned analytic APC for the source 20R physical planar model.

This module does not import, execute, or alter the author's implementation.
It uses the source physical encoder offset 3.1416 and source state chart,
but true mathematical pi for trigonometric identities and periodic lifts.
All solver operations below are closed-form SE(2)/3R operations; there is no
numerical projection fallback. See PLANAR_GEOMETRY_SPEC.md before using it.
"""

from __future__ import annotations

from dataclasses import dataclass
import itertools
import math
import sys
from typing import Sequence


PHYSICAL_OFFSET = 3.1416
TRUE_PERIOD = math.tau
JOINT_COUNT = 20
GROUND_X = 7.0
GROUND_Y = 4.0
SOURCE_REGULAR_SIN2_MIN = 1.0e-6
# The final two source labels name cyclic triples in the opposite order.
AUTHOR_LABEL_TO_CYCLIC_START = tuple(range(18)) + (19, 18)
# These signs preserve the source's structural elbow label after separating
# its mathematical pi identities from its physical encoder offset.
AUTHOR_BRANCH_ZERO_SIGN = (1,) * 17 + (-1, 1, -1)
SOURCE_CHART = tuple(
    [(-PHYSICAL_OFFSET, PHYSICAL_OFFSET)] * 19
    + [(0.0, 2.0 * PHYSICAL_OFFSET)]
)


@dataclass(frozen=True)
class SE2:
    """Translation and an unwrapped rotation; composition never snaps angles."""

    x: float
    y: float
    angle: float

    def __matmul__(self, other: "SE2") -> "SE2":
        c = math.cos(self.angle)
        s = math.sin(self.angle)
        return SE2(
            self.x + c * other.x - s * other.y,
            self.y + s * other.x + c * other.y,
            self.angle + other.angle,
        )

    def inverse(self) -> "SE2":
        c = math.cos(self.angle)
        s = math.sin(self.angle)
        return SE2(-c * self.x - s * self.y,
                   s * self.x - c * self.y, -self.angle)

    def as_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "angle_unwrapped_rad": self.angle}


@dataclass(frozen=True)
class FactorGeometry:
    """A_i = R(sign_i*q_i + beta_i) Tx(length_i) R(gamma_i)."""

    sign: int
    length: float
    beta: float
    gamma: float


def _ground_factor_geometry() -> FactorGeometry:
    c = math.cos(PHYSICAL_OFFSET)
    s = math.sin(PHYSICAL_OFFSET)
    tx = -GROUND_X * c + GROUND_Y * s
    ty = -GROUND_X * s - GROUND_Y * c
    beta = math.atan2(ty, tx)
    return FactorGeometry(-1, math.hypot(GROUND_X, GROUND_Y),
                          beta, PHYSICAL_OFFSET - beta)


FACTOR_GEOMETRY = (FactorGeometry(1, 1.0, 0.0, 0.0),) * 19 + (
    _ground_factor_geometry(),
)


def _state(q: Sequence[float]) -> tuple[float, ...]:
    if len(q) != JOINT_COUNT:
        raise ValueError("The source physical model has exactly 20 coordinates.")
    state = tuple(float(x) for x in q)
    if not all(math.isfinite(x) for x in state):
        raise ValueError("Non-finite input state; no projection was attempted.")
    return state


def _label(label: int) -> int:
    if isinstance(label, bool) or not isinstance(label, int) or not 0 <= label < 20:
        raise ValueError("The source passive label must be an integer in [0,19].")
    return label


def passive_indices(label: int) -> tuple[int, int, int]:
    start = AUTHOR_LABEL_TO_CYCLIC_START[_label(label)]
    return (start, (start + 1) % 20, (start + 2) % 20)


def canonical_branch_sign(label: int, branch: int) -> int:
    if isinstance(branch, bool) or not isinstance(branch, int) or branch not in (0, 1):
        raise ValueError("Analytic APC branch must be 0 or 1.")
    return AUTHOR_BRANCH_ZERO_SIGN[_label(label)] * (1 if branch == 0 else -1)


def wrap_true_angle(angle: float) -> float:
    """A diagnostic physical rotation residual, never a coordinate mutation."""
    return math.atan2(math.sin(angle), math.cos(angle))


def factor(index: int, q_value: float) -> SE2:
    """Exact source physical factor, including the final rigid ground factor."""
    if not 0 <= index < 20:
        raise ValueError("Factor index must be in [0,19].")
    if index < 19:
        return SE2(math.cos(q_value), math.sin(q_value), q_value)
    angle = PHYSICAL_OFFSET - q_value
    c = math.cos(angle)
    s = math.sin(angle)
    return SE2(-GROUND_X * c + GROUND_Y * s,
               -GROUND_X * s - GROUND_Y * c, angle)


def full_chain(q: Sequence[float]) -> SE2:
    state = _state(q)
    transform = SE2(0.0, 0.0, 0.0)
    for index, value in enumerate(state):
        transform = transform @ factor(index, value)
    return transform


def closure_residual(q: Sequence[float]) -> dict:
    """Endpoint position and physical orientation are scored separately."""
    state = _state(q)
    angle = 0.0
    xs = []
    ys = []
    for value in state[:19]:
        angle += value
        xs.append(math.cos(angle))
        ys.append(math.sin(angle))
    x = math.fsum(xs) - GROUND_X
    y = math.fsum(ys) - GROUND_Y
    rotation = wrap_true_angle(angle + PHYSICAL_OFFSET - state[19])
    chain = full_chain(state)
    return {
        "position_components_source_link_length_unit": [x, y],
        "position_norm_source_link_length_unit": math.hypot(x, y),
        "orientation_error_rad": rotation,
        "orientation_error_abs_rad": abs(rotation),
        "full_loop_translation_components_source_link_length_unit": [
            chain.x, chain.y
        ],
        "full_loop_translation_norm_source_link_length_unit": math.hypot(
            chain.x, chain.y
        ),
    }


def closure_jacobian(q: Sequence[float]) -> list[list[float]]:
    """Derivative of (endpoint_x-7, endpoint_y-4, unwrapped physical angle).

    The position rows use source link-length units, the last row radians.
    This is an analytic derivative, not an independent qualification oracle.
    """
    state = _state(q)
    angles = []
    angle = 0.0
    for value in state[:19]:
        angle += value
        angles.append(angle)
    row_x = [-math.fsum(math.sin(a) for a in angles[j:]) for j in range(19)]
    row_y = [math.fsum(math.cos(a) for a in angles[j:]) for j in range(19)]
    return [row_x + [0.0], row_y + [0.0], [1.0] * 19 + [-1.0]]


def solve_three_r(
    target: SE2,
    geometries: Sequence[FactorGeometry],
    elbow_sign: int,
) -> dict:
    """Closed-form 3R solution before encoder recovery and source-chart lifts.

    Singular boundary, infinite-solution degeneracy, and unreachable targets
    remain explicit. A roundoff-sized excursion outside the cosine domain
    is reported as ambiguous and is never clipped into an accepted solution.
    """
    if len(geometries) != 3 or elbow_sign not in (-1, 1):
        raise ValueError("Expected three factors and an elbow sign of -1 or +1.")
    if not all(math.isfinite(v) for v in (target.x, target.y, target.angle)):
        raise ValueError("The requested transform is non-finite.")
    a, b, c = geometries
    if any(g.length <= 0.0 or not math.isfinite(g.length) for g in geometries):
        raise ValueError("This 3R factorization requires positive finite lengths.")
    phi = target.angle - c.gamma
    wrist_x = target.x - c.length * math.cos(phi)
    wrist_y = target.y - c.length * math.sin(phi)
    wrist_norm2 = math.fsum((wrist_x * wrist_x, wrist_y * wrist_y))
    cos_elbow = (
        wrist_norm2 - a.length * a.length - b.length * b.length
    ) / (2.0 * a.length * b.length)
    roundoff_band = 32.0 * sys.float_info.epsilon * max(1.0, abs(cos_elbow))
    metadata = {
        "target": target.as_dict(),
        "standard_3r_target_orientation_unwrapped_rad": phi,
        "lengths_source_link_length_unit": [g.length for g in geometries],
        "wrist_source_link_length_unit": [wrist_x, wrist_y],
        "cos_elbow_unmodified": cos_elbow,
        "cosine_roundoff_diagnostic_band": roundoff_band,
        "canonical_elbow_sign": elbow_sign,
        "source_regular_sin2_min": SOURCE_REGULAR_SIN2_MIN,
    }
    if abs(cos_elbow) > 1.0:
        excess = abs(cos_elbow) - 1.0
        return {
            **metadata,
            "status": ("UNREACHABLE_ROUNDOFF_AMBIGUOUS"
                       if excess <= roundoff_band else "UNREACHABLE"),
            "source_regular_eligible": False,
            "standard_angles_rad": None,
        }
    sin2 = (1.0 - cos_elbow) * (1.0 + cos_elbow)
    metadata["sin2_elbow"] = sin2
    if a.length == b.length and wrist_norm2 == 0.0 and cos_elbow == -1.0:
        return {
            **metadata,
            "status": "DEGENERATE_INFINITE",
            "source_regular_eligible": False,
            "standard_angles_rad": None,
            "family": {
                "theta1": "free",
                "theta2_rad": math.pi,
                "theta3": "phi-theta1-theta2 modulo true 2*pi",
            },
        }
    theta2 = math.atan2(elbow_sign * math.sqrt(sin2), cos_elbow)
    theta1 = math.atan2(wrist_y, wrist_x) - math.atan2(
        b.length * math.sin(theta2), a.length + b.length * math.cos(theta2)
    )
    theta3 = phi - theta1 - theta2
    regular = sin2 > 0.0
    return {
        **metadata,
        "status": "REGULAR" if regular else "SINGULAR_BOUNDARY",
        "source_regular_eligible": sin2 > SOURCE_REGULAR_SIN2_MIN,
        "standard_angles_rad": [theta1, theta2, theta3],
    }


def _periodic_representatives(value: float, lower: float, upper: float) -> list[dict]:
    """Enumerate literal chart representatives; never normalize a state."""
    k_min = math.ceil((lower - value) / TRUE_PERIOD)
    k_max = math.floor((upper - value) / TRUE_PERIOD)
    representatives = []
    for lift in range(k_min, k_max + 1):
        lifted = value + lift * TRUE_PERIOD
        if lower <= lifted <= upper:
            representatives.append({"value": lifted, "true_period_lift": lift})
    return representatives


def project_apc(q: Sequence[float], passive_label: int, branch: int) -> dict:
    """Project one source passive label/branch without changing active values.

    Every valid source-chart representative is returned. A planner must choose
    a representative through an explicit, separately audited metric policy;
    this function does not choose the closest one or alter endpoint fixtures.
    Mathematical candidates near a singularity are retained as evidence but
    are marked ineligible under the author's sin^2(elbow)>1e-6 regularity gate.
    """
    state = _state(q)
    label = _label(passive_label)
    indices = passive_indices(label)
    sign = canonical_branch_sign(label, branch)
    start = indices[0]
    complement = SE2(0.0, 0.0, 0.0)
    active_indices = tuple((start + offset) % 20 for offset in range(3, 20))
    for index in active_indices:
        complement = complement @ factor(index, state[index])
    target = complement.inverse()
    geometries = tuple(FACTOR_GEOMETRY[i] for i in indices)
    analytic = solve_three_r(target, geometries, sign)
    result = {
        "model": "source20R_physical_offset_true_period_analytic_cycle3R_v1",
        "passive_label": label,
        "cyclic_start_index": start,
        "passive_indices_ordered": list(indices),
        "active_indices_ordered": list(active_indices),
        "source_structural_branch": branch,
        "canonical_elbow_sign": sign,
        "input_state": list(state),
        "input_within_source_chart": all(
            lo <= value <= hi for value, (lo, hi) in zip(state, SOURCE_CHART)
        ),
        "analytic": analytic,
        "status": analytic["status"],
        "candidates": [],
        "regular_candidate_count": 0,
        "source_regular_eligible": analytic["source_regular_eligible"],
        "numerical_solver_calls": 0,
    }
    angles = analytic["standard_angles_rad"]
    if angles is None:
        return result
    a, b, c = geometries
    raw_encoder = (
        (angles[0] - a.beta) / a.sign,
        (angles[1] - a.gamma - b.beta) / b.sign,
        (angles[2] - b.gamma - c.beta) / c.sign,
    )
    result["passive_unlifted_encoder_rad"] = list(raw_encoder)
    representatives = tuple(
        _periodic_representatives(value, *SOURCE_CHART[index])
        for index, value in zip(indices, raw_encoder)
    )
    if any(not values for values in representatives):
        result["status"] = "NO_SOURCE_CHART_REPRESENTATIVE"
        result["source_regular_eligible"] = False
        return result
    for combination in itertools.product(*representatives):
        projected = list(state)
        for index, lifted in zip(indices, combination):
            projected[index] = lifted["value"]
        active_unchanged = all(projected[i] == state[i] for i in active_indices)
        within_chart = all(
            lo <= value <= hi for value, (lo, hi) in zip(projected, SOURCE_CHART)
        )
        result["candidates"].append({
            "q": projected,
            "true_period_lifts": [entry["true_period_lift"] for entry in combination],
            "active_coordinates_exactly_unchanged": active_unchanged,
            "within_source_chart": within_chart,
            "closure": closure_residual(projected),
            "source_regular_eligible": (
                analytic["source_regular_eligible"] and within_chart
            ),
        })
    result["regular_candidate_count"] = sum(
        candidate["source_regular_eligible"] for candidate in result["candidates"]
    )
    return result


def model_metadata() -> dict:
    return {
        "model": "source20R_physical_offset_true_period_analytic_cycle3R_v1",
        "joint_count": JOINT_COUNT,
        "source_link_length_unit": "author normalized link length L=1; not mm",
        "physical_encoder_offset_rad": PHYSICAL_OFFSET,
        "mathematical_pi": math.pi,
        "true_period_rad": TRUE_PERIOD,
        "ground_vector": [GROUND_X, GROUND_Y],
        "source_chart_rad": [list(bounds) for bounds in SOURCE_CHART],
        "author_label_to_cyclic_start": list(AUTHOR_LABEL_TO_CYCLIC_START),
        "author_branch_zero_canonical_elbow_sign": list(AUTHOR_BRANCH_ZERO_SIGN),
        "source_regular_sin2_min": SOURCE_REGULAR_SIN2_MIN,
        "factor_geometry": [
            {"sign": g.sign, "length": g.length, "beta": g.beta, "gamma": g.gamma}
            for g in FACTOR_GEOMETRY
        ],
        "mechanical_joint_limits": (
            "Not enforced here. Source qminmax=179.9/180*3.1416 is distinct "
            "from the original run chart; a frozen experiment must declare "
            "its limit/collision eligibility separately."
        ),
        "original_author_source_executed": False,
        "numerical_solver_calls": 0,
    }
