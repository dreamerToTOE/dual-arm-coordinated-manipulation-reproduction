"""Saved-only D080 successor ledger v7: successful raw/envelope costs from V30.

Preserve every prior row, sample, failure, and coverage column. Consume an
actual personnel-independent cost certificate; never create one here. New
entries require exit0, declared basis and exact execution caps; the immutable
PATH01 STOP envelope is consumed only as an already charged V29 history. Bind the
V22 saved dispatch addendum and enumerate actual calls, including failed calls. This
module is not imported by science runners and is invoked only after review.
"""
from pathlib import Path
from decimal import Decimal
import argparse
import csv
import hashlib
import itertools
import json
import math

R = Path(__file__).resolve().parents[3]
O = Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/outputs')


def load(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def new(p, value):
    with p.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def nonnegative(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def charge(row, key):
    return row.get('charged_' + key, row[key])


# Actual solve counts are separate from cost-row, success and path counts.
# This function only reads saved execution fields and the immutable V22 base.
def source_solve_accounting(rows, old, op, version):
    addp = R/'results/p4_full/20261016_RECOVERY_QUALIFICATION_SOLVE_ACCOUNTING_V22_ADDENDUM.json'
    require(sha(addp) == '316024926cbd63e1f6ca53db0be6d7cc4419b9cb3b029450f642e3529f87bcb9',
            'FIXED_V22_SOURCE_SOLVE_ADDENDUM_REQUIRED')
    add = load(addp)
    baselinep = R/add['ledger_original_bytes_preserved']['path']
    require(sha(baselinep) == add['ledger_original_bytes_preserved']['sha256'],
            'V22_SOURCE_SOLVE_BASE_LEDGER_CHANGED')
    baseline = load(baselinep)
    baseline_rows = {r['execution']: r for r in baseline['executions']}
    positive = {r['execution']['path']: r for r in add['actual_source_solve_dispatches']}
    require(len(baseline_rows) == baseline['count'] == 40 and len(positive) == 5
            and add['authoritative_counters']['total_actual_source_solve_dispatches_through_V22'] == 5,
            'V22_40_EXECUTIONS_FIVE_ACTUAL_SOURCE_DISPATCHES_REQUIRED')
    prior_paths = {r['execution'] for r in old['executions']}
    inputs = {str(addp): sha(addp), str(baselinep): sha(baselinep)}
    enumerated = []
    for row in rows:
        path = row['execution']; ep = R/path; actual = load(ep)
        require(sha(ep) == row['execution_sha256'], 'SOURCE_COUNT_EXECUTION_SHA_CHANGED')
        inputs[str(ep)] = sha(ep)
        fields = {}
        for prefix, obj in (('', actual), ('counts.', actual.get('counts', {}))):
            require(isinstance(obj, dict), 'SOURCE_COUNT_OBJECT_REQUIRED')
            for key in ('solve_dispatched', 'solve_dispatch_attempted', 'solve_calls', 'solve_calls_from_result'):
                if key in obj:
                    value = obj[key]
                    require(type(value) is int and value >= 0, 'NONNEGATIVE_INTEGER_SOURCE_COUNT_REQUIRED')
                    fields[prefix + key] = value
        zero = actual.get('zero_calls', {})
        require(isinstance(zero, dict), 'ZERO_CALLS_OBJECT_REQUIRED')
        for key in ('solve', 'planner_solve'):
            if key in zero:
                require(type(zero[key]) is int and zero[key] == 0, 'EXPLICIT_ZERO_SOLVE_MUST_BE_ZERO')
                fields['zero_calls.' + key] = 0
        dispatched = [v for k, v in fields.items() if k in ('solve_dispatched', 'counts.solve_dispatched')]
        observed = [v for k, v in fields.items() if k.endswith('solve_calls') or k.endswith('solve_calls_from_result') or k.startswith('zero_calls.')]
        if dispatched:
            count = dispatched[0]; basis = 'SAVED_ACTUAL_SOLVE_DISPATCHED'
            require(all(v == count for v in dispatched + observed), 'SOURCE_SOLVE_COUNT_FIELDS_DISAGREE')
        elif observed:
            count = observed[0]; basis = 'SAVED_EXPLICIT_SOLVE_CALL_OR_ZERO'
            require(all(v == count for v in observed), 'SOURCE_SOLVE_CALL_FIELDS_DISAGREE')
        else:
            require(path in baseline_rows and path not in positive,
                    'NEW_EXECUTION_REQUIRES_ACTUAL_SOLVE_OR_EXPLICIT_ZERO_FIELD')
            count = 0; basis = 'FIXED_V22_ADDENDUM_BASELINE_NO_SOURCE_DISPATCH'
        attempted = [v for k, v in fields.items() if k.endswith('solve_dispatch_attempted')]
        require(not attempted or (count == 0 and all(v == 0 for v in attempted))
                or (dispatched and all(v >= count for v in attempted)),
                'ATTEMPT_WITHOUT_ACTUAL_DISPATCH_COUNT_IS_UNKNOWN')
        if path in baseline_rows:
            require(row['execution_sha256'] == baseline_rows[path]['execution_sha256'],
                    'V22_BASE_EXECUTION_CHANGED')
            expected = positive[path]['actual_source_solve_dispatches'] if path in positive else 0
            require(count == expected, 'ACTUAL_SOURCE_COUNT_DIFFERS_FROM_FIXED_V22')
            if path in positive:
                require(row['execution_sha256'] == positive[path]['execution']['sha256'],
                        'V22_POSITIVE_DISPATCH_EXECUTION_CHANGED')
        enumerated.append(dict(run_id=row['run_id'], execution=path,
            execution_sha256=row['execution_sha256'], status=actual['status'],
            saved_dispatch_fields=fields, actual_source_solve_dispatches=count,
            count_basis=basis, new_since_previous_snapshot=path not in prior_paths))
    previous = sum(r['actual_source_solve_dispatches'] for r in enumerated if not r['new_since_previous_snapshot'])
    added = sum(r['actual_source_solve_dispatches'] for r in enumerated if r['new_since_previous_snapshot'])
    if 'authoritative_source_solve_accounting' in old:
        require(previous == old['authoritative_source_solve_accounting']['total_actual_source_solve_dispatches'],
                'PRIOR_AUTHORITATIVE_SOURCE_COUNT_CHANGED')
    if version == 23:
        require(len(old['executions']) == 40 and len(rows) == 41 and previous == 5 and added == 0
                and {r['run_id'] for r in enumerated if r['new_since_previous_snapshot']}
                    == {'20261016_R2_ABB_CBIRRT_NR_PATH01'},
                'V23_PATH01_MUST_ADD_ONE_EXECUTION_AND_ZERO_SOURCE_SOLVES')
    return dict(schema='P4_ACTUAL_SOURCE_SOLVE_ACCOUNTING_V1',
        baseline_addendum=str(addp.relative_to(R)), baseline_addendum_sha256=sha(addp),
        baseline_ledger=str(baselinep.relative_to(R)), baseline_ledger_sha256=sha(baselinep),
        previous_snapshot=str(op.relative_to(R)), previous_snapshot_sha256=sha(op),
        previous_actual_source_solve_dispatches=previous, new_actual_source_solve_dispatches=added,
        total_actual_source_solve_dispatches=previous + added, executions_enumerated=len(enumerated),
        actual_source_solve_dispatches_by_execution=enumerated,
        counting_rule='Count actual saved source dispatches including failed calls once; no success, path, POST, stdout-line or cost-row substitution. Attempted dispatch fields are retained separately.',
        ledger_generation_new_source_solve_dispatches=0), inputs


D080_SCOPE = R/'configs/p4_d080/execution_scope_v1.json'

a = argparse.ArgumentParser(description=__doc__)
for name in ('execution', 'old-csv', 'stem', 'scope', 'status', 'external-post', 'external-log'):
    a.add_argument('--' + name, required=True)
a.add_argument('--external-post-sha256', required=True)
a.add_argument('--entry-kind', required=True, choices=('engineering', 'science'))
a.add_argument('--related-item-ids', nargs='+', default=[
    'P4-T05', 'P4-T08', 'P4-T09', 'P4-T11', 'P4-T12', 'P4-T17', 'P4-T25'])
a.add_argument('--expected-old-columns', type=int, default=174)
a.add_argument('--version', type=int, required=True)
x = a.parse_args()
require(x.version >= 30 and x.expected_old_columns >= 212, 'D080_V30_OR_LATER_AFTER_IMMUTABLE_V29_REQUIRED')
d080 = load(D080_SCOPE)
require(d080['allowed_environments'] == ['I', 'II', 'III', 'IV', 'V'], 'D080_I_V_SCOPE_REQUIRED')
require(d080['VI_future_science_authorized'] is False and d080['formal_table_I_original'] == 22500 and d080['formal_table_I_D080'] == 18000 and d080['formal_trials_per_cell'] == 500 and d080['formal_solve_timeout_s'] == 1000 and d080['formal_execution_authorized'] is False, 'D080_SCALE_AND_AUTHORIZATION_REQUIRED')
op = R / f'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V{x.version-1}.json'
old = load(op)
old_hashes = {str(op): sha(op), str(R/x.old_csv): sha(R/x.old_csv), str(D080_SCOPE): sha(D080_SCOPE)}
ep = R / x.execution
e = load(ep)
postp = R / x.external_post
post = load(postp)
logp = R / x.external_log
require(sha(postp) == x.external_post_sha256, 'EXPLICIT_INDEPENDENT_POST_SHA_CHANGED')
old_hashes.update({str(ep): sha(ep), str(postp): sha(postp), str(logp): sha(logp)})

# The entry kind is explicit and must agree with its actual execution label.
# Engineering success cannot increase the scientific-execution count.
classification = e['classification']
require(isinstance(classification, str) and classification, 'ACTUAL_CLASSIFICATION_REQUIRED')
label_engineering = (classification == 'ENGINEERING_BUILD_ONLY' or
                     classification.startswith('ENGINEERING_BUILD_ONLY_'))
engineering = x.entry_kind == 'engineering'
require(engineering == label_engineering, 'ENTRY_KIND_CLASSIFICATION_MISMATCH')
if 'engineering_only' in e:
    require(type(e['engineering_only']) is bool and e['engineering_only'] == engineering,
            'EXECUTION_ENGINEERING_FIELD_MISMATCH')
for field in ('formal_planning_calls', 'formal_table_I_calls', 'new_VI_candidate_constructions'):
    require(type(e.get(field, 0)) is int and e.get(field, 0) == 0, 'NEW_FORMAL_OR_VI_CALLS ' + field)
if engineering:
    for field in ('query_calls', 'solve_calls', 'binary_execution_calls'):
        require(type(e.get(field)) is int and e[field] == 0, 'ENGINEERING_NOT_RUNTIME_ZERO ' + field)
    require(e.get('scientific_execution_authorized', False) is False,
            'ENGINEERING_CANNOT_AUTHORIZE_SCIENCE')

# Both successful bases use one real independent POST and exact saved chain.
# Prior V29 PATH01 STOP is historical only; this generic tool never inserts it
# again or changes its original charge/receipt/time bytes or declared cap breach.
RAW_BASIS = 'EXTERNAL_TIME_DECIMAL_UPPER_BOUND_REPLACES_INTERNAL_SAMPLE_ONCE'
ENVELOPE_BASIS = 'EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
require(e['run_id'] != '20261018_R2_ABB_SBL_PCS_PATH01', 'OLD_PATH01_STOP_CAN_ONLY_BE_CONSUMED_FROM_V29_HISTORY')
chargep = ep.parent.parent/(e['run_id'] + '.supervision.charge.json')
external = load(chargep); receiptp = R/external['receipt']
# Historical single-object .jsonl and true multi-line JSONL receipts both exist.
try:
    receipt = load(receiptp)
except json.JSONDecodeError:
    retained = [json.loads(line) for line in receiptp.read_text().splitlines() if line.strip()]
    require(bool(retained), 'COMPLETE_NONEMPTY_INTERNAL_RECEIPT_REQUIRED')
    receipt = retained[-1]
require(external['run_id'] == e['run_id'] and external['source_execution'] == x.execution
        and external['execution_sha256'] == receipt['execution_sha256'] == sha(ep)
        and external['receipt_sha256'] == sha(receiptp)
        and external['time_file'] == x.external_log and external['time_sha256'] == sha(logp)
        and external['timing_valid'] is True and external['time_inode_unchanged'] is True
        and external['started_attempt'] is True
        and external['time_returncode'] == external['measured_child_exit'] == 0
        and external['completed_process_exit0'] is True and receipt['status'] == e['status'],
        'SUCCESSFUL_EXTERNAL_CHAIN_AND_PERSISTENCE_RECEIPT_REQUIRED')
old_hashes.update({str(chargep): sha(chargep), str(receiptp): sha(receiptp)})
for key in ('metadata', 'stderr'):
    saved = R/external[key]
    require(sha(saved) == external[key + '_sha256'], 'ORIGINAL_SUPERVISION_LOG_SHA_CHANGED')
    old_hashes[str(saved)] = sha(saved)
require(post['personnel_independent'] is True, 'PERSONNEL_INDEPENDENT_POST_REQUIRED')
require(post['checks_failed'] == 0 and post['checks_passed'] == post['checks_total']
        and post['checks_total'] > 0, 'COMPLETE_INDEPENDENT_POST_REQUIRED')
require((post.get('external_supervision_qualified') is True) or (post.get('external_cost_qualified') is True), 'EXTERNAL_COST_CERTIFICATE_REQUIRED')
# A saved physical-path POST may qualify the exact persisted envelope while
# deliberately leaving the supervisor identity gate false; retain that distinction.
if post.get('external_supervision_qualified') is False:
    require(post.get('external_cost_qualified') is True, 'EXTERNAL_COST_ONLY_POST_MUST_DECLARE_COST')
require(post['execution_sha256'] == sha(ep) and post.get('external_time_sha256', external['time_sha256']) == sha(logp),
        'POST_EXECUTION_AND_TIME_SHA_MISMATCH')
require(sha(chargep) == post.get('external_charge_sha256', sha(chargep)),
        'POST_ORIGINAL_EXTERNAL_CHARGE_SHA_REQUIRED')
if 'internal_receipt_sha256' in post:
    require(post['internal_receipt_sha256'] == sha(receiptp), 'POST_INTERNAL_RECEIPT_SHA_MISMATCH')
fields_time = logp.read_text().split()
require(len(fields_time) == 4 and fields_time == external['time_fields'], 'EXACT_FOUR_EXTERNAL_TIME_FIELDS_REQUIRED')
elapsed, user, system = (Decimal(v) for v in fields_time[:3])
require(fields_time[3] == '0' and all(v.is_finite() and v >= 0 for v in (elapsed, user, system)),
        'SUCCESSFUL_FINITE_NONNEGATIVE_EXTERNAL_COST_REQUIRED')
raw_wall = elapsed + Decimal('.01'); raw_cpu = user + system + Decimal('.02')
basis = post.get('charge_basis', external.get('charge_basis', RAW_BASIS))
envelope = None
if basis == RAW_BASIS:
    require(external.get('charge_basis', RAW_BASIS) == RAW_BASIS,
            'RAW_POST_MUST_NOT_DOWNGRADE_DECLARED_ENVELOPE_CHARGE')
    wall = float(raw_wall); cpu = float(raw_cpu)
elif basis == ENVELOPE_BASIS:
    require(external.get('charge_basis') == ENVELOPE_BASIS
            and external['monotonic_envelope_valid'] is True
            and post.get('external_charge_sha256', sha(chargep)) == sha(chargep)
            and post.get('internal_receipt_sha256', sha(receiptp)) == sha(receiptp),
            'ORIGINAL_SUPERVISOR_AND_INDEPENDENT_POST_MUST_DECLARE_ENVELOPE_BASIS')
    observed = (external['fallback_observed_outer_wait_wall_s'], external['fallback_reaped_children_CPU_s'],
                receipt['wall_s_through_execution_persistence'], receipt['cpu_s_through_execution_persistence'])
    require(all(nonnegative(v) for v in observed), 'FINITE_OUTER_AND_RECEIPT_OBSERVATIONS_REQUIRED')
    walls = (raw_wall, Decimal(str(observed[0])) + Decimal('.01'), Decimal(str(observed[2])) + Decimal('.01'))
    cpus = (raw_cpu, Decimal(str(observed[1])) + Decimal('.02'), Decimal(str(observed[3])) + Decimal('.02'))
    wall = float(max(walls)); cpu = float(max(cpus))
    require(external['raw_GNUtime_upper_wall_s'] == float(raw_wall)
            and external['raw_GNUtime_upper_cpu_s'] == float(raw_cpu), 'ORIGINAL_RAW_GNUTIME_FIELDS_MUST_REMAIN_SEPARATE')
    envelope = dict(wall_components_decimal_s=[str(v) for v in walls], cpu_components_decimal_s=[str(v) for v in cpus],
        component_order=['raw_GNUtime_upper', 'outer_monotonic_or_reaped_upper', 'internal_receipt_upper'],
        raw_GNUtime_upper_wall_s=float(raw_wall), raw_GNUtime_upper_cpu_s=float(raw_cpu),
        rule='Exact Decimal maximum of original raw/outer/receipt observations with .01 wall/.02 CPU padding; replace one internal sample once.')
else:
    raise RuntimeError('UNKNOWN_NEW_COST_BASIS_NO_SILENT_RAW_FALLBACK')
require(all(nonnegative(v) for v in (wall, cpu, e['wall_s'], e['cpu_s'])), 'FINITE_SAMPLE_COST_REQUIRED')
require(wall == external['wall_s'] and cpu == external['cpu_s']
        and post['upper_wall_s'] <= wall and post['upper_cpu_s'] <= cpu, 'POST_AND_ORIGINAL_CHARGE_UPPER_COST_MISMATCH')
require(wall <= e['budget']['wall_s'] and cpu <= e['budget']['cpu_s'], 'SUCCESSFUL_EXECUTION_CAP_EXCEEDED_USE_SEPARATE_STOP_REVIEW')
require(wall >= e['wall_s'] and cpu >= e['cpu_s'], 'EXTERNAL_UPPER_BELOW_INTERNAL_SAMPLE')
require(all(nonnegative(receipt[k]) for k in ('wall_s_through_execution_persistence', 'cpu_s_through_execution_persistence'))
        and wall >= receipt['wall_s_through_execution_persistence'] and cpu >= receipt['cpu_s_through_execution_persistence'],
        'EXTERNAL_UPPER_MUST_COVER_SAVED_INTERNAL_PERSISTENCE_RECEIPT')
require(x.execution not in {r['execution'] for r in old['executions']}, 'EXECUTION_ALREADY_CHARGED')
require(e['run_id'] not in {r['run_id'] for r in old['executions']}, 'RUN_ALREADY_CHARGED')
require(ep.parent.name == e['run_id'], 'EXECUTION_PATH_RUN_ID_MISMATCH')

for row in old['executions']:
    require(type(row['engineering_only']) is bool, 'PRIOR_EXPLICIT_ENTRY_KIND_REQUIRED')
    require(sha(R/row['execution']) == row['execution_sha256'], 'PRIOR_EXECUTION_SHA_CHANGED')
    require(all(nonnegative(charge(row, key)) for key in ('wall_s', 'cpu_s')), 'PRIOR_COST_INVALID')
    if 'charged_wall_s' in row or 'charged_cpu_s' in row:
        require('charged_wall_s' in row and 'charged_cpu_s' in row, 'PRIOR_PARTIAL_EXTERNAL_REPLACEMENT')
        pp, tp = R/row['external_post'], R/row['external_time']
        require(sha(pp) == row['external_post_sha256'] and sha(tp) == row['external_time_sha256'],
                'PRIOR_INDEPENDENT_CERTIFICATE_SHA_CHANGED')
        old_hashes.update({str(pp): sha(pp), str(tp): sha(tp)})
require(old['count'] == len(old['executions'])
        and old['science_count'] == sum(not r['engineering_only'] for r in old['executions'])
        and old['engineering_count'] == sum(r['engineering_only'] for r in old['executions']),
        'PRIOR_ENTRY_COUNTS_MISMATCH')
require(all(math.fsum(charge(r, key) for r in old['executions']) == old['conservative_r2_sum_' + key]
            for key in ('wall_s', 'cpu_s')), 'PRIOR_CHARGED_SUM_MISMATCH')

entry = dict(run_id=e['run_id'], execution=x.execution,
    execution_sha256=sha(ep), source_commit=e['source_commit'], status=e['status'],
    classification=classification, engineering_only=engineering,
    wall_s=e['wall_s'], cpu_s=e['cpu_s'], counts=e.get('counts', {}),
    authorization_budget_id=e.get('authorization_budget_id'), formal_planning_calls=0,
    formal_table_I_calls=0, new_VI_candidate_constructions=0,
    charged_wall_s=wall, charged_cpu_s=cpu,
    charge_basis=basis, monotonic_envelope=envelope,
    external_charge=str(chargep.relative_to(R)), external_charge_sha256=sha(chargep),
    internal_receipt=str(receiptp.relative_to(R)), internal_receipt_sha256=sha(receiptp),
    external_post=x.external_post, external_post_sha256=sha(postp),
    external_time=x.external_log, external_time_sha256=sha(logp))
rows = sorted(old['executions'] + [entry], key=lambda r: r['execution'])
require(len(rows) == len({r['execution'] for r in rows}) == len({r['run_id'] for r in rows}),
        'DISTINCT_EXECUTIONS_AND_RUN_IDS_REQUIRED')
# Cross-date recovery: an Oct16 build must be included alongside Oct15 runs.
actual = {str(p.relative_to(R)): sha(p) for p in (R/'results/p4_full').glob('*_R2_*/execution.json')}
require(actual == {r['execution']: r['execution_sha256'] for r in rows}, 'ALL_ACTUAL_R2_EXECUTIONS_REQUIRED')
for p in (R/'results/p4_full').glob('*_R2_*.supervision.charge.json'):
    run = p.name.removesuffix('.supervision.charge.json')
    require((p.parent/run/'execution.json').is_file(), 'ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING ' + run)
charged = {k: math.fsum(charge(r, k) for r in rows) for k in ('wall_s', 'cpu_s')}
measured = {k: math.fsum(r[k] for r in rows if not r.get('saved_only_preflight_cost_recovery', False)) for k in ('wall_s', 'cpu_s')}
sci = [r for r in rows if not r['engineering_only']]
eng = [r for r in rows if r['engineering_only']]
require(len(sci) == old['science_count'] + int(not engineering)
        and len(eng) == old['engineering_count'] + int(engineering), 'SUCCESSOR_ENTRY_KIND_COUNTS_MISMATCH')
if x.version == 19:
    require(len(rows) == 37 and len(sci) == 29 and len(eng) == 8 and engineering,
            'V19_CBIRRT_NR_BUILD_MUST_BE_29_SCIENCE_8_ENGINEERING')

accounting, accounting_inputs = source_solve_accounting(rows, old, op, x.version)
old_hashes.update(accounting_inputs)
legacy_fields = ('new_scientific_calls', 'new_qualification_planner_solves_in_this_snapshot',
                 'previous_snapshot_qualification_planner_solves', 'total_qualification_planner_solves')
legacy_history = list(old.get('legacy_source_solve_accounting_history', [])) + [dict(
    previous_snapshot=str(op.relative_to(R)), previous_snapshot_sha256=sha(op),
    fields_retained_verbatim={key: old[key] for key in legacy_fields if key in old},
    note='Historical narrow-scope fields retained here; current actual dispatch totals use authoritative_source_solve_accounting.')]

lp = R / f'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V{x.version}.json'
l = {**old, 'schema': f'P4_R2_RECOVERY_ACTUAL_LEDGER_V{x.version}',
    'previous_snapshot': str(op.relative_to(R)), 'previous_snapshot_sha256': sha(op),
    'executions': rows, 'count': len(rows), 'science_count': len(sci), 'engineering_count': len(eng),
    'saved_only_preflight_recovery_count': sum(bool(r.get('saved_only_preflight_cost_recovery', False)) for r in rows),
    'actual_runtime_execution_records_excluding_saved_only_recovery': sum(not r.get('saved_only_preflight_cost_recovery', False) for r in rows),
    'count_meaning': 'Cost records include an explicitly labelled saved-only preflight recovery; actual runtime records exclude it.',
    'science_wall_s': math.fsum(charge(r, 'wall_s') for r in sci),
    'science_cpu_s': math.fsum(charge(r, 'cpu_s') for r in sci),
    'engineering_wall_s': math.fsum(charge(r, 'wall_s') for r in eng),
    'engineering_cpu_s': math.fsum(charge(r, 'cpu_s') for r in eng),
    'measured_internal_own_cost_sum': measured,
    'conservative_r2_sum_wall_s': charged['wall_s'],
    'conservative_r2_sum_cpu_s': charged['cpu_s'],
    'r2_remaining': {k: old['r2_caps'][k] - charged[k] for k in charged},
    'scope': x.scope, 'saved_only_analysis': True, 'new_scientific_calls': 0,
    'd080_scope_config': str(D080_SCOPE.relative_to(R)),
    'd080_scope_config_sha256': sha(D080_SCOPE),
    'd080_formal_table_I_required_calls': 18000,
    'd080_formal_table_I_calls': 0,
    'd080_VI_status': 'ARCHIVED_OUT_OF_APPROVED_SCOPE_NO_NEW_EXECUTION',
    'authoritative_source_solve_accounting': accounting,
    'legacy_source_solve_accounting_history': legacy_history,
    'new_qualification_planner_solves_in_this_snapshot': accounting['new_actual_source_solve_dispatches'],
    'previous_snapshot_qualification_planner_solves': accounting['previous_actual_source_solve_dispatches'],
    'total_qualification_planner_solves': accounting['total_actual_source_solve_dispatches'],
    'new_scientific_calls_scope': 'Zero calls by this saved-only ledger generator; not the scientific activity newly recorded in this snapshot.',
    'coverage_related_item_ids': x.related_item_ids,
    'last_actual_execution': entry,
    'double_counting_rule': 'Each execution once; charged_wall_s/cpu_s replace the internal pre-save sample for supervised runs, never add both. Old entries and historical UNKNOWN boundaries retained.',
    'resource_charge_policy': 'Use charged_wall_s/cpu_s when present, otherwise the stored own sample. External upper covers worker import, preflight, execution, receipt persistence, exit; supervisor own record tail remains outside worker cost.',
    'cost_measurement_limitations': {**old['cost_measurement_limitations'],
        'ledger_sum_meaning': 'Mixed charge ledger: all historical own samples/raw bounds/V29 STOP envelope unchanged; new successful raw or monotonic-envelope upper charges replace one internal sample once. measured_internal_own_cost_sum retains all original samples.',
        'remaining_meaning': 'Cap minus charge ledger. Historical unsupervised recording tail remains UNKNOWN, so this is still an upper bound on remaining resource, not a fully measured exact remainder.'},
}
require(l['vi_B_candidate_cap'] == 974 and l['vi_B_remaining']['candidate_constructions'] == 0
        and l['vi_B_consumed'] == old['vi_B_consumed'] and l['vi_B_remaining'] == old['vi_B_remaining'],
        'VI974_EXHAUSTED_HISTORY_REQUIRED')
require(l['formal_table_I_calls'] == 0 and l['formal_table_I_required_calls'] == 22500
        and min(l['r2_remaining'].values()) > 0, 'FORMAL_ZERO_OR_R2_REMAINING_INVALID')
require(l['r2_caps'] == old['r2_caps'] == {'wall_s': 3600, 'cpu_s': 7200}, 'ORIGINAL_R2_TOTAL_CAPS_UNCHANGED_REQUIRED')
with (R/x.old_csv).open(newline='') as f:
    rd = csv.DictReader(f); fields = rd.fieldnames; before = list(rd)
require(len(before) == 211 and len({r['item_id'] for r in before}) == 211
        and len(fields) == len(set(fields)) == x.expected_old_columns, 'FULL211_OLD_COLUMN_CONTRACT_REQUIRED')
require(len(x.related_item_ids) == len(set(x.related_item_ids))
        and set(x.related_item_ids) <= {r['item_id'] for r in before},
        'RELATED_ITEM_IDS_MUST_BE_DISTINCT_EXISTING_OBLIGATIONS')
formal = [r for r in before if r['item_id'].startswith('P4-T18-')]
expected = set(itertools.product(['II', 'III', 'IV', 'V', 'VI'], ['RRT', 'Bi-RRT', 'SBL'], ['RSS', 'PCS', 'NR']))
require({tuple(r['item_id'].removeprefix('P4-T18-').split('_')) for r in formal} == expected
        and all(r['original_repeats'] == '500' and r['original_duration_budget'] == '1000s/call' for r in formal),
        'ORIGINAL45_CELLS_22500_TRIALS_SCALE_REQUIRED')
extra = [f'v{x.version}_{k}' for k in ('status', 'scope', 'execution', 'ledger')]
require(not set(extra) & set(fields), 'SUCCESSOR_COLUMNS_ALREADY_EXIST')
updated = []
for row in before:
    related = row['item_id'] in x.related_item_ids
    v = dict(row)
    v.update(zip(extra, [x.status if related else 'NO_NEW_EVIDENCE_FOR_THIS_OBLIGATION',
        x.scope if related else '本阶段本义务无新科学结论，原完整义务保持。',
        x.execution if related else 'NOT_APPLICABLE', str(lp.relative_to(R))]))
    updated.append(v)
require([{k: r[k] for k in fields} for r in updated] == before, 'HISTORICAL_COVERAGE_VALUES_CHANGED')
cp = R/f'reports/{x.stem}.csv'; mp = cp.with_suffix('.md')
destinations = (lp, cp, mp, *(O/p.name for p in (lp, cp, mp)))
require(not any(p.exists() for p in destinations), 'OLD_SNAPSHOT_COVERAGE_OR_MIRROR_EXISTS')
require(all(sha(Path(p)) == h for p, h in old_hashes.items()), 'INPUT_BYTES_CHANGED_BEFORE_APPEND')
new(lp, l)
with cp.open('x', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields+extra); w.writeheader(); w.writerows(updated)
with cp.open(newline='') as f:
    require([{k: r[k] for k in fields} for r in csv.DictReader(f)] == before,
            'SAVED_HISTORICAL_COLUMNS_NOT_IDENTICAL')
with mp.open('x') as f:
    f.write(f'# P4 D080范围与历史原文对照：{x.stem}\n\n211行前{len(fields)}列逐值保留，新增4列。{x.scope}\n\n')
    f.write(f'{len(rows)}execution={len(sci)}科学账+{len(eng)}工程。按独立监督上界替换新运行内部样本一次，累计wall{charged["wall_s"]:.17g}/CPU{charged["cpu_s"]:.17g}；历史未测尾部仍UNKNOWN。VI974余0且后续只读归档；原文历史分母22500保留，D080批准II–V正式0/18000、36组各500/1000s。其余D080图表/投影/可见性/消融义务保持。不P2/Isaac。\n\n')
    f.write(f'实际source solve派发：前次{accounting["previous_actual_source_solve_dispatches"]}、本次新增{accounting["new_actual_source_solve_dispatches"]}、累计{accounting["total_actual_source_solve_dispatches"]}；包含失败派发，路径检查不重复计solve。原狭scope计数值存入legacy历史。\n\n')
    f.write('|ID|原完整义务|原规模|本次范围|\n|---|---|---|---|\n')
    for row in updated:
        f.write('|' + '|'.join(str(row[k]).replace('|', '\\|').replace('\n', '<br>') for k in ('item_id', 'original_requirement', 'original_repeats', extra[1])) + '|\n')
for p in (lp, cp, mp):
    mirror = O/p.name
    with mirror.open('xb') as f:
        f.write(p.read_bytes())
    require(mirror.read_bytes() == p.read_bytes(), 'OUTPUT_MIRROR_BYTES_CHANGED')
require(all(sha(Path(p)) == h for p, h in old_hashes.items()), 'INPUT_BYTES_CHANGED_AFTER_APPEND')
print(json.dumps(dict(ledger=str(lp.relative_to(R)), executions=len(rows), science_count=len(sci),
    engineering_count=len(eng), entry_kind=x.entry_kind, charged=charged,
    actual_source_solve_dispatches=accounting['total_actual_source_solve_dispatches'],
    new_source_solve_dispatches=accounting['new_actual_source_solve_dispatches'],
    measured_internal=measured, columns=len(fields)+4, related_item_ids=x.related_item_ids)))
