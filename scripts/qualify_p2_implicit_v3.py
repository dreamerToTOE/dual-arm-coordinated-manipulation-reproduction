#!/usr/bin/env python3
"""Fixed Gate N/D, no estimator/controller/sensors or transport trials."""
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
import scipy
from baselines.p2_pose_force import mechanics as mech,contact_geometry as geo
from baselines.p2_pose_force.native_model import NativeModel,build_native
from baselines.p2_pose_force.estimator import continuous_linearization

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(x):
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else str(x)
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [clean(v) for v in x]
    return x
def dump(p,v):Path(p).write_text(json.dumps(clean(v),ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True);args=ap.parse_args()
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=False)
    cfgpath=ROOT/'configs/p2_closed_loop_protocol_v3.json';cfg=json.loads(cfgpath.read_text())
    sources=['baselines/p2_pose_force/native_kernel.cpp','baselines/p2_pose_force/native_model.py',
      'baselines/p2_pose_force/mechanics.py','baselines/p2_pose_force/contact_geometry.py','baselines/p2_pose_force/estimator.py',
      'baselines/p2_pose_force/observations.py','scripts/qualify_p2_implicit_v3.py','reports/P2_IMPLICIT_V3_QUALIFICATION_SPEC.md']
    binary=build_native('/home/ubuntu2004/lmy/.p2_native_build_v3');native=NativeModel(binary)
    metadata={'kind':'NATIVE_EQUIVALENCE_AND_IMPLICIT_DYNAMICS_QUALIFICATION_NO_CONTROL','date':'2026-10-14','command':sys.argv,
      'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      'source_sha256':{p:sha(ROOT/p) for p in sources},'protocol_sha256':sha(cfgpath),
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
      'build':json.loads(binary.with_name('build.json').read_text()),'corrections_used':2,'remaining_corrections':1,'FD_oracle':'50-digit five-point fourth-order; unchanged epsilon1e-6 and component atol1e-7'}
    dump(out/'metadata.json',metadata);(out/'config_snapshot.json').write_bytes(cfgpath.read_bytes())
    cases=[];started=time.perf_counter();failure=None
    def record(name,passed,evidence):
        e={'name':name,'pass':bool(passed),'evidence':clean(evidence)};cases.append(e)
        with (out/'cases.jsonl').open('a') as f:f.write(json.dumps(e,allow_nan=False)+'\n')
        print(name,'PASS' if passed else 'FAIL',flush=True)
        if not passed:raise RuntimeError('QUALIFICATION_FAILED:'+name)
    try:
        rows=[json.loads(s) for s in open(ROOT/'results/20261014_P2_contact_geometry_qualification02/cases.jsonl')]
        for row in rows:
            if row['category']!='finite_differential':continue
            d=row['data'];mode=row['name'].split('.')[0];O,E,G=(np.array(d[k]) for k in ('O','E','G'))
            state=mech.State(O,np.array(d['V_o']),E,E.copy(),np.eye(4),G,G.copy());U=(np.array(d['U_EE']),np.array(d['U_EE']))
            physics=mech.physics_from_protocol(cfg);f=native.state_rate(state,U,(mode,mode),physics)
            expected=geo.grasp_rate(O,E,G,state.V,U[0],geo.selection(mode));contact=native.contact(state,U,(mode,mode),physics)
            ev={'VG_error':(f[30:36]-expected.grasp_body).tolist(),'tau_error':(contact.tau[0]-expected.tau).tolist(),'original_case_index':row['case_index']}
            record('native_geometry_'+row['name'],max(np.max(np.abs(ev[k])) for k in ('VG_error','tau_error'))<=1e-10,ev)
        fixtures={}
        for variant in ('transport','sliding'):
            state=mech.initial_state(cfg,variant);d=np.zeros(42);d[:6]=[.0002,-.0001,.0001,.03,-.02,.01]
            d[30:36]=[.0001,-.0001,.0001,-.01,.01,-.01];d[36:42]=-d[30:36];state=state.retract(d);state.V=np.array([.01,-.005,.003,.08,-.06,.04])
            physics=mech.physics_from_protocol(cfg,'C' if variant=='sliding' else 'A');fixtures[variant]=(state,physics)
            U=(np.array([.004,-.002,.001,.03,-.02,.01]),np.array([-.003,.001,-.001,-.02,.015,-.01]))
            for m1 in ('tight','pivot','sliding'):
                for m2 in ('tight','pivot','sliding'):
                    modes=(m1,m2);ref=mech.mechanics(state,U,modes,physics);got=native.contact(state,U,modes,physics)
                    errs={k:float(np.max(np.abs(getattr(ref,k)-getattr(got,k)))) for k in ('D','tau','hK','hB','h','external','internal','W')}
                    rf=mech.state_rate(state,U,modes,physics);nf=native.state_rate(state,U,modes,physics)
                    ferr=[float(np.max(np.abs(rf[6*j:6*j+6]-nf[6*j:6*j+6]))) for j in range(7)]
                    record('native_mechanics_'+variant+'_'+m1+'_'+m2,max(errs.values())<=1e-10 and max(ferr)<=1e-7,{'contact_max_abs_components':errs,'rate_block_errors':dict(zip(mech.STATE_NAMES,ferr))})
            for modes in (('tight','tight'),('pivot','pivot'),('pivot','sliding')):
                f,A=native.continuous_linearization(state,U,modes,physics);rf,ra=continuous_linearization(state,U,modes,physics)
                fd=native.finite_difference_five_point_50digits(state,U,modes,physics,1e-6)
                errors={'AD_minus_FD50':float(np.max(np.abs(A-fd))),'AD_minus_Python_analytic':float(np.max(np.abs(A-ra))),'f_minus_Python':float(np.max(np.abs(f-rf)))}
                np.savez_compressed(out/('jac_'+variant+'_'+modes[0]+'_'+modes[1]+'.npz'),AD=A,FD50=fd,Python=ra,state=np.r_[state.V],f=f)
                record('native_Jac_'+variant+'_'+modes[0]+'_'+modes[1],max(errors.values())<=1e-7,errors)
        state,physics=fixtures['transport'];U=(np.array([.004,-.002,.001,.03,-.02,.01]),np.array([-.003,.001,-.001,-.02,.015,-.01]))
        new,diag=native.advance(state,U,('pivot','pivot'),physics,1/3000)
        delta=np.array(diag['last_delta']);mid=state.retract(delta/2);f=mech.state_rate(mid,U,('pivot','pivot'),physics)
        residual=delta-1/3000*f
        record('implicit_residual_against_canonical',np.max(np.abs(residual))<=1e-12 and diag['max_newton_iterations']<=12,{'canonical_residual42':residual.tolist(),'solver':diag})
        for variant in ('transport','high_moment','sliding'):
            traces=[]
            for scale in (1,2):
                state=mech.initial_state(cfg,variant);physics=mech.physics_from_protocol(cfg,'C' if variant=='sliding' else 'A');U=(np.zeros(6),np.zeros(6));modes=('pivot','pivot');dt=1/(3000*scale)
                steps=15000*scale;period=12*scale;start=time.perf_counter();data=[];label=variant+('_fine' if scale==2 else '_coarse')
                with gzip.open(out/(label+'.jsonl.gz'),'wt') as handle:
                    for tick in range(0,steps+1,period):
                        if time.perf_counter()-start>120:raise RuntimeError('DYNAMICS_WALL_LIMIT:'+label)
                        c=native.contact(state,U,modes,physics);mech.validate_state(state,c);r=mech.equilibrium_residual(state,c,physics)
                        row={'time_s':tick*dt,'tick':tick,'state':state.as_dict(),'tau':c.tau.tolist(),'hK_N_Nm':c.hK.tolist(),'hB_N_Nm':c.hB.tolist(),'h_N_Nm':c.h.tolist(),'external_N_Nm':c.external.tolist(),'internal_N_Nm':c.internal.tolist(),'force_balance_N':r[:3].tolist(),'moment_balance_Nm':r[3:].tolist(),'solver':None if tick==0 else diag}
                        handle.write(json.dumps(row,allow_nan=False)+'\n');data.append(row)
                        if tick<steps:state,diag=native.advance(state,U,modes,physics,dt,period)
                valid=np.max(np.abs(r[:3]))<=1e-6 and np.max(np.abs(r[3:]))<=1e-6 and np.max(np.abs(state.V[:3]))<=1e-7 and np.max(np.abs(state.V[3:]))<=1e-7
                record('five_seconds_'+label,valid,{'wall_s':time.perf_counter()-start,'terminal_force_N':r[:3].tolist(),'terminal_moment_Nm':r[3:].tolist(),'terminal_linear_speed_m_s':state.V[:3].tolist(),'terminal_angular_speed_rad_s':state.V[3:].tolist(),'duration_s':5})
                traces.append(data)
            maxima=np.zeros(6)
            for a,b in zip(*traces):
                A=np.array(a['state']['O']);B=np.array(b['state']['O']);raw=np.array(a['h_N_Nm'])-np.array(b['h_N_Nm']);hi=np.array(a['internal_N_Nm'])-np.array(b['internal_N_Nm'])
                maxima=np.maximum(maxima,[np.linalg.norm(A[:3,3]-B[:3,3]),np.linalg.norm(geo.se3_log(geo.inverse(A)@B)[3:]),np.max(np.abs(raw[:,:3])),np.max(np.abs(raw[:,3:])),np.max(np.abs(hi[:,:3])),np.max(np.abs(hi[:,3:]))])
            record('step_refinement_'+variant,np.all(maxima<=np.array([5e-5,5e-4,.05,.002,.05,.002])),dict(zip(['position_m','angle_rad','raw_force_N','raw_moment_Nm','internal_force_N','internal_moment_Nm'],maxima.tolist())))
    except Exception as exc:
        failure=str(exc);dump(out/'termination.json',{'reason':failure,'traceback':traceback.format_exc(),'native_evidence':getattr(exc,'evidence',None),'last_state':state.as_dict() if 'state' in locals() else None,'last_label':locals().get('label'),'last_tick':locals().get('tick'),'no_reset':True});print('STOP',failure,flush=True)
    summary={'status':'PASS' if failure is None else 'FAIL_STOP','completed_checks':len(cases),'passed_checks':sum(e['pass'] for e in cases),'wall_s':time.perf_counter()-started,'closed_loop_runs':0,'dynamics_qualified':failure is None,'estimator_controller_qualified':False,'reason':failure}
    dump(out/'summary.json',summary);dump(out/'artifact_sha256.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()})
    print(json.dumps(summary),flush=True);return 0 if failure is None else 2
if __name__=='__main__':sys.exit(main())
