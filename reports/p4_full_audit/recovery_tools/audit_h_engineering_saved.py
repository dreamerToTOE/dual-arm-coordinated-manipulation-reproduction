#!/usr/bin/env python3
"""Compact saved-only H engineering POST; never compile or execute binaries."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'results/p4_full/20261015_R2_ABB_RANDOM_HELPER_H_BUILD01'
OUT=ROOT/'reports/P4_FULL_R2_ABB_RANDOM_HELPER_H_BUILD_SAVED_POST_20261016'
CHECKS=[]


def path(p):
    p=Path(p);return p if p.is_absolute() else ROOT/p


def load(p):return json.loads(path(p).read_text())
def sha(p):return hashlib.sha256(path(p).read_bytes()).hexdigest()
def fingerprint(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def check(n,ok,**evidence):
    CHECKS.append(dict(check=n,passed=bool(ok),**evidence))


def same(n,a,b):
    check(n,a==b,actual_sha256=fingerprint(a),expected_sha256=fingerprint(b))


def audit():
    e=load(RUN/'execution.json');p=load(e['protocol']);c=load(e['claim']);m=load(e['external_manifest'])
    same('exact_source_commit',e['source_commit'],'cdf53f0183ac7fd2129415875f7b88ab486414ac')
    same('status',e['status'],'BUILT_NOT_QUERIED')
    same('classification',e['classification'],'ENGINEERING_BUILD_ONLY')
    same('protocol_frozen',p['frozen'],True)
    check('both_explicit_reviews',set(p['reviews'])=={'independent_static_review_passed','root_freeze_approved'} and all(v is True for v in p['reviews'].values()))
    same('protocol_hash',sha(e['protocol']),e['protocol_sha256'])
    same('claim_hash',sha(e['claim']),e['claim_sha256'])
    same('external_manifest_hash',sha(e['external_manifest']),e['manifest_sha256'])
    same('manifest_saved_exact',sha(RUN/'manifest.saved.json'),e['manifest_sha256'])
    same('manifest_execution_fields',{k:v for k,v in e.items()if k not in ('external_manifest','manifest_sha256')},{k:v for k,v in m.items()if k!='engineering_execution'})
    same('manifest_execution_reference',m['engineering_execution'],str((RUN/'execution.json').relative_to(ROOT)))
    same('claim_source',c['source_commit'],e['source_commit'])
    same('claim_protocol_hash',c['protocol_sha256'],e['protocol_sha256'])
    same('claim_one_shot',c['no_retry_reset_or_resume'],True)
    same('protocol_own_sources',p['own_source_sha256'],e['own_source_sha256'])
    same('claim_own_sources',c['own_source_sha256'],e['own_source_sha256'])
    for n,want in e['own_source_sha256'].items():
        same('own_current_hash.'+n,sha(n),want)
        blob=subprocess.check_output(['git','show',e['source_commit']+':'+n],cwd=ROOT)
        same('own_frozen_commit_blob.'+n,hashlib.sha256(blob).hexdigest(),want)
    frozen_name=str(path(e['protocol']).relative_to(ROOT))
    blob=subprocess.check_output(['git','show',e['source_commit']+':'+frozen_name],cwd=ROOT)
    same('frozen_protocol_commit_blob',hashlib.sha256(blob).hexdigest(),e['protocol_sha256'])
    same('zero_query',e['query_calls'],0);same('zero_solve',e['solve_calls'],0)
    same('zero_formal_table_I',e['formal_table_I_calls'],0);same('zero_VI_candidates',e['new_VI_candidate_constructions'],0)
    same('exact_2_targets',[v['factor']for v in e['entries']],['source_control','success_break'])
    same('frozen_2_targets',[v['factor']for v in p['targets']],['source_control','success_break'])
    same('old_asset_before_after',e['template_assets_sha256'],e['template_assets_after_sha256'])
    same('old_assets_frozen',e['template_assets_sha256'],p['template_assets_sha256'])
    for n,want in e['template_assets_sha256'].items():same('template_current_hash.'+n,sha(n),want)
    same('prior_frozen',e['prior_execution_sha256'],p['prior_execution_sha256'])
    same('prior_exact25',len(e['prior_execution_sha256']),25)
    prior_rows=[]
    for n,want in e['prior_execution_sha256'].items():
        same('prior_current_hash.'+n,sha(n),want);prior_rows.append(load(n))
    same('prior_wall_own_cost_sum',e['previous_r2_wall_s'],math.fsum(v['wall_s']for v in prior_rows))
    same('prior_cpu_own_cost_sum',e['previous_r2_cpu_s'],math.fsum(v['cpu_s']for v in prior_rows))
    same('fixed_budget',p['budget'],{'wall_s':60.,'cpu_s':120.,'single_wall_s':45.,'single_cpu_s':90.,'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.})
    check('aggregate_cost_within_caps',0<e['wall_s']<60 and 0<e['cpu_s']<120)
    check('total_r2_within_caps',e['previous_r2_wall_s']+e['wall_s']<3600 and e['previous_r2_cpu_s']+e['cpu_s']<7200)
    check('no_final_budget_stop','final_budget_exceeded'not in e)
    check('aggregate_covers_own_target_costs',e['wall_s']>=sum(v['wall_s']for v in e['entries']) and e['cpu_s']>=sum(v['cpu_s']for v in e['entries']))
    sys.path.insert(0,str(ROOT))
    from baselines.p4_full.geometry_consistent.abb_helper_instrumentation_draft import instrument_sources,APC,SVC,COL
    original={n:(Path(p['template_stage'])/n).read_bytes()for n in (APC,SVC,COL)}
    summaries=[]
    for entry,target in zip(e['entries'],p['targets']):
        factor=entry['factor'];stage=Path(entry['stage']);binary=Path(entry['binary'])
        same(factor+'.stage',str(stage),target['stage']);same(factor+'.binary',str(binary),target['binary'])
        same(factor+'.status',entry['status'],'BUILT_NOT_QUERIED');same(factor+'.compile_exit',entry['exit_code'],0)
        same(factor+'.binary_hash',sha(binary),entry['binary_sha256'])
        check(factor+'.ELF_not_executed',binary.read_bytes()[:4]==b'\x7fELF')
        for field in ('compiled_source_sha256','mesh_sha256'):
            for n,want in entry[field].items():same(factor+'.'+field+'.'+n,sha(stage/n),want)
        transformed,preview=instrument_sources(original,factor)
        same(factor+'.whole_source_byte_transform_preview',preview,p['source_transform_previews'][factor])
        same(factor+'.actual_manifest_preview',preview,e['source_transform_previews'][factor])
        for n,bytes_ in transformed.items():
            same(factor+'.actual_staged_full_bytes.'+n,hashlib.sha256((stage/n).read_bytes()).hexdigest(),hashlib.sha256(bytes_).hexdigest())
        check(factor+'.original_external_bytes_preserved',all((Path(p['template_stage'])/n).read_bytes()==b for n,b in original.items()))
        check(factor+'.target_caps',0<entry['wall_s']<45 and 0<entry['cpu_s']<90)
        command=entry['command'];same(factor+'.absolute_compiler',command[0],'/usr/bin/x86_64-linux-gnu-g++-11')
        same(factor+'.only_3_author_CPP',[n for n in command if n.endswith('.cpp') and str(stage) in n],[str(stage/n)for n in (APC,SVC,COL)])
        check(factor+'.no_fast_math','-ffast-math'not in command and '-O2'in command and '-std=c++17'in command)
        logs={}
        for channel in ('stdout','stderr'):
            external=stage/('compile.'+channel);saved=RUN/factor/('compile.'+channel)
            same(factor+'.full_compile_'+channel+'_copy',sha(external),sha(saved))
            logs[channel]=dict(bytes=external.stat().st_size,sha256=sha(external))
        warnings=Counter(re.findall(r'\[(-W[^\]]+)\]',(stage/'compile.stderr').read_text()))
        summaries.append(dict(factor=factor,exit_code=entry['exit_code'],wall_s=entry['wall_s'],cpu_s=entry['cpu_s'],binary_sha256=entry['binary_sha256'],logs=logs,warning_categories=dict(warnings)))
    return dict(source_commit=e['source_commit'],wall_s=e['wall_s'],cpu_s=e['cpu_s'],prior_count=25,
        previous_r2_wall_s=e['previous_r2_wall_s'],previous_r2_cpu_s=e['previous_r2_cpu_s'],
        new_r2_wall_s=math.fsum([e['previous_r2_wall_s'],e['wall_s']]),new_r2_cpu_s=math.fsum([e['previous_r2_cpu_s'],e['cpu_s']]),
        targets=summaries,execution_sha256=sha(RUN/'execution.json'),manifest_sha256=e['manifest_sha256'],
        protocol_sha256=e['protocol_sha256'],claim_sha256=e['claim_sha256'])


if __name__=='__main__':
    if OUT.with_suffix('.json').exists()or OUT.with_suffix('.md').exists():raise FileExistsError('Preserve existing POST')
    summary=audit();failed=[c for c in CHECKS if not c['passed']]
    report=dict(schema='P4_H_TWO_TARGET_ENGINEERING_SAVED_POST_V1',created_at_utc=datetime.now(timezone.utc).isoformat(),
        status='PASS_ENGINEERING_BUILT_NOT_QUERIED'if not failed else'FAIL_ENGINEERING_SAVED_POST',
        checks_total=len(CHECKS),checks_passed=len(CHECKS)-len(failed),checks_failed=len(failed),
        new_compile_calls=0,new_scientific_calls=0,new_helper_dispatches=0,
        scope='Saved build evidence only; git show reads metadata and pure byte transforms never evaluate a model.',
        script_sha256=sha(__file__),summary=summary,failed_checks=failed,checks=CHECKS)
    with OUT.with_suffix('.json').open('x')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    with OUT.with_suffix('.md').open('x')as f:
        f.write(f'''# ABB PCS helper H 两目标工程保存证据POST

**{report['status']}**，{report['checks_passed']}/{report['checks_total']}检查通过，{report['checks_failed']}失败。仅核对已保存工程结果，新增编译、科学调用及helper派发均为0。

唯一工程源提交cdf53f0，source_control和success_break两个目标均exit0且状态BUILT_NOT_QUERIED。复核冻结protocol/claim/manifest与提交源码、binary SHA、完整原始编译stdout/stderr及精确副本、原三文件整字节变换与可逆证明、旧资产和25笔prior哈希；原始编译警告全保留，不重编。

| 目标 | 墙钟秒 | CPU秒 | exit |
|---|---:|---:|---:|
''')
        for t in summary['targets']:f.write(f"| {t['factor']} | {t['wall_s']:.17g} | {t['cpu_s']:.17g} | {t['exit_code']} |\n")
        f.write(f'''
工程实际own-cost：墙钟{summary['wall_s']:.17g}秒、CPU{summary['cpu_s']:.17g}秒，两个单目标与合计均在冻结45/90与60/120帽内。原25笔累计{summary['previous_r2_wall_s']:.17g}/{summary['previous_r2_cpu_s']:.17g}，本项只入账一次后为26笔{summary['new_r2_wall_s']:.17g}/{summary['new_r2_cpu_s']:.17g}。

这仅确认构建交付，未调用两个binary、未运行64点科学资格，不能认定helper正确、规划能力或论文实验通过。正式Table I仍0/22500，VI仍974/974。
''')
    print(json.dumps({k:report[k]for k in ('status','checks_total','checks_passed','checks_failed')},ensure_ascii=False))
