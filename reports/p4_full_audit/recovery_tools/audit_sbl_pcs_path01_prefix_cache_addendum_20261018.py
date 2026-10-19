#!/usr/bin/env python3
"""Saved-only temporal addendum. Reuse all passed physical checks; no model import."""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
import os

ROOT=Path(__file__).resolve().parents[3]
BASE='reports/P4_FULL_R2_ABB_SBL_PCS_PATH01_PREFIX_SAVED_INDEPENDENT_POST_20261018.json'
RUN='results/p4_full/20261018_R2_ABB_SBL_PCS_PATH01'
OUT='reports/P4_FULL_R2_ABB_SBL_PCS_PATH01_PREFIX_SAVED_INDEPENDENT_POST_ADDENDUM_20261018'
CACHE='/etc/ld.so.cache'
OLD_CACHE='306f8fef1055e6d8c8de8a0dbcd0c8a38cbf29f1748cf83dcfb6bd2efead67de'
NEW_CACHE='24020a6e359e805d6dba2081a8eba874beed11c6d566fd46332d7cff0c697d4d'
checks=[];bound={}


def p(name):
    name=Path(name);return name if name.is_absolute() else ROOT/name


def raw(name):
    b=p(name).read_bytes();bound[str(name)]=hashlib.sha256(b).hexdigest();return b


def load(name):return json.loads(raw(name))
def ck(name,ok):checks.append(dict(check=name,passed=bool(ok)))
def sha(name):return hashlib.sha256(raw(name)).hexdigest()


base=load(BASE);base_sha=sha(BASE)
e=load(RUN+'/execution.json');protocol=load(e['protocol'])
charge=load(RUN+'.supervision.charge.json');receipt=load(RUN+'/cost_receipt.jsonl')
timefields=raw(RUN+'.supervision.time.txt').decode().split()
ck('preserved first audit exactly one current cache mismatch and all other42140 checks passed',base['checks_total']==42141 and base['checks_passed']==42140 and base['checks_failed']==1 and base['failures']==[dict(group='provenance',check='bound asset /etc/ld.so.cache',passed=False)])
ck('first audit personnel independent source execution exact',base['personnel_independent'] is True and base['execution_sha256']==sha(RUN+'/execution.json')=='cee39aae1538742e1ab54e19d28ff42a8de2c4165cf2511bb1477d69847bc1e0')
physical_groups=('node','math','branch','collision','collision_raw','collision_TCP','events','worker','counts','complete','external','source','queue')
ck('all retained physical prefix/raw/branch/matrix/limits/worker groups passed without rerunning',all(base['groups'][g]['total']>0 and base['groups'][g]['total']==base['groups'][g]['passed'] for g in physical_groups))
ck('source STOP261 status and unknown tail never promoted',e['status']=='STOP_FINAL_WALL_OR_CPU_BUDGET' and e['completed_nodes']==e['qualified_nodes']==261 and e['full_queue_checked'] is False and e['independent_path_qualified'] is False and base['independent_path_qualified'] is False)
ck('complete partial262 saved source coverage validated by first audit',base['partial_node_id']==261 and base['partial_source_stage']=='COLLISION_RESPONSE_RETAINED' and base['actual_saved_raw_PQP_queries']==60784 and base['original_counter_PQP_queries']==60552 and base['remaining_unverified_node_ids']==list(range(262,387)))
ck('runtime bound maps exact before and after including original cache',protocol['bound_files_sha256']==e['bound_files_sha256']==e['bound_files_after_sha256'] and e['bound_files_after_sha256'][CACHE]==OLD_CACHE)
mismatches=[];provider_count=0
for name,want in e['bound_files_after_sha256'].items():
    actual=hashlib.sha256(p(name).read_bytes()).hexdigest()
    if actual!=want:mismatches.append(dict(path=name,expected_sha256=want,current_sha256=actual))
    if '.so' in Path(name).name and name!=CACHE:provider_count+=1
