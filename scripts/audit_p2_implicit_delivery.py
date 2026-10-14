#!/usr/bin/env python3
"""Read-only preservation/readiness/ledger audit. Never executes science."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/20261014_P2_implicit_delivery_audit01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a,cwd=ROOT):return subprocess.check_output(['git',*a],cwd=cwd,text=True).strip()
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def diff(a,b,path=''):
 if isinstance(a,dict) and isinstance(b,dict):
  out=[]
  for k in sorted(a.keys()|b.keys()):
   if k not in a or k not in b:out.append({'path':path+'/'+k,'change':'ADDED' if k not in a else 'REMOVED'})
   else:out+=diff(a[k],b[k],path+'/'+k)
  return out
 return [] if a==b else [{'path':path,'before':a,'after':b}]
def main():
 OUT.mkdir(exist_ok=False)
 manifest=json.loads((ROOT/'results/20261013_P2_original_audit/preservation_manifest.json').read_text())
 mismatch=lambda base,items:[p for p,h in items.items() if not (base/p).is_file() or sha(base/p)!=h]
 protected=mismatch(ROOT,manifest['protected_files_sha256']);old=mismatch(ROOT.parent/'dual-arm-coordinated-manipulation-p2',manifest['old_P2_untracked_sha256'])
 retained={}
 for line in subprocess.check_output(['git','ls-tree','-r','eb2600a'],cwd=ROOT,text=True).splitlines():
  info,name=line.split('\t');obj=info.split()[2]
  if name.startswith(('baselines/p2_pose_force/','configs/p2_','reports/P2_','reports/p2_','reports/第二篇P2','results/20261013_P2','results/20261014_P2','scripts/qualify_p2_','scripts/audit_p2_','scripts/build_p2_','tests/test_p2_')):
   retained[name]=obj
 prior=[p for p,obj in retained.items() if not (ROOT/p).is_file() or git('hash-object',p)!=obj]
 v1p=ROOT/'configs/p2_closed_loop_protocol_v1.json';v2p=ROOT/'configs/p2_closed_loop_protocol_v2.json';v1=json.loads(v1p.read_text());v2=json.loads(v2p.read_text())
 stable=['conventions','original_parameters','model','clocks','estimator','reference','conditions','suite','metrics','outputs','contact_geometry']
 q1=dict(v1['numerical_qualification']);q2=dict(v2['numerical_qualification']);q1.pop('plant_integration');q2.pop('plant_integration')
 changed=diff(v1,v2)
 allowed={'/decisions/numerical_user_approval','/execution_authorized_this_round','/implicit_solver','/native_evaluation','/numerical_qualification/plant_integration','/parent_protocol','/qualification_source_commit_scope','/revision_input_commit','/schema_version','/status'}
 unapproved=[x['path'] for x in changed if x['path'] not in allowed and not x['path'].startswith('/readiness/')]
 indexes={};bad_artifacts=[];source_bad=[]
 for dirname in ('20261014_P2_implicit_qualification01','20261014_P2_implicit_FD_diagnosis01'):
  d=ROOT/'results'/dirname;idx=json.loads((d/'artifact_sha256.json').read_text());indexes[dirname]=sha(d/'artifact_sha256.json')
  for p,h in idx.items():
   if sha(d/p)!=h:bad_artifacts.append(dirname+'/'+p)
  meta=json.loads((d/'metadata.json').read_text())
  for p,h in meta['source_sha256'].items():
   blob=subprocess.check_output(['git','show',meta['source_commit']+':'+p],cwd=ROOT)
   if hashlib.sha256(blob).hexdigest()!=h:source_bad.append(dirname+':'+p)
 q=json.loads((ROOT/'results/20261014_P2_implicit_qualification01/summary.json').read_text());ds=json.loads((ROOT/'results/20261014_P2_implicit_FD_diagnosis01/summary.json').read_text())
 p4=ROOT.parent/'dual-arm-coordinated-manipulation-p4-three-methods';p4head=git('rev-parse','HEAD',cwd=p4);p4status=git('status','--porcelain',cwd=p4)
 checks={'protected_P4_files_exact':not protected,'old_P2_eight_files_exact':not old,'eb2600a_P2_science_reports_data_retained':not prior,'P4_HEAD_unchanged':p4head==manifest['base_commit'],'P4_clean':p4status=='','v1_exact':sha(v1p)=='423f58ca7cfe13861586bb486dcfd6d19c5e3d82b69e40c3d403c90d7c871df3','canonical_geometry_exact':sha(ROOT/'baselines/p2_pose_force/contact_geometry.py')=='47557da9189d8525e8a1ec343b5a4afc929405071d4e5de7d562091cc04a629a','canonical_mechanics_exact':sha(ROOT/'baselines/p2_pose_force/mechanics.py')=='34831b2cd37183bb597b674af853ac24a72f64b38b19ba1b182fd754f764ad61','v2_physics_controls_observations_seeds_budget_criteria_exact':all(v1[k]==v2[k] for k in stable) and q1==q2,'v2_diff_only_authorized_numerics_metadata':not unapproved,'all_new_artifact_SHA_exact':not bad_artifacts,'scientific_source_commit_bytes_exact':not source_bad,'actual_gate_FAIL_STOP_not_promoted':q['status']=='FAIL_STOP' and q['completed_checks']==46 and q['passed_checks']==45 and not q['dynamics_qualified'] and q['closed_loop_runs']==0,'diagnostic_not_promoted':not ds['qualification_promoted'],'no_implicit_trajectory_artifacts':not list((ROOT/'results/20261014_P2_implicit_qualification01').glob('*.jsonl.gz')),'remaining_correction_budget_one':ds['corrections_used_after_archive_fix']==2 and ds['remaining_corrections']==1}
 save('preservation_and_readiness.json',{'kind':'READ_ONLY_PRESERVATION_AND_READINESS_AUDIT_NOT_SCIENTIFIC_GATE_PASS','source_commit_at_audit':git('rev-parse','HEAD'),'checks':checks,'all_checks_pass':all(checks.values()),'protected_count':len(manifest['protected_files_sha256']),'protected_mismatches':protected,'old_P2_count':len(manifest['old_P2_untracked_sha256']),'old_P2_mismatches':old,'prior_P2_file_count':len(retained),'prior_P2_mismatches':prior,'artifact_mismatches':bad_artifacts,'source_mismatches':source_bad,'P4_HEAD':p4head,'P4_status':p4status,'v2_diff':changed,'unapproved_diff':unapproved,'artifact_index_SHA':indexes,'gate_status':'FAIL_STOP','implicit_plant_qualified':False,'estimator_qualified':False,'controller_qualified':False,'closed_loop_runs':0,'implicit_plant_trajectories':0,'corrections_used':2,'remaining_corrections':1})
 ledger=json.loads((ROOT/'results/20261014_P2_stage2_delivery_audit02/control_case_ledger.json').read_text());assert all(c['status']=='NOT_EXECUTED' for c in ledger['cases']);ledger.update({'current_protocol_v2_sha256':sha(v2p),'correction_rounds_already_used':2,'remaining_correction_rounds':1,'current_stop_reason':'NATIVE_RATE_JACOBIAN_FIXED_FD_GATE_FAIL_STOP','native_qualification_wall_s':q['wall_s'],'diagnostic_algorithm_wall_s':None,'diagnostic_process_wall_s_from_external_tool':0.145563236,'this_iteration_control_wall_s':0,'counting_note':'Original30case retained; unexecuted not failed controls. Component math and archive/report work do not consume control cases or fabricate results.'});save('control_case_ledger.json',ledger)
 save('artifact_sha256.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()});print(json.dumps({'all_checks_pass':all(checks.values()),'protected':len(manifest['protected_files_sha256']),'prior_P2':len(retained),'failures':{k:v for k,v in checks.items() if not v},'control_runs':0}));return 0 if all(checks.values()) else 2
if __name__=='__main__':raise SystemExit(main())
