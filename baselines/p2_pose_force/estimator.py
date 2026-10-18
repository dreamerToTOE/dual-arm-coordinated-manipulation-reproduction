"""P2 independent 42D right-SE(3) iterated error-state Kalman filter.

State: O,V,E1(native),E2(native),C(b1->b2),G1,G2. Prediction is paper
Eq18 right Euler, irrespective of the separately approved implicit plant.
Analytic F/H; finite differences are qualification oracles only. The fixed
prior is reused across all inner iterations. C is a Schmidt considered state,
Joseph covariance is injected/reset once, and each fresh packet is consumed
once. No ground-truth state, force, velocity or desired trajectory input exists.

The existing canonical contact_geometry module is not modified. The equivalent
small-angle geometry evaluator below must be qualified against that reference.
"""
from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.linalg import cho_factor, cho_solve, solve_triangular

from . import contact_geometry as geo
from . import mechanics as mech
from .observations import FilterState, Observation


DIM = 42
KINDS = ('EE1', 'EE2', 'hK1', 'hK2', 'visual1', 'visual2')
POSE_BLOCKS = (0, 2, 3, 4, 5, 6)
EYE6 = np.eye(6)
EYE42 = np.eye(DIM)
C_SLICE = slice(24, 30)


class EstimatorDomainError(ValueError):
    pass


def _finite(value, shape):
    a = np.asarray(value, dtype=float)
    if a.shape != shape or not np.all(np.isfinite(a)):
        raise EstimatorDomainError('NONFINITE_OR_WRONG_SHAPE')
    return a


def _skew(v):
    x, y, z = v
    return np.array([[0., -z, y], [z, 0., -x], [-y, x, 0.]])


def ad(x):
    out = np.zeros((6, 6))
    out[:3, :3] = out[3:, 3:] = _skew(x[3:])
    out[:3, 3:] = _skew(x[:3])
    return out


def _inverse(T):
    # Inputs are SE3 states; no projection, normalization or general inverse.
    out = np.eye(4)
    out[:3, :3] = T[:3, :3].T
    out[:3, 3] = -out[:3, :3]@T[:3, 3]
    return out


def _adjoint(T):
    out = np.zeros((6, 6))
    out[:3, :3] = out[3:, 3:] = T[:3, :3]
    out[:3, 3:] = _skew(T[:3, 3])@T[:3, :3]
    return out


def right_jacobian(x):
    """Convergent ad series, not the 12x12 expm reference implementation."""
    x = _finite(x, (6,))
    A = -ad(x)
    term = EYE6.copy(); total = term.copy()
    for n in range(1, 65):
        term = term@A/(n+1)
        total += term
        if n >= 3 and np.max(np.abs(term)) <= 1e-17:
            return total
    raise EstimatorDomainError('RIGHT_JACOBIAN_SERIES_NOT_CONVERGED')


def _jacobian_direction_times(x, w):
    """Columns are (d Jr(x)/d x_i) w, with w held fixed."""
    A = -ad(x)
    q = np.asarray(w, float).copy(); derivative = np.zeros((6, 6))
    total = np.zeros((6, 6)); factorial = 1.
    for n in range(1, 65):
        derivative = A@derivative + ad(q)
        q = A@q
        factorial *= n+1
        term = derivative/factorial
        total += term
        if n >= 3 and np.max(np.abs(term)) <= 1e-17*(1+np.max(np.abs(w))):
            return total
    raise EstimatorDomainError('JACOBIAN_DIRECTION_SERIES_NOT_CONVERGED')


def _left_inverse_jacobian(x):
    return np.linalg.solve(right_jacobian(-x), EYE6)


def _wrench_direction(y):
    out = np.zeros((6, 6))
    out[:3, 3:] = out[3:, :3] = _skew(y[:3])
    out[3:, 3:] = _skew(y[3:])
    return out


def _selector(block):
    out = np.zeros((6, DIM))
    out[:, 6*block:6*block+6] = EYE6
    return out


SELECTORS = tuple(_selector(i) for i in range(7))


