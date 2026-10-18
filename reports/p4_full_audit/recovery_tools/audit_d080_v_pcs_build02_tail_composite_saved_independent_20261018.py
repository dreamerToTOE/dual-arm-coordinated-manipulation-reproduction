#!/usr/bin/env python3
"""Saved-only independent same-source V BUILD02 tail composite POST; no runner/model/transform import.

Requires actual finished run and exact root-frozen protocol SHA. Never builds,
queries, makes protocols/claims, or re-runs prior body/pair/static certificates.
"""
from pathlib import Path
from decimal import Decimal
import argparse
import datetime
import hashlib
import json
import math
import os
import re
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[3]
RUN='20261018_R2_D080_V_PCS_BUILD02_TAIL'
OUT=ROOT/'reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_COMPOSITE_SAVED_INDEPENDENT_POST_20261018.json'
MERGED='reports/P4_D080_ENV_V_PCS_ENGINEERING_MERGED_INDEPENDENT_PRE_20261018.json'
MERGED_SHA='87e7843147fbb97c987b8b16a1722c98e9fbd75616ca362008855d672e2e68e4'
BODY='reports/P4_D080_ENV_V_PCS_INDEPENDENT_BODY_PAIR_STATIC_20261017.json'
BODY_SHA='ec7e0fce89e98a052efbd0c34eb32ac41f1da43519cfac33cdb5537c59af9a75'
HELPER='reports/P4_D080_ENV_V_PCS_MANIFEST_HELPER_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
HELPER_SHA='12d49c4c60a76a11d6fe78bfe0ac49fb5c4e52d112a5a9e8f876fe039a1e7f9c'
BUILDER='scripts/p4_d080/build_v_pcs_build02_tail_v1_draft.py'
SUPERVISOR='scripts/p4_d080/supervise_v_pcs_build02_tail_v1_draft.py'
HELPER_SOURCE='scripts/p4_d080/prepare_v_pcs_build_manifest_v1_draft.py'
COMPAT='reports/P4_D080_ENV_V_PCS_MONOTONIC_COMPAT_INDEPENDENT_PRE_20261018.json'
COMPAT_SHA='3f357584a3413b43eb2d2bc20465121a3a494579a824ce4a4eaa0dee27c58a7d'
PRESERVED=ROOT/'work/preserved_v_pcs_engineering_before_monotonic_envelope_20261018'
BASIS='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_build02')
OLD_STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1')
PREFIX='reports/P4_D080_ENV_V_PCS_BUILD01_FAILURE_SAVED_INDEPENDENT_POST_20261018.json'
PREFIX_SHA='3dca76842b2f50751bd9c0455b592dff89dd4dbf7c09fbf7dfcf72c487d9576a'
STATIC='reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_INCREMENTAL_INDEPENDENT_PRE_ADDENDUM_20261018.json'
STATIC_SHA='f9dbccfc47da7f3931b7c0575dd08f68af4b7cee62a16eda559809b724399a1f'
AUTHOR=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/ckcComau_industrialScene')
APC=ROOT/'build/p4_full/20261015_R2_SPATIAL01/ckcComau_industrialScene'
COL=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/V_aligned')
PQP=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3')
SCIENCE=('comau_v_pcs_observation_v1_draft.hpp','comau_v_pcs_local_driver_v1_draft.cpp','comau_v_pcs_instrumentation_v1_draft.py')
SOURCE_KEYS=('proj_classes/apc_class.cpp','validity_checkers/StateValidityCheckerPCS.cpp','validity_checkers/collisionDetection.cpp','planners/RRT_PCS.cpp','planners/RRT_PCS.h')
checks=[];retained={}
def path(n):
    p=Path(n);return p if p.is_absolute()else ROOT/p

def raw(n):
    p=path(n);data=p.read_bytes();retained[str(p)]=hashlib.sha256(data).hexdigest();return data

def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def load(n):return json.loads(raw(n))
def ck(group,label,ok):checks.append(dict(group=group,check=label,passed=bool(ok)))
def digest_map(values):return {n:sha(n)for n in values}
def group_members(pgid):
    result=[]
    for p in Path('/proc').glob('[0-9]*/stat'):
        try:
            fields=p.read_text().rsplit(')',1)[1].split()
            if int(fields[2])==pgid:result.append(int(p.parent.name))
        except(OSError,ValueError,IndexError):pass
    return sorted(result)


