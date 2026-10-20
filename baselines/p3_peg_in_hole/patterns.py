"""P3 arm-level perturbation patterns — paper Eq.(16)-(22).

[ORIGINAL] Equations transcribed from the paper page images (p.8570). The
paper gives no numeric parameter values; every numeric value used in
validation is therefore a TEST_FIXTURE supplied by the caller.

Wrench component order (Eq.16):
    w[0:3] = translation force in x, y, z        [N]
    w[3:6] = moment about x, y, z                [N*m]
Patterns live in the paper's task frame, in which the pushing / approach
direction is +z (Eq.19, Fig.5a).

Eq.(18): w = diag(a) . vsin(t*b + c) + d
Eq.(22) makes a time-varying for the spiral (a_1 = a_2 = f_spiral(t)), hence
`amplitude(t)` is a method rather than a constant vector.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np

WRENCH_ORDER: Tuple[str, ...] = ("fx", "fy", "fz", "mx", "my", "mz")
COMPONENT_UNITS: Tuple[str, ...] = ("N", "N", "N", "N*m", "N*m", "N*m")


class PatternDomainError(ValueError):
    """Raised when a perturbation pattern receives invalid input."""


def _vec6(value, name: str) -> np.ndarray:
    arr = np.asarray(value, dtype=float)
    if arr.shape != (6,):
        raise PatternDomainError(f"{name} must have shape (6,), got {arr.shape}")
    if not np.isfinite(arr).all():
        raise PatternDomainError(f"{name} must be finite")
    return arr.copy()


def _time(t) -> float:
    value = float(t)
    if not np.isfinite(value):
        raise PatternDomainError("time must be finite")
    return value


class GeneralPattern:
    """Eq.(17)-(18): w_i = a_i sin(b_i t + c_i) + d_i, i = 1..6."""

    name = "general"

    def __init__(self, a, b, c, d):
        self.a = _vec6(a, "a")   # amplitude: N (translation) / N*m (moment)
        self.b = _vec6(b, "b")   # angular frequency: rad/s
        self.c = _vec6(c, "c")   # phase: rad
        self.d = _vec6(d, "d")   # bias: N / N*m

    def amplitude(self, t: float) -> np.ndarray:
        """a(t). Constant for Eq.(17)-(21); time varying only for Eq.(22)."""
        return self.a

    def wrench(self, t) -> np.ndarray:
        """w(t) = diag(a(t)) sin(t b + c) + d   [N, N*m]."""
        tau = _time(t)
        return self.amplitude(tau) * np.sin(tau * self.b + self.c) + self.d


class Push(GeneralPattern):
    """Eq.(19): a = b = c = 0, d = [0 0 f_push 0 0 0]^T — push along +z."""

    name = "push"

    def __init__(self, f_push: float):
        self.f_push = float(f_push)
        if not np.isfinite(self.f_push):
            raise PatternDomainError("f_push must be finite")
        zero = np.zeros(6)
        super().__init__(zero, zero, zero, [0.0, 0.0, self.f_push, 0.0, 0.0, 0.0])


class Rub(GeneralPattern):
    """Eq.(20): moment about z. a_6 = f_rub [N*m], b_6 = v_rub [rad/s]."""

    name = "rub"

    def __init__(self, f_rub: float, v_rub: float):
        self.f_rub, self.v_rub = float(f_rub), float(v_rub)
        if not (np.isfinite(self.f_rub) and np.isfinite(self.v_rub)):
            raise PatternDomainError("f_rub and v_rub must be finite")
        a = np.zeros(6); a[5] = self.f_rub
        b = np.zeros(6); b[5] = self.v_rub
        super().__init__(a, b, np.zeros(6), np.zeros(6))


class Wiggle(GeneralPattern):
    """Eq.(21): moments about x and y.

    a = [0 0 0 f f 0]^T, b = [0 0 0 v v 0]^T, c = [0 0 0 0 pi/2 0]^T, d = 0.
    Hence w4 = f sin(vt), w5 = f cos(vt): an exact quadrature pair.
    """

    name = "wiggle"

    def __init__(self, f_wiggle: float, v_wiggle: float):
        self.f_wiggle, self.v_wiggle = float(f_wiggle), float(v_wiggle)
        if not (np.isfinite(self.f_wiggle) and np.isfinite(self.v_wiggle)):
            raise PatternDomainError("f_wiggle and v_wiggle must be finite")
        a = np.zeros(6); a[3] = self.f_wiggle; a[4] = self.f_wiggle
        b = np.zeros(6); b[3] = self.v_wiggle; b[4] = self.v_wiggle
        c = np.zeros(6); c[4] = np.pi / 2.0
        super().__init__(a, b, c, np.zeros(6))


class Spiral(GeneralPattern):
    """Eq.(22): x-y spiral with f_spiral(t) = alpha sin(v t) + beta.

    a(t) = [f_spiral(t), f_spiral(t), 0, 0, 0, 0]^T
    b    = [v, v, 0, 0, 0, 0]^T, c = [0, pi/2, 0, 0, 0, 0]^T, d = 0
    => w1 = f_spiral(t) sin(vt), w2 = f_spiral(t) cos(vt).

    beta < 0 is accepted: the paper states no positive-domain restriction on
    beta, so rejecting it would invent a constraint. The sign simply reverses
    the instantaneous spiral direction.
    """

    name = "spiral"

    def __init__(self, alpha: float, beta: float, v_spiral: float):
        self.alpha, self.beta, self.v_spiral = float(alpha), float(beta), float(v_spiral)
        if not (np.isfinite(self.alpha) and np.isfinite(self.beta)
                and np.isfinite(self.v_spiral)):
            raise PatternDomainError("alpha, beta and v_spiral must be finite")
        b = np.zeros(6); b[0] = self.v_spiral; b[1] = self.v_spiral
        c = np.zeros(6); c[1] = np.pi / 2.0
        super().__init__(np.zeros(6), b, c, np.zeros(6))

    def amplitude(self, t: float) -> np.ndarray:
        f_spiral = self.alpha * np.sin(self.v_spiral * t) + self.beta
        a = np.zeros(6)
        a[0] = f_spiral
        a[1] = f_spiral
        return a


_PATTERN_BUILDERS = {
    "push": lambda **kw: Push(**kw),
    "rub": lambda **kw: Rub(**kw),
    "wiggle": lambda **kw: Wiggle(**kw),
    "spiral": lambda **kw: Spiral(**kw),
}


def pattern_from_spec(spec: dict) -> GeneralPattern:
    """Build a pattern from a plain dict (used by fixtures / runners)."""
    kind = str(spec.get("kind", "")).lower()
    builder = _PATTERN_BUILDERS.get(kind)
    if builder is None:
        raise PatternDomainError(f"unknown pattern kind: {spec.get('kind')!r}")
    return builder(**{k: v for k, v in spec.items() if k != "kind"})
