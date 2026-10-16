#!/usr/bin/env python3
"""H draft: two R2-only control-flow targets, runtime plain/trace.

Describe/validate are saved-source bookkeeping only. Build requires a clean
committed exact frozen recipe and never launches a helper or planner query.
No native-numerics rerun and no CBiRRT distance factor are available.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from baselines.p4_full.geometry_consistent.abb_helper_instrumentation_draft import (
    APC,COL,SVC,FACTORS,instrument_sources,
)
TEMPLATE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1/geometry_consistent_plain')
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_random_helper_h_v1')
PQP=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3')
COMPILER='/usr/bin/x86_64-linux-gnu-g++-11'
RUN='20261015_R2_ABB_RANDOM_HELPER_H_BUILD01'
CLAIM='P4_R2_ABB_RANDOM_HELPER_H_BUILD_2_60W_120CPU_20261015'
SCIENCE_RUN='20261015_R2_ABB_RANDOM_HELPER_H01'
PRE='reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_PRE_DRAFT_20261015.md'
HEADER='baselines/p4_full/geometry_consistent/abb_helper_observation_draft.hpp'
DRIVER='baselines/p4_full/geometry_consistent/abb_helper_driver_draft.cpp'
REUSE='scripts/build_p4_full_r2_abb_rrt_pcs_e2e.py'
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),HEADER,DRIVER,PRE,REUSE,
     'baselines/p4_full/geometry_consistent/abb_helper_instrumentation_draft.py',
     'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py']
ENDPOINTS=[f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/{env}_{i}.json'
           for env in ('II','III') for i in (0,1)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def utc():return dt.datetime.now(dt.timezone.utc).isoformat()
def new_json(p,v):
    with Path(p).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cpu():
    a=resource.getrusage(resource.RUSAGE_SELF);b=resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime
def prior():
    paths=sorted(p for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json') if p.parent.name!=RUN)
    rows=[load(p) for p in paths]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths},math.fsum(x['wall_s'] for x in rows),math.fsum(x['cpu_s'] for x in rows)
def template_assets():
    # This exact reusable dependency reader imports only stdlib, no model code.
    spec=importlib.util.spec_from_file_location('p4_h_saved_template_reader',ROOT/REUSE)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    assets=m.template_assets()
    for p in [Path(COMPILER),Path('/usr/include/c++/11/bits/stl_algo.h')]:assets[str(p)]=sha(p)
    return assets
def previews():
    inputs={p:(TEMPLATE/p).read_bytes() for p in (APC,SVC,COL)}
    return {factor:instrument_sources(inputs,factor)[1] for factor in FACTORS}
def draft_protocol():
    previous,wall,used_cpu=prior()
    return {'schema':'P4_R2_ABB_RANDOM_HELPER_H_ENGINEERING_DRAFT_V1','frozen':False,
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False},
        'run_id':RUN,'claim_id':CLAIM,'author_commit':'909bd72fff778aca8682c96f9eb86ae4eb75557b',
        'classification':'ENGINEERING_BUILD_ONLY','template_stage':str(TEMPLATE),'build_root':str(BUILD),
        'template_assets_sha256':template_assets(),'own_source_sha256':{p:sha(ROOT/p) for p in OWN},
        'source_transform_previews':previews(),
        'targets':[{'factor':f,'stage':str(BUILD/f),'binary':str(BUILD/f/'p4_abb_random_helper_h')}
                   for f in FACTORS],
        'linked_author_cpp':[APC,SVC,COL],'runtime_observation_modes':['plain','trace'],
        'prior_execution_sha256':previous,'previous_r2_wall_s':wall,'previous_r2_cpu_s':used_cpu,
        'budget':{'wall_s':60.,'cpu_s':120.,'single_wall_s':45.,'single_cpu_s':90.,
                  'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'query_calls':0,'solve_calls':0,'formal_table_I_calls':0,'new_VI_candidate_constructions':0,
        'scientific_execution_authorized':False,
        'source_policy':'Only already-qualified R2 numerical base. H success-break versus original complete control flow; original shuffle/IK/identify/limits and collision-free helper contract. Observer no caps/model/RNG. D absent.',
        'one_shot':'Fresh exclusive claim/stages/ledger; preserve partial build/logs; no retry/reset/resume.'}
def science_draft():
    previous,wall,used_cpu=prior();contexts=[]
    for relative in ENDPOINTS:
        point=load(ROOT/relative)
        if point['status']!='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED' or not point['source_policy_collision_qualified']:
            raise ValueError('QUALIFIED_A01_SAVED_CENTER_REQUIRED')
        env=Path(relative).stem.rsplit('_',1)[0];endpoint=int(Path(relative).stem.rsplit('_',1)[1])
        for active in (0,1):
            for seed in (7,17):
                contexts.append({'case_id':f'{env}_{endpoint}_role{active}_seed{seed}',
                    'operation':'random_three_argument_helper','environment':env,'endpoint_source':relative,
                    'q12':point['selected_q_rad'],'active_chain':active,'seed':seed})
    if len(contexts)!=16:raise ValueError('FIXED16_REQUIRED')
    ready=(BUILD/'manifest.json').is_file() and load(BUILD/'manifest.json').get('status')=='BUILT_NOT_QUERIED'
    return {'schema':'P4_R2_ABB_RANDOM_HELPER_H_QUALIFICATION_DRAFT_V1','frozen':False,
        'execution_readiness':'WAIT_BUILD_ROOT_RUNNER_INDEPENDENT_REVIEW_AND_FREEZE',
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False,'prior_ledger_confirmed':False},
        'run_id':SCIENCE_RUN,'claim_id':'P4_R2_ABB_RANDOM_HELPER_H_FIXED64_60W_120CPU_20261015',
        'classification':'RECONSTRUCTED_A01_CENTERS / R2_NUMERICS / ORIGINAL_3ARG_HELPER_VS_H_BREAK / NONFORMAL',
        'fixed_contexts':contexts,'schedule':[[f,mode,c['case_id']] for f in FACTORS for mode in ('plain','trace') for c in contexts],
        'max_helper_dispatches':64,'max_final_independent_metric_checks':64,'max_final_aligned_collision_worker_dispatches':64,
        'endpoint_sources_sha256':{p:sha(ROOT/p) for p in ENDPOINTS},
        'own_source_sha256':{p:sha(ROOT/p) for p in OWN},
        'build_manifest':str(BUILD/'manifest.json'),'build_manifest_sha256':sha(BUILD/'manifest.json') if ready else 'MUST_BUILD_BEFORE_FREEZE',
        'binaries_sha256':{f:sha(BUILD/f/'p4_abb_random_helper_h') for f in FACTORS} if ready else 'MUST_BUILD_BEFORE_FREEZE',
        'prior_execution_sha256':previous,'previous_r2_wall_s':wall,'previous_r2_cpu_s':used_cpu,
        'budget':{'wall_s':60.,'cpu_s':120.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'comparison_gates':{'plain_trace_non_observation_exact_equality':True,'common_prefix_exact_equality':True,
            'source_control_normal_return_false':True,'break_stops_at_first_both_identified':True,
            'active_q_exactly_unchanged':True,'no_identified_success_both_false_same_final_q':True,
            'physical_translation_max_abs_mm':1e-5,'physical_rotation_matrix_max_abs':1e-5,
            'source_original_joint_bounds_required':True,'source_branch_and_independent_geometric_identity_separate':True,
            'aligned_v3_source_policy_discrete_collision_required':True},
        'source_structural_maxima_not_observed_counts':{'helper_dispatches':64,'direct_analytic_ik':512,
            'identify_analytic_ik':8192,'total_analytic_ik':8704,'source_arm_FK':1536,
            'external_math_arm_FK':128,'external_collision_adapter_calls':64,'external_collision_workers':128,
            'external_collision_adapter_arm_FK_J':256,
            'shuffle_calls':64,'libstdcxx11_structural_rand_draws':448},
        'rng_policy':'srand(original request seed) immediately before each actual source 3arg call. Preserve std::random_shuffle. Observe order after existing call; no extra rand/model. Actual rand starts/completions UNOBSERVED, never promote structural448 to observation.',
        'observation_policy':'Both binaries contain same enabled flag observations; plain/trace selected at runtime. Complete original bodies retained, whole-file reversed in memory. External watchdog only; trace emits entries/completions and in-helper branch candidate/identify results. No extra source final FK/IK/limits/collision.',
        'final_gate_policy':'Independently audit all64 returned final q including source false outputs. Source bool, physical closure/bounds, independent branch identity and aligned collision are separate fields; no all64-qualified expectation or seed replacement. Preserve all source intermediate candidates; they are not independently qualified by this final-only gate.',
        'root_runner_status':'SCIENCE_RUNNER_DRAFT_IMPLEMENTED_NOT_INDEPENDENTLY_REVIEWED_OR_FROZEN',
        'science_runner':'scripts/qualify_p4_full_r2_abb_random_helper_h_draft.py',
        'formal_table_I_calls':0,'new_VI_candidate_constructions':0,'no_retry_reset_or_resume':True,
        'limitations':['Fixed local interface only; no ambient distribution/PCS advantage/fair-speed/planner claim.',
            'Native-numerics helper execution remains unverified; old native IK failures/source retained, no repeated native numerical run.',
            'H is absent from the original three planners real grow path; original qualified RRT path remains unchanged.',
            'CBiRRT activeDistance D is a separate factor and future stage.',
            '211 full obligations and formal0/22500 remain; no P2/Isaac.']}
def validate(spec,path,execute=False):
    expected=draft_protocol()
    if set(spec)!=set(expected) or any(spec[k]!=v for k,v in expected.items() if k not in ('frozen','reviews')):
        raise ValueError('EXACT_CURRENT_H_RECIPE_REQUIRED')
    if type(spec['frozen']) is not bool or set(spec['reviews'])!=set(expected['reviews']) or any(type(v) is not bool for v in spec['reviews'].values()):
        raise ValueError('EXPLICIT_BOOLEAN_REVIEW_FIELDS_REQUIRED')
    if execute:
        if not spec['frozen'] or not all(spec['reviews'].values()):raise ValueError('ROOT_REVIEW_FREEZE_REQUIRED')
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        for name in [*OWN,str(path.relative_to(ROOT))]:
            subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
            if subprocess.check_output(['git','status','--porcelain','--',name],cwd=ROOT,text=True):raise ValueError('UNCOMMITTED '+name)
        for name,wanted in spec['own_source_sha256'].items():
            b=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)
            if hashlib.sha256(b).hexdigest()!=wanted:raise ValueError('COMMIT_BLOB_MISMATCH '+name)
        return commit
def live_group_cpu(pgid):
    total=0.
    for p in Path('/proc').glob('[0-9]*/stat'):
        try:
            f=p.read_text().rsplit(')',1)[1].split()
            if int(f[2])==pgid:total+=sum(int(f[i]) for i in (11,12,13,14))/os.sysconf('SC_CLK_TCK')
        except (OSError,ValueError,IndexError):pass
    return total
def build(spec,path):
    commit=validate(spec,path,True);folder=ROOT/'results/p4_full'/RUN
    if BUILD.exists() or folder.exists():raise FileExistsError('FRESH_H_BUILD_AND_LEDGER_REQUIRED')
    wall_cap=min(60.,3600.-spec['previous_r2_wall_s']);cpu_cap=min(120.,7200.-spec['previous_r2_cpu_s'])
    if min(wall_cap,cpu_cap)<=0:raise ValueError('R2_CAP_EXHAUSTED')
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    new_json(claim,{'schema':'P4_R2_ABB_RANDOM_HELPER_H_BUILD_CLAIM_DRAFT_V1','claim_id':CLAIM,
        'created_at_utc':utc(),'source_commit':commit,'protocol':str(path),'protocol_sha256':sha(path),
        'budget':spec['budget'],'own_source_sha256':spec['own_source_sha256'],'no_retry_reset_or_resume':True})
    BUILD.mkdir();folder.mkdir();begun=time.monotonic();used_cpu=cpu();proc=None;error=None
    record={'schema':'P4_R2_ABB_RANDOM_HELPER_H_ENGINEERING_EXECUTION_DRAFT_V1','run_id':RUN,
        'classification':'ENGINEERING_BUILD_ONLY','source_commit':commit,'protocol':str(path),
        'protocol_sha256':sha(path),'claim':str(claim.relative_to(ROOT)),'claim_sha256':sha(claim),
        'own_source_sha256':spec['own_source_sha256'],'template_assets_sha256':spec['template_assets_sha256'],
        'source_transform_previews':spec['source_transform_previews'],'prior_execution_sha256':spec['prior_execution_sha256'],
        'previous_r2_wall_s':spec['previous_r2_wall_s'],'previous_r2_cpu_s':spec['previous_r2_cpu_s'],
        'query_calls':0,'solve_calls':0,'formal_table_I_calls':0,'new_VI_candidate_constructions':0,
        'started_at_utc':utc(),'status':'STOP_PREFIX_RETAINED','entries':[]}
    old_handler=signal.getsignal(signal.SIGALRM)
    def alarm(*_):raise TimeoutError('H_AGGREGATE_WALL_CAP')
    try:
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,wall_cap)
        for target in spec['targets']:
            started=time.monotonic();target_cpu=cpu();stage=Path(target['stage']);factor=target['factor'];proc=None
            entry={'factor':factor,'stage':str(stage),'started_at_utc':utc(),'status':'STOP_PREFIX_RETAINED'}
            record['entries'].append(entry)
            try:
                shutil.copytree(TEMPLATE,stage,ignore=shutil.ignore_patterns('.git','paths','p4_abb_pcs_thin','compile.stdout','compile.stderr'))
                transformed,manifest=instrument_sources({p:(stage/p).read_bytes() for p in (APC,SVC,COL)},factor)
                if manifest!=spec['source_transform_previews'][factor]:raise ValueError('STAGED_TRANSFORM_PREVIEW_MISMATCH')
                for relative,b in transformed.items():(stage/relative).write_bytes(b)
                sources=[stage/p for p in spec['linked_author_cpp']]
                headers=sorted(p for p in stage.rglob('*') if p.is_file() and p.suffix in ('.h','.hpp'))
                entry['compiled_source_sha256']={str(p.relative_to(stage)):sha(p) for p in [*sources,*headers]}
                entry['mesh_sha256']={str(p.relative_to(stage)):sha(p) for p in sorted((stage/'simulator').glob('*.tris'))}
                cmd=[COMPILER,'-std=c++17','-O2','-Wall','-Wextra','-pthread','-I/opt/ros/humble/include/ompl-1.7',
                    '-I/usr/include/eigen3','-I'+str(PQP/'include'),'-I'+str(stage/'proj_classes'),
                    '-I'+str(stage/'validity_checkers'),'-I'+str((ROOT/HEADER).parent),'-include',str(ROOT/HEADER),
                    str(ROOT/DRIVER),*[str(p) for p in sources],str(PQP/'lib/libPQP.a'),
                    '-L/opt/ros/humble/lib/x86_64-linux-gnu','-Wl,-rpath,/opt/ros/humble/lib/x86_64-linux-gnu',
                    '-lompl','-lboost_filesystem','-lboost_system','-lboost_serialization','-lboost_program_options','-o',target['binary']]
                entry['command']=cmd
                if (time.monotonic()-begun>=wall_cap or cpu()-used_cpu>=cpu_cap
                    or time.monotonic()-started>=45. or cpu()-target_cpu>=90.):
                    raise TimeoutError('H_PREPARATION_CAP_BEFORE_COMPILER')
                with (stage/'compile.stdout').open('x') as out,(stage/'compile.stderr').open('x') as err:
                    def limits():resource.setrlimit(resource.RLIMIT_CPU,(90,90))
                    proc=subprocess.Popen(cmd,cwd=ROOT,stdout=out,stderr=err,preexec_fn=limits,start_new_session=True)
                    while proc.poll() is None:
                        live=live_group_cpu(proc.pid)
                        if (time.monotonic()-begun>=wall_cap or cpu()-used_cpu+live>=cpu_cap
                            or time.monotonic()-started>=45. or cpu()-target_cpu+live>=90.):
                            raise TimeoutError('H_TARGET_OR_AGGREGATE_WALL_CPU_CAP')
                        try:proc.wait(timeout=.02)
                        except subprocess.TimeoutExpired:pass
                entry['exit_code']=proc.returncode
                if proc.returncode:raise RuntimeError('H_BUILD_FAILED')
                entry.update(status='BUILT_NOT_QUERIED',binary=target['binary'],binary_sha256=sha(target['binary']))
            except BaseException as exc:
                if proc is not None and proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                if proc is not None:entry['exit_code']=proc.returncode
                entry['termination_reason']=repr(exc);raise
            finally:
                entry.update(ended_at_utc=utc(),wall_s=time.monotonic()-started,cpu_s=cpu()-target_cpu)
        record['status']='BUILT_NOT_QUERIED'
    except BaseException as exc:
        error=exc;record['termination_reason']=repr(exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old_handler)
        record['template_assets_after_sha256']={p:sha(p) for p in spec['template_assets_sha256']}
        if record['template_assets_after_sha256']!=spec['template_assets_sha256']:
            record['status']='STOP_OLD_ASSET_CHANGED';error=error or RuntimeError('OLD_ASSET_CHANGED')
        record.update(ended_at_utc=utc(),wall_s=time.monotonic()-begun,cpu_s=cpu()-used_cpu)
        # Final asset verification is part of this engineering execution. A
        # successfully linked binary remains preserved but does not establish
        # a qualified in-budget build when this mandatory tail crosses a cap.
        if record['wall_s']>=wall_cap or record['cpu_s']>=cpu_cap:
            record['final_budget_exceeded']={'wall_cap_s':wall_cap,'cpu_cap_s':cpu_cap,
                'wall_s':record['wall_s'],'cpu_s':record['cpu_s']}
            if record['status']=='BUILT_NOT_QUERIED':
                record['status']='STOP_FINAL_BUDGET_EXCEEDED'
            error=error or TimeoutError('H_FINAL_EVIDENCE_WALL_CPU_CAP')
        new_json(BUILD/'manifest.json',{**record,'engineering_execution':str((folder/'execution.json').relative_to(ROOT))})
        new_json(folder/'execution.json',{**record,'external_manifest':str(BUILD/'manifest.json'),'manifest_sha256':sha(BUILD/'manifest.json')})
    print(json.dumps({'status':record['status'],'targets_completed':sum(x['status']=='BUILT_NOT_QUERIED' for x in record['entries']),
                      'wall_s':record['wall_s'],'cpu_s':record['cpu_s'],'query_calls':0,'solve_calls':0}))
    if error is not None:raise error
def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--describe-protocol',action='store_true');g.add_argument('--describe-science-draft',action='store_true')
    g.add_argument('--validate-draft',type=Path);g.add_argument('--protocol',type=Path);a=p.parse_args()
    if a.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    if a.describe_science_draft:print(json.dumps(science_draft(),ensure_ascii=False,indent=2));return
    path=(a.validate_draft or a.protocol).resolve();spec=load(path)
    if a.validate_draft:validate(spec,path);print('STATIC_H_DRAFT_VALIDATED_ZERO_QUERY_ZERO_COMPILE');return
    build(spec,path)
if __name__=='__main__':main()
