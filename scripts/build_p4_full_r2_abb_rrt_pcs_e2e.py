#!/usr/bin/env python3
"""Draft one-target external RRT_PCS build; describe reads bytes, build never queries.

No scientific module imports. Only a committed exact frozen recipe can compile.
The existing qualified plain stage, all old paths and all failures are read-only.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
OLD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1')
TEMPLATE=OLD/'geometry_consistent_plain'
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_pcs_e2e_v1')
STAGE=BUILD/'geometry_consistent_observed'
PQP=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3')
PRE='reports/P4_FULL_R2_ABB_RRT_PCS_END_TO_END_PRE_DRAFT_20261015.md'
HEADER='baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_observation.hpp'
DRIVER='baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_driver.cpp'
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),HEADER,DRIVER,PRE]
RUN='20261015_R2_ABB_RRT_PCS_E2E_BUILD01'
CLAIM='P4_R2_ABB_RRT_PCS_E2E_BUILD_45W_90CPU_20261015'
BINARY=STAGE/'p4_abb_rrt_pcs_e2e'
ENDPOINTS=[f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_{i}.json' for i in (0,1)]
SIG='bool StateValidityChecker::reconstructRBS(const ob::State *s1, const ob::State *s2, Matrix &Confs, int active_chain, int ik_sol)'
IDENTIFY_SIG='State StateValidityChecker::identify_state_ik(State q1, State q2, State ik)'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def new_json(p,value):
    with Path(p).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cpu():
    a=resource.getrusage(resource.RUSAGE_SELF);b=resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime
def prior():
    files=sorted(p for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json') if p.parent.name!=RUN)
    rows=[load(p) for p in files]
    return {str(p.relative_to(ROOT)):sha(p) for p in files},math.fsum(r['wall_s'] for r in rows),math.fsum(r['cpu_s'] for r in rows)
def template_assets():
    manifest=load(OLD/'manifest.json')
    if manifest['status']!='BUILT_NOT_EXECUTED_OR_QUALIFIED' or manifest['author_commit']!='909bd72fff778aca8682c96f9eb86ae4eb75557b':
        raise ValueError('OLD_QUALIFIED_BUILD_REQUIRED')
    entries=[e for e in manifest['entries'] if (e['variant'],e['mode'])==('geometry_consistent','plain')]
    if len(entries)!=1 or entries[0]['exit_code']!=0:raise ValueError('EXACT_OLD_PLAIN_TARGET_REQUIRED')
    entry=entries[0];assets={str(OLD/'manifest.json'):sha(OLD/'manifest.json')}
    for field in ('source_sha256','mesh_sha256'):
        for relative,expected in entry[field].items():
            p=TEMPLATE/relative
            if sha(p)!=expected:raise ValueError('OLD_PLAIN_ASSET_CHANGED '+str(p))
            assets[str(p)]=expected
    old_binary=Path(entry['binary'])
    if sha(old_binary)!=entry['binary_sha256']:raise ValueError('OLD_BINARY_CHANGED')
    assets[str(old_binary)]=entry['binary_sha256']
    for p in [Path(manifest['protocol']),ROOT/manifest['claim'],ROOT/manifest['engineering_execution'],
              ROOT/'configs/p4_full/author_source_manifest.json',PQP/'lib/libPQP.a',
              Path('/opt/ros/humble/lib/x86_64-linux-gnu/libompl.so'),Path('/usr/include/nlohmann/json.hpp'),
              TEMPLATE/'run/plan_PCS.cpp',TEMPLATE/'run/plan_PCS.h']:
        assets[str(p)]=sha(p)
    if sha(ROOT/manifest['claim'])!=manifest['claim_sha256']:raise ValueError('OLD_CLAIM_CHANGED')
    return assets
def draft_protocol():
    previous,wall,used_cpu=prior()
    return {'schema':'P4_R2_ABB_RRT_PCS_E2E_ENGINEERING_V1','frozen':False,
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False},
        'claim_id':CLAIM,'run_id':RUN,'build_root':str(BUILD),'stage_root':str(STAGE),'binary':str(BINARY),
        'author_commit':'909bd72fff778aca8682c96f9eb86ae4eb75557b',
        'template_stage':str(TEMPLATE),'template_assets_sha256':template_assets(),
        'own_source_sha256':{p:sha(ROOT/p) for p in OWN},
        'prior_execution_sha256':previous,'previous_r2_wall_s':wall,'previous_r2_cpu_s':used_cpu,
        'budget':{'wall_s':45.,'cpu_s':90.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'allowed_changes':['State-level reconstructRBS original complete body in returning lambda; observe only after return.',
            'Vector-level identify_state_ik original complete body in returning lambda; record q/input_ik/returned_ik after return, zero extra IK.',
            'RRT save2file remove(temp) becomes retain(temp), I/O deviation only.'],
        'linked_author_cpp':['proj_classes/apc_class.cpp','validity_checkers/StateValidityCheckerPCS.cpp',
            'validity_checkers/collisionDetection.cpp','planners/RRT_PCS.cpp'],
        'query_calls':0,'solve_calls':0,'new_VI_candidate_constructions':0,
        'scientific_execution_authorized':False,
        'one_shot':'Fresh atomic claim/stage/ledger; no retry/reset/resume, failed prefix retained.'}
def science_draft():
    previous,wall,used_cpu=prior();points=[load(ROOT/p) for p in ENDPOINTS]
    for point in points:
        if point['status']!='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED' or not point['source_policy_collision_qualified']:
            raise ValueError('A01_ENDPOINT_NOT_SOURCE_POLICY_QUALIFIED')
    low=[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]*2
    high=[2.88,1.919,1.22,2.79,2.09,3.1416]*2
    if any(not all(a<=v<=b for a,v,b in zip(low,p['selected_q_rad'],high)) for p in points):
        raise ValueError('A01_ENDPOINT_OUTSIDE_ORIGINAL_MAIN_SAMPLER_BOX')
    build_ready=(BUILD/'manifest.json').exists() and load(BUILD/'manifest.json').get('status')=='BUILT_NOT_QUERIED'
    return {'schema':'P4_R2_ABB_RRT_PCS_E2E_QUALIFICATION_DRAFT_V1','frozen':False,
        'execution_readiness':'WAIT_BUILD_AND_ROOT_PATH_AUDIT_RUNNER_AND_FREEZE',
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False,'prior_ledger_confirmed':False},
        'run_id':'20261015_R2_ABB_RRT_PCS_E2E01','claim_id':'P4_R2_ABB_RRT_PCS_E2E_SEED7_30W_60CPU_20261015',
        'classification':'RECONSTRUCTED_ENDPOINTS_AND_R2_NUMERICS / ORIGINAL_RRT_PCS / OBSERVED_IO',
        'request':{'environment':'II','seed':7,'range_rad':2.6,'goal_bias':.05,'solve_seconds':10.,
            'start_q12':points[0]['selected_q_rad'],'goal_q12':points[1]['selected_q_rad'],
            'bounds_low_rad':low,'bounds_high_rad':high},
        'sampler_box_and_validity_callback':'Original plan_PCS.cpp bounds including q6+-3.1416 and always-true callback. Independent audit enforces full original mechanical limits.',
        'endpoint_sources_sha256':{p:sha(ROOT/p) for p in ENDPOINTS},
        'endpoint_branch_policy':'Each A01 endpoint retains its own original arm2 branch (start3, goal0); do not claim the endpoints share one branch.',
        'binary':str(BINARY),'binary_sha256':sha(BINARY) if build_ready else 'MUST_BUILD_BEFORE_FREEZE',
        'build_manifest':str(BUILD/'manifest.json'),
        'build_manifest_sha256':sha(BUILD/'manifest.json') if build_ready else 'MUST_BUILD_BEFORE_FREEZE',
        'own_source_sha256':{p:sha(ROOT/p) for p in OWN},
        'prior_execution_sha256':previous,'previous_r2_wall_s':wall,'previous_r2_cpu_s':used_cpu,
        'budget':{'solve_execution_wall_s':30.,'solve_execution_cpu_s':60.,'independent_path_audit_wall_s':120.,
            'independent_path_audit_cpu_s':240.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'seeds':'Call ompl::RNG::setSeed(7) and srand(7) before OMPL objects; no rerun seed.',
        'run_directory_policy':'Fresh directory with simulator mesh assets; driver creates absent paths/ empty. Never copy author paths/.',
        'output_contract':{'result.json':['status','planner_status','planner_status_code','exact','approximate','has_solution',
            'environment','seed','start_q12','goal_q12','milestones_q12','reconstruction_attempts','solve_calls','solve_wall_s','planner_data'],
            'reconstruction_attempt_fields':['qa12','qb12','active_chain','branch','returned','path_q12'],
            'planner_data':'vertices[{index,q12,start,goal}], edges[[parent,child]], num_vertices, num_edges',
            'reconstruction_attempts.jsonl':'Every state-level reconstruct return, full round-trip binary64 (max_digits10=17). False attempts retained.',
            'identify_observations.jsonl':'Every original vector identify return: q12,input_ik,returned_ik. No extra IK/FK; final result identify_observation_count.'},
        'independent_path_audit':'Root-owned, not yet implemented/frozen by this draft. Exact source solution AND complete reconstruction AND independent node/edge closure/branch/bounds/aligned collision gates required. No smoothing/truncation/IK repair.',
        'formal_table_I_calls':0,'new_VI_candidate_constructions':0,'no_retry':True,
        'limitations':['Observation adds I/O cost, not a paper performance sample.',
            'Original main rounded sampler bounds and q6+-3.1416 retained; physical full mechanical limits checked independently.',
            'Source exact can coexist with reconstruct false; preserve and refuse final qualification.',
            'Discrete source-policy collision only, not complete geometry or CCD.']}
def body_span(source,signature):
    if source.count(signature)!=1:raise ValueError('BODY_SIGNATURE_CARDINALITY')
    mask=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:' '*len(m.group()),source,flags=re.S)
    begin=mask.index('{',source.index(signature));at=begin+1;depth=1
    while depth:depth+=(mask[at]=='{')-(mask[at]=='}');at+=1
    return begin,at-1
def instrument(stage):
    changes=[];p=stage/'validity_checkers/StateValidityCheckerPCS.cpp';s=p.read_text();a,b=body_span(s,SIG);body=s[a+1:b]
    inserted='\n const bool p4_return=[&]() -> bool {'+body+'}();\n p4e2e::observe_reconstruction(s1,s2,active_chain,ik_sol,Confs,p4_return);\n return p4_return;\n'
    if inserted.count(body)!=1:raise ValueError('ORIGINAL_RECON_BODY_NOT_RETAINED_ONCE')
    before=sha(p);s=s[:a+1]+inserted+s[b:];a,b=body_span(s,IDENTIFY_SIG);identify_body=s[a+1:b]
    identify_insert='\n const State p4_input_ik=ik;\n State p4_return=[&]() -> State {'+identify_body+'}();\n p4e2e::observe_identify(q1,q2,p4_input_ik,p4_return);\n return p4_return;\n'
    if identify_insert.count(identify_body)!=1:raise ValueError('ORIGINAL_IDENTIFY_BODY_NOT_RETAINED_ONCE')
    p.write_text(s[:a+1]+identify_insert+s[b:]);changes.append({'file':str(p.relative_to(stage)),'before':before,'after':sha(p),
        'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'identify_body_sha256':hashlib.sha256(identify_body.encode()).hexdigest(),'kind':'POST_RETURN_RECON_AND_IDENTIFY_OBSERVATION'})
    p=stage/'planners/RRT_PCS.cpp';s=p.read_text();needle='std::remove("./paths/temp.txt");'
    if s.count(needle)!=1:raise ValueError('TEMP_REMOVE_CARDINALITY')
    before=sha(p);p.write_text(s.replace(needle,'/* P4 I/O observation: retain ./paths/temp.txt verbatim. */'))
    changes.append({'file':str(p.relative_to(stage)),'before':before,'after':sha(p),'kind':'RETAIN_TEMP_IO_DEVIATION'})
    return changes
def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    if set(spec)!=set(expected) or any(spec[k]!=v for k,v in expected.items() if k not in ('frozen','reviews')):
        raise ValueError('EXACT_CURRENT_RECIPE_REQUIRED')
    if type(spec['frozen']) is not bool or set(spec['reviews'])!=set(expected['reviews']) or any(type(v) is not bool for v in spec['reviews'].values()):
        raise ValueError('INVALID_REVIEW_FIELDS')
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
def live_group_cpu(pgid):
    total=0.
    for stat in Path('/proc').glob('[0-9]*/stat'):
        try:
            f=stat.read_text().rsplit(')',1)[1].split()
            if int(f[2])==pgid:total+=sum(int(f[i]) for i in (11,12,13,14))/os.sysconf('SC_CLK_TCK')
        except (OSError,ValueError,IndexError):pass
    return total
def build(spec,protocol):
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN
    if BUILD.exists() or folder.exists():raise FileExistsError('FRESH_STAGE_AND_LEDGER_REQUIRED')
    wall_cap=min(45.,3600.-spec['previous_r2_wall_s']);cpu_cap=min(90.,7200.-spec['previous_r2_cpu_s'])
    if min(wall_cap,cpu_cap)<=0:raise ValueError('R2_BUDGET_EXHAUSTED')
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    new_json(claim,{'schema':'P4_R2_ABB_RRT_PCS_E2E_ENGINEERING_CLAIM_V1','claim_id':CLAIM,'created_at_utc':utc(),
        'source_commit':commit,'protocol':str(protocol),'protocol_sha256':sha(protocol),'budget':spec['budget'],
        'own_source_sha256':spec['own_source_sha256'],'no_retry_reset_or_resume':True})
    BUILD.mkdir();folder.mkdir();begun=time.monotonic();used_cpu=cpu();proc=None
    previous_handler=signal.getsignal(signal.SIGALRM)
    def alarm(*_):raise TimeoutError('BUILD_WALL_CAP')
    record={'schema':'P4_R2_ABB_RRT_PCS_E2E_ENGINEERING_EXECUTION_V1','run_id':RUN,'classification':'ENGINEERING_BUILD_ONLY',
        'source_commit':commit,'protocol':str(protocol),'protocol_sha256':sha(protocol),'claim':str(claim.relative_to(ROOT)),
        'claim_sha256':sha(claim),'own_source_sha256':spec['own_source_sha256'],'author_commit':spec['author_commit'],
        'prior_execution_sha256':spec['prior_execution_sha256'],'previous_r2_wall_s':spec['previous_r2_wall_s'],
        'previous_r2_cpu_s':spec['previous_r2_cpu_s'],'query_calls':0,'solve_calls':0,'formal_table_I_calls':0,
        'new_VI_candidate_constructions':0,'started_at_utc':utc(),'status':'STOP_PREFIX_RETAINED'}
    error=None
    try:
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,wall_cap)
        shutil.copytree(TEMPLATE,STAGE,ignore=shutil.ignore_patterns('.git','paths','p4_abb_pcs_thin','compile.stdout','compile.stderr'))
        changes=instrument(STAGE)
        sources=[STAGE/p for p in spec['linked_author_cpp']]
        cmd=['g++','-std=c++17','-O2','-Wall','-Wextra','-pthread','-I/opt/ros/humble/include/ompl-1.7','-I/usr/include/eigen3',
            '-I'+str(PQP/'include'),'-I'+str(STAGE/'proj_classes'),'-I'+str(STAGE/'validity_checkers'),'-I'+str(STAGE/'planners'),
            '-I'+str((ROOT/HEADER).parent),'-include',str(ROOT/HEADER),str(ROOT/DRIVER),*[str(p) for p in sources],
            str(PQP/'lib/libPQP.a'),'-L/opt/ros/humble/lib/x86_64-linux-gnu','-Wl,-rpath,/opt/ros/humble/lib/x86_64-linux-gnu',
            '-lompl','-lboost_filesystem','-lboost_system','-lboost_serialization','-lboost_program_options','-o',str(BINARY)]
        record.update(command=cmd,changes=changes,template_assets_sha256=spec['template_assets_sha256'])
        headers=sorted(p for p in STAGE.rglob('*') if p.is_file() and p.suffix in ('.h','.hpp'))
        record['compiled_source_sha256']={str(p.relative_to(STAGE)):sha(p) for p in [*sources,*headers]}
        record['mesh_sha256']={str(p.relative_to(STAGE)):sha(p) for p in sorted((STAGE/'simulator').glob('*.tris'))}
        if time.monotonic()-begun>=wall_cap or cpu()-used_cpu>=cpu_cap:raise TimeoutError('BUILD_PREPARATION_CAP')
        with (BUILD/'compile.stdout').open('x') as out,(BUILD/'compile.stderr').open('x') as err:
            def limits():resource.setrlimit(resource.RLIMIT_CPU,(90,90))
            proc=subprocess.Popen(cmd,stdout=out,stderr=err,cwd=ROOT,preexec_fn=limits,start_new_session=True)
            while proc.poll() is None:
                if time.monotonic()-begun>=wall_cap or cpu()-used_cpu+live_group_cpu(proc.pid)>=cpu_cap:
                    raise TimeoutError('BUILD_WALL_OR_AGGREGATE_LIVE_CPU_CAP')
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
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--describe-science-draft',action='store_true')
    group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    if args.describe_science_draft:print(json.dumps(science_draft(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_DRAFT_VALIDATED_ZERO_QUERY_ZERO_COMPILE');return
    build(spec,protocol)
if __name__=='__main__':main()