def _null(H, supplied=None):
    H = np.asarray(H, dtype=float)
    if (H.ndim != 2 or H.shape[1] != 6 or not 1 <= H.shape[0] <= 6
            or not np.all(np.isfinite(H))
            or not np.allclose(H@H.T, np.eye(H.shape[0]), atol=1e-10, rtol=0)):
        raise EstimatorDomainError('INVALID_CONTACT_SELECTION')
    n = 6-H.shape[0]
    if supplied is None:
        # Exact standard bases avoid repeated SVD. Other H retains explicit SVD.
        if np.array_equal(H, EYE6):
            N = np.empty((6, 0))
        elif np.array_equal(H, EYE6[:5]):
            N = EYE6[:, 5:]
        elif np.array_equal(H, EYE6[2:]):
            N = EYE6[:, :2]
        else:
            N = np.linalg.svd(H, full_matrices=True)[2][H.shape[0]:].T
    else:
        N = _finite(supplied, (6, n))
    if (not np.allclose(H@N, np.zeros((H.shape[0], n)), atol=1e-10, rtol=0)
            or not np.allclose(N.T@N, np.eye(n), atol=1e-10, rtol=0)):
        raise EstimatorDomainError('INVALID_FREE_BASIS')
    return H, N.copy()


def _geometry_from_D(D, G, V, U, H, N, rcond=1e-12):
    tau = geo.se3_log(D)
    if np.linalg.norm(tau[3:]) >= np.pi-1e-6:
        raise EstimatorDomainError('PRINCIPAL_LOG_CHART_BOUNDARY')
    AdGi, AdDi = _adjoint(_inverse(G)), _adjoint(_inverse(D))
    q, z = AdGi@V, AdDi@U
    a = q-z
    J = right_jacobian(tau)
    L = np.linalg.solve(J, EYE6)
    if N.shape[1]:
        Ng = AdDi@N
        A = N.T@L@Ng
        sigma = np.linalg.svd(A, compute_uv=False)
        if sigma[-1] <= rcond*sigma[0]:
            raise EstimatorDomainError('FREE_CONSTRAINT_SINGULAR')
        VG = -Ng@np.linalg.solve(A, N.T@L@a)
    else:
        Ng, A, sigma, VG = np.empty((6, 0)), np.empty((0, 0)), np.empty(0), np.zeros(6)
    rate = L@(a+VG)
    return geo.GeometryRate(D, tau, a, VG, rate, N, A, sigma), (L, Ng, q, z, AdGi)


def fast_grasp_rate(O, E, G, V_o, U_EE, H, *, null_basis=None, rcond=1e-12):
    """Same approved model as canonical grasp_rate; no state changes or reset."""
    O, E, G = map(geo.validate_transform, (O, E, G))
    V, U = _finite(V_o, (6,)), _finite(U_EE, (6,))
    if not np.isfinite(rcond) or not 0 < rcond < 1:
        raise EstimatorDomainError('INVALID_RCOND')
    H, N = _null(H, null_basis)
    D = _inverse(E)@O@G
    return _geometry_from_D(D, G, V, U, H, N, rcond)[0]


def _contact_pose_and_jacobian(state, arm):
    G = state.G1 if arm == 0 else state.G2
    if arm == 0:
        T = _inverse(state.E1)@state.O
    else:
        T = _inverse(state.E2)@state.C@state.O
    D = T@G
    JD = np.zeros((6, DIM))
    JD[:, :6] = _adjoint(_inverse(G))
    JD[:, 12+6*arm:18+6*arm] = -_adjoint(_inverse(D))
    JD[:, 30+6*arm:36+6*arm] = EYE6
    if arm:
        JD[:, 24:30] = _adjoint(_inverse(state.O@G))
    return T, D, G, JD


def _measurement(state, kind, physics, jacobian=True):
    H = np.zeros((6, DIM)) if jacobian else None
    if kind == 'EE1' or kind == 'EE2':
        arm = int(kind[-1])-1
        value = (state.E1 if arm == 0 else state.E2).copy()
        if jacobian:
            H[:, 12+6*arm:18+6*arm] = EYE6
    elif kind == 'visual1':
        value = state.O.copy()
        if jacobian:
            H[:, :6] = EYE6
    elif kind == 'visual2':
        value = state.C@state.O
        if jacobian:
            H[:, :6] = EYE6
            H[:, 24:30] = _adjoint(_inverse(state.O))
    elif kind == 'hK1' or kind == 'hK2':
        arm = int(kind[-1])-1
        _, D, _, JD = _contact_pose_and_jacobian(state, arm)
        tau = geo.se3_log(D)
        K = np.asarray(physics.K[arm], float)
        value = -K*tau
        if jacobian:
            H = -K[:, None]*np.linalg.solve(right_jacobian(tau), JD)
    else:
        raise EstimatorDomainError('UNKNOWN_MEASUREMENT_KIND')
    return value, H


