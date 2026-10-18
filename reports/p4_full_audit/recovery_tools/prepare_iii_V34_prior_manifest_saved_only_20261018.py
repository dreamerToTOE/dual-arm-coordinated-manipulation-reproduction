#!/usr/bin/env python3
"""Read saved V34 references only; no candidate import, execution or freeze."""
import ast
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
LEDGER=ROOT/'results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V34.json'
BASE=ROOT/'scripts/p4_d080/build_v_pcs_local_v1_draft.py'
DRAFT=ROOT/'configs/p4_d080/iii_rrt_pcs_e2e_build_v1.DRAFT.json'
OUTPUT=ROOT/'configs/p4_d080/iii_rrt_pcs_V34_prior_evidence_v1.DRAFT.json'
def path(value):
    p=Path(value);return p if p.is_absolute()else ROOT/p
def sha(value):return hashlib.sha256(path(value).read_bytes()).hexdigest()
def load(value):return json.loads(path(value).read_text())
def receipt(value):
    raw=path(value).read_text()
    try:return json.loads(raw)
    except json.JSONDecodeError:return [json.loads(line)for line in raw.splitlines()if line.strip()][-1]

ledger=load(LEDGER);draft=load(DRAFT)
assert sha(BASE)=='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578'
source=BASE.read_text();definition=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef)and x.name=='validate_prior')
function_bytes=ast.get_source_segment(source,definition).encode()
assert max((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'),key=lambda p:int(p.stem.rsplit('V',1)[1])).resolve()==LEDGER.resolve()
actual={str(p.relative_to(ROOT)):sha(p)for folder,pattern in[(ROOT/'results/p4_full','*_R2_*/execution.json'),(ROOT/'results/p4_d080','*/execution.json')]for p in folder.glob(pattern)}
assert {r['execution']:r['execution_sha256']for r in ledger['executions']}==actual
assert len(ledger['executions'])==52
evidence={str(LEDGER):sha(LEDGER)};rows=[];role_count={};unknown=[]
for row in ledger['executions']:
    entry={'run_id':row['run_id'],'execution':row['execution'],'execution_sha256':row['execution_sha256'],
        'external_charge_available_in_ledger':'charged_wall_s'in row,'roles':{}}
    ep=path(row['execution']);assert sha(ep)==row['execution_sha256'];evidence[str(ep)]=row['execution_sha256']
    entry['roles']['execution']={'path':str(ep),'sha256':row['execution_sha256']}
    if 'charged_wall_s'in row:
        post=path(row['external_post']);post_data=load(post)
        time=path(row['external_time']);charge=ep.parent.parent/(row['run_id']+'.supervision.charge.json');charge_data=load(charge)
        internal=path(charge_data['receipt']);internal_data=receipt(internal)
        assert sha(post)==row['external_post_sha256']and sha(time)==row['external_time_sha256']==post_data['external_time_sha256']
        assert sha(charge)==post_data.get('external_charge_sha256',post_data.get('receipt_sha256'))
        assert sha(internal)==charge_data['receipt_sha256']
        assert row['execution_sha256']==post_data['execution_sha256']==charge_data['execution_sha256']==internal_data['execution_sha256']
        assert path(charge_data['source_execution']).resolve()==ep.resolve()and path(charge_data['time_file']).resolve()==time.resolve()
        assert sha(time)==charge_data['time_sha256']and time.read_text().strip().split()==charge_data['time_fields']
        assert post_data['personnel_independent']is True and post_data['external_supervision_qualified']is True
        assert post_data['checks_total']==post_data['checks_passed']and post_data['checks_failed']==0
        assert row['charged_wall_s']==post_data['upper_wall_s']and row['charged_cpu_s']==post_data['upper_cpu_s']
        assert charge_data['timing_valid']is True and charge_data['time_inode_unchanged']is True
        roles={'external_POST':post,'external_charge':charge,'internal_receipt':internal,'external_time':time,
            'external_metadata':path(charge_data['metadata']),'external_stderr':path(charge_data['stderr'])}
        for key in ['metadata','stderr']:assert sha(path(charge_data[key]))==charge_data[key+'_sha256']
        if 'internal_receipt'in post_data:
            assert path(post_data['internal_receipt']).resolve()==internal.resolve()and post_data['internal_receipt_sha256']==sha(internal)
        for role,filename in roles.items():
            digest=sha(filename);evidence[str(filename.resolve())]=digest;entry['roles'][role]={'path':str(filename.resolve()),'sha256':digest}
        entry['charge_basis_retained']=row['charge_basis']
    else:
        entry['missing_external_charge_status']='HISTORICAL_UNMEASURED_TAIL_RETAINED_UNKNOWN_NO_FABRICATED_ARTIFACT'
        unknown.append(row['run_id'])
    for role in entry['roles']:role_count[role]=role_count.get(role,0)+1
    rows.append(entry)
for folder in [ROOT/'results/p4_full',ROOT/'results/p4_d080']:
    for charge in folder.glob('*.supervision.charge.json'):
        assert (charge.parent/charge.name.removesuffix('.supervision.charge.json')/'execution.json').is_file()
wall=math.fsum(r.get('charged_wall_s',r['wall_s'])for r in ledger['executions'])
cpu=math.fsum(r.get('charged_cpu_s',r['cpu_s'])for r in ledger['executions'])
assert wall==ledger['conservative_r2_sum_wall_s']==1113.4602605769917
assert cpu==ledger['conservative_r2_sum_cpu_s']==927.6919419999999
assert wall+45<=3600 and cpu+90<=7200
assert len(evidence)==179 and len(unknown)==31 and role_count=={'execution':52,'external_POST':21,'external_charge':21,'internal_receipt':21,'external_time':21,'external_metadata':21,'external_stderr':21}
assert all(draft['prior'][k]is None for k in ['ledger','ledger_sha256','wall_s','cpu_s'])
merged=dict(draft['bound_files_sha256'])
for n,digest in evidence.items():
    assert n not in merged or merged[n]==digest;merged[n]=digest
result={'schema':'P4_D080_III_RRT_PCS_V34_PRIOR_EVIDENCE_DRAFT_V1',
 'status':'SAVED_BYTE_MANIFEST_ONLY_NOT_FROZEN_NOT_A_NEW_PRIOR_REVIEW_OR_BUDGET',
 'frozen':False,'personnel_independent':False,'new_scientific_calls':0,'new_compile_calls':0,
 'retained_base_builder':str(BASE.relative_to(ROOT)),'retained_base_builder_sha256':sha(BASE),
 'retained_validate_prior_function_sha256':hashlib.sha256(function_bytes).hexdigest(),
 'manifest_generation':'Stdlib read saved references and SHA only; no candidate import, binary/model/describe query, freeze or ledger write.',
 'prior_fragment_for_root_only':{'ledger':str(LEDGER.relative_to(ROOT)),'ledger_sha256':sha(LEDGER),'wall_s':wall,'cpu_s':cpu,'historical_unmeasured_tail':'RETAINED_UNKNOWN'},
 'evidence_sha256':evidence,'evidence_count':len(evidence),'execution_count':52,
 'charged_executions':21,'historical_unmeasured_executions':31,'roles_count':role_count,'execution_artifacts':rows,
 'historical_unknown_run_ids':unknown,'latest_physical_execution':rows[-1],
 'source_draft_sha256':sha(DRAFT),'existing_pre_prior_bound_count':len(draft['bound_files_sha256']),
 'merged_existing_plus_exact_prior_evidence_count':len(merged),
 'root_freeze_instructions':['Preserve DRAFT bytes; merge evidence_sha256 into frozen bound_files_sha256; add this manifest and final independent review certificate own SHA separately.',
    'Copy prior_fragment_for_root_only into new frozen prior; recheck latest ledger immediately before launch. Do not reuse this fragment if newer actual execution/ledger appears.',
    'Keep all original scientific/control/geometry/collision criteria and 45wall/90CPU group 40wall/80CPU working caps; science/formal flags remain false.',
    'Historical UNKNOWN tails remain UNKNOWN. This inventory does not requalify 52 old executions, change historical verdicts, charge costs again or approve execution.']}
with OUTPUT.open('x')as stream:stream.write(json.dumps(result,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'manifest':str(OUTPUT.relative_to(ROOT)),'sha256':sha(OUTPUT),'execution_count':52,'evidence_count':179,
 'merged_pre_prior_plus_prior_count':len(merged),'wall_s':wall,'cpu_s':cpu},indent=2))
