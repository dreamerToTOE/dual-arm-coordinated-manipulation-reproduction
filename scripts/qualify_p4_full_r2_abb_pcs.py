#!/usr/bin/env python3
"""DRAFT fixed ABB PCS local-interface qualification; never call planner solve.

Describe/validate only bind saved arrays and files. A frozen committed protocol,
successful four-target build and fresh one-shot claim are required to execute.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

THREAD_ENV_BEFORE={k:os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS',
    'MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}
for _key in THREAD_ENV_BEFORE:os.environ[_key]='1'
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import qualify_p4_full_r2_vi_rss_reconstructed as common
import build_p4_full_r2_abb_pcs as builder

SCHEMA='P4_R2_ABB_PCS_FIXED_LOCAL_QUALIFICATION_V1'
RUN='20261015_R2_ABB_PCS_LOCAL01'
CLAIM='P4_R2_ABB_PCS_LOCAL_120W_240CPU_20261015'
PRE='reports/P4_FULL_R2_ORDINARY_PCS_NR_INTEGRATION_PRE_DRAFT_20261015.md'
BUILD='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1/manifest.json'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
SOURCES=[str(Path(__file__).resolve().relative_to(ROOT)),PRE,
    'scripts/build_p4_full_r2_abb_pcs.py','scripts/qualify_p4_full_r2_vi_rss_reconstructed.py',
    'scripts/recover_p4_full_r2_endpoints.py',
    'baselines/p4_full/geometry_consistent/abb_pcs_qualification_driver.cpp',
    'baselines/p4_full/geometry_consistent/pcs_source_trace.hpp',
    'baselines/p4_full/geometry_consistent/spatial_ik_patch.py',
    'baselines/p4_full/geometry_consistent/collision_adapter.py',
    'baselines/p4_full/geometry_consistent/physical_nr.py',
    'baselines/p4_full/abb_independent_oracle.py',
    'baselines/p4_full/analyze_comau_native_qualification.py',
    'baselines/p4_full/geometry_consistent/rss_geometry.py']
GATES={'closure_position_mm':1e-5,'closure_rotation_maxabs':1e-5,
    'native_FK_position_mm':1e-7,'native_FK_rotation_maxabs':1e-10,
    'branch_zero_relative_epsilon':64*sys.float_info.epsilon,'source_RBS_tol_rad':.05}
CAPS={'top_project':320,'top_rbs':64,'top_reconstruct':64,
    'trace_fixed_project':4256,'trace_project_output_checks':4256,
    'independent_math_arm_FK':8536,'collision_adapter_calls':4260,
    'adapter_internal_arm_FK_J':17040,'adapter_PQP_queries':988320,
    'trace_native_FK':57344,'trace_PQP_queries':524288}

def path(value):
    p=Path(value);return p if p.is_absolute() else ROOT/p
def load(value):return json.loads(path(value).read_text())
def prior_paths():
    return sorted(str(p.relative_to(ROOT)) for p in (ROOT/'results/p4_full').glob(
        '20261015_R2_*/execution.json') if p.parent.name!=RUN)
def endpoint_files():
    return [f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/{e}_{k}.json'
        for e in ('II','III') for k in (0,1)]
def fixed_inputs():
    # This is array transcription/arithmetic, not a new model evaluation.
    center=[];roots=[];locals_=[];negative=[]
    upper0=165*3.1416/180
    for source in endpoint_files():
        old=load(source);q=old['selected_q_rad'];env=old['environment'];key=env+'_'+old['endpoint']
        if (old['status']!='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'
                or old['source_policy_collision_qualified'] is not True or len(q)!=12
                or not all(math.isfinite(v) for v in q)):
            raise common.StopQualification('SAVED_ENDPOINT_NOT_QUALIFIED_'+key)
        center.append({'center_id':key,'environment':env,'q12':q,'source':source})
        negative.append({'case_id':key+'_raw_closure_fail','environment':env,
            'q12':old['original_endpoint']['q_rad'],'expected':'CLOSURE_FAIL'})
        invalid=list(q);invalid[0]=upper0+.01
        negative.append({'case_id':key+'_q0_bound_fail','environment':env,
            'q12':invalid,'expected':'BOUND_FAIL'})
        for role in (0,1):
            for branch in range(8):
                roots.append({'case_id':f'{key}_a{role}_b{branch}','center_id':key,
                    'environment':env,'op':'project','q12':q,'active_chain':role,'branch':branch})
            coordinate=6*role;margin=upper0-abs(q[coordinate]);h=min(.08,margin/4)
            if h<=0:raise common.StopQualification('NO_FIXED_PERTURBATION_MARGIN')
            for sign in (-1,1):
                perturbed=list(q);perturbed[coordinate]+=sign*h
                locals_.append({'case_id':f'{key}_a{role}_s{sign:+d}','center_id':key,
                    'environment':env,'op':'project','q12':perturbed,'active_chain':role,
                    'coordinate':coordinate,'sign':sign,'h_rad':h})
    return {'centers':center,'root_requests':roots,'local_templates':locals_,'negative_nodes':negative}

def build_assets():
    if not path(BUILD).exists():return {'build_status':'MUST_BUILD_BEFORE_FREEZE','files':{}}
    manifest=load(BUILD)
    files={BUILD:common.sha(BUILD)}
    ready=manifest.get('status')=='BUILT_NOT_EXECUTED_OR_QUALIFIED'
    expected_targets={(v,m) for v in ('author_native','geometry_consistent') for m in ('plain','trace')}
    if ready:
        if (manifest.get('schema')!='P4_R2_ABB_PCS_ENGINEERING_BUILD_V1'
                or len(manifest.get('entries',[]))!=4
                or {(e.get('variant'),e.get('mode')) for e in manifest['entries']}!=expected_targets
                or set(manifest.get('own_source_sha256',{}))!=set(builder.OWN)
                or manifest.get('query_calls')!=0 or manifest.get('solve_calls')!=0):
            raise common.StopQualification('BUILD_MANIFEST_TARGETS_OR_SOURCE_SET_INVALID')
        commit=manifest.get('source_commit','')
        subprocess.run(['git','cat-file','-e',commit+'^{commit}'],cwd=ROOT,check=True,
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for name,expected in manifest['own_source_sha256'].items():
            blob=subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)
            if common.sha(path(name))!=expected or hashlib.sha256(blob).hexdigest()!=expected:
                raise common.StopQualification('BUILD_CURRENT_OR_COMMITTED_OWN_SOURCE_MISMATCH_'+name)
        claim_path='results/p4_full/'+builder.ID+'.claim.json'
        ledger_path='results/p4_full/'+builder.RUN+'/execution.json'
        claim,ledger=load(claim_path),load(ledger_path)
        recipe_path=manifest.get('protocol');recipe=load(recipe_path)
        recipe_relative=str(path(recipe_path).resolve().relative_to(ROOT))
        recipe_blob=subprocess.check_output(['git','show',commit+':'+recipe_relative],cwd=ROOT)
        if hashlib.sha256(recipe_blob).hexdigest()!=manifest.get('protocol_sha256'):
            raise common.StopQualification('BUILD_RECIPE_COMMIT_BLOB_MISMATCH')
        if (manifest.get('claim')!=claim_path or manifest.get('engineering_execution')!=ledger_path
                or manifest.get('claim_sha256')!=common.sha(path(claim_path))
                or manifest.get('protocol_sha256')!=common.sha(path(recipe_path))
                or recipe.get('schema')!='P4_R2_ABB_PCS_ENGINEERING_RECIPE_V1'
                or recipe.get('frozen') is not True or recipe.get('claim_id')!=builder.ID
                or recipe.get('targets')!=[[v,m] for v in ('author_native','geometry_consistent') for m in ('plain','trace')]
                or claim.get('schema')!='P4_R2_ABB_PCS_ENGINEERING_CLAIM_V1'
                or claim.get('claim_id')!=builder.ID or claim.get('budget')!=recipe.get('budget')
                or ledger.get('schema')!='P4_R2_ABB_PCS_ENGINEERING_EXECUTION_V1'
                or ledger.get('status')!=manifest['status'] or ledger.get('external_manifest')!=BUILD
                or ledger.get('manifest_sha256')!=common.sha(BUILD)
                or ledger.get('claim')!=claim_path or ledger.get('claim_sha256')!=common.sha(path(claim_path))
                or ledger.get('wall_s')!=manifest.get('engineering_build_wall_s')
                or ledger.get('cpu_s')!=manifest.get('engineering_build_cpu_s')
                or ledger.get('prior_execution_sha256')!=recipe.get('prior_execution_sha256')
                or ledger.get('previous_wall_s')!=recipe.get('previous_r2_wall_s')
                or ledger.get('previous_cpu_s')!=recipe.get('previous_r2_cpu_s')):
            raise common.StopQualification('BUILD_MANIFEST_CLAIM_RECIPE_EXECUTION_LINK_INVALID')
        for record in (claim,ledger):
            if any(record.get(k)!=manifest.get(k) for k in ('protocol','protocol_sha256',
                    'source_commit','author_commit','own_source_sha256','query_calls','solve_calls')):
                raise common.StopQualification('BUILD_PROVENANCE_RECORD_MISMATCH')
        if (recipe.get('own_source_sha256')!=manifest['own_source_sha256']
                or recipe.get('author_commit')!=manifest['author_commit']):
            raise common.StopQualification('BUILD_RECIPE_SOURCE_MISMATCH')
        files.update({name:common.sha(path(name)) for name in (claim_path,ledger_path,recipe_path)})
    for entry in manifest.get('entries',[]):
        if ready and (entry.get('exit_code')!=0 or not entry.get('binary_sha256')
                or not entry.get('source_sha256') or not entry.get('mesh_sha256')
                or entry.get('stage_root')!=str(Path(BUILD).parent/(entry['variant']+'_'+entry['mode']))
                or entry.get('binary')!=str(Path(entry['stage_root'])/'p4_abb_pcs_thin')):
            raise common.StopQualification('BUILD_ENTRY_NOT_SUCCESSFUL_OR_FIXED_STAGE_CHANGED')
        for key,values in (('source_sha256',entry.get('source_sha256',{})),
                ('mesh_sha256',entry.get('mesh_sha256',{}))):
            for name,value in values.items():
                filename=str(Path(entry['stage_root'])/name)
                if common.sha(filename)!=value:raise common.StopQualification('BUILD_ASSET_CHANGED_'+filename)
                files[filename]=value
        if entry.get('binary_sha256'):
            filename=entry['binary']
            if common.sha(filename)!=entry['binary_sha256']:raise common.StopQualification('BUILD_BINARY_CHANGED')
            files[filename]=entry['binary_sha256']
    return {'build_status':manifest.get('status'),'source_commit':manifest.get('source_commit'),
        'files':files}

def draft_protocol():
    prior=prior_paths();ledgers=[load(p) for p in prior]
    files=SOURCES+endpoint_files()+prior+['configs/p4_full/author_source_manifest.json',COLLISION]
    assets=build_assets()
    return {'schema':SCHEMA,'frozen':False,'run_id':RUN,'claim_id':CLAIM,
        'classification':'SOURCE_NATIVE_RETURN_VS_VERSIONED_R2_NUMERICS / FIXED_LOCAL_INTERFACE_ONLY',
        'budget':{'wall_s':120.,'cpu_s':240.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.},
        'prior_executions':prior,'previous_r2_wall_s':math.fsum(float(x['wall_s']) for x in ledgers),
        'previous_r2_cpu_s':math.fsum(float(x['cpu_s']) for x in ledgers),
        'bound_files_sha256':{p:common.sha(path(p)) for p in files},
        'build_manifest':BUILD,'build_assets':assets,'collision_manifest':COLLISION,
        'fixed_inputs':fixed_inputs(),'gates':GATES,'caps':CAPS,
        'root_selection':'For each exact saved center/role, geometry_consistent trace accepted roots: independent closure, original bounds, unique passive geometry branch identical to saved center. Nearest full12 Euclidean distance, branch ascending tie; no collision filtering or center replacement.',
        'downstream_policy':'Same selected branch for both numerical variants. Each local endpoint must independently pass closure/branch/bounds/aligned discrete collision before its source RBS. Source true permits reconstruct; source false retained. No branch/h replacement. Path node reuse requires exact q and previously qualified call record.',
        'trace_equivalence':'Compare logical original returned/q12/path_q12/status/request/environment only; trace instrumentation/count/native observations excluded. Exact parsed-number equality. Trace first, then plain, same process-isolated request.',
        'failure_policy':'Corrected success with wrong closure/nativeFK/active-coordinate/branch is soundness stop. Source-native unsound success retained and excluded from downstream. Bound/collision is ordinary rejection. Cap/runtime/unknown/source-equivalence mismatch stops, saves prefix/unexecuted fixed templates; no retry.',
        'scope':'No random sampler, planner allocation/solve, RSS, new formal statistics, collision-positive control rerun or VI B charge. Existing source mesh pairs/8mm tolerance/ABB collinear rod policy; no full physical geometry/CCD certificate.',
        'plain_accounting':'Internal plain calls are unobserved; logical requests and child CPU/wall measured, no fabricated inner counts. Trace counters exclude constructor; all post-top-level native FK observations counted.',
        'deduplication':'No dedup of captured successful projection events; every event gets2 math FK+1 adapter(4 internal armFK/J,2 source variant queries). Path only reuses exact previously checked nodes; no hidden new FK. Four centers get same gates once;8 negatives get math only.',
        'source_files':SOURCES,'solve_calls':0,'rng_calls':0,'VI_B_budget_charged':False}

def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    if {**spec,'frozen':False}!=expected or type(spec.get('frozen')) is not bool:
        raise common.StopQualification('PROTOCOL_SOURCE_LEDGER_OR_FIXED_INPUT_CHANGED')
    if execute:
        if spec['frozen'] is not True or spec['build_assets']['build_status']!='BUILT_NOT_EXECUTED_OR_QUALIFIED':
            raise common.StopQualification('FROZEN_PROTOCOL_AND_SUCCESSFUL_BUILD_REQUIRED')
        if 'results/p4_full/'+builder.RUN+'/execution.json' not in spec['prior_executions']:
            raise common.StopQualification('ENGINEERING_BUILD_NOT_CHARGED_TO_R2_LEDGER')
        for name in SOURCES+[str(protocol.relative_to(ROOT))]:
            subprocess.run(['git','ls-files','--error-unmatch',name],cwd=ROOT,check=True,
                stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if subprocess.check_output(['git','status','--porcelain','--',name],cwd=ROOT,text=True):
                raise common.StopQualification('SOURCE_OR_CONFIG_UNCOMMITTED_'+name)

def collision_worker(protocol):
    spec=load(protocol);request=json.loads(sys.stdin.read())
    claim=load('results/p4_full/'+CLAIM+'.claim.json')
    if (not spec.get('frozen') or claim['parent_pid']!=os.getppid()
            or claim['protocol_sha256']!=common.sha(protocol)):
        raise common.StopQualification('LIVE_ONE_SHOT_PARENT_REQUIRED')
    for name in SOURCES:
        if common.sha(path(name))!=spec['bound_files_sha256'][name]:
            raise common.StopQualification('WORKER_SOURCE_CHANGED')
    from baselines.p4_full.geometry_consistent import physical_nr
    from baselines.p4_full.geometry_consistent.collision_adapter import check_collision,close_sessions
    original=physical_nr.arm_fk_jac;counts={'started':0,'completed':0}
    def counted(q,env,arm):
        if counts['started']>=4:raise common.StopQualification('ADAPTER_INTERNAL_FK_CAP')
        counts['started']+=1
        print(json.dumps({'event':'adapter_arm_FK_J_started','call':counts['started'],
            'environment':env,'arm':arm,'q6':list(map(float,q))}),file=sys.stderr,flush=True)
        result=original(q,env,arm);counts['completed']+=1
        print(json.dumps({'event':'adapter_arm_FK_J_completed','call':counts['completed']}),
            file=sys.stderr,flush=True)
        return result
    physical_nr.arm_fk_jac=counted
    try:answer=check_collision(request['environment'],request['q12'],
        timeout_s=request['timeout_s'],manifest_path=spec['collision_manifest'])
    finally:physical_nr.arm_fk_jac=original;close_sessions()
    print(json.dumps({'collision':answer,'internal_arm_FK_J':counts},allow_nan=False),flush=True)

class Qualification:
    def __init__(self,spec,protocol,folder,budget):
        self.spec,self.protocol,self.folder,self.budget=spec,protocol,folder,budget
        self.evidence=common.Evidence(folder,budget);self.counts=Counter();self.results=[];self.local_outcomes=[]
        self.entries={(e['variant'],e['mode']):e for e in load(BUILD)['entries']}
    def count(self,key,n=1):
        if self.counts[key]+n>CAPS.get(key,float('inf')):
            raise common.StopQualification('AGGREGATE_CALL_CAP_'+key)
        self.counts[key]+=n
    def math_node(self,q,env,branch=None,role=0,native=None,active_input=None):
        import numpy as np
        import recover_p4_full_r2_endpoints as oracle
        self.budget.remaining()
        if len(q)!=12 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in q):
            raise common.StopQualification('NONFINITE_SOURCE_OUTPUT')
        self.count('independent_math_arm_FK',2)
        self.evidence.event('independent_math_FK_started',environment=env,q12=q,arms=[1,2])
        poses=[oracle.arm_fk(q[6*i:6*i+6],env,i+1) for i in range(2)]
        residual=oracle.matrix_error(poses[1],poses[0]@oracle.grasps_for(env)[0]@oracle.FLIP)
        limits=oracle.limit_score(q,env)
        identity=oracle.branch_identity(q[6*(1-role):6*(2-role)],env,GATES['branch_zero_relative_epsilon'])
        fk_errors=[] if native is None else [oracle.matrix_error(native[i],poses[i]) for i in range(2)]
        fk_ok=all(x['position_max_abs']<=GATES['native_FK_position_mm']
            and x['rotation_matrix_max_abs']<=GATES['native_FK_rotation_maxabs'] for x in fk_errors)
        active_ok=(active_input is None or q[6*role:6*role+6]==active_input[6*role:6*role+6])
        branch_ok=branch is None or branch in identity['branch_set']
        closed=residual['position_max_abs']<=GATES['closure_position_mm'] and residual['rotation_matrix_max_abs']<=GATES['closure_rotation_maxabs']
        row={'q12':q,'environment':env,'closure':residual,'closure_pass':closed,
            'limits':limits,'passive_branch_identity':identity,'branch_pass':branch_ok,
            'native_FK_errors':fk_errors,'native_FK_pass':fk_ok,'active_coordinates_unchanged':active_ok,
            'math_sound':closed and fk_ok and active_ok and branch_ok,
            'node_math_qualified':closed and fk_ok and active_ok and branch_ok and limits['legal']}
        self.evidence.event('independent_math_FK_completed',result=row)
        return row
    def collision(self,q,env,label):
        self.count('collision_adapter_calls');self.counts['adapter_internal_arm_FK_J_requested']+=4
        self.evidence.event('collision_started',environment=env,q12=q,label=label)
        raw=self.evidence.process([sys.executable,str(Path(__file__).resolve()),'--collision-worker',str(self.protocol)],
            json.dumps({'environment':env,'q12':q,'timeout_s':min(10.,self.budget.remaining())})+'\n',label)
        answer=json.loads(raw);r=answer['collision']
        self.count('adapter_internal_arm_FK_J',answer['internal_arm_FK_J']['started'])
        self.counts['adapter_internal_arm_FK_J_completed']+=answer['internal_arm_FK_J']['completed']
        if (answer['internal_arm_FK_J']!={'started':4,'completed':4} or r.get('status')!='CHECKED'
                or type(r.get('collision')) is not bool or r.get('selected_variant')!='aligned'
                or r.get('manifest_sha256')!=self.spec['bound_files_sha256'][COLLISION]
                or list(r.get('variants',{}))!=['native','aligned']):
            raise common.StopQualification('COLLISION_OR_INTERNAL_ACCOUNTING_INVALID')
        for variant,row in r['variants'].items():
            codes=row.get('query_codes',[]);self.count('adapter_PQP_queries',len(codes))
            if (not codes or any(type(c) is not int or c!=0 for c in codes)
                    or row.get('native_result') not in (0,1)):
                raise common.StopQualification('PQP_NATIVE_QUERY_ERROR_'+variant)
        if r['variants']['aligned']['pose_consistency'].get('passed') is not True:
            raise common.StopQualification('ALIGNED_COLLISION_TCP_MISMATCH')
        self.evidence.event('collision_completed',label=label,answer=answer)
        return r
    def trace_events(self,stem,answer):
        logfile=self.folder/(stem+'.stderr.txt');events=[];entered=Counter();completed=Counter()
        for line in logfile.read_text().splitlines():
            if line.startswith('P4_PCS_TRACE '):
                row=json.loads(line.split(' ',1)[1]);events.append(row)
                if row['event']=='entered':entered[row['kind']]+=1
                if row['event']=='completed':
                    completed[row['kind']]+=1
                    if row['kind']=='pqp' and row['result']['code']!=0:
                        raise common.StopQualification('SOURCE_INTERNAL_PQP_ERROR')
        if entered!=completed or dict(entered)!=answer['observed_counts']:
            raise common.StopQualification('TRACE_BOUNDARY_ACCOUNTING_MISMATCH')
        self.count('trace_fixed_project',entered['project_fixed'])
        self.count('trace_native_FK',entered['native_fk']);self.count('trace_PQP_queries',entered['pqp'])
        self.counts.update({'trace_'+k+'_completed':v for k,v in completed.items()})
        return events
    def source_pair(self,variant,env,request,label):
        op=request['op'];answers={};events=[]
        for mode in ('trace','plain'):
            self.count('top_'+op);entry=self.entries[(variant,mode)]
            process_number=self.evidence.process_number+1
            raw=self.evidence.process([entry['binary'],env,entry['stage_root'],mode],
                json.dumps(request)+'\n',label+'_'+variant+'_'+mode)
            answer=json.loads(raw)
            if answer.get('status')!='SOURCE_CALL_COMPLETED' or answer.get('request')!=request:
                raise common.StopQualification('SOURCE_CALL_NOT_COMPLETED')
            if answer.get('solve_calls')!=0 or answer.get('rng_calls')!=0:
                raise common.StopQualification('UNEXPECTED_SOLVE_OR_RNG')
            if mode=='trace':
                events=self.trace_events(f'{process_number:05d}_{label}_{variant}_{mode}',answer)
            answers[mode]=answer
        logical=lambda a:{k:a[k] for k in ('environment','request','status','returned','q12','path_q12') if k in a}
        if logical(answers['plain'])!=logical(answers['trace']):
            raise common.StopQualification('PLAIN_TRACE_ORIGINAL_RETURN_MISMATCH')
        trace=answers['trace'];checked=[]
        def finite_tree(value):
            if isinstance(value,list):return all(finite_tree(v) for v in value)
            return isinstance(value,(int,float)) and math.isfinite(value)
        for field in ('q12','path_q12'):
            if field in trace and not finite_tree(trace[field]):
                raise common.StopQualification('NONFINITE_SOURCE_RETURN_'+field)
        projection_events=[e for e in events if e['event']=='completed' and e['kind']=='project_fixed' and e['result']['returned']]
        if len(projection_events)!=len(trace['native_checks']):
            raise common.StopQualification('MISSING_INTERNAL_PROJECT_OUTPUT')
        starts={e['id']:e for e in events if e['event']=='entered'}
        for index,(event,observed) in enumerate(zip(projection_events,trace['native_checks'])):
            self.count('trace_project_output_checks');args=starts[event['id']]['args']
            output=event['result']['q1']+event['result']['q2']
            if observed['q12']!=output:raise common.StopQualification('NATIVE_OBSERVATION_Q_CHANGED')
            row=self.math_node(output,env,request['branch'],request['active_chain'],
                observed['poses'],args['q1']+args['q2'])
            # Source-native defects remain explicit evidence; corrected soundness
            # failure blocks this slice, rather than silently rejecting bad output.
            if variant=='geometry_consistent' and not row['math_sound']:
                self.evidence.event('corrected_soundness_failure',result=row)
                raise common.StopQualification('CORRECTED_PROJECT_SOUNDNESS_FAILURE')
            if observed['source_limits_legal']!=row['limits']['legal']:
                raise common.StopQualification('SOURCE_INDEPENDENT_BOUND_SEMANTICS_MISMATCH')
            row['collision']=self.collision(output,env,f'{label}_{variant}_node{index:03d}')
            row['node_qualified']=row['node_math_qualified'] and not row['collision']['collision']
            checked.append(row)
        result={'label':label,'variant':variant,'request':request,'original_return':trace,
            'plain_trace_logical_equivalent':True,'checked_projection_events':checked,
            'plain_internal_counts':'UNOBSERVED','source_call_completed':True}
        common.new_json(self.folder/(label+'_'+variant+'.json'),result)
        self.results.append(result);self.evidence.event('source_pair_qualified',result=result)
        return result
    def execute_schedule(self):
        import recover_p4_full_r2_endpoints as oracle
        fixed=self.spec['fixed_inputs'];centers={};roots={};selected={};local_results=self.local_outcomes
        for center in fixed['centers']:
            row=self.math_node(center['q12'],center['environment'])
            row['collision']=self.collision(center['q12'],center['environment'],center['center_id']+'_center')
            if not row['node_math_qualified'] or row['collision']['collision']:
                raise common.StopQualification('SAVED_CENTER_REQUALIFICATION_FAILED')
            centers[center['center_id']]=center
        for negative in fixed['negative_nodes']:
            row=self.math_node(negative['q12'],negative['environment'])
            passed=(not row['closure_pass'] if negative['expected']=='CLOSURE_FAIL' else not row['limits']['legal'])
            self.evidence.event('negative_control',fixture=negative,result=row,expected_rejection_observed=passed)
            if not passed:raise common.StopQualification('NEGATIVE_CONTROL_DID_NOT_REJECT')
        for fixture in fixed['root_requests']:
            request={k:fixture[k] for k in ('op','q12','active_chain','branch')}
            for variant in ('author_native','geometry_consistent'):
                result=self.source_pair(variant,fixture['environment'],request,fixture['case_id'])
                roots[(fixture['center_id'],fixture['active_chain'],fixture['branch'],variant)]=result
        for center in fixed['centers']:
            for role in (0,1):
                identity=oracle.branch_identity(center['q12'][6*(1-role):6*(2-role)],center['environment'],GATES['branch_zero_relative_epsilon'])
                eligible=[]
                for branch in range(8):
                    result=roots[(center['center_id'],role,branch,'geometry_consistent')]
                    nodes=result['checked_projection_events']
                    # Collision is deliberately not part of root identity selection.
                    if (result['original_return']['returned'] and len(nodes)==1
                            and nodes[0]['node_math_qualified'] and identity['unique']
                            and nodes[0]['passive_branch_identity']['unique']
                            and nodes[0]['passive_branch_identity']['branch_set']==identity['branch_set']):
                        distance=math.sqrt(math.fsum((a-b)**2 for a,b in zip(nodes[0]['q12'],center['q12'])))
                        eligible.append((distance,branch))
                selected[(center['center_id'],role)]=min(eligible)[1] if eligible else None
                self.evidence.event('fixed_branch_selected',center_id=center['center_id'],role=role,
                    eligible_distance_branch=eligible,selected_branch=selected[(center['center_id'],role)])
        for template in fixed['local_templates']:
            branch=selected[(template['center_id'],template['active_chain'])]
            if branch is None:
                self.evidence.event('local_not_executed_no_qualified_branch',fixture=template);continue
            request={k:template[k] for k in ('op','q12','active_chain')};request['branch']=branch
            center=centers[template['center_id']];qa=center['q12']
            for variant in ('author_native','geometry_consistent'):
                result=self.source_pair(variant,template['environment'],request,template['case_id']+'_project')
                nodes=result['checked_projection_events']
                outcome={'case_id':template['case_id'],'variant':variant,'branch':branch,'qualified_nonvacuous_RBS_and_path':False}
                local_results.append(outcome)
                if not result['original_return']['returned'] or len(nodes)!=1 or not nodes[0]['node_qualified']:
                    outcome['status']='LOCAL_ENDPOINT_REJECTED';continue
                qb=nodes[0]['q12'];distance=math.sqrt(math.fsum((a-b)**2 for a,b in zip(qa,qb)))
                edge={'op':'rbs','qa12':qa,'qb12':qb,'active_chain':request['active_chain'],'branch':branch}
                rbs=self.source_pair(variant,template['environment'],edge,template['case_id']+'_rbs')
                outcome.update(full12_distance_rad=distance,source_rbs_return=rbs['original_return']['returned'])
                if not rbs['original_return']['returned']:
                    outcome['status']='SOURCE_RBS_FALSE';continue
                edge['op']='reconstruct'
                recon=self.source_pair(variant,template['environment'],edge,template['case_id']+'_reconstruct')
                path_q=recon['original_return'].get('path_q12',[])
                known={tuple(qa):True,tuple(qb):nodes[0]['node_qualified']}
                for node in recon['checked_projection_events']:known[tuple(node['q12'])]=node['node_qualified']
                path_ok=(bool(recon['original_return']['returned']) and len(path_q)>=2 and path_q[0]==qa
                    and path_q[-1]==qb and all(known.get(tuple(q)) is True for q in path_q)
                    and all(math.sqrt(math.fsum((a-b)**2 for a,b in zip(x,y)))<.05 for x,y in zip(path_q,path_q[1:])))
                all_midpoints=all(n['node_qualified'] for n in rbs['checked_projection_events'])
                nonvacuous=distance>=.05 and bool(rbs['checked_projection_events']) and bool(recon['checked_projection_events'])
                outcome.update(source_reconstruct_return=recon['original_return']['returned'],
                    reconstructed_path_qualified=path_ok,all_rbs_midpoints_qualified=all_midpoints,
                    nonvacuous_source_recursion=nonvacuous,
                    qualified_nonvacuous_RBS_and_path=path_ok and all_midpoints and nonvacuous,
                    status='QUALIFIED_NONVACUOUS_LOCAL_EDGE' if path_ok and all_midpoints and nonvacuous else 'PARTIAL_OR_VACUOUS_OR_REJECTED')
                self.evidence.event('local_edge_finished',result=outcome)
        self.evidence.event('local_schedule_finished',outcomes=local_results)
        return local_results

def execute(spec,protocol):
    folder=ROOT/'results/p4_full'/RUN
    if folder.exists():raise common.StopQualification('OUTPUT_EXISTS_NO_OVERWRITE')
    common.new_json(ROOT/'results/p4_full'/(CLAIM+'.claim.json'),{'parent_pid':os.getpid(),
        'claim_id':CLAIM,'protocol_sha256':common.sha(protocol),'budget':spec['budget'],
        'created_at_utc':common.utc(),'no_retry':True})
    folder.mkdir();budget=common.RunBudget(spec,spec['previous_r2_wall_s'],spec['previous_r2_cpu_s'])
    q=Qualification(spec,protocol,folder,budget);error=None;outcomes=[]
    record={'schema':SCHEMA,'run_id':RUN,'classification':spec['classification'],
        'protocol_sha256':common.sha(protocol),'bound_files_sha256':spec['bound_files_sha256'],
        'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'solve_calls':0,'rng_calls':0,'formal_planning_pass':False,'VI_B_budget_charged':False,
        'previous_wall_s':spec['previous_r2_wall_s'],'previous_cpu_s':spec['previous_r2_cpu_s']}
    try:
        q.evidence.event('run_started',protocol=spec,thread_env_before=THREAD_ENV_BEFORE)
        outcomes=q.execute_schedule()
        corrected=[r for r in outcomes if r['variant']=='geometry_consistent']
        positive=(len(corrected)==16 and all(r['qualified_nonvacuous_RBS_and_path'] for r in corrected))
        record['status']='FIXED_LOCAL_ABB_PCS_QUALIFIED' if positive else 'FIXED_LOCAL_ABB_PCS_PARTIAL'
    except BaseException as exc:
        error=exc;record.update(status='STOP_PREFIX_RETAINED',termination_reason=repr(exc))
        q.evidence.event('run_stopped',reason=repr(exc))
    finally:
        budget.close()
        after={p:common.sha(path(p)) for p in spec['bound_files_sha256']}
        build_after={p:common.sha(path(p)) if path(p).is_file() else 'MISSING'
            for p in spec['build_assets']['files']}
        if after!=spec['bound_files_sha256'] or build_after!=spec['build_assets']['files']:
            record.update(status='STOP_BOUND_ASSET_CHANGED');error=error or common.StopQualification('BOUND_ASSET_CHANGED')
        record.update(wall_s=time.monotonic()-budget.started,cpu_s=budget.cpu()-budget.cpu_start,
            counts=dict(q.counts),outcomes=q.local_outcomes,bound_files_after_sha256=after,
            build_files_after_sha256=build_after,
            completed_source_pair_labels=[r['label']+'_'+r['variant'] for r in q.results],
            uncompleted_source_pair_labels=[label for label in (
                [f['case_id']+'_'+v for f in spec['fixed_inputs']['root_requests'] for v in ('author_native','geometry_consistent')]
                +[f['case_id']+'_'+op+'_'+v for f in spec['fixed_inputs']['local_templates']
                  for op in ('project','rbs','reconstruct') for v in ('author_native','geometry_consistent')])
                if label not in {r['label']+'_'+r['variant'] for r in q.results}],
            partial_accounting='Completed counters only include completed process answers. Raw trace/worker start/completion events in interrupted stderr retain partial counts; no guessed full cap. Requested adapter FK distinct from measured started/completed. Plain internal counts unobserved.',
            ended_at_utc=common.utc())
        record['cumulative_execution_wall_s']=spec['previous_r2_wall_s']+record['wall_s']
        record['cumulative_execution_cpu_s']=spec['previous_r2_cpu_s']+record['cpu_s']
        common.new_json(folder/'execution.json',record);q.evidence.events.close()
    print(json.dumps({'status':record['status'],'counts':dict(q.counts),'wall_s':record['wall_s'],'cpu_s':record['cpu_s']}))
    if error is not None:raise error

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--describe-protocol',action='store_true');g.add_argument('--validate-draft',type=Path)
    g.add_argument('--protocol',type=Path);g.add_argument('--collision-worker',type=Path,help=argparse.SUPPRESS)
    a=p.parse_args()
    if a.collision_worker:collision_worker(a.collision_worker.resolve());return
    if a.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(a.validate_draft or a.protocol).resolve();spec=load(protocol)
    validate(spec,protocol,bool(a.protocol))
    if a.validate_draft:
        print(json.dumps({'status':'STATIC_DRAFT_VALIDATED','scientific_calls':0,'caps':CAPS}));return
    execute(spec,protocol)
if __name__=='__main__':main()
