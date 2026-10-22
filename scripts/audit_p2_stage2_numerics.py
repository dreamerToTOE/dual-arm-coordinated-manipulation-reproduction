#!/usr/bin/env python3
"""Fixed local mathematics after Gate D timeout, never an ODE trajectory.

Central finite differences of the 42-dimensional right-coordinate vector field
and isolated one-step maps. Synthetic equilibria are diagnostic copies only;
no live plant, estimator, command stream, controller or benchmark is reset.
No new PASS/FAIL numerical-stability acceptance rule is defined here.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import scipy
from baselines.p2_pose_force.mechanics import (STATE_NAMES, initial_state,
    physics_from_protocol, mechanics, equilibrium_residual, state_rate,
    midpoint_step)

EPS = 1e-6
STEP_VALUES = (1/3000, 1/6000)
EULER_HEARTBEAT = .004
FROZEN_PROTOCOL_SHA = '423f58ca7cfe13861586bb486dcfd6d19c5e3d82b69e40c3d403c90d7c871df3'
GEOMETRY_SHA = '47557da9189d8525e8a1ec343b5a4afc929405071d4e5de7d562091cc04a629a'
SOURCES = ('scripts/audit_p2_stage2_numerics.py',
           'reports/P2_STAGE2_NUMERICAL_DIAGNOSIS.md',
           'baselines/p2_pose_force/mechanics.py',
           'baselines/p2_pose_force/contact_geometry.py',
           'configs/p2_closed_loop_protocol_v1.json')
MODES = ('pivot', 'pivot')
U_ZERO = (np.zeros(6), np.zeros(6))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                              allow_nan=False)+'\n')


def eig_json(values):
    ordered = sorted(values, key=lambda z: (float(z.real), float(z.imag)))
    return [{'real': float(z.real), 'imag': float(z.imag),
             'modulus': float(abs(z))} for z in ordered]


def spectrum(matrix, label_tolerance):
    values = np.linalg.eigvals(matrix)
    # This tolerance is an existing algebraic-label tolerance, not an added
    # scientific acceptance criterion. Preserve strict >1 counts separately.
    neutral = np.abs(values-1) <= label_tolerance
    outside = np.abs(values) > 1
    separated = (np.abs(values) > 1+label_tolerance) & ~neutral
    return {'eigenvalues': eig_json(values),
            'spectral_radius': float(np.max(np.abs(values))),
            'strict_outside_unit_circle_count': int(np.sum(outside)),
            'neutral_near_one_label_count': int(np.sum(neutral)),
            'outside_unit_circle_separated_from_neutral_count': int(np.sum(separated)),
            'separated_outside_eigenvalues': eig_json(values[separated]),
            'neutral_label_tolerance_from_frozen_algebra_atol': label_tolerance,
            'acceptance_decision': None}


def continuous_fd(state, physics):
    out = np.empty((42, 42))
    for i in range(42):
        direction = np.zeros(42); direction[i] = EPS
        plus = state_rate(state.retract(direction), U_ZERO, MODES, physics)
        minus = state_rate(state.retract(-direction), U_ZERO, MODES, physics)
        out[:, i] = (plus-minus)/(2*EPS)
    return out


def map_fd(state, physics, step):
    base = midpoint_step(state, U_ZERO, MODES, physics, step)
    out = np.empty((42, 42))
    for i in range(42):
        direction = np.zeros(42); direction[i] = EPS
        plus = midpoint_step(state.retract(direction), U_ZERO, MODES, physics, step)
        minus = midpoint_step(state.retract(-direction), U_ZERO, MODES, physics, step)
        # Both columns live in the same output tangent at the unperturbed
        # one-step base. This is not a world-translation/Euler-angle difference.
        out[:, i] = (plus.local(base)-minus.local(base))/(2*EPS)
    return out, base


def point_twist_matrix(R_E_in_object, point_in_object):
    columns = []
    for unit in np.eye(6):
        v, w = unit[:3], unit[3:]
        columns.append(np.r_[R_E_in_object.T @ (v+np.cross(w, point_in_object)),
                             R_E_in_object.T @ w])
    return np.column_stack(columns)


def independent_matrices(cfg, state, object_id):
    """Classical rigid-point velocities and forces, no adjoint/Jr reuse.

    D is an exact instantaneous damping map with the original Eq10 grasp-point
    velocity and EE-origin wrench map. K is an undeformed fixed-G reference;
    at preloaded finite deformation it is explicitly NOT an exact tangent K.
    """
    obj = cfg['model']['objects'][object_id]
    m = obj['mass_kg']; x, y, z = obj['dimensions_m']
    inertia = m/12*np.array([y*y+z*z, x*x+z*z, x*x+y*y])
    M = np.diag(np.r_[np.full(3, m), inertia])
    B = np.array(cfg['original_parameters']['B_nominal'])
    Ks = [np.array(cfg['original_parameters']['K_nominal']) for _ in range(2)]
    D = np.diag(np.array(cfg['original_parameters']['B_air']))
    K0 = np.zeros((6, 6))
    Es = (state.E1, np.linalg.inv(state.C) @ state.E2)
    mask = np.array([1, 1, 1, 1, 1, 0])
    for r, (E, G) in enumerate(zip(Es, (state.G1, state.G2))):
        Eo = np.linalg.inv(state.O) @ E
        velocity_at_grasp = point_twist_matrix(Eo[:3, :3], G[:3, 3])
        velocity_at_EE = point_twist_matrix(Eo[:3, :3], Eo[:3, 3])
        D += velocity_at_EE.T @ np.diag(mask*B) @ velocity_at_grasp
        # This reference is exact for D_contact=I, not preloaded finite D.
        undeformed = point_twist_matrix(G[:3, :3], G[:3, 3])
        K0 += undeformed.T @ np.diag(mask*Ks[r]) @ undeformed
    gravity_body = state.O[:3, :3].T @ np.array(cfg['model']['gravity_m_s2'])
    gravity_pose = np.zeros((6, 6))
    gravity_pose[:3, 3:] = np.column_stack([np.cross(gravity_body, unit)
                                           for unit in np.eye(3)])
    A12 = np.block([[np.zeros((6, 6)), np.eye(6)],
                   [-np.linalg.solve(M, K0)+gravity_pose, -np.linalg.solve(M, D)]])
    return M, D, K0, gravity_pose, A12


def fixture(cfg, variant, equilibrium):
    state = initial_state(cfg, variant)
    object_id = 'C' if variant == 'sliding' else 'A'
    phys = physics_from_protocol(cfg, object_id)
    drop = 0.
    if equilibrium:
        # Frozen fixtures place both EE x axes along world +z. Only this local
        # diagnostic copy is shifted; E/G/C stay the original frozen fixture.
        total_vertical_K = sum(K[0] for K in phys.K)
        drop = phys.mass * (-phys.gravity[2]) / total_vertical_K
        state.O[:3, 3] += np.array([0., 0., -drop])
    return state, phys, object_id, drop


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir', required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=False)
    cfg_path = ROOT/'configs/p2_closed_loop_protocol_v1.json'
    cfg = json.loads(cfg_path.read_text())
    if sha(cfg_path) != FROZEN_PROTOCOL_SHA:
        raise ValueError('FROZEN_PROTOCOL_HASH_CHANGED')
    if sha(ROOT/'baselines/p2_pose_force/contact_geometry.py') != GEOMETRY_SHA:
        raise ValueError('FROZEN_GEOMETRY_HASH_CHANGED')
    tolerance = cfg['numerical_qualification']['algebra_atol']
    metadata = {'kind': 'LOCAL_NUMERICAL_RISK_DIAGNOSIS_NO_TRAJECTORY',
        'date': '2026-10-14', 'command': sys.argv,
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_sha256': {p: sha(ROOT/p) for p in SOURCES},
        'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'protocol_sha256': sha(cfg_path), 'fd_step': EPS,
        'fd_step_units': 'per coordinate: m,rad,m/s,rad/s following 42-state order',
        'frozen_reference_Jacobian_atol': cfg['numerical_qualification']['Jacobian_atol'],
        'method': 'central FD42 at fixed points; fixed-prior right output local for one-step map',
        'state_order': list(STATE_NAMES), 'modes': list(MODES),
        'U_EE_body': [u.tolist() for u in U_ZERO],
        'fixtures': ['A_nominal', 'A_analytic_equilibrium', 'C_nominal', 'C_analytic_equilibrium'],
        'midpoint_steps_s': list(STEP_VALUES), 'observer_Euler_risk_delta_s': EULER_HEARTBEAT,
        'no_new_acceptance_rule': True, 'closed_loop_runs': 0,
        'new_ODE_trajectories': 0, 'actual_C_dynamics_gate_run': False,
        'plant_reset': False, 'controller_or_estimator_run': False,
        'corrections_used_before': 1, 'correction_consumed_by_this_audit': False,
        'status': 'RUNNING'}
    dump(out/'metadata.json', metadata)
    (out/'config_snapshot.json').write_bytes(cfg_path.read_bytes())
    started = time.perf_counter(); records = []
    try:
        for variant in ('transport', 'sliding'):
            for equilibrium in (False, True):
                state, phys, object_id, drop = fixture(cfg, variant, equilibrium)
                name = object_id+('_analytic_equilibrium' if equilibrium else '_nominal')
                f0 = state_rate(state, U_ZERO, MODES, phys)
                contact = mechanics(state, U_ZERO, MODES, phys)
                J = continuous_fd(state, phys)
                values = np.linalg.eigvals(J)
                M, D, K0, gravity_pose, A12 = independent_matrices(cfg, state, object_id)
                vv_error = J[6:12, 6:12] + np.linalg.solve(M, D)
                pose_error = J[6:12, :6] - (-np.linalg.solve(M, K0)+gravity_pose)
                record = {'name': name,
                    'fixture_origin': 'fixed mathematical synthesis, not an integrated or measured state',
                    'nominal_is_actual_equilibrium': False if not equilibrium else None,
                    'synthetic_world_drop_m': drop, 'state': state.as_dict(),
                    'physics': {'mass_kg': phys.mass, 'inertia_diag_kg_m2': phys.inertia_diag.tolist(),
                                'K': [k.tolist() for k in phys.K], 'B': phys.B.tolist(),
                                'Ba': phys.Ba.tolist(), 'gravity_world_m_s2': phys.gravity.tolist()},
                    'contact_tau': contact.tau.tolist(), 'elastic_hK': contact.hK.tolist(),
                    'damping_hB': contact.hB.tolist(), 'field_f0': f0.tolist(),
                    'gravity_balance_residual_N_Nm': equilibrium_residual(state, contact, phys).tolist(),
                    'continuous_right_field_Jacobian_42': J.tolist(),
                    'continuous_eigenvalues_per_s': eig_json(values),
                    'minimum_continuous_real_part_per_s': float(np.min(values.real)),
                    'maximum_continuous_modulus_per_s': float(np.max(np.abs(values))),
                    'independent_reference': {'M6': M.tolist(), 'D6_Eq10_EE_wrench_grasp_velocity': D.tolist(),
                        'K6_undeformed_fixed_G_only': K0.tolist(),
                        'gravity_pose_derivative': gravity_pose.tolist(),
                        'A12_undeformed_reference': A12.tolist(),
                        'A12_eigenvalues': eig_json(np.linalg.eigvals(A12)),
                        'Avv_FD_minus_independent_per_row': vv_error.tolist(),
                        'Apose_FD_minus_undeformed_reference_per_row': pose_error.tolist(),
                        'K_comparison_is_exact_reference_at_this_fixture': not equilibrium,
                        'no_new_crosscheck_acceptance_rule': True},
                    'steps': []}
                for h in STEP_VALUES:
                    F, base = map_fd(state, phys, h)
                    polynomial = np.eye(42)+h*J+.5*h*h*(J@J)
                    record['steps'].append({'step_s': h,
                        'isolated_one_step_is_not_a_trajectory': True,
                        'unperturbed_one_step_state': base.as_dict(),
                        'FD_right_step_Jacobian_42': F.tolist(),
                        'FD_step_spectrum': spectrum(F, tolerance),
                        'linear_midpoint_polynomial_spectrum': spectrum(polynomial, tolerance),
                        'fastest_real_branch_lambda_per_s': float(values[np.argmin(values.real)].real),
                        'fastest_real_branch_polynomial_multiplier':
                            eig_json([1+h*values[np.argmin(values.real)]+.5*(h*values[np.argmin(values.real)])**2])[0],
                        'FD_map_minus_linear_polynomial_max_abs': float(np.max(np.abs(F-polynomial))),
                        'polynomial_exact_linearization_only_at_stationary_equilibrium': equilibrium})
                euler = np.eye(42)+EULER_HEARTBEAT*J
                record['observer_full_heartbeat_Euler_without_updates_risk'] = {
                    'delta_s': EULER_HEARTBEAT, 'spectrum': spectrum(euler, tolerance),
                    'actual_IESEKF_or_measurement_updates_not_run': True,
                    'does_not_prove_full_filter_divergence': True}
                records.append(record)
                with (out/'fixtures.jsonl').open('a') as handle:
                    handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False)+'\n')
                print(json.dumps({'fixture': name,
                    'fastest_continuous_real_per_s': record['minimum_continuous_real_part_per_s'],
                    'midpoint_radii': [step['FD_step_spectrum']['spectral_radius'] for step in record['steps']],
                    'nonneutral_outside_counts': [step['FD_step_spectrum']['outside_unit_circle_separated_from_neutral_count'] for step in record['steps']],
                    'classification': 'RISK_DIAGNOSIS_NOT_GATE_RESULT'}), flush=True)
        metadata['status'] = 'COMPLETE_DIAGNOSIS'
    except Exception:
        metadata['status'] = 'ABORTED_DIAGNOSIS'
        dump(out/'termination.json', {'traceback': traceback.format_exc(),
                                     'no_live_plant_or_controller_was_run': True})
    metadata['wall_s'] = time.perf_counter()-started
    metadata['completed_fixtures'] = len(records)
    dump(out/'metadata.json', metadata)
    summary = {'status': metadata['status'], 'completed_fixtures': len(records),
        'closed_loop_runs': 0, 'new_ODE_trajectories': 0,
        'no_new_acceptance_rule': True, 'dynamics_gate_reexecuted': False,
        'actual_C_failure_claim': False, 'full_filter_divergence_claim': False,
        'wall_s': metadata['wall_s'],
        'fixtures': [{'name': r['name'],
            'fastest_continuous_real_per_s': r['minimum_continuous_real_part_per_s'],
            'step_spectral_radii': [s['FD_step_spectrum']['spectral_radius'] for s in r['steps']],
            'step_nonneutral_outside_counts': [s['FD_step_spectrum']['outside_unit_circle_separated_from_neutral_count'] for s in r['steps']]}
            for r in records]}
    dump(out/'summary.json', summary)
    dump(out/'artifact_sha256.json', {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    print(json.dumps(summary), flush=True)
    return 0 if metadata['status']=='COMPLETE_DIAGNOSIS' else 2


if __name__=='__main__':
    sys.exit(main())
