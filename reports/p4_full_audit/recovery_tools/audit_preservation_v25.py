"""DRAFT V25 saved-only preservation for actual SBL PCS scientific SETUP01.

Do not execute before actual setup, personnel-independent POST, V25 ledger and
coverage exist. Real POST path and SHA are mandatory execution parameters; no
future result or check total is predicted. Standard-library saved reads only.
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
OUT=ROOT/'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V25.json'
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


HISTORY_HEAD='c71420557dc866b41ee05a97c7a9c55c0e4811da'
HISTORY_SHA={
    'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V24.json':'adee31c9150354e4b145718b91f70a4451eaf9bf0f300e067905d6776b48d81e',
    'reports/P4_FULL_R2_SBL_PCS_BUILD01_ORIGINAL_VS_REPRODUCED_COVERAGE_20261017.csv':'8536a239e117d4008363b86b4e7e331ac3b25a96d97fc4ba5a77950ab001a3bd',
    'results/p4_full/20261016_RECOVERY_IMMUTABLE_VERIFICATION_V24.json':'b5e513181859674caa3ebc31f636f820a28a7a71ab832dab7a6f6c03825735a9',
}
RUN='20261017_R2_ABB_SBL_PCS_SETUP01'
CLASSIFICATION='R2_RECONSTRUCTED_A01_ORIGINAL_SBL_PCS_SETUP_PUBLIC_LINEAR_ACTION_OBSERVATION_ONLY'
RAW_STATUS='SOURCE_SETUP_PUBLIC13_OBSERVED_PENDING_INDEPENDENT_POST'
ZERO_CALLS={'compile':0,'solve':0,'independent_model_queries':0,'old_component_requery':0,'VI_constructions':0,'formal_table_I':0,'independent_path_qualification':0}
def absolute(p):
    p=Path(p);return p if p.is_absolute()else ROOT/p

def main():
    start_wall=time.monotonic();start_cpu=time.process_time()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--external-post',required=True)
    parser.add_argument('--external-post-sha256',required=True)
    parser.add_argument('--new-csv',required=True)
    args=parser.parse_args()
    if not re.fullmatch('[0-9a-f]{64}',args.external_post_sha256):raise RuntimeError('ACTUAL_POST_SHA256_REQUIRED')
    if OUT.exists():raise RuntimeError('V25_RESULT_ALREADY_EXISTS_NO_OVERWRITE')
    post_path=absolute(args.external_post)
    if not post_path.is_file():raise RuntimeError('WAIT_ACTUAL_SBL_SETUP_INDEPENDENT_POST')
    if sha(post_path)!=args.external_post_sha256:raise RuntimeError('ACTUAL_POST_PARAMETER_SHA_CHANGED')
    post=read(post_path)
    if not(post.get('schema')=='P4_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST_V1' and post.get('status')=='PASS_SBL_PCS_SETUP01_SAVED_INDEPENDENT_POST' and post.get('personnel_independent')is True and post.get('external_supervision_qualified')is True and post.get('external_timing_qualified')is True and post.get('external_cost_qualified')is True and post.get('setup_qualified')is True and type(post.get('checks_total'))is int and post['checks_total']>0 and type(post.get('checks_passed'))is int and post['checks_passed']==post['checks_total'] and type(post.get('checks_failed'))is int and post['checks_failed']==0 and post.get('failures')==[]):raise RuntimeError('WAIT_REAL_QUALIFIED_SETUP_POST_NO_PREDICTION')
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



    old_csv=ROOT/'reports/P4_FULL_R2_SBL_PCS_BUILD01_ORIGINAL_VS_REPRODUCED_COVERAGE_20261017.csv'
    new_csv=absolute(args.new_csv)
    if new_csv==old_csv:raise RuntimeError('NEW_COVERAGE_PATH_REQUIRED')
    oh,orr=csvread(old_csv);nh,nrr=csvread(new_csv);coverage_m=[]
    if len(orr)!=211 or len(nrr)!=211 or len({r['item_id']for r in nrr})!=211:coverage_m.append('211_UNIQUE')
    if len(oh)!=182 or len(nh)!=186 or nh[:182]!=oh or len(set(nh))!=186 or nh[182:]!=['v25_status','v25_scope','v25_execution','v25_ledger']:coverage_m.append('EXACT182_TO186_HISTORICAL_COLUMNS')
    if [r['item_id']for r in orr]!=[r['item_id']for r in nrr]:coverage_m.append('ID_ORDER')
    for old,new in zip(orr,nrr):
        for col in oh:
            if old[col]!=new[col]:coverage_m.append({'item':old['item_id'],'column':col})
    formal=[r for r in nrr if r['item_id'].startswith('P4-T18-')]
    expected=set(itertools.product(['II','III','IV','V','VI'],['RRT','Bi-RRT','SBL'],['RSS','PCS','NR']))
    if {tuple(r['item_id'].removeprefix('P4-T18-').split('_'))for r in formal}!=expected:coverage_m.append('45_CELLS')
    for r in formal:
        if r['original_repeats']!='500' or r['original_duration_budget']!='1000s/call':coverage_m.append({'item':r['item_id'],'reason':'FORMAL_SCALE'})
    ledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V25.json';ledger=read(ledger_path)
    oldledger_path=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V24.json';oldledger=read(oldledger_path)
    rows=ledger['executions'];lm=[]
    if ledger.get('schema')!='P4_R2_RECOVERY_ACTUAL_LEDGER_V25' or ledger.get('previous_snapshot')!=str(oldledger_path.relative_to(ROOT)) or ledger.get('previous_snapshot_sha256')!=sha(oldledger_path):lm.append('ACTUAL_V25_PREVIOUS_V24_BINDING')
    expected_ids={r['run_id']for r in oldledger['executions']}|{RUN}
    if len(oldledger['executions'])!=42 or len(rows)!=43 or ledger['count']!=43 or {r['run_id']for r in rows}!=expected_ids or len({r['execution']for r in rows})!=43:lm.append('DISTINCT_OLD42_PLUS_ONE_SCIENTIFIC_SETUP_43')
    actual={str(p.relative_to(ROOT)):sha(p)for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')}
    if actual!={r['execution']:r['execution_sha256']for r in rows}:lm.append('ALL_ACTUAL_CROSSDATE_EXECUTIONS')
    for row in rows:
        p=ROOT/row['execution'];execution=read(p)
        if sha(p)!=row['execution_sha256']or execution['wall_s']!=row['wall_s']or execution['cpu_s']!=row['cpu_s']:lm.append({'run':row['run_id'],'reason':'EXECUTION_HASH_OR_OWN_COST'})
    for key in('wall_s','cpu_s'):
        total=math.fsum(r.get('charged_'+key,r[key])for r in rows)
        if ledger['conservative_r2_sum_'+key]!=total or ledger['r2_remaining'][key]!=ledger['r2_caps'][key]-total:lm.append({'field':key,'reason':'CHARGED_FSUM_OR_REMAINING'})
        for category,engineering_only in (('science',False),('engineering',True)):
            subtotal=math.fsum(r.get('charged_'+key,r[key])for r in rows if r['engineering_only']is engineering_only)
            if ledger.get(category+'_'+key)!=subtotal:lm.append({'field':category+'_'+key,'reason':'CHARGED_CLASSIFICATION_FSUM'})
    if ledger['r2_caps']!={'wall_s':3600.,'cpu_s':7200.}:lm.append('ORIGINAL_R2_CAPS')
    if ledger['science_count']!=32 or ledger['engineering_count']!=11 or sum(r['engineering_only']is False for r in rows)!=32 or sum(r['engineering_only']is True for r in rows)!=11:lm.append('EXPECTED32_SCIENCE11_ENGINEERING')
    for old in oldledger['executions']:
        if next(r for r in rows if r['execution']==old['execution'])!=old:lm.append({'run':old['run_id'],'reason':'OLD_V24_ROW_CHANGED'})
    tail=next(r for r in rows if r['run_id']==RUN);pe=read(ROOT/tail['execution'])
    if ledger.get('last_actual_execution')!=tail:lm.append('ACTUAL_LAST_EXECUTION_BINDING')
    if pe.get('schema')!='P4_R2_ABB_SBL_PCS_SETUP01_EXECUTION_V3' or pe['run_id']!=RUN or pe['classification']!=CLASSIFICATION or tail['classification']!=CLASSIFICATION or tail['engineering_only']is not False or pe['status']!=RAW_STATUS or tail['status']!=RAW_STATUS:lm.append('ACTUAL_SCIENTIFIC_SETUP_ONLY_STATUS_CLASSIFICATION')
    for field,want in {'setup_calls':1,'public_project_calls':13,'solve_calls':0,'binary_execution_calls':1,'formal_table_I_calls':0,'new_VI_candidate_constructions':0}.items():
        if type(pe.get(field))is not int or pe[field]!=want:lm.append({'field':field,'reason':'EXACT_SETUP_PUBLIC13_NO_SOLVE_COUNTS'})
    if pe.get('zero_calls')!=ZERO_CALLS or any(type(v)is not int for v in pe.get('zero_calls',{}).values()):lm.append('EXACT_ZERO_CALLS_SAVED_SCOPE')
    if pe.get('external_supervision_qualified')is not False or pe.get('independent_path_qualified')is not False or pe.get('independent_saved_POST_required')is not True:lm.append('RAW_UNQUALIFIED_FLAGS_RETAINED')
    if pe.get('complete_source_raw_evidence_gate')is not True or pe.get('diagnostics')!=[]:lm.append('COMPLETE_SOURCE_EOF_REAP_RAW_GATE_REQUIRED')
    registry=pe.get('source_process_registry',[]);lifecycle=pe.get('source_lifecycle',{})
    if len(registry)!=1 or any(p.get('reaped')is not True or p.get('returncode')!=0 or p.get('actual_after_reap_group')!=[] for p in registry):lm.append('ONE_REAPED_SUCCESSFUL_EMPTY_SOURCE_GROUP_REQUIRED')
    if lifecycle.get('actual_pipe_EOF_observed')!={'stdout':True,'stderr':True} or lifecycle.get('actual_after_reap_group')!=[] or lifecycle.get('stdin_closed_after_unique_request')is not True or lifecycle.get('actual_request_sent')!=lifecycle.get('request_bytes') or not isinstance(lifecycle.get('request_bytes'),int) or lifecycle['request_bytes']<=0:lm.append('SOURCE_SINGLE_COMPLETE_REQUEST_STDIN_EOF_AND_DUAL_OUTPUT_EOF')
    counts=pe.get('counts',{})
    for field in ('source_process_start_attempted','source_process_started','setup_dispatch_attempted','setup_dispatched','stdout_complete_lines_observed','raw_response_lines_observed'):
        if type(counts.get(field))is not int or counts[field]!=1:lm.append({'field':field,'reason':'EXACT_SINGLE_SOURCE_SETUP_TRANSPORT'})
    if pe.get('actual_source_started')!={'mesh_load':1,'freeGridMotions':2} or pe.get('actual_source_completed')!=pe.get('actual_source_started'):lm.append('COMPLETE_NATIVE_SETUP_BODY_TRACE_PAIRS')
    if pe.get('original_native_output_sha256')!={} or pe.get('original_native_output_fsync_completed')!=[]:lm.append('SETUP_MUST_NOT_PRODUCE_PLANNING_OUTPUTS')
    if absolute(tail['external_post']).resolve()!=post_path.resolve() or tail['external_post_sha256']!=args.external_post_sha256 or post['execution_sha256']!=tail['execution_sha256'] or absolute(post['execution']).resolve()!=(ROOT/tail['execution']).resolve():lm.append('REAL_SETUP_POST_EXECUTION_BINDING')
    for field in ('execution','protocol','claim','receipt','internal_receipt','external_time'):
        p=absolute(post[field])
        if sha(p)!=post[field+'_sha256']:lm.append({'field':field,'reason':'ACTUAL_POST_CHAIN_HASH'})
    retained=post.get('retained_sha256')
    if not isinstance(retained,dict) or not retained:lm.append('ACTUAL_POST_RETAINED_ASSETS_REQUIRED')
    else:
        for name,want in retained.items():
            if sha(absolute(name))!=want:lm.append({'path':name,'reason':'POST_RETAINED_ASSET_CHANGED'})
    if pe['bound_files_sha256']!=pe['bound_files_after_sha256']:lm.append('SETUP_BOUND_MAP_CHANGED')
    for name,want in pe['bound_files_sha256'].items():
        if sha(absolute(name))!=want:lm.append({'path':name,'reason':'SETUP_BOUND_ASSET_CHANGED'})
    for field in ('protocol','claim'):
        if pe.get(field+'_sha256')!=sha(ROOT/pe[field]) or pe.get(field+'_after_sha256')!=pe[field+'_sha256']:lm.append({'field':field,'reason':'SETUP_PROTOCOL_OR_CLAIM_CHANGED'})
        if absolute(post[field]).resolve()!=(ROOT/pe[field]).resolve() or post[field+'_sha256']!=pe[field+'_sha256']:lm.append({'field':field,'reason':'ACTUAL_SETUP_POST_PROTOCOL_CLAIM_BINDING'})
    spec=read(ROOT/pe['protocol'])
    if spec.get('schema')!='P4_R2_ABB_SBL_PCS_SINGLE_SETUP_DRAFT_V1' or spec.get('frozen')is not True or not spec.get('reviews') or not all(v is True for v in spec['reviews'].values()) or spec.get('zero_calls')!=ZERO_CALLS or spec.get('run_id')!=RUN:lm.append('ACTUAL_FROZEN_REVIEWED_SETUP_PROTOCOL_REQUIRED')
    if spec.get('maxima')!={'new_source_processes':1,'source_requests':1,'setup_calls':1,'public_project_calls':13,'solve_calls':0,'seed':7}:lm.append('FROZEN_SINGLE_SETUP_PUBLIC13_MAXIMA')
    if pe.get('budget')!=spec.get('budget') or spec['budget'].get('wall_s')!=10. or spec['budget'].get('cpu_s')!=20.:lm.append('ORIGINAL_SETUP_10W20CPU_CAPS')
    built=spec['build_assets']
    for field in ('manifest','personnel_independent_POST'):
        bp=absolute(built[field]);want=built[field+'_sha256']
        if sha(bp)!=want or not isinstance(retained,dict) or retained.get(str(bp),retained.get(str(bp.relative_to(ROOT)) if bp.is_relative_to(ROOT) else str(bp)))!=want:lm.append({'field':field,'reason':'ACTUAL_BUILD_ANCESTOR_RETAINED_SHA_REQUIRED'})
    if spec.get('actual_charge_prior')!=pe.get('actual_charge_prior') or pe.get('prior_execution_sha256')!=pe.get('prior_execution_after_sha256'):lm.append('SETUP_PRIOR_LEDGER_OR_EXECUTIONS_CHANGED')
    if spec['actual_charge_prior'].get('ledger')!=str(oldledger_path.relative_to(ROOT)) or spec['actual_charge_prior'].get('ledger_sha256')!=sha(oldledger_path):lm.append('SETUP_EXACT_V24_CHARGED_PRIOR')
    if pe.get('runtime_mesh_sha256')!=pe.get('runtime_mesh_after_sha256') or len(pe.get('runtime_mesh_sha256',{}))!=20:lm.append('20_RUNTIME_MESHES_PRESERVED')
    for name,want in pe.get('runtime_mesh_sha256',{}).items():
        if sha(absolute(name))!=want:lm.append({'path':name,'reason':'RUNTIME_MESH_CHANGED'})
    mapped=pe.get('actual_loaded_project_symbol_scope',{}).get('mapped_files_sha256',{})
    if not mapped or pe.get('mapped_files_after_sha256')!=mapped:lm.append('ACTUAL_LOADED_MAPS_REQUIRED_AND_UNCHANGED')
    for name,want in mapped.items():
        if sha(absolute(name))!=want:lm.append({'path':name,'reason':'ACTUAL_MAPPED_FILE_CHANGED'})
    metadata=pe.get('actual_setup_metadata',{})
    if metadata.get('public_project_observation_count')!=13 or metadata.get('projection_observer_RNG_draws')!=0 or metadata.get('actual_setup_library_RNG_draws')!='UNOBSERVED' or metadata.get('original_solve_entry_available')is not False:lm.append('PUBLIC13_OBSERVER_SCOPE_NOT_SOLVE_OR_INTERNAL_RNG_QUALIFICATION')
    related={'P4-T02','P4-T05','P4-T08','P4-T11','P4-T17','P4-T25'}
    if set(ledger.get('coverage_related_item_ids',[]))!=related:coverage_m.append('EXPLICIT_SBL_SETUP_RELATED_IDS')
    for row in nrr:
        if row['item_id']in related:
            if row['v25_execution']!=tail['execution']:coverage_m.append({'item':row['item_id'],'reason':'SETUP_EXECUTION_BINDING'})
        elif row['v25_status']!='NO_NEW_EVIDENCE_FOR_THIS_OBLIGATION'or row['v25_execution']!='NOT_APPLICABLE':coverage_m.append({'item':row['item_id'],'reason':'UNRELATED_SETUP_EVIDENCE'})
    if any(row['v25_ledger']!=str(ledger_path.relative_to(ROOT)) for row in nrr):coverage_m.append('ACTUAL_V25_LEDGER_COLUMN_BINDING')
    timep=ROOT/tail['external_time'];fields=timep.read_text().split()
    if len(fields)!=4:raise RuntimeError('EXACT_FOUR_ACTUAL_EXTERNAL_TIME_FIELDS')
    elapsed,user,system=(Decimal(v)for v in fields[:3])
    if fields[3]!='0'or not all(v.is_finite()and v>=0 for v in(elapsed,user,system)):lm.append('SUCCESSFUL_FINITE_NONNEGATIVE_EXTERNAL_TIME_REQUIRED')
    if sha(timep)!=tail['external_time_sha256']or sha(timep)!=post['external_time_sha256']:lm.append('EXTERNAL_TIME_HASH_CHANGED')
    if tail['charged_wall_s']!=float(elapsed+Decimal('.01'))or tail['charged_cpu_s']!=float(user+system+Decimal('.02'))or tail['charged_wall_s']!=post['upper_wall_s']or tail['charged_cpu_s']!=post['upper_cpu_s']:lm.append('ACTUAL_EXTERNAL_UPPER_REPLACES_INTERNAL_ONCE')
    if tail['charged_wall_s']>10. or tail['charged_cpu_s']>20.:lm.append('SETUP_EXTERNAL_UPPER_WITHIN_FROZEN_CAPS')
    if ledger['vi_B_consumed']!=oldledger['vi_B_consumed']or ledger['vi_B_remaining']!=oldledger['vi_B_remaining']or ledger['vi_B_candidate_cap']!=974 or ledger['vi_B_consumed']['candidate_constructions']!=974 or ledger['vi_B_remaining']['candidate_constructions']!=0:lm.append('VI974_EXHAUSTED_HISTORY_CHANGED')
    if ledger['formal_table_I_calls']!=0 or ledger['formal_table_I_required_calls']!=22500:lm.append('FORMAL_ZERO_22500_OBLIGATIONS')
    addp=ROOT/'results/p4_full/20261016_RECOVERY_QUALIFICATION_SOLVE_ACCOUNTING_V22_ADDENDUM.json';add=read(addp)
    if sha(addp)!='316024926cbd63e1f6ca53db0be6d7cc4419b9cb3b029450f642e3529f87bcb9':lm.append('IMMUTABLE_V22_ACTUAL_SOLVE_ADDENDUM')
    sa=ledger['authoritative_source_solve_accounting'];enum=sa['actual_source_solve_dispatches_by_execution']
    if sa['schema']!='P4_ACTUAL_SOURCE_SOLVE_ACCOUNTING_V1'or sa['executions_enumerated']!=43 or len(enum)!=43 or sa['previous_actual_source_solve_dispatches']!=5 or sa['new_actual_source_solve_dispatches']!=0 or sa['total_actual_source_solve_dispatches']!=5 or sa['ledger_generation_new_source_solve_dispatches']!=0:lm.append('FIVE_ACTUAL_SOURCE_SOLVES_UNCHANGED_NO_SETUP_SOLVE')
    if sa['baseline_addendum']!=str(addp.relative_to(ROOT))or sa['baseline_addendum_sha256']!=sha(addp)or sa['previous_snapshot']!=str(oldledger_path.relative_to(ROOT))or sa['previous_snapshot_sha256']!=sha(oldledger_path):lm.append('SOURCE_COUNT_REAL_BASE_BINDING')
    if {z['execution']:z['execution_sha256']for z in enum}!={r['execution']:r['execution_sha256']for r in rows}:lm.append('ALL43_SOURCE_COUNT_ROWS_ENUMERATED')
    positive={z['execution']['path']:z for z in add['actual_source_solve_dispatches']}
    for z in enum:
        expected_count=positive[z['execution']]['actual_source_solve_dispatches']if z['execution']in positive else 0
        if type(z['actual_source_solve_dispatches'])is not int or z['actual_source_solve_dispatches']!=expected_count:lm.append({'run':z['run_id'],'reason':'ACTUAL_SOURCE_COUNT_CHANGED'})
        if z['new_since_previous_snapshot']is not(z['run_id']==RUN):lm.append({'run':z['run_id'],'reason':'ACTUAL_SOURCE_NEW_FLAG'})
        if z['run_id']==RUN and z['saved_dispatch_fields'].get('solve_calls')!=0:lm.append('SETUP_EXPLICIT_ZERO_SOLVE')
    if ledger.get('total_qualification_planner_solves')!=5 or ledger.get('new_qualification_planner_solves_in_this_snapshot')!=0 or ledger.get('previous_snapshot_qualification_planner_solves')!=5:lm.append('CURRENT_SOURCE_COUNTERS')
    history=[];hm=[]
    for name,want in HISTORY_SHA.items():
        p=ROOT/name;blob=subprocess.check_output(['git','show',HISTORY_HEAD+':'+name],cwd=ROOT)
        ok=hashlib.sha256(blob).hexdigest()==sha(p)==want
        history.append(dict(path=name,sha256=sha(p),fixed_sha256=want,matches_c7142055=ok))
        if not ok:hm.append(name)
    passed=baseline_contract and not(oldm or crashm or archive_m or otherm or coverage_m or lm or hm)and archive['sha_matches']and len(orr)==len(nrr)==211 and len(other)==5 and sum(z['preserved_uncommitted_files']for z in other)==13 and len(crash)==57
    result=dict(schema='P4_RECOVERY_IMMUTABLE_VERIFICATION_V25',created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),head_at_verification=git(ROOT,'rev-parse','HEAD').strip(),analysis_source=str(Path(__file__).resolve()),analysis_source_sha256=sha(__file__),baseline_manifest=str(BASE.relative_to(ROOT)),baseline_manifest_sha256=sha(BASE),old_scientific_files=len(b['files']),old_scientific_mismatches=oldm,crash_uncommitted_files=len(crash),crash_uncommitted_bytes=sum(z['bytes']for z in crash),crash_uncommitted_mismatches=crashm,external_archive=archive,other_worktrees=len(other),other_uncommitted_files=sum(z['preserved_uncommitted_files']for z in other),other_worktree_results=other,other_worktree_mismatches=otherm,
        coverage=dict(old_csv=str(old_csv.relative_to(ROOT)),new_csv=str(new_csv.relative_to(ROOT)),old_sha256=sha(old_csv),new_sha256=sha(new_csv),rows=len(nrr),previous_columns_preserved=len(oh),new_column_count=len(nh),tableI_cells=len(formal),formal_trials=0,formal_required=22500,mismatches=coverage_m),ledger=dict(path=str(ledger_path.relative_to(ROOT)),sha256=sha(ledger_path),count=len(rows),science_count=ledger['science_count'],engineering_count=ledger['engineering_count'],r2_remaining=ledger['r2_remaining'],mismatches=lm),scientific_setup=dict(run_id=RUN,execution=tail['execution'],execution_sha256=tail['execution_sha256'],raw_status=pe['status'],actual_post=str(post_path),actual_post_sha256=sha(post_path),actual_independent_checks=post['checks_total'],setup_calls=1,public_project_calls=13,solve_calls=0,independent_path_qualified=False),authoritative_source_solve_accounting=dict(previous=5,new=0,total=5,executions_enumerated=43),historical_snapshots=history,historical_mismatches=hm,preservation_new_scientific_calls=0,analysis_cost=dict(wall_s=time.monotonic()-start_wall,cpu_s=time.process_time()-start_cpu),passed=passed)
    with OUT.open('x')as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(passed=passed,path=str(OUT),mismatches=[oldm,crashm,archive_m,otherm,coverage_m,lm,hm]),ensure_ascii=False))

if __name__=='__main__':
    main()
