#!/usr/bin/env python3
"""Thin personnel-independent static V adapter review; zero model imports."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import math
import sys

ROOT=Path(__file__).resolve().parents[3]
FILES={
'scripts/p4_d080/qualify_v_pcs_physical01_v1_draft.py':'b85d6e93e3811d76f8a5f02f13b0a5df8b66e0b88c0907e196fb12d950340bfa',
'scripts/p4_d080/supervise_v_pcs_physical01_v1_draft.py':'c4633f2040df3b82b570ab25db6d863ee01aeb6c4d8fc7044394af9af41d7891',
'configs/p4_d080/v_pcs_physical01_v1.DRAFT.json':'460961f6a99f297a755c7714f5e1baa4c7b9ff30b0169ef1eecc814dd28f7674',
'reports/P4_D080_ENV_V_PCS_PHYSICAL01_PRE_DRAFT_20261018.md':'26421919b022b5a5c9728dfb5569ceeeb163259fb8fe6b6d4b78480b6b6dcb08',
'reports/P4_D080_ENV_V_PCS_PHYSICAL01_FIELD_MAP_DRAFT_20261018.md':'5a22a5a7804d1ec12330e9f7c4bd39bb4caeca20a2cd524d9fb301c86699d381'}
RUNNER,SUP,CONFIG,PRE,FIELD=list(FILES)
BASE='scripts/qualify_p4_full_r2_abb_sbl_pcs_path_tail02_draft.py'
BASE_SUP='scripts/supervise_p4_full_r2_abb_sbl_pcs_path_tail02_draft.py'
BASE_POST='reports/P4_FULL_R2_ABB_SBL_PCS_PATH_TAIL02_COMBINED_SAVED_INDEPENDENT_POST_20261018.json'
BASE_POST_SHA='c28a53f87a2fd4f64a6a09e029cb072be066844284d7efbb8ac331ae25f816c8'
QUEUE_POST='reports/P4_D080_ENV_V_PCS_LOCAL01_COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_ADDENDUM_20261018.json'
QUEUE_POST_SHA='ca155059e6311e9f4cd5eb7485ac590ae795874fa32b03c8ae2b7f61f2e6c59c'
OUT=ROOT/'reports/P4_D080_ENV_V_PCS_PHYSICAL01_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
checks=[];retained={}
def raw(n):
 p=Path(n);p=p if p.is_absolute()else ROOT/p;b=p.read_bytes();h=hashlib.sha256(b).hexdigest();assert retained.setdefault(str(p),h)==h;return b
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def load(n):return json.loads(raw(n))
def ck(n,v):checks.append(dict(check=n,passed=bool(v)))
def dump(n):return ast.dump(n,include_attributes=False)
def fn(tree,name):return next(n for n in ast.walk(tree)if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name)
def block(nodes):return ast.Module(body=nodes,type_ignores=[])
class Replace(ast.NodeTransformer):
 def __init__(self,values):self.values=values
 def visit_Constant(self,n):
  for a,b in self.values:
   if type(n.value)is type(a)and n.value==a:return ast.copy_location(ast.Constant(b),n)
  return n

def audit():
 p=load(CONFIG);q=load(QUEUE_POST);basepost=load(BASE_POST);t=ast.parse(raw(RUNNER));old=ast.parse(raw(BASE));s=ast.parse(raw(SUP));olds=ast.parse(raw(BASE_SUP));text=raw(RUNNER).decode()
 ck('five author stable submittedSHA exact; AST parsed only',all(sha(n)==h for n,h in FILES.items()))
 ck('reuse actual tail02 successful engineering lifecycle without old node requery',sha(BASE_POST)==BASE_POST_SHA and basepost['personnel_independent']is basepost['independent_path_qualified']is True and basepost['checks_failed']==0 and all(sha(n)==basepost['retained_sha256'][n]for n in(BASE,BASE_SUP)))
 ck('reuse complete queue4+prior14 and source194 no repeat',sha(QUEUE_POST)==QUEUE_POST_SHA and q['checks_total']==q['checks_passed']==4 and q['checks_failed']==0 and q['reused_prior14_checks_without_rerun']['checks']==14 and q['stats']['unique_nodes']==24 and sha(p['queue'])==p['queue_sha256']==q['queue_sha256']and p['fixed_queue']==load(p['queue']))
 ck('all execution flags false in draft, physical/local/path false; exact original24 not selected replacements',p['frozen']is p['scientific_execution_authorized']is p['formal_execution_authorized']is p['independent_local_qualified']is p['independent_path_qualified']is p['continuous_collision_certificate']is False and p['reviews']==dict(independent_static_review_passed=False,root_complete_queue_freeze_approved=False,latest_actual_prior_confirmed=False)and p['execution_node_ids']==list(range(24))and p['full_queue_node_count']==24 and p['max_nodes_per_execution']==256)
 ck('exact60wall120CPU work50/100 within original3600/7200 and unchanged gates',p['budget']==dict(wall_s=60.,cpu_s=120.,work_wall_s=50.,work_cpu_s=100.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)and p['gates']==dict(position_maxabs_mm=1e-5,rotation_matrix_maxabs=1e-5,strict_leaf_full12_L2_rad=.05,branch_zero_relative_epsilon=64*sys.float_info.epsilon))
 ck('48mathFK48branch24adapter96internalFK4176PQP zero new construction/solve/RNG/VI/formal',all(p[k]==v for k,v in dict(max_math_arm_FK=48,max_branch_identity=48,max_collision_calls=24,max_adapter_internal_arm_FK_J=96,max_PQP_queries=4176).items())and p['zero_calls']==dict(IK=0,NR=0,projection=0,RBS=0,solve=0,RNG=0,VI_constructions=0,formal_table_I=0))
 ck('supervisor actual parent inode/argv and counted adapter function exact tail02 AST',dump(fn(t,'supervisor_proof'))==dump(fn(old,'supervisor_proof'))and dump(fn(t,'counted'))==dump(fn(old,'counted')))
 registered=Replace([(180,120)]).visit(copy.deepcopy(fn(old,'registered_popen')))
 ck('worker launch AST identical except lower RLIMIT180to120',dump(registered)==dump(fn(t,'registered_popen')))
 tr=next(n for n in fn(t,'execute').body if isinstance(n,ast.Try));otr=next(n for n in fn(old,'execute').body if isinstance(n,ast.Try))
 ck('first14 complete cleanup registry/group/EOF/selector/tail statements exactly tail02 AST',dump(block(tr.finalbody[:14]))==dump(block(otr.finalbody[:14])))
 ck('final cleanup gate only PASS to COMPLETED status prefix adaptation',dump(Replace([('PASS_','COMPLETED_')]).visit(copy.deepcopy(otr.finalbody[14])))==dump(tr.finalbody[14]))
 outer=next(n for n in fn(s,'main').body if isinstance(n,ast.Try));oldouter=next(n for n in fn(olds,'main').body if isinstance(n,ast.Try));normalized=Replace([(90.,60.),(180.,120.),('P4_R2_ABB_SBL_PCS_PATH_TAIL02_EXTERNAL_COST_CHARGE_V1','P4_D080_V_PCS_PHYSICAL01_EXTERNAL_COST_CHARGE_V1')]).visit(copy.deepcopy(oldouter))
 ck('entire outer supervisor launch/finalize envelope exact AST except schema loweredcaps',dump(normalized)==dump(outer))
 ck('Budget inherits old alarms and CPU/live registry only overrides caps50/100 reserve10/20',ast.unparse(fn(t,'Budget')).startswith('class Budget(old.Budget):')and 'super().__init__(spec, begun, cpu_start)'in ast.unparse(fn(t,'Budget'))and 'min(50.0, 3600.0 - spec[\'previous_r2_wall_s\'] - 10.0)'in ast.unparse(fn(t,'Budget'))and 'min(100.0, 7200.0 - spec[\'previous_r2_cpu_s\'] - 20.0)'in ast.unparse(fn(t,'Budget')))
 # Explicit new science seam reviewed from source, no project imports/evaluation.
 loop=next(n for n in tr.body if isinstance(n,ast.For)and ast.unparse(n.target)=='i');lt=ast.unparse(loop)
 ck('fixed full24 node.q12 and V independent two-arm endpoint FK closure originalQ FLIP',"q = spec['fixed_queue']['nodes'][i]['q12']"in lt and "oracle.arm_fk(q[6 * a:6 * a + 6], 'V', a + 1)"in lt and "oracle.matrix_error(poses[1], poses[0] @ oracle.grasps_for('V')[0] @ oracle.FLIP)"in lt and "oracle.limit_score(q, 'V')"in lt)
 ck('two branch identities all requested passive assignments membership originaleps',"oracle.branch_identity(q[6 * a:6 * a + 6], 'V', GATES['branch_zero_relative_epsilon'])"in lt and "current['branches'][1 - a['active_chain']]['branch_set']"in lt and "for a in spec['fixed_queue']['nodes'][i]['role_branch_assignments']"in lt and "all((a['branch_pass'] for a in assignments))"in lt)
 ck('explicitVv3 native/aligned87API0 original1e-5alignedTCP no native promotion',"adapter.check_collision('V', q, timeout_s=min(10.0, budget.remaining()), manifest_path=COLLISION)"in lt and "set(variants) == {'native', 'aligned'}"in lt and "len(codes) == 87"in lt and "type(v) is int and v == 0"in lt and "variants.get('aligned', {}).get('pose_consistency', {}).get('passed') is True"in lt)
 ck('raw collision response saved before gates normalreject continues no local/pathpromotion',lt.index("durable_new(folder / f'node_{i:05d}_collision_response.json', collision)")<lt.index("require(collisionok,")and "qualified=bool(mathok and collisionok and (collision['collision'] is False))"in lt and not any(isinstance(n,(ast.Break,ast.Continue))for n in ast.walk(loop))and "status='COMPLETED_FIXED24_DIAGNOSTIC_PENDING_INDEPENDENT_POST'"in text and "independent_local_qualified=False,independent_path_qualified=False"in text)
 ledger=load(p['prior']['ledger']);currentledger=max((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'),key=lambda x:int(x.stem.rsplit('V',1)[1]));expected={r['execution']:r['execution_sha256']for r in ledger['executions']}
 ck('latestV33 exact ledger and51 execution identity maps priorcost not recalc oldmodel',currentledger==ROOT/p['prior']['ledger']and sha(currentledger)==p['prior']['ledger_sha256']=='2c1f443bc4a43a71e4cb505b6591583242f48e2ae27c570f7a98cfc5e5710be9'and expected==p['prior_execution_sha256']and len(expected)==51 and p['actual_charge_prior']['sha256']==p['prior']['ledger_sha256']and p['previous_r2_wall_s']==p['prior']['wall_s']==p['actual_charge_prior']['wall_s']==1103.9938663219941 and p['previous_r2_cpu_s']==p['prior']['cpu_s']==p['actual_charge_prior']['cpu_s']==923.983153 and 'B.RUN_NAME=RUN'in text and "B.RUN=ROOT/'results/p4_full'/RUN"in text and 'return B.validate_prior(spec)'in text)
 bound=p['bound_files_sha256'];get=lambda n:bound.get(n,bound.get(str((ROOT/n).resolve())))
 ck('15OWN exact currentsha and all prior evidence already bound no5052unionrehash',len(p['own_source_sha256'])==15 and all(sha(n)==h==get(n)for n,h in p['own_source_sha256'].items())and all(get(n)==h for n,h in p['actual_charge_prior']['evidence_sha256'].items()))
 manifest='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v3/manifest.json';m=load(manifest);entries=[x for x in m['entries']if x['model']=='V']
 ck('explicitmanifest twoVvariant ELF/source/27mesh/PQP bindings inherited exact noquery',sha(manifest)==bound[manifest]=='c5df871adeea01d6487454dfd16fa217dde779958b5ba08b86ffff0e4f4a6388'and {x['variant']for x in entries}=={'native','aligned'}and all(get(x['binary'])==x['binary_sha256']and len(x['mesh_sha256'])==27 and get(str(Path(x['cwd'])/'validity_checkers/collisionDetection.cpp'))==x['instrumented_source_sha256']and all(get(str(Path(x['cwd'])/'simulator'/n))==h for n,h in x['mesh_sha256'].items())for x in entries))
 ext=p['external_supervision'];prefix='results/p4_full/'+p['run_id']
 ck('exclusive originaltime paths hashes exact no oldrun orclaim; absent preload stable',ext['sibling_path']==prefix+'.supervision.time.txt'and ext['metadata_path']==prefix+'.supervision.jsonl'and ext['charge_path']==prefix+'.supervision.charge.json'and ext['stderr_path']==prefix+'.supervision.stderr.log'and sha('/usr/bin/time')==ext['time_binary_sha256']and sha('/usr/bin/python3')==ext['python_binary_sha256']and not(ROOT/prefix).exists()and not(ROOT/'results/p4_full'/(p['claim_id']+'.claim.json')).exists()and p['system_preload_state']==dict(path='/etc/ld.so.preload',exists=False,sha256=None)and not Path('/etc/ld.so.preload').exists())
 ck('fullmatrix sourceTCP box source17 diagnostic deferred savedonly original gates no extraFK',all(s in raw(PRE).decode()for s in('87','1e-5','Rtcp*Ry(-3.1416/2)','ptcp+Rtcp*[435,0,300]','independent_local_qualified/independent_path_qualified=false')))
 for n,h in retained.items():assert hashlib.sha256(Path(n).read_bytes()).hexdigest()==h
 return dict(bound_entries_reused_without_full_rehash=len(bound),fixed_nodes=24,original_source_collision_unique_nodes=17,source_project_only_unique_nodes=7)

def main():
 if OUT.exists()or OUT.with_suffix('.md').exists():raise FileExistsError('EXCLUSIVE_PHYSICAL_STATIC_REVIEW')
 details={}
 try:details=audit()
 except BaseException as exc:ck('structural staticcompletion '+repr(exc),False)
 failed=[x for x in checks if not x['passed']]
 report=dict(schema='P4_D080_V_PCS_PHYSICAL01_INCREMENTAL_PERSONNEL_INDEPENDENT_PRE_V1',status='PASS_INCREMENTAL_V_PHYSICAL_FIXED24_STATIC_ONLY'if not failed else'FAIL_INCREMENTAL_STATIC_RETAINED',personnel_independent=True,reviewer='/root/sbl_independent_resume independent of physical adapter author',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,source_sha256=FILES,reused_tail02_POST=BASE_POST,reused_tail02_POST_sha256=BASE_POST_SHA,reused_queue_POST=QUEUE_POST,reused_queue_POST_sha256=QUEUE_POST_SHA,retained_sha256=retained,**details,new_model_import_compile_binary_FK_J_IK_NR_PQP_RBS_RNG_solve_VI_formal_describe_calls=0,independent_local_qualified=False,independent_path_qualified=False,allowed_freeze_transform=dict(create_new_preserve_DRAFT=True,set_only_existing_flags_true=['frozen','scientific_execution_authorized','reviews.independent_static_review_passed','reviews.root_complete_queue_freeze_approved','reviews.latest_actual_prior_confirmed'],formal_false_and_nested_savedqueue_unchanged=True,additive_metadata='Exact reference/SHA to this certificate and its bound existing source/queue certificates; all existing scientific values/bindings retained.',commit_OWN_and_protocol_before_unique_supervisor_execution=True),limits=['Static seam only; no physical math or collision result claimed.','Whole24 diagnosis can finish with rejected nodes; original3false root connections and dependency pair remain unchanged.','Only original1e-5 source87pair discrete criteria; no continuous collision/solid CAD/suction contact/global path claim.','Original R2 total3600/7200 unchanged; VI archival974/974, formal18000 unapproved.'])
 with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
 with OUT.with_suffix('.md').open('x')as f:f.write('# V PHYSICAL01 增量人员独立静审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'。\n\n只审V固定24数据/数学接缝；复用tail02父链、计数、14块完整清理和外监督AST，工作帽降50/100、总60/120。正常数学/碰撞拒绝保存并继续全部24，local/path始终false；未导入模型、未执行或入账。冻结仅五既有flags与独审SHA附加metadata，原saved队列和所有科学条件不变。\n')
 print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),failures=failed,sha256=sha(OUT))))
 if failed:raise SystemExit(2)
if __name__=='__main__':main()
