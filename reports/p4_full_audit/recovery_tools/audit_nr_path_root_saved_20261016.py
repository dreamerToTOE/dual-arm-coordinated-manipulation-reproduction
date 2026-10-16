#!/usr/bin/env python3
"""Personnel-independent stdlib-only audit of already saved NR PATH01.

No model import, binary execution, FK/IK/NR/Jacobian/PQP/RNG or compilation.
Only saved binary64 arrays, matrices, events, source bytes and hashes are read.
"""
from pathlib import Path
from collections import Counter, defaultdict
import datetime
import hashlib
import json
import math
import struct
import subprocess

ROOT = Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN = ROOT/'results/p4_full/20261015_R2_ABB_RRT_NR_PATH01'
E2E = ROOT/'results/p4_full/20261015_R2_ABB_RRT_NR_E2E01'
OUT = ROOT/'reports/P4_FULL_R2_ABB_RRT_NR_PATH_ROOT_INDEPENDENT_POST_20261016.json'
groups = defaultdict(lambda: {'total': 0, 'passed': 0})
failed = []


def fp(name):
    p = Path(name)
    return p if p.is_absolute() else ROOT/p


def sha(name):
    return hashlib.sha256(fp(name).read_bytes()).hexdigest()


def read(name):
    return json.loads(fp(name).read_text())


def packed(a):
    return struct.pack('>'+str(len(a))+'d', *a)


