#!/usr/bin/env python3
"""Saved-byte/AST only: identity/helper seams. No candidate import or execution."""
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PRESERVE=ROOT/'work/preserved_v_build01_and_source01_before_build02_prior_helper_20261018'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)})
build=ROOT/'scripts/p4_d080/build_v_rrt_pcs_e2e_v2_draft.py';sup=ROOT/'scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v2_draft.py'
config=ROOT/'configs/p4_d080/v_rrt_pcs_e2e_build_v2.DRAFT.json';pre=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_BUILD02_EXECUTOR_PRE_DRAFT_20261018.md'
source=ROOT/'scripts/p4_d080/qualify_v_rrt_pcs_source01_v1_draft.py';ssup=ROOT/'scripts/p4_d080/supervise_v_rrt_pcs_source01_v1_draft.py'
sconfig=ROOT/'configs/p4_d080/v_rrt_pcs_source01_v1.DRAFT.json';spre=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_SOURCE01_PRE_DRAFT_20261018.md'
helper=ROOT/'scripts/p4_d080/validate_prior_preflight_recovery_v1.py'
manifest=load(PRESERVE/'manifest.json');d=load(config);sd=load(sconfig);old=load(PRESERVE/'configs/p4_d080/v_rrt_pcs_e2e_build_v1.DRAFT.json');osd=load(PRESERVE/'configs/p4_d080/v_rrt_pcs_source01_v1.DRAFT.json')
check('All8 pre-adaptation assets preserved by exact SHA',all(sha(PRESERVE/n)==v for n,v in manifest.items()))
oldnames=[n for n in manifest if 'source01'not in n.lower()]
check('Original BUILD01 runner supervisor DRAFT PRE remain current byte-identical',len(oldnames)==4 and all(sha(ROOT/n)==manifest[n]for n in oldnames))
for p in [build,sup,source,ssup,helper]:check('AST parse only '+p.name,isinstance(ast.parse(p.read_text()),ast.Module))
a=(PRESERVE/'scripts/p4_d080/build_v_rrt_pcs_e2e_v1_draft.py').read_text()
for x,y in [('20261018_R2_D080_V_RRT_PCS_BUILD01','20261018_R2_D080_V_RRT_PCS_BUILD02'),('v_rrt_pcs_e2e_build_v1.DRAFT.json','v_rrt_pcs_e2e_build_v2.DRAFT.json'),('P4_D080_ENV_V_RRT_PCS_BUILD_EXECUTOR_PRE_DRAFT_20261018.md','P4_D080_ENV_V_RRT_PCS_BUILD02_EXECUTOR_PRE_DRAFT_20261018.md'),('supervise_v_rrt_pcs_e2e_build_v1_draft.py','supervise_v_rrt_pcs_e2e_build_v2_draft.py')]:a=a.replace(x,y)
a=a.replace('import build_iii_rrt_pcs_e2e_v1_draft as I','import build_iii_rrt_pcs_e2e_v1_draft as I\nimport validate_prior_preflight_recovery_v1 as P').replace('SEAM_REVIEW,TEMPLATE]','SEAM_REVIEW,TEMPLATE,Path(P.__file__).resolve()]').replace('cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke','cpu=B.cpu;invoke=B.invoke').replace('\n\ndef frozen_assets(spec,protocol):','\n\ndef validate_prior(spec):\n    return P.validate_prior(spec,RUN_NAME,RUN)\n\n\ndef frozen_assets(spec,protocol):')
a=a.replace('(OWN[0],SUPERVISOR,PLAN,DEPENDENCIES)','(OWN[0],SUPERVISOR,PLAN,DEPENDENCIES,Path(P.__file__).resolve())')
check('Entire BUILD02 runner exact4 identity and helper-only substitutions',a==build.read_text())
a=(PRESERVE/'scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v1_draft.py').read_text().replace('20261018_R2_D080_V_RRT_PCS_BUILD01','20261018_R2_D080_V_RRT_PCS_BUILD02').replace('build_v_rrt_pcs_e2e_v1_draft.py','build_v_rrt_pcs_e2e_v2_draft.py')
check('Entire BUILD02 supervisor exact2 identity-only substitutions',a==sup.read_text())
a=(PRESERVE/'scripts/p4_d080/qualify_v_rrt_pcs_source01_v1_draft.py').read_text().replace('20261018_R2_D080_V_RRT_PCS_BUILD01','20261018_R2_D080_V_RRT_PCS_BUILD02').replace('P4_D080_ENV_V_RRT_PCS_BUILD01_SAVED_INDEPENDENT_POST','P4_D080_ENV_V_RRT_PCS_BUILD02_SAVED_INDEPENDENT_POST').replace('import qualify_iii_rrt_pcs_source01_v1_draft as I','import qualify_iii_rrt_pcs_source01_v1_draft as I\nimport validate_prior_preflight_recovery_v1 as P').replace('Path(B.__file__).resolve(), Path(B.lifecycle.__file__).resolve()]','Path(B.__file__).resolve(), Path(B.lifecycle.__file__).resolve(), Path(P.__file__).resolve()]').replace('\n\ndef preflight(spec, protocol):','\n\ndef validate_prior(spec):\n    return P.validate_prior(spec, RUN, ROOT / \'results/p4_full\' / RUN)\n\n\ndef preflight(spec, protocol):').replace('B.validate_prior(spec)','validate_prior(spec)')
check('Entire SOURCE01 runner exact BUILD02 and helper-only substitutions',a==source.read_text())
check('SOURCE01 supervisor unchanged byte-identical',sha(ssup)==manifest['scripts/p4_d080/supervise_v_rrt_pcs_source01_v1_draft.py'])
check('BUILD02 exact original2TU link objects stage budgets',all(d[k]==old[k]for k in ('stage_root','budget','working_budget','new_compile_calls','new_link_calls','commands','reused_objects','binary','source_transform_receipt','transformed_SVC_sha256','dependency_union_sha256','source_plan_sha256')))
check('BUILD02 all execution gates false and no science counters',all(d[k]is False for k in ('frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized'))and all(d[k]==0 for k in ('binary_execution_calls','query_calls','solve_calls','new_VI_candidate_constructions','formal_table_I_calls')))
check('Both priors remain unbound without new accounting',all(v['prior'][k]is None for v in (d,sd)for k in ('ledger','ledger_sha256','wall_s','cpu_s'))and d['independent_review_certificate']is None and sd['actual_charge_prior']is None)
check('SOURCE01 scientific request meshes caps exactly unchanged',sd['request']==osd['request']and sd['runtime_meshes_sha256']==osd['runtime_meshes_sha256']and sd['budget']==osd['budget']and sd['working_budget']==osd['working_budget'])
check('SOURCE01 actual BUILD02 POST binary unknown no anticipated pass',sd['build_assets']['execution'].endswith('V_RRT_PCS_BUILD02/execution.json')and 'V_RRT_PCS_BUILD02_SAVED_INDEPENDENT_POST'in sd['build_assets']['personnel_independent_POST']and all(sd['build_assets'][k]is None for k in ('execution_sha256','post_sha256','post_checks_total'))and sd['target']['binary_sha256']is None)
check('Both OWN bind exact current helper and metadata',all(v['bound_files_sha256'].get(str(helper))==sha(helper)and v['prior_validator_helper']=={'path':'scripts/p4_d080/validate_prior_preflight_recovery_v1.py','sha256':sha(helper),'interface':'validate_prior(spec,run_name,run_dir)'}for v in (d,sd)))
check('Both complete bound dictionaries current bytes',all(sha(n)==w for v in (d,sd)for n,w in v['bound_files_sha256'].items()))
check('Original B and lifecycle retained in both bindings',all(str(ROOT/n)in v['bound_files_sha256']for v in (d,sd)for n in ('scripts/p4_d080/build_v_pcs_local_v1_draft.py','scripts/build_p4_full_r2_abb_cbirrt_d_draft.py')))
check('BUILD02 own runner supervisor PRE bound',all(d['bound_files_sha256'].get(str(p))==sha(p)for p in (build,sup,pre)))
check('SOURCE01 own runner supervisor PRE bound',all(sd['bound_files_sha256'].get(str(p))==sha(p)for p in (source,ssup,spre)))
check('No direct binary or model call added by helper seam',all(x in build.read_text()for x in ('return P.validate_prior(spec,RUN_NAME,RUN)','cpu=B.cpu;invoke=B.invoke'))and 'return P.validate_prior(spec, RUN, ROOT / \'results/p4_full\' / RUN)'in source.read_text())
helper_tree=ast.parse(helper.read_text());helper_validate=next(n for n in helper_tree.body if isinstance(n,ast.FunctionDef)and n.name=='validate_prior')
check('Helper exact three-argument interface', [a.arg for a in helper_validate.args.args]==['spec','run_name','run_dir'])
check('Helper no imported non-stdlib model modules',all(not any(k in ast.unparse(n)for k in ('numpy','scipy','qualify_','build_v_','robot','ompl'))for n in helper_tree.body if isinstance(n,(ast.Import,ast.ImportFrom))))
run=ROOT/'results/p4_full'/d['run_name'];stage=Path(d['stage_root'])
check('New BUILD02 stage run sidecars all fresh',not stage.exists()and not run.exists()and not any(Path(str(run)+s).exists()for s in ('.supervision.time.txt','.supervision.jsonl','.supervision.stderr.log','.supervision.charge.json')))
check('Old orphan time charge metadata stderr remain present',all(Path(str(ROOT/'results/p4_full/20261018_R2_D080_V_RRT_PCS_BUILD01')+s).is_file()for s in ('.supervision.time.txt','.supervision.jsonl','.supervision.stderr.log','.supervision.charge.json')))
check('No false old runtime receipt created',not (ROOT/'results/p4_full/20261018_R2_D080_V_RRT_PCS_BUILD01').exists())
inputs=[build,sup,config,pre,source,ssup,sconfig,spre,helper,Path(__file__).resolve(),PRESERVE/'manifest.json']
result={'schema':'P4_D080_V_BUILD02_SOURCE01_PRIOR_SEAMS_SELF_STATIC_V1','personnel_independent':False,'candidate_imports':0,'compile_calls':0,'binary_execution_calls':0,'model_calls':0,'solve_calls':0,'checks_total':len(checks),'checks_passed':sum(x['passed']for x in checks),'checks_failed':sum(not x['passed']for x in checks),'checks':checks,'inputs_sha256':{str(p.relative_to(ROOT)):sha(p)for p in inputs},'status':'PASS_SELF_ONLY_NOT_INDEPENDENT_NOT_FROZEN'if all(x['passed']for x in checks)else 'FAIL_RETAINED','scope':'Identity and helper integration only; underlying prior-helper semantics require separate personnel-independent review; all old evidence retained.'}
out=ROOT/'reports/P4_D080_ENV_V_BUILD02_SOURCE01_PRIOR_SEAMS_SELF_STATIC_20261018.json'
with out.open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'status':result['status'],'passed':result['checks_passed'],'total':result['checks_total'],'failures':[x['name']for x in checks if not x['passed']],'sha256':sha(out)}))
