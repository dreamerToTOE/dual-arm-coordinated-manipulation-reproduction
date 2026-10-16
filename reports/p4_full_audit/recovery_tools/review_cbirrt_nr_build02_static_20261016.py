#!/usr/bin/env python3
"""Independent source/AST + actual saved prior only. No builder/parser import or execution."""
from pathlib import Path
import ast,datetime,hashlib,json,math
ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
B='scripts/build_p4_full_r2_abb_cbirrt_nr_v2_draft.py'
S='scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_v2_draft.py'
P='reports/P4_FULL_R2_ABB_CBIRRT_NR_ENGINEERING_V2_PRE_DRAFT_20261016.md'
EXPECTED={B:'b9b0274dec6f6c2ccb014f907e145619425e474b5b3a752423afe84834ec5c3d',S:'4860db3c64b30650008ab3ad40d172f1b3c12f581e710ee20fafb1b9464a8be3',P:'4683b3a1d6248e2d8b05aba6f1e951a65baf47b05fadd5dab747a82c7904312b'}
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_NR_BUILD02_INDEPENDENT_STATIC_REVIEW_20261016'
retained={};checks=[]
def raw(n):
 p=Path(n);p=p if p.is_absolute()else ROOT/p;b=p.read_bytes();retained[str(p)]=hashlib.sha256(b).hexdigest();return b
def read(n):return json.loads(raw(n))
def ck(n,ok):checks.append(dict(check=n,passed=bool(ok)))
def fn(t,n):return next(v for v in t.body if isinstance(v,ast.FunctionDef)and v.name==n)
def norm(v):return ast.dump(v,include_attributes=False)
def assign(t,n):return next(v.value for v in ast.walk(t)if isinstance(v,ast.Assign)and len(v.targets)==1 and isinstance(v.targets[0],ast.Name)and v.targets[0].id==n)
def callcount(t,n):return sum(isinstance(v,ast.Call)and isinstance(v.func,ast.Attribute)and v.func.attr==n for v in ast.walk(t))

for n,w in EXPECTED.items():ck('exact stable new3 SHA '+n,hashlib.sha256(raw(n)).hexdigest()==w)
b,s,p=(raw(n).decode()for n in(B,S,P));bt,st=ast.parse(b),ast.parse(s)
oldb=ast.parse(raw('scripts/build_p4_full_r2_abb_cbirrt_nr_draft.py'));olds=ast.parse(raw('scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_draft.py'))
for n in('require','path','durable_new','cpu','current_prior','added_header_assets','protected_dependency','compiler_group_members','preview','validate','supervisor_proof','main'):
 ck('existing complete function unchanged '+n,norm(fn(bt,n))==norm(fn(oldb,n)))
review=read('reports/P4_FULL_R2_ABB_CBIRRT_NR_ENGINEERING_INDEPENDENT_STATIC_REVIEW_V4_20261016.json')
for n,w in review['reviewed_source_sha256'].items():ck('original reviewed6 bytes remain '+n,hashlib.sha256(raw(n)).hexdigest()==w)
ck('scientific3 and numerical seam not edited or copied into new source',all(q not in b for q in('p4nr_iface::physical_gd','growTree(','si_->distance(','P4CBNR_BODY'))and
 'HEADER=\'baselines/p4_full/geometry_consistent/abb_cbirrt_nr_observation_draft.hpp\''in b and
 'DRIVER=\'baselines/p4_full/geometry_consistent/abb_cbirrt_nr_driver_draft.cpp\''in b and
 'TRANSFORM=\'baselines/p4_full/geometry_consistent/abb_cbirrt_nr_instrumentation_draft.py\''in b)
oldcommand=assign(fn(oldb,'build'),'command');command=assign(fn(bt,'build'),'command')
ck('actual compiler argv only adds MF stdout',len(command.elts)==len(oldcommand.elts)+2 and [v.value if isinstance(v,ast.Constant)else None for v in command.elts[1:4]]==['-MD','-MF','-']and
 [norm(v)for v in command.elts[:2]+command.elts[4:]]==[norm(v)for v in oldcommand.elts])
