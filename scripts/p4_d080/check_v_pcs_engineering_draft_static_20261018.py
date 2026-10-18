#!/usr/bin/env python3
"""Saved-byte and AST self-check only; no runner/transform imports or models."""
from pathlib import Path
from decimal import Decimal
import ast
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'reports/P4_D080_ENV_V_PCS_ENGINEERING_SUPERVISION_SELF_STATIC_20261018.json'
ARCHIVE = ROOT / 'work/preserved_v_pcs_engineering_before_supervisor_20261018'
rows = []

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def check(name, condition):
    rows.append({'check': name, 'pass': bool(condition)})

def read(name):
    p = Path(name)
    return p if p.is_absolute() else ROOT / p

def obj(p):
    return json.loads(Path(p).read_text())

def receipt(p):
    raw = Path(p).read_text()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [json.loads(s) for s in raw.splitlines() if s.strip()][-1]

files = ['scripts/p4_d080/build_v_pcs_local_v1_draft.py', 'scripts/p4_d080/supervise_v_pcs_build_v1_draft.py']
source = {}
for name in files:
    source[name] = read(name).read_text()
    ast.parse(source[name]); check('AST_' + name, True)
preservation = obj(ARCHIVE / 'manifest.json')
for name, value in preservation['files'].items():
    check('preserved_five_exact_' + name, sha(ARCHIVE / name) == value['sha256'])
    if name.startswith('baselines/'):
        check('unchanged_scientific_draft_' + name, sha(read(name)) == value['sha256'])
builder, supervisor = [source[n] for n in files]
for name, snippets, text in (
    ('builder', ['ACTUAL_GNUTIME_PARENT_AND_SUPERVISOR_GRANDPARENT_REQUIRED', 'EXACT_PARENT_ARGV_SOURCE_PROTOCOL_REQUIRED',
                 'EXCLUSIVE_SUPERVISION_INODE_REQUIRED', "signal.setitimer(signal.ITIMER_REAL, .02, .02)",
                 'lifecycle.live_group_cpu(proc.pid)', 'start_new_session=True', 'os.killpg(proc.pid, signal.SIGKILL)',
                 'proc.wait(timeout=2.)', 'COMPILER_GROUP_NOT_EMPTY_AFTER_KILL_WAIT', 'LATEST_VERSIONED_CHARGED_LEDGER_REQUIRED',
                 'PRIOR_INTERNAL_PERSISTENCE_RECEIPT_REQUIRED', 'PRIOR_DECIMAL_UPPER_REPLACEMENT_ONCE_REQUIRED',
                 'LATEST_CHARGED_PRIOR_CHANGED_DURING_BUILD', "('staged', state['staged'])", "('dependencies', state['dependencies'])",
                 'PROTOCOL_OR_CLAIM_CHANGED', "write_once(RUN / 'cost_receipt.json', receipt)",
                 "RUN_NAME = '20261018_R2_D080_V_PCS_BUILD01'"], builder),
    ('supervisor', ['os.O_WRONLY|os.O_CREAT|os.O_EXCL', 'pass_fds=(fd,)', "str(RUNNER),'--build','--protocol'",
                    "'cost_receipt.json'", 'time_inode_unchanged=identity_unchanged', 'independent_POST_required=True',
                    "RUN='20261018_R2_D080_V_PCS_BUILD01'"], supervisor),
):
    for item in snippets:
        check(name + '_contract_' + item, item in text)
check('no_ACTIVE_JSON_boolean_substitute', 'group_watchdog_active' not in builder and '--active-supervision' not in builder)
config = obj(read('configs/p4_d080/v_pcs_local_v1.DRAFT.json'))
check('config_remains_nonexecutable', config['frozen'] is False and config['engineering_execution_authorized'] is False
      and config['scientific_execution_authorized'] is False and config['formal_execution_authorized'] is False)
