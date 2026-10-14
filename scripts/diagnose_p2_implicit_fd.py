#!/usr/bin/env python3
"""One fixed mathematical diagnostic; no qualification promotion/control runs."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from baselines.p2_pose_force import mechanics as mech
from baselines.p2_pose_force.native_model import NativeModel,build_native
from baselines.p2_pose_force.estimator import continuous_linearization

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=ROOT/'results/20261014_P2_implicit_FD_diagnosis01';out.mkdir(exist_ok=False)
 cfgpath=ROOT/'configs/p2_closed_loop_protocol_v2.json';cfg=json.loads(cfgpath.read_text());old=ROOT/'results/20261014_P2_implicit_qualification01/jac_transport_tight_tight.npz'
 metadata={'kind':'FIXED_THREE_POINT_MATH_DIAGNOSTIC_NO_INTEGRATION_OR_CONTROL','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':{p:sha(ROOT/p) for p in ('scripts/diagnose_p2_implicit_fd.py','reports/P2_IMPLICIT_FD_DIAGNOSIS_SPEC.md','baselines/p2_pose_force/native_kernel.cpp','baselines/p2_pose_force/estimator.py')},'input_jacobian_sha256':sha(old),'protocol_sha256':sha(cfgpath),'qualification_promoted':False,'correction_count':1,'closed_loop_runs':0}
 (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n');start=time.perf_counter()
 state=mech.initial_state(cfg,'transport');d=np.zeros(42);d[:6]=[.0002,-.0001,.0001,.03,-.02,.01];d[30:36]=[.0001,-.0001,.0001,-.01,.01,-.01];d[36:42]=-d[30:36];state=state.retract(d);state.V=np.array([.01,-.005,.003,.08,-.06,.04]);physics=mech.physics_from_protocol(cfg)
 U=(np.array([.004,-.002,.001,.03,-.02,.01]),np.array([-.003,.001,-.001,-.02,.015,-.01]));modes=('tight','tight');native=NativeModel(build_native('/home/ubuntu2004/lmy/.p2_native_build'))
 f,A=native.continuous_linearization(state,U,modes,physics);rf,ra=continuous_linearization(state,U,modes,physics)
 original=np.load(old);assert np.array_equal(A,original['AD']);assert np.array_equal(ra,original['Python'])
 rows=[]
 for epsilon in (1e-6,2e-6,5e-7):
  fd=native.finite_difference_50digits(state,U,modes,physics,epsilon);e=A-fd;ind=np.unravel_index(np.abs(e).argmax(),e.shape)
  np.savez_compressed(out/('matrices_eps_'+format(epsilon,'.1e')+'.npz'),AD=A,FD50=fd,Python=ra)
  rows.append({'epsilon':epsilon,'max_absolute_error':float(np.abs(e).max()),'max_index':list(ind),'AD_row9_col27':float(A[9,27]),'FD_row9_col27':float(fd[9,27]),'error_row9_col27':float(e[9,27]),'qualifying_epsilon':epsilon==1e-6})
 ratios={'double_epsilon_error_ratio':rows[1]['error_row9_col27']/rows[0]['error_row9_col27'],'half_epsilon_error_ratio':rows[2]['error_row9_col27']/rows[0]['error_row9_col27']}
 summary={'status':'DIAGNOSTIC_ONLY_ORIGINAL_FAIL_STOP_RETAINED','rows':rows,'ratios':ratios,'AD_minus_independent_Python_max':float(np.abs(A-ra).max()),'wall_s':time.perf_counter()-start,'no_state_integration':True,'no_parameter_or_threshold_change':True,'no_qualification_rerun':True}
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'fixture.json').write_text(json.dumps({'state':state.as_dict(),'U':np.array(U).tolist(),'modes':modes},indent=2)+'\n')
 (out/'artifact_sha256.json').write_text(json.dumps({p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()},indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
