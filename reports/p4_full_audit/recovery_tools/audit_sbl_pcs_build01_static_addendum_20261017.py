#!/usr/bin/env python3
"""Independent SBL engineering source-only review. No implementation import or run."""
from pathlib import Path
import ast,hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'reports/P4_FULL_R2_ABB_SBL_PCS_BUILD01_INDEPENDENT_STATIC_REVIEW_ADDENDUM_20261017.json'
EXPECTED={
'baselines/p4_full/geometry_consistent/abb_sbl_pcs_observation_draft.hpp':'7507648eb8ede25eea1cadcc32270a0bdf27633b1520de717718f6a907b986ac',
'baselines/p4_full/geometry_consistent/abb_sbl_pcs_instrumentation_draft.py':'cf5f5192840883634dfd3f18ea117dd505b66a8f1648391ae15113508ae2a237',
'baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_draft.cpp':'899fbabf80d2bf8b01e59efea81aa21077a3b113662c579661e044d6f66df7b9',
'scripts/build_p4_full_r2_abb_sbl_pcs_draft.py':'251f44b0f931a34a2c1e5cfb91c13632c11362392cc3fb339fba1bafd2427628',
'scripts/supervise_p4_full_r2_abb_sbl_pcs_build_draft.py':'411b522f9533fe663d61f4fa12dd30687febc380dc4d84de6759f8eb593b4ca0',
'reports/P4_FULL_R2_ABB_SBL_PCS_ENGINEERING_V1_PRE_DRAFT_20261017.md':'bbbe51a38d49d3367db42533f1817cc155b347307104bf52fc21c79af610ed44',
'reports/P4_FULL_R2_ABB_SBL_PCS_HISTORICAL_CONNECT_STATIC_CORRECTION_20261017.md':'ebc95d713092f5dc6da73fd2fd22517e0fa170c9b27f79bd5c0612390702d878',
'reports/P4_FULL_R2_ABB_SBL_PCS_ENGINEERING_SOURCE_CONFIGURATION_CORRECTIONS_20261017.md':'b0e9a909ca5da9c9e912b02d0da20063e12e75b1e0f16a228a4eca9f6e5a9925'}
checks=[];read={}
def raw(p):
 p=Path(p);p=p if p.is_absolute()else ROOT/p;b=p.read_bytes();read[str(p)]=hashlib.sha256(b).hexdigest();return b
def text(p):return raw(p).decode()
def ck(g,n,v):checks.append(dict(group=g,check=n,passed=bool(v)))
def contains(g,s,items):
 for value in items:ck(g,value,value in s)
