#!/usr/bin/env python3
"""Personnel-independent saved-only P audit; stdlib and read-only git only.

No runner/model import, compilation, FK/J/IK/NR/PQP/RBS/solve/RNG call.
All arithmetic below uses already saved arrays, matrices and scalar factors.
Output uses exclusive creation.  Run only after the single frozen P has ended.
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

ROOT = Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN_ID = '20261018_R2_ABB_SBL_PCS_PATH01'
RUN = Path('results/p4_full')/RUN_ID
SOURCE = Path('results/p4_full/20261017_R2_ABB_SBL_PCS_SOLVE01')
STATIC = 'reports/P4_FULL_R2_ABB_SBL_PCS_PATH_INDEPENDENT_STATIC_REVIEW_20261018.json'
STATIC_SHA = '1896714d85a154d760d3266581641e271109ee7d7be9cd6dd4b120dd781a5979'
SOURCE_POST = 'reports/P4_FULL_R2_ABB_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST_20261017.json'
SOURCE_POST_SHA = 'fea6f01839a041430d10da796a0c7a59bd65dbf4bcf7487dc8c27a7c15358066'
SOURCE_EXEC_SHA = '2867a03699b8901c9e065bbcc1993a9ac14a7f624232f29ed603df89c1d09208'
COLLISION = '/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json'
RUNNER = 'scripts/qualify_p4_full_r2_abb_sbl_pcs_path_draft.py'
SUPERVISOR = 'scripts/supervise_p4_full_r2_abb_sbl_pcs_path_draft.py'
OUT = 'reports/P4_FULL_R2_ABB_SBL_PCS_PATH01_SAVED_INDEPENDENT_POST_20261018.json'
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
    e=read(RUN/'execution.json');p=read(e['protocol']);c=read(e['claim']);s=read(STATIC)
    ck('static','exact incremental static62 PASS',sha(STATIC)==STATIC_SHA and s['status']=='PASS_SBL_COMPLETE_SAVED_QUEUE_AND_INCREMENTAL_STATIC_REVIEW' and s['personnel_independent'] is True and s['checks_total']==s['checks_passed']==62 and s['checks_failed']==0 and s['runner_import_calls']==s['new_model_or_scientific_calls']==s['new_compile_calls']==0)
    for name,want in s['reviewed_sha256'].items():ck('static','reviewed immutable '+name,sha(name)==want)
    for name in (RUNNER,SUPERVISOR,'scripts/materialize_p4_full_r2_abb_sbl_pcs_path_draft.py'):ast.parse(raw(name),filename=name)
    ck('metadata','exact unique SBL path and source commit',e['schema']=='P4_R2_ABB_SBL_PCS_PATH_EXECUTION_V1' and e['run_id']==p['run_id']==RUN_ID and e['classification']==p['classification']=='R2_CORRECTED_SBL_PCS_RECONSTRUCTED_A01_DISCRETE_SOURCE_POLICY_PATH' and e['source_commit']==c['source_commit']==expected_commit)
    ck('metadata','committed frozen protocol three reviews',p['frozen'] is True and set(p['reviews'])=={'independent_static_review_passed','root_complete_queue_freeze_approved','latest_actual_prior_confirmed'} and all(v is True for v in p['reviews'].values()))
    ck('metadata','protocol/claim before-after immutable',sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256'] and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'] and c['run_id']==RUN_ID and c['no_retry_reset_resume'] is True)
    for name in [*p['own_source_sha256'],e['protocol']]:
        b=subprocess.check_output(['git','show',expected_commit+':'+name],cwd=ROOT)
        ck('provenance','committed frozen source/protocol '+name,hashlib.sha256(b).hexdigest()==p['own_source_sha256'].get(name,e['protocol_sha256'])==sha(name))
    ck('provenance','complete frozen source bound maps',p['bound_files_sha256']==e['bound_files_sha256']==e['bound_files_after_sha256'])
    for name,want in p['bound_files_sha256'].items():ck('provenance','bound asset '+name,sha(name)==want)
    for name,want in e['retained_run_files_sha256'].items():ck('provenance','retained run file '+name,sha(name)==want)
    ck('provenance','source provenance immutable',exact(e['source_provenance'],p['source_provenance']))
    se=read(SOURCE/'execution.json');spost=read(SOURCE_POST)
    ck('source','reuse immutable independent solve111 without rerun',sha(SOURCE/'execution.json')==SOURCE_EXEC_SHA and sha(SOURCE_POST)==SOURCE_POST_SHA and spost['personnel_independent'] is spost['solve_transport_qualified'] is spost['external_supervision_qualified'] is True and spost['checks_total']==spost['checks_passed']==111 and spost['checks_failed']==0 and spost['independent_path_qualified'] is False)
    sb=raw(SOURCE/'request_00_stdout.bin');ck('source','one exact saved stdout response',len(sb.splitlines())==1 and sb.endswith(b'\n'))
    d=json.loads(sb);ck('source','source exact single fixed II A01 request',d['exact'] is True and d['solution_count']==1 and exact(d,se['responses'][0]) and exact(d['request'],p['source_provenance']['request']) and d['request']['environment']=='II' and d['independent_path_qualified'] is False)
    stack=[];attempts=[];mpaths=None
    for row in d['trace']:
        if row['event']=='entered':stack.append(row)
        elif row['event']=='completed':
            entered=stack.pop();ck('source_trace','balanced original id'+str(row['id']),(entered['id'],entered['kind'])==(row['id'],row['kind']))
            if row['kind']=='state_reconstruct':
                a=entered['args'];attempts.append(dict(attempt_index=len(attempts),trace_entry_id=entered['id'],trace_return_id=row['id'],qa12=a['qa12'],qb12=a['qb12'],active_chain=a['active_chain'],branch=a['branch'],returned=row['result']['returned'],path_q12=row['result']['path_q12']))
        elif row['event']=='observed' and row['kind']=='save_source_mpaths':mpaths=row['args']['source_mpaths']
    ck('source','complete original trace and real saved mpaths',not stack and mpaths is not None)
    q=p['fixed_queue'];nodes=q['nodes'];edges=q['edges'];n=len(nodes)
    ck('queue','entire frozen387 unique queue retained',exact(q,read(RUN/'complete_original_saved_queue.json')) and n==len({bits(v) for v in nodes})==387 and n==q['full_queue_node_count']==p['full_queue_node_count']==e['node_count'] and len(edges)==5 and q['under_2048_full_queue_cap'] is True)
    ck('queue','all six original attempts including failed last role0 retained',exact(attempts,q['all_original_attempts']) and [a['returned'] for a in attempts]==[True,True,True,True,False,True] and [len(a['path_q12']) for a in attempts]==[35,41,185,65,2,65] and [a['trace_entry_id'] for a in attempts]==[11112,11312,11548,12648,13028,13033])
    identity=q['source_identity_audit'];ordered=list(reversed(mpaths[0]))+mpaths[1]
    ck('queue','actual path identities bridge and unknown connect preserved',identity['source_motion_path']==[v['motion_id'] for v in ordered]==[1,7,32,49,3,2] and identity['source_state_path']==[v['state_id'] for v in ordered] and identity['source_address_generations']==[v['address_generation'] for v in ordered] and identity['source_bridge_motion_ids']==[32,49] and identity['source_bridge_milestone_edge_index']==2 and identity['native_connect_motion_id']==50 and identity['native_connect_role'] is None and identity['complete_tree_motion_count']==23)
    ck('queue','all source milestone q bytes and A01 endpoints',exact([v['q12'] for v in ordered],d['milestones_q12']) and bits(nodes[0])==bits(d['request']['start_q12']) and bits(nodes[-1])==bits(d['request']['goal_q12']))
    expected_assignments=defaultdict(list);full_leaves=[];refs=[];dense_ids=[]
    for i,edge in enumerate(edges):
        attempt=attempts[edge['selected_attempt_index']];dense=[nodes[k] for k in edge['node_ids']]
        ck('queue','edge'+str(i)+' exact entire true original dense M',attempt['returned'] is True and exact(dense,attempt['path_q12']) and edge['active_chain']==attempt['active_chain'] and edge['branch']==attempt['branch'] and edge['edge_index']==i and bits(edge['qa12'])==bits(d['milestones_q12'][i])==bits(dense[0]) and bits(edge['qb12'])==bits(d['milestones_q12'][i+1])==bits(dense[-1]) and edge['qa_motion_id']==ordered[i]['motion_id'] and edge['qb_motion_id']==ordered[i+1]['motion_id'])
        leaves=[math.sqrt(math.fsum((x-y)**2 for x,y in zip(a,b))) for a,b in zip(dense,dense[1:])]
        ck('queue','edge'+str(i)+' every strict full12 leaf',exact(leaves,edge['leaf_distances_rad']) and all(v<.05 for v in leaves))
        for k in set(edge['node_ids']):expected_assignments[k].append((i,edge['active_chain'],edge['branch']))
        refs.extend(edge['node_ids']);dense_ids.extend(edge['node_ids'] if not dense_ids else edge['node_ids'][1:]);full_leaves.extend(leaves)
    ck('queue','all387 physical nodes391refs386leaves exact original fallback',set(refs)==set(range(n)) and len(refs)==391 and len(full_leaves)==386 and [v['selected_attempt_index'] for v in edges]==[0,1,2,3,5] and [v['consumed_attempt_indices'] for v in edges]==[[0],[1],[2],[3],[4,5]] and [v['edge_kind'] for v in edges]==['start_parent_to_child','start_parent_to_child','actual_cross_tree_bridge','goal_child_to_parent','goal_child_to_parent'] and dense_ids==q['original_dense_node_ids'] and len(dense_ids)==q['original_dense_path_node_count']==387)
    ck('queue','unchanged physical gates caps and full resource maxima',p['gates']==dict(position_maxabs_mm=1e-5,rotation_matrix_maxabs=1e-5,strict_leaf_full12_L2_rad=.05,branch_zero_relative_epsilon=64*sys.float_info.epsilon) and p['budget']==dict(wall_s=120.,cpu_s=240.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.) and p['max_math_arm_FK']==774 and p['max_collision_calls']==387 and p['max_adapter_internal_arm_FK_J']==1548 and p['max_nodes_per_execution']==2048)
    ck('complete','entire physical queue completed qualified',e['completed_nodes']==e['qualified_nodes']==n and e['uncompleted_node_ids']==[] and e['full_queue_checked'] is True and not e['diagnostics'] and e['status']=='PASS_DISCRETE_SOURCE_POLICY_START_TO_GOAL_PATH')
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
    for i, inputq in enumerate(nodes):
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
    for v in nodes:
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
    ck('complete', 'no partial stopped files exact all1935 node files', not list(path(RUN).glob('node_*_stopped_partial.json')) and
       len(list(path(RUN).glob('node_*.json'))) == n*5)
    prior = p['actual_charge_prior']
    ledger = read(prior['ledger'])
    prior_map = {r['execution']:r['execution_sha256'] for r in ledger['executions']}
    ck('prior', 'frozen current authoritative46execution prior exact', sha(prior['ledger']) == prior['ledger_sha256'] and len(prior_map) == 46 and
       prior_map == prior['execution_sha256'] == p['prior_execution_sha256'] == e['prior_execution_sha256'] == e['prior_execution_after_sha256'] and
       exact(e['actual_charge_prior'],prior))
    for row in ledger['executions']:
        ck('prior', 'original prior execution '+row['execution'], sha(row['execution']) == row['execution_sha256'])
        if 'charged_wall_s' in row:
            cert = read(row['external_post'])
            ck('prior', 'one original external upper replacement '+row['execution'], sha(row['external_post']) == row['external_post_sha256'] and
               cert['personnel_independent'] is cert['external_supervision_qualified'] is True and
               cert['checks_total'] == cert['checks_passed'] and cert['checks_failed'] == 0 and
               cert['execution_sha256'] == row['execution_sha256'] and cert['upper_wall_s'] == row['charged_wall_s'] and
               cert['upper_cpu_s'] == row['charged_cpu_s'] and sha(row['external_time']) == row['external_time_sha256'] == cert['external_time_sha256'])
    pw = math.fsum(r.get('charged_wall_s',r['wall_s']) for r in ledger['executions'])
    pc = math.fsum(r.get('charged_cpu_s',r['cpu_s']) for r in ledger['executions'])
    ck('prior', 'exact frozen charged fsum replaces old internal samples once', pw == ledger['conservative_r2_sum_wall_s'] == prior['wall_s'] ==
       p['previous_r2_wall_s'] == e['previous_r2_wall_s'] and pc == ledger['conservative_r2_sum_cpu_s'] == prior['cpu_s'] ==
       p['previous_r2_cpu_s'] == e['previous_r2_cpu_s'])
    ext = p['external_supervision']
    tb = raw(ext['sibling_path'])
    fields = tb.decode().split()
    elapsed,user,system = (Decimal(v) for v in fields[:3])
    uw,uc = float(elapsed+Decimal('.01')),float(user+system+Decimal('.02'))
    meta = raw(ext['metadata_path'])
    planned,started,reaped = [json.loads(line) for line in meta.splitlines()]
    proof = e['supervisor_launch_proof']
    charge = read(ext['charge_path'])
    receipt_lines = jsonlines(RUN/'cost_receipt.jsonl')
    receipt = receipt_lines[0]
    st = path(ext['sibling_path']).stat()
    ck('external', 'complete one line finite time exit0 local total caps', len(tb.splitlines()) == 1 and tb.endswith(b'\n') and
       len(fields) == 4 and fields[3] == '0' and all(v.is_finite() and v >= 0 for v in (elapsed,user,system)) and
       uw <= min(120.,3600.-pw) and uc <= min(240.,7200.-pc))
    ck('external', 'actual GNUtime PID supervisor parent argv reap identity', planned['event'] == 'planned_launch' and
       started['event'] == 'time_process_started' and reaped['event'] == 'time_process_reaped' and
       started['pid'] == reaped['pid'] == proof['actual_time_pid'] == charge['time_process_pid'] and
       reaped['returncode'] == 0 and reaped['failure'] is None and planned['supervisor_pid'] == proof['supervisor_pid'])
    argv = ['/usr/bin/time','--quiet','-f','%e %U %S %x','-o','/proc/self/fd/'+str(planned['time_fd']),'/usr/bin/python3',str(path(RUNNER)),
            '--protocol',str(path(e['protocol']))]
    ck('external', 'original exclusive held timeFD inode and argv identity', argv == planned['argv'] == started['argv'] == proof['actual_argv'] and
       st.st_ino == planned['time_inode'] == proof['time_inode'] and st.st_dev == planned['time_device'] == proof['time_device'] and
       planned['time_fd'] in proof['actual_time_output_fds'] and proof['actual_time_start_ticks'] > 0 and
       hashlib.sha256(meta.splitlines(keepends=True)[0]).hexdigest() == proof['planned_launch_line_sha256'])
    ck('external', 'exact planned frozen source binary protocol hashes', planned['run_id'] == RUN_ID and
       planned['protocol_sha256'] == e['protocol_sha256'] and planned['runner_sha256'] == p['own_source_sha256'][RUNNER] and
       planned['supervisor_source_sha256'] == p['own_source_sha256'][SUPERVISOR] and
       planned['time_binary_sha256'] == ext['time_binary_sha256'] == sha('/usr/bin/time') and
       planned['python_binary_sha256'] == ext['python_binary_sha256'] == sha('/usr/bin/python3'))
    ck('external', 'saved charge original hash identity measured exit caps', charge['schema'] == 'P4_R2_ABB_SBL_PCS_PATH_EXTERNAL_COST_CHARGE_V1' and
       charge['execution_sha256'] == sha(RUN/'execution.json') and charge['receipt_sha256'] == sha(RUN/'cost_receipt.jsonl') and
       charge['time_sha256'] == sha(ext['sibling_path']) and charge['metadata_sha256'] == sha(ext['metadata_path']) and
       charge['stderr_sha256'] == sha(ext['stderr_path']) and charge['time_fields'] == fields and exact([charge['wall_s'],charge['cpu_s']],[uw,uc]) and
       charge['timing_valid'] is charge['time_inode_unchanged'] is charge['wall_CPU_caps_pass'] is charge['completed_process_exit0'] is True and
       charge['time_returncode'] == charge['measured_child_exit'] == 0 and charge['failure'] is None)
    ck('external', 'whole child execution receipt persistence exit within upper bound', len(receipt_lines) == 1 and
       receipt['execution_sha256'] == sha(RUN/'execution.json') and receipt['status'] == e['status'] and
       0 <= e['wall_s'] <= receipt['wall_s_through_execution_persistence'] <= uw and
       0 <= e['cpu_s'] <= receipt['cpu_s_through_execution_persistence'] <= uc and
       receipt['last_receipt_persistence_tail'] == 'UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED' and
       receipt['external_supervision_qualified'] is e['external_supervision_qualified'] is charge['external_supervision_qualified'] is False)
    ck('scope', 'zero new IK NR projection RBS solve RNG VI formal calls', e['zero_calls'] ==
       dict.fromkeys(('IK','NR','projection','RBS','solve','RNG','VI_constructions','formal_table_I'),0) and
       e['formal_table_I_calls'] == e['new_VI_candidate_constructions'] == 0 and e['independent_path_qualified'] is False and
       e['continuous_collision_certificate'] is False and q['independent_path_qualified'] is False and
       q['independent_physical_queries_performed'] == 0 and q['continuous_collision_certificate'] is False)
    scope=read(p['D080_scope']['path'])
    ck('scope','D080 I-V no VI future science formal18000 remains unapproved',sha(p['D080_scope']['path'])==p['D080_scope']['sha256'] and scope['allowed_environments']==['I','II','III','IV','V'] and scope['VI_future_science_authorized'] is False and scope['formal_execution_authorized'] is False and scope['formal_table_I_D080']==p['D080_scope']['formal_table_I_D080']==18000 and p['D080_scope']['formal_table_I_original']==22500 and p['D080_scope']['formal_calls']==p['D080_scope']['VI_new_calls']==0)
    for name,h in list(retained.items()):
        ck('preservation', 'all read bytes retained '+name, hashlib.sha256(path(name).read_bytes()).hexdigest() == h)
    return dict(execution_sha256=sha(RUN/'execution.json'),protocol=e['protocol'],protocol_sha256=sha(e['protocol']),source_commit=e['source_commit'],
        source_status=se['status'],source_exact=d['exact'],source_has_solution=d['solution_count']==1,source_approximate=False,
        source_bridge_motion_ids=[32,49],native_connect_motion_id=50,native_connect_role=None,source_milestone_motion_ids=[1,7,32,49,3,2],
        source_attempt_returns=[a['returned'] for a in attempts],source_attempt_nodes=[len(a['path_q12']) for a in attempts],
        selected_source_attempt_indices=[edge['selected_attempt_index'] for edge in edges],nodes=n,edges=len(edges),leaves=len(full_leaves),
        maximum_full12_leaf_rad=max(full_leaves),maximum_saved_closure_position_mm=max_pos,maximum_saved_closure_rotation=max_rot,
        minimum_source_mechanical_margin_rad=minimum_margin,branch_sets_encountered=[list(v) for v in sorted(branch_sets)],
        native_collision_nodes=native_collision_nodes,aligned_collision_nodes=aligned_collision_nodes,PQP_queries=pqp,actual_counts=counts,
        external_time_sha256=sha(ext['sibling_path']),external_charge_sha256=sha(ext['charge_path']),external_time_fields=fields,
        upper_wall_s=uw,upper_cpu_s=uc,execution_sample_wall_s=e['wall_s'],execution_sample_cpu_s=e['cpu_s'],
        previous_charged_wall_s=pw,previous_charged_cpu_s=pc,cumulative_upper_wall_s=math.fsum((pw,uw)),cumulative_upper_cpu_s=math.fsum((pc,uc)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-source-commit',required=True)
    parser.add_argument('--output',default=OUT)
    args = parser.parse_args()
    if path(args.output).exists() or path(args.output).with_suffix('.md').exists():
        raise FileExistsError('EXCLUSIVE_INDEPENDENT_POST_NO_OVERWRITE')
    details = {}
    try:
        details = audit(args.expected_source_commit)
    except BaseException as exc:
        ck('audit_completion','complete saved audit without structural exception '+repr(exc),False)
    audit_script_sha256 = sha(__file__)
    failures = [c for c in checks if not c['passed']]
    passed = not failures
    external = bool(groups['external']['total']) and groups['external']['total'] == groups['external']['passed']
    report = dict(schema='P4_SBL_PCS_PATH01_SAVED_INDEPENDENT_POST_V1',
        status='PASS_COMPLETE_DISCRETE_SOURCE_POLICY_SBL_PATH_INDEPENDENT_POST' if passed else 'FAIL_COMPLETE_SBL_PATH_INDEPENDENT_POST',
        generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='sbl_independent_resume; independent of SBL P implementation',
        personnel_independent=True,checks_total=len(checks),checks_passed=sum(c['passed'] for c in checks),checks_failed=len(failures),
        groups=dict(groups),failures=failures,external_supervision_qualified=external,external_timing_qualified=external,
        independent_path_qualified=passed,completed_process_exit0=external,continuous_collision_certificate=False,
        charge_rule='Only P external upper replaces this P internal sample once; every old cost including failed S01 remains charged once.',
        **details,retained_sha256=retained,audit_script_sha256=audit_script_sha256,
        new_import_runner_model_native_query_compile_protocol_prior_claim_commit_calls=0,
        limitations=['Saved complete387-node/386-leaf original source-policy discrete path only; no new model or collision call in this audit.',
            'FK/J and branch invariant values originate from the frozen independently reviewed physical checker; saved matrices, signs, raw records and provenance are audited here.',
            'Original false final edge active0/b0 M2 remains failed; successful original active1/b3 fallback M65 is separately identified.',
            'Original Motion/state/generation identities and actual32to49 bridge remain; natural connect50 a_chain stays null; no planner_data was emitted.',
            'No continuous CCD, solid rod, omitted mesh pair, RSS, PCS advantage, global success-rate or full-paper claim.',
            'SBL SOLVE01 exact candidate and all earlier source failures/UNKNOWN are retained; P never overwrites source qualification or internal writer UNKNOWN.',
            'GNUtime whole-child cost covers import/preflight/workers/cleanup/hash/receipt/exit; supervisor own persistence overhead explicitly excluded.',
            '211 original obligations preserved with D080 I-V scope, original0/22500 and approved0/18000 separate; VI974/974 archival only; no P2/Isaac or extra budget.'])
    with path(args.output).open('x') as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False)
        stream.write('\n')
    with path(args.output).with_suffix('.md').open('x') as stream:
        stream.write('# P 完整保存路径人员独立 POST\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(report['checks_total'])+
            '，失败'+str(report['checks_failed'])+'。人员独立保存审计；新科学调用、runner/model import、编译、协议/账/claim生成均为0。\n\n'+
            '独立完整离散路径资格='+str(passed)+'；外层GNUtime资格='+str(external)+'。387节点、386叶原高精度队列及全部成功/失败原尝试保持；只适用于原aligned离散碰撞策略，不含连续碰撞或统计性能结论。\n\n'+
            '费用仅以本P外层上界替换本P内部样本一次，旧S01等成本不重复累计。211项原义务、D080 I-V范围、原0/22500与批准0/18000分列，VI974/974仅归档和所有历史STOP/UNKNOWN保持。\n\n'+
            json.dumps(details,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','checks_total','checks_passed','checks_failed','external_supervision_qualified','independent_path_qualified')},ensure_ascii=False))
    raise SystemExit(0 if passed else 2)


if __name__ == '__main__':
    main()
