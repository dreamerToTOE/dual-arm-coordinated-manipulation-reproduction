#!/usr/bin/env python3
"""Versioned stable propagation for the P2 estimator (mode B).

This is OUR numerical adaptation, not the authors' implementation. Mode A
(`PAPER_LITERAL_EULER`) stays untouched in estimator.py and is used as the
baseline elsewhere.

Mode B (`ADAPTED_STABLE_PROPAGATION_V1`):
    delta = h * phi1(hA) f          (exact for the linear part, L-stable)
    X+    = X boxplus delta
    Phi   = exp(hA)
    Qd    = Van Loan integral, i.e. Qd = S Phi^T
            with exp([[hA, hG],[0, -hA^T]]) = [[Phi, S],[0, Phi^-T]]

No clipping, no noise rescaling, no stiffness change, no gate bypass.
"""
import numpy as np
from scipy.linalg import expm
from baselines.p2_pose_force.estimator import (
    RightIESEKF as _BaseFilter,
    continuous_linearization as _cont_lin,
    _checked_covariance as _check_cov,
    PredictionReport as _PredReport)
MODE_A = "PAPER_LITERAL_EULER"
MODE_B = "ADAPTED_STABLE_PROPAGATION_V1"


def phi1_action(A, f, h):
    """Return (exp(hA), h*phi1(hA) f) with one augmented exponential."""
    n = A.shape[0]
    M = np.zeros((n + 1, n + 1))
    M[:n, :n] = h * A
    M[:n, n] = h * f
    E = expm(M)
    return E[:n, :n], E[:n, n]


def van_loan(A, G, h):
    """Exact discrete process noise for dx = A x dt + w, E[ww^T] = G dt."""
    n = A.shape[0]
    M = np.zeros((2 * n, 2 * n))
    M[:n, :n] = h * A
    M[:n, n:] = h * G
    M[n:, n:] = -h * A.T
    E = expm(M)
    Phi = E[:n, :n]
    S = E[:n, n:]
    Qd = S @ Phi.T
    return Phi, S, Qd


def propagate(state, f, A, h, qc_diag, max_exponent=0.5):
    """Mode B one-step propagation; returns predicted state, Phi and Qd.

    Qd uses the scaling-and-squaring Van Loan, which keeps symmetry/PSD to
    round-off for the stiff fixtures (single-shot Van Loan fails at C, 4 ms).
    """
    Phi, delta = phi1_action(A, f, h)
    G = np.diag(np.asarray(qc_diag, float))
    _, Qd = van_loan_stable(A, G, h, max_exponent=max_exponent)
    predicted = state.retract(delta)
    return predicted, Phi, Qd, delta


def qd_integral_reference(A, G, h, intervals=80):
    """Independent Simpson quadrature of the Van Loan integral (qualification)."""
    n = A.shape[0]
    if intervals % 2:
        intervals += 1
    xs = np.linspace(0.0, h, intervals + 1)
    acc = np.zeros((n, n))
    for i, s in enumerate(xs):
        E = expm(A * (h - s))
        val = E @ G @ E.T
        w = 1 if i in (0, intervals) else (4 if i % 2 else 2)
        acc += w * val
    return acc * (h / intervals) / 3.0


def van_loan_stable(A, G, h, max_exponent=0.5):
    """Scaling-and-squaring Van Loan.

    A single 2n x 2n exponential loses symmetry/PSD when |lambda|max * h is
    large (e.g. C at h=4 ms: |lambda|*h = 37). Splitting the step into
    2^n sub-steps with |lambda|*h/(2^n) <= max_exponent and composing
        Q(2h) = Phi(h) Q(h) Phi(h)^T + Q(h),  Phi(2h) = Phi(h)^2
    keeps Q_d symmetric and PSD to round-off at ~2 ms cost.
    """
    lam = float(np.max(np.abs(np.linalg.eigvals(A))))
    n = 0
    if lam > 0 and lam * h > max_exponent:
        n = int(np.ceil(np.log2(lam * h / max_exponent)))
    hs = h / (2 ** n)
    Phi, _, Qd = van_loan(A, G, hs)
    for _ in range(n):
        Qd = Phi @ Qd @ Phi.T + Qd
        Phi = Phi @ Phi
    return Phi, Qd



class StableRightIESEKF(_BaseFilter):
    """Mode B filter: identical to RightIESEKF except predict uses stable propagation."""
    def predict(self, dt, published_command):
        if self.stopped:
            from baselines.p2_pose_force.estimator import EstimatorDomainError
            raise EstimatorDomainError('FILTER_ALREADY_STOPPED')
        f, A = (self.rate_provider or _cont_lin)(
            self.state, published_command, self.modes, self.physics)
        pred, Phi, Qd, _ = propagate(self.state, f, A, dt, self.Qc_diag)
        P = _check_cov(Phi @ self.P @ Phi.T + Qd)
        rep = _PredReport(self.time, self.time + dt, Phi, Qd)
        self.state, self.P, self.time = pred, P, self.time + dt
        self.last_prediction = rep
        return rep
