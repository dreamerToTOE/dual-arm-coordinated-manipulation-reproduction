#!/usr/bin/env python3
"""Saved engineering POST only. No candidate imports, compiler, model or binary calls."""
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[3]
RUN='20261018_R2_D080_III_RRT_PCS_BUILD01'
EP='results/p4_full/'+RUN+'/execution.json'
PROTOCOL='configs/p4_d080/iii_rrt_pcs_e2e_build_v1.json'
PRE='reports/P4_D080_ENV_III_RRT_PCS_EXECUTOR_INCREMENTAL_INDEPENDENT_PRE_20261018.json'
MANIFEST='results/p4_full/'+RUN+'/compiler_evidence_saved/manifest.json'
EXPECTED_COMMIT='77d37499d8d6029a0095cef763027863cf5fe961'
checks=[];retained={}
def p(n):
    q=Path(n);return q if q.is_absolute() else ROOT/q
def raw(n):
    data=p(n).read_bytes();retained[str(p(n))]=hashlib.sha256(data).hexdigest();return data
def sha(n):return hashlib.sha256(raw(n)).hexdigest()
def js(n):return json.loads(raw(n))
def ck(n,v,e=None):checks.append(dict(name=n,passed=bool(v),evidence=e))
def group_members(g):
    out=[]
    for q in Path('/proc').glob('[0-9]*/stat'):
        try:
            a=q.read_text().rsplit(')',1)[1].split()
            if int(a[2])==g:out.append(int(q.parent.name))
        except (OSError,ValueError,IndexError):pass
    return sorted(out)
def md(data):
    if not data.endswith(b'\n') or any(z in data for z in [b'\r',b'$',b'#']):raise ValueError('SUPPORTED_GCC_MD_REQUIRED')
    logical=data.replace(b'\\\n',b' ').rstrip(b'\n');lexer=re.compile(rb'(?:\\[ \t#:\\]|[^ \t\r\n\\#$:\x00-\x1f\x7f])+|:')
    end=0;tokens=[]
    for m in lexer.finditer(logical):
        if logical[end:m.start()].strip(b' \t'):raise ValueError('UNPARSED_MD')
        v=m.group();end=m.end();tokens.append(v if v==b':' else re.sub(rb'\\([ \t#:\\])',lambda z:z.group(1),v))
    if logical[end:].strip(b' \t') or tokens.count(b':')!=1 or tokens.index(b':')!=1:raise ValueError('EXACT_ONE_MD_TARGET_REQUIRED')
    return str(Path(os.fsdecode(tokens[0])).resolve()),[str(Path(os.fsdecode(z)).resolve(strict=True)) for z in tokens[2:]]
