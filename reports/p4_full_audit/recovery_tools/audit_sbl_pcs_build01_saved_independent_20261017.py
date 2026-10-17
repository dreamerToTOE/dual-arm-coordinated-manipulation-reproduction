#!/usr/bin/env python3
"""Personnel-independent saved SBL_PCS BUILD01 POST. Never import runners,
models, run compiler/binary, generate protocols/claims or change science data.
"""
from pathlib import Path
from decimal import Decimal
import datetime
import ast
import hashlib
import json
import math
import os
import re
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[3]
RUN='20261017_R2_ABB_SBL_PCS_BUILD01'
PROTOCOL=None # exact root-frozen path required as an argument
PROTOCOL_SHA=None # supplied exact root-frozen SHA; no protocol generation
OUT=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_BUILD01_SAVED_INDEPENDENT_POST_20261017.json'
STATIC='reports/P4_FULL_R2_ABB_SBL_PCS_BUILD01_INDEPENDENT_STATIC_REVIEW_ADDENDUM_20261017.json'
STATIC_SHA='48f25087f972d5ac095c90db3fda4accd13ebf8e8b847ea36ed94c0d92f19e82'
checks=[];retained={}
def path(n):
    n=Path(n);return n if n.is_absolute()else ROOT/n
def raw(n):
    p=path(n);b=p.read_bytes();retained[str(p)]=hashlib.sha256(b).hexdigest();return b
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def load(n):return json.loads(raw(n))
def ck(group,label,ok):checks.append(dict(group=group,check=label,passed=bool(ok)))
def group_members(pgid):
    result=[]
    for p in Path('/proc').glob('[0-9]*/stat'):
        try:
            fields=p.read_text().rsplit(')',1)[1].split()
            if int(fields[2])==pgid:result.append(int(p.parent.name))
        except(OSError,ValueError,IndexError):pass
    return sorted(result)

