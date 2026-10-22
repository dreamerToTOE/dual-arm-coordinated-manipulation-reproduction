"""Dual-arm constrained numerical task (E1).

Two UR3 chains hold a shared object: the relative pose is kept fixed by
per-step null-space projection, while the absolute pose is driven to a target
under joint limits, spherical obstacles and a tilt bound.

The task is deliberately small enough to run on a CPU; it is not a replica of
the paper's six scenes.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .cost import (
    CostConfig,
    collision_cost,
    singularity_cost,
    stagnation_cost,
    terminal_goal_cost,
    tilt_cost,
)
from .dq import dq_conj, dq_from_rt, dq_mul, dq_to_rt, q_from_rotmat, q_to_rotmat
from .kinematics import SerialChain, absolute_pose, relative_jacobian, relative_pose
from .nullspace import project_step

UR3_DH = np.array(
    [
        [0.0, 0.1519, 0.0, 1.5708],
        [0.0, 0.0, -0.24365, 0.0],
        [0.0, 0.0, -0.21325, 0.0],
        [0.0, 0.11235, 0.0, 1.5708],
        [0.0, 0.08535, 0.0, -1.5708],
        [0.0, 0.0819, 0.0, 0.0],
    ]
)
BASE1 = np.array([0.612384, 0.353533, -0.353533, 0.612384, -0.087881, 0.013986, 0.013986, 0.087881])
BASE2 = np.array([-0.612384, 0.353533, -0.353533, -0.612384, 0.087864, 0.013983, 0.013983, -0.087864])
HOME1 = np.array([0.0, -1.0, 0.5, -1.5, 0.3, 0.2])
HOME2 = np.array([0.2, -0.9, 0.4, -1.4, 0.25, 0.15])


@dataclass
class DualArmTask:
    horizon: int = 15
    dt: float = 0.15
    cfg: CostConfig = field(default_factory=CostConfig.paper)
    n_points_per_link: int = 3
    safety_margin: float = 0.01
    use_singularity: bool = False  # paper Eq. (41) includes C_sing per step

    def __post_init__(self):
        self.c1 = SerialChain(UR3_DH, base=BASE1)
        self.c2 = SerialChain(UR3_DH, base=BASE2)
        self.q_home = np.concatenate([HOME1, HOME2])
        self.x1_0 = self.c1.fk(HOME1[None])[0]
        self.x2_0 = self.c2.fk(HOME2[None])[0]
        self.xr_0 = relative_pose(self.x1_0[None], self.x2_0[None])[0]
        self.xa_0 = absolute_pose(self.x1_0[None], self.x2_0[None])[0]
        # Target: a 6 cm lift plus a 4 deg rotation about x, applied in world.
        # Small object motion: at this grasp the absolute-pose Jacobian is
        # poorly conditioned (sigma_min ~ 0.12), so a 6 cm step needs ~1.7 rad
        # of joint motion.  The task therefore uses a 1.5 cm / 1 deg step and
        # reports the conditioning limit explicitly.
        qd = np.array([np.cos(np.deg2rad(0.5)), np.sin(np.deg2rad(0.5)), 0.0, 0.0])
        self.delta = dq_from_rt(qd, np.array([0.0, 0.0, 0.015]))
        self.xa_d = dq_mul(self.delta, self.xa_0)
        self.ref_z = self._rotated_z(self.xa_0)
        self.pos_d = dq_to_rt(self.xa_d[None])[1][0]
        # Two spherical obstacles with 3 cm clearance from the home links.
        self.obstacles = np.array([[0.32, -0.30, 0.55], [0.32, 0.32, 0.55]])
        self.obstacle_radii = np.array([0.05, 0.05])
        self.q_min = np.full(12, -2.8)
        self.q_max = np.full(12, 2.8)
        self.dq_max = np.full(12, 0.8)
        self.dq_min = -self.dq_max
        self.ddq_max = np.full(12, 2.0)
        self.link_points = None

    # ------------------------------------------------------------------
    def _link_points_from_frames(self, frames1, frames2, x1, x2):
        """Sample points along each link from precomputed frames, shape (M, P, 3)."""
        pts = []
        for chain, frames, x in ((self.c1, frames1, x1), (self.c2, frames2, x2)):
            base_p = dq_to_rt(np.broadcast_to(chain.base, x.shape))[1]
            origins = [base_p] + [dq_to_rt(f)[1] for f in frames] + [dq_to_rt(x)[1]]
            for k in range(len(origins) - 1):
                a, b = origins[k], origins[k + 1]
                for s in np.linspace(0.0, 1.0, self.n_points_per_link + 2)[1:-1]:
                    pts.append(a + s * (b - a))
        return np.stack(pts, axis=1)

    def _min_clearance(self, pts):
        d = np.linalg.norm(pts[:, :, None, :] - self.obstacles[None, None, :, :], axis=-1)
        d = d - self.obstacle_radii[None, None, :]
        return d.min(axis=(1, 2))[:, None]

    def min_clearance(self, q1, q2):
        x1, f1 = self.c1.fk_with_frames(q1)
        x2, f2 = self.c2.fk_with_frames(q2)
        return self._min_clearance(self._link_points_from_frames(f1, f2, x1, x2))

    @staticmethod
    def _rotated_z(xa):
        """World direction of the object's z axis (reference line) for a DQ."""
        r = xa[..., :4]
        z = np.zeros(r.shape[:-1] + (3,))
        z[..., 2] = 1.0
        q = r / np.linalg.norm(r, axis=-1, keepdims=True)
        w = q[..., :1]
        v = q[..., 1:]
        t = 2.0 * np.cross(v, z)
        return z + w * t + np.cross(v, t)

    def tilt_angle_deg(self, xa):
        """Angle between the current and the initial object z axis, in degrees."""
        cur = self._rotated_z(xa)
        cos = np.clip(np.sum(cur * self.ref_z, axis=-1), -1.0, 1.0)
        return np.rad2deg(np.arccos(cos))

    # ------------------------------------------------------------------
    def rollout(self, U: np.ndarray, q0: np.ndarray | None = None, stabilize: bool = True, max_stab: float = 0.05):
        """Roll out ``U`` (M, N, 12) with per-step projection and diagnostics.

        ``stabilize`` adds a discrete Newton correction on the relative-pose
        constraint after each high-level step.  It stands in for the 125 Hz
        low-level loop of Eqs. (50)-(51); without it the open-loop plan drifts
        by O(N T_h^2), which the paper corrects at the low level.
        """
        M, N, _ = U.shape
        q0 = self.q_home if q0 is None else np.asarray(q0, dtype=float)
        q1 = np.broadcast_to(q0[:6], (M, 6)).copy()
        q2 = np.broadcast_to(q0[6:], (M, 6)).copy()
        stage = np.zeros((M, 1))
        min_clear = np.full((M, 1), np.inf)
        tilt_max = np.zeros((M, 1))
        for k in range(N):
            J = relative_jacobian(self.c1, self.c2, q1, q2)
            q1, q2, _, _ = project_step(
                J,
                U[:, k, :6],
                U[:, k, 6:],
                q1,
                q2,
                self.dq_min[:6],
                self.dq_max[:6],
                self.dq_min[6:],
                self.dq_max[6:],
                self.q_min[:6],
                self.q_max[:6],
                self.q_min[6:],
                self.q_max[6:],
                self.dt,
            )
            if stabilize:
                x1s, x2s = self.c1.fk(q1), self.c2.fk(q2)
                xr = relative_pose(x1s, x2s)
                err = self.xr_0 - xr
                dq = np.einsum("mij,mj->mi", np.linalg.pinv(J, rcond=1e-10), err)
                dq = np.clip(dq, -max_stab, max_stab)
                q1 = np.clip(q1 + dq[:, :6], self.q_min[:6], self.q_max[:6])
                q2 = np.clip(q2 + dq[:, 6:], self.q_min[6:], self.q_max[6:])
            x1, f1 = self.c1.fk_with_frames(q1)
            x2, f2 = self.c2.fk_with_frames(q2)
            xa = absolute_pose(x1, x2)
            clear = self._min_clearance(self._link_points_from_frames(f1, f2, x1, x2))
            min_clear = np.minimum(min_clear, clear)
            tilt = self.tilt_angle_deg(xa)[:, None]
            tilt_max = np.maximum(tilt_max, tilt)
            if self.use_singularity:
                stage += singularity_cost(J, self.cfg)
            stage += collision_cost(clear, self.safety_margin, self.cfg.p_ec)
            stage += tilt_cost(tilt, self.cfg)
        x1 = self.c1.fk(q1)
        x2 = self.c2.fk(q2)
        xa = absolute_pose(x1, x2)
        pos = dq_to_rt(xa)[1]
        goal = terminal_goal_cost(xa, self.xa_d, pos, self.pos_d, self.cfg)
        dq_norm = np.sum(np.abs(np.concatenate([q1, q2], axis=1) - self.q_home), axis=1, keepdims=True)
        stay = stagnation_cost(goal, dq_norm, self.cfg)
        total = stage + goal + stay
        xr = relative_pose(x1, x2)
        drift = np.linalg.norm(xr - self.xr_0, axis=1, keepdims=True)
        return {
            "cost": total,
            "goal": goal,
            "stage": stage,
            "min_clearance": min_clear,
            "tilt_max": tilt_max,
            "pos_error": np.linalg.norm(pos - self.pos_d, axis=1, keepdims=True),
            "rel_drift": drift,
            "q1": q1,
            "q2": q2,
            "xa": xa,
        }

    def _pose_jacobian_fd(self, q: np.ndarray, h: float = 1e-6) -> np.ndarray:
        """Finite-difference Jacobian of the absolute pose (8 x 12) at one q."""
        q = np.asarray(q, dtype=float)
        xa0 = absolute_pose(self.c1.fk(q[None, :6]), self.c2.fk(q[None, 6:]))[0]
        J = np.zeros((8, 12))
        for j in range(12):
            qp = q.copy()
            qp[j] += h
            xp = absolute_pose(self.c1.fk(qp[None, :6]), self.c2.fk(qp[None, 6:]))[0]
            J[:, j] = (xp - xa0) / h
        return J

    def auxiliary_plan(self, gain: float = 0.15, q0: np.ndarray | None = None) -> np.ndarray:
        """Closed-loop CDTS auxiliary rollout (Eqs. 44-46), one sample.

        Used as the MPPI warm start (the paper's "previous cycle optimum"
        when the controller is already regulating near its operating point)
        and as the E2 reference.  Not a paper equation by itself.
        """
        q0 = self.q_home if q0 is None else np.asarray(q0, dtype=float)
        q1 = q0[None, :6].copy()
        q2 = q0[None, 6:].copy()
        U = np.zeros((self.horizon, 12))
        for k in range(self.horizon):
            x1 = self.c1.fk(q1)
            x2 = self.c2.fk(q2)
            xa = absolute_pose(x1, x2)
            J = self._pose_jacobian_fd(np.concatenate([q1[0], q2[0]]))
            Jr = relative_jacobian(self.c1, self.c2, q1, q2)[0]
            N = np.eye(12) - np.linalg.pinv(Jr, rcond=1e-10) @ Jr
            # Priority-consistent step: dq = N (Ja N)^+ e.  The paper's
            # Eq. (45) uses N Ja^+ e, which preserves the equality exactly but
            # only partially realises the absolute task (see E2 report).
            JN = J @ N
            step = N @ (np.linalg.pinv(JN, rcond=1e-4) @ (self.xa_d - xa[0])) * gain
            # Cap the per-step joint motion: the Newton step can be large near
            # this poorly conditioned grasp and would overshoot the target.
            step = np.clip(step, -0.05, 0.05)
            v = step / self.dt
            v = np.clip(v, -self.dq_max, self.dq_max)
            U[k] = v
            q1, q2, _, _ = project_step(
                Jr[None], v[None, :6], v[None, 6:], q1, q2,
                self.dq_min[:6], self.dq_max[:6], self.dq_min[6:], self.dq_max[6:],
                self.q_min[:6], self.q_max[:6], self.q_min[6:], self.q_max[6:], self.dt,
            )
            # same discrete constraint stabilisation as ``rollout``
            x1s, x2s = self.c1.fk(q1), self.c2.fk(q2)
            err_r = self.xr_0 - relative_pose(x1s, x2s)
            dq = np.einsum("mij,mj->mi", np.linalg.pinv(Jr[None], rcond=1e-10), err_r)
            dq = np.clip(dq, -0.05, 0.05)
            q1 = np.clip(q1 + dq[:, :6], self.q_min[:6], self.q_max[:6])
            q2 = np.clip(q2 + dq[:, 6:], self.q_min[6:], self.q_max[6:])
        return U

    def success(self, diag) -> np.ndarray:
        return (
            (diag["pos_error"] < 0.02)
            & (diag["min_clearance"] > self.safety_margin)
            & (diag["tilt_max"] <= self.cfg.tilt_max_deg)
            & (diag["rel_drift"] < 1e-3)
        )[:, 0]

    def nominal_trajectory(self):
        """Straight-line joint interpolation used only for initialisation/plots."""
        return np.zeros((self.horizon, 12))


