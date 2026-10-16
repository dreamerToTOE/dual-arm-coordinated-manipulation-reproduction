"""Audit immutable crash history and V21 BUILD03 ledger; saved evidence only.

Prepare/read/AST is not an execution. Requires actual successful BUILD03 and
personnel independent POST; never creates model/protocol/claim or science.
"""
from pathlib import Path
from decimal import Decimal
import collections
import csv
import datetime
import hashlib
import itertools
import json
import math
import os
import re
import subprocess
import tarfile
import time

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
OUT=ROOT/'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V21.json'
BASE=ROOT/'results/p4_full/20261015_RECOVERY_BASELINE_MANIFEST.json'
TREES=ROOT/'results/p4_full/20261015_RECOVERY_EXISTING_WORKTREES.json'
ARCHIVE=Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/work/recovery_20261015/preexisting_uncommitted.tar.gz')
start_wall=time.monotonic();start_cpu=time.process_time()
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(path,*args):return subprocess.check_output(['git','-C',str(path),*args],env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'}).decode()
def mismatch_file(p,h,size=None):
    p=Path(p)
    if not p.is_file():return {'path':str(p),'reason':'MISSING'}
    actual=sha(p);n=p.stat().st_size
    if actual!=h or (size is not None and n!=size):return {'path':str(p),'expected_sha256':h,'actual_sha256':actual,'expected_bytes':size,'actual_bytes':n}
    return None
def csvread(p):
    with Path(p).open(newline='') as f:
        rd=csv.DictReader(f);return rd.fieldnames,list(rd)
def arithmetic(values,stored):
    n=len(values);seq=sum(values);ref=math.fsum(values);u=2**-53;gamma=(n-1)*u/(1-(n-1)*u);bound=gamma*math.fsum(abs(x) for x in values)+.5*math.ulp(ref)
    return {'n':n,'stored_sequential_sum':stored,'recomputed_sequential_sum':seq,'faithfully_summed_reference':ref,'absolute_difference':abs(seq-ref),'binary64_forward_rounding_bound':bound,'within_rounding_bound':abs(seq-ref)<=bound,'stored_value_reproduced_exactly':seq==stored}

b=read(BASE);v2path=ROOT/'results/p4_full/20261015_RECOVERY_IMMUTABLE_VERIFICATION_V2.json';v2=read(v2path)
oldm=[x for p,h in b['files'].items() if (x:=mismatch_file(ROOT/p,h))]
crash=b['preexisting_uncommitted']['files'];crashm=[x for f in crash if (x:=mismatch_file(ROOT/f['path'],f['sha256'],f['bytes']))]
expected_tar={f['path']:f for f in crash};archive_m=[]
with tarfile.open(ARCHIVE,'r:gz') as tar:
    members=[x for x in tar.getmembers() if x.isfile()];seen=collections.Counter(x.name for x in members)
    for member in members:
        f=expected_tar.get(member.name)
        if f is None:archive_m.append({'path':member.name,'reason':'UNEXPECTED_FILE'});continue
        content=tar.extractfile(member).read();actual=hashlib.sha256(content).hexdigest()
        if actual!=f['sha256'] or len(content)!=f['bytes']:archive_m.append({'path':member.name,'expected_sha256':f['sha256'],'actual_sha256':actual,'expected_bytes':f['bytes'],'actual_bytes':len(content)})
    for path in expected_tar:
        if seen[path]!=1:archive_m.append({'path':path,'reason':'EXPECTED_ONCE','actual_occurrences':seen[path]})
archive={'path':str(ARCHIVE),'expected_sha256':b['snapshot_archive_sha256'],'actual_sha256':sha(ARCHIVE),'sha_matches':sha(ARCHIVE)==b['snapshot_archive_sha256'],'file_members':len(members),'archive_member_mismatches':archive_m,'read_policy':'Stream file member bytes only; no extraction or overwrite.'}

other=[];otherm=[]
for saved in read(TREES):
    path=Path(saved['path'])
    if path==ROOT:continue
    head=git(path,'rev-parse','HEAD').strip();status=git(path,'status','--porcelain=v1','--untracked-files=all');fm=[]
    for name,h in saved['uncommitted_files'].items():
        if x:=mismatch_file(path/name,h):fm.append(x)
    result={'path':str(path),'expected_head':saved['head'],'actual_head':head,'head_matches':head==saved['head'],'status_matches':status==saved['status'],'preserved_uncommitted_files':len(saved['uncommitted_files']),'uncommitted_mismatches':fm}
    other.append(result)
    if not result['head_matches'] or not result['status_matches'] or fm:otherm.append(result)


old_csv=ROOT/'reports/P4_FULL_R2_CBIRRT_NR_BUILD02_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
new_csv=ROOT/'reports/P4_FULL_R2_CBIRRT_NR_BUILD03_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
oh,orr=csvread(old_csv);nh,nrr=csvread(new_csv)
coverage_m=[]
if len(nrr)!=211 or len({r['item_id'] for r in nrr})!=211:coverage_m.append('211_UNIQUE')
if nh[:len(oh)]!=oh:coverage_m.append('HISTORICAL_COLUMNS')
if [r['item_id'] for r in orr]!=[r['item_id'] for r in nrr]:coverage_m.append('ID_ORDER')
for a,z in zip(orr,nrr):
    for col in oh:
        if a[col]!=z[col]:coverage_m.append({'item':a['item_id'],'column':col})
formal=[r for r in nrr if r['item_id'].startswith('P4-T18-')]
expected=set(itertools.product(['II','III','IV','V','VI'],['RRT','Bi-RRT','SBL'],['RSS','PCS','NR']))
if {tuple(r['item_id'].removeprefix('P4-T18-').split('_')) for r in formal}!=expected:coverage_m.append('45_CELLS')
for r in formal:
    if r['original_repeats']!='500' or r['original_duration_budget']!='1000s/call':coverage_m.append({'item':r['item_id'],'reason':'FORMAL_SCALE'})
ledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V21.json';ledger=read(ledger_path);oldledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V20.json';oldledger=read(oldledger_path);lm=[]
rows=ledger['executions'];expected_ids={r['run_id'] for r in oldledger['executions']}|{'20261016_R2_ABB_CBIRRT_NR_BUILD03'}
if {r['run_id'] for r in rows}!=expected_ids or len(rows)!=39:lm.append('DISTINCT39_EXECUTIONS')
for r in rows:
    p=ROOT/r['execution'];e=read(p)
    if sha(p)!=r['execution_sha256'] or e['wall_s']!=r['wall_s'] or e['cpu_s']!=r['cpu_s']:lm.append({'run':r['run_id'],'reason':'EXECUTION_HASH_OR_OWN_COST'})
for k in ['wall_s','cpu_s']:
    value=math.fsum(r.get('charged_'+k,r[k]) for r in rows)
    if ledger['conservative_r2_sum_'+k]!=value:lm.append({'field':k,'reason':'FSUM_EXACT'})
    if ledger['r2_remaining'][k]!=ledger['r2_caps'][k]-value:lm.append({'field':k,'reason':'REMAINING'})
tail=next(r for r in rows if r['run_id']=='20261016_R2_ABB_CBIRRT_NR_BUILD03')
post=read(ROOT/tail['external_post'])
pe=read(ROOT/tail['execution'])
if ledger['science_count']!=29 or ledger['engineering_count']!=10:lm.append('EXPECTED29_SCIENCE10_ENGINEERING')
if len(oh)!=166 or len(nh)!=170:coverage_m.append('EXPECTED166_TO170_COLUMNS')
if pe['status']!='BUILT_NOT_QUERIED' or pe['classification']!='ENGINEERING_BUILD_ONLY_ORIGINAL_CBIRRT_NR_WITH_EXISTING_PHYSICAL_GD_SEAM' or tail['engineering_only']is not True:lm.append('BUILD03_ENGINEERING_CLASSIFICATION_OR_STATUS')
if pe['schema']!='P4_R2_ABB_CBIRRT_NR_ENGINEERING_EXECUTION_V4' or pe['run_id']!='20261016_R2_ABB_CBIRRT_NR_BUILD03' or pe['exit_code']!=0 or pe['compiler_reaped']is not True or pe['diagnostics']!=[] or pe.get('compiler_group_members_after_cleanup')!=[]:lm.append('BUILD03_COMPILER_EXIT_REAP_EMPTY_GROUP_OR_EVIDENCE_GATE')
for field in ('query_calls','solve_calls','binary_execution_calls','formal_table_I_calls','new_VI_candidate_constructions'):
    if type(pe.get(field))is not int or pe[field]!=0:lm.append({'field':field,'reason':'ENGINEERING_RUNTIME_OR_FORMAL_CALL'})
expected_post='reports/P4_FULL_R2_ABB_CBIRRT_NR_BUILD03_ROOT_INDEPENDENT_POST_20261016.json'
if tail['external_post']!=expected_post or post['schema']!='P4_CBIRRT_NR_BUILD03_ROOT_INDEPENDENT_POST_V1' or post['status']!='PASS_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST' or post.get('engineering_build_qualified')is not True:lm.append('ACTUAL_BUILD03_PERSONNEL_INDEPENDENT_SUCCESS_POST_REQUIRED')
if post['checks_total']!=post['checks_passed'] or post['checks_total']<=0 or post['checks_failed']!=0 or post.get('failures')!=[]:lm.append('ENGINEERING_INDEPENDENT_POST_NOT_COMPLETE')
protocol=read(ROOT/pe['protocol']);stage=Path(protocol['stage_root']);manifest_path=Path(protocol['build_root'])/'manifest.json';manifest=read(manifest_path)
if manifest!={**pe,'engineering_execution':tail['execution']}:lm.append('BUILD03_REAL_MANIFEST_EXECUTION_EXACT')
if sha(Path(pe['binary']))!=pe['binary_sha256'] or Path(pe['binary']).read_bytes()[:4]!=b'\x7fELF':lm.append('BUILD03_BINARY_HASH_OR_ELF_CHANGED')
for field,expected_path in [('execution',ROOT/tail['execution']),('manifest',manifest_path),('protocol',ROOT/pe['protocol']),('claim',ROOT/pe['claim']),('receipt',ROOT/'results/p4_full/20261016_R2_ABB_CBIRRT_NR_BUILD03.supervision.charge.json'),('internal_receipt',ROOT/'results/p4_full/20261016_R2_ABB_CBIRRT_NR_BUILD03/cost_receipt.json')]:
    observed=Path(post[field]);observed=observed if observed.is_absolute()else ROOT/observed
    if observed.resolve()!=expected_path.resolve() or sha(observed)!=post[field+'_sha256']:lm.append({'field':field,'reason':'BUILD03_POST_REAL_LINK_HASH'})
if pe['bound_files_sha256']!=pe['bound_files_after_sha256']:lm.append('BUILD03_BOUND_MAP_CHANGED')
for name,want in pe['bound_files_sha256'].items():
    p=Path(name);p=p if p.is_absolute()else ROOT/p
    if sha(p)!=want:lm.append({'path':name,'reason':'BUILD03_BOUND_ASSET_CHANGED'})
stdout_path=ROOT/pe['compiler_dependency_stdout'];stdout=stdout_path.read_bytes()
if pe['compiler_dependency_stdout']!='results/p4_full/20261016_R2_ABB_CBIRRT_NR_BUILD03/compile.stdout' or not stdout or not stdout.endswith(b'\n') or sha(stdout_path)!=pe['compiler_dependency_stdout_sha256'] or len(stdout)!=pe['compiler_dependency_stdout_bytes'] or sha(stdout_path)!=post['compiler_stdout_sha256']:lm.append('BUILD03_COMPLETE_ORIGINAL_DEPENDENCY_STDOUT_CHANGED')
# Independent Make lexer: only saved compiler output is parsed, never make/eval
# or the builder's parser. Reconstruct byte offsets for all physical LF lines.
lexer=re.compile(rb'(?:\\[ \t#:\\]|\$\$|[^ \t\r\n\\#$:\x00-\x1f\x7f])+|:')
def rule_tokens(logical):
    found=list(lexer.finditer(logical));pos=0;values=[]
    for match in found:
        if logical[pos:match.start()].strip(b' \t'):raise ValueError('UNPARSED_SAVED_MAKE_BYTES')
        value=match.group();pos=match.end()
        if value!=b':':value=re.sub(rb'\\([ \t#:\\])|\$\$',lambda m:m.group(1)if m.group(1)is not None else b'$',value)
        values.append(value)
    if logical[pos:].strip(b' \t')or values.count(b':')!=1 or values.index(b':')!=1 or len(values)<3:raise ValueError('EXACT_SAVED_MAKE_RULE_REQUIRED')
    return os.fsdecode(values[0]),[os.fsdecode(v)for v in values[2:]]
def absolute(name):
    p=Path(name);return(p if p.is_absolute()else ROOT/p).resolve()
rules=[];offset=0;begin=0;pieces=[]
for physical in stdout.splitlines(keepends=True):
    if not physical.endswith(b'\n')or b'\r'in physical:raise ValueError('COMPLETE_SAVED_LF_LINE_REQUIRED')
    body=physical[:-1];slashes=len(body)-len(body.rstrip(bytes([92])));offset+=len(physical)
    if slashes%2:pieces.append(body[:-1]+b' ');continue
    pieces.append(body);target,names=rule_tokens(b''.join(pieces));rules.append((begin,offset,target,names));begin=offset;pieces=[]
if len(rules)!=6 or pieces or begin!=len(stdout):lm.append('BUILD03_EXACT6_COMPLETE_STDOUT_RULES_NO_FILL')
sources=[ROOT/'baselines/p4_full/geometry_consistent/abb_cbirrt_nr_driver_draft.cpp',ROOT/'baselines/p4_full/geometry_consistent/abb_nr_interface_kernel_draft.cpp',*[stage/n for n in protocol['linked_author_cpp']]]
expected_sources={str(p.resolve())for p in sources};actual_sources=collections.Counter();translation_units={};bindings=[];slices={};dependencies={}
for index,(begin,end,target,names)in enumerate(rules):
    resolved=[absolute(name)for name in names];source=str(resolved[0]);fragment=stdout[begin:end]
    if absolute(target)!=Path(pe['binary']).resolve() or source not in expected_sources or source in translation_units:lm.append('BUILD03_RULE_TARGET_OR_DISTINCT_TU')
    translation_units[source]=[str(p)for p in resolved]
    for p in resolved:
        if str(p)in expected_sources:actual_sources[str(p)]+=1
        dependencies[str(p)]=sha(p)
    name='dependency_stdout_slices/'+str(index)+'_'+Path(source).name+'.d';p=stage/name;digest=hashlib.sha256(fragment).hexdigest();slices[name]=digest
    if p.read_bytes()!=fragment or sha(p)!=digest:lm.append('BUILD03_DERIVED_SLICE_EXACT_RAW_BYTES')
    bindings.append(dict(index=index,source=source,actual_target=target,raw_stdout_offset_begin=begin,raw_stdout_offset_end=end,raw_bytes=len(fragment),raw_sha256=digest,derived_slice=name,derived_slice_sha256=digest,compiler_created_individual_d_file=False,dependencies_count=len(resolved)))
if len(expected_sources)!=6 or set(translation_units)!=expected_sources or actual_sources!=collections.Counter({q:1 for q in expected_sources}) or dict(actual_sources)!=pe['actual_source_dependency_occurrences']:lm.append('BUILD03_SIX_REAL_TU_COVERAGE_ONCE_NO_REPLACEMENT')
if bindings!=pe['compiler_dependency_rule_bindings'] or bindings!=post['actual_dependency_rule_bindings'] or translation_units!=pe['actual_dependency_translation_units'] or dependencies!=pe['actual_dependencies_sha256'] or pe['unfrozen_protected_dependencies']!=[] or post['unfrozen_protected_dependencies']!=[]:lm.append('BUILD03_REAL_RULES_SAVED_MAP_AND_INDEPENDENT_POST_BINDINGS')
if slices!=pe['compiler_dependency_files_sha256'] or slices!=pe['compiler_dependency_files_after_sha256'] or set((stage/'dependency_stdout_slices').glob('*'))!={stage/n for n in slices}:lm.append('BUILD03_DERIVED6_SLICE_SET_HASH_BEFORE_AFTER')
command=pe['command']
if command[0]!='/usr/bin/x86_64-linux-gnu-g++-11' or command[1:4]!=['-MD','-MF','-'] or [z for z in command if z.endswith('.cpp')]!=[str(p)for p in sources] or command[-2:]!=['-o',pe['binary']]:lm.append('BUILD03_UNIQUE_REAL_MULTI_TU_COMMAND')
# BUILD01 retains its original failed status, single overwritten .d evidence,
# cost-qualified-but-engineering-unqualified POST and bytes via old V20 rows.
failed_row=next(r for r in rows if r['run_id']=='20261016_R2_ABB_CBIRRT_NR_BUILD01');failed_e=read(ROOT/failed_row['execution']);failed_p=read(ROOT/failed_row['external_post'])
if failed_e['status']!='STOP_PREFIX_RETAINED' or failed_e['termination_reason']!="RuntimeError('ONE_COMPLETE_MD_FILE_PER_TRANSLATION_UNIT_REQUIRED')" or failed_p['status']!='STOP_BUILD_DEPENDENCY_EVIDENCE_INCOMPLETE' or failed_p['engineering_build_qualified']is not False:lm.append('BUILD01_FAILED_HISTORY_MUST_REMAIN')
# BUILD02's six raw rules succeeded, but its five unfrozen actual PQP headers
# still caused STOP. Bind that failure and its cost-only independent POST;
# this new successful build cannot rewrite the old scientific/engineering gate.
failed2_row=next(r for r in rows if r['run_id']=='20261016_R2_ABB_CBIRRT_NR_BUILD02');failed2_e=read(ROOT/failed2_row['execution']);failed2_p=read(ROOT/failed2_row['external_post'])
if sha(ROOT/failed2_row['execution'])!='dcc96bbef72e47e663e51eb2dcbe8ae8f1bb99cef1e31d5eabad17f056fe15df' or failed2_e['status']!='STOP_PREFIX_RETAINED' or failed2_e['termination_reason']!="RuntimeError('ACTUAL_PROTECTED_DEPENDENCY_NOT_IN_FROZEN_MANIFEST')" or sha(ROOT/failed2_row['external_post'])!='56a9800f2b7fd70c71e52ebe088c8a870406f46ec60d8f85efb1df3d1cea9737' or failed2_p['status']!='STOP_BUILD_PROTECTED_DEPENDENCY_UNFROZEN' or failed2_p['engineering_build_qualified']is not False or failed2_p['external_supervision_qualified']is not True:lm.append('BUILD02_FAILED_HISTORY_AND_COST_ONLY_POST_MUST_REMAIN')
for name,want in {
    'reports/p4_full_audit/recovery_tools/audit_preservation_v20.py':'203a565328e4671ed804bc694d7e01adf2c9284765db8e806985a9800e7c811d',
    'reports/p4_full_audit/recovery_tools/audit_preservation_v20_failed_build_20261016.py':'aae496e59ac02a1a393ed327078f5a62811866e303e2877e61d7df9807ceb5c5',
}.items():
    if sha(ROOT/name)!=want:lm.append({'path':name,'reason':'OLD_V20_SUCCESS_DRAFT_OR_REAL_FAILURE_AUDIT_SOURCE_CHANGED'})

related={'P4-T03','P4-T05','P4-T09','P4-T11','P4-T17','P4-T25'}
if set(ledger.get('coverage_related_item_ids',[]))!=related:coverage_m.append('EXPLICIT_II_NR_ENGINEERING_RELATED_IDS_REQUIRED')
for row in nrr:
    if row['item_id']not in related and (row['v21_status']!='NO_NEW_EVIDENCE_FOR_THIS_OBLIGATION' or row['v21_execution']!='NOT_APPLICABLE'):coverage_m.append({'item':row['item_id'],'reason':'UNRELATED_ENGINEERING_EVIDENCE'})
timep=ROOT/tail['external_time']
elapsed,user,system,exitstatus=timep.read_text().split()
if sha(ROOT/tail['external_post'])!=tail['external_post_sha256'] or sha(timep)!=tail['external_time_sha256']:lm.append('EXTERNAL_HASH_CHANGED')
if not post['external_supervision_qualified'] or not post['personnel_independent'] or post['checks_failed']!=0:lm.append('EXTERNAL_POST_NOT_QUALIFIED')
if exitstatus!='0' or tail['charged_wall_s']!=float(Decimal(elapsed)+Decimal('.01')) or tail['charged_cpu_s']!=float(Decimal(user)+Decimal(system)+Decimal('.02')):lm.append('EXTERNAL_CHARGE_INCORRECT')
if tail['charged_wall_s']!=post['upper_wall_s'] or tail['charged_cpu_s']!=post['upper_cpu_s']:lm.append('EXTERNAL_POST_UPPER_MISMATCH')
if any(next(r for r in rows if r['execution']==o['execution'])!=o for o in oldledger['executions']):lm.append('OLD_LEDGER_ENTRIES_CHANGED')
if ledger['vi_B_consumed']!=oldledger['vi_B_consumed'] or ledger['vi_B_remaining']!=oldledger['vi_B_remaining']:lm.append('VI_B_CHANGED')
if ledger['vi_B_candidate_cap']!=974 or ledger['vi_B_remaining']['candidate_constructions']!=0:lm.append('VI974_EXHAUSTED')
if ledger['formal_table_I_calls']!=0 or ledger['formal_table_I_required_calls']!=22500:lm.append('FORMAL_CALLS')
history=[];hm=[]
for name in ['20261016_RECOVERY_IMMUTABLE_VERIFICATION_V20.json','20261016_RECOVERY_ACTUAL_LEDGER_V20.json']:
    p=ROOT/'results/p4_full'/name;blob=subprocess.check_output(['git','show','f9dba45:'+str(p.relative_to(ROOT))],cwd=ROOT)
    ok=hashlib.sha256(blob).hexdigest()==sha(p);history.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'matchesf9dba45':ok})
    if not ok:hm.append(name)