def main():
    import argparse
    global PROTOCOL
    ap=argparse.ArgumentParser();ap.add_argument('--protocol-sha256',required=True);ap.add_argument('--protocol',required=True);args=ap.parse_args()
    PROTOCOL=str(path(args.protocol).resolve().relative_to(ROOT))
    PROTOCOL_SHA=args.protocol_sha256
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_REPORT_PRESERVED')
    execution='results/p4_full/'+RUN+'/execution.json'
    e=load(execution);p=load(PROTOCOL);claim=e['claim'];c=load(claim)
    manifest=str(Path(p['build_root'])/'manifest.json');m=load(manifest)
    internal='results/p4_full/'+RUN+'/cost_receipt.json';i=load(internal)
    receipt=p['external_supervision']['charge_path'];r=load(receipt)
    st=load(STATIC);stage=Path(p['stage_root']);template=Path(p['template_stage'])
    ck('freeze','exact root-frozen protocol bytes',sha(PROTOCOL)==PROTOCOL_SHA==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256'])
    ck('freeze','frozen boolean reviews and exact one target budget',p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())and p['targets']==1 and p['budget']==e['budget']==dict(wall_s=45.,cpu_s=90.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.))
    ck('freeze','stable independent BUILD03 static all checks successful',sha(STATIC)==STATIC_SHA and st['status']=='PASS_SBL_PCS_BUILD01_ENGINEERING_ONLY_STATIC_REVIEW'and st['checks_total']==st['checks_passed'] and st['checks_total']>0 and st['checks_failed']==0)
    ck('recipe','real engineering successful not science',e['schema']=='P4_R2_ABB_SBL_PCS_ENGINEERING_EXECUTION_V4'and e['status']==m['status']==i['status']=='BUILT_NOT_QUERIED'and e['exit_code']==0 and e['classification']==p['classification']=='ENGINEERING_BUILD_ONLY_ORIGINAL_SBL_PCS_EXISTING_R2_NUMERICS')
    ck('recipe','manifest exactly saved execution plus linkage',{k:v for k,v in m.items()if k!='engineering_execution'}==e and m['engineering_execution']==execution)
    ck('recipe','protocol claim binding and no retry',e['protocol']==PROTOCOL and c['source_commit']==e['source_commit']and c['run_id']==e['run_id']==RUN and c['no_retry_reset_resume']is True and sha(claim)==e['claim_sha256']==e['claim_after_sha256'])
    ck('recipe','protocol recorded maps exact',all(e[k]==p[k]for k in('author_commit','budget','actual_charge_prior','prior_execution_sha256','previous_r2_wall_s','previous_r2_cpu_s','bound_files_sha256','own_source_sha256','dependency_policy','environment_fingerprint')))
    ck('recipe','all bound assets after identical',e['bound_files_sha256']==e['bound_files_after_sha256'])
    for n,want in e['bound_files_sha256'].items():ck('bound','frozen actual bytes '+n,sha(n)==want)
    for n,want in e['own_source_sha256'].items():
        ck('own','actual source '+n,sha(n)==want)
        committed=subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)
        ck('commit','actual committed source '+n,hashlib.sha256(committed).hexdigest()==want)
    committed=subprocess.check_output(['git','show',e['source_commit']+':'+PROTOCOL],cwd=ROOT)
    ck('commit','actual committed exact protocol',hashlib.sha256(committed).hexdigest()==PROTOCOL_SHA)
    for n,want in st['reviewed_source_sha256'].items():ck('static','actual reviewed source '+n,sha(n)==want==e['own_source_sha256'][n])
    ck('static','current actual prior ledger bound SHA',sha(p['actual_charge_prior']['ledger'])==p['actual_charge_prior']['ledger_sha256'])
    preview=p['source_transform_preview'];sm=load(stage/'source_transform_manifest.json')
    ck('transform','actual full manifest matches frozen exact preview',sm==e['source_transform_manifest']==preview)
    ck('transform','actual same16 wrappers no H D NR or observer science',len(sm['changes'])==16 and all(x['kind']=='OBSERVE_COMPLETE_BODY'for x in sm['changes']) and sm['whole_files_byte_reversible']is True and sm['H_or_D_or_NR_correction_present']is False and sm['observer_model_calls']==sm['observer_RNG_draws']==0)
    for before,after,base in(('compiled_source_sha256','compiled_source_after_sha256',stage),('mesh_sha256','mesh_after_sha256',stage),('preserved_source_sha256','preserved_source_after_sha256',stage/'preserved_originals')):
        ck('staged',before+' before after exact',e[before]==e[after])
        for n,want in e[before].items():ck('staged',before+' actual bytes '+n,sha(base/n)==want)
    ck('transform','all5 original source preserved map',e['preserved_source_sha256']==preview['original_sha256'])
    for n,want in preview['original_sha256'].items():ck('transform','actual original/template bytes '+n,sha(stage/'preserved_originals'/n)==sha(template/n)==want)
    for n,want in preview['staged_sha256'].items():ck('transform','actual independent staged5 SHA '+n,sha(stage/n)==want==e['compiled_source_sha256'][n])
    # Independently unwrap only saved C++ text in memory, never invoke the
    # implementation transformer. The exact original complete body must occur
    # once and whole original file bytes must recover after all16 inverses.
    def body_span(source,signature):
        if source.count(signature)!=1:raise ValueError('INDEPENDENT_ONE_SAVED_SIGNATURE_REQUIRED')
        masked=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:' '*len(m.group()),source,flags=re.S)
        begin=masked.index('{',source.index(signature));index=begin+1;depth=1
        while depth:
            depth+=(masked[index]=='{')-(masked[index]=='}');index+=1
        return begin+1,index-1
    originals={name:raw(stage/'preserved_originals'/name).decode()for name in preview['original_sha256']}
    recovered={name:raw(stage/name).decode()for name in originals}
    for item in reversed(sm['changes']):
        name=item['file'];sig=item['signature'];oa,ob=body_span(originals[name],sig);a,b=body_span(recovered[name],sig);body=originals[name][oa:ob];wrapped=recovered[name][a:b]
        ck('transform','independent saved full body once '+sig,wrapped.count(body)==1 and hashlib.sha256(body.encode()).hexdigest()==item['body_sha256'])
        recovered[name]=recovered[name][:a]+body+recovered[name][b:]
    for name,body in recovered.items():ck('transform','independent saved whole-file inverse '+name,body.encode()==originals[name].encode())
    for name in ('planners/SBL_PCS.cpp','planners/SBL_PCS.h'):ck('author','SBL actual author identity '+name,sha(template/name)==sha('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning/'+name)==preview['original_sha256'][name])
    driver=ROOT/'baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_draft.cpp'
    sources=[driver,*[stage/n for n in p['linked_author_cpp']]]
    stdout_name='results/p4_full/'+RUN+'/compile.stdout'
    stdout=raw(stdout_name)
    ck('dependencies','actual original raw stdout path SHA bytes',e['compiler_dependency_stdout']==stdout_name and e['compiler_dependency_stdout_sha256']==sha(stdout_name)and e['compiler_dependency_stdout_bytes']==len(stdout)and len(stdout)>0)
    # Independent regex lexer on byte-preserving reconstructed logical lines.
    # No implementation parser import or invocation; no shell/eval/shlex.
    lexer=re.compile(rb'(?:\\[ \t#:\\]|\$\$|[^ \t\r\n\\#$:\x00-\x1f\x7f])+|:')
    def tokens(logical):
        found=list(lexer.finditer(logical));pos=0;values=[]
        for match in found:
            if logical[pos:match.start()].strip(b' \t'):raise ValueError('INDEPENDENT_UNPARSED_MAKE_BYTES')
            value=match.group();pos=match.end()
            if value!=b':':value=re.sub(rb'\\([ \t#:\\])|\$\$',lambda m:m.group(1)if m.group(1)is not None else b'$',value)
            values.append(value)
        if logical[pos:].strip(b' \t')or values.count(b':')!=1:raise ValueError('INDEPENDENT_EXACT_COLON_REQUIRED')
        at=values.index(b':')
        if at!=1 or len(values)<3:raise ValueError('INDEPENDENT_SINGLE_TARGET_NONEMPTY_DEPS_REQUIRED')
        return os.fsdecode(values[0]),[os.fsdecode(v)for v in values[2:]]
    rules=[];offset=0;start=0;pieces=[]
    for physical in stdout.splitlines(keepends=True):
        if not physical.endswith(b'\n')or b'\r'in physical:raise ValueError('INDEPENDENT_LF_COMPLETE_PHYSICAL_LINE_REQUIRED')
        body=physical[:-1];slashes=len(body)-len(body.rstrip(bytes([92])));offset+=len(physical)
        if slashes%2:pieces.append(body[:-1]+b' ');continue
        pieces.append(body);target,names=tokens(b''.join(pieces));rules.append((start,offset,target,names));start=offset;pieces=[]
    ck('dependencies','all stdout bytes5 exact complete logical compiler rules',len(rules)==5 and not pieces and start==len(stdout)and stdout.endswith(b'\n'))
    expected={str(q.resolve())for q in sources};source_occurrences={q:0 for q in expected};dependencies={};translation_units={};missing=[]
    frozen={str(path(n).resolve()):want for n,want in p['bound_files_sha256'].items()}
    frozen.update({str((stage/n).resolve()):want for n,want in e['compiled_source_sha256'].items()})
    pqp_lib=next(z for z in e['command']if z.endswith('/lib/libPQP.a'))
    protected=[ROOT,stage,template,Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning'),Path(pqp_lib).parents[1],Path('/opt/ros/humble/include/ompl-1.7/ompl'),Path('/usr/include/kdl'),Path('/usr/include/boost'),Path('/usr/include/eigen3'),Path('/usr/include/nlohmann')]
    bindings=[];files={}
    for index,(begin,end,target,names)in enumerate(rules):
        resolved=[path(n).resolve()for n in names];source=str(resolved[0]);fragment=stdout[begin:end]
        ck('dependencies','actual binary target exact rule '+str(index),path(target).resolve()==Path(p['binary']).resolve())
        ck('dependencies','actual first prereq distinct frozen TU rule '+str(index),source in expected and source not in translation_units)
        translation_units[source]=[str(q)for q in resolved]
        for q in resolved:
            key=str(q);want=sha(q);dependencies[key]=want
            if key in source_occurrences:source_occurrences[key]+=1
            if any(q.is_relative_to(base)for base in protected)and frozen.get(key)!=want:missing.append(key)
        slice_name='dependency_stdout_slices/'+str(index)+'_'+Path(source).name+'.d';slice_path=stage/slice_name;digest=hashlib.sha256(fragment).hexdigest();files[slice_name]=digest
        ck('dependencies','actual derived slice exact original byte offsets rule '+str(index),raw(slice_path)==fragment and sha(slice_path)==digest)
        bindings.append(dict(index=index,source=source,actual_target=target,raw_stdout_offset_begin=begin,raw_stdout_offset_end=end,raw_bytes=len(fragment),raw_sha256=digest,derived_slice=slice_name,derived_slice_sha256=digest,compiler_created_individual_d_file=False,dependencies_count=len(resolved)))
    ck('dependencies','all5 frozen TUs exactly once actual raw source occurrences',set(translation_units)==expected and source_occurrences=={q:1 for q in expected}and source_occurrences==e['actual_source_dependency_occurrences'])
    ck('dependencies','all derived slice manifest before after exact',files==e['compiler_dependency_files_sha256']==e['compiler_dependency_files_after_sha256']and set((stage/'dependency_stdout_slices').glob('*'))=={stage/q for q in files})
    ck('dependencies','independent actual raw rule binding exact',bindings==e['compiler_dependency_rule_bindings'])
    ck('dependencies','independent actual5 dependency lists exact',translation_units==e['actual_dependency_translation_units'])
    ck('dependencies','independent actual dependency SHA exact',dependencies==e['actual_dependencies_sha256'])
    ck('dependencies','zero unfrozen protected dependencies no retroactive binding',not missing and e['unfrozen_protected_dependencies']==[])
    for n,want in e['added_header_assets_after_sha256'].items():ck('headers','actual added namespace header '+n,sha(n)==want==p['bound_files_sha256'][n])
    ck('headers','OMPL KDL complete actual namespace sets retained',all({str(q)for q in base.rglob('*')if q.is_file()}=={n for n in e['added_header_assets_after_sha256']if Path(n).is_relative_to(base)}for base in(Path('/opt/ros/humble/include/ompl-1.7/ompl'),Path('/usr/include/kdl'),Path('/usr/include/eigen3'),Path('/usr/include/nlohmann'))))
    ck('headers','compiler OS actual fingerprint',e['environment_fingerprint']==dict(uname=list(os.uname()),os_release_sha256=sha('/etc/os-release')))
    for n,want in e['compile_log_sha256'].items():ck('logs','actual compile log '+n,sha(n)==want)
    binary=raw(e['binary'])
    ck('logs','actual link map digest retained',sha(path(e['link_map']))==e['link_map_sha256'])
    ck('binary','actual output ELF hash only not executed',hashlib.sha256(binary).hexdigest()==e['binary_sha256']and e['binary']==p['binary']and binary[:6]==b'\x7fELF\x02\x01'and struct.unpack_from('<H',binary,18)[0]==62)
    command=e['command'];cpp=[z for z in command if z.endswith('.cpp')]
    ck('command','one actual compiler command5 TUs output exactly',command[0]=='/usr/bin/x86_64-linux-gnu-g++-11'and command[1:4]==['-MD','-MF','-']and cpp==[str(q)for q in sources]and command[-2:]==['-o',e['binary']]and command.count(e['binary'])==1)
    ck('lifecycle','compiler successful reaped diagnostics empty',e['compiler_reaped']is True and e['exit_code']==0 and e['diagnostics']==[]and e['compiler_group_members_before_cleanup']==[]and e['compiler_group_members_after_cleanup']==[])
    ck('lifecycle','actual compiler group absent now',not group_members(e['compiler_pid']))
    ext=p['external_supervision'];timefile=ext['sibling_path'];fields=raw(timefile).decode().strip().split()
    ck('external','exact4 actual GNUtime fields',len(fields)==4)
    elapsed,user,system=(Decimal(v)for v in fields[:3]);exitcode=int(fields[3])
    upperwall=float(elapsed+Decimal('.01'));uppercpu=float(user+system+Decimal('.02'))
    ck('external','finite nonnegative upper timings and caps',all(v.is_finite()and v>=0 for v in(elapsed,user,system))and upperwall<=45 and uppercpu<=90 and upperwall+e['previous_r2_wall_s']<=3600 and uppercpu+e['previous_r2_cpu_s']<=7200)
    ck('external','actual charge fields match direct GNUtime upper',r['time_fields']==fields and r['wall_s']==upperwall and r['cpu_s']==uppercpu and r['timing_valid']is r['time_inode_unchanged']is r['wall_CPU_caps_pass']is r['completed_process_exit0']is True and r['time_returncode']==r['measured_child_exit']==exitcode==0 and r['started_attempt']is True and r['failure']is None)
    ck('external','actual charge binds execution internal receipt and time',r['source_execution']==execution and r['execution_sha256']==sha(execution)==i['execution_sha256']and r['receipt']==internal and r['receipt_sha256']==sha(internal)and r['time_file']==timefile and r['time_sha256']==sha(timefile))
    ck('external','internal excludes nonzero persistence tail external required',i['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and i['external_supervision_qualified']is False and r['external_supervision_qualified']is False and e['external_supervision_qualified']is False and i['wall_s_through_execution_persistence']<45 and i['cpu_s_through_execution_persistence']<90)
    metadata=raw(ext['metadata_path']);lines=metadata.splitlines(keepends=True);events=[json.loads(v)for v in lines]
    ck('external','exact launch started reaped records',len(events)==3 and [v['event']for v in events]==['planned_launch','time_process_started','time_process_reaped'])
    planned,started,reaped=events;proof=e['supervisor_launch_proof'];inode=path(timefile).stat()
    expectedargv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/'scripts/build_p4_full_r2_abb_sbl_pcs_draft.py'),'--protocol',str(path(PROTOCOL))]
    ck('external','actual metadata matches frozen recipe and PID identity',planned['run_id']==RUN and planned['protocol']==PROTOCOL and planned['protocol_sha256']==PROTOCOL_SHA and planned['argv']==started['argv']==proof['actual_argv']==expectedargv and started['pid']==reaped['pid']==r['time_process_pid']==proof['actual_time_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid'])
    ck('external','actual held FD inode and first planned line hash proof',planned['time_inode']==proof['time_inode']==inode.st_ino and planned['time_device']==proof['time_device']==inode.st_dev and planned['time_fd']in proof['actual_time_output_fds']and proof['planned_launch_line_sha256']==hashlib.sha256(lines[0]).hexdigest()and proof['actual_time_start_ticks']>0)
    ck('external','actual supervisor runner tool source SHA binding',planned['supervisor_source_sha256']==sha('scripts/supervise_p4_full_r2_abb_sbl_pcs_build_draft.py')and planned['runner_sha256']==sha('scripts/build_p4_full_r2_abb_sbl_pcs_draft.py')and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
    ck('external','all actual outer log hashes bound',r['metadata']==ext['metadata_path']and r['metadata_sha256']==sha(ext['metadata_path'])and r['stderr']==ext['stderr_path']and r['stderr_sha256']==sha(ext['stderr_path']))
    ck('cost','whole-child upper includes internal saved execution receipt cost',upperwall>=e['wall_s']and upperwall>=i['wall_s_through_execution_persistence']and uppercpu>=e['cpu_s']and uppercpu>=i['cpu_s_through_execution_persistence'])
    prior=load(p['actual_charge_prior']['ledger']);actual={str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if q.parent.name!=RUN}
    ck('prior','actual old prior identities all-date unchanged',len(actual)==len(prior['executions']) and actual==e['prior_execution_sha256']=={row['execution']:row['execution_sha256']for row in prior['executions']})
    ck('prior','actual prior effective charged totals unchanged',math.fsum(row.get('charged_wall_s',row['wall_s'])for row in prior['executions'])==e['previous_r2_wall_s']==p['actual_charge_prior']['wall_s'] and math.fsum(row.get('charged_cpu_s',row['cpu_s'])for row in prior['executions'])==e['previous_r2_cpu_s']==p['actual_charge_prior']['cpu_s'])
    ck('scope','zero scientific binary query solve VI formal',all(e[k]==p[k]==0 for k in('query_calls','solve_calls','binary_execution_calls','formal_table_I_calls','new_VI_candidate_constructions'))and p['scientific_execution_authorized']is False and not(stage/'paths').exists()and not(stage/'runtime').exists())
    ck('scope','VI974 exhausted formal0/22500 retained',prior['vi_B_candidate_cap']==974 and prior['vi_B_remaining']['candidate_constructions']==0 and prior['formal_table_I_calls']==0 and prior['formal_table_I_required_calls']==22500)
    for n,want in list(retained.items()):ck('unchanged','all read actual bytes remain '+n,hashlib.sha256(Path(n).read_bytes()).hexdigest()==want)
    failures=[q for q in checks if not q['passed']]
    report=dict(schema='P4_SBL_PCS_BUILD01_SAVED_INDEPENDENT_POST_V1',status='PASS_SBL_PCS_BUILD01_SAVED_INDEPENDENT_POST'if not failures else'FAIL_SBL_PCS_BUILD01_SAVED_INDEPENDENT_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of SBL_PCS builder driver transformer and supervisor',personnel_independent=True,external_supervision_qualified=not failures,external_timing_qualified=not failures,external_cost_qualified=not failures,engineering_build_qualified=not failures,checks=checks,checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),failures=failures,source_commit=e['source_commit'],execution=execution,execution_sha256=sha(execution),manifest=manifest,manifest_sha256=sha(manifest),receipt=receipt,receipt_sha256=sha(receipt),internal_receipt=internal,internal_receipt_sha256=sha(internal),protocol=PROTOCOL,protocol_sha256=sha(PROTOCOL),claim=claim,claim_sha256=sha(claim),external_time=timefile,external_time_sha256=sha(timefile),external_time_fields=fields,upper_wall_s=upperwall,upper_cpu_s=uppercpu,own_wall_s=e['wall_s'],own_cpu_s=e['cpu_s'],cumulative_charged_wall_s=e['previous_r2_wall_s']+upperwall,cumulative_charged_cpu_s=e['previous_r2_cpu_s']+uppercpu,compiler_pid=e['compiler_pid'],actual_translation_units=len(translation_units),actual_dependency_count=len(dependencies),actual_dependency_rule_bindings=bindings,compiler_stdout_sha256=sha(stdout_name),unfrozen_protected_dependencies=sorted(set(missing)),retained_sha256=retained,new_runner_model_import_compile_binary_query_solve_protocol_prior_claim_calls=0,limitations=['Saved successful engineering and ELF bytes only; binary was not executed or queried. No setup/solve/path/RBS/physical qualification inferred. Original historical connect a_chain source risk remains; setup-only driver refuses solve.','Preflight has no installed hard timer. Whole-child GNUtime includes builder import/preflight/claim/compiler/cleanup/receipts/exit and reaped descendants. Supervisor own journal/fsync costs excluded. Current upper replaces current own cost exactly once; previous effective charges remain unchanged.','Generic system actual headers are SHA/fingerprint recorded; no whole OS closure claim. After-group emptiness alone cannot prove historical orphan CPU; historical UNKNOWN retained.','Public13 projection remains unexecuted; matrix-storage and runtime/RNG certification are not inferred from this engineering build.','211 full paper obligations, VI974/974余0 and formal0/22500 persist. No P2/Isaac.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write('# SBL_PCS BUILD01 保存证据独立后审\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(len(checks))+'，失败'+str(len(failures))+'。\n\n人员独立saved-only：原五文件/16body、全部冻结字节、五TU真实stdout逻辑规则及派生切片、编译输出/ELF、commit/protocol/claim、真实外层GNUtime/heldFD/reap、实际compiler组空与账目逐项核验。新增compile/binary/query/solve/VI/protocol/prior/claim均0。\n\n本次完整子生命周期上界'+str(upperwall)+'wall/'+str(uppercpu)+'CPU，仅替换本次own一次；累积charged '+str(report['cumulative_charged_wall_s'])+'wall/'+str(report['cumulative_charged_cpu_s'])+'CPU。科学入口尚未执行，211义务、VI974余0、formal0/22500不变。\n')
    print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failures),failures=failures,upper_wall_s=upperwall,upper_cpu_s=uppercpu),ensure_ascii=False))
    if failures:raise SystemExit(2)

if __name__=='__main__':main()
