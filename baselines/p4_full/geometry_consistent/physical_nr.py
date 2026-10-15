"""Paper pseudoinverse NR on physical closed-chain constraints, qualification only.

This NumPy reference is an independently reconstructed implementation, not the
author's KDL runtime or a speed baseline.  Physical constants come from the
already qualified R1 elementary-transform oracles; no solver result is used as
ground truth.  World base yaws and grasps retain their source literals.
"""
from __future__ import annotations

import math
import time
from typing import Sequence

import numpy as np

from baselines.p4_full.abb_independent_oracle import abb_fk_and_jacobian
from baselines.p4_full.analyze_comau_native_qualification import (
    geometry as comau_geometry, serial_fk as comau_fk,
)


FLIP = np.diag([-1., -1., 1., 1.])
AUTHOR_PI = 3.1416


def skew(v):
    x, y, z = np.asarray(v, dtype=float)
    return np.array([[0., -z, y], [z, 0., -x], [-y, x, 0.]])


def log_so3(r):
    """Principal log; preserve a real derivative-chart ambiguity near pi."""
    axial = np.array([r[2, 1]-r[1, 2], r[0, 2]-r[2, 0],
                      r[1, 0]-r[0, 1]])/2
    s = float(np.linalg.norm(axial))
    c = float((np.trace(r)-1)/2)
    theta = math.atan2(s, c)
    if math.pi-theta < 1e-7:
        raise ValueError('SO3_PRINCIPAL_CHART_NEAR_PI')
    return axial*(1+theta**2/6) if theta < 1e-7 else axial*(theta/s)


def left_jacobian_inverse(phi):
    theta = float(np.linalg.norm(phi))
    k = skew(phi)
    coef = (1/12 + theta**2/720) if theta < 1e-4 else (
        1/theta**2-(1+math.cos(theta))/(2*theta*math.sin(theta)))
    return np.eye(3)-k/2+coef*(k@k)


def model_geometry(env):
    if env in ('II', 'III'):
        d, rod = (900., 300.) if env == 'II' else (1200., 500.)
        # II/III inputs are verified against R1 metadata by the run harness.
        grasp = np.eye(4); grasp[0, 3] = rod
        return {'arms': 2, 'bases': [[-d/2, 0., 0.], [d/2, 0., AUTHOR_PI]],
                'grasps': [grasp], 'position_unit': 'mm'}
    if env in ('IV', 'V', 'VI'):
        g = comau_geometry({'IV': 4, 'V': 5, 'VI': 6}[env])
        return {'arms': 3 if env == 'VI' else 2,
                'bases': g['bases_mm_rad'], 'grasps': g['grasps'],
                'position_unit': 'mm'}
    if env == 'I':
        return {'arms': 0, 'position_unit': 'source_link_length_unit'}
    raise ValueError('Unknown source environment')


def arm_fk_jac(q, env, arm):
    if env in ('II', 'III'):
        return abb_fk_and_jacobian(q, model_geometry(env)['bases'][arm-1])
    pose, stages = comau_fk(q, {'IV': 4, 'V': 5, 'VI': 6}[env], arm, True)
    axes = (np.array([0., 0., 1.]), np.array([0., 1., 0.]),
            np.array([0., 1., 0.]), np.array([1., 0., 0.]),
            np.array([0., 1., 0.]), np.array([1., 0., 0.]))
    world_axes = [t[:3, :3]@a for t, a in zip(stages, axes)]
    jp = np.column_stack([np.cross(a, pose[:3, 3]-t[:3, 3])
                          for a, t in zip(world_axes, stages)])
    return pose, np.vstack((jp, np.column_stack(world_axes)))


def source_limits(env):
    if env == 'I':
        bound = AUTHOR_PI*179.9/180
        return np.array([[-bound, bound]]*19+[[0, 2*AUTHOR_PI]])
    if env in ('II', 'III'):
        degrees = [[-165, 165], [-110, 110], [-110, 70],
                   [-160, 160], [-120, 120], [-400, 400]]
    else:
        degrees = [[-180, 180], [-60, 125], [-90, 75],
                   [-2700, 2700], [-120, 120], [-400, 400]]
    return np.tile(np.array(degrees)*AUTHOR_PI/180,
                   (model_geometry(env)['arms'], 1))


def planar_vector_jacobian(q):
    """Endpoint C, independently expanded cumulative-angle derivative."""
    angles = np.cumsum(q[:19])
    s, c = np.sin(angles), np.cos(angles)
    phi = float(np.sum(q[:19])+AUTHOR_PI-q[19])
    g = np.array([np.sum(c)-7., np.sum(s)-4.,
                  math.atan2(math.sin(phi), math.cos(phi))])
    j = np.zeros((3, 20))
    j[0, :19] = -np.cumsum(s[::-1])[::-1]
    j[1, :19] = np.cumsum(c[::-1])[::-1]
    j[2, :19] = 1.; j[2, 19] = -1.
    return g, j


