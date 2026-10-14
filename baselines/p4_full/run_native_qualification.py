"""Bounded real author-kernel builds/runs; no planning or reset of source endpoints."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(cmd, cwd, limit, output):
    start = time.monotonic()
    try:
        with output.open('wb') as f:
            p = subprocess.run(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT,
                               timeout=limit, env={**os.environ, 'OPENBLAS_NUM_THREADS': '1',
                                                  'OMP_NUM_THREADS': '1'})
        status, code = ('COMPLETED' if p.returncode == 0 else 'FAILED'), p.returncode
    except subprocess.TimeoutExpired:
        status, code = 'TIMEOUT', None
    return {'command': [str(x) for x in cmd], 'cwd': str(cwd), 'limit_s': limit,
            'status': status, 'exit_code': code, 'wall_s': time.monotonic()-start,
            'stdout_stderr': str(output.relative_to(ROOT)), 'log_sha256': sha(output)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-root', type=Path, required=True)
    ap.add_argument('--run-id', required=True)
    ap.add_argument('--targets', nargs='+', choices=['ABB', 'I', 'IV', 'V', 'VI'], required=True)
    args=ap.parse_args()
    source=args.source_root.resolve()
    out=ROOT/'results/p4_full'/args.run_id
    # Atomic unique directory; no overwriting earlier experimental data.
    out.mkdir(parents=True, exist_ok=False)
    build=ROOT/'build/p4_full'/args.run_id
    build.mkdir(parents=True, exist_ok=False)
    protocol_path=ROOT/'configs/p4_full/r1_qualification_v1.json'
    protocol=json.loads(protocol_path.read_text())
    source_manifest_path=ROOT/'configs/p4_full/author_source_manifest.json'
    manifest=json.loads(source_manifest_path.read_text())
    started=time.monotonic()
    record={'schema':'P4_D079_NATIVE_QUALIFICATION_RUN_V1','run_id':args.run_id,
            'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'git_status_at_start':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),
            'protocol_sha256':sha(protocol_path),'source_manifest_sha256':sha(source_manifest_path),
            'platform':platform.platform(),'formal_planning_calls':0,'stages':[],
            'copyright':'Only own test drivers/logs published. Author source and meshes external.'}
    def save():
        record['wall_s']=time.monotonic()-started
        (out/'execution.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    spec={'ABB':('CKCplanning','abb_native_qualification.cpp',[]),
          'I':('planar_ckc','planar_native_qualification.cpp',[]),
          'IV':('ckcComau2','comau_native_qualification.cpp',['-DP4_COMAU_MODEL=4']),
          'V':('ckcComau_industrialScene','comau_native_qualification.cpp',['-DP4_COMAU_MODEL=5']),
          'VI':('ckcComau3','comau_native_qualification.cpp',['-DP4_COMAU_MODEL=6'])}
    try:
        for target in args.targets:
            dirname,driver,defines=spec[target]
            src=source/dirname
            repo_name='ckcComau' if target=='V' else dirname
            candidates=[r for r in manifest['repositories'] if r['repository']==repo_name]
            if target=='V':candidates=[r for r in candidates if r['branch']=='industrialScene']
            if len(candidates)!=1:raise RuntimeError(f'Non-unique source manifest for {target}')
            repo=candidates[0]; hashes={x['path']:x['sha256'] for x in repo['files']}
            files=[src/'proj_classes/apc_class.cpp',src/'proj_classes/apc_class.h',
                   src/'proj_classes/kdl_class.cpp',src/'proj_classes/kdl_class.h']
            for f in files:
                if sha(f)!=hashes[str(f.relative_to(src))]:raise RuntimeError(f'Source bytes changed {f}')
            executable=build/target
            own=ROOT/'baselines/p4_full'/driver
            cmd=['g++','-std=c++17','-O2','-Wall','-Wextra','-I'+str(src/'proj_classes'),
                 '-I/usr/include/eigen3',*defines,str(own),str(files[0]),str(files[2]),
                 '-lorocos-kdl','-o',str(executable)]
            remaining=protocol['total_wall_limit_s']-(time.monotonic()-started)
            if remaining<=0:raise TimeoutError('Total qualification limit exhausted')
            stage={'target':target,'author_commit':repo['commit'],'driver_sha256':sha(own),
                   'author_source_hashes':{str(f.relative_to(src)):sha(f) for f in files}}
            record['stages'].append(stage);save()
            stage['build']=run(cmd,ROOT,min(protocol['build_single_limit_s'],remaining),out/(target+'_build.log'))
            save()
            if stage['build']['status']!='COMPLETED':continue
            stage['binary_sha256']=sha(executable)
            envs=['II','III'] if target=='ABB' else [target]
            stage['diagnostics']=[]
            for env in envs:
                remaining=protocol['total_wall_limit_s']-(time.monotonic()-started)
                if remaining<=0:raise TimeoutError('Total qualification limit exhausted')
                data=out/(env+'_native.json')
                if target in ['IV','V','VI']:
                    data=out/(env+'_native.jsonl')
                    invocation=[str(executable),str(data),str(protocol['seed'])]
                else:
                    invocation=[str(executable),env,str(data)]
                diagnostic=run(invocation,ROOT,
                               min(protocol['diagnostic_single_limit_s'],remaining),out/(env+'_native.log'))
                if data.exists():diagnostic.update(native_data=str(data.relative_to(ROOT)),native_sha256=sha(data))
                stage['diagnostics'].append(diagnostic);save()
        record['status']='COMPONENT_DIAGNOSTICS_RECORDED'
    except Exception as e:
        record['status']='STOP';record['error']=repr(e)
        raise
    finally:
        record['ended_at_utc']=dt.datetime.now(dt.timezone.utc).isoformat();save()
    print(json.dumps({'run_id':args.run_id,'status':record['status'],'wall_s':record['wall_s']}))

if __name__=='__main__':main()
