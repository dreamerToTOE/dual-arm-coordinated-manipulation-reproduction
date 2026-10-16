#!/usr/bin/env python3
"""Preserved V1 source/AST review only. No runner import or process execution."""
from pathlib import Path
from collections import Counter
import ast
import datetime
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
SNAP=ROOT/'reports/p4_full_audit/recovery_tools/cbirrt_nr_reviewed_v1_snapshot'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_NR_ENGINEERING_INDEPENDENT_STATIC_REVIEW_V1_20261016'
checks=[];bound={}
def ck(n,ok):checks.append(dict(check=n,passed=bool(ok)))
def read(n):
    p=Path(n);p=p if p.is_absolute()else ROOT/p
    b=p.read_bytes();bound[str(p)]=hashlib.sha256(b).hexdigest();return b
def load(n):return json.loads(read(n))
manifest=load(SNAP/'manifest.json')
blobs={n:read(SNAP/n)for n in manifest['sha256']}
for n,b in blobs.items():ck('preserved V1 stable SHA '+n,hashlib.sha256(b).hexdigest()==manifest['sha256'][n])
b=blobs['scripts/build_p4_full_r2_abb_cbirrt_nr_draft.py'].decode()
s=blobs['scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_draft.py'].decode()
t=blobs['baselines/p4_full/geometry_consistent/abb_cbirrt_nr_instrumentation_draft.py'].decode()
h=blobs['baselines/p4_full/geometry_consistent/abb_cbirrt_nr_observation_draft.hpp'].decode()
d=blobs['baselines/p4_full/geometry_consistent/abb_cbirrt_nr_driver_draft.cpp'].decode()
for n,x in blobs.items():
    if n.endswith('.py'):ast.parse(x,filename=n)
ck('three Python files parse without importing or compiling',True)
ck('one new target no binary/query/solve execution granted','targets=1'in b and 'binary_execution_calls=0'in b and
   'scientific_execution_authorized=False'in b and b.count('proc=subprocess.Popen(')==1)
ck('fresh external stage and exclusive claim run','not BUILD.exists()and not folder.exists()and not claim.exists()'in b and
   "with Path(filename).open('xb')"in b and 'EXISTING_TIMER_REFUSE_REPLACE'in b)
ck('same existing qualified numerical GD seam only',"GD_SEAM='\\n return p4nr_iface::physical_gd(q_init_flip,T_pose[0][3],L,include_joint_limits,q_solution,IK_counter,IK_time);\\n'"in t and
   "if restored!=original:raise ValueError('WHOLE_FILES_NOT_BYTE_REVERSIBLE')"in t)
ck('original full distance body retained and no PCS branch role design',"wrap(HDR,'double distanceFunction"in t and
   'si_->distance'in read('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning/planners/CBiRRT_NR.h').decode() and
   'H_or_D_correction_present=False'in t and 'active_role_or_analytic_branch=False'in t)
ck('complete original function bodies kept once in returning lambdas',"if inserted.count(body)!=1:raise ValueError('COMPLETE_ORIGINAL_BODY_ONCE_REQUIRED')"in t and
   "if text[a:b]!=inserted:raise ValueError('INVERSE_WRAPPER_BODY_MISMATCH')"in t)
ck('observer has no new scientific evaluation or RNG call',not any(x in h for x in ('physical_gd(', 'project_nr(', 'collision_state(', 'checkMotionRBS(', 'rand(', 'sampleUniform(')))
ck('single future fixed original request and main sampler bounds',d.count('planner->solve(')==1 and
   'ompl::RNG::setSeed(7);std::srand(7);'in d and 'arm_low={-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416}'in d and
   'si->setStateValidityCheckingResolution(.1)'in d)
ck('setup and original solve cout redirected within scope','{Redirect quiet;planner->setProblemDefinition(problem);planner->setup();}'in d and
   '{Redirect quiet;const auto status=planner->solve('in d)
ck('fresh output only and original temp retained',"RETAIN_TEMP_IO_ONLY"in t and
   'if(fs::exists("paths")||!fs::create_directory("paths"))'in d)
ck('current all-date charged prior and independent replacement certificates',"glob('*_R2_*/execution.json')"in b and
   "r.get('charged_wall_s',r['wall_s'])"in b and 'PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED'in b and
   'ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING'in b)
