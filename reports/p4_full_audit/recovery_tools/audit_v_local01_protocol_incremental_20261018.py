#!/usr/bin/env python3
"""Read only the fixed V local protocol seam; reuse larger prior certificates."""
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DRAFT = ROOT / 'configs/p4_d080/v_pcs_local01_v1.DRAFT.json'
RUNNER = ROOT / 'scripts/p4_d080/qualify_v_pcs_local_v1_draft.py'
SUP = ROOT / 'scripts/p4_d080/supervise_v_pcs_local_v1_draft.py'
FIXTURE = ROOT / 'configs/p4_d080/v_pcs_local_fixed_saved_v1.DRAFT.json'
FIELD = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL_FROZEN_FIELD_MAP_DRAFT_20261018.md'
PRE = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL_FIXED_PRE_DRAFT_20261018.md'
GATE = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL_COMPOSITE_BUILD_GATE_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
OUT = ROOT / 'reports/P4_D080_ENV_V_PCS_LOCAL01_PROTOCOL_INCREMENTAL_INDEPENDENT_PRE_20261018'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def path(n):
    p = Path(n)
    return p if p.is_absolute() else ROOT / p

def load(p):
    return json.loads(path(p).read_text())

checks = []
def check(name, ok):
    checks.append({'check': name, 'passed': bool(ok)})

d, f, g = load(DRAFT), load(FIXTURE), load(GATE)
check('Exact reviewed draft field-map PRE and13-check incremental gate bytes',
      sha(DRAFT) == '01ce5307a9283506dee8478dc8d2d808b5fa9e4bbfd75bc94d676868cc48ffd3'
      and sha(FIELD) == 'd395447df0b61506146457a1fb72f2f2b673e8ccec5615fba2150ca21881c85f'
      and sha(PRE) == 'c0756b74b9c619ed2840f4d0da5fadadfd6405d358f00850002942a62381ea27'
      and sha(GATE) == '307a989b8a093d9ace4bb458a38c96a8684afcb6faf04c912939418363f75c58'
      and g['checks_total'] == g['checks_passed'] == 13 and g['checks_failed'] == 0)
check('Top-level local-only identity flags false now formal false and exact30wall60CPU cap',
      d['schema'] == 'P4_D080_V_PCS_LOCAL_RUN_FROZEN_V1'
      and d['environment'] == 'V' and d['method'] == 'PCS'
      and d['run_id'] == '20261018_R2_D080_V_PCS_LOCAL01'
      and d['classification'] == 'CORRECTED_COMAU_APC_ALIGNED_V3_ORIGINAL_FIXED_PCS_RBS_CONTROL_RECONSTRUCTED_A02'
      and all(d[k] is False for k in ['frozen', 'scientific_execution_authorized', 'independent_review_passed', 'formal_execution_authorized'])
      and d['budget'] == {'wall_s': 30, 'cpu_s': 60})
p = d['driver_protocol']
check('Exact fixed18 per-mode requests caps and36public38stdout setup contract retained',
      sha(FIXTURE) == d['fixture_sha256'] == '1c7ced65d4652529c9d956142ab4264746aa30b7c0809cf4b2731a655b33401c'
      and p['schema'] == 'P4_D080_V_PCS_LOCAL_FROZEN_V1' and p['environment'] == 'V' and p['method'] == 'PCS'
      and p['api_local_only'] is True and all(p[k] is False for k in ['frozen', 'scientific_execution_authorized', 'independent_review_passed'])
      and p['requests'] == f['requests'] and len(p['requests']) == 18
      and Counter(x['op'] for x in p['requests']) == {'identify': 2, 'project': 8, 'rbs': 4, 'reconstruct': 4}
      and p['caps'] == f['caps_per_binary_proposal']
      and d['maxima'] == f['global_maxima_proposal']
      and d['maxima'] == {'public_requests': 36, 'project_fixed': 512, 'independent_unique_nodes': 256,
                         'source_processes': 2, 'setup_calls': 2, 'solve_calls': 0, 'formal_calls': 0}
      and d['schedule_modes'] == ['trace', 'plain'])
