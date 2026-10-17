"""V23 saved-only preservation successor; execution requires a real independent POST.

This draft never imports a project/model or runs compilation/binaries/science.
Do not run until the actual independent PATH01 POST and V23 ledger/CSV exist.
It writes only one new preservation JSON with exclusive creation.
"""
from pathlib import Path
import argparse
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
OUT=ROOT/'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V23.json'
BASE=ROOT/'results/p4_full/20261015_RECOVERY_BASELINE_MANIFEST.json'
TREES=ROOT/'results/p4_full/20261015_RECOVERY_EXISTING_WORKTREES.json'
ARCHIVE=Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/work/recovery_20261015/preexisting_uncommitted.tar.gz')
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


def main():
    start_wall=time.monotonic();start_cpu=time.process_time()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--external-post-sha256',required=True)
    args=parser.parse_args()
    if not re.fullmatch('[0-9a-f]{64}',args.external_post_sha256):raise RuntimeError('EXPLICIT_REAL_POST_SHA256_REQUIRED')
    if OUT.exists():raise RuntimeError('V23_RESULT_ALREADY_EXISTS_NO_OVERWRITE')
    post_path=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST_20261017.json'
    if not post_path.is_file():raise RuntimeError('WAIT_REAL_PERSONNEL_INDEPENDENT_PATH01_POST')
    if sha(post_path)!=args.external_post_sha256 or args.external_post_sha256!='b3a2443cb790df547597fe5a72b4eeb78341d2f93a4b4beca8252eba692c40c8':raise RuntimeError('FIXED_REAL_POST_SHA256_CHANGED')
    post=read(post_path)
    if not (post.get('personnel_independent') is True and post.get('external_supervision_qualified') is True and post.get('independent_path_qualified') is True and post.get('checks_total',0)>0 and post.get('checks_total')==post.get('checks_passed') and post.get('checks_failed')==0 and post.get('failures')==[]):raise RuntimeError('WAIT_SUCCESSFUL_REAL_PATH_POST_NOT_PREDICTED')
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



    old_csv=ROOT/'reports/P4_FULL_R2_CBIRRT_NR_SOLVE_ORIGINAL_VS_REPRODUCED_COVERAGE_20261016.csv'
    new_csv=ROOT/'reports/P4_FULL_R2_CBIRRT_NR_PATH_ORIGINAL_VS_REPRODUCED_COVERAGE_20261017.csv'
    oh,orr=csvread(old_csv);nh,nrr=csvread(new_csv);coverage_m=[]
    if len(nrr)!=211 or len({r['item_id']for r in nrr})!=211:coverage_m.append('211_UNIQUE')
    if len(oh)!=174 or len(nh)!=178 or nh[:len(oh)]!=oh:coverage_m.append('EXACT174_TO178_HISTORICAL_COLUMNS')
    if [r['item_id']for r in orr]!=[r['item_id']for r in nrr]:coverage_m.append('ID_ORDER')
    for old,new in zip(orr,nrr):
        for col in oh:
            if old[col]!=new[col]:coverage_m.append({'item':old['item_id'],'column':col})
    formal=[r for r in nrr if r['item_id'].startswith('P4-T18-')]
    expected=set(itertools.product(['II','III','IV','V','VI'],['RRT','Bi-RRT','SBL'],['RSS','PCS','NR']))
    if {tuple(r['item_id'].removeprefix('P4-T18-').split('_'))for r in formal}!=expected:coverage_m.append('45_CELLS')
    for r in formal:
        if r['original_repeats']!='500' or r['original_duration_budget']!='1000s/call':coverage_m.append({'item':r['item_id'],'reason':'FORMAL_SCALE'})
    ledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V23.json';ledger=read(ledger_path)
    oldledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V22.json';oldledger=read(oldledger_path)
    rows=ledger['executions'];run='20261016_R2_ABB_CBIRRT_NR_PATH01';lm=[]
    expected_ids={r['run_id']for r in oldledger['executions']}|{run}
    if {r['run_id']for r in rows}!=expected_ids or len(rows)!=41 or len({r['execution']for r in rows})!=41 or ledger['count']!=41:lm.append('DISTINCT41_EXECUTIONS')
    actual={str(p.relative_to(ROOT)):sha(p)for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')}
    if actual!={r['execution']:r['execution_sha256']for r in rows}:lm.append('ALL_ACTUAL_CROSSDATE_EXECUTIONS')
    for r in rows:
        p=ROOT/r['execution'];e=read(p)
        if sha(p)!=r['execution_sha256'] or e['wall_s']!=r['wall_s'] or e['cpu_s']!=r['cpu_s']:lm.append({'run':r['run_id'],'reason':'EXECUTION_HASH_OR_OWN_COST'})
    for k in ['wall_s','cpu_s']:
        total=math.fsum(r.get('charged_'+k,r[k])for r in rows)
        if ledger['conservative_r2_sum_'+k]!=total:lm.append({'field':k,'reason':'FSUM_EXACT'})
        if ledger['r2_remaining'][k]!=ledger['r2_caps'][k]-total:lm.append({'field':k,'reason':'REMAINING'})
    if ledger['r2_caps']!={'wall_s':3600.,'cpu_s':7200.}:lm.append('ORIGINAL_R2_CAPS')
    if ledger['science_count']!=31 or ledger['engineering_count']!=10 or sum(r['engineering_only']is False for r in rows)!=31:lm.append('EXPECTED31_SCIENCE10_ENGINEERING')
    tail=next(r for r in rows if r['run_id']==run);pe=read(ROOT/tail['execution'])
    if sha(ROOT/tail['execution'])!='ee8691a2e6ca2318e2ef4a8a2c8a2b3cc2f5a18c4d6e319a3d1857112a3ab025':lm.append('FIXED_PATH01_EXECUTION_SHA')
    if pe['schema']!='P4_R2_ABB_CBIRRT_NR_PATH_EXECUTION_V1' or pe['run_id']!=run or pe['classification']!='R2_RECONSTRUCTED_PHYSICAL_NR_CBIRRT_A01_FULL_DISCRETE_SOURCE_POLICY_PATH' or pe['status']!='PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH' or tail['engineering_only']is not False:lm.append('ACTUAL_PATH01_ONLY')
    if pe['independent_path_qualified']is not False or pe['external_supervision_qualified']is not False or pe['continuous_collision_certificate']is not False:lm.append('ORIGINAL_RAW_FALSE_FIELDS_MUST_STAY_FALSE')
    if pe['node_count']!=689 or pe['completed_nodes']!=689 or pe['qualified_nodes']!=689 or pe['full_queue_checked']is not True or pe['uncompleted_node_ids']!=[] or pe['diagnostics']!=[]:lm.append('COMPLETE689_NODES_REQUIRED')
    if pe['counts']!={'math_arm_FK_started':1378,'math_arm_FK_completed':1378,'collision_calls_started':689,'collision_worker_start_attempted':2,'collision_worker_started':2,'adapter_arm_FK_J_started':2756,'adapter_arm_FK_J_completed':2756,'collision_calls_completed':689,'PQP_queries':159848}:lm.append('ACTUAL_PATH01_COUNTS_CHANGED')
    if not pe['zero_calls'] or any(type(v)is not int or v!=0 for v in pe['zero_calls'].values()) or pe['zero_calls'].get('solve')!=0:lm.append('PATH01_ZERO_NEW_SOLVE_MODEL_PROJECTION_RBS_VI_CALLS')
    for field in ('formal_table_I_calls','new_VI_candidate_constructions'):
        if type(pe.get(field))is not int or pe[field]!=0:lm.append({'field':field,'reason':'NEW_FORMAL_OR_VI_CALL'})
    if tail['external_post']!=str(post_path.relative_to(ROOT)) or tail['external_post_sha256']!=args.external_post_sha256 or post['execution_sha256']!=tail['execution_sha256']:lm.append('REAL_INDEPENDENT_POST_BINDING')
    # Bind the actual published personnel-independent POST; no prediction or rewrite.
    if post['schema']!='P4_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST_V1' or post['status']!='PASS_CBIRRT_NR_PATH01_SAVED_INDEPENDENT_POST':lm.append('REAL_PATH_POST_SCHEMA_STATUS')
    if post['checks_total']!=41787 or post['checks_passed']!=41787 or post['nodes']!=689 or post['edges']!=11 or post['leaves']!=688 or post['dense_references']!=699 or post['actual_counts']!=pe['counts'] or post['PQP_queries']!=159848:lm.append('REAL_POST_COMPLETE_PATH_AND_COUNTS')
    for field in ['execution','protocol','claim','receipt','internal_receipt','external_time','source_execution','source_POST']:
        p=Path(post[field]);p=p if p.is_absolute()else ROOT/p
        if sha(p)!=post[field+'_sha256']:lm.append({'field':field,'reason':'ACTUAL_POST_CHAIN_HASH'})
    for name,want in post['retained_sha256'].items():
        p=Path(name);p=p if p.is_absolute()else ROOT/p
        if sha(p)!=want:lm.append({'path':name,'reason':'SAVED_POST_ASSET_CHANGED'})
    if pe['bound_files_sha256']!=pe['bound_files_after_sha256'] or pe['prior_execution_sha256']!=pe['prior_execution_after_sha256']:lm.append('BOUND_OR_PRIOR_MAP_CHANGED')
    for name,want in pe['bound_files_sha256'].items():
        p=Path(name);p=p if p.is_absolute()else ROOT/p
        if sha(p)!=want:lm.append({'path':name,'reason':'PATH_BOUND_ASSET_CHANGED'})
    for name,want in pe['retained_run_files_sha256'].items():
        if sha(ROOT/name)!=want:lm.append({'path':name,'reason':'PATH_LOOSE_OR_ARCHIVE_FILE_CHANGED'})
    queue=read(ROOT/'results/p4_full'/run/'complete_original_saved_queue.json')
    if queue['full_queue_node_count']!=689 or queue['full_dense_node_reference_count']!=699 or queue['full_dense_leaf_count']!=688 or queue['source_milestone_count']!=12 or queue['source_attempt_count']!=11 or len(queue['nodes'])!=689 or len(queue['edges'])!=11:lm.append('FULL_ORIGINAL689_699REF_688LEAF_QUEUE')
    if [len(z['path_q12'])for z in queue['all_original_attempts']]!=[65,65,17,65,129,129,65,33,33,33,65] or not all(z['returned']is True for z in queue['all_original_attempts']):lm.append('ELEVEN_REAL_SOURCE_M_RETAINED')
    snap=pe['durable_saved_snapshot'];snapshot_m=[]
    if len(snap['members'])!=3447 or snap['members_verified']!=3447 or any(snap.get(k)is not True for k in ['archive_file_fsync_completed','containing_directory_fsync_completed','loose_files_byte_exact']):snapshot_m.append('COMPLETE3447_DURABLE_SNAPSHOT_REQUIRED')
    if sha(ROOT/snap['path'])!=snap['sha256']:snapshot_m.append('DURABLE_TAR_SHA_CHANGED')
    with tarfile.open(ROOT/snap['path'],'r:')as tar:
        members2=tar.getmembers();seen2=collections.Counter(m.name for m in members2)
        if len(members2)!=3447 or set(seen2)!=set(snap['members']) or any(n!=1 for n in seen2.values()):snapshot_m.append('EXACT3447_TAR_MEMBERS_ONCE')
        for member in members2:
            if not member.isfile()or member.name not in snap['members']:snapshot_m.append({'member':member.name,'reason':'UNEXPECTED_OR_NONFILE'});continue
            record=snap['members'][member.name];raw=tar.extractfile(member).read()
            if hashlib.sha256(raw).hexdigest()!=record['sha256']or len(raw)!=record['bytes']:snapshot_m.append({'member':member.name,'reason':'TAR_MEMBER_BYTES_CHANGED'})
    if snapshot_m:lm.append({'durable_saved_snapshot':snapshot_m})
    related={'P4-T03','P4-T05','P4-T09','P4-T11','P4-T16','P4-T17','P4-T25','P4-T26'}
    if set(ledger.get('coverage_related_item_ids',[]))!=related:coverage_m.append('EXPLICIT_II_NR_PATH_RELATED_IDS')
    for r in nrr:
        if r['item_id']not in related and(r['v23_status']!='NO_NEW_EVIDENCE_FOR_THIS_OBLIGATION'or r['v23_execution']!='NOT_APPLICABLE'):coverage_m.append({'item':r['item_id'],'reason':'UNRELATED_SCIENTIFIC_EVIDENCE'})
    timep=ROOT/tail['external_time'];elapsed,user,system,exitstatus=timep.read_text().split()
    if sha(timep)!=tail['external_time_sha256']or sha(timep)!=post['external_time_sha256']:lm.append('EXTERNAL_TIME_HASH_CHANGED')
    if [elapsed,user,system,exitstatus]!=['19.58','15.94','1.87','0']or tail['charged_wall_s']!=float(Decimal(elapsed)+Decimal('.01'))or tail['charged_cpu_s']!=float(Decimal(user)+Decimal(system)+Decimal('.02'))or tail['charged_wall_s']!=19.59 or tail['charged_cpu_s']!=17.83:lm.append('EXTERNAL_CHARGE_INCORRECT')
    if tail['charged_wall_s']!=post['upper_wall_s']or tail['charged_cpu_s']!=post['upper_cpu_s']:lm.append('REAL_POST_EXTERNAL_UPPER_MISMATCH')
    if any(next(r for r in rows if r['execution']==old['execution'])!=old for old in oldledger['executions']):lm.append('OLD_LEDGER_ENTRIES_CHANGED')
    if ledger['vi_B_consumed']!=oldledger['vi_B_consumed']or ledger['vi_B_remaining']!=oldledger['vi_B_remaining']or ledger['vi_B_candidate_cap']!=974 or ledger['vi_B_remaining']['candidate_constructions']!=0:lm.append('VI974_HISTORY_CHANGED')
    if ledger['formal_table_I_calls']!=0 or ledger['formal_table_I_required_calls']!=22500:lm.append('FORMAL_CALLS')
    addp=ROOT/'results/p4_full/20261016_RECOVERY_QUALIFICATION_SOLVE_ACCOUNTING_V22_ADDENDUM.json';add=read(addp)
    if sha(addp)!='316024926cbd63e1f6ca53db0be6d7cc4419b9cb3b029450f642e3529f87bcb9':lm.append('IMMUTABLE_V22_SOLVE_ADDENDUM')
    sa=ledger['authoritative_source_solve_accounting'];enum=sa['actual_source_solve_dispatches_by_execution']
    if sa['schema']!='P4_ACTUAL_SOURCE_SOLVE_ACCOUNTING_V1'or sa['executions_enumerated']!=41 or len(enum)!=41 or sa['previous_actual_source_solve_dispatches']!=5 or sa['new_actual_source_solve_dispatches']!=0 or sa['total_actual_source_solve_dispatches']!=5 or sa['ledger_generation_new_source_solve_dispatches']!=0:lm.append('AUTHORITATIVE_FIVE_ACTUAL_SOLVES_NO_PATH_SOLVE')
    if sa['baseline_addendum']!=str(addp.relative_to(ROOT))or sa['baseline_addendum_sha256']!=sha(addp)or sa['previous_snapshot']!=str(oldledger_path.relative_to(ROOT))or sa['previous_snapshot_sha256']!=sha(oldledger_path):lm.append('SOURCE_SOLVE_ACCOUNTING_BASE_BINDING')
    if {z['execution']:z['execution_sha256']for z in enum}!={r['execution']:r['execution_sha256']for r in rows}:lm.append('ALL41_SOURCE_SOLVE_ROWS_ENUMERATED')
    positive={z['execution']['path']:z for z in add['actual_source_solve_dispatches']}
    for z in enum:
        expected_count=positive[z['execution']]['actual_source_solve_dispatches']if z['execution']in positive else 0
        if type(z['actual_source_solve_dispatches'])is not int or z['actual_source_solve_dispatches']!=expected_count:lm.append({'run':z['run_id'],'reason':'ACTUAL_SOURCE_SOLVE_COUNT'})
        if z['new_since_previous_snapshot']is not(z['run_id']==run):lm.append({'run':z['run_id'],'reason':'SOURCE_COUNT_NEW_FLAG'})
        if z['run_id']==run and z['saved_dispatch_fields'].get('zero_calls.solve')!=0:lm.append('PATH01_EXPLICIT_ZERO_SOLVE')
    for dispatch in add['actual_source_solve_dispatches']:
        item=dispatch['execution']
        if sha(ROOT/item['path'])!=item['sha256']or dispatch['actual_source_solve_dispatches']!=1:lm.append('REAL_SOLVE_DISPATCH_EXECUTION_CHANGED')
    history=[];hm=[]
    for p in [ROOT/'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V22.json',oldledger_path,old_csv,addp]:
        blob=subprocess.check_output(['git','show','742fff2:'+str(p.relative_to(ROOT))],cwd=ROOT)
        ok=hashlib.sha256(blob).hexdigest()==sha(p);history.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'matches742fff2':ok})
        if not ok:hm.append(str(p.relative_to(ROOT)))
    passed=baseline_contract and not(oldm or crashm or archive_m or otherm or coverage_m or lm or hm)and archive['sha_matches']and len(orr)==len(nrr)==211 and len(other)==5 and sum(z['preserved_uncommitted_files']for z in other)==13 and len(crash)==57
    result={'schema':'P4_RECOVERY_IMMUTABLE_VERIFICATION_V23','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head_at_verification':git(ROOT,'rev-parse','HEAD').strip(),'analysis_source':str(Path(__file__).resolve()),'analysis_source_sha256':sha(__file__),'baseline_manifest':str(BASE.relative_to(ROOT)),'baseline_manifest_sha256':sha(BASE),'old_scientific_files':len(b['files']),'old_scientific_mismatches':oldm,'crash_uncommitted_files':len(crash),'crash_uncommitted_bytes':sum(z['bytes']for z in crash),'crash_uncommitted_mismatches':crashm,'external_archive':archive,'other_worktrees':len(other),'other_uncommitted_files':sum(z['preserved_uncommitted_files']for z in other),'other_worktree_results':other,'other_worktree_mismatches':otherm,'coverage':{'old_csv':str(old_csv.relative_to(ROOT)),'new_csv':str(new_csv.relative_to(ROOT)),'old_sha256':sha(old_csv),'new_sha256':sha(new_csv),'rows':len(nrr),'previous_columns_preserved':len(oh),'new_column_count':len(nh),'tableI_cells':len(formal),'formal_trials':0,'formal_required':22500,'mismatches':coverage_m},'ledger':{'path':str(ledger_path.relative_to(ROOT)),'sha256':sha(ledger_path),'count':len(rows),'science_count':ledger['science_count'],'engineering_count':ledger['engineering_count'],'r2_remaining':ledger['r2_remaining'],'charge_rule':'External upper replaces internal sample once; historical unsupervised tail UNKNOWN retained.','mismatches':lm},'path01':{'execution':tail['execution'],'execution_sha256':tail['execution_sha256'],'external_post':tail['external_post'],'external_post_sha256':tail['external_post_sha256'],'complete_nodes':689,'complete_leaves':688,'durable_tar_members':len(snap['members']),'durable_tar_mismatches':snapshot_m,'source_raw_qualification_flags_preserved_false':True},'authoritative_source_solve_accounting':{'previous':sa['previous_actual_source_solve_dispatches'],'new':sa['new_actual_source_solve_dispatches'],'total':sa['total_actual_source_solve_dispatches'],'executions_enumerated':sa['executions_enumerated']},'historical_snapshots':history,'historical_mismatches':hm,'new_scientific_calls':0,'analysis_cost':{'wall_s':time.monotonic()-start_wall,'cpu_s':time.process_time()-start_cpu},'passed':passed}
    with OUT.open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({'passed':passed,'path':str(OUT),'mismatches':[oldm,crashm,archive_m,otherm,coverage_m,lm,hm]},ensure_ascii=False))

if __name__=="__main__":
    main()
