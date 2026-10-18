#!/usr/bin/env python3
"""Saved-only V37: charge one rejected engineering preflight; no execution."""
from pathlib import Path
import copy
import csv
import hashlib
import json
import math
import os

R = Path(__file__).resolve().parents[3]
RUN = '20261018_R2_D080_V_RRT_PCS_BUILD01'
EP = f'results/p4_full/{RUN}/execution.json'
POST = 'reports/P4_D080_ENV_V_RRT_PCS_BUILD01_RECOVERY_COST_INDEPENDENT_POST_20261018.json'
BASIS = 'EXTERNAL_PREFLIGHT_TWO_OBSERVATION_ENVELOPE_ONCE'
OLD = 'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V36.json'
CSV = 'reports/P4_D080_III_RRT_PCS_SOURCE01_ORIGINAL_VS_APPROVED_VS_ACTUAL_20261018.csv'
STEM = 'P4_D080_V_PREFLIGHT_RECOVERY_ORIGINAL_VS_APPROVED_VS_ACTUAL_20261018'

def sha(p):
    return hashlib.sha256((R/p).read_bytes()).hexdigest()

def load(p):
    return json.loads((R/p).read_text())

def new(p, obj):
    with (R/p).open('x') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())

old = load(OLD); e = load(EP); post = load(POST)
assert sha(OLD) == 'da2c5bfec0f44eca9d9444752d09fe46615bdad475e1bf9d1dd4f7b621cab351'
assert sha(EP) == '6e6b3d9f44a51a2ee2d3dd0f35efce10dc6d2d1090c74d5a13552cc93cd900df'
assert e['schema'] == 'SAVED_ONLY_PREFLIGHT_RECOVERY'
assert e['source_execution_created_during_attempt'] is False
assert e['compile_calls'] == e['solve_calls'] == e['binary_execution_calls'] == 0
assert post['personnel_independent'] is True and post['checks_failed'] == 0
assert post['checks_total'] == post['checks_passed'] > 0
assert post['saved_only_recovery'] is True and post['external_cost_qualified'] is True
assert post['external_supervision_qualified'] is False
assert post['execution_sha256'] == sha(EP)
assert post['upper_wall_s'] == e['wall_s'] == 0.098610285998584
assert post['upper_cpu_s'] == e['cpu_s'] == 0.092844
assert post['external_charge_sha256'] == sha(e['original_charge']) == e['original_charge_sha256']
assert len(old['executions']) == 54 and old['science_count'] == 39 and old['engineering_count'] == 15
old_hashes = {OLD: sha(OLD), CSV: sha(CSV), EP: sha(EP), POST: sha(POST)}
for row in old['executions']:
    assert sha(row['execution']) == row['execution_sha256']
    old_hashes[row['execution']] = row['execution_sha256']
entry = dict(run_id=RUN, execution=EP, execution_sha256=sha(EP), source_commit=e['source_commit'],
    status=e['status'], classification=e['classification'], engineering_only=True,
    saved_only_preflight_cost_recovery=True, source_execution_created_during_attempt=False,
    wall_s=e['wall_s'], cpu_s=e['cpu_s'], counts={'compile':0, 'solve':0, 'model':0},
    formal_planning_calls=0, formal_table_I_calls=0, new_VI_candidate_constructions=0,
    charged_wall_s=e['wall_s'], charged_cpu_s=e['cpu_s'], charge_basis=BASIS,
    external_charge=e['original_charge'], external_charge_sha256=sha(e['original_charge']),
    external_post=POST, external_post_sha256=sha(POST),
    external_time=f'results/p4_full/{RUN}.supervision.time.txt',
    external_time_sha256=post['external_time_sha256'], internal_receipt=None,
    internal_receipt_sha256=None, original_runtime_execution_sha256=None)
