#!/usr/bin/env python3
"""DRAFT: fixed saved ABB arm2 branch roundtrip, mathematical gate only.

No work on import. Current draft protocol refuses execution. A reviewed frozen
protocol, current accounting snapshot and live external launcher receipt are
required. Native literal source is provenance, not this corrected runtime.
"""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import math
import os
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
IDS = ('II_obs0681', 'II_obs0689', 'III_obs1065', 'III_obs1073')
SCHEMA = 'P4_R2_ABB_RSS_FIXED32_BRANCH_MATH_V1'


def path(p):
    p = Path(p)
    return p if p.is_absolute() else ROOT/p


def sha(p):
    return hashlib.sha256(path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(path(p).read_text())


def require(ok, why):
    if not ok:
        raise RuntimeError(why)


def new(p, value):
    with Path(p).open('x') as f:
        json.dump(value, f, ensure_ascii=False, allow_nan=False, indent=2)
        f.write('\n')


def cpu():
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime


def execute(protocol, receipt):
    begun = time.monotonic(); cpu0 = cpu()
    spec = load(protocol); launch = load(receipt)
    require(spec['schema'] == SCHEMA and spec['frozen'] is True, 'FROZEN_REVIEWED_PROTOCOL_REQUIRED')
    require(spec['budget']['wall_s'] == 10 and spec['budget']['cpu_s'] == 20,
            'FIXED_10W_20CPU_ONLY')
    require(launch['parent_pid'] == os.getppid() and launch['protocol_sha256'] == sha(protocol)
            and launch['single_use'] is True and launch['worker_wall_s'] <= 10
            and launch['worker_cpu_s'] <= 20, 'LIVE_EXTERNAL_ONE_SHOT_ENVELOPE_REQUIRED')
    accounting = spec['accounting_snapshot']
    require(isinstance(accounting, dict) and sha(accounting['path']) == accounting['sha256'],
            'ROOT_LATEST_ACCOUNTING_FREEZE_REQUIRED')
    old = load(accounting['path'])
    require(old['r2_remaining']['wall_s'] >= 10 and old['r2_remaining']['cpu_s'] >= 20
            and old['vi_B_remaining']['candidate_constructions'] == 0,
            'R2_REMAINING_OR_VI_HISTORY_MISMATCH')
    require(tuple(c['case_id'] for c in spec['fixed_cases']) == IDS
            and spec['passive_branches_in_order'] == list(range(8))
            and spec['runtime_layer'] == 'GEOMETRY_CONSISTENT_CORRECTED'
            and spec['budget']['max_IK_calls'] == 32 and spec['budget']['max_explicit_source_F_calls'] == 4
            and spec['budget']['max_independent_arm_FK_J_calls'] == 40, 'FIXED32_INPUT_ORDER_REQUIRED')
    for p, expected in spec['bound_files_sha256'].items():
        require(sha(p) == expected, 'BOUND_INPUT_CHANGED '+p)
    for c in spec['fixed_cases']:
        obs = load(c['observations_path'])[c['observation_index0']]
        require(obs['candidate_q_rad'] == c['q12_rad']
                and obs['branch'] == c['original_arm1_construction_branch'] == 1,
                'ORIGINAL_Q12_OR_ARM1_IDENTITY_CHANGED')
    # Apply the cap before scientific imports; the launcher includes import and
    # worker recording tail in its external upper bound.
    def expired(*_):
        raise RuntimeError('FIXED32_WALL_STOP')
    previous = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, max(.001, 10-(time.monotonic()-begun)))
    folder = ROOT/'results/p4_full'/spec['run_id']
    folder.mkdir(parents=True, exist_ok=False)
    events = (folder/'evidence.jsonl').open('x', buffering=1)
    counts = Counter(); outcomes = []; processes = []; error = None
    def event(kind, **fields):
        events.write(json.dumps(dict(event=kind, **fields), allow_nan=False)+'\n')
        events.flush(); os.fsync(events.fileno())
    def budget():
        require(time.monotonic()-begun < 10 and cpu()-cpu0 < 20, 'FIXED32_RESOURCE_STOP')
    def request(env, text, label, is_ik):
        budget(); counts['IK_started' if is_ik else 'source_F_started'] += 1
        require(counts['IK_started'] <= 32 and counts['source_F_started'] <= 4, 'FIXED32_CALL_CAP')
        inp=folder/(label+'.input.txt'); out=folder/(label+'.stdout.txt')
        err=folder/(label+'.stderr.txt'); raw=folder/(label+'.native.jsonl')
        with inp.open('x') as f:f.write(text+'\n')
        command=[str(path(spec['ik_binary'])),str(raw),'--env',env]
        event('dispatch_started', label=label, input_sha256=sha(inp), command=command)
        proc=None
        try:
            with inp.open() as fi, out.open('x') as fo, err.open('x') as fe:
                proc=subprocess.Popen(command,stdin=fi,stdout=fo,stderr=fe,
                    cwd=ROOT,start_new_session=True)
                processes.append(dict(pid=proc.pid, label=label, reaped=False))
                event('source_process_started',pid=proc.pid,label=label)
                proc.wait(timeout=max(.001,10-(time.monotonic()-begun)))
        finally:
            if proc is not None:
                if proc.poll() is None:os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(); processes[-1].update(reaped=True,returncode=proc.returncode)
                event('source_process_reaped', **processes[-1])
        require(proc.returncode == 0, 'NATIVE_PROCESS_FAILED')
        saved=raw.read_bytes(); require(saved == out.read_bytes(), 'RAW_STDOUT_MISMATCH')
        rows=[json.loads(line) for line in saved.splitlines()]
        require(len(rows)==1 and rows[0]['environment']==env and rows[0]['error'] is None,
                'EXACT_ONE_RAW_RESPONSE_REQUIRED')
        counts['IK_completed' if is_ik else 'source_F_completed'] += 1
        event('dispatch_returned',label=label,raw_sha256=sha(raw),response=rows[0])
        budget(); return rows[0]
    record=dict(schema=SCHEMA,run_id=spec['run_id'],classification=spec['classification'],
        protocol=str(protocol),protocol_sha256=sha(protocol),launcher_receipt=str(receipt),
        launcher_receipt_sha256=sha(receipt),bound_files_sha256=spec['bound_files_sha256'],
        collision_checked=False,full_RSS_qualified=False,formal_table_I_calls=0,
        new_VI_candidate_constructions=0,zero_calls=dict(solve=0,RBS=0,NR=0,RNG=0,sampling=0,collision=0))
    try:
        for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
            os.environ[key]='1'
        sys.path.insert(0,str(ROOT))
        import numpy as np
        from baselines.p4_full.geometry_consistent.physical_nr import arm_fk_jac, model_geometry, source_limits
        from scripts.recover_p4_full_r2_endpoints import branch_identity
        def independent(q6, env, arm):
            counts['independent_arm_FK_J_started']+=1; require(counts['independent_arm_FK_J_started']<=40,'FK_J_CAP')
            event('independent_arm_FK_J_started',q6=q6,environment=env,arm=arm)
            value=arm_fk_jac(q6,env,arm);counts['independent_arm_FK_J_completed']+=1
            event('independent_arm_FK_J_completed',call=counts['independent_arm_FK_J_completed']);return value
        def rank(j):
            scaled=j.copy();scaled[:3]/=1000
            sigma=np.linalg.svd(scaled,compute_uv=False)
            return dict(rank=int(np.count_nonzero(sigma>sigma[0]*spec['gates']['rank_relative'])),
                        singular_values=sigma.tolist(),position_row_scaling='mm_to_m')
        def errors(a,b):
            d=a-b;return dict(position_maxabs_mm=float(np.max(np.abs(d[:3,3]))),rotation_maxabs=float(np.max(np.abs(d[:3,:3]))))
        def close(v):return v['position_maxabs_mm']<=1e-5 and v['rotation_maxabs']<=1e-5
        def fk_agrees(v):return v['position_maxabs_mm']<=1e-7 and v['rotation_maxabs']<=1e-10
        for case in spec['fixed_cases']:
            budget();env=case['environment'];q=case['q12_rad'];q1=q[:6];q2=q[6:]
            one,j1=independent(q1,env,1);two,j2=independent(q2,env,2)
            f=request(env,'F 1 '+' '.join(format(v,'.17g') for v in q1),case['case_id']+'_F1',False)
            require(f['op']=='F' and f['arm']==1 and f['q']==q1 and f['success'] and f['finite'], 'SOURCE_F1_INVALID')
            native1=np.asarray(f['T']);g=model_geometry(env)
            target=native1@g['grasps'][0]@np.diag([-1.,-1.,1.,1.])
            target_physical=one@g['grasps'][0]@np.diag([-1.,-1.,1.,1.])
            original=dict(case_id=case['case_id'],q12_rad=q,original_arm1_construction_branch=1,
                passive_branch_identity=branch_identity(q2,env,spec['gates']['branch_zero_relative_epsilon']),
                passive_rank=rank(j2),closure=errors(two,target_physical),source_F1_vs_independent=errors(native1,one),
                source_target=target.tolist(),physical_target=target_physical.tolist(),collision_saved_only=case['saved_collision'])
            new(folder/(case['case_id']+'.original_math.json'),original)
            for b in range(8):
                label=case['case_id']+'_arm2_b'+str(b)
                response=request(env,'K 2 '+str(b)+' '+' '.join(format(float(v),'.17g') for v in target.ravel()),label,True)
                require(response['op']=='K' and response['arm']==2 and response['branch']==b
                        and response['target']==target.tolist(),'FIXED_ARM2_BRANCH_OR_TARGET_CHANGED')
                row=dict(case_id=case['case_id'],passive_arm=2,requested_source_branch=b,
                    original_q12_rad=q,native_response=response,collision_checked=False,
                    collision_qualification='UNKNOWN_REQUIRES_SEPARATE_FROZEN_REPLAY',original_active_arm1_unchanged=True)
                if response['success']:
                    solved=response['solution'];require(response['finite'] and len(solved)==6 and all(math.isfinite(v)for v in solved),'NONFINITE_SOURCE_SUCCESS')
                    full=q1+solved;outpose,j=independent(solved,env,2);ident=branch_identity(solved,env,spec['gates']['branch_zero_relative_epsilon'])
                    delta=[x-y for x,y in zip(solved,q2)];closure=errors(outpose,target_physical);roundtrip=errors(outpose,target)
                    bounds=source_limits(env);qarr=np.asarray(full)
                    legality=bool(np.all((bounds[:,0]<=qarr)&(qarr<=bounds[:,1])))
                    membership=b in ident['branch_set'];r=rank(j)
                    fk_consistent=fk_agrees(errors(native1,one)) and fk_agrees(errors(np.asarray(response['T']),outpose))
                    row.update(output_q12_rad=full,passive_delta_rad=delta,raw_passive_L2_rad=math.sqrt(math.fsum(x*x for x in delta)),
                        same_original_passive_under_source_raw0p1=math.sqrt(math.fsum(x*x for x in delta))<.1,
                        branch_identity=ident,requested_branch_in_independent_set=membership,passive_rank=r,
                        closure=closure,physical_roundtrip=roundtrip,source_FK_vs_independent=errors(np.asarray(response['T']),outpose),
                        limits_legal=legality,qualified_math_only=close(closure)and close(roundtrip)and membership and legality and fk_consistent,
                        singular_math_only=close(closure)and close(roundtrip)and membership and legality and fk_consistent and r['rank']<6,
                        full_RSS_or_collision_qualified=False)
                else:row.update(qualified_math_only=False,singular_math_only=False,rejection='SOURCE_IK_FALSE_RETAINED')
                new(folder/(label+'.json'),row);outcomes.append(row)
                event('fixed_branch_finished',case_id=case['case_id'],branch=b,qualified_math_only=row['qualified_math_only'])
        require(counts['IK_started']==counts['IK_completed']==32 and len(outcomes)==32,'FIXED32_COMPLETION_REQUIRED')
        record['status']='FIXED32_MATH_RECORDED_COLLISION_UNKNOWN'
    except BaseException as exc:
        error=exc;record.update(status='STOP_PREFIX_RETAINED',termination_reason=repr(exc))
        event('stopped',termination_reason=repr(exc))
    finally:
        after={p:sha(p)for p in spec['bound_files_sha256']}
        record.update(counts=dict(counts),source_process_registry=processes,branch_results_retained=len(outcomes),
            uncompleted_branch_ids=[c['case_id']+'_arm2_b'+str(b)for c in spec['fixed_cases']for b in range(8)
                if not any(r['case_id']==c['case_id']and r['requested_source_branch']==b for r in outcomes)],
            bound_files_after_sha256=after,wall_s=time.monotonic()-begun,cpu_s=cpu()-cpu0,
            source_commit=launch['source_commit'])
        if after!=spec['bound_files_sha256']:record.update(status='STOP_BOUND_INPUT_CHANGED')
        event('final_counts',counts=dict(counts));events.close();new(folder/'execution.json',record)
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
    if error is not None:raise error


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--protocol',type=Path,required=True)
    p.add_argument('--external-launcher-receipt',type=Path,required=True)
    args=p.parse_args();execute(args.protocol.resolve(),args.external_launcher_receipt.resolve())


if __name__=='__main__':main()
