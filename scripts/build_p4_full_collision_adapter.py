#!/usr/bin/env python3
"""Compile external author policies with additive recording; executes no query.

No upstream source or mesh is copied into the public repository. The two
variants preserve every mesh/pair/tolerance; aligned changes only the explicitly
identified world base coordinate expressions and ABB approximate-pi base yaw.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/home/ubuntu2004/lmy/.p4_d079_author_asset_audit')
PQP=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/compat02/PQP_v1.3')
DEFAULT_BUILD=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v2')
SPECS={'abb':('CKCplanning',0),'IV':('ckcComau2',4),
       'V':('ckcComau_industrialScene',5),'VI':('ckcComau3',6)}
PINNED={'CKCplanning':'909bd72fff778aca8682c96f9eb86ae4eb75557b',
        'ckcComau2':'80089340f0f1f6822e5b2821a63c998b6ae0413f',
        'ckcComau_industrialScene':'ef6e9c4df34d2ca1605b34c86f6fe9a689c757ca',
        'ckcComau3':'25488a86947cd07377cc62c43850df719a70d9ee',
        'planar_ckc':'e5edcb58e151b78baca43dd4922bfe27a48388cd'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replace_once(s,a,b):
    if s.count(a)!=1:raise ValueError('SOURCE_PATTERN_CARDINALITY '+a)
    return s.replace(a,b,1)

def stage(build,model,variant):
    repo,macro=SPECS[model];src=SOURCE/repo;dest=build/(model+'_'+variant)
    dest.mkdir(parents=True,exist_ok=False)
    for folder in ['validity_checkers','proj_classes','simulator']:(dest/folder).mkdir()
    originals={}
    for rel in ['validity_checkers/collisionDetection.cpp','validity_checkers/collisionDetection.h',
                'validity_checkers/model.h','simulator/MatVec.h']:
        originals[rel]=sha(src/rel);shutil.copy2(src/rel,dest/rel)
    if (src/'proj_classes/def.h').exists():
        rel='proj_classes/def.h';originals[rel]=sha(src/rel);shutil.copy2(src/rel,dest/rel)
    header=dest/'validity_checkers/collisionDetection.h';h=header.read_text()
    h=h.replace('#include <GL/glut.h>','// unused rendering header omitted for standalone build')
    h=re.sub(r'#include "[^"]*/MatVec.h"','#include "../simulator/MatVec.h"',h)
    header.write_text(h)
    file=dest/'validity_checkers/collisionDetection.cpp';s=file.read_text();patches=[]
    if variant=='aligned' and model=='abb':
        s=replace_once(s,'MRotZ(M02,3.14159265/2+offsetRot);','MRotZ(M02,3.1416/2);')
        # Applied after upstream's second base calculation, before its links.
        mark='\n\tT12[0] =  0;'
        s=replace_once(s,mark,'\n\tT02[0]=offsetX/2; T02[1]=0; T02[2]=0;'+mark)
        patches=['arm2 base yaw uses same source 3.1416 as qualified APC',
                 'arm2 base translation uses qualified world [d/2,0,0]']
    if variant=='aligned' and model in ('IV','V'):
        mark='\n\tT12[0] =  0;'
        y='offsetY' if model=='V' else '0'
        s=replace_once(s,mark,f'\n\tT02[0]=offsetX/2; T02[1]={y}; T02[2]=ROBOT2_HEIGHT;'+mark)
        patches=['arm2 world base translation uses source APC global coordinates; no mesh local frame changed']
    # Preserve all arguments and tolerance of every original actual PQP call.
    s=s.replace('PQP_Tolerance(&res[','p4_query(&res[')
    marker='\tPQP_REAL tolerance = 8;'
    extra='400.7' if model=='V' else '0'
    calls=f'\tp4_pose(R6,T7,{extra}); p4_pose(R62,T72,{extra});\n'
    if model=='VI':calls+='\tp4_pose(R63,T73);\n'
    s=replace_once(s,marker,calls+marker);file.write_text(s)
    meshes={}
    for p in sorted((src/'simulator').glob('*.tris')):
        (dest/'simulator'/p.name).symlink_to(p);meshes[p.name]=sha(p)
    exe=dest/'collision_batch'
    cmd=['g++','-std=c++17','-O2','-Wall','-Wextra',f'-DP4_MODEL={macro}',
         '-I'+str(dest/'validity_checkers'),'-I'+str(PQP/'include'),
         str(ROOT/'baselines/p4_full/geometry_consistent/collision_batch_driver.cpp'),
         str(PQP/'lib/libPQP.a'),'-o',str(exe)]
    start=time.monotonic()
    proc=subprocess.run(cmd,text=True,capture_output=True,timeout=120)
    (dest/'build.stdout.log').write_text(proc.stdout);(dest/'build.stderr.log').write_text(proc.stderr)
    result={'model':model,'variant':variant,'source_root':str(src),
            'source_commit':PINNED[repo],
            'source_files_sha256':originals,'mesh_sha256':meshes,'command':cmd,'exit_code':proc.returncode,
            'build_wall_s':time.monotonic()-start,'binary':str(exe),'cwd':str(dest),
            'binary_sha256':sha(exe) if exe.exists() else None,'physical_alignment_changes':patches,
            'instrumented_source_sha256':sha(file),'query_count':0}
    return result

def function_body(source,name):
    start=source.index('bool pcs::StateValidityChecker::'+name+'(')
    at=source.index('{',start);depth=1;end=at+1
    while depth:
        if source[end]=='{':depth+=1
        elif source[end]=='}':depth-=1
        end+=1
    return source[start:end].replace('pcs::StateValidityChecker::','PlanarNative::')

def planar(build):
    src=SOURCE/'planar_ckc';dest=build/'I_native';dest.mkdir()
    p=src/'validity_checkers/StateValidityCheckerPCS.cpp';h=src/'validity_checkers/StateValidityCheckerPCS.h'
    source=p.read_text();header=h.read_text()
    obstacles=re.search(r'^\s*Matrix obs = (\{.*\});',header,re.M).group(1)
    pre='''#include <cmath>\n#include <iostream>\n#include <sstream>\n#include <vector>\nusing State=std::vector<double>;using Matrix=std::vector<State>;
class PlanarNative{public:int n=20;double getL(){return 1.;} Matrix obs=OBSTACLES;
bool self_collision(State,double=1);bool obstacle_collision(State,double=.3);};\n'''.replace('OBSTACLES',obstacles)
    code=pre+'\n'+function_body(source,'self_collision')+'\n'+function_body(source,'obstacle_collision')
    code+='''\nint main(){PlanarNative c;std::string l;while(std::getline(std::cin,l)){std::istringstream s(l);State q;double x;while(s>>x)q.push_back(x);if(q.size()!=20)return 65;bool a=c.self_collision(q),b=c.obstacle_collision(q);std::cout<<"P4_COLLISION_RESULT {\\"native_result\\":"<<(!(a&&b))<<",\\"self_clear\\":"<<(a?"true":"false")<<",\\"obstacle_clear\\":"<<(b?"true":"false")<<",\\"poses\\":[],\\"query_codes\\":[]}"<<std::endl;}}\n'''
    file=dest/'planar_collision_external.cpp';file.write_text(code);exe=dest/'collision_batch'
    cmd=['g++','-std=c++17','-O2',str(file),'-o',str(exe)];start=time.monotonic()
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    (dest/'build.stdout.log').write_text(proc.stdout);(dest/'build.stderr.log').write_text(proc.stderr)
    return {'model':'I','variant':'native','source_root':str(src),
            'source_files_sha256':{str(p.relative_to(src)):sha(p),str(h.relative_to(src)):sha(h)},
            'source_commit':PINNED['planar_ckc'],
            'mesh_sha256':{},'command':cmd,'exit_code':proc.returncode,'binary':str(exe),'cwd':str(dest),
            'binary_sha256':sha(exe) if exe.exists() else None,'build_wall_s':time.monotonic()-start,
            'query_count':0,'physical_alignment_changes':[],
            'policy_scope':'Exact source point-obstacle and expanded nonadjacent segment intersection; no continuous or thickness guarantee'}

def main():
    a=argparse.ArgumentParser();a.add_argument('--build-root',type=Path,default=DEFAULT_BUILD);args=a.parse_args()
    args.build_root.mkdir(parents=True,exist_ok=False)
    manifest={'schema':'P4_COLLISION_ADAPTER_ENGINEERING_BUILD_V1','created_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
              'query_count':0,'license':'External author files/meshes only; no redistribution',
              'pqp_library_sha256':sha(PQP/'lib/libPQP.a'),'entries':[]}
    try:
        for model in SPECS:
            for variant in ['native','aligned']:
                r=stage(args.build_root,model,variant);manifest['entries'].append(r)
                print(json.dumps({k:r[k] for k in ['model','variant','exit_code','build_wall_s']}),flush=True)
                if r['exit_code']:raise RuntimeError('BUILD_FAILED')
        manifest['entries'].append(planar(args.build_root))
    finally:
        (args.build_root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
