#!/usr/bin/env python3
"""Thin stdlib-only AST/source audit; never executes reviewed bookkeeping."""
import ast
import copy
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
checks=[];inputs={}
def raw(n):
 v=(R/n).read_bytes();inputs[n]=hashlib.sha256(v).hexdigest();return v
def source(n):return raw(n).decode()
def ck(n,v):checks.append(dict(name=n,passed=bool(v)))
def fn(tree,name):return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
def eq(a,b):return ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
B='scripts/p4_d080/build_v_pcs_local_v1_draft.py';H='scripts/p4_d080/validate_prior_preflight_recovery_v1.py'
b=ast.parse(source(B));hs=source(H);h=ast.parse(hs)
ck('old_B_unchanged_and_helper_stable',inputs[B]=='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578' and inputs[H]=='b315972ce22569684c4fe21dc487fc0456b7db63b8224906020d6fc41911f65e')
x=fn(b,'validate_prior');y=copy.deepcopy(fn(h,'validate_prior'));y.args=x.args
ck('only_run_identity_localization_at_prior_entry',[ast.unparse(z)for z in y.body[:2]]==['RUN_NAME = run_name','RUN = Path(run_dir).resolve()'])
y.body=y.body[2:];loop=next(t for t in y.body if isinstance(t,ast.For) and ast.unparse(t.target)=='row');ix=next(i for i,t in enumerate(loop.body)if isinstance(t,ast.If)and 'RECOVERED_BASIS'in ast.unparse(t.test));seam=loop.body.pop(ix)
ck('only_new_early_dispatch_is_single_fixed_basis_and_continues',ast.unparse(seam)=="if row.get('charge_basis') == RECOVERED_BASIS:\n    validate_recovered_preflight(row, post_path, post, time_path, charge_path, charge, evidence)\n    continue")
ck('all_normal_prior_predicates_and_receipt_parser_identical_AST',eq(x,y) and eq(fn(b,'certificate_json'),fn(h,'certificate_json')))
ck('helper_imports_only_stdlib_and_no_top_level_calls',all(not isinstance(z,(ast.Import,ast.ImportFrom))or all(a.name.split('.')[0]in{'decimal','hashlib','json','math','pathlib'} for a in z.names)for z in h.body) and not any(isinstance(z,ast.Expr)and isinstance(z.value,ast.Call)for z in h.body))
special=ast.unparse(fn(h,'validate_recovered_preflight'))
ck('special_run_path_and_basis_exact_singleton',"RECOVERED_RUN = '20261018_R2_D080_V_RRT_PCS_BUILD01'"in ast.unparse(h) and "RECOVERED_BASIS = 'EXTERNAL_PREFLIGHT_TWO_OBSERVATION_ENVELOPE_ONCE'"in ast.unparse(h) and 'ONLY_SINGLE_EXPLICIT_V_BUILD01_PREFLIGHT_RECOVERY_ALLOWED'in special)
ck('special_requires_immutable_raw_four_null_receipt_exit1_false_supervision',all(t in special for t in ['IMMUTABLE_ORIGINAL_PREFLIGHT_EVIDENCE_CHANGED','ORIGINAL_MISSING_RECEIPT_NULL_HASHES_AND_FAIL_MUST_REMAIN','ORIGINAL_NONZERO_PREFLIGHT_GNUTIME_FIELDS_REQUIRED',"charge['execution_sha256'] is None","charge['receipt_sha256'] is None","charge['external_supervision_qualified'] is False"]))
ck('special_two_observation_Decimal_and_independent_recovery_certificate_required',all(t in special for t in ['FINITE_ORIGINAL_TWO_OBSERVATION_COSTS_REQUIRED','EXACT_DECIMAL_TWO_OBSERVATION_ENVELOPE_CHARGED_ONCE_REQUIRED',"post['external_supervision_qualified'] is False","post['external_cost_qualified'] is True","post['orphan_preflight_cost_observation_qualified'] is True","post['source_execution_created_during_attempt'] is False","post['saved_only_recovery'] is True","post['execution_sha256'] == row['execution_sha256'] == sha(execution_path)"]))
V37='reports/p4_full_audit/recovery_tools/append_preflight_recovery_v37_saved_only_20261018.py';v=source(V37)
ck('V37_exact_saved_singleton_no_new_runtime_and_old54_rows_retained',all(t in v for t in ["assert sha(EP) == '6e6b3d9f44a51a2ee2d3dd0f35efce10dc6d2d1090c74d5a13552cc93cd900df'","rows = sorted([*old['executions'], entry]",'count=55, science_count=39, engineering_count=16','actual_runtime_execution_records_excluding_saved_only_recovery=54',"assert ledger['measured_internal_own_cost_sum'] == old['measured_internal_own_cost_sum']","assert all(sha(n)==v for n,v in old_hashes.items())","with (R/p).open('x')",'assert len(table)==211 and len(fields)==240']))
V6='reports/p4_full_audit/recovery_tools/append_external_cost_snapshot_d080_v6_20261018.py';V7='reports/p4_full_audit/recovery_tools/append_external_cost_snapshot_d080_v7_20261018.py';v6=source(V6);v7=source(V7)
restored=v7.replace('successor ledger v7:','successor ledger v6:',1).replace("math.fsum(r[k] for r in rows if not r.get('saved_only_preflight_cost_recovery', False))","math.fsum(r[k] for r in rows)",1)
newlines="    'saved_only_preflight_recovery_count': sum(bool(r.get('saved_only_preflight_cost_recovery', False)) for r in rows),\n    'actual_runtime_execution_records_excluding_saved_only_recovery': sum(not r.get('saved_only_preflight_cost_recovery', False) for r in rows),\n    'count_meaning': 'Cost records include an explicitly labelled saved-only preflight recovery; actual runtime records exclude it.',\n"
restored=restored.replace(newlines,'',1)
ck('v7_reverses_byte_exact_to_v6_after_only_measurement_filter_and_count_metadata',restored==v6 and "r.get('saved_only_preflight_cost_recovery', False)"in v7)
post='reports/P4_D080_ENV_V_RRT_PCS_BUILD01_RECOVERY_COST_INDEPENDENT_POST_20261018.json';p=json.loads(raw(post))
ck('saved_recovery_POST8_complete_with_explicit_false_supervision',inputs[post]=='8017f6d6986048ed94eaa2f776d73c48256c11d09b957e48a9583e0b3f321953' and p['checks_total']==p['checks_passed']==8 and p['checks_failed']==0 and p['external_supervision_qualified']is False and p['external_cost_qualified']is p['saved_only_recovery']is True)
failed=[c for c in checks if not c['passed']]
report=dict(schema='P4_D080_PREFLIGHT_RECOVERY_CHAIN_THIN_INDEPENDENT_PRE_V1',personnel_independent=True,status='PASS_THIN_RECOVERY_BOOKKEEPING'if not failed else'FAIL_THIN_RECOVERY_BOOKKEEPING',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,inputs_sha256=inputs,new_scientific_compile_binary_model_calls=0,historical_full_ledger_rehash_repeated=False,limits=['Only the fixed failed preflight is accepted with a saved-only two-observation cost index; no old successful path or budget standard is relaxed.','V37 bookkeeping and v7 are statically reviewed, not executed by this auditor.','All ordinary prior validation remains identical AST; root must bind and freeze the latest actual ledger before authorized execution.'])
out=R/'reports/P4_D080_PREFLIGHT_RECOVERY_CHAIN_THIN_INDEPENDENT_PRE_20261018.json'
with out.open('x')as f:f.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps(dict(checks=len(checks),failed=failed,sha256=hashlib.sha256(out.read_bytes()).hexdigest())))
