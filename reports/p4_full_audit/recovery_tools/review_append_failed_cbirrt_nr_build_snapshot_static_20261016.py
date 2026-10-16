#!/usr/bin/env python3
"""Independent read/AST/saved-table audit; never invokes the ledger writer."""
from pathlib import Path
import ast
import csv
import datetime
import hashlib
import itertools
import json
import math

ROOT=Path(__file__).resolve().parents[3]
SOURCE='reports/p4_full_audit/recovery_tools/append_failed_cbirrt_nr_build_snapshot_20261016.py'
WANT='2d5e9fc8ecd4252cf1da884888019f28af8b506eb6228607a724e3c4ce317f8c'
OUT=ROOT/'reports/P4_FULL_R2_FAILED_CBIRRT_NR_BUILD_LEDGER_INDEPENDENT_STATIC_REVIEW_20261016'
retained={};checks=[]
def raw(n):
    p=Path(n);p=p if p.is_absolute()else ROOT/p;b=p.read_bytes()
    retained[str(p)]=hashlib.sha256(b).hexdigest();return b
def read(n):return json.loads(raw(n))
def ck(n,ok):checks.append(dict(check=n,passed=bool(ok)))
text=raw(SOURCE).decode();tree=ast.parse(text,filename=SOURCE)
ck('exact reviewed source and AST parse only',hashlib.sha256(text.encode()).hexdigest()==WANT)
imports={a.name for n in tree.body if isinstance(n,ast.Import)for a in n.names}
froms={n.module for n in tree.body if isinstance(n,ast.ImportFrom)}
ck('stdlib-only no runner model process compiler import',imports=={'argparse','csv','hashlib','itertools','json','math'}and froms=={'pathlib','decimal'})
ck('explicit new entry engineering science classification agreement',"choices=('engineering', 'science')"in text and
   'ENGINEERING_BUILD_ONLY_'in text and 'ENTRY_KIND_CLASSIFICATION_MISMATCH'in text and
   'EXECUTION_ENGINEERING_FIELD_MISMATCH'in text)
ck('engineering requires query solve binary all explicit int zero',"for field in ('query_calls', 'solve_calls', 'binary_execution_calls')"in text and
   "type(e.get(field)) is int and e[field] == 0"in text and 'ENGINEERING_CANNOT_AUTHORIZE_SCIENCE'in text)
ck('formal VI counters cannot increase','NEW_FORMAL_OR_VI_CALLS'in text and 'formal_planning_calls'in text and 'new_VI_candidate_constructions'in text)
ck('explicit external POST SHA rather than merely file exists',"a.add_argument('--external-post-sha256', required=True)"in text and
   "sha(postp) == x.external_post_sha256"in text and 'COMPLETE_INDEPENDENT_POST_REQUIRED'in text)
ck('actual independent cost cert binds exact execution and time',"post['personnel_independent'] is True"in text and
   "post['external_supervision_qualified'] is True"in text and "post['execution_sha256'] == sha(ep)"in text and
   "post['external_time_sha256'] == sha(logp)"in text)
ck('exact Decimal conservative upper observed failed finite exit1',"wall = float(elapsed + Decimal('.01'))"in text and
   "cpu = float(user + system + Decimal('.02'))"in text and "fields_time[3] == '1'"in text and 'POST_UPPER_COST_MISMATCH'in text)
ck('external upper includes internal sample and execution cap','EXTERNAL_UPPER_BELOW_INTERNAL_SAMPLE'in text and 'EXECUTION_CAP_EXCEEDED'in text)
ck('prior external hashes and all costs verified without changing old rows','PRIOR_INDEPENDENT_CERTIFICATE_SHA_CHANGED'in text and
   'PRIOR_PARTIAL_EXTERNAL_REPLACEMENT'in text and 'PRIOR_CHARGED_SUM_MISMATCH'in text)
