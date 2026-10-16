#!/usr/bin/env python3
"""Saved-only variant scope supplement; never imports a scientific module."""
from pathlib import Path
from collections import Counter
import datetime
import hashlib
import json

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN=Path('results/p4_full/20261015_R2_ABB_CBIRRT_D_PATH01')
POST='reports/P4_FULL_R2_ABB_CBIRRT_D_PATH01_SAVED_INDEPENDENT_POST_20261016.json'
POST_SHA='2c548df054867c7d9545fac3726142f3581b3cdfbe54299233a27bb07bace4d0'
OUT='reports/P4_FULL_R2_ABB_CBIRRT_D_PATH01_VARIANT_SCOPE_SAVED_SUPPLEMENT_20261016.json'
retained={}
checks=[]

def raw(n):
    p=Path(n);p=p if p.is_absolute()else ROOT/p
    b=p.read_bytes();retained[str(p.relative_to(ROOT))]=hashlib.sha256(b).hexdigest();return b
def read(n):return json.loads(raw(n))
def ck(n,ok):checks.append(dict(check=n,passed=bool(ok)))

def main():
    post=read(POST);e=read(RUN/'execution.json');p=read(e['protocol'])
    ck('fixed independent complete POST already passed',retained[POST]==POST_SHA and post['personnel_independent']is True and
       post['independent_path_qualified']is post['external_supervision_qualified']is True and post['checks_total']==post['checks_passed']==58152)
    ck('same execution and complete413node count',hashlib.sha256(raw(RUN/'execution.json')).hexdigest()==post['execution_sha256'] and
       e['completed_nodes']==e['qualified_nodes']==e['node_count']==413 and len(p['fixed_queue']['nodes'])==413)
    variants={k:dict(nodes=0,native_collision_nodes=0,pose_pass_nodes=0,pose_mismatch_nodes=0,PQP_queries=0,
       statuses=Counter(),maximum_saved_translation_error_mm=0.,maximum_saved_rotation_error=0.)for k in('native','aligned')}
    for i in range(413):
        collision=read(RUN/f'node_{i:05d}_collision_response.json')
        ck(str(i)+' selected aligned original policy',collision['status']=='CHECKED'and collision['collision']is False and
           collision['selected_variant']=='aligned'and set(collision['variants'])=={'native','aligned'})
        for name,row in collision['variants'].items():
            result=variants[name];pc=row['pose_consistency'];errors=pc['errors']
            passed=all(v['translation_maxabs_mm']<=1e-5 and v['rotation_maxabs']<=1e-5 for v in errors)
            ck(str(i)+' '+name+' full saved verdict matches original thresholds',len(errors)==2 and pc['passed']is passed and
               pc['status']==('PASS'if passed else'COLLISION_PHYSICAL_TCP_MISMATCH')and len(row['query_codes'])==116 and
               all(type(v)is int and v==0 for v in row['query_codes']))
            result['nodes']+=1;result['native_collision_nodes']+=bool(row['native_collision'])
            result['pose_pass_nodes']+=passed;result['pose_mismatch_nodes']+=not passed
            result['PQP_queries']+=len(row['query_codes']);result['statuses'][pc['status']]+=1
            result['maximum_saved_translation_error_mm']=max(result['maximum_saved_translation_error_mm'],*(v['translation_maxabs_mm']for v in errors))
            result['maximum_saved_rotation_error']=max(result['maximum_saved_rotation_error'],*(v['rotation_maxabs']for v in errors))
    edges=p['fixed_queue']['edges'];attempts=p['fixed_queue']['all_original_attempts']
    ck('four original complete source edges and passive-chain mechanism',len(edges)==4 and[e['active_chain']for e in edges]==[0,0,1,1]and
       [e['branch']for e in edges]==[3,3,3,3]and[e['selected_attempt_index']for e in edges]==[0,1,3,4]and
       edges[2]['edge_kind']=='actual_cross_tree_bridge'and edges[2]['consumed_attempt_indices']==[2,3]and
       attempts[2]['active_chain']==0 and attempts[2]['returned']is False and len(attempts[2]['path_q12'])==2 and
       attempts[3]['active_chain']==1 and attempts[3]['returned']is True and len(attempts[3]['path_q12'])==33)
    ck('both raw policies zero collision but acceptance only physically aligned',variants['native']['nodes']==variants['aligned']['nodes']==413 and
       variants['native']['native_collision_nodes']==variants['aligned']['native_collision_nodes']==0 and
       variants['native']['pose_mismatch_nodes']==413 and variants['aligned']['pose_pass_nodes']==413 and
       variants['native']['PQP_queries']==variants['aligned']['PQP_queries']==47908)
    for n,h in list(retained.items()):ck('unchanged retained '+n,hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h)
    failed=[c for c in checks if not c['passed']];passed=not failed
    report=dict(schema='P4_CBIRRT_D_PATH01_VARIANT_SCOPE_SAVED_SUPPLEMENT_V1',
       status='PASS_VARIANT_SCOPE_SAVED_SUPPLEMENT'if passed else'FAIL_VARIANT_SCOPE_SAVED_SUPPLEMENT',
       generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),personnel_independent=True,
       checks_total=len(checks),checks_passed=sum(c['passed']for c in checks),checks_failed=len(failed),failures=failed,
       original_independent_POST=POST,original_independent_POST_sha256=POST_SHA,execution_sha256=post['execution_sha256'],
       variants=variants,accepted_variant='aligned',native_physical_pose_qualified=False,
       selected_source_active_chain_indices=[0,0,1,1],selected_source_passive_branches=[3,3,3,3],
       original_bridge_failed_attempt=dict(index=2,active_chain=0,branch=3,returned=False,nodes=2),
       original_bridge_successful_fallback=dict(index=3,active_chain=1,branch=3,returned=True,nodes=33),
       method_scope='RECONSTRUCTED D-fixed original CBiRRT plus original discrete aligned source collision policy.',
       role_switch_scope='Single actual saved mechanism witness only; no PCS advantage, success-rate or performance inference.',
       continuous_collision_certificate=False,new_scientific_calls=0,runner_model_import_calls=0,
       retained_sha256=retained,audit_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    with(ROOT/OUT).open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with(ROOT/OUT).with_suffix('.md').open('x')as f:
        f.write('# P 碰撞变体与被动链机制保存审计补充\n\n'+report['status']+'：'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'。\n\n'+
           '完整413节点中，native和aligned原始PQP均无collision、各47908查询；native保存TCP全部413节点不符合物理坐标一致性，aligned全部413节点符合。完整路径资格接纳只依冻结aligned策略。\n\n'+
           '四条原始完整边active_chain=0,0,1,1、passive branch均3；真实跨树桥保留原active0失败M2与原active1成功fallback M33。该单条路径给出原机制实际发生的见证，不构成PCS复杂场景优势或统计性能证据。全部原始失败保持。\n\n'+
           json.dumps(variants,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),variants=variants),ensure_ascii=False))
    raise SystemExit(0 if passed else 2)

if __name__=='__main__':main()
