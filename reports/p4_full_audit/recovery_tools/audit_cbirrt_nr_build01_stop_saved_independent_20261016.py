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
    evidence=ROOT/'reports/p4_full_audit/saved_engineering_evidence'/RUN
    if evidence.exists():raise SystemExit('EXISTING_SAVED_PARTIAL_DEPENDENCY_PRESERVED')
    failure_out=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_NR_BUILD01_FAILURE_ROOT_CAUSE_20261016.json'
    if failure_out.exists()or failure_out.with_suffix('.md').exists():raise SystemExit('EXISTING_FAILURE_REPORT_PRESERVED')
    execution='results/p4_full/'+RUN+'/execution.json'
    e=load(execution);p=load(PROTOCOL);claim=e['claim'];c=load(claim)
    manifest=str(Path(p['build_root'])/'manifest.json');manifest_exists=path(manifest).exists()
    internal='results/p4_full/'+RUN+'/cost_receipt.json';i=load(internal)
    receipt=p['external_supervision']['charge_path'];r=load(receipt)
    st=load(STATIC);stage=Path(p['stage_root']);template=Path(p['template_stage'])
    ck('freeze','exact root-frozen protocol bytes',sha(PROTOCOL)==PROTOCOL_SHA==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256'])
    ck('freeze','frozen boolean reviews and exact one target budget',p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())and p['targets']==1 and p['budget']==e['budget']==dict(wall_s=45.,cpu_s=90.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.))
    ck('freeze','stable independent V4 all checks successful',sha(STATIC)==STATIC_SHA and st['status']=='PASS_VERSIONED_CBIRRT_NR_ENGINEERING_STATIC_REVIEW'and st['checks_total']==st['checks_passed']==176 and st['checks_failed']==0)
    ck('recipe','actual STOP after compiler0 not qualified build',e['schema']=='P4_R2_ABB_CBIRRT_NR_ENGINEERING_EXECUTION_V2'and e['status']==i['status']=='STOP_PREFIX_RETAINED'and e['exit_code']==0 and e['classification']==p['classification']=='ENGINEERING_BUILD_ONLY_ORIGINAL_CBIRRT_NR_WITH_EXISTING_PHYSICAL_GD_SEAM'and e['termination_reason']=="RuntimeError('ONE_COMPLETE_MD_FILE_PER_TRANSLATION_UNIT_REQUIRED')")
    ck('recipe','no successful manifest or published binary or actual6 dependency record',not manifest_exists and all(n not in e for n in('binary','binary_sha256','actual_dependency_translation_units','actual_dependencies_sha256','unfrozen_protected_dependencies')))
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
    expected_depfiles=[stage/('p4_abb_cbirrt_nr-'+q.stem+'.d')for q in sources]
    depfiles=sorted(stage.glob('*.d'));depfile=stage/'p4_abb_cbirrt_nr.d'
    ck('dependencies','actual only one common output-derived MD file',depfiles==[depfile]and set(e['compiler_dependency_files_sha256'])=={depfile.name})
    ck('dependencies','actual MD exact frozen STOP hash',sha(depfile)==e['compiler_dependency_files_sha256'][depfile.name]=='05621e65d40d89bccbacac84cdefd03aa9adc69fcede097545ced2dcd33e5538')
    ck('dependencies','all6 required source-specific files absent',len(expected_depfiles)==len(set(expected_depfiles))==6 and not any(q.exists()for q in expected_depfiles))
    deptext=raw(depfile).decode().replace(chr(92)+chr(10),' ')
    ck('dependencies','observed one make target actual output',deptext.count(':')==1 and deptext.split(':',1)[0]==p['binary'])
    resolved=[path(n).resolve()for n in shlex.split(deptext.split(':',1)[1])]
    translation_units=[str(q)for q in sources if q.resolve()in resolved]
    dependencies={str(q):sha(q)for q in resolved};missing=[str(q)for q in expected_depfiles if not q.exists()]
    ck('dependencies','only last CBiRRT_NR TU present first5 absent',translation_units==[str(sources[-1])]and all(q.resolve()not in resolved for q in sources[:-1]))
    ck('dependencies','no compiler probe retry or posthoc manifest repair',not manifest_exists and 'actual_dependencies_sha256'not in e and len(depfiles)==1)
    for n,want in e['added_header_assets_after_sha256'].items():ck('headers','actual added namespace header '+n,sha(n)==want==p['bound_files_sha256'][n])
    ck('headers','OMPL KDL complete actual namespace sets retained',all({str(q)for q in base.rglob('*')if q.is_file()}=={n for n in e['added_header_assets_after_sha256']if Path(n).is_relative_to(base)}for base in(Path('/opt/ros/humble/include/ompl-1.7/ompl'),Path('/usr/include/kdl'))))
    ck('headers','compiler OS actual fingerprint',e['environment_fingerprint']==dict(uname=list(os.uname()),os_release_sha256=sha('/etc/os-release')))
    for n,want in e['compile_log_sha256'].items():ck('logs','actual compile log '+n,sha(n)==want)
    binary=raw(p['binary']);binary_observed_sha256=hashlib.sha256(binary).hexdigest()
    ck('binary','unpublished ELF exists bytes only no qualification',len(binary)>64 and binary[:6]==b'\x7fELF\x02\x01'and struct.unpack_from('<H',binary,18)[0]==62 and 'binary_sha256'not in e)
    command=e['command'];cpp=[z for z in command if z.endswith('.cpp')]
    ck('command','one actual compiler command6 TUs output exactly',command[0]=='/usr/bin/x86_64-linux-gnu-g++-11'and command[1]=='-MD'and cpp==[str(q)for q in sources]and command[-2:]==['-o',p['binary']]and command.count(p['binary'])==1)
    ck('lifecycle','compiler successful reaped diagnostics empty',e['compiler_reaped']is True and e['exit_code']==0 and e['diagnostics']==[]and e['compiler_group_members_before_cleanup']==[]and e['compiler_group_members_after_cleanup']==[])
    ck('lifecycle','actual compiler group absent now',not group_members(e['compiler_pid']))
    ext=p['external_supervision'];timefile=ext['sibling_path'];fields=raw(timefile).decode().strip().split()
    ck('external','exact4 actual GNUtime fields',len(fields)==4)
    elapsed,user,system=(Decimal(v)for v in fields[:3]);exitcode=int(fields[3])
    upperwall=float(elapsed+Decimal('.01'));uppercpu=float(user+system+Decimal('.02'))
    ck('external','finite nonnegative upper timings and caps',all(v.is_finite()and v>=0 for v in(elapsed,user,system))and upperwall<=45 and uppercpu<=90 and upperwall+e['previous_r2_wall_s']<=3600 and uppercpu+e['previous_r2_cpu_s']<=7200)
    ck('external','actual charge fields match direct GNUtime upper',r['time_fields']==fields and r['wall_s']==upperwall and r['cpu_s']==uppercpu and r['timing_valid']is r['time_inode_unchanged']is r['wall_CPU_caps_pass']is True and r['completed_process_exit0']is False and r['time_returncode']==r['measured_child_exit']==exitcode==1 and r['started_attempt']is True and r['failure']is None)
    ck('external','actual charge binds execution internal receipt and time',r['source_execution']==execution and r['execution_sha256']==sha(execution)==i['execution_sha256']and r['receipt']==internal and r['receipt_sha256']==sha(internal)and r['time_file']==timefile and r['time_sha256']==sha(timefile))
    ck('external','internal excludes nonzero persistence tail external required',i['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and i['external_supervision_qualified']is False and r['external_supervision_qualified']is False and e['external_supervision_qualified']is False and i['wall_s_through_execution_persistence']<45 and i['cpu_s_through_execution_persistence']<90)
    metadata=raw(ext['metadata_path']);lines=metadata.splitlines(keepends=True);events=[json.loads(v)for v in lines]
    ck('external','exact launch started reaped records',len(events)==3 and [v['event']for v in events]==['planned_launch','time_process_started','time_process_reaped'])
    planned,started,reaped=events;proof=e['supervisor_launch_proof'];inode=path(timefile).stat()
    expectedargv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(ROOT/'scripts/build_p4_full_r2_abb_cbirrt_nr_draft.py'),'--protocol',str(path(PROTOCOL))]
    ck('external','actual metadata matches frozen recipe and PID identity',planned['run_id']==RUN and planned['protocol']==PROTOCOL and planned['protocol_sha256']==PROTOCOL_SHA and planned['argv']==started['argv']==proof['actual_argv']==expectedargv and started['pid']==reaped['pid']==r['time_process_pid']==proof['actual_time_pid']and reaped['returncode']==1 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid'])
    ck('external','actual held FD inode and first planned line hash proof',planned['time_inode']==proof['time_inode']==inode.st_ino and planned['time_device']==proof['time_device']==inode.st_dev and planned['time_fd']in proof['actual_time_output_fds']and proof['planned_launch_line_sha256']==hashlib.sha256(lines[0]).hexdigest()and proof['actual_time_start_ticks']>0)
    ck('external','actual supervisor runner tool source SHA binding',planned['supervisor_source_sha256']==sha('scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_draft.py')and planned['runner_sha256']==sha('scripts/build_p4_full_r2_abb_cbirrt_nr_draft.py')and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
    ck('external','all actual outer log hashes bound',r['metadata']==ext['metadata_path']and r['metadata_sha256']==sha(ext['metadata_path'])and r['stderr']==ext['stderr_path']and r['stderr_sha256']==sha(ext['stderr_path']))
    ck('cost','whole-child upper includes internal saved execution receipt cost',upperwall>=e['wall_s']and upperwall>=i['wall_s_through_execution_persistence']and uppercpu>=e['cpu_s']and uppercpu>=i['cpu_s_through_execution_persistence'])
    prior=load(p['actual_charge_prior']['ledger']);actual={str(q.relative_to(ROOT)):sha(q)for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if q.parent.name!=RUN}
    ck('prior','actual old36 identities all-date unchanged',len(actual)==36 and actual==e['prior_execution_sha256']=={row['execution']:row['execution_sha256']for row in prior['executions']})
    ck('prior','actual prior effective charged totals unchanged',math.fsum(row.get('charged_wall_s',row['wall_s'])for row in prior['executions'])==e['previous_r2_wall_s']==685.555705375994 and math.fsum(row.get('charged_cpu_s',row['cpu_s'])for row in prior['executions'])==e['previous_r2_cpu_s']==542.4289229999999)
    ck('scope','zero scientific binary query solve VI formal',all(e[k]==p[k]==0 for k in('query_calls','solve_calls','binary_execution_calls','formal_table_I_calls','new_VI_candidate_constructions'))and p['scientific_execution_authorized']is False and not(stage/'paths').exists()and not(stage/'runtime').exists())
    ck('scope','VI974 exhausted formal0/22500 retained',prior['vi_B_candidate_cap']==974 and prior['vi_B_remaining']['candidate_constructions']==0 and prior['formal_table_I_calls']==0 and prior['formal_table_I_required_calls']==22500)
    evidence.mkdir(parents=True)
    saved_dep=evidence/depfile.name
    with saved_dep.open('xb')as f:f.write(raw(depfile));f.flush();os.fsync(f.fileno())
    saved_manifest=evidence/'manifest.json'
    saved_record=dict(schema='P4_SAVED_PARTIAL_DEPENDENCY_ORIGINAL_BYTES_V1',source=str(depfile),source_sha256=sha(depfile),saved_copy=str(saved_dep.relative_to(ROOT)),saved_copy_sha256=sha(saved_dep),byte_count=saved_dep.stat().st_size,source_execution=execution,source_execution_sha256=sha(execution),classification='SAVED_COPY_OF_ORIGINAL_FAILED_BUILD_PARTIAL_DEPENDENCY_NOT_REBUILD_OR_REPAIR',complete_dependency_evidence=False,new_compiler_calls=0)
    with saved_manifest.open('x')as f:json.dump(saved_record,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    ck('preserve','saved original partial dependency bytes exact no reconstruction',raw(saved_dep)==raw(depfile)and sha(saved_dep)==saved_record['source_sha256']and saved_record['byte_count']==35015)
    for n,want in list(retained.items()):ck('unchanged','all read actual bytes remain '+n,hashlib.sha256(Path(n).read_bytes()).hexdigest()==want)
    failures=[q for q in checks if not q['passed']]
    external_ok=not failures
    report=dict(schema='P4_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST_V1',status='STOP_BUILD_DEPENDENCY_EVIDENCE_INCOMPLETE'if not failures else'FAIL_SAVED_STOP_EVIDENCE_REVIEW',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of CBiRRT_NR builder driver transformer and supervisor',personnel_independent=True,external_supervision_qualified=external_ok,external_timing_qualified=external_ok,external_cost_qualified=external_ok,engineering_build_qualified=False,scientific_execution_qualified=False,checks_verify_saved_STOP_and_cost_only=True,checks=checks,checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),failures=failures,source_commit=e['source_commit'],execution=execution,execution_sha256=sha(execution),manifest=manifest,manifest_exists=manifest_exists,manifest_sha256=None,receipt=receipt,receipt_sha256=sha(receipt),internal_receipt=internal,internal_receipt_sha256=sha(internal),protocol=PROTOCOL,protocol_sha256=sha(PROTOCOL),claim=claim,claim_sha256=sha(claim),external_time=timefile,external_time_sha256=sha(timefile),external_time_fields=fields,upper_wall_s=upperwall,upper_cpu_s=uppercpu,own_wall_s=e['wall_s'],own_cpu_s=e['cpu_s'],cumulative_charged_wall_s=e['previous_r2_wall_s']+upperwall,cumulative_charged_cpu_s=e['previous_r2_cpu_s']+uppercpu,compiler_pid=e['compiler_pid'],actual_translation_units=len(translation_units),expected_translation_units=6,observed_translation_units=translation_units,observed_partial_dependency_count=len(dependencies),missing_required_dependency_files=missing,dependency_evidence_complete=False,binary_observed=p['binary'],binary_observed_sha256=binary_observed_sha256,binary_qualified=False,retained_sha256=retained,new_runner_model_import_compile_binary_query_solve_protocol_prior_claim_calls=0,limitations=['STOP: compiler success is not engineering qualification. Only one output-derived MD file remains and first5 TU dependency evidence is missing; no successful manifest. Retained binary observed by SHA only, never executed/qualified. No solve/path/RBS/NR qualification.','Whole-child GNUtime includes builder import/preflight/claim/compiler/cleanup/receipts/exit and reaped descendants. Supervisor own journal/fsync costs excluded. Current upper replaces current own cost exactly once; previous effective charges remain unchanged.','Only remaining last-TU actual dependencies observed; complete6-TU frozen dependency gate NOT met. Generic system headers are partial SHA/fingerprint records; no whole OS closure claim. After-group emptiness alone cannot prove historical orphan CPU; historical UNKNOWN retained.','211 full paper obligations, VI974/974余0 and formal0/22500 persist. No P2/Isaac.'])
    cause=dict(schema='P4_CBIRRT_NR_BUILD01_INDEPENDENT_ENGINEERING_FAILURE_ROOT_CAUSE_V1',status='CONFIRMED_OUR_BUILD_DEPENDENCY_RECORDING_ERROR',generated_at_utc=report['generated_at_utc'],personnel_independent=True,execution=execution,execution_sha256=report['execution_sha256'],protocol=PROTOCOL,protocol_sha256=PROTOCOL_SHA,source_commit=e['source_commit'],compiler_exit_code=e['exit_code'],compiler_pid=e['compiler_pid'],observed_dependency_file=str(depfile),observed_dependency_sha256=sha(depfile),actual_translation_units=translation_units,expected_translation_units=[str(q)for q in sources],missing_required_dependency_files=missing,dependency_evidence_complete=False,engineering_build_qualified=False,original_author_or_paper_error_claim=False,root_cause='Our multi-input compile-and-link -MD -o recipe assumed general auxiliary-output naming applied to .d. Actual only output-derived .d remains and names only the last CBiRRT_NR TU. Independent static review incorrectly endorsed default six-file naming. This is our engineering/validation error, not evidence against author implementation or paper mathematics.',competing_explanations={'compiler_failure':'excluded by actual compiler0 and ELF','source_numerical_failure':'not tested: binary never executed','source_or_manifest_change':'excluded by actual before/after and frozen bytes','full6_dependency_evidence':'missing; cannot reconstruct retroactively by accepting binary'},repair_route='Separate new versioned fresh engineering run/claim/stage; compile each TU exactly once with explicit unique -c -MD -MF dependency and -o object, then one link over saved objects under unchanged45/90 and original cumulative caps. Freeze exact commands, source and actual prior first; do not rerun old claim or change science thresholds. Actual six .d evidence is mandatory; no probe compiler invocation or retroactive PASS.',official_documentation=[dict(url='https://gcc.gnu.org/onlinedocs/gcc/Preprocessor-Options.html',supported='MD-specific default uses -o argument with .d suffix; MF overrides this default.'),dict(url='https://gcc.gnu.org/onlinedocs/gcc-11.4.0/gcc/Overall-Options.html',supported='General auxiliary compile/link naming was wrongly generalized to MD dependency output; retain V4 incorrect assumption as history.')],prior_independent_static_report=STATIC,prior_independent_static_sha256=STATIC_SHA,prior_report_not_rewritten=True,external_timing_qualified=external_ok,external_cost_qualified=external_ok,external_time_fields=fields,upper_wall_s=upperwall,upper_cpu_s=uppercpu,new_science_compile_binary_claim_protocol_calls=0)
    with failure_out.open('x')as f:json.dump(cause,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with failure_out.with_suffix('.md').open('x')as f:f.write('# CBiRRT_NR BUILD01 工程失败独立根因\n\nSTOP：compiler exit0、reaped且组空，仍不授予build资格。六TU共用一次-MD -o，只剩output-derived p4_abb_cbirrt_nr.d且仅含末个CBiRRT_NR.cpp；五TU依赖缺失。我们的构建设计与独立静态审查错误地推广了通用aux命名规则，不是作者程序或论文理论错误。原V4、claim、binary、源码与所有失败字节保全。\n\n[GCC的MD专门规则](https://gcc.gnu.org/onlinedocs/gcc/Preprocessor-Options.html)说明-o决定.d默认名，MF可显式指定。新版本应使用六次独立-c -MD -MF与唯一object输出，再一次link；先冻结新stage/claim/命令和实际费用，保持科学条件与45/90及累计帽，不重试旧claim。\n\n费用独立资格='+str(external_ok)+'；实际GNUtime '+str(fields)+'，上界'+str(upperwall)+'wall/'+str(uppercpu)+'CPU。本次审查0compile/binary/science。\n')
    report.update(failure_report=str(failure_out.relative_to(ROOT)),failure_report_sha256=sha(failure_out),saved_partial_dependency=str(saved_dep.relative_to(ROOT)),saved_partial_dependency_sha256=sha(saved_dep),saved_partial_dependency_manifest=str(saved_manifest.relative_to(ROOT)),saved_partial_dependency_manifest_sha256=sha(saved_manifest))
    with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write('# CBiRRT_NR BUILD01 保存失败证据独立后审\n\n'+report['status']+'：已核STOP/费用事实'+str(report['checks_passed'])+'/'+str(len(checks))+'，审查差异'+str(len(failures))+'；engineering_build_qualified=false。检查通过仅表示失败事实和费用证据一致，不代表工程通过。\n\ncompiler93400 exit0/reaped、before/after组空、diagnostics空；实际只剩一份.d，六TU依赖门未通过，无成功manifest，保留ELF仅作SHA不执行。原五源/13body、21own、4829绑定与commit/protocol/claim均逐项核。\n\n真实GNUtime '+str(fields)+'，完整子生命周期上界'+str(upperwall)+'wall/'+str(uppercpu)+'CPU。费用独立资格='+str(external_ok)+'，仅替换本次own一次；累积charged '+str(report['cumulative_charged_wall_s'])+'wall/'+str(report['cumulative_charged_cpu_s'])+'CPU。0新增compile/binary/query/solve/VI/protocol/prior/claim，旧claim不重试。211义务、VI974余0、formal0/22500不变。\n')
    print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failures),failures=failures,upper_wall_s=upperwall,upper_cpu_s=uppercpu),ensure_ascii=False))
    if failures:raise SystemExit(2)

if __name__=='__main__':main()
