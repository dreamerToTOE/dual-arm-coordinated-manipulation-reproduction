#!/usr/bin/env python3
"""Exclusive outer GNUtime supervisor draft; no runner import or import effects."""
from pathlib import Path
from decimal import Decimal
import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
RUN='20261018_R2_D080_V_PCS_LOCAL01'
LABEL='CORRECTED_COMAU_APC_ALIGNED_V3_ORIGINAL_FIXED_PCS_RBS_CONTROL_RECONSTRUCTED_A02'
TIME=Path('/usr/bin/time')
PYTHON=Path('/usr/bin/python3')
RUNNER=ROOT/'scripts/p4_d080/qualify_v_pcs_local_v1_draft.py'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,reason):
    if not ok:raise RuntimeError(reason)
def new_json(p,value):
    with p.open('x')as stream:
        json.dump(value,stream,allow_nan=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
def child_cpu():
    r=resource.getrusage(resource.RUSAGE_CHILDREN);return r.ru_utime+r.ru_stime


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--protocol',required=True,type=Path)
    protocol=parser.parse_args().protocol.resolve();spec=json.loads(protocol.read_text())
    require(spec['run_id']==RUN and spec['classification']==LABEL and spec['frozen']is True
        and spec['schema']=='P4_D080_V_PCS_LOCAL_RUN_FROZEN_V1' and spec['environment']=='V'
        and spec['independent_review_passed']is True and spec['scientific_execution_authorized']is True
        and spec['formal_execution_authorized']is False and spec['budget']=={'wall_s':30,'cpu_s':60},'EXPLICIT_FROZEN_V_PCS_FIXED_LOCAL_REQUIRED')
    ext=spec['external_supervision'];prefix=ROOT/'results/p4_full'/RUN
    timefile=Path(str(prefix)+'.supervision.time.txt');metadata=Path(str(prefix)+'.supervision.jsonl')
    stderr=Path(str(prefix)+'.supervision.stderr.log');chargefile=Path(str(prefix)+'.supervision.charge.json')
    require(ext['sibling_path']==str(timefile.relative_to(ROOT))and ext['metadata_path']==str(metadata.relative_to(ROOT))
        and ext['stderr_path']==str(stderr.relative_to(ROOT))and ext['charge_path']==str(chargefile.relative_to(ROOT)),'EXACT_SUPERVISION_PATHS_REQUIRED')
    require(ext['format']=='%e %U %S %x'and ext['time_binary_sha256']==sha(TIME)and ext['python_binary_sha256']==sha(PYTHON),'EXACT_TIME_AND_PYTHON_REQUIRED')
    require(spec['bound_files_sha256'][str(Path(__file__).resolve())]==sha(__file__)
        and spec['bound_files_sha256'][str(RUNNER)]==sha(RUNNER),'FROZEN_SUPERVISOR_AND_RUNNER_REQUIRED')
    require(not prefix.exists()and not(ROOT/'results/p4_full'/('P4_D080_V_PCS_LOCAL01_FIXED_A02_PM005_30W60CPU_20261018.claim.json')).exists(),'OLD_RUN_OR_CLAIM_NO_RETRY')
    require(not any(p.exists()for p in(timefile,metadata,stderr,chargefile)),'OLD_SUPERVISION_ARTIFACT_NO_RETRY')
    # O_EXCL is the actual race-safe guard. GNUtime receives our already-open
    # inode via inheritedFD, never an overwrite-capable ordinary output path.
    fd=os.open(timefile,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    opened_identity=(os.fstat(fd).st_dev,os.fstat(fd).st_ino)
    meta=None;err=None;proc=None;attempted=False;begun=None;cpu0=None;failure=None
    try:
        meta=metadata.open('xb',buffering=0);err=stderr.open('xb',buffering=0)
        argv=[str(TIME),'--quiet','-f',ext['format'],'-o',f'/proc/self/fd/{fd}',str(PYTHON),str(RUNNER),'--protocol',str(protocol)]
        planned=dict(event='planned_launch',run_id=RUN,supervisor_pid=os.getpid(),supervisor_ppid=os.getppid(),
            supervisor_source_sha256=sha(__file__),protocol=str(protocol.relative_to(ROOT)),protocol_sha256=sha(protocol),
            runner_sha256=sha(RUNNER),time_binary_sha256=sha(TIME),python_binary_sha256=sha(PYTHON),argv=argv,
            time_fd=fd,time_inode=os.fstat(fd).st_ino,time_device=os.fstat(fd).st_dev,
            supervision_cost_boundary='GNUtime child local runner+two sequential reaped fixed V local sources. Supervisor own metadata/time-log fsync costs excluded.')
        meta.write(json.dumps(planned,allow_nan=False,separators=(',',':')).encode()+b'\n');meta.flush();os.fsync(meta.fileno())
        begun=time.monotonic();cpu0=child_cpu();attempted=True
        proc=subprocess.Popen(argv,cwd=ROOT,pass_fds=(fd,),stderr=err)
        meta.write(json.dumps(dict(event='time_process_started',pid=proc.pid,argv=argv),separators=(',',':')).encode()+b'\n');meta.flush()
        proc.wait()
    except BaseException as exc:
        failure=repr(exc)
        # This supervisor never starts a second time/runner after a failure.
        # If interrupted, allow the one finite30/60 child to reach its own STOP
        # and preserve/reap rather than orphaning a still-running experiment.
        if proc is not None and proc.returncode is None:proc.wait()
    finally:
        fallback_wall=0. if begun is None else time.monotonic()-begun
        fallback_cpu=0. if cpu0 is None else child_cpu()-cpu0
        current=timefile.stat();identity_unchanged=(current.st_dev,current.st_ino)==opened_identity
        os.fsync(fd);os.close(fd)
        if err is not None:err.flush();os.fsync(err.fileno());err.close()
        if meta is not None:
            meta.write(json.dumps(dict(event='time_process_reaped',pid=None if proc is None else proc.pid,
                returncode=None if proc is None else proc.returncode,failure=failure),separators=(',',':')).encode()+b'\n')
            meta.flush();os.fsync(meta.fileno());meta.close()
        execution=prefix/'execution.json';receipt=prefix/'cost_receipt.json'
        timing_valid=False;time_exit=None;wall=fallback_wall;cpu=fallback_cpu;fields=[]
        raw_wall=None;raw_cpu=None;envelope_valid=False;envelope_error=None;components=None
        try:
            fields=timefile.read_text().strip().split()
            if len(fields)!=4:raise ValueError('EXACT_FOUR_TIME_FIELDS_REQUIRED')
            elapsed,user,system=(Decimal(v)for v in fields[:3]);time_exit=int(fields[3])
            if not all(v.is_finite()and v>=0 for v in(elapsed,user,system)):raise ValueError('FINITE_NONNEGATIVE_TIME_FIELDS_REQUIRED')
            raw_wall=float(elapsed+Decimal('.01'));raw_cpu=float(user+system+Decimal('.02'));timing_valid=True
            wall=raw_wall;cpu=raw_cpu
        except (ValueError,ArithmeticError):pass
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
        except (ValueError,ArithmeticError):pass
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
        payload=dict(schema='P4_D080_V_PCS_LOCAL_EXTERNAL_COST_CHARGE_V1',run_id=RUN,
            source_execution=str(execution.relative_to(ROOT)),execution_sha256=sha(execution)if execution.is_file()else None,
            receipt=str(receipt.relative_to(ROOT)),receipt_sha256=sha(receipt)if receipt.is_file()else None,
            time_file=str(timefile.relative_to(ROOT)),time_sha256=sha(timefile),time_fields=fields,
            metadata=str(metadata.relative_to(ROOT)),metadata_sha256=sha(metadata)if metadata.is_file()else None,
            stderr=str(stderr.relative_to(ROOT)),stderr_sha256=sha(stderr)if stderr.is_file()else None,
            time_process_pid=None if proc is None else proc.pid,time_returncode=None if proc is None else proc.returncode,
            measured_child_exit=time_exit,started_attempt=attempted,wall_s=wall,cpu_s=cpu,
            charge_basis='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE',
            raw_GNUtime_upper_wall_s=raw_wall,raw_GNUtime_upper_cpu_s=raw_cpu,
            monotonic_envelope_valid=envelope_valid,monotonic_envelope_components=components,monotonic_envelope_error=envelope_error,
            timing_valid=timing_valid,time_inode_unchanged=identity_unchanged,
            fallback_observed_outer_wait_wall_s=fallback_wall,fallback_reaped_children_CPU_s=fallback_cpu,
            fallback_cost_completeness='UNQUALIFIED_FINITE_OBSERVATION_ONLY_IF_TIME_INVALID',
            cost_boundary='Effective prior charge replaces this execution pre-save cost, or charges orphan preflight attempt. Supervisor own journal/fsync cost excluded.',
            failure=failure,external_supervision_qualified=False,independent_POST_required=True)
        payload['wall_CPU_caps_pass']=bool(timing_valid and envelope_valid and identity_unchanged and wall<=min(30.,3600.-spec['prior']['wall_s']) and cpu<=min(60.,7200.-spec['prior']['cpu_s']))
        payload['execution_cap_breach']=dict(wall=wall>30.,cpu=cpu>60.)
        payload['completed_process_exit0']=bool(proc is not None and proc.returncode==time_exit==0 and failure is None)
        new_json(chargefile,payload)
    print(json.dumps(dict(external_charge=str(chargefile.relative_to(ROOT)),wall_s=wall,cpu_s=cpu,
        timing_valid=timing_valid,process_exit0=payload['completed_process_exit0'],independent_POST_required=True)))
    if not(payload['completed_process_exit0']and payload['wall_CPU_caps_pass']):raise SystemExit(1)


if __name__=='__main__':main()
