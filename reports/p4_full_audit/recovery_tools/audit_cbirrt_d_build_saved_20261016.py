#!/usr/bin/env python3
"""Read saved D BUILD01 bytes; no compiler, ELF, model or science execution."""
from pathlib import Path
from collections import defaultdict
import ast
import datetime
import hashlib
import json
import math
import struct
import subprocess

ROOT=Path('/home/ubuntu2004/lmy/dual-arm-coordinated-manipulation-p4-full')
RUN=ROOT/'results/p4_full/20261015_R2_ABB_CBIRRT_D_BUILD01'
OUT=ROOT/'reports/P4_FULL_R2_ABB_CBIRRT_D_BUILD01_SAVED_INDEPENDENT_POST_20261016.json'

def main():
    if OUT.exists() or OUT.with_suffix('.md').exists():raise SystemExit('EXISTING_REPORT_PRESERVED')
    checks=defaultdict(lambda:dict(total=0,passed=0));failures=[];retained={}
    def path(n):
        n=Path(n);return n if n.is_absolute() else ROOT/n
    def read(n):
        p=path(n);blob=p.read_bytes();retained[str(p)]=hashlib.sha256(blob).hexdigest();return blob
    def sha(n):return hashlib.sha256(read(n)).hexdigest()
    def load(n):return json.loads(read(n))
    def ck(group,label,ok):
        checks[group]['total']+=1;checks[group]['passed']+=bool(ok)
        if not ok:failures.append(dict(group=group,check=label))
    e=load(RUN/'execution.json');p=load(e['protocol']);c=load(e['claim']);m=load(e['external_manifest'])
    ck('recipe','exact build-only original status',e['status']==m['status']=='BUILT_NOT_QUERIED' and e['classification']=='ENGINEERING_BUILD_ONLY_D_SINGLE_TOKEN_NO_H')
    ck('recipe','frozen explicit reviews',p['frozen'] is True and all(v is True for v in p['reviews'].values()))
    ck('recipe','protocol unchanged',sha(e['protocol'])==e['protocol_sha256']==e['protocol_after_sha256']==c['protocol_sha256'])
    ck('recipe','claim unchanged',sha(e['claim'])==e['claim_sha256']==e['claim_after_sha256'])
    ck('recipe','source commit binding',e['source_commit']==c['source_commit']=='fc3495b89605ac3fb49d05e5f479dc7eceeb4b0e')
    ck('recipe','manifest exact record',sha(e['external_manifest'])==e['manifest_sha256'] and {k:v for k,v in e.items() if k not in ('external_manifest','manifest_sha256')}=={k:v for k,v in m.items() if k!='engineering_execution'} and m['engineering_execution']==str((RUN/'execution.json').relative_to(ROOT)))
    for field in ('own_source_sha256','template_assets_sha256','prior_execution_sha256'):
        after=field.replace('_sha256','_after_sha256')
        ck('hashes',field+' before after equality',e[field]==e[after])
        for n,h in e[field].items():ck('hashes',field+' '+n,sha(n)==h)
    ck('recipe','protocol bound maps',all(p[k]==e[k] for k in ('own_source_sha256','template_assets_sha256','prior_execution_sha256','source_transform_previews','previous_r2_wall_s','previous_r2_cpu_s','budget')))
    for n,h in e['own_source_sha256'].items():
        blob=subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)
        ck('commit','own committed '+n,hashlib.sha256(blob).hexdigest()==h)
    blob=subprocess.check_output(['git','show',e['source_commit']+':'+e['protocol']],cwd=ROOT)
    ck('commit','protocol committed exact',hashlib.sha256(blob).hexdigest()==e['protocol_sha256'])
    prior=[load(n) for n in e['prior_execution_sha256']]
    wall=math.fsum(x['wall_s'] for x in prior);cpu=math.fsum(x['cpu_s'] for x in prior)
    ck('budget','actual29 own-cost prior',len(prior)==29 and wall==e['previous_r2_wall_s'] and cpu==e['previous_r2_cpu_s'])
    ck('budget','aggregate complete cost under original caps',0<=e['wall_s']<min(60.,3600.-wall) and 0<=e['cpu_s']<min(120.,7200.-cpu))
    ck('budget','exact original budget',e['budget']==dict(wall_s=60.,cpu_s=120.,single_wall_s=45.,single_cpu_s=90.,r2_total_wall_s=3600.,r2_total_cpu_s=7200.))
    ck('scope','zero queries runtime solve formal VI',all(e[k]==0 for k in ('query_calls','solve_calls','binary_execution_calls','formal_table_I_calls','new_VI_candidate_constructions')) and p['scientific_execution_authorized'] is False)
    builder=read('scripts/build_p4_full_r2_abb_cbirrt_d_draft.py').decode();bt=ast.parse(builder)
    calls=[n for n in ast.walk(bt) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Popen']
    ck('scope','sole subprocess Popen argv is compiler cmd',len(calls)==1 and isinstance(calls[0].args[0],ast.Name) and calls[0].args[0].id=='cmd' and "cmd=[str(COMPILER)" in builder)
    ck('scope','no builder driver mode dispatch',all(x not in builder for x in ("[target['binary']",'--mode',"Popen(target['binary']")))
    ck('scope','two exact target order',[(x['factor']) for x in e['entries']]==['source_control','distance_destination_fix'])
    summaries=[];source_maps={}
    for x,t in zip(e['entries'],p['targets']):
        f=x['factor'];stage=Path(x['stage']);logs=RUN/f;preview=e['source_transform_previews'][f]
        ck('target',f+' success and caps',x['status']=='BUILT_NOT_QUERIED' and x['exit_code']==0 and 0<=x['wall_s']<45. and 0<=x['cpu_s']<90.)
        ck('target',f+' exact frozen paths',x['stage']==t['stage'] and x['binary']==t['binary'] and f==t['factor'])
        for before,after,base in [('compiled_source_sha256','compiled_source_after_sha256',stage),('mesh_sha256','mesh_after_sha256',stage),('preserved_source_sha256','preserved_source_after_sha256',stage/'preserved_originals')]:
            ck('target',f+' '+before+' unchanged',x[before]==x[after])
            for n,h in x[before].items():ck('target',f+' '+before+' '+n,sha(base/n)==h)
        ck('transform',f+' exact original map',x['preserved_source_sha256']==preview['original_sha256'])
        for n,h in preview['staged_sha256'].items():ck('transform',f+' actual transformed '+n,sha(stage/n)==h and x['compiled_source_sha256'][n]==h)
        sm=load(stage/'source_transform_manifest.json')
        ck('transform',f+' manifest byte bind',sha(stage/'source_transform_manifest.json')==x['source_transform_manifest_sha256'] and sm==preview)
        ck('transform',f+' no H and complete body',sm['H_patch_present'] is False and sm['whole_files_byte_reversible'] is True and sum(y['kind']=='OBSERVE_COMPLETE_BODY' for y in sm['changes'])==13 and sm['observer_model_calls']==sm['observer_RNG_draws']==0)
        ck('transform',f+' single declared temp I/O',sum(y['kind']=='RETAIN_TEMP_IO_ONLY' for y in sm['changes'])==1)
        for n,h in x['all_retained_log_sha256'].items():ck('logs',f+' '+n,sha(logs/n)==sha(stage/n)==h)
        ck('logs',f+' exact stdout stderr hash map',all(x['compile_log_sha256'][n]==x['all_retained_log_sha256'][n] for n in ('compile.stdout','compile.stderr')))
        cmd=x['command'];binary=read(x['binary'])
        ck('ELF',f+' binary hash',hashlib.sha256(binary).hexdigest()==x['binary_sha256'])
        ck('ELF',f+' parse ELF64 little endian x86_64 bytes only',binary[:6]==b'\x7fELF\x02\x01' and struct.unpack_from('<H',binary,18)[0]==62 and struct.unpack_from('<H',binary,16)[0] in (2,3))
        ck('command',f+' compiler output never argv0',cmd[0]=='/usr/bin/x86_64-linux-gnu-g++-11' and cmd[-2:]==['-o',x['binary']] and cmd.count(x['binary'])==1)
        cpp=[z for z in cmd if z.endswith('.cpp')]
        ck('command',f+' only driver and four declared author cpp',cpp==[str(ROOT/'baselines/p4_full/geometry_consistent/abb_cbirrt_d_driver_draft.cpp')]+[str(stage/n) for n in p['linked_author_cpp']])
        ck('target',f+' no runtime path artifacts',not (stage/'paths').exists() and not (stage/'runtime').exists())
        source_maps[f]={n:read(stage/n) for n in preview['staged_sha256']}
        summaries.append(dict(factor=f,wall_s=x['wall_s'],cpu_s=x['cpu_s'],binary_sha256=x['binary_sha256'],compiled_sources_and_headers=len(x['compiled_source_sha256']),meshes=len(x['mesh_sha256']),compile_stdout_bytes=len(read(logs/'compile.stdout')),compile_stderr_bytes=len(read(logs/'compile.stderr'))))
    a=source_maps['source_control'];b=source_maps['distance_destination_fix'];cbi='planners/CBiRRT_PCS.cpp'
    ck('transform','only D token difference across target full cpp',all(a[n]==b[n] for n in a if n!=cbi) and a[cbi].replace(b'\t\tretrieveStateVector(a->state, qa_dummy, qb);',b'\t\tretrieveStateVector(a->state, qa_dummy, qa);',1)==b[cbi])
    ck('hashes','all read bytes still unchanged',all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in retained.items()))
    report=dict(schema='P4_CBIRRT_D_BUILD01_STDLIB_SAVED_INDEPENDENT_POST_V1',status='PASS_SAVED_ENGINEERING_BUILD_AUDIT' if not failures else 'FAIL_SAVED_ENGINEERING_BUILD_AUDIT',generated_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer='nr_entry_review, independent of D engineering implementation',personnel_independent_of_D_builder_driver=True,checks_total=sum(x['total'] for x in checks.values()),checks_passed=sum(x['passed'] for x in checks.values()),checks_failed=len(failures),groups=dict(checks),failures=failures,source_commit=e['source_commit'],execution_sha256=sha(RUN/'execution.json'),audit_script_sha256=sha(__file__),own_wall_s=e['wall_s'],own_cpu_s=e['cpu_s'],prior_execution_count=len(prior),prior_own_wall_s=wall,prior_own_cpu_s=cpu,cumulative_own_wall_s=wall+e['wall_s'],cumulative_own_cpu_s=cpu+e['cpu_s'],targets=summaries,retained_sha256=retained,new_compile_binary_science_query_claim_protocol_commit_calls=0,limitations=['Saved compiler success and ELF bytes only; the three runtime interfaces were not executed in BUILD01.','No activeDistance, local RBS/reconstruction, solve, path or performance qualification is inferred.','Original failure history, all211 obligations, formal0/22500 and VI974/974 remain.'])
    with OUT.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
    with OUT.with_suffix('.md').open('x') as f:f.write(f"# D BUILD01 保存工程后审\n\n{report['status']}：{report['checks_passed']}/{report['checks_total']}，失败{len(failures)}。审查者未编写D工程builder/driver。本次新增编译、binary执行、科学查询、claim/protocol/commit均0。\n\n两个target均exit0且原source/mesh/完整日志/ELF/提交与协议链一致，只保留D单token与已声明观测I/O差异。own wall={e['wall_s']:.12f}s，CPU={e['cpu_s']:.12f}s；原60/120总帽及45/90单target帽均满足。\n\nBUILT_NOT_QUERIED只证明两target编译成功，distance/local/solve三个入口本次均未执行，不能视为算法或路径资格。原失败及211全文义务保持。\n")
    print(json.dumps({k:report[k] for k in ('status','checks_total','checks_passed','checks_failed')},ensure_ascii=False))

if __name__=='__main__':main()