def measurement_prediction(state, kind, physics):
    return _measurement(state, kind, physics, False)[0]


def measurement_jacobian(state, kind, physics):
    return _measurement(state, kind, physics, True)[1]


def continuous_linearization(state, U, modes, physics):
    """Return (paper vector field, analytic derivative wrt right prior error)."""
    U = tuple(_finite(u, (6,)) for u in U)
    if len(U) != 2 or len(modes) != 2:
        raise EstimatorDomainError('EXPECTED_TWO_CONTACTS')
    f = np.zeros(DIM); A = np.zeros((DIM, DIM))
    f[:6] = state.V; A[:6, 6:12] = EYE6
    f[12:18], f[18:24] = U
    external = np.zeros(6); Jexternal = np.zeros((6, DIM))
    for arm in range(2):
        H, N = _null(geo.selection(modes[arm]))
        T, D, G, JD = _contact_pose_and_jacobian(state, arm)
        result, (L, Ng, q, z, AdGi) = _geometry_from_D(D, G, state.V, U[arm], H, N)
        R = D[:3, :3]
        Rbar = np.zeros((6, 6)); Rbar[:3, :3] = Rbar[3:, 3:] = R
        Jq = np.zeros((6, DIM))
        Jq[:, 6:12] = AdGi
        Jq[:, 30+6*arm:36+6*arm] = ad(q)
        Jrelative = Rbar@Jq - np.vstack((R@_skew(q[:3]), R@_skew(q[3:])))@JD[3:]
        tau, B, K = result.tau, np.asarray(physics.B), np.asarray(physics.K[arm])
        h = -K*tau-B*(Rbar@q-U[arm])
        Jh = -K[:, None]*(L@JD)-B[:, None]*Jrelative
        P_h = H.T@H
        map_wrench = _adjoint(T).T
        y = map_wrench@(P_h@h)
        JT = np.zeros((6, DIM)); JT[:, :6] = EYE6
        JT[:, 12+6*arm:18+6*arm] = -_adjoint(_inverse(T))
        if arm:
            JT[:, 24:30] = _adjoint(_inverse(state.O))
        external += y
        Jexternal += _wrench_direction(y)@JT + map_wrench@P_h@Jh
        VG = result.grasp_body
        f[30+6*arm:36+6*arm] = VG
        if N.shape[1]:
            Ja = Jq-ad(z)@JD
            dJ_times = _jacobian_direction_times(tau, result.tau_rate)
            preliminary = ad(VG)@JD
            rhs = N.T@L@(Ja+preliminary-dJ_times@L@JD)
            A[30+6*arm:36+6*arm] = preliminary-Ng@np.linalg.solve(result.constraint_matrix, rhs)
    M = np.asarray(physics.M_diag)
    V = state.V
    C_V = -ad(V).T
    g_body = state.O[:3, :3].T@physics.gravity
    f[6:12] = ((external-physics.Ba*V-C_V@(M*V))/M
               +np.r_[g_body, np.zeros(3)])
    A[6:12] = Jexternal/M[:, None]
    A[6:12, 6:12] -= (np.diag(physics.Ba)+C_V*M[None, :]-_wrench_direction(M*V))/M[:, None]
    A[6:9, 3:6] += _skew(g_body)
    if not np.all(np.isfinite(f)) or not np.all(np.isfinite(A)):
        raise EstimatorDomainError('NONFINITE_DYNAMICS_LINEARIZATION')
    return f, A


def right_reset_jacobian(delta):
    delta = _finite(delta, (DIM,))
    out = EYE42.copy()
    for block in POSE_BLOCKS:
        sl = slice(6*block, 6*block+6)
        out[sl, sl] = right_jacobian(delta[sl])
    return out


