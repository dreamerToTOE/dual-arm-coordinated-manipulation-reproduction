#!/usr/bin/env python3
"""Failure-only saved independent V BUILD01 POST; no runner/model/transform import.

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
RUN='20261018_R2_D080_V_PCS_BUILD01'
OUT=ROOT/'reports/P4_D080_ENV_V_PCS_BUILD01_FAILURE_SAVED_INDEPENDENT_POST_20261018.json'
MERGED='reports/P4_D080_ENV_V_PCS_ENGINEERING_MERGED_INDEPENDENT_PRE_20261018.json'
MERGED_SHA='87e7843147fbb97c987b8b16a1722c98e9fbd75616ca362008855d672e2e68e4'
BODY='reports/P4_D080_ENV_V_PCS_INDEPENDENT_BODY_PAIR_STATIC_20261017.json'
BODY_SHA='ec7e0fce89e98a052efbd0c34eb32ac41f1da43519cfac33cdb5537c59af9a75'
HELPER='reports/P4_D080_ENV_V_PCS_MANIFEST_HELPER_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
HELPER_SHA='12d49c4c60a76a11d6fe78bfe0ac49fb5c4e52d112a5a9e8f876fe039a1e7f9c'
BUILDER='scripts/p4_d080/build_v_pcs_local_v1_draft.py'
SUPERVISOR='scripts/p4_d080/supervise_v_pcs_build_v1_draft.py'
HELPER_SOURCE='scripts/p4_d080/prepare_v_pcs_build_manifest_v1_draft.py'
COMPAT='reports/P4_D080_ENV_V_PCS_MONOTONIC_COMPAT_INDEPENDENT_PRE_20261018.json'
COMPAT_SHA='3f357584a3413b43eb2d2bc20465121a3a494579a824ce4a4eaa0dee27c58a7d'
PRESERVED=ROOT/'work/preserved_v_pcs_engineering_before_monotonic_envelope_20261018'
BASIS='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1')
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
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--protocol',required=True);ap.add_argument('--protocol-sha256',required=True)
    args=ap.parse_args();protocol=path(args.protocol).resolve();protocol_name=str(protocol.relative_to(ROOT))
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_POST_PRESERVED_NO_OVERWRITE')
    epath='results/p4_full/'+RUN+'/execution.json';e=load(epath);p=load(protocol);folder=path(epath).parent
    claim=str((folder/'claim.json').relative_to(ROOT));c=load(claim);internal=str((folder/'cost_receipt.json').relative_to(ROOT));i=load(internal)
    ext=p['external_supervision'];charge=ext['charge_path'];r=load(charge);merged=load(MERGED);body=load(BODY);helper=load(HELPER);compat=load(COMPAT)
    ck('freeze','exact committed root frozen protocol SHA',len(args.protocol_sha256)==64 and sha(protocol)==args.protocol_sha256==e['protocol_sha256']==e['protocol_after_sha256'])
    ck('freeze','frozen build-only V identity caps',p['schema']=='P4_D080_V_PCS_BUILD_FROZEN_V1'and p['frozen']is p['engineering_execution_authorized']is p['independent_review_passed']is True and p['scientific_execution_authorized']is p['formal_execution_authorized']is False and p['environment']=='V'and p['run_name']==RUN and p['stage_root']==str(STAGE)and p['budget']==dict(wall_s=45,cpu_s=90))
    ck('reuse','root merged8 and helper16 unchanged',sha(MERGED)==MERGED_SHA and sha(HELPER)==HELPER_SHA and merged['checks_total']==merged['checks_passed']==8 and merged['checks_failed']==0 and helper['checks_total']==helper['checks_passed']==16 and helper['checks_failed']==0 and merged['personnel_independent']is helper['personnel_independent']is True)
    ck('reuse','original219 body pair independent certificate unchanged',sha(BODY)==BODY_SHA and body['checks_total']==body['checks_passed']==219 and body['checks_failed']==0 and body['personnel_independent']is True)
    changed={BUILDER,SUPERVISOR,HELPER_SOURCE}
    merged_expected={str(PRESERVED/n if n in changed else path(n)):want for n,want in merged['source_sha256'].items()}
    helper_expected={str(PRESERVED/n if n in changed else path(n)):want for n,want in helper['reviewed_source_sha256'].items()}
    ck('reuse','historical merged implementation binds preserved engineering bytes',digest_map(merged_expected)==merged_expected)
    ck('reuse','historical helper implementation binds preserved engineering bytes',digest_map(helper_expected)==helper_expected)
    compat_ref=p['monotonic_compatibility_independent_pre'];compat_sources=compat['source_sha256']
    ck('compat','current independent7 compatibility PRE exact frozen path SHA status',sha(COMPAT)==COMPAT_SHA and compat_ref==dict(path=COMPAT,sha256=COMPAT_SHA,status=compat['status'])and compat['schema']=='P4_D080_V_PCS_MONOTONIC_COMPAT_INDEPENDENT_PRE_V1'and compat['status']=='PASS_INCREMENTAL_ENGINEERING_COMPATIBILITY_STATIC_ONLY'and compat['personnel_independent']is True and compat['checks_total']==compat['checks_passed']==7 and compat['checks_failed']==0)
    ck('compat','current three engineering sources exact increment and historical certificates',set(compat_sources)==changed and digest_map(compat_sources)==compat_sources and compat['historical_reviews_reused']==dict(merged_PRE=MERGED_SHA,helper_PRE=HELPER_SHA,body_pair219=BODY_SHA)and p['new_external_charge_basis']==BASIS)
    ck('compat','compat PRE and current source bytes prebound',p['bound_files_sha256'].get(str(path(COMPAT)))==COMPAT_SHA and all(p['bound_files_sha256'].get(str(path(n)))==want for n,want in compat_sources.items()))
    ck('reuse','three scientific sources remain old219 bytes',all(sha('baselines/p4_full/geometry_consistent/'+n)==body['source_sha256']['baselines/p4_full/geometry_consistent/'+n]for n in SCIENCE))
    ck('build','original engineering working-cap STOP and prefix preserved',e['schema']=='P4_D080_V_PCS_BUILD_EXECUTION_V1'and e['run_id']==e['run_name']==RUN and e['status']==i['status']=='STOP_ENGINEERING_FAILURE_RETAINED_PREFIX'and e['error']=='RuntimeError: BUILD_WORKING_CAP40W80CPU_RESERVE_FINAL45W90CPU'and e['engineering_only']is True and e['execution_type']=='engineering'and e['author_original_planning_qualified']is False and len(e['targets'])==2 and e['diagnostics']==[] and e['budget']==p['budget'] and e['working_budget']==dict(wall_s=40,cpu_s=80))
    ck('claim','exclusive original STARTED record binds actual source and frozen protocol',c['status']=='STARTED'and c['run_id']==RUN and c['source_commit']==e['source_commit']and c['protocol_sha256']==sha(protocol)and sha(claim)==e['claim_sha256']==e['claim_after_sha256'])
    committed=[BUILDER,SUPERVISOR,HELPER_SOURCE,COMPAT,protocol_name,*['baselines/p4_full/geometry_consistent/'+n for n in SCIENCE]]
    for name in committed:
        gitbytes=subprocess.check_output(['git','show',e['source_commit']+':'+name],cwd=ROOT)
        ck('commit','actual committed own source '+name,gitbytes==raw(name))
    ck('frozen','all prebound current exact and final bound map',e['bound_files_sha256']==e['bound_files_after_sha256']==p['bound_files_sha256']and digest_map(p['bound_files_sha256'])==p['bound_files_sha256'])
    ck('frozen','final staged and dependency bytes retained',digest_map(e['staged_after_sha256'])==e['staged_after_sha256']and digest_map(e['dependencies_after_sha256'])==e['dependencies_after_sha256'])
    ck('prior','prior before after identical exact frozen values',e['prior']==e['prior_after']and e['prior']['path']==p['prior']['ledger']and e['prior']['sha256']==p['prior']['ledger_sha256']and e['prior']['wall_s']==p['prior']['wall_s']and e['prior']['cpu_s']==p['prior']['cpu_s'])
    prior=load(p['prior']['ledger']);actual={str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if q.parent.name!=RUN}
    actual.update({str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_d080').glob('*/execution.json')})
    ck('prior','latest actual execution identities unchanged excluding current',sha(p['prior']['ledger'])==p['prior']['ledger_sha256']and actual=={z['execution']:z['execution_sha256']for z in prior['executions']})
    ck('prior','effective replacement totals unchanged',math.fsum(z.get('charged_wall_s',z['wall_s'])for z in prior['executions'])==p['prior']['wall_s']and math.fsum(z.get('charged_cpu_s',z['cpu_s'])for z in prior['executions'])==p['prior']['cpu_s'])
    ck('prior','all prior receipt POST log evidence is prebound and current',digest_map(e['prior']['evidence_sha256'])==e['prior']['evidence_sha256']and all(p['bound_files_sha256'].get(n)==v for n,v in e['prior']['evidence_sha256'].items()))
    proof=load(STAGE/'source_transform_manifest.json')
    ck('transform','actual source hash map exactly prior219 independent outputs',proof['input_sha256']==body['input_sha256']and proof['staged_sha256']==body['output_sha256']and proof['whole_input_files_byte_reversible']is True and len(proof['wrappers'])==12 and all(z['full_input_body_unchanged_once']is True for z in proof['wrappers']))
    ck('transform','original87 pair args and RRT search unchanged',proof['active_pair_count']==len(proof['active_pair_identities'])==87 and proof['collision_argument_or_pair_changes']==proof['additional_model_calls']==proof['additional_rng_calls']==0 and proof['RRT_search_source_byte_unchanged']is True and proof['planner_instantiation_permitted']is proof['H_random_helper_correction']is proof['D_CBiRRT_correction']is proof['five_argument_project_correction']is False)
    input_paths={SOURCE_KEYS[0]:APC/SOURCE_KEYS[0],SOURCE_KEYS[1]:AUTHOR/SOURCE_KEYS[1],SOURCE_KEYS[2]:COL/SOURCE_KEYS[2],SOURCE_KEYS[3]:AUTHOR/SOURCE_KEYS[3],SOURCE_KEYS[4]:AUTHOR/SOURCE_KEYS[4]}
    ck('transform','actual input byte identity original or corrected stages',all(sha(q)==body['input_sha256'][name]for name,q in input_paths.items()))
    colmanifest=load(COL.parent/'manifest.json');crow,=[z for z in colmanifest['entries']if z['model']=='V'and z['variant']=='aligned']
    ck('collision','v3 aligned original87/27 provenance reused',crow['active_call_statement_count']==87 and crow['tcp_observation_version']==3 and len(crow['mesh_sha256'])==27 and all(sha(COL/'simulator'/n)==v for n,v in crow['mesh_sha256'].items()))
    dependencies={};tu_count=0;commands=[];missing=[];reusable_saved_build_assets=[]
    def capture_asset(name,kind,mode,original_sha=None,command_index=None):
        filename=path(name);st=filename.stat();data=raw(filename)
        reusable_saved_build_assets.append(dict(path=str(filename),kind=kind,mode=mode,sha256=hashlib.sha256(data).hexdigest(),size_bytes=len(data),mtime_ns=st.st_mtime_ns,mtime_utc=datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat(),first_current_artifact_collection='THIS_SAVED_ONLY_FAILURE_POST',original_STOP_sha256=original_sha,original_STOP_sha256_status='RECORDED_IN_ORIGINAL_EXECUTION'if original_sha else'UNKNOWN_NOT_RECORDED_AT_STOP',corresponding_command_index=command_index,corresponding_saved_returncode=0))
    protected=(ROOT,STAGE,AUTHOR,APC,COL,PQP,Path('/opt/ros/humble/include/ompl-1.7'),Path('/usr/include/boost'),Path('/usr/include/eigen3'),Path('/usr/include/nlohmann'))
    frozen=p['bound_files_sha256'];frozen={str(Path(n).resolve()):v for n,v in frozen.items()};frozen.update(e['staged_after_sha256'])
    driver='comau_v_pcs_local_driver_v1_draft.cpp'
    for index,target in enumerate(e['targets']):
        mode=('plain','trace')[index];stage=STAGE/mode;cmds=target['commands'];deps=target['dependencies'];commands.extend(cmds)
        ck('target',mode+' exact retained build prefix not executed',target['mode']==mode and target['binary_execution_calls']==0 and ((mode=='plain'and target['status']=='BUILT_NOT_QUERIED'and len(cmds)==6 and len(deps)==5 and all(z.get('returncode')==0 for z in cmds))or(mode=='trace'and target['status']=='COMPILING'and len(cmds)==4 and len(deps)==3 and [z.get('returncode')for z in cmds]==[0,0,0,None]))and all(z['cwd']==str(stage)for z in cmds))
        ck('target',mode+' actual5 staged source bytes exactly219 outputs',all(sha(stage/n)==v for n,v in body['output_sha256'].items()))
        ck('target',mode+' all originally staged files current',all(sha(n)==v==e['staged_after_sha256'][n]for n,v in target['source_sha256'].items()))
        expected=[stage/driver,*[stage/n for n in SOURCE_KEYS if n.endswith('.cpp')]]
        for ti,(src,row,cmdrow)in enumerate(zip(expected,deps,cmds[:5])):
            argv=cmdrow['argv'];obj=stage/(str(ti)+'_'+src.stem+'.o');dep=obj.with_suffix('.d');target_path,ps=dependency_rule(raw(dep));tu_count+=1
            observed={str(q):sha(q)for q in ps};dependencies.update(observed);dependencies[str(dep.resolve())]=sha(dep)
            ck('dependency',mode+' TU'+str(ti)+' original MD target/firstsource/exact list',row['raw_path']==str(dep.relative_to(STAGE))and row['raw_sha256']==sha(dep)and row['target']==str(obj)and row['source']==str(src)and target_path==obj.resolve()and ps[0]==src.resolve()and row['actual_dependencies_sha256']==observed)
            ck('command',mode+' TU'+str(ti)+' frozen command exact source flags output',argv[0]=='/usr/bin/x86_64-linux-gnu-g++-11'and argv[1:7]==['-std=c++17','-O2','-Wall','-Wextra','-pthread','-DP4V_TRACE_MODE='+str(index)]and argv[-9:]==['-MD','-MF',str(dep),'-MT',str(obj),'-c',str(src),'-o',str(obj)])
            missing.extend(n for n,v in observed.items()if any(Path(n).is_relative_to(z)for z in protected)and frozen.get(n)!=v)
        ck('dependency',mode+' exact completed compiler MD files without incomplete promotion',set(stage.glob('*.d'))=={stage/(str(j)+'_'+q.stem+'.d')for j,q in enumerate(expected[:len(deps)])})
        if mode=='plain':
            binary=raw(target['binary']);link=cmds[-1]['argv']
            capture_asset(target['binary'],'linked_ELF64_executable',mode,target['binary_sha256'],5)
            ck('binary',mode+' ELF64 x86-64 digest only no execution',target['binary']==str(stage/'v_pcs_local')and sha(target['binary'])==target['binary_sha256']and binary[:6]==b'\x7fELF\x02\x01'and struct.unpack_from('<H',binary,18)[0]==62)
            ck('link',mode+' exact compiler output and all5 object inputs',link[:2]==['/usr/bin/x86_64-linux-gnu-g++-11','-pthread']and link[2:7]==[str(stage/(str(j)+'_'+q.stem+'.o'))for j,q in enumerate(expected)]and link[-2:]==['-o',target['binary']])
        else:
            failed=cmds[-1];failedsrc=expected[3];failedobj=stage/'3_collisionDetection.o';faileddep=failedobj.with_suffix('.d')
            ck('failure','trace collision TU4 interrupted no returncode or incomplete artifact promoted',failed['argv'][-4:]==['-c',str(failedsrc),'-o',str(failedobj)] and 'returncode'not in failed and not failedobj.exists()and not faileddep.exists()and 'binary'not in target and 'binary_sha256'not in target and not(stage/'4_RRT_PCS.o').exists()and not(stage/'v_pcs_local').exists())
        for ti,src in enumerate(expected[:len(deps)]):
            obj=stage/(str(ti)+'_'+src.stem+'.o');objbytes=raw(obj)
            ck('object',mode+' completed TU'+str(ti)+' saved ELF64 relocatable first POST hash',objbytes[:6]==b'\x7fELF\x02\x01'and struct.unpack_from('<H',objbytes,16)[0]==1 and struct.unpack_from('<H',objbytes,18)[0]==62)
            capture_asset(obj,'completed_ELF64_relocatable',mode,None,ti)
            dep=obj.with_suffix('.d');capture_asset(dep,'gcc_MD_dependency',mode,deps[ti]['raw_sha256'],ti)
    ck('dependency','all8 completed TUs no unfrozen actual protected dependency',tu_count==8 and not missing and dependencies==e['dependencies_after_sha256'])
    ck('logs','every compile/link log bytes saved',digest_map(e['compile_log_sha256'])==e['compile_log_sha256']and len(e['compile_log_sha256'])==20)
    groups=e['compiler_groups'];ck('lifecycle','all10 attempted compiler sessions reaped empty including killed collision group',len(groups)==10 and {z['pid']for z in groups}=={z['compiler_pid']for z in commands}and all(z['pid']==z['pgid']and z['reaped']is True and z['members_after_cleanup']==[]and not group_members(z['pgid'])for z in groups)and [z['returncode_after_cleanup']for z in groups]==[0]*9+[-9]and all(z['members_before_cleanup']==[]for z in groups[:9])and groups[-1]['pid']in groups[-1]['members_before_cleanup']and len(groups[-1]['members_before_cleanup'])==2 and groups[-1]['live_group_cpu_before_cleanup_s']>0)
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
    ck('cost','exact Decimal max envelope within original local and R2 caps',upperwall<=45 and uppercpu<=90 and upperwall+p['prior']['wall_s']<=3600 and uppercpu+p['prior']['cpu_s']<=7200)
    ck('cost','raw GNUtime kept separately with no lower clock selection',r['raw_GNUtime_upper_wall_s']==float(rawwall)and r['raw_GNUtime_upper_cpu_s']==float(rawcpu)and r['monotonic_envelope_components']==envelope_components and r['monotonic_envelope_valid']is True and r['monotonic_envelope_error']is None and r['charge_basis']==BASIS and r['execution_cap_breach']==dict(wall=False,cpu=False))
    ck('cost','external charge matches time execution receipt and max envelope',r['schema']=='P4_D080_V_PCS_BUILD_EXTERNAL_COST_CHARGE_V1'and r['run_id']==RUN and r['source_execution']==epath and r['execution_sha256']==sha(epath)==i['execution_sha256']and r['receipt']==internal and r['receipt_sha256']==sha(internal)and r['time_file']==ext['sibling_path']and r['time_sha256']==sha(ext['sibling_path'])and r['time_fields']==fields and r['wall_s']==upperwall and r['cpu_s']==uppercpu)
    ck('cost','one actual nonzero child completion preserved and cost chain retained',r['timing_valid']is r['time_inode_unchanged']is r['wall_CPU_caps_pass']is r['started_attempt']is True and r['completed_process_exit0']is False and r['time_returncode']==r['measured_child_exit']==exitcode==2 and r['failure']is None and r['external_supervision_qualified']is i['external_supervision_qualified']is False and i['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED')
    lines=raw(ext['metadata_path']).splitlines(keepends=True);events=[json.loads(v)for v in lines];planned,started,reaped=events;proof=e['supervisor_contract'];inode=path(ext['sibling_path']).stat()
    argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/BUILDER),'--build','--protocol',str(protocol)]
    ck('supervision','real launch/reap records and exact argv source protocol',len(events)==3 and [z['event']for z in events]==['planned_launch','time_process_started','time_process_reaped']and planned['run_id']==RUN and planned['protocol']==protocol_name and planned['protocol_sha256']==sha(protocol)and planned['argv']==started['argv']==proof['actual_argv']==argv and started['pid']==reaped['pid']==r['time_process_pid']==proof['actual_time_pid']and reaped['returncode']==2 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid'])
    ck('supervision','real held exclusive inode and first launch hash',planned['time_inode']==proof['time_inode']==inode.st_ino and planned['time_device']==proof['time_device']==inode.st_dev and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and proof['planned_launch_line_sha256']==hashlib.sha256(lines[0]).hexdigest())
    ck('supervision','sources actual time python and outer logs SHA',planned['supervisor_source_sha256']==sha(SUPERVISOR)and planned['runner_sha256']==sha(BUILDER)and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3')and r['metadata']==ext['metadata_path']and r['metadata_sha256']==sha(ext['metadata_path'])and r['stderr']==ext['stderr_path']and r['stderr_sha256']==sha(ext['stderr_path']))
    ck('cost','external full-child upper includes execution persistence',upperwall>=i['wall_s_through_execution_persistence']>=e['wall_s']and uppercpu>=i['cpu_s_through_execution_persistence']>=e['cpu_s']and e['cost_status']=='PROVISIONAL_REQUIRES_EXTERNAL_SUPERVISION_POST_NO_AUTO_CHARGE_REPLACEMENT')
    ck('scope','zero science runtime RNG solve VI formal',all(e[n]==0 for n in('scientific_calls','query_calls','solve_calls','rng_calls','binary_execution_calls'))and p['VI_future_execution_authorized']is p['formal_statistics_authorized']is False and p['D080_original_formal_denominator']==22500 and p['D080_approved_formal_denominator']==18000 and not any(STAGE.rglob('runtime'))and not any(STAGE.rglob('paths')))
    for name,want in list(retained.items()):
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=want:ck('preservation','final read-byte drift '+name,False)
    failures=[z for z in checks if not z['passed']];ok=not failures
    report=dict(schema='P4_D080_V_PCS_BUILD01_FAILURE_SAVED_INDEPENDENT_POST_V1',status='PASS_FAILURE_PRESERVATION_AND_COST_ONLY'if ok else'FAIL_BUILD_FAILURE_SAVED_AUDIT',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='/root/sbl_independent_resume independent of V builder/supervisor/transform',personnel_independent=True,external_supervision_qualified=ok,external_timing_qualified=ok,external_cost_qualified=ok,engineering_build_qualified=False,original_execution_status=e['status'],original_error=e['error'],completed_process_exit0=False,measured_child_exit=exitcode,successful_command_count=9,attempted_command_count=10,completed_translation_units=8,incomplete_trace_collision_TU_preserved=True,successful_checker_reused_sha256='2e4846beda35b7b224ba7915a3708eaf550e0f24654fbbee354dd403f666b9b6',checks=checks,checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),failures=failures,source_commit=e['source_commit'],execution=epath,execution_sha256=sha(epath),protocol=protocol_name,protocol_sha256=sha(protocol),claim=claim,claim_sha256=sha(claim),receipt=charge,receipt_sha256=sha(charge),external_charge_sha256=sha(charge),internal_receipt=internal,internal_receipt_sha256=sha(internal),external_time=ext['sibling_path'],external_time_sha256=sha(ext['sibling_path']),external_time_fields=fields,charge_basis=BASIS,monotonic_envelope_qualified=ok,raw_GNUtime_upper_wall_s=float(rawwall),raw_GNUtime_upper_cpu_s=float(rawcpu),monotonic_envelope_components=envelope_components,upper_wall_s=upperwall,upper_cpu_s=uppercpu,cumulative_charged_wall_s=p['prior']['wall_s']+upperwall,cumulative_charged_cpu_s=p['prior']['cpu_s']+uppercpu,actual_translation_units=tu_count,reusable_saved_build_assets=reusable_saved_build_assets,original_STOP_object_sha256_status='UNKNOWN_NOT_RECORDED_AT_STOP',actual_dependency_count=len(dependencies),unfrozen_protected_dependencies=sorted(set(missing)),retained_sha256=retained,new_runner_model_import_transform_compile_binary_query_solve_protocol_prior_claim_VI_formal_calls=0,old_body_pair_checks_reused=219,old_engineering_checks_reused=101,limits=['Original failure is preserved; external cost/preservation audit PASS does not qualify the two-target build.','Eight completed object ELF hashes are first captured by this POST, not original before/after execution fields; plain binary hash was recorded by builder.','Engineering and ELF bytes only; no setup/local/RBS/closure/collision/path qualification.','Whole child cost includes build process persistence and reaped compiler descendants; supervisor own fsync excluded; historical unmeasured tails UNKNOWN.','Actual compiler dependency closure retained; no complete generic OS-image or performance fairness claim.','D080 original22500 versus approved18000 distinct; formal statistics unauthorized; VI archived974/974.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write('# D080 环境 V PCS BUILD01 保存证据独立后审\n\n'+report['status']+'，'+str(report['checks_passed'])+'/'+str(len(checks))+'。\n\n原40wall/80CPU工作帽STOP保留；plain五TU及link成功，trace仅前三TU成功，第四collision组被清理为-9、RRT与link未执行。核八份MD/冻结源/既有219 body-pair证书/十组回收与最终哈希/三观测Decimal最大费用包络；不修改工程失败。新增构建、模型、局部和规划均0。保守费用上界 '+str(upperwall)+' wall / '+str(uppercpu)+' CPU；仅可替换当前own费用一次。工程构建资格仍false；本PASS仅保存失败与有效费用链，不代表V算法资格通过。\n')
    print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failures),failures=failures,upper_wall_s=upperwall,upper_cpu_s=uppercpu),ensure_ascii=False))
    if failures:raise SystemExit(2)

if __name__=='__main__':main()
