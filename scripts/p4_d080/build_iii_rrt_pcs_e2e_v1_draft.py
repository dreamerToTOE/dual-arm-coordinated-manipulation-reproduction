#!/usr/bin/env python3
"""III RRT_PCS build-only thin draft. No describe, binary or model queries.

Copy the qualified existing components unchanged;5 TU+1link only. Reuse V's
reviewed prior/invoke/dependency/group/Decimal accounting infrastructure.
This file is never an approval or an executable protocol by itself.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_v_pcs_local_v1_draft as B
RUN_NAME='20261018_R2_D080_III_RRT_PCS_BUILD01'
RUN=ROOT/'results/p4_full'/RUN_NAME
STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_iii_rrt_pcs_e2e_v1')
DEST=STAGE/'geometry_consistent_observed'
OLD_STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_rrt_pcs_e2e_v1/geometry_consistent_observed')
AUTHOR=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning')
PLAN=ROOT/'configs/p4_d080/iii_rrt_pcs_e2e_engineering_plan_v1.DRAFT.json'
PLAN_SHA='cb5f028e38339a36306d791dda2b41f9de04cc922e5fc70a8876046a1485258e'
DEPENDENCIES=ROOT/'configs/p4_d080/iii_rrt_pcs_saved_dependency_union_v1.DRAFT.json'
PRE=ROOT/'reports/P4_D080_ENV_III_RRT_PCS_EXECUTOR_PRE_DRAFT_20261018.md'
SUPERVISOR=ROOT/'scripts/p4_d080/supervise_iii_rrt_pcs_e2e_build_v1_draft.py'
LABEL='ENGINEERING_BUILD_ONLY_III_RRT_PCS_UNCHANGED_QUALIFIED_COMPONENTS'
B_SOURCE_SHA='1f79c14d02368959fce03c88c4c2f39b99cbdb0bbb5ffd149330a4ef91170578'
B.RUN_NAME=RUN_NAME;B.RUN=RUN;B.STAGE=STAGE;B.SUPERVISOR=SUPERVISOR
B.AUTHOR=AUTHOR;B.APC_STAGE=OLD_STAGE;B.COL_STAGE=OLD_STAGE
require=B.require;sha=B.sha;load=B.load;path=B.path;write_once=B.write_once
cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke
lifecycle=B.lifecycle;compiler_group_members=B.compiler_group_members
TIME=B.TIME;PYTHON=B.PYTHON;COMPILER=B.COMPILER;LIBDIR=B.LIBDIR;PQP=B.PQP


def active_d080(supervisor):
    # Legacy lifecycle guard remains unchanged. Supplement only the new D080
    # build/qualification/supervision scripts; skip our proven own launch chain.
    allowed={os.getpid(),supervisor['actual_time_pid'],supervisor['supervisor_pid']}
    active=[];directory=str(ROOT/'scripts/p4_d080')+'/'
    for entry in Path('/proc').glob('[0-9]*/cmdline'):
        pid=int(entry.parent.name)
        if pid in allowed:continue
        try:parts=entry.read_bytes().split(b'\0')
        except OSError:continue
        exe=parts[0].decode(errors='replace')if parts else ''
        scripts=[p.decode(errors='replace')for p in parts[1:3]]if 'python'in exe else []
        resolved=[]
        for script in scripts:
            if script.startswith('-'):continue
            try:resolved.append(str((Path('/proc',str(pid),'cwd')/script).resolve(strict=True)))
            except OSError:continue
        if any(s.startswith(directory)and Path(s).name.startswith(('build_','qualify_','supervise_'))for s in resolved):
            active.append({'pid':pid,'command':b' '.join(parts).decode(errors='replace')})
    return active


def frozen_assets(spec,protocol):
    require(sha(PLAN)==PLAN_SHA and sha(B.__file__)==B_SOURCE_SHA,'EXACT_PLAN_AND_REUSED_V_INFRASTRUCTURE_REQUIRED')
    plan=load(PLAN)
    require(spec['copy_exact_assets']==plan['copy_exact_assets']
        and spec['commands']==[u['command']for u in plan['compile_units']]+[plan['link_command']]
        and spec['binary']==plan['binary']and spec['stage_root']==str(STAGE)
        and spec['new_compile_calls']==5 and spec['new_link_calls']==1,'EXACT_THIN32_ASSETS_5TU1LINK_PLAN_REQUIRED')
    required=[Path(__file__).resolve(),SUPERVISOR,PRE,PLAN,DEPENDENCIES,Path(B.__file__).resolve(),
        ROOT/'scripts/build_p4_full_r2_abb_cbirrt_d_draft.py',
        ROOT/'baselines/p4_full/geometry_consistent/abb_cbirrt_d_instrumentation_draft.py',
        ROOT/'baselines/p4_full/geometry_consistent/abb_pcs_source_corrections_draft.py',
        COMPILER,TIME,PYTHON,Path('/usr/lib/gcc/x86_64-linux-gnu/11/cc1plus'),Path('/usr/bin/as'),
        Path('/usr/bin/x86_64-linux-gnu-ld.bfd'),Path('/etc/os-release'),B.SCOPE,B.OVERLAY,
        path(plan['base_manifest']),PQP/'lib/libPQP.a']
    require(sha(B.SCOPE)==B.SCOPE_SHA and sha(B.OVERLAY)==B.OVERLAY_SHA,'D080_SCOPE_BYTES_REQUIRED')
    scope=load(B.SCOPE)
    require(scope['allowed_environments']==['I','II','III','IV','V']
        and scope['VI_future_science_authorized']is False and scope['formal_execution_authorized']is False,'D080_SCOPE_NO_VI_OR_FORMAL')
    require(len(spec['copy_exact_assets'])==32,'EXACT32_COPY_ASSETS_REQUIRED')
    for row in spec['copy_exact_assets']:
        source=Path(row['source']);target=Path(row['destination'])
        require(target.is_relative_to(DEST)and sha(source)==row['sha256'],'SOURCE_COPY_IDENTITY_OR_DESTINATION_CHANGED')
        required.append(source)
    require(sha(DEPENDENCIES)==spec['dependency_union_sha256'],'SAVED_MD_UNION_BYTES_CHANGED')
    deps=load(DEPENDENCIES)
    require(deps['schema']=='P4_D080_III_RRT_PCS_SAVED_MD_DEPENDENCY_UNION_DRAFT_V1'
        and deps['new_compiler_or_dependency_preprocessing_calls']==0,'SAVED_MD_ONLY_UNION_REQUIRED')
    required.extend(path(n)for n in deps['source_MD_files_sha256'])
    pqp_names=('PQP.h','PQP_Internal.h','PQP_Compile.h','BV.h','Tri.h')
    require(set(deps['PQP_five_headers_sha256'])=={str(PQP/'include'/n)for n in pqp_names},'PREBOUND_EXACT_FIVE_PQP_HEADERS_REQUIRED')
    required.extend(PQP/'include'/n for n in pqp_names)
    libraries=[LIBDIR/'libompl.so',*[Path('/usr/lib/x86_64-linux-gnu')/('libboost_'+n+'.so')
        for n in ('filesystem','system','serialization','program_options')]]
    required.extend(p.resolve(strict=True)for p in libraries)
    bound={str(Path(n).resolve()):w for n,w in spec['bound_files_sha256'].items()}
    require(all(bound.get(str(p.resolve()))==sha(p)for p in required),'ALL_REQUIRED_III_ENGINEERING_INPUTS_TOOLS_MUST_BE_PREBOUND')
    for field in ('source_MD_files_sha256','actual_saved_dependencies_sha256','PQP_five_headers_sha256'):
        require(all(bound.get(str(path(n).resolve()))==w==sha(path(n))for n,w in deps[field].items()),'ALL_SAVED_MD_UNION_AND_FIVE_PQP_BYTES_MUST_BE_PREBOUND')
    require(all(Path(n).is_file()and sha(n)==w for n,w in bound.items()),'ANY_FROZEN_INPUT_DRIFT')
    return bound,plan


def validate_supervision(spec, protocol):
    # Actual GNUtime parent, grandparent supervisor, argv and held O_EXCL inode;
    # a JSON ACTIVE boolean is deliberately insufficient.
    ext = spec['external_supervision']
    raw = path(ext['metadata_path']).read_bytes().splitlines(keepends=True)[0]
    planned = json.loads(raw); parent = os.getppid()
    row = Path('/proc', str(parent), 'stat').read_text().rsplit(')', 1)[1].split()
    require(int(row[1]) == planned['supervisor_pid'] and sha(Path('/proc', str(parent), 'exe')) == sha(TIME),
            'ACTUAL_GNUTIME_PARENT_AND_SUPERVISOR_GRANDPARENT_REQUIRED')
    argv = [str(TIME), '--quiet', '-f', '%e %U %S %x', '-o', f"/proc/self/fd/{planned['time_fd']}",
            str(PYTHON), str(Path(__file__).resolve()), '--build', '--protocol', str(protocol)]
    require(planned['event'] == 'planned_launch' and planned['run_id'] == RUN_NAME
            and planned['protocol_sha256'] == sha(protocol) and planned['runner_sha256'] == sha(__file__)
            and planned['supervisor_source_sha256'] == sha(SUPERVISOR) and planned['argv'] == argv
            and Path('/proc', str(parent), 'cmdline').read_bytes().rstrip(b'\0').split(b'\0') == [s.encode() for s in argv],
            'EXACT_PARENT_ARGV_SOURCE_PROTOCOL_REQUIRED')
    output = path(ext['sibling_path']).stat(); held = []
    for descriptor in Path('/proc', str(parent), 'fd').iterdir():
        try:
            value = descriptor.stat()
            if (value.st_dev, value.st_ino) == (output.st_dev, output.st_ino):
                held.append(int(descriptor.name))
        except FileNotFoundError:
            pass
    require(held and (output.st_dev, output.st_ino) == (planned['time_device'], planned['time_inode']),
            'EXCLUSIVE_SUPERVISION_INODE_REQUIRED')
    return {'actual_time_pid': parent, 'actual_time_start_ticks': int(row[19]),
            'supervisor_pid': planned['supervisor_pid'], 'actual_argv': argv,
            'planned_launch_line_sha256': hashlib.sha256(raw).hexdigest(),
            'time_inode': output.st_ino, 'time_device': output.st_dev, 'actual_time_output_fds': sorted(held),
            'external_POST_required': True}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build',action='store_true',required=True)
    parser.add_argument('--protocol',type=Path,required=True);args=parser.parse_args();args.protocol=args.protocol.resolve()
    spec=load(args.protocol)
    require(spec['schema']=='P4_D080_III_RRT_PCS_BUILD_FROZEN_V1'and spec['frozen']is True
        and spec['engineering_execution_authorized']is True and spec['independent_review_passed']is True
        and spec['scientific_execution_authorized']is False and spec['formal_execution_authorized']is False
        and spec['environment']=='III'and spec['run_name']==RUN_NAME and spec['classification']==LABEL
        and spec['budget']=={'wall_s':45,'cpu_s':90}and spec['working_budget']=={'wall_s':40,'cpu_s':80},
        'FROZEN_BUILD_ONLY_III_PCS_EXACT_PROTOCOL_REQUIRED')
    supervisor=validate_supervision(spec,args.protocol)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    plan=load(PLAN)
    for filename in [Path(__file__).resolve(),SUPERVISOR,PRE,PLAN,DEPENDENCIES,Path(B.__file__).resolve(),
                     path(plan['new_driver']),path(plan['unchanged_observer']),args.protocol]:
        relative=str(filename.relative_to(ROOT))
        require(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)==filename.read_bytes(),
                'EXACT_COMMITTED_OWN_PROTOCOL_REQUIRED_'+relative)
    require(not lifecycle.active_p4()and not active_d080(supervisor),'OTHER_ACTIVE_P4_EXECUTION')
    require(signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'EXISTING_TIMER_REFUSE_REPLACE')
    require(not STAGE.exists()and not RUN.exists(),'OCCUPIED_STAGE_OR_RUN_NO_OVERWRITE')
    started=time.monotonic();before_cpu=cpu();RUN.mkdir(parents=True,exist_ok=False)
    record={'source_commit':commit,'schema':'P4_D080_III_RRT_PCS_BUILD_EXECUTION_V1',
        'run_name':RUN_NAME,'run_id':RUN_NAME,'classification':LABEL,'engineering_only':True,'execution_type':'engineering',
        'environment':'III','status':'STARTED','scientific_calls':0,'query_calls':0,'solve_calls':0,'rng_calls':0,
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
        require(time.monotonic()-started<40 and cpu()-before_cpu+live<80,'BUILD_WORKING_CAP40W80CPU_RESERVE_FINAL45W90CPU')
    def alarm(*_):check()
    try:
        write_once(RUN/'claim.json',record);record['claim_sha256']=sha(RUN/'claim.json')
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,.02,.02);check()
        record['prior']=validate_prior(spec)
        bound,plan=frozen_assets(spec,args.protocol)
        require(all(bound.get(n)==w for n,w in record['prior']['evidence_sha256'].items()),'LATEST_PRIOR_ALL_EVIDENCE_MUST_BE_PREBOUND')
        record['bound_files_sha256']=bound;STAGE.mkdir(exist_ok=False)
        for row in spec['copy_exact_assets']:
            target=Path(row['destination']);write_once(target,Path(row['source']).read_bytes())
            require(sha(target)==row['sha256'],'COPIED_III_SOURCE_OR_MESH_BYTES_CHANGED')
            state['staged'][str(target.resolve())]=row['sha256']
        staged=dict(state['staged'])
        write_once(STAGE/'copied_source_manifest.json',{'plan_sha256':PLAN_SHA,'copies':spec['copy_exact_assets']})
        target={'mode':'geometry_consistent_observed','status':'COMPILING','source_sha256':staged,
            'commands':[],'dependencies':[],'objects':[],'binary_execution_calls':0}
        record['targets'].append(target)
        for unit,command in zip(plan['compile_units'],spec['commands'][:5]):
            source=Path(unit['source']);obj=Path(unit['object']);dep=Path(unit['dependency']);obj.parent.mkdir(parents=True,exist_ok=True)
            require(not obj.exists()and not dep.exists(),'OCCUPIED_OBJECT_OR_DEP_NO_OVERWRITE')
            log=Path(unit['stdout'].removesuffix('.stdout.log'));log.parent.mkdir(parents=True,exist_ok=True)
            invoke(command,DEST,log,target,state,check)
            # First collect each successful object before any later dependency gate.
            observed={'index':unit['index'],'object':str(obj),'object_sha256':sha(obj),'object_size_bytes':obj.stat().st_size,
                'dependency':str(dep),'dependency_sha256':sha(dep),'collection':'IMMEDIATELY_AFTER_SAVED_SUCCESSFUL_COMPILE_BEFORE_DEPENDENCY_GATE'}
            state['staged'][str(obj.resolve())]=observed['object_sha256'];state['dependencies'][str(dep.resolve())]=observed['dependency_sha256']
            target['objects'].append(observed);write_once(RUN/('unit_'+str(unit['index'])+'_first_collected.json'),observed)
            evidence=B.dependency_evidence(dep,obj,source,staged,bound,state)
            target['dependencies'].append(evidence)
        binary=Path(plan['binary']);require(not binary.exists(),'OCCUPIED_ELF_NO_OVERWRITE')
        invoke(spec['commands'][5],DEST,Path(plan['link_stdout'].removesuffix('.stdout.log')),target,state,check)
        state['staged'][str(binary.resolve())]=sha(binary)
        target.update(status='BUILT_NOT_QUERIED',binary=str(binary),binary_sha256=sha(binary),new_compile_calls=5,new_link_calls=1)
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
        if record['wall_s'] >= 45 or record['cpu_s'] >= 90:
            record['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'; code = 2
        record['cost_status'] = 'PROVISIONAL_REQUIRES_EXTERNAL_SUPERVISION_POST_NO_AUTO_CHARGE_REPLACEMENT'
        write_once(RUN / 'execution.json', record)
        receipt = {'schema': 'P4_D080_III_RRT_PCS_BUILD_COST_RECEIPT_V1', 'execution_sha256': sha(RUN / 'execution.json'),
                   'status': record['status'], 'wall_s_through_execution_persistence': time.monotonic() - started,
                   'cpu_s_through_execution_persistence': cpu() - before_cpu,
                   'last_receipt_persistence_tail': 'UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',
                   'external_supervision_qualified': False}
        if receipt['wall_s_through_execution_persistence'] >= 45 or receipt['cpu_s_through_execution_persistence'] >= 90:
            receipt['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'; code = 2
        write_once(RUN / 'cost_receipt.json', receipt)
    return code


if __name__=='__main__':sys.exit(main())
