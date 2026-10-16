"""Audit fixed crash baseline and fixed31-execution ledger. Never inspect live run dirs."""
from pathlib import Path
import collections
import csv
import datetime
import hashlib
import itertools
import json
import math
import os
import subprocess
import tarfile
import time

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
OUT=ROOT/'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V13.json'
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


old_csv=ROOT/'reports/P4_FULL_R2_CBIRRT_D_BUILD_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
new_csv=ROOT/'reports/P4_FULL_R2_CBIRRT_D_DISTANCE_STOP_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
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
ledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V13.json';ledger=read(ledger_path);oldledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V12.json';oldledger=read(oldledger_path);lm=[]
rows=ledger['executions'];expected_ids={r['run_id'] for r in oldledger['executions']}|{'20261015_R2_ABB_CBIRRT_D_DISTANCE01'}
if {r['run_id'] for r in rows}!=expected_ids or len(rows)!=31:lm.append('DISTINCT31_EXECUTIONS')
for r in rows:
    p=ROOT/r['execution'];e=read(p)
    if sha(p)!=r['execution_sha256'] or e['wall_s']!=r['wall_s'] or e['cpu_s']!=r['cpu_s']:lm.append({'run':r['run_id'],'reason':'EXECUTION_HASH_OR_OWN_COST'})
for k in ['wall_s','cpu_s']:
    value=math.fsum(r[k] for r in rows)
    if ledger['conservative_r2_sum_'+k]!=value:lm.append({'field':k,'reason':'FSUM_EXACT'})
    if ledger['r2_remaining'][k]!=ledger['r2_caps'][k]-value:lm.append({'field':k,'reason':'REMAINING'})
if ledger['vi_B_consumed']!=oldledger['vi_B_consumed'] or ledger['vi_B_remaining']!=oldledger['vi_B_remaining']:lm.append('VI_B_CHANGED')
if ledger['vi_B_candidate_cap']!=974 or ledger['vi_B_remaining']['candidate_constructions']!=0:lm.append('VI974_EXHAUSTED')
if ledger['formal_table_I_calls']!=0 or ledger['formal_table_I_required_calls']!=22500:lm.append('FORMAL_CALLS')
history=[];hm=[]
for name in ['20261016_RECOVERY_IMMUTABLE_VERIFICATION_V12.json','20261016_RECOVERY_ACTUAL_LEDGER_V12.json']:
    p=ROOT/'results/p4_full'/name;blob=subprocess.check_output(['git','show','ea1973c:'+str(p.relative_to(ROOT))],cwd=ROOT)
    ok=hashlib.sha256(blob).hexdigest()==sha(p);history.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'matchesea1973c':ok})
    if not ok:hm.append(name)
passed=not(oldm or crashm or archive_m or otherm or coverage_m or lm or hm) and archive['sha_matches'] and len(orr)==len(nrr)==211 and len(other)==5 and len(crash)==57
result={'schema':'P4_RECOVERY_IMMUTABLE_VERIFICATION_V13','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head_at_verification':git(ROOT,'rev-parse','HEAD').strip(),'analysis_source':str(Path(__file__).resolve()),'analysis_source_sha256':sha(__file__),'baseline_manifest':str(BASE.relative_to(ROOT)),'baseline_manifest_sha256':sha(BASE),'old_scientific_files':len(b['files']),'old_scientific_mismatches':oldm,'crash_uncommitted_files':len(crash),'crash_uncommitted_bytes':sum(f['bytes'] for f in crash),'crash_uncommitted_mismatches':crashm,'external_archive':archive,'other_worktrees':len(other),'other_uncommitted_files':sum(x['preserved_uncommitted_files'] for x in other),'other_worktree_results':other,'other_worktree_mismatches':otherm,'coverage':{'old_csv':str(old_csv.relative_to(ROOT)),'new_csv':str(new_csv.relative_to(ROOT)),'old_sha256':sha(old_csv),'new_sha256':sha(new_csv),'rows':len(nrr),'previous_columns_preserved':len(oh),'new_column_count':len(nh),'tableI_cells':len(formal),'formal_trials':0,'formal_required':22500,'mismatches':coverage_m},'ledger':{'path':str(ledger_path.relative_to(ROOT)),'sha256':sha(ledger_path),'count':len(rows),'science_count':ledger['science_count'],'engineering_count':ledger['engineering_count'],'r2_remaining':ledger['r2_remaining'],'mismatches':lm},'historical_snapshots':history,'historical_mismatches':hm,'new_scientific_calls':0,'analysis_cost':{'wall_s':time.monotonic()-start_wall,'cpu_s':time.process_time()-start_cpu},'passed':passed}
with OUT.open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':passed,'path':str(OUT),'mismatches':[oldm,crashm,archive_m,otherm,coverage_m,lm,hm]},ensure_ascii=False))