ck('new cost replaces own once distinct execution run IDs',"return row.get('charged_' + key, row[key])"in text and
   'EXECUTION_ALREADY_CHARGED'in text and 'RUN_ALREADY_CHARGED'in text and 'DISTINCT_EXECUTIONS_AND_RUN_IDS_REQUIRED'in text)
ck('all dates actual executions not old Oct15 prefix',"glob('*_R2_*/execution.json')"in text and
   "glob('20261015_R2_*/execution.json')"not in text and 'ALL_ACTUAL_R2_EXECUTIONS_REQUIRED'in text)
ck('orphan supervised attempt blocks next ledger','ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING'in text)
ck('explicit prior engineering science counts and successor increments','PRIOR_ENTRY_COUNTS_MISMATCH'in text and
   'SUCCESSOR_ENTRY_KIND_COUNTS_MISMATCH'in text and 'V19_CBIRRT_NR_BUILD_MUST_BE_29_SCIENCE_8_ENGINEERING'in text)
ck('original sample sums remain separately preserved','measured_internal_own_cost_sum'in text and 'science_wall_s'in text and
   'engineering_wall_s'in text and 'Historical unsupervised recording tail remains UNKNOWN'in text)
ck('211 rows all old columns unique immutable prefix twice checked','FULL211_OLD_COLUMN_CONTRACT_REQUIRED'in text and
   'HISTORICAL_COVERAGE_VALUES_CHANGED'in text and 'SAVED_HISTORICAL_COLUMNS_NOT_IDENTICAL'in text and
   'x.expected_old_columns >= 158'in text)
ck('all45 TableI cells original500x1000 preserved','ORIGINAL45_CELLS_22500_TRIALS_SCALE_REQUIRED'in text and
   "['II', 'III', 'IV', 'V', 'VI'], ['RRT', 'Bi-RRT', 'SBL'], ['RSS', 'PCS', 'NR']"in text and
   "r['original_repeats'] == '500'"in text and "r['original_duration_budget'] == '1000s/call'"in text)
ck('related item IDs explicit distinct existing not silent entire table pass','RELATED_ITEM_IDS_MUST_BE_DISTINCT_EXISTING_OBLIGATIONS'in text and
   'NO_NEW_EVIDENCE_FOR_THIS_OBLIGATION'in text and "related = row['item_id'] in x.related_item_ids"in text)
ck('all outputs exclusive preserved original inputs and byte exact mirrors',"with p.open('x')"in text and
   "with cp.open('x', newline='')"in text and "with mirror.open('xb')"in text and
   'INPUT_BYTES_CHANGED_BEFORE_APPEND'in text and 'INPUT_BYTES_CHANGED_AFTER_APPEND'in text and 'OUTPUT_MIRROR_BYTES_CHANGED'in text)
ck('VI974 and formal22500 exact obligations retained','VI974_EXHAUSTED_HISTORY_REQUIRED'in text and
   'FORMAL_ZERO_OR_R2_REMAINING_INVALID'in text and "l['formal_table_I_required_calls'] == 22500"in text)
original_source='reports/p4_full_audit/recovery_tools/append_external_cost_snapshot_v2_20261016.py'
original=ast.parse(raw(original_source));normal=ast.parse(text)
original.body[0].value=ast.Constant(value='same')
normal.body[0].value=ast.Constant(value='same')
extra_reasons={'EXACT_SAVED_FAILED_ENGINEERING_EVIDENCE_REQUIRED','FAILED_BUILD_POST_BOUNDARY_REQUIRED'}
removed=[];kept=[]
for node in normal.body:
    if isinstance(node,ast.Expr)and isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Name)and node.value.func.id=='require'and len(node.value.args)>1 and isinstance(node.value.args[1],ast.Constant)and node.value.args[1].value in extra_reasons:
        removed.append(node.value.args[1].value)
    else:kept.append(node)
