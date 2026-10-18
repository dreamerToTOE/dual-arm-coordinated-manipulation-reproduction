#!/usr/bin/env python3
"""Stdlib saved-only review of others' V local composite-build gate delta."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'work/preserved_v_pcs_local_before_composite_BUILD02_gate_20261018/qualify_v_pcs_local_v1_draft.py'
RUNNER = ROOT / 'scripts/p4_d080/qualify_v_pcs_local_v1_draft.py'
SUP = ROOT / 'scripts/p4_d080/supervise_v_pcs_local_v1_draft.py'
PRE = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL_FIXED_PRE_DRAFT_20261018.md'
OLD_PRE = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
POST = ROOT / 'reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_COMPOSITE_SAVED_INDEPENDENT_POST_ADDENDUM_20261018.json'
FAILURE = ROOT / 'reports/P4_D080_ENV_V_PCS_BUILD01_FAILURE_SAVED_INDEPENDENT_POST_20261018.json'
FIXTURE = ROOT / 'configs/p4_d080/v_pcs_local_fixed_saved_v1.DRAFT.json'
SELF = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL_COMPOSITE_ACTUAL_GATE_SELF_STATIC_20261018.json'
OUT = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL_COMPOSITE_BUILD_GATE_INCREMENTAL_INDEPENDENT_PRE_20261018'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def path(n):
    p = Path(n)
    return p if p.is_absolute() else ROOT / p

def load(p):
    return json.loads(path(p).read_text())

def dump(n):
    return ast.dump(n, include_attributes=False)

checks = []
def check(name, passed):
    checks.append({'check': name, 'passed': bool(passed)})

old, new = BASE.read_text(), RUNNER.read_text()
a, b = ast.parse(old), ast.parse(new)
ad = {n.name: n for n in a.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
bd = {n.name: n for n in b.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
expected = {
    RUNNER: 'aafb13d2bfb1932c478e110206677280ce0e476eead8959715818d8d3ecd3b7f',
    SUP: '2a0920c0eb6dfe2684366f1acf541a0c69c2797ef3bbc89d0a5c82578cfed4d1',
    PRE: 'c0756b74b9c619ed2840f4d0da5fadadfd6405d358f00850002942a62381ea27',
    POST: '3a04f69aedc861166de04e147046a19ea35500b13e73270acb4e742ec7e9f7f8',
    FAILURE: '3dca76842b2f50751bd9c0455b592dff89dd4dbf7c09fbf7dfcf72c487d9576a',
    FIXTURE: '1c7ced65d4652529c9d956142ab4264746aa30b7c0809cf4b2731a655b33401c',
    SELF: 'c37d09fac22f760770e6d3d0410a49467a6bebd5c209cb0413c1223d7d3df2fb',
}
previous = load(OLD_PRE)
check('Exact saved 6e10abec baseline and prior29-check certificate reused without rerun',
      sha(BASE) == '6e10abec76e505318ecc9f83b0c027699491c6634130d64e9fd1994d819e4544'
      and sha(OLD_PRE) == 'bace889bf78635d047a073ac2f364b547472ffa1b15aa1cab7b159f9094889e0'
      and previous['checks_total'] == previous['checks_passed'] == 29 and previous['checks_failed'] == 0)
check('Exact final runner supervisor PRE fixture and actual self/POST bytes', all(sha(p) == h for p, h in expected.items()))
unchanged = {k: dump(ad[k]) == dump(bd[k]) for k in ad if k != 'preflight'}
check('Budget Session supervisor_proof collect_semantics independent_nodes execute main entire AST unchanged',
      set(ad) == set(bd) and all(unchanged.values()))
allowed = {'BUILD_RUN', 'BUILD_COMPOSITE_POST', 'BUILD_COMPOSITE_POST_SHA', 'BUILD01_FAILURE_POST',
           'BUILD01_FAILURE_POST_SHA', 'BUILD01_EXEC_SHA'}
def module_without_gate(tree):
    rows = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'preflight':
            continue
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in allowed for t in node.targets):
            continue
        rows.append(dump(node))
    return rows
check('Only build identity constants and preflight differ; no new imports or runtime bodies',
      module_without_gate(a) == module_without_gate(b))
old_prefix = old[old.index('def preflight('):old.index('    build_path = path(spec[')]
new_prefix = new[new.index('def preflight('):new.index('    require(isinstance(BUILD_COMPOSITE_POST_SHA,')]
old_suffix = old[old.index('    collision = load(B.COL_ROOT'):old.index('\ndef collect_semantics')]
new_suffix = new[new.index('    collision = load(B.COL_ROOT'):new.index('\ndef collect_semantics')]
check('Preflight scientific input/prior/mesh/scope/commit guards outside build block unchanged',
      old_prefix == new_prefix and old_suffix == new_suffix)
check('Fixed36 requests and 38 stdout contract retain prior bytes and constants',
      sha(FIXTURE) == expected[FIXTURE] and 'PUBLIC_REQUESTS_PER_BINARY = 18' in new
      and 'STDOUT_JSON_ROWS_PER_BINARY = 1 + PUBLIC_REQUESTS_PER_BINARY' in new
      and 'driver[\'requests\'] == fixture[\'requests\']' in new)
p = load(POST); epath = path(p['execution']); e = load(epath); f = load(FAILURE)
check('Actual exact pinned personnel-independent ADDENDUM5/5 reuses64 and preserves base metadata FAIL',
      p['schema'] == 'P4_D080_V_PCS_BUILD02_TAIL_COMPOSITE_SAVED_INDEPENDENT_POST_V1'
      and p['status'] == 'PASS_SAME_SOURCE_COMPOSITE_BUILD02_TAIL_SAVED_POST'
      and p['personnel_independent'] is True and p['engineering_build_qualified'] is True
      and p['composite_build_qualified'] is True and p['external_supervision_qualified'] is True
      and p['checks_total'] == p['checks_passed'] == 5 and p['checks_failed'] == 0
      and p['base_passed_checks_reused_without_rerun'] == 64
      and p['base_failed_check_preserved']['passed'] is False)
check('Actual tail execution and original BUILD01false STOP historical object UNKNOWN separate',
      sha(epath) == p['execution_sha256'] == '493286682200e4eee003b7c1eae70ed91d35fbd56953bb44d4671343dd58e0a6'
      and e['schema'] == 'P4_D080_V_PCS_BUILD02_TAIL_EXECUTION_V1'
      and e['status'] == 'BUILT_TAIL_NOT_QUERIED_PENDING_COMPOSITE_INDEPENDENT_POST'
      and e['run_id'] == '20261018_R2_D080_V_PCS_BUILD02_TAIL'
      and p['original_BUILD01_engineering_build_qualified'] is False
      and p['source_failure_POST_sha256'] == sha(FAILURE)
      and f['engineering_build_qualified'] is False
      and f['original_execution_status'] == e['original_BUILD01_status_retained'] == 'STOP_ENGINEERING_FAILURE_RETAINED_PREFIX'
      and f['execution_sha256'] == e['original_BUILD01_execution_sha256'] == '0027c3c1c64d72cf02903b383ea7bbf3fb417b2b0107c6a673398cb8db825a2a'
      and f['original_STOP_object_sha256_status'] == e['original_STOP_object_sha256_status'] == 'UNKNOWN_NOT_RECORDED_AT_STOP')
cpath, rpath = path(p['receipt']), path(p['internal_receipt'])
c, r = load(cpath), load(rpath)
check('Actual tail exact charge receipt execution SHA and unchanged monotonic-envelope cost basis',
      sha(cpath) == p['external_charge_sha256'] == p['receipt_sha256']
      and sha(rpath) == p['internal_receipt_sha256'] == c['receipt_sha256']
      and c['execution_sha256'] == r['execution_sha256'] == sha(epath)
      and c['charge_basis'] == p['charge_basis'] == 'EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
      and c['monotonic_envelope_valid'] is True and p['monotonic_envelope_qualified'] is True
      and c['wall_s'] == p['upper_wall_s'] and c['cpu_s'] == p['upper_cpu_s'])
targets = p['build_targets']
check('Reused plain and newly linked trace exact ELF bytes source executions statuses and compile/link counts',
      [t['mode'] for t in targets] == ['plain', 'trace']
      and [t['status'] for t in targets] == ['REUSED_BUILT_NOT_QUERIED', 'BUILT_NOT_QUERIED']
      and [t['new_compile_calls'] for t in targets] == [0, 2]
      and [t['new_link_calls'] for t in targets] == [0, 1]
      and targets[0]['source_execution_sha256'] == f['execution_sha256']
      and targets[1]['source_execution_sha256'] == sha(epath)
      and len(e['targets']) == 2
      and all(sha(t['binary']) == t['binary_sha256']
              and sum(x['mode'] == t['mode'] and x['binary'] == t['binary']
                      and x['binary_sha256'] == t['binary_sha256'] and x['status'] == t['status'] for x in e['targets']) == 1
              for t in targets))
gate = new[new.index('    require(isinstance(BUILD_COMPOSITE_POST_SHA,'):new.index('    collision = load(B.COL_ROOT')]
check('Runtime gate requires exact pinned POST schema status SHA oldfailure and both observed binary bytes',
      all(s in gate for s in ['sha(post_path) == spec[\'build_assets\'][\'post_sha256\'] == BUILD_COMPOSITE_POST_SHA',
          "post['original_BUILD01_engineering_build_qualified'] is False", "old_failure['engineering_build_qualified'] is False",
          "'UNKNOWN_NOT_RECORDED_AT_STOP'", "sha(frozen['binary']) == target['binary_sha256'] == frozen['binary_sha256'] == observed['binary_sha256']"]))
check('All five composite and retained failure evidence files explicitly required in frozen asset SHA map',
      "for filename in [BUILD_COMPOSITE_POST, BUILD01_FAILURE_POST, build_path, path(post['receipt']), path(post['internal_receipt'])]:" in gate
      and "spec['bound_files_sha256'].get(str(filename.resolve())) == sha(filename)" in gate)
check('30wall60CPU and R2 budgets unchanged; no source/planning/path proof promoted by engineering certificate',
      unchanged['Budget'] and "spec['budget'] == {'wall_s': 30, 'cpu_s': 60}" in new
      and p['source_planning_qualified'] is False and p['independent_path_qualified'] is False
      and unchanged['independent_nodes'] and unchanged['execute'])

result = {
    'schema': 'P4_D080_V_PCS_LOCAL_COMPOSITE_BUILD_GATE_INCREMENTAL_PERSONNEL_INDEPENDENT_PRE_V1',
    'status': 'PASS_INCREMENTAL_COMPOSITE_BUILD_GATE_STATIC_ONLY' if all(c['passed'] for c in checks) else 'FAIL_STATIC_RETAINED',
    'reviewer': 'v_engineering_resume: independent of sbl_path_resume composite gate delta',
    'personnel_independent_for_this_delta': True,
    'personnel_independence_limit': 'Reviewer authored original V driver/header/transform and early local draft; review is only others composite-build gate increment relative to independently reviewed 6e10abec. No re-review claim for those earlier scientific bodies.',
    'reused_prior29_checks_without_rerun': {'path': str(OLD_PRE.relative_to(ROOT)), 'sha256': sha(OLD_PRE), 'checks': 29},
    'baseline_runner_sha256': sha(BASE),
    'source_sha256': {str(k.relative_to(ROOT)): sha(k) for k in expected},
    'actual_tail_execution_sha256': sha(epath),
    'unchanged_named_AST_bodies': unchanged,
    'checks': checks,
    'checks_total': len(checks), 'checks_passed': sum(c['passed'] for c in checks),
    'checks_failed': sum(not c['passed'] for c in checks),
    'zero_new_calls': dict.fromkeys(['runner_import', 'describe', 'compile', 'binary', 'FK', 'Jacobian', 'IK', 'NR', 'PQP', 'RBS', 'RNG', 'solve', 'freeze', 'accounting_append'], 0),
    'limits': ['Actual local source run not executed by this reviewer.', 'Root must freeze current V32 charged prior and exact runtime protocol before unique local30/60.', 'No independent math/branch/limits/collision/path certificate; successful local output remains pending independent qualification.', 'BUILD01false, original object STOP hash UNKNOWN and first composite metadata FAIL remain unchanged.']
}
for ext, value in [('.json', json.dumps(result, ensure_ascii=False, indent=2) + '\n'),
                   ('.md', '# V local组合工程门增量独审\n\n'
                    + result['status'] + f"；{result['checks_passed']}/{len(checks)}。只审相对已审6e10abec的他人build门增量，不重复29/219。\n\n"
                    + '固定36请求、38 stdout、Budget/Session/proof/collect/execute/independent_nodes/main AST不变；新增门精确绑定实际BUILD02 ADDENDUM3a04f69、旧BUILD01false/STOP历史对象SHA UNKNOWN、plain复用/trace新链接的两ELF及费用收据链。旧BUILD01失败与首份组合metadata FAIL保留。\n\n'
                    + '本审查者是早期V driver/header/transform与local草案作者，仅对此次他人build门增量具人员独立性。无新import/describe/模型/编译/科学/冻结/入账；root须冻结最新V32及唯一30wall/60CPU。成功source结果仍需独立物理/分支/限位/碰撞/叶距资格。\n\n'
                    + '\n'.join('- ' + c['check'] + ': ' + ('PASS' if c['passed'] else 'FAIL') for c in checks) + '\n')]:
    with Path(str(OUT) + ext).open('x') as f:
        f.write(value)
print(json.dumps({'status': result['status'], 'checks_passed': result['checks_passed'], 'checks_total': len(checks),
                  'outputs_sha256': {ext: sha(str(OUT) + ext) for ext in ['.json', '.md']}}, ensure_ascii=False))
