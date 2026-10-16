#!/usr/bin/env python3
"""Saved-only audit of IV wrist run02, after its unique real execution.

This reviewer implemented V3 engineering recovery, not original science
functions. Do not label this a completely personnel-independent scientific
audit. No scientific module import, binary execution, compilation, model,
FK/IK/Jacobian/SVD/branch-invariant query, sampling or retry. Only saved
matrices/spectra, source-limit arithmetic, JSON/bytes and hashes are examined.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import datetime
import hashlib
import json
import math
import struct
import subprocess

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
DEFAULT_RUN='results/p4_full/20261015_R2_IV_RSS_WRIST_FIXED100_02'
DEFAULT_OUT='reports/P4_FULL_R2_IV_RSS_WRIST_FIXED100_02_SAVED_ENGINEERING_POST_20261016.json'


def fp(n):
    n=Path(n)
    return n if n.is_absolute() else ROOT/n


def sha(n):return hashlib.sha256(fp(n).read_bytes()).hexdigest()


def exact(a,b):
    if isinstance(a,bool) or isinstance(b,bool):return type(a) is type(b) and a==b
    if type(a) in (int,float) and type(b) in (int,float):return struct.pack('>d',a)==struct.pack('>d',b)
    if type(a) is not type(b):return False
    if isinstance(a,dict):return set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b


def mm(a,b):
    return [[math.fsum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def err(a,b):
    return {'position_maxabs_mm':max(abs(a[i][3]-b[i][3]) for i in range(3)),
            'rotation_matrix_maxabs':max(abs(a[i][j]-b[i][j]) for i in range(3) for j in range(3))}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run',default=DEFAULT_RUN);ap.add_argument('--output',default=DEFAULT_OUT)
    args=ap.parse_args();run=fp(args.run);out=fp(args.output)
    if not (run/'execution.json').is_file():raise SystemExit('SAVED_EXECUTION_NOT_READY_NO_ACTION')
    if out.exists() or out.with_suffix('.md').exists():raise SystemExit('EXISTING_AUDIT_PRESERVED_NO_OVERWRITE')
    retained={};groups=defaultdict(lambda:{'total':0,'passed':0});failed=[]
    def ck(group,label,ok):
        groups[group]['total']+=1;groups[group]['passed']+=bool(ok)
        if not ok:failed.append({'group':group,'check':label})
    def saved(n):
        n=fp(n);retained[str(n.relative_to(ROOT)) if n.is_relative_to(ROOT) else str(n)]=sha(n)
        return json.loads(n.read_text())
    def raw(n):
        n=fp(n);retained[str(n.relative_to(ROOT))]=sha(n);return n.read_bytes()
    def spectrum(label,r):
        values=r['singular_values'];cut=1e-6*values[0]
        ck('spectra',label+' six finite ordered nonnegative singular values',len(values)==6 and
           all(math.isfinite(x) and x>=0 for x in values) and values==sorted(values,reverse=True))
        ck('spectra',label+' saved cutoff/rank exact arithmetic',exact(cut,r['cutoff']) and r['rank']==sum(x>cut for x in values)
           and r['relative_threshold']==1e-6 and r['linear_rows']=='mm to m')
    def branch(label,b):
        es=(1,-1,1,-1,1,-1,1,-1);ws=(1,-1,-1,1,-1,1,1,-1)
        expected=[i for i in range(8) if (b['shoulder_sign'] is None or b['shoulder_sign']==(1 if i<4 else -1))
                  and (b['elbow_sign'] is None or b['elbow_sign']==es[i]) and (b['wrist_sign'] is None or b['wrist_sign']==ws[i])]
        ck('branches',label+' saved signs to branch set',b['branch_set']==expected and b['unique'] is
           all(b[k] is not None for k in ('shoulder_sign','elbow_sign','wrist_sign')))
        ck('branches',label+' original numbering and epsilon',b['source_elbow_sign_by_label']==list(es)
           and b['source_wrist_sign_by_label']==list(ws) and b['branch_zero_relative_epsilon']==64*2.220446049250313e-16)
    e=saved(run/'execution.json');p=saved(e['protocol']);c=saved(e['claim']);shared=p['shared_fixed100_budget']
    first=saved(shared['first_execution']);firstp=saved(shared['first_protocol']);firstc=saved(shared['first_claim'])
    ck('provenance','run02 explicit V3 schema',e['schema']=='P4_R2_IV_RSS_WRIST_FIXED100_MATH_QUALIFICATION_V3'
       and e['run_id']==p['run_id']=='20261015_R2_IV_RSS_WRIST_FIXED100_02')
    ck('provenance','reviewed frozen protocol',p['frozen'] is True and all(v is True for v in p['reviews'].values())
       and p['execution_readiness']=='FROZEN_REVIEWED_READY')
    ck('provenance','protocol and claim hashes unchanged',sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']
       and sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'] and c['protocol_sha256']==e['protocol_sha256'])
    ck('provenance','bound before after exact',e['bound_files_sha256']==p['bound_files_sha256']==e['bound_files_after_sha256'])
    for n,h in p['bound_files_sha256'].items():ck('provenance','bound '+n,sha(n)==h)
    for n in p['source_files']+[e['protocol']]:
        blob=subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)
        ck('provenance','committed source '+n,hashlib.sha256(blob).hexdigest()==sha(n))
    ck('first01','original STOP reason and zero model',first['status']=='STOP_PREFIX_RETAINED'
       and first['termination_reason']=="StopQualification('RUNTIME_GEOMETRY_OR_SOURCE_LIMITS_CHANGED')"
       and first['target_results']==first['branch_observations']==[] and all(v==0 for v in first['counts'].values())
       and len(first['uncompleted_branch_diagnostic_ids'])==800)
    ck('first01','immutable execution protocol claim',sha(shared['first_execution'])==shared['first_execution_sha256']
       and sha(shared['first_protocol'])==shared['first_protocol_sha256']==first['protocol_sha256']==first['protocol_after_sha256']
       and sha(shared['first_claim'])==shared['first_claim_sha256']==first['claim_sha256']==first['claim_after_sha256'])
    ck('first01','same fixed inputs gates binary',p['fixed_inputs']==firstp['fixed_inputs'] and p['gates']==firstp['gates']
       and p['binary']==firstp['binary'] and p['binary_sha256']==firstp['binary_sha256'])
    prior=[saved(n) for n in p['prior_executions']]
    wall=math.fsum(x['wall_s'] for x in prior);cpu=math.fsum(x['cpu_s'] for x in prior)
    ck('budget','V10 exact28 own prior',len(prior)==28 and wall==p['previous_r2_wall_s']==e['previous_r2_wall_s']
       and cpu==p['previous_r2_cpu_s']==e['previous_r2_cpu_s'])
    ck('budget','first own cost deducted shared30/60',exact(p['budget']['wall_s'],30-first['wall_s'])
       and exact(p['budget']['cpu_s'],60-first['cpu_s']) and exact(shared,e['shared_fixed100_budget'])
       and shared['shared_total_wall_s']==30 and shared['shared_total_cpu_s']==60)
    ck('budget','exact cumulative own not cumulative twice',e['cumulative_execution_wall_s']==wall+e['wall_s']
       and e['cumulative_execution_cpu_s']==cpu+e['cpu_s'] and e['r2_remaining']['wall_s']==3600-(wall+e['wall_s'])
       and math.isclose(e['r2_remaining']['cpu_s'],7200-cpu-e['cpu_s'],abs_tol=2e-12))
    timed=e['wall_s']>=p['budget']['wall_s'] or e['cpu_s']>=p['budget']['cpu_s']
    if timed:ck('budget','cap cannot math PASS',e['mathematical_component_gate']=='UNKNOWN_OR_FAILED'
                and e['status']=='STOP_WALL_OR_CPU_BUDGET_PREFIX_RETAINED')
    ck('budget','no model extras VI/formal',all(e[k]==0 for k in ('new_VI_candidate_constructions','collision_queries','RBS_calls',
       'NR_calls','RNG_calls','solve_calls','formal_planning_calls')) and e['full_RSS_or_planning_pass'] is False)
    events=[json.loads(line) for line in raw(run/'events.jsonl').splitlines()];ec=Counter(x['event'] for x in events)
    fkstarts=[x for x in events if x['event']=='mathematical_arm_FK_J_started']
    fkdone=[x for x in events if x['event']=='mathematical_arm_FK_J_completed']
    count=e['counts'];targets={}
    for t in e['target_results']:
        item=t['fixed_input'];sample=item['sample'];targets[sample]=t
        ck('targets',str(sample)+' frozen original input',exact(item,p['fixed_inputs'][sample]))
        tf=run/f'target_s{sample:03d}.json'
        if tf.exists():ck('targets',str(sample)+' retained target exact',exact(saved(tf),t))
        else:ck('targets',str(sample)+' absent target is STOP prefix',e['status']!='FIXED_100_WRIST_MATHEMATICS_RECORDED')
        q=item['forced_passive_q6_rad'];original=item['source_passive_q6_rad']
        ck('targets',str(sample)+' only passiveq5 forced',exact(q[:4]+q[5:],original[:4]+original[5:]) and q[4]==0.)
        spectrum(str(sample)+' passive',t['passive_rank_report']);branch(str(sample)+' passive',t['passive_branch_identity'])
        flip=[[-1.,0.,0.,0.],[0.,-1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
        invq=[[1.,0.,0.,-1800.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
        target=mm(mm(t['passive_pose'],flip),invq)
        ck('targets',str(sample)+' saved target matrix arithmetic',max(abs(target[i][j]-t['active_target'][i][j]) for i in range(4) for j in range(4))<=2e-12)
        observed=[x for x in fkdone if x['case_id']==f'IV_s{sample:03d}_passive']
        ck('targets',str(sample)+' FK event bound to passive cache',len(observed)==1 and exact(observed[0]['pose'],t['passive_pose'])
           and exact(observed[0]['jacobian'],t['passive_world_jacobian']))
    rawrows={};rawaccepted=0;rawtails=[];dispatched=[];processes=[]
    for ev in events:
        if ev['event']=='external_K_dispatched':
            ids=ev['request_ids'];dispatched+=ids;sample=int(ids[0][4:7]);target=ev['target']
            fn=run/f'native_s{sample:03d}.jsonl';rows=[]
            if fn.exists():
                for line1,line in enumerate(raw(fn).splitlines(keepends=True),1):
                    try:r=json.loads(line)
                    except (ValueError,UnicodeDecodeError):rawtails.append({'file':str(fn.relative_to(ROOT)),'line1':line1,'sha256':hashlib.sha256(line).hexdigest()});break
                    b=len(rows)
                    ck('native',f'{sample}/{b} interface and target',r['schema']=='P4_SPATIAL_BATCH_V1' and r['model']==4
                       and r['op']=='K' and r['arm']==1 and r['input_line']==b+1 and r['branch']==b and exact(r['target'],target))
                    rows.append(r);rawrows[ids[b]]=r
                    rawaccepted+=r.get('success') is True and r.get('finite') is True and not r.get('error')
            ck('native',str(sample)+' at most frozen8 returns',len(rows)<=8)
            ck('native',str(sample)+' target was saved before dispatch',sample in targets and exact(target,targets[sample]['active_target']))
        if ev['event']=='process_started':
            label=ev['label'];sample=int(label[4:7]);inp=fp(ev['input']);text=raw(inp).decode();lines=text.splitlines()
            ck('native',label+' fixed eightK input',len(lines)==8)
            for branch_index,line in enumerate(lines):
                parts=line.split();ck('native',label+'/'+str(branch_index)+' literal target bits',parts[:3]==['K','1',str(branch_index)]
                   and exact([float(x) for x in parts[3:]],[v for row in targets[sample]['active_target'] for v in row]))
            stem=inp.with_name(inp.name.removesuffix('.input.txt'))
            stdout=Path(str(stem)+'.stdout.txt');stderr=Path(str(stem)+'.stderr.txt')
            done=[x for x in events if x['event']=='process_finished' and x['label']==label]
            if done:
                fin=done[0];ck('native',label+' process completed with raw SHA',len(done)==1 and fin['exit_code']==0
                   and sha(stdout)==fin['stdout_sha256'] and sha(stderr)==fin['stderr_sha256'])
                ck('native',label+' stdout and native saved file bytes',raw(stdout)==raw(run/f'native_s{sample:03d}.jsonl'))
            processes.append({'sample':sample,'label':label,'completed':bool(done),'stdout':str(stdout.relative_to(ROOT)),
                              'stdout_sha256':sha(stdout) if stdout.exists() else None,'stderr_sha256':sha(stderr) if stderr.exists() else None})
    confirmed=list(rawrows)
    unknown=[case for case in dispatched if case not in rawrows]
    account=e['native_call_accounting']
    ck('counts','native actual accounting exact',account['external_K_dispatched']==len(dispatched)
       and account['external_K_JSON_completed']==len(confirmed) and account['JSON_completed_request_ids']==confirmed
       and account['native_accepted_FK_observed']==rawaccepted and account['unconfirmed_dispatched_request_ids']==unknown)
    ck('counts','native actual internal starts UNOBSERVED',account['internal_true_K_started']==account['internal_true_native_FK_started']=='UNOBSERVED_NO_NATIVE_START_HOOK')
    observations=e['branch_observations'];doneids=[];g0=[];g1=[];summaries=[]
    bounds=p['geometry']['source_limit_representations']['runtime_full12_bounds_rad']
    for r in observations:
        case=r['case_id'];sample=r['sample'];branch_index=r['branch'];t=targets[sample];native=r['native_active_ik']
        ck('diagnostics',case+' raw native row exact',case in rawrows and exact(rawrows[case],native) and r['source_accepted'] is native['success'])
        fn=run/(case+'.json');complete=fn.exists() and 'soundness_failure' not in r
        if fn.exists():ck('diagnostics',case+' saved final exact',exact(saved(fn),r))
        if not complete:
            summaries.append({'case_id':case,'status':'INCOMPLETE_PREFIX_OR_SOUNDNESS_FAILURE','soundness_failure':r.get('soundness_failure')});continue
        doneids.append(case);reasons=[];additional=[];pr=t['passive_rank_report']
        if not native['success']:reasons.append('ACTIVE_IK_REJECTED')
        else:
            q=r['candidate_q12_rad'];qa=native['solution'];p1=r['active_pose'];p2=t['passive_pose']
            ck('diagnostics',case+' finite exact root plus fixed passive',len(q)==12 and all(math.isfinite(x) for x in q)
               and exact(q,qa+t['fixed_input']['forced_passive_q6_rad']) and native['finite'] is True and not native['error'])
            roundtrip=err(p1,t['active_target'])
            grasp=p['geometry']['grasp_transforms'][0];flip=[[-1.,0.,0.,0.],[0.,-1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
            closure=err(p2,mm(mm(p1,grasp),flip))
            for name,actual in (('active_roundtrip',roundtrip),('physical_closure',closure)):
                ck('diagnostics',case+' '+name+' saved matrix arithmetic',all(math.isclose(value,r[name][k],abs_tol=2e-12,rel_tol=2e-12) for k,value in actual.items()))
                ck('diagnostics',case+' '+name+' original physical threshold',actual['position_maxabs_mm']<=1e-5 and actual['rotation_matrix_maxabs']<=1e-5)
            legal=all(lo<=value<=hi for value,(lo,hi) in zip(q,bounds))
            ck('diagnostics',case+' exact runtime bounds and actual legal',exact(bounds,r['source_bounds_rad']) and r['source_all12_bounds_legal'] is legal)
            if not legal:reasons.append('JOINT_LIMIT_REJECTED')
            spectrum(case+' active',r['active_rank_report']);spectrum(case+' full6x12',r['physical_constraint']['full_rank_report'])
            branch(case+' active',r['active_branch_identity'])
            ck('diagnostics',case+' cached passive evidence exact',exact(r['passive_rank_report'],pr) and exact(r['passive_branch_identity'],t['passive_branch_identity']))
            js=r['physical_constraint']['constraint_jacobian_6_by_12']
            ck('diagnostics',case+' full cached derivative shape finite',len(js)==6 and all(len(row)==12 and all(math.isfinite(x) for x in row) for row in js))
            if pr['rank']!=5:additional.append('PASSIVE_RANK_NOT_5')
            if branch_index not in r['active_branch_identity']['branch_set']:additional.append('REQUESTED_ACTIVE_BRANCH_NOT_IN_GEOMETRIC_MEETING_SET')
            if r['physical_constraint']['full_rank_report']['rank']!=6:additional.append('FULL_PHYSICAL_CONSTRAINT_RANK_NOT_6')
            activeevents=[x for x in fkdone if x['case_id']==case]
            ck('diagnostics',case+' FK event bound to active cache',len(activeevents)==1 and exact(activeevents[0]['pose'],p1)
               and exact(activeevents[0]['jacobian'],r['active_world_jacobian']))
        if pr['rank']>=6:reasons.append('PASSIVE_FULL_RANK')
        ck('diagnostics',case+' exact original G0/G1 reasons',r['G0_reasons']==reasons and r['G1_additional_reasons']==additional)
        G0=not reasons;G1=G0 and not additional
        ck('diagnostics',case+' G0/G1 separately classified',r['G0_qualified'] is G0 and r['G1_qualified'] is G1
           and r['collision_checked'] is r['RBS_checked'] is r['full_RSS_or_planning_pass'] is False)
        if G0:g0.append(case)
        if G1:g1.append(case)
        summaries.append({'case_id':case,'source_accepted':native['success'],'G0_qualified':G0,'G1_qualified':G1,'G0_reasons':reasons,'G1_additional_reasons':additional})
    allids=[case for item in p['fixed_inputs'] for case in item['branch_request_ids']]
    missing=[case for case in allids if case not in doneids]
    ck('counts','fixed100_800 denominators unchanged',e['fixed_target_denominator']==len(p['fixed_inputs'])==100
       and e['branch_request_denominator']==len(allids)==800)
    ck('counts','diagnostic UNKNOWN tail exact',e['uncompleted_branch_diagnostic_ids']==missing)
    ck('counts','G0_G1 saved denominators exact',e['G0_qualified_branches']==len(g0) and e['G1_qualified_branches']==len(g1)
       and e['G0_qualified_targets']==len({case[4:7] for case in g0}) and e['G1_qualified_targets']==len({case[4:7] for case in g1}))
    ck('counts','FK started completed actual events',count.get('mathematical_arm_FK_J_started',0)==len(fkstarts)
       and count.get('mathematical_arm_FK_J_completed',0)==len(fkdone) and len(fkstarts)<=900)
    ck('counts','no inferred complete internal calls',count.get('external_K_dispatched',0)==len(dispatched)<=800
       and count['external_K_JSON_completed']==len(confirmed) and count['native_accepted_FK_observed']==rawaccepted)
    scientific_complete=len(doneids)==800 and count.get('fixed_targets_completed',0)==100 and not any('soundness_failure' in r for r in observations)
    expected_pass=scientific_complete and bool(g1) and not timed and e['status']=='FIXED_100_WRIST_MATHEMATICS_RECORDED'
    ck('scientific_scope','math component gate exactly complete positive only',e['mathematical_component_gate']==('PASS_RECONSTRUCTED_MATH_ONLY' if expected_pass else 'UNKNOWN_OR_FAILED'))
    if expected_pass:ck('scientific_scope','all accepted sound only complete run',e['all_source_accepted_roots_sound'] is True and len(missing)==0)
    ck('provenance','all retained read bytes unchanged',all(sha(n)==h for n,h in retained.items()))
    report={'schema':'P4_IV_WRIST02_STDLIB_SAVED_ENGINEERING_POST_V1','status':'PASS_SAVED_EVIDENCE_AUDIT' if not failed else 'FAIL_SAVED_EVIDENCE_AUDIT',
            'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'reviewer_is_V3_engineering_implementer':True,'reviewer_is_original_scientific_function_author':False,
            'fully_personnel_independent':False,'scientific_run_original_status':e['status'],'scientific_run_original_component_gate':e['mathematical_component_gate'],
            'checks_total':sum(v['total'] for v in groups.values()),'checks_passed':sum(v['passed'] for v in groups.values()),'checks_failed':len(failed),
            'groups':dict(groups),'failures':failed,'run':str(run.relative_to(ROOT)),'execution_sha256':sha(run/'execution.json'),
            'audit_script_sha256':sha(__file__),'prior_execution_count':len(prior),'prior_wall_s':wall,'prior_cpu_s':cpu,
            'own_wall_s':e['wall_s'],'own_cpu_s':e['cpu_s'],'shared_first01_plus_run02_wall_s':first['wall_s']+e['wall_s'],
            'shared_first01_plus_run02_cpu_s':first['cpu_s']+e['cpu_s'],'raw_K_return_count':len(confirmed),'raw_finite_accepted_K_nativeFK_observed':rawaccepted,
            'G0_branches':len(g0),'G1_branches':len(g1),'G0_targets':len({case[4:7] for case in g0}),'G1_targets':len({case[4:7] for case in g1}),
            'actual_FK_J_started':len(fkstarts),'actual_FK_J_completed':len(fkdone),'completed_diagnostic_count':len(doneids),'unknown_diagnostic_count':len(missing),
            'raw_incomplete_tails':rawtails,'unconfirmed_dispatched_ids':unknown,'uncompleted_diagnostic_ids':missing,'branch_summaries':summaries,
            'processes':processes,'retained_sha256':retained,
            'new_scientific_calls':dict.fromkeys(('FK','IK','Jacobian','SVD','geometric_branch_query','collision','RBS','NR','RNG','solve','compile','VI_construction'),0),
            'limitations':['This reviewer implemented V3 engineering recovery; this audit is separate from the runner but not completely personnel independent.',
                           'No scientific model, FK/IK, SVD or branch invariant was recomputed; rank arithmetic uses saved spectra, branch membership uses saved independent signs.',
                           'Original first01 guard failure, run02 status and every UNKNOWN tail remain unchanged.',
                           'G0/G1 are fixed mathematical component gates only; no collision, RSS distribution, RBS, planner, full figure/table or continuous certificate.',
                           'All original211 obligations, formal0/22500 andVI974/974 remain.']}
    with out.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    text=(f"# IV wrist02 保存证据后审\n\n**{report['status']}**：{report['checks_passed']}/{report['checks_total']}，失败{len(failed)}。"
          "本审查者实施过v3工程入口修补，未编写原科学函数；因此这是runner之外的保存审计，不宣称人员完全独立。新增科学/编译调用均为0。\n\n"
          f"原运行状态{e['status']}；原数学组件门{e['mathematical_component_gate']}。"
          f"实际K返回{len(confirmed)}，数学FK/J开始/完成{len(fkstarts)}/{len(fkdone)}，完整诊断{len(doneids)}/800，UNKNOWN {len(missing)}。"
          f"G0分支/目标{len(g0)}/{len({case[4:7] for case in g0})}，G1分支/目标{len(g1)}/{len({case[4:7] for case in g1})}。\n\n"
          f"first01+run02共享实账wall={first['wall_s']+e['wall_s']:.12f}s、CPU={first['cpu_s']+e['cpu_s']:.12f}s，原30/60上限保留。"
          "原01失败与02输出均未改；未重算FK/IK/Jacobian/SVD/几何分支。矩阵/谱/界/原batch与原始事件只作保存证据核对。"
          "本项不含碰撞、RSS分布、RBS或规划，不认定P4完整复现。\n")
    with out.with_suffix('.md').open('x') as f:f.write(text)
    print(json.dumps({k:report[k] for k in ('status','checks_total','checks_passed','checks_failed','scientific_run_original_status','scientific_run_original_component_gate')},ensure_ascii=False))


if __name__=='__main__':main()
