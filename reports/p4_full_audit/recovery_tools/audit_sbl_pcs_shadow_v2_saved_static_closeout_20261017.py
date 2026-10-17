#!/usr/bin/python3
# Saved-evidence/static-AST closeout only. Never invokes either transform again.
import ast
import hashlib
import json
from pathlib import Path
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
BASE=ROOT/'baselines/p4_full/geometry_consistent'
R=ROOT/'reports'
STEM='P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_INDEPENDENT_STATIC_CLOSEOUT_20261017'
jf=(R/(STEM+'.json')).open('x',encoding='utf-8');mf=(R/(STEM+'.md')).open('x',encoding='utf-8')
checks=[]
def ck(n,b,d=None):checks.append({'name':n,'passed':bool(b),'detail':d})
def sha(b):return hashlib.sha256(b).hexdigest()
p1=R/'P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_20261017.json'
p2=R/'P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_ADDENDUM_20261017.json'
e1=json.loads(p1.read_text());e2=json.loads(p2.read_text())
ck('initial_check_executed_zero_transforms',e1['pure_text_transform_calls']=={'v1':0,'v2':0})
ck('single_authorized_check_v1_v2_each_once',e2['pure_text_transform_calls']=={'v1':1,'v2':1})
ck('addendum_failure_is_independent_checker',e2['exception']=={'type':'ValueError','message':'INDEPENDENT_RETURNING_LAMBDA_REQUIRED'})
ck('all_other_addendum_checks_passed',sum(not c['passed'] for c in e2['checks'])==1)
ck('no_scientific_calls_both_prior',all(e[k]==0 for e in (e1,e2) for k in ('scientific_calls','compile_calls','model_calls','setup_calls','solve_calls','stage_writes','original_or_candidate_mutations')))
texts={n:(BASE/n).read_text() for n in ('abb_sbl_pcs_instrumentation_draft.py','abb_sbl_pcs_instrumentation_shadow_v2_draft.py')}
trees={n:ast.parse(t) for n,t in texts.items()}
def calls(tree):
    f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='instrument_sources')
    return [x.value for x in f.body if isinstance(x,ast.Expr) and isinstance(x.value,ast.Call) and isinstance(x.value.func,ast.Name) and x.value.func.id=='wrap']
a,b=[calls(trees[n]) for n in texts]
ck('AST_both_exact16_wrapper_calls',len(a)==len(b)==16)
SAVE='void ompl::geometric::SBL::save2file(vector<Motion*> mpath1, vector<Motion*> mpath2)'
class Normalize(ast.NodeTransformer):
    def visit_Name(self,n):return ast.copy_location(ast.Constant(value=SAVE),n) if n.id=='SAVE' else n
for i,(ca,cb) in enumerate(zip(a,b)):
    ck('AST_wrapper_call_same_'+str(i),ast.dump(ca,include_attributes=False)==ast.dump(Normalize().visit(cb),include_attributes=False))
