#!/usr/bin/env python3
"""Versioned prior validator retaining v1 rules plus one explicit cost-only POST exception.

The v1 helper remains byte-for-byte preserved for all historical protocols.  This
successor admits the already executed III physical run only when its corrected
cost-only certificate binds the execution, GNUtime file, charge, receipt and POST
hashes exactly.  It never upgrades external supervision to qualified supervision.
"""
from pathlib import Path
import hashlib, json, math
from decimal import Decimal

# Keep the reviewed v1 implementation as the ordinary predicate source.
import validate_prior_preflight_recovery_v1 as V1

ROOT=V1.ROOT
RECOVERED_BASIS=V1.RECOVERED_BASIS
COST_ONLY_RUN='20261018_R2_D080_III_RRT_PCS_PHYSICAL01'
COST_ONLY_POST='reports/P4_D080_ENV_III_RRT_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_COST_ONLY_V2_CORRECTED_20261018.json'
COST_ONLY_EXECUTION='results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01/execution.json'
COST_ONLY_TIME='results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01.supervision.time.txt'
COST_ONLY_CHARGE='results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01.supervision.charge.json'
COST_ONLY_RECEIPT='results/p4_full/20261018_R2_D080_III_RRT_PCS_PHYSICAL01/cost_receipt.jsonl'
COST_ONLY_EXECUTION_SHA='2ac3e464d54afa59ad7ae3d01dd900cf3cca645132ba4c73e9a35b95ac506737'
COST_ONLY_TIME_SHA='7046ba75582a4a0e34347b04627fb7ca30c01c145aa17f646ad49b9fca643802'
COST_ONLY_CHARGE_SHA='37141bb8b583eca540e83054cb8f9c6fbca5ca01bbc260c5cae9c63d77feab81'
COST_ONLY_RECEIPT_SHA='3b99bd30a8f57d65e76ec04f8a7d6f0ffb020ec2277afc79f9bd4fd52b6e40ae'

def require(ok,reason):
    if not ok: raise RuntimeError(reason)
def path(value): return V1.path(value)
def sha(value): return V1.sha(value)
def load(value): return V1.load(value)
def certificate_json(value): return V1.certificate_json(value)