normal.body=kept
for node in ast.walk(normal):
    if isinstance(node,ast.Constant)and node.value=='ACTUAL_FAILED_BUILD_FINITE_EXTERNAL_COST_REQUIRED':node.value='SUCCESSFUL_FINITE_NONNEGATIVE_EXTERNAL_COST_REQUIRED'
    if isinstance(node,ast.Compare)and isinstance(node.left,ast.Subscript)and isinstance(node.left.value,ast.Name)and node.left.value.id=='fields_time'and isinstance(node.left.slice,ast.Constant)and node.left.slice.value==3:
        if len(node.comparators)==1 and isinstance(node.comparators[0],ast.Constant)and node.comparators[0].value=='1':node.comparators[0].value='0'
ck('only intended failed-run changes exact independent AST reversal',set(removed)==extra_reasons and len(removed)==2 and ast.dump(normal,include_attributes=False)==ast.dump(original,include_attributes=False))
ck('successful previous writer and115 static proof preserved',hashlib.sha256(raw(original_source)).hexdigest()=='31be17ef58dc2319845a62dbb0fc27222855b501b37b5aaf933c257b7ddc460c'and
   hashlib.sha256(raw('reports/P4_FULL_R2_EXTERNAL_LEDGER_V2_INDEPENDENT_STATIC_REVIEW_20261016.json')).hexdigest()=='a9d9c5f3eda3360f3b2c889dfde382a754807f6cfe83c886c0be897fd58e1f24')
ck('hard reject all other failures and unqualified build',all(q in text for q in("e['run_id'] == '20261016_R2_ABB_CBIRRT_NR_BUILD01'","e['status'] == 'STOP_PREFIX_RETAINED'","e['exit_code'] == 0","e['compiler_reaped'] is True","e['compiler_group_members_after_cleanup'] == []","e['diagnostics'] == []","post['status'] == 'STOP_BUILD_DEPENDENCY_EVIDENCE_INCOMPLETE'","post['external_timing_qualified'] is True","post['external_cost_qualified'] is True","post['engineering_build_qualified'] is False","post['external_time_fields'] == fields_time")))
post_name='reports/P4_FULL_R2_ABB_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST_20261016.json'
post=read(post_name);execution=read(post['execution']);fields_time=raw(post['external_time']).decode().split()
ck('actual genuine personnel-independent failed cost certificate',hashlib.sha256(raw(post_name)).hexdigest()=='f4d04c1de62acfeea83e94137f146947db2f3f6045ab2b7ee1a544b61b82fed1'and
   post['status']=='STOP_BUILD_DEPENDENCY_EVIDENCE_INCOMPLETE'and post['checks_total']==post['checks_passed']==13720 and post['checks_failed']==0 and
   post['personnel_independent']is post['external_supervision_qualified']is post['external_timing_qualified']is post['external_cost_qualified']is True and post['engineering_build_qualified']is False and
   post['execution_sha256']==hashlib.sha256(raw(post['execution'])).hexdigest()and post['external_time_sha256']==hashlib.sha256(raw(post['external_time'])).hexdigest()and
   post['external_time_fields']==fields_time==['33.95','44.43','11.03','1']and post['upper_wall_s']==33.96 and post['upper_cpu_s']==55.48)
ck('actual stopped execution compiler0 group empty non-science',execution['status']=='STOP_PREFIX_RETAINED'and execution['exit_code']==0 and execution['compiler_reaped']is True and execution['compiler_group_members_after_cleanup']==[]and execution['diagnostics']==[]and
   all(execution[k]==0 for k in('query_calls','solve_calls','binary_execution_calls','formal_table_I_calls','new_VI_candidate_constructions')))
