#!/usr/bin/env python3
"""Archive predeclared E/C unit qualifications only after N/D70 passes."""
import hashlib,json,os,platform,subprocess,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/20261014_P2_components_qualification01'
TESTS=['tests/test_p2_estimator.py','tests/test_p2_observations_qualification.py','tests/test_p2_control_qualification.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def main():
 gate=ROOT/'results/20261014_P2_implicit_qualification_v3_01';prior=json.loads((gate/'summary.json').read_text());assert prior['status']=='PASS' and prior['passed_checks']==70 and prior['dynamics_qualified']
 OUT.mkdir(exist_ok=False);cfg=ROOT/'configs/p2_closed_loop_protocol_v3.json';command=[sys.executable,'-m','pytest','-q',*TESTS,'--junitxml='+str(OUT/'pytest.xml')]
 sources=['scripts/qualify_p2_components.py','baselines/p2_pose_force/estimator.py','baselines/p2_pose_force/observations.py','baselines/p2_pose_force/control.py','baselines/p2_pose_force/mechanics.py','baselines/p2_pose_force/contact_geometry.py',*TESTS]
 save('metadata.json',{'kind':'PREDECLARED_E_C_COMPONENT_QUALIFICATION_NO_CONTROL','date':'2026-10-14','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':{p:sha(ROOT/p) for p in sources},'command':command,'python':platform.python_version(),'config_path':str(cfg.relative_to(ROOT)),'protocol_sha256':sha(cfg),'test_fixture_protocol':'v1 original physical/estimator/control values; all unchanged in v3','required_prior_N_D_index_sha256':sha(gate/'artifact_sha256.json'),'wall_limit_s':120,'corrections_used':2,'remaining_corrections':1,'closed_loop_runs':0});(OUT/'config_snapshot.json').write_bytes(cfg.read_bytes())
 start=time.perf_counter();failure=None
 try:
  result=subprocess.run(command,cwd=ROOT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),capture_output=True,text=True,timeout=120)
  (OUT/'stdout.txt').write_text(result.stdout);(OUT/'stderr.txt').write_text(result.stderr);status=result.returncode
 except subprocess.TimeoutExpired as exc:
  (OUT/'stdout.txt').write_bytes(exc.stdout or b'');(OUT/'stderr.txt').write_bytes(exc.stderr or b'');status=124;failure='COMPONENT_QUALIFICATION_WALL_LIMIT'
 cases=[]
 if (OUT/'pytest.xml').exists():
  for c in ET.parse(OUT/'pytest.xml').getroot().iter('testcase'):
   fail=c.find('failure');error=c.find('error');skip=c.find('skipped')
   cases.append({'name':c.get('classname')+'.'+c.get('name'),'time_s':float(c.get('time','0')),'status':'FAIL' if fail is not None or error is not None else 'SKIPPED' if skip is not None else 'PASS','failure':fail.text if fail is not None else error.text if error is not None else None})
 qualified=status==0 and bool(cases) and all(c['status']=='PASS' for c in cases)
 if not qualified and failure is None:failure='E_C_COMPONENT_QUALIFICATION_FAILED'
 summary={'status':'PASS' if qualified else 'FAIL_STOP','returncode':status,'wall_s':time.perf_counter()-start,'case_count':len(cases),'passed':sum(c['status']=='PASS' for c in cases),'cases':cases,'estimator_controller_components_qualified':qualified,'multirate_runner_qualified':False,'closed_loop_qualified':False,'closed_loop_runs':0,'reason':failure}
 save('summary.json',summary)
 if not qualified:save('termination.json',{'reason':failure,'no_control_run_started':True,'failures_preserved':True})
 save('artifact_sha256.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()});print(json.dumps({k:v for k,v in summary.items() if k!='cases'}));return 0 if qualified else 2
if __name__=='__main__':raise SystemExit(main())
