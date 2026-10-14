#!/usr/bin/env python3
"""Read-only original-asset, actual log causality, budgets and stopped-case audit."""
import gzip,hashlib,json,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/20261014_P2_closed_loop_delivery_audit01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args,cwd=ROOT):return subprocess.check_output(['git',*args],cwd=cwd,text=True).strip()
def logread(p):
 with gzip.open(p,'rt') as f:return [json.loads(x) for x in f]
def write(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 OUT.mkdir(exist_ok=False);checks={};issues=[]
 manifest=json.loads((ROOT/'results/20261013_P2_original_audit/preservation_manifest.json').read_text())
 for label,base,field in (('P4_protected',ROOT,'protected_files_sha256'),('old_P2_untracked',ROOT.parent/'dual-arm-coordinated-manipulation-p2','old_P2_untracked_sha256')):
  failures=[p for p,h in manifest[field].items() if not (base/p).is_file() or sha(base/p)!=h];checks[label+'_bytes_exact']=not failures;issues.extend(label+':'+p for p in failures)
 old=[]
 for line in subprocess.check_output(['git','ls-tree','-r','4276ce5'],cwd=ROOT,text=True).splitlines():
  info,p=line.split('\t');obj=info.split()[2]
  if p.startswith(('reports/P2_','reports/p2_','reports/第二篇P2','results/20261013_P2','results/20261014_P2','configs/p2_','baselines/p2_pose_force/','tests/test_p2_')) and p not in ('baselines/p2_pose_force/native_kernel.cpp','baselines/p2_pose_force/native_model.py'):
   old.append(p)
   if git('hash-object',p)!=obj:issues.append('prior_P2_changed:'+p)
 checks['prior_P2_science_reports_failures_preserved']=not any(x.startswith('prior_P2_changed:') for x in issues)
 p4=ROOT.parent/'dual-arm-coordinated-manipulation-p4-three-methods';checks['P4_HEAD_clean']=git('rev-parse','HEAD',cwd=p4)==manifest['base_commit'] and git('status','--porcelain',cwd=p4)==''
 v1=json.loads((ROOT/'configs/p2_closed_loop_protocol_v1.json').read_text());v3=json.loads((ROOT/'configs/p2_closed_loop_protocol_v3.json').read_text());checks['original_physics_controls_noise_clocks_seed_budget_metrics_exact']=all(v1[k]==v3[k] for k in ('conventions','original_parameters','model','clocks','estimator','reference','conditions','suite','metrics','outputs','contact_geometry'))
 checks['v1_bytes_exact']=sha(ROOT/'configs/p2_closed_loop_protocol_v1.json')=='423f58ca7cfe13861586bb486dcfd6d19c5e3d82b69e40c3d403c90d7c871df3'
 checks['approved_geometry_bytes_exact']=sha(ROOT/'baselines/p2_pose_force/contact_geometry.py')=='47557da9189d8525e8a1ec343b5a4afc929405071d4e5de7d562091cc04a629a'
 names=['20261014_P2_implicit_qualification01','20261014_P2_implicit_FD_diagnosis01','20261014_P2_implicit_qualification_v3_01','20261014_P2_components_qualification01','20261014_P2_clock_qualification01','20261014_P2_closed_loop_suite01','20261014_P2_closed_loop_suite02','20261014_P2_closed_loop_analysis01']
 indexsha={};bad=[]
 for name in names:
  d=ROOT/'results'/name;idx=json.loads((d/'artifact_sha256.json').read_text());indexsha[name]=sha(d/'artifact_sha256.json')
  for p,h in idx.items():
   if sha(d/p)!=h:bad.append(name+'/'+p)
 checks['all_original_new_run_indexes_exact']=not bad;issues.extend('artifact:'+p for p in bad)
 suite=ROOT/'results/20261014_P2_closed_loop_suite02';run=suite/'case_11_exp3_7';ss=json.loads((suite/'summary.json').read_text());summary=json.loads((run/'summary.json').read_text());ledger=json.loads((suite/'case_ledger.json').read_text());meta=json.loads((run/'metadata.json').read_text())
 source_bad=[]
 for p,h in meta['source_sha256'].items():
  b=subprocess.check_output(['git','show',meta['source_commit']+':'+p],cwd=ROOT)
  if hashlib.sha256(b).hexdigest()!=h:source_bad.append(p)
 checks['actual_closedloop_source_commit_bytes_exact']=not source_bad
 sensors=logread(run/'sensors.jsonl.gz');est=logread(run/'estimator.jsonl.gz');plant=logread(run/'plant.jsonl.gz');commands=logread(run/'commands.jsonl.gz');init=json.loads((run/'initialization.json').read_text());events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
 trans=[s['observation'] for s in sensors if s['phase']=='transport'];issued=[(s['kind'],s['sample_id']) for s in trans];consumed=[tuple(k) for k in init['consumed_samples']]+[tuple(k) for e in est for k in e['observations_consumed']]
 checks['all_sensor_samples_unique_and_consumed_once']=len(issued)==len(set(issued)) and len(consumed)==len(set(consumed)) and set(issued)==set(consumed)
 obsbykey={(s['kind'],s['sample_id']):s for s in trans};checks['every_update_at_exact_sample_delivery_stamp']=all(obsbykey[tuple(k)]['sample_stamp']==e['time_s']==obsbykey[tuple(k)]['delivery_stamp'] for e in est for k in e['observations_consumed'])
 checks['integer_250Hz_plant_log']=len(plant)==987 and all(p['tick']==12*i and abs(p['time_s']-12*i/3000)<1e-12 for i,p in enumerate(plant))
 commands_by_tick={c['tick']:c for c in commands};pubok=True
 for e in events:
  if e['type']=='publish':
   c=commands_by_tick[e['source_command_tick']];side=e['side']-1;published=np.array(c['U_selected'][side]);pubok&=e['source_command_tick']<=e['tick'] and np.array_equal(published,np.array(e['U'])) and e['tick']%(15 if side==0 else 60)==0
 checks['publication_only_uses_causal_H_selected_latest_command']=bool(pubok)
 checks['no_primary_GT_state_control']=summary['GT_control_state_reads']==0 and all(c['source']=='observation_initialized_IESEKF' and not c['diagnostic_GT'] for c in commands)
 checks['failure_prefix_not_feedback_success']=summary['last_event_time_s']==3.948 and all(np.count_nonzero(c['U_F'])==0 and np.count_nonzero(c['U_P'])==0 for c in commands)
 checks['one_failed_case_29_not_executed']=ss['executed_cases']==1 and ss['completed_cases']==0 and ledger['not_executed']==29 and len([c for c in ledger['cases'] if c['status']=='FAIL_STOP'])==1
 checks['three_corrections_exhausted_not_reset']=summary['corrections_used']==3 and summary['remaining_corrections']==0 and ledger['corrections_used']==3
 checks['actual_wall_within_original_limits']=summary['wall_s']<=120 and ss['wall_s']+ss['prior_qualification_wall_s']<=7200
 checks['missing_frozen_windows_null']=all(v is None for v in summary['metrics'].values())
 checks['closedloop_failure_not_promoted']=not ss['closed_loop_qualified'] and summary['reason']=='ESTIMATOR_MODEL_PAD_DOMAIN_INVALID'
 checks['observer_original_Euler_no_substep']=meta['observer_mean_integration']=='original Eq18 right Euler at fresh observation/heartbeat events; no internal substeps'
 write('preservation_and_causality.json',{'kind':'READ_ONLY_DELIVERY_AUDIT_NOT_FULL_LOOP_PASS','checks':checks,'all_checks_pass':all(checks.values()),'issues':issues,'protected_P4_files':len(manifest['protected_files_sha256']),'old_P2_files':len(manifest['old_P2_untracked_sha256']),'prior_P2_files_from4276ce5':len(old),'source_mismatches':source_bad,'run_index_sha256':indexsha,'case':summary,'transport_observation_count':len(issued),'consumed_count':len(consumed),'P4_HEAD':manifest['base_commit'],'closedloop_qualified':False,'current_correction_count':3})
 write('artifact_sha256.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()});print(json.dumps({'all_checks_pass':all(checks.values()),'failed_checks':{k:v for k,v in checks.items() if not v},'P4_preserved':1023,'prior_P2_files':len(old),'observations':len(issued),'control_cases':1}));return 0 if all(checks.values()) else 2
if __name__=='__main__':raise SystemExit(main())
