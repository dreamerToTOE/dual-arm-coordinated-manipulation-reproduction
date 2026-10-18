#!/usr/bin/env python3
"""Thin AST/saved-input PRE only. No candidate imports or scientific calls."""
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
def p(n):
    q=Path(n);return q if q.is_absolute() else ROOT/q
def raw(n):return p(n).read_bytes()
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def js(n):return json.loads(raw(n))
def tree(n):return ast.parse(raw(n))
def fn(t,n):return next(z for z in t.body if isinstance(z,(ast.FunctionDef,ast.ClassDef)) and z.name==n)
def dump(n):return ast.dump(n,include_attributes=False)
RUNNER='scripts/p4_d080/qualify_iii_rrt_pcs_source01_v1_draft.py'
SUP='scripts/p4_d080/supervise_iii_rrt_pcs_source01_v1_draft.py'
BASESUP='scripts/p4_d080/supervise_v_pcs_local_v1_draft.py'
SPEC='configs/p4_d080/iii_rrt_pcs_source01_v1.DRAFT.json'
PRE='reports/P4_D080_ENV_III_RRT_PCS_SOURCE01_PRE_DRAFT_20261018.md'
BUILDPOST='reports/P4_D080_ENV_III_RRT_PCS_BUILD01_SAVED_INDEPENDENT_POST_20261018.json'
BUILD='results/p4_full/20261018_R2_D080_III_RRT_PCS_BUILD01/execution.json'
L='scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py'
B='scripts/p4_d080/build_v_pcs_local_v1_draft.py'
s=js(SPEC);e=js(BUILD);post=js(BUILDPOST);t=tree(RUNNER);txt=raw(RUNNER).decode();checks=[]
def ck(n,v,ev=None):checks.append(dict(name=n,passed=bool(v),evidence=ev))
ck('exact_stable_four_drafts',sha(RUNNER)=='0226422a81b86a37cb306f574cec38ab1daf7a05192ca87d6021e7a4bd8cbd7c' and sha(SUP)=='e3297acf9b9230cba3d08ea1350984d59f1589ce804df03b2897268b92d75f6c' and sha(SPEC)=='867b02b9f4e52a734527d3ef515c84524fae9d843fca69547b8a80f5be6ed016' and sha(PRE)=='03d93f357fd62ea246587c67216207947530d617621bc966f2c910a2e61bace6')
ck('exact_reused_transport_and_prior_bases_no_import',sha(L)=='c177eb8299e43eaa8fe7bc80db4aea1a0c445aa1f0655f3e339048a5532a1eca' and sha(B)=='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578' and sha(BASESUP)=='2a0920c0eb6dfe2684366f1acf541a0c69c2797ef3bbc89d0a5c82578cfed4d1')
bs=tree(BASESUP);ns=tree(SUP);bm=fn(bs,'main');nm=copy.deepcopy(fn(ns,'main'))
replacements={'P4_D080_III_RRT_PCS_SOURCE01_A01_SEED7_30W60CPU_20261018.claim.json':'P4_D080_V_PCS_LOCAL01_FIXED_A02_PM005_30W60CPU_20261018.claim.json','GNUtime child local runner+one reaped III RRT PCS source, one original10s solve. Supervisor own metadata/time-log fsync costs excluded.':'GNUtime child local runner+two sequential reaped fixed V local sources. Supervisor own metadata/time-log fsync costs excluded.','P4_D080_III_RRT_PCS_SOURCE01_EXTERNAL_COST_CHARGE_V1':'P4_D080_V_PCS_LOCAL_EXTERNAL_COST_CHARGE_V1'}
for z in ast.walk(nm):
    if isinstance(z,ast.Constant) and isinstance(z.value,str) and z.value in replacements:z.value=replacements[z.value]
