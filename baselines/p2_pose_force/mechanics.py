"""P2 Eq9--12/16 independent COM dynamics. Linear-first body coordinates.

The frozen, approved G evolution is imported without modification. No desired
pose, sensor, observer, or controller is an input to this plant module.
"""
from dataclasses import dataclass
import numpy as np
from scipy.linalg import block_diag
from scipy.spatial.transform import Rotation
from .contact_geometry import (adjoint, inverse, se3_exp, se3_log, selection,
                               grasp_rate, skew, validate_transform)

POSE_NAMES = ('O', 'E1', 'E2', 'C', 'G1', 'G2')
STATE_NAMES = ('O', 'V', 'E1', 'E2', 'C', 'G1', 'G2')


@dataclass
class State:
    O: np.ndarray
    V: np.ndarray
    E1: np.ndarray
    E2: np.ndarray
    C: np.ndarray
    G1: np.ndarray
    G2: np.ndarray

    def copy(self):
        return State(*(getattr(self, n).copy() for n in STATE_NAMES))

    def retract(self, delta):
        delta = np.asarray(delta, float).reshape(42)
        return State(*(getattr(self, n) + delta[6*i:6*i+6] if n == 'V'
                       else getattr(self, n) @ se3_exp(delta[6*i:6*i+6])
                       for i, n in enumerate(STATE_NAMES)))

    def local(self, other):
        return np.concatenate([getattr(self, n)-getattr(other, n) if n == 'V'
                               else se3_log(inverse(getattr(other, n)) @ getattr(self, n))
                               for n in STATE_NAMES])

    def as_dict(self):
        return {n: getattr(self, n).tolist() for n in STATE_NAMES}


@dataclass
class Physics:
    mass: float
    inertia_diag: np.ndarray
    K: tuple
    B: np.ndarray
    Ba: np.ndarray
    gravity: np.ndarray

    @property
    def M_diag(self):
        return np.r_[np.full(3, self.mass), self.inertia_diag]


def physics_from_protocol(config, object_id='A', condition='exp3', observer=False):
    obj = config['model']['objects'][object_id]
    m = obj['mass_kg']; x, y, z = obj['dimensions_m']
    par = config['original_parameters']
    K = (np.array(par['K_nominal'], float), np.array(par['K_nominal'], float))
    if observer and condition == 'exp4':
        K = tuple(np.array(par['exp4_model_K'+str(r)], float) for r in (1, 2))
    return Physics(m, m/12*np.array([y*y+z*z, x*x+z*z, x*x+y*y]),
                   K, np.array(par['B_nominal'], float),
                   np.array(par['B_air'], float),
                   np.array(config['model']['gravity_m_s2'], float))


def transform(position, rotation=None):
    T = np.eye(4); T[:3, 3] = position
    if rotation is not None: T[:3, :3] = rotation
    return T


def initial_state(config, variant='transport'):
    model = config['model']
    C = transform(model['true_C_b1_to_b2']['translation_m'],
                  Rotation.from_rotvec([0, 0, np.pi]).as_matrix())
    if variant == 'sliding':
        obj = config['suite']['conditional_sliding']
        O = transform(obj['initial_pose']['position_m'],
                      Rotation.from_rotvec([0, -np.pi/2, 0]).as_matrix())
        specs = obj['grasps']
    else:
        R = Rotation.from_rotvec([0, 0, 3*np.pi/4]).as_matrix() if variant == 'high_moment' else np.eye(3)
        O = transform(model['initial_nominal_O_A']['translation_m'], R)
        specs = model['A_grasps']
    G1, G2 = [transform(s['translation_in_object_m'],
                       np.array(s['R_columns_in_object']).T) for s in specs]
    return State(O, np.zeros(6), O @ G1, C @ O @ G2, C, G1, G2)


def common_endpoints(state):
    return state.E1, inverse(state.C) @ state.E2


@dataclass
class Contact:
    D: np.ndarray
    tau: np.ndarray
    hK: np.ndarray
    hB: np.ndarray
    h: np.ndarray
    H: np.ndarray
    W: np.ndarray
    external: np.ndarray
    internal: np.ndarray | None
    singular_values: np.ndarray | None


def mechanics(state, U, modes, physics, *, decompose=True):
    Es = common_endpoints(state); Gs = (state.G1, state.G2)
    Ds = []; taus = []; elast = []; damp = []; maps = []
    for r, (E, G) in enumerate(zip(Es, Gs)):
        D = inverse(E) @ state.O @ G; tau = se3_log(D)
        Rbar = block_diag(D[:3, :3], D[:3, :3])
        # Preserve the paper's Rbar approximation: NOT Ad(D) or exact D rate.
        relative = Rbar @ adjoint(inverse(G)) @ state.V - U[r]
        Ds.append(D); taus.append(tau)
        elast.append(-physics.K[r] * tau); damp.append(-physics.B * relative)
        A = G @ inverse(D)  # T^o_e, includes physical wrench application point.
        maps.append(adjoint(inverse(A)).T)
    H = block_diag(*(selection(mode) for mode in modes))
    W = np.hstack(maps) @ H.T
    hK = np.array(elast); hB = np.array(damp); h = hK+hB
    transmitted = H @ h.ravel()
    external = W @ transmitted
    if decompose:
        internal = (H.T @ (transmitted - np.linalg.pinv(W, rcond=1e-12) @ external)).reshape(2, 6)
        sig = np.linalg.svd(W, compute_uv=False)
    else:
        internal, sig = None, None
    return Contact(np.array(Ds), np.array(taus), hK, hB, h, H, W,
                   external, internal, sig)


def acceleration(state, external, physics):
    v, w = state.V[:3], state.V[3:]
    C = np.block([[skew(w), np.zeros((3, 3))], [skew(v), skew(w)]])
    return ((external - physics.Ba*state.V - C @ (physics.M_diag*state.V))
            / physics.M_diag + np.r_[state.O[:3, :3].T @ physics.gravity, np.zeros(3)])


def state_rate(state, U, modes, physics):
    contact = mechanics(state, U, modes, physics, decompose=False)
    rate = np.zeros(42); rate[:6] = state.V
    rate[6:12] = acceleration(state, contact.external, physics)
    rate[12:18] = U[0]; rate[18:24] = U[1]
    for r, (E, G) in enumerate(zip(common_endpoints(state), (state.G1, state.G2))):
        result = grasp_rate(state.O, E, G, state.V, U[r], selection(modes[r]))
        rate[30+6*r:36+6*r] = result.grasp_body
    return rate


def midpoint_step(state, U, modes, physics, dt):
    """Explicit coupled Lie exponential midpoint; no geometric projection."""
    first = state_rate(state, U, modes, physics)
    half = state.retract(.5*dt*first)
    second = state_rate(half, U, modes, physics)
    return state.retract(dt*second)


def validate_state(state, contact=None):
    for name in POSE_NAMES: validate_transform(getattr(state, name))
    if not np.all(np.isfinite(state.V)): raise ValueError('NONFINITE_STATE')
    if contact is not None:
        if not np.all(np.isfinite(contact.h)): raise ValueError('NONFINITE_CONTACT')
        if np.any(np.abs(contact.tau[:, :3]) > .005) or np.any(np.abs(contact.tau[:, 3:]) > .15):
            raise ValueError('PAD_DOMAIN_INVALID')


def equilibrium_residual(state, contact, physics):
    gravity_force = np.r_[physics.mass * (state.O[:3, :3].T @ physics.gravity), np.zeros(3)]
    return contact.external + gravity_force
