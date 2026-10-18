#!/usr/bin/env python3
"""DRAFT V BUILD02 engineering tail: reuse eight saved objects; only 2 TU+link.

No transform, describe, model, binary execution or scientific query. Actual
BUILD01 STOP is immutable; eight object hashes were first collected by its
independent failure POST, and their original STOP hashes remain UNKNOWN.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_v_pcs_local_v1_draft as B
RUN_NAME='20261018_R2_D080_V_PCS_BUILD02_TAIL'
RUN=ROOT/'results/p4_full'/RUN_NAME
STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_build02')
OLD_STAGE=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1')
OLD_RUN='20261018_R2_D080_V_PCS_BUILD01'
SOURCE_POST=ROOT/'reports/P4_D080_ENV_V_PCS_BUILD01_FAILURE_SAVED_INDEPENDENT_POST_20261018.json'
SOURCE_POST_SHA='3dca76842b2f50751bd9c0455b592dff89dd4dbf7c09fbf7dfcf72c487d9576a'
SOURCE_EXEC=ROOT/'results/p4_full'/OLD_RUN/'execution.json'
SOURCE_EXEC_SHA='0027c3c1c64d72cf02903b383ea7bbf3fb417b2b0107c6a673398cb8db825a2a'
PRE=ROOT/'reports/P4_D080_ENV_V_PCS_BUILD02_TAIL_PRE_DRAFT_20261018.md'
SUPERVISOR=ROOT/'scripts/p4_d080/supervise_v_pcs_build02_tail_v1_draft.py'
LABEL='ENGINEERING_BUILD_TAIL_ONLY_V_PCS_REUSE8TU_BUILD2TU_ORIGINAL_CONTROL'
BASIS='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE'
# Identity-only context for the already reviewed prior, dependency and invoke
# functions. No body is replaced; the source/old stage remains read-only.
B.RUN_NAME=RUN_NAME;B.RUN=RUN;B.STAGE=STAGE;B.SUPERVISOR=SUPERVISOR
require=B.require;sha=B.sha;load=B.load;path=B.path;write_once=B.write_once
cpu=B.cpu;validate_prior=B.validate_prior;invoke=B.invoke
lifecycle=B.lifecycle;compiler_group_members=B.compiler_group_members
TIME=B.TIME;PYTHON=B.PYTHON;COMPILER=B.COMPILER;LIBDIR=B.LIBDIR;PQP=B.PQP


def tail_commands(libraries):
    old=OLD_STAGE/'trace';dest=STAGE/'trace'
    sources=[old/'validity_checkers/collisionDetection.cpp',old/'planners/RRT_PCS.cpp']
    common=[str(COMPILER),'-std=c++17','-O2','-Wall','-Wextra','-pthread','-DP4V_TRACE_MODE=1',
        '-I'+str(B.OMPL),'-I/usr/include/eigen3','-I'+str(PQP/'include'),
        '-I'+str(old),'-I'+str(old/'proj_classes'),'-I'+str(old/'validity_checkers'),
        '-include',str(old/B.OBSERVER.name)]
    new=[];commands=[]
    for index,source in enumerate(sources,3):
        obj=dest/(str(index)+'_'+source.stem+'.o');dep=obj.with_suffix('.d');new.append(obj)
        commands.append([*common,'-MD','-MF',str(dep),'-MT',str(obj),'-c',str(source),'-o',str(obj)])
    objects=[old/'0_comau_v_pcs_local_driver_v1_draft.o',old/'1_apc_class.o',old/'2_StateValidityCheckerPCS.o',*new]
    commands.append([str(COMPILER),'-pthread',*map(str,objects),str(PQP/'lib/libPQP.a'),*map(str,libraries),
        '-Wl,-rpath,'+str(LIBDIR),'-o',str(dest/'v_pcs_local')])
    return commands


def reuse_assets(spec,protocol):
    bound,meshes,libraries=B.frozen_assets(spec,protocol)
    post=load(SOURCE_POST);source=load(SOURCE_EXEC)
    require(sha(SOURCE_POST)==SOURCE_POST_SHA and sha(SOURCE_EXEC)==SOURCE_EXEC_SHA
        and post['schema']=='P4_D080_V_PCS_BUILD01_FAILURE_SAVED_INDEPENDENT_POST_V1'
        and post['status']=='PASS_FAILURE_PRESERVATION_AND_COST_ONLY'and post['personnel_independent']is True
        and post['checks_total']==post['checks_passed']==78 and post['checks_failed']==0
        and post['external_supervision_qualified']is True and post['engineering_build_qualified']is False
        and post['execution_sha256']==SOURCE_EXEC_SHA and post['completed_translation_units']==8
        and post['original_STOP_object_sha256_status']=='UNKNOWN_NOT_RECORDED_AT_STOP'
        and source['status']==post['original_execution_status']=='STOP_ENGINEERING_FAILURE_RETAINED_PREFIX'
        and source['error']==post['original_error']=='RuntimeError: BUILD_WORKING_CAP40W80CPU_RESERVE_FINAL45W90CPU',
        'EXACT_INDEPENDENT_BUILD01_FAILURE_AND_FIRST_COLLECTED_PREFIX_REQUIRED')
    required=[Path(__file__).resolve(),SUPERVISOR,PRE,SOURCE_POST,SOURCE_EXEC,
        *[path(n)for n in post['retained_sha256']],*map(Path,source['bound_files_sha256']),
        *map(Path,source['staged_after_sha256']),*map(Path,source['dependencies_after_sha256'])]
    require(all(bound.get(str(p.resolve()))==sha(p)for p in required),'ALL_TAIL_OLD_SOURCES_EVIDENCE_AND_OWN_FILES_MUST_BE_PREBOUND')
    require(source['bound_files_sha256']==source['bound_files_after_sha256']
        and all(sha(n)==w for n,w in source['staged_after_sha256'].items())
        and all(sha(n)==w for n,w in source['dependencies_after_sha256'].items()),'ORIGINAL_SOURCES_AND_EIGHT_DEPS_MUST_REMAIN_EXACT')
    reusable=post['reusable_saved_build_assets'];require(len(reusable)==17,'EXACT17_SAVED_ARTIFACTS_REQUIRED')
    objects=[r for r in reusable if r['kind']=='completed_ELF64_relocatable']
    deps=[r for r in reusable if r['kind']=='gcc_MD_dependency']
    bins=[r for r in reusable if r['kind']=='linked_ELF64_executable']
    require(len(objects)==8 and len(deps)==8 and len(bins)==1 and bins[0]['mode']=='plain'
        and all(r['original_STOP_sha256']is None and r['original_STOP_sha256_status']=='UNKNOWN_NOT_RECORDED_AT_STOP'for r in objects),
        'ORIGINAL_OBJECT_HASH_UNKNOWN_MUST_REMAIN_EXPLICIT')
    for row in reusable:
        p=Path(row['path']);stat=p.stat()
        require(p.is_relative_to(OLD_STAGE)and not p.is_symlink()and row['corresponding_saved_returncode']==0
            and row['first_current_artifact_collection']=='THIS_SAVED_ONLY_FAILURE_POST'
            and sha(p)==row['sha256']==bound.get(str(p.resolve()))and stat.st_size==row['size_bytes']
            and stat.st_mtime_ns==row['mtime_ns'],'FIRST_COLLECTED_OLD_ARTIFACT_BYTES_OR_IDENTITY_CHANGED')
    require(not(OLD_STAGE/'trace/3_collisionDetection.o').exists()and not(OLD_STAGE/'trace/3_collisionDetection.d').exists()
        and not(OLD_STAGE/'trace/4_RRT_PCS.o').exists()and not(OLD_STAGE/'trace/4_RRT_PCS.d').exists()
        and not(OLD_STAGE/'trace/v_pcs_local').exists(),'ORIGINAL_FAILED_OR_UNSTARTED_OUTPUTS_MUST_REMAIN_ABSENT')
    require(spec['commands']==tail_commands(libraries),'EXACT_ORIGINAL_FLAGS_ONLY_TWO_TAIL_TUS_AND_LINK_REQUIRED')
    return bound,libraries,source,post,reusable


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
    require(spec['schema']=='P4_D080_V_PCS_BUILD02_TAIL_FROZEN_V1'and spec['frozen']is True
        and spec['engineering_execution_authorized']is True and spec['independent_review_passed']is True
        and spec['scientific_execution_authorized']is False and spec['formal_execution_authorized']is False
        and spec['environment']=='V'and spec['run_name']==RUN_NAME and spec['classification']==LABEL
        and spec['stage_root']==str(STAGE)and spec['budget']=={'wall_s':20,'cpu_s':40}
        and spec['working_budget']=={'wall_s':15,'cpu_s':30},'FROZEN_INDEPENDENT_TAIL_ENGINEERING_ONLY_REQUIRED')
    supervisor=validate_supervision(spec,args.protocol)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for filename in [Path(__file__).resolve(),SUPERVISOR,PRE,Path(B.__file__).resolve(),SOURCE_POST,args.protocol]:
        relative=str(filename.relative_to(ROOT))
        require(subprocess.check_output(['git','show',commit+':'+relative],cwd=ROOT)==filename.read_bytes(),
            'FROZEN_OWN_AND_REUSED_SOURCE_PROTOCOL_MUST_BE_COMMITTED_'+relative)
    require(not lifecycle.active_p4()and signal.getitimer(signal.ITIMER_REAL)==(0.,0.),'NO_ACTIVE_P4_OR_TIMER_REQUIRED')
    require(not RUN.exists()and not STAGE.exists(),'FRESH_TAIL_RUN_STAGE_NO_RETRY_OR_OVERWRITE')
    started=time.monotonic();before_cpu=cpu();RUN.mkdir(parents=True,exist_ok=False)
    record={'source_commit':commit,'schema':'P4_D080_V_PCS_BUILD02_TAIL_EXECUTION_V1','run_name':RUN_NAME,'run_id':RUN_NAME,
        'classification':LABEL,'engineering_only':True,'status':'STARTED','execution_type':'engineering','environment':'V',
        'scientific_calls':0,'query_calls':0,'solve_calls':0,'rng_calls':0,'binary_execution_calls':0,
        'budget':dict(spec['budget']),'working_budget':dict(spec['working_budget']),'protocol_sha256':sha(args.protocol),
        'supervisor_contract':supervisor,'targets':[],'author_original_planning_qualified':False,
        'source_failure_POST':str(SOURCE_POST.relative_to(ROOT)),'source_failure_POST_sha256':SOURCE_POST_SHA,
        'original_STOP_object_sha256_status':'UNKNOWN_NOT_RECORDED_AT_STOP',
        'source_transform_calls':0,'new_translation_units_expected':2,'reused_translation_units_expected':8,
        'external_supervision_and_independent_post_required':True}
    code=2;diagnostics=[];state={'proc':None,'groups':[],'dependencies':{},'staged':{}}
    old_handler=signal.getsignal(signal.SIGALRM)
    def check():
        proc=state['proc'];live=0. if proc is None or proc.returncode is not None else lifecycle.live_group_cpu(proc.pid)
        require(time.monotonic()-started<15 and cpu()-before_cpu+live<30,'TAIL_WORKING_CAP15W30CPU_RESERVE_FINAL20W40CPU')
    def alarm(*_):check()
    try:
        write_once(RUN/'claim.json',record);record['claim_sha256']=sha(RUN/'claim.json')
        signal.signal(signal.SIGALRM,alarm);signal.setitimer(signal.ITIMER_REAL,.02,.02);check()
        record['prior']=validate_prior(spec)
        bound,libraries,source,post,reusable=reuse_assets(spec,args.protocol)
        require(all(bound.get(n)==w for n,w in record['prior']['evidence_sha256'].items()),'LATEST_PRIOR_ALL_EVIDENCE_MUST_BE_PREBOUND')
        record['bound_files_sha256']=bound
        record['reused_saved_build_assets']=reusable
        record['original_BUILD01_status_retained']=source['status'];record['original_BUILD01_execution_sha256']=SOURCE_EXEC_SHA
        record['original_staged_and_dependency_sha256']={**source['staged_after_sha256'],**source['dependencies_after_sha256']}
        write_once(RUN/'reused_first_collected_assets.json',{'source_POST':str(SOURCE_POST.relative_to(ROOT)),
            'source_POST_sha256':SOURCE_POST_SHA,'assets':reusable,'original_STOP_object_sha256_status':'UNKNOWN_NOT_RECORDED_AT_STOP'})
        dest=STAGE/'trace';dest.mkdir(parents=True,exist_ok=False)
        plain=source['targets'][0]
        require(plain['mode']=='plain'and plain['status']=='BUILT_NOT_QUERIED','ORIGINAL_PLAIN_LINKED_ELF_REQUIRED')
        record['targets'].append({'mode':'plain','status':'REUSED_BUILT_NOT_QUERIED','binary':plain['binary'],
            'binary_sha256':plain['binary_sha256'],'source_execution':str(SOURCE_EXEC.relative_to(ROOT)),
            'source_execution_sha256':SOURCE_EXEC_SHA,'new_commands':[],'new_compile_calls':0,'binary_execution_calls':0})
        target={'mode':'trace','status':'COMPILING_TAIL','source_sha256':source['targets'][1]['source_sha256'],
            'commands':[],'dependencies':[],'binary_execution_calls':0,'reused_old_object_count':3}
        record['targets'].append(target)
        for index,command in enumerate(spec['commands'][:2],3):
            obj=dest/('3_collisionDetection.o'if index==3 else'4_RRT_PCS.o');dep=obj.with_suffix('.d')
            src=OLD_STAGE/('trace/validity_checkers/collisionDetection.cpp'if index==3 else'trace/planners/RRT_PCS.cpp')
            invoke(command,OLD_STAGE/'trace',RUN/('trace_'+str(index)),target,state,check)
            state['dependencies'][str(dep.resolve())]=sha(dep)
            evidence=B.dependency_evidence(dep,obj,src,{},bound,state)
            require(all(bound.get(n)==w for n,w in evidence['actual_dependencies_sha256'].items()if Path(n).is_relative_to(OLD_STAGE)),
                'ORIGINAL_STAGE_ACTUAL_HEADER_AND_SOURCE_BYTES_MUST_BE_FROZEN')
            target['dependencies'].append(evidence)
            state['staged'][str(obj.resolve())]=sha(obj)
        invoke(spec['commands'][2],OLD_STAGE/'trace',RUN/'trace_link',target,state,check)
        binary=dest/'v_pcs_local';target.update(status='BUILT_NOT_QUERIED',binary=str(binary),binary_sha256=sha(binary))
        state['staged'][str(binary.resolve())]=sha(binary)
        require(all(sha(n)==w for n,w in bound.items()),'FROZEN_OLD_ASSET_DRIFT')
        record['status']='BUILT_TAIL_NOT_QUERIED_PENDING_COMPOSITE_INDEPENDENT_POST';code=0
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
            record['compile_log_sha256'] = {str(p.relative_to(ROOT)): sha(p) for p in sorted(RUN.glob('*.log')) if p.is_file()}
        except BaseException as error:
            diagnostics.append({'stage': 'compile_log_hashes', 'error': repr(error)})
        record['diagnostics'] = diagnostics
        record['wall_s'] = time.monotonic() - started; record['cpu_s'] = cpu() - before_cpu
        if diagnostics:
            record['status'] = 'STOP_CLEANUP_OR_EVIDENCE_ERROR'; code = 2
        if record['wall_s'] >= 20 or record['cpu_s'] >= 40:
            record['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'; code = 2
        record['cost_status'] = 'PROVISIONAL_REQUIRES_EXTERNAL_SUPERVISION_POST_NO_AUTO_CHARGE_REPLACEMENT'
        write_once(RUN / 'execution.json', record)
        receipt = {'schema': 'P4_D080_V_PCS_BUILD_COST_RECEIPT_V1', 'execution_sha256': sha(RUN / 'execution.json'),
                   'status': record['status'], 'wall_s_through_execution_persistence': time.monotonic() - started,
                   'cpu_s_through_execution_persistence': cpu() - before_cpu,
                   'last_receipt_persistence_tail': 'UNMEASURED_NONZERO_EXTERNAL_SUPERVISION_REQUIRED',
                   'external_supervision_qualified': False}
        if receipt['wall_s_through_execution_persistence'] >= 20 or receipt['cpu_s_through_execution_persistence'] >= 40:
            receipt['status'] = 'STOP_FINAL_WALL_OR_CPU_BUDGET'; code = 2
        write_once(RUN / 'cost_receipt.json', receipt)
    return code


if __name__=='__main__':sys.exit(main())
