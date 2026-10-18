#!/usr/bin/env python3
"""Incremental saved-manifest/AST review only; never import or describe builder."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_INCREMENTAL_INDEPENDENT_PRE_20261018'
BUILDER='scripts/p4_d080/build_v_pcs_build02_tail_v1_draft.py'
SUPERVISOR='scripts/p4_d080/supervise_v_pcs_build02_tail_v1_draft.py'
PRE='reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_PRE_DRAFT_20261018.md'
DRAFT='configs/p4_d080/v_pcs_build02_tail_v1.DRAFT.json'
POST='reports/P4_D080_ENV_V_PCS_BUILD01_FAILURE_SAVED_INDEPENDENT_POST_20261018.json'
POSTSHA='3dca76842b2f50751bd9c0455b592dff89dd4dbf7c09fbf7dfcf72c487d9576a'
OLD='scripts/p4_d080/build_v_pcs_local_v1_draft.py'
OLD_SUPERVISOR='scripts/p4_d080/supervise_v_pcs_build_v1_draft.py'
OLD_STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1')
STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_build02')
RUN='20261018_R2_D080_V_PCS_BUILD02_TAIL'
checks=[];reviewed={}
def ck(n,v):checks.append(dict(check=n,passed=bool(v)))
def path(n):
    p=Path(n);return p if p.is_absolute()else ROOT/p
def sha(n):return hashlib.sha256(path(n).read_bytes()).hexdigest()
def read(n,want=None):
    b=path(n).read_bytes();reviewed[n]=hashlib.sha256(b).hexdigest()
    if want:ck('exact reviewed SHA '+n,reviewed[n]==want)
    return b
def js(n,want=None):return json.loads(read(n,want))
def fn(t,n):return next(x for x in t.body if isinstance(x,ast.FunctionDef)and x.name==n)
def dump(n):return ast.dump(n,include_attributes=False)

b=read(BUILDER,'7ecc6e334112f580173b1e250ea2e8ef465b87e179c8de6505eabb69d5f06477').decode()
s=read(SUPERVISOR,'5c736ec386bba793f5172ccab3e16c4c2dba7df6aad6a46a8f28a00a26b8bd32').decode()
pre=read(PRE,'0c9a3a83c1af2812093966ea5c913f080ad4192a374cb4098570329f533f87b2').decode()
old=read(OLD).decode();olds=read(OLD_SUPERVISOR).decode();bt,st,ot=[ast.parse(x)for x in(b,s,old)]
ck('new sources parse and no review-time builder/model import',True)
post=js(POST,POSTSHA);e=js(post['execution'],post['execution_sha256']);p=js(DRAFT,'72fd1aa90d4590c178f1dec8b00d5f2c75f947990667fc881c45c111ae922cef')
ck('reuse exact independent failure78 and first-collected17 without re-audit',post['personnel_independent']is True and post['checks_total']==post['checks_passed']==78 and post['checks_failed']==0 and post['engineering_build_qualified']is False and post['completed_translation_units']==8 and len(post['reusable_saved_build_assets'])==17)
ck('original build failure and historical object UNKNOWN remain explicit',e['status']==post['original_execution_status']=='STOP_ENGINEERING_FAILURE_RETAINED_PREFIX'and e['error']==post['original_error']=='RuntimeError: BUILD_WORKING_CAP40W80CPU_RESERVE_FINAL45W90CPU'and post['original_STOP_object_sha256_status']=='UNKNOWN_NOT_RECORDED_AT_STOP'and POSTSHA in b and "post['engineering_build_qualified']is False"in b and "'original_STOP_object_sha256_status':'UNKNOWN_NOT_RECORDED_AT_STOP'"in b)
ck('draft initially unapproved and only20wall40CPU15work30CPU',p['schema']=='P4_D080_V_PCS_BUILD02_TAIL_FROZEN_V1'and all(p[x]is False for x in('frozen','independent_review_passed','engineering_execution_authorized','scientific_execution_authorized','formal_execution_authorized'))and p['budget']==dict(wall_s=20,cpu_s=40)and p['working_budget']==dict(wall_s=15,cpu_s=30)and p['stage_root']==str(STAGE)and p['run_name']==RUN)
ck('builder admits exact limits and zero science only after freeze',all(x in b for x in("spec['budget']=={'wall_s':20,'cpu_s':40}","spec['working_budget']=={'wall_s':15,'cpu_s':30}","spec['scientific_execution_authorized']is False","spec['formal_execution_authorized']is False","time.monotonic()-started<15 and cpu()-before_cpu+live<30","record['wall_s'] >= 20 or record['cpu_s'] >= 40")))
ck('proven prior invoke dependency functions direct aliases only',"cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke"in b and "evidence=B.dependency_evidence(dep,obj,src,{},bound,state)"in b and not any(isinstance(x,ast.FunctionDef)and x.name in('invoke','validate_prior','dependency_evidence')for x in bt.body))
ck('only reviewed B identity globals changed new run stage supervisor',"B.RUN_NAME=RUN_NAME;B.RUN=RUN;B.STAGE=STAGE;B.SUPERVISOR=SUPERVISOR"in b and "bound,meshes,libraries=B.frozen_assets(spec,protocol)"in b)
ck('GNUtime parent argv inode body AST identical prior reviewed source',dump(fn(bt,'validate_supervision'))==dump(fn(ot,'validate_supervision')))
envelope=lambda x:x[x.index('        timing_valid=False;'):x.index('        payload=dict(')]
ck('whole exact Decimal three observation envelope copied without change',envelope(s)==envelope(olds))
ck('external20/40 and current cumulative3600/7200 admission no silent fallback',"wall<=min(20.,3600.-spec['prior']['wall_s'])"in s and "cpu<=min(40.,7200.-spec['prior']['cpu_s'])"in s and "bool(timing_valid and envelope_valid and identity_unchanged"in s and "'EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'"in s)
ck('child originalRLIMIT90 distinguished from live group30 work and40 total','resource.setrlimit(resource.RLIMIT_CPU, (90, 90))'in old and all(x in pre for x in('RLIMIT_CPU=90','15/30','20/40')))
bound=p['bound_files_sha256'];normalized={str(path(n).resolve()):w for n,w in bound.items()}
oldsets={**e['bound_files_sha256'],**e['staged_after_sha256'],**e['dependencies_after_sha256'],**post['retained_sha256']}
ck('draft prebinds complete old source staged dependency and POST evidence union',all(normalized.get(str(path(n).resolve()))==want for n,want in oldsets.items())and normalized.get(str(path(POST).resolve()))==POSTSHA)
assets=post['reusable_saved_build_assets'];objects=[x for x in assets if x['kind']=='completed_ELF64_relocatable'];deps=[x for x in assets if x['kind']=='gcc_MD_dependency'];bins=[x for x in assets if x['kind']=='linked_ELF64_executable']
ck('first-collected17 original identities current and prebound',len(objects)==len(deps)==8 and len(bins)==1 and bins[0]['mode']=='plain'and all(path(x['path']).is_relative_to(OLD_STAGE)and sha(x['path'])==x['sha256']==normalized.get(str(path(x['path']).resolve()))and path(x['path']).stat().st_size==x['size_bytes']and path(x['path']).stat().st_mtime_ns==x['mtime_ns']for x in assets))
ck('eight original object hash UNKNOWN never promoted',all(x['original_STOP_sha256']is None and x['original_STOP_sha256_status']=='UNKNOWN_NOT_RECORDED_AT_STOP'for x in objects)and "'ORIGINAL_OBJECT_HASH_UNKNOWN_MUST_REMAIN_EXPLICIT'"in b)
ck('firstcollected identity required before and after new tail',all(x in b for x in("stat.st_mtime_ns==row['mtime_ns']","stat.st_size==row['size_bytes']","sha(p)==row['sha256']==bound.get(str(p.resolve()))","'FIRST_COLLECTED_OLD_ARTIFACT_BYTES_OR_IDENTITY_CHANGED'","s.st_mtime_ns==row['mtime_ns']","'FINAL_FIRST_COLLECTED_ARTIFACT_BYTES_OR_IDENTITY_CHANGED'")))
ck('new source helper and PRE exact bytes prebound',all(normalized.get(str(path(n).resolve()))==sha(n)for n in(BUILDER,SUPERVISOR,PRE,OLD)))
oldtrace=e['targets'][1]['commands'][3]['argv'];oldplain=e['targets'][0]['commands'];oldtr=OLD_STAGE/'trace';dest=STAGE/'trace'
expected=[]
for i,rel in((3,'validity_checkers/collisionDetection.cpp'),(4,'planners/RRT_PCS.cpp')):
    src=oldtr/rel;obj=dest/(str(i)+'_'+src.stem+'.o');dep=obj.with_suffix('.d');expected.append(oldtrace[:-9]+['-MD','-MF',str(dep),'-MT',str(obj),'-c',str(src),'-o',str(obj)])
newobjects=[oldtr/'0_comau_v_pcs_local_driver_v1_draft.o',oldtr/'1_apc_class.o',oldtr/'2_StateValidityCheckerPCS.o',dest/'3_collisionDetection.o',dest/'4_RRT_PCS.o']
expected.append(oldplain[-1]['argv'][:2]+[str(x)for x in newobjects]+oldplain[-1]['argv'][7:-1]+[str(dest/'v_pcs_local')])
ck('draft exact original flags two trace sources only new MF MT outputs and ordered link',p['commands']==expected and len(p['commands'])==3)
tc=ast.get_source_segment(b,fn(bt,'tail_commands'))
ck('tail command generator mirrors exact frozen arrays and validation refuses drift',all(x in tc for x in("sources=[old/'validity_checkers/collisionDetection.cpp',old/'planners/RRT_PCS.cpp']","'-std=c++17','-O2','-Wall','-Wextra','-pthread','-DP4V_TRACE_MODE=1'","'-I'+str(old)","'-include',str(old/B.OBSERVER.name)","enumerate(sources,3)","'-MD','-MF',str(dep),'-MT',str(obj),'-c',str(source),'-o',str(obj)","old/'0_comau_v_pcs_local_driver_v1_draft.o',old/'1_apc_class.o',old/'2_StateValidityCheckerPCS.o',*new"))and "require(spec['commands']==tail_commands(libraries)"in b)
ck('runtime exact two compile then one link no old target build or transform',"for index,command in enumerate(spec['commands'][:2],3):"in b and "invoke(spec['commands'][2],OLD_STAGE/'trace',RUN/'trace_link',target,state,check)"in b and "'new_commands':[],'new_compile_calls':0,'binary_execution_calls':0"in b and "'source_transform_calls':0"in b and "'reused_old_object_count':3"in b)
ck('all outputs new stage original incomplete assets stay absent',not STAGE.exists()and not(ROOT/'results/p4_full'/RUN).exists()and all(not(oldtr/n).exists()for n in('3_collisionDetection.o','3_collisionDetection.d','4_RRT_PCS.o','4_RRT_PCS.d','v_pcs_local'))and "'FRESH_TAIL_RUN_STAGE_NO_RETRY_OR_OVERWRITE'"in b and "'ORIGINAL_FAILED_OR_UNSTARTED_OUTPUTS_MUST_REMAIN_ABSENT'"in b)
ck('new actual MD protected dependencies cannot be patched after query',"B.dependency_evidence(dep,obj,src,{},bound,state)"in b and "all(bound.get(n)==w for n,w in evidence['actual_dependencies_sha256'].items()if Path(n).is_relative_to(OLD_STAGE))"in b and "'ORIGINAL_STAGE_ACTUAL_HEADER_AND_SOURCE_BYTES_MUST_BE_FROZEN'"in b)
ck('new object and linked ELF final byte hashes recorded without execution',"state['staged'][str(obj.resolve())]=sha(obj)"in b and "state['staged'][str(binary.resolve())]=sha(binary)"in b and "binary_sha256=sha(binary)"in b)
ck('committed own source protocol and fixed failure cert required before fresh claim',"for filename in [Path(__file__).resolve(),SUPERVISOR,PRE,Path(B.__file__).resolve(),SOURCE_POST,args.protocol]"in b and "'FROZEN_OWN_AND_REUSED_SOURCE_PROTOCOL_MUST_BE_COMMITTED_'"in b and "write_once(RUN/'claim.json',record)"in b)
ck('all compiler groups killed reaped empty and logs persisted before final receipt',all(x in b for x in("proc.wait(timeout=2.)","entry['members_after_cleanup'] = compiler_group_members(proc.pid)","'COMPILER_GROUP_NOT_EMPTY_AFTER_KILL_WAIT'","record['compile_log_sha256']","'cost_receipt.json'","'UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'")))
lp=p['prior']['ledger'];ledger=js(lp,'504a57af9ba144f7c36abcffe6bb9c7905ec76358d4ec38ddb3397f230f92517')
actual={str(x.relative_to(ROOT)):sha(x)for x in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')};actual.update({str(x.relative_to(ROOT)):sha(x)for x in(ROOT/'results/p4_d080').glob('*/execution.json')})
ck('draft V31 latest full actual execution map and exact conservative sums',len(ledger['executions'])==49 and actual=={r['execution']:r['execution_sha256']for r in ledger['executions']}and p['prior']['ledger_sha256']==sha(lp)and p['prior']['wall_s']==math.fsum(x.get('charged_wall_s',x['wall_s'])for x in ledger['executions'])and p['prior']['cpu_s']==math.fsum(x.get('charged_cpu_s',x['cpu_s'])for x in ledger['executions']))
evidence={str(path(lp).resolve()):sha(lp)}
for row in ledger['executions']:
    evidence[str(path(row['execution']).resolve())]=row['execution_sha256']
    if 'charged_wall_s'not in row:continue
    evidence[str(path(row['external_post']).resolve())]=row['external_post_sha256'];evidence[str(path(row['external_time']).resolve())]=row['external_time_sha256']
    cp=path(row['execution']).parent.parent/(row['run_id']+'.supervision.charge.json');c=json.loads(cp.read_bytes());evidence[str(cp.resolve())]=sha(cp)
    for n in('receipt','metadata','stderr'):
        q=path(c[n]);evidence[str(q.resolve())]=sha(q)
ck('all V31 execution POST log charge receipt and metadata evidence prebound',all(normalized.get(n)==w for n,w in evidence.items()))
ck('new20/40 fits old cumulative budget without adding science or VI',p['prior']['wall_s']+20<=3600 and p['prior']['cpu_s']+40<=7200 and p['D080_original_formal_denominator']==22500 and p['D080_approved_formal_denominator']==18000 and p['VI_future_execution_authorized']is p['formal_statistics_authorized']is False and p['new_compile_calls']==2 and p['new_link_calls']==1 and p['reused_translation_units']==8 and p['source_transform_calls']==0)
ck('all draft4792 current bound input bytes exact',len(bound)==4792 and all(sha(n)==want for n,want in bound.items()))
ck('PRE source failure nonqualification old stage and RLIMIT cost boundaries explicit',all(x in pre for x in('旧stage只读','engineering_build_qualified=false','UNKNOWN_NOT_RECORDED_AT_STOP','Decimal','不重编旧8TU','20/40','原STOP')))
for n,h in list(reviewed.items()):ck('all reviewed inputs stable '+n,sha(n)==h)
failed=[x for x in checks if not x['passed']]
report=dict(schema='P4_D080_V_PCS_BUILD02_TAIL_INCREMENTAL_INDEPENDENT_PRE_V1',status='PASS_INCREMENTAL_BUILD02_TAIL_STATIC_ONLY'if not failed else'FAIL_TAIL_STATIC_REVIEW',generated_at_utc=datetime.now(timezone.utc).isoformat(),personnel_independent=True,reviewer='/root/sbl_independent_resume',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,reviewed_sha256=reviewed,source_sha256={n:reviewed[n]for n in(BUILDER,SUPERVISOR,PRE)},draft_protocol=DRAFT,draft_protocol_sha256=reviewed[DRAFT],reused_failure_POST=POST,reused_failure_POST_sha256=POSTSHA,current_prior=p['prior'],new_scientific_model_import_describe_compile_link_transform_binary_query_calls=0,original_BUILD01_engineering_build_qualified=False,original_object_STOP_hash_status='UNKNOWN_NOT_RECORDED_AT_STOP',new_build_compile_calls_authorized_only_after_root_freeze=2,new_build_link_calls_authorized_only_after_root_freeze=1,retained_old_completed_TUs=8,firstcollected_assets=17,limits=['Static increment and current saved-byte identity only; no old8TU body/pair repeat, transform, builder import or execution.','New stage two trace TUs and link20wall40CPU;15/30 working governor,5/10 reserve; inherited childRLIMIT90 is not declared40 hard cap.','Root may append this certificate binding and set frozen/independent/engineering flags true, preserve all scientific/formal false and exact approved commands.','Same-source composite engineering certificate remains pending real new tail compile and saved-only POST; original BUILD01 remains failed.'])
with OUT.with_suffix('.json').open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
with OUT.with_suffix('.md').open('x')as f:f.write('# V BUILD02 尾段增量独立静审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'，失败'+str(report['checks_failed'])+'。\n\n复用原失败78项与首收集17资产证书；不重审旧8TU科学body，不导入或describe builder。原stage只读，新stage仅两trace TU和一次link，原flags/源/include/library保留；20wall/40CPU总帽、15/30工作帽和外三观测Decimal计费。原BUILD01 false、对象STOP哈希UNKNOWN及原费用永久保留。\n\n本次无编译/链接/transform/模型/query/binary/科学调用。root须冻结并提交精确协议才可唯一执行。\n')
print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),failures=failed)))
if failed:raise SystemExit(2)
