#!/usr/bin/env python3
"""S02 independent AST/diff/saved-byte review only; no runner import."""
from pathlib import Path
from collections import Counter
import ast
import base64
import hashlib
import json

ROOT=Path(__file__).resolve().parents[3]
NEW='scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py'
OLD='scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_draft.py'
SUP='scripts/supervise_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py'
OLDSUP='scripts/supervise_p4_full_r2_abb_cbirrt_d_solve_draft.py'
PRE='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE02_PRE_DRAFT_20261016.md'
EXPECTED={NEW:'b204013b29eb88a178bee0333728e5f14c1e239c0cd8a2a2fa6cd1c331b87263',
 SUP:'93e1450c8908e8f05d37e51f2713836f7c5aa6b50031099d0bcbba554acccd84',
 PRE:'f37423aa8f8a97ca20b24affa98c55f781cba113279db877cca6b18ecb21ebfd',
 OLD:'7f0327f56bb86246d22f897743b0b2abad6fd54e9527eb0a55e79fdbe4589a46',
 OLDSUP:'b4c25d0dcb91a7c79efbc5ee0e341e60bd0c2ec068dd3cc1224b4cfe7f135834'}
S01='results/p4_full/20261015_R2_ABB_CBIRRT_D_SOLVE01'

def sha(n):return hashlib.sha256((ROOT/n).read_bytes()).hexdigest()
def load(n):return json.loads((ROOT/n).read_text())

