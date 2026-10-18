#!/usr/bin/env python3
"""Review and consume one saved-only helper result; no model or helper rerun."""
from pathlib import Path
import ast
import hashlib
import json
import math
import struct
ROOT=Path(__file__).resolve().parents[3]
SRC='scripts/p4_d080/crosscheck_v_pcs_physical01_source_saved_v1_draft.py';SRC_SHA='94313116c78fc0e781944858da0e6019f904ef40738abd47e52e35b9d41b6d51'
RESULT='reports/P4_D080_ENV_V_PCS_PHYSICAL01_SOURCE_SAVED_CROSSCHECK_20261018.json';RESULT_SHA='1788b0a11a04702dd36621e8418d4b94df9405e06f4d8e88385f52dedf2c6309'
POST='reports/P4_D080_ENV_V_PCS_PHYSICAL01_SAVED_INDEPENDENT_POST_20261018.json';POST_SHA='0a9cdde6f9cee4d625861d4bf2180c315b07b1e253804522a30b9bc8be1a38a9'
OUT=ROOT/'reports/P4_D080_ENV_V_PCS_PHYSICAL01_SOURCE_SAVED_INCREMENTAL_INDEPENDENT_POST_20261018.json'
def path(n):p=Path(n);return p if p.is_absolute()else ROOT/p
def sha(n):return hashlib.sha256(path(n).read_bytes()).hexdigest()
def load(n):return json.loads(path(n).read_bytes())
def key(q):return struct.pack('>12d',*q).hex()
def main():
 if OUT.exists()or OUT.with_suffix('.md').exists():raise FileExistsError('EXCLUSIVE_SOURCE_SAVED_INCREMENTAL_REVIEW')
 j=load(RESULT);post=load(POST);checks=[]
 def ck(n,v):checks.append(dict(check=n,passed=bool(v)))
 tree=ast.parse(path(SRC).read_bytes());imports=[]
 for n in ast.walk(tree):
  if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
  if isinstance(n,ast.ImportFrom):imports.append(n.module)
 ck('exact reviewed helper stdlib only no model process dynamicexecution',sha(SRC)==SRC_SHA and j['script_sha256']==SRC_SHA and set(imports)<={'__future__','argparse','hashlib','json','math','os','pathlib','re','struct'}and not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in('eval','exec','__import__','compile')for n in ast.walk(tree)))
 ck('original author634 report retained peoplefalse and exact core430peopletrue',sha(RESULT)==RESULT_SHA and j['checks_total']==j['checks_passed']==634 and j['checks_failed']==0 and all(r['passed']for r in j['checks'])and j['personnel_independent']is False and sha(POST)==POST_SHA and post['personnel_independent']is True and post['checks_total']==post['checks_passed']==430 and post['checks_failed']==0)
 ck('all31 saved inputs hash exact no5052union or prior scientificreaudit',len(j['inputs_sha256'])==31 and all(sha(n)==h for n,h in j['inputs_sha256'].items()))
 ck('rawsourcecloser remainsUNKNOWN; original gates and no physical promotion',j['position_gate_mm']==j['rotation_matrix_gate']==1e-5 and j['gate_changed']is False and j['new_model_calls']==j['new_binary_calls']==j['new_sampling_or_constructions']==0 and j['independent_local_qualified']is j['independent_path_qualified']is j['continuous_collision_certificate']is j['independent_per_pair_closer_recomputed']is False and j['independent_per_pair_closer_status']=='UNKNOWN_NOT_EXPOSED_BY_SAVED_ADAPTER_VARIANTS')
 records={mode:{r['id']:r for row in load('results/p4_full/20261018_R2_D080_V_PCS_LOCAL01/'+mode+'/parsed_rows.json')for r in row['observed_records']}for mode in('trace','plain')}
 rows=j['collision_occurrences'];ck('all original34permode68 collision identities no skip',len(rows)==68 and all(len([x for x in rows if x['mode']==m])==34 and {x['source_record_id']for x in rows if x['mode']==m}=={i for i,r in records[m].items()if r['kind']=='collision'}for m in records))
 expected_ids=load('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/v_pcs_local_v1/source_transform_manifest.json')['active_pair_identities'];max_tcp_p=max_tcp_r=max_box_p=max_box_r=0.;all_ok=True;group=set();reject=set()
 for r in rows:
  original=records[r['mode']][r['source_record_id']];saved=load('results/p4_full/20261018_R2_D080_V_PCS_PHYSICAL01/node_'+format(r['node_id'],'05d')+'.json');o=original['result'];pairs=o['active_pairs'];poses=saved['poses'];k=key(original['args']['q12']);group.add(r['node_id'])
  canonical=json.dumps(original,sort_keys=True,separators=(',',':'),allow_nan=False).encode();ok=k==key(saved['q12'])==r['binary64_be_key']and hashlib.sha256(canonical).hexdigest()==r['canonical_source_record_sha256']and [[p['first'],p['second']]for p in pairs]==expected_ids and len(pairs)==87 and all(p['pair_index']==i and p['tolerance_mm']==8 and type(p['api_code'])is int and p['api_code']==0 and type(p['closer_than_tolerance'])is bool for i,p in enumerate(pairs))
  aggregate=any(p['closer_than_tolerance']for p in pairs);ok=ok and bool(o['returned'])==aggregate==saved['collision']['collision']and r['true_pairs']==[p for p in pairs if p['closer_than_tolerance']]
  if aggregate:reject.add(r['node_id'])
  for a in range(2):
   tp=max(abs(o['physical_tcp_poses'][a][i][3]-poses[a][i][3])for i in range(3));tr=max(abs(o['physical_tcp_poses'][a][i][l]-poses[a][i][l])for i in range(3)for l in range(3));max_tcp_p=max(max_tcp_p,tp);max_tcp_r=max(max_tcp_r,tr);ok=ok and tp<=1e-5 and tr<=1e-5 and abs(tp-r['tcp_metrics'][a]['position_maxabs_mm'])<=1e-12 and abs(tr-r['tcp_metrics'][a]['rotation_matrix_maxabs'])<=1e-14
  # Independently expanded column formula rather than helper's matrix product.
  x=poses[0];c=math.cos(-3.1416/2);s=math.sin(-3.1416/2);box=[[c*x[i][0]-s*x[i][2],x[i][1],s*x[i][0]+c*x[i][2],x[i][3]+435*x[i][0]+300*x[i][2]]for i in range(3)]+[[0.,0.,0.,1.]]
  bp=max(abs(o['source_box_pose'][i][3]-box[i][3])for i in range(3));br=max(abs(o['source_box_pose'][i][l]-box[i][l])for i in range(3)for l in range(3));max_box_p=max(max_box_p,bp);max_box_r=max(max_box_r,br);ok=ok and bp<=1e-5 and br<=1e-5 and abs(bp-r['box_metrics']['position_maxabs_mm'])<=1e-10 and abs(br-r['box_metrics']['rotation_matrix_maxabs'])<=1e-12
  all_ok=all_ok and ok
 ck('complete68original source qpair87API8mm aggregate TCP box arithmetic independently checked',all_ok and len(group)==17 and reject=={15,19,23})
 ck('source17 exactly14clear3reject andproject7exact1clear6reject partition',j['summary']['source_collision17']==dict(nodes=17,aligned_clear=14,aligned_reject=3,node_ids=sorted(group))and j['summary']['project_only7']==dict(nodes=7,aligned_clear=1,aligned_reject=6,node_ids=sorted(set(range(24))-group)))
 ck('core430 all24diagnostics and9reject unchanged; originalRBSrootsstillfalse',set(post['rejected_node_ids'])=={0,2,15,16,17,19,20,21,23}and post['independent_local_qualified']is post['independent_path_qualified']is False)
 failed=[r for r in checks if not r['passed']];report=dict(schema='P4_D080_V_PCS_PHYSICAL01_SOURCE_SAVED_INCREMENTAL_PERSONNEL_INDEPENDENT_POST_V1',status='PASS_SAVED_SOURCE17_TCP_BOX_PAIR_AGGREGATE_ONLY'if not failed else'FAIL_SOURCE_SAVED_INCREMENTAL_RETAINED',personnel_independent=True,reviewer='/root/sbl_independent_resume independent saved arithmetic review; helper source author remains nonindependent',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,helper=SRC,helper_sha256=SRC_SHA,helper_result=RESULT,helper_result_sha256=RESULT_SHA,reused_physical430_POST=POST,reused_physical430_POST_sha256=POST_SHA,source17_crosscheck_status='PASS_ORIGINAL_SOURCE_POLICY_SAVED_ONLY',summary=j['summary'],maximum_source_TCP_position_error_mm=max_tcp_p,maximum_source_TCP_rotation_error=max_tcp_r,maximum_source_box_position_error_mm=max_box_p,maximum_source_box_rotation_error=max_box_r,independent_local_qualified=False,independent_path_qualified=False,continuous_collision_certificate=False,independent_per_pair_closer_recomputed=False,independent_per_pair_closer_status=j['independent_per_pair_closer_status'],new_model_FK_J_IK_NR_PQP_RBS_compile_binary_solve_RNG_VI_formal_calls=0,core430_rerun_calls=0,helper_execution_calls=1,limitations=j['limitations'])
 with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
 with OUT.with_suffix('.md').open('x')as f:f.write('# V PHYSICAL01 原source17保存一致性独审\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'。\n\nsource17为14clear/3reject，另project-only7为1clear/6reject；原34×2mode记录的87pair/8mm/API0/any closer与保存独立TCP及箱体原式1e-5门相符。独立adapter未暴露逐pair closer，逐pair几何独立重算保持UNKNOWN；local/path仍false，不证明CAD吸盘接触或CCD。\n')
 print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failed),sha256=sha(OUT),failures=failed)))
 if failed:raise SystemExit(2)
if __name__=='__main__':main()
