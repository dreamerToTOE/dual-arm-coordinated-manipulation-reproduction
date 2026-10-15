#!/usr/bin/env python3
"""DRAFT thin ABB PCS build: four external targets; zero executable queries.

--describe-protocol only reads files. --protocol requires a committed frozen
recipe. Author files/meshes stay outside the repository. No default make/main.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from baselines.p4_full.geometry_consistent.spatial_ik_patch import stage_spatial_ik
import qualify_p4_full_r2_vi_rss_reconstructed as common

AUTHOR=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit/CKCplanning')
BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/abb_pcs_qualification_v1')
PQP=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3')
PRE='reports/P4_FULL_R2_ORDINARY_PCS_NR_INTEGRATION_PRE_DRAFT_20261015.md'
TRACE='baselines/p4_full/geometry_consistent/pcs_source_trace.hpp'
DRIVER='baselines/p4_full/geometry_consistent/abb_pcs_qualification_driver.cpp'
OWN=[str(Path(__file__).relative_to(ROOT)),TRACE,DRIVER,
     'baselines/p4_full/geometry_consistent/spatial_ik_patch.py',
     'scripts/qualify_p4_full_r2_vi_rss_reconstructed.py',PRE]
ID='P4_R2_ABB_PCS_BUILD_4_180W_360CPU_20261015'
RUN='20261015_R2_ABB_PCS_BUILD01'

def prior_ledgers():
    return sorted(p for p in (ROOT/'results/p4_full').glob('20261015_R2_*/execution.json')
                  if p.parent.name!=RUN)

def draft_protocol():
    prior=prior_ledgers();rows=[json.loads(p.read_text()) for p in prior]
    return {'schema':'P4_R2_ABB_PCS_ENGINEERING_RECIPE_V1','frozen':False,
        'claim_id':ID,'build_root':str(BUILD),'author_root':str(AUTHOR),
        'author_commit':'909bd72fff778aca8682c96f9eb86ae4eb75557b',
        'own_source_sha256':{p:common.sha(ROOT/p) for p in OWN},
        'author_manifest_sha256':common.sha(ROOT/'configs/p4_full/author_source_manifest.json'),
        'PQP_library_sha256':common.sha(PQP/'lib/libPQP.a'),
        'targets':[[v,t] for v in ('author_native','geometry_consistent') for t in ('plain','trace')],
        'budget':{'wall_s':180.,'cpu_s':360.,'single_wall_s':45.,'single_cpu_s':90.},
        'prior_execution_sha256':{str(p.relative_to(ROOT)):common.sha(p) for p in prior},
        'previous_r2_wall_s':sum(float(r['wall_s']) for r in rows),
        'previous_r2_cpu_s':sum(float(r['cpu_s']) for r in rows),
        'r2_total_wall_s':3600.,'r2_total_cpu_s':7200.,
        'source_policy':'Original SVCPCS and RRT/CBiRRT/SBL bodies; fixed overload only. No random sampler, tolerance, collision/model/limits/control-flow repair.',
        'query_calls':0,'solve_calls':0,'scientific_execution_authorized':False}

def body_span(source,signature):
    if source.count(signature)!=1:raise ValueError('SIGNATURE_CARDINALITY '+signature)
    # Mask strings/comments without changing character offsets before counting braces.
    mask=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
        lambda m:' '*len(m.group()),source,flags=re.S)
    start=mask.index('{',source.index(signature));depth=1;at=start+1
    while depth:
        depth+=(mask[at]=='{')-(mask[at]=='}');at+=1
    return start,at-1

def wrap(source,signature,kind,args,result,void=False):
    a,b=body_span(source,signature);body=source[a+1:b]
    lead='\n auto p4_id=p4pcs::enter("'+kind+'",'+args+');\n'
    if void:
        middle=' [&]() -> void {'+body+'}();\n'
        tail=' p4pcs::leave(p4_id,"'+kind+'",'+result+');\n'
    else:
        middle=' auto p4_return=[&]() {'+body+'}();\n'
        tail=' p4pcs::leave(p4_id,"'+kind+'",'+result+');\n return p4_return;\n'
    changed=source[:a+1]+lead+middle+tail+source[b:]
    # The original body is retained literally once inside its observation wrapper.
    if changed[a+1+len(lead)+middle.index('{')+1:][:len(body)]!=body:
        raise ValueError('INSTRUMENTATION_BODY_PARITY_FAILED')
    return changed

def instrument(stage):
    edits=[]
    p=stage/'proj_classes/apc_class.cpp';s=p.read_text();before=common.sha(p)
    s=wrap(s,'void two_robots::FKsolve_rob(State q, int robot_num)', 'native_fk',
        '{{"q6",q},{"arm",robot_num}}','p4pcs::json::object()',True)
    s=wrap(s,'bool two_robots::IKsolve_rob(Matrix T, int robot_num, int solution_num)',
        'native_ik','{{"T",T},{"arm",robot_num},{"branch",solution_num}}',
        '{{"returned",p4_return}}')
    p.write_text(s);edits.append({'path':str(p.relative_to(stage)),'before':before,'after':common.sha(p)})
    p=stage/'validity_checkers/StateValidityCheckerPCS.cpp';s=p.read_text();before=common.sha(p)
    s=wrap(s,'bool StateValidityChecker::IKproject(State &q1, State &q2, int active_chain, int ik_sol)',
        'project_fixed','{{"q1",q1},{"q2",q2},{"active_chain",active_chain},{"branch",ik_sol}}',
        '{{"returned",p4_return},{"q1",q1},{"q2",q2}}')
    for sig,kind,depth in [
        ('bool StateValidityChecker::checkMotionRBS(State qa1, State qa2, State qb1, State qb2, int active_chain, int ik_sol, int recursion_depth, int non_decrease_count)','rbs','recursion_depth'),
        ('bool StateValidityChecker::reconstructRBS(State qa1, State qa2, State qb1, State qb2, int active_chain, int ik_sol, Matrix &M, int iteration, int last_index, int firstORsecond)','reconstruct','iteration')]:
        s=wrap(s,sig,kind,'{{"qa1",qa1},{"qa2",qa2},{"qb1",qb1},{"qb2",qb2},{"active_chain",active_chain},{"branch",ik_sol},{"depth",'+depth+'}}',
            '{{"returned",p4_return}}')
    p.write_text(s);edits.append({'path':str(p.relative_to(stage)),'before':before,'after':common.sha(p)})
    p=stage/'validity_checkers/collisionDetection.cpp';s=p.read_text();before=common.sha(p)
    s=s.replace('PQP_Tolerance(&res[','p4pcs::query(&res[')
    s=wrap(s,'int collisionDetection::collision_state(Matrix M, State q1, State q2)',
        'collision','{{"q1",q1},{"q2",q2}}','{{"returned",p4_return}}')
    p.write_text(s);edits.append({'path':str(p.relative_to(stage)),'before':before,'after':common.sha(p)})
    return edits

def adapt_header(stage):
    p=stage/'validity_checkers/collisionDetection.h';s=p.read_text()
    if s.count('#include <GL/glut.h>')!=1:raise ValueError('UNUSED_GLUT_ANCHOR')
    s=s.replace('#include <GL/glut.h>','// unused rendering include omitted in nonvisual target')
    s,n=re.subn(r'#include "[^"\n]*/MatVec.h"','#include "../simulator/MatVec.h"',s)
    if n!=1:raise ValueError('MATVEC_PATH_ANCHOR')
    p.write_text(s)

def verify_frozen(spec,path):
    expected=draft_protocol()
    if {**spec,'frozen':False}!=expected or spec.get('frozen') is not True:
        raise ValueError('FROZEN_EXACT_BUILD_RECIPE_REQUIRED')
    for p in [*OWN,str(path.relative_to(ROOT))]:
        subprocess.run(['git','ls-files','--error-unmatch',p],cwd=ROOT,check=True,
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if subprocess.check_output(['git','status','--porcelain','--',p],cwd=ROOT,text=True):
            raise ValueError('UNCOMMITTED_BUILD_SOURCE '+p)

def build(spec,protocol):
    verify_frozen(spec,protocol)
    source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    for name,expected in spec['own_source_sha256'].items():
        blob=subprocess.check_output(['git','show',source_commit+':'+name],cwd=ROOT)
        if hashlib.sha256(blob).hexdigest()!=expected:
            raise ValueError('BUILD_SOURCE_COMMIT_BLOB_MISMATCH '+name)
    if BUILD.exists():raise FileExistsError('BUILD_ROOT_EXISTS_NO_OVERWRITE')
    ledger=ROOT/'results/p4_full'/RUN
    if ledger.exists():raise FileExistsError('ENGINEERING_LEDGER_EXISTS_NO_OVERWRITE')
    if min(spec['budget']['wall_s'],spec['budget']['cpu_s'],
            spec['r2_total_wall_s']-spec['previous_r2_wall_s'],
            spec['r2_total_cpu_s']-spec['previous_r2_cpu_s'])<=0:
        raise ValueError('ENGINEERING_BUDGET_EXHAUSTED_BEFORE_CLAIM')
    claim=ROOT/'results/p4_full'/(ID+'.claim.json')
    common.new_json(claim,
        {'schema':'P4_R2_ABB_PCS_ENGINEERING_CLAIM_V1','claim_id':ID,
         'protocol':str(protocol),'protocol_sha256':common.sha(protocol),'budget':spec['budget'],
         'source_commit':source_commit,'own_source_sha256':spec['own_source_sha256'],
         'author_commit':spec['author_commit'],'query_calls':0,'solve_calls':0,
         'retain_failed_stage':True,'created_at_utc':common.utc()})
    BUILD.mkdir();ledger.mkdir();start=time.monotonic();cpu_start=common.RunBudget.cpu();entries=[]
    budget=None;target_start=None;target_cpu_start=None
    manifest={'schema':'P4_R2_ABB_PCS_ENGINEERING_BUILD_V1','protocol':str(protocol),
        'protocol_sha256':common.sha(protocol),'query_calls':0,'solve_calls':0,'entries':entries,
        'classification':'SOURCE_NATIVE_VS_VERSIONED_R2_NUMERICS / OBSERVATION_EQUIVALENCE_PENDING',
        'source_commit':source_commit,'own_source_sha256':spec['own_source_sha256'],
        'author_commit':spec['author_commit'],'claim':str(claim.relative_to(ROOT)),
        'claim_sha256':common.sha(claim),'engineering_execution':str((ledger/'execution.json').relative_to(ROOT))}
    status='STOP_RETAINED_PREFIX'
    try:
        budget=common.RunBudget({'budget':{**spec['budget'],'r2_total_wall_s':spec['r2_total_wall_s'],
            'r2_total_cpu_s':spec['r2_total_cpu_s']}},spec['previous_r2_wall_s'],spec['previous_r2_cpu_s'])
        staged=stage_spatial_ik('abb',AUTHOR,BUILD/'geometry_template')
        manifest['spatial_stage']=staged
        for variant,mode in spec['targets']:
            target_start=time.monotonic();target_cpu_start=common.RunBudget.cpu()
            signal.setitimer(signal.ITIMER_REAL,min(spec['budget']['single_wall_s'],
                budget.wall_cap-(target_start-budget.started)))
            dest=BUILD/(variant+'_'+mode)
            binary=dest/'p4_abb_pcs_thin'
            row={'variant':variant,'mode':mode,'stage_root':str(dest),'binary':str(binary),
                'status':'PREPARING_TARGET','started_at_utc':common.utc()}
            entries.append(row)
            source=AUTHOR if variant=='author_native' else BUILD/'geometry_template'
            shutil.copytree(source,dest,ignore=shutil.ignore_patterns('.git'))
            adapt_header(dest);edits=instrument(dest) if mode=='trace' else []
            files=[dest/'proj_classes/apc_class.cpp',dest/'validity_checkers/StateValidityCheckerPCS.cpp',
                dest/'validity_checkers/collisionDetection.cpp',*[dest/'planners'/n for n in
                ('RRT_PCS.cpp','CBiRRT_PCS.cpp','SBL_PCS.cpp')]]
            cmd=['g++','-std=c++17','-O2','-Wall','-Wextra','-pthread',
                '-I/opt/ros/humble/include/ompl-1.7','-I/usr/include/eigen3',
                '-I'+str(PQP/'include'),'-I'+str(dest/'proj_classes'),
                '-I'+str(dest/'validity_checkers'),'-I'+str(ROOT/TRACE).rsplit('/',1)[0],
                '-include',str(ROOT/TRACE),str(ROOT/DRIVER),*[str(p) for p in files],
                str(PQP/'lib/libPQP.a'),'-L/opt/ros/humble/lib/x86_64-linux-gnu',
                '-Wl,-rpath,/opt/ros/humble/lib/x86_64-linux-gnu','-lompl',
                '-lboost_filesystem','-lboost_system','-lboost_serialization',
                '-lboost_program_options','-o',str(binary)]
            wallcap=min(spec['budget']['wall_s'],spec['r2_total_wall_s']-spec['previous_r2_wall_s'])
            cpucap=min(spec['budget']['cpu_s'],spec['r2_total_cpu_s']-spec['previous_r2_cpu_s'])
            headers=sorted(p for p in dest.rglob('*') if p.is_file() and p.suffix in ('.h','.hpp'))
            row.update(command=cmd,instrumentation=edits,
                source_sha256={str(p.relative_to(dest)):common.sha(p) for p in [*files,*headers]},
                mesh_sha256={str(p.relative_to(dest)):common.sha(p) for p in sorted((dest/'simulator').glob('*.tris'))},
                status='COMPILING_TARGET')
            if min(spec['budget']['single_wall_s']-(time.monotonic()-target_start),
                    spec['budget']['single_cpu_s']-(common.RunBudget.cpu()-target_cpu_start),
                    budget.remaining())<=0:raise TimeoutError('BUILD_TARGET_PREPARATION_CAP')
            with (dest/'compile.stdout').open('x') as out,(dest/'compile.stderr').open('x') as err:
                def child_limits():resource.setrlimit(resource.RLIMIT_CPU,(int(spec['budget']['single_cpu_s']),int(spec['budget']['single_cpu_s'])))
                proc=subprocess.Popen(cmd,stdout=out,stderr=err,preexec_fn=child_limits,start_new_session=True)
                try:
                    while proc.poll() is None:
                        # Include live compiler descendants, not only reaped CPU.
                        live=0.
                        for stat in Path('/proc').glob('[0-9]*/stat'):
                            try:
                                fields=stat.read_text().rsplit(')',1)[1].split()
                                if int(fields[2])==proc.pid:
                                    # Root RUSAGE_CHILDREN excludes this still-live
                                    # group. Include a member's already-reaped
                                    # descendants here, without counting live
                                    # descendants twice.
                                    live+=sum(int(fields[i]) for i in (11,12,13,14))/os.sysconf('SC_CLK_TCK')
                            except (OSError,ValueError,IndexError):pass
                        if (time.monotonic()-target_start>=spec['budget']['single_wall_s']
                                or time.monotonic()-start>=wallcap
                                or common.RunBudget.cpu()-target_cpu_start+live>=spec['budget']['single_cpu_s']
                                or common.RunBudget.cpu()-cpu_start+live>=cpucap):
                            raise TimeoutError('BUILD_WALL_OR_LIVE_AGGREGATE_CPU_CAP')
                        try:proc.wait(timeout=.02)
                        except subprocess.TimeoutExpired:pass
                except BaseException:
                    if proc.poll() is None:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                    row.update(exit_code=proc.returncode,wall_s=time.monotonic()-target_start,
                        cpu_s=common.RunBudget.cpu()-target_cpu_start,status='STOP_RETAINED_PREFIX')
                    raise
            row.update(exit_code=proc.returncode,wall_s=time.monotonic()-target_start,
                cpu_s=common.RunBudget.cpu()-target_cpu_start,
                status='TARGET_BUILT_NOT_EXECUTED' if proc.returncode==0 else 'BUILD_FAILED_PREFIX_RETAINED',
                binary_sha256=common.sha(binary) if binary.exists() else None)
            if proc.returncode:raise RuntimeError('BUILD_FAILED '+variant+' '+mode)
            signal.setitimer(signal.ITIMER_REAL,max(1e-9,budget.wall_cap-(time.monotonic()-budget.started)))
        status='BUILT_NOT_EXECUTED_OR_QUALIFIED'
    except BaseException as exc:
        manifest['termination_reason']=repr(exc)
        if entries and 'wall_s' not in entries[-1]:
            entries[-1].update(status='STOP_RETAINED_PREFIX',wall_s=time.monotonic()-target_start,
                cpu_s=common.RunBudget.cpu()-target_cpu_start)
        raise
    finally:
        if budget is not None:budget.close()
        manifest.update(status=status,engineering_build_wall_s=time.monotonic()-start,
            engineering_build_cpu_s=common.RunBudget.cpu()-cpu_start)
        common.new_json(BUILD/'manifest.json',manifest)
        common.new_json(ledger/'execution.json',{'schema':'P4_R2_ABB_PCS_ENGINEERING_EXECUTION_V1',
            'status':status,'classification':'ENGINEERING_BUILD_ONLY','source_commit':source_commit,
            'own_source_sha256':spec['own_source_sha256'],'author_commit':spec['author_commit'],
            'claim':str(claim.relative_to(ROOT)),'claim_sha256':common.sha(claim),
            'wall_s':manifest['engineering_build_wall_s'],'cpu_s':manifest['engineering_build_cpu_s'],
            'external_manifest':str(BUILD/'manifest.json'),'manifest_sha256':common.sha(BUILD/'manifest.json'),
            'query_calls':0,'solve_calls':0,'protocol':str(protocol),'protocol_sha256':common.sha(protocol),
            'prior_execution_sha256':spec['prior_execution_sha256'],
            'previous_wall_s':spec['previous_r2_wall_s'],'previous_cpu_s':spec['previous_r2_cpu_s']})
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--describe-protocol',action='store_true');g.add_argument('--protocol',type=Path)
    a=p.parse_args()
    if a.describe_protocol:print(json.dumps(draft_protocol(),ensure_ascii=False,indent=2));return
    build(json.loads(a.protocol.read_text()),a.protocol.resolve())
if __name__=='__main__':main()
