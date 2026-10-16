#!/usr/bin/env python3
"""Single original CBiRRT_NR solve with immutable qualified physical-GD seam.

Draft only. Missing actual engineering build and independent POST rejects even
protocol description. Import creates no protocol/claim, query or process.
Source EXACT is a candidate pending a separate full saved-path qualification.
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
import selectors
import signal
import subprocess
import time
import qualify_p4_full_r2_abb_cbirrt_d_tail02_draft as tail
import build_p4_full_r2_abb_cbirrt_nr_draft as buildlib
old=tail.old
ROOT=old.ROOT
RUN='20261016_R2_ABB_CBIRRT_NR_SOLVE01'
CLAIM='P4_R2_ABB_CBIRRT_NR_SOLVE01_II_A01_SEED7_ONCE_30W_60CPU_20261016'
LABEL='R2_RECONSTRUCTED_PHYSICAL_NR_SINGLE_ORIGINAL_CBIRRT_NR_SOLVE'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_NR_SOLVE_PRE_DRAFT_20261016.md'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_cbirrt_nr_solve_draft.py'
BUILD_POST='reports/P4_FULL_R2_ABB_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST_20261016.json'
BUILD_POST_SCHEMA='P4_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST_V1'
LOCAL='results/p4_full/20261015_R2_ABB_NR_LOCAL01/execution.json'
LOCAL_POST='reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_INDEPENDENT_POST_20261015.json'
LOCAL_RAW='reports/P4_FULL_R2_ABB_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_20261015.json'
PATH_EXEC='results/p4_full/20261015_R2_ABB_RRT_NR_PATH01/execution.json'
PATH_EXEC_SHA='fd74acd7ce5f747cc7123cacef8c9467b1fa985d9d88afdcac47aee0956a5754'
PATH_POST='reports/P4_FULL_R2_ABB_RRT_NR_PATH_ROOT_INDEPENDENT_POST_20261016.json'
PATH_SOURCE_EXEC_SHA='573a1e0bb11a345811ff380a838eb4818000963e98adb90664dfaace755a58b7'
ENDPOINTS=[f'results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_{i}.json'for i in(0,1)]
MARKER=b'P4_CBIRRT_NR_TRACE '
TRACE_KINDS={'distanceFunction','nr_gd','state_project','vector_project','nr_valid_midpoint','state_rbs','vector_rbs',
    'state_reconstruct','vector_reconstruct','collision','mesh_load','growTree','save2file'}
OWN=list(dict.fromkeys([str(Path(__file__).resolve().relative_to(ROOT)),PRE,SUPERVISOR,*tail.OWN,*buildlib.OWN]))
require=old.require
sha=old.sha
load=old.load
exact=old.exact


def build_assets():
    manifest=buildlib.BUILD/'manifest.json';execution=ROOT/'results/p4_full'/buildlib.RUN/'execution.json'
    require(manifest.is_file()and execution.is_file()and old.path(BUILD_POST).is_file(),
        'WAIT_ACTUAL_CBIRRT_NR_BUILD_AND_PERSONNEL_INDEPENDENT_POST_NO_PLACEHOLDER_PROTOCOL')
    m=load(manifest);e=load(execution);post=load(BUILD_POST)
    require(e['schema']=='P4_R2_ABB_CBIRRT_NR_ENGINEERING_EXECUTION_V2'and e['run_id']==buildlib.RUN
        and e['status']=='BUILT_NOT_QUERIED'and e['exit_code']==0 and e['compiler_reaped']is True
        and e['compiler_group_members_after_cleanup']==[]and e['diagnostics']==[]
        and e['query_calls']==e['solve_calls']==e['binary_execution_calls']==e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0,
        'ACTUAL_SUCCESSFUL_COMPILER_ONLY_BUILD_REQUIRED')
    require(m==dict(e,engineering_execution=str(execution.relative_to(ROOT))), 'REAL_BUILD_MANIFEST_MUST_MATCH_ACTUAL_EXECUTION')
    require(e['bound_files_after_sha256']==e['bound_files_sha256']and e['compiled_source_after_sha256']==e['compiled_source_sha256']
        and e['mesh_after_sha256']==e['mesh_sha256']and e['preserved_source_after_sha256']==e['preserved_source_sha256']
        and e['unfrozen_protected_dependencies']==[]and len(e['compiler_dependency_files_sha256'])==6,
        'ENGINEERING_BOUND_ASSETS_ACTUAL_SIX_TU_DEPENDENCIES_REQUIRED')
    require(post['schema']==BUILD_POST_SCHEMA and post['status']=='PASS_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST'
        and post['personnel_independent']is True and post['external_supervision_qualified']is True
        and post['checks_total']==post['checks_passed']and post['checks_total']>0 and post['checks_failed']==0
        and post['failures']==[],'REAL_PERSONNEL_INDEPENDENT_BUILD_POST_MUST_PASS')
    files={BUILD_POST:sha(BUILD_POST),str(manifest):sha(manifest),str(execution.relative_to(ROOT)):sha(execution)}
    for field,filename in(('execution',execution),('manifest',manifest),('protocol',old.path(e['protocol'])),('claim',old.path(e['claim']))):
        require(old.path(post[field]).resolve()==filename.resolve()and post[field+'_sha256']==sha(filename), 'REAL_BUILD_POST_LINK_REQUIRED '+field)
    receipts={'receipt':ROOT/'results/p4_full'/(buildlib.RUN+'.supervision.charge.json'),'internal_receipt':execution.parent/'cost_receipt.json'}
    for field,wanted in receipts.items():
        filename=old.path(post[field]);require(filename.resolve()==wanted.resolve()and filename.is_file()and post[field+'_sha256']==sha(filename),'REAL_BUILD_POST_RECEIPT_LINK_REQUIRED '+field)
        files[str(filename)]=sha(filename)
    external=load(receipts['receipt']);internal=load(receipts['internal_receipt'])
    require(external['execution_sha256']==sha(execution)and external['receipt_sha256']==sha(receipts['internal_receipt'])
        and external['timing_valid']is True and external['time_inode_unchanged']is True
        and external['wall_CPU_caps_pass']is True and external['completed_process_exit0']is True
        and internal['execution_sha256']==sha(execution)and internal['status']=='BUILT_NOT_QUERIED','ACTUAL_ENGINEERING_INTERNAL_AND_EXTERNAL_RECEIPTS_MUST_MATCH')
    require(isinstance(post['retained_sha256'],dict)and post['retained_sha256'],'REAL_BUILD_POST_RETAINED_BINDINGS_REQUIRED')
    files.update(post['retained_sha256']);files.update(e['bound_files_sha256'])
    for field,prefix in(('compiled_source_sha256',buildlib.STAGE),('mesh_sha256',buildlib.STAGE),
        ('preserved_source_sha256',buildlib.STAGE/'preserved_originals'),('compiler_dependency_files_sha256',buildlib.STAGE)):
        for name,want in e[field].items():
            p=prefix/name;require(sha(p)==want,'ACTUAL_BUILT_STAGE_CHANGED '+str(p));files[str(p)]=want
    for field,hashfield in(('protocol','protocol_sha256'),('claim','claim_sha256'),('binary','binary_sha256')):
        require(sha(e[field])==e[hashfield],'ACTUAL_BUILD_RECIPE_OR_BINARY_CHANGED '+field);files[e[field]]=e[hashfield]
    require(e['binary']==str(buildlib.BINARY),'EXACT_CBIRRT_NR_BINARY_REQUIRED')
    for name,want in files.items():require(sha(name)==want,'BOUND_BUILD_OR_INDEPENDENT_POST_ASSET_CHANGED '+name)
    return dict(manifest=str(manifest),manifest_sha256=sha(manifest),execution=str(execution.relative_to(ROOT)),execution_sha256=sha(execution),
        personnel_independent_POST=BUILD_POST,personnel_independent_POST_sha256=sha(BUILD_POST),
        target=dict(stage=str(buildlib.STAGE),binary=str(buildlib.BINARY)),files_sha256=files)


def prerequisites():
    files={};local=load(LOCAL);lp=load(LOCAL_POST);raw=load(LOCAL_RAW);pe=load(PATH_EXEC);pp=load(PATH_POST)
    require(local['status']=='FIXED_LOCAL_ABB_NR_QUALIFIED'and local['next_planner_gate_supported']is True
        and local['soundness_passed']is True and local['full_node_queue_checked']is True
        and local['uncompleted_top_requests']==[]and local['uncompleted_node_ids']==[]
        and local['endpoint_project_gate_by_environment']=={'II':True,'III':True},'EXISTING_QUALIFIED_NR_LOCAL_MUST_BE_REUSED')
    require(lp['schema']=='P4_NR_LOCAL_PERSONNEL_INDEPENDENT_STDLIB_SAVED_POST_V1'and lp['status']=='PASS_SAVED_EVIDENCE_AUDIT'
        and lp['checks_total']==lp['checks_passed']==218766 and lp['checks_failed']==0
        and lp['zero_new_scientific_calls']is True and lp['zero_compile_calls']is True,'EXACT_EXISTING_LOCAL_INDEPENDENT_POST_REQUIRED')
    require(raw['schema']=='P4_NR_LOCAL_ROOT_RAW_LINK_ADDENDUM_V1'and raw['status']=='PASS_RAW_LINK_ADDENDUM'
        and raw['checks_total']==raw['checks_passed']==666 and raw['checks_failed']==0
        and raw['main_report_sha256']==sha(LOCAL_POST),'EXACT_EXISTING_LOCAL_RAW_LINK_REQUIRED')
    require(sha(PATH_EXEC)==PATH_EXEC_SHA and pe['status']=='PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH'
        and pe['full_node_queue_checked']is True and pe['full_node_queue_count']==393 and pe['uncompleted_node_ids']==[]
        and len(pe['completed_node_ids'])==393,'EXISTING_COMPLETE_393_NR_PATH_CERTIFICATE_REQUIRED')
    require(pp['schema']=='P4_NR_PATH_PERSONNEL_INDEPENDENT_STDLIB_SAVED_POST_V1'and pp['status']=='PASS_SAVED_EVIDENCE_AUDIT'
        and pp['personnel_independent']is True and pp['checks_total']==pp['checks_passed']==24448 and pp['checks_failed']==0
        and pp['execution_sha256']==PATH_EXEC_SHA and pp['source_execution_sha256']==PATH_SOURCE_EXEC_SHA
        and pp['summary']['unique_nodes']==pp['summary']['qualified_nodes']==393
        and pp['summary']['full_dense_leaf_count']==392,'EXACT_EXISTING_393_PATH_PERSONNEL_INDEPENDENT_POST_REQUIRED')
    for name in(LOCAL,LOCAL_POST,LOCAL_RAW,PATH_EXEC,PATH_POST):files[name]=sha(name)
    # Bind stored recipes and all evidence files; no component is queried again.
    for name,e in((LOCAL,local),(PATH_EXEC,pe)):
        require(e['bound_files_sha256']==e['bound_files_after_sha256']and e['diagnostics']==[], 'OLD_QUALIFIED_COMPONENT_BOUND_ASSETS_CHANGED')
        files.update(e['bound_files_sha256'])
        for field in('protocol','claim'):
            require(sha(e[field])==e[field+'_sha256']==e[field+'_after_sha256'],'OLD_COMPONENT_RECIPE_CHANGED')
            files[e[field]]=sha(e[field])
        for p in old.path(name).parent.rglob('*'):
            if p.is_file():files[str(p.relative_to(ROOT))]=sha(p)
    q1=buildlib.reused.Q1_MANIFEST;q=load(q1)
    require(q['status']=='BUILT_NOT_QUERIED'and q['returncode']==0,'EXISTING_Q1_BUILD_PROVENANCE_REQUIRED')
    files[str(q1)]=sha(q1)
    for name,want in files.items():require(sha(name)==want,'REUSED_COMPONENT_EVIDENCE_CHANGED '+name)
    return dict(Q1_manifest=str(q1),Q1_manifest_sha256=sha(q1),NR_local_POST=LOCAL_POST,NR_local_raw_POST=LOCAL_RAW,
        complete_393_NR_path_POST=PATH_POST,complete_393_NR_path_POST_sha256=sha(PATH_POST),files_sha256=files,
        scope='Reuse saved Q1/local/full393 mathematical and discrete collision evidence only; no requery; does not qualify a new CBiNR path.')


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
    for charge in(ROOT/'results/p4_full').glob('*_R2_*.supervision.charge.json'):
        run=charge.name.removesuffix('.supervision.charge.json')
        if run!=RUN:require((charge.parent/run/'execution.json').is_file(),'ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING '+run)
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
        solve_seconds=10.,start_q12=q[0],goal_q12=q[1],bounds_low_rad=low,bounds_high_rad=high),sampler_low_rad=low,sampler_high_rad=high,
        endpoint_policy='Same independently qualified RECONSTRUCTED A01 q12; no endpoint projection/requery, no active role or analytic branch controls in NR.')

def draft_protocol():
    # Hard-fail before constructing any prior/protocol if real build or POST absent.
    assets=build_assets();ready=prerequisites();ep=endpoints();prior=current_prior()
    stage=Path(assets['target']['stage']);meshes={str(p):sha(p)for p in sorted((stage/'simulator').glob('*.tris'))}
    require(len(meshes)==20,'EXACT20_BOUND_NATIVE_MESHES_REQUIRED')
    bound={**ready['files_sha256'],**assets['files_sha256'],**ep['files_sha256'],**meshes,
        prior['ledger']:prior['ledger_sha256'],**{n:sha(n)for n in OWN},'/usr/bin/time':sha('/usr/bin/time'),'/usr/bin/python3':sha('/usr/bin/python3')}
    return dict(schema='P4_R2_ABB_CBIRRT_NR_SINGLE_SOLVE_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_freeze_approved=False,latest_actual_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,prerequisites=ready,build_assets=assets,
        stdout_contract=dict(complete_response_count=1,setup_preamble_count=0,stdin_unique_write_then_immediate_close=True,
            request_bytes_base64_SHA_and_actual_written_result_required=True,unknown_duplicate_or_tail='STOP_RETAIN_ALL_RAW',
            actual_both_pipe_EOF_required=True,empty_preclose_group_requires_actual_poll_exit0=True,actual_after_reap_empty_group_required=True),
        endpoints=ep,request=ep['request'],runtime_meshes_sha256=meshes,actual_charge_prior=prior,
        own_source_sha256={n:sha(n)for n in OWN},bound_files_sha256=bound,
        prior_execution_sha256=prior['execution_sha256'],previous_r2_wall_s=prior['wall_s'],previous_r2_cpu_s=prior['cpu_s'],
        budget=dict(wall_s=30.,cpu_s=60.,child_cpu_limit_s=60,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),
        maxima=dict(new_processes=1,source_requests=1,solve_calls=1,source_seed=7,source_solve_seconds=10.),
        external_supervision=dict(required=True,exclusive_sibling_time_log=True,
            sibling_path='results/p4_full/'+RUN+'.supervision.time.txt',format='%e %U %S %x',
            metadata_path='results/p4_full/'+RUN+'.supervision.jsonl',stderr_path='results/p4_full/'+RUN+'.supervision.stderr.log',
            charge_path='results/p4_full/'+RUN+'.supervision.charge.json',time_binary_sha256=sha('/usr/bin/time'),
            python_binary_sha256=sha('/usr/bin/python3'),elapsed_decimal_upper_padding_s=.01,
            CPU_user_plus_system_upper_padding_s=.02,final_independent_POST_required=True),
        source_policy='Original author CBiNR full12 distance/two-tree control/RBS/reconstruction/geometry/bounds/resolution. Immutable previously qualified physical-GD seam remains RECONSTRUCTED; no PCS H/D/role/branch changes.',
        result_policy='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT is a candidate. Void save/false reconstruction/all native failures retained. No independent physical/path qualification inside S.',
        RNG_boundary='setSeed7+srand7 once before objects;1structural directRNG. Actual library constructor/seed draws and unhooked rand/sampleUniform totals UNOBSERVED, not zero.',
        zero_calls=dict(compile=0,independent_FK_IK_NR_collision=0,independent_path_qualification=0,old_component_requery=0,VI_constructions=0,formal_table_I=0),
        no_retry_reset_resume=True)


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
        self.wall_cap=min(30.,3600.-spec['previous_r2_wall_s']);self.cpu_cap=min(60.,7200.-spec['previous_r2_cpu_s'])
        require(min(self.wall_cap,self.cpu_cap)>0,'SOLVE_TOTAL_BUDGET_EXHAUSTED')

class Session(tail.Session):
    def __init__(self,target,work,budget,journal,counts):
        super().__init__(target,budget,journal,counts)
        self.command=[target['binary'],'II',str(work),'solve','trace']
        self.start_ticks=None;self.pipe_EOF_observed={'stdout':False,'stderr':False};self.after_reap_group=None
        self.request_raw=None;self.request_sent=None;self.stdin_closed_after_request=False;self.close_poll_result=None;self.close_postpoll_group=None;self.close_poll_observations=[]
    def start(self):
        previous_mask=signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})
        try:
            def limits():
                signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask);resource.setrlimit(resource.RLIMIT_CPU,(60,60))
            self.counts['source_process_start_attempted']+=1;self.journal.add('source_process_start_attempted',command=self.command)
            self.proc=subprocess.Popen(self.command,cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                bufsize=0,start_new_session=True,preexec_fn=limits,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8',**old.builder.THREADS})
            self.budget.processes.append(self.proc);self.counts['source_process_started']+=1
            row=old.stat_row(self.proc.pid);require(row is not None and int(row[2])==self.proc.pid,'ACTUAL_REGISTERED_SOURCE_STAT_REQUIRED')
            self.start_ticks=int(row[19]);require(self.start_ticks>0,'ACTUAL_SOURCE_START_TICKS_REQUIRED')
            self.journal.add('source_process_started',pid=self.proc.pid,start_ticks=self.start_ticks,command=self.command)
        finally:signal.pthread_sigmask(signal.SIG_SETMASK,previous_mask)
        self.budget.check();self.register_pipes();group=old.process_group_members(self.proc.pid)
        require([r['pid']for r in group]==[self.proc.pid],'UNEXPECTED_SOURCE_START_GROUP')
        row=old.stat_row(self.proc.pid);require(row is not None and int(row[19])==self.start_ticks,'SOURCE_PID_IDENTITY_CHANGED_AT_START')
        self.journal.add('source_start_group',members=group,actual_start_ticks=int(row[19]));self.startup_complete=True
    def pump(self,timeout=.02,enforce=True):
        if enforce:self.budget.check();timeout=min(timeout,max(0.,self.budget.remaining()))
        for key,_ in self.selector.select(max(0.,timeout)):
            raw=os.read(key.fileobj.fileno(),65536)
            if not raw:
                self.pipe_EOF_observed[key.data]=True;self.selector.unregister(key.fileobj)
                self.journal.add('actual_pipe_EOF_observed',channel=key.data);continue
            self.raw[key.data].extend(raw)
            if key.data=='stdout':self.pending+=raw
            self.journal.add('raw_pipe_chunk',channel=key.data,bytes=len(raw),base64=base64.b64encode(raw).decode())
        if enforce:self.budget.check()
    def query(self,request):
        self.budget.check();raw=json.dumps(request,allow_nan=False,separators=(',',':')).encode()+b'\n'
        self.request_raw=raw;self.journal.add('solve_request_exact_bytes',request=request,bytes=len(raw),
            base64=base64.b64encode(raw).decode(),sha256=hashlib.sha256(raw).hexdigest())
        require(len(raw)<4096 and self.proc.poll()is None,'SOURCE_NOT_READY_FOR_EXACT_REQUEST')
        self.counts['solve_dispatch_attempted']+=1
        try:
            self.request_sent=os.write(self.proc.stdin.fileno(),raw)
            require(self.request_sent==len(raw),'INCOMPLETE_REQUEST_NO_RETRY')
            self.counts['solve_dispatched']+=1
        finally:
            # The source waits for EOF before solving. Close even after a failed
            # single write; cleanup never sends a retry or second request.
            if self.proc.stdin and not self.proc.stdin.closed:self.proc.stdin.close()
            self.stdin_closed_after_request=True
            self.journal.add('single_request_write_and_stdin_close',actual_sent=self.request_sent,
                sent_bytes_base64=None if self.request_sent is None else base64.b64encode(raw[:self.request_sent]).decode(),
                sent_sha256=None if self.request_sent is None else hashlib.sha256(raw[:self.request_sent]).hexdigest(),
                exact_full_request_written=self.request_sent==len(raw),stdin_closed=self.proc.stdin.closed)
        while b'\n'not in self.pending:
            self.pump();require(bool(self.selector.get_map())or b'\n'in self.pending,'EOF_WITHOUT_RESPONSE')
        line,self.pending=self.pending.split(b'\n',1);rawline=line+b'\n';self.counts['stdout_complete_lines_observed']+=1
        self.journal.add('raw_response_line',bytes=len(rawline),base64=base64.b64encode(rawline).decode())
        require(line.startswith(b'{'),'UNKNOWN_STDOUT_PREFIX_NO_SKIP')
        response=json.loads(line);self.counts['raw_response_lines_observed']+=1;self.responses.append(response);return response
    def finish(self,normal):
        if self.closed:return
        try:
            if self.proc is not None:
                self.register_pipes()
                if normal:
                    self.close_group=old.process_group_members(self.proc.pid)
                    self.close_poll_result=self.proc.poll();self.close_poll_observations.append(self.close_poll_result)
                    ids=[r['pid']for r in self.close_group]
                    if ids==[self.proc.pid]and self.close_poll_result is None:
                        row=old.stat_row(self.proc.pid)
                        if row is None or int(row[19])!=self.start_ticks:
                            # A source can finish between poll and /proc read.
                            # One actual re-poll may enter only the reviewed
                            # exit0+empty-group alternative, never infer success.
                            self.close_poll_result=self.proc.poll();self.close_poll_observations.append(self.close_poll_result)
                            self.close_postpoll_group=old.process_group_members(self.proc.pid)
                            require(self.close_poll_result==0 and self.close_postpoll_group==[],
                                'VANISHED_OR_CHANGED_SOURCE_REQUIRES_ACTUAL_EXIT0_AND_EMPTY_GROUP')
                    else:
                        self.close_postpoll_group=old.process_group_members(self.proc.pid)
                        require(ids in([], [self.proc.pid])and self.close_poll_result==0 and self.close_postpoll_group==[],
                            'EXITED_SOURCE_REQUIRES_ACTUAL_POLL_EXIT0_AND_ACTUAL_EMPTY_GROUP')
                    require(self.stdin_closed_after_request and self.proc.stdin.closed,'STDIN_MUST_CLOSE_AFTER_UNIQUE_WRITE')
                    self.journal.add('source_close_group',members=self.close_group,actual_poll_result=self.close_poll_result,actual_poll_observations=self.close_poll_observations,actual_postpoll_group=self.close_postpoll_group,start_ticks=self.start_ticks)
                    deadline=time.monotonic()+self.budget.remaining()
                else:kill_source_group(self.proc);deadline=time.monotonic()+2.
                while self.selector.get_map()and time.monotonic()<deadline:self.pump(.01,enforce=normal)
                try:self.proc.wait(timeout=max(.001,deadline-time.monotonic()))
                except subprocess.TimeoutExpired:kill_source_group(self.proc);self.proc.wait(timeout=1.)
                while self.selector.get_map()and time.monotonic()<deadline:self.pump(0.,enforce=False)
                self.eof=all(self.pipe_EOF_observed.values())and not self.selector.get_map()
                self.after_reap_group=old.process_group_members(self.proc.pid)
                self.journal.add('source_after_reap_group',members=self.after_reap_group,returncode=self.proc.returncode,
                    actual_pipe_EOF_observed=self.pipe_EOF_observed,start_ticks=self.start_ticks)
                require(not self.after_reap_group,'ACTUAL_SOURCE_GROUP_MUST_BE_EMPTY_AFTER_REAP')
                for stream in(self.proc.stdin,self.proc.stdout,self.proc.stderr):
                    if stream is not None and not stream.closed:stream.close()
            self.selector.close();self.closed=True
            if normal:require(self.eof and not self.pending and self.proc.returncode==0,'SOURCE_ACTUAL_DUAL_EOF_TAIL_OR_EXIT_FAILED')
        except BaseException:
            # Leave the selector usable for the central failure drain.
            raise


def kill_source_group(proc):
    group=old.process_group_members(proc.pid)
    if group:
        try:os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    if proc.poll()is None:proc.kill()


def raw_trace(raw):
    rows=[]
    for line in raw.splitlines(keepends=True):
        if MARKER in line:
            require(line.endswith(b'\n'),'INCOMPLETE_RAW_NR_TRACE_LINE')
            rows.append(json.loads(line.split(MARKER,1)[1]))
    return rows


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
    require(response['schema']=='P4_ABB_CBIRRT_NR_TRANSPORT_DRAFT_V1'and response['environment']=='II'
        and response['operation']=='solve'and response['mode']=='trace'and exact(response['request'],spec['request']),
        'EXACT_SINGLE_SOLVE_TRANSPORT_REQUIRED')
    require(response['source_dispatch_started']==response['source_dispatch_completed']==response['solve_calls']==1
        and response['formal_table_I_calls']==0 and response['independent_path_qualified']is False,
        'SINGLE_SOURCE_SOLVE_ONLY_REQUIRED')
    statuses=('SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT','SOURCE_NONEXACT_RETAINED_PREFIX')
    require(response['status']in statuses and(response['status']==statuses[0])is response['exact']and 'error'not in response,
        'VALID_COMPLETE_SOURCE_STATUS_REQUIRED')
    c=response['construction'];require(c['cbirrt_constructor_dispatch_completed']==c['ompl_setSeed_calls_completed']==c['srand_calls_completed']==1
        and c['source_direct_rng_member_initializations_structural']==1
        and c['source_direct_rng_member_true_started_completed']=='UNOBSERVED_LIBRARY_NOT_HOOKED'
        and c['library_internal_seed_draws']=='UNOBSERVED_NOT_REPORTED_ZERO','EXACT_SOURCE_RNG_BOUNDARY_REQUIRED')
    require(response['state_validity_callback']=='ORIGINAL_MAIN_ALWAYS_TRUE_NO_FK'and response['resolution']==.1
        and response['distance_policy']=='ORIGINAL_FULL12_SI_DISTANCE_NO_ACTIVE_ROLE_OR_ANALYTIC_BRANCH'
        and response['solution_path_simplification']is False and response['continuous_collision_certificate']is False,
        'EXACT_ORIGINAL_NR_ENTRY_CONDITIONS_REQUIRED')
    for observed in(c,response):
        require(observed['source_counts_observed']is True,'ACTUAL_TRACE_REQUIRED')
        stack=[];started=Counter();completed=Counter()
        for event in observed['trace']:
            require(event['kind']in TRACE_KINDS or event['kind']=='save_source_mpaths','ONLY_NR_OBSERVER_EVENT_KINDS_ALLOWED')
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
    require(c['source_started']==c['source_completed']=={'mesh_load':1}and len(c['trace'])==2
        and c['trace'][0]['args']=={}and c['trace'][1]['result']=={},'SINGLE_CONSTRUCTOR_MESH_TRACE_REQUIRED')
    # Preserve identities, both roots/parents, bridge and every false reconstruction.
    # These objects are independently audited after S; no path PASS is asserted here.
    require(isinstance(response['trees']['nodes'],list)and isinstance(response['milestones_q12'],list),
        'COMPLETE_NATIVE_TREE_AND_MILESTONE_OBSERVATIONS_REQUIRED')
    required_node_fields={'motion_id','tree','state_id','parent_motion_id','root_state_id','root_motion_id','q12','root_q12'}
    require(all(set(node)==required_node_fields for node in response['trees']['nodes']),'SAVE_ONLY_ACTUAL_NR_TREE_FIELDS_NO_PCS_BRANCH_ROLE')
    require(response['planner_data']is not None if response['exact']else response['planner_data']is None,'EXACT_ONLY_SOURCE_PLANNER_DATA_POLICY')
    return response['status']

def execute(spec,protocol):
    begun=time.monotonic();cpu_start=old.own_reaped_cpu();commit=validate(spec,protocol,True)
    launch_proof=supervisor_proof(spec,protocol);folder=ROOT/'results/p4_full'/RUN
    claim=ROOT/'results/p4_full'/(CLAIM+'.claim.json')
    require(not folder.exists()and not claim.exists(),'EXCLUSIVE_SINGLE_SOLVE_NO_RETRY')
    require(not old.builder.active_p4(),'OTHER_ACTIVE_P4_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    budget=None;journal=None;session=None;counts=Counter();diagnostics=[];error=None
    record=dict(schema='P4_R2_ABB_CBIRRT_NR_SOLVE01_EXECUTION_V1',run_id=RUN,classification=LABEL,status='STOP_PREFIX_RETAINED',
        source_commit=commit,protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),claim=str(claim.relative_to(ROOT)),
        budget=spec['budget'],bound_files_sha256=spec['bound_files_sha256'],prior_execution_sha256=spec['prior_execution_sha256'],
        previous_r2_wall_s=spec['previous_r2_wall_s'],previous_r2_cpu_s=spec['previous_r2_cpu_s'],actual_charge_prior=spec['actual_charge_prior'],
        stdout_contract=spec['stdout_contract'],
        supervisor_launch_proof=launch_proof,external_supervision_qualified=False,independent_saved_POST_required=True,
        independent_path_qualified=False,zero_calls=spec['zero_calls'],formal_table_I_calls=0,new_VI_candidate_constructions=0)
    try:
        old.durable_new(claim,dict(schema='P4_R2_ABB_CBIRRT_NR_SOLVE01_CLAIM_V1',run_id=RUN,protocol=record['protocol'],
            protocol_sha256=record['protocol_sha256'],source_commit=commit,budget=spec['budget'],no_retry_reset_resume=True))
        record['claim_sha256']=sha(claim);folder.mkdir();journal=tail.Journal(folder/'evidence.jsonl')
        journal.add('setup',record=record);budget=Budget(spec,begun,cpu_start);budget.start();budget.check()
        work=folder/'work';(work/'simulator').mkdir(parents=True);copied={}
        for name,want in spec['runtime_meshes_sha256'].items():
            budget.check();target=work/'simulator'/Path(name).name
            with target.open('xb')as stream:stream.write(old.path(name).read_bytes())
            require(sha(target)==want,'RUNTIME_MESH_CHANGED');copied[str(target.relative_to(ROOT))]=want
        record['runtime_mesh_sha256']=copied;require(len(copied)==20 and not(work/'paths').exists()and not(folder/'paths').exists(),'FRESH_NATIVE_PATH_DIRECTORIES_REQUIRED')
        session=Session(spec['build_assets']['target'],work,budget,journal,counts);session.start()
        response=session.query(spec['request']);journal.add('parsed_response_before_gates',response=response)
        result_status=check_response(response,spec);session.finish(normal=True);budget.check()
        expected=response['construction']['trace']+response['trace'];actual=raw_trace(bytes(session.raw['stderr']))
        require(exact(actual,expected),'RAW_BODY_TRACE_MUST_MATCH_FULL_SOURCE_RESPONSE')
        lines=bytes(session.raw['stdout']).splitlines(keepends=True)
        require(len(lines)==1 and lines[0].endswith(b'\n')and exact(json.loads(lines[0]),response),'EXACT_ONE_COMPLETE_SOURCE_STDOUT_NO_PREAMBLE_REQUIRED')
        require(counts['stdout_complete_lines_observed']==1,'EXACT_ONE_RESPONSE_LINE_REQUIRED')
        require(session.request_sent==len(session.request_raw)and exact(json.loads(session.request_raw),response['request'])
            and session.stdin_closed_after_request,'ACTUAL_FULL_SINGLE_REQUEST_MUST_MATCH_RESPONSE_AND_STDIN_CLOSE')
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
            try:kill_source_group(proc)
            except BaseException as exc:diagnostics.append(dict(stage='kill',error=repr(exc)))
        if session is not None:
            try:session.finish(normal=False)
            except BaseException as exc:diagnostics.append(dict(stage='session_cleanup',error=repr(exc)))
        for proc in processes:
            try:kill_source_group(proc);proc.wait(timeout=1.)
            except BaseException as exc:diagnostics.append(dict(stage='central_reap',pid=proc.pid,error=repr(exc)))
        after_groups={str(p.pid):old.process_group_members(p.pid)for p in processes}
        record['source_process_registry']=[dict(pid=p.pid,reaped=p.returncode is not None,returncode=p.returncode,
            actual_start_ticks=None if session is None or session.proc is not p else session.start_ticks,
            actual_after_reap_group=after_groups[str(p.pid)])for p in processes]
        if session is not None:
            record['source_lifecycle']=dict(actual_start_ticks=session.start_ticks,actual_pipe_EOF_observed=session.pipe_EOF_observed,
                actual_preclose_group=session.close_group,actual_preclose_poll_result=session.close_poll_result,actual_preclose_poll_observations=session.close_poll_observations,actual_postpoll_group=session.close_postpoll_group,
                actual_after_reap_group=session.after_reap_group,stdin_closed_after_unique_request=session.stdin_closed_after_request,
                request_bytes=None if session.request_raw is None else len(session.request_raw),actual_request_sent=session.request_sent,
                request_sha256=None if session.request_raw is None else hashlib.sha256(session.request_raw).hexdigest())
        record['counts']=dict(counts)
        raw_gate=session is not None and session.proc is not None and session.proc.returncode==0 and session.eof and session.closed and session.startup_complete and not session.pending and session.after_reap_group==[]and all(session.pipe_EOF_observed.values())and all(not g for g in after_groups.values())
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
        if record['wall_s']>=min(30.,3600.-spec['previous_r2_wall_s'])or record['cpu_s']>=min(60.,7200.-spec['previous_r2_cpu_s']):record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
        if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'
        if folder.is_dir():
            old.durable_new(folder/'execution.json',record)
            receipt=dict(schema='P4_R2_ABB_CBIRRT_NR_SOLVE01_COST_RECEIPT_V1',execution_sha256=sha(folder/'execution.json'),status=record['status'],
                wall_s_through_execution_persistence=time.monotonic()-begun,cpu_s_through_execution_persistence=old.own_reaped_cpu()-cpu_start+old.direct_live_cpu(processes),
                last_receipt_persistence_tail='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',external_supervision_qualified=False)
            if receipt['wall_s_through_execution_persistence']>=min(30.,3600.-spec['previous_r2_wall_s'])or receipt['cpu_s_through_execution_persistence']>=min(60.,7200.-spec['previous_r2_cpu_s']):receipt['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'
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