def validate_prior(spec,run_name,run_dir):
    """Same v1 validation, with a single explicit III cost-only branch."""
    RUN=Path(run_dir).resolve()
    ledger_path=path(spec['prior']['ledger']).resolve()
    ledgers=list((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
    require(ledgers and ledger_path==max(ledgers,key=lambda p:int(p.stem.rsplit('V',1)[1])).resolve(),'LATEST_VERSIONED_CHARGED_LEDGER_REQUIRED')
    require(sha(ledger_path)==spec['prior']['ledger_sha256'],'PRIOR_LEDGER_CHANGED')
    ledger=load(ledger_path)
    actual={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'results/p4_full').glob('*_R2_*/execution.json') if p.parent!=RUN}
    actual.update({str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'results/p4_d080').glob('*/execution.json') if p.parent!=RUN})
    require({r['execution']:r['execution_sha256'] for r in ledger['executions']}==actual,'PRIOR_LEDGER_MUST_COVER_EVERY_ACTUAL_EXECUTION')
    evidence={str(ledger_path):sha(ledger_path)}
    for row in ledger['executions']:
        evidence[str(path(row['execution']))]=row['execution_sha256']
        if 'charged_wall_s' not in row: continue
        post_path=path(row['external_post']); post=load(post_path)
        time_path=path(row['external_time']); charge_path=path(row['execution']).parent.parent/(row['run_id']+'.supervision.charge.json'); charge=load(charge_path)
        if row.get('charge_basis')==V1.RECOVERED_BASIS:
            V1.validate_recovered_preflight(row,post_path,post,time_path,charge_path,charge,evidence); continue
        exception=(row['run_id']==COST_ONLY_RUN and row['charge_basis']=='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE')
        if exception:
            require(str(post_path.relative_to(ROOT))==COST_ONLY_POST and str(path(row['execution']).relative_to(ROOT))==COST_ONLY_EXECUTION
                    and row['execution_sha256']==COST_ONLY_EXECUTION_SHA and row['external_time']==COST_ONLY_TIME
                    and row['external_time_sha256']==COST_ONLY_TIME_SHA
                    and str(charge_path.relative_to(ROOT))==COST_ONLY_CHARGE
                    and str(path(charge['receipt']).relative_to(ROOT))==COST_ONLY_RECEIPT
                    and charge['receipt_sha256']==COST_ONLY_RECEIPT_SHA,
                    'ONLY_DECLARED_III_COST_ONLY_POST_EXCEPTION')
            require(row['external_post']==COST_ONLY_POST
                    and row['external_post_sha256']==sha(post_path)
                    and row['external_post_sha256']=='7e243fe04e936b9b4ef6670f99aa1f4b95be09c082b1f91bafdeb1c0e0f02d06'
                    and sha(time_path)==COST_ONLY_TIME_SHA and sha(charge_path)==COST_ONLY_CHARGE_SHA
                    and sha(path(charge['receipt']))==COST_ONLY_RECEIPT_SHA,
                    'III_COST_ONLY_POST_DIGEST_BINDING_REQUIRED')
            require(post['personnel_independent'] is True and post['external_supervision_qualified'] is False
                    and post['external_timing_qualified'] is False and post['external_cost_qualified'] is True and post['checks_total']==post['checks_passed']
                    and post['checks_failed']==0 and post['execution_sha256']==row['execution_sha256']
                    and post['upper_wall_s']<=row['charged_wall_s'] and post['upper_cpu_s']<=row['charged_cpu_s']
                    and sha(time_path)==row['external_time_sha256']==post['external_time_sha256'],
                    'III_COST_ONLY_POST_HASH_AND_BOUNDARY_REQUIRED')
        else:
            require(sha(post_path)==row['external_post_sha256'] and post['personnel_independent'] is True
                    and post['external_supervision_qualified'] is True and post['checks_total']==post['checks_passed']
                    and post['checks_failed']==0 and post['execution_sha256']==row['execution_sha256']
                    and post['upper_wall_s']==row['charged_wall_s'] and post['upper_cpu_s']==row['charged_cpu_s']
                    and sha(time_path)==row['external_time_sha256']==post['external_time_sha256'],
                    'PRIOR_EXTERNAL_POST_EXECUTION_TIMING_CERTIFICATE_REQUIRED')
        require(sha(charge_path)==post.get('external_charge_sha256',post.get('receipt_sha256'))
                and charge['execution_sha256']==row['execution_sha256'] and path(charge['source_execution']).resolve()==path(row['execution']).resolve()
                and path(charge['time_file']).resolve()==time_path.resolve() and charge['time_sha256']==row['external_time_sha256']
                and charge['timing_valid'] is True and charge['time_inode_unchanged'] is True,'PRIOR_HASHED_EXTERNAL_CHARGE_BINDING_REQUIRED')
        receipt_path=path(charge['receipt']); receipt=certificate_json(receipt_path)
        require(sha(receipt_path)==charge['receipt_sha256'] and receipt['execution_sha256']==row['execution_sha256'],'PRIOR_INTERNAL_PERSISTENCE_RECEIPT_REQUIRED')
        fields=time_path.read_text().strip().split(); require(len(fields)==4 and fields==charge['time_fields'],'PRIOR_EXACT_FOUR_GNUTIME_FIELDS_REQUIRED')
        elapsed,user,system=(Decimal(v) for v in fields[:3]); exit_code=int(fields[3])
        require(all(v.is_finite() and v>=0 for v in (elapsed,user,system)) and exit_code==charge['measured_child_exit']==charge['time_returncode'],'PRIOR_FINITE_TIME_AND_EXACT_SAVED_EXIT_REQUIRED')
        basis=row['charge_basis']; raw_wall=float(elapsed+Decimal('.01')); raw_cpu=float(user+system+Decimal('.02'))
        if basis=='EXTERNAL_TIME_DECIMAL_UPPER_BOUND_REPLACES_INTERNAL_SAMPLE_ONCE':
            require(raw_wall==row['charged_wall_s']==charge['wall_s'] and raw_cpu==row['charged_cpu_s']==charge['cpu_s'],'PRIOR_DECIMAL_UPPER_REPLACEMENT_ONCE_REQUIRED')
        elif basis=='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE':
            if charge.get('charge_basis')!=basis:
                require(row['run_id']=='20261018_R2_ABB_SBL_PCS_PATH01' and row['execution_sha256']=='cee39aae1538742e1ab54e19d28ff42a8de2c4165cf2511bb1477d69847bc1e0' and sha(charge_path)=='110293de768c992b99cd75da371de7c68a189271fcfc4687da785ea4fff16a27' and raw_wall==charge['wall_s'] and raw_cpu==charge['cpu_s'],'ONLY_IMMUTABLE_PATH01_OLD_RAW_CHARGE_EXCEPTION_ALLOWED')
            observations=(charge['fallback_observed_outer_wait_wall_s'],charge['fallback_reaped_children_CPU_s'],receipt['wall_s_through_execution_persistence'],receipt['cpu_s_through_execution_persistence'])
            require(all(type(v) in (int,float) and math.isfinite(v) and v>=0 for v in observations),'FINITE_SAVED_OUTER_AND_RECEIPT_ENVELOPE_REQUIRED')
            expected_wall=float(max(elapsed+Decimal('.01'),Decimal(str(observations[0]))+Decimal('.01'),Decimal(str(observations[2]))+Decimal('.01')))
            expected_cpu=float(max(user+system+Decimal('.02'),Decimal(str(observations[1]))+Decimal('.02'),Decimal(str(observations[3]))+Decimal('.02')))
            require(post['charge_basis']==basis and post['external_charge_sha256']==sha(charge_path) and post['internal_receipt_sha256']==sha(receipt_path)
                    and row['charged_wall_s']==expected_wall and row['charged_cpu_s']==expected_cpu
                    and (post['upper_wall_s']<=expected_wall and post['upper_cpu_s']<=expected_cpu if exception else post['upper_wall_s']==expected_wall and post['upper_cpu_s']==expected_cpu),
                    'PRIOR_INDEPENDENT_EXACT_MONOTONIC_ENVELOPE_CERTIFICATE_REQUIRED')
            execution=load(path(row['execution'])); breach={'wall':expected_wall>execution['budget']['wall_s'],'cpu':expected_cpu>execution['budget']['cpu_s']}
            if any(breach.values()): require(row['execution_cap_breach']==breach and post['execution_cap_breach_retained'] is True,'REAL_PRIOR_CAP_BREACH_MUST_REMAIN_RECORDED_NOT_REJECTED')
            if charge.get('charge_basis')==basis:
                require(charge['wall_s']==expected_wall and charge['cpu_s']==expected_cpu and charge['raw_GNUtime_upper_wall_s']==raw_wall and charge['raw_GNUtime_upper_cpu_s']==raw_cpu,'NEW_ENVELOPE_CHARGE_MUST_SEPARATELY_RETAIN_RAW_TIME')
        else: raise RuntimeError('UNKNOWN_PRIOR_CHARGE_BASIS_NO_SILENT_FALLBACK')
        for filename in (post_path,charge_path,receipt_path,time_path): evidence[str(filename.resolve())]=sha(filename)
        for key in ('metadata','stderr'):
            filename=path(charge[key]); require(sha(filename)==charge[key+'_sha256'],'PRIOR_SUPERVISION_LOG_CHANGED'); evidence[str(filename.resolve())]=sha(filename)
        if 'internal_receipt' in post: require(path(post['internal_receipt']).resolve()==receipt_path.resolve() and post['internal_receipt_sha256']==sha(receipt_path),'PRIOR_POST_INTERNAL_RECEIPT_CHANGED')
    for folder in (ROOT/'results/p4_full',ROOT/'results/p4_d080'):
        for charge in folder.glob('*.supervision.charge.json'):
            name=charge.name.removesuffix('.supervision.charge.json')
            if name==run_name: continue
            require((charge.parent/name/'execution.json').is_file(),'UNACCOUNTED_SUPERVISED_ATTEMPT_'+name)
    wall=math.fsum(row.get('charged_wall_s',row['wall_s']) for row in ledger['executions']); used=math.fsum(row.get('charged_cpu_s',row['cpu_s']) for row in ledger['executions'])
    require(all(math.isfinite(v) and v>=0 for v in (wall,used)) and wall==ledger['conservative_r2_sum_wall_s'] and used==ledger['conservative_r2_sum_cpu_s'],'EXACT_CURRENT_CHARGED_SUMS_REQUIRED')
    require(wall+spec['budget']['wall_s']<=3600 and used+spec['budget']['cpu_s']<=7200,'NO_R2_TOTAL_BUDGET_INCREASE')
    require(wall==spec['prior']['wall_s'] and used==spec['prior']['cpu_s'],'EXACT_FROZEN_CHARGED_PRIOR_REQUIRED')
    return {'path':str(ledger_path.relative_to(ROOT)),'sha256':sha(ledger_path),'wall_s':wall,'cpu_s':used,'evidence_sha256':evidence,'historical_unmeasured_tail':'RETAINED_UNKNOWN'}