e=js(EP);s=js(PROTOCOL);pre=js(PRE);plan=js(s['plan']);folder=p(EP).parent
c=js(folder/'claim.json');i=js(folder/'cost_receipt.json');ext=s['external_supervision'];r=js(ext['charge_path']);t=e['targets'][0]
ck('exact_saved_execution_and_expected_frozen_source_protocol',sha(EP)=='16696c0d80ce0ac893814afc2ca5e0720e6ebb478da63cc6e46eb8f7b80c4f31' and sha(PROTOCOL)==e['protocol_sha256']==e['protocol_after_sha256']=='4c6fa136d7a9097c8386bc094a6379501caf9df91efbd9bf90a4d3991a21b50e' and e['source_commit']==c['source_commit']==EXPECTED_COMMIT)
ck('reuse_exact_personnel_independent_thin_PRE23_without_older_body_reaudit',sha(PRE)=='1efc7e6f913635da988975fb94961edb1145a670993a5804eede860cecd78eae' and pre['personnel_independent'] is True and pre['checks_total']==pre['checks_passed']==23 and pre['checks_failed']==0)
for n,w in pre['inputs_sha256'].items():ck('same_reviewed_input '+n,sha(n)==w)
ck('frozen_engineering_only_exact45_90_work40_80',s['frozen'] is s['independent_review_passed'] is s['engineering_execution_authorized'] is True and s['scientific_execution_authorized'] is s['formal_execution_authorized'] is False and s['budget']==e['budget']=={'wall_s':45,'cpu_s':90} and s['working_budget']==e['working_budget']=={'wall_s':40,'cpu_s':80} and s['environment']==e['environment']=='III')
draft=js('configs/p4_d080/iii_rrt_pcs_e2e_build_v1.DRAFT.json');cmp=dict(s)
for k in ['status','frozen','independent_review_passed','engineering_execution_authorized','prior','bound_files_sha256','independent_static_review']:cmp.pop(k,None)
before=dict(draft)
for k in ['status','frozen','independent_review_passed','engineering_execution_authorized','prior','bound_files_sha256']:before.pop(k,None)
ck('only_approved_root_freeze_transform_no_changed_scientific_or_build_conditions',cmp==before and all(s['bound_files_sha256'].get(n)==w for n,w in draft['bound_files_sha256'].items()) and s['prior']==pre['allowed_root_only_freeze_transform']['prior'])
for n in ['scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py','scripts/p4_d080/supervise_iii_rrt_pcs_e2e_build_v1_draft.py',s['plan'],s['dependency_union'],PROTOCOL,PRE]:
    ck('committed_actual_bytes '+n,subprocess.check_output(['git','show',EXPECTED_COMMIT+':'+n],cwd=ROOT)==raw(n))
