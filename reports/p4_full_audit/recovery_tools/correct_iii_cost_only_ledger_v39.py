#!/usr/bin/env python3
"""Create an immutable successor ledger that corrects only III cost-only POST binding."""
from pathlib import Path
import copy, hashlib, json, math

R = Path(__file__).resolve().parents[3]
OLD = R / 'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V38.json'
NEW = R / 'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V39.json'
OLD_POST = R / 'reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json'
NEW_POST = R / 'reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_COST_ONLY_V2_CORRECTED_20261018.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_bytes())
def require(ok, msg):
    if not ok: raise RuntimeError(msg)

old = load(OLD)
require(not NEW.exists(), 'V39_ALREADY_EXISTS')
require(sha(OLD_POST) == next(r['external_post_sha256'] for r in old['executions']
                              if r['run_id'] == '20261018_R2_D080_III_RRT_PCS_PHYSICAL01'), 'V38_POST_BINDING_MISMATCH')
corrected = load(NEW_POST)
require(corrected['personnel_independent'] is True and corrected['external_supervision_qualified'] is False
        and corrected['external_cost_qualified'] is True and corrected['checks_failed'] == 0
        and corrected['execution_sha256'] == '2ac3e464d54afa59ad7ae3d01dd900cf3cca645132ba4c73e9a35b95ac506737'
        and corrected['external_time_sha256'] == '7046ba75582a4a0e34347b04627fb7ca30c01c145aa17f646ad49b9fca643802'
        and corrected['external_charge_sha256'] == '37141bb8b583eca540e83054cb8f9c6fbca5ca01bbc260c5cae9c63d77feab81'
        and corrected['internal_receipt_sha256'] == '3b99bd30a8f57d65e76ec04f8a7d6f0ffb020ec2277afc79f9bd4fd52b6e40ae',
        'CORRECTED_COST_ONLY_POST_NOT_EXACT')

rows = copy.deepcopy(old['executions'])
target = next(r for r in rows if r['run_id'] == '20261018_R2_D080_III_RRT_PCS_PHYSICAL01')
target['external_post'] = str(NEW_POST.relative_to(R))
target['external_post_sha256'] = sha(NEW_POST)
target['cost_only_post_correction'] = {
    'previous_post': str(OLD_POST.relative_to(R)),
    'previous_post_sha256': sha(OLD_POST),
    'corrected_post': str(NEW_POST.relative_to(R)),
    'corrected_post_sha256': sha(NEW_POST),
    'reason': 'V38 retained an earlier cost-only POST missing explicit external time/charge SHA bindings; V39 changes only the ledger evidence pointer and preserves the earlier POST byte-for-byte.',
}
require(sha(R / target['execution']) == target['execution_sha256'], 'III_EXECUTION_CHANGED')
actual = {str(p.relative_to(R)): sha(p) for p in (R/'results/p4_full').glob('*_R2_*/execution.json')}
require(actual == {r['execution']: r['execution_sha256'] for r in rows}, 'ACTUAL_EXECUTION_SET_CHANGED')
wall = math.fsum(r.get('charged_wall_s', r['wall_s']) for r in rows)
cpu = math.fsum(r.get('charged_cpu_s', r['cpu_s']) for r in rows)
require(wall == old['conservative_r2_sum_wall_s'] and cpu == old['conservative_r2_sum_cpu_s'], 'COST_SUM_CHANGED')
new = copy.deepcopy(old)
new.update({
    'schema': 'P4_R2_RECOVERY_ACTUAL_LEDGER_V39',
    'previous_snapshot': str(OLD.relative_to(R)),
    'previous_snapshot_sha256': sha(OLD),
    'executions': rows,
    'last_actual_execution': target,
    'ledger_correction': {
        'kind': 'EVIDENCE_POINTER_ONLY_COST_ONLY_POST_CORRECTION',
        'old_post': str(OLD_POST.relative_to(R)),
        'old_post_sha256': sha(OLD_POST),
        'new_post': str(NEW_POST.relative_to(R)),
        'new_post_sha256': sha(NEW_POST),
        'execution_sha256_unchanged': True,
        'charged_wall_cpu_unchanged': True,
        'scientific_results_unchanged': True,
    },
})
NEW.write_bytes(json.dumps(new, ensure_ascii=False, indent=2).encode())
print(json.dumps({'ledger': str(NEW.relative_to(R)), 'sha256': sha(NEW), 'wall_s': wall, 'cpu_s': cpu,
                  'executions': len(rows), 'corrected_post_sha256': sha(NEW_POST)}))
