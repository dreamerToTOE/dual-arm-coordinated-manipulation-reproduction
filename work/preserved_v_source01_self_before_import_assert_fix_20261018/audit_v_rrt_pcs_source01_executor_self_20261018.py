#!/usr/bin/env python3
"""Pure stdlib AST/current-byte V SOURCE01 self review; never imports candidates."""
from pathlib import Path
from collections import Counter
import ast
import hashlib
import json
ROOT=Path(__file__).resolve().parents[3]
if not (ROOT/'AGENTS.md').is_file():ROOT=Path.cwd().resolve()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
def check(name,ok):checks.append({'name':name,'pass':bool(ok)})
def tree(p):return ast.parse(p.read_text())
def fn(t,n):return next(x for x in t.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))and x.name==n)
def dump(x):return ast.dump(x,include_attributes=False)
runner=ROOT/'scripts/p4_d080/qualify_v_rrt_pcs_source01_v1_draft.py'
sup=ROOT/'scripts/p4_d080/supervise_v_rrt_pcs_source01_v1_draft.py'
old=ROOT/'scripts/p4_d080/qualify_iii_rrt_pcs_source01_v1_draft.py'
oldsup=ROOT/'scripts/p4_d080/supervise_iii_rrt_pcs_source01_v1_draft.py'
config=ROOT/'configs/p4_d080/v_rrt_pcs_source01_v1.DRAFT.json'
pre=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_PRE_DRAFT_20261018.md'
d=json.loads(config.read_text());t=tree(runner);s=tree(sup);ot=tree(old)
check('Python AST parses without candidate import',isinstance(t,ast.Module)and isinstance(s,ast.Module))
check('Every current bound file hash matches',all(Path(n).is_file()and sha(n)==v for n,v in d['bound_files_sha256'].items()))
check('Top level draft and every review gate remain false',all(d[k]is False for k in ('frozen','scientific_execution_authorized','independent_review_passed','formal_execution_authorized'))and all(v is False for v in d['reviews'].values()))
check('Actual ELF BUILD POST checks and prior are unbound',d['target']['binary_sha256']is None and all(d['build_assets'][k]is None for k in ('execution_sha256','post_sha256','post_checks_total'))and all(d['prior'][k]is None for k in ('ledger','ledger_sha256','wall_s','cpu_s'))and d['actual_charge_prior']is None)
req=d['request'];caps=req['caps'];names={'public_request','project_fixed','identify','is_valid_rbs','rbs','reconstruct','native_fk','native_ik','specific_ik','limits','collision','pqp','mesh_load','records'}
check('Exact14 resource caps frozen at configure ceiling',set(caps)==names and all(type(v)is int and v==1000000 for v in caps.values())and d['resource_caps_only']is True and d['cap_reached_action']=='FAIL_RETAIN_PREFIX_NO_RETRY')
check('Single source solve10 seed7 range.2 original goalbias',req['seed']==7 and req['solve_seconds']==10. and req['range_rad']==.2 and req['goal_bias']==.05 and d['source_process_limit']==d['source_solve_limit']==1)
check('Outer30/60 work25/50 without new models or physical claim',d['budget']=={'wall_s':30,'cpu_s':60}and d['working_budget']=={'wall_s':25,'cpu_s':50}and d['new_independent_model_calls']==0 and d['independent_path_qualified']is False)
check('V original restricted sampler bounds',req['bounds_low_rad']==[-3.1416,-1.0472,-3.1416/2,-3.1416,-2.0944,-3.1416]*2 and req['bounds_high_rad']==[3.1416,2.1871,1.3090,3.1416,2.0944,3.1416]*2)
for role,digest in [('start','f906a6b61999c71efe15c8d86188edbded704d66dcba18f9833d940ccfa6c405'),('goal','feae5fd78837327db9c83d66621e2aa4fc9eec72a46c0d0dfc1e98cbc9d88737')]:
 p=ROOT/('results/p4_full/20261015_R2_ENDPOINT_COLLISION_REPLAY01/V_'+role+'.json');j=json.loads(p.read_text());check('Exact saved A02 '+role,sha(p)==digest and req[role+'_q12']==j['selected_q_rad']and j['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'and j['collision']['selected_variant']=='aligned')
local=json.loads((ROOT/'configs/p4_d080/v_pcs_local01_v1.json').read_text())
check('All27 runtime meshes equal saved local protocol',len(d['runtime_meshes_sha256'])==27 and d['runtime_meshes_sha256']==local['runtime_meshes_sha256'])
check('Original driver unchanged from20/20 seam review',sha(ROOT/'baselines/p4_full/geometry_consistent/comau_v_rrt_pcs_e2e_driver_v1_draft.cpp')=='e7e99e8f6d96f88a86f95daff3ee3bfb7fb5dbca991f85b6c2dddfa8ff85f82b')
# Reconstruct the only supervisor identity substitutions; lifecycle/cost bytes match.
a=oldsup.read_text()
for x,y in [('20261018_R2_D080_III_RRT_PCS_SOURCE01','20261018_R2_D080_V_RRT_PCS_SOURCE01'),('P4_D080_III_RRT_PCS_SOURCE01_A01','P4_D080_V_RRT_PCS_SOURCE01_A02'),('CORRECTED_ABB_APC_ALIGNED_III_ORIGINAL_RRT_PCS_CONTROL_RECONSTRUCTED_A01','CORRECTED_COMAU_APC_ALIGNED_V3_RECONSTRUCTED_A02_ORIGINAL_RRT_CONTROL'),('qualify_iii_rrt_pcs_source01','qualify_v_rrt_pcs_source01'),('P4_D080_III_RRT_PCS_SOURCE01','P4_D080_V_RRT_PCS_SOURCE01'),("spec['environment']=='III'","spec['environment']=='V'"),('FROZEN_III_RRT_PCS','FROZEN_V_RRT_PCS'),('one reaped III RRT PCS source','one reaped V RRT PCS source')]:a=a.replace(x,y)
check('Entire supervisor exact approved identity-only adaptation',sup.read_text()==a)
# Reconstruct expected full execute body, preserving all cleanup/accounting branches.
node=fn(ot,'execute');a='\n'.join(old.read_text().splitlines()[node.lineno-1:node.end_lineno])+'\n'
for x,y in [('P4_D080_III_RRT_PCS_SOURCE01','P4_D080_V_RRT_PCS_SOURCE01'),('FRESH_SINGLE_III_SOURCE','FRESH_SINGLE_V_SOURCE'),('RUNTIME_III_MESH_BYTES_CHANGED','RUNTIME_V_MESH_BYTES_CHANGED'),('III_SINGLE_SOURCE_DID_NOT_COMPLETE','V_SINGLE_SOURCE_DID_NOT_COMPLETE')]:a=a.replace(x,y)
a=a.replace("        result = session.run_once(spec['request'])","        global ACTIVE_SESSION\n        ACTIVE_SESSION = session\n        result = session.run_once(spec['request'])")
a=a.replace("'schema': 'P4_D080_V_RRT_PCS_SOURCE01_EXECUTION_V1', 'run_id': RUN, 'classification': LABEL,","'schema': 'P4_D080_V_RRT_PCS_SOURCE01_EXECUTION_V1', 'run_id': RUN, 'classification': LABEL, 'environment': 'V',")
a=a.replace("        record['source_identify_true_started'] = result['identify_true_started']","        record['source_identify_true_started'] = result['identify_true_started']\n        record['source_observed_counts_started'] = result['source_observed_counts_started']\n        record['source_FK_IK_PQP_started'] = {n: result['source_observed_counts_started'].get(n, 0) for n in ('native_fk', 'native_ik', 'specific_ik', 'pqp')}\n        record['source_actual_internal_call_starts'] = 'V_OBSERVER_ENTRY_RECORDS_WITH_LEGACY_POSTRETURN_ABI_SEPARATE'")
check('Whole execute including finalizer exact fixed adaptation AST',dump(fn(t,'execute'))==dump(fn(ast.parse(a),'execute')))
text=runner.read_text()
check('Direct audited budget transport proof activity aliases',all(v in text for v in ['Budget, Session = I.Budget, I.Session','supervisor_proof, active_d080 = I.supervisor_proof, I.active_d080','I.__file__ = str(Path(__file__).resolve())','III_SOURCE = Path(I.__file__).resolve()']))
check('Actual build and all bound stage dependency maps mandatory',all(v in text for v in ["assets['post_checks_total'] > 0","post['checks_total'] == post['checks_passed'] == assets['post_checks_total']","'bound_files_after_sha256', 'staged_after_sha256', 'dependencies_after_sha256'","post['engineering_build_qualified'] is True"]))
check('V source classifications stay physically unqualified',all(v in text for v in ["result['full_physical_geometry_or_CCD_qualified'] is False","result['full_solve_plain_trace_consistency_qualified'] is False","result['independent_path_qualified'] is False","result['source_observation_trace_mode'] == 1"]))
check('Legacy true false postreturn ABI reused in full',"inherited_status = I.result_contract(legacy, spec, work)"in text and "legacy.update(schema='P4_ABB_III_RRT_PCS_END_TO_END_DRAFT_V1', environment='III')"in text)
check('Real V entered records and full stdout stderr trace retained',all(v in text for v in ["row['event'] == 'completed'",'counts == expected_counts',"ACTIVE_SESSION.raw['stderr'].splitlines()",'len(traces) == 2 * len(records)',"record['source_observed_counts_started'] = result['source_observed_counts_started']"]))
check('D080 VI and formal scopes unchanged',d['VI_future_science_authorized']is False and d['formal_table_I_D080_required']==18000 and d['formal_table_I_calls']==0)
check('All own source PRE and true lifecycle bound',all(str(ROOT/v)in d['bound_files_sha256']for v in ['scripts/p4_d080/qualify_v_rrt_pcs_source01_v1_draft.py','scripts/p4_d080/supervise_v_rrt_pcs_source01_v1_draft.py','scripts/p4_d080/qualify_iii_rrt_pcs_source01_v1_draft.py','scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py','scripts/p4_d080/build_v_pcs_local_v1_draft.py','scripts/build_p4_full_r2_abb_cbirrt_d_draft.py','reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_PRE_DRAFT_20261018.md']))
check('Raw preservation complete inherited finalizer',all(v in text for v in ["'source_process_registry'","'pipe_EOF_observed'","'ALL_REAL_WORKERS_REAPED_EMPTY_DUAL_EOF_REQUIRED'","'raw_evidence_persistence'","L.durable_new(folder / 'cost_receipt.json', receipt)"]))
check('No direct subprocess run at module scope',not any(isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Attribute)and n.value.func.attr in {'run','Popen','check_output','execute'}for n in t.body))
check('Candidate source not imported by this self checker','import qualify_'not in Path(__file__).read_text()and 'import build_'not in Path(__file__).read_text())
result={'schema':'P4_D080_V_SOURCE01_SELF_STATIC_V1','personnel_independent':False,'candidate_imports':0,'compile_calls':0,'binary_execution_calls':0,'model_calls':0,'solve_calls':0,'checks_total':len(checks),'checks_passed':sum(x['pass']for x in checks),'checks_failed':sum(not x['pass']for x in checks),'checks':checks,'inputs_sha256':{str(p.relative_to(ROOT)):sha(p)for p in [runner,sup,config,pre,old,oldsup]},'status':'PASS_SELF_ONLY_NOT_INDEPENDENT_NOT_FROZEN'if all(x['pass']for x in checks)else 'FAIL_RETAINED'}
out=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_EXECUTOR_SELF_STATIC_20261018.json'
with out.open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'status':result['status'],'checks_passed':result['checks_passed'],'checks_total':result['checks_total'],'failures':[x['name']for x in checks if not x['pass']],'sha256':sha(out)}))
