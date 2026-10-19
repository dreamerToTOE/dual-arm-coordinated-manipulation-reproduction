#!/usr/bin/env python3
"""Pure saved-ledger validation with one explicitly audited preflight exception.

No model, binary, compiler, subprocess or import-time filesystem execution.
Normal B.validate_prior rows retain its exact original body and predicates.
Only one immutable 20261018 V BUILD01 missing-execution/receipt attempt has a
separate saved-only two-observation cost certificate; its failure is retained.
"""
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RECOVERED_RUN='20261018_R2_D080_V_RRT_PCS_BUILD01'
RECOVERED_BASIS='EXTERNAL_PREFLIGHT_TWO_OBSERVATION_ENVELOPE_ONCE'
ORIGINAL_CHARGE_SHA='a928bd149ec0084f040f460c0ac771eefdbe2f4fb98514c318a52324ddd0f756'
ORIGINAL_FILES={
    'charge':('results/p4_full/'+RECOVERED_RUN+'.supervision.charge.json',ORIGINAL_CHARGE_SHA),
    'time':('results/p4_full/'+RECOVERED_RUN+'.supervision.time.txt','c8ad42b5726c63bd680400335bb4fb088dc349c8f5a5440fe8461384bc4b329f'),
    'metadata':('results/p4_full/'+RECOVERED_RUN+'.supervision.jsonl','158a3e3527db8871b2f024fd0d5d8bf906ccee0ed76b8673c1474bb523598e6d'),
    'stderr':('results/p4_full/'+RECOVERED_RUN+'.supervision.stderr.log','6f6ccafe40576c7ff809a94ad3bfb18bda686220e39baba072d4bdf521031191'),
}

def require(ok,reason):
    if not ok:raise RuntimeError(reason)

def path(value):
    p=Path(value);return p if p.is_absolute()else ROOT/p

def sha(value):return hashlib.sha256(path(value).read_bytes()).hexdigest()
def load(value):return json.loads(path(value).read_bytes())