rows = sorted([*old['executions'], entry], key=lambda r:r['execution'])
assert len({r['run_id'] for r in rows}) == len(rows) == 55
actual = {str(p.relative_to(R)):sha(str(p.relative_to(R))) for p in (R/'results/p4_full').glob('*_R2_*/execution.json')}
assert actual == {r['execution']:r['execution_sha256'] for r in rows}
charge = lambda r,k:r.get('charged_'+k, r[k])
totals = {k:math.fsum(charge(r,k) for r in rows) for k in ('wall_s','cpu_s')}
assert totals['wall_s'] < 3600 and totals['cpu_s'] < 7200
ledger = copy.deepcopy(old)
ledger.update(schema='P4_R2_RECOVERY_ACTUAL_LEDGER_V37', previous_snapshot=OLD,
    previous_snapshot_sha256=sha(OLD), count=55, science_count=39, engineering_count=16,
    executions=rows, scope='One rejected uncommitted V engineering preflight, separately recovered cost only; no new compile/model/solve.',
    last_actual_execution=entry, new_qualification_planner_solves_in_this_snapshot=0,
    previous_snapshot_qualification_planner_solves=7, total_qualification_planner_solves=7,
    conservative_r2_sum_wall_s=totals['wall_s'], conservative_r2_sum_cpu_s=totals['cpu_s'],
    r2_remaining={k:old['r2_caps'][k]-v for k,v in totals.items()},
    saved_only_preflight_recovery_count=1, actual_runtime_execution_records_excluding_saved_only_recovery=54,
    count_meaning='55 cost records = 54 actual runtime execution records + 1 explicitly post-attempt preflight recovery cost index; not 55 experimental runs.',
    last_new_cost_entry_kind='SAVED_ONLY_PREFLIGHT_RECOVERY_NOT_BUILD',
    recovered_preflight_independent_POST=POST, recovered_preflight_independent_POST_sha256=sha(POST))
for k in ('wall_s','cpu_s'):
    ledger['engineering_'+k] = math.fsum(charge(r,k) for r in rows if r['engineering_only'])
# A recovery has no internal runtime sample. Keep the old measured sum exact.
assert ledger['measured_internal_own_cost_sum'] == old['measured_internal_own_cost_sum']
a = ledger['authoritative_source_solve_accounting']
a.update(previous_snapshot=OLD, previous_snapshot_sha256=sha(OLD),
    previous_actual_source_solve_dispatches=7, new_actual_source_solve_dispatches=0,
    total_actual_source_solve_dispatches=7, executions_enumerated=55)
a['actual_source_solve_dispatches_by_execution'] = [dict(r,new_since_previous_snapshot=False) for r in a['actual_source_solve_dispatches_by_execution']]
a['actual_source_solve_dispatches_by_execution'].append(dict(run_id=RUN,execution=EP,execution_sha256=sha(EP),
    status=e['status'],saved_dispatch_fields={'solve_calls':0},actual_source_solve_dispatches=0,
    count_basis='EXPLICIT_POST_ATTEMPT_PREFLIGHT_RECOVERY_ZERO_SCIENCE',new_since_previous_snapshot=True))
lp='results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V37.json'
new(lp,ledger)
with (R/CSV).open(newline='') as f:
    reader=csv.DictReader(f); fields=reader.fieldnames; table=list(reader)
assert len(table)==211 and len(fields)==240
extra=['v37_status','v37_scope','v37_execution','v37_ledger']
with (R/f'reports/{STEM}.csv').open('x',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields+extra);w.writeheader()
    for r in table:
        w.writerow({**r,extra[0]:'NO_NEW_SCIENCE_PREFLIGHT_COST_ONLY',extra[1]:ledger['scope'],extra[2]:EP,extra[3]:lp})
with (R/f'reports/{STEM}.md').open('x') as f:
    f.write('# D080 V37：原论文 / 批准范围 / 实际证据\n\n211行历史前240列全部保留，新增4列仅记一次工程前置拒绝及费用，不增加科学完成率。III649完整路径资格待执行，II五条路径直接复用。\n\n')
    f.write(f'55费用记录=54实际runtime记录+1明确事后费用恢复索引；39科学账、16工程费用账。新编译/模型/solve均0，累计source solve7。累计wall={totals["wall_s"]!r}s、CPU={totals["cpu_s"]!r}s，历史未测尾UNKNOWN。原BUILD01仍未构建，原exit1/null receipt/三观测不完整均保留。正式0/18000，VI只读。\n')
assert all(sha(n)==v for n,v in old_hashes.items())
print(json.dumps(dict(ledger=lp,cost_records=55,actual_runtime_records=54,charged=totals,new_solve_calls=0,columns=244)))
