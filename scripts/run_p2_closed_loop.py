#!/usr/bin/env python3
"""Frozen P2 causal multi-rate trials; true plant and estimator/control are separate."""
import argparse,gzip,hashlib,json,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from scipy.spatial.transform import Rotation
from baselines.p2_pose_force import mechanics as mech,contact_geometry as geo
from baselines.p2_pose_force.native_model import NativeModel,build_native
from baselines.p2_pose_force.observations import ObservationGenerator,calibrate_paired_visuals,declared_grasps,initialize_from_fresh,FilterState
from baselines.p2_pose_force.estimator import RightIESEKF
from baselines.p2_pose_force.control import PoseForceController,QuinticReference,SlidingReference
from baselines.p2_pose_force.clocking import EndpointClock

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clean(x):
 if isinstance(x,np.ndarray):return clean(x.tolist())
 if isinstance(x,np.integer):return int(x)
 if isinstance(x,np.bool_):return bool(x)
 if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else str(x)
 if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [clean(v) for v in x]
 return x
def write(p,x):Path(p).write_text(json.dumps(clean(x),ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def log(handle,x):handle.write(json.dumps(clean(x),ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n')
def cases(cfg):
 out=[]
 for c in ('exp1','exp2','exp3','exp4'):
  for seed in cfg['suite']['main_seeds']:out.append({'id':len(out)+1,'condition':c,'seed':seed,'variant':'transport','GT':False,'scale':1})
 for variant in ('high_moment','delay'):
  for c in ('exp1','exp3'):out.append({'id':len(out)+1,'condition':c,'seed':7,'variant':variant,'GT':False,'scale':1})
 out.append({'id':25,'condition':'exp3','seed':7,'variant':'sliding','GT':False,'scale':1})
 for c in ('exp1','exp2','exp3','exp4'):out.append({'id':len(out)+1,'condition':c,'seed':7,'variant':'transport','GT':True,'scale':1})
 out.append({'id':30,'condition':'exp3','seed':7,'variant':'transport','GT':False,'scale':2})
 assert len(out)==30;return out

def require_contact(state,contact):
 mech.validate_state(state,contact)
 s=contact.singular_values
 if len(s)!=6 or s[-1]<=1e-12*s[0]:raise RuntimeError('TRANSPORT_CONTACT_RANK_INVALID')
 residual=contact.W@(contact.H@contact.internal.ravel())
 if np.any(np.abs(residual)>1e-9):raise RuntimeError('INTERNAL_PROJECTION_RESIDUAL_INVALID')

def solver_log(e):return {k:v for k,v in e.items() if k!='last_accepted_state'}

def run_case(cfg,case,out,native,suite_started,prior_wall):
 out.mkdir(exist_ok=False);start=time.perf_counter();physics=mech.physics_from_protocol(cfg,'C' if case['variant']=='sliding' else 'A');variant=case['variant'];scale=case['scale'];dt=1/(3000*scale)
 state=mech.initial_state(cfg,variant if variant in ('sliding','high_moment') else 'transport');modes=('pivot','pivot');Uzero=np.zeros((2,6));filt=None;tick=None;ref=None;control=None;failure=None;trace_rows=[];max_Newton=0;phase='precalibration';est_updates=0;est_predictions=0;primary_GT_reads=0
 cfgpath=ROOT/'configs/p2_closed_loop_protocol_v3.json';sources=['scripts/run_p2_closed_loop.py','baselines/p2_pose_force/clocking.py','baselines/p2_pose_force/native_kernel.cpp','baselines/p2_pose_force/native_model.py','baselines/p2_pose_force/estimator.py','baselines/p2_pose_force/observations.py','baselines/p2_pose_force/control.py','baselines/p2_pose_force/mechanics.py','baselines/p2_pose_force/contact_geometry.py','reports/P2_CLOSED_LOOP_RUNTIME_SPEC.md']
 write(out/'metadata.json',{'kind':'FROZEN_P2_INDEPENDENT_PLANT_ESTIMATED_CONTROL' if not case['GT'] else 'FROZEN_P2_EXPLICIT_GT_STATE_CONTROL_DIAGNOSTIC','date':'2026-10-14','case':case,'seed':case['seed'],'task':'P2_STAGE2_ORIGINAL_CONTROLLER','baseline':'original Eq9-12/16/19-21/25, approved spatial-free Log geometry','platform':'independent rigid COM ODE, ideal Cartesian endpoints; not robot joint control','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':{p:sha(ROOT/p) for p in sources},'command':sys.argv,'config_path':str(cfgpath.relative_to(ROOT)),'protocol_sha256':sha(cfgpath),'build':json.loads(native.binary.with_name('build.json').read_text()),'true_K':[k.tolist() for k in physics.K],'wall_limit_s':120,'suite_wall_limit_s':7200,'corrections_used':3,'remaining_corrections':0,'observer_mean_integration':'original Eq18 right Euler at fresh observation/heartbeat events; no internal substeps','causal_phase_clocks':'global_case_s=precalibration time;settle5+t;transport10+t','covariance_log':'diag each event, full at1Hz/failure; complete covariance propagation/checking every prediction/update','no_gt_primary_controller':not case['GT']});(out/'config_snapshot.json').write_bytes(cfgpath.read_bytes())
 sensor=ObservationGenerator(cfg,case['seed'],variant=variant,tick_scale=scale,contact_provider=native.contact)
 clock=EndpointClock(cfg,scale,delayed=variant=='delay');target=np.eye(4);target[:3,3]=[.15,.08,.35];target[:3,:3]=Rotation.from_rotvec([0,0,np.pi/2]).as_matrix()
 handles={name:gzip.open(out/(name+'.jsonl.gz'),'wt',compresslevel=1) for name in ('plant','sensors','estimator','commands','settling')};events=(out/'events.jsonl').open('w')
 def budget():
  if time.perf_counter()-start>120:raise RuntimeError('CASE_WALL_LIMIT')
  if time.perf_counter()-suite_started+prior_wall>7200:raise RuntimeError('SUITE_WALL_LIMIT')
 def plant_row(t,c,phase,solver=None,reference=None):
  row={'phase':phase,'time_s':t,'global_case_time_s':5+t if phase=='settle' else 10+t,'tick':tick,'state':state.as_dict(),'D':c.D,'tau':c.tau,'hK_N_Nm':c.hK,'hB_N_Nm':c.hB,'h_N_Nm':c.h,'internal_N_Nm':c.internal,'external_N_Nm':c.external,'W':c.W,'W_singular_values':c.singular_values,'solver':solver}
  if reference is not None:
   error=geo.se3_log(geo.inverse(state.O)@reference.pose);estimated_error=geo.se3_log(geo.inverse(state.O)@filt.state.O);goal=geo.se3_log(geo.inverse(state.O)@target)
   row.update(reference={'pose':reference.pose,'desired_body_twist':reference.body_twist,'segment':reference.segment},GT_tracking_Log_rho_m_theta_rad=error,estimated_minus_true_Log_rho_m_theta_rad=estimated_error,estimated_minus_true_V_linear_m_s_angular_rad_s=filt.state.V-state.V,GT_goal_distance_m=float(np.linalg.norm(state.O[:3,3]-target[:3,3])),GT_goal_angle_rad=float(np.linalg.norm(goal[3:])),GT_waypoint_position_error_m=float(np.linalg.norm(state.O[:3,3]-reference.pose[:3,3])),estimated_state=filt.state.as_dict(),old_applied_input_NA_body_m_s_rad_s=clock.applied.copy())
  return row
 try:
  pairs=sensor.precalibration_pairs(state)
  for a,b in pairs:
   budget()
   for obs in (a,b):log(handles['sensors'],{'phase':'precalibration','global_case_time_s':obs.delivery_stamp,'observation':obs.as_dict()})
  calibration=calibrate_paired_visuals(pairs,cfg);write(out/'calibration.json',{'C_estimated':calibration.C,'iterations':calibration.iterations,'max_mean_component':calibration.maximum_mean_component,'pair_count':75,'sample_ids':calibration.sample_ids,'input':'only paired simulated visual observations; trueC not substituted'})
  log(events,{'type':'calibration_complete_before_settle','global_case_time_s':5,'available_before_transport':True});phase='settle';diag=None
  for tick in range(0,15000*scale+1,12*scale):
   budget();c=native.contact(state,Uzero,modes,physics);require_contact(state,c);log(handles['settling'],plant_row(tick*dt,c,'settle',None if diag is None else solver_log(diag)))
   if tick<15000*scale:state,diag=native.advance(state,Uzero,modes,physics,dt,12*scale);max_Newton=max(max_Newton,diag['max_newton_iterations'])
  balance=mech.equilibrium_residual(state,c,physics)
  if np.max(np.abs(balance[:3]))>1e-6 or np.max(np.abs(balance[3:]))>1e-6 or np.max(np.abs(state.V[:3]))>1e-7 or np.max(np.abs(state.V[3:]))>1e-7:raise RuntimeError('FIXED_FIVE_SECOND_SETTLE_INVALID')
  log(events,{'type':'true_integrated_settle_pass','global_case_time_s':10,'balance_N_Nm':balance,'V_m_s_rad_s':state.V});phase='transport';tick=0;packet=sensor.sample_packet(state,0,c,modes=modes);init=initialize_from_fresh(packet,calibration,*declared_grasps(cfg,variant),time_s=0.)
  filt=RightIESEKF.from_protocol(init.state,cfg,condition=case['condition'],object_id='C' if variant=='sliding' else 'A',modes=modes,rate_provider=native.continuous_linearization)
  filt.seen_samples.update((o.kind,o.sample_id) for o in init.consumed_observations)
  for n in mech.STATE_NAMES:
   if np.shares_memory(getattr(state,n),getattr(filt.state,n)):raise RuntimeError('PLANT_ESTIMATE_ARRAY_ALIAS')
  assert filt.state.origin=='observations'
  write(out/'initialization.json',{'source':'fresh noisy EE1/EE2/visual1, zeroV, declaredG, observedC','estimate':filt.state.as_dict(),'consumed_samples':[(o.kind,o.sample_id) for o in packet],'P0':filt.P,'no_true_state_input':True})
  controller=PoseForceController.from_protocol(cfg,case['condition'],object_id='C' if variant=='sliding' else 'A',variant=variant,contact_provider=native.contact)
  reference=SlidingReference(cfg) if variant=='sliding' else QuinticReference(cfg);end_tick=(30 if variant=='sliding' else 95)*3000*scale
  event_ticks=[s*3000*scale for s in ((5,25,30) if variant=='sliding' else (3,7,13,23,55,76,95))]
  while True:
   budget();t=tick*dt;old_published=clock.published.copy();contact=native.contact(state,clock.applied,modes,physics);require_contact(state,contact);old_modes=modes;switched=False
   if variant=='sliding' and tick in (5*3000*scale,25*3000*scale):
    newmode='sliding' if tick==5*3000*scale else 'pivot';guard=geo.mode_switch_guard(contact.D[1],modes[1],newmode,contact.h[1])
    log(events,{'type':'mode_switch_guard','tick':tick,'time_s':t,'old':modes[1],'new':newmode,'guard':guard,'true_raw_h':contact.h[1],'true_tau':contact.tau[1]})
    if not guard['eligible']:raise RuntimeError('MODE_SWITCH_PRELOAD_INVALID')
    modes=(modes[0],newmode);switched=True;contact=native.contact(state,clock.applied,modes,physics);require_contact(state,contact)
   packet=packet if tick==0 else sensor.sample_packet(state,tick,contact,modes=modes)
   for obs in packet:log(handles['sensors'],{'phase':'transport','global_case_time_s':10+obs.delivery_stamp,'observation':obs.as_dict(),'used_for':'initialization_only' if tick==0 else 'fresh_filter_packet'})
   heartbeat=tick%(12*scale)==0
   if heartbeat or packet:
    predict=filt.predict_to(t,old_published);est_predictions+=predict is not None
    if switched:filt.modes=modes
    update=filt.update(packet) if tick>0 and packet else None;est_updates+=update is not None
    row={'tick':tick,'time_s':t,'global_case_time_s':10+t,'state':filt.state.as_dict(),'P_diagonal':np.diag(filt.P),'P_full_at_1Hz':filt.P if tick%(3000*scale)==0 else None,'old_published_model_input':old_published,'prediction_interval_s':None if predict is None else predict.end_stamp-predict.start_stamp,'observations_consumed':[] if update is None else update.sample_keys,'iterations':None if update is None else update.iterations,'converged':None if update is None else update.converged,'consecutive_nonconverged':filt.consecutive_nonconverged,'iteration_increments':None if update is None else update.iteration_increments,'innovation_before':None if update is None else update.innovation_before,'innovation_after':None if update is None else update.innovation_after,'stop_requested':filt.stopped}
    log(handles['estimator'],row)
    if update is not None and update.stop_requested:raise RuntimeError(update.stop_reason)
    modeled=native.contact(filt.state,old_published,modes,controller.physics)
    if np.any(np.abs(modeled.tau[:,:3])>.005) or np.any(np.abs(modeled.tau[:,3:])>.15):raise RuntimeError('ESTIMATOR_MODEL_PAD_DOMAIN_INVALID')
   if heartbeat:
    estimate=FilterState.from_mechanics(state) if case['GT'] else filt.state
    primary_GT_reads+=bool(case['GT']);ref=reference.sample(t,estimate.O);control=controller.evaluate(estimate,old_published,ref,modes,t,diagnostic_GT=case['GT']);clock.receive(tick,control.U_cmd)
    row=plant_row(t,contact,'transport',None if diag is None else solver_log(diag),ref);log(handles['plant'],row);trace_rows.append(clean(row))
    commandrow=control.as_dict();commandrow.update(tick=tick,source='explicit_GT_state_diagnostic' if case['GT'] else 'observation_initialized_IESEKF',estimated_model_K=[k.tolist() for k in controller.physics.K],old_actual_applied=clock.applied.copy());log(handles['commands'],commandrow)
   for event in clock.publish_and_deliver(tick,modes):event.update(time_s=t,global_case_time_s=10+t);log(events,event)
   if tick==end_tick:break
   nexttick=clock.next_tick(tick,end_tick,event_ticks);state,diag=native.advance(state,clock.applied,modes,physics,dt,nexttick-tick);max_Newton=max(max_Newton,diag['max_newton_iterations']);tick=nexttick
 except Exception as exc:
  failure=str(exc);write(out/'termination.json',{'reason':failure,'traceback':traceback.format_exc(),'phase':phase,'tick':tick,'time_s':None if tick is None else tick*dt,'last_accepted_plant_state':state.as_dict(),'last_estimate_state':None if filt is None else filt.state.as_dict(),'last_published_U':clock.published,'last_actual_U':clock.applied,'last_control':None if control is None else control.as_dict(),'native_evidence':getattr(exc,'evidence',None),'no_reset_or_reanchoring':True})
  if filt is not None:
   matrices={'P':filt.P}
   if filt.last_prediction is not None:matrices.update(F=filt.last_prediction.transition,Qd=filt.last_prediction.process_covariance)
   if filt.last_update_matrices is not None:matrices.update(zip(('Pprior','Hwhitened','Kwhitened','reset','Panchor'),filt.last_update_matrices))
   np.savez_compressed(out/'failure_filter_matrices.npz',**matrices)
 finally:
  for handle in handles.values():handle.close()
  events.close()
 metrics={'GT_final_position_RMS_m':None,'GT_final_angle_RMS_rad':None,'true_internal_stack_force_RMS_N':None,'true_internal_each_moment_RMS_Nm':None}
 if failure is None and variant!='sliding':
  final=[r for r in trace_rows if 85<=r['time_s']<=95];transport=[r for r in trace_rows if 13<=r['time_s']<=76];h=np.array([r['internal_N_Nm'] for r in transport]);metrics.update(GT_final_position_RMS_m=float(np.sqrt(np.mean([r['GT_goal_distance_m']**2 for r in final]))),GT_final_angle_RMS_rad=float(np.sqrt(np.mean([r['GT_goal_angle_rad']**2 for r in final]))),true_internal_stack_force_RMS_N=float(np.sqrt(np.mean(np.sum(h[:,:,:3]**2,axis=(1,2))))),true_internal_each_moment_RMS_Nm=np.sqrt(np.mean(np.sum(h[:,:,3:]**2,axis=2),axis=0)).tolist())
 summary={'status':'COMPLETE' if failure is None else 'FAIL_STOP','case':case,'reason':failure,'wall_s':time.perf_counter()-start,'phase':phase,'last_event_time_s':None if tick is None else tick*dt,'last_transport_log_time_s':trace_rows[-1]['time_s'] if trace_rows else None,'transport_samples':len(trace_rows),'estimator_predictions':est_predictions,'estimator_updates':est_updates,'GT_control_state_reads':primary_GT_reads,'metrics':metrics,'max_Newton_corrections':max_Newton,'no_reset':True,'control_gain_or_condition_changes':False,'corrections_used':3,'remaining_corrections':0};write(out/'summary.json',summary);write(out/'artifact_sha256.json',{p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file()});print(json.dumps(summary),flush=True);return summary

def half_step_gate(coarse,fine):
 def read(p):
  with gzip.open(p/'plant.jsonl.gz','rt') as f:return [json.loads(s) for s in f]
 a,b=read(coarse),read(fine)
 if len(a)!=len(b):return {'pass':False,'reason':'HALF_STEP_LOG_COUNT_MISMATCH'}
 maxima=np.zeros(6)
 for x,y in zip(a,b):
  if x['time_s']!=y['time_s']:return {'pass':False,'reason':'HALF_STEP_PHYSICAL_CLOCK_MISMATCH'}
  p,q=np.array(x['state']['O']),np.array(y['state']['O']);raw=np.array(x['h_N_Nm'])-np.array(y['h_N_Nm']);hi=np.array(x['internal_N_Nm'])-np.array(y['internal_N_Nm'])
  maxima=np.maximum(maxima,[np.linalg.norm(p[:3,3]-q[:3,3]),np.linalg.norm(geo.se3_log(geo.inverse(p)@q)[3:]),np.max(np.abs(raw[:,:3])),np.max(np.abs(raw[:,3:])),np.max(np.abs(hi[:,:3])),np.max(np.abs(hi[:,3:]))])
 return {'pass':bool(np.all(maxima<=np.array([5e-5,5e-4,.05,.002,.05,.002]))),'maxima':dict(zip(('position_m','angle_rad','raw_force_N','raw_moment_Nm','internal_force_N','internal_moment_Nm'),maxima.tolist())),'samples_compared':len(a),'thresholds_unchanged':True}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True);args=ap.parse_args();out=Path(args.output_dir).resolve();out.mkdir(exist_ok=False)
 cfgpath=ROOT/'configs/p2_closed_loop_protocol_v3.json';cfg=json.loads(cfgpath.read_text());gates=[ROOT/'results/20261014_P2_implicit_qualification_v3_01',ROOT/'results/20261014_P2_components_qualification01',ROOT/'results/20261014_P2_clock_qualification01']
 for gate in gates:assert json.loads((gate/'summary.json').read_text())['status']=='PASS'
 prior_wall=sum(json.loads((g/'summary.json').read_text()).get('wall_s',0) for g in gates);suite_started=time.perf_counter();native=NativeModel(build_native('/home/ubuntu2004/lmy/.p2_native_build_v3'))
 allcases=cases(cfg);ledger=[dict(c,status='NOT_EXECUTED',directory=None) for c in allcases];write(out/'config_snapshot.json',cfg);write(out/'metadata.json',{'kind':'FROZEN_FIRST_30_CASE_SUITE','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'protocol_sha256':sha(cfgpath),'command':sys.argv,'gate_indexes':{str(g.relative_to(ROOT)):sha(g/'artifact_sha256.json') for g in gates},'registered_control_cases':30,'execution_order':[11,30]+[c['id'] for c in allcases if c['id'] not in (11,30)],'corrections_used':3,'remaining_corrections':0,'prior_qualification_wall_s':prior_wall,'max_case_wall_s':120,'max_suite_wall_s':7200})
 def saveledger():write(out/'case_ledger.json',{'cases':ledger,'executed_control_cases':sum(c['status']!='NOT_EXECUTED' for c in ledger),'executed_primary':sum(c['id']<=20 and c['status']!='NOT_EXECUTED' for c in ledger),'not_executed':sum(c['status']=='NOT_EXECUTED' for c in ledger),'corrections_used':3,'remaining_corrections':0})
 saveledger();failure=None;results={}
 for ident in [11,30]+[c['id'] for c in allcases if c['id'] not in (11,30)]:
  case=allcases[ident-1];directory=out/('case_'+format(ident,'02d')+'_'+case['condition']+'_'+str(case['seed']));ledger[ident-1].update(status='RUNNING',directory=str(directory.relative_to(ROOT)));saveledger()
  summary=run_case(cfg,case,directory,native,suite_started,prior_wall);results[ident]=summary;ledger[ident-1]['status']=summary['status'];saveledger()
  if summary['status']!='COMPLETE':failure='CASE_'+str(ident)+':'+str(summary['reason']);break
  if ident==30:
   step=half_step_gate(out/'case_11_exp3_7',directory);write(out/'full_half_step_gate.json',step)
   if not step['pass']:failure='FULL_CONTROLLED_HALF_STEP_GATE_FAILED';break
  if time.perf_counter()-suite_started+prior_wall>7200:failure='SUITE_WALL_LIMIT';break
 write(out/'summary.json',{'status':'COMPLETE' if failure is None else 'FAIL_STOP','reason':failure,'executed_cases':len(results),'completed_cases':sum(s['status']=='COMPLETE' for s in results.values()),'executed_primary':sum(i<=20 for i in results),'wall_s':time.perf_counter()-suite_started,'prior_qualification_wall_s':prior_wall,'closed_loop_qualified':failure is None,'all_30_runs_complete':len(results)==30 and failure is None,'corrections_used':3,'remaining_corrections':0});write(out/'artifact_sha256.json',{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()});return 0 if failure is None else 2
if __name__=='__main__':raise SystemExit(main())