def main():
 checks=[];failed=[];retained={}
 def ck(name,ok,evidence):
  row=dict(id=name,passed=bool(ok),evidence=evidence);checks.append(row)
  if not ok:failed.append(row)
 def bind(n,want=None):
  retained[n]=sha(n)
  if want is not None:ck('sha '+n,retained[n]==want,want)
 def has(name,text,parts):ck(name,all(p in text for p in parts),parts)
 for n,w in EXPECTED.items():bind(n,w)
 texts={n:(ROOT/n).read_text()for n in(EXPECTED)}
 trees={n:ast.parse(texts[n])for n in(NEW,OLD,SUP,OLDSUP)}
 ck('all_four_Python_AST_only',all(isinstance(t,ast.Module)for t in trees.values()),'ast.parse, no runner import/compile/execute')
 defs={n:{x.name:x for x in trees[n].body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}for n in(NEW,OLD)}
 src={k:ast.get_source_segment(texts[NEW],v)for k,v in defs[NEW].items()}
 def equal_function(name):
  ck('AST_unchanged_'+name,ast.dump(defs[NEW][name],include_attributes=False)==ast.dump(defs[OLD][name],include_attributes=False),name)
 for name in('prerequisites','current_prior','endpoints','validate','supervisor_proof','check_response','main'):equal_function(name)
 for name in('__init__','start','finish'):
  new=next(x for x in defs[NEW]['Session'].body if isinstance(x,ast.FunctionDef)and x.name==name)
  old=next(x for x in defs[OLD]['Session'].body if isinstance(x,ast.FunctionDef)and x.name==name)
  ck('Session_AST_unchanged_'+name,ast.dump(new,include_attributes=False)==ast.dump(old,include_attributes=False),name)
 raw=(ROOT/S01/'source_stdout.bin').read_bytes();bind(S01+'/source_stdout.bin')
 assignment=next(x for x in trees[NEW].body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PREAMBLE'for t in x.targets))
 ck('exact_original_55_byte_preamble',ast.literal_eval(assignment.value)==raw==b'Debug:   CBiRRT: Planner range detected to be 3.415829\n'and len(raw)==55,raw.decode())
 e=load(S01+'/execution.json');bind(S01+'/execution.json','99c5cc5e980bf52489b154d5a678df903a1897a1e9e966c341ea6b5229533fdd')
 charge=load(S01+'.supervision.charge.json');bind(S01+'.supervision.charge.json')
 ck('original_actual_STOP_JSONDecode_minus9_retained',e['status']=='STOP_PREFIX_RETAINED'and e['termination_reason']=="JSONDecodeError('Expecting value: line 1 column 1 (char 0)')"and e['source_process_registry']==[dict(pid=78833,reaped=True,returncode=-9)]and e['complete_source_raw_evidence_gate']is False,
  'Original source01 failure was not reclassified')
 ck('original_dispatched_one_source_attempt',e['counts']['solve_dispatched']==1,'Original raw_response_lines_observed=1 was nonJSON, not successful response')
 ck('shared_original_charge_exact',charge['time_fields']==['1.43','0.93','0.19','1']and charge['wall_s']==1.44 and charge['cpu_s']==1.14,'Shared remaining 28.56/58.86, not renewed30/60')
 has('previous_stop_full_raw_recipe_and_diagnosis_bound',src['previous_stop'],[
  'sha(S01+\'/execution.json\')==S01_EXEC_SHA','old.path(S01).rglob(\'*\')',"S01+'.supervision.time.txt'",
  "S01+'.supervision.jsonl'","S01+'.supervision.stderr.log'","S01+'.supervision.charge.json',DIAGNOSIS",
  "e['bound_files_sha256']==e['bound_files_after_sha256']","files.update(e['bound_files_sha256'])",
  'original_source_solve_entered=True',"original_source_solve_completed='UNOBSERVED'"])
 has('protocol_exact_shared_remainder_and_one_request',src['draft_protocol'],[
  'previous=previous_stop()',"**previous['files_sha256']",'wall_s=28.56,cpu_s=58.86,child_cpu_limit_s=60',
  'new_processes=1,source_requests=1,solve_calls=1,source_seed=7,source_solve_seconds=10.',
  "unknown_or_duplicate_or_tail='STOP_RETAIN_ALL_RAW'"])
 has('Budget_shared28_56_58_86_and_totalR2',src['Budget'],[
  "self.wall_cap=min(28.56,3600.-spec['previous_r2_wall_s'])",
  "self.cpu_cap=min(58.86,7200.-spec['previous_r2_cpu_s'])"])
 session=defs[NEW]['Session'];query=next(x for x in session.body if isinstance(x,ast.FunctionDef)and x.name=='query');q=ast.get_source_segment(texts[NEW],query)
 has('one_dispatch_with_no_retransmission',q,["self.counts['solve_dispatch_attempted']+=1",'sent=os.write(self.proc.stdin.fileno(),raw)',"self.counts['solve_dispatched']+=1",'INCOMPLETE_REQUEST_NO_RETRY'])
 ck('exactly_one_request_write_site',q.count('os.write(')==1,'Outer line receive loop never writes another request')
 has('every_complete_stdout_line_raw_before_classification',q,["self.journal.add('raw_stdout_line',bytes=len(rawline),base64=base64.b64encode(rawline).decode())",'if rawline==PREAMBLE:'])
 ck('raw_before_preamble_classification',q.index("self.journal.add('raw_stdout_line'")<q.index('if rawline==PREAMBLE:'),'No original stdout discarded')
 has('only_exact_once_before_response_preamble_accepted',q,[
  'if rawline==PREAMBLE:',"self.counts['setup_preamble_lines_observed']+=1",
  "self.counts['setup_preamble_lines_observed']==1 and self.counts['raw_response_lines_observed']==0",
  'DUPLICATE_OR_LATE_SETUP_PREAMBLE_NO_SKIP',
  "self.counts['setup_preamble_lines_observed']==1 and line.startswith(b'{')",
  'UNKNOWN_STDOUT_LINE_OR_MISSING_EXACT_PREAMBLE_NO_SKIP'])
 has('response_raw_before_parse_and_count_after_parse',q,["self.journal.add('raw_response_line'",'response=json.loads(line)',"self.counts['raw_response_lines_observed']+=1"])
 ck('response_parse_order',q.index("self.journal.add('raw_response_line'")<q.index('response=json.loads(line)')<q.index("self.counts['raw_response_lines_observed']+=1"),'Malformed JSON remains raw STOP, never completed response')
 ck('no_broad_stdout_cleanup',not any(token in q for token in('re.match','re.search','strip(',"startswith(b'Debug'","startswith(b'Info'")),
  'No regex, trim, wildcard logger filtering or swallowing unknown lines')
 execute=src['execute']
 has('normal_final_stdout_exact_two_lines',execute,["len(lines)==2 and lines[0]==PREAMBLE and lines[1].endswith(b'\\n')and exact(json.loads(lines[1]),response)",
  "counts['stdout_complete_lines_observed']==2 and counts['setup_preamble_lines_observed']==1",
  "counts['solve_dispatched']==counts['raw_response_lines_observed']==1"])
 has('original_post_response_EOF_pending_gate_kept',execute,[
  "session.finish(normal=True)","not session.pending","'STOP_PROCESS_EOF_OR_EXIT_UNQUALIFIED'",
  'RAW_BODY_TRACE_MUST_MATCH_FULL_SOURCE_RESPONSE'])
 has('before_after_source_and_prior_hashes_stay_mandatory',execute,[
  'BOUND_ASSET_CHANGED','RECIPE_CHANGED','PRIOR_OR_AUTHORITATIVE_LEDGER_CHANGED',
  "record['protocol_after_sha256']=sha(protocol);record['claim_after_sha256']=sha(claim)"])
 has('final_internal_and_receipt_shared_caps',execute,[
  "record['wall_s']>=min(28.56,3600.-spec['previous_r2_wall_s'])",
  "record['cpu_s']>=min(58.86,7200.-spec['previous_r2_cpu_s'])",
  "receipt['wall_s_through_execution_persistence']>=min(28.56,3600.-spec['previous_r2_wall_s'])",
  "receipt['cpu_s_through_execution_persistence']>=min(58.86,7200.-spec['previous_r2_cpu_s'])"])
 has('exact_source_status_and_independent_path_false_unchanged',src['check_response'],[
  'SOURCE_EXACT_PENDING_INDEPENDENT_PATH_AUDIT','SOURCE_NONEXACT_RETAINED_PREFIX',"response['independent_path_qualified']is False"])
 # Normalize only explicit supervisor metadata/caps. Remaining source must be
 # byte-for-byte the old independently reviewed implementation.
 normalized=texts[SUP].replace("RUN='20261015_R2_ABB_CBIRRT_D_SOLVE02'","RUN='20261015_R2_ABB_CBIRRT_D_SOLVE01'")
 normalized=normalized.replace('scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_v2_draft.py','scripts/qualify_p4_full_r2_abb_cbirrt_d_solve_draft.py')
 normalized=normalized.replace('finite28.56/58.86','finite30/60').replace('P4_R2_ABB_CBIRRT_D_SOLVE02_EXTERNAL_COST_CHARGE_V2','P4_R2_ABB_CBIRRT_D_SOLVE_EXTERNAL_COST_CHARGE_V1')
 normalized=normalized.replace('wall<=min(28.56,3600.','wall<=min(30.,3600.').replace('cpu<=min(58.86,7200.','cpu<=min(60.,7200.')
 ck('supervisor_only_explicit_identity_schema_caps_delta',normalized==texts[OLDSUP],'O_EXCL FD, actual PID/argv/inode, GNUtime wait, Decimal upper bounds unchanged')
 pre=texts[PRE]
 has('PRE_truthful_started_solve_and_temporary_setup_range',pre,[
  '不能把本项说成0solve','setRange(Range)','将实际grow范围设回2.6','第二次版本化入口尝试','无自动第三次'])
 has('PRE_no_new_algorithm_compile_or_budget',pre,[
  '不改现有binary、driver、observer、OMPL、原算法或任何科学阈值','精确余28.56wall/58.86CPU','所有211项原文义务','不开展RSS新VI构造、P2或Isaac'])
 diagnosis='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE01_STDOUT_SOURCE_DIAGNOSIS_20261016.json';bind(diagnosis,'cd257201d77757ee6b7fa0c6aca73859afe7813603f171c58b591e438cb4bfd7')
 static='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE01_STDOUT_LIBRARY_STATIC_SUPPLEMENT_20261016.json';bind(static)
 diag=load(diagnosis);ck('saved_independent_source_entry_and_no_finalJSON',diag['source_solve_started']is True and diag['actual_final_JSON_response_count']==0 and diag['source_solve_completed']=='UNKNOWN_NO_FINAL_RESPONSE','Saved raw41 prefix, not outcome')
 oldreview='reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE_INDEPENDENT_STATIC_REVIEW_20261016.json';bind(oldreview,'0ecb673be83c757a237ded397fc17a13d662f1764ded93e48b56a23f5feb68c9')
 prior=load(oldreview);ck('original_complete_static_evidence_reused',prior['status']=='PASS_STATIC_DRAFT_ONLY_NO_EXECUTION'and prior['checks_passed']==prior['checks_total']==55 and prior['checks_failed']==0,'Original static55 did not detect transport preamble; original FAIL remains')
 ck('current_sources_unchanged_during_static_review',all(sha(n)==w for n,w in EXPECTED.items()),'Locked exact S02/S01 source/PRE hashes')
 report=dict(schema='P4_SOLVE02_INDEPENDENT_STATIC_REVIEW_V1',status='PASS_STATIC_VERSIONED_TRANSPORT_FIX_NO_EXECUTION'if not failed else'STOP_STATIC_FINDINGS',
  reviewer='nr_path_prepare: not S02 runner/supervisor/PRE implementer',personnel_independent=True,
  reviewed_source_sha256=EXPECTED,retained_sha256=retained,checks_total=len(checks),checks_passed=len(checks)-len(failed),checks_failed=len(failed),failures=failed,full_checks=checks,
  new_runner_import_describe_protocol_prior_claim_compile_scientific_calls=0,external_supervision_qualified=False,independent_path_qualified=False,
  qualifications=['Only versioned transport correction; immutable source01 remains failed and source solve result UNKNOWN.',
   'One new process/request with the same II/seed7/10s source conditions; original shared budget remaining28.56wall/58.86CPU, latest totalR2 ledger still required.',
   'Exact preamble whitelist accepts the original55bytes only once before the one realJSON. Unknown/duplicate/tail remains STOP.',
   'Static review is not actual execution qualification; native exact still pending complete saved double-tree and independent physical path P.'])
 out=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_SOLVE02_INDEPENDENT_STATIC_REVIEW_20261016.json'
 with out.open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({k:report[k]for k in('status','checks_total','checks_passed','checks_failed','personnel_independent')}))

if __name__=='__main__':main()