ck('only current mismatch is post-run loader cache, all binaries/libs/source/meshes exact',mismatches==[dict(path=CACHE,expected_sha256=OLD_CACHE,current_sha256=NEW_CACHE)] and provider_count>0)
cache_stat=p(CACHE).stat();exec_stat=p(RUN+'/execution.json').stat();time_stat=p(RUN+'.supervision.time.txt').stat()
ck('current cache modified after saved execution and completed external time artifact',cache_stat.st_mtime_ns>exec_stat.st_mtime_ns and cache_stat.st_mtime_ns>time_stat.st_mtime_ns and cache_stat.st_ctime_ns>time_stat.st_mtime_ns)
ck('new cache bytes exact expected and historical manifest unchanged',sha(CACHE)==NEW_CACHE and protocol['bound_files_sha256'][CACHE]==OLD_CACHE)
dpkg_bytes=Path('/var/log/dpkg.log').read_bytes()
dpkg_lines=[s for s in dpkg_bytes.decode().splitlines() if s.startswith(('2026-10-18 14:43:48 ','2026-10-18 14:43:49 '))]
ck('saved dpkg evidence records later libbluetooth configuration and libc-bin trigger','2026-10-18 14:43:49 status installed libbluetooth3:amd64 5.64-0ubuntu1.6' in dpkg_lines and '2026-10-18 14:43:49 trigproc libc-bin:amd64 2.35-0ubuntu3.15 <none>' in dpkg_lines)
timezone_text=raw('/etc/timezone').decode().strip()
ck('dpkg local timestamp timezone identified Asia Shanghai',timezone_text=='Asia/Shanghai')
ck('cache mtime corroborates recorded later trigger minute',datetime.fromtimestamp(cache_stat.st_mtime,timezone.utc).strftime('%Y-%m-%d %H:%M')=='2026-10-18 06:43' and datetime.fromtimestamp(time_stat.st_mtime,timezone.utc).strftime('%Y-%m-%d %H:%M')=='2026-10-18 06:41')
queue_file=RUN+'/complete_original_saved_queue.json';queue=load(queue_file)
ck('entire original fullqueue binary64 retained exact protocol',queue==protocol['fixed_queue'] and queue['full_queue_node_count']==387 and len(queue['nodes'])==387 and queue['source_milestone_count']==6 and queue['source_attempt_count']==6)
ck('original false/fallback and unknown native connect metadata remain', [v['returned'] for v in queue['all_original_attempts']]==[True,True,True,True,False,True] and queue['source_identity_audit']['native_connect_motion_id']==50 and queue['source_identity_audit']['native_connect_role'] is None)
ck('native/aligned disjoint saved observations both0 but native TCP mismatch remains separate',base['native_collision_nodes']==base['aligned_collision_nodes']==0 and base['nodes']==262 and base['maximum_saved_closure_position_mm']<=1e-5 and base['maximum_saved_closure_rotation']<=1e-5)
ck('source exact and all saved unmodified provenance reused, not new qualification solve',base['source_exact'] is True and e['zero_calls']==dict.fromkeys(('IK','NR','projection','RBS','solve','RNG','VI_constructions','formal_table_I'),0))
ck('original supervision/charge/receipt source chain exact',base['external_supervision_qualified'] is True and base['external_charge_sha256']==sha(RUN+'.supervision.charge.json') and base['receipt_sha256']==sha(RUN+'/cost_receipt.jsonl') and charge['execution_sha256']==receipt['execution_sha256']==sha(RUN+'/execution.json'))
ck('original raw exit1 GNUtime not retroactively certified',timefields==charge['time_fields']==['119.80','9.11','0.96','1'] and charge['time_returncode']==charge['measured_child_exit']==1 and charge['completed_process_exit0'] is False and charge['external_supervision_qualified'] is False)
elapsed,user,system=map(Decimal,timefields[:3])
wall_components=dict(raw_GNUtime_plus_padding=elapsed+Decimal('.01'),outer_monotonic_plus_padding=Decimal(str(charge['fallback_observed_outer_wait_wall_s']))+Decimal('.01'),receipt_monotonic_plus_padding=Decimal(str(receipt['wall_s_through_execution_persistence']))+Decimal('.01'))
cpu_components=dict(raw_GNUtime_user_system_plus_padding=user+system+Decimal('.02'),outer_reaped_CPU_plus_padding=Decimal(str(charge['fallback_reaped_children_CPU_s']))+Decimal('.02'),receipt_CPU_plus_padding=Decimal(str(receipt['cpu_s_through_execution_persistence']))+Decimal('.02'))
wall=float(max(wall_components.values()));cpu=float(max(cpu_components.values()))
ck('independent Decimal max envelope exact matches first external checks',wall==base['upper_wall_s']==122.08026397300002 and cpu==base['upper_cpu_s']==10.098723)
ck('wall cap breached and raw GNUtime under-count explicitly retained',float(wall_components['raw_GNUtime_plus_padding'])<e['wall_s']<receipt['wall_s_through_execution_persistence']<wall and wall>e['budget']['wall_s']==120 and cpu<e['budget']['cpu_s']==240)
ck('conservative envelope within original remaining aggregate budget',e['previous_r2_wall_s']+wall<3600 and e['previous_r2_cpu_s']+cpu<7200)
stderr=raw(RUN+'.supervision.stderr.log').decode()
ck('actual termination stack preserves wall alarm in fsync without asserting measured IO breakdown',all(s in stderr for s in ('D64_AGGREGATE_HARD_WALL_CAP','os.fsync(f.fileno())',"node_{i:05d}_collision_response.json")))
ck('original source journal and complete worker cleanup unchanged',base['groups']['worker']['total']==base['groups']['worker']['passed'] and e['complete_collision_worker_cleanup_gate'] is True and all(v['reaped'] is True and v['returncode']==0 for v in e['collision_worker_registry']))
ck('D080 formal0 VI0 and original full path unqualified',e['formal_table_I_calls']==e['new_VI_candidate_constructions']==0 and protocol['D080_scope']['formal_table_I_original']==22500 and protocol['D080_scope']['formal_table_I_D080']==18000 and e['continuous_collision_certificate'] is False)
ck('current cache stable through incrementally saved-only review',sha(CACHE)==NEW_CACHE and p(CACHE).stat().st_mtime_ns==cache_stat.st_mtime_ns)
for name,want in list(bound.items()):ck('incremental input immutable '+name,hashlib.sha256(p(name).read_bytes()).hexdigest()==want)
failures=[c for c in checks if not c['passed']];passed=not failures
metrics={k:base[k] for k in ('maximum_full12_leaf_rad','maximum_saved_closure_position_mm','maximum_saved_closure_rotation','minimum_source_mechanical_margin_rad','branch_sets_encountered','native_collision_nodes','aligned_collision_nodes','actual_saved_raw_PQP_queries','original_counter_PQP_queries')}
drift=dict(path=CACHE,historical_sha256=OLD_CACHE,current_sha256=NEW_CACHE,execution_after_matches_historical=True,mtime_UTC=datetime.fromtimestamp(cache_stat.st_mtime,timezone.utc).isoformat(),mtime_ns=cache_stat.st_mtime_ns,ctime_ns=cache_stat.st_ctime_ns,external_time_file_mtime_UTC=datetime.fromtimestamp(time_stat.st_mtime,timezone.utc).isoformat(),dpkg_evidence=dict(source='/var/log/dpkg.log',source_observed_sha256=hashlib.sha256(dpkg_bytes).hexdigest(),local_timezone=timezone_text,relevant_lines=dpkg_lines),only_current_mismatch=True,actual_bound_shared_library_files_unchanged=provider_count,scope='Historical run remains bound to original before/after manifest. New cache is a future-run input only; no retrospective rewrite. Package-trigger correspondence supports post-run cause; not a claim of exact ldconfig syscall observation.')
report=dict(schema='P4_SBL_PCS_PATH01_PREFIX_SAVED_INDEPENDENT_POST_ADDENDUM_V1',status='PASS_COMBINED_SAVED_PREFIX262_AND_MONOTONIC_ACCOUNTING' if passed else 'FAIL_PREFIX_CACHE_TEMPORAL_ADDENDUM',generated_at_utc=datetime.now(timezone.utc).isoformat(),personnel_independent=True,reviewer='sbl_independent_resume',checks_total=len(checks),checks_passed=len(checks)-len(failures),checks_failed=len(failures),checks=checks,failures=failures,reused_base_POST=BASE,reused_base_POST_sha256=base_sha,base_failed_check_preserved=base['failures'],base_passed_checks_reused_without_rerun=42140,source_full_queue=queue_file,source_full_queue_sha256=sha(queue_file),execution=RUN+'/execution.json',execution_sha256=sha(RUN+'/execution.json'),source_commit=e['source_commit'],protocol=e['protocol'],protocol_sha256=sha(e['protocol']),external_time=RUN+'.supervision.time.txt',external_time_sha256=sha(RUN+'.supervision.time.txt'),external_charge_sha256=sha(RUN+'.supervision.charge.json'),internal_receipt_sha256=sha(RUN+'/cost_receipt.jsonl'),charge_basis='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE',upper_wall_s=wall,upper_cpu_s=cpu,wall_components_decimal_s={k:str(v) for k,v in wall_components.items()},cpu_components_decimal_s={k:str(v) for k,v in cpu_components.items()},external_supervision_qualified=passed,external_timing_qualified=False,conservative_monotonic_envelope_cost_qualified=passed,execution_cap_breach_retained=True,scientific_run_within_local_budget=False,completed_process_exit0=False,independent_path_qualified=False,continuous_collision_certificate=False,saved_prefix_qualified=passed,partial_path_prefix_qualified=passed,independent_prefix_node_ids=list(range(262)) if passed else [],independently_saved_qualified_node_ids=list(range(262)) if passed else [],independently_saved_qualified_nodes=262 if passed else 0,original_execution_completed_nodes=261,original_execution_qualified_nodes=261,remaining_unverified_node_ids=list(range(262,387)),remaining_unverified_nodes=125,source_execution_status=e['status'],full_queue_nodes=387,post_run_loader_cache_drift=drift,metrics=metrics,retained_sha256=bound,new_runner_model_import_scientific_compile_describe_calls=0,limits=['First FAIL and original STOP remain immutable. This addendum qualifies262 saved points only by reusing passed first-audit physical groups and resolving post-run cache chronology.','Partial id261 interrupted fsync success stays UNKNOWN; current complete bytes and saved duplicate/math/raw evidence support saved-only independent point qualification.','Raw GNUtime elapsed cannot bound monotonic full child cost. Clock discrepancy exact cause UNKNOWN; monotonic envelope conservatively charges actual local120 breach.','No full source-policy start-to-goal path, no CCD/performance/formal statistics, no VI/P2/Isaac/FR3 execution.'])
with p(OUT+'.json').open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
with p(OUT+'.md').open('x') as f:f.write('# SBL PATH01 保存前缀与计费增量补记\n\n'+report['status']+'；增量'+str(report['checks_passed'])+'/'+str(report['checks_total'])+'。复用首版已通过42140项，不重跑物理或审计。\n\n原PATH01仍STOP：261点final通过，第262点原fsync中断但完整数学/raw碰撞及重复保存现字节通过独立核对；组合保存证书覆盖262/387，余125未验，完整路径未通过。\n\n唯一漂移是运行结束后的/etc/ld.so.cache：原before/after一致，mtime和dpkg后续触发相互支持，所有实际绑定库/二进制/源码均原字节。首版FAIL不改，新run需绑定当前cache。\n\n保守实际费用'+str(wall)+'wall/'+str(cpu)+'CPU，保留120s局部帽超限、GNUtime低估及原因UNKNOWN；监督链可资格，GNUtime完整wall资格=False。正式0/18000，VI仅归档。\n')
print(json.dumps(dict(status=report['status'],checks_total=len(checks),checks_failed=len(failures),output=OUT+'.json',sha256=sha(OUT+'.json'),saved_prefix_qualified=passed,upper_wall_s=wall,upper_cpu_s=cpu)))
if failures:raise SystemExit(1)