ck('original_claim_STARTED_immutable_and_success_engineering_only',c['status']=='STARTED' and sha(folder/'claim.json')==e['claim_sha256']==e['claim_after_sha256'] and e['status']==i['status']==t['status']=='BUILT_NOT_QUERIED' and e['engineering_only'] is True and e['execution_type']=='engineering' and e['diagnostics']==[] and e['author_original_planning_qualified'] is False)
ck('runtime_before_after_frozen929_maps_equal_without_duplicate_full_hash_sweep',e['bound_files_sha256']==e['bound_files_after_sha256']==s['bound_files_sha256'] and len(s['bound_files_sha256'])==929)
copies={z['destination']:z['sha256'] for z in plan['copy_exact_assets']}
ck('exact32_copied_source_mesh_assets_current_bytes_and_saved_prepost',len(copies)==32 and t['source_sha256']==copies and all(sha(z['source'])==sha(z['destination'])==z['sha256']==e['staged_after_sha256'][z['destination']] for z in plan['copy_exact_assets']))
ck('exact_single_target_six_serial_success_commands',len(e['targets'])==1 and len(t['commands'])==6 and [z['argv'] for z in t['commands']]==s['commands'] and all(z['returncode']==0 and z['cwd']==str(Path(s['binary']).parent) for z in t['commands']) and t['new_compile_calls']==5 and t['new_link_calls']==1 and t['binary_execution_calls']==0)
all_deps={};actual_paths=set();objnames=[];missing=[]
for index,(unit,obj,dep) in enumerate(zip(plan['compile_units'],t['objects'],t['dependencies'])):
    objnames.append(unit['object']);dpath=unit['dependency'];target,paths=md(raw(dpath));observed={n:sha(n) for n in paths};actual_paths.update(paths);all_deps.update(observed);all_deps[dpath]=sha(dpath)
    ck('TU'+str(index)+' actual_MD_independent_parse_and_saved_hashes',target==unit['object'] and paths[0]==unit['source'] and dep['target']==target and dep['source']==unit['source'] and dep['raw_sha256']==sha(dpath) and dep['actual_dependencies_sha256']==observed)
    first=folder/('unit_'+str(index)+'_first_collected.json');ob=raw(unit['object'])
    ck('TU'+str(index)+' first_collected_object_SHA_size_and_relocatable_ELF',js(first)==obj and sha(first)==e['immediate_object_collection_receipts_sha256'][str(first.relative_to(ROOT))] and obj['index']==index and obj['object']==unit['object'] and obj['dependency']==dpath and obj['object_sha256']==sha(unit['object'])==e['staged_after_sha256'][unit['object']] and obj['dependency_sha256']==sha(dpath) and obj['object_size_bytes']==len(ob) and obj['collection']=='IMMEDIATELY_AFTER_SAVED_SUCCESSFUL_COMPILE_BEFORE_DEPENDENCY_GATE' and ob[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',ob,16)[0]==1 and struct.unpack_from('<H',ob,18)[0]==62)
    for n,w in observed.items():
        if n in copies:
            if copies[n]!=w:missing.append(n)
        elif s['bound_files_sha256'].get(n)!=w:missing.append(n)
ck('five_actual_MD_union_complete677_files_and_all_prebound',len(t['dependencies'])==len(t['objects'])==5 and all_deps==e['dependencies_after_sha256'] and len(all_deps)==677 and not missing,{'actual_dependency_paths':len(actual_paths),'unbound_paths':sorted(set(missing))})
binary=raw(s['binary'])
ck('one_link_ELF64_exact_hash_and_five_expected_objects',t['binary']==s['binary'] and t['binary_sha256']==sha(s['binary'])==e['staged_after_sha256'][s['binary']] and binary[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',binary,18)[0]==62 and all(s['commands'][-1].count(n)==1 for n in objnames))
ck('staged_map_exact32copies_five_objects_oneELF_current_bytes',set(e['staged_after_sha256'])==set(copies)|set(objnames)|{s['binary']} and all(sha(n)==w for n,w in e['staged_after_sha256'].items()))
ck('six_groups_exit0_reaped_currently_empty_observed_ticks',len(e['compiler_groups'])==6 and {z['pid'] for z in e['compiler_groups']}=={z['compiler_pid'] for z in t['commands']} and all(z['pid']==z['pgid'] and z['reaped'] is True and z['returncode_after_cleanup']==0 and z['members_after_cleanup']==[] and not group_members(z['pgid']) and (isinstance(z['start_ticks_observation'],int) and z['start_ticks_observation']>0 or z['start_ticks_observation']=='UNKNOWN_PROCESS_EXITED_BEFORE_READ') for z in e['compiler_groups']))
ck('all_twelve_compile_link_stdout_stderr_raw_bytes_retained',len(e['compile_log_sha256'])==12 and all(sha(n)==w for n,w in e['compile_log_sha256'].items()))
prior_manifest=js('configs/p4_d080/iii_rrt_pcs_V34_prior_evidence_v1.DRAFT.json')
ck('latest_V34_before_after179evidence_maps_reused_exact',e['prior']==e['prior_after'] and e['prior']['path']==s['prior']['ledger'] and e['prior']['sha256']==s['prior']['ledger_sha256']==sha(s['prior']['ledger']) and e['prior']['wall_s']==s['prior']['wall_s'] and e['prior']['cpu_s']==s['prior']['cpu_s'] and e['prior']['evidence_sha256']==prior_manifest['evidence_sha256'] and all(s['bound_files_sha256'].get(n)==w for n,w in e['prior']['evidence_sha256'].items()))
archive=js(MANIFEST);expected_archive={**{u['dependency']:sha(u['dependency']) for u in plan['compile_units']},**e['compile_log_sha256']}
ck('stdlib_archive17_originalMD_and_logs_exact_same_bytes_execution_unchanged',sha(MANIFEST)=='a923d6970d00405329c0f12e247ee049df6aeacec0245704b573583cc6f620ff' and archive['saved_only'] is archive['original_execution_unchanged'] is True and archive['new_compile_or_model_calls']==0 and archive['execution_sha256']==sha(EP) and len(archive['files'])==17 and {z['source_absolute_path']:z['source_sha256'] for z in archive['files']}==expected_archive and all(raw(z['source_absolute_path'])==raw(z['archived_relative_path']) and sha(z['archived_relative_path'])==z['archived_sha256']==z['source_sha256'] and len(raw(z['archived_relative_path']))==z['bytes'] for z in archive['files']))
fields=raw(ext['sibling_path']).decode().split();elapsed,user,system=map(Decimal,fields[:3]);exitcode=int(fields[3])
rawwall=elapsed+Decimal('.01');rawcpu=user+system+Decimal('.02')
walls=[rawwall,Decimal(str(r['fallback_observed_outer_wait_wall_s']))+Decimal('.01'),Decimal(str(i['wall_s_through_execution_persistence']))+Decimal('.01')]
cpus=[rawcpu,Decimal(str(r['fallback_reaped_children_CPU_s']))+Decimal('.02'),Decimal(str(i['cpu_s_through_execution_persistence']))+Decimal('.02')]
upperwall=float(max(walls));uppercpu=float(max(cpus));components={'wall_decimal_s':[str(v) for v in walls],'cpu_decimal_s':[str(v) for v in cpus],'order':['raw_GNUtime_plus_padding','outer_monotonic_or_reaped_plus_padding','internal_receipt_plus_padding']}
ck('exact_finite_Decimal_three_observation_envelope_and_local_R2_caps',all(v.is_finite() and v>=0 for v in walls+cpus) and upperwall==r['wall_s']==22.0565060610004 and uppercpu==r['cpu_s']==34.199148 and r['monotonic_envelope_components']==components and r['raw_GNUtime_upper_wall_s']==float(rawwall) and r['raw_GNUtime_upper_cpu_s']==float(rawcpu) and upperwall<45 and uppercpu<90 and upperwall+s['prior']['wall_s']<3600 and uppercpu+s['prior']['cpu_s']<7200)
ck('external_charge_receipt_execution_time_links_exact',r['source_execution']==EP and r['execution_sha256']==i['execution_sha256']==sha(EP) and r['receipt_sha256']==sha(r['receipt']) and r['time_file']==ext['sibling_path'] and r['time_sha256']==sha(ext['sibling_path']) and r['time_fields']==fields and r['charge_basis']=='EXTERNAL_MONOTONIC_ENVELOPE_REPLACES_INTERNAL_SAMPLE_ONCE' and r['monotonic_envelope_valid'] is r['timing_valid'] is r['time_inode_unchanged'] is r['wall_CPU_caps_pass'] is r['completed_process_exit0'] is r['started_attempt'] is True and r['time_returncode']==r['measured_child_exit']==exitcode==0 and r['failure'] is r['monotonic_envelope_error'] is None and r['external_supervision_qualified'] is i['external_supervision_qualified'] is False)
lines=raw(ext['metadata_path']).splitlines(keepends=True);events=[json.loads(z) for z in lines];launch,start,reap=events;proof=e['supervisor_contract'];inode=p(ext['sibling_path']).stat()
ck('actual_GNUtime_launch_reap_proven_parent_argv_and_exclusive_inode',len(events)==3 and [z['event'] for z in events]==['planned_launch','time_process_started','time_process_reaped'] and launch['argv']==start['argv']==proof['actual_argv'] and launch['protocol_sha256']==sha(PROTOCOL) and launch['run_id']==RUN and launch['supervisor_pid']==proof['supervisor_pid'] and start['pid']==reap['pid']==r['time_process_pid']==proof['actual_time_pid'] and reap['returncode']==0 and reap['failure'] is None and launch['time_inode']==proof['time_inode']==inode.st_ino and launch['time_device']==proof['time_device']==inode.st_dev and launch['time_fd'] in proof['actual_time_output_fds'] and proof['actual_time_start_ticks']>0 and proof['planned_launch_line_sha256']==hashlib.sha256(lines[0]).hexdigest())
ck('outer_metadata_stderr_hashes_and_actual_supervisor_runner_identity',r['metadata_sha256']==sha(ext['metadata_path']) and r['stderr_sha256']==sha(ext['stderr_path']) and launch['supervisor_source_sha256']==sha('scripts/p4_d080/supervise_iii_rrt_pcs_e2e_build_v1_draft.py') and launch['runner_sha256']==sha('scripts/p4_d080/build_iii_rrt_pcs_e2e_v1_draft.py') and launch['time_binary_sha256']==sha('/usr/bin/time') and launch['python_binary_sha256']==sha('/usr/bin/python3'))
ck('zero_model_binary_rng_planning_formal_VI_execution',all(e[k]==0 for k in ['scientific_calls','query_calls','solve_calls','rng_calls','binary_execution_calls','formal_table_I_calls','new_VI_candidate_constructions']) and e['author_original_planning_qualified'] is False)
for n,w in list(retained.items()):
    if hashlib.sha256(Path(n).read_bytes()).hexdigest()!=w:ck('saved_input_changed_during_audit '+n,False)
failed=[z for z in checks if not z['passed']];ok=not failed
report={'schema':'P4_D080_III_RRT_PCS_BUILD01_SAVED_INDEPENDENT_POST_V1','personnel_independent':True,'status':'PASS_BUILT_NOT_QUERIED_SAVED_ENGINEERING_POST' if ok else 'FAIL_SAVED_ENGINEERING_POST','checks_total':len(checks),'checks_passed':len(checks)-len(failed),'checks_failed':len(failed),'checks':checks,'failures':failed,'engineering_build_qualified':ok,'external_supervision_qualified':ok,'external_timing_qualified':ok,'external_cost_qualified':ok,'source_planning_qualified':False,'independent_path_qualified':False,'source_commit':EXPECTED_COMMIT,'execution':EP,'execution_sha256':sha(EP),'protocol':PROTOCOL,'protocol_sha256':sha(PROTOCOL),'receipt':ext['charge_path'],'receipt_sha256':sha(ext['charge_path']),'external_charge_sha256':sha(ext['charge_path']),'internal_receipt':r['receipt'],'internal_receipt_sha256':sha(r['receipt']),'external_time':ext['sibling_path'],'external_time_sha256':sha(ext['sibling_path']),'upper_wall_s':upperwall,'upper_cpu_s':uppercpu,'charge_basis':r['charge_basis'],'new_translation_units':5,'new_link_calls':1,'raw_dependency_and_log_archive':MANIFEST,'raw_dependency_and_log_archive_sha256':sha(MANIFEST),'archive_files':17,'actual_dependency_paths':len(actual_paths),'unfrozen_protected_dependencies':sorted(set(missing)),'reused_independent_static_checks':23,'new_auditor_compile_binary_model_scientific_calls':0,'historical_full_prior_rehash_repeated':False,'retained_sha256':retained,'auditor_sha256':sha(__file__),'limitations':['Engineering only BUILT_NOT_QUERIED; no setup, projection, local connection, planning or independent path qualification.','V34 saved prior evidence maps and runtime unchanged identity reused; no repeated full929 or historical execution hash sweep.','32 fresh copied assets, all5 actual MD dependencies/objects,6 compiler sessions and17 GitHub archive bytes independently verified saved-only.','Original II four paths, V collisions, all old UNKNOWN and VI974/974 retained; formal0/18000.','Cost envelope is whole child including reaped compilers; supervisor own journal/fsync tail excluded as frozen.']}
out=ROOT/'reports/P4_D080_ENV_III_RRT_PCS_BUILD01_SAVED_INDEPENDENT_POST_20261018.json'
with out.open('x') as f:f.write(json.dumps(report,ensure_ascii=False,allow_nan=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'total':len(checks),'failures':failed,'upper_wall_s':upperwall,'upper_cpu_s':uppercpu,'sha256':sha(out)},ensure_ascii=False,indent=2))
