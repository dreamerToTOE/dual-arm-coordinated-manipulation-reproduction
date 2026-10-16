#!/usr/bin/env python3
"""Independent static AST/byte and saved-prior review; never import builder.

Pure memory reconstruction below is an independent restricted AST literal
reader and string transform, not execution/import of the implementation.
"""
from pathlib import Path
from collections import Counter
import argparse
import ast
import datetime
import hashlib
import json
import math
import re

ROOT=Path(__file__).resolve().parents[3]
TEMPLATE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1/geometry_consistent_plain')
AUTHOR=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning')
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_NR_ENGINEERING_INDEPENDENT_STATIC_REVIEW_V2_20261016'
BUILDER='scripts/build_p4_full_r2_abb_cbirrt_nr_draft.py'
SUPER='scripts/supervise_p4_full_r2_abb_cbirrt_nr_build_draft.py'
TRANSFORM='baselines/p4_full/geometry_consistent/abb_cbirrt_nr_instrumentation_draft.py'
OBSERVER='baselines/p4_full/geometry_consistent/abb_cbirrt_nr_observation_draft.hpp'
DRIVER='baselines/p4_full/geometry_consistent/abb_cbirrt_nr_driver_draft.cpp'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_NR_ENGINEERING_PRE_DRAFT_20261016.md'
EXPECTED={SUPER:'a979515b29cfcca934d28a6b83723a62424b9684d1190c29d20a95d8a4ba9b33',
   TRANSFORM:'07f5632ca92843b0be96ebece15cc8a64060768cdf4dc466242e176505a04c3e',
   OBSERVER:'74917caa8fab59821776617b44c119f57762153135e0c773bbc22dd180b190e4',
   DRIVER:'65c95cdb2fe09e916a9f564baf01906901d80e136ccb48014c8ce9633b1bf0e7'}
checks=[];retained={}
def ck(n,ok):checks.append(dict(check=n,passed=bool(ok)))
def raw(n):
    p=Path(n);p=p if p.is_absolute()else ROOT/p
    b=p.read_bytes();retained[str(p)]=hashlib.sha256(b).hexdigest();return b
def read(n):return json.loads(raw(n))
def digest(b):return hashlib.sha256(b).hexdigest()
def func(tree,name):return next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
def plain_ast(node):return ast.dump(node,include_attributes=False)
def body_span(text,signature):
    if text.count(signature)!=1:raise ValueError('INDEPENDENT_SINGLE_CPP_SIGNATURE '+signature)
    masked=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',lambda m:' '*len(m.group()),text,flags=re.S)
    left=masked.index('{',text.index(signature))+1;at=left;depth=1
    while depth:
        depth+=(masked[at]=='{')-(masked[at]=='}');at+=1
    return left,at-1
def json_cpp(fields):return 'p4cbnr::json{'+','.join('{"'+k+'",'+v+'}'for k,v in fields)+'}'
def literal(node,names):
    if isinstance(node,ast.Constant):return node.value
    if isinstance(node,ast.Name):return names[node.id]
    if isinstance(node,ast.List):return[literal(v,names)for v in node.elts]
    if isinstance(node,ast.Tuple):return tuple(literal(v,names)for v in node.elts)
    if isinstance(node,ast.Call)and isinstance(node.func,ast.Name)and node.func.id=='J':return json_cpp(literal(node.args[0],names))
    raise ValueError('NONLITERAL_IMPLEMENTATION_AST_NOT_EXECUTED '+ast.dump(node))

