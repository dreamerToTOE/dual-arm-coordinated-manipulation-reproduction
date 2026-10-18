#!/usr/bin/env python3
"""DRAFT RSS fixed32 V2 GNUtime one-shot supervisor; no runner import."""
from pathlib import Path
from decimal import Decimal
import argparse
import hashlib
import json
import os
import resource
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
RUN='20261017_R2_ABB_RSS_BRANCH_MATH01'
LABEL='RECONSTRUCTED_FIXED_SAVED_INPUT_BRANCH_MAPPING_MATH_ONLY'
TIME=Path('/usr/bin/time')
PYTHON=Path('/usr/bin/python3')
RUNNER=ROOT/'scripts/qualify_p4_full_r2_abb_rss_branch_fixed32_supervised_v2_draft.py'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,reason):
    if not ok:raise RuntimeError(reason)
def new_json(p,value):
    with p.open('x')as stream:
        json.dump(value,stream,allow_nan=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    fd=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
def child_cpu():
    r=resource.getrusage(resource.RUSAGE_CHILDREN);return r.ru_utime+r.ru_stime
def own_cpu():
    r=resource.getrusage(resource.RUSAGE_SELF);return r.ru_utime+r.ru_stime
def absolute(p):
    p=Path(p);return p if p.is_absolute()else ROOT/p
def proc_table():
    rows={}
    for p in Path('/proc').glob('[0-9]*/stat'):
        try:
            fields=p.read_text().rsplit(')',1)[1].split();pid=int(p.parent.name)
            rows[pid]=dict(pid=pid,ppid=int(fields[1]),pgrp=int(fields[2]),start_ticks=int(fields[19]),state=fields[0],own_plus_reaped_children_cpu_s=sum(int(fields[i])for i in(11,12,13,14))/os.sysconf('SC_CLK_TCK'))
        except (OSError,ValueError,IndexError):pass
    return rows
def descendants(table,parent):
    found={parent};changed=True
    while changed:
        more={pid for pid,r in table.items()if r['ppid']in found};changed=bool(more-found);found.update(more)
    return {pid:table[pid]for pid in found if pid in table}
def exact_source_processes(spec):
    found=[];binary=absolute(spec['ik_binary']).resolve()
    for pid,row in proc_table().items():
        try:
            if Path('/proc',str(pid),'exe').resolve()==binary:found.append(row)
        except (OSError,RuntimeError):pass
    return found
def kill_source_identity(row):
    current=proc_table().get(row['pid'])
    if current is None:return
    require(current['start_ticks']==row['start_ticks'] and current['pgrp']==row['pid'],'SOURCE_PID_REUSE_OR_NONLEADER_REFUSE_KILL')
    try:os.killpg(row['pid'],signal.SIGKILL)
    except ProcessLookupError:pass
def source_groups_after(groups):
    table=proc_table();return {str(pid):[r for r in table.values()if r['pgrp']==pid]for pid in groups}
def stop_children(proc,spec,identities,groups):
    # Frozen native executable is the sole permitted source process. Discover
    # it globally as well as by ancestry, so worker death cannot hide orphans.
    for row in exact_source_processes(spec):groups[row['pid']]=row
    errors=[]
    for row in groups.values():
        try:kill_source_identity(row)
        except BaseException as exc:errors.append(repr(exc))
    table=proc_table()
    current_time=table.get(proc.pid)
    if current_time is not None and getattr(proc,'p4_start_ticks',current_time['start_ticks'])!=current_time['start_ticks']:
        raise RuntimeError('TIME_PROCESS_PID_REUSE_REFUSE_KILL')
    for pid,row in descendants(table,proc.pid).items():
        identities[pid]=row
        if pid==proc.pid:continue # retain GNUtime to write its actual receipt
        current=proc_table().get(pid)
        if current is not None and current['start_ticks']==row['start_ticks']:
            try:os.kill(pid,signal.SIGKILL)
            except ProcessLookupError:pass
            except BaseException as exc:errors.append(repr(exc))
    if errors:raise RuntimeError('STOP_CHILD_ERRORS '+repr(errors))
def watch(proc,spec,begun,cpu0,meta):
    identities={};groups={};stop=None;engineering=spec['supervision_engineering']
    while proc.poll()is None:
        table=proc_table();live=descendants(table,proc.pid)
        for pid,row in live.items():
            if pid not in identities:
                meta.write(json.dumps(dict(event='watchdog_actual_process_observed',process=row),separators=(',',':')).encode()+b'\n');meta.flush()
            identities[pid]=row
        for row in exact_source_processes(spec):groups[row['pid']]=row
        # Child times of reaped processes propagate up; summing the current
        # live tree is conservative during a non-atomic /proc observation.
        observed_cpu=child_cpu()-cpu0+sum(r['own_plus_reaped_children_cpu_s']for r in live.values())
        observed_wall=time.monotonic()-begun
        if observed_wall>=engineering['external_wall_kill_s'] or observed_cpu>=engineering['external_cpu_kill_s']:
            stop=dict(reason='EXTERNAL_LIVE_WALL_OR_CPU_STOP',observed_wall_s=observed_wall,observed_cpu_s=observed_cpu)
            meta.write(json.dumps(dict(event='watchdog_stop',**stop),separators=(',',':')).encode()+b'\n');meta.flush();os.fsync(meta.fileno())
            stop_children(proc,spec,identities,groups)
            try:proc.wait(timeout=.25)
            except subprocess.TimeoutExpired:
                # Actual time fields may then be incomplete; never certify a
                # fallback as complete. Retain the invalid raw time and cost.
                proc.kill();proc.wait(timeout=.25)
            break
        time.sleep(.01)
    return identities,groups,stop


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--protocol',required=True,type=Path)
    protocol=parser.parse_args().protocol.resolve();spec=json.loads(protocol.read_text())
    require(spec['schema']=='P4_R2_ABB_RSS_FIXED32_BRANCH_MATH_SUPERVISED_V2' and spec['run_id']==RUN and spec['classification']==LABEL and spec['frozen']is True
        and set(spec['reviews'])=={'independent_static_review_passed','root_freeze_approved','latest_actual_charged_prior_confirmed'} and all(type(v)is bool and v for v in spec['reviews'].values()),'EXPLICIT_FROZEN_RSS_FIXED32_V2_REQUIRED')
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
        try:
            fields=timefile.read_text().strip().split()
            if len(fields)!=4:raise ValueError('EXACT_FOUR_TIME_FIELDS_REQUIRED')
            elapsed,user,system=(Decimal(v)for v in fields[:3]);time_exit=int(fields[3])
            if not all(v.is_finite()and v>=0 for v in(elapsed,user,system)):raise ValueError('FINITE_NONNEGATIVE_TIME_FIELDS_REQUIRED')
            wall=float(elapsed+Decimal('.01'));cpu=float(user+system+Decimal('.02'));timing_valid=True
        except (ValueError,ArithmeticError,OSError):pass
        def retained_hash(p):
            try:return sha(p)if p.is_file()else None
            except BaseException as exc:cleanup_errors.append('retained_hash '+str(p)+' '+repr(exc));return None
        payload=dict(schema='P4_R2_ABB_RSS_FIXED32_SUPERVISED_V2_EXTERNAL_COST_CHARGE_V1',run_id=RUN,
            source_execution=str(execution.relative_to(ROOT)),execution_sha256=retained_hash(execution),
            receipt=str(receipt.relative_to(ROOT)),receipt_sha256=retained_hash(receipt),
            time_file=str(timefile.relative_to(ROOT)),time_sha256=retained_hash(timefile),time_fields=fields,
            metadata=str(metadata.relative_to(ROOT)),metadata_sha256=retained_hash(metadata),
            stderr=str(stderr.relative_to(ROOT)),stderr_sha256=retained_hash(stderr),
            time_process_pid=None if proc is None else proc.pid,time_returncode=None if proc is None else proc.returncode,
            measured_child_exit=time_exit,started_attempt=attempted,wall_s=wall,cpu_s=cpu,
            timing_valid=timing_valid,time_inode_unchanged=identity_unchanged,
            fallback_observed_outer_wait_wall_s=fallback_wall,fallback_reaped_children_CPU_s=fallback_cpu,
            fallback_cost_completeness='UNQUALIFIED_FINITE_OBSERVATION_ONLY_IF_TIME_INVALID',
            cost_boundary='Effective prior charge replaces this execution pre-save cost, or charges orphan preflight attempt. Supervisor own journal/fsync cost excluded.',
            failure=failure,watchdog_stop=watchdog_stop,watchdog_cleanup_errors=cleanup_errors,observed_process_identities=list(identities.values()),observed_source_groups=list(source_groups.values()),source_seen_after_time_exit=post_time_sources,source_groups_after_cleanup=source_groups_after(source_groups),remaining_exact_source_processes=exact_source_processes(spec),supervisor_own_observed_cpu_s=own_cpu()-supervisor_cpu0,supervisor_own_cost_boundary='Separate finite observation; not included in GNUtime child charge. Final supervisor record persistence still outside this sample.',external_supervision_qualified=False,independent_POST_required=True)
        payload['wall_CPU_caps_pass']=bool(timing_valid and identity_unchanged and wall<=min(10.,3600.-spec['previous_r2_wall_s']) and cpu<=min(20.,7200.-spec['previous_r2_cpu_s']))
        payload['completed_process_exit0']=bool(proc is not None and proc.returncode==time_exit==0 and failure is None and watchdog_stop is None and not cleanup_errors and not post_time_sources and not payload['remaining_exact_source_processes'] and all(not g for g in payload['source_groups_after_cleanup'].values()))
        new_json(chargefile,payload)
    print(json.dumps(dict(external_charge=str(chargefile.relative_to(ROOT)),wall_s=wall,cpu_s=cpu,
        timing_valid=timing_valid,process_exit0=payload['completed_process_exit0'],independent_POST_required=True)))
    if not(payload['completed_process_exit0']and payload['wall_CPU_caps_pass']):raise SystemExit(1)


if __name__=='__main__':main()