def validate_recovered_preflight(row,post_path,post,time_path,charge_path,charge,evidence):
    require(row['run_id']==RECOVERED_RUN and row['charge_basis']==RECOVERED_BASIS
        and row['execution']=='results/p4_full/'+RECOVERED_RUN+'/execution.json',
        'ONLY_SINGLE_EXPLICIT_V_BUILD01_PREFLIGHT_RECOVERY_ALLOWED')
    execution_path=path(row['execution']);recovery=load(execution_path)
    require(recovery['schema']=='SAVED_ONLY_PREFLIGHT_RECOVERY' and recovery['run_id']==RECOVERED_RUN
        and recovery['source_execution_created_during_attempt']is False
        and type(recovery['solve_calls'])is int and recovery['solve_calls']==0
        and type(recovery['compile_calls'])is int and recovery['compile_calls']==0
        and type(recovery['binary_execution_calls'])is int and recovery['binary_execution_calls']==0
        and recovery['original_charge_sha256']==ORIGINAL_CHARGE_SHA
        and recovery['charge_basis']==RECOVERED_BASIS,
        'SAVED_ONLY_RECOVERY_IS_NOT_AN_ACTUAL_ENGINEERING_OR_SCIENTIFIC_EXECUTION')
    for filename,digest in ORIGINAL_FILES.values():
        require(sha(filename)==digest,'IMMUTABLE_ORIGINAL_PREFLIGHT_EVIDENCE_CHANGED '+filename)
        evidence[str(path(filename))]=digest
    require(charge_path.resolve()==path(ORIGINAL_FILES['charge'][0]).resolve()
        and time_path.resolve()==path(ORIGINAL_FILES['time'][0]).resolve()
        and path(charge['source_execution']).resolve()==execution_path.resolve()
        and charge['run_id']==RECOVERED_RUN and charge['execution_sha256']is None and charge['receipt_sha256']is None
        and not path(charge['receipt']).exists() and charge['monotonic_envelope_valid']is False
        and charge['external_supervision_qualified']is False and charge['completed_process_exit0']is False
        and charge['timing_valid']is True and charge['time_inode_unchanged']is True
        and charge['wall_CPU_caps_pass']is False,'ORIGINAL_MISSING_RECEIPT_NULL_HASHES_AND_FAIL_MUST_REMAIN')
    fields=time_path.read_text().strip().split()
    require(fields==['0.08','0.05','0.01','1']==charge['time_fields']
        and charge['measured_child_exit']==charge['time_returncode']==1,
        'ORIGINAL_NONZERO_PREFLIGHT_GNUTIME_FIELDS_REQUIRED')
    elapsed,user,system=(Decimal(v)for v in fields[:3])
    outer_wall=Decimal(str(charge['fallback_observed_outer_wait_wall_s']))
    outer_cpu=Decimal(str(charge['fallback_reaped_children_CPU_s']))
    require(all(v.is_finite()and v>=0 for v in(elapsed,user,system,outer_wall,outer_cpu)),
        'FINITE_ORIGINAL_TWO_OBSERVATION_COSTS_REQUIRED')
    wall=float(max(elapsed+Decimal('.01'),outer_wall+Decimal('.01')))
    cpu=float(max(user+system+Decimal('.02'),outer_cpu+Decimal('.02')))
    require(wall==0.098610285998584==charge['wall_s']==row['charged_wall_s']==recovery['wall_s']
        and cpu==0.092844==charge['cpu_s']==row['charged_cpu_s']==recovery['cpu_s'],
        'EXACT_DECIMAL_TWO_OBSERVATION_ENVELOPE_CHARGED_ONCE_REQUIRED')
    require(sha(post_path)==row['external_post_sha256'] and post['personnel_independent']is True
        and post['external_supervision_qualified']is False and post['external_cost_qualified']is True
        and post['orphan_preflight_cost_observation_qualified']is True
        and post['checks_total']==post['checks_passed']>0
        and post['checks_failed']==0 and post['execution_sha256']==row['execution_sha256']==sha(execution_path)
        and post['upper_wall_s']==wall and post['upper_cpu_s']==cpu
        and post['external_time_sha256']==row['external_time_sha256']==sha(time_path)
        and post['external_charge_sha256']==ORIGINAL_CHARGE_SHA
        and post['source_execution_created_during_attempt']is False and post['saved_only_recovery']is True,
        'INDEPENDENT_SAVED_ONLY_RECOVERY_AND_ORIGINAL_ATTEMPT_COST_POST_REQUIRED')
    evidence[str(post_path)]=sha(post_path)


def certificate_json(filename):
    # Historical .jsonl receipts include both a single pretty JSON object and
    # one-object-per-line variants. Parse saved bytes, never execute a runner.
    raw = Path(filename).read_text()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
        require(bool(rows), 'NONEMPTY_SAVED_RECEIPT_REQUIRED')
        return rows[-1]