def independent_reconstruction(transform_tree,preview):
    names={}
    for n in transform_tree.body:
        if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and isinstance(n.value,ast.Constant):names[n.targets[0].id]=n.value.value
    fn=func(transform_tree,'instrument_sources');wraps=[]
    for n in fn.body:
        if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in('state_args','pre'):
            names[n.targets[0].id]=literal(n.value,names)
        if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='wrap':
            vals=[literal(v,names)for v in n.value.args]
            kw={k.arg:literal(k.value,names)for k in n.value.keywords}
            wraps.append((*vals[:6],kw.get('pre',vals[6]if len(vals)>6 else'')))
    files=[names[k]for k in('KDL','SVC','COL','CBI','HDR')]
    original={n:raw(TEMPLATE/n)for n in files}
    for n,blob in original.items():
        ck('original template/author bytes '+n,blob==raw(AUTHOR/n)and digest(blob)==preview['original_sha256'][n])
    current={n:v.decode()for n,v in original.items()};inverse=[]
    kdl,gd,seam=names['KDL'],names['GD'],names['GD_SEAM']
    a,z=body_span(current[kdl],gd);oldgd=current[kdl][a:z]
    current[kdl]=current[kdl][:a]+seam+current[kdl][z:]
    ck('same qualified GD seam exact call only',seam=='\n return p4nr_iface::physical_gd(q_init_flip,T_pose[0][3],L,include_joint_limits,q_solution,IK_counter,IK_time);\n')
    ck('exact13 complete function wrappers',len(wraps)==13)
    for fields in wraps:
        file,signature,kind,result,args,returns,*tail=fields
        pre=tail[-1]if tail else''
        a,z=body_span(current[file],signature);body=current[file][a:z]
        lead='\n const auto p4_id=p4cbnr::enabled ? p4cbnr::enter("'+kind+'",'+args+') : 0;\n'+pre
        if result=='void':inserted=lead+' [&]() -> void {'+body+'}();\n if(p4cbnr::enabled)p4cbnr::leave(p4_id,"'+kind+'",'+returns+');\n'
        else:inserted=lead+' '+result+' p4_return=[&]() -> '+result+' {'+body+'}();\n if(p4cbnr::enabled)p4cbnr::leave(p4_id,"'+kind+'",'+returns+');\n return p4_return;\n'
        ck('complete source or existing-seam body once '+kind,inserted.count(body)==1 and
           any(r.get('signature')==signature and r.get('body_sha256')==digest(body.encode())for r in preview['changes']))
        inverse.append((file,signature,inserted,body));current[file]=current[file][:a]+inserted+current[file][z:]
    needle='std::remove("./paths/temp.txt");';replacement='/* P4 CBiNR I/O observation: retain ./paths/temp.txt verbatim. */'
    ck('only original unique temp deletion anchor',current[names['CBI']].count(needle)==1)
    current[names['CBI']]=current[names['CBI']].replace(needle,replacement)
    staged={n:digest(v.encode())for n,v in current.items()}
    ck('independent memory reconstruction equals all5 actual staged preview hashes',staged==preview['staged_sha256'])
    restored=dict(current);restored[names['CBI']]=restored[names['CBI']].replace(replacement,needle)
    for file,signature,inserted,body in reversed(inverse):
        a,z=body_span(restored[file],signature)
        ck('inverse entire body exact '+signature,restored[file][a:z]==inserted)
        restored[file]=restored[file][:a]+body+restored[file][z:]
    a,z=body_span(restored[kdl],gd);restored[kdl]=restored[kdl][:a]+oldgd+restored[kdl][z:]
    ck('independent inverse restores all original bytes including CRLF',{n:v.encode()for n,v in restored.items()}==original)
    return staged,[w[2]for w in wraps]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--builder-sha256',required=True);ap.add_argument('--pre-sha256',required=True);a=ap.parse_args()
    expected={**EXPECTED,BUILDER:a.builder_sha256,PRE:a.pre_sha256}
    blobs={n:raw(n)for n in expected}
    for n,want in expected.items():ck('stable reviewed SHA '+n,digest(blobs[n])==want)
    b,s,t,h,d,pre=(blobs[n].decode()for n in(BUILDER,SUPER,TRANSFORM,OBSERVER,DRIVER,PRE))
    bt,st,tt=(ast.parse(v,filename=n)for v,n in((b,BUILDER),(s,SUPER),(t,TRANSFORM)))
    ck('all three Python sources AST parse without importing compiling or describing',True)
    v1=ROOT/'reports/p4_full_audit/recovery_tools/cbirrt_nr_reviewed_v1_snapshot'
    oldb=ast.parse(raw(v1/BUILDER));olds=raw(v1/SUPER)
    ck('V1 failed report and all six original bytes remain',read('reports/P4_FULL_R2_ABB_CBIRRT_NR_ENGINEERING_INDEPENDENT_STATIC_REVIEW_V1_20261016.json')['checks_failed']==2 and
       all(digest(raw(v1/n))==want for n,want in read(v1/'manifest.json')['sha256'].items()))
    ck('supervisor and transform observer driver unchanged V1',blobs[SUPER]==olds and all(blobs[n]==raw(v1/n)for n in(TRANSFORM,OBSERVER,DRIVER)))
    preview=read('work/cbirrt_nr_static_previews_20261016/source_transform_preview.json')
    staged,kinds=independent_reconstruction(tt,preview)
    nr_manifest=read('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_nr_interface_v1/manifest.json')
    rrt_manifest=read('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_nr_e2e_v1/manifest.json')
    for name in ('baselines/p4_full/geometry_consistent/abb_nr_interface_kernel_draft.cpp',
                 'baselines/p4_full/geometry_consistent/physical_nr_abb_cpp_draft.hpp',
                 'baselines/p4_full/geometry_consistent/abb_nr_interface_observation_draft.hpp'):
        ck('immutable previously built qualified GD asset '+name,digest(raw(name))==nr_manifest['own_source_sha256'][name]==rrt_manifest['own_source_sha256'][name])
    ck('previous interface and RRT_NR engineering manifests actual successful',nr_manifest['status']==rrt_manifest['status']=='BUILT_NOT_QUERIED'and
       nr_manifest['exit_code']==rrt_manifest['exit_code']==0)
    ck('preview no added role branch H D or observer scientific work',preview['full12_distance_original']is True and
       preview['active_role_or_analytic_branch']is preview['H_or_D_correction_present']is False and
       preview['observer_model_calls']==preview['observer_RNG_draws']==0 and preview['whole_files_byte_reversible']is True)
    originalh=raw(AUTHOR/'planners/CBiRRT_NR.h').decode();originalc=raw(AUTHOR/'planners/CBiRRT_NR.cpp').decode()
    left,right=body_span(originalh,'double distanceFunction(const Motion *a, const Motion *b) const')
    ck('original full12 NN only si distance preserved',originalh[left:right].strip()=='return si_->distance(a->state, b->state);')
    ck('original two grow modes iteration limits and true connection retained','growTree(tree, tgi, nmotion, tmotion, rmotion, 1, 100)'in originalc and
       'growTree(otherTree, tgi, nmotion, reached_motion, rmotion, 2, 500)'in originalc and
       'connectionPoint_ = std::make_pair(startMotion->state, goalMotion->state);'in originalc)
    ck('observer no model FK IK NR collision RBS or RNG calls',not any(x in h for x in('physical_gd(','project_nr(','collision_state(','checkMotionRBS(','sampleUniform(','rand(')))
    ck('identity remains actual Motion state no q merge','inline unsigned long identity(const void* value)'in h and
       'std::map<const void*,unsigned long> identities'in h and 'state_to_motion.at(m->root)'in d and 'equal q never merged'in d)
    solve_left,solve_right=body_span(originalc,'ompl::base::PlannerStatus ompl::geometric::CBiRRT::solve(const base::PlannerTerminationCondition &ptc)')
    grow_left,grow_right=body_span(originalc,'ompl::geometric::CBiRRT::Motion* ompl::geometric::CBiRRT::growTree(TreeData &tree, TreeGrowingInfo &tgi, Motion *nmotion, Motion *tmotion, Motion *rmotion, int mode, int count_iterations)')
    solve_body=originalc[solve_left:solve_right];grow_body=originalc[grow_left:grow_right]
    ck('original tree motions not deleted before snapshot',originalc.count('delete motions[i];')==2 and
       'delete motions['not in solve_body and 'freeMemory()'not in solve_body and 'tree->remove('not in solve_body and
       'delete 'not in grow_body and 'delete tmotion;'in solve_body and 'delete rmotion;'in solve_body)
    ck('future thin driver single fixed solve and original full12 main sampler','FROZEN_II_SEED7_RANGE26_SOLVE10_REQUIRED'in d and
       d.count('planner->solve(')==1 and 'arm_low={-2.88,-1.919,-1.919,-2.79,-2.09,-3.1416}'in d and
       'arm_high={2.88,1.919,1.22,2.79,2.09,3.1416}'in d and 'si->setStateValidityCheckingResolution(.1)'in d and
       'si->setStateValidityChecker([](const ob::State*){return true;})'in d)
    ck('seed once before every OMPL object and simplification absent',d.count('ompl::RNG::setSeed(7)')==d.count('std::srand(7)')==1 and
       d.index('ompl::RNG::setSeed(7)')<d.index('auto space=') and 'solution_path_simplification' in d and 'simplifySolution('not in d)
    ck('all constructor setup solve getPlannerData stdout scoped to stderr','{Redirect quiet;si->setup();planner=std::make_unique<Probe>(si);}'in d and
       '{Redirect quiet;planner->setProblemDefinition(problem);planner->setup();}'in d and
       '{Redirect quiet;const auto status=planner->solve('in d and '{Redirect quiet;planner->getPlannerData(data);}'in d)
    ck('one request original future stdin close obligation explicit','while(std::getline(std::cin,extra))'in d and
       'EXACTLY_ONE_REQUEST_REQUIRED'in d and 'FRESH_ABSENT_PATHS_REQUIRED'in d and d.count('std::cout<<out.dump()')==1)
    ck('new exclusive one target zero binary/query/solve scientific execution','targets=1'in b and
       'query_calls=0,solve_calls=0,binary_execution_calls=0'in b and 'scientific_execution_authorized=False'in b and
       b.count('proc=subprocess.Popen(')==1 and "RUN='20261016_R2_ABB_CBIRRT_NR_BUILD01'"in b)
    ck('compiler command preserves four cpp kernel and optimization only adds MD',"LINKED=(KDL,SVC,COL,CBI)"in b and
       "command=[str(COMPILER),'-MD','-std=c++17','-O1','-g0','-Wall','-Wextra','-pthread'"in b and
       "'-include',str(ROOT/HEADER),str(ROOT/DRIVER),str(ROOT/KERNEL),*[str(p)for p in sources]"in b and
       "'-lompl','-lorocos-kdl','-lboost_filesystem','-lboost_system','-lboost_serialization','-lboost_program_options'"in b)
    ck('no extra compiler preprocessing inspection or binary execution','-E'not in ast.unparse(func(bt,'build')) and
       "'-M'"not in b and "'-MM'"not in b and "'-dumpspecs'"not in b and "'-###'"not in b)
    ck('actual linked four Boost libraries match existing -L search order',"for name in('filesystem','system','serialization','program_options')"in b and
       "choices=[Path('/opt/ros/humble/lib/x86_64-linux-gnu')"in b and "Path('/usr/lib/x86_64-linux-gnu')"in b and
       'ACTUAL_LINKED_BOOST_LIBRARY_REQUIRED'in b and 'bind(selected);bind(selected.resolve())'in b)
    selected_boost={}
    for name in ('filesystem','system','serialization','program_options'):
        options=[Path('/opt/ros/humble/lib/x86_64-linux-gnu')/('libboost_'+name+'.so'),Path('/usr/lib/x86_64-linux-gnu')/('libboost_'+name+'.so')]
        selected=next((p for p in options if p.is_file()),None)
        ck('actual linked selected Boost exists '+name,selected is not None)
        if selected is not None:
            selected_boost[name]=dict(selected=str(selected),resolved=str(selected.resolve()),sha256=digest(raw(selected)))
            ck('actual selected Boost resolves same content '+name,digest(raw(selected.resolve()))==selected_boost[name]['sha256'])
    ck('OMPL KDL full namespaces related Boost closure no whole OS binding',"OMPL_HEADERS=Path('/opt/ros/humble/include/ompl-1.7/ompl')"in b and
       "KDL_HEADERS=Path('/usr/include/kdl')"in b and "for root in(OMPL_HEADERS,KDL_HEADERS)"in b and
       'files.update(added_header_assets(files))'in b and "Path('/usr/include').rglob"not in b and 'BOOST_MACRO_SUPPORT'in b)
    ck('actual single compilation six perTU default MD artifacts cannot overwrite',"BINARY.name+'-'+p.stem+'.d'"in b and
       'ONE_COMPLETE_MD_FILE_PER_TRANSLATION_UNIT_REQUIRED'in b and "'-MF'"not in b and
       'actual_dependencies(record,spec,[ROOT/DRIVER,ROOT/KERNEL,*sources])'in b)
    ck('every dep file binds its own source all dependency hashes saved','MD_FILE_MUST_BIND_ITS_ACTUAL_TRANSLATION_UNIT'in b and
       "record['actual_dependency_translation_units']=per_source"in b and "record['actual_dependencies_sha256']=dependencies"in b)
    ck('protected actual dependency must belong frozen source or exact staged derivative','frozen.update({str((STAGE/name).resolve()):want' in b and
       "protected_dependency(filename)and frozen.get(str(filename))!=digest"in b and
       'ACTUAL_PROTECTED_DEPENDENCY_NOT_IN_FROZEN_MANIFEST'in b)
    ck('generic OS headers recorded not extra closed-world scientific gate','generic libc/libstdc++/OS headers use frozen compiler and OS fingerprint'in b and
       "environment_fingerprint=dict(uname=list(os.uname()),os_release_sha256=sha('/etc/os-release'))"in b and
       'COMPILER_OS_FINGERPRINT_CHANGED'in b)
    ck('all added header namespace set SHA checked again finally','ADDED_HEADER_NAMESPACE_SET_OR_SHA_CHANGED'in b and
       "record['added_header_assets_after_sha256']=header_after"in b)
    ck('source transform original5 preserved and new hash all before after','EXACT_STAGED_SOURCE_PREVIEW_REQUIRED'in b and
       "STAGE/'preserved_originals'/name"in b and 'compiled_source_after_sha256'in b and 'mesh_after_sha256'in b and
       'preserved_source_after_sha256'in b and 'STAGED_ASSET_CHANGED'in b)
    ck('compiler tools existing libraries inherited kernel chain bound','files=reused.assets()'in b and
       "'compiled_source_sha256','mesh_sha256'"in b and "('protocol','protocol_sha256'),('claim','claim_sha256'),('binary','binary_sha256')"in b and
       '/usr/lib/gcc/x86_64-linux-gnu/11/cc1plus'in b and '/usr/bin/x86_64-linux-gnu-ld.bfd'in b)
    ck('frozen current all-date actual ledger and charged upper replacement hard gate',plain_ast(func(bt,'current_prior'))==plain_ast(func(oldb,'current_prior')) and
       "glob('*_R2_*/execution.json')"in b and 'PRIOR_ONE_EXTERNAL_REPLACEMENT_CERTIFICATE_REQUIRED'in b and
       'ORPHAN_SUPERVISED_ATTEMPT_REQUIRES_ACCOUNTING'in b)
    ck('45/90 budget remains within original3600/7200',"wall_cap=min(45.,3600.-spec['previous_r2_wall_s'])"in b and
       "cpu_cap=min(90.,7200.-spec['previous_r2_cpu_s'])"in b and "resource.setrlimit(resource.RLIMIT_CPU,(90,90))"in b)
    ck('SIGALRM cannot interrupt compiler fork registration','signal.pthread_sigmask(signal.SIG_BLOCK,{signal.SIGALRM})'in b and
       'start_new_session=True,preexec_fn=limits'in b and "record['compiler_pid']=proc.pid"in b and
       'lifecycle.live_group_cpu(proc.pid)'in b)
    ck('compiler cleanup turns timer off before kill reaps then actual group-empty gate','signal.setitimer(signal.ITIMER_REAL,0)'in b and
       'if members:os.killpg(proc.pid,signal.SIGKILL)'in b and "record['compiler_reaped']=True"in b and
       "record['compiler_group_members_after_cleanup']=compiler_group_members(proc.pid)"in b and
       'ACTUAL_COMPILER_GROUP_NOT_EMPTY_AFTER_KILL_WAIT'in b)
    ck('failure cleanup evidence caps cannot yield builder success',"if diagnostics:record['status']='STOP_CLEANUP_OR_EVIDENCE_ERROR'"in b and
       "record['status']='STOP_FINAL_WALL_OR_CPU_BUDGET'"in b and "record.get('terminal_receipt_status')=='BUILT_NOT_QUERIED'"in b)
    ck('fresh claim run stage protocol committed source and no active timer','EXCLUSIVE_FRESH_CBIRRT_NR_STAGE_RUN_CLAIM_REQUIRED'in b and
       'OTHER_ACTIVE_P4_EXECUTION'in b and 'EXISTING_TIMER_REFUSE_REPLACE'in b and
       "subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)==path(name).read_bytes()"in b)
    ck('actual GNUtime parent binary exact argv FD inode proof before claim',plain_ast(func(bt,'supervisor_proof'))==plain_ast(func(oldb,'supervisor_proof')) and
       'ACTUAL_GNU_TIME_PARENT_REQUIRED'in b and 'EXACT_TIME_SOURCE_PROTOCOL_ARGV_REQUIRED'in b and 'EXCLUSIVE_SUPERVISION_INODE_REQUIRED'in b)
    ck('outer source no builder import one process no retry','import build_'not in s and s.count('subprocess.Popen(')==1 and
       'OLD_SUPERVISION_ARTIFACT_NO_RETRY'in s and 'proc.wait()'in s)
    ck('O_EXCL heldFD actual inode immutable whole-child GNUtime boundary','os.O_WRONLY|os.O_CREAT|os.O_EXCL'in s and 'pass_fds=(fd,)'in s and
       'builder+compiler and all reaped compiler descendants'in s and 'identity_unchanged'in s)
    ck('full child import preflight cleanup execution receipt exit externally measured',"receipt=prefix/'cost_receipt.json'"in s and
       "wall=float(elapsed+Decimal('.01'));cpu=float(user+system+Decimal('.02'))"in s and
       "wall<=min(45.,3600.-spec['previous_r2_wall_s'])"in s and "cpu<=min(90.,7200.-spec['previous_r2_cpu_s'])"in s)
    ck('external certification not self-granted tail boundary explicit','Supervisor own journal/fsync cost excluded.'in s and
       'external_supervision_qualified=False,independent_POST_required=True'in s and
       'UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED'in b)
    ledger=read('results/p4_full/20261016_RECOVERY_ACTUAL_LEDGER_V18.json')
    ck('latest V18 actual36 charged previous scope',ledger['count']==36 and ledger['science_count']==29 and ledger['engineering_count']==7 and
       ledger['conservative_r2_sum_wall_s']==685.555705375994 and ledger['conservative_r2_sum_cpu_s']==542.4289229999999)
    actual={str(p.relative_to(ROOT)):digest(raw(p))for p in(ROOT/'results/p4_full').glob('*_R2_*/execution.json')}
    ck('all actual36 execution identities ledger exact',actual=={r['execution']:r['execution_sha256']for r in ledger['executions']})
    ck('prior cost fsum exact and has45/90 headroom',all(math.fsum(r.get('charged_'+k,r[k])for r in ledger['executions'])==ledger['conservative_r2_sum_'+k]for k in('wall_s','cpu_s'))and
       ledger['r2_remaining']['wall_s']>=45 and ledger['r2_remaining']['cpu_s']>=90)
    ck('VI974 exhausted formal0/22500 full obligations unchanged',ledger['vi_B_candidate_cap']==974 and ledger['vi_B_remaining']['candidate_constructions']==0 and
       ledger['formal_table_I_calls']==0 and ledger['formal_table_I_required_calls']==22500 and '211'in pre and '不提前 P2/Isaac'in pre)
    ck('only engineering draft no actual new run claim build yet',not(ROOT/'results/p4_full/20261016_R2_ABB_CBIRRT_NR_BUILD01').exists()and
       not(ROOT/'results/p4_full/P4_R2_ABB_CBIRRT_NR_BUILD_1_45W_90CPU_20261016.claim.json').exists()and
       not Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_cbirrt_nr_v1').exists())
    for n,want in list(retained.items()):ck('read bytes unchanged '+n,digest(Path(n).read_bytes())==want)
    failed=[c for c in checks if not c['passed']]
    report=dict(schema='P4_CBIRRT_NR_ENGINEERING_INDEPENDENT_STATIC_REVIEW_V2',
       status='PASS_VERSIONED_CBIRRT_NR_ENGINEERING_STATIC_REVIEW'if not failed else'FAIL_V2_STATIC_REVIEW',
       generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review; independent of implementation',personnel_independent=True,
       checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,
       reviewed_source_sha256=expected,independently_reconstructed_staged_sha256=staged,original_body_observation_kinds=kinds,
       actual_selected_boost_libraries=selected_boost,retained_sha256=retained,
       new_scientific_calls=0,runner_model_import_calls=0,CXX_compile_calls=0,binary_execution_calls=0,protocol_generation_calls=0,prior_generation_calls=0,claims_created=0,
       independent_pure_memory_inverse_performed=True,engineering_built=False,science_qualified=False,
       prior_V1_failure_retained=True,limitations=['Static byte/AST and saved prior only. Root must freeze concrete latest actual protocol/source commit, then at most one45wall/90CPU engineering target.',
          'Only existing physical GD numerical reconstruction; original CBiNR full12 NN/grow/RBS/reconstruction bodies preserved. No faithful-original-KDL or paper-theory claim.',
          'Actual compiler dependencies must include all6 distinct translation units. Related protected numerical/library dependencies require frozen or exact staged SHA; generic OS headers are recorded with compiler/OS fingerprint and no whole-OS closure claim.',
          'After compiler kill/wait actual group emptiness is required. Failure-orphan CPU remains UNKNOWN unless later independent actual cost evidence covers it; after-group emptiness alone cannot prove historical CPU completeness.',
          'Successful engineering needs actual independent saved POST and whole-child external upper; does not authorize driver solve/path scientific qualification.',
          'Future driver waits stdin EOF before dispatch; future single-request runner must close stdin after writing, preserve full stdout/stderr EOF and actual process exit/group state without requiring an already-exited group to be live.',
          'V1 asset/lifecycle gaps are engineering review findings; original old binary hashes, qualifications, failures and UNKNOWN are preserved.','211 obligations, VI974余0 and formal0/22500 remain. No P2/Isaac.'])
    with OUT.with_suffix('.json').open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:f.write('# CBiRRT_NR 工程 V2 人员独立静态终审\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(len(checks))+'。0科学、编译、binary、runner/model import、协议/prior/claim。\n\n'+
       '独立纯内存重建并逆变换核完整五源原字节；13处完整body包装、同一已合格physical GD seam、原full12 NN/双树/RBS/回溯保持。V1两缺口保全，V2补实际相关库头绑定及compiler清理后真实组空门。\n\n'+
       '唯一真实多TU编译的-MD副产物按六不同stem分开保存，实际相关依赖必须已冻结，通用OS头按实际清单/指纹记录；[GCC11输出命名规则](https://gcc.gnu.org/onlinedocs/gcc-11.4.0/gcc/Overall-Options.html)。外层45/90含完整子生命周期，实际编译和独立后审尚待执行，静态报告不授权solve。\n')
    print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),failures=failed),ensure_ascii=False))
    raise SystemExit(0 if not failed else 2)

if __name__=='__main__':main()