prior = d['prior']; ledger_path = path(prior['ledger']); ledger = load(ledger_path)
check('Exact latest V32 charged prior50 executions costs and historical UNKNOWN retained',
      prior['ledger'] == 'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V32.json'
      and sha(ledger_path) == prior['ledger_sha256'] == 'f490eda1eb4083b773e1329306b3e01461f07901e64736629d2a8eb3000a9fe4'
      and ledger['schema'] == 'P4_R2_RECOVERY_ACTUAL_LEDGER_V32' and ledger['count'] == 50
      and prior['wall_s'] == ledger['conservative_r2_sum_wall_s'] == 1091.3322264829947
      and prior['cpu_s'] == ledger['conservative_r2_sum_cpu_s'] == 915.032232
      and prior['historical_unmeasured_tail'] == 'RETAINED_UNKNOWN'
      and ledger['executions'][-1]['execution'] == d['build_assets']['execution']
      and ledger['d080_formal_table_I_required_calls'] == 18000 and ledger['d080_formal_table_I_calls'] == 0
      and ledger['d080_VI_status'] == 'ARCHIVED_OUT_OF_APPROVED_SCOPE_NO_NEW_EXECUTION')
ba = d['build_assets']; postpath = path(ba['personnel_independent_POST']); post = load(postpath); ex = path(ba['execution'])
check('Actual BUILD02 independent composite ADDENDUM and tail execution exact SHA',
      sha(postpath) == ba['post_sha256'] == '3a04f69aedc861166de04e147046a19ea35500b13e73270acb4e742ec7e9f7f8'
      and sha(ex) == ba['execution_sha256'] == post['execution_sha256'] == '493286682200e4eee003b7c1eae70ed91d35fbd56953bb44d4671343dd58e0a6'
      and post['status'] == 'PASS_SAME_SOURCE_COMPOSITE_BUILD02_TAIL_SAVED_POST'
      and post['original_BUILD01_engineering_build_qualified'] is False
      and post['source_planning_qualified'] is False and post['independent_path_qualified'] is False)
check('Both exact reused plain and new trace ELF bytes match actual composite certificate',
      set(ba['targets']) == {'plain', 'trace'}
      and all(ba['targets'][t['mode']] == {'binary': t['binary'], 'binary_sha256': t['binary_sha256']}
              and sha(t['binary']) == t['binary_sha256'] for t in post['build_targets']))
required = [RUNNER, SUP, FIXTURE, PRE,
            ROOT / 'scripts/qualify_p4_full_r2_abb_sbl_pcs_setup_draft.py',
            ROOT / 'scripts/p4_d080/build_v_pcs_local_v1_draft.py',
            ROOT / 'reports/P4_D080_ENV_V_PCS_MONOTONIC_COMPAT_INDEPENDENT_PRE_20261018.json',
            ledger_path, postpath, ex, path(post['source_failure_POST']), path(post['receipt']), path(post['internal_receipt'])]
check('Current OWN and latest ledger/composite/failure/receipt key bindings exact; no4823-file rehash',
      all(d['bound_files_sha256'].get(str(p.resolve())) == sha(p) for p in required)
      and sha(RUNNER) == 'aafb13d2bfb1932c478e110206677280ce0e476eead8959715818d8d3ecd3b7f'
      and sha(SUP) == '2a0920c0eb6dfe2684366f1acf541a0c69c2797ef3bbc89d0a5c82578cfed4d1')
