#!/usr/bin/env python3
"""Personnel-independent static P review: read/AST only, never import a runner."""
from pathlib import Path
import ast
from datetime import datetime, timezone
import hashlib
import json
import math
import struct

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'reports/P4_FULL_R2_ABB_CBIRRT_D_PATH_INDEPENDENT_STATIC_REVIEW_20261016'
checks = []
bound = {}


def read(name, wanted=None):
    raw = (ROOT / name).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    bound[name] = actual
    if wanted is not None:
        check('stable SHA ' + name, actual == wanted)
    return raw


def check(name, passed):
    checks.append({'check': name, 'passed': bool(passed)})


def body_function(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


def one_nested(tree, cls, predicate):
    nodes = [n for n in ast.walk(body_function(tree, 'execute')) if isinstance(n, cls) and predicate(n)]
    check('exact one requested AST node ' + cls.__name__, len(nodes) == 1)
    return nodes[0]


runner = read('scripts/qualify_p4_full_r2_abb_cbirrt_d_path_draft.py',
              'b4230a660bc5d441e3256c2dc287d6a899cd2c8d0c20eeb7a8d90dd9fd57c17c').decode()
helper = read('scripts/materialize_p4_full_r2_abb_cbirrt_d_path_draft.py',
              'eb8438312a001aec63c18fb277b32e56f30c66a000e37b0526f0faf58bbb7e4e').decode()
supervisor = read('scripts/supervise_p4_full_r2_abb_cbirrt_d_path_draft.py',
                  '2ca5d89f6a128bbaec4b74011723a3849b0479aba7f50a6bf43f241d080be59a').decode()
read('reports/P4_FULL_R2_ABB_CBIRRT_D_PATH_PRE_DRAFT_20261016.md',
     '2094a3479b0471ab4a8dc0b09c3cb8004f84dd4d173db660d1cb9b7dbefdab2b')
read('reports/P4_FULL_R2_ABB_CBIRRT_D_PATH_MATERIALIZER_PRE_DRAFT_20261016.md',
     '3c584bab1914174eba4dbbfb87cd9e46ec990d430c09e19813981969e5e5a001')
original = read('scripts/qualify_p4_full_r2_abb_rrt_path.py',
                'bdf4db7537b327872674e355dcbdcd5e31bebbb5a53ae6e21a07490a514b6865').decode()
tree, old_tree = ast.parse(runner), ast.parse(original)
ast.parse(helper); ast.parse(supervisor)
check('all reviewed Python sources parse without import or compilation', True)
selector = lambda n: ast.unparse(n.iter) == "enumerate(spec['fixed_queue']['nodes'])"
loop = one_nested(tree, ast.For, selector)
old_loop = one_nested(old_tree, ast.For, selector)
counted = one_nested(tree, ast.FunctionDef, lambda n: n.name == 'counted')
old_counted = one_nested(old_tree, ast.FunctionDef, lambda n: n.name == 'counted')
loop_ast = ast.dump(loop, include_attributes=False)
counted_ast = ast.dump(counted, include_attributes=False)
check('entire physical node loop AST exactly equals qualified original PCS loop',
      loop_ast == ast.dump(old_loop, include_attributes=False))
check('adapter FK/J counted wrapper AST exactly equals original PCS wrapper',
      counted_ast == ast.dump(old_counted, include_attributes=False))
check('closure and leaf gates retain original position1e-5 rotation1e-5 leaf.05 epsilon64',
      "GATES={'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5," in runner
      and "'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*sys.float_info.epsilon}" in runner)
check('node loop preserves original limits and all incident passive branch assignments',
      "oracle.limit_score(q, 'II')" in ast.unparse(loop)
      and "current['branches'][1 - e['active_chain']]['branch_set']" in ast.unparse(loop)
      and 'all((a[\'branch_pass\'] for a in assignments))' in ast.unparse(loop))
check('collision v3 manifest and both native/aligned builds are frozen',
      'collision_adapter_v3/manifest.json' in runner
      and "sorted(r['variant']for r in entries)==['aligned','native']" in runner
      and "entry['binary'],entry['binary_sha256']" in runner
      and "entry['source_files_sha256'].items()" in runner and "entry['mesh_sha256'].items()" in runner)
check('no replacement science loop, IK/NR/RBS/solve/RNG zero scope',
      'zero_calls=dict(IK=0,NR=0,projection=0,RBS=0,solve=0,RNG=0,VI_constructions=0,formal_table_I=0)' in runner)
check('actual S02 execution is hard SHA bound and correct independent schema/status required',
      "SOURCE_EXEC_SHA='c7cbd868da1cd9feb149bc057c4a63ff3e722b81123998e1a8cc5e8e1bab5906'" in runner
      and "post['schema']=='P4_SOLVE02_SAVED_INDEPENDENT_POST_V1'" in runner
      and "post['status']=='PASS_SOLVE02_TRANSPORT_EVIDENCE_INDEPENDENT_POST'" in runner)
check('two stdout lines must be exact55B preamble plus unique original JSON',
      "len(lines)==2 and lines[0]==source.PREAMBLE" in runner and 'exact(json.loads(lines[1]),d)' in runner)
check('all S provenance before/after, retained raw, meshes and native output files are bound',
      "e['bound_files_sha256']==e['bound_files_after_sha256']" in runner
      and "post['retained_sha256'].items()" in runner and "e['runtime_mesh_sha256'].items()" in runner
      and "e['original_native_output_sha256'].items()" in runner
      and "d['construction']['trace']+d['trace']" in runner)
check('complete materialization precedes prior and cap derivation',
      'queue=saved.materialize(d,provenance[\'request\']);prior=current_prior()' in runner)
check('2048 cap rejects full over-cap queue before claim or physical query',
      "spec['full_queue_node_count']<=MAX_NODES and spec['fixed_queue']['under_2048_full_queue_cap']is True" in runner
      and 'commit=validate(spec,protocol,True)' in runner
      and 'MAX_NODES=2048' in runner)
check('full saved node loop has no queue slice or changed ordering',
      ast.unparse(loop.iter) == "enumerate(spec['fixed_queue']['nodes'])"
      and 'require(len(results)==len(spec[\'fixed_queue\'][\'nodes\']))' not in runner
      and "require(len(results)==len(spec['fixed_queue']['nodes']),'COMPLETE_FULL_QUEUE_REQUIRED')" in runner)
check('full validation and latest actual prior are recomputed before frozen execution',
      'expected=draft_protocol()' in runner
      and "'LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS'" in runner
      and "'EXACT_PRIOR_CHARGE_SUMS_REQUIRED'" in runner)
check('external replacement costs require independent execution/time certificates once',
      "r.get('charged_wall_s',r['wall_s'])" in runner
      and "r.get('charged_cpu_s',r['cpu_s'])" in runner
      and "'PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED'" in runner)
check('P budget 120wall/240CPU also intersects original3600/7200 remaining caps',
      "self.wall_cap=min(120.,3600.-spec['previous_r2_wall_s'])" in runner
      and "self.cpu_cap=min(240.,7200.-spec['previous_r2_cpu_s'])" in runner
      and 'budget=dict(wall_s=120.,cpu_s=240.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)' in runner)
check('claim and run are exclusive; no active P4 or existing timer admitted',
      "'EXCLUSIVE_P_NO_RETRY_RESET_OR_RESUME'" in runner
      and "'OTHER_ACTIVE_P4_EXECUTION'" in runner and "'EXISTING_TIMER_REFUSE_REPLACE'" in runner)
check('frozen source/protocol bytes must match committed Git blobs before science',
      "subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT)==path(n).read_bytes()" in runner)
check('outer actual parent GNUtime PID/argv and exclusive time inode are checked',
      "'EXACT_SUPERVISOR_PARENT_CHAIN_REQUIRED'" in runner
      and "'ACTUAL_PARENT_GNU_TIME_REQUIRED'" in runner
      and "'ACTUAL_TIME_ARGV_MISMATCH'" in runner and "'EXCLUSIVE_SUPERVISION_INODE_MISMATCH'" in runner)
check('collision worker fork/register alarm mask and child CPU hard cap are present',
      'signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})' in runner
      and 'resource.setrlimit(resource.RLIMIT_CPU,(240,240))' in runner
      and 'budget.processes.append(proc)' in runner
      and 'start_new_session=True,preexec_fn=limits' in runner)
check('central registry covers worker initialization failures outside adapter session map',
      'list({p.pid:p for p in budget.processes}.values())' in runner
      and 'os.killpg(proc.pid,signal.SIGKILL)' in runner and 'proc.wait(timeout=1.)' in runner)
check('both start and close process-group singleton snapshots are required',
      "'COLLISION_WORKER_START_GROUP_NOT_SINGLE_CHILD'" in runner
      and "'COLLISION_WORKER_CLOSE_GROUP_NOT_SINGLE_CHILD'" in runner)
check('original transport is only lifecycle-adapted and restored after cleanup',
      'adapter_process_api=adapter.subprocess' in runner
      and 'adapter.subprocess=SimpleNamespace(Popen=registered_popen' in runner
      and 'adapter.subprocess=adapter_process_api' in runner)
check('worker gate requires two actual workers/session identities and exit0',
      "len(processes)==counts['collision_worker_started']==2 and len(sessions)==2" in runner
      and 'all(p.returncode==0 for p in processes)' in runner)
check('real selector close, finite raw pipe EOF drain and empty pending/tail are required',
      'selector_closed=session.selector.get_map()is None' in runner
      and 'deadline=time.monotonic()+1.' in runner
      and 'chunk=os.read(fd,65536)' in runner
      and 'else:eof=True' in runner and "'UNEXPECTED_COLLISION_WORKER_STDOUT_TAIL'" in runner)
check('final asset/protocol/claim/prior hashes and diagnostics can only invalidate PASS',
      "'P_BOUND_ASSET_CHANGED'" in runner and "'P_PROTOCOL_OR_CLAIM_CHANGED'" in runner
      and "'P_PRIOR_CHARGED_LEDGER_CHANGED'" in runner
      and "if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'" in runner)
check('original S02 source result never rewritten and independent path starts false',
      'independent_path_qualified=False,continuous_collision_certificate=False' in runner
      and "durable_new(folder/'execution.json',record)" in runner)
check('supervisor does not import runner and never starts second process on failure',
      not any(isinstance(n,(ast.Import,ast.ImportFrom)) and 'qualify_' in ast.unparse(n)
              for n in ast.parse(supervisor).body)
      and supervisor.count('subprocess.Popen(') == 1 and 'proc.wait()' in supervisor)
check('supervisor O_EXCL inheritedFD avoids overwrite and records actual identity',
      'os.O_WRONLY|os.O_CREAT|os.O_EXCL' in supervisor and 'pass_fds=(fd,)' in supervisor
      and 'opened_identity=(os.fstat(fd).st_dev,os.fstat(fd).st_ino)' in supervisor)
check('outer full child cost uses Decimal conservative upper bounds and cap rejection',
      "wall=float(elapsed+Decimal('.01'));cpu=float(user+system+Decimal('.02'))" in supervisor
      and "wall<=min(120.,3600.-spec['previous_r2_wall_s'])" in supervisor
      and "cpu<=min(240.,7200.-spec['previous_r2_cpu_s'])" in supervisor)
check('cost record explicitly excludes supervisor own persistence and requires independent POST',
      'Supervisor own journal/fsync cost excluded.' in supervisor
      and 'external_supervision_qualified=False,independent_POST_required=True' in supervisor)
check('helper has no file/process/scientific import or main execution entry',
      {n.module for n in ast.parse(helper).body if isinstance(n,ast.ImportFrom)} == {'collections'}
      and {a.name for n in ast.parse(helper).body if isinstance(n,ast.Import) for a in n.names} == {'math','struct'}
      and '__main__' not in helper)
check('helper retains tree identities, actual bridge, parent direction and complete PlannerData',
      "'PLANNER_DATA_NOT_EXACT_TWO_TREES_PLUS_ACTUAL_BRIDGE'" in helper
      and "'MISSING_OR_FABRICATED_REAL_BRIDGE'" in helper
      and "'MILESTONES_NOT_REVERSE_START_PLUS_FORWARD_GOAL_IDENTITY_ORDER'" in helper)
check('helper consumes original role0/fallback calls and retains all failed attempts',
      "((0,'ik_q1_active'),(1,'ik_q2_active'))" in helper
      and "'ORIGINAL_ROLE0_THEN_ROLE1_FALLBACK_CALL_ORDER_CHANGED'" in helper
      and 'all_original_attempts=attempts' in helper)
check('helper requires entire original true M endpoints, branch and strict full12 leaves',
      "'ENTIRE_ORIGINAL_SUCCESSFUL_M_FIRST_LAST_BINARY64_REQUIRED'" in helper
      and "'FULL12_ORIGINAL_LEAF_DISTANCE_NOT_STRICT_POINT05'" in helper
      and "'SUCCESSFUL_ORIGINAL_BRANCH_NOT_0_TO_7'" in helper)

# Saved-array cross-check only: never execute the helper or science runner.
queue = json.loads(read('work/cbirrt_d_source02_saved_materialize_20261016/full_queue.json',
                       '38ce4780897186fadff49f15cec239008df237b519deb9d16ddbac73eedb852f'))
key = lambda q: struct.pack('>12d', *q)
check('actual saved full queue413 unique and4 edges412 leaves, not a prefix',
      len(queue['nodes']) == len({key(q) for q in queue['nodes']}) == queue['full_queue_node_count'] == 413
      and len(queue['edges']) == 4 and sum(len(e['node_ids']) - 1 for e in queue['edges']) == 412
      and set(i for e in queue['edges'] for i in e['node_ids']) == set(range(413)))
check('saved5 original attempts preserve true/true/false/true/true and M lengths',
      [a['returned'] for a in queue['all_original_attempts']] == [True,True,False,True,True]
      and [len(a['path_q12']) for a in queue['all_original_attempts']] == [109,145,2,33,129])
check('saved4 selected true edges exactly109/145/33/129 including failed fallback prefix',
      [len(e['node_ids']) for e in queue['edges']] == [109,145,33,129]
      and [e['selected_attempt_index'] for e in queue['edges']] == [0,1,3,4]
      and queue['edges'][2]['consumed_attempt_indices'] == [2,3])
check('saved all M coordinates and every strict leaf retained exactly in full queue',
      all([key(queue['nodes'][i]) for i in e['node_ids']] ==
          [key(q) for q in queue['all_original_attempts'][e['selected_attempt_index']]['path_q12']]
          and len(e['leaf_distances_rad']) == len(e['node_ids']) - 1
          and all(math.isfinite(v) and v < .05 for v in e['leaf_distances_rad'])
          for e in queue['edges']))
check('saved actual queue explicitly has zero physical queries and no qualified path/CCD',
      queue['independent_physical_queries_performed'] == 0
      and queue['independent_path_qualified'] is False and queue['continuous_collision_certificate'] is False)
post = json.loads(read('reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE02_SAVED_INDEPENDENT_POST_20261016.json',
                      '730dbb69ff3749975639dd9cad2fe1f31ca45cb2bf370c0470cfddd329d64412'))
check('actual S02 independent5284 saved POST permits only transport not physical path',
      post['schema'] == 'P4_SOLVE02_SAVED_INDEPENDENT_POST_V1'
      and post['checks_total'] == post['checks_passed'] == 5284 and post['checks_failed'] == 0
      and post['external_supervision_qualified'] is True and post['independent_path_qualified'] is False)
ledger = json.loads(read('results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V17.json',
                        '10b7d97d485e6a28bcb5760cce2cb1f2d5ca920884531bb456e6de749e6dea8a'))
check('actual V17 prior35 and charged sums are available with enough P120/240 headroom',
      ledger['count'] == 35 and ledger['conservative_r2_sum_wall_s'] == 580.675705375994
      and ledger['conservative_r2_sum_cpu_s'] == 530.628923
      and ledger['r2_remaining']['wall_s'] >= 120 and ledger['r2_remaining']['cpu_s'] >= 240)
check('VI974 budget exhausted, formal0/22500 unchanged by P saved path qualification',
      ledger['vi_B_remaining']['candidate_constructions'] == 0
      and ledger['formal_table_I_calls'] == 0 and ledger['formal_table_I_required_calls'] == 22500)

failures = [r for r in checks if not r['passed']]
report = {
    'schema': 'P4_CBIRRT_D_PATH_INDEPENDENT_STATIC_REVIEW_V1',
    'status': 'PASS_P_COMPLETE_SAVED_QUEUE_AND_STATIC_SCIENCE_REVIEW' if not failures else 'FAIL_STATIC_REVIEW',
    'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    'reviewer': 'nr_local_independent_post; independent of P implementation',
    'personnel_independent': True,
    'checks_total': len(checks), 'checks_passed': len(checks)-len(failures), 'checks_failed': len(failures),
    'failures': failures, 'checks': checks, 'reviewed_sha256': bound,
    'physical_loop_AST_sha256': hashlib.sha256(loop_ast.encode()).hexdigest(),
    'counted_wrapper_AST_sha256': hashlib.sha256(counted_ast.encode()).hexdigest(),
    'new_scientific_calls': 0, 'runner_import_calls': 0, 'protocol_generation_calls': 0,
    'prior_generation_calls': 0, 'claims_created': 0, 'physical_path_qualified': False,
    'limits': [
        'Static source and saved-array review only; root must freeze actual full queue, latest charged prior and committed protocol.',
        'P has not executed. This report does not qualify413 nodes, closure, branches, limits, collision, EOF or actual costs.',
        'Complete physical P and personnel-independent saved POST are required; no CCD/solid rod/omitted pair/performance/full paper claim.',
        'Original S01/D/H STOP and UNKNOWN remain unchanged; no extra VI or formal planning authorized.',
    ],
}
with OUT.with_suffix('.json').open('x') as stream:
    json.dump(report,stream,ensure_ascii=False,indent=2);stream.write('\n')
summary = f'''# CBiRRT D P 完整保存路径：人员独立静态审查

实际 {report['checks_passed']}/{report['checks_total']}、失败{len(failures)}，状态 `{report['status']}`。仅静态读源码/AST及已保存数组，personnel_independent=true；零runner import、协议/prior/claim、科学或物理调用。

P完整科学节点循环及counted FK/J包装AST分别与原已验证PCS path源码逐节点相同（loop SHA `{report['physical_loop_AST_sha256']}`）。闭链位置/旋转maxabs各1e-5、原限位、全部关联边被动branch、64epsilon、严格full12叶距<.05及v3 native/aligned原碰撞门保持。真实S02与独立5284报告、两行原stdout/raw/版本链先核；保存完整413节点/412叶，四真M109/145/33/129，原false M2及fallback顺序保留，不验前缀。

120wall/240CPU和2048完整队列帽、最新charged ledger替换一次、原3600/7200总帽、独占GNUtime真实父PID/argv/inode、worker登记及进程组/EOF/回收和最终hash/费用门已审。P尚未执行，source EXACT仍候选；root须冻结真实完整队列与最新账、提交后唯一执行，并另做人员独立保存后审。静态通过不证明物理路径、CCD/全部实体碰撞对、性能优势或完整论文。
'''
with OUT.with_suffix('.md').open('x') as stream:stream.write(summary)
print(json.dumps({'status':report['status'],'passed':report['checks_passed'],'total':report['checks_total'],
                  'failures':failures,'report':str(OUT.with_suffix('.json')),
                  'report_sha256':hashlib.sha256(OUT.with_suffix('.json').read_bytes()).hexdigest()},ensure_ascii=False))
if failures:raise SystemExit(1)
