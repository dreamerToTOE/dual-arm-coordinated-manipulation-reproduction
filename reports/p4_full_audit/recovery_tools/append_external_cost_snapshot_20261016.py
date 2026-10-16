"""Saved-only successor ledger: retain samples, charge supervised cost once.

PRE: reuse append_actual_snapshot and the existing 211-row coverage contract.
No scientific calls. Old execution/ledger/coverage bytes remain unchanged.
The independent POST must certify the exclusive external time record first.
"""
from pathlib import Path
from decimal import Decimal
import argparse
import csv
import hashlib
import json
import math

R = Path(__file__).resolve().parents[3]
O = Path('/home/ubuntu2004/Documents/Codex/2026-10-15/codex-p4-https-github-com-dreamertotoe/outputs')
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def new(p, value):
    with p.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')

a = argparse.ArgumentParser()
for name in ('execution', 'old-csv', 'stem', 'scope', 'status', 'external-post', 'external-log'):
    a.add_argument('--' + name, required=True)
a.add_argument('--version', type=int, required=True)
x = a.parse_args()
op = R / f'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V{x.version-1}.json'
old = load(op)
ep = R / x.execution
e = load(ep)
postp = R / x.external_post
post = load(postp)
logp = R / x.external_log
# A frozen independent POST is consumed as evidence, never generated here.
assert post['personnel_independent'] is True
assert post['checks_failed'] == 0 and post['checks_passed'] == post['checks_total']
assert post['external_supervision_qualified'] is True
assert post['execution_sha256'] == sha(ep)
assert post['external_time_sha256'] == sha(logp)
elapsed, user, system, exit_status = logp.read_text().split()
assert exit_status == '0'
wall = float(Decimal(elapsed) + Decimal('.01'))
cpu = float(Decimal(user) + Decimal(system) + Decimal('.02'))
assert wall == post['upper_wall_s'] and cpu == post['upper_cpu_s']
assert wall <= e['budget']['wall_s'] and cpu <= e['budget']['cpu_s']
assert wall >= e['wall_s'] and cpu >= e['cpu_s']
assert x.execution not in {r['execution'] for r in old['executions']}
for row in old['executions']:
    assert sha(R / row['execution']) == row['execution_sha256']
entry = dict(run_id=e['run_id'], execution=x.execution,
    execution_sha256=sha(ep), source_commit=e['source_commit'], status=e['status'],
    classification=e['classification'], engineering_only=False,
    wall_s=e['wall_s'], cpu_s=e['cpu_s'], counts=e.get('counts', {}),
    authorization_budget_id=None, formal_planning_calls=0,
    charged_wall_s=wall, charged_cpu_s=cpu,
    charge_basis='EXTERNAL_TIME_DECIMAL_UPPER_BOUND_REPLACES_INTERNAL_SAMPLE_ONCE',
    external_post=x.external_post, external_post_sha256=sha(postp),
    external_time=x.external_log, external_time_sha256=sha(logp))
