#!/usr/bin/env python3
"""Stdlib saved-byte/AST self check, no candidate import or tool/model call."""
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
def p(n):return Path(n)if Path(n).is_absolute()else ROOT/n
def sha(n):return hashlib.sha256(p(n).read_bytes()).hexdigest()
def load(n):return json.loads(p(n).read_text())
def parse(n):return ast.parse(p(n).read_text())
def fn(t,n):return next(x for x in t.body if isinstance(x,ast.FunctionDef)and x.name==n)
def dump(x):return ast.dump(x,include_attributes=False)
RUNNER='scripts/p4_d080/qualify_rss_fixed32_refresh_v1_draft.py'
SUP='scripts/p4_d080/supervise_rss_fixed32_refresh_v1_draft.py'
TEMPLATE='configs/p4_d080/rss_fixed32_refresh_v1.DRAFT.json'
PRE='reports/P4_D080_RSS_FIXED32_THIN_ENGINEERING_REFRESH_PRE_DRAFT_20261018.md'
OLD_RUNNER='scripts/qualify_p4_full_r2_abb_rss_branch_fixed32_supervised_v2_draft.py'
OLD_SUP='scripts/supervise_p4_full_r2_abb_rss_branch_fixed32_v2_draft.py'
OLD_TEMPLATE='configs/p4_full/r2_abb_rss_branch_fixed32_math_supervised_v2.draft.json'
OLD_PRE='reports/P4_FULL_R2_ABB_RSS_BRANCH_FIXED32_SUPERVISED_V2_PRE_DRAFT_20261017.md'
BASE='scripts/p4_d080/build_v_pcs_local_v1_draft.py'
BASE_SUP='scripts/p4_d080/supervise_v_pcs_build_v1_draft.py'
SCOPE='configs/p4_d080/execution_scope_v1.json'
OVERLAY='results/p4_d080/20261017_SCOPE_RECOVERY/budget_scope_overlay.json'
archive=ROOT/'work/preserved_rss_fixed32_V2_before_D080_thin_refresh_20261018'
manifest=load(archive/'manifest.json');new=load(TEMPLATE);old=load(OLD_TEMPLATE)
r=parse(RUNNER);s=parse(SUP);oldr=parse(OLD_RUNNER);olds=parse(OLD_SUP);bases=parse(BASE_SUP)
rt=p(RUNNER).read_text();st=p(SUP).read_text();checks=[]
def check(name,ok,evidence=None):checks.append({'name':name,'passed':bool(ok),'evidence':evidence})
check('both_new_sources_parse_AST_without_import',isinstance(r,ast.Module)and isinstance(s,ast.Module))
check('all_four_V2_originals_preserved_and_unchanged',len(manifest)==4 and all(sha(n)==m['sha256']==sha(archive/n)for n,m in manifest.items()))
check('exact_V2_runner_and_supervisor_bytes',sha(OLD_RUNNER)=='4839efdf5b6bb921e1ec82a06074d20dda007365b1d8744f9e72abd343a49862'
 and sha(OLD_SUP)=='fada7f5aaf9e94d06aeb7572c062ba2dff7b843286ebaa571bf3af293a590619')
check('exact_reviewed_V_infrastructure_unchanged',sha(BASE)=='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578'
 and sha(BASE_SUP)=='7b50c7cd39a00958605f04a6fe997915dcd1f93aada4ed3f36276e2260f8e2ad')
assignments={v.targets[0].id:ast.literal_eval(v.value)for v in r.body if isinstance(v,ast.Assign)and len(v.targets)==1 and isinstance(v.targets[0],ast.Name)and v.targets[0].id in ['SCIENCE','LEGACY_SHA','LEGACY_SUPERVISOR_SHA','LEGACY_TEMPLATE_SHA','LEGACY_PRE_SHA','B_SHA','RUN','CLAIM','SCHEMA']}
science=assignments['SCIENCE']
check('all_twenty_original_scientific_fields_exact',len(science)==20 and all(new[k]==old[k]for k in science),list(science))
check('fixed4_same_complete_q12_and_order',new['fixed_cases']==old['fixed_cases']and [c['case_id']for c in new['fixed_cases']]==['II_obs0681','II_obs0689','III_obs1065','III_obs1073'])
check('original_branch0_7_and10wall20CPU_all_call_caps',new['passive_branches_in_order']==list(range(8))and new['budget']==old['budget']and new['budget']['wall_s']==10 and new['budget']['cpu_s']==20)
check('all_original_working_watchdog_stops_and_source_env_exact',new['supervision_engineering']==old['supervision_engineering']and new['source_environment']==old['source_environment'])
check('original_classification_targets_gates_gamma_zero_calls_exact',new['classification']=='RECONSTRUCTED_FIXED_SAVED_INPUT_BRANCH_MAPPING_MATH_ONLY'
 and new['RSS_gamma_preserved']==.2 and new['zero_calls']==old['zero_calls']and all(v==0 for v in new['zero_calls'].values()))