def prediction_linearization(state, U, modes, physics, dt, *, rate_provider=None):
    """Exact differential of X boxplus(dt*f), NOT an implicit observer step."""
    if not np.isfinite(dt) or dt <= 0:
        raise EstimatorDomainError('INVALID_PREDICTION_INTERVAL')
    provider = continuous_linearization if rate_provider is None else rate_provider
    f, A = provider(state, U, modes, physics)
    f, A = _finite(f, (DIM,)), _finite(A, (DIM, DIM))
    increment = dt*f
    predicted = state.retract(increment)
    F = EYE42.copy()+dt*A; Lw = EYE42.copy()
    for block in POSE_BLOCKS:
        sl = slice(6*block, 6*block+6)
        J = right_jacobian(increment[sl])
        F[sl] = dt*J@A[sl]
        F[sl, sl] += _adjoint(geo.se3_exp(-increment[sl]))
        Lw[sl, sl] = J
    return predicted, F, Lw


def _checked_covariance(P):
    P = _finite(P, (DIM, DIM))
    asymmetry = float(np.max(np.abs(P-P.T)))
    if asymmetry > 1e-10:
        raise EstimatorDomainError('COVARIANCE_ASYMMETRY')
    # Average only after the frozen asymmetry check; never clip eigenvalues.
    P = (P+P.T)/2
    try:
        cho_factor(P, lower=True, check_finite=False)
    except np.linalg.LinAlgError:
        if np.linalg.eigvalsh(P)[0] < -1e-10:
            raise EstimatorDomainError('COVARIANCE_NEGATIVE_EIGENVALUE')
    return P


@dataclass
class PredictionReport:
    start_stamp: float
    end_stamp: float
    transition: np.ndarray
    process_covariance: np.ndarray


@dataclass
class UpdateReport:
    stamp: float
    iterations: int
    converged: bool
    increment: np.ndarray
    iteration_increments: tuple
    innovation_before: np.ndarray
    innovation_after: np.ndarray
    sample_keys: tuple
    consecutive_nonconverged: int
    stop_requested: bool
    stop_reason: str | None
    prior_information_consumptions: int = 1