ck('actual_collision_wrapper_int',ast.literal_eval(a[8].args[2])=='collision' and ast.literal_eval(a[8].args[3])=='int')
prior_checker=(R/'p4_full_audit/recovery_tools/audit_sbl_pcs_shadow_v2_independent_addendum_20261017.py').read_text()
ck('failed_checker_regex_excluded_int',"(?:void|bool|State)" in prior_checker and "(?:void|bool|State|int)" not in prior_checker)
ck('failure_precedes_collision_body_record',not any(c['name']=='v1_body_collision' for c in e2['checks']) and any(c['name']=='v1_body_native_ik' and c['passed'] for c in e2['checks']))
ck('completed_inverse_checks_eight_original_bodies',len([c for c in e2['checks'] if c['name'].startswith('v1_body_') and c['passed']])==8)
ck('both_transform_returns_precede_independent_inverse',prior_checker.index("out2,manifest2=v2['instrument_sources'](original)")<prior_checker.index("unwrap(out1,manifest1,original,'v1')"))
new_text=texts['abb_sbl_pcs_instrumentation_shadow_v2_draft.py']
ck('transform_checks_full_inverse_before_return',new_text.index("if restored!=original:raise ValueError('WHOLE_SBL_SOURCE_BYTES_NOT_REVERSIBLE')")<new_text.index('return current,dict('))
ck('new_save_verbatim_disclaimer','save_body_verbatim_original=False' in new_text and 'save_body_contains_exactly_two_documented_IO_expression_edits=True' in new_text)
ck('new_header_required','abb_sbl_pcs_observation_shadow_v2_draft.hpp' in new_text)
header=BASE/'abb_sbl_pcs_observation_shadow_v2_draft.hpp'
ck('candidate_header_unchanged',sha(header.read_bytes())=='3c0d3031d53532bb077e7eabb3911aa9f911f771bb34216406cf0a71fb9108c3')
ck('candidate_transform_unchanged',sha(new_text.encode())=='926592eb43ef8ad90a6434a30aa613c2c6c41416e9f9120c734b76adc3a39209')
retained={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in (p1,p2,R/'P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_20261017.md',R/'P4_FULL_R2_ABB_SBL_PCS_WRITER_SHADOW_V2_INDEPENDENT_STATIC_REVIEW_ADDENDUM_20261017.md',R/'p4_full_audit/recovery_tools/audit_sbl_pcs_shadow_v2_independent_20261017.py',R/'p4_full_audit/recovery_tools/audit_sbl_pcs_shadow_v2_independent_addendum_20261017.py',header,BASE/'abb_sbl_pcs_instrumentation_shadow_v2_draft.py')}
d={'schema':'P4_SBL_SHADOW_V2_SAVED_STATIC_CLOSEOUT_V1','status':'STATIC_DESIGN_QUALIFIED_FULL_INDEPENDENT_OUTPUT_INVERSE_DEFERRED' if all(c['passed'] for c in checks) else 'STATIC_CLOSEOUT_FAILED_RETAINED','personnel_independent':True,'reviewer':'sbl_shadow_independent','checks_total':len(checks),'checks_passed':sum(c['passed'] for c in checks),'checks_failed':sum(not c['passed'] for c in checks),'checks':checks,'new_transform_calls':0,'cumulative_transform_calls':{'v1':1,'v2':1},'compile_calls':0,'scientific_calls':0,'stage_writes':0,'retained_sha256':retained,'source_control_review':'Author 3 assigned writes/2 metadata reads/4 addMotion sources; registry root/grow captures assigned optional 0/1 once, connect is unknown for lifetime, no Motion storage/layout/ctor write; source scientific control unmodified except two versioned output expressions.','evidence_limits':['Both pure-text transforms returned normally through their internal full-file inverse guards in the one authorized engineering check; independent output inversion stopped after eight v1 body checks because reviewer regex excluded int.','The in-memory transformed outputs were not persisted before the reviewer exception. No independent full-five-file output SHA or complete v1/v2 output difference certificate is claimed.','This closeout only parses AST and reads saved reports. It does not repeat either transform.','Later new engineering stage must independently check all five emitted files, exactly two writer edits, v1/v2 expected output boundaries and actual C++/writer buffer persistence.','No compiled/runtime header qualification, sidecar saved, text-write success, historical-UB occurrence, local/solve/path certificate or algorithm/timing equivalence is claimed.'],'D080':'Read AGENTS, CODEX_START_HERE, D080 decision/task/handoff; I-V approved, VI archived, original 211/22500 preserved, future D080 formal18000 separately approved. Old handoff setup pending is superseded by actual SETUP01 certificate and V25.'}
json.dump(d,jf,ensure_ascii=False,indent=2);jf.write('\n');jf.close()
lines=['# SBL shadow v2 独立静审收尾：静态设计合格，完整输出独立逆核待新工程 stage','',f"状态：`{d['status']}`；本补记静态 {d['checks_passed']}/{d['checks_total']}。",'', '原始审查器两处我方文本错误在 transform 前停止，v1/v2 调用均0。第一次补记才实际各调用1次，两 transform 正常返回，已越过它们自身的五文件逐字逆恢复 guard。随后独立逆核的lambda正则漏列 collision 的 int 返回类型，核过8个 v1原 body后停止；该失败属于审查器，未发现候选科学源码缺陷。原两份脚本/JSON/MD全部保留，禁止将其固定叙述的未完成后续检查当成证据。','', '遵循主代理不重复已执行transform的限制，本收尾只读保存证据和Python AST，新增transform0。独立核对16个wrapper调用的原文件/签名/观察kind/result/args/returns/pre/post均相同（仅SAVE常量引用归一），并定位原失败为int正则遗漏。未持久化的内存输出已随上次进程结束，不能声称本项完成了独立五文件输出逆恢复、输出SHA或完整v1/v2差异核验。','', '源码静态边界有效：原三赋值/两writer读取/四addMotion来源；root/grow仅在原赋值之后捕获optional；connect整个lifetime始终unknown，不根据parent、RBS成功角色或地址复用补值。无Motion布局/ctor/成员写回；仅两writer表达式改用shadow；其他原科学控制语句及v1 wrapper位置不变。已知0由optional持值保留，unknown文本-1/JSONnull；plain/trace均收集attempt。header无落盘sidecar，写成功未知。','', '下一项新的工程stage必须对真实发出的五文件独立逆核并显式选择v2 header，冻结driver保存buffer及实际ik_path行序/三列/写成功检查。该工程尚未执行，本项不解除local/solve/path科学门。没有编译、模型、setup/solve/RBS/IK/采样/碰撞，不改共享治理或预算。','', '已读D080五文件，当前批准范围I–V，VI只读归档；211和原22500事实保留，D08018000正式统计另审。不重复II四条路径；最新SETUP01/V25直接复用，不采用旧handoff的setup待运行描述。不进P2/Isaac。','',f"JSON：`reports/{STEM}.json`。",'']
mf.write('\n'.join(lines));mf.close()
print(json.dumps({'status':d['status'],'checks_passed':d['checks_passed'],'checks_total':d['checks_total'],'json_sha256':sha((R/(STEM+'.json')).read_bytes()),'md_sha256':sha((R/(STEM+'.md')).read_bytes())}))