def validate_prior(spec,run_name,run_dir):
    RUN_NAME=run_name;RUN=Path(run_dir).resolve()
    ledger_path = path(spec['prior']['ledger']).resolve()
    ledgers = list((ROOT / 'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
    require(ledgers and ledger_path == max(ledgers, key=lambda p: int(p.stem.rsplit('V', 1)[1])).resolve(),
            'LATEST_VERSIONED_CHARGED_LEDGER_REQUIRED')
    require(sha(ledger_path) == spec['prior']['ledger_sha256'], 'PRIOR_LEDGER_CHANGED')
    ledger = load(ledger_path)
    actual = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'results/p4_full').glob('*_R2_*/execution.json') if p.parent != RUN}
    actual.update({str(p.relative_to(ROOT)): sha(p) for p in (ROOT / 'results/p4_d080').glob('*/execution.json') if p.parent != RUN})
    require({r['execution']: r['execution_sha256'] for r in ledger['executions']} == actual,
            'PRIOR_LEDGER_MUST_COVER_EVERY_ACTUAL_EXECUTION')
    evidence = {str(ledger_path): sha(ledger_path)}
    for row in ledger['executions']:
        evidence[str(path(row['execution']))] = row['execution_sha256']
        if 'charged_wall_s' not in row:
            continue  # Historical unmeasured persistence tails remain UNKNOWN.
        post_path = path(row['external_post']); post = load(post_path)
        time_path = path(row['external_time'])
        charge_path = path(row['execution']).parent.parent / (row['run_id'] + '.supervision.charge.json')
        charge = load(charge_path)
        if row.get('charge_basis') == RECOVERED_BASIS:
            validate_recovered_preflight(row,post_path,post,time_path,charge_path,charge,evidence)
            continue
        require(sha(post_path) == row['external_post_sha256'] and post['personnel_independent'] is True
                and post['external_supervision_qualified'] is True and post['checks_total'] == post['checks_passed']
                and post['checks_failed'] == 0 and post['execution_sha256'] == row['execution_sha256']
                and post['upper_wall_s'] == row['charged_wall_s'] and post['upper_cpu_s'] == row['charged_cpu_s']
                and sha(time_path) == row['external_time_sha256'] == post['external_time_sha256'],
                'PRIOR_EXTERNAL_POST_EXECUTION_TIMING_CERTIFICATE_REQUIRED')
        require(sha(charge_path) == post.get('external_charge_sha256', post.get('receipt_sha256'))
                and charge['execution_sha256'] == row['execution_sha256']
                and path(charge['source_execution']).resolve() == path(row['execution']).resolve()
                and path(charge['time_file']).resolve() == time_path.resolve()
                and charge['time_sha256'] == row['external_time_sha256']
                and charge['timing_valid'] is True and charge['time_inode_unchanged'] is True,
                'PRIOR_HASHED_EXTERNAL_CHARGE_BINDING_REQUIRED')
        receipt_path = path(charge['receipt']); receipt = certificate_json(receipt_path)
        require(sha(receipt_path) == charge['receipt_sha256'] and receipt['execution_sha256'] == row['execution_sha256'],
                'PRIOR_INTERNAL_PERSISTENCE_RECEIPT_REQUIRED')
        fields = time_path.read_text().strip().split()
        require(len(fields) == 4 and fields == charge['time_fields'], 'PRIOR_EXACT_FOUR_GNUTIME_FIELDS_REQUIRED')
        elapsed, user, system = (Decimal(v) for v in fields[:3]); exit_code = int(fields[3])
        require(all(v.is_finite() and v >= 0 for v in (elapsed, user, system))
                and exit_code == charge['measured_child_exit'] == charge['time_returncode'],
                'PRIOR_FINITE_TIME_AND_EXACT_SAVED_EXIT_REQUIRED')
        basis = row['charge_basis']
        raw_wall = float(elapsed + Decimal('.01')); raw_cpu = float(user + system + Decimal('.02'))
        if basis == 'EXTERNAL_TIME_DECIMAL_UPPER_BOUND_REPLACES_INTERNAL_SAMPLE_ONCE':
            require(raw_wall == row['charged_wall_s'] == charge['wall_s']
                    and raw_cpu == row['charged_cpu_s'] == charge['cpu_s'],
                    'PRIOR_DECIMAL_UPPER_REPLACEMENT_ONCE_REQUIRED')
        elif basis == 'EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE':
            # The one historical raw-time discrepancy is independently charged
            # without rewriting its original charge. Future V charges declare
            # this basis and retain raw fields separately at their first write.
            if charge.get('charge_basis') != basis:
                require(row['run_id'] == '20261018_R2_ABB_SBL_PCS_PATH01'
                        and row['execution_sha256'] == 'cee39aae1538742e1ab54e19d28ff42a8de2c4165cf2511bb1477d69847bc1e0'
                        and sha(charge_path) == '110293de768c992b99cd75da371de7c68a189271fcfc4687da785ea4fff16a27'
                        and raw_wall == charge['wall_s'] and raw_cpu == charge['cpu_s'],
                        'ONLY_IMMUTABLE_PATH01_OLD_RAW_CHARGE_EXCEPTION_ALLOWED')
            observations = (charge['fallback_observed_outer_wait_wall_s'], charge['fallback_reaped_children_CPU_s'],
                            receipt['wall_s_through_execution_persistence'], receipt['cpu_s_through_execution_persistence'])
            require(all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in observations),
                    'FINITE_SAVED_OUTER_AND_RECEIPT_ENVELOPE_REQUIRED')
            expected_wall = float(max(elapsed + Decimal('.01'), Decimal(str(observations[0])) + Decimal('.01'),
                                      Decimal(str(observations[2])) + Decimal('.01')))
            expected_cpu = float(max(user + system + Decimal('.02'), Decimal(str(observations[1])) + Decimal('.02'),
                                     Decimal(str(observations[3])) + Decimal('.02')))
            require(post['charge_basis'] == basis and post['external_charge_sha256'] == sha(charge_path)
                    and post['internal_receipt_sha256'] == sha(receipt_path)
                    and row['charged_wall_s'] == post['upper_wall_s'] == expected_wall
                    and row['charged_cpu_s'] == post['upper_cpu_s'] == expected_cpu,
                    'PRIOR_INDEPENDENT_EXACT_MONOTONIC_ENVELOPE_CERTIFICATE_REQUIRED')
            execution = load(path(row['execution']))
            breach = {'wall': expected_wall > execution['budget']['wall_s'],
                      'cpu': expected_cpu > execution['budget']['cpu_s']}
            if any(breach.values()):
                require(row['execution_cap_breach'] == breach and post['execution_cap_breach_retained'] is True,
                        'REAL_PRIOR_CAP_BREACH_MUST_REMAIN_RECORDED_NOT_REJECTED')
            if charge.get('charge_basis') == basis:
                require(charge['wall_s'] == expected_wall and charge['cpu_s'] == expected_cpu
                        and charge['raw_GNUtime_upper_wall_s'] == raw_wall
                        and charge['raw_GNUtime_upper_cpu_s'] == raw_cpu,
                        'NEW_ENVELOPE_CHARGE_MUST_SEPARATELY_RETAIN_RAW_TIME')
        else:
            raise RuntimeError('UNKNOWN_PRIOR_CHARGE_BASIS_NO_SILENT_FALLBACK')
        for filename in (post_path, charge_path, receipt_path, time_path):
            evidence[str(filename.resolve())] = sha(filename)
        for key in ('metadata', 'stderr'):
            filename = path(charge[key])
            require(sha(filename) == charge[key + '_sha256'], 'PRIOR_SUPERVISION_LOG_CHANGED')
            evidence[str(filename.resolve())] = sha(filename)
        if 'internal_receipt' in post:
            require(path(post['internal_receipt']).resolve() == receipt_path.resolve()
                    and post['internal_receipt_sha256'] == sha(receipt_path), 'PRIOR_POST_INTERNAL_RECEIPT_CHANGED')
    for folder in (ROOT / 'results/p4_full', ROOT / 'results/p4_d080'):
        for charge in folder.glob('*.supervision.charge.json'):
            name = charge.name.removesuffix('.supervision.charge.json')
            if name == RUN_NAME:
                continue
            require((charge.parent / name / 'execution.json').is_file(), 'UNACCOUNTED_SUPERVISED_ATTEMPT_' + name)
    wall = math.fsum(row.get('charged_wall_s', row['wall_s']) for row in ledger['executions'])
    used = math.fsum(row.get('charged_cpu_s', row['cpu_s']) for row in ledger['executions'])
    require(all(math.isfinite(v) and v >= 0 for v in (wall, used))
            and wall == ledger['conservative_r2_sum_wall_s'] and used == ledger['conservative_r2_sum_cpu_s'],
            'EXACT_CURRENT_CHARGED_SUMS_REQUIRED')
    require(wall + spec['budget']['wall_s'] <= 3600 and used + spec['budget']['cpu_s'] <= 7200,
            'NO_R2_TOTAL_BUDGET_INCREASE')
    require(wall == spec['prior']['wall_s'] and used == spec['prior']['cpu_s'], 'EXACT_FROZEN_CHARGED_PRIOR_REQUIRED')
    return {'path': str(ledger_path.relative_to(ROOT)), 'sha256': sha(ledger_path),
            'wall_s': wall, 'cpu_s': used, 'evidence_sha256': evidence,
            'historical_unmeasured_tail': 'RETAINED_UNKNOWN'}
