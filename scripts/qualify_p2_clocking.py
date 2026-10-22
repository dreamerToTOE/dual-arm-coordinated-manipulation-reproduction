#!/usr/bin/env python3
"""Predeclared two deterministic clock tests; no plant/filter/control trial."""
import hashlib,json,os,subprocess,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/20261014_P2_clock_qualification01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def main():
 assert json.loads((ROOT/'results/20261014_P2_components_qualification01/summary.json').read_text())['status']=='PASS'
 OUT.mkdir(exist_ok=False);command=[sys.executable,'-m','pytest','-q','tests/test_p2_clocking.py','--junitxml='+str(OUT/'pytest.xml')];start=time.perf_counter()
 sources=['baselines/p2_pose_force/clocking.py','tests/test_p2_clocking.py','scripts/qualify_p2_clocking.py','scripts/run_p2_closed_loop.py','reports/P2_CLOSED_LOOP_RUNTIME_SPEC.md'];cfg=ROOT/'configs/p2_closed_loop_protocol_v3.json'
 save('metadata.json',{'kind':'DETERMINISTIC_CAUSAL_CLOCK_QUALIFICATION_NO_ODE','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':{p:sha(ROOT/p) for p in sources},'protocol_sha256':sha(cfg),'command':command,'corrections_used':2,'remaining_corrections':1,'closed_loop_runs':0});(OUT/'config_snapshot.json').write_bytes(cfg.read_bytes())
 p=subprocess.run(command,cwd=ROOT,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),capture_output=True,text=True,timeout=120);(OUT/'stdout.txt').write_text(p.stdout);(OUT/'stderr.txt').write_text(p.stderr)
 cases=[]
 for c in ET.parse(OUT/'pytest.xml').getroot().iter('testcase'):
  f=c.find('failure');e=c.find('error');cases.append({'name':c.get('name'),'pass':f is None and e is None and c.find('skipped') is None,'failure':f.text if f is not None else e.text if e is not None else None})
 passed=p.returncode==0 and len(cases)==2 and all(c['pass'] for c in cases);save('summary.json',{'status':'PASS' if passed else 'FAIL_STOP','returncode':p.returncode,'cases':cases,'wall_s':time.perf_counter()-start,'clocking_components_qualified':passed,'full_loop_qualified':False,'closed_loop_runs':0});save('artifact_sha256.json',{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()});print(json.dumps({'pass':passed,'cases':len(cases)}));return 0 if passed else 2
if __name__=='__main__':raise SystemExit(main())
