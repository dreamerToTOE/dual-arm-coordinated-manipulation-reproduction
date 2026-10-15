"""Auditable external native and physical-base-aligned collision policies.

Import ``check_collision(environment, q)`` or send JSONL {environment,q} to
``python -m baselines.p4_full.geometry_consistent.collision_adapter``. Building
is explicit and separate; importing this module does not launch any process.
``collision`` is bool only after a real source-policy query and TCP consistency
check. It certifies the original discrete source policy, never continuous CCD.
"""
from __future__ import annotations
import atexit
import hashlib
import json
import math
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time

DEFAULT_MANIFEST=Path('/home/ubuntu2004/lmy/.p4_d079_dependency_audit/collision_adapter_v2/manifest.json')
_sessions={}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class NativeSession:
    def __init__(self,entry,env):
        self.entry=entry;self.env=env
        if sha(entry['binary'])!=entry['binary_sha256']:raise ValueError('BINARY_HASH_CHANGED')
        for relative,expected in entry['source_files_sha256'].items():
            if sha(Path(entry['source_root'])/relative)!=expected:raise ValueError('SOURCE_HASH_CHANGED '+relative)
        for name,expected in entry['mesh_sha256'].items():
            if sha(Path(entry['cwd'])/'simulator'/name)!=expected:raise ValueError('MESH_HASH_CHANGED '+name)
        self.command=[entry['binary'],env]
        self.proc=subprocess.Popen(self.command,cwd=entry['cwd'],stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0)
        self.pending=b''
        self.selector=selectors.DefaultSelector();self.selector.register(self.proc.stdout,selectors.EVENT_READ)
    def query(self,q,timeout_s):
        start=time.monotonic();raw=[]
        self.proc.stdin.write((' '.join(format(float(x),'.17g') for x in q)+'\n').encode());self.proc.stdin.flush()
        while True:
            if b'\n' not in self.pending:
                remaining=timeout_s-(time.monotonic()-start)
                if remaining<=0 or not self.selector.select(remaining):
                    self.close();raise TimeoutError('COLLISION_PROCESS_TIMEOUT')
                chunk=os.read(self.proc.stdout.fileno(),65536)
                if not chunk:raise RuntimeError('COLLISION_PROCESS_EXIT '+str(self.proc.poll())+' '+''.join(raw))
                self.pending+=chunk;continue
            line,self.pending=self.pending.split(b'\n',1)
            text=line.decode(errors='replace');raw.append(text+'\n')
            if text.startswith('P4_COLLISION_RESULT '):
                row=json.loads(text.split(' ',1)[1]);row.update(source_stdout=''.join(raw),
                     source_stderr='merged into source_stdout',source_command=self.command,
                     wall_s=time.monotonic()-start)
                return row
    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try:self.proc.wait(timeout=.5)
            except subprocess.TimeoutExpired:self.proc.terminate();self.proc.wait(timeout=2)
        self.selector.close()

def close_sessions():
    for session in list(_sessions.values()):
        try:session.close()
        except Exception:pass
    _sessions.clear()
atexit.register(close_sessions)

def _evaluate_pose(env,q,row):
    if env=='I':return {'status':'SOURCE_PLANAR_GEOMETRY','passed':True,'errors':[]}
    import numpy as np
    from baselines.p4_full.geometry_consistent.physical_nr import arm_fk_jac
    poses=row.get('poses',[]);arms=len(q)//6
    if len(poses)!=arms:return {'status':'POSE_CAPTURE_MISSING','passed':False}
    errors=[]
    for i,values in enumerate(poses):
        actual=np.asarray(values,dtype=float).reshape(3,4)
        expected=arm_fk_jac(q[i*6:i*6+6],env,i+1)[0][:3,:]
        errors.append({'arm':i+1,'translation_maxabs_mm':float(np.max(np.abs(actual[:,3]-expected[:,3]))),
                       'rotation_maxabs':float(np.max(np.abs(actual[:,:3]-expected[:,:3]))),
                       'collision_TCP':actual.tolist(),'independent_TCP':expected.tolist()})
    passed=all(e['translation_maxabs_mm']<=1e-5 and e['rotation_maxabs']<=1e-5 for e in errors)
    return {'status':'PASS' if passed else 'COLLISION_PHYSICAL_TCP_MISMATCH','passed':passed,
            'position_gate_mm':1e-5,'rotation_matrix_gate':1e-5,'errors':errors}