# The only main-body changed statement is the stronger III admission gate.
ck('supervisor_all_lifecycle_Decimal_inode_cost_AST_reused_except_admission',len(bm.body)==len(nm.body) and all(dump(x)==dump(y) for j,(x,y) in enumerate(zip(bm.body,nm.body)) if j!=4),{'admission_statement_only':4})
ck('build49_exact_engineering_certificate_reused_without_retest',sha(BUILDPOST)=='c311dd3601995006c6b476163b51c3719bad193896d17ca349e35ca5ed3d829e' and sha(BUILD)=='16696c0d80ce0ac893814afc2ca5e0720e6ebb478da63cc6e46eb8f7b80c4f31' and post['checks_total']==post['checks_passed']==49 and post['personnel_independent'] is post['engineering_build_qualified'] is True and post['source_planning_qualified'] is post['independent_path_qualified'] is False and s['target']['binary_sha256']==e['targets'][0]['binary_sha256']==sha(s['target']['binary']))
endpoints=[js('results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/III_'+str(i)+'.json') for i in range(2)]
expected={'environment':'III','seed':7,'range_rad':.8,'goal_bias':.05,'solve_seconds':10.,'start_q12':endpoints[0]['selected_q_rad'],'goal_q12':endpoints[1]['selected_q_rad'],'bounds_low_rad':[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]*2,'bounds_high_rad':[2.88,1.919,1.22,2.79,2.09,3.1416]*2}
ck('fixed_III_A01_seed7_range08_original10s_full_input_binary64_exact',json.dumps(expected,sort_keys=True)==json.dumps(s['request'],sort_keys=True) and all(z['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED' for z in endpoints) and len(json.dumps(expected,separators=(',',':')).encode()+b'\n')<4096)
meshes={n:w for n,w in e['staged_after_sha256'].items() if Path(n).parent==Path(s['target']['binary']).parent/'simulator' and Path(n).suffix=='.tris'}
bound=s['bound_files_sha256']
ck('all_saved_build_dependencies_and_exact20mesh_prebound_maps_reused',len(meshes)==20 and s['runtime_meshes_sha256']==meshes and all(bound.get(n)==w for field in ['staged_after_sha256','dependencies_after_sha256'] for n,w in e[field].items()) and len(bound)==734)
sc=fn(t,'Session');bc=fn(t,'Budget');sessions=[z for z in sc.body if isinstance(z,ast.FunctionDef)]
ck('audited_pump_register_finish_and_budget_close_remaining_inherited',ast.unparse(sc.bases[0])=='L.Session' and {z.name for z in sessions}=={'__init__','start','run_once'} and ast.unparse(bc.bases[0])=='L.Budget' and {z.name for z in bc.body if isinstance(z,ast.FunctionDef)}=={'__init__','check'})
sessiontext=ast.unparse(sc)
ck('one_compact_write_then_stdin_EOF_raw_mixed_stdout_retained',sessiontext.count('os.write(')==1 and all(z in sessiontext for z in ["separators=(',', ':')","self.proc.stdin.close()",'self.pending == bytes(self.raw[\'stdout\'])','self.pending = b\'\'',"json.loads(lines[-1]) == result",'self.finish(normal=True)']) and sessiontext.count('subprocess.Popen(')==1)
ck('single_registered_source_process_before_interrupts_group_CPU_caps',s['source_process_limit']==s['source_solve_limit']==1 and s['budget']=={'wall_s':30,'cpu_s':60} and s['working_budget']=={'wall_s':25,'cpu_s':50} and 'B.lifecycle.live_group_cpu' in ast.unparse(bc) and 'resource.setrlimit(resource.RLIMIT_CPU, (60, 60))' in sessiontext and txt.index('sessions.append(session)')<txt.index('session.start()'))
guard=copy.deepcopy(fn(t,'active_d080'))
for z in ast.walk(guard):
    if isinstance(z,ast.Constant) and z.value=='time_pid':z.value='actual_time_pid'
ck('actual_D080_guard_exact_III_build_body_except_proof_key',dump(guard)==dump(fn(tree('scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py'),'active_d080')) and 'not L.active_p4() and not active_d080(proof)' in txt)
ck('full_result_log_counts_true_false_partial_and_observed_one_solve_only',all(z in txt for z in ["record['solve_calls_from_result'] = result['solve_calls']","record['status'] = result_contract(result, spec, work)",'COMPLETE_ORIGINAL_POSTRETURN_LOGS_MUST_MATCH_RESULT_NO_TRUNCATION','EXACT_APPROXIMATE_AND_NO_SOLUTION_MUST_REMAIN_SEPARATE',"'source_FK_IK_PQP_started': 'UNOBSERVED_NO_START_HOOK'","'independent_path_qualified': False"]) and txt.index("record['status'] = result_contract(result, spec, work)")<txt.index("record['solve_calls_from_result'] = result['solve_calls']"))
ck('central_cleanup_reap_double_EOF_raw_outputs_and_receipt_preserved',all(z in txt for z in ['L.kill_source_group(session.proc)','session.finish(normal=False)','ALL_REAL_WORKERS_REAPED_EMPTY_DUAL_EOF_REQUIRED',"'process{index}_{channel}.bin'","record['retained_run_files_sha256']", "L.durable_new(folder / 'execution.json', record)","L.durable_new(folder / 'cost_receipt.json', receipt)"]))
ck('runtime_current_prior_commit_and_parent_inode_gates_required',all(z in txt for z in ['prior = B.validate_prior(spec)',"record['prior_after'] = B.validate_prior(spec)",'ALL_RUNTIME_SOURCE_AND_PROTOCOL_MUST_BE_COMMITTED','ACTUAL_EXCLUSIVE_TIME_INODE_REQUIRED','ACTUAL_GNUTIME_PARENT_SOURCE_PROTOCOL_ARGV_REQUIRED','ALL_CURRENT_CHARGED_PRIOR_CERTIFICATES_REQUIRED']) and s['actual_charge_prior'] is None)
ck('draft_flags_false_and_exact_current_V35_reference',all(s[k] is False for k in ['frozen','scientific_execution_authorized','independent_review_passed','formal_execution_authorized']) and all(z is False for z in s['reviews'].values()) and s['prior']['ledger_sha256']==sha(s['prior']['ledger'])=='0565da281be5f00acd8444b8d7fd31c2392e0a4556ac2dbab2115b3fb312f28f' and s['prior']['wall_s']==1135.516766637992 and s['prior']['cpu_s']==961.89109)
ck('D080_no_VI_formal_or_independent_model_and_fresh_claim',s['VI_future_science_authorized'] is False and s['formal_table_I_D080_required']==18000 and s['formal_table_I_calls']==s['new_independent_model_calls']==0 and not (ROOT/'results/p4_full'/s['run_id']).exists() and not (ROOT/'results/p4_full'/(s['claim_id']+'.claim.json')).exists())
failed=[z for z in checks if not z['passed']]
report={'schema':'P4_D080_III_RRT_PCS_SOURCE01_INCREMENTAL_INDEPENDENT_PRE_V1','personnel_independent':True,'status':'PASS_THIN_ONE_SOURCE_PRE_ONLY' if not failed else 'FAIL_THIN_ONE_SOURCE_PRE','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'inputs_sha256':{n:sha(n) for n in [RUNNER,SUP,SPEC,PRE,BUILD,BUILDPOST,L,B,BASESUP]},'auditor_sha256':sha(__file__),'reused_engineering_POST_checks':49,'repeated_build_or_local_science_calls':0,'new_compile_binary_model_scientific_calls':0,'full_old_bound_hash_sweep_repeated':False,'allowed_root_freeze_transform':{'preserve_DRAFT':True,'new_config_required':True,'flags_to_true':['frozen','scientific_execution_authorized','independent_review_passed'],'review_flags_to_true':'exact three existing boolean reviews','formal_execution_authorized':False,'prior':'Bind latest actual charged ledger; actual_charge_prior exactly reused B.validate_prior return; preserve734 original bindings and add its complete evidence plus this PRE/auditor. No conflicting overwrite. Runtime independently enforces current prior.','status_and_prior_completion_metadata_only':'Frozen source only; no path or independent-model qualification.','fixed_conditions':'III A01 binary64,seed7,range.8,bias.05,one original10s solve,one process,30/60 outer25/50 work; exact already-built81dac2 binary/20mesh and all scientific/source bytes unchanged.','commit_before_root_unique_supervisor':True},'limits':['Source exact is a saved candidate only; independent full-path qualification remains false.','No repeated II paths, III local7+1 or BUILD49.','Original FK/IK/PQP internal starts unobserved; actual completed one solve recorded from returned result only.','No solve retry after failure under unchanged root cause; preserve all partial outputs and raw logs.']}
out=ROOT/'reports/P4_D080_ENV_III_RRT_PCS_SOURCE01_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
with out.open('x') as f:f.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks_total':len(checks),'failed':failed,'sha256':sha(out)},ensure_ascii=False,indent=2))
