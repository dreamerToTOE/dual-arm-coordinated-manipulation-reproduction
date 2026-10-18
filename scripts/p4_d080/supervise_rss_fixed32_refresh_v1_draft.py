#!/usr/bin/env python3
"""D080 fixed32 supervisor draft: reuse V2 process lifecycle, V Decimal envelope.

No runner import or model execution at preparation. Separate frozen protocol
and precise independent review required; original10wall20CPU cap remains.
"""
from pathlib import Path
from decimal import Decimal
import argparse
import json
import os
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import supervise_p4_full_r2_abb_rss_branch_fixed32_v2_draft as S
RUN='20261018_R2_D080_ABB_RSS_BRANCH_MATH01'
LABEL='RECONSTRUCTED_FIXED_SAVED_INPUT_BRANCH_MAPPING_MATH_ONLY'
TIME=Path('/usr/bin/time');PYTHON=Path('/usr/bin/python3')
RUNNER=ROOT/'scripts/p4_d080/qualify_rss_fixed32_refresh_v1_draft.py'
sha=S.sha;require=S.require;new_json=S.new_json;child_cpu=S.child_cpu;own_cpu=S.own_cpu
proc_table=S.proc_table;exact_source_processes=S.exact_source_processes
stop_children=S.stop_children;kill_source_identity=S.kill_source_identity
source_groups_after=S.source_groups_after;watch=S.watch


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--protocol',required=True,type=Path)
    protocol=parser.parse_args().protocol.resolve();spec=json.loads(protocol.read_text())
    require(sha(S.__file__)=='fada7f5aaf9e94d06aeb7572c062ba2dff7b843286ebaa571bf3af293a590619'
        and spec['own_source_sha256'][str(Path(S.__file__).resolve().relative_to(ROOT))]==sha(S.__file__),
        'EXACT_REUSED_V2_SUPERVISION_LIFECYCLE_REQUIRED')
    require(spec['schema']=='P4_D080_ABB_RSS_FIXED32_BRANCH_MATH_REFRESH_V1' and spec['run_id']==RUN and spec['classification']==LABEL and spec['frozen']is True
        and spec['qualification_execution_authorized']is True and spec['engineering_execution_authorized']is False and spec['formal_execution_authorized']is False
        and spec['budget']['wall_s']==10 and spec['budget']['cpu_s']==20 and set(spec['reviews'])=={'independent_static_review_passed','root_freeze_approved','latest_actual_charged_prior_confirmed'} and all(type(v)is bool and v for v in spec['reviews'].values()),'EXPLICIT_FROZEN_D080_RSS_FIXED32_REQUIRED')
    ext=spec['external_supervision'];prefix=ROOT/'results/p4_full'/RUN
    timefile=Path(str(prefix)+'.supervision.time.txt');metadata=Path(str(prefix)+'.supervision.jsonl')
    stderr=Path(str(prefix)+'.supervision.stderr.log');chargefile=Path(str(prefix)+'.supervision.charge.json')
    require(ext['sibling_path']==str(timefile.relative_to(ROOT))and ext['metadata_path']==str(metadata.relative_to(ROOT))
        and ext['stderr_path']==str(stderr.relative_to(ROOT))and ext['charge_path']==str(chargefile.relative_to(ROOT)),'EXACT_SUPERVISION_PATHS_REQUIRED')
    require(ext['format']=='%e %U %S %x'and ext['time_binary_sha256']==sha(TIME)and ext['python_binary_sha256']==sha(PYTHON),'EXACT_TIME_AND_PYTHON_REQUIRED')
    require(spec['own_source_sha256'][str(Path(__file__).resolve().relative_to(ROOT))]==sha(__file__)
        and spec['own_source_sha256'][str(RUNNER.relative_to(ROOT))]==sha(RUNNER),'FROZEN_SUPERVISOR_AND_RUNNER_REQUIRED')
    require(not exact_source_processes(spec),'EXISTING_EXACT_SOURCE_PROCESS_REFUSE_START')
    require(not prefix.exists()and not(ROOT/'results/p4_full'/(spec['claim_id']+'.claim.json')).exists(),'OLD_RUN_OR_CLAIM_NO_RETRY')
    require(not any(p.exists()for p in(timefile,metadata,stderr,chargefile)),'OLD_SUPERVISION_ARTIFACT_NO_RETRY')
    # O_EXCL is the actual race-safe guard. GNUtime receives our already-open
    # inode via inheritedFD, never an overwrite-capable ordinary output path.
    fd=os.open(timefile,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    opened_identity=(os.fstat(fd).st_dev,os.fstat(fd).st_ino)
    meta=None;err=None;proc=None;attempted=False;begun=None;cpu0=None;failure=None
    identities={};source_groups={};watchdog_stop=None;cleanup_errors=[];supervisor_cpu0=own_cpu();post_time_sources=[]
    try:
        meta=metadata.open('xb',buffering=0);err=stderr.open('xb',buffering=0)
        argv=[str(TIME),'--quiet','-f',ext['format'],'-o',f'/proc/self/fd/{fd}',str(PYTHON),str(RUNNER),'--protocol',str(protocol)]
        planned=dict(event='planned_launch',run_id=RUN,supervisor_pid=os.getpid(),supervisor_ppid=os.getppid(),supervisor_start_ticks=proc_table()[os.getpid()]['start_ticks'],
            supervisor_source_sha256=sha(__file__),protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),
            runner_sha256=sha(RUNNER),time_binary_sha256=sha(TIME),python_binary_sha256=sha(PYTHON),argv=argv,supervision_engineering=spec['supervision_engineering'],
            time_fd=fd,time_inode=os.fstat(fd).st_ino,time_device=os.fstat(fd).st_dev,
            supervision_cost_boundary='GNUtime fixed32 worker imports+at most36 sequential source processes+durable tail. Supervisor own watchdog/journal/fsync is separately observed, excluded from child GNUtime charge.')
        meta.write(json.dumps(planned,allow_nan=False,separators=(',',':')).encode()+b'\n');meta.flush();os.fsync(meta.fileno())
        begun=time.monotonic();cpu0=child_cpu();attempted=True
        proc=subprocess.Popen(argv,cwd=ROOT,pass_fds=(fd,),stderr=err)
        observed=proc_table().get(proc.pid)
        if observed is not None:proc.p4_start_ticks=observed['start_ticks']
        meta.write(json.dumps(dict(event='time_process_started',pid=proc.pid,argv=argv),separators=(',',':')).encode()+b'\n');meta.flush()
        identities,source_groups,watchdog_stop=watch(proc,spec,begun,cpu0,meta)
    except BaseException as exc:
        failure=repr(exc)
        # No relaunch. External interruption stops the sole actual child tree;
        # surviving source groups are still discovered by exact frozen binary.
        if proc is not None:
            try:stop_children(proc,spec,identities,source_groups)
            except BaseException as stop_error:cleanup_errors.append(repr(stop_error))
    finally:
        if proc is not None:
            try:
                stop_children(proc,spec,identities,source_groups);proc.wait(timeout=.25)
            except BaseException as stop_error:cleanup_errors.append(repr(stop_error))
        try:
            post_time_sources=exact_source_processes(spec)
            for row in post_time_sources:
                source_groups[row['pid']]=row;kill_source_identity(row)
        except BaseException as stop_error:cleanup_errors.append(repr(stop_error))
        fallback_wall=0. if begun is None else time.monotonic()-begun
        fallback_cpu=0. if cpu0 is None else child_cpu()-cpu0
        identity_unchanged=False
        try:
            current=timefile.stat();identity_unchanged=(current.st_dev,current.st_ino)==opened_identity
        except BaseException as exc:cleanup_errors.append('time_inode '+repr(exc))
        try:os.fsync(fd)
        except BaseException as exc:cleanup_errors.append('time_fsync '+repr(exc))
        finally:os.close(fd)
        if err is not None:
            try:err.flush();os.fsync(err.fileno())
            except BaseException as exc:cleanup_errors.append('supervisor_stderr '+repr(exc))
            finally:err.close()
        if meta is not None:
            try:
                meta.write(json.dumps(dict(event='time_process_reaped',pid=None if proc is None else proc.pid,
                    returncode=None if proc is None else proc.returncode,failure=failure),separators=(',',':')).encode()+b'\n')
                meta.flush();os.fsync(meta.fileno())
            except BaseException as exc:cleanup_errors.append('supervisor_metadata '+repr(exc))
            finally:meta.close()
        execution=prefix/'execution.json';receipt=prefix/'cost_receipt.jsonl'
        timing_valid=False;time_exit=None;wall=fallback_wall;cpu=fallback_cpu;fields=[]
        raw_wall=None;raw_cpu=None;envelope_valid=False;envelope_error=None;components=None
        try:
            fields=timefile.read_text().strip().split()
            if len(fields)!=4:raise ValueError('EXACT_FOUR_TIME_FIELDS_REQUIRED')
            elapsed,user,system=(Decimal(v)for v in fields[:3]);time_exit=int(fields[3])
            if not all(v.is_finite()and v>=0 for v in(elapsed,user,system)):raise ValueError('FINITE_NONNEGATIVE_TIME_FIELDS_REQUIRED')
            raw_wall=float(elapsed+Decimal('.01'));raw_cpu=float(user+system+Decimal('.02'));timing_valid=True
            wall=raw_wall;cpu=raw_cpu
        except (ValueError,ArithmeticError,OSError):pass
        # Conservative three-observation envelope at first persistence. Raw
        # GNUtime remains separate, including future clock adjustments; no
        # unqualified fallback is promoted when time or receipt is incomplete.
        # Even an incomplete receipt keeps the greatest already observed
        # raw/outer costs; completeness still fails and needs independent audit.
        try:
            outer_wall=Decimal(str(fallback_wall))+Decimal('.01')
            outer_cpu=Decimal(str(fallback_cpu))+Decimal('.02')
            if not all(v.is_finite()and v>=0 for v in(outer_wall,outer_cpu)):
                raise ValueError('FINITE_OUTER_OBSERVATION_REQUIRED')
            wall=float(max(outer_wall,Decimal(str(raw_wall))))if raw_wall is not None else float(outer_wall)
            cpu=float(max(outer_cpu,Decimal(str(raw_cpu))))if raw_cpu is not None else float(outer_cpu)
        except (ValueError,ArithmeticError,OSError):pass
        try:
            saved=json.loads(receipt.read_text())
            if not(timing_valid and execution.is_file() and saved['execution_sha256']==sha(execution)):
                raise ValueError('COMPLETE_RAW_TIME_AND_EXACT_INTERNAL_RECEIPT_REQUIRED')
            values=[Decimal(str(v))for v in(fallback_wall,fallback_cpu,
                saved['wall_s_through_execution_persistence'],saved['cpu_s_through_execution_persistence'])]
            if not all(v.is_finite()and v>=0 for v in values):raise ValueError('FINITE_MONOTONIC_AND_RECEIPT_VALUES_REQUIRED')
            walls=[elapsed+Decimal('.01'),values[0]+Decimal('.01'),values[2]+Decimal('.01')]
            cpus=[user+system+Decimal('.02'),values[1]+Decimal('.02'),values[3]+Decimal('.02')]
            wall=float(max(walls));cpu=float(max(cpus));envelope_valid=True
            components=dict(wall_decimal_s=[str(v)for v in walls],cpu_decimal_s=[str(v)for v in cpus],
                order=['raw_GNUtime_plus_padding','outer_monotonic_or_reaped_plus_padding','internal_receipt_plus_padding'])
        except (OSError,ValueError,ArithmeticError,KeyError,TypeError)as exc:envelope_error=repr(exc)
        def retained_hash(p):
            try:return sha(p)if p.is_file()else None
            except BaseException as exc:cleanup_errors.append('retained_hash '+str(p)+' '+repr(exc));return None
        payload=dict(schema='P4_D080_ABB_RSS_FIXED32_REFRESH_EXTERNAL_COST_CHARGE_V1',run_id=RUN,
            source_execution=str(execution.relative_to(ROOT)),execution_sha256=retained_hash(execution),
            receipt=str(receipt.relative_to(ROOT)),receipt_sha256=retained_hash(receipt),
            time_file=str(timefile.relative_to(ROOT)),time_sha256=retained_hash(timefile),time_fields=fields,
            metadata=str(metadata.relative_to(ROOT)),metadata_sha256=retained_hash(metadata),
            stderr=str(stderr.relative_to(ROOT)),stderr_sha256=retained_hash(stderr),
            time_process_pid=None if proc is None else proc.pid,time_returncode=None if proc is None else proc.returncode,
            measured_child_exit=time_exit,started_attempt=attempted,wall_s=wall,cpu_s=cpu,
            charge_basis='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE',
            raw_GNUtime_upper_wall_s=raw_wall,raw_GNUtime_upper_cpu_s=raw_cpu,
            monotonic_envelope_valid=envelope_valid,monotonic_envelope_components=components,monotonic_envelope_error=envelope_error,
            timing_valid=timing_valid,time_inode_unchanged=identity_unchanged,
            fallback_observed_outer_wait_wall_s=fallback_wall,fallback_reaped_children_CPU_s=fallback_cpu,
            fallback_cost_completeness='UNQUALIFIED_FINITE_OBSERVATION_ONLY_IF_TIME_INVALID',
            cost_boundary='Effective prior charge replaces this execution pre-save cost, or charges orphan preflight attempt. Supervisor own journal/fsync cost excluded.',
            failure=failure,watchdog_stop=watchdog_stop,watchdog_cleanup_errors=cleanup_errors,observed_process_identities=list(identities.values()),observed_source_groups=list(source_groups.values()),source_seen_after_time_exit=post_time_sources,source_groups_after_cleanup=source_groups_after(source_groups),remaining_exact_source_processes=exact_source_processes(spec),supervisor_own_observed_cpu_s=own_cpu()-supervisor_cpu0,supervisor_own_cost_boundary='Separate finite observation; not included in GNUtime child charge. Final supervisor record persistence still outside this sample.',external_supervision_qualified=False,independent_POST_required=True)
        payload['wall_CPU_caps_pass']=bool(timing_valid and envelope_valid and identity_unchanged and wall<=min(10.,3600.-spec['previous_r2_wall_s']) and cpu<=min(20.,7200.-spec['previous_r2_cpu_s']))
        payload['execution_cap_breach']=dict(wall=wall>10.,cpu=cpu>20.)
        payload['completed_process_exit0']=bool(proc is not None and proc.returncode==time_exit==0 and failure is None and watchdog_stop is None and not cleanup_errors and not post_time_sources and not payload['remaining_exact_source_processes'] and all(not g for g in payload['source_groups_after_cleanup'].values()))
        new_json(chargefile,payload)
    print(json.dumps(dict(external_charge=str(chargefile.relative_to(ROOT)),wall_s=wall,cpu_s=cpu,
        timing_valid=timing_valid,process_exit0=payload['completed_process_exit0'],independent_POST_required=True)))
    if not(payload['completed_process_exit0']and payload['wall_CPU_caps_pass']):raise SystemExit(1)


if __name__=='__main__':main()
