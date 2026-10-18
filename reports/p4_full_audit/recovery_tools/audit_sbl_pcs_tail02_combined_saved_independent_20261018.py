#!/usr/bin/env python3
"""TAIL02 saved-only125 audit plus exact independent262 prefix reuse.

No runner/model import, compilation, FK/J/IK/NR/PQP/RBS/solve/RNG call.
Original physical saved-node checking body is reused; prefix is not re-audited.
"""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
import argparse
import ast
import base64
import datetime
import hashlib
import json
import math
import struct
import subprocess
import sys
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN_ID='20261018_R2_ABB_SBL_PCS_PATH_TAIL02'
RUN=Path('results/p4_full')/RUN_ID
STATIC='reports/P4_FULL_R2_ABB_SBL_PCS_PATH_TAIL02_INDEPENDENT_STATIC_REVIEW_20261018.json'
STATIC_SHA='cfdf761a4d715fd0a2243aa87fc1dd6bc7e01ddfc6c4308a5e838cb7130e5041'
PREFIX='reports/P4_FULL_R2_ABB_SBL_PCS_PATH01_PREFIX_SAVED_INDEPENDENT_POST_ADDENDUM_20261018.json'
PREFIX_SHA='e2fb37a5d63e5219395baedef7630c386893ea13aa07e9bcc0777aa8316b75b4'
PREFIX_EXEC='results/p4_full/20261018_R2_ABB_SBL_PCS_PATH01/execution.json'
PREFIX_EXEC_SHA='cee39aae1538742e1ab54e19d28ff42a8de2c4165cf2511bb1477d69847bc1e0'
COLLISION='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
RUNNER='scripts/qualify_p4_full_r2_abb_sbl_pcs_path_tail02_draft.py'
SUPERVISOR='scripts/supervise_p4_full_r2_abb_sbl_pcs_path_tail02_draft.py'
OUT='reports/P4_FULL_R2_ABB_SBL_PCS_PATH_TAIL02_COMBINED_SAVED_INDEPENDENT_POST_20261018.json'
BASIS='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
groups = defaultdict(lambda: {'total': 0, 'passed': 0})
checks = []
retained = {}


def path(name):
    p = Path(name)
    return p if p.is_absolute() else ROOT/p


def label(name):
    p = path(name)
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def raw(name):
    b = path(name).read_bytes()
    h = hashlib.sha256(b).hexdigest()
    old = retained.setdefault(label(name), h)
    ck('preservation', 'same read SHA '+label(name), old == h)
    return b


def sha(name):
    return hashlib.sha256(raw(name)).hexdigest()


def read(name):
    return json.loads(raw(name))


def ck(group, description, ok):
    ok = bool(ok)
    groups[group]['total'] += 1
    groups[group]['passed'] += ok
    checks.append(dict(group=group, check=description, passed=ok))
    return ok