check('reuse_exact_execute_Budget_NativeOnce_function_objects_no_math_copy',
 'V.execute(args.protocol.resolve())'in rt and not any(isinstance(v,(ast.FunctionDef,ast.ClassDef))and v.name in ['execute','Budget','NativeOnce','independent','rank','errors','close','fk_agrees']for v in r.body)
 and 'from baselines'not in rt and 'import numpy'not in rt)
check('only_engineering_hooks_and_identity_globals_mutated',all(x in rt for x in [
 'V.validate=validate;V.current_prior=current_prior;V.supervisor_proof=supervisor_proof;V.active_p4=active_p4',
 'V.__file__=str(SELF);V.RUN=RUN;V.CLAIM=CLAIM;V.SCHEMA=SCHEMA;V.SUPERVISOR=str(SUPERVISOR.relative_to(ROOT))',
 "B.RUN_NAME=RUN;B.RUN=ROOT/'results/p4_full'/RUN"]))
check('complete_reviewed_prior_validator_direct_call','saved=B.validate_prior(ACTIVE_SPEC)'in rt and 'PRIOR_LEDGER='not in rt and 'V25'not in rt and 'V34'not in rt and 'V35'not in rt)
check('all_five_prior_fields_remain_null',all(new[k]is None for k in ['prior','accounting_snapshot','actual_charge_prior','previous_r2_wall_s','previous_r2_cpu_s']))
check('all_execution_authority_flags_and_reviews_false',new['frozen']is False and all(new[k]is False for k in ['qualification_execution_authorized','engineering_execution_authorized','formal_execution_authorized'])and all(v is False for v in new['reviews'].values()))
scope=load(SCOPE)
check('D080_original_scope_and_overlay_SHA_unchanged',sha(SCOPE)=='edbf914187f449d0ce145987cbf38bc7d668c69b536f806a86b28b6da1bded41'
 and sha(OVERLAY)=='7fe6eb5eaaf9002c7e1f62192acb472788225bd6207dc181a5d41baca4f52ac7')
check('D080_scope_I_V_18k_no_VI_or_formal_and_runtime_gate',scope['allowed_environments']==['I','II','III','IV','V']and scope['formal_table_I_D080']==18000
 and scope['VI_future_science_authorized']is False and scope['formal_execution_authorized']is False
 and "scope['formal_table_I_D080']==18000"in rt and "ledger['d080_formal_table_I_calls']==0"in rt)
check('original_science_bound_subset_preserved_current',all(new['bound_files_sha256'].get(k)==v==sha(k)for k,v in old['bound_files_sha256'].items()))
check('all_pre_prior_binding_bytes_current',all(sha(k)==v for k,v in new['bound_files_sha256'].items()),len(new['bound_files_sha256']))
check('source_record_canonical_identities_retained',all(sha(c['observations_path'])==c['observations_sha256']and load(c['observations_path'])[c['observation_index0']]['candidate_q_rad']==c['q12_rad']for c in new['fixed_cases']))
check('no_describe_or_implicit_prior_interface','--describe'not in rt and len(fn(r,'main').body)==4)
check('original_supervisor_actual_parent_argv_proof_reused',"ORIGINAL_PROOF=V.supervisor_proof"in rt and 'LAUNCH=ORIGINAL_PROOF(spec,protocol)'in rt)
check('old_activity_guard_retained_plus_D080_real_script_guard','rows=ORIGINAL_ACTIVE()'in rt
 and "allowed={os.getpid(),LAUNCH['actual_time_pid'],LAUNCH['supervisor_pid']}"in rt
 and "Path('/proc',str(pid),'cwd')/script"in rt and "('build_','qualify_','supervise_')"in rt)
life=['proc_table','exact_source_processes','stop_children','kill_source_identity','source_groups_after','watch']
check('original_supervisor_lifecycle_tools_direct_alias_no_copy',all(x+'=S.'+x in st for x in life)
 and not any(isinstance(v,ast.FunctionDef)and v.name in life for v in s.body),life)
# Compare the copied reviewed envelope AST after the sole exception handler
# addition allowing an unreadable original time file to remain unqualified.
bs=fn(bases,'main');ns=fn(s,'main');bf=next(v for v in bs.body if isinstance(v,ast.Try)).finalbody
nf=next(v for v in ns.body if isinstance(v,ast.Try)).finalbody
def envelope(body):
 begin=next(i for i,v in enumerate(body)if isinstance(v,ast.Assign)and ast.unparse(v).startswith('timing_valid = False'))
 end=next(i for i in range(begin,len(body))if isinstance(body[i],ast.Assign)and ast.unparse(body[i]).startswith('payload = dict('))
 return body[begin:end]
