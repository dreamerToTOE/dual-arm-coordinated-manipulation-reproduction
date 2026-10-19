#!/usr/bin/env python3
"""V RRT_PCS engineering-only2TU+1link draft, no binary/model execution."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_iii_rrt_pcs_e2e_v1_draft as I
import validate_prior_preflight_recovery_v2 as P
B=I.B
RUN_NAME='20261019_R2_D080_V_RRT_PCS_BUILD02_RECOVERY'
RUN=ROOT/'results/p4_full'/RUN_NAME
STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_rrt_pcs_e2e_v2')
DEST=STAGE
TRACE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1/trace')
PLAN=ROOT/'configs/p4_d080/v_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'
TEMPLATE=ROOT/'configs/p4_d080/v_rrt_pcs_e2e_build_v3.DRAFT.json'
PLAN_SHA='1c320aa3d55a638124b86b1235445c0aac80857dd4313dcb4d8c060f802d55fe'
DEPENDENCIES=ROOT/'configs/p4_d080/v_rrt_pcs_saved_dependency_union_v1.DRAFT.json'
PRE=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_BUILD02_EXECUTOR_PRE_DRAFT_20261018.md'
SUPERVISOR=ROOT/'scripts/p4_d080/supervise_v_rrt_pcs_e2e_build_v3_draft.py'
TRANSFORM=ROOT/'baselines/p4_full/geometry_consistent/comau_v_rrt_pcs_e2e_instrumentation_v1_draft.py'
SEAM_REVIEW=ROOT/'reports/P4_D080_ENV_V_RRT_PCS_THIN_DRAFT_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
COMPOSITE=ROOT/'reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_COMPOSITE_SAVED_INDEPENDENT_POST_ADDENDUM_20261018.json'
LABEL='ENGINEERING_BUILD_ONLY_V_RRT_PCS_2TU1LINK_ORIGINAL_RRT_CONTROL'
I_SOURCE_SHA='a3035ab09ade161811026eb08fc0523ab07f7adde3da86cd431cabcfddc3eabe'
B_SOURCE_SHA='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578'
OWN=[Path(__file__).resolve(),SUPERVISOR,PRE,PLAN,DEPENDENCIES,Path(I.__file__).resolve(),Path(B.__file__).resolve(),
    TRANSFORM,ROOT/'baselines/p4_full/geometry_consistent/comau_v_rrt_pcs_e2e_driver_v1_draft.cpp',
    ROOT/'baselines/p4_full/geometry_consistent/abb_rrt_pcs_e2e_observation.hpp',SEAM_REVIEW,TEMPLATE,Path(P.__file__).resolve()]
I.__file__=__file__;I.RUN_NAME=RUN_NAME;I.SUPERVISOR=SUPERVISOR
B.RUN_NAME=RUN_NAME;B.RUN=RUN;B.STAGE=STAGE;B.SUPERVISOR=SUPERVISOR
B.AUTHOR=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/ckcComau_industrialScene');B.APC_STAGE=TRACE;B.COL_STAGE=TRACE
require=B.require;sha=B.sha;load=B.load;path=B.path;write_once=B.write_once
cpu=B.cpu;invoke=B.invoke
lifecycle=B.lifecycle;compiler_group_members=B.compiler_group_members
validate_supervision=I.validate_supervision;active_d080=I.active_d080
TIME=B.TIME;PYTHON=B.PYTHON;COMPILER=B.COMPILER;LIBDIR=B.LIBDIR;PQP=B.PQP


# The reviewed engineering plan is byte-frozen at the v1 stage identity.
# Recovery gets a fresh stage root, so only paths that name that stage are
# rebased in-memory; all source, dependency, compiler, and reuse bytes remain
# exactly those reviewed by the original plan.
OLD_STAGE='/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_rrt_pcs_e2e_v1'

def rebase_stage_paths(value):
    if isinstance(value, str):
        return value.replace(OLD_STAGE, str(STAGE))
    if isinstance(value, list):
        return [rebase_stage_paths(item) for item in value]
    if isinstance(value, dict):
        return {key: rebase_stage_paths(item) for key, item in value.items()}
    return value


def validate_prior(spec):
    return P.validate_prior(spec,RUN_NAME,RUN)


def frozen_assets(spec,protocol):
    require(sha(PLAN)==PLAN_SHA and sha(OWN[5])==I_SOURCE_SHA and sha(B.__file__)==B_SOURCE_SHA,
        'EXACT_REVIEWED_PLAN_AND_REUSED_III_V_INFRASTRUCTURE_REQUIRED')
    plan=load(PLAN); plan_local=rebase_stage_paths(plan); review=load(SEAM_REVIEW)
    require(spec['commands']==plan_local['commands']and spec['reused_objects']==plan['reused_objects']
        and spec['new_compile_calls']==2 and spec['new_link_calls']==1 and spec['stage_root']==str(STAGE)
        and spec['binary']==plan_local['commands'][2][-1],'EXACT_ORIGINAL_TWO_TU_ONE_LINK_PLAN_REQUIRED')
    require(review['personnel_independent']is True and review['checks_total']==review['checks_passed']==20
        and review['checks_failed']==0 and spec['source_transform_receipt']==review['pure_transform_receipt']
        and spec['transformed_SVC_sha256']==review['pure_transform_output_sha256'],'EXACT20_SEAM_REVIEW_TRANSFORM_REQUIRED')
    require(sha(B.SCOPE)==B.SCOPE_SHA and sha(B.OVERLAY)==B.OVERLAY_SHA,'D080_SCOPE_BYTES_REQUIRED')
    scope=load(B.SCOPE)
    require(scope['allowed_environments']==['I','II','III','IV','V']and scope['formal_table_I_D080']==18000
        and scope['VI_future_science_authorized']is False and scope['formal_execution_authorized']is False,'D080_NO_VI_OR_FORMAL')
    required=[*OWN,COMPOSITE,ROOT/'scripts/build_p4_full_r2_abb_cbirrt_d_draft.py',
        ROOT/'baselines/p4_full/geometry_consistent/abb_cbirrt_d_instrumentation_draft.py',
        ROOT/'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py',
        COMPILER,TIME,PYTHON,Path('/usr/lib/gcc/x86_64-linux-gnu/11/cc1plus'),Path('/usr/bin/as'),
        Path('/usr/bin/x86_64-linux-gnu-ld.bfd'),Path('/etc/os-release'),B.SCOPE,B.OVERLAY,PQP/'lib/libPQP.a']
    for name,want in plan['source_builds'].items():require(sha(path(name))==want,'OLD_V_SOURCE_BUILD_CHANGED');required.append(path(name))
    for name,want in plan['own_sources_sha256'].items():require(sha(path(name))==want,'OLD_V_E2E_SEAM_SOURCE_CHANGED');required.append(path(name))
    for row in plan['reused_objects']:
        for field in ('object','dependency','source'):
            require(sha(row[field])==row[field+'_sha256'],'REUSED_V_OBJECT_MD_SOURCE_CHANGED');required.append(Path(row[field]))
    composite=load(COMPOSITE)
    require(sha(COMPOSITE)=='3a04f69aedc861166de04e147046a19ea35500b13e73270acb4e742ec7e9f7f8'
        and composite['personnel_independent']is True and composite['composite_build_qualified']is True
        and composite['original_BUILD01_engineering_build_qualified']is False,'EXACT_OLD_COMPOSITE_QUALIFICATION_AND_FAILED_BUILD01_RETAINED')
    for row in plan['reuse_dependency_bound_sets']:
        require(sha(path(row['protocol']))==row['sha256'],'ORIGINAL_REVIEWED_V_DEPENDENCY_POOL_CHANGED');required.append(path(row['protocol']))
    observer=plan['qualified_V_observer'];require(sha(observer['path'])==observer['sha256'],'SAME_PATH_V_TRACE1_OBSERVER_CHANGED');required.append(Path(observer['path']))
    for field in ('cpp','header'):
        require(sha(plan['RRT_source_byte_identity'][field])==plan['RRT_source_byte_identity'][field+'_sha256'],'WHOLE_ORIGINAL_V_RRT_BYTES_CHANGED')
        required.append(Path(plan['RRT_source_byte_identity'][field]))
    require(sha(plan['source_byte_transform']['input'])==plan['source_byte_transform']['input_sha256'],'QUALIFIED_V_INPUT_SVC_CHANGED')
    required.append(Path(plan['source_byte_transform']['input']))
    require(sha(DEPENDENCIES)==spec['dependency_union_sha256'],'EXACT_SAVED_MD_UNION_REQUIRED');deps=load(DEPENDENCIES)
    require(deps['schema']=='P4_D080_V_RRT_PCS_SAVED_MD_DEPENDENCY_UNION_DRAFT_V1'
        and deps['new_compiler_or_dependency_preprocessing_calls']==0 and deps['reused_three_MD_unique_dependency_count']==663,
        'SAVED_MD_ONLY_NO_NEW_HEADER_DISCOVERY')
    bound={str(path(n).resolve()):w for n,w in spec['bound_files_sha256'].items()}
    certificate=spec['independent_review_certificate'];require(isinstance(certificate,dict)and set(certificate)=={'path','sha256'},'EXACT_EXECUTOR_INDEPENDENT_REVIEW_BINDING_REQUIRED')
    certificate_path=path(certificate['path']);require(sha(certificate_path)==certificate['sha256'],'EXECUTOR_REVIEW_BYTES_CHANGED')
    checked=load(certificate_path);checked_inputs={str(path(n).resolve()):w for n,w in checked['inputs_sha256'].items()}
    require(checked['personnel_independent']is True and checked['checks_total']==checked['checks_passed']
        and checked['checks_failed']==0 and all(checked_inputs.get(str(p.resolve()))==sha(p)for p in (OWN[0],SUPERVISOR,PLAN,DEPENDENCIES,Path(P.__file__).resolve())),
        'EXACT_NEW_EXECUTOR_AND_PLAN_INDEPENDENT_REVIEW_REQUIRED')
    required.append(certificate_path)
    for field in ('source_MD_files_sha256','actual_saved_dependencies_sha256','PQP_five_headers_sha256'):
        require(all(bound.get(str(path(n).resolve()))==w==sha(n)for n,w in deps[field].items()),'ALL_SAVED_UNION_AND_PQP_BYTES_PREBOUND')
    required.extend(path(n)for n in deps['source_MD_files_sha256'])
    require(set(Path(n).name for n in deps['PQP_five_headers_sha256'])=={'PQP.h','PQP_Internal.h','PQP_Compile.h','BV.h','Tri.h'},'EXACT_FIVE_PQP_HEADERS_REQUIRED')
    libraries=[LIBDIR/'libompl.so',*[Path('/usr/lib/x86_64-linux-gnu')/('libboost_'+n+'.so')for n in ('filesystem','system','serialization','program_options')]]
    required.extend(p.resolve(strict=True)for p in libraries)
    require(all(bound.get(str(p.resolve()))==sha(p)for p in required),'ALL_REQUIRED_INPUTS_AND_REUSED_OBJECTS_PREBOUND')
    require(all(Path(n).is_file()and sha(n)==w for n,w in bound.items()),'ANY_FROZEN_ENGINEERING_INPUT_DRIFT')
    return bound,plan


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build',action='store_true',required=True)
    parser.add_argument('--protocol',type=Path,required=True);args=parser.parse_args();args.protocol=args.protocol.resolve()
    spec=load(args.protocol)
    require(spec['schema']=='P4_D080_V_RRT_PCS_BUILD_FROZEN_V1'and spec['frozen']is True
        and spec['engineering_execution_authorized']is True and spec['independent_review_passed']is True
        and spec['scientific_execution_authorized']is False and spec['formal_execution_authorized']is False
        and spec['environment']=='V'and spec['run_name']==RUN_NAME and spec['classification']==LABEL
        and spec['budget']=={'wall_s':30,'cpu_s':60}and spec['working_budget']=={'wall_s':25,'cpu_s':50},
        'FROZEN_BUILD_ONLY_V_RRT_PCS_EXACT_PROTOCOL_REQUIRED')
    supervisor=validate_supervision(spec,args.protocol)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    plan=load(PLAN)
    for filename in [*OWN,args.protocol]:
        relative=str(filename.relative_to(ROOT))
        require(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)==filename.read_bytes(),
                'EXACT_COMMITTED_OWN_PROTOCOL_REQUIRED_'+relative)
    require(not lifecycle.active_p4()and not active_d080(supervisor),'OTHER_ACTIVE_P4_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    require(not STAGE.exists()and not RUN.exists(),'OCCUPIED_STAGE_OR_RUN_NO_OVERWRITE')
    started=time.monotonic();before_cpu=cpu();RUN.mkdir(parents=True,exist_ok=False)
    record={'source_commit':commit,'schema':'P4_D080_V_RRT_PCS_BUILD_EXECUTION_V1',
        'run_name':RUN_NAME,'run_id':RUN_NAME,'classification':LABEL,'engineering_only':True,'execution_type':'engineering',
        'environment':'V','status':'STARTED','scientific_calls':0,'query_calls':0,'solve_calls':0,'rng_calls':0,
        'binary_execution_calls':0,'formal_table_I_calls':0,'new_VI_candidate_constructions':0,
        'budget':spec['budget'],'working_budget':spec['working_budget'],'protocol_sha256':sha(args.protocol),
        'supervisor_contract':supervisor,'targets':[],'author_original_planning_qualified':False,
        'external_supervision_and_independent_post_required':True}
    code=2;diagnostics=[];state={'proc':None,'groups':[],'dependencies':{},'staged':{}}
    old_handler=signal.getsignal(signal.SIGALRM)
    def check():
        proc=state['proc'];live=0. if proc is None or proc.returncode is not None else lifecycle.live_group_cpu(proc.pid)
        if proc is not None and proc.returncode is None:
            entry=state['groups'][-1]
            if 'start_ticks_observation'in entry:
                pass
            else:
                try:
                    fields=Path('/proc',str(proc.pid),'stat').read_text().rsplit(')',1)[1].split()
                    entry['start_ticks_observation']=int(fields[19])
                except(OSError,ValueError,IndexError):
                    entry['start_ticks_observation']='UNKNOWN_PROCESS_EXITED_BEFORE_READ'
        require(time.monotonic()-started<25 and cpu()-before_cpu+live<50,'BUILD_WORKING_CAP25W50CPU_RESERVE_FINAL30W60CPU')
    def alarm(*_):check()
    try:
        write_once(RUN/'claim.json',record);record['claim_sha256']=sha(RUN/'claim.json')
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,.02,.02);check()
        record['prior']=validate_prior(spec)
        bound,plan=frozen_assets(spec,args.protocol)
        require(all(bound.get(n)==w for n,w in record['prior']['evidence_sha256'].items()),'LATEST_PRIOR_ALL_EVIDENCE_MUST_BE_PREBOUND')
        record['bound_files_sha256']=bound;STAGE.mkdir(exist_ok=False)
        driver=plan_local['copy_driver_only'];driver_target=Path(driver['destination'])
        write_once(driver_target,Path(driver['source']).read_bytes())
        require(sha(driver_target)==driver['sha256'],'EXACT_V_DRIVER_COPY_REQUIRED')
        transform_spec=importlib.util.spec_from_file_location('p4_V_RRT_PCS_pure_e2e_observer_transform',TRANSFORM)
        transform=importlib.util.module_from_spec(transform_spec);transform_spec.loader.exec_module(transform)
        changed,proof=transform.instrument_svc(Path(plan_local['source_byte_transform']['input']).read_bytes())
        require(proof==spec['source_transform_receipt']and hashlib.sha256(changed).hexdigest()==spec['transformed_SVC_sha256'],
            'EXACT_PRE_REVIEWED_V_SVC_TRANSFORM_RECEIPT_REQUIRED')
        svc=Path(plan_local['source_byte_transform']['output']);write_once(svc,changed)
        state['staged'].update({str(driver_target.resolve()):sha(driver_target),str(svc.resolve()):sha(svc)})
        staged=dict(state['staged'])
        write_once(STAGE/'source_transform_manifest.json',proof)
        target={'mode':'geometry_consistent_observed','status':'COMPILING','source_sha256':staged,
            'commands':[],'dependencies':[],'objects':[],'binary_execution_calls':0}
        record['targets'].append(target)
        for index,command in enumerate(spec['commands'][:2]):
            source=Path(command[command.index('-c')+1]);obj=Path(command[command.index('-o')+1]);dep=Path(command[command.index('-MF')+1])
            obj.parent.mkdir(parents=True,exist_ok=True)
            require(not obj.exists()and not dep.exists(),'OCCUPIED_OBJECT_OR_DEP_NO_OVERWRITE')
            log=STAGE/'logs'/str(index);log.parent.mkdir(parents=True,exist_ok=True)
            invoke(command,DEST,log,target,state,check)
            # First collect each successful object before any later dependency gate.
            observed={'index':index,'object':str(obj),'object_sha256':sha(obj),'object_size_bytes':obj.stat().st_size,
                'dependency':str(dep),'dependency_sha256':sha(dep),'collection':'IMMEDIATELY_AFTER_SAVED_SUCCESSFUL_COMPILE_BEFORE_DEPENDENCY_GATE'}
            state['staged'][str(obj.resolve())]=observed['object_sha256'];state['dependencies'][str(dep.resolve())]=observed['dependency_sha256']
            target['objects'].append(observed);write_once(RUN/('unit_'+str(index)+'_first_collected.json'),observed)
            evidence=B.dependency_evidence(dep,obj,source,staged,bound,state)
            target['dependencies'].append(evidence)
        binary=Path(spec['binary']);require(not binary.exists(),'OCCUPIED_ELF_NO_OVERWRITE')
        invoke(spec['commands'][2],DEST,STAGE/'logs/link',target,state,check)
        state['staged'][str(binary.resolve())]=sha(binary)
        target.update(status='BUILT_NOT_QUERIED',binary=str(binary),binary_sha256=sha(binary),new_compile_calls=2,new_link_calls=1)
        require(all(sha(n)==w for n,w in bound.items()),'FROZEN_INPUT_DRIFT_DURING_BUILD')
        record['status']='BUILT_NOT_QUERIED';code=0
    except BaseException as error:
        record['status']='STOP_ENGINEERING_FAILURE_RETAINED_PREFIX';record['error']=type(error).__name__+': '+str(error)
    finally:
        # Same success/failure finalization as SBL BUILD02. Disable only our
        # timer, kill/reap every compiler group, then prove source/dep/prior bytes.
        previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
        try:
            signal.setitimer(signal.ITIMER_REAL, 0)
            while signal.SIGALRM in signal.sigpending():
                signal.sigwait({signal.SIGALRM})
            signal.signal(signal.SIGALRM, old_handler)
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
        for entry in state['groups']:
            proc = entry.pop('_process')
            try:
                entry['members_before_cleanup'] = compiler_group_members(proc.pid)
                entry['live_group_cpu_before_cleanup_s'] = lifecycle.live_group_cpu(proc.pid)
                if entry['members_before_cleanup']:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                proc.wait(timeout=2.)
                entry['reaped'] = True; entry['returncode_after_cleanup'] = proc.returncode
                entry['members_after_cleanup'] = compiler_group_members(proc.pid)
                require(not entry['members_after_cleanup'], 'COMPILER_GROUP_NOT_EMPTY_AFTER_KILL_WAIT')
            except BaseException as error:
                diagnostics.append({'stage': 'compiler_cleanup', 'error': repr(error)})
        record['compiler_groups'] = state['groups']
        for label, expected in (('bound_files', record.get('bound_files_sha256', spec['bound_files_sha256'])),
                                ('staged', state['staged']), ('dependencies', state['dependencies'])):
            observed = {}; errors = []
            for name, digest in expected.items():
                try:
                    observed[name] = sha(name)
                    require(observed[name] == digest, 'FINAL_HASH_CHANGED_' + name)
                except BaseException as error:
                    errors.append({'path': name, 'error': repr(error)})
            record[label + '_after_sha256'] = observed
            if errors:
                diagnostics.append({'stage': label + '_final_hashes', 'errors': errors})
        try:
            record['protocol_after_sha256'] = sha(args.protocol)
            record['claim_after_sha256'] = sha(RUN / 'claim.json')
            require(record['protocol_after_sha256'] == record['protocol_sha256']
                    and record['claim_after_sha256'] == record.get('claim_sha256'), 'PROTOCOL_OR_CLAIM_CHANGED')
            record['prior_after'] = validate_prior(spec)
            require(record['prior_after'] == record['prior'], 'LATEST_CHARGED_PRIOR_CHANGED_DURING_BUILD')
        except BaseException as error:
            diagnostics.append({'stage': 'final_protocol_claim_prior', 'error': repr(error)})
        try:
            record['compile_log_sha256'] = {str(p): sha(p) for p in sorted((STAGE/'logs').glob('*.log')) if p.is_file()}
            record['immediate_object_collection_receipts_sha256'] = {str(p.relative_to(ROOT)): sha(p) for p in sorted(RUN.glob('unit_*_first_collected.json')) if p.is_file()}
        except BaseException as error:
            diagnostics.append({'stage': 'compile_log_hashes', 'error': repr(error)})
        record['diagnostics'] = diagnostics
        record['wall_s'] = time.monotonic() - started; record['cpu_s'] = cpu() - before_cpu
        if diagnostics:
            record['status'] = 'STOP_CLEANUP_OR_EVIDENCE_ERROR'; code = 2
        if record['wall_s'] >= 30 or record['cpu_s'] >= 60:
            record['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'; code = 2
        record['cost_status'] = 'PROVISIONAL_REQUIRES_EXTERNAL_SUPERVISION_POST_NO_AUTO_CHARGE_REPLACEMENT'
        write_once(RUN / 'execution.json', record)
        receipt = {'schema': 'P4_D080_V_RRT_PCS_BUILD_COST_RECEIPT_V1', 'execution_sha256': sha(RUN / 'execution.json'),
                   'status': record['status'], 'wall_s_through_execution_persistence': time.monotonic() - started,
                   'cpu_s_through_execution_persistence': cpu() - before_cpu,
                   'last_receipt_persistence_tail': 'UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',
                   'external_supervision_qualified': False}
        if receipt['wall_s_through_execution_persistence'] >= 30 or receipt['cpu_s_through_execution_persistence'] >= 60:
            receipt['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'; code = 2
        write_once(RUN / 'cost_receipt.json', receipt)
    return code

if __name__=='__main__':sys.exit(main())
