"""P2 estimator qualification declaration, written before estimator implementation.

2026-10-14. These are component mathematics/interface cases, not transport runs.
Execution is conditional on the independent dynamics gate, controlled by root.

Required evidence:
  * 42D right retraction and independent owned state (native E1/E2, C b1->b2).
  * Table-II elastic measurements and full measurement differential. Force rows
    are compared in their corresponding Log-strain units (divide BOTH sides by
    the fixed K); primal signed forces are checked separately against mechanics.
  * Discrete Eq18 prediction differential against independent central retraction
    differences at frozen epsilon=1e-6, atol=1e-7, rtol=0. No FD in live filter.
  * Right covariance reset against a separate matrix Exp/Log oracle.
  * A fixed-prior iterated update consumes each packet once, keeps all states on
    SE3, uses Joseph covariance, and never updates the considered calibration.
  * Correct continuous-Q interval scaling; timestamp/duplicate rejection.
  * Any proposed equivalent fast G evaluator agrees with the byte-preserved
    canonical evaluator; this is not authorization to replace plant geometry.

No thresholds, protocol, random seeds or canonical geometry are edited here.
"""
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm, logm

from baselines.p2_pose_force import contact_geometry as geo
from baselines.p2_pose_force import mechanics as mech
from baselines.p2_pose_force.estimator import (
    FilterState, Observation, RightIESEKF, EstimatorDomainError,
    measurement_prediction, measurement_jacobian, prediction_linearization,
    right_reset_jacobian, fast_grasp_rate,
)


ROOT = Path(__file__).resolve().parents[1]
EPS = 1e-6
ATOL = 1e-7
KINDS = ('EE1', 'EE2', 'hK1', 'hK2', 'visual1', 'visual2')


@pytest.fixture
def protocol():
    return json.loads((ROOT/'configs/p2_closed_loop_protocol_v1.json').read_text())


@pytest.fixture
def physics(protocol):
    return mech.physics_from_protocol(protocol, observer=True)


@pytest.fixture
def state(protocol):
    s = mech.initial_state(protocol)
    d = np.zeros(42)
    d[:6] = [.0002, -.0001, .0001, .03, -.02, .01]
    d[30:36] = [.0001, -.0001, .0001, -.01, .01, -.01]
    d[36:42] = [-.0001, .0001, -.0001, .01, -.01, .01]
    s = s.retract(d)
    s.V = np.array([.01, -.005, .003, .08, -.06, .04])
    return FilterState.from_mechanics(s)


def covariance(protocol, kind):
    key = 'EE' if kind.startswith('EE') else 'hK' if kind.startswith('hK') else 'visual_object'
    return np.diag(protocol['original_parameters']['R'][key])


def observation(protocol, kind, value, index=0, stamp=0.):
    return Observation(kind=kind, value=value, covariance=covariance(protocol, kind),
                       sample_id=index, sample_stamp=stamp, delivery_stamp=stamp)


def make_filter(protocol, state, physics):
    return RightIESEKF.from_protocol(state, protocol, physics=physics,
                                    modes=('pivot', 'pivot'), initial_time=0.)


def hat(x):
    v, w = x[:3], x[3:]
    z = np.zeros((4, 4))
    z[:3, :3] = [[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]]
    z[:3, 3] = v
    return z


def log_oracle(T):
    m = logm(T)
    assert np.max(np.abs(m.imag)) <= 1e-10
    m = m.real
    return np.r_[m[:3, 3], m[2, 1], m[0, 2], m[1, 0]]


def test_state_contract_and_no_plant_alias(protocol):
    plant = mech.initial_state(protocol)
    f = FilterState.from_mechanics(plant)
    for name in mech.STATE_NAMES:
        assert not np.shares_memory(getattr(plant, name), getattr(f, name))
    d = np.zeros(42)
    d[0] = .001; d[11] = .002; d[25] = -.0003
    np.testing.assert_allclose(f.retract(d).local(f), d, atol=1e-12, rtol=0)
    assert f.E2.shape == (4, 4)
    np.testing.assert_allclose(f.C, plant.C, atol=0, rtol=0)