ck('one compiler process zero queries solves binary calls',callcount(bt,'Popen')==1 and 'query_calls=0,solve_calls=0,binary_execution_calls=0'in b and 'scientific_execution_authorized=False'in b)
ck('new exclusive BUILD02 stage claim and outer paths',"RUN='20261016_R2_ABB_CBIRRT_NR_BUILD02'"in b and "CLAIM='P4_R2_ABB_CBIRRT_NR_BUILD_2_45W_90CPU_20261016'"in b and
 "BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_cbirrt_nr_v2')"in b and "RUN='20261016_R2_ABB_CBIRRT_NR_BUILD02'"in s and "RUNNER=ROOT/'scripts/build_p4_full_r2_abb_cbirrt_nr_v2_draft.py'"in s)
ck('original failure exact execution protocol claim logs recipe raw d bound',all(q in b for q in('a6f84e38ecef47649d9dc12cf7316a9ebc68429e6b126bd6cc1b23e4845d8b4d','EXACT_ORIGINAL_BUILD01_DEPENDENCY_STOP_MUST_REMAIN','05621e65d40d89bccbacac84cdefd03aa9adc69fcede097545ced2dcd33e5538',"for filename in previous.parent.rglob('*')", "bind(failed['protocol'],failed['protocol_sha256'])", "bind(failed['claim'],failed['claim_sha256'])")))
ck('Make parser is byte-based no shlex eval make process','import shlex'not in b and 'eval('not in b and 'make_rule_tokens' in b and 'dependency_rules' in b and
 "target=[];deps=[];token=bytearray()"in b and 'UNEXPANDED_MAKE_VARIABLE_OR_UNQUOTED_DOLLAR'in b and 'UNSUPPORTED_OR_INCOMPLETE_GCC_MAKE_ESCAPE'in b)
ck('Make parser single target and nonempty prerequisites','MULTIPLE_UNESCAPED_MAKE_RULE_COLONS'in b and "flush();require(colon and len(target)==1 and deps"in b)
ck('raw dependency stdout exact LF final continuation and no skip','COMPLETE_NONEMPTY_DEPENDENCY_STDOUT_REQUIRED'in b and 'EXACT_LF_DEPENDENCY_PHYSICAL_LINES_REQUIRED'in b and
 "for line in raw.splitlines(keepends=True)"in b and 'if trailing%2:'in b and 'UNTERMINATED_CONTINUATION_OR_UNCOVERED_STDOUT'in b and "target,deps=make_rule_tokens(bytes(logical))"in b)
ck('exact6 original compiler rules source-first distinct and coverage once','EXACTLY_SIX_REAL_COMPILER_STDOUT_RULES_REQUIRED'in b and 'SIX_DISTINCT_FROZEN_TRANSLATION_UNITS_REQUIRED'in b and
 'EACH_ACTUAL_RULE_FIRST_DEPENDENCY_MUST_BE_DISTINCT_FROZEN_TU'in b and 'EXACT_COMPLETE_SIX_TU_COVERAGE_ONCE_REQUIRED'in b and 'source_occurrences==Counter({name:1 for name in expected})'in b)
ck('target actual binary exact repeated permitted','ACTUAL_GCC_DEPENDENCY_TARGET_MUST_BE_EXACT_BINARY'in b and "path(rule['target']).resolve()==BINARY.resolve()"in b and "source not in per_source"in b)
ck('all actual protected deps belong frozen or exact staged derivative','frozen.update({str((STAGE/name).resolve()):want'in b and "if protected_dependency(filename)and frozen.get(name)!=digest:missing.append(name)"in b and 'ACTUAL_PROTECTED_DEPENDENCY_NOT_IN_FROZEN_MANIFEST'in b)
ck('full raw stdout preserved SHA byte count and offsets','compiler_dependency_stdout_sha256'in b and 'compiler_dependency_stdout_bytes'in b and 'raw_stdout_offset_begin'in b and 'raw_stdout_offset_end'in b and 'raw_sha256=digest'in b)
ck('six slices are explicitly derived bytes never invented compiler files',"compiler_created_individual_d_file=False"in b and 'DERIVED_RAW_RULE_SLICE_MUST_BE_BYTE_EXACT'in b and
 "fragment=raw[rule['offset_begin']:rule['offset_end']]"in b and "with saved.open('xb')"in b and "derived_slice_sha256=digest"in b)
