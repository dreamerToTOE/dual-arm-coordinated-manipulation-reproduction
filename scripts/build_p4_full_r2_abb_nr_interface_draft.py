#!/usr/bin/env python3
"""One-target ABB NR interface engineering candidate. Never query or solve.

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

ROOT=reused.ROOT
OLD=reused.OLD
TEMPLATE=reused.TEMPLATE
PQP=reused.PQP
AUTHOR=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning')
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_nr_interface_v1')
STAGE=BUILD/'physical_nr_observed'
BINARY=STAGE/'p4_abb_nr_interface'
Q1_MANIFEST=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/nr_abb_q1_cpp_v1/manifest.json')
COMPILER='/usr/bin/x86_64-linux-gnu-g++-11'
PRE='reports/P4_FULL_R2_ABB_NR_INTERFACE_PRE_DRAFT_20261015.md'
HEADER='baselines/p4_full/geometry_consistent/abb_nr_interface_observation_draft.hpp'
DRIVER='baselines/p4_full/geometry_consistent/abb_nr_interface_draft.cpp'
KERNEL='baselines/p4_full/geometry_consistent/abb_nr_interface_kernel_draft.cpp'
CORE='baselines/p4_full/geometry_consistent/physical_nr_abb_cpp_draft.hpp'
FIXTURE='reports/P4_FULL_R2_ABB_NR_INTERFACE_SAVED_INPUTS_20261015.json'
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),HEADER,DRIVER,KERNEL,CORE,FIXTURE,PRE,
     'scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py',
     'baselines/p4_full/geometry_consistent/pcs_source_trace.hpp']
RUN='20261015_R2_ABB_NR_INTERFACE_BUILD01'
CLAIM='P4_R2_ABB_NR_INTERFACE_BUILD_45W_90CPU_20261015'
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
def assets():
    result=reused.template_assets()
    q1_build=load(Q1_MANIFEST)
    if q1_build.get('status')!='BUILT_NOT_QUERIED' or q1_build.get('command',[None])[0]!=COMPILER:
        raise ValueError('EXACT_SUCCESSFUL_Q1_COMPILER_BUILD_REQUIRED')
    libraries=q1_build['library_headers_sha256']
    if len(libraries)!=379 or COMPILER not in libraries:raise ValueError('EXACT_Q1_379_LIBRARY_HEADERS_REQUIRED')
    result[str(Q1_MANIFEST)]=sha(Q1_MANIFEST)
    for name,wanted in libraries.items():
        if sha(name)!=wanted:raise ValueError('Q1_COMPILER_OR_LIBRARY_HEADER_CHANGED '+name)
        result[name]=wanted
    for name in NR_SOURCE:
        template=TEMPLATE/name; original=AUTHOR/name
        if sha(template)!=sha(original):raise ValueError('NR_TEMPLATE_AUTHOR_BYTES_DIFFER '+name)
        result[str(template)]=sha(template);result[str(original)]=sha(original)
    for p in [Path('/usr/lib/x86_64-linux-gnu/liborocos-kdl.so'),
              ROOT/'results/p4_full/20261015_R2_NR_ABB_Q1_01/execution.json',
              ROOT/'reports/P4_FULL_R2_NR_ABB_Q1_INDEPENDENT_SAVED_POST_REVIEW_20261015.json']:
        result[str(p)]=sha(p)
    q1=load(ROOT/'results/p4_full/20261015_R2_NR_ABB_Q1_01/execution.json')
    if q1.get('status')!='PASS_FIXED64_NUMERICAL_TRANSFER':raise ValueError('Q1_NUMERICAL_TRANSFER_REQUIRED')
    post=load(ROOT/'reports/P4_FULL_R2_NR_ABB_Q1_INDEPENDENT_SAVED_POST_REVIEW_20261015.json')
    if post.get('status')!='PASS_INDEPENDENT_SAVED_POST_REVIEW' or post.get('checks_total')!=post.get('checks_passed'):
        raise ValueError('Q1_INDEPENDENT_POST_PASS_REQUIRED')
    return result
def draft_protocol():
    previous,wall,used_cpu=prior()
    return {'schema':'P4_R2_ABB_NR_INTERFACE_ENGINEERING_V1','frozen':False,
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False,'Q1_independent_POST_confirmed':False},
        'claim_id':CLAIM,'run_id':RUN,'build_root':str(BUILD),'stage_root':str(STAGE),'binary':str(BINARY),
        'author_commit':'909bd72fff778aca8682c96f9eb86ae4eb75557b',
        'template_stage':str(TEMPLATE),'template_assets_sha256':assets(),
        'own_source_sha256':{p:sha(ROOT/p) for p in OWN},
        'prior_execution_sha256':previous,'previous_r2_wall_s':wall,'previous_r2_cpu_s':used_cpu,
        'budget':{'wall_s':45.,'cpu_s':90.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'allowed_changes':['Only kdl::GD body is replaced by the already-Q1-qualified physical NR call and original q_solution API.',
            'Original GD source bytes copied verbatim under preserved_originals before replacement; all other kdl bodies/header retained.',
            'NR SVC numerical/recursion bodies retained once inside returning lambdas; entry/post-return observation only.',
            'Existing corrected collision geometry/policy retained; PQP_Tolerance calls route through the existing trace wrapper.',
            'Original RRT_NR.cpp/.h remain byte-identical and linked. Local driver exposes no solve/RNG entry.'],
        'linked_author_cpp':LINKED,'query_calls':0,'solve_calls':0,'rng_calls':0,'new_VI_candidate_constructions':0,
        'scientific_execution_authorized':False,
        'one_shot':'Fresh atomic claim/stage/ledger; no retry/reset/resume, failed prefix retained.'}
def wrap(source,signature,kind,args,result,return_type='bool'):
    a,b=body_span(source,signature);body=source[a+1:b]
    inserted='\n auto p4_id=p4pcs::enter("'+kind+'",'+args+');\n const '+return_type+' p4_return=[&]() -> '+return_type+' {'+body+'}();\n p4nr_iface::leave(p4_id,"'+kind+'",'+result+');\n return p4_return;\n'
    if inserted.count(body)!=1:raise ValueError('ORIGINAL_BODY_NOT_RETAINED_ONCE')
    return source[:a+1]+inserted+source[b:]
def instrument(stage):
    changes=[]
    p=stage/'proj_classes/kdl_class.cpp';original=p.read_text();a,b=body_span(original,'bool kdl::GD(State q_init_flip)')
    saved=stage/'preserved_originals/proj_classes/kdl_class.cpp';saved.parent.mkdir(parents=True);shutil.copy2(p,saved)
    seam='\n return p4nr_iface::physical_gd(q_init_flip,T_pose[0][3],L,include_joint_limits,q_solution,IK_counter,IK_time);\n'
    p.write_text(original[:a+1]+seam+original[b:])
    changes.append({'file':str(p.relative_to(stage)),'before':hashlib.sha256(original.encode()).hexdigest(),
        'after':sha(p),'original_GD_body_sha256':hashlib.sha256(original[a+1:b].encode()).hexdigest(),
        'preserved_original':str(saved.relative_to(stage)),'preserved_original_sha256':sha(saved),'kind':'GD_ONLY_NUMERICAL_SEAM'})
    p=stage/'validity_checkers/StateValidityCheckerNR.cpp';s=p.read_text();before=sha(p)
    specs=[('bool StateValidityChecker::IKproject(State &q, bool includeObs)','nr_project','{{"q12",q},{"includeObs",includeObs}}','{{"returned",p4_return},{"q12",q}}'),
      ('bool StateValidityChecker::isValidRBS(State &q)','nr_valid_midpoint','{{"q12",q}}','{{"returned",p4_return},{"q12",q}}'),
      ('bool StateValidityChecker::checkMotionRBS(State s1, State s2, int recursion_depth, int non_decrease_count)','nr_rbs','{{"qa12",s1},{"qb12",s2},{"recursion_depth",recursion_depth},{"non_decrease_count",non_decrease_count}}','{{"returned",p4_return}}'),
      ('bool StateValidityChecker::reconstructRBS(State q1, State q2, Matrix &M, int iteration, int last_index, int firstORsecond)','nr_reconstruct','{{"qa12",q1},{"qb12",q2},{"iteration",iteration},{"last_index",last_index},{"firstORsecond",firstORsecond}}','{{"returned",p4_return}}')]
    bodies={}
    for sig,kind,args,result in specs:
        a,b=body_span(s,sig);bodies[sig]=hashlib.sha256(s[a+1:b].encode()).hexdigest();s=wrap(s,sig,kind,args,result)
    p.write_text(s);changes.append({'file':str(p.relative_to(stage)),'before':before,'after':sha(p),'body_sha256':bodies,'kind':'ORIGINAL_NR_BODIES_WITH_OBSERVATION'})
    p=stage/'validity_checkers/collisionDetection.cpp';s=p.read_text();before=sha(p);n=s.count('PQP_Tolerance(&res[')
    if n!=142:raise ValueError('EXACT142_EXISTING_PQP_CALL_SITES_REQUIRED')
    s=s.replace('PQP_Tolerance(&res[','p4pcs::query(&res[')
    s=wrap(s,'int collisionDetection::collision_state(Matrix M, State q1, State q2)',
        'collision','{{"q1",q1},{"q2",q2}}','{{"returned",p4_return}}','int')
    p.write_text(s);changes.append({'file':str(p.relative_to(stage)),'before':before,'after':sha(p),'kind':'EXISTING_PQP_OBSERVATION_ONLY','pqp_call_sites':n})
    for name in ['planners/RRT_NR.cpp','planners/RRT_NR.h']:
        if sha(stage/name)!=sha(TEMPLATE/name):raise ValueError('ORIGINAL_RRT_NR_CHANGED')
    return changes
def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    if set(spec)!=set(expected) or any(spec[k]!=v for k,v in expected.items() if k not in ('frozen','reviews')):raise ValueError('EXACT_CURRENT_RECIPE_REQUIRED')
    if type(spec['frozen']) is not bool or set(spec['reviews'])!=set(expected['reviews']) or any(type(v) is not bool for v in spec['reviews'].values()):raise ValueError('INVALID_REVIEW_FIELDS')
    if execute:
        if not spec['frozen'] or not all(spec['reviews'].values()):raise ValueError('REVIEW_AND_ROOT_FREEZE_REQUIRED')
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
    new_json(claim,{'schema':'P4_R2_ABB_NR_INTERFACE_ENGINEERING_CLAIM_V1','claim_id':CLAIM,'created_at_utc':utc(),
        'source_commit':commit,'protocol':str(protocol),'protocol_sha256':sha(protocol),'budget':spec['budget'],
        'own_source_sha256':spec['own_source_sha256'],'no_retry_reset_or_resume':True})
    BUILD.mkdir();folder.mkdir();begun=time.monotonic();used_cpu=cpu();proc=None;error=None
    previous_handler=signal.getsignal(signal.SIGALRM)
    def alarm(*_):raise TimeoutError('BUILD_WALL_CAP')
    record={'schema':'P4_R2_ABB_NR_INTERFACE_ENGINEERING_EXECUTION_V1','run_id':RUN,'classification':'ENGINEERING_BUILD_ONLY',
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