@pytest.mark.parametrize('kind', KINDS)
def test_original_measurement_and_analytic_jacobian(state, physics, kind):
    nominal = measurement_prediction(state, kind, physics)
    H = measurement_jacobian(state, kind, physics)
    contact = mech.mechanics(state, (np.zeros(6), np.zeros(6)),
                             ('pivot', 'pivot'), physics, decompose=False)
    if kind.startswith('hK'):
        np.testing.assert_allclose(nominal, contact.hK[int(kind[-1])-1], atol=1e-10, rtol=0)
    fd = np.zeros((6, 42))
    for i in range(42):
        d = np.zeros(42); d[i] = EPS
        plus = measurement_prediction(state.retract(d), kind, physics)
        minus = measurement_prediction(state.retract(-d), kind, physics)
        if kind.startswith('hK'):
            fd[:, i] = (plus-minus)/(2*EPS)
        else:
            fd[:, i] = (log_oracle(np.linalg.inv(nominal)@plus)
                        -log_oracle(np.linalg.inv(nominal)@minus))/(2*EPS)
    scale = np.array(physics.K[int(kind[-1])-1]) if kind.startswith('hK') else np.ones(6)
    np.testing.assert_allclose(H/scale[:, None], fd/scale[:, None], atol=ATOL, rtol=0)


@pytest.mark.parametrize('modes', [('tight', 'tight'), ('pivot', 'pivot'), ('pivot', 'sliding')])
def test_discrete_prediction_jacobian(state, physics, modes):
    U = (np.array([.004, -.002, .001, .03, -.02, .01]),
         np.array([-.003, .001, -.001, -.02, .015, -.01]))
    dt = .004
    predicted, F, L = prediction_linearization(state, U, modes, physics, dt)
    oracle = state.retract(dt*mech.state_rate(state, U, modes, physics))
    np.testing.assert_allclose(predicted.local(oracle), 0, atol=1e-10, rtol=0)
    fd = np.zeros((42, 42))
    for i in range(42):
        d = np.zeros(42); d[i] = EPS
        splus, sminus = state.retract(d), state.retract(-d)
        plus = splus.retract(dt*mech.state_rate(splus, U, modes, physics))
        minus = sminus.retract(dt*mech.state_rate(sminus, U, modes, physics))
        fd[:, i] = (plus.local(predicted)-minus.local(predicted))/(2*EPS)
    np.testing.assert_allclose(F, fd, atol=ATOL, rtol=0)
    assert F.shape == L.shape == (42, 42)


def test_right_reset_against_independent_matrix_oracle():
    delta = np.zeros(42)
    for i in (0, 2, 3, 5, 6):
        delta[6*i:6*i+6] = [.0003, -.0002, .0001, .04, -.03, .02]
    J = right_reset_jacobian(delta)
    fd = np.eye(42)
    for block in (0, 2, 3, 4, 5, 6):
        x = delta[6*block:6*block+6]
        T = expm(hat(x))
        for i in range(6):
            d = np.zeros(6); d[i] = EPS
            fd[6*block:6*block+6, 6*block+i] = (
                log_oracle(np.linalg.inv(T)@expm(hat(x+d)))
                -log_oracle(np.linalg.inv(T)@expm(hat(x-d))))/(2*EPS)
    np.testing.assert_allclose(J, fd, atol=ATOL, rtol=0)


