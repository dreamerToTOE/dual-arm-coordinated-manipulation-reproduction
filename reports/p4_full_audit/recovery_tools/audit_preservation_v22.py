"""Audit immutable crash history and V22 SOLVE01 ledger; saved evidence only.

Prepare/read/AST is not an execution. Requires actual successful SOLVE01 and
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
OUT=ROOT/'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V22.json'
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
baseline_contract=(sha(BASE)=='ed334ff481e304037acdbf3897c386cf8246e64b9439d841ec18c14e0fb60235' and len(b['files'])==1028 and len(b['preexisting_uncommitted']['files'])==57 and sum(f['bytes'] for f in b['preexisting_uncommitted']['files'])==8482891)
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


old_csv=ROOT/'reports/P4_FULL_R2_CBIRRT_NR_BUILD03_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
new_csv=ROOT/'reports/P4_FULL_R2_CBIRRT_NR_SOLVE_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
oh,orr=csvread(old_csv);nh,nrr=csvread(new_csv)
coverage_m=[]
if len(nrr)!=211 or len({r['item_id'] for r in nrr})!=211:coverage_m.append('211_UNIQUE')
if len(oh)!=170 or len(nh)!=174 or nh[:len(oh)]!=oh:coverage_m.append('EXACT170_TO174_HISTORICAL_COLUMNS')
if [r['item_id'] for r in orr]!=[r['item_id'] for r in nrr]:coverage_m.append('ID_ORDER')
for a,z in zip(orr,nrr):
    for col in oh:
        if a[col]!=z[col]:coverage_m.append({'item':a['item_id'],'column':col})
formal=[r for r in nrr if r['item_id'].startswith('P4-T18-')]
expected=set(itertools.product(['II','III','IV','V','VI'],['RRT','Bi-RRT','SBL'],['RSS','PCS','NR']))
if {tuple(r['item_id'].removeprefix('P4-T18-').split('_')) for r in formal}!=expected:coverage_m.append('45_CELLS')
for r in formal:
    if r['original_repeats']!='500' or r['original_duration_budget']!='1000s/call':coverage_m.append({'item':r['item_id'],'reason':'FORMAL_SCALE'})
ledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V22.json';ledger=read(ledger_path)
oldledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V21.json';oldledger=read(oldledger_path);lm=[]
rows=ledger['executions'];run='20261016_R2_ABB_CBIRRT_NR_SOLVE01'
expected_ids={r['run_id'] for r in oldledger['executions']}|{run}
if {r['run_id'] for r in rows}!=expected_ids or len(rows)!=40 or len({r['execution'] for r in rows})!=40:lm.append('DISTINCT40_EXECUTIONS')
actual={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'results/p4_full').glob('*_R2_*/execution.json')}
if actual!={r['execution']:r['execution_sha256'] for r in rows}:lm.append('ALL_ACTUAL_CROSSDATE_EXECUTIONS')
for r in rows:
    p=ROOT/r['execution'];e=read(p)
    if sha(p)!=r['execution_sha256'] or e['wall_s']!=r['wall_s'] or e['cpu_s']!=r['cpu_s']:lm.append({'run':r['run_id'],'reason':'EXECUTION_HASH_OR_OWN_COST'})
for k in ['wall_s','cpu_s']:
    value=math.fsum(r.get('charged_'+k,r[k]) for r in rows)
    if ledger['conservative_r2_sum_'+k]!=value:lm.append({'field':k,'reason':'FSUM_EXACT'})
    if ledger['r2_remaining'][k]!=ledger['r2_caps'][k]-value:lm.append({'field':k,'reason':'REMAINING'})
tail=next(r for r in rows if r['run_id']==run);post=read(ROOT/tail['external_post']);pe=read(ROOT/tail['execution'])
if ledger['science_count']!=30 or ledger['engineering_count']!=10 or sum(not r['engineering_only'] for r in rows)!=30:lm.append('EXPECTED30_SCIENCE10_ENGINEERING')
if pe['status']!='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT' or pe['classification']!='R2_RECONSTRUCTED_PHYSICAL_NR_SINGLE_ORIGINAL_CBIRRT_NR_SOLVE' or tail['engineering_only'] is not False or pe['independent_path_qualified'] is not False:lm.append('SOLVE01_CANDIDATE_NOT_PATH_QUALIFIED')
if pe['schema']!='P4_R2_ABB_CBIRRT_NR_SOLVE01_EXECUTION_V3' or pe['run_id']!=run or pe['complete_source_raw_evidence_gate'] is not True or pe['diagnostics']!=[] or not pe['source_exact'] or pe['source_approximate']:lm.append('SOLVE01_ACTUAL_EXACT_RAW_GATE')
for field in ('formal_table_I_calls','new_VI_candidate_constructions'):
    if type(pe.get(field)) is not int or pe[field]!=0:lm.append({'field':field,'reason':'NEW_FORMAL_OR_VI_CALL'})
expected_post='reports/P4_FULL_R2_ABB_CBIRRT_NR_SOLVE01_SAVED_INDEPENDENT_POST_20261016.json'
if tail['external_post']!=expected_post or sha(ROOT/tail['external_post'])!='549d585f1fb2be390b28a0d64dfb90815e58092a9efd7e3c4d478abebe381ef1' or post['schema']!='P4_CBIRRT_NR_SOLVE01_SAVED_INDEPENDENT_POST_V1' or post['status']!='PASS_CBIRRT_NR_SOLVE01_TRANSPORT_EVIDENCE_INDEPENDENT_POST' or post['independent_path_qualified'] is not False:lm.append('REAL_INDEPENDENT_SOLVE_POST_ONLY')
if post['checks_total']!=16711 or post['checks_passed']!=16711 or post['checks_failed']!=0 or post['failures']!=[] or not post['source_complete_reconstruction_observed'] or post['selected_complete_dense_node_count']!=689:lm.append('SOLVE_POST_COMPLETE689_CANDIDATE')
for field in ['execution','protocol','claim','receipt','internal_receipt','external_time']:
    p=Path(post[field]);p=p if p.is_absolute() else ROOT/p
    if sha(p)!=post[field+'_sha256']:lm.append({'field':field,'reason':'ACTUAL_POST_CHAIN_HASH'})
for name,want in post['retained_sha256'].items():
    p=Path(name);p=p if p.is_absolute() else ROOT/p
    if sha(p)!=want:lm.append({'path':name,'reason':'SAVED_RAW_ASSET_CHANGED'})
if post['source_bridge_motion_ids']!=[16,14] or [z['node_count'] for z in post['state_reconstruction_attempts']]!=[65,65,17,65,129,129,65,33,33,33,65] or not all(z['returned'] is True for z in post['state_reconstruction_attempts']):lm.append('SOURCE_BRIDGE_OR11_ORIGINAL_M_CHANGED')
if pe['bound_files_sha256']!=pe['bound_files_after_sha256'] or pe['prior_execution_sha256']!=pe['prior_execution_after_sha256']:lm.append('BOUND_OR_PRIOR_MAP_CHANGED')
for name,want in pe['bound_files_sha256'].items():
    p=Path(name);p=p if p.is_absolute()else ROOT/p
    if sha(p)!=want:lm.append({'path':name,'reason':'SOLVE_BOUND_ASSET_CHANGED'})
related={'P4-T03','P4-T05','P4-T09','P4-T11','P4-T12','P4-T17','P4-T25'}
if set(ledger.get('coverage_related_item_ids',[]))!=related:coverage_m.append('EXPLICIT_II_NR_SOLVE_RELATED_IDS')
for row in nrr:
    if row['item_id']not in related and (row['v22_status']!='NO_NEW_EVIDENCE_FOR_THIS_OBLIGATION' or row['v22_execution']!='NOT_APPLICABLE'):coverage_m.append({'item':row['item_id'],'reason':'UNRELATED_SCIENTIFIC_EVIDENCE'})
timep=ROOT/tail['external_time'];elapsed,user,system,exitstatus=timep.read_text().split()
if sha(ROOT/tail['external_post'])!=tail['external_post_sha256'] or sha(timep)!=tail['external_time_sha256']:lm.append('EXTERNAL_HASH_CHANGED')
if not post['external_supervision_qualified'] or not post['personnel_independent'] or post['checks_failed']!=0:lm.append('EXTERNAL_POST_NOT_QUALIFIED')
if exitstatus!='0' or tail['charged_wall_s']!=float(Decimal(elapsed)+Decimal('.01')) or tail['charged_cpu_s']!=float(Decimal(user)+Decimal(system)+Decimal('.02')) or tail['charged_wall_s']!=9.06 or tail['charged_cpu_s']!=8.71:lm.append('EXTERNAL_CHARGE_INCORRECT')
if tail['charged_wall_s']!=post['upper_wall_s'] or tail['charged_cpu_s']!=post['upper_cpu_s']:lm.append('EXTERNAL_POST_UPPER_MISMATCH')
if any(next(r for r in rows if r['execution']==o['execution'])!=o for o in oldledger['executions']):lm.append('OLD_LEDGER_ENTRIES_CHANGED')
if ledger['vi_B_consumed']!=oldledger['vi_B_consumed'] or ledger['vi_B_remaining']!=oldledger['vi_B_remaining'] or ledger['vi_B_candidate_cap']!=974 or ledger['vi_B_remaining']['candidate_constructions']!=0:lm.append('VI974_HISTORY_CHANGED')
if ledger['formal_table_I_calls']!=0 or ledger['formal_table_I_required_calls']!=22500:lm.append('FORMAL_CALLS')
addp=ROOT/'results/p4_full/20261016_RECOVERY_QUALIFICATION_SOLVE_ACCOUNTING_V22_ADDENDUM.json';add=read(addp)
if sha(addp)!='316024926cbd63e1f6ca53db0be6d7cc4419b9cb3b029450f642e3529f87bcb9' or add['authoritative_counters']['previous_snapshot_actual_source_solve_dispatches']!=4 or add['authoritative_counters']['new_actual_source_solve_dispatches_recorded_in_V22']!=1 or add['authoritative_counters']['total_actual_source_solve_dispatches_through_V22']!=5:lm.append('V22_REAL_SOLVE_COUNT_ADDENDUM_REQUIRED')
for dispatch in add['actual_source_solve_dispatches']:
    item=dispatch['execution']
    if sha(ROOT/item['path'])!=item['sha256'] or dispatch['actual_source_solve_dispatches']!=1:lm.append('REAL_SOLVE_DISPATCH_EXECUTION_CHANGED')
history=[];hm=[]
for p in [ROOT/'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V21.json',oldledger_path,old_csv]:
    blob=subprocess.check_output(['git','show','119a1b3:'+str(p.relative_to(ROOT))],cwd=ROOT)
    ok=hashlib.sha256(blob).hexdigest()==sha(p);history.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'matches119a1b3':ok})
    if not ok:hm.append(str(p.relative_to(ROOT)))
passed=baseline_contract and not(oldm or crashm or archive_m or otherm or coverage_m or lm or hm) and archive['sha_matches'] and len(orr)==len(nrr)==211 and len(other)==5 and sum(x['preserved_uncommitted_files']for x in other)==13 and len(crash)==57
result={'schema':'P4_RECOVERY_IMMUTABLE_VERIFICATION_V22','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head_at_verification':git(ROOT,'rev-parse','HEAD').strip(),'analysis_source':str(Path(__file__).resolve()),'analysis_source_sha256':sha(__file__),'baseline_manifest':str(BASE.relative_to(ROOT)),'baseline_manifest_sha256':sha(BASE),'old_scientific_files':len(b['files']),'old_scientific_mismatches':oldm,'crash_uncommitted_files':len(crash),'crash_uncommitted_bytes':sum(f['bytes'] for f in crash),'crash_uncommitted_mismatches':crashm,'external_archive':archive,'other_worktrees':len(other),'other_uncommitted_files':sum(x['preserved_uncommitted_files'] for x in other),'other_worktree_results':other,'other_worktree_mismatches':otherm,'coverage':{'old_csv':str(old_csv.relative_to(ROOT)),'new_csv':str(new_csv.relative_to(ROOT)),'old_sha256':sha(old_csv),'new_sha256':sha(new_csv),'rows':len(nrr),'previous_columns_preserved':len(oh),'new_column_count':len(nh),'tableI_cells':len(formal),'formal_trials':0,'formal_required':22500,'mismatches':coverage_m},'ledger':{'path':str(ledger_path.relative_to(ROOT)),'sha256':sha(ledger_path),'count':len(rows),'science_count':ledger['science_count'],'engineering_count':ledger['engineering_count'],'r2_remaining':ledger['r2_remaining'],'charge_rule':'External upper replaces internal sample once; historical unsupervised tail UNKNOWN retained.','mismatches':lm},'historical_snapshots':history,'historical_mismatches':hm,'new_scientific_calls':0,'analysis_cost':{'wall_s':time.monotonic()-start_wall,'cpu_s':time.process_time()-start_cpu},'passed':passed}
with OUT.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':passed,'path':str(OUT),'mismatches':[oldm,crashm,archive_m,otherm,coverage_m,lm,hm]},ensure_ascii=False))
