#!/usr/bin/env python3
"""Link fixed64 H outputs to exact existing certificates; zero science calls.

Read-only stdlib operation on binary64 arrays, saved matrices, branch sets,
raw collision JSON, old process evidence, hashes and committed source bytes.
The original H execution STOP and all30 original UNKNOWN final gates remain.
"""
from pathlib import Path
from collections import defaultdict
import datetime
import hashlib
import json
import math
import struct
import subprocess

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN=ROOT/'results/p4_full/20261015_R2_ABB_RANDOM_HELPER_H01'
LOCAL=ROOT/'results/p4_full/20261015_R2_ABB_PCS_LOCAL01'
OUT=ROOT/'reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_ALL64_SAVED_CERTIFICATE_LINKAGE_20261016.json'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bits(q):return struct.pack('>'+str(len(q))+'d',*q)
def exact(a,b):
    if isinstance(a,bool) or isinstance(b,bool):return type(a) is type(b) and a==b
    if type(a) in (int,float) and type(b) in (int,float):return bits([a])==bits([b])
    if type(a) is not type(b):return False
    if isinstance(a,dict):return set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b


def main():
    if OUT.exists() or OUT.with_suffix('.md').exists():raise SystemExit('PRESERVE_EXISTING_LINKAGE_NO_OVERWRITE')
    checks=[];retained={}
    def ck(k,v):checks.append({'check':k,'passed':bool(v)})
    def saved(p):
        p=Path(p);p=p if p.is_absolute() else ROOT/p
        retained[str(p.relative_to(ROOT))]=sha(p)
        return json.loads(p.read_text())
    e=saved(RUN/'execution.json');p=saved(e['protocol']);le=saved(LOCAL/'execution.json')
    oldpost=ROOT/'reports/P4_FULL_R2_ABB_PCS_FIXED_LOCAL_POST_REVIEW_20261015.md'
    retained[str(oldpost.relative_to(ROOT))]=sha(oldpost)
    post=saved('reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_ROOT_INDEPENDENT_POST_V2_20261016.json')
    ck('original_H_STOP_and30UNKNOWN_preserved',e['status']=='STOP_CLEANUP_OR_EVIDENCE_ERROR'
       and len(e['completed_final_ids'])==34 and len(e['uncompleted_final_fixtures'])==30)
    ck('personnel_independent_prefix_POST',post['personnel_independent'] is True and post['checks_failed']==0
       and post['source_execution_sha256']==sha(RUN/'execution.json'))
    ck('local_PARTIAL_history_preserved',le['status']=='FIXED_LOCAL_ABB_PCS_PARTIAL'
       and le['formal_planning_pass'] is False and sha(LOCAL/'execution.json')==e['prior_execution_sha256'][str((LOCAL/'execution.json').relative_to(ROOT))])
    for model in ('scripts/recover_p4_full_r2_endpoints.py','baselines/p4_full/abb_independent_oracle.py',
                  'baselines/p4_full/analyze_comau_native_qualification.py','baselines/p4_full/geometry_consistent/collision_adapter.py',
                  'baselines/p4_full/geometry_consistent/physical_nr.py','baselines/p4_full/geometry_consistent/rss_geometry.py'):
        ck('same_bound_numeric_geometry_source_'+model,e['bound_files_sha256'][model]==le['bound_files_sha256'][model]==sha(ROOT/model))
    manifest=p['collision_manifest'];mh=e['bound_files_sha256'][manifest]
    ck('same_unchanged_collision_manifest',sha(manifest)==mh)
    summaries=saved(RUN/'independent_final_summary.json');known={}
    for f in summaries:
        known.setdefault((f['environment'],bits(f['q12'])),f)
    groups=defaultdict(list);responses={};contexts={x['case_id']:x for x in p['fixed_contexts']}
    for fixture in p['fixed_schedule']:
        i=fixture['dispatch_index'];r=saved(RUN/f'helper_{i:03d}_raw_response.json')
        responses[i]=r;groups[(fixture['environment'],bits(r['q12']))].append(i)
    ck('exact19_keys_12_livecovered',len(groups)==19 and len(known)==12)
    expected_uncovered=[[34,50],[36,52],[38,39,54,55],[40,41,56,57],[42,43,58,59],[44,45,60,61],[46,47,62,63]]
    ck('uncovered7_key_identities', [ids for k,ids in groups.items() if k not in known]==expected_uncovered)
    eventpath=LOCAL/'events.jsonl';retained[str(eventpath.relative_to(ROOT))]=sha(eventpath)
    local_events=[json.loads(line) for line in eventpath.read_text().splitlines()]
    ck('old_local_events_independent_POST_hash',sha(eventpath)=='1102c2149b18b188c9fa6e5335f47c1c6e90462816b0dbf97a9792ce1700197f')
    localmap={};historical=[]
    for ids in expected_uncovered:
        i=ids[0];fixture=p['fixed_schedule'][i];q=responses[i]['q12'];key=(fixture['environment'],bits(q))
        matches=[]
        for fn in sorted(LOCAL.glob('*geometry_consistent.json')):
            v=json.loads(fn.read_text())
            for j,n in enumerate(v.get('checked_projection_events',[])):
                if n['environment']==key[0] and bits(n['q12'])==key[1]:matches.append((fn,v,j,n))
        ck('historical_unique_saved_root_'+str(i),len(matches)==1)
        fn,v,j,n=matches[0];saved(fn)
        blob=subprocess.check_output(['git','show','HEAD:'+str(fn.relative_to(ROOT))],cwd=ROOT)
        ck('historical_committed_bytes_'+str(i),hashlib.sha256(blob).hexdigest()==sha(fn))
        ev=[x for x in local_events if x['event']=='source_pair_qualified' and x['result']['label']==v['label']
            and x['result']['variant']==v['variant']]
        ck('old_raw_event_exact_full_saved_record_'+str(i),len(ev)==1 and exact(ev[0]['result'],v))
        ck('old_exact_env_q_and_qualifications_'+str(i),n['node_qualified'] is n['node_math_qualified'] is n['math_sound'] is True
           and n['closure_pass'] is n['branch_pass'] is n['native_FK_pass'] is n['active_coordinates_unchanged'] is True
           and n['limits']['legal'] is True and n['closure']['position_max_abs']<=1e-5 and n['closure']['rotation_matrix_max_abs']<=1e-5)
        ck('same_active_role_in_historical_root_'+str(i),v['request']['active_chain']==fixture['active_chain']
           and exact(q[6*fixture['active_chain']:6*(fixture['active_chain']+1)],v['request']['q12'][6*fixture['active_chain']:6*(fixture['active_chain']+1)]))
        col=n['collision']
        ck('same_manifest_qualified_discrete_clear_'+str(i),col['status']=='CHECKED' and col['collision'] is False
           and col['selected_variant']=='aligned' and col['manifest_sha256']==mh and col['variants']['aligned']['pose_consistency']['passed'] is True)
        for variant,row in col['variants'].items():
            raw=[json.loads(line.split(' ',1)[1]) for line in row['source_stdout'].splitlines() if line.startswith('P4_COLLISION_RESULT ')]
            ck('old_worker_raw_'+str(i)+'_'+variant,len(raw)==1 and all(exact(val,row[k]) for k,val in raw[0].items())
               and all(type(code) is int and code==0 for code in row['query_codes']) and row['native_result']==0)
        poses=[x['independent_TCP'] for x in col['variants']['aligned']['pose_consistency']['errors']]
        a,b=poses;length=300. if key[0]=='II' else 500.
        xyz=max(abs(b[j][3]-(a[j][3]+a[j][0]*length)) for j in range(3))
        rot=max(abs(b[j][k]-a[j][k]*(-1. if k<2 else 1.)) for j in range(3) for k in range(3))
        ck('saved_independent_TCP_closure_arithmetic_'+str(i),xyz<=1e-5 and rot<=1e-5)
        localmap[key]=(fn,v,j,n)
        historical.append({'dispatch_indexes':ids,'environment':key[0],'q12':q,'evidence_file':str(fn.relative_to(ROOT)),
                           'evidence_file_sha256':sha(fn),'projection_event_index':j,'passive_branch_identity':n['passive_branch_identity'],
                           'saved_physical_closure':n['closure'],'saved_aligned_independent_TCP_closure':{'position_maxabs_mm':xyz,'rotation_maxabs':rot},
                           'same_collision_manifest_sha256':mh,'no_new_queries':True})
    certificates=[]
    for fixture in p['fixed_schedule']:
        i=fixture['dispatch_index'];r=responses[i];q=r['q12'];key=(fixture['environment'],bits(q));active=fixture['active_chain'];passive=1-active
        # Corresponding source-control final contains the exact same active arm.
        source_index=next(x['dispatch_index'] for x in p['fixed_schedule'] if x['factor']=='source_control'
                          and x['mode']==fixture['mode'] and x['case_id']==fixture['case_id'])
        sc=summaries[source_index]
        ck('same_context_unchanged_active_binary64_'+str(i),bits(q[6*active:6*(active+1)])==bits(sc['q12'][6*active:6*(active+1)])
           ==bits(fixture['q12'][6*active:6*(active+1)]))
        branches=[None,None];branches[active]=sc['branches'][active]
        if key in known:
            ref=known[key];branches[passive]=ref['branches'][passive]
            physical_ref={'kind':'H_ORIGINAL_COMPLETED_FINAL','dispatch_index':ref['dispatch_index'],
                          'file':str((RUN/f"final_{ref['dispatch_index']:03d}.json").relative_to(ROOT))}
            ck('same_q_live_complete_certificate_'+str(i),ref['physical_final_qualified'] is True and ref['collision']['manifest_sha256']==mh)
        else:
            fn,v,j,n=localmap[key];branches[passive]=n['passive_branch_identity']
            physical_ref={'kind':'PCS_LOCAL01_HISTORICAL_EXACT_ENV_Q','file':str(fn.relative_to(ROOT)),'projection_event_index':j}
            ck('same_q_historical_passive_branch_role_'+str(i),v['request']['active_chain']==active and n['node_qualified'] is True)
        tr_index=next(x['dispatch_index'] for x in p['fixed_schedule'] if x['factor']==fixture['factor']
                      and x['mode']=='trace' and x['case_id']==fixture['case_id'])
        marks=[ev['args'] for ev in responses[tr_index]['trace'] if ev['event']=='observed'
               and ev['kind']=='identify_completed_in_helper' and bits(ev['args']['q1']+ev['args']['q2'])==bits(q)]
        ck('own_context_final_source_label_observed_'+str(i),bool(marks));mark=marks[-1]
        direct=mark['branch'] in branches[passive]['branch_set']
        dual=all(type(label) in (int,float) and label in range(8) and label in branches[1-j]['branch_set'] for j,label in enumerate(mark['ik']))
        ck('own_context_direct_and_dual_labels_'+str(i),direct and dual)
        deg=[(-165,165),(-110,110),(-110,70),(-160,160),(-120,120),(-400,400)]*2
        legal=all(lo*3.1416/180.<=x<=hi*3.1416/180. for x,(lo,hi) in zip(q,deg))
        ck('own_context_original_full12_bounds_'+str(i),legal)
        certificates.append({'dispatch_index':i,'factor':fixture['factor'],'mode':fixture['mode'],'case_id':fixture['case_id'],
                             'environment':fixture['environment'],'source_returned':r['returned'],'physical_certificate':physical_ref,
                             'active_branch_source_control_final':source_index,'independent_arm_branch_sets':[b['branch_set'] for b in branches],
                             'source_trace_dispatch_index':tr_index,'source_final_direct_branch':mark['branch'],'source_final_dual_labels':mark['ik'],
                             'active_unchanged':True,'direct_branch_membership':direct,'dual_label_membership':dual,'source_limits_legal':legal,
                             'evidence_classification':'SAVED_REUSED_EVIDENCE_ONLY','new_live_final_gate_completed':False})
    ck('source_bool_separately_preserved',sum(x['source_returned'] for x in certificates)==32 and len(certificates)==64)
    ck('retained_all_saved_bytes_unchanged',all(sha(ROOT/n)==h for n,h in retained.items()))
    failures=[x for x in checks if not x['passed']]
    report={'schema':'P4_H_FIXED64_EXACT_SAVED_CERTIFICATE_LINKAGE_V1','status':'PASS_SAVED_CERTIFICATE_LINKAGE_64_ONLY' if not failures else 'FAIL_LINKAGE',
            'classification':'SAVED_REUSED_EVIDENCE_ONLY','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'personnel_independent':True,'checks_total':len(checks),'checks_passed':len(checks)-len(failures),'checks_failed':len(failures),
            'checks':checks,'script_sha256':sha(__file__),'original_H_execution_sha256':sha(RUN/'execution.json'),
            'original_H_status':e['status'],'original_H_completed_final_count':34,'original_H_unknown_final_count':30,
            'original_H_status_or_counts_changed':False,'all64_have_exact_saved_physical_and_context_branch_certificate':not failures,
            'distinct_env_q12_binary64_keys':len(groups),'own_completed_keys':len(known),'historical_exact_keys':len(localmap),
            'historical7':historical,'certificates':certificates,'retained_sha256':retained,
            'new_scientific_calls':dict.fromkeys(('helper','FK','IK','branch_invariant_evaluation','Jacobian','PQP','NR','RBS','RNG','solve','compile','VI_construction','formal_Table_I'),0),
            'limitations':['Original H run remains STOP with34 actual complete finals and30 original UNKNOWN gates.',
                           'Exact saved physical certificates are reused from same environment, binary64 joint vector, bound numerical model and collision manifest.',
                           'Active arm branch sets use same-context source_control completed final; passive sets use same-q completed H final or historical PCS fixed projection.',
                           'Every context source direct and dual label is checked separately against reused independent geometry sets; no new branch computation.',
                           'No H original gate is resumed, replaced or reclassified as a new live completion.',
                           'No sampling distribution, source-native implementation, planner or continuous collision claim; formal0/22500 andVI974/974 remain.']}
    with OUT.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    text=(f"# H 固定64输出：已有资格证据精确链接\n\n**{report['status']}**：{report['checks_passed']}/{report['checks_total']}，失败{len(failures)}。分类为 **SAVED_REUSED_EVIDENCE_ONLY**，新增科学/编译/候选调用全部为0。\n\n"
          "64个输出共19组同环境且逐bit相同的q12；原H34完整终态覆盖12组，其余7组全部精确匹配此前PCS_LOCAL01已审查的合格固定投影事件。旧事件的闭链、原限位、几何分支、相同v3碰撞manifest、aligned TCP与raw查询证据均保留。\n\n"
          "逐64上下文另行核对active角保持、direct分支和两臂source dual labels。active几何分支引用同一上下文原source_control完整终态的相同6角；passive分支引用相同q的完整H终态或旧PCS投影。全部成员关系一致，不借用另一上下文的source标签、不重新计算几何分支。\n\n"
          "原H execution仍为STOP_CLEANUP_OR_EVIDENCE_ERROR，34个实际完整final及30个原UNKNOWN门均未改变。此后审只链接已有证据，不声称64个现场外门完成，不构成新运行、resume、规划/分布资格或连续无碰撞证明。原论文完整义务、正式0/22500和VI974/974不变。\n")
    with OUT.with_suffix('.md').open('x') as f:f.write(text)
    print(json.dumps({k:report[k] for k in ('status','checks_total','checks_passed','checks_failed','historical_exact_keys')},ensure_ascii=False))


if __name__=='__main__':main()