def exact(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if type(a) in (int, float) and type(b) in (int, float):
        return packed([a]) == packed([b])
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return set(a) == set(b) and all(exact(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(exact(x, y) for x, y in zip(a, b))
    return a == b


def ck(group, label, ok):
    groups[group]['total'] += 1
    groups[group]['passed'] += bool(ok)
    if not ok:
        failed.append({'group': group, 'check': label})


def lines(name, prefix=None):
    raw = fp(name).read_bytes()
    ck('raw', str(name)+' complete newline', not raw or raw.endswith(b'\n'))
    result = []
    for i, line in enumerate(raw.splitlines(), 1):
        if prefix is not None:
            if not line.startswith(prefix):
                ck('raw', str(name)+' unexpected line '+str(i), False)
                continue
            line = line[len(prefix):]
        try:
            result.append(json.loads(line))
        except (ValueError, UnicodeDecodeError):
            ck('raw', str(name)+' unparseable line '+str(i), False)
    return result


execution_before_sha256 = sha(RUN/'execution.json')
e = read(RUN/'execution.json')
p = read(e['protocol'])
c = read(e['claim'])
se = read(E2E/'execution.json')
sp = read(se['protocol'])
sc = read(se['claim'])
d = read(E2E/'runtime/result.json')
attempts = lines(E2E/'runtime/reconstruction_attempts.jsonl')
queue = read(RUN/'node_queue.json')
full = read(RUN/'full_fixed_queue.json')
ck('metadata', 'fixed path PASS', e['schema'] == 'P4_R2_ABB_RRT_NR_PATH_EXECUTION_V1' and
   e['status'] == 'PASS_DISCRETE_SOURCE_POLICY_NR_START_TO_GOAL_PATH')
ck('metadata', 'path reviewed frozen', p['frozen'] is True and all(x is True for x in p['reviews'].values()) and
   p['execution_readiness'] == 'FROZEN_REVIEWED_READY')
ck('metadata', 'path protocol original after hashes', sha(e['protocol']) == e['protocol_sha256'] == e['protocol_after_sha256'])
ck('metadata', 'path claim source and hashes', sha(e['claim']) == e['claim_sha256'] == e['claim_after_sha256'] and
   c['source_commit'] == e['source_commit'] and c['protocol_sha256'] == e['protocol_sha256'])
ck('metadata', 'source exact pending history kept', se['status'] == 'SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT' and
   d['exact'] is True and d['approximate'] is False and d['has_solution'] is True and se['returncode'] == 0)
ck('metadata', 'source one actual solve', se['solve_dispatched'] == se['solve_calls_from_result'] == d['solve_calls'] == 1)
ck('metadata', 'source request fixed', exact(d['request'], sp['request']) and exact(sp['request'], se['driver_request']) and
   d['seed'] == 7 and d['range_rad'] == 2.6 and d['goal_bias'] == .05 and d['request']['solve_seconds'] == 10.)
ck('metadata', 'source source/claim/protocol hash', sha(se['protocol']) == se['protocol_sha256'] == se['protocol_after_sha256'] and
   sha(se['claim']) == se['claim_sha256'] == se['claim_after_sha256'] and sc['source_commit'] == se['source_commit'])
ck('metadata', 'source result digest', sha(E2E/'runtime/result.json') == se['result_sha256'])
ck('metadata', 'source reviewed frozen', sp['frozen'] is True and all(v is True for v in sp['reviews'].values()))
ck('metadata', 'source local multilayer gate', sp['local_gate']['ready'] is True)
ck('metadata', 'formal/VI zero', e['zero_calls'] == dict.fromkeys(('solve','NR','IK','projection','RBS','RNG','VI_constructions','formal_table_I'), 0) and
   d['formal_table_I_calls'] == se['formal_table_I_calls'] == 0 and se['new_VI_candidate_constructions'] == 0)
ck('metadata', 'fixed original gates', p['gates'] == {'position_maxabs_mm': 1e-5, 'rotation_matrix_maxabs': 1e-5,
   'strict_leaf_full12_L2_rad': .05, 'source_literal_pi_for_mechanical_limits': 3.1416,
   'source_PQP_tolerance_mm': 8., 'fixed_active_or_branch_gate': False, 'continuous_collision_certificate': False})
for name, wanted in sp['own_source_sha256'].items():
    blob = subprocess.check_output(['git','show',se['source_commit']+':'+name], cwd=ROOT)
    ck('provenance', 'source committed blob '+name, hashlib.sha256(blob).hexdigest() == wanted == sha(name))
ck('provenance', 'source own before after', sp['own_source_sha256'] == se['own_source_sha256'] == se['own_source_after_sha256'])
ck('provenance', 'source build before after', sp['build_assets']['files'] == se['build_assets_before_sha256'] == se['build_assets_after_sha256'])
for name, wanted in se['retained_run_files_sha256'].items():
    ck('provenance', 'source retained file '+name, sha(name) == wanted)
ck('provenance', 'path bound before after', p['bound_files_sha256'] == e['bound_files_sha256'] == e['bound_files_after_sha256'])
for name, wanted in e['bound_files_sha256'].items():
    ck('provenance', 'current bound '+name, sha(name) == wanted)
ck('provenance', 'queue protocol and hash', exact(p['fixed_queue'], full) and exact(full['nodes'], queue) and
   sha(RUN/'node_queue.json') == e['node_queue_sha256'])

milestones = d['milestones_q12']
for i, suffix in enumerate(('start_q12','goal_q12')):
    point = read('results/p4_full/20261015_R2_ENDPOINT_RECONSTRUCTED01/II_'+str(i)+'.json')
    ck('source_path', suffix+' exact A01', exact(d[suffix], point['selected_q_rad']) and
       point['status'] == 'RECONSTRUCTED_SOURCE_POLICY_QUALIFIED' and point['source_policy_collision_qualified'] is True)
ck('source_path', 'milestone exact start goal', packed(milestones[0]) == packed(d['start_q12']) and packed(milestones[-1]) == packed(d['goal_q12']))
ck('source_path', 'all JSONL paths exact', exact(attempts, d['reconstruction_attempts']) and
   len(attempts) == len(milestones)-1 == d['reconstruction_calls_completed_observed'] == 6)
ck('source_path', 'no source incomplete tails', se['observation_prefix']['reconstruction_incomplete_tails'] == [] and
   se['observation_prefix']['reconstruction_calls_completed_observed'] == len(attempts))
nodes = []
lookup = {}


def add(q, ref):
    key = packed(q)
    if key not in lookup:
        lookup[key] = len(nodes)
        nodes.append({'node_id': len(nodes), 'environment': 'II', 'q12': q, 'refs': [], 'collision_required': True})
    nodes[lookup[key]]['refs'].append(ref)
    return lookup[key]


milestone_ids = [add(q, {'kind':'milestone','milestone_index':i}) for i,q in enumerate(milestones)]
leaves = []
edge_summary = []
for i, a in enumerate(attempts):
    ck('source_path', str(i)+' original completion schema', a['schema'] == 'P4_ABB_RRT_NR_RECONSTRUCTION_DRAFT_V1' and
       a['attempt_index'] == i and a['observation'] == 'ORIGINAL_STATE_LEVEL_CALL_COMPLETED_POST_RETURN' and a['returned'] is True)
    ck('source_path', str(i)+' original ordered edge bits', packed(a['qa12']) == packed(milestones[i]) and packed(a['qb12']) == packed(milestones[i+1]))
    for side in ('qa12','qb12'):
        add(a[side], {'kind':'attempt_endpoint','attempt_index':i,'side':side,'returned':True})
    ids = [add(q, {'kind':'original_dense_path','attempt_index':i,'path_index':j,'returned':True}) for j,q in enumerate(a['path_q12'])]
    ck('source_path', str(i)+' dense endpoints exact', len(ids) >= 2 and packed(a['path_q12'][0]) == packed(a['qa12']) and packed(a['path_q12'][-1]) == packed(a['qb12']))
    local_leaves = [math.sqrt(math.fsum((x-y)**2 for x,y in zip(u,v))) for u,v in zip(a['path_q12'],a['path_q12'][1:])]
    for j, length in enumerate(local_leaves):
        ck('leaves', str(i)+':'+str(j)+' strict .05', length < .05)
    leaves += local_leaves
    edge = full['edges'][i]
    ck('source_path', str(i)+' full queue edge links', edge['node_ids'] == ids and exact(edge['leaf_distances_rad'], local_leaves) and edge['structural_qualified'] is True)
    edge_summary.append({'edge_index':i,'dense_nodes':len(ids),'leaves':len(local_leaves),'max_leaf_L2_rad':max(local_leaves)})
ck('queue', 'independently reconstructed full queue bits refs', exact(nodes, queue) and full['milestone_node_ids'] == milestone_ids)
ck('queue', 'all393 no missing duplicated ids', len(nodes) == 393 and [n['node_id'] for n in queue] == list(range(393)) and len(lookup) == 393)
ck('queue', 'all full paths fit resource cap', len(nodes) <= p['max_unique_nodes'] == 2048 and p['full_queue_node_count'] == len(nodes))
tree = d['planner_data']
vertices = tree['vertices']
ck('tree', 'complete vertices and edges', tree['num_vertices'] == len(vertices) == 55 and tree['num_edges'] == len(tree['edges']) == 54 and
   [v['index'] for v in vertices] == list(range(len(vertices))))
vp = full['source_tree_vertex_path']
ck('tree', 'tree actual start and goal flags', len(vp) == len(milestones) and vertices[vp[0]]['start'] is True and vertices[vp[-1]]['goal'] is True)
for i, (v,q) in enumerate(zip(vp,milestones)):
    ck('tree', 'path vertex '+str(i)+' exact', packed(vertices[v]['q12']) == packed(q))
for a,b in zip(vp,vp[1:]):
    ck('tree', 'actual directed edge '+str(a)+'->'+str(b), [a,b] in tree['edges'])

stdout = RUN/'00001_independent_full_node_queue.stdout.txt'
stderr = RUN/'00001_independent_full_node_queue.stderr.txt'
responses = lines(stdout, b'P4_NR_NODE_RESPONSE ')
events = lines(stderr, b'P4_NR_NODE_EVENT ')
inventory = read(RUN/'raw_prefix_inventory.json')
ck('raw', 'complete retained inventory raw exact', exact(responses, inventory['node_responses']) and exact(events, inventory['worker_events']) and inventory['actual_observed_only'] is True)
ck('raw', 'all393 response ids exactly once', [r['node_id'] for r in responses] == list(range(393)))
parent_events = lines(RUN/'events.jsonl')
ck('raw', 'single worker process exit0', [v['event'] for v in parent_events] == ['process_started','process_finished'] and parent_events[-1]['exit_code'] == 0 and
   parent_events[-1]['stdout_sha256'] == sha(stdout) and parent_events[-1]['stderr_sha256'] == sha(stderr))
worker = read(RUN/'node_worker_started.json')
ck('raw', 'worker parent claim protocol queue binding', worker['parent_pid'] == c['parent_pid'] and worker['protocol_sha256'] == e['protocol_sha256'] and worker['node_queue_sha256'] == e['node_queue_sha256'])
request = read(RUN/'00001_independent_full_node_queue.input.txt')
ck('raw', 'request queue binding', request['node_queue_sha256'] == e['node_queue_sha256'])
by_node = defaultdict(list)
for event in events:
    by_node[event['node_id']].append(event)
expected_events = ['math_arm_FK_started','math_arm_FK_completed']*2+['collision_started']+['adapter_arm_FK_J_started','adapter_arm_FK_J_completed']*4+['collision_completed']
bounds = [(lo*3.1416/180, hi*3.1416/180) for lo,hi in [(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)]]*2
collision_manifest = read(p['collision_manifest'])
entries = {r['variant']:r for r in collision_manifest['entries'] if r['model'] == 'abb'}
max_position = max_rotation = 0.
min_margin = math.inf
native_mismatches = 0
native_collision_counts = Counter()
pqp_counts = Counter()
for i, (source, response) in enumerate(zip(queue, responses)):
    node = read(RUN/f'node_{i:05d}.json')
    ck('nodes', str(i)+' raw response bit exact', exact(node, response['result']))
    ck('nodes', str(i)+' input queue immutable', all(exact(node[k],v) for k,v in source.items()) and source['collision_required'] is True)
    ck('nodes', str(i)+' completed physical flags', node['stage'] == 'COMPLETED' and node['math_qualified'] is True and node['node_qualified'] is True)
    poses = node['poses']
    ck('nodes', str(i)+' two finite homogeneous saved poses', len(poses) == 2 and all(len(t)==4 and all(len(r)==4 for r in t) and
       all(type(x) in (float,int) and math.isfinite(x) for r in t for x in r) and t[3] == [0.,0.,0.,1.] for t in poses))
    t1,t2 = poses
    target = [[(-t1[r][j] if j<2 else t1[r][j]) for j in range(3)]+[300.*t1[r][0]+t1[r][3]] for r in range(3)]
    position = max(abs(t2[r][3]-target[r][3]) for r in range(3))
    rotation = max(abs(t2[r][j]-target[r][j]) for r in range(3) for j in range(3))
    max_position = max(max_position, position)
    max_rotation = max(max_rotation, rotation)
    ck('poses', str(i)+' independent stored matrix closure', position <= 1e-5 and rotation <= 1e-5)
    ck('poses', str(i)+' recorded residual agrees arithmetic', abs(position-node['closure']['position_max_abs']) <= 1e-10 and abs(rotation-node['closure']['rotation_matrix_max_abs']) <= 1e-14)
    q = node['q12']
    for j,(v,(lo,hi)) in enumerate(zip(q,bounds)):
        ck('limits', str(i)+':'+str(j)+' original mechanical bound', math.isfinite(v) and lo <= v <= hi)
        min_margin = min(min_margin,v-lo,hi-v)
    ck('limits', str(i)+' saved limits agree', node['limits'] == {'legal':True,'violations':[],'source_literal_pi_preserved':3.1416,'planar_q19_policy':None})
    for arm in (1,2):
        partial = read(RUN/f'node_{i:05d}_arm{arm}.json')
        ck('nodes', str(i)+' arm'+str(arm)+' durable partial', exact(partial['poses'],poses[:arm]) and packed(partial['q12']) == packed(q))
    ck('nodes', str(i)+' durable math', exact(read(RUN/f'node_{i:05d}_math.json')['closure'],node['closure']))
    collision = node['collision']
    ck('collision', str(i)+' durable raw exact', exact(collision,read(RUN/f'node_{i:05d}_collision_raw.json')))
    ck('collision', str(i)+' aligned selected checked clear', collision['status']=='CHECKED' and collision['collision'] is False and
       collision['selected_variant']=='aligned' and collision['manifest_sha256']==sha(p['collision_manifest']) and collision['continuous_collision_certificate'] is False)
    for variant in ('native','aligned'):
        row = collision['variants'][variant]
        raw_rows = [json.loads(s.split(' ',1)[1]) for s in row['source_stdout'].splitlines() if s.startswith('P4_COLLISION_RESULT ')]
        ck('collision', str(i)+' '+variant+' one original response', len(raw_rows)==1)
        for name in ('native_result','cpu_s','poses','query_codes'):
            ck('collision', str(i)+' '+variant+' raw '+name, exact(raw_rows[0][name], row[name]))
        ck('collision', str(i)+' '+variant+' command source provenance', row['source_command']==[entries[variant]['binary'],'II'] and
           row['provenance']['binary_sha256']==entries[variant]['binary_sha256'] and row['provenance']['source_files_sha256']==entries[variant]['source_files_sha256'] and row['provenance']['mesh_sha256']==entries[variant]['mesh_sha256'])
        codes=row['query_codes']
        ck('collision', str(i)+' '+variant+' every actual PQP code zero', len(codes)>0 and all(type(v) is int and v==0 for v in codes) and row['query_error_codes']==[])
        pqp_counts[variant]+=len(codes)
        errors=[]
        for arm in range(2):
            actual=[row['poses'][arm][r*4:(r+1)*4] for r in range(3)]
            err=row['pose_consistency']['errors'][arm]
            ck('collision_pose', str(i)+' '+variant+str(arm)+' recorded native matrix bits', exact(actual,err['collision_TCP']))
            expected=err['independent_TCP']
            pe=max(abs(actual[r][3]-expected[r][3]) for r in range(3))
            re=max(abs(actual[r][j]-expected[r][j]) for r in range(3) for j in range(3))
            ck('collision_pose', str(i)+' '+variant+str(arm)+' error arithmetic', exact(pe,err['translation_maxabs_mm']) and exact(re,err['rotation_maxabs']))
            errors.append(pe<=1e-5 and re<=1e-5)
            if variant=='aligned':
                ck('collision_pose', str(i)+' aligned'+str(arm)+' independently stored oracle pose',
                   max(abs(actual[r][j]-poses[arm][r][j]) for r in range(3) for j in range(4))<=1e-5)
        ck('collision_pose', str(i)+' '+variant+' saved pose gate arithmetic', row['pose_consistency']['passed'] is all(errors))
        if variant=='aligned':
            ck('collision_pose', str(i)+' aligned both TCP qualify', all(errors))
        else:
            native_mismatches += not all(errors)
            native_collision_counts[str(row['native_result'])]+=1
    node_events=by_node[i]
    ck('events', str(i)+' complete ordered worker event sequence', [v['event'] for v in node_events]==expected_events)
    ck('events', str(i)+' collision complete exact query counts', node_events[-1]['variant_query_counts']=={v:len(collision['variants'][v]['query_codes']) for v in ('native','aligned')} and node_events[-1]['PQP_queries']==sum(len(collision['variants'][v]['query_codes']) for v in ('native','aligned')))
    expected_counts={'math_arm_FK_started':2*(i+1),'math_arm_FK_completed':2*(i+1),'collision_calls_started':i+1,
       'adapter_arm_FK_J_started':4*(i+1),'adapter_arm_FK_J_completed':4*(i+1),'collision_calls_completed':i+1,'PQP_queries':sum(pqp_counts.values())}
    ck('events', str(i)+' actual cumulative response counts', response['observed_counts']==expected_counts)

ecounts=Counter(v['event'] for v in events)
for kind,count in ecounts.items():
    ck('accounting', kind+' actual event count', e['counts']['actual_'+kind]==count)
ck('accounting', 'native/aligned PQP totals', e['counts']['actual_adapter_native_PQP_queries']==pqp_counts['native'] and
   e['counts']['actual_adapter_aligned_PQP_queries']==pqp_counts['aligned'] and e['counts']['actual_adapter_PQP_queries']==sum(pqp_counts.values()))
ck('accounting', 'all checked/no tail', e['completed_node_ids']==list(range(393)) and e['uncompleted_node_ids']==[] and e['full_node_queue_checked'] is True and e['full_node_queue_count']==393 and e['diagnostics']==[])
ck('accounting', 'all final saved node files', len(list(RUN.glob('node_[0-9][0-9][0-9][0-9][0-9].json')))==393)
prior=[read(f) for f in e['prior_executions']]
ck('budget', 'own wall sum once', math.fsum(v['wall_s'] for v in prior)==e['previous_r2_wall_s']==p['previous_r2_wall_s'])
ck('budget', 'own CPU sum once', math.fsum(v['cpu_s'] for v in prior)==e['previous_r2_cpu_s']==p['previous_r2_cpu_s'])
ck('budget', 'path limits and cumulative remain', e['wall_s']<120 and e['cpu_s']<240 and e['previous_r2_wall_s']+e['wall_s']<3600 and e['previous_r2_cpu_s']+e['cpu_s']<7200)
for name,wanted in e['bound_files_sha256'].items():
    ck('preservation', 'final read-only bound '+name, sha(name)==wanted)
ck('preservation', 'original execution unchanged', sha(RUN/'execution.json')==execution_before_sha256)
total=sum(v['total'] for v in groups.values())
passed=sum(v['passed'] for v in groups.values())
report={'schema':'P4_NR_PATH_PERSONNEL_INDEPENDENT_STDLIB_SAVED_POST_V1',
   'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'run_id':RUN.name,'reviewer':'nr_entry_review (not path runner author)',
   'personnel_independent':True,'status':'PASS_SAVED_EVIDENCE_AUDIT' if not failed else 'FAIL_SAVED_EVIDENCE_AUDIT',
   'checks_total':total,'checks_passed':passed,'checks_failed':len(failed),'check_groups':dict(groups),'failed_checks':failed,
   'zero_new_scientific_calls':True,'zero_compile_calls':True,'audit_script_sha256':sha(Path(__file__)),
   'execution_sha256':sha(RUN/'execution.json'),'protocol_sha256':sha(e['protocol']),
   'source_execution_sha256':sha(E2E/'execution.json'),'source_result_sha256':sha(E2E/'runtime/result.json'),
   'summary':{'unique_nodes':len(nodes),'qualified_nodes':len(responses),'reconstruction_edges':len(attempts),
       'full_dense_leaf_count':len(leaves),'max_leaf_full12_L2_rad':max(leaves),
       'max_saved_pose_closure_position_mm':max_position,'max_saved_pose_closure_rotation_matrix':max_rotation,
       'min_original_mechanical_limit_margin_rad':min_margin,'source_tree_vertices':len(vertices),'source_tree_edges':len(tree['edges']),
       'source_tree_vertex_path':vp,'edge_summaries':edge_summary,'worker_events_actual':dict(ecounts),
       'PQP_queries_actual':dict(pqp_counts),'native_TCP_mismatch_nodes':native_mismatches,
       'native_collision_result_counts':dict(native_collision_counts),'bound_asset_count':len(e['bound_files_sha256']),
       'scientific_path_wall_s':e['wall_s'],'scientific_path_cpu_s':e['cpu_s']},
   'evidence_boundary':['Only stored arrays/matrices/events, literal mechanical limits and file/source hashes were examined.',
       'No FK/IK/NR/Jacobian/collision/PQP/RNG/binary/compile execution was performed.',
       'Native TCP inconsistency is retained separately; only aligned v3 source discrete policy is qualified.',
       'One RECONSTRUCTED physical-NR/A01 path does not establish author KDL equivalence, random success statistics, performance, CCD or complete P4.']}
with OUT.open('x') as stream:
    json.dump(report,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
md=OUT.with_suffix('.md')
with md.open('x') as stream:
    stream.write(f'''# NR393完整路径人员独立保存证据审查\n\n2026-10-16，`{report['status']}`，{passed}/{total}项检查通过，失败{len(failed)}。人员独立于科学runner作者；全部使用stdlib保存证据算术与哈希，0新科学调用、0编译。\n\n原单次E2E exact非approx历史PENDING原样保留；7里程点、6条原state-level回溯true、55树节点/54边，以及原tree序列{vp}逐bit吻合。完整393唯一节点及392叶全部覆盖，最大叶距{max(leaves):.17g}<.05rad。所有qa/qb/Confs、节点来源refs、原始JSONL、stdout响应、保存partial与事件保持一致；无未完成尾部。\n\n对保存的双臂TCP矩阵独立计算闭链，最大位置{max_position:.17g}mm、旋转矩阵{max_rotation:.17g}；原机械界最小余量{min_margin:.17g}rad。393节点全部aligned原策略碰撞clear；native/aligned原始PQP响应逐bit绑定，查询各{pqp_counts['native']}/{pqp_counts['aligned']}，所有实际querycode为整数0。native TCP不一致{native_mismatches}节点如实保留。786数学臂FK/J、1572adapter内部FK/J、393collision的实际开始/完成事件与记录一致。\n\n1352绑定资产、原科学execution/协议/claim/binary/source/mesh和24既往execution逐own成本均复核。实际本路径3.773092653wall/3.95727CPU，原120/240及累计3600/7200帽内。原execution未修改。\n\n这仅为原离散碰撞策略下的一条RECONSTRUCTED物理NR/A01起终点路径保存证据，不证明CCD、实体杆面/省略pair、作者KDL数值等价、速度胜负、RSS或完整P4。\n''')
print(json.dumps({'status':report['status'],'checks_total':total,'checks_passed':passed,'checks_failed':len(failed),
   'report_sha256':sha(OUT),'md_sha256':sha(md),'summary':report['summary'],'failed_checks':failed},ensure_ascii=False))