def main():
 if OUT.exists()or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_REPORT_PRESERVED')
 contents={p:text(p)for p in EXPECTED}
 for p,want in EXPECTED.items():ck('stable','reviewed eight draft bytes '+p,hashlib.sha256(contents[p].encode()).hexdigest()==want)
 B=contents['scripts/build_p4_full_r2_abb_sbl_pcs_draft.py'];S=contents['scripts/supervise_p4_full_r2_abb_sbl_pcs_build_draft.py'];T=contents['baselines/p4_full/geometry_consistent/abb_sbl_pcs_instrumentation_draft.py'];D=contents['baselines/p4_full/geometry_consistent/abb_sbl_pcs_driver_draft.cpp'];H=contents['baselines/p4_full/geometry_consistent/abb_sbl_pcs_observation_draft.hpp']
 for name in ('scripts/build_p4_full_r2_abb_sbl_pcs_draft.py','scripts/supervise_p4_full_r2_abb_sbl_pcs_build_draft.py','baselines/p4_full/geometry_consistent/abb_sbl_pcs_instrumentation_draft.py'):
  tree=ast.parse(contents[name]);ck('AST','standard-library AST only '+name,isinstance(tree,ast.Module))
 transformer=ast.parse(T);assignments={}
 for node in transformer.body:
  if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
   try:assignments[node.targets[0].id]=ast.literal_eval(node.value)
   except (ValueError,TypeError):pass
 wraps=[n for n in ast.walk(transformer)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='wrap']
 ck('wrapper','exact16 literal scientific/lifecycle wrappers',len(wraps)==16)
 template=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1/geometry_consistent_plain');author=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning')
 for n in wraps:
  filename=assignments[n.args[0].id];signature=ast.literal_eval(n.args[1]);ck('wrapper','exact existing original signature '+signature,text(template/filename).count(signature)==1)
 for relative,want in [('planners/SBL_PCS.cpp',assignments['ORIGINAL_SBL']),('planners/SBL_PCS.h',assignments['ORIGINAL_HDR'])]:ck('author','author/template exact unchanged '+relative,hashlib.sha256(raw(template/relative)).hexdigest()==hashlib.sha256(raw(author/relative)).hexdigest()==want)
 contains('wrapper',T,['EXACT_AUTHOR_SBL_BYTES_REQUIRED','COMPLETE_AUTHOR_BODY_ONCE_REQUIRED','INVERSE_SBL_WRAPPER_BODY_MISMATCH','WHOLE_SBL_SOURCE_BYTES_NOT_REVERSIBLE','for file,signature,inserted,body in reversed(inverse)','H_or_D_or_NR_correction_present=False','observer_model_calls=0,observer_RNG_draws=0'])
 contains('lifecycle',H,['++next_lifetime,++generations[m],++next_state','const bool connect=connection_scope!=0','!connect','UNINITIALIZED_NOT_READ','x.a_chain_initialized?json(m->a_chain):json(nullptr)','original_children_before_parent_null','mark("motion_before_native_retirement",before)','state_to_motion.erase(item.state);live.erase(it)','RETIRE_EXACT_LIFETIME_TOKEN','NO_RESET_WHILE_SBL_OBJECTS_LIVE'])
 contains('lifecycle',T,['p4sbl::register_motion(&tree,motion)','p4sbl::prepare_retirement(motion)','p4sbl::retire(p4_retirement)','p4sbl::prepare_grid(grid)','p4sbl::retire_grid(p4_retirements)','p4sbl::ConnectionScope p4_connection_scope','p4sbl::paths_snapshot(mpath1,mpath2)','original_save_may_read_uninitialized_historical_connect_a_chain'])
 contains('setup-only',D,['std::string(argv[3])!="setup"','SEPARATE_SETUP_QUALIFICATION_REQUIRED_NO_SOLVE','og::SBL(si,.8,1)','ompl::RNG::setSeed(7);std::srand(7)','std::make_shared<ob::RealVectorStateSpace>(12)','setStateValidityCheckingResolution(.02)','start_grid_dim==dim&&goal_grid_dim==dim','{"native_grid_dimensions",{start_grid_dim,goal_grid_dim}}','REGISTRY_MUST_BE_EMPTY_AFTER_DESTRUCTION','OBSERVED_LINEAR_ACTION_MATRIX_NOT_PROTECTED_STORAGE_BYTES','sampler_allocated_by_observer'])
 ck('setup-only','no driver solve dispatch','->solve('not in D and '.solve('not in D)
 ck('setup-only','seed before first state-space construction',D.index('ompl::RNG::setSeed(7)')<D.index('std::make_shared<ob::RealVectorStateSpace>'))
 contains('setup-only',D,['sample<13','p->project(input.get(),output)','FINITE_PUBLIC_LINEAR_ACTION_REQUIRED','PUBLIC_LINEAR_ACTION_ORIGIN_MUST_BE_ZERO','output_binary64','actual_setup_library_RNG_draws','UNOBSERVED'])
 apis={
 '/opt/ros/humble/include/ompl-1.7/ompl/base/ProjectionEvaluator.h':['getDimension() const','getCellSizes() const','hasBounds() const','getBounds() const','userConfigured() const','Eigen::Ref<Eigen::VectorXd>'],
 '/opt/ros/humble/include/ompl-1.7/ompl/base/ScopedState.h':['explicit ScopedState(StateSpacePtr space)'],
 '/opt/ros/humble/include/ompl-1.7/ompl/base/ValidStateSampler.h':['getName() const'],
 '/opt/ros/humble/include/ompl-1.7/ompl/datastructures/Grid.h':['getDimension() const'],
 '/opt/ros/humble/include/ompl-1.7/ompl/base/spaces/RealVectorStateProjections.h':['class RealVectorLinearProjectionEvaluator','class RealVectorRandomLinearProjectionEvaluator','ProjectionMatrix projection_']}
 for p,names in apis.items():contains('actual C++ API',text(p),names)
 contains('author-original',text(author/'run/plan_PCS.cpp'),['step = {0.8, 0.6};','step[env-1]'])
 contains('dependencies',B,["'-MD','-MF','-'",'EXACTLY_FIVE_REAL_COMPILER_STDOUT_RULES_REQUIRED','FIVE_DISTINCT_FROZEN_TRANSLATION_UNITS_REQUIRED','EXACT_COMPLETE_FIVE_TU_COVERAGE_ONCE_REQUIRED','ACTUAL_PROTECTED_DEPENDENCY_NOT_IN_FROZEN_MANIFEST','compiler_created_individual_d_file=False','SYSTEM_SBL_HEADER_MUST_NOT_REPLACE_AUTHOR_CLASS','LINKED=(APC,SVC,COL,SBL)','NAMESPACE_ROOTS=(OMPL_HEADERS,KDL_HEADERS,EIGEN_HEADERS,JSON_HEADERS)','BOOST_MACRO_SUPPORT=','ADDED_HEADER_NAMESPACE_SET_OR_SHA_CHANGED'])
 bt=ast.parse(B);pqp=next(ast.literal_eval(n.value)for n in bt.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='PQP_FIXED_HEADERS'for x in n.targets))
 ck('dependencies','five specific fixed PQP headers',set(pqp)=={'BV.h','PQP.h','PQP_Compile.h','PQP_Internal.h','Tri.h'})
 for name,want in pqp.items():ck('dependencies','actual prefrozen PQP '+name,hashlib.sha256(raw(Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3/include')/name)).hexdigest()==want)
 contains('gate',B,['budge'+'t=dict(wall_s=45.,cpu_s=90.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.)','LATEST_LEDGER_MUST_COVER_ALL_ACTUAL_EXECUTIONS','PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED','ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING','UNCOMMITTED_BUILD_SOURCE_OR_PROTOCOL','EXCLUSIVE_FRESH_SBL_PCS_STAGE_RUN_CLAIM_REQUIRED','OTHER_ACTIVE_P4_EXECUTION','BUILT_NOT_QUERIED','STOP_FINAL_WALL_OR_CPU_BUDGET','compiler_group_members_after_cleanup','ACTUAL_COMPILER_GROUP_NOT_EMPTY_AFTER_KILL_WAIT'])
 ck('gate','builder timer starts accounting before validate; installed after preflight',B.index('begun=time.monotonic();used=cpu();commit=validate')<B.index('signal.setitimer(signal.ITIMER_REAL,.02,.02)'))
 btree=ast.parse(B);pc=[n for n in ast.walk(btree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='subprocess'and n.func.attr=='Popen']
 ck('gate','only compiler Popen in builder',len(pc)==1 and isinstance(pc[0].args[0],ast.Name)and pc[0].args[0].id=='command')
 contains('external',S,['os.O_WRONLY|os.O_CREAT|os.O_EXCL','pass_fds=(fd,)','proc.wait()','%e %U %S %x',"Decimal('.01')","Decimal('.02')",'wall<=min(45.,3600.-spec','cpu<=min(90.,7200.-spec','independent_POST_required=True'])
 contains('scope',contents['reports/P4_FULL_R2_ABB_SBL_PCS_ENGINEERING_V1_PRE_DRAFT_20261017.md'],['211','22500','974/974','BUILT_NOT_QUERIED'])
 for p,want in list(read.items()):ck('unchanged','review input preserved '+p,hashlib.sha256(Path(p).read_bytes()).hexdigest()==want)
 fail=[x for x in checks if not x['passed']]
 report=dict(corrected_invalid_audit_assertion='Initial audit required invented key grid_dimensions; actual native_grid_dimensions and values/gates are valid. Original source and failed report retained unchanged. This complete rerun corrects only auditor literal.',original_failed_report='reports/P4_FULL_R2_ABB_SBL_PCS_BUILD01_INDEPENDENT_STATIC_REVIEW_20261017.json',schema='P4_SBL_PCS_BUILD01_INDEPENDENT_STATIC_REVIEW_V1',status='PASS_SBL_PCS_BUILD01_ENGINEERING_ONLY_STATIC_REVIEW'if not fail else'FAIL_SBL_PCS_BUILD01_ENGINEERING_ONLY_STATIC_REVIEW',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of SBL implementation',personnel_independent=True,independent_static_review_passed=not fail,engineering_build_qualified=False,scientific_runtime_qualified=False,checks=checks,checks_total=len(checks),checks_passed=len(checks)-len(fail),checks_failed=len(fail),failures=fail,reviewed_source_sha256=EXPECTED,retained_sha256=read,new_execution_counts={k:0 for k in ('project_import','describe','transform','compile','binary','setup','model','FK','IK','collision','RBS','solve','protocol','claim','prior','VI','formal')},byte_reversal_executed=False,limits=['Static source/AST/actual-header review only. Source reversal guards and complete-body policy reviewed; transform not invoked. Actual compiler/dependency/source/ELF/external-cost POST remains required.','Whole GNUtime child measures import/preflight/header scans/validation/compiler/final persistence/exit; preflight has no installed hard watchdog. Actual full-child upper must meet45wall/90CPU. Supervisor own metadata/fsync costs excluded.','Original historical connect a_chain read in save remains; setup-only driver refuses solve before model construction. Future solve requires separate root-cause qualification.','Future public13 observes only existing linear action, not protected storage bytes. Bound actual lib project pure multiplication evidence remains a separate pre-setup gate; setup RNG internals UNOBSERVED.','211 obligations,VI974/974 remaining0,formal0/22500 persist; no path/performance/RSS/PCS advantage or full-paper inference.'])
 with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
 with OUT.with_suffix('.md').open('x')as f:f.write('# SBL_PCS BUILD01 独立工程静审\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(len(checks))+'，失败'+str(len(fail))+'。\n\n独立读取八稿、16原签名、作者SBL/配置、实际OMPL API与五PQP头。仅标准库AST/文本/字节检查；零项目import、describe、transform、compile、binary、setup、solve、protocol/claim/prior。允许root冻结唯一工程构建，成功仍须真实POST，不能推出运行资格。\n\n外层GNUtime覆盖完整child；preflight虽计费但尚无硬watchdog，最终实际45wall/90CPU门必须通过。历史connect的a_chain风险保留，driver在构造前拒solve；public13只是未来公有线性作用，实际库纯乘法证据仍待setup前门。\n\n全部211义务、VI974/974余0、formal0/22500保留。\n')
 print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(fail),failures=fail),ensure_ascii=False))
 if fail:raise SystemExit(2)
if __name__=='__main__':main()
