#!/usr/bin/env python3
"""Narrow saved PRE append-identity addendum; reuse14 completed checks."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
OLD=ROOT/'reports/P4_D080_ENV_V_PCS_LOCAL01_COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_20261018.json'
OLD_SHA='0f2d2677718d62b3830043826e8c0ee057045a66aef1403b428ed013f62d97df'
PRE=ROOT/'reports/P4_D080_ENV_V_PCS_LOCAL01_SAVED_QUEUE_PRE_DRAFT_20261018.md'
PRE_SHA='74108769809ee43948789edf19fdb86db3fc6ee258fdff056b2265d0c8d0a597'
OUT=ROOT/'reports/P4_D080_ENV_V_PCS_LOCAL01_COMPLETE_QUEUE_SAVED_INDEPENDENT_PRE_ADDENDUM_20261018.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(name,value):return dict(check=name,passed=bool(value))
def main():
 if OUT.exists()or OUT.with_suffix('.md').exists():raise FileExistsError('EXCLUSIVE_PRE_IDENTITY_ADDENDUM')
 old=json.loads(OLD.read_bytes());b=PRE.read_bytes();prefix=b[:1936];suffix=b[1936:]
 checks=[ck('original15-check FAIL preserved with sole PRE identity mismatch and14 passes',sha(OLD)==OLD_SHA and old['checks_total']==15 and old['checks_passed']==14 and old['checks_failed']==1 and old['failures']==[dict(check='exact reviewed inputs and personnel independent source transport194 reused',passed=False)]),ck('original1936byte PRE prefix exact03cd hash; actual appendedPRE exact7410 hash',hashlib.sha256(prefix).hexdigest()=='03cdcbf00ed143ad8f8e0b61dbd830cfec862205546347987e3c3dc5f2c24c34'and sha(PRE)==PRE_SHA),ck('suffix is only one actual materialization outcome paragraph no condition edits',suffix.startswith('\n2026-10-18保存数据物化结果（非新科学）：'.encode())and suffix.count(b'\n')==2 and b'c8d9e38b0354d64276fbfc15f47748ec58aa9be12bf862557325acab3a4e44c7'in suffix and b'6fa6da08e32e92068bad12346e14cf4d68440c6c205147937ea8c912daec8e35'in suffix and all(v.encode()in suffix for v in('完整union24节点','全部29次','34次collision','6次/3唯输入','3309条','62项','24条true','strict full12 L2<.05','不能据此改判'))),ck('all prior byte inputs including source/queue/PRE unchanged since14 completed checks',all(sha(n)==h for n,h in old['retained_sha256'].items()))]
 failed=[x for x in checks if not x['passed']]
 summary={k:old[k]for k in('stats','maximum_independent_fsum_vs_saved_distance_difference_rad','maximum_independent_fsum_vs_saved_distance_difference_ULP','source_projection_true','source_projection_false','source_public_RBS_true','source_public_RBS_false','source_public_RBS_dependency_not_executed','source_public_reconstruct_true','source_public_reconstruct_false','source_public_reconstruct_dependency_not_executed')}
 report=dict(schema='P4_D080_V_PCS_LOCAL01_COMPLETE_QUEUE_SAVED_PERSONNEL_INDEPENDENT_PRE_V1',status='PASS_SAVED_QUEUE_ONLY_PENDING_PHYSICAL_PROTOCOL'if not failed else'FAIL_PRE_IDENTITY_ADDENDUM_RETAINED',personnel_independent=True,reviewer='/root/sbl_independent_resume independent of saved queue/materializer author',checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),checks=checks,failures=failed,reused_prior14_checks_without_rerun=dict(path=str(OLD.relative_to(ROOT)),sha256=OLD_SHA,checks=14,original_FAIL_retained=True),materializer=old['materializer'],materializer_sha256=old['materializer_sha256'],queue=old['queue'],queue_sha256=old['queue_sha256'],PRE=str(PRE.relative_to(ROOT)),PRE_sha256=PRE_SHA,original_PRE_prefix_length=1936,original_PRE_prefix_sha256=hashlib.sha256(prefix).hexdigest(),reused_source_transport194=old['reused_source_transport194'],reused_source_transport194_sha256=old['reused_source_transport194_sha256'],independent_local_qualified=False,independent_path_qualified=False,continuous_collision_certificate=False,new_model_compile_binary_FK_J_IK_NR_PQP_RBS_RNG_solve_VI_formal_calls=0,scientific_budget_charge=0,execution_authorized=False,limits=old['limits'],**summary)
 with OUT.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
 with OUT.with_suffix('.md').open('x')as f:f.write('# V LOCAL01 完整保存队列独审PRE身份补记\n\n'+report['status']+'；'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'。\n\n原FAIL仅因作者发送PRE hash后追加实际结果段；原1936字节前缀SHA03cd与当前全文SHA7410均独立确认，条件没有修改。复用原14项树/节点/叶/失败审查，不重复模型或完整保存审。24节点仍待物理冻结；原false与依赖失败不改判。\n')
 print(json.dumps(dict(status=report['status'],checks_failed=len(failed),failures=failed,sha256=sha(OUT))))
 if failed:raise SystemExit(2)
if __name__=='__main__':main()
