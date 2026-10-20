"""Synchronisation allocation tau, Eq.(8), and its two limits Eq.(6)/(7).

    tau_dot_ci = tau_ci (1 - tau_ci) G(xi^O, xidot^O) / k ,   tau_ci(0) = eps
    G          = - xidot^O . (xi^O - xi^O(T*)) / (eps + ||xi^O - xi^O(T*)||^2)

k sits in the *denominator*: larger k means slower switching.  G > 0 exactly when
the object is closing on the intercept point.

ORIGINAL for Eq.(8).  `official_tau_dot` reproduces the divergent behaviour found
in Multiarm_ds::calculate_coordination_allocation() so that the deviation can be
quantified; it is DEVIATION_REFERENCE and is never used as the primary model.
"""

import numpy as np


def G_of(xi_o, xidot_o, xi_star, eps=1e-6):
    """Eq.(8) coordination function, scalar."""
    d = np.asarray(xi_o, float) - np.asarray(xi_star, float)
    v = np.asarray(xidot_o, float)
    return float(-(v @ d) / (eps + float(d @ d)))


def tau_dot(tau, G, k):
    """Eq.(8) right-hand side."""
    return tau * (1.0 - tau) * G / k


def closed_form(tau0, G, k, t):
    """Exact solution of Eq.(8) for constant G.

    tau(t) = 1 / (1 + ((1-tau0)/tau0) exp(-G t / k))

    For tau0 in {0,1} the solution is the constant tau0; the formula is singular
    there, so those cases are returned directly (they are the two unique
    equilibria of the logistic field, see T01).
    """
    tau0 = float(tau0)
    t = np.asarray(t, float)
    if tau0 <= 0.0:
        return np.zeros_like(t)
    if tau0 >= 1.0:
        return np.ones_like(t)
    return 1.0 / (1.0 + ((1.0 - tau0) / tau0) * np.exp(-G * t / k))


def rk4(tau0, Gfun, k, T, dt):
    """Integrate Eq.(8) with fixed-step RK4.  `Gfun(t)` returns G(t)."""
    n = int(round(T / dt))
    t = np.linspace(0.0, n * dt, n + 1)
    tau = np.empty(n + 1)
    tau[0] = tau0
    for i in range(n):
        ti = t[i]
        g1 = Gfun(ti)
        g2 = Gfun(ti + dt / 2)
        g3 = g2
        g4 = Gfun(ti + dt)
        k1 = tau_dot(tau[i], g1, k)
        k2 = tau_dot(tau[i] + dt / 2 * k1, g2, k)
        k3 = tau_dot(tau[i] + dt / 2 * k2, g3, k)
        k4 = tau_dot(tau[i] + dt * k3, g4, k)
        tau[i + 1] = tau[i] + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, tau


# --------------------------------------------------------------------------
# DEVIATION_REFERENCE: what Multiarm_ds actually does
# --------------------------------------------------------------------------
def official_tau_dot(tau, xi_o, xidot_o, xi_v, scale=10.0):
    """`Multiarm_ds::calculate_coordination_allocation()` as written upstream.

    Differences from Eq.(8), all measured in T01:
      (a) uses only the x component of the object velocity, not the full inner product
      (b) divides by the distance to the *current virtual object*, not to the
          intercept point plus eps
      (c) carries no minus sign (the direction of xi^O - xi^V absorbs it)
      (d) folds 1/k into the constant 10
      (e) clamps tau into [0.001, 0.99], which Eq.(8) does not have
    """
    xi_o = np.asarray(xi_o, float)
    xi_v = np.asarray(xi_v, float)
    dist = float(np.linalg.norm(xi_o - xi_v))
    if dist < 1e-12:
        dist = 1e-12
    dtau = scale * tau * (1.0 - tau) * float(xidot_o[0]) / dist
    new = tau + dtau
    return dtau, float(np.clip(new, 0.001, 0.99))