def check_collision(environment,q,*,timeout_s=30.,manifest_path=None):
    """Never raises for a source/runtime failure; returns collision=None + reason.

    Native and aligned results are both retained. The aligned policy changes no
    mesh, pair, tolerance, link frame, grasp or source obstacle coordinate.
    Caller owns execution budget; no retries or alternative input is attempted.
    """
    answer={'environment':environment,'collision':None,'status':'UNKNOWN','scope':'AUTHOR_DISCRETE_COLLISION_POLICY',
            'continuous_collision_certificate':False,'variants':{},'source_command':None}
    try:
        env=str(environment);q=[float(x) for x in q];count={'I':20,'II':12,'III':12,'IV':12,'V':12,'VI':18}[env]
        if len(q)!=count or not all(math.isfinite(x) for x in q):raise ValueError('INVALID_CONFIGURATION')
        # No new principal-angle gate: source legally allows many 2pi lifts.
        path=Path(manifest_path or os.environ.get('P4_COLLISION_MANIFEST',str(DEFAULT_MANIFEST)))
        manifest=json.loads(path.read_text());answer['manifest_sha256']=sha(path)
        answer['manifest_path']=str(path);model='abb' if env in ('II','III') else env
        for variant in (['native'] if env in ('I','VI') else ['native','aligned']):
            entry=next(r for r in manifest['entries'] if r['model']==model and r['variant']==variant)
            if entry['exit_code']!=0:raise ValueError('COLLISION_BUILD_NOT_SUCCESSFUL')
            key=(str(path),env,variant)
            if key not in _sessions:_sessions[key]=NativeSession(entry,env)
            row=_sessions[key].query(q,timeout_s)
            row['provenance']={k:entry[k] for k in ['source_root','source_commit','source_files_sha256',
                            'mesh_sha256','binary_sha256','physical_alignment_changes']}
            row['pose_consistency']=_evaluate_pose(env,q,row)
            row['native_collision']=None if row.get('native_result') not in (0,1) else bool(row['native_result'])
            row['query_error_codes']=[x for x in row.get('query_codes',[]) if x!=0]
            answer['variants'][variant]=row
        preferred=answer['variants'].get('aligned',answer['variants']['native'])
        answer['source_command']=preferred['source_command'];answer['selected_variant']='aligned' if 'aligned' in answer['variants'] else 'native'
        if preferred['native_collision'] is None or preferred['query_error_codes']:
            answer['status']='SOURCE_COLLISION_QUERY_ERROR'
        elif not preferred['pose_consistency']['passed']:
            answer['status']='COLLISION_PHYSICAL_TCP_MISMATCH'
        else:
            answer['collision']=preferred['native_collision'];answer['status']='CHECKED'
        answer['source_stdout']=preferred['source_stdout'];answer['source_stderr']=preferred['source_stderr']
        answer['limitations']=(['Source planar obstacles use sampled vertices and nonparallel segment intersection; original f retained.'] if env=='I' else
             ['Original mesh pair list and 8mm PQP tolerance retained; no omitted pair inferred clear.',
              'TCP consistency is checked per query; source CAD mesh frame policy is retained.'])
        if env in ('II','III'):
            answer['limitations'].append('Source setP supplies collinear rod triangle vertices; preserved as source policy, not a rod surface or CCD certificate.')
    except Exception as e:
        answer['status']='COLLISION_ADAPTER_ERROR';answer['error']=repr(e)
    return answer

def main():
    for line in sys.stdin:
        if not line.strip():continue
        try:
            request=json.loads(line);answer=check_collision(request['environment'],request['q'],
                    timeout_s=float(request.get('timeout_s',30.)))
        except Exception as e:answer={'collision':None,'status':'INVALID_REQUEST','error':repr(e)}
        print(json.dumps(answer,ensure_ascii=False,allow_nan=False),flush=True)
if __name__=='__main__':main()