be=envelope(bf);ne=envelope(nf)
# New RSS finalizer retains the original V2 retained_hash helper after the V
# envelope; it is not part of the reused envelope itself.
ne=[v for v in ne if not(isinstance(v,ast.FunctionDef)and v.name=='retained_hash')]
for v in ne:
 for child in ast.walk(v):
  if isinstance(child,ast.ExceptHandler)and isinstance(child.type,ast.Tuple)and [getattr(e,'id','')for e in child.type.elts]==['ValueError','ArithmeticError','OSError']:
   child.type.elts=child.type.elts[:2]
check('Decimal_three_observation_envelope_exact_reviewed_V_AST_except_explicit_OSError',len(be)==len(ne)and all(dump(a)==dump(z)for a,z in zip(be,ne)))
check('raw_and_complete_envelope_separately_recorded','EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'in st and 'raw_GNUtime_upper_wall_s=raw_wall'in st
 and 'monotonic_envelope_valid=envelope_valid'in st and 'bool(timing_valid and envelope_valid and identity_unchanged'in st)
check('original_ten_twenty_caps_and_explicit_breach_retained',"wall<=min(10.,3600.-spec['previous_r2_wall_s'])"in st and "cpu<=min(20.,7200.-spec['previous_r2_cpu_s'])"in st
 and "payload['execution_cap_breach']=dict(wall=wall>10.,cpu=cpu>20.)"in st)
check('new_protocol_flags_required_before_launch',"spec['qualification_execution_authorized']is True"in st and "spec['engineering_execution_authorized']is False"in st
 and "spec['formal_execution_authorized']is False"in st and "'EXACT_REUSED_V2_SUPERVISION_LIFECYCLE_REQUIRED'"in st)
run=ROOT/'results/p4_full'/new['run_id'];claim=ROOT/'results/p4_full'/(new['claim_id']+'.claim.json')
check('new_run_claim_all_sidecars_absent',not run.exists()and not claim.exists()and not any(Path(str(run)+suffix).exists()for suffix in ['.supervision.time.txt','.supervision.jsonl','.supervision.stderr.log','.supervision.charge.json']))
check('no_stale_old_path_reused',new['run_id']!=old['run_id']and new['claim_id']!=old['claim_id']and all(new['run_id']in new['external_supervision'][key]for key in ['sibling_path','metadata_path','stderr_path','charge_path']))
check('nonempty_exact_review_binding_committed_protocol_REQUIRED','spec[\'review_evidence_sha256\']and all(sha(n)==w'in rt and 'COMMITTED_REFRESH_INPUT_REQUIRED_'in rt)
inputs=[RUNNER,SUP,TEMPLATE,PRE,OLD_RUNNER,OLD_SUP,OLD_TEMPLATE,OLD_PRE,BASE,BASE_SUP,SCOPE,OVERLAY]
result={'schema':'P4_D080_RSS_FIXED32_THIN_REFRESH_SELF_STATIC_V1','personnel_independent':False,
 'status':'PASS_SELF_STATIC_ONLY_NOT_EXECUTABLE_OR_SCIENTIFIC_QUALIFICATION'if all(c['passed']for c in checks)else 'FAIL_SELF_STATIC',
 'checks_total':len(checks),'checks_passed':sum(c['passed']for c in checks),'checks_failed':sum(not c['passed']for c in checks),
 'inputs_sha256':{n:sha(n)for n in inputs},'self_auditor_sha256':sha(__file__),'checks':checks,
 'scope':'Saved bytes/AST only, no adapter/module import, describe, compile, FK/IK/J/SVD, collision, sampler, RBS, solve, claim or new prior/ledger execution.',
 'new_scientific_calls':0,'new_compile_calls':0,'prior_bound':False,'original_model_and_all_scientific_function_bodies_unchanged':True,
 'independent_incremental_review_required':True,'prior_self_report':'reports/P4_D080_RSS_FIXED32_THIN_ENGINEERING_REFRESH_SELF_STATIC_20261018.json','prior_self_report_sha256':sha('reports/P4_D080_RSS_FIXED32_THIN_ENGINEERING_REFRESH_SELF_STATIC_20261018.json'),'self_auditor_correction':'First self report incorrectly required22 scientific field names; actual original immutable recipe has20. Only auditor cardinality assertion/label corrected; runner, supervisor, template, PRE and scientific content unchanged.'}
out=ROOT/'reports/P4_D080_RSS_FIXED32_THIN_ENGINEERING_REFRESH_SELF_STATIC_ADDENDUM_20261018.json'
with out.open('x')as f:f.write(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'total':len(checks),'pass':result['checks_passed'],'failed':[c for c in checks if not c['passed']],
 'output_sha256':sha(out)},indent=2))