def run_closed_loop(
    task: DualArmTask,
    rng: np.random.Generator,
    control_steps: int = 20,
    samples: int = 60,
    inner_iterations: int = 8,
    std: float = 0.3,
    lam: float = 0.5,
    update_gain: float = 0.3,
    switch: bool = True,
    eta: float = 0.1,
) -> dict:
    """Receding-horizon MPPI with the paper's auxiliary/L switching.

    ``switch=False`` runs sampling control only (the E1 baseline); ``True``
    adds Eqs. (44)-(49): the auxiliary CDTS plan is evaluated with the same
    cost, ``L`` integrates ``C_t / C_s - eta``, and the executed first control
    is taken from the auxiliary plan whenever ``L < 0``.
    """
    from .sampler import adaptive_weights, colored, weighted_noise
    from .switch import UnexploredIndicator

    q = task.q_home.copy()
    u_seq = np.zeros((task.horizon, 12))
    ind = UnexploredIndicator(eta=eta, l_min=-0.05, l_max=0.4, dt=task.dt)
    hist = {"pos": [], "clear": [], "tilt": [], "drift": [], "L": [], "used_aux": [],
            "C_t": [], "C_s": [], "ratio": []}
    for _ in range(control_steps):
        for _ in range(inner_iterations):
            eps = colored(
                rng, samples, task.horizon, 12,
                std=std, gamma=2.0, max_abs=task.dt * task.ddq_max[0],
            )
            diag = task.rollout(u_seq[None] + eps, q0=q)
            w, lam = adaptive_weights(diag["cost"], lam, (22, 30))
            u_seq = np.clip(u_seq + update_gain * weighted_noise(eps, w), -task.dq_max, task.dq_max)

        u_exec = u_seq
        used_aux = False
        if switch:
            c_s = float(task.rollout(u_seq[None], q0=q)["cost"][0, 0])
            u_aux = task.auxiliary_plan(q0=q)
            c_t = float(task.rollout(u_aux[None], q0=q)["cost"][0, 0])
            ratio = c_t / max(c_s, 1e-9)
            hist["C_t"].append(c_t)
            hist["C_s"].append(c_s)
            hist["ratio"].append(ratio)
            ind.update(ratio)
            if not ind.use_sampling:
                u_exec = u_aux
                used_aux = True

        step = task.rollout(u_exec[None, :1], q0=q)
        hist["pos"].append(float(step["pos_error"][0, 0]))
        hist["clear"].append(float(step["min_clearance"][0, 0]))
        hist["tilt"].append(float(step["tilt_max"][0, 0]))
        hist["drift"].append(float(step["rel_drift"][0, 0]))
        hist["L"].append(float(ind.value))
        hist["used_aux"].append(used_aux)
        q = np.concatenate([step["q1"][0], step["q2"][0]])
        u_seq = np.vstack([u_seq[1:], u_seq[-1:]])
    return {
        "q": q,
        "history": hist,
        "final_pos_error": hist["pos"][-1],
        "min_clearance": min(hist["clear"]),
        "max_tilt": max(hist["tilt"]),
        "max_drift": max(hist["drift"]),
        "aux_fraction": float(np.mean(hist["used_aux"])),
    }
