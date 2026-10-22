#!/usr/bin/env python3
"""Independently qualify saved D081 20R paths; never invoke a planner.

Geometry is reconstructed explicitly with NumPy segment arithmetic. No import
of the production model, strategy, planner, Shapely or GEOS is permitted here.
Each saved RBS leaf receives two additional recursive midpoint levels, using
independent analytic 3R closure for PCS or independent full-Jacobian NR for NR.
This is finite discrete qualification, not continuous collision detection.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
from collections import Counter
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'results/20261019_D081_stability_pilot'
DEFAULT_OUTPUT = ROOT / 'results/20261022_D082_independent_planar01'
LENGTH = math.sin(math.pi / 38.0)
LENGTHS = np.r_[np.full(19, LENGTH), 0.0]
LINK_RADIUS = .002
POS_TOL = ANGLE_TOL = 1e-8
BRANCH_EPS = 1e-10
ENVIRONMENTS = {'E0_sparse': ((.45, .72, .045),),
                'E1_clutter': ((.45, .72, .045), (.50, .18, .065), (.72, .60, .05))}
PAIR_I, PAIR_J = np.array([(i,j) for i in range(20) for j in range(i+1,20)
                           if j != i+1 and (i,j) != (0,19)], dtype=int).T
START = np.full(20, -math.pi/19)
START[0] = START[19] = math.pi/2 - math.pi/38
GOAL = START.copy()
GOAL[16:19] = (-2*math.pi/19, math.pi/19, -2*math.pi/19)
WALL_START = time.perf_counter()
CPU_START = time.process_time()


def guard():
    if time.perf_counter()-WALL_START > 175 or time.process_time()-CPU_START > 175:
        raise RuntimeError('175 second internal compute budget reached; stop without planner calls')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)+'\n')


def wrap(x):
    return (np.asarray(x)+math.pi) % (2*math.pi)-math.pi


def fk(q):
    """Independent closed-chain convention: 19 moving links plus ground B->A."""
    q = np.asarray(q, dtype=float)
    theta = np.cumsum(q, axis=-1)
    steps = LENGTH * np.stack([np.cos(theta[...,:19]), np.sin(theta[...,:19])],axis=-1)
    origin = np.zeros(q.shape[:-1]+(1,2))
    vertices = np.concatenate([origin, np.cumsum(steps,axis=-2)],axis=-2)
    residual = np.concatenate([vertices[...,-1,:]-[1.,0.], wrap(theta[...,-1])[...,None]],axis=-1)
    return vertices, residual


def point_segment_distance(p, a, b):
    """Broadcast Euclidean distance, including degenerate segments."""
    v = b-a
    vv = np.sum(v*v,axis=-1)
    numerator = np.sum((p-a)*v,axis=-1)
    t = np.divide(numerator, vv, out=np.zeros_like(numerator), where=vv>0)
    t = np.clip(t,0.,1.)
    return np.linalg.norm(p-(a+t[...,None]*v),axis=-1)


def cross(a,b):
    return a[...,0]*b[...,1]-a[...,1]*b[...,0]


def segment_distance(a,b,c,d):
    """2D exact finite-segment cases plus endpoint distances; no GEOS calls.

    A nonparallel line intersection has distance zero iff its two parameters
    lie in [0,1]. Collinear overlap/degenerate cases are covered by the minimum
    of four endpoint-to-segment distances. No geometric clearance epsilon is
    added to the scientific collision boundary.
    """
    u,v,w = b-a,d-c,c-a
    denom = cross(u,v)
    t = np.divide(cross(w,v),denom,out=np.full_like(denom,np.inf),where=denom!=0)
    s = np.divide(cross(w,u),denom,out=np.full_like(denom,np.inf),where=denom!=0)
    intersects = (denom!=0)&(t>=0)&(t<=1)&(s>=0)&(s<=1)
    minimum = np.minimum.reduce([point_segment_distance(a,c,d),point_segment_distance(b,c,d),
                                  point_segment_distance(c,a,b),point_segment_distance(d,a,b)])
    return np.where(intersects,0.,minimum)


def geometry(q, env):
    q = np.asarray(q,dtype=float)
    if q.ndim != 2 or q.shape[1] != 20 or not np.isfinite(q).all():
        raise ValueError('finite Nx20 state array required')
    vertices,residual = fk(q)
    n = len(q)
    a = np.concatenate([vertices[:,:-1,:],np.broadcast_to([1.,0.],(n,1,2))],axis=1)
    b = np.concatenate([vertices[:,1:,:],np.zeros((n,1,2))],axis=1)
    self_clear = segment_distance(a[:,PAIR_I],b[:,PAIR_I],a[:,PAIR_J],b[:,PAIR_J])-2*LINK_RADIUS
    obs = np.array(ENVIRONMENTS[env],dtype=float)
    obstacle_clear = point_segment_distance(obs[None,:,None,:2],a[:,None,:,:],b[:,None,:,:])-obs[None,:,None,2]-LINK_RADIUS
    return {'position':np.linalg.norm(residual[:,:2],axis=1), 'angle':np.abs(residual[:,2]),
            'joint_margin':np.min(math.pi-np.abs(q),axis=1),
            'self_clearance':np.min(self_clear,axis=1),
            'obstacle_clearance':np.min(obstacle_clear,axis=(1,2)),
            'clearance':np.minimum(np.min(self_clear,axis=1),np.min(obstacle_clear,axis=(1,2)))}


def aggregate(values):
    return {'point_count':len(values['position']),
            'maximum_position_residual_m':float(max(values['position'])),
            'maximum_angle_residual_rad':float(max(values['angle'])),
            'minimum_joint_margin_rad':float(min(values['joint_margin'])),
            'minimum_self_clearance_m':float(min(values['self_clearance'])),
            'minimum_obstacle_clearance_m':float(min(values['obstacle_clearance'])),
            'minimum_clearance_m':float(min(values['clearance'])),
            'closure_failures':int(np.count_nonzero((values['position']>POS_TOL)|(values['angle']>ANGLE_TOL))),
            'joint_limit_failures':int(np.count_nonzero(values['joint_margin']<0)),
            'collision_failures':int(np.count_nonzero(values['clearance']<=0))}


def branch(q,p):
    s = np.sin(np.asarray(q)[...,p+1])
    return np.where(np.abs(s)<=BRANCH_EPS,0,np.sign(s)).astype(int)


def block_pose(q, lengths):
    angles = np.cumsum(q)
    return np.array([np.dot(lengths,np.cos(angles)),np.dot(lengths,np.sin(angles))]), float(sum(q))


def rotate(v, angle):
    c,s=math.cos(angle),math.sin(angle)
    return np.array([c*v[0]-s*v[1],s*v[0]+c*v[1]])


def analytic_close(seed,p,b):
    """Solve the selected 3R chart through independent 2D pose composition."""
    pre,pre_angle=block_pose(seed[:p],LENGTHS[:p])
    post,post_angle=block_pose(seed[p+3:],LENGTHS[p+3:])
    phi = float(wrap(-pre_angle-post_angle))
    required=rotate(np.array([1.,0.])-pre,-pre_angle)-rotate(post,phi)
    wrist=required-LENGTH*np.array([math.cos(phi),math.sin(phi)])
    c=(float(np.dot(wrist,wrist))-2*LENGTH*LENGTH)/(2*LENGTH*LENGTH)
    if abs(c)>1+1e-12:
        raise ValueError('independent chart midpoint unreachable')
    q2=(1 if b>=0 else -1)*math.acos(min(1.,max(-1.,c)))
    q1=math.atan2(wrist[1],wrist[0])-math.atan2(LENGTH*math.sin(q2),LENGTH*(1+math.cos(q2)))
    result=seed.copy()
    result[p:p+3]=wrap([q1,q2,phi-q1-q2])
    return result


def nr_close(seed, cfg):
    """Independent NR of paper Sec.II.B.2, using full 3x20 Jacobian/SVD."""
    q=seed.copy()
    for k in range(int(cfg['nr_max_iterations'])+1):
        _,res=fk(q)
        if np.linalg.norm(res[:2])<=POS_TOL and abs(res[2])<=ANGLE_TOL:
            return q,k
        if k==cfg['nr_max_iterations']:
            raise ValueError('independent NR midpoint did not converge')
        angles=np.cumsum(q)
        dx=-LENGTHS*np.sin(angles)
        dy=LENGTHS*np.cos(angles)
        j=np.array([np.cumsum(dx[::-1])[::-1],np.cumsum(dy[::-1])[::-1],np.ones(20)])
        u,s,vt=np.linalg.svd(j,full_matrices=False)
        cutoff=max(cfg['svd_absolute_cutoff'],cfg['svd_relative_cutoff']*s[0])
        inv=np.divide(1.,s,out=np.zeros_like(s),where=s>cutoff)
        delta=-(vt.T@(inv*(u.T@res)))
        q=wrap(q+delta)
    raise AssertionError('unreachable')


def refine(a,b,partition,branch_label,cfg,levels=2):
    if levels==0:
        return [a,b],0
    seed=(a+b)/2
    if partition is None:
        mid,updates=nr_close(seed,cfg)
    else:
        mid=analytic_close(seed,partition,branch_label)
        updates=0
    left,lu=refine(a,mid,partition,branch_label,cfg,levels-1)
    right,ru=refine(mid,b,partition,branch_label,cfg,levels-1)
    return left+right[1:],updates+lu+ru


def assert_equal(a,b,message):
    if not np.array_equal(np.asarray(a),np.asarray(b)):
        raise AssertionError(message)


def ancestry(d,side,node):
    result=[]
    tree=d['trees'][side]
    while tree[node]['parent'] is not None:
        result.append(tree[node]['incoming_attempt'])
        node=tree[node]['parent']
    return list(reversed(result))


def validate_provenance(d):
    assert_equal(d['start'],START,'model start changed')
    assert_equal(d['goal'],GOAL,'model goal changed')
    assert_equal(d['path'][0],START,'path exact start mismatch')
    assert_equal(d['path'][-1],GOAL,'path exact goal mismatch')
    a,b=d['meeting']
    assert_equal(d['trees']['START'][a]['q'],d['trees']['GOAL'][b]['q'],'meeting mismatch')
    left=ancestry(d,'START',a)
    right=list(reversed(ancestry(d,'GOAL',b)))
    expected=[(i,'START',False) for i in left]+[(i,'GOAL',True) for i in right]
    actual=[(e['attempt_index'],e['tree'],e['reversed']) for e in d['path_edges']]
    if actual!=expected:
        raise AssertionError('path tree ancestry mismatch')
    reconstructed=[d['start']]
    milestones=[d['start']]
    leaf_count=0
    max_distance_error=0.
    edge_records=[]
    for e in d['path_edges']:
        at=d['attempts'][e['attempt_index']]
        conn=at['connection']
        if not at['accepted'] or not conn['success'] or at['tree']!=e['tree']:
            raise AssertionError('path edge not an accepted tree edge')
        if e['partition']!=conn['partition'] or e['branch']!=conn['branch']:
            raise AssertionError('path edge chart metadata mismatch')
        child=d['trees'][e['tree']][at['added_node']]
        parent=d['trees'][e['tree']][at['nearest_node']]
        if child['parent']!=at['nearest_node'] or child['incoming_attempt']!=e['attempt_index']:
            raise AssertionError('tree parent metadata mismatch')
        assert_equal(parent['q'],conn['path'][0],'edge parent mismatch')
        assert_equal(child['q'],conn['path'][-1],'edge child mismatch')
        successes=[t for t in conn['trials'] if t['success']]
        if len(successes)!=1:
            raise AssertionError('expected exactly one successful connection trial')
        t=successes[0]
        if (t['partition'],t['branch'])!=(e['partition'],e['branch']):
            raise AssertionError('trial chart metadata mismatch')
        ids=t['verified_prefix_indices']
        assert_equal([t['checked_points'][i]['q'] for i in ids],conn['path'],'RBS point provenance mismatch')
        if len(ids)!=len(t['checked_points']) or set(ids)!=set(range(len(ids))):
            raise AssertionError('successful trial has unchecked/unordered saved points')
        leaves=t['leaf_edges']
        if [(x['from'],x['to']) for x in leaves]!=list(zip(ids[:-1],ids[1:])):
            raise AssertionError('saved RBS leaf topology mismatch')
        edge=np.array(conn['path'])
        dist=np.linalg.norm(np.diff(edge,axis=0),axis=1)
        if len(leaves)!=len(dist) or any(not x['qualified'] for x in leaves):
            raise AssertionError('leaf count/qualification mismatch')
        if np.any(dist>d['config']['rbs_resolution_rad']):
            raise AssertionError('saved RBS leaf exceeds declared resolution')
        error=max(abs(float(x['distance_rad'])-float(v)) for x,v in zip(leaves,dist))
        max_distance_error=max(max_distance_error,error)
        if error>2e-15:
            raise AssertionError('saved leaf distance metadata mismatch')
        if e['partition'] is not None:
            branches=branch(edge,e['partition'])
            if np.any((branches!=0)&(branches!=e['branch'])):
                raise AssertionError('saved edge branch mismatch')
        if e['reversed']:
            edge=edge[::-1]
        assert_equal(reconstructed[-1],edge[0],'adjacent solution edges mismatch')
        reconstructed.extend(edge[1:].tolist())
        milestones.append(edge[-1].tolist())
        if e['point_count']!=len(edge):
            raise AssertionError('edge point count mismatch')
        leaf_count+=len(leaves)
        edge_records.append((e,edge))
    assert_equal(reconstructed,d['path'],'ordered path composition mismatch')
    assert_equal(milestones,d['path_milestones'],'milestone provenance mismatch')
    return edge_records,leaf_count,max_distance_error


def negative_fixtures(payloads):
    fixtures=[]
    def test(name,actual,expected):
        ok=bool(actual==expected)
        fixtures.append({'name':name,'actual':actual,'expected':expected,'passed':ok})
        if not ok:
            raise AssertionError('oracle fixture failed '+name)
    for name,coords,expected in [
        ('segments_cross',[[0.,0.],[1.,1.],[0.,1.],[1.,0.]],0.),
        ('segments_parallel',[[0.,0.],[1.,0.],[0.,2.],[1.,2.]],2.),
        ('segments_collinear_overlap',[[0.,0.],[2.,0.],[1.,0.],[3.,0.]],0.),
        ('segments_collinear_disjoint',[[0.,0.],[1.,0.],[2.,0.],[3.,0.]],1.),
        ('segments_degenerate',[[0.,0.],[0.,0.],[1.,0.],[3.,0.]],1.)]:
        test(name,float(segment_distance(*np.array(coords))),expected)
    test('circle_exact_tangent_collides',bool(point_segment_distance(np.array([.5,.25]),np.array([0.,0.]),np.array([1.,0.]))-.25<=0),True)
    test('circle_above_tangent_clear',bool(point_segment_distance(np.array([.5,.250001]),np.array([0.,0.]),np.array([1.,0.]))-.25>0),True)
    pos=aggregate(geometry(START[None,:],'E0_sparse'))
    test('known_exact_start_qualifies',bool(pos['closure_failures']==pos['joint_limit_failures']==pos['collision_failures']==0),True)
    altered=START.copy();altered[19]+=1e-4
    test('terminal_angle_perturbation_rejected',bool(aggregate(geometry(altered[None,:],'E0_sparse'))['closure_failures']==1),True)
    altered=START.copy();altered[0]=math.pi+.01
    test('joint_bound_violation_rejected',bool(aggregate(geometry(altered[None,:],'E0_sparse'))['joint_limit_failures']==1),True)
    fixture_source=None
    for f,d in payloads:
        for a in d['attempts']:
            for t in (a.get('connection') or {}).get('trials',[]):
                for i,cp in enumerate(t['checked_points']):
                    if cp.get('q') is not None and (cp.get('qualification',{}).get('collision') or {}).get('collision'):
                        result=aggregate(geometry(np.array([cp['q']]),d['environment']))
                        test('saved_closed_collision_rejected',bool(result['collision_failures']==1 and result['closure_failures']==0 and result['joint_limit_failures']==0),True)
                        fixture_source={'artifact':str(f.relative_to(ROOT)),'sha256':sha(f),'attempt_index':a['attempt_index'],
                                        'trial_partition':t['partition'],'checked_point_index':i,'q':cp['q'],'independent_result':result}
                        return {'checks':fixtures,'saved_collision_fixture':fixture_source,'all_passed':True}
    raise AssertionError('no saved collision negative fixture available')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    output=args.output.resolve()
    if output.exists():
        raise SystemExit('Refusing to overwrite '+str(output))
    output.mkdir(parents=True)
    (output/'dense_paths').mkdir()
    files=sorted((INPUT/'raw_planner').glob('*.json.gz'))
    evidence_files=files+[INPUT/x for x in ['artifact_sha256.json','config_snapshot.json','run_metadata.json','planner_summary.json','planner_trials.csv']]
    initial_hashes={str(f.relative_to(ROOT)):sha(f) for f in evidence_files}
    original_manifest=json.loads((INPUT/'artifact_sha256.json').read_text())
    original_manifest_matches={k:sha(INPUT/k)==v for k,v in original_manifest.items()}
    if not all(original_manifest_matches.values()):
        raise AssertionError('original input manifest mismatch')
    metadata=json.loads((INPUT/'run_metadata.json').read_text())
    production_source={k:{'saved_sha256':v,'current_sha256':sha(ROOT/k),'matches':v==sha(ROOT/k)} for k,v in metadata['source_files'].items()}
    if not all(x['matches'] for x in production_source.values()):
        raise AssertionError('production source changed since saved pilot')
    payloads=[(f,json.load(gzip.open(f,'rt'))) for f in files]
    fixture=negative_fixtures(payloads)
    save(output/'oracle_fixtures.json',fixture)
    results=[]
    counts=Counter()
    dense_points=0
    all_saved=0
    leaf_total=0
    new_total=0
    for f,d in payloads:
        guard()
        counts[(d['environment'],d['method'],d['status'])]+=1
        if d['status']!='SUCCESS':
            continue
        edges,leaves,meta_error=validate_provenance(d)
        path=np.array(d['path'],dtype=float)
        saved_values=geometry(path,d['environment'])
        saved_result=aggregate(saved_values)
        dense=[path[0]]
        segment_charts=[]
        nr_updates=0
        branch_failures=0
        edge_summaries=[]
        for e,edge in edges:
            edge_dense=[edge[0]]
            for a,b in zip(edge[:-1],edge[1:]):
                points,updates=refine(a,b,e['partition'],e['branch'],d['config'])
                nr_updates+=updates
                edge_dense.extend(points[1:])
            edge_dense=np.array(edge_dense)
            if e['partition'] is not None:
                bs=branch(edge_dense,e['partition'])
                branch_failures+=int(np.count_nonzero((bs!=0)&(bs!=e['branch'])))
            dense.extend(edge_dense[1:])
            segment_charts.extend([{'partition':e['partition'],'branch':e['branch'],'attempt_index':e['attempt_index']} for _ in range(len(edge_dense)-1)])
            edge_summaries.append({'attempt_index':e['attempt_index'],'partition':e['partition'],'branch':e['branch'],
                                   'saved_point_count':len(edge),'dense_point_count':len(edge_dense),
                                   'reversed':e['reversed'],'tree':e['tree']})
        dense=np.array(dense)
        dense_values=geometry(dense,d['environment'])
        dense_result=aggregate(dense_values)
        all_saved+=len(path);leaf_total+=leaves;dense_points+=len(dense);new_total+=len(dense)-len(path)
        selected=[e['partition'] for e in d['path_edges'] if e['partition'] is not None]
        switches=sum(a!=b for a,b in zip(selected[:-1],selected[1:]))
        lengths=np.linalg.norm(np.diff(path,axis=0),axis=1)
        dense_lengths=np.linalg.norm(np.diff(dense,axis=0),axis=1)
        source_clear=np.array([x['collision']['minimum_clearance'] for x in d['path_metrics']['state_qualifications']])
        clearance_delta=float(np.max(np.abs(source_clear-saved_values['clearance'])))
        name=f.name.removesuffix('.json.gz')
        dense_path=output/'dense_paths'/f'{name}.npz'
        np.savez_compressed(dense_path,q=dense,position_residual_m=dense_values['position'],angle_residual_rad=dense_values['angle'],
                            joint_margin_rad=dense_values['joint_margin'],self_clearance_m=dense_values['self_clearance'],
                            obstacle_clearance_m=dense_values['obstacle_clearance'],
                            partition=np.array([-1 if x['partition'] is None else x['partition'] for x in segment_charts]),
                            branch=np.array([0 if x['branch'] is None else x['branch'] for x in segment_charts]),
                            attempt_index=np.array([x['attempt_index'] for x in segment_charts]))
        qualified=bool(not branch_failures and all(saved_result[k]==0 and dense_result[k]==0 for k in ['closure_failures','joint_limit_failures','collision_failures']))
        record={'artifact':str(f.relative_to(ROOT)),'input_sha256':initial_hashes[str(f.relative_to(ROOT))],
                'environment':d['environment'],'method':d['method'],'seed':d['seed'],'independently_qualified':qualified,
                'exact_start_goal':True,'tree_edge_and_RBS_provenance':True,'saved_leaf_count':leaves,
                'saved_leaf_maximum_metadata_distance_error_rad':meta_error,
                'saved':saved_result,'dense':dense_result,'added_midpoints':len(dense)-len(path),
                'saved_path_length_rad':float(sum(lengths)),'dense_path_length_rad':float(sum(dense_lengths)),
                'maximum_saved_step_rad':float(max(lengths)),'maximum_dense_step_rad':float(max(dense_lengths)),
                'solution_partitions':selected,'genuine_solution_partition_switches':switches,
                'dense_branch_mismatches':branch_failures,'independent_NR_updates':nr_updates,
                'maximum_saved_clearance_difference_from_GEOS_m':clearance_delta,
                'dense_artifact':str(dense_path.relative_to(ROOT)),'dense_sha256':sha(dense_path),'edges':edge_summaries}
        results.append(record)
        save(output/f'{name}_qualification.json',record)
        print(json.dumps({k:record[k] for k in ['environment','method','seed','independently_qualified','added_midpoints','genuine_solution_partition_switches']}),flush=True)
    unchanged={k:sha(ROOT/k)==v for k,v in initial_hashes.items()}
    source_paths=[Path(__file__),ROOT/'baselines/p4_comparison/model.py',ROOT/'baselines/p4_comparison/strategies.py',ROOT/'baselines/p4_comparison/planner.py',ROOT/'configs/p4_d081/numeric_pilot_v1.json',ROOT/'configs/p4_d081/numeric_stability_pilot_v1.json']
    successful=len(results)
    all_pass=all(r['independently_qualified'] for r in results) and all(unchanged.values()) and successful==26
    summary={'schema':'P4_D082_INDEPENDENT_SAVED_PLANAR_DISCRETE_QUALIFICATION_V1',
             'status':'PASS_DISCRETE_WITH_STRATEGY_MIDPOINT_REFINEMENT' if all_pass else 'FAIL_PRESERVED',
             'scope':'RECONSTRUCTED_20R_PLANAR_D081_STABILITY_PILOT_ONLY',
             'input_trial_count':len(payloads),'source_success_count':successful,'independent_qualified_count':sum(r['independently_qualified'] for r in results),
             'source_outcomes':[{'environment':a,'method':b,'status':c,'count':n} for (a,b,c),n in sorted(counts.items())],
             'saved_path_points':all_saved,'saved_RBS_leaves':leaf_total,'additional_reconstructed_midpoints':new_total,
             'dense_path_points':dense_points,'refinement_levels_per_saved_leaf':2,
             'position_tolerance_m':POS_TOL,'angle_tolerance_rad':ANGLE_TOL,'joint_limits_rad':[-math.pi,math.pi],
             'link_capsule_radius_m':LINK_RADIUS,'self_collision_pair_count':len(PAIR_I),'obstacle_circles':ENVIRONMENTS,
             'total_genuine_solution_partition_switches':sum(r['genuine_solution_partition_switches'] for r in results),
             'all_saved_solution_PCS_partitions':sorted(set(p for r in results for p in r['solution_partitions'])),
             'oracle_fixtures_passed':fixture['all_passed'],'original_manifest_all_match':all(original_manifest_matches.values()),
             'input_files_unchanged':all(unchanged.values()),'input_hashes':initial_hashes,
             'production_sources_match_saved_metadata':production_source,
             'verifier_source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in source_paths},
             'paper_original_sha256':sha(ROOT/'references/private_sources/P4_original.pdf'),
             'paper_reading_basis':'Full local manuscript read in current root session; pp.2-3 equations1-3 and RBS; pp.3-4 passive branches/PCS; pp.5-8 experimental scope.',
             'git_head_at_execution':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),
             'command':'python3 scripts/p4_d082/independent_planar_validation.py --output results/20261022_D082_independent_planar01',
             'wall_sec':time.perf_counter()-WALL_START,'process_cpu_sec':time.process_time()-CPU_START,
             'new_planner_calls':0,'source_author_calls':0,'formal_Table_I_calls':0,'results':results,
             'limitations':[
                 'Finite sampled configurations only: no exact/continuous swept-volume collision certificate and no dynamic execution.',
                 'Two added recursive midpoint levels on each saved RBS leaf are independent reconstruction after planning; they are not claims that original planner ran extra points.',
                 'PCS uses the recorded passive partition and branch with active midpoint interpolation and analytical closure; NR uses projected recursive midpoints with the saved NR parameters. Unprojected linear chords are not used as closure tests.',
                 'All 26 saved successful trajectories are checked. The 24 original TIME_LIMIT outcomes are preserved, not rerun or reclassified.',
                 'The 20R geometry and E0/E1 circles are a reconstructed planar proxy, not original spatial environments II-V or the original Table I.',
                 'All successful PCS paths used partition0; zero final-path swaps cannot substantiate a full-PCS swapping advantage over fixed0.',
                 'The self-collision pair exclusions and radii reproduce the frozen model; no omitted-pair physical safety claim is made.'
             ]}
    save(output/'summary.json',summary)
    rows=[]
    for r in results:
        rows.append({'environment':r['environment'],'method':r['method'],'seed':r['seed'],'qualified':r['independently_qualified'],
                     'saved_points':r['saved']['point_count'],'dense_points':r['dense']['point_count'],'saved_leaves':r['saved_leaf_count'],
                     'maximum_dense_step_rad':r['maximum_dense_step_rad'],'maximum_dense_closure_m':r['dense']['maximum_position_residual_m'],
                     'maximum_dense_angle_rad':r['dense']['maximum_angle_residual_rad'],'minimum_dense_clearance_m':r['dense']['minimum_clearance_m'],
                     'minimum_joint_margin_rad':r['dense']['minimum_joint_margin_rad'],'solution_swaps':r['genuine_solution_partition_switches']})
    with (output/'qualification_table.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    manifest={str(p.relative_to(output)):sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
    save(output/'artifact_sha256.json',manifest)
    print(json.dumps({k:summary[k] for k in ['status','source_success_count','independent_qualified_count','saved_path_points','saved_RBS_leaves','additional_reconstructed_midpoints','dense_path_points','wall_sec','process_cpu_sec']}),flush=True)
    return 0 if all_pass else 1


if __name__=='__main__':
    raise SystemExit(main())
