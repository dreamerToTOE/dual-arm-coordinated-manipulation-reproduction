#!/usr/bin/env python3
"""Complete original CBiRRT saved path candidate; no science at import/describe.

Missing real S and personnel-independent POST hard-refuses draft generation.
The physical node loop is the original qualified PCS path loop, unchanged.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import qualify_p4_full_r2_abb_cbirrt_d_solve_draft as source
import materialize_p4_full_r2_abb_cbirrt_d_path_draft as saved

old=source.old
ROOT=old.ROOT
RUN='20261015_R2_ABB_CBIRRT_D_PATH01'
CLAIM='P4_R2_ABB_CBIRRT_D_PATH_FULL2048_120W_240CPU_20261016'
LABEL='R2_NUMERICS_D_FIXED_CBIRRT_RECONSTRUCTED_A01_DISCRETE_SOURCE_POLICY_PATH'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_D_PATH_PRE_DRAFT_20261016.md'
MATERIALIZER_PRE='reports/P4_FULL_R2_ABB_CBIRRT_D_PATH_MATERIALIZER_PRE_DRAFT_20261016.md'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_cbirrt_d_path_draft.py'
SOURCE_DIR='results/p4_full/'+source.RUN
SOURCE_POST='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE01_SAVED_INDEPENDENT_POST_20261016.json'
ORIGINAL_PCS='scripts/qualify_p4_full_r2_abb_rrt_path.py'
ORIGINAL_PCS_SHA='bdf4db7537b327872674e355dcbdcd5e31bebbb5a53ae6e21a07490a514b6865'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
MAX_NODES=2048
GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5,
    'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*sys.float_info.epsilon}
OWN=list(dict.fromkeys([str(Path(__file__).resolve().relative_to(ROOT)),PRE,MATERIALIZER_PRE,SUPERVISOR,
    'scripts/materialize_p4_full_r2_abb_cbirrt_d_path_draft.py',ORIGINAL_PCS,
    'scripts/recover_p4_full_r2_endpoints.py','scripts/qualify_p4_full_r2_vi_rss_reconstructed.py',
    'baselines/p4_full/geometry_consistent/collision_adapter.py','baselines/p4_full/geometry_consistent/physical_nr.py',
    'baselines/p4_full/abb_independent_oracle.py','baselines/p4_full/analyze_comau_native_qualification.py',
    'baselines/p4_full/geometry_consistent/rss_geometry.py',*source.OWN]))
require=old.require
sha=old.sha
load=old.load
path=old.path
exact=old.exact
key=saved.key
durable_new=old.durable_new

def bind(files,name,want=None):
    name=str(name);actual=sha(name);require(want is None or actual==want,'P_BOUND_HASH_CHANGED '+name);files[name]=actual
    return load(name)if name.endswith('.json')else None

def source_provenance():
    require(path(SOURCE_DIR+'/execution.json').is_file()and path(SOURCE_POST).is_file(),
        'WAIT_ACTUAL_SINGLE_S_AND_PERSONNEL_INDEPENDENT_POST_NO_PLACEHOLDER_QUEUE')
    files={};e=bind(files,SOURCE_DIR+'/execution.json');post=bind(files,SOURCE_POST)
    require(e['schema']=='P4_R2_ABB_CBIRRT_D_SOLVE_EXECUTION_V1'and e['run_id']==source.RUN
        and e['status']=='SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT'and e['source_exact']is True
        and e['source_has_solution']is True and e['source_approximate']is False,
        'ACTUAL_EXACT_NONAPPROXIMATE_SINGLE_S_REQUIRED')
    require(post['schema']=='P4_SOLVE01_SAVED_INDEPENDENT_POST_V1'
        and post['status']=='PASS_SOLVE01_TRANSPORT_EVIDENCE_INDEPENDENT_POST'
        and post['personnel_independent']is True and post['external_supervision_qualified']is True
        and post['checks_total']==post['checks_passed']and post['checks_total']>0 and post['checks_failed']==0
        and post['execution_sha256']==sha(SOURCE_DIR+'/execution.json')
        and post['source_status']==e['status']and post['source_exact']is True and post['source_has_solution']is True
        and post['source_approximate']is False,'S_FULL_ACTUAL_INDEPENDENT_TRANSPORT_AND_EXACT_CONTRACT_REQUIRED')
    require(e['bound_files_sha256']==e['bound_files_after_sha256'],'S_ORIGINAL_BOUND_SET_CHANGED')
    for n,w in e['bound_files_sha256'].items():bind(files,n,w)
    p=bind(files,e['protocol'],e['protocol_sha256']);c=bind(files,e['claim'],e['claim_sha256'])
    require(e['protocol_sha256']==e['protocol_after_sha256']and e['claim_sha256']==e['claim_after_sha256']
        and p['frozen']is True and all(type(v)is bool and v for v in p['reviews'].values())
        and p['run_id']==source.RUN and c['protocol_sha256']==e['protocol_sha256'],'S_FROZEN_PROTOCOL_CLAIM_CHAIN_REQUIRED')
    require(e['complete_source_raw_evidence_gate']is True and len(e['source_process_registry'])==1
        and all(r['reaped']is True and r['returncode']==0 for r in e['source_process_registry'])
        and e['counts']['solve_dispatched']==e['counts']['raw_response_lines_observed']==1,
        'S_ONE_REQUEST_PROCESS_COMPLETE_RAW_EOF_EXIT_REQUIRED')
    require(isinstance(post['retained_sha256'],dict)and post['retained_sha256'],'FULL_S_INDEPENDENT_BINDINGS_REQUIRED')
    for n,w in post['retained_sha256'].items():bind(files,n,w)
    for n,w in e['runtime_mesh_sha256'].items():bind(files,n,w)
    for n,w in e['original_native_output_sha256'].items():bind(files,n,w)
    bind(files,e['evidence_journal'],e['evidence_journal_sha256'])
    rows=[json.loads(line)for line in path(e['evidence_journal']).read_bytes().splitlines()if line.strip()]
    parsed=[r['response']for r in rows if r['event']=='parsed_response_before_gates']
    require(len(parsed)==1,'EXACT_ONE_S_PARSED_RESPONSE_REQUIRED');d=parsed[0]
    stdout=SOURCE_DIR+'/source_stdout.bin';stderr=SOURCE_DIR+'/source_stderr.bin';bind(files,stdout);bind(files,stderr)
    lines=path(stdout).read_bytes().splitlines(keepends=True)
    require(len(lines)==1 and lines[0].endswith(b'\n')and exact(json.loads(lines[0]),d),'S_ORIGINAL_STDOUT_RESPONSE_BINARY64_REQUIRED')
    require(exact(source.tail.raw_trace(path(stderr).read_bytes()),d['construction']['trace']+d['trace']),
        'S_COMPLETE_ORIGINAL_BODY_TRACE_REQUIRED')
    require(exact(d['request'],p['request'])and d['source_dispatch_started']==d['source_dispatch_completed']==d['solve_calls']==1
        and d['formal_table_I_calls']==0 and d['independent_path_qualified']is False,
        'S_ACTUAL_FIXED_REQUEST_ONE_SOLVE_SCOPE_REQUIRED')
    return d,files,dict(execution=SOURCE_DIR+'/execution.json',execution_sha256=sha(SOURCE_DIR+'/execution.json'),
        independent_POST=SOURCE_POST,independent_POST_sha256=sha(SOURCE_POST),protocol=e['protocol'],claim=e['claim'],
        source_commit=e['source_commit'],request=p['request'],source_status=e['status'],
        scope='Native exact remains pending independently qualified complete discrete source-policy path.')

def current_prior():
    ledgers=list((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
    require(ledgers,'WAIT_ACTUAL_CURRENT_AUTHORITATIVE_LEDGER');ledger=max(ledgers,key=lambda p:int(p.stem.rsplit('V',1)[1]));value=load(ledger)
    actual={str(p.relative_to(ROOT)):sha(p)for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')if p.parent.name!=RUN}
    require({r['execution']:r['execution_sha256']for r in value['executions']}==actual,'LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS')
    wall=math.fsum(r.get('charged_wall_s',r['wall_s'])for r in value['executions'])
    cpu=math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in value['executions'])
    require(all(math.isfinite(v)and v>=0 for v in(wall,cpu))and wall==value['conservative_r2_sum_wall_s']
        and cpu==value['conservative_r2_sum_cpu_s'],'EXACT_PRIOR_CHARGE_SUMS_REQUIRED')
    for r in value['executions']:
        if 'charged_wall_s'not in r:continue
        post=load(r['external_post'])
        require(sha(r['external_post'])==r['external_post_sha256']and post['personnel_independent']is True
            and post['external_supervision_qualified']is True and post['checks_total']==post['checks_passed']and post['checks_failed']==0
            and post['execution_sha256']==r['execution_sha256']and post['upper_wall_s']==r['charged_wall_s']and post['upper_cpu_s']==r['charged_cpu_s']
            and sha(r['external_time'])==r['external_time_sha256']==post['external_time_sha256'],'PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED')
    for run in(source.tail.RUN,Path(source.L_DIR).name,source.RUN):
        prefix=ROOT/'results/p4_full'/run
        require(not Path(str(prefix)+'.supervision.charge.json').is_file()or(prefix/'execution.json').is_file(),
            'KNOWN_D_L_S_ORPHAN_CHARGE_REQUIRES_ACCOUNTING '+run)
    return dict(ledger=str(ledger.relative_to(ROOT)),ledger_sha256=sha(ledger),execution_sha256=actual,
        wall_s=wall,cpu_s=cpu,historical_unmeasured_tail='RETAINED_UNKNOWN; CHARGED_REMAINING_IS_UPPER_BOUND')

def draft_protocol():
    d,files,provenance=source_provenance();queue=saved.materialize(d,provenance['request']);prior=current_prior()
    require(sha(ORIGINAL_PCS)==ORIGINAL_PCS_SHA,'QUALIFIED_PCS_PHYSICAL_LOOP_SOURCE_CHANGED')
    manifest=bind(files,COLLISION);entries=[r for r in manifest['entries']if r['model']=='abb']
    require(sorted(r['variant']for r in entries)==['aligned','native'],'EXACT_V3_ABB_NATIVE_ALIGNED_REQUIRED')
    for entry in entries:
        require(entry['exit_code']==0,'V3_COLLISION_BUILD_REQUIRED');bind(files,entry['binary'],entry['binary_sha256'])
        for n,w in entry['source_files_sha256'].items():bind(files,str(Path(entry['source_root'])/n),w)
        for n,w in entry['mesh_sha256'].items():bind(files,str(Path(entry['cwd'])/'simulator'/n),w)
    for n in OWN:bind(files,n)
    bind(files,prior['ledger'],prior['ledger_sha256'])
    for n,w in prior['execution_sha256'].items():bind(files,n,w)
    bind(files,'/usr/bin/time');bind(files,'/usr/bin/python3');n=min(len(queue['nodes']),MAX_NODES)
    return dict(schema='P4_R2_ABB_CBIRRT_D_PATH_DRAFT_V1',frozen=False,
        reviews=dict(independent_static_review_passed=False,root_complete_queue_freeze_approved=False,latest_actual_prior_confirmed=False),
        run_id=RUN,claim_id=CLAIM,classification=LABEL,source_provenance=provenance,fixed_queue=queue,
        bound_files_sha256=files,own_source_sha256={n:sha(n)for n in OWN},actual_charge_prior=prior,
        prior_execution_sha256=prior['execution_sha256'],previous_r2_wall_s=prior['wall_s'],previous_r2_cpu_s=prior['cpu_s'],
        budget=dict(wall_s=120.,cpu_s=240.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.),gates=GATES,
        max_nodes_per_execution=MAX_NODES,full_queue_node_count=len(queue['nodes']),
        max_math_arm_FK=2*n,max_collision_calls=n,max_adapter_internal_arm_FK_J=4*n,
        zero_calls=dict(IK=0,NR=0,projection=0,RBS=0,solve=0,RNG=0,VI_constructions=0,formal_table_I=0),
        external_supervision=dict(required=True,sibling_path='results/p4_full/'+RUN+'.supervision.time.txt',format='%e %U %S %x',
            metadata_path='results/p4_full/'+RUN+'.supervision.jsonl',stderr_path='results/p4_full/'+RUN+'.supervision.stderr.log',
            charge_path='results/p4_full/'+RUN+'.supervision.charge.json',time_binary_sha256=sha('/usr/bin/time'),python_binary_sha256=sha('/usr/bin/python3'),
            elapsed_decimal_upper_padding_s=.01,CPU_user_plus_system_upper_padding_s=.02,final_independent_POST_required=True),
        scope='Full original true dense M only: original math closure/limits/per-edge passive branch and v3 aligned discrete source collision; native kept separately. No CCD/solid-rod/omitted-pair/PCS-advantage claim.',
        resource_policy='Complete unique original queue, at most2048; above cap blocks science without truncation. No second source solve or RBS, no node replacement, retry/reset/resume.',
        no_retry_reset_resume=True)

def validate(spec,protocol,execute=False):
    expected=draft_protocol()
    require(set(spec)==set(expected)and all(spec[k]==v for k,v in expected.items()if k not in('frozen','reviews')),'EXACT_CURRENT_FULL_CBIRRT_SAVED_QUEUE_AND_PRIOR_REQUIRED')
    require(type(spec['frozen'])is bool and set(spec['reviews'])==set(expected['reviews'])and all(type(v)is bool for v in spec['reviews'].values()),'EXPLICIT_P_REVIEW_FIELDS_REQUIRED')
    if not execute:return None
    require(spec['frozen']and all(spec['reviews'].values()),'P_INDEPENDENT_REVIEW_ROOT_COMPLETE_QUEUE_FREEZE_REQUIRED')
    require(spec['full_queue_node_count']<=MAX_NODES and spec['fixed_queue']['under_2048_full_queue_cap']is True,'COMPLETE_QUEUE_OVER2048_NO_PHYSICAL_QUERY')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for n in[*OWN,str(protocol.relative_to(ROOT))]:
        require(subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT)==path(n).read_bytes(),'UNCOMMITTED_P_SOURCE_OR_PROTOCOL '+n)
    return commit

class Budget(old.Budget):
    def __init__(self,spec,begun,cpu_start):
        super().__init__(spec,begun,cpu_start)
        self.wall_cap=min(120.,3600.-spec['previous_r2_wall_s']);self.cpu_cap=min(240.,7200.-spec['previous_r2_cpu_s'])
        require(min(self.wall_cap,self.cpu_cap)>0,'P_TOTAL_BUDGET_EXHAUSTED')

# Actual parent/argv/exclusive time-inode proof has the same function body as S;
# its globals resolve to this independently versioned P runner/supervisor.
def supervisor_proof(spec,protocol):
    ext=spec['external_supervision'];metadata=path(ext['metadata_path'])
    planned_raw=metadata.read_bytes().splitlines(keepends=True)[0];planned=json.loads(planned_raw)
    parent=os.getppid();row=old.stat_row(parent)
    require(row is not None and int(row[1])==planned['supervisor_pid'],'EXACT_SUPERVISOR_PARENT_CHAIN_REQUIRED')
    require(planned['event']=='planned_launch'and planned['run_id']==RUN and planned['protocol_sha256']==sha(protocol)
        and planned['runner_sha256']==sha(__file__)and planned['supervisor_source_sha256']==sha(SUPERVISOR),'EXACT_SUPERVISOR_SOURCE_PROTOCOL_REQUIRED')
    require(sha(Path('/proc',str(parent),'exe'))==ext['time_binary_sha256'],'ACTUAL_PARENT_GNU_TIME_REQUIRED')
    expected=['/usr/bin/time','--quiet','-f',ext['format'],'-o',f"/proc/self/fd/{planned['time_fd']}",'/usr/bin/python3',str(Path(__file__).resolve()),'--protocol',str(protocol)]
    require(Path('/proc',str(parent),'cmdline').read_bytes().rstrip(b'\0').split(b'\0')==[v.encode()for v in expected]
        and planned['argv']==expected,'ACTUAL_TIME_ARGV_MISMATCH')
    sibling=path(ext['sibling_path']).stat();held=[]
    for p in Path('/proc',str(parent),'fd').iterdir():
        try:
            s=p.stat()
            if(s.st_ino,s.st_dev)==(sibling.st_ino,sibling.st_dev):held.append(int(p.name))
        except FileNotFoundError:pass
    require(held and sibling.st_ino==planned['time_inode']and sibling.st_dev==planned['time_device'],'EXCLUSIVE_SUPERVISION_INODE_MISMATCH')
    return dict(actual_time_pid=parent,actual_time_start_ticks=int(row[19]),supervisor_pid=planned['supervisor_pid'],
        actual_argv=expected,planned_launch_line_sha256=hashlib.sha256(planned_raw).hexdigest(),
        time_inode=sibling.st_ino,time_device=sibling.st_dev,actual_time_output_fds=sorted(held),external_POST_required=True)

def execute(spec,protocol):
    raise RuntimeError('P_EXECUTION_BODY_PENDING_ACTUAL_S_SAVED_QUEUE_AND_REVIEW_NO_SCIENCE')

def main():
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--describe-protocol',action='store_true');group.add_argument('--validate-draft',type=Path);group.add_argument('--protocol',type=Path)
    args=parser.parse_args()
    if args.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    protocol=(args.validate_draft or args.protocol).resolve();spec=load(protocol)
    if args.validate_draft:validate(spec,protocol);print('STATIC_P_DRAFT_VALIDATED_NO_EXECUTION');return
    execute(spec,protocol)

if __name__=='__main__':main()