def dependency_rule(data):
    # Reuse independent BUILD02 lexer. Read original gcc -MD bytes only;
    # do not invoke implementation's shlex parser or compiler.
    if not data.endswith(b'\n')or b'\r'in data or b'$'in data or b'#'in data:raise ValueError('EXACT_SUPPORTED_GCC_MD_BYTES_REQUIRED')
    logical=data.replace(b'\\\n',b' ').rstrip(b'\n')
    lexer=re.compile(rb'(?:\\[ \t#:\\]|[^ \t\r\n\\#$:\x00-\x1f\x7f])+|:')
    matches=list(lexer.finditer(logical));offset=0;tokens=[]
    for match in matches:
        if logical[offset:match.start()].strip(b' \t'):raise ValueError('UNPARSED_GCC_MD_BYTES')
        value=match.group();offset=match.end()
        if value!=b':':value=re.sub(rb'\\([ \t#:\\])',lambda m:m.group(1),value)
        tokens.append(value)
    if logical[offset:].strip(b' \t')or tokens.count(b':')!=1 or tokens.index(b':')!=1 or len(tokens)<3:raise ValueError('EXACT_ONE_TARGET_NONEMPTY_GCC_MD_RULE_REQUIRED')
    return Path(os.fsdecode(tokens[0])).resolve(),[Path(os.fsdecode(v)).resolve(strict=True)for v in tokens[2:]]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--protocol',required=True);ap.add_argument('--protocol-sha256',required=True);ap.add_argument('--expected-source-commit',required=True)
    args=ap.parse_args();protocol=path(args.protocol).resolve();protocol_name=str(protocol.relative_to(ROOT))
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_COMPOSITE_POST_PRESERVED_NO_OVERWRITE')
    epath='results/p4_full/'+RUN+'/execution.json';e=load(epath);p=load(protocol);folder=path(epath).parent
    claim=str((folder/'claim.json').relative_to(ROOT));c=load(claim);internal=str((folder/'cost_receipt.json').relative_to(ROOT));i=load(internal)
    ext=p['external_supervision'];charge=ext['charge_path'];r=load(charge);prefix=load(PREFIX);static=load(STATIC)
    ck('static','exact independent incremental addendum5 with prior44 reused',sha(STATIC)==STATIC_SHA and static['personnel_independent']is True and static['checks_total']==static['checks_passed']==5 and static['checks_failed']==0 and static['base_passed_checks_reused_without_rerun']==44)
    for name in(BUILDER,SUPERVISOR,'reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_PRE_DRAFT_20261018.md'):
        ck('static','same reviewed tail source '+name,sha(name)==static['source_sha256'][name])
    ck('prefix','reuse exact independent first-collected17 failure78 without8TU reaudit',sha(PREFIX)==PREFIX_SHA and prefix['schema']=='P4_D080_V_PCS_BUILD01_FAILURE_SAVED_INDEPENDENT_POST_V1'and prefix['personnel_independent']is True and prefix['checks_total']==prefix['checks_passed']==78 and prefix['checks_failed']==0 and prefix['engineering_build_qualified']is False and prefix['completed_translation_units']==8 and len(prefix['reusable_saved_build_assets'])==17 and prefix['original_STOP_object_sha256_status']=='UNKNOWN_NOT_RECORDED_AT_STOP')
    olde=load(prefix['execution']);ck('prefix','original BUILD01 STOP and object UNKNOWN never promoted',sha(prefix['execution'])==prefix['execution_sha256']==e['original_BUILD01_execution_sha256']and olde['status']==prefix['original_execution_status']==e['original_BUILD01_status_retained']=='STOP_ENGINEERING_FAILURE_RETAINED_PREFIX'and olde['error']==prefix['original_error']=='RuntimeError: BUILD_WORKING_CAP40W80CPU_RESERVE_FINAL45W90CPU'and e['original_STOP_object_sha256_status']=='UNKNOWN_NOT_RECORDED_AT_STOP')
    ck('freeze','exact committed root frozen protocol SHA and unique expected commit',sha(protocol)==args.protocol_sha256==e['protocol_sha256']==e['protocol_after_sha256']and e['source_commit']==c['source_commit']==args.expected_source_commit)
    ck('freeze','frozen engineering only V20/40 work15/30',p['schema']=='P4_D080_V_PCS_BUILD02_TAIL_FROZEN_V1'and p['frozen']is p['engineering_execution_authorized']is p['independent_review_passed']is True and p['scientific_execution_authorized']is p['formal_execution_authorized']is False and p['environment']=='V'and p['run_name']==RUN and p['stage_root']==str(STAGE)and p['budget']==e['budget']==dict(wall_s=20,cpu_s=40)and p['working_budget']==e['working_budget']==dict(wall_s=15,cpu_s=30))
    draft=load(static['draft_protocol']);cmp=dict(p);cmp['bound_files_sha256']=dict(cmp['bound_files_sha256'])
    for k in('frozen','engineering_execution_authorized','independent_review_passed'):cmp[k]=False
    ck('freeze','frozen draft differs only3 flags and additive exact independent certificate binding',cmp['bound_files_sha256'].pop(str(path(STATIC)),None)==STATIC_SHA and cmp==draft and sha(static['draft_protocol'])==static['draft_protocol_sha256'])
    ck('build','new tail successful with original prefix still a failure',e['schema']=='P4_D080_V_PCS_BUILD02_TAIL_EXECUTION_V1'and e['run_id']==e['run_name']==RUN and e['status']==i['status']=='BUILT_TAIL_NOT_QUERIED_PENDING_COMPOSITE_INDEPENDENT_POST'and e['engineering_only']is True and e['execution_type']=='engineering'and e['author_original_planning_qualified']is False and e['source_failure_POST']==PREFIX and e['source_failure_POST_sha256']==PREFIX_SHA and e['diagnostics']==[]and e['source_transform_calls']==0 and e['new_translation_units_expected']==2 and e['reused_translation_units_expected']==8)
    ck('claim','exclusive original STARTED record immutable',c['status']=='STARTED'and c['run_id']==RUN and c['protocol_sha256']==sha(protocol)and sha(claim)==e['claim_sha256']==e['claim_after_sha256'])
    for name in(BUILDER,SUPERVISOR,'reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_PRE_DRAFT_20261018.md','scripts/p4_d080/build_v_pcs_local_v1_draft.py',PREFIX,protocol_name):
        ck('commit','actual committed current bytes '+name,subprocess.check_output(['git','show',e['source_commit']+':'+name],cwd=ROOT)==raw(name))
    ck('frozen','all prebound current exact and final map',e['bound_files_sha256']==e['bound_files_after_sha256']==p['bound_files_sha256']and digest_map(p['bound_files_sha256'])==p['bound_files_sha256'])
    ck('frozen','new object executable dependency bytes immutable',digest_map(e['staged_after_sha256'])==e['staged_after_sha256']and digest_map(e['dependencies_after_sha256'])==e['dependencies_after_sha256'])
    assets=prefix['reusable_saved_build_assets'];assetdoc=load(folder/'reused_first_collected_assets.json')
    ck('prefix','saved first-collected assets exact no fabricated historical hashes',e['reused_saved_build_assets']==assets and assetdoc==dict(source_POST=PREFIX,source_POST_sha256=PREFIX_SHA,assets=assets,original_STOP_object_sha256_status='UNKNOWN_NOT_RECORDED_AT_STOP')and e['original_staged_and_dependency_sha256']=={**olde['staged_after_sha256'],**olde['dependencies_after_sha256']})
    after=[]
    for row in assets:
        f=path(row['path']);st=f.stat();after.append(dict(path=str(f),sha256=sha(f),size_bytes=st.st_size,mtime_ns=st.st_mtime_ns))
        ck('reuse','firstcollected same bytes size mtime '+row['path'],sha(f)==row['sha256']and st.st_size==row['size_bytes']and st.st_mtime_ns==row['mtime_ns'])
    ck('reuse','all17 identities after exactly recorded',after==e['reused_saved_build_assets_after'])
    ck('reuse','original failed or unstarted trace artifacts remain absent',all(not(OLD_STAGE/'trace'/n).exists()for n in('3_collisionDetection.o','3_collisionDetection.d','4_RRT_PCS.o','4_RRT_PCS.d','v_pcs_local')))
    ck('prior','before after exact frozen actual prior',e['prior']==e['prior_after']and e['prior']['path']==p['prior']['ledger']and e['prior']['sha256']==p['prior']['ledger_sha256']and e['prior']['wall_s']==p['prior']['wall_s']and e['prior']['cpu_s']==p['prior']['cpu_s'])
    prior=load(p['prior']['ledger']);actual={str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if q.parent.name!=RUN}
    actual.update({str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_d080').glob('*/execution.json')})
    ck('prior','prior actual execution set and original charge replacement sums exact',sha(p['prior']['ledger'])==p['prior']['ledger_sha256']and actual=={z['execution']:z['execution_sha256']for z in prior['executions']}and math.fsum(z.get('charged_wall_s',z['wall_s'])for z in prior['executions'])==p['prior']['wall_s']and math.fsum(z.get('charged_cpu_s',z['cpu_s'])for z in prior['executions'])==p['prior']['cpu_s'])
    ck('prior','all prior certificate log evidence prebound current',digest_map(e['prior']['evidence_sha256'])==e['prior']['evidence_sha256']and all(p['bound_files_sha256'].get(n)==w for n,w in e['prior']['evidence_sha256'].items()))
    plain,trace=e['targets'];oldplain=olde['targets'][0];oldtrace=olde['targets'][1]
    ck('target','plain exact old ELF reused without new command',plain['mode']=='plain'and plain['status']=='REUSED_BUILT_NOT_QUERIED'and plain['binary']==oldplain['binary']and plain['binary_sha256']==oldplain['binary_sha256']==sha(plain['binary'])and plain['source_execution']==prefix['execution']and plain['source_execution_sha256']==prefix['execution_sha256']and plain['new_commands']==[]and plain['new_compile_calls']==plain['binary_execution_calls']==0)
    commands=trace['commands'];dependencies={};missing=[];tu_count=0;objects=[];dest=STAGE/'trace';oldtr=OLD_STAGE/'trace'
    ck('target','trace exact2 compile plus link unqueried',trace['mode']=='trace'and trace['status']=='BUILT_NOT_QUERIED'and trace['binary_execution_calls']==0 and trace['reused_old_object_count']==3 and trace['source_sha256']==oldtrace['source_sha256']and [x['argv']for x in commands]==p['commands']and len(commands)==3 and len(trace['dependencies'])==2 and all(x['returncode']==0 and x['cwd']==str(oldtr)for x in commands))
    frozen={str(Path(n).resolve()):w for n,w in p['bound_files_sha256'].items()}
    protected=(ROOT,STAGE,OLD_STAGE,AUTHOR,APC,COL,PQP,Path('/opt/ros/humble/include/ompl-1.7'),Path('/usr/include/boost'),Path('/usr/include/eigen3'),Path('/usr/include/nlohmann'))
    oldflags=oldtrace['commands'][3]['argv'][:-9]
    for index,(rel,row,cmdrow)in enumerate(zip(('validity_checkers/collisionDetection.cpp','planners/RRT_PCS.cpp'),trace['dependencies'],commands[:2]),3):
        src=oldtr/rel;obj=dest/(str(index)+'_'+src.stem+'.o');dep=obj.with_suffix('.d');target_path,ps=dependency_rule(raw(dep));tu_count+=1;observed={str(q):sha(q)for q in ps};dependencies.update(observed);dependencies[str(dep.resolve())]=sha(dep);objects.append(obj)
        ck('command','new TU'+str(index)+' original flags source only new outputs',cmdrow['argv']==oldflags+['-MD','-MF',str(dep),'-MT',str(obj),'-c',str(src),'-o',str(obj)])
        ck('dependency','new TU'+str(index)+' exact actual MD and independent dependency parse',row['raw_path']==str(dep.relative_to(STAGE))and row['raw_sha256']==sha(dep)and row['target']==str(obj)and row['source']==str(src)and target_path==obj.resolve()and ps[0]==src.resolve()and row['actual_dependencies_sha256']==observed)
        missing.extend(n for n,w in observed.items()if any(Path(n).is_relative_to(z)for z in protected)and frozen.get(n)!=w)
        data=raw(obj);ck('object','new TU'+str(index)+' saved relocatable ELF64 original final digest',data[:6]==b'\x7fELF\x02\x01'and struct.unpack_from('<H',data,16)[0]==1 and struct.unpack_from('<H',data,18)[0]==62 and e['staged_after_sha256'][str(obj)]==sha(obj))
    ck('dependency','only2 new TUs complete actual protected dependency closure',tu_count==2 and missing==[]and dependencies==e['dependencies_after_sha256']and set(dest.glob('*.d'))=={q.with_suffix('.d')for q in objects}and set(dest.glob('*.o'))==set(objects))
    binary=raw(trace['binary']);newbinary=dest/'v_pcs_local';linked=[oldtr/'0_comau_v_pcs_local_driver_v1_draft.o',oldtr/'1_apc_class.o',oldtr/'2_StateValidityCheckerPCS.o',*objects]
    expectedlink=oldplain['commands'][-1]['argv'][:2]+[str(q)for q in linked]+oldplain['commands'][-1]['argv'][7:-1]+[str(newbinary)]
    ck('binary','new trace ELF64 exact recorded and plain remains original recorded hash',trace['binary']==str(newbinary)and trace['binary_sha256']==sha(newbinary)==e['staged_after_sha256'][str(newbinary)]and binary[:6]==b'\x7fELF\x02\x01'and struct.unpack_from('<H',binary,18)[0]==62 and commands[-1]['argv']==expectedlink)
    ck('frozen','new stage contains exactly2objects2MD and linkedELF',{q for q in dest.iterdir()if q.is_file()}=={*objects,*[q.with_suffix('.d')for q in objects],newbinary}and set(e['staged_after_sha256'])=={str(q)for q in[*objects,newbinary]})
    ck('logs','all6 new compile/link log bytes retained',digest_map(e['compile_log_sha256'])==e['compile_log_sha256']and len(e['compile_log_sha256'])==6)
    groups=e['compiler_groups'];ck('lifecycle','all3 compiler sessions reaped empty exit0',len(groups)==3 and {z['pid']for z in groups}=={z['compiler_pid']for z in commands}and all(z['pid']==z['pgid']and z['reaped']is True and z['returncode_after_cleanup']==0 and z['members_after_cleanup']==[]and not group_members(z['pgid'])for z in groups))
    fields=raw(ext['sibling_path']).decode().strip().split()
    if len(fields)!=4:raise ValueError('EXACT_FOUR_GNUTIME_FIELDS_REQUIRED')
    elapsed,user,system=(Decimal(v)for v in fields[:3]);exitcode=int(fields[3])
    rawwall=elapsed+Decimal('.01');rawcpu=user+system+Decimal('.02')
    observed=(r['fallback_observed_outer_wait_wall_s'],r['fallback_reaped_children_CPU_s'],i['wall_s_through_execution_persistence'],i['cpu_s_through_execution_persistence'])
    values=[Decimal(str(v))for v in observed]
    walls=[rawwall,values[0]+Decimal('.01'),values[2]+Decimal('.01')]
    cpus=[rawcpu,values[1]+Decimal('.02'),values[3]+Decimal('.02')]
    upperwall=float(max(walls));uppercpu=float(max(cpus))
    envelope_components=dict(wall_decimal_s=[str(v)for v in walls],cpu_decimal_s=[str(v)for v in cpus],order=['raw_GNUtime_plus_padding','outer_monotonic_or_reaped_plus_padding','internal_receipt_plus_padding'])
    ck('cost','all raw and monotonic observations finite nonnegative',all(v.is_finite()and v>=0 for v in(elapsed,user,system,*values)))
    ck('cost','exact Decimal max envelope within original local and R2 caps',upperwall<=20 and uppercpu<=40 and upperwall+p['prior']['wall_s']<=3600 and uppercpu+p['prior']['cpu_s']<=7200)
    ck('cost','raw GNUtime kept separately with no lower clock selection',r['raw_GNUtime_upper_wall_s']==float(rawwall)and r['raw_GNUtime_upper_cpu_s']==float(rawcpu)and r['monotonic_envelope_components']==envelope_components and r['monotonic_envelope_valid']is True and r['monotonic_envelope_error']is None and r['charge_basis']==BASIS and r['execution_cap_breach']==dict(wall=False,cpu=False))
    ck('cost','external charge matches time execution receipt and max envelope',r['schema']=='P4_D080_V_PCS_BUILD02_TAIL_EXTERNAL_COST_CHARGE_V1'and r['run_id']==RUN and r['source_execution']==epath and r['execution_sha256']==sha(epath)==i['execution_sha256']and r['receipt']==internal and r['receipt_sha256']==sha(internal)and r['time_file']==ext['sibling_path']and r['time_sha256']==sha(ext['sibling_path'])and r['time_fields']==fields and r['wall_s']==upperwall and r['cpu_s']==uppercpu)
    ck('cost','one actual completed supervision no automatic qualification',r['timing_valid']is r['time_inode_unchanged']is r['wall_CPU_caps_pass']is r['completed_process_exit0']is r['started_attempt']is True and r['time_returncode']==r['measured_child_exit']==exitcode==0 and r['failure']is None and r['external_supervision_qualified']is i['external_supervision_qualified']is False and i['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED')
    lines=raw(ext['metadata_path']).splitlines(keepends=True);events=[json.loads(v)for v in lines];planned,started,reaped=events;proof=e['supervisor_contract'];inode=path(ext['sibling_path']).stat()
    argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/BUILDER),'--build','--protocol',str(protocol)]
    ck('supervision','real launch/reap records and exact argv source protocol',len(events)==3 and [z['event']for z in events]==['planned_launch','time_process_started','time_process_reaped']and planned['run_id']==RUN and planned['protocol']==protocol_name and planned['protocol_sha256']==sha(protocol)and planned['argv']==started['argv']==proof['actual_argv']==argv and started['pid']==reaped['pid']==r['time_process_pid']==proof['actual_time_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid'])
    ck('supervision','real held exclusive inode and first launch hash',planned['time_inode']==proof['time_inode']==inode.st_ino and planned['time_device']==proof['time_device']==inode.st_dev and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and proof['planned_launch_line_sha256']==hashlib.sha256(lines[0]).hexdigest())
    ck('supervision','sources actual time python and outer logs SHA',planned['supervisor_source_sha256']==sha(SUPERVISOR)and planned['runner_sha256']==sha(BUILDER)and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3')and r['metadata']==ext['metadata_path']and r['metadata_sha256']==sha(ext['metadata_path'])and r['stderr']==ext['stderr_path']and r['stderr_sha256']==sha(ext['stderr_path']))
    ck('cost','external full-child upper includes execution persistence',upperwall>=i['wall_s_through_execution_persistence']>=e['wall_s']and uppercpu>=i['cpu_s_through_execution_persistence']>=e['cpu_s']and e['cost_status']=='PROVISIONAL_REQUIRES_EXTERNAL_SUPERVISION_POST_NO_AUTO_CHARGE_REPLACEMENT')
    ck('scope','zero science runtime RNG solve VI formal',all(e[n]==0 for n in('scientific_calls','query_calls','solve_calls','rng_calls','binary_execution_calls'))and p['VI_future_execution_authorized']is p['formal_statistics_authorized']is False and p['D080_original_formal_denominator']==22500 and p['D080_approved_formal_denominator']==18000 and not any(STAGE.rglob('runtime'))and not any(STAGE.rglob('paths')))
    for name,want in list(retained.items()):
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=want:ck('preservation','all saved read bytes stable '+name,False)
    failures=[z for z in checks if not z['passed']];ok=not failures
    targets=[dict(mode='plain',status=plain['status'],binary=plain['binary'],binary_sha256=plain['binary_sha256'],source_execution=prefix['execution'],source_execution_sha256=prefix['execution_sha256'],new_compile_calls=0,new_link_calls=0),dict(mode='trace',status=trace['status'],binary=trace['binary'],binary_sha256=trace['binary_sha256'],source_execution=epath,source_execution_sha256=sha(epath),new_compile_calls=2,new_link_calls=1)]
    report=dict(schema='P4_D080_V_PCS_BUILD02_TAIL_COMPOSITE_SAVED_INDEPENDENT_POST_V1',status='PASS_SAME_SOURCE_COMPOSITE_BUILD02_TAIL_SAVED_POST'if ok else'FAIL_BUILD02_TAIL_COMPOSITE_SAVED_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='/root/sbl_independent_resume independent of tail build implementation',personnel_independent=True,external_supervision_qualified=ok,external_timing_qualified=ok,external_cost_qualified=ok,engineering_build_qualified=ok,composite_build_qualified=ok,original_BUILD01_engineering_build_qualified=False,original_BUILD01_status=olde['status'],source_failure_POST=PREFIX,source_failure_POST_sha256=PREFIX_SHA,source_original_STOP_object_hash_status='UNKNOWN_NOT_RECORDED_AT_STOP',checks=checks,checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),failures=failures,source_commit=e['source_commit'],execution=epath,execution_sha256=sha(epath),protocol=protocol_name,protocol_sha256=sha(protocol),claim=claim,claim_sha256=sha(claim),receipt=charge,receipt_sha256=sha(charge),external_charge_sha256=sha(charge),internal_receipt=internal,internal_receipt_sha256=sha(internal),external_time=ext['sibling_path'],external_time_sha256=sha(ext['sibling_path']),external_time_fields=fields,charge_basis=BASIS,monotonic_envelope_qualified=ok,raw_GNUtime_upper_wall_s=float(rawwall),raw_GNUtime_upper_cpu_s=float(rawcpu),monotonic_envelope_components=envelope_components,upper_wall_s=upperwall,upper_cpu_s=uppercpu,cumulative_charged_wall_s=p['prior']['wall_s']+upperwall,cumulative_charged_cpu_s=p['prior']['cpu_s']+uppercpu,build_targets=targets,reused_translation_units=8,new_translation_units=2,new_link_calls=1,actual_new_dependency_count=len(dependencies),unfrozen_protected_dependencies=sorted(set(missing)),retained_sha256=retained,new_runner_model_import_transform_compile_binary_query_solve_protocol_prior_claim_VI_formal_calls=0,old_firstcollected_failure_checks_reused=78,old_TU_dependency_body_reaudit_calls=0,limits=['Same-source composite engineering result only: plain from retained BUILD01 and trace linked using3 old plus2 new objects.','Original BUILD01 STOP remains failed,8 original object hashes at STOP remain UNKNOWN; first-collected current hashes are not historical before/after claims.','No old8TU rebuild or body/dependency re-audit; exact independent first-collected certificate reused;2 new TU raw MD/objects/link checked saved-only.','No setup/local/RBS/closure/collision/path qualification or binary execution.','Whole-child Decimal envelope with .01/.02 padding; final supervisor own journal/fsync tail excluded.','D080 original22500 versus approved18000 separate; formal unapproved; VI archival974/974.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write('# V BUILD02 尾段同源组合工程独立后审\n\n'+report['status']+'，'+str(report['checks_passed'])+'/'+str(len(checks))+'。\n\n直接复用旧8TU/17首收集资产证书，只核新两trace TU原flags/MD/对象与一次link、3编译组清理、源与旧资产前后身份、三观测Decimal费用。原BUILD01失败和旧对象STOP哈希UNKNOWN永不改判。新compile/binary/query/模型调用全0。\n\n仅同源组合plain+trace工程资格，不代表局部/路径/碰撞科学通过。费用 '+str(upperwall)+' wall / '+str(uppercpu)+' CPU。\n')
    print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failures),failures=failures,upper_wall_s=upperwall,upper_cpu_s=uppercpu),ensure_ascii=False))
    if failures:raise SystemExit(2)

if __name__=='__main__':main()
