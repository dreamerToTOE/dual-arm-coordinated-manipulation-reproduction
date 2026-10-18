#!/usr/bin/env python3
"""Independent incremental static/saved-array SBL path review; no runner/model import."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import ast
import copy
import hashlib
import importlib.util
import json
import math
import struct
import sys

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_PATH_INDEPENDENT_STATIC_REVIEW_20261018'
RUN='20261018_R2_ABB_SBL_PCS_PATH01'
R='scripts/qualify_p4_full_r2_abb_sbl_pcs_path_draft.py'
M='scripts/materialize_p4_full_r2_abb_sbl_pcs_path_draft.py'
S='scripts/supervise_p4_full_r2_abb_sbl_pcs_path_draft.py'
P='reports/P4_FULL_R2_ABB_SBL_PCS_PATH_PRE_DRAFT_20261018.md'
OLD='scripts/qualify_p4_full_r2_abb_cbirrt_d_path_draft.py'
COMMON='scripts/materialize_p4_full_r2_abb_cbirrt_d_path_draft.py'
OLD_S='scripts/supervise_p4_full_r2_abb_cbirrt_d_path_draft.py'
ORIGINAL='scripts/qualify_p4_full_r2_abb_rrt_path.py'
SOURCE='results/p4_full/20261017_R2_ABB_SBL_PCS_SOLVE01'
POST='reports/P4_FULL_R2_ABB_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST_20261017.json'
reviewed={};checks=[];negative=[]


def read(name,want=None):
    p=Path(name);p=p if p.is_absolute() else ROOT/p
    b=p.read_bytes();h=hashlib.sha256(b).hexdigest();reviewed[str(name)]=h
    if want is not None:ck('hash bound '+str(name),h==want)
    return b


def js(name,want=None):return json.loads(read(name,want))
def ck(name,passed):checks.append(dict(check=name,passed=bool(passed)))
def fn(t,name):return next(n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
def dump(n):return ast.dump(n,include_attributes=False)
def part(src,t,name):return ast.get_source_segment(src,fn(t,name))
def packed(q):return struct.pack('>12d',*q)


runner=read(R).decode();helper=read(M).decode();supervisor=read(S).decode();pre=read(P).decode()
old=read(OLD,'b4230a660bc5d441e3256c2dc287d6a899cd2c8d0c20eeb7a8d90dd9fd57c17c').decode()
common=read(COMMON,'eb8438312a001aec63c18fb277b32e56f30c66a000e37b0526f0faf58bbb7e4e').decode()
old_s=read(OLD_S,'2ca5d89f6a128bbaec4b74011723a3849b0479aba7f50a6bf43f241d080be59a').decode()
original=read(ORIGINAL,'bdf4db7537b327872674e355dcbdcd5e31bebbb5a53ae6e21a07490a514b6865').decode()
rt,ht,st,ot,pt=[ast.parse(s) for s in (runner,helper,supervisor,old,original)]
ck('all four new files read and all three Python sources parse without runner import',True)
for name in ('Budget','supervisor_proof'):
    ck('unchanged proven '+name+' AST',dump(fn(rt,name))==dump(fn(ot,name)))
selector=lambda n:isinstance(n,ast.For) and ast.unparse(n.iter)=="enumerate(spec['fixed_queue']['nodes'])"
loops=[n for n in ast.walk(fn(rt,'execute')) if selector(n)]
pl=[n for n in ast.walk(fn(pt,'execute')) if selector(n)]
ck('one full original PCS physical loop identical AST',len(loops)==len(pl)==1 and dump(loops[0])==dump(pl[0]))
ck('physical loop also original source text identical',ast.get_source_segment(runner,loops[0])==ast.get_source_segment(original,pl[0]))
counted=[n for n in ast.walk(fn(rt,'execute')) if isinstance(n,ast.FunctionDef) and n.name=='counted']
pc=[n for n in ast.walk(fn(pt,'execute')) if isinstance(n,ast.FunctionDef) and n.name=='counted']
ck('counted FK/J wrapper original AST identical',len(counted)==len(pc)==1 and dump(counted[0])==dump(pc[0]))
normalized=part(runner,rt,'execute').replace('P4_R2_ABB_SBL_PCS_PATH_EXECUTION_V1','P4_R2_ABB_CBIRRT_D_PATH_EXECUTION_V1').replace('P4_R2_ABB_SBL_PCS_PATH_CLAIM_V1','P4_R2_ABB_CBIRRT_D_PATH_CLAIM_V1').replace('P4_R2_ABB_SBL_PCS_PATH_COST_RECEIPT_V1','P4_R2_ABB_CBIRRT_D_PATH_COST_RECEIPT_V1').replace('source.L.Journal','source.tail.Journal')
ck('whole execute transport/cleanup differs only three schema labels and proven Journal alias',normalized==part(old,ot,'execute'))
normalized=supervisor.replace(RUN,'20261015_R2_ABB_CBIRRT_D_PATH01').replace('R2_CORRECTED_SBL_PCS_RECONSTRUCTED_A01_DISCRETE_SOURCE_POLICY_PATH','R2_NUMERICS_D_FIXED_CBIRRT_RECONSTRUCTED_A01_DISCRETE_SOURCE_POLICY_PATH').replace('qualify_p4_full_r2_abb_sbl_pcs_path_draft.py','qualify_p4_full_r2_abb_cbirrt_d_path_draft.py').replace('P4_R2_ABB_SBL_PCS_PATH_EXTERNAL_COST_CHARGE_V1','P4_R2_ABB_CBIRRT_D_PATH_EXTERNAL_COST_CHARGE_V1')
ck('entire GNUtime supervisor identical except run/label/runner/schema',normalized==old_s)
ck('unchanged scientific gates explicit',"'position_maxabs_mm':1e-5,'rotation_matrix_maxabs':1e-5" in runner and "'strict_leaf_full12_L2_rad':.05,'branch_zero_relative_epsilon':64*sys.float_info.epsilon" in runner)
ck('120/240 caps within 3600/7200 cumulative',"budget=dict(wall_s=120.,cpu_s=240.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)" in runner)
ck('entire queue cap before exclusive claim and no truncation',"spec['full_queue_node_count']<=MAX_NODES" in runner and "MAX_NODES=2048" in runner and "for i,q in enumerate(spec['fixed_queue']['nodes']):" in runner)
ck('common materializer and all science/oracle sources in frozen OWN bindings',COMMON in runner and ORIGINAL in runner and '*path_reuse.OWN,*source.OWN' in runner)
ck('frozen/three reviews initially false before explicit committed execution',"frozen=False" in runner and "independent_static_review_passed=False,root_complete_queue_freeze_approved=False,latest_actual_prior_confirmed=False" in runner and "subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT)==path(n).read_bytes()" in runner)
ck('zero new solve/reconstruct/IK/NR/RNG/VI/formal declaration',"zero_calls=dict(IK=0,NR=0,projection=0,RBS=0,solve=0,RNG=0,VI_constructions=0,formal_table_I=0)" in runner)
ck('no retry and all original failures preserved by fresh claim/run',"'EXCLUSIVE_P_NO_RETRY_RESET_OR_RESUME'" in runner and "'OLD_SUPERVISION_ARTIFACT_NO_RETRY'" in supervisor and "'OTHER_ACTIVE_P4_EXECUTION'" in runner)
ck('outer O_EXCL FD, actual parent identity and conservative costs reused',"os.O_WRONLY|os.O_CREAT|os.O_EXCL" in supervisor and 'pass_fds=(fd,)' in supervisor and "wall=float(elapsed+Decimal('.01'));cpu=float(user+system+Decimal('.02'))" in supervisor)
ck('native/aligned collision separate immutable v3 with binaries/source/meshes',"collision_adapter_v3/manifest.json" in runner and "sorted(r['variant']for r in entries)==['aligned','native']" in runner and "entry['source_files_sha256'].items()" in runner and "entry['mesh_sha256'].items()" in runner)
ck('PRE keeps source/corrected/reconstructed and discrete-only boundaries',all(s in pre for s in ('387','386','UNKNOWN','RECONSTRUCTED','CORRECTED','不证明CCD','不重solve/reconstruct/投影')))

e=js(SOURCE+'/execution.json','2867a03699b8901c9e065bbcc1993a9ac14a7f624232f29ed603df89c1d09208')
post=js(POST,'fea6f01839a041430d10da796a0c7a59bd65dbf4bcf7487dc8c27a7c15358066')
ck('reuse exact independent transport111 PASS without rerunning audit',post['status']=='PASS_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST' and post['checks_total']==post['checks_passed']==111 and post['checks_failed']==0 and post['personnel_independent'] is True and post['solve_transport_qualified'] is True and post['external_supervision_qualified'] is True and post['independent_path_qualified'] is False)
ck('runner binds exact prior execution/POST and SBL schema',e['status']=='SOURCE_SINGLE_SOLVE_OBSERVED_PENDING_INDEPENDENT_POST' and reviewed[SOURCE+'/execution.json'] in runner and reviewed[POST] in runner and "post['schema']=='P4_SBL_PCS_SOLVE01_SAVED_INDEPENDENT_POST_V1'" in runner)
ck('SBL one process requires actual returncode/reaped-empty-group and both EOF',"r['returncode']==0" in runner and "r['actual_after_reap_group']==[]" in runner and "r['actual_pipe_EOF_observed']=={'stdout':True,'stderr':True}" in runner)
ck('source full before/after/raw/native/mesh retained binding and raw trace exact',all(s in runner for s in ("e['bound_files_sha256']==e['bound_files_after_sha256']","post['retained_sha256'].items()","e['runtime_mesh_sha256'].items()","e['retained_run_files_sha256'].items()","source.L.raw_trace(path(stderr).read_bytes())","path(row['saved_path']).read_bytes()==path(row['original_path']).read_bytes()==raw")))
scope=js('configs/p4_d080/execution_scope_v1.json')
ck('D080 I-V formal18000 unapproved and VI archival explicit',scope['allowed_environments']==['I','II','III','IV','V'] and scope['VI_future_science_authorized'] is False and scope['formal_table_I_D080']==18000 and scope['formal_execution_authorized'] is False and "scope['formal_table_I_D080']==18000" in runner and "scope['VI_future_science_authorized']is False" in runner)
ledgers=list((ROOT/'results/p4_full').glob('20261016_RECOVERY_ACTUAL_LEDGER_V*.json'))
lp=max(ledgers,key=lambda p:int(p.stem.rsplit('V',1)[1]));ledger=js(str(lp.relative_to(ROOT)))
actual={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'results/p4_full').glob('*_R2_*/execution.json') if p.parent.name!=RUN}
ck('latest actual prior covers all real executions with no lost/changed entry',{r['execution']:r['execution_sha256'] for r in ledger['executions']}==actual)
wall=math.fsum(r.get('charged_wall_s',r['wall_s']) for r in ledger['executions']);cpu=math.fsum(r.get('charged_cpu_s',r['cpu_s']) for r in ledger['executions'])
ck('actual cumulative costs exact and this fixed budget fits',wall==ledger['conservative_r2_sum_wall_s'] and cpu==ledger['conservative_r2_sum_cpu_s'] and wall+120<=3600 and cpu+240<=7200)
ck('runner recomputes actual prior and refuses all orphan charged attempts',"'LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS'" in runner and "'PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED'" in runner and "'ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING '" in runner and "if p.parent.name!=RUN" in runner)
ck('fresh target physical run/claim absent',(not (ROOT/'results/p4_full'/RUN).exists()) and not (ROOT/'results/p4_full/P4_R2_ABB_SBL_PCS_PATH_FULL387_120W_240CPU_20261018.claim.json').exists())

# Only this pure saved-array helper is imported, after checking its complete
# import whitelist and common helper source hash. No runner or model import.
ck('materializer only Counter plus hash-bound pure array common import',{n.module for n in ht.body if isinstance(n,ast.ImportFrom)}=={'collections'} and {a.name for n in ht.body if isinstance(n,ast.Import) for a in n.names}=={'materialize_p4_full_r2_abb_cbirrt_d_path_draft'} and '__main__' not in helper)
ck('common helper only math/struct/Counter, no import-time calls',{n.module for n in ast.parse(common).body if isinstance(n,ast.ImportFrom)}=={'collections'} and {a.name for n in ast.parse(common).body if isinstance(n,ast.Import) for a in n.names}=={'math','struct'} and not any(isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) for n in ast.parse(common).body))
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('independent_saved_sbl_path_materializer',ROOT/M);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
raw=read(SOURCE+'/request_00_stdout.bin');lines=raw.splitlines();ck('one original saved JSONLF response',len(lines)==1 and raw.endswith(b'\n'))
d=json.loads(lines[0]);q=module.materialize(d,d['request'])
ck('reference exact full queue387/386/5/6',len(q['nodes'])==387 and len(q['edges'])==5 and q['source_attempt_count']==6 and sum(len(x['node_ids'])-1 for x in q['edges'])==386 and q['original_dense_path_node_count']==387 and q['under_2048_full_queue_cap'] is True)
ck('true identities bridge32to49 and natural connect50 retained',q['source_identity_audit']['source_motion_path']==[1,7,32,49,3,2] and q['source_identity_audit']['source_bridge_motion_ids']==[32,49] and q['source_identity_audit']['native_connect_motion_id']==50 and q['source_identity_audit']['native_connect_role'] is None and q['source_identity_audit']['complete_tree_motion_count']==23)
ck('unknown connect null and SBL absence of planner_data explicit',"'UNINITIALIZED_NOT_READ'" in helper and 'NOT_EMITTED_BY_THIS_SBL_DRIVER' in q['source_identity_audit']['planner_data'])
ck('false original last edge attempt retained separately with complete M', [x['returned'] for x in q['all_original_attempts']]==[True,True,True,True,False,True] and [len(x['path_q12']) for x in q['all_original_attempts']]==[35,41,185,65,2,65] and [x['selected_attempt_index'] for x in q['edges']]==[0,1,2,3,5] and [x['consumed_attempt_indices'] for x in q['edges']]==[[0],[1],[2],[3],[4,5]])
ck('original roles/branch3 and full12 strict leaves intact',[x['active_chain'] for x in q['edges']]==[0,0,0,1,1] and all(x['branch']==3 for x in q['edges']) and max(v for x in q['edges'] for v in x['leaf_distances_rad'])==0.04975420918021825)
ck('full packed-binary64 queue retains A01 first/last and signed zero identity',len({packed(x) for x in q['nodes']})==387 and packed(q['nodes'][0])==packed(d['request']['start_q12']) and packed(q['nodes'][-1])==packed(d['request']['goal_q12']))
ck('native six-significant-digit display separate from binary64 physical queue','trace binary64' in pre and 'qualification uses trace binary64' in q['source_native_text_precision_policy'])
mutations={}
x=copy.deepcopy(d);x['trees_before_destruction']['nodes'][0]['parent_motion_id']=99;mutations['registered_parent_drift']=x
x=copy.deepcopy(d);x['milestones_q12'][0][5]=-0.0;mutations['signed_zero_endpoint_identity']=x
x=copy.deepcopy(d)
for row in x['trees_before_destruction']['nodes']:
    if row['motion_id']==50:row['a_chain']=0;row['a_chain_provenance']='GROW_ASSIGNED'
mutations['invent_initialized_connect_role']=x
x=copy.deepcopy(d)
for row in x['trace']:
    if row['kind']=='state_reconstruct' and row['event']=='entered' and row['id']==13028:row['args']['active_chain']=1
mutations['change_false_attempt_role']=x
x=copy.deepcopy(d)
for row in x['trace']:
    if row['kind']=='state_reconstruct' and row['event']=='completed' and row['id']==13028:row['result']['returned']=True
mutations['false_attempt_promoted_true']=x
x=copy.deepcopy(d)
for row in x['native_file_evidence']:
    if row['name']=='work/path.txt':b=bytearray.fromhex(row['bytes_hex']);b[0]=ord('4');row['bytes_hex']=b.hex()
mutations['native_final_header_disagrees']=x
for name,mutated in mutations.items():
    reason=None
    try:module.materialize(mutated,mutated['request'])
    except ValueError as exc:reason=str(exc)
    negative.append(dict(case=name,rejected=reason is not None,reason=reason));ck('independent saved negative '+name,reason is not None)
for name,h in list(reviewed.items()):
    p=Path(name);p=p if p.is_absolute() else ROOT/p
    ck('all reviewed sources/evidence still immutable '+name,hashlib.sha256(p.read_bytes()).hexdigest()==h)
failed=[c for c in checks if not c['passed']]
report=dict(schema='P4_SBL_PCS_PATH_INDEPENDENT_STATIC_REVIEW_V1',status='PASS_SBL_COMPLETE_SAVED_QUEUE_AND_INCREMENTAL_STATIC_REVIEW' if not failed else 'FAIL_STATIC_REVIEW',generated_at_utc=datetime.now(timezone.utc).isoformat(),personnel_independent=True,reviewer='sbl_independent_resume',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),failures=failed,checks=checks,reviewed_sha256=reviewed,original_physical_loop_AST_equal=True,original_physical_loop_source_equal=True,runner_import_calls=0,new_model_or_scientific_calls=0,new_compile_calls=0,new_describe_calls=0,pure_saved_array_helper_reference_calls=1,independent_negative_cases=negative,source_transport_POST_reused=POST,current_prior=dict(ledger=str(lp.relative_to(ROOT)),execution_count=len(actual),wall_s=wall,cpu_s=cpu),queue=dict(nodes=387,leaves=386,milestones=6,edges=5,attempts=6,failed_attempts_retained=1),limits=['Engineering/static and saved arrays only; independent physical full path remains pending unique frozen execution and saved-only POST.','Original writer internal fstream flags stay UNKNOWN; output shadow is RECONSTRUCTED_OUTPUT_METADATA_ONLY.','Physical loop and native/aligned discrete collision policy unchanged; no CCD/performance/formal statistics claim; VI archival only.'])
with OUT.with_suffix('.json').open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
with OUT.with_suffix('.md').open('x') as f:
    f.write('# SBL PCS 完整路径增量独立静审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'，失败'+str(report['checks_failed'])+'。\n\n复用原SOLVE01独立111项证书；完整原387节点/386叶、六milestone/五边、六attempt（含一false）与真实Motion/generation/自然桥身份均保留。六个纯保存数组反例均拒绝。原PCS物理loop源码与AST逐字相同，外GNUtime/清理监督仅改新run/schema标签。\n\n本审查无runner/模型导入、无编译、无describe及新科学运行。120wall/240CPU资格预算仍须root冻结最新协议并提交后唯一执行；目前不宣称物理路径通过。VI只读，正式18k未授权，CCD及原fstream内部状态仍未证。\n')
print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),output=str(OUT.with_suffix('.json').relative_to(ROOT)))))
if failed:raise SystemExit(1)
