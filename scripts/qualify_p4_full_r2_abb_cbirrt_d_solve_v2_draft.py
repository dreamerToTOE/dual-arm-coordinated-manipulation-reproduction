#!/usr/bin/env python3
"""S02 exact setup-preamble transport correction, shared original S budget.

No protocol or process at import; original S01 source/STOP are immutable.

Reuse the reviewed TAIL journal/pipe cleanup and immutable D build readers.
Missing actual D/LOCAL02 evidence rejects describe/validate before any claim.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import time
import qualify_p4_full_r2_abb_cbirrt_d_tail02_draft as tail

old=tail.old
ROOT=old.ROOT
RUN='20261015_R2_ABB_CBIRRT_D_SOLVE02'
CLAIM='P4_R2_ABB_CBIRRT_D_SOLVE02_SHARED_REMAINDER_II_SEED7_ONCE_20261016'
LABEL='R2_NUMERICS_D_FIXED_SINGLE_ORIGINAL_CBIRRT_SOLVE'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE02_PRE_DRAFT_20261016.md'
DESIGN='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE_RUNNER_DESIGN_PRE_DRAFT_20261016.md'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py'
S01='results/p4_full/20261015_R2_ABB_CBIRRT_D_SOLVE01'
S01_EXEC_SHA='99c5cc5e980bf52489b154d5a678df903a1897a1e9e966c341ea6b5229533fdd'
PREAMBLE=b'Debug:   CBiRRT: Planner range detected to be 3.415829\n'
DIAGNOSIS='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE01_STDOUT_SOURCE_DIAGNOSIS_20261016.json'
DIAGNOSIS_SHA='cd257201d77757ee6b7fa0c6aca73859afe7813603f171c58b591e438cb4bfd7'
D_POST='reports/P4_FULL_R2_ABB_CBIRRT_D_TAIL02_SAVED_INDEPENDENT_POST_20261016.json'
D_POST_SHA='4c6d30b2e8106394235e8990de7b6738d0d587bf198a94d314d6fe49736ff2ca'
L_DIR='results/p4_full/20261015_R2_ABB_CBIRRT_D_LOCAL02'
L_POST='reports/P4_FULL_R2_ABB_CBIRRT_D_LOCAL02_SAVED_INDEPENDENT_POST_20261016.json'
ENDPOINTS=[f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_{i}.json'for i in(0,1)]
OWN=list(dict.fromkeys([str(Path(__file__).resolve().relative_to(ROOT)),PRE,DESIGN,SUPERVISOR,*tail.OWN]))
require=old.require
sha=old.sha
load=old.load
exact=old.exact


def previous_stop():
    e=load(S01+'/execution.json');c=load(S01+'.supervision.charge.json')
    require(sha(S01+'/execution.json')==S01_EXEC_SHA and e['status']=='STOP_PREFIX_RETAINED'
        and e['termination_reason']=="JSONDecodeError('Expecting value: line 1 column 1 (char 0)')"
        and e['complete_source_raw_evidence_gate']is False and e['counts']['solve_dispatched']==1,
        'EXACT_ORIGINAL_S01_TRANSPORT_STOP_REQUIRED')
    require(e['source_process_registry']==[dict(pid=78833,reaped=True,returncode=-9)]
        and e['diagnostics']==[]and old.path(S01+'/source_stdout.bin').read_bytes()==PREAMBLE,
        'ORIGINAL_S01_RAW_PREFIX_AND_KILLED_SOURCE_MUST_REMAIN')
    require(c['execution_sha256']==S01_EXEC_SHA and c['time_fields']==['1.43','0.93','0.19','1']
        and c['wall_s']==1.44 and c['cpu_s']==1.14 and c['timing_valid']is True,
        'EXACT_PREVIOUS_SHARED_COST_CHARGE_REQUIRED')
    require(sha(DIAGNOSIS)==DIAGNOSIS_SHA,'INDEPENDENT_STATIC_SOURCE_DIAGNOSIS_REQUIRED')
    files={str(p.relative_to(ROOT)):sha(p)for p in old.path(S01).rglob('*')if p.is_file()}
    for n in(e['protocol'],e['claim'],S01+'.supervision.time.txt',S01+'.supervision.jsonl',
        S01+'.supervision.stderr.log',S01+'.supervision.charge.json',DIAGNOSIS):files[n]=sha(n)
    require(sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']
        and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256']and e['bound_files_sha256']==e['bound_files_after_sha256'],
        'ORIGINAL_S01_RECIPE_OR_SOURCE_CHANGED')
    files.update(e['bound_files_sha256'])
    for n,h in files.items():require(sha(n)==h,'ORIGINAL_S01_SAVED_ASSET_CHANGED '+n)
    return dict(original_execution=S01+'/execution.json',original_execution_sha256=S01_EXEC_SHA,
        original_status='STOP_PREFIX_RETAINED',original_final_JSON_observed=0,
        original_source_solve_entered=True,original_source_solve_completed='UNOBSERVED',
        shared_original_wall_s=30.,shared_original_cpu_s=60.,consumed_upper_wall_s=1.44,
        consumed_upper_cpu_s=1.14,remaining_wall_s=28.56,remaining_cpu_s=58.86,files_sha256=files)


def prerequisites():
    for run in(tail.RUN,Path(L_DIR).name):
        prefix=ROOT/'results/p4_full'/run
        require(not Path(str(prefix)+'.supervision.charge.json').is_file()or(prefix/'execution.json').is_file(),
            'KNOWN_D_OR_L_ORPHAN_SUPERVISION_CHARGE_REQUIRES_AUTHORITATIVE_ACCOUNTING '+run)
    require(old.path(D_POST).is_file()and old.path(L_DIR+'/execution.json').is_file()and old.path(L_POST).is_file(),
        'WAIT_ACTUAL_D_SPLIT_AND_LOCAL02_INDEPENDENT_POST_NO_PLACEHOLDER_PROTOCOL')
    d=load(D_POST);de=load('results/p4_full/'+tail.RUN+'/execution.json')
    require(sha(D_POST)==D_POST_SHA and d['schema']=='P4_TAIL02_SAVED_INDEPENDENT_AGGREGATE_POST_V1'
        and d['status']=='PASS_SPLIT_SAVED_PREFIX_PLUS_MISSING_TWO_INDEPENDENT_POST'
        and d['personnel_independent']is True and d['external_supervision_qualified']is True
        and d['checks_failed']==0 and d['checks_total']==d['checks_passed']==1374
        and d['aggregate_actual_responses']==64 and d['aggregate_source_processes']==9
        and d['aggregate_plain_trace_pairs']==32 and d['original_single_run_PASS']is False,
        'EXACT_ACTUAL_D_SPLIT_COMPLETE_CONTRACT_REQUIRED')
    require(d['execution_sha256']==sha('results/p4_full/'+tail.RUN+'/execution.json')
        and de['status']==tail.LABEL and de['completed_new_dispatch_ids']==[62,63]
        and de['UNKNOWN_new_dispatch_ids']==[],'ACTUAL_D_SPLIT_EXECUTION_REQUIRED')
    le=load(L_DIR+'/execution.json');lp=load(L_POST)
    require(lp['schema']=='P4_LOCAL02_SAVED_INDEPENDENT_POST_V1'
        and lp['status']=='PASS_LOCAL02_SAVED_DISCRETE_SEAM_INDEPENDENT_POST'
        and lp['personnel_independent']is True and lp['external_supervision_qualified']is True
        and lp['checks_total']==lp['checks_passed']and lp['checks_total']>0 and lp['checks_failed']==0
        and lp['execution_sha256']==sha(L_DIR+'/execution.json')
        and le['status']=='PASS_FIXED3_LOCAL_SEAM_SAVED_DISCRETE_CERTIFICATE_REUSED',
        'ACTUAL_LOCAL02_AND_INDEPENDENT_POST_REQUIRED')
    # This exact dictionary is a draft AND contract, not a prediction of L's result.
    required=('actual12_all_true','six_plain_trace_pairs_binary64_equal',
        'complete_three_M_binary64_equal_saved80_65_34','two_SVC_zero_CBi_zero_direct_rng',
        'raw_EOF_and_all_processes_reaped_exit0','old177_complete_discrete_certificate_reused',
        'external_cost_and_identity_qualified','original_D64_STOP_and_H_STOP_preserved')
    require(set(lp.get('required_gates',{}))==set(required)
        and all(lp['required_gates'][k]is True for k in required),'EXACT_LOCAL02_FULL_AND_CONTRACT_REQUIRED')
    files={D_POST:sha(D_POST),L_POST:sha(L_POST),L_DIR+'/execution.json':sha(L_DIR+'/execution.json')}
    for e in(de,le):
        require(e['bound_files_sha256']==e['bound_files_after_sha256'],'PREREQUISITE_BOUND_SET_CHANGED')
        require(sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']
            and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'],'PREREQUISITE_RECIPE_CHANGED')
        for n in(e['protocol'],e['claim']):files[n]=sha(n)
        files.update(e['bound_files_sha256'])
    for audit in(d,lp):
        require(isinstance(audit['retained_sha256'],dict)and audit['retained_sha256'],'FULL_SAVED_AUDIT_BINDINGS_REQUIRED')
        files.update(audit['retained_sha256'])
    for n,h in files.items():require(sha(n)==h,'PREREQUISITE_ASSET_CHANGED '+n)
    return dict(distance_classification=tail.LABEL,distance_POST=D_POST,distance_POST_sha256=sha(D_POST),
        local_execution=L_DIR+'/execution.json',local_POST=L_POST,local_POST_sha256=sha(L_POST),files_sha256=files)


def current_prior():
    ledgers=list((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
    require(ledgers,'WAIT_AUTHORITATIVE_ACTUAL_CHARGE_LEDGER')
    ledger=max(ledgers,key=lambda p:int(p.stem.rsplit('V',1)[1]));saved=load(ledger)
    actual={str(p.relative_to(ROOT)):sha(p)for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if p.parent.name!=RUN}
    require({r['execution']:r['execution_sha256']for r in saved['executions']}==actual,'LATEST_LEDGER_MUST_COVER_EVERY_ACTUAL_EXECUTION')
    wall=math.fsum(r.get('charged_wall_s',r['wall_s'])for r in saved['executions'])
    cpu=math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in saved['executions'])
    require(all(math.isfinite(v)and v>=0 for v in(wall,cpu))and wall==saved['conservative_r2_sum_wall_s']
        and cpu==saved['conservative_r2_sum_cpu_s'],'AUTHORITATIVE_SINGLE_CHARGE_TOTALS_REQUIRED')
    for r in saved['executions']:
        if 'charged_wall_s'in r:
            post=load(r['external_post'])
            require(sha(r['external_post'])==r['external_post_sha256']and post['personnel_independent']is True
                and post['external_supervision_qualified']is True and post['checks_failed']==0
                and post['checks_total']==post['checks_passed']
                and post['execution_sha256']==r['execution_sha256']and post['upper_wall_s']==r['charged_wall_s']
                and post['upper_cpu_s']==r['charged_cpu_s']and sha(r['external_time'])==r['external_time_sha256']==post['external_time_sha256'],
                'PRIOR_EXTERNAL_CHARGE_NOT_INDEPENDENTLY_CERTIFIED')
    return dict(ledger=str(ledger.relative_to(ROOT)),ledger_sha256=sha(ledger),execution_sha256=actual,wall_s=wall,cpu_s=cpu,
        historical_unmeasured_tail='RETAINED_UNKNOWN; CHARGED_REMAINING_IS_UPPER_BOUND')


def endpoints():
    # Reuse the already-frozen endpoint hashes from original D's four-point evidence.
    points={r['source']:r for r in load(old.SAVED)['points']};files={};q=[]
    low=[-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416]*2
    high=[2.88,1.919,1.22,2.79,2.09,3.1416]*2
    for n in ENDPOINTS:
        e=load(n);saved=points[n]
        require(sha(n)==saved['source_sha256']and e['status']=='RECONSTRUCTED_SOURCE_POLICY_QUALIFIED'
            and e['source_policy_collision_qualified']is True and exact(e['selected_q_rad'],saved['q12']),
            'ORIGINAL_FROZEN_A01_ENDPOINT_REQUIRED')
        v=e['selected_q_rad'];require(len(v)==12 and all(math.isfinite(x)and a<=x<=b for x,a,b in zip(v,low,high)),
            'ORIGINAL_ENDPOINT_WITHIN_NATIVE_SAMPLER_BOX_REQUIRED')
        files[n]=sha(n);q.append(v)
    return dict(files_sha256=files,request=dict(environment='II',operation='solve',seed=7,range_rad=2.6,
        solve_seconds=10.,start_q12=q[0],goal_q12=q[1]),sampler_low_rad=low,sampler_high_rad=high,
        branch_policy='A01 own original passive branch start3/goal0; no wrap/lift/project or common-branch claim.')


def draft_protocol():
    ready=prerequisites();previous=previous_stop();assets=old.build_assets();ep=endpoints();prior=current_prior()
    stage=Path(assets['targets']['distance_destination_fix']['stage'])
    meshes={str(p):sha(p)for p in sorted((stage/'simulator').glob('*.tris'))}
    require(len(meshes)==20,'EXACT20_BOUND_NATIVE_MESHES_REQUIRED')
    bound={**ready['files_sha256'],**previous['files_sha256'],**assets['files_sha256'],**ep['files_sha256'],**meshes,
        prior['ledger']:prior['ledger_sha256'],**{n:sha(n)for n in OWN},
        '/usr/bin/time':sha('/usr/bin/time'),'/usr/bin/python3':sha('/usr/bin/python3')}
    return dict(schema='P4_R2_ABB_CBIRRT_D_SOLVE02_DRAFT_V2',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_freeze_approved=False,latest_actual_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,prerequisites=ready,build_assets=assets,previous_S01_stop=previous,
        stdout_contract=dict(exact_setup_preamble_base64=base64.b64encode(PREAMBLE).decode(),preamble_bytes=55,
            exact_setup_preamble_count=1,complete_response_count=1,unknown_or_duplicate_or_tail='STOP_RETAIN_ALL_RAW'),
        endpoints=ep,request=ep['request'],runtime_meshes_sha256=meshes,actual_charge_prior=prior,
        own_source_sha256={n:sha(n)for n in OWN},bound_files_sha256=bound,
        prior_execution_sha256=prior['execution_sha256'],previous_r2_wall_s=prior['wall_s'],previous_r2_cpu_s=prior['cpu_s'],
        budget=dict(wall_s=28.56,cpu_s=58.86,child_cpu_limit_s=60,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),
        maxima=dict(new_processes=1,source_requests=1,solve_calls=1,source_seed=7,source_solve_seconds=10.),
        external_supervision=dict(required=True,exclusive_sibling_time_log=True,
            sibling_path='results/p4_full/'+RUN+'.supervision.time.txt',format='%e %U %S %x',
            metadata_path='results/p4_full/'+RUN+'.supervision.jsonl',stderr_path='results/p4_full/'+RUN+'.supervision.stderr.log',
            charge_path='results/p4_full/'+RUN+'.supervision.charge.json',time_binary_sha256=sha('/usr/bin/time'),
            python_binary_sha256=sha('/usr/bin/python3'),elapsed_decimal_upper_padding_s=.01,
            CPU_user_plus_system_upper_padding_s=.02,final_independent_POST_required=True),
        source_policy='Original D-fixed author CBi, original geometry/bounds/role selection/RBS/fallback, delta/resolution. No H patch or source rebuild.',
        result_policy='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT only a candidate. Native nonexact/false/reconstruction failures remain. No independent physical/path validation inside S.',
        RNG_boundary='setSeed7+srand7 once before objects;1structural directRNG. Actual library constructor/seed draws and unhooked rand/sampleUniform call totals UNOBSERVED, not zero.',
        zero_calls=dict(compile=0,independent_FK_IK_NR_collision=0,independent_path_qualification=0,
            old_distance_requery=0,local_seam_requery=0,VI_constructions=0,formal_table_I=0),no_retry_reset_resume=True)


def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_SINGLE_SOLVE_RECIPE_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_SOLVE_REVIEWS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'SOLVE_REVIEW_AND_ROOT_FREEZE_REQUIRED')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for n in[*OWN,str(protocol.relative_to(ROOT))]:
        subprocess.run(['git','ls-files','--error-unmatch',n],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        require(not subprocess.check_output(['git','status','--porcelain','--',n],cwd=ROOT,text=True),'UNCOMMITTED '+n)
    for n,h in spec['own_source_sha256'].items():
        require(hashlib.sha256(subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT)).hexdigest()==h,'COMMIT_BLOB_MISMATCH '+n)
    return commit


class Budget(old.Budget):
    def __init__(self,spec,begun,cpu_start):
        super().__init__(spec,begun,cpu_start)
        self.wall_cap=min(28.56,3600.-spec['previous_r2_wall_s']);self.cpu_cap=min(58.86,7200.-spec['previous_r2_cpu_s'])
        require(min(self.wall_cap,self.cpu_cap)>0,'SOLVE_TOTAL_BUDGET_EXHAUSTED')


class Session(tail.Session):
    def __init__(self,target,work,budget,journal,counts):
        super().__init__(target,budget,journal,counts)
        self.command=[target['binary'],'II',str(work),'solve','trace']
    def start(self):
        previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
        try:
            def limits():
                signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask);resource.setrlimit(resource.RLIMIT_CPU,(60,60))
            self.counts['source_process_start_attempted']+=1;self.journal.add('source_process_start_attempted',command=self.command)
            self.proc=subprocess.Popen(self.command,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                bufsize=0,start_new_session=True,preexec_fn=limits,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8',**old.builder.THREADS})
            self.budget.processes.append(self.proc);self.counts['source_process_started']+=1
            self.journal.add('source_process_started',pid=self.proc.pid,command=self.command)
        finally:signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
        self.budget.check();self.register_pipes();group=old.process_group_members(self.proc.pid)
        require([r['pid']for r in group]==[self.proc.pid],'UNEXPECTED_SOURCE_START_GROUP')
        self.journal.add('source_start_group',members=group);self.startup_complete=True
    def query(self,request):
        self.budget.check();self.journal.add('solve_request',request=request)
        raw=json.dumps(request,allow_nan=False,separators=(',',':')).encode()+b'\n'
        require(len(raw)<4096 and self.proc.poll()is None,'SOURCE_NOT_READY_FOR_EXACT_REQUEST')
        self.counts['solve_dispatch_attempted']+=1
        sent=os.write(self.proc.stdin.fileno(),raw);require(sent==len(raw),'INCOMPLETE_REQUEST_NO_RETRY')
        self.counts['solve_dispatched']+=1
        while True:
            while b'\n'not in self.pending:
                self.pump();require(bool(self.selector.get_map())or b'\n'in self.pending,'EOF_WITHOUT_RESPONSE')
            line,self.pending=self.pending.split(b'\n',1);rawline=line+b'\n'
            self.counts['stdout_complete_lines_observed']+=1
            self.journal.add('raw_stdout_line',bytes=len(rawline),base64=base64.b64encode(rawline).decode())
            if rawline==PREAMBLE:
                self.counts['setup_preamble_lines_observed']+=1
                self.journal.add('recognized_exact_setup_preamble',bytes=55,sha256=hashlib.sha256(rawline).hexdigest())
                require(self.counts['setup_preamble_lines_observed']==1 and self.counts['raw_response_lines_observed']==0,
                    'DUPLICATE_OR_LATE_SETUP_PREAMBLE_NO_SKIP')
                continue
            require(self.counts['setup_preamble_lines_observed']==1 and line.startswith(b'{'),
                'UNKNOWN_STDOUT_LINE_OR_MISSING_EXACT_PREAMBLE_NO_SKIP')
            self.journal.add('raw_response_line',bytes=len(rawline),base64=base64.b64encode(rawline).decode())
            response=json.loads(line);self.counts['raw_response_lines_observed']+=1
            self.responses.append(response);return response
    def finish(self,normal):
        was_closed=self.closed
        try:super().finish(normal)
        finally:
            if not was_closed and self.close_group is not None:self.journal.add('source_close_group',members=self.close_group)


def supervisor_proof(spec,protocol):
    ext=spec['external_supervision'];metadata=old.path(ext['metadata_path'])
    planned_raw=metadata.read_bytes().splitlines(keepends=True)[0];planned=json.loads(planned_raw)
    parent=os.getppid();row=old.stat_row(parent)
    require(row is not None and int(row[1])==planned['supervisor_pid'],'EXACT_SUPERVISOR_PARENT_CHAIN_REQUIRED')
    require(planned['event']=='planned_launch'and planned['run_id']==RUN and planned['protocol_sha256']==sha(protocol)
        and planned['runner_sha256']==sha(__file__)and planned['supervisor_source_sha256']==sha(SUPERVISOR),'EXACT_SUPERVISOR_SOURCE_PROTOCOL_REQUIRED')
    require(sha(Path('/proc',str(parent),'exe'))==ext['time_binary_sha256'],'ACTUAL_PARENT_GNU_TIME_REQUIRED')
    expected=['/usr/bin/time','--quiet','-f',ext['format'],'-o',f"/proc/self/fd/{planned['time_fd']}",'/usr/bin/python3',str(Path(__file__).resolve()),'--protocol',str(protocol)]
    require(Path('/proc',str(parent),'cmdline').read_bytes().rstrip(b'\0').split(b'\0')==[v.encode()for v in expected]
        and planned['argv']==expected,'ACTUAL_TIME_ARGV_MISMATCH')
    sibling=old.path(ext['sibling_path']).stat();held=[]
    for p in Path('/proc',str(parent),'fd').iterdir():
        try:
            s=p.stat()
            if(s.st_ino,s.st_dev)==(sibling.st_ino,sibling.st_dev):held.append(int(p.name))
        except FileNotFoundError:pass
    require(held and sibling.st_ino==planned['time_inode']and sibling.st_dev==planned['time_device'],'EXCLUSIVE_SUPERVISION_INODE_MISMATCH')
    return dict(actual_time_pid=parent,actual_time_start_ticks=int(row[19]),supervisor_pid=planned['supervisor_pid'],
        actual_argv=expected,planned_launch_line_sha256=hashlib.sha256(planned_raw).hexdigest(),
        time_inode=sibling.st_ino,time_device=sibling.st_dev,actual_time_output_fds=sorted(held),external_POST_required=True)


def check_response(response,spec):
    require(response['schema']=='P4_ABB_CBIRRT_D_TRANSPORT_DRAFT_V1'and response['environment']=='II'
        and response['operation']=='solve'and response['mode']=='trace'and exact(response['request'],spec['request']),
        'EXACT_SINGLE_SOLVE_TRANSPORT_REQUIRED')
    require(response['source_dispatch_started']==response['source_dispatch_completed']==response['solve_calls']==1
        and response['formal_table_I_calls']==0 and response['independent_path_qualified']is False,
        'SINGLE_SOURCE_SOLVE_ONLY_REQUIRED')
    statuses=('SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT','SOURCE_NONEXACT_RETAINED_PREFIX')
    require(response['status']in statuses and(response['status']==statuses[0])is response['exact']and 'error'not in response,
        'VALID_COMPLETE_SOURCE_STATUS_REQUIRED')
    c=response['construction'];require(c['cbirrt_constructor_dispatch_completed']==c['ompl_setSeed_calls_completed']==c['srand_calls_completed']==1
        and c['svc_only_constructor_dispatch_completed']==0 and c['source_direct_rng_member_initializations_structural']==1
        and c['source_direct_rng_member_true_started_completed']=='UNOBSERVED_LIBRARY_NOT_HOOKED'
        and c['library_internal_seed_draws']=='UNOBSERVED_NOT_REPORTED_ZERO','EXACT_SOURCE_RNG_BOUNDARY_REQUIRED')
    for observed in(c,response):
        require(observed['source_counts_observed']is True,'ACTUAL_TRACE_REQUIRED')
        stack=[];started=Counter();completed=Counter()
        for event in observed['trace']:
            key=(event['id'],event['kind'])
            if event['event']=='entered':stack.append(key);started[event['kind']]+=1
            elif event['event']=='observed':
                require(event['kind']=='save_source_mpaths'and 'source_mpaths'in event['args'],
                    'ONLY_EXISTING_SOURCE_MPATHS_OBSERVATION_ALLOWED')
            else:
                require(event['event']=='completed'and stack and stack.pop()==key,'SOURCE_TRACE_NESTING_OR_RETURN_FAILED')
                completed[event['kind']]+=1
        require(not stack and dict(started)==observed['source_started']and dict(completed)==observed['source_completed'],
            'SOURCE_TRACE_COUNTS_MUST_BE_ACTUAL')
    require(c['source_started']==c['source_completed']=={'mesh_load':1},'SINGLE_CONSTRUCTOR_MESH_TRACE_REQUIRED')
    # Preserve identities, both roots/parents, bridge and every false reconstruction.
    # These objects are independently audited after S; no path PASS is asserted here.
    require(isinstance(response['trees']['nodes'],list)and isinstance(response['milestones_q12'],list),
        'COMPLETE_NATIVE_TREE_AND_MILESTONE_OBSERVATIONS_REQUIRED')
    return response['status']


def execute(spec,protocol):
    begun=time.monotonic();cpu_start=old.own_reaped_cpu();commit=validate(spec,protocol,True)
    launch_proof=supervisor_proof(spec,protocol);folder=ROOT/'results/p4_full'/RUN
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists(),'EXCLUSIVE_SINGLE_SOLVE_NO_RETRY')
    require(not old.builder.active_p4(),'OTHER_ACTIVE_P4_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    budget=None;journal=None;session=None;counts=Counter();diagnostics=[];error=None
    record=dict(schema='P4_R2_ABB_CBIRRT_D_SOLVE02_EXECUTION_V2',run_id=RUN,classification=LABEL,status='STOP_PREFIX_RETAINED',
        source_commit=commit,protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),
        budget=spec['budget'],bound_files_sha256=spec['bound_files_sha256'],prior_execution_sha256=spec['prior_execution_sha256'],
        previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],actual_charge_prior=spec['actual_charge_prior'],
        previous_S01_stop=spec['previous_S01_stop'],stdout_contract=spec['stdout_contract'],
        supervisor_launch_proof=launch_proof,external_supervision_qualified=False,independent_saved_POST_required=True,
        independent_path_qualified=False,zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0)
    try:
        old.durable_new(claim,dict(schema='P4_R2_ABB_CBIRRT_D_SOLVE02_CLAIM_V2',run_id=RUN,protocol=record['protocol'],
            protocol_sha256=record['protocol_sha256'],source_commit=commit,budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=tail.Journal(folder/'evidence.jsonl')
        journal.add('setup',record=record);budget=Budget(spec,begun,cpu_start);budget.start();budget.check()
        work=folder/'work';(work/'simulator').mkdir(parents=True);copied={}
        for name,want in spec['runtime_meshes_sha256'].items():
            budget.check();target=work/'simulator'/Path(name).name
            with target.open('xb')as stream:stream.write(old.path(name).read_bytes())
            require(sha(target)==want,'RUNTIME_MESH_CHANGED');copied[str(target.relative_to(ROOT))]=want
        record['runtime_mesh_sha256']=copied;require(len(copied)==20 and not(work/'paths').exists()and not(folder/'paths').exists(),'FRESH_NATIVE_PATH_DIRECTORIES_REQUIRED')
        session=Session(spec['build_assets']['targets']['distance_destination_fix'],work,budget,journal,counts);session.start()
        response=session.query(spec['request']);journal.add('parsed_response_before_gates',response=response)
        result_status=check_response(response,spec);session.finish(normal=True);budget.check()
        expected=response['construction']['trace']+response['trace'];actual=tail.raw_trace(bytes(session.raw['stderr']))
        require(exact(actual,expected),'RAW_BODY_TRACE_MUST_MATCH_FULL_SOURCE_RESPONSE')
        lines=bytes(session.raw['stdout']).splitlines(keepends=True)
        require(len(lines)==2 and lines[0]==PREAMBLE and lines[1].endswith(b'\n')and exact(json.loads(lines[1]),response),'EXACT_PREAMBLE_PLUS_ONE_COMPLETE_SOURCE_STDOUT_REQUIRED')
        require(counts['stdout_complete_lines_observed']==2 and counts['setup_preamble_lines_observed']==1,'EXACT_ONE_SETUP_LINE_PLUS_RESPONSE_REQUIRED')
        require(counts['solve_dispatched']==counts['raw_response_lines_observed']==1,'EXACT_ONE_SOURCE_DISPATCH_RETURN_REQUIRED')
        record.update(status=result_status,source_exact=response['exact'],source_has_solution=response['has_solution'],
            source_approximate=response['approximate'],source_planner_status=response['planner_status'],
            actual_source_started=response['source_started'],actual_source_completed=response['source_completed'])
    except BaseException as exc:
        if budget is not None:budget.close()
        error=exc;record['termination_reason']=repr(exc)
    finally:
        if budget is not None:budget.close()
        processes=list({p.pid:p for p in([]if budget is None else budget.processes)+([]if session is None or session.proc is None else[session.proc])}.values())
        for proc in processes:
            try:old.kill_source_process(proc)
            except BaseException as exc:diagnostics.append(dict(stage='kill',error=repr(exc)))
        if session is not None:
            try:session.finish(normal=False)
            except BaseException as exc:diagnostics.append(dict(stage='session_cleanup',error=repr(exc)))
        for proc in processes:
            try:old.kill_source_process(proc);proc.wait(timeout=1.)
            except BaseException as exc:diagnostics.append(dict(stage='central_reap',pid=proc.pid,error=repr(exc)))
        record['source_process_registry']=[dict(pid=p.pid,reaped=p.returncode is not None,returncode=p.returncode)for p in processes]
        record['counts']=dict(counts)
        raw_gate=session is not None and session.proc is not None and session.proc.returncode==0 and session.eof and session.closed and session.startup_complete and not session.pending
        record['complete_source_raw_evidence_gate']=raw_gate
        if record['status'].startswith('SOURCE_')and not(len(processes)==counts['source_process_started']==1 and raw_gate):record['status']='STOP_PROCESS_EOF_OR_EXIT_UNQUALIFIED'
        try:
            after={n:sha(n)for n in spec['bound_files_sha256']};record['bound_files_after_sha256']=after
            require(after==spec['bound_files_sha256'],'BOUND_ASSET_CHANGED')
            record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)
            require(record['protocol_after_sha256']==record['protocol_sha256']and record['claim_after_sha256']==record.get('claim_sha256'),'RECIPE_CHANGED')
            latest=current_prior();record['prior_execution_after_sha256']=latest['execution_sha256']
            require(latest==spec['actual_charge_prior'],'PRIOR_OR_AUTHORITATIVE_LEDGER_CHANGED')
        except BaseException as exc:diagnostics.append(dict(stage='mandatory_hashes',error=repr(exc)))
        if journal is not None:
            try:
                journal.stream.write(b'\n')
                if session is not None:
                    journal.add('final_complete_raw_streams',streams={c:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),base64=base64.b64encode(raw).decode())for c,raw in session.raw.items()},EOF=session.eof)
                    for channel,raw in session.raw.items():
                        with(folder/f'source_{channel}.bin').open('xb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
                journal.add('final_counts',counts=dict(counts),diagnostics=diagnostics);journal.finish()
                record['evidence_journal']=str((folder/'evidence.jsonl').relative_to(ROOT));record['evidence_journal_sha256']=sha(folder/'evidence.jsonl')
                native_files=[p for base in(folder/'paths',folder/'work/paths')if base.is_dir()for p in sorted(base.rglob('*'))if p.is_file()]
                record['original_native_output_sha256']={str(p.relative_to(ROOT)):sha(p)for p in native_files}
                record['original_native_output_fsync_completed']=[]
                for p in native_files:
                    with p.open('rb')as stream:os.fsync(stream.fileno())
                    record['original_native_output_fsync_completed'].append(str(p.relative_to(ROOT)))
            except BaseException as exc:diagnostics.append(dict(stage='final_evidence_preservation',error=repr(exc)))
        record['diagnostics']=diagnostics
        record.update(wall_s=time.monotonic()-begun,cpu_s=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes))
        if record['wall_s']>=min(28.56,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(58.86,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            old.durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_R2_ABB_CBIRRT_D_SOLVE02_COST_RECEIPT_V2',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
                last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(28.56,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(58.86,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
            with(folder/'cost_receipt.jsonl').open('xb')as stream:
                stream.write(json.dumps(receipt,allow_nan=False,separators=(',',':')).encode()+b'\n');stream.flush();os.fsync(stream.fileno())
            record['terminal_receipt_status']=receipt['status']
    print(json.dumps(dict(status=record.get('terminal_receipt_status',record['status']),external_supervision_qualified=False,
        independent_path_qualified=False,new_compile=0,formal_table_I_calls=0)))
    if error is not None:raise error
    require(record.get('terminal_receipt_status','').startswith('SOURCE_'),'SINGLE_SOLVE_TRANSPORT_DID_NOT_COMPLETE')


def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_SINGLE_SOLVE_DRAFT_VALIDATED_NO_EXECUTION');return
    execute(spec,protocol)


if __name__=='__main__':main()
