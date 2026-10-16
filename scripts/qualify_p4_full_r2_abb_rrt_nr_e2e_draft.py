#!/usr/bin/env python3
"""One-shot original ABB RRT_NR pilot DRAFT, no retries and no formal statistics.

Describe/validate only read files and saved scalars. A successful bound build,
committed exact frozen protocol and new atomic claim are mandatory to execute.
This runner never projects, repairs, smooths or independently qualifies a path.
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
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_p4_full_r2_abb_rrt_nr_e2e_draft as builder

SCHEMA='P4_R2_ABB_RRT_NR_E2E_QUALIFICATION_V1'
RUN='20261015_R2_ABB_RRT_NR_E2E01'
CLAIM='P4_R2_ABB_RRT_NR_E2E_SEED7_30W_60CPU_20261015'
OWN=[str(Path(__file__).resolve().relative_to(ROOT)),*builder.OWN]
BUILD=builder.BUILD/'manifest.json'

def path(value):
    p=Path(value);return p if p.is_absolute() else ROOT/p
def all_prior():
    files=sorted(p for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json') if p.parent.name!=RUN)
    rows=[builder.load(p) for p in files]
    return {str(p.relative_to(ROOT)):builder.sha(p) for p in files},math.fsum(r['wall_s'] for r in rows),math.fsum(r['cpu_s'] for r in rows)
def build_assets():
    if not BUILD.exists():return {'status':'MUST_BUILD_BEFORE_FREEZE','files':{}}
    saved=builder.load(BUILD)
    if saved.get('schema')!='P4_R2_ABB_RRT_NR_E2E_ENGINEERING_EXECUTION_V1' or saved.get('status')!='BUILT_NOT_QUERIED' or saved.get('exit_code')!=0:
        raise ValueError('SUCCESSFUL_EXACT_ENGINEERING_BUILD_REQUIRED')
    if saved.get('author_commit')!='909bd72fff778aca8682c96f9eb86ae4eb75557b' or saved.get('query_calls')!=0 or saved.get('solve_calls')!=0:
        raise ValueError('BUILD_SCOPE_CHANGED')
    files={str(BUILD):builder.sha(BUILD)}
    for name,wanted in saved['own_source_sha256'].items():
        p=ROOT/name
        blob=subprocess.check_output(['git','show',saved['source_commit']+':'+name],cwd=ROOT)
        if builder.sha(p)!=wanted or hashlib.sha256(blob).hexdigest()!=wanted:raise ValueError('BUILD_OWN_COMMIT_MISMATCH '+name)
        files[str(p)]=wanted
    for field in ('compiled_source_sha256','mesh_sha256'):
        for name,wanted in saved[field].items():
            p=builder.STAGE/name
            if builder.sha(p)!=wanted:raise ValueError('BUILT_ASSET_CHANGED '+str(p))
            files[str(p)]=wanted
    for name,wanted in saved['template_assets_sha256'].items():
        if builder.sha(name)!=wanted:raise ValueError('TEMPLATE_PROVENANCE_CHANGED '+name)
        files[name]=wanted
    for field,hashfield in [('protocol','protocol_sha256'),('claim','claim_sha256'),('binary','binary_sha256')]:
        p=path(saved[field])
        if builder.sha(p)!=saved[hashfield]:raise ValueError('BUILD_LINK_HASH_MISMATCH '+field)
        files[str(p)]=saved[hashfield]
    execution=path(saved['engineering_execution']);e=builder.load(execution)
    if e.get('manifest_sha256')!=builder.sha(BUILD) or path(e.get('external_manifest',''))!=BUILD or e.get('source_commit')!=saved['source_commit']:
        raise ValueError('ENGINEERING_EXECUTION_MANIFEST_LINK')
    files[str(execution)]=builder.sha(execution)
    return {'status':'BUILT_NOT_QUERIED','source_commit':saved['source_commit'],'files':files,
        'binary':str(builder.BINARY),'binary_sha256':saved['binary_sha256']}
def draft_protocol():
    prior,wall,cpu=all_prior();assets=build_assets();gate=builder.local_gate()
    endpoint_paths=[f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_{i}.json'for i in(0,1)]
    points=[builder.load(ROOT/p)for p in endpoint_paths]
    for p in points:
        if p['status']!='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED' or not p['source_policy_collision_qualified']:
            raise ValueError('A01_ENDPOINT_REQUIRED')
    low=[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]*2
    high=[2.88,1.919,1.22,2.79,2.09,3.1416]*2
    if any(not all(a<=x<=b for a,x,b in zip(low,p['selected_q_rad'],high))for p in points):
        raise ValueError('ENDPOINT_OUTSIDE_ORIGINAL_MAIN_SAMPLER_BOUNDS')
    request={'environment':'II','seed':7,'range_rad':2.6,'goal_bias':.05,'solve_seconds':10.,
        'start_q12':points[0]['selected_q_rad'],'goal_q12':points[1]['selected_q_rad'],
        'bounds_low_rad':low,'bounds_high_rad':high}
    return {'schema':SCHEMA,'frozen':False,'run_id':RUN,'claim_id':CLAIM,
        'execution_readiness':'WAIT_SUCCESSFUL_BUILD_LOCAL_SAVED_POST_INDEPENDENT_STATIC_REVIEW_ROOT_FREEZE',
        'reviews':{'independent_static_review_passed':False,'root_freeze_approved':False,
            'prior_execution_ledger_confirmed':False,'II_local_saved_POST_confirmed':False},
        'classification':'RECONSTRUCTED_A01_ENDPOINTS / Q1_PHYSICAL_FULL_NR_CPP / ORIGINAL_RRT_NR / OBSERVED_IO',
        'environment':'II','seed':7,'request':request,'local_gate':gate,
        'endpoint_sources_sha256':{p:builder.sha(ROOT/p)for p in endpoint_paths},
        'sampler_box_and_validity_callback':'Original plan_NR.cpp full12 bounds, q6+-3.1416, resolution0.1 and always-true validity callback; independent physical limits distinct.',
        'build_assets':assets,'own_source_sha256':{p:builder.sha(ROOT/p)for p in OWN},
        'prior_execution_sha256':prior,'previous_r2_wall_s':wall,'previous_r2_cpu_s':cpu,
        'budget':{'wall_s':30.,'cpu_s':60.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'subsequent_independent_path_audit':{'wall_s':120.,'cpu_s':240.,'max_unique_dense_nodes':2048,
            'max_mathematical_arm_FK_J':4096,'max_collision_adapter_calls':2048,'max_adapter_internal_FK_J':8192,
            'scope':'Separate claim/protocol/execution and complete preserved queue; UNKNOWN on cap; no IK/NR/projection/repair/CCD.',
            'gates':{'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,
                'mechanical_limits_low_rad':[-165*3.1416/180,-110*3.1416/180,-110*3.1416/180,-160*3.1416/180,-120*3.1416/180,-400*3.1416/180]*2,
                'mechanical_limits_high_rad':[165*3.1416/180,110*3.1416/180,70*3.1416/180,160*3.1416/180,120*3.1416/180,400*3.1416/180]*2,
                'mechanical_limits_rule':'All12 finite within original literal3.1416 limits inclusive, no extra chart or lift.',
                'fixed_active_chain_or_analytic_branch_gate':False,
                'consecutive_dense_leaf_full12_L2_strictly_below_rad':.05,
                'milestone_endpoint_rule':'Complete original milestones first=start and last=goal exact binary64; no tolerance/truncation.',
                'edge_reconstruction_rule':'Every consecutive milestone pair matches one original state-level reconstruction returnedtrue with exact qa/qb and full dense first/last; retain false attempts.',
                'collision_rule':'All distinct full path nodes/milestones/start/goal require v3 aligned CHECKED collisionfalse and zero native/aligned PQP querycodes; original native collision retained separately.',
                'dense_queue_rule':'Complete full queue must fit2048 unique-node cap and all checked before PASS; overcap retains full tail UNKNOWN, never prefix qualification.',
                'no_subsampling_smoothing_projection_repair':True,'complete_physical_geometry_or_CCD_claim':False}},
        'output_contract':{'result.json':['status','planner_status','planner_status_code','exact','approximate','has_solution',
            'environment','seed','start_q12','goal_q12','milestones_q12','reconstruction_attempts','solve_calls','solve_wall_s','planner_data'],
            'reconstruction_attempts.jsonl':'Every completed original state-level reconstruct:qa12,qb12,returned,full path_q12, exact roundtrip binary64 max_digits10=17 including falseprefix.',
            'planner_data':'Complete vertices index/q12/start/goal and edges parent/child; no fabricated/truncated path.'},
        'observation_accounting':'Completed state-level reconstruct only; unreturned Confs UNKNOWN; raw complete JSONL prefixes retained; no inferred started counts.',
        'one_shot_policy':'Fixed seed7 one solve, fresh atomic claim/output, no retry/reset/resume; exact/approx/false/timeout/error retained.',
        'formal_table_I_calls':0,'formal_table_I_required_calls':22500,'new_VI_candidate_constructions':0,
        'planning_pilot_attempt_cap':1,'full_P4_or_PCS_advantage_pass':False,'no_path_modification':True,
        'limitations':['Observed IO pilot is not a paper performance sample.','Original discrete pair/tolerance policy is not complete physical geometry or CCD.','Source Exact may coexist with reconstructfalse; refuse final path qualification.']}
def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    if set(spec)!=set(expected) or any(spec[k]!=v for k,v in expected.items() if k not in ('frozen','reviews','execution_readiness')):
        raise ValueError('EXACT_CURRENT_SCIENCE_PROTOCOL_REQUIRED')
    if type(spec['frozen']) is not bool or set(spec['reviews'])!=set(expected['reviews']) or any(type(v) is not bool for v in spec['reviews'].values()):
        raise ValueError('INVALID_REVIEW_FIELDS')
    if execute:
        if not spec['frozen'] or not all(spec['reviews'].values()) or spec['execution_readiness']!='FROZEN_REVIEWED_READY':
            raise ValueError('REVIEW_AND_ROOT_FREEZE_REQUIRED')
        if spec['build_assets']['status']!='BUILT_NOT_QUERIED' or not spec['local_gate']['ready']:raise ValueError('SUCCESSFUL_BUILD_AND_LOCAL_GATE_REQUIRED')
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        for name in [*OWN,str(protocol.relative_to(ROOT))]:
            subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if subprocess.check_output(['git','status','--porcelain','--',name],cwd=ROOT,text=True):raise ValueError('UNCOMMITTED_SOURCE_OR_PROTOCOL '+name)
        for name,wanted in spec['own_source_sha256'].items():
            blob=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)
            if hashlib.sha256(blob).hexdigest()!=wanted:raise ValueError('COMMITTED_SOURCE_MISMATCH '+name)
        return commit
def retained_jsonl(file):
    rows=[];tails=[]
    if not file.exists():return rows,tails
    for line1,line in enumerate(file.read_bytes().splitlines(keepends=True),1):
        try:rows.append(json.loads(line))
        except (ValueError,UnicodeDecodeError):
            tails.append({'line1':line1,'sha256':hashlib.sha256(line).hexdigest(),'status':'INCOMPLETE_OR_UNPARSABLE_PREFIX_TAIL'});break
    return rows,tails
def execute(spec,protocol):
    commit=validate(spec,protocol,True);folder=ROOT/'results/p4_full'/RUN
    if folder.exists():raise FileExistsError('OUTPUT_EXISTS_NO_OVERWRITE')
    wall_cap=min(spec['budget']['wall_s'],3600.-spec['previous_r2_wall_s']);cpu_cap=min(spec['budget']['cpu_s'],7200.-spec['previous_r2_cpu_s'])
    if min(wall_cap,cpu_cap)<=0:raise ValueError('R2_BUDGET_EXHAUSTED')
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json');begun=time.monotonic();cpu_start=builder.cpu()
    builder.new_json(claim,{'schema':'P4_R2_ABB_RRT_NR_E2E_CLAIM_V1','claim_id':CLAIM,'source_commit':commit,
        'protocol':str(protocol),'protocol_sha256':builder.sha(protocol),'budget':spec['budget'],
        'created_at_utc':builder.utc(),'no_retry_reset_or_resume':True})
    folder.mkdir();runtime=folder/'runtime';proc=None;error=None;old_handler=signal.getsignal(signal.SIGALRM)
    record={'schema':'P4_R2_ABB_RRT_NR_E2E_EXECUTION_V1','run_id':RUN,'status':'STOP_PREFIX_RETAINED',
        'classification':spec['classification'],'source_commit':commit,'protocol':str(protocol),'protocol_sha256':builder.sha(protocol),
        'claim':str(claim.relative_to(ROOT)),'claim_sha256':builder.sha(claim),
        'build_manifest':str(BUILD),'build_manifest_sha256':builder.sha(BUILD),
        'binary':spec['build_assets']['binary'],'binary_sha256':spec['build_assets']['binary_sha256'],
        'own_source_sha256':spec['own_source_sha256'],'build_assets_before_sha256':spec['build_assets']['files'],
        'driver_request':spec['request'],'environment':'II','seed':7,'solve_dispatched':0,'solve_calls_from_result':None,
        'formal_table_I_calls':0,'new_VI_candidate_constructions':0,'independent_path_qualified':False,
        'prior_execution_sha256':spec['prior_execution_sha256'],'previous_r2_wall_s':spec['previous_r2_wall_s'],
        'previous_r2_cpu_s':spec['previous_r2_cpu_s'],'started_at_utc':builder.utc(),'runtime':str(runtime.relative_to(ROOT))}
    def alarm(*_):raise TimeoutError('E2E_HARD_WALL_CAP')
    try:
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,max(1e-9,wall_cap-(time.monotonic()-begun)))
        runtime.mkdir()
        # Source loader expects ./simulator; copy bound mesh bytes into fresh run.
        (runtime/'simulator').mkdir()
        mesh_assets={}
        for source_name,wanted in spec['build_assets']['files'].items():
            source=Path(source_name)
            if source.parent==builder.STAGE/'simulator' and source.suffix=='.tris':
                target=runtime/'simulator'/source.name;shutil.copy2(source,target)
                if builder.sha(target)!=wanted:raise ValueError('RUNTIME_MESH_COPY_HASH '+source.name)
                mesh_assets[str(target.relative_to(ROOT))]=wanted
        if not mesh_assets:raise ValueError('NO_BOUND_RUNTIME_MESHES')
        record['runtime_mesh_sha256']=mesh_assets
        request=folder/'driver_request.json'
        with request.open('x') as stream:
            json.dump(spec['request'],stream,ensure_ascii=False,allow_nan=False,separators=(',',':'));stream.write('\n')
        command=[spec['build_assets']['binary'],str(runtime)];record['command']=command
        before_remaining=min(wall_cap-(time.monotonic()-begun),cpu_cap-(builder.cpu()-cpu_start))
        if before_remaining<=0:raise TimeoutError('E2E_SETUP_BUDGET_EXHAUSTED')
        env={**os.environ,**{k:'1' for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']}}
        with request.open() as fin,(folder/'driver.stdout').open('x') as out,(folder/'driver.stderr').open('x') as err:
            def limits():resource.setrlimit(resource.RLIMIT_CPU,(60,60))
            proc=subprocess.Popen(command,stdin=fin,stdout=out,stderr=err,cwd=ROOT,env=env,preexec_fn=limits,start_new_session=True)
            record['solve_dispatched']=1
            builder.new_json(folder/'dispatch.json',{'command':command,'child_pid':proc.pid,'dispatched_at_utc':builder.utc(),
                'internal_solve_started':'UNOBSERVED_UNTIL_DRIVER_RESULT','no_retry':True})
            while proc.poll() is None:
                if time.monotonic()-begun>=wall_cap or builder.cpu()-cpu_start+builder.live_group_cpu(proc.pid)>=cpu_cap:
                    raise TimeoutError('E2E_HARD_WALL_OR_LIVE_AGGREGATE_CPU_CAP')
                try:proc.wait(timeout=.02)
                except subprocess.TimeoutExpired:pass
        record['returncode']=proc.returncode
        result=runtime/'result.json'
        if not result.exists():raise ValueError('DRIVER_RESULT_MISSING')
        returned=builder.load(result);record['result']=str(result.relative_to(ROOT));record['result_sha256']=builder.sha(result)
        record['solve_calls_from_result']=returned.get('solve_calls')
        record['source_exact']=returned.get('exact');record['source_approximate']=returned.get('approximate')
        record['driver_status']=returned.get('status');record['source_planner_status']=returned.get('planner_status')
        if proc.returncode:raise RuntimeError('DRIVER_RETURN_NONZERO_'+str(proc.returncode))
        if returned.get('schema')!='P4_ABB_RRT_NR_END_TO_END_DRAFT_V1' or returned.get('request')!=spec['request'] or returned.get('solve_calls')!=1:
            raise ValueError('DRIVER_RESULT_INTERFACE_OR_REQUEST_CHANGED')
        record['status']='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT' if returned.get('exact') is True and returned.get('approximate') is False else 'SOURCE_NONEXACT_RETAINED'
    except BaseException as exc:
        error=exc;record['termination_reason']=repr(exc)
        if proc is not None and proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
        if proc is not None:record['returncode']=proc.returncode
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,old_handler)
        # Evidence finalization is retained even after the hard execution limit.
        try:
            result=runtime/'result.json'
            if result.exists():
                record['result']=str(result.relative_to(ROOT));record['result_sha256']=builder.sha(result)
                returned=builder.load(result)
                record['solve_calls_from_result']=returned.get('solve_calls')
                record['source_exact']=returned.get('exact');record['source_approximate']=returned.get('approximate')
            recon,recon_tail=retained_jsonl(runtime/'reconstruction_attempts.jsonl')
            record['observation_prefix']={'reconstruction_calls_completed_observed':len(recon),
                'reconstruction_true_started':'UNOBSERVED_NO_START_HOOK',
                'reconstruction_incomplete_tails':recon_tail}
            after={p:builder.sha(p) for p in spec['build_assets']['files']}
            record['build_assets_after_sha256']=after
            record['own_source_after_sha256']={p:builder.sha(ROOT/p) for p in OWN}
            record['endpoint_sources_after_sha256']={p:builder.sha(ROOT/p) for p in spec['endpoint_sources_sha256']}
            if after!=spec['build_assets']['files'] or record['own_source_after_sha256']!=spec['own_source_sha256']:
                raise ValueError('BOUND_SOURCE_OR_ASSET_CHANGED')
            if record['endpoint_sources_after_sha256']!=spec['endpoint_sources_sha256']:
                raise ValueError('BOUND_ORIGINAL_RECONSTRUCTED_ENDPOINT_CHANGED')
            record['protocol_after_sha256']=builder.sha(protocol);record['claim_after_sha256']=builder.sha(claim)
            if record['protocol_after_sha256']!=record['protocol_sha256'] or record['claim_after_sha256']!=record['claim_sha256']:
                raise ValueError('PROTOCOL_OR_CLAIM_CHANGED')
            record['retained_run_files_sha256']={str(p.relative_to(ROOT)):builder.sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}
        except BaseException as final_error:
            record['finalization_error']=repr(final_error);record['status']='STOP_EVIDENCE_FINALIZATION_FAILED'
            error=error or final_error
        record.update(ended_at_utc=builder.utc(),wall_s=time.monotonic()-begun,cpu_s=builder.cpu()-cpu_start)
        if record['wall_s']>=wall_cap or record['cpu_s']>=cpu_cap:
            record['status']='STOP_WALL_OR_CPU_BUDGET_PREFIX_RETAINED'
        record['cumulative_execution_wall_s']=spec['previous_r2_wall_s']+record['wall_s']
        record['cumulative_execution_cpu_s']=spec['previous_r2_cpu_s']+record['cpu_s']
        record['r2_remaining']={'wall_s':3600.-record['cumulative_execution_wall_s'],'cpu_s':7200.-record['cumulative_execution_cpu_s']}
        builder.new_json(folder/'execution.json',record)
    print(json.dumps({'status':record['status'],'source_exact':record.get('source_exact'),'source_approximate':record.get('source_approximate'),
        'wall_s':record['wall_s'],'cpu_s':record['cpu_s'],'independent_path_qualified':False},ensure_ascii=False))
    if error is not None:raise error
def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=builder.load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_DRAFT_VALIDATED_ZERO_SCIENCE');return
    execute(spec,protocol)
if __name__=='__main__':main()