def test_packet_iteration_keeps_one_prior(protocol, state, physics):
    filt = make_filter(protocol, state, physics)
    prior = filt.state.copy(); P0 = filt.P.copy()
    d = np.array([.002, 0, 0, 0, 0, 0])
    obs = observation(protocol, 'EE1', prior.E1@expm(hat(d)))
    report = filt.update([obs])
    var, noise = P0[12, 12], obs.covariance[0, 0]
    expected = var/(var+noise)*d[0]
    assert 1 <= report.iterations <= 5
    assert report.converged
    np.testing.assert_allclose(filt.state.local(prior)[12], expected, atol=1e-10, rtol=0)
    np.testing.assert_allclose(filt.P[12, 12], var*noise/(var+noise), atol=1e-10, rtol=0)
    assert np.linalg.eigvalsh(filt.P)[0] >= -1e-10


def test_schmidt_keeps_calibration_mean_and_covariance(protocol, state, physics):
    filt = make_filter(protocol, state, physics)
    for i in range(6):
        cross = .2*np.sqrt(filt.P[i, i]*filt.P[24+i, 24+i])
        filt.P[i, 24+i] = filt.P[24+i, i] = cross
    C, PCC, POC = filt.state.C.copy(), filt.P[24:30, 24:30].copy(), filt.P[:6, 24:30].copy()
    view = measurement_prediction(filt.state, 'visual2', physics)
    view = view@expm(hat(np.array([.001, -.0005, .0003, .003, -.002, .001])))
    report = filt.update([observation(protocol, 'visual2', view)])
    assert report.converged
    np.testing.assert_array_equal(filt.state.C, C)
    np.testing.assert_allclose(filt.P[24:30, 24:30], PCC, atol=1e-14, rtol=0)
    assert np.max(np.abs(filt.P[:6, 24:30]-POC)) > 1e-12
    assert np.linalg.eigvalsh(filt.P)[0] >= -1e-10
    for name in mech.POSE_NAMES:
        geo.validate_transform(getattr(filt.state, name))


def test_process_Q_scaling_at_actual_event_interval(protocol, state, physics):
    full = make_filter(protocol, state, physics)
    part = make_filter(protocol, state, physics)
    u = (np.zeros(6), np.zeros(6))
    rfull = full.predict(.004, u)
    rpart = part.predict(.001, u)
    expected = .004**2*np.array(protocol['original_parameters']['Q']['E1'])
    np.testing.assert_allclose(np.diag(rfull.process_covariance)[12:18], expected, atol=1e-20, rtol=0)
    np.testing.assert_allclose(np.diag(rpart.process_covariance)[12:18], expected/4, atol=1e-20, rtol=0)
    np.testing.assert_allclose(rfull.process_covariance[24:30], 0, atol=0, rtol=0)


def test_duplicate_and_wrong_timestamp_are_rejected(protocol, state, physics):
    filt = make_filter(protocol, state, physics)
    obs = observation(protocol, 'EE1', filt.state.E1.copy())
    filt.update([obs])
    state_before, P_before = filt.state.copy(), filt.P.copy()
    with pytest.raises(EstimatorDomainError):
        filt.update([obs])
    np.testing.assert_allclose(filt.state.local(state_before), 0, atol=0, rtol=0)
    np.testing.assert_array_equal(filt.P, P_before)
    future = observation(protocol, 'EE2', filt.state.E2.copy(), stamp=.001)
    with pytest.raises(EstimatorDomainError):
        filt.update([future])


@pytest.mark.parametrize('mode', ['tight', 'pivot', 'sliding'])
def test_equivalent_fast_geometry_against_canonical(protocol, state, mode):
    E = state.E1; G = state.G1; U = np.array([.003, -.002, .001, .03, -.02, .01])
    H = geo.selection(mode)
    expected = geo.grasp_rate(state.O, E, G, state.V, U, H)
    got = fast_grasp_rate(state.O, E, G, state.V, U, H)
    for name in ('D', 'tau', 'relative_body', 'grasp_body', 'tau_rate', 'constraint_matrix'):
        np.testing.assert_allclose(getattr(got, name), getattr(expected, name), atol=1e-10, rtol=0)