old_csv_blob=subprocess.check_output(['git','show','f9dba45:'+str(old_csv.relative_to(ROOT))],cwd=ROOT)
old_csv_ok=hashlib.sha256(old_csv_blob).hexdigest()==sha(old_csv)
for name,want in {
    'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V20.json':'19cf4ecb806532f0330b2a1e56ffde4475c07bd1011f0d2640578259c54fca0f',
    'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V20.json':'707e451cc2b1a42237f6ed2fd050526276a871149fc3ca64c35d09cb45c3f700',
    'reports/P4_FULL_R2_CBIRRT_NR_BUILD02_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv':'d22b3f6e10b9016bc9271fc7577e08cc72f5964da3ec894a3526e29b531492dc',
}.items():
    if sha(ROOT/name)!=want:hm.append({'path':name,'reason':'EXACT_ACTUAL_V20_FAILED_SNAPSHOT_CHANGED'})

history.append({'path':str(old_csv.relative_to(ROOT)),'sha256':sha(old_csv),'matchesf9dba45':old_csv_ok})
if not old_csv_ok:hm.append(str(old_csv.relative_to(ROOT)))
passed=not(oldm or crashm or archive_m or otherm or coverage_m or lm or hm) and archive['sha_matches'] and len(orr)==len(nrr)==211 and len(other)==5 and sum(x['preserved_uncommitted_files']for x in other)==13 and len(crash)==57
result={'schema':'P4_RECOVERY_IMMUTABLE_VERIFICATION_V21','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head_at_verification':git(ROOT,'rev-parse','HEAD').strip(),'analysis_source':str(Path(__file__).resolve()),'analysis_source_sha256':sha(__file__),'baseline_manifest':str(BASE.relative_to(ROOT)),'baseline_manifest_sha256':sha(BASE),'old_scientific_files':len(b['files']),'old_scientific_mismatches':oldm,'crash_uncommitted_files':len(crash),'crash_uncommitted_bytes':sum(f['bytes'] for f in crash),'crash_uncommitted_mismatches':crashm,'external_archive':archive,'other_worktrees':len(other),'other_uncommitted_files':sum(x['preserved_uncommitted_files'] for x in other),'other_worktree_results':other,'other_worktree_mismatches':otherm,'coverage':{'old_csv':str(old_csv.relative_to(ROOT)),'new_csv':str(new_csv.relative_to(ROOT)),'old_sha256':sha(old_csv),'new_sha256':sha(new_csv),'rows':len(nrr),'previous_columns_preserved':len(oh),'new_column_count':len(nh),'tableI_cells':len(formal),'formal_trials':0,'formal_required':22500,'mismatches':coverage_m},'ledger':{'path':str(ledger_path.relative_to(ROOT)),'sha256':sha(ledger_path),'count':len(rows),'science_count':ledger['science_count'],'engineering_count':ledger['engineering_count'],'r2_remaining':ledger['r2_remaining'],'charge_rule':'External upper replaces internal sample once; historical unsupervised tail UNKNOWN retained.','mismatches':lm},'historical_snapshots':history,'historical_mismatches':hm,'new_scientific_calls':0,'analysis_cost':{'wall_s':time.monotonic()-start_wall,'cpu_s':time.process_time()-start_cpu},'passed':passed}
with OUT.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':passed,'path':str(OUT),'mismatches':[oldm,crashm,archive_m,otherm,coverage_m,lm,hm]},ensure_ascii=False))