ck('raw and slices final SHA unchanged hard gates',"('compiler_dependency_files_sha256','compiler_dependency_files_after_sha256',STAGE)"in b and 'ORIGINAL_DEPENDENCY_STDOUT_CHANGED_AFTER_SLICING'in b and 'STAGED_ASSET_CHANGED'in b)
ck('compiler0 precedes dependency actual parse then build status',b.index("require(proc.returncode==0,'CBIRRT_NR_BUILD_FAILED')")<b.index("actual_dependencies(record,spec,[ROOT/DRIVER")<b.index("record['status']='BUILT_NOT_QUERIED'"))
ck('ELF hash retained even dependency STOP while success manifest stays gated',b.index("record.update(binary=str(BINARY),binary_sha256=sha(BINARY))")<b.index("actual_dependencies(record,spec,[ROOT/DRIVER")and "if record['status']=='BUILT_NOT_QUERIED':durable_new(BUILD/'manifest.json'"in b)
ck('existing45/90 original total unchanged no extra preprocessing probe',"wall_cap=min(45.,3600.-spec['previous_r2_wall_s'])"in b and "cpu_cap=min(90.,7200.-spec['previous_r2_cpu_s'])"in b and 'resource.setrlimit(resource.RLIMIT_CPU,(90,90))'in b and "'-M'"not in b and "'-E'"not in b and "'-###'"not in b)
# Same supervisor operations and exact source other than version identities.
ns=ast.parse(s);os=ast.parse(raw('scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_draft.py'))
for t in(ns,os):
 for v in ast.walk(t):
  if isinstance(v,ast.Constant)and isinstance(v.value,str):v.value=v.value.replace('20261016_R2_ABB_CBIRRT_NR_BUILD02','20261016_R2_ABB_CBIRRT_NR_BUILD01').replace('build_p4_full_r2_abb_cbirrt_nr_v2_draft.py','build_p4_full_r2_abb_cbirrt_nr_draft.py').replace('ENGINEERING_EXTERNAL_COST_CHARGE_V2','ENGINEERING_EXTERNAL_COST_CHARGE_V1')
