"""Closed-form diagnostic replay of existing ABB native outputs, no solver.

No new joint sample, FK evaluator, Jacobian evaluator, inverse solver, native
binary or planner is called.  Predicted error vectors use saved transforms,
source geometry and elementary angle identities only.  Counterfactual phase
contributions are explicitly distinguished from measured native outputs.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np

REPO = Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
DATA = REPO/'results/p4_full/20261014T1528_R1_ABB01'
OUT = Path(__file__).resolve().parent

def rz(angle):
    c,s = math.cos(angle),math.sin(angle)
    return np.array([[c,-s,0.],[s,c,0.],[0.,0.,1.]])

def rx(angle):
    c,s = math.cos(angle),math.sin(angle)
    return np.array([[1.,0.,0.],[0.,c,-s],[0.,s,c]])

def pose(rotation=np.eye(3), position=np.zeros(3)):
    result=np.eye(4);result[:3,:3]=rotation;result[:3,3]=position
    return result

def inv_pose(t):
    return pose(t[:3,:3].T,-t[:3,:3].T@t[:3,3])

def maximum(values):
    return max(values) if values else None

def main():
    input_paths=[DATA/f'{e}_{s}.json' for e in ('II','III') for s in ('native','independent')]
    hashes={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths}
    delta=(3.1416-math.pi)/2.
    psi_error=2.*delta
    facing=pose(np.diag([-1.,-1.,1.]))
    results={}
    for env in ('II','III'):
        native=json.loads((DATA/f'{env}_native.json').read_text())
        oracle=json.loads((DATA/f'{env}_independent.json').read_text())
        d,l=native['D_mm'],native['L_mm']
        base={1:np.array(native['base1']),2:np.array(native['base2'])}
        bases={r:pose(rz(b[2]),np.r_[b[:2],0.]) for r,b in base.items()}
        rod=pose(position=np.array([l,0.,0.]))
        target_chain=pose(position=np.array([d,0.,0.]))
        ik=[];nr=[]
        for row_index,row in enumerate(native['rows']):
            if row['kind']=='ik' and row['success']:
                target=np.array(row['target']);actual=np.array(row['T_out'])
                q=np.array(row['solution']);r=row['robot'];branch=row['branch']
                target_wrist_world=target[:3,3]-132.*target[:3,0]
                target_wrist_local=rz(base[r][2]).T@(target_wrist_world-np.r_[base[r][:2],0.])
                rho=math.hypot(target_wrist_local[0],target_wrist_local[1])
                z=target_wrist_local[2]-290.
                radial_sign=1. if branch<4 else -1.
                q2_error=radial_sign*delta
                ideal_radial=radial_sign*rho
                actual_radial=ideal_radial*math.cos(q2_error)+z*math.sin(q2_error)
                actual_z=z*math.cos(q2_error)-ideal_radial*math.sin(q2_error)
                predicted_wrist_local=np.array([actual_radial*math.cos(q[0]),actual_radial*math.sin(q[0]),290.+actual_z])
                predicted_wrist_world=rz(base[r][2])@predicted_wrist_local+np.r_[base[r][:2],0.]
                predicted_error=predicted_wrist_world-target_wrist_world+132.*(actual[:3,0]-target[:3,0])
                observed_error=actual[:3,3]-target[:3,3]
                phi=math.atan2(target_wrist_local[1],target_wrist_local[0])
                shoulder_angle_error=math.atan2(math.sin(q[0]-phi-(0 if branch<4 else math.pi)),
                                               math.cos(q[0]-phi-(0 if branch<4 else math.pi)))
                ik.append({'row_index':row_index,'index':row['index'],'robot':r,'branch':branch,
                           'q2_error_from_PI_over_2_rad':q2_error,
                           'q1_error_from_PI_shoulder_flip_rad':shoulder_angle_error,
                           'target_wrist_rho_mm':rho,'target_wrist_height_above_shoulder_mm':z,
                           'observed_translation_error_mm':observed_error.tolist(),
                           'predicted_translation_error_mm':predicted_error.tolist(),
                           'prediction_max_component_residual_mm':float(np.max(np.abs(observed_error-predicted_error))),
                           'observed_translation_max_abs_mm':float(np.max(np.abs(observed_error))),
                           'observed_translation_l2_mm':float(np.linalg.norm(observed_error)),
                           'orientation_max_abs_error':float(np.max(np.abs(actual[:3,:3]-target[:3,:3])))})
            elif row['kind']=='nr' and row['success']:
                q=np.array(row['solution']);q0=np.array(row['input']);t1=np.array(row['T1']);t2=np.array(row['T2']);chain=np.array(row['T_chain'])
                a2=inv_pose(bases[2])@t2
                physical_left=t1@rod@facing
                predicted_left=bases[1]@chain@facing@a2
                ideal_chain_left=bases[1]@target_chain@facing@a2
                measured_error=physical_left[:3,3]-t2[:3,3]
                base_only_error=ideal_chain_left[:3,3]-t2[:3,3]
                chain_contribution=predicted_left[:3,3]-ideal_chain_left[:3,3]
                measured_rotation_error=physical_left[:3,:3]-t2[:3,:3]
                measured_chain_error=chain[:3,3]-target_chain[:3,3]
                # The adjacent, coaxial q1[5]/q2[5] chain columns are equal.
                # Minimum-norm NR increments preserve their difference.
                initial_difference=q0[5]-q0[11]
                measured_difference=q[5]-q[11]
                inferred_prequantization_q1_6=q[11]+initial_difference
                hypothetical_unquantized_left=t1.copy()
                hypothetical_unquantized_left[:3,:3]=t1[:3,:3]@rx(inferred_prequantization_q1_6-q[5])
                hypothetical_unquantized_chain=inv_pose(bases[1])@hypothetical_unquantized_left@rod@facing@inv_pose(a2)@facing
                nr.append({'row_index':row_index,'index':row['index'],
                           'physical_translation_error_mm':measured_error.tolist(),
                           'physical_translation_max_abs_mm':float(np.max(np.abs(measured_error))),
                           'physical_rotation_matrix_max_abs_error':float(np.max(np.abs(measured_rotation_error))),
                           'base_approximate_pi_contribution_mm':base_only_error.tolist(),
                           'native_chain_residual_contribution_mm':chain_contribution.tolist(),
                           'combined_prediction_max_component_residual_mm':float(np.max(np.abs(measured_error-base_only_error-chain_contribution))),
                           'combined_prediction_rotation_max_abs_residual':float(np.max(np.abs(physical_left[:3,:3]-predicted_left[:3,:3]))),
                           'native_chain_target_translation_error_mm':measured_chain_error.tolist(),
                           'native_chain_target_translation_max_abs_mm':float(np.max(np.abs(measured_chain_error))),
                           'native_chain_target_rotation_matrix_max_abs_error':float(np.max(np.abs(chain[:3,:3]-np.eye(3)))),
                           'q1_6_recorded_rad':float(q[5]),'q2_6_recorded_rad':float(q[11]),
                           'coaxial_joint_difference_change_rad':float(measured_difference-initial_difference),
                           'inferred_prequantization_q1_6_rad':float(inferred_prequantization_q1_6),
                           'source_quantization_threshold_rad':1e-4,
                           'hypothetical_unquantized_chain_target_translation_max_abs_mm':float(np.max(np.abs(hypothetical_unquantized_chain[:3,3]-target_chain[:3,3]))),
                           'hypothetical_unquantized_chain_target_rotation_matrix_max_abs_error':float(np.max(np.abs(hypothetical_unquantized_chain[:3,:3]-np.eye(3)))),
                           'hypothesis_scope':'Saved matrices and coaxial-update invariant only. Presnap solver vector was not logged; no solver rerun or replacement output was generated.'})
        jac=[e for e in oracle['evidence'] if e['kind']=='jacobian_fixture']
        fk=[e for e in oracle['evidence'] if e['kind']=='fk']
        results[env]={'native_accepted_ik_count':len(ik),'ik_rows':ik,'nr_rows':nr,
                      'maximum_ik_prediction_residual_mm':maximum([r['prediction_max_component_residual_mm'] for r in ik]),
                      'maximum_ik_orientation_error':maximum([r['orientation_max_abs_error'] for r in ik]),
                      'ik_error_range_mm':[min(r['observed_translation_max_abs_mm'] for r in ik),max(r['observed_translation_max_abs_mm'] for r in ik)],
                      'maximum_nr_combined_prediction_residual_mm':maximum([r['combined_prediction_max_component_residual_mm'] for r in nr]),
                      'maximum_nr_combined_rotation_prediction_residual':maximum([r['combined_prediction_rotation_max_abs_residual'] for r in nr]),
                      'nr_physical_error_range_mm':[min(r['physical_translation_max_abs_mm'] for r in nr),max(r['physical_translation_max_abs_mm'] for r in nr)],
                      'nr_chain_translation_error_range_mm':[min(r['native_chain_target_translation_max_abs_mm'] for r in nr),max(r['native_chain_target_translation_max_abs_mm'] for r in nr)],
                      'snap_candidates':[r for r in nr if abs(r['coaxial_joint_difference_change_rad'])>1e-10],
                      'native_fk_count':len(fk),'maximum_independent_fk_translation_error_mm':max(e['errors']['translation_max_abs_mm'] for e in fk),
                      'native_and_independent_jacobian_ranks':{e['name']:{k:e[k]['rank'] for k in ['independent_analytic','native_finite_difference','independent_finite_difference']} for e in jac},
                      'frozen_check_counts':{'total':oracle['checks_total'],'passed':oracle['checks_passed'],'failed':oracle['checks_failed']}}
    after={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths}
    result={'schema':'P4_ABB_SAVED_FAILURE_CLOSED_FORM_REPLAY_V1',
            'scope':'Derived analysis only: all native accepted outputs remain failed under the frozen qualification. No new configuration, solver, FK program, constant change, projection or planning executed.',
            'native_run_id':'20261014T1528_R1_ABB01','input_sha256':hashes,'input_bytes_unchanged':hashes==after,
            'analysis_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_PI_literal':3.1416,'mathematical_pi':math.pi,'PI_literal_error_rad':psi_error,
            'PI_over_2_error_rad':delta,'geometry_unchanged_mm':{'b_plus_l1':290,'l2':270,'l3a':70,'l3b_plus_l4':302,'apc_l5_plus_lee':132,'kdl_l5_plus_lee':132},
            'equations':{'ik_wrist_prediction':'r_actual = r_branch cos(eta) + z sin(eta); z_actual=z cos(eta)-r_branch sin(eta), eta=sign_branch*(3.1416-pi)/2; yaw uses saved native q1.',
                         'physical_chain_relation':'T_left = B1 C_native S inv(B2) T_right, S=diag(-1,-1,1,1); base-only and chain-residual contributions add in position.',
                         'quantization_invariant':'before source output quantization, coaxial equal Jacobian columns preserve q1[5]-q2[5]; inferred presnap is labeled unobserved.'},
            'environments':results}
    with (OUT/'derived_failures.json').open('x',encoding='utf-8') as handle:json.dump(result,handle,ensure_ascii=False,indent=2,allow_nan=False)
    print(json.dumps({'input_bytes_unchanged':result['input_bytes_unchanged'],'PI_over_2_error_rad':delta,
                      'environments':{e:{k:v for k,v in values.items() if k.startswith('maximum_') or k.endswith('_range_mm') or k=='native_accepted_ik_count'} for e,values in results.items()}},indent=2))

if __name__=='__main__':main()