def exact(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if type(a) in (int, float) and type(b) in (int, float):
        return struct.pack('>d', a) == struct.pack('>d', b)
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return set(a) == set(b) and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def bits(q):
    return struct.pack('>12d', *q)


def jsonlines(name):
    b = raw(name)
    ck('raw', label(name)+' newline terminated', not b or b.endswith(b'\n'))
    return [json.loads(line) for line in b.splitlines()]


def finite_matrix(pose, rows=4, cols=4):
    return (isinstance(pose, list) and len(pose) == rows and
            all(isinstance(row, list) and len(row) == cols and
                all(type(v) in (int, float) and math.isfinite(v) for v in row) for row in pose))


def same_float(a, b, tolerance=1e-12):
    return math.isfinite(a) and math.isfinite(b) and abs(a-b) <= tolerance


def audit(expected_commit):
    e=read(RUN/'execution.json');p=read(e['protocol']);c=read(e['claim']);s=read(STATIC);prefix=read(PREFIX)
    ck('static','exact incremental58 independent PASS reused',sha(STATIC)==STATIC_SHA and s['personnel_independent'] is True and s['checks_total']==s['checks_passed']==58 and s['checks_failed']==0 and s['new_runner_model_import_scientific_compile_describe_calls']==0)
    for name in (RUNNER,SUPERVISOR):
        ast.parse(raw(name),filename=name)
        ck('static','same reviewed current tail source '+name,sha(name)==s['reviewed_sha256'][name])
    ck('prefix','exact independent262 certificate reused without physical repeat',sha(PREFIX)==PREFIX_SHA and prefix['schema']=='P4_SBL_PCS_PATH01_PREFIX_SAVED_INDEPENDENT_POST_ADDENDUM_V1' and prefix['personnel_independent'] is prefix['saved_prefix_qualified'] is prefix['partial_path_prefix_qualified'] is True and prefix['checks_total']==prefix['checks_passed']==35 and prefix['checks_failed']==0 and prefix['independently_saved_qualified_nodes']==262 and prefix['independent_prefix_node_ids']==prefix['independently_saved_qualified_node_ids']==list(range(262)) and prefix['remaining_unverified_node_ids']==list(range(262,387)) and prefix['independent_path_qualified'] is False and prefix['execution_cap_breach_retained'] is True and prefix['scientific_run_within_local_budget'] is False)
    pe=read(PREFIX_EXEC)
    ck('prefix','original STOP261 final and262 saved collision responses unchanged',sha(PREFIX_EXEC)==PREFIX_EXEC_SHA==prefix['execution_sha256'] and pe['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET' and pe['completed_nodes']==pe['qualified_nodes']==261 and pe['counts']['collision_calls_completed']==262 and pe['full_queue_checked'] is False)
    ck('metadata','exact tail run unique expected committed source',e['schema']=='P4_R2_ABB_SBL_PCS_PATH_TAIL02_EXECUTION_V1' and e['run_id']==p['run_id']==c['run_id']==RUN_ID and e['classification']==p['classification']=='R2_CORRECTED_SBL_PCS_RECONSTRUCTED_A01_SAVED_PREFIX_PLUS_ORIGINAL_TAIL' and e['source_commit']==c['source_commit']==expected_commit)
    ck('metadata','committed frozen protocol three explicit true reviews',p['frozen'] is True and set(p['reviews'])=={'independent_static_review_passed','root_complete_queue_freeze_approved','latest_actual_prior_confirmed'} and all(v is True for v in p['reviews'].values()))
    ck('metadata','protocol claim exact before after no retry',sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256'] and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'] and c['no_retry_reset_resume'] is True)
    for name in [*p['own_source_sha256'],e['protocol']]:
        committed=subprocess.check_output(['git','show',expected_commit+':'+name],cwd=ROOT)
        ck('provenance','frozen committed current bytes '+name,hashlib.sha256(committed).hexdigest()==p['own_source_sha256'].get(name,e['protocol_sha256'])==sha(name))
    ck('provenance','bound map exact before and after',p['bound_files_sha256']==e['bound_files_sha256']==e['bound_files_after_sha256'])
    for name,want in p['bound_files_sha256'].items():ck('provenance','bound bytes '+name,sha(name)==want)
    for name,want in e['retained_run_files_sha256'].items():ck('provenance','retained tail bytes '+name,sha(name)==want)
    ck('prefix','provenance exactly binds independent prefix and no prefix query',exact(e['prefix_provenance'],p['prefix_provenance']) and p['prefix_provenance']['independent_POST']==PREFIX and p['prefix_provenance']['independent_POST_sha256']==PREFIX_SHA and p['prefix_provenance']['execution_sha256']==PREFIX_EXEC_SHA and p['prefix_provenance']['independently_saved_qualified_node_ids']==list(range(262)) and p['prefix_provenance']['new_physical_queries_for_prefix']==0 and p['prefix_provenance']['original_stop_retained'] is True)
    q=p['fixed_queue'];nodes=q['nodes'];edges=q['edges'];tail=list(range(262,387));n=len(tail)
    originalq=read(prefix['source_full_queue'])
    ck('queue','exact original complete387 queue reused by independent SHA',sha(prefix['source_full_queue'])==prefix['source_full_queue_sha256'] and exact(q,originalq) and exact(q,read(RUN/'complete_original_saved_queue.json')) and len(nodes)==p['full_queue_node_count']==e['original_full_queue_node_count']==387 and len({bits(x)for x in nodes})==387 and len(edges)==5)
    ck('queue','prefix262 and tail125 exhaust fixed387 with no overlap',p['execution_node_ids']==e['execution_node_ids']==tail and p['execution_node_count']==e['node_count']==n==125 and prefix['independent_prefix_node_ids']+tail==list(range(387)) and not set(prefix['independent_prefix_node_ids'])&set(tail))
    ck('complete','tail original IDs125 all qualified without promoting original STOP',e['completed_nodes']==e['qualified_nodes']==125 and e['completed_original_node_ids']==tail and e['uncompleted_node_ids']==[] and e['full_tail_checked'] is True and e['full_queue_checked'] is False and e['status']=='PASS_DISCRETE_SOURCE_POLICY_TAIL262_386_PENDING_COMBINED_POST' and e['diagnostics']==[])
    ck('queue','unchanged scientific gates and fixed tail caps',p['gates']==dict(position_maxabs_mm=1e-5,rotation_matrix_maxabs=1e-5,strict_leaf_full12_L2_rad=.05,branch_zero_relative_epsilon=64*sys.float_info.epsilon) and p['budget']==dict(wall_s=90.,cpu_s=180.,work_wall_s=80.,work_cpu_s=160.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.) and p['max_math_arm_FK']==250 and p['max_collision_calls']==125 and p['max_adapter_internal_arm_FK_J']==500)
    expected_assignments=defaultdict(list)
    for k,edge in enumerate(edges):
        for i in set(edge['node_ids']):expected_assignments[i].append((k,edge['active_chain'],edge['branch']))
    events = jsonlines(RUN/'events.jsonl')
    ck('events', 'complete events file exact recorded SHA', sha(RUN/'events.jsonl') == e['events_sha256'] and e['events'] == str(RUN/'events.jsonl'))
    event_by = defaultdict(list)
    for ev in events:
        event_by[ev['event']].append(ev)
    ck('events', 'setup and final counts complete no stopped event', len(event_by['setup']) == len(event_by['final_counts']) == 1 and
       not event_by['stopped'] and event_by['final_counts'][0]['counts'] == e['counts'] and event_by['final_counts'][0]['diagnostics'] == [])
    manifest = read(COLLISION)
    entries = {v['variant']:v for v in manifest['entries'] if v['model'] == 'abb'}
    ck('collision', 'collision v3 both exact frozen successful builds', manifest['schema'] == 'P4_COLLISION_ADAPTER_ENGINEERING_BUILD_V3' and
       set(entries) == {'native','aligned'} and all(v['exit_code'] == 0 for v in entries.values()) and
       sha(COLLISION) == p['bound_files_sha256'][COLLISION])
    max_pos = max_rot = 0.
    minimum_margin = math.inf
    pqp = 0
    native_collision_nodes = aligned_collision_nodes = 0
    branch_sets = set()
    bounds = [(lo*3.1416/180., hi*3.1416/180.) for lo,hi in [(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)]]*2
    ELBOW = (1,-1,1,-1,1,-1,1,-1)
    WRIST = (1,-1,-1,1,-1,1,1,-1)
    for i in tail:
        inputq=nodes[i]
        final = RUN/f'node_{i:05d}.json'
        if not path(final).is_file():
            ck('complete', 'required final node'+str(i)+' exists', False)
            continue
        r = read(final)
        a1 = read(RUN/f'node_{i:05d}_arm1.json')
        a2 = read(RUN/f'node_{i:05d}_arm2.json')
        mr = read(RUN/f'node_{i:05d}_math.json')
        cr = read(RUN/f'node_{i:05d}_collision_response.json')
        ck('node', str(i)+' input bits exact fully qualified', r['node_id'] == i and bits(r['q12']) == bits(inputq) and
           r['stage'] == 'COMPLETED' and r['qualified'] is r['math_qualified'] is True)
        ck('node', str(i)+' original FK saved snapshots exact', a1['node_id'] == a2['node_id'] == mr['node_id'] == i and
           exact(a1['q12'], inputq) and exact(a2['q12'], inputq) and exact(a1['poses'], r['poses'][:1]) and exact(a2['poses'], r['poses']) and
           len(r['poses']) == 2 and all(finite_matrix(t) and t[3] == [0.,0.,0.,1.] for t in r['poses']))
        ck('node', str(i)+' math and raw collision retained before result', all(exact(mr[k], r[k]) for k in
           ('q12','poses','branches','closure','limits','edge_assignments','math_qualified')) and exact(cr,r['collision']))
        pose1, pose2 = r['poses']
        cp = max(abs(pose2[j][3]-(pose1[j][3]+300.*pose1[j][0])) for j in range(3))
        ct = max(abs(pose2[j][k]-pose1[j][k]*(-1. if k < 2 else 1.)) for j in range(3) for k in range(3))
        ck('math', str(i)+' saved FK closure original300mm grasp FLIP', same_float(cp,r['closure']['position_max_abs'],1e-10) and
           same_float(ct,r['closure']['rotation_matrix_max_abs']) and cp <= 1e-5 and ct <= 1e-5)
        max_pos, max_rot = max(max_pos,cp), max(max_rot,ct)
        margins = [min(v-lo,hi-v) for v,(lo,hi) in zip(inputq,bounds)]
        minimum_margin = min(minimum_margin,*margins)
        ck('math', str(i)+' all original limits literal3.1416 without wrapping', all(v >= 0 for v in margins) and
           r['limits'] == dict(legal=True,violations=[],source_literal_pi_preserved=3.1416,planar_q19_policy=None))
        for arm,b in enumerate(r['branches']):
            epsilon = p['gates']['branch_zero_relative_epsilon']
            signed = lambda v,scale: None if abs(v) <= epsilon*scale else (1 if v > 0 else -1)
            rs = signed(b['signed_shoulder_radius_mm'],270.+math.hypot(70.,302.))
            es = signed(b['elbow_factor'],1.)
            ws = signed(b['wrist_factor'],1.)
            expected = [z for z in range(8) if (rs is None or (1 if z < 4 else -1) == rs) and
                        (es is None or ELBOW[z] == es) and (ws is None or WRIST[z] == ws)]
            ck('branch', str(i)+' arm'+str(arm+1)+' saved invariants zero rule and branch set',
               b['shoulder_sign'] == rs and b['elbow_sign'] == es and b['wrist_sign'] == ws and
               b['branch_set'] == expected and b['unique'] is all(v is not None for v in (rs,es,ws)))
            branch_sets.add(tuple(expected))
        ck('branch', str(i)+' every incident edge passive role branch enforced',
           [(a['edge'],a['role'],a['requested_branch']) for a in r['edge_assignments']] == expected_assignments[i] and
           bool(r['edge_assignments']) and all(a['branch_pass'] is True and a['requested_branch'] in r['branches'][1-a['role']]['branch_set'] for a in r['edge_assignments']))
        collision = r['collision']
        ck('collision', str(i)+' exact aligned policy collision false retained both variants', collision['status'] == 'CHECKED' and
           collision['environment'] == 'II' and collision['scope'] == 'AUTHOR_DISCRETE_COLLISION_POLICY' and
           collision['collision'] is False and collision['selected_variant'] == 'aligned' and
           collision['continuous_collision_certificate'] is False and set(collision['variants']) == {'native','aligned'} and
           collision['manifest_sha256'] == p['bound_files_sha256'][COLLISION])
        for variant, row in collision['variants'].items():
            ent = entries[variant]
            lines = row['source_stdout'].splitlines(keepends=True)
            terminal = [line for line in lines if line.startswith('P4_COLLISION_RESULT ')]
            native = json.loads(terminal[0].split(' ',1)[1]) if len(terminal) == 1 else {}
            ck('collision_raw', str(i)+' '+variant+' unique original raw JSON exact', len(terminal) == 1 and
               lines[-1] == terminal[0] and terminal[0].endswith('\n') and all(exact(row[k],v) for k,v in native.items()) and
               {'native_result','cpu_s','poses','query_codes'} <= set(native) and row['source_stderr'] == 'merged into source_stdout')
            ck('collision_raw', str(i)+' '+variant+' frozen build mesh pair provenance', row['source_command'] == [ent['binary'],'II'] and
               row['provenance'] == {k:ent[k] for k in ('source_root','source_commit','source_files_sha256','mesh_sha256','binary_sha256','physical_alignment_changes')})
            codes = row['query_codes']
            pqp += len(codes)
            ck('collision_raw', str(i)+' '+variant+' all original PQP query codes zero', bool(codes) and
               all(type(v) is int and v == 0 for v in codes) and row['query_error_codes'] == [] and
               type(row['native_result']) is int and row['native_result'] in (0,1) and row['native_collision'] is bool(row['native_result']))
            pc = row['pose_consistency']
            errors = pc['errors']
            for arm, er in enumerate(errors):
                tcp = [row['poses'][arm][j:j+4] for j in (0,4,8)]
                independent = er['independent_TCP']
                dp = max(abs(tcp[j][3]-independent[j][3]) for j in range(3))
                dr = max(abs(tcp[j][k]-independent[j][k]) for j in range(3) for k in range(3))
                ck('collision_TCP', str(i)+' '+variant+' arm'+str(arm+1)+' saved query FK/J capture and residual',
                   er['arm'] == arm+1 and exact(er['collision_TCP'],tcp) and finite_matrix(independent,3,4) and
                   same_float(dp,er['translation_maxabs_mm']) and same_float(dr,er['rotation_maxabs']))
            ck('collision_TCP', str(i)+' '+variant+' exact saved TCP pass criterion', len(errors) == 2 and
               pc['position_gate_mm'] == pc['rotation_matrix_gate'] == 1e-5 and pc['passed'] is all(
                   er['translation_maxabs_mm'] <= 1e-5 and er['rotation_maxabs'] <= 1e-5 for er in errors))
            if variant == 'native':
                native_collision_nodes += bool(row['native_collision'])
            else:
                aligned_collision_nodes += bool(row['native_collision'])
                ck('collision', str(i)+' aligned TCP physically consistent no collision', pc['status'] == 'PASS' and
                   pc['passed'] is True and row['native_collision'] is False)
        for name, expected in [('math_node_started',1),('math_node_completed',1),('math_arm_FK_started',2),('math_arm_FK_completed',2),
                               ('collision_started',1),('collision_response_retained',1),('node_completed',1)]:
            evs = [v for v in event_by[name] if v['node_id'] == i]
            ck('events', str(i)+' '+name+' exact event count', len(evs) == expected)
        start = [v for v in event_by['math_node_started'] if v['node_id'] == i]
        finish = [v for v in event_by['math_arm_FK_completed'] if v['node_id'] == i]
        col = [v for v in event_by['collision_response_retained'] if v['node_id'] == i]
        ck('events', str(i)+' original q FK poses collision raw exactly journaled', len(start) == 1 and
           bits(start[0]['q12']) == bits(inputq) and [v['arm'] for v in finish] == [1,2] and
           exact([v['pose'] for v in finish],r['poses']) and len(col) == 1 and exact(col[0]['response'],collision))
    counts = e['counts']
    expected_counts = dict(collision_worker_start_attempted=2,collision_worker_started=2,
        math_arm_FK_started=2*n,math_arm_FK_completed=2*n,branch_identity_started=2*n,branch_identity_completed=2*n,
        collision_calls_started=n,collision_calls_completed=n,adapter_internal_arm_FK_J_started=4*n,
        adapter_internal_arm_FK_J_completed=4*n,PQP_queries=pqp)
    ck('counts', 'actual complete physical counters exact no hidden extra', counts == expected_counts)
    ck('events', 'all original adapter counted FK/J starts returns complete', len(event_by['adapter_internal_FK_J_started']) ==
       len(event_by['adapter_internal_FK_J_completed']) == 4*n)
    wanted = []
    for v in [nodes[i] for i in tail]:
        wanted.extend([(arm+1,v[arm*6:arm*6+6]) for _ in ('native','aligned') for arm in range(2)])
    actual = [(v['arm'],v['q6']) for v in event_by['adapter_internal_FK_J_started']]
    ck('events', 'both workers per query original FK/J q6 order bits retained', exact(actual, wanted))
    registry, workers = e['collision_worker_registry'], e['collision_worker_evidence']
    ck('worker', 'exact two centrally registered reaped exit0', len(registry) == len(workers) == 2 and
       len({r['pid'] for r in registry}) == 2 and {r['pid'] for r in registry} == {r['pid'] for r in workers} and
       all(r['reaped'] is True and r['returncode'] == 0 for r in registry) and e['complete_collision_worker_cleanup_gate'] is True)
    for w in workers:
        pid = w['pid']
        variant = next(k for k,v in entries.items() if w['command'] == [v['binary'],'II'])
        start_group, close_group = w['start_process_group'], w['close_process_group']
        ck('worker', variant+' both direct singleton process group snapshots', len(start_group) == len(close_group) == 1 and
           start_group[0]['pid'] == start_group[0]['pgrp'] == close_group[0]['pid'] == close_group[0]['pgrp'] == pid and
           start_group[0]['ppid'] == close_group[0]['ppid'] and start_group[0]['ppid'] > 0)
        ck('worker', variant+' actual closed selector drained EOF empty pending tail', w['original_selector_closed'] is True and
           w['pipe_EOF_drained'] is True and base64.b64decode(w['stdout_pending_base64'],validate=True) ==
           base64.b64decode(w['stdout_EOF_tail_base64'],validate=True) == b'')
        for event, field, value in [('collision_worker_started','pid',pid),('collision_worker_start_group','members',start_group),
                                   ('collision_worker_close_group','members',close_group),('collision_worker_after_original_close_group','members',[]),
                                   ('collision_worker_final_raw_tail','pending_base64','')]:
            evs = [r for r in event_by[event] if r['pid'] == pid]
            ck('worker', variant+' journal '+event+' direct evidence', len(evs) == 1 and exact(evs[0][field],value))
    ck('complete', 'no partial stopped files exact all625 tail node files', not list(path(RUN).glob('node_*_stopped_partial.json')) and
       len(list(path(RUN).glob('node_*.json'))) == n*5)
    prior=p['actual_charge_prior'];ledger=read(prior['ledger']);prior_map={r['execution']:r['execution_sha256']for r in ledger['executions']}
    ck('prior','frozen authoritative actual prior exactly retained',sha(prior['ledger'])==prior['ledger_sha256'] and prior_map==prior['execution_sha256']==p['prior_execution_sha256']==e['prior_execution_sha256']==e['prior_execution_after_sha256'] and exact(e['actual_charge_prior'],prior))
    pw=math.fsum(r.get('charged_wall_s',r['wall_s'])for r in ledger['executions']);pc=math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in ledger['executions'])
    ck('prior','same exact frozen upper prior including historical STOP charge',pw==ledger['conservative_r2_sum_wall_s']==prior['wall_s']==p['previous_r2_wall_s']==e['previous_r2_wall_s'] and pc==ledger['conservative_r2_sum_cpu_s']==prior['cpu_s']==p['previous_r2_cpu_s']==e['previous_r2_cpu_s'])
    ck('prior','tail not previously charged and all frozen actual execution SHAs',str(RUN/'execution.json')not in prior_map and all(sha(name)==want for name,want in prior_map.items()))
    ext=p['external_supervision'];tb=raw(ext['sibling_path']);fields=tb.decode().split();elapsed,user,system=(Decimal(x)for x in fields[:3])
    meta=raw(ext['metadata_path']);planned,started,reaped=[json.loads(line)for line in meta.splitlines()];proof=e['supervisor_launch_proof'];charge=read(ext['charge_path']);receipts=jsonlines(RUN/'cost_receipt.jsonl');receipt=receipts[0]
    rawwall=elapsed+Decimal('.01');rawcpu=user+system+Decimal('.02')
    walls=[rawwall,Decimal(str(charge['fallback_observed_outer_wait_wall_s']))+Decimal('.01'),Decimal(str(receipt['wall_s_through_execution_persistence']))+Decimal('.01')]
    cpus=[rawcpu,Decimal(str(charge['fallback_reaped_children_CPU_s']))+Decimal('.02'),Decimal(str(receipt['cpu_s_through_execution_persistence']))+Decimal('.02')]
    uw,uc=float(max(walls)),float(max(cpus));st=path(ext['sibling_path']).stat()
    ck('external','finite complete raw one line exit0',len(tb.splitlines())==1 and tb.endswith(b'\n') and len(fields)==4 and fields[3]=='0' and all(x.is_finite()and x>=0 for x in(elapsed,user,system,*walls,*cpus)))
    ck('external','actual GNUtime supervisor parent argv reap identity',planned['event']=='planned_launch'and started['event']=='time_process_started'and reaped['event']=='time_process_reaped'and started['pid']==reaped['pid']==proof['actual_time_pid']==charge['time_process_pid']and reaped['returncode']==0 and reaped['failure']is None and planned['supervisor_pid']==proof['supervisor_pid'])
    argv=['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(path(RUNNER)),'--protocol',str(path(e['protocol']))]
    ck('external','exclusive held timeFD inode and exact argv',argv==planned['argv']==started['argv']==proof['actual_argv']and st.st_ino==planned['time_inode']==proof['time_inode']and st.st_dev==planned['time_device']==proof['time_device']and planned['time_fd']in proof['actual_time_output_fds']and proof['actual_time_start_ticks']>0 and hashlib.sha256(meta.splitlines(keepends=True)[0]).hexdigest()==proof['planned_launch_line_sha256'])
    ck('external','frozen planned source binary protocol SHAs',planned['run_id']==RUN_ID and planned['protocol_sha256']==e['protocol_sha256']and planned['runner_sha256']==p['own_source_sha256'][RUNNER]and planned['supervisor_source_sha256']==p['own_source_sha256'][SUPERVISOR]and planned['time_binary_sha256']==ext['time_binary_sha256']==sha('/usr/bin/time')and planned['python_binary_sha256']==ext['python_binary_sha256']==sha('/usr/bin/python3'))
    ck('external','original charge time metadata stderr receipt execution exact SHA chain',charge['schema']=='P4_R2_ABB_SBL_PCS_PATH_TAIL02_EXTERNAL_COST_CHARGE_V1'and charge['run_id']==RUN_ID and charge['source_execution']==str(RUN/'execution.json')and charge['execution_sha256']==receipt['execution_sha256']==sha(RUN/'execution.json')and charge['receipt']==str(RUN/'cost_receipt.jsonl')and charge['receipt_sha256']==sha(RUN/'cost_receipt.jsonl')and charge['time_file']==ext['sibling_path']and charge['time_sha256']==sha(ext['sibling_path'])and charge['metadata']==ext['metadata_path']and charge['metadata_sha256']==sha(ext['metadata_path'])and charge['stderr']==ext['stderr_path']and charge['stderr_sha256']==sha(ext['stderr_path'])and charge['time_fields']==fields)
    ck('external','conservative exact Decimal three observation upper envelope',charge['charge_basis']==ext['charge_basis']==BASIS and charge['raw_GNUtime_upper_wall_s']==float(rawwall)and charge['raw_GNUtime_upper_cpu_s']==float(rawcpu)and charge['monotonic_envelope_components']==dict(wall_decimal_s=[str(x)for x in walls],cpu_decimal_s=[str(x)for x in cpus],order=['raw_GNUtime_plus_padding','outer_monotonic_or_reaped_plus_padding','internal_receipt_plus_padding'])and charge['monotonic_envelope_valid']is True and charge['monotonic_envelope_error']is None and exact([charge['wall_s'],charge['cpu_s']],[uw,uc]))
    ck('external','complete successful charge and measured original process exit0',charge['timing_valid']is charge['time_inode_unchanged']is charge['wall_CPU_caps_pass']is charge['completed_process_exit0']is charge['started_attempt']is True and charge['time_returncode']==charge['measured_child_exit']==0 and charge['failure']is None and charge['execution_cap_breach']==dict(wall=False,cpu=False))
    ck('external','whole execution and receipt covered by envelope inside unchanged caps',len(receipts)==1 and receipt['status']==e['status']and 0<=e['wall_s']<=receipt['wall_s_through_execution_persistence']<=uw<=min(90.,3600.-pw)and 0<=e['cpu_s']<=receipt['cpu_s_through_execution_persistence']<=uc<=min(180.,7200.-pc)and receipt['last_receipt_persistence_tail']=='UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'and receipt['external_supervision_qualified']is e['external_supervision_qualified']is charge['external_supervision_qualified']is False)
    ck('scope','zero new generation formal VI and no premature continuous claim',e['zero_calls']==dict.fromkeys(('IK','NR','projection','RBS','solve','RNG','VI_constructions','formal_table_I'),0)and e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and e['independent_path_qualified']is False and e['continuous_collision_certificate']is False and q['independent_path_qualified']is False and q['independent_physical_queries_performed']==0 and q['continuous_collision_certificate']is False)
    scope=read(p['D080_scope']['path'])
    ck('scope','D080 I-V formal0/18000 not authorized and VI archival',sha(p['D080_scope']['path'])==p['D080_scope']['sha256']and scope['allowed_environments']==['I','II','III','IV','V']and scope['VI_future_science_authorized']is False and scope['formal_execution_authorized']is False and scope['formal_table_I_D080']==p['D080_scope']['formal_table_I_D080']==18000 and p['D080_scope']['formal_table_I_original']==22500 and p['D080_scope']['formal_calls']==p['D080_scope']['VI_new_calls']==0)
    for name,h in list(retained.items()):ck('preservation','all saved read bytes retained '+name,hashlib.sha256(path(name).read_bytes()).hexdigest()==h)
    pm=prefix['metrics']
    return dict(execution=str(RUN/'execution.json'),execution_sha256=sha(RUN/'execution.json'),protocol=e['protocol'],protocol_sha256=sha(e['protocol']),source_commit=e['source_commit'],reused_prefix_POST=PREFIX,reused_prefix_POST_sha256=PREFIX_SHA,reused_independent_prefix_nodes=262,newly_saved_tail_nodes=125,combined_node_ids=list(range(387)),nodes=387,leaves=386,edges=5,milestones=6,source_attempt_returns=[True,True,True,True,False,True],source_attempt_nodes=[35,41,185,65,2,65],source_bridge_motion_ids=[32,49],native_connect_motion_id=50,native_connect_role=None,original_PATH01_STOP_preserved=True,original_PATH01_final_nodes=261,prefix_independently_saved_nodes=262,maximum_full12_leaf_rad=pm['maximum_full12_leaf_rad'],maximum_saved_closure_position_mm=max(max_pos,pm['maximum_saved_closure_position_mm']),maximum_saved_closure_rotation=max(max_rot,pm['maximum_saved_closure_rotation']),minimum_source_mechanical_margin_rad=min(minimum_margin,pm['minimum_source_mechanical_margin_rad']),branch_sets_encountered=[list(x)for x in sorted(branch_sets|{tuple(x)for x in pm['branch_sets_encountered']})],native_collision_nodes=native_collision_nodes+pm['native_collision_nodes'],aligned_collision_nodes=aligned_collision_nodes+pm['aligned_collision_nodes'],new_tail_PQP_queries=pqp,combined_actual_saved_raw_PQP_queries=pqp+pm['actual_saved_raw_PQP_queries'],actual_tail_counts=counts,external_time=ext['sibling_path'],external_time_sha256=sha(ext['sibling_path']),external_charge_sha256=sha(ext['charge_path']),internal_receipt_sha256=sha(RUN/'cost_receipt.jsonl'),external_time_fields=fields,charge_basis=BASIS,wall_components_decimal_s=[str(x)for x in walls],cpu_components_decimal_s=[str(x)for x in cpus],upper_wall_s=uw,upper_cpu_s=uc,execution_sample_wall_s=e['wall_s'],execution_sample_cpu_s=e['cpu_s'],previous_charged_wall_s=pw,previous_charged_cpu_s=pc,cumulative_upper_wall_s=math.fsum((pw,uw)),cumulative_upper_cpu_s=math.fsum((pc,uc)))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--expected-source-commit',required=True);parser.add_argument('--output',default=OUT);args=parser.parse_args()
    if path(args.output).exists()or path(args.output).with_suffix('.md').exists():raise FileExistsError('EXCLUSIVE_COMBINED_POST_NO_OVERWRITE')
    details={}
    try:details=audit(args.expected_source_commit)
    except BaseException as exc:ck('audit_completion','complete saved audit without structural exception '+repr(exc),False)
    auditsha=sha(__file__);failures=[x for x in checks if not x['passed']];passed=not failures
    external=bool(groups['external']['total'])and groups['external']['total']==groups['external']['passed']
    report=dict(schema='P4_SBL_PCS_PATH_TAIL02_COMBINED_SAVED_INDEPENDENT_POST_V1',status='PASS_COMPLETE387_DISCRETE_SOURCE_POLICY_SBL_PATH_COMBINED_POST'if passed else'FAIL_SBL_TAIL02_COMBINED_SAVED_POST',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),personnel_independent=True,reviewer='sbl_independent_resume; independent of SBL tail implementation',checks_total=len(checks),checks_passed=sum(x['passed']for x in checks),checks_failed=len(failures),groups=dict(groups),failures=failures,external_supervision_qualified=external,external_timing_qualified=external,completed_process_exit0=external,independent_tail_qualified=passed,independent_path_qualified=passed,continuous_collision_certificate=False,**details,retained_sha256=retained,audit_script_sha256=auditsha,new_runner_model_FK_J_IK_NR_PQP_RBS_solve_RNG_compile_describe_calls=0,prefix_physical_reaudit_calls=0,charge_rule='Replace this TAIL02 internal sample once with the exact three-observation Decimal conservative upper. Historical PATH01 STOP and all prior charges remain unchanged.',limitations=['One original SBL solution with fixed reconstructed A01 endpoints and corrected numerical source, independent discrete aligned source-policy only.','Only125 new tail saved nodes audited;262 prefix nodes reused from exact independent ADDENDUM certificate without physical rerun or prefix raw re-audit.','Original PATH01 STOP261 final and262 saved qualified physical points remain distinct; original budget breach and original cache first FAIL remain preserved.','Original false final role0 attempt M2 remains failed; role1/branch3 M65 fallback and actual32to49 bridge retained; natural connect50 a_chain null.','Original native TCP mismatch remains separate; no continuous CCD, solid rod, omitted mesh pair, RSS global path, PCS advantage or statistical success-rate proof.','Conservative whole-child envelope covers time runner+reaped workers and persistence receipt; final supervisor own journal/fsync tail excluded.','D080 I-V retained, VI974/974 archival; formal0/18000 and original0/22500 separate. No P2/Isaac.'])
    with path(args.output).open('x')as stream:json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
    with path(args.output).with_suffix('.md').open('x')as stream:
        stream.write('# SBL PCS 尾段与原前缀组合人员独立 POST\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'，失败'+str(report['checks_failed'])+'。\n\n只检查125个新保存尾点；复用262点独立前缀证书，完整原387节点/386叶，原PATH01 STOP及帽超限永久保留。本审查无模型、FK/J、IK/NR、碰撞、规划、编译、describe调用。\n\n独立完整离散路径资格='+str(passed)+'，外层保守费用资格='+str(external)+'。不证明连续碰撞、正式统计或PCS优势。\n\n'+json.dumps(details,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k]for k in('status','checks_total','checks_passed','checks_failed','external_supervision_qualified','independent_path_qualified')},ensure_ascii=False));raise SystemExit(0 if passed else 2)

if __name__=='__main__':main()