class RightIESEKF:
    """Anchored iterated right-error update with an uncertain fixed calibration."""
    def __init__(self, state, physics, modes, covariance, process_noise_continuous,
                 *, initial_time=0., maximum_iterations=5, convergence=None,
                 stop_after_nonconverged=3, rate_provider: Callable | None = None):
        if maximum_iterations != 5 or stop_after_nonconverged != 3:
            raise EstimatorDomainError('FROZEN_ITERATION_OR_STOP_LIMIT_CHANGED')
        self.state = (state.copy() if isinstance(state, FilterState)
                      else FilterState.from_mechanics(state))
        self.physics = mech.Physics(float(physics.mass), np.array(physics.inertia_diag, float).copy(),
                                   tuple(np.array(k, float).copy() for k in physics.K),
                                   np.array(physics.B, float).copy(), np.array(physics.Ba, float).copy(),
                                   np.array(physics.gravity, float).copy())
        self.modes = tuple(modes)
        for mode in self.modes:
            geo.selection(mode)
        if len(self.modes) != 2:
            raise EstimatorDomainError('EXPECTED_TWO_CONTACTS')
        self.P = _checked_covariance(covariance).copy()
        self.Qc_diag = _finite(process_noise_continuous, (DIM,)).copy()
        if np.any(self.Qc_diag < 0) or np.any(self.Qc_diag[C_SLICE] != 0):
            raise EstimatorDomainError('INVALID_PROCESS_NOISE_OR_UNFROZEN_C')
        self.time = float(initial_time)
        if not np.isfinite(self.time):
            raise EstimatorDomainError('INVALID_INITIAL_TIME')
        self.maximum_iterations = maximum_iterations
        self.stop_after_nonconverged = stop_after_nonconverged
        self.convergence = (np.r_[np.full(6, 1e-6), np.full(6, 1e-5), np.full(30, 1e-6)]
                            if convergence is None else _finite(convergence, (DIM,)).copy())
        if np.any(self.convergence <= 0):
            raise EstimatorDomainError('INVALID_CONVERGENCE_LIMIT')
        self.rate_provider = rate_provider
        self.seen_samples = set()
        self.consecutive_nonconverged = 0
        self.stopped = False
        self.last_update_matrices = None
        self.last_prediction = None
        self.last_update = None

    @classmethod
    def from_protocol(cls, state, config, *, physics=None, modes=None,
                      initial_time=0., condition='exp3', object_id='A', rate_provider=None):
        est = config['estimator']; params = config['original_parameters']
        Pdiag = np.concatenate([np.array(est['P0_blocks'][name], float)
                                for name in ('O', 'V', 'E1', 'E2', 'C', 'G1', 'G2')])
        Qdiag = .004*np.concatenate([np.array(params['Q'][name], float)
                                   for name in ('O', 'V', 'E1', 'E2', 'C_transport', 'G1', 'G2')])
        cv = est['convergence']
        pose_tol = np.r_[np.full(3, cv['pose_translation_component_m']),
                         np.full(3, cv['pose_rotation_component_rad'])]
        vel_tol = np.r_[np.full(3, cv['velocity_linear_component_m_s']),
                        np.full(3, cv['velocity_angular_component_rad_s'])]
        convergence = np.r_[pose_tol, vel_tol, np.tile(pose_tol, 5)]
        physics = (mech.physics_from_protocol(config, object_id, condition, observer=True)
                   if physics is None else physics)
        modes = tuple(config['model']['mode_transport']) if modes is None else modes
        return cls(state, physics, modes, np.diag(Pdiag), Qdiag, initial_time=initial_time,
                   maximum_iterations=est['maximum_update_iterations'], convergence=convergence,
                   stop_after_nonconverged=est['stop_after_consecutive_nonconverged_updates'],
                   rate_provider=rate_provider)

    def predict(self, dt, published_command):
        if self.stopped:
            raise EstimatorDomainError('FILTER_ALREADY_STOPPED')
        predicted, F, Lw = prediction_linearization(self.state, published_command, self.modes,
                                                   self.physics, dt, rate_provider=self.rate_provider)
        Qd = dt*(Lw*self.Qc_diag[None, :])@Lw.T
        posterior_P = _checked_covariance(F@self.P@F.T+Qd)
        report = PredictionReport(self.time, self.time+dt, F, Qd)
        self.state, self.P, self.time = predicted, posterior_P, self.time+dt
        self.last_prediction = report
        return report

    def predict_to(self, stamp, published_command):
        stamp = float(stamp)
        if not np.isfinite(stamp) or stamp < self.time-1e-12:
            raise EstimatorDomainError('OUT_OF_SEQUENCE_PREDICTION')
        dt = stamp-self.time
        if abs(dt) <= 1e-12:
            return None
        report = self.predict(dt, published_command)
        self.time = stamp
        report.end_stamp = stamp
        return report

    def _check_packet(self, observations):
        if self.stopped:
            raise EstimatorDomainError('FILTER_ALREADY_STOPPED')
        packet = tuple(observations)
        if not packet:
            raise EstimatorDomainError('EMPTY_MEASUREMENT_PACKET')
        keys = []
        for obs in packet:
            if obs.kind not in KINDS:
                raise EstimatorDomainError('UNKNOWN_MEASUREMENT_KIND')
            if (not np.isfinite(obs.sample_stamp) or not np.isfinite(obs.delivery_stamp)
                    or abs(obs.sample_stamp-self.time) > 1e-12
                    or obs.delivery_stamp < obs.sample_stamp-1e-12
                    or abs(obs.delivery_stamp-self.time) > 1e-12):
                raise EstimatorDomainError('STALE_FUTURE_OR_WRONG_DELIVERY_TIMESTAMP')
            key = (obs.kind, obs.sample_id)
            try:
                if key in self.seen_samples or key in keys:
                    raise EstimatorDomainError('DUPLICATE_MEASUREMENT_ID')
            except TypeError as exc:
                raise EstimatorDomainError('UNHASHABLE_SAMPLE_ID') from exc
            keys.append(key)
            if obs.kind.startswith('hK'):
                _finite(obs.value, (6,))
            else:
                geo.validate_transform(obs.value)
            R = _finite(obs.covariance, (6, 6))
            if np.max(np.abs(R-R.T)) > 1e-10:
                raise EstimatorDomainError('MEASUREMENT_COVARIANCE_ASYMMETRY')
            try:
                cho_factor(R, lower=True, check_finite=False)
            except np.linalg.LinAlgError as exc:
                raise EstimatorDomainError('MEASUREMENT_COVARIANCE_NOT_POSITIVE') from exc
        return packet, tuple(keys)

    def _linearized_packet(self, state, observations, anchor_map):
        residuals, whitened, jacobians = [], [], []
        for obs in observations:
            expected, H = _measurement(state, obs.kind, self.physics)
            if obs.kind.startswith('hK'):
                residual = np.asarray(obs.value)-expected
            else:
                residual = geo.se3_log(_inverse(expected)@obs.value)
                H = _left_inverse_jacobian(residual)@H
            H = H@anchor_map
            R = np.asarray(obs.covariance)
            diagonal = np.diag(R)
            if np.array_equal(R, np.diag(diagonal)):
                sd = np.sqrt(diagonal)
                rw, Hw = residual/sd, H/sd[:, None]
            else:
                sqrtR = np.linalg.cholesky(R)
                rw = solve_triangular(sqrtR, residual, lower=True, check_finite=False)
                Hw = solve_triangular(sqrtR, H, lower=True, check_finite=False)
            residuals.append(residual); whitened.append(rw); jacobians.append(Hw)
        return np.concatenate(residuals), np.concatenate(whitened), np.vstack(jacobians)

    @staticmethod
    def _gain(P0, Hw):
        cross = P0@Hw.T
        S = np.eye(Hw.shape[0])+Hw@cross
        try:
            factor = cho_factor((S+S.T)/2, lower=True, check_finite=False)
            K = cho_solve(factor, cross.T, check_finite=False).T
        except np.linalg.LinAlgError as exc:
            raise EstimatorDomainError('INNOVATION_COVARIANCE_NOT_POSITIVE') from exc
        K[C_SLICE] = 0.
        return K

    def update(self, observations):
        observations, keys = self._check_packet(observations)
        prior = self.state.copy(); P0 = _checked_covariance(self.P).copy()
        delta = np.zeros(DIM); current = prior
        increments = []; converged = False; innovation_before = None
        for iteration in range(self.maximum_iterations):
            T = right_reset_jacobian(delta)
            residual, rw, Hw = self._linearized_packet(current, observations, T)
            if innovation_before is None:
                innovation_before = residual.copy()
            K = self._gain(P0, Hw)
            candidate_delta = K@(rw+Hw@delta)
            candidate_delta[C_SLICE] = 0.
            candidate = prior.retract(candidate_delta)
            change = candidate.local(current)
            increments.append(change.copy())
            delta, current = candidate_delta, candidate
            if np.all(np.abs(change) <= self.convergence):
                converged = True
                break
        # Relinearize final covariance without a sixth state-update iteration.
        reset = right_reset_jacobian(delta)
        residual, rw, Hw = self._linearized_packet(current, observations, reset)
        K = self._gain(P0, Hw)
        IKH = EYE42-K@Hw
        Panchor = IKH@P0@IKH.T+K@K.T  # R is identity after exact whitening.
        posterior = _checked_covariance(reset@Panchor@reset.T)
        for name in mech.POSE_NAMES:
            geo.validate_transform(getattr(current, name))
        _finite(current.V, (6,))
        self.consecutive_nonconverged = 0 if converged else self.consecutive_nonconverged+1
        stop = self.consecutive_nonconverged >= self.stop_after_nonconverged
        report = UpdateReport(self.time, len(increments), converged, delta.copy(), tuple(increments),
                              innovation_before, residual.copy(), keys, self.consecutive_nonconverged,
                              stop, 'IESEKF_THREE_NONCONVERGED_UPDATES' if stop else None)
        self.state, self.P = current, posterior
        self.seen_samples.update(keys)
        self.stopped = stop
        self.last_update_matrices = (P0, Hw, K, reset, Panchor)
        self.last_update = report
        return report