def closure_vector_jacobian(q: Sequence[float], env):
    q = np.asarray(q, dtype=float)
    if not np.isfinite(q).all():
        raise ValueError('NONFINITE_CONFIGURATION')
    if env == 'I':
        if q.shape != (20,): raise ValueError('Expected source20R')
        return planar_vector_jacobian(q)
    geometry = model_geometry(env)
    n = 6*geometry['arms']
    if q.shape != (n,): raise ValueError('Wrong number of physical coordinates')
    poses, jacobians = zip(*(arm_fk_jac(q[6*i:6*i+6], env, i+1)
                             for i in range(geometry['arms'])))
    values, blocks = [], []
    for i, grasp in enumerate(geometry['grasps'], 1):
        target = poses[0]@grasp@FLIP
        actual = poses[i]
        e = actual[:3, :3]@target[:3, :3].T
        phi = log_so3(e)
        values.extend(actual[:3, 3]-target[:3, 3]); values.extend(phi)
        j = np.zeros((6, n))
        offset = poses[0][:3, :3]@grasp[:3, 3]
        j[:3, :6] = -jacobians[0][:3]+skew(offset)@jacobians[0][3:]
        j[:3, 6*i:6*i+6] = jacobians[i][:3]
        log_j = left_jacobian_inverse(phi)
        j[3:, :6] = -log_j@e@jacobians[0][3:]
        j[3:, 6*i:6*i+6] = log_j@jacobians[i][3:]
        blocks.append(j)
    return np.array(values), np.vstack(blocks)


def residual_metrics(q, env):
    if env == 'I':
        g, _ = closure_vector_jacobian(q, env)
        return {'translation_max_abs': float(np.max(np.abs(g[:2]))),
                'rotation_matrix_max_abs': max(abs(math.sin(g[2])),
                                              abs(1-math.cos(g[2]))),
                'rotation_angle_max_rad': abs(float(g[2])),
                'position_unit': 'source_link_length_unit'}
    geometry = model_geometry(env)
    poses = [arm_fk_jac(q[6*i:6*i+6], env, i+1)[0]
             for i in range(geometry['arms'])]
    errors = [poses[i+1]-poses[0]@grasp@FLIP
              for i, grasp in enumerate(geometry['grasps'])]
    angles = [np.linalg.norm(log_so3(poses[i+1][:3, :3]@
              (poses[0]@grasp@FLIP)[:3, :3].T))
              for i, grasp in enumerate(geometry['grasps'])]
    return {'translation_max_abs': float(max(np.max(np.abs(e[:3, 3])) for e in errors)),
            'rotation_matrix_max_abs': float(max(np.max(np.abs(e[:3, :3])) for e in errors)),
            'rotation_angle_max_rad': float(max(angles)), 'position_unit': 'mm'}


def periodic_chart(q, env):
    """Numerical angle normalization only, never relax physical joint limits."""
    q = np.asarray(q, dtype=float).copy()
    if env == 'I':
        q[:19] = np.arctan2(np.sin(q[:19]), np.cos(q[:19]))
        q[19] %= 2*math.pi
    else:
        q[:] = np.arctan2(np.sin(q), np.cos(q))
    return q


def project_nr(q_input, env, *, wall_limit_s=120., max_iterations=10000,
               position_gate=1e-5, rotation_gate=1e-5, svd_relative=1e-12):
    """Undamped full-Jacobian Moore-Penrose update; keep every final candidate."""
    started = time.monotonic()
    original = np.asarray(q_input, dtype=float)
    q = original.copy()
    trace = []
    status = 'ITERATION_LIMIT'
    bounds = source_limits(env)
    metrics = None
    try:
        for iteration in range(max_iterations+1):
            if time.monotonic()-started >= wall_limit_s:
                status = 'WALL_LIMIT'; break
            g, j = closure_vector_jacobian(q, env)
            metrics = residual_metrics(q, env)
            trace.append({'iteration': iteration, **metrics})
            if (metrics['translation_max_abs'] <= position_gate
                    and metrics['rotation_matrix_max_abs'] <= rotation_gate):
                q = periodic_chart(q, env)
                metrics = residual_metrics(q, env)
                legal = np.all((bounds[:, 0] <= q) & (q <= bounds[:, 1]))
                post_closed = (metrics['translation_max_abs'] <= position_gate
                               and metrics['rotation_matrix_max_abs'] <= rotation_gate)
                status = ('POST_CHART_RESIDUAL_REJECTED' if not post_closed else
                          'CONVERGED' if legal else 'CLOSED_BUT_JOINT_LIMIT_REJECTED')
                break
            if iteration == max_iterations: break
            u, s, vh = np.linalg.svd(j, full_matrices=False)
            inv = np.zeros_like(s)
            mask = s > s[0]*svd_relative
            inv[mask] = 1/s[mask]
            q -= vh.T@(inv*(u.T@g))
            if not np.isfinite(q).all():
                status = 'NONFINITE'; break
    except (ValueError, np.linalg.LinAlgError) as error:
        status = str(error)
    return {'status': status, 'input_q_rad': original.tolist(),
            'candidate_q_rad': q.tolist() if np.isfinite(q).all() else None,
            'metrics': metrics, 'trace': trace, 'wall_s': time.monotonic()-started,
            'method': 'Paper full-Jacobian pseudoinverse NR, NumPy reference',
            'collision_checked': False}
