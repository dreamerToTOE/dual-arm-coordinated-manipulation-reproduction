#!/usr/bin/env python3
"""Read-only saved-prefix audit, preservation check and NOT_EXECUTED ledger.

No plant/observer/controller import; no scientific trial is launched here.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-dir',required=True);ap.add_argument('--output-dir',required=True)
    a=ap.parse_args();run=Path(a.run_dir);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=False)
    meta=json.loads((run/'metadata.json').read_text());summary=json.loads((run/'summary.json').read_text())
    termination=json.loads((run/'termination.json').read_text());index=json.loads((run/'artifact_sha256.json').read_text())
    checks={};checks['all_original_run_hashes']=all(sha(run/p)==s for p,s in index.items())
    checks['science_source_hashes_match']=all(sha(ROOT/p)==s for p,s in meta['source_sha256'].items())
    checks['source_commit_bytes_match']=all(hashlib.sha256(subprocess.check_output(['git','show',meta['source_commit']+':'+p],cwd=ROOT)).hexdigest()==s for p,s in meta['source_sha256'].items())
    cfg=json.loads((run/'config_snapshot.json').read_text())
    checks['protocol_unchanged']=sha(ROOT/'configs/p2_closed_loop_protocol_v1.json')==sha(run/'config_snapshot.json')==meta['protocol_sha256']=='423f58ca7cfe13861586bb486dcfd6d19c5e3d82b69e40c3d403c90d7c871df3'
    checks['accepted_geometry_unchanged']=sha(ROOT/cfg['contact_geometry']['source'])==cfg['contact_geometry']['source_sha256']
    manifest=json.loads((ROOT/'results/20261013_P2_original_audit/preservation_manifest.json').read_text())
    bad=[p for p,s in manifest['protected_files_sha256'].items() if not (ROOT/p).is_file() or sha(ROOT/p)!=s]
    old=ROOT.parent/'dual-arm-coordinated-manipulation-p2'
    old_bad=[p for p,s in manifest['old_P2_untracked_sha256'].items() if not (old/p).is_file() or sha(old/p)!=s]
    p4=ROOT.parent/'dual-arm-coordinated-manipulation-p4-three-methods'
    checks['protected_baseline_files']=not bad;checks['old_P2_untracked_preserved']=not old_bad
    checks['P4_worktree_HEAD']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=p4,text=True).strip()==manifest['base_commit']
    checks['P4_worktree_clean']=not subprocess.check_output(['git','status','--porcelain'],cwd=p4,text=True).strip()
    prior=[p for p in subprocess.check_output(['git','ls-tree','-r','--name-only','834bcc372717a3b4ffbd0bd6ef7262b3b58237bf'],cwd=ROOT,text=True).splitlines()
           if p.startswith(('results/20261013_P2','results/20261014_P2_contact','reports/P2_','configs/p2_','baselines/p2_pose_force/contact_geometry'))]
    prior_bad=[p for p in prior if not (ROOT/p).is_file() or (ROOT/p).read_bytes()!=subprocess.check_output(['git','show','834bcc372717a3b4ffbd0bd6ef7262b3b58237bf:'+p],cwd=ROOT)]
    checks['prior_P2_science_artifacts_preserved']=not prior_bad
    rows=[json.loads(line) for line in gzip.open(run/'transport.jsonl.gz','rt')]
    t=np.array([r['time_s'] for r in rows]);tau=np.array([r['tau'] for r in rows])
    velocity=np.array([r['state']['V'] for r in rows]);poses=np.array([r['state']['O'] for r in rows])
    raw=np.array([r['hK_N_Nm'] for r in rows])+np.array([r['hB_N_Nm'] for r in rows]);internal=np.array([r['internal_N_Nm'] for r in rows])
    checks['saved_timestamps_250Hz']=len(t)>1 and bool(np.max(np.abs(np.diff(t)-.004))<1e-12)
    checks['finite_logged_state_force']=all(np.isfinite(x).all() for x in (t,tau,velocity,poses,raw,internal))
    checks['logged_SE3_valid']=bool(max(np.max(np.abs(O[:3,:3].T@O[:3,:3]-np.eye(3))) for O in poses)<1e-10 and max(abs(np.linalg.det(O[:3,:3])-1) for O in poses)<1e-10)
    checks['EE_locked_all_saved_samples']=all(all(r['state'][e]==rows[0]['state'][e] for e in ('E1','E2')) for r in rows)
    checks['real_failure_not_gate_PASS']=summary['status']=='FAIL_STOP' and termination['reason']=='DYNAMICS_WALL_LIMIT' and termination['last_tick']*termination['dt_s']<5
    checks['no_closed_loop_results']=summary['closed_loop_runs']==0 and not summary['estimator_qualified'] and not summary['controller_qualified']
    audit={'kind':'READ_ONLY_ARTIFACT_AND_PRESERVATION_AUDIT','checks':checks,'all_checks_pass':all(checks.values()),
       'protected_file_count':len(manifest['protected_files_sha256']),'protected_failures':bad,
       'old_P2_file_count':len(manifest['old_P2_untracked_sha256']),'old_P2_failures':old_bad,
       'prior_P2_artifact_count':len(prior),'prior_P2_failures':prior_bad,
       'qualification_status':'FAIL_STOP','control_qualified':False,
       'source_run':str(run),'source_metadata_sha256':sha(run/'metadata.json'),'source_run_index_sha256':sha(run/'artifact_sha256.json')}
    write(out/'artifact_and_preservation_audit.json',audit)
    stats={'scope':'uncontrolled gravity-settling prefix only; no pose/force controller performance',
       'sample_count':len(rows),'first_log_time_s':float(t[0]),'last_log_time_s':float(t[-1]),
       'last_integrated_time_s':termination['last_tick']*termination['dt_s'],
       'required_settle_duration_s':5,'wall_s':summary['wall_s'],
       'final_logged_world_displacement_m':(poses[-1,:3,3]-poses[0,:3,3]).tolist(),
       'max_linear_speed_components_m_s':np.max(np.abs(velocity[:,:3]),axis=0).tolist(),
       'max_angular_speed_components_rad_s':np.max(np.abs(velocity[:,3:]),axis=0).tolist(),
       'max_tau_translation_components_m':np.max(np.abs(tau[:,:,:3]),axis=0).tolist(),
       'max_tau_rotation_components_rad':np.max(np.abs(tau[:,:,3:]),axis=0).tolist(),
       'final_logged_contact_force_components_N':raw[-1,:,:3].tolist(),
       'final_logged_contact_moment_components_Nm':raw[-1,:,3:].tolist(),
       'max_internal_force_norm_each_arm_N':np.max(np.linalg.norm(internal[:,:,:3],axis=2),axis=0).tolist(),
       'max_internal_moment_norm_each_arm_Nm':np.max(np.linalg.norm(internal[:,:,3:],axis=2),axis=0).tolist(),
       'final_logged_force_balance_N':rows[-1]['force_balance_N'],
       'final_logged_moment_balance_Nm':rows[-1]['moment_balance_Nm'],
       'fixed_five_second_terminal_metrics':None,'half_step_metrics':None,'main_experiment_metrics':None}
    write(out/'actual_prefix_metrics.json',stats)
    cases=[]
    for condition in cfg['suite']['primary_transport']['conditions']:
        for seed in cfg['suite']['main_seeds']:
            cases.append({'id':len(cases)+1,'kind':'primary_transport','condition':condition,'seed':seed,'duration_s':95})
    for kind in ('representative_high_moment','representative_delay'):
        for condition in cfg['suite'][kind]['conditions']:
            cases.append({'id':len(cases)+1,'kind':kind,'condition':condition,'seed':7,'duration_s':95})
    cases.append({'id':25,'kind':'conditional_sliding','condition':'exp3','seed':7,'duration_s':30})
    for condition in cfg['suite']['diagnostic_GT']['conditions']:
        cases.append({'id':len(cases)+1,'kind':'diagnostic_GT','condition':condition,'seed':7,'duration_s':95})
    cases.append({'id':30,'kind':'full_dynamics_half_step','condition':'exp3','seed':7,'duration_s':95})
    for case in cases: case.update(status='NOT_EXECUTED',reason='independent dynamics qualification stopped before estimator/control',result=None)
    ledger={'protocol_sha256':meta['protocol_sha256'],'cases':cases,'planned_primary':20,'planned_control_cases':30,
       'executed_primary':0,'executed_control_cases':0,'not_executed_cases':30,'diagnostic_GT_runs':0,
       'correction_rounds_already_used':1,'remaining_correction_rounds':2,'control_wall_s':0,
       'component_qualification_wall_s':summary['wall_s'],'counting_note':'Unexecuted controls are not fabricated failed trials. Prefix is one aborted no-control qualification.'}
    write(out/'control_case_ledger.json',ledger)
    write(out/'artifact_sha256.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    print(json.dumps({'all_checks_pass':all(checks.values()),'checks':len(checks),'protected_files':len(manifest['protected_files_sha256']),
         'saved_samples':len(rows),'last_integrated_time_s':stats['last_integrated_time_s'],'planned_controls_not_executed':30},ensure_ascii=False))
    return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
