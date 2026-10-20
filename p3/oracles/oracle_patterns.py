"""Independent analytical references for Eq.(16)-(22).

Deliberately does NOT import the production package: each component is written
as a scalar closed form (math.sin), so agreement is not circular.
"""
from __future__ import annotations

import math

import numpy as np


def general(t, a, b, c, d):
    """Eq.(17)-(18) written as an explicit per-component loop."""
    out = np.empty(6)
    for i in range(6):
        out[i] = a[i] * math.sin(b[i] * t + c[i]) + d[i]
    return out


def push(t, f_push):
    # Eq.(19): a = b = c = 0, d = [0 0 f_push 0 0 0]
    return np.array([0.0, 0.0, f_push, 0.0, 0.0, 0.0])


def rub(t, f_rub, v_rub):
    # Eq.(20): only the 6th component; a=b=c=0 elsewhere
    return np.array([0.0, 0.0, 0.0, 0.0, 0.0, f_rub * math.sin(v_rub * t)])


def wiggle(t, f_wiggle, v_wiggle):
    # Eq.(21): c_5 = pi/2 => my is a cosine relative to mx
    return np.array([
        0.0, 0.0, 0.0,
        f_wiggle * math.sin(v_wiggle * t),
        f_wiggle * math.sin(v_wiggle * t + math.pi / 2.0),
        0.0,
    ])


def spiral(t, alpha, beta, v_spiral):
    # Eq.(22): a_1 = a_2 = alpha sin(vt) + beta, c_2 = pi/2
    f_spiral = alpha * math.sin(v_spiral * t) + beta
    return np.array([
        f_spiral * math.sin(v_spiral * t),
        f_spiral * math.sin(v_spiral * t + math.pi / 2.0),
        0.0, 0.0, 0.0, 0.0,
    ])


ORACLES = {
    "push": lambda t, p: push(t, p["f_push"]),
    "rub": lambda t, p: rub(t, p["f_rub"], p["v_rub"]),
    "wiggle": lambda t, p: wiggle(t, p["f_wiggle"], p["v_wiggle"]),
    "spiral": lambda t, p: spiral(t, p["alpha"], p["beta"], p["v_spiral"]),
}