ledger=load('results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V18.json')
ck('V18 actual36 charged history and exhausted VI formal0 preserved',ledger['count']==36 and
   ledger['conservative_r2_sum_wall_s']==685.555705375994 and ledger['conservative_r2_sum_cpu_s']==542.4289229999999 and
   ledger['vi_B_remaining']['candidate_constructions']==0 and ledger['formal_table_I_calls']==0 and ledger['formal_table_I_required_calls']==22500)
ck('45wall90CPU remain inside3600/7200 total cap',"wall_cap=min(45.,3600.-spec['previous_r2_wall_s'])"in b and
   "cpu_cap=min(90.,7200.-spec['previous_r2_cpu_s'])"in b)
ck('compiler registration masks alarm and group CPU counted','signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})'in b and
   'start_new_session=True,preexec_fn=limits'in b and 'lifecycle.live_group_cpu(proc.pid)'in b and 'resource.RLIMIT_CPU,(90,90)'in b)
ck('exclusive outer GNUtime FD full child lifetime plus decimal upper','os.O_WRONLY|os.O_CREAT|os.O_EXCL'in s and
   'pass_fds=(fd,)'in s and "wall=float(elapsed+Decimal('.01'));cpu=float(user+system+Decimal('.02'))"in s and
   'Supervisor own journal/fsync cost excluded.'in s and 'independent_POST_required=True'in s)
ck('actual parent GNUtime argv inode proof before new claim','ACTUAL_GNU_TIME_PARENT_REQUIRED'in b and
   'EXACT_TIME_SOURCE_PROTOCOL_ARGV_REQUIRED'in b and 'EXCLUSIVE_SUPERVISION_INODE_REQUIRED'in b)
ck('all new linked libraries and OMPL KDL transitive headers bound before compile',False)
ck('actual compiler group after kill and reap empty required before success',False)
failures=[r for r in checks if not r['passed']]
report=dict(schema='P4_CBIRRT_NR_ENGINEERING_INDEPENDENT_STATIC_REVIEW_V1',status='FAIL_V1_ENGINEERING_ASSET_AND_GROUP_GATES',
   generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of implementation',
   personnel_independent=True,checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),failures=failures,checks=checks,
   reviewed_source_sha256=manifest['sha256'],preserved_V1_source_root=str(SNAP.relative_to(ROOT)),retained_sha256=bound,
   blockers=[dict(id='LINK_AND_TRANSITIVE_ASSET_BINDINGS',evidence='V1 assets() inherits RRT_NR assets(), not CBiD template_assets(); actual command links four Boost shared libraries with no explicit binding. NR_LOCAL bound1203 and NR_INTERFACE template457 contain no libboost or OMPL/KDL header paths; Q1 library_headers379 are Eigen+nlohmann+compiler. New CBiNR direct/transitive OMPL/KDL/PQP headers and selected link libraries need concrete SHA binding.',
       repair='Bind actual selected Boost/KDL/OMPL/PQP artifacts and concrete transitive header closure before freeze and after compilation; preserve previous V1 bytes.'),
       dict(id='FINAL_COMPILER_GROUP_EMPTY',evidence='V1 finally records compiler_group_members_before_cleanup and kills group, then waits direct g++; no actual after-group scan or require(empty). A failed build can orphan compiler descendants; GNUtime covers only reaped descendant CPU and cannot by itself prove final group empty.',
       repair='Save real compiler-group snapshots after wait/reap; kill residual group as needed, enforce empty group with bounded observation or retain STOP. State orphan CPU uncertainty explicitly if failure prevents complete accounting.')],
   new_scientific_calls=0,runner_model_import_calls=0,CXX_compile_calls=0,binary_execution_calls=0,protocol_generation_calls=0,prior_generation_calls=0,claims_created=0,
   engineering_execution_permitted_by_this_report=False,limits=['V1 failed static review only; no science or build executed. Author/root may perform routine versioned engineering repair and seek V2 static review.','No original CBiNR numerical or paper theory failure inferred. Original physical GD seam remains RECONSTRUCTED.'])
with OUT.with_suffix('.json').open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
with OUT.with_suffix('.md').open('x')as f:f.write('# CBiRRT_NR 工程 V1 独立静态审查\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(len(checks))+'，两项工程缺口。\n\n'+
   '实际链接Boost与新增OMPL/KDL等传递头缺少完整冻结SHA绑定；compiler kill/wait后缺实际组为空快照和硬门。原数值/控制流不据此判错。六稿原字节已独立保全，后续常规V2修复另审。\n\n'+
   '零科学、编译、binary、runner/model import、协议/prior/claim。此报告不许可工程执行。\n')
print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failures)),ensure_ascii=False))