ck('no output V19 or new coverage generated by independent review',not(ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V19.json').exists()and not(ROOT/'reports/P4_FULL_R2_CBIRRT_NR_BUILD_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv').exists())

old=read('results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V18.json')
ck('actual V18 count science engineering36=29+7',len(old['executions'])==old['count']==36 and
   old['science_count']==sum(not r['engineering_only']for r in old['executions'])==29 and
   old['engineering_count']==sum(r['engineering_only']for r in old['executions'])==7)
for row in old['executions']:
    ck('actual old execution SHA '+row['run_id'],hashlib.sha256(raw(row['execution'])).hexdigest()==row['execution_sha256'])
    if 'charged_wall_s'in row:
        cert=read(row['external_post']);time=raw(row['external_time'])
        ck('actual old external cert '+row['run_id'],hashlib.sha256(raw(row['external_post'])).hexdigest()==row['external_post_sha256']and
           hashlib.sha256(time).hexdigest()==row['external_time_sha256']and cert['personnel_independent']is cert['external_supervision_qualified']is True and
           cert['execution_sha256']==row['execution_sha256']and cert['upper_wall_s']==row['charged_wall_s']and cert['upper_cpu_s']==row['charged_cpu_s'])
for k,wanted in [('wall_s',685.555705375994),('cpu_s',542.4289229999999)]:
    ck('actual V18 charged fsum '+k,math.fsum(r.get('charged_'+k,r[k])for r in old['executions'])==old['conservative_r2_sum_'+k]==wanted)
cp='reports/P4_FULL_R2_CBIRRT_D_PATH_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
raw(cp)
with(ROOT/cp).open(newline='')as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
ck('actual prior coverage211 rows158 unique columns',len(rows)==len({r['item_id']for r in rows})==211 and len(fields)==len(set(fields))==158)
formal=[r for r in rows if r['item_id'].startswith('P4-T18-')]
expected=set(itertools.product(['II','III','IV','V','VI'],['RRT','Bi-RRT','SBL'],['RSS','PCS','NR']))
ck('actual full45cells500repeat1000sec input coverage',len(formal)==45 and
   {tuple(r['item_id'].removeprefix('P4-T18-').split('_'))for r in formal}==expected and
   all(r['original_repeats']=='500'and r['original_duration_budget']=='1000s/call'for r in formal))
for n,h in list(retained.items()):ck('all read input bytes unchanged '+n,hashlib.sha256(Path(n).read_bytes()).hexdigest()==h)
failed=[r for r in checks if not r['passed']]
report=dict(schema='P4_FAILED_CBIRRT_NR_BUILD_LEDGER_INDEPENDENT_STATIC_REVIEW_V1',status='PASS_FAILED_ENGINEERING_ALL_DATE_COST_LEDGER_STATIC_REVIEW'if not failed else'FAIL_STATIC_REVIEW',
   generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of ledger author',personnel_independent=True,
   checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),failures=failed,checks=checks,source_sha256=WANT,
   actual_prior_ledger_count=36,actual_prior_science_count=29,actual_prior_engineering_count=7,actual_prior_coverage_rows=211,actual_prior_coverage_columns=158,
   old_columns_must_remain_identical=True,retained_sha256=retained,new_scientific_calls=0,runner_import_calls=0,writer_invocations=0,
   concrete_protocol_prior_ledger_or_claim_created=0,compile_calls=0,
   limitations=['Static source plus saved old36execution/211x158 coverage checks only. No new ledger or science has been generated.','Actual successor records STOP as engineering only. Actual independent failure/cost certificate exists and must be bound by explicit SHA and exact exit1; root chooses related items. No build success or runtime authorization.','Original successful writer remains unchanged. This separate failed engineering writer increments engineering only and preserves scientific/formal/VI counts.'])
with OUT.with_suffix('.json').open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
with OUT.with_suffix('.md').open('x')as f:f.write('# R2 失败CBiRRT_NR跨日期成本账工具独立静态审查\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(len(checks))+'。仅源码/AST和已保存V18的36项及211×158范围表读取；未调用新账工具。\n\n'+
   '显式engineering/science、全日期execution、独立POST固定SHA与GNUtime身份、成本替换一次、原列前缀守恒、45单元×500、VI974余0、正式22500义务均有硬门。实际STOP及费用已独立核证；本审查未执行写账工具，V19须由root实际追加，不授予工程通过。\n')
print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed)),ensure_ascii=False))
