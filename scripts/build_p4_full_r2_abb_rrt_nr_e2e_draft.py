#!/usr/bin/env python3
"""One-target original RRT_NR e2e engineering candidate. Never query or solve.

Reuses the previous RRT_PCS builder's asset/hash/body/CPU helpers and fresh
stage/claim/watchdog pattern. Describe and validate are byte-only operations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time
import build_p4_full_r2_abb_rrt_pcs_e2e as reused
import build_p4_full_r2_abb_nr_interface_draft as nr

ROOT=reused.ROOT
OLD=reused.OLD
TEMPLATE=reused.TEMPLATE
PQP=reused.PQP
AUTHOR=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning')
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_nr_e2e_v1')
STAGE=BUILD/'physical_nr_observed'
BINARY=STAGE/'p4_abb_rrt_nr_e2e'
Q1_MANIFEST=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/nr_abb_q1_cpp_v1/manifest.json')
COMPILER='/usr/bin/x86_64-linux-gnu-g++-11'
PRE='reports/P4_FULL_R2_ABB_RRT_NR_ENTRY_PRE_DRAFT_20261015.md'
HEADER='baselines/p4_full/geometry_consistent/abb_rrt_nr_e2e_observation_draft.hpp'
DRIVER='baselines/p4_full/geometry_consistent/abb_rrt_nr_e2e_driver_draft.cpp'
KERNEL='baselines/p4_full/geometry_consistent/abb_nr_interface_kernel_draft.cpp'
CORE='baselines/p4_full/geometry_consistent/physical_nr_abb_cpp_draft.hpp'
FIXTURE='reports/P4_FULL_R2_ABB_NR_INTERFACE_SAVED_INPUTS_20261015.json'
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),HEADER,DRIVER,KERNEL,CORE,FIXTURE,PRE,
     'scripts/build_p4_full_r2_abb_nr_interface_draft.py',
     'baselines/p4_full/geometry_consistent/abb_nr_interface_observation_draft.hpp',
     'baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_observation.hpp',
     'scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py',
     'baselines/p4_full/geometry_consistent/pcs_source_trace.hpp']
RUN='20261015_R2_ABB_RRT_NR_E2E_BUILD01'
CLAIM='P4_R2_ABB_RRT_NR_E2E_BUILD_45W_90CPU_20261015'
LOCAL_POST=ROOT/'reports/P4_FULL_R2_ABB_NR_LOCAL_INDEPENDENT_POST_20261015.json'
LOCAL_ROOT_POST=ROOT/'reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_INDEPENDENT_POST_20261015.json'
LOCAL_ROOT_RAW=ROOT/'reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_20261015.json'
NR_SOURCE=['proj_classes/kdl_class.cpp','proj_classes/kdl_class.h',
    'validity_checkers/StateValidityCheckerNR.cpp','validity_checkers/StateValidityCheckerNR.h',
    'planners/RRT_NR.cpp','planners/RRT_NR.h']
LINKED=['proj_classes/kdl_class.cpp','validity_checkers/StateValidityCheckerNR.cpp',
    'validity_checkers/collisionDetection.cpp','planners/RRT_NR.cpp']
sha,load,utc,new_json,cpu,live_group_cpu,body_span=(reused.sha,reused.load,reused.utc,
    reused.new_json,reused.cpu,reused.live_group_cpu,reused.body_span)

def prior():
    files=sorted(p for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json') if p.parent.name!=RUN)
    rows=[load(p) for p in files]
    return {str(p.relative_to(ROOT)):sha(p) for p in files},math.fsum(r['wall_s'] for r in rows),math.fsum(r['cpu_s'] for r in rows)
def local_gate():
    p=ROOT/'results/p4_full/20261015_R2_ABB_NR_LOCAL01/execution.json'
    if not p.exists():return {'ready':False,'status':'MUST_PASS_II_LOCAL_GATE_BEFORE_FREEZE','execution':str(p)}
    d=load(p)
    execution_ready=(d.get('next_planner_gate_supported') is True and d.get('soundness_passed') is True
        and d.get('endpoint_project_gate_by_environment',{}).get('II') is True
        and d.get('full_node_queue_checked') is True
        and not d.get('uncompleted_top_requests') and not d.get('uncompleted_node_ids')
        and d.get('status') in ('FIXED_LOCAL_ABB_NR_QUALIFIED','FIXED_LOCAL_ABB_NR_PARTIAL'))
    protocol=Path(d['protocol']);protocol=protocol if protocol.is_absolute() else ROOT/protocol
    protocol_ready=(sha(protocol)==d.get('protocol_sha256')==d.get('protocol_after_sha256'))
    def complete_saved_checks(report,count):
        rows=report.get('checks')
        return (report.get('checks_total')==count and report.get('checks_passed')==count
            and report.get('checks_failed')==0 and report.get('failed_checks')==[]
            and isinstance(rows,list) and len(rows)==count
            and all(row.get('passed') is True for row in rows))
    saved=load(LOCAL_POST) if LOCAL_POST.exists() else {}
    independent=load(LOCAL_ROOT_POST) if LOCAL_ROOT_POST.exists() else {}
    raw_links=load(LOCAL_ROOT_RAW) if LOCAL_ROOT_RAW.exists() else {}
    # Both exact, reviewed saved-evidence contracts are required. The first
    # author declares personnel_independent=False; the second is by a separate
    # reviewer. File existence or the execution's gate flag alone never opens it.
    saved_ready=(saved.get('schema')=='P4_R2_ABB_NR_LOCAL_SAVED_POST_V1'
        and saved.get('status')=='PASS_SAVED_EVIDENCE_POST'
        and saved.get('run_id')==d.get('run_id')
        and saved.get('execution_sha256')==sha(p)
        and saved.get('protocol_sha256')==sha(protocol)
        and saved.get('audit_author_wrote_runner') is True
        and saved.get('personnel_independent') is False
        and saved.get('result',{}).get('next_environment_II_planner_gate') is True
        and saved.get('audit_scientific_calls')==dict.fromkeys(('solve','NR','FK','Jacobian','IK','PQP','RNG','compile'),0)
        and complete_saved_checks(saved,117258))
    independent_ready=(independent.get('schema')=='P4_NR_LOCAL_PERSONNEL_INDEPENDENT_STDLIB_SAVED_POST_V1'
        and independent.get('status')=='PASS_SAVED_EVIDENCE_AUDIT'
        and independent.get('run_id')==d.get('run_id')
        and independent.get('reviewer')=='nr_local_independent_post (not runner author)'
        and independent.get('zero_new_scientific_calls') is True
        and independent.get('zero_compile_calls') is True
        and complete_saved_checks(independent,218766))
    raw_links_ready=(raw_links.get('schema')=='P4_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_V1'
        and raw_links.get('status')=='PASS_RAW_LINK_ADDENDUM'
        and raw_links.get('run_id')==d.get('run_id')
        and LOCAL_ROOT_POST.exists() and raw_links.get('main_report_sha256')==sha(LOCAL_ROOT_POST)
        and raw_links.get('zero_new_scientific_calls') is True
        and raw_links.get('zero_compile_calls') is True
        and complete_saved_checks(raw_links,666))
    return {'ready':execution_ready and protocol_ready and saved_ready and independent_ready and raw_links_ready,
        'execution_gate_ready':execution_ready,'protocol_gate_ready':protocol_ready,
        'saved_POST_gate_ready':saved_ready,'personnel_independent_POST_gate_ready':independent_ready,
        'personnel_independent_raw_link_gate_ready':raw_links_ready,
        'status':d.get('status'),
        'execution':str(p),'execution_sha256':sha(p),'saved_POST':str(LOCAL_POST),
        'protocol':str(protocol),'protocol_sha256':sha(protocol),
        'saved_POST_sha256':sha(LOCAL_POST) if LOCAL_POST.exists() else 'MUST_PASS_SAVED_POST_BEFORE_FREEZE',
        'saved_POST_contract':{'schema':'P4_R2_ABB_NR_LOCAL_SAVED_POST_V1','status':'PASS_SAVED_EVIDENCE_POST',
            'checks_total':117258,'checks_passed':117258,'checks_failed':0,'personnel_independent':False,
            'execution_and_protocol_sha256_required':True,'result.next_environment_II_planner_gate':True},
        'personnel_independent_POST':str(LOCAL_ROOT_POST),
        'personnel_independent_POST_sha256':sha(LOCAL_ROOT_POST) if LOCAL_ROOT_POST.exists() else 'MUST_PASS_PERSONNEL_INDEPENDENT_POST_BEFORE_FREEZE',
        'personnel_independent_POST_contract':{'schema':'P4_NR_LOCAL_PERSONNEL_INDEPENDENT_STDLIB_SAVED_POST_V1',
            'status':'PASS_SAVED_EVIDENCE_AUDIT','checks_total':218766,'checks_passed':218766,'checks_failed':0,
            'reviewer':'nr_local_independent_post (not runner author)',
            'zero_new_scientific_calls':True,'zero_compile_calls':True},
        'personnel_independent_raw_link_POST':str(LOCAL_ROOT_RAW),
        'personnel_independent_raw_link_POST_sha256':sha(LOCAL_ROOT_RAW) if LOCAL_ROOT_RAW.exists() else 'MUST_PASS_RAW_LINK_POST_BEFORE_FREEZE',
        'personnel_independent_raw_link_POST_contract':{'schema':'P4_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_V1',
            'status':'PASS_RAW_LINK_ADDENDUM','checks_total':666,'checks_passed':666,'checks_failed':0,
            'main_report_sha256_required':True,'zero_new_scientific_calls':True,'zero_compile_calls':True}}
def assets():
    result=nr.assets()
    manifest=nr.BUILD/'manifest.json';d=load(manifest)
    if d.get('status')!='BUILT_NOT_QUERIED' or d.get('exit_code')!=0:raise ValueError('EXACT_SUCCESSFUL_NR_INTERFACE_ENGINEERING_REQUIRED')
    result[str(manifest)]=sha(manifest)
    for field in ('own_source_sha256','template_assets_sha256'):
        for name,wanted in d[field].items():
            p=Path(name);p=p if p.is_absolute() else ROOT/p
            if sha(p)!=wanted:raise ValueError('NR_INTERFACE_BOUND_ASSET_CHANGED '+str(p))
            result[str(p)]=wanted
    for field in ('compiled_source_sha256','mesh_sha256'):
        for name,wanted in d[field].items():
            p=nr.STAGE/name
            if sha(p)!=wanted:raise ValueError('NR_INTERFACE_BUILT_STAGE_CHANGED '+str(p))
            result[str(p)]=wanted
    for field,hashfield in [('protocol','protocol_sha256'),('claim','claim_sha256'),('binary','binary_sha256')]:
        p=Path(d[field]);p=p if p.is_absolute() else ROOT/p
        if sha(p)!=d[hashfield]:raise ValueError('NR_INTERFACE_BUILD_LINK_CHANGED '+field)
        result[str(p)]=d[hashfield]
    gate=local_gate()
    if 'execution_sha256' in gate:
        result[gate['execution']]=gate['execution_sha256'];local=load(gate['execution'])
        if local.get('bound_files_after_sha256')!=local.get('bound_files_sha256'):raise ValueError('LOCAL_BOUND_ASSETS_CHANGED')
        for name,wanted in local['bound_files_sha256'].items():
            p=Path(name);p=p if p.is_absolute() else ROOT/p
            if sha(p)!=wanted:raise ValueError('LOCAL_BOUND_ASSET_CHANGED '+str(p))
            result[str(p)]=wanted
        for field,hashfield in [('protocol','protocol_sha256'),('claim','claim_sha256')]:
            p=Path(local[field]);p=p if p.is_absolute() else ROOT/p
            if sha(p)!=local[hashfield]:raise ValueError('LOCAL_PROTOCOL_OR_CLAIM_CHANGED')
            result[str(p)]=local[hashfield]
    if LOCAL_POST.exists():result[str(LOCAL_POST)]=sha(LOCAL_POST)
    if LOCAL_ROOT_POST.exists():result[str(LOCAL_ROOT_POST)]=sha(LOCAL_ROOT_POST)
    if LOCAL_ROOT_RAW.exists():result[str(LOCAL_ROOT_RAW)]=sha(LOCAL_ROOT_RAW)
    for name in ('run/plan_NR.cpp','run/plan_NR.h'):result[str(AUTHOR/name)]=sha(AUTHOR/name)
    return result
def draft_protocol():
    previous,wall,used_cpu=prior()
    return {'schema':'P4_R2_ABB_RRT_NR_E2E_ENGINEERING_V1','frozen':False,
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False,'Q1_independent_POST_confirmed':False,'II_local_gate_confirmed':False},
        'claim_id':CLAIM,'run_id':RUN,'build_root':str(BUILD),'stage_root':str(STAGE),'binary':str(BINARY),
        'author_commit':'909bd72fff778aca8682c96f9eb86ae4eb75557b',
        'template_stage':str(TEMPLATE),'template_assets_sha256':assets(),'local_gate':local_gate(),
        'own_source_sha256':{p:sha(ROOT/p) for p in OWN},
        'prior_execution_sha256':previous,'previous_r2_wall_s':wall,'previous_r2_cpu_s':used_cpu,
        'budget':{'wall_s':45.,'cpu_s':90.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'allowed_changes':['Only kdl::GD body uses the existing physical NR seam, original body complete file preserved.',
            'Original state-level NR reconstruct complete body in returning lambda; full qa/qb/Confs/returned observed post-return.',
            'RRT_NR save2file remove(temp) becomes retain(temp), unique explicit IO deviation; inverse replacement must recover original source.',
            'Original SVC vector numerical/recursion and corrected collision code restored byte-identical; no local trace expansion.',
            'New thin II seed7 range2.6 solve10 driver retains original resolution0.1 and sampler bounds; building never queries.'],
        'linked_author_cpp':LINKED,'query_calls':0,'solve_calls':0,'rng_calls':0,'new_VI_candidate_constructions':0,
        'scientific_execution_authorized':False,
        'one_shot':'Fresh atomic claim/stage/ledger; no retry/reset/resume, failed prefix retained.'}
def instrument(stage):
    changes=[];p=stage/'proj_classes/kdl_class.cpp';original=p.read_text();a,b=body_span(original,'bool kdl::GD(State q_init_flip)')
    saved=stage/'preserved_originals/proj_classes/kdl_class.cpp';saved.parent.mkdir(parents=True);shutil.copy2(p,saved)
    seam='\n return p4nr_iface::physical_gd(q_init_flip,T_pose[0][3],L,include_joint_limits,q_solution,IK_counter,IK_time);\n'
    p.write_text(original[:a+1]+seam+original[b:])
    changes.append({'file':str(p.relative_to(stage)),'before':hashlib.sha256(original.encode()).hexdigest(),
        'after':sha(p),'original_GD_body_sha256':hashlib.sha256(original[a+1:b].encode()).hexdigest(),
        'preserved_original':str(saved.relative_to(stage)),'preserved_original_sha256':sha(saved),'kind':'EXISTING_GD_ONLY_NUMERICAL_SEAM'})
    p=stage/'validity_checkers/StateValidityCheckerNR.cpp';s=p.read_text();before=sha(p)
    sig='bool StateValidityChecker::reconstructRBS(const ob::State *s1, const ob::State *s2, Matrix &Confs)'
    a,b=body_span(s,sig);body=s[a+1:b]
    inserted='\n const bool p4_return=[&]() -> bool {'+body+'}();\n p4e2e::observe_nr_reconstruction(s1,s2,Confs,p4_return);\n return p4_return;\n'
    if inserted.count(body)!=1:raise ValueError('ORIGINAL_STATE_RECON_BODY_NOT_RETAINED_ONCE')
    p.write_text(s[:a+1]+inserted+s[b:]);changes.append({'file':str(p.relative_to(stage)),'before':before,'after':sha(p),
        'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'kind':'POST_RETURN_COMPLETE_CONFS_OBSERVATION'})
    p=stage/'planners/RRT_NR.cpp';s=p.read_text();needle='std::remove("./paths/temp.txt");';replacement='/* P4 I/O observation: retain ./paths/temp.txt verbatim. */'
    if s.count(needle)!=1:raise ValueError('UNIQUE_TEMP_REMOVE_REQUIRED')
    before=sha(p);s=s.replace(needle,replacement)
    if s.replace(replacement,needle)!=(TEMPLATE/'planners/RRT_NR.cpp').read_text():raise ValueError('RRT_NR_NON_IO_CHANGE')
    p.write_text(s);changes.append({'file':str(p.relative_to(stage)),'before':before,'after':sha(p),'kind':'RETAIN_TEMP_IO_DEVIATION_ONLY'})
    for name in ['planners/RRT_NR.h','validity_checkers/collisionDetection.cpp']:
        if sha(stage/name)!=sha(TEMPLATE/name):raise ValueError('UNEXPECTED_LOCAL_TRACE_OR_SOURCE_CHANGE')
    return changes
def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    if set(spec)!=set(expected) or any(spec[k]!=v for k,v in expected.items() if k not in ('frozen','reviews')):raise ValueError('EXACT_CURRENT_RECIPE_REQUIRED')
    if type(spec['frozen']) is not bool or set(spec['reviews'])!=set(expected['reviews']) or any(type(v) is not bool for v in spec['reviews'].values()):raise ValueError('INVALID_REVIEW_FIELDS')
    if execute:
        if not spec['frozen'] or not all(spec['reviews'].values()) or not spec['local_gate']['ready']:raise ValueError('REVIEW_AND_II_LOCAL_GATE_AND_ROOT_FREEZE_REQUIRED')
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        for name in [*OWN,str(protocol.relative_to(ROOT))]:
            subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
            if subprocess.check_output(['git','status','--porcelain','--',name],cwd=ROOT,text=True):raise ValueError('UNCOMMITTED '+name)
        for name,wanted in spec['own_source_sha256'].items():
            blob=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)
            if hashlib.sha256(blob).hexdigest()!=wanted:raise ValueError('COMMIT_BLOB_MISMATCH '+name)
        return commit
def build(spec,protocol):
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN
    if BUILD.exists() or folder.exists():raise FileExistsError('FRESH_STAGE_AND_LEDGER_REQUIRED')
    wall_cap=min(45.,3600.-spec['previous_r2_wall_s']);cpu_cap=min(90.,7200.-spec['previous_r2_cpu_s'])
    if min(wall_cap,cpu_cap)<=0:raise ValueError('R2_BUDGET_EXHAUSTED')
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    new_json(claim,{'schema':'P4_R2_ABB_RRT_NR_E2E_ENGINEERING_CLAIM_V1','claim_id':CLAIM,'created_at_utc':utc(),
        'source_commit':commit,'protocol':str(protocol),'protocol_sha256':sha(protocol),'budget':spec['budget'],
        'own_source_sha256':spec['own_source_sha256'],'no_retry_reset_or_resume':True})
    BUILD.mkdir();folder.mkdir();begun=time.monotonic();used_cpu=cpu();proc=None;error=None
    previous_handler=signal.getsignal(signal.SIGALRM)
    def alarm(*_):raise TimeoutError('BUILD_WALL_CAP')
    record={'schema':'P4_R2_ABB_RRT_NR_E2E_ENGINEERING_EXECUTION_V1','run_id':RUN,'classification':'ENGINEERING_BUILD_ONLY',
        'source_commit':commit,'protocol':str(protocol),'protocol_sha256':sha(protocol),'claim':str(claim.relative_to(ROOT)),
        'claim_sha256':sha(claim),'own_source_sha256':spec['own_source_sha256'],'author_commit':spec['author_commit'],
        'prior_execution_sha256':spec['prior_execution_sha256'],'previous_r2_wall_s':spec['previous_r2_wall_s'],
        'previous_r2_cpu_s':spec['previous_r2_cpu_s'],'query_calls':0,'solve_calls':0,'rng_calls':0,'formal_table_I_calls':0,
        'new_VI_candidate_constructions':0,'started_at_utc':utc(),'status':'STOP_PREFIX_RETAINED'}
    try:
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,wall_cap)
        shutil.copytree(TEMPLATE,STAGE,ignore=shutil.ignore_patterns('.git','paths','p4_abb_pcs_thin','compile.stdout','compile.stderr'))
        changes=instrument(STAGE);sources=[STAGE/p for p in LINKED]
        cmd=[COMPILER,'-std=c++17','-O1','-g0','-Wall','-Wextra','-pthread','-I/opt/ros/humble/include/ompl-1.7','-I/usr/include/eigen3',
            '-I'+str(PQP/'include'),'-I'+str(STAGE/'proj_classes'),'-I'+str(STAGE/'validity_checkers'),'-I'+str(STAGE/'planners'),
            '-I'+str((ROOT/HEADER).parent),'-include',str(ROOT/HEADER),str(ROOT/DRIVER),str(ROOT/KERNEL),*[str(p) for p in sources],
            str(PQP/'lib/libPQP.a'),'-L/opt/ros/humble/lib/x86_64-linux-gnu','-Wl,-rpath,/opt/ros/humble/lib/x86_64-linux-gnu',
            '-lompl','-lorocos-kdl','-lboost_filesystem','-lboost_system','-lboost_serialization','-lboost_program_options','-o',str(BINARY)]
        record.update(command=cmd,changes=changes,template_assets_sha256=spec['template_assets_sha256'])
        headers=sorted(p for p in STAGE.rglob('*') if p.is_file() and p.suffix in ('.h','.hpp'))
        record['compiled_source_sha256']={str(p.relative_to(STAGE)):sha(p) for p in [*sources,*headers]}
        record['mesh_sha256']={str(p.relative_to(STAGE)):sha(p) for p in sorted((STAGE/'simulator').glob('*.tris'))}
        if time.monotonic()-begun>=wall_cap or cpu()-used_cpu>=cpu_cap:raise TimeoutError('BUILD_PREPARATION_CAP')
        with (BUILD/'compile.stdout').open('x') as out,(BUILD/'compile.stderr').open('x') as err:
            def limits():resource.setrlimit(resource.RLIMIT_CPU,(90,90))
            proc=subprocess.Popen(cmd,stdout=out,stderr=err,cwd=ROOT,preexec_fn=limits,start_new_session=True)
            while proc.poll() is None:
                if time.monotonic()-begun>=wall_cap or cpu()-used_cpu+live_group_cpu(proc.pid)>=cpu_cap:raise TimeoutError('BUILD_WALL_OR_AGGREGATE_LIVE_CPU_CAP')
                try:proc.wait(timeout=.02)
                except subprocess.TimeoutExpired:pass
        record['exit_code']=proc.returncode
        if proc.returncode:raise RuntimeError('BUILD_FAILED')
        record.update(status='BUILT_NOT_QUERIED',binary=str(BINARY),binary_sha256=sha(BINARY))
    except BaseException as exc:
        error=exc;record['termination_reason']=repr(exc)
        if proc is not None and proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        if proc is not None:record['exit_code']=proc.returncode
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous_handler)
        record['template_assets_after_sha256']={p:sha(p) for p in spec['template_assets_sha256']}
        if record['template_assets_after_sha256']!=spec['template_assets_sha256']:
            record['status']='STOP_OLD_ASSET_CHANGED';error=error or RuntimeError('OLD_ASSET_CHANGED')
        record.update(ended_at_utc=utc(),wall_s=time.monotonic()-begun,cpu_s=cpu()-used_cpu)
        new_json(BUILD/'manifest.json',{**record,'engineering_execution':str((folder/'execution.json').relative_to(ROOT))})
        new_json(folder/'execution.json',{**record,'external_manifest':str(BUILD/'manifest.json'),'manifest_sha256':sha(BUILD/'manifest.json')})
    print(json.dumps({'status':record['status'],'wall_s':record['wall_s'],'cpu_s':record['cpu_s'],'query_calls':0,'solve_calls':0}))
    if error is not None:raise error
def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_DRAFT_VALIDATED_ZERO_QUERY_ZERO_COMPILE');return
    build(spec,protocol)
if __name__=='__main__':main()