rows = sorted(old['executions'] + [entry], key=lambda r: r['execution'])
actual = {str(p.relative_to(R)) for p in (R/'results/p4_full').glob('20261015_R2_*/execution.json')}
assert actual == {r['execution'] for r in rows}
def charge(row, key): return row.get('charged_' + key, row[key])
charged = {k: math.fsum(charge(r, k) for r in rows) for k in ('wall_s', 'cpu_s')}
measured = {k: math.fsum(r[k] for r in rows) for k in ('wall_s', 'cpu_s')}
sci = [r for r in rows if not r['engineering_only']]
eng = [r for r in rows if r['engineering_only']]
lp = R / f'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V{x.version}.json'
l = {**old, 'schema': f'P4_R2_RECOVERY_ACTUAL_LEDGER_V{x.version}',
    'previous_snapshot': str(op.relative_to(R)), 'previous_snapshot_sha256': sha(op),
    'executions': rows, 'count': len(rows), 'science_count': len(sci), 'engineering_count': len(eng),
    'science_wall_s': math.fsum(charge(r, 'wall_s') for r in sci),
    'science_cpu_s': math.fsum(charge(r, 'cpu_s') for r in sci),
    'engineering_wall_s': math.fsum(charge(r, 'wall_s') for r in eng),
    'engineering_cpu_s': math.fsum(charge(r, 'cpu_s') for r in eng),
    'measured_internal_own_cost_sum': measured,
    'conservative_r2_sum_wall_s': charged['wall_s'],
    'conservative_r2_sum_cpu_s': charged['cpu_s'],
    'r2_remaining': {k: old['r2_caps'][k] - charged[k] for k in charged},
    'scope': x.scope, 'saved_only_analysis': True, 'new_scientific_calls': 0,
    'last_actual_execution': entry,
    'double_counting_rule': 'Each execution once; charged_wall_s/cpu_s replace the internal pre-save sample for supervised runs, never add both. Old entries and historical UNKNOWN boundaries retained.',
    'resource_charge_policy': 'Use charged_wall_s/cpu_s when present, otherwise the stored own sample. External upper covers worker import, preflight, execution, receipt persistence, exit; supervisor own record tail remains outside worker cost.',
    'cost_measurement_limitations': {**old['cost_measurement_limitations'],
        'ledger_sum_meaning': 'Mixed charge ledger: old stored own samples plus external decimal upper bounds for supervised runs. Each execution charged once. measured_internal_own_cost_sum separately preserves all original samples.',
        'remaining_meaning': 'Cap minus charge ledger. Historical unsupervised recording tail remains UNKNOWN, so this is still an upper bound on remaining resource, not a fully measured exact remainder.'},
}
assert l['vi_B_remaining']['candidate_constructions'] == 0
assert l['formal_table_I_calls'] == 0 and min(l['r2_remaining'].values()) > 0
with (R/x.old_csv).open(newline='') as f:
    rd = csv.DictReader(f); fields = rd.fieldnames; before = list(rd)
assert len(before) == 211 and len({r['item_id'] for r in before}) == 211
extra = [f'v{x.version}_{k}' for k in ('status', 'scope', 'execution', 'ledger')]
assert not set(extra) & set(fields)
updated = []
for row in before:
    related = row['item_id'] in {'P4-T05','P4-T08','P4-T09','P4-T11','P4-T12','P4-T17','P4-T25'}
    v = dict(row)
    v.update(zip(extra, [x.status if related else 'NO_NEW_EVIDENCE_FOR_THIS_OBLIGATION',
        x.scope if related else '本阶段本义务无新科学结论，原完整义务保持。',
        x.execution if related else 'NOT_APPLICABLE', str(lp.relative_to(R))]))
    updated.append(v)
cp = R/f'reports/{x.stem}.csv'; mp = cp.with_suffix('.md')
assert not any(p.exists() for p in (lp, cp, mp))
new(lp, l)
with cp.open('x', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields+extra); w.writeheader(); w.writerows(updated)
with cp.open(newline='') as f:
    assert [{k: r[k] for k in fields} for r in csv.DictReader(f)] == before
with mp.open('x') as f:
    f.write(f'# P4全文范围：{x.stem}\n\n211行前{len(fields)}列逐值保留，新增4列。{x.scope}\n\n')
    f.write(f'{len(rows)}execution={len(sci)}科学账+{len(eng)}工程。按独立监督上界替换新运行内部样本一次，累计wall{charged["wall_s"]:.17g}/CPU{charged["cpu_s"]:.17g}；历史未测尾部仍UNKNOWN。VI974余0、正式0/22500，全部原文实验规模保持。不P2/Isaac。\n\n')
    f.write('|ID|原完整义务|原规模|本次范围|\n|---|---|---|---|\n')
    for row in updated:
        f.write('|' + '|'.join(str(row[k]).replace('|','\\|').replace('\n','<br>') for k in ('item_id','original_requirement','original_repeats',extra[1])) + '|\n')
for p in (lp, cp, mp):
    with (O/p.name).open('xb') as f: f.write(p.read_bytes())
print(json.dumps(dict(ledger=str(lp.relative_to(R)), executions=len(rows), charged=charged,
    measured_internal=measured, columns=len(fields)+4)))
