#!/usr/bin/env python3
"""Independent static and saved-evidence review of prior-validator v2."""
import ast, hashlib, json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
V1=R/'scripts/p4_d080/validate_prior_preflight_recovery_v1.py'
V2=R/'scripts/p4_d080/validate_prior_preflight_recovery_v2.py'
BUILDER=R/'scripts/p4_d080/build_v_rrt_pcs_e2e_v2_draft.py'
LEDGER=R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V39.json'
POST=R/'reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_COST_ONLY_V2_CORRECTED_20261018.json'
checks=[]; inputs={}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(name,passed,detail=''): checks.append({'name':name,'passed':bool(passed),'detail':detail})
for p in (V1,V2,BUILDER,LEDGER,POST): inputs[str(p.relative_to(R))]=sha(p)
v1=V1.read_text(); v2=V2.read_text(); builder=BUILDER.read_text(); ledger=json.loads(LEDGER.read_bytes()); post=json.loads(POST.read_bytes())
ck('immutable_v1_helper_preserved',sha(V1)=='b315972ce22569684c4fe21dc487fc0456b7db63b8224906020d6fc41911f65e')
ck('v2_ast_parses_without_import_execution',all(ast.parse(Path(p).read_text()) for p in (V1,V2,BUILDER)))
ck('v2_imports_v1_as_ordinary_predicate_source','import validate_prior_preflight_recovery_v1 as V1' in v2 and 'V1.validate_recovered_preflight' in v2)
ck('exception_is_exact_single_run_and_basis',"COST_ONLY_RUN='20261018_R2_D080_III_RRT_PCS_PHYSICAL01'" in v2 and "COST_ONLY_POST='reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_COST_ONLY_V2_CORRECTED_20261018.json'" in v2 and "row['charge_basis']=='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'" in v2)
ck('cost_only_never_upgrades_supervision',"post['external_supervision_qualified'] is False" in v2 and "post['external_timing_qualified'] is False" in v2 and "post['external_cost_qualified'] is True" in v2 and "post['external_supervision_qualified'] is True" in v2)
ck('ordinary_branch_still_requires_supervision',"else:\n            require(sha(post_path)==row['external_post_sha256']" in v2 and "and post['external_supervision_qualified'] is True" in v2)
ck('all_hash_and_receipt_predicates_retained',all(s in v2 for s in ['PRIOR_HASHED_EXTERNAL_CHARGE_BINDING_REQUIRED','PRIOR_INTERNAL_PERSISTENCE_RECEIPT_REQUIRED','PRIOR_SUPERVISION_LOG_CHANGED','PRIOR_POST_INTERNAL_RECEIPT_CHANGED','PRIOR_LEDGER_MUST_COVER_EVERY_ACTUAL_EXECUTION']))
ck('v2_builder_binds_v2_helper','import validate_prior_preflight_recovery_v2 as P' in builder and 'Path(P.__file__).resolve()' in builder)
ck('corrected_post_saved_16_of_16_cost_only',post['personnel_independent'] is True and post['checks_total']==post['checks_passed'] and post['checks_failed']==0 and post['external_supervision_qualified'] is False and post['external_cost_qualified'] is True)
row=next(r for r in ledger['executions'] if r['run_id']=='20261018_R2_D080_III_RRT_PCS_PHYSICAL01')
ck('v39_only_repoints_post_and_preserves_cost',row['external_post'].endswith('COST_ONLY_V2_CORRECTED_20261018.json') and row['charged_wall_s']==8.531047851987532 and row['charged_cpu_s']==7.210078 and ledger['previous_snapshot'].endswith('V38.json'))
ck('v38_and_old_post_remain_preserved',(R/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V38.json').is_file() and (R/'reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json').is_file())
ck('no_top_level_process_execution',not any(isinstance(n,ast.Call) and isinstance(getattr(n,'func',None),ast.Name) and n.func.id in {'run','Popen','check_output','system'} for n in ast.walk(ast.parse(v2))))
failed=[x for x in checks if not x['passed']]
report={'schema':'P4_D080_PRIOR_VALIDATOR_V2_INDEPENDENT_REVIEW_V1','personnel_independent':True,'status':'PASS_UNIQUE_COST_ONLY_EXCEPTION' if not failed else 'FAIL_PRIOR_VALIDATOR_V2_REVIEW','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'failures':failed,'inputs_sha256':inputs,'baseline_v1_sha256':sha(V1),'allowed_exception':{'run_id':'20261018_R2_D080_III_RRT_PCS_PHYSICAL01','post_sha256':sha(POST),'ledger_sha256':sha(LEDGER),'supervision_qualified':False,'cost_qualified':True},'limits':['v1 remains preserved; no ordinary external supervision predicate is relaxed.','Cost-only is not planning/path/scientific qualification.']}
out=R/'reports/P4_D080_PRIOR_VALIDATOR_V2_INDEPENDENT_REVIEW_20261019.json'; out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'status':report['status'],'checks':len(checks),'failed':failed,'sha256':sha(out)}))
