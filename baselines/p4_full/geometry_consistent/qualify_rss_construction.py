"""Fixed-input RSS closure/rank qualification, never collision or path evidence."""
from __future__ import annotations
from collections import Counter
import datetime as dt
import json
from pathlib import Path
import subprocess
import numpy as np
from baselines.p4_full.geometry_consistent.run_qualification import (
    ROOT, PROTOCOL, RAW, Budget, Batch, dump_new, sha,
)
from baselines.p4_full.geometry_consistent.physical_nr import (
    arm_fk_jac, model_geometry, source_limits, residual_metrics,
)
from baselines.p4_full.geometry_consistent.rss_geometry import apply_mode

ADDENDUM=ROOT/'configs/p4_full/r2_rss_fixed_construction_addendum_v1.json'


def main():
    protocol=json.loads(PROTOCOL.read_text()); budget=Budget(protocol)
    spec=json.loads(ADDENDUM.read_text())
    out=ROOT/'results/p4_full'/spec['run_id'];out.mkdir(parents=True,exist_ok=False)
    previous=ROOT/'results/p4_full/20261015_R2_SPATIAL01'
    used_wall=used_cpu=0.
    for rid in spec['prior_runs']:
        r=json.loads((ROOT/'results/p4_full'/rid/'execution.json').read_text())
        used_wall+=r['wall_s'];used_cpu+=r['cpu_s']
    budget.p=dict(budget.p)
    budget.p['total_execution_wall_s']-=used_wall
    budget.p['total_cpu_s']-=used_cpu
    record={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'git_status_at_start':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),
            'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'protocol_sha256':sha(PROTOCOL),'addendum_sha256':sha(ADDENDUM),
            'previous_wall_s':used_wall,'previous_cpu_s':used_cpu,'models':[],
            'formal_planning_calls':0,'collision_queries':0,'new_rng_draws':0,
            'classification':'DETERMINISTIC_STRATIFIED_COMPONENT_INPUTS_NOT_RSS_DISTRIBUTION_TRIALS'}
    try:
        for env in spec['environments']:
            model='abb' if env in ('II','III') else 'comau_v'
            executable=ROOT/'build/p4_full/20261015_R2_SPATIAL01'/(model+'_batch')
            folder=out/env;folder.mkdir();batch=Batch(executable,env,folder,budget)
            path=ROOT/'results/p4_full'/RAW[env]
            if env in ('II','III'):
                source=json.loads(path.read_text())['rows']
                inputs=[(r['index'],r['q']) for r in source if r['kind']=='fk']
                modes=[0,1,2];family='ABB'
            else:
                source=[json.loads(s) for s in path.read_text().splitlines()]
                inputs=[(r['sample'],r['q_rad'][6:12]) for r in source if r['type']=='fk_sample']
                modes=[1];family='COMAU'
            assert len(inputs)==100
            requests=[];tags=[]
            g=model_geometry(env);S=np.diag([-1.,-1.,1.,1.])
            for idx, raw_q in inputs:
                for mode in modes:
                    qp=apply_mode(raw_q,family,mode)
                    tp,jp=arm_fk_jac(qp,env,2)
                    scaled=jp.copy();scaled[:3]/=1000
                    sigma=np.linalg.svd(scaled,compute_uv=False)
                    rank=int(np.sum(sigma>sigma[0]*1e-6))
                    target=tp@S@np.linalg.inv(g['grasps'][0])
                    for branch in range(8):
                        requests.append(('K',1,branch,target))
                        tags.append((idx,mode,branch,raw_q,qp,rank,sigma,target))
            rows=batch(requests)
            counts=Counter();qualified_targets=set();checks=[];observations=[]
            for tag,row in zip(tags,rows):
                budget.remaining()
                idx,mode,branch,raw_q,qp,rank,sigma,target=tag
                counts['branch_attempts']+=1;counts['mode'+str(mode)+'_branch_attempts']+=1
                reasons=[];q=None;metrics=None;bounds_legal=False
                if rank>=6:reasons.append('PASSIVE_FULL_RANK')
                if not row['success']:reasons.append('ACTIVE_IK_REJECTED')
                else:
                    q=np.r_[row['solution'],qp]
                    bounds=source_limits(env)
                    bounds_legal=bool(np.all((bounds[:,0]<=q)&(q<=bounds[:,1])))
                    metrics=residual_metrics(q,env)
                    if not bounds_legal:reasons.append('JOINT_LIMIT_REJECTED')
                    if metrics['translation_max_abs']>1e-5 or metrics['rotation_matrix_max_abs']>1e-5:
                        reasons.append('PHYSICAL_CLOSURE_REJECTED')
                    counts['active_ik_accepted']+=1
                qualified=not reasons
                if qualified:
                    qualified_targets.add((idx,mode));counts['qualified_branch_candidates']+=1
                for reason in reasons:counts[reason]+=1
                observations.append({'source_index':idx,'mode':mode,'branch':branch,
                    'source_passive_q_rad':raw_q,'forced_passive_q_rad':qp.tolist(),
                    'passive_rank':rank,'scaled_passive_singular_values':sigma.tolist(),
                    'active_target':target.tolist(),'native_active_ik':row,
                    'candidate_q_rad':q.tolist() if q is not None else None,
                    'physical_metrics':metrics,'source_joint_limits_legal':bounds_legal,
                    'qualified_closure_rank_bounds_only':qualified,'rejection_reasons':reasons,
                    'collision_checked':False,'RBS_or_branch_bridge_checked':False})
                # A returned accepted IK must be sound; expected geometric
                # rejection is counted, never treated as a solver bug.
                checks.append({'check':f'sound_{idx}_{mode}_{branch}',
                    'passed':not row['success'] or ('PHYSICAL_CLOSURE_REJECTED' not in reasons),
                    'detail':reasons})
            for mode in modes:
                found=sum(m==mode for _,m in qualified_targets)
                counts['mode'+str(mode)+'_qualified_targets']=found
                checks.append({'check':'at_least_one_closed_singular_target_mode'+str(mode),
                               'passed':found>0,'qualified_targets':found,'fixed_inputs':100})
            summary={'environment':env,'fixed_passive_targets':100*len(modes),
                     'qualified_passive_targets':len(qualified_targets),'counts':dict(counts),
                     'checks':len(checks),'passed':sum(c['passed'] for c in checks),
                     'failed':sum(not c['passed'] for c in checks),'source_sha256':sha(path),
                     'binary_sha256':sha(executable),'collision_checked':False,
                     'RBS_or_branch_bridge_checked':False,'formal_planning_calls':0}
            dump_new(folder/'observations.json',observations)
            dump_new(folder/'checks.json',checks);dump_new(folder/'summary.json',summary)
            record['models'].append(summary)
            print(json.dumps(summary),flush=True)
        record['status']='FIXED_COMPONENT_CONSTRUCTION_RECORDED'
    except Exception as error:
        record['status']='STOP';record['error']=repr(error);raise
    finally:
        import time
        record['wall_s']=time.monotonic()-budget.started
        record['cpu_s']=budget.cpu()-budget.cpu_start
        record['cumulative_execution_wall_s']=used_wall+record['wall_s']
        record['cumulative_execution_cpu_s']=used_cpu+record['cpu_s']
        record['ended_at_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
        dump_new(out/'execution.json',record)


if __name__=='__main__':main()
