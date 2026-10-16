#!/usr/bin/env python3
"""Personnel-independent saved CBiRRT_NR BUILD01 POST. Never import runners,
models, run compiler/binary, generate protocols/claims or change science data.
"""
from pathlib import Path
from decimal import Decimal
import datetime
import hashlib
import json
import math
import os
import shlex
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[3]
RUN='20261016_R2_ABB_CBIRRT_NR_BUILD01'
PROTOCOL='configs/p4_full/r2_abb_cbirrt_nr_engineering_v1.json'
PROTOCOL_SHA='1909272b19708ddcbaeb5b26a835c4fcc280fc4a2e7fa41232d4e8ad65a8e703'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST_20261016.json'
STATIC='reports/P4_FULL_R2_ABB_CBIRRT_NR_ENGINEERING_INDEPENDENT_STATIC_REVIEW_V4_20261016.json'
STATIC_SHA='04449391db8bc675959fba588ef68b34f4fd213318834ea4d009983e16a2d46f'
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
    if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_REPORT_PRESERVED')
    execution='results/p4_full/'+RUN+'/execution.json'
    e=load(execution);p=load(PROTOCOL);claim=e['claim'];c=load(claim)
    manifest=str(Path(p['build_root'])/'manifest.json');m=load(manifest)
    internal='results/p4_full/'+RUN+'/cost_receipt.json';i=load(internal)
    receipt=p['external_supervision']['charge_path'];r=load(receipt)
    st=load(STATIC);stage=Path(p['stage_root']);template=Path(p['template_stage'])
    ck('freeze','exact root-frozen protocol bytes',sha(PROTOCOL)==PROTOCOL_SHA==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256'])
    ck('freeze','frozen boolean reviews and exact one target budget',p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())and p['targets']==1 and p['budget']==e['budget']==dict(wall_s=45.,cpu_s=90.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.))
    ck('freeze','stable independent V4 all checks successful',sha(STATIC)==STATIC_SHA and st['status']=='PASS_VERSIONED_CBIRRT_NR_ENGINEERING_STATIC_REVIEW'and st['checks_total']==st['checks_passed']==176 and st['checks_failed']==0)
    ck('recipe','real engineering successful not science',e['schema']=='P4_R2_ABB_CBIRRT_NR_ENGINEERING_EXECUTION_V2'and e['status']==m['status']==i['status']=='BUILT_NOT_QUERIED'and e['exit_code']==0 and e['classification']==p['classification']=='ENGINEERING_BUILD_ONLY_ORIGINAL_CBIRRT_NR_WITH_EXISTING_PHYSICAL_GD_SEAM')
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
    preview=p['source_transform_preview'];sm=load(stage/'source_transform_manifest.json')
    ck('transform','actual full manifest equals independently reviewed original5 preview',sm==e['source_transform_manifest']==preview and preview['staged_sha256']==st['independently_reconstructed_staged_sha256'])
    ck('transform','actual same13 wrappers no added PCS H/D/role/branch or observer science',sum(x['kind']=='OBSERVE_COMPLETE_BODY'for x in sm['changes'])==13 and sm['full12_distance_original']is True and sm['whole_files_byte_reversible']is True and sm['H_or_D_correction_present']is sm['active_role_or_analytic_branch']is False and sm['observer_model_calls']==sm['observer_RNG_draws']==0)
    for before,after,base in(('compiled_source_sha256','compiled_source_after_sha256',stage),('mesh_sha256','mesh_after_sha256',stage),('preserved_source_sha256','preserved_source_after_sha256',stage/'preserved_originals')):
        ck('staged',before+' before after exact',e[before]==e[after])
        for n,want in e[before].items():ck('staged',before+' actual bytes '+n,sha(base/n)==want)
    ck('transform','all5 original source preserved map',e['preserved_source_sha256']==preview['original_sha256'])
    for n,want in preview['original_sha256'].items():ck('transform','actual original/template/author bytes '+n,sha(stage/'preserved_originals'/n)==sha(template/n)==sha('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning/'+n)==want)
    for n,want in preview['staged_sha256'].items():ck('transform','actual independent staged5 SHA '+n,sha(stage/n)==want==e['compiled_source_sha256'][n])
    driver=ROOT/'baselines/p4_full/geometry_consistent/abb_cbirrt_nr_driver_draft.cpp';kernel=ROOT/'baselines/p4_full/geometry_consistent/abb_nr_interface_kernel_draft.cpp'
    sources=[driver,kernel,*[stage/n for n in p['linked_author_cpp']]]
    depfiles=[stage/('p4_abb_cbirrt_nr-'+s.stem+'.d')for s in sources]
    ck('dependencies','exact6 distinct actual MD files',len(depfiles)==len(set(depfiles))==6 and set(stage.glob('*.d'))==set(depfiles)and set(e['compiler_dependency_files_sha256'])=={str(q.relative_to(stage))for q in depfiles})
    frozen={str(path(n).resolve()):want for n,want in p['bound_files_sha256'].items()}
    frozen.update({str((stage/n).resolve()):want for n,want in e['compiled_source_sha256'].items()})
    protected=[ROOT,stage,template,Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning'),Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/PQP_v1.3'),Path('/opt/ros/humble/include/ompl-1.7/ompl'),Path('/usr/include/kdl'),Path('/usr/include/boost'),Path('/usr/include/eigen3'),Path('/usr/include/nlohmann')]
    # Exact PQP include root comes from actual frozen compiler argv and library.
    pqp_lib=next(z for z in e['command']if z.endswith('/lib/libPQP.a'));protected.append(Path(pqp_lib).parents[1])
    dependencies={};translation_units={};missing=[]
    for source,dep in zip(sources,depfiles):
        text=raw(dep).decode().replace(chr(92)+chr(10),' ')
        ck('dependencies','single make target '+dep.name,text.count(':')==1)
        resolved=[path(n).resolve()for n in shlex.split(text.split(':',1)[1])]
        ck('dependencies','each TU own source '+source.name,source.resolve()in resolved and len(resolved)>1)
        translation_units[str(source)]=[str(q)for q in resolved]
        ck('dependencies','MD SHA actual '+dep.name,sha(dep)==e['compiler_dependency_files_sha256'][dep.name])
        for q in resolved:
            want=sha(q);dependencies[str(q)]=want
            if any(q.is_relative_to(base)for base in protected)and frozen.get(str(q))!=want:missing.append(str(q))
    ck('dependencies','independent actual6 dependency lists exact',translation_units==e['actual_dependency_translation_units'])
    ck('dependencies','independent actual dependency SHA exact',dependencies==e['actual_dependencies_sha256'])
    ck('dependencies','zero unfrozen protected dependencies no retroactive binding',not missing and e['unfrozen_protected_dependencies']==[])
    for n,want in e['added_header_assets_after_sha256'].items():ck('headers','actual added namespace header '+n,sha(n)==want==p['bound_files_sha256'][n])
    ck('headers','OMPL KDL complete actual namespace sets retained',all({str(q)for q in base.rglob('*')if q.is_file()}=={n for n in e['added_header_assets_after_sha256']if Path(n).is_relative_to(base)}for base in(Path('/opt/ros/humble/include/ompl-1.7/ompl'),Path('/usr/include/kdl'))))
    ck('headers','compiler OS actual fingerprint',e['environment_fingerprint']==dict(uname=list(os.uname()),os_release_sha256=sha('/etc/os-release')))
    for n,want in e['compile_log_sha256'].items():ck('logs','actual compile log '+n,sha(n)==want)
    binary=raw(e['binary'])
    ck('binary','actual output ELF hash only not executed',hashlib.sha256(binary).hexdigest()==e['binary_sha256']and e['binary']==p['binary']and binary[:6]==b'\x7fELF\x02\x01'and struct.unpack_from('<H',binary,18)[0]==62)
    command=e['command'];cpp=[z for z in command if z.endswith('.cpp')]
    ck('command','one actual compiler command6 TUs output exactly',command[0]=='/usr/bin/x86_64-linux-gnu-g++-11'and command[1]=='-MD'and cpp==[str(q)for q in sources]and command[-2:]==['-o',e['binary']]and command.count(e['binary'])==1)
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
    expectedargv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/'scripts/build_p4_full_r2_abb_cbirrt_nr_draft.py'),'--protocol',str(path(PROTOCOL))]
    ck('external','actual metadata matches frozen recipe and PID identity',planned['run_id']==RUN and planned['protocol']==PROTOCOL and planned['protocol_sha256']==PROTOCOL_SHA and planned['argv']==started['argv']==proof['actual_argv']==expectedargv and started['pid']==reaped['pid']==r['time_process_pid']==proof['actual_time_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid'])
    ck('external','actual held FD inode and first planned line hash proof',planned['time_inode']==proof['time_inode']==inode.st_ino and planned['time_device']==proof['time_device']==inode.st_dev and planned['time_fd']in proof['actual_time_output_fds']and proof['planned_launch_line_sha256']==hashlib.sha256(lines[0]).hexdigest()and proof['actual_time_start_ticks']>0)
    ck('external','actual supervisor runner tool source SHA binding',planned['supervisor_source_sha256']==sha('scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_draft.py')and planned['runner_sha256']==sha('scripts/build_p4_full_r2_abb_cbirrt_nr_draft.py')and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
    ck('external','all actual outer log hashes bound',r['metadata']==ext['metadata_path']and r['metadata_sha256']==sha(ext['metadata_path'])and r['stderr']==ext['stderr_path']and r['stderr_sha256']==sha(ext['stderr_path']))
    ck('cost','whole-child upper includes internal saved execution receipt cost',upperwall>=e['wall_s']and upperwall>=i['wall_s_through_execution_persistence']and uppercpu>=e['cpu_s']and uppercpu>=i['cpu_s_through_execution_persistence'])
    prior=load(p['actual_charge_prior']['ledger']);actual={str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if q.parent.name!=RUN}
    ck('prior','actual old36 identities all-date unchanged',len(actual)==36 and actual==e['prior_execution_sha256']=={row['execution']:row['execution_sha256']for row in prior['executions']})
    ck('prior','actual prior effective charged totals unchanged',math.fsum(row.get('charged_wall_s',row['wall_s'])for row in prior['executions'])==e['previous_r2_wall_s']==685.555705375994 and math.fsum(row.get('charged_cpu_s',row['cpu_s'])for row in prior['executions'])==e['previous_r2_cpu_s']==542.4289229999999)
    ck('scope','zero scientific binary query solve VI formal',all(e[k]==p[k]==0 for k in('query_calls','solve_calls','binary_execution_calls','formal_table_I_calls','new_VI_candidate_constructions'))and p['scientific_execution_authorized']is False and not(stage/'paths').exists()and not(stage/'runtime').exists())
    ck('scope','VI974 exhausted formal0/22500 retained',prior['vi_B_candidate_cap']==974 and prior['vi_B_remaining']['candidate_constructions']==0 and prior['formal_table_I_calls']==0 and prior['formal_table_I_required_calls']==22500)
    for n,want in list(retained.items()):ck('unchanged','all read actual bytes remain '+n,hashlib.sha256(Path(n).read_bytes()).hexdigest()==want)
    failures=[q for q in checks if not q['passed']]
    report=dict(schema='P4_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST_V1',status='PASS_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST'if not failures else'FAIL_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of CBiRRT_NR builder driver transformer and supervisor',personnel_independent=True,external_supervision_qualified=not failures,checks=checks,checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),failures=failures,source_commit=e['source_commit'],execution=execution,execution_sha256=sha(execution),manifest=manifest,manifest_sha256=sha(manifest),receipt=receipt,receipt_sha256=sha(receipt),internal_receipt=internal,internal_receipt_sha256=sha(internal),protocol=PROTOCOL,protocol_sha256=sha(PROTOCOL),claim=claim,claim_sha256=sha(claim),external_time=timefile,external_time_sha256=sha(timefile),upper_wall_s=upperwall,upper_cpu_s=uppercpu,own_wall_s=e['wall_s'],own_cpu_s=e['cpu_s'],cumulative_charged_wall_s=e['previous_r2_wall_s']+upperwall,cumulative_charged_cpu_s=e['previous_r2_cpu_s']+uppercpu,compiler_pid=e['compiler_pid'],actual_translation_units=len(translation_units),actual_dependency_count=len(dependencies),unfrozen_protected_dependencies=sorted(set(missing)),retained_sha256=retained,new_runner_model_import_compile_binary_query_solve_protocol_prior_claim_calls=0,limitations=['Saved successful engineering and ELF bytes only; binary was not executed or queried. No solve/path/RBS/NR physical qualification inferred.','Whole-child GNUtime includes builder import/preflight/claim/compiler/cleanup/receipts/exit and reaped descendants. Supervisor own journal/fsync costs excluded. Current upper replaces current own cost exactly once; previous effective charges remain unchanged.','Generic system actual headers are SHA/fingerprint recorded; no whole OS closure claim. After-group emptiness alone cannot prove historical orphan CPU; historical UNKNOWN retained.','211 full paper obligations, VI974/974余0 and formal0/22500 persist. No P2/Isaac.'])
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write('# CBiRRT_NR BUILD01 保存证据独立后审\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(len(checks))+'，失败'+str(len(failures))+'。\n\n人员独立saved-only：原五源/13body、全部冻结字节、六TU实际.d、编译输出/ELF、commit/protocol/claim、真实外层GNUtime/heldFD/reap、实际compiler组空与账目逐项核验。新增compile/binary/query/solve/VI/protocol/prior/claim均0。\n\n本次完整子生命周期上界'+str(upperwall)+'wall/'+str(uppercpu)+'CPU，仅替换本次own一次；累积charged '+str(report['cumulative_charged_wall_s'])+'wall/'+str(report['cumulative_charged_cpu_s'])+'CPU。科学入口尚未执行，211义务、VI974余0、formal0/22500不变。\n')
    print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failures),failures=failures,upper_wall_s=upperwall,upper_cpu_s=uppercpu),ensure_ascii=False))
    if failures:raise SystemExit(2)

if __name__=='__main__':main()