check('local_remains_unfrozen_empty', config['proposed_fixed_fixture']['requests'] == [] and config['caps'] is None and config['prior'] is None)
check('R2_run_identity_in_config', config['proposed_build_run_name'] == '20261018_R2_D080_V_PCS_BUILD01')
ledger = max((ROOT / 'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'), key=lambda p: int(p.stem.rsplit('V', 1)[1]))
prior = obj(ledger)
actual = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'results/p4_full').glob('*_R2_*/execution.json')}
actual.update({str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'results/p4_d080').glob('*/execution.json')})
check('latest_snapshot_covers_actual_executions', {r['execution']: r['execution_sha256'] for r in prior['executions']} == actual)
certificates = []
for row in prior['executions']:
    if 'charged_wall_s' not in row:
        continue
    post_path = read(row['external_post']); post = obj(post_path)
    time_path = read(row['external_time'])
    charge_path = read(row['execution']).parent.parent / (row['run_id'] + '.supervision.charge.json'); charge = obj(charge_path)
    receipt_path = read(charge['receipt']); rec = receipt(receipt_path)
    fields = time_path.read_text().strip().split(); elapsed, user, system = [Decimal(s) for s in fields[:3]]
    checks = {
        'post': sha(post_path) == row['external_post_sha256'] and post['personnel_independent'] is True
                and post['external_supervision_qualified'] is True and post['checks_total'] == post['checks_passed']
                and post['checks_failed'] == 0 and post['execution_sha256'] == row['execution_sha256'],
        'charge': sha(charge_path) == post.get('external_charge_sha256', post.get('receipt_sha256'))
                and charge['execution_sha256'] == row['execution_sha256']
                and sha(receipt_path) == charge['receipt_sha256'] and rec['execution_sha256'] == row['execution_sha256'],
        'timing': sha(time_path) == row['external_time_sha256'] == post['external_time_sha256'] == charge['time_sha256']
                and fields == charge['time_fields'] and len(fields) == 4
                and float(elapsed + Decimal('.01')) == row['charged_wall_s'] == charge['wall_s'] == post['upper_wall_s']
                and float(user + system + Decimal('.02')) == row['charged_cpu_s'] == charge['cpu_s'] == post['upper_cpu_s']
                and int(fields[3]) == charge['measured_child_exit'] == charge['time_returncode'],
        'logs': all(sha(read(charge[k])) == charge[k + '_sha256'] for k in ('metadata', 'stderr')),
    }
    for key, value in checks.items():
        check('saved_prior_' + row['run_id'] + '_' + key, value)
    certificates.append({'run_id': row['run_id'], 'post_sha256': sha(post_path), 'charge_sha256': sha(charge_path),
                         'receipt_sha256': sha(receipt_path), 'time_sha256': sha(time_path)})
check('charged_sum_exact', math.fsum(r.get('charged_wall_s', r['wall_s']) for r in prior['executions']) == prior['conservative_r2_sum_wall_s']
      and math.fsum(r.get('charged_cpu_s', r['cpu_s']) for r in prior['executions']) == prior['conservative_r2_sum_cpu_s'])
failed = [r for r in rows if not r['pass']]
report = {'schema': 'P4_D080_V_PCS_ENGINEERING_SUPERVISION_SELF_STATIC_20261018',
          'status': 'SELF_STATIC_PASS_PENDING_INDEPENDENT_REVIEW' if not failed else 'SELF_STATIC_FAIL_RETAINED',
          'checks_total': len(rows), 'checks_passed': len(rows) - len(failed), 'checks_failed': len(failed), 'checks': rows,
          'source_sha256': {name: sha(read(name)) for name in [*files, 'configs/p4_d080/v_pcs_local_v1.DRAFT.json']},
          'preservation_manifest': str((ARCHIVE / 'manifest.json').relative_to(ROOT)), 'preservation_manifest_sha256': sha(ARCHIVE / 'manifest.json'),
          'prior_snapshot': str(ledger.relative_to(ROOT)), 'prior_snapshot_sha256': sha(ledger),
          'prior_charge_s': {'wall': prior['conservative_r2_sum_wall_s'], 'cpu': prior['conservative_r2_sum_cpu_s']},
          'saved_external_certificates': certificates, 'source_body_pair_static_reused': 'reports/P4_D080_ENV_V_PCS_INDEPENDENT_ENGINEERING_GATES_20261017.json',
          'new_runner_import_transform_describe_compile_binary_model_setup_local_solve_VI_formal_calls': 0,
          'scientific_qualification_claim': False}
with OUT.open('x') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2); stream.write('\n')
print(json.dumps({'status': report['status'], 'checks_total': len(rows), 'failed': failed, 'prior': str(ledger), 'external_certificates': len(certificates)}))