ck('full supervisor AST same except new version identities',norm(ns)==norm(os))
ck('exclusive outer FD external whole-child cap and actual parent proof retained','os.O_WRONLY|os.O_CREAT|os.O_EXCL'in s and 'pass_fds=(fd,)'in s and 'proc.wait()'in s and 'identity_unchanged'in s and "wall<=min(45.,3600.-spec['previous_r2_wall_s'])"in s and 'ACTUAL_GNU_TIME_PARENT_REQUIRED'in b)
ck('actual cleanup ordered timer kill wait reap finalgroup unchanged from STOP bytes',all(q in b for q in("signal.setitimer(signal.ITIMER_REAL,0)","try:os.killpg(proc.pid,signal.SIGKILL)","proc.wait(timeout=2.)","record['compiler_reaped']=True","record['compiler_group_members_after_cleanup']=compiler_group_members(proc.pid)",'ACTUAL_COMPILER_GROUP_NOT_EMPTY_AFTER_KILL_WAIT')))
ck('PRE names engineering error original failure no scientific change actual future gate',all(q in p for q in('责任属于我们的工程实现及静态审查','这些只读源码依据支持本恢复设计','原 211','974/974','0/22500','真实工程通过仍须人员独立POST')))
prior=read('results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V19.json')
ck('actual V19 stopped engineering charged once37=29science8engineering',prior['count']==37 and prior['science_count']==29 and prior['engineering_count']==8 and len(prior['executions'])==37)
actual={str(q.relative_to(ROOT)):hashlib.sha256(raw(q)).hexdigest()for q in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')}
ck('actual all37 execution identities exact V19',actual=={r['execution']:r['execution_sha256']for r in prior['executions']})
stop=read('reports/P4_FULL_R2_ABB_CBIRRT_NR_BUILD_ROOT_INDEPENDENT_POST_20261016.json')
ck('genuine failed cost qualification not build qualification',stop['status']=='STOP_BUILD_DEPENDENCY_EVIDENCE_INCOMPLETE'and stop['external_supervision_qualified']is True and stop['engineering_build_qualified']is False and stop['upper_wall_s']==33.96 and stop['upper_cpu_s']==55.48)
ck('V19 current totals exact fsum45/90 headroom',all(math.fsum(r.get('charged_'+k,r[k])for r in prior['executions'])==prior['conservative_r2_sum_'+k]for k in('wall_s','cpu_s'))and prior['r2_remaining']['wall_s']>=45 and prior['r2_remaining']['cpu_s']>=90)
ck('new run claim stage not executed',not(ROOT/'results/p4_full/20261016_R2_ABB_CBIRRT_NR_BUILD02').exists()and not(ROOT/'results/p4_full/P4_R2_ABB_CBIRRT_NR_BUILD_2_45W_90CPU_20261016.claim.json').exists()and not Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_cbirrt_nr_v2').exists())
ck('VI exhausted formal full scope retained',prior['vi_B_candidate_cap']==974 and prior['vi_B_remaining']['candidate_constructions']==0 and prior['formal_table_I_calls']==0 and prior['formal_table_I_required_calls']==22500)
for n,w in list(retained.items()):ck('read input unchanged '+n,hashlib.sha256(Path(n).read_bytes()).hexdigest()==w)
failed=[v for v in checks if not v['passed']]
report=dict(schema='P4_CBIRRT_NR_BUILD02_INDEPENDENT_STATIC_REVIEW_V1',status='PASS_BUILD02_EXPLICIT_STDOUT_DEPENDENCY_STATIC_REVIEW'if not failed else'FAIL_BUILD02_STATIC_REVIEW',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of new engineering implementation',personnel_independent=True,checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,reviewed_source_sha256=EXPECTED,retained_sha256=retained,new_runner_model_parser_import_execute_compile_binary_science_protocol_prior_claim_calls=0,new_engineering_run_executed=False,engineering_build_qualified=False,actual_future_dependency_transport_unverified=True,official_sources=[dict(url='https://gcc.gnu.org/onlinedocs/gcc-11.1.0/gcc/Preprocessor-Options.html',support='MF minus selects stdout; MD emits actual compile dependencies without preprocessing-only mode.'),dict(url='https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-11.1.0/gcc/c-family/c-opts.c',support='c_common_finish selects stdout for dash dependency output and writes dependencies even on compilation errors.'),dict(url='https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-11.1.0/libcpp/mkdeps.c',support='deps_write emits Make rule with wrapped physical lines.')],limitations=['Static/AST and saved actual V19 evidence only. No invocation of builder/parser/describe/compiler/binary. Root must freeze exact current protocol/commit and uniquely run; actual six complete raw rules and successful compiler/reap/hash/cost remain mandatory.','Prior V4 default-dependency-name inference was disproved by BUILD01. Original failure, recipes, .d, binary and reports retained; unchanged scientific transform/body evidence remains distinct from invalidated dependency assumption.','No new OS closure/scientific design/threshold/sample/formal planning; original211 obligations VI974余0 formal0/22500 remain.'])
with OUT.with_suffix('.json').open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
with OUT.with_suffix('.md').open('x')as f:f.write('# CBiRRT_NR BUILD02 工程独立静态审查\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(len(checks))+'。三新稿固定SHA，原六稿与科学源字节保持；命令唯一依赖I/O差分为-MF -。\n\n[GCC11专门预处理规则](https://gcc.gnu.org/onlinedocs/gcc-11.1.0/gcc/Preprocessor-Options.html)及[c-opts实现](https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-11.1.0/gcc/c-family/c-opts.c)支持stdout设计，但不替代下次真实唯一编译。六完整Make原规则/首TU身份/全受管SHA/完整raw及派生切片、实际compiler退出/组空/外层费用均仍是执行后门。\n\n原BUILD01 STOP不变；新v2未构建、未查询。人员独立只读AST/实际V19；0runner/parser import或执行、0compile/binary/science/protocol/prior/claim。211义务、VI974余0、formal0/22500保留。\n')
print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),failures=failed),ensure_ascii=False))
if failed:raise SystemExit(2)