manifest = load(ROOT / '/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json')
model, = [m for m in manifest['entries'] if m['model'] == 'V' and m['variant'] == 'aligned']
expected_meshes = {str(Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/V_aligned/simulator') / n): h
                   for n, h in model['mesh_sha256'].items()}
check('Original V27 mesh identity map and87pair policy reused without model calls',
      d['runtime_meshes_sha256'] == expected_meshes and len(expected_meshes) == 27
      and model['active_call_statement_count'] == 87 and model['tcp_observation_version'] == 3
      and all(d['bound_files_sha256'].get(n) == h for n, h in expected_meshes.items()))
ext = d['external_supervision']; run = d['run_id']; preload = Path('/etc/ld.so.preload')
check('External uniqueGNUtime paths tool hashes and actual absent preload state exact',
      ext['required'] is True and ext['format'] == '%e %U %S %x'
      and all(ext[k] == f'results/p4_full/{run}.supervision.{suffix}'
              for k, suffix in [('sibling_path', 'time.txt'), ('metadata_path', 'jsonl'), ('stderr_path', 'stderr.log'), ('charge_path', 'charge.json')])
      and ext['time_binary_sha256'] == sha('/usr/bin/time') and ext['python_binary_sha256'] == sha('/usr/bin/python3')
      and ext['elapsed_decimal_upper_padding_s'] == .01 and ext['CPU_user_plus_system_upper_padding_s'] == .02
      and ext['final_independent_POST_required'] is True
      and d['system_preload_state'] == {'path': '/etc/ld.so.preload', 'exists': False, 'sha256': None} and not preload.exists())
result = {
    'schema': 'P4_D080_V_PCS_LOCAL01_PROTOCOL_INCREMENTAL_PERSONNEL_INDEPENDENT_PRE_V1',
    'status': 'PASS_INCREMENTAL_PROTOCOL_SEAM_STATIC_ONLY' if all(x['passed'] for x in checks) else 'FAIL_STATIC_RETAINED',
    'reviewer': 'v_engineering_resume: independent of root stdlib protocol preparation',
    'personnel_independent_for_this_delta': True,
    'personnel_independence_limit': 'Reviewer authored early V driver/header/transform and early local draft; this review only independently checks root protocol metadata against fixed prior certificates, not the original scientific source.',
    'draft_protocol': str(DRAFT.relative_to(ROOT)), 'draft_protocol_sha256': sha(DRAFT),
    'field_map_sha256': sha(FIELD), 'PRE_sha256': sha(PRE),
    'reused_gate_certificate': str(GATE.relative_to(ROOT)), 'reused_gate_certificate_sha256': sha(GATE),
    'latest_V32_sha256': sha(ledger_path), 'bound_map_existing_entries': len(d['bound_files_sha256']),
    'checks': checks, 'checks_total': len(checks), 'checks_passed': sum(x['passed'] for x in checks),
    'checks_failed': sum(not x['passed'] for x in checks),
    'allowed_final_freeze_transform': {
        'create_new_file_preserve_DRAFT': True,
        'set_only_these_six_existing_flags_to_true': ['frozen', 'independent_review_passed', 'scientific_execution_authorized',
            'driver_protocol.frozen', 'driver_protocol.independent_review_passed', 'driver_protocol.scientific_execution_authorized'],
        'formal_execution_authorized_must_remain_false': True,
        'allowed_additive_metadata': 'Exact SHA binding/reference to this protocol-seam certificate and the exact13-check incremental gate certificate; their original29-check certificate chain may also be bound. All other existing fields/values/bindings must remain equal.',
        'new_formal_protocol_must_be_committed_with_runtime_OWN_and_certificates_before_unique_supervisor_execution': True,
        'allowed_execution_scope': 'One fixed V source-local/transport30wall60CPU only; no oracle, planner/solve, formal calls or new scientific design.',
    },
    'zero_new_calls': dict.fromkeys(['runner_import', 'describe', 'compile', 'binary', 'FK', 'Jacobian', 'IK', 'NR', 'PQP', 'RBS', 'RNG', 'solve', 'freeze', 'accounting_append'], 0),
    'limits': ['No full4823 union rehash or219 scientific-body repeat; reused exact certificate gates and root byte-only union are still enforced by runtime preflight.',
               'Source-local success means observed plain/trace source output and a pending queue only, not independent physical/branch/limits/collision/leaf/path qualification.',
               'Original BUILD01false, historical object STOP hash UNKNOWN, base composite metadata FAIL and all old results remain unchanged.']
}
for suffix, value in [('.json', json.dumps(result, ensure_ascii=False, indent=2) + '\n'),
                      ('.md', '# V local01协议接缝增量独审\n\n' + result['status']
                       + f"；{result['checks_passed']}/{len(checks)}。精确DRAFT01ce5307、V32 f490eda1、两ELF、36public/38stdout、30/60与原固定输入匹配。仅查关键接缝，未重复4823或219。\n\n"
                       + '允许root保留DRAFT原字节，在新正式文件中只将顶层与driver的frozen/review/scientific_authorization共六flag置true，追加本证书和13项组合门证书的精确binding/reference；formal=false和全部其他既有字段/绑定不变。唯一source-local仍只产原始来源/一致性/待验节点，独立Comau物理、branch、原界、87pair碰撞和叶距另冻。最终协议及OWN/证书须先commit，再唯一supervisor执行。\n\n'
                       + '人员独立性只针对root本次协议metadata；本审者是早期V科学源码/草案作者，不宣称重新独审其原科学体。无模型/import/describe/编译/执行/冻结/入账。\n')]:
    with Path(str(OUT) + suffix).open('x') as stream:
        stream.write(value)
print(json.dumps({'status': result['status'], 'checks_passed': result['checks_passed'], 'checks_total': len(checks),
                  'outputs_sha256': {s: sha(str(OUT) + s) for s in ['.json', '.md']}}, ensure_ascii=False))
