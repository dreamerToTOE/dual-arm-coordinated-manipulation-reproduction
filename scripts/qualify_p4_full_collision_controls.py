#!/usr/bin/env python3
"""Separate build/audit and explicitly invoked fixed collision controls.

Default --prepare only compiles and audits pair text. --run is scientific
qualification and must be frozen/authorized separately. No robot endpoints run.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import re
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.build_p4_full_collision_adapter import SOURCE,PQP,SPECS,DEFAULT_BUILD
CONTROL_BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_controls_v2')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump_new(p,d):
    with Path(p).open('x') as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')
def code_only(s):return re.sub(r'/\*.*?\*/|//[^\n]*','',s,flags=re.S)
def pairs(s,name):return [re.sub(r'\s+','',m) for m in re.findall(name+r'\((.*?)\);',code_only(s),re.S)]

def prepare_planar(build):
    manifest=json.loads((DEFAULT_BUILD/'manifest.json').read_text())
    entry=next(x for x in manifest['entries'] if x['model']=='I');source=Path(entry['cwd'])/'planar_collision_external.cpp'
    code=source.read_text();prefix=code[:code.index('\nint main()')]
    main='''\nint main(){PlanarNative c;State straight(20,0),cross=straight,hit=straight,away=straight;
cross[0]=0;cross[1]=acos(-1.)/2;cross[2]=-acos(-1.);hit[0]=atan2(2.,8.);away[0]=-acos(-1.)/2;
bool a=c.self_collision(cross),b=c.self_collision(straight),d=c.obstacle_collision(hit),e=c.obstacle_collision(away);
std::cout<<"{\\"self_cross_clear\\":"<<(a?"true":"false")<<",\\"self_straight_clear\\":"<<(b?"true":"false")
<<",\\"obstacle_hit_clear\\":"<<(d?"true":"false")<<",\\"obstacle_away_clear\\":"<<(e?"true":"false")<<"}"<<std::endl;
return !a&&b&&!d&&e?0:1;}\n'''
    file=build/'planar_controls_external.cpp';file.write_text(prefix+main);exe=build/'planar_controls'
    cmd=['g++','-std=c++17','-O2',str(file),'-o',str(exe)]
    proc=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
    (build/'planar_build.stdout.log').write_text(proc.stdout);(build/'planar_build.stderr.log').write_text(proc.stderr)
    return {'source_function_sha256':sha(source),'control_source_sha256':sha(file),
            'binary':str(exe),'binary_sha256':sha(exe) if exe.exists() else None,'build_command':cmd,
            'build_exit_code':proc.returncode,'query_count':0}

def prepare(build):
    build.mkdir(parents=True,exist_ok=False)
    exe=build/'pqp_engine_controls';src=ROOT/'baselines/p4_full/geometry_consistent/collision_engine_controls.cpp'
    cmd=['g++','-std=c++17','-O2','-I'+str(PQP/'include'),str(src),str(PQP/'lib/libPQP.a'),'-o',str(exe)]
    start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN)
    proc=subprocess.run(cmd,text=True,capture_output=True,timeout=120);after=resource.getrusage(resource.RUSAGE_CHILDREN)
    (build/'build.stdout.log').write_text(proc.stdout);(build/'build.stderr.log').write_text(proc.stderr)
    audit=[]
    for model,(repo,_) in SPECS.items():
        original=SOURCE/repo/'validity_checkers/collisionDetection.cpp';text=original.read_text()
        original_pairs=pairs(text,'PQP_Tolerance');variants=[]
        for variant in ['native','aligned']:
            staged=DEFAULT_BUILD/(model+'_'+variant)/'validity_checkers/collisionDetection.cpp'
            staged_pairs=pairs(staged.read_text(),'p4_query')
            variants.append({'variant':variant,'staged_source_sha256':sha(staged),
                             'all_active_source_pair_arguments_preserved':staged_pairs==original_pairs,
                             'active_call_statement_count':len(staged_pairs)})
        audit.append({'model':model,'source_sha256':sha(original),'active_pair_call_statements':original_pairs,
                      'active_call_statement_count':len(original_pairs),'variants':variants,
                      'tolerance_literals_mm':re.findall(r'PQP_REAL tolerance\s*=\s*([^;]+)',code_only(text)),
                      'policy_limit':'This reproduces the complete active source call list; commented or absent pairs are not proved clear.'})
    planar_preparation=prepare_planar(build)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    result={'schema':'P4_COLLISION_CONTROLS_ENGINEERING_PREPARATION_V1','created_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'command':cmd,'exit_code':proc.returncode,'build_wall_s':time.monotonic()-start,
            'build_cpu_s':after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
            'source_sha256':sha(src),'binary':str(exe),'binary_sha256':sha(exe) if exe.exists() else None,
            'pqp_library_sha256':sha(PQP/'lib/libPQP.a'),'source_pair_audit':audit,'collision_queries':0,
            'planar_preparation':planar_preparation,
            'qualification_status':'NOT_RUN'}
    dump_new(build/'preparation.json',result)
    print(json.dumps({'exit_code':proc.returncode,'collision_queries':0,
          'source_pair_argument_parity':all(v['all_active_source_pair_arguments_preserved'] for a in audit for v in a['variants'])}))
    if proc.returncode or planar_preparation['build_exit_code']:raise RuntimeError('CONTROL_BUILD_FAILED')

def cpu_total():
    a,b=resource.getrusage(resource.RUSAGE_SELF),resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime+a.ru_stime+b.ru_utime+b.ru_stime

def run(build,out,protocol_path):
    # Unique output, frozen protocol, aggregate budgets and failure prefixes.
    out.mkdir(parents=True,exist_ok=False);start=time.monotonic();cpu_start=cpu_total()
    execution={'schema':'P4_COLLISION_CONTROLS_EXECUTION_V1','started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
               'command':[sys.executable]+sys.argv,'protocol_path':str(protocol_path.resolve()),
               'protocol_sha256':None,'source_commit':None,
               'script_sha256':sha(__file__),'processes':[],'query_count_started_upper_bound':0,
               'query_count_completed_from_output':0,'status':'STARTED','passed':False}
    results=execution['processes'];passed=False
    wall_limit=60.;cpu_limit=120.
    def remaining():
        wall=wall_limit-(time.monotonic()-start);cpu=cpu_limit-(cpu_total()-cpu_start)
        if min(wall,cpu)<=0:raise TimeoutError('COLLISION_CONTROL_AGGREGATE_BUDGET')
        return min(wall,cpu),cpu
    def process(model,cmd,queries,metadata):
        timeout,cpu_left=remaining()
        row={'model':model,'command':cmd,'stdin':'','timeout_s':timeout,
             'query_count_submitted_upper_bound':queries,'stdout':'','stderr':'','exit_code':None,**metadata}
        results.append(row);execution['query_count_started_upper_bound']+=queries
        child_cpu_cap=max(1,int(math.ceil(cpu_left)))
        def child_limit():resource.setrlimit(resource.RLIMIT_CPU,(child_cpu_cap,child_cpu_cap))
        at=time.monotonic();before_cpu=cpu_total()
        try:
            proc=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout,
                                preexec_fn=child_limit)
            row.update(stdout=proc.stdout,stderr=proc.stderr,exit_code=proc.returncode)
            parsed=json.loads(proc.stdout);row['result']=parsed
            if model=='I':
                row['passed']=(proc.returncode==0 and parsed=={'self_cross_clear':False,'self_straight_clear':True,
                                    'obstacle_hit_clear':False,'obstacle_away_clear':True})
            else:
                row['passed']=(proc.returncode==0 and parsed.get('passed') is True and
                               parsed.get('same_query_code')==0 and parsed.get('far_query_code')==0 and
                               parsed.get('same_closer_than_tolerance')==1 and parsed.get('far_closer_than_tolerance')==0)
            execution['query_count_completed_from_output']+=queries
        except subprocess.TimeoutExpired as e:
            def decoded(x):return x.decode(errors='replace') if isinstance(x,bytes) else (x or '')
            row.update(stdout=decoded(e.stdout),stderr=decoded(e.stderr),error='TIMEOUT',passed=False)
            raise
        except Exception as e:
            row.update(error=repr(e),passed=False);raise
        finally:
            row['wall_s']=time.monotonic()-at;row['cpu_s']=cpu_total()-before_cpu
        remaining()
        if not row['passed']:raise RuntimeError('COLLISION_CONTROL_FAILED_'+model)
    try:
        execution['source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,timeout=remaining()[0]).strip()
        execution['protocol_sha256']=sha(protocol_path)
        protocol=json.loads(protocol_path.read_text());execution['protocol_sha256']=sha(protocol_path)
        if protocol.get('frozen') is not True:raise ValueError('COLLISION_CONTROLS_PROTOCOL_NOT_FROZEN')
        wall_limit=float(protocol['wall_limit_s']);cpu_limit=float(protocol['cpu_limit_s'])
        if not (0<wall_limit<=60 and 0<cpu_limit<=120):raise ValueError('COLLISION_CONTROLS_BUDGET_NOT_ALLOWED')
        execution.update(wall_limit_s=wall_limit,cpu_limit_s=cpu_limit)
        prep_path=build/'preparation.json';prep=json.loads(prep_path.read_text())
        execution['preparation_sha256']=sha(prep_path)
        if protocol.get('preparation_sha256') and protocol['preparation_sha256']!=sha(prep_path):raise ValueError('PREPARATION_HASH_CHANGED')
        manifest_path=DEFAULT_BUILD/'manifest.json';manifest=json.loads(manifest_path.read_text())
        execution['collision_adapter_manifest_sha256']=sha(manifest_path)
        if protocol.get('collision_adapter_manifest_sha256') and protocol['collision_adapter_manifest_sha256']!=sha(manifest_path):raise ValueError('ADAPTER_MANIFEST_HASH_CHANGED')
        exe=prep['binary']
        if prep['exit_code']!=0 or sha(exe)!=prep['binary_sha256']:raise ValueError('CONTROL_BINARY_HASH_CHANGED')
        for a in prep['source_pair_audit']:
            original=SOURCE/SPECS[a['model']][0]/'validity_checkers/collisionDetection.cpp'
            if sha(original)!=a['source_sha256']:raise ValueError('PAIR_SOURCE_HASH_CHANGED')
            for v in a['variants']:
                staged=DEFAULT_BUILD/(a['model']+'_'+v['variant'])/'validity_checkers/collisionDetection.cpp'
                if sha(staged)!=v['staged_source_sha256'] or not v['all_active_source_pair_arguments_preserved']:
                    raise ValueError('SOURCE_PAIR_PARITY_NOT_CONFIRMED')
        for model,repo,mesh in [('abb','CKCplanning','Base_r.tris'),('IV','ckcComau2','base_r.tris'),
                               ('V','ckcComau_industrialScene','base_r.tris'),('VI','ckcComau3','base_r.tris')]:
            path=SOURCE/repo/'simulator'/mesh
            entry=next(r for r in manifest['entries'] if r['model']==model and r['variant']=='native')
            if sha(path)!=entry['mesh_sha256'][mesh]:raise ValueError('CONTROL_MESH_HASH_CHANGED')
            process(model,[exe,str(path)],2,{'mesh_sha256':sha(path),'binary_sha256':sha(exe)})
        plan=prep['planar_preparation'];pexe=plan['binary']
        if plan['build_exit_code']!=0 or sha(pexe)!=plan['binary_sha256']:raise ValueError('PLANAR_CONTROL_BINARY_HASH_CHANGED')
        process('I',[pexe],4,{'preparation':plan,'binary_sha256':sha(pexe)})
        passed=len(results)==5 and all(r['passed'] for r in results)
        execution['status']='SOURCE_POLICY_QUALIFIED' if passed else 'CONTROL_FAILED'
    except Exception as e:
        execution.update(status='FAIL_STOP',error=repr(e));passed=False
    finally:
        execution.update(passed=passed,wall_s=time.monotonic()-start,cpu_s=cpu_total()-cpu_start,
                         ended_at_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        execution['full_geometry_qualified']=False;execution['continuous_collision_certificate']=False
        execution['limitations']=['Engine controls use real original meshes; pair parity certifies exact active source policy only.',
            'ABB source collinear rod triangles are not an independently validated solid rod collision mesh.',
            'No omitted-pair coverage, complete physical geometry, CCD, endpoints, RSS, RBS or planning qualification.']
        dump_new(out/'execution.json',execution)
        dump_new(out/'result.json',{'schema':'P4_COLLISION_ENGINE_AND_SOURCE_POLICY_CONTROL_RESULT_V1',**execution})
    print(json.dumps({'passed':passed,'status':execution['status'],'out':str(out)}))
    return 0 if passed else 1

def main():
    a=argparse.ArgumentParser();a.add_argument('--prepare',action='store_true');a.add_argument('--run',action='store_true')
    a.add_argument('--build-root',type=Path,default=CONTROL_BUILD);a.add_argument('--output',type=Path)
    a.add_argument('--protocol',type=Path);args=a.parse_args()
    if args.run:
        if args.output is None or args.protocol is None:a.error('--run requires --output and frozen --protocol')
        return run(args.build_root,args.output,args.protocol)
    else:prepare(args.build_root)
if __name__=='__main__':sys.exit(main())
