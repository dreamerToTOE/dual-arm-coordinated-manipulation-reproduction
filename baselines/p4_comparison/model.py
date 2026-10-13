"""Predeclared paper-environment-I-family planar closed chain.

Independent mathematical reconstruction, not the unprovided original Figure 2a
geometry.  Twenty actuated revolute joints join nineteen moving links to a
ground link.  The terminal joint is a zero-length rotational flange.  No
author code, FR3 model, collision backend or historical acceptance is imported.

The only passive partitions used here are (0, 1, 2) and (16, 17, 18): both
contain three positive-length links and admit genuine two-branch planar IK.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, atan2, cos, pi, sin

import numpy as np
import shapely


def wrap_angle(value):
    """Return the principal revolute-joint/SE(2) angle in [-pi, pi)."""
    return (np.asarray(value) + pi) % (2.0 * pi) - pi


@dataclass(frozen=True)
class IKResult:
    success: bool
    q: np.ndarray | None
    reason: str
    cosine: float | None = None
    branch: int = 0


class PlanarModel:
    """Fixed 20R model, exact 3R inverse closure, and real GEOS geometry."""

    n = 20
    partitions = (0, 16)
    position_tolerance = 1e-8
    angle_tolerance = 1e-8
    branch_epsilon = 1e-10
    cosine_roundoff = 1e-12
    link_radius = 0.002
    environments = {
        "E0_sparse": ((0.45, 0.72, 0.045),),
        "E1_clutter": ((0.45, 0.72, 0.045), (0.50, 0.18, 0.065),
                       (0.72, 0.60, 0.05)),
    }

    def __init__(self):
        self.lengths = np.r_[np.full(19, sin(pi / 38.0)), 0.0]
        self.target_translation = np.array([1.0, 0.0])
        self.target_angle = 0.0
        self.lower = np.full(self.n, -pi)
        self.upper = np.full(self.n, pi)
        a = pi / 19.0
        self.start = np.full(self.n, -a)
        self.start[0] = pi / 2.0 - a / 2.0
        self.start[19] = pi / 2.0 - a / 2.0
        self.goal = self.start.copy()
        self.goal[16:19] = (-2.0 * a, a, -2.0 * a)
        first, second = np.triu_indices(20, 1)
        allowed = (second != first + 1) & ~((first == 0) & (second == 19))
        self._pair_first = first[allowed]
        self._pair_second = second[allowed]

    def _q(self, q):
        vector = np.asarray(q, dtype=float)
        if vector.shape != (self.n,) or not np.isfinite(vector).all():
            raise ValueError("A finite twenty-joint configuration is required")
        return vector

    def fk(self, q):
        """A + nineteen moving-link endpoints; then actual terminal angle.

        The final zero-length flange has no extra geometry vertex.  Angles are
        relative; every moving link is translated along its post-joint x axis.
        """
        vector = self._q(q)
        angles = np.cumsum(vector)
        steps = self.lengths[:, None] * np.column_stack((np.cos(angles),
                                                        np.sin(angles)))
        vertices = np.vstack((np.zeros(2), np.cumsum(steps[:19], axis=0)))
        return vertices, float(angles[-1])

    def closure(self, q):
        vertices, angle = self.fk(q)
        return np.r_[vertices[-1] - self.target_translation,
                     float(wrap_angle(angle - self.target_angle))]

    def jacobian(self, q):
        """Analytic derivative of endpoint xy and local SO(2) residual."""
        vector = self._q(q)
        angles = np.cumsum(vector)
        dx = -self.lengths * np.sin(angles)
        dy = self.lengths * np.cos(angles)
        return np.vstack((np.cumsum(dx[::-1])[::-1],
                          np.cumsum(dy[::-1])[::-1], np.ones(self.n)))

    def branch(self, q, partition_start):
        self._partition(partition_start)
        value = sin(float(self._q(q)[partition_start + 1]))
        return 0 if abs(value) <= self.branch_epsilon else (1 if value > 0 else -1)

    def _partition(self, partition_start):
        if partition_start not in self.partitions:
            raise ValueError("Only predeclared three-R partitions 0 and 16 are valid")

    def _transform(self, q, lengths):
        if len(q) == 0:
            return np.eye(3)
        angles = np.cumsum(q)
        position = np.array([np.dot(lengths, np.cos(angles)),
                             np.dot(lengths, np.sin(angles))])
        c, s = cos(float(angles[-1])), sin(float(angles[-1]))
        return np.array([[c, -s, position[0]],
                         [s, c, position[1]], [0.0, 0.0, 1.0]])

    @staticmethod
    def _inverse(transform):
        result = np.eye(3)
        result[:2, :2] = transform[:2, :2].T
        result[:2, 2] = -result[:2, :2] @ transform[:2, 2]
        return result

    def ik(self, q, partition_start, branch):
        """Close the selected 3R chain, leaving every active joint unchanged.

        T_passive = inverse(T_prefix) T_target inverse(T_suffix).  The only
        clipping is preregistered 1e-12 roundoff at the exact cosine boundary.
        This is not relaxation of geometric, closure or joint-limit tests.
        """
        self._partition(partition_start)
        try:
            vector = self._q(q)
        except ValueError:
            return IKResult(False, None, "INVALID_INPUT")
        if branch not in (-1, 0, 1):
            return IKResult(False, None, "INVALID_BRANCH")
        p = partition_start
        prefix = self._transform(vector[:p], self.lengths[:p])
        suffix = self._transform(vector[p + 3:], self.lengths[p + 3:])
        target = np.eye(3)
        target[:2, 2] = self.target_translation
        required = self._inverse(prefix) @ target @ self._inverse(suffix)
        phi = atan2(required[1, 0], required[0, 0])
        a1, a2, a3 = self.lengths[p:p + 3]
        x = float(required[0, 2] - a3 * cos(phi))
        y = float(required[1, 2] - a3 * sin(phi))
        cosine = (x*x + y*y - a1*a1 - a2*a2) / (2.0*a1*a2)
        if not np.isfinite(cosine):
            return IKResult(False, None, "NONFINITE_IK", float(cosine))
        if abs(cosine) > 1.0 + self.cosine_roundoff:
            return IKResult(False, None, "IK_UNREACHABLE", float(cosine))
        bounded = min(1.0, max(-1.0, cosine))
        middle = (1 if branch >= 0 else -1) * acos(bounded)
        if branch == 0 and abs(sin(middle)) > self.branch_epsilon:
            return IKResult(False, None, "NON_SINGULAR_BRANCH_ZERO", float(cosine))
        first = atan2(y, x) - atan2(a2*sin(middle), a1 + a2*cos(middle))
        third = phi - first - middle
        result = vector.copy()
        result[p:p + 3] = wrap_angle([first, middle, third])
        residual = self.closure(result)
        if (np.linalg.norm(residual[:2]) > self.position_tolerance or
                abs(residual[2]) > self.angle_tolerance):
            return IKResult(False, None, "IK_CLOSURE_RESIDUAL", float(cosine))
        if np.any(result < self.lower) or np.any(result > self.upper):
            return IKResult(False, None, "JOINT_LIMIT", float(cosine))
        return IKResult(True, result, "SUCCESS", float(cosine), self.branch(result, p))

    def collision(self, q, environment):
        """Real GEOS Cartesian distances with exact capsule/circle radii.

        A capsule pair collides when GEOS centerline distance <= 2r.  A circular
        obstacle collides when GEOS segment-to-center distance <= r_link+r_circle.
        Only links sharing an actual revolute joint are excluded.  Ground is
        the last segment, connecting the fixed B base to the fixed A base.
        """
        if environment not in self.environments:
            raise ValueError("Unknown preregistered environment")
        vertices, _ = self.fk(q)
        starts = np.vstack((vertices[:-1], self.target_translation))
        ends = np.vstack((vertices[1:], vertices[0]))
        segments = shapely.linestrings(np.stack((starts, ends), axis=1))
        distance = np.asarray(shapely.distance(segments[self._pair_first],
                                               segments[self._pair_second]))
        clearance = distance - 2.0*self.link_radius
        minimum_index = int(np.argmin(clearance))
        minimum = float(clearance[minimum_index])
        names = [f"moving_link_{index + 1:02d}" for index in range(19)] + ["ground_link"]
        pair = [names[self._pair_first[minimum_index]], names[self._pair_second[minimum_index]]]
        queries = len(clearance)
        for index, (x, y, radius) in enumerate(self.environments[environment]):
            obstacle = shapely.points(x, y)
            values = np.asarray(shapely.distance(segments, obstacle)) - radius - self.link_radius
            candidate_index = int(np.argmin(values))
            candidate = float(values[candidate_index])
            queries += len(values)
            if candidate < minimum:
                minimum = candidate
                pair = [names[candidate_index], f"{environment}_circle_{index + 1:02d}"]
        return {"collision": minimum <= 0.0, "pair": pair,
                "minimum_clearance": minimum, "geometry_queries": queries,
                "source": "Shapely/GEOS Cartesian distance; analytical capsule/circle radii"}

    def valid(self, q, environment):
        try:
            vector = self._q(q)
        except ValueError:
            return {"valid": False, "reason": "INVALID_INPUT", "collision": None,
                    "closure_position": None, "closure_angle": None, "joint_margin": None}
        residual = self.closure(vector)
        position, angle = float(np.linalg.norm(residual[:2])), float(abs(residual[2]))
        margin = float(np.min(np.minimum(vector - self.lower, self.upper - vector)))
        result = {"valid": False, "reason": None, "closure_position": position,
                  "closure_angle": angle, "joint_margin": margin, "collision": None}
        if margin < 0.0:
            result["reason"] = "JOINT_LIMIT"
        elif position > self.position_tolerance or angle > self.angle_tolerance:
            result["reason"] = "CLOSURE_RESIDUAL"
        else:
            result["collision"] = self.collision(vector, environment)
            result["reason"] = "COLLISION" if result["collision"]["collision"] else "SUCCESS"
            result["valid"] = result["reason"] == "SUCCESS"
        return result

    def singular_fixture(self):
        """Predeclared deterministic algebra fixture; not a planner shortcut."""
        q = (self.start + self.goal) / 2.0
        q[17] = 0.0
        return self.ik(q, 0, self.branch(self.start, 0))
